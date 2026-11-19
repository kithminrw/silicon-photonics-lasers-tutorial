# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 2: mode solving with femwell (Open-Photonics, Chapters 6 and 7).

Run it from a terminal:
    python lab02_femwell.py              # prints every checkpoint and saves lab02_femwell.png (a few minutes)
    python lab02_femwell.py --quick      # five widths instead of twelve, no direct 2 um BOX solve
    python lab02_femwell.py --no-plot    # numbers only

It needs femwell (which brings scikit-fem, gmsh and shapely), NumPy and Matplotlib. All lengths are in micrometres.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-02/
"""
import sys
import time
from collections import OrderedDict

import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict

LAM = 1.55       # vacuum wavelength
RES = 0.05       # mesh size in and near the silicon (Exercise 2 shows it is converged to the fourth decimal)
HALF_W, HALF_H = 2.0, 1.6   # the oxide around the waveguide: 4 um wide, 3.2 um tall


def n_si(lam):
    """Silicon at room temperature (Sellmeier fit of Li, 1980), lam in micrometres; as in Lab 1."""
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / lam**2 + 0.00810461 * l1**2 / (lam**2 - l1**2))


def n_ox(lam):
    """Fused silica (Malitson, 1965)."""
    return np.sqrt(1 + 0.6961663 * lam**2 / (lam**2 - 0.0684043**2) + 0.4079426 * lam**2 / (lam**2 - 0.1162414**2)
                   + 0.8974794 * lam**2 / (lam**2 - 9.896161**2))


# ---------------------------------------------------------------------------------------------------------
# Part A. Mesh a cross-section and solve for its modes (Chapter 6, Sections 6.3 and 6.4)
# ---------------------------------------------------------------------------------------------------------
def cross_section(width, t=0.22, slab=0.0, res=RES, half_w=HALF_W, half_h=HALF_H):
    """Triangular mesh of a strip (slab = 0) or rib (slab > 0) in oxide, with named regions.

    The polygons are listed in priority order: where they overlap, the first one wins. The mesh is fine
    (res) in the silicon and within 0.6 um of it, and coarsens to 0.25 um far away.
    """
    polys = OrderedDict(core=box(-width / 2, 0, width / 2, t))
    sizes = {"core": {"resolution": res, "distance": 0.6}}
    if slab > 0:
        polys["slab"] = box(-half_w, 0, half_w, slab)
        sizes["slab"] = {"resolution": 1.2 * res, "distance": 0.4}
    polys["clad"] = box(-half_w, t / 2 - half_h, half_w, t / 2 + half_h)
    return from_meshio(mesh_from_OrderedDict(polys, sizes, default_resolution_max=0.25))


def solve(width, lam=LAM, t=0.22, slab=0.0, num=2, res=RES, n_core=None, half_w=HALF_W, half_h=HALF_H):
    """Guided modes of the cross-section at one wavelength, highest n_eff first.

    Returns a list of (n_eff, TE fraction, femwell Mode). The permittivity is constant on each triangle
    (ElementTriP0): silicon in the core and slab, oxide elsewhere. Modes below the oxide index are not guided.
    """
    mesh = cross_section(width, t, slab, res, half_w, half_h)
    basis0 = Basis(mesh, ElementTriP0())
    epsilon = basis0.zeros() + n_ox(lam) ** 2
    n1 = n_si(lam) if n_core is None else n_core
    epsilon[basis0.get_dofs(elements="core")] = n1 ** 2
    if slab > 0:
        epsilon[basis0.get_dofs(elements="slab")] = n1 ** 2
    modes = compute_modes(basis0, epsilon, wavelength=lam, num_modes=num, order=2)
    out = [(float(np.real(m.n_eff)), float(m.te_fraction), m) for m in modes]
    return sorted([o for o in out if o[0] > n_ox(lam) + 1e-3], key=lambda o: -o[0])


def pick(modes, pol="TE", order=0):
    """The order-th TE-like (TE fraction > 0.5) or TM-like mode of a list from solve(), or None."""
    found = [m for m in modes if (m[1] > 0.5) == (pol == "TE")]
    return found[order] if len(found) > order else None


# ---------------------------------------------------------------------------------------------------------
# Part B. The effective-index method of Lab 1, for comparison (Chapter 6, Section 6.2)
# ---------------------------------------------------------------------------------------------------------
def slab_modes(n1, n2, n3, d, lam, tm=False):
    """Effective indices of every guided mode of a three-layer slab, by bisection (Lab 1, Part A)."""
    k0 = 2 * np.pi / lam

    def F(neff):
        kappa, g2, g3 = k0 * np.sqrt(n1**2 - neff**2), k0 * np.sqrt(neff**2 - n2**2), k0 * np.sqrt(neff**2 - n3**2)
        p2, p3 = (g2 * n1**2 / n2**2, g3 * n1**2 / n3**2) if tm else (g2, g3)
        return kappa * d - np.arctan(p2 / kappa) - np.arctan(p3 / kappa)

    lo, hi, modes, m = max(n2, n3) + 1e-12, n1 - 1e-12, [], 0
    while F(lo) > m * np.pi:
        a, b = lo, hi
        for _ in range(60):
            c = 0.5 * (a + b)
            a, b = (c, b) if F(c) > m * np.pi else (a, c)
        modes.append(0.5 * (a + b))
        m += 1
    return modes


def eim(width, t=0.22, slab=0.0, lam=LAM, te=True, order=0):
    """Effective index of a strip or rib by the EIM (Lab 1, Part D), with this lab's Sellmeier indices."""
    n_I = slab_modes(n_si(lam), n_ox(lam), n_ox(lam), t, lam, tm=not te)[0]
    n_II = slab_modes(n_si(lam), n_ox(lam), n_ox(lam), slab, lam, tm=not te)[0] if slab > 0 else n_ox(lam)
    lateral = slab_modes(n_I, n_II, n_II, width, lam, tm=te)
    return lateral[order] if len(lateral) > order else float("nan")


