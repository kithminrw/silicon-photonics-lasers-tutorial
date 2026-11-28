# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 17: gain, saturation, noise and patterning of a semiconductor optical amplifier (Open-Photonics, Chapter 28).

Run it from a terminal:
    python lab17_soa.py              # prints every checkpoint and saves lab17_soa.png
    python lab17_soa.py --no-plot    # numbers only

NumPy only (Matplotlib for the figure). The amplifier is the one of Worked Example 28.1: small-signal modal gain
35 /cm, internal loss 5 /cm, saturation power 12 mW, n_sp = 2, gain recovery 200 ps; Part D adds the slab-coupled,
large-mode amplifier of Figure 24.13.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-17/
"""
import math
import sys

import numpy as np

G0, AI, PSAT, NSP, TAU = 35.0, 5.0, 12.0, 2.0, 200e-12     # /cm, /cm, mW, -, s
H, C, LAM = 6.626e-34, 2.998e8, 1550e-9


# ---------------------------------------------------------------------------------------------------------
# Part A. Gain and saturation (Section 28.2)
# ---------------------------------------------------------------------------------------------------------
def amp(pin_mw, L_mm, g0=G0, ai=AI, psat=PSAT, n=400):
    """Output power (mW) for input powers pin_mw (mW): dP/dz = (g0/(1 + P/psat) - ai) P, RK4 along the length."""
    dz = L_mm * 0.1 / n
    P = np.atleast_1d(np.asarray(pin_mw, float)).copy()
    f = lambda p: (g0 / (1 + p / psat) - ai) * p
    for _ in range(n):
        k1 = f(P); k2 = f(P + dz / 2 * k1); k3 = f(P + dz / 2 * k2); k4 = f(P + dz * k3)
        P = P + dz / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return P


def p3db(L_mm, **kw):
    """Small-signal gain (dB), and the input and output powers (dBm) where the gain is 3 dB below it."""
    g_ss = 10 * math.log10(amp(1e-6, L_mm, **kw)[0] / 1e-6)
    lo, hi = -40.0, 30.0
    for _ in range(60):
        m = (lo + hi) / 2; p = 10 ** (m / 10)
        if 10 * math.log10(amp(p, L_mm, **kw)[0] / p) > g_ss - 3: lo = m
        else: hi = m
    return g_ss, lo, lo + g_ss - 3


# ---------------------------------------------------------------------------------------------------------
# Part B. Noise figure and ASE (Section 28.3)
# ---------------------------------------------------------------------------------------------------------
def noise_figure(G, g0=G0, ai=AI, nsp=NSP):
    """F = 2 n_sp (G - 1)/G x g/(g - alpha_i), small-signal, as a linear ratio."""
    return 2 * nsp * (G - 1) / G * g0 / (g0 - ai)


def ase_dbm_per_01nm(G, g0=G0, ai=AI, nsp=NSP):
    """ASE power density at the output, in dBm per 0.1 nm: n_sp h nu (G - 1) g/(g - alpha_i) x bandwidth."""
    hnu = H * C / LAM; B = C * 0.1e-9 / LAM ** 2
    return 10 * math.log10(nsp * hnu * (G - 1) * g0 / (g0 - ai) * B * 1e3)


# ---------------------------------------------------------------------------------------------------------
# Part C. Patterning (Section 28.4): the carrier-reservoir model of the integrated gain h = ln G
# ---------------------------------------------------------------------------------------------------------
BITS = np.array([0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0])


def reservoir(pin_mw, dt, h0, tau=TAU, psat=PSAT):
    """dh/dt = (h0 - h)/tau - Pin (e^h - 1)/E_sat, with E_sat = P_sat tau (four Euler sub-steps per sample)."""
    esat = psat * 1e-3 * tau
    h = np.empty_like(pin_mw); hh = h0
    for k, p in enumerate(pin_mw):
        for _ in range(4):
            hh += dt / 4 * ((h0 - hh) / tau - p * 1e-3 * (math.exp(hh) - 1) / esat)
        h[k] = hh
    return h


def pattern(rate=10e9, p1=1.0, p0=0.05, spb=64, tau=TAU):
    """Gain (dB) and output (mW) for the bit pattern BITS at `rate`, with raised-cosine edges (30 % of a bit)."""
    dt = 1 / rate / spb
    nrz = np.repeat(BITS.astype(float), spb)
    k = np.arange(-spb // 2, spb // 2 + 1); w = np.cos(np.pi * k / (0.6 * spb)) ** 2 * (np.abs(k) < 0.3 * spb)
    nrz = np.convolve(nrz, w / w.sum(), mode="same")
    pin = p0 + (p1 - p0) * nrz
    h0 = (G0 - AI) * 0.1                                       # ln of the 1 mm small-signal gain
    pre = np.full(40 * spb, pin.mean())                        # settle at the average power first
    h = reservoir(np.r_[pre, pin], dt, h0, tau)[len(pre):]
    return np.arange(len(pin)) * dt, pin, 10 * np.log10(np.exp(h)), pin * np.exp(h), h0


def main(plot=True):
    print("Part A. Gain and saturation")
    rows = {}
    for L in (0.5, 1.0, 2.0):
        g, pin, pout = p3db(L); rows[L] = (g, pin, pout)
        print(f"  {L:.1f} mm: small-signal gain {g:.1f} dB; -3 dB point at {pin:.1f} dBm in, {pout:.1f} dBm out")

    print("Part B. Noise figure and ASE")
    G1 = 10 ** (rows[1.0][0] / 10)
    print(f"  1 mm, n_sp = 2: F = {10*math.log10(noise_figure(G1)):.2f} dB; limit at high gain "
          f"{10*math.log10(2*NSP*G0/(G0-AI)):.2f} dB; ideal amplifier (n_sp = 1, no loss) {10*math.log10(2*(G1-1)/G1):.2f} dB")
    ase = ase_dbm_per_01nm(G1); pout = -15 + rows[1.0][0]
    print(f"  ASE {ase:.1f} dBm per 0.1 nm; a -15 dBm input leaves at {pout:.1f} dBm: OSNR {pout-ase:.1f} dB in 0.1 nm")
    print(f"  with a 3 dB input coupler: F = {10*math.log10(noise_figure(G1))+3:.2f} dB")

    print("Part C. Patterning at 10 Gb/s")
    t, pin, gdb, pout_t, h0 = pattern()
    print(f"  small-signal gain {10*math.log10(math.exp(h0)):.1f} dB; with 1 mW ones and 0.05 mW zeros the gain swings "
          f"{gdb.min():.1f} to {gdb.max():.1f} dB; mean output {pout_t.mean():.1f} mW")
    for tau in (100e-12, 1e-9):
        _, _, g2, _, _ = pattern(tau=tau)
        print(f"  gain recovery {tau*1e12:.0f} ps: gain {g2.min():.1f} to {g2.max():.1f} dB")

    print("Part D. A large-mode amplifier (Figure 24.13)")
    gam_ratio, psat_ratio, ai2 = 0.69 / 7.32, 10.3, 0.5
    g02, psat2 = G0 * gam_ratio, PSAT * psat_ratio
    L2 = math.log(20) / (g02 - ai2) * 10                      # mm for the same 13 dB
    g, pin2, pout2 = p3db(L2, g0=g02, ai=ai2, psat=psat2)
    F2 = 10 * math.log10(noise_figure(10 ** (g / 10), g0=g02, ai=ai2))
    print(f"  modal gain {g02:.2f} /cm, loss {ai2} /cm, P_sat {psat2:.0f} mW: {L2:.1f} mm for {g:.1f} dB; "
          f"-3 dB output {pout2:.1f} dBm (against {rows[1.0][2]:.1f} dBm); F = {F2:.2f} dB")

    if plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a, b, c) = plt.subplots(1, 3, figsize=(12, 3.6))
        pin_dbm = np.linspace(-30, 15, 181)
        for L, col in ((0.5, "C0"), (1.0, "C1"), (2.0, "C2")):
            po = amp(10 ** (pin_dbm / 10), L)
            a.plot(10 * np.log10(po), 10 * np.log10(po) - pin_dbm, color=col, label=f"{L} mm")
            a.plot(rows[L][2], rows[L][0] - 3, "o", color=col)
        a.set_xlabel("Output power (dBm)"); a.set_ylabel("Gain (dB)"); a.legend(); a.grid(alpha=0.3); a.set_title("A. gain and saturation")
        Ls = np.linspace(0.05, 3, 200); Gs = np.exp((G0 - AI) * Ls * 0.1)
        b.plot(10 * np.log10(Gs), 10 * np.log10(noise_figure(Gs)), label="n_sp = 2, 5 /cm loss")
        b.plot(10 * np.log10(Gs), 10 * np.log10(2 * (Gs - 1) / Gs), "--", label="ideal")
        b.set_xlabel("Small-signal gain (dB)"); b.set_ylabel("Noise figure (dB)"); b.legend(); b.grid(alpha=0.3); b.set_title("B. noise figure")
        c.plot(t * 1e9, gdb, color="C3"); c.axhline(10 * math.log10(math.exp(h0)), ls=":", color="grey")
        c.set_xlabel("Time (ns)"); c.set_ylabel("Gain (dB)"); c.grid(alpha=0.3); c.set_title("C. patterning, 10 Gb/s")
        fig.tight_layout(); fig.savefig("lab17_soa.png", dpi=150)
        print("saved lab17_soa.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
