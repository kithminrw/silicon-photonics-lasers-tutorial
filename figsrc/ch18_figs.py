"""Figures and numbers for Chapter 18 (thermo-optic phase shifters).

Run from the worktree root:   python -I -X utf8 figsrc/ch18_figs.py
Writes assets/figs/ch18_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.

Data: figsrc/ch18_heater.json only (scikit-fem heat-equation solutions of figsrc/ch18_heater.py: G', P_pi, the step
response at 30 stored times with t10/t63/t90 from the full solution, and a 61 x 25 temperature map per case on
x = -12..12 um, y = -4.5..2.3 um, normalised to the waveguide). The maps are drawn with bilinear interpolation; the
crosstalk profile is the map interpolated to the waveguide's mid-height (y = 0.11 um). Geometry as in ch18_heater.py: rib
500 x 220 nm with a 90 nm slab, 2 um BOX, 2.3 um oxide cladding, TiN 2 um x 120 nm with its base 1.90 um above the BOX
(1.68 um above the rib), trenches 3-12 um from the waveguide, undercut 24 um wide.
The locking-loop panel uses the drop-port Lorentzian of the lock demo (_includes/demos/lock.html: 0.64 nm wide, peak 0.9).
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
H = json.load(open(os.path.join(HERE, "ch18_heater.json")))
LAM = 1.55e-6
DNDT = H["dndT"]                                   # 1.89e-4 /K (rib)
DTL = LAM / (2 * DNDT)                             # K m for a pi shift


def case(heater, config, d=H):
    return [c for c in d["cases"] if c["heater"] == heater and c["config"] == config][0]


def heatmap():
    """The maps of ch18_heater.json as 2D arrays, and each case's profile at the waveguide's mid-height."""
    m0 = H["cases"][0]["map"]
    x = np.linspace(*m0["x"], m0["nx"]); y = np.linspace(*m0["y"], m0["ny"])
    px = np.arange(0.0, 12.0001, 0.1)
    cases = []
    for c in H["cases"]:
        v = np.array(c["map"]["v"]).reshape(m0["ny"], m0["nx"])
        row = np.array([np.interp(0.11, y, v[:, i]) for i in range(len(x))])
        prof = np.interp(px, x, row) / np.interp(0.0, x, row)
        cases.append(dict(heater=c["heater"], config=c["config"], map=v, profile=prof))
    return dict(x=x, y=y, px=px, cases=cases)


# ------------------------------------------------------------------ Figure 18.1: heater types
def _section(ax, label_layers=False):
    box(ax, -3.2, -2.7, 6.4, 0.7, "sub", z=0)
    box(ax, -3.2, -2.0, 6.4, 2.0, "ox", z=0)
    box(ax, -3.2, 0.0, 6.4, 2.3, "oxtop", z=0)
    if label_layers:
        label(ax, -3.05, 1.45, "SiO$_2$\ncladding", ha="left", fs=FS_SMALL, col=MUTED)
        label(ax, -3.05, -1.0, "BOX", ha="left", fs=FS_SMALL, col=MUTED)
        label(ax, -3.05, -2.35, "Si substrate", ha="left", fs=FS_SMALL, col=MUTED)


def _rib(ax, rib="si", slab_l="si", slab_r="si"):
    box(ax, -3.2, 0, 2.95, 0.09, slab_l, z=2); box(ax, 0.25, 0, 2.95, 0.09, slab_r, z=2)
    box(ax, -0.25, 0, 0.5, 0.22, rib, ec=INK, lw=0.3, z=2)


def _heat(ax, x, y, n=3, dy=0.55, col=RED):
    """Small arrows showing heat leaving a source."""
    for k in range(n):
        xx = x + (k - (n - 1) / 2) * 0.55
        arrow(ax, (xx, y), (xx, y - dy), col=col, lw=0.8, ms=5, z=6)


def fig_types():
    fig = plt.figure(figsize=(6.3, 2.55))
    W = 0.325
    axes = [fig.add_axes([0.005 + i * 0.335, 0.0, W, 1.0]) for i in range(3)]
    for ax in axes:
        frameless(ax, (-2.6, 2.6), (-2.7, 2.65))
        _section(ax, label_layers=(ax is axes[0]))
    # (a) TiN strip above the rib
    ax = axes[0]; _rib(ax)
    box(ax, -1.0, 1.90, 2.0, 0.12, "tin", ec=INK, lw=0.3, z=4)
    _heat(ax, 0, 1.82, n=3, dy=0.6)
    dim(ax, (1.3, 0.22), (1.3, 1.90), "1.7 µm", text_off=(0.55, 0), bg=None)
    label(ax, 0, 2.17, "TiN, 2 µm", fs=FS_SMALL)
    label(ax, 0, 2.48, "metal heater", bold=True, fs=7.2)
    scalebar(ax, 1.3, -2.45, 1.0, "1 µm", above=True)
    # (b) doped-silicon heater beside the rib (current along the waveguide)
    ax = axes[1]; _rib(ax)
    for xa in (-1.5, 0.45):
        box(ax, xa, 0, 1.05, 0.09, "nn", z=3)
    callout(ax, (0.95, 0.06), (0.7, 0.85), "doped slab strips", ha="left")
    ax.text(0, 2.48, "doped-silicon heater", ha="center", va="center", fontsize=7.2, fontweight="bold", color=INK)
    ax.text(0, 2.1, "current along the waveguide", ha="center", va="center", fontsize=FS_SMALL, color=INK)
    _heat(ax, 0, -0.08, n=3, dy=0.6)
    # (c) in-waveguide heater: lightly doped rib and slab, contacts on both sides
    ax = axes[2]; _rib(ax, rib="ndop", slab_l="ndop", slab_r="ndop")
    box(ax, -3.2, 0, 1.7, 0.09, "nn", z=3); box(ax, 1.5, 0, 1.7, 0.09, "nn", z=3)
    for xc in (-2.0, 2.0):
        box(ax, xc - 0.2, 0.09, 0.4, 2.21, "metal", z=3)
    arrow(ax, (-1.35, 0.42), (1.35, 0.42), col=BLUE, lw=1.0, ms=6, z=6)
    label(ax, 0, 0.62, "current", col=BLUE, fs=FS_SMALL)
    label(ax, -0.85, -0.3, "n", fs=FS_SMALL); label(ax, -2.0, -0.3, "n$^{++}$", fs=FS_SMALL); label(ax, 2.0, -0.3, "n$^{++}$", fs=FS_SMALL)
    ax.text(0, 2.48, "in-waveguide heater", ha="center", va="center", fontsize=7.2, fontweight="bold", color=INK)
    _heat(ax, 0, -0.45, n=1, dy=0.55)
    for ax, s in zip(axes, "abc"):
        panel(ax, s, x=0.0, y=1.0)
    save(fig, "ch18_types")
    print(f"[18.1] TiN base {1.90:.2f} um, rib top 0.22 um: {1.90-0.22:.2f} um above the silicon")


# ------------------------------------------------------------------ Figure 18.2: thermal circuit and step response
def fig_circuit():
    c = case("metal", "plain")
    t, s = np.array(c["t"]), np.array(c["step"])
    t10, t63, t90 = c["t10"], c["t63"], c["t90"]                # from the full solution (ch18_heater.py)
    Gp = case("metal", "plain")["G_per_length"]; Ppi = case("metal", "plain")["P_pi_mW"]
    fig = plt.figure(figsize=(6.3, 2.5))
    # (a) circuit
    ax = fig.add_axes([0.0, 0.02, 0.43, 0.92]); frameless(ax, (0, 10), (0, 8), equal=False)
    yt, yb = 5.6, 1.3
    ax.plot([1.2, 8.6], [yt, yt], color=INK, lw=1.0); ax.plot([1.2, 8.6], [yb, yb], color=INK, lw=1.0)
    # current source P
    ax.add_patch(Circle((1.2, (yt + yb) / 2), 0.62, fc="white", ec=INK, lw=1.0, zorder=3))
    ax.plot([1.2, 1.2], [yt, (yt + yb) / 2 + 0.62], color=INK, lw=1.0); ax.plot([1.2, 1.2], [(yt + yb) / 2 - 0.62, yb], color=INK, lw=1.0)   # wired to both rails
    arrow(ax, (1.2, (yt + yb) / 2 - 0.4), (1.2, (yt + yb) / 2 + 0.42), col=INK, lw=0.9, ms=6, z=4)
    ax.text(0.45, (yt + yb) / 2, "$P$", ha="right", va="center", fontsize=8.5, color=RED)
    # resistor R_th (zig-zag)
    xr = 4.4; zz_y = np.linspace(yt - 1.0, yb + 1.0, 9); zz_x = xr + 0.32 * np.array([0, 1, -1, 1, -1, 1, -1, 1, 0])
    ax.plot([xr, xr], [yt, yt - 1.0], color=INK, lw=1.0); ax.plot(zz_x, zz_y, color=INK, lw=1.0); ax.plot([xr, xr], [yb + 1.0, yb], color=INK, lw=1.0)
    ax.text(xr + 0.55, (yt + yb) / 2, "$R_\\mathrm{th} = 1/G\u2032L$", ha="left", va="center", fontsize=7.5)   # U+2032: a real prime in the SVG (not cmsy10's '0')
    # capacitor C_th
    xc = 7.6; ym = (yt + yb) / 2
    ax.plot([xc, xc], [yt, ym + 0.18], color=INK, lw=1.0); ax.plot([xc, xc], [ym - 0.18, yb], color=INK, lw=1.0)
    ax.plot([xc - 0.5, xc + 0.5], [ym + 0.18] * 2, color=INK, lw=1.6); ax.plot([xc - 0.5, xc + 0.5], [ym - 0.18] * 2, color=INK, lw=1.6)
    ax.text(xc + 0.65, ym, "$C_\\mathrm{th}$", ha="left", va="center", fontsize=7.5)
    ax.plot([xr, xc], [yt, yt], "o", color=INK, ms=3)
    ax.text(5.9, yt + 0.25, "waveguide, $\\Delta T$", ha="center", va="bottom", fontsize=7, color=INK)
    ax.text(5.8, yb - 0.25, "heat sink: the substrate, $T_0$", ha="center", va="top", fontsize=7, color=INK)
    xg = 2.0
    ax.plot([xg, xg], [yb, yb - 0.55], color=INK, lw=1.0)
    for k, hw in enumerate((0.45, 0.3, 0.15)):
        ax.plot([xg - hw, xg + hw], [yb - 0.55 - 0.18 * k] * 2, color=INK, lw=1.0)
    ax.text(5.0, 7.75, "$\\Delta T = P R_\\mathrm{th}$,   $\\tau \\approx R_\\mathrm{th} C_\\mathrm{th}$", ha="center", va="top", fontsize=8)
    ax.text(5.0, 6.95, "heat ↔ current,  temperature ↔ voltage", ha="center", va="top", fontsize=6.6, color=MUTED)
    panel(ax, "a", x=0.0, y=1.0)
    # (b) FEM step response against a single RC pole
    b = fig.add_axes([0.55, 0.17, 0.43, 0.75])
    tt = np.linspace(0, 60e-6, 400)
    b.plot(t * 1e6, s, "o", color=C1, ms=3.5, label="heat equation, TiN plain")
    b.plot(tt * 1e6, 1 - np.exp(-tt / t63), color=C2, ls="--", lw=1.2, label=f"one RC pole, τ = {t63*1e6:.1f} µs")
    for v, tv in ((0.1, t10), (0.9, t90)):
        b.plot([0, tv * 1e6], [v, v], color=MUTED, lw=0.6, ls=":"); b.plot([tv * 1e6] * 2, [0, v], color=MUTED, lw=0.6, ls=":")
    b.annotate("", xy=(t90 * 1e6, 0.5), xytext=(t10 * 1e6, 0.5), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    b.text(t90 * 1e6 + 1.5, 0.5, f"10–90 %: {(t90-t10)*1e6:.0f} µs", ha="left", va="center", fontsize=7)
    b.set_xlim(0, 60); b.set_ylim(0, 1.05)
    finish(b, "Time after a power step (µs)", "$\\Delta T$ / final $\\Delta T$", legend=True, loc="lower right")
    tag(b, "b")
    save(fig, "ch18_circuit")
    rc1090 = t63 * np.log(9)
    print(f"[18.2] TiN plain: G' {Gp:.2f} W/(m K), P_pi {Ppi:.1f} mW; FEM t10 {t10*1e6:.2f} t63 {t63*1e6:.2f} t90 {t90*1e6:.2f} us, "
          f"10-90 {(t90-t10)*1e6:.1f} us; single pole with tau = t63: 10-90 {rc1090*1e6:.1f} us; "
          f"stored step samples {len(t)}")


# ------------------------------------------------------------------ Figure 18.3: temperature maps
def fig_maps():
    hm = heatmap()
    x, y = np.array(hm["x"]), np.array(hm["y"])
    L = 300e-6
    dTwg = DTL / L                                   # K at the waveguide, the same for every design at its P_pi
    vmax = 2.0 * dTwg
    fig = plt.figure(figsize=(6.3, 4.3))
    hs, gap = 0.285, 0.035
    tops = [0.975 - i * (hs + gap) for i in range(3)]
    names = (("plain", "plain"), ("trench", "deep trenches"), ("undercut", "substrate undercut"))
    for (cfg, title), top in zip(names, tops):
        ax = fig.add_axes([0.0, top - hs, 0.80, hs]); frameless(ax, (-12, 12), (-3.2, 2.5))
        c = case("metal", cfg, hm); m = np.array(c["map"]) * dTwg
        X, Y = np.meshgrid(x, y)
        air = np.zeros_like(m, bool)
        if cfg == "trench": air |= (np.abs(X) > 3.0) & (Y > -2.0) & (Y < 2.3)
        if cfg == "undercut": air |= (Y < -2.0)
        mm = np.ma.masked_where(air, m)
        # heat flow: streamlines of -grad T in the solid. Air is treated as insulating: its grid values are replaced by
        # the nearest solid ones, so the coarse gradient has no flux into a trench or the cavity.
        mf = m.copy()
        if cfg == "undercut":
            j0 = np.argmax(y >= -2.0); mf[:j0] = mf[j0]
        if cfg == "trench":
            rows = (y > -2.0) & (y < 2.3)
            for side in (1, -1):
                cols = np.where(side * x > 3.0)[0]; edge = np.argmin(abs(x - side * 2.8))
                mf[np.ix_(rows, cols)] = mf[rows, edge][:, None]
        # the map is drawn from mf so that it reaches the trench walls and the cavity roof (a masked array left a white
        # strip there); the air itself is covered by the white trench and cavity boxes drawn below
        ax.imshow(mf, extent=(x[0], x[-1], y[0], y[-1]), origin="lower", cmap=HEAT_CMAP, vmin=0, vmax=vmax,
                  interpolation="bilinear", zorder=1, aspect="auto")
        lv = [0.25 * dTwg, 0.5 * dTwg, dTwg, 1.5 * dTwg]
        cs = ax.contour(X, Y, mm, levels=lv, colors=INK, linewidths=0.45, zorder=3)
        for t in ax.clabel(cs, fmt=lambda v: f"{v:.0f} K" if v >= 10 else f"{v:.1f} K", fontsize=5.8, inline_spacing=2):
            t.set_zorder(6); t.set_bbox(dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.7))   # readable over streamlines and outlines
        gy, gx = np.gradient(mf, y, x)
        U, V = np.ma.masked_where(air, -gx), np.ma.masked_where(air, -gy)
        seeds = [(xx, 1.86) for xx in ((-0.9, -0.45, 0.45, 0.9) if cfg == "undercut" else (-0.9, -0.45, 0.0, 0.45, 0.9))]
        ax.streamplot(x, y, U.filled(np.nan), V.filled(np.nan), start_points=seeds, color=BLUE, linewidth=0.6,
                      arrowsize=0.55, density=3, broken_streamlines=False, integration_direction="forward", zorder=4)
        # outlines
        for yy in (0.0, -2.0):
            ax.plot([-12, 12], [yy, yy], color=MUTED, lw=0.3, zorder=2)
        ax.plot([-12, 12], [2.3, 2.3], color=INK, lw=0.6, zorder=2)
        if cfg == "trench":
            for xa in (-12, 3): box(ax, xa, -2.0, 9.0, 4.3, "#FFFFFF", ec=MUTED, lw=0.5, z=2)
            label(ax, 7.5, 0.15, "air trench", fs=FS_SMALL, col=MUTED, z=5)
        if cfg == "undercut":
            box(ax, -12, -5.0, 24, 3.0, "#FFFFFF", ec=MUTED, lw=0.5, z=2)
            label(ax, -6.0, -2.65, "cavity: substrate etched away", fs=FS_SMALL, col=MUTED, z=5)
        box(ax, -0.25, 0, 0.5, 0.22, "none", ec=INK, lw=0.6, z=5); box(ax, -2.5, 0, 5.0, 0.09, "none", ec=INK, lw=0.4, z=5)
        box(ax, -1.0, 1.90, 2.0, 0.12, "tin", ec=INK, lw=0.4, z=5)
        Ppi = case("metal", cfg)["P_pi_mW"]
        fig.text(0.815, top - 0.02, title, fontsize=7.6, fontweight="bold", color=INK, va="top")
        fig.text(0.815, top - 0.075, f"P$_\\pi$ = {Ppi:.1f} mW", fontsize=7, color=INK, va="top")
        panel(ax, "abc"[names.index((cfg, title))], x=-0.0, y=1.08)          # above the top surface line
        print(f"[18.3] {cfg}: P_pi {Ppi:.2f} mW, waveguide {dTwg:.1f} K at P_pi over {L*1e6:.0f} um, hottest point {ax_max(m, air):.1f} K, "
              f"substrate top (x=0) {np.interp(-2.0, y, m[:, np.argmin(abs(x))]):.1f} K")
    # shared scale bar and colour key
    ax = fig.axes[-1]
    scalebar(ax, 6.0, -2.95, 5.0, "5 µm", above=True)
    cax = fig.add_axes([0.835, 0.06, 0.13, 0.03])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0, vmax), cmap=HEAT_CMAP), cax=cax, orientation="horizontal")
    cb.set_ticks([0, dTwg, vmax]); cb.set_ticklabels(["0", f"{dTwg:.0f}", f"{vmax:.0f} K"]); cb.ax.tick_params(labelsize=6.5, length=2)
    cb.outline.set_linewidth(0.4)
    fig.text(0.835, 0.105, "temperature rise", fontsize=6.8, color=INK)
    save(fig, "ch18_maps")


def ax_max(m, air):
    return float(np.ma.masked_where(air, m).max())


# ------------------------------------------------------------------ Figure 18.4: crosstalk against distance
def fig_crosstalk():
    hm = heatmap()
    px = np.array(hm["px"])
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    for (h, cfg), col, ls, lab in ((("metal", "plain"), C1, "-", "TiN, plain"), (("metal", "undercut"), C4, "-", "TiN, undercut"),
                                    (("doped", "plain"), C1, "--", "doped Si, plain"), (("doped", "undercut"), C4, "--", "doped Si, undercut")):
        p = np.array(case(h, cfg, hm)["profile"])
        ax.plot(px, 100 * p, color=col, ls=ls, lw=1.4 if ls == "-" else 1.1, label=lab)
        print(f"[18.4] {h} {cfg}: neighbour at 5 um {100*np.interp(5, px, p):.0f} %, 10 um {100*np.interp(10, px, p):.0f} %, "
              f"12 um {100*np.interp(12, px, p):.1f} %")
    for d, h, cfg in ((5, "metal", "plain"), (10, "metal", "plain"), (10, "metal", "undercut")):
        v = 100 * np.interp(d, px, case(h, cfg, hm)["profile"])
        ax.plot(d, v, "o", color=C1 if cfg == "plain" else C4, ms=4)
        ax.text(d + 0.5, v + 2, f"{v:.0f} %", fontsize=7, color=C1 if cfg == "plain" else C4, ha="left", va="bottom")
    ax.set_xlim(0, 12); ax.set_ylim(0, 100)
    finish(ax, "Distance from the heated waveguide (µm)", "Neighbour's temperature rise (%)", legend=True, loc="upper right")
    ax.legend(loc="upper right", fontsize=7)
    save(fig, "ch18_crosstalk")


# ------------------------------------------------------------------ Figure 18.5: dither lock-in loop
FW, PK = 0.64, 0.9                                  # nm FWHM, peak drop transmission (lock demo)


def drop(d):
    return PK / (1 + (2 * d / FW) ** 2)


def ddrop(d):
    return -PK * 8 * d / FW ** 2 / (1 + (2 * d / FW) ** 2) ** 2


def fig_lock():
    fig = plt.figure(figsize=(6.3, 4.3))
    # (a) block diagram
    ax = fig.add_axes([0.0, 0.50, 1.0, 0.48]); frameless(ax, (0, 20), (1.0, 7.2), equal=False)
    yo = 5.9                                          # optical row
    block(ax, 1.3, yo - 0.95, 2.0, 0.8, "laser", fc="#FBEFEC", ec=OPT)
    ax.plot([2.3, 11.5], [yo - 0.95, yo - 0.95], color=OPT, lw=1.6)                         # bus
    ax.add_patch(Circle((6.0, yo - 0.1), 0.75, fc="none", ec=OPT, lw=1.6, zorder=3))         # ring, close to both buses
    ax.add_patch(Wedge((6.0, yo - 0.1), 0.83, 200, 340, width=0.16, fc=MAT["tin"], ec="none", alpha=0.6, zorder=4))   # heater over the ring
    ax.text(6.0, yo - 0.1, "ring", ha="center", va="center", fontsize=6.5, color=OPT)
    ax.plot([4.4, 9.0], [yo + 0.75, yo + 0.75], color=OPT, lw=1.6)                            # drop bus
    arrow(ax, (9.0, yo + 0.75), (10.4, yo + 0.75), col=OPT, lw=1.6, ms=8)
    ax.text(8.2, yo + 0.95, "drop", ha="center", va="bottom", fontsize=6.8, color=OPT)
    ax.text(11.4, yo - 0.8, "through →", ha="right", va="bottom", fontsize=6.8, color=OPT)
    callout(ax, (6.55, yo - 0.62), (7.6, yo - 0.25), "heater", ha="left")
    block(ax, 11.1, yo + 0.75, 1.4, 0.8, "PD", fc="#EEF3FB", ec=ELEC)
    ye = 2.4                                          # electrical row
    block(ax, 13.6, yo + 0.75, 1.5, 0.8, "TIA", fc="#EEF3FB", ec=ELEC)
    wire(ax, [(11.8, yo + 0.75), (12.85, yo + 0.75)], col=ELEC)
    ax.add_patch(Circle((16.1, yo + 0.75), 0.42, fc="white", ec=ELEC, lw=0.9, zorder=3)); ax.text(16.1, yo + 0.75, "×", ha="center", va="center", fontsize=10, color=ELEC, zorder=4)
    wire(ax, [(14.35, yo + 0.75), (15.68, yo + 0.75)], col=ELEC)
    block(ax, 18.4, yo + 0.75, 2.2, 0.8, "low-pass", fc="#EEF3FB", ec=ELEC)
    wire(ax, [(16.52, yo + 0.75), (17.3, yo + 0.75)], col=ELEC)
    block(ax, 18.4, ye + 1.3, 2.2, 0.8, "integrator", fc="#EEF3FB", ec=ELEC)
    wire(ax, [(18.4, yo + 0.35), (18.4, ye + 1.7)], col=ELEC)
    ax.text(18.55, (yo + ye + 2.05) / 2 + 0.2, "error\nsignal", ha="left", va="center", fontsize=6.5, color=ELEC, linespacing=1.0)
    block(ax, 14.6, 4.95, 2.0, 0.8, "dither\n20 kHz", fc="#F3F6FB", ec=INK, fs=6.6)
    wire(ax, [(15.6, 4.95), (16.1, 4.95), (16.1, yo + 0.33)], col=INK)
    ax.add_patch(Circle((12.3, ye + 1.3), 0.42, fc="white", ec=ELEC, lw=0.9, zorder=3)); ax.text(12.3, ye + 1.3, "+", ha="center", va="center", fontsize=10, color=ELEC, zorder=4)
    wire(ax, [(17.3, ye + 1.3), (12.72, ye + 1.3)], col=ELEC)
    wire(ax, [(13.6, 4.95), (12.3, 4.95), (12.3, ye + 1.72)], col=INK)
    block(ax, 8.6, ye + 1.3, 2.4, 0.8, "heater driver", fc="#EEF3FB", ec=ELEC, fs=6.6)
    wire(ax, [(11.88, ye + 1.3), (9.8, ye + 1.3)], col=ELEC)
    wire(ax, [(7.4, ye + 1.3), (6.0, ye + 1.3), (6.0, yo - 1.08)], col=ELEC)
    ax.text(3.4, ye + 0.15, "Heater power = integrator output + small dither.\nThe lock-in (× and low-pass) gives the slope's sign;\n"
            "the integrator climbs to the top of the drop peak.", ha="left", va="center", fontsize=6.6, color=INK, linespacing=1.3)
    ax.text(0.2, 1.3, "optical", color=OPT, fontsize=6.6, ha="left"); ax.text(1.5, 1.3, "electrical", color=ELEC, fontsize=6.6, ha="left")
    panel(ax, "a", x=0.0, y=1.0)
    # (b) drop-port Lorentzian and the dither at three operating points
    d = np.linspace(-1.2, 1.2, 600)
    b = fig.add_axes([0.08, 0.08, 0.38, 0.33])
    b.plot(d, drop(d), color=OPT)
    dd = 0.09
    for d0, txt in ((-0.32, "in phase"), (0.0, "only 2f"), (0.32, "antiphase")):
        b.plot(d0, drop(d0), "o", color=INK, ms=3.5)
        b.annotate("", xy=(d0 + dd, drop(d0) - 0.14), xytext=(d0 - dd, drop(d0) - 0.14), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=5))
        b.text(d0, drop(d0) + 0.05, txt, ha="center", va="bottom", fontsize=6.5, color=INK)
    b.set_xlim(-1.2, 1.2); b.set_ylim(0, 1.1)
    finish(b, "Resonance − laser (nm)", "Drop-port power")
    b.text(-1.15, 1.05, "← ring cold (blue)", fontsize=6.3, color=MUTED, ha="left", va="top")
    tag(b, "b")
    # (c) lock-in output
    c = fig.add_axes([0.60, 0.08, 0.38, 0.33])
    e = ddrop(d) / np.abs(ddrop(d)).max()
    c.plot(d, e, color=ELEC)
    c.axhline(0, color=INK, lw=0.6)
    c.plot(0, 0, "o", color=INK, ms=4); c.text(0.06, -0.12, "lock point", fontsize=6.6, ha="left", va="top")
    c.annotate("", xy=(-0.12, 0.62), xytext=(-0.55, 0.62), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8))
    c.annotate("", xy=(0.12, -0.62), xytext=(0.55, -0.62), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8))
    c.text(-0.6, 0.75, "heat more", fontsize=6.5, color=MUTED, ha="center"); c.text(0.6, -0.86, "heat less", fontsize=6.5, color=MUTED, ha="center")
    c.set_xlim(-1.2, 1.2); c.set_ylim(-1.15, 1.15)
    finish(c, "Resonance − laser (nm)", "Lock-in output (norm.)")
    tag(c, "c")
    save(fig, "ch18_lock")
    print(f"[18.5] drop Lorentzian FWHM {FW} nm, peak {PK}; error signal extrema at +-{FW/(2*np.sqrt(3)):.3f} nm")


if __name__ == "__main__":
    which = sys.argv[1:] or ["types", "circuit", "maps", "crosstalk", "lock"]
    for w in which:
        globals()["fig_" + w]()
