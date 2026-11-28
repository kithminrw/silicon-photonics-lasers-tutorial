"""Figures and numbers for the receiver design walkthrough of Chapter 21 (Sections 21.8-21.9).

Run from the repository root:  python -I -X utf8 figsrc/ch21_rx.py
NumPy and matplotlib only. Prints every number the chapter quotes, then writes
assets/figs/ch21_rxchain.svg, ch21_tia.svg, ch21_eyes.svg, ch21_bwopt.svg and ch21_ber.svg.

The models are deliberately simple: a single-pole core amplifier inside a shunt-feedback TIA,
first-order post-amplifier stages, the photodiode's transit time as one pole, Gaussian noise,
a periodic PRBS7 NRZ pattern filtered exactly in the frequency domain (circular convolution).
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch

k_B, T, q = 1.380649e-23, 300.0, 1.602176634e-19
KT4 = 4 * k_B * T
BR = 50e9; TB = 1 / BR                       # 50 Gb/s NRZ, 20 ps unit interval
RESP, ER_DB, ID = 0.9, 4.0, 1e-7             # A/W, extinction (dB), dark current (as in the rx demo)

# ---- the walkthrough's assumptions ------------------------------------------------------------
C_J, C_W, C_PAD = 17e-15, 5e-15, 15e-15      # junction (Ex 21.1), detector wiring (Ex 21.1), pads + micro-bump
GM, FT_EFF = 16e-3, 200e9                    # input inverter g_m and its effective f_T
C_I = GM / (2 * math.pi * FT_EFF)            # input capacitance of the TIA
C_T = C_J + C_W + C_PAD + C_I                # total capacitance at the input node
C_OUT = 16e-15                               # load on the core amplifier's output
GBW = GM / (2 * math.pi * C_OUT)             # gain-bandwidth product of the core amplifier
GAMMA = 1.0                                  # channel-noise factor
F_TR = 54e9                                  # photodiode transit-time limit (Ex 21.1), modelled as one pole
GM_LA = 10e-3                                # first post-amplifier stage
EN_LA = math.sqrt(KT4 * GAMMA / GM_LA * 1.5) # its input noise voltage density (1.5: its load adds half again)
N_LA = 3                                     # post-amplifier stages
F_TIA, F_LA = 45e9, 70e9                     # bandwidth allocation of the broadband design
V_SLICER = 80e-3                             # swing wanted at the decision circuit at sensitivity
VDD = 0.9
GM_ID = 8.0                                  # g_m/I_D of each transistor (1/V)


def ber_of_q(Q): return 0.5 * math.erfc(Q / math.sqrt(2))


def q_for(target):
    lo, hi = 0.0, 20.0
    for _ in range(100):
        m = (lo + hi) / 2
        if ber_of_q(m) > target: lo = m
        else: hi = m
    return (lo + hi) / 2


Q12, QKP4 = q_for(1e-12), q_for(2.4e-4)


def dbm(P): return 10 * math.log10(P / 1e-3)


# ---- responses -------------------------------------------------------------------------------
def pole(f, fp, n=1): return 1 / (1 + 1j * f / fp) ** n


def butter2(f, f3):
    s = 1j * f / f3
    return 1 / (1 + math.sqrt(2) * s + s * s)


def tia_design(f3, CT=C_T, gbw=GBW):
    """Maximally flat (Butterworth) shunt-feedback TIA around a single-pole amplifier of fixed GBW.
    Returns the amplifier gain A, feedback resistor R_F, amplifier time constant tau and R_T."""
    def f0(A):
        tau = A / (2 * math.pi * gbw); x = tau * (A + math.sqrt(A * A - 1))
        return math.sqrt((A + 1) / (x * tau)) / (2 * math.pi)
    lo, hi = 1.0001, 200.0
    for _ in range(200):
        m = (lo + hi) / 2
        if f0(m) > f3: lo = m
        else: hi = m
    A = (lo + hi) / 2; tau = A / (2 * math.pi * gbw); RF = tau * (A + math.sqrt(A * A - 1)) / CT
    return A, RF, tau, RF * A / (A + 1)


def zt(f, A, RF, tau, CT=C_T):
    s = 2j * math.pi * f
    return RF * A / ((A + 1) + s * (tau + RF * CT) + s * s * tau * RF * CT)


def ctle(f, fz, fp): return (1 + 1j * f / fz) / (1 + 1j * f / fp)


def la(f, fla, n=N_LA): return pole(f, fla / math.sqrt(2 ** (1 / n) - 1), n)


def chain(f, ftia, fla, CT=C_T, eq=None):
    """Photocurrent-to-decision response, normalised to 1 at low frequency."""
    A, RF, tau, RT = tia_design(ftia, CT)
    H = zt(f, A, RF, tau, CT) / RT * la(f, fla) * pole(f, F_TR)
    return H * (ctle(f, *eq) if eq else 1)


FN = np.linspace(1e6, 1.5e12, 600001)        # grid for noise integrals


def rx_noise(ftia, fla, CT=C_T, eq=None, en_la=EN_LA):
    """Input-referred rms noise (A) of TIA + post-amplifier: R_F, core amplifier and post-amplifier parts."""
    A, RF, tau, RT = tia_design(ftia, CT)
    Hla2 = np.abs(la(FN, fla) * (ctle(FN, *eq) if eq else 1)) ** 2
    Hz2 = np.abs(zt(FN, A, RF, tau, CT) / RT) ** 2
    s_rf = KT4 / RF
    s_amp = KT4 * GAMMA / GM * (1 / RF ** 2 + (2 * math.pi * FN * CT) ** 2)
    i_rf = np.trapezoid(s_rf * Hz2 * Hla2, FN)
    i_amp = np.trapezoid(s_amp * Hz2 * Hla2, FN)
    i_la = np.trapezoid(en_la ** 2 / RT ** 2 * Hla2, FN)
    return dict(A=A, RF=RF, RT=RT, rf=math.sqrt(i_rf), amp=math.sqrt(i_amp), la=math.sqrt(i_la),
                tot=math.sqrt(i_rf + i_amp + i_la))


def f3db(Hfun, fmax=400e9):
    ff = np.linspace(1e6, fmax, 400001)
    m = np.abs(Hfun(ff)) / abs(Hfun(np.array([1e6]))[0])
    return ff[np.argmax(m < 1 / math.sqrt(2))]


def peaking_db(Hfun, fmax=300e9):
    ff = np.linspace(1e6, fmax, 30001)
    return 20 * math.log10((np.abs(Hfun(ff)) / abs(Hfun(np.array([1e6]))[0])).max())


# ---- PRBS7 NRZ, exact periodic filtering ---------------------------------------------------------
NS = 60                                      # samples per bit (6 samples = 0.1 UI)


def prbs7():
    s, out = 0x7F, []
    for _ in range(127):
        b = ((s >> 6) ^ (s >> 5)) & 1
        s = ((s << 1) | b) & 0x7F
        out.append(b)
    return np.array(out)


BITS = prbs7()
NPTS = len(BITS) * NS
XNRZ = np.repeat(BITS.astype(float), NS)
FR = np.fft.rfftfreq(NPTS, d=TB / NS)


def filt(H): return np.fft.irfft(np.fft.rfft(XNRZ) * H, n=NPTS)


def samples(y, p):
    """The sample of every bit at phase p (in samples from the start of that bit; p may exceed one UI,
    since the filters delay the signal)."""
    return y[(np.arange(len(BITS)) * NS + p) % NPTS]


def pulse(H):
    """Response to a single 1 bit (samples 0..NS-1 high), for DFE tap weights."""
    x = np.zeros(NPTS); x[:NS] = 1.0
    return np.fft.irfft(np.fft.rfft(x) * H, n=NPTS)


def decide(y, p, pr=None, ntap=0, ptap=None):
    """Samples at phase p after an ntap decision-feedback equaliser whose taps are the post-cursors of the
    pulse response pr at phase ptap (correct past decisions assumed)."""
    v = samples(y, p)
    if ntap:
        ptap = p if ptap is None else ptap
        for j in range(1, ntap + 1):
            v = v - pr[(j * NS + ptap) % NPTS] * np.roll(BITS, j)
    return v


def eye_open(y, jit=0, pr=None, ntap=0):
    """Inner vertical eye opening (fraction of the step) at the best phase; jit = phase error tolerated
    (samples) with the DFE taps left at the nominal phase."""
    best, bp = -9.0, 0
    for p in range(3 * NS):
        o = 9.0
        for d in range(-jit, jit + 1):
            v = decide(y, p + d, pr, ntap, p); o = min(o, v[BITS == 1].min() - v[BITS == 0].max())
        if o > best: best, bp = o, p
    return best, bp


def stat_ber(v, sigma1, sigma0):
    """Mean BER over the PRBS7 decisions v (amperes), at the best threshold."""
    ones = v[BITS == 1]; zeros = v[BITS == 0]
    erfc = np.vectorize(math.erfc); best = 1.0
    for th in np.linspace(zeros.min(), ones.max(), 161):
        e = (0.5 * erfc((ones - th) / (sigma1 * math.sqrt(2)))).sum() + (0.5 * erfc((th - zeros) / (sigma0 * math.sqrt(2)))).sum()
        best = min(best, e / len(BITS))
    return best


def levels(Pavg, er_db=ER_DB):
    r = 10 ** (er_db / 10)
    return RESP * 2 * Pavg * r / (r + 1), RESP * 2 * Pavg / (r + 1)


def sens_dbm(sig_th, bwn, extra_db=0.0, M=1.0, F=1.0):
    """Average power for Q = Q12 with thermal + shot + dark-current noise (as the rx demo), plus a penalty."""
    lo, hi = -30.0, 5.0
    for _ in range(80):
        m = (lo + hi) / 2; P = 1e-3 * 10 ** (m / 10); i1, i0 = levels(P)
        s1 = math.sqrt(sig_th ** 2 + 2 * q * (i1 + ID) * bwn); s0 = math.sqrt(sig_th ** 2 + 2 * q * (i0 + ID) * bwn)
        if (i1 - i0) / (s1 + s0) < Q12: lo = m
        else: hi = m
    return (lo + hi) / 2 + extra_db


JIT = NS // 10                               # 0.1 UI of sampling-phase error, in samples
LATCH_NOISE, LATCH_OFFSET = 1e-3, 1e-3       # decision latch: rms input noise and residual offset (V)
F_TIA2 = 20e9                                # the narrow TIA of Section 21.9
EQ = (16e9, 35e9)                            # its CTLE: zero and pole
NTAP = 1                                     # its DFE taps
F_TX = 35e9                                  # an assumed transmitter bandwidth, for one comparison only
SWING = RESP * 2 * (10 ** (ER_DB / 10) - 1) / (10 ** (ER_DB / 10) + 1) * 1e-3 * 10 ** (-11.6 / 10)  # photocurrent swing at -11.6 dBm


def design(ftia, fla, eq=None, ntap=0, ftx=None):
    """Everything the walkthrough quotes for one front end (ftx: optional transmitter pole, not part of the receiver)."""
    d = rx_noise(ftia, fla, eq=eq)
    H = lambda f: chain(f, ftia, fla, eq=eq)
    d["f3"] = f3db(H); d["peak"] = peaking_db(H)
    Hs = H(FR) * (pole(FR, ftx) if ftx else 1)
    d["y"] = filt(Hs); d["pr"] = pulse(Hs); d["ntap"] = ntap
    d["open"], d["ph"] = eye_open(d["y"], 0, d["pr"], ntap); d["open_j"], _ = eye_open(d["y"], JIT, d["pr"], ntap)
    d["v_tia"] = SWING * d["RT"]; d["G"] = V_SLICER / d["v_tia"]; d["gs"] = d["G"] ** (1 / N_LA)
    d["fs"] = fla / math.sqrt(2 ** (1 / N_LA) - 1); d["gbw_stage"] = d["gs"] * d["fs"]
    d["rt_tot"] = d["RT"] * d["G"]; d["latch"] = LATCH_NOISE / d["rt_tot"]; d["sig"] = math.hypot(d["tot"], d["latch"])
    off = 10 * math.log10(1 + 2 * LATCH_OFFSET / V_SLICER)
    d["sens_noise"] = sens_dbm(d["tot"], 35e9); d["sens_latch"] = sens_dbm(d["sig"], 35e9)
    d["sens"] = d["sens_latch"] - 10 * math.log10(d["open"]) + off
    d["sens_j"] = d["sens_latch"] - 10 * math.log10(d["open_j"]) + off if d["open_j"] > 0 else np.inf
    d["off_pen"] = off
    return d


# ======================================================================== numbers for the text
def numbers():
    print("== Step 1: specification")
    r = 10 ** (ER_DB / 10); om = 2 * (r - 1) / (r + 1)
    Ps = 1e-3 * 10 ** (-11.6 / 10)
    print(f"Q(1e-12) = {Q12:.3f}, Q(KP4 2.4e-4) = {QKP4:.3f}; OMA/Pavg at 4 dB ER = {om:.3f}")
    print(f"at -11.6 dBm: Pavg {Ps*1e6:.1f} uW, OMA {om*Ps*1e6:.1f} uW, photocurrent swing {SWING*1e6:.1f} uA, noise allowance swing/2Q = {SWING/(2*Q12)*1e6:.2f} uA rms")
    print(f"Example 21.2: 20 pA/rtHz x sqrt(35 GHz) = {20e-12*math.sqrt(35e9)*1e6:.2f} uA")
    Prx = 1e-3 * 10 ** (-2.7 / 10); i1, i0 = levels(Prx)
    print(f"received -2.7 dBm: avg photocurrent {RESP*Prx*1e6:.0f} uA, swing {(i1-i0)*1e6:.0f} uA pp; dynamic range {-2.7+11.6:.1f} dB optical = {2*(-2.7+11.6):.1f} dB electrical")

    print("\n== Step 2: capacitance")
    print(f"C_I = g_m/(2 pi f_T) = {C_I*1e15:.1f} fF; C_T = {C_J*1e15:.0f} + {C_W*1e15:.0f} + {C_PAD*1e15:.0f} + {C_I*1e15:.1f} = {C_T*1e15:.1f} fF")

    print("\n== Step 3: bandwidth")
    ref = np.trapezoid(np.abs(butter2(FN, 0.7 * BR)) ** 2, FN)
    rows = []
    for rr in np.round(np.arange(0.25, 1.31, 0.05), 2):
        y = filt(butter2(FR, rr * BR)); o, _ = eye_open(y); oj, _ = eye_open(y, JIT)
        npen = 5 * math.log10(np.trapezoid(np.abs(butter2(FN, rr * BR)) ** 2, FN) / ref)
        isi = -10 * math.log10(o) if o > 0 else np.inf; isij = -10 * math.log10(oj) if oj > 0 else np.inf
        rows.append((rr, isi, npen, isi + npen, isij + npen))
    print("generic second-order Butterworth receiver (noise penalty relative to 0.7 B):")
    for rw in rows:
        if rw[0] in (0.3, 0.35, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 1.0, 1.2):
            print(f"  f3 = {rw[0]:.2f} B: ISI {rw[1]:.2f} dB, noise {rw[2]:+.2f} dB, total {rw[3]:+.2f}, with 0.1 UI timing error {rw[4]:+.2f}")
    b0 = min(rows, key=lambda t: t[3]); b1 = min(rows, key=lambda t: t[4])
    print(f"  optimum {b0[0]:.2f} B ({b0[3]:+.2f} dB); with 0.1 UI timing error {b1[0]:.2f} B ({b1[4]:+.2f} dB)")
    b65 = np.trapezoid(np.abs(butter2(FN, 0.65 * BR)) ** 2, FN)
    for rr in (0.3, 0.65, 1.2):
        bwn = np.trapezoid(np.abs(butter2(FN, rr * BR)) ** 2, FN); o = eye_open(filt(butter2(FR, rr * BR)))[0]
        print(f"  eye figure: f3 = {rr} B: noise bandwidth {bwn/1e9:.1f} GHz ({bwn/(rr*BR):.3f} f3), noise x{math.sqrt(bwn/b65):.2f} of 0.65 B, opening {o:.2f}, worst-case Q {o*Q12/math.sqrt(bwn/b65):.1f}")
    i3 = np.trapezoid(np.abs(butter2(FN, 0.7 * BR)) ** 2 * FN ** 2, FN)
    print(f"Personick-style integrals, Butterworth at 0.7B: I2 = {ref/BR:.3f}, I3 = {i3/BR**3:.3f}")
    rss = 1 / math.sqrt(1 / F_TR ** 2 + 1 / F_TIA ** 2 + 1 / F_LA ** 2)
    d = design(F_TIA, F_LA)
    print(f"allocation PD {F_TR/1e9:.0f}, TIA {F_TIA/1e9:.0f}, post-amp {F_LA/1e9:.0f} GHz: root-sum-square {rss/1e9:.1f} GHz, computed {d['f3']/1e9:.1f} GHz = {d['f3']/BR:.2f} B")

    print("\n== Step 4: TIA")
    Rres = 1 / (2 * math.pi * C_T * F_TIA)
    print(f"resistor front end for {F_TIA/1e9:.0f} GHz: R = {Rres:.0f} ohm; white noise {math.sqrt(KT4/Rres)*1e12:.1f} pA/rtHz; post-amp noise referred {EN_LA/Rres*1e12:.1f} pA/rtHz")
    print(f"core amplifier GBW = g_m/(2 pi C_out) = {GBW/1e9:.0f} GHz")
    for f in (25e9, 35e9, 45e9, 65e9):
        a, rf, ta, rt = tia_design(f)
        print(f"  Butterworth TIA at {f/1e9:.0f} GHz: A = {a:.2f}, f_A = {GBW/a/1e9:.0f} GHz, R_F = {rf:.0f}, R_T = {rt:.0f} ohm ({20*math.log10(rt):.1f} dBohm), limit GBW/(2pi C_T f^2) = {GBW/(2*math.pi*C_T*f**2):.0f}")
    A, RF = d["A"], d["RF"]
    print(f"first-order view at the design: R_in = R_F/(A+1) = {RF/(A+1):.0f} ohm; (A+1)/(2 pi R_F C_T) = {(A+1)/(2*math.pi*RF*C_T)/1e9:.0f} GHz; A/g_m = {A/GM:.0f} ohm")

    print("\n== Step 5: noise")
    print(f"white floor 4kT/R_F: {math.sqrt(KT4/RF)*1e12:.1f} pA/rtHz; amplifier f^2 term equals it at {math.sqrt(KT4/RF/(KT4*GAMMA/GM))/(2*math.pi*C_T)/1e9:.0f} GHz and is {math.sqrt(KT4*GAMMA/GM)*2*math.pi*C_T*d['f3']*1e12:.1f} pA/rtHz at {d['f3']/1e9:.0f} GHz")
    print(f"post-amp e_n = {EN_LA*1e9:.2f} nV/rtHz -> {EN_LA/d['RT']*1e12:.1f} pA/rtHz at the input")
    print(f"rms: R_F {d['rf']*1e6:.2f}, amplifier {d['amp']*1e6:.2f}, post-amp {d['la']*1e6:.2f}, total {d['tot']*1e6:.2f} uA; equivalent density over 35 GHz {d['tot']/math.sqrt(35e9)*1e12:.1f} pA/rtHz")
    for ct, lab in ((C_J + C_W + C_I, "monolithic, no pads"), (C_T, "flip-chip"), (C_T + 40e-15, "wire bond, +40 fF")):
        nn = rx_noise(F_TIA, F_LA, CT=ct)
        print(f"  C_T {ct*1e15:.0f} fF ({lab}): R_T {nn['RT']:.0f} ohm, rms {nn['tot']*1e6:.2f} uA, sensitivity change {10*math.log10(nn['tot']/d['tot']):+.2f} dB")
    Hla2 = np.abs(la(FN, F_LA)) ** 2; Hin2 = np.abs(pole(FN, F_TIA)) ** 2
    ires = math.sqrt(np.trapezoid((KT4 / Rres) * Hin2 * Hla2 + EN_LA ** 2 / Rres ** 2 * Hla2, FN))
    print(f"resistor front end ({Rres:.0f} ohm) with the same post-amp: {ires*1e6:.2f} uA rms ({10*math.log10(ires/d['tot']):+.1f} dB)")

    print("\n== Step 6: post-amplifier and decision circuit")
    print(f"TIA output at sensitivity {d['v_tia']*1e3:.1f} mV pp; gain to {V_SLICER*1e3:.0f} mV: {d['G']:.2f} ({20*math.log10(d['G']):.1f} dB); {N_LA} stages of {d['gs']:.2f}")
    print(f"shrinkage sqrt(2^(1/n)-1) = {math.sqrt(2**(1/N_LA)-1):.2f}; each stage needs {d['fs']/1e9:.0f} GHz, GBW {d['gbw_stage']/1e9:.0f} GHz = {d['gbw_stage']/GBW:.2f} x a plain stage")
    print(f"optimum number of stages 2 ln G = {2*math.log(d['G']):.1f}; optimum stage gain sqrt(e) = {math.sqrt(math.e):.2f}")
    for nst in (1, 2, 3, 4):
        g1 = d["G"] ** (1 / nst); print(f"  {nst} plain stages (GBW {GBW/1e9:.0f} GHz each): {GBW/g1*math.sqrt(2**(1/nst)-1)/1e9:.0f} GHz")
    print(f"total transimpedance {d['rt_tot']:.0f} ohm ({20*math.log10(d['rt_tot']):.1f} dBohm); 1 mV rms latch noise -> {d['latch']*1e6:.2f} uA; total {d['sig']*1e6:.2f} uA")
    for off in (1e-3, 3e-3):
        print(f"  latch offset {off*1e3:.0f} mV on {V_SLICER*1e3:.0f} mV: penalty {10*math.log10(1+2*off/V_SLICER):.2f} dB")
    i_avg = RESP * 1e-3 * 10 ** (-2.7 / 10); i1, i0 = levels(1e-3 * 10 ** (-2.7 / 10))
    print(f"at -2.7 dBm: DC photocurrent {i_avg*1e6:.0f} uA -> {i_avg*RF*1e3:.0f} mV across R_F uncancelled; swing {(i1-i0)*d['RT']*1e3:.0f} mV pp at the TIA output, x{d['G']:.1f} -> {(i1-i0)*d['rt_tot']*1e3:.0f} mV")

    print("\n== Step 7: eye and sensitivity")
    print(f"eye opening {d['open']:.3f} -> ISI penalty {-10*math.log10(d['open']):.2f} dB; peaking {d['peak']:.2f} dB")
    print(f"clock 0.1 UI (2 ps) off centre: opening {d['open_j']:.3f} ({-10*math.log10(d['open_j']):.2f} dB)")
    rj = 0.3e-12
    print(f"random clock jitter {rj*1e12:.1f} ps rms uses 2Q x RJ = {2*Q12*rj*1e12:.1f} ps of the {TB*1e12:.0f} ps unit interval")
    print(f"sensitivity: thermal+shot {d['sens_noise']:.2f} dBm; + latch noise {d['sens_latch']:.2f}; + ISI and {LATCH_OFFSET*1e3:.0f} mV offset ({d['off_pen']:.2f} dB) {d['sens']:.2f} dBm; with 0.1 UI timing error {d['sens_j']:.2f} dBm")
    print(f"(Example 21.2's 3.74 uA receiver: {sens_dbm(20e-12*math.sqrt(35e9), 35e9):.2f} dBm)")

    print("\n== Step 8: power")
    i_tia = GM / (2 * GM_ID); p_tia = i_tia * VDD
    i_la = 2 * GM_LA / GM_ID; p_la = N_LA * i_la * VDD; p_dc = 0.3e-3
    p_fe = p_tia + p_la + p_dc
    print(f"TIA inverter: g_m {GM*1e3:.0f} mS from NMOS + PMOS at g_m/I_D = {GM_ID:.0f}/V each -> {i_tia*1e3:.2f} mA, {p_tia*1e3:.2f} mW at {VDD} V")
    print(f"post-amp: {i_la*1e3:.1f} mA per stage -> {p_la*1e3:.2f} mW; DC loop and bias {p_dc*1e3:.1f} mW; front end {p_fe*1e3:.2f} mW = {p_fe/BR*1e12:.2f} pJ/bit")
    print(f"Table 38.1 allows 1.0 pJ/bit = {1.0e-12*BR*1e3:.0f} mW per lane; left for decision, clock recovery, deserialiser: {(1.0e-12*BR-p_fe)*1e3:.0f} mW")

    print("\n== Section 21.9: noise against TIA bandwidth")
    sweep = []
    for ft in (20e9, 25e9, 30e9, 35e9, 45e9, 55e9):
        dd = design(ft, F_LA); sweep.append((ft, dd))
        print(f"  TIA {ft/1e9:.0f} GHz: R_F {dd['RF']:.0f}, R_T {dd['RT']:.0f} ohm, overall {dd['f3']/1e9:.1f} GHz ({dd['f3']/BR:.2f} B), rms {dd['tot']*1e6:.2f} uA, opening {dd['open']:.3f}, sensitivity {dd['sens']:.2f} dBm (0.1 UI off {dd['sens_j']:.2f})")
    a30 = [x for x in sweep if x[0] == 30e9][0][1]
    expo = math.log(d['tot'] / a30['tot']) / math.log(d['f3'] / a30['f3'])
    print(f"  30 -> 45 GHz TIA: overall bandwidth x{d['f3']/a30['f3']:.2f}, noise x{d['tot']/a30['tot']:.2f}: i_rms grows as bandwidth^{expo:.1f}")
    print("\n== Section 21.9: narrow TIA with equalisers")
    d3 = design(F_TIA2, F_LA); d2 = design(F_TIA2, F_LA, eq=EQ); d4 = design(F_TIA2, F_LA, ntap=NTAP); d5 = design(F_TIA2, F_LA, ntap=2)
    print(f"TIA {F_TIA2/1e9:.0f} GHz: A {d3['A']:.2f}, R_F {d3['RF']:.0f}, R_T {d3['RT']:.0f}; output at sensitivity {d3['v_tia']*1e3:.0f} mV pp")
    for lab, dd in (("alone", d3), (f"+ CTLE (zero {EQ[0]/1e9:.0f}, pole {EQ[1]/1e9:.0f} GHz, boost {20*math.log10(EQ[1]/EQ[0]):.1f} dB)", d2), ("+ 1-tap DFE", d4), ("+ 2-tap DFE", d5)):
        print(f"  {lab}: overall {dd['f3']/1e9:.1f} GHz, opening {dd['open']:.3f} (0.1 UI off {dd['open_j']:.3f}), rms {dd['tot']*1e6:.2f} uA, sensitivity {dd['sens']:.2f} dBm (0.1 UI off {dd['sens_j']:.2f}), better than Example 21.3 by {d['sens']-dd['sens']:.2f} dB")
    print(f"  DFE first tap h1 = {d4['pr'][(NS + d4['ph']) % NPTS]:.3f} of the step, main cursor h0 = {d4['pr'][d4['ph'] % NPTS]:.3f}")
    a, b = design(F_TIA, F_LA, ftx=F_TX), design(F_TIA2, F_LA, ntap=NTAP, ftx=F_TX)
    print(f"with a {F_TX/1e9:.0f} GHz transmitter pole: Example 21.3 {a['sens']:.2f} dBm (loses {a['sens']-d['sens']:.2f} dB), narrow TIA + 1-tap DFE {b['sens']:.2f} dBm (loses {b['sens']-d4['sens']:.2f} dB)")
    i_avg = RESP * 1e-3 * 10 ** (-2.7 / 10); i1, i0 = levels(1e-3 * 10 ** (-2.7 / 10))
    print(f"narrow TIA at -2.7 dBm: swing {(i1-i0)*d3['RT']*1e3:.0f} mV pp, DC {i_avg*d3['RF']*1e3:.0f} mV across R_F")
    print(f"BER test: no errors in {math.log(20)/1e-12:.2e} bits gives 95 % confidence of BER < 1e-12: {math.log(20)/1e-12/BR:.0f} s at 50 Gb/s; for 1e-9: {math.log(20)/1e-9/BR*1e3:.0f} ms")
    return d, d2, d3, d4, sweep


# ======================================================================== figures
def _tri(ax, x, y, w, h, **kw):
    ax.add_patch(Polygon([[x, y - h / 2], [x, y + h / 2], [x + w, y]], closed=True, **kw))


def fig_chain(d):
    """Block diagram of the front end with the capacitances, bandwidths and signal levels of Worked Example 21.3."""
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.set_xlim(-1.6, 13.4); ax.set_ylim(0, 5.4); ax.axis("off")
    y = 3.35; lw = 1.2
    kw = dict(fill=False, ec=INK, lw=lw)
    ax.annotate("", xy=(0.95, y), xytext=(-0.1, y), arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.6))
    ax.text(-0.1, y + 0.22, "light", color=AMBER, fontsize=7.5)
    ax.add_patch(plt.Circle((1.4, y), 0.42, fill=False, ec=INK, lw=lw))
    ax.annotate("", xy=(1.4, y + 0.28), xytext=(1.4, y - 0.28), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1))
    ax.text(1.4, y + 0.6, "Ge PD", ha="center", fontsize=7.5, fontweight="bold")
    ax.plot([1.82, 6.3], [y, y], color=INK, lw=lw)
    caps = ((2.5, f"{(C_J+C_W)*1e15:.0f} fF\ndetector", C1), (3.9, f"{C_PAD*1e15:.0f} fF\npads, bump", C2), (5.3, f"{C_I*1e15:.0f} fF\nTIA input", C3))
    for xc, lab, col in caps:
        ax.plot([xc, xc], [y, y - 0.55], color=INK, lw=lw)
        ax.plot([xc - 0.22, xc + 0.22], [y - 0.55, y - 0.55], color=col, lw=2.2)
        ax.plot([xc - 0.22, xc + 0.22], [y - 0.72, y - 0.72], color=col, lw=2.2)
        ax.plot([xc, xc], [y - 0.72, y - 0.98], color=INK, lw=lw)
        ax.plot([xc - 0.15, xc + 0.15], [y - 0.98, y - 0.98], color=INK, lw=lw)
        ax.text(xc, y - 1.45, lab, ha="center", va="center", fontsize=6.6, color=col, linespacing=1.05)
    ax.text(3.9, y - 2.1, f"C$_T$ = {C_T*1e15:.0f} fF", ha="center", fontsize=7.5, color=INK, fontweight="bold")
    xt = 6.3                                   # TIA input
    _tri(ax, xt, y, 1.05, 1.1, **kw); ax.text(xt + 0.2, y, "−A", fontsize=7.5, va="center")
    ax.plot([xt - 0.3, xt - 0.3, xt + 1.35, xt + 1.35], [y, y + 1.0, y + 1.0, y], color=INK, lw=lw)
    ax.add_patch(Rectangle((xt + 0.15, y + 0.87), 0.75, 0.26, fill=True, fc="white", ec=INK, lw=lw))
    ax.text(xt + 0.52, y + 1.27, f"R$_F$ = {d['RF']:.0f} Ω", ha="center", fontsize=7)
    ax.text(xt + 0.52, y + 1.68, "TIA", ha="center", fontweight="bold", fontsize=8)
    ax.add_patch(Rectangle((xt - 0.38, y - 1.55), 1.81, 0.5, fill=False, ec=MUTED, lw=1, ls="--"))   # wide enough for its label
    ax.text(xt + 0.52, y - 1.3, "DC cancel", ha="center", va="center", fontsize=6.5, color=MUTED)
    ax.plot([xt + 1.35, xt + 1.35], [y, y - 1.05], color=MUTED, lw=1, ls="--")                  # from the output into the box
    ax.plot([xt - 0.3, xt - 0.3], [y - 1.05, y], color=MUTED, lw=1, ls="--")                    # and back to the input
    xl = 8.05                                  # post-amplifier
    ax.plot([xt + 1.05, xl], [y, y], color=INK, lw=lw)
    for i in range(N_LA):
        _tri(ax, xl + 0.72 * i, y, 0.52, 0.62, **kw)
        ax.plot([xl + 0.52 + 0.72 * i, xl + 0.72 + 0.72 * i], [y, y], color=INK, lw=lw)
    xlc = xl + 0.72 * (N_LA - 1) / 2 + 0.26
    ax.text(xlc, y + 0.72, "post-amplifier", ha="center", fontweight="bold", fontsize=8)
    ax.text(xlc, y + 0.46, f"{N_LA} stages, ×{d['G']:.1f}", ha="center", fontsize=7)
    xd = 10.35                                 # decision circuit
    ax.plot([xl + 0.72 * N_LA - 0.2, xd], [y, y], color=INK, lw=lw)
    ax.add_patch(Rectangle((xd, y - 0.42), 1.4, 0.84, fill=False, ec=INK, lw=lw))
    ax.text(xd + 0.7, y + 0.1, "decision", ha="center", va="center", fontsize=7.5, fontweight="bold")
    ax.text(xd + 0.7, y - 0.2, "latch", ha="center", va="center", fontsize=6.5, color=MUTED)
    ax.annotate("", xy=(12.65, y), xytext=(xd + 1.4, y), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1))
    ax.text(12.7, y, "data", va="center", fontsize=7.5)
    ax.add_patch(Rectangle((xd, y - 1.8), 1.4, 0.72, fill=False, ec=INK, lw=lw))
    ax.text(xd + 0.7, y - 1.44, "clock\nrecovery", ha="center", va="center", fontsize=6.8, linespacing=1.0)
    ax.annotate("", xy=(xd + 0.7, y - 0.42), xytext=(xd + 0.7, y - 1.08), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1))
    ax.plot([xd + 1.4, xd + 1.85, xd + 1.85], [y - 1.44, y - 1.44, y], color=INK, lw=1)
    yb = 0.62
    ax.plot([-1.5, 13.3], [yb + 0.45, yb + 0.45], color=GRID, lw=0.8)
    ax.text(-1.5, yb + 0.12, "bandwidth", fontsize=6.8, color=MUTED, fontweight="bold", va="center")
    ax.text(-1.5, yb - 0.4, "signal at\n−11.6 dBm", fontsize=6.8, color=MUTED, fontweight="bold", va="center", linespacing=1.0)
    for xc, bw, sig in ((1.4, f"{F_TR/1e9:.0f} GHz (transit)", f"{SWING*1e6:.0f} µA pp"),
                        (xt + 0.52, f"{F_TIA/1e9:.0f} GHz", f"{d['v_tia']*1e3:.1f} mV pp"),
                        (xlc, f"{F_LA/1e9:.0f} GHz", ""),
                        (xd + 0.7, f"{d['f3']/1e9:.0f} GHz overall", f"{V_SLICER*1e3:.0f} mV pp")):
        ax.text(xc, yb + 0.12, bw, ha="center", fontsize=7, color=INK, va="center")
        if sig: ax.text(xc, yb - 0.4, sig, ha="center", fontsize=7, color=C4, va="center")
    savefig(fig, "ch21_rxchain")


def fig_tia():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    f = np.logspace(9, 11.5, 600)
    designs = [(25e9, C1), (35e9, C3), (45e9, C2), (65e9, C4)]
    for f3, col in designs:
        A, RF, tau, RT = tia_design(f3)
        a.semilogx(f / 1e9, 20 * np.log10(np.abs(zt(f, A, RF, tau))), color=col, label=f"{f3/1e9:.0f} GHz: R$_F$ = {RF:.0f} Ω, A = {A:.1f}")
        a.plot(f3 / 1e9, 20 * math.log10(RT / math.sqrt(2)), "o", color=col, ms=4)
    fl = np.logspace(math.log10(18e9), math.log10(95e9), 50)
    a.semilogx(fl / 1e9, 20 * np.log10(GBW / (2 * math.pi * C_T * fl ** 2) / math.sqrt(2)), ls="--", color=MUTED, lw=1)
    a.text(60, 52, "limit:\nR$_T$ falls\nas 1/f²", fontsize=7, color=MUTED, va="top")
    a.set_xlim(1, 300); a.set_ylim(30, 62)
    finish(a, "Frequency (GHz)", "Transimpedance (dBΩ)")
    a.legend(loc="lower left", fontsize=6.4)
    for f3, col in designs:
        A, RF, tau, RT = tia_design(f3)
        s = KT4 / RF + KT4 * GAMMA / GM * (1 / RF ** 2 + (2 * math.pi * f * C_T) ** 2)
        b.loglog(f / 1e9, np.sqrt(s) * 1e12, color=col, label=f"R$_F$ = {RF:.0f} Ω")
    b.set_xlim(1, 300); b.set_ylim(2, 300)
    b.text(150, 150, "f² rise:\namplifier\nnoise × C$_T$", fontsize=7, color=MUTED, ha="center", va="center")
    b.text(1.3, 2.6, "white floors: 4kT/R$_F$", fontsize=7, color=MUTED)
    finish(b, "Frequency (GHz)", "Input-referred noise (pA/√Hz)")
    b.legend(loc="upper left", fontsize=6.4)
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.5)
    savefig(fig, "ch21_tia")


def fig_eyes():
    """Eyes at the decision circuit for three bandwidths of a second-order Butterworth receiver at one received
    power: the noise is white noise filtered by the same response, scaled so that an ISI-free eye at
    0.65 x bit rate has Q = 7.03 (sensitivity), and growing with the square root of the noise bandwidth."""
    rng = np.random.default_rng(7)
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.4), sharey=True)
    sig_ref = 1 / (2 * Q12)
    b65 = np.trapezoid(np.abs(butter2(FN, 0.65 * BR)) ** 2, FN)
    t = (np.arange(2 * NS + 1) - NS) / NS
    for ax, rr, title in zip(axs, (0.3, 0.65, 1.2), ("too little: 0.3 × bit rate", "about right: 0.65 × bit rate", "too much: 1.2 × bit rate")):
        H = butter2(FR, rr * BR); y = filt(H); o, ph = eye_open(y)
        sig = sig_ref * math.sqrt(np.trapezoid(np.abs(butter2(FN, rr * BR)) ** 2, FN) / b65)
        shift = ph - NS // 2
        segs = []
        for rep in range(4):
            nz = np.fft.irfft(np.fft.rfft(rng.normal(0, 1, NPTS)) * H, n=NPTS)
            yn = np.roll(y + nz * sig / nz.std(), -shift)
            for kbit in range(len(BITS)):
                idx = (kbit * NS + NS // 2 - NS + np.arange(2 * NS + 1)) % NPTS
                segs.append(np.column_stack([t, yn[idx]]))
        ax.add_collection(LineCollection(segs, colors=C1, linewidths=0.5, alpha=0.09, rasterized=True))
        Y = samples(y, ph)
        lo1, hi0 = Y[BITS == 1].min(), Y[BITS == 0].max()
        ax.annotate("", xy=(0, lo1), xytext=(0, hi0), arrowprops=dict(arrowstyle="<->", color=C4, lw=1.1, shrinkA=0, shrinkB=0))
        ax.axhline(0.5, color=MUTED, lw=0.6, ls=":")
        ax.set_xlim(-1, 1); ax.set_ylim(-0.5, 1.5)
        ax.set_title(title, fontsize=7.8, loc="left", color=INK)
        ax.text(0.04, 0.03, f"opening {o:.2f}, noise ×{sig/sig_ref:.2f}\nworst-case Q = {o/(2*sig):.1f}", transform=ax.transAxes, fontsize=6.6, color=INK)
        ax.set_xticks([-1, -0.5, 0, 0.5, 1]); ax.set_xticklabels(["−1", "", "0", "", "1"])
        ax.set_xlabel("Time (UI)")
    axs[0].set_ylabel("Signal (normalised)")
    fig.tight_layout(w_pad=1.0)
    savefig(fig, "ch21_eyes")


def fig_bwopt(sweep_f):
    """Sensitivity against overall receiver bandwidth: a receiver whose noise density stays at 20 pA/rtHz
    (second-order Butterworth response), and the TIA-limited front end of Section 21.8 (TIA bandwidth swept)."""
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    rs = np.round(np.arange(0.3, 1.31, 0.025), 3); s_n, s_i, s_j = [], [], []
    for rr in rs:
        y = filt(butter2(FR, rr * BR)); o, _ = eye_open(y); oj, _ = eye_open(y, JIT)
        bwn = np.trapezoid(np.abs(butter2(FN, rr * BR)) ** 2, FN); base = sens_dbm(20e-12 * math.sqrt(bwn), bwn)
        s_n.append(base); s_i.append(base - 10 * math.log10(o) if o > 0 else np.nan); s_j.append(base - 10 * math.log10(oj) if oj > 0 else np.nan)
    s_n, s_i, s_j = map(np.array, (s_n, s_i, s_j))
    ax.plot(rs, s_n, color=C1, lw=1.0, ls=":", label="20 pA/√Hz: noise only")
    ax.plot(rs, s_i, color=C1, label="20 pA/√Hz: noise and ISI")
    ax.plot(rs, s_j, color=C1, lw=1.0, ls="--", label="… clock 0.1 UI off centre")
    i0 = np.nanargmin(s_i); ax.plot(rs[i0], s_i[i0], "o", color=C1, ms=4)
    print(f"  bwopt: 20 pA/rtHz receiver: best {s_i[i0]:.2f} dBm at {rs[i0]:.3f} B; clock off: best {np.nanmin(s_j):.2f} at {rs[np.nanargmin(s_j)]:.3f} B; at 0.7 B {s_i[np.argmin(abs(rs-0.7))]:.2f}")
    xs = np.array([dd["f3"] / BR for dd in sweep_f]); ys = np.array([dd["sens"] for dd in sweep_f]); yj = np.array([dd["sens_j"] for dd in sweep_f])
    ax.plot(xs, ys, color=C3, label="TIA-limited front end (C$_T$ = 50 fF)")
    ax.plot(xs, yj, color=C3, lw=1.0, ls="--", label="… clock 0.1 UI off centre")
    j = int(np.argmin(ys)); ax.plot(xs[j], ys[j], "o", color=C3, ms=4)
    print(f"  bwopt: TIA-limited: best {ys[j]:.2f} dBm at {xs[j]:.3f} B (TIA {sweep_f[j]['ftia']/1e9:.0f} GHz); clock off best {np.nanmin(yj):.2f} at {xs[int(np.nanargmin(yj))]:.3f} B")
    dx = [dd for dd in sweep_f if abs(dd["ftia"] - F_TIA) < 1][0]
    ax.plot(dx["f3"] / BR, dx["sens"], "s", color=C2, ms=5)
    ax.annotate("Example 21.3", (dx["f3"] / BR, dx["sens"]), xytext=(8, -12), textcoords="offset points", fontsize=7, color=C2)
    ax.set_xlim(0.3, 1.3); ax.set_ylim(-15.5, -8)
    finish(ax, "Receiver bandwidth / bit rate", "Sensitivity at $10^{-12}$ (dBm)")
    ax.legend(loc="lower right", fontsize=6.4)                # the empty corner; at upper right the curve crossed it
    savefig(fig, "ch21_bwopt")


def ber_curve(d, P):
    out = []
    for p in P:
        Pw = 1e-3 * 10 ** (p / 10); i1, i0 = levels(Pw)
        s1 = math.sqrt(d["sig"] ** 2 + 2 * q * (i1 + ID) * 35e9); s0 = math.sqrt(d["sig"] ** 2 + 2 * q * (i0 + ID) * 35e9)
        v = i0 + (i1 - i0) * decide(d["y"], d["ph"], d["pr"], d["ntap"])
        out.append(stat_ber(v, s1, s0))
    return np.maximum(np.array(out), 1e-20)


def p_at(P, b, target=1e-12):
    lb = np.log10(b); j = int(np.argmax(lb < math.log10(target)))
    return P[j - 1] + (P[j] - P[j - 1]) * (math.log10(target) - lb[j - 1]) / (lb[j] - lb[j - 1]) if j > 0 else float("nan")


def fig_ber(d, d2, d3, d4):
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    P = np.linspace(-18, -8, 41)
    cases = [(f"Example 21.3 ({F_TIA/1e9:.0f} GHz TIA)", d, C1, "-"), (f"{F_TIA2/1e9:.0f} GHz TIA alone", d3, C4, "--"),
             (f"{F_TIA2/1e9:.0f} GHz TIA + CTLE", d2, C2, "-"), (f"{F_TIA2/1e9:.0f} GHz TIA + 1-tap DFE", d4, C3, "-")]
    for lab, dd, col, ls in cases:
        b = ber_curve(dd, P)
        ax.semilogy(P, b, color=col, ls=ls, label=lab)
        print(f"  BER curve {lab}: 1e-12 at {p_at(P, b):.2f} dBm, 2.4e-4 at {p_at(P, b, 2.4e-4):.2f} dBm")
    ax.axhline(1e-12, color=MUTED, lw=0.7, ls=":"); ax.text(-17.85, 2.5e-12, "$10^{-12}$", fontsize=7, color=MUTED)
    ax.axhline(2.4e-4, color=MUTED, lw=0.7, ls=":"); ax.text(-17.85, 5e-4, "KP4 FEC threshold", fontsize=7, color=MUTED)
    ax.set_xlim(-18, -10); ax.set_ylim(1e-16, 1e-1)
    finish(ax, "Average received power (dBm)", "Bit-error ratio")
    lg = ax.legend(loc="upper right", fontsize=6.5, frameon=True, framealpha=0.92, edgecolor="none")
    savefig(fig, "ch21_ber")


if __name__ == "__main__":
    d, d2, d3, d4, sweep = numbers()
    fig_chain(d); fig_tia(); fig_eyes()
    sweep_f = []
    for ft in np.concatenate([np.arange(14e9, 40e9, 2e9), np.arange(40e9, 85e9, 5e9)]):
        dd = design(ft, F_LA); dd["ftia"] = ft; sweep_f.append(dd)
    fig_bwopt(sweep_f); fig_ber(d, d2, d3, d4)
