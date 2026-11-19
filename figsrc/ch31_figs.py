"""Figures of Chapter 31 (How Photonic Simulators Work).

    python -I -X utf8 figsrc/ch31_figs.py [names...]

ch31_landscape  what each kind of solver keeps: dimensions against the way the equations are solved
ch31_fde        the Yee grid of a finite-difference mode solver, a computed mode, and n_eff against grid step
                (data: ch31_fde.json from ch31_fde.py)
ch31_eme        eigenmode expansion of a 0.5 -> 3 um taper: sections and local modes, power against length,
                convergence (data: ch31_eme.json from ch31_eme.py)
ch31_yee        the 3D Yee cell, the discrete curl around one H component, and the leapfrog in time
ch31_numerics   the Courant limit (a small 3D FDTD in NumPy, run here) and numerical dispersion against cells per
                wavelength (the Yee dispersion relation, solved here)
ch31_pml        absorbing boundaries: three absorbers and their reflection against thickness (ch31_meep_pml.json)
ch31_pulse      one pulsed run against continuous-wave runs, for a sidewall Bragg grating (ch31_meep_bragg.json)
ch31_subpixel   staircase against subpixel averaging: the slab index against resolution (ch31_meep_conv.json)
ch31_bend       2D FDTD of 90-degree bends: the field at 1550 nm and the loss against resolution (ch31_meep_bend.json)
ch31_cost       memory and run time of a 3D grating-coupler simulation against resolution (ch31_meep_cost.json)
ch31_varfdtd    collapsing the vertical direction: strip and rib, 3D mode solver against the effective-index method
                (ch31_fde_sweep.json)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from matplotlib.patches import Rectangle, Polygon, Circle, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
LAM, N_SI, N_OX, N_I = 1.55, 3.4764, 1.4440, 2.8482
EC, HC = BLUE, RED            # colours of E and H components in the drawings


def load(name):
    return json.load(open(os.path.join(HERE, name)))


# ------------------------------------------------------------------ slab helpers (NumPy)
def slab_te(lam, d, n1, n2, nb=None):
    """Fundamental TE mode of a symmetric slab: n_eff and the confinement of int E^2 in the film."""
    k = 2 * np.pi / lam
    lo = np.sqrt(max(n1 ** 2 - (np.pi / (k * d)) ** 2, n2 ** 2)) + 1e-12      # kappa d / 2 < pi / 2 above this
    hi = n1 - 1e-12
    for _ in range(200):
        m = (lo + hi) / 2
        ka, ga = k * np.sqrt(n1 ** 2 - m ** 2), k * np.sqrt(m ** 2 - n2 ** 2)
        if ka * np.tan(ka * d / 2) - ga > 0: lo = m
        else: hi = m
    ka, ga = k * np.sqrt(n1 ** 2 - m ** 2), k * np.sqrt(m ** 2 - n2 ** 2)
    inside = d / 2 + np.sin(ka * d) / (2 * ka)
    outside = np.cos(ka * d / 2) ** 2 / ga
    return m, inside / (inside + outside)


def lateral_tm(lam, w, nc, ncl):
    """Fundamental mode of the lateral slab with TM boundary conditions (TE-like strip): bisection."""
    k = 2 * np.pi / lam
    r = (nc / ncl) ** 2
    lo = np.sqrt(max(nc ** 2 - (np.pi / (k * w)) ** 2, ncl ** 2)) + 1e-12
    hi = nc - 1e-12
    for _ in range(200):
        m = (lo + hi) / 2
        ka, ga = k * np.sqrt(nc ** 2 - m ** 2), k * np.sqrt(m ** 2 - ncl ** 2)
        if ka * np.tan(ka * w / 2) - r * ga > 0: lo = m
        else: hi = m
    return m


def slab_stack_te(lam, layers, n_lo, n_hi):
    """TE0 of a slab made of layers [(thickness, index), ...] from bottom to top between half-spaces n_lo and n_hi,
    by transfer matrices and bisection on the decaying-solution condition."""
    k = 2 * np.pi / lam

    def f(n):
        g_lo = k * np.sqrt(n ** 2 - n_lo ** 2)
        E, dE = 1.0, g_lo                       # E and dE/dz at the bottom, decaying downwards
        for t, nl in layers:
            q2 = k ** 2 * (nl ** 2 - n ** 2)
            if q2 > 0:
                q = np.sqrt(q2); E, dE = E * np.cos(q * t) + dE / q * np.sin(q * t), -E * q * np.sin(q * t) + dE * np.cos(q * t)
            else:
                q = np.sqrt(-q2); E, dE = E * np.cosh(q * t) + dE / q * np.sinh(q * t), E * q * np.sinh(q * t) + dE * np.cosh(q * t)
        return dE + k * np.sqrt(n ** 2 - n_hi ** 2) * E   # zero when the field decays upwards too

    ns = np.linspace(max(n_lo, n_hi) + 1e-6, max(nl for _, nl in layers) - 1e-6, 4000)
    v = np.array([f(n) for n in ns])
    i = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0][-1]
    lo, hi = ns[i], ns[i + 1]
    for _ in range(100):
        m = (lo + hi) / 2
        if np.sign(f(m)) == np.sign(f(lo)): lo = m
        else: hi = m
    return m


# ------------------------------------------------------------------ Figure 31.1
def fig_landscape():
    fig, ax = geom_axes(figsize=(6.3, 3.2), xlim=(0, 13.3), ylim=(-0.35, 6.3), equal=False)
    cols = [("a cross-section", 3.3), ("2D: top view or side view", 6.95), ("the full 3D device", 10.95)]
    rows = [("eigenmodes\n(frequency\ndomain)", 4.95), ("one\nfrequency,\nwhole device", 2.95), ("time\nstepping\n(all\nfrequencies)", 0.95)]
    for t, x in cols:
        label(ax, x, 6.05, t, fs=7.0, bold=True)
    for t, y in rows:
        label(ax, 0.8, y, t, fs=6.5, bold=True, ha="center")
    for x in [1.65, 5.15, 8.85]:
        ax.plot([x, x], [-0.1, 5.85], color=GRID, lw=0.8, zorder=0)
    for y in [1.95, 3.95]:
        ax.plot([1.65, 13.25], [y, y], color=GRID, lw=0.8, zorder=0)

    def card(x, y, w, h, title, lines, fc="#EEF3FA"):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=fc, ec=INK, lw=0.7, zorder=3))
        label(ax, x, y + h / 2 - 0.22, title, fs=6.8, bold=True, z=5)
        label(ax, x, y - 0.12, lines, fs=5.9, col=MUTED, z=5)

    card(3.3, 4.95, 3.2, 1.5, "mode solver: FDE, FEM",
         "modes of one cross-section:\n$n_\\mathrm{eff}$, $n_g$, fields, loss\nunknowns: 2 × $N_xN_y$")
    card(6.95, 4.95, 3.4, 1.5, "EME  ·  BPM",
         "modes of each section, matched\n(EME), or one field marched along z\n(BPM); cost $\\propto$ sections × modes³")
    card(10.95, 4.95, 3.9, 1.5, "EME with 3D modes",
         "devices that change slowly along z\n(tapers, MMIs, couplers), from\nfull-vector cross-section modes")
    card(6.95, 2.95, 3.4, 1.5, "2D FDFD / FEM",
         "one sparse linear solve per\nwavelength, $N_xN_y$ unknowns:\nresonators, inverse design")
    card(10.95, 2.95, 3.9, 1.5, "3D FDFD / FEM",
         "$N_xN_yN_z$ unknowns per wavelength:\nhuge memory (direct solvers) or\nslow convergence (iterative)")
    card(6.95, 0.95, 3.4, 1.5, "2D and 2.5D FDTD",
         "a pulse on an $N_xN_y$ grid;\n2.5D folds the vertical direction\ninto an effective index")
    card(10.95, 0.95, 3.9, 1.5, "3D FDTD",
         "any geometry, all wavelengths in one\nrun: $N_xN_yN_z$ cells × $N_t$ steps;\nthe most general, the most costly", fc="#FBF3E6")
    ax.text(3.3, 2.95, "a cross-section has no\n'whole device': its\nmodes are the answer", ha="center", va="center", fontsize=5.9, color=MUTED, style="italic")
    ax.text(3.3, 0.95, "(possible, but a mode\nsolver does it better)", ha="center", va="center", fontsize=5.9, color=MUTED, style="italic")
    arrow(ax, (5.3, -0.22), (13.2, -0.22), col=MUTED, lw=0.8, ms=6)
    label(ax, 9.25, -0.22, "more of the geometry kept → more general, more costly", fs=5.8, col=MUTED, bg="white")
    save(fig, "ch31_landscape")


# ------------------------------------------------------------------ Figure 31.2
def fig_fde():
    d = load("ch31_fde.json")
    fig = plt.figure(figsize=(6.3, 2.75))
    # (a) the Yee positions in a few cells near the strip's corner
    a = fig.add_axes([0.0, 0.08, 0.30, 0.80])
    frameless(a, (-0.5, 5.6), (-0.6, 5.0))
    h = 1.0
    nx, ny = 5, 4
    cx, cy = 2.35, 1.6               # the corner of the core in cell units (core to the lower left)
    e1, e2 = 1.0, 0.0
    for i in range(nx):
        for j in range(ny):
            fx = np.clip(cx - i, 0, 1); fy = np.clip(cy - j, 0, 1)
            f = fx * fy
            a.add_patch(Rectangle((i, j), 1, 1, fc=(np.array(plt.matplotlib.colors.to_rgb(MAT["si"])) * f
                                                    + np.array(plt.matplotlib.colors.to_rgb(MAT["ox"])) * (1 - f)),
                                  ec="none", zorder=1))
    a.plot([0, cx, cx], [cy, cy, 0], color=INK, lw=1.0, zorder=4)
    for i in range(nx + 1):
        a.plot([i, i], [0, ny], color=INK, lw=0.4, alpha=0.6, zorder=2)
    for j in range(ny + 1):
        a.plot([0, nx], [j, j], color=INK, lw=0.4, alpha=0.6, zorder=2)
    for i in range(nx):
        for j in range(ny + 1):
            arrow(a, (i + 0.32, j), (i + 0.68, j), col=EC, lw=0.9, ms=5, z=6)
    for i in range(nx + 1):
        for j in range(ny):
            arrow(a, (i, j + 0.32), (i, j + 0.68), col=TEAL, lw=0.9, ms=5, z=6)
    for i in range(nx + 1):
        for j in range(ny + 1):
            a.plot(i, j, "o", ms=2.2, color=MUTED, zorder=6)
    for i in range(nx):
        for j in range(ny):
            a.plot(i + 0.5, j + 0.5, "o", ms=3.2, mfc="white", mec=HC, mew=0.8, zorder=6)
    label(a, 1.5, 0.2, "Si", fs=6.4, bold=True, bg="white", z=8)
    label(a, 4.0, 3.2, "SiO$_2$", fs=6.4, bold=True, bg="white", z=8)
    yl = 4.55
    arrow(a, (-0.3, yl), (0.15, yl), col=EC, lw=0.9, ms=5); label(a, 0.22, yl, "$E_x$", fs=6.5, col=EC, ha="left")
    arrow(a, (1.25, yl - 0.22), (1.25, yl + 0.22), col=TEAL, lw=0.9, ms=5); label(a, 1.4, yl, "$E_y$", fs=6.5, col=TEAL, ha="left")
    a.plot(2.45, yl, "o", ms=2.2, color=MUTED); label(a, 2.6, yl, "$E_z$", fs=6.5, col=MUTED, ha="left")
    a.plot(3.6, yl, "o", ms=3.2, mfc="white", mec=HC, mew=0.8); label(a, 3.75, yl, "$H_z$", fs=6.5, col=HC, ha="left")
    label(a, 2.5, -0.35, "one cell = $h$; cells cut by a wall get a mixed ε", fs=5.8, col=MUTED)
    panel(a, "a", 0.0, 1.05)
    # (b) the computed TE0 E_x on the window, with every fifth grid line
    f = d["field"]
    Ex = np.array(f["Ex"]); xc = np.array(f["xc"]); yn = np.array(f["yn"])
    b = fig.add_axes([0.345, 0.16, 0.28, 0.68])
    b.imshow(Ex, extent=(xc[0], xc[-1], yn[0], yn[-1]), origin="lower", cmap=SIGNED_CMAP, vmin=-1, vmax=1, zorder=1,
             interpolation="bilinear")
    xc0, yc0 = d["core_centre"]
    b.add_patch(Rectangle((xc0 - 0.25, yc0 - 0.11), 0.5, 0.22, fc="none", ec=INK, lw=0.8, zorder=3))
    for x in np.arange(-1.2, 1.21, 0.1):
        b.axvline(x, color=INK, lw=0.2, alpha=0.35, zorder=2)
    for y in np.arange(-0.9, 0.91, 0.1):
        b.axhline(y, color=INK, lw=0.2, alpha=0.35, zorder=2)
    b.set_xlim(-1.0, 1.0); b.set_ylim(-0.75, 0.75); b.set_aspect("equal"); b.grid(False)
    b.set_xticks([-1, 0, 1]); b.set_yticks([-0.5, 0, 0.5])
    b.set_xlabel("x (µm)", labelpad=1); b.set_ylabel("y (µm)", labelpad=1)
    b.text(0.03, 0.95, f"TE0  $E_x$,  $h$ = 20 nm\n$n_\\mathrm{{eff}}$ = {f['n_eff']:.4f}", transform=b.transAxes, fontsize=6.0,
           va="top", color=INK)
    b.text(0.97, 0.04, "grid lines drawn every 5th", transform=b.transAxes, fontsize=5.6, va="bottom", ha="right", color=MUTED)
    tag(b, "b")
    # (c) n_eff against grid step
    c = fig.add_axes([0.72, 0.16, 0.27, 0.70])
    for mode, col, lab in [("stair", C2, "sampled (staircase)"), ("avg", C1, "averaged ε")]:
        rr = sorted([r for r in d["runs"] if r["mode"] == mode], key=lambda r: r["h"])
        c.plot([1000 * r["h"] for r in rr], [r["n_eff"] for r in rr], "o-", color=col, ms=3, lw=1.1, label=lab)
    c.axhline(2.4459, color=INK, lw=0.8, ls="--", label="femwell (Ch. 6): 2.4459")
    c.set_xlim(0, 42); c.set_ylim(2.39, 2.52)
    finish(c, xlabel="grid step $h$ (nm)", ylabel="$n_\\mathrm{eff}$ (TE0)")
    c.legend(loc="upper left", fontsize=6.0, handlelength=1.5)
    tag(c, "c")
    save(fig, "ch31_fde")


# ------------------------------------------------------------------ Figure 31.3
def fig_eme():
    d = load("ch31_eme.json")
    fig = plt.figure(figsize=(6.3, 3.4))
    # (a) top view of the taper (20 um long), cut into 8 sections for the drawing, with local TE0 profiles
    a = fig.add_axes([0.0, 0.53, 1.0, 0.42])
    L, ns = 20.0, 8
    xs = np.linspace(0, L, ns + 1)
    sc = 1.6                                            # transverse scale
    frameless(a, (-4.2, 24.6), (-3.0 * sc, 2.9 * sc), equal=False)
    w = lambda x: d["w0"] + (d["w1"] - d["w0"]) * x / L
    box(a, -4.2, -3.0 * sc, 28.8, 5.9 * sc, "ox", z=0)
    a.add_patch(Polygon([[0, -w(0) / 2 * sc], [L, -w(L) / 2 * sc], [L, w(L) / 2 * sc], [0, w(0) / 2 * sc]], fc="none", ec=INK, lw=0.6, ls=(0, (2, 1.5)), zorder=4))
    box(a, -4.2, -w(0) / 2 * sc, 4.2, w(0) * sc, "si", z=2); box(a, L, -w(L) / 2 * sc, 4.6, w(L) * sc, "si", z=2)
    for i in range(ns):
        xm = (xs[i] + xs[i + 1]) / 2
        box(a, xs[i], -w(xm) / 2 * sc, xs[i + 1] - xs[i], w(xm) * sc, "si", z=2)
    for x in xs:
        a.plot([x, x], [-2.75 * sc, 2.75 * sc], color=INK, lw=0.5, ls=(0, (2, 1.5)), zorder=3)
    for p in d["profiles"]:
        x0 = (p["w"] - d["w0"]) / (d["w1"] - d["w0"]) * L
        xx = np.array(p["x"]); H = np.array(p["H"])
        xx = np.concatenate([-xx[::-1], xx[1:]]); H = np.concatenate([H[::-1], H[1:]])
        m = np.abs(xx) < 2.7
        a.plot(x0 + 1.1 * H[m], xx[m] * sc, color=RED, lw=0.9, zorder=5)
        a.plot([x0, x0], [-2.7 * sc, 2.7 * sc], color=RED, lw=0.4, alpha=0.4, zorder=4)
    label(a, -2.1, 1.1 * sc, "0.5 µm\nTE0 in", fs=6.0)
    label(a, 22.4, 2.25 * sc, "3 µm", fs=6.0)
    label(a, 10, -2.6 * sc, "sections of constant width; each interface → an S-matrix from mode overlaps", fs=6.0, bg="white", z=8)
    label(a, 10, 2.5 * sc, "local TE0 profiles (red)", fs=6.0, col=RED, bg="white", z=8)
    a.text(24.5, -2.9 * sc, "length 20 µm, 8 sections drawn; width × 1.6", fontsize=5.6, color=MUTED, style="italic", ha="right", va="bottom")
    panel(a, "a", 0.0, 1.02)
    # (b) power against taper length
    b = fig.add_axes([0.08, 0.09, 0.40, 0.34])
    Ls = np.array(d["L"])
    b.semilogy(Ls, d["P_TE2"], color=C2, lw=1.3, label="into TE2")
    b.semilogy(Ls, np.maximum(d["P_TE4"], 1e-9), color=C3, lw=1.0, label="into TE4")
    b.plot([20], [0.006887], "o", mfc="none", mec=INK, ms=5, mew=0.9)
    b.annotate("Ch. 8 demo's\nEME check", (20, 0.006887), (27, 0.03), fontsize=5.8, color=INK,
               arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED))
    b.set_xlim(0, 60); b.set_ylim(1e-5, 0.5)
    finish(b, xlabel="taper length (µm)", ylabel="power converted")
    b.legend(loc="lower left", fontsize=5.8, handlelength=1.4, borderaxespad=0.2)
    tag(b, "b")
    # (c) convergence at 20 um
    c = fig.add_axes([0.60, 0.09, 0.38, 0.34])
    cs = d["conv_sections"]; cm = d["conv_modes"]
    c.loglog([r["n"] for r in cs], [100 * r["P_TE2"] for r in cs], "o-", color=C2, ms=3, lw=1.1, label="against sections (24 modes)")
    c.loglog([r["n"] for r in cm[1:]], [100 * r["P_TE2"] for r in cm[1:]], "s--", color=C5, ms=3, lw=1.0, label="against modes (200 sections)")
    c.axhline(100 * cs[-1]["P_TE2"], color=MUTED, lw=0.6, ls=":")
    c.set_ylim(0.1, 100); c.set_xlim(0.8, 500)
    c.set_xticks([1, 10, 100]); c.set_xticklabels(["1", "10", "100"]); c.set_yticks([0.1, 1, 10, 100]); c.set_yticklabels(["0.1", "1", "10", "100"])
    finish(c, xlabel="number of sections or modes", ylabel="TE2 at 20 µm (%)")
    c.legend(loc="upper right", fontsize=5.8, handlelength=1.6)
    tag(c, "c")
    save(fig, "ch31_eme")


# ------------------------------------------------------------------ Figure 31.4
def iso(p, a=0.42, th=np.deg2rad(32)):
    x, y, z = p
    return np.array([x + a * y * np.cos(th), z + a * y * np.sin(th)])


def fig_yee():
    fig = plt.figure(figsize=(6.3, 2.75))
    # (a) the 3D cell
    a = fig.add_axes([0.0, 0.02, 0.36, 0.9])
    frameless(a, (-0.35, 1.75), (-0.3, 1.65))
    V = {(i, j, k): iso((i, j, k)) for i in (0, 1) for j in (0, 1) for k in (0, 1)}
    edges = [((0, j, k), (1, j, k)) for j in (0, 1) for k in (0, 1)] + [((i, 0, k), (i, 1, k)) for i in (0, 1) for k in (0, 1)] + \
            [((i, j, 0), (i, j, 1)) for i in (0, 1) for j in (0, 1)]
    hidden = lambda p, q: (p == (0, 1, 0) or q == (0, 1, 0))
    for p, q in edges:
        P, Q = V[p], V[q]
        a.plot([P[0], Q[0]], [P[1], Q[1]], color=INK, lw=0.7, ls=(0, (2, 2)) if hidden(p, q) else "-", alpha=0.5 if hidden(p, q) else 1, zorder=2)
    # E on every edge midpoint, along the edge
    for p, q in edges:
        m = (np.array(p) + np.array(q)) / 2
        dvec = (np.array(q) - np.array(p)) * 0.17
        P0, P1 = iso(m - dvec), iso(m + dvec)
        hid = hidden(p, q)
        arrow(a, P0, P1, col=EC, lw=1.1 if not hid else 0.8, ms=6, z=5, alpha=1 if not hid else 0.45)
    # H at the three visible face centres, normal to the face
    faces = [((0.5, 0, 0.5), (0, -1, 0), "$H_y$", 0.55, (-0.06, -0.07)), ((1, 0.5, 0.5), (1, 0, 0), "$H_x$", 0.22, (0.08, 0)),
             ((0.5, 0.5, 1), (0, 0, 1), "$H_z$", 0.22, (0, 0.07))]
    for c0, n, t, ln, off in faces:
        c0 = np.array(c0); n = np.array(n) * ln
        arrow(a, iso(c0), iso(c0 + n), col=HC, lw=1.2, ms=6, z=6)
        a.plot(*iso(c0), "o", ms=2.6, color=HC, zorder=6)
        tp = iso(c0 + n) + np.array(off)
        label(a, tp[0], tp[1], t, fs=7, col=HC)
    for p, t, off in [((0.5, 0, 0), "$E_x$", (0, -0.1)), ((1, 0.5, 0), "$E_y$", (0.16, -0.02)), ((1, 0, 0.5), "$E_z$", (0.12, 0))]:
        q = iso(p) + np.array(off)
        label(a, q[0], q[1], t, fs=7, col=EC)
    o = iso((0, 0, 0))
    for vec, t in [((0.35, 0, 0), "x"), ((0, 0.5, 0), "y"), ((0, 0, 0.32), "z")]:
        pass
    label(a, 0.7, 1.58, "E on the edges, H at the faces", fs=6.3, col=INK)
    panel(a, "a", 0.0, 1.02)
    # (b) the discrete curl around H_z
    b = fig.add_axes([0.37, 0.02, 0.27, 0.9])
    frameless(b, (-0.45, 1.5), (-0.5, 1.65))
    b.add_patch(Rectangle((0, 0), 1, 1, fc="#F3F6FB", ec=INK, lw=0.8, zorder=1))
    b.plot(0.5, 0.5, "o", ms=9, mfc="white", mec=HC, mew=1.2, zorder=4); b.plot(0.5, 0.5, "o", ms=2.4, color=HC, zorder=5)
    label(b, 0.5, 0.33, "$H_z$", fs=7.5, col=HC)
    arrow(b, (0.3, 0), (0.7, 0), col=EC, lw=1.3, ms=7); label(b, 0.5, -0.13, "$E_x(j)$", fs=6.8, col=EC)
    arrow(b, (0.7, 1), (0.3, 1), col=EC, lw=1.3, ms=7); label(b, 0.5, 1.13, "$E_x(j{+}1)$", fs=6.8, col=EC)
    arrow(b, (1, 0.3), (1, 0.7), col=EC, lw=1.3, ms=7); label(b, 1.03, 0.5, "$E_y(i{+}1)$", fs=6.8, col=EC, ha="left")
    arrow(b, (0, 0.7), (0, 0.3), col=EC, lw=1.3, ms=7); label(b, -0.03, 0.5, "$E_y(i)$", fs=6.8, col=EC, ha="right")
    b.text(0.5, 1.47, "circulation of E around a face\n= rate of change of the H through it", ha="center", va="center", fontsize=6.1, color=INK)
    b.text(0.5, -0.38, "(Faraday's law on one face:\nthe discrete curl)", ha="center", va="center", fontsize=5.9, color=MUTED)
    panel(b, "b", 0.0, 1.02)
    # (c) leapfrog in time: a 1D x-t lattice
    c = fig.add_axes([0.66, 0.1, 0.34, 0.8])
    frameless(c, (-0.6, 4.6), (-0.7, 3.75), equal=False)
    for n in range(4):
        for i in range(5):
            c.plot(i, n, "o", ms=4.2, color=EC, zorder=4)
    for n in range(3):
        for i in range(4):
            c.plot(i + 0.5, n + 0.5, "s", ms=4.0, mfc="white", mec=HC, mew=1.0, zorder=4)
    # one update of E at (2, 2) from H at (1.5, 1.5), (2.5, 1.5) and E at (2, 1)
    for src in [(1.5, 1.5), (2.5, 1.5), (2, 1)]:
        c.annotate("", (2, 2), src, arrowprops=dict(arrowstyle="-|>", lw=0.9, color=EC, shrinkA=3, shrinkB=4, mutation_scale=7), zorder=5)
    for src in [(1, 1), (2, 1), (1.5, 0.5)]:
        c.annotate("", (1.5, 1.5), src, arrowprops=dict(arrowstyle="-|>", lw=0.9, color=HC, shrinkA=3, shrinkB=4, mutation_scale=7), zorder=5)
    for n, t in [(0, "$n$"), (1, "$n{+}1$"), (2, "$n{+}2$"), (3, "$n{+}3$")]:
        label(c, -0.45, n, t, fs=6.3, ha="right", col=EC)
    for n, t in [(0.5, "$n{+}\\frac{1}{2}$"), (1.5, "$n{+}\\frac{3}{2}$"), (2.5, "$n{+}\\frac{5}{2}$")]:
        label(c, 4.55, n, t, fs=6.3, ha="left", col=HC)
    label(c, 2, -0.5, "position along x  →   (E at $i$, H at $i{+}\\frac{1}{2}$)", fs=5.9, col=MUTED)
    c.text(2, 3.55, "time ↑: H half a step after E", ha="center", fontsize=6.1, color=INK)
    panel(c, "c", 0.0, 1.0)
    save(fig, "ch31_yee")


# ------------------------------------------------------------------ Figure 31.5
def fdtd3d_maxfield(S, n=16, steps=160, seed=1):
    """Vacuum 3D Yee FDTD on a periodic n^3 grid (c = dx = 1), random initial E: the largest |E| at each step."""
    rng = np.random.default_rng(seed)
    E = [rng.standard_normal((n, n, n)) for _ in range(3)]
    H = [np.zeros((n, n, n)) for _ in range(3)]
    dt = S
    fwd = lambda f, ax: np.roll(f, -1, ax) - f
    bwd = lambda f, ax: f - np.roll(f, 1, ax)
    out = []
    for _ in range(steps):
        H[0] -= dt * (fwd(E[2], 1) - fwd(E[1], 2)); H[1] -= dt * (fwd(E[0], 2) - fwd(E[2], 0)); H[2] -= dt * (fwd(E[1], 0) - fwd(E[0], 1))
        E[0] += dt * (bwd(H[2], 1) - bwd(H[1], 2)); E[1] += dt * (bwd(H[0], 2) - bwd(H[2], 0)); E[2] += dt * (bwd(H[1], 0) - bwd(H[0], 1))
        out.append(max(np.abs(e).max() for e in E))
    return np.array(out)


def vp_error(N, u, Sn):
    """Relative phase-velocity error of the 3D Yee scheme for a wave along unit vector u in a medium, with N cells per
    wavelength in the medium and Courant number Sn = c dt / (n dx) in that medium."""
    rhs = np.sin(np.pi * Sn / N) ** 2 / Sn ** 2
    f = lambda kd: np.sum(np.sin(kd * np.asarray(u) / 2) ** 2) - rhs     # kd = k dx
    lo, hi = 1e-9, np.pi
    for _ in range(200):
        m = (lo + hi) / 2
        if f(m) < 0: lo = m
        else: hi = m
    return (2 * np.pi / N) / m - 1


def numerics_numbers():
    Smax = 1 / np.sqrt(3)
    gro = lambda S: abs((2 - 12 * S ** 2 - np.sqrt((2 - 12 * S ** 2) ** 2 - 4 + 0j)) / 2)
    Sn = 0.5 / N_SI
    dirs = {"axis": (1, 0, 0), "face": (1 / np.sqrt(2), 1 / np.sqrt(2), 0), "body": (1 / np.sqrt(3),) * 3}
    N20 = LAM / N_SI / 0.020
    return {"Smax": Smax, "g101": gro(1.01 * Smax), "g102": gro(1.02 * Smax), "Sn_si": Sn, "N_20nm": N20,
            "err_20nm": {k: vp_error(N20, u, Sn) for k, u in dirs.items()},
            "err_10": {k: vp_error(10, u, Sn) for k, u in dirs.items()},
            "err_40": {k: vp_error(40, u, Sn) for k, u in dirs.items()}}


def fig_numerics():
    nn = numerics_numbers()
    Smax = nn["Smax"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.5))
    steps = 160
    for f, col, lab in [(0.99, C1, "S = 0.99 × 1/√3"), (1.01, C4, "S = 1.01 × 1/√3")]:
        m = fdtd3d_maxfield(f * Smax, steps=steps)
        a.semilogy(np.arange(1, steps + 1), m / m[0], color=col, lw=1.3, label=lab)
    g = nn["g101"]
    n0 = 40
    nn_ = np.arange(n0, steps + 1)
    a.semilogy(nn_, 1e2 * g ** (nn_ - n0), color=INK, lw=0.7, ls="--")
    a.text(100, 1e2 * g ** (100 - n0) * 0.08, f"×{g:.3f} per step\n(theory)", fontsize=6.0, color=INK, ha="left", va="top")
    a.set_ylim(0.1, 1e14); a.set_xlim(0, steps)
    finish(a, xlabel="time step", ylabel="largest |E| (relative)")
    a.legend(loc="upper left", fontsize=6.3)
    tag(a, "a")
    Ns = np.logspace(np.log10(5), np.log10(100), 60)
    Sn = nn["Sn_si"]
    for (k, u), col, lab in zip([("axis", (1, 0, 0)), ("face", (1 / np.sqrt(2), 1 / np.sqrt(2), 0)), ("body", (1 / np.sqrt(3),) * 3)],
                                [C1, C2, C3], ["along an axis", "face diagonal", "body diagonal"]):
        e = [-vp_error(N, u, Sn) for N in Ns]
        b.loglog(Ns, e, color=col, lw=1.3, label=lab)
    b.axvline(nn["N_20nm"], color=MUTED, lw=0.7, ls=":")
    b.text(nn["N_20nm"] * 1.06, 2e-2, "20 nm cells\nin silicon", fontsize=5.9, color=MUTED, va="center")
    b.set_xlim(5, 100); b.set_ylim(1e-4, 1e-1)
    b.set_xticks([5, 10, 20, 50, 100]); b.set_xticklabels(["5", "10", "20", "50", "100"]); b.minorticks_off()
    finish(b, xlabel="cells per wavelength in the material", ylabel="phase-velocity error (too slow)")
    b.legend(loc="lower left", fontsize=6.3)
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch31_numerics")


# ------------------------------------------------------------------ Figure 31.6
def fig_pml():
    d = load("ch31_meep_pml.json")
    fig = plt.figure(figsize=(6.3, 2.55))
    a = fig.add_axes([0.06, 0.18, 0.33, 0.68])
    u = np.linspace(0, 1, 200)
    a.plot(np.concatenate([[-0.25, 0, 0], u]), np.concatenate([[0, 0, 0.55], 0.55 * np.ones_like(u)]), color=C2, lw=1.4, label="abrupt lossy block")
    a.plot(np.concatenate([[-0.25], u]), np.concatenate([[0], u ** 2]), color=C3, lw=1.4, label="graded absorber (scalar ε and μ loss)")
    a.plot(np.concatenate([[-0.25], u]), np.concatenate([[0], u ** 2]), color=C1, lw=1.4, ls=(0, (4, 2)), label="PML (stretches x only)")
    a.axvline(0, color=INK, lw=0.6)
    a.text(-0.125, 0.03, "interior", fontsize=6.1, ha="center", va="bottom", color=MUTED)
    a.text(0.62, 0.03, "boundary layer", fontsize=6.1, ha="center", va="bottom", color=MUTED)
    a.set_xlim(-0.25, 1); a.set_ylim(0, 1.32)
    a.set_xticks([0, 0.5, 1]); a.set_xticklabels(["0", "d/2", "d"]); a.set_yticks([])
    finish(a, xlabel="depth into the layer", ylabel="loss (conductivity)")
    a.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=5.9, handlelength=1.8)
    tag(a, "a")
    b = fig.add_axes([0.53, 0.18, 0.45, 0.68])
    for kind, col, lab, mk in [("block", C2, "abrupt lossy block", "o"), ("absorber", C3, "graded absorber", "s"), ("pml", C1, "PML", "D")]:
        rr = [r for r in d["kinds"][kind] if not (kind == "pml" and r["d"] >= 5.9)]
        b.semilogy([r["d"] for r in rr], [max(r["R1550"], 1e-16) for r in rr], mk + "-", color=col, ms=3, lw=1.2, label=lab)
    b.axvline(LAM / 2.848, color=MUTED, lw=0.6, ls=":")
    b.text(LAM / 2.848 + 0.05, 3e-15, "one guided\nwavelength", fontsize=5.8, color=MUTED, va="bottom")
    b.set_ylim(1e-15, 2); b.set_xlim(0, 6.2)
    finish(b, xlabel="layer thickness d (µm)", ylabel="power reflected into TE0")
    b.legend(loc="upper right", fontsize=6.2)
    tag(b, "b")
    save(fig, "ch31_pml")


# ------------------------------------------------------------------ Figure 31.7
def gauss_pulse(fc, df, t):
    """MEEP's GaussianSource: exp(-i 2 pi fc t) exp(-(t - t0)^2 / (2 w^2)), w = 1/df, t0 = 5 w."""
    w = 1 / df; t0 = 5 * w
    return np.exp(-2j * np.pi * fc * (t - t0)) * np.exp(-(t - t0) ** 2 / (2 * w ** 2))


