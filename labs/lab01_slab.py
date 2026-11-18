"""Lab 1: slab and channel waveguide modes in Python (Open-Photonics, Chapters 5 and 6).

Run it from a terminal:
    python lab01_slab.py              # prints every checkpoint and saves lab01_slab.png
    python lab01_slab.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. All lengths are in micrometres.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-01/
"""
import sys

import numpy as np

N_SI, N_OX = 3.476, 1.444   # silicon and silica at 1550 nm
LAM = 1.55                  # vacuum wavelength


# ---------------------------------------------------------------------------------------------------------
# Part A. The slab eigenvalue equation (Chapter 5, Section 5.3)
# ---------------------------------------------------------------------------------------------------------
def slab_F(neff, n1, n2, n3, d, lam, tm=False):
    """kappa*d minus the two reflection phases. Guided mode m solves slab_F(neff) = m*pi.

    n1 is the film, n2 the substrate and n3 the cover; d is the film thickness.
    TM modes weight each cladding's decay constant by n1^2/n_i^2 (continuity of H_y and of (1/n^2) dH_y/dx).
    """
    k0 = 2 * np.pi / lam
    kappa = k0 * np.sqrt(n1**2 - neff**2)          # transverse wavenumber in the film
    g2 = k0 * np.sqrt(neff**2 - n2**2)             # decay constants in the claddings
    g3 = k0 * np.sqrt(neff**2 - n3**2)
    p2, p3 = (g2 * n1**2 / n2**2, g3 * n1**2 / n3**2) if tm else (g2, g3)
    return kappa * d - np.arctan(p2 / kappa) - np.arctan(p3 / kappa)


def slab_modes(n1, n2, n3, d, lam, tm=False):
    """Effective indices of every guided mode, fundamental first, found by bisection.

    slab_F falls steadily as neff rises from the higher cladding index to n1, so each mode number m has
    at most one solution, and mode m exists only if slab_F at the bottom of the range exceeds m*pi.
    """
    lo, hi = max(n2, n3) + 1e-12, n1 - 1e-12
    modes, m = [], 0
    while slab_F(lo, n1, n2, n3, d, lam, tm) > m * np.pi:
        a, b = lo, hi
        for _ in range(60):                         # 60 halvings: far below any digit we print
            c = 0.5 * (a + b)
            if slab_F(c, n1, n2, n3, d, lam, tm) > m * np.pi:
                a = c
            else:
                b = c
        modes.append(0.5 * (a + b))
        m += 1
    return modes


# ---------------------------------------------------------------------------------------------------------
# Part B. Field, evanescent decay and confinement (Chapter 5, Section 5.5)
# ---------------------------------------------------------------------------------------------------------
def te_field(neff, n1, n2, n3, d, lam, x):
    """E_y of a TE mode on the grid x: film from x = 0 to x = d, substrate below, cover above.

    Inside the film E = cos(kappa*x - phi2) with tan(phi2) = g2/kappa, which matches E and dE/dx at x = 0;
    the eigenvalue equation makes it match at x = d as well.
    """
    k0 = 2 * np.pi / lam
    kappa, g2, g3 = (k0 * np.sqrt(n1**2 - neff**2), k0 * np.sqrt(neff**2 - n2**2), k0 * np.sqrt(neff**2 - n3**2))
    phi2 = np.arctan(g2 / kappa)
    film = np.cos(kappa * x - phi2)
    below = np.cos(phi2) * np.exp(g2 * x)
    above = np.cos(kappa * d - phi2) * np.exp(-g3 * (x - d))
    return np.where(x < 0, below, np.where(x <= d, film, above))


def confinement(neff, n1, n2, n3, d, lam):
    """Fraction of a TE mode's power (|E|^2, Chapter 5) inside the film."""
    x = np.linspace(-3.0, d + 3.0, 60001)           # wide enough for the tails to have died away
    E2 = te_field(neff, n1, n2, n3, d, lam, x) ** 2
    inside = (x >= 0) & (x <= d)
    return E2[inside].sum() / E2.sum()


# ---------------------------------------------------------------------------------------------------------
# Part C. Group index with material dispersion (Chapter 5, Section 5.6)
# ---------------------------------------------------------------------------------------------------------
def n_si(lam):
    """Silicon at room temperature (Sellmeier fit of Li, 1980), lam in micrometres."""
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / lam**2 + 0.00810461 * l1**2 / (lam**2 - l1**2))


def n_ox(lam):
    """Fused silica (Malitson, 1965)."""
    return np.sqrt(1 + 0.6961663 * lam**2 / (lam**2 - 0.0684043**2) + 0.4079426 * lam**2 / (lam**2 - 0.1162414**2)
                   + 0.8974794 * lam**2 / (lam**2 - 9.896161**2))


def group_index(neff_of_lam, lam=LAM, dl=0.005):
    """n_g = n_eff - lam * dn_eff/dlam, with a central difference over +-5 nm."""
    return neff_of_lam(lam) - lam * (neff_of_lam(lam + dl) - neff_of_lam(lam - dl)) / (2 * dl)


