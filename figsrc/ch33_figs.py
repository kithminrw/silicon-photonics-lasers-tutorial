"""Figures of Chapter 33 (layout with KLayout and GDSII).

    python -I -X utf8 figsrc/ch33_figs.py

Reads the numbers and outlines written by the Docker scripts (ch33_klayout.json, ch33_gdsfactory.json) and
draws everything with Matplotlib; the grid-snapping analysis is computed here with NumPy.

ch33_layers      a heater-ring cell on SiEPIC EBeam layer numbers, and what each layer is for
ch33_records     the tiny GDS of ch33_gdsii.py, record by record, and one record taken apart
ch33_hierarchy   10 000 rings with and without hierarchy: the cell trees and the file sizes
ch33_klayout     what the KLayout example drew: one ring polygon with its cut line, vertices on the 1 nm grid
ch33_gdsfactory  the gdsfactory MZI test cell, its ports, and the SAX simulation of its extracted netlist
ch33_gridarc     a 10 um bend on a 1 nm and a 5 nm grid: snapped vertices and the width error they make
ch33_floorplan   a small chip floorplan to scale on the 127 um fibre-array pitch
ch33_routing     a bundle route from the fibre-array pitch to a dense device, with ports and orientations
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *  # noqa: E402,F401
from geomstyle import *  # noqa: E402,F401
import ch33_gdsii  # noqa: E402
from matplotlib.patches import Rectangle as Rect, Polygon as MPoly  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KL = json.load(open(os.path.join(HERE, "ch33_klayout.json"), encoding="utf-8"))
GFJ = os.path.join(HERE, "ch33_gdsfactory.json")
GF = json.load(open(GFJ, encoding="utf-8")) if os.path.exists(GFJ) else None
MONO = {"family": "monospace"}

# layer colours (fills) used in every layout drawing of this chapter
LCOL = {"Si": MAT["si"], "M1_heater": MAT["tin"], "M2_router": MAT["metal"], "M_Open": "none",
        "DevRec": "none", "PinRec": RED, "FloorPlan": "none", "Text": INK}


def draw_poly(ax, rings, fc, ec="none", lw=0.0, alpha=1.0, z=2, ls="-", hatch=None):
    """Draw a polygon given as [hull, hole, hole, ...] (lists of [x, y])."""
    verts, codes = [], []
    for r in rings:
        r = np.asarray(r, float)
        if len(r) < 3:
            continue
        verts += r.tolist() + [r[0].tolist()]
        codes += [MPath.MOVETO] + [MPath.LINETO] * (len(r) - 1) + [MPath.CLOSEPOLY]
    p = PathPatch(MPath(verts, codes), fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z, ls=ls, hatch=hatch)
    ax.add_patch(p)
    return p


# ------------------------------------------------------------------ Figure 33.1: a cell and its layers
def fig_layers():
    H = KL["heater"]["layers"]
    fig = plt.figure(figsize=(6.6, 3.5))
    ax = fig.add_axes([0.0, 0.0, 0.47, 1.0])
    frameless(ax, (-88, 88), (-30, 124))
    for p in H["FloorPlan"]["polys"]:
        draw_poly(ax, p, "none", ec=MUTED, lw=0.7, ls=(0, (4, 3)), z=1)
    for p in H["Si"]["polys"]:
        draw_poly(ax, p, LCOL["Si"], ec="#6F86A3", lw=0.3, z=3)
    for p in H["M1_heater"]["polys"]:
        draw_poly(ax, p, LCOL["M1_heater"], alpha=0.75, z=4)
    for p in H["M2_router"]["polys"]:
        draw_poly(ax, p, LCOL["M2_router"], alpha=0.55, z=5)
    for p in H["M_Open"]["polys"]:
        draw_poly(ax, p, "none", ec=INK, lw=0.7, z=6, hatch="////")
    for p in H["DevRec"]["polys"]:
        draw_poly(ax, p, "none", ec=TEAL, lw=0.8, ls=(0, (2, 1.5)), z=6)
    for p in H["PinRec"]["polys"]:
        draw_poly(ax, p, RED, ec=RED, lw=1.5, z=7)
    # labels and annotations
    lab = [t for t in KL["heater"]["texts"] if t[1].startswith("opt_in")][0]
    ax.plot(lab[2], lab[3], marker="+", color=INK, ms=6, mew=1.0, zorder=8)
    ax.text(lab[2] - 1, lab[3] - 4.0, "opt_in_TE_1550_device_demo_ringheater", fontsize=5.4, color=INK, va="top", **MONO)
    for t in KL["heater"]["texts"]:
        if t[0] == "PinRec":
            ax.text(t[2] + (4 if t[2] > 0 else -4), t[3], t[1], fontsize=5.6, color=RED, ha="left" if t[2] > 0 else "right",
                    va="center", **MONO)
    callout(ax, (-7.2, -7.0), (-30, 20), "ring and bus, Si 1/0", fs=6, ha="right")
    callout(ax, (0, 11.5), (0, 52), "heater, M1_heater 11/0", fs=6, ha="center", va="bottom")
    callout(ax, (40, 35), (50, 44), "lead, M2_router 12/0", fs=6, ha="center", va="bottom")
    ax.text(-50, 85, "pad\n(M2 under an\nM_Open window)", fontsize=6, color=INK, ha="center", va="center",
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"), zorder=9)
    callout(ax, (40, 13), (55, 20), "DevRec 68/0", fs=6, col=TEAL, ha="left")
    ax.text(83, -24, "FloorPlan 99/0", fontsize=5.8, color=MUTED, ha="right", va="bottom")
    scalebar(ax, -82, -23, 20, "20 µm")
    panel(ax, "a", 0.0, 1.08)                      # above the FloorPlan outline, not on it
    # (b) what each layer becomes
    bx = fig.add_axes([0.49, 0.0, 0.51, 1.0])
    frameless(bx, (0, 1), (0, 1), equal=False)
    panel(bx, "b", 0.0, 0.99)
    rows = [("Si", "1/0", "si", "silicon kept; the rest etched to\nthe oxide (one e-beam write)", True),
            ("M1_heater", "11/0", "tin", "resistive heater metal", True),
            ("M2_router", "12/0", "metal", "routing metal and pads", True),
            ("M_Open", "13/0", "open", "opening in the top oxide over pads", True),
            ("Text", "10/0", "text", "test labels for the prober", False),
            ("DevRec", "68/0", "devrec", "device outline, for netlisting\nand overlap checks", False),
            ("PinRec", "1/10", "pin", "ports: where waveguides join", False),
            ("Waveguide", "1/99", "wgpath", "paths that become waveguides", False),
            ("FloorPlan", "99/0", "fp", "the design area", False)]
    y = 0.905
    bx.text(0.11, 0.965, "layer", fontsize=6.6, color=MUTED, fontweight="bold")
    bx.text(0.30, 0.965, "L/D", fontsize=6.6, color=MUTED, fontweight="bold")
    bx.text(0.43, 0.965, "what it is for", fontsize=6.6, color=MUTED, fontweight="bold")
    bx.plot([0.0, 1.0], [0.947, 0.947], color=GRID, lw=0.8)
    first_virtual = True
    for name, ld, kind, what, fab in rows:
        if not fab and first_virtual:
            bx.plot([0.0, 1.0], [y + 0.045, y + 0.045], color=MUTED, lw=0.6, ls=(0, (3, 2)))
            bx.text(1.0, y + 0.052, "not fabricated: for the design tools", fontsize=5.8, color=MUTED, ha="right", style="italic")
            first_virtual = False
        sx, sy, sw, sh = 0.03, y - 0.022, 0.055, 0.044
        if kind in ("si", "tin", "metal"):
            bx.add_patch(Rect((sx, sy), sw, sh, fc=MAT[kind], ec="none", alpha=0.85 if kind != "si" else 1))
        elif kind == "open":
            bx.add_patch(Rect((sx, sy), sw, sh, fc="none", ec=INK, lw=0.7, hatch="////"))
        elif kind == "text":
            bx.text(sx + sw / 2, sy + sh / 2, "Aa", fontsize=6.5, ha="center", va="center", color=INK, **MONO)
        elif kind == "devrec":
            bx.add_patch(Rect((sx, sy), sw, sh, fc="none", ec=TEAL, lw=0.8, ls=(0, (2, 1.5))))
        elif kind == "pin":
            bx.plot([sx + 0.01, sx + sw - 0.01], [sy + sh / 2] * 2, color=RED, lw=2.0)
        elif kind == "wgpath":
            bx.plot([sx, sx + sw * 0.5, sx + sw * 0.5, sx + sw], [sy + 0.005, sy + 0.005, sy + sh - 0.005, sy + sh - 0.005], color=BLUE, lw=0.9)
        elif kind == "fp":
            bx.add_patch(Rect((sx, sy), sw, sh, fc="none", ec=MUTED, lw=0.7, ls=(0, (3, 2))))
        bx.text(0.11, y, name, fontsize=6.6, color=INK, va="center")
        bx.text(0.30, y, ld, fontsize=6.6, color=INK, va="center", **MONO)
        bx.text(0.43, y, what, fontsize=6.3, color=INK if fab else MUTED, va="center", linespacing=1.05)
        y -= 0.098 if "\n" in what else 0.083
    save(fig, "ch33_layers")


# ------------------------------------------------------------------ Figure 33.2: GDSII records
KIND = {"HEADER": "lib", "BGNLIB": "lib", "LIBNAME": "lib", "UNITS": "lib", "ENDLIB": "lib",
        "BGNSTR": "str", "STRNAME": "str", "ENDSTR": "str",
        "BOUNDARY": "el", "PATH": "el", "SREF": "el", "AREF": "el", "TEXT": "el", "ENDEL": "el"}
KFC = {"lib": "#E8EEF8", "str": "#FBF0DC", "el": "#E3F1EF", "prop": "#FFFFFF"}


def fmt_val(name, val):
    if val is None:
        return ""
    if name in ("BGNLIB", "BGNSTR"):
        y, mo, d, h, mi, s = val[:6]
        return f"{y}-{mo:02d}-{d:02d} {h:02d}:{mi:02d} (×2)"
    if name == "UNITS":
        return f"{val[0]:g} µm, {val[1]:.0e} m".replace("e-09", "e-9")
    if name == "XY":
        pts = list(zip(val[0::2], val[1::2]))
        s = ""
        for k, (x, y) in enumerate(pts):
            item = f"({x},{y})"
            if len(s) + len(item) > 26 and k < len(pts):
                return s + "…"
            s += item + " "
        return s.strip()
    if name in ("LIBNAME", "STRNAME", "SNAME", "STRING"):
        return f'"{val}"'
    if name == "ANGLE":
        return f"{val[0]:g}°"
    if name == "STRANS":
        return f"0x{val[0]:04X}"
    if name == "COLROW":
        return f"{val[0]} col × {val[1]} rows"
    if isinstance(val, tuple) and len(val) == 1:
        return str(val[0])
    return str(val)


def fig_records():
    data = ch33_gdsii.build_tiny()
    recs = ch33_gdsii.records(data)
    assert len(data) == KL["tiny"]["bytes"]
    fig = plt.figure(figsize=(6.6, 6.6))
    # (a) one record taken apart: the XY of the WG boundary
    ax = fig.add_axes([0.0, 0.83, 1.0, 0.17])
    frameless(ax, (0, 1), (0, 1), equal=False)
    panel(ax, "a", 0.0, 1.0)
    xy = [r for r in recs if r[2] == "XY"][0]
    off, n, name, dt, raw, val = xy
    bytes_ = data[off:off + n]
    groups = [("length", bytes_[0:2], "#E8EEF8"), ("type", bytes_[2:3], "#FBF0DC"), ("data type", bytes_[3:4], "#FBF0DC")]
    for k in range(5):
        groups.append((f"x{k + 1}", bytes_[4 + 8 * k:8 + 8 * k], "#E3F1EF"))
        groups.append((f"y{k + 1}", bytes_[8 + 8 * k:12 + 8 * k], "#E3F1EF"))
    x = 0.035
    cw = 0.0198
    for i, (lab, b, fc) in enumerate(groups):
        w = cw * len(b)
        ax.add_patch(Rect((x, 0.42), w, 0.26, fc=fc, ec=INK, lw=0.5))
        ax.text(x + w / 2, 0.55, " ".join(f"{c:02X}" for c in b), fontsize=4.9, ha="center", va="center", color=INK, **MONO)
        if i == 0:
            ax.text(x + w / 2, 0.74, "length", fontsize=6.3, ha="center", color=INK)
        elif i == 1:
            ax.text(x + w, 0.92, "record type", fontsize=6.3, ha="right", color=INK)
            ax.plot([x + w / 2, x + w / 2], [0.69, 0.9], color=MUTED, lw=0.5)
        elif i == 2:
            ax.text(x, 0.74, "data type", fontsize=6.3, ha="left", color=INK)
        x += w + 0.0025
    v = list(zip(val[0::2], val[1::2]))
    ax.text(0.035, 0.30, f"0x002C = {n} bytes", fontsize=6.4, color=INK, va="top")
    ax.text(0.168, 0.30, "0x10 = XY,  3 = 4-byte signed integers", fontsize=6.4, color=INK, va="top")
    ax.text(0.47, 0.30, "five (x, y) pairs in nm: " + ", ".join(f"({a}, {b})" for a, b in v),
            fontsize=6.4, color=INK, va="top")
    ax.text(0.47, 0.13, "the fifth point repeats the first: a boundary is closed; FF FF FF 06 = −250 (two's complement)",
            fontsize=6.3, color=MUTED, va="top")
    # (b) the whole file in two columns
    split = [i for i, r in enumerate(recs) if r[2] == "BGNSTR"][1]
    cols = [recs[:split], recs[split:]]
    for ci, col in enumerate(cols):
        bx = fig.add_axes([0.0 + 0.5 * ci, 0.0, 0.5, 0.81])
        frameless(bx, (0, 1), (0, 1), equal=False)
        if ci == 0:
            panel(bx, "b", 0.0, 1.035)
            yl = 0.36
            for lab, k in (("library records", "lib"), ("structure (cell) records", "str"), ("element records", "el"),
                           ("records inside an element", "prop")):
                bx.add_patch(Rect((0.05, yl - 0.012), 0.05, 0.026, fc=KFC[k], ec=GRID, lw=0.5))
                bx.text(0.12, yl, lab, fontsize=6.3, va="center", color=INK)
                yl -= 0.04
            T = KL["tiny"]
            bx.text(0.05, yl - 0.01, f"{T['bytes']} bytes, {T['records']} records. Read back by KLayout: cells "
                    f"{', '.join(T['cells'])};\nan array of 4 WG at 127 µm, one WG turned by 90°, a path and a label.\n"
                    "Integers are big-endian two's complement; reals are excess-64,\nbase-16 (Calma, 1987).",
                    fontsize=6.2, va="top", color=MUTED, linespacing=1.3)
        nrow = 22
        dy = 0.96 / nrow
        bx.text(0.02, 0.985, "offset", fontsize=6.2, color=MUTED, fontweight="bold")
        bx.text(0.13, 0.985, "bytes (first 8)", fontsize=6.2, color=MUTED, fontweight="bold")
        bx.text(0.505, 0.985, "record", fontsize=6.2, color=MUTED, fontweight="bold")
        bx.text(0.70, 0.985, "value", fontsize=6.2, color=MUTED, fontweight="bold")
        depth = 0
        for j, (off, n, name, dt, raw, val) in enumerate(col):
            yy = 0.95 - j * dy
            kind = KIND.get(name, "prop")
            if name in ("ENDEL",):
                depth_here = 2
            elif kind == "el":
                depth_here = 2
            elif kind == "str":
                depth_here = 1
            elif kind == "lib":
                depth_here = 0
            else:
                depth_here = 3
            bx.add_patch(Rect((0.0, yy - dy / 2), 1.0, dy * 0.92, fc=KFC[kind], ec="none"))
            hx = data[off:off + min(n, 8)].hex(" ").upper() + (" …" if n > 8 else "")
            bx.text(0.02, yy, f"{off:3d}", fontsize=6.0, va="center", color=MUTED, **MONO)
            bx.text(0.13, yy, hx, fontsize=5.6, va="center", color=INK, **MONO)
            bx.text(0.505 + 0.02 * (depth_here - 0) * 0.5, yy, name, fontsize=6.2, va="center", color=INK,
                    fontweight="bold" if kind in ("lib", "str") or name in ("BOUNDARY", "PATH", "SREF", "AREF", "TEXT") else "normal")
            bx.text(0.70, yy, fmt_val(name, val), fontsize=6.0, va="center", color=INK)
    save(fig, "ch33_records")


# ------------------------------------------------------------------ Figure 33.3: hierarchy and file size
def fig_hierarchy():
    Hh = KL["hierarchy"]
    S = Hh["sizes_bytes"]
    fig = plt.figure(figsize=(6.6, 2.9))
    ax = fig.add_axes([0.0, 0.0, 0.52, 1.0])
    frameless(ax, (0, 10), (0, 6.2), equal=False)
    panel(ax, "a", 0.0, 1.0)
    npts = Hh["ring_in_gds"]["points"]
    # left tree: hierarchical
    block(ax, 2.4, 5.2, 1.6, 0.6, "TOP", fs=7, bold=True)
    block(ax, 2.4, 2.9, 2.6, 0.95, f"ring\n1 ring ({npts} points)\n+ 1 bus (4 points)", fs=6.2, fc="#EEF3FA")
    wire(ax, [(2.4, 4.9), (2.4, 3.4)], col=INK, lw=0.9)
    ax.text(2.55, 4.15, "1 array instance\n100 × 100, 40 × 30 µm", fontsize=6.0, color=INK, va="center")
    ax.text(2.4, 1.85, "hierarchical:\nthe ring is stored once", fontsize=6.4, color=INK, ha="center", va="top", fontweight="bold")
    # right tree: flat
    block(ax, 7.4, 5.2, 1.6, 0.6, "TOP", fs=7, bold=True)
    for k in range(7):
        xx = 5.4 + k * 0.62
        ax.add_patch(Rect((xx - 0.25, 2.55), 0.5, 0.7, fc="#EEF3FA", ec=INK, lw=0.5))
        ax.add_patch(Circle((xx, 2.85), 0.17, fc="none", ec=BLUE, lw=0.8))
        ax.plot([xx - 0.2, xx + 0.2], [3.12, 3.12], color=BLUE, lw=0.8)
        ax.plot([7.4, xx], [4.9, 3.25], color=MUTED, lw=0.4)
    ax.text(9.5, 2.85, "…", fontsize=9, color=INK, ha="center", va="center")
    ax.text(7.4, 1.85, "flat: " + f"{Hh['polygons_flat']:,}".replace(",", " ") + " polygons\nin the top cell", fontsize=6.4, color=INK,
            ha="center", va="top", fontweight="bold")
    ax.text(5.0, 0.35, "the same 10 000 rings (XOR of the two layouts: empty)", fontsize=6.0, color=MUTED, ha="center", style="italic")
    # (b) file sizes
    bx = fig.add_axes([0.62, 0.17, 0.37, 0.74])
    tag(bx, "b")
    cases = [("one AREF", "array"), ("10 000 SREFs", "sref"), ("flat", "flat")]
    y = np.arange(len(cases))[::-1]
    h = 0.26
    g = [S[k]["gds"] for _, k in cases]
    op = [S[k]["oas_plain"] for _, k in cases]
    oc = [S[k]["oas_compact"] for _, k in cases]
    bx.barh(y + h, g, h, color=BLUE, label="GDSII")
    bx.barh(y, op, h, color=AMBER, label="OASIS")
    bx.barh(y - h, oc, h, color=TEAL, label="OASIS, compacted")
    bx.set_xscale("log")
    bx.set_xlim(1e3, 3e8)
    bx.set_yticks(y)
    bx.set_yticklabels([c for c, _ in cases])
    bx.grid(axis="y", visible=False)

    def human(b):
        return f"{b / 1e6:.1f} MB" if b >= 1e6 else f"{b / 1e3:.0f} kB" if b >= 1e4 else f"{b / 1e3:.1f} kB"
    for yy, vals in ((y + h, g), (y, op), (y - h, oc)):
        for yi, v in zip(yy, vals):
            bx.text(v * 1.25, yi, human(v), fontsize=5.8, va="center", color=INK)
    bx.legend(loc="upper right", fontsize=6.0, handlelength=1.0)
    finish(bx, xlabel="File size (bytes)")
    save(fig, "ch33_hierarchy")


# ------------------------------------------------------------------ Figure 33.4: the KLayout example
def fig_klayout():
    E = KL["example"]
    fig = plt.figure(figsize=(6.6, 2.9))
    # (a) the three cells as placed, to scale
    ax = fig.add_axes([0.0, 0.02, 0.2, 0.96])
    frameless(ax, (-30, 54), (-25, 275))           # room on the right for the pitch dimension
    for p in E["outlines"]:
        draw_poly(ax, p, MAT["si"], ec="#6F86A3", lw=0.5)
    for t, x, y in E["texts"]:
        ax.text(-16, y + 3.0, t, fontsize=5.6, color=INK, ha="left", va="top")
        ax.text(-16, y + 29.0, f"ring_r10_g{t.split()[1]}", fontsize=5.0, color=MUTED, ha="left", va="bottom", **MONO)
    dim(ax, (47, 0), (47, 127), "127 µm", text_off=(0, 0), fs=5.6)      # right of the gap labels and cell names
    dim(ax, (47, 127), (47, 254), "127 µm", text_off=(0, 0), fs=5.6)
    panel(ax, "a", 0.0, 1.0)
    # (b) one ring polygon as stored in GDS: hull and cut line, vertices marked
    bx = fig.add_axes([0.2, 0.02, 0.42, 0.96])
    frameless(bx, (-12.0, 25), (-12.0, 12.3))
    ring = [p for p in E["outlines"] if len(p[0]) > 100 and abs(np.mean(np.asarray(p[0])[:, 1])) < 30][0]
    hull = np.asarray(ring[0])
    draw_poly(bx, ring, MAT["si"], ec="none")
    bx.plot(np.r_[hull[:, 0], hull[0, 0]], np.r_[hull[:, 1], hull[0, 1]], color=BLUE, lw=0.5)
    bus = [p for p in E["outlines"] if len(p[0]) == 4 and abs(np.mean(np.asarray(p[0])[:, 1]) - 10.95) < 1][0]
    draw_poly(bx, bus, MAT["si"], ec="none")
    # find the cut line: the two consecutive hull points whose segment crosses the ring radially
    r = np.hypot(hull[:, 0], hull[:, 1])
    jumps = [i for i in range(len(hull) - 1) if abs(r[i + 1] - r[i]) > 0.3]
    for i in jumps[:2]:
        bx.plot(hull[i:i + 2, 0], hull[i:i + 2, 1], color=RED, lw=1.2)
    if jumps:
        i = jumps[0]
        callout(bx, tuple(hull[i:i + 2].mean(axis=0)), (11.5, 6.0), "cut line: GDSII has\nno holes, so the\ninner edge is joined\nto the outer", fs=5.8)
    rr = E["rings"][1]
    bx.text(11.5, -2.0, f"one polygon of {rr['ring_points']}\npoints: two edges of\n256 joined by a cut;\n{rr['ring_holes']} holes",
            fontsize=5.8, color=INK, va="top")
    bx.add_patch(Rect((-1.0, 9.7), 2.0, 1.55, fc="none", ec=RED, lw=0.7, zorder=8))
    scalebar(bx, 13, -11, 5, "5 µm")
    panel(bx, "b", 0.0, 1.07)                      # clear of the bus
    # (c) zoom on the gap: vertices on the 1 nm grid
    cx = fig.add_axes([0.70, 0.12, 0.29, 0.8])
    out = hull[r > 10.0]
    sel = out[(np.abs(out[:, 0]) < 0.62) & (out[:, 1] > 9.9)]
    sel = sel[np.argsort(sel[:, 0])]
    ro = 10.25
    t = np.linspace(-0.07, 0.07, 400)
    cx.plot(ro * np.sin(t) * 1e3, ro * np.cos(t) * 1e3 - 10000, color=MUTED, lw=0.8, ls=(0, (3, 2)), label="ideal circle")
    cx.plot(sel[:, 0] * 1e3, sel[:, 1] * 1e3 - 10000, "-o", color=BLUE, ms=2.5, lw=0.9, label="polygon edge")
    cx.axhline(450, color=INK, lw=1.0)
    cx.fill_between([-650, 650], 450, 520, color=MAT["si"], lw=0)
    cx.fill_between(sel[:, 0] * 1e3, sel[:, 1] * 1e3 - 10000, 150, color=MAT["si"], lw=0, alpha=0.6)
    cx.annotate("", xy=(0, 450), xytext=(0, 250), arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=6))
    cx.text(15, 350, f"gap {rr['gap_um'] * 1e3:.0f} nm\n(measured)", fontsize=6.0, color=RED, va="center")
    cx.text(-640, 470, "bus", fontsize=6, color=INK, va="bottom")
    cx.set_xlim(-650, 650)
    cx.set_ylim(150, 520)
    cx.set_xlabel("x (nm)")
    cx.set_ylabel("y − 10 µm (nm)")
    cx.legend(loc="lower center", fontsize=5.8)
    tag(cx, "c")
    save(fig, "ch33_klayout")


# ------------------------------------------------------------------ grid-snapping analysis (Section 33.5)
def nvert(R, e):
    """Vertices per full circle that keep the chord sagitta of a circle of radius R within e."""
    return math.ceil(math.pi / math.acos(1 - e / R))


def radial(poly, phi):
    """Radius of a polygon (vertices ordered counter-clockwise around the origin) along the directions phi."""
    ang = np.unwrap(np.arctan2(poly[:, 1], poly[:, 0]))
    k = np.clip(np.searchsorted(ang, phi) - 1, 0, len(poly) - 2)
    a, b = poly[k], poly[k + 1]
    d = np.c_[np.cos(phi), np.sin(phi)]
    e = b - a
    # solve a + t e = s d for s (2 x 2, vectorised by Cramer's rule)
    det = d[:, 0] * (-e[:, 1]) - d[:, 1] * (-e[:, 0])
    return (a[:, 0] * (-e[:, 1]) - a[:, 1] * (-e[:, 0])) / det


def bend_edges(R, w, N, grid, sweep=math.pi / 2):
    """Outer and inner edge vertices of a circular bend with N segments per full circle, snapped to grid (nm)."""
    nq = int(round(N * sweep / (2 * math.pi)))
    th = np.linspace(0, sweep, nq + 1)
    out = np.c_[(R + w / 2) * np.cos(th), (R + w / 2) * np.sin(th)]
    inn = np.c_[(R - w / 2) * np.cos(th), (R - w / 2) * np.sin(th)]
    if grid:
        out, inn = np.round(out / grid) * grid, np.round(inn / grid) * grid
    return out, inn


def grid_stats(R=10000.0, w=500.0, N=256, grid=1.0, nphi=20001):
    out, inn = bend_edges(R, w, N, grid)
    phi = np.linspace(0.002, math.pi / 2 - 0.002, nphi)
    ro, ri = radial(out, phi), radial(inn, phi)
    werr = ro - ri - w
    return {"phi": phi, "werr": werr, "eo": ro - (R + w / 2), "mean_r_err": float(((ro + ri) / 2 - R).mean()),
            "w_rms": float(werr.std()), "w_pp": float(werr.max() - werr.min()), "w_mean": float(werr.mean()),
            "eo_min": float((ro - (R + w / 2)).min()), "eo_max": float((ro - (R + w / 2)).max())}


GRIDNUM = {}


def grid_numbers():
    R_o = 10250.0
    GRIDNUM["N_for_e"] = {e: nvert(R_o, e) for e in (2.0, 1.0, 0.5, 0.25, 0.1)}
    GRIDNUM["stats"] = {}
    for g in (1.0, 5.0):
        for N in (64, 128, 256, 512, 1024, 4096):
            s = grid_stats(N=N, grid=g)
            GRIDNUM["stats"][(g, N)] = {k: v for k, v in s.items() if k not in ("phi", "werr", "eo")}
    # mean-radius deficit of a polygon whose vertices lie on the circle: 2/3 of the sagitta (exact average)
    N = 228
    th = np.linspace(-math.pi / N, math.pi / N, 200001)
    ring = {}
    for name, R_e in (("outer", R_o), ("inner", 9750.0)):
        r_chord = R_e * math.cos(math.pi / N) / np.cos(th)
        ring[name] = {"sagitta_nm": R_e * (1 - math.cos(math.pi / N)), "mean_deficit_nm": float(R_e - r_chord.mean())}
    d_mid = (ring["outer"]["mean_deficit_nm"] + ring["inner"]["mean_deficit_nm"]) / 2
    ring["centre_deficit_nm"] = d_mid
    ring["width_change_nm"] = ring["inner"]["mean_deficit_nm"] - ring["outer"]["mean_deficit_nm"]
    ring["dlambda_nm"] = 1550 * (2.446 / 4.18) * d_mid / 10000.0      # lambda (n_eff/n_g) dR/R, Chapter 6 indices
    GRIDNUM["ring228"] = ring
    # an off-grid port: a 30 degree arc of radius 10 um ends at (R sin 30, R(1 - cos 30)); its end face, snapped
    # as part of the bend, against a straight that starts from the snapped port
    R, w, a = 10000.0, 500.0, math.radians(30)
    c = np.array([R * math.sin(a), R * (1 - math.cos(a))])
    nrm = np.array([-math.sin(a), math.cos(a)])
    bend_end = np.round(np.array([c + w / 2 * nrm, c - w / 2 * nrm]))
    port = np.round(c)
    straight_start = np.round(np.array([port + w / 2 * nrm, port - w / 2 * nrm]))
    GRIDNUM["port30"] = {"centre": c.tolist(), "bend_end": bend_end.tolist(), "straight_start": straight_start.tolist(),
                         "mismatch_nm": np.abs(bend_end - straight_start).max(axis=1).tolist()}
    return GRIDNUM


def calloutb(ax, xy, xytext, text, col=INK, fs=FS_SMALL, ha="left", va="center", lc=MUTED):
    """callout() with a white box behind the text, for labels over busy backgrounds."""
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=col, ha=ha, va=va, zorder=11,
                bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.9),
                arrowprops=dict(arrowstyle="-", color=lc, lw=0.6, shrinkA=1, shrinkB=0))


# ------------------------------------------------------------------ Figure 33.6: grid-snapped arc
def fig_gridarc():
    fig = plt.figure(figsize=(6.6, 4.4))
    R, w, N = 10000.0, 500.0, 256
    # (a) a few vertices of the outer edge on the 1 nm grid, the error magnified
    ax = fig.add_axes([0.07, 0.56, 0.4, 0.4])
    th0, th1 = math.radians(41.5), math.radians(48.6)
    out_i, _ = bend_edges(R, w, N, 0)
    out_s, _ = bend_edges(R, w, N, 1.0)
    thv = np.arctan2(out_i[:, 1], out_i[:, 0])
    m = (thv > th0) & (thv < th1)
    t = np.linspace(th0, th1, 400)
    M = 100.0                                          # error magnification

    def mag(pts):                                      # radial deviation from the ideal circle, times M
        pts = np.asarray(pts, float)
        r = np.hypot(pts[:, 0], pts[:, 1]); a = np.arctan2(pts[:, 1], pts[:, 0])
        rr = (R + w / 2) + M * (r - (R + w / 2))
        return a, rr
    a_i, r_i = mag(out_i[m]); a_s, r_s = mag(out_s[m])
    sx = lambda a: (R + w / 2) * a / 1e3              # arc length along the edge (um)
    ax.plot(sx(t), np.zeros_like(t), color=MUTED, lw=1.0, ls=(0, (3, 2)), label="ideal arc")
    # chord between ideal vertices, magnified: sample along each chord
    for pts, col, lab, ms in ((out_i[m], BLUE, "vertices on the arc (chords)", 3), (out_s[m], RED, "snapped to the 1 nm grid", 3)):
        segs_a, segs_r = [], []
        for p, q in zip(pts[:-1], pts[1:]):
            u = np.linspace(0, 1, 30)[:, None]
            s = p + u * (q - p)
            aa, rr = mag(s)
            segs_a += list(aa); segs_r += list(rr)
        ax.plot(sx(np.array(segs_a)), (np.array(segs_r) - (R + w / 2)) / M, color=col, lw=1.0, label=lab)
        aa, rr = mag(pts)
        ax.plot(sx(aa), (rr - (R + w / 2)) / M, "o", color=col, ms=ms)
    ax.set_xlim(sx(th0), sx(th1))
    ax.set_ylim(-1.1, 1.0)
    finish(ax, xlabel="Position along the outer edge (µm)", ylabel="Edge − ideal (nm)")
    ax.legend(loc="upper left", fontsize=5.8, ncol=1)
    tag(ax, "a")
    ax.text(0.98, 0.95, f"R = 10 µm, 500 nm wide,\n{N} vertices per circle", transform=ax.transAxes, fontsize=6.0, ha="right", va="top")
    # (b) the width along the bend, 1 nm and 5 nm grids
    bx = fig.add_axes([0.58, 0.56, 0.4, 0.4])
    for g, col in ((5.0, AMBER), (1.0, BLUE)):
        s = grid_stats(N=N, grid=g)
        bx.plot(np.degrees(s["phi"]), s["werr"], color=col, lw=0.6,
                label=f"{g:g} nm grid: rms {s['w_rms']:.2f} nm")
    bx.set_xlim(0, 90)
    bx.set_ylim(-7, 7)
    bx.set_xticks([0, 30, 60, 90])
    finish(bx, xlabel="Angle along the 90° bend (°)", ylabel="Width − 500 nm (nm)")
    bx.legend(loc="lower center", fontsize=5.8, ncol=1)
    tag(bx, "b")
    # (c) error against the number of vertices
    cx = fig.add_axes([0.07, 0.09, 0.4, 0.33])
    Ns = np.array([32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024, 2048, 4096])
    sag = (R + w / 2) * (1 - np.cos(np.pi / Ns))
    cx.loglog(Ns, sag, color=MUTED, lw=1.2, ls=(0, (3, 2)), label="sagitta (no grid)")
    for g, col in ((1.0, BLUE), (5.0, AMBER)):
        rms = [grid_stats(N=int(n), grid=g, nphi=4001)["w_rms"] for n in Ns]
        cx.loglog(Ns, rms, "o-", color=col, ms=2.5, lw=1.0, label=f"rms width error, {g:g} nm grid")
    cx.set_ylim(0.03, 60)
    cx.axvline(nvert(R + w / 2, 1.0), color=INK, lw=0.6, ls=":")
    cx.text(nvert(R + w / 2, 1.0) / 1.08, 0.05, f"{nvert(R + w / 2, 1.0)}: sagitta 1 nm", fontsize=5.8, color=INK, va="center", ha="right")
    finish(cx, xlabel="Vertices per full circle", ylabel="Error (nm)")
    cx.legend(loc="upper right", fontsize=5.6)
    tag(cx, "c")
    # (d) an off-grid port after a 30 degree bend: the joint at the upper corner, nm by nm
    dx = fig.add_axes([0.58, 0.09, 0.4, 0.33])
    P = GRIDNUM["port30"]
    be = np.array(P["bend_end"]); ss = np.array(P["straight_start"])
    o = be[0].copy()                                   # origin: the bend's snapped upper corner
    a = math.radians(30)
    tdir = np.array([math.cos(a), math.sin(a)])
    fb = (be[1] - be[0]) / np.linalg.norm(be[1] - be[0])
    fs_ = (ss[1] - ss[0]) / np.linalg.norm(ss[1] - ss[0])
    Lr = 30.0
    poly(dx, [be[0] - o - Lr * tdir, be[0] - o, be[0] - o + Lr * fb, be[0] - o + Lr * fb - Lr * tdir], "si", alpha=0.9, z=2)
    poly(dx, [ss[0] - o, ss[0] - o + Lr * tdir, ss[0] - o + Lr * fs_ + Lr * tdir, ss[0] - o + Lr * fs_], "#C9D6E6", alpha=0.95, z=2)
    gx, gy = np.meshgrid(np.arange(-6, 7), np.arange(-5, 7))
    dx.plot(gx.ravel(), gy.ravel(), ".", color=MUTED, ms=1.6, zorder=3)
    dx.plot(*(be[0] - o), "o", color=BLUE, ms=4, zorder=6)
    dx.plot(*(ss[0] - o), "s", color=RED, ms=4, mfc="white", zorder=6)
    ideal = np.array(P["centre"]) + 250.0 * np.array([-math.sin(a), math.cos(a)]) - o
    dx.plot(*ideal, "x", color=INK, ms=4, zorder=6)
    dx.set_xlim(-6, 6); dx.set_ylim(-5, 6); dx.set_aspect("equal")
    dx.set_xticks([-5, 0, 5]); dx.set_yticks([-5, 0, 5])
    dx.grid(False)
    finish(dx, xlabel="x (nm)", ylabel="y (nm)")
    dx.text(-5.6, -4.6, "bend", fontsize=6.2, color=INK)
    dx.text(5.6, 1.6, "straight", fontsize=6.2, color=INK, ha="right")
    calloutb(dx, tuple(be[0] - o), (-5.6, 3.8), "corner snapped\nwith the bend", fs=5.6, col=BLUE)
    calloutb(dx, tuple(ss[0] - o), (1.2, 5.3), "corner of the straight\nplaced at the snapped port", fs=5.6, col=RED)
    calloutb(dx, tuple(ideal), (2.0, -3.6), "exact corner", fs=5.6)
    tag(dx, "d")

    save(fig, "ch33_gridarc")


# ------------------------------------------------------------------ gdsfactory figures (Figures 33.5, 33.7, 33.8)
GLAYER = {"1/0": ("si", 1.0, 3), "2/0": ("#DCE6F2", 1.0, 2), "47/0": ("tin", 0.8, 5), "49/0": ("metal", 0.55, 6),
          "45/0": ("metal", 0.4, 6), "41/0": ("metal", 0.4, 6), "43/0": (INK, 0.6, 7), "44/0": (INK, 0.6, 7)}


def rdp(pts, tol):
    """Ramer-Douglas-Peucker simplification of an open polyline (for drawing only: drops points that move the
    outline by less than tol, far below what the figure can show)."""
    pts = np.asarray(pts, float)
    if len(pts) < 3 or tol <= 0:
        return pts
    a, b = pts[0], pts[-1]
    ab = b - a
    n = np.hypot(*ab)
    d = (np.abs(ab[0] * (pts[:, 1] - a[1]) - ab[1] * (pts[:, 0] - a[0])) / n) if n > 0 else np.hypot(*(pts - a).T)
    i = int(np.argmax(d))
    if d[i] <= tol:
        return np.array([a, b])
    return np.vstack([rdp(pts[:i + 1], tol)[:-1], rdp(pts[i:], tol)])


def draw_outline(ax, outline, skip=("99/0",), ec_si="#6F86A3", lw_si=0.15, tol=0.0):
    """Draw polygons per layer; skip those outside the axes, and simplify by tol (um) for the drawing."""
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    for ld, plist in outline.items():
        if ld in skip or ld not in GLAYER:
            continue
        mat, alpha, z = GLAYER[ld]
        for p in plist:
            hull = np.asarray(p[0])
            if hull[:, 0].max() < x0 or hull[:, 0].min() > x1 or hull[:, 1].max() < y0 or hull[:, 1].min() > y1:
                continue
            rings = [rdp(np.vstack([r, r[:1]]), tol)[:-1] if tol else r for r in (np.asarray(q) for q in p)]
            draw_poly(ax, rings, MAT.get(mat, mat), ec=ec_si if ld == "1/0" else "none", lw=lw_si if ld == "1/0" else 0,
                      alpha=alpha, z=z)


def port_arrow(ax, p, L, col=RED, lw=0.9, label=None, fs=5.6, loff=1.25, ms=6):
    a = math.radians(p["o"])
    x, y = p["x"], p["y"]
    arrow(ax, (x, y), (x + L * math.cos(a), y + L * math.sin(a)), col=col, lw=lw, ms=ms, z=9)
    if label:
        ax.text(x + loff * L * math.cos(a), y + loff * L * math.sin(a) + (0.35 * L if abs(math.sin(a)) < 0.5 else 0),
                label, fontsize=fs, color=col, ha="center", va="center", zorder=9)


def fig_gdsfactory():
    M = GF["mzi_test"]
    fig = plt.figure(figsize=(6.6, 2.9))
    ax = fig.add_axes([0.0, 0.03, 0.5, 0.95])
    x0, y0, x1, y1 = M["bbox"]
    frameless(ax, (x0 - 8, x1 + 30), (y0 - 10, y1 + 12))
    draw_outline(ax, M["outline"], tol=0.02)
    for p in M["inst_ports"]:
        if p["type"] != "optical" or p["inst"] is None:
            continue
        if p["inst"].startswith("grating") and p["name"] == "o1" or p["inst"].startswith("mzi"):
            port_arrow(ax, p, 9.0, label=p["name"])
    for name, lx, ly in M["labels"]:
        ax.plot(lx, ly, "+", color=INK, ms=6, mew=1.0, zorder=9)
        ax.text(lx - 2, ly + 7, name, fontsize=5.4, color=INK, ha="left", va="bottom", zorder=9, **MONO)
    ax.text(x0 - 6, 0, "out", fontsize=6.2, color=BLUE, ha="right", va="center")
    ax.text(x0 - 6, 127, "in", fontsize=6.2, color=BLUE, ha="right", va="center")
    dim(ax, (x1 + 18, 0), (x1 + 18, 127), "127 µm", fs=5.8)
    scalebar(ax, x1 - 30, y0 - 6, 20, "20 µm")
    short = {"grating_coupler_elliptical": "grating couplers"}
    inst = "\n".join(f"{n} {short.get(k, k)}" for k, n in sorted(M["instances"].items(), key=lambda kv: -kv[1]))
    ax.text(x0 + 2, 64, f"extracted netlist:\n{inst}\n{M['n_nets']} nets", fontsize=5.6, color=MUTED, va="center",
            linespacing=1.25)
    panel(ax, "a", 0.0, 1.0)
    # (b) the SAX simulation of the extracted netlist
    bx = fig.add_axes([0.6, 0.17, 0.38, 0.74])
    S = M["sax"]
    bx.plot(S["wl_nm"], S["T_dB"], color=BLUE, lw=1.0)
    mins = np.array(S["minima_nm"])
    near = int(np.argmin(np.abs(mins - 1550)))
    a, b = (mins[near - 1], mins[near]) if mins[near] > 1550 else (mins[near], mins[near + 1])
    bx.annotate("", xy=(b, -32), xytext=(a, -32), arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.8, shrinkA=0, shrinkB=0, mutation_scale=6))
    bx.text((a + b) / 2, -30.5, f"{b - a:.2f} nm", fontsize=6.2, color=RED, ha="center", va="bottom")
    bx.set_xlim(1535, 1565)
    bx.set_ylim(-40, 3)
    finish(bx, xlabel="Wavelength (nm)", ylabel="Transmission (dB)")
    bx.text((a + b) / 2, -33.5, f"expected\n{S['fsr_formula_nm']:.2f}", fontsize=5.8, color=INK, ha="center", va="top")   # fits between the dips
    tag(bx, "b")
    save(fig, "ch33_gdsfactory")


def fig_floorplan():
    C = GF["chip"]
    W, H = C["die"]
    fig, ax = geom_axes(figsize=(6.4, 5.3), xlim=(-60, W + 20), ylim=(-70, H + 30))
    ax.add_patch(Rect((0, 0), W, H, fc="none", ec=INK, lw=0.9, zorder=1))
    draw_outline(ax, C["outline"], tol=0.1)
    for lab in C["labels"]:
        ax.plot(lab["x"], lab["y"], "o", color=RED, ms=3.2, zorder=10)
        ax.text(lab["x"] + 8, lab["y"] + 9, lab["text"], fontsize=6.8, color=RED, ha="left", va="bottom", zorder=10, **MONO)
    ys = [82.5 + 127 * k for k in range(6)]
    for k in range(5):
        dim(ax, (-30, ys[k]), (-30, ys[k + 1]), "127" if k else "127 µm", fs=6.8, text_off=(0, 0))
    ax.text(-30, ys[0] - 25, "fibre\narray", fontsize=7.0, color=INK, ha="center", va="top")
    # what is where (positions from the gdsfactory script: devices between their couplers, pads at 100 um pitch)
    ax.text(240, 82.5 + 127 * 1.5 + 2, "MZI, ΔL = 100 µm", fontsize=7.4, color=INK, ha="left", va="center")
    ax.text(222, 82.5 + 127 * 3 + 83, "ring with heater", fontsize=7.4, color=INK, ha="left", va="center")   # beside the ring, clear of the bus
    ax.text(W - 48, H / 2, "loopback", fontsize=7.4, color=INK, ha="center", va="center", rotation=90)
    dim(ax, (480, 680), (580, 680), "100 µm", fs=7.0, text_off=(0, 11))
    ax.text(635, 623.5, "probe pads\n80 × 80 µm", fontsize=7.4, color=INK, ha="left", va="center")
    scalebar(ax, W - 120, -45, 100, "100 µm")
    ax.text(W / 2, H + 12, f"die {W:.0f} × {H:.0f} µm", fontsize=7.6, color=INK, ha="center", va="bottom")
    save(fig, "ch33_floorplan")


def fig_routing():
    F = GF["fanin"]
    lens = F["route_lengths"]
    fig = plt.figure(figsize=(6.6, 3.7))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    frameless(ax, (-60, 300), (-30, 415))
    draw_outline(ax, F["outline"], lw_si=0.9, tol=0.05)
    gc_ports = [p for p in F["ports"] if p["type"] == "optical" and abs(p["x"]) < 1e-6 and p["o"] == 0]
    dev_ports = [p for p in F["ports"] if p["type"] == "optical" and abs(p["x"] - 250) < 1e-6 and p["o"] == 180]
    for p in gc_ports:
        port_arrow(ax, p, 14.0, lw=0.8, ms=5)
    for p in dev_ports:
        port_arrow(ax, p, 14.0, lw=0.8, ms=4)
    # route lengths, matched to their couplers (the first route leaves the lowest coupler)
    order = sorted(gc_ports, key=lambda p: p["y"])
    by_y = {175.0: 0, 180.0: 1, 185.0: 2, 190.0: 3}
    for k, p in enumerate(order):
        ax.text(p["x"] + 24, p["y"], f"route {lens[k]:.1f} µm", fontsize=5.8, color=INK, va="center",
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"), zorder=9)
    dim(ax, (-48, 0), (-48, 127), "127 µm", fs=5.8)
    ax.text(262, 199, "device ports,\n5 µm apart", fontsize=5.8, color=INK, ha="center", va="bottom")
    scalebar(ax, 200, -20, 50, "50 µm")
    ax.add_patch(Rect((0, 160), 45, 45, fc="none", ec=RED, lw=0.7, zorder=8))
    panel(ax, "a", 0.0, 1.0)
    # (b) zoom where the bundle turns: nested Euler bends at a 5 um separation
    bx = fig.add_axes([0.53, 0.06, 0.46, 0.9])
    frameless(bx, (0, 45), (160, 205))
    draw_outline(bx, F["outline"], lw_si=0.4, tol=0.005)
    for y in (175, 180, 185, 190):
        bx.plot([40, 45], [y, y], color=MAT["si"], lw=0)
    dim(bx, (38, 175), (38, 180), "5 µm", fs=5.8, text_off=(3.3, 0))
    bx.text(44, 203.5, "10 µm Euler bends, nested;\nvertical runs 5.5 µm apart", fontsize=5.8, color=INK, va="top", ha="right")   # clear of the runs
    bx.add_patch(Rect((0, 160), 45, 45, fc="none", ec=RED, lw=0.9, zorder=8))
    scalebar(bx, 30, 162, 10, "10 µm")
    panel(bx, "b", 0.0, 1.07)                      # above the frame, not on its corner
    save(fig, "ch33_routing")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    g = grid_numbers()
    print("vertices per circle for a sagitta e on the 10.25 um edge:", g["N_for_e"])
    for k, v in g["stats"].items():
        print("grid %g nm, N %d:" % k, {kk: round(vv, 3) for kk, vv in v.items()})
    print("ring228:", g["ring228"])
    print("port30:", g["port30"])
    fig_layers()
    fig_records()
    fig_hierarchy()
    fig_klayout()
    fig_gridarc()
    if GF and "fig_gdsfactory" in globals():
        fig_gdsfactory(); fig_floorplan(); fig_routing()
