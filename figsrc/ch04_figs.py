"""Figures for Chapter 4 (materials and platforms).

Run from the repository root:   python -I -X utf8 figsrc/ch04_figs.py
Writes assets/figs/ch04_modesize.svg and ch04_combined.svg and prints the numbers they show.
Mode sizes come from the exact TE0 solution of a symmetric slab (the vertical direction of each platform's waveguide),
with the chapter's indices at 1550 nm.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402

LAM = 1.55
# (name, core index, cladding index, typical core thickness in µm (Figure 4.2), core material, colour)
PAIRS = [("Si / SiO$_2$", 3.476, 1.444, 0.22, "si", C1),
         ("LiNbO$_3$ ($n_e$) / SiO$_2$", 2.138, 1.444, 0.40, "ln", C4),
         ("Si$_3$N$_4$ / SiO$_2$", 1.996, 1.444, 0.40, "sin", C2),
         ("InGaAsP / InP", 3.36, 3.17, 0.50, "q", C6)]


def slab_te0(n1, n2, t, lam=LAM):
    """n_eff, kappa, gamma of the TE0 mode of a symmetric slab of thickness t (bisection on kappa tan(kappa t/2) = gamma)."""
    k0 = 2 * np.pi / lam
    f = lambda ne: np.sqrt(n1 ** 2 - ne ** 2) * np.tan(k0 * np.sqrt(n1 ** 2 - ne ** 2) * t / 2) - np.sqrt(ne ** 2 - n2 ** 2)
    lo = max(n2 + 1e-12, np.sqrt(max(n1 ** 2 - (np.pi / (k0 * t)) ** 2, n2 ** 2)) + 1e-12)   # tan argument below pi/2
    hi = n1 - 1e-12
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) > 0: lo = m
        else: hi = m
    ne = (lo + hi) / 2
    return ne, k0 * np.sqrt(n1 ** 2 - ne ** 2), k0 * np.sqrt(ne ** 2 - n2 ** 2)


def profile(n1, n2, t, x):
    ne, ka, ga = slab_te0(n1, n2, t)
    E = np.where(np.abs(x) <= t / 2, np.cos(ka * x), np.cos(ka * t / 2) * np.exp(-ga * (np.abs(x) - t / 2)))
    return E


def width_e2(n1, n2, t):
    """Full width of the intensity at 1/e² of its peak."""
    ne, ka, ga = slab_te0(n1, n2, t)
    if np.cos(ka * t / 2) ** 2 > np.exp(-2):           # 1/e² point outside the core
        return t + 2 * (np.log(np.cos(ka * t / 2) ** 2) + 2) / (2 * ga)
    return 2 * np.arccos(np.exp(-1)) / ka


# ------------------------------------------------------------------ Figure: index contrast sets the mode size
def fig_modesize():
    fig = plt.figure(figsize=(6.3, 3.3))
    a = fig.add_axes([0.085, 0.14, 0.40, 0.78])
    t = np.logspace(np.log10(0.04), np.log10(3.0), 400)
    print("slab TE0 at 1550 nm (1/e² intensity width):")
    for name, n1, n2, t0, mat, col in PAIRS:
        NA = np.sqrt(n1 ** 2 - n2 ** 2)
        tc = LAM / (2 * NA)                                # TE1 cut-off of the symmetric slab
        W = np.array([width_e2(n1, n2, tt) for tt in t])
        sm = t <= tc
        a.loglog(t[sm], W[sm], color=col, label=name)
        a.loglog(t[~sm], W[~sm], color=col, ls=":", lw=1.2)
        im = np.argmin(W)
        w0 = width_e2(n1, n2, t0)
        ne0, ka0, ga0 = slab_te0(n1, n2, t0)
        a.plot([t0], [w0], "o", color=col, ms=5, zorder=5, mec="white", mew=0.6)
        print(f"  {name.replace('$', ''):28s} Δn {n1-n2:.3f}, NA {NA:.3f}: single-mode below {1e3*tc:.0f} nm; "
              f"smallest width {W[im]:.2f} µm at t = {1e3*t[im]:.0f} nm; at the typical {1e3*t0:.0f} nm: n_eff {ne0:.3f}, "
              f"width {w0:.2f} µm, decay length 1/γ {1e3/ga0:.0f} nm")
    a.set_xlim(0.04, 3.0); a.set_ylim(0.2, 20)
    a.set_xticks([0.05, 0.1, 0.2, 0.5, 1, 2]); a.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1", "2"])
    a.set_yticks([0.2, 0.5, 1, 2, 5, 10, 20]); a.set_yticklabels(["0.2", "0.5", "1", "2", "5", "10", "20"])
    a.minorticks_off()
    finish(a, "Core thickness (µm)", "Mode width, 1/e² intensity (µm)")
    a.legend(loc="upper right", fontsize=6.5, handlelength=1.4, borderaxespad=0.2)
    a.text(2.9, 0.215, "dots: typical thickness (Figure 4.2)\ndotted: multimode", fontsize=6.3, color=MUTED, va="bottom", ha="right")
    tag(a, "a")
    # (b) the profiles at the typical thickness, to one scale
    x = np.linspace(-2.6, 2.6, 521)
    for k, (name, n1, n2, t0, mat, col) in enumerate(PAIRS):
        b = fig.add_axes([0.60, 0.14 + 0.195 * (3 - k), 0.38, 0.17])
        b.axvspan(-t0 / 2, t0 / 2, color=MAT[mat], alpha=0.9, lw=0)
        I = profile(n1, n2, t0, x) ** 2
        b.fill_between(x, 0, I, color=col, alpha=0.18, lw=0)
        b.plot(x, I, color=col, lw=1.3)
        w0 = width_e2(n1, n2, t0)
        b.annotate("", (w0 / 2, np.exp(-2)), (-w0 / 2, np.exp(-2)),
                   arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=5, shrinkA=0, shrinkB=0))
        b.text(w0 / 2 + 0.08, np.exp(-2) + 0.05, f"{w0:.2f} µm", fontsize=6.4, color=INK, va="bottom")
        b.text(-2.55, 0.92, name.split(" / ")[0] + f", {1e3*t0:.0f} nm", fontsize=6.6, color=INK, va="top")
        b.set_xlim(-2.6, 2.6); b.set_ylim(0, 1.08); b.set_yticks([]); b.grid(False)
        b.spines["left"].set_visible(False)
        if k < 3: b.set_xticklabels([])
        else: b.set_xlabel("Vertical position (µm)")
        if k == 0: tag(b, "b")
    save(fig, "ch04_modesize")


# ------------------------------------------------------------------ Figure: one silicon wafer, four materials
def fig_combined():
    T_SI, T_BOX = 0.22, 2.0
    Y_SIN, T_SIN, W_SIN = 0.42, 0.40, 1.2           # SiN 200 nm above the silicon (representative)
    Y_TOP = 0.92                                     # planarised oxide, 100 nm over the SiN
    T_LN, T_AU = 0.30, 0.50
    fig, ax = geom_axes(figsize=(6.3, 2.45), xlim=(-0.5, 33.5), ylim=(-3.2, 5.2))
    SUB = -T_BOX - 0.7
    box(ax, -0.5, SUB, 34, 0.7, "sub"); box(ax, -0.5, -T_BOX, 34, T_BOX, "ox")
    ax.plot([-0.5, 33.5], [SUB, SUB], color=MUTED, lw=0.6, ls=(0, (4, 3)))
    # upper oxide everywhere except a window in the III-V region
    xw0, xw1 = 21.0, 33.5
    box(ax, -0.5, 0, xw0 + 0.5, Y_TOP, "oxtop")
    box(ax, xw0, 0, xw1 - xw0, 0.05, "oxtop")          # thin bond layer left in the window
    # 1. Si to SiN interlayer coupler: SiN above a narrow silicon taper tip
    x1 = 2.6
    cbox(ax, x1, 0, 0.18, T_SI, "si", z=3)
    cbox(ax, x1, Y_SIN, W_SIN, T_SIN, "sin", z=3)
    dim(ax, (x1 + 1.05, T_SI), (x1 + 1.05, Y_SIN), "", fs=6)
    label(ax, x1 + 1.2, (T_SI + Y_SIN) / 2, "200 nm", fs=6.0, ha="left")
    # 2. SiN waveguide alone
    x2 = 7.6
    cbox(ax, x2, Y_SIN, W_SIN, T_SIN, "sin", z=3)
    # 3. TFLN film bonded on the oxide over a SiN waveguide, with gold electrodes on the film
    x3 = 14.6
    cbox(ax, x3, Y_SIN, W_SIN, T_SIN, "sin", z=3)
    box(ax, x3 - 5.6, Y_TOP, 11.2, T_LN, "ln", z=3)
    for sgn in (-1, 1):
        cbox(ax, x3 + sgn * (2.5 + 1.5), Y_TOP + T_LN, 3.0, T_AU, "metal", z=3)
    dim(ax, (x3 - 2.5, Y_TOP + T_LN + 0.75), (x3 + 2.5, Y_TOP + T_LN + 0.75), "5 µm gap", fs=6.0)
    # 4. III-V gain section bonded over a silicon waveguide (stack as in Chapter 27, illustrative)
    x4 = 27.3
    cbox(ax, x4, 0, 0.8, T_SI, "si", z=3)
    yb = T_SI + 0.03                                                    # 30 nm bond layer above the silicon
    box(ax, x4 - 6.0, T_SI, 12.0, 0.03, "bcb", z=3)
    box(ax, x4 - 6.0, yb, 12.0, 0.11, "inp", z=3)                       # n-InP contact layer
    cbox(ax, x4, yb + 0.11, 3.0, 0.30, "q", z=3)                        # MQW
    cbox(ax, x4, yb + 0.41, 3.0, 1.50, "inp", z=3)                      # p-InP
    cbox(ax, x4, yb + 1.91, 3.0, 0.10, "ge", z=3)                       # p-InGaAs contact layer (drawn dark)
    cbox(ax, x4, yb + 2.01, 3.0, 0.30, "metal", z=3)                    # p contact
    for sgn in (-1, 1):
        cbox(ax, x4 + sgn * 4.4, yb + 0.11, 1.6, 0.30, "metal", z=3)    # n contacts
    # silicon under the oxide in the other regions (the device layer was etched away there; nothing to draw)
    # labels
    yl = SUB - 0.2
    for x, t in ((x1, "Si → SiN\ninterlayer coupler"), (x2, "SiN waveguide\n1.2 × 0.4 µm"),
                 (x3, "TFLN on SiN:\nPockels phase shifter"), (x4, "bonded InP/MQW on Si:\ngain (laser, SOA)")):
        label(ax, x, yl, t, fs=6.6, va="top")
    label(ax, 33.4, -1.0, "BOX\n2 µm", fs=6.4, ha="right", col=INK)
    label(ax, 33.4, SUB + 0.35, "Si handle", fs=6.4, ha="right", col=INK)
    callout(ax, (x1 + 0.05, 0.1), (x1 - 1.4, -0.75), "Si tip", fs=6.4, ha="right")
    callout(ax, (x4 + 0.3, 0.1), (x4 + 1.6, -0.75), "Si 220 nm", fs=6.4, ha="left")
    callout(ax, (x3 - 4.6, Y_TOP + T_LN / 2), (x3 - 5.9, Y_TOP + 1.1), "LiNbO$_3$ film", fs=6.4, ha="right")
    callout(ax, (x4 - 1.5, yb + 0.26), (x4 - 3.3, yb + 1.6), "MQW", fs=6.4, ha="right")
    callout(ax, (x4 + 1.5, yb + 1.1), (x4 + 2.5, yb + 1.9), "p-InP", fs=6.4, ha="left")
    label(ax, x4 - 4.4, yb + 0.85, "n", fs=6.0); label(ax, x4 + 4.4, yb + 0.85, "n", fs=6.0)
    legend_patches(ax, [("si", "Si"), ("ox", "SiO$_2$"), ("sin", "Si$_3$N$_4$"), ("ln", "LiNbO$_3$"), ("inp", "InP"),
                        ("q", "InGaAsP MQW"), ("metal", "metal")], loc="upper left", ncol=7, fs=6.3,
                   columnspacing=0.9, handletextpad=0.4, bbox_to_anchor=(0.0, 1.0))
    scalebar(ax, 0.2, 3.25, 2.0, "2 µm")
    note(ax, "to scale; device spacing compressed; representative dimensions", loc="upper right")
    save(fig, "ch04_combined")


if __name__ == "__main__":
    fig_modesize(); fig_combined()
