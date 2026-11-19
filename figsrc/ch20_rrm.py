"""Figures and numbers for Chapter 20, Sections 20.8-20.9 (ring-modulator dynamics, drivers and locking).

Run from the repository root:   python -I -X utf8 figsrc/ch20_rrm.py
Writes assets/figs/ch20_*.svg and prints every number the chapter quotes from these models.

The ring is the reference-link ring of Worked Example 20.2 and the ring-modulator demo
(_includes/demos/ringmod.html): 7.2 µm radius, n_g = 3.89, Q_i = 15 000, Q_L = 8000, 50 pm/V, 2 Vpp,
a static Lorentzian dip. Dynamics use coupled-mode theory (one mode, energy amplitude a):
    da/dt = (j(w_r - w_L) - 1/tau) a - j mu s_in,   s_out = s_in - j mu a,
with 1/tau = w/(2 Q_L) and mu^2 = 2/tau_e = w/Q_c. The carrier-injection ring uses the Soref-Bennett
relations of Chapter 19 and its femwell mode weights (figsrc/ch19_pn.json).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *                                   # noqa: E402,F401

HERE = os.path.dirname(os.path.abspath(__file__))
C0 = 2.998e8
LAM = 1550e-9
R_RING, NG = 7.2e-6, 3.89
QI, QL = 15000.0, 8000.0
QC = 1 / (1 / QL - 1 / QI)
EFF = 50e-12                                   # m per volt (50 pm/V)
VPP = 2.0
W0 = 2 * math.pi * C0 / LAM
FWHM_M = LAM / QL                              # resonance width in metres
FWHM_HZ = C0 / LAM / QL


def tmin():
    return ((1 / QI - 1 / QC) / (1 / QI + 1 / QC)) ** 2


def T_static(det_m):
    """Through-port transmission; det = laser wavelength - resonance wavelength."""
    return 1 - (1 - tmin()) / (1 + (2 * det_m / FWHM_M) ** 2)


def levels(det_m, eff=EFF, vpp=VPP):
    """Demo convention: more reverse bias moves the resonance red; det is laser - mid resonance."""
    sh = eff * vpp / 2
    return T_static(det_m + sh), T_static(det_m - sh)      # low bias, high bias


def er_il(det_m, eff=EFF, vpp=VPP):
    a, b = levels(det_m, eff, vpp)
    hi, lo = max(a, b), min(a, b)
    return 10 * math.log10(hi / max(lo, 1e-9)), -10 * math.log10((hi + lo) / 2)


def reference_detuning():
    """Detuning (laser blue of the resonance) at which the insertion loss is 3.0 dB."""
    lo, hi = -400e-12, 0.0
    for _ in range(80):
        m = (lo + hi) / 2
        if er_il(m)[1] > 3.0: hi = m
        else: lo = m
    return (lo + hi) / 2


DET = reference_detuning()


def dlam_to_dw(dl):
    return -2 * math.pi * C0 * dl / LAM ** 2


# ------------------------------------------------------------------ coupled-mode theory
GAM = W0 / (2 * QL)
MU = math.sqrt(W0 / QC)


def small_signal(f, det_m):
    """|H(f)/H(0)| of the output power for a small sinusoidal shift of the resonance."""
    d0 = dlam_to_dw(-det_m)                     # w_r - w_L; det = lam_L - lam_r
    a0 = -1j * MU / (GAM - 1j * d0)
    s0 = 1 - 1j * MU * a0
    c1 = np.conj(s0) * a0 * MU / 2
    W = 2 * np.pi * np.asarray(f)
    H = c1 / (1j * W - 1j * d0 + GAM) + np.conj(c1) / (1j * W + 1j * d0 + GAM)
    H0 = c1 / (-1j * d0 + GAM) + np.conj(c1) / (1j * d0 + GAM)
    return np.abs(H / H0)


def bw3db(det_m):
    f = np.linspace(1e8, 200e9, 20000)
    h = small_signal(f, det_m)
    idx = np.where(h < 1 / math.sqrt(2))[0]
    return f[idx[0]] if len(idx) else float("nan"), f[np.argmax(h)], 20 * math.log10(h.max())


def cmt_time(lam_r_of_t, det_mid, dt, n):
    """Integrate the CMT equation (RK4) for a resonance wavelength lam_r(t) (relative to its mid value)."""
    a = None; out = np.empty(n)
    def rhs(a, k):
        dw = dlam_to_dw(lam_r_of_t(k)) - dlam_to_dw(det_mid * 0) + dlam_to_dw(-det_mid)   # w_r - w_L
        return (1j * dw - GAM) * a - 1j * MU
    # start from the static solution
    dw0 = dlam_to_dw(lam_r_of_t(0)) + dlam_to_dw(-det_mid)
    a = -1j * MU / (GAM - 1j * dw0)
    for k in range(n):
        k1 = rhs(a, k); k2 = rhs(a + dt / 2 * k1, k); k3 = rhs(a + dt / 2 * k2, k); k4 = rhs(a + dt * k3, k)
        a = a + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[k] = abs(1 - 1j * MU * a) ** 2
    return out


def edge_times(p, dt, t0):
    """10-90 % transition time and overshoot of a step response p (step at index t0)."""
    p0, p1 = p[t0 - 1], p[-1]
    lo, hi = p0 + 0.1 * (p1 - p0), p0 + 0.9 * (p1 - p0)
    seg = p[t0:]
    if p1 > p0:
        t10 = np.argmax(seg >= lo); t90 = np.argmax(seg >= hi); over = (seg.max() - p1) / (p1 - p0)
    else:
        t10 = np.argmax(seg <= lo); t90 = np.argmax(seg <= hi); over = (p1 - seg.min()) / (p0 - p1)
    return (t90 - t10) * dt, over


# ------------------------------------------------------------------ Figure 20.1: small-signal response against detuning
def fig_response():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    f = np.linspace(0.1e9, 60e9, 600)
    dets = [(-0.15, C1), (-0.35, C3), (DET / FWHM_M, C4), (-0.75, C2), (-1.0, C5)]
    for x, col in dets:
        lab = f"{abs(x):.2f} FWHM" + (" (reference)" if abs(x - DET / FWHM_M) < 1e-6 else "")
        a.plot(f / 1e9, 20 * np.log10(small_signal(f, x * FWHM_M)), color=col, label=lab, lw=1.8 if "ref" in lab else 1.3)
    a.axhline(-3, color=MUTED, lw=0.6, ls=":")
    a.set_xlim(0, 60); a.set_ylim(-12, 10)
    finish(a, "Modulation frequency (GHz)", "Response (dB)")
    a.legend(fontsize=6.4, loc="lower left", title="laser blue of resonance by", title_fontsize=6.4)
    tag(a, "a")

    xs = np.linspace(0.02, 1.4, 140)
    bws = [bw3db(-x * FWHM_M)[0] / 1e9 for x in xs]
    b.plot(xs, bws, color=C1, label="3 dB bandwidth (GHz)")
    b.axhline(FWHM_HZ / 1e9, color=MUTED, lw=0.6, ls=":")
    b.text(1.38, FWHM_HZ / 1e9 + 0.8, f"linewidth c/λQ = {FWHM_HZ / 1e9:.1f} GHz", fontsize=6.4, color=MUTED, ha="right")
    b.set_xlim(0, 1.4); b.set_ylim(0, 60)
    finish(b, "Laser detuning (multiples of the 3 dB linewidth)", "3 dB bandwidth (GHz)")
    b2 = b.twinx()
    ers = [er_il(-x * FWHM_M)[0] for x in xs]
    b2.plot(xs, ers, color=C2, ls="--")
    b2.set_ylim(0, 12); b2.set_ylabel("Extinction at 2 Vpp (dB)", color=C2)
    b2.tick_params(axis="y", colors=C2); b2.spines["right"].set_visible(True); b2.spines["right"].set_color(C2); b2.grid(False)
    b.plot([abs(DET) / FWHM_M], [bw3db(DET)[0] / 1e9], "o", color=INK, ms=3.5)
    b.annotate("Worked Example 20.2", (abs(DET) / FWHM_M, bw3db(DET)[0] / 1e9), xytext=(8, -14), textcoords="offset points", fontsize=6.4)
    b.text(0.05, 55, "bandwidth (solid)", fontsize=6.4, color=C1)
    b.text(0.05, 50.5, "extinction (dashed)", fontsize=6.4, color=C2)
    tag(b, "b")
    savefig(fig, "ch20_rrm_response")
    print("Ring: Q_c %.0f, dip %.1f dB, FWHM %.1f pm = %.2f GHz, photon lifetime tau = Q/w = %.2f ps (energy)" %
          (QC, -10 * math.log10(tmin()), FWHM_M * 1e12, FWHM_HZ / 1e9, QL / W0 * 1e12))
    er, il = er_il(DET)
    print("Reference detuning for IL 3.0 dB: %.1f pm (%.3f FWHM, %.2f GHz); ER %.2f dB" % (DET * 1e12, DET / FWHM_M, C0 * abs(DET) / LAM ** 2 / 1e9, er))
    for x in (0.05, 0.15, 0.35, abs(DET) / FWHM_M, 0.75, 1.0, 1.25):
        bw, fpk, pk = bw3db(-x * FWHM_M)
        er, il = er_il(-x * FWHM_M)
        print("   detuning %.2f FWHM: f3dB %.1f GHz, peak %.1f dB at %.1f GHz; ER %.2f dB, IL %.2f dB" % (x, bw / 1e9, pk, fpk / 1e9, er, il))
    print("   half-linewidth pole: %.2f GHz" % (FWHM_HZ / 2 / 1e9))


# ------------------------------------------------------------------ Figure 20.2: large-signal edges
def fig_edges():
    dt = 0.05e-12
    n = 2400
    t0 = 400
    lo_shift, hi_shift = -EFF * VPP / 2, EFF * VPP / 2           # resonance relative to its mid value
    fig, ax = plt.subplots(figsize=(4.9, 2.6))
    res = {}
    for name, a_, b_, col in (("rising bias: resonance moves away from the laser", lo_shift, hi_shift, C1),
                              ("falling bias: resonance moves onto the laser", hi_shift, lo_shift, C4)):
        p = cmt_time(lambda k: a_ if k < t0 else b_, DET, dt, n)
        t = (np.arange(n) - t0) * dt * 1e12
        pn = (p - p[t0 - 1]) / (p[-1] - p[t0 - 1])
        ax.plot(t, pn, color=col, label=name)
        res[name] = edge_times(p, dt, t0) + (p[t0 - 1], p[-1])
    ax.axhline(1, color=MUTED, lw=0.5, ls=":"); ax.axhline(0, color=MUTED, lw=0.5, ls=":")
    ax.set_xlim(-5, 60); ax.set_ylim(-0.15, 1.5)
    finish(ax, "Time after an ideal 2 V step (ps)", "Normalised change of output power")
    ax.legend(fontsize=6.4, loc="lower right")
    savefig(fig, "ch20_rrm_edges")
    for k, (tr, ov, p0, p1) in res.items():
        print("Edge '%s': 10-90 %% %.1f ps, overshoot %.0f %%, power %.3f -> %.3f" % (k, tr * 1e12, ov * 100, p0, p1))
    print("   single-pole reference: 10-90 %% of a pole at the half linewidth %.1f ps" % (2.197 / (2 * math.pi * FWHM_HZ / 2) * 1e12))


# ------------------------------------------------------------------ Figure 20.3: carrier injection and pre-emphasis
def injection_ring_numbers():
    d = json.load(open(os.path.join(HERE, "ch19_pn.json")))
    x, w = np.array(d["x"]), np.array(d["w"])
    gam_core = float(np.sum(w[np.abs(x) <= 0.25]) * (x[1] - x[0]))
    F = 0.8
    def shift(N):        # blue shift (m) for equal electron and hole densities N (cm^-3) in the 500 nm core, along 80 % of the ring
        dn = 8.8e-22 * N + 8.5e-18 * N ** 0.8
        return LAM * F * gam_core * dn / NG
    def dalpha(N):       # added loss in cm^-1, core-weighted and averaged round the ring (carriers on the fraction F only)
        return F * gam_core * (8.5e-18 * N + 6.0e-18 * N)
    return gam_core, F, shift, dalpha


def fig_injection():
    gam_core, F, shift, dalpha = injection_ring_numbers()
    target = 1.5 * FWHM_M
    lo, hi = 1e15, 1e19
    for _ in range(80):
        m = math.sqrt(lo * hi)
        if shift(m) < target: lo = m
        else: hi = m
    N1 = math.sqrt(lo * hi)
    vol = F * 2 * math.pi * R_RING * 0.5e-6 * 0.22e-6 * 1e6            # cm^3
    tau = 1e-9
    I_hold = 1.602e-19 * N1 * vol / tau
    alpha0 = 2 * math.pi * NG / (LAM * 100 * QI)                        # cm^-1 for Q_i
    QI1 = 2 * math.pi * NG / (LAM * 100 * (alpha0 + dalpha(N1)))
    print("Injection ring: core weight %.3f, N for a 1.5-linewidth blue shift %.2e cm^-3 (shift %.0f pm)" % (gam_core, N1, shift(N1) * 1e12))
    print("   core volume %.2e cm^3, hold current %.0f uA (%.0f uW at 0.9 V), Q_i %.0f -> %.0f, intrinsic loss %.1f -> %.1f cm^-1" %
          (vol, I_hold * 1e6, I_hold * 0.9 * 1e6, QI, QI1, alpha0, alpha0 + dalpha(N1)))
    print("   thermal tuning for the same shift at 0.26 nm/mW: %.2f mW" % (shift(N1) * 1e9 / 0.26))
    s28 = 0.28e-9
    lo, hi = 1e15, 1e19
    for _ in range(80):
        m = math.sqrt(lo * hi)
        if shift(m) < s28: lo = m
        else: hi = m
    N28 = math.sqrt(lo * hi)
    I28 = 1.602e-19 * N28 * vol / tau
    print("   0.28 nm by injection: N %.2e, %.0f uA, %.0f uW at 0.9 V; by heater %.2f mW; Q_i -> %.0f" %
          (N28, I28 * 1e6, I28 * 0.9e6, 0.28 / 0.26, 2 * math.pi * NG / (LAM * 100 * (alpha0 + dalpha(N28)))))
    for tp in (40e-12,):
        print("   pre-emphasis pulse %.0f ps: pulse/hold current ratio %.1f; extra forward voltage for that ratio at n = 1.5: %.2f V" %
              (tp * 1e12, tau / tp, 1.5 * 0.02585 * math.log(tau / tp)))
    print("   charge after one 100 ps bit with the hold current alone: %.1f %%" % (100 * (1 - math.exp(-0.1))))

    # time-domain: 10 Gb/s, charge-control model, quasi-static ring (photon lifetime << bit)
    rate, n = 10e9, 200
    T = 1 / rate; dt = T / n
    bits = np.array([0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0])
    tp = 40e-12; npul = int(round(tp / dt))
    def run(mode):
        q = 0.0; Q = []; prev = 0
        for b in bits:
            for k in range(n):
                if mode == "nrz":
                    i = 5.0 * b                                   # five times the hold current, in units of Q1/tau
                else:                                             # hold current plus a charge pulse of about Q1 on each edge
                    i = 1.0 * b
                    if b == 1 and prev == 0 and k < npul: i += tau / tp
                    if b == 0 and prev == 1 and k < npul: i = -(tau / tp)
                q += dt / tau * (i - q)
                q = max(q, 0.0)
                Q.append(q)
            prev = b
        return np.array(Q)
    def transmission(q):
        """Quasi-static through port (photon lifetime << bit); shift and loss taken linear in the charge."""
        qi = 2 * math.pi * NG / (LAM * 100 * (alpha0 + dalpha(N1) * q))
        ql = 1 / (1 / qi + 1 / QC)
        tm = ((1 / qi - 1 / QC) / (1 / qi + 1 / QC)) ** 2
        det = shift(N1) * q                                          # laser at the cold resonance; the resonance moves blue
        return 1 - (1 - tm) / (1 + (2 * det / (LAM / ql)) ** 2)
    t = np.arange(len(bits) * n) * dt * 1e9
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.3, 3.3), sharex=True)
    out = {}
    for mode, col, lab in (("nrz", C4, "NRZ current, 5 × hold"), ("pe", C1, "hold current + 40 ps pre-emphasis pulses")):
        Q = run(mode)
        Tt = np.array([transmission(v) for v in Q])
        a.plot(t, Q, color=col, label=lab)
        b.plot(t, Tt, color=col)
        ones = [Tt[k * n + n - 1] for k in range(len(bits)) if bits[k] == 1]
        zeros = [Tt[k * n + n - 1] for k in range(len(bits)) if bits[k] == 0]
        out[lab] = (min(ones), max(zeros))
    for k, bt in enumerate(bits):
        if bt: a.axvspan(k * T * 1e9, (k + 1) * T * 1e9, color=GRID, alpha=0.5, lw=0)
    a.set_ylim(0, 3.2); a.axhline(1, color=MUTED, lw=0.6, ls=":")
    finish(a, None, "Charge / charge for '1'")
    a.legend(fontsize=6.4, loc="upper left", ncol=2)
    b.set_ylim(0, 1.0)
    finish(b, "Time (ns), 10 Gb/s, shaded bits are '1'", "Transmission")
    savefig(fig, "ch20_injection")
    for k, (o, z) in out.items():
        print("   %s: lowest '1' %.3f, highest '0' %.3f at the end of the bit" % (k, o, z))
    print("   cold dip %.3f; '1' level for steady charge %.3f" % (transmission(0.0), transmission(1.0)))


# ------------------------------------------------------------------ Figure 20.4: PAM4 levels on the ring
def fig_pam4():
    V = np.linspace(0, VPP, 400)
    def T_of_V(v):     # 0 V = low bias end of the 2 Vpp swing
        return T_static(DET - (v - VPP / 2) * EFF)
    Tv = np.array([T_of_V(v) for v in V])
    v_eq = np.linspace(0, VPP, 4)
    t_eq = np.array([T_of_V(v) for v in v_eq])
    t_tg = np.linspace(t_eq.min(), t_eq.max(), 4)
    v_pd = []
    for tt in t_tg:
        lo, hi = 0.0, VPP
        inc = T_of_V(VPP) > T_of_V(0)
        for _ in range(80):
            m = (lo + hi) / 2
            if (T_of_V(m) < tt) == inc: lo = m
            else: hi = m
        v_pd.append((lo + hi) / 2)
    v_pd = np.array(v_pd)
    fig, ax = plt.subplots(figsize=(4.9, 2.7))
    ax.plot(V, Tv, color=INK, lw=1.2, label="ring transmission at the reference detuning")
    ax.plot(v_eq, t_eq, "o", color=C4, ms=5, label="equally spaced drive")
    ax.plot(v_pd, t_tg, "s", color=C1, ms=4.5, mfc="none", mew=1.3, label="pre-distorted drive")
    for tt in t_eq: ax.axhline(tt, color=C4, lw=0.5, ls=":", xmax=0.06)
    for tt in t_tg: ax.axhline(tt, color=C1, lw=0.5, ls="--", xmin=0.94)
    ax.set_xlim(-0.05, VPP + 0.05)
    finish(ax, "Drive voltage within the 2 Vpp swing (V, more reverse bias to the right)", "Transmission")
    ax.legend(fontsize=6.4, loc="upper left")
    savefig(fig, "ch20_pam4")
    eyes = np.diff(t_eq) if t_eq[-1] > t_eq[0] else -np.diff(t_eq)
    ideal = (t_eq.max() - t_eq.min()) / 3
    print("PAM4 on the reference ring: levels %s; eyes %s (ideal %.4f each)" % (np.round(t_eq, 4), np.round(eyes, 4), ideal))
    print("   eye ratios %s; smallest eye penalty %.2f dB" % (np.round(eyes / ideal, 3), 10 * math.log10(ideal / eyes.min())))
    print("   pre-distorted voltages %s V (equally spaced: %s)" % (np.round(v_pd, 3), np.round(v_eq, 3)))


def driver_numbers():
    print("Driver and locking numbers:")
    for eff in (50e-12, 25e-12):
        print("   %.0f pm/V: swing for a 100 pm shift %.1f Vpp; CV^2/4 at 20 fF %.0f fJ/bit" % (eff * 1e12, 100e-12 / eff, 0.25 * 20e-15 * (100e-12 / eff) ** 2 * 1e15))
    Cc, Rb, Cl = 2e-12, 50e3, 70e-15
    print("   AC coupling 2 pF / 50 kOhm into 70 fF: swing kept %.3f (%.2f dB), corner %.2f MHz, droop over 72 bits at 50 Gb/s %.1f %%" %
          (Cc / (Cc + Cl), 20 * math.log10(Cc / (Cc + Cl)), 1 / (2 * math.pi * Rb * Cc) / 1e6, 100 * 72 / 50e9 / (Rb * Cc)))
    # average-power locking at the reference detuning
    a, b = levels(DET)
    tavg = (a + b) / 2
    h = 0.1e-12
    a2, b2 = levels(DET - h)
    slope = ((a2 + b2) / 2 - tavg) / (-h)       # per metre of laser - resonance detuning
    print("   reference point: average transmission %.3f; d<T>/d(detuning) %.4f per pm; a 1 K drift (75 pm) changes <T> by %.3f" %
          (tavg, slope * 1e-12, slope * 75e-12))
    print("   DC bias tuning: +/-1 V moves the resonance +/-%.0f pm = %.2f K of drift" % (EFF * 1e12, EFF / 75e-12))
    # where is the average-power curve monotonic?
    ds = np.linspace(-600e-12, 600e-12, 2401)
    av = np.array([sum(levels(d)) / 2 for d in ds])
    print("   minimum of the average transmission at detuning %.0f pm" % (ds[np.argmin(av)] * 1e12))


if __name__ == "__main__":
    fig_response()
    fig_edges()
    fig_injection()
    fig_pam4()
    driver_numbers()
