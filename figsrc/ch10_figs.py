"""Figures for Chapter 10 (Y-branches and MMIs).
Run from the worktree root: python -I -X utf8 figsrc/ch10_figs.py   (set FIGPREVIEW for PNG previews)

MMI model: the chapter's 2D effective-index picture of a 220 nm silicon MMI at 1550 nm, slab index n_r = 2.85 in
oxide n_c = 1.444, TE-like modes with E normal to the side walls, so the lateral problem is TM (sigma = 1). The
lateral modes are solved by finite differences (H_y, with (1/n^2) dH/dx continuous), not taken as ideal sines, so
the images show the small blur of the real, not exactly quadratic, mode spacing. Access waveguides: 1.5 um wide
(tapered, Section 10.4). Coupling at the junctions by overlaps in the MMI's own weighting, reflections neglected:
the eigenmode expansion of Lab 3.
The Y-branch profiles come from femwell (figsrc/ch09_fields.py -> ch09_fields.json).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
NR, NC, LAM0, W, WA = 2.85, 1.444, 1.55, 6.0, 1.5
XG = 1.4          # port offset of the general-interference 2 x 2 (excites every low-order mode; W/4 would miss nu = 3, 7, ...)
DX, XMAX = 0.025, 5.0                # cell-centred grid: the 1.5 um and 6 um walls fall between points
XC = (np.arange(int(round(2 * XMAX / DX))) - (int(round(2 * XMAX / DX)) - 1) / 2) * DX     # exactly symmetric about 0


def We_of(W=W, lam=LAM0, sigma=1):
    return W + (lam / np.pi) * (NC / NR) ** (2 * sigma) / np.sqrt(NR ** 2 - NC ** 2)


def Lpi_of(W=W, lam=LAM0, sigma=1):
    return 4 * NR * We_of(W, lam, sigma) ** 2 / (3 * lam)


def modes1d(nprof, lam):
    """Guided TM modes of the lateral index profile nprof (on XC): n_eff (descending) and H_y, each normalised to
    sum(H^2 / n^2) dx = 1 (unit power up to a constant) and positive at its largest value."""
    k0 = 2 * np.pi / lam
    e = nprof ** 2; N = len(XC)
    eh = 2 / (e[:-1] + e[1:])                                   # 1/n^2 at the half points
    main = np.zeros(N); main[:-1] -= eh; main[1:] -= eh
    main[0] -= 2 / e[0]; main[-1] -= 2 / e[-1]
    D = (np.diag(main) + np.diag(eh, 1) + np.diag(eh, -1)) / DX ** 2
    s = np.sqrt(e)
    w, V = np.linalg.eigh(s[:, None] * D * s[None, :] + np.diag(k0 ** 2 * e))
    H = V / s[:, None]
    ne = np.sqrt(np.maximum(w, 0)) / k0
    o = np.argsort(-ne); ne, H = ne[o], H[:, o]
    g = ne > NC + 1e-6
    ne, H = ne[g], H[:, g]
    for k in range(H.shape[1]):
        H[:, k] /= np.sqrt(np.sum(H[:, k] ** 2 / e) * DX)
        if H[np.argmax(np.abs(H[:, k])), k] < 0: H[:, k] *= -1
    return ne, H


def strip(width, x0=0.0):
    return np.where(np.abs(XC - x0) < width / 2, NR, NC)


class MMI:
    """Modes of the multimode section and of the access guides at one wavelength."""
    def __init__(self, W=W, lam=LAM0):
        self.W, self.lam = W, lam
        self.n = strip(W); self.ne, self.H = modes1d(self.n, lam)
        self.b = 2 * np.pi * self.ne / lam
        self._acc = {}

    def access(self, x0):
        """Fundamental mode of the 1.5 um access guide, solved once (centred) and shifted to x0."""
        if not self._acc:
            n = strip(WA); ne, H = modes1d(n, self.lam)
            self._acc["c"] = (ne[0], H[:, 0])
        ne, h = self._acc["c"]
        return strip(WA, x0), ne, np.interp(XC - x0, XC, h, left=0, right=0)

    def coef(self, x0):
        """Amplitudes of the MMI modes excited by (or coupling to) an access guide centred at x0: overlaps in the
        MMI's own 1/n^2 weighting, with the access mode normalised in the same weighting (as in Lab 3)."""
        n, nea, h = self.access(x0)
        e = self.n ** 2
        h = h / np.sqrt(np.sum(h ** 2 / e) * DX)
        return (self.H.T @ (h / e)) * DX

    def field(self, x0, z):
        """H_y across the MMI at the lengths z (array) for input at x0: shape (len(XC), len(z))."""
        c = self.coef(x0)
        ph = np.exp(-1j * np.outer(self.b - self.b[0], np.atleast_1d(z)))
        return self.H @ (c[:, None] * ph)

    def ports(self, x0, outs, L):
        """Power transmitted into access guides at positions outs for input at x0 and MMI length L."""
        c = self.coef(x0); ph = np.exp(-1j * (self.b - self.b[0]) * L)
        return np.array([abs(np.sum(c * self.coef(xo) * ph)) ** 2 for xo in outs])


