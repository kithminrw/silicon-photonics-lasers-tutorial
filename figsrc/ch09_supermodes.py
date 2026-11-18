"""Even and odd supermodes of two 500 x 220 nm silicon strips (femwell) against gap and wavelength.
Gives the cross-over length L_x = lambda / (2 (n_even - n_odd)) for Chapter 9 and checks the
directional-coupler demo's model. Writes figsrc/ch09_supermodes.json.
Run: .venv/bin/python figsrc/ch09_supermodes.py"""
import json, os
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2


def pair(gap, lam, w=0.5, t=0.22, res=0.025):
    a = box(-gap / 2 - w, 0, -gap / 2, t); b = box(gap / 2, 0, gap / 2 + w, t)
    polys = OrderedDict(left=a, right=b, clad=box(-3.5, -2.0, 3.5, 2.0))
    resolutions = dict(left={"resolution": res, "distance": 0.6}, right={"resolution": res, "distance": 0.6})
    mesh = from_meshio(mesh_from_OrderedDict(polys, resolutions, default_resolution_max=0.25))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(lam) ** 2
    for k in ("left", "right"):
        eps[basis0.get_dofs(elements=k)] = n_si(lam) ** 2
    ms = compute_modes(basis0, eps, wavelength=lam, num_modes=4, order=2)
    te = sorted([float(np.real(m.n_eff)) for m in ms if m.te_fraction > 0.5], reverse=True)
    return te[0], te[1]


if __name__ == "__main__":
    out = {"gap": [], "lam": [], "n_even": [], "n_odd": [], "Lx": []}
    for lam in (1.55,):
        for gap in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4):
            ne, no = pair(gap, lam)
            Lx = lam / (2 * (ne - no))
            print(f"lambda {lam} gap {gap}: n_even {ne:.4f} n_odd {no:.4f} dn {ne-no:.4f} L_x {Lx:.1f} um", flush=True)
            for k, v in zip(out, (gap, lam, ne, no, Lx)): out[k].append(v)
    for lam in (1.50, 1.60):
        ne, no = pair(0.2, lam); Lx = lam / (2 * (ne - no))
        print(f"lambda {lam} gap 0.2: dn {ne-no:.4f} L_x {Lx:.1f} um", flush=True)
        for k, v in zip(out, (0.2, lam, ne, no, Lx)): out[k].append(v)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "ch09_supermodes.json"), "w"), indent=1)
    print("done")
