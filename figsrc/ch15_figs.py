"""Figures for Chapter 15 (grating couplers).

Run from the repository root:   python -I -X utf8 figsrc/ch15_figs.py [name ...]
Writes assets/figs/ch15_*.svg and prints every number the figures and captions use.

Models are the chapter's own: averaged-index phase matching (Worked Example 15.1: slab indices 2.848 / 2.539 for
220 / 150 nm, fill 50 %), the thin-sheet directionality model of Section 15.2 and the gceff demo, the exponential
emission of a uniform grating against the SMF-28 Gaussian (w0 = 5.2 um) of Section 15.3, the angular-acceptance
bandwidth of Section 15.4 (n_g = 3.5) and the two-mirror Fabry-Perot of Section 15.5 (strip n_g = 4.18, Chapter 6).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: E402,F401
from geomstyle import *     # noqa: E402,F401

LAM = 1.55
N_HI, N_LO, FF = 2.848, 2.539, 0.5          # TE slab indices of 220 nm and 150 nm Si (Chapter 5), fill factor
N_EFF = FF * N_HI + (1 - FF) * N_LO          # 2.694
N_OX, N_SI = 1.444, 3.476
TH_AIR = 8.0                                 # fibre angle in air, degrees
S_AIR = math.sin(math.radians(TH_AIR))
TH_OX = math.degrees(math.asin(S_AIR / N_OX))
PERIOD_EST = LAM / (N_EFF - S_AIR)           # 0.607 um (Worked Example 15.1)
PERIOD_SIM = 0.607                           # drawn: Worked Example 15.1 (Lab 6's 2D FDTD puts its peak within 1 nm of 1550 nm)
W0 = 5.2                                     # SMF-28 mode radius at 1550 nm
T_SI, ETCH, BOX = 0.22, 0.07, 2.0
R_SUB = (N_SI - N_OX) / (N_SI + N_OX)         # 0.413


def numbers():
    print(f"n_eff (averaged) = {N_EFF:.3f}; sin 8 deg = {S_AIR:.3f}; period = {PERIOD_EST*1000:.1f} nm; "
          f"angle in oxide = {TH_OX:.2f} deg")
    print(f"substrate field reflection r = {R_SUB:.3f}, power {R_SUB**2*100:.1f} %")


# =====================================================================================================
# Figure 15.1: the grating coupler to scale (side view of the whole stack, and a zoom of the teeth)
# =====================================================================================================
def fig_xsection():
    z0, z1, y0, y1 = -6.0, 26.0, -3.0, 13.5
    W = 6.3
    H = W * (y1 - y0) / (z1 - z0)
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); frameless(ax, (z0, z1), (y0, y1))
    LG, TOP = 20.0, T_SI + 2.0                       # grating length (Table 15.1), top of the oxide cladding (drawn 2 um)
    box(ax, z0, y0, z1 - z0, -BOX - y0, "sub")
    box(ax, z0, -BOX, z1 - z0, BOX, "ox")
    box(ax, z0, 0, z1 - z0, TOP, "oxtop")
    # silicon: input waveguide, teeth (unetched, fill 50 %) and grooves (150 nm left)
    box(ax, z0, 0, -z0, T_SI, "si", z=3)
    n = int(round(LG / PERIOD_SIM))
    for i in range(n):
        za = i * PERIOD_SIM
        box(ax, za, 0, FF * PERIOD_SIM, T_SI, "si", z=3)
        box(ax, za + FF * PERIOD_SIM, 0, (1 - FF) * PERIOD_SIM, T_SI - ETCH, "si", z=3)
    zend = n * PERIOD_SIM
    # beam: up through the oxide at TH_OX, refracted to 8 deg in air, into the fibre core
    zb, h_air = 3.8, 10.0                             # beam centre on the grating (Section 15.3), fibre face height above the oxide
    t_ox, t_air = math.tan(math.radians(TH_OX)), math.tan(math.radians(TH_AIR))
    zt = zb + (TOP - T_SI) * t_ox                     # where the beam axis leaves the oxide
    zf, yf = zt + h_air * t_air, TOP + h_air          # fibre face centre
    ux, uy = math.sin(math.radians(TH_AIR)), math.cos(math.radians(TH_AIR))   # fibre axis (up-right)
    px, py = uy, -ux                                  # across the fibre axis
    L = 40
    clad = [(zf - 62.5 * px, yf - 62.5 * py), (zf + 62.5 * px, yf + 62.5 * py),
            (zf + 62.5 * px + L * ux, yf + 62.5 * py + L * uy), (zf - 62.5 * px + L * ux, yf - 62.5 * py + L * uy)]
    poly(ax, clad, "glass", z=2)
    core = [(zf - 4.1 * px, yf - 4.1 * py), (zf + 4.1 * px, yf + 4.1 * py),
            (zf + 4.1 * px + L * ux, yf + 4.1 * py + L * uy), (zf - 4.1 * px + L * ux, yf - 4.1 * py + L * uy)]
    poly(ax, core, "core", z=2)
    ax.plot([zf - 62.5 * px, zf + 62.5 * px], [yf - 62.5 * py, yf + 62.5 * py], color=MUTED, lw=0.6, zorder=3)
    # the up-going beam: 1/e2 band of the fibre mode (2 w0 = 10.4 um), in oxide and in air
    hw = W0 / math.cos(math.radians(TH_OX))
    poly(ax, [(zb - hw, T_SI), (zb + hw, T_SI), (zt + hw, TOP), (zt - hw, TOP)], AMBER, alpha=0.28, z=4)
    hwa = W0 / math.cos(math.radians(TH_AIR))
    poly(ax, [(zt - hwa, TOP), (zt + hwa, TOP), (zf + W0 * px, yf + W0 * py), (zf - W0 * px, yf - W0 * py)], AMBER, alpha=0.28, z=4)
    ax.plot([zb, zt, zf], [T_SI, TOP, yf], color=AMBER, lw=0.9, ls=(0, (6, 2, 1, 2)), zorder=5)
    arrow(ax, (zt + 1.0 * t_air, TOP + 1.0), (zt + 3.6 * t_air, TOP + 3.6), col=AMBER, lw=1.6, ms=10)
    # down-going light, its reflection from the substrate (17 %) and what is lost
    zd = 2.6
    arrow(ax, (zd, -0.12), (zd + 1.8 * t_ox, -BOX + 0.06), col=AMBER, lw=1.3, ms=8)
    arrow(ax, (zd + 0.9, -BOX + 0.06), (zd + 0.9 + 1.8 * t_ox, -0.12), col=AMBER, lw=1.1, ms=7, ls=(0, (3, 2)))
    arrow(ax, (zd + 0.25, -BOX - 0.06), (zd + 0.25 + 0.75 * t_ox, -BOX - 0.8), col=AMBER, lw=1.1, ms=7)
    label(ax, zd + 1.7, -1.0, "17 % reflected back up", fs=FS_SMALL, ha="left")
    label(ax, zd + 1.7, -2.45, "the rest is lost in the substrate", fs=FS_SMALL, ha="left")
    label(ax, zd - 0.5, -1.0, "emitted\ndown", fs=FS_SMALL, ha="right")
    # input
    arrow(ax, (-5.6, 0.75), (-2.0, 0.75), col=RED, lw=1.1, ms=8)
    label(ax, -5.6, 1.35, "TE mode in", fs=FS_SMALL, ha="left", col=RED)
    label(ax, -5.6, -0.45, "220 nm Si", fs=FS_SMALL, ha="left")
    # angle marks: vertical reference and arc in air
    ax.plot([zt, zt], [TOP, TOP + 7.0], color=MUTED, lw=0.7, ls=(0, (2, 2)), zorder=5)
    a = np.radians(np.linspace(90 - TH_AIR, 90, 30)); r = 6.2
    ax.plot(zt + r * np.cos(a), TOP + r * np.sin(a), color=INK, lw=0.9, zorder=6)
    label(ax, zt + 0.5, TOP + r + 0.55, "8°", fs=FS, ha="left", bg="white")
    callout(ax, (zb - 3.2, 1.2), (-2.4, 3.2), f"{TH_OX:.1f}° in the oxide", ha="right")
    # layer labels
    label(ax, z1 - 0.4, -2.55, "Si substrate", fs=FS, ha="right")
    label(ax, z1 - 0.4, -1.0, "BOX 2 µm", fs=FS, ha="right")
    label(ax, z1 - 0.4, 1.45, "oxide cladding", fs=FS, ha="right")
    label(ax, z1 - 0.4, 2.75, "air", fs=FS, ha="right", col=MUTED)
    dim(ax, (0, 0.85), (zend, 0.85), f"grating {zend:.0f} µm", fs=FS_SMALL, text_off=(5.0, 0))
    label(ax, z1 - 0.4, 12.6, "SMF-28: cladding 125 µm (beyond the frame)", fs=FS_SMALL, ha="right")
    callout(ax, (zf + 2.0 * px + 0.6 * ux, yf + 2.0 * py + 0.6 * uy), (zf + 6.5, yf - 1.6), "core 8.2 µm", ha="left")
    callout(ax, (zt - hwa + 4.0 * t_air + 0.4, TOP + 4.0), (-2.0, TOP + 3.3), "beam, 10.4 µm\nwide (1/e$^2$)", ha="right")
    scalebar(ax, -5.0, 8.8, 5.0, "5 µm")
    panel(ax, "a", 0.005, 0.995)
    # zoom of three periods, to scale (inset in the empty air on the right)
    zx0, zx1, zy0, zy1 = -0.12, 3 * PERIOD_SIM + 0.12, -0.30, 0.50
    yb0, yb1 = 3.4, 8.6                                # data heights of the inset in panel a
    h_in = (yb1 - yb0) / (y1 - y0)
    w_in = h_in * H * (zx1 - zx0) / (zy1 - zy0) / W
    x_in = 0.965 - w_in
    ai = fig.add_axes([x_in, (yb0 - y0) / (y1 - y0), w_in, h_in]); frameless(ai, (zx0, zx1), (zy0, zy1))
    box(ai, zx0, zy0, zx1 - zx0, -zy0, "ox"); box(ai, zx0, 0, zx1 - zx0, zy1, "oxtop")
    for i in range(-1, 4):
        za = i * PERIOD_SIM
        box(ai, za, 0, FF * PERIOD_SIM, T_SI, "si", z=3)
        box(ai, za + FF * PERIOD_SIM, 0, (1 - FF) * PERIOD_SIM, T_SI - ETCH, "si", z=3)
    ai.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, fc="none", ec=MUTED, lw=0.6, zorder=8))
    dim(ai, (0, 0.34), (PERIOD_SIM, 0.34), f"Λ = {PERIOD_SIM*1000:.0f} nm", fs=FS_SMALL, text_off=(0, 0.075), bg=None)
    dim(ai, (2 * PERIOD_SIM, 0.28), (2.5 * PERIOD_SIM, 0.28), "fill 50 %", fs=FS_SMALL, text_off=(0.02, 0.07), bg=None)
    dim(ai, (2.75 * PERIOD_SIM, 0), (2.75 * PERIOD_SIM, T_SI), "")
    label(ai, 2.8 * PERIOD_SIM, 0.11, "220\nnm", fs=FS_SMALL, ha="left")
    dim(ai, (1.25 * PERIOD_SIM, T_SI - ETCH), (1.25 * PERIOD_SIM, T_SI), "")
    ai.plot([1.25 * PERIOD_SIM, 1.36 * PERIOD_SIM], [T_SI - ETCH - 0.005, -0.13], color=MUTED, lw=0.5, zorder=7)
    label(ai, 1.38 * PERIOD_SIM, -0.17, "70 nm etch", fs=FS_SMALL, ha="left")
    panel(ai, "b", 0.012, 0.975)
    # leader from the inset down to the grating
    zc = z0 + (x_in + w_in / 2) * (z1 - z0)
    ax.plot([zc, zc], [yb0, T_SI + 0.05], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=7)
    save(fig, "ch15_xsection")
    print(f"Fig 15.1: period drawn {PERIOD_SIM*1000:.0f} nm, {n} periods = {zend:.1f} um; oxide angle {TH_OX:.2f} deg; "
          f"fibre face {h_air:.0f} um above the cladding at z = {zf:.2f} um; inset at z = {zc:.1f} um")


# =====================================================================================================
# Figure 15.2: wavevector diagrams, 8 degree coupler and vertical coupling
# =====================================================================================================
def _kpanel(ax, K, title_lab, vertical=False):
    xl, yl = (-3.15, 3.15), (-1.75, 1.95)
    frameless(ax, xl, yl)
    # half planes: cladding above, BOX below
    ax.add_patch(Rectangle((xl[0], 0), xl[1] - xl[0], yl[1], fc=MAT["oxtop"], ec="none", zorder=0))
    ax.add_patch(Rectangle((xl[0], yl[0]), xl[1] - xl[0], -yl[0], fc=MAT["ox"], ec="none", zorder=0))
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(N_OX * np.cos(t), N_OX * np.sin(t), color=TEAL, lw=1.0, zorder=2)
    if not vertical:
        tt = np.linspace(0, np.pi, 200)
        ax.plot(np.cos(tt), np.sin(tt), color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
    ax.plot(xl, [0, 0], color=INK, lw=0.6, zorder=2)
    ax.text(xl[1], -0.07, "$k_z/k_0$", ha="right", va="top", fontsize=FS_SMALL, color=INK)
    kz = N_EFF - K
    # beta along the waveguide, then -K (drawn just above and below the axis)
    arrow(ax, (0, -0.10), (N_EFF, -0.10), col=BLUE, lw=1.5, ms=9, z=5)
    label(ax, 2.25, -0.32, f"β/k$_0$ = {N_EFF:.3f}", fs=FS_SMALL, col=BLUE)
    arrow(ax, (N_EFF, 0.12), (kz, 0.12), col=RED, lw=1.5, ms=9, z=5)
    if vertical:
        arrow(ax, (kz, 0.30), (kz - K, 0.30), col=RED, lw=1.2, ms=8, z=5, ls=(0, (4, 2)))
        label(ax, N_EFF / 2 + 0.25, 0.17, "−K", fs=FS_SMALL, col=RED, va="bottom")
        label(ax, -N_EFF / 2, 0.36, "−K again", fs=FS_SMALL, col=RED, va="bottom")
        ax.plot([-N_EFF], [0], "o", ms=4.5, color=RED, zorder=6)
        callout(ax, (-N_EFF, -0.05), (-3.0, -1.0), "β − 2K = −β:\nthe backward\nguided mode\n(second-order\nBragg reflection)", ha="left")
    else:
        label(ax, N_EFF / 2 + 0.6, 0.31, f"−K = −λ/Λ = −{K:.3f}", fs=FS_SMALL, col=RED, va="bottom")
    # radiated waves where kz meets the circles
    ax.plot([kz, kz], [yl[0] + 0.05, yl[1] - 0.12], color=INK, lw=0.6, ls=(0, (2, 2)), zorder=3)
    up, dn = math.sqrt(N_OX ** 2 - kz ** 2), -math.sqrt(N_OX ** 2 - kz ** 2)
    arrow(ax, (0, 0), (kz, up), col=TEAL, lw=1.5, ms=9, z=5)
    arrow(ax, (0, 0), (kz, dn), col=TEAL, lw=1.2, ms=8, z=5, ls=(0, (4, 2)))
    if not vertical:
        ua = math.sqrt(1 - kz ** 2)
        arrow(ax, (0, 0), (kz, ua), col=INK, lw=1.0, ms=7, z=6)
        callout(ax, (kz + 0.02, up - 0.05), (0.75, 1.62), f"oxide cladding: {TH_OX:.1f}°", ha="left")
        callout(ax, (kz * 0.75, ua * 0.75), (-0.45, 1.2), "air: 8°", ha="right")
        label(ax, -0.18, 0.40, "air, n = 1", fs=FS_SMALL, col=MUTED, ha="right", va="bottom")
        callout(ax, (kz + 0.02, dn + 0.05), (0.75, -1.55), "into the BOX", ha="left")
        label(ax, kz + 0.05, yl[1] - 0.05, f"$k_z/k_0$ = {kz:.3f} = sin 8°", fs=FS_SMALL, ha="left", va="top")
    else:
        callout(ax, (0.02, up - 0.1), (0.6, 1.62), "straight up (θ = 0)", ha="left")
        callout(ax, (0.02, dn + 0.1), (0.6, -1.55), "straight down", ha="left")
    label(ax, 2.95, 1.25, "n = 1.444", fs=FS_SMALL, col=TEAL, ha="right")
    label(ax, xl[0] + 0.35, 1.72, "cladding", fs=FS_SMALL, col=MUTED, ha="left")
    label(ax, xl[1] - 0.05, -1.55, "BOX", fs=FS_SMALL, col=MUTED, ha="right")
    panel(ax, title_lab, 0.0, 1.0)


def fig_kdiagram():
    fig = plt.figure(figsize=(6.3, 2.25))
    a1 = fig.add_axes([0.0, 0.0, 0.49, 1.0]); a2 = fig.add_axes([0.51, 0.0, 0.49, 1.0])
    K8 = LAM / PERIOD_EST
    _kpanel(a1, K8, "a")
    Kv = N_EFF                                   # vertical coupling: Lambda = lambda / n_eff
    _kpanel(a2, Kv, "b", vertical=True)
    label(a2, 3.1, 0.62, f"Λ = λ/n$_\\mathrm{{eff}}$ = {LAM / N_EFF * 1000:.0f} nm", fs=FS_SMALL, ha="right", col=RED)
    label(a1, 3.1, 0.62, f"Λ = {PERIOD_EST * 1000:.0f} nm", fs=FS_SMALL, ha="right", col=RED)
    save(fig, "ch15_kdiagram")
    print(f"Fig 15.2: K(8 deg) = {K8:.3f}, kz = {N_EFF - K8:.3f}; vertical period {LAM / N_EFF * 1000:.1f} nm, 2K = {2 * Kv:.3f}")


# =====================================================================================================
# Figure 15.3: directionality, thin-sheet model (as in the gceff demo)
# =====================================================================================================
def directionality(t, r, lam=LAM):
    ph = 2 * (2 * np.pi / lam) * N_OX * t * np.cos(np.radians(TH_OX)) + np.pi
    up = 1 + r * r + 2 * r * np.cos(ph)
    return up / (up + 1 - r * r)


def fig_directionality():
    fig = plt.figure(figsize=(6.3, 2.55))
    ad = fig.add_axes([0.0, 0.02, 0.36, 0.96]); frameless(ad, (0, 10), (0, 8.4), equal=False)
    # layers (schematic)
    box(ad, 0, 0, 10, 1.6, "sub"); box(ad, 0, 1.6, 10, 3.6, "ox"); box(ad, 0, 5.2, 10, 3.2, "oxtop")
    box(ad, 0.6, 5.12, 8.4, 0.16, "si", z=3)
    label(ad, 0.35, 0.55, "Si substrate", fs=FS_SMALL, ha="left")
    label(ad, 0.35, 2.05, "BOX", fs=FS_SMALL, ha="left")
    label(ad, 9.6, 7.95, "cladding", fs=FS_SMALL, ha="right")
    label(ad, 9.0, 5.62, "grating as a thin sheet", fs=FS_SMALL, ha="right")
    # emitted up and down, reflected, transmitted
    arrow(ad, (2.6, 5.35), (2.95, 7.4), col=AMBER, lw=1.5, ms=9)
    label(ad, 2.5, 6.6, "1", fs=FS, ha="right", col=AMBER)
    arrow(ad, (3.4, 5.05), (4.0, 1.68), col=AMBER, lw=1.5, ms=9)
    label(ad, 3.45, 3.1, "1", fs=FS, ha="right", col=AMBER)
    arrow(ad, (4.3, 1.68), (4.9, 5.05), col=AMBER, lw=1.2, ms=8, ls=(0, (3, 2)))
    arrow(ad, (4.95, 5.35), (5.3, 7.4), col=AMBER, lw=1.2, ms=8, ls=(0, (3, 2)))
    label(ad, 5.0, 3.15, "$r\\,e^{j\\varphi}$", fs=FS, ha="left", col=AMBER)
    arrow(ad, (4.15, 1.5), (4.45, 0.15), col=AMBER, lw=1.0, ms=7)
    label(ad, 4.65, 0.75, "lost: $1-r^2$ of the\ndownward power", fs=FS_SMALL, ha="left")
    label(ad, 4.0, 8.05, "up: $1 + r\\,e^{j\\varphi}$", fs=FS, ha="center", col=INK)
    label(ad, 8.1, 1.6 + 0.22, f"r = {R_SUB:.2f}", fs=FS_SMALL, ha="left", va="bottom")
    dim(ad, (9.55, 1.6), (9.55, 5.12), "", fs=FS_SMALL)
    label(ad, 9.35, 3.75, "t", fs=FS, ha="right", italic=True)
    label(ad, 9.35, 2.75, "$\\varphi = 2k_0n_\\mathrm{ox}t\\cos\\theta + \\pi$", fs=FS_SMALL, ha="right")
    note(ad, "schematic", "lower right")
    panel(ad, "a", 0.0, 1.0)
    # directionality against BOX thickness
    ap = fig.add_axes([0.47, 0.17, 0.52, 0.75])
    t = np.linspace(1.0, 3.5, 2501)
    Dsi, Dm = directionality(t, R_SUB), directionality(t, 0.95)
    ap.plot(t, 100 * Dm, color=C3, lw=1.4, label="bottom mirror (r = 0.95)")
    ap.plot(t, 100 * Dsi, color=C1, lw=1.8, label=f"Si substrate (r = {R_SUB:.2f})")
    ap.axhline(50, color=MUTED, lw=0.7, ls=(0, (3, 2)))
    # maxima of the substrate curve near 2 um, and the 2 um point
    mx = [t[i] for i in range(1, len(t) - 1) if Dsi[i] > Dsi[i - 1] and Dsi[i] >= Dsi[i + 1]]
    mn = [t[i] for i in range(1, len(t) - 1) if Dsi[i] < Dsi[i - 1] and Dsi[i] <= Dsi[i + 1]]
    best = [m for m in mx if 1.7 < m < 2.6]
    D2 = float(directionality(2.0, R_SUB))
    for m in best:
        ap.plot([m], [100 * directionality(m, R_SUB)], "o", ms=4, color=C1, zorder=5)
    ap.plot([2.0], [100 * D2], "o", ms=5, mfc="white", mec=C1, mew=1.4, zorder=6)
    ap.annotate(f"2 µm: {100 * D2:.0f} %", xy=(2.0, 100 * D2), xytext=(1.69, 12), fontsize=6.8, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=3))
    for m in best:
        ap.text(m, 100 * directionality(m, R_SUB) + 3.5, f"{m:.2f} µm", ha="center", va="bottom", fontsize=6.8, color=INK)
    per = best[1] - best[0]
    ap.set_xlim(1.0, 3.5); ap.set_ylim(0, 100)
    ap.set_yticks([0, 25, 50, 75, 100])
    ap.legend(loc="lower left", fontsize=6.8, ncol=2, bbox_to_anchor=(0.04, 1.0), handlelength=1.6, columnspacing=1.2)
    finish(ap, "BOX thickness t (µm)", "directionality (%)")
    tag(ap, "b")
    save(fig, "ch15_directionality")
    print(f"Fig 15.3: D(2 um) = {100 * D2:.1f} %, maxima at {best[0]:.3f} / {best[1]:.3f} um (period {per:.3f} um); "
          f"range {100 * Dsi.min():.1f}-{100 * Dsi.max():.1f} %; mirror range {100 * Dm.min():.1f}-{100 * Dm.max():.1f} %; "
          f"minima {[round(m, 3) for m in mn]}")


# =====================================================================================================
# Figure 15.4: overlap of the exponential emission of a uniform grating with the fibre Gaussian
# =====================================================================================================
def overlap(inv_a, zf, w=W0):
    """|integral sqrt(2a) e^{-az} g(z) dz|^2 over z > 0 (grating long enough to emit everything), closed form."""
    a = 1.0 / inv_a
    m = zf - a * w * w / 2
    I = math.exp(a * a * w * w / 4 - a * zf) * w * math.sqrt(math.pi) / 2 * math.erfc(-m / w)
    return 2 * a * math.sqrt(2 / (math.pi * w * w)) * I * I


def best_overlap(inv_a):
    zs = np.linspace(-5, 40, 1801)
    v = [overlap(inv_a, z) for z in zs]
    i = int(np.argmax(v))
    return v[i], zs[i]


def fig_overlap():
    fig = plt.figure(figsize=(6.3, 2.5))
    a1 = fig.add_axes([0.075, 0.17, 0.40, 0.72]); a2 = fig.add_axes([0.585, 0.17, 0.40, 0.72])
    # optimum
    grid = np.linspace(0.2, 6.0, 1161) * W0
    ov = np.array([best_overlap(x)[0] for x in grid])
    i0 = int(np.argmax(ov)); inv_opt = grid[i0]; ov_opt, zf_opt = best_overlap(inv_opt)
    cases = [(0.5 * W0, "too strong", C4), (inv_opt, "best uniform", C1), (4.0 * W0, "too weak", C2)]
    z = np.linspace(-6, 32, 500)
    g = np.sqrt(2 / (np.pi * W0 ** 2)) * np.exp(-2 * (z - zf_opt) ** 2 / W0 ** 2)
    a1.fill_between(z, 0, g, color=MUTED, alpha=0.15, lw=0)
    a1.plot(z, g, color=MUTED, lw=1.2, ls=(0, (4, 2)), label=f"fibre mode at z = {zf_opt:.1f} µm")
    for inv, lab, col in cases:
        a = 1 / inv
        p = np.where(z >= 0, 2 * a * np.exp(-2 * a * np.clip(z, 0, None)), 0)
        a1.plot(z, p, color=col, lw=1.6, label=f"{lab}, 1/α = {inv:.1f} µm")
    a1.axvline(0, color=INK, lw=0.6)
    a1.text(-0.6, 0.2, "grating starts", fontsize=6.5, color=INK, va="center", ha="right", rotation=90)
    a1.text(1.0, 0.395, f"peak {2 / cases[0][0]:.2f}", fontsize=6.3, color=C4, va="top", ha="left")
    a1.set_xlim(-6, 32); a1.set_ylim(0, 0.40)
    a1.set_yticks([0, 0.1, 0.2, 0.3, 0.4])
    a1.legend(loc="upper right", fontsize=6.4, handlelength=1.5)
    finish(a1, "position along the grating z (µm)", "power emitted per µm (1/µm)")
    tag(a1, "a")
    # overlap against 1/alpha
    x = grid[::4]
    a2.plot(x, 100 * ov[::4], color=C1, lw=1.8)
    for inv, lab, col in cases:
        o, zf = best_overlap(inv)
        a2.plot([inv], [100 * o], "o", ms=5, color=col, zorder=5)
        print(f"   {lab}: 1/alpha = {inv:.2f} um -> best overlap {100 * o:.1f} % at z_fibre = {zf:.2f} um")
    a2.annotate(f"{100 * ov_opt:.0f} % at 1/α = {inv_opt:.1f} µm\n= {inv_opt / W0:.2f} w$_0$, fibre at {zf_opt:.1f} µm",
                xy=(inv_opt, 100 * ov_opt), xytext=(11.5, 86), fontsize=6.8, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=3))
    a2.axhline(95, color=C3, lw=0.8, ls=(0, (3, 2)))
    a2.text(30.5, 96.5, "apodised: above 95 %", fontsize=6.5, color=C3, ha="right", va="bottom")
    a2.set_xlim(0, 31); a2.set_ylim(0, 105)
    a2.set_yticks([0, 20, 40, 60, 80, 100])
    finish(a2, "1/α, emission length (µm)", "best overlap (%)")
    tag(a2, "b")
    save(fig, "ch15_overlap")
    print(f"Fig 15.4: best uniform overlap {100 * ov_opt:.2f} % at 1/alpha = {inv_opt:.2f} um = {inv_opt / W0:.3f} w0, "
          f"fibre at {zf_opt:.2f} um ({10 * math.log10(ov_opt):.2f} dB)")


# =====================================================================================================
# Figure 15.5: bandwidth from the fibre's angular acceptance
# =====================================================================================================
def theta_air(lam, ng, period=PERIOD_EST):
    ne = N_EFF - (ng - N_EFF) * (lam - LAM) / LAM          # first-order dispersion of the grating index
    s = np.clip(ne - lam / period, -1, 1)
    return np.degrees(np.arcsin(s))


def coupling(lam, ng, w0=W0, period=PERIOD_EST):
    dth = np.radians(theta_air(lam, ng, period) - TH_AIR)
    return np.exp(-(np.pi * w0 * dth / lam) ** 2)


def bw1db(ng, w0=W0):
    """1 dB bandwidth (um) of the angular-acceptance model; the period is re-chosen so the peak sits at 1550 nm."""
    period = LAM / (N_EFF - S_AIR)
    lam = np.linspace(LAM - 0.4, LAM + 0.4, 160001)
    e = coupling(lam, ng, w0, period)
    ok = lam[e >= 10 ** -0.1]
    return ok[-1] - ok[0], ok[0], ok[-1]


def fig_bandwidth():
    NG = 3.5
    fig = plt.figure(figsize=(6.3, 2.5))
    a1 = fig.add_axes([0.075, 0.17, 0.40, 0.72]); a2 = fig.add_axes([0.585, 0.17, 0.40, 0.72])
    dth = math.degrees(math.sqrt(0.1 * math.log(10)) * LAM / (math.pi * W0))
    bw, l1, l2 = bw1db(NG)
    lam = np.linspace(1.49, 1.61, 600)
    th = theta_air(lam, NG)
    a1.axhspan(TH_AIR - dth, TH_AIR + dth, color=C3, alpha=0.13, lw=0)
    a1.axhline(TH_AIR, color=C3, lw=0.9, ls=(0, (4, 2)))
    a1.text(1.6075, TH_AIR + dth - 0.25, f"fibre accepts ±{dth:.1f}°\nwithin 1 dB", fontsize=6.5, color=C3, ha="right", va="top")
    a1.plot(lam, th, color=C1, lw=1.8)
    for l in (l1, l2):
        a1.plot([l, l], [0, theta_air(l, NG)], color=MUTED, lw=0.7, ls=(0, (2, 2)))
    a1.annotate("", xy=(l2, 1.0), xytext=(l1, 1.0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    a1.text((l1 + l2) / 2, 1.35, f"{bw * 1000:.0f} nm", ha="center", va="bottom", fontsize=7, color=INK)
    a1.text(1.493, 14.2, "beam angle in air", fontsize=6.8, color=C1, ha="left", va="center")
    a1.set_xlim(1.49, 1.61); a1.set_ylim(0, 16)
    a1.set_xticks([1.50, 1.52, 1.54, 1.56, 1.58, 1.60])
    a1.set_xticklabels(["1500", "1520", "1540", "1560", "1580", "1600"])
    finish(a1, "wavelength (nm)", "beam angle θ (°)")
    tag(a1, "a")
    # bandwidth against group index for two fibre modes
    ngs = np.linspace(1.6, 4.5, 59)
    for w0, lab, col in ((W0, "SMF-28, mode 10.4 µm", C1), (2.0, "mode 4 µm", C2)):
        b = np.array([bw1db(n, w0)[0] for n in ngs])
        a2.plot(ngs, 1000 * b, color=col, lw=1.8, label=lab)
    a2.plot([NG], [1000 * bw], "o", ms=5, color=C1, zorder=5)
    a2.annotate(f"Si grating, $n_g$ ≈ {NG}:\n{bw * 1000:.0f} nm", xy=(NG, 1000 * bw), xytext=(4.0, 58), fontsize=6.8, color=INK,
                ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=3))
    a2.set_xlim(1.6, 4.5); a2.set_ylim(0, 200)
    a2.legend(loc="upper right", fontsize=6.6)
    finish(a2, "group index of the grating $n_g$", "1 dB bandwidth (nm)")
    tag(a2, "b")
    save(fig, "ch15_bandwidth")
    b4 = bw1db(NG, 2.0)[0]
    print(f"Fig 15.5: 1 dB acceptance +/-{dth:.2f} deg; n_g {NG}: 1 dB bandwidth {bw * 1000:.1f} nm ({l1 * 1000:.1f}-{l2 * 1000:.1f} nm); "
          f"4 um mode: {b4 * 1000:.0f} nm; SMF at n_g 2.0: {bw1db(2.0)[0] * 1000:.0f} nm; "
          f"d(theta)/d(lambda) = {-(NG - S_AIR) / (LAM * math.cos(math.radians(TH_AIR))) * 180 / math.pi / 1000:.3f} deg/nm")


# =====================================================================================================
# Figure 15.6: a loopback spectrum (model) and the Fabry-Perot fringes of back-reflection
# =====================================================================================================
def fig_fringes():
    NG_C, NG_WG, LGAP = 3.5, 4.18, 1000.0           # grating group index; strip group index (Chapter 6); couplers 1 mm apart
    PEAK = 10 * math.log10(0.50)                     # one coupler: uniform grating, 2 um BOX (Table 15.1), -3.0 dB
    fsr = LAM ** 2 / (2 * NG_WG * LGAP)             # um
    fig = plt.figure(figsize=(6.3, 2.5))
    a1 = fig.add_axes([0.075, 0.17, 0.40, 0.72]); a2 = fig.add_axes([0.585, 0.17, 0.40, 0.72])
    lam = np.linspace(1.49, 1.61, 361)
    one = PEAK + 10 * np.log10(coupling(lam, NG_C))
    bw, l1, l2 = bw1db(NG_C)
    R = 10 ** -1.5                                   # -15 dB per coupler
    up, dn = -20 * np.log10(1 - R), -20 * np.log10(1 + R)
    a1.plot(lam, one, color=C1, lw=1.4, ls=(0, (4, 2)), label=f"one coupler (peak {PEAK:.1f} dB)".replace("-", "−"))
    a1.fill_between(lam, 2 * one + dn, 2 * one + up, color=C2, lw=0, alpha=0.9)
    a1.plot(lam, 2 * one, color=C2, lw=0.6, label="loopback, two couplers")
    a1.annotate("", xy=(l2, PEAK - 1), xytext=(l1, PEAK - 1), arrowprops=dict(arrowstyle="<|-|>", color=C1, lw=0.7, mutation_scale=6))
    a1.text((l1 + l2) / 2, PEAK - 1.25, f"1 dB: {bw * 1000:.0f} nm", ha="center", va="top", fontsize=6.6, color=C1)
    a1.set_xlim(1.49, 1.61); a1.set_ylim(-20, 0); a1.set_yticks([-20, -15, -10, -5, 0])
    a1.annotate(f"fringes: {up - dn:.2f} dB\npeak to trough", xy=(1.55, 2 * PEAK - 0.4), xytext=(1.55, -11.5),
                fontsize=6.4, color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a1.set_xticks([1.50, 1.52, 1.54, 1.56, 1.58, 1.60])
    a1.set_xticklabels(["1500", "1520", "1540", "1560", "1580", "1600"])
    a1.legend(loc="lower center", fontsize=6.4, handlelength=1.6)
    finish(a1, "wavelength (nm)", "transmission (dB)")
    tag(a1, "a")
    # zoom: fringes for two reflection levels
    lz = np.linspace(1.5490, 1.5510, 841)
    phi = 4 * np.pi * NG_WG * LGAP / lz
    out = []
    for RdB, col, lw in ((-15, C2, 1.5), (-20, C1, 1.5)):
        Rr = 10 ** (RdB / 10)
        f = -10 * np.log10(np.abs(1 - Rr * np.exp(1j * phi)) ** 2)
        pp = -20 * np.log10(1 - Rr) + 20 * np.log10(1 + Rr)
        out.append((RdB, pp))
        a2.plot((lz - LAM) * 1000, f, color=col, lw=lw, label=f"{RdB} dB per coupler: {pp:.2f} dB peak to trough".replace("-", "−"))
    # FSR marker between two adjacent maxima of the -15 dB curve
    k0 = np.ceil(2 * NG_WG * LGAP / 1.5505)            # phase = 2 pi k at a maximum
    lm1 = 2 * NG_WG * LGAP / (k0 + 1); lm2 = 2 * NG_WG * LGAP / k0
    ya = 0.36
    a2.annotate("", xy=((lm2 - LAM) * 1000, ya), xytext=((lm1 - LAM) * 1000, ya),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    a2.text(((lm1 + lm2) / 2 - LAM) * 1000, ya + 0.03, f"{fsr * 1000:.2f} nm", ha="center", va="bottom", fontsize=6.8)
    a2.set_xlim(-1, 1); a2.set_ylim(-0.55, 0.62); a2.set_xticks([-1, -0.5, 0, 0.5, 1])
    a2.legend(loc="lower center", fontsize=6.4, ncol=1, handlelength=1.6)
    finish(a2, "wavelength − 1550 nm (nm)", "ripple (dB)")
    tag(a2, "b")
    save(fig, "ch15_fringes")
    print(f"Fig 15.6: FSR {fsr * 1000:.3f} nm (n_g {NG_WG}, L {LGAP:.0f} um); peak-to-trough "
          + ", ".join(f"{r} dB -> {p:.3f} dB" for r, p in out) + f"; loopback peak {2 * PEAK:.1f} dB")


# =====================================================================================================
# Figure 15.7: top views: straight vs focusing footprint, focusing grating lines, 2D grating
# =====================================================================================================
ETCHED = "#7C93B0"          # shallow-etched silicon in a top view (a darker shade of MAT["si"])


def focusing_lines(q0=23, nq=31, half=22.0):
    """Confocal ellipses n_eff r - sin(theta_air) x = q lambda with the focus at the waveguide end (Van Laere 2007)."""
    phi = np.radians(np.linspace(-half, half, 41))
    out = []
    for q in range(q0, q0 + nq):
        r0 = q * LAM / (N_EFF - S_AIR * np.cos(phi))
        r1 = r0 + (1 - FF) * LAM / (N_EFF - S_AIR * np.cos(phi))     # groove: the etched part of each period
        out.append((phi, r0, r1))
    return out


def fig_topviews():
    fig = plt.figure(figsize=(6.3, 3.55))
    # (a) footprints to the same scale
    TAPER = 300.0
    aa = fig.add_axes([0.0, 0.70, 1.0, 0.30]); frameless(aa, (-12, 352), (-17, 15))
    yA, yB = 6.5, -9.5
    wg_straight(aa, -10, 0, yA, 0.5)
    wg_taper(aa, 0, TAPER, yA, 0.5, 12.0)
    box(aa, TAPER, yA - 6, 20, 12, ETCHED, z=2)
    aa.add_patch(Circle((TAPER + 3.8, yA), 5.2, fc="none", ec=RED, lw=0.8, ls=(0, (2, 1.5)), zorder=4))
    label(aa, TAPER / 2, yA + 4.5, f"straight grating: linear taper, {TAPER:.0f} µm (illustrative), then a 12 × 20 µm grating", fs=FS_SMALL)
    lines = focusing_lines()
    rmax = lines[-1][2][len(lines[-1][2]) // 2] + 1.0
    wg_straight(aa, -10, 0, yB, 0.5)
    th = np.radians(np.linspace(-22, 22, 60))
    poly(aa, np.vstack([[0, yB]], ) if False else np.vstack([[[0, yB]], np.c_[rmax * np.cos(th), yB + rmax * np.sin(th)]]), "si", z=2)
    aa.add_patch(Circle((18.0, yB), 5.2, fc="none", ec=RED, lw=0.8, ls=(0, (2, 1.5)), zorder=4))
    label(aa, rmax + 6, yB, f"focusing grating: the whole coupler is about {rmax:.0f} µm long", fs=FS_SMALL, ha="left")
    scalebar(aa, 300, -16.0, 50, "50 µm")
    panel(aa, "a", 0.0, 1.0)
    # (b) focusing grating, to scale
    ab = fig.add_axes([0.0, 0.0, 0.5, 0.66]); frameless(ab, (-7, 36), (-17, 17))
    wg_straight(ab, -7, 0.0, 0, 0.5)
    th = np.radians(np.linspace(-22, 22, 120))
    poly(ab, np.vstack([[[0, 0]], np.c_[rmax * np.cos(th), rmax * np.sin(th)]]), "si", z=2)
    for phi, r0, r1 in lines:
        pts = np.vstack([np.c_[r0 * np.cos(phi), r0 * np.sin(phi)], np.c_[r1[::-1] * np.cos(phi[::-1]), r1[::-1] * np.sin(phi[::-1])]])
        poly(ab, pts, ETCHED, z=3)
    zf = lines[0][1][20] + 3.8
    ab.add_patch(Circle((zf, 0), 5.2, fc="none", ec=RED, lw=1.0, ls=(0, (3, 2)), zorder=5))
    callout(ab, (zf, -5.2), (zf, -10.6), "fibre mode, 10.4 µm", ha="center", col=RED)
    callout(ab, (-0.3, 0.3), (-3.0, 7.5), "focus at the\nwaveguide end", ha="center")
    callout(ab, (lines[-1][1][34] * np.cos(lines[-1][0][34]), lines[-1][1][34] * np.sin(lines[-1][0][34])), (30, 14.5),
            "teeth on confocal\nellipses", ha="center")
    scalebar(ab, -5, -15.5, 10, "10 µm")
    panel(ab, "b", 0.0, 1.0)
    # (c) 2D grating: square lattice of holes where two orthogonal waveguides meet (illustrative dimensions)
    ac = fig.add_axes([0.5, 0.0, 0.5, 0.66]); frameless(ac, (-20, 23), (-20, 14))
    G, P2, D2 = 12.0, 0.60, 0.36
    for (x0, y0, x1, y1) in ((-20, 0, -G / 2, 0), (0, -20, 0, -G / 2)):
        if y0 == y1:
            wg_taper(ac, -20, -G / 2, 0, 9.5, G)
        else:
            poly(ac, [(-4.75, -20), (4.75, -20), (G / 2, -G / 2), (-G / 2, -G / 2)], "si", z=2)
    box(ac, -G / 2, -G / 2, G, G, "si", z=2)
    xs = np.arange(-G / 2 + P2 / 2, G / 2, P2)
    HX, HY = np.meshgrid(xs, xs)
    fig.canvas.draw()
    ppd = ac.transData.transform((1, 0))[0] - ac.transData.transform((0, 0))[0]     # pixels per um
    dpt = D2 * ppd * 72 / fig.dpi                                                       # hole diameter in points
    ac.scatter(HX.ravel(), HY.ravel(), s=dpt ** 2, marker="o", c=ETCHED, linewidths=0, zorder=3)
    ac.add_patch(Circle((0, 0), 5.2, fc="none", ec=RED, lw=1.0, ls=(0, (3, 2)), zorder=5))
    # the two fibre polarisations and where they go
    arrow(ac, (8.5, 9.5), (13.5, 9.5), col=C2, lw=1.3, ms=7, style="<|-|>", z=6)
    arrow(ac, (11.0, 7.0), (11.0, 12.0), col=C1, lw=1.3, ms=7, style="<|-|>", z=6)
    label(ac, 15.0, 11.6, "the fibre's two\npolarisations", fs=FS_SMALL, ha="left")
    arrow(ac, (-9, 2.2), (-18, 2.2), col=C1, lw=1.4, ms=8, z=6)
    label(ac, -13.5, 3.6, "TE, waveguide 1", fs=FS_SMALL, col=C1)
    arrow(ac, (2.4, -9), (2.4, -18.5), col=C2, lw=1.4, ms=8, z=6)
    label(ac, 3.9, -14.5, "TE, waveguide 2", fs=FS_SMALL, col=C2, ha="left")
    note(ac, "illustrative dimensions", "lower left")
    callout(ac, (3.7, -3.7), (11.0, -6.5), "fibre mode", ha="left", col=RED)
    scalebar(ac, 12, -18.5, 10, "10 µm")
    panel(ac, "c", 0.0, 1.0)
    save(fig, "ch15_topviews")
    rl = [l[1][20] for l in lines]
    print(f"Fig 15.7: focusing grating: {len(lines)} lines from r = {rl[0]:.2f} to {rl[-1]:.2f} um on axis "
          f"(period {rl[1] - rl[0]:.3f} um on axis, {LAM / (N_EFF - S_AIR * np.cos(np.radians(22))):.3f} um at 22 deg), "
          f"eccentricity {S_AIR / N_EFF:.4f}; coupler length {rmax:.1f} um vs {TAPER + 20:.0f} um")


FIGS = {"xsection": fig_xsection, "kdiagram": fig_kdiagram, "directionality": fig_directionality, "overlap": fig_overlap,
        "bandwidth": fig_bandwidth, "fringes": fig_fringes, "topviews": fig_topviews}

if __name__ == "__main__":
    numbers()
    names = sys.argv[1:] or list(FIGS)
    for nme in names:
        FIGS[nme]()
