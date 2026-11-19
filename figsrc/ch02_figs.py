"""Figures for Chapter 2 (electromagnetic theory).

Run from the repository root:   python -I -X utf8 figsrc/ch02_figs.py
Writes assets/figs/ch02_planewave.svg, ch02_sp.svg, ch02_tir.svg and prints the numbers they show.
Indices are the chapter's values at 1550 nm (Table 2.1 and Worked Example 2.4).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402

LAM = 1.55
N_SI, N_OX, N_SIN, N_AIR = 3.476, 1.444, 1.996, 1.0
NEFF_SLAB = 2.848            # TE0 of the 220 nm slab (Chapter 5)


def fresnel(n1, n2, th):
    """Complex r_s, r_p (chapter's convention) at incidence angle th (rad); evanescent branch decays (e^{jwt})."""
    s2 = (n1 / n2 * np.sin(th)) ** 2
    c2 = np.sqrt(1 - s2 + 0j)
    c2 = np.where(s2 > 1, -1j * np.sqrt(s2 - 1), c2)
    c1 = np.cos(th)
    rs = (n1 * c1 - n2 * c2) / (n1 * c1 + n2 * c2)
    rp = (n2 * c1 - n1 * c2) / (n2 * c1 + n1 * c2)
    return rs, rp


def decay_nm(n1, n2, th):
    return 1e3 / (2 * np.pi / LAM * np.sqrt(np.maximum((n1 * np.sin(th)) ** 2 - n2 ** 2, 1e-12)))


# ------------------------------------------------------------------ Figure: a plane wave
def fig_planewave():
    fig = plt.figure(figsize=(6.3, 3.9))
    a = fig.add_axes([0.0, 0.40, 1.0, 0.60])
    frameless(a, xlim=(-1.0, 10.4), ylim=(-2.05, 2.05))
    # oblique projection: z to the right, x up, y towards the reader (down and to the left)
    P = lambda x, y, z: (z - 0.3 * y, x - 0.45 * y)
    L = 4.3                                         # drawn wavelength
    z = np.linspace(0, 2 * L, 400)
    E = 1.45 * np.cos(2 * np.pi * z / L); H = 1.25 * np.cos(2 * np.pi * z / L)
    # axes
    for p0, p1, t, off in (((0, 0, 0), (1.85, 0, 0), "$x$", (0.0, 0.12)), ((0, 0, 0), (0, 2.1, 0), "$y$", (-0.15, -0.1)),
                           ((0, 0, -0.4), (0, 0, 2 * L + 1.4), "$z$", (0.15, 0.0))):
        arrow(a, P(*p0), P(*p1), col=MUTED, lw=0.7, ms=7)
        q = P(*p1); label(a, q[0] + off[0], q[1] + off[1], t, col=MUTED, fs=8)
    # E (in the x-z plane) and H (in the y-z plane), with arrows from the axis
    a.plot(*P(E, 0 * z, z), color=C1, lw=1.6, zorder=5)
    a.plot(*P(0 * z, H, z), color=C2, lw=1.6, zorder=4)
    for zz in np.arange(0, 2 * L + 1e-9, L / 8):
        e = 1.45 * np.cos(2 * np.pi * zz / L)
        if abs(e) > 0.15:
            arrow(a, P(0, 0, zz), P(e, 0, zz), col=C1, lw=0.8, ms=5, z=5)
            arrow(a, P(0, 0, zz), P(0, e * 1.25 / 1.45, zz), col=C2, lw=0.8, ms=5, z=4)
    label(a, *np.add(P(1.45, 0, 0), (0.25, 0.1)), "$\\mathbf{E}$", col=C1, fs=10)
    label(a, *np.add(P(0, 1.25, 0), (-0.3, -0.05)), "$\\mathbf{H}$", col=C2, fs=10)
    # k and the wavelength
    arrow(a, P(0, 0, 2 * L + 0.2), P(0, 0, 2 * L + 1.3), col=INK, lw=1.8, ms=10, z=6)
    label(a, *np.add(P(0, 0, 2 * L + 0.8), (0, 0.3)), "$\\mathbf{k}$", col=INK, fs=10)
    dim(a, P(1.75, 0, 0), P(1.75, 0, L), "$\\lambda = \\lambda_0/n$", fs=7.5)
    label(a, 9.95, -1.55, "$\\mathbf{E} \\perp \\mathbf{H} \\perp \\mathbf{k}$,  $|\\mathbf{E}|/|\\mathbf{H}| = \\eta_0/n$\n"
          "power flows along $\\mathbf{S} = \\mathbf{E}\\times\\mathbf{H}$", fs=7.0, ha="right", va="center")
    panel(a, "a", 0.0, 0.98)
    # (b) one frequency in three materials, equal intensity
    b = fig.add_axes([0.075, 0.08, 0.89, 0.30])
    zz = np.linspace(0, 3.1, 1200)
    rows = [("air", N_AIR, MUTED), ("silica", N_OX, C2), ("silicon", N_SI, C1)]
    print("plane wave at 1550 nm:")
    for i, (name, n, col) in enumerate(rows):
        y0 = 2 - i
        amp = 0.36 / np.sqrt(n)                     # equal intensity: |E| ∝ 1/sqrt(n)
        b.plot(zz, y0 + amp * np.cos(2 * np.pi * n * zz / LAM), color=col, lw=1.3)
        b.axhline(y0, color=GRID, lw=0.6, zorder=0)
        lam_m = 1e3 * LAM / n
        b.text(-0.04, y0, f"{name}\n$n$ = {n:g}", ha="right", va="center", fontsize=7, color=INK)
        b.annotate("", (LAM / n, y0 + 0.5), (0, y0 + 0.5),
                   arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
        b.text(LAM / n + 0.04, y0 + 0.5, f"{lam_m:.0f} nm", ha="left", va="center", fontsize=6.8, color=col)
        print(f"  {name}: n = {n}, wavelength {lam_m:.0f} nm, relative field for equal intensity {1/np.sqrt(n):.3f}")
    b.set_xlim(0, 3.1); b.set_ylim(-0.6, 2.75)
    b.set_yticks([]); b.grid(False)
    for s in ("left",): b.spines[s].set_visible(False)
    b.set_xlabel("Position $z$ (µm)", labelpad=1)
    b.text(3.1, -0.55, "193.4 THz in every material", ha="right", va="bottom", fontsize=6.8, color=MUTED)
    print("  frequency %.1f THz" % (299792.458 / 1550))
    tag(b, "b")
    save(fig, "ch02_planewave")


# ------------------------------------------------------------------ Figure: s and p at an interface
def fig_sp():
    th1 = np.radians(15.0)
    th2 = np.arcsin(N_SI * np.sin(th1) / N_OX)
    rs, rp = fresnel(N_SI, N_OX, th1)
    Rs, Rp = abs(rs) ** 2, abs(rp) ** 2
    thb = np.degrees(np.arctan(N_OX / N_SI))
    print("s/p at 15° from Si into SiO2: refraction angle %.1f°, R_s %.3f, R_p %.3f; Brewster %.1f°" %
          (np.degrees(th2), Rs, Rp, thb))
    fig = plt.figure(figsize=(6.3, 2.75))
    for k, pol in enumerate(("s", "p")):
        ax = fig.add_axes([0.0 + 0.5 * k, 0.0, 0.5, 1.0])
        frameless(ax, xlim=(-2.25, 2.25), ylim=(-1.85, 2.05))
        box(ax, -2.25, 0, 4.5, 2.05, "si", alpha=0.35)
        box(ax, -2.25, -1.85, 4.5, 1.85, "ox")
        ax.plot([0, 0], [-1.75, 1.75], color=MUTED, lw=0.6, ls=(0, (3, 3)))
        Lr = 1.55
        u_in = np.array([np.sin(th1), -np.cos(th1)])           # direction of travel
        u_rf = np.array([np.sin(th1), np.cos(th1)])
        u_tr = np.array([np.sin(th2), -np.cos(th2)])
        rays = [(-Lr * u_in, np.zeros(2), u_in, 1.0, "incident"), (np.zeros(2), Lr * u_rf, u_rf, np.sqrt(Rs if pol == "s" else Rp), "reflected"),
                (np.zeros(2), Lr * u_tr, u_tr, 1.0, "transmitted")]
        for p0, p1, u, amp, name in rays:
            arrow(ax, tuple(p0), tuple(p1), col=RED, lw=1.3, ms=9, z=5)
            # field markers at two points along each ray
            for f in (0.38, 0.72):
                c = p0 + f * (p1 - p0)
                if pol == "s":
                    ax.plot(*c, "o", ms=6.5, mfc="white", mec=C1, mew=1.0, zorder=7)
                    ax.plot(*c, ".", ms=3.0, color=C1, zorder=8)
                else:
                    nrm = np.array([-u[1], u[0]]) * 0.24 * max(amp, 0.45)
                    arrow(ax, tuple(c - nrm), tuple(c + nrm), col=C1, lw=1.0, ms=6, style="<|-|>", z=7)
        label(ax, -1.95, 1.8, f"Si, $n_1$ = {N_SI}", fs=7, ha="left", va="top")
        label(ax, -1.95, -1.6, f"SiO$_2$, $n_2$ = {N_OX}", fs=7, ha="left", va="bottom")
        # angles
        t = np.linspace(np.pi / 2, np.pi / 2 + th1, 30)
        ax.plot(0.62 * np.cos(t), 0.62 * np.sin(t), color=INK, lw=0.6)
        callout(ax, (-0.1, 0.6), (-0.6, 0.45), "15°", fs=6.5, ha="right")
        t = np.linspace(-np.pi / 2, -np.pi / 2 + th2, 30)
        ax.plot(0.55 * np.cos(t), 0.55 * np.sin(t), color=INK, lw=0.6)
        label(ax, 0.36, -0.78, f"{np.degrees(th2):.1f}°", fs=6.5)
        R = Rs if pol == "s" else Rp
        if pol == "s":
            txt = "s (TE): $\\mathbf{E}$ out of the page\n(normal to the plane of incidence)"
        else:
            txt = "p (TM): $\\mathbf{E}$ in the plane of incidence,\nnormal to each ray"
        label(ax, 2.15, 1.8, txt, fs=6.8, ha="right", va="top", col=INK)
        label(ax, 2.15, 0.78, f"$R_{pol}$ = {100*R:.1f} %", fs=7.0, ha="right", col=INK)
        panel(ax, "ab"[k], 0.01, 0.995)
    save(fig, "ch02_sp")


# ------------------------------------------------------------------ Figure: TIR and the evanescent tail
def fig_tir():
    thc = np.degrees(np.arcsin(N_OX / N_SI))
    th_mode = np.degrees(np.arcsin(NEFF_SLAB / N_SI))
    d_mode = decay_nm(N_SI, N_OX, np.radians(th_mode))
    pairs = [("Si / SiO$_2$", N_SI, N_OX, C1), ("Si / air", N_SI, N_AIR, C3), ("SiN / SiO$_2$", N_SIN, N_OX, C2)]
    print("critical angles: " + ", ".join(f"{n.replace('$_2$', '2')} {np.degrees(np.arcsin(b / a)):.1f}°" for n, a, b, _ in pairs))
    print("slab TE0 (n_eff %.3f): ray angle %.1f°, field decay length 1/gamma %.0f nm, intensity %.0f nm" %
          (NEFF_SLAB, th_mode, d_mode, d_mode / 2))
    fig = plt.figure(figsize=(6.3, 4.3))
    # (a) three regimes, silicon above, oxide below
    a = fig.add_axes([0.0, 0.53, 1.0, 0.47])
    frameless(a, xlim=(-0.3, 12.3), ylim=(-1.75, 1.85))
    cases = [(15.0, "below θ$_c$: part of the\nlight is transmitted"), (thc, "at θ$_c$ = %.1f°: the transmitted\nray grazes the interface" % thc),
             (th_mode, "beyond θ$_c$: all is reflected,\nan evanescent field remains")]
    for k, (thd, txt) in enumerate(cases):
        x0 = 2.0 + 4.1 * k
        th = np.radians(thd)
        box(a, x0 - 1.95, 0, 3.9, 1.55, "si", alpha=0.35)
        box(a, x0 - 1.95, -1.25, 3.9, 1.25, "ox")
        a.plot([x0, x0], [-1.15, 1.45], color=MUTED, lw=0.6, ls=(0, (3, 3)))
        Lr = 1.4
        rs, rp = fresnel(N_SI, N_OX, th)
        R = abs(rs) ** 2
        arrow(a, (x0 - Lr * np.sin(th), Lr * np.cos(th)), (x0, 0), col=RED, lw=1.8, ms=9, z=6)
        arrow(a, (x0, 0), (x0 + Lr * np.sin(th), Lr * np.cos(th)), col=RED, lw=max(0.5, 1.8 * R), ms=8, z=6)
        if thd < thc - 1e-6:
            th2 = np.arcsin(N_SI * np.sin(th) / N_OX)
            arrow(a, (x0, 0), (x0 + 1.1 * np.sin(th2), -1.1 * np.cos(th2)), col=RED, lw=1.8 * (1 - R), ms=8, z=6)
            label(a, x0 + 0.95, -0.55, f"{np.degrees(th2):.1f}°", fs=6.5, ha="left")
        elif abs(thd - thc) < 1e-6:
            arrow(a, (x0, -0.02), (x0 + 1.6, -0.02), col=RED, lw=0.9, ms=7, z=6, ls=(0, (3, 2)))
        else:
            # evanescent intensity below the interface, drawn over 3 decay lengths (vertical scale expanded)
            yy = np.linspace(0, -1.2, 60)
            for j in range(len(yy) - 1):
                I = np.exp(-2 * (-yy[j]) / 0.33)
                box(a, x0 - 1.4, yy[j + 1], 2.8, yy[j] - yy[j + 1], C3, alpha=0.75 * I, z=3)
            label(a, x0 + 1.45, -0.42, f"field decays as\n$e^{{-\\gamma x}}$, 1/γ = {d_mode:.0f} nm", fs=6.4, ha="left", va="center")
        t = np.linspace(np.pi / 2, np.pi / 2 + th, 30)
        a.plot(x0 + 0.5 * np.cos(t), 0.5 * np.sin(t), color=INK, lw=0.6)
        label(a, x0 - 0.2, 0.75, f"{thd:.1f}°" if k else "15°", fs=6.5, ha="right" if k else "center")
        label(a, x0, 1.62, txt, fs=6.6, va="bottom")
    label(a, 0.0, -1.48, f"Si above ($n$ = {N_SI}), SiO$_2$ below ($n$ = {N_OX})", fs=6.6, ha="left", col=MUTED)
    note(a, "rays not to scale; evanescent shading stretched", loc="lower right")
    panel(a, "a", 0.0, 1.0)
    # (b) decay length against angle, (c) phase on reflection
    b = fig.add_axes([0.085, 0.09, 0.38, 0.37])
    c = fig.add_axes([0.6, 0.09, 0.38, 0.37])
    for name, n1, n2, col in pairs:
        tc = np.degrees(np.arcsin(n2 / n1))
        th = np.linspace(tc + 0.05, 90, 600)
        b.plot(th, decay_nm(n1, n2, np.radians(th)), color=col, label=name)
        b.axvline(tc, color=col, lw=0.6, ls=":")
    b.plot([th_mode], [d_mode], "o", color=INK, ms=4.5, zorder=5)
    b.annotate(f"220 nm slab, TE$_0$:\n{th_mode:.0f}°, {d_mode:.0f} nm", (th_mode, d_mode), xytext=(58, 330),
               fontsize=6.6, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xlim(10, 90); b.set_ylim(0, 600)
    finish(b, "Angle of incidence θ$_1$ (°)", "Decay length 1/γ (nm)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.8, handlelength=1.4)
    tag(b, "b")
    th = np.linspace(thc + 0.01, 89.99, 600)
    rs, rp = fresnel(N_SI, N_OX, np.radians(th))
    c.plot(th, np.angle(rs) / np.pi, color=C1, label="s (TE)")
    c.plot(th, np.angle(rp) / np.pi, color=C1, ls="--", label="p (TM)")
    rs0, rp0 = fresnel(N_SI, N_OX, np.radians(th_mode))
    print("reflection phase at %.1f°: s %.3f pi, p %.3f pi; at 89.99°: s %.3f pi" %
          (th_mode, np.angle(rs0) / np.pi, np.angle(rp0) / np.pi, np.angle(rs[-1]) / np.pi))
    c.plot([th_mode], [np.angle(rs0) / np.pi], "o", color=INK, ms=4.5, zorder=5)
    c.axvline(thc, color=C1, lw=0.6, ls=":")
    c.set_xlim(20, 90); c.set_ylim(0, 1.05)
    c.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); c.set_yticklabels(["0", "π/4", "π/2", "3π/4", "π"])
    finish(c, "Angle of incidence θ$_1$ (°)", "Phase of $r$ (Si / SiO$_2$)", legend=True, loc="lower right")
    c.text(thc + 1, 0.98, "θ$_c$", fontsize=7, color=C1, va="top")
    tag(c, "c")
    save(fig, "ch02_tir")


if __name__ == "__main__":
    fig_planewave(); fig_sp(); fig_tir()
