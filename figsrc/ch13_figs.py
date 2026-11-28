"""Figures and numbers for Chapter 13 (Bragg gratings).

Run from the repository root:   python -I -X utf8 figsrc/ch13_figs.py [name ...]
Writes assets/figs/ch13_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.

The grating is the one of Worked Examples 13.1-13.2, the bragg demo (_includes/demos/bragg.html) and Lab 5: a
500 x 220 nm silicon strip, n_eff = 2.446 and n_g = 4.18 at 1550 nm (n_eff falls with wavelength at the rate n_g
sets), period 316.8 nm, kappa = 12.6 /mm, 300 periods. Spectra come from coupled-mode theory: the closed form for a
uniform grating and, for apodised or phase-shifted ones, a product of uniform-section matrices (as in the demo).
"""
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
NEFF, NG, LAM = 2.446, 4.18, 1.55e-6
PER = LAM / (2 * NEFF)                     # 316.8 nm
K0 = 12.6e3                                # 1/m (Worked Example 13.2)
KPDK = 1.4e5                               # 1/m, PDK upper value


def neff_l(l):
    return NEFF - (NG - NEFF) * (l - LAM) / LAM


def delta(l, per=PER):
    return 2 * np.pi * neff_l(l) / l - np.pi / per


def r_uniform(l, kap, L, per=PER):
    """Complex reflection of a uniform grating (coupled-mode theory)."""
    d = delta(l, per).astype(complex)
    s = np.sqrt(kap ** 2 - d ** 2 + 0j)
    return -1j * kap * np.sinh(s * L) / (s * np.cosh(s * L) + 1j * d * np.sinh(s * L))


def sec(l, d, kap):
    """Coupled-mode matrix of a uniform section of length l: maps (A, B) at its end to its start."""
    s = np.sqrt(kap ** 2 - d ** 2 + 0j)
    ch = np.cosh(s * l); sh = np.where(np.abs(s) > 1e-12, np.sinh(s * l) / np.where(np.abs(s) > 1e-12, s, 1), l)
    return np.array([[ch - 1j * d * sh, -1j * kap * sh], [1j * kap * sh, ch + 1j * d * sh]])


def mul(A, B):
    return np.einsum("ij...,jk...->ik...", A, B)


def grating(l, kz, L, shift_at=None):
    """Matrix of a grating cut into len(kz) sections with couplings kz; optional pi phase shift after section shift_at."""
    d = delta(l); n = len(kz); dl = L / n
    T = np.array([[np.ones_like(l, complex), np.zeros_like(l, complex)], [np.zeros_like(l, complex), np.ones_like(l, complex)]])
    P = np.array([[np.full_like(l, -1j, complex), 0 * l], [0 * l, np.full_like(l, 1j, complex)]])
    for i, k in enumerate(kz):
        T = mul(T, sec(dl, d, k))
        if shift_at is not None and i == shift_at: T = mul(T, P)
    return T


def refl(T):
    return np.abs(T[1, 0] / T[0, 0]) ** 2


def fwhm(x, y):
    i0 = np.argmax(y); h = y[i0] / 2
    lo = i0
    while lo > 0 and y[lo] > h: lo -= 1
    hi = i0
    while hi < len(y) - 1 and y[hi] > h: hi += 1
    f = lambda a, b: x[a] + (h - y[a]) * (x[b] - x[a]) / (y[b] - y[a])
    return f(hi - 1, hi) - f(lo, lo + 1)


def sidelobe_db(x, y):
    """Strongest reflection beyond the first minimum on each side of the peak, in dB below the peak."""
    i0 = np.argmax(y); lo = i0
    while lo > 0 and y[lo - 1] < y[lo]: lo -= 1
    hi = i0
    while hi < len(y) - 1 and y[hi + 1] < y[hi]: hi += 1
    side = max(y[:lo].max() if lo > 0 else 0, y[hi + 1:].max() if hi < len(y) - 1 else 0)
    return 10 * np.log10(side / y[i0])


def numbers():
    print(f"period {PER*1e9:.2f} nm; Delta n for kappa: 12.6/mm -> {K0*LAM/2:.5f}, 140/mm -> {KPDK*LAM/2:.4f}")
    for k in (K0, 40e3, KPDK):
        print(f"stop band (long grating) for kappa {k/1e3:.1f}/mm: {LAM**2*k/(np.pi*NG)*1e9:.2f} nm")