def fig_pulse():
    d = load("ch31_meep_bragg.json")
    fig = plt.figure(figsize=(6.3, 3.3))
    # (a) top view of a few periods with the source and monitors
    a = fig.add_axes([0.0, 0.70, 1.0, 0.27])
    frameless(a, (-5.2, 5.2), (-0.9, 0.95), equal=False)
    per, w0, dw = d["period"], d["w0"], d["dw"]
    box(a, -5.2, -0.9, 10.4, 1.85, "ox", z=0)
    box(a, -5.2, -w0 / 2, 10.4, w0, "si", z=1)
    xs0 = -2.6
    for i in range(16):
        x = xs0 + i * per
        box(a, x, w0 / 2, per / 2, dw / 2, "si", z=2); box(a, x, -w0 / 2 - dw / 2, per / 2, dw / 2, "si", z=2)
        box(a, x + per / 2, w0 / 2 - dw / 2, per / 2, dw / 2, "ox", z=2); box(a, x + per / 2, -w0 / 2, per / 2, dw / 2, "ox", z=2)
    a.text(xs0 + 16 * per + 0.1, 0, "…", fontsize=9, va="center")
    for x, t, col in [(-4.6, "mode\nsource", RED), (-3.4, "reflection\nmonitor", INK), (4.4, "transmission\nmonitor", INK)]:
        a.plot([x, x], [-0.75, 0.75], color=col, lw=1.2, zorder=4)
        label(a, x + (0.12 if x < 0 else -0.12), 0.72, t, fs=5.8, col=col, ha="left" if x < 0 else "right", va="top", z=6)
    dim(a, (xs0, -0.62), (xs0 + per, -0.62), f"Λ = {1000 * per:.0f} nm", fs=5.8, text_off=(0.85, 0))
    a.text(0.0, 0.88, f"{d['n_per']} periods; width {1000 * (w0 - dw):.0f}/{1000 * (w0 + dw):.0f} nm (2D top view: core index {d['n_core']:.3f} in oxide)",
           ha="center", va="top", fontsize=5.9, color=INK)
    a.text(5.15, -0.88, "16 periods drawn, to scale", fontsize=5.6, color=MUTED, style="italic", ha="right", va="bottom")
    panel(a, "a", 0.0, 1.0)
    # (b) the source in time and its spectrum
    b = fig.add_axes([0.07, 0.11, 0.26, 0.46])
    fc, df = d["fc"], d["df"]
    t = np.linspace(0, 10 / df, 2000)
    s = gauss_pulse(fc, df, t)
    tfs = t * 1e-6 / 299792458 * 1e15          # MEEP time unit = 1 um / c
    b.plot(tfs, np.real(s), color=RED, lw=0.7)
    b.plot(tfs, np.abs(s), color=INK, lw=0.6, ls="--")
    b.set_xlim(tfs[0], tfs[-1]); b.set_yticks([-1, 0, 1])
    finish(b, xlabel="time (fs)", ylabel="source current")
    tag(b, "b")
    bi = b.inset_axes([0.62, 0.62, 0.36, 0.36])
    lam = np.linspace(1.40, 1.72, 300); f = 1 / lam
    w = 1 / df
    spec = np.exp(-((f - fc) * 2 * np.pi * w) ** 2 / 2)
    bi.plot(lam * 1000, spec, color=RED, lw=0.8)
    bi.set_xticks([1450, 1650]); bi.set_yticks([]); bi.tick_params(labelsize=5.5, length=2, pad=1)
    bi.set_title("spectrum", fontsize=5.6, pad=1); bi.grid(False)
    # (c) spectra
    c = fig.add_axes([0.43, 0.11, 0.55, 0.46])
    lamr = np.array(d["lam"]) * 1000
    c.plot(lamr, d["T"], color=C1, lw=1.3, label="transmitted (one pulsed run)")
    c.plot(lamr, d["R"], color=C2, lw=1.3, label="reflected (same run)")
    # CW runs: the value after 1600 um/c, with a bar spanning the values after 400, 800, 1200 and 1600 um/c
    cl = np.array([1000 * r["lam"] for r in d["cw"]]); cv = np.array([r["T"] for r in d["cw"]])
    lo = cv - np.array([min(r["T_at"]) for r in d["cw"]]); hi = np.array([max(r["T_at"]) for r in d["cw"]]) - cv
    c.errorbar(cl, cv, yerr=[lo, hi], fmt="o", mfc="white", mec=INK, mew=1.0, ms=5, ecolor=INK, elinewidth=0.8, capsize=2,
               label="transmitted, CW runs at one λ each")
    c.set_xlim(1480, 1620); c.set_ylim(0, 1.08)
    finish(c, xlabel="wavelength (nm)", ylabel="power")
    c.legend(loc="lower left", fontsize=5.6, handlelength=1.5, borderaxespad=0.2)
    tag(c, "c")
    save(fig, "ch31_pulse")


