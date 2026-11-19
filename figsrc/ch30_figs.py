"""Figures of Chapter 30 (design flow and open PDKs).

    python -I -X utf8 figsrc/ch30_figs.py

ch30_flow      the design flow as a loop, with the tools of each stage
ch30_pdk       what a process design kit contains
ch30_layout    top view of a GC-MZI-GC test cell (positions to scale) and its cell hierarchy
ch30_solvers   what a mode solver, EME and FDTD each compute (schematic)
ch30_netlist   the same cell as S-parameter blocks, its netlist and the simulated response
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

DESIGN_FC, LAB_FC = "#EEF3FA", "#FBF3E6"      # block fills: design stages / after tape-out
MONO = {"family": "monospace"}

# compact models shared by the layout and netlist figures
N0, NG, L0 = 2.446, 4.18, 1.55                 # 500 x 220 nm strip, femwell (Chapter 6)
GC_IL, GC_BW1 = 4.1, 30.6                      # SiEPIC EBeam PDK TE grating coupler: peak loss (dB), 1 dB bandwidth (nm) (Chapter 15)
R_BEND, DL = 5.0, 100.0                        # bend radius and arm-length difference of the test MZI (um)
PITCH = 127.0                                  # fibre-array pitch (um)


# ------------------------------------------------------------------ Figure 30.1
def fig_flow():
    fig, ax = geom_axes(figsize=(6.3, 2.75), xlim=(0, 10.5), ylim=(0, 4.6), equal=False)
    bw, bh = 1.62, 0.78
    xs = [1.0, 3.1, 5.2, 7.3, 9.4]
    yt, yb = 3.3, 1.05
    top = [("concept and\nspecification", "block diagram, targets\n(e.g. Ch 1 link)"),
           ("component\nsimulation", "mode solver, EME,\nFDTD (femwell, MEEP)"),
           ("compact\nmodels", "S-matrix against λ\nfor each device"),
           ("circuit\nsimulation", "netlist of models\n(SAX, SiEPIC-Tools)"),
           ("layout", "PDK cells + routing\n(KLayout, gdsfactory)")]
    bot = [("verification", "DRC, connectivity,\ndesign for test"),
           ("tape-out", "GDS file to the\nfoundry or openEBL"),
           ("fabrication", "foundry process\n(Chapter 35)"),
           ("test", "probe station,\nspectra (Chapter 36)"),
           ("analysis", "fits and statistics\n(Chapter 37)")]
    for i, (t, sub) in enumerate(top):
        block(ax, xs[i], yt, bw, bh, t, fc=DESIGN_FC, fs=7.2, bold=True)
        label(ax, xs[i], yt + bh / 2 + 0.3, sub, fs=6.0, col=MUTED)
        if i < 4:
            arrow(ax, (xs[i] + bw / 2 + 0.02, yt), (xs[i + 1] - bw / 2 - 0.02, yt), lw=0.9, ms=7)
    order = [4, 3, 2, 1, 0]                      # bottom row runs right to left
    for k, (t, sub) in enumerate(bot):
        x = xs[order[k]]
        fc = DESIGN_FC if k < 2 else LAB_FC
        block(ax, x, yb, bw, bh, t, fc=fc, fs=7.2, bold=True)
        label(ax, x, yb - bh / 2 - 0.3, sub, fs=6.0, col=MUTED)
        if k < 4:
            arrow(ax, (x - bw / 2 - 0.02, yb), (xs[order[k + 1]] + bw / 2 + 0.02, yb), lw=0.9, ms=7)
    arrow(ax, (xs[4], yt - bh / 2 - 0.02), (xs[4], yb + bh / 2 + 0.02), lw=0.9, ms=7)
    # feedback: measured data update the compact models
    ym = 1.98
    ax.plot([xs[0], xs[0], xs[2] - 0.0], [yb + bh / 2 + 0.02, ym, ym], color=C4, lw=1.1, zorder=2)
    arrow(ax, (xs[2], ym), (xs[2], yt - bh / 2 - 0.02), col=C4, lw=1.1, ms=7)
    label(ax, (xs[0] + xs[2]) / 2 - 0.1, ym + 0.17, "measured n$_\\mathrm{eff}$, n$_g$, loss and coupling update the models", fs=6.3, col=C4)
    # design iteration before layout
    ax.annotate("", xy=(xs[1] + 0.25, yt - bh / 2 - 0.02), xytext=(xs[3] - 0.25, yt - bh / 2 - 0.02),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8, ls=(0, (3, 2)), connectionstyle="arc3,rad=-0.22", mutation_scale=7))
    label(ax, 6.75, 2.5, "iterate until the\ncircuit meets the spec", fs=6.0, col=MUTED, ha="left")
    # legend
    for j, (fc, t) in enumerate(((DESIGN_FC, "designer"), (LAB_FC, "foundry and lab"))):
        block(ax, 8.9 + 0.0 * j, 2.42 - 0.3 * j, 0.24, 0.17, fc=fc, lw=0.6, r=0.03)
        label(ax, 9.1, 2.42 - 0.3 * j, t, fs=6.2, ha="left")
    save(fig, "ch30_flow")


# ------------------------------------------------------------------ Figure 30.2
def fig_pdk():
    fig = plt.figure(figsize=(6.3, 3.25))
    cards = [("layer table", "used by layout, DRC"), ("cells and PCells", "used by layout"),
             ("compact models", "used by circuit simulation"), ("design rules", "used by DRC"),
             ("layer stack", "used by mode and FDTD solvers"), ("design-for-test rules", "used by the test station")]
    cw, ch = 0.315, 0.43
    pos = [(0.005 + j * 0.335, 0.53 - i * 0.505) for i in range(2) for j in range(3)]
    axs = []
    for (t, sub), (x, y) in zip(cards, pos):
        bg = fig.add_axes([x, y, cw, ch]); frameless(bg, (0, 1), (0, 1), equal=False)
        bg.add_patch(FancyBboxPatch((0.01, 0.01), 0.98, 0.98, boxstyle="round,pad=0,rounding_size=0.04", fc="#F7F9FC", ec=GRID, lw=0.8))
        bg.text(0.05, 0.93, t, fontsize=7.5, fontweight="bold", color=INK, va="top")
        bg.text(0.05, 0.05, sub, fontsize=6.2, color=MUTED, va="bottom", style="italic")
        axs.append(bg)
    # 1 layer table
    a = axs[0]
    rows = [("si", "Si, full etch", "1/0"), ("#7F97B5", "Si, partial etch", "2/0"), ("pdop", "p implant", "20/0"),
            ("ndop", "n implant", "21/0"), ("tin", "heater", "11/0"), ("metal", "metal", "12/0"), ("white", "pad opening", "13/0")]
    for k, (m, n, num) in enumerate(rows):
        yy = 0.76 - k * 0.088
        a.add_patch(Rectangle((0.07, yy - 0.03), 0.09, 0.06, fc=MAT.get(m, m), ec=MUTED if m == "white" else "none", lw=0.5))
        a.text(0.21, yy, n, fontsize=6.3, va="center", color=INK)
        a.text(0.93, yy, num, fontsize=6.3, va="center", ha="right", color=INK, **MONO)
    a.text(0.93, 0.835, "GDS layer", fontsize=5.8, ha="right", va="center", color=MUTED)
    # 2 cells and PCells: GC, Y-branch, ring with parameters
    a = axs[1]
    gx, gy = 0.10, 0.55
    a.add_patch(Polygon([[gx, gy - 0.13], [gx + 0.17, gy - 0.008], [gx + 0.17, gy + 0.008], [gx, gy + 0.13]], fc=MAT["si"], ec="none"))
    for k in range(5):
        a.plot([gx - 0.01 - 0.018 * k] * 2, [gy - 0.12, gy + 0.12], color=MAT["si"], lw=1.6)
    a.text(gx + 0.05, gy - 0.22, "grating\ncoupler", fontsize=6, ha="center", va="top", color=INK)
    yx, yy0 = 0.40, 0.55
    a.plot([yx, yx + 0.06], [yy0, yy0], color=MAT["si"], lw=2.2)
    a.add_patch(Polygon([[yx + 0.06, yy0 - 0.012], [yx + 0.15, yy0 - 0.05], [yx + 0.15, yy0 + 0.05], [yx + 0.06, yy0 + 0.012]], fc=MAT["si"]))
    a.text(yx + 0.08, gy - 0.22, "Y-branch", fontsize=6, ha="center", va="top", color=INK)
    t = np.linspace(0, 2 * np.pi, 100); rx, ry = 0.80, 0.58
    a.plot(rx + 0.085 * np.cos(t), ry + 0.13 * np.sin(t), color=MAT["si"], lw=2.0)
    a.plot([0.66, 0.94], [ry - 0.175] * 2, color=MAT["si"], lw=2.0)
    a.text(rx, gy - 0.22, "ring PCell:\nradius, gap", fontsize=6, ha="center", va="top", color=INK)
    # 3 compact models: S-matrix and a GC transmission curve
    a = axs[2]
    a.text(0.08, 0.66, "S($\\lambda$) =", fontsize=7, va="center", color=INK)
    a.text(0.40, 0.66, "$\\left[\\matrix{S_{11} & S_{12}\\\\ S_{21} & S_{22}}\\right]$" if False else "S$_{11}$  S$_{12}$\nS$_{21}$  S$_{22}$",
           fontsize=7, va="center", color=INK, linespacing=1.5)
    a.plot([0.37, 0.36, 0.36, 0.37], [0.77, 0.77, 0.55, 0.55], color=INK, lw=0.8)
    a.plot([0.66, 0.67, 0.67, 0.66], [0.77, 0.77, 0.55, 0.55], color=INK, lw=0.8)
    inset = fig.add_axes([pos[2][0] + 0.75 * cw * 0.0 + 0.215, pos[2][1] + 0.12, 0.09, 0.19])
    lam = np.linspace(1500, 1600, 200)
    inset.plot(lam, -GC_IL - (lam - 1550) ** 2 * (1.0 / (GC_BW1 / 2) ** 2), color=C1, lw=1.0)
    inset.set_ylim(-14, -2); inset.set_xticks([1500, 1600]); inset.set_yticks([])
    inset.tick_params(labelsize=5.5, length=2, pad=1); inset.grid(False)
    inset.set_xlabel("λ (nm)", fontsize=5.5, labelpad=0); inset.set_title("|S$_{21}$|$^2$ (dB)", fontsize=5.5, pad=1, color=INK)
    a.text(0.08, 0.36, "fitted to simulation\nor measurement", fontsize=6.2, color=INK, va="center")
    # 4 design rules: min width, min gap, enclosure
    a = axs[3]
    a.add_patch(Rectangle((0.08, 0.62), 0.55, 0.07, fc=MAT["si"]))
    a.add_patch(Rectangle((0.08, 0.44), 0.55, 0.07, fc=MAT["si"]))
    a.annotate("", xy=(0.69, 0.62), xytext=(0.69, 0.69), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))
    a.annotate("", xy=(0.69, 0.51), xytext=(0.69, 0.62), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=RED, mutation_scale=5, shrinkA=0, shrinkB=0))
    a.text(0.73, 0.70, "minimum width", fontsize=6.0, va="center", color=INK)
    a.text(0.73, 0.565, "minimum gap", fontsize=6.0, va="center", color=RED)
    a.add_patch(Rectangle((0.10, 0.17), 0.30, 0.16, fc=MAT["metal"], alpha=0.35, ec="none"))
    a.add_patch(Rectangle((0.16, 0.21), 0.18, 0.08, fc=MAT["al"], ec=MUTED, lw=0.4))
    a.text(0.45, 0.25, "enclosure, density", fontsize=6.0, va="center", color=INK)
    # 5 layer stack (to scale in z: 2 um BOX, 220 nm Si, 90 nm slab, cladding)
    a = axs[4]
    sx = lambda u: 0.08 + 0.5 * u / 3.0
    sy = lambda z: 0.20 + 0.55 * (z + 2.0) / 4.6
    a.add_patch(Rectangle((sx(0), sy(-2.0)), sx(3) - sx(0), sy(0) - sy(-2.0), fc=MAT["ox"], ec=OXE_(), lw=0.4))
    a.add_patch(Rectangle((sx(0), sy(0)), sx(3) - sx(0), sy(3.5) - sy(0), fc=MAT["oxtop"], ec=OXE_(), lw=0.4))
    a.add_patch(Rectangle((sx(0), sy(0)), sx(3) - sx(0), sy(0.09) - sy(0), fc=MAT["si"]))
    a.add_patch(Rectangle((sx(1.25), sy(0)), sx(1.75) - sx(1.25), sy(0.22) - sy(0), fc=MAT["si"]))
    a.add_patch(Rectangle((sx(1.0), sy(1.9)), sx(2.0) - sx(1.0), sy(2.02) - sy(1.9) + 0.008, fc=MAT["tin"]))
    a.add_patch(Rectangle((sx(0.2), sy(2.6)), sx(1.0) - sx(0.2), sy(3.2) - sy(2.6), fc=MAT["metal"]))
    for z, txt in ((2.95, "metal"), (1.96, "heater, 1.9 µm up"), (0.45, "Si 220 nm,\n90 nm slab"), (-1.0, "BOX 2 µm")):
        a.text(0.62, sy(z), txt, fontsize=5.9, va="center", color=INK, linespacing=1.0)
    a.text(0.62, sy(3.9), "thickness, index", fontsize=5.9, va="center", color=MUTED)
    # 6 design for test: GC column at 127 um pitch with labels
    a = axs[5]
    for k in range(4):
        yy = 0.72 - k * 0.15
        a.add_patch(Polygon([[0.12, yy - 0.04], [0.20, yy - 0.004], [0.20, yy + 0.004], [0.12, yy + 0.04]], fc=MAT["si"]))
        a.plot([0.20, 0.36], [yy, yy], color=MAT["si"], lw=1.2)
    a.annotate("", xy=(0.08, 0.72), xytext=(0.08, 0.57), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))
    a.text(0.065, 0.645, "127\nµm", fontsize=5.5, ha="right", va="center", color=INK, linespacing=0.9)
    a.text(0.40, 0.72, "opt_in_TE_1550_ring1", fontsize=5.6, va="center", color=VIOLET, **MONO)
    a.text(0.40, 0.45, "couplers on the fibre-\narray pitch, one direction,\nmachine-readable labels", fontsize=6.0, va="center", color=INK)
    fig.text(0.995, 0.002, "layer numbers illustrative", fontsize=5.8, color=MUTED, style="italic", ha="right", va="bottom")
    save(fig, "ch30_pdk")


def OXE_():
    return "#AFC3DA"


# ------------------------------------------------------------------ geometry of the test cell
def mzi_cell():
    """Centre lines (um) of a GC-MZI-GC cell like the openEBL ones: GCs on a 127 um column, MZI to the right.
    Returns a dict of named paths and the component placements; prints the arm lengths."""
    R = R_BEND
    h = (DL - R * (2 * np.pi - 4)) / 2            # hairpin height that makes the long arm DL longer
    P = {}
    y0 = 0.0
    xY1 = 30.0                                    # Y-branch 1 input
    LY, SEP = 15.0, 2.75                          # Y-branch length and output separation (drawn)
    SB_L, SB_H = 20.0, 10.0 - SEP / 2             # S-bends that open the arms to +-10 um
    P["in"] = np.c_[[0, xY1], [y0, y0]]
    xa0 = xY1 + LY
    # arms: S-bend out, straight with a hairpin (upper) or plain (lower), S-bend in
    def sbend(x0, ya, yb, n=60):
        x = np.linspace(0, SB_L, n)
        return np.c_[x0 + x, ya + (yb - ya) * (1 - np.cos(np.pi * x / SB_L)) / 2]
    def arc(cx, cy, r, a0, a1, n=40):
        t = np.radians(np.linspace(a0, a1, n)); return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]
    span = 4 * R + 40.0                            # horizontal span of the hairpin section
    xs0 = xa0 + SB_L
    up = [sbend(xa0, y0 + SEP / 2, y0 + 10)]
    yU = y0 + 10
    xh = xs0 + 10.0
    up += [np.c_[[xs0, xh], [yU, yU]],
           arc(xh, yU + R, R, -90, 0), np.c_[[xh + R, xh + R], [yU + R, yU + R + h]],
           arc(xh + 2 * R, yU + R + h, R, 180, 90), np.c_[[xh + 2 * R, xh + 2 * R + 40.0], [yU + 2 * R + h] * 2],
           arc(xh + 2 * R + 40.0, yU + R + h, R, 90, 0), np.c_[[xh + 3 * R + 40.0] * 2, [yU + R + h, yU + R]],
           arc(xh + 4 * R + 40.0, yU + R, R, 180, 270), np.c_[[xh + 4 * R + 40.0, xs0 + span + 20.0], [yU, yU]]]
    xe = xs0 + span + 20.0
    up += [sbend(xe, yU, y0 + SEP / 2)]
    lo = [sbend(xa0, y0 - SEP / 2, y0 - 10), np.c_[[xs0, xe], [y0 - 10, y0 - 10]], sbend(xe, y0 - 10, y0 - SEP / 2)]
    P["upper"] = np.vstack(up); P["lower"] = np.vstack(lo)
    L = lambda p: float(np.sum(np.hypot(*np.diff(p, axis=0).T)))
    xY2 = xe + SB_L                               # Y-branch 2 (mirrored), output at xY2 + LY
    xo = xY2 + LY
    # output: right, bend up, up to the second coupler's row, bend left, back to x = 0
    out = [np.c_[[xo, xo + 15.0], [y0, y0]], arc(xo + 15.0, y0 + R, R, -90, 0), np.c_[[xo + 15.0 + R] * 2, [y0 + R, PITCH - R]],
           arc(xo + 15.0, PITCH - R, R, 0, 90), np.c_[[xo + 15.0, 0.0], [PITCH, PITCH]]]
    P["out"] = np.vstack(out)
    print(f"MZI arms: upper {L(P['upper']):.2f} um, lower {L(P['lower']):.2f} um, difference {L(P['upper']) - L(P['lower']):.2f} um (target {DL})")
    return P, dict(xY1=xY1, xY2=xY2, LY=LY, SEP=SEP, xo=xo, h=h)


def draw_gc(ax, x, y, facing=1, col=MAT["si"], z=3):
    """Grating coupler: taper from the waveguide at (x, y) back to a 12 um grating; the waveguide leaves towards +x."""
    Lt, Wg = 22.0, 12.0
    ax.add_patch(Polygon([[x, y - 0.25], [x - Lt, y - Wg / 2], [x - Lt, y + Wg / 2], [x, y + 0.25]], fc=col, ec="none", alpha=0.55, zorder=z))
    for k in range(10):
        xx = x - Lt - 0.63 * 2 * k - 0.6
        ax.plot([xx, xx], [y - Wg / 2 - 0.4 * k / 3, y + Wg / 2 + 0.4 * k / 3], color=col, lw=1.0, zorder=z)


def draw_y(ax, x, y, LY, SEP, flip=False, col=MAT["si"], z=3):
    pts = np.array([[0, -0.3], [LY * 0.4, -0.55], [LY, -SEP / 2 - 0.4], [LY, SEP / 2 + 0.4], [LY * 0.4, 0.55], [0, 0.3]])
    if flip: pts[:, 0] = LY - pts[:, 0]
    ax.add_patch(Polygon(pts + [x, y], fc=col, ec="none", zorder=z))


# ------------------------------------------------------------------ Figure 30.3
def fig_layout():
    P, g = mzi_cell()
    fig = plt.figure(figsize=(6.3, 2.95))
    ax = fig.add_axes([0.0, 0.0, 0.64, 1.0]); frameless(ax, (-50, 215), (-36, 150))
    wl = dict(color=MAT["si"], lw=1.4, solid_capstyle="butt", zorder=3)
    for k in ("in", "upper", "lower", "out"):
        ax.plot(P[k][:, 0], P[k][:, 1], **wl)
    draw_gc(ax, 0, 0); draw_gc(ax, 0, PITCH)
    draw_y(ax, g["xY1"], 0, g["LY"], g["SEP"]); draw_y(ax, g["xY2"], 0, g["LY"], g["SEP"], flip=True)
    # device-recognition boxes of the PDK cells (dashed) and their pins
    for (x0, y0, w, h) in ((-44, -9, 44, 18), (-44, PITCH - 9, 44, 18), (g["xY1"], -4, g["LY"], 8), (g["xY2"], -4, g["LY"], 8)):
        ax.add_patch(Rectangle((x0, y0), w, h, fc="none", ec=TEAL, lw=0.6, ls=(0, (3, 2)), zorder=4))
    for (x, y) in ((0, 0), (0, PITCH), (g["xY1"], 0), (g["xY1"] + g["LY"], 1.375), (g["xY1"] + g["LY"], -1.375),
                   (g["xY2"], 1.375), (g["xY2"], -1.375), (g["xY2"] + g["LY"], 0)):
        ax.plot([x], [y], marker="|", ms=4, mew=1.2, color=RED, zorder=5)
    # floor plan
    ax.add_patch(Rectangle((-48, -24), 258, 170, fc="none", ec=MUTED, lw=0.7, zorder=1))
    # labels
    label(ax, -22, -14.5, "grating coupler", fs=FS_SMALL, va="top")
    label(ax, -22, PITCH + 12, "grating coupler", fs=FS_SMALL, va="bottom")
    ax.text(-44, PITCH - 15.5, "opt_in_TE_1550_MZI1", fontsize=5.8, color=VIOLET, va="center", **MONO)
    callout(ax, (g["xY1"] + 7, -1), (g["xY1"] - 2, -20), "Y-branch", fs=FS_SMALL, ha="center")
    callout(ax, (g["xY2"] + 7, -1), (g["xY2"] + 12, -20), "Y-branch", fs=FS_SMALL, ha="center")
    xh = g["xY1"] + g["LY"] + 20 + 10 + 2 * R_BEND + 20
    label(ax, xh, 10 + 2 * R_BEND + g["h"] + 7, f"long arm: +{DL:.0f} µm", fs=FS_SMALL, va="bottom")
    label(ax, xh, -15, "short arm", fs=FS_SMALL, va="top")
    callout(ax, (g["xo"] + 15 + R_BEND, 70), (g["xo"] - 18, 82), "routed\nwaveguide,\nR = 5 µm", fs=FS_SMALL, ha="right")
    dim(ax, (-46, 0), (-46, PITCH), "", col=INK)
    label(ax, -47, PITCH / 2, "127 µm", fs=FS_SMALL, rot=90, bg="white")
    scalebar(ax, 135, 104, 50, "50 µm")
    note(ax, "positions to scale; waveguides drawn as lines", loc="lower right")
    panel(ax, "a", 0.0, 1.0)
    # legend of layers
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], color=MAT["si"], lw=2, label="Si (waveguide layer)"),
          Line2D([], [], color=TEAL, lw=0.8, ls=(0, (3, 2)), label="device recognition"),
          Line2D([], [], color=RED, lw=0, marker="|", ms=5, mew=1.2, label="pins (ports)"),
          Line2D([], [], color=MUTED, lw=0.8, label="floor plan"),
          Line2D([], [], color=VIOLET, lw=0, marker="$T$", ms=5, label="text label")]
    ax.legend(handles=hs, loc="upper left", bbox_to_anchor=(0.215, 0.76), fontsize=6.0, frameon=False, handlelength=1.6, borderaxespad=0.2)

    # (b) cell hierarchy
    b = fig.add_axes([0.655, 0.02, 0.345, 0.96]); frameless(b, (0, 1), (0, 1), equal=False)
    panel(b, "b", 0.0, 1.0)
    nodes = [(0.30, 0.88, "TOP", "chip, with floor plan", DESIGN_FC),
             (0.30, 0.66, "MZI1", "test cell", DESIGN_FC)]
    kids = [("ebeam_gc_te1550 × 2", "PDK cell, fixed"), ("ebeam_y_1550 × 2", "PDK cell, fixed"), ("Waveguide × 4", "PCell: path, width, radius")]
    for (x, y, t, s, fc) in nodes:
        block(b, x, y, 0.42, 0.09, t, fc=fc, fs=7, bold=True, r=0.012)
        b.text(x + 0.25, y, s, fontsize=6.2, color=MUTED, va="center")
    b.plot([0.30, 0.30], [0.835, 0.705], color=INK, lw=0.8)
    yk = [0.46, 0.30, 0.14]
    b.plot([0.12, 0.12], [0.615, yk[-1]], color=INK, lw=0.8)
    b.plot([0.12, 0.30], [0.615, 0.615], color=INK, lw=0.8) if False else None
    for y, (t, s) in zip(yk, kids):
        b.plot([0.12, 0.18], [y, y], color=INK, lw=0.8)
        block(b, 0.57, y + 0.012, 0.78, 0.085, "", fc="#FFFFFF", fs=6.5, r=0.012)
        b.text(0.20, y + 0.012, t, fontsize=6.5, va="center", color=INK, **MONO)
        b.text(0.20, y - 0.06, s, fontsize=6.0, va="center", color=MUTED)
    save(fig, "ch30_layout")


# ------------------------------------------------------------------ Figure 30.4
def gc_t(lam_nm):
    """Power transmission of the grating-coupler compact model: Gaussian in wavelength, GC_IL dB at 1550 nm, 1 dB down at +-BW/2."""
    return 10 ** (-(GC_IL + ((lam_nm - 1550) / (GC_BW1 / 2)) ** 2) / 10)


def fig_netlist():
    P, g = mzi_cell()
    Lu = float(np.sum(np.hypot(*np.diff(P["upper"], axis=0).T))); Ll = float(np.sum(np.hypot(*np.diff(P["lower"], axis=0).T)))
    fig = plt.figure(figsize=(6.3, 4.1))
    ax = fig.add_axes([0.0, 0.60, 1.0, 0.40]); frameless(ax, (0, 10.5), (0, 2.1), equal=False)
    panel(ax, "a", 0.0, 1.0)
    # blocks with ports
    BL = [("gc1", "gc_te1550", 1.0, 1.0, 2), ("y1", "y_branch", 3.0, 1.0, 3), ("arm1", "straight", 5.25, 1.55, 2),
          ("arm2", "straight", 5.25, 0.45, 2), ("y2", "y_branch", 7.5, 1.0, 3), ("gc2", "gc_te1550", 9.5, 1.0, 2)]
    W_, H_ = 1.25, 0.55
    for name, model, x, y, n in BL:
        block(ax, x, y, W_, H_ if n == 2 else 0.85, "", fc="#F3F6FB")
        ax.text(x, y + 0.08, name, ha="center", va="center", fontsize=7, fontweight="bold", color=INK, **MONO)
        ax.text(x, y - 0.13, f"{model}  {n}×{n}", ha="center", va="center", fontsize=5.8, color=MUTED, **MONO)
    def port(x, y, t, side):
        ax.plot([x], [y], "o", ms=3, color=RED, zorder=6)
        ax.text(x + (0.06 if side > 0 else -0.06), y + 0.1, t, fontsize=5.6, color=RED, ha="left" if side > 0 else "right", va="bottom", **MONO)
    hw = W_ / 2
    links = [((1.0 + hw, 1.0), (3.0 - hw, 1.0)), ((3.0 + hw, 1.2), (5.25 - hw, 1.55)), ((3.0 + hw, 0.8), (5.25 - hw, 0.45)),
             ((5.25 + hw, 1.55), (7.5 - hw, 1.2)), ((5.25 + hw, 0.45), (7.5 - hw, 0.8)), ((7.5 + hw, 1.0), (9.5 - hw, 1.0))]
    for p0, p1 in links:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=INK, lw=0.9, zorder=2)
    for (x, y, t, s) in ((1.0 - hw, 1.0, "o1", -1), (1.0 + hw, 1.0, "o2", 1), (3.0 - hw, 1.0, "o1", -1), (3.0 + hw, 1.2, "o2", 1),
                         (3.0 + hw, 0.8, "o3", 1), (5.25 - hw, 1.55, "o1", -1), (5.25 + hw, 1.55, "o2", 1), (5.25 - hw, 0.45, "o1", -1),
                         (5.25 + hw, 0.45, "o2", 1), (7.5 - hw, 1.2, "o2", -1), (7.5 - hw, 0.8, "o3", -1), (7.5 + hw, 1.0, "o1", 1),
                         (9.5 - hw, 1.0, "o2", -1), (9.5 + hw, 1.0, "o1", 1)):
        port(x, y, t, s)
    arrow(ax, (0.0, 1.0), (1.0 - hw - 0.05, 1.0), col=OPT, lw=1.0)
    ax.text(0.02, 0.88, "in", fontsize=6.5, color=OPT, va="top")
    arrow(ax, (9.5 + hw + 0.05, 1.0), (10.45, 1.0), col=OPT, lw=1.0)
    ax.text(10.45, 0.88, "out", fontsize=6.5, color=OPT, ha="right", va="top")
    ax.text(5.25, 1.95, f"L = {Lu:.1f} µm", ha="center", fontsize=6.2, color=INK)
    ax.text(5.25, 0.07, f"L = {Ll:.1f} µm", ha="center", fontsize=6.2, color=INK)
    # (b) netlist text
    b = fig.add_axes([0.0, 0.0, 0.42, 0.57]); frameless(b, (0, 1), (0, 1), equal=False)
    panel(b, "b", 0.0, 1.0)
    txt = ("instances:\n"
           "  gc1, gc2:   gc_te1550\n"
           "  y1, y2:     y_branch\n"
           f"  arm1: straight(L={Lu:.1f})\n"
           f"  arm2: straight(L={Ll:.1f})\n"
           "connections:\n"
           "  gc1,o2 - y1,o1\n"
           "  y1,o2 - arm1,o1   y1,o3 - arm2,o1\n"
           "  arm1,o2 - y2,o2   arm2,o2 - y2,o3\n"
           "  y2,o1 - gc2,o2\n"
           "ports:\n"
           "  in: gc1,o1     out: gc2,o1")
    b.add_patch(FancyBboxPatch((0.04, 0.12), 0.94, 0.77, boxstyle="round,pad=0,rounding_size=0.03", fc="#F7F9FC", ec=GRID, lw=0.8))
    b.text(0.08, 0.85, txt, fontsize=6.6, va="top", ha="left", color=INK, linespacing=1.38, **MONO)
    # (c) circuit response: the GC envelope times the MZI fringes
    lam = np.linspace(1500, 1600, 4001)
    beta = 2 * np.pi * (N0 - (NG - N0) * (lam / 1000 - L0) / L0) / (lam / 1000)       # rad/um
    alpha = 2.0 / 4.343 * 1e-4 / 2                                                     # field loss, 2 dB/cm, per um
    e = 0.5 * (np.exp((-1j * beta - alpha) * Lu) + np.exp((-1j * beta - alpha) * Ll))   # ideal Y-branches
    T = gc_t(lam) ** 2 * np.abs(e) ** 2
    TdB = 10 * np.log10(T)
    fsr = (L0 * 1000) ** 2 / (NG * (Lu - Ll) * 1000)
    print(f"MZI: FSR at 1550 nm = {fsr:.2f} nm; peak transmission {TdB.max():.2f} dB (2 x {GC_IL} dB couplers)")
    c = fig.add_axes([0.53, 0.09, 0.45, 0.44])
    c.plot(lam, TdB, color=C1, lw=0.9, label="GC → MZI → GC")
    c.plot(lam, 10 * np.log10(gc_t(lam) ** 2), color=C2, lw=1.2, ls="--", label="two couplers alone")
    c.set_xlim(1500, 1600); c.set_ylim(-50, 6)
    finish(c, xlabel="wavelength (nm)", ylabel="transmission (dB)")
    c.legend(loc="upper right", fontsize=6.3, ncol=1, borderaxespad=0.1, handlelength=1.6)
    c.annotate("", xy=(1550 + fsr / 2 + 0.0, -3.5), xytext=(1550 - fsr / 2, -3.5), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))
    c.text(1550, -2.2, f"FSR {fsr:.1f} nm", ha="center", fontsize=6.3, color=INK)
    tag(c, "c")
    save(fig, "ch30_netlist")


# ------------------------------------------------------------------ Figure 30.5 (solvers)
def fig_solvers():
    import matplotlib.tri as mtri
    fig = plt.figure(figsize=(6.3, 2.55))
    titles = [("mode solver (FDE, FEM)", "a cross-section → its modes:\n$n_\\mathrm{eff}$, $n_g$, fields, overlaps"),
              ("eigenmode expansion (EME)", "a device that changes along z,\ncut into sections → S-matrix"),
              ("FDTD", "Maxwell's equations on a grid,\nstepped in time → any geometry")]
    axs = []
    for k, (t, sub) in enumerate(titles):
        a = fig.add_axes([0.005 + k * 0.335, 0.2, 0.32, 0.66])
        fig.text(0.005 + k * 0.335 + 0.16, 0.95, t, ha="center", va="center", fontsize=7.5, fontweight="bold", color=INK)
        fig.text(0.005 + k * 0.335 + 0.16, 0.115, sub, ha="center", va="center", fontsize=6.3, color=MUTED, linespacing=1.15)
        axs.append(a)
    rng = np.random.default_rng(3)
    # (a) cross-section of the 500 x 220 nm strip with a mesh that is finer near the core, and the TE0-like intensity
    a = axs[0]; frameless(a, (-1.3, 1.3), (-0.9, 1.1))
    box(a, -1.3, -0.9, 2.6, 0.9, "ox", z=1); box(a, -1.3, 0, 2.6, 1.1, "oxtop", z=1)
    pts = [np.c_[rng.uniform(-1.3, 1.3, 110), rng.uniform(-0.9, 1.1, 110)]]
    near = np.c_[rng.normal(0, 0.4, 170), rng.normal(0.11, 0.25, 170)]
    pts.append(near[(np.abs(near[:, 0]) < 1.3) & (near[:, 1] > -0.9) & (near[:, 1] < 1.1)])
    corners = np.array([[x, y] for x in (-1.3, 1.3) for y in (-0.9, 1.1)] + [[x, y] for x in (-0.25, 0.25) for y in (0, 0.22)])
    P = np.vstack(pts + [corners])
    tri = mtri.Triangulation(P[:, 0], P[:, 1])
    a.triplot(tri, color=MUTED, lw=0.3, alpha=0.6, zorder=2)
    box(a, -0.25, 0, 0.5, 0.22, "si", z=3, alpha=0.9)
    xx, yy = np.meshgrid(np.linspace(-1.3, 1.3, 200), np.linspace(-0.9, 1.1, 160))
    I = np.exp(-(xx / 0.38) ** 2 - ((yy - 0.11) / 0.22) ** 2)
    a.contour(xx, yy, I, levels=[0.2, 0.5, 0.8], colors=[RED], linewidths=0.8, zorder=4)
    label(a, 0.55, 0.62, "|E|²", fs=6.3, col=RED, ha="left")
    # (b) EME: a taper cut into sections, with a local mode in each
    b = axs[1]; frameless(b, (-0.5, 10.5), (-2.4, 3.0), equal=False)
    xs = np.linspace(0, 10, 7); w = lambda x: 0.5 + 2.5 * x / 10
    b.add_patch(Polygon([[0, -w(0) / 2], [10, -w(10) / 2], [10, w(10) / 2], [0, w(0) / 2]], fc=MAT["si"], ec="none", alpha=0.35, zorder=1))
    for i in range(6):
        xm = (xs[i] + xs[i + 1]) / 2
        box(b, xs[i], -w(xm) / 2, xs[i + 1] - xs[i], w(xm), "si", z=2, alpha=0.85)
        yy = np.linspace(-1.9, 1.9, 80); prof = np.exp(-(yy / (0.45 * w(xm) + 0.1)) ** 2)
        b.plot(xm + 0.55 * prof - 0.25, yy, color=RED, lw=0.8, zorder=3)
    for x in xs:
        b.plot([x, x], [-2.2, 2.2], color=INK, lw=0.6, ls=(0, (2, 1.5)), zorder=4)
    arrow(b, (0.2, 2.55), (3.2, 2.55), col=INK, lw=0.8, ms=6); arrow(b, (3.2, 2.85), (0.2, 2.85), col=MUTED, lw=0.8, ms=6)
    label(b, 3.5, 2.7, "forward and backward modes\nmatched at each interface", fs=5.9, ha="left")
    # (c) FDTD: a strip waveguide on a coarse drawing of the grid, with a field snapshot of a pulse
    c = axs[2]; frameless(c, (0, 10), (-2.4, 3.0), equal=False)
    xx, yy = np.meshgrid(np.linspace(0, 10, 400), np.linspace(-2.4, 2.4, 120))
    core = np.abs(yy) < 0.35
    E = np.cos(2 * np.pi * xx / 0.9) * np.exp(-((xx - 5.5) / 1.6) ** 2) * np.where(core, 1.0, np.exp(-(np.abs(yy) - 0.35) / 0.35))
    c.imshow(E, extent=(0, 10, -2.4, 2.4), origin="lower", cmap=SIGNED_CMAP, vmin=-1, vmax=1, aspect="auto", zorder=1, interpolation="bilinear")
    c.plot([0, 10], [0.35, 0.35], color=INK, lw=0.6, zorder=3); c.plot([0, 10], [-0.35, -0.35], color=INK, lw=0.6, zorder=3)
    for x in np.arange(0, 10.01, 0.5):
        c.plot([x, x], [-2.4, 2.4], color=INK, lw=0.25, alpha=0.35, zorder=2)
    for y in np.arange(-2.4, 2.41, 0.4):
        c.plot([0, 10], [y, y], color=INK, lw=0.25, alpha=0.35, zorder=2)
    arrow(c, (6.6, 2.7), (9.2, 2.7), col=INK, lw=0.8, ms=6)
    label(c, 6.4, 2.7, "pulse, step by step in time", fs=5.9, ha="right")
    for k in range(3):
        panel(axs[k], "abc"[k], 0.0, 1.12)
    fig.text(0.995, 0.005, "schematic: meshes, fields and grids not to scale", fontsize=6, color=MUTED, style="italic", ha="right", va="bottom")
    save(fig, "ch30_solvers")


if __name__ == "__main__":
    which = sys.argv[1:] or ["flow", "pdk", "layout", "netlist", "solvers"]
    for k in which:
        globals()["fig_" + k]()
