"""Figures of Chapter 32 (simulation tools in practice).

    python -I -X utf8 figsrc/ch32_figs.py

ch32_lumerical   the Ansys Lumerical products, the solvers in each and the data passed between them (diagram)
ch32_tidy3d      the Tidy3D workflow: Python on your computer, runs on the vendor's servers (diagram)
ch32_modeconv    convergence of the strip's n_eff in three mode solvers   (data: ch32_tidy3d.json, ch32_femwell.json, ch32_meep_modes.json)
ch32_loop        the set-up, run and check loop that applies to any tool (diagram)
ch32_fit         checking a material fit: silicon (Li 1980) with one and two poles    (data: ch32_tidy3d.json)
ch32_region      the worked example's simulation region to scale, with its grid       (data: ch32_tidy3d.json)
ch32_bendconv    3D MEEP bend: transmission, reflection and cost against resolution  (data: ch32_meep_bend.json)
ch32_cost        cells, time steps and memory of the same bend in three set-ups      (data: both, plus the estimate below)

The JSON files come from figsrc/ch32_tidy3d.py (Tidy3D 2.12.2, local) and figsrc/ch32_meep_bend.py (MEEP 1.35.1),
both run in the photonics-labs Docker container. The Lumerical cell count is this script's own estimate (lumerical_grid).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
savefig = save          # plots and drawings alike: SVG, plus a PNG preview when FIGPREVIEW is set

HERE = os.path.dirname(os.path.abspath(__file__))
T3D = json.load(open(os.path.join(HERE, "ch32_tidy3d.json"))) if os.path.exists(os.path.join(HERE, "ch32_tidy3d.json")) else None
MEEP = json.load(open(os.path.join(HERE, "ch32_meep_bend.json"))) if os.path.exists(os.path.join(HERE, "ch32_meep_bend.json")) else None

PROD_FC, DATA_FC, AUTO_FC, CLOUD_FC = "#EEF3FA", "#FBF3E6", "#EEF6F1", "#F3EEF9"
MONO = {"family": "monospace"}

# the worked example (Section 32.6): a 2 um-radius 90-degree bend of a 500 x 220 nm strip
R, W, T = 2.0, 0.5, 0.22
DOM = dict(x=(-1.5, 3.25), y=(-3.25, 1.5), z=(-1.0, 1.0))   # region inside the absorbing layers (um)
N_SI, N_OX = 3.476, 1.444
LAM0, LAM_MIN = 1.55, 1.50
C0 = 299792458.0
T_RUN = 250e-15                                              # physical time simulated in every set-up (s)


# ------------------------------------------------------------------ Figure 32.1
def fig_lumerical():
    fig, ax = geom_axes(figsize=(6.3, 3.85), xlim=(0, 10.4), ylim=(0, 6.35), equal=False)

    def prod(x, y, w, h, name, items, fc=PROD_FC, dy=0.43):
        block(ax, x, y, w, h, fc=fc, lw=0.8, r=0.08)
        label(ax, x, y + h / 2 - 0.2, name, fs=7.4, bold=True)
        for k, (s, sub) in enumerate(items):
            yy = y + h / 2 - 0.55 - k * dy
            label(ax, x - w / 2 + 0.14, yy, s, fs=6.6, ha="left", bold=True, col=BLUE)
            label(ax, x - w / 2 + 0.14, yy - 0.18, sub, fs=5.8, ha="left", col=MUTED)

    prod(1.85, 5.1, 2.9, 1.7, "MODE", [("FDE", "eigenmodes of a cross-section"), ("EME", "bidirectional eigenmode expansion"),
                                         ("varFDTD", "2.5D: slab modes + 2D FDTD")], dy=0.4)
    prod(1.85, 3.2, 2.9, 1.3, "FDTD", [("3D / 2D FDTD", "any geometry, broadband, in time"),
                                         ("RCWA, STACK", "periodic layers, thin films")], dy=0.4)
    prod(8.75, 4.25, 2.9, 3.4, "INTERCONNECT", [("circuit solver", "frequency and time domain"), ("S-parameter element", "imports any N-port data"),
                                                 ("compact models", "waveguides, couplers, lasers"), ("CML Compiler", "builds PDK model libraries")],
         dy=0.55)
    # Multiphysics: one wide box with its five solvers side by side
    block(ax, 3.55, 1.55, 6.8, 1.2, fc=PROD_FC, lw=0.8, r=0.08)
    label(ax, 3.55, 1.97, "Multiphysics", fs=7.4, bold=True)
    mp_items = [("CHARGE", "drift-diffusion:\ncarriers, current"), ("HEAT", "conduction,\nJoule heating"),
                ("FEEM", "finite-element\nmode solver"), ("DGTD", "finite-element\ntime domain"), ("MQW", "quantum-well\ngain, k·p")]
    for k, (s, sub) in enumerate(mp_items):
        xx = 0.45 + k * 1.33
        label(ax, xx, 1.62, s, fs=6.6, ha="left", bold=True, col=BLUE)
        label(ax, xx, 1.27, sub, fs=5.6, ha="left", col=MUTED)

    def flow(p0, p1, col=RED, rad=0.0):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=col, lw=0.9, mutation_scale=7,
                                                          shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"), zorder=6)
    flow((3.3, 5.45), (7.3, 5.1))
    label(ax, 5.3, 5.55, "FDE: n$_\\mathrm{eff}$, n$_g$, loss against λ → waveguide model", fs=5.9, col=RED, bg="white", z=7)
    flow((3.3, 4.95), (7.3, 4.45))
    label(ax, 5.3, 4.9, "EME: S-matrix of a taper, MMI, coupler", fs=5.9, col=RED, bg="white", z=7)
    flow((3.3, 3.2), (7.3, 3.4))
    label(ax, 5.3, 3.5, "FDTD: S-parameters from a port sweep", fs=5.9, col=RED, bg="white", z=7)
    label(ax, 5.3, 3.02, "→ N-port element in the circuit", fs=5.9, col=RED, bg="white", z=7)
    # imported carrier density and temperature: a bracket on the left feeding MODE and FDTD
    ax.plot([0.2, 0.2], [3.2, 5.1], color=TEAL, lw=0.9, zorder=6)
    for yy in (3.2, 5.1):
        arrow(ax, (0.2, yy), (0.4, yy), col=TEAL, lw=0.9, ms=6)
    arrow(ax, (0.2, 2.15), (0.2, 3.2), col=TEAL, lw=0.9, ms=0.1)
    label(ax, 0.32, 2.4, "carrier density, temperature → Δn, Δα", fs=5.8, col=TEAL, ha="left", bg="white", z=7)
    flow((6.6, 2.15), (7.95, 2.55), col=TEAL, rad=-0.2)
    label(ax, 6.85, 2.62, "gain → laser,\nSOA models", fs=5.7, col=TEAL, ha="right", bg="white", z=7)
    # automation band
    block(ax, 5.2, 0.42, 10.2, 0.62, fc=AUTO_FC, lw=0.7, r=0.06)
    label(ax, 5.2, 0.53, "automation: Lumerical script (.lsf) in every product · Python API (PyLumerical, lumapi) · sweeps and optimisation · lumopt (adjoint)",
          fs=6.1, col=INK)
    label(ax, 5.2, 0.27, "project files: .lms (MODE)   .fsp (FDTD)   .ldev (Multiphysics)   .icp (INTERCONNECT)", fs=5.8, col=MUTED)
    save(fig, "ch32_lumerical")


# ------------------------------------------------------------------ Figure 32.2
def fig_tidy3d():
    fig, ax = geom_axes(figsize=(6.3, 3.0), xlim=(0, 10.4), ylim=(0, 4.95), equal=False)
    ax.add_patch(FancyBboxPatch((0.45, 0.62), 4.15, 4.2, boxstyle="round,pad=0,rounding_size=0.1", fc="#F7F9FC", ec=GRID, lw=0.8))
    ax.add_patch(FancyBboxPatch((4.85, 0.62), 5.45, 4.2, boxstyle="round,pad=0,rounding_size=0.1", fc=CLOUD_FC, ec=GRID, lw=0.8))
    label(ax, 0.62, 4.6, "your computer: Python and the tidy3d package", fs=6.8, bold=True, ha="left")
    label(ax, 5.02, 4.6, "the vendor's servers (needs an account)", fs=6.8, bold=True, ha="left")

    def card(x, y, w, title, sub, fc):
        block(ax, x, y, w, 0.66, fc=fc, lw=0.8)
        label(ax, x, y + 0.13, title, fs=6.6, bold=True)
        label(ax, x, y - 0.15, sub, fs=5.5, col=MUTED)
    card(2.52, 3.9, 3.75, "build a td.Simulation", "structures, sources, monitors, grid_spec, boundary_spec, symmetry", PROD_FC)
    card(2.52, 2.95, 3.75, "validate and look", "checks run as each object is made; plot, num_cells, num_time_steps", PROD_FC)
    card(2.52, 2.0, 3.75, "local mode solver (optional)", "ModeSolver(...).solve() runs here: no account, no credits", "white")
    card(2.52, 1.05, 3.75, "post-process and plot", "results as labelled arrays (xarray)", PROD_FC)
    arrow(ax, (2.52, 3.56), (2.52, 3.29), lw=0.8, ms=6)
    card(6.1, 2.95, 2.1, "upload the task", "web.Job, web.run", "white")
    card(6.1, 2.0, 2.1, "estimate the cost", "upper bound: all time steps", "white")
    card(6.1, 1.05, 2.1, "run on GPU servers", "stops early at shutoff", "white")
    card(9.0, 1.05, 2.3, "results (HDF5 file)", "only the monitors' data", "white")
    card(9.0, 3.2, 2.3, "web GUI in a browser", "build, view and run", "white")
    arrow(ax, (4.41, 2.95), (5.04, 2.95), col=BLUE, lw=1.0, ms=7)
    arrow(ax, (6.1, 2.61), (6.1, 2.34), lw=0.8, ms=6)
    arrow(ax, (6.1, 1.66), (6.1, 1.39), lw=0.8, ms=6)
    arrow(ax, (7.16, 1.05), (7.84, 1.05), lw=0.8, ms=6)
    ax.plot([9.0, 9.0], [2.86, 1.39], color=MUTED, lw=0.7, ls=(0, (2, 2)))
    wire(ax, [(9.0, 0.71), (9.0, 0.3), (2.52, 0.3), (2.52, 0.71)], col=BLUE, lw=1.0)
    label(ax, 5.8, 0.42, "download", fs=5.9, col=BLUE, bg="white")
    # optimisation loop
    wire(ax, [(0.64, 1.05), (0.25, 1.05), (0.25, 3.9), (0.64, 3.9)], col=TEAL, lw=1.0)
    label(ax, 0.13, 2.47, "optimise: gradient from a forward and an adjoint run", fs=5.6, col=TEAL, rot=90)
    save(fig, "ch32_tidy3d")


# ------------------------------------------------------------------ Figure 32.4
def fig_loop():
    fig, ax = geom_axes(figsize=(6.3, 3.35), xlim=(0, 10.4), ylim=(0, 5.6), equal=False)
    setup = [("1 geometry", "from the GDS or\nparametric code"), ("2 materials", "dispersion fit,\nthen check it"),
             ("3 grid", "auto + refinement,\nsub-pixel averaging"), ("4 sources", "mode or beam,\nband, polarisation"),
             ("5 monitors", "mode, flux, field;\nnormalisation"), ("6 boundaries", "PML far enough,\nsymmetry planes")]
    xs = np.linspace(0.95, 9.45, 6)
    for k, (t, s_) in enumerate(setup):
        block(ax, xs[k], 4.3, 1.45, 0.55, t, fc=PROD_FC, fs=6.8, bold=True)
        label(ax, xs[k], 4.92, s_, fs=5.6, col=MUTED)
        if k < 5:
            arrow(ax, (xs[k] + 0.74, 4.3), (xs[k + 1] - 0.74, 4.3), lw=0.8, ms=6)
    label(ax, 0.22, 5.47, "set up", fs=6.8, col=BLUE, bold=True, ha="left")
    run = [("7 first run", "power adds up? fields\ndecayed? reflections?"), ("8 converge", "grid, region size,\nrun time, mode count"),
           ("9 sweep, optimise", "parameters, corners,\nadjoint design"), ("10 export", "S-parameters → circuit\n(INTERCONNECT, SAX)")]
    xr = [9.3, 7.15, 5.0, 2.85]
    for k, (t, s_) in enumerate(run):
        block(ax, xr[k], 2.55, 1.65, 0.55, t, fc=DATA_FC, fs=6.8, bold=True)
        label(ax, xr[k], 1.93, s_, fs=5.6, col=MUTED)
        if k < 3:
            arrow(ax, (xr[k] - 0.84, 2.55), (xr[k + 1] + 0.84, 2.55), lw=0.8, ms=6)
    arrow(ax, (9.45, 4.02), (9.45, 2.83), lw=0.8, ms=6)
    label(ax, 0.22, 3.15, "run and check", fs=6.8, col=BLUE, bold=True, ha="left")
    block(ax, 0.88, 2.55, 1.42, 0.55, "11 record", fc=AUTO_FC, fs=6.8, bold=True)
    arrow(ax, (xr[3] - 0.84, 2.55), (1.6, 2.55), lw=0.8, ms=6)
    label(ax, 0.88, 1.93, "script, versions,\nsettings, data", fs=5.6, col=MUTED)
    # failure loops
    for p0, p1 in (((7.15, 2.83), (4.35, 4.02)), ((9.0, 2.83), (6.25, 4.02))):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.9, ls=(0, (3, 2)),
                                                          mutation_scale=7, shrinkA=0, shrinkB=0, connectionstyle="arc3,rad=0.15"))
    label(ax, 8.0, 3.62, "a check fails:\nfix the set-up", fs=5.9, col=RED, bg="white", ha="left")
    # glue
    block(ax, 5.2, 0.58, 10.1, 0.78, fc=AUTO_FC, lw=0.7, r=0.06)
    ax.text(5.2, 0.76, "open glue: gdsfactory (layout as code) + gplugins → MEEP, Tidy3D, Lumerical, femwell, MPB, meow (EME) → SAX (circuits)",
            fontsize=6.0, color=INK, ha="center", va="center")
    ax.text(5.2, 0.41, "one component description, one layer stack, the same ports in every solver", fontsize=5.8, color=MUTED, ha="center", va="center")
    save(fig, "ch32_loop")


# ------------------------------------------------------------------ helpers for the data figures
FEM = json.load(open(os.path.join(HERE, "ch32_femwell.json"))) if os.path.exists(os.path.join(HERE, "ch32_femwell.json")) else None
MMODES = json.load(open(os.path.join(HERE, "ch32_meep_modes.json"))) if os.path.exists(os.path.join(HERE, "ch32_meep_modes.json")) else None


def n_si_li(l):
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / l**2 + 0.00810461 * l1**2 / (l**2 - l1**2))


def axis_cells(lo, hi, fine_spans, d_fine, d_coarse):
    """Cells along one axis of a rectilinear grid: steps of d_fine inside the spans that contain silicon, d_coarse
    elsewhere, with an abrupt change between them (a simplification of any tool's graded mesh)."""
    n, edges = 0, sorted(set([lo, hi] + [p for s_ in fine_spans for p in s_]))
    for a, b_ in zip(edges[:-1], edges[1:]):
        if b_ <= lo or a >= hi:
            continue
        a, b_ = max(a, lo), min(b_, hi)
        fine = any(s_[0] <= a + 1e-9 and b_ <= s_[1] + 1e-9 for s_ in fine_spans)
        n += int(np.ceil((b_ - a) / (d_fine if fine else d_coarse) - 1e-9))
    return n


def lumerical_grid(accuracy=2, d_override=0.022):
    """This chapter's estimate of a Lumerical set-up of the bend: auto non-uniform mesh at the given mesh accuracy
    (6 + 4(accuracy - 1) points per wavelength at the shortest wavelength, 1.5 um) and a mesh override of d_override
    over the silicon. Returns (nx, ny, nz) inside the PML. Not the tool's own mesher."""
    ppw = 6 + 4 * (accuracy - 1)
    d_ox = LAM_MIN / N_OX / ppw
    nx = axis_cells(*DOM["x"], [(DOM["x"][0], R + W / 2)], d_override, d_ox)
    ny = axis_cells(*DOM["y"], [(-R - W / 2, DOM["y"][1])], d_override, d_ox)
    nz = axis_cells(*DOM["z"], [(-T / 2, T / 2)], d_override, d_ox)
    return nx, ny, nz


def dt_courant(d, factor):
    """Largest stable time step of a 3D Yee grid whose smallest step is d (m) on every axis, times a safety factor."""
    return factor / (C0 * np.sqrt(3.0 / d**2))


def meep_runs():
    return sorted(MEEP["runs"], key=lambda r: r["resolution"]) if MEEP else []


def cells_inside(v, lo, hi):
    c = (np.array(v[:-1]) + np.array(v[1:])) / 2
    return int(np.sum((c > lo) & (c < hi)))


def setups():
    """The bend in three set-ups: interior cells, cells computed with the mirror plane, time steps for T_RUN."""
    out = []
    nx, ny, nz = lumerical_grid(2, 0.022)
    n = nx * ny * nz
    out.append(dict(name="Lumerical FDTD", sub="mesh accuracy 2 + 22 nm override", cells=n, computed=n / 2,
                    steps=T_RUN / dt_courant(22e-9, 0.99), grid=(nx, ny, nz), how="estimate"))
    if T3D:
        g = T3D["bend_grid20"]
        inside = [cells_inside(g[a], *DOM[a]) for a in "xyz"]
        r20 = [r for r in T3D["bend"] if r["steps_per_wvl"] == 20 and r["symmetry"] == [0, 0, 1]][0]
        n = int(np.prod(inside))
        out.append(dict(name="Tidy3D", sub="auto grid, 20 steps per wavelength", cells=n, computed=n / 2, steps=r20["time_steps"],
                        grid=tuple(inside), total=r20["num_cells"], how="from the object"))
    for res, sub, how in ((25, "uniform, resolution 25 (40 nm)", "run here"), (45, "uniform, resolution 45 (22 nm)", "formula")):
        n3 = [int(round((DOM[a][1] - DOM[a][0]) * res)) for a in "xyz"]
        n = int(np.prod(n3))
        out.append(dict(name="MEEP", sub=sub, cells=n, computed=n / 2, steps=T_RUN / (0.5 / res * 1e-6 / C0), grid=tuple(n3), how=how))
    return out


# ------------------------------------------------------------------ Figure 32.3
def fig_modeconv():
    if not (T3D and FEM):
        return
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.55))
    rows = T3D["modes"]
    for ax, key, title in ((axs[0], "neff_TE", "TE$_0$"), (axs[1], "neff_TM", "TM$_0$")):
        d = np.array([r["dmin_nm"] for r in rows]); n = np.array([r[key] for r in rows])
        o = np.argsort(d)
        ax.plot(d[o], n[o], color=C2, lw=0.8, marker="o", ms=3.2, label="Tidy3D, local (no sub-pixel averaging)")
        fd = np.array([r["res_um"] * 1e3 for r in FEM["conv"]]); fn = np.array([r[key] for r in FEM["conv"]])
        ax.plot(fd, fn, color=C1, lw=1.4, marker="s", ms=3.2, label="femwell (mesh follows the faces)")
        if MMODES:
            md = np.array([1e3 / r["resolution"] for r in MMODES["rows"]]); mn = np.array([r[key] for r in MMODES["rows"]])
            ax.plot(md, mn, color=C3, lw=1.1, marker="^", ms=3.2, label="MEEP eigenmode (sub-pixel averaging)")
        ax.axhline(fn[np.argmin(fd)], color=C1, lw=0.7, ls=(0, (3, 2)))
        ax.set_xscale("log"); ax.invert_xaxis()
        ax.set_xticks([100, 50, 20, 10, 5]); ax.set_xticklabels(["100", "50", "20", "10", "5"])
        ax.minorticks_off()
        ax.set_xlim(115, 4.5)
        finish(ax, xlabel="cell or element size in the core (nm)", ylabel="n$_\\mathrm{eff}$")
        ax.text(0.97, 0.05, title, transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, fontweight="bold", color=INK)
    tag(axs[0], "a"); tag(axs[1], "b")
    axs[0].set_ylim(2.08, 2.66); axs[1].set_ylim(1.62, 2.05)
    h, l = axs[0].get_legend_handles_labels()
    fig.tight_layout(w_pad=1.5, rect=(0, 0.1, 1, 1))
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=6.6, handlelength=1.8, bbox_to_anchor=(0.5, 0.0))
    savefig(fig, "ch32_modeconv")