# ------------------------------------------------------------------ Figure 13.1: the grating to scale
def fig_geometry():
    P = PER * 1e6; w = 0.5; c = 0.05; nP = 6
    xs = nP * P + 0.84; ys = 0.88                          # drawing span (um); the figure height keeps 1:1 scale
    fig = plt.figure(figsize=(6.3, 6.3 * ys / xs / 0.70))
    ax = fig.add_axes([0.0, 0.30, 1.0, 0.70]); frameless(ax, (-0.42, nP * P + 0.42), (-0.43, 0.45))
    ax.set_aspect("equal", adjustable="datalim")
    # outline: lead-in, nP periods (wide half then narrow half, each sidewall stepping by c), lead-out
    top = [(-0.42, w / 2), (0, w / 2)]
    for i in range(nP):
        x = i * P
        top += [(x, w / 2 + c / 2), (x + P / 2, w / 2 + c / 2), (x + P / 2, w / 2 - c / 2), (x + P, w / 2 - c / 2)]
    top += [(nP * P, w / 2), (nP * P + 0.42, w / 2)]
    top = np.array(top); bot = top[::-1] * [1, -1]
    poly(ax, np.vstack([top, bot]), "si", z=2)
    box(ax, -0.42, -0.43, nP * P + 0.84, 0.88, "oxtop", z=0)
    # dimensions
    dim(ax, (0, w / 2 + c / 2 + 0.07), (P, w / 2 + c / 2 + 0.07), "")
    label(ax, P / 2, w / 2 + c / 2 + 0.135, f"Λ = {P*1000:.1f} nm", fs=7)
    dim(ax, (-0.3, -w / 2), (-0.3, w / 2), "")
    label(ax, -0.27, 0.0, "500 nm", fs=6.6, ha="left", bg=MAT["si"])
    xc = 2 * P + P / 2
    tick_dim(ax, (xc + 0.04, w / 2 - c / 2), (xc + 0.04, w / 2 + c / 2), "")
    callout(ax, (xc + 0.04, w / 2 + 0.005), (xc + 0.22, w / 2 + 0.16), "50 nm corrugation", fs=6.6)
    # forward wave and the partial reflections of successive periods
    arrow(ax, (-0.40, 0.05), (nP * P + 0.38, 0.05), col=RED, lw=1.1, ms=8)
    label(ax, nP * P + 0.38, 0.12, "forward wave", fs=6.6, col=RED, ha="right")
    for i in range(nP):
        x = i * P + P / 2
        arrow(ax, (x, -0.07), (x - 0.24, -0.07), col=BLUE, lw=0.9, ms=6)
    label(ax, 0.6 * P, -0.155, "reflections from each period, in phase when $2n_\\mathrm{eff}\\Lambda = \\lambda_B$", fs=6.6, col=BLUE, ha="left")
    scalebar(ax, nP * P - 0.02, -0.39, 0.2, "200 nm", above=True)
    panel(ax, "a", x=0.0, y=0.98)
    # effective-index profile along z and its first Fourier component
    b = fig.add_axes([0.0, 0.0, 1.0, 0.27]); b.set_xlim(-0.42, nP * P + 0.42); b.set_ylim(-1.0, 1.25); b.set_axis_off()
    z = np.linspace(0, nP * P, 4000)
    sq = np.where((z % P) < P / 2, 0.5, -0.5)
    b.plot(np.r_[-0.42, 0, z, nP * P, nP * P + 0.42], np.r_[0, 0, sq, 0, 0], color=INK, lw=1.0, drawstyle="default")
    b.plot(z, (2 / np.pi) * np.cos(2 * np.pi * (z - P / 4) / P) * 1.0, color=C2, lw=1.2, ls=(0, (3, 1.5)))
    b.text(-0.40, 0.5, "$n_\\mathrm{eff} + \\Delta n/2$", fontsize=6.6, color=INK, va="center")
    b.text(-0.40, -0.5, "$n_\\mathrm{eff} - \\Delta n/2$", fontsize=6.6, color=INK, va="center")
    b.text(nP * P + 0.05, 0.75, "first Fourier\ncomponent, $2\\Delta n/\\pi$", fontsize=6.6, color=C2, va="center", ha="left")
    panel(b, "b", x=0.0, y=1.08)
    save(fig, "ch13_geometry")


