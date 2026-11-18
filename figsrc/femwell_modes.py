"""Full-vectorial modes of SOI channel waveguides with femwell (open-source FEM).
Used for the numbers and figures of Chapter 6. Run: .venv/bin/python figsrc/femwell_modes.py [quick]
"""
import sys
from collections import OrderedDict
import numpy as np
from shapely.geometry import box, Polygon
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict

def n_si(l):
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / l**2 + 0.00810461 * l1**2 / (l**2 - l1**2))

def n_sio2(l):
    return np.sqrt(1 + 0.6961663 * l**2 / (l**2 - 0.0684043**2) + 0.4079426 * l**2 / (l**2 - 0.1162414**2)
                   + 0.8974794 * l**2 / (l**2 - 9.896161**2))

def modes(width, lam, t=0.22, slab=0.0, num=4, res=0.025):
    """Modes of a strip (slab=0) or rib (slab>0) waveguide in oxide; returns list of (n_eff, te_fraction)."""
    core = box(-width / 2, 0, width / 2, t)
    polys = OrderedDict(core=core)
    if slab > 0:
        polys["slab"] = box(-3, 0, 3, slab)
    polys["clad"] = box(-3, -2.0, 3, 2.0)
    resolutions = dict(core={"resolution": res, "distance": 0.6})
    if slab > 0:
        resolutions["slab"] = {"resolution": 0.04, "distance": 0.4}
    mesh = from_meshio(mesh_from_OrderedDict(polys, resolutions, default_resolution_max=0.25))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(lam) ** 2
    eps[basis0.get_dofs(elements="core")] = n_si(lam) ** 2
    if slab > 0:
        eps[basis0.get_dofs(elements="slab")] = n_si(lam) ** 2
    ms = compute_modes(basis0, eps, wavelength=lam, num_modes=num, order=2)
    out = [(float(np.real(m.n_eff)), float(m.te_fraction)) for m in ms]
    return [o for o in out if o[0] > n_sio2(lam) + 1e-3]

def ng(width, lam, pol="TE", **kw):
    d = 0.01
    def pick(l):
        ms = modes(width, l, **kw)
        cand = [m for m in ms if (m[1] > 0.5) == (pol == "TE")]
        return cand[0][0] if cand else np.nan
    n0, n1, n2 = pick(lam - d), pick(lam), pick(lam + d)
    return n1, n1 - lam * (n2 - n0) / (2 * d)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        for lam in (1.55, 1.31):
            ms = modes(0.5, lam)
            print(lam, [(round(n, 4), round(te, 2)) for n, te in ms])
            print("  TE ng:", [round(x, 3) for x in ng(0.5, lam, "TE")], " TM ng:", [round(x, 3) for x in ng(0.5, lam, "TM")])
