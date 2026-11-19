"""Figures and numbers for Chapter 33 (optical links and transceivers).

Run from the repository root:   python -I -X utf8 figsrc/ch33_links.py
Writes assets/figs/ch33_*.svg and prints every number the chapter quotes from these models.

The receiver model is the one of the Chapter 21 demo (_includes/demos/rx.html): Ge PIN with R = 0.9 A/W,
0.1 µA dark current, TIA noise 20 pA/√Hz over a noise bandwidth of 0.7 × the symbol rate, Gaussian noise,
level-dependent shot noise. Everything else (jitter budget, front-end poles, energy split) is an
illustrative choice anchored to Table 33.1, and the chapter says so.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *                                   # noqa: E402,F401
from matplotlib.patches import Circle, FancyBboxPatch, Polygon   # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

QE = 1.602e-19
RESP, IDARK, IN_TIA = 0.9, 1e-7, 20e-12       # A/W, A, A/√Hz (Chapter 21)
ER_REF = 10 ** 0.4                            # 4 dB extinction (Chapter 20)
P_RX = -2.7                                   # received power per lane, dBm (Table 33.1)
LOSS, PEN = 12.7, 3.0                         # link loss and penalty allowances, dB (Table 33.1)
BER_T, BER_KP4 = 1e-12, 2.4e-4
UI = 20.0                                     # ps at 50 Gb/s


# ------------------------------------------------------------------ receiver model
def ber_of_q(q):
    return 0.5 * math.erfc(q / math.sqrt(2))


def q_of_ber(ber):
    lo, hi = 0.0, 20.0
    for _ in range(100):
        m = (lo + hi) / 2
        if ber_of_q(m) > ber: lo = m
        else: hi = m
    return (lo + hi) / 2


def mw(dbm): return 1e-3 * 10 ** (dbm / 10)
def dbm(p): return 10 * math.log10(p / 1e-3)


def sigma(i, bn, rin=None, i_n=IN_TIA):
    s2 = i_n ** 2 * bn + 2 * QE * (i + IDARK) * bn
    if rin is not None: s2 += 10 ** (rin / 10) * bn * i ** 2
    return math.sqrt(s2)


def nrz_ber(p_dbm, r=ER_REF, rate=50e9, rin=None, offset=0.0, i_n=IN_TIA):
    """NRZ BER at average received power p_dbm; offset = decision-threshold offset in A (input-referred)."""
    bn = 0.7 * rate
    p = mw(p_dbm)
    i1, i0 = RESP * 2 * p * r / (r + 1), RESP * 2 * p / (r + 1)
    s1, s0 = sigma(i1, bn, rin, i_n), sigma(i0, bn, rin, i_n)
    vth = (s0 * i1 + s1 * i0) / (s0 + s1) + offset
    return 0.25 * math.erfc((i1 - vth) / (math.sqrt(2) * s1)) + 0.25 * math.erfc((vth - i0) / (math.sqrt(2) * s0))


def pam4_ber(p_dbm, r=ER_REF, rate=100e9, rin=None):
    """PAM4 at symbol rate rate/2, outer extinction r, equally spaced levels, Gray code (BER = SER/2)."""
    bn = 0.7 * rate / 2
    p = mw(p_dbm)
    hi, lo = RESP * 2 * p * r / (r + 1), RESP * 2 * p / (r + 1)
    lev = [lo + k * (hi - lo) / 3 for k in range(4)]
    s = [sigma(i, bn, rin) for i in lev]
    ser = sum(math.erfc((lev[k + 1] - lev[k]) / (s[k] + s[k + 1]) / math.sqrt(2)) for k in range(3)) / 4
    return ser / 2


def sensitivity(fn, target=BER_T, lo=-40.0, hi=30.0):
    for _ in range(90):
        m = (lo + hi) / 2
        if fn(m) > target: lo = m
        else: hi = m
    return (lo + hi) / 2


S_REF = sensitivity(lambda p: nrz_ber(p))            # -11.6 dBm, as in Chapter 21


# ------------------------------------------------------------------ Figure 33.1: one lane of the reference transceiver
def fig_architecture():
    fig, ax = plt.subplots(figsize=(6.3, 3.75))
    ax.set_xlim(0, 100); ax.set_ylim(-3, 60); ax.set_aspect("equal"); ax.axis("off")
    OPT, ELE, CTL = TEAL, INK, AMBER

    def box(x, y, w, h, text, ec=INK, fc="#FFFFFF", fs=6.6, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0", fc=fc, ec=ec, lw=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, fontweight="bold" if bold else "normal")

    def arrow(x0, y0, x1, y1, col=ELE, ls="-", lw=0.9):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, ls=ls, mutation_scale=7, shrinkA=0, shrinkB=0))

    def note(x, y, s, col=MUTED, fs=6.0, ha="center", va="center", **kw):
        ax.text(x, y, s, fontsize=fs, color=col, ha=ha, va=va, **kw)

    # chip regions
    for (x, y, w, h, t) in ((1, 33, 86, 26, "transmitter: driver IC over photonic IC"), (1, -2, 98, 22, "receiver: photonic IC beside receiver IC")):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.5", fc="none", ec=GRID, lw=1.0, ls="--"))
        note(x + w - 1, y + h - 1.6, t, ha="right", fs=6.2, style="italic")

    # ---------------- transmitter
    y_bus = 39.5
    box(3, 36.5, 13, 6, "CW laser λ₁\n+10 dBm", ec=AMBER, fc="#FBF1DF")
    ax.plot([16, 84], [y_bus, y_bus], color=OPT, lw=2.0, solid_capstyle="butt")
    ax.add_patch(Circle((31, y_bus + 3.6), 3.0, fc="none", ec=RED, lw=1.8))
    for xr in (47, 53, 59):
        ax.add_patch(Circle((xr, y_bus + 2.6), 2.0, fc="none", ec=MUTED, lw=1.0))
    note(53, y_bus - 2.4, "λ₂–λ₄ rings, routing −0.8 dB", fs=5.6)
    note(31, y_bus - 2.4, "−3.0 dB, 4 dB ER", fs=5.6)
    ax.add_patch(Polygon([[81.5, y_bus - 1.6], [85.5, y_bus - 1.6], [86.5, y_bus + 1.6], [80.5, y_bus + 1.6]], fc=BLUE, ec="none", alpha=0.8))
    note(83.5, y_bus - 3.0, "GC −3 dB", fs=5.6)
    note(70, y_bus + 1.6, "+3.2 dBm", col=OPT, fs=6.0)
    # electronics
    box(18, 49.5, 12, 5.5, "serialiser")
    box(19, 42.8, 10, 4.6, "PLL")
    arrow(24, 47.4, 24, 49.5)
    note(25.0, 48.4, "clock", fs=5.4, ha="left")
    box(34, 49.5, 13, 5.5, "driver + FFE\n2 Vpp")
    note(2.0, 53.6, "data in,\n50 Gb/s", fs=6.0, ha="left", col=INK)
    arrow(11, 52.25, 18, 52.25)
    arrow(30, 52.25, 34, 52.25)
    ax.plot([40.5, 40.5, 31], [49.5, 47.8, 47.8], color=ELE, lw=0.9)
    arrow(31, 47.8, 31, y_bus + 6.7)
    box(52, 49.5, 13, 5.5, "lock loop\n(heater)", ec=CTL, fc="#FBF1DF")
    ax.plot([52, 36], [50.5, y_bus + 4.6], color=CTL, lw=0.9, ls="--")
    note(76, 52.25, "one heater loop\nper ring (Ch 18)", col=CTL, fs=5.8)

    # ---------------- fibre (return path)
    ax.plot([86.5, 95, 95, 4, 4, 7], [y_bus, y_bus, 25, 25, 12, 12], color=BLUE, lw=1.5, solid_joinstyle="round")
    for k in range(5):
        ax.add_patch(Circle((44 + 2.0 * k, 25), 1.6, fc="none", ec=BLUE, lw=0.9))
    note(50, 28.0, "2 km SMF: −0.4 dB, 34 ps/nm  ·  two connectors: −1.0 dB  ·  +1.8 dBm", col=BLUE, fs=6.0)

    # ---------------- receiver
    y_rx = 12
    ax.add_patch(Polygon([[7, y_rx - 1.6], [11, y_rx - 1.6], [12, y_rx + 1.6], [6, y_rx + 1.6]], fc=BLUE, ec="none", alpha=0.8))
    note(9, y_rx + 3.2, "GC −3 dB\n−1.2 dBm", fs=5.6)
    ax.plot([12, 40], [y_rx, y_rx], color=OPT, lw=2.0, solid_capstyle="butt")
    ax.add_patch(Circle((22, y_rx - 3.4), 2.8, fc="none", ec=RED, lw=1.8))
    ax.plot([16, 28], [y_rx - 6.8, y_rx - 6.8], color=OPT, lw=1.6)
    note(22, y_rx + 2.6, "drop ring −1.5 dB", fs=5.6)
    box(28, 2.4, 7, 5.6, "Ge PD", fc="#E3F4F6")
    note(31.5, 0.6, "−2.7 dBm", col=OPT, fs=6.0)
    box(38, 2.4, 10, 5.6, "TIA\n20 pA/√Hz")
    box(51, 2.4, 9, 5.6, "CTLE")
    box(63, 2.4, 9, 5.6, "slicer")
    box(77, 2.4, 13, 5.6, "deserialiser")
    for x0, x1 in ((35, 38), (48, 51), (60, 63), (72, 77)):
        arrow(x0, 5.2, x1, 5.2)
    arrow(90, 5.2, 98, 5.2)
    note(94, 7.0, "data out", fs=5.8, col=INK)
    box(61, 11.5, 10, 5.0, "CDR")
    arrow(66, 11.5, 66, 8.0)
    note(65.2, 9.6, "clock", fs=5.4, ha="right")
    ax.plot([74, 74, 73], [5.2, 14.0, 14.0], color=ELE, lw=0.9)
    arrow(73, 14.0, 71, 14.0)
    note(75, 12.8, "data and edge\nsamples", fs=5.4, ha="left")
    box(43, 13.0, 12, 5.0, "lock loop", ec=CTL, fc="#FBF1DF")
    ax.plot([43, 25], [14.0, y_rx - 3.0], color=CTL, lw=0.9, ls="--")
    note(66, 0.4, "UI = 20 ps", fs=5.8)
    savefig(fig, "ch33_architecture")
    print("Fig 33.1 power levels: fibre in %.1f dBm, after fibre %.1f, after RX GC %.1f, at PD %.1f dBm" %
          (10 - 3.0 - 0.8 - 3.0, 10 - 3.0 - 0.8 - 3.0 - 1.4, 10 - 3.0 - 0.8 - 3.0 - 1.4 - 3.0, 10 - 12.7))


# ------------------------------------------------------------------ Figure 33.2: BER against Q and received power
def fig_ber():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.45]))
    q = np.linspace(0, 9, 400)
    a.semilogy(q, [ber_of_q(x) for x in q], color=C1)
    for ber, lab, col in ((BER_T, "10⁻¹²", INK), (BER_KP4, "KP4 FEC\n2.4×10⁻⁴", AMBER)):
        qq = q_of_ber(ber)
        a.plot([0, qq, qq], [ber, ber, 1e-18], color=col, lw=0.7, ls=":")
        a.text(qq - 0.15, ber / 30, f"Q = {qq:.2f}", fontsize=6.8, color=col, ha="right", va="top")
        a.text(0.15, ber * 4, lab, fontsize=6.8, color=col, va="bottom")
    a.set_xlim(0, 9); a.set_ylim(1e-18, 1)
    finish(a, "Q factor", "Bit-error ratio")
    tag(a, "a")

    p = np.linspace(-18, -1, 400)
    cases = [("no extinction penalty", dict(r=1e9), MUTED, "--"), ("4 dB ER (reference)", dict(), C1, "-"),
             ("+ RIN −135 dB/Hz", dict(rin=-135), C2, "-"), ("+ RIN −130 dB/Hz", dict(rin=-130), C4, "-")]
    sens = {}
    for lab, kw, col, ls in cases:
        b.semilogy(p, [nrz_ber(x, **kw) for x in p], color=col, ls=ls, label=lab)
        sens[lab] = sensitivity(lambda x: nrz_ber(x, **kw))
    b.axhline(BER_T, color=INK, lw=0.6, ls=":")
    b.axhline(BER_KP4, color=AMBER, lw=0.6, ls=":")
    b.text(-8.6, BER_T * 2, "10⁻¹²", fontsize=6.6, color=INK, va="bottom")
    b.text(-10.8, BER_KP4 * 2, "KP4 threshold", fontsize=6.6, color=AMBER, va="bottom")
    s0, s1, s2 = sens["no extinction penalty"], sens["4 dB ER (reference)"], sens["+ RIN −135 dB/Hz"]
    for xa, xb, yy, txt in ((s0, s1, 3e-14, f"{s1 - s0:.1f} dB"), (s1, s2, 2.5e-11, f"{s2 - s1:.1f} dB")):
        b.annotate("", (xb, yy), (xa, yy), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=7))
        b.text((xa + xb) / 2, yy * (0.08 if yy < 1e-12 else 6), txt, fontsize=6.8, ha="center", color=INK)
    b.axvline(P_RX, color=TEAL, lw=0.8, ls="--")
    b.text(P_RX - 0.25, 2e-2, "received\n−2.7 dBm", fontsize=6.6, color=TEAL, ha="right")
    b.set_xlim(-18, -1); b.set_ylim(1e-18, 1)
    finish(b, "Average received power (dBm)", "Bit-error ratio")
    b.legend(loc="lower right", fontsize=6.6)
    tag(b, "b")
    savefig(fig, "ch33_ber")
    print("Fig 33.2: Q(1e-12) %.3f, Q(1e-15) %.3f, Q(KP4) %.3f" % (q_of_ber(1e-12), q_of_ber(1e-15), q_of_ber(BER_KP4)))
    for k, v in sens.items(): print("   sensitivity %-24s %.2f dBm" % (k, v))
    print("   ER penalty (sim) %.2f dB; (r+1)/(r-1) = %.2f dB; RIN -135 %.2f dB; RIN -130 %.2f dB" %
          (s1 - s0, 10 * math.log10((ER_REF + 1) / (ER_REF - 1)), s2 - s1, sens["+ RIN −130 dB/Hz"] - s1))
    print("   BER at sensitivity +0.5 dB: %.1e, +1 dB: %.1e" % (nrz_ber(s1 + 0.5), nrz_ber(s1 + 1.0)))
    print("   margin to received power %.2f dB; after 3.0 dB allowances %.2f dB" % (P_RX - s1, P_RX - s1 - PEN))


def penalty_numbers():
    """Penalties quoted in Section 33.2 and Worked Example 33.1."""
    print("Penalties relative to %.2f dBm:" % S_REF)
    for erdb in (4, 6, 10):
        r = 10 ** (erdb / 10)
        print("   ER %d dB: (r+1)/(r-1) = %.2f dB" % (erdb, 10 * math.log10((r + 1) / (r - 1))))
    for rin in (-145, -140, -135, -130):
        print("   RIN %d dB/Hz at 4 dB ER: %.2f dB" % (rin, sensitivity(lambda x: nrz_ber(x, rin=rin)) - S_REF))
    s_inf = sensitivity(lambda x: nrz_ber(x, r=1e9))
    print("   RIN -140 dB/Hz at high ER: %.2f dB; formula 1/(1-Q^2 RIN Bn) %.2f dB" %
          (sensitivity(lambda x: nrz_ber(x, r=1e9, rin=-140)) - s_inf, 10 * math.log10(1 / (1 - q_of_ber(BER_T) ** 2 * 1e-14 * 35e9))))
    rho = 1e-13 * 35e9
    qmax = (ER_REF - 1) / ((ER_REF + 1) * math.sqrt(rho))
    print("   RIN -130 at 4 dB ER: Q at infinite power %.2f, BER floor %.1e" % (qmax, ber_of_q(qmax)))
    sth = IN_TIA * math.sqrt(35e9)
    for f in (0.5, 1.0):
        print("   offset %.1f sigma (%.2f uA): %.2f dB (formula 1 + d/(Q sigma): %.2f dB)" %
              (f, f * sth * 1e6, sensitivity(lambda x: nrz_ber(x, offset=f * sth)) - S_REF, 10 * math.log10(1 + f / q_of_ber(BER_T))))
    p = mw(S_REF)
    print("   OMA at sensitivity: %.1f uW (%.2f dBm); thermal sigma %.2f uA" % (2 * p * (ER_REF - 1) / (ER_REF + 1) * 1e6, dbm(2 * p * (ER_REF - 1) / (ER_REF + 1)), sth * 1e6))


# ------------------------------------------------------------------ front-end model (Figures 33.3 and the ISI numbers)
F_RING, F_RX = 24e9, 32e9          # transmitter as one pole at the ring's 24 GHz optical bandwidth (Ch 20); RX 2nd-order Butterworth


def chain(u, dt, f_ring=F_RING, f_rx=F_RX):
    """Drive u through a first-order pole (ring) and a second-order Butterworth (receiver). RK4 per step."""
    wr, w = 2 * math.pi * f_ring, 2 * math.pi * f_rx
    s = np.zeros(3); out = np.empty(len(u))
    def f(s, ui): return np.array([wr * (ui - s[0]), s[2], w * w * (s[0] - s[1]) - math.sqrt(2) * w * s[2]])
    for k, ui in enumerate(u):
        k1 = f(s, ui); k2 = f(s + dt / 2 * k1, ui); k3 = f(s + dt / 2 * k2, ui); k4 = f(s + dt * k3, ui)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out[k] = s[1]
    return out


def butter2(u, dt, f3):
    w = 2 * math.pi * f3
    s = np.zeros(2); out = np.empty(len(u))
    def f(s, ui): return np.array([s[1], w * w * (ui - s[0]) - math.sqrt(2) * w * s[1]])
    for k, ui in enumerate(u):
        k1 = f(s, ui); k2 = f(s + dt / 2 * k1, ui); k3 = f(s + dt / 2 * k2, ui); k4 = f(s + dt * k3, ui)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out[k] = s[0]
    return out


def peak_distortion(rate, levels, n=48, nsym=30):
    """Eye opening (fraction of the ideal eye) from the pulse response, best sampling phase."""
    dt = 1 / rate / n
    u = np.zeros(n * nsym); u[:n] = 1.0
    h = chain(u, dt)
    best = -9
    for ph in range(n):
        smp = h[ph::n]; k0 = np.argmax(smp)
        best = max(best, smp[k0] - (levels - 1) * (np.sum(np.abs(smp)) - abs(smp[k0])))
    return best


def front_end_numbers():
    def loss(f): return 10 * math.log10((1 + (f / F_RING) ** 2) * (1 + (f / F_RX) ** 4))
    print("Front end (ring pole 24 GHz, RX Butterworth 32 GHz, noise bandwidth %.1f GHz):" % (1.1107 * 32))
    print("   loss at 25 GHz %.2f dB, at 50 GHz %.2f dB, octave loss %.2f dB (PAM4 rule 20 log 3 = %.2f dB)" %
          (loss(25e9), loss(50e9), loss(50e9) - loss(25e9), 20 * math.log10(3)))
    for name, rate, lev in (("NRZ 50 GBd", 50e9, 2), ("NRZ 100 GBd", 100e9, 2), ("PAM4 50 GBd", 50e9, 4)):
        e = peak_distortion(rate, lev)
        print("   %s: eye %.3f of ideal, ISI penalty %.2f dB" % (name, e, 10 * math.log10(1 / e)))
    # receiver bandwidth: ISI against noise for a second-order Butterworth alone, NRZ
    print("   receiver bandwidth sweep (Butterworth alone, NRZ, total relative to f3 = 0.63 B):")
    n = 48
    def isi_pp(x):
        u = np.zeros(n * 30); u[:n] = 1.0
        h = butter2(u, 1 / 50e9 / n, x * 50e9)
        e = max(h[ph::n].max() - (np.sum(np.abs(h[ph::n])) - h[ph::n].max()) for ph in range(n))
        return 10 * math.log10(1 / e)
    ref = 10 * math.log10(math.sqrt(0.63))
    for x in (0.35, 0.4, 0.45, 0.5, 0.55, 0.63, 0.75, 1.0):
        pp = isi_pp(x)
        print("     f3 = %.2f B: ISI %.2f dB, ISI + noise %.2f dB" % (x, pp, pp + 10 * math.log10(math.sqrt(x)) - ref))
    print("   Ch 21 noise bandwidth 0.7 B corresponds to f3 = %.2f B for this response" % (0.7 / 1.1107))


# ------------------------------------------------------------------ Figure 33.3: NRZ and PAM4 eyes
def fig_eyes():
    rng = np.random.default_rng(7)
    n, nsym = 32, 2600
    p_rx = -8.0
    p = mw(p_rx)
    i1, i0 = RESP * 2 * p * ER_REF / (ER_REF + 1), RESP * 2 * p / (ER_REF + 1)
    sth = IN_TIA * math.sqrt(0.7 * 50e9)
    cm = LinearSegmentedColormap.from_list("eye", [(1, 1, 1, 0), (0.62, 0.72, 0.90, 1), BLUE, INK])
    fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.35), sharey=True)
    panels = (("NRZ, 50 GBd (50 Gb/s)", 50e9, 2), ("NRZ, 100 GBd (100 Gb/s)", 100e9, 2), ("PAM4, 50 GBd (100 Gb/s)", 50e9, 4))
    for ax, (title, rate, m) in zip(axs, panels):
        dt = 1 / rate / n
        sym = rng.integers(0, m, nsym) / (m - 1)
        drive = np.repeat(i0 + (i1 - i0) * sym, n)
        sig_ = chain(drive, dt)
        noise = butter2(rng.standard_normal(len(drive)), dt, F_RX)
        noise *= sth / noise[200:].std()
        y = (sig_ + noise) * 1e6
        # fold into two symbol periods, centred on the best sampling phase
        ph = np.argmax([np.std(sig_[10 * n + k::n][:-2]) for k in range(n)])
        start = 40 * n + ph - n
        seg = y[start: start + ((len(y) - start) // (2 * n)) * 2 * n].reshape(-1, 2 * n)
        tt = np.tile(np.arange(2 * n) / n, (seg.shape[0], 1))
        H, xe, ye = np.histogram2d(tt.ravel(), seg.ravel(), bins=(2 * n, 150), range=[[0, 2], [0, 260]])
        ax.imshow(np.sqrt(H.T), origin="lower", aspect="auto", extent=[0, 2, 0, 260], cmap=cm, interpolation="bilinear")
        ax.set_title(title, fontsize=7.5, loc="left", color=INK)
        ax.set_xlim(0, 2); ax.set_xticks([0, 0.5, 1, 1.5, 2]); ax.grid(False)
        ax.set_xlabel("Time (symbol periods)")
    axs[0].set_ylabel("Photocurrent (µA)")
    fig.set_dpi(220)
    savefig(fig, "ch33_eyes")
    print("Fig 33.3: received %.1f dBm, levels %.1f / %.1f uA, noise %.2f uA rms" % (p_rx, i0 * 1e6, i1 * 1e6, sth * 1e6))


def format_numbers():
    print("NRZ vs PAM4 (sensitivity, margin after 3.0 dB allowances at -2.7 dBm):")
    for name, fn, tgt in (("NRZ 50 Gb/s, 1e-12", lambda x: nrz_ber(x), BER_T), ("NRZ 50 Gb/s, KP4", lambda x: nrz_ber(x), BER_KP4),
                          ("NRZ 100 Gb/s, 1e-12", lambda x: nrz_ber(x, rate=100e9), BER_T),
                          ("PAM4 100 Gb/s, 1e-12", lambda x: pam4_ber(x), BER_T), ("PAM4 100 Gb/s, KP4", lambda x: pam4_ber(x), BER_KP4)):
        s = sensitivity(fn, tgt)
        print("   %-22s %.2f dBm, margin %.2f dB" % (name, s, P_RX - s - PEN))
    print("   PAM4 at equal bit rate, thermal limit: 10 log 3 - 5 log 2 = %.2f dB" % (10 * math.log10(3) - 5 * math.log10(2)))
    for tol in (40, 60):
        print("   dispersion tolerance %d ps/nm at 50 GBd -> %.0f ps/nm at 100 GBd; 34 ps/nm reached at %.0f GBd" % (tol, tol / 4, 50 * math.sqrt(tol / 34)))
    print("   channels on the 400 GHz grid (%.2f nm) in a 13.7 nm FSR: %.2f" % (1550.9 ** 2 * 400e9 / 2.998e17, 13.7 / 3.207))


def ffe_numbers():
    print("TX FFE on a single pole at 12.5 GHz (0.25 B), 50 Gb/s:")
    a = math.exp(-2 * math.pi * 0.25)
    h0 = 1 - a
    eye0, eye1 = h0 * (1 - a / (1 - a)), h0 / (1 + a)
    print("   post-cursor/cursor %.3f; eye without FFE %.3f, with FFE %.3f (+%.2f dB); taps %.3f / -%.3f; long-run level %.2f dB" %
          (a, eye0, eye1, 10 * math.log10(eye1 / eye0), 1 / (1 + a), a / (1 + a), 20 * math.log10((1 - a) / (1 + a))))
    # ISI jitter: zero-crossing spread for random data, with and without FFE
    rng = np.random.default_rng(3)
    bits = rng.integers(0, 2, 3000) * 2 - 1.0
    n = 64
    for label, taps in (("without", (1.0,)), ("with", (1 / (1 + a), -a / (1 + a)))):
        tx = np.convolve(bits, taps)[:len(bits)]
        u = np.repeat(tx, n)
        k = math.exp(-2 * math.pi * 12.5e9 * (1 / 50e9 / n))
        y = np.empty_like(u); s = u[0]
        for i, ui in enumerate(u):
            s = k * s + (1 - k) * ui; y[i] = s
        idx = np.where(np.sign(y[1:]) != np.sign(y[:-1]))[0][10:]
        tc = ((idx + y[idx] / (y[idx] - y[idx + 1])) / n) % 1.0
        print("   ISI jitter %s FFE: %.2f ps peak to peak" % (label, (tc.max() - tc.min()) * UI))


# ------------------------------------------------------------------ Figure 33.4: bathtub
JITTER = [("Transmitter: serialiser, driver, ring", 2.0, 0.30), ("Modulator and fibre ISI (after FFE)", 2.0, 0.0),
          ("Receiver front end: TIA, CTLE", 1.0, 0.25), ("Clock: PLL and CDR", 1.0, 0.35)]


def bathtub(t, dj, rj):
    """Dominant-term dual-Dirac bathtub; every bit counted as a transition (conservative)."""
    return 0.5 * math.erfc((t - dj / 2) / (math.sqrt(2) * rj)) + 0.5 * math.erfc(((UI - t) - dj / 2) / (math.sqrt(2) * rj))


def fig_bathtub():
    dj = sum(j[1] for j in JITTER); rj = math.sqrt(sum(j[2] ** 2 for j in JITTER))
    fig, ax = plt.subplots(figsize=(4.9, 2.7))
    t = np.linspace(0, UI, 1200)
    for r, col, lab in ((rj, C1, f"budget: DJ {dj:.1f} ps, RJ {rj:.2f} ps rms"), (2 * rj, C4, f"RJ doubled ({2 * rj:.2f} ps rms)")):
        ax.semilogy(t, [min(bathtub(x, dj, r), 1) for x in t], color=col, label=lab)
    q12, qk = q_of_ber(BER_T), q_of_ber(BER_KP4)
    for ber, q, col, lab in ((BER_T, q12, INK, "10⁻¹²"), (BER_KP4, qk, AMBER, "KP4")):
        ax.axhline(ber, color=col, lw=0.6, ls=":")
        ax.text(19.8, ber * 2.2, lab, fontsize=6.8, color=col, ha="right")
        half = dj / 2 + q * rj
        ax.annotate("", (UI - half, ber), (half, ber), arrowprops=dict(arrowstyle="<->", color=col, lw=0.8, mutation_scale=6))
        ax.text(UI / 2, ber * 0.06, f"{UI - 2 * half:.1f} ps open", fontsize=6.8, color=col, ha="center", va="top")
    ax.set_xlim(0, UI); ax.set_ylim(1e-16, 1)
    finish(ax, "Sampling time within the 20 ps bit (ps)", "Bit-error ratio", legend=True, loc="upper center")
    ax.legend(loc="upper center", fontsize=6.6, ncol=1, bbox_to_anchor=(0.5, 1.0))
    savefig(fig, "ch33_bathtub")
    print("Fig 33.4 / Table 33.2: DJ %.2f ps, RJ %.3f ps rms; 2Q(1e-12) %.3f, 2Q(KP4) %.3f" % (dj, rj, 2 * q12, 2 * qk))
    for r, lab in ((rj, "budget"), (2 * rj, "RJ x2")):
        tj12, tjk = dj + 2 * q12 * r, dj + 2 * qk * r
        print("   %s: TJ(1e-12) %.2f ps, open %.2f ps (%.2f UI); TJ(KP4) %.2f ps, open %.2f ps (%.2f UI)" %
              (lab, tj12, UI - tj12, (UI - tj12) / UI, tjk, UI - tjk, (UI - tjk) / UI))
    print("   RJ that closes the eye at 1e-12: %.2f ps rms" % ((UI - dj) / (2 * q12)))
    print("   lane skew over 2 km across 1546.12-1555.75 nm: %.0f ps = %.1f UI" % (34 * (1555.75 - 1546.12), 34 * (1555.75 - 1546.12) / UI))


# ------------------------------------------------------------------ Figure 33.5: energy per bit
E_HEAT, E_TIA, E_DRV, E_MOD = 0.80, 1.0, 0.5, 0.02     # pJ/bit at 50 Gb/s (Table 33.1)


def e_laser(p_dbm, rate, eta=0.15):
    return mw(p_dbm) / eta / rate * 1e12


def fig_energy():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    eta = np.linspace(0.05, 0.40, 200)
    base = np.zeros_like(eta)
    stack = [("modulators", np.full_like(eta, E_MOD), MUTED), ("drivers", np.full_like(eta, E_DRV), C3),
             ("TIAs", np.full_like(eta, E_TIA), C5), ("heaters", np.full_like(eta, E_HEAT), C2),
             ("laser, +10 dBm", np.array([e_laser(10, 50e9, e) for e in eta]), C1)]
    for lab, v, col in stack:
        a.fill_between(eta * 100, base, base + v, color=col, alpha=0.75, lw=0, label=lab)
        base = base + v
    other = E_MOD + E_DRV + E_TIA + E_HEAT
    a.plot(eta * 100, [other + e_laser(7.13, 50e9, e) for e in eta], color=INK, lw=1.0, ls="--", label="laser cut to +7.1 dBm")
    a.axhline(5, color=RED, lw=0.8, ls=":")
    a.text(39.5, 4.85, "5 pJ/bit target", fontsize=6.6, color=RED, ha="right", va="top")
    a.plot([15], [other + e_laser(10, 50e9, 0.15)], "o", color=INK, ms=3.5)
    a.annotate("Table 33.1", (15, other + e_laser(10, 50e9, 0.15)), xytext=(6, 6), textcoords="offset points", fontsize=6.6)
    a.set_xlim(5, 40); a.set_ylim(0, 8)
    h, l = a.get_legend_handles_labels()
    a.legend(h[::-1], l[::-1], fontsize=6.2, loc="upper right", bbox_to_anchor=(1.0, 1.02))
    finish(a, "Laser wall-plug efficiency (%)", "Energy per bit (pJ/bit)")
    tag(a, "a")

    rates = np.linspace(10e9, 100e9, 181)
    lasers = []
    for r in rates:
        s = sensitivity(lambda x: nrz_ber(x, rate=r))
        lasers.append(e_laser(s + LOSS + PEN + 3.0, r))
    lasers = np.array(lasers)
    heat = E_HEAT * 50e9 / rates
    elec = np.full_like(rates, E_TIA + E_DRV + E_MOD)
    base = np.zeros_like(rates)
    for lab, v, col in (("TIAs, drivers, modulators", elec, C5), ("heaters", heat, C2), ("laser, 3 dB margin", lasers, C1)):
        b.fill_between(rates / 1e9, base, base + v, color=col, alpha=0.75, lw=0, label=lab)
        base = base + v
    b.axvspan(54, 66, color=MUTED, alpha=0.12, lw=0)
    b.axvspan(66, 100, color=MUTED, alpha=0.25, lw=0)
    b.text(83, 5.5, "NRZ at 1550 nm:\n2 km exceeds the\ndispersion tolerance", fontsize=6.4, color=INK, ha="center", va="top")
    i50 = np.argmin(abs(rates - 50e9))
    b.plot([50], [base[i50]], "o", color=INK, ms=3.5)
    b.annotate(f"{base[i50]:.1f} pJ/bit", (50, base[i50]), xytext=(-4, 8), textcoords="offset points", fontsize=6.6, ha="right")
    b.set_xlim(10, 100); b.set_ylim(0, 8)
    h, l = b.get_legend_handles_labels()
    b.legend(h[::-1], l[::-1], fontsize=6.2, loc="upper right", bbox_to_anchor=(1.0, 1.02))
    finish(b, "Lane rate (Gb/s, NRZ)", "Energy per bit (pJ/bit)")
    tag(b, "b")
    savefig(fig, "ch33_energy")
    print("Fig 33.5a: total at 15 %% and +10 dBm %.2f pJ/bit; laser +7.13 dBm %.2f; 5 pJ/bit reached at eta = %.1f %%; at 30 %% %.2f" %
          (other + e_laser(10, 50e9), other + e_laser(7.13, 50e9), 100 * mw(10) / ((5 - other) * 1e-12 * 50e9), other + e_laser(10, 50e9, 0.30)))
    for r in (10e9, 25e9, 50e9, 100e9):
        s = sensitivity(lambda x: nrz_ber(x, rate=r))
        el = e_laser(s + LOSS + PEN + 3.0, r)
        print("   %3.0f Gb/s: sensitivity %.2f dBm, laser %.2f dBm, laser %.2f + heaters %.2f + electronics %.2f = %.2f pJ/bit" %
              (r / 1e9, s, s + LOSS + PEN + 3.0, el, E_HEAT * 50e9 / r, E_TIA + E_DRV + E_MOD, el + E_HEAT * 50e9 / r + E_TIA + E_DRV + E_MOD))
    s10 = sensitivity(lambda x: nrz_ber(x, i_n=10e-12))
    gain = S_REF - s10
    saved = e_laser(S_REF + LOSS + PEN + 3.0, 50e9) - e_laser(s10 + LOSS + PEN + 3.0, 50e9)
    print("   TIA 10 pA/rtHz: sensitivity %.2f dBm (%.2f dB better); laser energy saved %.3f pJ/bit = %.1f mW per lane" %
          (s10, gain, saved, saved * 50e9 * 1e-12 * 1e3))


if __name__ == "__main__":
    print("Reference sensitivity %.2f dBm" % S_REF)
    fig_architecture()
    fig_ber()
    penalty_numbers()
    front_end_numbers()
    format_numbers()
    ffe_numbers()
    fig_eyes()
    fig_bathtub()
    fig_energy()
