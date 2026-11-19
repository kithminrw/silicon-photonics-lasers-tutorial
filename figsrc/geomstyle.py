"""geomstyle.py -- shared helpers for the device drawings (cross-sections, top views, ray and level diagrams,
block diagrams). Use together with figstyle:

    from figstyle import *
    from geomstyle import *
    fig, ax = geom_axes(figsize=(6.3, 2.4), xlim=(-3, 3), ylim=(-1, 1.5))    # equal aspect, no frame
    box(ax, -3, -1, 6, 1, "ox"); box(ax, -0.25, 0, 0.5, 0.22, "si")
    dim(ax, (-0.25, 0.35), (0.25, 0.35), "500 nm")
    scalebar(ax, 2.0, -0.8, 1.0, "1 µm")
    save(fig, "ch06_geometries")          # -> assets/figs/ch06_geometries.svg (+ a PNG preview if $FIGPREVIEW is set)

Material colours match the ones already used in ch04_xsections.svg and the demos' BD.GEO palette, so a material
looks the same in every figure. Figures are drawn for paper (dark text, transparent background); the site puts
them on a white card in the dark theme, so never draw white text on a transparent background.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, FancyBboxPatch, Circle, Ellipse, Wedge
from matplotlib.colors import LinearSegmentedColormap
from figstyle import INK, TEAL, BLUE, AMBER, RED, VIOLET, MUTED, GRID, FIGDIR

# ------------------------------------------------------------------ materials
MAT = {
    "si": "#9DB3CC",        # crystalline silicon (core, slab, substrate)
    "sub": "#C9D3DF",       # silicon handle wafer (lighter, so the device layer stands out)
    "ox": "#DCE9F7",        # SiO2 (BOX, cladding)
    "oxtop": "#EAF2FB",     # upper (deposited) oxide cladding, a shade lighter than the BOX
    "sin": "#E0B060",       # silicon nitride
    "ln": "#EE9AAA",        # lithium niobate
    "bto": "#B8A8E0",       # barium titanate
    "inp": "#C9C2B0",       # InP
    "q": "#8E7F5A",         # InGaAsP / InGaAs / MQW active region
    "mqw": "#B5473A",       # quantum wells drawn as lines (RED)
    "gaas": "#E3E7EE",      # GaAs
    "ge": "#7E8794",        # germanium
    "metal": "#C98A1C",     # contacts, pads, electrodes (AMBER)
    "al": "#B9BFC9",        # aluminium / copper interconnect when it must differ from contact metal
    "tin": "#E08A3A",       # TiN / doped-Si heater
    "pdop": "#F2B8B0",      # p-doped silicon (light)
    "pp": "#E07A6E",        # p++ silicon
    "ndop": "#B9D3F0",      # n-doped silicon (light)
    "nn": "#6F9BD8",        # n++ silicon
    "intr": "#9DB3CC",      # intrinsic / undoped silicon (same as si)
    "poly": "#B4C7A1",      # polysilicon
    "air": "#FFFFFF",
    "water": "#D4ECF4",     # aqueous cladding (sensors)
    "polymer": "#E6DDF2",   # polymer (photonic wire bonds, overlays, epoxy)
    "epoxy": "#F1E9C9",
    "glass": "#E8EEF5",     # fibre-array glass, lids
    "core": "#F6D7A8",      # fibre core (Ge-doped silica), drawn warm so it shows in the cladding
    "resist": "#D9A7C7",    # photoresist
    "bcb": "#E9E3D0",       # bonding layer (BCB / thin oxide)
}
MAT_NAME = {"si": "Si", "ox": "SiO$_2$", "sin": "Si$_3$N$_4$", "ln": "LiNbO$_3$", "bto": "BaTiO$_3$", "inp": "InP", "q": "InGaAsP",
            "ge": "Ge", "metal": "metal", "tin": "TiN", "water": "water", "air": "air", "polymer": "polymer"}

# intensity maps: white -> blue -> ink (|E|², power density); signed fields: red-white-blue
FIELD_CMAP = LinearSegmentedColormap.from_list("op_field", ["#FFFFFF", "#BFD3F2", BLUE, "#13285C"])
SIGNED_CMAP = LinearSegmentedColormap.from_list("op_signed", ["#2556B8", "#9DB8E8", "#FFFFFF", "#EBA79C", "#B5473A"])
HEAT_CMAP = LinearSegmentedColormap.from_list("op_heat", ["#FFFFFF", "#F6D9A8", "#E08A3A", "#B5473A", "#5A1F16"])

FS, FS_SMALL = 7.0, 6.3         # label font sizes for drawings (axis text is 7.5-8.5 from figstyle)


def _c(mat):
    return MAT.get(mat, mat)


# ------------------------------------------------------------------ axes
def geom_axes(figsize=(6.3, 2.4), xlim=(0, 1), ylim=(0, 1), equal=True, rect=None, fig=None):
    """A frameless axes for a drawing. With equal=True one data unit is the same length on both axes (to scale)."""
    if fig is None:
        fig = plt.figure(figsize=figsize)
    ax = fig.add_axes(rect or [0, 0, 1, 1])
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    if equal: ax.set_aspect("equal")
    ax.set_axis_off()
    return fig, ax


def frameless(ax, xlim=None, ylim=None, equal=True):
    """Turn an existing (sub)axes into a drawing area."""
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    if equal: ax.set_aspect("equal")
    ax.set_axis_off()
    return ax


# ------------------------------------------------------------------ shapes
def box(ax, x, y, w, h, mat, alpha=1.0, ec="none", lw=0.0, z=1, **kw):
    """Rectangle with lower-left corner (x, y)."""
    p = Rectangle((x, y), w, h, fc=_c(mat), ec=ec, lw=lw, alpha=alpha, zorder=z, **kw)
    ax.add_patch(p); return p


def cbox(ax, xc, y, w, h, mat, **kw):
    """Rectangle centred on xc horizontally, bottom at y."""
    return box(ax, xc - w / 2, y, w, h, mat, **kw)


def poly(ax, pts, mat, alpha=1.0, ec="none", lw=0.0, z=1, **kw):
    p = Polygon(np.asarray(pts), closed=True, fc=_c(mat), ec=ec, lw=lw, alpha=alpha, zorder=z, **kw)
    ax.add_patch(p); return p


def trapezoid(ax, xc, y, wbot, wtop, h, mat, **kw):
    """Ridge with sloped sidewalls (wbot at y, wtop at y + h)."""
    return poly(ax, [(xc - wbot / 2, y), (xc + wbot / 2, y), (xc + wtop / 2, y + h), (xc - wtop / 2, y + h)], mat, **kw)


def ribbon(ax, xs, ys, w, mat, z=2, **kw):
    """A waveguide of width w drawn along the centre line (xs, ys) (top views: straight, bent, any path)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    dx, dy = np.gradient(xs), np.gradient(ys)
    L = np.hypot(dx, dy); L[L == 0] = 1
    nx, ny = -dy / L, dx / L
    left = np.c_[xs + nx * w / 2, ys + ny * w / 2]; right = np.c_[xs - nx * w / 2, ys - ny * w / 2]
    return poly(ax, np.vstack([left, right[::-1]]), mat, z=z, **kw)


