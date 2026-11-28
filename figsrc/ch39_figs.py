"""Figures for Chapter 39 (sensing, LiDAR, quantum and computing).

Run from the repository root:   python -I -X utf8 figsrc/ch39_figs.py
Writes assets/figs/ch39_sensor.svg (from figsrc/ch39_fields.json, femwell; see ch39_fields.py), ch39_opa.svg,
ch39_fmcw.svg, ch39_quantum.svg, ch39_mesh.svg and ch39_comb.svg, and prints the numbers they show.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402
import matplotlib           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55
_trapz = getattr(np, "trapezoid", None) or np.trapz     # NumPy 2 renamed trapz; the same trapezoidal integral
OPT_C = RED


def sb(ax, x0, y0, L, H, w, mat="si"):
    """S-bend with fewer points than geomstyle.wg_sbend (smaller SVG)."""
    xs, ys = sbend_xy(x0, y0, L, H, n=48)
    return ribbon(ax, xs, ys, w, mat)


def joint(ax, x, y, w, mat="si", e=0.03):
    """A short straight piece over the joint of two waveguide pieces at (x, y), where both run along x: abutting
    polygons leave a hairline seam when anti-aliased; this covers it (same colour, opaque)."""
    return wg_straight(ax, x - e, x + e, y, w, mat)


# ------------------------------------------------------------------ Figure: the sensor waveguide's fields (femwell)
def fig_sensor():
    path = os.path.join(HERE, "ch39_fields.json")
    if not os.path.exists(path):
        print("ch39_fields.json missing: run ch39_fields.py in the femwell container first"); return
    d = json.load(open(path))
    g = d["grid"]; nx, ny = g["nx"], g["ny"]
    x = np.linspace(*g["x"], nx); y = np.linspace(*g["y"], ny)
    W, T, NW = d["w"], d["t"], d["n_water"]
    k0 = 2 * np.pi / d["lam"]
    fig = plt.figure(figsize=(6.3, 2.45))
    # sensitivities from figsrc/ch39_sensor.py (finer mesh, two water indices): n_eff, n_g, d n_eff / d n_water, S
    SENS = {"TE": (2.4263, 4.235, 0.15, 54), "TM": (1.7031, 3.740, 0.50, 206)}
    print("sensor waveguide (femwell, coarse mesh for the fields):")
    for k, pol in enumerate(("TE", "TM")):
        m = d["modes"][pol]
        I = np.array(m["map"], float).reshape(ny, nx) / 999
        ne_s, ng, dndn, S = SENS[pol]
        gam = k0 * np.sqrt(ne_s ** 2 - NW ** 2)
        print(f"  {pol}: n_eff {m['neff']:.4f} (ch39_sensor.py {ne_s}), confinement core {m['conf_core']:.3f}, "
              f"water {m['conf_water']:.3f}; decay length into water 1/γ {1e3/gam:.0f} nm; S {S} nm/RIU, dn_eff/dn_c {dndn}")
        ax = fig.add_axes([0.01 + 0.5 * k, 0.10, 0.47, 0.88])
        frameless(ax, xlim=g["x"], ylim=g["y"])
        box(ax, g["x"][0], g["y"][0], g["x"][1] - g["x"][0], -g["y"][0], "ox", z=0)
        box(ax, g["x"][0], 0, g["x"][1] - g["x"][0], g["y"][1], "water", z=0)
        rgba = np.zeros(I.shape + (4,)); rgba[..., :3] = matplotlib.colors.to_rgb(BLUE)
        rgba[..., 3] = np.clip(I, 0, 1) ** 0.6 * 0.92
        ax.imshow(rgba, extent=(*g["x"], *g["y"]), origin="lower", zorder=1, interpolation="bilinear")
        cs = ax.contour(x, y, I, levels=[np.exp(-2), 0.5], colors=[INK, INK], linewidths=[0.6, 0.6], linestyles=[":", "-"], zorder=3)
        ax.add_patch(Rectangle((-W / 2, 0), W, T, fc="none", ec=INK, lw=0.9, zorder=4))
        label(ax, g["x"][0] + 0.2, g["y"][1] - 0.05, f"water, $n$ = {NW}", fs=6.6, ha="left", va="top")
        label(ax, g["x"][0] + 0.05, g["y"][0] + 0.05, "SiO$_2$", fs=6.6, ha="left", va="bottom")
        label(ax, g["x"][1] - 0.05, g["y"][1] - 0.05, f"{pol}$_0$", fs=8, ha="right", va="top", bold=True)
        txt = (f"$n_\\mathrm{{eff}}$ = {ne_s:.3f}\n∂$n_\\mathrm{{eff}}$/∂$n_c$ = {dndn:.2f}\n"
               f"$S$ = {S:.0f} nm/RIU")
        label(ax, g["x"][1] - 0.05, g["y"][0] + 0.05, txt, fs=6.5, ha="right", va="bottom", bg="white")
        if k == 0: scalebar(ax, -1.15, -0.32, 0.5, "500 nm")
        panel(ax, "ab"[k], 0.0, 1.0)
        ax.set_clip_on(True)
    fig.text(0.5, 0.015, "power density $S_z$ (blue); contours at half and 1/e² of the peak; 500 × 220 nm Si strip, 1550 nm",
             ha="center", fontsize=6.5, color=MUTED)
    save(fig, "ch39_sensor")


# ------------------------------------------------------------------ Figure: optical phased array
def array_factor(th, N, d, dphi):
    psi = 2 * np.pi / LAM * d * np.sin(th) - dphi
    num = np.sin(N * psi / 2); den = N * np.sin(psi / 2)
    out = np.where(np.abs(den) < 1e-12, 1.0, (num / np.where(np.abs(den) < 1e-12, 1, den)) ** 2)
    return out


def fig_opa():
    N, th0 = 16, np.radians(20)
    fig = plt.figure(figsize=(6.3, 4.4))
    # (a) top view of an 8-channel array (schematic)
    a = fig.add_axes([0.0, 0.50, 1.0, 0.50])
    frameless(a, xlim=(-1.0, 31.0), ylim=(-5.4, 5.6))
    w = 0.16
    wg_straight(a, -0.6, 1.0, 0, w)
    label(a, -0.6, 0.6, "light in", fs=6.6, ha="left", col=OPT_C)
    ys = [0.0]
    xs = [1.0, 3.6, 6.2, 8.8]
    for lev in range(3):
        new = []
        h = 4.0 / 2 ** lev
        for yc in ys:
            for s in (1, -1):
                sb(a, xs[lev], yc, xs[lev + 1] - xs[lev], s * h / 2, w)
                new.append(yc + s * h / 2)
        ys = new
    ys = sorted(ys)
    joint(a, xs[0], 0.0, w)
    yl = [0.0]
    for lev in range(3):                       # cover the seams where the tree's levels meet
        h = 4.0 / 2 ** lev
        yl = [yc + s * h / 2 for yc in yl for s in (1, -1)]
        for yc in yl:
            joint(a, xs[lev + 1], yc, w)
    for yc in ys:
        wg_straight(a, 8.8, 15.0, yc, w)
        cbox(a, 12.0, yc - 0.22, 3.4, 0.44, "tin", z=3)
    label(a, 12.0, max(ys) + 0.9, "phase shifters", fs=6.6)
    label(a, 4.9, -5.0, "splitter tree (1 → N)", fs=6.6)
    # fan-in to the emitter pitch
    pitch = 0.7
    ye = [(i - (len(ys) - 1) / 2) * pitch for i in range(len(ys))]
    for y0, y1 in zip(ys, ye):
        sb(a, 15.0, y0, 4.0, y1 - y0, w)
        wg_straight(a, 19.0, 28.5, y1, w)
        joint(a, 15.0, y0, w); joint(a, 19.0, y1, w)
        for xt in np.arange(19.6, 28.4, 0.45):
            a.plot([xt, xt], [y1 - 0.13, y1 + 0.13], color="white", lw=0.8, zorder=4)
    label(a, 23.8, max(ye) + 0.9, "grating emitters", fs=6.6)
    dim(a, (28.9, ye[-1]), (28.9, ye[-2]), "", fs=6.0)
    label(a, 29.15, (ye[-1] + ye[-2]) / 2, "pitch $d$", fs=6.4, ha="left")
    label(a, 23.8, min(ye) - 0.95, "beam leaves the chip upwards", fs=6.3, col=MUTED)
    label(a, 30.8, -4.75, "phase step Δφ steers θ (across the emitters)\nwavelength steers ψ (along them, Chapter 15)",
          fs=6.4, ha="right", va="center")
    note(a, "schematic, N = 8 drawn", loc="upper right")
    panel(a, "a", 0.0, 1.0)
    # (b) far field of 16 emitters steered to 20°, at two pitches
    b = fig.add_axes([0.095, 0.09, 0.87, 0.33])
    th = np.radians(np.linspace(-90, 90, 3601))
    print("OPA, N = %d, steered to %.0f°:" % (N, np.degrees(th0)))
    for d, col, lab in ((LAM / 2, C1, "$d$ = λ/2 = 0.78 µm"), (2.0, C4, "$d$ = 2 µm")):
        dphi = 2 * np.pi / LAM * d * np.sin(th0)
        AF = array_factor(th, N, d, dphi)
        b.plot(np.degrees(th), 10 * np.log10(np.maximum(AF, 1e-4)), color=col, lw=1.2, label=lab)
        bw = np.degrees(0.886 * LAM / (N * d * np.cos(th0)))
        # numerical half-power width of the main lobe
        m = np.abs(np.degrees(th) - np.degrees(th0)) < 3 * bw
        tt = np.degrees(th)[m][AF[m] >= 0.5]
        lobes = [np.degrees(np.arcsin(s)) for s in (np.sin(th0) + k * LAM / d for k in range(-5, 6)) if abs(s) <= 1]
        print(f"  d = {d:.3f} µm: Δφ = {np.degrees(dphi):.0f}°, beam width 0.886λ/(Nd cosθ) = {bw:.2f}° "
              f"(numerical {tt.max() - tt.min():.2f}°), main and grating lobes at " + ", ".join(f"{l:.1f}°" for l in lobes))
    b.annotate("main beam, 20°", (20, 0), xytext=(34, -4.5), fontsize=6.6, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.annotate("grating lobe", (-25.7, 0), xytext=(-62, -4.5), fontsize=6.6, color=C4, arrowprops=dict(arrowstyle="-", color=C4, lw=0.6))
    b.set_xlim(-90, 90); b.set_ylim(-30, 2); b.set_xticks(range(-90, 91, 30))
    finish(b, "Angle θ (°)", "Far field (dB)", legend=True, loc="upper right")
    b.legend(loc="upper left", fontsize=6.6, ncol=1, handlelength=1.4, bbox_to_anchor=(0.0, 1.02))
    b.text(89, 1.0, "16 emitters, array factor", fontsize=6.5, color=MUTED, ha="right", va="top")
    tag(b, "b")
    save(fig, "ch39_opa")


# ------------------------------------------------------------------ Figure: FMCW chirp and beat
def fig_fmcw():
    B, T, c = 1e9, 10e-6, 3e8                      # Worked Example 39.2
    targets = [(40.0, 0.5), (100.0, 1.0)]
    fb = lambda R: 2 * R * B / (c * T)
    print("FMCW: resolution %.0f cm; beat at 100 m %.1f MHz, at 40 m %.1f MHz; delay at 100 m %.3f µs" %
          (100 * c / (2 * B), fb(100) / 1e6, fb(40) / 1e6, 2 * 100 / c * 1e6))
    fig, (a, z, b) = plt.subplots(1, 3, figsize=(6.3, 2.5), gridspec_kw=dict(width_ratios=[1.15, 0.85, 1.15]))
    t = np.linspace(0, 2 * T, 8000)
    saw = lambda t: B * ((t % T) / T)
    tau = 2 * 100 / c
    for ax in (a, z):
        ax.plot(t * 1e6, saw(t) / 1e9, color=C1, label="transmitted")
        tr = t[t >= tau]
        ax.plot(tr * 1e6, saw(tr - tau) / 1e9, color=C2, ls="--", label="echo, 100 m")
    a.add_patch(Rectangle((4.0, 0.36), 2.0, 0.28, fc="none", ec=INK, lw=0.6, zorder=5))
    a.text(6.2, 0.36, "(b)", fontsize=6.4, va="top")
    a.set_xlim(0, 20); a.set_ylim(0, 1.25)
    finish(a, "Time (µs)", "Frequency offset (GHz)")
    a.legend(loc="upper left", fontsize=6.3, ncol=2, handlelength=1.5, columnspacing=0.8)
    tag(a, "a")
    t1 = 5.3e-6
    z.annotate("", (t1 * 1e6, saw(t1 - tau) / 1e9), (t1 * 1e6, saw(t1) / 1e9),
               arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    z.text(t1 * 1e6 + 0.06, (saw(t1) + saw(t1 - tau)) / 2e9, f"$f_b$ = {fb(100)/1e6:.1f} MHz", fontsize=6.4, va="center")
    y0 = 0.45
    z.annotate("", (4.5 + tau * 1e6, y0), (4.5, y0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    z.text(4.06, y0 + 0.022, f"2R/c =\n{tau*1e6:.3f} µs", fontsize=6.4, ha="left", va="bottom")
    z.set_xlim(4, 6); z.set_ylim(0.36, 0.64)
    finish(z, "Time (µs)")
    tag(z, "b")
    # (c) spectrum of the beat signal over one sweep (Hann window), two targets
    fs, n = 500e6, 5000
    tt = np.arange(n) / fs
    sig = sum(A * np.cos(2 * np.pi * fb(R) * tt) for R, A in targets)
    win = np.hanning(n)
    spec = np.abs(np.fft.rfft(sig * win, 8 * n)) ** 2
    f = np.fft.rfftfreq(8 * n, 1 / fs)
    spec_db = 10 * np.log10(spec / spec.max() + 1e-12)
    b.plot(f / 1e6, spec_db, color=C1, lw=1.0)
    for R, A in targets:
        b.annotate(f"{R:.0f} m", (fb(R) / 1e6, 10 * np.log10(A ** 2)), xytext=(fb(R) / 1e6 + 6, 10 * np.log10(A ** 2) - 6),
                   fontsize=6.6, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xlim(0, 100); b.set_ylim(-40, 5)
    finish(b, "Beat frequency (MHz)", "Beat spectrum (dB)")
    top = b.secondary_xaxis("top", functions=(lambda fm: fm * 1e6 * c * T / (2 * B), lambda R: 2 * R * B / (c * T) / 1e6))
    top.set_xlabel("Range (m)", labelpad=2); top.set_xticks([50, 100, 150])
    tag(b, "c")
    fig.tight_layout(w_pad=1.2)
    save(fig, "ch39_fmcw")


# ------------------------------------------------------------------ Figure: a quantum-photonic chip
def fig_quantum():
    fig = plt.figure(figsize=(6.3, 2.75))
    a = fig.add_axes([0.0, 0.0, 0.74, 1.0])
    frameless(a, xlim=(-1, 47), ylim=(-9.4, 9.2))
    w = 0.22
    block(a, 1.6, 0, 3.6, 3.0, "pump\nlaser", fc="#FBEDEA", ec=OPT_C, fs=6.3)
    wg_straight(a, 3.4, 5.5, 0, w)
    for s in (1, -1):
        sb(a, 5.5, 0, 3.0, s * 4.0, w)
        wg_straight(a, 8.5, 18.0, s * 4.0, w)
        wg_ring(a, 12.0, s * 4.0 + s * 1.45, 1.2, w, "sin")
        block(a, 16.5, s * 4.0, 2.6, 1.6, "", fc="#F3F6FB", ec=MUTED, lw=0.6)
        # demultiplex signal and idler onto two waveguides
        wg_straight(a, 18.0, 19.5, s * 4.0, w)
        for s2 in (1, -1):
            sb(a, 19.5, s * 4.0, 3.0, s2 * 1.2, w)
            wg_straight(a, 22.5, 24.0, s * 4.0 + s2 * 1.2, w)
            for xj in (22.5, 24.0):            # no hairline seams at the joints
                joint(a, xj, s * 4.0 + s2 * 1.2, w)
        for xj in (8.5, 18.0, 19.5):
            joint(a, xj, s * 4.0, w)
    joint(a, 5.5, 0.0, w)
    label(a, 10.5, 8.3, "SFWM ring sources", fs=6.5)
    label(a, 16.5, -6.4, "pump\nfilters", fs=6.0, col=MUTED, va="top")
    label(a, 21.0, -6.6, "signal /\nidler split", fs=6.0, col=MUTED, va="top")
    # mesh
    ins = sorted([s * 4.0 + s2 * 1.2 for s in (1, -1) for s2 in (1, -1)])
    for yv in ins:
        wg_straight(a, 24.0, 37.5, yv, w)
    cols = [[(0, 1), (2, 3)], [(1, 2)], [(0, 1), (2, 3)], [(1, 2)]]
    for ci, prs in enumerate(cols):
        xc = 26.0 + 3.0 * ci
        for i, j in prs:
            block(a, xc, (ins[i] + ins[j]) / 2, 2.2, abs(ins[j] - ins[i]) + 0.9, "", fc="#FFF4E0", ec=AMBER, lw=0.7, z=4)
    label(a, 30.5, 8.3, "MZI mesh", fs=6.5)
    label(a, 30.5, -6.9, "heaters set\nthe unitary", fs=6.0, col=MUTED, va="top")
    a.add_patch(FancyBboxPatch((38.0, -7.6), 8.4, 15.6, boxstyle="round,pad=0,rounding_size=0.6", fc="#F2F5FA", ec=INK, lw=0.7, ls="--"))
    for yv in ins:
        wg_straight(a, 37.5, 41.2, yv, w)
        a.add_patch(Polygon([[41.2, yv - 0.7], [43.6, yv - 0.7], [43.6, yv + 0.7], [41.2, yv + 0.7]], fc="#DCE4F0", ec=INK, lw=0.5, zorder=4))
        for k in range(4):
            a.plot([41.4 + 0.55 * k, 41.4 + 0.55 * k], [yv - 0.55, yv + 0.55], color=INK, lw=0.4, zorder=5)
    label(a, 42.2, 7.0, "SNSPDs", fs=6.5)
    label(a, 42.2, -8.5, "cryogenic", fs=6.0, col=MUTED)
    note(a, "schematic", loc="lower left")
    panel(a, "a", 0.0, 1.0)
    # (b) energy conservation in four-wave mixing
    b = fig.add_axes([0.79, 0.24, 0.19, 0.62])
    for f_, h, col, t in ((-1, 0.55, C1, "idler"), (0, 1.0, OPT_C, "pump"), (1, 0.55, C4, "signal")):
        b.plot([f_, f_], [0, h], color=col, lw=2.2)
        b.text(f_, h + 0.05, t, ha="center", va="bottom", fontsize=6.4, color=col)
    b.annotate("", (1, 0.3), (0, 0.3), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.6, mutation_scale=6))
    b.annotate("", (-1, 0.3), (0, 0.3), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.6, mutation_scale=6))
    b.set_xlim(-1.7, 1.7); b.set_ylim(0, 1.35); b.set_yticks([]); b.set_xticks([-1, 0, 1])
    b.set_xticklabels(["$\\omega_i$", "$\\omega_p$", "$\\omega_s$"]); b.grid(False)
    b.spines["left"].set_visible(False)
    b.set_xlabel("$2\\omega_p = \\omega_s + \\omega_i$", fontsize=7)
    tag(b, "b")
    save(fig, "ch39_quantum")


# ------------------------------------------------------------------ Figure: an MZI mesh for matrix multiplication
def fig_mesh():
    N = 6
    fig = plt.figure(figsize=(6.3, 3.3))
    # (a) one cell
    a = fig.add_axes([0.0, 0.62, 1.0, 0.38])
    frameless(a, xlim=(-0.5, 25.5), ylim=(-1.9, 2.3))
    w = 0.12
    ytop, ybot, yc = 1.0, -1.0, 0.25
    e = 0.02                                   # straights overlap the S-bends slightly: no hairline seam at the joints
    def coupler(x0):
        for s in (1, -1):
            yv = ytop if s == 1 else ybot
            sb(a, x0, yv, 1.5, -s * (1.0 - yc), w)
            wg_straight(a, x0 + 1.5 - e, x0 + 3.0 + e, s * yc, w)
            sb(a, x0 + 3.0, s * yc, 1.5, s * (1.0 - yc), w)
    for s, yv in ((1, ytop), (-1, ybot)):
        wg_straight(a, 0.0, 5.0 + e, yv, w); wg_straight(a, 9.5 - e, 12.0 + e, yv, w); wg_straight(a, 16.5 - e, 19.0, yv, w)
    coupler(5.0); coupler(12.0)
    cbox(a, 2.5, ytop - 0.25, 3.0, 0.5, "tin", z=3); label(a, 2.5, ytop + 0.6, "φ (external)", fs=6.5)
    cbox(a, 10.75, ytop - 0.25, 2.5, 0.5, "tin", z=3); label(a, 10.75, ytop + 0.6, "θ (internal)", fs=6.5)
    label(a, 7.25, -1.6, "50:50 coupler", fs=6.2, col=MUTED); label(a, 14.25, -1.6, "50:50 coupler", fs=6.2, col=MUTED)
    label(a, 25.3, 0.3, "θ sets the split (bar ↔ cross),\nφ the relative phase:\nany 2 × 2 unitary", fs=6.6, ha="right", va="center")
    panel(a, "a", 0.0, 1.0)
    # (b) rectangular mesh, N = 6
    b = fig.add_axes([0.0, 0.0, 1.0, 0.60])
    frameless(b, xlim=(-1.6, 25.5), ylim=(-0.9, 6.4), equal=False)
    yl = [5.0 - k for k in range(N)]
    n_mzi = 0
    for yv in yl:
        b.plot([0, 22.6], [yv, yv], color=OPT_C, lw=1.0, zorder=1)
    for ci in range(N):
        xc = 1.8 + 3.0 * ci
        start = 0 if ci % 2 == 0 else 1
        for i in range(start, N - 1, 2):
            block(b, xc, (yl[i] + yl[i + 1]) / 2, 2.2, 1.55, "", fc="#FFF4E0", ec=AMBER, lw=0.8, z=3)
            label(b, xc, (yl[i] + yl[i + 1]) / 2, "θ, φ", fs=5.8, z=5)
            n_mzi += 1
    for yv in yl:
        cbox(b, 20.6, yv - 0.17, 1.0, 0.34, "tin", z=3)
    label(b, 20.6, 5.65, "output\nphases", fs=6.0, va="bottom")
    for k, yv in enumerate(yl):
        label(b, -0.3, yv, f"$x_{k+1}$", fs=7, ha="right")
        label(b, 22.9, yv, f"$y_{k+1}$", fs=7, ha="left")
    label(b, 9.3, -0.65, f"N = {N}: N(N − 1)/2 = {n_mzi} MZIs and N output phase shifters set an N × N unitary; light computes y = Ux in one pass",
          fs=6.5)
    print("mesh: N = %d, MZIs %d (N(N-1)/2 = %d), phase shifters %d" % (N, n_mzi, N * (N - 1) // 2, 2 * n_mzi + N))
    panel(b, "b", 0.0, 1.0)
    save(fig, "ch39_mesh")


# ------------------------------------------------------------------ Figure: a Kerr microcomb
def fig_comb():
    fig = plt.figure(figsize=(6.3, 2.4))
    a = fig.add_axes([0.0, 0.0, 0.44, 1.0])
    frameless(a, xlim=(-6.5, 6.5), ylim=(-4.4, 4.4))
    wg_ring(a, 0, 1.15, 2.6, 0.26, "sin")
    wg_straight(a, -6.0, 6.0, -1.75, 0.26, "sin")
    arrow(a, (-6.2, -2.7), (-4.2, -2.7), col=OPT_C, lw=1.2, ms=8)
    label(a, -5.2, -3.45, "CW pump", fs=6.6, col=OPT_C)
    arrow(a, (4.2, -2.7), (6.2, -2.7), col=OPT_C, lw=1.2, ms=8)
    label(a, 5.2, -3.45, "comb out", fs=6.6, col=OPT_C)
    label(a, 0, 1.15, "high-Q\nSi$_3$N$_4$ ring", fs=6.6)
    label(a, 0, 4.05, "line spacing = FSR = $c/(n_g L)$", fs=6.6, va="bottom")      # above the ring, not on it
    note(a, "schematic", loc="lower left")
    panel(a, "a", 0.0, 1.0)
    b = fig.add_axes([0.52, 0.2, 0.46, 0.68])
    m = np.arange(-40, 41)
    P = 10 * np.log10(1 / np.cosh(m / 11.0) ** 2)
    P[m == 0] = 8.0
    for mm, pp in zip(m, P):
        b.plot([mm, mm], [-40, pp], color=OPT_C if mm == 0 else C1, lw=1.0 if mm else 1.6)
    x0 = 12
    b.annotate("", (x0 + 1, -4.0), (x0, -4.0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=5, shrinkA=0, shrinkB=0))
    b.text(x0 + 2.0, -3.4, "FSR", fontsize=6.6, va="bottom")
    b.text(0, 9.0, "pump", fontsize=6.6, color=OPT_C, ha="center", va="bottom")
    b.text(41, 13, "sech$^2$ envelope\n(soliton comb)", fontsize=6.4, color=MUTED, ha="right", va="top")
    b.set_xlim(-42, 42); b.set_ylim(-40, 14)
    b.set_yticks([]); b.set_xticks([0]); b.set_xticklabels(["$f_p$"]); b.grid(False)
    b.spines["left"].set_visible(False)
    finish(b, "Frequency", "Power (dB, schematic)")
    tag(b, "b")
    save(fig, "ch39_comb")

# ------------------------------------------------------------------ Figure: a Fourier-transform spectrometer (Section 39.6)
FTS_N, FTS_DL, FTS_NG, FTS_LAM = 32, 0.40e-3, 4.2, 1.55e-6     # MZIs, delay step (m), group index of the Si wire, centre (m)


def fts_model():
    """MZI k has a delay k*DL, so it samples the interferogram at an optical path difference x_k = n_g k DL
    (the phase's slope with wavenumber is set by the group index). Spectrum on a fine wavenumber grid inside the
    unaliased band of width 1/(2 dx) above sigma0, where sigma0*dx is an integer (the band folds onto itself there)."""
    dx = FTS_NG * FTS_DL
    s0 = np.floor(1 / FTS_LAM * dx) / dx                     # band edge, 1/m
    band = 1 / (2 * dx)
    s = np.linspace(0, band, 4001)                            # offset wavenumber inside the band
    lam = 1 / (s0 + s) * 1e9                                  # nm
    lc = lam[2000]
    def line(l0, w, a): return a * np.exp(-0.5 * ((lam - l0) / w) ** 2)
    S = line(lc - 0.16, 0.006, 1.0) + line(lc - 0.06, 0.006, 0.8) + line(lc + 0.17, 0.05, 0.45)   # two close lines and a broad band
    k = np.arange(FTS_N); x = k * dx
    # each MZI's two outputs, subtracted, give the cosine interferogram without its constant part
    I = np.array([_trapz(S * np.cos(2 * np.pi * s * xk), s) for xk in x])
    # reconstruction: one-sided cosine transform (half weight at k = 0), Hann apodisation, on the band's grid
    w = 0.5 * (1 + np.cos(np.pi * k / FTS_N)); w[0] *= 0.5
    rec = np.array([np.sum(w * I * np.cos(2 * np.pi * sj * x)) for sj in s])
    rec = np.clip(rec, 0, None); rec *= _trapz(S, s) / _trapz(rec, s)    # same area as the input
    m = S.max(); S /= m; rec /= m
    dlam = (lam[0] - lam[-1]) / 1
    res = FTS_LAM ** 2 / (FTS_N * dx) * 1e12               # pm, about lambda^2/(N n_g DL)
    return k, I / np.abs(I).max(), lam, S, rec, dlam, res, (FTS_N - 1) * FTS_DL * 1e3


def fig_spectrometer():
    k, I, lam, S, rec, band, res, lmax = fts_model()
    print(f"spectrometer: N = {FTS_N}, delay step {FTS_DL*1e3:.2f} mm, longest delay {lmax:.1f} mm, n_g = {FTS_NG}: "
          f"band {band:.3f} nm, resolution lambda^2/(N n_g dL) = {res:.1f} pm, channels {band*1e3/res:.1f}")
    fig = plt.figure(figsize=(6.3, 3.9))
    a = fig.add_axes([0.0, 0.50, 1.0, 0.48]); frameless(a, (-1, 41), (-1.2, 9.6), equal=False)
    wg_straight(a, -0.5, 2.7, 4.6, 0.10, "si"); label(a, -0.4, 5.2, "light in", fs=FS_SMALL, ha="left", col=RED)
    block(a, 4.0, 4.6, 2.6, 2.4, "splitter\ntree", fs=FS_SMALL)
    ys = [8.4, 6.7, 5.0, 2.3, 0.6]; names = ["k = 0", "k = 1", "k = 2", "k = 30", "k = 31"]; dls = [0, 1, 2, 30, 31]
    for yv, nm, n in zip(ys, names, dls):
        # branch from the splitter tree: a diagonal, then level into the MZI (its label sits on the level part)
        a.plot([5.3, 7.0, 8.8], [4.6 + (yv - 4.6) * 0.15, yv, yv], color=INK, lw=0.7)
        block(a, 10.0, yv, 2.4, 0.9, "", fc="#F3F6FB", lw=0.7)
        a.plot([11.2, 22.8], [yv - 0.25, yv - 0.25], color=INK, lw=0.7)      # each arm one unbroken line
        a.plot([11.2, 22.8], [yv + 0.25, yv + 0.25], color=INK, lw=0.7)
        if n:                                                    # MZI k > 0: the delay arm drawn as a loop that grows with k
            r = 0.2 + 0.5 * n / 31
            hh = r * 1.1 + 0.05                                  # loop height; it rests on the arm (tangent), as a coiled delay
            a.add_patch(matplotlib.patches.Ellipse((14.0 + r * 2.2, yv + 0.25 + hh / 2), r * 4.4, hh, fill=False, ec=AMBER, lw=0.9))
        block(a, 24.0, yv, 2.4, 0.9, "", fc="#F3F6FB", lw=0.7)
        a.plot([25.2, 27.35], [yv, yv], color=INK, lw=0.7)
        block(a, 28.0, yv, 1.3, 0.8, "PD", fs=5.8, fc="#FFF4E0", ec=AMBER, lw=0.7)
        label(a, 7.9, yv + 0.12, nm, fs=6.0, va="bottom")
        label(a, 29.0, yv, f"P$_{{{n}}}$", fs=6.4, ha="left")
    for xv in (10.0, 24.0, 28.0): label(a, xv, 3.65, "·\n·\n·", fs=6.5)
    label(a, 19.0, 9.45, "MZI k: one arm longer by k·ΔL (drawn as a loop)", fs=FS_SMALL)
    label(a, 35.5, 5.6, "each detector reads one\npoint of the interferogram;\nits Fourier transform\nis the spectrum", fs=FS_SMALL, ha="center")
    panel(a, "a", 0.0, 1.0); label(a, 40.8, -1.0, "schematic", fs=6.0, col=MUTED, italic=True, ha="right")
    b = fig.add_axes([0.07, 0.08, 0.36, 0.34])
    b.vlines(k, 0, I, color=C1, lw=1.0); b.plot(k, I, "o", color=C1, ms=2.6); b.axhline(0, color=INK, lw=0.6)
    b.set_xlim(-1, FTS_N); b.set_ylim(-1.08, 1.08); b.set_yticks([-1, 0, 1])
    finish(b, "MZI number k (delay k·ΔL)", "Output difference"); tag(b, "b")
    c = fig.add_axes([0.55, 0.08, 0.43, 0.34])
    c.plot(lam, S, color=MUTED, lw=1.0, label="input spectrum")
    c.plot(lam, rec, color=C4, lw=1.4, label=f"from 32 detectors ({res:.0f} pm resolution)")
    c.set_xlim(lam.min(), lam.max()); c.set_ylim(0, 1.25); c.set_yticks([0, 0.5, 1])
    c.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2))           # every 0.2 nm: the labels do not run together
    c.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.1f"))
    finish(c, "Wavelength (nm)", "Power (normalised)"); c.legend(loc="upper left", fontsize=6.0); tag(c, "c")
    save(fig, "ch39_spectrometer")


# ------------------------------------------------------------------ Figure: a chip gyroscope and its shot-noise limit (Section 39.7)
def gyro_limit(ell, loss_db_cm, r=2.5e-3, P0=1e-3, lam=1.55e-6):
    """Shot-noise-limited rotation rate (deg/h in 1 s) of an interferometric gyroscope: a spiral of length ell (m)
    at mean radius r encloses N A = ell r / 2, so dphi = 4 pi ell r Omega / (lam c); the detected power is P0 e^(-alpha ell),
    and the phase noise sqrt(2 h nu B / P) for B = 1 Hz (ideal detector; backscatter, Kerr and drift left out)."""
    h, c = 6.626e-34, 2.998e8
    alpha = loss_db_cm * 100 / 4.343
    dphi = np.sqrt(2 * h * c / lam / (P0 * np.exp(-alpha * ell)))
    om = dphi * lam * c / (4 * np.pi * ell * r)
    return om * 180 / np.pi * 3600


def fig_gyro():
    earth = 15.04                         # deg/h
    om_e = earth * np.pi / 180 / 3600
    dph_chip = 4 * np.pi * 1.0 * 2.5e-3 * om_e / (1.55e-6 * 2.998e8)
    dph_fib = 4 * np.pi * 1000 * 0.04 * om_e / (1.55e-6 * 2.998e8)
    print(f"gyro: Earth rate {om_e:.3e} rad/s; Sagnac phase of 1 m at r = 2.5 mm {dph_chip:.2e} rad, of 1 km fibre at r = 4 cm "
          f"{dph_fib:.2e} rad ({dph_fib/dph_chip:.0f}x)")
    for D, ng in ((0.018, 1.5),):
        print(f"gyro: ring of diameter {D*1e3:.0f} mm, n_g {ng}: Sagnac splitting {D*om_e/(ng*1.55e-6):.2f} Hz at the Earth rate")
    ell = np.logspace(-2, 1.3, 400)
    fig = plt.figure(figsize=(6.3, 2.7))
    a = fig.add_axes([0.0, 0.0, 0.48, 1.0]); frameless(a, (-4.3, 7.6), (-4.6, 4.3))
    # one continuous Archimedean spiral; its outer end and its inner end both lead to the coupler on the right
    N, r0, pitch, W = 4, 1.0, 0.55, 1.5
    th = np.linspace(0, 2 * np.pi * N, 1600); rr = r0 + pitch * th / (2 * np.pi)
    sx, sy = rr * np.cos(th), rr * np.sin(th); rmax = rr[-1]
    a.plot(sx, sy, color=MAT["sin"], lw=W, solid_capstyle="butt", zorder=2)
    def qarc(cx, cy, R, t0, t1):
        t = np.linspace(t0, t1, 60); return cx + R * np.cos(t), cy + R * np.sin(t)
    xc = 5.4                                                   # coupler position
    # outer lead: leaves the outer end going up (+y), a quarter turn right, then straight into the top coupler arm
    R1 = 0.95; x1, y1 = qarc(rmax + R1, 0, R1, np.pi, np.pi / 2)
    a.plot(np.r_[x1, xc - 0.6], np.r_[y1, R1], color=MAT["sin"], lw=W, zorder=2)
    # inner lead: leaves the inner end going down (-y), a quarter turn right, then straight out to the bottom arm,
    # passing under the turns on a second waveguide layer (dashed between the two interlayer transitions, dots)
    # the transition (first dot) sits on the quarter turn, in the gap before the next turn, so the inner end never
    # touches that turn; from there on it is dashed, under every turn
    R2 = 0.45; tsplit = 1.25 * np.pi
    x2, y2 = qarc(r0 + R2, 0, R2, np.pi, tsplit)
    a.plot(x2, y2, color=MAT["sin"], lw=W, zorder=2)
    x3, y3 = qarc(r0 + R2, 0, R2, tsplit, 3 * np.pi / 2)
    xb = rmax + 0.35
    a.plot(np.r_[x3, xb], np.r_[y3, -R2], color=VIOLET, lw=W, ls=(0, (3, 1.6)), zorder=3)
    for xv, yv in ((x2[-1], y2[-1]), (xb, -R2)):
        a.plot([xv], [yv], "o", color=VIOLET, ms=3.2, zorder=4)
    a.plot([xb, xc - 0.6], [-R2, -R2], color=MAT["sin"], lw=W, zorder=2)
    yb = -R2
    block(a, xc, (R1 + yb) / 2, 1.2, R1 - yb + 0.3, "2×2\ncoupler", fs=5.6, fc="#F3F6FB", lw=0.7)
    for yv, txt in ((R1, "laser"), (yb, "detector")):
        a.plot([xc + 0.6, xc + 1.0], [yv, yv], color=MAT["sin"], lw=W, zorder=2)
        label(a, xc + 1.05, yv, txt, fs=5.6, ha="left")
    # light both ways round: arrowheads on the spiral itself
    def head(tc, sgn, col):
        t = np.array([tc, tc + sgn * 0.12]); r = r0 + pitch * t / (2 * np.pi)
        a.annotate("", xy=(r[1] * np.cos(t[1]), r[1] * np.sin(t[1])), xytext=(r[0] * np.cos(t[0]), r[0] * np.sin(t[0])),
                   arrowprops=dict(arrowstyle="-|>", color=col, lw=0, mutation_scale=9), zorder=6)
    head(2 * np.pi * 3 + 1.1, -1, RED); head(2 * np.pi * 2 + 4.3, +1, BLUE)
    label(a, 2.2, 3.35, "clockwise", fs=FS_SMALL, col=RED); label(a, -3.2, -3.4, "anticlockwise", fs=FS_SMALL, col=BLUE)
    label(a, 1.0, -3.95, "spiral: N turns at mean radius r", fs=5.8)
    a.add_patch(matplotlib.patches.FancyArrowPatch((-3.9, 2.4), (-2.6, 3.7), connectionstyle="arc3,rad=-0.4", arrowstyle="-|>", mutation_scale=8, color=INK, lw=0.9))
    label(a, -4.2, 1.9, "rotation Ω", fs=FS_SMALL, ha="left")
    label(a, 5.0, -1.6, "inner end crosses under\nthe turns on a second\nwaveguide layer (dashed)", fs=5.6, col=VIOLET, ha="center")
    panel(a, "a", 0.02, 1.0); label(a, 7.5, -4.5, "schematic", fs=6.0, col=MUTED, italic=True, ha="right")
    b = fig.add_axes([0.57, 0.16, 0.41, 0.76])
    for ldb, col, (tx, ty) in ((1.0, C2, (0.2, 900)), (0.1, C1, (2.0, 95)), (0.01, C3, (8.6, 9.0))):   # labels off the curves
        om = gyro_limit(ell, ldb); i = np.argmin(om)
        b.loglog(ell, om, color=col, lw=1.5)
        b.plot(ell[i], om[i], "o", color=col, ms=3.5)
        b.text(tx, ty, f"{ldb:g} dB/cm", fontsize=6.4, color=col, ha="center", va="center")
        print(f"gyro: {ldb} dB/cm: best length {ell[i]:.2f} m (2/alpha = {2*4.343/(ldb*100):.2f} m), limit {om[i]:.0f} deg/h in 1 s")
    b.axhline(earth, color=INK, lw=0.8, ls=(0, (4, 3))); b.text(0.012, earth * 1.3, "Earth's rotation, 15°/h", fontsize=6.3, color=INK)
    b.set_xlim(0.01, 20); b.set_ylim(3, 3e4)
    finish(b, "Spiral length (m)", "Smallest rotation (°/h, 1 s)")
    tag(b, "b")
    save(fig, "ch39_gyro")


if __name__ == "__main__":
    ALL = {"sensor": fig_sensor, "opa": fig_opa, "fmcw": fig_fmcw, "quantum": fig_quantum, "mesh": fig_mesh, "comb": fig_comb,
           "spectrometer": fig_spectrometer, "gyro": fig_gyro}
    for name in (sys.argv[1:] or list(ALL)):
        ALL[name]()
