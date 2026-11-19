"""Figures and numbers for Section 25.10 (laser transmitters compared: VCSELs, DMLs and EMLs).

Run from the repository root:  python -I -X utf8 figsrc/ch25_tx.py
NumPy and matplotlib only; about a minute. Prints every number the section quotes, then writes
assets/figs/ch25_tx_devices.svg, ch25_tx_dispersion.svg, ch25_tx_energy.svg and ch25_tx_map.svg.

Models (all illustrative: typical in size, not the numbers of any product):
  * DML: a 150 um single-mode DFB laser built for direct modulation, simulated with the single-mode rate equations
    and the chirp formula of Sections 24.3 and 25.2 (the same equations as figsrc/ch25_figs.py): six 6 nm strained
    quantum wells, a logarithmic gain with g0 = 2400 /cm, gain compression 2e-17 cm^3 and alpha = 3. The grating
    and the HR-coated rear facet are lumped into an effective mirror loss of 35 /cm, 70 % of which leaves through
    the front facet. Forward voltage V = 0.9 V + 5 ohm x I.
  * EAM (the modulator of an EML): the logarithm of its transmission follows the drive voltage (an absorption
    linear in voltage), between -3 dB ("1") and -13 dB ("0"), behind the RC pole of its capacitance; its phase
    follows the transmission as phi = (alpha_EAM / 2) ln T (Koyama and Iga), with a constant alpha_EAM.
  * Fibre: standard single-mode fibre as an all-pass filter exp(-j beta2 w^2 L / 2) on the optical field (the sign
    convention is checked against the textbook broadening of a chirped Gaussian pulse in numbers()).
  * Receiver: the fourth-order Bessel-Thomson reference receiver at 0.75 x the bit rate of figsrc/ch2x_lasers.py;
    the eye opening is the inner opening at the best sampling instant of a periodic PRBS7 pattern, and the
    dispersion penalty is 10 log10(eye back-to-back / eye after the fibre), the eye-closure (ISI) penalty of a
    thermal-noise-limited receiver (Chapter 38). It counts vertical closure only, not the loss of eye width.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch
import ch2x_lasers as VC                                   # the VCSEL of Section 24.8 and Worked Example 25.2

q, c = 1.602e-19, 3e10                                       # C, cm/s

# ============================================================== the DML
DML = dict(L=150e-4, w=1.5e-4, d=36e-7, Gam=0.07, eta=0.8, ai=12.0, am=35.0, F1=0.7, g0=2400.0, Ntr=1.8e18,
           eps=2e-17, A=1e8, B=1e-10, C=3e-29, ng=3.6, lam=1.31, alpha=3.0, beta=1e-4, V0=0.9, RS=5.0)
p = DML
VG = c / p["ng"]; VOL = p["L"] * p["w"] * p["d"]; TP = 1 / (VG * (p["ai"] + p["am"]))
GTH = (p["ai"] + p["am"]) / p["Gam"]; NTH = p["Ntr"] * np.exp(GTH / p["g0"])
HV = 1.2398 / p["lam"] * q
ADIFF = p["g0"] / NTH


def rrec(N): return p["A"] * N + p["B"] * N ** 2 + p["C"] * N ** 3


ITH = q * VOL / p["eta"] * rrec(NTH)
SLOPE = p["eta"] * p["am"] * p["F1"] / (p["ai"] + p["am"]) * 1.2398 / p["lam"]          # W/A, front facet
DFAC = np.sqrt(p["Gam"] * VG * ADIFF * p["eta"] / (q * VOL)) / (2 * np.pi)              # Hz/sqrt(A)
KFAC = 4 * np.pi ** 2 * (TP + p["eps"] / (VG * ADIFF))
I0D, I1D = 20e-3, 60e-3                                                                 # DML zero and one levels


def dml_volt(I): return p["V0"] + p["RS"] * I


def dml_op(I):
    S = p["Gam"] * TP * p["eta"] * (I - ITH) / (q * VOL)
    fr = np.sqrt(VG * ADIFF * S / (TP * (1 + p["eps"] * S))) / (2 * np.pi)
    return dict(S=S, fr=fr, P=SLOPE * (I - ITH), adiab=p["alpha"] / (4 * np.pi) * p["eps"] * S / TP)


# ============================================================== pattern, drive, simulations
def prbs7():
    s, out = [1] * 7, []
    for _ in range(127):
        out.append(s[6]); s = [s[6] ^ s[5]] + s[:6]
    return np.array(out)


BITS = prbs7()


def nrz(spb, rise):
    """Periodic NRZ pattern, 0..1, with raised-cosine edges `rise` samples long."""
    raw = np.repeat(BITS.astype(float), spb)
    k = max(int(rise), 2); ker = np.sin(np.linspace(0, np.pi, k)); ker /= ker.sum()
    kk = np.zeros(len(raw)); kk[:k] = ker; kk = np.roll(kk, -(k // 2))
    return np.real(np.fft.ifft(np.fft.fft(raw) * np.fft.fft(kk)))


def dml_sim(BR, dt, I0=I0D, I1=I1D):
    """Rate equations (RK4) for three pattern periods; returns front-facet power (W), chirp (Hz), field, samples/bit."""
    spb = int(round(1 / BR / dt)); Id = I0 + (I1 - I0) * nrz(spb, 0.3 * spb)
    g0, Ntr, G, eps, beta = p["g0"], p["Ntr"], p["Gam"], p["eps"], p["beta"]
    S = G * TP * p["eta"] * (Id[0] - ITH) / (q * VOL); N = NTH

    def der(N, S, I):
        g = g0 * np.log(N / Ntr) / (1 + eps * S)
        return p["eta"] * I / (q * VOL) - rrec(N) - VG * g * S, G * VG * g * S - S / TP + G * beta * p["B"] * N ** 2
    n = len(Id); Ns, Ss = np.empty(n), np.empty(n)
    for per in range(3):
        for i in range(n):
            I = Id[i]
            k1 = der(N, S, I); k2 = der(N + dt / 2 * k1[0], S + dt / 2 * k1[1], I)
            k3 = der(N + dt / 2 * k2[0], S + dt / 2 * k2[1], I); k4 = der(N + dt * k3[0], S + dt * k3[1], I)
            N += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); S += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            if per == 2: Ns[i], Ss[i] = N, S
    P = Ss * VOL / G * VG * p["am"] * p["F1"] * HV
    chirp = p["alpha"] / (4 * np.pi) * (G * VG * g0 * np.log(Ns / Ntr) - 1 / TP)     # index follows N (Section 25.2)
    phi = 2 * np.pi * np.cumsum(chirp - chirp.mean()) * dt                            # mean frequency = carrier offset
    return P, chirp, np.sqrt(P) * np.exp(1j * phi), spb


# the EAM: a 100 um x 2 um junction with a 0.3 um intrinsic region and a 40 fF pad
EAM = dict(L=100e-4, w=2e-4, di=0.3e-4, er=12.4, Cpad=40e-15, T1=-3.0, T0=-13.0, Vb1=0.5, Vb0=2.5)
EPS0 = 8.854e-14                                                                         # F/cm
CJ = EPS0 * EAM["er"] * EAM["L"] * EAM["w"] / EAM["di"]
CEAM = CJ + EAM["Cpad"]
FRC = {R: 1 / (2 * np.pi * R * CEAM) for R in (50.0, 25.0)}


def eam_sim(BR, dt, alpha, fRC=None):
    fRC = fRC or FRC[25.0]
    spb = int(round(1 / BR / dt)); u = nrz(spb, 0.3 * spb)
    f = np.fft.fftfreq(len(u), dt)
    u = np.real(np.fft.ifft(np.fft.fft(u) / (1 + 1j * f / fRC)))
    lnT = np.log(10) / 10 * (EAM["T0"] + (EAM["T1"] - EAM["T0"]) * u)
    P = np.exp(lnT)
    phi = alpha / 2 * lnT                                     # Delta nu = (alpha / 4 pi) d ln P / dt
    chirp = np.gradient(phi, dt) / (2 * np.pi)
    return P, chirp, np.sqrt(P) * np.exp(1j * phi), spb


def fibre(E, dt, DL, lam_um=1.55):
    """Accumulated dispersion DL (ps/nm) at wavelength lam_um: beta2 L = -DL lambda^2 / (2 pi c)."""
    b2L = -DL * 1e-3 * (lam_um * 1e-6) ** 2 / (2 * np.pi * 3e8)               # ps/nm = 1e-3 s/m
    w = 2 * np.pi * np.fft.fftfreq(len(E), dt)
    return np.fft.ifft(np.fft.fft(E) * np.exp(-1j * b2L * w ** 2 / 2))


def bessel4(x, dt, f3):
    s = 1j * np.fft.fftfreq(len(x), dt) / f3 * 2.1139
    H = 105 / (s ** 4 + 10 * s ** 3 + 45 * s ** 2 + 105 * s + 105)
    return np.real(np.fft.ifft(np.fft.fft(x) * H))


def eye(P, spb):
    n = len(BITS); best = (-1e9, 0); one = BITS == 1
    for tau in range(0, spb, max(1, spb // 60)):
        v = P[(np.arange(n) * spb + tau) % (n * spb)]
        h = v[one].min() - v[~one].max()
        if h > best[0]: best = (h, tau)
    return best


def penalties(E, spb, dt, BR, DLs, lam_um=1.55):
    rx = lambda x: bessel4(x, dt, 0.75 * BR)
    b2b = eye(rx(abs(E) ** 2), spb)[0]
    out = []
    for DL in DLs:
        h = eye(rx(abs(fibre(E, dt, DL, lam_um)) ** 2), spb)[0]
        out.append(10 * np.log10(b2b / h) if h > 0 else np.inf)
    return b2b, np.array(out)


def crossing(DLs, pen, thr=2.0):
    """First dispersion (along DLs) at which the penalty exceeds thr, by linear interpolation."""
    j = int(np.argmax(pen > thr))
    if pen[j] <= thr or j == 0: return np.nan
    a, b = pen[j - 1], min(pen[j], thr + 10)
    return DLs[j - 1] + (thr - a) * (DLs[j] - DLs[j - 1]) / (b - a)


def d_fibre(lam_nm, lam0_nm, S0=0.093):
    """G.652-type dispersion (ps/(nm km)) from the zero-dispersion wavelength and slope, as IEEE 802.3 and the
    CWDM4 MSA specify it: D = S0/4 lambda (1 - (lambda0/lambda)^4)."""
    return S0 / 4 * lam_nm * (1 - (lam0_nm / lam_nm) ** 4)


DT = 0.25e-12
CASES = [("DML (α = 3)", "dml", None, C2), ("EML, α$_\\mathrm{EAM}$ = +0.5", "eam", 0.5, C4),
         ("chirp-free (α = 0)", "eam", 0.0, INK), ("EML, α$_\\mathrm{EAM}$ = −0.5", "eam", -0.5, C1)]
RESULTS = {}


def run_sweeps():
    """Penalty against accumulated dispersion at 10 and 25 Gb/s (1550 nm) for the four transmitters."""
    for BR in (10e9, 25e9):
        DLs = np.arange(-600, 2001, 20.0) * (10e9 / BR) ** 2
        for name, kind, al, col in CASES:
            P, ch, E, spb = dml_sim(BR, DT) if kind == "dml" else eam_sim(BR, DT, al)
            b2b, pen = penalties(E, spb, DT, BR, DLs)
            RESULTS[(BR, name)] = dict(DL=DLs, pen=pen, b2b=b2b, P=P, chirp=ch, E=E, spb=spb)


# ============================================================== numbers
def numbers():
    print("== the DML")
    print(f"V = {VOL:.3g} cm3, tau_p {TP*1e12:.2f} ps, N_th {NTH:.3g} cm-3, a = g0/N_th {ADIFF:.3g} cm2, I_th {ITH*1e3:.2f} mA,"
          f" slope (front) {SLOPE:.3f} W/A")
    print(f"D = {DFAC/np.sqrt(1e3)/1e9:.2f} GHz/sqrt(mA) (Ch 24 laser 0.85, VCSEL 6.1), K = {KFAC*1e9:.3f} ns,"
          f" damping cap 2 pi sqrt2/K = {2*np.pi*np.sqrt(2)/KFAC/1e9:.0f} GHz")
    o0, o1 = dml_op(I0D), dml_op(I1D)
    print(f"levels {I0D*1e3:.0f}/{I1D*1e3:.0f} mA: P {o0['P']*1e3:.2f}/{o1['P']*1e3:.2f} mW (ER {10*np.log10(o1['P']/o0['P']):.2f} dB,"
          f" OMA {(o1['P']-o0['P'])*1e3:.2f} mW, average {(o0['P']+o1['P'])/2*1e3:.2f} mW),"
          f" f_r {o0['fr']/1e9:.1f}/{o1['fr']/1e9:.1f} GHz, eps S {p['eps']*o1['S']:.3f},"
          f" adiabatic chirp {o0['adiab']/1e9:.2f}/{o1['adiab']/1e9:.2f} GHz (difference {(o1['adiab']-o0['adiab'])/1e9:.2f} GHz"
          f" = {(o1['adiab']-o0['adiab'])*1.55e-6**2/3e8*1e12:.3f} pm at 1550 nm)")
    print("== the EAM")
    print(f"C_j = {CJ*1e15:.0f} fF, with pad {CEAM*1e15:.0f} fF; RC bandwidth {FRC[50.0]/1e9:.0f} GHz from 50 ohm,"
          f" {FRC[25.0]/1e9:.0f} GHz from 25 ohm (50 ohm source with a 50 ohm shunt termination)")
    vs, vh = 1e5, 5e4                                         # electron, hole drift velocities (m/s)
    print(f"transit time across {EAM['di']*1e4:.1f} um: electrons {EAM['di']*1e-2/vs*1e12:.1f} ps, holes {EAM['di']*1e-2/vh*1e12:.1f} ps;"
          f" transit-limited bandwidth ~0.44/t: {0.44/(EAM['di']*1e-2/vh)/1e9:.0f}-{0.44/(EAM['di']*1e-2/vs)/1e9:.0f} GHz")
    print("== fibre")
    for lam0 in (1300, 1324):
        print(f"lambda0 {lam0}: D(1310) {d_fibre(1310, lam0):+.2f}, D(1264.5) {d_fibre(1264.5, lam0):+.2f},"
              f" D(1337.5) {d_fibre(1337.5, lam0):+.2f}, D(1550) {d_fibre(1550, lam0):+.2f} ps/(nm km)")
    print(f"CWDM4 2 km limits: {2*d_fibre(1264.5,1324):.1f} to {2*d_fibre(1337.5,1300):.1f} ps/nm (MSA: -11.9 to 6.7)")
    print(f"beta2 at 1550 nm, 17 ps/(nm km): {-17e-6*1.55e-6**2/(2*np.pi*3e8)*1e27:.1f} ps^2/km")
    # check of the fibre sign convention: a chirped Gaussian pulse against the textbook result
    dt = 0.5e-12; t = (np.arange(4096) - 2048) * dt; T0 = 20e-12; b2L = -0.170 * 1.55e-6 ** 2 / (2 * np.pi * 3e8)
    for C in (-2, 0, 2):
        E = np.exp(-(1 + 1j * C) * t ** 2 / (2 * T0 ** 2)); Eo = fibre(E, dt, 170.0)
        w = lambda e: np.sqrt(np.sum(t ** 2 * abs(e) ** 2) / np.sum(abs(e) ** 2))
        CA = -C                                                # the same pulse in the e^{-jwt} convention
        an = np.sqrt((1 + CA * b2L / T0 ** 2) ** 2 + (b2L / T0 ** 2) ** 2)
        print(f"  check: chirped Gaussian C = {C:+d} over 170 ps/nm broadens {w(Eo)/w(E):.3f} x (analytic {an:.3f})")
    print("== dispersion penalties at 1550 nm (eye-closure penalty; reach = 1 dB)")
    for BR in (10e9, 25e9):
        for name, kind, al, col in CASES:
            r = RESULTS[(BR, name)]
            DL, pen = r["DL"], r["pen"]; pos = DL >= 0; neg = DL <= 0
            x2 = crossing(DL[pos], pen[pos], 2.0); x1 = crossing(DL[pos], pen[pos], 1.0)
            xn = crossing(-DL[neg][::-1], pen[neg][::-1], 2.0); xn1 = crossing(-DL[neg][::-1], pen[neg][::-1], 1.0)
            if kind == "dml":
                oma = dml_op(I1D)["P"] - dml_op(I0D)["P"]
            else:
                oma = 10 ** (EAM["T1"] / 10) - 10 ** (EAM["T0"] / 10)
            print(f"{BR/1e9:4.1f} Gb/s {name:28s}: 1 dB at {x1:6.0f} ps/nm = {x1/17:5.1f} km, 2 dB at {x2:6.0f} ps/nm = {x2/17:5.1f} km;"
                  f" normal side 1/2 dB at {-xn1:6.0f}/{-xn:6.0f} ps/nm; chirp p-p {(r['chirp'].max()-r['chirp'].min())/1e9:5.1f} GHz,"
                  f" b2b eye {100*r['b2b']/oma:.0f} % of OMA")
    for BR in (10e9, 25e9):
        a = RESULTS[(BR, CASES[2][0])]; m = a["DL"] >= 0
        print(f"chirp-free tolerance x (B/10G)^2: 1 dB {crossing(a['DL'][m], a['pen'][m], 1.0)*(BR/10e9)**2:.0f},"
              f" 2 dB {crossing(a['DL'][m], a['pen'][m])*(BR/10e9)**2:.0f} ps/nm (Chapter 2: 1000-1600 ps/nm at 10 Gb/s)")
    a = RESULTS[(25e9, CASES[2][0])]
    b2b, pen = penalties(a["E"], a["spb"], DT, 25e9, [34 * (50 / 25) ** 2])
    print(f"chirp-free, the reference link's 34 ps/nm at 50 Gb/s = 136 ps/nm at 25 Gb/s: penalty {pen[0]:.2f} dB")
    # the DML in the O band (25 Gb/s): the CWDM4 corners and 10 km
    r = RESULTS[(25e9, CASES[0][0])]
    pts = {"1310 nm, 10 km (lambda0 1324)": 10 * d_fibre(1310, 1324), "1310 nm, 10 km (lambda0 1300)": 10 * d_fibre(1310, 1300),
           "1264.5 nm, 2 km": 2 * d_fibre(1264.5, 1324), "1337.5 nm, 2 km": 2 * d_fibre(1337.5, 1300),
           "1264.5 nm, 10 km": 10 * d_fibre(1264.5, 1324), "1337.5 nm, 10 km": 10 * d_fibre(1337.5, 1300)}
    b2b, pen = penalties(r["E"], r["spb"], DT, 25e9, list(pts.values()), lam_um=1.31)
    for (k, v), x in zip(pts.items(), pen):
        print(f"25 Gb/s DML, O band, {k}: {v:+.1f} ps/nm -> penalty {x:.2f} dB")
    r = RESULTS[(10e9, CASES[0][0])]
    b2b, pen = penalties(r["E"], r["spb"], DT, 10e9, [10 * d_fibre(1310, 1324), 10 * d_fibre(1310, 1300)], lam_um=1.31)
    print(f"10 Gb/s DML at 1310 nm over 10 km: penalties {pen[0]:.2f} / {pen[1]:.2f} dB")
    print("== wavelength drift")
    print(f"uncooled DFB, 0.1 nm/K over 0-70 C: {0.1*70:.0f} nm (CWDM4 lane width 13 nm; LR4 LAN-WDM lane width"
          f" {1296.59-1294.53:.2f} nm -> {(1296.59-1294.53)/0.1:.0f} K)")
    print(f"EAM absorption edge 0.5 nm/K vs DFB 0.1 nm/K: detuning changes 0.4 nm/K, {0.4*70:.0f} nm over 70 K")


# ============================================================== energy per bit at 25 Gb/s
VDD, BR_E = 3.3, 25e9


def ioffe_cop(Tc, Th, ZT):
    """Maximum coefficient of performance of a thermoelectric cooler (Ioffe), temperatures in kelvin."""
    m = np.sqrt(1 + ZT)
    return Tc / (Th - Tc) * (m - Th / Tc) / (m + 1)


def energy():
    """Electrical power (W) by part for five transmitters at 25 Gb/s NRZ. Assumptions in the comments."""
    E = {}
    # VCSEL, Worked Example 25.2 levels 2 / 8 mA; current-mode driver from 3.3 V with a 50 ohm back-termination
    T = VC.tj_for(2e-3, 8e-3)
    plas = 0.5 * (2e-3 * VC.volt(2e-3) + 8e-3 * VC.volt(8e-3))
    itail = 6e-3 / (50 / (50 + VC.RS))
    E["VCSEL\n850 nm"] = dict(laser=plas, load=0.0, driver=VDD * (2e-3 + itail) - plas, temp=0.0)
    print(f"VCSEL: laser {plas*1e3:.1f} mW (junction {T:.0f} C); tail {itail*1e3:.1f} mA + 2 mA bias from {VDD} V ="
          f" {VDD*(2e-3+itail)*1e3:.1f} mW in all")
    # DML 20 / 60 mA; laser + 20 ohm series resistor = 25 ohm line, 25 ohm back-termination: half the tail reaches it
    pd = 0.5 * (I0D * dml_volt(I0D) + I1D * dml_volt(I1D))
    itail = 2 * (I1D - I0D)
    E["DML\n1310 nm"] = dict(laser=pd, load=0.0, driver=VDD * (I0D + itail) - pd, temp=0.0)
    print(f"DML: laser {pd*1e3:.1f} mW (V {dml_volt(I0D):.2f}/{dml_volt(I1D):.2f} V); tail {itail*1e3:.0f} mA + {I0D*1e3:.0f} mA bias"
          f" from {VDD} V = {VDD*(I0D+itail)*1e3:.0f} mW in all; average chip output {(dml_op(I0D)['P']+dml_op(I1D)['P'])/2*1e3:.1f} mW")
    # EML: DFB section CW at 60 mA; EAM 2 Vpp, 50 ohm shunt termination, back-terminated driver; photocurrent
    Idfb = 60e-3; pdfb = Idfb * dml_volt(Idfb); pcw = SLOPE * (Idfb - ITH)
    vpp = 2.0; pterm = (vpp / 2) ** 2 / 50.0; pdrv = VDD * vpp / 25.0
    T1, T0 = 10 ** (EAM["T1"] / 10), 10 ** (EAM["T0"] / 10); resp = p["lam"] / 1.2398     # A/W, every photon absorbed
    iph1, iph0 = pcw * (1 - T1) * resp, pcw * (1 - T0) * resp
    pph = 0.5 * (iph1 * EAM["Vb1"] + iph0 * EAM["Vb0"])
    pabs = pcw * (1 - 0.5 * (T1 + T0))
    heat = (pdfb - pcw) + pabs + pph + pterm
    cop = ioffe_cop(273.15 + 45, 273.15 + 75, 0.8)
    ptec = heat / cop
    E["EML\ncooled"] = dict(laser=pdfb, load=pterm + pph, driver=pdrv - pterm, temp=ptec)
    print(f"EML: DFB {pdfb*1e3:.0f} mW electrical, {pcw*1e3:.1f} mW CW into the EAM; EAM out {pcw*T1*1e3:.1f}/{pcw*T0*1e3:.2f} mW"
          f" (average {pcw*(T1+T0)/2*1e3:.1f} mW); termination {pterm*1e3:.0f} mW; driver tail {vpp/25*1e3:.0f} mA = {pdrv*1e3:.0f} mW;"
          f" photocurrent {iph1*1e3:.1f}/{iph0*1e3:.1f} mA at {EAM['Vb1']}/{EAM['Vb0']} V -> {pph*1e3:.1f} mW; absorbed {pabs*1e3:.1f} mW")
    print(f"     heat on the TEC {heat*1e3:.0f} mW; Ioffe COP_max (45 C chip, 75 C hot side, ZT 0.8) {cop:.2f} -> TEC >= {ptec*1e3:.0f} mW;"
          f" at 25 C case: none")
    # silicon MZM: CW laser +10 dBm in the waveguide at 15 % wall plug (Ch 38); 2 Vpp into 50 ohm (Ch 20); bias heater
    plsi = 10e-3 / 0.15
    E["Si MZM"] = dict(laser=plsi, load=pterm, driver=pdrv - pterm, temp=26e-3 / 2)
    # silicon ring: the same laser; 20 fJ/bit ring, 0.5 pJ/bit CMOS driver (Ch 38), heater up to 20 mW (Ch 18)
    E["Si ring"] = dict(laser=plsi, load=20e-15 * BR_E, driver=0.5e-12 * BR_E, temp=20e-3)
    for k, v in E.items():
        tot = sum(v.values())
        print(f"{k.replace(chr(10),' '):14s}: " + ", ".join(f"{kk} {vv*1e3:5.1f}" for kk, vv in v.items())
              + f" mW; total {tot*1e3:5.0f} mW = {tot/BR_E*1e12:5.1f} pJ/bit at 25 Gb/s, without the driver overhead"
              f" {(tot-v['driver'])/BR_E*1e12:4.1f} pJ/bit")
    return E


# ============================================================== Figure 25.8: the devices
def _title(ax, letter, text, x=0.0, y=1.0):
    ax.text(x, y, letter, transform=ax.transAxes, fontweight="bold", color=INK, fontsize=9.5, ha="left", va="top", zorder=10)
    dx = 0.17 / (ax.get_position().width * ax.figure.get_figwidth())       # 0.17 inch to the right of the letter
    ax.text(x + dx, y - 0.005, text, transform=ax.transAxes, fontweight="bold", color=INK, fontsize=7.4,
            ha="left", va="top", zorder=10)


def fig_devices():
    fig = plt.figure(figsize=(6.6, 4.8))
    # ---- (a) VCSEL: the Section 24.8 design, widths to scale, heights x2
    VS = 2.0
    a = fig.add_axes([0.0, 0.68, 0.42, 0.31]); frameless(a, (-25, 25), (-3.0, 24.0)); a.set_anchor("NW")
    nl, nh = VC.LAM / 4 / VC.NL * VS, VC.LAM / 4 / VC.NH * VS
    box(a, -16, -2.6, 32, 2.6, "gaas"); label(a, -5, -1.3, "GaAs substrate", fs=FS_SMALL)
    y = 0.0
    for k in range(VC.NBOT):
        box(a, -16, y, 32, nl, "#EEF2FA"); box(a, -16, y + nl, 32, nh, "#B8C9E8"); y += nl + nh
    ybot = y; R = 12.0
    box(a, -R, y, 2 * R, VC.LCAV * VS, "#F4E6CC")
    for k in range(3):
        a.plot([-R, R], [y + VC.LCAV * VS / 2 + (k - 1) * 0.11] * 2, color=MAT["mqw"], lw=0.5)
    ycav = y; y += VC.LCAV * VS; yo = y
    for k in range(VC.NTOP):
        box(a, -R, y, 2 * R, nl, "#EEF2FA"); box(a, -R, y + nl, 2 * R, nh, "#B8C9E8"); y += nl + nh
    ytop = y
    box(a, -R, yo + nl * 0.15, R - 3.0, nl * 0.7, INK); box(a, 3.0, yo + nl * 0.15, R - 3.0, nl * 0.7, INK)
    box(a, -R, ytop, 5.0, 0.5, "metal"); box(a, R - 5.0, ytop, 5.0, 0.5, "metal")
    label(a, -16.6, ybot / 2, "n-DBR\n34 pairs", fs=FS_SMALL, ha="right")
    label(a, -12.6, (yo + ytop) / 2, "p-DBR\n20 pairs", fs=FS_SMALL, ha="right")
    callout(a, (9.5, yo + 0.2), (16.6, 10.6), "oxide\naperture", fs=FS_SMALL, ha="left")
    callout(a, (14.0, ycav + 0.25), (16.6, 6.2), "cavity,\n3 QWs", fs=FS_SMALL, ha="left")
    callout(a, (10.0, ytop + 0.5), (14.0, ytop + 4.6), "ring contact", fs=FS_SMALL, ha="left")
    arrow(a, (0, ytop + 0.7), (0, ytop + 8.5), col=RED, lw=1.6, ms=9)
    label(a, 1.0, ytop + 6.8, "850 nm", fs=FS_SMALL, col=RED, ha="left")
    for sg in (-1, 1):
        a.plot(sg * np.array([9.5, 6.5, 3.8, 3.0, 2.8]), [ytop - 0.05, yo + 3.0, yo + 1.0, yo + 0.3, ycav - 0.8],
               color=TEAL, lw=0.8, ls=(0, (3, 2)))
    label(a, -9.5, ytop + 2.0, "I(t)", fs=FS_SMALL, col=TEAL)
    scalebar(a, 4.0, -2.05, 10.0, "10 µm")
    _title(a, "a", "VCSEL (heights ×2)", x=0.0)
    print(f"VCSEL drawing: n-DBR {ybot/VS:.2f} um, cavity {VC.LCAV:.3f} um, p-DBR {(ytop-yo)/VS:.2f} um, total {ytop/VS:.2f} um")

    # ---- (b) DML and (c) EML side views; lengths to scale with each other (98.9 um per inch)
    tt = np.linspace(0, 1, 300); wav = np.where((tt * 5) % 2 < 1, 1.0, 0.0)

    def stack(ax, x0, x1, grating=True, mqw="q", wells=MAT["mqw"]):
        box(ax, x0, 0.0, x1 - x0, 0.3, "metal")
        box(ax, x0, 0.3, x1 - x0, 2.4, "inp")
        box(ax, x0, 2.7, x1 - x0, 0.55, mqw)
        for k in range(3):
            ax.plot([x0, x1], [2.83 + 0.14 * k] * 2, color=wells, lw=0.7, zorder=3)
        box(ax, x0, 3.25, x1 - x0, 1.9, "inp")
        if grating:
            per = 6.0; z = x0 + 1.0
            while z + per / 2 <= x1 - 1.0:
                box(ax, z, 3.45, per / 2, 0.3, "q", z=2); z += per

    def facet(ax, x, txt, side):
        box(ax, x - 3.0 if side < 0 else x, 0.3, 3.0, 4.85, VIOLET, alpha=0.55, z=3)
        label(ax, x + side * 8, 5.95, txt, fs=FS_SMALL, col=VIOLET, bold=True)

    def light_out(ax, x, L, wy=2.97, chirped=False):
        arrow(ax, (x + 4, wy), (x + L, wy), col=RED, lw=1.6, ms=9)
        xs = x + L + 8 + 46 * tt
        ax.plot(xs, 2.25 + 1.45 * wav, color=MUTED, lw=0.9)
        if chirped:                                           # rising edges blue-shifted, falling edges red-shifted
            for e in np.where(np.diff(wav) != 0)[0]:
                ax.plot([xs[e]] * 2, [2.25, 3.7], color=BLUE if wav[e + 1] > wav[e] else RED, lw=1.8)

    b = fig.add_axes([0.445, 0.70, 0.545, 0.28]); frameless(b, (-50, 305.7), (-1.5, 7.6), equal=False)
    Ld = p["L"] * 1e4
    stack(b, 0, Ld); box(b, 0, 5.15, Ld, 0.3, "metal")
    facet(b, 0, "HR", -1); facet(b, Ld, "AR", 1)
    light_out(b, Ld, 48, chirped=True)
    label(b, Ld + 48 + 31, 1.45, "chirped edges", fs=FS_SMALL, col=INK)
    arrow(b, (Ld / 2, 7.25), (Ld / 2, 5.6), col=TEAL, lw=1.0, ms=7)
    label(b, Ld / 2 + 6, 7.0, "I(t): bias + data current", fs=FS_SMALL, col=TEAL, ha="left")
    label(b, Ld / 2, 1.5, "n-InP substrate", fs=FS_SMALL)
    label(b, Ld / 2, 4.55, "p-InP", fs=FS_SMALL)
    callout(b, (22, 2.97), (-46, 1.7), "MQW", fs=FS_SMALL, ha="left")
    callout(b, (18, 3.6), (-46, 4.5), "grating", fs=FS_SMALL, ha="left")
    dim(b, (0, -0.8), (Ld, -0.8), f"{Ld:.0f} µm")
    _title(b, "b", "DML", x=0.0)

    c = fig.add_axes([0.07, 0.385, 0.92, 0.28]); frameless(c, (-50, 550.5), (-1.5, 7.6), equal=False)
    Lf, Li, Le = 300.0, 50.0, 100.0; xe = Lf + Li + Le
    stack(c, 0, Lf)
    stack(c, Lf, xe, grating=False, mqw="#D9CFAE", wells="#C98A7E")
    box(c, 0, 5.15, Lf, 0.3, "metal"); box(c, Lf + Li, 5.15, Le, 0.3, "metal")
    poly(c, [(Lf + 10, 5.151), (Lf + Li - 10, 5.151), (Lf + Li - 16, 3.9), (Lf + 16, 3.9)], "white", z=4)
    facet(c, 0, "HR", -1); facet(c, xe, "AR", 1)
    light_out(c, xe, 42)
    arrow(c, (230, 7.25), (230, 5.6), col=TEAL, lw=1.0, ms=7)
    label(c, 236, 7.0, "DC current", fs=FS_SMALL, col=TEAL, ha="left")
    arrow(c, (Lf + Li + Le / 2, 7.25), (Lf + Li + Le / 2, 5.6), col=BLUE, lw=1.0, ms=7)
    label(c, Lf + Li + Le / 2 + 6, 7.0, "−V(t): reverse bias + data", fs=FS_SMALL, col=BLUE, ha="left")
    label(c, Lf / 2 - 20, 1.75, "DFB section: continuous wave, single frequency", fs=FS_SMALL)
    label(c, Lf + Li + Le / 2, 1.75, "EAM (QCSE)", fs=FS_SMALL)
    label(c, Lf + Li / 2, 6.15, "isolation\ntrench", fs=FS_SMALL, col=INK)
    callout(c, (Lf + 2, 2.8), (Lf - 12, 0.85), "butt joint to a wider-gap MQW", fs=FS_SMALL, ha="right")
    for x0, x1, t in ((0, Lf, f"{Lf:.0f} µm"), (Lf, Lf + Li, f"{Li:.0f}"), (Lf + Li, xe, f"{Le:.0f} µm")):
        dim(c, (x0, -0.8), (x1, -0.8), t)
    _title(c, "c", "EML, side view", x=0.0)

    # ---- (d) EML top view, to scale on its own (except the ridge width)
    d = fig.add_axes([0.0, 0.0, 0.50, 0.335]); frameless(d, (-48, 530), (-175, 165)); d.set_anchor("W")
    W = 250.0
    box(d, 0, -W / 2, xe, W, "#ECE7DA", ec=MUTED, lw=0.5)
    box(d, 0, -3, xe, 6, "q", z=3)                                              # ridge, drawn 3x wider
    box(d, 4, -7, Lf - 8, 14, "metal", alpha=0.9, z=4)                          # DFB stripe contact
    box(d, 90, 22, 100, 80, "metal", z=4); box(d, 135, 6, 10, 17, "metal", z=4)   # DFB bond pad and bridge
    box(d, Lf + Li + 4, -7, Le - 8, 14, "metal", alpha=0.9, z=4)                # EAM stripe
    box(d, Lf + Li + 25, -85, 50, 50, "metal", z=4); box(d, Lf + Li + 45, -36, 10, 30, "metal", z=4)
    for x in (Lf, Lf + Li):
        d.plot([x, x], [-W / 2, W / 2], color=MUTED, lw=0.6, ls=":", zorder=5)
    label(d, 140, 62, "DFB pad", fs=FS_SMALL, col="white", bold=True, z=6)
    label(d, Lf + Li + 50, -60, "EAM\npad", fs=FS_SMALL, col="white", bold=True, z=6)
    callout(d, (225, 0), (225, -70), "ridge (drawn 3× wider)", fs=FS_SMALL, ha="center")
    label(d, Lf + Li / 2, 105, "isolation", fs=FS_SMALL, col=MUTED)
    d.plot([Lf + Li + 75, xe + 35], [-60, -60], color=INK, lw=0.7, zorder=6)     # off-chip 50 ohm termination
    zy = np.linspace(-66, -114, 9); zx = xe + 35 + 7 * np.array([0, 1, -1, 1, -1, 1, -1, 1, 0])
    d.plot(np.r_[xe + 35, zx, xe + 35], np.r_[-60, zy, -120], color=INK, lw=0.7, zorder=6)
    for k, wdt in enumerate((14, 9, 4)):
        d.plot([xe + 35 - wdt, xe + 35 + wdt], [-122 - 5 * k] * 2, color=INK, lw=0.7)
    label(d, xe + 46, -90, "50 Ω", fs=FS_SMALL, ha="left")
    arrow(d, (xe + 4, 0), (xe + 55, 0), col=RED, lw=1.4, ms=8)
    dim(d, (-25, -W / 2), (-25, W / 2), f"{W:.0f} µm")
    dim(d, (0, -150), (xe, -150), f"{xe:.0f} µm")
    _title(d, "d", "EML, top view", x=0.0)

    # ---- (e) silicon-photonics transmitter, schematic
    e = fig.add_axes([0.52, 0.0, 0.47, 0.335]); frameless(e, (0, 100), (-30, 42), equal=False)
    block(e, 9, 4, 14, 14, "CW\nlaser", fc="#F3E6D6", fs=FS_SMALL)
    e.plot([16, 26], [4, 4], color=RED, lw=1.2)
    for yy in (12, -4):
        e.plot([26, 31, 33, 67, 69, 74], [4, 4 + (yy - 4) * 0.4, yy, yy, 4 + (yy - 4) * 0.4, 4], color=RED, lw=1.2)
    box(e, 35, 14, 30, 3.5, "metal", z=3); box(e, 35, 5.5, 30, 3.0, "metal", z=3); box(e, 35, -9.5, 30, 3.5, "metal", z=3)
    label(e, 50, 22.5, "travelling-wave electrodes", fs=FS_SMALL)
    e.plot([74, 84], [4, 4], color=RED, lw=1.2)
    poly(e, [(84, 2.5), (84, 5.5), (92, 10), (92, -2)], "si", z=3)
    for k in range(5):
        e.plot([85.5 + 1.3 * k] * 2, [3.2 - 0.8 * k, 4.8 + 0.8 * k], color=INK, lw=0.6, zorder=4)
    arrow(e, (88, 11), (88, 24), col=RED, lw=1.3, ms=8)
    label(e, 90, 21, "to fibre", fs=FS_SMALL, col=RED, ha="left")
    arrow(e, (31, -22), (35.5, 5.6), col=BLUE, lw=1.0, ms=7)
    label(e, 31, -26, "voltage driver, 2 Vpp", fs=FS_SMALL, col=BLUE)
    e.plot([65, 70, 70], [7, 7, -12], color=INK, lw=0.6); label(e, 71, -16, "50 Ω", fs=FS_SMALL, ha="left")
    _title(e, "e", "Silicon transmitter (schematic)", x=0.0)
    save(fig, "ch25_tx_devices")


# ============================================================== Figure 25.9: chirp and dispersion
def _eye_panel(ax, r, DL, col, BR):
    spb = r["spb"]; n = len(BITS) * spb
    raw = bessel4(abs(fibre(r["E"], DT, DL)) ** 2, DT, 0.75 * BR)
    h, tau = eye(raw, spb)
    lo, hi = np.percentile(raw, 0.5), np.percentile(raw, 99.5)
    t = np.arange(2 * spb + 1) / spb - 1
    segs = [np.column_stack([t, (raw[(kb * spb + tau - spb + np.arange(2 * spb + 1)) % n] - lo) / (hi - lo)])
            for kb in range(len(BITS))]
    ax.add_collection(LineCollection(segs, colors=col, linewidths=0.5, alpha=0.22, rasterized=True))
    v = raw[(np.arange(len(BITS)) * spb + tau) % n]
    lo1, hi0 = (v[BITS == 1].min() - lo) / (hi - lo), (v[BITS == 0].max() - lo) / (hi - lo)
    if h > 0:
        ax.annotate("", xy=(0, lo1), xytext=(0, hi0), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9, shrinkA=0, shrinkB=0))
    return 10 * np.log10(r["b2b"] / h)


def fig_dispersion():
    fig = plt.figure(figsize=(6.6, 4.9))
    BR = 10e9; DLe = 425.0                                     # 25 km at 17 ps/(nm km)
    eyes = [(CASES[0][0], 0.0, "DML, back to back", C2), (CASES[0][0], DLe, "DML after 25 km at 1550 nm", C2),
            (CASES[1][0], DLe, "EML (α$_\\mathrm{EAM}$ = +0.5) after 25 km", C4)]
    for k, (name, DL, title, col) in enumerate(eyes):
        ax = fig.add_axes([0.06 + k * 0.32, 0.67, 0.27, 0.27])
        pen = _eye_panel(ax, RESULTS[(BR, name)], DL, col, BR)
        ax.text(0.03, 0.97, f"penalty {max(pen, 0):.1f} dB" if DL else "10 Gb/s, open eye", transform=ax.transAxes,
                fontsize=6.6, color=INK, va="top")
        ax.set_xlim(-1, 1); ax.set_ylim(-0.2, 1.3); ax.set_yticks([]); ax.grid(False)
        ax.set_xticks([-1, 0, 1]); ax.set_xticklabels(["−1", "0", "1"]); ax.set_xlabel("Time (bits)", labelpad=1)
        ax.set_title(title, fontsize=7.3, loc="left", color=INK, pad=3)
        tag(ax, "abc"[k])
        print(f"eye panel {title}: penalty {pen:.2f} dB")
    for k, BR in enumerate((10e9, 25e9)):
        ax = fig.add_axes([0.07 + k * 0.49, 0.08, 0.41, 0.38])
        for name, kind, al, col in CASES:
            r = RESULTS[(BR, name)]; DL, pen = r["DL"], r["pen"].copy()
            for side in (DL >= 0, DL <= 0):                    # each curve ends where it first passes 2.5 dB
                idx = np.where(side)[0]
                if side[0]: idx = idx[::-1]
                over = np.where(pen[idx] > 2.5)[0]
                if len(over): pen[idx[over[0] + 1:]] = np.nan
            ax.plot(DL, pen, color=col, lw=1.3, ls="--" if kind == "dml" else "-", label=name)
        ax.axhline(1, color=MUTED, lw=0.6, ls=":")
        s = (10e9 / BR) ** 2
        ax.set_ylim(-0.3, 3.0); ax.set_xlim(-600 * s, 2000 * s)
        finish(ax, "Accumulated dispersion (ps/nm)", "Dispersion penalty (dB)")
        top = ax.secondary_xaxis("top", functions=(lambda x: x / 17, lambda x: x * 17))
        top.set_xlabel("km of fibre at 1550 nm", fontsize=7, labelpad=2); top.tick_params(labelsize=6.8)
        ax.text(0.02, 0.97, f"{BR/1e9:.0f} Gb/s NRZ", transform=ax.transAxes, fontsize=7.6, color=INK, va="top", fontweight="bold")
        ax.text(1980 * s, 0.94, "1 dB", fontsize=6.4, color=MUTED, va="top", ha="right")
        tag(ax, "de"[k])
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="center", bbox_to_anchor=(0.53, 0.555), ncol=4, fontsize=6.6, handlelength=2.4, frameon=False)
    plt.rcParams["savefig.dpi"] = 150                          # resolution of the rasterised eye traces
    save(fig, "ch25_tx_dispersion")
    plt.rcParams["savefig.dpi"] = "figure"


# ============================================================== Figure 25.10: energy per bit
def fig_energy(E):
    fig, ax = plt.subplots(figsize=(6.3, 2.6))
    names = list(E.keys())
    parts = [("laser", "laser (electrical)", C1, None), ("load", "modulator load", C3, None),
             ("driver", "driver overhead (estimate)", C2, "////"), ("temp", "TEC (70 °C case) or heater", C4, None)]
    y = np.arange(len(names))[::-1]
    for yi, nm in zip(y, names):
        x0 = 0.0
        for key, lab, col, hatch in parts:
            w = E[nm][key] / BR_E * 1e12
            if w <= 0: continue
            ax.barh(yi, w, left=x0, height=0.62, color=col if hatch is None else "white", edgecolor=col, hatch=hatch, lw=0.8)
            x0 += w
        tot = sum(E[nm].values())
        ax.text(x0 + 0.25, yi, f"{tot/BR_E*1e12:.1f} pJ/bit ({tot*1e3:.0f} mW)", va="center", fontsize=7, color=INK)
    hd = [Patch(fc=col if hatch is None else "white", ec=col, hatch=hatch, lw=0.8, label=lab) for _, lab, col, hatch in parts]
    ax.legend(handles=hd, loc="lower right", fontsize=6.6, ncol=2)
    ax.set_yticks(y); ax.set_yticklabels([n.replace("\n", " ") for n in names])
    ax.set_xlim(0, 25); ax.grid(axis="y", visible=False)
    finish(ax, "Energy per bit at 25 Gb/s NRZ (pJ/bit)")
    save(fig, "ch25_tx_energy")


# ============================================================== Figure 25.11: where each transmitter is used
STD = [  # (label, GBd, reach in m, band, PAM4, label position (x factor, y factor), ha)
    ("10GBASE-SR", 10.3125, (300, 400), "mmf", False, (1.07, 1.0), "left"),
    ("25GBASE-SR, 100GBASE-SR4", 25.78125, (70, 100), "mmf", False, (1.07, 1.0), "left"),
    ("10GBASE-LR", 10.3125, (10e3,), "o", False, (0.93, 1.0), "right"),
    ("25GBASE-LR, 100GBASE-LR4", 25.78125, (10e3,), "o", False, (0.93, 1.25), "right"),
    ("100G CWDM4", 25.78125, (2e3,), "o", False, (0.93, 1.0), "right"),
    ("100GBASE-DR, 400GBASE-DR4", 53.125, (500,), "o", True, (0.93, 1.0), "right"),
    ("100GBASE-FR1, 400GBASE-FR4", 53.125, (2e3,), "o", True, (1.07, 0.92), "left"),
    ("400GBASE-LR4-6", 53.125, (6e3,), "o", True, (1.07, 0.92), "left"),
    ("100GBASE-LR1", 53.125, (10e3,), "o", True, (1.07, 1.12), "left"),
    ("10GBASE-ER", 10.3125, (40e3,), "c", False, (0.93, 1.0), "right"),
    ("400ZR", 59.84375, (120e3,), "coh", False, (0.93, 1.0), "right"),
]
BANDS = {"mmf": ("850 nm, multimode fibre (OM3–OM4)", C1, "o"), "o": ("O band, single-mode fibre", C3, "s"),
         "c": ("C band, single-mode fibre", C4, "^"), "coh": ("C band, coherent DWDM", C5, "*")}


def fig_map():
    fig = plt.figure(figsize=(6.6, 4.5))
    ax = fig.add_axes([0.10, 0.27, 0.88, 0.70])
    B = np.logspace(np.log10(2), np.log10(130), 200)
    cf = RESULTS[(10e9, CASES[2][0])]; m = cf["DL"] >= 0
    tol10 = crossing(cf["DL"][m], cf["pen"][m], 1.0)            # chirp-free 1 dB tolerance at 10 GBd (ps/nm)
    lines = [(17.0, INK, "-", "chirp-free NRZ at 1550 nm (17 ps/(nm·km))"),
             (abs(d_fibre(1264.5, 1324)), C3, "-.", f"chirp-free NRZ, worst CWDM lane ({abs(d_fibre(1264.5, 1324)):.1f} ps/(nm·km))"),
             (abs(d_fibre(1310, 1324)), C3, ":", f"chirp-free NRZ at 1310 nm ({abs(d_fibre(1310, 1324)):.1f} ps/(nm·km))")]
    for D, col, ls, lab in lines:
        ax.plot(B, tol10 * (10 / B) ** 2 / D * 1e3, color=col, lw=1.0, ls=ls, label=lab + ", 1 dB")
    for b in (10.3125, 25.78125, 53.125):
        print(f"map: chirp-free 1 dB tolerance at {b} GBd {tol10*(10/b)**2:.0f} ps/nm -> "
              + ", ".join(f"{tol10*(10/b)**2/D:.1f} km at {D:.2f} ps/(nm km)" for D, *_ in lines))
    seen = set()
    for lab, gbd, reach, band, pam, (fx, fy), ha in STD:
        name, col, mk = BANDS[band]
        if len(reach) == 2:
            ax.plot([gbd, gbd], reach, color=col, lw=1.6, solid_capstyle="round", zorder=4)
        for rr in reach:
            ax.plot(gbd, rr, marker=mk, ms=8 if mk == "*" else 5, color=col, mfc="white" if pam else col, mew=1.1, ls="none",
                    zorder=5, label=name if band not in seen else None)
            seen.add(band)
        ax.text(gbd * fx, np.exp(np.mean(np.log(reach))) * fy, lab, fontsize=6.3, color=col, ha=ha, va="center", zorder=6,
                bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.85))
    ax.plot([], [], marker="s", color=MUTED, mfc="white", ls="none", ms=5, label="open marker: PAM4 (two bits per symbol)")
    kw = dict(fontsize=7, style="italic", color=MUTED, zorder=6)
    ax.text(2.3, 150, "typically VCSELs", **kw)
    ax.text(2.3, 4.0e3, "typically DMLs", **kw)
    ax.text(38, 1.0e3, "typically EMLs\nor Si MZMs", ha="center", **kw)
    ax.text(2.3, 6.5e4, "typically EMLs", **kw)
    ax.text(75, 4.0e4, "IQ modulators:\nInP, Si or TFLN", ha="center", **kw)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(2, 130); ax.set_ylim(30, 3e5)
    ax.set_xticks([2.5, 5, 10, 25, 50, 100]); ax.set_xticklabels(["2.5", "5", "10", "25", "50", "100"])
    ax.minorticks_off()
    ax.set_yticks([100, 1e3, 1e4, 1e5]); ax.set_yticklabels(["100 m", "1 km", "10 km", "100 km"])
    finish(ax, "Symbol rate per lane (GBd)", "Reach")
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.53, 0.0), ncol=2, fontsize=6.4, frameon=False, handlelength=2.4)
    save(fig, "ch25_tx_map")


if __name__ == "__main__":
    run_sweeps()
    numbers()
    E = energy()
    fig_devices()
    fig_dispersion()
    fig_energy(E)
    fig_map()
