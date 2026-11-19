"""Figures for Chapter 34 (sensing, LiDAR, quantum and computing).

Run from the repository root:   python -I -X utf8 figsrc/ch34_figs.py
Writes assets/figs/ch34_sensor.svg (from figsrc/ch34_fields.json, femwell; see ch34_fields.py), ch34_opa.svg,
ch34_fmcw.svg, ch34_quantum.svg, ch34_mesh.svg and ch34_comb.svg, and prints the numbers they show.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402
import matplotlib           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LAM = 1.55
OPT_C = RED


def sb(ax, x0, y0, L, H, w, mat="si"):
    """S-bend with fewer points than geomstyle.wg_sbend (smaller SVG)."""
    xs, ys = sbend_xy(x0, y0, L, H, n=48)
    return ribbon(ax, xs, ys, w, mat)


# ------------------------------------------------------------------ Figure: the sensor waveguide's fields (femwell)
def fig_sensor():
    path = os.path.join(HERE, "ch34_fields.json")
    if not os.path.exists(path):
        print("ch34_fields.json missing: run ch34_fields.py in the femwell container first"); return
    d = json.load(open(path))
    g = d["grid"]; nx, ny = g["nx"], g["ny"]
    x = np.linspace(*g["x"], nx); y = np.linspace(*g["y"], ny)
    W, T, NW = d["w"], d["t"], d["n_water"]
    k0 = 2 * np.pi / d["lam"]
    fig = plt.figure(figsize=(6.3, 2.45))
    # sensitivities from figsrc/ch34_sensor.py (finer mesh, two water indices): n_eff, n_g, d n_eff / d n_water, S
    SENS = {"TE": (2.4263, 4.235, 0.15, 54), "TM": (1.7031, 3.740, 0.50, 206)}
    print("sensor waveguide (femwell, coarse mesh for the fields):")
    for k, pol in enumerate(("TE", "TM")):
        m = d["modes"][pol]
        I = np.array(m["map"], float).reshape(ny, nx) / 999
        ne_s, ng, dndn, S = SENS[pol]
        gam = k0 * np.sqrt(ne_s ** 2 - NW ** 2)
        print(f"  {pol}: n_eff {m['neff']:.4f} (ch34_sensor.py {ne_s}), confinement core {m['conf_core']:.3f}, "
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
    save(fig, "ch34_sensor")


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
    save(fig, "ch34_opa")


# ------------------------------------------------------------------ Figure: FMCW chirp and beat
def fig_fmcw():
    B, T, c = 1e9, 10e-6, 3e8                      # Worked Example 34.2
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
    save(fig, "ch34_fmcw")


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
    save(fig, "ch34_quantum")


# ------------------------------------------------------------------ Figure: an MZI mesh for matrix multiplication
def fig_mesh():
    N = 6
    fig = plt.figure(figsize=(6.3, 3.3))
    # (a) one cell
    a = fig.add_axes([0.0, 0.62, 1.0, 0.38])
    frameless(a, xlim=(-0.5, 25.5), ylim=(-1.9, 2.3))
    w = 0.12
    ytop, ybot, yc = 1.0, -1.0, 0.25
    def coupler(x0):
        for s in (1, -1):
            yv = ytop if s == 1 else ybot
            sb(a, x0, yv, 1.5, -s * (1.0 - yc), w)
            wg_straight(a, x0 + 1.5, x0 + 3.0, s * yc, w)
            sb(a, x0 + 3.0, s * yc, 1.5, s * (1.0 - yc), w)
    for s, yv in ((1, ytop), (-1, ybot)):
        wg_straight(a, 0.0, 5.0, yv, w); wg_straight(a, 9.5, 12.0, yv, w); wg_straight(a, 16.5, 19.0, yv, w)
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
    save(fig, "ch34_mesh")


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
    label(a, 0, 4.15, "line spacing = FSR = $c/(n_g L)$", fs=6.6, va="top")
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
    save(fig, "ch34_comb")


if __name__ == "__main__":
    fig_sensor(); fig_opa(); fig_fmcw(); fig_quantum(); fig_mesh(); fig_comb()
