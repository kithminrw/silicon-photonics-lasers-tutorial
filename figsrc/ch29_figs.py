"""Figures of Chapter 29 (design principles and simulation workflows), and every number the chapter computes.

    python -I -X utf8 figsrc/ch29_figs.py [workflow flowdown costmap convergence sensitivity montecarlo tuning loop numbers]

ch29_workflow     the design-and-simulation workflow as a V: specify downwards, verify upwards, measurement closes it
ch29_flowdown     the reference link's targets flowed down to device parameters
ch29_costmap      what each level of model captures against what one evaluation costs; the coupler's design tasks
ch29_convergence  femwell mesh convergence of the coupler's cross-over length and of its sensitivity to a width bias
ch29_sensitivity  tornado chart of the coupling against each variation; the bias-tolerant width
ch29_montecarlo   Monte Carlo histograms with spec limits: the coupler's coupling, the ring's resonance error
ch29_tuning       yield against heater range for three ways of locking the rings (Worked Example 29.3)
ch29_loop         separating width and thickness errors from two measured rings

The femwell and MEEP results come from figsrc/ch29_sims.py (run in the photonics-labs Docker container), stored in
figsrc/ch29_sims.json. The wafer model is that of Worked Example 35.1 and Figure 37.6.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
SIMS = json.load(open(os.path.join(HERE, "ch29_sims.json")))

SPEC_FC, VER_FC, LAB_FC = "#EEF3FA", "#EAF5F2", "#FBF3E6"     # block fills: specify (down), verify (up), lab
NL = "\n"

# ------------------------------------------------------------------ shared numbers (Chapters 1, 6, 12, 14, 18, 35)
LAM = 1550.0                     # nm
NG = 4.18                        # group index of the 500 x 220 nm strip (Chapter 6)
SPACING = 3.2                    # channel spacing, nm (400 GHz)
FSR = 4 * SPACING                # 12.8 nm (Chapter 14)
L_RING = (LAM * 1e-3) ** 2 / (NG * FSR * 1e-3)        # um
ALPHA_DB_CM = 2.0                # propagation loss, dB/cm
A_RT = 10 ** (-ALPHA_DB_CM * L_RING * 1e-4 / 20)       # single-pass amplitude transmission
XT_SPEC = -20.0                  # dB, neighbouring-channel crosstalk (Table 1.3)
PASS_MIN = 0.4                   # nm: drop passband no narrower than a 50 Gb/s NRZ signal (Chapter 14)
SW, ST = 0.6, 1.4                # ring shift per nm of width and of thickness, nm/nm (Chapters 6, 35)
DTDT = 0.075                     # nm/K (Chapter 1, 18)
T_RANGE = 50.0                   # K, 20 to 70 C
ETA = 0.26                       # nm/mW heater tuning efficiency (Worked Example 18.2)
BL = 2.5                         # um, effective coupling length added by the bends (Chapter 9)


# ------------------------------------------------------------------ ring and coupler models
def drop(phi, k2, a=A_RT):
    """Drop-port power of a symmetric add-drop ring (Chapter 12), phase phi from resonance."""
    t2 = 1 - k2
    return k2 ** 2 * a / (1 - 2 * a * t2 * np.cos(phi) + a ** 2 * t2 ** 2)


def crosstalk_db(k2, a=A_RT):
    """Power of a neighbouring channel (3.2 nm = FSR/4 away) relative to the channel, in the drop port."""
    return 10 * np.log10(drop(2 * np.pi * SPACING / FSR, k2, a) / drop(0.0, k2, a))


def fwhm_nm(k2, a=A_RT):
    t2 = 1 - k2
    c = (1 + a ** 2 * t2 ** 2 - 2 * (1 - a * t2) ** 2) / (2 * a * t2)
    return np.arccos(c) * FSR / np.pi


def drop_loss_db(k2, a=A_RT):
    return -10 * np.log10(drop(0.0, k2, a))


def solve_k2(f, target, lo=0.01, hi=0.5):
    """Bisection for f(k2) = target, f monotonic."""
    flo = f(lo) - target
    for _ in range(80):
        mid = 0.5 * (lo + hi); fm = f(mid) - target
        if np.sign(fm) == np.sign(flo): lo, flo = mid, fm
        else: hi = mid
    return 0.5 * (lo + hi)


def k2_of(lc, lx):
    """Power coupling of a coupler of effective length lc with cross-over length lx (Chapter 9)."""
    return np.sin(np.pi * lc / (2 * lx)) ** 2


LX0 = SIMS["sens"]["Lx0"]        # um, femwell, 500/200/220 nm at 1550 nm


def window():
    k2_hi = solve_k2(crosstalk_db, XT_SPEC)
    k2_lo = solve_k2(fwhm_nm, PASS_MIN)
    k2_c = np.sqrt(k2_lo * k2_hi)
    return k2_lo, k2_c, k2_hi


def lc_for(k2, lx=LX0):
    return 2 * lx * np.arcsin(np.sqrt(k2)) / np.pi


def twoline(ax, x, y, title, sub, fs1=6.9, fs2=5.6, dy=(0.15, -0.13)):
    label(ax, x, y + dy[0], title, fs=fs1, bold=True)
    label(ax, x, y + dy[1], sub, fs=fs2, col=MUTED)


# ------------------------------------------------------------------ Figure 29.1
def fig_workflow():
    fig, ax = geom_axes(figsize=(6.3, 3.3), xlim=(0, 10.6), ylim=(-0.15, 5.4), equal=False)
    bw, bh = 2.3, 0.66
    left = [("system specification", "Table 1.3: rate, reach, BER," + NL + "margin, energy per bit"),
            ("architecture and budgets", "blocks; loss, wavelength," + NL + "heater and energy budgets"),
            ("component targets", "FSR, coupling window, Q," + NL + "extinction, insertion loss"),
            ("device design", "cheapest model first: formula," + NL + "mode solver, EME, 2.5D FDTD")]
    right = [("chip measured", "test and analysis" + NL + "(Chapters 36, 37)"),
             ("layout verified", "DRC, connectivity, test" + NL + "structures (Chapters 33, 34)"),
             ("circuit verified", "compact models with their" + NL + "variation; circuit yield"),
             ("device verified", "full-wave check (3D FDTD);" + NL + "corners and Monte Carlo")]
    ys = [4.55, 3.45, 2.35, 1.25]
    xl = [1.30, 1.95, 2.60, 3.25]
    xr = [10.6 - x for x in xl]
    for i in range(4):
        block(ax, xl[i], ys[i], bw, bh, "", fc=SPEC_FC, lw=0.7)
        twoline(ax, xl[i], ys[i], *left[i])
        block(ax, xr[i], ys[i], bw, bh, "", fc=VER_FC if i else LAB_FC, lw=0.7)
        twoline(ax, xr[i], ys[i], *right[i])
        ax.annotate("", xy=(xl[i] + bw / 2 + 0.05, ys[i]), xytext=(xr[i] - bw / 2 - 0.05, ys[i]),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.7, ls=(0, (3, 2)), mutation_scale=6))
        if i < 3:
            arrow(ax, (xl[i] + 0.25, ys[i] - bh / 2 - 0.02), (xl[i + 1] - 0.05, ys[i + 1] + bh / 2 + 0.02), lw=0.8, ms=6)
            arrow(ax, (xr[i + 1] + 0.05, ys[i + 1] + bh / 2 + 0.02), (xr[i] - 0.25, ys[i] - bh / 2 - 0.02), lw=0.8, ms=6)
    label(ax, 5.3, ys[0] + 0.22, "does it meet the spec" + NL + "at this level?", fs=5.8, col=MUTED)
    # bottom: the design point, reached by the simulation loop
    yb = 0.24
    block(ax, 5.3, yb, 3.9, 0.56, "", fc="#F3F0FA", lw=0.7)
    label(ax, 5.3, yb + 0.12, "design point", fs=6.9, bold=True)
    label(ax, 5.3, yb - 0.12, "converge → sweep → sensitivities → corners, Monte Carlo", fs=5.6, col=VIOLET)
    th = np.radians(np.linspace(100, -230, 120)); cx, cy = 4.5, yb + 0.12
    ax.plot(cx + 0.17 * np.cos(th), cy + 0.13 * np.sin(th), color=VIOLET, lw=0.8, zorder=5)
    arrow(ax, (cx + 0.17 * np.cos(th[-4]), cy + 0.13 * np.sin(th[-4])), (cx + 0.17 * np.cos(th[-1]), cy + 0.13 * np.sin(th[-1])),
          col=VIOLET, lw=0.8, ms=5)
    arrow(ax, (xl[3] + 0.3, ys[3] - bh / 2 - 0.02), (5.3 - 1.3, yb + 0.28 + 0.02), lw=0.8, ms=6)
    arrow(ax, (5.3 + 1.3, yb + 0.28 + 0.02), (xr[3] - 0.3, ys[3] - bh / 2 - 0.02), lw=0.8, ms=6)
    # measurement closes the loop
    xe = 10.56
    ax.plot([xr[0] + bw / 2 + 0.02, xe, xe, xr[2] + bw / 2 + 0.06], [ys[0], ys[0], ys[2], ys[2]], color=RED, lw=1.0, zorder=2)
    arrow(ax, (xr[2] + bw / 2 + 0.08, ys[2]), (xr[2] + bw / 2 + 0.02, ys[2]), col=RED, lw=1.0, ms=6)
    label(ax, 9.86, 1.83, "measured bias," + NL + "indices, losses" + NL + "update the models", fs=5.6, col=RED, ha="center")
    label(ax, 0.05, 0.62, "specify" + NL + "(top-down)", fs=6.2, col=BLUE, ha="left", bold=True)
    label(ax, 10.55, 0.62, "verify" + NL + "(bottom-up)", fs=6.2, col=TEAL, ha="right", bold=True)
    save(fig, "ch29_workflow")


# ------------------------------------------------------------------ Figure 29.2
def fig_flowdown():
    lo, c, hi = window()
    fig, ax = geom_axes(figsize=(6.3, 3.35), xlim=(0, 10.9), ylim=(0.25, 5.25), equal=False)
    xs = [1.75, 4.35, 6.95, 9.55]
    ys = [4.62, 3.42, 2.22, 1.0]
    bw, bh = 2.42, 0.82
    lvl = ["system", "block", "component", "device"]
    for y, t in zip(ys, lvl):
        label(ax, 0.2, y, t, fs=6.2, col=MUTED, rot=90, italic=True)

    def card(x, y, w, title, sub, tag=None, fc=SPEC_FC):
        block(ax, x, y, w, bh, "", fc=fc, lw=0.7)
        label(ax, x, y + 0.22, title, fs=6.7, bold=True)
        label(ax, x, y - 0.12, sub, fs=5.5, col=INK)
        if tag:
            label(ax, x + w / 2 - 0.05, y - bh / 2 + 0.07, tag, fs=5.0, col=MUTED, ha="right", italic=True)

    def link(x0, y0, x1, y1):
        ym = (y0 - bh / 2 + y1 + bh / 2) / 2
        ax.plot([x0, x0, x1, x1], [y0 - bh / 2, ym, ym, y1 + bh / 2], color=INK, lw=0.7, zorder=1)

    card(5.65, ys[0], 8.2, "reference link (Table 1.3)",
         "4 × 50 Gb/s NRZ over 2 km, BER below 10$^{-12}$, margin ≥ 3 dB, ≤ 5 pJ/bit, 20–70 °C", "Chapter 1", fc="#F7F9FC")
    xd = (xs[0] + xs[1]) / 2
    card(xd, ys[1], 5.02, "demultiplexer", "crosstalk ≤ −20 dB, drop loss ≤ 1 dB," + NL + "four channels 3.2 nm apart", "Chapter 14")
    card(xs[2], ys[1], bw, "ring modulator", "extinction ≥ 4 dB at 2 Vpp," + NL + "insertion loss ≤ 3 dB", "Chapter 20")
    card(xs[3], ys[1], bw, "thermal control", "rings on channel, 20–70 °C," + NL + "inside the energy budget", "Chapter 18")
    for x in (xd, xs[2], xs[3]):
        link(x, ys[0], x, ys[1])
    comp = [("free spectral range", "4 × 3.2 nm = 12.8 nm", "Chapter 14"),
            ("coupling per coupler", f"κ² between {lo*100:.1f} and {hi*100:.1f} %" + NL + "(passband, crosstalk)", "Example 29.1"),
            ("tuning per volt, Q", "≈ 50 pm/V; Q$_i$ 15 000," + NL + "Q$_L$ 8000", "Chapter 20"),
            ("tuning range", "3.75 nm of drift" + NL + "+ fabrication spread", "Chapters 18, 35")]
    dev = [("ring length", f"L = {L_RING:.1f} µm (R = {L_RING/2/np.pi:.2f} µm)" + NL + f"for n$_g$ = {NG}", "Chapter 14"),
           ("coupler", f"200 nm gap, {lc_for(c):.1f} µm effective" + NL + "length (centre of window)", "Example 29.1"),
           ("junction", "lateral junction made" + NL + "L- or U-shaped", "Chapters 19, 20"),
           ("heater", "TiN, 0.26 nm/mW; range set" + NL + "by the locking scheme", "Ch. 18, Example 29.3")]
    for i in range(4):
        card(xs[i], ys[2], bw, *comp[i])
        card(xs[i], ys[3], bw, *dev[i], fc="#F3F0FA")
        link(xs[i], ys[2], xs[i], ys[3])
        link(xd if i < 2 else xs[i], ys[1], xs[i], ys[2])
    save(fig, "ch29_flowdown")


# ------------------------------------------------------------------ the cost of each level of model (Worked Example 29.2)
def costs():
    """Time per evaluation of the demultiplexer ring's coupler with each level of model, on one CPU core.
    Measured: femwell supermode solve (4 and 12 modes) and MEEP's FDTD speed and memory per cell (ch29_sims.py);
    estimated from them: EME, 2.5D and 3D FDTD of the whole coupler."""
    lo, c, hi = window()
    ls = lc_for(c) - BL                                 # straight section, um
    sb_len, sb_off = 13.0, 2.0                          # S-bends of Figure 9.3: length and lateral offset, um
    L_dev = ls + 2 * sb_len
    W_dev = 2 * (0.1 + 0.5 + sb_off)                    # outer edges of the two guides, um
    buf, pml, dx = 1.0, 1.0, 0.02                       # um
    X = L_dev + 2 * (buf + pml); Y = W_dev + 2 * (buf + pml); Z = 0.22 + 2 * (buf + pml)
    nx, ny, nz = X / dx, Y / dx, Z / dx
    c0 = 299792458.0
    S = 0.5                                             # Courant number (MEEP's default; 3D limit 1/sqrt(3))
    dt = S * dx * 1e-6 / c0                             # s
    T = 2 * 4.2 * X * 1e-6 / c0 + 0.25e-12              # light crosses the domain twice, plus the source pulse
    steps = T / dt
    bench = {b["dims"]: b for b in SIMS["bench"]}
    cells3, cells2 = nx * ny * nz, nx * ny
    t3 = cells3 * steps / bench[3]["rate"]
    t2 = cells2 * steps / bench[2]["rate"]
    mem3 = cells3 * bench[3]["bytes_per_cell"]
    eme = {r["modes"]: r["sec"] for r in SIMS["eme"]}
    n_sec = 1 + 2 * 20                                  # straight section + 20 sections per S-bend
    t_eme = n_sec * eme[12]
    t_mode = SIMS["time25"]["median"]
    # a compact-model evaluation: the ring's drop port at 1000 wavelengths
    phi = np.linspace(-np.pi, np.pi, 1000)
    t0 = time.perf_counter()
    for _ in range(200):
        drop(phi, c)
    t_cm = (time.perf_counter() - t0) / 200
    t0 = time.perf_counter()
    for _ in range(20000):
        k2_of(8.2, 37.85)
    t_formula = (time.perf_counter() - t0) / 20000
    return dict(L_dev=L_dev, W_dev=W_dev, X=X, Y=Y, Z=Z, nx=nx, ny=ny, nz=nz, cells3=cells3, cells2=cells2, dt=dt, T=T,
                steps=steps, t3=t3, t2=t2, mem3=mem3, n_sec=n_sec, t_eme=t_eme, t_mode=t_mode, t_cm=t_cm,
                t_formula=t_formula, ls=ls, eme12=eme[12], eme4=eme[4])


def fmt_time(s):
    for unit, v in (("year", 3.156e7), ("day", 86400), ("h", 3600), ("min", 60), ("s", 1), ("ms", 1e-3), ("µs", 1e-6)):
        if s >= v:
            x = s / v
            txt = f"{x:.0f}" if x >= 10 else f"{x:.1f}"
            return f"{txt} {unit}" + ("s" if unit in ("year", "day") and txt != "1.0" else "")
    return f"{s*1e9:.0f} ns"


# ------------------------------------------------------------------ Figure 29.3
def fig_costmap():
    C = costs()
    fig = plt.figure(figsize=(6.3, 3.0))
    a = fig.add_axes([0.25, 0.17, 0.42, 0.74])
    rows = [("formula", "coupled-mode theory, ring" + NL + "and link formulas", C["t_formula"], "ideal geometry, weak coupling"),
            ("compact model", "S-matrices in a circuit" + NL + "simulator", C["t_cm"], "only where it was fitted"),
            ("mode solver", "FDE or FEM on one" + NL + "cross-section", C["t_mode"], "uniform along z"),
            ("EME", "local modes, section" + NL + "by section", C["t_eme"], "finite mode set"),
            ("2.5D FDTD", "in-plane FDTD with" + NL + "an effective index", C["t2"], "no vertical radiation"),
            ("3D FDTD", "full-vector Maxwell" + NL + "on a grid", C["t3"], "grid and run time")]
    cols = [MUTED, VIOLET, C1, C3, C2, C4]
    for i, (n, sub, t, miss) in enumerate(rows):
        a.plot([t], [i], "o", color=cols[i], ms=6, zorder=5)
        a.text(t * 1.8, i + 0.12, fmt_time(t), fontsize=6.6, color=cols[i], va="center", ha="left", fontweight="bold")
        a.text(t * 1.8, i - 0.2, miss, fontsize=5.7, color=MUTED, va="center", ha="left", style="italic")
        a.text(-0.03, i + 0.13, n, transform=a.get_yaxis_transform(), fontsize=7.0, color=INK, ha="right", va="center",
               fontweight="bold")
        a.text(-0.03, i - 0.22, sub, transform=a.get_yaxis_transform(), fontsize=5.3, color=MUTED, ha="right", va="center")
    a.set_yticks([])
    a.set_xscale("log"); a.set_xlim(1e-7, 1e7); a.set_ylim(-0.6, len(rows) - 0.4)
    for v, t in [(1, "1 s"), (60, "1 min"), (3600, "1 h"), (86400, "1 day")]:
        a.axvline(v, color=GRID, lw=0.8, zorder=0)
        a.text(v, len(rows) - 0.45, t, fontsize=5.8, color=MUTED, ha="center", va="bottom")
    a.set_xticks([1e-6, 1e-4, 1e-2, 1, 1e2, 1e4, 1e6])
    a.grid(axis="y", color="none")
    a.set_xlabel("time for one evaluation of the ring coupler, one core (s)", fontsize=7.5)
    a.annotate("", xy=(-0.4, len(rows) - 0.7), xytext=(-0.4, -0.3), xycoords=("axes fraction", "data"),
               arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7, mutation_scale=6), annotation_clip=False)
    a.text(-0.43, (len(rows) - 1) / 2, "fewer assumptions", transform=a.get_yaxis_transform(), rotation=90, fontsize=6.2,
           ha="center", va="center", color=INK)
    fig.text(0.005, 0.985, "a", fontweight="bold", color=INK, fontsize=9.5, ha="left", va="top")
    # (b) design tasks
    b = fig.add_axes([0.765, 0.17, 0.175, 0.74])
    n_grid = len(SIMS["grid"]) + len(SIMS["channels"])
    tasks = ["one" + NL + "design", "20-gap" + NL + "sweep", "1000-die" + NL + "Monte" + NL + "Carlo"]
    meth = [("mode solver + CMT", C1, [C["t_mode"], 20 * C["t_mode"], n_grid * C["t_mode"] + 1000 * C["t_formula"]]),
            ("EME", C3, [C["t_eme"], 20 * C["t_eme"], 1000 * C["t_eme"]]),
            ("3D FDTD", C4, [C["t3"], 20 * C["t3"], 1000 * C["t3"]])]
    w = 0.26
    for j, (n, col, ts) in enumerate(meth):
        for i, t in enumerate(ts):
            b.bar(i + (j - 1) * w, t, w * 0.92, color=col, alpha=0.85, label=n if i == 0 else None, zorder=3)
    b.set_yscale("log"); b.set_ylim(1, 1e11)
    for v, t in ((60, "1 min"), (3600, "1 h"), (86400, "1 day"), (3.156e7, "1 year")):
        b.axhline(v, color=GRID, lw=0.8, zorder=0)
        b.text(2.55, v, t, fontsize=5.6, color=MUTED, ha="left", va="center", clip_on=False)
    b.set_xticks(range(3)); b.set_xticklabels(tasks, fontsize=5.8)
    b.set_xlim(-0.5, 2.5)
    b.set_ylabel("time, one core (s)", fontsize=7)
    b.grid(axis="x", color="none"); b.grid(axis="y", color="none")
    b.legend(fontsize=5.4, loc="upper left", handlelength=0.9, borderaxespad=0.1)
    fig.text(0.70, 0.985, "b", fontweight="bold", color=INK, fontsize=9.5, ha="left", va="top")
    save(fig, "ch29_costmap")


# ------------------------------------------------------------------ Figure 29.4
def fig_convergence():
    rows = SIMS["convergence"]
    h = np.array([r["res"] for r in rows]) * 1000
    L = np.array([r["Lx"] for r in rows])
    s = np.array([r["dlnLx_dbias"] for r in rows]) * 100
    # Richardson-style fit L(h) = L_inf - C h^p on the five finest meshes
    best = None
    for p in np.linspace(0.5, 4, 351):
        A = np.c_[np.ones(5), h[-5:] ** p]
        coef, res, *_ = np.linalg.lstsq(A, L[-5:], rcond=None)
        r = np.sum((A @ coef - L[-5:]) ** 2)
        if best is None or r < best[0]:
            best = (r, p, coef)
    _, p, coef = best
    Linf = coef[0]
    nodes = {round(r["res"] * 1000): r["nodes"] for r in rows}
    fig = plt.figure(figsize=(6.3, 2.5))
    a = fig.add_axes([0.085, 0.19, 0.38, 0.7])
    hh = np.linspace(8, 50, 200)
    a.plot(hh, coef[0] + coef[1] * hh ** p, color=C1, lw=0.9, ls="--", alpha=0.7)
    a.plot(h, L, "o", color=C1, ms=4, zorder=5)
    a.axhline(Linf, color=MUTED, lw=0.7, ls=":")
    a.axhspan(Linf * 0.999, Linf * 1.001, color=C3, alpha=0.12, lw=0)
    a.text(83, Linf * 1.0013, "extrapolated value ± 0.1 %", fontsize=6, color=C3, ha="left", va="bottom")
    for k, dx, dy in ((80, -3, 0.07), (25, 6, -0.06), (10, 3, -0.07)):
        i = list(np.round(h)).index(k)
        a.annotate(f"{nodes[k]} nodes", xy=(h[i], L[i]), xytext=(h[i] + dx, L[i] + dy), fontsize=5.8, color=MUTED,
                   ha="left", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
    a.set_xlim(85, 5); a.set_ylim(37.45, 37.97)
    finish(a, "mesh size at the cores (nm)", "cross-over length L$_x$ (µm)")
    tag(a, "a")
    b = fig.add_axes([0.6, 0.19, 0.38, 0.7])
    sm, ss = s[-4:].mean(), s[-4:].std()
    b.axhspan(sm - ss, sm + ss, color=C2, alpha=0.15, lw=0)
    b.plot(h, s, "o-", color=C2, ms=4, lw=0.9)
    b.text(83, -0.0535, f"finest four: {sm:.3f} ± {ss:.3f} %/nm".replace("-", "−"), fontsize=6, color=C2, ha="left", va="center")
    b.set_xlim(85, 5); b.set_ylim(-0.08, -0.05)
    finish(b, "mesh size at the cores (nm)", "d ln L$_x$ / d(width bias) (%/nm)")
    tag(b, "b")
    save(fig, "ch29_convergence")
    return dict(p=p, Linf=Linf, s_mean=sm, s_sd=ss)


# ------------------------------------------------------------------ Monte Carlo model: wafer and coupler
NWAF = 177                       # wafers of 113 dies: 20 001 dies


def wafer(nwaf, rng):
    """The 113 dies of Figure 37.6's 200 mm wafer (15 mm pitch), on nwaf wafers, with the variations of Worked
    Example 35.1: thickness and width bowls of 6 nm from centre to edge, small tilts, and a random die-to-die width
    of sigma 1.5 nm (fresh on every wafer)."""
    R, P = 100.0, 15.0
    g = np.arange(-R, R + 0.1, P) + P / 2
    X, Y = np.meshgrid(g, g); X, Y = X.ravel(), Y.ravel()
    keep = np.hypot(np.abs(X) + P / 2, np.abs(Y) + P / 2) <= R
    X, Y = np.tile(X[keep], nwaf), np.tile(Y[keep], nwaf); rho = np.hypot(X, Y) / R
    dt = -3.0 + 6.0 * rho ** 2 + 0.6 * X / R
    dw = -3.0 + 6.0 * rho ** 2 + 0.6 * Y / R + 1.5 * rng.standard_normal(X.size)
    return dw, dt


def lnlx_model():
    """Quadratic fit of ln L_x (femwell grid) in the width bias b and thickness error t (nm); channel offsets."""
    g = SIMS["grid"]
    b = np.array([r["bias"] for r in g]); t = np.array([r["dt"] for r in g]); y = np.log([r["Lx"] for r in g])
    A = np.c_[np.ones_like(b), b, t, b ** 2, t ** 2, b * t]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    rms = np.sqrt(np.mean((A @ coef - y) ** 2))
    ch = SIMS["channels"]
    lam = np.array([r["lam"] for r in ch]) * 1000
    off = np.log([r["Lx"] for r in ch]) - coef[0]
    f = lambda b_, t_: coef[0] + coef[1] * b_ + coef[2] * t_ + coef[3] * b_ ** 2 + coef[4] * t_ ** 2 + coef[5] * b_ * t_
    return f, off, lam, rms


def coupler_mc(nwaf=NWAF, seed=29, k2_design=None, sig_gap=0.0):
    """Per die: the couplers of all four demultiplexer rings (one coupling length, centred on the mean channel)."""
    rng = np.random.default_rng(seed)
    dw, dt = wafer(nwaf, rng)
    f, off, lam, rms = lnlx_model()
    lo, c, hi = window()
    k2d = c if k2_design is None else k2_design
    lx_mid = np.exp(f(0, 0) + off.mean())
    lc = lc_for(k2d, lx_mid)
    dg = SIMS["sens"]["dlnLx_dgap"]
    n = dw.size
    k2 = np.empty((n, 4))
    for j in range(4):
        e_gap = sig_gap * rng.standard_normal(n)
        k2[:, j] = k2_of(lc, np.exp(f(dw, dt) + off[j] + dg * e_gap))
    ok = np.all((k2 >= lo) & (k2 <= hi), axis=1)
    return k2, ok, dict(lc=lc, lx_mid=lx_mid, rms=rms)


def ring_mc(nwaf=NWAF, seed=29):
    rng = np.random.default_rng(seed)
    dw, dt = wafer(nwaf, rng)
    return SW * dw + ST * dt, dw, dt


def tuning_yield(e, H, strategy):
    """Fraction of dies whose rings can be held on a channel from 20 to 70 C with heater range H (nm).
    e: fabrication shift of the resonance (nm, red positive). The design offset is chosen for the best yield."""
    drift = DTDT * T_RANGE
    if strategy == "hop":
        ok = H >= SPACING - 1e-12
        return float(ok), SPACING / 2
    if H < drift: return 0.0, np.nan
    # own channel: the ring's resonances repeat every FSR (four channels), so any order may serve its channel;
    # nearest channel fixed at start-up: any channel will do, so the pattern repeats every channel spacing
    period = FSR if strategy == "own" else SPACING
    best = None
    for d0 in np.linspace(0, period, int(round(period / 0.025)) + 1)[:-1]:   # design offset, 25 pm steps
        d = (d0 - e - drift) % period + drift     # smallest blue distance >= drift from a usable resonance
        ok = d <= H + 1e-12
        if best is None or ok.mean() > best[0]:
            best = (ok.mean(), mean_heater(d[ok], 0.0), d0)
    return best[0], best[1]


def own_windows(e, H):
    """Best design offset for own-channel locking and the bands of fabrication shift it covers (one per order)."""
    drift = DTDT * T_RANGE
    best = None
    for d0 in np.linspace(0, FSR, 513)[:-1]:
        ok = ((d0 - e - drift) % FSR + drift) <= H + 1e-12
        if best is None or ok.mean() > best[0]:
            best = (ok.mean(), d0)
    y, d0 = best
    # covered: d0 - e - drift - k FSR in [0, H - drift]  ->  e in [d0 - H - k FSR, d0 - drift - k FSR]
    return y, [(d0 - H - k * FSR, d0 - drift - k * FSR) for k in (-1, 0, 1)]


def mean_heater(d, _):
    """Mean heater shift (nm) over dies and a temperature spread uniformly from 20 to 70 C: d minus the mean drift."""
    if d.size == 0: return np.nan
    return d.mean() - DTDT * T_RANGE / 2


# ------------------------------------------------------------------ Figure 29.5
def fig_sensitivity():
    S = SIMS["sens"]
    lo, c, hi = window()
    f, off, lam, rms = lnlx_model()
    lx_mid = np.exp(f(0, 0) + off.mean())
    lc = lc_for(c, lx_mid)
    k0 = k2_of(lc, lx_mid)
    rel = lambda dln: (k2_of(lc, lx_mid * np.exp(dln)) / k0 - 1) * 100
    items = [("width alone, ±7.5 nm" + NL + "(gap held)", S["dlnLx_dw"] * 7.5),
             ("gap alone, ±5 nm" + NL + "(what if)", S["dlnLx_dgap"] * 5),
             ("thickness, ±3 nm", S["dlnLx_dt"] * 3),
             ("channel, 1546 to 1556 nm", None),
             ("width bias, ±7.5 nm" + NL + "(gap narrows as width grows)", None)]
    fig = plt.figure(figsize=(6.3, 2.6))
    a = fig.add_axes([0.245, 0.18, 0.33, 0.72])
    for i, (n, d) in enumerate(items):
        if n.startswith("channel"):
            v_lo, v_hi = rel(off[0] - off.mean()), rel(off[-1] - off.mean())
        elif n.startswith("width bias"):
            v_lo, v_hi = (k2_of(lc, np.exp(f(-7.5, 0) + off.mean())) / k0 - 1) * 100, (k2_of(lc, np.exp(f(7.5, 0) + off.mean())) / k0 - 1) * 100
        else:
            v_lo, v_hi = rel(-d), rel(d)
        y = len(items) - 1 - i
        a.barh(y, v_hi, 0.55, color=C4, alpha=0.8, zorder=3)
        a.barh(y, v_lo, 0.55, color=C1, alpha=0.8, zorder=3)
        a.text(-27, y, n, fontsize=6.0, ha="right", va="center", color=INK)
    a.axvline(0, color=INK, lw=0.7)
    for v in ((lo / c - 1) * 100, (hi / c - 1) * 100):
        a.axvline(v, color=RED, lw=0.9, ls="--")
    a.text((hi / c - 1) * 100 - 0.8, -0.45, "window", fontsize=6, color=RED, ha="right")
    a.set_xlim(-25, 25); a.set_yticks([]); a.set_ylim(-0.6, 4.6)
    a.grid(axis="y", color="none")
    finish(a, "change of κ² (%)")
    from matplotlib.patches import Patch
    a.legend(handles=[Patch(fc=C1, alpha=0.8, label="variable at its low end"), Patch(fc=C4, alpha=0.8, label="at its high end")],
             fontsize=5.6, loc="lower center", bbox_to_anchor=(0.5, 0.99), ncol=2, handlelength=1.0, borderaxespad=0.0)
    tag(a, "a")
    b = fig.add_axes([0.665, 0.18, 0.32, 0.72])
    T = SIMS["tolerant"]
    W = np.array([r["w"] for r in T]) * 1000
    for k, col, n in (("dW", C1, "width alone"), ("dgap", C2, "gap alone"), ("dbias", C4, "width bias")):
        v = np.array([r[k] for r in T]) * 100
        b.plot(W, v, "o-", color=col, ms=3, lw=1.1, label=n)
    v = np.array([r["dbias"] for r in T]) * 100
    i = np.where(np.diff(np.sign(v)))[0][0]
    w0 = W[i] + (W[i + 1] - W[i]) * v[i] / (v[i] - v[i + 1])
    b.axhline(0, color=INK, lw=0.6)
    b.plot([w0], [0], "o", ms=5, mfc="white", mec=C4, mew=1.2, zorder=6)
    b.annotate(f"bias-tolerant\nat {w0:.0f} nm", xy=(w0, 0), xytext=(w0 + 30, 0.42), fontsize=6, color=C4,
               arrowprops=dict(arrowstyle="-", color=C4, lw=0.5))
    b.set_xlim(330, 670); b.set_ylim(-0.5, 1.4)
    finish(b, "strip width (nm), 200 nm gap", "d ln L$_x$ / d(error) (%/nm)")
    b.legend(fontsize=6, loc="upper right")
    tag(b, "b")
    save(fig, "ch29_sensitivity")
    return dict(w0=w0)


# ------------------------------------------------------------------ Figure 29.6
def fig_montecarlo():
    lo, c, hi = window()
    k2c, okc, infoc = coupler_mc()
    k2b, okb, infob = coupler_mc(k2_design=0.145)
    e, dw, dt = ring_mc()
    fig = plt.figure(figsize=(6.3, 2.5))
    a = fig.add_axes([0.08, 0.19, 0.4, 0.7])
    bins = np.linspace(8, 16, 81)
    hc = a.hist(k2c.ravel() * 100, bins=bins, color=C1, alpha=0.75)[0]
    hb = a.hist(k2b.ravel() * 100, bins=bins, color=C2, alpha=0.75)[0]
    for v in (lo, hi):
        a.axvline(v * 100, color=RED, lw=1.0, ls="--")
    ymax = max(hc.max(), hb.max())
    a.set_ylim(0, ymax * 1.5)
    a.text(lo * 100 - 0.12, ymax * 1.42, "passband" + NL + "≥ 0.4 nm", fontsize=5.8, color=RED, ha="right", va="top")
    a.text(hi * 100 + 0.12, ymax * 1.42, "crosstalk" + NL + "≤ −20 dB", fontsize=5.8, color=RED, ha="left", va="top")
    a.text(np.median(k2c) * 100, hc.max() * 1.04, "centred:" + NL + f"{okc.mean()*100:.0f} % of dies pass", fontsize=5.9,
           color=C1, ha="center", va="bottom")
    a.text(np.median(k2b) * 100 + 0.35, hb.max() * 1.04, "designed for 14.5 %:" + NL + f"{okb.mean()*100:.0f} % pass", fontsize=5.9,
           color="#9A6A12", ha="center", va="bottom")
    a.set_yticks([])
    finish(a, "coupling κ² of each ring coupler (%)", "rings")
    tag(a, "a")
    b = fig.add_axes([0.58, 0.19, 0.4, 0.7])
    H = 3.75 + 9.0
    y, bands = own_windows(e, H)
    bins = np.linspace(-9, 9, 73)
    b.hist(e, bins=bins, color=C1, alpha=0.75)
    for k_, (e_lo, e_hi) in enumerate(bands):
        lo_, hi_ = max(e_lo, -9), min(e_hi, 9)
        if hi_ <= lo_: continue
        b.axvspan(lo_, hi_, color=C3, alpha=0.14 if k_ == 1 else 0.07, lw=0)
        for v in (e_lo, e_hi):
            if -9 < v < 9: b.axvline(v, color=RED, lw=1.0, ls="--" if k_ == 1 else ":")
    e_lo, e_hi = bands[1]
    ymax = b.get_ylim()[1]; b.set_ylim(0, ymax * 1.3)
    b.text((e_lo + e_hi) / 2, ymax * 1.24, f"tunable with a {H:.2f} nm heater range:" + NL + f"{y*100:.1f} % of dies", fontsize=6,
           color=C3, ha="center", va="top")
    b.set_yticks([])
    finish(b, "fabrication shift of the ring resonance (nm)", "dies")
    tag(b, "b")
    save(fig, "ch29_montecarlo")
    return dict(yc=okc.mean(), yb=okb.mean(), k2c=(k2c.min(), k2c.max()), k2b=(k2b.min(), k2b.max()), lc=infoc["lc"],
                rms=infoc["rms"], H=H, yH=y, e_sd=e.std(), e_lo=e_lo, e_hi=e_hi)


# ------------------------------------------------------------------ Figure 29.7
def fig_tuning():
    e, dw, dt = ring_mc()
    Hs = np.linspace(2.5, 20, 176)
    fig = plt.figure(figsize=(6.3, 2.5))
    a = fig.add_axes([0.08, 0.19, 0.4, 0.7])
    res = {}
    for st, col, n in (("own", C1, "own channel"), ("fixed", C2, "nearest channel, fixed at start-up"),
                       ("hop", C3, "nearest channel, re-locked as it warms")):
        ys = np.array([tuning_yield(e, H, st)[0] for H in Hs]) * 100
        a.plot(Hs, ys, color=col, lw=1.4, label=n)
        res[st] = (Hs, ys)
    a.set_xlim(2.5, 20); a.set_ylim(-2, 104)
    a.axhline(99, color=MUTED, lw=0.6, ls=":")
    sec = a.secondary_xaxis("top", functions=(lambda x: x / ETA, lambda p: p * ETA))
    sec.set_xlabel("heater power at 0.26 nm/mW (mW)", fontsize=7); sec.tick_params(labelsize=6.5)
    finish(a, "heater tuning range (nm)", "dies on channel, 20–70 °C (%)")
    a.legend(fontsize=5.8, loc="lower right")
    fig.text(0.005, 0.985, "a", fontweight="bold", color=INK, fontsize=9.5, ha="left", va="top")
    # (b) heater range for 99 % and mean heater power
    b = fig.add_axes([0.6, 0.19, 0.38, 0.7])
    need, meanp = [], []
    for st in ("own", "fixed", "hop"):
        Hs_, ys = res[st]
        H99 = Hs_[np.argmax(ys >= 99.0)]
        H99 = refine_h99(e, st, H99)
        need.append(H99)
        meanp.append(tuning_yield(e, H99, st)[1])
    x = np.arange(3)
    b.bar(x - 0.2, np.array(need) / ETA, 0.38, color=C1, alpha=0.85, label="maximum (sets the driver)")
    b.bar(x + 0.2, np.array(meanp) / ETA, 0.38, color=C2, alpha=0.85, label="mean (sets the energy)")
    for i in range(3):
        b.text(x[i] - 0.2, need[i] / ETA + 1, f"{need[i]/ETA:.0f}", ha="center", fontsize=6.2, color=C1)
        b.text(x[i] + 0.2, meanp[i] / ETA + 1, f"{meanp[i]/ETA:.0f}", ha="center", fontsize=6.2, color=C2)
    b.set_xticks(x); b.set_xticklabels(["own\nchannel", "nearest,\nfixed", "nearest,\nre-locked"], fontsize=6.5)
    b.grid(axis="x", color="none")
    finish(b, None, "heater power per ring, 99 % of dies (mW)")
    b.legend(fontsize=5.8, loc="upper right")
    tag(b, "b")
    save(fig, "ch29_tuning")
    return dict(need=need, meanp=meanp)


def refine_h99(e, st, H):
    lo_, hi_ = H - 0.2, H
    for _ in range(40):
        m = 0.5 * (lo_ + hi_)
        if tuning_yield(e, m, st)[0] >= 0.99: hi_ = m
        else: lo_ = m
    return hi_


# ------------------------------------------------------------------ Figure 29.8
def fig_loop():
    st = {round(r["w"] * 1000): r for r in SIMS["strip"]}
    a1, b1 = st[500]["shift_W"], st[500]["shift_t"]
    a2, b2 = st[1000]["shift_W"], st[1000]["shift_t"]
    M = np.array([[a1, b1], [a2, b2]])
    true = np.array([-4.0, 3.0])                      # illustrative: 4 nm narrower, 3 nm thicker
    meas = M @ true
    sig = 0.05                                        # nm, resonance-position uncertainty per ring (illustrative)
    Minv = np.linalg.inv(M)
    cov = Minv @ (sig ** 2 * np.eye(2)) @ Minv.T
    sdW, sdt = np.sqrt(np.diag(cov))
    fig = plt.figure(figsize=(6.3, 2.6))
    a = fig.add_axes([0.08, 0.18, 0.4, 0.72])
    Ws = np.linspace(-8, 2, 50)
    for (aa, bb, m, col, n) in ((a1, b1, meas[0], C1, "500 nm ring"), (a2, b2, meas[1], C2, "1 µm ring")):
        for s_ in (-1, 1):
            a.plot(Ws, (m + s_ * 3 * sig - aa * Ws) / bb, color=col, lw=0.5, ls=":")
        a.plot(Ws, (m - aa * Ws) / bb, color=col, lw=1.3, label=f"{n}: {m:+.2f} nm")
    # 3-sigma ellipse
    vals, vecs = np.linalg.eigh(cov)
    th = np.linspace(0, 2 * np.pi, 200)
    ell = (vecs @ (3 * np.sqrt(vals)[:, None] * np.vstack([np.cos(th), np.sin(th)]))).T + true
    a.fill(ell[:, 0], ell[:, 1], fc=C4, alpha=0.35, ec=C4, lw=0.8, zorder=6)
    a.plot(*true, "o", color=INK, ms=1.5, zorder=7)
    txt = (f"ΔW = {true[0]:+.0f} ± {3*sdW:.1f} nm" + NL + f"Δt = {true[1]:+.0f} ± {3*sdt:.2f} nm (3σ)").replace("-", "−")
    a.annotate(txt, xy=true, xytext=(-7.6, 0.6),
               fontsize=6, color=C4, arrowprops=dict(arrowstyle="-", color=C4, lw=0.5))
    a.set_xlim(-8, 2); a.set_ylim(0, 6)
    finish(a, "width error ΔW (nm)", "thickness error Δt (nm)")
    a.legend(fontsize=5.8, loc="upper right", title="measured shift", title_fontsize=5.8)
    tag(a, "a")
    b = fig.add_axes([0.6, 0.18, 0.38, 0.72])
    W = np.array([r["w"] for r in SIMS["strip"]]) * 1000
    b.bar([0, 1], [a1, a2], 0.35, color=C1, alpha=0.85, label="per nm of width", zorder=3)
    b.bar([0.38, 1.38], [b1, b2], 0.35, color=C2, alpha=0.85, label="per nm of thickness", zorder=3)
    for x_, v in ((0, a1), (1, a2), (0.38, b1), (1.38, b2)):
        b.text(x_, v + 0.03, f"{v:.2f}", ha="center", fontsize=6.2)
    b.set_xticks([0.19, 1.19]); b.set_xticklabels(["500 nm strip", "1 µm strip"], fontsize=7)
    b.set_ylim(0, 1.75); b.grid(axis="x", color="none")
    finish(b, None, "ring resonance shift (nm per nm)")
    b.legend(fontsize=6, loc="upper right")
    tag(b, "b")
    save(fig, "ch29_loop")
    return dict(M=M, meas=meas, sdW=sdW, sdt=sdt, det=np.linalg.det(M))


# ------------------------------------------------------------------ every number the chapter quotes
def fig_numbers():
    lo, c, hi = window()
    print(f"[29.1] ring L {L_RING:.2f} um, R {L_RING/2/np.pi:.3f} um, a {A_RT:.5f}")
    print(f"[29.1] Ch 14 design k2 14.5 %: crosstalk {crosstalk_db(0.145):.2f} dB, FWHM {fwhm_nm(0.145):.3f} nm")
    print(f"[29.1] window k2 {lo*100:.2f}-{hi*100:.2f} %, centre {c*100:.2f} % (x/÷ {hi/c:.3f}); at centre: crosstalk "
          f"{crosstalk_db(c):.2f} dB, FWHM {fwhm_nm(c):.3f} nm, Q_L {LAM/fwhm_nm(c):.0f}, drop loss {drop_loss_db(c):.3f} dB")
    th = np.arcsin(np.sqrt(c)); g = -2 * th / np.tan(th)
    print(f"[29.1] L_x {LX0:.3f} um -> L_c {lc_for(c):.2f} um effective, straight {lc_for(c)-BL:.2f} um; dlnk2/dlnLx {g:.3f}")
    S = SIMS["sens"]
    for k in ("w", "gap", "t", "lam", "bias"):
        d = S["dlnLx_d" + k]
        print(f"[29.4] dlnLx/d{k} {d*100:+.3f} %/nm -> dlnk2 {g*d*100:+.3f} %/nm; window alone allows ±{np.log(hi/c)/abs(g*d):.1f} nm")
    C = costs()
    print(f"[29.3] coupler device {C['L_dev']:.1f} x {C['W_dev']:.1f} um (straight {C['ls']:.2f} um); FDTD domain "
          f"{C['X']:.1f} x {C['Y']:.1f} x {C['Z']:.2f} um; {C['nx']:.0f} x {C['ny']:.0f} x {C['nz']:.0f} = {C['cells3']:.3g} cells; "
          f"dt {C['dt']*1e15:.4f} fs; T {C['T']*1e12:.2f} ps; steps {C['steps']:.3g}; work {C['cells3']*C['steps']:.3g} cell-steps; "
          f"memory {C['mem3']/1e9:.1f} GB; time one core {C['t3']/3600:.0f} h = {C['t3']/86400:.1f} days; 12 cores (ideal) {C['t3']/12/3600:.1f} h")
    print(f"[29.3] 2.5D: {C['cells2']:.3g} cells, {C['t2']/60:.1f} min; EME {C['n_sec']} sections x {C['eme12']:.1f} s = {C['t_eme']/60:.1f} min "
          f"(4 modes {C['eme4']:.1f} s); mode solve {C['t_mode']:.1f} s; compact model {C['t_cm']*1e6:.0f} us; formula {C['t_formula']*1e9:.0f} ns")
    for b in SIMS["bench"]:
        print(f"[29.3] MEEP bench {b['dims']}D: {b['rate']:.3g} cell-steps/s, {b['bytes_per_cell']:.0f} B/cell, Courant {b['courant']}")
    n_grid = len(SIMS["grid"]) + len(SIMS["channels"])
    print(f"[29.3] MC 1000 dies: mode solver {n_grid} solves {n_grid*C['t_mode']/60:.1f} min; EME {1000*C['t_eme']/86400:.1f} days; "
          f"3D FDTD {1000*C['t3']/3.156e7:.1f} years on one core")
    cv = fig_convergence()
    print(f"[29.4] convergence: L_inf {cv['Linf']:.3f} um, order p {cv['p']:.2f}; bias sensitivity finest four {cv['s_mean']:.4f} ± {cv['s_sd']:.4f} %/nm")
    for r in SIMS["convergence"]:
        print(f"    res {r['res']*1000:.0f} nm L_x {r['Lx']:.3f} ({(r['Lx']/cv['Linf']-1)*100:+.2f} %) bias {r['dlnLx_dbias']*100:+.4f}")
    for r in SIMS["domain"]:
        print(f"    window {2*r['hw']:.0f} x {2*r['hh']:.0f}: L_x {r['Lx']:.3f}")
    se = fig_sensitivity()
    print(f"[29.4] bias-tolerant width {se['w0']:.1f} nm")
    f, off, lam, rms = lnlx_model()
    print(f"[29.5] ln L_x model rms {rms:.2e}; channel offsets {np.round(off*100, 2)} %")
    mc = fig_montecarlo()
    print(f"[29.5] coupler MC: centred L_c {mc['lc']:.2f} um, yield {mc['yc']*100:.2f} %, k2 range {mc['k2c'][0]*100:.2f}-{mc['k2c'][1]*100:.2f} %; "
          f"14.5 % design yield {mc['yb']*100:.2f} %, range {mc['k2b'][0]*100:.2f}-{mc['k2b'][1]*100:.2f} %")
    for sg in (2.0, 3.0, 4.0, 5.0):
        k2, ok, _ = coupler_mc(sig_gap=sg)
        print(f"    with an independent gap error sigma {sg} nm: yield {ok.mean()*100:.1f} %")
    e, dw, dt = ring_mc()
    print(f"[29.5] ring MC: e sd {e.std():.2f} nm, 0.5-99.5 % span {np.percentile(e, 99.5)-np.percentile(e, 0.5):.2f} nm, "
          f"min {e.min():.2f} max {e.max():.2f}; sd(dw) {dw.std():.2f}, sd(dt) {dt.std():.2f}, corr {np.corrcoef(dw, dt)[0,1]:.2f}")
    sw, st_ = dw.std(), dt.std()
    print(f"[29.5] corners 3 sigma stacked: {3*(SW*sw + ST*st_):.2f} nm; independent RSS 3 sigma: {3*np.hypot(SW*sw, ST*st_):.2f} nm; "
          f"actual 3 sd {3*e.std():.2f} nm")
    print(f"[29.5] histogram panel: H {mc['H']:.2f} nm, own-channel yield {mc['yH']*100:.1f} %, window e {mc['e_lo']:.2f} to {mc['e_hi']:.2f}")
    tu = fig_tuning()
    for st, H, P in zip(("own", "fixed", "hop"), tu["need"], tu["meanp"]):
        print(f"[29.5] tuning {st}: 99 % needs {H:.2f} nm = {H/ETA:.1f} mW; mean heater {P:.2f} nm = {P/ETA:.1f} mW; 8 rings at 200 Gb/s "
              f"{8*P/ETA*1e-3/200e9*1e12:.2f} pJ/bit (max {8*H/ETA*1e-3/200e9*1e12:.2f})")
    for H in (5.4, 6.95):
        print(f"    H {H} nm: own {tuning_yield(e, H, 'own')[0]*100:.1f} %, fixed {tuning_yield(e, H, 'fixed')[0]*100:.1f} %, hop {tuning_yield(e, H, 'hop')[0]*100:.0f} %")
    lp = fig_loop()
    print(f"[29.8] loop: M {np.round(lp['M'], 3).tolist()}, det {lp['det']:.3f}, measured {np.round(lp['meas'], 3)}, 1 sigma W {lp['sdW']:.3f} t {lp['sdt']:.3f} nm")
    for r in SIMS["strip"]:
        print(f"    strip {r['w']*1000:.0f}: n_eff {r['neff']:.4f} n_g {r['ng']:.3f} dn/dW {r['dn_dW']:.3e} dn/dt {r['dn_dt']:.3e} shifts {r['shift_W']:.3f} {r['shift_t']:.3f}")
    # exponential compact model of L_x(gap) from the Chapter 9 femwell points, fitted on 150-300 nm
    d9 = json.load(open(os.path.join(HERE, "ch09_supermodes.json")))
    g9, L9 = np.array(d9["gap"][:6]), np.array(d9["Lx"][:6])
    m = (g9 > 0.149) & (g9 < 0.301)
    cf = np.polyfit(g9[m], np.log(L9[m]), 1)
    err = (np.exp(np.polyval(cf, g9)) / L9 - 1) * 100
    print(f"[29.7] L_x(gap) exponential fit 150-300 nm: errors {dict(zip(np.round(g9*1000).astype(int).tolist(), np.round(err, 2).tolist()))} %")


if __name__ == "__main__":
    which = sys.argv[1:] or ["workflow", "flowdown", "costmap", "numbers"]
    for k in which:
        globals()["fig_" + k]()
