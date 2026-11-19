# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 10: laser rate equations in Python (Open-Photonics, Chapters 24 and 25).

Run it from a terminal:
    python lab10_rate_equations.py              # prints every checkpoint and saves lab10_rate_equations.png
    python lab10_rate_equations.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. Inside, the units are the chapters' own: cm, s, A and W;
the printout converts to mA, mW, ns and GHz.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-10/
"""
import math
import sys

import numpy as np

# The 400 um InGaAsP Fabry-Perot laser of Worked Example 24.1: the parameters of the Chapter 24 and 25 demos
Q = 1.602e-19                 # electron charge (C)
VG = 3e10 / 3.6               # group velocity (cm/s): group index 3.6
HNU = 1.2398 / 1.55 * Q       # photon energy at 1550 nm (J)
W, D_ACT = 2e-4, 0.05e-4      # active region 2 um wide and 50 nm thick (cm)
GAMMA = 0.06                  # confinement factor
ETA_I = 0.8                   # injection efficiency
ALPHA_I = 15.0                # internal loss (1/cm)
G0, NTR0 = 1500.0, 2e18       # gain g(N) = G0 ln(N/Ntr) (1/cm); transparency density at 25 C (1/cm^3)
T0N = 143.0                   # Ntr grows as exp((T - 25 C)/T0N) (K)
EPS = 2e-17                   # gain compression (cm^3)
BETA = 1e-4                   # fraction of the spontaneous emission that enters the lasing mode
A_SRH, B_RAD, C_AUG = 1e8, 1e-10, 3e-29   # recombination coefficients of Chapter 23 (1/s, cm^3/s, cm^6/s)
NSP = 1.8                     # population-inversion factor (Chapter 25)


# ---------------------------------------------------------------------------------------------------------
# Part A. The cavity and the threshold (Chapter 24, Sections 24.1, 24.2 and 24.4)
# ---------------------------------------------------------------------------------------------------------
def recomb(N):
    """Recombination rate R(N) = AN + BN^2 + CN^3 (Chapter 23), in cm^-3 s^-1."""
    return A_SRH * N + B_RAD * N**2 + C_AUG * N**3


def laser(L_um=400.0, R1=0.32, R2=0.32, T=25.0):
    """Cavity, threshold and slope of the Fabry-Perot laser, as a dict.

    R1 is the front facet (the output) and R2 the rear; T is the temperature in degrees C.
    """
    L = L_um * 1e-4                                       # cavity length (cm)
    V = L * W * D_ACT                                     # active volume (cm^3)
    am = math.log(1 / (R1 * R2)) / (2 * L)                # mirror loss (1/cm)
    tp = 1 / (VG * (ALPHA_I + am))                        # photon lifetime (s)
    Ntr = NTR0 * math.exp((T - 25) / T0N)                 # transparency density: rises with temperature
    gth = (ALPHA_I + am) / GAMMA                          # threshold gain: Gamma g_th = alpha_i + alpha_m
    Nth = Ntr * math.exp(gth / G0)                        # the carrier density that gives it
    Ith = Q * V / ETA_I * recomb(Nth)                     # threshold current (A)
    eta_d = ETA_I * am / (ALPHA_I + am)                   # differential quantum efficiency, both facets
    F1 = (1 - R1) / ((1 - R1) + math.sqrt(R1 / R2) * (1 - R2))   # share of the output leaving the front facet
    return dict(L_um=L_um, V=V, am=am, tp=tp, Ntr=Ntr, gth=gth, Nth=Nth, Ith=Ith, eta_d=eta_d, F1=F1,
                slope=eta_d * F1 * HNU / Q, T=T)


# ---------------------------------------------------------------------------------------------------------
# Part B. The steady-state L-I curve (Chapter 24, Sections 24.3 and 24.4)
# ---------------------------------------------------------------------------------------------------------
def front_power(S, lz):
    """Front-facet power (W) at photon density S: S V/Gamma photons in the cavity, leaving at the rate v_g alpha_m."""
    return S * lz["V"] / GAMMA * VG * lz["am"] * HNU * lz["F1"]


def li_curve(lz, n=300):
    """Steady-state L-I curve, parametric in N just below its clamped value N_th (gain compression neglected).

    For each N, dS/dt = 0 gives S (stimulated emission seeded by the spontaneous emission beta B N^2);
    dN/dt = 0 then gives the current that holds that N. Returns current (A) and front-facet power (W).
    """
    x = 10 ** (-0.2 - 7 * np.arange(n + 1) / n)          # 1 - N/N_th, from 0.63 down to 6e-8
    N = lz["Nth"] * (1 - x)
    g = G0 * np.log(N / lz["Ntr"])
    S = GAMMA * BETA * B_RAD * N**2 / (1 / lz["tp"] - GAMMA * VG * g)
    I = Q * lz["V"] / ETA_I * (recomb(N) + VG * g * S)
    return I, front_power(S, lz)


# ---------------------------------------------------------------------------------------------------------
# Part C. The turn-on transient with a Runge-Kutta integrator (Chapter 24, Section 24.6)
# ---------------------------------------------------------------------------------------------------------
def rates(y, I, lz):
    """The rate equations of Section 24.3: dN/dt and dS/dt at y = (N, S) and current I, with gain compression."""
    N, S = y
    g = G0 * math.log(max(N, 1e10) / lz["Ntr"]) / (1 + EPS * S)
    return np.array([ETA_I * I / (Q * lz["V"]) - recomb(N) - VG * g * S,
                     GAMMA * VG * g * S - S / lz["tp"] + GAMMA * BETA * B_RAD * N**2])


def rk4(f, y0, dt, n_steps):
    """Classic fourth-order Runge-Kutta for dy/dt = f(y): returns the n_steps + 1 states, y0 first."""
    ys = np.empty((n_steps + 1, len(y0)))
    y = np.array(y0, dtype=float)
    for k in range(n_steps + 1):
        ys[k] = y
        k1 = f(y)
        k2 = f(y + dt / 2 * k1)
        k3 = f(y + dt / 2 * k2)
        k4 = f(y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ys


def turn_on(I, lz, y0=(1e17, 1.0), t_end=4e-9, dt=0.5e-12):
    """The current steps from 0 to I at t = 0 (the demo's switch-on). Returns times (s), N and S.

    dt = 0.5 ps is a fifth of the photon lifetime: small enough for RK4 to follow the fastest change.
    """
    n = round(t_end / dt)
    ys = rk4(lambda y: rates(y, I, lz), y0, dt, n)
    return dt * np.arange(n + 1), ys[:, 0], ys[:, 1]


def peaks(t, y):
    """Times and heights of the local maxima of y, each refined by a parabola through it and its two neighbours."""
    i = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
    a, b, c = y[i - 1], y[i], y[i + 1]
    shift = 0.5 * (a - c) / (a - 2 * b + c)              # vertex of the parabola, in samples
    return t[i] + shift * (t[1] - t[0]), b - 0.25 * (a - c) * shift


# ---------------------------------------------------------------------------------------------------------
# Part D. Small-signal modulation response (Chapter 25, Section 25.1)
# ---------------------------------------------------------------------------------------------------------
def small_signal(I, lz):
    """f_r, damping, K-factor and the noise quantities at bias I above threshold, as in the Chapter 25 demo."""
    S = GAMMA * lz["tp"] * ETA_I * (I - lz["Ith"]) / (Q * lz["V"])    # photon density, linear above threshold
    a = G0 / lz["Nth"]                                                 # differential gain dg/dN at N_th
    wr2 = VG * a * S / (lz["tp"] * (1 + EPS * S))                      # (2 pi f_r)^2
    K = 4 * math.pi**2 * (lz["tp"] + EPS / (VG * a))                   # K-factor (s)
    fr = math.sqrt(wr2) / (2 * math.pi)
    tdn = 1 / (A_SRH + 2 * B_RAD * lz["Nth"] + 3 * C_AUG * lz["Nth"]**2)   # differential carrier lifetime dN/dR
    Np = S * lz["V"] / GAMMA                                           # photons in the cavity
    return dict(S=S, a=a, wr2=wr2, K=K, fr=fr, gam=K * fr**2 + 1 / tdn, tdn=tdn, Np=Np,
                P=Np * HNU * VG * lz["am"],                            # output power, both facets (W)
                Rsp=VG * (ALPHA_I + lz["am"]) * NSP)                   # spontaneous emission into the mode (1/s)


def H2(ss, f):
    """|H(f)|^2 = f_r^4 / ((f_r^2 - f^2)^2 + (f gamma/2pi)^2), written with angular frequencies."""
    w = 2 * np.pi * f
    return ss["wr2"]**2 / ((ss["wr2"] - w**2)**2 + w**2 * ss["gam"]**2)


def f3db(response, lo=1e8, hi=2e11):
    """3 dB bandwidth of a response function |H(f)|^2: bisection on a log scale for |H|^2 = 1/2."""
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if response(mid) > 0.5:
            lo = mid
        else:
            hi = mid
    return lo


def jacobian(y, I, lz):
    """2 x 2 matrix of the partial derivatives of the rate equations at y, by central differences."""
    J = np.empty((2, 2))
    for k in range(2):
        e = np.zeros(2)
        e[k] = 1e-6 * y[k]
        J[:, k] = (rates(y + e, I, lz) - rates(y - e, I, lz)) / (2 * e[k])
    return J


def steady_state(I, lz):
    """(N, S) where both rate equations vanish, gain compression and spontaneous emission included: Newton's method."""
    y = np.array([lz["Nth"], max(GAMMA * lz["tp"] * ETA_I * (I - lz["Ith"]) / (Q * lz["V"]), 1e10)])
    for _ in range(50):
        dy = np.linalg.solve(jacobian(y, I, lz), -rates(y, I, lz))
        y = y + dy
        if abs(dy[1]) < 1e-12 * y[1]:
            break
    return y


def linearised(I, lz):
    """Linearise the full rate equations at the operating point: d(dy)/dt = J dy + b dI.

    The eigenvalues of J are -gamma/2 +- j omega_d, so det J = omega_r^2 and -trace J = gamma.
    Returns f_r, gamma, the ringing frequency f_d and the normalised response |H(f)|^2 = |dS(f)/dS(0)|^2.
    """
    y = steady_state(I, lz)
    J = jacobian(y, I, lz)
    b = np.array([ETA_I / (Q * lz["V"]), 0.0])
    dS0 = np.linalg.solve(-J, b)[1]
    response = lambda f: abs(np.linalg.solve(2j * np.pi * f * np.eye(2) - J, b)[1] / dS0) ** 2
    ev = np.linalg.eigvals(J)
    return dict(y=y, fr=math.sqrt(np.linalg.det(J)) / (2 * math.pi), gam=-np.trace(J),
                fd=abs(ev[0].imag) / (2 * math.pi), response=response)


# ---------------------------------------------------------------------------------------------------------
# Part F. Relative intensity noise and linewidth (Chapter 25, Sections 25.3 and 25.4)
# ---------------------------------------------------------------------------------------------------------
def rin(ss, f):
    """RIN (1/Hz) of the Chapter 25 demo: Langevin noise filtered by the laser's response, plus shot noise 2 h nu/P."""
    w = 2 * np.pi * f
    g0 = 1 / ss["tdn"]
    return (4 * ss["Rsp"] * (g0**2 + w**2) / (ss["Np"] * ((ss["wr2"] - w**2)**2 + w**2 * ss["gam"]**2))
            + 2 * HNU / ss["P"])


def linewidth(ss, alpha=4.0):
    """Schawlow-Townes-Henry linewidth (Hz): R_sp (1 + alpha^2) / (4 pi N_p), the key equation of Section 25.4."""
    return ss["Rsp"] * (1 + alpha**2) / (4 * math.pi * ss["Np"])


def main(plot=True):
    print("Lab 10: laser rate equations (the 400 um InGaAsP Fabry-Perot laser of Worked Example 24.1)\n")

    # ---- Part A
    lz = laser()
    print("A. Cavity and threshold, cleaved facets R = 0.32")
    print(f"   mode spacing lambda^2/(2 n_g L) = {1e7 * 1.55e-4**2 / (2 * 3.6 * lz['L_um'] * 1e-4):.2f} nm"
          "   (Chapter 24: 0.83 nm)")
    print(f"   mirror loss alpha_m = {lz['am']:.1f} /cm, photon lifetime tau_p = {1e12 * lz['tp']:.2f} ps"
          "   (Chapter 24: 28.5 /cm; Chapter 25: 2.76 ps)")
    print(f"   threshold gain g_th = {lz['gth']:.0f} /cm, N_th = {lz['Nth']:.3g} /cm^3, R(N_th) = {recomb(lz['Nth']):.3g}"
          " /cm^3/s   (Chapter 24: 725 /cm, 3.24e18, 2.4e27)")
    print(f"   threshold current I_th = {1e3 * lz['Ith']:.1f} mA   (Chapter 24: 19 mA; demo readout 19.2 mA)")
    print(f"   eta_d = {lz['eta_d']:.3f}, slope = {lz['slope']:.3f} W/A per facet   (Chapter 24: 0.52 and 0.21 W/A)\n")

    # ---- Part B
    I_li, P_li = li_curve(lz)
    P50 = np.interp(0.05, I_li, P_li)
    P_lin = lz["slope"] * (0.05 - lz["Ith"])
    V50 = 0.85 + 5 * 0.05                                 # diode drop plus series resistance
    print("B. Steady-state L-I curve")
    print(f"   front-facet power at 50 mA = {1e3 * P50:.2f} mW (straight line from I_th: {1e3 * P_lin:.2f} mW)"
          "   (Chapter 24: about 6.5 mW)")
    print(f"   wall-plug efficiency at 50 mA, both facets: {2 * P50 / (0.05 * V50):.1%} of {1e3 * 0.05 * V50:.0f} mW"
          "   (Chapter 24: about 23 % of 55 mW)")
    print(f"   at threshold the facet emits {1e6 * np.interp(lz['Ith'], I_li, P_li):.1f} uW of spontaneous emission"
          " into the lasing mode\n")

    # ---- Part C
    t, N, S = turn_on(0.04, lz)
    P = front_power(S, lz)
    tau_n = lz["Nth"] / recomb(lz["Nth"])
    t_N = t[np.argmax(N >= lz["Nth"])]
    t_half = t[np.argmax(P >= 0.5 * P[-1])]
    tp_, Pp = peaks(t, P)
    f_ring = 1 / np.mean(np.diff(tp_[1:6]))               # from the second to the sixth peak: the small ringing
    print("C. Turn-on transient at 40 mA (RK4, 0.5 ps steps, from N = 1e17 /cm^3)")
    print(f"   carrier lifetime at threshold N_th/R(N_th) = {1e9 * tau_n:.2f} ns; tau_n ln(I/(I - I_th)) = "
          f"{1e9 * tau_n * math.log(0.04 / (0.04 - lz['Ith'])):.2f} ns   (Chapter 24: 1.35 ns and 0.9 ns)")
    print(f"   RK4: N reaches N_th at {1e9 * t_N:.2f} ns, the light passes half its final power at {1e9 * t_half:.2f} ns,"
          f" first peak {1e3 * Pp[0]:.1f} mW at {1e9 * tp_[0]:.2f} ns")
    print(f"   ringing at {f_ring / 1e9:.2f} GHz, settling to {1e3 * P[-1]:.2f} mW"
          f"   (Chapter 24 demo readout: f_r = 3.9 GHz)\n")

    # ---- Part D
    print("D. Small-signal modulation response")
    for I_mA, ch in ((40, ""), (50, "   (Chapter 25: 4.7 and 7.2 GHz)"), (120, "   (Chapter 25: 8.4 and 12.6 GHz)")):
        ss = small_signal(I_mA * 1e-3, lz)
        print(f"   {I_mA:3d} mA: f_r = {ss['fr'] / 1e9:.2f} GHz, f_3dB = {f3db(lambda f: H2(ss, f)) / 1e9:.2f} GHz{ch}")
    ss50 = small_signal(0.05, lz)
    print(f"   a = g0/N_th = {ss50['a']:.3g} cm^2, K = {1e12 * ss50['K']:.0f} ps, cap 2 pi sqrt(2)/K ="
          f" {2 * math.pi * math.sqrt(2) / ss50['K'] / 1e9:.1f} GHz   (Chapter 25: 4.6e-16 cm^2, 314 ps, about 28 GHz)")
    for I_mA in (40, 50):
        lin = linearised(I_mA * 1e-3, lz)
        print(f"   full rate equations linearised at {I_mA} mA: f_r = {lin['fr'] / 1e9:.2f} GHz, gamma = {lin['gam'] / 1e9:.2f}"
              f" /ns, ringing f_d = {lin['fd'] / 1e9:.2f} GHz, f_3dB = {f3db(lin['response']) / 1e9:.2f} GHz")
    print()

    # ---- Part E
    print("E. Temperature (the transparency density grows with T0N = 143 K)")
    Iths = {T: laser(T=T)["Ith"] for T in (25, 55, 85)}
    print("   I_th = " + ", ".join(f"{1e3 * v:.1f} mA at {T} C" for T, v in Iths.items())
          + "   (Chapter 24: 19 to 52 mA from 25 to 85 C)")
    Nth = lz["Nth"]
    p = (A_SRH * Nth + 2 * B_RAD * Nth**2 + 3 * C_AUG * Nth**3) / recomb(Nth)
    print(f"   T0 = 60 K / ln(I_th(85)/I_th(25)) = {60 / math.log(Iths[85] / Iths[25]):.1f} K   (Chapter 24: T0 = 60 K);"
          f" at 25 C, d ln R/d ln N = {p:.2f}, so T0 = T0N/{p:.2f} = {T0N / p:.0f} K")
    print(f"   at 85 C, 50 mA is below threshold: the front facet emits only {1e6 * np.interp(0.05, *li_curve(laser(T=85))):.0f} uW"
          " of spontaneous emission\n")

    # ---- Part F
    fs = 40e9 * np.arange(1, 401) / 400
    print("F. Intensity noise and linewidth")
    for I_mA in (50, 120):
        ss = small_signal(I_mA * 1e-3, lz)
        r = 10 * np.log10(rin(ss, fs))
        print(f"   {I_mA:3d} mA: RIN peak {r.max():.1f} dB/Hz at {fs[r.argmax()] / 1e9:.1f} GHz, {10 * np.log10(rin(ss, 1e8)):.1f}"
              f" dB/Hz at 100 MHz; shot-noise floor {10 * np.log10(2 * HNU / ss['P']):.1f} dB/Hz")
    print(f"   linewidth at 50 mA ({1e3 * ss50['P'] / 2:.2f} mW per facet): {linewidth(ss50) / 1e6:.2f} MHz with alpha = 4,"
          f" {linewidth(ss50, 0) / 1e6:.3f} MHz with alpha = 0   (Chapter 25: 2.1 and 0.12 MHz at 6.5 mW)\n")

    if plot:
        make_figure(lz, (t, N, P))


def make_figure(lz, transient):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 3, figsize=(14, 8))
    # (a) L-I curves at three temperatures
    for T, col in ((25, "tab:blue"), (55, "tab:orange"), (85, "tab:red")):
        lt = laser(T=T)
        I, P = li_curve(lt)
        keep = I <= 0.12
        ax[0, 0].plot(1e3 * I[keep], 1e3 * P[keep], color=col, label=f"{T} °C, $I_{{th}}$ = {1e3 * lt['Ith']:.1f} mA")
    ax[0, 0].set(xlim=(0, 120), ylim=(0, None), xlabel="current (mA)", ylabel="front-facet power (mW)",
                 title="(a) L–I curves")
    ax[0, 0].legend(fontsize=8)
    # (b) turn-on transient at 40 mA
    t, N, P = transient
    ax[0, 1].plot(1e9 * t, 1e3 * P, color="tab:blue")
    ax[0, 1].set(xlabel="time (ns)", ylabel="front-facet power (mW)", title="(b) switch-on, 0 → 40 mA")
    tw = ax[0, 1].twinx()
    tw.plot(1e9 * t, N / lz["Nth"], color="tab:green", ls="--", lw=1)
    tw.set_ylabel("carrier density $N/N_{th}$ (dashed)", color="tab:green")
    # (c) modulation response at three biases
    f = np.linspace(1e7, 25e9, 600)
    for I_mA, col in ((30, "tab:orange"), (50, "tab:blue"), (120, "tab:red")):
        ax[0, 2].plot(f / 1e9, 10 * np.log10(H2(small_signal(I_mA * 1e-3, lz), f)), color=col, label=f"{I_mA} mA")
    ax[0, 2].axhline(-3, color="grey", ls=":", lw=0.8)
    ax[0, 2].set(ylim=(-20, 16), xlabel="frequency (GHz)", ylabel="$|H(f)|^2$ (dB)", title="(c) modulation response")
    ax[0, 2].legend(fontsize=8)
    # (d) f_r and f_3dB against bias
    Is = np.linspace(21e-3, 120e-3, 100)
    sss = [small_signal(I, lz) for I in Is]
    ax[1, 0].plot(1e3 * Is, [s["fr"] / 1e9 for s in sss], color="tab:blue", label="$f_r$")
    ax[1, 0].plot(1e3 * Is, [f3db(lambda f, s=s: H2(s, f)) / 1e9 for s in sss], color="tab:red", label="$f_{3dB}$")
    ax[1, 0].plot([50, 50, 120, 120], [4.7, 7.2, 8.4, 12.6], "ko", ms=4, label="Chapter 25")
    ax[1, 0].set(xlabel="bias current (mA)", ylabel="frequency (GHz)", title="(d) bandwidth against bias")
    ax[1, 0].legend(fontsize=8)
    # (e) threshold against temperature, on a log scale: a straight line means exp(T/T0)
    Ts = np.linspace(10, 95, 60)
    ax[1, 1].semilogy(Ts, [1e3 * laser(T=T)["Ith"] for T in Ts], color="tab:blue", label="rate equations")
    ax[1, 1].semilogy(Ts, 1e3 * lz["Ith"] * np.exp((Ts - 25) / 60), "k:", label=r"$e^{(T-25)/60\,\mathrm{K}}$")
    ax[1, 1].minorticks_off()
    ax[1, 1].set_yticks([15, 20, 30, 40, 50, 60], labels=["15", "20", "30", "40", "50", "60"])
    ax[1, 1].set(xlabel="temperature (°C)", ylabel="threshold current (mA)", title="(e) threshold, $T_0$ = 60 K")
    ax[1, 1].legend(fontsize=8)
    # (f) RIN spectra
    f = np.linspace(1e8, 25e9, 600)
    for I_mA, col in ((30, "tab:orange"), (50, "tab:blue"), (120, "tab:red")):
        ax[1, 2].plot(f / 1e9, 10 * np.log10(rin(small_signal(I_mA * 1e-3, lz), f)), color=col, label=f"{I_mA} mA")
    ax[1, 2].axhline(-140, color="grey", ls=":", lw=0.8)
    ax[1, 2].set(ylim=(-175, -110), xlabel="frequency (GHz)", ylabel="RIN (dB/Hz)", title="(f) relative intensity noise")
    ax[1, 2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("lab10_rate_equations.png", dpi=150)
    print("Saved the figure as lab10_rate_equations.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
