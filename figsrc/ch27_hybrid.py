"""Supermodes of a heterogeneous III-V-on-silicon laser waveguide against the silicon width (Chapter 27), with femwell.
Generic stack (illustrative, not any company's process): 500 nm thick Si strip in oxide on a BOX (substrate left out),
30 nm oxide bond layer, n-InP contact layer (110 nm, 12 um wide), then a 3 um wide mesa: MQW active region
(300 nm, average index 3.37), p-InP cladding (1.5 um), p-InGaAs contact (100 nm, index 3.6); air around the mesa.
For each Si width: the TE supermodes' effective indices, their confinement in the MQW and in the Si, and, for the
demo and Figure 27.2, maps of the fundamental and its partner (the laterally even mode that shares the silicon most)
on a 49 x 27 grid: "map", the intensity (0..99), and "field",
the signed E_x (-99..99; the mode's phase taken out, the sign chosen so that E_x summed over the MQW region is
positive, so an in-phase supermode is positive in the silicon too and an anti-phase one negative there).
Run: .venv/bin/python figsrc/ch27_hybrid.py   ->  figsrc/ch27_hybrid.json  (femwell; the photonics-labs container)
"""
import json, os
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0, ElementVector, ElementDG, ElementTriP1
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

LAM, TSI, TBOND = 1.55, 0.50, 0.03
N_INP, N_MQW, N_CAP = 3.17, 3.37, 3.60
Y0 = TSI + TBOND                      # bottom of the III-V
LAYERS = [("ncont", 0.11, 6.0, N_INP), ("mqw", 0.30, 1.5, N_MQW), ("pclad", 1.50, 1.5, N_INP), ("cap", 0.10, 1.5, N_CAP)]


def structure(wsi):
    P = OrderedDict(); y = Y0; nmap = {}
    for name, t, half, n in LAYERS:
        P[name] = box(-half, y, half, y + t); nmap[name] = n; y += t
    P["si"] = box(-wsi / 2, 0, wsi / 2, TSI); nmap["si"] = n_si(LAM)
    P["ox"] = box(-6, -1.6, 6, Y0); nmap["ox"] = n_sio2(LAM)              # BOX, side fill and bond layer (no substrate: leakage ignored)
    P["air"] = box(-6, Y0, 6, y + 1.2); nmap["air"] = 1.0
    res = {"si": {"resolution": 0.03, "distance": 1.0}, "mqw": {"resolution": 0.04, "distance": 1.0},
           "ncont": {"resolution": 0.04, "distance": 0.5}}
    mesh = from_meshio(mesh_from_OrderedDict(P, res, default_resolution_max=0.3))
    return mesh, list(P), nmap, y


def ex_field(m, GX, GY, cache):
    """Signed E_x of mode m at the grid points, scaled to -1..1, and the largest imaginary part left (should be ~0).
    cache: a dict shared by the modes of one structure (they share the mesh, so the probe matrix is built once)."""
    (et, et_basis), _ = m.basis.split(m.E)
    pb = et_basis.with_element(ElementVector(ElementDG(ElementTriP1())))
    f = et_basis.interpolate(et)
    (exr, bx), _ = pb.split(pb.project(np.real(f))); (exi, _), _ = pb.split(pb.project(np.imag(f)))
    P = np.vstack([GX.ravel(), GY.ravel()])
    if "probes" not in cache: cache["probes"] = bx.probes(P)
    v = cache["probes"] @ exr + 1j * (cache["probes"] @ exi)
    k = np.argmax(np.abs(v)); v = v / (v[k] / abs(v[k]))          # take out the mode's arbitrary phase
    mqw = (np.abs(P[0]) <= 1.5) & (P[1] >= Y0 + 0.11) & (P[1] <= Y0 + 0.41)
    if v[mqw].real.sum() < 0: v = -v
    return v.real / np.abs(v.real).max(), float(np.abs(v.imag).max() / np.abs(v).max())


