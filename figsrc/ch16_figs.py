"""Figures for Chapter 16 (edge couplers and spot-size converters).

Run from the repository root:   python -I -X utf8 figsrc/ch16_figs.py [name ...]
Writes assets/figs/ch16_*.svg and prints every number the figures and captions use.

Mode sizes and overlaps come from the femwell sweep of figsrc/ch16_taper.py (ch16_taper.json, Table 16.1); the mode
maps of Figure 16.3 from figsrc/ch16_fields.py (ch16_fields.json, run in the femwell container). Gaussian butt coupling
and the angled-facet suppression use the chapter's formulas (Section 16.1, Worked Example 16.2).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: E402,F401
from geomstyle import *     # noqa: E402,F401

HERE = os.path.dirname(os.path.abspath(__file__))
LAM, N_OX, T_SI, BOX = 1.55, 1.444, 0.22, 2.0
FIBRES = [("lensed 2.5 um", "lensed fibre, 2.5 µm", 2.5, C4), ("UHNA 4 um", "UHNA fibre, 4 µm", 4.0, C2),
          ("SMF-28 10.4 um", "SMF-28, 10.4 µm", 10.4, C1)]


def sweep(pol="TE"):
    """Reliable rows of the femwell sweep (window large enough: < 3 % of the power near its edge)."""
    d = json.load(open(os.path.join(HERE, "ch16_taper.json")))
    rows = sorted([o for o in d if o["pol"] == pol and o["edge"] < 0.03], key=lambda o: o["width"])
    return rows


def interp_log(rows, key, w):
    W = np.array([r["width"] for r in rows]); V = np.log(np.array([r[key] for r in rows]))
    return np.exp(np.interp(w, W, V))


def butt(mc, mf):
    r = mc / mf
    return (2 * r / (1 + r * r)) ** 2


# =====================================================================================================
# Figure 16.1: the size mismatch, to scale, and Gaussian butt coupling against mode size
# =====================================================================================================
def fig_butt():
    rows = sweep("TE")
    s500 = [r for r in rows if abs(r["width"] - 0.5) < 1e-6][0]
    fig = plt.figure(figsize=(6.3, 2.55))
    a1 = fig.add_axes([0.0, 0.02, 0.36, 0.96]); frameless(a1, (-7.2, 7.2), (-7.0, 7.4))
    a1.add_patch(Circle((0, 0), 4.1, fc=MAT["core"], ec="none", alpha=0.55, zorder=1))
    for (k, lab, mfd, col) in FIBRES:
        a1.add_patch(Circle((0, 0), mfd / 2, fc="none", ec=col, lw=1.1, ls=(0, (3, 1.6)), zorder=3))
    box(a1, -0.25, -0.11, 0.5, 0.22, "si", z=4, ec=INK, lw=0.3)
    a1.add_patch(Ellipse((0, 0), s500["mfd_x"], s500["mfd_y"], fc=AMBER, ec="none", alpha=0.75, zorder=5))
    callout(a1, (3.68, 3.68), (4.3, 6.4), "SMF-28 mode 10.4 µm", col=C1, ha="center")
    callout(a1, (-2.9, -2.9), (-4.4, -5.3), "SMF-28 core 8.2 µm", ha="center")
    callout(a1, (1.414, -1.414), (4.4, -3.6), "UHNA 4 µm", col=C2, ha="center")
    callout(a1, (-0.884, 0.884), (-4.4, 4.4), "lensed 2.5 µm", col=C4, ha="center")
    callout(a1, (0.15, 0.12), (3.2, 2.0), f"Si strip 500 × 220 nm,\nmode {s500['mfd_x']:.1f} µm", ha="left")
    scalebar(a1, 4.6, -6.9, 2.0, "2 µm")
    panel(a1, "a", 0.0, 1.0)
    # butt coupling against mode size
    a2 = fig.add_axes([0.47, 0.17, 0.51, 0.75])
    mc = np.logspace(np.log10(0.25), np.log10(25), 400)
    for (k, lab, mfd, col) in FIBRES:
        a2.plot(mc, 10 * np.log10(butt(mc, mfd)), color=col, lw=1.6, label=lab)
        m = np.array([math.sqrt(r["mfd_x"] * r["mfd_y"]) for r in rows])
        e = np.array([r["overlap"][k] for r in rows])
        a2.plot(m, 10 * np.log10(e), "o", ms=3.2, color=col, mfc="white", mew=1.0, zorder=5)
    a2.plot([], [], "o", ms=3.2, color=MUTED, mfc="white", mew=1.0, label="femwell, Si tips (Table 16.1)")
    a2.set_xscale("log")
    a2.set_xlim(0.25, 25); a2.set_ylim(-25, 0.5)
    a2.set_xticks([0.3, 1, 3, 10]); a2.set_xticklabels(["0.3", "1", "3", "10"])
    a2.set_yticks([-25, -20, -15, -10, -5, 0])
    m5 = math.sqrt(s500["mfd_x"] * s500["mfd_y"])
    a2.axvline(m5, color=MUTED, lw=0.7, ls=(0, (2, 2)))
    a2.text(m5 * 1.08, -24.3, "500 nm strip", fontsize=6.5, color=MUTED, ha="left", va="bottom")
    a2.legend(loc="lower right", fontsize=6.3, handlelength=1.5, bbox_to_anchor=(1.0, 0.0))
    finish(a2, "chip mode size, MFD (µm)", "coupling (dB)")
    tag(a2, "b")
    save(fig, "ch16_butt")
    g = {k: butt(m5, mfd) for (k, lab, mfd, col) in FIBRES}
    print(f"Fig 16.1: 500 nm strip MFD {s500['mfd_x']:.2f} x {s500['mfd_y']:.2f} um; Gaussian estimate to SMF {10*math.log10(g['SMF-28 10.4 um']):.1f} dB, "
          f"lensed {10*math.log10(g['lensed 2.5 um']):.1f} dB; femwell SMF {100*s500['overlap']['SMF-28 10.4 um']:.2f} % "
          f"({10*math.log10(s500['overlap']['SMF-28 10.4 um']):.1f} dB), lensed {100*s500['overlap']['lensed 2.5 um']:.1f} % "
          f"({10*math.log10(s500['overlap']['lensed 2.5 um']):.1f} dB)")
    best = max(rows, key=lambda r: r["overlap"]["lensed 2.5 um"])
    print(f"   best femwell overlap with the lensed fibre {100*best['overlap']['lensed 2.5 um']:.0f} % at {1000*best['width']:.0f} nm; "
          f"Gaussian formula at that size {100*butt(math.sqrt(best['mfd_x']*best['mfd_y']), 2.5):.0f} %")


# =====================================================================================================
# Figure 16.2: an inverse taper in top and side view with the local mode size (adiabatic)
# =====================================================================================================
def fig_taper():
    rows = sweep("TE")
    L, W0, W1, Z0 = 200.0, 0.50, 0.16, -30.0
    z = np.linspace(Z0, L, 461)
    w = np.where(z < 0, W0, W0 + (W1 - W0) * np.clip(z, 0, L) / L)
    mx, my = interp_log(rows, "mfd_x", w), interp_log(rows, "mfd_y", w)
    tip = [r for r in rows if abs(r["width"] - W1) < 1e-6][0]
    fig = plt.figure(figsize=(6.3, 3.4))
    a1 = fig.add_axes([0.085, 0.585, 0.89, 0.38]); a2 = fig.add_axes([0.085, 0.12, 0.89, 0.38])
    ZF = L + 32
    for ax in (a1, a2):
        ax.set_xlim(Z0, ZF); ax.grid(False)
        ax.axvline(L, color=INK, lw=0.8)
    # (a) top view
    a1.axhspan(-6.5, 6.5, xmax=(L - Z0) / (ZF - Z0), color=MAT["ox"], lw=0, zorder=0)
    a1.axhspan(-6.5, 6.5, xmin=(L - Z0) / (ZF - Z0), color=MAT["glass"], lw=0, zorder=0)
    a1.fill_between(z, -mx / 2, mx / 2, color=AMBER, alpha=0.35, lw=0, zorder=2)
    a1.fill_between(z, -w / 2, w / 2, color=MAT["si"], lw=0, zorder=3)
    a1.plot(z, w / 2, color="#5F7896", lw=0.6, zorder=3); a1.plot(z, -w / 2, color="#5F7896", lw=0.6, zorder=3)
    a1.fill_between([L, ZF], -2.0, 2.0, color=C1, alpha=0.18, lw=0, zorder=2)
    a1.text(L + 3, 2.6, "UHNA fibre,\nmode 4 µm", fontsize=6.5, color=C1, va="bottom")
    a1.text(L - 3, 4.8, "facet", fontsize=6.5, ha="right", va="top")
    a1.text(-26, 1.0, "500 nm Si strip", fontsize=6.5, va="bottom")
    a1.annotate(f"{1000 * W1:.0f} nm tip: mode {tip['mfd_x']:.1f} µm wide", xy=(L - 1, tip["mfd_x"] / 2), xytext=(118, 3.9), fontsize=6.5,
                ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a1.annotate("linear taper, 500 → 160 nm over 200 µm", xy=(100, 0.0), xytext=(60, -3.7), fontsize=6.5, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a1.set_ylim(-5.05, 5.05); a1.set_yticks([-4, -2, 0, 2, 4])
    a1.set_ylabel("x (µm)"); a1.tick_params(labelbottom=False)
    a1.text(1.0, 1.02, "top view", transform=a1.transAxes, ha="right", va="bottom", fontsize=6.5, color=MUTED, style="italic")
    tag(a1, "a")
    # (b) side view with the 2 um BOX and the substrate
    yb = -T_SI / 2 - BOX
    a2.axhspan(yb, 4.5, xmax=(L - Z0) / (ZF - Z0), color=MAT["ox"], lw=0, zorder=0)
    a2.axhspan(-6.5, 4.5, xmin=(L - Z0) / (ZF - Z0), color=MAT["glass"], lw=0, zorder=0)
    a2.axhspan(-6.5, yb, xmax=(L - Z0) / (ZF - Z0), color=MAT["sub"], lw=0, zorder=0)
    a2.fill_between(z, -my / 2, my / 2, color=AMBER, alpha=0.35, lw=0, zorder=2)
    leak = np.where(-my / 2 < yb, -my / 2, yb)
    a2.fill_between(z, leak, yb, where=(-my / 2 < yb), color=RED, alpha=0.55, lw=0, zorder=3)
    a2.fill_between(z, -T_SI / 2, T_SI / 2, color=MAT["si"], lw=0, zorder=3)
    a2.fill_between([L, ZF], -2.0, 2.0, color=C1, alpha=0.18, lw=0, zorder=2)
    a2.text(-26, yb - 0.3, "Si substrate", fontsize=6.5, va="top")
    a2.text(-26, -1.25, "BOX 2 µm", fontsize=6.5, va="center")
    a2.text(-26, 0.35, "220 nm Si", fontsize=6.5, va="bottom")
    zl = z[np.argmax(-my / 2 < yb)]
    a2.annotate(f"mode reaches the substrate:\n{100 * tip['below2um']:.1f} % of the power below 2 µm", xy=(L - 3, yb - 0.15),
                xytext=(130, -4.4), fontsize=6.5, ha="center", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a2.set_ylim(-5.6, 4.5); a2.set_yticks([-4, -2, 0, 2, 4])
    a2.set_ylabel("y (µm)"); a2.set_xlabel("position along the coupler z (µm)")
    a2.text(1.0, 1.02, "side view", transform=a2.transAxes, ha="right", va="bottom", fontsize=6.5, color=MUTED, style="italic")
    tag(a2, "b")
    fig.canvas.draw()
    for ax in (a1, a2):
        sx = (ax.transData.transform((0, 1))[1] - ax.transData.transform((0, 0))[1]) / (ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0])
        ax.text(0.005, 0.02, f"transverse scale × {sx:.0f}", transform=ax.transAxes, fontsize=6.0, color=MUTED, style="italic", ha="left", va="bottom")
        print(f"   transverse axis stretched x {sx:.2f} relative to z")
    save(fig, "ch16_taper")
    i1 = np.argmax(mx > 1.0)
    print(f"Fig 16.2: tip {1000*W1:.0f} nm: MFD {tip['mfd_x']:.2f} x {tip['mfd_y']:.2f} um, below 2 um {100*tip['below2um']:.1f} %; "
          f"mode exceeds 1 um at z = {z[i1]:.0f} um (w = {1000*w[i1]:.0f} nm); envelope crosses the BOX bottom at z = {zl:.0f} um")


# =====================================================================================================
# Figure 16.6: an angled facet (Worked Example 16.2)
# =====================================================================================================
def fig_angled():
    TH = 8.0
    R0 = ((N_OX - 1) / (N_OX + 1)) ** 2
    th_air = math.degrees(math.asin(N_OX * math.sin(math.radians(TH))))
    fig = plt.figure(figsize=(6.3, 2.6))
    a1 = fig.add_axes([0.0, 0.02, 0.53, 0.96]); frameless(a1, (-26, 21), (-12.5, 14.5))
    a1.add_patch(Rectangle((-26, -12.5), 26, 27, fc=MAT["ox"], ec="none", zorder=0))
    a1.plot([0, 0], [-12.5, 14.5], color=INK, lw=1.0, zorder=3)
    w = 1.5                                    # 1/e2 radius of a 3 um spot
    t = math.radians(TH); ta = math.radians(th_air)
    d_in = np.array([math.cos(t), -math.sin(t)])          # towards the facet
    d_ref = np.array([-math.cos(t), -math.sin(t)])         # reflected
    d_out = np.array([math.cos(ta), -math.sin(ta)])        # in air
    P = np.array([0.0, 2.0])

    def band(d, start, length, hw, col, alpha, z=2, ls=None):
        n = np.array([-d[1], d[0]])
        p0, p1 = start, start + d * length
        poly(a1, [p0 + n * hw, p1 + n * hw, p1 - n * hw, p0 - n * hw], col, alpha=alpha, z=z)
    band(d_in, P - d_in * 26.5, 26.5, w, AMBER, 0.45)
    band(d_ref, P, 26.5, w, AMBER, 0.22)
    band(d_out, P, 21, w, AMBER, 0.45)
    # silicon tip along the waveguide axis
    tip0 = P - d_in * 26.5; tip1 = P - d_in * 6
    a1.plot([tip0[0], tip1[0]], [tip0[1], tip1[1]], color="#5F7896", lw=1.6, zorder=3, solid_capstyle="butt")
    arrow(a1, tuple(P - d_in * 16), tuple(P - d_in * 10), col=INK, lw=1.0, ms=7)
    arrow(a1, tuple(P + d_ref * 15), tuple(P + d_ref * 21), col=INK, lw=0.9, ms=7, ls=(0, (3, 2)))
    arrow(a1, tuple(P + d_out * 10), tuple(P + d_out * 16), col=INK, lw=1.0, ms=7)
    # normal and angle arcs
    a1.plot([-25, 20], [P[1], P[1]], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=4)

    def arc(r, a0, a1_, txt, tx, ty):
        aa = np.radians(np.linspace(a0, a1_, 40))
        a1.plot(P[0] + r * np.cos(aa), P[1] + r * np.sin(aa), color=INK, lw=0.8, zorder=5)
        label(a1, tx, ty, txt, fs=FS_SMALL, bg="white")
    arc(11, 180, 180 - TH, f"{TH:.0f}°", -13.6, P[1] + 0.95)
    arc(18, 180 - TH, 180 + TH, f"{2 * TH:.0f}°", -19.6, P[1] - 0.3)
    arc(9, -th_air, 0, f"{th_air:.1f}°", 10.9, P[1] - 1.0)
    label(a1, -23.5, 13.4, "chip (oxide cladding)", fs=FS_SMALL, ha="left")
    label(a1, 1.0, 13.4, "air", fs=FS_SMALL, ha="left", col=MUTED)
    label(a1, -14, 7.2, "waveguide, 3 µm spot", fs=FS_SMALL)
    label(a1, -14, -8.6, f"reflected {100 * R0:.1f} %,\nmisses the mode", fs=FS_SMALL)
    label(a1, 13.5, -6.8, "to the fibre", fs=FS_SMALL)
    note(a1, "angles to scale", "lower right")
    panel(a1, "a", 0.0, 1.0)
    # return loss against tilt
    a2 = fig.add_axes([0.625, 0.17, 0.365, 0.75])
    th = np.linspace(0, 12, 241)
    for spot, col in ((2.0, C4), (3.0, C2), (5.0, C1)):
        sup = np.exp(-(np.pi * N_OX * (spot / 2) * np.radians(2 * th) / LAM) ** 2)
        a2.plot(th, 10 * np.log10(R0 * sup), color=col, lw=1.6, label=f"{spot:.0f} µm spot")
    s8 = math.exp(-(math.pi * N_OX * 1.5 * math.radians(2 * TH) / LAM) ** 2)
    tot = 10 * math.log10(R0 * s8)
    a2.plot([TH], [tot], "o", ms=5, color=C2, zorder=5)
    a2.annotate(f"{TH:.0f}°, 3 µm: {tot:.1f} dB".replace("-", "−"), xy=(TH, tot), xytext=(9.0, -7.5), fontsize=6.8, color=INK,
                ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=3))
    a2.set_xlim(0, 12); a2.set_ylim(-60, 0)
    a2.text(0.3, 10 * math.log10(R0) + 1.2, f"flat oxide–air facet: {10 * math.log10(R0):.1f} dB".replace("-", "−"), fontsize=6.5, color=INK, va="bottom")
    a2.legend(loc="lower left", fontsize=6.6)
    finish(a2, "waveguide tilt at the facet (°)", "reflection back into the mode (dB)")
    tag(a2, "b")
    save(fig, "ch16_angled")
    print(f"Fig 16.6: R = {100 * R0:.2f} % ({10 * math.log10(R0):.1f} dB); air angle {th_air:.2f} deg; 3 um spot at 8 deg: "
          f"extra {-10 * math.log10(s8):.2f} dB, total {tot:.2f} dB")


# =====================================================================================================
# Figure 16.5: making the facet: dicing and polishing, or a deep-etched trench
# =====================================================================================================
def _stack(ax, x0, x1, ytop, ex):
    """Chip layers seen from the side between x0 and x1; top surface at ytop; thin layers drawn ex times thicker."""
    t_clad, t_si, t_box = 2.0 * ex, T_SI * ex, BOX * ex
    y_si = ytop - t_clad
    box(ax, x0, -200, x1 - x0, 200 + y_si - t_box, "sub")
    box(ax, x0, y_si - t_box, x1 - x0, t_box, "ox")
    box(ax, x0, y_si, x1 - x0, t_clad, "oxtop")
    box(ax, x0, y_si, x1 - x0, t_si, "si", z=3)
    return y_si + t_si / 2


def _fibre(ax, xl, yc, length, lensed=False, z=2):
    """A fibre (125 um cladding, 8.2 um core) lying along x with its end face at xl."""
    if lensed:
        # conical tip ending in a small lens (schematic shape, fibre diameter to scale)
        a = np.linspace(np.pi / 2, -np.pi / 2, 40)
        rn = 9.0
        nose = [(xl + rn * (1 - math.cos(t)), yc + rn * math.sin(t)) for t in a]
        pts = [(xl + 75, yc + 62.5)] + nose + [(xl + 75, yc - 62.5), (xl + length, yc - 62.5), (xl + length, yc + 62.5)]
        poly(ax, pts, "glass", z=z, ec=MUTED, lw=0.5)
        poly(ax, [(xl + 1.5, yc + 3.0), (xl + 75, yc + 4.1), (xl + length, yc + 4.1), (xl + length, yc - 4.1), (xl + 75, yc - 4.1),
                  (xl + 1.5, yc - 3.0)], "core", z=z + 1)
    else:
        box(ax, xl, yc - 62.5, length, 125, "glass", z=z, ec=MUTED, lw=0.5)
        box(ax, xl, yc - 4.1, length, 8.2, "core", z=z + 1)


def fig_facets():
    EX = 4.0
    fig = plt.figure(figsize=(6.3, 2.35))
    a1 = fig.add_axes([0.0, 0.0, 0.44, 1.0]); frameless(a1, (-170, 150), (-150, 92))
    a2 = fig.add_axes([0.46, 0.0, 0.54, 1.0]); frameless(a2, (-170, 230), (-150, 92))
    # (a) diced and polished chip, fibre butted with index-matching gel
    yc = _stack(a1, -170, 0, 30, EX)
    a1.plot([0, 0], [-150, 30], color=INK, lw=1.0, zorder=4)
    box(a1, 0, yc - 30, 6, 60, "epoxy", z=1)
    _fibre(a1, 6, yc, 150)
    label(a1, -165, 42, "chip", fs=FS_SMALL, ha="left")
    label(a1, -85, -60, "Si substrate", fs=FS_SMALL)
    callout(a1, (0, -40), (-60, -120), "diced, then polished\nto an optical finish", ha="center")
    callout(a1, (3, yc - 25), (35, -110), "index-matching gel", ha="left")
    label(a1, 80, 72, "fibre (125 µm)", fs=FS_SMALL)
    panel(a1, "a", 0.0, 1.0)
    # (b) deep-etched trench: facet defined by lithography, fibre lowered into the trench, dicing later
    TW = 200.0
    yc2 = _stack(a2, -170, 0, 30, EX)
    _stack(a2, TW, 230, 30, EX)
    yfl = yc2 - 95.0                                  # trench floor, deeper than the fibre radius below the waveguide
    box(a2, 0, -200, TW, 200 + yfl, "sub")
    a2.plot([0, 0, TW, TW], [30, yfl, yfl, 30], color=INK, lw=0.8, zorder=5)
    _fibre(a2, 6, yc2, TW - 20, lensed=True, z=5)
    xd = TW - 40
    a2.plot([xd, xd], [-150, 92], color=RED, lw=0.9, ls=(0, (4, 2)), zorder=7)
    label(a2, xd + 4, 88, "dice here,\nafter testing", fs=FS_SMALL, ha="left", va="top", col=RED)
    callout(a2, (0, yc2), (-85, 62), "facet etched through\noxide and BOX", ha="center")
    label(a2, 122, 50, "lensed fibre lowered\ninto the trench", fs=FS_SMALL)
    dim(a2, (-12, yc2), (-12, yfl), "", fs=FS_SMALL)
    label(a2, -18, (yc2 + yfl) / 2 - 8, "trench floor\nmore than\n62.5 µm below\nthe waveguide", fs=FS_SMALL, ha="right")
    label(a2, 92, (yfl - 150) / 2 - 8, "Si substrate", fs=FS_SMALL)
    panel(a2, "b", 0.0, 1.0)
    note(a2, f"layer thicknesses × {EX:.0f}; fibres to scale", "lower right")
    save(fig, "ch16_facets")
    print(f"Fig 16.5: fibre radius 62.5 um sets the trench depth below the waveguide (drawn {yc2 - yfl:.0f} um); layers drawn x {EX}")


# =====================================================================================================
# Figure 16.4: multi-stage, overlay, suspended and SWG couplers (schematic side and top views)
# =====================================================================================================
def _smooth(z, z0, z1, a, b):
    t = np.clip((z - z0) / (z1 - z0), 0, 1)
    return a + (b - a) * t * t * (3 - 2 * t)


def _envelope(ax, z, yc, hw):
    ax.fill_between(z, yc - hw, yc + hw, color=AMBER, alpha=0.38, lw=0, zorder=3)


def fig_multistage():
    fig = plt.figure(figsize=(6.3, 4.3))
    H = 0.235
    axs = [fig.add_axes([0.0, 1 - (i + 1) * H - i * 0.015, 1.0, H]) for i in range(4)]
    for ax in axs:
        frameless(ax, (-3, 122), (-7.2, 6.6), equal=False)
    z = np.linspace(0, 100, 161)
    FAC = 100

    def facet(ax, y0=-7.2, y1=5.5):
        ax.plot([FAC, FAC], [y0, y1], color=INK, lw=0.9, zorder=7)
        arrow(ax, (FAC + 3, 0.8), (FAC + 14, 0.8), col=AMBER, lw=1.6, ms=9)
        label(ax, FAC + 8.5, 2.6, "to the fibre", fs=FS_SMALL)

    # (a) polymer or oxynitride overlay
    ax = axs[0]
    box(ax, 0, -7.2, FAC, 2.2, "sub"); box(ax, 0, -5, FAC, 5, "ox")
    box(ax, 0, 0, 25, 2.0, "oxtop")
    box(ax, 25, 0, FAC - 25, 3.6, "polymer", z=2)
    box(ax, 0, 0, 62, 0.4, "si", z=4)
    _envelope(ax, z, _smooth(z, 30, 62, 0.2, 1.8), _smooth(z, 30, 62, 0.5, 1.35))
    facet(ax)
    panel(ax, "a", 0.0, 1.0); label(ax, 3.5, 5.75, "polymer or oxynitride overlay", fs=FS, ha="left", va="center")
    callout(ax, (50, 0.2), (44, -2.6), "Si inverse taper (tip)", ha="center")
    label(ax, 82, 4.4, "overlay waveguide, a few µm", fs=FS_SMALL, ha="center")
    label(ax, 6, -2.6, "BOX", fs=FS_SMALL, ha="left")
    # (b) silicon to silicon nitride, then a SiN inverse taper
    ax = axs[1]
    box(ax, 0, -7.2, FAC, 2.2, "sub"); box(ax, 0, -5, FAC, 5, "ox"); box(ax, 0, 0, FAC, 4.9, "oxtop")   # thick enough to hold the SiN spot
    box(ax, 0, 0, 50, 0.4, "si", z=4)
    box(ax, 20, 1.4, FAC - 20, 0.6, "sin", z=4)
    _envelope(ax, z, _smooth(z, 22, 50, 0.2, 1.7), np.maximum(_smooth(z, 22, 50, 0.5, 0.85), _smooth(z, 66, FAC, 0.85, 3.1)))
    facet(ax)
    panel(ax, "b", 0.0, 1.0); label(ax, 3.5, 5.75, "two stages: Si, then SiN", fs=FS, ha="left", va="center")
    callout(ax, (40, 0.2), (36, -2.6), "Si taper hands over", ha="center")
    callout(ax, (30, 1.95), (16, 3.6), "SiN waveguide", ha="center")
    label(ax, 76, -3.3, "SiN inverse taper: wider tip,\nlarger spot", fs=FS_SMALL, ha="center")
    # (c) suspended: substrate removed under the taper
    ax = axs[2]
    box(ax, 0, -7.2, 35, 2.2, "sub"); box(ax, 35, -7.2, FAC - 35, 0.7, "sub")
    box(ax, 0, -5, FAC, 5, "ox"); box(ax, 0, 0, FAC, 4.4, "oxtop")
    box(ax, 0, 0, 82, 0.4, "si", z=4)
    _envelope(ax, z, 0.2 + 0 * z, _smooth(z, 45, 82, 0.5, 3.4))
    facet(ax)
    panel(ax, "c", 0.0, 1.0); label(ax, 3.5, 5.75, "suspended", fs=FS, ha="left", va="center")
    label(ax, 67, -5.8, "substrate etched away: air below the oxide", fs=FS_SMALL, ha="center", va="center")
    callout(ax, (25, 0.2), (18, -2.6), "Si inverse taper", ha="center")
    # (d) SWG taper, top view
    ax = axs[3]
    box(ax, 0, -5.0, FAC, 10.2, "ox")
    box(ax, 0, -0.45, 22, 0.9, "si", z=4)
    P = 3.2
    for z0 in np.arange(22, 92, P):
        w = float(_smooth(np.array([z0]), 22, 92, 0.9, 0.35)[0])
        box(ax, z0, -w / 2 * 1.6, P * 0.5, w * 1.6, "si", z=4)
    _envelope(ax, z, 0 * z, np.maximum(0.7, _smooth(z, 30, 95, 0.7, 3.4)))
    facet(ax, -5.0, 5.2)
    panel(ax, "d", 0.0, 1.0); label(ax, 3.5, 5.75, "subwavelength-grating taper (top view)", fs=FS, ha="left", va="center")
    label(ax, 57, -3.6, "segments shorter than the wavelength: a graded, lower index", fs=FS_SMALL, ha="center")
    note(axs[3], "schematic, not to scale", "lower right")
    save(fig, "ch16_multistage")
    print("Fig 16.4: schematic (no numbers)")


# =====================================================================================================
# Figure 16.3: femwell intensity maps of the tip mode, to scale (ch16_fields.json)
# =====================================================================================================
def fig_modes():
    d = json.load(open(os.path.join(HERE, "ch16_fields.json")))
    g, fg = d["grid"], d["fine"]
    X0, X1, Y0, Y1 = g["x"][0], g["x"][1], g["y"][0], g["y"][1]
    order = [(0.50, "TE"), (0.20, "TE"), (0.18, "TE"), (0.16, "TE"), (0.14, "TE"), (0.14, "TM")]
    match = {(0.50, "TE"): ("lensed", 2.5, C4), (0.20, "TE"): ("lensed", 2.5, C4), (0.18, "TE"): ("lensed", 2.5, C4),
             (0.16, "TE"): ("UHNA", 4.0, C2), (0.14, "TE"): ("SMF-28", 10.4, C1), (0.14, "TM"): ("lensed", 2.5, C4)}
    table = {(round(o["width"], 3), o["pol"]): o for o in json.load(open(os.path.join(HERE, "ch16_taper.json")))}
    modes = {(round(m["width"], 3), m["pol"]): m for m in d["modes"]}
    fig = plt.figure(figsize=(6.3, 3.46))
    W, H = 0.30, 0.486
    DBMIN = -30.0
    for k, key in enumerate(order):
        r, c = divmod(k, 3)
        ax = fig.add_axes([0.005 + c * (W + 0.012), 0.514 - r * 0.514, W, H])
        frameless(ax, (X0, X1), (Y0, Y1))
        m = modes[key]
        A = 0.4 * np.array(m["map"], float).reshape(g["ny"], g["nx"])          # intensity in dB re. the peak
        im = ax.imshow(A, extent=(X0, X1, Y0, Y1), origin="lower", cmap=FIELD_CMAP, vmin=DBMIN, vmax=0, interpolation="bilinear", zorder=1)
        if "fine" in m:
            F = 0.4 * np.array(m["fine"], float).reshape(fg["ny"], fg["nx"])
            ax.imshow(F, extent=(fg["x"][0], fg["x"][1], fg["y"][0], fg["y"][1]), origin="lower", cmap=FIELD_CMAP, vmin=DBMIN, vmax=0,
                      interpolation="bilinear", zorder=2)
        ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fc="none", ec=MUTED, lw=0.6, zorder=6, clip_on=False))
        w = key[0]
        ax.add_patch(Rectangle((-w / 2, -T_SI / 2), w, T_SI, fc="none", ec=INK, lw=0.6, zorder=5))
        yb = -T_SI / 2 - BOX
        ax.plot([X0, X1], [yb, yb], color=INK, lw=0.8, ls=(0, (4, 2)), zorder=5)
        name, mfd, col = match[key]
        ax.add_patch(Circle((0, 0), mfd / 2, fc="none", ec="white", lw=2.2, zorder=5))
        ax.add_patch(Circle((0, 0), mfd / 2, fc="none", ec=col, lw=1.1, ls=(0, (3, 1.5)), zorder=5))
        t = table.get(key)
        ov = t["overlap"][[kk for kk in t["overlap"] if kk.startswith(name)][0]] if t else None
        ax.text(X0 + 0.5, Y1 - 0.5, f"{key[1]}, {1000 * w:.0f} nm tip", ha="left", va="top", fontsize=7.2, color=INK, fontweight="bold", zorder=7)
        ax.text(X0 + 0.5, Y1 - 2.0, f"MFD {t['mfd_x']:.1f} × {t['mfd_y']:.1f} µm", ha="left", va="top", fontsize=6.6, color=INK, zorder=7)
        ax.text(X0 + 0.5, Y0 + 0.5, f"{name} {mfd:g} µm: {100 * ov:.0f} %", ha="left", va="bottom", fontsize=6.6, color=col, zorder=7)
        if m["below2um"] >= 0.005:
            pct = 100 * m["below2um"]
            ax.text(X1 - 0.5, yb - 1.6, f"{pct:.1f} % below" if pct < 9.95 else f"{pct:.0f} % below", ha="right", va="top", fontsize=6.3,
                    color=INK, zorder=7, bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8))
        if k == 0:
            ax.text(X1 - 0.5, yb + 0.3, "2 µm BOX ends", ha="right", va="bottom", fontsize=6.3, color=INK, zorder=7)
            ax.plot([X1 - 5.5, X1 - 0.5], [Y1 - 1.0, Y1 - 1.0], color=INK, lw=1.4, zorder=7, solid_capstyle="butt")
            ax.text(X1 - 3.0, Y1 - 1.4, "5 µm", ha="center", va="top", fontsize=6.3, color=INK, zorder=7)
        print(f"   {key[1]} {1000 * w:.0f} nm: femwell MFD {m['mfd_x']:.2f} x {m['mfd_y']:.2f} um (Table: "
              f"{t['mfd_x']:.2f} x {t['mfd_y']:.2f}), below 2 um {100 * m['below2um']:.1f} % (Table {100 * t['below2um']:.1f} %), "
              f"overlap with {name} {100 * ov:.0f} %")
    cax = fig.add_axes([0.945, 0.12, 0.013, 0.76])
    cb = fig.colorbar(im, cax=cax, ticks=[-30, -20, -10, 0])
    cb.ax.tick_params(labelsize=6.5, length=2)
    cb.outline.set_linewidth(0.5)
    cb.set_label("intensity (dB)", fontsize=7)
    save(fig, "ch16_modes")
    print("Fig 16.3: maps from ch16_fields.json")


FIGS = {"butt": fig_butt, "taper": fig_taper, "modes": fig_modes, "multistage": fig_multistage, "facets": fig_facets,
        "angled": fig_angled}


# ====================================================================== Figure 16.7: elliptical and astigmatic beams
def gw(z, w0, z0, lam=1.55):
    zr = math.pi * w0 ** 2 / lam
    return w0 * np.sqrt(1 + ((z - z0) / zr) ** 2)


def fig_astig():
    lam, wx0, wy0, zx0, zy0 = 1.55, 1.5, 1.2, -4.0, 0.0       # illustrative edge-coupler beam: x waist 4 um inside the chip
    z = np.linspace(-8, 20, 600); zo = z >= 0
    fig = plt.figure(figsize=(6.3, 3.3))
    for k, (w0, z0, ttl, col) in enumerate(((wx0, zx0, "top view: width in the chip plane, x", C1), (wy0, zy0, "side view: height across the chip, y", C4))):
        ax = fig.add_axes([0.08, 0.56 - 0.44 * k, 0.48, 0.36])
        w = gw(z, w0, z0, lam)
        ax.add_patch(plt.Rectangle((-8, -6), 8, 12, fc="#E3E7EE", ec="none", zorder=0))
        ax.text(-7.6, 4.6, "chip", fontsize=6.5, color=MUTED, va="center")
        ax.axvline(0, color=INK, lw=0.9); ax.text(0.3, 4.6, "facet", fontsize=6.5, color=INK, va="center")
        ax.fill_between(z[zo], -w[zo], w[zo], color=col, alpha=0.18, lw=0)
        ax.plot(z[zo], w[zo], color=col, lw=1.4); ax.plot(z[zo], -w[zo], color=col, lw=1.4)
        if z0 < 0:                                              # the beam seems to come from a waist inside the chip
            ax.plot(z[~zo], w[~zo], color=col, lw=1.0, ls=(0, (3, 2))); ax.plot(z[~zo], -w[~zo], color=col, lw=1.0, ls=(0, (3, 2)))
        ax.axvline(z0, color=col, lw=0.8, ls=":")
        ax.annotate("", xy=(z0, -w0), xytext=(z0, w0), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.7, mutation_scale=6))
        lab = f"waist {2*w0:.1f} µm,\n{abs(z0):.0f} µm inside\nthe chip" if z0 < 0 else f"waist {2*w0:.1f} µm, on the facet"
        ax.text(z0 + 0.5 if z0 >= 0 else -7.7, -4.3 if z0 < 0 else -4.8, lab, fontsize=6.2, color=col, ha="left", va="center", zorder=5,
                bbox=dict(boxstyle="square,pad=0.1", fc="#E3E7EE" if z0 < 0 else "white", ec="none"))
        ax.set_xlim(-8, 20); ax.set_ylim(-6, 6); ax.set_yticks([-4, 0, 4]); ax.grid(False)
        ax.set_title(ttl, loc="left", fontsize=7.2, color=INK, pad=2)
        if k == 1:
            finish(ax, "Distance from the facet, z (µm)", "y (µm)")
            ax.annotate("", xy=(zx0, 5.3), xytext=(zy0, 5.3), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
            ax.text((zx0 + zy0) / 2, 5.5, "Δz", fontsize=6.6, ha="center", va="bottom", color=INK)
        else:
            ax.set_xticklabels([]); finish(ax, None, "x (µm)"); tag(ax, "a")
    b = fig.add_axes([0.66, 0.14, 0.32, 0.76])
    dz = np.linspace(0, 15, 301)
    print("astigmatism loss (one direction defocused by dz, the other matched):")
    for w0, col, txt in ((1.25, C4, "2.5 µm spot"), (2.5, C2, "5 µm spot"), (5.2, C1, "10.4 µm (SMF-28)")):
        zr = math.pi * w0 ** 2 / lam; loss = 5 * np.log10(1 + (dz / (2 * zr)) ** 2)
        b.plot(dz, loss, color=col, lw=1.5)
        l5 = 5 * math.log10(1 + (5 / (2 * zr)) ** 2); l10 = 5 * math.log10(1 + (10 / (2 * zr)) ** 2)
        print(f"  w0 {w0} um (zR {zr:.2f} um): 5 um -> {l5:.2f} dB, 10 um -> {l10:.2f} dB")
        tx, ty, ha = (9.4, 1.9, "left") if w0 < 2 else (14.6, min(loss[-1], 3.8) + 0.12, "right")
        b.text(tx, ty, txt, fontsize=6.4, color=col, ha=ha, va="bottom")
    b.axvline(5, color=MUTED, lw=0.6, ls=":")
    b.set_xlim(0, 15); b.set_ylim(0, 4)
    finish(b, "Astigmatism Δz (µm)", "Coupling loss (dB)"); tag(b, "b")
    print(f"  drawn beam: x waist {2*wx0} um at z = {zx0}, y waist {2*wy0} um on the facet")
    save(fig, "ch16_astig")


FIGS["astig"] = fig_astig

if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for nme in names:
        FIGS[nme]()
