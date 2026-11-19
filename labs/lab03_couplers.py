"""Lab 3: directional coupler and MMI design in Python (Open-Photonics, Chapters 9 and 10).

Run it from a terminal:
    python lab03_couplers.py              # prints every checkpoint and saves lab03_couplers.png
    python lab03_couplers.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. All lengths are in micrometres.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-03/
"""
import sys

import numpy as np

LAM = 1.55       # vacuum wavelength
T_SI = 0.22      # silicon thickness
W_WG = 0.5       # width of each coupler waveguide
H = 0.005        # finite-difference step for the couplers (5 nm)


def n_si(lam):
    """Silicon at room temperature (Sellmeier fit of Li, 1980), lam in micrometres."""
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / lam**2 + 0.00810461 * l1**2 / (lam**2 - l1**2))


def n_ox(lam):
    """Fused silica (Malitson, 1965)."""
    return np.sqrt(1 + 0.6961663 * lam**2 / (lam**2 - 0.0684043**2) + 0.4079426 * lam**2 / (lam**2 - 0.1162414**2)
                   + 0.8974794 * lam**2 / (lam**2 - 9.896161**2))


# ---------------------------------------------------------------------------------------------------------
# Part A. Collapse the vertical direction: the effective-index method (Chapter 6, Section 6.2; Lab 1)
# ---------------------------------------------------------------------------------------------------------
def slab_F(neff, n1, n2, n3, d, lam, tm=False):
    """kappa*d minus the two reflection phases; guided mode m solves slab_F(neff) = m*pi (Lab 1, Chapter 5)."""
    k0 = 2 * np.pi / lam
    kappa = k0 * np.sqrt(n1**2 - neff**2)
    g2, g3 = k0 * np.sqrt(neff**2 - n2**2), k0 * np.sqrt(neff**2 - n3**2)
    p2, p3 = (g2 * n1**2 / n2**2, g3 * n1**2 / n3**2) if tm else (g2, g3)
    return kappa * d - np.arctan(p2 / kappa) - np.arctan(p3 / kappa)


def slab_modes(n1, n2, n3, d, lam, tm=False):
    """Effective indices of every guided slab mode, fundamental first, by bisection (Lab 1)."""
    lo, hi = max(n2, n3) + 1e-12, n1 - 1e-12
    modes, m = [], 0
    while slab_F(lo, n1, n2, n3, d, lam, tm) > m * np.pi:
        a, b = lo, hi
        for _ in range(60):
            c = 0.5 * (a + b)
            if slab_F(c, n1, n2, n3, d, lam, tm) > m * np.pi:
                a = c
            else:
                b = c
        modes.append(0.5 * (a + b))
        m += 1
    return modes


def vertical_index(lam=LAM):
    """n_I: the TE0 effective index of the 220 nm silicon film in oxide, the core of every lateral problem below."""
    return slab_modes(n_si(lam), n_ox(lam), n_ox(lam), T_SI, lam)[0]


# ---------------------------------------------------------------------------------------------------------
# Part B. A finite-difference mode solver for the lateral profile
# ---------------------------------------------------------------------------------------------------------
def grid(half_width, h):
    """Cell-centred grid from -half_width to +half_width. Choose half_width and h so that every wall of the
    structure falls on a cell boundary, midway between two nodes; then each node sits in one material."""
    return (np.arange(int(round(2 * half_width / h))) + 0.5) * h - half_width


def strips(x, centres, width, n_core, n_clad):
    """Index profile of waveguides of the given width centred at `centres`, in cladding."""
    inside = np.zeros(len(x), bool)
    for c in centres:
        inside |= np.abs(x - c) < width / 2
    return np.where(inside, n_core, n_clad)