# ---------------------------------------------------------------------------------------------- 10.1 Y-branch
def fig_ybranch():
    F10 = json.load(open(os.path.join(HERE, "ch09_fields.json")))
    xl = np.array(F10["xl"])
    from ch09_figs import to_D                      # D_x = n^2 E_x: continuous across the side walls
    s05 = to_D(xl, F10["strips"][0]["modes"][0], [(-0.25, 0.25)])
    st0, st1 = (to_D(xl, m, [(-0.6, 0.6)]) for m in F10["strips"][1]["modes"][:2])
    print("Y-branch profiles (femwell, TE): 0.5 um strip n_eff", [round(x, 4) for x in F10["strips"][0]["n"]],
          "; 1.2 um stem n_eff", [round(x, 4) for x in F10["strips"][1]["n"]])
    sep = 2.0                                                        # arm centre spacing at the far end (um)
    shift = lambda f, d: np.interp(xl - d, xl, f, left=0, right=0)
    upper, lower = shift(s05, sep / 2), shift(s05, -sep / 2)
    even, odd = (upper + lower) / np.sqrt(2), (upper - lower) / np.sqrt(2)     # odd taken positive in the upper arm
    if st1[np.argmin(abs(xl - 0.3))] < 0: st1 = -st1                            # stem TE1 positive on the upper side
    # geometry (um, illustrative): 0.5 um input, linear taper to a 1.2 um stem over 8 um, two 0.5 um arms leaving
    # with a 0.2 um gap at the tip and separating by raised-cosine S-bends to a 2 um centre spacing over 10 um
    zin, zt, zs, zend = 3.0, 11.0, 21.0, 30.0
    VS = 2.0                                                          # transverse (vertical) scale factor
    fig = plt.figure(figsize=(6.3, 3.75))
    for k, mode in enumerate(("split", "comb")):
        ax = fig.add_axes([0.0, 0.515 - 0.5 * k, 1.0, 0.475]); frameless(ax, (-1.2, 36.5), (-2.45 * VS, 2.75 * VS), equal=True)
        box(ax, -1.2, -1.7 * VS, zend + 1.2, 3.4 * VS, "ox", z=0)
        wg_straight(ax, -1.2, zin, 0, 0.5 * VS)
        wg_taper(ax, zin, zt, 0, 0.5 * VS, 1.2 * VS)
        for sg in (1, -1):
            xs, ys = sbend_xy(zt, sg * 0.35, zs - zt, sg * (sep / 2 - 0.35))
            ribbon(ax, xs, ys * VS, 0.5 * VS, "si")
            wg_straight(ax, zs, zend, sg * sep / 2 * VS, 0.5 * VS)

        def prof(zc, f, col, amp, ls="-"):
            """a mode profile drawn across the guide at z = zc, its amplitude along z (peak = amp um)"""
            m = np.abs(xl) < 2.3
            ax.plot(zc + amp * f[m], xl[m] * VS, color=col, lw=1.2, ls=ls, zorder=6)
            ax.plot([zc, zc], [-2.3 * VS, 2.3 * VS], color=MUTED, lw=0.5, ls=":", zorder=5)
        A = 1.6 / np.abs(s05).max()       # all profiles on one scale (unit power each): the input mode peaks at 1.6 um
        zst = 10.4                                                    # station in the stem (1.15 um wide there)
        top = 2.35 * VS
        if mode == "split":
            prof(1.0, s05, C1, A)
            prof(zst, st0, C1, A)
            prof(27.0, even, C1, A)
            arrow(ax, (-1.1, 0.75 * VS), (1.6, 0.75 * VS), col=RED, lw=1.0, ms=7)
            label(ax, zend + 0.3, sep / 2 * VS, "50 %", ha="left", fs=7)
            label(ax, zend + 0.3, -sep / 2 * VS, "50 %", ha="left", fs=7)
            label(ax, 1.0, top, "input mode", fs=6.5, va="bottom")
            label(ax, zst, top, "stem TE0", fs=6.5, va="bottom")
            label(ax, 27.0, top, "even supermode", fs=6.5, va="bottom")
            ax.text(36.4, -2.45 * VS, f"transverse scale × {VS:.0f}", ha="right", va="bottom", fontsize=6.0, color=MUTED, style="italic")
            panel(ax, "a", x=0.0, y=1.0)
        else:
            prof(28.4, upper, INK, A)
            prof(24.0, even / np.sqrt(2), C1, A)
            prof(24.0, odd / np.sqrt(2), C4, A, ls=(0, (3, 1.5)))
            prof(zst, st0 / np.sqrt(2), C1, A)
            prof(zst, st1 / np.sqrt(2), C4, A, ls=(0, (3, 1.5)))
            prof(1.0, s05 / np.sqrt(2), C1, A)
            arrow(ax, (zend + 0.3, (sep / 2 + 0.55) * VS), (zend - 2.6, (sep / 2 + 0.55) * VS), col=RED, lw=1.0, ms=7)
            label(ax, zend + 0.3, sep / 2 * VS, "in", ha="left", fs=7)
            label(ax, 28.4, top, "one arm", fs=6.5, va="bottom")
            label(ax, 24.0, top, "= even + odd", fs=6.5, va="bottom")
            label(ax, zst, top, "stem TE0 + TE1", fs=6.5, va="bottom")
            label(ax, 1.0, top, "50 % out", fs=6.5, va="bottom")
            for dz in (0.0, 1.3, 2.6):                                # the odd part radiates where the stem narrows
                for sg in (1, -1):
                    arrow(ax, (zin + 2.2 + dz, sg * 0.5 * VS), (zin + 1.2 + dz, sg * 1.6 * VS), col=C4, lw=0.8, ms=5, ls=(0, (2, 1.5)))
            label(ax, zin + 5.6, -2.05 * VS, "odd part radiates", fs=6.5, col=C4, ha="left")
            panel(ax, "b", x=0.0, y=1.0)
            scalebar(ax, 31.2, -2.4 * VS, 5.0, "5 µm")
    save(fig, "ch10_ybranch")