# ---------------------------------------------------------------------------------------------------------
# Part C. Group index from a wavelength derivative (Chapter 6, Section 6.3)
# ---------------------------------------------------------------------------------------------------------
def group_index(width, lam=LAM, dl=0.01, mid=None, **kw):
    """n_g = n_eff - lam * dn_eff/dlam for TE0 and TM0, central difference over +-10 nm.

    The silicon and oxide indices change with wavelength too (n_si, n_ox), so this includes material
    dispersion, as Table 6.1 does. Pass the modes at lam as mid if you have them already. Returns
    {"TE": (n_eff, n_g), "TM": (n_eff, n_g)}, without a polarisation that is not guided.
    """
    lo, hi = solve(width, lam - dl, **kw), solve(width, lam + dl, **kw)
    mid = solve(width, lam, **kw) if mid is None else mid
    out = {}
    for pol in ("TE", "TM"):
        found = [pick(m, pol) for m in (lo, mid, hi)]
        if all(found):
            n0, n1, n2 = (f[0] for f in found)
            out[pol] = (n1, n1 - lam * (n2 - n0) / (2 * dl))
    return out


# ---------------------------------------------------------------------------------------------------------
# Part E. Substrate leakage through a finite buried oxide (Chapter 7, Section 7.4)
# ---------------------------------------------------------------------------------------------------------
def leaky_mode(t_box, pol="TE", width=0.5, lam=LAM, n_guess=None, t_sub=1.0, absorb=2.0, res=RES):
    """Complex n_eff of TE0 or TM0 with the silicon handle t_box below the waveguide.

    The handle (n_si) is cut to t_sub and made absorbing, with Im(eps) rising quadratically with depth, so
    the light that tunnels into it is not reflected back: the bottom of the window behaves like an
    infinitely thick substrate. Returns (n_eff, loss in dB/cm).
    """
    polys = OrderedDict(core=box(-width / 2, 0, width / 2, 0.22),
                        substrate=box(-HALF_W, -t_box - t_sub, HALF_W, -t_box),
                        clad=box(-HALF_W, -t_box - t_sub, HALF_W, 0.22 + 1.5))
    sizes = {"core": {"resolution": res, "distance": 0.6}, "substrate": {"resolution": 0.1, "distance": 0.2}}
    mesh = from_meshio(mesh_from_OrderedDict(polys, sizes, default_resolution_max=0.25))
    basis0 = Basis(mesh, ElementTriP0())
    epsilon = (basis0.zeros() + n_ox(lam) ** 2).astype(complex)
    epsilon[basis0.get_dofs(elements="core")] = n_si(lam) ** 2
    sub = basis0.get_dofs(elements="substrate")             # one P0 unknown per triangle
    depth = (-t_box - mesh.p[1, mesh.t].mean(axis=0)[sub]) / t_sub   # 0 at the top of the handle, 1 at the bottom
    epsilon[sub] = n_si(lam) ** 2 * (1 + 1j * absorb * depth**2)
    if n_guess is None:
        n_guess = 2.446 if pol == "TE" else 1.771
    # the shift-invert solver returns the mode closest to n_guess; the handle's own modes are far off,
    # because the absorber gives them a large imaginary part
    mode = compute_modes(basis0, epsilon, wavelength=lam, num_modes=1, n_guess=n_guess, order=2)[0]
    n = complex(mode.n_eff)
    k0 = 2 * np.pi / lam
    return n, 20 / np.log(10) * k0 * n.imag * 1e4          # power loss 2*k0*Im(n) per um, in dB/cm


