"""Lateral PN phase shifter in a 500 x 220 nm rib (90 nm slab) at 1550 nm (Chapter 19).
1. femwell TE0 mode of the rib; 2. its sensitivity to the silicon index, binned across the width:
   w(x) = d n_eff / d n_Si(x) per um of width, from first-order perturbation (Mode.calculate_pertubated_neff);
3. a check against a direct solve with a doped, partly depleted junction; 4. the Soref-Bennett phase shift,
   loss and V_pi L against bias for a few dopings.
Run: .venv/bin/python figsrc/ch19_pn.py   ->  figsrc/ch19_pn.json
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

LAM, W, T, SLAB = 1.55, 0.5, 0.22, 0.09
Q, EPS0, KT, NI = 1.602e-19, 8.854e-12, 0.02585, 1.0e10


def rib():
    P = OrderedDict(core=box(-W / 2, 0, W / 2, T), slab=box(-3, 0, 3, SLAB), clad=box(-3.5, -2.0, 3.5, 2.0))
    res = {"core": {"resolution": 0.015, "distance": 0.6}, "slab": {"resolution": 0.02, "distance": 0.4}}
    mesh = from_meshio(mesh_from_OrderedDict(P, res, default_resolution_max=0.25))
    b0 = Basis(mesh, ElementTriP0())
    si = np.concatenate([b0.get_dofs(elements="core"), b0.get_dofs(elements="slab")])
    return mesh, b0, si


def solve(b0, eps):
    ms = compute_modes(b0, eps, wavelength=LAM, num_modes=2, order=2)
    return [m for m in ms if m.te_fraction > 0.5][0]


def soref(N, P):   # 1550 nm, cm^-3 -> (delta n, delta alpha in 1/cm)
    return -(8.8e-22 * N + 8.5e-18 * P ** 0.8), 8.5e-18 * N + 6.0e-18 * P


def depletion(Na, Nd, V):   # reverse bias V > 0; returns (xp, xn) in um
    vbi = KT * np.log(Na * Nd / NI ** 2)
    na, nd = Na * 1e6, Nd * 1e6
    Wd = np.sqrt(2 * 11.7 * EPS0 * (vbi + V) * (na + nd) / (Q * na * nd))
    return 1e6 * Wd * nd / (na + nd), 1e6 * Wd * na / (na + nd), vbi


if __name__ == "__main__":
    mesh, b0, si = rib()
    nS, nO = n_si(LAM), n_sio2(LAM)
    eps = b0.zeros() + nO ** 2; eps[si] = nS ** 2
    m = solve(b0, eps)
    neff0 = float(np.real(m.n_eff)); print("rib TE0 n_eff", neff0)
    # element centroids of the silicon
    cx = mesh.p[0, mesh.t].mean(axis=0)
    edges = np.arange(-2.0, 2.0001, 0.02); centres = 0.5 * (edges[1:] + edges[:-1]); wts = []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = si[(cx[si] >= a) & (cx[si] < b)]
        de = b0.zeros(); de[sel] = 2 * nS * 1e-4              # delta n = 1e-4 in this strip of silicon
        wts.append(float(np.real(m.calculate_pertubated_neff(de) - m.n_eff)) / 1e-4 / (b - a))
    wts = np.array(wts)
    print("integral of w over x (= d n_eff / d n_Si for all silicon):", float(np.sum(wts) * 0.02))

    def dneff_weights(Na, Nd, V, xj=0.0, contact=1.2, Nc=1e20):
        """sum of w(x) * complex delta n(x) dx, with each 20 nm bin split exactly at the depletion edges."""
        xp, xn, _ = depletion(Na, Nd, V)
        def seg(a, b, lo, hi):   # length of [a, b] inside [lo, hi]
            return max(0.0, min(b, hi) - max(a, lo))
        def cplx(N, P):
            d_n, d_a = soref(N, P)
            return d_n + 1j * d_a * 100 * LAM * 1e-6 / (4 * np.pi)   # alpha 1/cm -> 1/m; kappa = lambda alpha / (4 pi)
        tot = 0j
        for a, b, wv in zip(edges[:-1], edges[1:], wts):
            tot += wv * (seg(a, b, -9, -contact) * cplx(0, Nc) + seg(a, b, -contact, xj - xp) * cplx(0, Na)
                         + seg(a, b, xj + xn, contact) * cplx(Nd, 0) + seg(a, b, contact, 9) * cplx(Nc, 0))
        return complex(tot)

    # direct check: 5e17/5e17 at 0 V and 2 V, index change only, against the weights
    def direct(Na, Nd, V):
        xp, xn, _ = depletion(Na, Nd, V)
        e = eps.copy()
        for sel_fn, (N, P) in ((lambda x: x <= -xp, (0, Na)), (lambda x: x >= xn, (Nd, 0))):
            sel = si[sel_fn(cx[si]) & (np.abs(cx[si]) <= 1.2)]
            e[sel] = (nS + soref(N, P)[0]) ** 2
        return float(np.real(solve(b0, e).n_eff)) - neff0
    for V in (0.0, 2.0):
        print(f"check 5e17, {V} V: direct {direct(5e17, 5e17, V):.4e}  weights {dneff_weights(5e17, 5e17, V, Nc=0).real:.4e}")

    out = dict(lam=LAM, neff=neff0, x=[round(float(c), 3) for c in centres], w=[round(float(v), 5) for v in wts], cases=[])
    for N in (2e17, 5e17, 1e18):
        d0 = dneff_weights(N, N, 0.0)
        rows = []
        for V in (0.5, 1, 2, 3, 4):
            dv = dneff_weights(N, N, V) - d0
            vpil = LAM * 1e-4 / (2 * dv.real) * V            # V cm  (lambda in cm)
            rows.append(dict(V=V, dneff=dv.real, VpiL_Vcm=vpil))
        a0 = 4 * np.pi * d0.imag / (LAM * 1e-6) / 100 * 4.343   # dB/cm
        xp, xn, vbi = depletion(N, N, 0)
        out["cases"].append(dict(N=N, vbi=vbi, W0_nm=1000 * (xp + xn), loss_dB_cm=a0, rows=rows))
        print(f"N = {N:.0e}: Vbi {vbi:.3f} V, W0 {1000*(xp+xn):.0f} nm, loss {a0:.2f} dB/cm; "
              + "  ".join(f"{r['V']} V: dn {r['dneff']:.2e}, VpiL {r['VpiL_Vcm']:.2f}" for r in rows))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "ch19_pn.json"), "w"))
