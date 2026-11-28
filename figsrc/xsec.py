"""xsec.py -- drawing helpers for the dimensioned device cross-sections of Section 24.9.

The shapes come from xsec_devices.py and the modes from xsec_modes.json (computed by xsec_modes.py). Every panel is
drawn to scale (equal aspect), with axes in micrometres; layers are filled polygons with thin outlines, so that
adjacent layers always meet: nothing is drawn as a separate, disconnected piece.
"""
import numpy as np
from matplotlib.patches import Polygon as MPoly, Rectangle
from figstyle import INK, MUTED, RED, BLUE
from xsec_devices import COL


def draw_shapes(ax, shapes, lw=0.35, ec="#5A6478", wells=True):
    for z, s in enumerate(shapes):
        ax.add_patch(MPoly(s["poly"], closed=True, fc=s["col"], ec=s.get("ec", ec), lw=lw, zorder=1 + 0.001 * z, joinstyle="miter"))
        if wells and s.get("wells"):                        # the wells inside an averaged quantum-well layer, drawn as bands
            nw, tw, tb = s["wells"]; xs = [p[0] for p in s["poly"]]; ys = [p[1] for p in s["poly"]]
            outer = abs((max(ys) - min(ys)) - (nw * tw + (nw + 1) * tb)) < 1e-6      # barriers outside the first and last well too
            y = min(ys) + (tb if outer else 0.0); x0, x1 = min(xs), max(xs)
            ax.add_patch(Rectangle((x0, min(ys)), x1 - x0, max(ys) - min(ys), fc=COL["sch"], ec="none", zorder=1 + 0.001 * z + 0.0001))
            for k in range(nw):
                ax.add_patch(Rectangle((x0, y), x1 - x0, tw, fc=COL["qw"], ec="none", zorder=1 + 0.001 * z + 0.0002))
                y += tw + tb


def draw_mode(ax, mp, star=True, z=5, at=None):
    X, Y = np.meshgrid(mp["x"], mp["y"]); I = np.array(mp["I"]); I = I / I.max()
    ax.contourf(X, Y, I, levels=[np.exp(-2), 1.01], colors=[RED], alpha=0.20, zorder=z)
    ax.contourf(X, Y, I, levels=[0.5, 1.01], colors=[RED], alpha=0.25, zorder=z)
    ax.contour(X, Y, I, levels=[np.exp(-2)], colors=[RED], linewidths=0.9, linestyles=[(0, (3, 2))], zorder=z + 0.5)
    if star:
        j, i = np.unravel_index(np.argmax(I), I.shape)
        xs, ys = at if at is not None else (mp["x"][i], mp["y"][j])     # the solver's full-resolution peak when given
        ax.plot([xs], [ys], marker="*", ms=9, mfc="#F5D547", mec=INK, mew=0.6, zorder=z + 2)
        return xs, ys


def current(ax, paths, col=BLUE, lw=0.85, z=7):
    """Current paths: polylines, each ending in an arrowhead on its last segment."""
    for p in paths:
        p = np.asarray(p, float)
        if len(p) > 2:
            ax.plot(p[:-1, 0], p[:-1, 1], color=col, lw=lw, zorder=z, solid_capstyle="round", solid_joinstyle="round")
        ax.annotate("", xy=tuple(p[-1]), xytext=tuple(p[-2]), arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=7,
                    shrinkA=0, shrinkB=0), zorder=z)


def vdim(ax, x, y0, y1, text, side="right", col=INK, fs=6.2, off=0.08, z=9):
    ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.6, mutation_scale=5.5, shrinkA=0, shrinkB=0), zorder=z)
    ax.text(x + (off if side == "right" else -off), (y0 + y1) / 2, text, ha="left" if side == "right" else "right", va="center",
            fontsize=fs, color=col, zorder=z, bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none", alpha=0.75))


def hdim(ax, y, x0, x1, text, col=INK, fs=6.2, above=True, off=0.06, z=9):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.6, mutation_scale=5.5, shrinkA=0, shrinkB=0), zorder=z)
    ax.text((x0 + x1) / 2, y + (off if above else -off), text, ha="center", va="bottom" if above else "top", fontsize=fs, color=col, zorder=z)


def tag(ax, x, y, text, fs=6.2, ha="left", col=INK, z=9, bg=True):
    ax.text(x, y, text, fontsize=fs, ha=ha, va="center", color=col, zorder=z,
            bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.7) if bg else None)


def axes_um(ax, xlim, ylim, title, xl="x (µm)", yl="y (µm)"):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.grid(False)
    ax.set_title(title, loc="left", fontsize=7.2, color=INK, pad=3)
    ax.tick_params(labelsize=6.3, length=2.5, pad=1.5)
    ax.set_xlabel(xl, fontsize=6.4, labelpad=1); ax.set_ylabel(yl, fontsize=6.4, labelpad=1)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(True); ax.spines[sp].set_linewidth(0.5); ax.spines[sp].set_color("#9AA4B5")


def legend_column(ax, items, rows, title="Computed for this stack", fs=6.1, y0=0.985, dy=0.049, table_dy=0.056, wrap=None):
    """items: (kind, colour, text); kind in 'patch', 'line', 'fill', 'star', 'arrow', 'xarrow'. rows: (name, value)."""
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    y = y0
    for kind, c, txt in items:
        if kind == "patch":
            ax.add_patch(Rectangle((0.0, y - 0.016), 0.10, 0.032, fc=c, ec="#5A6478", lw=0.4))
        elif kind == "fill":
            ax.add_patch(Rectangle((0.0, y - 0.016), 0.10, 0.032, fc=c, alpha=0.4, ec=RED, lw=0.7, ls=(0, (3, 2))))
        elif kind == "line":
            ax.plot([0.0, 0.10], [y, y], color=c, lw=2.2, solid_capstyle="butt")
        elif kind == "star":
            ax.plot([0.05], [y], marker="*", ms=8.5, mfc="#F5D547", mec=INK, mew=0.6)
        elif kind == "arrow":
            ax.annotate("", xy=(0.10, y), xytext=(0.0, y), arrowprops=dict(arrowstyle="-|>", color=c, lw=0.9, mutation_scale=7))
        ax.text(0.14, y, txt, fontsize=fs, va="center", ha="left", color=INK)
        y -= dy
    y -= 0.015
    ax.text(0.0, y, title, fontsize=fs + 0.5, fontweight="bold", va="center", color=INK)
    y -= table_dy
    for name, val in rows:
        ax.text(0.0, y, name, fontsize=fs, va="center", color=INK)
        ax.text(1.0, y, val, fontsize=fs, va="center", ha="right", color=INK, fontweight="bold")
        ax.plot([0, 1], [y - table_dy / 2, y - table_dy / 2], color="#C8CFDA", lw=0.5)
        y -= table_dy
