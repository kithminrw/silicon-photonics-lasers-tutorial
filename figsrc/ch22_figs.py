"""Figures for Chapter 22 (absorption, emission and gain).

Run from the repository root:  python -I -X utf8 figsrc/ch22_figs.py
Writes assets/figs/ch22_processes.svg, ch22_levels.svg, ch22_lineshape.svg and ch22_bandgaps.svg, and prints every
number the figures and captions use.

All drawings are concept diagrams. Energies that carry numbers come from the chapter and Appendix B: erbium's
980 nm pump and 1530 nm emission (Worked Example 22.1; 1480 nm pumping from Chapter 28), band gaps of 0.80 eV for the
1550 nm InGaAsP alloy, 1.12 eV (indirect) for Si, and 0.66 eV (indirect) / 0.80 eV (direct) for Ge.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *

HC = 1239.84                      # eV nm


def photon(ax, p0, p1, col=RED, nw=3.0, amp=0.22, lw=1.2, ms=8, alpha=1.0, z=6):
    """A wavy photon from p0 to p1 with an arrowhead at p1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    t = np.linspace(0, 1, 200); head = 0.55 / L
    tt = t * (1 - head)
    env = np.minimum(1, np.minimum(tt, 1 - head - tt) / 0.08 + 0.15)
    pts = p0 + np.outer(tt * L, u) + np.outer(amp * np.sin(2 * np.pi * nw * t) * np.clip(env, 0, 1), n)
    ax.plot(pts[:, 0], pts[:, 1], color=col, lw=lw, alpha=alpha, zorder=z, solid_capstyle="round")
    arrow(ax, tuple(pts[-1]), tuple(p1), col=col, lw=lw, ms=ms, z=z)


def level(ax, x0, x1, y, text=None, lw=1.6, col=INK, fs=FS, side="left"):
    ax.plot([x0, x1], [y, y], color=col, lw=lw, solid_capstyle="butt", zorder=3)
    if text:
        if side == "left":
            label(ax, x0 - 0.2, y, text, ha="right", fs=fs)
        else:
            label(ax, x1 + 0.2, y, text, ha="left", fs=fs)


def electron(ax, x, y, filled=True, r=0.27):
    from matplotlib.patches import Circle
    if filled:
        ax.add_patch(Circle((x, y), r, fc=BLUE, ec=BLUE, lw=0.8, zorder=8))
    else:
        ax.add_patch(Circle((x, y), r, fc="white", ec=BLUE, lw=0.8, ls=(0, (2, 1.5)), zorder=8))


