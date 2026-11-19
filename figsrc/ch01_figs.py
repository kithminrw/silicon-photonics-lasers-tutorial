"""Figures for Chapter 1 (why integrated photonics).

Run from the repository root:   python -I -X utf8 figsrc/ch01_figs.py
Writes assets/figs/ch01_soi_stack.svg, ch01_dbm_ruler.svg, ch01_bands.svg and prints the numbers they show.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402

C0 = 299792.458             # speed of light, nm·THz


# ------------------------------------------------------------------ an SOI chip in cross-section
def fig_soi_stack():
    """Representative 220 nm SOI stack with the devices of a transceiver, all to one scale (µm)."""
    T_SI, T_SLAB, T_BOX, T_GE = 0.22, 0.09, 2.0, 0.5     # Ch 1, 4, 6, 21
    H_HEAT, T_HEAT, W_HEAT = 1.90, 0.12, 2.0               # TiN heater of Ch 18: bottom 1.9 µm above the BOX, 2 µm wide
    M1, T_M1, M2, T_M2, TOP = 2.6, 0.5, 3.6, 0.7, 4.7      # interconnect (representative)
    GC_P, GC_E = 0.63, 0.07                                # grating period and etch depth (Ch 15, 29)
    print("SOI stack: Si %.0f nm, slab %.0f nm, BOX %.1f µm, Ge %.1f µm, heater %.2f µm above the Si top" %
          (1e3 * T_SI, 1e3 * T_SLAB, T_BOX, T_GE, H_HEAT - T_SI))

    fig, ax = geom_axes(figsize=(6.3, 2.75), xlim=(-0.6, 28.4), ylim=(-3.55, 7.0))
    SUB = -T_BOX - 0.9
    box(ax, -0.6, SUB, 29.0, 0.9, "sub")
    box(ax, -0.6, -T_BOX, 29.0, T_BOX, "ox")
    box(ax, -0.6, 0, 29.0, TOP, "oxtop")
    for xb in (-0.6, 28.4):                                # break marks in the handle wafer
        pass
    ax.plot([-0.6, 28.4], [SUB, SUB], color=MUTED, lw=0.6, ls=(0, (4, 3)))

    # 1. grating coupler (a cut along the waveguide), with a window in the metal stack above it
    x0 = 0.4; n = 7
    box(ax, x0 - 0.3, 0, n * GC_P + 0.6, T_SI, "si", z=3)
    for k in range(n):
        box(ax, x0 + k * GC_P + GC_P / 2, T_SI - GC_E, GC_P / 2, GC_E, "oxtop", z=4)
    xg = x0 + n * GC_P / 2
    arrow(ax, (xg - 0.55, 6.55), (xg, T_SI + 0.15), col=RED, lw=1.4, ms=9)
    label(ax, xg - 0.45, 6.75, "from the fibre", col=RED, fs=6.5, ha="center", va="bottom")

    # 2. strip waveguide with a TiN heater above it (thermal phase shifter)
    xs = 7.4
    cbox(ax, xs, 0, 0.5, T_SI, "si", z=3)
    cbox(ax, xs, H_HEAT, W_HEAT, T_HEAT, "tin", z=3)
    dim(ax, (xs - 1.35, T_SI), (xs - 1.35, H_HEAT), "", fs=6.0)
    label(ax, xs - 1.5, (T_SI + H_HEAT) / 2, "1.7 µm", fs=6.0, ha="right")

    # 3. carrier-depletion modulator: rib with a p-n junction, p++/n++ contacts, W vias to M1
    xm = 14.6; half = 3.3
    box(ax, xm - half, 0, 2 * half, T_SLAB, "pdop", z=3)
    box(ax, xm, 0, half, T_SLAB, "ndop", z=3)
    box(ax, xm - 0.25, 0, 0.25, T_SI, "pdop", z=3); box(ax, xm, 0, 0.25, T_SI, "ndop", z=3)
    box(ax, xm - half, 0, 1.2, T_SLAB, "pp", z=3); box(ax, xm + half - 1.2, 0, 1.2, T_SLAB, "nn", z=3)
    for xv in (xm - half + 0.6, xm + half - 0.6):
        cbox(ax, xv, T_SLAB, 0.35, M1 - T_SLAB, "al", z=3)
        cbox(ax, xv, M1, 1.6, T_M1, "metal", z=3)

    # 4. germanium photodiode on silicon (vertical p-i-n): p Si underneath, n++ Ge top, W vias
    xp = 23.6
    box(ax, xp - 3.6, 0, 7.2, T_SI, "pdop", z=3)
    box(ax, xp - 3.6, 0, 1.1, T_SI, "pp", z=3); box(ax, xp + 2.5, 0, 1.1, T_SI, "pp", z=3)
    cbox(ax, xp, T_SI, 4.0, T_GE, "ge", z=3)
    cbox(ax, xp, T_SI + T_GE - 0.08, 4.0, 0.08, "nn", z=4)
    for xv, yb in ((xp - 3.05, T_SI), (xp + 3.05, T_SI), (xp, T_SI + T_GE)):
        cbox(ax, xv, yb, 0.35, M1 - yb, "al", z=3)
    cbox(ax, xp - 3.05, M1, 1.4, T_M1, "metal", z=3); cbox(ax, xp + 3.05, M1, 1.4, T_M1, "metal", z=3)
    cbox(ax, xp, M1, 1.4, T_M1, "metal", z=3)
    # second metal: a via up from M1 and a pad opening in the top oxide
    cbox(ax, xp, M1 + T_M1, 0.35, M2 - M1 - T_M1, "al", z=3)
    cbox(ax, xp, M2, 3.2, T_M2, "metal", z=3)
    cbox(ax, xm + half - 0.6, M1 + T_M1, 0.35, M2 - M1 - T_M1, "al", z=3)
    cbox(ax, xm + half - 0.6, M2, 2.4, T_M2, "metal", z=3)
    cbox(ax, xp, M2 + T_M2, 2.2, TOP - M2 - T_M2 + 0.01, "air", z=3)

    # labels: device names below the substrate, layer names on the left/right edges
    yl = SUB - 0.25
    for x, t in ((xg, "grating coupler\n70 nm etch"), (xs, "strip + TiN heater\n500 × 220 nm"),
                 (xm, "p–n rib modulator\n90 nm slab"), (xp, "Ge photodiode\n0.5 µm Ge")):
        label(ax, x, yl, t, fs=6.6, va="top")
    label(ax, 28.3, -1.0, "BOX\n2 µm", fs=6.4, ha="right", va="center", col=INK)
    label(ax, 28.3, SUB + 0.45, "Si handle", fs=6.4, ha="right", col=INK)
    label(ax, 28.3, 4.1, "oxide\ncladding", fs=6.4, ha="right", col=INK)
    callout(ax, (xs + 0.25, 0.11), (xs + 1.9, -0.6), "Si 220 nm", fs=6.4)
    callout(ax, (xm - half - 0.2, M1 + T_M1 / 2), (xm - half - 1.0, M1 + T_M1 / 2), "M1", fs=6.4, ha="right")
    callout(ax, (xm + half - 1.8, M2 + T_M2 / 2), (xm + half - 2.6, M2 + T_M2 / 2), "M2", fs=6.4, ha="right")
    callout(ax, (xm - half + 0.42, 1.3), (xm - half - 1.0, 1.3), "W via", fs=6.4, ha="right")
    callout(ax, (xp + 0.8, TOP), (xp + 0.8, 5.5), "pad opening", fs=6.4, ha="center", va="bottom")
    label(ax, xm - 0.9, 0.42, "p", fs=6.4); label(ax, xm + 0.9, 0.42, "n", fs=6.4)
    label(ax, xm - half + 0.6, -0.35, "p++", fs=6.0); label(ax, xm + half - 0.6, -0.35, "n++", fs=6.0)
    label(ax, xp, 0.95, "n++", fs=6.0)
    legend_patches(ax, [("si", "Si"), ("pdop", "p-doped Si"), ("ndop", "n-doped Si"), ("ge", "Ge"), ("tin", "TiN"),
                        ("al", "W"), ("metal", "Al/Cu")], loc="upper left", ncol=7, fs=6.3,
                   bbox_to_anchor=(0.12, 1.0), columnspacing=0.9, handletextpad=0.4)
    scalebar(ax, 9.6, 5.55, 2.0, "2 µm")
    note(ax, "to scale; device spacing compressed", loc="upper right")
    save(fig, "ch01_soi_stack")


# ------------------------------------------------------------------ dBm and milliwatts on one ruler
def fig_dbm_ruler():
    laser, losses, sens = 10.0, [3, 0.8, 3, 1.4, 3, 1.5], -12.0       # Worked Example 1.1
    rx = laser - sum(losses)
    margin = rx - sens
    mw = lambda d: 10 ** (d / 10)
    print("dBm ruler: laser %.1f dBm = %.2f mW; received %.1f dBm = %.3f mW; sensitivity %.1f dBm = %.1f µW; "
          "loss %.1f dB, margin %.1f dB" % (laser, mw(laser), rx, mw(rx), sens, 1e3 * mw(sens), sum(losses), margin))
    fig, ax = plt.subplots(figsize=(6.3, 2.05))
    ax.set_xlim(-43, 25); ax.set_ylim(-1.55, 2.5)
    for s in ("left", "bottom", "top", "right"): ax.spines[s].set_visible(False)
    ax.set_yticks([]); ax.set_xticks([]); ax.grid(False)
    ax.plot([-40, 20], [0, 0], color=INK, lw=1.0)
    for d in range(-40, 21, 10):
        ax.plot([d, d], [-0.13, 0.13], color=INK, lw=0.9)
        ax.text(d - (1.0 if d == 20 else 0), 0.24, (f"{d:+d}" if d else "0") + (" dBm" if d == 20 else ""),
                ha="left" if d == 20 else "center", va="bottom", fontsize=7.5, color=INK)
        p = mw(d)
        s = (f"{p:g} mW" if p >= 1 else f"{1e3*p:g} µW" if p >= 1e-3 else f"{1e6*p:g} nW")
        ax.text(d, -0.24, s, ha="center", va="top", fontsize=7.5, color=INK)
    for d in range(-40, 21):
        if d % 10: ax.plot([d, d], [-0.06, 0.06], color=INK, lw=0.5)
    # the reference-link levels
    for d, t, col, dy in ((laser, "laser\n+10 dBm = 10 mW", AMBER, 0.95), (rx, "received\n−2.7 dBm = 0.54 mW", TEAL, 1.6),
                          (sens, "receiver needs\n−12 dBm = 63 µW", RED, 0.95)):
        ax.plot([d], [0], "o", color=col, ms=5.5, zorder=5)
        ax.plot([d, d], [0.62, dy - 0.07], color=col, lw=0.8)
        ax.text(d, dy, t, ha="center", va="bottom", fontsize=6.8, color=col)
    # brackets: link loss and margin
    def bracket(a, b, y, t, col):
        ax.annotate("", (b, y), (a, y), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.8, mutation_scale=6, shrinkA=0, shrinkB=0))
        ax.text((a + b) / 2, y - 0.12, t, ha="center", va="top", fontsize=6.6, color=col)
    bracket(rx, laser, -0.95, f"losses {sum(losses):.1f} dB", INK)
    bracket(sens, rx, -0.95, f"margin {margin:.1f} dB", TEAL)
    # rules of thumb
    ax.annotate("", (-27, -0.95), (-30, -0.95), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8, mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.text(-28.5, -1.07, "+3 dB: × 2", ha="center", va="top", fontsize=6.6, color=MUTED)
    ax.annotate("", (-30, 0.75), (-40, 0.75), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8, mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.text(-35, 0.85, "+10 dB: × 10", ha="center", va="bottom", fontsize=6.6, color=MUTED)
    save(fig, "ch01_dbm_ruler")


# ------------------------------------------------------------------ telecom bands on wavelength and frequency axes
BANDS = [("O", 1260, 1360, "original"), ("E", 1360, 1460, "extended"), ("S", 1460, 1530, "short"),
         ("C", 1530, 1565, "conventional"), ("L", 1565, 1625, "long"), ("U", 1625, 1675, "ultra-long")]
CH = [1546.12, 1549.32, 1552.52, 1555.75]     # Table 1.3 (ITU 400 GHz grid)


def fig_bands():
    print("bands (nm -> THz, width):")
    for b, l0, l1, _ in BANDS:
        print(f"  {b}: {l0}-{l1} nm = {C0/l1:.2f}-{C0/l0:.2f} THz, {C0/l0 - C0/l1:.2f} THz wide")
    fch = [C0 / l for l in CH]
    print("reference-link channels (THz):", ", ".join(f"{f:.2f}" for f in fch),
          "; spacings (GHz):", ", ".join(f"{1e3*(fch[i]-fch[i+1]):.0f}" for i in range(3)),
          "; span %.2f nm" % (CH[-1] - CH[0]))
    fig = plt.figure(figsize=(6.3, 2.75))
    a = fig.add_axes([0.06, 0.52, 0.90, 0.30])
    b = fig.add_axes([0.30, 0.11, 0.42, 0.19])
    cols = [C3, C5, MUTED, C1, C2, C4]
    for (nm, l0, l1, long), col in zip(BANDS, cols):
        a.axvspan(l0, l1, color=col, alpha=0.22, lw=0)
        a.text((l0 + l1) / 2, 0.66, nm, ha="center", va="center", fontsize=9, fontweight="bold", color=INK)
        rng = f"{l0}–\n{l1}" if l1 - l0 < 40 else f"{l0}–{l1}"
        a.text((l0 + l1) / 2, 0.30, rng, ha="center", va="center", fontsize=6.2, color=INK)
    for l in CH:
        a.plot([l, l], [0.0, 0.12], color=RED, lw=0.8)
    a.set_xlim(1260, 1675); a.set_ylim(0, 1)
    a.set_yticks([]); a.grid(False)
    a.spines["left"].set_visible(False)
    a.set_xticks(range(1300, 1651, 50)); a.set_xlim(1260, 1675)
    a.set_xlabel("Wavelength (nm)", labelpad=2, loc="right")
    top = a.secondary_xaxis("top", functions=(lambda l: C0 / np.maximum(l, 1), lambda f: C0 / np.maximum(f, 1)))
    top.set_xticks(range(180, 240, 10)); top.set_xlabel("Frequency (THz)", labelpad=3)
    a.spines["top"].set_visible(True)
    # zoom on the reference-link channels
    for k, (l, f) in enumerate(zip(CH, fch)):
        b.plot([l, l], [0, 1], color=RED, lw=1.6)
        b.text(l, 1.08, f"{f:.1f}", ha="center", va="bottom", fontsize=6.4, color=RED)
    b.annotate("", (CH[1], 0.5), (CH[0], 0.5), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    b.text((CH[0] + CH[1]) / 2, 0.58, "3.2 nm\n= 400 GHz", ha="center", va="bottom", fontsize=6.2, color=INK)
    b.set_xlim(1544, 1558); b.set_ylim(0, 1); b.set_yticks([]); b.grid(False)
    b.spines["left"].set_visible(False)
    b.set_xticks([1546, 1550, 1554, 1558]); b.tick_params(labelsize=6.8)
    b.text(1557.9, 1.08, "THz", ha="left", va="bottom", fontsize=6.4, color=RED)
    b.set_xlabel("Wavelength (nm)", fontsize=7, labelpad=1)
    # guides from the C band to the zoom
    from matplotlib.patches import ConnectionPatch
    for xa, xb in ((1544, 1544), (1558, 1558)):
        fig.add_artist(ConnectionPatch((xa, -0.36), (xb, 1.42), coordsA=a.transData, coordsB=b.transData, color=MUTED, lw=0.5, ls=":"))
    fig.text(0.74, 0.20, "the four channels of\nthe reference link", fontsize=6.6, color=RED, va="center")
    save(fig, "ch01_bands")


if __name__ == "__main__":
    fig_soi_stack(); fig_dbm_ruler(); fig_bands()
