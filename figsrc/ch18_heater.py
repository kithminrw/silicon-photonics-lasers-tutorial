"""Thermal cross-sections of a silicon phase shifter (Chapter 18), solved with scikit-fem.
Rib waveguide 500 x 220 nm with a 90 nm slab on a 2 um BOX, 2.3 um oxide cladding, air above (insulating).
Heaters: a TiN strip 2 um wide, 120 nm thick, 1.68 um above the silicon ("metal"), or Joule heating in the
doped rib and slab within 1.5 um of the waveguide ("doped"). Configurations: plain, deep trenches 3 um from
the waveguide, and an undercut (substrate removed beneath a 24 um wide, continuous oxide membrane; in a real
device the etch reaches it through periodic openings, which this 2D section leaves out). Per unit length: steady temperature rise, thermal conductance G', the step
response at the waveguide, and a coarse temperature map for the demo.
Run: .venv/bin/python figsrc/ch18_heater.py   ->  figsrc/ch18_heater.json
"""
import json, os, sys
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0, ElementTriP1, BilinearForm, LinearForm, condense, solve
from skfem.helpers import dot, grad
from skfem.io.meshio import from_meshio
from femwell.mesh import mesh_from_OrderedDict
from scipy.sparse.linalg import splu

W, DSUB, TBOX, TCLAD = 40.0, 40.0, 2.0, 2.3
MAT = {  # thermal conductivity W/(m K), volumetric heat capacity J/(m^3 K)
    "si": (148.0, 1.63e6), "sio2": (1.38, 1.60e6), "tin": (28.0, 2.85e6), "air": (0.026, 1.2e3)}


def build(heater, config):
    P = OrderedDict()
    if heater == "metal":
        P["heater"] = box(-1.0, 1.90, 1.0, 2.02)
    P["core"] = box(-0.25, 0.0, 0.25, 0.22)
    if heater == "doped":
        P["hslabL"] = box(-1.5, 0.0, -0.25, 0.09); P["hslabR"] = box(0.25, 0.0, 1.5, 0.09)
    P["slab"] = box(-2.5, 0.0, 2.5, 0.09)
    if config == "trench":       # deep trenches through cladding and BOX, 3 um from the waveguide
        P["trenchL"] = box(-12.0, -TBOX, -3.0, TCLAD); P["trenchR"] = box(3.0, -TBOX, 12.0, TCLAD)
    if config == "undercut":     # substrate etched away beneath (through periodic openings): an oxide membrane
        P["cavity"] = box(-12.0, -TBOX - 6.0, 12.0, -TBOX)
    P["clad"] = box(-W, 0.0, W, TCLAD)
    P["box"] = box(-W, -TBOX, W, 0.0)
    P["sub"] = box(-W, -TBOX - DSUB, W, -TBOX)
    res = {"core": {"resolution": 0.04, "distance": 3}, "slab": {"resolution": 0.06, "distance": 2}}
    if heater == "metal": res["heater"] = {"resolution": 0.04, "distance": 3}
    mesh = from_meshio(mesh_from_OrderedDict(P, res, default_resolution_max=3.0))
    mat = {"heater": "tin", "core": "si", "hslabL": "si", "hslabR": "si", "slab": "si", "trenchL": "air", "trenchR": "air",
           "cavity": "air", "clad": "sio2", "box": "sio2", "sub": "si"}
    return mesh, [n for n in P], mat


