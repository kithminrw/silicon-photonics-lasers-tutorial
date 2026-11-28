# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 15: self-heating and thermal roll-over of a laser on silicon (Open-Photonics, Chapters 24 and 27).

Run it from a terminal:
    python lab15_heating.py              # prints every checkpoint and saves lab15_heating.png
    python lab15_heating.py --no-plot    # numbers only

NumPy only (Matplotlib for the figure). The laser is the model of Figure 27.5: threshold 20 mA without heating,
V = 0.9 V + 6 ohm x I, T0 = 60 K, and a slope efficiency chosen so that at 100 mA and 80 K/W it emits the 20 mW of
Worked Example 27.1.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-15/
"""
import math
import sys

import numpy as np

ITH0, V0, RS, T0 = 20e-3, 0.9, 6.0, 60.0          # A, V, ohm, K
I_REF, P_REF, Z_REF = 100e-3, 20e-3, 80.0          # the operating point of Worked Example 27.1
DGAIN, DMODE = 0.48, 0.1                           # gain-peak and single-mode drift (nm/K), Worked Example 27.1


def calibrate():
    """Slope efficiency (W/A) that puts the laser at 20 mW at 100 mA with Z_th = 80 K/W, self-consistently."""
    P = P_REF
    dT = Z_REF * (I_REF * (V0 + RS * I_REF) - P)
    return P / (I_REF - ITH0 * math.exp(dT / T0))


ETA = calibrate()


# ---------------------------------------------------------------------------------------------------------
# Part A. One operating point, solved self-consistently (Section 27.6)
# ---------------------------------------------------------------------------------------------------------
def operate(I, Z, T_extra=0.0, iters=200):
    """Output power (W) and temperature rise (K) at current I (A) with thermal impedance Z (K/W).

    The heat sink may be T_extra above the 25 C reference. Fixed-point iteration, damped: the threshold depends on
    the temperature, the temperature on the dissipated power, and the power on the threshold."""
    dT = 0.0
    for _ in range(iters):
        Ith = ITH0 * math.exp((dT + T_extra) / T0)
        P = max(0.0, ETA * (I - Ith))
        dT_new = Z * (I * (V0 + RS * I) - P)
        if abs(dT_new - dT) < 1e-9:
            break
        dT = 0.5 * dT + 0.5 * dT_new
    return P, dT


def part_a():
    print("Part A. One operating point")
    print(f"  slope efficiency calibrated to Worked Example 27.1: {ETA:.4f} W/A")
    P, dT = operate(I_REF, Z_REF)
    Ith = ITH0 * math.exp(dT / T0)
    print(f"  100 mA, 80 K/W: {1e3 * P:.2f} mW, dissipating {1e3 * (I_REF * (V0 + RS * I_REF) - P):.0f} mW, {dT:.2f} K hot;"
          f" threshold {1e3 * Ith:.2f} mA, {100 * (Ith / ITH0 - 1):.0f} % above its cold value;"
          f" gain peak +{DGAIN * dT:.1f} nm, single mode +{DMODE * dT:.1f} nm")
    print("  Worked Example 27.1: 20 mW, 130 mW, 10.4 K, 19 %, about 5 nm and 1 nm")


# ---------------------------------------------------------------------------------------------------------
# Part B. L-I curves and roll-over (Figure 27.5b)
# ---------------------------------------------------------------------------------------------------------
def li_curve(Z, T_extra=0.0, Imax=0.7, n=701):
    I = np.linspace(0, Imax, n)
    P = np.array([operate(i, Z, T_extra)[0] for i in I])
    return I, P


def part_b():
    print("Part B. L-I curves and roll-over")
    out = {}
    for Z in (0.0, 40.0, 80.0, 160.0):
        I, P = li_curve(Z)
        k = int(np.argmax(P))
        roll = k < len(I) - 1
        out[Z] = (I, P)
        print(f"  Z_th {Z:5.0f} K/W: " + (f"peak {1e3 * P[k]:5.1f} mW at {1e3 * I[k]:4.0f} mA, {operate(I[k], Z)[1]:5.1f} K hot there"
                                         if roll else f"still rising at {1e3 * I[-1]:.0f} mA ({1e3 * P[-1]:.0f} mW)"))
    print("  Figure 27.5b: at 80 K/W the output rolls over at 78 mW near 420 mA; at 40 K/W it keeps rising")
    return out


# ---------------------------------------------------------------------------------------------------------
# Part C. A hotter heat sink
# ---------------------------------------------------------------------------------------------------------
def part_c():
    print("Part C. Heat-sink temperature (Z_th = 80 K/W)")
    out = {}
    for Ths in (25.0, 55.0, 85.0):
        I, P = li_curve(Z_REF, T_extra=Ths - 25.0)
        k = int(np.argmax(P))
        P100 = operate(I_REF, Z_REF, Ths - 25.0)[0]
        out[Ths] = (I, P)
        print(f"  heat sink {Ths:3.0f} C: {1e3 * P100:5.1f} mW at 100 mA; maximum {1e3 * P[k]:5.1f} mW at {1e3 * I[k]:4.0f} mA")
    return out


# ---------------------------------------------------------------------------------------------------------
# Part D. What a thermal shunt buys
# ---------------------------------------------------------------------------------------------------------
def part_d():
    print("Part D. What halving Z_th buys at 85 C")
    for Z in (80.0, 40.0):
        I, P = li_curve(Z, T_extra=60.0)
        k = int(np.argmax(P))
        # current needed for 20 mW at 85 C, if reachable
        need = next((i for i, p in zip(I, P) if p >= 20e-3), None)
        txt = f"20 mW at {1e3 * need:.0f} mA ({operate(need, Z, 60.0)[1]:.1f} K hot)" if need is not None else "never reaches 20 mW"
        print(f"  Z_th {Z:3.0f} K/W: maximum {1e3 * P[k]:5.1f} mW; {txt}")


def main(plot=True):
    part_a()
    b = part_b()
    c = part_c()
    part_d()
    if not plot:
        return
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for Z, col in zip(b, ("k", "tab:green", "tab:blue", "tab:red")):
        I, P = b[Z]; ax[0].plot(1e3 * I, 1e3 * P, color=col, label=f"{Z:.0f} K/W")
    P, dT = operate(I_REF, Z_REF); ax[0].plot([100], [1e3 * P], "ko", ms=4)
    ax[0].set(xlabel="current (mA)", ylabel="output (mW)", title="(a) self-heating, heat sink 25 °C", ylim=(0, 160)); ax[0].legend(fontsize=8)
    for Ths, col in zip(c, ("tab:blue", "tab:orange", "tab:red")):
        I, P = c[Ths]; ax[1].plot(1e3 * I, 1e3 * P, color=col, label=f"{Ths:.0f} °C")
    ax[1].set(xlabel="current (mA)", ylabel="output (mW)", title="(b) Z_th = 80 K/W, three heat sinks"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig("lab15_heating.png", dpi=150)
    print("Saved the figure as lab15_heating.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
