"""Mode size of a silicon inverse-taper tip against tip width, and its overlap with fibre modes (Chapter 16).
Full-vectorial femwell modes of a 220 nm silicon strip in oxide (no substrate, so substrate leakage is ignored).
Run: .venv/bin/python figsrc/ch16_taper.py   ->  figsrc/ch16_taper.json
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

LAM, T, HALF = 1.55, 0.22, 7.0
FIBRES = {"lensed 2.5 um": 2.5, "UHNA 4 um": 4.0, "SMF-28 10.4 um": 10.4}


def tip_mode(width, pol="TE", HALF=HALF):
    polys = OrderedDict(core=box(-width / 2, 0, width / 2, T), clad=box(-HALF, -HALF + T / 2, HALF, HALF + T / 2))
    res = dict(core={"resolution": min(0.02, width / 4), "distance": 1.5})
    mesh = from_meshio(mesh_from_OrderedDict(polys, res, default_resolution_max=0.35 if HALF < 8 else 0.5))
    b0 = Basis(mesh, ElementTriP0())
    eps = b0.zeros() + n_sio2(LAM) ** 2
    eps[b0.get_dofs(elements="core")] = n_si(LAM) ** 2
    ms = compute_modes(b0, eps, wavelength=LAM, num_modes=2, order=2)
    m = [m for m in ms if (m.te_fraction > 0.5) == (pol == "TE")][0]
    ib, I = m.calculate_intensity()   # returns (basis, values)
    # integrate on the FEM quadrature points (no resampling): intensity moments and Gaussian overlaps
    P = np.clip(ib.interpolate(I).value, 0, None) * ib.dx
    X, Y = ib.global_coordinates().value
    P /= P.sum()
    xc, yc = (P * X).sum(), (P * Y).sum()
    sx, sy = np.sqrt((P * (X - xc) ** 2).sum()), np.sqrt((P * (Y - yc) ** 2).sum())
    # field ~ sqrt(intensity) for a single-signed fundamental mode; overlap with a centred circular Gaussian
    F = np.sqrt(P / ib.dx)
    ov = {}
    for name, mfd in FIBRES.items():
        G = np.exp(-((X - xc) ** 2 + (Y - yc) ** 2) / (mfd / 2) ** 2)
        ov[name] = float(((F * G) * ib.dx).sum() ** 2 / (((F ** 2) * ib.dx).sum() * ((G ** 2) * ib.dx).sum()))
    r = np.hypot(X - xc, Y - yc)
    edge = float(P[r > HALF - 1.0].sum())   # power within 1 um of the window edge: domain check
    sub = float(P[Y < -2.0].sum())          # power more than 2 um below the core: where a 2 um BOX would end
    return dict(width=width, pol=pol, window=2 * HALF, neff=float(np.real(m.n_eff)), mfd_x=float(4 * sx), mfd_y=float(4 * sy),
                overlap=ov, edge=edge, below2um=sub)


if __name__ == "__main__":
    import sys
    path = os.path.join(os.path.dirname(__file__), "ch16_taper.json")
    if len(sys.argv) > 1 and sys.argv[1] == "refine":
        # narrow tips whose mode reaches the 14 um window: redo in a 24 um window and merge
        out = json.load(open(path))
        done = {(round(o["width"], 4), o["pol"]) for o in out if o.get("window", 14) > 20}
        jobs = [(w, "TE") for w in (0.13, 0.135, 0.14, 0.15, 0.16, 0.17)] + [(w, "TM") for w in (0.09, 0.10, 0.12)]
        jobs = [j for j in jobs if (round(j[0], 4), j[1]) not in done]
        half = 12.0
    else:
        out, half = [], HALF
        jobs = [(w, p) for w in (0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.25, 0.30, 0.40, 0.50) for p in ("TE", "TM")]
    for w, pol in jobs:
        try:
            r = tip_mode(w, pol, half)
        except Exception as e:   # mode not found
            print(w, pol, "failed:", e); continue
        out = [o for o in out if not (abs(o["width"] - w) < 1e-9 and o["pol"] == pol)] + [r]
        print(f"w={1000*w:4.0f} nm {pol} (window {2*half:.0f} um): neff {r['neff']:.4f}  MFD {r['mfd_x']:.2f} x {r['mfd_y']:.2f} um  "
              + "  ".join(f"{k.split()[0]} {100*v:.0f}%" for k, v in r["overlap"].items()) + f"  edge {r['edge']:.1e}  below -2um {r['below2um']:.1e}")
        json.dump(sorted(out, key=lambda o: (o["pol"], o["width"])), open(path, "w"), indent=1)