def fd_modes(n, h, lam, tm=True):
    """Lateral modes of the index profile n (one value per node, step h), highest effective index first.

    tm=True is the lateral problem of a TE-like mode, whose electric field is normal to the side walls (Lab 1):
        d/dx( (1/n^2) dH/dx ) + k0^2 H = beta^2 H / n^2   for H = H_y.
    Between two nodes 1/n^2 is taken as 2/(n_i^2 + n_(i+1)^2), which keeps (1/n^2) dH/dx continuous at a wall.
    Writing H = n v turns this into a symmetric tridiagonal eigenproblem for beta^2, solved by numpy.linalg.eigh.
    tm=False solves d^2E/dx^2 + k0^2 n^2 E = beta^2 E (field parallel to the walls).
    The fields come back as columns, normalised so that sum(|H|^2 / n^2) h = 1 (TM) or sum(|E|^2) h = 1 (TE):
    with these weights the modes are orthonormal, which is what an eigenmode expansion needs.
    """
    k0 = 2 * np.pi / lam
    eps = n**2
    if tm:
        a = 1 / eps
        a_mid = 2 / (eps[:-1] + eps[1:])                         # 1/n^2 halfway between neighbouring nodes
        a_left, a_right = np.r_[a[0], a_mid], np.r_[a_mid, a[-1]]  # the field is zero just outside the window
        diag = n * (k0**2 - (a_left + a_right) / h**2) * n
        off = n[:-1] * a_mid * n[1:] / h**2
    else:
        diag = k0**2 * eps - 2 / h**2
        off = np.ones(len(n) - 1) / h**2
    beta2, v = np.linalg.eigh(np.diag(diag) + np.diag(off, 1) + np.diag(off, -1))
    beta2, v = beta2[::-1], v[:, ::-1]
    fields = (n[:, None] * v if tm else v) / np.sqrt(h)
    return np.sqrt(np.maximum(beta2, 0)) / k0, fields


def overlap(f, g, n, h, tm=True):
    """Inner product of two lateral fields with the weight that makes the modes orthonormal."""
    return np.sum(f * g / (n**2 if tm else 1)) * h


# ---------------------------------------------------------------------------------------------------------
# Part C. Supermodes of two coupled strips (Chapter 9, Sections 9.2 and 9.3)
# ---------------------------------------------------------------------------------------------------------
def coupler(gap, lam=LAM, h=H, pad=1.0):
    """Grid, index profile and modes of two 500 nm strips separated by gap (all walls on cell boundaries)."""
    x = grid(gap / 2 + W_WG + pad, h)
    n = strips(x, (-(gap + W_WG) / 2, (gap + W_WG) / 2), W_WG, vertical_index(lam), n_ox(lam))
    neff, fields = fd_modes(n, h, lam)
    return x, n, neff, fields


def crossover(gap, lam=LAM):
    """Even and odd supermode indices and the cross-over length L_x = lambda / (2 (n_even - n_odd))."""
    _, _, neff, _ = coupler(gap, lam)
    return neff[0], neff[1], lam / (2 * (neff[0] - neff[1]))


def strip_mode(x, centre, lam=LAM, h=H):
    """Fundamental mode of one 500 nm strip on its own, centred at `centre`, on the coupler's grid."""
    n = strips(x, (centre,), W_WG, vertical_index(lam), n_ox(lam))
    return fd_modes(n, h, lam)[1][:, 0]


def bisect(f, a, b, n=60):
    """A root of f between a and b, where f changes sign, by halving the interval n times."""
    fa = f(a)
    for _ in range(n):
        c = 0.5 * (a + b)
        if (f(c) > 0) == (fa > 0):
            a, fa = c, f(c)
        else:
            b = c
    return 0.5 * (a + b)


