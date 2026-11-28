# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 14: coupling light into chips (Open-Photonics, Chapters 3, 17 and 36).

Run it from a terminal:
    python lab14_coupling.py              # prints every checkpoint and saves lab14_coupling.png
    python lab14_coupling.py --no-plot    # numbers only

NumPy only (Matplotlib for the figure). Lengths in micrometres, angles in radians inside.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-14/
"""
import math
import sys

import numpy as np

LAM = 1.55          # wavelength (um)
N_LENS = 1.53       # printed-lens resist (Xu et al. 2023)
PITCH = 127.0       # fibre-array pitch (um)


# ---------------------------------------------------------------------------------------------------------
# Part A. Overlap integrals on a grid against the closed forms (Section 17.2)
# ---------------------------------------------------------------------------------------------------------
def gauss_field(X, Y, w, z=0.0, n=1.0, x0=0.0, tilt=0.0):
    """Complex field of a Gaussian beam of waist w, a distance z from its waist, centred at x0 and tilted by
    `tilt` in the x-z plane (small angle)."""
    zr = math.pi * n * w * w / LAM
    q = z + 1j * zr
    k = 2 * math.pi * n / LAM
    r2 = (X - x0) ** 2 + Y ** 2
    return (1j * zr / q) * np.exp(-1j * k * r2 / (2 * q)) * np.exp(1j * k * tilt * X)


def overlap(E1, E2, dA):
    return abs(np.sum(E1 * np.conj(E2)) * dA) ** 2 / (np.sum(abs(E1) ** 2) * dA * np.sum(abs(E2) ** 2) * dA)


def eta_closed(w1, w2, d=0.0, th=0.0, n=1.0):
    """Closed form of Section 17.2 (waists in one plane): size mismatch, offset and tilt."""
    s = w1 * w1 + w2 * w2
    return (2 * w1 * w2 / s) ** 2 * math.exp(-2 * d * d / s) * math.exp(-2 * (math.pi * n * th / LAM) ** 2 * w1 * w1 * w2 * w2 / s)


def part_a():
    print("Part A. Overlap integrals on a grid")
    w1, w2 = 5.2, 4.6                                         # SMF-28 over a grating coupler (Worked Example 17.1)
    x = np.linspace(-30, 30, 601); X, Y = np.meshgrid(x, x); dA = (x[1] - x[0]) ** 2
    E1 = gauss_field(X, Y, w1)
    for d, th in ((0.0, 0.0), (2.35, 0.0), (0.0, math.radians(2.0))):
        e_num = overlap(E1, gauss_field(X, Y, w2, x0=d, tilt=th), dA)
        print(f"  w {w1}/{w2} um, offset {d} um, tilt {math.degrees(th):.1f} deg: grid {e_num:.5f}, closed form {eta_closed(w1, w2, d, th):.5f}"
              f" ({10 * math.log10(e_num):.3f} dB)")
    e_gap = overlap(E1, gauss_field(X, Y, w2, z=10.0), dA)
    print(f"  the same pair with a 10 um air gap: {10 * math.log10(e_gap / eta_closed(w1, w2)):.3f} dB below no gap"
          "  (Worked Example 17.1: 0.05 dB)")


# ---------------------------------------------------------------------------------------------------------
# Part B. Four test interfaces (Table 36.1)
# ---------------------------------------------------------------------------------------------------------
def tol(f, hi):
    lo = 0.0
    for _ in range(80):
        m = (lo + hi) / 2
        if f(m) > 10 ** -0.1: lo = m
        else: hi = m
    return (lo + hi) / 2


def eta_gap(g, w1, w2, n=1.0):
    """Coupling of two waists w1 and w2 a distance g apart (Kogelnik)."""
    return 4 * (w1 * w2) ** 2 / ((w1 * w1 + w2 * w2) ** 2 + (LAM * g / (math.pi * n)) ** 2)


def part_b():
    print("Part B. Four test interfaces at 1550 nm (1 dB tolerances)")
    rows = (("cleaved fibre array over grating couplers", 5.2, 4.6), ("high-NA fibre array butted to edge couplers", 2.0, 1.8),
            ("lensed fibre array at edge couplers", 1.25, 1.25), ("lenses on the fibres and on the chip", 12.5, 12.5))
    out = []
    for name, w1, w2 in rows:
        e0 = eta_closed(w1, w2)
        d = tol(lambda v: eta_closed(w1, w2, d=v) / e0, 100)
        t = math.degrees(tol(lambda v: eta_closed(w1, w2, th=v) / e0, 1.0))
        g = tol(lambda v: eta_gap(v, w1, w2) / eta_gap(0, w1, w2), 1e5)
        print(f"  {name:45s} offset +-{d:5.2f} um, tilt +-{t:5.2f} deg, gap {g:6.1f} um, rotation over 889 um {math.degrees(d / 889):.3f} deg")
        out.append((name, d, t, g))
    print("  Table 36.1: +-2.35, 2.8 deg, 50 um; +-0.91, 7.2 deg, 7.5 um; +-0.60, 10.9 deg, 3.2 um; +-6.0, 1.1 deg, 322 um")
    return out


# ---------------------------------------------------------------------------------------------------------
# Part C. A printed lens: length, the collimating ellipse, and a ray check (Section 17.5)
# ---------------------------------------------------------------------------------------------------------
def lens_design(w0, W, n=N_LENS):
    zr = math.pi * n * w0 * w0 / LAM
    L = zr * math.sqrt((W / w0) ** 2 - 1)
    R = L * (1 + (zr / L) ** 2)                               # wavefront radius at the surface
    return zr, L, R


def trace(surface, R, n=N_LENS, angles=None):
    """Rays leave a point source at the wavefront's centre (a distance R behind the apex, inside the lens) at the
    given angles, refract at the surface into air, and come out at some angle to the axis. surface(y) gives the
    surface's axial position (from the source) at height y and its slope dz/dy. Returns output angles (rad)."""
    out = []
    for a in angles:
        # find the height y where the ray meets the surface: z = y / tan(a) on the ray
        lo, hi = 0.0, R
        for _ in range(100):
            y = (lo + hi) / 2
            zs, _ = surface(y)
            if y / math.tan(a) < zs: lo = y
            else: hi = y
        zs, dz = surface(y)
        nrm = np.array([1.0, -dz]); nrm /= np.linalg.norm(nrm)         # outward normal (z, y)
        d = np.array([math.cos(a), math.sin(a)])
        c1 = d @ nrm; sin_t = math.sqrt(max(0.0, 1 - c1 * c1)) * n
        if sin_t >= 1:
            out.append(float("nan")); continue
        t = n * d + (math.sqrt(1 - sin_t ** 2) - n * c1) * nrm         # vector form of Snell's law into air
        out.append(math.atan2(t[1], t[0]))
    return np.array(out)