# ------------------------------------------------------------------ Figure 31.8
def fig_subpixel():
    d = load("ch31_meep_conv.json")
    fig = plt.figure(figsize=(6.3, 2.5))
    a = fig.add_axes([0.0, 0.08, 0.27, 0.84])
    frameless(a, (-0.2, 7.2), (-0.6, 9.6))
    R, cx, cy = 11.0, -3.2, -7.4                     # a curved wall crossing the grid
    si, ox = np.array(plt.matplotlib.colors.to_rgb(MAT["si"])), np.array(plt.matplotlib.colors.to_rgb(MAT["ox"]))
    for y0, avg, t in [(5.0, False, "staircase: each pixel all one material"), (0.0, True, "averaged: mixed pixels in between")]:
        for i in range(7):
            for j in range(4):
                xs = i + (np.arange(16) + 0.5) / 16; ys = j + (np.arange(16) + 0.5) / 16
                X, Y = np.meshgrid(xs, ys)
                f = np.mean((X - cx) ** 2 + (Y - cy) ** 2 < R ** 2) if avg else float((i + 0.5 - cx) ** 2 + (j + 0.5 - cy) ** 2 < R ** 2)
                a.add_patch(Rectangle((i, y0 + j), 1, 1, fc=si * f + ox * (1 - f), ec="white", lw=0.5, zorder=1))
        th = np.linspace(0, np.pi / 2, 400)
        xa, ya = cx + R * np.cos(th), cy + R * np.sin(th)
        m = (xa >= 0) & (xa <= 7) & (ya >= 0) & (ya <= 4)
        a.plot(xa[m], ya[m] + y0, color=RED, lw=1.2, zorder=3)
        label(a, 3.5, y0 + 4.35, t, fs=5.9)
    label(a, 0.55, 0.45, "Si", fs=6.2, bold=True, z=5); label(a, 6.4, 3.5, "SiO$_2$", fs=6.2, bold=True, z=5)
    panel(a, "a", 0.0, 1.0)
    for k, (pol, title) in enumerate([("TE", "TE0, $E$ along the film"), ("TM", "TM0, $E$ across the film")]):
        ax = fig.add_axes([0.36 + 0.33 * k, 0.17, 0.29, 0.70])
        ex = d[pol]["n_exact"]
        for avg, col, lab in [(False, C2, "staircase"), (True, C1, "subpixel averaging")]:
            rr = sorted([r for r in d["runs"] if r["pol"] == pol and r["avg"] == avg], key=lambda r: r["res"])
            ax.semilogx([r["res"] for r in rr], [r["n_eff"] for r in rr], "o-", color=col, ms=3, lw=1.1, label=lab)
        ax.axhline(ex, color=INK, lw=0.8, ls="--", label=f"exact, {ex:.4f}")
        ax.set_xticks([10, 20, 50, 100]); ax.set_xticklabels(["10", "20", "50", "100"])
        ax.set_ylim(ex - 0.16, ex + 0.16)
        finish(ax, xlabel="pixels per µm", ylabel="$n_\\mathrm{eff}$" if k == 0 else None)
        ax.set_title(title, fontsize=7, loc="left")
        if k == 0: ax.legend(loc="lower right", fontsize=6.0)
        tag(ax, "bc"[k])
    save(fig, "ch31_subpixel")


