"""Block diagrams for Chapter 33 (optical links and transceivers): a coherent transceiver, and where the electrical
path runs in pluggable, linear-drive and co-packaged optics.

Run from the repository root:   python -I -X utf8 figsrc/ch33_figs.py
Writes assets/figs/ch33_coherent.svg and ch33_cpo.svg. Both are schematics without numbers.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402

OPT_C, ELE_C = RED, BLUE
FC_OPT, FC_ELE, FC_DSP = "#FBEDEA", "#EAF0FB", "#F3F6FB"


def owire(ax, pts, arrow_end=False, lw=1.3):
    wire(ax, pts, col=OPT_C, lw=lw, arrow_end=arrow_end, ms=7)


def ewire(ax, pts, arrow_end=True, lw=0.9):
    wire(ax, pts, col=ELE_C, lw=lw, arrow_end=arrow_end, ms=6)


# ------------------------------------------------------------------ Figure: coherent transceiver
def iq_modulator(ax, x0, yc, tag_):
    """Nested MZM: outer interferometer with an MZM in each arm and a 90° shifter on the lower one. Returns output x."""
    dy = 2.6
    owire(ax, [(x0, yc), (x0 + 2.0, yc + dy), (x0 + 4.0, yc + dy)]); owire(ax, [(x0, yc), (x0 + 2.0, yc - dy), (x0 + 4.0, yc - dy)])
    for s, nm in ((1, "I"), (-1, "Q")):
        block(ax, x0 + 8.0, yc + s * dy, 8.0, 2.6, f"MZM {nm}", fc=FC_OPT, ec=OPT_C, fs=6.5, z=4)
        owire(ax, [(x0 + 12.0, yc + s * dy), (x0 + 13.5, yc + s * dy)])
        ewire(ax, [(x0 + 8.0, yc + s * (dy + 3.6)), (x0 + 8.0, yc + s * (dy + 1.3))])
        label(ax, x0 + 8.9, yc + s * (dy + 3.0), tag_ + nm, fs=6.3, col=ELE_C, ha="left")
    block(ax, x0 + 15.5, yc - dy, 4.0, 2.6, "90°", fc="white", ec=OPT_C, fs=6.5, z=4)
    owire(ax, [(x0 + 13.5, yc + dy), (x0 + 19.5, yc + dy), (x0 + 21.5, yc)])
    owire(ax, [(x0 + 17.5, yc - dy), (x0 + 19.5, yc - dy), (x0 + 21.5, yc)])
    return x0 + 21.5


def fig_coherent():
    fig, ax = geom_axes(figsize=(6.3, 3.9), xlim=(0, 100), ylim=(0, 64), equal=False)
    # ---------------- transmitter (top)
    yx, yy = 54.0, 39.0
    yl = (yx + yy) / 2
    block(ax, 6.5, yl, 10.0, 6.0, "laser", fc=FC_OPT, ec=OPT_C, fs=6.8)
    owire(ax, [(11.5, yl), (14.0, yl)])
    owire(ax, [(14.0, yl), (16.0, yx), (18.0, yx)]); owire(ax, [(14.0, yl), (16.0, yy), (18.0, yy)])
    xo = iq_modulator(ax, 18.0, yx, "X"); iq_modulator(ax, 18.0, yy, "Y")
    label(ax, 29.0, yx + 7.4, "IQ modulator, polarisation X", fs=6.4, col=INK)
    label(ax, 29.0, yy - 7.5, "IQ modulator, polarisation Y", fs=6.4, col=INK)
    owire(ax, [(xo, yx), (50.0, yx), (55.0, yl + 1.0)])
    block(ax, 48.5, yy, 6.0, 3.4, "rotate", fc="white", ec=OPT_C, fs=6.0, z=4)
    owire(ax, [(xo, yy), (45.5, yy)]); owire(ax, [(51.5, yy), (53.0, yy), (55.0, yl - 1.0)])
    block(ax, 58.0, yl, 6.0, 6.0, "PBC", fc=FC_OPT, ec=OPT_C, fs=6.5, z=4)
    owire(ax, [(61.0, yl), (68.5, yl)], arrow_end=True)
    label(ax, 69.0, yl, "to fibre", fs=6.6, ha="left", col=OPT_C)
    block(ax, 88.0, yl + 3.0, 20.0, 12.0, "Tx DSP\n4 DACs + drivers", fc=FC_DSP, ec=ELE_C, fs=6.6)
    label(ax, 88.0, yl - 5.0, "drive XI, XQ, YI, YQ", fs=6.3, col=ELE_C)
    label(ax, 88.0, yl + 12.4, "data in", fs=6.3, col=ELE_C)
    ewire(ax, [(88.0, yl + 11.0), (88.0, yl + 9.0)])
    # ---------------- receiver (bottom)
    yrx, yry = 22.0, 7.0
    label(ax, 3.5, 25.2, "from fibre", fs=6.6, col=OPT_C, ha="center")
    owire(ax, [(1.0, yrx), (7.0, yrx)], arrow_end=True)
    block(ax, 10.0, yrx, 6.0, 5.0, "PSR", fc=FC_OPT, ec=OPT_C, fs=6.5, z=4)
    owire(ax, [(13.0, yrx), (26.0, yrx)])
    owire(ax, [(10.0, yrx - 2.5), (10.0, yry), (26.0, yry)])
    block(ax, 17.0, 14.75, 8.0, 4.0, "LO laser", fc=FC_OPT, ec=OPT_C, fs=6.2, z=4)
    owire(ax, [(21.0, 14.75), (22.5, 14.75)])
    owire(ax, [(22.5, 14.75), (24.3, 19.5), (26.0, 19.5)]); owire(ax, [(22.5, 14.75), (24.3, 10.0), (26.0, 10.0)])
    for yc, p in ((yrx - 1.25, "X"), (yry + 1.5, "Y")):
        block(ax, 32.0, yc, 12.0, 6.6, "90° hybrid", fc=FC_OPT, ec=OPT_C, fs=6.4, z=4)
        for k, dyo in enumerate((2.4, 0.8, -0.8, -2.4)):
            owire(ax, [(38.0, yc + dyo), (43.5, yc + dyo)], lw=1.0)
        for s_, nm in ((1, "I"), (-1, "Q")):
            yb = yc + s_ * 1.6
            block(ax, 47.0, yb, 7.0, 3.0, "BPD " + nm, fc="white", ec=INK, fs=6.0, z=4)
            ewire(ax, [(50.5, yb), (53.5, yb)])
            block(ax, 57.0, yb, 7.0, 3.0, "TIA", fc=FC_ELE, ec=ELE_C, fs=6.0, z=4)
            ewire(ax, [(60.5, yb), (63.5, yb)])
            block(ax, 67.0, yb, 7.0, 3.0, "ADC", fc=FC_ELE, ec=ELE_C, fs=6.0, z=4)
            ewire(ax, [(70.5, yb), (78.0, yb)])
        label(ax, 32.0, yc + (4.6 if p == "X" else -4.6), "polarisation " + p, fs=6.3, col=INK)
    block(ax, 88.0, 15.0, 20.0, 22.0, "Rx DSP\n\ndispersion,\npolarisation\nunscrambling,\ncarrier phase,\ndecisions",
          fc=FC_DSP, ec=ELE_C, fs=6.4)
    # separators and key
    ax.plot([1, 99], [29.0, 29.0], color=GRID, lw=0.8)
    label(ax, 1.0, 63.5, "transmitter", fs=7.0, bold=True, ha="left", va="top")
    label(ax, 1.0, 28.0, "receiver", fs=7.0, bold=True, ha="left", va="top")
    ax.plot([50, 54], [1.2, 1.2], color=OPT_C, lw=1.3); label(ax, 54.7, 1.2, "optical", fs=6.3, ha="left", col=OPT_C)
    ax.plot([63, 67], [1.2, 1.2], color=ELE_C, lw=0.9); label(ax, 67.7, 1.2, "electrical", fs=6.3, ha="left", col=ELE_C)
    note(ax, "schematic", loc="lower left")
    save(fig, "ch33_coherent")


# ------------------------------------------------------------------ Figure: pluggable, linear-drive and co-packaged optics
def fig_cpo():
    fig, ax = geom_axes(figsize=(6.3, 3.9), xlim=(0, 100), ylim=(0, 64), equal=False)
    rows = [(54.0, "a", "pluggable module (retimed)"), (33.0, "b", "linear-drive pluggable"), (10.0, "c", "co-packaged optics")]
    for yc, letter, title in rows:
        label(ax, 0.5, yc + 8.6, letter, fs=9.5, bold=True, ha="left", va="center")
        label(ax, 3.5, yc + 8.6, title, fs=7.0, ha="left", va="center", bold=True)
        # board and switch package
        box(ax, 2.0, yc - 6.0, 96.0, 1.2, "#DDE3EA")
        label(ax, 3.0, yc - 7.6, "circuit board", fs=6.0, ha="left", col=MUTED)
        box(ax, 6.0, yc - 4.8, 22.0, 1.4, "#E8DFC8", ec=MUTED, lw=0.4)           # package substrate
        block(ax, 17.0, yc - 0.6, 12.0, 7.0, "switch /\nXPU", fc=FC_DSP, ec=INK, fs=6.6, z=4)
    # (a) pluggable: long trace to a module with a DSP retimer
    for yc, dsp in ((54.0, True), (33.0, False)):
        ewire(ax, [(23.0, yc - 1.5), (70.5 if dsp else 79.5, yc - 1.5)], lw=1.4)
        label(ax, 46.0, yc + 0.3, "electrical lanes across the board", fs=6.3, col=ELE_C)
        ax.add_patch(FancyBboxPatch((66.0, yc - 5.5), 31.0, 10.6, boxstyle="round,pad=0,rounding_size=1.0", fc="none", ec=INK, lw=0.8, ls="--"))
        label(ax, 96.5, yc + 6.6, "module at the front panel", fs=6.0, ha="right", col=MUTED)
        if dsp:
            block(ax, 74.0, yc - 1.5, 7.0, 6.0, "DSP\nretimer", fc="#F6E7C8", ec=AMBER, fs=6.0, z=4)
            ewire(ax, [(77.5, yc - 1.5), (79.0, yc - 1.5)])
        else:
            label(ax, 72.5, yc + 2.6, "no DSP:\nthe host\nequalises", fs=5.8, col=MUTED)
        block(ax, 83.0, yc - 1.5, 7.0, 6.0, "drivers,\nTIAs" if dsp else "linear\ndrivers,\nTIAs", fc=FC_ELE, ec=ELE_C, fs=5.8, z=4)
        ewire(ax, [(86.5, yc - 1.5), (88.0, yc - 1.5)])
        block(ax, 92.0, yc - 1.5, 6.0, 6.0, "PIC", fc=FC_OPT, ec=OPT_C, fs=6.0, z=4)
        owire(ax, [(95.0, yc + 1.0), (99.5, yc + 1.0)], arrow_end=True)
    # (c) co-packaged optics: optical engines on the package, laser outside
    yc = 10.0
    box(ax, 6.0, yc - 4.8, 46.0, 1.4, "#E8DFC8", ec=MUTED, lw=0.4)
    for xe in (35.0, 46.0):
        block(ax, xe, yc - 1.8, 8.0, 3.0, "EIC", fc=FC_ELE, ec=ELE_C, fs=5.8, z=4)
        block(ax, xe, yc + 1.5, 8.0, 3.0, "PIC", fc=FC_OPT, ec=OPT_C, fs=5.8, z=4)
    ewire(ax, [(23.0, yc - 1.8), (31.0, yc - 1.8)], lw=1.4)
    label(ax, 27.0, yc + 0.6, "millimetres", fs=6.0, col=ELE_C)
    label(ax, 40.5, yc + 5.3, "optical engines on the package", fs=6.0, col=INK)
    owire(ax, [(50.0, yc + 1.5), (60.0, yc + 1.5), (99.5, yc + 1.5)], arrow_end=True)
    label(ax, 76.0, yc + 3.2, "data fibres to the front panel", fs=6.0, col=OPT_C)
    block(ax, 86.0, yc - 3.0, 14.0, 5.0, "laser module\n(replaceable)", fc=FC_OPT, ec=OPT_C, fs=5.8, z=4)
    owire(ax, [(79.0, yc - 3.0), (62.0, yc - 3.0), (50.2, yc + 0.6)], arrow_end=True)
    label(ax, 70.0, yc - 4.8, "CW light in by fibre", fs=6.0, col=OPT_C)
    note(ax, "schematic", loc="lower right")
    save(fig, "ch33_cpo")


if __name__ == "__main__":
    fig_coherent(); fig_cpo()
