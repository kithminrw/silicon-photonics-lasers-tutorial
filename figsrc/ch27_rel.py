"""Figures and worked-example numbers for Section 27.9 (reliability: how lasers age and fail).

Run from the repository root:  python -I -X utf8 figsrc/ch27_rel.py
NumPy and Matplotlib only. Prints every number the section and its captions quote, then writes
assets/figs/ch27_rel_*.svg.

  ch27_rel_sites      where lasers fail: an edge emitter, an EML, an oxide VCSEL, and lasers on silicon (bonded and
                      grown), with the failure sites marked (schematic)
  ch27_rel_bathtub    the bathtub curve built from a mixture of distributions (weak sub-population, random failures,
                      lognormal wear-out), with and without burn-in; and the lognormal wear-out hazard for three spreads
  ch27_rel_ageing     synthetic life-test data: operating-current drift under APC at three junction temperatures,
                      sqrt(t) fits extrapolated to the +20 % end-of-life line, and a lognormal plot of the times to failure
  ch27_rel_arrhenius  acceleration factor against stress temperature for several activation energies; and the Arrhenius
                      fit of the median lives of ch27_rel_ageing, extrapolated to 40 degC

Worked examples: 27.2 (acceleration factors 85 -> 40 degC), 27.3 (zero-failure FIT bound, chi-square),
27.4 (drift -> end of life -> lognormal -> FIT), 27.5 (self-heating on SOI and life, the laser of Section 27.6).
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *
from matplotlib.patches import Circle, Ellipse

KB = 8.617333e-5          # Boltzmann constant, eV/K
C2K = 273.15
H_YR = 8766.0             # hours per year (365.25 days)
HEAT = "#E08A3A"


# ====================================================================== statistics helpers
def af_T(Ea, T_use, T_stress):
    """Arrhenius acceleration factor between two temperatures in degC."""
    return np.exp(Ea / KB * (1.0 / (T_use + C2K) - 1.0 / (np.asarray(T_stress, float) + C2K)))


def Phi(z):
    return 0.5 * np.vectorize(math.erfc)(-np.asarray(z, float) / math.sqrt(2.0))


def phi(z):
    z = np.asarray(z, float)
    return np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def inv_Phi(p):
    """Inverse standard normal CDF (bisection on erfc; accurate to ~1e-10)."""
    p = np.atleast_1d(np.asarray(p, float)); out = np.empty_like(p)
    for i, pi in enumerate(p):
        lo, hi = -10.0, 10.0
        for _ in range(80):
            m = 0.5 * (lo + hi)
            if 0.5 * math.erfc(-m / math.sqrt(2)) < pi: lo = m
            else: hi = m
        out[i] = 0.5 * (lo + hi)
    return out


def ln_hazard(t, t50, s):
    """Hazard (per hour) of a lognormal life distribution with median t50 (h) and shape s."""
    z = np.log(np.asarray(t, float) / t50) / s
    return phi(z) / (s * np.asarray(t, float) * (1.0 - Phi(z)))


def ln_cdf(t, t50, s):
    return Phi(np.log(np.asarray(t, float) / t50) / s)


# ====================================================================== Worked Examples 27.2 and 27.3
def worked_examples_23():
    print("== Worked Example 27.2: acceleration from 85 degC stress to 40 degC use")
    for Ea in (0.4, 0.5, 0.7):
        a = float(af_T(Ea, 40, 85))
        print(f"  Ea {Ea} eV: AF = {a:.2f}; 5000 h at 85 degC = {5000*a:,.0f} h = {5000*a/H_YR:.1f} years at 40 degC")
    a = float(af_T(0.7, 40, 85))
    print(f"  with 1.5 x current and n = 2 as well: x{1.5**2:.2f} -> AF {a*2.25:.1f} (Ea 0.7)")
    print("== Worked Example 27.3: zero failures, chi-square upper bound (2 degrees of freedom)")
    for CL in (0.6, 0.9):
        print(f"  chi2({CL:.0%}; 2) = -2 ln(1 - CL) = {-2*math.log(1-CL):.3f}")
    N, t = 25, 2000
    for Ea in (None, 0.5, 0.7):
        a = 1.0 if Ea is None else float(af_T(Ea, 40, 85))
        T = N * t * a
        b60, b90 = -math.log(0.4) / T * 1e9, -math.log(0.1) / T * 1e9
        print(f"  {N} x {t} h at 85 degC, Ea {Ea}: {T:.3g} equivalent device-hours -> lambda < {b60:,.0f} FIT (60 %), {b90:,.0f} FIT (90 %)")
    for Ea in (0.5, 0.7):
        n = -math.log(0.4) / 100e-9 / (5000 * float(af_T(Ea, 40, 85)))
        print(f"  to show 100 FIT at 60 % with 5000 h at 85 degC and Ea {Ea}: {n:.0f} lasers")
    print(f"  100 FIT = MTTF {1e9/100:.0e} h = {1e9/100/H_YR:,.0f} years; 1e5 lasers at 100 FIT: {1e5*100e-9*H_YR:.1f} failures per year")


# ====================================================================== synthetic life test (ageing figure, WE 27.4)
EA_TRUE, T50_USE_TRUE, SIG_TRUE, M_EXP, EOL = 0.60, 1.0e6, 0.60, 0.5, 20.0   # model behind the synthetic data
T_STRESS = (70.0, 85.0, 100.0)
N_DEV, T_TEST = 12, 5000.0
T_USE = 40.0


def life_test():
    """Synthetic APC life test: dI_op/I_op0 (%) = A_i t^m with A_i lognormal; fit each laser, extrapolate to +20 %."""
    rng = np.random.default_rng(35)
    times = np.arange(250.0, T_TEST + 1, 250.0)
    out = {}
    for T in T_STRESS:
        t50 = T50_USE_TRUE / float(af_T(EA_TRUE, T_USE, T))
        A_med = EOL / t50 ** M_EXP
        A = A_med * np.exp(SIG_TRUE * M_EXP * rng.standard_normal(N_DEV))     # TTF = (EOL/A)^(1/m) -> shape SIG_TRUE
        drift = A[:, None] * times[None, :] ** M_EXP + 0.12 * rng.standard_normal((N_DEV, times.size))
        x = times ** M_EXP
        A_fit = (drift * x).sum(1) / (x * x).sum()                                 # least squares through the origin
        ttf = (EOL / A_fit) ** (1 / M_EXP)
        mu, s = np.log(ttf).mean(), np.log(ttf).std(ddof=1)
        out[T] = dict(times=times, drift=drift, A_fit=A_fit, ttf=ttf, mu=mu, s=s)
        print(f"  {T:.0f} degC: drift at {T_TEST:.0f} h median {np.median(drift[:, -1]):.2f} % "
              f"(range {drift[:, -1].min():.2f}-{drift[:, -1].max():.2f} %); median TTF {math.exp(mu):,.0f} h, sigma {s:.2f}")
    # Arrhenius fit of ln(t50) against 1/kT
    xk = np.array([1 / (KB * (T + C2K)) for T in T_STRESS]); y = np.array([out[T]["mu"] for T in T_STRESS])
    Ea_fit, c = np.polyfit(xk, y, 1)
    mu_use = c + Ea_fit / (KB * (T_USE + C2K))
    sig = float(np.sqrt(np.mean([out[T]["s"] ** 2 for T in T_STRESS])))
    t50_use = math.exp(mu_use)
    print(f"  Arrhenius fit: Ea = {Ea_fit:.3f} eV; t50 at {T_USE:.0f} degC = {t50_use:,.0f} h = {t50_use/H_YR:.0f} years; pooled sigma {sig:.2f}")
    return out, Ea_fit, c, t50_use, sig


def worked_example_4(out, Ea_fit, t50_use, sig):
    print("== Worked Example 27.4: from drift to FIT")
    d85 = float(np.median(out[85.0]["drift"][:, -1]))
    t85 = T_TEST * (EOL / d85) ** 2
    print(f"  hand calculation: median drift {d85:.1f} % in {T_TEST:.0f} h at 85 degC -> +{EOL:.0f} % at {T_TEST:.0f} x ({EOL:.0f}/{d85:.1f})^2 = {t85:,.0f} h")
    a = float(af_T(Ea_fit, T_USE, 85))
    print(f"  AF(85 -> 40 degC, Ea {Ea_fit:.2f} eV) = {a:.1f} -> {t85*a:,.0f} h = {t85*a/H_YR:.0f} years at 40 degC")
    print(f"  lognormal MTTF = t50 exp(sigma^2/2) = {t50_use*math.exp(sig**2/2):,.0f} h")
    for yr in (5, 10, 15, 20, 25):
        t = yr * H_YR
        z = math.log(t / t50_use) / sig
        print(f"  year {yr:2d}: z = {z:.2f}, phi(z) = {float(phi(z)):.3g}, F = {float(ln_cdf(t, t50_use, sig))*1e6:.1f} ppm, hazard = {float(ln_hazard(t, t50_use, sig))*1e9:.1f} FIT")
    F10 = float(ln_cdf(10 * H_YR, t50_use, sig))
    print(f"  average wear-out failure rate over the first 10 years: -ln(1-F)/t = {-math.log(1-F10)/(10*H_YR)*1e9:.2f} FIT")
    for Tj in (60.0, 70.0, 80.0):
        t50 = t50_use / float(af_T(Ea_fit, T_USE, Tj))
        print(f"  same lasers at a {Tj:.0f} degC junction: t50 = {t50:,.0f} h = {t50/H_YR:.1f} years; "
              f"wear-out at year 10 = {float(ln_hazard(10*H_YR, t50, sig))*1e9:,.0f} FIT, F(10 yr) = {float(ln_cdf(10*H_YR, t50, sig))*100:.2f} %")
    return t85


def side_numbers():
    """Numbers quoted in the text of Section 27.9 outside the worked examples."""
    print("== Other numbers in Section 27.9")
    for V in (200.0, -50.0, 1000.0):     # human-body model: 100 pF through 1.5 kOhm (JS-001)
        print(f"  HBM {V:+.0f} V: peak {abs(V)/1500*1e3:.0f} mA, energy {0.5*100e-12*V*V*1e6:.3f} uJ, time constant {1500*100e-12*1e9:.0f} ns")
    for d_um in (6.0, 4.0):
        A = math.pi * (d_um / 2 * 1e-4) ** 2
        print(f"  VCSEL {d_um:.0f} um aperture at 8 mA: J = {8e-3/A/1e3:.1f} kA/cm2")
    print(f"  J ratio 6 -> 4 um = {(6/4)**2:.2f}; with life ~ J^-2: x{(4/6)**4:.2f}")
    hv = 1.23984 / 1.55
    Pabs, Vb = 5e-3, 2.0
    Iph = Pabs / hv
    print(f"  EAM at 1550 nm: {1/hv:.2f} A/W at unity efficiency; {Pabs*1e3:.0f} mW absorbed -> {Iph*1e3:.2f} mA; "
          f"heat = P_abs + I_ph V_b = {Pabs*1e3:.1f} + {Iph*Vb*1e3:.1f} = {(Pabs+Iph*Vb)*1e3:.1f} mW")
    for tdd in (2.8e8, 7.3e6, 1e6):
        print(f"  TDD {tdd:.1e} cm-2: mean spacing {1/math.sqrt(tdd)*1e4:.2f} um")
    qd = 6e10
    print(f"  QD density {qd:.0e} cm-2: spacing {1/math.sqrt(qd)*1e7:.0f} nm; dots per dislocation at 7.3e6: {qd/7.3e6:,.0f}")


# ====================================================================== Worked Example 27.5 (self-heating and life)
V0, RS, T0, ITH0, P_OUT = 0.9, 6.0, 60.0, 0.020, 0.020    # the laser of Figure 27.5 / Worked Example 27.1
ETA = P_OUT / (0.1 - ITH0 * math.exp(80.0 * (0.1 * (V0 + RS * 0.1) - P_OUT) / T0))


def i_for_power(Z, delta=0.0):
    """Current for P_OUT under APC, with the threshold raised by a fraction delta through ageing."""
    Is = np.linspace(0.02, 0.6, 290001)
    dT = Z * (Is * (V0 + RS * Is) - P_OUT)
    f = ETA * (Is - ITH0 * (1 + delta) * np.exp(dT / T0)) - P_OUT
    k = int(np.argmax(f >= 0))
    return (Is[k], dT[k]) if f[k] >= 0 else (None, None)


def worked_example_5():
    print("== Worked Example 27.5: self-heating on SOI and life (heat sink 70 degC, 20 mW under APC)")
    Ths, res = 70.0, {}
    for Z in (20.0, 40.0, 80.0):
        I, dT = i_for_power(Z)
        lo, hi = 0.0, 5.0
        for _ in range(60):
            m = 0.5 * (lo + hi); Ie, _ = i_for_power(Z, m)
            if Ie is None or Ie > 1.2 * I: hi = m
            else: lo = m
        Ie, dTe = i_for_power(Z, lo)
        res[Z] = (I, dT, lo)
        print(f"  Z_th {Z:.0f} K/W: I_op {I*1e3:.1f} mA, P_diss {1e3*(I*(V0+RS*I)-P_OUT):.0f} mW, dT {dT:.1f} K, T_j {Ths+dT:.1f} degC; "
              f"threshold may rise {lo*100:.1f} % before I_op is +20 % ({Ie*1e3:.1f} mA, dT {dTe:.1f} K)")
    I20, dT20, d20 = res[20.0]
    for Z in (40.0, 80.0):
        I, dT, d = res[Z]
        for Ea in (0.5, 0.7):
            arr = math.exp(Ea / KB * (1 / (Ths + dT + C2K) - 1 / (Ths + dT20 + C2K)))
            marg = (d / d20) ** (1 / M_EXP)
            print(f"  Z_th {Z:.0f} vs 20 K/W, Ea {Ea}: Arrhenius x{arr:.2f}, smaller APC margin (sqrt t) x{marg:.2f}, life x{arr*marg:.2f}")


# ====================================================================== Figure: failure sites
def fig_sites():
    fig = plt.figure(figsize=(6.3, 5.0))
    fs = 6.3
    # ---------------- (a) edge-emitting laser (FP or DFB), side view along the cavity
    a = fig.add_axes([0.0, 0.53, 0.49, 0.46]); frameless(a, (-1.6, 11.6), (-1.6, 7.0), equal=False)
    box(a, 0, 0, 10, 2.4, "inp"); box(a, 0, 2.4, 10, 0.55, "q")
    for yq in (2.55, 2.68, 2.81):
        a.plot([0, 10], [yq, yq], color=MAT["mqw"], lw=0.7, zorder=3)
    box(a, 0, 2.95, 10, 1.9, "inp"); box(a, 0, 4.85, 10, 0.35, "metal"); box(a, 0, -0.3, 10, 0.3, "metal")
    box(a, -0.25, 0, 0.25, 4.85, "#7FB7C9", z=3); box(a, 10, 0, 0.25, 4.85, "#B9A0D6", z=3)
    arrow(a, (10.3, 2.68), (11.5, 2.68), col=RED, lw=1.4, ms=7)
    a.add_patch(Ellipse((10.1, 2.68), 0.9, 0.9, fc=HEAT, alpha=0.55, ec="none", zorder=4))
    label(a, 5, 1.2, "n-InP", fs=fs); label(a, 5, 3.9, "p-InP", fs=fs)
    callout(a, (10.15, 2.3), (9.2, -1.2), "1 facet: oxidation, COD", fs=fs, ha="center")
    callout(a, (-0.12, 4.3), (1.3, 6.3), "2 coating (AR/HR)", fs=fs, ha="center")
    callout(a, (4.0, 2.68), (3.2, -1.2), "3 active region: non-radiative\ndefects grow (dark lines in GaAs)", fs=fs, ha="center")
    callout(a, (6.6, 3.4), (7.2, 6.3), "4 p-dopant diffusion", fs=fs, ha="center")
    panel(a, "a", x=0.0, y=1.0)
    a.text(0.07, 0.995, "FP or DFB edge emitter", transform=a.transAxes, ha="left", va="top", fontsize=6.6, color=INK)
    # ---------------- (b) EML: DFB section, isolation, EAM
    b = fig.add_axes([0.51, 0.53, 0.49, 0.46]); frameless(b, (-1.0, 12.2), (-1.6, 7.0), equal=False)
    box(b, 0, 0, 11, 2.4, "inp"); box(b, 0, 2.95, 11, 1.9, "inp")
    box(b, 0, 2.4, 6.3, 0.55, "q"); box(b, 6.3, 2.4, 4.7, 0.55, "#A99A70")
    for yq in (2.55, 2.68, 2.81):
        b.plot([0, 6.3], [yq, yq], color=MAT["mqw"], lw=0.7, zorder=3)
        b.plot([6.3, 11], [yq, yq], color=VIOLET, lw=0.7, zorder=3)
    for xg in np.arange(0.3, 5.6, 0.35):
        box(b, xg, 3.0, 0.17, 0.2, "q", z=3)
    box(b, 0, 4.85, 5.6, 0.35, "metal"); box(b, 7.1, 4.85, 3.9, 0.35, "metal"); box(b, 0, -0.3, 11, 0.3, "metal")
    box(b, 5.6, 4.2, 1.5, 1.0, "white", z=3)
    b.plot([6.3, 6.3], [2.4, 2.95], color=INK, lw=0.8, ls=(0, (2, 1)), zorder=4)
    arrow(b, (11.0, 2.68), (12.1, 2.68), col=RED, lw=1.1, ms=6)
    b.add_patch(Ellipse((7.2, 2.68), 1.6, 0.9, fc=HEAT, alpha=0.6, ec="none", zorder=4))
    label(b, 2.8, 1.2, "DFB laser (CW)", fs=fs); label(b, 8.9, 1.2, "EAM (reverse bias)", fs=fs)
    callout(b, (6.35, 4.5), (4.4, 6.3), "5 isolation gap", fs=fs, ha="center")
    callout(b, (6.3, 2.5), (5.0, -1.2), "6 laser–modulator junction", fs=fs, ha="center")
    callout(b, (7.5, 3.0), (9.4, 6.3), "7 EAM input: photocurrent\nheating, thermal runaway", fs=fs, ha="center")
    panel(b, "b", x=0.0, y=1.0)
    b.text(0.07, 0.995, "EML", transform=b.transAxes, ha="left", va="top", fontsize=6.6, color=INK)
    # ---------------- (c) oxide-aperture VCSEL cross-section
    c = fig.add_axes([0.0, 0.02, 0.40, 0.49]); frameless(c, (-6.2, 6.6), (-1.0, 9.6), equal=False)
    box(c, -6.0, 0, 12.0, 1.0, "gaas")
    for k in range(9):
        box(c, -3.0, 1.0 + k * 0.32, 6.0, 0.16, "#C8CED8"); box(c, -3.0, 1.16 + k * 0.32, 6.0, 0.16, "#E6E9EF")
    box(c, -6.0, 1.0, 3.0, 0.4, "gaas")
    box(c, -3.0, 3.88, 6.0, 0.6, "#D8DCE3")
    for yq in (4.07, 4.18, 4.29):
        c.plot([-3.0, 3.0], [yq, yq], color=MAT["mqw"], lw=0.7, zorder=3)
    box(c, -3.0, 4.48, 6.0, 0.22, "#B9C6D6")
    poly(c, [(-3.0, 4.48), (-1.0, 4.53), (-1.0, 4.65), (-3.0, 4.70)], "#8E99A8", z=3)
    poly(c, [(3.0, 4.48), (1.0, 4.53), (1.0, 4.65), (3.0, 4.70)], "#8E99A8", z=3)
    for k in range(8):
        box(c, -3.0, 4.70 + k * 0.32, 6.0, 0.16, "#C8CED8"); box(c, -3.0, 4.86 + k * 0.32, 6.0, 0.16, "#E6E9EF")
    box(c, -3.0, 7.26, 1.6, 0.3, "metal"); box(c, 1.4, 7.26, 1.6, 0.3, "metal")
    arrow(c, (0, 7.4), (0, 9.2), col=RED, lw=1.4, ms=7)
    for s in (-1, 1):
        c.add_patch(Ellipse((s * 1.0, 4.45), 0.7, 0.5, fc=HEAT, alpha=0.6, ec="none", zorder=4))
    c.plot([-0.95, -0.55, -0.75, -0.3], [4.4, 4.05, 3.75, 3.3], color=INK, lw=0.7, zorder=5)
    callout(c, (-1.0, 4.6), (-3.6, 8.3), "8 oxide tip: strain,\ndislocations start", fs=fs, ha="center")
    callout(c, (3.0, 5.6), (5.0, 8.4), "9 mesa wall:\nhumidity", fs=fs, ha="center")
    callout(c, (0.0, 4.15), (4.85, 2.0), "10 small area:\nESD", fs=fs, ha="center")
    label(c, -4.6, 2.3, "n-DBR", fs=fs); label(c, -4.4, 4.6, "oxide\naperture", fs=fs)
    label(c, 0, 0.5, "GaAs substrate", fs=fs)
    panel(c, "c", x=0.0, y=1.0)
    c.text(0.07, 0.995, "oxide VCSEL", transform=c.transAxes, ha="left", va="top", fontsize=6.6, color=INK)
    # ---------------- (d) lasers on silicon: bonded (left) and grown QD (right)
    d = fig.add_axes([0.41, 0.02, 0.59, 0.49]); frameless(d, (-0.4, 16.4), (-1.0, 9.6), equal=False)
    box(d, 0, 0, 7.6, 1.6, "sub"); box(d, 0, 1.6, 7.6, 1.6, "ox"); box(d, 0, 3.2, 7.6, 0.3, "ox")
    box(d, 3.3, 3.2, 1.0, 0.45, "si", z=3)
    box(d, 0.6, 3.65, 6.4, 0.12, "bcb", z=3)
    box(d, 0.6, 3.77, 6.4, 0.45, "inp"); box(d, 2.3, 4.22, 3.0, 0.5, "q")
    d.plot([2.3, 5.3], [4.47, 4.47], color=MAT["mqw"], lw=0.8, zorder=4)
    box(d, 2.3, 4.72, 3.0, 1.8, "inp"); box(d, 2.6, 6.52, 2.4, 0.3, "metal")
    box(d, 0.9, 4.22, 1.0, 0.3, "metal"); box(d, 5.7, 4.22, 1.0, 0.3, "metal")
    d.add_patch(Ellipse((3.8, 4.47), 3.0, 0.7, fc=HEAT, alpha=0.4, ec="none", zorder=5))
    arrow(d, (3.8, 4.0), (3.8, 2.3), col=HEAT, lw=1.2, ms=6, z=6)
    for xv in (1.4, 6.1):
        d.add_patch(Ellipse((xv, 3.71), 0.5, 0.14, fc="white", ec=INK, lw=0.4, zorder=6))
    callout(d, (6.1, 3.71), (6.0, 8.0), "11 bond interface:\nvoids, defects", fs=fs, ha="center")
    callout(d, (3.8, 2.4), (1.4, 0.75), "12 BOX: heat (Z$_\\mathrm{th}$)", fs=fs, ha="left")
    callout(d, (2.35, 5.6), (1.2, 8.0), "13 mesa walls", fs=fs, ha="center")
    label(d, 3.8, -0.6, "bonded (no III–V facet)", fs=6.3)
    # grown QD laser
    x0 = 8.6
    box(d, x0, 0, 7.4, 1.4, "sub"); box(d, x0, 1.4, 7.4, 2.2, "gaas")
    box(d, x0, 2.6, 7.4, 0.2, "#C9CEDA"); box(d, x0, 3.6, 7.4, 1.0, "#D8DCE3")
    box(d, x0, 4.6, 7.4, 0.5, "q")
    for xd in np.arange(x0 + 0.25, x0 + 7.3, 0.36):
        d.add_patch(Circle((xd, 4.85), 0.08, fc=MAT["mqw"], ec="none", zorder=4))
    box(d, x0, 5.1, 7.4, 1.4, "#D8DCE3"); box(d, x0, 6.5, 7.4, 0.3, "metal")
    rng = np.random.default_rng(5)
    for k, xs in enumerate(np.linspace(x0 + 0.5, x0 + 6.9, 9)):
        top = 2.6 if k % 3 else 6.4
        y = np.linspace(1.4, top, 20)
        d.plot(xs + 0.18 * np.sin((y - 1.4) * rng.uniform(1.5, 3)), y, color=INK, lw=0.6, alpha=0.8, zorder=3)
    d.plot([x0 + 1.2, x0 + 5.6], [4.55, 4.55], color=INK, lw=1.1, zorder=5)
    d.annotate("14 threading dislocations", xy=(x0 + 2.25, 2.1), xytext=(x0 + 3.7, 0.7), fontsize=fs, color=INK, ha="center", va="center", zorder=9,
               bbox=dict(boxstyle="square,pad=0.15", fc=MAT["sub"], ec="none"), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    callout(d, (x0 + 4.6, 4.55), (x0 + 4.4, 8.0), "15 misfit dislocation\nnear the dots (REDC)", fs=fs, ha="center")
    label(d, x0 + 3.7, -0.6, "grown quantum-dot laser", fs=6.3)
    panel(d, "d", x=0.0, y=1.0)
    d.text(0.05, 0.995, "lasers on silicon", transform=d.transAxes, ha="left", va="top", fontsize=6.6, color=INK)
    note(d, "schematic, not to scale", loc="upper right")
    save(fig, "ch27_rel_sites")


# ====================================================================== Figure: bathtub
P_WEAK, BETA_W, ETA_W, LAM_RAND = 0.01, 0.5, 100.0, 10e-9     # weak sub-population (Weibull), random failures (/h)
BURN_H, BURN_T = 48.0, 100.0                                   # burn-in: 48 h at 100 degC junction


def bathtub_hazard(t, t50, sig, t_shift=0.0):
    """Hazard (per hour) of the mixture: each laser has random (exponential) and wear-out (lognormal) failures; a
    fraction P_WEAK also carries an early (Weibull, beta < 1) failure. t_shift = use-equivalent burn-in age."""
    t = np.asarray(t, float) + t_shift
    Rw = np.exp(-(t / ETA_W) ** BETA_W); fw = (BETA_W / ETA_W) * (t / ETA_W) ** (BETA_W - 1) * Rw
    Rmix = P_WEAK * Rw + (1 - P_WEAK); fmix = P_WEAK * fw
    return fmix / Rmix + LAM_RAND + ln_hazard(t, t50, sig)


def fig_bathtub(t50, sig, Ea_burn):
    t_b = BURN_H * float(af_T(Ea_burn, T_USE, BURN_T))
    print(f"== Bathtub: burn-in {BURN_H:.0f} h at {BURN_T:.0f} degC = {t_b:,.0f} h of use (Ea {Ea_burn:.2f}); "
          f"weak lasers left after it: {math.exp(-(t_b/ETA_W)**BETA_W)*100:.1f} %")
    t = np.logspace(0, 6, 600)
    h0 = bathtub_hazard(t, t50, sig) * 1e9
    h1 = bathtub_hazard(t, t50, sig, t_b) * 1e9
    for tt in (1, 10, 100, 1000, H_YR, 10 * H_YR, 20 * H_YR):
        print(f"  t = {tt:9,.0f} h: {float(bathtub_hazard(tt, t50, sig))*1e9:10,.1f} FIT without, "
              f"{float(bathtub_hazard(tt, t50, sig, t_b))*1e9:8,.1f} FIT with burn-in")
    F0 = 1 - (P_WEAK * math.exp(-(10 * H_YR / ETA_W) ** BETA_W) + 1 - P_WEAK) * math.exp(-LAM_RAND * 10 * H_YR) * (1 - float(ln_cdf(10 * H_YR, t50, sig)))
    print(f"  fraction failed in 10 years without burn-in {F0*100:.2f} %")
    fig = plt.figure(figsize=(6.3, 2.75))
    a = fig.add_axes([0.08, 0.17, 0.50, 0.68])
    a.loglog(t, h0, color=C4, label="no burn-in")
    a.loglog(t, h1, color=C1, ls="--", label=f"after burn-in ({BURN_H:.0f} h at {BURN_T:.0f} °C)")
    a.loglog(t, np.full_like(t, LAM_RAND * 1e9), color=MUTED, lw=0.9, ls=":")
    a.loglog(t, ln_hazard(t, t50, sig) * 1e9, color=C3, lw=0.9, ls=":")
    a.text(3, LAM_RAND * 1e9 * 1.35, f"random, {LAM_RAND*1e9:.0f} FIT", fontsize=6.5, color=MUTED)
    a.text(1.3e5, 0.2, "wear-out\n(lognormal)", fontsize=6.5, color=C3, ha="left")
    a.text(1.6, 3e4, "infant\nmortality", fontsize=6.5, color=C4, ha="left")
    a.set_xlim(1, 1e6); a.set_ylim(0.1, 1e6)
    finish(a, "Operating time (h)", "Failure rate (FIT)", legend=True, loc="upper right")
    top = a.secondary_xaxis("top", functions=(lambda x: x / H_YR, lambda y: y * H_YR))
    top.set_xticks([1, 10, 100]); top.set_xticklabels(["1 yr", "10 yr", "100 yr"]); top.tick_params(labelsize=7)
    tag(a, "a")
    b = fig.add_axes([0.70, 0.17, 0.29, 0.68])
    yrs = np.linspace(0.5, 30, 300)
    for s, col in ((0.5, C1), (sig, C3), (1.0, C2)):
        h = ln_hazard(yrs * H_YR, t50, s) * 1e9
        b.semilogy(yrs, h, color=col, label=(f"σ = {s:.2f} (fit)" if s == sig else f"σ = {s:.1f}"))
        print(f"  t50 {t50:,.0f} h, sigma {s:.2f}: FIT at 10/20 yr = {float(ln_hazard(10*H_YR, t50, s))*1e9:.2f} / {float(ln_hazard(20*H_YR, t50, s))*1e9:.1f}")
    b.set_xlim(0, 30); b.set_ylim(0.01, 1e4)
    for yv in (10, 20):
        b.axvline(yv, color=GRID, lw=1.0, zorder=0)
    finish(b, "Years at 40 °C", "Wear-out rate (FIT)", legend=True, loc="lower right")
    tag(b, "b")
    save(fig, "ch27_rel_bathtub")
    return t_b


# ====================================================================== Figure: ageing (drift, EOL, lognormal plot)
TCOL = {70.0: C1, 85.0: C2, 100.0: C4}


def fig_ageing(out):
    fig = plt.figure(figsize=(6.3, 2.9))
    a = fig.add_axes([0.08, 0.16, 0.48, 0.74])
    for T in T_STRESS:
        r = out[T]; col = TCOL[T]
        for i in range(N_DEV):
            a.plot(r["times"], np.clip(r["drift"][i], 0.05, None), color=col, lw=0.6, alpha=0.45)
        t50 = math.exp(r["mu"]); A50 = EOL / t50 ** M_EXP
        tt = np.logspace(2, math.log10(t50), 100)
        a.plot(tt, A50 * tt ** M_EXP, color=col, lw=1.3, ls="--")
        a.plot([t50], [EOL], "o", color=col, ms=4, zorder=5)
        a.plot([], [], color=col, lw=1.3, label=f"{T:.0f} °C")
    a.axhline(EOL, color=INK, lw=0.9)
    a.text(130, EOL * 1.12, "end of life: I$_\\mathrm{op}$ +20 %", fontsize=6.5, color=INK)
    a.axvspan(100, T_TEST, color=GRID, alpha=0.45, zorder=0, lw=0)
    a.text(700, 0.22, "5000 h test", fontsize=6.5, color=MUTED, ha="center")
    a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(100, 5e5); a.set_ylim(0.15, 40)
    a.set_yticks([0.2, 0.5, 1, 2, 5, 10, 20]); a.set_yticklabels(["0.2", "0.5", "1", "2", "5", "10", "20"])
    finish(a, "Ageing time (h)", "Rise of operating current (%)", legend=True, loc="lower right")
    tag(a, "a")
    b = fig.add_axes([0.67, 0.16, 0.32, 0.74])
    probs = np.array([0.01, 0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95, 0.99])
    for T in T_STRESS:
        r = out[T]; col = TCOL[T]
        tt = np.sort(r["ttf"]); n = tt.size
        pr = (np.arange(1, n + 1) - 0.3) / (n + 0.4)
        b.semilogx(tt, inv_Phi(pr), "o", color=col, ms=3)
        xs = np.logspace(math.log10(tt[0] / 1.5), math.log10(tt[-1] * 1.5), 50)
        b.semilogx(xs, (np.log(xs) - r["mu"]) / r["s"], color=col, lw=1.0)
    b.set_yticks(inv_Phi(probs)); b.set_yticklabels([f"{p*100:g}" for p in probs])
    b.set_ylim(inv_Phi([0.005])[0], inv_Phi([0.995])[0]); b.set_xlim(5e3, 1e6)
    finish(b, "Time to +20 % (h)", "Cumulative failures (%)")
    tag(b, "b")
    save(fig, "ch27_rel_ageing")


# ====================================================================== Figure: Arrhenius
def fig_arrhenius(out, Ea_fit, c, t50_use):
    fig = plt.figure(figsize=(6.3, 2.75))
    a = fig.add_axes([0.08, 0.17, 0.40, 0.70])
    Ts = np.linspace(40, 125, 200)
    for Ea, col in ((0.4, C1), (0.5, C3), (0.7, C2), (1.0, C4)):
        a.semilogy(Ts, af_T(Ea, T_USE, Ts), color=col, label=f"{Ea:.1f} eV")
        v = float(af_T(Ea, T_USE, 85))
        a.plot([85], [v], "o", color=col, ms=3.5)
        a.text(86.5, v * (0.93 if Ea == 0.4 else 1.07), f"{v:.1f}" if v < 100 else f"{v:.0f}", fontsize=6.3, color=col, ha="left",
               va="top" if Ea == 0.4 else "bottom", bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))
    a.axvline(85, color=MUTED, lw=0.7, ls=":")
    a.set_xlim(40, 125); a.set_ylim(1, 3000)
    finish(a, "Stress temperature (°C)", "Acceleration factor vs 40 °C", legend=True, loc="upper left")
    tag(a, "a")
    b = fig.add_axes([0.60, 0.17, 0.38, 0.70])
    xk = lambda T: 1000.0 / (np.asarray(T, float) + C2K)
    for T in T_STRESS:
        r = out[T]; se = r["s"] / math.sqrt(N_DEV)
        b.errorbar([xk(T)], [math.exp(r["mu"])], yerr=[[math.exp(r["mu"]) * (1 - math.exp(-se))], [math.exp(r["mu"]) * (math.exp(se) - 1)]],
                   fmt="o", color=TCOL[T], ms=4, capsize=2, lw=0.9)
    Tline = np.linspace(T_USE, 105, 100)
    b.semilogy(xk(Tline), np.exp(c + Ea_fit / (KB * (Tline + C2K))), color=INK, lw=1.0, ls="--")
    b.plot([xk(T_USE)], [t50_use], "s", color=INK, ms=4)
    b.annotate(f"40 °C: {t50_use/1e6:.1f} × 10$^6$ h\n({t50_use/H_YR:.0f} years)", xy=(xk(T_USE), t50_use), xytext=(3.0, 2.2e6),
               fontsize=6.5, color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.text(3.12, 2.6e4, f"slope: E$_a$ = {Ea_fit:.2f} eV", fontsize=6.5, color=INK)
    b.set_xlim(2.62, 3.25); b.set_ylim(1e4, 5e6)
    b.invert_xaxis()
    finish(b, "1000 / T (K$^{-1}$)", "Median life t$_{50}$ (h)")
    top = b.secondary_xaxis("top", functions=(lambda x: 1000.0 / x - C2K, lambda T: 1000.0 / (T + C2K)))
    top.set_xticks([40, 70, 85, 100]); top.set_xticklabels(["40", "70", "85", "100 °C"]); top.tick_params(labelsize=7)
    tag(b, "b")
    save(fig, "ch27_rel_arrhenius")


if __name__ == "__main__":
    worked_examples_23()
    print("== Synthetic life test (Figure: ageing)")
    out, Ea_fit, c, t50_use, sig = life_test()
    worked_example_4(out, Ea_fit, t50_use, sig)
    worked_example_5()
    side_numbers()
    fig_sites()
    fig_bathtub(t50_use, sig, Ea_fit)
    fig_ageing(out)
    fig_arrhenius(out, Ea_fit, c, t50_use)