def solve_case(heater, config, lam=1.55, dndT=None):
    mesh, names, mat = build(heater, config)
    b0 = Basis(mesh, ElementTriP0()); b1 = Basis(mesh, ElementTriP1())
    k, c, q = b0.zeros(), b0.zeros(), b0.zeros()
    src = ["heater"] if heater == "metal" else ["core", "hslabL", "hslabR"]
    for n in names:
        d = b0.get_dofs(elements=n)
        k[d], c[d] = MAT[mat[n]]
    # heater area from the polygons themselves (um^2)
    A = {"metal": 2.0 * 0.12, "doped": 0.5 * 0.22 + 2 * 1.25 * 0.09}[heater]
    for n in src:
        q[b0.get_dofs(elements=n)] = 1.0 / A          # 1 W per metre of heater, spread over its area (W/(m um^2))
    kk, cc, qq = b0.interpolate(k), b0.interpolate(c), b0.interpolate(q)
    K = BilinearForm(lambda u, v, w: w["k"] * dot(grad(u), grad(v))).assemble(b1, k=kk)       # W/(m K), scale-free in 2D
    M = BilinearForm(lambda u, v, w: w["c"] * u * v).assemble(b1, c=cc) * 1e-12                 # J/(m K): um^2 -> m^2
    f = LinearForm(lambda v, w: w["q"] * v).assemble(b1, q=qq)                                  # W/m
    D = b1.get_dofs(lambda x: np.isclose(x[1], -TBOX - DSUB))
    T = solve(*condense(K, f, D=D))
    X, Y = mesh.p
    core = (np.abs(X) <= 0.25 + 1e-9) & (Y >= -1e-9) & (Y <= 0.22 + 1e-9)
    dT = float(T[core].mean())                     # K per (W/m)
    Gp = 1.0 / dT                                  # W/(m K)
    # step response at the waveguide: implicit Euler on logarithmic time steps
    I = np.setdiff1d(np.arange(b1.N), D)
    Kc, Mc, fc = K[I][:, I].tocsc(), M[I][:, I].tocsc(), f[I]
    ts = np.concatenate([[0], np.logspace(-8, -2.3, 120)])
    u = np.zeros(len(I)); resp = [0.0]; ci = np.where(core[I])[0]
    lu, last = None, None
    for i in range(1, len(ts)):
        dt = ts[i] - ts[i - 1]
        if last is None or abs(dt - last) / dt > 0.02:
            lu = splu((Mc / dt + Kc).tocsc()); last = dt
        u = lu.solve(Mc @ u / dt + fc)
        resp.append(float(u[ci].mean() / dT))
    resp = np.array(resp)
    t10, t63, t90 = [float(np.interp(v, resp, ts)) for v in (0.1, 1 - np.exp(-1), 0.9)]
    # temperature map, normalised to the waveguide
    gx, gy = np.linspace(-12, 12, 61), np.linspace(-4.5, 2.3, 25)
    GX, GY = np.meshgrid(gx, gy)
    tm = (b1.probes(np.vstack([GX.ravel(), GY.ravel()])) @ T).reshape(GX.shape) / dT
    out = dict(heater=heater, config=config, dT_per_Wm=dT, G_per_length=Gp, t10=t10, t63=t63, t90=t90,
               t=[float(x) for x in ts[1::4]], step=[round(float(x), 4) for x in resp[1::4]],
               map=dict(x=[-12, 12], y=[-4.5, 2.3], nx=61, ny=25, v=[round(float(v), 3) for v in tm.ravel()]))
    if dndT:
        out["P_pi_mW"] = 1e3 * lam * 1e-6 * Gp / (2 * dndT)
    return out


if __name__ == "__main__":
    dndT = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0e-4   # effective-index thermo-optic coefficient of the rib, 1/K
    res = []
    for h in ("metal", "doped"):
        for cfg in ("plain", "trench", "undercut"):
            r = solve_case(h, cfg, dndT=dndT)
            res.append(r)
            print(f"{h:5s} {cfg:8s}: dT {r['dT_per_Wm']:.3f} K per mW/mm  G' {r['G_per_length']:.3f} W/(m K)  "
                  f"P_pi {r['P_pi_mW']:.2f} mW  t10/63/90 {r['t10']*1e6:.2f}/{r['t63']*1e6:.2f}/{r['t90']*1e6:.2f} us", flush=True)
    json.dump(dict(dndT=dndT, cases=res), open(os.path.join(os.path.dirname(__file__), "ch18_heater.json"), "w"))
