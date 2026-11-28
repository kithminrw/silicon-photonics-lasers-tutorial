"""Figures for Chapter 5 (the slab waveguide). Run from the worktree root:
    python -I -X utf8 figsrc/ch05_figs.py
Writes assets/figs/ch05_rays.svg, ch05_graphical.svg, ch05_fields.svg, ch05_confinement.svg and prints every number
used in the figures and captions. Uses the exact asymmetric-slab solver slab_modes from part2_figs.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from part2_figs import slab_modes
from matplotlib.patches import Arc

N1, N2, N3, LAM = 3.476, 1.444, 1.444, 1.55
K0 = 2 * np.pi / LAM


def kgp(ne, n1=N1, n2=N2, n3=N3, lam=LAM):
    k0 = 2 * np.pi / lam
    return k0 * np.sqrt(n1**2 - ne**2), k0 * np.sqrt(ne**2 - n2**2), k0 * np.sqrt(ne**2 - n3**2)


def profile(ne, d, x, tm=False, n1=N1, n2=N2, n3=N3, lam=LAM):
    """E_y (TE) or H_y (TM) of the mode with index ne; film from x = 0 (substrate side) to x = d."""
    ka, g2, g3 = kgp(ne, n1, n2, n3, lam)
    p2 = g2 * n1**2 / n2**2 if tm else g2
    ed = np.cos(ka * d) + p2 / ka * np.sin(ka * d)
    return np.where(x < 0, np.exp(g2 * x), np.where(x <= d, np.cos(ka * x) + p2 / ka * np.sin(ka * x), ed * np.exp(-g3 * (x - d))))


def nprof(x, d, n1=N1, n2=N2, n3=N3):
    return np.where(x < 0, n2, np.where(x <= d, n1, n3))


# ------------------------------------------------------------------ Figure: ray picture
def fig_rays():
    d = 0.22
    ne = slab_modes(N1, N2, N3, d, LAM)[0]
    ka, g2, g3 = kgp(ne)
    th = np.arcsin(ne / N1)
    phi = np.arctan(g2 / ka)
    adv = d * np.tan(th)
    print(f"[rays] TE0 220 nm: n_eff {ne:.3f}, theta {np.degrees(th):.1f} deg, kappa {ka:.2f}/um, gamma {g2:.2f}/um, "
          f"1/gamma {1000/g2:.0f} nm, phi {phi:.3f} rad ({np.degrees(phi):.1f} deg), 2 kappa d {2*ka*d:.3f} rad, "
          f"2phi2+2phi3 {4*phi:.3f} rad, advance per crossing {1000*adv:.0f} nm")
    x0, x1, z0, z1 = -0.34, 0.56, -0.02, 2.62
    fig, ax = geom_axes(figsize=(6.3, 6.3 * (x1 - x0) / (z1 - z0)), xlim=(z0, z1), ylim=(x0, x1))
    box(ax, z0, x0, z1 - z0, -x0, "ox"); box(ax, z0, d, z1 - z0, x1 - d, "oxtop"); box(ax, z0, 0, z1 - z0, d, "si")
    # evanescent tails as a fading band (|E|^2 of TE0, drawn only in the claddings)
    zz = np.array([z0, 2.05])
    for xa, xb, sgn in ((x0, 0, -1), (d, x1, 1)):
        xs = np.linspace(xa, xb, 60)
        for k in range(len(xs) - 1):
            xm = 0.5 * (xs[k] + xs[k + 1]); dist = -xm if sgn < 0 else xm - d
            ax.add_patch(Rectangle((zz[0], xs[k]), zz[1] - zz[0], xs[k + 1] - xs[k], fc=AMBER, ec="none",
                                   alpha=0.38 * np.exp(-2 * g2 * dist), zorder=1.5))
    # zig-zag ray
    zs, xs, z, up = [0.08], [0.0], 0.08, True
    while z + adv < 2.0:
        z += adv; zs.append(z); xs.append(d if up else 0.0); up = not up
    ax.plot(zs, xs, color=RED, lw=1.5, zorder=4)
    for k in range(len(zs) - 1):
        zm, xm = 0.5 * (zs[k] + zs[k + 1]), 0.5 * (xs[k] + xs[k + 1])
        dz, dx = zs[k + 1] - zs[k], xs[k + 1] - xs[k]
        arrow(ax, (zm - 0.02 * dz, xm - 0.02 * dx), (zm + 0.02 * dz, xm + 0.02 * dx), col=RED, lw=1.2, ms=8, z=5)
    # wavevector triangle on the first segment
    za, zb = zs[0], zs[1]
    ax.plot([za, zb], [0, 0], color=INK, lw=0.9, ls=(0, (3, 2)), zorder=5)
    ax.plot([zb, zb], [0, d], color=INK, lw=0.9, ls=(0, (3, 2)), zorder=5)
    label(ax, (za + zb) / 2, -0.035, r"$\beta = n_\mathrm{eff}k_0$", fs=7, va="top")
    label(ax, zb + 0.02, d / 2 - 0.03, r"$\kappa$", fs=7.5, ha="left")
    label(ax, (za + zb) / 2 - 0.05, d / 2 + 0.03, r"$n_1k_0$", fs=7, ha="right", col=RED)
    # angle from the normal at a bottom reflection point
    zr = zs[2]
    ax.plot([zr, zr], [0, d * 0.98], color=INK, lw=0.7, ls=":", zorder=5)
    ax.add_patch(Arc((zr, 0), 0.22, 0.22, theta1=90 - np.degrees(th), theta2=90, color=INK, lw=0.8, zorder=6))
    label(ax, zr + 0.065, 0.135, r"$\theta$", fs=7.5, ha="left")
    # reflection phases
    for k in (3, 4):
        top = xs[k] > 0.1
        callout(ax, (zs[k], xs[k]), (zs[k] + 0.07, d + 0.13 if top else -0.12),
                (r"$-2\phi_3$ at the cover" if top else r"$-2\phi_2$ at the substrate"), fs=7)
    # material labels
    label(ax, 0.06, x1 - 0.05, r"cover, $n_3$ = 1.444 (SiO$_2$)", fs=7, ha="left", va="top")
    label(ax, 0.06, x0 + 0.035, r"substrate, $n_2$ = 1.444 (SiO$_2$)", fs=7, ha="left", va="bottom")
    label(ax, 2.31, d / 2, r"film, $n_1$ = 3.476 (Si)", fs=6.5, ha="right", va="center", bg=MAT["si"])   # left of the field axis
    # transverse field of the mode at the right end
    xf = np.linspace(x0, x1, 400)
    E = profile(ne, d, xf); E /= E.max()
    ax.plot(2.33 + 0.2 * E, xf, color=BLUE, lw=1.4, zorder=6)
    ax.plot([2.33, 2.33], [x0, x1], color=MUTED, lw=0.6, zorder=5)
    label(ax, 2.39, x1 - 0.05, r"TE$_0$ field $E_y$", fs=6.5, ha="left", va="top", col=BLUE)
    dim(ax, (2.25, d), (2.25, d + 1 / g2), "", lw=0.6)
    label(ax, 2.22, d + 0.5 / g2, r"1/$\gamma$" + f"\n{1000/g2:.0f} nm", fs=6.3, ha="right", va="center")
    label(ax, 0.62, d + 0.075, "evanescent tail", fs=6.5, col=MUTED, va="center", italic=True)
    label(ax, 0.62, -0.075, "evanescent tail", fs=6.5, col=MUTED, va="center", italic=True)
    scalebar(ax, 1.55, x0 + 0.05, 0.2, "200 nm", above=True)
    label(ax, 2.0, x1 - 0.04, "TE$_0$, $d$ = 220 nm, $\\lambda_0$ = 1550 nm\n" +
          rf"$\theta$ = {np.degrees(th):.1f}°,  $\kappa d$ = {ka*d:.2f} rad,  $\phi_2 = \phi_3$ = {phi:.2f} rad",
          fs=6.5, col=INK, va="top", ha="right")
    save(fig, "ch05_rays")


# ------------------------------------------------------------------ Figure: graphical solution of the eigenvalue equation
LABPOS = {("TE", 0.22, 0): (2.93, 0.9), ("TE", 0.30, 0): (3.06, 3.4), ("TE", 0.30, 1): (1.5, 4.6),
          ("TM", 0.22, 0): (2.15, 1.7), ("TM", 0.30, 0): (2.3, 3.45), ("TM", 0.30, 1): (1.62, 4.45)}


def fig_graphical():
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 3.0), sharey=True)
    ne = np.linspace(N2 + 1e-6, N1 - 1e-6, 2000)
    ka, g2, g3 = kgp(ne)
    for ax, tm, name in ((axs[0], False, "TE"), (axs[1], True, "TM")):
        p2 = g2 * N1**2 / N2**2 if tm else g2
        p3 = g3 * N1**2 / N3**2 if tm else g3
        rhs = np.arctan(p2 / ka) + np.arctan(p3 / ka)
        for m, ls in ((0, "-"), (1, "--")):
            ax.plot(ne, m * np.pi + rhs, ls, color=C2, lw=1.4, label=rf"$m\pi + \phi_2 + \phi_3$, $m$ = {m}")
        for d, col in ((0.22, C1), (0.30, C3)):
            ax.plot(ne, ka * d, color=col, lw=1.4, label=rf"$\kappa d$, $d$ = {1000*d:.0f} nm")
            for m, n in enumerate(slab_modes(N1, N2, N3, d, LAM, tm)):
                k_ = K0 * np.sqrt(N1**2 - n**2)
                ax.plot(n, k_ * d, "o", color=INK, ms=4, zorder=5)
                pos = LABPOS[(name, d, m)]
                ax.annotate(rf"{name}$_{m}$  {n:.3f}", (n, k_ * d), xytext=pos, textcoords="data", fontsize=6.5, color=INK,
                            ha="left", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkA=0, shrinkB=2))
                print(f"[graphical] {name}{m} at d = {1000*d:.0f} nm: n_eff {n:.4f}, kappa d {k_*d:.3f} rad")
        ax.set_xlim(N2, N1); ax.set_ylim(0, 5)
        ax.text(0.97, 0.96, name, transform=ax.transAxes, ha="right", va="top", fontsize=8.5, fontweight="bold", color=INK)
        finish(ax, r"Effective index $n_\mathrm{eff}$", "Phase (rad)" if not tm else None)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=6.8, handlelength=1.8, bbox_to_anchor=(0.5, 0.0))
    tag(axs[0], "a"); tag(axs[1], "b"); fig.tight_layout(w_pad=1.5, rect=(0, 0.08, 1, 1))
    save(fig, "ch05_graphical")


# ------------------------------------------------------------------ Figure: field profiles over the layer stack
def power_norm_te(ne, d, x):
    E = profile(ne, d, x)
    return E / np.sqrt(np.trapezoid(E**2, x) * ne)          # E_y^2 = psi^2 / (n_eff int psi^2)  (2 Z0 P = 1)


def power_norm_tm_ex(ne, d, x):
    H = profile(ne, d, x, tm=True); n = nprof(x, d)
    return np.sqrt(ne) * H / n**2 / np.sqrt(np.trapezoid(H**2 / n**2, x))   # E_x = beta H_y / (omega eps0 n^2)


def fig_fields():
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 3.0), sharey=False)
    cases = [(axs[0], 0.22, [("TE", 0, C1, "-"), ("TM", 0, C2, "-")]), (axs[1], 0.30, [("TE", 0, C1, "-"), ("TE", 1, C3, "-")])]
    ref = None
    for ax, d, ms in cases:
        x = np.linspace(-0.6 + d / 2, 0.6 + d / 2, 4801)
        xc = x - d / 2
        ax.axhspan(-0.6, -d / 2, color=MAT["ox"], lw=0, zorder=0); ax.axhspan(d / 2, 0.6, color=MAT["oxtop"], lw=0, zorder=0)
        ax.axhspan(-d / 2, d / 2, color=MAT["si"], lw=0, zorder=0, alpha=0.85)
        for pol, m, col, ls in ms:
            ne = slab_modes(N1, N2, N3, d, LAM, pol == "TM")[m]
            f = power_norm_tm_ex(ne, d, x) if pol == "TM" else power_norm_te(ne, d, x)
            if ref is None: ref = np.abs(f).max()
            f = f / ref
            if pol == "TM":       # draw the jumps as breaks
                for msk in (x < 0, (x >= 0) & (x <= d), x > d):
                    ax.plot(f[msk], xc[msk], color=col, ls=ls, lw=1.6, label=None)
                ax.plot([], [], color=col, lw=1.6, label=rf"TM$_{m}$  $E_x$, $n_\mathrm{{eff}}$ = {ne:.3f}")
                k = np.argmin(np.abs(x - d)); jin, jout = f[k - 1], f[k + 1]
                print(f"[fields] TM0 220 nm: E_x just inside {jin:.3f}, just outside {jout:.3f}, ratio {jout/jin:.2f} (n1^2/n2^2 = {N1**2/N2**2:.2f})")
                ax.annotate("", xy=(jout, d / 2), xytext=(jin, d / 2), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.8, mutation_scale=6))
                ax.text(jout + 0.03, d / 2 + 0.035, r"jump $\times(n_1/n_2)^2$" + f" = {N1**2/N2**2:.1f}", fontsize=6.5, color=col, ha="left", va="bottom")
            else:
                ax.plot(f, xc, color=col, ls=ls, lw=1.6, label=rf"TE$_{m}$  $E_y$, $n_\mathrm{{eff}}$ = {ne:.3f}")
                g = K0 * np.sqrt(ne**2 - N2**2)
                print(f"[fields] {pol}{m} at d = {1000*d:.0f} nm: n_eff {ne:.4f}, 1/gamma {1000/g:.0f} nm")
        ax.axvline(0, color=MUTED, lw=0.6)
        ax.set_ylim(-0.6, 0.6); ax.set_xlim(-1.25, 1.85)
        ax.set_yticks(np.arange(-0.6, 0.61, 0.2)); ax.set_yticklabels([f"{1000*v:.0f}" for v in np.arange(-0.6, 0.61, 0.2)])
        ax.text(-1.2, -0.56, "SiO$_2$", fontsize=7, color=INK, va="bottom")
        ax.text(-1.2, 0.56, "SiO$_2$", fontsize=7, color=INK, va="top")
        ax.text(-1.2, 0.0, f"Si\n{1000*d:.0f} nm", fontsize=7, color=INK, va="center")
        ax.grid(False)
        ax.legend(loc="lower right", fontsize=6.5, frameon=True, framealpha=0.9, edgecolor="none", handlelength=1.4)
        finish(ax, "Field (equal power)", "Position across the film (nm)" if d < 0.25 else None)
    tag(axs[0], "a"); tag(axs[1], "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch05_fields")


# ------------------------------------------------------------------ Figure: confinement factor and decay length against thickness
def gamma_conf(d, tm=False, n1=N1, n2=N2, lam=LAM):
    ms = slab_modes(n1, n2, n2, d, lam, tm)
    if not ms: return np.nan, np.nan, np.nan
    ne = ms[0]; k0 = 2 * np.pi / lam; g = k0 * np.sqrt(ne**2 - n2**2)
    span = max(12 / g, 1.0)
    x = np.linspace(-span, d + span, 40001)
    f = profile(ne, d, x, tm, n1, n2, n2, lam)
    w = f**2 / nprof(x, d, n1, n2, n2)**2 if tm else f**2          # power density: E_y^2 (TE), H_y^2/n^2 (TM)
    inside = (x >= 0) & (x <= d)
    return ne, 1 / g, np.trapezoid(w * inside, x) / np.trapezoid(w, x)


def fig_confinement():
    ds = np.linspace(0.02, 1.0, 197)
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    for tm, col, name in ((False, C1, "TE$_0$"), (True, C2, "TM$_0$")):
        res = np.array([gamma_conf(d, tm) for d in ds])
        a.plot(1000 * ds, res[:, 2], color=col, label=name)
        b.plot(1000 * ds, 1000 * res[:, 1], color=col, label=name)
        ne, dl, G = gamma_conf(0.22, tm)
        a.plot(220, G, "o", color=col, ms=4); b.plot(220, 1000 * dl, "o", color=col, ms=4)
        print(f"[confinement] {'TM0' if tm else 'TE0'} 220 nm: n_eff {ne:.4f}, 1/gamma {1000*dl:.0f} nm, Gamma {G:.3f}")
        for d in (0.1, 0.4, 0.6):
            ne, dl, G = gamma_conf(d, tm)
            print(f"    d = {1000*d:.0f} nm: Gamma {G:.3f}, 1/gamma {1000*dl:.0f} nm")
    gte = np.array([gamma_conf(d)[2] for d in ds]); gtm = np.array([gamma_conf(d, True)[2] for d in ds])
    k = np.where((gtm > gte) & (ds > 0.1))[0][0]
    print(f"[confinement] TM power fraction exceeds TE above d = {1000*ds[k]:.0f} nm")
    _, dlte, Gte = gamma_conf(0.22); _, dltm, Gtm = gamma_conf(0.22, True)
    a.annotate(f"{Gte:.2f}", (220, Gte), xytext=(8, -12), textcoords="offset points", fontsize=7, color=C1)
    a.annotate(f"{Gtm:.2f}", (220, Gtm), xytext=(8, -12), textcoords="offset points", fontsize=7, color=C2)
    b.annotate(f"{1000*dlte:.0f} nm", (220, 1000 * dlte), xytext=(4, -13), textcoords="offset points", fontsize=7, color=C1)
    b.annotate(f"{1000*dltm:.0f} nm", (220, 1000 * dltm), xytext=(8, 2), textcoords="offset points", fontsize=7, color=C2)
    for ax in (a, b): ax.axvline(220, color=MUTED, lw=0.7, ls=":"); ax.set_xlim(0, 1000)
    a.set_ylim(0, 1)
    b.set_yscale("log"); b.set_ylim(50, 3000)
    b.set_yticks([50, 100, 200, 500, 1000, 2000]); b.set_yticklabels(["50", "100", "200", "500", "1000", "2000"])
    finish(a, "Silicon thickness d (nm)", r"Confinement factor $\Gamma$", legend=True, loc="lower right")
    finish(b, "Silicon thickness d (nm)", r"Decay length 1/$\gamma$ (nm)", legend=True, loc="upper right")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.5)
    save(fig, "ch05_confinement")


if __name__ == "__main__":
    fig_rays(); fig_graphical(); fig_fields(); fig_confinement()
