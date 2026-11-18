"""Bulk sensitivity of a 500 x 220 nm silicon strip in water (Chapter 34), with femwell.
Oxide below (BOX), water above and at the sides. For TE0 and TM0: n_eff, group index, d n_eff / d n_water, and the
ring-resonance bulk sensitivity S = (lambda / n_g) d n_eff / d n_water in nm per refractive-index unit.
Run: .venv/bin/python figsrc/ch34_sensor.py
"""
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

def modes(lam, nw, w=0.5, t=0.22):
    P = OrderedDict(core=box(-w / 2, 0, w / 2, t), water=box(-3, 0, 3, 2.5), box=box(-3, -2.0, 3, 0))
    mesh = from_meshio(mesh_from_OrderedDict(P, {"core": {"resolution": 0.02, "distance": 0.8}}, default_resolution_max=0.25))
    b0 = Basis(mesh, ElementTriP0()); eps = b0.zeros()
    eps[b0.get_dofs(elements="core")] = n_si(lam) ** 2
    eps[b0.get_dofs(elements="water")] = nw ** 2
    eps[b0.get_dofs(elements="box")] = n_sio2(lam) ** 2
    ms = compute_modes(b0, eps, wavelength=lam, num_modes=3, order=2)
    te = [m for m in ms if m.te_fraction > 0.5][0]; tm = [m for m in ms if m.te_fraction < 0.5][0]
    return float(np.real(te.n_eff)), float(np.real(tm.n_eff))

NW = 1.318   # water near 1550 nm
lam = 1.55
base = modes(lam, NW); up = modes(lam, NW + 0.01); lo_l = modes(lam - 0.01, NW); hi_l = modes(lam + 0.01, NW)
for k, name in enumerate(("TE", "TM")):
    dndn = (up[k] - base[k]) / 0.01
    ng = base[k] - lam * (hi_l[k] - lo_l[k]) / 0.02
    print(f"{name}: n_eff {base[k]:.4f}, n_g {ng:.3f}, dn_eff/dn_water {dndn:.3f}, S = {1000*lam*dndn/ng:.0f} nm/RIU")