# ------------------------------------------------------------------ Figure 13.2: band diagram near the stop band
def fig_band():
    l = np.linspace(1520e-9, 1580e-9, 6001)
    d = delta(l)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL, sharey=True, gridspec_kw=dict(width_ratios=[1.5, 1]))
    for k, col, lab in ((KPDK, C1, "κ = 140 mm$^{-1}$"), (K0, C2, "κ = 12.6 mm$^{-1}$")):
        q = d ** 2 - k ** 2
        # add the exact band edges (q = 0) to the plotted points, so the two branches meet at K = pi/Lambda and the
        # decay-rate loop closes on Im K = 0 instead of stopping one sample short of the edge
        s_ = np.where(np.diff(np.sign(q)) != 0)[0]
        lp = np.insert(l, s_ + 1, l[s_] - q[s_] * (l[s_ + 1] - l[s_]) / (q[s_ + 1] - q[s_])); qp = np.insert(q, s_ + 1, 0.0)
        re = np.where(qp >= 0, np.sqrt(np.abs(qp)), np.nan); im = np.where(qp <= 0, np.sqrt(np.abs(qp)), np.nan)
        a1.plot(re / 1e3, lp * 1e9, color=col, lw=1.6, label=lab); a1.plot(-re / 1e3, lp * 1e9, color=col, lw=1.6)
        a2.plot(im / 1e3, lp * 1e9, color=col, lw=1.6)
        inside = l[q < 0]
        gap = (inside.max() - inside.min()) * 1e9
        print(f"band gap for kappa {k/1e3:.1f}/mm: {inside.min()*1e9:.2f}-{inside.max()*1e9:.2f} nm, width {gap:.2f} nm (formula {LAM**2*k/(np.pi*NG)*1e9:.2f})")
        if k == KPDK:
            for ax in (a1, a2): ax.axhspan(inside.min() * 1e9, inside.max() * 1e9, color=C1, alpha=0.08, lw=0)
            a1.text(-290, 1550, f"stop band\n{gap:.1f} nm", fontsize=6.8, color=C1, va="center")
            g1 = gap
        else:
            a1.annotate(f"{gap:.1f} nm", xy=(3, 1550), xytext=(40, 1550), fontsize=6.8, color=C2, va="center",
                        arrowprops=dict(arrowstyle="-", color=C2, lw=0.6))
    a1.set_xlim(-300, 300); a1.set_ylim(1522, 1578)
    finish(a1, "Bloch wavenumber $K - \\pi/\\Lambda$ (mm$^{-1}$)", "Wavelength (nm)")
    a2.set_xlim(0, 160)
    h, lb = a1.get_legend_handles_labels(); a2.legend(h, lb, loc="lower right", fontsize=6.8)
    finish(a2, "Decay rate Im $K$ (mm$^{-1}$)")
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=1.2)
    save(fig, "ch13_band")


# ------------------------------------------------------------------ Figure 13.3: reflection against kappa L
def fig_kappaL():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL)
    l = LAM + np.linspace(-6e-9, 6e-9, 6001)
    gap = LAM ** 2 * K0 / (np.pi * NG) * 1e9
    a1.fill_between([-gap / 2, gap / 2], 0, 1.0, color=MUTED, alpha=0.10, lw=0)
    for N, col in ((150, C3), (300, C2), (750, C1), (1500, C5)):
        L = N * PER; R = np.abs(r_uniform(l, K0, L)) ** 2
        a1.plot((l - LAM) * 1e9, R, color=col, lw=1.4, label=f"N = {N}, κL = {K0*L:.1f}")
        bw = LAM ** 2 / (NG * L) * np.sqrt((K0 * L / np.pi) ** 2 + 1) * 1e9
        print(f"kappa 12.6/mm, N {N}: L {L*1e6:.0f} um, kL {K0*L:.2f}, R_peak {R.max()*100:.1f} % (tanh^2 {np.tanh(K0*L)**2*100:.1f}), null BW {bw:.2f} nm")
    a1.text(0, 1.04, f"stop band {gap:.1f} nm", ha="center", fontsize=6.6, color=MUTED)
    a1.text(5.8, 1.13, "κ = 12.6 mm$^{-1}$", ha="right", va="center", fontsize=6.6, color=INK)
    a1.set_xlim(-6, 6); a1.set_ylim(0, 1.42); a1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    finish(a1, "Wavelength − 1550 nm (nm)", "Reflectivity")
    a1.legend(loc="upper left", fontsize=6.3, handlelength=1.2, borderaxespad=0.1, ncol=2, columnspacing=0.8)
    l = LAM + np.linspace(-22e-9, 22e-9, 8001)
    L = 300 * PER
    for k, col in ((K0, C2), (40e3, C3), (KPDK, C1)):
        R = np.abs(r_uniform(l, k, L)) ** 2
        a2.plot((l - LAM) * 1e9, R, color=col, lw=1.4, label=f"κ = {k/1e3:g} mm$^{{-1}}$, κL = {k*L:.1f}")
        bw = LAM ** 2 / (NG * L) * np.sqrt((k * L / np.pi) ** 2 + 1) * 1e9
        print(f"L 95 um, kappa {k/1e3:.1f}/mm: kL {k*L:.2f}, R_peak {R.max()*100:.2f} %, null BW {bw:.2f} nm, long-grating {LAM**2*k/(np.pi*NG)*1e9:.2f} nm")
    a2.set_xlim(-22, 22); a2.set_ylim(0, 1.42); a2.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    finish(a2, "Wavelength − 1550 nm (nm)", "Reflectivity")
    a2.text(21, 1.36, "L = 95 µm", ha="right", va="top", fontsize=6.6, color=INK)
    a2.legend(loc="upper left", fontsize=6.3, handlelength=1.2, borderaxespad=0.1)
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch13_kappaL")


