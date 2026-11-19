"""Chapter 32: femwell reference for Worked Example 32.1 and Section 32.5 (run in the photonics-labs container).

    MSYS_NO_PATHCONV=1 docker exec -e OMP_NUM_THREADS=1 -w /repo/figsrc photonics-labs /opt/conda/envs/labs/bin/python ch32_femwell.py

Writes ch32_femwell.json:
  conv     TE0 and TM0 n_eff of the 500 x 220 nm strip at 1550 nm against the element size in the core (femwell's
           triangular mesh follows the core's faces, so it converges smoothly)
  ng       TE0 group index with material dispersion (Li silicon, Malitson silica) and with both indices frozen at their
           1550 nm values (Section 32.5, step 2)
"""
import json, time
import numpy as np
from femwell_modes import modes, n_si, n_sio2
from collections import OrderedDict
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict

out = {"conv": []}
for res in (0.08, 0.06, 0.045, 0.035, 0.025, 0.018, 0.013, 0.010):
    t0 = time.time()
    ms = modes(0.5, 1.55, res=res)
    te = [n for n, f in ms if f > 0.5][0]; tm = [n for n, f in ms if f <= 0.5][0]
    r = {"res_um": res, "neff_TE": te, "neff_TM": tm, "seconds": time.time() - t0}
    print(r, flush=True); out["conv"].append(r)


def te0_const(lam, n_core, n_clad, res=0.018):
    polys = OrderedDict(core=box(-0.25, 0, 0.25, 0.22), clad=box(-3, -2.0, 3, 2.0))
    mesh = from_meshio(mesh_from_OrderedDict(polys, {"core": {"resolution": res, "distance": 0.6}}, default_resolution_max=0.25))
    b0 = Basis(mesh, ElementTriP0())
    eps = b0.zeros() + n_clad ** 2
    eps[b0.get_dofs(elements="core")] = n_core ** 2
    ms = compute_modes(b0, eps, wavelength=lam, num_modes=2, order=2)
    return [float(np.real(m.n_eff)) for m in ms if m.te_fraction > 0.5][0]


d = 0.01
disp = [modes(0.5, l, res=0.018) for l in (1.55 - d, 1.55, 1.55 + d)]
nte = [[n for n, f in m if f > 0.5][0] for m in disp]
ng_disp = nte[1] - 1.55 * (nte[2] - nte[0]) / (2 * d)
nc = [te0_const(l, n_si(1.55), n_sio2(1.55)) for l in (1.55 - d, 1.55, 1.55 + d)]
ng_const = nc[1] - 1.55 * (nc[2] - nc[0]) / (2 * d)
out["ng"] = {"neff_TE": nte[1], "ng_dispersive": ng_disp, "ng_constant_index": ng_const}
print(out["ng"])
json.dump(out, open("ch32_femwell.json", "w"), indent=1)
print("wrote ch32_femwell.json")
