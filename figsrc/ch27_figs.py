"""Figures for Chapter 27 (lasers on silicon).

Run from the repository root:  python -I -X utf8 figsrc/ch27_figs.py
NumPy and Matplotlib only (the femwell supermodes come from figsrc/ch27_hybrid.json, made by figsrc/ch27_hybrid.py,
the data of Table 27.1 and the hybrid demo). Prints every number the captions quote, then writes assets/figs/ch27_*.svg.

  ch27_options     six ways to bring the laser to the silicon (schematic side views)
  ch27_hetero      heterogeneous laser along its length (schematic) and the fundamental supermode moving from the
                   III-V into the silicon as the silicon widens (femwell maps of ch27_hybrid.json)
  ch27_printing    micro-transfer printing in four steps (schematic)
  ch27_monolithic  quantum-dot laser grown on silicon: blanket stack with dislocation filters, and growth in a pocket
  ch27_thermal     heat path of a bonded laser on SOI (BOX, thermal shunt) and L-I curves with self-heating
                   (Worked Example 27.1: Z_th = 80 K/W, 100 mA, 1.5 V, 20 mW -> 10.4 K, +19 % threshold)
  ch27_microring   row of directly modulated microring lasers on one bus, and the 0.1 % size sensitivity of their modes
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *
from matplotlib.patches import FancyArrowPatch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
HEAT = "#E08A3A"


# ====================================================================== Figure: integration options
def soi(ax, x0, x1, recess=None, top=True):
    """SOI chip from x0 to x1: substrate 0-1.2, BOX 1.2-1.9, Si device layer 1.9-2.15, top oxide 2.15-2.7.
    recess=(xa, xb, ybottom) etches a pocket through everything down to ybottom."""
    segs = [(x0, x1)] if recess is None else [(x0, recess[0]), (recess[1], x1)]
    box(ax, x0, 0, x1 - x0, 1.2 if recess is None else recess[2], "sub")
    if recess is not None:
        for a, b in segs:
            if b > a: box(ax, a, recess[2], b - a, 1.2 - recess[2], "sub")
    for a, b in segs:
        if b <= a: continue
        box(ax, a, 1.2, b - a, 0.7, "ox")
        if top: box(ax, a, 2.15, b - a, 0.55, "oxtop")


def si_wg(ax, x0, x1):
    box(ax, x0, 1.9, x1 - x0, 0.25, "si", z=3)


def gc_teeth(ax, x0, n=6, p=0.32):
    box(ax, x0 - 0.3, 1.9, n * p + 0.3, 0.12, "si", z=3)
    for k in range(n):
        box(ax, x0 + k * p, 2.02, p / 2, 0.13, "si", z=3)


def light(ax, pts, curved=None, lw=1.3):
    if curved is None:
        arrow(ax, pts[0], pts[1], col=RED, lw=lw, ms=7, z=8)
    else:
        a = FancyArrowPatch(pts[0], pts[1], connectionstyle=f"arc3,rad={curved}", arrowstyle="-|>", mutation_scale=7,
                            color=RED, lw=lw, zorder=8)
        ax.add_patch(a)


def caption_under(ax, title, sub):
    ax.text(5, -0.35, title, ha="center", va="top", fontsize=7.2, color=INK, fontweight="bold")
    ax.text(5, -1.05, sub, ha="center", va="top", fontsize=6.3, color=MUTED)


def fig_options():
    fig = plt.figure(figsize=(6.3, 3.75))
    W, H = 0.325, 0.48
    axs = [fig.add_axes([0.005 + c * 0.333, 0.515 - r * 0.505, W, H]) for r in range(2) for c in range(3)]
    for ax in axs:
        frameless(ax, (0, 10), (-1.8, 5.4))
    # 1 off-chip laser, fibre to a grating coupler
    ax = axs[0]
    soi(ax, 3.0, 10); si_wg(ax, 6.8, 10); gc_teeth(ax, 4.9)
    block(ax, 1.7, 3.7, 2.4, 1.0, "laser\nmodule", fc=MAT["inp"], fs=6.3)
    th = np.radians(12)
    fx = 5.85 - np.sin(th) * np.array([0.0, 2.3]); fy = 2.75 + np.cos(th) * np.array([0.0, 2.3])
    ax.plot(fx, fy, color=MAT["glass"], lw=9, solid_capstyle="butt", zorder=4)
    ax.plot(fx, fy, color=MAT["core"], lw=2.2, solid_capstyle="butt", zorder=5)
    xs_, ys_ = np.linspace(2.9, fx[1], 40), None
    ys_ = 3.7 + (fy[1] - 3.7) * np.sin(np.linspace(0, np.pi / 2, 40)) ** 0.6
    ax.plot(xs_, ys_, color=MUTED, lw=1.0, zorder=3)
    light(ax, ((fx[1] + 0.05, fy[1] - 0.3), (5.95, 2.25)), lw=1.1)
    light(ax, ((7.2, 2.45), (9.6, 2.45)))
    label(ax, 7.4, 4.0, "fibre", fs=6.3, col=MUTED)
    panel(ax, "a", y=1.0)
    caption_under(ax, "off-chip laser", "fibre-coupled, replaceable")
    # 2 flip-chip, butt-coupled into an edge coupler
    ax = axs[1]
    soi(ax, 0.3, 10, recess=(0.3, 4.6, 0.55)); si_wg(ax, 4.6, 10)
    for xb in (1.1, 2.3, 3.5):
        box(ax, xb - 0.35, 0.55, 0.7, 0.4, "metal")
    box(ax, 0.5, 0.95, 3.9, 0.2, "metal", alpha=0.7)
    box(ax, 0.5, 1.15, 3.9, 0.6, "inp"); box(ax, 0.5, 1.75, 3.9, 0.35, "q")
    ax.plot([0.5, 4.4], [1.93, 1.93], color=MAT["mqw"], lw=0.8, zorder=3)
    box(ax, 0.5, 2.10, 3.9, 1.9, "inp")
    label(ax, 2.45, 3.25, "laser die,\nface down", fs=6.3)
    label(ax, 2.45, 0.2, "solder", fs=6.0, col=INK)
    light(ax, ((4.0, 2.02), (6.2, 2.02)))
    light(ax, ((7.2, 2.45), (9.6, 2.45)))
    panel(ax, "b", y=1.0)
    caption_under(ax, "flip-chip", "tested die, butt-coupled")
    # 3 VCSEL flip-chipped over a grating coupler
    ax = axs[2]
    soi(ax, 0.3, 10); si_wg(ax, 6.4, 10); gc_teeth(ax, 4.5)
    x0v, x1v = 3.0, 6.6
    for xb in (x0v + 0.4, x1v - 0.4):
        box(ax, xb - 0.3, 2.7, 0.6, 0.35, "metal")
    box(ax, x0v, 3.05, x1v - x0v, 0.12, "metal", alpha=0.7)
    y = 3.17
    for k in range(4):
        box(ax, x0v, y, x1v - x0v, 0.1, "#B8C9E8"); box(ax, x0v, y + 0.1, x1v - x0v, 0.1, "#EEF2FA"); y += 0.2
    box(ax, x0v, y, x1v - x0v, 0.22, "q"); ax.plot([x0v, x1v], [y + 0.11] * 2, color=MAT["mqw"], lw=0.8)
    y += 0.22
    for k in range(3):
        box(ax, x0v, y, x1v - x0v, 0.1, "#B8C9E8"); box(ax, x0v, y + 0.1, x1v - x0v, 0.1, "#EEF2FA"); y += 0.2
    box(ax, x0v, y, x1v - x0v, 0.5, "gaas")
    label(ax, x1v + 0.2, y - 0.2, "VCSEL,\nface down", fs=6.3, ha="left")
    light(ax, ((5.0, 3.1), (5.3, 2.3)), lw=1.1)
    light(ax, ((6.8, 2.45), (9.6, 2.45)))
    panel(ax, "c", y=1.0)
    caption_under(ax, "VCSEL", "over a grating coupler")
    # 4 heterogeneous: III-V bonded on the Si waveguide
    ax = axs[3]
    soi(ax, 0.3, 10, top=False); si_wg(ax, 0.3, 10)
    box(ax, 0.3, 2.15, 9.7, 0.08, "bcb")
    box(ax, 1.0, 2.23, 7.0, 0.25, "inp")
    poly(ax, [(1.6, 2.48), (6.2, 2.48), (7.6, 2.48), (7.6, 2.56), (6.2, 2.78), (1.6, 2.78)], "q")
    ax.plot([1.6, 6.2], [2.63, 2.63], color=MAT["mqw"], lw=0.8)
    poly(ax, [(1.6, 2.78), (6.2, 2.78), (6.2, 3.95), (1.6, 3.95)], "inp")
    box(ax, 1.6, 3.95, 4.6, 0.25, "metal")
    box(ax, 1.0, 2.48, 0.5, 0.2, "metal")
    label(ax, 3.9, 3.35, "bonded III–V", fs=6.3)
    callout(ax, (7.0, 2.53), (7.6, 3.6), "taper", fs=6.0)
    light(ax, ((3.4, 2.63), (6.4, 2.63)), lw=1.1)
    light(ax, ((6.5, 2.6), (8.0, 2.3)), curved=0.35, lw=1.1)
    light(ax, ((8.2, 2.45), (9.8, 2.45)))
    panel(ax, "d", y=1.0)
    caption_under(ax, "heterogeneous", "wafer or die bonding")
    # 5 micro-transfer printed coupon
    ax = axs[4]
    soi(ax, 0.3, 10, top=False); si_wg(ax, 0.3, 10)
    box(ax, 0.3, 2.15, 9.7, 0.08, "ox")
    box(ax, 1.4, 2.23, 5.4, 0.12, "polymer")
    box(ax, 1.4, 2.35, 5.4, 0.3, "inp"); box(ax, 1.4, 2.65, 5.4, 0.3, "q")
    ax.plot([1.4, 6.8], [2.8, 2.8], color=MAT["mqw"], lw=0.8)
    box(ax, 1.4, 2.95, 5.4, 1.1, "inp"); box(ax, 2.2, 4.05, 3.8, 0.22, "metal")
    for xt in (1.05, 6.8):
        box(ax, xt, 3.3, 0.35, 0.12, "inp")
    label(ax, 4.1, 3.5, "printed coupon", fs=6.3)
    callout(ax, (1.2, 3.42), (0.5, 4.8), "broken tether", fs=6.0)
    callout(ax, (6.0, 2.29), (7.6, 3.4), "adhesive", fs=6.0)
    light(ax, ((4.6, 2.8), (6.6, 2.8)), lw=1.1)
    light(ax, ((6.8, 2.75), (8.2, 2.3)), curved=0.35, lw=1.1)
    light(ax, ((8.4, 2.45), (9.8, 2.45)))
    panel(ax, "e", y=1.0)
    caption_under(ax, "transfer-printed", "tested coupons, printed in parallel")
    # 6 monolithic: QD laser grown in a pocket
    ax = axs[5]
    soi(ax, 0.3, 10, recess=(0.3, 5.0, 0.4)); si_wg(ax, 5.3, 10)
    box(ax, 0.5, 0.4, 4.3, 1.1, "gaas")
    for xs in np.linspace(0.8, 4.4, 7):
        ax.plot([xs, xs + 0.15, xs + 0.05], [0.42, 0.95, 1.35], color=MUTED, lw=0.5, zorder=3)
    box(ax, 0.5, 1.5, 4.3, 0.35, "#D8DCE3")
    box(ax, 0.5, 1.85, 4.3, 0.3, "q")
    for xd in np.arange(0.7, 4.7, 0.3):
        ax.add_patch(Circle((xd, 2.0), 0.06, fc=MAT["mqw"], ec="none", zorder=4))
    box(ax, 0.5, 2.15, 4.3, 0.9, "#D8DCE3"); box(ax, 0.5, 3.05, 4.3, 0.2, "metal")
    label(ax, 2.65, 2.62, "grown laser", fs=6.3)
    label(ax, 2.65, 0.95, "buffer", fs=6.0, bg="#E3E7EE")
    light(ax, ((4.2, 2.0), (6.6, 2.0)))
    light(ax, ((7.2, 2.45), (9.6, 2.45)))
    panel(ax, "f", y=1.0)
    caption_under(ax, "monolithic", "quantum dots grown on Si")
    fig.text(0.995, 0.005, "not to scale", ha="right", va="bottom", fontsize=6, color=MUTED, style="italic")
    save(fig, "ch27_options")


# ====================================================================== Figure: heterogeneous laser and taper (femwell)
def fig_hetero():
    D = json.load(open(os.path.join(HERE, "ch27_hybrid.json")))
    nx, ny = D["map"]["nx"], D["map"]["ny"]
    ys = np.linspace(D["map"]["y"][0], D["map"]["y"][1], ny)
    # fundamental supermode at every computed width (shares), and its intensity map where one was stored
    wa = np.array([w["w"] for w in D["widths"]])
    gm = np.array([w["modes"][0]["G_mqw"] for w in D["widths"]]); gs = np.array([w["modes"][0]["G_si"] for w in D["widths"]])
    for w in D["widths"]:
        m = w["modes"][0]
        print(f"hybrid: w {w['w']:.2f} um  n_eff {m['neff']:.4f}  MQW {100*m['G_mqw']:.1f} %  Si {100*m['G_si']:.1f} %"
              + ("  (map)" if "map" in m else ""))
    mw, prof = [], []
    for w in D["widths"]:
        m = w["modes"][0]
        if "map" in m:
            p = np.array(m["map"], float).reshape(ny, nx).sum(axis=1)       # intensity integrated across the width
            mw.append(w["w"]); prof.append(p / p.max())
    mw = np.array(mw); prof = np.array(prof).T                                   # (height, width)
    yf = np.linspace(ys[0], ys[-1], 161)
    prof = np.array([np.interp(yf, ys, col) for col in prof.T]).T
    ys = yf; ws = wa
    # where the MQW and Si shares are equal (linear interpolation between the computed widths)
    d = gm - gs; j = np.where(np.diff(np.sign(d)) != 0)[0][0]
    w_eq = ws[j] + (ws[j + 1] - ws[j]) * d[j] / (d[j] - d[j + 1])
    print(f"equal MQW and Si shares at w = {w_eq:.3f} um ({100*np.interp(w_eq, ws, gm):.0f} % each)")
    fig = plt.figure(figsize=(6.3, 4.3))
    # (a) the laser along its length
    ax = fig.add_axes([0.0, 0.61, 1.0, 0.38]); frameless(ax, (-4, 106), (-2.2, 7.4), equal=False)
    box(ax, 0, 0, 100, 1.0, "sub"); box(ax, 0, 1.0, 100, 1.4, "ox")
    box(ax, 0, 2.4, 100, 0.55, "si", z=3)
    for x0 in (3, 83):
        for k in range(24):
            box(ax, x0 + k * 0.58, 2.95, 0.29, 0.25, "si", z=3)
    box(ax, 0, 2.95, 100, 0.25, "oxtop", z=1); box(ax, 21, 2.95, 58, 0.12, "bcb", z=2)
    box(ax, 22, 3.07, 56, 0.4, "inp")
    box(ax, 26, 3.47, 48, 0.55, "q"); ax.plot([26, 74], [3.75, 3.75], color=MAT["mqw"], lw=1.0, zorder=3)
    box(ax, 26, 4.02, 48, 2.3, "inp"); box(ax, 30, 6.32, 40, 0.35, "metal")
    box(ax, 22.5, 3.47, 2.5, 0.25, "metal"); box(ax, 75, 3.47, 2.5, 0.25, "metal")
    label(ax, 50, 5.2, "III–V gain section (p-InP / MQW / n-InP)", fs=FS_SMALL)
    label(ax, 10, 4.1, "Si Bragg mirror", fs=FS_SMALL); label(ax, 90, 4.1, "Si Bragg mirror\n(partial: output)", fs=FS_SMALL)
    label(ax, 50, 1.7, "buried oxide", fs=FS_SMALL); label(ax, 50, 0.45, "Si substrate", fs=FS_SMALL)
    # Si width along the laser and the taper regions
    for xa, xb, t in ((0, 26, "Si 1.5 µm wide"), (26, 38, "taper"), (38, 62, "Si 0.4–0.5 µm"), (62, 74, "taper"), (74, 100, "Si 1.5 µm wide")):
        ax.plot([xa + 0.4, xb - 0.4], [-0.6, -0.6], color=MUTED, lw=0.6)
        ax.text((xa + xb) / 2, -0.75, t, ha="center", va="top", fontsize=6.0, color=MUTED)
    for xx in (26, 38, 62, 74):
        ax.plot([xx, xx], [-0.9, 7.2], color=MUTED, lw=0.5, ls=(0, (2, 2)), zorder=6)
    # the mode: in the Si at the ends, in the MQW in the gain section
    zz = np.linspace(0, 100, 400)
    yc = np.interp(zz, [0, 26, 38, 62, 74, 100], [2.67, 2.67, 3.75, 3.75, 2.67, 2.67])
    for k, a in ((0.9, 0.25), (0.55, 0.45), (0.28, 0.75)):
        ax.fill_between(zz, yc - k * 0.55, yc + k * 0.55, color=RED, alpha=a * 0.45, lw=0, zorder=5)
    arrow(ax, (99, 2.67), (104, 2.67), col=RED, lw=1.5, ms=8, z=8)
    note(ax, "not to scale; red: where the light is", loc="upper right")
    panel(ax, "a", x=0.0, y=1.0)
    # (b) femwell map along a taper
    b = fig.add_axes([0.10, 0.09, 0.76, 0.42])
    # resample the width axis finely (linear interpolation between the widths with stored maps) for a smooth image
    wf = np.linspace(mw[0], mw[-1], 221)
    img = np.array([np.interp(wf, mw, row) for row in prof])
    b.imshow(img, origin="lower", aspect="auto", extent=[wf[0], wf[-1], ys[0], ys[-1]], cmap=FIELD_CMAP, vmin=0, vmax=1,
             interpolation="bilinear")
    for wv in mw:
        b.plot([wv], [-0.55], marker="^", color=MUTED, ms=3.5, clip_on=False, zorder=5)
    lay = [("Si", 0.0, 0.5), ("MQW", 0.64, 0.94)]
    for name, y0, y1 in lay:
        for yy in (y0, y1):
            b.axhline(yy, color=INK, lw=0.5, ls=(0, (3, 2)))
    b.text(1.53, 0.25, "Si", va="center", fontsize=6.8, color=INK, clip_on=False)
    b.text(1.53, 0.79, "MQW", va="center", fontsize=6.8, color=INK, clip_on=False)
    b.text(1.53, 1.7, "p-InP", va="center", fontsize=6.8, color=INK, clip_on=False)
    b.text(1.53, -0.35, "oxide", va="center", fontsize=6.8, color=INK, clip_on=False)
    b.axvline(w_eq, color=AMBER, lw=0.8)
    for wv, ha, dx in ((mw[0], "left", 0.02), (w_eq, "center", 0.0), (mw[-1], "right", -0.02)):
        g1, g2 = np.interp(wv, ws, gm), np.interp(wv, ws, gs)
        print(f"label at w = {wv:.3f} um: MQW {100*g1:.1f} %, Si {100*g2:.1f} %")
        b.text(wv + dx, 2.45, f"MQW {100*g1:.0f} %\nSi {100*g2:.0f} %", ha=ha, va="top", fontsize=6.3, color=INK,
               bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.85))
    b.set_ylim(-0.6, 2.6); b.set_xlim(mw[0], mw[-1]); b.grid(False)
    finish(b, "Silicon width under the III–V (µm), increasing along the taper", "Height (µm)")
    tag(b, "b")
    save(fig, "ch27_hetero")


# ====================================================================== Figure: micro-transfer printing
def fig_printing():
    fig = plt.figure(figsize=(6.3, 2.0))
    axs = [fig.add_axes([0.005 + i * 0.25, 0.04, 0.24, 0.94]) for i in range(4)]
    for ax in axs:
        frameless(ax, (0, 10), (-0.3, 9.3))
    def source(ax, picked=False, n=2):
        box(ax, 0.2, 0, 9.6, 1.6, "inp")
        box(ax, 0.2, 1.6, 9.6, 0.25, "#E3E7EE")       # sacrificial layer (etched under the coupons)
        for x0 in (1.0, 5.6)[:n]:
            box(ax, x0 + 0.2, 1.6, 3.0, 0.25, "white")  # undercut
            if not picked:
                box(ax, x0, 1.85, 3.4, 1.4, "inp"); box(ax, x0, 2.35, 3.4, 0.3, "q")
                ax.plot([x0, x0 + 3.4], [2.5, 2.5], color=MAT["mqw"], lw=0.7)
                box(ax, x0 + 0.6, 3.25, 2.2, 0.2, "metal")
        for xt in (0.65, 4.4, 5.25, 9.0):
            if not picked: box(ax, xt, 2.5, 0.35, 0.12, "inp")
    # 1 released coupons on tethers
    ax = axs[0]; source(ax)
    for xs in (0.2, 4.75, 9.35):
        box(ax, xs, 1.85, 0.45, 0.8, "inp")
    callout(ax, (0.82, 2.55), (1.0, 5.0), "tether", fs=6.0)
    callout(ax, (2.6, 1.72), (5.2, 4.2), "sacrificial layer\netched away", fs=6.0)
    label(ax, 5, 6.8, "III–V source wafer:\nfinished, tested devices", fs=6.3)
    panel(ax, "1", y=1.0)
    # 2 stamp picks up
    ax = axs[1]; source(ax, picked=True)
    for xs in (0.2, 4.75, 9.35):
        box(ax, xs, 1.85, 0.45, 0.8, "inp")
    box(ax, 0.6, 5.5, 8.8, 1.8, "polymer", ec=MUTED, lw=0.5)
    for x0 in (1.0, 5.6):
        box(ax, x0 + 0.4, 5.0, 2.6, 0.5, "polymer", ec=MUTED, lw=0.5)
        box(ax, x0 + 0.6, 4.8, 2.2, 0.2, "metal")
        box(ax, x0, 3.4, 3.4, 1.4, "inp"); box(ax, x0, 3.9, 3.4, 0.3, "q")
        ax.plot([x0, x0 + 3.4], [4.05, 4.05], color=MAT["mqw"], lw=0.7)
    arrow(ax, (5, 7.6), (5, 8.9), col=INK, lw=1.0, ms=7)
    label(ax, 5, 6.4, "elastomer stamp", fs=6.3)
    panel(ax, "2", y=1.0)
    # 3 printing onto the silicon target wafer
    ax = axs[2]
    box(ax, 0.2, 0, 9.6, 1.4, "sub"); box(ax, 0.2, 1.4, 9.6, 0.6, "ox"); box(ax, 0.2, 2.0, 9.6, 0.22, "si")
    box(ax, 0.2, 2.22, 9.6, 0.15, "ox")
    box(ax, 0.6, 5.5, 8.8, 1.8, "polymer", ec=MUTED, lw=0.5)
    for x0 in (1.0, 5.6):
        box(ax, x0 + 0.4, 5.0, 2.6, 0.5, "polymer", ec=MUTED, lw=0.5)
        box(ax, x0 + 0.6, 4.8, 2.2, 0.2, "metal")
        box(ax, x0, 3.4, 3.4, 1.4, "inp"); box(ax, x0, 3.9, 3.4, 0.3, "q")
        ax.plot([x0, x0 + 3.4], [4.05, 4.05], color=MAT["mqw"], lw=0.7)
        arrow(ax, (x0 + 1.7, 3.25), (x0 + 1.7, 2.6), col=INK, lw=0.9, ms=6)
    label(ax, 5, 8.3, "printed onto the processed\nSi wafer, many at a time", fs=6.3)
    label(ax, 5, 0.7, "SOI target wafer", fs=6.0)
    panel(ax, "3", y=1.0)
    # 4 after printing: wired up, coupled to the Si waveguide
    ax = axs[3]
    box(ax, 0.2, 0, 9.6, 1.4, "sub"); box(ax, 0.2, 1.4, 9.6, 0.6, "ox"); box(ax, 0.2, 2.0, 9.6, 0.22, "si")
    box(ax, 0.2, 2.22, 9.6, 0.15, "ox")
    for x0 in (1.0, 5.6):
        box(ax, x0, 2.37, 3.4, 0.1, "polymer")
        box(ax, x0, 2.47, 3.4, 1.4, "inp"); box(ax, x0, 2.97, 3.4, 0.3, "q")
        ax.plot([x0, x0 + 3.4], [3.12, 3.12], color=MAT["mqw"], lw=0.7)
        box(ax, x0 + 0.6, 3.87, 2.2, 0.2, "metal")
        ax.plot([x0 + 1.7, x0 + 1.7, x0 + 4.0], [4.07, 5.2, 5.2], color=MAT["metal"], lw=1.4)
    label(ax, 5, 6.4, "metal wiring; light couples\nto the Si below", fs=6.3)
    label(ax, 5, 0.7, "SOI target wafer", fs=6.0)
    light(ax, ((2.7, 3.12), (3.9, 2.25)), curved=0.25, lw=1.0)
    panel(ax, "4", y=1.0)
    fig.text(0.995, 0.01, "not to scale", ha="right", va="bottom", fontsize=6, color=MUTED, style="italic")
    save(fig, "ch27_printing")


# ====================================================================== Figure: monolithic growth
def fig_monolithic():
    fig = plt.figure(figsize=(6.3, 2.9))
    a = fig.add_axes([0.0, 0.03, 0.47, 0.95]); frameless(a, (-3.2, 10), (-0.4, 9.6), equal=False)
    layers = [("Si substrate", "sub", 0.0, 1.4), ("GaAs buffer", "gaas", 1.4, 2.0), ("", "#C9CEDA", 3.4, 0.25),
              ("", "gaas", 3.65, 0.6), ("", "#C9CEDA", 4.25, 0.25), ("", "gaas", 4.5, 0.5),
              ("n-cladding", "#D8DCE3", 5.0, 1.2), ("QD active", "q", 6.2, 0.5), ("p-cladding", "#D8DCE3", 6.7, 1.2),
              ("contact", "metal", 7.9, 0.25)]
    for name, m, y0, h in layers:
        box(a, 0, y0, 10, h, m)
    rng = np.random.default_rng(3)
    for x0 in np.linspace(0.4, 9.6, 16):
        stop = rng.choice([3.4, 4.25, 6.0], p=[0.55, 0.3, 0.15])
        y = np.linspace(1.4, stop, 20)
        x = x0 + 0.25 * np.sin((y - 1.4) * rng.uniform(1, 3)) + (y - 1.4) * rng.uniform(-0.15, 0.15)
        a.plot(x, y, color=INK, lw=0.6, alpha=0.75, zorder=3)
        if stop < 5:
            a.plot([x[-1], x[-1] + rng.choice([-1, 1]) * 0.9], [stop, stop + 0.04], color=INK, lw=0.6, alpha=0.75, zorder=3)
    for xd in np.arange(0.3, 10, 0.4):
        a.add_patch(Circle((xd, 6.45), 0.09, fc=MAT["mqw"], ec="none", zorder=4))
    for name, m, y0, h in layers:
        if name:
            a.text(-0.2, y0 + h / 2, name, ha="right", va="center", fontsize=6.5, color=INK)
    a.text(-0.3, 3.95, "dislocation\nfilters", ha="right", va="center", fontsize=6.5, color=INK)
    a.plot([-0.15, -0.15], [3.4, 4.5], color=MUTED, lw=0.6)
    callout(a, (6.1, 2.5), (7.2, 0.6), "threading dislocations", fs=6.3)
    a.annotate("", xy=(10.25, 6.45), xytext=(10.25, 1.4), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=6), annotation_clip=False)
    a.text(10.35, 3.9, "several\nµm", fontsize=6.3, color=INK, va="center", ha="left")
    panel(a, "a", x=-0.02, y=1.0)
    note(a, "not to scale", loc="upper right")
    # (b) growth in a pocket next to the SOI waveguide
    b = fig.add_axes([0.53, 0.03, 0.47, 0.95]); frameless(b, (0, 10), (-0.4, 9.6), equal=False)
    box(b, 0, 0, 10, 2.4, "sub")
    box(b, 5.6, 2.4, 4.4, 1.8, "ox"); box(b, 5.6, 4.2, 4.4, 0.5, "si"); box(b, 5.6, 4.7, 4.4, 1.6, "oxtop")
    box(b, 0.5, 2.4, 4.8, 1.2, "gaas")
    for x0 in np.linspace(0.8, 5.0, 8):
        y = np.linspace(2.4, 3.4, 10)
        b.plot(x0 + 0.15 * np.sin(4 * y), y, color=INK, lw=0.6, alpha=0.75)
    box(b, 0.5, 3.6, 4.8, 0.6, "#D8DCE3"); box(b, 0.5, 4.2, 4.8, 0.5, "q")
    for xd in np.arange(0.7, 5.2, 0.4):
        b.add_patch(Circle((xd, 4.45), 0.09, fc=MAT["mqw"], ec="none", zorder=4))
    box(b, 0.5, 4.7, 4.8, 1.2, "#D8DCE3"); box(b, 0.5, 5.9, 4.8, 0.25, "metal")
    arrow(b, (4.8, 4.45), (7.3, 4.45), col=RED, lw=1.5, ms=8, z=8)
    label(b, 2.9, 7.6, "laser grown in a pocket\netched through the BOX", fs=6.5)
    label(b, 7.8, 7.6, "SOI waveguide,\nactive region aligned", fs=6.5)
    label(b, 7.8, 3.3, "BOX", fs=6.5); label(b, 5, 1.1, "Si substrate", fs=6.5)
    label(b, 2.9, 3.0, "buffer", fs=6.3, bg="#E3E7EE")
    callout(b, (5.4, 4.45), (6.3, 5.6), "gap", fs=6.0)
    panel(b, "b", x=0.0, y=1.0)
    note(b, "not to scale", loc="upper right")
    save(fig, "ch27_monolithic")


# ====================================================================== Figure: thermal path and self-heating
ZTH, I0, V0, RS, POUT0, T0 = 80.0, 0.100, 0.9, 6.0, 0.020, 60.0     # Worked Example 27.1 (V = 0.9 V + 6 ohm x I = 1.5 V)
ITH0 = 0.020                                                          # threshold without self-heating (illustrative)


def lasing(I, Z, eta):
    """Output power (W) and temperature rise (K) with self-heating: P = eta (I - Ith0 exp(dT/T0)), dT = Z (IV - P)."""
    Ps = np.linspace(0, 0.3, 30001)
    dT = Z * (I * (V0 + RS * I) - Ps)
    f = Ps - eta * np.clip(I - ITH0 * np.exp(dT / T0), 0, None)
    k = np.argmax(f >= 0)
    return Ps[k], Z * (I * (V0 + RS * I) - Ps[k])


def fig_thermal():
    # calibrate the slope efficiency so the worked example's point holds: 20 mW at 100 mA with Z = 80 K/W
    dT0 = ZTH * (I0 * (V0 + RS * I0) - POUT0)
    eta = POUT0 / (I0 - ITH0 * np.exp(dT0 / T0))
    print(f"Worked Example 27.1: P_diss {1e3*(I0*(V0+RS*I0)-POUT0):.0f} mW, dT {dT0:.1f} K, threshold x{np.exp(dT0/T0):.3f}; "
          f"model I_th0 {ITH0*1e3:.0f} mA, V = {V0} V + {RS} ohm I, slope efficiency {eta:.3f} W/A")
    fig = plt.figure(figsize=(6.3, 2.9))
    a = fig.add_axes([0.0, 0.02, 0.52, 0.96]); frameless(a, (-7.6, 7.6), (-3.6, 4.6))
    # to scale: 2 um BOX, 500 nm Si, 30 nm bond, n-InP 110 nm x 12 um, mesa 3 um wide (MQW 300 nm, p-InP 1.5 um, cap)
    box(a, -7.6, -3.6, 15.2, 1.6, "sub"); box(a, -7.6, -2.0, 15.2, 2.0, "ox"); box(a, -7.6, 0.0, 15.2, 0.53, "ox")
    box(a, -0.25, 0.0, 0.5, 0.5, "si", z=3)
    box(a, -6.0, 0.53, 12.0, 0.11, "inp"); box(a, -1.5, 0.64, 3.0, 0.30, "q")
    a.plot([-1.5, 1.5], [0.79, 0.79], color=MAT["mqw"], lw=0.9, zorder=3)
    box(a, -1.5, 0.94, 3.0, 1.5, "inp"); box(a, -1.5, 2.44, 3.0, 0.1, "q")
    box(a, -1.2, 2.54, 2.4, 0.3, "metal")
    for s in (-1, 1):
        box(a, s * 4.6 - 0.9, 0.64, 1.8, 0.3, "metal")
        box(a, s * 4.6 - 0.45, -2.0, 0.9, 2.53, "metal" if s > 0 else "ox", z=2)
    # heat source and paths
    a.add_patch(plt.matplotlib.patches.Ellipse((0, 0.79), 2.8, 0.55, fc=HEAT, alpha=0.35, ec="none", zorder=4))
    for x0, y0, x1, y1 in ((0, 0.6, 0, -0.9), (-0.9, 0.6, -2.0, -0.9), (0.9, 0.6, 2.0, -0.9)):
        arrow(a, (x0, y0), (x1, y1), col=HEAT, lw=1.3, ms=7, z=6)
    label(a, 0, -1.5, "BOX blocks most of the heat", fs=6.3, col=INK, bg=MAT["ox"])
    arrow(a, (1.6, 0.58), (3.6, 0.58), col=HEAT, lw=1.3, ms=7, z=6)
    arrow(a, (4.6, 0.3), (4.6, -2.5), col=HEAT, lw=1.6, ms=8, z=6)
    label(a, 4.0, -2.45, "thermal shunt\n(metal through the BOX)", fs=6.3, ha="right", va="top")
    label(a, 0, 3.15, "p contact", fs=6.3); label(a, -4.6, 1.25, "n contact", fs=6.3); label(a, 4.6, 1.25, "n contact", fs=6.3)
    label(a, 0, 1.7, "p-InP", fs=6.3); label(a, -6.9, -1.0, "BOX", fs=6.3, ha="left")
    label(a, -6.9, -2.85, "Si substrate", fs=6.3, ha="left")
    scalebar(a, -7.2, 2.6, 2.0, "2 µm")
    panel(a, "a", x=0.0, y=1.0)
    note(a, "to scale; heat flow schematic", loc="upper right")
    # (b) L-I curves
    b = fig.add_axes([0.62, 0.17, 0.36, 0.76])
    Is = np.linspace(0, 0.6, 241)
    for Z, col, lab in ((0.0, MUTED, "no self-heating"), (40.0, C3, r"Z$_\mathrm{th}$ = 40 K/W (shunt)"), (80.0, C4, r"Z$_\mathrm{th}$ = 80 K/W")):
        P = np.array([lasing(I, Z, eta)[0] for I in Is])
        b.plot(Is * 1e3, P * 1e3, color=col, label=lab)
        k = np.argmax(P)
        print(f"Z = {Z:.0f} K/W: P(100 mA) = {1e3*lasing(0.1, Z, eta)[0]:.1f} mW, dT(100 mA) = {lasing(0.1, Z, eta)[1]:.1f} K; "
              f"peak {1e3*P[k]:.1f} mW at {1e3*Is[k]:.0f} mA" + (" (roll-over)" if k < len(Is) - 1 else ""))
    P1, dT1 = lasing(I0, ZTH, eta)
    b.plot([I0 * 1e3], [P1 * 1e3], "o", color=C4, ms=4)
    b.annotate(f"{P1*1e3:.0f} mW, +{dT1:.1f} K", xy=(I0 * 1e3, P1 * 1e3), xytext=(150, 12), fontsize=6.5, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xlim(0, 600); b.set_ylim(0, 160)
    finish(b, "Current (mA)", "Output power (mW)", legend=True, loc="upper left")
    tag(b, "b")
    save(fig, "ch27_thermal")


# ====================================================================== Figure: microring laser transmitter
def fig_microring():
    D, ng, lam, dndT = 40.0, 3.7, 1310.0, 2e-4
    fsr = lam ** 2 / (ng * np.pi * D * 1e3)
    dl_size = lam * 1e-3
    dl_T = lam * dndT / ng
    print(f"microring: D {D} um, n_g {ng}: FSR {fsr:.2f} nm at {lam:.0f} nm; +0.1 % size -> {dl_size:.2f} nm; "
          f"{dl_T:.3f} nm/K")
    fig = plt.figure(figsize=(6.3, 3.6))
    a = fig.add_axes([0.0, 0.42, 1.0, 0.57]); frameless(a, (-30, 290), (-28, 52))
    box(a, -30, -28, 320, 80, "ox", z=0)
    wg_straight(a, -30, 290, 0, 1.0, "si")
    for i in range(4):
        cx = 30 + 70 * i; cy = D / 2 - 1.5
        wg_ring(a, cx, cy, D / 2 - 1.5, 3.0, "inp")
        wg_ring(a, cx, cy, D / 2 - 1.5, 1.2, "q")
        a.add_patch(Circle((cx, cy), 6.0, fc=MAT["metal"], ec="none", zorder=3))
        wg_arc(a, cx, cy, D / 2 + 3.0, 2.2, 25, 155, "tin", alpha=0.7, z=2)
        label(a, cx + 14, -6.5, f"D$_{i+1}$", fs=FS)
        label(a, cx, cy, f"λ$_{i+1}$", fs=6.3)
    callout(a, (100 + 14, cy + 17.5), (128, 44), "heater (or MOS tuning)", fs=6.3)
    arrow(a, (275, -4.5), (289, -4.5), col=RED, lw=1.4, ms=8)
    label(a, 272, -10.5, "4 λ out", fs=6.3, col=RED)
    label(a, -26, 4.5, "Si bus", fs=6.3, ha="left")
    callout(a, (100 - 8, 2.0), (60, -19), "III–V microring (MQW), bonded over the Si bus", fs=6.3)
    scalebar(a, 220, -20, 20, "20 µm")
    note(a, f"rings {D:.0f} µm across, to scale; D$_1$ < D$_2$ < D$_3$ < D$_4$ by fractions of a per cent", loc="lower left")
    panel(a, "a", x=0.0, y=1.0)
    b = fig.add_axes([0.10, 0.10, 0.86, 0.24])
    m = np.arange(-4, 5)
    l1 = 1310 + m * fsr; l2 = l1 + dl_size
    for x in l1: b.plot([x, x], [0, 1], color=C1, lw=1.6)
    for x in l2: b.plot([x, x], [0, 0.75], color=C2, lw=1.6)
    b.annotate("", xy=(1310 + dl_size, 0.86), xytext=(1310, 0.86), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7, mutation_scale=6))
    b.text(1310 + dl_size + 0.25, 0.86, f"{dl_size:.2f} nm", ha="left", va="center", fontsize=6.5, color=INK)
    b.annotate("", xy=(1310 + fsr, 1.12), xytext=(1310, 1.12), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    b.text(1310 + fsr / 2, 1.18, f"FSR {fsr:.2f} nm", ha="center", va="bottom", fontsize=6.5, color=INK)
    b.set_xlim(1297, 1323); b.set_ylim(0, 1.75); b.set_yticks([])
    b.plot([], [], color=C1, lw=1.6, label=f"D = {D:.0f} µm"); b.plot([], [], color=C2, lw=1.6, label=f"D 0.1 % larger")
    b.legend(loc="upper left", ncol=2, bbox_to_anchor=(0.0, 1.08))
    finish(b, "Wavelength (nm)", "Modes")
    tag(b, "b")
    save(fig, "ch27_microring")


# ================================================================== Figure 27.11: a magneto-optic MZI isolator (Section 27.10)
def fig_isolator():
    """(a) Schematic of an MZI isolator: magneto-optic garnet on both arms, magnetised in opposite directions, gives
    non-reciprocal phases +-pi/4 (pi/2 between the arms), and a reciprocal delay gives -pi/2: forward the arms meet in
    phase, backward in antiphase, so the backward light leaves through the other port. (b) Forward and backward
    transmission against wavelength for a short and a long reciprocal delay (orders 1 and 20), n_g = 4.2; the
    non-reciprocal phase is taken as constant with wavelength."""
    lam0, ng = 1.55, 4.2
    lam = np.linspace(1.50, 1.60, 2001)
    fig = plt.figure(figsize=(6.3, 2.6))
    a = fig.add_axes([0.0, 0.0, 0.45, 1.0]); frameless(a, (0, 100), (-9, 62), equal=False)
    y0, dy, SI = 31, 13, dict(color=MAT["si"], lw=2.2, solid_capstyle="butt")
    a.plot([2, 12], [y0, y0], **SI)                                       # input and Y-branch
    for sg in (1, -1):
        xs = np.linspace(12, 24, 30); a.plot(xs, y0 + sg * dy * (1 - np.cos(np.pi * (xs - 12) / 12)) / 2, **SI)
        a.plot([24, 70], [y0 + sg * dy] * 2, **SI)
        xs = np.linspace(70, 80, 30); a.plot(xs, y0 + sg * (dy - (dy - 3) * (1 - np.cos(np.pi * (xs - 70) / 10)) / 2), **SI)
        a.plot([88, 98], [y0 + sg * 3] * 2, **SI)
        box(a, 30, y0 + sg * dy - 3, 26, 6, "#D9C7E8", ec=VIOLET, lw=0.6, z=3)
    box(a, 80, y0 - 6, 8, 12, MAT["si"], z=3); label(a, 84, y0 - 9, "2×2", fs=5.8)
    arrow(a, (33, y0 + dy + 5.5), (53, y0 + dy + 5.5), col=VIOLET, lw=0.8, ms=6)
    arrow(a, (53, y0 - dy - 5.5), (33, y0 - dy - 5.5), col=VIOLET, lw=0.8, ms=6)
    label(a, 43, y0 + dy + 10, "garnet, M →: +π/4 forward, −π/4 back", fs=FS_SMALL, col=VIOLET)
    label(a, 43, y0 - dy - 10, "garnet, M ←: −π/4 forward, +π/4 back", fs=FS_SMALL, col=VIOLET)
    box(a, 60, y0 + dy - 2.5, 7, 5, "tin", z=3)
    callout(a, (63.5, y0 + dy + 2.5), (72, y0 + dy + 14), "reciprocal −π/2", ha="left")
    arrow(a, (2, y0 + 4), (10, y0 + 4), col=RED, lw=1.1, ms=7); label(a, 2, y0 + 8, "in", fs=FS_SMALL, ha="left", col=RED)
    label(a, 99, y0 + 7, "out", fs=FS_SMALL, ha="right", col=RED)
    label(a, 99, y0 - 7, "monitor", fs=FS_SMALL, ha="right", col=MUTED)
    label(a, 50, -1.5, "forward: the arms meet in phase → out", fs=FS_SMALL)
    label(a, 50, -6.0, "backward (from out): in antiphase → radiated at the Y-branch", fs=FS_SMALL)
    panel(a, "a", 0.0, 1.0)
    b = fig.add_axes([0.55, 0.17, 0.43, 0.62])
    for m, col in ((1, C1), (20, C2)):
        nL = (m - 0.25) * lam0                                    # n_eff dL (um) for a reciprocal phase of 2 pi m - pi/2 (n_eff 2.45)
        dphi = 2 * np.pi * (m - 0.25) + 2 * np.pi * (nL / 2.45) * ng * (1 / lam - 1 / lam0)
        Tf = np.cos((dphi + np.pi / 2) / 2) ** 2
        Tb = np.cos((dphi - np.pi / 2) / 2) ** 2
        b.plot(1e3 * lam, 10 * np.log10(Tf + 1e-9), color=col, lw=1.3, label=f"order {m}: forward")
        b.plot(1e3 * lam, 10 * np.log10(Tb + 1e-9), color=col, lw=1.0, ls=(0, (3, 2)), label=f"order {m}: backward")
        iso = 10 * np.log10(Tf + 1e-12) - 10 * np.log10(Tb + 1e-12)
        i0 = int(np.argmin(np.abs(lam - lam0))); i1 = i2 = i0                 # the contiguous window around 1550 nm
        while i1 > 0 and iso[i1 - 1] >= 20: i1 -= 1
        while i2 < len(lam) - 1 and iso[i2 + 1] >= 20: i2 += 1
        print(f"Fig 27.11: order {m}: delta L {1e3 * nL / 2.45:.0f} nm; isolation >= 20 dB from {1e3 * lam[i1]:.1f} to {1e3 * lam[i2]:.1f} nm"
              f" ({1e3 * (lam[i2] - lam[i1]):.1f} nm)")
    b.set_ylim(-40, 2); b.set_xlim(1500, 1600)
    finish(b, "Wavelength (nm)", "Transmission (dB)")
    b.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), fontsize=5.8, ncol=2, handlelength=1.6, borderaxespad=0)
    b.text(-0.12, 1.32, "b", transform=b.transAxes, fontweight="bold", color=INK, fontsize=9.5, ha="right")
    save(fig, "ch27_isolator")



if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1:
        for _n in _s.argv[1:]: globals()['fig_' + _n]()
    else:
        fig_options(); fig_printing(); fig_monolithic(); fig_thermal(); fig_microring()
        fig_hetero(); fig_isolator()
