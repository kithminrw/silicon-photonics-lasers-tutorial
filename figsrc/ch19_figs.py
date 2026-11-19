"""Figures and numbers for Chapter 19 (electro-optic effects across platforms).

Run from the worktree root:   python -I -X utf8 figsrc/ch19_figs.py
Writes assets/figs/ch19_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.

- Soref-Bennett relations at 1550 nm as in the chapter's key equation.
- PN phase shifter: the femwell sensitivity weights of figsrc/ch19_pn.json (500 x 220 nm rib, 90 nm slab) and the same
  abrupt-junction / Soref-Bennett sum as figsrc/ch19_pn.py, re-evaluated here on a fine bias grid (NumPy only).
- TFLN electrodes: a 2D electrostatic finite-difference solution (anisotropic permittivity) for the field lines.
- Franz-Keldysh: the textbook Airy-function absorption of a direct edge, in arbitrary units (shape only).
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55                      # um
DB = 10 / np.log(10)            # 1/cm -> dB/cm


def soref(N, P):
    """Soref-Bennett at 1550 nm (cm^-3) -> (delta n, delta alpha in 1/cm)."""
    return -(8.8e-22 * N + 8.5e-18 * P ** 0.8), 8.5e-18 * N + 6.0e-18 * P


# ------------------------------------------------------------------ Figure 19.1: Soref-Bennett
def fig_soref():
    Nn = np.logspace(16, 19, 301)
    dn_e, da_e = -soref(Nn, 0)[0], soref(Nn, 0)[1]
    dn_h, da_h = -soref(0, Nn)[0], soref(0, Nn)[1]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.75), gridspec_kw=dict(wspace=0.38))
    a.loglog(Nn, dn_h, color=C4, label="holes, $\\Delta P$")
    a.loglog(Nn, dn_e, color=C1, label="electrons, $\\Delta N$")
    for d, col, va, dy, xf, ha in ((dn_h[200], C4, "bottom", 1.25, 1 / 1.25, "right"), (dn_e[200], C1, "top", 0.8, 1.25, "left")):
        a.plot(1e18, d, "o", color=col, ms=4)
        a.text(1e18 * xf, d * dy, f"{d*1e3:.2f} × 10$^{{-3}}$", ha=ha, va=va, fontsize=7, color=col)
    a.set_xlim(1e16, 1e19); a.set_ylim(1e-5, 2e-2)
    finish(a, "Carrier density change (cm$^{-3}$)", "Index change $|\\Delta n|$", legend=True, loc="upper left")
    tag(a, "a")
    b.loglog(DB * da_h, dn_h, color=C4, label="holes")
    b.loglog(DB * da_e, dn_e, color=C1, label="electrons")
    for N, lab in ((1e17, "10$^{17}$"), (1e18, "10$^{18}$")):
        for (dn, da), col, off in ((soref(0, N), C4, (-1, 1)), (soref(N, 0), C1, (1, -1))):
            b.plot(DB * da, -dn, "o", color=col, ms=4)
            b.text(DB * da * (0.8 if off[0] < 0 else 1.25), -dn * (1.12 if off[1] > 0 else 0.86), lab + " cm$^{-3}$",
                   ha="right" if off[0] < 0 else "left", va="bottom" if off[1] > 0 else "top", fontsize=6.6, color=col)
    b.set_xlim(0.3, 300); b.set_ylim(1e-5, 2e-2)
    finish(b, "Absorption (dB/cm)", "Index change $|\\Delta n|$", legend=True, loc="upper left")
    tag(b, "b")
    save(fig, "ch19_soref")
    h, e = soref(0, 1e18), soref(1e18, 0)
    print(f"[19.1] 1e18: holes dn {-h[0]:.3e}, alpha {h[1]:.2f} /cm = {DB*h[1]:.1f} dB/cm; electrons dn {-e[0]:.3e}, "
          f"alpha {e[1]:.2f} /cm = {DB*e[1]:.1f} dB/cm; index per unit loss, holes/electrons = {(-h[0]/h[1])/(-e[0]/e[1]):.2f}")
    h, e = soref(0, 1e17), soref(1e17, 0)
    print(f"[19.1] 1e17: holes dn {-h[0]:.3e} at {DB*h[1]:.2f} dB/cm; electrons dn {-e[0]:.3e} at {DB*e[1]:.2f} dB/cm; "
          f"ratio {(-h[0]/h[1])/(-e[0]/e[1]):.2f}")


# ------------------------------------------------------------------ PN junction model (as figsrc/ch19_pn.py)
PN = json.load(open(os.path.join(HERE, "ch19_pn.json")))
XB = np.array(PN["x"]); WB = np.array(PN["w"]); EDGES = np.r_[XB - 0.01, XB[-1] + 0.01]
Q, EPS0, KT, NI = 1.602e-19, 8.854e-12, 0.02585, 1.0e10


def depletion(Na, Nd, V):
    vbi = KT * np.log(Na * Nd / NI ** 2)
    na, nd = Na * 1e6, Nd * 1e6
    Wd = np.sqrt(2 * 11.7 * EPS0 * (vbi + V) * (na + nd) / (Q * na * nd))
    return 1e6 * Wd * nd / (na + nd), 1e6 * Wd * na / (na + nd), vbi


def dneff(Na, Nd, V, xj=0.0, contact=1.2, Nc=1e20):
    xp, xn, _ = depletion(Na, Nd, V)
    def seg(a, b, lo, hi):
        return max(0.0, min(b, hi) - max(a, lo))
    def cplx(N, P):
        d_n, d_a = soref(N, P)
        return d_n + 1j * d_a * 100 * LAM * 1e-6 / (4 * np.pi)
    tot = 0j
    for a, b, wv in zip(EDGES[:-1], EDGES[1:], WB):
        tot += wv * (seg(a, b, -9, -contact) * cplx(0, Nc) + seg(a, b, -contact, xj - xp) * cplx(0, Na)
                     + seg(a, b, xj + xn, contact) * cplx(Nd, 0) + seg(a, b, contact, 9) * cplx(Nc, 0))
    return complex(tot)


def vpil(N, V):
    return LAM * 1e-4 / (2 * (dneff(N, N, V) - dneff(N, N, 0)).real) * V      # V cm


def loss0(N):
    return 4 * np.pi * dneff(N, N, 0).imag / (LAM * 1e-6) / 100 * DB          # dB/cm


# ------------------------------------------------------------------ Figure 19.2: PN, PIN and MOS structures
def _doped(ax, xa, xb, mat, rib=True, z=2):
    """A doped region [xa, xb] of the 220 nm rib / 90 nm slab."""
    box(ax, xa, 0, xb - xa, 0.09, mat, z=z)
    lo, hi = max(xa, -0.25), min(xb, 0.25)
    if rib and hi > lo:
        box(ax, lo, 0.09, hi - lo, 0.13, mat, z=z)


def _frame(ax, ytop):
    box(ax, -3.3, -0.32, 6.6, 0.32, "ox", z=0)
    box(ax, -3.3, 0, 6.6, ytop, "oxtop", z=0)
    ax.text(-3.22, -0.16, "BOX", fontsize=FS_SMALL, color=MUTED, va="center")


def _via(ax, x, top, text, col=INK):
    box(ax, x - 0.2, 0.09, 0.4, top - 0.09, "metal", z=3)
    ax.text(x, top + 0.03, text, ha="center", va="bottom", fontsize=FS_SMALL, color=col)


def fig_structures():
    N = 5e17
    xp0, xn0, vbi = depletion(N, N, 0.0); xp2, xn2, _ = depletion(N, N, 2.0)
    fig = plt.figure(figsize=(6.3, 3.0))
    rows = [0.675, 0.345, 0.015]
    ylim = (-0.34, 0.86); xlim = (-3.3, 3.3)
    axes = [fig.add_axes([0.0, r, 0.70, 0.31]) for r in rows]
    for ax in axes:
        frameless(ax, xlim, ylim)
    # (a) PN, depletion
    ax = axes[0]; _frame(ax, 0.62)
    _doped(ax, -3.3, -1.2, "pp"); _doped(ax, -1.2, -xp2, "pdop"); _doped(ax, xn2, 1.2, "ndop"); _doped(ax, 1.2, 3.3, "nn")
    box(ax, -xp2, 0, xp2 + xn2, 0.22, "#FFFFFF", ec=MUTED, lw=0.4, z=3)
    _via(ax, -2.3, 0.62, "0 V"); _via(ax, 2.3, 0.62, "+V (reverse)")
    label(ax, -0.75, 0.3, "p", fs=FS); label(ax, 0.75, 0.3, "n", fs=FS)
    label(ax, -1.65, 0.3, "p$^{++}$", fs=FS_SMALL); label(ax, 1.65, 0.3, "n$^{++}$", fs=FS_SMALL)
    callout(ax, (0.03, 0.02), (0.45, -0.17), f"depleted, {1e3*(xp2+xn2):.0f} nm at 2 V", ha="left")
    scalebar(ax, 2.2, -0.29, 1.0, "1 µm")
    panel(ax, "a", x=0.0, y=1.0)
    # (b) PIN, injection
    ax = axes[1]; _frame(ax, 0.62)
    _doped(ax, -3.3, -0.75, "pp", rib=False); _doped(ax, -0.75, 0.75, "si"); _doped(ax, 0.75, 3.3, "nn", rib=False)
    rng = np.random.default_rng(3)
    for col in (RED, BLUE):
        xs = rng.uniform(-0.23, 0.23, 26); ys = rng.uniform(0.02, 0.2, 26)
        ax.plot(xs, ys, "o", ms=1.6, color=col, mec="none", zorder=4)
    _via(ax, -2.3, 0.62, "+V (forward)"); _via(ax, 2.3, 0.62, "0 V")
    label(ax, -1.65, 0.3, "p$^{++}$", fs=FS_SMALL); label(ax, 1.65, 0.3, "n$^{++}$", fs=FS_SMALL)
    callout(ax, (0.12, 0.03), (0.45, -0.17), "injected electrons and holes", ha="left")
    label(ax, -0.55, 0.3, "i", fs=FS, italic=True)
    panel(ax, "b", x=0.0, y=1.0)
    # (c) MOS capacitor (SISCAP): n-Si rib, thin gate oxide, p-poly on top (illustrative dimensions)
    ax = axes[2]; _frame(ax, 0.62)
    tox = 0.03                                    # drawn; a real gate oxide is a few nm
    box(ax, -0.25, 0, 3.55, 0.09, "ndop", z=2); box(ax, -0.25, 0.09, 0.5, 0.13, "ndop", z=2); box(ax, 1.2, 0, 2.1, 0.09, "nn", z=2)
    box(ax, -0.25, 0.22, 0.5, tox, "ox", ec=INK, lw=0.3, z=3)
    box(ax, -3.3, 0.22 + tox, 3.55, 0.2, "pdop", z=2); box(ax, -3.3, 0.22 + tox, 1.55, 0.2, "pp", z=2)
    ax.plot([-0.24, 0.24], [0.205, 0.205], color=BLUE, lw=1.6, zorder=4, solid_capstyle="butt")
    ax.plot([-0.24, 0.24], [0.268, 0.268], color=RED, lw=1.6, zorder=4, solid_capstyle="butt")
    box(ax, -2.5, 0.22 + tox + 0.2, 0.4, 0.62 - 0.45 - tox, "metal", z=3)
    ax.text(-2.3, 0.65, "+V", ha="center", va="bottom", fontsize=FS_SMALL, color=INK)
    _via(ax, 2.3, 0.62, "0 V")
    label(ax, -1.0, 0.56, "p poly-Si", fs=FS_SMALL); label(ax, 0.75, 0.3, "n", fs=FS); label(ax, 1.65, 0.3, "n$^{++}$", fs=FS_SMALL)
    callout(ax, (-0.1, 0.2), (-0.35, -0.17), "accumulated charge", ha="right")
    note(ax, "illustrative; oxide drawn thicker", loc="lower right")
    panel(ax, "c", x=0.0, y=1.0)
    # right-hand descriptions
    txt = [("Depletion (PN)", f"Reverse bias widens the depleted\ngap: {1e3*(xp0+xn0):.0f} nm at 0 V, {1e3*(xp2+xn2):.0f} nm at 2 V\n(5 × 10$^{{17}}$ cm$^{{-3}}$). Fast, small Δn."),
           ("Injection (PIN)", "Forward bias floods the intrinsic\nwaveguide with carriers. Large Δn,\n~1 ns recombination: slow."),
           ("Accumulation (MOS)", "Charge piles up on both sides of\na thin oxide where the mode is\nstrongest. Large Δn per volt,\nhigh capacitance.")]
    for r, (t1, t2) in zip(rows, txt):
        fig.text(0.715, r + 0.255, t1, fontsize=7.6, fontweight="bold", color=INK, va="top")
        fig.text(0.715, r + 0.175, t2, fontsize=6.7, color=INK, va="top", linespacing=1.25)
    save(fig, "ch19_junctions")
    print(f"[19.2] 5e17: Vbi {vbi:.3f} V, W {1e3*(xp0+xn0):.1f} nm at 0 V, {1e3*(xp2+xn2):.1f} nm at 2 V")


# ------------------------------------------------------------------ Figure 19.3: three dopings
def fig_dopings():
    Ns = (2e17, 5e17, 1e18); cols = (C3, C1, C4); labs = ("2 × 10$^{17}$", "5 × 10$^{17}$", "1 × 10$^{18}$")
    Vs = np.linspace(0.25, 4, 31)
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7), gridspec_kw=dict(wspace=0.36, width_ratios=[1.1, 1]))
    pts = []
    for N, col, lab, case in zip(Ns, cols, labs, PN["cases"]):
        a.plot(Vs, [vpil(N, V) for V in Vs], color=col, label=lab + " cm$^{-3}$")
        a.plot(2.0, vpil(N, 2.0), "o", color=col, ms=4)
        v2, l0 = vpil(N, 2.0), loss0(N)
        pts.append((v2, l0))
        print(f"[19.3] N {N:.0e}: VpiL at 1/2/4 V = {vpil(N,1):.2f}/{v2:.2f}/{vpil(N,4):.2f} V cm (json 2 V: "
              f"{[r['VpiL_Vcm'] for r in case['rows'] if r['V']==2][0]:.2f}); loss 0 V {l0:.2f} dB/cm "
              f"(json {case['loss_dB_cm']:.2f}); loss x VpiL {l0*v2:.1f} dB V; W0 {1e3*sum(depletion(N,N,0)[:2]):.0f} nm")
    a.set_xlim(0, 4); a.set_ylim(0, 2.8)
    finish(a, "Reverse bias (V)", "$V_\\pi L$ (V·cm)", legend=True, loc="upper left")
    tag(a, "a")
    vv = np.linspace(0.6, 3.0, 50)
    for c in (10, 20, 30):
        b.plot(vv, c / vv, color=MUTED, lw=0.7, ls=":")
        b.text(2.97, c / 2.97 + 0.4, f"{c} dB·V", fontsize=6.3, color=MUTED, ha="right", va="bottom")
    for (v2, l0), col, lab in zip(pts, cols, labs):
        b.plot(v2, l0, "o", color=col, ms=5)
        b.text(v2 + 0.08, l0 + 0.8, lab, fontsize=6.8, color=col, ha="left", va="bottom")
    b.set_xlim(0.6, 3.0); b.set_ylim(0, 35)
    finish(b, "$V_\\pi L$ at 2 V (V·cm)", "Loss at 0 V (dB/cm)")
    tag(b, "b")
    save(fig, "ch19_dopings")


# ------------------------------------------------------------------ Figure 19.4: TFLN push-pull electrodes
def laplace_tfln():
    h = 0.05
    x = np.arange(-20, 20 + h / 2, h); y = np.arange(-3.0, 6.0 + h / 2, h)
    nx, ny = len(x), len(y)
    xc, yc = 0.5 * (x[1:] + x[:-1]), 0.5 * (y[1:] + y[:-1])
    XC, YC = np.meshgrid(xc, yc)
    ex = np.ones_like(XC); ey = np.ones_like(XC)                        # air
    sub = YC < -2.0; box_ = (YC >= -2.0) & (YC < 0)
    ex[sub] = ey[sub] = 11.7; ex[box_] = ey[box_] = 3.9
    film = (YC >= 0) & (YC < 0.3)
    ridge = np.zeros_like(film)
    for xr in (-5.5, 5.5):                                            # ridges in the two gaps, sidewalls ~60 deg
        hw = 0.6 + (0.6 - (YC - 0.3)) * 0.3 / 0.3 * 0.29
        ridge |= (YC >= 0.3) & (YC < 0.6) & (np.abs(XC - xr) <= hw)
    ln = film | ridge
    ex[ln] = 28.0; ey[ln] = 44.0                                      # x-cut: crystal z horizontal, x vertical (clamped)
    X, Y = np.meshgrid(x, y)
    fixed = np.zeros((ny, nx), bool); phi = np.zeros((ny, nx))
    tol = 1e-9                                                         # grid lines at 0.3, 3 and 8 um are not exact in floating point
    el_y = (Y >= 0.3 - tol) & (Y <= 1.1 + tol)
    sig = el_y & (np.abs(X) <= 3.0 + tol); gnd = el_y & (np.abs(X) >= 8.0 - tol)
    fixed |= sig | gnd; phi[sig] = 1.0
    # edge coefficients: x-edges average the cells above and below, y-edges the cells left and right
    Ax = np.zeros((ny, nx - 1)); Ax[:-1] += ex; Ax[1:] += ex; Ax[1:-1] /= 2
    Ay = np.zeros((ny - 1, nx)); Ay[:, :-1] += ey; Ay[:, 1:] += ey; Ay[:, 1:-1] /= 2
    AL = np.pad(Ax, ((0, 0), (1, 0))); AR = np.pad(Ax, ((0, 0), (0, 1)))
    AD = np.pad(Ay, ((1, 0), (0, 0))); AU = np.pad(Ay, ((0, 1), (0, 0)))
    S = AL + AR + AD + AU
    J, I = np.meshgrid(np.arange(ny), np.arange(nx), indexing="ij")
    masks = [((I + J) % 2 == p) & ~fixed for p in (0, 1)]
    phi[~fixed] = 0.5
    om = 1.985
    for it in range(6000):
        dmax = 0
        for m in masks:
            nb = AL * np.roll(phi, 1, 1) + AR * np.roll(phi, -1, 1) + AD * np.roll(phi, 1, 0) + AU * np.roll(phi, -1, 0)
            d = nb[m] / S[m] - phi[m]
            phi[m] += om * d
            dmax = max(dmax, np.abs(d).max())
        if dmax < 1e-7:
            break
    print(f"[19.4] SOR converged in {it+1} iterations (last max update {dmax:.1e})")
    return x, y, phi


def fig_tfln():
    x, y, phi = laplace_tfln()
    Ey, Ex = np.gradient(-phi, y, x)
    g = 5.0
    j = np.argmin(abs(y - 0.45))
    for xr in (-5.5, 5.5):
        i = np.argmin(abs(x - xr))
        print(f"[19.4] ridge at x = {xr:+.1f} um: E_x = {Ex[j, i]:+.3f} V/um per volt, i.e. {abs(Ex[j, i])*g:.2f} of V/g")
    fig, ax = geom_axes(figsize=(6.3, 2.15), xlim=(-12.5, 12.5), ylim=(-2.6, 3.65))
    box(ax, -12.5, -2.6, 25, 0.6, "sub", z=0); box(ax, -12.5, -2.0, 25, 2.0, "ox", z=0)
    box(ax, -12.5, 0, 25, 0.3, "ln", z=1)
    for xr in (-5.5, 5.5):
        trapezoid(ax, xr, 0.3, 1.2 + 2 * 0.17, 1.2, 0.3, "ln", z=1)
    for xa, xb, t in ((-12.5, -8, "G"), (-3, 3, "S"), (8, 12.5, "G")):
        box(ax, xa, 0.3, xb - xa, 0.8, "metal", z=4)
        label(ax, (xa + xb) / 2 + (0.6 if xa < -12 else -0.6 if xb > 12 else 0), 0.7, t, bold=True, fs=8)
    sel = (np.abs(x) <= 12.6)
    xs, Exs, Eys, Ps = x[sel], Ex[:, sel], Ey[:, sel], phi[:, sel]
    seeds = [(xr, yy) for xr in (-5.5, 5.5) for yy in np.r_[np.linspace(-1.9, -0.15, 5), 0.45, 1.3, 1.9, 2.5]]
    ax.streamplot(xs, y, Exs, Eys, start_points=seeds, integration_direction="both", color=INK, linewidth=0.6,
                  arrowsize=0.6, density=4, broken_streamlines=False, zorder=3)
    for xr, s in ((-5.5, -1), (5.5, 1)):
        arrow(ax, (xr - s * 0.55, 0.45), (xr + s * 0.55, 0.45), col=RED, lw=1.4, ms=7, z=6)
        label(ax, xr, 0.98, "−Δn" if s > 0 else "+Δn", col=RED, fs=7, bold=True, z=7)
    dim(ax, (3.0, 3.05), (8.0, 3.05), f"g = {g:.0f} µm", text_off=(0, 0.3), bg=None)
    arrow(ax, (-12.0, 3.05), (-10.2, 3.05), col=INK, lw=0.9, ms=6); label(ax, -9.9, 3.05, "crystal $z$", ha="left", fs=FS_SMALL)
    label(ax, -12.3, -1.55, "SiO$_2$", ha="left", fs=FS_SMALL); label(ax, -12.3, -2.3, "Si", ha="left", fs=FS_SMALL)
    callout(ax, (-11.2, 0.15), (-12.3, -0.7), "x-cut LiNbO$_3$ film", ha="left", va="center")
    scalebar(ax, 9.0, -2.45, 2.0, "2 µm")
    save(fig, "ch19_tfln")


# ------------------------------------------------------------------ Figure 19.5: Franz-Keldysh
AI0, AIP0 = 0.355028053887817, 0.258819403792807


def airy(xv):
    """Ai and Ai' from the Maclaurin series (|x| <= 5) and the asymptotic form beyond (x > 5)."""
    xv = np.atleast_1d(np.asarray(xv, float)); ai = np.zeros_like(xv); aip = np.zeros_like(xv)
    for k, x in enumerate(xv):
        if x > 5:
            z = 2 / 3 * x ** 1.5; e = np.exp(-z) / (2 * np.sqrt(np.pi))
            ai[k] = e / x ** 0.25 * (1 - 5 / (72 * z)); aip[k] = -e * x ** 0.25 * (1 + 7 / (72 * z))
            continue
        f, fp, g, gp = 0.0, 0.0, 0.0, 0.0
        tf, tg = 1.0, x                           # terms of f (powers 3n) and g (powers 3n+1)
        for n in range(0, 120):
            p = 3 * n
            f += tf; g += tg
            if p > 0: fp += tf * p / x
            gp += tg * (p + 1) / x if x != 0 else (1.0 if n == 0 else 0.0)
            tf *= x ** 3 / ((p + 2) * (p + 3)); tg *= x ** 3 / ((p + 3) * (p + 4))
            if abs(tf) < 1e-18 and abs(tg) < 1e-18 and n > 3: break
        ai[k] = AI0 * f - AIP0 * g; aip[k] = AI0 * fp - AIP0 * gp
    return ai, aip


