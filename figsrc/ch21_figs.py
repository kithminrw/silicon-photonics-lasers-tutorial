"""Figures and numbers for Chapter 21 (photodetectors and receivers), Sections 21.2-21.5. The front-end figures of
Sections 21.8-21.9 are drawn by figsrc/ch21_rx.py.

Run from the worktree root:   python -I -X utf8 figsrc/ch21_figs.py
Writes assets/figs/ch21_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.

Models are those of the chapter and its demos:
- photodiode bandwidth (Worked Example 21.1, _includes/demos/pdbw.html): v_sat 6e4 m/s, eps_r 16.2, 5 fF parasitic,
  70 ohm, f_t = 0.45 v_sat/d, f_RC = 1/(2 pi R C), 1/f^2 = 1/f_t^2 + 1/f_RC^2; responsivity 0.9 x 1.25 A/W x absorbed
  fraction x 0.92 (waveguide) or 0.95 (normal incidence), alpha 3000 /cm (assumed), overlap 0.5, waveguide width 4 um;
- receiver sensitivity (Worked Example 21.2, _includes/demos/rx.html): 50 Gb/s, B = 35 GHz, 0.9 A/W, 20 pA/sqrt(Hz),
  ER 4 dB, dark current 100 nA, BER 1e-12, APD excess noise F = kM + (1 - k)(2 - 1/M).
"""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
from figstyle import *
from geomstyle import *

VS, EPS, CPAR, RL, WWG, GAM, ETA, RMAX, ALPHA = 6e4, 16.2 * 8.854e-12, 5e-15, 70.0, 4.0, 0.5, 0.9, 1.25, 3000.0
QE, RB, RESP, IN, ID = 1.602e-19, 50e9, 0.9, 20e-12, 1e-7
B = 0.7 * RB


