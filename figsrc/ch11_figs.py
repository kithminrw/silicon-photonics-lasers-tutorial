"""Figures for Chapter 11 (Mach-Zehnder interferometers). Pure NumPy/Matplotlib.
Run from the worktree root: python -I -X utf8 figsrc/ch11_figs.py   (set FIGPREVIEW for PNG previews)

Model: couplers C = [[t, -j k], [-j k, t]] (the chapter's convention), arms diag(a e^{-j phi}), input at the upper port.
500 x 220 nm Si strip at 1550 nm: n_eff 2.446, n_g 4.18 (Chapter 6, femwell). Reference-link channels on the
400 GHz grid: 1546.12, 1549.32, 1552.52, 1555.75 nm (Chapter 1).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

NEFF, NG, LAM0 = 2.446, 4.18, 1.55
C0 = 299792.458                     # speed of light in nm * THz  (lambda[nm] = C0 / nu[THz])
CH_NU = np.array([193.9, 193.5, 193.1, 192.7])
CH_LAM = C0 / CH_NU


def coupler(k2):
    t, k = np.sqrt(1 - k2), np.sqrt(k2)
    return np.array([[t, -1j * k], [-1j * k, t]])


def mzi(dphi, k1=0.5, k2=0.5):
    """bar and cross power of an MZI with input at the upper port; dphi = phi_2 - phi_1 (lower minus upper)."""
    dphi = np.atleast_1d(dphi)
    out = np.empty((2, dphi.size))
    for i, d in enumerate(dphi):
        v = coupler(k2) @ np.diag([1, np.exp(-1j * d)]) @ coupler(k1) @ np.array([1, 0])
        out[:, i] = np.abs(v) ** 2
    return out


def er_cross(k1, k2):
    t1, c1, t2, c2 = np.sqrt(1 - k1), np.sqrt(k1), np.sqrt(1 - k2), np.sqrt(k2)
    return ((t1 * c2 + c1 * t2) / (t1 * c2 - c1 * t2)) ** 2


# ---------------------------------------------------------------------------------------------- 11.1 the matrix chain
def fig_chain():
    fig, ax = geom_axes(figsize=(6.3, 2.35), xlim=(0, 100), ylim=(-12, 25), equal=False)
    yU, yL, yc, w = 15.0, 5.0, 10.0, 0.9            # arm centre lines, coupler centre, drawn guide width (schematic)

    def dc(x0, L=16):
        """schematic directional coupler between x0 and x0 + L; returns nothing."""
        for s, y in ((1, yU), (-1, yL)):
            xs, ys = sbend_xy(x0, y, 5, -s * (abs(y - yc) - 0.9)); ribbon(ax, xs, ys, w, "si")
            wg_straight(ax, x0 + 5, x0 + L - 5, yc + s * 0.9, w)
            xs, ys = sbend_xy(x0 + L - 5, yc + s * 0.9, 5, s * (abs(y - yc) - 0.9)); ribbon(ax, xs, ys, w, "si")
    box(ax, 0, -1, 100, 22, "ox", z=0)
    wg_straight(ax, 3, 12, yU, w); wg_straight(ax, 3, 12, yL, w)
    dc(12); dc(70)
    wg_straight(ax, 28, 70, yU, w); wg_straight(ax, 28, 70, yL, w)
    wg_straight(ax, 86, 96, yU, w); wg_straight(ax, 86, 96, yL, w)
    box(ax, 40, yL - 1.6, 18, 3.2, "tin", z=3, alpha=0.85)                    # heater over the lower arm
    label(ax, 49, yL - 3.3, "phase shifter (heater)", fs=6.3, va="top")
    label(ax, 49, yU + 2.2, r"$a_1e^{-j\phi_1}$", fs=7.5, va="bottom")
    label(ax, 35, yL + 2.0, r"$a_2e^{-j\phi_2}$", fs=7.5, va="bottom")
    # ports
    label(ax, 2.5, yU, "in 1", ha="right", fs=6.8); label(ax, 2.5, yL, "in 2", ha="right", fs=6.8)
    label(ax, 96.6, yU, "bar", ha="left", fs=6.8, col=AMBER, bold=True); label(ax, 96.6, yL, "cross", ha="left", fs=6.8, col=BLUE, bold=True)
    arrow(ax, (3.2, yU + 2.3), (9.5, yU + 2.3), col=RED, lw=1.0)
    label(ax, 20, yU + 2.2, r"$C_1$: $\kappa_1^2$", fs=7.5, va="bottom"); label(ax, 78, yU + 2.2, r"$C_2$: $\kappa_2^2$", fs=7.5, va="bottom")
    # each element's matrix under it; light travels left to right, so the matrices multiply right to left
    ym = -5.4
    for x0, x1 in ((12, 28), (28, 70), (70, 86)):
        ax.plot([x0 + 0.6, x0 + 0.6, x1 - 0.6, x1 - 0.6], [-2.0, -2.8, -2.8, -2.0], color=MUTED, lw=0.7)
    label(ax, 20, ym, r"$C_1$", fs=8.5); label(ax, 49, ym, r"$\mathrm{diag}(a_1e^{-j\phi_1},\ a_2e^{-j\phi_2})$", fs=8)
    label(ax, 78, ym, r"$C_2$", fs=8.5)
    label(ax, 50, -10.2, r"$\left(\genfrac{}{}{0}{}{b_\mathrm{bar}}{b_\mathrm{cross}}\right) = C_2\ \mathrm{diag}(a_1e^{-j\phi_1},\ a_2e^{-j\phi_2})\ C_1"
                         r"\left(\genfrac{}{}{0}{}{1}{0}\right)$", fs=8)
    note(ax, "not to scale", loc="upper right")
    save(fig, "ch11_chain")


# ---------------------------------------------------------------------------------------------- 11.2 bar/cross and extinction
def fig_phase():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    d = np.linspace(0, 4 * np.pi, 801)
    bar, crs = mzi(d)
    a.plot(d / np.pi, crs, color=C1, label="cross")
    a.plot(d / np.pi, bar, color=C2, label="bar")
    a.set_xlim(0, 4); a.set_ylim(-0.02, 1.15); a.set_xticks([0, 1, 2, 3, 4]); a.set_xticklabels(["0", "π", "2π", "3π", "4π"])
    finish(a, "Phase difference Δφ", "Output power (of input)")
    a.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.04))
    tag(a, "a")
    d = np.linspace(0, 2 * np.pi, 2001)
    for k2, col, ls in ((0.50, C1, "-"), (0.55, C2, "-"), (0.60, C4, "-")):
        _, crs = mzi(d, 0.5, k2)
        er = 10 * np.log10(er_cross(0.5, k2)) if k2 != 0.5 else np.inf
        lab = "50/50: perfect null" if k2 == 0.5 else f"{100*k2:.0f}/{100*(1-k2):.0f}: ER {er:.0f} dB"
        b.plot(d / np.pi, 10 * np.log10(np.maximum(crs, 1e-6)), color=col, ls=ls, label=lab)
        if k2 != 0.5:
            print(f"cross-port ER, first 50/50, second {100*k2:.0f}/{100*(1-k2):.0f}: formula {er:.2f} dB, "
                  f"from the curve {10*np.log10(crs.max()/crs.min()):.2f} dB")
    b.set_xlim(0, 2); b.set_ylim(-45, 3); b.set_xticks([0, 0.5, 1, 1.5, 2]); b.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
    finish(b, "Phase difference Δφ", "Cross-port power (dB)")
    b.legend(loc="lower left", fontsize=6.8, title="second coupler", title_fontsize=6.8)
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch11_phase")


# ---------------------------------------------------------------------------------------------- 11.5 lattice filter
def lattice(Phi, th, ph, m=(1, 2)):
    """Two-stage MZI lattice: couplers with power coupling sin^2(th_i), upper arm of stage s longer by m_s unit delays
    (phase m_s * Phi) plus a trim phase ph_s. Returns (P_upper, P_lower) for input at the upper port."""
    Phi = np.atleast_1d(Phi)
    out = np.empty((2, Phi.size))
    C = [coupler(np.sin(t) ** 2) for t in th]
    for i, P in enumerate(Phi):
        v = C[0] @ np.array([1, 0])
        for s in range(2):
            v = C[s + 1] @ (np.array([np.exp(-1j * (m[s] * P + ph[s])), 1]) * v)
        out[:, i] = np.abs(v) ** 2
    return out


# The maximally flat two-stage half-band design (a flat-top interleaver): couplers with theta = 45, 60 and 75 degrees,
# i.e. 50 %, 75 % and 93.3 % of the power coupled across, no trim phase; checked numerically below (P = 1 at Phi = 0,
# P = 0 at Phi = pi, and the flatness of both).
LATTICE_TH = (np.pi / 4, np.pi / 3, 5 * np.pi / 12)
LATTICE_PH = (0.0, 0.0)


def fig_lattice():
    th, ph = LATTICE_TH, LATTICE_PH
    k2 = np.sin(th) ** 2
    e = 1e-2
    p0, pe, pp, ppe = (lattice([x], th, ph)[0][0] for x in (0, e, np.pi, np.pi + e))
    print("lattice couplers (power to the other guide):", np.round(k2, 4), f" P(0) = {p0:.6f}, 1 - P(0.01) = {1-pe:.2e} (single MZI {np.sin(e/2)**2:.2e});"
          f" P(pi) = {pp:.1e}, P(pi + 0.01) = {ppe:.2e} (single MZI {np.sin(e/2)**2:.2e})")
    fsr_nu = CH_NU[0] - CH_NU[2]                      # 0.8 THz: period that passes channels 1 and 3
    dL = C0 * 1e-3 / (NG * fsr_nu)                    # um  (c / (n_g FSR); C0 in nm*THz -> um*THz is C0*1e-3)
    print(f"unit delay dL = c/(n_g x {1000*fsr_nu:.0f} GHz) = {dL:.2f} um;  FSR at 1550 nm = {1e3*LAM0**2/(NG*dL):.2f} nm")
    fig = plt.figure(figsize=(6.3, 4.3))
    ax = fig.add_axes([0.0, 0.66, 1.0, 0.34]); frameless(ax, (-5, 106), (0, 21), equal=False)
    yU, yL, yc, w = 15.0, 5.0, 10.0, 0.9
    def dc(x0, L=12):
        for s, y in ((1, yU), (-1, yL)):
            xs, ys = sbend_xy(x0, y, 4, -s * (abs(y - yc) - 0.9)); ribbon(ax, xs, ys, w, "si")
            wg_straight(ax, x0 + 4, x0 + L - 4, yc + s * 0.9, w)
            xs, ys = sbend_xy(x0 + L - 4, yc + s * 0.9, 4, s * (abs(y - yc) - 0.9)); ribbon(ax, xs, ys, w, "si")
    box(ax, 0, 0.6, 100, 18.8, "ox", z=0)
    xs_c = (6, 40, 80)
    for i, x0 in enumerate(xs_c):
        dc(x0); label(ax, x0 + 6, 2.1,f"$\\kappa_{i+1}^2$ = {100*k2[i]:.0f} %", fs=6.8)
    wg_straight(ax, 1, 6, yU, w); wg_straight(ax, 1, 6, yL, w); wg_straight(ax, 92, 99, yU, w); wg_straight(ax, 92, 99, yL, w)
    # stage 1: upper arm longer by dL, stage 2: by 2 dL (drawn as loops)
    for (xa, xb, m) in ((18, 40, 1), (52, 80, 2)):
        wg_straight(ax, xa, xb, yL, w)
        xm, hw, hh = (xa + xb) / 2, 4.5, 1.8 * m + 0.6
        pts = [(xa, yU), (xm - hw, yU), (xm - hw, yU + hh), (xm + hw, yU + hh), (xm + hw, yU), (xb, yU)]
        P = np.array(pts, float)
        for p0, p1 in zip(P[:-1], P[1:]):
            ribbon(ax, np.linspace(p0[0], p1[0], 2), np.linspace(p0[1], p1[1], 2), w, "si")
        box(ax, xa + 1.2, yL - 1.1, 5.5, 2.2, "tin", z=3, alpha=0.85)
        label(ax, xm, yU + hh + 1.0, "Δ$L$" if m == 1 else "2Δ$L$", fs=7.5, va="bottom")
    label(ax, 23.5, yL - 2.1, "trim heaters", fs=6.3, va="top", ha="left")
    label(ax, 0.4, yU, "in", ha="right", fs=6.8)
    label(ax, 99.6, yU, "odd", ha="left", fs=6.8, col=BLUE, bold=True); label(ax, 99.6, yL, "even", ha="left", fs=6.8, col=AMBER, bold=True)
    note(ax, "not to scale", loc="upper right")
    panel(ax, "a", x=0.0, y=1.0)
    # response
    b = fig.add_axes([0.09, 0.09, 0.89, 0.47])
    lam = np.linspace(1544.0, 1558.0, 2801)
    nu = C0 / lam
    Phi = 2 * np.pi * (nu - CH_NU[0]) / fsr_nu
    Pl = lattice(Phi, th, ph)
    Ps = mzi(Phi)                                           # single MZI, same delay: odd channels at its cross port
    to_db = lambda p: 10 * np.log10(np.maximum(p, 1e-5))
    b.plot(lam, to_db(Ps[1]), color=C1, lw=1.0, ls=(0, (4, 2)))
    b.plot(lam, to_db(Ps[0]), color=C2, lw=1.0, ls=(0, (4, 2)))
    # which lattice output passes the odd channels
    up_odd = Pl[0][np.argmin(abs(lam - CH_LAM[0]))] > 0.5
    odd, even = (Pl[0], Pl[1]) if up_odd else (Pl[1], Pl[0])
    b.plot(lam, to_db(odd), color=C1)
    b.plot(lam, to_db(even), color=C2)
    b.plot([], [], color=MUTED, lw=1.0, ls=(0, (4, 2)), label="single MZI (ΔL)")
    b.plot([], [], color=MUTED, label="two-stage lattice")
    b.text(1550.92, -12, "odd\nport", color=C1, fontsize=7, ha="center", fontweight="bold")
    b.text(1547.45, -12, "even\nport", color=C2, fontsize=7, ha="center", fontweight="bold")
    for i, l in enumerate(CH_LAM):
        b.axvline(l, color=MUTED, lw=0.6, ls=":")
        b.text(l, 1.2, f"ch {i+1}", ha="center", va="bottom", fontsize=6.5, color=MUTED)
    b.set_xlim(1544, 1558); b.set_ylim(-42, 1)
    finish(b, "Wavelength (nm)", "Transmission (dB)")
    b.legend(loc="lower center", fontsize=6.8, bbox_to_anchor=(0.25, 0.0), handlelength=2.4)
    tag(b, "b")
    # numbers: pass band of the even port around channel 2, stop band (rejection > 20 dB) around channel 1
    def span(mask, l0):
        j = np.argmin(abs(lam - l0))
        if not mask[j]: return 0.0
        i0 = i1 = j
        while i0 > 0 and mask[i0 - 1]: i0 -= 1
        while i1 < len(mask) - 1 and mask[i1 + 1]: i1 += 1
        return lam[i1] - lam[i0]
    for name, P in (("single MZI", Ps[0]), ("lattice", even)):
        print(f"{name}: -0.5 dB pass band {span(P > 10 ** -0.05, CH_LAM[1]):.2f} nm, -1 dB {span(P > 10 ** -0.1, CH_LAM[1]):.2f} nm; "
              f"rejection > 20 dB over {span(P < 0.01, CH_LAM[0]):.2f} nm around the neighbouring channel; "
              f"at 1 nm from its own channel {10*np.log10(np.interp(CH_LAM[1] + 1.0, lam, P)):.2f} dB")
    save(fig, "ch11_lattice")
    return dL


# ---------------------------------------------------------------------------------------------- 11.6 group index from the FSR
def dphase(lam_nm, dL):
    lam = lam_nm * 1e-3
    neff = NEFF - (NG - NEFF) * (lam - LAM0) / LAM0          # n_eff(lam) linear, slope set by n_g (as in the demo)
    return 2 * np.pi * neff * dL / lam


def spectrum(lam_nm, dL):
    """bar-port power of an ideal unbalanced MZI, with a phase offset (fabrication, or a heater) that puts two
    adjacent maxima symmetrically about 1550 nm."""
    fsr = 1e3 * LAM0 ** 2 / (NG * dL)
    phi0 = np.pi - dphase(1550 - fsr / 2, dL)
    return mzi(dphase(lam_nm, dL) + phi0)[0]


def peaks(lam, P):
    i = np.where((P[1:-1] > P[:-2]) & (P[1:-1] >= P[2:]) & (P[1:-1] > 0.9))[0] + 1
    return lam[i]


def fig_ng():
    fig = plt.figure(figsize=(6.3, 3.3))
    lam = np.linspace(1540, 1560, 40001)
    dls = (50, 100, 300)
    axs = [fig.add_axes([0.08, 0.70 - 0.29 * i, 0.50, 0.23]) for i in range(3)]
    for ax, dL, col in zip(axs, dls, (C1, C3, C5)):
        P = spectrum(lam, dL)
        ax.plot(lam, P, color=col, lw=1.2)
        pk = peaks(lam, P)
        j = np.where(pk < 1550)[0][-1]                       # the two maxima either side of 1550 nm
        l0, l1 = pk[j], pk[j + 1]
        fsr = l1 - l0; lm = (l0 + l1) / 2
        ng = (lm * 1e-3) ** 2 / (fsr * 1e-3 * dL)
        print(f"dL {dL} um: FSR measured between peaks {l0:.2f} and {l1:.2f} nm = {fsr:.3f} nm (formula {1e3*LAM0**2/(NG*dL):.3f} nm);"
              f" n_g = lambda^2/(FSR dL) = {ng:.3f}")
        ax.annotate("", xy=(l1, 1.12), xytext=(l0, 1.12), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
        ax.text(max(l1, l0) + 0.25, 1.12, f"FSR {fsr:.2f} nm" if fsr < 10 else f"FSR {fsr:.1f} nm", fontsize=6.8, va="center", ha="left", color=INK,
                bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))
        ax.text(1540.2, 1.12, f"Δ$L$ = {dL} µm", fontsize=7, va="center", ha="left", color=col, fontweight="bold",
                bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))
        ax.set_xlim(1540, 1560); ax.set_ylim(0, 1.36); ax.set_yticks([0, 1]); ax.set_xticks([1540, 1545, 1550, 1555, 1560])
        if ax is not axs[-1]: ax.set_xticklabels([])
    axs[1].set_ylabel("Bar-port power")
    axs[-1].set_xlabel("Wavelength (nm)")
    tag(axs[0], "a")
    b = fig.add_axes([0.70, 0.12, 0.29, 0.81])
    d = np.linspace(30, 400, 200)
    b.axvspan(50, 300, color=GRID, alpha=0.6, lw=0)
    b.loglog(d, 1e3 * LAM0 ** 2 / (NG * d), color=INK, lw=1.4, label=f"using $n_g$ = {NG}")
    b.loglog(d, 1e3 * LAM0 ** 2 / (NEFF * d), color=MUTED, lw=1.0, ls=(0, (4, 2)), label=f"using $n_\\mathrm{{eff}}$ = {NEFF}")
    for dL, col in zip(dls, (C1, C3, C5)):
        b.plot(dL, 1e3 * LAM0 ** 2 / (NG * dL), "o", color=col, ms=5, zorder=5)
    b.set_xlim(30, 400); b.set_ylim(1, 40)
    b.set_xticks([50, 100, 200, 300]); b.set_xticklabels(["50", "100", "200", "300"])
    b.set_yticks([1, 2, 5, 10, 20]); b.set_yticklabels(["1", "2", "5", "10", "20"]); b.minorticks_off()
    b.text(55, 1.25, "first-chip\nrange", fontsize=6.5, color=MUTED, va="bottom")
    finish(b, "Δ$L$ (µm)", "FSR at 1550 nm (nm)")
    b.legend(loc="upper right", fontsize=6.8)
    tag(b, "b")
    print(f"first-chip range: FSR {1e3*LAM0**2/(NG*50):.1f} nm at 50 um to {1e3*LAM0**2/(NG*300):.2f} nm at 300 um;"
          f" with n_eff instead of n_g the FSR would be {NG/NEFF:.2f} times larger")
    save(fig, "ch11_ng")


# ---------------------------------------------------------------------------------------------- 11.4 switches
def mzi_icon(ax, x0, y0, L=10.0, sep=2.4, heat=False, path=None, col=RED):
    """Small schematic MZI between x0 and x0 + L, arms at y0 +- sep/2; path = 'bar' or 'cross' marks the light that
    enters the upper port and where it leaves."""
    w, cl, bl = 0.32, 1.8, 1.3                                  # guide width, coupler length, bend length
    yu, yd = y0 + sep / 2, y0 - sep / 2
    segs = []
    for x in (x0, x0 + L - 2 * bl - cl):
        for s_, y in ((1, yu), (-1, yd)):
            xs, ys = sbend_xy(x, y, bl, -s_ * (sep / 2 - 0.25)); segs.append((xs, ys))
            segs.append((np.array([x + bl, x + bl + cl]), np.array([y0 + s_ * 0.25] * 2)))
            xs, ys = sbend_xy(x + bl + cl, y0 + s_ * 0.25, bl, s_ * (sep / 2 - 0.25)); segs.append((xs, ys))
    for y in (yu, yd):
        segs.append((np.array([x0 + 2 * bl + cl, x0 + L - 2 * bl - cl]), np.array([y, y])))
    for xs, ys in segs:
        ribbon(ax, xs, ys, w, "si", z=2)
    if heat:
        box(ax, x0 + 2 * bl + cl + 1.2, yd - 0.35, L - 4 * bl - 2 * cl - 2.4, 0.7, "tin", z=3, alpha=0.85)
    if path:
        ax.plot([x0 - 1.2, x0], [yu, yu], color=col, lw=1.6, zorder=4, solid_capstyle="butt")
        yo = yu if path == "bar" else yd
        arrow(ax, (x0 + L, yo), (x0 + L + 1.4, yo), col=col, lw=1.6, ms=7)
    return yu, yd


def route(st, i):
    """Path of input i (rows 0..3, top to bottom) through a 4 x 4 Benes network of switches A, B | C, D | E, F with
    states st (0 bar, 1 cross): list of (position, row), position 0, 1, 2 entering a stage and 0.5, 1.5, 2.5 leaving it."""
    sw = lambda stage, row: 2 * stage + row // 2
    through = lambda stage, row: row if st[sw(stage, row)] == 0 else (row ^ 1)
    w = {0: 0, 1: 2, 2: 1, 3: 3}                                 # perfect-shuffle wiring between stages
    path, r = [(0, i)], i
    for stage in range(3):
        if stage: r = w[r]; path.append((stage, r))
        r = through(stage, r); path.append((stage + 0.5, r))
    return path


def benes_states(perm):
    """Switch states that realise input i -> output perm[i], found by trying all 64 settings."""
    import itertools
    for st in itertools.product((0, 1), repeat=6):
        if [route(st, i)[-1][1] for i in range(4)] == list(perm):
            return st
    return None


def fig_switch():
    fig = plt.figure(figsize=(6.3, 2.75))
    # a: the two states of a 2 x 2 MZI switch
    a = fig.add_axes([0.0, 0.0, 0.40, 1.0]); frameless(a, (-3.0, 18.6), (-7.6, 5.6), equal=False)
    for y0, heat, st, txt in ((2.2, False, "cross", "heater off, Δφ = 0: cross"), (-4.4, True, "bar", "heater on, Δφ = π: bar")):
        mzi_icon(a, 0, y0, L=15.0, heat=heat, path=st)
        a.text(7.5, y0 + 1.75, txt, ha="center", va="bottom", fontsize=6.8, color=INK)
        a.text(-1.4, y0 + 1.2, "in", ha="right", va="center", fontsize=6.5, color=INK)
    panel(a, "a", x=0.0, y=1.0)
    # b: 4 x 4 Benes network of six switches
    b = fig.add_axes([0.42, 0.0, 0.58, 1.0]); frameless(b, (-1.6, 11.6), (-0.9, 4.9), equal=False)
    perm = (2, 0, 3, 1)                                          # in 1 -> out 3, in 2 -> out 1, in 3 -> out 4, in 4 -> out 2
    st = benes_states(perm)
    print("Benes 4x4 switch states (0 bar, 1 cross) for in -> out", [p + 1 for p in perm], ":", st)
    X = {0: 1.2, 1: 5.0, 2: 8.8}                                  # switch column centres
    Y = lambda row: 3.6 - row * 1.0 - (0.4 if row >= 2 else 0)   # port rows, a gap between the two switches of a stage
    cols = [C1, C2, C3, C5]
    for stage in range(3):
        for k in range(2):
            yt, yb = Y(2 * k), Y(2 * k + 1)
            block(b, X[stage], (yt + yb) / 2, 1.6, 1.55, "", fc="#F3F6FB", ec=MUTED, lw=0.7, r=0.12, z=1)
            b.text(X[stage], yb - 0.62, "cross" if st[2 * stage + k] else "bar", ha="center", va="top", fontsize=6.0, color=MUTED, style="italic")
    for i in range(4):
        pth = route(st, i)
        pts = [(-0.4, Y(i))]
        for pos, row in pth:
            stage = int(pos)
            pts.append((X[stage] - 0.8 if pos == stage else X[stage] + 0.8, Y(row)))
        pts.append((10.4, Y(pth[-1][1])))
        P = np.array(pts)
        b.plot(P[:, 0], P[:, 1], color=cols[i], lw=1.5, zorder=4, solid_joinstyle="round")
        b.text(-0.55, Y(i), f"in {i+1}", ha="right", va="center", fontsize=6.5, color=cols[i])
        b.text(10.55, Y(pth[-1][1]), f"out {pth[-1][1]+1}", ha="left", va="center", fontsize=6.5, color=cols[i])
    b.text(5.0, 4.55, "4 × 4 Beneš network of 2 × 2 MZI switches", ha="center", va="center", fontsize=6.8, color=INK)
    panel(b, "b", x=0.0, y=1.0)
    note(b, "not to scale", loc="lower right")
    save(fig, "ch11_switch")


if __name__ == "__main__":
    fig_chain()
    fig_phase()
    fig_switch()
    fig_lattice()
    fig_ng()