# ------------------------------------------------------------------ Figure 31.9
def fig_bend():
    d = load("ch31_meep_bend.json")
    fig = plt.figure(figsize=(6.3, 2.6))
    for k, r in enumerate(d["fields"]):
        ax = fig.add_axes([0.0 + 0.27 * k, 0.1, 0.26, 0.82])
        F = np.array(r["field_re"]).T; E = np.array(r["eps"]).T
        x0, x1, y0, y1 = r["extent"]
        ax.imshow(F, extent=(x0, x1, y0, y1), origin="lower", cmap=SIGNED_CMAP, vmin=-0.6, vmax=0.6, interpolation="bilinear", zorder=1)
        ax.contour(np.linspace(x0, x1, E.shape[1]), np.linspace(y0, y1, E.shape[0]), E, levels=[(N_I ** 2 + N_OX ** 2) / 2],
                   colors=[INK], linewidths=0.6, zorder=2)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_axis_off()
        loss = -10 * np.log10(r["T1550"])
        ax.text(0.03, 0.97, f"R = {r['R']:.0f} µm\nloss {loss:.2f} dB", transform=ax.transAxes, va="top", fontsize=6.3, color=INK,
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
        ax.plot([x1 - 1.2, x1 - 0.2], [y0 + 0.25, y0 + 0.25], color=INK, lw=1.4)
        ax.text(x1 - 0.7, y0 + 0.33, "1 µm", fontsize=5.8, ha="center", va="bottom")
        panel(ax, "ab"[k], 0.0, 1.04)
    c = fig.add_axes([0.64, 0.17, 0.34, 0.7])
    for avg, col, lab in [(False, C2, "staircase"), (True, C1, "subpixel averaging")]:
        rr = sorted([r for r in d["conv"] if r["avg"] == avg], key=lambda r: r["res"])
        c.plot([r["res"] for r in rr], [-10 * np.log10(r["T1550"]) for r in rr], "o-", color=col, ms=3, lw=1.1, label=lab)
    finish(c, xlabel="pixels per µm", ylabel="loss of the 1 µm bend (dB)")
    c.legend(loc="lower right", fontsize=6.0)
    tag(c, "c")
    save(fig, "ch31_bend")


# ------------------------------------------------------------------ Figure 31.10 and Worked Example 31.3
GC_BOX = (20.0, 16.0, 6.0)        # 3D grating coupler: x (along), y (across), z (substrate to fibre plane), um, inside PML
GC_PML = 1.0
GC_T = 300.0                       # simulated time, in units of 1 um / c (3.34 fs): about 1 ps


def cost_model():
    c = load("ch31_meep_cost.json")
    runs = c["runs"]
    # bytes per cell: slope of memory against cells over three runs; throughput: the largest run's
    bpc = c["bytes_per_cell"]
    ups = max(runs, key=lambda r: r["cells"])["updates_per_s"]
    return bpc, ups, runs


def gc_estimate(res, bpc, ups, sym=1):
    sx, sy, sz = (s + 2 * GC_PML for s in GC_BOX)
    cells = sx * res * sy * res * sz * res / sym
    dt = 0.5 / res
    steps = GC_T / dt
    return {"cells": cells, "steps": steps, "mem_GB": cells * bpc / 1e9, "core_h": cells * steps / ups / 3600}


def fig_cost():
    bpc, ups, _ = cost_model()
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.45))
    res = np.array([10, 15, 20, 25, 30, 40, 50, 60, 80, 100])
    for sym, ls, lab in [(1, "-", "3D"), (2, "--", "3D, one mirror plane")]:
        e = [gc_estimate(r, bpc, ups, sym) for r in res]
        a.loglog(res, [x["mem_GB"] for x in e], ls, color=C1, lw=1.3, label=lab)
        b.loglog(res, [x["core_h"] for x in e], ls, color=C1, lw=1.3, label=lab)
    sx, sz = GC_BOX[0] + 2 * GC_PML, GC_BOX[2] + 2 * GC_PML
    m2 = [sx * r * sz * r * bpc / 2 / 1e9 for r in res]               # 2D: half the field components, roughly
    t2 = [sx * r * sz * r * (GC_T / (0.5 / r)) / ups / 3600 for r in res]
    a.loglog(res, m2, color=C2, lw=1.2, label="2D (side view)")
    b.loglog(res, t2, color=C2, lw=1.2, label="2D (side view)")
    for ax in (a, b):
        ax.axvline(50, color=MUTED, lw=0.7, ls=":")
    a.axhline(16, color=RED, lw=0.7, ls=":"); a.text(97, 13, "16 GB: a laptop", fontsize=5.8, color=RED, va="top", ha="right")
    b.axhline(24, color=RED, lw=0.7, ls=":"); b.text(97, 19, "one core-day", fontsize=5.8, color=RED, va="top", ha="right")
    for ax in (a, b):
        ax.set_xlim(10, 100); ax.set_xticks([10, 20, 50, 100]); ax.set_xticklabels(["10", "20", "50", "100"]); ax.minorticks_off()
    a.text(52, 2e-3, "20 nm\ncells", fontsize=5.8, color=MUTED, va="bottom")
    finish(a, xlabel="pixels per µm", ylabel="memory (GB)")
    finish(b, xlabel="pixels per µm", ylabel="run time (core-hours)")
    a.legend(loc="upper left", fontsize=6.0); tag(a, "a"); tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch31_cost")