# ------------------------------------------------------------------ Figure 21.1: Ge-on-Si photodiodes
def fig_pd():
    fig = plt.figure(figsize=(6.3, 3.55))
    # (a) vertical PIN, waveguide-fed, cross-section to scale
    ax = fig.add_axes([0.0, 0.47, 0.49, 0.53]); frameless(ax, (-3.6, 3.6), (-0.6, 2.35))
    box(ax, -3.6, -0.6, 7.2, 0.6, "ox", z=0); box(ax, -3.6, 0, 7.2, 2.35, "oxtop", z=0)
    box(ax, -3.6, 0, 7.2, 0.22, "pdop", z=1); box(ax, -3.6, 0, 1.2, 0.22, "pp", z=2); box(ax, 2.4, 0, 1.2, 0.22, "pp", z=2)
    box(ax, -2.0, 0.22, 4.0, 0.5, "ge", z=2); box(ax, -2.0, 0.72, 4.0, 0.1, "nn", z=3)
    box(ax, -0.4, 0.82, 0.8, 1.2, "metal", z=3)
    for xc in (-3.0, 3.0):
        box(ax, xc - 0.2, 0.22, 0.4, 1.8, "metal", z=3)
    arrow(ax, (1.2, 0.3), (1.2, 0.68), col=RED, lw=1.1, ms=6, z=6); arrow(ax, (-1.2, 0.3), (-1.2, 0.68), col=RED, lw=1.1, ms=6, z=6)
    label(ax, 0.0, 0.47, "intrinsic Ge, 0.5 µm", fs=FS_SMALL)
    label(ax, 1.25, 1.0, "n$^{+}$ Ge", fs=FS_SMALL, ha="left")
    label(ax, -3.5, -0.3, "p-Si; light travels into the page", fs=FS_SMALL, ha="left")
    dim(ax, (-2.0, 1.25), (2.0, 1.25), "", lw=0.6); label(ax, -1.15, 1.42, "4 µm", fs=FS_SMALL)
    scalebar(ax, 2.2, -0.52, 1.0, "1 µm")
    panel(ax, "a", x=0.0, y=1.0)
    ax.text(0.5, 0.995, "vertical PIN", transform=ax.transAxes, ha="center", va="top", fontsize=7.5, fontweight="bold", color=INK)
    # (b) lateral PIN in the Ge, illustrative
    bx = fig.add_axes([0.51, 0.47, 0.49, 0.53]); frameless(bx, (-3.6, 3.6), (-0.6, 2.35))
    box(bx, -3.6, -0.6, 7.2, 0.6, "ox", z=0); box(bx, -3.6, 0, 7.2, 2.35, "oxtop", z=0)
    box(bx, -3.6, 0, 7.2, 0.22, "si", z=1)
    box(bx, -2.0, 0.22, 4.0, 0.5, "ge", z=2)
    box(bx, -2.0, 0.22, 1.0, 0.5, "pp", z=3, alpha=0.75); box(bx, 1.0, 0.22, 1.0, 0.5, "nn", z=3, alpha=0.75)
    for xc in (-1.5, 1.5):
        box(bx, xc - 0.2, 0.72, 0.4, 1.3, "metal", z=3)
    for yy in (0.36, 0.58):
        arrow(bx, (-0.85, yy), (0.85, yy), col=RED, lw=1.1, ms=6, z=6)
    label(bx, -1.5, -0.3, "p$^{+}$ Ge", fs=FS_SMALL); label(bx, 0, -0.3, "i-Ge", fs=FS_SMALL); label(bx, 1.5, -0.3, "n$^{+}$ Ge", fs=FS_SMALL)
    label(bx, 0, 1.0, "field set by lithography", fs=FS_SMALL, col=RED)
    note(bx, "illustrative", loc="lower right")
    panel(bx, "b", x=0.0, y=1.0)
    bx.text(0.5, 0.995, "lateral PIN", transform=bx.transAxes, ha="center", va="top", fontsize=7.5, fontweight="bold", color=INK)
    # (c) side view along the detector: evanescent absorption over 15 um
    VS_ = 4.0                                                                  # vertical exaggeration
    cx = fig.add_axes([0.0, 0.0, 1.0, 0.44]); frameless(cx, (-4.5, 21.5), (-0.9 * VS_, 1.4 * VS_))
    L = 15.0; a = GAM * ALPHA * 1e-4                                          # 1/um
    box(cx, -4.5, -0.9 * VS_, 26, 0.9 * VS_, "ox", z=0); box(cx, -4.5, 0, 26, 1.4 * VS_, "oxtop", z=0)
    z = np.linspace(-4.5, 21.5, 600); P = np.where(z < 0, 1.0, np.exp(-a * np.clip(z, 0, L)))
    P = np.where(z > L, np.exp(-a * L), P)
    cx.imshow(P[None, :], extent=(-4.5, 21.5, 0, 0.22 * VS_), aspect="auto", cmap=FIELD_CMAP, vmin=0, vmax=1.15, zorder=1)
    box(cx, 0, 0.22 * VS_, L, 0.5 * VS_, "ge", z=2); box(cx, 0, 0.72 * VS_, L, 0.1 * VS_, "nn", z=2)
    zz = np.linspace(0, L, 200); y0p, hp = 0.9 * VS_, 0.3 * VS_                # guided-power curve drawn above the Ge
    cx.plot(np.r_[-4.5, zz, 21.5], y0p + hp * np.r_[1.0, np.exp(-a * zz), np.exp(-a * L)], color=C1, lw=1.2, zorder=5)
    cx.plot([-4.5, 21.5], [y0p, y0p], color=C1, lw=0.4, ls=":", zorder=5)
    cx.text(-2.6, y0p + hp + 0.1, "guided power", fontsize=6.6, color=C1, va="bottom")
    pab = 1 - math.exp(-a * L)
    cx.text(L + 0.6, y0p + hp * (1 - pab) + 0.1, f"{100*(1-pab):.1f} % left", fontsize=6.6, color=C1, va="bottom")
    arrow(cx, (-4.2, 0.11 * VS_), (-2.2, 0.11 * VS_), col=OPT, lw=1.1, ms=6, z=6)
    label(cx, -4.3, -0.45 * VS_, "Si waveguide", fs=FS_SMALL, ha="left")
    label(cx, L / 2, 0.47 * VS_, f"Ge, {L:.0f} µm long", fs=FS_SMALL)
    dim(cx, (0, -0.55 * VS_), (L, -0.55 * VS_), "", lw=0.6)
    label(cx, L / 2, -0.55 * VS_, f"{100*pab:.1f} % absorbed in {L:.0f} µm", fs=FS_SMALL, bg="white")
    note(cx, f"vertical scale × {VS_:.0f}", loc="lower right")
    panel(cx, "c", x=0.0, y=1.0)
    save(fig, "ch21_pd")
    print(f"[21.1] evanescent: Gamma alpha = {a:.3f} /um, absorbed in {L:.0f} um: {100*pab:.1f} %")