# ------------------------------------------------------------------ Figure 13.4: apodisation
def fig_apod():
    N = 300; L = N * PER
    z = (np.arange(N) + 0.5) / N - 0.5
    gauss = np.exp(-(z / 0.22) ** 2)
    boost = 1 / gauss.mean()
    l = LAM + np.linspace(-15e-9, 15e-9, 6001)
    cases = [("uniform", np.full(N, K0), C1, "-"), ("Gaussian, same κ$_\\mathrm{max}$", K0 * gauss, C2, "-"),
             (f"Gaussian, κ$_\\mathrm{{max}}$ × {boost:.2f}", K0 * boost * gauss, C3, (0, (4, 1.5)))]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 2.95), gridspec_kw=dict(width_ratios=[1, 1.7]))
    for name, kz, col, ls in cases:
        zz = np.r_[-0.5, np.repeat(np.linspace(-0.5, 0.5, N + 1)[1:-1], 2), 0.5] * L * 1e6 + L * 1e6 / 2
        a1.plot(np.linspace(0, L * 1e6, N), kz / 1e3, color=col, lw=1.5, ls=ls, label=name)
        R = refl(grating(l, kz, L))
        a2.plot((l - LAM) * 1e9, 10 * np.log10(np.maximum(R, 1e-9)), color=col, lw=1.3, ls=ls, label=name)
        print(f"apodisation {name}: peak {R.max()*100:.1f} %, FWHM {fwhm((l-LAM)*1e9, R):.2f} nm, strongest side lobe {sidelobe_db((l-LAM)*1e9, R):.1f} dB")
    a1.set_xlim(0, L * 1e6); a1.set_ylim(0, 36)
    finish(a1, "Position along the grating (µm)", "κ (mm$^{-1}$)")
    a2.set_xlim(-15, 15); a2.set_ylim(-80, 3)
    finish(a2, "Wavelength − 1550 nm (nm)", "Reflectivity (dB)")
    h, lb = a1.get_legend_handles_labels()
    fig.legend(h, lb, loc="upper center", ncol=3, fontsize=6.8, handlelength=1.8, bbox_to_anchor=(0.5, 1.0))
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=1.8, rect=(0, 0, 1, 0.91))
    save(fig, "ch13_apod")


# ------------------------------------------------------------------ Figure 13.5: the Fabry-Perot cavity (Section 13.5)
def airy_T(phi, R1, R2, A=1.0):
    """Power transmission of a Fabry-Perot cavity: mirror reflectances R1, R2, single-pass power transmission A,
    round-trip phase phi (radians)."""
    rho = np.sqrt(R1 * R2) * A
    return (1 - R1) * (1 - R2) * A / ((1 - rho) ** 2 + 4 * rho * np.sin(phi / 2) ** 2)


def finesse_exact(rho):
    """FSR / FWHM of the Airy peak (exact); None when the fringes never fall to half the peak (rho < 3 - 2 sqrt 2)."""
    x = (1 - rho) / (2 * np.sqrt(rho))
    return np.pi / (2 * np.arcsin(x)) if x <= 1 else None


def dbr_cavity(l, N=300, Ns=316, nsec=60):
    """Two N-period gratings of Worked Example 13.2 around a spacer of Ns + 1/2 periods (a quarter-wave spacer plus
    Ns whole periods), so that one resonance sits at the Bragg wavelength."""
    Lg = N * PER
    P = np.array([[np.full_like(l, -1j, complex), 0 * l], [0 * l, np.full_like(l, 1j, complex)]])
    G = grating(l, np.full(nsec, K0), Lg)
    return mul(mul(mul(G, sec(Ns * PER, delta(l), 0.0)), P), G)