# ------------------------------------------------------------------ Figure 31.11
def fig_varfdtd():
    sw = load("ch31_fde_sweep.json")
    t, s = 0.22, sw["slabs"]["rib"]
    nI, _ = slab_te(LAM, t, N_SI, N_OX)
    nII = slab_stack_te(LAM, [(s, N_SI)], N_OX, N_OX)
    fig = plt.figure(figsize=(6.3, 2.75))
    # (a) the idea: at every point of the top view, the vertical slab mode gives an effective index
    a = fig.add_axes([0.0, 0.04, 0.45, 0.9])
    frameless(a, (0, 10), (0, 7.4), equal=False)
    # cross-section of a rib
    box(a, 0.3, 2.2, 4.6, 0.9, "ox", z=0); box(a, 0.3, 3.9, 4.6, 0.8, "oxtop", z=0)
    box(a, 0.3, 3.1, 4.6, 0.32, "si", z=1); box(a, 1.9, 3.1, 1.4, 0.8, "si", z=1)
    label(a, 2.6, 5.05, "cross-section of a rib", fs=6.2, bold=True)
    zz = np.linspace(2.2, 4.7, 100)
    for xc, tt, col in [(2.6, 0.8, RED), (0.95, 0.32, C2)]:
        prof = np.exp(-((zz - (3.1 + tt / 2)) / (0.25 + tt / 2)) ** 2)
        a.plot(xc + 0.55 * prof, zz, color=col, lw=1.0, zorder=4)
    label(a, 2.6, 1.85, f"slab I: 220 nm → $n_\\mathrm{{I}}$ = {nI:.3f}", fs=5.9, col=RED)
    label(a, 2.6, 1.45, f"slab II: {1000 * s:.0f} nm → $n_\\mathrm{{II}}$ = {nII:.3f}", fs=5.9, col=C2)
    arrow(a, (5.1, 3.5), (5.9, 3.5), col=INK, lw=1.0, ms=7)
    label(a, 5.5, 3.85, "solve each\nvertical slab", fs=5.8)
    # top view as an effective-index map (a ring and a bus guide)
    box(a, 6.0, 0.6, 3.9, 5.2, C2, z=0, alpha=0.45)
    a.add_patch(plt.matplotlib.patches.Annulus((7.95, 3.9), 1.35, 0.42, fc=RED, ec="none", alpha=0.75, zorder=1))
    box(a, 6.0, 1.45, 3.9, 0.42, RED, z=1, alpha=0.75)
    label(a, 7.95, 6.2, "top view: 2D map of\n$n_\\mathrm{I}$ (red) and $n_\\mathrm{II}$ (amber)", fs=6.0, bold=False)
    label(a, 7.95, 0.25, "→ 2D FDTD on this map", fs=5.9)
    panel(a, "a", 0.0, 1.0)
    # (b) the error of the effective-index method against width, for three etch depths
    b = fig.add_axes([0.57, 0.16, 0.41, 0.72])
    for kind, col, mk, lab in [("strip", C1, "o", "strip (etched through)"), ("rib", C2, "s", "rib, 90 nm slab"),
                               ("shallow", C3, "D", "rib, 150 nm slab")]:
        sl = sw["slabs"][kind]
        n2 = N_OX if sl is None else slab_stack_te(LAM, [(sl, N_SI)], N_OX, N_OX)
        rr = sw[kind]
        err = [lateral_tm(LAM, r["w"], nI, n2) - r["n_eff"] for r in rr]
        b.semilogy([r["w"] for r in rr], err, mk + "-", color=col, ms=3.2, lw=1.1, label=lab)
    b.set_xlim(0.25, 1.25); b.set_ylim(2e-3, 0.3)
    b.set_yticks([0.003, 0.01, 0.03, 0.1, 0.3]); b.set_yticklabels(["0.003", "0.01", "0.03", "0.1", "0.3"])
    finish(b, xlabel="width (µm)", ylabel="$n_\\mathrm{eff}$ error: effective index − 3D")
    b.legend(loc="upper right", fontsize=6.0, handlelength=1.6)
    tag(b, "b")
    save(fig, "ch31_varfdtd")


FIGS = {"landscape": fig_landscape, "fde": fig_fde, "eme": fig_eme, "yee": fig_yee, "numerics": fig_numerics,
        "pml": fig_pml, "pulse": fig_pulse, "subpixel": fig_subpixel, "bend": fig_bend, "cost": fig_cost,
        "varfdtd": fig_varfdtd}

if __name__ == "__main__":
    if sys.argv[1:] == ["numbers"]:
        nn = numerics_numbers(); print(nn)
        bpc, ups, runs = cost_model(); print("bytes/cell", bpc, "updates/s", ups)
        for r in [30, 50]:
            print(r, gc_estimate(r, bpc, ups), gc_estimate(r, bpc, ups, 2))
        sys.exit()
    for k in sys.argv[1:] or list(FIGS):
        FIGS[k]()