def wg_straight(ax, x0, x1, y, w, mat="si", **kw):
    return box(ax, min(x0, x1), y - w / 2, abs(x1 - x0), w, mat, z=kw.pop("z", 2), **kw)


def arc_xy(cx, cy, r, th0, th1, n=200):
    """Points along a circular arc (angles in degrees)."""
    t = np.radians(np.linspace(th0, th1, n))
    return cx + r * np.cos(t), cy + r * np.sin(t)


def wg_arc(ax, cx, cy, r, w, th0, th1, mat="si", **kw):
    """Bent waveguide (annulus sector) of centre radius r between angles th0 and th1 (degrees)."""
    t = np.radians(np.linspace(th0, th1, 240))
    ro, ri = r + w / 2, r - w / 2
    pts = np.vstack([np.c_[cx + ro * np.cos(t), cy + ro * np.sin(t)], np.c_[cx + ri * np.cos(t[::-1]), cy + ri * np.sin(t[::-1])]])
    return poly(ax, pts, mat, z=kw.pop("z", 2), **kw)


def wg_ring(ax, cx, cy, r, w, mat="si", **kw):
    return wg_arc(ax, cx, cy, r, w, 0, 360, mat, **kw)


def sbend_xy(x0, y0, L, H, n=200):
    """Raised-cosine S-bend centre line from (x0, y0) to (x0 + L, y0 + H)."""
    x = np.linspace(0, L, n)
    return x0 + x, y0 + H * (1 - np.cos(np.pi * x / L)) / 2