# ---------------------------------------------------------------------------------------------- 10.2 abrupt junction
def fig_junction():
    m = MMI()
    We = We_of(); xs = We / 6
    c0, cp = m.coef(0.0), m.coef(xs)
    p0, pp = c0 ** 2, cp ** 2
    print(f"MMI 6 um at 1550 nm: {len(m.ne)} guided TM modes; L_pi exact = {np.pi/(m.b[0]-m.b[1]):.2f} um (formula {Lpi_of():.2f});"
          f" W_e = {We:.3f} um, W_e/6 = {xs:.3f} um")
    print(f"guided power: centred input {p0.sum():.4f}, input at W_e/6 {pp.sum():.4f}")
    print("power fractions (%), centred:", np.round(100 * p0, 2))
    print("power fractions (%), at W_e/6:", np.round(100 * pp, 2))
    fig = plt.figure(figsize=(6.3, 3.1))
    a = fig.add_axes([0.06, 0.15, 0.33, 0.78])
    n_show = 5
    off = 0
    rows = [(m.access(0.0)[2], "input, centred", C1), (m.access(xs)[2], "input at $W_e$/6", C2)] + \
           [(m.H[:, v], f"$\\phi_{v}$", INK) for v in range(n_show)]
    for i, (f, lab, col) in enumerate(rows):
        y0 = -1.25 * i
        f = f / np.abs(f).max() * 0.55
        a.plot(XC, y0 + f, color=col, lw=1.2)
        a.axhline(y0, color=GRID, lw=0.6, zorder=0)
        a.text(-4.3, y0 + 0.08, lab, fontsize=6.8, color=col, va="bottom", ha="left")
    a.axvspan(-W / 2, W / 2, color=MAT["si"], alpha=0.25, lw=0, zorder=0)
    a.set_xlim(-4.4, 4.4); a.set_ylim(-1.25 * (len(rows) - 1) - 0.8, 0.9)
    a.set_yticks([]); a.spines["left"].set_visible(False); a.grid(False)
    a.set_xticks([-3, 0, 3])
    a.set_xlabel("Position across the MMI (µm)")
    tag(a, "a")
    b = fig.add_axes([0.48, 0.15, 0.51, 0.78])
    nu = np.arange(len(p0))
    b.bar(nu - 0.2, 100 * p0, width=0.4, color=C1, label="centred input")
    b.bar(nu + 0.2, 100 * pp, width=0.4, color=C2, label="input at $W_e$/6")
    for v in (2, 5, 8, 11):
        b.text(v + 0.2, 100 * pp[v] + 0.6, "0", ha="center", va="bottom", fontsize=6.3, color=C2)
    b.set_xlim(-0.7, 12.7); b.set_xticks(range(0, 13))
    finish(b, "Mode number ν of the 6 µm section", "Power coupled into the mode (%)")
    b.legend(loc="upper right")
    tag(b, "b")
    save(fig, "ch10_junction")
    return m