# ================================================================== Figure 22.1: the three processes
def fig_processes():
    fig = plt.figure(figsize=(6.3, 2.25))
    W = 1 / 3
    for k, (key, name, rate) in enumerate([("abs", "Absorption", r"rate $B_{12}\,\rho(\nu)\,N_1$"),
                                           ("stim", "Stimulated emission", r"rate $B_{21}\,\rho(\nu)\,N_2$"),
                                           ("spon", "Spontaneous emission", r"rate $A_{21}N_2 = N_2/\tau_{sp}$")]):
        ax = fig.add_axes([k * W, 0.0, W, 1.0]); frameless(ax, (0, 10), (-0.9, 6.6))
        y1, y2, xa, xb, xe = 1.5, 4.6, 3.0, 7.0, 5.0
        level(ax, xa, xb, y2, "$E_2$"); level(ax, xa, xb, y1, "$E_1$")
        ym = (y1 + y2) / 2
        if key == "abs":
            photon(ax, (0.2, ym), (4.4, ym))
            label(ax, 1.9, ym + 0.65, r"$h\nu$", col=RED)
            electron(ax, xe, y1, filled=False); electron(ax, xe, y2)
            arrow(ax, (xe + 0.75, y1 + 0.35), (xe + 0.75, y2 - 0.35), col=INK, lw=1.0, ms=7)
            label(ax, 5.0, 0.15, "photon absorbed,\nelectron lifted", fs=FS_SMALL, col=MUTED)
        elif key == "stim":
            photon(ax, (0.2, ym), (3.6, ym))
            label(ax, 1.9, ym + 0.65, r"$h\nu$", col=RED)
            electron(ax, xe, y2, filled=False); electron(ax, xe, y1)
            arrow(ax, (xe - 0.75, y2 - 0.35), (xe - 0.75, y1 + 0.35), col=INK, lw=1.0, ms=7)
            for dy in (0.42, -0.42):
                photon(ax, (6.1, ym + dy), (9.8, ym + dy))
            label(ax, 8.0, ym - 1.25, "two identical\nphotons", fs=FS_SMALL, col=RED)
            label(ax, 5.0, 0.15, "same frequency, direction,\nphase and polarisation", fs=FS_SMALL, col=MUTED)
        else:
            electron(ax, xe, y2, filled=False); electron(ax, xe, y1)
            arrow(ax, (xe - 0.75, y2 - 0.35), (xe - 0.75, y1 + 0.35), col=INK, lw=1.0, ms=7)
            photon(ax, (5.6, ym + 0.15), (8.9, ym + 1.9))
            for ang in (-5, -40):
                a = np.radians(ang); p0 = np.array([5.6, ym]) + 0.5 * np.array([np.cos(a), np.sin(a)])
                p1 = p0 + 2.6 * np.array([np.cos(a), np.sin(a)])
                arrow(ax, tuple(p0), tuple(p1), col=RED, lw=0.7, ms=6, ls=(0, (2, 2)))
            label(ax, 9.0, ym + 0.8, r"$h\nu$", col=RED)
            label(ax, 5.0, 0.15, "any direction, random phase", fs=FS_SMALL, col=MUTED)
        label(ax, 5.0, 6.3, name, bold=True, fs=7.6)
        label(ax, 5.0, 5.55, rate, fs=FS)
        panel(ax, "abc"[k], x=0.0, y=1.0)
    save(fig, "ch22_processes")