def fig_fp():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL)
    ph = np.linspace(-1.3, 1.3, 4001)
    for R, col in ((0.3, C2), (0.7, C3), (0.95, C1)):
        F = finesse_exact(R)
        a1.plot(ph, airy_T(2 * np.pi * ph, R, R), color=col, lw=1.4, label=f"R = {R:.2f}, F = {F:.1f}")
        print(f"Airy, lossless, R1 = R2 = {R}: finesse {F:.2f} (approximate formula {np.pi * np.sqrt(R) / (1 - R):.2f}),"
              f" T_min {airy_T(np.pi, R, R):.3f}")
    F95 = finesse_exact(0.95); hw = 0.5 / F95
    a1.annotate("", xy=(1, 1.08), xytext=(0, 1.08), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6))
    a1.text(0.5, 1.12, "FSR", fontsize=6.6, ha="center", va="bottom", color=INK)
    a1.annotate(f"FWHM =\nFSR / F", xy=(hw, 0.5), xytext=(0.17, 0.6), fontsize=6.6, color=C1, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=C1, lw=0.6))
    a1.set_xlim(-1.3, 1.3); a1.set_ylim(0, 1.62); a1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    a1.set_xticks([-1, -0.5, 0, 0.5, 1])
    finish(a1, "Round-trip phase / 2π (cycles from resonance)", "Transmission")
    a1.legend(loc="upper left", fontsize=6.2, borderaxespad=0.1, ncol=1)
    # (b) the Bragg-mirror cavity of Worked Example 13.3: transfer matrices against the Airy formula with L_eff
    N, Ns = 300, 316
    Lg = N * PER; Ls = (Ns + 0.5) * PER; R = np.tanh(K0 * Lg) ** 2; Lp = np.tanh(K0 * Lg) / (2 * K0); Leff = Ls + 2 * Lp
    l = LAM + np.linspace(-4e-9, 4e-9, 16001)
    Tm = 1 - refl(dbr_cavity(l, N, Ns))
    phi = 4 * np.pi * NG * Leff * (1 / l - 1 / LAM) * 1.0       # round-trip phase from the resonance at 1550 nm (group index)
    Ta = airy_T(phi, R, R)
    Rg = np.abs(r_uniform(l, K0, Lg)) ** 2
    a2.plot((l - LAM) * 1e9, Rg, color=MUTED, lw=1.0, ls=(0, (1, 1.5)), label="one mirror: reflectance")
    a2.plot((l - LAM) * 1e9, Ta, color=C2, lw=1.2, ls=(0, (4, 2)), label=f"Airy, R = {R:.2f}, $L_\\mathrm{{eff}}$ = {Leff * 1e6:.0f} µm")
    a2.plot((l - LAM) * 1e9, Tm, color=C1, lw=1.4, label="transfer matrices")
    lf = LAM + np.linspace(-0.4e-9, 0.4e-9, 16001); Tf = 1 - refl(dbr_cavity(lf, N, Ns)); fw = fwhm(lf * 1e9, Tf)
    FSR = LAM ** 2 / (2 * NG * Leff); Fe = finesse_exact(R)
    from scipy.signal import find_peaks
    pk, _ = find_peaks(Tm, height=0.5); offs = (l[pk] - LAM) * 1e9
    near = offs[np.argsort(np.abs(offs))[:3]]
    i1 = pk[np.argmin(np.abs(offs - 1.66))]
    lf1 = l[i1] + np.linspace(-0.5e-9, 0.5e-9, 8001); fw1 = fwhm(lf1 * 1e9, 1 - refl(dbr_cavity(lf1, N, Ns)))
    a2.annotate(f"FWHM {fw * 1000:.0f} pm\nQ ≈ {round(1550 / fw, -2):.0f}", xy=(fw / 2 + 0.02, 0.55), xytext=(1.0, 1.3), fontsize=6.4, color=C1,
                ha="left", va="center", arrowprops=dict(arrowstyle="-", color=C1, lw=0.6))
    a2.set_xlim(-4, 4); a2.set_ylim(0, 1.62); a2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    finish(a2, "Wavelength − 1550 nm (nm)", "Transmission, reflectance")
    a2.legend(loc="upper left", fontsize=6.0, borderaxespad=0.1, bbox_to_anchor=(0.0, 1.0), handlelength=1.8)
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch13_fp")
    print(f"DBR cavity: two {N}-period gratings, kL {K0 * Lg:.3f}, R {R:.4f}, penetration {Lp * 1e6:.1f} um, spacer {Ls * 1e6:.2f} um,"
          f" L_eff {Leff * 1e6:.1f} um, Airy FSR {FSR * 1e9:.3f} nm, finesse {Fe:.2f}, FWHM {FSR / Fe * 1e12:.0f} pm, Q {LAM / (FSR / Fe):.0f}")
    print(f"  transfer matrices: peaks nearest 1550 nm at {np.round(np.sort(near), 3)} nm; centre FWHM {fw * 1000:.1f} pm (Q {1550 / fw:.0f});"
          f" neighbour FWHM {fw1 * 1000:.0f} pm; one grating's reflectance at +1.66 nm {np.abs(r_uniform(np.array([LAM + 1.66e-9]), K0, Lg))[0] ** 2:.3f}")
    A = np.exp(-2 / 4.343 * 100 * Leff); rho = R * A
    print(f"  with 2 dB/cm over L_eff: single pass {A:.5f}, rho {rho:.4f}, T_max {(1 - R) ** 2 * A / (1 - rho) ** 2:.3f}, finesse {finesse_exact(rho):.2f};"
          f" photon lifetime (lossless) {LAM / (FSR / Fe) * LAM / (2 * np.pi * 3e8) * 1e12:.2f} ps")