# ---------------------------------------------------------------------------------------------------------
# Part D. The effective-index method for strips and ribs (Chapter 6, Section 6.2)
# ---------------------------------------------------------------------------------------------------------
def eim(width, t, slab, lam=LAM, te=True, n_core=N_SI, n_clad=N_OX):
    """Effective index of the fundamental mode of a strip (slab = 0) or rib (slab > 0) by the EIM.

    1. Vertical slabs: the core region (thickness t) gives n_I, the region beside it (thickness slab) n_II.
    2. Lateral slab of width `width` between n_II claddings, with the other polarisation's boundary
       conditions: a TE-like mode's field is normal to the side walls, so the lateral slab is solved as TM.
    """
    n_I = slab_modes(n_core, n_clad, n_clad, t, lam, tm=not te)[0]
    n_II = slab_modes(n_core, n_clad, n_clad, slab, lam, tm=not te)[0] if slab > 0 else n_clad
    lateral = slab_modes(n_I, n_II, n_II, width, lam, tm=te)
    return lateral[0] if lateral else float('nan')


# Reference: femwell's full vectorial solutions for 220 nm strips in oxide at 1550 nm (Chapter 6, figsrc/ch06_sweep.py)
FEMWELL_W = np.round(np.arange(0.25, 1.001, 0.05), 2)
FEMWELL_TE0 = np.array([1.6020, 1.8272, 2.0537, 2.2276, 2.3537, 2.4459, 2.5148, 2.5675, 2.6086, 2.6413, 2.6677, 2.6893,
                        2.7073, 2.7224, 2.7352, 2.7461])
FEMWELL_TM0 = np.array([1.5419, 1.5930, 1.6440, 1.6914, 1.7337, 1.7707, 1.8026, 1.8301, 1.8537, 1.8741, 1.8916, 1.9068,
                        1.9201, 1.9317, 1.9419, 1.9509])
FEMWELL_NG_TE0 = np.array([2.982, 4.099, 4.416, 4.379, 4.278, 4.184, 4.106, 4.044, 3.994, 3.954, 3.921, 3.894, 3.872,
                           3.853, 3.837, 3.824])


def first_width_with(n_modes_wanted, n_I, n_II, lam=LAM, tm=True, lo=0.05, hi=2.0):
    """Smallest lateral width at which the lateral slab guides n_modes_wanted modes (a cut-off), by bisection."""
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if len(slab_modes(n_I, n_II, n_II, mid, lam, tm)) >= n_modes_wanted:
            hi = mid
        else:
            lo = mid
    return hi


def main(plot=True):
    print("Lab 1: slab and channel waveguide modes (lengths in um, wavelength 1.55 um)\n")

    # ---- Part A
    te = slab_modes(N_SI, N_OX, N_OX, 0.22, LAM)
    tm = slab_modes(N_SI, N_OX, N_OX, 0.22, LAM, tm=True)
    print("A. 220 nm silicon film in oxide")
    print(f"   TE modes: {np.round(te, 4)}   (Chapter 5: one mode, n_eff = 2.848)")
    print(f"   TM modes: {np.round(tm, 4)}   (Chapter 5: one mode, n_eff = 2.053)")
    air = slab_modes(N_SI, N_OX, 1.0, 0.22, LAM)
    print(f"   with an air cover instead of oxide: TE0 n_eff = {air[0]:.4f} (the asymmetric slab)\n")

    # ---- Part B
    ne = te[0]
    k0 = 2 * np.pi / LAM
    gamma = k0 * np.sqrt(ne**2 - N_OX**2)
    G = confinement(ne, N_SI, N_OX, N_OX, 0.22, LAM)
    print("B. The TE0 mode of the 220 nm film")
    print(f"   evanescent decay length 1/gamma = {1000 / gamma:.0f} nm   (Chapter 5: 101 nm)")
    print(f"   confinement factor Gamma = {G:.3f}            (Chapter 5: 0.81)")
    print(f"   ray angle from the normal = {np.degrees(np.arcsin(ne / N_SI)):.1f} deg\n")

    # ---- Part B, continued: modes against thickness and the single-mode limit
    d_cut = LAM / (2 * np.sqrt(N_SI**2 - N_OX**2))
    lo, hi = 0.1, 0.5                                # bisection on the thickness where TE1 appears
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if len(slab_modes(N_SI, N_OX, N_OX, mid, LAM)) >= 2:
            hi = mid
        else:
            lo = mid
    print("   single-mode limit of the symmetric film:")
    print(f"   formula lambda / (2 sqrt(n1^2 - n2^2)) = {1000 * d_cut:.1f} nm; bisection on the solver = {1000 * hi:.1f} nm"
          "   (Chapter 5: 245 nm)\n")

    # ---- Part C
    ng_te = group_index(lambda l: slab_modes(n_si(l), n_ox(l), n_ox(l), 0.22, l)[0])
    ng_tm = group_index(lambda l: slab_modes(n_si(l), n_ox(l), n_ox(l), 0.22, l, tm=True)[0])
    ng_bulk = group_index(n_si)
    print("C. Group index of the 220 nm film, waveguide plus material dispersion")
    print(f"   TE0 n_g = {ng_te:.2f}, TM0 n_g = {ng_tm:.2f}   (Chapter 5: 3.70 and 3.96); bulk silicon {ng_bulk:.2f}\n")

    # ---- Part D
    n_eim = eim(0.5, 0.22, 0.0)
    n_I = slab_modes(N_SI, N_OX, N_OX, 0.22, LAM)[0]
    w_te1 = first_width_with(2, n_I, N_OX)
    print("D. Effective-index method for a 500 x 220 nm strip")
    print(f"   TE0: EIM {n_eim:.3f} against femwell {FEMWELL_TE0[FEMWELL_W == 0.5][0]:.3f}   (Chapter 6: 2.49 and 2.446)")
    print(f"   TM0: EIM {eim(0.5, 0.22, 0.0, te=False):.3f} against femwell {FEMWELL_TM0[FEMWELL_W == 0.5][0]:.3f}")
    print(f"   TE1 appears at a width of {1000 * w_te1:.0f} nm by the EIM; femwell finds it between 400 and 450 nm"
          "   (Chapter 6: ~320 and ~450 nm)")
    ng_eim = group_index(lambda l: eim(0.5, 0.22, 0.0, lam=l, n_core=n_si(l), n_clad=n_ox(l)))
    print(f"   group index: EIM {ng_eim:.2f} against femwell {FEMWELL_NG_TE0[FEMWELL_W == 0.5][0]:.2f}   (Chapter 6: 4.18)")
    print(f"   a rib, 500 nm wide, 220 nm etched to a 90 nm slab: EIM TE0 n_eff = {eim(0.5, 0.22, 0.09):.3f}"
          "   (femwell, Table 6.1: 2.568)")
    widths = FEMWELL_W
    errs = np.array([eim(w, 0.22, 0.0) for w in widths]) - FEMWELL_TE0
    print(f"   EIM minus femwell over 250-1000 nm: from {errs.max():+.3f} (narrowest) to {errs.min():+.3f} (widest)\n")

    if plot:
        make_figure(te, ne, widths)