# ------------------------------------------------------------------ Figure 21.2: bandwidth and responsivity
def pd_model(d_um, area_um2, wg=True, length_um=15.0):
    C = EPS * area_um2 * 1e-12 / (d_um * 1e-6) + CPAR
    frc = 1 / (2 * np.pi * RL * C); ft = 0.45 * VS / (d_um * 1e-6)
    f = 1 / np.sqrt(1 / frc ** 2 + 1 / ft ** 2)
    absb = 1 - np.exp(-GAM * ALPHA * 1e-4 * length_um) if wg else 1 - np.exp(-ALPHA * 1e-4 * d_um)
    return f, frc, ft, C, ETA * RMAX * absb * (0.92 if wg else 0.95)


def fig_bw():
    d = np.linspace(0.1, 2.0, 400)
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.75), gridspec_kw=dict(wspace=0.32))
    a.plot(d, 0.45 * VS / (d * 1e-6) / 1e9, color=MUTED, ls="--", lw=1.0, label="transit limit")
    for Lw, col in ((5, C3), (15, C1), (50, C4)):
        f, frc, ft, C, R = pd_model(d, Lw * WWG)
        a.plot(d, f / 1e9, color=col, label=f"{Lw} × 4 µm")
        j = np.argmax(f); a.plot(d[j], f[j] / 1e9, "o", color=col, ms=3.5)
        print(f"[21.2] {Lw} x 4 um: optimum d {d[j]:.2f} um, {f[j]/1e9:.0f} GHz; at 0.5 um {np.interp(0.5, d, f)/1e9:.0f} GHz")
    f, frc, ft, C, R = pd_model(np.array([0.5]), 15 * WWG)
    a.plot(0.5, f[0] / 1e9, "s", color=C1, ms=5, mfc="white", mew=1.2)
    a.annotate(f"Worked Example 21.1\n{f[0]/1e9:.0f} GHz", xy=(0.5, f[0] / 1e9), xytext=(0.62, 104), fontsize=6.6,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a.set_xlim(0, 2); a.set_ylim(0, 140)
    finish(a, "Intrinsic Ge thickness (µm)", "3 dB bandwidth (GHz)", legend=True, loc="upper right")
    a.legend(loc="center right", fontsize=6.8, title="waveguide detector", title_fontsize=6.8)
    tag(a, "a")
    print(f"[21.2] WE 21.1: C {C[0]*1e15:.1f} fF, f_RC {frc[0]/1e9:.0f} GHz, f_t {ft[0]/1e9:.0f} GHz, f3dB {f[0]/1e9:.0f} GHz, R {float(np.atleast_1d(R)[0]):.2f} A/W")
    # (b) responsivity against bandwidth, thickness as the parameter
    dd = np.linspace(0.15, 3.0, 300)
    for wg, area, col, lab in ((True, 15 * WWG, C1, "waveguide, 15 × 4 µm"), (False, np.pi * 30 ** 2 / 4, C2, "normal incidence, 30 µm")):
        f, frc, ft, C, R = pd_model(dd, area, wg=wg)
        R = np.broadcast_to(R, dd.shape)
        b.plot(f / 1e9, R, color=col, label=lab)
        for dm in (0.25, 0.5, 1.0, 2.0):
            i = np.argmin(abs(dd - dm)); b.plot(f[i] / 1e9, R[i], "o", color=col, ms=3.2)
            up = wg and dm != 0.25
            b.text(f[i] / 1e9 + (0.0 if wg else 1.2), R[i] + (0.035 if up else -0.035 if wg else -0.02), f"{dm:g}", fontsize=6.3, color=col,
                   ha="center" if wg else "left", va="bottom" if up else "top")
        if not wg:
            for dm in (0.5, 1.0, 2.0):
                i = np.argmin(abs(dd - dm))
                print(f"[21.2] NI 30 um, d {dm} um: {f[i]/1e9:.1f} GHz, {R[i]:.2f} A/W")
    b.text(69, 0.03, "dot labels: Ge thickness (µm)", fontsize=6.3, color=MUTED, ha="right", va="bottom")
    b.set_xlim(0, 70); b.set_ylim(0, 1.1)
    finish(b, "3 dB bandwidth (GHz)", "Responsivity at 1550 nm (A/W)", legend=True, loc="center right")
    tag(b, "b")
    save(fig, "ch21_bw")


# ------------------------------------------------------------------ Figure 21.3: noise against received power (PIN)
def fig_noise():
    qt = qtarget()
    r = 10 ** 0.4
    p = np.linspace(-25, 5, 601); P = 1e-3 * 10 ** (p / 10)
    i1, i0 = RESP * 2 * P * r / (r + 1), RESP * 2 * P / (r + 1)
    th = IN * np.sqrt(B) * np.ones_like(P)
    sh1 = np.sqrt(2 * QE * i1 * B); dk = np.sqrt(2 * QE * ID * B) * np.ones_like(P)
    s1 = np.sqrt(th ** 2 + 2 * QE * (i1 + ID) * B); s0 = np.sqrt(th ** 2 + 2 * QE * (i0 + ID) * B)
    allowed = (i1 - i0) / (2 * qt)
    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    ax.semilogy(p, 1e6 * th, color=C1, label="TIA thermal noise")
    ax.semilogy(p, 1e6 * sh1, color=C2, label="shot noise of the '1' level")
    ax.semilogy(p, 1e6 * dk, color=C3, label="shot noise of 100 nA dark current")
    ax.semilogy(p, 1e6 * (s1 + s0) / 2, color=C6, lw=1.0, ls="--", label="total (mean of both levels)")
    ax.semilogy(p, 1e6 * allowed, color=C4, label="allowed: $(I_1 - I_0)/2Q$, Q = 7.03")
    j = np.argmin(abs(allowed - (s1 + s0) / 2)); ax.plot(p[j], 1e6 * allowed[j], "o", color=C4, ms=4)
    sens = sens_dbm(1.0, 0.1, ber_q=qt)                       # the same crossing, found by bisection
    ax.annotate(f"sensitivity {sens:.1f} dBm".replace("-", "−"), xy=(p[j], 1e6 * allowed[j]), xytext=(-24.5, 7.5), fontsize=6.8,
                va="bottom", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    k = np.argmin(abs(sh1 - th))
    ax.axvline(-2.7, color=MUTED, lw=0.7, ls=":"); ax.text(-2.5, 0.07, "link delivers\n−2.7 dBm", fontsize=6.4, color=MUTED, va="bottom")
    ax.set_xlim(-25, 5); ax.set_ylim(0.01, 1000)
    finish(ax, "Average received power (dBm)", "rms current (µA)", legend=True, loc="upper left")
    ax.legend(loc="upper left", fontsize=6.4)
    save(fig, "ch21_noise")
    print(f"[21.3n] thermal {1e6*th[0]:.2f} uA; dark shot {1e6*dk[0]:.3f} uA; sensitivity {sens:.2f} dBm (grid crossing {p[j]:.2f}); shot of the '1' equals thermal at "
          f"{p[k]:.1f} dBm ({1e6*i1[k]:.0f} uA); at the sensitivity the '1' shot noise is {1e6*sh1[j]:.2f} uA "
          f"({100*(sh1[j]/th[j])**2:.0f} % of the thermal noise power); at -2.7 dBm: {1e6*sh1[np.argmin(abs(p+2.7))]:.2f} uA")


# ------------------------------------------------------------------ Figure 21.4: avalanche photodiode
def sens_dbm(M, k, er_db=4.0, ber_q=7.034):
    r = 10 ** (er_db / 10); F = k * M + (1 - k) * (2 - 1 / M) if M > 1 else 1.0
    th = IN ** 2 * B
    def q_of(pdbm):
        P = 1e-3 * 10 ** (pdbm / 10)
        i1, i0 = M * RESP * 2 * P * r / (r + 1), M * RESP * 2 * P / (r + 1)
        s1 = math.sqrt(th + 2 * QE * M * F * (i1 + M * ID) * B); s0 = math.sqrt(th + 2 * QE * M * F * (i0 + M * ID) * B)
        return (i1 - i0) / (s1 + s0)
    lo, hi = -40.0, 5.0
    for _ in range(70):
        m = (lo + hi) / 2
        if q_of(m) < ber_q: lo = m
        else: hi = m
    return (lo + hi) / 2


def qtarget(ber=1e-12):
    lo, hi = 0.0, 20.0
    for _ in range(80):
        m = (lo + hi) / 2
        if 0.5 * math.erfc(m / math.sqrt(2)) > ber: lo = m
        else: hi = m
    return (lo + hi) / 2


def fig_apd():
    fig = plt.figure(figsize=(6.3, 3.0))
    # (a) SACM stack and its field (illustrative doping)
    layers = [("n$^{+}$ Si", 0.3, "nn"), ("i-Si: multiplication", 0.5, "si"), ("p Si: charge", 0.1, "pdop"),
              ("i-Ge: absorption", 1.0, "ge"), ("p$^{+}$ Ge", 0.1, "pp")]
    ax = fig.add_axes([0.0, 0.14, 0.27, 0.8]); frameless(ax, (0, 1.6), (-0.25, 2.25), equal=False)
    y = 0.0; edges = {}
    for name, t, m in layers:
        box(ax, 0.15, y, 1.2, t, m, z=2, ec=INK, lw=0.3)
        ax.text(1.42, y + t / 2, name, fontsize=6.4, va="center", ha="left", color=INK)
        edges[name] = (y, y + t); y += t
    box(ax, 0.15, -0.25, 1.2, 0.25, "ox", z=1); ax.text(0.75, -0.13, "BOX", ha="center", va="center", fontsize=6.3, color=MUTED)
    arrow(ax, (0.75, 2.24), (0.75, 1.95), col=OPT, lw=1.2, ms=7); ax.text(0.9, 2.17, "light", fontsize=6.6, color=OPT, va="center")
    panel(ax, "a", x=0.0, y=1.02)
    # field: Poisson across the stack, charge sheet N_A = 2e17 cm^-3 over 100 nm, 80 kV/cm in the Ge
    eps_si, eps_ge = 11.7 * 8.854e-12, 16.2 * 8.854e-12
    NA, tch, Ege = 2e17 * 1e6, 0.1e-6, 80e5
    E_si_top = Ege * eps_ge / eps_si                                     # D continuous at the Ge/Si interface
    E_mult = E_si_top + QE * NA * tch / eps_si
    yy, EE = [], []
    y_n, y_m0, y_m1, y_c1, y_g1, y_top = 0.0, 0.3, 0.8, 0.9, 1.9, 2.0
    for ys, Es in ((y_n, 0), (y_m0 - 0.04, 0), (y_m0, E_mult), (y_m1, E_mult), (y_c1, E_si_top), (y_c1, Ege), (y_g1, Ege), (y_g1 + 0.03, 0), (y_top, 0)):
        yy.append(ys); EE.append(Es / 1e5)
    fa = fig.add_axes([0.47, 0.14, 0.17, 0.8])
    fa.fill_betweenx(yy, 0, EE, color=C4, alpha=0.18, lw=0); fa.plot(EE, yy, color=C4, lw=1.4)
    fa.set_ylim(-0.25, 2.25); fa.set_xlim(0, 500); fa.set_yticks([]); fa.set_xticks([0, 200, 400])
    fa.spines["left"].set_visible(False); fa.grid(False)
    finish(fa, "Field (kV/cm)")
    fa.text(E_mult / 1e5 - 10, 0.55, f"{E_mult/1e5:.0f}", fontsize=6.4, color=C4, ha="right", va="center")
    fa.text(Ege / 1e5 + 15, 1.4, f"{Ege/1e5:.0f}", fontsize=6.4, color=C4, ha="left", va="center")
    V = Ege * 1.0e-6 + (E_si_top + E_mult) / 2 * tch + E_mult * 0.5e-6 + E_mult * 0.3e-6 * 0
    print(f"[21.3] SACM field: Ge {Ege/1e5:.0f} kV/cm, Si side of interface {E_si_top/1e5:.0f}, multiplication {E_mult/1e5:.0f} kV/cm; "
          f"bias across Ge + charge + multiplication about {V:.1f} V (illustrative)")
    fa.text(495, 2.22, "illustrative doping", fontsize=6, color=MUTED, style="italic", ha="right", va="top")
    # (b) sensitivity against gain
    b = fig.add_axes([0.77, 0.17, 0.22, 0.75])
    qt = qtarget()
    Ms = np.linspace(1.0, 40, 157)
    pin = sens_dbm(1.0, 0.1, ber_q=qt)
    for k, col in ((0.1, C1), (0.5, C2)):
        s = np.array([sens_dbm(M, k, ber_q=qt) for M in Ms])
        b.plot(Ms, s, color=col, label=f"k = {k}")
        j = np.argmin(s); b.plot(Ms[j], s[j], "o", color=col, ms=3.5)
        if k == 0.1: b.text(Ms[j], s[j] - 0.35, f"M = {Ms[j]:.0f}, {s[j]:.1f} dBm", fontsize=6.3, color=col, ha="center", va="top")
        else: b.text(Ms[j] + 2.5, s[j], f"M = {Ms[j]:.0f}, {s[j]:.1f} dBm", fontsize=6.3, color=col, ha="left", va="center")
        print(f"[21.3] k {k}: optimum M {Ms[j]:.1f}, sensitivity {s[j]:.2f} dBm (PIN {pin:.2f} dBm); gain {pin - s[j]:.1f} dB")
    b.axhline(pin, color=MUTED, lw=0.7, ls=":"); b.text(39, pin + 0.3, "PIN", fontsize=6.4, color=MUTED, ha="right", va="bottom")
    b.set_xlim(0, 40); b.set_ylim(-21, -10)
    finish(b, "APD gain M", "Sensitivity (dBm)", legend=True, loc="upper right")
    b.legend(loc="center right", fontsize=6.6)
    tag(b, "b")
    save(fig, "ch21_apd")


if __name__ == "__main__":
    which = sys.argv[1:] or ["pd", "bw", "noise", "apd"]
    for w in which:
        globals()["fig_" + w]()
