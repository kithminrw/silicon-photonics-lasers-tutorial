"""Chapter 32: numbers from the Tidy3D Python package (local only: no account, nothing sent to the cloud).

    MSYS_NO_PATHCONV=1 docker exec -w /repo photonics-labs /opt/t3d/bin/python figsrc/ch32_tidy3d.py

Tidy3D 2.12.2, installed with pip in a virtual environment inside the photonics-labs container (/opt/t3d, made with
--system-site-packages from /opt/conda/envs/labs, which has 2.11.2). Writes figsrc/ch32_tidy3d.json with

  fit    the Li (1980) silicon index between 1.2 and 2.0 um fitted with 1 and 2 poles (FastDispersionFitter), and
         the error of each fit across the band (Section 32.5, Figure 32.5);
  modes  n_eff of the TE0 and TM0 modes of the 500 x 220 nm strip from the LOCAL mode solver against the auto-grid
         density (minimum steps per wavelength), the convergence check of Worked Example 32.1. The local solver has no
         sub-pixel averaging (its documentation says so and it warns), and the auto-grid puts grid lines on the core's
         faces, where the tangential E samples sit exactly on the interface: the answer then jumps with the grid;
  bend   cells, time steps and time step of the 3D bend set-up of figsrc/ch32_tidy3d_bend.py against the grid
         density, with and without the mirror plane (Worked Example 32.2). Only built and validated, never run.
"""
import json, os, time
import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver
from tidy3d.plugins.dispersion import FastDispersionFitter

HERE = os.path.dirname(os.path.abspath(__file__))
out = {"tidy3d_version": td.__version__}


def n_si_li(l):                                       # Li (1980), room temperature, l in um
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / l**2 + 0.00810461 * l1**2 / (l**2 - l1**2))


# ---------------------------------------------------------------- material fit
wl = np.linspace(1.2, 2.0, 81)
fits = {}
for npoles in (1, 2):
    med, rms = FastDispersionFitter(wvl_um=wl, n_data=n_si_li(wl)).fit(min_num_poles=npoles, max_num_poles=npoles,
                                                                       tolerance_rms=1e-12)
    wl_fine = np.linspace(1.2, 2.0, 321)
    n_fit = np.array([med.nk_model(td.C_0 / x)[0] for x in wl_fine])
    fits[str(npoles)] = {"rms": float(rms), "wl": list(wl_fine), "n_fit": list(n_fit),
                         "err": list(n_fit - n_si_li(wl_fine))}
    print("fit", npoles, "pole(s): weighted rms", rms, " max |dn|", np.abs(n_fit - n_si_li(wl_fine)).max())
out["fit"] = fits

# ---------------------------------------------------------------- mode-solver convergence (local, no subpixel)
lam0 = 1.55
freq0 = td.C_0 / lam0
si = td.Medium(permittivity=n_si_li(lam0) ** 2)
sio2 = td.Medium(permittivity=1.444023621703261 ** 2)        # Malitson at 1550 nm (Chapter 6)
core = td.Structure(geometry=td.Box(center=(0, 0, 0.11), size=(td.inf, 0.5, 0.22)), medium=si)
rows = []
for spw in range(10, 62, 2):
    sim = td.Simulation(center=(0, 0, 0.11), size=(2, 3, 3), medium=sio2, structures=[core],
                        grid_spec=td.GridSpec.auto(min_steps_per_wvl=spw, wavelength=lam0),
                        boundary_spec=td.BoundarySpec.all_sides(td.PML()), run_time=1e-12)
    plane = td.Box(center=(0, 0, 0.11), size=(0, 3, 3))
    t0 = time.time()
    m = ModeSolver(simulation=sim, plane=plane, freqs=[freq0],
                   mode_spec=td.ModeSpec(num_modes=2, target_neff=3.0)).solve()
    ne = np.ravel(m.n_eff.values); te = np.ravel(m.pol_fraction.te.values)
    gy = np.diff(sim.grid.boundaries.y); gz = np.diff(sim.grid.boundaries.z)
    r = {"steps_per_wvl": spw, "dmin_nm": float(min(gy.min(), gz.min()) * 1e3), "ny": len(gy), "nz": len(gz),
         "neff_TE": float(ne[np.argmax(te)]), "neff_TM": float(ne[np.argmin(te)]), "seconds": time.time() - t0}
    print(r); rows.append(r)
out["modes"] = rows

# ---------------------------------------------------------------- bend: grid size against grid density
src = open(os.path.join(HERE, "ch32_tidy3d_bend.py")).read().split("sim.validate_pre_upload()")[0]
ns = {}
exec(src, ns)
base = ns["sim"]
rows = []
for spw, sym in ((10, (0, 0, 1)), (15, (0, 0, 1)), (20, (0, 0, 1)), (30, (0, 0, 1)), (20, (0, 0, 0))):
    if True:
        s = base.updated_copy(grid_spec=td.GridSpec.auto(min_steps_per_wvl=spw, wavelength=lam0), symmetry=sym)
        s.validate_pre_upload()
        steps = [np.diff(b) for b in s.grid.boundaries.to_list]
        r = {"steps_per_wvl": spw, "symmetry": list(sym), "num_cells": int(s.num_cells),
             "computational_points": int(s.num_computational_grid_points), "time_steps": int(s.num_time_steps),
             "dt_fs": s.dt * 1e15, "grid": [len(d) for d in steps], "dmin_nm": float(min(d.min() for d in steps) * 1e3),
             "dmax_nm": float(max(d.max() for d in steps) * 1e3), "monitor_bytes": s.monitors_data_size}
        print(r); rows.append(r)
out["bend"] = rows
xs = base.grid.boundaries                                    # the grid lines of the 20 steps/wavelength set-up
out["bend_grid20"] = {"x": list(xs.x), "y": list(xs.y), "z": list(xs.z)}

json.dump(out, open(os.path.join(HERE, "ch32_tidy3d.json"), "w"), indent=1)
print("wrote ch32_tidy3d.json")