def golden_max(f, a, b, n=60):
    """The maximum of f between a and b (one maximum only) by golden-section search."""
    g = (np.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    for _ in range(n):
        if f(c) > f(d):
            b, d = d, c
            c = b - g * (b - a)
        else:
            a, c = c, d
            d = a + g * (b - a)
    return 0.5 * (a + b)


def expansion(field_in, ports, n, h, lam, tm=True):
    """Eigenmode expansion: launch field_in into the structure n, and return a function of the length z that
    gives the power coupled into each port field. Only guided modes (n_eff above the cladding) are kept;
    whatever the input puts into the rest is lost, as radiation would be.
    """
    neff, modes = fd_modes(n, h, lam, tm)
    guided = neff > n.min()
    neff, modes = neff[guided], modes[:, guided]
    unit = lambda f: f / np.sqrt(overlap(f, f, n, h, tm))
    c = np.array([overlap(unit(field_in), m, n, h, tm) for m in modes.T])          # amplitude in each mode
    d = [np.array([overlap(unit(p), m, n, h, tm) for m in modes.T]) for p in ports]  # each mode's share of a port
    beta = 2 * np.pi * neff / lam

    def port_powers(z):
        ph = np.exp(-1j * np.outer(beta, np.atleast_1d(z)))                         # modes x lengths
        return [np.abs((c * dk) @ ph) ** 2 for dk in d]
    return port_powers, c, neff, modes


# Reference: femwell's full vectorial supermodes of two 500 x 220 nm strips in oxide (Chapter 9, figsrc/ch09_supermodes.py)
FEMWELL_GAP = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.40])
FEMWELL_EVEN = np.array([2.4807, 2.4651, 2.4573, 2.4529, 2.4503, 2.4477])
FEMWELL_ODD = np.array([2.4277, 2.4328, 2.4368, 2.4397, 2.4418, 2.4441])
FEMWELL_LX = np.array([14.625, 23.974, 37.846, 58.904, 91.131, 216.032])
FEMWELL_LX_LAM = {1.50: 47.202, 1.55: 37.846, 1.60: 30.605}   # 200 nm gap
L_BENDS = 2.5                                                  # effective length added by the bends (Chapter 9)


# ---------------------------------------------------------------------------------------------------------
# Part D. The multimode section of an MMI (Chapter 10, Section 10.3)
# ---------------------------------------------------------------------------------------------------------
W_MMI = 6.0      # width of the multimode section (Worked Example 10.1)
W_ACC = 1.5      # width of the tapered access waveguides where they meet it
H_MMI = 0.01     # finite-difference step for the MMI (10 nm)
L_SIGMA0 = 35.4  # the 1 x 2 length 3 L_pi / 8 that sigma = 0 (field parallel to the walls) would give, with n_r = 2.85


def mmi_grid(lam=LAM, pad=1.5):
    """Grid and index profile of the multimode section, with pad micrometres of oxide on each side."""
    x = grid(W_MMI / 2 + pad, H_MMI)
    return x, strips(x, (0.0,), W_MMI, vertical_index(lam), n_ox(lam))


def access_mode(x, centre, lam=LAM):
    """Fundamental mode of a W_ACC-wide access waveguide centred at `centre`, on the MMI's grid."""
    n = strips(x, (centre,), W_ACC, vertical_index(lam), n_ox(lam))
    return fd_modes(n, H_MMI, lam)[1][:, 0]


def effective_width(n_r, n_c, sigma, lam=LAM):
    """W_e = W + (lam/pi) (n_c/n_r)^(2 sigma) / sqrt(n_r^2 - n_c^2) (Section 10.3); sigma = 0 or 1."""
    return W_MMI + lam / np.pi * (n_c / n_r) ** (2 * sigma) / np.sqrt(n_r**2 - n_c**2)