def wg_sbend(ax, x0, y0, L, H, w, mat="si", **kw):
    xs, ys = sbend_xy(x0, y0, L, H)
    return ribbon(ax, xs, ys, w, mat, **kw)


def wg_taper(ax, x0, x1, y, w0, w1, mat="si", **kw):
    """Linear taper along x from width w0 at x0 to w1 at x1."""
    return poly(ax, [(x0, y - w0 / 2), (x1, y - w1 / 2), (x1, y + w1 / 2), (x0, y + w0 / 2)], mat, z=kw.pop("z", 2), **kw)


# ------------------------------------------------------------------ annotation
def dim(ax, p0, p1, text="", off=(0, 0), col=INK, fs=FS_SMALL, lw=0.7, ha="center", va="center", bg="white", text_off=(0, 0), z=6):
    """Dimension line with arrowheads between p0 and p1 and a label at its middle (shifted by text_off, data units)."""
    (x0, y0), (x1, y1) = p0, p1
    x0 += off[0]; x1 += off[0]; y0 += off[1]; y1 += off[1]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=z,
                arrowprops=dict(arrowstyle="<|-|>", color=col, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=6))
    if text:
        kw = dict(boxstyle="square,pad=0.08", fc=bg, ec="none") if bg else None
        ax.text((x0 + x1) / 2 + text_off[0], (y0 + y1) / 2 + text_off[1], text, ha=ha, va=va, fontsize=fs, color=col, bbox=kw, zorder=z + 1)


def tick_dim(ax, p0, p1, text="", col=INK, fs=FS_SMALL, lw=0.6, gap=0.0, text_off=(0, 0), ha="center", va="center"):
    """Dimension with short end ticks instead of arrowheads (for very short lengths)."""
    (x0, y0), (x1, y1) = p0, p1
    ax.plot([x0, x1], [y0, y1], color=col, lw=lw, zorder=6)
    a = np.arctan2(y1 - y0, x1 - x0) + np.pi / 2
    t = 0.04 * max(abs(np.diff(ax.get_xlim()))[0], abs(np.diff(ax.get_ylim()))[0]) / 4
    for x, y in ((x0, y0), (x1, y1)):
        ax.plot([x - t * np.cos(a), x + t * np.cos(a)], [y - t * np.sin(a), y + t * np.sin(a)], color=col, lw=lw, zorder=6)
    if text:
        ax.text((x0 + x1) / 2 + text_off[0], (y0 + y1) / 2 + text_off[1], text, ha=ha, va=va, fontsize=fs, color=col, zorder=7)


def scalebar(ax, x, y, length, label, col=INK, fs=FS_SMALL, lw=1.4, above=True):
    """Horizontal scale bar starting at (x, y), `length` data units long."""
    ax.plot([x, x + length], [y, y], color=col, lw=lw, solid_capstyle="butt", zorder=8)
    yr = np.diff(ax.get_ylim())[0]
    ax.text(x + length / 2, y + (0.02 if above else -0.02) * yr, label, ha="center", va="bottom" if above else "top", fontsize=fs, color=col, zorder=8)


