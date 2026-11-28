"""Figures and numbers for Chapter 12 (ring resonators).

Run from the worktree root:   python -I -X utf8 figsrc/ch12_figs.py
Writes assets/figs/ch12_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.

The ring is the one of Table 12.1 and the ring demo (_includes/demos/ring.html): a 500 x 220 nm silicon strip,
n_eff = 2.446, n_g = 4.18 at 1550 nm, R = 10 um, 2 dB/cm. The bus-ring coupling is the femwell-fitted supermode
model of Chapter 9 (figsrc/ch09_supermodes.py): dn = 0.0205 exp(-8.75 (g - 0.2 um)), L_x = lambda / (2 dn),
integrated along the curved gap: L_eff = sqrt(2 pi R / 8.75), kappa^2 = sin^2(pi L_eff / (2 L_x)).
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

NEFF, NG, LAM = 2.446, 4.18, 1.55          # um
R0, W, H = 10.0, 0.5, 0.22                 # um
LOSS_DB = 2.0                              # dB/cm


def kappa2(R, g):
    dn = 0.0205 * np.exp(-8.75 * (g - 0.2)); lx = LAM / (2 * dn); leff = np.sqrt(2 * np.pi * R / 8.75)
    return np.sin(np.minimum(np.pi / 2, np.pi * leff / (2 * lx))) ** 2


def a_of(loss_db, R=R0):
    alpha = loss_db * 100 / 4.343           # 1/m
    return np.exp(-alpha * 2 * np.pi * R * 1e-6 / 2)


def neff_l(l):
    return NEFF - (NG - NEFF) * (l - LAM) / LAM


def phi_l(l, R=R0):
    return 2 * np.pi * neff_l(l) * 2 * np.pi * R / l


def res_lambda(m, R=R0):
    x = NEFF * 2 * np.pi * R / m
    for _ in range(50): x = neff_l(x) * 2 * np.pi * R / m
    return x


def allpass(phi, a, t):
    """Complex through-port field: (t - a e^{-j phi}) / (1 - a t e^{-j phi})."""
    e = np.exp(-1j * phi)
    return (t - a * e) / (1 - a * t * e)


def adddrop(phi, a, t1, t2):
    e = np.exp(-1j * phi)
    den = 1 - t1 * t2 * a * e
    thr = (t1 - t2 * a * e) / den
    drp = -np.sqrt((1 - t1 ** 2) * (1 - t2 ** 2) * a) * np.exp(-1j * phi / 2) / den
    return thr, drp


def fwhm_pm(a, t, R=R0):
    L = 2 * np.pi * R
    return (1 - a * t) * LAM ** 2 / (np.pi * NG * L * np.sqrt(a * t)) * 1e6


def detune_phi(dl_pm, R=R0):
    """Round-trip phase offset from resonance for a wavelength offset dl (pm), group index included."""
    return -2 * np.pi * NG * 2 * np.pi * R * (dl_pm * 1e-6) / LAM ** 2


def critical_gap(loss_db, R=R0):
    a = a_of(loss_db, R); lo, hi = 0.1, 0.6
    for _ in range(80):
        m = (lo + hi) / 2
        if np.sqrt(1 - kappa2(R, m)) < a: lo = m          # still over-coupled: widen the gap
        else: hi = m
    return (lo + hi) / 2


A0 = a_of(LOSS_DB)
QI = 2 * np.pi * NG / (LAM * 1e-6 * LOSS_DB * 100 / 4.343)


def numbers():
    print(f"a = {A0:.5f}, Q_i = {QI:.3g}, FSR(1550) = {LAM**2/(NG*2*np.pi*R0)*1e3:.3f} nm")
    for g in (0.2, 0.25, 0.3):
        k2 = kappa2(R0, g); t = np.sqrt(1 - k2); fw = fwhm_pm(A0, t)
        tmin = (A0 - t) ** 2 / (1 - A0 * t) ** 2
        bu = k2 / (1 - A0 * t) ** 2
        print(f"gap {g*1000:.0f} nm: kappa2 {100*k2:.2f} %, t {t:.5f}, FWHM {fw:.1f} pm, Q_L {1550e3/fw:.3g}, ER {-10*np.log10(tmin):.1f} dB, build-up {bu:.0f}")
    print(f"critical gap at 2 dB/cm: {1000*critical_gap(2.0):.0f} nm; at 3.6 dB/cm: {1000*critical_gap(3.6):.0f} nm; at 1 dB/cm: {1000*critical_gap(1.0):.0f} nm")


# ------------------------------------------------------------------ Figure 12.1: geometry and definitions
def fig_geometry():
    g = 0.2
    fig = plt.figure(figsize=(6.3, 2.6))
    span = (-15.0, 15.0)
    cc = R0 + g + W                                     # centre-to-centre ring/bus
    for k, (rect, ad) in enumerate((([0.0, 0.0, 0.355, 1.0], False), ([0.385, 0.0, 0.355, 1.0], True))):
        ax = fig.add_axes(rect); frameless(ax, span, (-14.6, 15.4))
        wg_ring(ax, 0, 0, R0, W, "si")
        wg_straight(ax, -14, 14, -cc, W, "si")
        if ad: wg_straight(ax, -14, 14, cc, W, "si")
        # circulating light (counter-clockwise for light entering from the left on the lower bus)
        xs, ys = arc_xy(0, 0, R0 - 2.0, 225, 330)
        ax.plot(xs, ys, color=RED, lw=1.0); arrow(ax, (xs[-2], ys[-2]), (xs[-1], ys[-1]), col=RED, lw=1.0, ms=7)
        arrow(ax, (-14.0, -cc - 1.6), (-10.0, -cc - 1.6), col=RED, lw=1.0, ms=7)
        label(ax, -14.0, -cc - 3.0, "in", ha="left", fs=7.5)
        arrow(ax, (10.0, -cc - 1.6), (14.0, -cc - 1.6), col=RED, lw=1.0, ms=7)
        label(ax, 14.0, -cc - 3.0, "through", ha="right", fs=7.5)
        label(ax, 0, -cc - 2.2, r"$t_1$, $\kappa_1$" if ad else r"$t$, $\kappa$", fs=7.5)
        label(ax, 0, 4.6, r"$a$, $\phi = \beta L$", fs=7.5)
        label(ax, 0, 3.0, "round trip", fs=6.8, col=MUTED)
        # radius
        ang = np.radians(200)
        dim(ax, (0, 0), (R0 * np.cos(ang), R0 * np.sin(ang)), "")
        label(ax, -5.6, 0.5, "$R$ = 10 µm", fs=7)
        if ad:
            arrow(ax, (-10.0, cc + 1.6), (-14.0, cc + 1.6), col=RED, lw=1.0, ms=7)
            label(ax, -9.4, cc + 1.6, "drop", ha="left", fs=7.5)
            label(ax, 9.4, cc + 1.6, "add", ha="right", fs=7.5, col=MUTED)
            label(ax, 0, cc + 2.2, "$t_2$, $\\kappa_2$", fs=7.5)
        if not ad:
            scalebar(ax, 8.5, 12.0, 5.0, "5 µm")
        panel(ax, "b" if ad else "a", x=0.0, y=1.0)
    # cross-section through the coupling point
    ax = fig.add_axes([0.76, 0.12, 0.24, 0.76]); frameless(ax, (-0.95, 0.95), (-0.55, 0.75))
    box(ax, -0.95, -0.55, 1.9, 0.55, "ox"); box(ax, -0.95, 0, 1.9, 0.75, "oxtop")
    xr = -(g / 2 + W / 2); xb = g / 2 + W / 2
    cbox(ax, xr, 0, W, H, "si"); cbox(ax, xb, 0, W, H, "si")
    label(ax, xr, H / 2, "ring", fs=6.5); label(ax, xb, H / 2, "bus", fs=6.5)
    dim(ax, (-g / 2, H + 0.09), (g / 2, H + 0.09), "")
    label(ax, 0, H + 0.2, "gap 200 nm", fs=6.5, bg="white")
    dim(ax, (xb - W / 2, -0.1), (xb + W / 2, -0.1), "500 nm", text_off=(0, -0.09))
    dim(ax, (xr - W / 2 - 0.08, 0), (xr - W / 2 - 0.08, H), "")
    label(ax, xr - W / 2 - 0.12, H / 2, "220 nm", fs=6.3, ha="right", rot=90)
    label(ax, 0.9, -0.45, "SiO$_2$", fs=6.5, ha="right", col=MUTED)
    scalebar(ax, -0.9, -0.47, 0.5, "500 nm")
    panel(ax, "c", x=0.0, y=1.06)
    save(fig, "ch12_geometry")


# ------------------------------------------------------------------ Figure 12.2: coupling regimes, intensity and phase
def fig_regimes():
    gc = critical_gap(LOSS_DB)
    cases = [(0.2, "200 nm, over", C1), (0.25, "250 nm, over", C3),
             (gc, f"{1000*gc:.0f} nm, critical", INK), (0.3, "300 nm, under", C2)]
    dl = np.linspace(-40, 40, 4001)
    ph = detune_phi(dl)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL)
    for g, lab, col in cases:
        t = np.sqrt(1 - kappa2(R0, g)); E = allpass(ph, A0, t)
        T = np.abs(E) ** 2
        lw = 1.3 if col == INK else 1.6
        a1.plot(dl, 10 * np.log10(np.maximum(T, 1e-6)), color=col, lw=lw, label=lab)
        p = np.unwrap(np.angle(E)); p -= p[0]
        a2.plot(dl, p / np.pi, color=col, lw=lw)
        print(f"regime {lab}: T_min {10*np.log10(max(T.min(),1e-9)):.1f} dB, phase swing {(p.max()-p.min())/np.pi:.2f} pi, net {p[-1]/np.pi:.2f} pi")
    a1.set_ylim(-40, 1.5); a1.set_xlim(-40, 40)
    finish(a1, "Detuning from resonance (pm)", "Through-port transmission (dB)")
    a1.legend(loc="lower left", fontsize=6.6, handlelength=1.4, borderaxespad=0.2)
    a2.set_xlim(-40, 40); a2.set_ylim(-1.15, 2.15); a2.set_yticks([-1, -0.5, 0, 0.5, 1, 1.5, 2])
    a2.set_yticklabels(["−π", "", "0", "", "π", "", "2π"])
    finish(a2, "Detuning from resonance (pm)", "Through-port phase")
    a2.text(-38, 2.0, "over-coupled: the phase\nturns by a full 2π", ha="left", va="top", fontsize=6.6, color=C1)
    a2.text(38, -0.8, "under-coupled: it swings\nand returns", ha="right", va="center", fontsize=6.6, color=C2)
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch12_regimes")


# ------------------------------------------------------------------ Figure 12.3: add-drop ring
def fig_adddrop():
    g = 0.2; t = np.sqrt(1 - kappa2(R0, g))
    dl = np.linspace(-80, 80, 4001); ph = detune_phi(dl)
    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    for a, ls, lab in ((1.0, (0, (3, 2)), "lossless"), (A0, "-", "2 dB/cm")):
        thr, drp = adddrop(ph, a, t, t)
        Tt, Td = np.abs(thr) ** 2, np.abs(drp) ** 2
        ax.plot(dl, 10 * np.log10(np.maximum(Tt, 1e-6)), color=C2, ls=ls, lw=1.5 if ls == "-" else 1.1)
        ax.plot(dl, 10 * np.log10(np.maximum(Td, 1e-6)), color=C1, ls=ls, lw=1.5 if ls == "-" else 1.1)
        i0 = np.argmin(np.abs(dl))
        fw = fwhm_pm(a * t, t)
        print(f"add-drop {lab}: drop peak {10*np.log10(Td[i0]):.2f} dB, through min {10*np.log10(max(Tt[i0],1e-12)):.1f} dB, FWHM {fw:.1f} pm, Q_L {1550e3/fw:.3g}, drop at +-40 pm {10*np.log10(Td[np.argmin(np.abs(dl-40))]):.1f} dB")
    ax.set_xlim(-80, 80); ax.set_ylim(-40, 2)
    finish(ax, "Detuning from resonance (pm)", "Transmission (dB)")
    ax.text(-60, -15.0, "drop", color=C1, fontsize=7.5, fontweight="bold", va="top")
    ax.text(60, -2.4, "through", color=C2, fontsize=7.5, fontweight="bold", va="top", ha="center")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=MUTED, lw=1.5, label="2 dB/cm"), Line2D([], [], color=MUTED, lw=1.1, ls=(0, (3, 2)), label="lossless")],
              loc="lower right", fontsize=6.8)
    save(fig, "ch12_adddrop")


# ------------------------------------------------------------------ Figure 12.4: anatomy of the resonances
def fig_anatomy():
    g = 0.25; t = np.sqrt(1 - kappa2(R0, g))
    ms = [98, 99, 100, 101, 102]
    lr = {m: res_lambda(m) for m in ms}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.25, 1]))
    l = np.linspace(1.529, 1.566, 70001)
    T = np.abs(allpass(phi_l(l), A0, t)) ** 2
    # resample so every narrow dip is drawn at its full depth
    for m in ms:
        if 1.529 < lr[m] < 1.566:
            ll = lr[m] + np.linspace(-60e-6, 60e-6, 241)
            l = np.concatenate([l, ll]); T = np.concatenate([T, np.abs(allpass(phi_l(ll), A0, t)) ** 2])
    o = np.argsort(l); l, T = l[o], T[o]
    a1.plot(1000 * l, T, color=C1, lw=1.0)
    inside = [m for m in ms if 1.529 < lr[m] < 1.566]
    for m in inside:
        a1.text(1000 * lr[m], 1.05, f"$m$ = {m}", ha="center", fontsize=6.6, color=INK)
    print("resonances (nm):", {m: round(1000 * lr[m], 3) for m in ms})
    pairs = list(zip(inside[1:], inside[:-1]))           # higher m = shorter wavelength
    for m_hi, m_lo in pairs:
        x0, x1 = 1000 * lr[m_hi], 1000 * lr[m_lo]
        dim(a1, (x0, 0.55), (x1, 0.55), "", lw=0.7)
        a1.text((x0 + x1) / 2, 0.6, f"FSR {x1-x0:.2f} nm", ha="center", va="bottom", fontsize=6.6, color=INK)
        print(f"FSR between m={m_hi} and {m_lo}: {x1-x0:.3f} nm")
    a1.set_ylim(0, 1.17); a1.set_xlim(1529, 1566)
    finish(a1, "Wavelength (nm)", "Through-port transmission")
    # one resonance
    m = 99; l0 = lr[m]
    dl = np.linspace(-40, 40, 4001)
    Tz = np.abs(allpass(phi_l(l0 + dl * 1e-6), A0, t)) ** 2
    a2.plot(dl, Tz, color=C1)
    tmin = Tz.min(); half = (1 + tmin) / 2
    # FWHM from the curve
    idx = np.where(Tz < half)[0]; i0, i1 = idx[0], idx[-1]
    xl = dl[i0 - 1] + (half - Tz[i0 - 1]) * (dl[i0] - dl[i0 - 1]) / (Tz[i0] - Tz[i0 - 1])   # interpolated half-depth crossings
    xr = dl[i1] + (half - Tz[i1]) * (dl[i1 + 1] - dl[i1]) / (Tz[i1 + 1] - Tz[i1])
    fw = xr - xl; er = -10 * np.log10(tmin)                     # measured at this resonance, not the 1550 nm formula
    print(f"m=99 at {1000*l0:.3f} nm: FWHM {fw:.2f} pm (formula {fwhm_pm(A0, t):.2f}), T_min {tmin:.4f}, ER {er:.1f} dB, Q_L {1000*l0/(fw*1e-3):.3g}, finesse {LAM**2/(NG*2*np.pi*R0)*1e6/fw:.0f}")
    dim(a2, (xl, half), (xr, half), "")
    a2.text(xr + 2.5, half, f"FWHM\n{fw:.1f} pm", ha="left", va="center", fontsize=6.8, color=INK)
    a2.annotate("", xy=(-27, tmin), xytext=(-27, 1.0), arrowprops=dict(arrowstyle="<|-|>", color=C4, lw=0.8, mutation_scale=6))
    a2.plot([-30, 0], [tmin, tmin], color=C4, lw=0.6, ls=":")
    a2.text(-28.5, 0.47, f"extinction\n{er:.1f} dB", ha="right", va="center", fontsize=6.8, color=C4)
    a2.text(39, 0.18, f"$Q_L = \\lambda/\\mathrm{{FWHM}}$\n= {1000*l0/(fw*1e-3)/1e3:.0f} 000", ha="right", va="center", fontsize=6.8, color=INK)
    a2.set_xlim(-40, 40); a2.set_ylim(0, 1.1)
    finish(a2, f"Detuning from {1000*l0:.2f} nm (pm)", "Through-port transmission")
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=1.6)
    save(fig, "ch12_anatomy")


# ------------------------------------------------------------------ Figure 12.5: design curves against the gap
def fig_gapdesign():
    gs = np.linspace(0.15, 0.40, 2001)
    k2 = kappa2(R0, gs); t = np.sqrt(1 - k2)
    L = 2 * np.pi * R0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL)
    Qc = 2 * np.pi * NG * L / (LAM * k2)                 # coupling loss per round trip kappa^2
    QL = LAM * 1e3 / (fwhm_pm(A0, t) * 1e-3)
    a1.semilogy(1000 * gs, Qc, color=C5, lw=1.3, label="$Q_c$ (coupling)")
    a1.semilogy(1000 * gs, QI + 0 * gs, color=MUTED, lw=1.3, ls=(0, (4, 2)), label="$Q_i$ (2 dB/cm)")
    a1.semilogy(1000 * gs, QL, color=C1, lw=1.8, label="$Q_L$ (loaded)")
    for g in (0.2, 0.25, 0.3):
        tt = np.sqrt(1 - kappa2(R0, g)); q = LAM * 1e3 / (fwhm_pm(A0, tt) * 1e-3)
        a1.plot(1000 * g, q, "o", color=C1, ms=4)
    gc = critical_gap(LOSS_DB)
    a1.axvline(1000 * gc, color=MUTED, lw=0.7, ls=":")
    a1.text(1000 * gc + 3, 1.3e4, f"$Q_c = Q_i$\n{1000*gc:.0f} nm", fontsize=6.6, color=MUTED, va="bottom")
    a1.set_xlim(150, 400); a1.set_ylim(1e4, 3e6)
    finish(a1, "Coupling gap (nm)", "Quality factor")
    a1.legend(loc="upper left", fontsize=6.8)
    for loss, col in ((1.0, C3), (2.0, C1), (3.6, C2)):
        a = a_of(loss)
        tmin = (a - t) ** 2 / (1 - a * t) ** 2
        a2.plot(1000 * gs, -10 * np.log10(np.maximum(tmin, 1e-6)), color=col, label=f"{loss:g} dB/cm")
        print(f"loss {loss} dB/cm: critical gap {1000*critical_gap(loss):.0f} nm; ER at 200/250/300 nm: " +
              ", ".join(f"{-10*np.log10((a-np.sqrt(1-kappa2(R0,g)))**2/(1-a*np.sqrt(1-kappa2(R0,g)))**2):.1f}" for g in (0.2, 0.25, 0.3)))
    for g in (0.2, 0.25, 0.3):
        tt = np.sqrt(1 - kappa2(R0, g)); er = -10 * np.log10((A0 - tt) ** 2 / (1 - A0 * tt) ** 2)
        a2.plot(1000 * g, er, "o", color=C1, ms=4)
    a2.set_xlim(150, 400); a2.set_ylim(0, 40)
    finish(a2, "Coupling gap (nm)", "Extinction (dB)")
    a2.legend(loc="upper left", fontsize=6.8)
    a2.text(160, 17, "over-\ncoupled", fontsize=6.6, color=MUTED, ha="left")
    a2.text(395, 22, "under-\ncoupled", fontsize=6.6, color=MUTED, ha="right")
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch12_gapdesign")


# ------------------------------------------------------------------ Figure 12.6: split resonance (coupled-mode theory)
def fig_split():
    g = 0.3; k2 = kappa2(R0, g); t = np.sqrt(1 - k2)
    L = 2 * np.pi * R0
    Qc = 2 * np.pi * NG * L / (LAM * k2)
    fw_i = 1550e3 / QI; fw_c = 1550e3 / Qc; fw = fw_i + fw_c         # linewidths in pm
    print(f"split: 300 nm ring, FWHM_i {fw_i:.2f} pm, FWHM_c {fw_c:.2f} pm, FWHM_L {fw:.2f} pm (Q_L {1550e3/fw:.3g})")
    d = np.linspace(-30, 30, 3001)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL)
    for s, col in ((0.0, C6), (1.0, C3), (3.0, C1)):
        gg = s * fw / 2                                   # splitting 2g = s * FWHM
        D = 1j * d + fw / 2                               # rates in pm (half-widths)
        den = D ** 2 + gg ** 2
        thr = 1 - fw_c * D / den
        ref = fw_c * 1j * gg / den
        Tt, Rr = np.abs(thr) ** 2, np.abs(ref) ** 2
        lab = "no backscatter" if s == 0 else f"splitting {s:g} × FWHM"
        a1.plot(d, Tt, color=col, label=lab, lw=1.5)
        a2.plot(d, Rr, color=col, lw=1.5)
        print(f"  2g = {s} FWHM ({2*gg:.1f} pm): T_min {Tt.min():.3f}, R_max {Rr.max():.3f}")
    a1.set_xlim(-30, 30); a1.set_ylim(0, 1.05)
    finish(a1, "Detuning (pm)", "Through-port transmission")
    a1.legend(loc="lower left", fontsize=6.6, borderaxespad=0.2)
    a2.set_xlim(-30, 30); a2.set_ylim(0, 0.42)
    finish(a2, "Detuning (pm)", "Power reflected to the input")
    # sketch: the scatterer couples the clockwise and counter-clockwise modes; the reflected wave leaves by the input
    ins = a2.inset_axes([0.56, 0.5, 0.44, 0.5]); frameless(ins, (-2.3, 2.3), (-1.75, 1.35))
    wg_ring(ins, 0, 0, 1.0, 0.12, "si"); wg_straight(ins, -2.2, 2.2, -1.2, 0.12, "si")
    for r0, th0, th1, col in ((0.72, 210, 330, RED), (0.72, 150, 30, BLUE)):
        xs, ys = arc_xy(0, 0, r0, th0, th1)
        ins.plot(xs, ys, color=col, lw=0.9); arrow(ins, (xs[-2], ys[-2]), (xs[-1], ys[-1]), col=col, lw=0.9, ms=6)
    ins.plot([np.cos(np.radians(60))], [np.sin(np.radians(60))], "o", color=INK, ms=3.5, zorder=8)
    label(ins, 1.1, 1.05, "scatterer", fs=6.2, ha="left")
    label(ins, 0, -0.35, "CCW", fs=6.2, col=RED); label(ins, 0, 0.35, "CW", fs=6.2, col=BLUE)
    # "in" above the bus and "reflected" below it, so the longer label stays clear of the ring
    arrow(ins, (-2.2, -0.92), (-1.3, -0.92), col=RED, lw=0.9, ms=6); arrow(ins, (-1.3, -1.5), (-2.2, -1.5), col=BLUE, lw=0.9, ms=6)
    label(ins, -2.25, -0.8, "in", fs=6.2, ha="left", va="bottom"); label(ins, -2.25, -1.62, "reflected", fs=6.2, ha="left", va="top", col=BLUE)
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch12_split")


if __name__ == "__main__":
    numbers()
    fig_geometry(); fig_regimes(); fig_adddrop(); fig_anatomy(); fig_gapdesign(); fig_split()