# ================================================================== Figure 22.2: two-, three- and four-level schemes
def fig_levels():
    E980, E1530, E1480 = HC / 980, HC / 1530, HC / 1480
    print(f"Er3+: 980 nm = {E980:.3f} eV, 1480 nm = {E1480:.3f} eV, 1530 nm = {E1530:.3f} eV")
    fig = plt.figure(figsize=(6.3, 2.9))
    # ---- (a) two-level
    ax = fig.add_axes([0.0, 0.0, 0.27, 1.0]); frameless(ax, (0, 10), (-2.4, 10.0), equal=False)
    level(ax, 2.6, 8.2, 1.0, "1"); level(ax, 2.6, 8.2, 6.5, "2")
    arrow(ax, (3.6, 1.2), (3.6, 6.3), col=BLUE, lw=1.6, ms=9); label(ax, 3.35, 3.9, "pump", col=BLUE, rot=90, fs=FS_SMALL)
    arrow(ax, (5.4, 6.3), (5.4, 1.2), col=RED, lw=1.6, ms=9); label(ax, 5.15, 3.9, "stimulated", col=RED, rot=90, fs=FS_SMALL)
    arrow(ax, (7.2, 6.3), (7.2, 1.2), col=RED, lw=1.0, ms=7, ls=(0, (2, 1.6))); label(ax, 6.95, 3.9, "spontaneous", col=RED, rot=90, fs=FS_SMALL)
    label(ax, 5.4, 9.3, "Two levels", bold=True, fs=7.6)
    label(ax, 5.4, -1.2, "pump stimulates emission as\nreadily as absorption:\n$N_2 \\to N_1$ at best, no gain", fs=FS_SMALL, col=MUTED)
    panel(ax, "a", 0.0, 1.0)
    # ---- (b) three-level: erbium, energies to scale
    ax = fig.add_axes([0.30, 0.0, 0.40, 1.0]); frameless(ax, (0, 10), (-0.36, 1.50), equal=False)
    xa, xb = 2.4, 8.4
    bands = [(0.0, 0.045, r"$^4$I$_{15/2}$ (ground)"), (E1530, E1530 + 0.045, r"$^4$I$_{13/2}$"), (E980, E980 + 0.03, r"$^4$I$_{11/2}$")]
    for lo, hi, txt in bands:
        ax.add_patch(Rectangle((xa, lo), xb - xa, hi - lo, fc="#E9E1CF", ec="none", zorder=1))
        ax.plot([xa, xb], [lo, lo], color=INK, lw=1.4, zorder=3)
        label(ax, xb + 0.15, lo + (hi - lo) / 2, txt, ha="left", fs=FS_SMALL)
    arrow(ax, (3.1, 0.005), (3.1, E980), col=BLUE, lw=1.6, ms=9)
    label(ax, 2.85, 0.62, "pump 980 nm", col=BLUE, rot=90, fs=FS_SMALL)
    arrow(ax, (4.4, 0.005), (4.4, E1480), col=BLUE, lw=1.0, ms=7, ls=(0, (3, 1.6)))
    label(ax, 4.15, 0.36, "or 1480 nm", col=BLUE, rot=90, fs=FS_SMALL)
    # fast non-radiative decay 11/2 -> 13/2
    zz = np.linspace(E980 - 0.01, E1530 + 0.05, 60)
    ax.plot(5.4 + 0.12 * np.sin(np.linspace(0, 6 * np.pi, 60)), zz, color=MUTED, lw=0.9, zorder=5)
    arrow(ax, (5.4, E1530 + 0.06), (5.4, E1530 + 0.046), col=MUTED, lw=0.9, ms=6)
    label(ax, 5.62, (E980 + E1530) / 2 + 0.02, "fast,\nnon-radiative", ha="left", col=MUTED, fs=FS_SMALL)
    arrow(ax, (7.2, E1530), (7.2, 0.005), col=RED, lw=1.8, ms=9)
    label(ax, 7.45, 0.40, "1530 nm\n$\\tau_{sp}$ ≈ 10 ms", ha="left", col=RED, fs=FS_SMALL)
    label(ax, 5.4, 1.43, "Three levels: Er$^{3+}$ in silica", bold=True, fs=7.6)
    label(ax, 5.4, -0.22, "the lower laser level is the ground state:\nmore than half the ions must be pumped", fs=FS_SMALL, col=MUTED)
    # energy scale bar (0.2 eV)
    ax.plot([1.2, 1.2], [0.2, 0.4], color=INK, lw=1.2); label(ax, 1.05, 0.3, "0.2 eV", ha="right", fs=FS_SMALL)
    panel(ax, "b", 0.0, 1.0)
    # ---- (c) four-level
    ax = fig.add_axes([0.73, 0.0, 0.27, 1.0]); frameless(ax, (0, 10), (-2.4, 10.0), equal=False)
    ys = [0.4, 2.0, 6.0, 7.6]
    for i, y in enumerate(ys):
        level(ax, 2.6, 8.2, y, str(i))
    arrow(ax, (3.4, 0.6), (3.4, 7.4), col=BLUE, lw=1.6, ms=9); label(ax, 3.15, 3.9, "pump", col=BLUE, rot=90, fs=FS_SMALL)
    for (y0, y1, x) in ((ys[3], ys[2], 5.6), (ys[1], ys[0], 5.6)):
        zz = np.linspace(y0 - 0.12, y1 + 0.3, 30)
        ax.plot(x + 0.1 * np.sin(np.linspace(0, 4 * np.pi, 30)), zz, color=MUTED, lw=0.9)
        arrow(ax, (x, y1 + 0.32), (x, y1 + 0.1), col=MUTED, lw=0.9, ms=6)
    label(ax, 5.85, 6.85, "fast", ha="left", col=MUTED, fs=FS_SMALL); label(ax, 5.85, 1.2, "fast", ha="left", col=MUTED, fs=FS_SMALL)
    arrow(ax, (7.3, 5.85), (7.3, 2.15), col=RED, lw=1.8, ms=9); label(ax, 7.05, 4.0, "laser", col=RED, rot=90, fs=FS_SMALL)
    label(ax, 5.4, 9.3, "Four levels", bold=True, fs=7.6)
    label(ax, 5.4, -1.2, "the lower laser level empties\nas fast as it fills:\ninversion at any pump", fs=FS_SMALL, col=MUTED)
    panel(ax, "c", 0.0, 1.0)
    fig.text(0.865, 0.88, "not to scale", fontsize=6, color=MUTED, style="italic", ha="center")
    fig.text(0.135, 0.88, "not to scale", fontsize=6, color=MUTED, style="italic", ha="center")
    save(fig, "ch22_levels")