if __name__ == "__main__":
    out = dict(lam=LAM, stack=dict(tsi=TSI, tbond=TBOND, layers=[[n, t, h, nn] for n, t, h, nn in LAYERS]), widths=[])
    gx, gy = np.linspace(-3, 3, 49), np.linspace(-0.6, 2.6, 27)
    GX, GY = np.meshgrid(gx, gy)
    MAPS = (0.50, 0.65, 0.75, 0.85, 1.00, 1.50)
    for wsi in (0.40, 0.50, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00, 1.20, 1.50):
        mesh, names, nmap, ytop = structure(wsi)
        b0 = Basis(mesh, ElementTriP0())
        eps = b0.zeros()
        for nme in names:
            eps[b0.get_dofs(elements=nme)] = nmap[nme] ** 2
        ms = compute_modes(b0, eps, wavelength=LAM, num_modes=10, order=2)
        cand, cache = [], {}
        for m in ms:
            if m.te_fraction < 0.5: continue
            g_mqw = float(np.real(m.calculate_confinement_factor(elements="mqw")))
            g_si = float(np.real(m.calculate_confinement_factor(elements="si")))
            if g_mqw + g_si > 0.05:                      # hybrid supermodes only (no cap-layer or cladding modes)
                ex, imag = ex_field(m, GX, GY, cache)
                E = ex.reshape(GX.shape)
                par = float((E * E[:, ::-1]).sum() / (E * E).sum())   # +1: E_x even in x (couples to the centred Si strip), -1: odd
                cand.append((m, g_mqw, g_si, ex, par, imag))
        # the fundamental (highest n_eff) and its partner: the other laterally even mode that shares the silicon most.
        # Even and odd are told apart by the symmetry of E_x (an odd mode can still put energy in a wide silicon strip)
        fund = cand[0]
        even = [c for c in cand[1:] if c[4] > 0]
        others = [c for c in even if c[2] > 0.003]
        partner = max(others, key=lambda c: c[2]) if others else (even[0] if even else None)
        rows = []
        for tag, cnd in (("fundamental", fund), ("partner", partner)):
            if cnd is None: continue
            m, g_mqw, g_si, ex, par, imag = cnd
            r = dict(kind=tag, neff=float(np.real(m.n_eff)), G_mqw=g_mqw, G_si=g_si)
            if any(abs(wsi - x) < 1e-9 for x in MAPS):
                ib, I = m.calculate_intensity()
                v = ib.probes(np.vstack([GX.ravel(), GY.ravel()])) @ I
                v = np.clip(v, 0, None); v /= v.max()
                r["map"] = [int(round(99 * float(x))) for x in v]
                r["field"] = [int(round(99 * float(x))) for x in ex]
                print(f"    {tag}: E_x map, imaginary residue {imag:.1e}, min {ex.min():+.2f}", flush=True)
            rows.append(r)
        # the III-V mesa's own odd mode: odd in x, so it cannot couple to the centred strip's even modes; listed while it
        # stays out of the silicon (< 5 %: a strip wider than about 1.2 um guides an odd mode of its own, and the two mix).
        # Every candidate is listed in "cands" as [n_eff, G_mqw, G_si, parity]
        odd = [c for c in cand[1:] if c[4] < 0 and c[1] > c[2] and c[2] < 0.05]
        out["widths"].append(dict(w=wsi, modes=rows, odd_neff=float(np.real(odd[0][0].n_eff)) if odd else None,
                                  cands=[[round(float(np.real(c[0].n_eff)), 5), round(c[1], 4), round(c[2], 4), round(c[4], 3)] for c in cand]))
        print(f"    candidates: " + "  ".join(f"[n {np.real(c[0].n_eff):.4f} MQW {100*c[1]:.1f}% Si {100*c[2]:.1f}% parity {c[4]:+.2f}]" for c in cand), flush=True)
        print(f"w_Si {wsi:.2f} um: " + "  ".join(f"[{r['kind'][:4]} n {r['neff']:.4f}, MQW {100*r['G_mqw']:.1f}%, Si {100*r['G_si']:.0f}%]" for r in rows), flush=True)
    out["map"] = dict(x=[-3, 3], y=[-0.6, 2.6], nx=49, ny=27)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "ch27_hybrid.json"), "w"))
