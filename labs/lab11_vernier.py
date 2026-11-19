# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 11: design a Vernier tunable laser in Python (Open-Photonics, Chapter 26).

Run it from a terminal:
    python lab11_vernier.py              # prints every checkpoint and saves lab11_vernier.png
    python lab11_vernier.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. Wavelengths and radii are in micrometres (printed in nm),
heater powers in mW.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-11/
"""
import math
import sys

import numpy as np

# The model of the Chapter 26 demo: a III-V gain chip and two silicon rings closed by a loop mirror
NEFF0, NG, LAM0 = 2.446, 4.18, 1.55   # 500 x 220 nm strip at 1550 nm: effective and group index (Chapter 6)
LOSS_DB_CM = 3.0                      # propagation loss in the rings
A_UM = math.exp(-(LOSS_DB_CM * 100 / 4.343) / 2 * 1e-6)   # field amplitude left after 1 um of ring
L_CAV, NG_CAV = 2500.0, 3.9           # the whole laser cavity: about 2.5 mm, average group index 3.9
DEMO_BAND = (1.5, 1.6)                # the demo looks for lasing modes from 1500 to 1600 nm
P_PI = 26.0                           # mW for a pi phase shift with the TiN heater of Chapter 18 (Table 18.1)


# ---------------------------------------------------------------------------------------------------------
# Part A. One ring: drop response, FSR and linewidth (Chapter 12; Chapter 26, Section 26.5)
# ---------------------------------------------------------------------------------------------------------
def n_eff(lam):
    """Effective index, falling linearly with wavelength so that n_eff - lam dn_eff/dlam = NG."""
    return NEFF0 - (NG - NEFF0) * (lam - LAM0) / LAM0


def drop(lam, R, phase=0.0, k2=0.15):
    """Power transmission to the drop port of an add-drop ring of radius R with two identical couplers.

    k2 is the power coupling of each coupler, so t^2 = 1 - k2 stays in the ring; a is the field left after a round
    trip; a heater adds `phase` to the round-trip phase. On resonance the drop is k2^2 a / (1 - t^2 a)^2.
    """
    L = 2 * np.pi * R
    a = A_UM ** L
    t2 = 1 - k2
    phi = 2 * np.pi * n_eff(lam) * L / lam + phase
    return k2**2 * a / (1 - 2 * t2 * a * np.cos(phi) + t2**2 * a**2)


def fsr(R):
    """Free spectral range lambda^2 / (n_g L) at 1550 nm."""
    return LAM0**2 / (NG * 2 * np.pi * R)


def local_peaks(x, y, floor=0.5):
    """x positions of the local maxima of y that rise above `floor`."""
    i = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]) & (y[1:-1] > floor))[0] + 1
    return x[i]


def fwhm(f, lam_peak, span=0.005, n=20001):
    """Full width at half maximum of the peak of f(lam) near lam_peak, on a fine local grid (um)."""
    x = np.linspace(lam_peak - span, lam_peak + span, n)
    y = f(x)
    above = x[y >= y.max() / 2]
    return above[-1] - above[0]


# ---------------------------------------------------------------------------------------------------------
# Part B. Two rings: the Vernier filter and the gain (Chapter 26, Section 26.5)
# ---------------------------------------------------------------------------------------------------------
def vernier_fsr(R1, R2):
    """FSR_V = FSR1 FSR2 / |FSR1 - FSR2| at 1550 nm."""
    return fsr(R1) * fsr(R2) / abs(fsr(R1) - fsr(R2))


def round_trip(lam, R1, R2, p1=0.0, p2=0.0, k2=0.15):
    """Filter seen by the light in one round trip: through both drop ports to the loop mirror and back."""
    return (drop(lam, R1, p1, k2) * drop(lam, R2, p2, k2)) ** 2


def gain(lam):
    """The demo's gain window: a parabola peaking at 1550 nm and reaching zero 70 nm either side."""
    return np.maximum(0, 1 - ((lam - 1.55) / 0.07) ** 2)


