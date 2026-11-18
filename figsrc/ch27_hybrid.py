"""Supermodes of a heterogeneous III-V-on-silicon laser waveguide against the silicon width (Chapter 27), with femwell.
Generic stack (illustrative, not any company's process): 500 nm thick Si strip in oxide on a BOX (substrate left out),
30 nm oxide bond layer, n-InP contact layer (110 nm, 12 um wide), then a 3 um wide mesa: MQW active region
(300 nm, average index 3.37), p-InP cladding (1.5 um), p-InGaAs contact (100 nm, index 3.6); air around the mesa.
For each Si width: the TE supermodes' effective indices, their confinement in the MQW and in the Si, and an
intensity map of each of the two lowest TE modes for the demo.
Run: .venv/bin/python figsrc/ch27_hybrid.py   ->  figsrc/ch27_hybrid.json
"""
import json, os
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
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
        cand = []
        for m in ms:
            if m.te_fraction < 0.5: continue
            g_mqw = float(np.real(m.calculate_confinement_factor(elements="mqw")))
            g_si = float(np.real(m.calculate_confinement_factor(elements="si")))
            if g_mqw + g_si > 0.05:                      # hybrid supermodes only (no cap-layer or cladding modes)
                cand.append((m, g_mqw, g_si))
        # the fundamental (highest n_eff) and its partner: the other even mode that shares the silicon
        fund = cand[0]
        others = [c for c in cand[1:] if c[2] > 0.003]
        partner = max(others, key=lambda c: c[2]) if others else (cand[1] if len(cand) > 1 else None)
        rows = []
        for tag, cnd in (("fundamental", fund), ("partner", partner)):
            if cnd is None: continue
            m, g_mqw, g_si = cnd
            r = dict(kind=tag, neff=float(np.real(m.n_eff)), G_mqw=g_mqw, G_si=g_si)
            if any(abs(wsi - x) < 1e-9 for x in MAPS):
                ib, I = m.calculate_intensity()
                v = ib.probes(np.vstack([GX.ravel(), GY.ravel()])) @ I
                v = np.clip(v, 0, None); v /= v.max()
                r["map"] = [int(round(99 * float(x))) for x in v]
            rows.append(r)
        odd = [c for c in cand[1:] if c[2] <= 0.003]
        out["widths"].append(dict(w=wsi, modes=rows, odd_neff=float(np.real(odd[0][0].n_eff)) if odd else None))
        print(f"w_Si {wsi:.2f} um: " + "  ".join(f"[{r['kind'][:4]} n {r['neff']:.4f}, MQW {100*r['G_mqw']:.1f}%, Si {100*r['G_si']:.0f}%]" for r in rows), flush=True)
    out["map"] = dict(x=[-3, 3], y=[-0.6, 2.6], nx=49, ny=27)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "ch27_hybrid.json"), "w"))