# ================================================================== Figure 22.3: lineshapes and saturation
def lorentz(x, fwhm):
    return (fwhm / 2 / np.pi) / (x ** 2 + (fwhm / 2) ** 2)


def gauss(x, fwhm):
    s = fwhm / (2 * np.sqrt(2 * np.log(2)))
    return np.exp(-x ** 2 / (2 * s ** 2)) / (s * np.sqrt(2 * np.pi))


def fig_lineshape():
    x = np.linspace(-3, 3, 1201)
    L, G = lorentz(x, 1.0), gauss(x, 1.0)
    print(f"same FWHM: peak Lorentzian {L.max():.3f}, Gaussian {G.max():.3f} (ratio {G.max()/L.max():.2f});"
          f" at 3 FWHM from centre L/G = {lorentz(3,1)/gauss(3,1):.2e}")
    fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.35))
    a, b, cc = axs
    a.plot(x, L, color=C1, label="Lorentzian (homogeneous)")
    a.plot(x, G, color=C2, label="Gaussian (inhomogeneous)")
    a.annotate("", xy=(0.5, 0.5 * L.max()), xytext=(-0.5, 0.5 * L.max()),
               arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    a.text(0, 0.5 * L.max() - 0.075, r"$\Delta\nu$", ha="center", va="top", fontsize=7.5, color=INK)
    a.set_xlim(-2.5, 2.5); a.set_ylim(0, 1.2)
    a.legend(loc="upper center", fontsize=6.5, handlelength=1.4, bbox_to_anchor=(0.5, 1.04))
    finish(a, r"$(\nu - \nu_0)/\Delta\nu$", r"$g(\nu)\cdot\Delta\nu$")
    tag(a, "a")
    # (b) homogeneous: a signal at nu_s saturates the whole line (I = I_sat)
    xs = 0.6
    g0 = lorentz(x, 1.0) / lorentz(0, 1.0)
    sat = 1 / (1 + 1.0 * lorentz(xs, 1.0) / lorentz(0, 1.0) * 3)        # I = 3 I_sat(nu_0)
    b.plot(x, g0, color=MUTED, ls="--", lw=1.0, label="no signal")
    b.plot(x, g0 * sat, color=C1, label="strong signal")
    b.annotate("", xy=(xs, 0.0), xytext=(xs, -0.001), annotation_clip=False)
    b.axvline(xs, color=RED, lw=0.9, ymax=0.93)
    b.text(xs + 0.08, 1.05, "signal", color=RED, fontsize=6.6, va="center")
    b.set_xlim(-2.5, 2.5); b.set_ylim(0, 1.15)
    b.legend(loc="upper left", fontsize=6.3, handlelength=1.4)
    finish(b, r"$(\nu - \nu_0)/\Delta\nu$", "Gain (norm.)")
    b.set_yticks([0, 0.5, 1])
    tag(b, "b")
    # (c) inhomogeneous: packets of homogeneous width dh under a Gaussian envelope; the signal burns a hole
    dh = 0.15
    centres = np.linspace(-3, 3, 601); wts = gauss(centres, 1.0); wts /= wts.sum()
    Lk = lorentz(x[:, None] - centres[None, :], dh)
    g_un = Lk @ wts
    s_k = 1 / (1 + 3 * lorentz(xs - centres, dh) / lorentz(0, dh))
    g_sat = Lk @ (wts * s_k)
    nrm = g_un.max()
    cc.plot(x, g_un / nrm, color=MUTED, ls="--", lw=1.0)
    cc.plot(x, g_sat / nrm, color=C2)
    for xc in np.arange(-1.6, 1.61, 0.4):
        cc.plot(x, 0.13 * lorentz(x - xc, dh) / lorentz(0, dh), color=C2, lw=0.5, alpha=0.6)
    cc.axvline(xs, color=RED, lw=0.9, ymax=0.93)
    cc.text(xs + 0.08, 1.05, "signal", color=RED, fontsize=6.6, va="center")
    cc.text(-2.4, 0.2, "emitters with\ndifferent centres", fontsize=6.3, color=C2, va="center")
    cc.annotate("spectral\nhole", xy=(xs, (g_sat / nrm)[np.argmin(abs(x - xs))] + 0.02), xytext=(1.3, 0.62),
                fontsize=6.6, color=INK, ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    cc.set_xlim(-2.5, 2.5); cc.set_ylim(0, 1.15); cc.set_yticks([0, 0.5, 1])
    finish(cc, r"$(\nu - \nu_0)/\Delta\nu$", "Gain (norm.)")
    tag(cc, "c")
    j = np.argmin(abs(x - xs)); print(f"hole depth at signal: {1 - g_sat[j]/g_un[j]:.2f} of the local gain; homogeneous drop {1 - sat:.2f}")
    fig.tight_layout(w_pad=1.0)
    save(fig, "ch22_lineshape")


# ================================================================== Figure 22.4: direct and indirect gaps
def fig_bandgaps():
    fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.75), sharey=True)
    k = np.linspace(-1, 1, 401)
    mv = 0.45                                         # curvature of the drawn valence band (eV per unit k^2)

    def vb(ax):
        ax.plot(k, -mv * k ** 2 * 1.6, color=INK, lw=1.5)
        ax.plot(k, -mv * k ** 2 * 3.2, color=INK, lw=0.8, alpha=0.6)

    def valley(ax, k0, E0, curv, lw=1.5, kr=0.45, alpha=1.0):
        kk = k[abs(k - k0) <= kr]
        ax.plot(kk, E0 + curv * (kk - k0) ** 2, color=INK, lw=lw, alpha=alpha)

    def dots(ax, x, y, col, filled=True):
        ax.plot(x, y, "o", ms=4.2, mfc=col if filled else "white", mec=col, mew=0.9, zorder=7)

    # (a) direct gap: InGaAsP at 1550 nm
    a = axs[0]; Eg = 0.80
    vb(a); valley(a, 0, Eg, 3.0, kr=0.75)
    dots(a, [-0.05, 0.05, 0], [Eg + 0.012, Eg + 0.012, Eg + 0.035], BLUE); dots(a, [-0.05, 0.05], [-0.012, -0.012], RED, filled=False)
    photon_v(a, 0.0, Eg - 0.02, 0.02)
    a.text(0.08, Eg / 2, f"photon\n{HC/Eg:.0f} nm", fontsize=6.6, color=RED, va="center")
    a.set_title("Direct gap: InGaAsP, InP, GaAs", fontsize=7.2, color=INK)
    a.annotate("", xy=(-0.55, Eg), xytext=(-0.55, 0), arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    a.text(-0.6, Eg / 2, f"{Eg:.2f} eV", fontsize=6.6, color=MUTED, ha="right", va="center", rotation=90)
    tag(a, "a")
    # (b) indirect gap: silicon (CB minimum near X, k = 0.85 of the zone edge)
    b = axs[1]; Eg = 1.12; k0 = 0.85
    vb(b)
    for s in (-1, 1):
        valley(b, s * k0, Eg, 2.2, kr=0.32)
    b.annotate("", xy=(0.0, 1.88), xytext=(0.0, 1.45), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.7, mutation_scale=6))
    b.text(0.05, 1.42, "conduction band\nat $k$ = 0 far higher", fontsize=6.0, color=MUTED, ha="center", va="top")
    dots(b, [k0 - 0.04, k0 + 0.04], [Eg + 0.01, Eg + 0.01], BLUE); dots(b, [-0.05, 0.05], [-0.012, -0.012], RED, filled=False)
    # photon (vertical) + phonon (horizontal): the electron needs both
    photon_v(b, k0, Eg - 0.02, 0.03)
    b.annotate("", xy=(0.04, 0.03), xytext=(k0 - 0.02, 0.03), arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.3, mutation_scale=8, shrinkA=0, shrinkB=0))
    b.text((k0 + 0.04) / 2, 0.09, "phonon\nsupplies $\\Delta k$", fontsize=6.6, color=TEAL, ha="center", va="bottom")
    b.text(k0 + 0.06, Eg / 2 + 0.12, "photon", fontsize=6.6, color=RED, va="center", ha="left", rotation=90)
    b.set_title("Indirect gap: Si, 1.12 eV", fontsize=7.2, color=INK)
    tag(b, "b")
    # (c) germanium: L valley (zone edge) 0.66 eV, Gamma valley 0.80 eV
    cax = axs[2]; EL, EG_ = 0.66, 0.80
    vb(cax)
    for s in (-1, 1):
        valley(cax, s * 1.0, EL, 2.0, kr=0.3)
    valley(cax, 0, EG_, 3.0, kr=0.5)
    dots(cax, [0.96, 0.99], [EL + 0.012, EL + 0.03], BLUE); dots(cax, [-0.97], [EL + 0.012], BLUE)
    dots(cax, [0.0], [EG_ + 0.01], BLUE)
    dots(cax, [-0.05, 0.05], [-0.012, -0.012], RED, filled=False)
    photon_v(cax, 0.0, EG_ - 0.02, 0.02)
    cax.annotate("", xy=(0.62, EG_), xytext=(0.62, EL), arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.7, mutation_scale=5, shrinkA=0, shrinkB=0))
    cax.plot([0.3, 0.68], [EG_, EG_], color=MUTED, lw=0.5, ls=":"); cax.plot([0.56, 0.95], [EL, EL], color=MUTED, lw=0.5, ls=":")
    cax.text(0.58, (EG_ + EL) / 2 + 0.01, f"{EG_ - EL:.2f} eV", fontsize=6.4, color=MUTED, ha="right", va="center")
    cax.set_title("Ge: 0.66 eV indirect, 0.80 eV direct", fontsize=7.2, color=INK)
    tag(cax, "c")
    for ax in axs:
        ax.set_xlim(-1.05, 1.05); ax.set_ylim(-0.42, 1.9)
        ax.set_xticks([-1, 0, 1]); ax.set_xticklabels(["zone\nedge", "0", "zone\nedge"])
        ax.grid(False)
        ax.axhline(0, color=GRID, lw=0.5, zorder=0)
        ax.set_xlabel("Crystal momentum $k$")
    axs[0].set_ylabel("Electron energy (eV)")
    axs[0].text(-1.0, 1.86, "energies\nto scale", fontsize=6.0, color=MUTED, style="italic", ha="left", va="top")
    fig.tight_layout(w_pad=0.6)
    save(fig, "ch22_bandgaps")
    print(f"photon momentum h/lambda vs zone edge pi/a: at 1550 nm and a = 0.543 nm, ratio "
          f"{(2*np.pi/1550e-9)/(np.pi/0.543e-9):.1e} (photon k in the material x n = 3.5: {(2*np.pi*3.5/1550e-9)/(np.pi/0.543e-9):.1e})")


def photon_v(ax, kx, Etop, Ebot, col=RED):
    """Vertical emission arrow (a photon) from the conduction band down to the valence band."""
    zz = np.linspace(Etop, Ebot + 0.06, 120)
    ax.plot(kx + 0.035 * np.sin(np.linspace(0, 8 * np.pi, 120)), zz, color=col, lw=1.0, zorder=6)
    ax.annotate("", xy=(kx, Ebot), xytext=(kx, Ebot + 0.07), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0, mutation_scale=7, shrinkA=0, shrinkB=0))


if __name__ == "__main__":
    print("photon energies: 1550 nm", f"{HC/1550:.3f} eV; 1310 nm {HC/1310:.3f} eV")
    for B, lab in ((1e-10, "InGaAsP"), (1e-14, "Si")):
        print(f"radiative lifetime 1/(B N) at 1e18 cm^-3, {lab}: {1/(B*1e18):.1e} s")
    fig_processes()
    fig_levels()
    fig_lineshape()
    fig_bandgaps()