# ---------------------------------------------------------------------------------------------- 10.3 self-imaging maps
def ideal_field(x0, z, m):
    """Field in the MMI with the ideal modes of Section 10.3: sines across the effective width W_e, with the quadratic
    spacing beta_0 - beta_nu = nu (nu + 2) pi / (3 L_pi) (L_pi from the formula), as many as the section guides.
    The input is the 1.5 um access guide's mode, projected onto them."""
    Lp, We = Lpi_of(), We_of()
    nmodes = len(m.ne)
    inside = np.abs(XC) < We / 2
    nu = np.arange(nmodes)
    phi = np.sqrt(2 / We) * np.sin(np.outer(XC + We / 2, (nu + 1) * np.pi / We)) * inside[:, None]
    h = m.access(x0)[2]; h = h / np.sqrt(np.sum(h ** 2) * DX)
    c = (phi.T @ h) * DX
    ph = np.exp(-1j * np.outer(nu * (nu + 2) * np.pi / (3 * Lp), np.atleast_1d(z)))
    return phi @ (c[:, None] * ph), c


def fig_selfimaging(m):
    Lp = Lpi_of(); We = We_of()
    z = np.linspace(0, 3 * Lp * 1.04, 900)
    XMAP = 0.85        # an input that excites every low-order mode and keeps the N-fold images apart
    _, c = ideal_field(XMAP, [0.0], m)
    print(f"ideal-mode map: {len(c)} modes, input power captured {np.sum(c**2):.4f} (general), "
          f"{np.sum(ideal_field(0.0, [0.0], m)[1]**2):.4f} (centred)")
    cases = [("general", XMAP, [(3 / 4, "3$L_\\pi$/4", "4"), (1.5, "3$L_\\pi$/2", "2"), (3.0, "3$L_\\pi$", "1")]),
             ("paired", We / 6, [(0.5, "$L_\\pi$/2", "2"), (1.0, "$L_\\pi$", "1"), (1.5, "3$L_\\pi$/2", "2"), (2.0, "2$L_\\pi$", "1"), (3.0, "3$L_\\pi$", "1")]),
             ("symmetric", 0.0, [(3 / 8, "3$L_\\pi$/8", "2"), (3 / 4, "3$L_\\pi$/4", "1"), (9 / 8, "9$L_\\pi$/8", "2"), (3 / 2, "3$L_\\pi$/2", "1")])]
    titles = {"general": f"general: input {XMAP:.2f} µm off centre", "paired": f"paired: input at $W_e$/6 = {We/6:.2f} µm",
              "symmetric": "symmetric: centred input"}
    fig, axs = plt.subplots(3, 1, figsize=(6.3, 4.6), sharex=True)
    xm = np.abs(XC) < 3.6
    for ax, (name, x0, marks) in zip(axs, cases):
        I = np.abs(ideal_field(x0, z, m)[0]) ** 2
        I = I[xm]; I /= I.max()
        ax.imshow(I ** 0.7, origin="lower", aspect="auto", cmap=FIELD_CMAP, extent=(z[0], z[-1], XC[xm][0], XC[xm][-1]), interpolation="bilinear")
        ax.axhline(W / 2, color=MUTED, lw=0.5); ax.axhline(-W / 2, color=MUTED, lw=0.5)
        ax.grid(False)
        ax.set_yticks([-3, 0, 3]); ax.set_ylim(-3.6, 3.6)
        for f, lab, what in marks:
            ax.axvline(f * Lp, color=AMBER, lw=0.8, ls=(0, (3, 2)))
            ax.text(f * Lp, 3.75, f"{lab} ({what})", ha="center", va="bottom", fontsize=6.5, color=INK)
        ax.plot([0], [x0], marker=">", color=RED, ms=5, clip_on=False, zorder=5)
        ax.text(z[-1] * 0.995, -3.3, titles[name], ha="right", va="bottom", fontsize=6.8, color=INK,
                bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.85))
        ax.set_ylabel("x (µm)")
    axs[-1].set_xlabel("Distance along the MMI, z (µm)")
    axs[-1].set_xlim(0, z[-1])
    for ax, t in zip(axs, "abc"):
        tag(ax, t)
    fig.tight_layout(h_pad=1.6)
    save(fig, "ch10_selfimaging")
    print(f"self-imaging marks with L_pi = {Lp:.1f} um: 3Lpi/8 {3*Lp/8:.1f}, Lpi/2 {Lp/2:.1f}, 3Lpi/2 {1.5*Lp:.1f}, 3Lpi {3*Lp:.1f} um")