# ------------------------------------------------------------------ Figure 32.5
def fig_fit():
    if not T3D:
        return
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.5))
    for k, col in (("1", C4), ("2", C1)):
        f = T3D["fit"][k]
        wl = np.array(f["wl"]); nf = np.array(f["n_fit"]); n0 = n_si_li(wl)
        axs[0].plot(wl, (nf - n0) * 1e4, color=col, label=f"{k} pole" + ("s" if k != "1" else ""))
        # material group index N = n - lambda dn/dlambda, from the fit and from the formula
        Nf = nf - wl * np.gradient(nf, wl); N0 = n0 - wl * np.gradient(n0, wl)
        axs[1].plot(wl[3:-3], (Nf - N0)[3:-3] * 1e3, color=col)
    for ax in axs:
        ax.axvspan(1.5, 1.6, color=GRID, alpha=0.7, lw=0)
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_xlim(1.2, 2.0)
    finish(axs[0], xlabel="wavelength (µm)", ylabel="error in n (×10$^{-4}$)")
    finish(axs[1], xlabel="wavelength (µm)", ylabel="error in group index (×10$^{-3}$)")
    axs[0].legend(loc="lower left", fontsize=7)
    tag(axs[0], "a"); tag(axs[1], "b")
    fig.tight_layout(w_pad=1.5)
    savefig(fig, "ch32_fit")