def make_figure(te, ne, widths):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    # (a) effective index of every mode against film thickness
    ds = np.linspace(0.02, 1.0, 200)
    for tm, col, lab in ((False, "tab:blue", "TE"), (True, "tab:orange", "TM")):
        modes = [slab_modes(N_SI, N_OX, N_OX, d, LAM, tm) for d in ds]
        for m in range(max(len(x) for x in modes)):
            ax[0, 0].plot(ds, [x[m] if len(x) > m else np.nan for x in modes], color=col, lw=1.4,
                          label=lab if m == 0 else None)
    ax[0, 0].axvline(0.22, color="grey", ls=":", lw=0.8)
    ax[0, 0].set(xlabel="film thickness d (µm)", ylabel="effective index", title="(a) slab modes, 1550 nm")
    ax[0, 0].legend()
    # (b) the TE0 field of the 220 nm film
    x = np.linspace(-0.6, 0.82, 800)
    E = te_field(ne, N_SI, N_OX, N_OX, 0.22, LAM, x)
    ax[0, 1].axvspan(0, 0.22, color="0.85", label="silicon film")
    ax[0, 1].plot(x, E / E.max(), color="tab:blue")
    ax[0, 1].set(xlabel="x (µm)", ylabel="E_y (normalised)", title="(b) TE0 field, 220 nm film")
    ax[0, 1].legend()
    # (c) group index against thickness
    dg = np.linspace(0.1, 1.0, 46)
    for tm, col, lab in ((False, "tab:blue", "TE0"), (True, "tab:orange", "TM0")):
        ax[1, 0].plot(dg, [group_index(lambda l: slab_modes(n_si(l), n_ox(l), n_ox(l), d, l, tm)[0]) for d in dg],
                      color=col, label=lab)
    ax[1, 0].axhline(group_index(n_si), color="grey", ls=":", lw=0.8)
    ax[1, 0].set(xlabel="film thickness d (µm)", ylabel="group index", title="(c) group index (with material dispersion)")
    ax[1, 0].legend()
    # (d) EIM against femwell for 220 nm strips
    ax[1, 1].plot(widths, FEMWELL_TE0, "o", color="tab:blue", ms=4, label="TE0, femwell")
    ax[1, 1].plot(widths, [eim(w, 0.22, 0.0) for w in widths], color="tab:blue", label="TE0, EIM")
    ax[1, 1].plot(widths, FEMWELL_TM0, "o", color="tab:orange", ms=4, label="TM0, femwell")
    ax[1, 1].plot(widths, [eim(w, 0.22, 0.0, te=False) for w in widths], color="tab:orange", label="TM0, EIM")
    ax[1, 1].set(xlabel="strip width W (µm)", ylabel="effective index", title="(d) 220 nm strips: EIM against femwell")
    ax[1, 1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("lab01_slab.png", dpi=150)
    print("Saved the figure as lab01_slab.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
