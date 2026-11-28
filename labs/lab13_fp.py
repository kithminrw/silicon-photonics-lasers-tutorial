# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 13: Fabry-Perot cavities (Open-Photonics, Chapter 13 Section 13.5, with Chapters 24 and 28).

Run it from a terminal:
    python lab13_fp.py              # prints every checkpoint and saves lab13_fp.png
    python lab13_fp.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. Lengths are in micrometres and wavelengths in micrometres inside
the script; the printout converts to nm, pm and dB/cm.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-13/
"""
import math
import sys

import numpy as np

LAM0 = 1.55                         # centre wavelength (um)
C_UM = 2.998e14                     # speed of light (um/s)


def db_per_cm(alpha_per_um):
    """Power loss coefficient (1/um) to dB/cm."""
    return 10 * math.log10(math.e) * alpha_per_um * 1e4


def per_um(db_cm):
    """dB/cm to a power loss coefficient (1/um)."""
    return db_cm / (10 * math.log10(math.e)) * 1e-4


# ---------------------------------------------------------------------------------------------------------
# Part A. The Airy function (Section 13.5)
# ---------------------------------------------------------------------------------------------------------
def airy(phi, R1, R2, A=1.0):
    """Power transmission and reflection of a Fabry-Perot cavity.

    R1, R2: power reflectances of the mirrors; A: single-pass power transmission (above 1 for gain);
    phi: round-trip phase (radians). Light enters through mirror 1.
    """
    rho = math.sqrt(R1 * R2) * A                          # what one round trip returns, in amplitude squared
    s2 = np.sin(np.asarray(phi) / 2) ** 2
    den = (1 - rho) ** 2 + 4 * rho * s2
    T = (1 - R1) * (1 - R2) * A / den
    R = ((math.sqrt(R1) - math.sqrt(R2) * A) ** 2 + 4 * math.sqrt(R1 * R2) * A * s2) / den
    return T, R


def finesse(rho):
    """FSR / FWHM of an Airy peak, exactly; None when the fringes never fall to half the peak."""
    x = (1 - rho) / (2 * math.sqrt(rho))
    return math.pi / (2 * math.asin(x)) if x <= 1 else None


def finesse_approx(rho):
    """The high-finesse approximation pi sqrt(rho) / (1 - rho)."""
    return math.pi * math.sqrt(rho) / (1 - rho)


def fwhm(x, y):
    """Full width at half maximum of the highest peak of y(x), with linear interpolation at both sides."""
    i = int(np.argmax(y)); h = y[i] / 2
    j = i
    while j > 0 and y[j] > h: j -= 1
    k = i
    while k < len(y) - 1 and y[k] > h: k += 1
    xl = x[j] + (h - y[j]) * (x[j + 1] - x[j]) / (y[j + 1] - y[j])
    xr = x[k - 1] + (h - y[k - 1]) * (x[k] - x[k - 1]) / (y[k] - y[k - 1])
    return xr - xl


def part_a():
    print("Part A. The Airy function")
    for R in (0.30, 0.70, 0.95):
        F = finesse(R)
        ph = np.linspace(-math.pi, math.pi, 200001)
        T, Rr = airy(ph, R, R)
        Fn = 2 * math.pi / fwhm(ph, T)
        print(f"  R1 = R2 = {R:.2f}, lossless: finesse {F:.2f} (approximation {finesse_approx(R):.2f}, numerical FWHM {Fn:.2f});"
              f" T_max {T.max():.4f}, T_min {T.min():.4f}; largest |T + R - 1| {np.abs(T + Rr - 1).max():.1e}")
    T, _ = airy(0.0, 0.95, 0.60)
    print(f"  R1 = 0.95, R2 = 0.60, lossless: peak transmission {100 * T:.1f} %;", end="")
    T, _ = airy(0.0, 0.60, 0.60)
    print(f" R1 = R2 = 0.60: {100 * T:.1f} %")
    print("  Chapter 13 (Figure 13.5a and the fp demo): finesse 2.3, 8.7 and 61.2; 33 % and 100 %")


# ---------------------------------------------------------------------------------------------------------
# Part B. A cavity between two Bragg mirrors (Worked Example 13.3)
# ---------------------------------------------------------------------------------------------------------
NEFF, NG = 2.446, 4.18               # 500 x 220 nm silicon strip at 1550 nm (Chapter 6)
PER = LAM0 / (2 * NEFF)              # Bragg period (um): 316.8 nm
KAP = 12.6e-3                        # grating coupling coefficient (1/um), Worked Example 13.2


def delta(lam, alpha=0.0):
    """Detuning from the Bragg condition (1/um); a power loss alpha (1/um) makes it complex. In the matrices
    below the forward amplitude grows as exp(+j delta z), so a loss adds +j alpha/2."""
    neff = NEFF - (NG - NEFF) * (lam - LAM0) / LAM0        # n_eff falls with wavelength at the rate n_g sets
    return 2 * np.pi * neff / lam - np.pi / PER + 0.5j * alpha


def section(length, d, kap):
    """Coupled-mode matrix of a uniform section: maps the forward and backward amplitudes (A, B) at its end
    to those at its start. kap = 0 gives plain propagation."""
    s = np.sqrt(kap ** 2 - d ** 2 + 0j)
    ch = np.cosh(s * length)
    small = np.abs(s) < 1e-12                                  # sinh(sL)/s -> L as s -> 0 (exactly on the Bragg wavelength)
    sh = np.where(small, length, np.sinh(s * length) / np.where(small, 1, s))
    return np.array([[ch - 1j * d * sh, -1j * kap * sh], [1j * kap * sh, ch + 1j * d * sh]])


def mul(A, B):
    return np.einsum("ij...,jk...->ik...", A, B)


def dbr_cavity(lam, N=300, Ns=316, alpha=0.0):
    """Two N-period gratings around a spacer of Ns whole periods plus a quarter-wave (pi/2 in each direction),
    which puts one resonance on the Bragg wavelength. Returns the power transmission."""
    d = delta(lam, alpha)
    G = section(N * PER, d, KAP)
    S = section(Ns * PER, d, 0.0)
    Q = np.array([[np.full_like(d, -1j), 0 * d], [0 * d, np.full_like(d, 1j)]])
    M = mul(mul(mul(G, S), Q), G)
    return 1 / np.abs(M[0, 0]) ** 2                            # B = 0 beyond the far end: t = 1 / M11


def part_b():
    print("Part B. A cavity between two Bragg mirrors")
    N, Ns = 300, 316
    Lg = N * PER
    R = math.tanh(KAP * Lg) ** 2
    Lp = math.tanh(KAP * Lg) / (2 * KAP)                       # penetration depth at the Bragg wavelength
    Ls = (Ns + 0.5) * PER
    Leff = Ls + 2 * Lp
    fsr = LAM0 ** 2 / (2 * NG * Leff)
    F = finesse(R)
    print(f"  one grating: {N} periods, {Lg:.1f} um, kappa L {KAP * Lg:.3f}, R {100 * R:.1f} %; penetration {Lp:.1f} um")
    print(f"  spacer {Ls:.2f} um, L_eff {Leff:.1f} um, FSR {1e3 * fsr:.3f} nm, finesse {F:.2f},"
          f" FWHM {1e6 * fsr / F:.0f} pm, Q {LAM0 / (fsr / F):.0f}, photon lifetime {1e12 * LAM0 / (fsr / F) * LAM0 / (2 * math.pi * C_UM):.2f} ps")
    lam = LAM0 + np.linspace(-4e-3, 4e-3, 32001)
    T = dbr_cavity(lam, N, Ns)
    pk = [i for i in range(1, len(T) - 1) if T[i] > T[i - 1] and T[i] >= T[i + 1] and T[i] > 0.5]
    near = sorted(pk, key=lambda i: abs(lam[i] - LAM0))[:3]
    print("  transfer matrices: resonances at " + ", ".join(f"{1e3 * (lam[i] - LAM0):+.3f}" for i in sorted(near)) + " nm from 1550 nm")
    for i in sorted(near, key=lambda i: abs(lam[i] - LAM0))[:2]:
        lf = lam[i] + np.linspace(-6e-4, 6e-4, 24001)
        Tf = dbr_cavity(lf, N, Ns)
        print(f"    peak at {1e3 * (lf[np.argmax(Tf)] - LAM0):+.3f} nm: T {Tf.max():.4f}, FWHM {1e6 * fwhm(lf, Tf):.1f} pm")
    a = per_um(2.0)
    A = math.exp(-a * Leff)
    Ta, _ = airy(0.0, R, R, A)
    lf = LAM0 + np.linspace(-6e-4, 6e-4, 24001)
    Tl = dbr_cavity(lf, N, Ns, alpha=a)
    print(f"  with 2 dB/cm: Airy over L_eff: A {A:.4f}, rho {R * A:.4f}, T_max {Ta:.3f}, finesse {finesse(R * A):.2f};"
          f" transfer matrices with the loss in every section: T_max {Tl.max():.3f}, FWHM {1e6 * fwhm(lf, Tl):.0f} pm")
    print("  Worked Example 13.3: 33.1 um, 166.4 um, 1.73 nm, F 8.50, 203 pm, Q 7600, 6.3 ps; 204 pm; +-1.66 nm, 0.44 nm wide;"
          " 96 % and F 8.3")
    return dict(lam=lam, T=T, R=R, Leff=Leff, fsr=fsr)


# ---------------------------------------------------------------------------------------------------------
# Part C. Measuring loss from the fringes (the Fabry-Perot method)
# ---------------------------------------------------------------------------------------------------------
NG_INP, R_FACET = 3.6, 0.30          # a cleaved III-V waveguide (Chapter 24)


def measure_cleaved(L, alpha_db, R=R_FACET, rng=None, noise=0.005, drift=0.1, step=0.5e-6, span=2e-3):
    """A simulated transmission sweep of a waveguide L um long between two cleaved facets.

    The light coupled in drifts by +-`drift` across the sweep (fibre movement) and the detector adds `noise`
    (relative, Gaussian). Returns wavelength (um) and detected power (arbitrary units)."""
    rng = rng or np.random.default_rng(1)
    lam = LAM0 + np.arange(-span / 2, span / 2, step)
    phi = 4 * np.pi * NG_INP * L / lam                        # round-trip phase (only its variation matters)
    T, _ = airy(phi, R, R, math.exp(-per_um(alpha_db) * L))
    eta = 0.3 * (1 + drift * np.sin(2 * np.pi * (lam - lam[0]) / span + 0.7))
    return lam, eta * T * (1 + noise * rng.standard_normal(lam.size))


def fringe_contrast(lam, P, fsr, smooth=9):
    """Contrast K = (Pmax - Pmin)/(Pmax + Pmin) in each whole free spectral range of a sweep, after a short
    moving average (noise would otherwise make the peaks higher and the valleys lower)."""
    Ps = np.convolve(P, np.ones(smooth) / smooth, mode="same")
    edges = np.arange(lam[0] + smooth * (lam[1] - lam[0]), lam[-1] - fsr, fsr)
    K, lc = [], []
    for e in edges:
        m = (lam >= e) & (lam < e + fsr)
        hi, lo = Ps[m].max(), Ps[m].min()
        K.append((hi - lo) / (hi + lo)); lc.append(e + fsr / 2)
    return np.array(lc), np.array(K)


def rho_from_contrast(K):
    """Invert K = 2 rho / (1 + rho^2)."""
    return (1 - np.sqrt(1 - K ** 2)) / K


def part_c():
    print("Part C. Loss from the fringes")
    rng = np.random.default_rng(7)
    L, a_true = 2000.0, 3.0
    fsr = LAM0 ** 2 / (2 * NG_INP * L)
    lam, P = measure_cleaved(L, a_true, rng=rng)
    lc, K = fringe_contrast(lam, P, fsr)
    rho = rho_from_contrast(K)
    a = np.log(R_FACET / rho) / L
    adb = np.array([db_per_cm(x) for x in a])
    rho_true = R_FACET * math.exp(-per_um(a_true) * L)
    print(f"  {L / 1000:.0f} mm waveguide, R = {R_FACET}, true loss {a_true} dB/cm: FSR {1e6 * fsr:.0f} pm, rho {rho_true:.4f},"
          f" contrast {2 * rho_true / (1 + rho_true ** 2):.4f}")
    print(f"  {len(K)} fringes: contrast {K.mean():.4f} +- {K.std():.4f}; loss {adb.mean():.2f} +- {adb.std():.2f} dB/cm"
          f" (coupling drifting by +-10 % across the sweep)")
    for dr, nz, what in ((0.0, 0.005, "no drift, same noise"), (0.1, 0.0, "drift, no noise")):
        lam2, P2 = measure_cleaved(L, a_true, rng=np.random.default_rng(7), noise=nz, drift=dr)
        _, K2 = fringe_contrast(lam2, P2, fsr)
        a2 = np.array([db_per_cm(x) for x in np.log(R_FACET / rho_from_contrast(K2)) / L])
        print(f"    {what}: loss {a2.mean():.2f} +- {a2.std():.2f} dB/cm")
    for Rg in (0.28, 0.32):
        print(f"  assuming R = {Rg} instead of {R_FACET}: loss {db_per_cm(np.mean(np.log(Rg / rho)) / L):.2f} dB/cm")
    Ls = np.array([1000.0, 2000.0, 4000.0]); lnr = []
    for Lx in Ls:
        lam_x, P_x = measure_cleaved(Lx, a_true, rng=rng)
        _, Kx = fringe_contrast(lam_x, P_x, LAM0 ** 2 / (2 * NG_INP * Lx))
        lnr.append(np.mean(np.log(rho_from_contrast(Kx))))
    slope, icpt = np.polyfit(Ls, lnr, 1)
    print(f"  three lengths (1, 2, 4 mm): ln rho = ln R - alpha L gives loss {db_per_cm(-slope):.2f} dB/cm and R {math.exp(icpt):.3f}"
          f" without knowing R")
    return dict(lam=lam, P=P, lc=lc, adb=adb, a_true=a_true)


# ---------------------------------------------------------------------------------------------------------
# Part D. Gain from the fringes below threshold (Hakki-Paoli)
# ---------------------------------------------------------------------------------------------------------
L_LAS, R_LAS, ALPHA_I = 400.0, 0.32, 15e-4      # the laser of Worked Example 24.1 (um, -, 1/um)
LAMP, ZERO = 1.550, 30e-3                        # gain peak and the distance to zero modal gain (um), as in the laser demo


def net_gain(lam, net_peak):
    """Net modal gain Gamma g - alpha_i (1/um): parabolic modal gain with its zero 30 nm from the peak."""
    gpk = net_peak + ALPHA_I
    return gpk * (1 - ((lam - LAMP) / ZERO) ** 2) - ALPHA_I


def emission(lam, net_peak):
    """Spontaneous emission leaving one facet below threshold, filtered by the cavity (arbitrary units).
    Only the shape matters; the smooth envelope does not change the peak-to-valley ratio of a fringe."""
    G = np.exp(net_gain(lam, net_peak) * L_LAS)
    phi = 4 * np.pi * NG_INP * L_LAS / lam
    rho = R_LAS * G
    return np.exp(-((lam - LAMP) / 0.04) ** 2) / ((1 - rho) ** 2 + 4 * rho * np.sin(phi / 2) ** 2)


def hakki_paoli(lam, P, fsr):
    """Net modal gain (1/um) from the peak-to-valley ratio r of each fringe: R G = (sqrt r - 1)/(sqrt r + 1)."""
    out_l, out_g = [], []
    start = lam[0]
    while start + 1.5 * fsr < lam[-1]:
        m = (lam >= start) & (lam < start + fsr)
        i = np.argmax(np.where(m, P, -1))                         # the peak in this free spectral range
        w = (lam > lam[i] - fsr / 2) & (lam < lam[i] + fsr / 2)
        r = P[i] / P[w].min()
        rg = (math.sqrt(r) - 1) / (math.sqrt(r) + 1)
        out_l.append(lam[i]); out_g.append(math.log(rg / R_LAS) / L_LAS)
        start += fsr
    return np.array(out_l), np.array(out_g)


def osa(lam, P, res):
    """What an optical spectrum analyser with a Gaussian filter of FWHM `res` (um) records."""
    if res <= 0:
        return P
    dl = lam[1] - lam[0]
    x = np.arange(-3 * res, 3 * res + dl, dl)
    k = np.exp(-4 * math.log(2) * (x / res) ** 2)
    return np.convolve(P, k / k.sum(), mode="same")


def part_d():
    print("Part D. Gain from the fringes (Hakki-Paoli)")
    fsr = LAM0 ** 2 / (2 * NG_INP * L_LAS)
    am = math.log(1 / R_LAS ** 2) / (2 * L_LAS)
    lam = LAMP + np.arange(-0.012, 0.012, 0.2e-6)
    print(f"  laser of Worked Example 24.1: FSR {1e6 * fsr:.0f} pm; threshold when the net modal gain reaches alpha_m = {1e4 * am:.1f} /cm")
    res_all = {}
    for npk in (10e-4, 20e-4, 26e-4):
        P = emission(lam, npk)
        rho = R_LAS * math.exp(npk * L_LAS)
        F = finesse(rho)
        line = f"  net gain at the peak {1e4 * npk:4.0f} /cm: rho {rho:.3f}, fringe FWHM {1e6 * fsr / F:5.1f} pm;"
        res_all[npk] = {}
        for res in (0.0, 0.02e-3, 0.06e-3, 0.1e-3):
            lg, gg = hakki_paoli(lam, osa(lam, P, res), fsr)
            j = np.argmin(np.abs(lg - LAMP))
            res_all[npk][res] = (lg, gg)
            line += f"  {'exact' if res == 0 else f'{1e6 * res:.0f} pm'} {1e4 * gg[j]:5.1f}"
        print(line + "  /cm")
    print("  (true values 10, 20 and 26 /cm; OSA resolutions 20, 60 and 100 pm)")
    return dict(res=res_all, am=am)


# ---------------------------------------------------------------------------------------------------------
def main(plot=True):
    part_a()
    b = part_b()
    c = part_c()
    d = part_d()
    if not plot:
        return
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.5))
    ph = np.linspace(-1.3, 1.3, 3001)
    for R, col in ((0.3, "tab:orange"), (0.7, "tab:green"), (0.95, "tab:blue")):
        ax[0, 0].plot(ph, airy(2 * np.pi * ph, R, R)[0], color=col, label=f"R = {R}, F = {finesse(R):.1f}")
    ax[0, 0].set(xlabel="round-trip phase / 2π", ylabel="transmission", title="(a) the Airy function, lossless mirrors")
    ax[0, 0].legend(fontsize=8)
    lam = b["lam"]
    phi = 4 * np.pi * NG * b["Leff"] * (1 / lam - 1 / LAM0)
    ax[0, 1].plot(1e3 * (lam - LAM0), airy(phi, b["R"], b["R"])[0], "--", color="tab:orange", label="Airy with L_eff")
    ax[0, 1].plot(1e3 * (lam - LAM0), b["T"], color="tab:blue", label="transfer matrices")
    ax[0, 1].set(xlabel="wavelength − 1550 nm (nm)", ylabel="transmission", title="(b) cavity between two Bragg mirrors")
    ax[0, 1].legend(fontsize=8)
    m = c["lam"] < c["lam"][0] + 0.6e-3
    ax[1, 0].plot(1e3 * (c["lam"][m] - LAM0), c["P"][m], color="tab:blue", lw=0.8)
    ax[1, 0].set(xlabel="wavelength − 1550 nm (nm)", ylabel="detected power (a.u.)", title="(c) fringes of a 2 mm cleaved waveguide")
    t = ax[1, 0].inset_axes([0.62, 0.62, 0.35, 0.33])
    t.plot(1e3 * (c["lc"] - LAM0), c["adb"], "o", ms=3, color="tab:red"); t.axhline(c["a_true"], color="k", lw=0.8, ls=":")
    t.set_title("loss per fringe (dB/cm)", fontsize=7); t.tick_params(labelsize=6)
    for npk, col in ((10e-4, "tab:green"), (20e-4, "tab:orange"), (26e-4, "tab:red")):
        lg, gg = d["res"][npk][0.0]
        x = np.linspace(lg[0], lg[-1], 300)
        ax[1, 1].plot(1e3 * (x - LAMP), 1e4 * net_gain(x, npk), color=col, lw=0.8)
        ax[1, 1].plot(1e3 * (lg - LAMP), 1e4 * gg, "o", ms=2.5, color=col, label=f"{1e4 * npk:.0f} /cm, exact")
        lg, gg = d["res"][npk][0.06e-3]
        ax[1, 1].plot(1e3 * (lg - LAMP), 1e4 * gg, "x", ms=3, color=col)
    ax[1, 1].axhline(1e4 * d["am"], color="k", ls=":", lw=0.8)
    ax[1, 1].set(xlabel="wavelength − 1550 nm (nm)", ylabel="net modal gain (/cm)",
                 title="(d) Hakki–Paoli: dots exact, crosses with a 60 pm OSA")
    ax[1, 1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("lab13_fp.png", dpi=150)
    print("Saved the figure as lab13_fp.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