def part_c():
    print("Part C. A printed lens on a 2.5 um edge coupler, 25 um beam")
    w0, W = 1.25, 12.5
    zr, L, R = lens_design(w0, W)
    e = 1 / N_LENS; a = R / (1 + e); b = a * math.sqrt(1 - e * e); c = a * e
    rs = (N_LENS - 1) / N_LENS * R
    print(f"  Rayleigh range in the resist {zr:.2f} um, lens length {L:.1f} um, wavefront radius {R:.1f} um, apex radius {rs:.1f} um,"
          f" ellipse a {a:.1f} b {b:.1f} um  (Section 17.5: 48 um, apex radius 17 um)")
    ell = lambda y: (c + a * math.sqrt(max(0.0, 1 - (y / b) ** 2)), -a * y / (b * b) / math.sqrt(max(1e-15, 1 - (y / b) ** 2)))
    sph = lambda y: (R - rs + math.sqrt(max(0.0, rs * rs - y * y)), -y / math.sqrt(max(1e-15, rs * rs - y * y)))
    theta = LAM / (math.pi * N_LENS * w0)                    # 1/e^2 half-angle of the beam in the resist
    ang = np.linspace(0.02, 1.5, 6) * theta
    to_e, to_s = trace(ell, R, angles=ang), trace(sph, R, angles=ang)
    for k in range(len(ang)):
        sph_txt = "misses the cap" if np.isnan(to_s[k]) else f"{math.degrees(to_s[k]):+.2f} deg"
        print(f"    ray at {math.degrees(ang[k]):5.2f} deg ({ang[k] / theta:.2f} x the beam's half-angle): leaves the ellipse at"
              f" {math.degrees(to_e[k]):+.1e} deg, a sphere of the same apex radius at {sph_txt}")
    return dict(L=L, a=a, b=b, c=c, rs=rs, R=R, theta=theta)


