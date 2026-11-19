"""Figures of Chapter 34 (verification and tape-out).

    python -I -X utf8 figsrc/ch34_figs.py [name ...]

ch34_flow      the verification flow, from the layout to the tape-out package
ch34_rules     twelve kinds of design rule, each drawn with a violation
ch34_engine    how a DRC engine checks: edge pairs, sizing, Euclidean and projection metrics (ch34_engine.json)
ch34_markers   the DRC run of the chapter's deck on its test layout (ch34_geom.json, ch34_drc.json)
ch34_curved    curved geometry on a grid: off-grid ring vertices and the gap ripple of a pulley coupler
               (computed here; counts from ch34_pulley.json)
ch34_connect   SiEPIC-Tools connectivity check of an MZI with three mistakes (ch34_connect.json)
ch34_derive    drawn layers -> mask layers, a trench-style process, and a sliver (ch34_derive.json)
ch34_density   silicon density of a 1 mm die in 100 um windows, before and after dummy fill (ch34_density.json)

The JSON files come from ch34_drc.py, ch34_connect.py and ch34_density.py (KLayout's Python module) and from the
KLayout application running ch34_deck.lydrc; see those files.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from matplotlib.patches import Rectangle, Polygon as MPoly, Circle
from matplotlib.path import Path
from matplotlib.patches import PathPatch

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK_FC, SIGN_FC, PKG_FC = "#EEF3FA", "#FBF3E6", "#EAF4EC"
ERR = RED
SLAB_C, HTR_C, M_C, FP_C = "#D7E3F0", MAT["tin"], "#E9C77F", MUTED


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def draw_poly(ax, hull, holes=(), fc=MAT["si"], ec="none", lw=0.0, z=2, alpha=1.0, **kw):
    """Polygon with holes as a single path (even-odd)."""
    verts, codes = [], []
    for ring in [hull] + list(holes):
        ring = list(ring)
        if not ring:
            continue
        verts += ring + [ring[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(ring) - 1) + [Path.CLOSEPOLY]
    p = PathPatch(Path(verts, codes), fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, **kw)
    ax.add_patch(p)
    return p


def mark_circle(ax, x, y, r, col=ERR, lw=1.0, z=8):
    ax.add_patch(Circle((x, y), r, fill=False, ec=col, lw=lw, zorder=z))


def meets(pts, win):
    """True if the bounding box of pts meets the window ((x0, x1), (y0, y1)); always True without a window."""
    if win is None:
        return True
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    (x0, x1), (y0, y1) = win
    return not (max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1)


def clip_ring(pts, win, pad=0.2):
    """Clip a closed outline to an enlarged window (Sutherland-Hodgman), so a close-up stores only what it shows."""
    if win is None:
        return pts
    (x0, x1), (y0, y1) = win
    dx, dy = (x1 - x0) * pad, (y1 - y0) * pad
    x0, x1, y0, y1 = x0 - dx, x1 + dx, y0 - dy, y1 + dy
    out = list(pts)
    for inside, inter in (
            (lambda q: q[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
            (lambda q: q[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
            (lambda q: q[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
            (lambda q: q[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
        inp, out = out, []
        if not inp:
            break
        prev = inp[-1]
        for cur in inp:
            if inside(cur):
                if not inside(prev):
                    out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(inter(prev, cur))
            prev = cur
    return out


def draw_clipped(ax, hull, holes, win, **kw):
    if not meets(hull, win):
        return
    h = clip_ring(hull, win)
    if len(h) < 3:
        return
    hs = [clip_ring(x, win) for x in holes if meets(x, win)]
    draw_poly(ax, h, [x for x in hs if len(x) >= 3], **kw)


# ------------------------------------------------------------------ Figure 34.1
def fig_flow():
    fig, ax = geom_axes(figsize=(6.3, 3.15), xlim=(0, 10.5), ylim=(-0.05, 5.2), equal=False)
    # the layout
    block(ax, 0.68, 2.55, 1.2, 0.95, "layout\n(GDS or\nOASIS)", fc="#F3F6FB", fs=7.0, bold=True)
    checks = [("design-rule check", "widths, gaps, enclosures,", "angles, grid, density"),
              ("connectivity", "pins meet, widths match,", "no overlapping cells"),
              ("layout vs schematic", "extracted netlist", "= intended circuit"),
              ("design for test", "labels, coupler pitch", "and orientation"),
              ("extracted simulation", "lengths and bends", "as drawn")]
    xc, bw, bh = 2.95, 2.1, 0.8
    ys = [4.55, 3.55, 2.55, 1.55, 0.55]
    for (t, s1, s2), y in zip(checks, ys):
        block(ax, xc, y, bw, bh, "", fc=CHECK_FC)
        label(ax, xc, y + 0.2, t, fs=6.8, bold=True)
        label(ax, xc, y - 0.05, s1, fs=5.6, col=MUTED)
        label(ax, xc, y - 0.24, s2, fs=5.6, col=MUTED)
        ax.plot([1.28, 1.6, 1.6], [2.55, 2.55, y], color=INK, lw=0.8, zorder=1)
        arrow(ax, (1.6, y), (xc - bw / 2 - 0.02, y), lw=0.8, ms=6)
        ax.plot([xc + bw / 2, 4.25, 4.25], [y, y, 2.55], color=INK, lw=0.8, zorder=1)
    # review: clean?
    dx, dy = 4.95, 2.55
    ax.add_patch(MPoly([(dx - 0.6, dy), (dx, dy + 0.55), (dx + 0.6, dy), (dx, dy - 0.55)], closed=True, fc="white", ec=INK, lw=0.8, zorder=3))
    label(ax, dx, dy, "markers\nreviewed", fs=6.2)
    arrow(ax, (4.25, 2.55), (dx - 0.6, dy), lw=0.8, ms=6)
    # fix loop
    ax.plot([dx, dx], [dy - 0.55, -0.0], color=ERR, lw=1.0, zorder=1)
    ax.plot([dx, 0.68], [0.0, 0.0], color=ERR, lw=1.0, zorder=1)
    arrow(ax, (0.68, 0.0), (0.68, 2.55 - 0.48), col=ERR, lw=1.0, ms=7)
    label(ax, 5.1, 0.95, "error: fix the\nlayout, run every\ncheck again", fs=5.8, col=ERR, ha="left")
    # waiver
    label(ax, dx + 0.05, 3.55, "false or intended:\nwaive, with a reason", fs=5.8, col=VIOLET)
    ax.plot([dx, dx], [3.25, dy + 0.55], color=VIOLET, lw=0.6)
    # sign-off and package
    sx, pw, ph = 7.0, 1.65, 2.0
    block(ax, sx, 2.55, pw, ph, "", fc=SIGN_FC)
    label(ax, sx, 3.3, "foundry sign-off", fs=6.8, bold=True)
    for k, t in enumerate(("layer map, derived", "masks and merges", "density and fill", "manufacturing grid", "die size, keep-outs",
                           "the foundry's DRC")):
        label(ax, sx, 3.0 - 0.25 * k, t, fs=5.7, col=MUTED)
    arrow(ax, (dx + 0.6, dy), (sx - pw / 2 - 0.02, 2.55), lw=0.8, ms=6)
    label(ax, (dx + 0.6 + sx - pw / 2) / 2, 2.72, "clean", fs=5.8, col=TEAL)
    px = 9.3
    block(ax, px, 2.55, pw, ph, "", fc=PKG_FC)
    label(ax, px, 3.3, "tape-out package", fs=6.8, bold=True)
    for k, t in enumerate(("GDS or OASIS file", "layer map", "DRC report", "waivers", "design notes", "test plan")):
        label(ax, px, 3.0 - 0.25 * k, t, fs=5.7, col=MUTED)
    arrow(ax, (sx + pw / 2 + 0.02, 2.55), (px - pw / 2 - 0.02, 2.55), lw=0.8, ms=6)
    arrow(ax, (px, 2.55 - ph / 2 - 0.02), (px, 0.95), lw=0.8, ms=6)
    label(ax, px, 0.7, "to the foundry\n(MPW run)", fs=6.2, bold=True)
    label(ax, xc, 5.13, "run by the designer, after every change", fs=6.0, col=MUTED)
    label(ax, (sx + px) / 2, 3.85, "repeated by the foundry or the run's checks", fs=6.0, col=MUTED)
    save(fig, "ch34_flow")


# ------------------------------------------------------------------ Figure 34.2
def fig_rules():
    fig = plt.figure(figsize=(6.3, 4.6))
    names = ["(a) width", "(b) space", "(c) notch", "(d) enclosure", "(e) overlap", "(f) extension",
             "(g) area and holes", "(h) density", "(i) acute angle", "(j) off-grid vertex", "(k) self-intersection",
             "(l) zero-width spike"]
    axs = []
    for k in range(12):
        r, c = divmod(k, 4)
        ax = fig.add_axes([0.005 + c * 0.25, 0.68 - r * 0.33, 0.235, 0.27])
        frameless(ax, (0, 4), (0, 3))
        ax.text(0.0, 3.25, names[k], fontsize=7.2, fontweight="bold", color=INK, ha="left", va="bottom")
        axs.append(ax)
    si = MAT["si"]

    def red_dim(ax, p0, p1, t, off=(0, 0), toff=(0, 0), ha="center"):
        dim(ax, p0, p1, t, off=off, col=ERR, fs=6.0, text_off=toff, ha=ha)

    # (a) width: a waveguide with a narrow neck
    ax = axs[0]
    poly(ax, [(0.1, 1.1), (1.4, 1.1), (1.7, 1.35), (2.3, 1.35), (2.6, 1.1), (3.9, 1.1), (3.9, 1.9), (2.6, 1.9), (2.3, 1.65),
              (1.7, 1.65), (1.4, 1.9), (0.1, 1.9)], "si")
    red_dim(ax, (2.0, 1.35), (2.0, 1.65), "", )
    label(ax, 2.0, 0.65, "w < w$_\\min$", fs=6.3, col=ERR)
    ax.plot([2.0, 2.0], [0.8, 1.3], color=ERR, lw=0.5)
    # (b) space: two waveguides, gap below minimum
    ax = axs[1]
    box(ax, 0.2, 1.62, 3.6, 0.55, "si"); box(ax, 0.2, 0.83, 3.6, 0.55, "si")
    red_dim(ax, (2.0, 1.38), (2.0, 1.62), "")
    label(ax, 2.0, 2.55, "s < s$_\\min$ between shapes", fs=6.3, col=ERR)
    ax.plot([2.0, 2.0], [1.62, 2.4], color=ERR, lw=0.5)
    # (c) notch: one polygon with a slot
    ax = axs[2]
    poly(ax, [(0.4, 0.5), (3.6, 0.5), (3.6, 2.5), (2.15, 2.5), (2.15, 1.1), (1.85, 1.1), (1.85, 2.5), (0.4, 2.5)], "si")
    red_dim(ax, (1.85, 1.9), (2.15, 1.9), "")
    label(ax, 2.0, 2.78, "space inside one shape", fs=6.3, col=ERR)
    # (d) enclosure: slab around a rib core
    ax = axs[3]
    box(ax, 0.3, 0.6, 3.4, 1.65, SLAB_C, ec=MUTED, lw=0.4)
    box(ax, 0.3, 1.25, 3.4, 0.45, "si", z=3)
    label(ax, 3.55, 0.85, "slab", fs=6.0, col=MUTED, ha="right")
    red_dim(ax, (2.6, 1.7), (2.6, 2.25), "")
    label(ax, 2.75, 2.6, "e < e$_\\min$", fs=6.3, col=ERR, ha="left")
    dim(ax, (1.2, 0.6), (1.2, 1.25), "", col=TEAL, fs=6.0)
    label(ax, 1.1, 0.35, "e ≥ e$_\\min$", fs=6.0, col=TEAL, ha="right")
    # (e) overlap: metal pad over the end of a heater
    ax = axs[4]
    box(ax, 0.2, 1.15, 2.7, 0.7, HTR_C, alpha=0.85)
    box(ax, 2.6, 0.6, 1.2, 1.8, M_C, alpha=0.75, ec=MAT["metal"], lw=0.6, z=3)
    label(ax, 1.2, 1.5, "heater", fs=6.0)
    label(ax, 3.2, 2.15, "metal", fs=6.0)
    red_dim(ax, (2.6, 0.95), (2.9, 0.95), "")
    label(ax, 2.0, 0.35, "overlap < o$_\\min$", fs=6.3, col=ERR)
    # (f) extension: a doped region must extend past the end of the waveguide
    ax = axs[5]
    box(ax, 0.3, 0.8, 2.6, 1.4, MAT["pdop"], alpha=0.8)
    box(ax, 0.1, 1.28, 2.75, 0.45, "si", z=3)
    label(ax, 0.9, 2.45, "implant", fs=6.0, col=MUTED)
    red_dim(ax, (2.85, 1.95), (2.9, 1.95), "")
    ax.plot([2.85, 2.85], [1.28, 2.1], color=ERR, lw=0.5, ls=(0, (2, 1)))
    label(ax, 3.0, 2.45, "x < x$_\\min$", fs=6.3, col=ERR)
    # (g) area and holes
    ax = axs[6]
    box(ax, 0.3, 1.25, 0.25, 0.25, "si")
    label(ax, 0.42, 0.85, "A < A$_\\min$", fs=6.0, col=ERR)
    mark_circle(ax, 0.42, 1.37, 0.32, lw=0.8)
    draw_poly(ax, [(1.5, 0.5), (3.8, 0.5), (3.8, 2.5), (1.5, 2.5)], [[(2.5, 1.4), (2.75, 1.4), (2.75, 1.65), (2.5, 1.65)]])
    mark_circle(ax, 2.62, 1.52, 0.32, lw=0.8)
    label(ax, 2.65, 2.78, "hole < A$_\\min$", fs=6.0, col=ERR)
    # (h) density: a window with little silicon
    ax = axs[7]
    rng = np.random.default_rng(3)
    ax.add_patch(Rectangle((0.5, 0.3), 2.6, 2.6, fill=False, ec=INK, lw=0.7, ls=(0, (3, 2))))
    box(ax, 0.5, 1.5, 2.6, 0.12, "si")
    box(ax, 1.8, 0.3, 0.12, 1.2, "si")
    label(ax, 1.8, 2.45, "ρ = A$_\\mathrm{Si}$ / A$_\\mathrm{window}$", fs=6.0)
    label(ax, 3.25, 0.55, "ρ < ρ$_\\min$", fs=6.3, col=ERR, ha="left", rot=90)
    # (i) acute angle: a taper drawn to a point
    ax = axs[8]
    poly(ax, [(0.2, 1.1), (1.0, 1.1), (3.6, 1.5), (1.0, 1.9), (0.2, 1.9)], "si")
    t = np.linspace(-0.15, 0.15, 20)
    ax.plot(3.6 - 0.9 * np.cos(t), 1.5 + 0.9 * np.sin(t), color=ERR, lw=0.7)
    label(ax, 2.55, 2.25, "θ < θ$_\\min$", fs=6.3, col=ERR)
    mark_circle(ax, 3.6, 1.5, 0.22, lw=0.8)
    # (j) off-grid vertex
    ax = axs[9]
    for gx in np.arange(0.5, 4.0, 0.5):
        for gy in np.arange(0.5, 3.0, 0.5):
            ax.plot(gx, gy, "o", ms=1.6, color=MUTED, zorder=5)
    poly(ax, [(0.5, 0.5), (3.0, 0.5), (3.18, 1.77), (0.5, 2.5)], "si", alpha=0.9)
    ax.plot(3.18, 1.77, "o", ms=3.2, color=ERR, zorder=6)
    ax.plot(3.0, 2.0, "o", ms=3.2, mfc="none", mec=TEAL, zorder=6)
    label(ax, 3.3, 1.45, "vertex off\nthe grid", fs=5.8, col=ERR, ha="left")
    # (k) self-intersection: the outline crosses itself
    ax = axs[10]
    pts = [(0.4, 2.0), (3.6, 2.0), (0.4, 1.0), (3.6, 1.0)]
    poly(ax, pts, "si", alpha=0.9)
    ax.plot([p[0] for p in pts + pts[:1]], [p[1] for p in pts + pts[:1]], color=INK, lw=0.6, zorder=4)
    for (x, y), lab in zip(pts, "1234"):
        label(ax, x, y + (0.18 if y > 1.5 else -0.18), lab, fs=5.6, col=MUTED)
    mark_circle(ax, 2.0, 1.5, 0.25, lw=0.8)
    label(ax, 2.0, 0.45, "edges 2→3 and 4→1 cross", fs=6.0, col=ERR)
    # (l) zero-width spike
    ax = axs[11]
    poly(ax, [(0.4, 0.8), (3.6, 0.8), (3.6, 1.6), (2.0, 1.6), (2.0, 2.6), (2.0, 1.6), (0.4, 1.6)], "si")
    ax.plot([2.0, 2.0], [1.6, 2.6], color=INK, lw=0.9, zorder=4)
    mark_circle(ax, 2.0, 2.1, 0.55, lw=0.8)
    label(ax, 2.0, 0.45, "out and back: no area", fs=6.0, col=ERR)
    save(fig, "ch34_rules")


# ------------------------------------------------------------------ Figure 34.3
def edge_pair_poly(ep):
    (a, b) = ep
    return [(a[0], a[1]), (a[2], a[3]), (b[0], b[1]), (b[2], b[3])]


def fig_engine():
    d = load("ch34_engine.json")
    fig = plt.figure(figsize=(6.3, 2.05))
    ax1 = fig.add_axes([0.0, 0.0, 0.33, 0.84]); frameless(ax1, (-0.15, 3.15), (-0.45, 1.25))
    ax2 = fig.add_axes([0.34, 0.0, 0.33, 0.84]); frameless(ax2, (-0.15, 3.15), (-0.45, 1.25))
    ax3 = fig.add_axes([0.69, 0.0, 0.31, 0.84]); frameless(ax3, (-0.15, 2.95), (-0.95, 1.25))
    for x, t in ((0.0, "(a) edge pairs"), (0.34, "(b) sizing"), (0.69, "(c) metrics")):
        fig.text(x, 0.93, t, fontsize=7.5, fontweight="bold", color=INK, va="bottom")
    # (a) the edges and the width-check edge pair on the neck
    for p in d["bone"]:
        draw_poly(ax1, p, fc=MAT["si"])
        pts = p + [p[0]]
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            ax1.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.6, mutation_scale=5), zorder=4)
    for ep in d["width_pairs"]:
        draw_poly(ax1, edge_pair_poly(ep), fc="none", ec=ERR, lw=1.2, z=6)
    label(ax1, 1.5, -0.17, "neck 120 nm: one edge pair < 150 nm", fs=6.0, col=ERR)
    label(ax1, 1.5, -0.36, "edges run clockwise; inside on the right", fs=5.7, col=MUTED)
    # (b) shrink by 75 nm, grow by 75 nm, compare
    for p in d["bone"]:
        draw_poly(ax2, p, fc="none", ec=INK, lw=0.6, ls=(0, (3, 2)), z=3)
    for p in d["shrunk"]:
        draw_poly(ax2, p, fc=MAT["si"], z=2)
    for p in d["narrow"]:
        draw_poly(ax2, p, fc=ERR, z=4)
    label(ax2, 1.5, -0.17, "shrink by w/2, grow back: the neck is lost", fs=6.0)
    label(ax2, 1.5, -0.36, "original − regrown = parts narrower than w", fs=6.0, col=ERR)
    # (c) Euclidean vs projection metrics
    for p in d["rects"]:
        draw_poly(ax3, p, fc=MAT["si"])
    for ep in d["space_euclid"]:
        draw_poly(ax3, edge_pair_poly(ep), fc="none", ec=ERR, lw=1.0, z=6)
    for ep in d["space_proj"]:
        draw_poly(ax3, edge_pair_poly(ep), fc="none", ec=BLUE, lw=1.0, ls=(0, (2, 1)), z=7)
    label(ax3, 1.2, 0.2, "corner to corner: 141 nm,\nEuclidean only", fs=5.8, col=ERR, ha="left")
    label(ax3, 1.15, -0.4, "face to face: 150 nm,\nboth metrics", fs=5.8, col=INK, ha="left")
    ax3.plot([0.05, 0.3], [-0.85, -0.85], color=ERR, lw=1.0); label(ax3, 0.36, -0.85, "Euclidean", fs=5.8, ha="left")
    ax3.plot([1.25, 1.5], [-0.85, -0.85], color=BLUE, lw=1.0, ls=(0, (2, 1))); label(ax3, 1.56, -0.85, "projection", fs=5.8, ha="left")
    save(fig, "ch34_engine")


# ------------------------------------------------------------------ Figure 34.4
def draw_layout(ax, g, lw_fp=0.7, win=None):
    if win is None:
        for p in g["fp"]:
            h = p["hull"] + [p["hull"][0]]
            ax.plot([q[0] for q in h], [q[1] for q in h], color=FP_C, lw=lw_fp, ls=(0, (4, 2)), zorder=1)
    for p in g["slab"]:
        draw_clipped(ax, p["hull"], p["holes"], win, fc=SLAB_C, ec=MUTED, lw=0.3, z=1)
    for p in g["si"]:
        draw_clipped(ax, p["hull"], p["holes"], win, fc=MAT["si"], z=2)
    for p in g["htr"]:
        draw_clipped(ax, p["hull"], p["holes"], win, fc=HTR_C, z=3, alpha=0.75)
    for p in g["m"]:
        draw_clipped(ax, p["hull"], p["holes"], win, fc=M_C, ec=MAT["metal"], lw=0.4, z=4, alpha=0.7)


def draw_markers(ax, drc, rules=None, lw=0.8, dot=1.2, win=None):
    for rule, v in drc.items():
        if rules and rule not in rules:
            continue
        for m in v["markers"]:
            xy = m["xy"]
            pts = list(zip(xy[0::2], xy[1::2]))
            if not meets(pts, win):
                continue
            if m["kind"] == "edge-pair":
                if len(set(pts)) == 1:
                    ax.plot(pts[0][0], pts[0][1], "o", ms=dot, color=ERR, zorder=9)
                else:
                    draw_poly(ax, pts, fc=ERR, ec=ERR, lw=lw, z=9, alpha=0.55)
            else:
                draw_poly(ax, pts, fc=ERR, ec=ERR, lw=lw, z=9, alpha=0.45)


def fig_markers():
    g = load("ch34_geom.json")
    drc = load("ch34_drc.json")
    fig = plt.figure(figsize=(6.3, 5.25))
    ax = fig.add_axes([0.0, 0.31, 1.0, 0.68]); frameless(ax, (-1.5, 97.5), (-1.0, 60.5))
    draw_layout(ax, g)
    draw_markers(ax, drc, lw=0.6)
    ax.text(0.0, 1.0, "(a)", transform=ax.transAxes, fontsize=8.5, fontweight="bold", color=INK, va="top")
    feats = {f[0].split()[0]: (f[1], f[2]) for f in g["features"]}
    clean = ("A1", "A4", "B1")
    # (feature, text, label position, ha)
    calls = [("A2", "SI.W.1", (26, 55.3), "center"), ("A3", "SI.W.1\nSI.ANG.1", (43.5, 56.2), "center"),
             ("A5", "SI.FP.1", (92.5, 55.3), "center"),
             ("B2", "SI.S.1", (28, 43.2), "center"), ("B3", "SI.N.1 ×18", (42.6, 43.2), "center"),
             ("B4", "SI.A.1", (51.5, 36.6), "center"), ("B5", "SI.ODD.1 ×1, SI.W.1 ×6,\nSI.N.1 ×4, SI.ANG.1 ×4", (63.0, 43.6), "left"),
             ("C1", "SI.GRID.1 ×272", (12, 25.3), "center"), ("C2", "SI.S.1 ×58\nSI.W.1 ×2", (52.0, 14.5), "left"),
             ("D1", "SLAB.EN.1", (82.0, 4.0), "left"), ("D2", "M.OV.1", (84.0, 14.3), "center")]
    for f, t, (lx, ly), ha in calls:
        label(ax, lx, ly, t, fs=6.4, col=ERR, ha=ha, va="center")
    for k, (x, y) in feats.items():
        dy = -2.0 if k[0] in "AB" else 0
        if k in ("C1", "C2"):
            label(ax, x, y, k, fs=6.6, col=MUTED, bold=True)
        elif k in ("D1",):
            label(ax, 58.0, 4.0, k, fs=6.6, col=MUTED, bold=True, ha="right")
        elif k in ("D2",):
            label(ax, 57.0, 10.0, k, fs=6.6, col=MUTED, bold=True, ha="right")
        else:
            label(ax, x, y + dy, k, fs=6.6, col=TEAL if k in clean else MUTED, bold=True)
    for k in clean:
        x, y = feats[k]
        label(ax, x, y - 3.6, "clean", fs=6.2, col=TEAL)
    label(ax, 89.5, 57.0, "floorplan", fs=5.8, col=MUTED, ha="right")
    ax.annotate("", xy=(40.0, 12.4), xytext=(51.6, 14.5), arrowprops=dict(arrowstyle="-", color=ERR, lw=0.5))
    ax.annotate("", xy=(59.0, 40.6), xytext=(62.8, 43.0), arrowprops=dict(arrowstyle="-", color=ERR, lw=0.5))
    scalebar(ax, 2.0, 1.0, 10.0, "10 µm")
    # close-ups
    zooms = [("(b) C2: gap at the 200 nm minimum", (38.4, 41.6), (11.75, 12.95)),
             ("(c) B3: grating notches", (40.75, 42.75), (39.55, 40.45)),
             ("(d) B5: the outline crosses itself", (55.7, 59.3), (39.45, 40.55))]
    for k, (t, xl, yl) in enumerate(zooms):
        a = fig.add_axes([0.005 + k * 0.335, 0.0, 0.32, 0.26]); frameless(a, xl, yl)
        draw_layout(a, g, win=(xl, yl))
        draw_markers(a, drc, lw=0.6, win=(xl, yl))
        a.add_patch(Rectangle((xl[0], yl[0]), xl[1] - xl[0], yl[1] - yl[0], fill=False, ec=MUTED, lw=0.6, zorder=10))
        fig.text(0.005 + k * 0.335, 0.265, t, fontsize=7.0, fontweight="bold", color=INK, va="bottom")
        span = xl[1] - xl[0]
        sb = 0.5 if span > 2.5 else 0.2
        scalebar(a, xl[0] + 0.05 * span, yl[0] + 0.06 * (yl[1] - yl[0]), sb, f"{int(sb * 1000)} nm")
    save(fig, "ch34_markers")


# ------------------------------------------------------------------ Figure 34.5
def ring_pts(cx, cy, r, step, a0=0.0, a1=360.0):
    n = int(round((a1 - a0) / step))
    full = abs((a1 - a0) - 360.0) < 1e-9
    ks = np.arange(n) if full else np.arange(n + 1)
    a = np.radians(a0 + ks * step)
    return np.c_[cx + r * np.cos(a), cy + r * np.sin(a)]


def q(pts, g):
    """Round coordinates (um) to a grid g (um) -- exactly as integer multiples of g, as a layout would store them."""
    return np.round(pts / g) * g


def seg_dist(p, a, b):
    """Distance from points p (N,2) to segments a->b (M,2); returns (N,) minimum over segments."""
    ab = b - a
    t = np.clip(((p[:, None, :] - a[None]) * ab[None]).sum(-1) / (ab * ab).sum(-1)[None], 0, 1)
    proj = a[None] + t[..., None] * ab[None]
    return np.sqrt(((p[:, None, :] - proj) ** 2).sum(-1)).min(1)


def pulley_gap(g, R=5.0, w=0.5, gap=0.2, sr=2.5, sb=1.0, ring_only=False):
    cx, cy = 40.0, 12.0 + 0.25 + gap + R + w / 2
    ro = ring_pts(cx, cy, R + w / 2, sr)
    bi = ring_pts(cx, cy, R + w / 2 + gap, sb, 225, 315)
    if g:
        ro, bi = q(ro, g), q(bi, g)
    ro_closed = np.vstack([ro, ro[:1]])
    # ring vertices under the bus, distance to the bus edge; bus vertices, distance to the ring edge
    ang_r = (np.degrees(np.arctan2(ro[:, 1] - cy, ro[:, 0] - cx)) + 360) % 360
    sel = (ang_r > 226) & (ang_r < 314)
    d1 = seg_dist(ro[sel], bi[:-1], bi[1:])
    if ring_only:
        return ang_r[sel], d1 * 1000
    d2 = seg_dist(bi[1:-1], ro_closed[:-1], ro_closed[1:])
    ang_b = (np.degrees(np.arctan2(bi[1:-1, 1] - cy, bi[1:-1, 0] - cx)) + 360) % 360
    a = np.r_[ang_r[sel], ang_b]; d = np.r_[d1, d2]
    o = np.argsort(a)
    return a[o], d[o] * 1000


def fig_curved():
    pul = load("ch34_pulley.json")
    g = load("ch34_geom.json")
    drc = load("ch34_drc.json")
    R, w, GR = 5.0, 0.5, 0.005
    c1 = g["rings"]["C1"]
    pts = np.vstack([ring_pts(c1["cx"], c1["cy"], R + w / 2, 2.5), ring_pts(c1["cx"], c1["cy"], R - w / 2, 2.5)])
    pts_nm = np.round(pts * 1000).astype(int)                    # 1 nm database unit
    off = (pts_nm[:, 0] % 5 != 0) | (pts_nm[:, 1] % 5 != 0)
    n_off = int(off.sum())
    assert n_off == len(drc["SI.GRID.1"]["markers"]), (n_off, len(drc["SI.GRID.1"]["markers"]))
    fig = plt.figure(figsize=(6.3, 2.75))
    # (a) the ring, on- and off-grid vertices
    ax = fig.add_axes([0.0, 0.02, 0.27, 0.86]); frameless(ax, (c1["cx"] - 5.6, c1["cx"] + 5.6), (c1["cy"] - 5.6, c1["cy"] + 5.6))
    for p in g["si"]:
        if abs(np.mean([h[0] for h in p["hull"]]) - c1["cx"]) < 3 and abs(np.mean([h[1] for h in p["hull"]]) - c1["cy"]) < 3:
            draw_poly(ax, p["hull"], p["holes"], fc=MAT["si"])
    ax.plot(pts[off, 0], pts[off, 1], "o", ms=1.6, color=ERR, zorder=5, lw=0)
    ax.plot(pts[~off, 0], pts[~off, 1], "o", ms=3.0, mfc="white", mec=TEAL, mew=0.9, zorder=6, lw=0)
    fig.text(0.0, 0.93, "(a) ring C1, 288 vertices", fontsize=7.5, fontweight="bold", color=INK)
    label(ax, c1["cx"], c1["cy"] + 0.8, f"{n_off} off the\n5 nm grid", fs=6.0, col=ERR)
    label(ax, c1["cx"], c1["cy"] - 0.9, f"{len(pts) - n_off} on it", fs=6.0, col=TEAL)
    # (b) one vertex, its 1 nm and 5 nm grids
    k = 5                                                         # the 6th outer vertex, at 12.5 degrees
    v = pts[k]; vn = pts_nm[k] / 1000.0
    ax = fig.add_axes([0.285, 0.1, 0.2, 0.74])
    x0, y0 = np.floor(vn[0] * 200) / 200 - 0.005, np.floor(vn[1] * 200) / 200 - 0.005
    frameless(ax, (x0, x0 + 0.02), (y0, y0 + 0.02))
    for xx in np.arange(x0, x0 + 0.0201, 0.001):
        ax.plot([xx, xx], [y0, y0 + 0.02], color=GRID, lw=0.4, zorder=1)
        ax.plot([x0, x0 + 0.02], [xx - x0 + y0, xx - x0 + y0], color=GRID, lw=0.4, zorder=1)
    for xx in np.arange(x0, x0 + 0.0201, 0.005):
        ax.plot([xx, xx], [y0, y0 + 0.02], color=MUTED, lw=0.7, zorder=2)
        ax.plot([x0, x0 + 0.02], [xx - x0 + y0, xx - x0 + y0], color=MUTED, lw=0.7, zorder=2)
    vs = np.round(vn / GR) * GR
    ax.plot(*v, "x", ms=5, color=INK, zorder=6)
    ax.plot(*vn, "o", ms=4.5, color=ERR, zorder=7)
    ax.plot(*vs, "o", ms=5, mfc="white", mec=TEAL, mew=1.2, zorder=7)
    arrow(ax, tuple(vn), tuple(vs), col=TEAL, lw=0.8, ms=6, z=8)
    fig.text(0.29, 0.93, "(b) one vertex, 20 × 20 nm", fontsize=7.5, fontweight="bold", color=INK)
    ax.text(0.5, -0.05, "×: exact   ●: stored (1 nm)   ○: snapped (5 nm)", transform=ax.transAxes, fontsize=5.6, color=INK, ha="center", va="top")
    # (c) the gap along the pulley coupler, at each ring vertex under the bus (the closest points)
    ax = fig.add_axes([0.575, 0.17, 0.415, 0.66])
    mins = {}
    for gg, col, lab, mk in ((0, MUTED, "exact", None), (0.001, BLUE, "1 nm grid", "o"), (0.005, ERR, "5 nm grid", "s")):
        a, d = pulley_gap(gg, ring_only=True)
        ax.plot(a, d, color=col, lw=0.9, label=lab, marker=mk, ms=2.2)
        mins[gg] = d.min()
    ax.axhline(200, color=INK, lw=0.8, ls=(0, (4, 2)))
    ax.axhline(198, color=MUTED, lw=0.7, ls=(0, (1, 1.5)))
    ax.text(227, 200.08, "rule 200 nm", fontsize=6.0, color=INK, ha="left", va="bottom",
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))
    ax.text(227, 197.92, "2 nm tolerance", fontsize=6.0, color=MUTED, ha="left", va="top",
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))
    ax.set_xlim(226, 314); ax.set_ylim(197.0, 202.5)
    finish(ax, xlabel="angle around the ring (°)", ylabel="gap at a ring vertex (nm)")
    ax.legend(loc="lower left", fontsize=6.0, ncol=3, handlelength=1.6, columnspacing=0.9, bbox_to_anchor=(0.0, 1.0),
              borderaxespad=0.2)
    print("pulley minimum gap (nm): exact %.2f, 1 nm %.2f, 5 nm %.2f" % (mins[0], mins[0.001], mins[0.005]))
    fig.text(0.53, 0.93, "(c)", fontsize=7.5, fontweight="bold", color=INK)
    save(fig, "ch34_curved")


# ------------------------------------------------------------------ Figure 34.6
def pin_poly(pin):
    (x0, y0), (x1, y1) = pin["pts"][0], pin["pts"][-1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * pin["width"] / 2, dx / L * pin["width"] / 2
    return [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]


def draw_circuit(ax, r, devrec=True, pins=True, lw_dev=0.5, win=None):
    for p in r["si"]:
        draw_clipped(ax, p["hull"], p["holes"], win, fc=MAT["si"], z=2)
    for c in r["components"]:
        if devrec and c["devrec"] and meets(c["devrec"], win):
            h = clip_ring(c["devrec"], win, pad=0.05) if win else c["devrec"]
            if win:
                ax.add_patch(MPoly(h, closed=True, fill=False, ec=MUTED, lw=lw_dev, ls=(0, (3, 2)), zorder=3))
            else:
                h = h + [h[0]]
                ax.plot([q[0] for q in h], [q[1] for q in h], color=MUTED, lw=lw_dev, ls=(0, (3, 2)), zorder=3)
        if pins:
            for pin in c["pins"]:
                if not meets(pin["pts"], win):
                    continue
                col = TEAL if pin["net"] is not None else ERR
                draw_poly(ax, pin_poly(pin), fc=col, ec=col, lw=0.4, z=6, alpha=0.85)


def fig_connect():
    d = load("ch34_connect.json")
    fig = plt.figure(figsize=(6.3, 3.6))
    # (a) the MZI as routed
    ax = fig.add_axes([0.0, 0.0, 0.33, 0.92]); frameless(ax, (-12, 116), (5, 176))
    draw_circuit(ax, d["good"], pins=False)
    for c in d["good"]["components"]:
        for pin in c["pins"]:
            ax.plot(*pin["pts"][0], "o", ms=2.2, color=TEAL, zorder=7)
    fig.text(0.0, 0.95, "(a) MZI test circuit, 8 cells", fontsize=7.5, fontweight="bold", color=INK)
    label(ax, 10, 33, "GC", fs=6.0, col=MUTED); label(ax, 10, 160, "GC", fs=6.0, col=MUTED)
    label(ax, 57.4, 37.0, "Y1", fs=6.0, col=MUTED); label(ax, 66.5, 166.0, "Y2", fs=6.0, col=MUTED)
    for (x, y, k) in ((50, 157, "1"), (40, 30, "2"), (104.8, 95, "3")):
        mark_circle(ax, x, y, 5.5, lw=0.9)
        label(ax, x + 8.5, y + 5.5, k, fs=7.0, col=ERR, bold=True)
    scalebar(ax, -8, 9, 20, "20 µm")
    # zooms
    rows = [("nudge", "(b) 1: Y2 moved 50 nm after routing", (49.35, 50.65), (156.55, 157.6)),
            ("width", "(c) 2: input routed as a 350 nm waveguide", (47.6, 51.6), (29.45, 30.55)),
            ("overlap", "(d) 3: a stray Y-branch on the long arm", (94.0, 114.0), (89.5, 100.5))]
    notes = {"nudge": "SiEPIC-Tools: 6 disconnected pins and, since the\ncircuit no longer reaches the labelled coupler,\n‘opt_in label: missing’. Netlist: 5 of 8 nets.\nDRC: no width or space error.",
             "width": "SiEPIC-Tools: 2 mismatched pins\n(‘Pin widths: 500, 350’). Netlist: 8 of 8 nets.\nDRC: no width or space error.",
             "overlap": "SiEPIC-Tools: 1 overlapping component\nand the stray cell’s 3 disconnected pins.\nDRC: 5 space errors where the silicon\nof the two cells comes too close."}
    for k, (v, t, xl, yl) in enumerate(rows):
        y0 = 0.655 - k * 0.325
        a = fig.add_axes([0.355, y0, 0.3, 0.255]); frameless(a, xl, yl)
        r = d[v]
        draw_circuit(a, r, lw_dev=0.7, win=(xl, yl))
        for cat, items in r["error_boxes"].items():
            if "Overlapping" in cat:
                for it in items:
                    for b in it["boxes"]:
                        a.add_patch(Rectangle((b[0], b[1]), b[2] - b[0], b[3] - b[1], fc=ERR, ec=ERR, alpha=0.35, lw=0.6, zorder=5))
        a.add_patch(Rectangle((xl[0], yl[0]), xl[1] - xl[0], yl[1] - yl[0], fill=False, ec=MUTED, lw=0.6, zorder=10))
        fig.text(0.355, y0 + 0.262, t, fontsize=7.0, fontweight="bold", color=INK)
        fig.text(0.675, y0 + 0.215, notes[v], fontsize=6.1, color=INK, va="top", linespacing=1.35)
        span = xl[1] - xl[0]
        sb = {"nudge": 0.2, "width": 0.5, "overlap": 5.0}[v]
        scalebar(a, xl[0] + 0.05 * span, yl[0] + 0.07 * (yl[1] - yl[0]), sb, f"{int(sb * 1000)} nm" if sb < 1 else f"{sb:g} µm")
        if v == "nudge":
            dim(a, (50.45, 157.25), (50.45, 157.30), "", col=ERR, fs=6.0)
            label(a, 50.52, 157.36, "50 nm", fs=6.0, col=ERR, ha="left")
    # legend
    ax.plot(36, 19, "s", ms=4, color=TEAL); label(ax, 39, 19, "pin on a net", fs=5.8, ha="left")
    ax.plot(76, 19, "s", ms=4, color=ERR); label(ax, 79, 19, "pin left open", fs=5.8, ha="left")
    ax.plot([34.5, 37.5], [11, 11], color=MUTED, lw=0.6, ls=(0, (3, 2))); label(ax, 39, 11, "DevRec outline", fs=5.8, ha="left")
    save(fig, "ch34_connect")


# ------------------------------------------------------------------ Figure 34.7
def fig_derive():
    d = load("ch34_derive.json")
    fig = plt.figure(figsize=(6.3, 3.3))
    W_, H_ = 40.0, 14.0
    panels = [("(a) drawn: core and slab", 0.0, 0.52), ("(b) derived: full and shallow etch", 0.505, 0.52),
              ("(c) trench-style alternative", 0.0, 0.03), ("(d) the two slivers, close up", 0.505, 0.03)]
    axs = []
    for t, x, y in panels:
        a = fig.add_axes([x, y, 0.49, 0.4])
        fig.text(x, y + 0.405, t, fontsize=7.3, fontweight="bold", color=INK)
        axs.append(a)
    for a in axs[:3]:
        frameless(a, (-0.5, W_ + 0.5), (-0.5, H_ + 0.5))
        a.add_patch(Rectangle((0, 0), W_, H_, fill=False, ec=MUTED, lw=0.5, zorder=8))
    a = axs[0]
    for p in d["slab"]:
        draw_poly(a, p["hull"], p["holes"], fc=SLAB_C, ec=MUTED, lw=0.4, z=2)
    for p in d["core"]:
        draw_poly(a, p["hull"], p["holes"], fc=MAT["si"], z=3)
    label(a, 22, 4.0 + 2.6, "slab (kept 90 nm)", fs=5.8, col=MUTED)
    label(a, 34, 13.2, "slab drawn by hand", fs=5.8, col=MUTED)
    label(a, 3.0, 11.6, "core (strip)", fs=5.8); label(a, 3.0, 5.2, "core (rib)", fs=5.8)
    a = axs[1]
    for p in d["core"]:
        draw_poly(a, p["hull"], p["holes"], fc=MAT["si"], z=1)
    for p in d["full_etch"]:
        draw_poly(a, p["hull"], p["holes"], fc="#5E6B80", z=2, alpha=0.85)
    for p in d["shallow"]:
        draw_poly(a, p["hull"], p["holes"], fc="#A9B6C9", z=3)
    label(a, 20, 1.0, "full etch = window − (core + slab)", fs=5.8, col="white")
    label(a, 22, 6.6, "shallow = slab − core", fs=5.8, col=INK, bg="white")
    a = axs[2]
    a.add_patch(Rectangle((0, 0), W_, H_, fc=MAT["si"], alpha=0.45, ec="none", zorder=1))
    for p in d["trench"]:
        draw_poly(a, p["hull"], p["holes"], fc="#5E6B80", z=2, alpha=0.85)
    for p in d["core"]:
        draw_poly(a, p["hull"], p["holes"], fc=MAT["si"], z=3)
    label(a, 20, 7.25, "etch = (core sized by 2 µm) − core; the rest stays silicon", fs=5.8, col=INK, bg="white")
    # (d) close-ups of the slivers: taper start (shallow etch) and the 5 nm gap (full etch), stretched vertically
    a = axs[3]; a.set_axis_off()
    s1 = fig.add_axes([0.505, 0.06, 0.225, 0.33]); frameless(s1, (5.8, 7.2), (3.55, 4.45))
    s2 = fig.add_axes([0.765, 0.06, 0.225, 0.33]); frameless(s2, (29.6, 31.0), (10.70, 10.80), equal=False)
    for ss in (s1, s2):
        for p in d["slab"]:
            draw_poly(ss, p["hull"], p["holes"], fc=SLAB_C, ec=MUTED, lw=0.4, z=2)
        for p in d["core"]:
            draw_poly(ss, p["hull"], p["holes"], fc=MAT["si"], z=3)
        for p in d["narrow"]:
            draw_poly(ss, p["hull"], p["holes"], fc=ERR, z=5, alpha=0.8)
        xl, yl = ss.get_xlim(), ss.get_ylim()
        ss.add_patch(Rectangle((xl[0], yl[0]), xl[1] - xl[0], yl[1] - yl[0], fill=False, ec=MUTED, lw=0.6, zorder=10))
    label(s1, 6.5, 4.39, "slab taper starts at the core width:", fs=5.5, col=ERR, bg="white")
    label(s1, 6.5, 3.61, f"two knife edges, {d['knife_len'] * 1000:.0f} nm long", fs=5.5, col=ERR, bg="white")
    label(s2, 30.3, 10.792, "slab 5 nm from the core:", fs=5.5, col=ERR, bg="white")
    label(s2, 30.3, 10.708, "a 5 nm line in the full etch", fs=5.5, col=ERR, bg="white")
    fw, fh = fig.get_size_inches()
    ex = (0.33 * fh / 0.10) / (0.225 * fw / 1.4)
    s2.text(1.0, -0.04, f"vertical scale × {ex:.0f}", transform=s2.transAxes, fontsize=5.4, color=MUTED, style="italic", ha="right", va="top")
    scalebar(s1, 6.75, 3.7, 0.2, "200 nm")
    scalebar(s2, 30.65, 10.73, 0.2, "200 nm")
    save(fig, "ch34_derive")


# ------------------------------------------------------------------ Figure 34.8
def fig_density():
    d = load("ch34_density.json")
    fig = plt.figure(figsize=(6.3, 3.0))
    # (a) the die
    ax = fig.add_axes([0.0, 0.02, 0.28, 0.84]); frameless(ax, (-10, 1010), (-10, 1010))
    ax.add_patch(Rectangle((0, 0), 1000, 1000, fill=False, ec=MUTED, lw=0.6))
    for p in d["si"]:
        draw_poly(ax, p["hull"], p["holes"], fc=INK, ec=INK, lw=0.3, z=2)
    for p in d["gc"]:
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        ax.add_patch(Rectangle((min(xs) - 10, min(ys) - 10), max(xs) - min(xs) + 20, max(ys) - min(ys) + 20, fc=AMBER, alpha=0.35, ec="none", zorder=1))
    ax.add_patch(Rectangle((0, 150), 160, 190, fill=False, ec=BLUE, lw=0.7, zorder=4))
    fig.text(0.0, 0.92, "(a) 1 mm die, Si 1.2 %", fontsize=7.5, fontweight="bold", color=INK)
    scalebar(ax, 20, 25, 200, "200 µm")
    # (b) close-up of fill around a coupler and the loopback
    a = fig.add_axes([0.285, 0.02, 0.18, 0.84]); frameless(a, (0, 160), (150, 340))
    verts, codes = [], []
    for p in d["fill_zoom"]:
        if not (p[0][0] < 160 and p[0][1] > 150 and p[0][1] < 340):
            continue
        verts += list(p) + [p[0]]; codes += [Path.MOVETO] + [Path.LINETO] * (len(p) - 1) + [Path.CLOSEPOLY]
    a.add_patch(PathPatch(Path(verts, codes), fc=MUTED, ec="none", alpha=0.75, zorder=2))
    for p in d["si"]:
        xs = [q[0] for q in p["hull"]]; ys = [q[1] for q in p["hull"]]
        if min(xs) < 160 and min(ys) < 340 and max(ys) > 150:
            draw_clipped(a, p["hull"], p["holes"], ((0, 160), (150, 340)), fc=INK, ec=INK, lw=0.4, z=3)
    a.add_patch(Rectangle((0, 150), 160, 190, fill=False, ec=BLUE, lw=0.7, zorder=4))
    scalebar(a, 8, 156, 50, "50 µm")
    fig.text(0.29, 0.92, "(b) fill, close up", fontsize=7.5, fontweight="bold", color=INK)
    # (c), (d) density maps
    n = len(d["map_before"])
    cen = d["win"] / 2 + d["step"] * np.arange(n)
    ext = (cen[0] - d["step"] / 2, cen[-1] + d["step"] / 2, cen[0] - d["step"] / 2, cen[-1] + d["step"] / 2)
    cmap = plt.get_cmap("viridis")
    for k, (key, t) in enumerate((("map_before", "(c) before fill"), ("map_after", "(d) after fill"))):
        m = np.array(d[key]) * 100
        a = fig.add_axes([0.56 + k * 0.205, 0.12, 0.18, 0.72])
        im = a.imshow(m, origin="lower", extent=ext, cmap=cmap, vmin=0, vmax=35, interpolation="nearest")
        a.contour(cen, cen, m, levels=[20], colors=[ERR], linewidths=0.9)
        a.set_xticks([0, 500, 1000]); a.set_yticks([0, 500, 1000])
        a.tick_params(labelsize=6.5); a.grid(False)
        if k:
            a.set_yticklabels([])
        a.set_xlabel("x (µm)", fontsize=6.8)
        if not k:
            a.set_ylabel("y (µm)", fontsize=6.8)
        st = d["before" if k == 0 else "after"]
        fig.text(0.56 + k * 0.205, 0.92, t, fontsize=7.5, fontweight="bold", color=INK)
        fig.text(0.56 + k * 0.205, 0.865, f"{st['below']} of {st['n']} windows < 20 %", fontsize=6.0, color=ERR)
    cax = fig.add_axes([0.955, 0.12, 0.012, 0.72])
    cb = fig.colorbar(im, cax=cax); cb.ax.tick_params(labelsize=6.0); cb.set_label("Si density in a 100 µm window (%)", fontsize=6.3)
    save(fig, "ch34_density")


FIGS = dict(flow=fig_flow, rules=fig_rules, engine=fig_engine, markers=fig_markers, curved=fig_curved,
            connect=fig_connect, derive=fig_derive, density=fig_density)

if __name__ == "__main__":
    which = sys.argv[1:] or list(FIGS)
    for w in which:
        FIGS[w]()