def main(plot=True, quick=False):
    t_start = time.time()
    print("Lab 2: mode solving with femwell (lengths in um, wavelength 1.55 um)\n")

    # ---- Part A
    mesh = cross_section(0.5)
    m500 = solve(0.5, num=3)
    te0, tm0, te1 = pick(m500, "TE"), pick(m500, "TM"), pick(m500, "TE", 1)
    print("A. 500 x 220 nm silicon strip in oxide")
    print(f"   n_si = {n_si(LAM):.4f}, n_ox = {n_ox(LAM):.4f}; mesh of {mesh.nelements} triangles")
    print(f"   TE0: n_eff = {te0[0]:.4f}, TE fraction {te0[1]:.3f}   (Table 6.1: 2.446)")
    print(f"   TM0: n_eff = {tm0[0]:.4f}, TE fraction {tm0[1]:.3f}   (Table 6.1: 1.771)")
    print(f"   TE1: n_eff = {te1[0]:.4f}, TE fraction {te1[1]:.3f}   (Chapter 6: 1.49, barely above the oxide)\n")

    # ---- Part B
    widths = np.array([0.35, 0.40, 0.45, 0.50, 0.60]) if quick else np.round(np.arange(0.25, 0.801, 0.05), 2)
    sweep = []
    for w in widths:
        ms = solve(w, num=3)
        sweep.append([(pick(ms, p, o) or (np.nan,))[0] for p, o in (("TE", 0), ("TM", 0), ("TE", 1))])
    sweep = np.array(sweep)
    first_te1 = widths[np.argmax(np.isfinite(sweep[:, 2]))]
    below = widths[widths < first_te1]
    print("B. Width sweep, 220 nm strips")
    for w, (a, b, c) in zip(widths, sweep):
        print(f"   W = {1000 * w:4.0f} nm: TE0 {a:.4f}  TM0 {b:.4f}  TE1 {'  -   ' if np.isnan(c) else f'{c:.4f}'}"
              f"   | EIM TE0 {eim(w):.4f}")
    print(f"   TE1 is guided from {1000 * first_te1:.0f} nm" + (f" (not at {1000 * below[-1]:.0f} nm)" if len(below) else "")
          + "   (Chapter 6: about 450 nm)")
    print(f"   EIM: TE0 {eim(0.5):.3f} at 500 nm (femwell {te0[0]:.3f}), TE1 from "
          f"{1000 * eim_cutoff():.0f} nm   (Chapter 6: 2.49 and about 320 nm)\n")

    # ---- Part C
    ng = group_index(0.5, mid=m500)
    print("C. Group index of the 500 x 220 nm strip, central difference over +-10 nm")
    print(f"   TE0 n_g = {ng['TE'][1]:.2f}   (Table 6.1: 4.18)")
    print(f"   TM0 n_g = {ng['TM'][1]:.2f}   (Table 6.1: 3.74)")
    fsr = LAM**2 / (ng["TE"][1] * 100) * 1000
    print(f"   an MZI with dL = 100 um: FSR = {fsr:.2f} nm   (Worked Example 6.1: 5.7 nm)\n")

    # ---- Part D
    rib = group_index(0.5, slab=0.09)
    print("D. Rib, 500 nm wide, 220 nm film etched to a 90 nm slab")
    print(f"   TE0 n_eff = {rib['TE'][0]:.4f}, n_g = {rib['TE'][1]:.2f}   (Table 6.1: 2.568 and 3.89)")
    print(f"   EIM: {eim(0.5, slab=0.09):.3f}   (Lab 1: 2.600)\n")

    # ---- Part E
    print("E. Substrate leakage of the 500 x 220 nm strip through the buried oxide")
    boxes = (0.6, 1.0)
    leak = {}
    for pol, mode in (("TE", te0), ("TM", tm0)):
        k0 = 2 * np.pi / LAM
        gamma = k0 * np.sqrt(mode[0] ** 2 - n_ox(LAM) ** 2)
        losses = [leaky_mode(tb, pol, n_guess=mode[0])[1] for tb in boxes]
        per100 = 10 * np.log10(losses[0] / losses[1]) / (10 * (boxes[1] - boxes[0]))   # 10 steps of 100 nm per um
        at2 = losses[1] * 10 ** (-per100 * 10 * (2.0 - boxes[1]) / 10)
        leak[pol] = (losses, per100)
        chapter = {"TE": "8.0 um^-1, 7 dB", "TM": "4.2 um^-1, 3.6 dB"}[pol]
        print(f"   {pol}0: {losses[0]:.3g} dB/cm with {1000 * boxes[0]:.0f} nm of BOX, {losses[1]:.3g} dB/cm with "
              f"{1000 * boxes[1]:.0f} nm: {per100:.2f} dB per 100 nm")
        print(f"        e^(-2 gamma t) with gamma = {gamma:.2f} um^-1 predicts {20 / np.log(10) * gamma * 0.1:.2f} dB"
              f" per 100 nm   (Worked Example 7.2: {chapter})")
        print(f"        extrapolated to a 2 um BOX: {at2:.2g} dB/cm")
    if not quick:
        direct = leaky_mode(2.0, "TM", n_guess=tm0[0])[1]
        leak["TM2"] = direct
        print(f"   TM0 solved directly with a 2 um BOX: {direct:.2g} dB/cm")
    print(f"\nTook {time.time() - t_start:.0f} s")

    if plot:
        make_figure(te0, tm0, widths, sweep, boxes, leak)