# ---------------------------------------------------------------------------------------------------------
# Part C. Cavity modes and the lasing mode (Chapter 26, Section 26.5)
# ---------------------------------------------------------------------------------------------------------
def cavity_modes(band=DEMO_BAND, L=L_CAV, ngc=NG_CAV):
    """Cavity modes lambda^2/(2 n_g L) apart (0.123 nm), on the demo's grid that starts at 1500 nm.

    Their exact positions depend on the total round-trip phase, which a phase section would set.
    """
    d = LAM0**2 / (2 * ngc * L)
    k = np.arange(math.ceil((band[0] - 1.5) / d), math.floor((band[1] - 1.5) / d) + 1)
    return 1.5 + d * k


def lase(modes, p1=0.0, p2=0.0, R1=10.0, R2=11.0, k2=0.15):
    """Pick the cavity mode with the highest net gain, gain x round-trip filter, as the demo does.

    The rival is the best mode more than 2 nm away, on another pair of ring resonances (another supermode);
    `margin` is its net gain relative to the lasing mode, in dB, and `cavity` the same for the best mode within
    2 nm (a neighbouring cavity mode under the same filter peak).
    """
    filt = round_trip(modes, R1, R2, p1, p2, k2)
    v = gain(modes) * filt
    i = np.argmax(v)
    far = np.abs(modes - modes[i]) > 0.002
    j = np.argmax(np.where(far, v, 0))
    near = ~far
    near[i] = False
    return dict(lam=modes[i], rival=modes[j], margin=10 * np.log10(v[j] / v[i]),
                cavity=10 * np.log10(v[near].max() / v[i]), filter_db=10 * np.log10(filt[i]))


# ---------------------------------------------------------------------------------------------------------
# Part D. Tuning with the two heaters (Chapter 26, Section 26.5; heaters from Chapter 18)
# ---------------------------------------------------------------------------------------------------------
def heater_mw(phase):
    """Heater power (mW) for a round-trip phase shift: P_pi per pi, whatever the ring's length."""
    return phase / np.pi * P_PI


def tuning_map(modes, n=56, R1=10.0, R2=11.0, k2=0.15):
    """Lasing wavelength for an n x n grid of heater phases (cell centres, as in the demo): lam[i, j] for
    ring-1 phase i and ring-2 phase j."""
    ph = 2 * np.pi * (np.arange(n) + 0.5) / n
    D1 = drop(modes[None, :], R1, ph[:, None], k2)        # n x (number of modes)
    D2 = drop(modes[None, :], R2, ph[:, None], k2)
    g = gain(modes)
    lam = np.empty((n, n))
    for i in range(n):
        lam[i] = modes[np.argmax(g * (D1[i] * D2) ** 2, axis=1)]
    return ph, lam


# ---------------------------------------------------------------------------------------------------------
# Part E. Design: radii and coupling for a tuning range and a side-mode margin
# ---------------------------------------------------------------------------------------------------------
def align(lam, R):
    """Heater phase (0 to 2 pi) that puts a resonance of ring R exactly at lam."""
    return (-2 * np.pi * n_eff(lam) * 2 * np.pi * R / lam) % (2 * np.pi)


def suppression(R1, R2, k2, lam_t, grid):
    """Tune both rings onto lam_t and compare its net gain with the best anywhere else under the gain.

    The rival is the highest point of gain x filter more than 2 nm away, on a fine grid: whatever the cavity
    length, some cavity mode sits close to it. Also returns the round-trip filter loss at lam_t and the margin
    over the neighbouring cavity modes, one cavity-mode spacing either side.
    """
    p1, p2 = align(lam_t, R1), align(lam_t, R2)
    peak = gain(lam_t) * round_trip(lam_t, R1, R2, p1, p2, k2)
    v = gain(grid) * round_trip(grid, R1, R2, p1, p2, k2)
    j = np.argmax(np.where(np.abs(grid - lam_t) > 0.002, v, 0))
    d = LAM0**2 / (2 * NG_CAV * L_CAV)
    adj = max(gain(x) * round_trip(x, R1, R2, p1, p2, k2) for x in (lam_t - d, lam_t + d))
    return dict(margin=10 * np.log10(v[j] / peak), rival=grid[j], target=lam_t, cavity=10 * np.log10(adj / peak),
                loss=10 * np.log10(round_trip(lam_t, R1, R2, p1, p2, k2)))


