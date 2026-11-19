"""Intensity maps of the fundamental mode of a 220 nm silicon inverse-taper tip in oxide at 1550 nm (Chapter 16,
Figure 16.3), with femwell. Same model as ch16_taper.py (full-vectorial, infinite oxide, no substrate): a 24 um window
for the large modes of the narrow TE tips, 14 um for the others, as in that sweep. The maps are sampled on a common
grid (zero outside the computed window) so that they can be drawn side by side to the same scale.
Run (Docker container with femwell): python -u figsrc/ch16_fields.py  ->  figsrc/ch16_fields.json
Map values: intensity relative to the peak in units of 0.4 dB (integer 25 log10(I/I_max), clipped at -100 = -40 dB). Grid coordinates are relative to the centre of
the silicon core (x across the tip width, y vertical, up positive).
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

LAM, T = 1.55, 0.22
JOBS = [(0.50, "TE", 7.0), (0.20, "TE", 7.0), (0.18, "TE", 7.0), (0.16, "TE", 12.0), (0.14, "TE", 12.0), (0.14, "TM", 7.0)]
GX, GY = np.linspace(-9, 9, 73), np.linspace(-9, 7, 65)            # common window, 0.25 um steps
FX, FY = np.linspace(-1.5, 1.5, 61), np.linspace(-1.5, 1.5, 61)    # fine window for the small modes, 0.05 um steps
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f} s]", *a, flush=True)


def solve(width, pol, half):
    polys = OrderedDict(core=box(-width / 2, 0, width / 2, T), clad=box(-half, -half + T / 2, half, half + T / 2))
    res = dict(core={"resolution": min(0.02, width / 4), "distance": 1.5})
    mesh = from_meshio(mesh_from_OrderedDict(polys, res, default_resolution_max=0.35 if half < 8 else 0.5))
    log(f"  mesh: {mesh.nelements} elements")
    b0 = Basis(mesh, ElementTriP0())
    eps = b0.zeros() + n_sio2(LAM) ** 2
    eps[b0.get_dofs(elements="core")] = n_si(LAM) ** 2
    ms = compute_modes(b0, eps, wavelength=LAM, num_modes=2, order=2)
    log("  modes solved")
    return [m for m in ms if (m.te_fraction > 0.5) == (pol == "TE")][0]


def enc(v):
    """Peak-normalised intensity to integers 25 log10(I), clipped at -100 (-40 dB): a compact log map."""
    return [int(round(25 * np.log10(max(float(x), 1e-4)))) for x in v]


def sample(ib, I, gx, gy, half):
    X, Y = np.meshgrid(gx, gy)
    inside = (np.abs(X) < half - 0.05) & (np.abs(Y) < half - 0.05)
    v = np.zeros(X.size)
    pts = np.vstack([X.ravel()[inside.ravel()], Y.ravel()[inside.ravel()] + T / 2])
    v[inside.ravel()] = ib.probes(pts) @ I
    return np.clip(v, 0, None)


if __name__ == "__main__":
    out = dict(lam=LAM, t=T, grid=dict(x=[-9, 9], y=[-9, 7], nx=len(GX), ny=len(GY)),
               fine=dict(x=[-1.5, 1.5], y=[-1.5, 1.5], nx=len(FX), ny=len(FY)), modes=[])
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch16_fields.json")
    for w, pol, half in JOBS:
        log(f"{pol} {1000 * w:.0f} nm, window {2 * half:.0f} um")
        m = solve(w, pol, half)
        ib, I = m.calculate_intensity()
        # moments on the quadrature points, as in ch16_taper.py (a check against Table 16.1)
        P = np.clip(ib.interpolate(I).value, 0, None) * ib.dx
        X, Y = ib.global_coordinates().value
        P /= P.sum()
        xc, yc = (P * X).sum(), (P * Y).sum()
        sx, sy = np.sqrt((P * (X - xc) ** 2).sum()), np.sqrt((P * (Y - yc) ** 2).sum())
        below = float(P[Y < -2.0].sum())
        v = sample(ib, I, GX, GY, half)
        log("  sampled")
        peak = v.max()
        r = dict(width=w, pol=pol, window=2 * half, neff=float(np.real(m.n_eff)), mfd_x=float(4 * sx), mfd_y=float(4 * sy),
                 below2um=below, map=enc(v / peak))
        if w >= 0.25:
            vf = sample(ib, I, FX, FY, half)
            r["fine"] = enc(vf / vf.max())
        out["modes"].append(r)
        log(f"{pol} {1000*w:.0f} nm: neff {r['neff']:.4f}  MFD {r['mfd_x']:.2f} x {r['mfd_y']:.2f} um  below -2 um {100*below:.1f} %")
        json.dump(out, open(path, "w"))