# ------------------------------------------------------------------ Figure 32.6
def fig_region():
    if not T3D:
        return
    g = T3D["bend_grid20"]
    gx, gy, gz = (np.array(g[k]) for k in "xyz")
    PML_FC, GL = "#C9C2B0", dict(color="#8C99B0", lw=0.12, alpha=0.7, zorder=2)

    def pml(ax, u, v, U, V):
        for (u0, u1, v0, v1) in ((u[0], U[0], v[0], v[-1]), (U[1], u[-1], v[0], v[-1]), (U[0], U[1], v[0], V[0]), (U[0], U[1], V[1], v[-1])):
            ax.add_patch(Rectangle((u0, v0), u1 - u0, v1 - v0, fc=PML_FC, alpha=0.6, ec="none", zorder=1))
        for x in u:
            ax.plot([x, x], [v[0], v[-1]], **GL)
        for y in v:
            ax.plot([u[0], u[-1]], [y, y], **GL)

    fig = plt.figure(figsize=(6.3, 3.45))
    ax = fig.add_axes([0.0, 0.0, 0.58, 1.0]); frameless(ax, (gx[0] - 0.05, gx[-1] + 0.05), (gy[0] - 0.62, gy[-1] + 0.05))
    box(ax, gx[0], gy[0], gx[-1] - gx[0], gy[-1] - gy[0], "ox", z=0)
    pml(ax, gx, gy, DOM["x"], DOM["y"])
    box(ax, gx[0], -R - W / 2, 0.01 - gx[0], W, "si", z=3)
    wg_arc(ax, 0, 0, R, W, -90, 0, "si", z=3)
    box(ax, R - W / 2, 0, W, gy[-1], "si", z=3)
    ax.plot([-1.0, -1.0], [-R - 1.0, -R + 1.0], color=RED, lw=1.6, zorder=6)
    ax.plot([-0.5, -0.5], [-R - 1.0, -R + 1.0], color=BLUE, lw=1.3, zorder=6)
    ax.plot([R - 1.0, R + 1.0], [1.0, 1.0], color=BLUE, lw=1.3, zorder=6)
    arrow(ax, (-0.95, -R), (-0.6, -R), col=RED, lw=1.0, ms=6, z=7)
    label(ax, -1.0, -R - 1.08, "mode\nsource", fs=7.3, col=RED, va="top", bg="white")
    label(ax, -0.45, -R + 1.08, "R monitor", fs=7.3, col=BLUE, va="bottom", ha="left", bg="white")
    label(ax, R - 1.0, 1.12, "T monitor", fs=7.3, col=BLUE, ha="left", va="bottom", bg="white")
    ax.plot([0, R * np.cos(np.radians(-45))], [0, R * np.sin(np.radians(-45))], color=INK, lw=0.7, zorder=5)
    ax.plot([0], [0], marker="+", color=INK, ms=5, zorder=5)
    label(ax, 0.62, -0.38, "R = 2 µm", fs=7.5, col=INK, bg="white", ha="left")
    label(ax, (DOM["x"][0] + DOM["x"][1]) / 2, (gy[0] + DOM["y"][0]) / 2, "PML (12 cells)", fs=7.3, col=INK, bg="white")
    dim(ax, (DOM["x"][0], gy[0] - 0.2), (DOM["x"][1], gy[0] - 0.2), "4.75 µm inside the PML", fs=7.3)
    scalebar(ax, gx[-1] - 1.05, gy[0] - 0.55, 1.0, "1 µm")
    panel(ax, "a", 0.0, 1.0)
    ylo, yhi = gy[0], -0.4
    ax2 = fig.add_axes([0.61, 0.22, 0.39, 0.66]); frameless(ax2, (ylo - 0.05, yhi + 0.05), (gz[0] - 0.05, gz[-1] + 0.05))
    box(ax2, ylo, gz[0], yhi - ylo, gz[-1] - gz[0], "ox", z=0)
    gyc = gy[gy <= yhi]
    pml(ax2, np.r_[gyc, yhi], gz, (DOM["y"][0], yhi + 1), DOM["z"])
    box(ax2, -R - W / 2, -T / 2, W, T, "si", z=3)
    ax2.plot([ylo, yhi], [0, 0], color=TEAL, lw=1.0, ls=(0, (4, 2)), zorder=5)
    ax2.add_patch(Rectangle((-R - 1.0, -0.8), 2.0, 1.6, fc="none", ec=RED, lw=1.0, zorder=6))
    label(ax2, -R, 0.84, "source plane", fs=7.3, col=RED, va="bottom", bg="white")
    label(ax2, ylo + 0.08, 0.07, "mirror plane", fs=7.3, col=TEAL, va="bottom", ha="left", bg="white")
    label(ax2, (ylo + yhi) / 2, gz[0] - 0.12, "cross-section through the source (y–z)", fs=7.3, va="top")
    panel(ax2, "b", 0.0, 1.08)
    save(fig, "ch32_region")


