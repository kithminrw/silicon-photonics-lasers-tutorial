"""Figures of Chapter 29 (fabrication).

    python -I -X utf8 figsrc/ch29_figs.py

ch29_soi       SOI wafer to scale (handle shortened) and the Smart Cut steps
ch29_litho     lithography and etch as a strip of cross-sections (schematic)
ch29_opc       blur of a projected image: drawn layout, printed shape, and optical proximity correction (simple model)
ch29_etch      full, rib and shallow etch to scale
ch29_stack     front-end and back-end stack of an active SOI process (to scale; back-end thicknesses illustrative)
ch29_sens      resonance shift over the width-thickness plane; sensitivity against width (femwell, Chapter 6 sweep), slab limit for thickness
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
OXE = "#AFC3DA"          # thin edge line so the pale oxide shows against the page


# ------------------------------------------------------------------ helpers
def zigzag_break(ax, x0, x1, y, amp=0.06, n=10, gap=0.12, fc="white", z=5):
    """A torn-edge break across a layer between x0 and x1: a white band with zigzag edges at height y."""
    xs = np.linspace(x0, x1, 2 * n + 1)
    lo = y - gap / 2 + amp * np.where(np.arange(xs.size) % 2, 1, -1)
    hi = lo + gap
    poly(ax, np.vstack([np.c_[xs, lo], np.c_[xs[::-1], hi[::-1]]]), fc, z=z)
    ax.plot(xs, lo, color=INK, lw=0.6, zorder=z + 1); ax.plot(xs, hi, color=INK, lw=0.6, zorder=z + 1)


def oxbox(ax, x, y, w, h, z=1, mat="ox"):
    return box(ax, x, y, w, h, mat, ec=OXE, lw=0.5, z=z)


# ------------------------------------------------------------------ Figure 29.1
def fig_soi():
    T_SI, T_BOX, T_HANDLE = 0.22, 2.0, 725.0
    print(f"SOI: film {T_SI*1000:.0f} nm, BOX {T_BOX:.1f} um, handle {T_HANDLE:.0f} um; film/wafer = 1/{(T_HANDLE + T_BOX + T_SI)/T_SI:.0f}")
    fig = plt.figure(figsize=(6.3, 3.0))
    # (a) stack to scale
    ax = fig.add_axes([0.0, 0.03, 0.30, 0.88]); frameless(ax, (-0.3, 4.6), (-4.7, 0.95))
    x0, w = 0.0, 1.5
    box(ax, x0, -4.5, w, 4.5 - T_BOX, "sub", z=1)
    oxbox(ax, x0, -T_BOX, w, T_BOX, z=2)
    box(ax, x0, 0, w, T_SI, "si", z=3)
    zigzag_break(ax, x0 - 0.05, x0 + w + 0.05, -3.35, amp=0.07, n=7, gap=0.16)
    lx = w + 0.25
    callout(ax, (w, T_SI / 2), (lx, 0.55), "Si film, 220 nm", fs=FS)
    dim(ax, (w + 0.12, -T_BOX), (w + 0.12, 0), "", col=INK)
    label(ax, lx, -1.0, "buried oxide\n(BOX), 2 µm", ha="left", fs=FS)
    label(ax, lx, -2.75, "Si handle", ha="left", fs=FS)
    label(ax, lx, -3.95, "≈ 0.7 mm thick,\nshortened", ha="left", fs=FS_SMALL, col=MUTED)
    scalebar(ax, 0.25, -4.62, 1.0, "1 µm", above=False)
    panel(ax, "a", 0.0, 1.07)
    ax.text(0.02, 1.0, "SOI wafer, to scale", transform=ax.transAxes, fontsize=FS_SMALL, color=MUTED, va="top", ha="left")
    ax.text(0.13, 1.07, "", transform=ax.transAxes)

    # (b) Smart Cut, six schematic steps in two rows
    W, D, TOX = 2.4, 0.75, 0.07          # wafer width, donor/handle thickness, oxide (schematic proportions)
    steps = ["oxidise the donor", "implant hydrogen", "flip and bond", "anneal: split", "polish and anneal", "reuse the donor"]
    cols = [0.335, 0.555, 0.775]; rows = [0.50, 0.03]; aw, ah = 0.215, 0.40
    axs = []
    for k, title in enumerate(steps):
        a = fig.add_axes([cols[k % 3], rows[k // 3], aw, ah]); frameless(a, (-0.15, W + 0.15), (-0.15, 2.45))
        a.text(0.0, 1.0, f"{k + 1}  {title}", transform=a.transAxes, fontsize=FS, color=INK, va="top", ha="left",
               fontweight="bold" if False else "normal")
        axs.append(a)

    def donor(a, y, flipped=False, cut=None, h=D, rough=False):
        """Donor wafer with oxide all round; the implanted plane is drawn dashed at `cut` below the oxidised face."""
        oxbox(a, 0 - TOX, y - TOX, W + 2 * TOX, h + 2 * TOX, z=1)
        box(a, 0, y, W, h, "si", z=2)
        if cut is not None:
            yc = y + cut if flipped else y + h - cut
            a.plot([0, W], [yc, yc], color=RED, lw=1.0, ls=(0, (3, 2)), zorder=4)
            return yc

    # 1 oxidise
    a = axs[0]; donor(a, 0.35)
    callout(a, (W * 0.8, 0.35 + D + TOX / 2), (W * 0.55, 1.65), "SiO$_2$", fs=FS_SMALL)
    label(a, W / 2, 0.35 + D / 2, "donor Si wafer", fs=FS_SMALL)
    # 2 implant
    a = axs[1]; yc = donor(a, 0.35, cut=0.2)
    for xa in np.linspace(0.25, W - 0.25, 6):
        arrow(a, (xa, 1.75), (xa, 1.27), col=RED, lw=0.8, ms=5)
    label(a, W / 2, 1.92, "H$^+$ ions", fs=FS_SMALL, col=RED)
    callout(a, (W * 0.2, yc), (W * 0.05, 0.12), "implanted layer", fs=FS_SMALL, col=RED)
    # 3 bond
    a = axs[2]
    box(a, 0, 0.1, W, D, "sub", z=1)
    label(a, W / 2, 0.1 + D / 2, "handle wafer", fs=FS_SMALL)
    yc = donor(a, 0.1 + D + TOX, flipped=True, cut=0.2)
    arrow(a, (W / 2, 2.25), (W / 2, 1.95), col=INK, lw=0.8, ms=5)
    label(a, W * 0.98, 1.4, "face down", fs=FS_SMALL, ha="right")
    # 4 split
    a = axs[3]
    box(a, 0, 0.1, W, D, "sub", z=1)
    oxbox(a, 0, 0.1 + D, W, TOX, z=2)
    box(a, 0, 0.1 + D + TOX, W, 0.2, "si", z=3)
    yl = 0.1 + D + TOX + 0.2 + 0.32
    oxbox(a, -TOX, yl, W + 2 * TOX, 0.55 + TOX, z=1); box(a, 0, yl, W, 0.55, "si", z=2)
    xs = np.linspace(0, W, 25); a.plot(xs, 0.1 + D + TOX + 0.2 + 0.015 * np.where(np.arange(25) % 2, 1, -1), color=INK, lw=0.5, zorder=4)
    a.plot(xs, yl + 0.015 * np.where(np.arange(25) % 2, 1, -1), color=INK, lw=0.5, zorder=4)
    arrow(a, (W * 0.85, yl + 0.1), (W * 0.85, yl + 0.42), col=INK, lw=0.7, ms=5)
    label(a, W / 2, yl + 0.27, "rest of donor", fs=FS_SMALL)
    # 5 polish
    a = axs[4]
    box(a, 0, 0.1, W, D, "sub", z=1); label(a, W / 2, 0.1 + D / 2, "handle", fs=FS_SMALL)
    oxbox(a, 0, 0.1 + D, W, TOX, z=2)
    box(a, 0, 0.1 + D + TOX, W, 0.17, "si", z=3)
    callout(a, (W * 0.3, 0.1 + D + TOX + 0.17), (W * 0.1, 1.55), "smooth Si film", fs=FS_SMALL)
    callout(a, (W * 0.75, 0.1 + D + TOX / 2), (W * 0.62, 1.25), "BOX", fs=FS_SMALL)
    # 6 reuse
    a = axs[5]; donor(a, 0.35, h=0.55)
    label(a, W / 2, 0.35 + 0.275, "donor, a little thinner", fs=FS_SMALL)
    a.annotate("", xy=(0.15, 1.75), xytext=(W - 0.15, 1.15), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8,
               connectionstyle="arc3,rad=0.35", mutation_scale=7))
    label(a, W / 2, 1.95, "back to step 1", fs=FS_SMALL)
    for k in (0, 1, 3, 4):
        fig.text(cols[k % 3 + 1] - 0.012, rows[k // 3] + 0.17, "›", fontsize=13, color=MUTED, ha="center", va="center")
    fig.text(cols[0] - 0.005, 0.93, "b", fontweight="bold", fontsize=9.5, color=INK, ha="left", va="center")
    fig.text(0.98, 0.012, "b: not to scale", fontsize=6, color=MUTED, style="italic", ha="right", va="bottom")
    save(fig, "ch29_soi")


# ------------------------------------------------------------------ Figure 29.2
def fig_litho():
    fig = plt.figure(figsize=(6.3, 2.75))
    W = 2.6; TSI, TBOX, TRES = 0.22, 0.45, 0.42; XW, WW = 1.3, 0.5   # schematic proportions
    steps = ["spin on resist", "expose (mask or e-beam)", "develop", "plasma etch", "strip the resist", "clad and planarise"]
    cols = [0.0, 0.34, 0.68]; rows = [0.5, 0.0]; aw, ah = 0.31, 0.47
    for k, title in enumerate(steps):
        a = fig.add_axes([cols[k % 3], rows[k // 3], aw, ah]); frameless(a, (-0.1, W + 0.1), (-TBOX - 0.05, 1.6))
        a.text(0.0, 1.0, f"{k + 1}  {title}", transform=a.transAxes, fontsize=FS, color=INK, va="top", ha="left")
        oxbox(a, 0, -TBOX, W, TBOX, z=1)
        if k <= 2:
            box(a, 0, 0, W, TSI, "si", z=2)
        else:
            box(a, XW - WW / 2, 0, WW, TSI, "si", z=2)
        if k == 0:
            box(a, 0, TSI, W, TRES, "resist", z=3)
            callout(a, (W * 0.85, TSI + TRES / 2), (W * 0.62, 1.05), "photoresist", fs=FS_SMALL)
            callout(a, (W * 0.15, TSI / 2), (W * 0.02, 0.9), "Si film", fs=FS_SMALL)
            label(a, W * 0.04, -TBOX / 2, "buried oxide", fs=FS_SMALL, ha="left")
        if k == 1:
            box(a, 0, TSI, W, TRES, "resist", z=3)
            box(a, 0, TSI, XW - WW / 2, TRES, "#C07FAA", z=3, alpha=0.9)     # exposed resist (positive tone)
            box(a, XW + WW / 2, TSI, W - XW - WW / 2, TRES, "#C07FAA", z=3, alpha=0.9)
            box(a, 0, 1.18, W, 0.06, "glass", ec=MUTED, lw=0.4, z=3)
            box(a, XW - WW / 2, 1.12, WW, 0.06, INK, z=4)                   # chrome on the mask
            for xa in np.r_[np.linspace(0.2, XW - WW / 2 - 0.1, 3), np.linspace(XW + WW / 2 + 0.1, W - 0.2, 3)]:
                arrow(a, (xa, 1.10), (xa, TSI + TRES + 0.04), col=VIOLET, lw=0.8, ms=5)
            label(a, W * 0.98, 1.4, "mask", fs=FS_SMALL, ha="right")
        if k == 2:
            box(a, XW - WW / 2, TSI, WW, TRES, "resist", z=3)
            label(a, W / 2, 1.05, "exposed resist dissolves\n(positive resist)", fs=FS_SMALL)
        if k == 3:
            box(a, XW - WW / 2, TSI, WW, TRES, "resist", z=3)
            for xa in (0.35, 0.7, 1.9, 2.25):
                arrow(a, (xa, 1.15), (xa, 0.06), col=AMBER, lw=0.8, ms=5)
            label(a, W / 2, 1.3, "ions", fs=FS_SMALL, col=AMBER)
        if k == 4:
            callout(a, (XW + WW / 2, TSI / 2), (W * 0.7, 0.75), "Si strip", fs=FS_SMALL)
        if k == 5:
            box(a, 0, 0, W, 0.95, "oxtop", ec=OXE, lw=0.5, z=1)
            box(a, XW - WW / 2, 0, WW, TSI, "si", z=2)
            callout(a, (W * 0.85, 0.7), (W * 0.62, 1.25), "SiO$_2$ cladding", fs=FS_SMALL)
    for k in (0, 1, 3, 4):
        fig.text(cols[k % 3 + 1] - 0.015, rows[k // 3] + 0.2, "›", fontsize=13, color=MUTED, ha="center", va="center")
    fig.text(0.995, 0.0, "not to scale", fontsize=6, color=MUTED, style="italic", ha="right", va="bottom")
    save(fig, "ch29_litho")


# ------------------------------------------------------------------ Figure 29.3 (OPC)
def fig_opc():
    """Blur-and-threshold model of projection lithography: the mask is convolved with a Gaussian and printed where the
    image exceeds half its open-field value. The blur is set so that the narrowest isolated line that still prints is
    120 nm, inside the chapter's 100-150 nm for dry 248/193 nm tools. A 1 x 2 MMI with two outputs is drawn, printed,
    then corrected (serifs on convex corners, notches in concave corners, wider gap, a hammerhead on the line end)."""
    from matplotlib.path import Path
    WMIN = 0.120
    # isolated line of width w: peak = erf(w / (2 sqrt2 sigma)); erf(x) = 0.5 at x = 0.4769
    sig = WMIN / (2 * np.sqrt(2) * 0.4769)
    h = 0.005
    x = np.arange(-0.8, 4.0, h); y = np.arange(-0.6, 2.2, h)
    XX, YY = np.meshgrid(x, y)
    P = np.c_[XX.ravel(), YY.ravel()]

    def raster(polys):
        m = np.zeros(XX.size, bool)
        for pts in polys:
            m |= Path(np.asarray(pts)).contains_points(P)
        return m.reshape(XX.shape).astype(float)

    def blur(m):
        kx = np.fft.fftfreq(x.size, h); ky = np.fft.fftfreq(y.size, h)
        KX, KY = np.meshgrid(kx, ky)
        G = np.exp(-2 * (np.pi * sig) ** 2 * (KX ** 2 + KY ** 2))
        return np.real(np.fft.ifft2(np.fft.fft2(m) * G))

    rect = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    WG, GAP, TIP = 0.5, 0.15, 0.15
    yc = 0.8
    yl = yc - GAP / 2 - WG / 2                                        # centre of the lower output
    body = rect(0.5, yc - 0.6, 2.1, yc + 0.6)
    inp = rect(-0.8, yc - WG / 2, 0.5, yc + WG / 2)
    out1 = rect(2.1, yc + GAP / 2, 4.0, yc + GAP / 2 + WG)

    def taper(b_in, b_tip, x_end):                                     # lower output: straight, then tapers to a tip
        return [(2.1, yl - WG / 2), (2.6, yl - WG / 2), (x_end, yl - TIP / 2 - b_tip), (x_end, yl + TIP / 2 + b_tip),
                (2.6, yl + WG / 2 - b_in), (2.1, yl + WG / 2 - b_in)]
    out2 = taper(0.0, 0.0, 3.2)
    drawn = [body, inp, out1, out2]
    s = 0.07                                                          # serif half-size
    serifs = [rect(cx - s, cy - s, cx + s, cy + s) for cx, cy in ((0.5, yc - 0.6), (0.5, yc + 0.6), (2.1, yc - 0.6), (2.1, yc + 0.6))]
    GB = 0.006                                                        # gap bias: each inner edge moved back 6 nm
    out1c = rect(2.1, yc + GAP / 2 + GB, 4.0, yc + GAP / 2 + WG)
    out2c = taper(GB, 0.02, 3.2)
    hammer = [rect(3.14, yl - TIP / 2 - 0.05, 3.235, yl + TIP / 2 + 0.05)]
    opc = [body, inp, out1c, out2c] + serifs + hammer
    notch = [rect(cx - 0.05, cy - 0.05, cx + 0.05, cy + 0.05) for cx, cy in ((0.5, yc - WG / 2), (0.5, yc + WG / 2))]
    I0 = blur(raster(drawn))
    I1 = blur(np.clip(raster(opc) - raster(notch), 0, 1))
    col = np.argmin(abs(x - 2.35))
    def gap_w(I):
        g = (I[:, col] < 0.5) & (abs(y - yc) < 0.2)
        return g.sum() * h
    end = np.argmin(abs(y - yl))
    def end_x(I):
        return x[np.where(I[end] > 0.5)[0].max()]
    print(f"OPC model: sigma {sigma_nm(sig)} nm; printed gap {gap_w(I0)*1000:.0f} nm (drawn {GAP*1000:.0f}) -> {gap_w(I1)*1000:.0f} nm with OPC; "
          f"tip end at {end_x(I0):.3f} um (drawn 3.200) -> {end_x(I1):.3f} um with OPC")
    fig = plt.figure(figsize=(6.3, 2.05))
    for k, (I, mask, ttl) in enumerate(((I0, drawn, "mask = drawn layout"), (I1, opc, "mask with proximity correction"))):
        a = fig.add_axes([0.005 + 0.5 * k, 0.02, 0.49, 0.84]); frameless(a, (-0.2, 3.4), (-0.25, 1.85))
        a.contourf(XX, YY, I, levels=[0.5, 10], colors=[MAT["si"]], zorder=1)
        for pts in mask:
            a.add_patch(Polygon(np.asarray(pts), closed=True, fc="none", ec=INK, lw=0.6, ls=(0, (2, 1.2)), zorder=3))
        if k == 1:
            for pts in notch:
                a.add_patch(Polygon(np.asarray(pts), closed=True, fc="none", ec=RED, lw=0.6, zorder=3))
        a.text(0.04, 1.03, ttl, transform=a.transAxes, fontsize=7.5, fontweight="bold", color=INK, va="bottom", ha="left")
    ax0, ax1 = fig.axes[0], fig.axes[1]
    callout(ax0, (0.55, yc + 0.55), (0.7, 1.72), "corners round", fs=FS_SMALL)
    callout(ax0, (2.35, yc - 0.01), (1.75, -0.17), f"gap {GAP*1000:.0f} → {gap_w(I0)*1000:.0f} nm", fs=FS_SMALL)
    callout(ax0, (end_x(I0), yl), (2.75, -0.17), f"tip pulls back {(3.2 - end_x(I0))*1000:.0f} nm", fs=FS_SMALL)
    callout(ax1, (0.5 + s, yc + 0.6 + s), (0.7, 1.72), "serifs", fs=FS_SMALL)
    callout(ax1, (0.55, yc + WG / 2), (0.0, 1.72), "notches", fs=FS_SMALL, col=RED)
    callout(ax1, (2.35, yc + GAP / 2 + GB), (1.75, -0.17), "biased gap", fs=FS_SMALL)
    callout(ax1, (3.2, yl - TIP / 2 - 0.05), (2.75, -0.17), "hammerhead", fs=FS_SMALL)
    scalebar(ax1, 2.85, 1.62, 0.5, "500 nm", above=True)
    fig.text(0.01, 0.995, "a", fontweight="bold", fontsize=9.5, color=INK, va="top")
    fig.text(0.515, 0.995, "b", fontweight="bold", fontsize=9.5, color=INK, va="top")
    save(fig, "ch29_opc")


def sigma_nm(s):
    return f"{s*1000:.0f}"


# ------------------------------------------------------------------ Figure 29.4 (etch depths)
def fig_etch():
    T, W, ANG = 0.22, 0.50, 4.0                   # film, ridge width, sidewall angle off vertical (degrees, drawn)
    cases = [("full etch", 0.22, "strip: routing, bends,\nrings, couplers"),
             ("130 nm etch", 0.13, "rib: modulators,\nlow-loss routing"),
             ("70 nm etch", 0.07, "grating-coupler teeth\n(cut along the grating)")]
    fig = plt.figure(figsize=(6.3, 1.95))
    for k, (name, etch, use) in enumerate(cases):
        a = fig.add_axes([k / 3 + 0.005, 0.0, 1 / 3 - 0.01, 0.98]); frameless(a, (-1.3, 1.3), (-0.95, 0.62))
        oxbox(a, -1.3, -0.5, 2.6, 0.5, z=1)
        box(a, -1.3, 0, 2.6, 0.48, "oxtop", z=1)
        slab = T - etch
        sl = np.tan(np.radians(ANG)) * etch
        if k < 2:
            if slab > 0:
                box(a, -1.3, 0, 2.6, slab, "si", z=2)
            trapezoid(a, 0, slab, W + 2 * sl, W, etch, "si", z=2)
            dim(a, (-W / 2, T + 0.09), (W / 2, T + 0.09), "500 nm")
            if slab > 0:
                tick_dim(a, (0.95, 0), (0.95, slab), "", lw=0.6)
                label(a, 0.95, slab + 0.07, f"{slab*1000:.0f} nm slab", fs=FS_SMALL, ha="center", va="bottom")
            tick_dim(a, (-0.55, 0), (-0.55, T), "", lw=0.6)
            label(a, -0.62, T / 2, "220 nm", fs=FS_SMALL, ha="right")
        else:
            LAMG, FF = 0.63, 0.5                   # grating period (Chapter 15, full simulation) and fill factor
            box(a, -1.3, 0, 2.6, slab, "si", z=2)
            x = -1.3 + 0.09
            while x + LAMG * FF < 1.3:
                trapezoid(a, x + LAMG * FF / 2, slab, LAMG * FF + 2 * sl, LAMG * FF, etch, "si", z=2)
                x += LAMG
            dim(a, (-1.21, T + 0.07), (-1.21 + LAMG, T + 0.07), "Λ ≈ 630 nm", bg=None, text_off=(0.25, 0.1), ha="left")
            tick_dim(a, (1.18, slab), (1.18, T), "", lw=0.6)
            label(a, 1.12, T + 0.08, "70 nm", fs=FS_SMALL, ha="right", va="bottom")
        a.text(0.5, 1.0, name, transform=a.transAxes, ha="center", va="top", fontsize=FS + 0.5, color=INK, fontweight="bold")
        label(a, 0, -0.73, use, fs=FS_SMALL, col=MUTED, va="center")
        panel(a, "abc"[k], 0.0, 1.0)
        if k == 0:
            label(a, -1.25, -0.25, "BOX", fs=FS_SMALL, ha="left")
            label(a, -1.25, 0.38, "oxide cladding", fs=FS_SMALL, ha="left")
        if k == 2:
            scalebar(a, 0.45, -0.38, 0.5, "500 nm", above=True)
    print("etch depths: full 220 nm, rib 130 nm (90 nm slab), shallow 70 nm (150 nm slab); GC period 630 nm drawn")
    save(fig, "ch29_etch")


# ------------------------------------------------------------------ Figure 29.4
def fig_stack():
    """Cross-section of an active SOI process, true scale in both directions. Front end from the earlier chapters
    (220 nm film, 90 nm slab, 2 um BOX, contacts 1.2 um from the rib, Ge 4 um wide and 0.5 um thick, TiN heater
    2 um wide and 0.12 um thick at 1.9 um); back-end metal thicknesses illustrative."""
    T, SLAB, BOX = 0.22, 0.09, 2.0
    Y_CL = 2.3                        # top of the first cladding (heater level, Chapter 18 model)
    M1 = (2.6, 3.2); M2 = (4.0, 5.2); PAS = 5.9
    fig, ax = geom_axes(figsize=(6.3, 3.05), xlim=(-0.6, 24.6), ylim=(-3.0, 7.0))
    XL, XR = -0.4, 23.6
    box(ax, XL, -2.95, XR - XL, 0.95, "sub", z=1)
    zigzag_break(ax, XL - 0.1, XR + 0.1, -2.78, amp=0.06, n=40, gap=0.12)
    oxbox(ax, XL, -BOX, XR - XL, BOX, z=1)
    box(ax, XL, 0, XR - XL, PAS, "oxtop", ec=OXE, lw=0.4, z=1)          # all the deposited dielectrics
    # --- PN-junction phase shifter (rib), centred at x = 2.5
    xc = 2.5
    box(ax, 0.3, 0, 1.0, SLAB, "pp", z=3); box(ax, 1.3, 0, xc - 1.3, SLAB, "pdop", z=3)
    box(ax, xc, 0, 3.7 - xc, SLAB, "ndop", z=3); box(ax, 3.7, 0, 1.0, SLAB, "nn", z=3)
    box(ax, xc - 0.25, SLAB, 0.25, T - SLAB, "pdop", z=3); box(ax, xc, SLAB, 0.25, T - SLAB, "ndop", z=3)
    # --- Ge vertical PIN photodiode on a p-doped Si pad, centred at x = 9.75
    xg = 9.75
    box(ax, 6.2, 0, 7.1, T, "pdop", z=3); box(ax, 6.2, 0, 1.0, T, "pp", z=3); box(ax, 12.3, 0, 1.0, T, "pp", z=3)
    trapezoid(ax, xg, T, 4.0, 3.7, 0.5, "ge", z=3)
    box(ax, xg - 1.85, T + 0.42, 3.7, 0.08, "nn", z=4)
    # --- strip waveguide under a TiN heater, x = 16
    xh = 16.0
    box(ax, xh - 0.25, 0, 0.5, T, "si", z=3)
    box(ax, xh - 1.0, 1.9, 2.0, 0.12, "tin", z=4)
    # --- grating coupler with an oxide window above it, x = 19.6 ... 23.4
    for x in np.arange(19.7, 23.3, 0.63):
        box(ax, x, 0.15, 0.315, 0.07, "si", z=3)
    box(ax, 19.4, 0, 4.0, 0.15, "si", z=3)
    # --- contacts (W plugs) from Si/Ge to metal 1
    def plug(x, y0, y1, w=0.22):
        box(ax, x - w / 2, y0, w, y1 - y0, "al", ec=MUTED, lw=0.3, z=5)
    for x in (0.8, 4.2): plug(x, SLAB, M1[0])
    for x in (6.7, 12.8): plug(x, T, M1[0])
    plug(xg, T + 0.5, M1[0])
    # --- metal 1, vias, metal 2, passivation and pad opening
    for x0, x1 in ((0.3, 1.3), (3.7, 4.7), (6.2, 7.3), (12.2, 13.3), (9.0, 10.5)):
        box(ax, x0, M1[0], x1 - x0, M1[1] - M1[0], "metal", z=5)
    for x in (0.8, 9.75): plug(x, M1[1], M2[0], w=0.3)
    box(ax, -0.2, M2[0], 5.6, M2[1] - M2[0], "metal", z=5)
    box(ax, 8.2, M2[0], 3.1, M2[1] - M2[0], "metal", z=5)
    box(ax, XL, PAS - 0.0, 0, 0, "none")
    # passivation opening over the pad, and the oxide window over the grating coupler
    box(ax, 0.5, M2[1], 3.8, PAS - M2[1] + 0.01, "white", z=6)
    box(ax, 19.0, 1.1, 4.6, PAS - 1.1 + 0.01, "white", z=6)
    ax.plot([0.5, 0.5, 4.3, 4.3], [PAS, M2[1], M2[1], PAS], color=OXE, lw=0.5, zorder=6)
    ax.plot([19.0, 19.0, 23.6], [PAS, 1.1, 1.1], color=OXE, lw=0.5, zorder=6)
    # --- labels
    fs = FS_SMALL
    label(ax, xc, -0.35, "PN phase shifter", fs=fs, va="top", bold=True)
    label(ax, xg, -0.35, "Ge photodiode", fs=fs, va="top", bold=True)
    label(ax, xh, -0.35, "heated waveguide", fs=fs, va="top", bold=True)
    label(ax, 21.5, -0.35, "grating coupler", fs=fs, va="top", bold=True)
    callout(ax, (0.8, SLAB / 2), (-0.3, 1.25), "p$^{++}$", fs=fs, ha="center")
    callout(ax, (1.9, SLAB / 2), (1.6, 1.0), "p", fs=fs, ha="center")
    callout(ax, (3.1, SLAB / 2), (3.4, 1.0), "n", fs=fs, ha="center")
    callout(ax, (4.2, SLAB / 2), (5.25, 1.25), "n$^{++}$", fs=fs, ha="center")
    callout(ax, (xg + 1.2, T + 0.3), (xg + 1.7, 1.45), "Ge, 0.5 µm", fs=fs, ha="left")
    callout(ax, (7.6, T / 2), (7.6, 1.25), "p-Si", fs=fs, ha="center")
    callout(ax, (xh + 0.9, 1.96), (xh + 0.4, 2.75), "TiN heater (contacted\nat its ends, out of plane)", fs=fs, ha="left")
    callout(ax, (6.7, 1.6), (5.65, 2.25), "W contact", fs=fs, ha="right")
    callout(ax, (13.3, 2.9), (14.0, 3.6), "metal 1", fs=fs, ha="left")
    callout(ax, (9.75, 3.6), (7.4, 3.6), "via", fs=fs, ha="right")
    label(ax, 9.75, M2[1] + 0.25, "metal 2", fs=fs, va="bottom")
    label(ax, 2.4, PAS + 0.15, "pad opening", fs=fs, va="bottom")
    label(ax, 21.3, PAS + 0.15, "oxide window", fs=fs, va="bottom")
    label(ax, 16.0, PAS - 0.45, "deposited oxide", fs=fs, col=MUTED)
    label(ax, 11.5, -1.0, "buried oxide, 2 µm", fs=fs, col=INK)
    label(ax, 11.5, -2.33, "Si handle (shortened)", fs=fs, col=INK)
    # front end / back end brackets
    for (y0, y1, txt) in ((0, 0.72, "front end"), (0.72, PAS, "back end")):
        ax.plot([24.0, 24.15, 24.15, 24.0], [y0 + 0.04, y0 + 0.04, y1 - 0.04, y1 - 0.04], color=MUTED, lw=0.7)
        ax.text(24.3, (y0 + y1) / 2, txt, rotation=90, ha="left", va="center", fontsize=fs, color=MUTED)
    scalebar(ax, 17.6, 6.45, 2.0, "2 µm", above=True)
    note(ax, "true scale in both directions; back-end thicknesses illustrative", loc="upper left")
    print("stack: film 220 nm, slab 90 nm, BOX 2 um, Ge 4 x 0.5 um, TiN 2 x 0.12 um at 1.9 um; M1 %.1f-%.1f, M2 %.1f-%.1f, top %.1f um (illustrative)" % (M1 + M2 + (PAS,)))
    save(fig, "ch29_stack")


# ------------------------------------------------------------------ Figure 29.6 (sensitivity)
def n_si(l):        # silicon, wavelength in um (same Sellmeier as femwell_modes.py)
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / l ** 2 + 0.00810461 * l1 ** 2 / (l ** 2 - l1 ** 2))


def n_sio2(l):      # silica (Malitson), as in femwell_modes.py
    return np.sqrt(1 + 0.6961663 * l ** 2 / (l ** 2 - 0.0684043 ** 2) + 0.4079426 * l ** 2 / (l ** 2 - 0.1162414 ** 2)
                   + 0.8974794 * l ** 2 / (l ** 2 - 9.896161 ** 2))


def slab_te0(t_um, lam_um):
    """TE0 effective index of a symmetric Si slab in SiO2 (bisection on the even-mode equation, first branch)."""
    n1, n2, k0 = n_si(lam_um), n_sio2(lam_um), 2 * np.pi / lam_um
    f = lambda n: np.tan(k0 * np.sqrt(n1 ** 2 - n ** 2) * t_um / 2) - np.sqrt(n ** 2 - n2 ** 2) / np.sqrt(n1 ** 2 - n ** 2)
    lo = max(n2, np.sqrt(max(n1 ** 2 - (np.pi / (k0 * t_um)) ** 2, n2 ** 2))) + 1e-9
    hi = n1 - 1e-9
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) > 0: lo = m          # f falls from +inf to -inf as n rises
        else: hi = m
    return (lo + hi) / 2


def fig_sens():
    LAM, NG = 1550.0, 4.18
    DW, DT = 0.6, 1.4                        # nm/nm, the chapter's rounded values (Chapter 6 femwell numbers)
    print(f"check: 1550 x 1.6e-3 / 4.18 = {LAM*1.6e-3/NG:.3f} nm/nm (width); 1550 x 3.7e-3 / 4.18 = {LAM*3.7e-3/NG:.3f} (thickness)")
    print(f"worked example: 1.4 x 6 + 0.6 x 6 = {DT*6 + DW*6:.1f} nm; random 1.5 nm width -> +-{DW*1.5:.1f} nm; channel spacing 1549.32 - 1546.12 = {1549.32-1546.12:.2f} nm")
    s6 = json.load(open(os.path.join(HERE, "ch06_sweep.json")))          # femwell: Chapter 6 width sweep at 220 nm
    w6 = np.array(s6["widths"]) * 1000; n6 = np.array([r[0][0] for r in s6["neff1550"]]); g6 = np.array(s6["ng_te1550"])
    sel = w6 >= 400
    dn6 = np.gradient(n6, w6)
    sw = LAM * dn6 / g6                                                  # nm of shift per nm of width
    # wide-waveguide limit of the thickness sensitivity: the 220 nm slab (NumPy model)
    n0 = slab_te0(0.22, 1.55); dndt = (slab_te0(0.225, 1.55) - slab_te0(0.215, 1.55)) / 10.0
    ngs = n0 - 1.55 * (slab_te0(0.22, 1.56) - slab_te0(0.22, 1.54)) / 0.02
    st_slab = LAM * dndt / ngs
    print(f"slab 220 nm: n_eff {n0:.3f}, n_g {ngs:.2f}, dn/dt {dndt:.2e} per nm -> {st_slab:.2f} nm per nm of thickness")
    for i in np.where(sel)[0]:
        print(f"  W {w6[i]:5.0f} nm: n_g {g6[i]:.3f}, dn/dW {dn6[i]:.2e} -> {sw[i]:.3f} nm per nm of width")

    fig = plt.figure(figsize=(6.3, 2.75))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.75])
    g = np.linspace(-8, 8, 321); X, Y = np.meshgrid(g, g)
    Z = DW * X + DT * Y
    m = ax.pcolormesh(X, Y, Z, cmap=SIGNED_CMAP, vmin=-16, vmax=16, shading="auto", rasterized=True)   # red = red shift
    cs = ax.contour(X, Y, Z, levels=[-9.6, -6.4, -3.2, 3.2, 6.4, 9.6], colors=INK, linewidths=0.5, linestyles="solid")
    ax.contour(X, Y, Z, levels=[0], colors=INK, linewidths=0.9)
    ax.clabel(cs, fmt=lambda v: f"{v:+.1f}", fontsize=6.2, inline_spacing=2)
    ax.plot([6], [6], "o", ms=5, mfc="white", mec=INK, mew=1.0)
    ax.annotate(f"+{DT*6 + DW*6:.0f} nm", xy=(6, 6), xytext=(1.6, 7.0), fontsize=7, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    ax.add_patch(Ellipse((0, 0), 2 * 1.5, 0.35, fc="none", ec=INK, lw=0.8, ls=(0, (2, 1.5))))
    ax.annotate("random width, σ = 1.5 nm", xy=(-1.5, 0.1), xytext=(-7.6, 1.6), fontsize=6.3, color=INK,
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8),
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    ax.set_xlim(-8, 8); ax.set_ylim(-8, 8); ax.set_aspect("equal"); ax.grid(False)
    ax.set_xticks([-8, -4, 0, 4, 8]); ax.set_yticks([-8, -4, 0, 4, 8])
    finish(ax, xlabel="width error ΔW (nm)", ylabel="thickness error Δt (nm)")
    cb = fig.colorbar(m, ax=ax, fraction=0.05, pad=0.03); cb.set_label("resonance shift (nm)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    tag(ax, "a")
    ax2 = fig.add_axes([0.64, 0.15, 0.34, 0.75])
    ax2.plot(w6[sel], sw[sel], color=C2, marker="s", ms=3.5, label="per nm of width")
    ax2.plot([500], [LAM * 3.7e-3 / NG], "o", ms=5, color=C1, label="per nm of thickness")
    ax2.axhline(st_slab, color=C1, lw=0.9, ls="--")
    ax2.text(1000, st_slab + 0.05, "thickness: wide-guide (slab) limit", fontsize=6.4, color=C1, ha="right", va="bottom")
    ax2.set_xlim(380, 1020); ax2.set_ylim(0, 1.75)
    finish(ax2, xlabel="waveguide width (nm)", ylabel="resonance shift (nm per nm)")
    ax2.legend(loc="center right", fontsize=6.6, bbox_to_anchor=(1.0, 0.55))
    tag(ax2, "b")
    save(fig, "ch29_sens")



if __name__ == "__main__":
    which = sys.argv[1:] or ["soi", "litho", "opc", "etch", "stack", "sens"]
    for k in which:
        globals()["fig_" + k]()
