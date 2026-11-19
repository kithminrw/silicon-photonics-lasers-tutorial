"""Mode fields of silicon strips and coupled pairs (femwell), for the Chapter 9 and 10 figures.

1. Two 500 x 220 nm strips, 200 nm gap, 1550 nm: the even and odd TE supermodes (n_eff, E_x on a cross-section grid
   and along a line through the strips' mid-height).
2. Single strips 500 nm (the Y-branch input and arms) and 1200 nm (the Y-branch stem): TE0 and TE1 along the line.
3. An asymmetric pair (widths w1 + w2 = 1 um, 200 nm gap) at several width differences, as along an adiabatic
   3 dB coupler: the two TE supermodes' n_eff and E_x along the line.

A deliberately light run (two modes per structure, 35 nm mesh at the cores, order-2 elements, two BLAS threads):
the profiles are for drawing; the effective indices quoted in the chapters come from ch09_supermodes.py and
ch06_sweep.py. The JSON is rewritten after every structure, so a partial run is usable.
Runs in the photonics-labs container (femwell); writes figsrc/ch09_fields.json next to this file, which
figsrc/ch09_figs.py and figsrc/ch10_figs.py draw from. Run: python figsrc/ch09_fields.py
"""
import json, os, time
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0, ElementVector, ElementDG, ElementTriP1
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

LAM, T, GAP, RES = 1.55, 0.22, 0.20, 0.035
XL = np.linspace(-2.0, 2.0, 401)                 # line cut through mid-height (um)
GX, GY = np.linspace(-1.6, 1.6, 161), np.linspace(-0.5, 0.72, 62)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch09_fields.json")


def solve(cores, num=2):
    """TE-like modes (highest n_eff first) of strips cores = [(x_left, width), ...] in oxide."""
    polys = OrderedDict((f"c{i}", box(x0, 0, x0 + w, T)) for i, (x0, w) in enumerate(cores))
    polys["clad"] = box(-2.6, -1.5, 2.6, 1.6)
    res = {k: {"resolution": RES, "distance": 0.5} for k in polys if k != "clad"}
    mesh = from_meshio(mesh_from_OrderedDict(polys, res, default_resolution_max=0.3))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(LAM) ** 2
    for k in res:
        eps[basis0.get_dofs(elements=k)] = n_si(LAM) ** 2
    ms = compute_modes(basis0, eps, wavelength=LAM, num_modes=num, order=2)
    return sorted([m for m in ms if m.te_fraction > 0.5], key=lambda m: -np.real(m.n_eff))


def ex_sampler(m):
    """Return a function giving the complex E_x of mode m at points (2, N)."""
    (et, et_basis), _ = m.basis.split(m.E)
    pb = et_basis.with_element(ElementVector(ElementDG(ElementTriP1())))
    f = et_basis.interpolate(et)
    re = pb.project(np.real(f)); im = pb.project(np.imag(f))
    (exr, bx), _ = pb.split(re); (exi, _), _ = pb.split(im)
    return lambda P: bx.probes(P) @ exr + 1j * (bx.probes(P) @ exi)


def line_and_map(m, want_map=False, xref=-GAP / 2 - 0.25):
    """E_x along the mid-height line (real, unit integral of |E_x|^2, positive at x = xref) and optionally on the grid."""
    s = ex_sampler(m)
    line = s(np.vstack([XL, np.full_like(XL, T / 2)]))
    k = np.argmax(np.abs(line)); ph = line[k] / abs(line[k])
    line = line / ph
    if line[np.argmin(np.abs(XL - xref))].real < 0:
        line = -line; ph = -ph
    pw = np.trapezoid(np.abs(line) ** 2, XL)
    out = dict(n=float(np.real(m.n_eff)), line=[round(float(v), 5) for v in (line.real / np.sqrt(pw))],
               imag_frac=float(np.abs(line.imag).max() / np.abs(line).max()))
    if want_map:
        G = np.meshgrid(GX, GY)
        v = s(np.vstack([G[0].ravel(), G[1].ravel()])) / ph
        v = v.real / np.abs(v.real).max()
        out["map"] = [int(round(99 * float(x))) for x in v]
    return out


def dump(out):
    json.dump(out, open(OUT, "w"))


if __name__ == "__main__":
    t0 = time.time()
    out = dict(lam=LAM, t=T, gap=GAP, res=RES, xl=[float(x) for x in XL], grid=dict(x=[-1.6, 1.6, 161], y=[-0.5, 0.72, 62]))
    # 1. symmetric pair
    te = solve([(-GAP / 2 - 0.5, 0.5), (GAP / 2, 0.5)])
    ne, no = float(np.real(te[0].n_eff)), float(np.real(te[1].n_eff))
    out["sym"] = dict(n_even=ne, n_odd=no, Lx=LAM / (2 * (ne - no)), even=line_and_map(te[0], True), odd=line_and_map(te[1], True))
    dump(out)
    print(f"[{time.time()-t0:.0f} s] pair 500/500, gap {GAP}: n_even {ne:.4f} n_odd {no:.4f} L_x {LAM/(2*(ne-no)):.1f} um", flush=True)
    # 2. single strips
    out["strips"] = []
    for w in (0.5, 1.2):
        te = solve([(-w / 2, w)])
        te = [m for m in te if np.real(m.n_eff) > n_sio2(LAM) + 1e-3]
        out["strips"].append(dict(w=w, n=[float(np.real(m.n_eff)) for m in te], modes=[line_and_map(m, xref=-0.15)["line"] for m in te]))
        dump(out)
        print(f"[{time.time()-t0:.0f} s] strip {w} um: TE n_eff {[round(float(np.real(m.n_eff)), 4) for m in te]}", flush=True)
    # 3. asymmetric pairs along an adiabatic coupler (narrow guide on the left, wide on the right)
    out["asym"] = []
    for dw in (0.20, 0.10, 0.04, 0.0):
        w1, w2 = 0.5 - dw / 2, 0.5 + dw / 2
        if dw == 0.0:
            r = dict(w1=w1, w2=w2, n1=ne, n2=no, m1=dict(line=out["sym"]["even"]["line"]), m2=dict(line=out["sym"]["odd"]["line"]))
        else:
            te = solve([(-GAP / 2 - w1, w1), (GAP / 2, w2)])
            r = dict(w1=w1, w2=w2, n1=float(np.real(te[0].n_eff)), n2=float(np.real(te[1].n_eff)),
                     m1=line_and_map(te[0]), m2=line_and_map(te[1]))
        out["asym"].append(r); dump(out)
        print(f"[{time.time()-t0:.0f} s] asym {w1:.2f}/{w2:.2f}: n {r['n1']:.4f} / {r['n2']:.4f}", flush=True)
    print("done", flush=True)