# ------------------------------------------------------------------ Figure 32.7
def fig_cost():
    S = setups()
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.45), sharey=True)
    ylab = [f"{s_['name']}\n{s_['sub']}" for s_ in S]
    yy = np.arange(len(S))[::-1]
    cols = [C3, C1, C2, C2][:len(S)]
    cells = np.array([s_["computed"] for s_ in S]) / 1e6
    upd = np.array([s_["computed"] * s_["steps"] for s_ in S]) / 1e9
    axs[0].barh(yy, cells, color=cols, height=0.6)
    axs[1].barh(yy, upd, color=cols, height=0.6)
    for k, s_ in enumerate(S):
        axs[0].text(cells[k] + 0.04, yy[k], f"{cells[k]:.2f} M ({s_['how']})", va="center", fontsize=6.3, color=INK)
        axs[1].text(upd[k] + 0.25, yy[k], f"{upd[k]:.1f}×10$^9$ ({s_['steps']:.0f} steps)", va="center", fontsize=6.3, color=INK)
    axs[0].set_yticks(yy); axs[0].set_yticklabels(ylab, fontsize=6.4)
    axs[0].set_xlim(0, cells.max() * 1.85); axs[1].set_xlim(0, upd.max() * 1.8)
    finish(axs[0], xlabel="cells computed: PML excluded, mirror plane used (millions)")
    finish(axs[1], xlabel="cell updates for 250 fs (×10$^9$)")
    for ax in axs:
        ax.grid(axis="y", visible=False)
    tag(axs[0], "a"); tag(axs[1], "b")
    fig.tight_layout(w_pad=0.8)
    savefig(fig, "ch32_cost")


