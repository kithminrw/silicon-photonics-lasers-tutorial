"""Figures for Chapter 6 (channel waveguides). Run from the worktree root:
    python -I -X utf8 figsrc/ch06_figs.py [geometries eim fields sensitivity]
Writes assets/figs/ch06_geometries.svg, ch06_eim.svg, ch06_fields.svg, ch06_sensitivity.svg and prints every number
used in the figures and captions. Femwell data: figsrc/ch06_sweep.json (width sweep, from ch06_sweep.py) and
figsrc/ch06_fields.json (from `ch06_fields.py fields`, run in the photonics-labs container). The thickness
sensitivity uses the femwell value quoted in Section 6.7 at 500 nm and the effective-index method for the trend
(the femwell thickness sweep `ch06_fields.py tsweep` was not run: the shared container was overloaded).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from part2_figs import slab_modes

N_SI, N_OX, LAM = 3.476, 1.444, 1.55
K0 = 2 * np.pi / LAM
HERE = os.path.dirname(os.path.abspath(__file__))


def xsec_bg(ax, x0, x1, y0, y1):
    box(ax, x0, y0, x1 - x0, -y0, "ox", z=0); box(ax, x0, 0, x1 - x0, y1, "oxtop", z=0)


# ------------------------------------------------------------------ Figure: geometries to scale
def fig_geometries():
    fig = plt.figure(figsize=(6.3, 3.5))
    X0, X1, Y0, Y1 = -1.0, 1.0, -0.45, 0.62
    axs = [fig.add_axes([0.0, 0.5, 0.49, 0.48]), fig.add_axes([0.51, 0.5, 0.49, 0.48]),
           fig.add_axes([0.0, 0.0, 0.49, 0.48]), fig.add_axes([0.51, 0.0, 0.49, 0.48])]
    for ax in axs: frameless(ax, (X0, X1), (Y0, Y1))
    # (a) strip
    ax = axs[0]; xsec_bg(ax, X0, X1, Y0, Y1); box(ax, -0.25, 0, 0.5, 0.22, "si", z=2)
    dim(ax, (-0.25, 0.32), (0.25, 0.32), "500 nm"); dim(ax, (0.36, 0), (0.36, 0.22), "")
    label(ax, 0.40, 0.11, "220 nm", fs=FS_SMALL, ha="left")
    label(ax, 0, 0.53, "Strip", fs=7.5, bold=True)
    label(ax, X0 + 0.04, -0.4, "buried oxide", fs=FS_SMALL, ha="left", va="bottom")
    label(ax, X0 + 0.16, Y1 - 0.04, "oxide cladding", fs=FS_SMALL, ha="left", va="top")
    panel(ax, "a", 0.0, 1.0)
    # (b) rib
    ax = axs[1]; xsec_bg(ax, X0, X1, Y0, Y1); box(ax, X0, 0, X1 - X0, 0.09, "si", z=2); box(ax, -0.25, 0, 0.5, 0.22, "si", z=2)
    dim(ax, (-0.25, 0.32), (0.25, 0.32), "500 nm"); dim(ax, (0.36, 0), (0.36, 0.22), "")
    label(ax, 0.40, 0.155, "220 nm", fs=FS_SMALL, ha="left")
    dim(ax, (-0.62, 0), (-0.62, 0.09), ""); label(ax, -0.66, 0.045, "90 nm slab", fs=FS_SMALL, ha="right")
    label(ax, 0, 0.53, "Rib", fs=7.5, bold=True)
    panel(ax, "b", 0.0, 1.0)
    # (c) slot
    ax = axs[2]; xsec_bg(ax, X0, X1, Y0, Y1)
    box(ax, -0.30, 0, 0.25, 0.22, "si", z=2); box(ax, 0.05, 0, 0.25, 0.22, "si", z=2)
    dim(ax, (-0.30, 0.32), (-0.05, 0.32), ""); label(ax, -0.33, 0.32, "250 nm", fs=FS_SMALL, ha="right")
    dim(ax, (-0.05, -0.08), (0.05, -0.08), ""); label(ax, 0.0, -0.17, "100 nm gap", fs=FS_SMALL)
    dim(ax, (0.41, 0), (0.41, 0.22), ""); label(ax, 0.45, 0.11, "220 nm", fs=FS_SMALL, ha="left")
    label(ax, 0, 0.53, "Slot", fs=7.5, bold=True)
    scalebar(ax, 0.45, -0.38, 0.5, "500 nm", above=True)
    panel(ax, "c", 0.0, 1.0)
    # (d) subwavelength grating, top view
    ax = axs[3]; box(ax, X0, Y0, X1 - X0, Y1 - Y0, "oxtop", z=0)
    yc = 0.05
    box(ax, X0, yc - 0.25, 0.55, 0.5, "si", z=2)
    period, seg = 0.2, 0.1
    xs = np.arange(X0 + 0.55 + 0.05, X1, period)
    for x in xs: box(ax, x, yc - 0.25, seg, 0.5, "si", z=2)
    dim(ax, (xs[2], yc + 0.33), (xs[3], yc + 0.33), ""); label(ax, xs[3] + 0.04, yc + 0.33, r"period $\Lambda$ = 200 nm", fs=FS_SMALL, ha="left")
    dim(ax, (xs[5], yc - 0.33), (xs[5] + seg, yc - 0.33), ""); label(ax, xs[5] + seg + 0.03, yc - 0.33, "100 nm", fs=FS_SMALL, ha="left")
    arrow(ax, (X0 + 0.05, yc), (X0 + 0.42, yc), col=RED, lw=1.1, ms=7)
    label(ax, 0, 0.53, "Subwavelength grating (top view)", fs=7.5, bold=True)
    panel(ax, "d", 0.0, 1.0)
    note(ax, "slot and SWG dimensions illustrative", loc="lower right")
    save(fig, "ch06_geometries")
    print("[geometries] Bragg period of a 500 nm strip at 1550 nm: lambda/(2 n_eff) =", round(1000 * 1.55 / (2 * 2.446)), "nm")


# ------------------------------------------------------------------ Figure: effective-index method, step by step (rib)
def slab_field(n1, n2, d, lam, tm, x):
    ne = slab_modes(n1, n2, n2, d, lam, tm)[0]; k0 = 2 * np.pi / lam
    ka, g = k0 * np.sqrt(n1**2 - ne**2), k0 * np.sqrt(ne**2 - n2**2)
    xc = x - d / 2
    return ne, np.where(np.abs(xc) <= d / 2, np.cos(ka * xc), np.cos(ka * d / 2) * np.exp(-g * (np.abs(xc) - d / 2)))


def fig_eim():
    t, s, W = 0.22, 0.09, 0.5
    nI = slab_modes(N_SI, N_OX, N_OX, t, LAM)[0]
    nII = slab_modes(N_SI, N_OX, N_OX, s, LAM)[0]
    ne = slab_modes(nI, nII, nII, W, LAM, tm=True)[0]
    ne_strip = slab_modes(nI, N_OX, N_OX, W, LAM, tm=True)[0]
    print(f"[eim] rib 500/220/90: n_I {nI:.4f}, n_II {nII:.4f}, EIM n_eff {ne:.4f} (femwell 2.568); strip: {ne_strip:.4f} (femwell 2.446)")
    fig = plt.figure(figsize=(6.3, 3.6))
    # (a) cross-section to scale, regions I and II
    ax = fig.add_axes([0.0, 0.56, 1.0, 0.43]); frameless(ax, (-1.6, 1.6), (-0.32, 0.52))
    xsec_bg(ax, -1.6, 1.6, -0.32, 0.52)
    box(ax, -1.6, 0, 3.2, s, "si", z=2); box(ax, -W / 2, 0, W, t, "si", z=2)
    for x in (-W / 2, W / 2): ax.plot([x, x], [-0.3, 0.5], color=INK, lw=0.7, ls=(0, (3, 2)), zorder=4)
    label(ax, 0, 0.40, "region I\nfilm $t$ = 220 nm", fs=6.8)
    label(ax, -0.95, 0.42, "region II: slab $s$ = 90 nm", fs=6.8); label(ax, 0.95, 0.42, "region II", fs=6.8)
    dim(ax, (-W / 2, -0.12), (W / 2, -0.12), "")
    label(ax, 0, -0.21, "$W$ = 500 nm", fs=6.8)
    scalebar(ax, 1.0, -0.26, 0.5, "500 nm", above=True)
    panel(ax, "a", 0.0, 1.0)
    # (b) step 1: vertical slabs
    b = fig.add_axes([0.08, 0.08, 0.38, 0.38])
    y = np.linspace(-0.4, 0.62, 800)
    _, fI = slab_field(N_SI, N_OX, t, LAM, False, y)
    _, fII = slab_field(N_SI, N_OX, s, LAM, False, y)
    b.axhspan(0, t, color=MAT["si"], alpha=0.35, lw=0); b.axhspan(0, s, color=MAT["si"], alpha=0.5, lw=0)
    b.plot(fI, y, color=C1, label=rf"I: $n_\mathrm{{I}}$ = {nI:.3f}")
    b.plot(fII, y, color=C2, label=rf"II: $n_\mathrm{{II}}$ = {nII:.3f}")
    b.set_ylim(-0.4, 0.62); b.set_xlim(0, 1.6)
    b.set_yticks([0, 0.09, 0.22]); b.set_yticklabels(["0", "90", "220"])
    finish(b, r"Field $E_x$ (TE slabs)", "Height (nm)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.5)
    tag(b, "b")
    # (c) step 2: lateral slab with TM boundary conditions
    c = fig.add_axes([0.6, 0.08, 0.38, 0.38])
    x = np.linspace(-1.2, 1.2, 1200)
    ka, g = K0 * np.sqrt(nI**2 - ne**2), K0 * np.sqrt(ne**2 - nII**2)
    H = np.where(np.abs(x) <= W / 2, np.cos(ka * x), np.cos(ka * W / 2) * np.exp(-g * (np.abs(x) - W / 2)))
    nprof = np.where(np.abs(x) <= W / 2, nI, nII)
    c2 = c.twinx()
    c2.plot(x, nprof, color=MUTED, lw=1.0, ls="--"); c2.set_ylim(1.4, 3.6); c2.set_ylabel("Index", color=MUTED)
    c2.tick_params(axis="y", colors=MUTED); c2.spines["right"].set_visible(True); c2.spines["right"].set_color(MUTED); c2.grid(False)
    c.plot(x, H, color=C1)
    c.text(0.36, 0.85, rf"$n_\mathrm{{eff}}$ = {ne:.3f}", fontsize=7, color=C1, ha="left")
    c.set_xlim(-1.2, 1.2); c.set_ylim(0, 1.6)
    c.text(0.0, 1.45, r"$n_\mathrm{I}$", ha="center", fontsize=7, color=MUTED)
    c.text(-0.85, 1.45, r"$n_\mathrm{II}$", ha="center", fontsize=7, color=MUTED); c.text(0.85, 1.45, r"$n_\mathrm{II}$", ha="center", fontsize=7, color=MUTED)
    finish(c, "Lateral position (µm)", r"Field $H_y$ (TM slab)")
    tag(c, "c")
    save(fig, "ch06_eim")


# ------------------------------------------------------------------ Figure: full-vectorial mode fields (femwell)
def fig_fields():
    p = os.path.join(HERE, "ch06_fields.json")
    if not os.path.exists(p): print("[fields] no ch06_fields.json yet"); return
    S = json.load(open(p))
    gx = np.linspace(*S["grid"]["x"]); gy = np.linspace(*S["grid"]["y"])
    cases = [("a", "strip TE$_0$", S["strip"]["te"], gx, [(-0.25, 0.25)], False),
             ("b", "strip TM$_0$", S["strip"]["tm"], gx, [(-0.25, 0.25)], False)]
    if "rib" in S: cases.append(("c", "rib TE$_0$", S["rib"], np.linspace(*S["rib"]["grid"]["x"]), [(-0.25, 0.25)], True))
    if "slot" in S: cases.append(("d", "slot TE$_0$", S["slot"], gx, [(-0.30, -0.05), (0.05, 0.30)], False))
    if len(cases) > 2:
        fig = plt.figure(figsize=(6.3, 3.9))
        pos = [[0.0, 0.5, 0.49, 0.47], [0.51, 0.5, 0.49, 0.47], [0.0, 0.0, 0.49, 0.47], [0.51, 0.0, 0.49, 0.47]]
    else:
        fig = plt.figure(figsize=(6.3, 1.95))
        pos = [[0.0, 0.0, 0.49, 0.94], [0.51, 0.0, 0.49, 0.94]]
    for (t_, name, d, xg, cores, rib), ps in zip(cases, pos):
        ax = fig.add_axes(ps)
        I = np.array(d["I"], float).reshape(len(gy), len(xg)) / 999
        ax.imshow(I, extent=(xg[0], xg[-1], gy[0], gy[-1]), origin="lower", cmap=FIELD_CMAP, vmin=0, vmax=1, interpolation="bilinear", zorder=1)
        for x0, x1 in cores:
            ax.add_patch(Rectangle((x0, 0), x1 - x0, 0.22, fc="none", ec=INK, lw=0.8, zorder=3))
        if rib:
            ax.plot([xg[0], -0.25], [0.09, 0.09], color=INK, lw=0.8, zorder=3); ax.plot([0.25, xg[-1]], [0.09, 0.09], color=INK, lw=0.8, zorder=3)
            ax.plot([xg[0], xg[-1]], [0, 0], color=INK, lw=0.8, zorder=3)
        frameless(ax, (-0.85, 0.85), (-0.42, 0.66))
        ax.text(-0.82, 0.63, f"{name}\n$n_\\mathrm{{eff}}$ = {d['neff']:.3f}", fontsize=7, color=INK, va="top", ha="left", zorder=5)
        ax.text(0.97 if t_ != "a" else -0.97, gy[0] + 0.04, "", fontsize=6)
        panel(ax, t_, 0.93, 1.0)
        print(f"[fields] {name}: n_eff {d['neff']:.4f}")
    ax = fig.axes[2] if len(cases) > 2 else fig.axes[0]
    scalebar(ax, 0.25, -0.38, 0.5, "500 nm", above=True)
    if "slot" in S:
        sl = S["slot"]; xl = np.array(sl["xl"]); ex = np.array(sl["ex_line"])
        gapmax = np.abs(ex[np.abs(xl) < 0.04]).max(); railmax = np.abs(ex[(np.abs(xl) > 0.06) & (np.abs(xl) < 0.29)]).max()
        print(f"[fields] slot: E_x in the gap / max E_x in the rails = {gapmax/railmax:.2f} (n_Si^2/n_ox^2 = {N_SI**2/N_OX**2:.2f})")
    print(f"[fields] strip Ez/|E| max: TE {S['strip']['te']['ez_frac']:.2f}, TM {S['strip']['tm']['ez_frac']:.2f}")
    save(fig, "ch06_fields")


# ------------------------------------------------------------------ Figure: fabrication sensitivity
def fig_sensitivity():
    S = json.load(open(os.path.join(HERE, "ch06_sweep.json")))
    W = np.array(S["widths"])
    te = np.array([max(n for n, f in ms if f > 0.5) for ms in S["neff1550"]])
    tm = np.array([max(n for n, f in ms if f <= 0.5) for ms in S["neff1550"]])
    ng = np.array(S["ng_te1550"])
    dW_te = np.gradient(te, W * 1000); dW_tm = np.gradient(tm, W * 1000)      # per nm
    i5 = np.argmin(np.abs(W - 0.5))
    print(f"[sensitivity] dn/dW at 500 nm: TE {dW_te[i5]:.2e}/nm, TM {dW_tm[i5]:.2e}/nm; ring shift per nm of width (TE) "
          f"{1550*dW_te[i5]/ng[i5]:.2f} nm; at 1 um {1550*dW_te[-1]/ng[-1]:.2f} nm")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    a.plot(W, 1e3 * dW_te, "o-", color=C1, ms=2.5, label="TE$_0$, width (femwell)")
    a.plot(W, 1e3 * dW_tm, "o-", color=C2, ms=2.5, label="TM$_0$, width (femwell)")
    b.plot(W, 1550 * dW_te / ng, "o-", color=C1, ms=2.5, label="width error (femwell)")
    # thickness: the femwell value of Section 6.7 at 500 nm, and the trend against width from the effective-index method
    def eim(Wd, t):
        nI = slab_modes(N_SI, N_OX, N_OX, t, LAM)[0]
        return slab_modes(nI, N_OX, N_OX, Wd, LAM, tm=True)[0]
    We = np.linspace(0.3, 1.0, 29)
    dt_eim = np.array([(eim(w, 0.225) - eim(w, 0.215)) / 10 for w in We])
    dt_fw = 3.7e-3                                                     # femwell, Chapter 6 text (Section 6.7)
    a.plot(We, 1e3 * dt_eim, "--", color=C3, label="TE$_0$, thickness (EIM)")
    a.plot(0.5, 1e3 * dt_fw, "s", color=C3, ms=4.5, label="TE$_0$, thickness (femwell)")
    b.plot(We, 1550 * dt_eim / np.interp(We, W, ng), "--", color=C3, label="thickness error (EIM)")
    b.plot(0.5, 1550 * dt_fw / ng[i5], "s", color=C3, ms=4.5, label="thickness error (femwell)")
    print(f"[sensitivity] thickness: femwell 3.7e-3/nm at 500 nm -> ring shift {1550*dt_fw/ng[i5]:.2f} nm per nm; "
          f"EIM dn/dt at 0.3/0.5/1.0 um: {dt_eim[0]:.2e} {np.interp(0.5, We, dt_eim):.2e} {dt_eim[-1]:.2e}")
    for ax in (a, b): ax.axvline(0.5, color=MUTED, lw=0.6, ls=":"); ax.set_xlim(0.25, 1.0)
    a.set_ylim(0, 6); b.set_ylim(0, 2.5)
    finish(a, "Width (µm)", r"d$n_\mathrm{eff}$/d$x$ ($10^{-3}$ per nm)", legend=True, loc="upper right")
    a.legend(loc="upper right", fontsize=6.3)
    finish(b, "Width (µm)", "Ring resonance shift per nm (nm)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.3)
    b.text(0.27, 0.12, "TE$_0$, 1550 nm", fontsize=7, color=INK, va="bottom")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch06_sensitivity")


if __name__ == "__main__":
    which = sys.argv[1:] or ["geometries", "eim", "fields", "sensitivity"]
    for w in which:
        globals()["fig_" + w]()
