"""Mode fields of the Chapter 34 biosensor waveguide (500 x 220 nm Si strip, oxide below, water above), with femwell.
Same structure as figsrc/ch34_sensor.py (which gives the sensitivities), on a smaller domain and a coarser mesh: one
solve at 1550 nm for TE0 and TM0, giving n_eff, the confinement in the core and in the water, and the power density
(Poynting z) on a grid for Figure 34.1.
Runs in the photonics-labs container (femwell), with few threads:
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python ch34_fields.py   ->  ch34_fields.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

LAM, NW, W, T = 1.55, 1.318, 0.5, 0.22

if __name__ == "__main__":
    P = OrderedDict(core=box(-W / 2, 0, W / 2, T), water=box(-2.0, 0, 2.0, 1.8), box=box(-2.0, -1.4, 2.0, 0))
    mesh = from_meshio(mesh_from_OrderedDict(P, {"core": {"resolution": 0.03, "distance": 0.5}}, default_resolution_max=0.2))
    b0 = Basis(mesh, ElementTriP0()); eps = b0.zeros()
    eps[b0.get_dofs(elements="core")] = n_si(LAM) ** 2
    eps[b0.get_dofs(elements="water")] = NW ** 2
    eps[b0.get_dofs(elements="box")] = n_sio2(LAM) ** 2
    print("elements:", mesh.t.shape[1], flush=True)
    ms = compute_modes(b0, eps, wavelength=LAM, num_modes=3, order=2)
    te = [m for m in ms if m.te_fraction > 0.5][0]; tm = [m for m in ms if m.te_fraction < 0.5][0]
    gx, gy = np.linspace(-1.2, 1.2, 121), np.linspace(-0.6, 1.0, 81)
    GX, GY = np.meshgrid(gx, gy)
    out = dict(lam=LAM, n_water=NW, n_si=float(n_si(LAM)), n_ox=float(n_sio2(LAM)), w=W, t=T,
               grid=dict(x=[-1.2, 1.2], y=[-0.6, 1.0], nx=121, ny=81), modes={})
    for name, m in (("TE", te), ("TM", tm)):
        g_core = float(np.real(m.calculate_confinement_factor(elements="core")))
        g_water = float(np.real(m.calculate_confinement_factor(elements="water")))
        ib, I = m.calculate_intensity()
        v = ib.probes(np.vstack([GX.ravel(), GY.ravel()])) @ I
        v = np.clip(v, 0, None); v /= v.max()
        out["modes"][name] = dict(neff=float(np.real(m.n_eff)), te_fraction=float(m.te_fraction), conf_core=g_core,
                                  conf_water=g_water, map=[int(round(999 * float(x))) for x in v])
        print(f"{name}: n_eff {float(np.real(m.n_eff)):.4f}, TE fraction {float(m.te_fraction):.3f}, "
              f"confinement core {g_core:.3f}, water {g_water:.3f}", flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch34_fields.json"), "w"))
    print("done", flush=True)
