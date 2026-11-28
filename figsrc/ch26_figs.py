"""Figures for Chapter 26 (single-frequency and tunable lasers).

Run from the repository root:  python -I -X utf8 figsrc/ch26_figs.py
NumPy and Matplotlib only. Prints every number the captions quote, then writes assets/figs/ch26_*.svg.

  ch26_dfb          DFB laser along its cavity (lambda/4-shifted grating) and the longitudinal intensity of its
                    lasing mode for kappa*L = 1, 2, 3 (coupled-mode transfer matrices at threshold)
  ch26_dfb_spectra  amplified transmission just below threshold of a uniform and a lambda/4-shifted DFB (kappa*L = 2)
  ch26_dbr          three-section DBR laser and its tuning: cavity modes, mirror peak, mode hops, phase-section reset
  ch26_ecl          III-V/Si external-cavity laser, top view: RSOA, phase heater, two Vernier rings, loop mirror
  ch26_vernier      Vernier gearing: the two ring combs before and after heating ring 2 by one FSR difference, and
                    the lasing wavelength against the ring-2 heater power
  ch26_sil          self-injection locking to a high-Q ring (schematic)
  ch26_multi        multi-wavelength sources: DFB array with multiplexer, and comb source with demultiplexer

The DFB and DBR lasers are illustrative (L = 400 um, n_g = 3.6, kappa*L = 1-3, as for the Chapter 24 laser); the
Vernier numbers are those of Worked Example 26.1 (n_g = 4.18, R = 10 and 11 um, 0.18 nm/mW heaters); the ring
filter model (n_eff 2.446, kappa^2 = 0.15, 3 dB/cm, gain window centred on 1550 nm) is the one of the vernier demo.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *

LAM0 = 1550.0          # nm
NG_III = 3.6           # group index of the III-V lasers (as in Chapter 24)


# ====================================================================== DFB coupled-mode theory
def t_section(s, kap, l):
    """Transfer matrix of a uniform grating section for the slowly varying amplitudes [R, S] (forward, backward).
    s = alpha - i*delta (field gain and detuning, 1/length), kap = coupling coefficient (complex for a phase shift)."""
    g = np.sqrt(s * s + abs(kap) ** 2 + 0j)
    M = np.array([[s, -1j * kap], [1j * np.conj(kap), -s]], dtype=complex)
    return np.cosh(g * l) * np.eye(2) + np.sinh(g * l) / g * M


def t_dfb(s, kL, shift, L=1.0):
    k = kL / L
    if shift:   # quarter-wave shift: the grating phase jumps by pi in the middle, kappa -> -kappa
        return t_section(s, -k, L / 2) @ t_section(s, k, L / 2)
    return t_section(s, k, L)


def dfb_modes(kL, shift, n=4):
    """Threshold modes (alpha_th*L, delta*L) of an AR-coated DFB: zeros of T22 (Newton, checked)."""
    found = []
    for a0 in (0.2, 0.6, 1.0, 1.6, 2.4):
        for d0 in np.arange(-11, 11.01, 0.5):
            s = complex(a0, -d0)
            for _ in range(80):
                f = t_dfb(s, kL, shift)[1, 1]
                d = (t_dfb(s + 1e-7, kL, shift)[1, 1] - f) / 1e-7
                s -= f / d
            if abs(t_dfb(s, kL, shift)[1, 1]) < 1e-9 and s.real > 0 and abs(s.imag) < 12:
                m = (round(s.real, 5), round(-s.imag, 5))
                if all(abs(m[0] - o[0]) + abs(m[1] - o[1]) > 1e-3 for o in found):
                    found.append(m)
    return sorted(found)[:n]


def dfb_profile(kL, shift, aL, dL, nz=401):
    """|R|^2 + |S|^2 along the cavity at threshold (R(0) = 0, S(L) = 0), normalised to its mean."""
    zs = np.linspace(0, 1, nz); s = complex(aL, -dL); out = []
    for z in zs:
        if not shift or z <= 0.5:
            T = t_section(s, kL, z)
        else:
            T = t_section(s, -kL, z - 0.5) @ t_section(s, kL, 0.5)
        v = T @ np.array([0, 1])
        out.append(abs(v[0]) ** 2 + abs(v[1]) ** 2)
    out = np.array(out)
    return zs, out / out.mean()


def dl_nm(dL, L_um):
    """Detuning delta*L to wavelength offset (nm): delta = -2 pi n_g dlam / lam^2."""
    return -dL / (L_um * 1e3) * LAM0 ** 2 / (2 * np.pi * NG_III)


# ---------------------------------------------------------------------- Figure: DFB structure + intensity
def fig_dfb():
    L = 400.0
    fig = plt.figure(figsize=(6.3, 3.9))
    ax = fig.add_axes([0.10, 0.50, 0.86, 0.48]); ax.set_axis_off()
    XL = (-48, 448); ax.set_xlim(*XL); ax.set_ylim(-0.6, 8.6)
    box(ax, 0, 0.0, L, 0.35, "metal")
    box(ax, 0, 0.35, L, 2.65, "inp")
    box(ax, 0, 3.0, L, 0.7, "q")
    for k in range(3):
        ax.plot([0, L], [3.17 + 0.18 * k] * 2, color=MAT["mqw"], lw=0.9, zorder=3)
    box(ax, 0, 3.7, L, 3.2, "inp")
    # grating: InGaAsP teeth in the p-InP above the active region, a half-period (lambda/4) shift in the middle
    lam_d = 400 / 44.5
    base = 4.25; box(ax, 0, base, L, 0.18, "q", z=2)
    teeth = []
    z = 0.0
    while z + lam_d / 2 <= L / 2 + 1e-6:
        teeth.append(z); z += lam_d
    z = L / 2 + lam_d / 2 + lam_d / 2                     # the right half starts half a period late
    while z + lam_d / 2 <= L + 1e-6:
        teeth.append(z); z += lam_d
    for z0 in teeth:
        box(ax, z0, base + 0.18, lam_d / 2, 0.42, "q", z=2)
    box(ax, 0, 6.9, L, 0.35, "metal")
    for x in (-3.2, L):
        box(ax, x, 0.35, 3.2, 6.55, VIOLET, alpha=0.55, z=3)
    # labels inside the layers
    label(ax, 300, 1.7, "n-InP substrate", fs=FS)
    label(ax, 100, 2.55, "MQW active region", fs=FS_SMALL, col=INK)
    ax.annotate("", xy=(100, 3.05), xytext=(100, 2.75), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    label(ax, 300, 5.8, "p-InP", fs=FS)
    label(ax, 300, 7.75, "p contact", fs=FS_SMALL)
    label(ax, 100, -0.35, "n contact", fs=FS_SMALL)
    callout(ax, (40, 4.75), (12, 5.6), "grating (InGaAsP), period Λ", fs=FS_SMALL, ha="left")
    arrow(ax, (L / 2, 5.95), (L / 2, 4.95), col=RED, lw=0.9, ms=7)
    label(ax, L / 2, 6.25, "λ/4 shift", fs=FS, col=RED, bold=True)
    label(ax, -1.6, 7.75, "AR", fs=FS_SMALL, col=VIOLET, bold=True)
    label(ax, L + 1.6, 7.75, "AR", fs=FS_SMALL, col=VIOLET, bold=True)
    arrow(ax, (-6, 3.35), (-44, 3.35), col=RED, lw=1.6, ms=9)
    arrow(ax, (L + 6, 3.35), (L + 44, 3.35), col=RED, lw=1.6, ms=9)
    label(ax, -25, 4.1, "light", fs=FS_SMALL, col=RED)
    label(ax, L + 25, 4.1, "light", fs=FS_SMALL, col=RED)
    neff = 3.2; Lam = LAM0 / (2 * neff)
    print(f"DFB grating: period {Lam:.0f} nm for n_eff = {neff}, {L*1e3/Lam:.0f} periods in {L:.0f} um")
    note(ax, f"not to scale (a real grating has about {round(L*1e3/Lam, -2):.0f} periods of {Lam:.0f} nm)", loc="lower right")
    panel(ax, "a", x=-0.09, y=1.0)
    # intensity along the cavity at threshold, lambda/4 shift
    b = fig.add_axes([0.10, 0.11, 0.86, 0.34]); b.set_xlim(*XL)
    for kL, col in ((1, C1), (2, C2), (3, C4)):
        aL, dL = dfb_modes(kL, True)[0]
        zs, P = dfb_profile(kL, True, aL, dL)
        b.plot(zs * L, P, color=col, label=f"κL = {kL}")
        print(f"lambda/4 DFB kL={kL}: alpha_th L = {aL:.3f} (net modal gain {2*aL/(L*1e-4):.1f} /cm for L = {L:.0f} um), "
              f"centre/edge intensity {P[len(P)//2]/P[0]:.2f}, peak/mean {P.max():.2f}")
    b.axvline(L / 2, color=MUTED, lw=0.6, ls=":")
    b.set_ylim(0, 3.2); b.set_xticks([0, 100, 200, 300, 400]); b.spines["bottom"].set_bounds(0, L)
    b.legend(loc="upper left", ncol=3, bbox_to_anchor=(0.06, 1.05))
    finish(b, "Position along the cavity (µm)", "Intensity / mean")
    tag(b, "b")
    save(fig, "ch26_dfb")


# ---------------------------------------------------------------------- Figure: DFB spectra
def fig_dfb_spectra():
    L, kL = 400.0, 2.0
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.5), sharey=True)
    dLs = np.linspace(-9, 9, 3601)
    sb = dl_nm(kL, L)                                   # stop band edge |delta| = kappa
    print(f"kL = {kL}, L = {L:.0f} um, n_g = {NG_III}: stop band +-{abs(sb):.2f} nm "
          f"({2*abs(sb):.2f} nm wide); kappa = {kL/(L*1e-4):.0f} /cm")
    for ax, shift, name in ((axs[0], False, "uniform grating"), (axs[1], True, "λ/4-shifted grating")):
        modes = dfb_modes(kL, shift)
        a_las = modes[0][0]
        a = 0.95 * a_las
        T = np.array([abs(1 / t_dfb(complex(a, -d), kL, shift)[1, 1]) ** 2 for d in dLs])
        x = dl_nm(dLs, L)
        ax.axvspan(-abs(sb), abs(sb), color=GRID, lw=0, zorder=0)
        ax.plot(x, 10 * np.log10(T), color=C1 if not shift else C4, lw=1.3)
        ax.set_xlim(-2.0, 2.0); ax.set_ylim(-10, 45)
        ax.text(0, 44, "stop\nband", ha="center", va="top", fontsize=6.8, color=MUTED)
        g = [2 * m[0] / (L * 1e-4) for m in modes]
        lam = [dl_nm(m[1], L) for m in modes]
        print(f"{name}: modes (dlambda nm, net modal gain /cm): " + ", ".join(f"({l:+.2f}, {gg:.1f})" for l, gg in zip(lam, g)))
        if not shift:
            ax.text(0.03, 0.97, f"two modes, equal\nthreshold ({g[0]:.0f} cm$^{{-1}}$)", transform=ax.transAxes, fontsize=6.8, color=INK, va="top")
        else:
            ax.text(0.03, 0.97, f"one mode at λ$_B$:\n{g[0]:.0f} cm$^{{-1}}$; next modes\nneed {g[1]:.0f} cm$^{{-1}}$", transform=ax.transAxes, fontsize=6.8, color=INK, va="top")
        ax.text(0.97, 0.97, name, transform=ax.transAxes, ha="right", va="top", fontsize=7.2, color=INK)
        finish(ax, "Wavelength − λ$_B$ (nm)")
    axs[0].set_ylabel("Transmission (dB)")
    tag(axs[0], "a"); tag(axs[1], "b")
    fig.tight_layout(w_pad=1.5)
    save(fig, "ch26_dfb_spectra")


# ====================================================================== DBR laser tuning model
DBR = dict(Lg=400.0, Lp=150.0, Leff=100.0)            # um: gain, phase, effective DBR length (penetration)


def dbr_tuning(dn):
    """Lasing wavelength change (nm) with DBR current only, and the Bragg shift, for a DBR index change dn (<0)."""
    Lt = DBR["Lg"] + DBR["Lp"] + DBR["Leff"]
    dlc = LAM0 ** 2 / (2 * NG_III * Lt * 1e3)          # nm, cavity mode spacing
    lb = LAM0 * dn / NG_III                             # Bragg shift
    ms = np.arange(-20, 21)
    lm = ms[:, None] * dlc + LAM0 * dn[None, :] * DBR["Leff"] / (NG_III * Lt)
    las = lm[np.argmin(abs(lm - lb[None, :]), axis=0), np.arange(len(dn))]
    # phase-section index change that puts a mode exactly on the Bragg peak, kept in (-dnp_max, 0]
    dnp_max = LAM0 * 1e-3 / (2 * DBR["Lp"])
    need = (lb - lm[np.argmin(abs(lm - lb[None, :]), axis=0), np.arange(len(dn))])
    dnp_all = (lb[None, :] - lm) * NG_III * Lt / (LAM0 * DBR["Lp"])
    dnp = np.array([c[(c <= 1e-12) & (c > -dnp_max - 1e-12)].max() for c in dnp_all.T])
    return lm, lb, las, dnp, dlc, dnp_max


def fig_dbr():
    fig = plt.figure(figsize=(6.3, 4.4))
    ax = fig.add_axes([0.07, 0.56, 0.90, 0.43]); ax.set_axis_off()
    ax.set_xlim(-70, 790); ax.set_ylim(-1.2, 9.6)
    Lg, Lp, Ld = 400, 150, 200
    x1, x2, x3 = Lg, Lg + Lp, Lg + Lp + Ld
    box(ax, 0, 0.0, x3, 0.35, "metal")
    box(ax, 0, 0.35, x3, 2.65, "inp")
    box(ax, 0, 3.0, x3, 0.45, "q")                                   # passive waveguide core all along
    box(ax, 0, 3.45, x1, 0.55, "q")                                  # active MQW over the gain section
    for k in range(3):
        ax.plot([0, x1], [3.57 + 0.15 * k] * 2, color=MAT["mqw"], lw=0.9, zorder=3)
    box(ax, 0, 4.0, x1, 2.9, "inp"); box(ax, x1, 3.45, x3 - x1, 3.45, "inp")
    lam_d = 9.0
    z = x2
    while z + lam_d / 2 <= x3:
        box(ax, z, 3.45, lam_d / 2, 0.38, "q", z=2); z += lam_d
    for xa, xb, nm, cur in ((0, x1 - 6, "gain", "I$_\\mathrm{gain}$"), (x1 + 6, x2 - 6, "phase", "I$_\\mathrm{phase}$"),
                            (x2 + 6, x3, "DBR", "I$_\\mathrm{DBR}$")):
        box(ax, xa, 6.9, xb - xa, 0.35, "metal")
        label(ax, (xa + xb) / 2, 8.75, nm + " section", fs=FS, bold=True)
        arrow(ax, ((xa + xb) / 2, 8.25), ((xa + xb) / 2, 7.35), col=ELEC, lw=0.9, ms=7)
        label(ax, (xa + xb) / 2 + 12, 7.8, cur, fs=FS_SMALL, col=ELEC, ha="left")
    for xx in (x1, x2):
        ax.plot([xx, xx], [-0.2, 7.5], color=MUTED, lw=0.6, ls=(0, (2, 2)))
    label(ax, 300, 1.3, "n-InP", fs=FS); label(ax, 200, 5.45, "p-InP", fs=FS)
    callout(ax, (120, 3.75), (140, 2.35), "MQW (gain)", fs=FS_SMALL)
    callout(ax, (x1 + 70, 3.2), (x1 + 75, 1.6), "passive waveguide\n(no gain)", fs=FS_SMALL, ha="center")
    callout(ax, (x2 + 100, 3.7), (x2 + 60, 5.45), "Bragg grating", fs=FS_SMALL)
    label(ax, -2, -0.75, "cleaved facet", fs=FS_SMALL, ha="left", col=MUTED)
    arrow(ax, (-4, 3.6), (-62, 3.6), col=RED, lw=1.6, ms=9)
    label(ax, -33, 4.4, "light", fs=FS_SMALL, col=RED)
    note(ax, "not to scale", loc="lower right")
    panel(ax, "a", x=-0.06, y=1.0)
    # tuning
    dn = -np.linspace(0, 0.010, 2001)
    lm, lb, las, dnp, dlc, dnp_max = dbr_tuning(dn)
    hops = np.sum(np.abs(np.diff(las)) > dlc / 2)
    print(f"DBR laser: Lg {DBR['Lg']:.0f}, Lp {DBR['Lp']:.0f}, Leff {DBR['Leff']:.0f} um; mode spacing {dlc:.3f} nm; "
          f"Bragg shift {lb[-1]:.2f} nm for dn = {dn[-1]:.3f}; cavity modes move "
          f"{DBR['Leff']/(DBR['Lg']+DBR['Lp']+DBR['Leff']):.3f} times as fast as the mirror peak; {hops} hops; "
          f"phase section needs up to {dnp_max*1e3:.2f}e-3")
    b = fig.add_axes([0.10, 0.10, 0.50, 0.38])
    x = -dn * 1e3
    for row in lm:
        if row.max() > -5.5 and row.min() < 1.0:
            b.plot(x, row, color="#BAC3D1", lw=0.7, zorder=1)
    b.plot(x, lb, color=C2, lw=1.2, ls=(0, (4, 2)), label="mirror peak", zorder=2)
    b.plot(x, las, color=C1, lw=1.6, label="lasing, DBR current only", zorder=3)
    b.set_xlim(0, 10); b.set_ylim(-4.8, 0.6)
    b.text(9.6, -0.15, "cavity modes", ha="right", va="center", fontsize=6.5, color=MUTED,
           bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85), zorder=4)
    b.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="none", framealpha=1)
    finish(b, "DBR index change −Δn (10$^{-3}$)", "Wavelength change (nm)")
    tag(b, "b")
    c = fig.add_axes([0.71, 0.10, 0.27, 0.38])
    yy = -dnp * 1e3; yy[1:][np.diff(yy) < -1] = np.nan             # break the line where the phase section resets
    c.plot(x, yy, color=C3, lw=1.3)
    c.set_xlim(0, 10); c.set_ylim(0, 6.5)
    finish(c, "DBR index change −Δn (10$^{-3}$)", "Phase-section −Δn (10$^{-3}$)")
    c.text(0.5, 6.2, "keeps a mode on the\nmirror peak", fontsize=6.5, color=INK, va="top")
    tag(c, "c")
    save(fig, "ch26_dbr")


# ====================================================================== Vernier rings (Worked Example 26.1 / vernier demo)
NG_SI, NEFF_SI, LAM_UM = 4.18, 2.446, 1.55
K2, LOSS_DBCM = 0.15, 3.0
HEATER = 0.18                                         # nm/mW (Chapter 18, ring with a 9.15 nm FSR)


def fsr(R):
    return LAM_UM ** 2 / (NG_SI * 2 * np.pi * R) * 1e3     # nm


def drop(lam_nm, R, shift_nm=0.0):
    """Drop response of an add-drop ring (coupling and loss of the vernier demo). The round-trip phase is taken
    linear in wavelength, 2 pi (lambda - 1550 nm - shift)/FSR, so each comb has the constant FSR of the key equation
    and both rings resonate at 1550 nm with the heaters off; shift_nm moves the resonances (heater)."""
    L = 2 * np.pi * R
    a = np.exp(-(LOSS_DBCM * 100 / 4.343) / 2 * 1e-6) ** L
    t2 = 1 - K2
    phi = 2 * np.pi * (lam_nm - 1550.0 - shift_nm) / fsr(R)
    return K2 * K2 * a / (1 - 2 * t2 * a * np.cos(phi) + t2 * t2 * a * a)


def gain_window(lam_nm):
    return np.clip(1 - ((lam_nm - 1550.0) / 70.0) ** 2, 0, None)


def bezier(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    P = [np.asarray(p, float) for p in (p0, p1, p2, p3)]
    xy = (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]
    return xy[:, 0], xy[:, 1]


def ribbon_var(ax, xs, ys, ws, mat, z=2, **kw):
    """Like geomstyle.ribbon but with a width that varies along the path (tapers)."""
    xs, ys, ws = np.asarray(xs, float), np.asarray(ys, float), np.asarray(ws, float)
    dx, dy = np.gradient(xs), np.gradient(ys); L = np.hypot(dx, dy); L[L == 0] = 1
    nx, ny = -dy / L, dx / L
    left = np.c_[xs + nx * ws / 2, ys + ny * ws / 2]; right = np.c_[xs - nx * ws / 2, ys - ny * ws / 2]
    return poly(ax, np.vstack([left, right[::-1]]), mat, z=z, **kw)


def fig_ecl():
    fig, ax = geom_axes(figsize=(6.3, 2.75), xlim=(-73, 163), ylim=(-17, 64))
    W = 0.9                                                        # drawn waveguide width (actual 0.5 um)
    R1, R2, gap = 10.0, 11.0, 0.2
    pitch = W + gap                                                # centre-line distance waveguide-ring at the gap
    yb = 0.0
    x1 = 72.0; c1 = yb + pitch + R1                                # ring 1 above the bus
    yM = c1 + R1 + pitch                                           # its drop waveguide
    x2 = x1 - (R1 + R2 + 14.0); c2 = yM + pitch + R2               # ring 2 on the drop waveguide, to the left
    yT = c2 + R2 + pitch                                           # its drop waveguide, to the loop mirror
    box(ax, -2, -14, 164, 77, "ox", z=0)
    label(ax, 160, -11.5, "silicon chip", fs=FS_SMALL, ha="right", col=MUTED)
    # RSOA (broken: it is about 1 mm long), gain waveguide curved to meet the AR-coated facet at 7 degrees
    box(ax, -70, -10, 64, 14, "inp", z=1)
    th = np.radians(7); xa, xb, y0 = -36.0, -6.0, -5.0
    xs = np.r_[np.linspace(-68, xa, 30), np.linspace(xa, xb, 40)[1:]]
    ys = np.where(xs < xa, y0, y0 + np.tan(th) * (xs - xa) ** 2 / (2 * (xb - xa)))
    ribbon(ax, xs, ys, 2.0, "q", z=2)
    box(ax, -70, -10, 2.0, 14, VIOLET, z=3); box(ax, -7.4, -10, 1.4, 14, VIOLET, alpha=0.6, z=3)
    ax.plot([-52, -52], [-11.5, 5.5], color="white", lw=6, zorder=4)
    for dx in (-1.3, 1.3):
        ax.plot([-52 + dx - 0.9, -52 + dx + 0.9], [-11.5, 5.5], color=MUTED, lw=0.6, zorder=5)
    label(ax, -38, 10.5, "reflective SOA\n(III–V gain chip, ~1 mm)", fs=FS_SMALL)
    label(ax, -69, -12.8, "HR", fs=FS_SMALL, col=VIOLET, bold=True, ha="left")
    label(ax, -7, -12.8, "AR", fs=FS_SMALL, col=VIOLET, bold=True)
    label(ax, -24, -8.0, "gain waveguide", fs=FS_SMALL, col=INK)
    # edge coupler (inverse taper) from the chip facet, angled to meet the refracted beam
    ye = ys[-1] + (-2 - xb) * np.tan(np.radians(14))              # where that beam meets the silicon chip edge
    ex, ey = bezier((-2, ye), (4, ye + 6 * np.tan(np.radians(14))), (8, yb), (16, yb))
    ribbon_var(ax, ex, ey, np.linspace(0.25, W, len(ex)), "si")
    wg_straight(ax, 16, x1 + R1 + 8, yb, W, "si")
    box(ax, 22, yb - 2.0, 28, 4.0, "tin", alpha=0.55, z=1)
    label(ax, 36, yb - 4.6, "phase heater", fs=FS_SMALL)
    # rings, their drop waveguides, heaters
    wg_ring(ax, x1, c1, R1, W, "si"); wg_ring(ax, x2, c2, R2, W, "si")
    wg_straight(ax, x2 - R2 - 8, x1 + R1 + 8, yM, W, "si")
    xe = x1 + R1 + 26
    wg_straight(ax, x2 - R2 - 8, xe, yT, W, "si")
    wg_arc(ax, x1, c1, R1, 2.4, -70, 70, "tin", alpha=0.55, z=1)
    wg_arc(ax, x2, c2, R2, 2.4, 110, 250, "tin", alpha=0.55, z=1)
    label(ax, x1, c1, "ring 1\nR = 10 µm", fs=FS_SMALL)
    label(ax, x2, c2, "ring 2\nR = 11 µm", fs=FS_SMALL)
    callout(ax, (x1 + R1 + 1.3, c1 - 4), (x1 + R1 + 9, c1 - 8), "ring heaters", fs=FS_SMALL)
    # loop mirror: 2 x 2 coupler (input = lower left port, output = upper left port) whose right ports are looped
    Lc, s = 10.0, pitch
    wg_straight(ax, xe, xe + Lc, yT, W, "si"); wg_straight(ax, xe, xe + Lc, yT + s, W, "si")
    rl = 8.0; ym = yT + s / 2; xcl = xe + Lc + 5 + 0.707 * rl
    pu = (xcl - 0.707 * rl, ym + 0.707 * rl); pl = (xcl - 0.707 * rl, ym - 0.707 * rl)
    bu = bezier((xe + Lc, yT + s), (xe + Lc + 3, yT + s), (pu[0] - 2.5, pu[1] - 2.5), pu)
    t = np.radians(np.linspace(135, -135, 200))
    arc = (xcl + rl * np.cos(t), ym + rl * np.sin(t))
    bl = bezier(pl, (pl[0] - 2.5, pl[1] + 2.5), (xe + Lc + 3, yT), (xe + Lc, yT))
    ribbon(ax, np.r_[bu[0], arc[0][1:], bl[0][1:]], np.r_[bu[1], arc[1][1:], bl[1][1:]], W, "si")
    label(ax, xcl + 0.5, ym, "loop\nmirror", fs=FS_SMALL)
    ox, oy = sbend_xy(xe - 12, yT + s + 4.5, 12, -4.5)
    ribbon(ax, ox, oy, W, "si"); wg_straight(ax, x1 - 6, xe - 12, yT + s + 4.5, W, "si")
    arrow(ax, (x1 - 7, yT + s + 4.5), (x1 - 21, yT + s + 4.5), col=RED, lw=1.3, ms=8)
    label(ax, x1 - 23, yT + s + 4.5, "output", fs=FS_SMALL, col=RED, ha="right")
    # light path (one way; the loop mirror sends it back)
    for (xa_, xb_, y_) in ((24, 34, yb + 3.0), (x1 - 2, x1 - 14, yM + 3.0), (x1 + 8, x1 + 20, yT - 3.0)):
        arrow(ax, (xa_, y_), (xb_, y_), col=RED, lw=1.0, ms=6)
    scalebar(ax, 100, -9.5, 20, "20 µm")
    note(ax, "rings, gaps and Si layout to scale; waveguides drawn 0.9 µm wide; RSOA shortened", loc="upper left")
    print(f"ECL drawing: ring 1 at ({x1:.1f}, {c1:.1f}), ring 2 at ({x2:.1f}, {c2:.1f}); FSR {fsr(R1):.3f} / {fsr(R2):.3f} nm")
    save(fig, "ch26_ecl")


def fig_vernier():
    R1, R2 = 10.0, 11.0
    F1, F2 = fsr(R1), fsr(R2)
    FV = F1 * F2 / abs(F1 - F2)
    dF = abs(F1 - F2)
    print(f"Vernier: FSR1 {F1:.3f} nm, FSR2 {F2:.3f} nm, dFSR {dF:.3f} nm, FSR_V {FV:.1f} nm, gearing {F1/dF:.1f}; "
          f"one step needs {dF/HEATER:.1f} mW at {HEATER} nm/mW")
    k = np.arange(-25, 26)
    r1 = 1550 + k * F1; r2 = 1550 + k * F2; r2s = 1550 + dF + k * F2
    fig = plt.figure(figsize=(6.3, 4.6))
    XL = (1450, 1650)
    def comb(ax, ra, rb, title):
        ax.set_xlim(*XL); ax.set_ylim(-1.3, 1.75)
        for x in ra[(ra > XL[0]) & (ra < XL[1])]: ax.plot([x, x], [0.08, 0.95], color=C2, lw=1.3)
        for x in rb[(rb > XL[0]) & (rb < XL[1])]: ax.plot([x, x], [-0.95, -0.08], color=C1, lw=1.3)
        ax.axhline(0, color=MUTED, lw=0.5)
        best = [x for x in ra if np.min(abs(rb - x)) < 0.05 and XL[0] < x < XL[1]]
        for x in best:
            ax.axvspan(x - 1.4, x + 1.4, color=RED, alpha=0.15, lw=0)
            ax.text(x, 1.0, f"{x:.1f}", ha="center", va="bottom", fontsize=6.5, color=RED)
        ax.set_yticks([0.5, -0.5]); ax.set_yticklabels(["ring 1", "ring 2"]); ax.grid(False)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.text(XL[0] + 1, 1.75, title, fontsize=7.2, color=INK, va="top")
        return best
    a = fig.add_axes([0.11, 0.73, 0.86, 0.22]); best0 = comb(a, r1, r2, "both heaters off")
    a.set_xticklabels([])
    tag(a, "a")
    print("coincidences (unheated):", [f"{x:.2f}" for x in best0])
    i0 = int(np.argmin(np.abs(np.array(best0) - 1550)))
    xa_, xb_ = best0[i0], best0[i0 + 1]
    a.annotate("", xy=(xb_, -1.12), xytext=(xa_, -1.12), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    a.text((xa_ + xb_) / 2, -1.12, f"FSR$_V$ = {xb_ - xa_:.0f} nm", ha="center", va="center", fontsize=6.8,
           color=INK, bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))
    b = fig.add_axes([0.11, 0.45, 0.86, 0.22]); best1 = comb(b, r1, r2s, f"ring 2 heated: its comb moved by {dF:.2f} nm (about {dF/HEATER:.1f} mW)")
    print("coincidences (ring 2 +dFSR):", [f"{x:.2f}" for x in best1])
    b.set_xlabel("Wavelength (nm)")
    tag(b, "b")
    # lasing wavelength against the ring-2 heater power: argmax of gain x (drop1 x drop2)^2 on a fine grid
    lam = np.arange(1480.0, 1620.0, 0.002)
    d1 = drop(lam, R1)
    P = np.linspace(0, F2 / HEATER, 600)
    las = []
    for p in P:
        v = gain_window(lam) * (d1 * drop(lam, R2, HEATER * p)) ** 2
        las.append(lam[np.argmax(v)])
    las = np.array(las)
    steps = np.where(np.abs(np.diff(las)) > 2)[0]
    print("tuning over one FSR2 of heating (%.1f mW): lasing range %.1f-%.1f nm; jumps at P =" % (P[-1], las.min(), las.max()),
          ", ".join(f"{P[i+1]:.1f} mW ({las[i+1]-las[i]:+.2f} nm)" for i in steps))
    yl = las.copy(); yl[1:][np.abs(np.diff(las)) > 2] = np.nan
    both = 1550 + HEATER * P
    c = fig.add_axes([0.11, 0.08, 0.86, 0.27])
    c.plot(P, yl, color=C1, lw=2.0, solid_capstyle="butt", label=f"ring 2 heated: steps of FSR$_1$ = {F1:.2f} nm every {dF/HEATER:.1f} mW")
    c.plot(P[P <= 25], both[P <= 25], color=C3, lw=1.3, label=f"both rings heated together: continuous, {HEATER} nm/mW")
    c.set_xlim(0, 47); c.set_ylim(1495, 1648); c.set_yticks([1500, 1525, 1550, 1575, 1600])
    c.legend(loc="upper right")
    finish(c, "Heater power on ring 2 (mW)", "Lasing λ (nm)")
    tag(c, "c")
    save(fig, "ch26_vernier")


# ====================================================================== schematics
def fig_sil():
    fig = plt.figure(figsize=(6.3, 2.4))
    ax = fig.add_axes([0.0, 0.0, 0.60, 1.0]); frameless(ax, (-8, 100), (-26, 36))
    box(ax, -6, -8, 30, 16, "inp")
    wg_straight(ax, -6, 24, 0, 2.2, "q")
    label(ax, 9, 11.5, "DFB or FP laser\n(no isolator)", fs=FS_SMALL)
    box(ax, 28, -24, 70, 56, "ox", z=0)
    label(ax, 96, -21, "SiN chip", fs=FS_SMALL, ha="right", col=MUTED)
    wg_straight(ax, 28, 98, 0, 1.4, "sin")
    R = 15; cx, cy = 63, 0.7 + 1.4 + 0.9 + R
    wg_ring(ax, cx, cy, R, 1.4, "sin")
    label(ax, cx, cy + 1.5, "high-Q ring\n(Q ~ 10$^7$)", fs=FS_SMALL)
    a1 = FancyArrowPatch((cx + R + 4, cy - 2), (cx + R + 2, cy + 6), connectionstyle="arc3,rad=0.3", arrowstyle="-|>",
                         mutation_scale=7, color=RED, lw=1.0, zorder=7)
    ax.add_patch(a1)
    a2 = FancyArrowPatch((cx - R - 4, cy - 2), (cx - R - 2, cy + 6), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>",
                         mutation_scale=7, color=RED, lw=1.0, ls=(0, (3, 2)), zorder=7)
    ax.add_patch(a2)
    label(ax, cx + R + 4, cy + 11, "forward", fs=FS_SMALL, col=RED)
    label(ax, cx - R - 6, cy + 13, "backscattered", fs=FS_SMALL, col=RED)
    box(ax, 31, -1.8, 10, 3.6, "tin", alpha=0.6, z=1)
    label(ax, 36, -13.5, "heater: sets the phase of the feedback", fs=FS_SMALL, ha="left")
    ax.plot([36, 36], [-11.8, -2.0], color=MUTED, lw=0.6)
    arrow(ax, (31, 3.6), (43, 3.6), col=RED, lw=1.2, ms=7)
    arrow(ax, (58, -4.2), (42, -4.2), col=RED, lw=1.0, ms=7, ls=(0, (3, 2)))
    label(ax, 59, -4.2, "feedback to the laser", fs=FS_SMALL, col=RED, ha="left")
    arrow(ax, (86, 3.6), (98, 3.6), col=RED, lw=1.2, ms=7)
    label(ax, 92, 7.0, "out", fs=FS_SMALL, col=RED)
    panel(ax, "a", x=0.0, y=1.0)
    note(ax, "not to scale", loc="lower left")
    b = fig.add_axes([0.66, 0.20, 0.32, 0.70])
    f = np.linspace(-6, 6, 1201)
    b.plot(f, 1 / (1 + ((f - 2.2) / 1.6) ** 2), color=MUTED, lw=1.2)
    b.plot(f, 1 / (1 + (f / 0.06) ** 2), color=C4, lw=1.4)
    b.plot(f, 0.55 * (1 - 0.9 / (1 + (f / 0.25) ** 2)), color=C1, lw=0.9, ls=(0, (3, 2)))
    b.annotate("", xy=(0.3, 0.75), xytext=(1.9, 0.9), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7, mutation_scale=7))
    b.text(3.3, 1.02, "free-running:\nMHz linewidth", fontsize=6.5, color=MUTED, va="center")
    b.text(-0.5, 1.02, "locked: below 1 kHz,\non the ring resonance", fontsize=6.5, color=C4, va="center", ha="right")
    b.text(-5.8, 0.45, "ring\ntransmission", fontsize=6.5, color=C1, va="top")
    b.set_xticks([]); b.set_yticks([]); b.set_ylim(0, 1.15); b.grid(False)
    finish(b, "Optical frequency", "Power spectrum")
    tag(b, "b")
    b.text(1.0, -0.12, "schematic", transform=b.transAxes, ha="right", va="top", fontsize=6, color=MUTED, style="italic")
    save(fig, "ch26_sil")


def fig_multi():
    fig = plt.figure(figsize=(6.3, 3.9))
    ch = np.array([1546.12, 1549.32, 1552.52, 1555.75])
    nu = 299792.458 / ch
    print("reference channels (THz):", ", ".join(f"{v:.2f}" for v in nu), " spacing", ", ".join(f"{v*1e3:.0f}" for v in -np.diff(nu)), "GHz")
    # (a) laser array
    a = fig.add_axes([0.0, 0.52, 0.58, 0.46]); frameless(a, (0, 10), (0, 5.2), equal=False)
    for i in range(4):
        y = 4.3 - 1.05 * i
        block(a, 1.5, y, 2.0, 0.72, f"DFB λ$_{i+1}$", fc="#EFE9DC", fs=FS_SMALL)
        a.text(0.25, y, "I, T", ha="right", va="center", fontsize=6.0, color=ELEC)
        wire(a, [(2.5, y), (5.3, 2.72 + 0.35 * (1.5 - i))], col=OPT, lw=0.9)
    block(a, 6.2, 2.72, 1.8, 2.3, "multi-\nplexer", fs=FS_SMALL)
    wire(a, [(7.1, 2.72), (9.4, 2.72)], col=OPT, lw=1.4)
    a.text(8.25, 3.0, "4 λ, one\nwaveguide", ha="center", va="bottom", fontsize=6.3, color=INK)
    panel(a, "a", x=0.0, y=1.0)
    s1 = fig.add_axes([0.66, 0.60, 0.32, 0.34])
    for c in ch:
        s1.plot([c, c], [0, 1], color=C1, lw=2.0)
    s1.set_xlim(1543, 1559); s1.set_ylim(0, 1.25); s1.set_yticks([])
    s1.set_xticks([1546, 1550, 1554, 1558])
    s1.set_ylim(0, 1.5)
    s1.text(1550.9, 1.47, "reference-link channels,\n400 GHz (3.2 nm) apart", ha="center", va="top", fontsize=6.5, color=INK)
    s1.annotate("", xy=(ch[2], 1.06), xytext=(ch[1], 1.06), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=5))
    finish(s1, "Wavelength (nm)", "Power")
    # (b) comb source
    b = fig.add_axes([0.0, 0.02, 0.58, 0.46]); frameless(b, (0, 10), (0, 5.2), equal=False)
    block(b, 1.5, 2.6, 2.0, 0.8, "pump laser", fc="#EFE9DC", fs=FS_SMALL)
    wire(b, [(2.5, 2.6), (3.6, 2.6)], col=OPT, lw=1.0)
    b.add_patch(plt.Circle((4.35, 3.35), 0.6, fc="none", ec=MAT["sin"], lw=3.0, zorder=3))
    b.plot([3.6, 5.1], [2.6, 2.6], color=MAT["sin"], lw=3.0, zorder=3)
    b.text(4.35, 4.25, "SiN microring\n(Kerr comb)", ha="center", va="bottom", fontsize=6.3, color=INK)
    wire(b, [(5.1, 2.6), (6.0, 2.6)], col=OPT, lw=1.4)
    block(b, 6.85, 2.6, 1.6, 2.3, "demulti-\nplexer", fs=FS_SMALL)
    for i in range(5):
        y = 3.6 - 0.5 * i
        wire(b, [(7.65, y), (8.3, y)], col=OPT, lw=0.8)
        block(b, 8.85, y, 1.0, 0.36, "mod" if i < 4 else "…", fs=5.8, fc="#F3F6FB")
    panel(b, "b", x=0.0, y=1.0)
    s2 = fig.add_axes([0.66, 0.10, 0.32, 0.34])
    k = np.arange(-14, 15); env = 1 / np.cosh(k / 5.5) ** 2
    lines = 1550 + 3.2 * k
    for x, e in zip(lines, env):
        s2.plot([x, x], [0, e], color=C3, lw=1.3)
    s2.plot(lines, env, color=MUTED, lw=0.6, ls=":")
    s2.set_xlim(1500, 1600); s2.set_ylim(0, 1.5); s2.set_yticks([])
    s2.text(1550, 1.47, "equally spaced lines\n(illustrative envelope)", ha="center", va="top", fontsize=6.5, color=INK)
    finish(s2, "Wavelength (nm)", "Power")
    save(fig, "ch26_multi")


# ====================================================================== mode-locked laser (Section 26.8)
C_LIGHT = 2.998e8
MLL_LAM, MLL_NG, MLL_F, MLL_BW = 1310.0, 3.5, 20e9, 4.0    # nm, group index, repetition rate (Hz), locked bandwidth (nm FWHM)


def comb_field(f_rep, bw_nm, lam_nm=MLL_LAM, gdd_ps2=0.0, random_phase=False, seed=3, nfft=8192):
    """One round trip of the intensity of a comb of lines f_rep apart under a Gaussian power envelope of FWHM bw_nm
    (the model of the mll demo). Returns t (ps), I(t) over its mean, line offsets (GHz), line powers, envelope FWHM (Hz)."""
    dnu = C_LIGHT * bw_nm * 1e-9 / (lam_nm * 1e-9) ** 2
    K = int(np.ceil(2.5 * dnu / f_rep))   # amplitude envelope down to 2e-4
    k = np.arange(-K, K + 1); nu = k * f_rep
    P = np.exp(-4 * np.log(2) * (nu / dnu) ** 2)
    ph = (np.random.default_rng(seed).uniform(0, 2 * np.pi, k.size) if random_phase
          else 0.5 * gdd_ps2 * 1e-24 * (2 * np.pi * nu) ** 2)
    spec = np.zeros(nfft, complex); spec[k % nfft] = np.sqrt(P) * np.exp(1j * ph)
    I = np.abs(np.fft.ifft(spec) * nfft) ** 2; I /= I.mean()
    return np.arange(nfft) / nfft / f_rep * 1e12, I, nu / 1e9, P, dnu


def fwhm(t, I):
    i = int(np.argmax(I)); I = np.roll(I, I.size // 2 - i); h = I.max() / 2; c = I.size // 2
    lo = c
    while I[lo] > h: lo -= 1
    hi = c
    while I[hi] > h: hi += 1
    dt = t[1] - t[0]
    xl = lo + (h - I[lo]) / (I[lo + 1] - I[lo]); xh = hi - 1 + (I[hi - 1] - h) / (I[hi - 1] - I[hi])
    return (xh - xl) * dt


def gain_window(T=50.0, tau_g=300.0, tau_a=3.0, g0=2.4, q0=0.6, loss=0.35, ea=3.5, eg=0.4, tp=1.5):
    """Periodic steady state of a saturable gain g and a saturable absorber q (round-trip values) under a train of
    Gaussian pulses of FWHM tp (ps) and energy ea, eg in units of the absorber's and the gain's saturation energies:
    dq/dt = (q0 - q)/tau_a - q P/E_a, dg/dt = (g0 - g)/tau_g - g P/E_g (illustrative parameters)."""
    dt = 0.01; t = np.arange(-T / 2, T / 2, dt); s = tp / 2.3548
    P = np.exp(-t ** 2 / (2 * s * s)); P /= P.sum() * dt
    g, q = 0.8, q0
    for _ in range(40):
        G, Q = np.empty_like(t), np.empty_like(t)
        for i in range(t.size):
            G[i], Q[i] = g, q
            g += dt * ((g0 - g) / tau_g - g * P[i] * eg)
            q += dt * ((q0 - q) / tau_a - q * P[i] * ea)
    return t, G, Q, loss, P


def fig_mll():
    f, bw = MLL_F, MLL_BW
    L = C_LIGHT / (2 * MLL_NG * f)
    dl = (MLL_LAM * 1e-9) ** 2 * f / C_LIGHT * 1e12            # line spacing, pm
    t, I, nu, P, dnu = comb_field(f, bw)
    tau = fwhm(t, I)
    _, Ir, _, _, _ = comb_field(f, bw, random_phase=True)
    print(f"mll: L = {L*1e3:.3f} mm for {f/1e9:.0f} GHz at n_g = {MLL_NG}; line spacing {dl:.1f} pm; "
          f"envelope {dnu/1e9:.0f} GHz FWHM = {dnu/f:.1f} lines; pulse {tau:.3f} ps; TBP {tau*1e-12*dnu:.3f}; "
          f"peak/mean locked {I.max():.1f} (0.94/(f tau) = {0.939/(f*tau*1e-12):.1f}), random {Ir.max():.1f}")
    print(f"mll: 64 lines x 32 GBd x 2 bit = {64*32*2/1000:.3f} Tbit/s")
    tw, G, Q, loss, Pw = gain_window()
    net = G - Q - loss
    win = tw[net > 0]
    print(f"mll gain window: g before {G[0]:.3f}, q before {Q[0]:.3f}, net before {net[0]:+.3f}, "
          f"window {win.min():.2f} to {win.max():.2f} ps ({win.max()-win.min():.2f} ps)")

    fig = plt.figure(figsize=(6.3, 4.5))
    # (a) the two-section laser, side view
    a = fig.add_axes([0.0, 0.58, 0.56, 0.40]); frameless(a, (-6, 112), (-14, 30))
    box(a, 0, -10, 100, 8, "inp"); box(a, 0, -2, 100, 2.2, "q"); box(a, 0, 0.2, 100, 7, "inp")
    box(a, 1, 7.2, 84, 1.6, "metal"); box(a, 88, 7.2, 11, 1.6, "metal")
    a.plot([86.5, 86.5], [7.2, 10.5], color=MUTED, lw=0.6, ls=(0, (2, 2)))
    label(a, 43, 13.5, "gain section: forward current I", fs=FS_SMALL)
    label(a, 94, 17.5, "saturable\nabsorber:\nreverse bias V", fs=FS_SMALL)
    label(a, 22, -6, "n-InP", fs=FS_SMALL, col=MUTED); label(a, 20, 4, "p-InP", fs=FS_SMALL, col=MUTED)
    label(a, 8, -0.9, "active region", fs=FS_SMALL - 0.4, col="white", ha="left")
    xs = np.linspace(55, 75, 200); a.fill_between(xs, -0.9, -0.9 + 1.0 + 5.5 * np.exp(-((xs - 65) / 3.0) ** 2),
                                                  color=RED, alpha=0.55, lw=0, zorder=4)
    arrow(a, (70, 3.5), (80, 3.5), col=RED, lw=1.1, ms=7)
    label(a, 72, -6, "one pulse circulating", fs=FS_SMALL, col=RED)
    for xf in (0, 100): a.plot([xf, xf], [-10, 7.2], color=INK, lw=1.2)
    label(a, 0, -12.8, "cleaved facet", fs=FS_SMALL - 0.3, col=MUTED); label(a, 100, -12.8, "cleaved facet", fs=FS_SMALL - 0.3, col=MUTED)
    for k in range(3):
        xx = 103 + 3.2 * k; a.fill_between([xx, xx + 0.8], [-1.0, -1.0], [4.0, 4.0], color=RED, lw=0)
    label(a, 107, -5.5, "pulse\ntrain", fs=FS_SMALL, col=RED)
    dim(a, (0, 25.5), (100, 25.5), "L: one round trip, 2L, takes 1/f$_{rep}$", fs=FS_SMALL)
    panel(a, "a", x=0.0, y=1.02); label(a, 50, -12.8, "not to scale", fs=6.0, col=MUTED, italic=True)
    # (b) the net-gain window
    b = fig.add_axes([0.66, 0.62, 0.32, 0.33])
    m = (tw > -6) & (tw < 16)
    b.fill_between(tw[m], 0, Pw[m] / Pw.max() * 0.45, color=MUTED, alpha=0.25, lw=0, label="pulse")
    b.plot(tw[m], G[m], color=C1, lw=1.4, label="gain")
    b.plot(tw[m], Q[m] + loss, color=C4, lw=1.4, label="absorber + cavity loss")
    b.fill_between(tw[m], G[m], Q[m] + loss, where=net[m] > 0, color=AMBER, alpha=0.45, lw=0)
    b.annotate("", xy=(0.6, 0.62), xytext=(5.0, 0.42), arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=0.8, mutation_scale=7))
    b.text(5.3, 0.42, "net gain\nonly here", fontsize=6.3, color=AMBER, va="center")
    b.set_xlim(-6, 16); b.set_ylim(0, 1.1); b.set_yticks([0, 0.5, 1.0])
    finish(b, "Time (ps)", "Round-trip gain, loss"); b.legend(loc="lower right", fontsize=6.0, handlelength=1.4)
    tag(b, "b")
    # (c) the comb, (d) locked against random phases
    c = fig.add_axes([0.07, 0.09, 0.27, 0.36])
    lam = MLL_LAM - (MLL_LAM * 1e-9) ** 2 * nu * 1e9 / C_LIGHT * 1e9
    for x, p in zip(lam, P):
        c.plot([x, x], [0, p], color=C3, lw=0.7)
    c.set_xlim(MLL_LAM - 4.5, MLL_LAM + 4.5); c.set_ylim(0, 1.15); c.set_yticks([0, 0.5, 1])
    c.text(MLL_LAM, 1.12, f"{dl:.0f} pm apart", ha="center", va="top", fontsize=6.3, color=INK)
    finish(c, "Wavelength (nm)", "Line power"); tag(c, "c")
    d = fig.add_axes([0.45, 0.09, 0.53, 0.36])
    T = 1e12 / f
    tt = np.concatenate([t - T, t, t + T]); II = np.tile(np.roll(I, I.size // 2), 3); IR = np.tile(Ir, 3)
    d.plot(tt - T / 2, IR, color=MUTED, lw=0.6, label=f"random phases: noise (peak {Ir.max():.0f}× mean)")
    d.plot(tt - T / 2, II, color=C4, lw=1.1, label=f"locked phases: {tau:.2f} ps pulses (peak {I.max():.0f}× mean)")
    d.set_xlim(-T * 1.25, T * 1.25); d.set_ylim(0, I.max() * 1.3)
    finish(d, "Time (ps)", "Power / mean"); d.legend(loc="upper left", fontsize=6.0, ncol=1)
    tag(d, "d")
    save(fig, "ch26_mll")


if __name__ == "__main__":
    ALL = {"dfb": fig_dfb, "dfb_spectra": fig_dfb_spectra, "dbr": fig_dbr, "ecl": fig_ecl, "vernier": fig_vernier,
           "sil": fig_sil, "multi": fig_multi, "mll": fig_mll}
    for name in (sys.argv[1:] or list(ALL)):
        ALL[name]()
