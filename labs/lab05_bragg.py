# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 5: Bragg gratings with transfer matrices (Open-Photonics, Chapter 13).

Run it from a terminal:
    python lab05_bragg.py              # prints every checkpoint and saves lab05_bragg.png
    python lab05_bragg.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. All lengths are in micrometres.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-05/
"""
import sys

import numpy as np

# The grating of Worked Examples 13.1 and 13.2, also the defaults of the chapter's demo
NEFF, NG = 2.446, 4.18      # effective and group index of a 500 x 220 nm silicon strip at 1550 nm (Chapter 6)
LAM0 = 1.55                 # design wavelength
PERIOD = LAM0 / (2 * NEFF)  # first-order Bragg period, 0.3168 um
KAPPA = 12.6e-3             # coupling coefficient, per um (12.6 /mm)
N_PER = 300                 # number of periods


def n_eff(lam):
    """Effective index of the unperturbed waveguide, linear in wavelength with slope set by the group index.

    n_g = n_eff - lam dn_eff/dlam, so dn_eff/dlam = -(n_g - n_eff)/lam: the same model as the chapter's demo.
    """
    return NEFF - (NG - NEFF) * (lam - LAM0) / LAM0


def dn_for_kappa(kappa, lam=LAM0):
    """Index step that gives the coupling coefficient kappa: kappa = 2 dn / lam for a square-wave grating.

    A step dn has a first Fourier component of amplitude 2 dn / pi, and kappa = pi (that amplitude) / lam.
    """
    return kappa * lam / 2


# ---------------------------------------------------------------------------------------------------------
# Part A. Transfer matrices from index steps (Chapter 13, Section 13.3)
# ---------------------------------------------------------------------------------------------------------
# A matrix is a nested list [[a, b], [c, d]] whose entries are arrays over wavelength, so that one product
# handles a whole spectrum at once. It maps the forward and backward amplitudes (A, B) at the right-hand
# end of a section to those at its left-hand end.
def mul(P, Q):
    """Product of two 2 x 2 matrices of arrays (four lines of NumPy, ten times faster than numpy.matmul here)."""
    return [[P[0][0] * Q[0][0] + P[0][1] * Q[1][0], P[0][0] * Q[0][1] + P[0][1] * Q[1][1]],
            [P[1][0] * Q[0][0] + P[1][1] * Q[1][0], P[1][0] * Q[0][1] + P[1][1] * Q[1][1]]]


def step(na, nb):
    """An index step from na (left) to nb (right): continuity of E (A + B) and of H (n (A - B)) at the step."""
    p, m = 0.5 * (1 + nb / na), 0.5 * (1 - nb / na)
    return [[p, m], [m, p]]


def layer(n, length, lam):
    """A uniform layer: the forward wave goes as exp(-j beta z), the backward one as exp(+j beta z)."""
    e = np.exp(2j * np.pi * n * length / lam)
    return [[e, 0 * e], [0 * e, 1 / e]]


def period_matrix(lam, dn, high_first=True, period=None):
    """One period: half a period at n_eff + dn/2 and half at n_eff - dn/2, between two stretches of unperturbed guide.

    Referring every period to the unperturbed guide at both ends lets periods be multiplied in any order:
    the steps out of one period and into the next combine into the single step between them.
    """
    period = PERIOD if period is None else period
    n0 = n_eff(lam)
    a, b = (n0 + dn / 2, n0 - dn / 2) if high_first else (n0 - dn / 2, n0 + dn / 2)
    M = step(n0, a)
    for m in (layer(a, period / 2, lam), step(a, b), layer(b, period / 2, lam), step(b, n0)):
        M = mul(M, m)
    return M


def power(M, N):
    """M to the power N by repeated squaring: N identical periods in about 2 log2(N) products."""
    one, zero = 1 + 0 * M[0][0], 0 * M[0][0]
    result = [[one, zero], [zero, one]]
    while N:
        if N & 1:
            result = mul(result, M)
        M = mul(M, M)
        N >>= 1
    return result


def spectrum(M):
    """Power reflection and transmission of a grating with total matrix M, with nothing incident from the far end.

    (A_in, B_in) = M (A_out, 0), so r = B_in/A_in = M[1][0]/M[0][0] and t = A_out/A_in = 1/M[0][0].
    """
    return np.abs(M[1][0] / M[0][0]) ** 2, np.abs(1 / M[0][0]) ** 2


def uniform(lam, n_per=N_PER, kappa=KAPPA):
    """R and T of a uniform grating of n_per periods."""
    return spectrum(power(period_matrix(np.asarray(lam, float), dn_for_kappa(kappa)), n_per))


def grating(lam, dns, shift=False, periods=None):
    """R and T of any grating, period by period; dns lists each period's index step, periods (optional) each length.

    shift=True moves the second half by half a period (low index first), so the two low-index half-periods
    at the centre merge into one layer a full period long: a quarter-wave (pi) phase shift.
    """
    lam = np.asarray(lam, float)
    periods = [PERIOD] * len(dns) if periods is None else periods
    M = None
    for i, (dn, period) in enumerate(zip(dns, periods)):
        P = period_matrix(lam, dn, high_first=not (shift and i >= len(dns) // 2), period=period)
        M = P if M is None else mul(M, P)
    return spectrum(M)


# ---------------------------------------------------------------------------------------------------------
# Part B. Bandwidth, coupled-mode theory and the band gap (Chapter 13, Section 13.2)
# ---------------------------------------------------------------------------------------------------------
def cmt_reflectivity(lam, kappa=KAPPA, length=N_PER * PERIOD):
    """Coupled-mode theory for a uniform grating: r = -j kappa sinh(sL) / (s cosh(sL) + j delta sinh(sL)).

    delta = beta - pi/Lambda is the detuning and s^2 = kappa^2 - delta^2; s is imaginary outside the stop-band.
    """
    delta = 2 * np.pi * n_eff(lam) / lam - np.pi / PERIOD
    s = np.sqrt((kappa**2 - delta**2).astype(complex))
    r = -1j * kappa * np.sinh(s * length) / (s * np.cosh(s * length) + 1j * delta * np.sinh(s * length))
    return np.abs(r) ** 2


def bisect(f, a, b, n=60):
    """A root of f between a and b, where f changes sign, by halving the interval n times."""
    fa = f(a)
    for _ in range(n):
        c = 0.5 * (a + b)
        if (f(c) > 0) == (fa > 0):
            a, fa = c, f(c)
        else:
            b = c
    return 0.5 * (a + b)


def golden_min(f, a, b, n=60):
    """The minimum of f between a and b (one minimum only) by golden-section search."""
    g = (np.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    for _ in range(n):
        if f(c) < f(d):
            b, d = d, c
            c = b - g * (b - a)
        else:
            a, c = c, d
            d = a + g * (b - a)
    return 0.5 * (a + b)


def first_nulls(lam, R, Rfun):
    """The first minimum of R on each side of the main peak: walk outwards on the grid, then refine."""
    i = np.argmax(R)
    nulls = []
    for direction in (-1, 1):
        j = i
        while R[j + direction] < R[j]:
            j += direction
        nulls.append(golden_min(Rfun, lam[j - 1], lam[j + 1]))
    return nulls


def band_gap(kappa, lo=1.45, hi=1.65):
    """Edges of the photonic band gap from one period's matrix: a Bloch wave exp(-j K z) needs cos(K Lambda) = Tr(P)/2.

    Inside the gap |Tr(P)/2| > 1, K is complex and light cannot propagate (the 1D photonic band gap).
    """
    def outside(lam):                          # > 0 inside the gap
        P = period_matrix(np.array([lam]), dn_for_kappa(kappa))
        return abs(np.real(P[0][0] + P[1][1])[0]) / 2 - 1
    centre = bisect(lambda l: 2 * n_eff(l) * PERIOD - l, lo, hi)
    return bisect(outside, lo, centre), bisect(outside, centre, hi)


# ---------------------------------------------------------------------------------------------------------
# Part C. Apodisation (Chapter 13, Section 13.4)
# ---------------------------------------------------------------------------------------------------------
def gaussian(n_per):
    """Gaussian apodisation profile of the chapter's demo, exp(-(z/0.22)^2), z from -0.5 to 0.5 along the grating."""
    z = (np.arange(n_per) + 0.5) / n_per - 0.5
    return np.exp(-(z / 0.22) ** 2)