# ---------------------------------------------------------------------------------------------------------
# Part D. Every channel at once: a Monte Carlo of an 8-fibre array (Section 36.8)
# ---------------------------------------------------------------------------------------------------------
def part_d(trials=20000, seed=3):
    print("Part D. Worst channel of an 8-fibre array (Monte Carlo, illustrative errors)")
    rng = np.random.default_rng(seed)
    xs = (np.arange(8) - 3.5) * PITCH
    res = {}
    for name, w, s_core, s_tilt in (("lensed fibre array, 2.5 um spots", 1.25, 0.35, 0.3), ("lenses on both sides, 25 um beam", 12.5, 1.5, 0.3)):
        dx = rng.normal(0, s_core, (trials, 8)); dy = rng.normal(0, s_core, (trials, 8))   # spot errors: cores and lens pointing
        rot = np.radians(rng.normal(0, 0.03, (trials, 1)))                                 # array rotation in its plane
        dy = dy + xs[None, :] * rot
        th = np.radians(rng.normal(0, s_tilt, (trials, 8)))                                # pointing (angle) errors
        loss = -10 * np.log10(np.exp(-(dx ** 2 + dy ** 2) / (w * w)) * np.exp(-(math.pi * th / LAM) ** 2 * w * w))
        worst = loss.max(axis=1)
        res[name] = worst
        print(f"  {name:34s} worst channel: median {np.median(worst):5.2f} dB, 95th percentile {np.percentile(worst, 95):5.2f} dB;"
              f" all eight within 1 dB in {100 * np.mean(worst < 1):5.1f} % of arrays")
    print("  (spot errors sigma 0.35 um per axis for the lensed array, 1.5 um for the printed lenses; 0.03 deg rotation; 0.3 deg pointing)")
    return res


def main(plot=True):
    part_a()
    part_b()
    c = part_c()
    d = part_d()
    if not plot:
        return
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    dd = np.linspace(0, 10, 300)
    for w1, w2, col, lab in ((1.25, 1.25, "tab:orange", "2.5 um spots (lensed)"), (5.2, 4.6, "tab:green", "fibre over a grating"),
                             (12.5, 12.5, "tab:blue", "25 um beams (printed lenses)")):
        e0 = eta_closed(w1, w2)
        ax[0].plot(dd, [10 * math.log10(eta_closed(w1, w2, d=v) / e0) for v in dd], color=col, label=lab)
    ax[0].axhline(-1, color="grey", ls=":"); ax[0].set(ylim=(-6, 0.3), xlabel="lateral offset (um)", ylabel="coupling change (dB)", title="(a) offset tolerance")
    ax[0].legend(fontsize=8)
    # (b) the lens and the traced rays
    L, a_, b_, c_, R, th = c["L"], c["a"], c["b"], c["c"], c["R"], c["theta"]
    ys = np.linspace(-1.6 * 12.5, 1.6 * 12.5, 200)
    zs = c_ + a_ * np.sqrt(np.clip(1 - (ys / b_) ** 2, 0, 1)) - (R - L)
    ax[1].plot(zs, ys, color="tab:purple"); ax[1].plot([0, 0], [ys[0], ys[-1]], color="k", lw=0.8)
    for ang in np.linspace(-1.5, 1.5, 13) * th:
        lo, hi = 0.0, R
        for _ in range(60):
            y = (lo + hi) / 2
            if abs(y) / math.tan(abs(ang) + 1e-12) < c_ + a_ * math.sqrt(max(0, 1 - (y / b_) ** 2)): lo = y
            else: hi = y
        ysg = math.copysign(y, ang); zhit = c_ + a_ * math.sqrt(max(0, 1 - (y / b_) ** 2)) - (R - L)
        ax[1].plot([-(R - L), zhit], [0, ysg], color="tab:red", lw=0.6); ax[1].plot([zhit, L + 40], [ysg, ysg], color="tab:red", lw=0.6)
    ax[1].set(xlim=(-(R - L) - 2, L + 40), xlabel="distance from the facet (um)", ylabel="height (um)", title="(b) rays through the collimating ellipse")
    ax[1].set_aspect("equal")
    for (name, worst), col in zip(d.items(), ("tab:orange", "tab:blue")):
        ax[2].hist(worst, bins=np.linspace(0, 6, 61), color=col, alpha=0.6, label=name)
    ax[2].axvline(1, color="grey", ls=":"); ax[2].set(xlabel="worst-channel loss (dB)", ylabel="arrays", title="(c) 8-fibre array, Monte Carlo")
    ax[2].legend(fontsize=8)
    fig.tight_layout(); fig.savefig("lab14_coupling.png", dpi=150)
    print("Saved the figure as lab14_coupling.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
