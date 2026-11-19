"""Mode fields and thickness sensitivity of SOI channel waveguides (femwell), for the Chapter 6 and 7 figures.

    python ch06_fields.py fields    -> ch06_fields.json
        500 x 220 nm strip at 1550 nm, TE0 and TM0: |E|^2 and the dominant transverse component on a grid;
        rib 500 nm / 220 nm film / 90 nm slab, TE0; slot of two 250 nm rails with a 100 nm gap, 220 nm thick
        (typical, illustrative dimensions), TE0 map and E_x along a line through mid-height.
    python ch06_fields.py tsweep    -> ch06_tsens.json
        TE0 and TM0 n_eff of strips 0.3-1.0 um wide at t = 215 and 225 nm (d n_eff / dt), same mesh settings as
        ch06_sweep.py.

Runs in the photonics-labs container (femwell; femwell_modes.py must sit next to it); figsrc/ch06_figs.py and
ch07_figs.py draw from the JSON files.
"""
import json, os, sys
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0, ElementVector, ElementDG, ElementTriP1
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2, modes

LAM = 1.55
HERE = os.path.dirname(os.path.abspath(__file__))


def solve(polys_si, lam=LAM, num=3, res=0.04, dom=(-1.7, -1.3, 1.7, 1.5), fine=None):
    """Coarse mesh on purpose (shared, busy container): n_eff to about 1e-3, fields for drawing."""
    polys = OrderedDict()
    resolutions = {}
    for k, p in polys_si.items():
        polys[k] = p
        resolutions[k] = {"resolution": (fine or {}).get(k, res), "distance": 0.4}
    polys["clad"] = box(*dom)
    mesh = from_meshio(mesh_from_OrderedDict(polys, resolutions, default_resolution_max=0.35))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(lam) ** 2
    for k in polys_si:
        eps[basis0.get_dofs(elements=k)] = n_si(lam) ** 2
    ms = compute_modes(basis0, eps, wavelength=lam, num_modes=num, order=2, n_guess=3.0)
    return sorted(ms, key=lambda m: -np.real(m.n_eff))


def samplers(m):
    """Functions returning complex E_x, E_y, E_z of mode m at points (2, N)."""
    (et, et_basis), (ez, ez_basis) = m.basis.split(m.E)
    pb = et_basis.with_element(ElementVector(ElementDG(ElementTriP1())))
    f = et_basis.interpolate(et)
    re = pb.project(np.real(f)); im = pb.project(np.imag(f))
    (exr, bx), (eyr, by) = pb.split(re)
    (exi, _), (eyi, _) = pb.split(im)
    sx = lambda P: bx.probes(P) @ exr + 1j * (bx.probes(P) @ exi)
    sy = lambda P: by.probes(P) @ eyr + 1j * (by.probes(P) @ eyi)
    sz = lambda P: ez_basis.probes(P) @ ez
    return sx, sy, sz


def field_map(m, gx, gy, comp):
    """|E|^2 (normalised to 1) and the signed dominant transverse component (normalised to +-1) on the grid."""
    sx, sy, sz = samplers(m)
    G = np.meshgrid(gx, gy)
    P = np.vstack([G[0].ravel(), G[1].ravel()])
    ex, ey, ez = sx(P), sy(P), sz(P)
    I = np.abs(ex) ** 2 + np.abs(ey) ** 2 + np.abs(ez) ** 2
    main = ex if comp == "x" else ey
    k = np.argmax(np.abs(main)); main = main / (main[k] / abs(main[k]))
    s = main.real / np.abs(main.real).max()
    return dict(I=[int(round(999 * float(v))) for v in I / I.max()], main=[int(round(999 * float(v))) for v in s],
                ez_frac=float(np.abs(ez).max() / np.sqrt(I.max())))


def pick(ms, te=True):
    return [m for m in ms if (m.te_fraction > 0.5) == te][0]


def run_fields():
    out = dict(lam=LAM)
    gx, gy = np.linspace(-1.0, 1.0, 161), np.linspace(-0.6, 0.82, 115)
    out["grid"] = dict(x=[-1.0, 1.0, 161], y=[-0.6, 0.82, 115])
    ms = solve(OrderedDict(core=box(-0.25, 0, 0.25, 0.22)))
    te, tm = pick(ms, True), pick(ms, False)
    out["strip"] = dict(te=dict(neff=float(np.real(te.n_eff)), te_frac=float(te.te_fraction), **field_map(te, gx, gy, "x")),
                        tm=dict(neff=float(np.real(tm.n_eff)), te_frac=float(tm.te_fraction), **field_map(tm, gx, gy, "y")))
    print("strip TE0", out["strip"]["te"]["neff"], "TM0", out["strip"]["tm"]["neff"],
          "Ez/|E| max", out["strip"]["te"]["ez_frac"], out["strip"]["tm"]["ez_frac"], flush=True)
    json.dump(out, open(os.path.join(HERE, "ch06_fields.json"), "w"))
    ms = solve(OrderedDict(core=box(-0.25, 0, 0.25, 0.22), slab=box(-2.2, 0, 2.2, 0.09)), dom=(-2.2, -1.3, 2.2, 1.5), fine=dict(slab=0.05))
    te = pick(ms, True)
    gxr = np.linspace(-1.5, 1.5, 201)
    out["rib"] = dict(neff=float(np.real(te.n_eff)), grid=dict(x=[-1.5, 1.5, 201], y=[-0.6, 0.82, 115]), **field_map(te, gxr, gy, "x"))
    print("rib TE0", out["rib"]["neff"], flush=True)
    json.dump(out, open(os.path.join(HERE, "ch06_fields.json"), "w"))
    RW, GAP = 0.25, 0.10
    ms = solve(OrderedDict(left=box(-GAP / 2 - RW, 0, -GAP / 2, 0.22), right=box(GAP / 2, 0, GAP / 2 + RW, 0.22)), res=0.02)
    te = pick(ms, True)
    out["slot"] = dict(neff=float(np.real(te.n_eff)), rail=RW, gap=GAP, **field_map(te, gx, gy, "x"))
    sx, sy, sz = samplers(te)
    xl = np.linspace(-1.0, 1.0, 801)
    ex = sx(np.vstack([xl, np.full_like(xl, 0.11)]))
    k = np.argmax(np.abs(ex)); ex = ex / (ex[k] / abs(ex[k]))
    out["slot"]["xl"] = [float(v) for v in xl]
    out["slot"]["ex_line"] = [round(float(v), 5) for v in ex.real / np.abs(ex.real).max()]
    print("slot TE0", out["slot"]["neff"], flush=True)
    json.dump(out, open(os.path.join(HERE, "ch06_fields.json"), "w"))
    print("done fields")


def run_tsweep():
    out = dict(widths=[], t=[0.215, 0.225], te=[], tm=[])
    for w in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        row_te, row_tm = [], []
        for t in (0.215, 0.225):
            mm = modes(w, LAM, t=t, num=4, res=0.03)
            row_te.append(max([n for n, f in mm if f > 0.5], default=float("nan")))
            row_tm.append(max([n for n, f in mm if f <= 0.5], default=float("nan")))
        out["widths"].append(float(w)); out["te"].append(row_te); out["tm"].append(row_tm)
        print("w", w, "dn/dt TE", (row_te[1] - row_te[0]) / 10, "TM", (row_tm[1] - row_tm[0]) / 10, flush=True)
        json.dump(out, open(os.path.join(HERE, "ch06_tsens.json"), "w"))
    print("done tsweep")


if __name__ == "__main__":
    {"fields": run_fields, "tsweep": run_tsweep}[sys.argv[1]]()