# ------------------------------------------------------------------ Figure 13.6: quarter-wave-shifted cavity
def fig_cavity():
    N = 750; L = N * PER; ns = 750
    kz = np.full(ns, K0)
    l = LAM + np.linspace(-4e-9, 4e-9, 8001)
    Ts = 1 - refl(grating(l, kz, L, shift_at=ns // 2 - 1))
    Tu = 1 - np.abs(r_uniform(l, K0, L)) ** 2
    i0 = np.argmax(np.where(np.abs(l - LAM) < 0.5e-9, Ts, 0))
    # refine the peak and its width on a fine grid
    lf = l[i0] + np.linspace(-0.6e-9, 0.6e-9, 6001); Tf = 1 - refl(grating(lf, kz, L, shift_at=ns // 2 - 1))
    fw = fwhm(lf * 1e9, Tf); lp = lf[np.argmax(Tf)]
    print(f"cavity: {N} periods, kL {K0*L:.2f}, peak T {Tf.max()*100:.1f} % at {lp*1e9:.3f} nm, FWHM {fw*1000:.0f} pm, Q {lp*1e9/fw:.0f}")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL)
    a1.plot((l - LAM) * 1e9, Tu, color=MUTED, lw=1.1, ls=(0, (3, 2)), label="uniform")
    a1.plot((l - LAM) * 1e9, Ts, color=C1, lw=1.5, label="λ/4 shift in the middle")
    a1.set_xlim(-4, 4); a1.set_ylim(0, 1.32); a1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    a1.annotate(f"FWHM {fw*1000:.0f} pm, Q ≈ {round(lp*1e9/fw, -2):.0f}", xy=(0.07, 0.85), xytext=(0.3, 1.12), fontsize=6.6, color=C1,
                arrowprops=dict(arrowstyle="-", color=C1, lw=0.6), va="center", ha="left")
    finish(a1, "Wavelength − 1550 nm (nm)", "Transmission")
    a1.legend(loc="upper left", fontsize=6.6, ncol=2, borderaxespad=0.1, columnspacing=1.0)
    # field envelope |A|^2 + |B|^2 along z, normalised to the input, from the output end backwards
    for shifted, lam0, col, lab in ((True, lp, C1, "λ/4-shifted, on resonance"), (False, LAM, MUTED, "uniform, at $\\lambda_B$")):
        d = delta(np.array([lam0]))
        dl = L / ns; v = np.array([[1.0 + 0j], [0j]]); prof = [v.copy()]
        P = np.array([[-1j, 0], [0, 1j]])
        mats = []
        for i in range(ns):
            mats.append(sec(dl, d, K0)[:, :, 0])
            if shifted and i == ns // 2 - 1: mats.append(P)
        for M in reversed(mats):
            v = M @ v
            if M.shape == (2, 2) and not np.allclose(M, P): prof.append(v.copy())
        prof = np.array(prof[::-1])[:, :, 0]
        I = (np.abs(prof[:, 0]) ** 2 + np.abs(prof[:, 1]) ** 2) / np.abs(prof[0, 0]) ** 2
        zz = np.linspace(0, L * 1e6, len(I))
        a2.plot(zz, I, color=col, lw=1.5, ls="-" if shifted else (0, (3, 2)), label=lab)
        print(f"field envelope ({lab}): max {I.max():.1f} at z = {zz[np.argmax(I)]:.0f} um, end {I[-1]:.3f}")
    a2.set_xlim(0, L * 1e6); a2.set_yscale("log"); a2.set_ylim(0.05, 60)
    a2.set_yticks([0.1, 1, 10]); a2.set_yticklabels(["0.1", "1", "10"]); a2.minorticks_off()
    finish(a2, "Position along the grating (µm)", "$|A|^2 + |B|^2$ (input = 1)")
    a2.legend(loc="upper right", fontsize=6.6)
    a2.axvline(L * 1e6 / 2, color=C1, lw=0.6, ls=":")
    a2.text(L * 1e6 / 2 + 3, 0.3, "λ/4 shift", fontsize=6.6, color=C1, ha="left", va="center")
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch13_cavity")


# ------------------------------------------------------------------ Figure 13.7: contra-directional coupler
def fig_contradc():
    S = json.load(open(os.path.join(HERE, "ch06_sweep.json")))
    W = S["widths"]
    i1, i2 = W.index(0.55), W.index(0.45)
    n1, n2 = S["neff1550"][i1][0][0], S["neff1550"][i2][0][0]
    g1, g2 = S["ng_te1550"][i1], S["ng_te1550"][i2]
    per = LAM / (n1 + n2)
    n_l = lambda n0, ng, l: n0 - (ng - n0) * (l - LAM) / LAM

    def solve(f):
        x = LAM
        for _ in range(60): x = f(x)
        return x
    l11 = solve(lambda l: 2 * n_l(n1, g1, l) * per)
    l22 = solve(lambda l: 2 * n_l(n2, g2, l) * per)
    l12 = solve(lambda l: (n_l(n1, g1, l) + n_l(n2, g2, l)) * per)
    print(f"contra-DC: n_eff(550) {n1:.4f} (ng {g1:.3f}), n_eff(450) {n2:.4f} (ng {g2:.3f}); period {per*1e9:.1f} nm; "
          f"drop {l12*1e9:.1f} nm, wide-guide reflection {l11*1e9:.1f} nm, narrow-guide reflection {l22*1e9:.1f} nm")
    fig = plt.figure(figsize=(6.3, 2.6))
    ax = fig.add_axes([0.0, 0.0, 0.56, 1.0])
    P = per * 1e6; nP = 7; w1, w2, gap, c = 0.55, 0.45, 0.15, 0.04
    x0, x1 = -0.5, nP * P + 0.5
    frameless(ax, (x0 - 0.05, x1 + 0.05), (-1.05, 1.0))
    box(ax, x0 - 0.05, -1.05, x1 - x0 + 0.1, 2.05, "oxtop", z=0)
    y1 = gap / 2 + w1 / 2; y2 = -(gap / 2 + w2 / 2)          # centre lines: wide guide above, narrow below
    # wide guide: corrugation on its lower (inner) sidewall
    edge = [(x0, y1 - w1 / 2), (0, y1 - w1 / 2)]
    for i in range(nP):
        x = i * P; edge += [(x, y1 - w1 / 2 - c / 2), (x + P / 2, y1 - w1 / 2 - c / 2), (x + P / 2, y1 - w1 / 2 + c / 2), (x + P, y1 - w1 / 2 + c / 2)]
    edge += [(nP * P, y1 - w1 / 2), (x1, y1 - w1 / 2)]
    poly(ax, np.vstack([np.array(edge), [(x1, y1 + w1 / 2), (x0, y1 + w1 / 2)]]), "si", z=2)
    edge = [(x0, y2 + w2 / 2), (0, y2 + w2 / 2)]
    for i in range(nP):
        x = i * P; edge += [(x, y2 + w2 / 2 + c / 2), (x + P / 2, y2 + w2 / 2 + c / 2), (x + P / 2, y2 + w2 / 2 - c / 2), (x + P, y2 + w2 / 2 - c / 2)]
    edge += [(nP * P, y2 + w2 / 2), (x1, y2 + w2 / 2)]
    poly(ax, np.vstack([np.array(edge), [(x1, y2 - w2 / 2), (x0, y2 - w2 / 2)]]), "si", z=2)
    # ports
    arrow(ax, (x0, y1 + w1 / 2 + 0.09), (x0 + 0.45, y1 + w1 / 2 + 0.09), col=RED, lw=1.0, ms=7)
    label(ax, x0, y1 + w1 / 2 + 0.2, "in", fs=7, ha="left")
    arrow(ax, (x1 - 0.45, y1 + w1 / 2 + 0.09), (x1, y1 + w1 / 2 + 0.09), col=RED, lw=1.0, ms=7)
    label(ax, x1, y1 + w1 / 2 + 0.2, "through", fs=7, ha="right")
    arrow(ax, (x0 + 0.45, y2 - w2 / 2 - 0.09), (x0, y2 - w2 / 2 - 0.09), col=BLUE, lw=1.0, ms=7)
    label(ax, x0, y2 - w2 / 2 - 0.21, f"drop ({l12*1e9:.0f} nm band)", fs=7, ha="left", col=BLUE)
    label(ax, nP * P / 2, y1, "550 nm", fs=6.6); label(ax, nP * P / 2, y2, "450 nm", fs=6.6)
    dim(ax, (P, y1 + w1 / 2 + 0.1), (2 * P, y1 + w1 / 2 + 0.1), "")
    label(ax, 1.5 * P, y1 + w1 / 2 + 0.2, f"Λ = {per*1e9:.0f} nm", fs=6.6)
    scalebar(ax, nP * P - 0.45, -0.98, 0.5, "500 nm")
    note(ax, "illustrative dimensions", loc="lower left")
    panel(ax, "a", x=0.0, y=1.0)
    # phase matching
    b = fig.add_axes([0.66, 0.17, 0.33, 0.76])
    l = np.linspace(1480e-9, 1620e-9, 400)
    b1 = 2 * np.pi * n_l(n1, g1, l) / l / 1e6; b2 = 2 * np.pi * n_l(n2, g2, l) / l / 1e6
    KG = 2 * np.pi / per / 1e6
    b.plot(l * 1e9, 2 * b1, color=C2, lw=1.4, label="2β$_1$ (wide)")
    b.plot(l * 1e9, b1 + b2, color=C1, lw=1.6, label="β$_1$ + β$_2$")
    b.plot(l * 1e9, 2 * b2, color=C3, lw=1.4, label="2β$_2$ (narrow)")
    b.axhline(KG, color=INK, lw=0.8, ls=(0, (3, 2)))
    b.text(1615, KG + 0.07, "2π/Λ", fontsize=6.8, ha="right", va="bottom")
    for x, col in ((l22, C3), (l12, C1), (l11, C2)):
        b.plot(x * 1e9, KG, "o", color=col, ms=4, zorder=5)
        b.axvline(x * 1e9, color=col, lw=0.6, ls=":")
    b.set_xlim(1480, 1620); b.set_ylim(KG - 1.1, KG + 1.1); b.set_yticks([19.0, 19.5, 20.0, 20.5])
    b.set_xticks([l22 * 1e9, l12 * 1e9, l11 * 1e9]); b.set_xticklabels([f"{x*1e9:.0f}" for x in (l22, l12, l11)])
    finish(b, "Wavelength (nm)", "Wavenumber (µm$^{-1}$)")
    b.legend(loc="upper right", fontsize=6.3, handlelength=1.2, borderaxespad=0.1)
    tag(b, "b")
    save(fig, "ch13_contradc")
    return l11, l12, l22


# ------------------------------------------------------------------ Figure 13.8: photonic-crystal waveguide and cavity
def fig_phc():
    a = 0.40; r = 0.30 * a                       # illustrative lattice constant and hole radius (um)
    h = a * np.sqrt(3) / 2
    ncol, nrow = 13, 3
    fig = plt.figure(figsize=(6.3, 1.95))
    for k, (rect, kind) in enumerate((([0.0, 0.0, 0.49, 1.0], "W1"), ([0.51, 0.0, 0.49, 1.0], "L3"))):
        ax = fig.add_axes(rect); frameless(ax, (-0.25, (ncol - 1) * a + 0.45), (-(nrow + 0.75) * h, (nrow + 1.45) * h))
        box(ax, -0.25, -(nrow + 0.6) * h, (ncol - 1) * a + 0.7, 2 * (nrow + 0.6) * h, "si", z=1)
        removed = 0
        for j in range(-nrow, nrow + 1):
            for i in range(ncol + 1):
                x = i * a + (0.5 * a if j % 2 else 0) - (0.5 * a if j % 2 else 0) * 0
                if x > (ncol - 1) * a + 0.3: continue
                if kind == "W1" and j == 0: removed += 1; continue
                if kind == "L3" and j == 0 and i in (5, 6, 7): removed += 1; continue
                ax.add_patch(Circle((x, j * h), r, fc="white", ec=MUTED, lw=0.3, zorder=3))
        if kind == "W1":
            arrow(ax, (-0.2, 0), ((ncol - 1) * a + 0.4, 0), col=RED, lw=1.1, ms=8)
            label(ax, (ncol - 1) * a / 2, 0.13, "guided along the missing row", fs=6.6, col=RED)
            dim(ax, (0, -(nrow + 0.75) * h + 0.02), (a, -(nrow + 0.75) * h + 0.02), "")
            label(ax, a + 0.08, -(nrow + 0.6) * h - 0.02, "$a$ = 400 nm", fs=6.6, ha="left", va="top")   # below the slab edge
        else:
            ax.add_patch(Ellipse((6 * a, 0), 3.2 * a, 0.9 * h, fc=RED, alpha=0.18, lw=0, zorder=2))
            callout(ax, (6 * a, 0.12), (6 * a + 0.9, (nrow + 1.15) * h), "three holes removed: a cavity", fs=6.6, col=RED, lc=RED)
            scalebar(ax, (ncol - 1) * a - 0.75, -(nrow + 0.75) * h + 0.02, 1.0, "1 µm", above=False)
        panel(ax, "a" if kind == "W1" else "b", x=0.0, y=1.0)
        print(f"phc {kind}: a {a*1000:.0f} nm, r {r*1000:.0f} nm, holes removed {removed}")
    save(fig, "ch13_phc")


FIGS = {"geometry": fig_geometry, "band": fig_band, "kappaL": fig_kappaL, "apod": fig_apod, "fp": fig_fp, "cavity": fig_cavity,
        "contradc": fig_contradc, "phc": fig_phc}

if __name__ == "__main__":
    names = sys.argv[1:]
    if not names: numbers()
    for nme in names or list(FIGS):
        FIGS[nme]()