def fk_alpha(E, Eg, th):
    """Direct-edge absorption (arb. units) at photon energy E (eV), field energy th (eV); th = 0: sqrt edge."""
    if th == 0:
        return np.sqrt(np.clip(E - Eg, 0, None)) / np.pi / E
    eta = (Eg - E) / th
    ai, aip = airy(eta)
    return np.sqrt(th) * (aip ** 2 - eta * ai ** 2) / E


def fig_fk():
    Eg = 0.80                                     # eV: direct gap of Ge, ~1550 nm (the chapter's number)
    E = np.linspace(Eg - 0.09, Eg + 0.05, 600)
    lam = 1.23984 / E
    fig = plt.figure(figsize=(6.3, 2.6))
    # (a) tilted bands and photon-assisted tunnelling
    ax = fig.add_axes([0.0, 0.04, 0.42, 0.90]); frameless(ax, (0, 10.6), (-2.3, 6.4), equal=False)
    xx = np.array([0.4, 9.6]); slope = -0.3
    Ec = lambda x: 5.4 + slope * (x - 0.4); Ev = lambda x: 1.6 + slope * (x - 0.4)
    ax.plot(xx, Ec(xx), color=INK, lw=1.6); ax.plot(xx, Ev(xx), color=INK, lw=1.6)
    ax.text(9.75, Ec(9.6), "$E_c$", fontsize=7.5, va="center"); ax.text(9.75, Ev(9.6), "$E_v$", fontsize=7.5, va="center")
    for xi in np.linspace(0.6, 9.4, 15):          # filled valence band
        ax.plot([xi, xi], [Ev(xi) - 0.8, Ev(xi)], color=MUTED, lw=0.4, alpha=0.5)
    x0 = 2.6; yv = Ev(x0); ytop = yv + 2.7        # photon energy below the gap (3.8 units)
    arrow(ax, (x0, yv), (x0, ytop), col=RED, lw=1.5, ms=8)
    ax.text(x0 + 0.2, yv + 1.0, r"$\hbar\omega < E_g$", ha="left", va="center", fontsize=7.5, color=RED)
    xc = 0.4 + (5.4 - ytop) / (-slope)            # where that energy meets the conduction band
    arrow(ax, (x0, ytop), (xc, ytop), col=BLUE, lw=1.1, ms=7, ls=(0, (3, 2)))
    ax.text((x0 + xc) / 2, ytop + 0.3, "tunnels", ha="center", va="bottom", fontsize=7, color=BLUE)
    ax.plot(xc, ytop, "o", color=BLUE, ms=3.5)
    xg = 1.0
    dim(ax, (xg, Ev(xg)), (xg, Ec(xg)), "", lw=0.6)
    ax.text(xg - 0.15, (Ev(xg) + Ec(xg)) / 2, "$E_g$", fontsize=7.5, va="center", ha="right")
    arrow(ax, (9.4, 5.9), (7.4, 5.9), col=INK, lw=0.9, ms=6); ax.text(9.6, 5.9, "$F$", ha="left", va="center", fontsize=7.5)
    ax.text(8.4, 5.55, "field tilts the bands", ha="center", va="top", fontsize=6.6)
    note(ax, "schematic", loc="lower right")
    panel(ax, "a", x=0.0, y=1.0)
    # (b) absorption edge with and without field
    b = fig.add_axes([0.52, 0.17, 0.46, 0.77])
    a0 = fk_alpha(E, Eg, 0.0); a1 = fk_alpha(E, Eg, 0.012); a2 = fk_alpha(E, Eg, 0.025)
    ref = fk_alpha(np.array([Eg + 0.05]), Eg, 0.0)[0]
    for a_, col, lab in ((a0, C6, "no field"), (a1, C2, "field"), (a2, C4, "stronger field")):
        b.semilogy(lam * 1e3, np.maximum(a_ / ref, 1e-4), color=col, label=lab)
    lop = 1.23984 / (Eg - 0.02) * 1e3; ledge = 1.23984 / Eg * 1e3
    b.axvline(lop, color=MUTED, lw=0.7, ls="--")
    b.text(lop + 3, 1.5e-3, "$\\lambda_\\mathrm{op}$", fontsize=7.5, color=MUTED, ha="left", va="bottom")
    b.text(ledge - 2, 1.5e-3, "edge", fontsize=6.8, color=C6, ha="right", va="bottom")
    ia = fk_alpha(np.array([Eg - 0.02]), Eg, 0.025)[0] / ref
    b.plot(lop, ia, "o", color=C4, ms=4)
    b.text(lop + 3, ia * 1.3, "field on: absorbs", fontsize=6.8, color=C4, ha="left", va="bottom")
    b.text(lop + 3, 4e-3, "0 V: transparent", fontsize=6.8, color=C6, ha="left", va="bottom")
    b.set_xlim(1.23984 / (Eg + 0.045) * 1e3, 1.23984 / (Eg - 0.085) * 1e3); b.set_ylim(1e-3, 2)
    b.set_xticks([]); b.set_yticks([]); b.minorticks_off()
    finish(b, "Wavelength →", "Absorption (log scale)", legend=True, loc="upper right")
    b.grid(False)
    tag(b, "b")
    save(fig, "ch19_fk")
    print(f"[19.5] edge at {ledge:.0f} nm (Eg {Eg} eV); operating wavelength drawn {lop:.0f} nm; "
          f"absorption at lambda_op relative to 50 meV above the edge: {fk_alpha(np.array([Eg-0.02]), Eg, 0.012)[0]/ref:.3f}, "
          f"{fk_alpha(np.array([Eg-0.02]), Eg, 0.025)[0]/ref:.3f}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["soref", "structures", "dopings", "tfln", "fk"]
    for w in which:
        globals()["fig_" + w]()
