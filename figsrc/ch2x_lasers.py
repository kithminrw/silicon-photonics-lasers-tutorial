"""Figures and numbers for the VCSEL (Section 24.8) and laser-driving (Sections 25.7-25.9) additions.

Run from the repository root:  python -I -X utf8 figsrc/ch2x_lasers.py
NumPy and matplotlib only; about a minute (the eye diagrams integrate the rate equations).
Prints every number the chapters quote, then writes assets/figs/ch24_vcsel.svg, ch24_vcsel_li.svg,
ch25_bw.svg, ch25_zerolevel.svg and ch25_eyes.svg.

Two lasers:
  * the 400 um InGaAsP Fabry-Perot laser of Chapter 24 (the parameters of _includes/demos/laser.html and dyn.html);
  * an illustrative 850 nm oxide-aperture VCSEL: GaAs/AlGaAs mirrors computed with transfer matrices, three
    8 nm quantum wells, a 6 um aperture. Its temperature behaviour is a deliberately simple model: transparency
    density proportional to absolute temperature, gain peak moving 0.30 nm/K against a cavity resonance moving
    0.065 nm/K (Lorentzian gain spectrum, 20 nm half-width), carrier leakage switching on above ~120 C junction temperature, and
    self-heating through a 2.5 K/mW thermal impedance. The numbers are typical in size, not those of any product.
Large-signal runs integrate the rate equations (RK4) behind a small parasitic network (pad capacitance, mirror
resistance, junction capacitance and diode), for a periodic PRBS7 pattern, and view the output through a
fourth-order Bessel-Thomson reference receiver at 0.75 x the bit rate.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle, FancyArrowPatch

q, c, kB = 1.602e-19, 3e10, 8.617e-5          # C, cm/s, eV/K
TWO_PI = 2 * np.pi

# ============================================================== the Chapter 24 Fabry-Perot laser (cm, s)
FP = dict(L=400e-4, w=2e-4, d=0.05e-4, Gam=0.06, eta=0.8, ai=15.0, g0=1500.0, Ntr=2e18, eps=2e-17, R=0.32,
          A=1e8, B=1e-10, C=3e-29, ng=3.6, lam=1.55, T0=60.0)


def fp_op(I):
    """Operating point of the Chapter 24 laser at current I (A), as in the dyn.html demo."""
    p = FP; vg = c / p["ng"]; V = p["L"] * p["w"] * p["d"]
    am = np.log(1 / p["R"] ** 2) / (2 * p["L"]); tp = 1 / (vg * (p["ai"] + am))
    Nth = p["Ntr"] * np.exp((p["ai"] + am) / p["Gam"] / p["g0"])
    Ith = q * V / p["eta"] * (p["A"] * Nth + p["B"] * Nth ** 2 + p["C"] * Nth ** 3)
    S = p["Gam"] * tp * p["eta"] * max(I - Ith, 0) / (q * V); a = p["g0"] / Nth
    fr = np.sqrt(vg * a * S / (tp * (1 + p["eps"] * S))) / TWO_PI
    slope = 0.5 * p["eta"] * am / (p["ai"] + am) * 1.2398 / p["lam"]          # W/A per facet
    return dict(Ith=Ith, fr=fr, slope=slope)


# ============================================================== the VCSEL
LAM = 0.85                                   # um
NH, NL, NC, NSUB = 3.52, 3.05, 3.42, 3.65    # Al0.12GaAs, Al0.9GaAs, Al0.3GaAs spacer, GaAs (approximate, 850 nm)
NTOP, NBOT = 20, 34                          # mirror pairs
HV_Q = 1.2398 / LAM                          # photon energy in eV (= V)


def layer_matrix(n, d, lam):
    k = TWO_PI * n / lam * d
    return np.array([[np.cos(k), 1j * np.sin(k) / n], [1j * n * np.sin(k), np.cos(k)]])


def refl(n_in, layers, n_out, lam):
    M = np.eye(2, dtype=complex)
    for n, d in layers:
        M = M @ layer_matrix(n, d, lam)
    B, C = M @ np.array([1, n_out])
    return (n_in * B - C) / (n_in * B + C)


def pairs(N, lam=LAM):
    """N quarter-wave pairs, low index first (seen from the cavity)."""
    return [(NL, lam / 4 / NL), (NH, lam / 4 / NH)] * N


TOP = pairs(NTOP)                              # cavity -> air
BOT = pairs(NBOT) + [(NL, LAM / 4 / NL)]       # cavity -> substrate


def penetration(layers, n_out):
    """Phase penetration depth -(1/2) dphi/dbeta of a mirror seen from the cavity (um)."""
    dl = 1e-4
    p = [np.angle(refl(NC, layers, n_out, l)) for l in (LAM - dl, LAM + dl)]
    db = TWO_PI * NC * (1 / (LAM + dl) - 1 / (LAM - dl))
    return -(p[1] - p[0]) / db / 2


R_TOP, R_BOT = abs(refl(NC, TOP, 1.0, LAM)) ** 2, abs(refl(NC, BOT, NSUB, LAM)) ** 2
LPEN_T, LPEN_B = penetration(TOP, 1.0), penetration(BOT, NSUB)
LCAV = LAM / NC                                                  # one-wavelength cavity (um)
LEFF = (LCAV + LPEN_T + LPEN_B) * 1e-4                           # cm
AM = np.log(1 / (R_TOP * R_BOT)) / (2 * LEFF); AMT = np.log(1 / R_TOP) / (2 * LEFF)
AI, NG = 20.0, 3.8; VG = c / NG
DIA, NW, DW = 6e-4, 3, 8e-7                                      # aperture (cm), wells, well width (cm)
VACT = np.pi * (DIA / 2) ** 2 * NW * DW
GAM = 1.8 * NW * DW / LEFF * 0.8                                 # standing-wave factor 1.8, transverse overlap 0.8
TP = 1 / (VG * (AI + AM)); GTH = (AI + AM) / GAM
G0, NTR25, A_, B_, C_, ETA0, EPS, BETA = 3000.0, 1.8e18, 1e8, 1e-10, 1e-30, 0.8, 2e-17, 1e-4
LP25, DLP, DLC, WG = 838.0, 0.30, 0.065, 20.0                    # gain peak, its drift, cavity drift (nm, nm/K), half-width
TLK, DTLK = 140.0, 20.0                                          # leakage: eta_i halves at 140 C junction
ZTH, V0, RS = 2.5e3, 1.55, 80.0                                  # K/W, V, ohm
CP, RM, CJ, NID = 120e-15, 70.0, 250e-15, 2.0                    # parasitics: pad C, mirror R, junction C, ideality
ALPHA = 4.0


def detune(T): return 1 / (1 + (((850 + DLC * (T - 25)) - (LP25 + DLP * (T - 25))) / WG) ** 2)
def ntr(T): return NTR25 * (T + 273.15) / 298.15
def etai(T): return ETA0 / (1 + np.exp((T - TLK) / DTLK))
def nth(T): return ntr(T) * np.exp(GTH / (G0 * detune(T)))
def rrec(N): return A_ * N + B_ * N ** 2 + C_ * N ** 3
def ith(T): return q * VACT * rrec(nth(T)) / etai(T)
def slope(T): return etai(T) * AMT / (AI + AM) * HV_Q        # W/A through the top mirror
def volt(I): return V0 + RS * I


def li(I, Ta):
    """Self-consistent CW output (W) and junction temperature (C) at current I (A) and ambient Ta."""
    T = Ta
    for _ in range(300):
        P = max(0.0, slope(T) * (I - ith(T)))
        T = 0.5 * T + 0.5 * (Ta + ZTH * (I * volt(I) - P))
    return P, T


def vcsel_ss(I, Ta=25.0):
    """Small-signal parameters at bias I: relaxation frequency, damping, and the parasitic network."""
    P, T = li(I, Ta)
    S = P * GAM / (VACT * HV_Q * q * VG * AMT)
    N = nth(T); a = G0 * detune(T) / N
    wr2 = VG * a * S / (TP * (1 + EPS * S)); K = 4 * np.pi ** 2 * (TP + EPS / (VG * a))
    tdn = 1 / (A_ + 2 * B_ * N + 3 * C_ * N ** 2)
    gam = K * wr2 / (4 * np.pi ** 2) + 1 / tdn
    Rj = NID * kB * (T + 273.15) / I
    return dict(P=P, T=T, S=S, a=a, wr2=wr2, fr=np.sqrt(wr2) / TWO_PI, K=K, gam=gam, Rj=Rj, tdn=tdn)


def vcsel_H(f, o, parasitics=True):
    w = TWO_PI * f
    H = o["wr2"] / (o["wr2"] - w ** 2 + 1j * w * o["gam"])
    if parasitics:
        Zp = 1 / (1j * w * CP); Zb = RM + o["Rj"] / (1 + 1j * w * o["Rj"] * CJ)
        H = H * Zp / (Zp + Zb) / (1 + 1j * w * o["Rj"] * CJ)
    return H


def f3db(o, parasitics=True):
    f = np.linspace(1e7, 1e11, 20001); H2 = np.abs(vcsel_H(f, o, parasitics)) ** 2
    return f[np.argmax(H2 < 0.5)]


# ============================================================== large-signal simulation
def prbs7():
    s, out = [1] * 7, []
    for _ in range(127):
        out.append(s[6]); s = [s[6] ^ s[5]] + s[:6]
    return np.array(out)


BITS = prbs7()


def drive(I0, I1, spb, taps=(1.0,), pre=0):
    """FIR current drive: I = Imid + (I1-I0)/2 * sum_k c_k d[n-k] (d = +-1). sum(c) = 1 keeps the steady levels."""
    d = 2 * BITS - 1; x = np.zeros(len(d))
    for j, cj in enumerate(taps):
        x += cj * np.roll(d, j - pre)
    return np.repeat((I1 + I0) / 2 + (I1 - I0) / 2 * x, spb)


def tj_for(I0, I1, Ta=25.0):
    """Junction temperature for a balanced pattern between I0 and I1 (thermal time constants >> a bit)."""
    T = Ta
    for _ in range(200):
        P0, P1 = (max(0.0, slope(T) * (i - ith(T))) for i in (I0, I1))
        T = 0.5 * T + 0.5 * (Ta + ZTH * (0.5 * (I0 * volt(I0) + I1 * volt(I1)) - 0.5 * (P0 + P1)))
    return T


def simulate(W, T, dt):
    """Rate equations behind the parasitic network. W: (cases, samples) drive current over one pattern period;
    T: junction temperature per case. Returns output power (W) and chirp (Hz) over the second period."""
    T = np.asarray(T, float); VT = NID * kB * (T + 273.15); f = detune(T); Ntr = ntr(T); eta = etai(T)
    Is = 6e-3 / np.exp(1.45 / VT)
    nc, ns = W.shape; I0 = W[:, 0]
    vj = VT * np.log(I0 / Is + 1); vp = vj + RM * I0
    N = nth(T) * 0.98; S = np.full(nc, 1e13)

    def der(vp, vj, N, S, Id):
        ib = (vp - vj) / RM; iD = Is * (np.exp(vj / VT) - 1)
        gs = G0 * f * np.log(N / Ntr) / (1 + EPS * S)
        return ((Id - ib) / CP, (ib - iD) / CJ, eta * iD / (q * VACT) - rrec(N) - VG * gs * S,
                GAM * VG * gs * S - S / TP + GAM * BETA * B_ * N ** 2)
    for _ in range(int(3e-9 / dt)):                     # settle at the first level
        k = der(vp, vj, N, S, I0)
        vp, vj, N, S = (x + dt * dx for x, dx in zip((vp, vj, N, S), k)); S = np.maximum(S, 1.0)
    P = np.zeros((nc, ns)); chirp = np.zeros((nc, ns))
    for per in range(2):
        for i in range(ns):
            Id = W[:, i]; st = (vp, vj, N, S)
            k1 = der(*st, Id)
            k2 = der(*(x + dt / 2 * d for x, d in zip(st, k1)), Id)
            k3 = der(*(x + dt / 2 * d for x, d in zip(st, k2)), Id)
            k4 = der(*(x + dt * d for x, d in zip(st, k3)), Id)
            vp, vj, N, S = (x + dt / 6 * (a + 2 * b + 2 * cc + d) for x, a, b, cc, d in zip(st, k1, k2, k3, k4))
            S = np.maximum(S, 1.0)
            if per == 1:
                P[:, i] = S * VACT / GAM * HV_Q * q * VG * AMT
                chirp[:, i] = ALPHA / (4 * np.pi) * (GAM * VG * G0 * f * np.log(N / Ntr) - 1 / TP)
    return P, chirp


def bessel4(x, dt, f3):
    n = x.shape[-1]; s = 1j * np.fft.rfftfreq(n, dt) / f3 * 2.1139
    H = 105 / (s ** 4 + 10 * s ** 3 + 45 * s ** 2 + 105 * s + 105)
    return np.fft.irfft(np.fft.rfft(x, axis=-1) * H, n=n, axis=-1)


def eye_height(P, spb):
    """Inner eye height at the best sampling instant (the delay search covers the laser and filter latency)."""
    n = len(BITS); best = (-1e9, 0); one = BITS == 1
    for tau in range(0, 3 * spb, max(1, spb // 40)):
        v = P[(np.arange(n) * spb + tau) % (n * spb)]
        h = v[one].min() - v[~one].max()
        if h > best[0]: best = (h, tau)
    return best


BR, DT = 25e9, 0.2e-12
SPB = int(round(1 / BR / DT))


# ============================================================== numbers
def numbers():
    print("== VCSEL design")
    print(f"mirrors: top {NTOP} pairs R = {R_TOP:.5f} (T = {100*(1-R_TOP):.3f} %), bottom {NBOT} pairs R = {R_BOT:.6f}")
    print(f"penetration depths {LPEN_T:.3f}, {LPEN_B:.3f} um; cavity {LCAV:.3f} um; Leff = {LEFF*1e4:.3f} um")
    print(f"alpha_m = {AM:.1f} /cm (top {AMT:.1f}); Gamma = {GAM:.4f}; tau_p = {TP*1e12:.2f} ps; g_th = {GTH:.0f} /cm")
    print(f"round-trip gain in the VCSEL = {100*(np.exp(2*(AI+AM)*LEFF)-1):.2f} %;"
          f" FP round trip x{np.exp(2*(FP['ai']+np.log(1/FP['R']**2)/(2*FP['L']))*FP['L']):.1f}")
    print(f"active volume {VACT:.3g} cm3 (FP {FP['L']*FP['w']*FP['d']:.3g}, ratio {FP['L']*FP['w']*FP['d']/VACT:.0f})")
    print(f"mode spacing lambda^2/(2 ng Leff) = {LAM**2/(2*NG*LEFF*1e4)*1e3:.0f} nm")
    for T in (25, 45, 76, 85):
        print(f"T = {T} C: detune {detune(T):.3f}, Nth {nth(T):.3g}, Ith {ith(T)*1e3:.3f} mA, slope {slope(T):.3f} W/A,"
              f" J_th {ith(T)/(np.pi*(DIA/2)**2)/1e3:.2f} kA/cm2, tau_n = Nth/R = {nth(T)/rrec(nth(T))*1e9:.2f} ns")
    Ts = np.arange(0, 101); I_T = np.array([ith(T) for T in Ts])
    print(f"threshold minimum {I_T.min()*1e3:.3f} mA at {Ts[I_T.argmin()]} C; Ith(85)/Ith(25) = {ith(85)/ith(25):.2f}"
          f" (FP: {np.exp(60/FP['T0']):.2f}); slope(85)/slope(25) = {slope(85)/slope(25):.3f}")
    for Ta in (25, 55, 85):
        Is = np.linspace(0, 20e-3, 2001); r = np.array([li(i, Ta) for i in Is]); j = r[:, 0].argmax()
        print(f"Ta = {Ta} C: roll-over {r[j,0]*1e3:.2f} mW at {Is[j]*1e3:.1f} mA (junction {r[j,1]:.0f} C);"
              f" at 5 mA {li(5e-3,Ta)[0]*1e3:.2f} mW, junction {li(5e-3,Ta)[1]:.0f} C")
    P5, T5 = li(5e-3, 25)
    print(f"at 5 mA, 25 C: V = {volt(5e-3):.2f} V, Pel = {5e-3*volt(5e-3)*1e3:.2f} mW, Pout {P5*1e3:.2f} mW,"
          f" wall-plug {P5/(5e-3*volt(5e-3))*100:.0f} %")
    print("== small signal (Ta = 25 C)")
    for I in (1e-3, 2e-3, 4e-3, 8e-3):
        o = vcsel_ss(I)
        print(f"I = {I*1e3:.0f} mA: fr {o['fr']/1e9:.1f} GHz, damping ratio {o['gam']/(2*np.sqrt(o['wr2'])):.2f},"
              f" f3dB intrinsic {f3db(o, False)/1e9:.1f} GHz, with parasitics {f3db(o)/1e9:.1f} GHz, Rj {o['Rj']:.1f} ohm, Tj {o['T']:.0f} C")
    o = vcsel_ss(4e-3)
    D = o["fr"] / np.sqrt((4e-3 - ith(o["T"])) * 1e3)
    print(f"VCSEL D = fr/sqrt(I-Ith) = {D/1e9:.2f} GHz/sqrt(mA) at 4 mA; K = {o['K']*1e9:.3f} ns,"
          f" bandwidth limit 2 pi sqrt2/K = {TWO_PI*np.sqrt(2)/o['K']/1e9:.0f} GHz")
    f50 = fp_op(50e-3)
    print(f"FP: Ith {f50['Ith']*1e3:.2f} mA, fr(50 mA) {f50['fr']/1e9:.2f} GHz,"
          f" D = {f50['fr']/np.sqrt((50e-3-f50['Ith'])*1e3)/1e9:.2f} GHz/sqrt(mA), slope/facet {f50['slope']:.3f} W/A")
    print("== extinction ratio")
    for erdb in (3, 6, 9):
        er = 10 ** (erdb / 10); print(f"ER {erdb} dB: OMA/Pavg = {2*(er-1)/(er+1):.2f}, penalty {10*np.log10((er+1)/(er-1)):.2f} dB")
    print("== temperature compensation")
    fp25, fp85 = fp_op(0), None
    Ith25 = fp25["Ith"]; Ith85 = Ith25 * np.exp(60 / FP["T0"]); s = fp25["slope"]
    P0, P1 = 1e-3, 5e-3
    i0, i1 = Ith25 + P0 / s, Ith25 + P1 / s; j0, j1 = Ith85 + P0 / s, Ith85 + P1 / s
    print(f"FP, P0/P1 = 1/5 mW per facet: 25 C I0 {i0*1e3:.1f} I1 {i1*1e3:.1f} (Imod {(i1-i0)*1e3:.1f}) mA;"
          f" 85 C I0 {j0*1e3:.1f} I1 {j1*1e3:.1f} mA; Ith {Ith25*1e3:.1f} -> {Ith85*1e3:.1f} mA")
    P0, P1 = 0.8e-3, 3.2e-3
    res = {}
    for Ta in (25.0, 85.0):
        T = Ta
        for _ in range(200):
            I0, I1 = ith(T) + P0 / slope(T), ith(T) + P1 / slope(T)
            T = 0.5 * T + 0.5 * (Ta + ZTH * (0.5 * (I0 * volt(I0) + I1 * volt(I1)) - 0.5 * (P0 + P1)))
        res[Ta] = (I0, I1, T)
        print(f"VCSEL, P0/P1 = 0.8/3.2 mW, Ta {Ta:.0f} C: I0 {I0*1e3:.2f} I1 {I1*1e3:.2f} mA, Imod {(I1-I0)*1e3:.2f} mA,"
              f" Iavg {(I0+I1)/2*1e3:.2f} mA, junction {T:.0f} C, Ith {ith(T)*1e3:.3f} mA, slope {slope(T):.3f} W/A")
    I0, I1, _ = res[25.0]; Imod = I1 - I0
    T = 85.0                                            # APC holds the average power, Imod left at its 25 C value
    for _ in range(200):
        Imid = ith(T) + 2e-3 / slope(T); a0, a1 = Imid - Imod / 2, Imid + Imod / 2
        T = 0.5 * T + 0.5 * (85 + ZTH * (0.5 * (a0 * volt(a0) + a1 * volt(a1)) - 2e-3))
    p0, p1 = slope(T) * (a0 - ith(T)), slope(T) * (a1 - ith(T))
    print(f"  85 C with APC only: P0 {p0*1e3:.2f} P1 {p1*1e3:.2f} mW, ER {10*np.log10(p1/p0):.2f} dB (target 6.02 dB)")


# ============================================================== Figure 24.6: VCSEL cross-section and standing wave
def field_profile(lam):
    """|E|^2 along the axis for light from the top (air), via characteristic matrices from the substrate up."""
    stack = list(reversed(TOP)) + [(NC, LCAV)] + BOT        # top (air side) to bottom
    E, H = 1.0 + 0j, NSUB + 0j                              # transmitted wave in the substrate
    zs, Es, ns = [], [], []
    z = 0.0
    for n, d in reversed(stack):                           # walk upwards
        for s in np.linspace(0, d, 12, endpoint=False):
            M = layer_matrix(n, s, lam); e, _ = M @ np.array([E, H])
            zs.append(z + s); Es.append(abs(e) ** 2); ns.append(n)
        M = layer_matrix(n, d, lam); E, H = M @ np.array([E, H]); z += d
    return np.array(zs), np.array(Es), np.array(ns), z


def fig_vcsel():
    fig = plt.figure(figsize=(6.3, 3.3))
    ax = fig.add_axes([0.0, 0.02, 0.52, 0.93]); ax.set_axis_off(); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    # substrate and bottom contact
    ax.add_patch(Rectangle((0.6, 0.35), 8.8, 0.25, color=AMBER, lw=0))
    ax.add_patch(Rectangle((0.6, 0.6), 8.8, 1.0, color="#E3E7EE", lw=0))
    ax.text(5, 1.1, "n-GaAs substrate", ha="center", va="center", fontsize=7, color=INK)
    ax.text(9.5, 0.47, "n contact", ha="left", va="center", fontsize=6.5, color=INK)
    y = 1.6
    for k in range(13):                                       # n-DBR (not all 34 pairs drawn)
        ax.add_patch(Rectangle((0.6, y), 8.8, 0.13, color="#B8C9E8", lw=0)); y += 0.13
        ax.add_patch(Rectangle((0.6, y), 8.8, 0.13, color="#EEF2FA", lw=0)); y += 0.13
    ax.text(0.45, 3.3, "n-DBR\n34 pairs", ha="right", va="center", fontsize=6.8, color=INK)
    # mesa: cavity, oxide layer, p-DBR
    x0, x1 = 2.2, 7.8
    ax.add_patch(Rectangle((x0, y), x1 - x0, 0.55, color="#F4E6CC", lw=0))
    for k in range(3):
        ax.plot([x0, x1], [y + 0.18 + 0.09 * k] * 2, color=RED, lw=1.2)
    ax.text(0.45, y + 0.27, "cavity, 3 QWs", ha="right", va="center", fontsize=6.8, color=INK)
    y += 0.55
    yo = y
    for k in range(10):                                       # p-DBR
        ax.add_patch(Rectangle((x0, y), x1 - x0, 0.13, color="#B8C9E8", lw=0)); y += 0.13
        ax.add_patch(Rectangle((x0, y), x1 - x0, 0.13, color="#EEF2FA", lw=0)); y += 0.13
    ax.text(0.45, yo + 1.3, "p-DBR\n20 pairs", ha="right", va="center", fontsize=6.8, color=INK)
    ax.add_patch(Rectangle((x0, yo + 0.13), 1.95, 0.13, color=MUTED, lw=0))      # oxidised Al0.98GaAs
    ax.add_patch(Rectangle((x1 - 1.95, yo + 0.13), 1.95, 0.13, color=MUTED, lw=0))
    ax.annotate("oxide aperture", xy=(x1 - 1.0, yo + 0.2), xytext=(8.3, yo + 0.95), fontsize=6.8, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.annotate("", xy=(x0 + 1.95, yo + 0.5), xytext=(x1 - 1.95, yo + 0.5),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(5, yo + 0.75, "6 µm", ha="center", va="center", fontsize=6.5, color=INK,
            bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))
    # top ring contact and the beam
    ax.add_patch(Rectangle((x0, y), 1.6, 0.22, color=AMBER, lw=0)); ax.add_patch(Rectangle((x1 - 1.6, y), 1.6, 0.22, color=AMBER, lw=0))
    ax.text(x1 + 0.1, y + 0.11, "p contact (ring)", ha="left", va="center", fontsize=6.5, color=INK)
    ax.add_patch(FancyArrowPatch((5, y + 0.3), (5, 9.7), arrowstyle="-|>", mutation_scale=11, color=RED, lw=1.6))
    ax.text(5.25, 9.2, "850 nm light,\nround beam", ha="left", va="center", fontsize=6.8, color=INK)
    for sgn in (-1, 1):                                       # current funnelled through the aperture
        xs = 5 + sgn * np.array([2.0, 1.95, 1.4, 0.75, 0.55])
        ys = np.array([y - 0.05, yo + 1.4, yo + 0.6, yo + 0.25, yo - 0.25])
        ax.plot(xs, ys, color=TEAL, lw=0.9, ls=(0, (3, 2)))
    ax.text(x0 - 0.1, y - 0.35, "current", ha="right", va="center", fontsize=6.5, color=TEAL)
    ax.text(-1.6, 9.75, "a", fontweight="bold", fontsize=9.5, color=INK, va="top")
    ax.text(9.9, 0.05, "not to scale", ha="right", va="bottom", fontsize=6, color=MUTED, style="italic")
    # standing wave
    b = fig.add_axes([0.66, 0.15, 0.32, 0.78])
    lams = np.linspace(0.845, 0.855, 801)
    # resonance: the wavelength that maximises the field at the cavity centre
    def centre_field(l):
        z, E, n, ztot = field_profile(l); zmid = (sum(d for _, d in BOT) + LCAV / 2)
        return E[np.argmin(abs(z - zmid))]
    fc = np.array([centre_field(l) for l in lams]); lres = lams[fc.argmax()]
    z, E, n, ztot = field_profile(lres)
    zb = sum(d for _, d in BOT)
    zz = -zb                                              # shade the high-index layers and the cavity
    for nn, d in list(reversed(BOT)) + [(NC, LCAV)] + TOP:
        if nn == NH: b.axhspan(zz, zz + d, color="#DCE4F3", lw=0)
        if nn == NC: b.axhspan(zz, zz + d, color="#F4E6CC", lw=0)
        zz += d
    b.plot(E / E.max(), z - zb, color=C1, lw=1.0)
    b.set_ylim(-1.6, LCAV + 1.6); b.set_xlim(0, 1.3); b.set_xticks([0, 0.5, 1])
    b.axhline(LCAV / 2, color=RED, lw=0.6, ls=":")
    b.text(1.28, LCAV / 2, "QWs", ha="right", va="center", fontsize=6.5, color=RED)
    b.text(1.28, LCAV + 1.5, "p-DBR", ha="right", va="top", fontsize=6.5, color=INK)
    b.text(1.28, -1.5, "n-DBR", ha="right", va="bottom", fontsize=6.5, color=INK)
    finish(b, "Optical intensity |E|² (norm.)", "Height above the cavity's base (µm)")
    b.grid(False)
    tag(b, "b")
    savefig(fig, "ch24_vcsel")
    print(f"resonance at {lres*1e3:.2f} nm; intensity in the mirrors falls to 1/e of the cavity peak within"
          f" ~{LPEN_T:.2f} um (phase penetration depth)")


# ============================================================== Figure 24.7: VCSEL L-I and threshold vs temperature
def fig_vcsel_li():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.25, 1]))
    Is = np.linspace(0, 18e-3, 721)
    for Ta, col in ((25, C1), (55, C2), (85, C4)):
        P = np.array([li(i, Ta)[0] for i in Is]) * 1e3; j = P.argmax()
        a.plot(Is * 1e3, P, color=col, label=f"{Ta} °C")
        a.plot(Is[j] * 1e3, P[j], "o", color=col, ms=3.5)
    a.set_xlim(0, 18); a.set_ylim(0, 7.2)
    a.text(14.3, 6.75, "roll-over", fontsize=7, color=INK, ha="center")
    finish(a, "Current (mA)", "Output power (mW)", legend=True, loc="upper left")
    tag(a, "a")
    Ts = np.linspace(0, 100, 201)
    b.plot(Ts, [ith(T) / ith(25) for T in Ts], color=C1, label="VCSEL (gain–cavity detuning)")
    b.plot(Ts, np.exp((Ts - 25) / FP["T0"]), color=C2, label="Ch 24 FP laser, T$_0$ = 60 K")
    b.axvline(25 + (850 - LP25) / (DLP - DLC), ymax=0.78, color=MUTED, lw=0.6, ls=":")      # stops below the legend
    b.text(25 + (850 - LP25) / (DLP - DLC) + 1.5, 0.3, "gain peak on\ncavity mode", fontsize=6.5, color=MUTED, ha="left")
    b.set_xlim(0, 100); b.set_ylim(0, 3.5)
    finish(b, "Junction temperature (°C)", "Threshold / threshold at 25 °C", legend=True, loc="upper left")
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    savefig(fig, "ch24_vcsel_li")


# ============================================================== Figure 25.1: bias-dependent bandwidth
def fig_bw():
    fig, (a, b, cax) = plt.subplots(1, 3, figsize=(6.6, 2.6))
    f = np.linspace(0.05e9, 40e9, 800)
    for I, col in zip((1e-3, 2e-3, 4e-3, 8e-3), (C5, C3, C2, C1)):
        o = vcsel_ss(I)
        r = 20 * np.log10(np.abs(vcsel_H(f, o)))
        a.plot(f / 1e9, r, color=col, label=f"{I*1e3:.0f} mA")
        print(f"response at {I*1e3:.0f} mA peaks {r.max():.1f} dB at {f[r.argmax()]/1e9:.1f} GHz")
    a.axhline(-3, color=MUTED, lw=0.6, ls=":")
    a.set_xlim(0, 40); a.set_ylim(-20, 15)
    finish(a, "Frequency (GHz)", "Response (dB)", legend=True, loc="upper right")
    tag(a, "a")
    Iv = np.linspace(0.3e-3, 16e-3, 300)
    xv, yv = [], []
    for I in Iv:
        o = vcsel_ss(I)
        if o["P"] > 0: xv.append(np.sqrt((I - ith(o["T"])) * 1e3)); yv.append(o["fr"] / 1e9)
    b.plot(xv, yv, color=C1, label="VCSEL (with self-heating)")
    j = int(np.argmax(yv)); print(f"VCSEL fr peaks at {yv[j]:.1f} GHz, sqrt(I-Ith) = {xv[j]:.2f}, I = {Iv[[k for k in range(len(Iv)) if vcsel_ss(Iv[k])['P'] > 0][j]]*1e3:.1f} mA")
    Ith_fp = fp_op(0)["Ith"]; If = np.linspace(Ith_fp * 1.001, 120e-3, 300)
    b.plot(np.sqrt((If - Ith_fp) * 1e3), [fp_op(i)["fr"] / 1e9 for i in If], color=C2, label="Ch 24 FP laser")
    b.set_xlim(0, 10); b.set_ylim(0, 25)
    finish(b, r"√(I − I$_\mathrm{th}$)  (√mA)", "Relaxation frequency $f_r$ (GHz)", legend=True, loc="upper right")
    tag(b, "b")
    # extraction of the K-factor: damping rate against fr^2 over the biases a datasheet would use (1-8 mA)
    Ik = np.linspace(1e-3, 8e-3, 15); pts = [vcsel_ss(I) for I in Ik]
    x = np.array([o["fr"] ** 2 for o in pts]) / 1e18; yk = np.array([o["gam"] for o in pts]) / 1e9
    K, g0 = np.polyfit(x, yk, 1)
    cax.plot(x, yk, "o", color=C1, ms=3)
    xx = np.linspace(0, x.max() * 1.05, 50); cax.plot(xx, K * xx + g0, color=MUTED, lw=0.9, ls="--")
    cax.text(0.05, 0.95, f"slope K = {K:.2f} ns\nintercept γ$_0$ = {g0:.1f} ns$^{{-1}}$", transform=cax.transAxes,
             fontsize=6.6, color=INK, va="top")
    cax.set_xlim(0, x.max() * 1.05); cax.set_ylim(0, None)
    finish(cax, "$f_r^2$ (GHz$^2$)", "Damping rate γ (ns$^{-1}$)")
    tag(cax, "c")
    print(f"K-factor fit over 1-8 mA: K = {K:.3f} ns, gamma0 = {g0:.2f} /ns, cap 2 pi sqrt2/K = {TWO_PI*np.sqrt(2)/K:.1f} GHz")
    fig.tight_layout(w_pad=1.4)
    savefig(fig, "ch25_bw")


# ============================================================== Figure 25.6: choosing the zero level
def fig_zerolevel():
    I1 = 8e-3; I0s = np.arange(0, 5.01e-3, 0.25e-3)
    W = np.array([drive(i0, I1, SPB) for i0 in I0s]); Tj = np.array([tj_for(i0, I1) for i0 in I0s])
    P, ch = simulate(W, Tj, DT); Pf = bessel4(P, DT, 0.75 * BR)
    eye = np.array([eye_height(p, SPB)[0] for p in Pf])
    P0 = np.array([max(slope(T) * (i0 - ith(T)), 0) for i0, T in zip(I0s, Tj)])
    P1 = np.array([slope(T) * (I1 - ith(T)) for T in Tj])
    with np.errstate(divide="ignore"):
        ER = 10 * np.log10(P1 / P0)
    cpp = (ch.max(axis=1) - ch.min(axis=1)) / 1e9
    print("== zero level sweep, 25 Gb/s, I1 = 8 mA")
    for i in range(len(I0s)):
        print(f"I0 {I0s[i]*1e3:.2f} mA: Tj {Tj[i]:.0f} C, OMA {(P1[i]-P0[i])*1e3:.2f} mW, eye {eye[i]*1e3:.2f} mW,"
              f" ER {ER[i]:.1f} dB, chirp p-p {cpp[i]:.0f} GHz")
    ithv = ith(Tj[0])
    fig, axs = plt.subplots(1, 3, figsize=FULL)
    a, b, cax = axs
    a.plot(I0s * 1e3, (P1 - P0) * 1e3, color=MUTED, ls="--", label="OMA (steady levels)")
    a.plot(I0s * 1e3, eye * 1e3, color=C1, marker="o", ms=2.5, label="eye height")
    a.axhline(0, color=INK, lw=0.6); a.set_ylim(-3, 4.8)
    finish(a, "Zero-level current I$_0$ (mA)", "Power (mW)", legend=True, loc="lower right")
    b.plot(I0s[1:] * 1e3, ER[1:], color=C2, marker="o", ms=2.5); b.set_ylim(0, 25)
    finish(b, "Zero-level current I$_0$ (mA)", "Extinction ratio (dB)")
    cax.plot(I0s * 1e3, cpp, color=C4, marker="o", ms=2.5); cax.set_ylim(0, 180)
    finish(cax, "Zero-level current I$_0$ (mA)", "Peak-to-peak chirp (GHz)")
    for ax, t in zip(axs, "abc"):
        ax.axvline(ithv * 1e3, color=MUTED, lw=0.6, ls=":"); ax.set_xlim(0, 5); tag(ax, t)
    a.text(ithv * 1e3 + 0.12, 4.3, r"I$_\mathrm{th}$", fontsize=6.5, color=MUTED)      # above the OMA line, clear of the legend
    fig.tight_layout(w_pad=1.6)
    savefig(fig, "ch25_zerolevel")


# ============================================================== Figure 25.7: eyes with and without equalisation
TAPS = (-0.1, 0.9, 0.1, 0.1)       # pre-cursor, main, two post-cursors: best of a grid search (step 0.05) on this model


def fig_eyes():
    cases = [(2e-3, 8e-3, (1.0,), 0, "5 mA average, no equalisation"),
             (1e-3, 5e-3, (1.0,), 0, "3 mA average, no equalisation"),
             (1e-3, 5e-3, TAPS, 1, "3 mA average, 4-tap FIR")]
    W = np.array([drive(i0, i1, SPB, t, p) for i0, i1, t, p, _ in cases])
    Tj = np.array([tj_for(i0, i1) for i0, i1, *_ in cases])
    P, ch = simulate(W, Tj, DT); Pf = bessel4(P, DT, 0.75 * BR)
    print("== eyes, 25 Gb/s")
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.5), sharey=True)
    t = np.arange(2 * SPB + 1) / SPB - 1
    for k, (ax, p, cs) in enumerate(zip(axs, Pf, cases)):
        h, tau = eye_height(p, SPB)
        oma = slope(Tj[k]) * (cs[1] - cs[0])
        print(f"{cs[4]}: Tj {Tj[k]:.0f} C, eye {h*1e3:.2f} mW of OMA {oma*1e3:.2f} mW ({100*h/oma:.0f} %),"
              f" current {W[k].min()*1e3:.2f}-{W[k].max()*1e3:.2f} mA, chirp p-p {(ch[k].max()-ch[k].min())/1e9:.0f} GHz")
        n = len(BITS) * SPB; segs = []
        for kb in range(len(BITS)):
            idx = (kb * SPB + tau - SPB + np.arange(2 * SPB + 1)) % n
            segs.append(np.column_stack([t, p[idx] * 1e3]))
        ax.add_collection(LineCollection(segs, colors=C1, linewidths=0.5, alpha=0.18, rasterized=True))
        v = p[(np.arange(len(BITS)) * SPB + tau) % n]
        lo1, hi0 = v[BITS == 1].min() * 1e3, v[BITS == 0].max() * 1e3
        if h > 0:
            ax.annotate("", xy=(0, lo1), xytext=(0, hi0), arrowprops=dict(arrowstyle="<->", color=C4, lw=1.1, shrinkA=0, shrinkB=0))
        ax.set_xlim(-1, 1); ax.set_ylim(0, 6.5)
        ax.set_title(cs[4], fontsize=7.6, loc="left", color=INK)
        ax.text(0.04, 0.95, f"eye {h*1e3:.2f} mW\n= {100*h/oma:.0f} % of OMA", transform=ax.transAxes, fontsize=6.6, color=INK, va="top")
        ax.set_xticks([-1, -0.5, 0, 0.5, 1]); ax.set_xticklabels(["−1", "", "0", "", "1"])
        ax.set_xlabel("Time (UI)")
    axs[0].set_ylabel("Optical power (mW)")
    fig.tight_layout(w_pad=1.0)
    plt.rcParams["savefig.dpi"] = 150
    savefig(fig, "ch25_eyes")
    plt.rcParams["savefig.dpi"] = "figure"
    # the FIR's own response and the zero level's relaxation frequency
    for fq in (0, BR / 8, BR / 4, BR / 2):
        z = np.exp(1j * TWO_PI * fq / BR)
        Cf = sum(cj * z ** (-(j - 1)) for j, cj in enumerate(TAPS))
        print(f"FIR |C| at {fq/1e9:.2f} GHz = {abs(Cf):.2f}")
    o = vcsel_ss(1e-3, 25)
    print(f"zero level (1 mA) relaxation frequency {o['fr']/1e9:.1f} GHz (Ta 25 C CW)")


def drive_asym(I0, I1, spb, a_rise, a_fall):
    """Two edge taps: the first bit after a rising edge gets +a_rise*dI, the first bit after a falling edge -a_fall*dI."""
    b, prev = BITS, np.roll(BITS, 1); dI = I1 - I0
    I = np.where(b == 1, I1, I0).astype(float)
    I += np.where((b == 1) & (prev == 0), a_rise * dI, 0.0)
    I -= np.where((b == 0) & (prev == 1), a_fall * dI, 0.0)
    return np.repeat(I, spb)


def more_numbers():
    print("== driving numbers")
    T = tj_for(0.0, 8e-3); N = nth(T); tn = N / rrec(N)
    for i0 in (0.0, 0.1e-3):
        print(f"turn-on delay I0 = {i0*1e3:.1f} mA -> I1 = 8 mA: tau_n {tn*1e9:.2f} ns, Ith {ith(T)*1e3:.3f} mA,"
              f" t_d = {tn*np.log((8e-3-i0)/(8e-3-ith(T)))*1e12:.0f} ps")
    I0, I1 = 2e-3, 8e-3; T = tj_for(I0, I1); P0, P1 = (slope(T) * (i - ith(T)) for i in (I0, I1)); er = P1 / P0
    print(f"WE: I0 2, I1 8 mA, Tj {T:.0f} C: P0 {P0*1e3:.2f} P1 {P1*1e3:.2f} mW, ER {er:.2f} = {10*np.log10(er):.2f} dB,"
          f" OMA {(P1-P0)*1e3:.2f}, Pavg {(P0+P1)/2*1e3:.2f} mW, penalty {10*np.log10((er+1)/(er-1)):.2f} dB,"
          f" electrical {0.5*(I0*volt(I0)+I1*volt(I1))*1e3:.2f} mW, V(8 mA) {volt(8e-3):.2f} V,"
          f" chirp 69 GHz = {(LAM*1e-6)**2*69e9/3e8*1e9:.3f} nm")
    o = vcsel_ss(8e-3)
    print(f"8 mA: diff. resistance RS = {RS:.0f} ohm; a 50 ohm back termination passes {50/(50+RS)*100:.0f} % of the"
          f" modulation current to the laser -> {6/(50/(50+RS)):.1f} mA switched for 6 mA")
    # asymmetric two-tap FFE and the 40 Gb/s case
    W = np.array([drive(1e-3, 5e-3, SPB), drive_asym(1e-3, 5e-3, SPB, 0.0, -0.3)])
    Tj = tj_for(1e-3, 5e-3); P, _ = simulate(W, np.full(2, Tj), DT); Pf = bessel4(P, DT, 0.75 * BR)
    oma = slope(Tj) * 4e-3
    for lab, p in zip(("no EQ", "fall tap -0.3 (softer falling edge)"), Pf):
        h = eye_height(p, SPB)[0]; print(f"25 Gb/s 1/5 mA, {lab}: eye {h*1e3:.2f} mW ({100*h/oma:.0f} % of OMA)")
    spb40 = int(round(1 / 40e9 / DT))
    W = np.array([drive(2e-3, 8e-3, spb40), drive(2e-3, 8e-3, spb40, (-0.1, 1.1, -0.1, 0.1), 1)])
    Tj = tj_for(2e-3, 8e-3); P, _ = simulate(W, np.full(2, Tj), DT); Pf = bessel4(P, DT, 0.75 * 40e9)
    oma = slope(Tj) * 6e-3
    for lab, p in zip(("no EQ", "taps (-0.1, 1.1, -0.1, 0.1)"), Pf):
        h = eye_height(p, spb40)[0]; print(f"40 Gb/s 2/8 mA, {lab}: eye {h*1e3:.2f} mW ({100*h/oma:.0f} % of OMA)")
    print("== microring laser (Ch 27)")
    for D in (40.0,):
        ng, lam = 3.7, 1.31
        print(f"ring {D:.0f} um, ng {ng}: FSR {lam**2/(ng*np.pi*D)*1e3:.2f} nm; a 0.1 % larger ring moves a mode by"
              f" {lam*1e3*1e-3:.2f} nm; with dn_eff/dT = 2e-4 /K the modes drift {lam*1e3*2e-4/ng:.3f} nm/K")


if __name__ == "__main__":
    numbers()
    more_numbers()
    fig_vcsel()
    fig_vcsel_li()
    fig_bw()
    fig_zerolevel()
    fig_eyes()
