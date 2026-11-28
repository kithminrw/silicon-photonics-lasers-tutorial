# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 16: driving a ring modulator: operating point, bandwidth, NRZ eyes and PAM4 (Open-Photonics, Chapter 20).

Run it from a terminal:
    python lab16_ringmod.py              # prints every checkpoint and saves lab16_ringmod.png
    python lab16_ringmod.py --no-plot    # numbers only

NumPy only (Matplotlib for the figure). The ring is the reference-link ring of Worked Example 20.2 and Section 20.8:
7.2 um radius, n_g = 3.89, Q_i = 15 000, Q_L = 8000, a junction that moves the resonance by 50 pm/V, 2 Vpp drive.
Static: a Lorentzian dip. Dynamic: coupled-mode theory for the energy amplitude a of the ring mode,
    da/dt = (j(w_r - w_L) - 1/tau) a - j mu s_in,   s_out = s_in - j mu a,   1/tau = w/(2 Q_L),  mu^2 = w/Q_c.
More reverse bias moves the resonance to the red; the laser sits on the blue side of the resonance.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-16/
"""
import math
import sys

import numpy as np

C0, LAM = 2.998e8, 1550e-9
QI, QL = 15000.0, 8000.0
QC = 1 / (1 / QL - 1 / QI)
EFF, VPP = 50e-12, 2.0                       # resonance shift per volt (m/V), drive swing (V)
W0 = 2 * math.pi * C0 / LAM
FWHM_M, FWHM_HZ = LAM / QL, C0 / LAM / QL
GAM, MU = W0 / (2 * QL), math.sqrt(W0 / QC)


# ---------------------------------------------------------------------------------------------------------
# Part A. The static operating point (Worked Example 20.2)
# ---------------------------------------------------------------------------------------------------------
def tmin():
    return ((1 / QI - 1 / QC) / (1 / QI + 1 / QC)) ** 2


def T_static(det_m):
    """Through-port transmission for a laser det_m (m) from the resonance (laser minus resonance)."""
    return 1 - (1 - tmin()) / (1 + (2 * det_m / FWHM_M) ** 2)


def T_of_V(V, det_mid):
    """Transmission at drive voltage V (0 ... VPP); det_mid is the laser's detuning from the mid-swing resonance."""
    return T_static(det_mid - EFF * (V - VPP / 2))


def er_il(det_mid):
    lo, hi = sorted((T_of_V(0.0, det_mid), T_of_V(VPP, det_mid)))
    return 10 * math.log10(hi / lo), -10 * math.log10((hi + lo) / 2)


def detuning_for_il(il_db=3.0):
    lo, hi = -400e-12, 0.0                      # laser on the blue side: negative detuning
    for _ in range(80):
        m = (lo + hi) / 2
        if er_il(m)[1] > il_db: hi = m
        else: lo = m
    return (lo + hi) / 2


# ---------------------------------------------------------------------------------------------------------
# Part B. Small-signal bandwidth against detuning (Section 20.8)
# ---------------------------------------------------------------------------------------------------------
def dlam_to_dw(dl):
    return -2 * math.pi * C0 * dl / LAM ** 2


def small_signal(f, det_m):
    """|H(f)/H(0)| of the output power for a small sinusoidal shift of the resonance."""
    d0 = dlam_to_dw(-det_m)
    a0 = -1j * MU / (GAM - 1j * d0); s0 = 1 - 1j * MU * a0
    c1 = np.conj(s0) * a0 * MU / 2; Wf = 2 * np.pi * np.asarray(f)
    Hf = c1 / (1j * Wf - 1j * d0 + GAM) + np.conj(c1) / (1j * Wf + 1j * d0 + GAM)
    H0 = c1 / (-1j * d0 + GAM) + np.conj(c1) / (1j * d0 + GAM)
    return np.abs(Hf / H0)


def bw3db(det_m):
    f = np.linspace(1e8, 200e9, 20000); h = small_signal(f, det_m)
    idx = np.where(h < 1 / math.sqrt(2))[0]
    return (f[idx[0]] if len(idx) else float("nan")), f[np.argmax(h)], 20 * math.log10(h.max())


# ---------------------------------------------------------------------------------------------------------
# Part C. NRZ eyes from the coupled-mode equation (RK4), with ideal 2 V steps
# ---------------------------------------------------------------------------------------------------------
def prbs7(n=127, seed=0x7F):
    s, out = seed, []
    for _ in range(n):
        b = ((s >> 6) ^ (s >> 5)) & 1; s = ((s << 1) | b) & 0x7F; out.append(b)
    return np.array(out)


def nrz_trace(det_mid, rate, spb=64, rise_ps=0.0):
    """Output power over two passes of a PRBS7 pattern (bit 1 = 2 V, bit 0 = 0 V), sampled spb times per bit.
    rise_ps: optional 10-90 % rise time of the drive (a first-order filter), 0 for ideal steps."""
    bits = np.tile(prbs7(), 2); dt = 1 / rate / spb
    V = np.repeat(bits * VPP, spb).astype(float)
    if rise_ps > 0:
        tau = rise_ps * 1e-12 / 2.197; a = dt / (tau + dt); y = V[0]
        for k in range(len(V)):
            y += a * (V[k] - y); V[k] = y
    amp = -1j * MU / (GAM - 1j * dlam_to_dw(-(det_mid - EFF * (V[0] - VPP / 2))))
    out = np.empty(len(V))
    for k in range(len(V)):
        dw = dlam_to_dw(-(det_mid - EFF * (V[k] - VPP / 2)))
        f = lambda a: (1j * dw - GAM) * a - 1j * MU
        k1 = f(amp); k2 = f(amp + dt / 2 * k1); k3 = f(amp + dt / 2 * k2); k4 = f(amp + dt * k3)
        amp = amp + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[k] = abs(1 - 1j * MU * amp) ** 2
    return bits, out, dt