def eim_cutoff(lam=LAM, lo=0.05, hi=1.0):
    """Width at which the EIM first guides TE1, by bisection (Lab 1's first_width_with)."""
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if np.isfinite(eim(mid, order=1)) else (mid, hi)
    return hi


def make_figure(te0, tm0, widths, sweep, boxes, leak):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    # (a), (b) the intensity of TE0 and TM0 (femwell's own plot, on our axes)
    for a, (n, te, mode), name in ((ax[0, 0], te0, "TE0"), (ax[0, 1], tm0, "TM0")):
        mode.plot_intensity(ax=a, colorbar=False)
        a.set(xlim=(-0.8, 0.8), ylim=(-0.5, 0.72), aspect="equal", xlabel="x (µm)", ylabel="y (µm)",
              title=f"({'a' if name == 'TE0' else 'b'}) {name}: n_eff = {n:.4f}, TE fraction {te:.2f}")
    # (c) effective index against width: femwell against the EIM
    wf = np.linspace(0.2, 0.85, 66)
    ax[1, 0].plot(widths, sweep[:, 0], "o-", color="tab:blue", ms=4, label="TE0, femwell")
    ax[1, 0].plot(widths, sweep[:, 1], "o-", color="tab:orange", ms=4, label="TM0, femwell")
    ax[1, 0].plot(widths, sweep[:, 2], "s-", color="tab:green", ms=4, label="TE1, femwell")
    ax[1, 0].plot(wf, [eim(w) for w in wf], "--", color="tab:blue", lw=1, label="TE0, EIM")
    ax[1, 0].plot(wf, [eim(w, order=1) for w in wf], "--", color="tab:green", lw=1, label="TE1, EIM")
    ax[1, 0].axhline(n_ox(LAM), color="grey", ls=":", lw=0.8)
    ax[1, 0].set(xlabel="strip width W (µm)", ylabel="effective index", title="(c) 220 nm strips at 1550 nm")
    ax[1, 0].legend(fontsize=8)
    # (d) leakage against BOX thickness, with the e^(-2 gamma t) lines through the femwell points
    tb = np.linspace(0.5, 3.0, 50)
    for pol, col in (("TE", "tab:blue"), ("TM", "tab:orange")):
        losses, per100 = leak[pol]
        ax[1, 1].semilogy(boxes, losses, "o", color=col, label=f"{pol}0, femwell")
        ax[1, 1].semilogy(tb, losses[1] * 10 ** (-per100 * 10 * (tb - boxes[1]) / 10), "-", color=col, lw=1,
                          label=f"{pol}0, {per100:.1f} dB per 100 nm")
    if "TM2" in leak:
        ax[1, 1].semilogy([2.0], [leak["TM2"]], "D", color="tab:orange", mfc="none", label="TM0, 2 µm BOX solved")
    ax[1, 1].axhline(0.1, color="grey", ls=":", lw=0.8)
    ax[1, 1].set(xlabel="buried-oxide thickness (µm)", ylabel="substrate leakage (dB/cm)", ylim=(1e-10, 1e4),
                 title="(d) leakage into the silicon handle")
    ax[1, 1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("lab02_femwell.png", dpi=150)
    print("Saved the figure as lab02_femwell.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv, quick="--quick" in sys.argv)