# ------------------------------------------------------------------ Figure 32.8
def fig_bendconv():
    runs = meep_runs()
    if not runs:
        return
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.55))
    res = np.array([r["resolution"] for r in runs])
    L = np.array([-r["T1550_dB"] for r in runs])
    Lb = np.array([[-10 * np.log10(x) for x in r["T"]] for r in runs])
    Rr = np.array([r["R1550_dB"] for r in runs])
    ax = axs[0]
    ax.fill_between(res, Lb.min(axis=1), Lb.max(axis=1), color=C1, alpha=0.15, lw=0, label="1500–1600 nm")
    ax.plot(res, L, color=C1, marker="o", ms=3.5, label="loss, 1550 nm")
    ax.set_ylim(0, max(0.3, L.max() * 1.15))
    finish(ax, xlabel="resolution (cells per µm)", ylabel="bend loss into TE$_0$ (dB)")
    ax2 = ax.twinx()
    ax2.plot(res, Rr, color=C4, marker="^", ms=3.5, lw=1.0, label="reflection")
    ax2.set_ylabel("reflection, 1550 nm (dB)", color=C4); ax2.tick_params(axis="y", colors=C4)
    ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(C4); ax2.grid(False); ax2.set_ylim(-50, 0)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=6.4)
    ax = axs[1]
    cells = np.array([r["cells_computed"] for r in runs]); cpu = np.array([r["cpu_s"] for r in runs])
    ax.loglog(res, cells / 1e6, color=C3, marker="s", ms=3.5, label="cells computed (millions)")
    ax.loglog(res, cpu / 60, color=C2, marker="o", ms=3.5, label="CPU time (minutes)")
    ax.loglog(res, cells[0] / 1e6 * (res / res[0]) ** 3, color=C3, lw=0.7, ls=(0, (3, 2)))
    ax.loglog(res, cpu[0] / 60 * (res / res[0]) ** 4, color=C2, lw=0.7, ls=(0, (3, 2)))
    ax.text(22, cells[0] / 1e6 * (22 / res[0]) ** 3 * 0.45, r"$\propto$ res$^3$", fontsize=6.4, color=C3, ha="left", va="top")
    ax.text(17, cpu[0] / 60 * (17 / res[0]) ** 4 * 1.6, r"$\propto$ res$^4$", fontsize=6.4, color=C2, ha="right", va="bottom")
    ax.set_xlim(9, 33)
    ax.set_xticks([10, 15, 20, 30]); ax.set_xticklabels(["10", "15", "20", "30"]); ax.minorticks_off()
    finish(ax, xlabel="resolution (cells per µm)", ylabel="cost")
    ax.legend(loc="upper left", fontsize=6.4)
    tag(axs[0], "a"); tag(axs[1], "b")
    fig.tight_layout(w_pad=2.0)
    savefig(fig, "ch32_bendconv")


if __name__ == "__main__":
    fig_lumerical()
    fig_tidy3d()
    fig_modeconv()
    fig_loop()
    fig_fit()
    fig_region()
    fig_cost()
    fig_bendconv()
    for s_ in setups():
        print(f"{s_['name']:16s} {s_['sub']:36s} grid {s_['grid']} cells {s_['cells']:,} computed {s_['computed']:,.0f} "
              f"steps {s_['steps']:.0f} updates {s_['computed'] * s_['steps']:.3g} fields(double) {s_['computed'] * 48 / 2**20:.0f} MB")