def eye_opening(bits, p, spb, det_mid):
    """Inner vertical eye opening at the best sampling phase, as a fraction of the static swing (second pass only)."""
    n = len(bits) // 2; ones, zeros = bits[n:] == 1, bits[n:] == 0
    seg = p[n * spb:].reshape(n, spb)
    lo, hi = sorted((T_of_V(0.0, det_mid), T_of_V(VPP, det_mid)))
    best = max((seg[ones, k].min() - seg[zeros, k].max(), k) for k in range(spb))
    return best[0] / (hi - lo), best[1] / spb


# ---------------------------------------------------------------------------------------------------------
# Part D. PAM4 on the Lorentzian, and pre-distortion (Section 20.9)
# ---------------------------------------------------------------------------------------------------------
def pam4_eyes(volts, det_mid):
    t = [T_of_V(v, det_mid) for v in volts]
    e = np.diff(t); return e / e.mean()


def predistort(det_mid):
    """Drive voltages whose transmissions are equally spaced between those at 0 and VPP (bisection on T(V))."""
    t0, t3 = T_of_V(0.0, det_mid), T_of_V(VPP, det_mid); out = [0.0]
    for frac in (1 / 3, 2 / 3):
        target = t0 + frac * (t3 - t0); lo, hi = 0.0, VPP
        for _ in range(60):
            m = (lo + hi) / 2
            if (T_of_V(m, det_mid) - target) * (t3 - t0) < 0: lo = m
            else: hi = m
        out.append((lo + hi) / 2)
    return out + [VPP]


def main(plot=True):
    print("Part A. The operating point")
    det = detuning_for_il(3.0); er, il = er_il(det)
    print(f"  Q_c {QC:.0f}; dip {-10*math.log10(tmin()):.1f} dB; linewidth {FWHM_M*1e12:.1f} pm = {FWHM_HZ/1e9:.1f} GHz; "
          f"photon lifetime {QL/W0*1e12:.2f} ps")
    print(f"  for 3.0 dB insertion loss the laser sits {abs(det)*1e12:.0f} pm ({abs(det)/FWHM_M:.2f} linewidths) blue of the "
          f"resonance; extinction {er:.2f} dB at 2 Vpp")

    print("Part B. Small-signal bandwidth")
    for x in (0.05, 0.30, abs(det) / FWHM_M, 1.0):
        bw, fpk, pk = bw3db(-x * FWHM_M); e, i = er_il(-x * FWHM_M)
        print(f"  {x:.2f} linewidths blue: f3dB {bw/1e9:.1f} GHz (peak {pk:.1f} dB at {fpk/1e9:.1f} GHz); extinction {e:.2f} dB, loss {i:.2f} dB")

    print("Part C. NRZ eyes (ideal 2 V steps)")
    eyes = {}
    for rate in (25e9, 50e9):
        for x in (abs(det) / FWHM_M, 0.30):
            bits, p, dt = nrz_trace(-x * FWHM_M, rate)
            op, ph = eye_opening(bits, p, 64, -x * FWHM_M); eyes[(rate, round(x, 2))] = (bits, p, dt)
            print(f"  {rate/1e9:.0f} Gb/s, laser {x:.2f} linewidths blue: inner eye {op*100:.0f} % of the static swing (best phase {ph:.2f} of a bit)")
    bits, p, dt = nrz_trace(det, 50e9, rise_ps=12.0)
    op, _ = eye_opening(bits, p, 64, det)
    print(f"  50 Gb/s at the operating point with a 12 ps driver rise time: inner eye {op*100:.0f} %")

    print("Part D. PAM4")
    eq = [0.0, VPP / 3, 2 * VPP / 3, VPP]; e = pam4_eyes(eq, det)
    print(f"  equally spaced drive: eyes {e[0]:.2f} : {e[1]:.2f} : {e[2]:.2f} (bottom : middle : top); smallest-eye penalty "
          f"{10*math.log10(1/e.min()):.1f} dB on top of PAM4's 4.8 dB")
    pd = predistort(det)
    print(f"  pre-distorted drive: {', '.join(f'{v:.2f}' for v in pd)} V -> eyes {', '.join(f'{v:.2f}' for v in pam4_eyes(pd, det))}")

    if plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
        for ax, rate in zip(axs[:2], (25e9, 50e9)):
            bits, p, dt = eyes[(rate, round(abs(det) / FWHM_M, 2))]
            n = len(bits) // 2; spb = 64; seg = p[n * spb:]
            for k in range(n - 2):
                tr = seg[k * spb: k * spb + 2 * spb]
                ax.plot(np.arange(len(tr)) / spb, tr, color="C0", lw=0.5, alpha=0.4)
            ax.set_xlabel("Time (bits)"); ax.set_ylabel("Transmission"); ax.set_title(f"C. NRZ eye, {rate/1e9:.0f} Gb/s"); ax.grid(alpha=0.3)
        V = np.linspace(0, VPP, 201)
        axs[2].plot(V, [T_of_V(v, det) for v in V], color="k", lw=1)
        axs[2].plot(eq, [T_of_V(v, det) for v in eq], "o", color="C3", label="equally spaced")
        axs[2].plot(pd, [T_of_V(v, det) for v in pd], "s", color="C0", label="pre-distorted")
        axs[2].set_xlabel("Drive (V)"); axs[2].set_ylabel("Transmission"); axs[2].legend(); axs[2].grid(alpha=0.3); axs[2].set_title("D. PAM4 levels")
        fig.tight_layout(); fig.savefig("lab16_ringmod.png", dpi=150)
        print("saved lab16_ringmod.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
