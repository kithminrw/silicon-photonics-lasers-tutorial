"""Straight and bent TE0 modes of the 500 x 220 nm silicon strip at 1550 nm (femwell, conformal transformation via
compute_modes(radius=R)), for the Chapter 8 figures: the outward shift of the mode and the mode-mismatch loss at a
straight-bend junction, from the full-vectorial overlap of the two modes.

For each radius the straight and bent modes are solved on the same mesh. The domain stops just inside the radiation
caustic x_r = R (n_eff / n_ox - 1), so the bent mode is computed as a bound mode (its radiation loss, which is
negligible for these radii, is left out; Figure 8.2 takes it from the 1D model).

Runs in the photonics-labs container (femwell_modes.py next to it); writes ch08_bend.json next to this file.
"""
import json, os, sys
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0, ElementVector, ElementDG, ElementTriP1
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

LAM, W, T = 1.55, 0.5, 0.22
HERE = os.path.dirname(os.path.abspath(__file__))


def te0(basis0, eps, R):
    ms = compute_modes(basis0, eps, wavelength=LAM, num_modes=2, order=2, radius=R, n_guess=2.6)
    ms = sorted([m for m in ms if m.te_fraction > 0.5], key=lambda m: -np.real(m.n_eff))
    return ms[0]


def ex_line(m, xl, y=T / 2):
    (et, et_basis), _ = m.basis.split(m.E)
    pb = et_basis.with_element(ElementVector(ElementDG(ElementTriP1())))
    f = et_basis.interpolate(et)
    re = pb.project(np.real(f)); im = pb.project(np.imag(f))
    (exr, bx), _ = pb.split(re); (exi, _), _ = pb.split(im)
    P = np.vstack([xl, np.full_like(xl, y)])
    return bx.probes(P) @ exr + 1j * (bx.probes(P) @ exi)


if __name__ == "__main__":
    out = dict(lam=LAM, w=W, t=T, runs=[])
    for R in [float(a) for a in sys.argv[1:]] or (1.5, 2.0, 3.0, 5.0):
        xr = R * (2.446 / 1.444 - 1)
        xb = min(xr - 0.04, 1.7)
        polys = OrderedDict(core=box(-W / 2, 0, W / 2, T), clad=box(-1.7, -1.3, xb, 1.5))
        mesh = from_meshio(mesh_from_OrderedDict(polys, dict(core={"resolution": 0.04, "distance": 0.4}), default_resolution_max=0.35))
        basis0 = Basis(mesh, ElementTriP0())
        eps = basis0.zeros() + n_sio2(LAM) ** 2
        eps[basis0.get_dofs(elements="core")] = n_si(LAM) ** 2
        ms_, mb = te0(basis0, eps, np.inf), te0(basis0, eps, R)
        c12, c21 = ms_.calculate_overlap(mb), mb.calculate_overlap(ms_)
        eta = float(abs(c12 * c21) / abs(ms_.calculate_power() * mb.calculate_power()))
        xl = np.linspace(-1.0, min(xb, 1.5), 501)
        es, eb = np.abs(ex_line(ms_, xl)) ** 2, np.abs(ex_line(mb, xl)) ** 2
        run = dict(R=R, xb=xb, n_straight=float(np.real(ms_.n_eff)), n_bent=float(np.real(mb.n_eff)), eta=eta,
                   junction_dB=float(-10 * np.log10(eta)), xl=[float(v) for v in xl],
                   ex2_straight=[float(v) for v in es / es.max()], ex2_bent=[float(v) for v in eb / eb.max()],
                   peak_shift=float(xl[np.argmax(eb)] - xl[np.argmax(es)]),
                   centroid_shift=float(np.trapezoid(xl * eb, xl) / np.trapezoid(eb, xl) - np.trapezoid(xl * es, xl) / np.trapezoid(es, xl)))
        out["runs"].append(run)
        print(f"R {R}: domain to {xb:.2f}, n straight {run['n_straight']:.4f}, bent {run['n_bent']:.4f}, eta {eta:.5f}, "
              f"junction {run['junction_dB']:.4f} dB, peak shift {1000*run['peak_shift']:.0f} nm, centroid {1000*run['centroid_shift']:.0f} nm", flush=True)
        json.dump(out, open(os.path.join(HERE, "ch08_bend.json"), "w"))
    print("done")