# ---------------------------------------------------------------------------------------------- 10.4 geometries to scale
def mmi_device(ax, y0, L, ins, outs, Lt=10.0, Lw=4.0, wa=WA, w=0.5, Ls=12.0, pitch=None):
    """Top view of an MMI with tapered access guides; ins/outs are port offsets (um) from the centre line."""
    box(ax, 0, y0 - W / 2, L, W, "si", z=2)
    for side, ports in ((-1, ins), (1, outs)):
        for p in ports:
            xa = 0 if side < 0 else L
            wg_taper(ax, xa, xa + side * Lt, y0 + p, wa, w)
            xb = xa + side * Lt
            if pitch and len(ports) > 1:
                tgt = np.sign(p) * pitch / 2
                xs, ys = sbend_xy(0, 0, Ls, tgt - p)
                ribbon(ax, xb + side * xs, y0 + p + ys, w, "si")
                wg_straight(ax, xb + side * Ls, xb + side * (Ls + Lw), y0 + tgt, w)
            else:
                wg_straight(ax, xb, xb + side * (Ls + Lw), y0 + p, w)


def fig_mmi_geom():
    Lp = Lpi_of(); We = We_of()
    L12, Lpair, Lgen = 3 * Lp / 8, Lp / 2, 3 * Lp / 2
    print(f"MMI lengths: 1x2 {L12:.1f}, 2x2 paired {Lpair:.1f}, 2x2 general {Lgen:.1f} um; ports +-We/4 = {We/4:.2f}, +-We/6 = {We/6:.2f}")
    fig, ax = geom_axes(figsize=(6.3, 2.75), xlim=(-30, 168), ylim=(-28.5, 9.5))
    rows = [("1 × 2, symmetric", 4.5, L12, [0.0], [We / 4, -We / 4]),
            ("2 × 2, paired", -7.5, Lpair, [We / 6, -We / 6], [We / 6, -We / 6]),
            ("2 × 2, general", -19.5, Lgen, [XG, -XG], [XG, -XG])]
    box(ax, -30, -28.5, 198, 38, "ox", z=0)
    for name, y0, L, ins, outs in rows:
        mmi_device(ax, y0, L, ins, outs, pitch=4.0)
        dim(ax, (0, y0 + W / 2 + 1.0), (L, y0 + W / 2 + 1.0), f"{L:.1f} µm", fs=6.5)
        label(ax, -29, y0 + W / 2 + 1.6, name, ha="left", fs=6.8, bold=True)
    # width and port positions on the 1x2
    y0 = rows[0][1]; L = rows[0][2]
    dim(ax, (L + 33.5, y0 - W / 2), (L + 33.5, y0 + W / 2), "", fs=6.3)
    label(ax, L + 35, y0, f"W = {W:.0f} µm", ha="left", fs=6.5)
    label(ax, L + 2, y0 + We / 4 + 1.3, f"±{We/4:.2f} µm", ha="left", fs=6.0, col=MUTED)
    label(ax, rows[1][2] + 2, rows[1][1] + We / 6 + 1.6, f"±{We/6:.2f} µm", ha="left", fs=6.0, col=MUTED)
    label(ax, rows[2][2] + 2, rows[2][1] + XG + 1.6, f"±{XG:.1f} µm", ha="left", fs=6.0, col=MUTED)
    scalebar(ax, 130, -27.5, 20, "20 µm")
    note(ax, "to scale; access tapers 1.5 → 0.5 µm over 10 µm", loc="upper right")
    save(fig, "ch10_mmi_geom")