def design(R1, R2, k2, targets, grid):
    """The worst case of `suppression` over the target wavelengths (the weakest margins, the largest loss)."""
    rs = [suppression(R1, R2, k2, lt, grid) for lt in targets]
    worst = max(rs, key=lambda r: r["margin"])
    return dict(worst, cavity=max(r["cavity"] for r in rs), loss=min(r["loss"] for r in rs))


def kappa_for_margin(R1, R2, margin_db, targets, grid, lo=0.01, hi=0.6):
    """Largest power coupling k2 that keeps every rival at least margin_db below the lasing mode at every target.

    Bisection: a weaker coupling narrows the resonances and suppresses the neighbouring supermodes more.
    Returns nan if even the weakest coupling fails: then a rival is a whole Vernier FSR away, and only a
    longer FSR_V (closer radii) can push it out of the gain window.
    """
    if design(R1, R2, lo, targets, grid)["margin"] > -margin_db:
        return float("nan")
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if design(R1, R2, mid, targets, grid)["margin"] <= -margin_db:
            lo = mid
        else:
            hi = mid
    return lo


def main(plot=True):
    print("Lab 11: a Vernier tunable laser, gain chip + two silicon rings + loop mirror (lengths in um)\n")
    R1, R2 = 10.0, 11.0

    # ---- Part A
    F1, F2 = fsr(R1), fsr(R2)
    lam = np.linspace(1.40, 1.70, 600001)                 # 0.5 pm steps
    print("A. One ring at a time: radii 10 and 11 um, n_g = 4.18, 3 dB/cm, power coupling 15 %")
    print(f"   FSR = lambda^2/(n_g 2 pi R) = {1e3 * F1:.3f} and {1e3 * F2:.3f} nm   (Chapter 26: 9.148 and 8.316 nm)")
    for R in (R1, R2):
        pk = local_peaks(lam, drop(lam, R))
        near = pk[(pk > 1.537) & (pk < 1.565)]
        w = fwhm(lambda x: drop(x, R), near[0])
        print(f"   R = {R:.0f} um: resonances at {', '.join(f'{1e3 * p:.2f}' for p in near)} nm; FWHM {1e3 * w:.3f} nm,"
              f" finesse {fsr(R) / w:.1f}, Q {near[0] / w:.0f}, peak drop {10 * np.log10(drop(near[0], R)):.2f} dB")
    print()

    # ---- Part B
    FV = vernier_fsr(R1, R2)
    co = local_peaks(lam, round_trip(lam, R1, R2))
    nu = 299792.458 / (1e3 * co)                           # THz
    print("B. The Vernier filter")
    print(f"   FSR_V = FSR1 FSR2/|FSR1 - FSR2| = {1e3 * FV:.1f} nm, gearing FSR1/(FSR1 - FSR2) = {F1 / (F1 - F2):.1f}"
          "   (Chapter 26: about 91 nm and 11)")
    print(f"   coincidences of the two combs at {', '.join(f'{1e3 * c:.1f}' for c in co)} nm:"
          f" {', '.join(f'{1e3 * d:.1f}' for d in np.diff(co))} nm apart, {', '.join(f'{-d:.2f}' for d in np.diff(nu))} THz")
    print(f"   gain there: {', '.join(f'{gain(c):.2f}' for c in co)}: only one coincidence lies in the gain window\n")

    # ---- Part C
    modes = cavity_modes()
    r0 = lase(modes)
    print("C. Cavity modes and mode selection, heaters off")
    print(f"   {len(modes)} cavity modes from 1500 to 1600 nm, {1e3 * (modes[1] - modes[0]):.3f} nm apart")
    print(f"   lasing at {1e3 * r0['lam']:.2f} nm, round-trip filter loss {r0['filter_db']:.2f} dB   (demo: 1542.26 nm)")
    print(f"   next-best supermode at {1e3 * r0['rival']:.2f} nm, {r0['margin']:.1f} dB   (demo: -21.2 dB)")
    print(f"   nearest rival cavity mode under the same filter peak: {r0['cavity']:.1f} dB\n")

    # ---- Part D
    ph, lmap = tuning_map(modes)
    p2 = np.linspace(0, 2 * np.pi, 2001)
    cut = np.array([lase(modes, 0.0, p)["lam"] for p in p2])
    hop = np.where(np.abs(np.diff(cut)) > 0.002)[0]
    small = hop[np.abs(np.diff(cut)[hop]) < 0.02]           # hops of one ring FSR, not jumps across the gain window
    step = np.median(np.diff(p2[small]))
    res1 = local_peaks(lam, drop(lam, R1))
    res1 = res1[res1 > 1.542][:4]                           # ring 1's resonances from 1542.29 nm upwards
    p_on = [align(r, R2) for r in res1]                     # ring-2 phases that line ring 2 up with each of them
    las = [lase(modes, 0.0, p)["lam"] for p in p_on]
    print("D. Tuning")
    print(f"   56 x 56 heater map: lasing from {1e3 * lmap.min():.1f} to {1e3 * lmap.max():.1f} nm,"
          f" {len(np.unique(np.round(lmap, 7)))} of the {len(modes)} cavity modes reached")
    print(f"   heater tuning FSR/(2 P_pi) with P_pi = {P_PI:.0f} mW: {1e3 * F1 / (2 * P_PI):.3f} nm/mW for ring 1,"
          f" {1e3 * F2 / (2 * P_PI):.3f} nm/mW for ring 2   (Chapter 26: 0.18 nm/mW for a 9.15 nm FSR)")
    print(f"   heating ring 2 alone, the laser hops every {step / np.pi:.3f} pi of phase, {heater_mw(step):.2f} mW,"
          f" a {1e3 * F2 * step / (2 * np.pi):.3f} nm shift of ring 2   (Chapter 26: 0.83 nm, about 5 mW)")
    print(f"   ring 2 heated by {', '.join(f'{heater_mw(p):.1f}' for p in p_on)} mW lines up with ring 1 at"
          f" {', '.join(f'{1e3 * x:.2f}' for x in res1)} nm;")
    print(f"   it lases at {', '.join(f'{1e3 * x:.2f}' for x in las)} nm, hops of"
          f" {', '.join(f'{1e3 * x:.2f}' for x in np.diff(las))} nm   (Chapter 26: 9.15 nm)")
    print(f"   a full Vernier period, {1e3 * FV:.0f} nm, takes 2 P_pi = {2 * P_PI:.0f} mW on ring 2\n")

    # ---- Part E
    grid = np.arange(1.48, 1.62, 5e-6)                      # 5 pm steps across the gain window
    targets = np.arange(1.530, 1.5701, 0.005)
    print("E. Design for 1530-1570 nm: both rings tuned onto each target, rivals anywhere under the gain")
    for k2 in (0.15, 0.10):
        r = design(R1, R2, k2, targets, grid)
        print(f"   10/11 um, k2 = {k2:.2f}: worst rival {r['margin']:.1f} dB at {1e3 * r['rival']:.1f} nm"
              f" (tuned to {1e3 * r['target']:.0f} nm), round-trip filter loss {r['loss']:.2f} dB,"
              f" nearest cavity modes {r['cavity']:.1f} dB")
    print("   largest coupling that keeps every rival 30 dB down over the whole range:")
    designs = []
    for a, b in ((10.0, 11.0), (10.0, 10.9), (7.0, 7.9), (5.0, 5.9)):
        k = kappa_for_margin(a, b, 30, targets, grid)
        designs.append((a, b, k))
        head = (f"   R = {a:.1f}/{b:.1f} um: FSR_V {1e3 * vernier_fsr(a, b):.0f} nm,"
                f" gearing {fsr(a) / (fsr(a) - fsr(b)):.1f}, ")
        if np.isnan(k):
            print(head + "no coupling reaches 30 dB: the next coincidence is inside the gain window")
        else:
            r = design(a, b, k, targets, grid)
            print(head + f"k2 = {k:.3f}, round-trip filter loss {r['loss']:.2f} dB,"
                  f" nearest cavity modes {r['cavity']:.1f} dB")
    print()

    if plot:
        make_figure(modes, r0, lmap, p2, cut, grid, targets, designs)


