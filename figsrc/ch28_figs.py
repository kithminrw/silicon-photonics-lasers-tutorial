"""Figures for Chapter 28 (semiconductor optical amplifiers).

Run from the repository root:  python -I -X utf8 figsrc/ch28_figs.py
NumPy and Matplotlib only. Prints every number the captions quote, then writes assets/figs/ch28_*.svg.

The amplifier is the one of Worked Example 28.1 and the soa demo: small-signal modal gain 35 /cm, internal loss
5 /cm, P_sat = 12 mW, n_sp = 2, homogeneous saturation dP/dz = (G0/(1 + P/Psat) - alpha_i) P along the length.

  ch28_geometry    top view of an angled-waveguide SOA chip (to scale) and the facet geometry (why the angle helps)
  ch28_saturation  gain against output power and output against input power for 0.5, 1 and 2 mm
  ch28_noise       output spectrum with ASE (illustrative) and noise figure against gain
  ch28_patterning  a saturated SOA amplifying a 10 Gb/s bit pattern (carrier-reservoir gain model)
  ch28_ripple      gain ripple from residual facet reflectivity, 20 dB gain, R = 1e-4 and 1e-3
  ch28_placement   booster, in-line and pre-amplifier positions in a link
  ch28_edfa        erbium levels and an EDFA
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *
from matplotlib.patches import FancyArrowPatch, Polygon

G0, AI, PSAT, NSP = 35.0, 5.0, 12.0, 2.0          # /cm, /cm, mW
NG, LAM = 3.6, 1550.0


def amp(Pin, L_mm, n=400):
    """Output power (mW) of an L_mm long SOA for input Pin (mW): RK4 along z."""
    L = L_mm * 0.1; dz = L / n; P = np.asarray(Pin, float).copy()
    f = lambda p: (G0 / (1 + p / PSAT) - AI) * p
    for _ in range(n):
        k1 = f(P); k2 = f(P + dz / 2 * k1); k3 = f(P + dz / 2 * k2); k4 = f(P + dz * k3)
        P = P + dz / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return P


def p3db(L_mm):
    """Input and output power (dBm) where the gain has dropped 3 dB below its small-signal value."""
    g0 = 10 * np.log10(amp(np.array([1e-6]), L_mm)[0] / 1e-6)
    lo, hi = -40.0, 25.0
    for _ in range(60):
        m = (lo + hi) / 2; p = 10 ** (m / 10)
        if 10 * np.log10(amp(np.array([p]), L_mm)[0] / p) > g0 - 3: lo = m
        else: hi = m
    pin = lo
    return g0, pin, pin + g0 - 3


# ====================================================================== Figure: geometry
def fig_geometry():
    th = 8.0; neff = 3.2
    tha = np.degrees(np.arcsin(neff * np.sin(np.radians(th))))
    print(f"angled SOA: waveguide at {th} deg to the facet normal; reflected wave {2*th:.0f} deg off the waveguide axis; "
          f"beam leaves at {tha:.1f} deg in air (n_eff {neff})")
    fig = plt.figure(figsize=(6.3, 2.5))
    a = fig.add_axes([0.0, 0.02, 0.62, 0.96]); frameless(a, (-190, 1190), (-90, 420))
    L, Wc = 1000.0, 300.0
    box(a, 0, 0, L, Wc, "inp")
    t = np.tan(np.radians(th)); y0 = Wc / 2 - L * t / 2
    xs = np.array([0, L]); ys = y0 + xs * t
    ribbon(a, xs, ys, 8.0, "q", z=3)
    poly(a, [(60, y0 + 60 * t - 22), (L - 60, y0 + (L - 60) * t - 22), (L - 60, y0 + (L - 60) * t + 22), (60, y0 + 60 * t + 22)],
         "metal", alpha=0.45, z=2)
    for x in (-10, L):
        box(a, x, 0, 10, Wc, VIOLET, alpha=0.6, z=4)
    # beams in air, refracted away from the facet normal
    ta = np.tan(np.radians(tha))
    a.plot([-170, 0], [y0 - 170 * ta, y0], color=RED, lw=1.4, zorder=5)
    arrow(a, (-170, y0 - 170 * ta), (-90, y0 - 90 * ta), col=RED, lw=1.4, ms=8)
    a.plot([L, L + 170], [y0 + L * t, y0 + L * t + 170 * ta], color=RED, lw=1.4, zorder=5)
    arrow(a, (L + 60, y0 + L * t + 60 * ta), (L + 170, y0 + L * t + 170 * ta), col=RED, lw=1.4, ms=8)
    label(a, -100, y0 + 40, "in", fs=FS, col=RED); label(a, L + 110, y0 + L * t - 45, "out", fs=FS, col=RED)
    label(a, 500, 255, "contact over the active waveguide", fs=FS_SMALL)
    label(a, 0, 345, "AR coating", fs=FS_SMALL, col=VIOLET); label(a, L, 345, "AR coating", fs=FS_SMALL, col=VIOLET)
    dim(a, (0, -40), (L, -40), "1 mm", fs=FS_SMALL)
    note(a, f"to scale, waveguide drawn 8 µm wide; tilt {th:.0f}°", loc="upper left")
    panel(a, "a", x=0.0, y=0.92)
    # (b) facet zoom
    b = fig.add_axes([0.64, 0.02, 0.36, 0.96]); frameless(b, (-6.5, 4.5), (-4.6, 4.6))
    box(b, -6.5, -4.6, 6.5, 9.2, "inp")
    box(b, 0, -4.6, 0.25, 9.2, VIOLET, alpha=0.6, z=4)
    tt = np.radians(th)
    zz = np.linspace(-6.5, 0, 50)
    ribbon(b, zz, zz * np.tan(tt), 1.0, "q", z=3)
    b.plot([-6.5, 4.5], [0, 0], color=MUTED, lw=0.6, ls=(0, (3, 2)))
    b.text(4.4, 0.25, "facet normal", ha="right", va="bottom", fontsize=6.2, color=MUTED)
    arrow(b, (-5.5, -5.5 * np.tan(tt)), (-1.2, -1.2 * np.tan(tt)), col=RED, lw=1.2, ms=7, z=6)
    arrow(b, (-0.05, 0.0), (-5.6 * np.cos(tt), 5.6 * np.sin(tt) + 0.0), col=RED, lw=1.0, ms=7, ls=(0, (3, 2)), z=6)
    ang = np.radians(tha)
    arrow(b, (0.3, 0.05), (0.3 + 4.0 * np.cos(ang), 0.05 + 4.0 * np.sin(ang)), col=RED, lw=1.3, ms=8)
    b.text(-3.3, 1.35, f"residual reflection, {2*th:.0f}° off\nthe guide: misses it", fontsize=6.2, color=RED, ha="center", va="bottom")
    b.text(1.2, 2.9, f"out at ≈ {tha:.0f}°", fontsize=6.2, color=RED, ha="left")
    b.text(-3.3, -1.3, f"guide at {th:.0f}° to the\nfacet normal", fontsize=6.2, color=INK, ha="center", va="top")
    b.text(0.4, -4.3, "AR", fontsize=6.2, color=VIOLET, ha="left", va="bottom", fontweight="bold")
    panel(b, "b", x=0.0, y=0.92)
    b.text(0.99, 0.01, "not to scale", transform=b.transAxes, ha="right", va="bottom", fontsize=6, color=MUTED, style="italic")
    save(fig, "ch28_geometry")


# ====================================================================== Figure: saturation for three lengths
def fig_saturation():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    pin_dbm = np.linspace(-40, 15, 400); pin = 10 ** (pin_dbm / 10)
    for L, col in ((0.5, C3), (1.0, C1), (2.0, C4)):
        pout = amp(pin, L); g = 10 * np.log10(pout / pin); po = 10 * np.log10(pout)
        g0, pi3, po3 = p3db(L)
        print(f"L = {L} mm: small-signal gain {g0:.1f} dB, -3 dB output {po3:.1f} dBm (input {pi3:.1f} dBm), "
              f"max output in range {po.max():.1f} dBm")
        a.plot(po, g, color=col, label=f"{L:g} mm")
        a.plot([po3], [g0 - 3], "o", color=col, ms=4)
        b.plot(pin_dbm, po, color=col, label=f"{L:g} mm")
        b.plot([pi3], [po3], "o", color=col, ms=4)
    a.set_xlim(-20, 20); a.set_ylim(0, 30)
    finish(a, "Output power (dBm)", "Gain (dB)", legend=True, loc="upper right")
    a.text(-19, 1.0, "dots: gain 3 dB below\nits small-signal value", fontsize=6.5, color=INK, va="bottom")
    tag(a, "a")
    b.set_xlim(-40, 15); b.set_ylim(-30, 20)
    finish(b, "Input power (dBm)", "Output power (dBm)", legend=True, loc="lower right")
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch28_saturation")


# ====================================================================== Figure: ASE and noise figure
def nf(G, nsp=NSP, ai=AI, g=G0):
    return 10 * np.log10(2 * nsp * (G - 1) / G * g / (g - ai))


def fig_noise():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.15]))
    # (a) output spectrum: ASE density n_sp h nu (G - 1) G0/(G0 - alpha_i) in 0.1 nm, with an illustrative parabolic
    #     gain spectrum (peak 35 /cm at 1550 nm, 40 nm half-width); signal -15 dBm in (the soa demo's default)
    lam = np.unique(np.r_[np.linspace(1500, 1600, 401), np.linspace(1549.7, 1550.3, 61)])
    gl = G0 * np.clip(1 - ((lam - 1550) / 40) ** 2, 0, None)
    Gl = np.exp((gl - AI) * 0.1)
    hnu = 6.626e-34 * 2.998e8 / (lam * 1e-9)
    B = 2.998e8 * 0.1e-9 / (lam * 1e-9) ** 2                     # Hz in 0.1 nm
    dg = gl - AI; dg = np.where(np.abs(dg) < 1e-6, 1e-6, dg)                  # S = n_sp h nu Gamma g (G - 1)/(Gamma g - alpha_i), any g > 0
    ase_w = np.where(gl > 0, NSP * hnu * (Gl - 1) * gl / dg * B, 1e-15) + 1e-15
    ase = 10 * np.log10(ase_w * 1e3)
    pin_dbm = -15.0
    pout = 10 * np.log10(amp(np.array([10 ** (pin_dbm / 10)]), 1.0)[0])
    print(f"ASE at the gain peak: {ase.max():.1f} dBm per 0.1 nm; signal {pin_dbm:.0f} dBm in -> {pout:.1f} dBm out; "
          f"OSNR {pout - ase.max():.1f} dB in 0.1 nm")
    sig = 10 * np.log10(10 ** (ase / 10) + 10 ** (pout / 10) * np.exp(-((lam - 1550) / 0.05) ** 2))
    a.fill_between(lam, -80, ase, color=C2, alpha=0.25, lw=0)
    a.plot(lam, sig, color=C1, lw=1.1)
    a.axvspan(1547, 1553, color=C3, alpha=0.12, lw=0)
    a.text(1551.5, pout + 1.5, f"signal, {pout:.0f} dBm", ha="left", va="bottom", fontsize=6.5, color=C1)
    a.text(1575, -55, "ASE", ha="center", fontsize=7.0, color=C2)
    a.text(1554, -25, "optical\nfilter", ha="left", fontsize=6.5, color=C3)
    a.set_xlim(1500, 1600); a.set_ylim(-70, 8); a.set_yticks([-60, -40, -20, 0])
    finish(a, "Wavelength (nm)", "Power per 0.1 nm (dBm)")
    a.text(0.02, 0.97, "gain spectrum\nillustrative", transform=a.transAxes, ha="left", va="top", fontsize=6, color=MUTED, style="italic")
    tag(a, "a")
    # (b) noise figure against small-signal gain (length varied)
    L = np.linspace(0.02, 3.0, 400)            # mm
    G = np.exp((G0 - AI) * L * 0.1)
    gdb = 10 * np.log10(G)
    ideal = 10 * np.log10(2 * 1 * (G - 1) / G)
    real = nf(G)
    b.plot(gdb, ideal, color=MUTED)
    b.plot(gdb, real, color=C1)
    b.plot(gdb, real + 3, color=C4, ls=(0, (4, 2)))
    b.text(29.5, 2.75, "n$_{sp}$ = 1, no internal loss: 3 dB limit", ha="right", va="top", fontsize=6.5, color=MUTED)
    b.text(29.5, 6.4, "n$_{sp}$ = 2, α$_i$ = 5 cm$^{-1}$", ha="right", va="top", fontsize=6.5, color=C1)
    b.text(29.5, 9.4, "same, after a 3 dB input coupler", ha="right", va="top", fontsize=6.5, color=C4)
    G1 = np.exp(3.0)
    print(f"noise figure at 1 mm (G {10*np.log10(G1):.1f} dB): {nf(G1):.2f} dB; quantum limit {10*np.log10(2):.2f} dB; "
          f"high-gain limit for n_sp 2, alpha 5: {10*np.log10(4*G0/(G0-AI)):.2f} dB")
    b.plot([10 * np.log10(G1)], [nf(G1)], "o", color=C1, ms=4)
    b.annotate(f"1 mm: {nf(G1):.1f} dB", xy=(10 * np.log10(G1), nf(G1)), xytext=(13, 4.2), fontsize=6.5, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.axhline(10 * np.log10(2), color=MUTED, lw=0.6, ls=":")
    b.set_xlim(0, 30); b.set_ylim(0, 11)
    finish(b, "Small-signal gain (dB)", "Noise figure (dB)")
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch28_noise")


# ====================================================================== Figure: patterning
TAU = 200e-12                                    # s, gain recovery time (Section 28.4: 100 ps to 1 ns)


def reservoir(Pin_mW, dt, h0):
    """Carrier-reservoir model of an SOA (integrated gain h = ln G): dh/dt = (h0 - h)/tau - Pin (e^h - 1)/Esat."""
    Esat = PSAT * 1e-3 * TAU                     # J
    h = np.empty_like(Pin_mW); hh = h0
    for k, p in enumerate(Pin_mW):
        for _ in range(4):
            hh += dt / 4 * ((h0 - hh) / TAU - p * 1e-3 * (np.exp(hh) - 1) / Esat)
        h[k] = hh
    return h


def fig_patterning():
    bits = np.array([0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0])
    rate = 10e9; spb = 64; dt = 1 / rate / spb
    p1, p0 = 1.0, 0.05                            # mW in the waveguide ("1" and "0" levels)
    # raised-cosine edges, 30 % of a bit
    nrz = np.repeat(bits.astype(float), spb)
    k = np.arange(-spb // 2, spb // 2 + 1); w = np.cos(np.pi * k / (0.6 * spb)) ** 2 * (np.abs(k) < 0.3 * spb)
    nrz = np.convolve(nrz, w / w.sum(), mode="same")
    pin = p0 + (p1 - p0) * nrz
    h0 = (G0 - AI) * 0.1                          # ln of the 1 mm small-signal gain (13 dB)
    pre = np.full(40 * spb, pin.mean())           # settle on the average power first
    h = reservoir(np.r_[pre, pin], dt, h0)[len(pre):]
    G = np.exp(h); pout = pin * G
    t = np.arange(len(pin)) * dt * 1e9
    gdb = 10 * np.log10(G)
    print(f"patterning: 10 Gb/s, '1' = {p1} mW, '0' = {p0} mW in, tau = {TAU*1e12:.0f} ps, small-signal gain {10*np.log10(np.exp(h0)):.1f} dB; "
          f"gain {gdb.min():.1f}-{gdb.max():.1f} dB; mean output {pout.mean():.1f} mW")
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.3, 3.4), sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1]))
    a.plot(t, pin * np.exp(h0), color=MUTED, lw=1.0, ls=(0, (3, 2)), label="input × small-signal gain")
    a.plot(t, pout, color=C1, lw=1.4, label="output")
    a.set_ylim(0, 22.5)
    finish(a, None, "Power (mW)")
    a.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2)
    for i, bt in enumerate(bits):
        a.text((i + 0.5) / rate * 1e9, 21.6, str(bt), ha="center", va="center", fontsize=6.0, color=MUTED)
    tag(a, "a")
    b.plot(t, gdb, color=C4, lw=1.3)
    b.axhline(10 * np.log10(np.exp(h0)), color=MUTED, lw=0.6, ls=":")
    b.text(0.62, 10 * np.log10(np.exp(h0)) - 0.15, "small-signal gain", ha="left", va="top", fontsize=6.5, color=MUTED)
    b.set_ylim(gdb.min() - 1.2, 10 * np.log10(np.exp(h0)) + 0.8)
    b.set_xlim(0, t[-1])
    finish(b, "Time (ns)", "Gain (dB)")
    tag(b, "b")
    fig.tight_layout(h_pad=0.6)
    save(fig, "ch28_patterning")


# ====================================================================== Figure: facet ripple
def fig_ripple():
    Gs, L = 100.0, 1.0e-3                          # single-pass gain (20 dB), 1 mm
    fsr = (LAM * 1e-9) ** 2 / (2 * NG * L) * 1e9
    dl = np.linspace(0, 3 * fsr, 1200)
    phi = 2 * np.pi * NG * L * dl * 1e-9 / (LAM * 1e-9) ** 2
    fig, ax = plt.subplots(figsize=(4.6, 2.3))
    for R, col in ((1e-4, C1), (1e-3, C4)):
        r = Gs * R
        Gfp = (1 - R) ** 2 * Gs / ((1 - r) ** 2 + 4 * r * np.sin(phi) ** 2)
        y = 10 * np.log10(Gfp)
        rip = 20 * np.log10((1 + r) / (1 - r))
        print(f"R = {R:.0e} each facet, G = 20 dB: ripple {rip:.2f} dB (computed {y.max()-y.min():.2f} dB); FSR {fsr*1e3:.0f} pm")
        exp = int(np.log10(R))
        ax.plot(dl * 1e3, y, color=col, label=f"R = 10$^{{{exp}}}$: ripple {rip:.2g} dB")
    ax.axhline(20, color=MUTED, lw=0.6, ls=":")
    ax.set_xlim(0, 3 * fsr * 1e3); ax.set_ylim(19, 21.6)
    finish(ax, "Wavelength offset (pm)", "Gain (dB)", legend=True, loc="upper right")
    ax.legend(loc="upper right", ncol=1)
    save(fig, "ch28_ripple")


# ====================================================================== Figure: SOA positions in a link
def soa_sym(ax, x, y, w=0.9, h=0.7, lab="SOA"):
    ax.add_patch(Polygon([(x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x + w / 2, y)], closed=True, fc="#F6E3C0",
                         ec=INK, lw=0.8, zorder=3))
    ax.text(x - w / 8, y, lab, ha="center", va="center", fontsize=5.8, color=INK, zorder=4)


def fig_placement():
    fig, ax = geom_axes(figsize=(6.3, 1.55), xlim=(0, 16.6), ylim=(-1.45, 1.35), equal=False)
    y = 0.4
    items = [(0.9, "laser"), (2.6, "modulator")]
    for x, t in items:
        block(ax, x, y, 1.4, 0.7, t, fs=6.3)
    soa_sym(ax, 4.3, y)
    block(ax, 6.3, y, 1.9, 0.7, "switch matrix,\nphased array", fs=5.8)
    soa_sym(ax, 8.2, y)
    ax.plot([9.0, 10.8], [y, y], color=OPT, lw=1.0, zorder=2)
    ax.add_patch(plt.matplotlib.patches.Ellipse((9.9, y), 0.5, 0.9, fc="none", ec=OPT, lw=0.9, zorder=2))
    ax.text(9.9, y + 0.62, "fibre", ha="center", fontsize=6.0, color=MUTED)
    soa_sym(ax, 11.4, y)
    block(ax, 12.85, y, 1.0, 0.7, "filter", fs=6.0)
    block(ax, 14.2, y, 0.9, 0.7, "PD", fs=6.3)
    block(ax, 15.6, y, 1.0, 0.7, "TIA", fs=6.3)
    for x0, x1 in ((1.6, 1.9), (3.3, 3.85), (4.75, 5.35), (7.25, 7.75), (8.65, 9.0), (10.8, 10.95), (11.85, 12.35),
                   (13.35, 13.75)):
        wire(ax, [(x0, y), (x1, y)], col=OPT, lw=1.0, ms=6)
    wire(ax, [(14.65, y), (15.1, y)], col=ELEC, lw=1.0, ms=6)
    for x, t1, t2 in ((4.3, "booster", "high output,\nruns saturated"), (8.2, "in-line", "moderate gain,\nlinear, low noise"),
                      (11.4, "pre-amplifier", "low NF, high gain,\nASE filtered")):
        ax.text(x, -0.3, t1, ha="center", va="top", fontsize=6.8, color=INK, fontweight="bold")
        ax.text(x, -0.62, t2, ha="center", va="top", fontsize=6.2, color=MUTED)
    save(fig, "ch28_placement")


# ====================================================================== Figure: erbium levels and EDFA
def fig_edfa():
    hc = 1239.84
    E980, E1480, E1530 = hc / 980, hc / 1480, hc / 1530
    print(f"Er levels: 980 nm = {E980:.3f} eV, 1480 nm = {E1480:.3f} eV, 1530 nm = {E1530:.3f} eV")
    fig = plt.figure(figsize=(6.3, 2.4))
    a = fig.add_axes([0.08, 0.04, 0.36, 0.90])
    a.set_xlim(0, 11.5); a.set_ylim(-0.08, 1.45); a.grid(False)
    for e0, e1, nm, lab in ((0.0, 0.06, "$^4$I$_{15/2}$", "ground"), (E1530 - 0.01, E1530 + 0.05, "$^4$I$_{13/2}$", "τ ≈ 10 ms"),
                            (E980 - 0.01, E980 + 0.03, "$^4$I$_{11/2}$", "")):
        a.add_patch(plt.Rectangle((1.0, e0), 7.0, e1 - e0, fc=GRID, ec=INK, lw=0.6))
        a.text(8.2, (e0 + e1) / 2 + 0.03, nm, va="center", fontsize=7.5, color=INK)
        if lab: a.text(8.25, e0 - 0.04, lab, va="center", ha="left", fontsize=6.3, color=MUTED)
    arrow(a, (2.0, 0.03), (2.0, E980), col=C1, lw=1.5, ms=8)
    a.text(1.75, E980 / 2, "980 nm\npump", ha="right", va="center", fontsize=6.5, color=C1)
    arrow(a, (4.7, 0.03), (4.7, E1480), col=C3, lw=1.5, ms=8)
    a.text(4.45, 0.38, "1480 nm\npump", ha="right", va="center", fontsize=6.5, color=C3)
    arrow(a, (2.5, E980), (3.2, E1530 + 0.04), col=MUTED, lw=0.9, ms=6, ls=(0, (2, 2)))
    a.text(3.3, (E980 + E1530) / 2 + 0.06, "fast, non-radiative", fontsize=6.2, color=MUTED, va="center")
    arrow(a, (6.4, E1530 + 0.02), (6.4, 0.03), col=RED, lw=1.8, ms=9)
    a.text(6.65, 0.42, "signal\n1530–1565 nm\n(stimulated)", fontsize=6.5, color=RED, va="center")
    a.set_xticks([])
    finish(a, None, "Energy (eV)")
    a.spines["bottom"].set_visible(False)
    tag(a, "a")
    b = fig.add_axes([0.50, 0.0, 0.50, 1.0]); frameless(b, (0, 10), (0.75, 5.0), equal=False)
    y = 3.2
    block(b, 1.0, y, 1.1, 0.6, "isolator", fs=5.8)
    block(b, 2.9, y, 1.3, 0.7, "WDM\ncoupler", fs=5.8)
    block(b, 2.9, 1.3, 1.5, 0.7, "980 nm\npump laser", fs=5.8, fc="#EFE9DC")
    wire(b, [(2.9, 1.65), (2.9, y - 0.35)], col=C1, lw=1.0, ms=6)
    for k in range(4):
        b.add_patch(plt.matplotlib.patches.Ellipse((5.6, y), 1.6 - 0.12 * k, 1.3 - 0.12 * k, fc="none", ec=RED, lw=0.9, zorder=2))
    b.text(5.6, y - 1.0, "Er-doped fibre,\nmetres long", ha="center", va="top", fontsize=6.3, color=INK)
    block(b, 8.0, y, 1.1, 0.6, "isolator", fs=5.8)
    wire(b, [(0.0, y), (0.45, y)], col=OPT, lw=1.0, ms=6)
    wire(b, [(1.55, y), (2.25, y)], col=OPT, lw=1.0, ms=6)
    b.plot([3.55, 4.8], [y, y], color=OPT, lw=1.0)
    wire(b, [(6.4, y), (7.45, y)], col=OPT, lw=1.0, ms=6)
    wire(b, [(8.55, y), (9.9, y)], col=OPT, lw=1.4, ms=7)
    b.text(0.1, y + 0.45, "signal in", fontsize=6.3, color=INK)
    b.text(9.9, y + 0.45, "amplified\nsignal out", fontsize=6.3, color=INK, ha="right")
    panel(b, "b", x=0.0, y=0.98)
    save(fig, "ch28_edfa")


if __name__ == "__main__":
    fig_geometry(); fig_saturation(); fig_noise(); fig_patterning(); fig_ripple(); fig_placement(); fig_edfa()