def side_lobe_db(lam, R):
    """The strongest reflection beyond the first minimum on either side of the main peak, in dB below the peak.

    Walk out from the peak to below half maximum first (a strong grating's flat top has rounding-error ripples),
    then on to the first minimum.
    """
    i = np.argmax(R)
    lobes = []
    for direction in (-1, 1):
        j = i
        while R[j] > R[i] / 2:
            j += direction
        while 0 < j < len(R) - 1 and R[j + direction] < R[j]:
            j += direction
        lobes.append(R[j:].max() if direction > 0 else R[:j + 1].max())
    return 10 * np.log10(max(lobes) / R[i])


def fwhm(lam, R):
    """Full width at half maximum of the main peak on a grid, with linear interpolation at the two crossings."""
    i, half = np.argmax(R), R.max() / 2
    edges = []
    for direction in (-1, 1):
        j = i
        while R[j + direction] > half:
            j += direction
        k = j + direction
        edges.append(lam[j] + (half - R[j]) * (lam[k] - lam[j]) / (R[k] - R[j]))
    return edges[1] - edges[0]


# ---------------------------------------------------------------------------------------------------------
# Part D. A quarter-wave-shifted cavity (Chapter 13, Section 13.6)
# ---------------------------------------------------------------------------------------------------------
def shifted(lam, n_per, kappa=KAPPA):
    """R and T of a uniform grating whose second half is shifted by half a period (a lambda/4 phase shift)."""
    lam = np.asarray(lam, float)
    dn = dn_for_kappa(kappa)
    first = power(period_matrix(lam, dn, high_first=True), n_per // 2)
    second = power(period_matrix(lam, dn, high_first=False), n_per - n_per // 2)
    return spectrum(mul(first, second))


def cavity(n_per, kappa=KAPPA):
    """Resonance wavelength, peak transmission, full width at half maximum and Q of the lambda/4-shifted grating."""
    T = lambda l: shifted(np.array([l]), n_per, kappa)[1][0]
    peak = golden_min(lambda l: -T(l), LAM0 - 2e-4, LAM0 + 2e-4)
    Tp = T(peak)
    edges = []
    for direction in (-1, 1):                  # step out until T falls below half, then bisect
        far = peak
        while T(far) > Tp / 2:
            far += direction * 1e-5
            if abs(far - peak) > 3e-3:          # no half-maximum inside the stop-band: the mirrors are too weak
                return peak, Tp, np.nan, np.nan
        edges.append(bisect(lambda l: T(l) - Tp / 2, peak, far))
    width = edges[1] - edges[0]
    return peak, Tp, width, peak / width


def main(plot=True):
    print("Lab 5: Bragg gratings with transfer matrices (lengths in um, wavelength around 1.55 um)\n")
    L = N_PER * PERIOD
    dn = dn_for_kappa(KAPPA)
    lam = np.linspace(1.535, 1.565, 6001)

    # ---- Part A
    R, T = uniform(lam)
    i = np.argmax(R)
    print("A. A uniform grating built from index steps")
    print(f"   period {1000 * PERIOD:.1f} nm   (Chapter 13: 316.8 nm); index step {dn:.5f} for kappa = 12.6 /mm")
    print(f"   {N_PER} periods: L = {L:.1f} um, kappa L = {KAPPA * L:.3f}   (Chapter 13: 95 um, 1.2)")
    Rfun = lambda l: uniform(np.array([l]))[0][0]
    peak = golden_min(lambda l: -Rfun(l), lam[i - 1], lam[i + 1])
    print(f"   peak reflectivity {100 * Rfun(peak):.2f} % at {1000 * peak:.2f} nm; tanh^2(kappa L) = "
          f"{100 * np.tanh(KAPPA * L) ** 2:.2f} %   (Chapter 13: 69 %)")
    print(f"   Bragg wavelength 2 n_eff Lambda = {2000 * NEFF * PERIOD:.2f} nm   (Chapter 13: 1550 nm)")
    print(f"   energy conservation: largest |R + T - 1| = {np.max(np.abs(R + T - 1)):.0e}\n")

    # ---- Part B
    nulls = first_nulls(lam, R, Rfun)
    bw = LAM0**2 / (NG * L) * np.sqrt((KAPPA * L / np.pi) ** 2 + 1)
    print("B. Bandwidth, coupled-mode theory and the band gap")
    print(f"   first nulls at {1000 * nulls[0]:.2f} and {1000 * nulls[1]:.2f} nm: bandwidth {1000 * (nulls[1] - nulls[0]):.2f} nm;"
          f" formula {1000 * bw:.2f} nm   (Chapter 13: 6.5 nm)")
    print(f"   largest difference from coupled-mode theory over 1535-1565 nm: "
          f"{np.max(np.abs(R - cmt_reflectivity(lam))):.4f} in R")
    P = period_matrix(np.array([LAM0]), dn)
    M, n99 = P, 1
    while spectrum(M)[0][0] < 0.99:
        M, n99 = mul(M, P), n99 + 1
    print(f"   99 % reflection needs {n99} periods, {n99 * PERIOD:.0f} um   (Chapter 13: 750 periods, 238 um)")
    for kap, chap in ((KAPPA, ""), (0.14, "   (Chapter 13: about 25 nm)")):
        lo, hi = band_gap(kap)
        print(f"   band gap for kappa = {1000 * kap:.1f} /mm: {1000 * (hi - lo):.2f} nm; lambda^2 kappa / (pi n_g) = "
              f"{1e3 * LAM0**2 * kap / (np.pi * NG):.2f} nm{chap}")
    print()

    # ---- Part C
    lam_w = np.linspace(1.52, 1.58, 6001)
    Ru = uniform(lam_w)[0]
    prof = gaussian(N_PER)
    Ra = grating(lam_w, dn * prof)[0]
    scale = 1 / prof.mean()                                  # same kappa L on average, so the same peak
    Rb = grating(lam_w, dn * scale * prof)[0]
    print("C. Gaussian apodisation, exp(-(z/0.22)^2) along the grating")
    print(f"   uniform:                 peak {100 * Ru.max():.1f} %, FWHM {1000 * fwhm(lam_w, Ru):.2f} nm, "
          f"strongest side lobe {side_lobe_db(lam_w, Ru):.1f} dB")
    print(f"   apodised, same kappa:    peak {100 * Ra.max():.1f} %, FWHM {1000 * fwhm(lam_w, Ra):.2f} nm, "
          f"strongest side lobe {side_lobe_db(lam_w, Ra):.1f} dB")
    print(f"   apodised, kappa x {scale:.2f}:  peak {100 * Rb.max():.1f} %, FWHM {1000 * fwhm(lam_w, Rb):.2f} nm, "
          f"strongest side lobe {side_lobe_db(lam_w, Rb):.1f} dB")
    lam_s = np.linspace(1.50, 1.60, 4001)                    # a strong grating: kappa = 100 /mm, kappa L = 9.5
    Rs, Rsa = uniform(lam_s, kappa=0.1)[0], grating(lam_s, dn_for_kappa(0.1) * prof)[0]
    print(f"   a strong grating, kappa = 100 /mm: uniform peak {100 * Rs.max():.2f} %, FWHM {1000 * fwhm(lam_s, Rs):.1f} nm;"
          f" apodised {100 * Rsa.max():.2f} %, {1000 * fwhm(lam_s, Rsa):.1f} nm")
    print("   (Chapter 13: Example 13.2's grating drops from 69 % to 19 % and widens from 3.9 to 5.6 nm; a strong grating's"
          " peak is only slightly lower and a little narrower)\n")

    # ---- Part D
    print("D. A quarter-wave-shifted grating (a pi phase shift at the centre)")
    results = {}
    for n in (300, 500, 750, 1000):
        lam_r, Tp, width, Q = cavity(n)
        results[n] = (lam_r, Tp, width, Q)
        if np.isnan(Q):
            print(f"   {n:4d} periods (kappa L = {KAPPA * n * PERIOD:.1f}): T = {100 * Tp:.1f} % at {1000 * lam_r:.3f} nm, "
                  "but the stop-band never falls below half, so there is no FWHM")
        else:
            print(f"   {n:4d} periods (kappa L = {KAPPA * n * PERIOD:.1f}): T = {100 * Tp:.1f} % at {1000 * lam_r:.3f} nm, "
                  f"FWHM {1000 * width:.3f} nm, Q = {Q:.0f}")
    print("   (Chapter 13: a narrow transmission peak opens in the middle of the stop-band)\n")

    if plot:
        make_figure(lam, R, T, lam_w, Ru, Ra, Rb, scale, n99)


def make_figure(lam, R, T, lam_w, Ru, Ra, Rb, scale, n99):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    nm = lambda x: 1000 * x
    # (a) the uniform grating: transfer matrices against coupled-mode theory
    ax[0, 0].plot(nm(lam), R, color="tab:orange", lw=1.8, label="R, transfer matrices")
    ax[0, 0].plot(nm(lam), cmt_reflectivity(lam), color="k", ls="--", lw=0.9, label="R, coupled-mode theory")
    ax[0, 0].plot(nm(lam), T, color="tab:blue", lw=1.2, label="T, transfer matrices")
    ax[0, 0].axhline(np.tanh(KAPPA * N_PER * PERIOD) ** 2, color="grey", ls=":", lw=0.8, label="tanh²(κL)")
    ax[0, 0].set(xlabel="wavelength (nm)", ylabel="power", ylim=(0, 1.02),
                 title=f"(a) uniform grating, {N_PER} periods, κL = 1.2")
    ax[0, 0].legend(fontsize=8, loc="center right")
    # (b) peak reflectivity against the number of periods
    ns = np.arange(10, 1001, 10)
    P = period_matrix(np.array([LAM0]), dn_for_kappa(KAPPA))
    peaks = [spectrum(power(P, n))[0][0] for n in ns]
    nf = np.linspace(0, 1000, 400)
    ax[0, 1].plot(nf, np.tanh(KAPPA * nf * PERIOD) ** 2, color="k", lw=1, label="tanh²(κL)")
    ax[0, 1].plot(ns[::3], peaks[::3], "o", color="tab:orange", ms=4, label="transfer matrices")
    for n, text in ((N_PER, f"{N_PER} periods"), (n99, f"{n99} periods: 99 %")):
        ax[0, 1].axvline(n, color="grey", ls=":", lw=0.8)
        ax[0, 1].text(n + 12, 0.42, text, rotation=90, fontsize=8, color="grey")
    ax[0, 1].set(xlabel="number of periods N", ylabel="peak reflectivity", title="(b) peak R at the Bragg wavelength")
    ax[0, 1].legend(fontsize=8, loc="lower right")
    # (c) apodisation, on a dB scale
    db = lambda r: 10 * np.log10(np.maximum(r, 1e-9))
    ax[1, 0].plot(nm(lam_w), db(Ru), color="tab:orange", lw=1.2, label="uniform")
    ax[1, 0].plot(nm(lam_w), db(Ra), color="tab:blue", lw=1.2, label="Gaussian, same κ")
    ax[1, 0].plot(nm(lam_w), db(Rb), color="tab:green", lw=1.2, label=f"Gaussian, κ × {scale:.2f}")
    ax[1, 0].set(xlabel="wavelength (nm)", ylabel="reflection (dB)", ylim=(-80, 3), title="(c) apodisation and side lobes")
    ax[1, 0].legend(fontsize=8, loc="upper left")
    # (d) the quarter-wave-shifted cavity
    lam_c = np.linspace(1.5465, 1.5535, 3001)
    for n, col in ((500, "tab:purple"), (750, "tab:blue"), (1000, "tab:green")):
        ax[1, 1].plot(nm(lam_c), shifted(lam_c, n)[1], color=col, lw=1.2, label=f"{n} periods")
    ax[1, 1].set(xlabel="wavelength (nm)", ylabel="transmission", ylim=(0, 1.02), title="(d) λ/4-shifted grating: the cavity")
    ax[1, 1].legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig("lab05_bragg.png", dpi=150)
    print("Saved the figure as lab05_bragg.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
