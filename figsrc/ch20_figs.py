"""Figures and numbers for Chapter 20 (modulators), Sections 20.1-20.6. The ring-dynamics figures of Sections 20.8-20.9
are drawn by figsrc/ch20_rrm.py; this script imports its static ring model (reference ring of Worked Example 20.2:
R = 7.2 um, n_g = 3.89, Q_i = 15 000, Q_L = 8000, 50 pm/V, 2 Vpp, laser at the 3.0 dB insertion-loss point).

Run from the worktree root:   python -I -X utf8 figsrc/ch20_figs.py
Writes assets/figs/ch20_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
from figstyle import *
from geomstyle import *
import ch20_rrm as rrm

RB = 50e9                     # bit rate of the reference link
UI = 1e12 / RB                # ps
BITS = [0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1]


def smooth_wave(levels, sym_ps, os_=80, rise_ps=6.0):
    """Piecewise-constant symbols smoothed by a Gaussian filter of the given 10-90 % rise time."""
    y = np.repeat(np.asarray(levels, float), os_)
    dt = sym_ps / os_
    sig = rise_ps / 2.563 / dt                     # 10-90 % of an erf edge = 2.563 sigma
    k = np.arange(-int(4 * sig) - 1, int(4 * sig) + 2); g = np.exp(-0.5 * (k / sig) ** 2); g /= g.sum()
    yp = np.r_[np.full(len(k), y[0]), y, np.full(len(k), y[-1])]
    ys = np.convolve(yp, g, mode="same")[len(k):-len(k)]
    return np.arange(len(y)) * dt, ys


# ------------------------------------------------------------------ Figure 20.1: modulator metrics
def fig_metrics():
    # levels of the reference-link target (Worked Example 20.2): 4 dB extinction at 3 dB insertion loss
    ER = 10 ** 0.4; Pav = 10 ** -0.3
    P1, P0 = 2 * Pav * ER / (ER + 1), 2 * Pav / (ER + 1); OMA = P1 - P0
    t_lo, t_hi = rrm.levels(rrm.DET)
    print(f"[20.1] (for comparison, the static ring model at its 3.0 dB point: ER {10*math.log10(max(t_lo,t_hi)/min(t_lo,t_hi)):.2f} dB)")
    t, p = smooth_wave([P1 if b else P0 for b in BITS], UI, rise_ps=7.0)
    fig, ax = plt.subplots(figsize=(6.3, 2.55))
    ax.plot(t, p, color=C1, lw=1.6)
    T = len(BITS) * UI
    for v, ls, col in ((1.0, ":", INK), (P1, "--", MUTED), (P0, "--", MUTED), (Pav, "-.", C2)):
        ax.plot([0, T + 8], [v, v], color=col, lw=0.8, ls=ls)
    ax.text(3, 1.015, "input power $P_\\mathrm{in}$", fontsize=7, va="bottom", color=INK)
    ax.text(T + 10, P1, "$P_1$", fontsize=8, va="center"); ax.text(T + 10, P0, "$P_0$", fontsize=8, va="center")
    ax.text(T + 10, Pav, "$P_\\mathrm{avg}$", fontsize=8, va="center", color=C2)
    xb = T + 42
    ax.annotate("", xy=(xb, P1), xytext=(xb, P0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    ax.text(xb + 4, (P1 + P0) / 2 - 0.08, f"OMA = $P_1 - P_0$\n= {OMA/Pav:.2f} $P_\\mathrm{{avg}}$", fontsize=7, va="center", ha="left")
    xb2 = T + 92
    ax.annotate("", xy=(xb2, 1.0), xytext=(xb2, Pav), arrowprops=dict(arrowstyle="<|-|>", color=C2, lw=0.8, mutation_scale=7))
    ax.text(xb2 + 4, (1.0 + Pav) / 2 + 0.06, f"insertion\nloss {10*math.log10(1/Pav):.1f} dB", fontsize=7, va="center", ha="left", color=C2)
    ax.text(T + 42 + 4, P0 - 0.1, f"ER = $P_1/P_0$ = {10*math.log10(ER):.1f} dB", fontsize=7, va="top", ha="left")
    for k, b in enumerate(BITS):
        ax.text((k + 0.5) * UI, 0.03, str(b), ha="center", va="bottom", fontsize=6.6, color=MUTED)
    ax.set_xlim(0, T + 150); ax.set_ylim(0, 1.12)
    ax.set_xticks(np.arange(0, T + 1, 80))
    ax.spines["bottom"].set_bounds(0, T)
    finish(ax, "Time (ps), 50 Gb/s", "Power / input power")
    save(fig, "ch20_metrics")
    print(f"[20.1] reference-link target: P1 {P1:.3f}, P0 {P0:.3f} (of P_in), P_avg {Pav:.3f} -> IL {10*math.log10(1/Pav):.2f} dB, "
          f"ER {10*math.log10(ER):.2f} dB, OMA {OMA:.3f} P_in = {OMA/Pav:.3f} P_avg")


# ------------------------------------------------------------------ Figure 20.2: travelling-wave MZM
def _rib_doped(ax, xc, left, right, z=2):
    """Rib (500 x 220 nm, 90 nm slab) centred at xc with the left and right halves doped."""
    box(ax, xc - 0.25, 0.09, 0.25, 0.13, left, z=z); box(ax, xc, 0.09, 0.25, 0.13, right, z=z)


def fig_mzm():
    fig = plt.figure(figsize=(6.3, 4.1))
    # (a) schematic top view
    ax = fig.add_axes([0.0, 0.50, 1.0, 0.48]); frameless(ax, (0, 20), (-3.1, 3.1), equal=False)
    ya = 0.75; lw_wg = 2.2
    ax.plot([0.2, 2.0], [0, 0], color=MAT["si"], lw=lw_wg, solid_capstyle="butt", zorder=2)
    box(ax, 2.0, -0.45, 1.0, 0.9, "si", z=2)                                  # 1x2 MMI
    for s in (1, -1):
        xs, ys = sbend_xy(3.0, 0.25 * s, 1.0, (ya - 0.25) * s)
        ax.plot(xs, ys, color=MAT["si"], lw=lw_wg, zorder=2)
        ax.plot([4.0, 16.0], [ya * s, ya * s], color=MAT["si"], lw=lw_wg, solid_capstyle="butt", zorder=2)
        xs, ys = sbend_xy(16.0, ya * s, 1.0, (0.25 - ya) * s)
        ax.plot(xs, ys, color=MAT["si"], lw=lw_wg, zorder=2)
    box(ax, 17.0, -0.45, 1.0, 0.9, "si", z=2)                                 # 2x1 MMI
    ax.plot([18.0, 19.8], [0, 0], color=MAT["si"], lw=lw_wg, solid_capstyle="butt", zorder=2)
    # electrodes (coplanar strips) and the DC bias line between the arms
    box(ax, 5.0, ya + 0.35, 9.0, 0.75, "metal", z=3); box(ax, 5.0, -ya - 1.1, 9.0, 0.75, "metal", z=3)
    ax.plot([5.0, 14.0], [0, 0], color=MAT["metal"], lw=0.8, ls=(0, (2, 1.5)), zorder=3)
    label(ax, 9.5, ya + 0.72, "S (signal)", fs=FS_SMALL, bold=True); label(ax, 9.5, -ya - 0.72, "G (ground)", fs=FS_SMALL, bold=True)
    label(ax, 6.6, 0.0, "DC bias", fs=FS_SMALL - 0.3, bg="white")
    # driver at the input end, termination at the far end
    block(ax, 4.6, 2.55, 1.6, 0.7, "driver", fc="white", ec=ELEC, fs=6.6, col=ELEC)
    ax.plot([5.3, 5.3], [2.2, 1.85], color=ELEC, lw=0.9, zorder=4)
    ax.plot([5.3, 5.3], [-1.85, -2.2], color=ELEC, lw=0.9, zorder=4)
    for k, hw in enumerate((0.3, 0.2, 0.1)):
        ax.plot([5.3 - hw, 5.3 + hw], [-2.2 - 0.17 * k] * 2, color=ELEC, lw=0.9, zorder=4)
    xt = 14.6; zz = np.linspace(-1.0, 1.0, 9)
    ax.plot([14.0, xt, xt], [1.47, 1.47, 1.0], color=ELEC, lw=0.9); ax.plot(xt + 0.18 * np.array([0, 1, -1, 1, -1, 1, -1, 1, 0]), zz[::-1], color=ELEC, lw=0.9)
    ax.plot([xt, xt, 14.0], [-1.0, -1.47, -1.47], color=ELEC, lw=0.9)
    ax.text(xt + 0.35, 0.0, "50 Ω", ha="left", va="center", fontsize=7, color=ELEC)
    # heater for the bias point
    box(ax, 15.0, -ya - 0.17, 0.9, 0.34, "tin", z=4)
    callout(ax, (15.45, -ya - 0.17), (15.9, -2.3), "heater (bias point)", ha="left")
    # travelling waves
    arrow(ax, (6.6, 2.45), (12.5, 2.45), col=ELEC, lw=1.0, ms=7)
    ax.text(12.7, 2.45, "RF wave, $n_\\mathrm{RF} \\approx 3.6$", ha="left", va="center", fontsize=6.8, color=ELEC)
    arrow(ax, (6.6, -2.55), (12.5, -2.55), col=OPT, lw=1.0, ms=7)
    ax.text(12.7, -2.55, "light, $n_g = 3.9$", ha="left", va="center", fontsize=6.8, color=OPT)
    # cut line
    ax.plot([10.5, 10.5], [-2.15, 2.1], color=INK, lw=0.7, ls=(0, (4, 2)), zorder=5)
    ax.text(10.6, 2.15, "A", fontsize=7, fontweight="bold", va="bottom"); ax.text(10.6, -2.15, "A′", fontsize=7, fontweight="bold", va="top")
    note(ax, "not to scale (3 mm long)", loc="lower right")
    panel(ax, "a", x=0.0, y=1.0)
    # (b) cross-section A-A', to scale
    bx = fig.add_axes([0.0, 0.0, 1.0, 0.47]); frameless(bx, (-10.2, 10.2), (-0.75, 3.25))
    box(bx, -10.2, -0.75, 20.4, 0.75, "ox", z=0); box(bx, -10.2, 0, 20.4, 2.35, "oxtop", z=0)
    xa = 3.0                                                                  # arm centres at -3 and +3 um
    # slab doping (lateral junctions back to back, shared n++ in the middle)
    for xa_, xb_, m in ((-10.2, -xa - 1.2, "pp"), (-xa - 1.2, -xa, "pdop"), (-xa, -xa + 1.2, "ndop"), (-xa + 1.2, xa - 1.2, "nn"),
                        (xa - 1.2, xa, "ndop"), (xa, xa + 1.2, "pdop"), (xa + 1.2, 10.2, "pp")):
        box(bx, xa_, 0, xb_ - xa_, 0.09, m, z=2)
    _rib_doped(bx, -xa, "pdop", "ndop"); _rib_doped(bx, xa, "ndop", "pdop")
    for x0 in (-xa, xa):
        box(bx, x0 - 0.25, 0, 0.5, 0.22, "none", ec=INK, lw=0.3, z=3)
    for xv in (-6.5, 6.5, 0.0):
        box(bx, xv - 0.2, 0.09, 0.4, 1.66 if xv else 1.76, "metal", z=3)
    box(bx, -10.2, 1.75, 6.2, 1.0, "metal", z=3); box(bx, 4.0, 1.75, 6.2, 1.0, "metal", z=3)
    box(bx, -0.4, 1.75, 0.8, 0.2, "metal", z=3)
    label(bx, -7.1, 2.25, "S", bold=True, fs=8); label(bx, 7.1, 2.25, "G", bold=True, fs=8)
    label(bx, 0.0, 2.15, "DC bias $V_b$", fs=FS_SMALL)
    for x0, s in ((-xa, "$V_b - v/2$"), (xa, "$V_b + v/2$")):
        label(bx, x0, -0.38, s, fs=FS_SMALL)
    label(bx, -xa - 0.6, 0.38, "p", fs=FS_SMALL); label(bx, -xa + 0.6, 0.38, "n", fs=FS_SMALL)
    label(bx, xa - 0.6, 0.38, "n", fs=FS_SMALL); label(bx, xa + 0.6, 0.38, "p", fs=FS_SMALL)
    label(bx, -8.6, 0.38, "p$^{++}$", fs=FS_SMALL); label(bx, 8.6, 0.38, "p$^{++}$", fs=FS_SMALL); label(bx, -1.0, 0.38, "n$^{++}$", fs=FS_SMALL)
    label(bx, -9.9, -0.38, "BOX", fs=FS_SMALL, col=MUTED, ha="left")
    scalebar(bx, 7.6, -0.62, 2.0, "2 µm")
    note(bx, "electrode heights illustrative", loc="upper right")
    panel(bx, "b", x=0.0, y=1.0)
    save(fig, "ch20_mzm")
    L = 3e-3; ng, nrf = 3.9, 3.6
    print(f"[20.2] velocity-mismatch limit 1.4c/(pi L |n_RF-n_g|) = {1.4*2.998e8/(math.pi*L*abs(nrf-ng))/1e9:.0f} GHz for L = 3 mm")


# ------------------------------------------------------------------ Figure 20.3: ring modulator
def fig_ring():
    R, w, gap = 7.2, 0.5, 0.2
    fig = plt.figure(figsize=(6.3, 3.3))
    ax = fig.add_axes([0.0, 0.0, 0.52, 1.0]); frameless(ax, (-11.5, 11.5), (-10.4, 11.2))
    box(ax, -11.5, -10.4, 23, 21.6, "oxtop", z=0)
    yb = -(R + w + gap)                                                     # bus centre line
    wg_straight(ax, -11.5, 11.5, yb, w, "si")
    span = 0.8 * 360; th0 = -90 + (360 - span) / 2; th1 = th0 + span        # junction on 80 % of the ring, away from the bus
    wg_ring(ax, 0, 0, R, w, "si")
    wg_arc(ax, 0, 0, R - w / 4, w / 2, th0, th1, "pdop", z=3); wg_arc(ax, 0, 0, R + w / 4, w / 2, th0, th1, "ndop", z=3)
    wg_arc(ax, 0, 0, R - 0.85, 1.2, th0, th1, "pdop", z=2, alpha=0.55); wg_arc(ax, 0, 0, R + 0.85, 1.2, th0, th1, "ndop", z=2, alpha=0.55)
    tc0, tc1 = th0 + 12, th1 - 12                                          # contacts kept clear of the bus
    wg_arc(ax, 0, 0, R - 2.1, 1.3, tc0, tc1, "pp", z=2); wg_arc(ax, 0, 0, R + 2.1, 1.3, tc0, tc1, "nn", z=2)
    for th in np.linspace(tc0 + 6, tc1 - 6, 9):                                # vias
        for rr in (R - 2.1, R + 2.1):
            ax.add_patch(Circle((rr * np.cos(np.radians(th)), rr * np.sin(np.radians(th))), 0.3, fc=MAT["metal"], ec="none", zorder=5))
    # TiN heater above the ring: outline only, so the junction stays visible
    wg_arc(ax, 0, 0, R, 1.1, tc0 + 10, tc1 - 10, "none", z=6, ec="#B8691F", lw=0.9, ls=(0, (3, 1.5)))
    callout(ax, (R * np.cos(np.radians(55)) + 0.4, R * np.sin(np.radians(55)) + 0.4), (5.2, 10.4), "TiN heater above (outline)", ha="left", va="center")
    ax.plot([0, 0], [0, R - 0.3], color=INK, lw=0.6); ax.plot(0, 0, "o", color=INK, ms=2)
    label(ax, 0.3, 3.4, "R = 7.2 µm", fs=FS_SMALL, ha="left")
    th = np.radians(165)
    callout(ax, ((R - 0.85) * np.cos(th), (R - 0.85) * np.sin(th)), (-2.6, 0.6), "p", ha="left")
    callout(ax, ((R + 0.85) * np.cos(np.radians(150)), (R + 0.85) * np.sin(np.radians(150))), (-10.9, 9.6), "n", ha="left")
    callout(ax, ((R - 2.1) * np.cos(np.radians(205)), (R - 2.1) * np.sin(np.radians(205))), (-2.6, -2.2), "p$^{++}$ contact", ha="left")
    callout(ax, ((R + 2.1) * np.cos(np.radians(-25)), (R + 2.1) * np.sin(np.radians(-25))), (9.0, -9.3), "n$^{++}$ contact", ha="center", va="top")
    label(ax, 0, -3.6, "junction on 80 %", fs=FS_SMALL); label(ax, 0, -4.7, "of the ring", fs=FS_SMALL)
    label(ax, -10.9, yb - 0.9, "bus", fs=FS_SMALL, ha="left")
    scalebar(ax, -4.0, -10.0, 5.0, "5 µm")
    panel(ax, "a", x=0.0, y=1.0)
    # (b)-(d) junction shapes in the rib, schematic
    shapes = (("lateral (Table 19.1)", "lat"), ("offset towards n", "off"), ("L-shaped", "L"))
    for k, (title, kind) in enumerate(shapes):
        bx = fig.add_axes([0.56, 0.69 - k * 0.32, 0.43, 0.26]); frameless(bx, (-1.05, 1.05), (-0.16, 0.36))
        box(bx, -1.05, -0.16, 2.1, 0.16, "ox", z=0); box(bx, -1.05, 0, 2.1, 0.36, "oxtop", z=0)
        xj = {"lat": 0.0, "off": 0.1, "L": 0.25}[kind]
        box(bx, -1.05, 0, 1.05 + xj, 0.09, "pdop", z=2); box(bx, xj, 0, 1.05 - xj, 0.09, "ndop", z=2)
        if kind in ("lat", "off"):
            box(bx, -0.25, 0.09, 0.25 + xj, 0.13, "pdop", z=2); box(bx, xj, 0.09, 0.25 - xj, 0.13, "ndop", z=2)
            bx.plot([xj, xj], [0, 0.22], color=INK, lw=1.4, zorder=4)
        else:
            box(bx, -0.25, 0.0, 0.5, 0.22, "pdop", z=2); box(bx, -0.05, 0.09, 0.3, 0.13, "ndop", z=3)
            box(bx, 0.25, 0.0, 0.8, 0.09, "ndop", z=3)
            bx.plot([-0.05, -0.05, 0.25, 0.25], [0.22, 0.09, 0.09, 0.0], color=INK, lw=1.4, zorder=4)
        box(bx, -0.25, 0, 0.5, 0.22, "none", ec=INK, lw=0.3, z=5)
        bx.text(-1.02, 0.34, title, fontsize=7, fontweight="bold", va="top", color=INK)
        if k == 0:
            label(bx, -0.65, 0.16, "p", fs=FS_SMALL); label(bx, 0.65, 0.16, "n", fs=FS_SMALL)
            scalebar(bx, 0.55, -0.13, 0.5, "500 nm", above=True)
        panel(bx, "bcd"[k], x=-0.03, y=1.0)
    fig.text(0.99, 0.015, "thick line: the junction; doping profiles schematic", ha="right", fontsize=6, color=MUTED, style="italic")
    save(fig, "ch20_ring")
    fsr = 1550 ** 2 / (3.89 * 2 * math.pi * R * 1e3)
    print(f"[20.3] R {R} um, FSR {fsr:.1f} nm, junction on {span:.0f} deg (80 %), circumference {2*math.pi*R:.1f} um")


# ------------------------------------------------------------------ Figure 20.4: GeSi electro-absorption modulator
def fig_eam():
    Lg, wg_ge, w = 40.0, 0.8, 0.5
    fig = plt.figure(figsize=(6.3, 2.6))
    ax = fig.add_axes([0.0, 0.0, 0.66, 1.0]); frameless(ax, (-4, 62), (-9.5, 9.5))
    box(ax, -4, -9.5, 66, 19, "oxtop", z=0)
    x0, x1 = 10.0, 10.0 + Lg
    wg_straight(ax, -4, x0 - 4, 0, w, "si"); wg_taper(ax, x0 - 4, x0, 0, w, wg_ge, "si")
    wg_taper(ax, x1, x1 + 4, 0, wg_ge, w, "si"); wg_straight(ax, x1 + 4, 62, 0, w, "si")
    box(ax, x0, 1.0, Lg, 4.5, "pp", z=1); box(ax, x0, -5.5, Lg, 4.5, "nn", z=1)
    box(ax, x0, -1.0, Lg, 2.0, "si", z=1)
    box(ax, x0, -wg_ge / 2, Lg, wg_ge, "ge", z=3)
    for xv in np.arange(x0 + 2, x1 - 1, 4.0):
        ax.add_patch(Circle((xv, 3.8), 0.45, fc=MAT["metal"], ec="none", zorder=4)); ax.add_patch(Circle((xv, -3.8), 0.45, fc=MAT["metal"], ec="none", zorder=4))
    box(ax, x0, 3.2, Lg, 1.2, "metal", z=3, alpha=0.5); box(ax, x0, -4.4, Lg, 1.2, "metal", z=3, alpha=0.5)
    label(ax, x0 + 12, 6.6, "p$^{++}$ Si and contact", fs=FS_SMALL); label(ax, x0 + 12, -6.6, "n$^{++}$ Si and contact", fs=FS_SMALL)
    callout(ax, (x0 + 6, 0.2), (x0 + 3, 8.4), "GeSi absorber", ha="center", va="bottom")
    arrow(ax, (-3.5, 1.4), (2.0, 1.4), col=OPT, lw=1.2, ms=7); label(ax, -3.5, 2.5, "light in", col=OPT, fs=FS_SMALL, ha="left")
    dim(ax, (x0, -8.2), (x1, -8.2), f"{Lg:.0f} µm", bg="white")
    ax.plot([x0 + 30, x0 + 30], [-6.2, 6.2], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=6)
    ax.text(x0 + 30.4, 6.3, "B", fontsize=7, fontweight="bold"); ax.text(x0 + 30.4, -6.3, "B′", fontsize=7, fontweight="bold", va="top")
    note(ax, "to scale; dimensions illustrative", loc="upper right")
    panel(ax, "a", x=0.0, y=1.0)
    # (b) cross-section B-B'
    bx = fig.add_axes([0.69, 0.08, 0.30, 0.86]); frameless(bx, (-3.0, 3.0), (-0.9, 2.0))
    box(bx, -3, -0.9, 6, 0.9, "ox", z=0); box(bx, -3, 0, 6, 2.0, "oxtop", z=0)
    box(bx, -3, 0, 2.6, 0.22, "pp", z=2); box(bx, 0.4, 0, 2.6, 0.22, "nn", z=2); box(bx, -0.4, 0, 0.8, 0.06, "si", z=2)
    box(bx, -0.4, 0.06, 0.8, 0.45, "ge", z=3)
    for xc in (-1.9, 1.9):
        box(bx, xc - 0.2, 0.22, 0.4, 1.4, "metal", z=3)
    arrow(bx, (-0.35, 0.3), (0.35, 0.3), col=RED, lw=1.0, ms=5, z=6)
    label(bx, 0, 0.75, "field", col=RED, fs=FS_SMALL)
    label(bx, -1.2, -0.35, "p$^{++}$", fs=FS_SMALL); label(bx, 1.2, -0.35, "n$^{++}$", fs=FS_SMALL)
    callout(bx, (0.3, 0.45), (1.0, 1.25), "GeSi", ha="left")
    scalebar(bx, -2.8, -0.75, 1.0, "1 µm")
    panel(bx, "b", x=0.0, y=1.0)
    save(fig, "ch20_eam")
    print(f"[20.4] EAM drawn {Lg:.0f} um long, absorber {wg_ge} um wide (illustrative)")


# ------------------------------------------------------------------ Figure 20.5: modulation formats
def fig_formats():
    fig = plt.figure(figsize=(6.3, 3.9))
    T = len(BITS) * UI
    # (a) NRZ
    a = fig.add_axes([0.08, 0.60, 0.53, 0.33])
    t, y = smooth_wave(BITS, UI, rise_ps=6)
    a.plot(t, y, color=C1)
    for k, b in enumerate(BITS):
        a.text((k + 0.5) * UI, 1.12, str(b), ha="center", va="bottom", fontsize=6.5, color=MUTED)
    a.set_xlim(0, T); a.set_ylim(-0.1, 1.3); a.set_yticks([0, 1]); a.set_xticks(np.arange(0, T + 1, 80)); a.set_xticklabels([])
    finish(a, None, "NRZ level")
    a.text(0.04, 1.02, "50 GBd, 1 bit per symbol", transform=a.transAxes, ha="left", va="bottom", fontsize=6.8, color=INK)
    tag(a, "a")
    # (b) PAM4, Gray code
    gray = {(0, 0): 0, (0, 1): 1, (1, 1): 2, (1, 0): 3}
    syms = [gray[(BITS[2 * k], BITS[2 * k + 1])] for k in range(len(BITS) // 2)]
    b = fig.add_axes([0.08, 0.15, 0.53, 0.36])
    t, y = smooth_wave(np.array(syms) / 3, 2 * UI, rise_ps=10)
    b.plot(t, y, color=C3)
    for k, s in enumerate(syms):
        b.text((k + 0.5) * 2 * UI, 1.12, f"{BITS[2*k]}{BITS[2*k+1]}", ha="center", va="bottom", fontsize=6.5, color=MUTED)
    for lv in (0, 1 / 3, 2 / 3, 1):
        b.axhline(lv, color=MUTED, lw=0.5, ls=":")
    b.set_xlim(0, T); b.set_ylim(-0.1, 1.3); b.set_yticks([0, 1 / 3, 2 / 3, 1]); b.set_yticklabels(["0", "1/3", "2/3", "1"])
    b.set_xticks(np.arange(0, T + 1, 80))
    finish(b, "Time (ps), 50 Gb/s", "PAM4 level")
    b.text(0.04, 1.02, "25 GBd, 2 bits per symbol (Gray code)", transform=b.transAxes, ha="left", va="bottom", fontsize=6.8, color=INK)
    tag(b, "b")
    # (c) IQ modulator, schematic
    c = fig.add_axes([0.66, 0.57, 0.34, 0.40]); frameless(c, (0, 10), (-3.4, 3.6), equal=False)
    for s, lab in ((1, "I"), (-1, "Q")):
        y0 = 1.6 * s
        c.plot([0.3, 1.2], [0, 0], color=OPT, lw=1.3); c.plot([1.2, 2.0], [0, y0], color=OPT, lw=1.3)
        c.plot([2.0, 2.6], [y0, y0], color=OPT, lw=1.3)
        c.plot([2.6, 3.1, 6.1, 6.6], [y0, y0 + 0.55, y0 + 0.55, y0], color=OPT, lw=1.0)
        c.plot([2.6, 3.1, 6.1, 6.6], [y0, y0 - 0.55, y0 - 0.55, y0], color=OPT, lw=1.0)
        c.add_patch(Rectangle((3.6, y0 + 0.3), 2.0, 0.5, fc="none", ec=ELEC, lw=0.8, zorder=3))
        c.add_patch(Rectangle((3.6, y0 - 0.8), 2.0, 0.5, fc="none", ec=ELEC, lw=0.8, zorder=3))
        c.text(4.6, y0, f"MZM {lab}, at null", ha="center", va="center", fontsize=6.1, color=INK)
        c.plot([6.6, 7.6], [y0, y0], color=OPT, lw=1.3)
        c.plot([7.6, 8.4], [y0, 0], color=OPT, lw=1.3)
    c.add_patch(Rectangle((6.85, -1.85), 0.55, 0.5, fc=MAT["tin"], ec="none", zorder=3))
    c.text(7.15, -2.35, "90°", ha="center", va="top", fontsize=6.6, color=INK)
    c.plot([8.4, 9.8], [0, 0], color=OPT, lw=1.3)
    c.text(0.3, 0.3, "laser", fontsize=6.6, color=OPT); c.text(9.8, 0.3, "out", fontsize=6.6, color=OPT, ha="right")
    note(c, "schematic", loc="lower right")
    panel(c, "c", x=-0.02, y=1.02)
    # (d) constellations
    d = fig.add_axes([0.73, 0.10, 0.24, 0.38])
    q = np.array([-3, -1, 1, 3]) / 3
    for xi in q:
        d.plot(q, [xi] * 4, "o", color=GRID, ms=3.5, mec=MUTED, mew=0.4)
    for (i, qq), lab in (((1, 1), "00"), ((-1, 1), "01"), ((-1, -1), "11"), ((1, -1), "10")):
        d.plot(i * 0.707, qq * 0.707, "o", color=C4, ms=6)
        d.text(i * 0.707, qq * 0.707 + 0.17 * (1 if qq > 0 else -1), lab, ha="center", va="bottom" if qq > 0 else "top", fontsize=6.4, color=C4)
    d.axhline(0, color=INK, lw=0.6); d.axvline(0, color=INK, lw=0.6)
    d.set_xlim(-1.35, 1.35); d.set_ylim(-1.35, 1.35); d.set_aspect("equal")
    d.set_xticks([]); d.set_yticks([]); d.grid(False)
    for sp in d.spines.values(): sp.set_visible(False)
    d.text(1.33, 0.06, "I", fontsize=7.5, ha="right", va="bottom"); d.text(0.06, 1.33, "Q", fontsize=7.5, ha="left", va="top")
    d.text(0, -1.55, "QPSK (red), 16-QAM (grey)", ha="center", va="top", fontsize=6.6, color=INK)
    tag(d, "d")
    save(fig, "ch20_formats")
    print(f"[20.5] PAM4 eye height 1/3 of NRZ: power penalty 10 log10(3) = {10*math.log10(3):.2f} dB; symbols {syms}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["metrics", "mzm", "ring", "eam", "formats"]
    for w in which:
        globals()["fig_" + w]()
