"""Effective index of the 500 x 220 nm strip (TE0) from 1480 to 1620 nm with femwell, for the synthetic spectra of
the Chapter 32 figures (MZI fringes, n_g from the FSR, Bragg grating); the group index follows from a polynomial fit,
n_g = n_eff - lambda dn_eff/dlambda. Parallel worker processes, one BLAS thread each. Runs in the photonics-labs
container beside femwell_modes.py:
    docker exec -e OMP_NUM_THREADS=1 photonics-labs /opt/conda/envs/labs/bin/python /tmp/<dir>/ch32_disp.py
and writes ch32_disp.json next to itself.

The JSON in figsrc/ comes from a run that was stopped after six of the eight wavelengths (1.48 and 1.54 um missing)
because the shared container was overloaded: its printed n_eff values were copied into ch32_disp.json, with n_g from
the same cubic fit (n_eff 2.4459 and n_g 4.184 at 1550 nm, as in Chapter 6).
"""
import os, sys, json
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from femwell_modes import modes

RES = 0.03


def te0(l):
    n = [m for m in modes(0.5, l, t=0.22, num=2, res=RES) if m[1] > 0.5][0][0]
    print(l, n, flush=True)
    return n


if __name__ == "__main__":
    lams = [round(float(x), 3) for x in np.arange(1.48, 1.6201, 0.02)]
    with Pool(4) as p:
        neff = p.map(te0, lams)
    pf = np.polyfit(np.array(lams) - 1.55, neff, 3)
    dp = np.polyder(pf)
    out = {"lam_um": lams, "neff": neff, "res": RES,
           "ng": [float(n - l * np.polyval(dp, l - 1.55)) for l, n in zip(lams, neff)]}
    print(json.dumps(out))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch32_disp.json"), "w") as f:
        json.dump(out, f, indent=1)