def main(plot=True):
    print("Lab 3: directional couplers and MMIs (lengths in um, wavelength 1.55 um, TE-like modes)\n")

    # ---- Part A
    n_I, n_c = vertical_index(), n_ox(LAM)
    print("A. The effective-index method: collapse the 220 nm film")
    print(f"   n_Si = {n_si(LAM):.4f}, n_ox = {n_c:.4f}; the film's TE0 index n_I = {n_I:.4f}   (Chapter 5: 2.848;"
          " Chapter 10: n_r = 2.85)")
    print(f"   lateral problem: {n_I:.4f} in the waveguides, {n_c:.4f} around them, solved as TM (E normal to the walls)\n")

    # ---- Part B
    print("B. The finite-difference solver against the exact slab, one 500 nm strip")
    exact = slab_modes(n_I, n_c, n_c, W_WG, LAM, tm=True)
    for h in (0.02, 0.01, 0.005):
        x = grid(W_WG / 2 + 1.5, h)
        neff, _ = fd_modes(strips(x, (0.0,), W_WG, n_I, n_c), h, LAM)
        print(f"   step {1000 * h:4.0f} nm ({len(x):4d} nodes): n_eff = {neff[0]:.5f}, {neff[1]:.5f}")
    print(f"   exact lateral slab (bisection):  n_eff = {exact[0]:.5f}, {exact[1]:.5f}   (Lab 1: EIM 2.491)")
    x = grid(W_WG / 2 + 1.5, H)
    te = fd_modes(strips(x, (0.0,), W_WG, n_I, n_c), H, LAM, tm=False)[0][0]
    print(f"   femwell (full vectorial): 2.4459   (Chapter 6: 2.446); the lateral problem solved as TE instead: {te:.4f}\n")

    # ---- Part C
    print("C. Supermodes of two 500 nm strips and the cross-over length")
    rows = [crossover(g) for g in FEMWELL_GAP]
    ne, no, Lx = map(np.array, zip(*rows))
    i200 = 2
    print(f"   200 nm gap: n_even = {ne[i200]:.4f}, n_odd = {no[i200]:.4f}, L_x = {Lx[i200]:.1f} um; femwell "
          f"{FEMWELL_EVEN[i200]:.4f}, {FEMWELL_ODD[i200]:.4f}, {FEMWELL_LX[i200]:.1f} um   (Chapter 9: 2.4573, 2.4368, 37.8 um)")
    print("   gap (nm)   EIM L_x   femwell L_x   EIM / femwell")
    for g, a, b in zip(FEMWELL_GAP, Lx, FEMWELL_LX):
        print(f"   {1000 * g:6.0f}   {a:9.1f}   {b:11.1f}   {a / b:9.2f}")
    print(f"   growth per 100 nm of gap (200 -> 300 nm): EIM {Lx[4] / Lx[2]:.2f}x, femwell {FEMWELL_LX[4] / FEMWELL_LX[2]:.2f}x"
          "   (Chapter 9: about 2.4x)")
    # a 3 dB coupler: half a cross-over length, part of it supplied by the bends
    print(f"   3 dB coupler at 200 nm: L_x/2 = {Lx[i200] / 2:.2f} um; straight section with {L_BENDS} um of bends "
          f"{Lx[i200] / 2 - L_BENDS:.1f} um   (Chapter 9: 16.4 um)")
    xg, ng, _, _ = coupler(0.2)
    left = strip_mode(xg, -(0.2 + W_WG) / 2)
    right = strip_mode(xg, (0.2 + W_WG) / 2)
    powers = expansion(left, [left, right], ng, H, LAM)[0]
    z50 = bisect(lambda z: powers(z)[1][0] - 0.5, 0.0, Lx[i200] * 0.9)
    print(f"   launching the single-strip mode and propagating (eigenmode expansion): 50 % crosses at {z50:.2f} um")
    lx_lam = {lam: crossover(0.2, lam)[2] for lam in (1.50, 1.53, 1.57, 1.60)}
    print(f"   L_x at 1500 and 1600 nm: EIM {lx_lam[1.50]:.1f} and {lx_lam[1.60]:.1f} um, femwell "
          f"{FEMWELL_LX_LAM[1.50]:.1f} and {FEMWELL_LX_LAM[1.60]:.1f} um   (Chapter 9: 47 and 31 um)")
    split = {lam: np.sin(np.pi * Lx[i200] / (4 * lx_lam[lam])) ** 2 for lam in (1.53, 1.57)}
    print(f"   the 1550 nm 3 dB coupler crosses {100 * split[1.53]:.1f} % at 1530 nm and {100 * split[1.57]:.1f} % at 1570 nm,"
          f" {100 * (split[1.57] - split[1.53]) / 40:.2f} %/nm   (Chapter 9: 43.5 % and 57 %, 0.35 %/nm)\n")

    # ---- Part D
    xm, nm_ = mmi_grid()
    neff, modes = fd_modes(nm_, H_MMI, LAM)
    guided = int(np.sum(neff > n_c))
    L_pi = LAM / (2 * (neff[0] - neff[1]))
    We = {s: effective_width(n_I, n_c, s) for s in (0, 1)}
    Lpi_f = {s: 4 * n_I * We[s] ** 2 / (3 * LAM) for s in (0, 1)}
    print(f"D. The {W_MMI:.0f} um multimode section")
    print(f"   {guided} guided modes; n_0 = {neff[0]:.5f}, n_1 = {neff[1]:.5f}")
    print(f"   beat length L_pi = lambda / (2 (n_0 - n_1)) = {L_pi:.1f} um")
    print(f"   formula 4 n_r W_e^2 / (3 lambda), sigma = 1 (field normal to the walls): W_e = {We[1]:.3f} um, "
          f"L_pi = {Lpi_f[1]:.1f} um   (Chapter 10, n_r = 2.85: W_e = 6.052 um, L_pi = 89.8 um)")
    print(f"   for comparison, sigma = 0 (field parallel to the walls): W_e = {We[0]:.3f} um, L_pi = {Lpi_f[0]:.1f} um")
    te_n = fd_modes(nm_, H_MMI, LAM, tm=False)[0]
    print(f"   and the same section solved as TE (field parallel to the walls): L_pi = {LAM / (2 * (te_n[0] - te_n[1])):.1f} um")
    beta = 2 * np.pi * neff[:guided] / LAM
    nu = np.arange(guided)
    ratio = (beta[0] - beta[1:]) / (beta[0] - beta[1]) / (nu[1:] * (nu[1:] + 2) / 3)
    print("   (beta_0 - beta_nu) against the quadratic law nu (nu + 2) pi / (3 L_pi), as a ratio:")
    print("   " + ", ".join(f"nu = {v}: {r:.3f}" for v, r in zip(nu[2::4], ratio[1::4])) + "\n")

    # ---- Part E
    We_fd = np.sqrt(3 * LAM * L_pi / (4 * n_I))                  # the effective width the solver implies
    centre, up, down = access_mode(xm, 0.0), access_mode(xm, We_fd / 4), access_mode(xm, -We_fd / 4)
    powers, c, _, gmodes = expansion(centre, [up, down], nm_, H_MMI, LAM)
    total = lambda z: powers(z)[0][0] + powers(z)[1][0]
    zs = np.linspace(20, 50, 3001)
    Pz = powers(zs)
    L12 = golden_max(total, *zs[np.argmax(Pz[0] + Pz[1])] + np.array([-0.05, 0.05]))
    pu, pd = powers(L12)[0][0], powers(L12)[1][0]
    field = gmodes @ (c * np.exp(-2j * np.pi * neff[:guided] * L12 / LAM))
    I = np.abs(field) ** 2
    peak_x = xm[xm > 0][np.argmax(I[xm > 0])]
    print("E. Self-imaging: a centred 1 x 2 MMI by eigenmode expansion")
    print(f"   input: the mode of a {W_ACC} um access guide; {100 * np.sum(c**2):.2f} % of its power goes into guided modes,"
          f" {100 * np.sum(c[1::2] ** 2):.1f} % into odd ones")
    print(f"   best length {L12:.2f} um: {100 * pu:.1f} % + {100 * pd:.1f} %, excess loss {-10 * np.log10(pu + pd):.2f} dB")
    print(f"   3 L_pi / 8 = {3 * L_pi / 8:.2f} um from the solver's L_pi   (Chapter 10: 33.7 um)")
    p35 = powers(L_SIGMA0)
    print(f"   cut at {L_SIGMA0} um, the length sigma = 0 would give: {100 * p35[0][0]:.1f} % + {100 * p35[1][0]:.1f} %,"
          f" excess loss {-10 * np.log10(p35[0][0] + p35[1][0]):.2f} dB")
    print(f"   the two images peak at +-{peak_x:.2f} um; W_e/4 = {We_fd / 4:.2f} um   (Chapter 10: +-1.51 um)\n")

    if plot:
        make_figure(Lx, xg, ng, xm, nm_, c, gmodes, neff[:guided], L12, L_pi, zs, Pz)