def make_figure(modes, r0, lmap, p2, cut, grid, targets, designs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 3, figsize=(14, 8))
    # (a) the two rings' drop responses near 1550 nm
    x = np.linspace(1.535, 1.565, 6001)
    ax[0, 0].plot(1e3 * x, 10 * np.log10(drop(x, 10.0)), color="tab:orange", label="ring 1, R = 10 µm")
    ax[0, 0].plot(1e3 * x, 10 * np.log10(drop(x, 11.0)), color="tab:blue", label="ring 2, R = 11 µm")
    ax[0, 0].set(ylim=(-30, 2), xlabel="wavelength (nm)", ylabel="drop (dB)", title="(a) two rings, $\\kappa^2$ = 0.15")
    ax[0, 0].legend(fontsize=8, loc="lower right")
    # (b) the Vernier filter (in dB) and the gain over a wide band
    x = np.linspace(1.43, 1.67, 240001)
    ax[0, 1].plot(1e3 * x, 10 * np.log10(round_trip(x, 10.0, 11.0)), color="tab:green", lw=0.8)
    ax[0, 1].set(ylim=(-60, 3), xlabel="wavelength (nm)", ylabel="round-trip filter $(D_1D_2)^2$ (dB)",
                 title="(b) Vernier filter and gain, heaters off")
    tw = ax[0, 1].twinx()
    tw.plot(1e3 * x, gain(x), "k--", lw=1)
    tw.set(ylim=(0, 1.05), ylabel="gain (relative, dashed)")
    # (c) zoom on the lasing peak with the cavity modes
    x = np.linspace(r0["lam"] - 0.001, r0["lam"] + 0.001, 801)
    ax[0, 2].plot(1e3 * x, gain(x) * round_trip(x, 10.0, 11.0), color="tab:green", label="gain × filter")
    sel = np.abs(modes - r0["lam"]) < 0.001
    v = gain(modes[sel]) * round_trip(modes[sel], 10.0, 11.0)
    ax[0, 2].vlines(1e3 * modes[sel], 0, v, color="tab:blue", lw=1.2, label="cavity modes")
    ax[0, 2].vlines(1e3 * r0["lam"], 0, v.max(), color="tab:red", lw=2.2, label=f"lasing, {1e3 * r0['lam']:.2f} nm")
    ax[0, 2].set(ylim=(0, None), xlabel="wavelength (nm)", ylabel="net gain (relative)", title="(c) cavity modes under the peak")
    ax[0, 2].legend(fontsize=8, loc="upper right")
    # (d) tuning map against the two heater powers
    pw = heater_mw(np.array([0, 2 * np.pi]))
    im = ax[1, 0].imshow(1e3 * lmap.T, origin="lower", extent=(pw[0], pw[1], pw[0], pw[1]), cmap="turbo",
                         vmin=1500, vmax=1600, interpolation="nearest")
    fig.colorbar(im, ax=ax[1, 0], label="lasing wavelength (nm)")
    ax[1, 0].set(xlabel="ring 1 heater (mW)", ylabel="ring 2 heater (mW)", title="(d) tuning map")
    # (e) ring 2's heater alone
    ax[1, 1].plot(heater_mw(p2), 1e3 * cut, ".", ms=1.5, color="tab:blue")
    ax[1, 1].set(xlabel="ring 2 heater (mW), ring 1 off", ylabel="lasing wavelength (nm)",
                 title="(e) one heater: hops of one ring-1 FSR")
    # (f) design: rival margin against coupling
    ks = np.linspace(0.02, 0.4, 20)
    for (a, b, k), col in zip(designs, ("tab:blue", "tab:green", "tab:orange", "tab:red")):
        ax[1, 2].plot(ks, [-design(a, b, kk, targets, grid)["margin"] for kk in ks], color=col, label=f"{a:g} / {b:g} µm")
    ax[1, 2].axhline(30, color="grey", ls=":", lw=0.8)
    ax[1, 2].set(xlabel="power coupling $\\kappa^2$", ylabel="worst rival suppression (dB)",
                 title="(f) design: 1530–1570 nm", ylim=(0, None))
    ax[1, 2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("lab11_vernier.png", dpi=150)
    print("Saved the figure as lab11_vernier.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
