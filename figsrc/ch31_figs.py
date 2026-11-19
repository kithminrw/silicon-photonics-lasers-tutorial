"""Figures of Chapter 31 (testing photonic chips).

    python -I -X utf8 figsrc/ch31_figs.py

ch31_setup     the passive test setup (block diagram with the chip in side view)
ch31_dft       a design-for-test coupler row with the fibre array's footprint: loopback, device, cutback spiral
ch31_probe     DC needles and a GSG probe on an active device, with the instruments
ch31_liv       laser test: setup, L-I-V with the extracted parameters, threshold against temperature (synthetic)
ch31_rf        high-speed tests: frequency domain (lightwave component analyser) and time domain (eye, BER)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from matplotlib.lines import Line2D

INSTR = "#F3F6FB"
LH = [Line2D([], [], color=OPT, lw=1.4, label="optical (fibre)"), Line2D([], [], color=ELEC, lw=1.0, label="electrical")]


def legend_paths(ax, loc="lower left", bbox=None, extra=(), ncol=1):
    kw = dict(loc=loc, fontsize=6.3, frameon=False, handlelength=1.8, ncol=ncol)
    if bbox: kw["bbox_to_anchor"] = bbox
    ax.legend(handles=LH + list(extra), **kw)


def paddles(ax, x, y, r=0.13, n=3, dx=0.32):
    for k in range(n):
        xc = x + (k - (n - 1) / 2) * dx
        ax.add_patch(Ellipse((xc, y), 2 * r * 0.75, 2 * r * 1.6, fc="white", ec=INK, lw=0.8, zorder=4))


def owire(ax, pts, arrow_end=True):
    wire(ax, pts, col=OPT, lw=1.3, arrow_end=arrow_end, ms=7)


def ewire(ax, pts, arrow_end=True, ls="-"):
    wire(ax, pts, col=ELEC, lw=0.9, arrow_end=arrow_end, ms=6, ls=ls)


# ------------------------------------------------------------------ Figure 31.1
def fig_setup():
    fig, ax = geom_axes(figsize=(6.3, 3.1), xlim=(0, 10.6), ylim=(0, 5.2), equal=False)
    yo = 4.15
    block(ax, 0.95, yo, 1.6, 0.8, "tunable laser\n1500–1600 nm", fc=INSTR, fs=6.8)
    ax.add_patch(Circle((2.25, yo), 0.07, fc=OPT, ec="none", zorder=5))
    owire(ax, [(1.75, yo), (2.25, yo)], arrow_end=False)
    owire(ax, [(2.25, yo), (2.25, 3.03)])
    block(ax, 2.25, 2.75, 1.25, 0.55, "reference\ndetector", fc=INSTR, fs=6.4)
    label(ax, 2.36, 3.6, "tap", fs=6.2, ha="left", col=OPT)
    owire(ax, [(2.25, yo), (3.05, yo)], arrow_end=False)
    block(ax, 3.75, yo, 1.4, 0.8, "", fc=INSTR)
    paddles(ax, 3.75, yo + 0.1)
    label(ax, 3.75, yo - 0.27, "polarisation ctrl", fs=6.2)
    # fibre array over the chip (side view)
    xa, ya = 6.0, 3.05
    ax.plot([4.45, 5.25, 5.82], [yo, yo, ya + 0.75], color=OPT, lw=1.3, zorder=3)
    label(ax, 4.85, yo + 0.12, "PM fibre", fs=6.2, col=OPT, va="bottom")
    poly(ax, [(xa - 0.38, ya), (xa + 0.38, ya), (xa + 0.48, ya + 0.75), (xa - 0.28, ya + 0.75)], "glass", ec=MUTED, lw=0.6, z=4)
    ax.plot([xa - 0.14, xa - 0.04], [ya + 0.75, ya + 0.02], color=OPT, lw=1.0, zorder=5)
    ax.plot([xa + 0.14, xa + 0.24], [ya + 0.75, ya + 0.02], color=OPT, lw=1.0, zorder=5)
    ax.plot([xa + 0.24, 6.6, 7.4], [ya + 0.75, yo, yo], color=OPT, lw=1.3, zorder=3)
    callout(ax, (xa - 0.33, ya + 0.35), (4.9, 3.3), "fibre array", fs=6.3, ha="right")
    box(ax, 5.1, 2.55, 1.8, 0.42, "si", z=3)
    box(ax, 5.1, 2.97, 1.8, 0.05, "ox", z=3)
    for k in range(4):
        box(ax, 5.75 + 0.14 * k, 2.97, 0.07, 0.04, "#6F86A3", z=4)
    label(ax, 6.0, 2.76, "chip", fs=6.3)
    box(ax, 4.9, 2.25, 2.2, 0.3, "metal", z=3)
    label(ax, 6.0, 2.4, "temperature-controlled stage", fs=5.9)
    box(ax, 4.75, 1.85, 2.5, 0.4, "al", z=2)
    label(ax, 6.0, 2.05, "motorised XYZ stages", fs=5.9)
    block(ax, 8.6, yo, 1.9, 0.8, "power meters /\nphotodetectors", fc=INSTR, fs=6.6)
    arrow(ax, (7.4, yo), (7.64, yo), col=OPT, lw=1.3)
    block(ax, 8.6, 2.6, 1.9, 0.55, "temperature\ncontroller", fc=INSTR, fs=6.4)
    ewire(ax, [(7.65, 2.6), (7.25, 2.6), (7.25, 2.4), (7.1, 2.4)], arrow_end=False)
    # computer and control lines
    block(ax, 5.3, 0.55, 8.6, 0.6, "computer: sweep, alignment, temperature, data", fc="#E9EEF6", fs=6.8)
    yc = 0.85
    for x, y in ((0.95, yo - 0.4), (2.25, 2.475), (6.0, 1.85), (8.6, 2.325)):
        ax.plot([x, x], [yc, y], color=ELEC, lw=0.9, zorder=1)
    ax.plot([9.9, 9.9, 9.55], [yc, yo, yo], color=ELEC, lw=0.9, zorder=1)
    ax.plot([0.95, 0.95, 8.6, 8.6], [yo + 0.4, 4.95, 4.95, yo + 0.4], color=ELEC, lw=0.8, ls=(0, (3, 2)), zorder=1)
    label(ax, 4.7, 5.02, "trigger: the detectors sample in step with the wavelength sweep", fs=6.2, col=ELEC, va="bottom")
    legend_paths(ax, loc="lower left", bbox=(0.0, 0.17), extra=[Line2D([], [], color=ELEC, lw=0.8, ls=(0, (3, 2)), label="trigger")])
    note(ax, "not to scale")
    save(fig, "ch31_setup")


# ------------------------------------------------------------------ Figure 31.2
def fig_dft():
    P, CLAD, MFD = 127.0, 125.0, 10.4          # array pitch, fibre cladding diameter, SMF-28 mode field diameter at 1550 nm (um)
    R_RING, GAP, ENL = 10.0, 0.25, 3.0          # ring of Table 12.1, drawn enlarged ENL times
    fig, ax = geom_axes(figsize=(6.3, 3.25), xlim=(-95, 705), ylim=(-150, 262))
    xs = [k * P for k in range(6)]
    wl = dict(color=MAT["si"], lw=1.3, zorder=3, solid_capstyle="butt")

    def gc(x):   # grating below, waveguide leaving upwards from (x, 0)
        ax.add_patch(Polygon([[x - 0.25, 0], [x - 6, -22], [x + 6, -22], [x + 0.25, 0]], fc=MAT["si"], ec="none", alpha=0.6, zorder=3))
        for k in range(10):
            yy = -23 - 1.26 * k
            ax.plot([x - 6 - 0.1 * k, x + 6 + 0.1 * k], [yy, yy], color=MAT["si"], lw=0.8, zorder=3)
    for x in xs:
        gc(x)
        ax.add_patch(Circle((x, -28), CLAD / 2, fc=MAT["glass"], ec=MUTED, lw=0.5, alpha=0.5, zorder=2))
        ax.add_patch(Circle((x, -28), MFD / 2, fc=MAT["core"], ec=AMBER, lw=0.5, zorder=4))
    t = np.linspace(np.pi, 0, 80)
    # loopback: couplers 1 and 2
    yl = 30.0
    ax.plot(np.r_[xs[0], xs[0] + P / 2 + P / 2 * np.cos(t), xs[1]], np.r_[0, yl + P / 2 * np.sin(t), 0], **wl)
    label(ax, P / 2, yl + P / 2 + 14, "loopback", fs=FS, bold=True)
    # device: a ring next to the bus between couplers 3 and 4
    yd = 150.0
    ax.plot(np.r_[xs[2], xs[2] + P / 2 + P / 2 * np.cos(t), xs[3]], np.r_[0, yd + P / 2 * np.sin(t), 0], **wl)
    rr = ENL * R_RING
    ax.add_patch(Circle((xs[2] - ENL * GAP - rr - 0.0, 85), rr, fc="none", ec=MAT["si"], lw=1.3, zorder=3))
    label(ax, 2.5 * P, yd + P / 2 + 14, "device under test", fs=FS, bold=True)
    label(ax, xs[2] - ENL * GAP - rr, 85 + rr + 12, "ring (×3)", fs=FS_SMALL, col=MUTED)
    # cutback spiral between couplers 5 and 6
    cx, cy, r0, pitch, turns = 4.5 * P, 175.0, 14.0, 7.0, 4
    th = np.linspace(0, turns * 2 * np.pi, 900)
    r = r0 + pitch * th / (2 * np.pi)
    sx, sy = cx + r * np.cos(th), cy + r * np.sin(th)
    ax.plot(sx, sy, **wl); ax.plot(2 * cx - sx, 2 * cy - sy, **wl)
    ax.plot([sx[0], 2 * cx - sx[0]], [sy[0], 2 * cy - sy[0]], **wl)
    re = r[-1]
    ax.plot([xs[5], xs[5], cx + re], [0, cy, cy], **wl)
    ax.plot([xs[4], xs[4], cx - re], [0, cy, cy], **wl)
    label(ax, cx, cy + re + 14, "cutback spiral", fs=FS, bold=True)
    # machine-readable labels, vertical beside each input coupler
    for x, code in ((xs[0], "opt_in_TE_1550_loopback"), (xs[2], "opt_in_TE_1550_ring250"), (xs[4], "opt_in_TE_1550_spiral1")):
        ax.text(x + (-9 if code.endswith("loopback") else 9), 8, code, fontsize=5.5, color=VIOLET, va="bottom", ha="center", rotation=90, family="monospace")
    # dimensions and notes
    dim(ax, (xs[0], -112), (xs[1], -112), "", col=INK)
    label(ax, P / 2, -124, "127 µm", fs=FS_SMALL, va="top")
    callout(ax, (xs[3] + 40, -28 - 40), (xs[3] + 20, -132), "fibre claddings (125 µm) and mode fields (10.4 µm)\nof the fibre array, over the couplers", fs=FS_SMALL, ha="left")
    scalebar(ax, -80, 225, 100, "100 µm")
    note(ax, "to scale except the ring (×3); waveguides drawn as lines", loc="upper right")
    print(f"DFT: pitch {P} um, cladding {CLAD} um ({P - CLAD:.0f} um between fibres), MFD {MFD} um; spiral outer radius {re:.0f} um")
    save(fig, "ch31_dft")


# ------------------------------------------------------------------ Figure 31.3
def fig_probe():
    fig, ax = geom_axes(figsize=(6.3, 3.0), xlim=(0, 10.6), ylim=(0, 5.0), equal=False)
    # chip
    box(ax, 2.3, 0.55, 5.6, 3.55, "#E7EDF5", ec=MUTED, lw=0.6, z=1)
    label(ax, 2.4, 0.7, "chip (top view)", fs=6.2, col=MUTED, ha="left")
    # couplers and bus
    for y in (3.2, 1.6):
        poly(ax, [(2.95, y - 0.02), (2.6, y - 0.16), (2.6, y + 0.16), (2.95, y + 0.02)], "si", z=3)
    wl = dict(color=MAT["si"], lw=1.6, zorder=3)
    t = np.linspace(np.pi / 2, -np.pi / 2, 60)
    ax.plot(np.r_[2.95, 5.3, 5.3 + 0.8 * np.cos(t), 5.3, 2.95], np.r_[3.2, 3.2, 2.4 + 0.8 * np.sin(t), 1.6, 1.6], **wl)
    # ring modulator: PN junction (p outside, n inside) and a heater arc on top
    xr, yr, rr = 4.3, 2.63, 0.45
    ax.add_patch(Circle((xr, yr), rr + 0.06, fc=MAT["pdop"], ec="none", zorder=2))
    ax.add_patch(Circle((xr, yr), rr - 0.06, fc=MAT["ndop"], ec="none", zorder=2))
    ax.add_patch(Circle((xr, yr), rr, fc="none", ec=MAT["si"], lw=1.6, zorder=3))
    ax.add_patch(Circle((xr, yr), rr - 0.17, fc="#E7EDF5", ec="none", zorder=2))
    ax.add_patch(Wedge((xr, yr), rr + 0.03, 120, 240, width=0.06, fc=MAT["tin"], ec="none", zorder=4))
    # metal: heater (left arc) to two DC pads at the top, junction to G-S-G pads at the right
    def pad(x, y, s=0.42, txt=""):
        box(ax, x - s / 2, y - s / 2, s, s, "metal", z=3)
        if txt: label(ax, x, y, txt, fs=6.3, bold=True)
    ca, sa = np.cos(np.radians(120)) * rr, np.sin(np.radians(120)) * rr
    pads_dc = [(3.45, 3.65), (xr + ca, 3.65)]
    for (x, y) in pads_dc: pad(x, y)
    mt = dict(color=MAT["metal"], lw=1.2, zorder=2)
    ax.plot([xr + ca, xr + ca], [yr + sa, 3.44], **mt)
    ax.plot([xr + ca, 3.45, 3.45], [yr - sa, yr - sa, 3.44], **mt)
    gsg = [(7.25, yr + 0.65, "G"), (7.25, yr, "S"), (7.25, yr - 0.65, "G")]
    for (x, y, s) in gsg: pad(x, y, 0.48, s)
    ax.plot([xr, 7.0], [yr, yr], **mt)                                                   # n (inside) to S
    ax.plot([xr + 0.2, xr + 0.2, 6.6, 6.6], [yr - rr - 0.06, 1.25, 1.25, yr + 0.65], **mt)  # p (outside) to both G
    for y in (yr + 0.65, yr - 0.65): ax.plot([6.6, 7.0], [y, y], **mt)
    ax.plot([xr], [yr], "o", ms=2.5, color=MAT["metal"], zorder=4)
    label(ax, 4.62, 2.02, "ring: PN junction,\nheater on the left", fs=6.0, va="top", ha="left")
    # fibre array over the couplers
    box(ax, 1.65, 1.2, 1.1, 2.4, "glass", ec=MUTED, lw=0.6, z=4, alpha=0.85)
    for y in (3.2, 1.6):
        ax.add_patch(Circle((2.68, y), 0.06, fc=MAT["core"], ec=AMBER, lw=0.5, zorder=5))
    label(ax, 2.2, 2.4, "fibre\narray", fs=6.0)
    block(ax, 0.75, 3.2, 1.2, 0.5, "laser", fc=INSTR, fs=6.4)
    block(ax, 0.75, 1.6, 1.2, 0.5, "detector", fc=INSTR, fs=6.4)
    owire(ax, [(1.35, 3.2), (1.65, 3.2)]); owire(ax, [(1.65, 1.6), (1.36, 1.6)])
    # DC needles from the top
    for (x, y) in pads_dc:
        poly(ax, [(x - 0.03, y + 0.05), (x + 0.03, y + 0.05), (x + 0.45, 4.65), (x + 0.33, 4.65)], "#7E8794", z=6)
    block(ax, 6.0, 4.62, 1.9, 0.48, "source-measure unit", fc=INSTR, fs=6.4)
    ewire(ax, [(3.84, 4.66), (5.05, 4.66)], arrow_end=False)
    ewire(ax, [(5.33, 4.66), (5.05, 4.66)], arrow_end=False)
    label(ax, 3.2, 4.4, "DC needles", fs=6.3, ha="right")
    # GSG probe from the right
    poly(ax, [(7.3, 3.4), (7.3, 1.86), (8.3, 2.13), (9.0, 2.38), (9.0, 2.88), (8.3, 3.13)], "#9AA3B0", z=6, alpha=0.95)
    for (x, y, s) in gsg:
        ax.plot([7.4, 7.65], [y, y], color=INK, lw=1.0, zorder=7)
    label(ax, 8.3, 2.63, "GSG\nprobe", fs=6.2, z=8)
    block(ax, 9.75, 3.75, 1.5, 0.48, "bias tee", fc=INSTR, fs=6.4)
    block(ax, 9.75, 4.6, 1.5, 0.45, "DC bias", fc=INSTR, fs=6.4)
    block(ax, 9.75, 1.0, 1.5, 0.65, "network\nanalyser", fc=INSTR, fs=6.4)
    ewire(ax, [(9.0, 2.63), (9.75, 2.63), (9.75, 3.51)], arrow_end=False)
    ewire(ax, [(9.75, 4.38), (9.75, 3.99)], arrow_end=False)
    ewire(ax, [(10.3, 3.51), (10.3, 1.33)], arrow_end=False)
    label(ax, 10.38, 2.45, "RF", fs=6.0, ha="left", col=ELEC)
    label(ax, 6.0, 0.25, "heater: IV and tuning against power   ·   junction: IV, shift against bias, and S$_{21}$ through the GSG probe", fs=6.2, col=INK)
    note(ax, "not to scale", loc="upper left")
    save(fig, "ch31_probe")


# ------------------------------------------------------------------ Figure 31.4
ITH25, ETA, V0, RS, T0 = 19.0, 0.21, 0.85, 5.0, 60.0     # Chapter 24 FP laser: mA, W/A per facet, V, ohm, K


def laser_liv(I, T, rng):
    """Synthetic L-I-V of the Chapter 24 laser at heat-sink temperature T (no self-heating). I in mA."""
    ith = ITH25 * np.exp((T - 25) / T0)
    s = 0.35
    P = ETA * s * np.log1p(np.exp((I - ith) / s)) + 2e-4 * I                     # mW (W/A x mA), soft knee + spontaneous emission
    nvt, I0 = 2 * 0.02585, ith / np.exp(V0 / (2 * 0.02585))               # diode reaching V0 at threshold
    Vj = np.minimum(nvt * np.log1p(I / I0), V0 + 0 * I)                           # junction voltage clamps above threshold
    V = Vj + RS * I * 1e-3
    return P + rng.normal(0, 0.012, I.size), V + rng.normal(0, 0.002, I.size), ith


def fig_liv():
    rng = np.random.default_rng(31)
    I = np.arange(0, 80.01, 0.5)
    fig = plt.figure(figsize=(6.3, 4.0))
    # (a) setup
    ax = fig.add_axes([0.0, 0.62, 1.0, 0.38]); frameless(ax, (0, 10.6), (0, 2.0), equal=False)
    panel(ax, "a", 0.0, 1.0)
    block(ax, 1.0, 1.05, 1.5, 0.7, "current source,\nvoltage sense", fc=INSTR, fs=6.3)
    block(ax, 2.75, 1.05, 1.1, 0.7, "laser\non TEC", fc="#FBF3E6", fs=6.3)
    ewire(ax, [(1.75, 1.05), (2.2, 1.05)])
    block(ax, 4.25, 1.05, 1.0, 0.7, "lens,\nfibre", fc=INSTR, fs=6.3)
    owire(ax, [(3.3, 1.05), (3.75, 1.05)])
    block(ax, 5.55, 1.05, 0.95, 0.7, "isolator", fc=INSTR, fs=6.3)
    owire(ax, [(4.75, 1.05), (5.08, 1.05)])
    ax.add_patch(Circle((6.45, 1.05), 0.1, fc=OPT, ec="none", zorder=5))
    owire(ax, [(6.03, 1.05), (6.45, 1.05)], arrow_end=False)
    outs = [(1.78, "power meter: L–I"), (1.3, "optical spectrum analyser: spectrum, SMSR"),
            (0.82, "fast photodiode + electrical spectrum analyser: RIN"), (0.34, "delayed self-heterodyne: linewidth")]
    for y, t_ in outs:
        owire(ax, [(6.45, 1.05), (6.9, y), (7.15, y)])
        ax.text(7.2, y, t_, fontsize=6.3, va="center", color=INK)
    label(ax, 6.45, 1.36, "split", fs=5.8, col=OPT)
    # (b) L-I-V at 25 C with the extraction
    b = fig.add_axes([0.08, 0.08, 0.38, 0.45])
    P, V, ith = laser_liv(I, 25.0, rng)
    sel = (I > 1.3 * ith) & (I < 3.5 * ith)
    k, c0 = np.polyfit(I[sel], P[sel], 1)
    ith_fit = -c0 / k
    kv, cv = np.polyfit(I[sel] * 1e-3, V[sel], 1)
    print(f"LIV 25 C: true Ith {ith:.1f} mA; fitted Ith {ith_fit:.2f} mA, slope {k:.3f} W/A, Rs {kv:.2f} ohm, V(0) {cv:.3f} V")
    b.plot(I, P, ".", ms=2.2, color=C1, label="output power")
    xx = np.linspace(ith_fit, 80, 10)
    b.plot(xx, k * xx + c0, color=C1, lw=0.8, ls="--")
    b.set_xlim(0, 80); b.set_ylim(0, 14)
    finish(b, xlabel="current (mA)", ylabel="power per facet (mW)")
    b2 = b.twinx()
    b2.plot(I, V, ".", ms=2.2, color=C2)
    b2.plot(I, kv * I * 1e-3 + cv, color=C2, lw=0.8, ls="--")
    b2.set_ylim(0, 1.8); b2.set_ylabel("voltage (V)", color=C2); b2.tick_params(axis="y", colors=C2); b2.grid(False)
    b2.spines["right"].set_visible(True); b2.spines["right"].set_color(C2)
    b.annotate(f"$I_\\mathrm{{th}}$ = {ith_fit:.1f} mA", xy=(ith_fit, 0.1), xytext=(2, 3.4), fontsize=6.5, color=C1,
               arrowprops=dict(arrowstyle="-", color=C1, lw=0.6))
    b.text(52, 5.2, f"slope {k:.2f} W/A", fontsize=6.5, color=C1, ha="left")
    b.text(36, 12.3, f"dV/dI = {kv:.1f} Ω", fontsize=6.5, color=C2, ha="left")
    tag(b, "b")
    # (c) L-I at four temperatures, threshold against temperature
    c = fig.add_axes([0.6, 0.08, 0.38, 0.45])
    temps = [25, 45, 65, 85]; cols = [C1, C3, C2, C4]; iths = []
    for T, col in zip(temps, cols):
        Pt, Vt, ith_t = laser_liv(I, T, rng)
        sel = (I > 1.3 * ith_t) & (I < min(80, 3.5 * ith_t))
        kt, ct = np.polyfit(I[sel], Pt[sel], 1); iths.append(-ct / kt)
        c.plot(I, Pt, color=col, lw=1.1); c.text(81, Pt[-1], f"{T} °C", fontsize=6.3, color=col, va="center", ha="left", clip_on=False)
    c.set_xlim(0, 80); c.set_ylim(0, 14)
    finish(c, xlabel="current (mA)", ylabel="power per facet (mW)")
    c.text(4, 13.3, "heat-sink temperature:", fontsize=6.3, color=INK, va="center") if False else None
    tag(c, "c")
    iths = np.array(iths); slope, icpt = np.polyfit(temps, np.log(iths), 1)
    print("thresholds (fitted):", np.round(iths, 2), f"-> T0 = {1/slope:.1f} K")
    ins = fig.add_axes([0.645, 0.335, 0.13, 0.15])
    ins.semilogy(temps, iths, "o", ms=3, color=INK)
    tt = np.linspace(20, 90, 20); ins.semilogy(tt, np.exp(icpt + slope * tt), color=MUTED, lw=0.8)
    ins.set_xticks([25, 85]); ins.set_yticks([20, 50]); ins.set_yticklabels(["20", "50"]); ins.minorticks_off()
    ins.tick_params(labelsize=5.5, length=2, pad=1); ins.grid(False)
    ins.set_xlabel("T (°C)", fontsize=5.5, labelpad=0); ins.set_ylabel("$I_\\mathrm{th}$ (mA)", fontsize=5.5, labelpad=0)
    ins.set_title(f"$T_0$ = {1/slope:.0f} K", fontsize=6, pad=2, color=INK)
    save(fig, "ch31_liv")


# ------------------------------------------------------------------ Figure 31.5
def fig_rf():
    fig, ax = geom_axes(figsize=(6.3, 3.6), xlim=(0, 10.6), ylim=(0, 6.2), equal=False)
    # (a) frequency domain
    panel(ax, "a", 0.0, 1.0)
    ax.text(0.3, 6.08, "frequency domain: electro-optic S$_{21}$ and the 3 dB bandwidth", fontsize=7, va="top", color=INK)
    ya = 4.35
    block(ax, 1.0, ya + 0.75, 1.3, 0.5, "CW laser", fc=INSTR, fs=6.4)
    block(ax, 4.0, ya, 1.6, 0.8, "modulator\n(device)", fc="#FBF3E6", fs=6.6)
    owire(ax, [(1.65, ya + 0.75), (2.7, ya + 0.75), (2.7, ya + 0.2), (3.2, ya + 0.2)])
    block(ax, 2.2, ya - 0.55, 1.2, 0.5, "bias tee", fc=INSTR, fs=6.3); label(ax, 1.55, ya - 0.2, "+ DC bias", fs=5.8, col=ELEC, ha="left")
    ewire(ax, [(2.8, ya - 0.55), (3.5, ya - 0.55), (3.5, ya - 0.4)])
    label(ax, 3.62, ya - 0.47, "GSG", fs=5.8, ha="left", col=ELEC)
    owire(ax, [(4.8, ya), (6.55, ya)])
    ax.add_patch(FancyBboxPatch((6.35, ya - 1.25), 3.95, 1.75, boxstyle="round,pad=0,rounding_size=0.08", fc="none", ec=MUTED, lw=0.8, ls=(0, (3, 2))))
    label(ax, 8.33, ya + 0.38, "lightwave component analyser", fs=6.2, col=MUTED)
    block(ax, 7.35, ya, 1.6, 0.6, "calibrated\nphotoreceiver", fc=INSTR, fs=6.3)
    block(ax, 9.3, ya - 0.55, 1.6, 0.9, "network analyser\nport 1 → port 2", fc=INSTR, fs=6.3)
    ewire(ax, [(8.15, ya), (9.3, ya), (9.3, ya - 0.1)])
    ewire(ax, [(8.5, ya - 0.55), (7.0, ya - 0.55), (7.0, ya - 0.95), (1.0, ya - 0.95), (1.0, ya - 0.55), (1.6, ya - 0.55)])
    label(ax, 4.0, ya - 0.83, "RF drive, swept 0 → tens of GHz", fs=6.0, col=ELEC, va="bottom")
    # (b) time domain
    panel(ax, "b", 0.0, 0.45)
    ax.text(0.3, 2.75, "time domain: eye diagram and bit-error ratio", fontsize=7, va="top", color=INK)
    yb = 1.45
    block(ax, 0.95, yb, 1.5, 0.75, "pattern\ngenerator", fc=INSTR, fs=6.4)
    block(ax, 2.55, yb, 1.1, 0.6, "driver", fc=INSTR, fs=6.4)
    ewire(ax, [(1.7, yb), (2.0, yb)])
    block(ax, 3.8, yb, 1.0, 0.6, "bias tee", fc=INSTR, fs=6.2)
    ewire(ax, [(3.1, yb), (3.3, yb)])
    block(ax, 5.1, yb, 1.2, 0.75, "modulator\n(device)", fc="#FBF3E6", fs=6.4)
    ewire(ax, [(4.3, yb), (4.5, yb)])
    block(ax, 5.1, yb + 0.95, 1.1, 0.42, "CW laser", fc=INSTR, fs=6.2)
    owire(ax, [(5.1, yb + 0.74), (5.1, yb + 0.375)])
    block(ax, 6.65, yb, 1.1, 0.6, "attenuator", fc=INSTR, fs=6.2)
    owire(ax, [(5.7, yb), (6.1, yb)])
    ax.add_patch(Circle((7.5, yb), 0.07, fc=OPT, ec="none", zorder=5))
    owire(ax, [(7.2, yb), (7.5, yb)], arrow_end=False)
    block(ax, 9.2, yb + 0.6, 2.0, 0.55, "sampling oscilloscope: eye", fc=INSTR, fs=6.2)
    block(ax, 8.5, yb - 0.6, 0.9, 0.5, "receiver", fc=INSTR, fs=6.2)
    block(ax, 9.75, yb - 0.6, 1.1, 0.5, "error\ndetector: BER", fc=INSTR, fs=6.0)
    owire(ax, [(7.5, yb), (7.8, yb + 0.6), (8.2, yb + 0.6)])
    owire(ax, [(7.5, yb), (7.8, yb - 0.6), (8.05, yb - 0.6)])
    ewire(ax, [(8.95, yb - 0.6), (9.2, yb - 0.6)])
    ax.plot([0.95, 0.95, 10.5, 10.5, 10.2], [yb - 0.375, 0.35, 0.35, yb + 0.6, yb + 0.6], color=ELEC, lw=0.8, ls=(0, (3, 2)), zorder=1)
    ax.plot([10.5, 10.3], [yb - 0.6, yb - 0.6], color=ELEC, lw=0.8, ls=(0, (3, 2)), zorder=1)
    label(ax, 5.2, 0.43, "clock and pattern reference", fs=6.0, col=ELEC, va="bottom")
    legend_paths(ax, loc="lower left", bbox=(0.0, 0.44), ncol=2)
    note(ax, "not to scale")
    save(fig, "ch31_rf")


if __name__ == "__main__":
    which = sys.argv[1:] or ["setup", "dft", "probe", "liv", "rf"]
    for k in which:
        globals()["fig_" + k]()