# ---------------------------------------------------------------------------------------------- 10.5 bandwidth and tolerance
def best_length(m, x0, outs, L0, span=0.08):
    """Length near L0 with the largest total output power (fine grid search)."""
    Ls = np.linspace(L0 * (1 - span), L0 * (1 + span), 801)
    T = np.array([m.ports(x0, outs, L).sum() for L in Ls])
    return Ls[np.argmax(T)]


def fig_mmi_perf():
    Lp = Lpi_of(); We = We_of()
    m = MMI()
    designs = [("1 × 2", 3 * Lp / 8, 0.0, [We / 4, -We / 4], C1),
               ("2 × 2 paired", Lp / 2, We / 6, [We / 6, -We / 6], C3),
               ("2 × 2 general", 3 * Lp / 2, XG, [XG, -XG], C5)]
    best = []
    for name, L0, x0, outs, col in designs:
        Lb = best_length(m, x0, outs, L0)
        P0, Pb = m.ports(x0, outs, L0), m.ports(x0, outs, Lb)
        best.append(Lb)
        print(f"{name}: formula length {L0:.2f} um (excess loss {-10*np.log10(P0.sum()):.2f} dB); best {Lb:.2f} um "
              f"({100*(Lb/L0-1):+.1f} %), excess loss {-10*np.log10(Pb.sum()):.2f} dB, split {100*Pb[0]:.1f} / {100*Pb[-1]:.1f} %")
    lams = np.linspace(1.50, 1.60, 21)
    res = {d[0]: [] for d in designs}
    for lam in lams:
        ml = MMI(lam=lam)
        for (name, L0, x0, outs, col), Lb in zip(designs, best):
            res[name].append(ml.ports(x0, outs, Lb))
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    inband = np.abs(lams - 1.55) <= 0.0201
    for (name, L0, x0, outs, col), Lb in zip(designs, best):
        P = np.array(res[name]); tot = P.sum(axis=1)
        a.plot(1000 * lams, -10 * np.log10(tot), color=col, label=f"{name}, {Lb:.1f} µm")
        msg = (f"{name} at {Lb:.2f} um: excess loss {-10*np.log10(tot[10]):.2f} dB at 1550 nm; at 1500/1530/1570/1600 nm "
               + " / ".join(f"{-10*np.log10(tot[i]):.2f}" for i in (0, 6, 14, 20)) + " dB")
        if name != "1 × 2":
            imb = 10 * np.log10(P[:, 0] / P[:, 1])
            msg += f"; imbalance 1530-1570 nm {imb[inband].min():+.2f} to {imb[inband].max():+.2f} dB, 1500-1600 nm {imb.min():+.2f} to {imb.max():+.2f} dB"
        print(msg)
    a.set_xlim(1500, 1600); a.set_ylim(0, 2.6)
    finish(a, "Wavelength (nm)", "Excess loss (dB)")
    a.legend(loc="upper center", fontsize=6.8, title="length chosen at 1550 nm", title_fontsize=6.8)
    tag(a, "a")
    # b: the 1 x 2 against its length
    Ls = np.linspace(29, 38.5, 191)
    el = np.array([-10 * np.log10(m.ports(0.0, [We / 4, -We / 4], L).sum()) for L in Ls])
    b.plot(Ls, el, color=C1)
    L12, L12s0 = 3 * Lp / 8, 3 * Lpi_of(sigma=0) / 8
    pts = [(best[0], f"best: {best[0]:.1f} µm", C1, (-0.5, 0.55), "right"),
           (L12, f"3$L_\\pi$/8 = {L12:.1f} µm", C1, (1.0, -0.02), "left"),
           (L12s0, f"σ = 0 by mistake: {L12s0:.2f} µm", C2, (-0.4, 0.9), "right")]
    for Lm, txt, col, (dx, dy), ha in pts:
        e = -10 * np.log10(m.ports(0.0, [We / 4, -We / 4], Lm).sum())
        b.plot(Lm, e, "o", color=col, ms=4, zorder=5)
        b.annotate(txt, xy=(Lm, e), xytext=(Lm + dx, e + dy), fontsize=6.6, color=INK, ha=ha, va="center",
                   arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkA=1, shrinkB=2))
        print(f"1x2 excess loss at L = {Lm:.2f} um: {e:.2f} dB")
    j = np.argmin(el)
    print(f"1x2 within 0.1 dB of its best over {Ls[el < el[j] + 0.1].min():.2f}-{Ls[el < el[j] + 0.1].max():.2f} um")
    for dw in (-0.06, 0.06):                                          # +-1 % width at the 1550 nm best length
        mw = MMI(W=W + dw)
        print(f"1x2 at W = {W+dw:.2f} um, L = {best[0]:.2f}: excess loss {-10*np.log10(mw.ports(0.0, [We_of(W+dw)/4, -We_of(W+dw)/4], best[0]).sum()):.2f} dB")
    b.set_xlim(29, 38.5); b.set_ylim(0, 2.6)
    finish(b, "Length of the 1 × 2 MMI (µm)", "Excess loss at 1550 nm (dB)")
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch10_mmi_perf")


if __name__ == "__main__":
    which = sys.argv[1:] or ["ybranch", "junction", "selfimaging", "geom", "perf"]
    m = None
    if "ybranch" in which and os.path.exists(os.path.join(HERE, "ch09_fields.json")): fig_ybranch()
    if "junction" in which or "selfimaging" in which: m = fig_junction()
    if "selfimaging" in which: fig_selfimaging(m)
    if "geom" in which: fig_mmi_geom()
    if "perf" in which: fig_mmi_perf()