def label(ax, x, y, text, col=INK, fs=FS, ha="center", va="center", bold=False, italic=False, bg=None, z=9, rot=0):
    kw = dict(boxstyle="square,pad=0.1", fc=bg, ec="none") if bg else None
    return ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=col, fontweight="bold" if bold else "normal",
                   style="italic" if italic else "normal", bbox=kw, zorder=z, rotation=rot)


def callout(ax, xy, xytext, text, col=INK, fs=FS_SMALL, ha="left", va="center", lc=MUTED):
    """A label joined to a point by a thin leader line."""
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=col, ha=ha, va=va, zorder=9,
                arrowprops=dict(arrowstyle="-", color=lc, lw=0.6, shrinkA=1, shrinkB=0))


def arrow(ax, p0, p1, col=INK, lw=1.0, ms=8, style="-|>", ls="-", z=7, **kw):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, color=col, lw=lw, linestyle=ls, zorder=z,
                        shrinkA=0, shrinkB=0, **kw)
    ax.add_patch(a); return a


def note(ax, text="not to scale", loc="lower right", fs=6.0):
    """Small italic note in a corner of the axes: 'not to scale', 'vertical scale × 5', ..."""
    x, ha = (0.995, "right") if "right" in loc else (0.005, "left")
    y, va = (0.005, "bottom") if "lower" in loc else (0.995, "top")
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=fs, color=MUTED, style="italic", zorder=10)


def panel(ax, s, x=0.0, y=1.0):
    """Panel letter for a frameless (drawing) axes, in axes coordinates."""
    ax.text(x, y, s, transform=ax.transAxes, fontweight="bold", color=INK, fontsize=9.5, ha="left", va="top", zorder=10)


def legend_patches(ax, items, loc="upper right", ncol=1, fs=6.5, **kw):
    """Material legend: items = [("si", "Si"), ("ox", "SiO₂"), ...]."""
    from matplotlib.patches import Patch
    h = [Patch(fc=_c(m), ec=MUTED if _c(m).upper() in ("#FFFFFF", "WHITE") else "none", lw=0.5, label=t) for m, t in items]
    return ax.legend(handles=h, loc=loc, ncol=ncol, fontsize=fs, frameon=False, handlelength=1.2, handleheight=0.9, **kw)


# ------------------------------------------------------------------ block diagrams
def block(ax, x, y, w, h, text="", fc="#F3F6FB", ec=INK, lw=0.8, fs=FS, col=INK, r=0.06, bold=False, z=3):
    """Rounded block centred on (x, y)."""
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(p)
    if text:
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, zorder=z + 1, fontweight="bold" if bold else "normal")
    return p


def wire(ax, pts, col=INK, lw=0.9, arrow_end=True, ms=7, ls="-", z=2):
    """Poly-line connection; arrowhead on the last segment."""
    pts = np.asarray(pts, float)
    if len(pts) > 2:
        ax.plot(pts[:-1, 0], pts[:-1, 1], color=col, lw=lw, ls=ls, zorder=z, solid_capstyle="butt")
    if arrow_end:
        arrow(ax, tuple(pts[-2]), tuple(pts[-1]), col=col, lw=lw, ms=ms, ls=ls, z=z)
    else:
        ax.plot(pts[-2:, 0], pts[-2:, 1], color=col, lw=lw, ls=ls, zorder=z)


OPT, ELEC = RED, BLUE      # colours of optical and electrical paths in block diagrams


# ------------------------------------------------------------------ saving
def save(fig, name, png=True):
    """Write assets/figs/<name>.svg (text kept as text). If $FIGPREVIEW names a folder, also write a 150 dpi PNG
    there on a white background, so the drawing can be looked at before it goes on the site."""
    os.makedirs(FIGDIR, exist_ok=True)
    path = os.path.join(FIGDIR, name + ".svg")
    fig.savefig(path, metadata={"Date": None})
    prev = os.environ.get("FIGPREVIEW")
    if png and prev:
        os.makedirs(prev, exist_ok=True)
        fig.savefig(os.path.join(prev, name + ".png"), dpi=150, transparent=False, facecolor="white")
    plt.close(fig)
    print("wrote", path)