def make_figure(Lx, xg, ng, xm, nm_, c, gmodes, neff, L12, L_pi, zs, Pz):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    # (a) the even and odd supermodes at a 200 nm gap
    _, f = fd_modes(ng, H, LAM)
    for wall in (-0.1 - W_WG, 0.1):
        ax[0, 0].axvspan(wall, wall + W_WG, color="0.88")
    for k, col, lab in ((0, "tab:blue", "even"), (1, "tab:orange", "odd")):
        sign = np.sign(f[np.argmax(np.abs(f[:, k])), k])
        ax[0, 0].plot(xg, sign * f[:, k] / np.abs(f[:, k]).max(), color=col, label=lab)
    ax[0, 0].set(xlim=(-1.4, 1.4), xlabel="x (µm)", ylabel="H_y (normalised)", title="(a) supermodes, 200 nm gap")
    ax[0, 0].legend(fontsize=8)
    # (b) cross-over length against gap
    ax[0, 1].semilogy(1000 * FEMWELL_GAP, FEMWELL_LX, "o", color="tab:blue", ms=5, label="femwell (Chapter 9)")
    ax[0, 1].semilogy(1000 * FEMWELL_GAP, Lx, "s-", color="tab:orange", ms=4, label="EIM + finite differences")
    ax[0, 1].set(xlabel="gap (nm)", ylabel="cross-over length L_x (µm)", title="(b) L_x against gap, 1550 nm")
    ax[0, 1].legend(fontsize=8)
    # (c) intensity in the MMI
    zmap = np.linspace(0, 2 * L12, 400)
    I = np.abs(gmodes @ (c[:, None] * np.exp(-2j * np.pi * np.outer(neff, zmap) / LAM))) ** 2
    ax[1, 0].imshow(I**0.6, extent=(zmap[0], zmap[-1], xm[0], xm[-1]), origin="lower", aspect="auto", cmap="inferno")
    for yy in (-W_MMI / 2, W_MMI / 2):
        ax[1, 0].axhline(yy, color="w", lw=0.6, ls=":")
    ax[1, 0].axvline(L12, color="w", lw=0.8, ls="--")
    ax[1, 0].set(xlabel="z (µm)", ylabel="x (µm)", title=f"(c) 6 µm MMI, centred input: images at {L12:.1f} µm")
    # (d) power in the two output ports against length
    ax[1, 1].plot(zs, Pz[0], color="tab:blue", label="upper port")
    ax[1, 1].plot(zs, Pz[1], color="tab:orange", ls="--", label="lower port")
    ax[1, 1].plot(zs, Pz[0] + Pz[1], color="k", lw=1, label="total")
    ax[1, 1].axvline(3 * L_pi / 8, color="grey", ls=":", lw=0.9)
    ax[1, 1].axvline(L_SIGMA0, color="tab:red", ls=":", lw=0.9)
    ax[1, 1].text(3 * L_pi / 8 + 0.3, 0.05, "3Lπ/8", color="grey", fontsize=8)
    ax[1, 1].text(L_SIGMA0 + 0.3, 0.15, "σ = 0", color="tab:red", fontsize=8)
    ax[1, 1].set(xlabel="MMI length (µm)", ylabel="power", ylim=(0, 1.02), title="(d) 1 × 2 MMI: power in each output")
    ax[1, 1].legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig("lab03_couplers.png", dpi=150)
    print("Saved the figure as lab03_couplers.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
