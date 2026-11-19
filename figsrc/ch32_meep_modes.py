"""Chapter 32: the 500 x 220 nm strip's TE0 and TM0 effective indices from MEEP's eigenmode solver (MPB, called by
MEEP, with MEEP's default sub-pixel averaging) against resolution. The same solver launches and analyses the modes of
the bend in figsrc/ch32_meep_bend.py, so its convergence bounds that of the bend.

    MSYS_NO_PATHCONV=1 docker exec -e OMP_NUM_THREADS=1 -w /repo/figsrc photonics-labs \
        /opt/conda/envs/labs/bin/python ch32_meep_modes.py

Writes ch32_meep_modes.json. MEEP 1.35.1, constant indices 3.476 and 1.444, 1550 nm.
"""
import json, time
import meep as mp

w, t, f = 0.5, 0.22, 1 / 1.55
si, ox = mp.Medium(index=3.476), mp.Medium(index=1.444)
rows = []
for res in (10, 15, 20, 25, 30, 40, 50, 60, 80):
    t0 = time.time()
    sim = mp.Simulation(cell_size=mp.Vector3(0.25, 2.6, 2.2), resolution=res, default_material=ox,
                        geometry=[mp.Block(center=mp.Vector3(), size=mp.Vector3(mp.inf, w, t), material=si)],
                        boundary_layers=[mp.PML(0.3, direction=mp.Y), mp.PML(0.3, direction=mp.Z)])
    sim.init_sim()
    where = mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 2.0, 1.6))
    n = {}
    for name, par in (("TE", mp.EVEN_Z), ("TM", mp.ODD_Z)):
        em = sim.get_eigenmode(f, mp.X, where, 1, mp.Vector3(2.4 * f, 0, 0), parity=par)
        n[name] = em.k.x / f
    r = {"resolution": res, "neff_TE": n["TE"], "neff_TM": n["TM"], "seconds": time.time() - t0}
    print(r, flush=True); rows.append(r)
json.dump({"meep_version": mp.__version__, "rows": rows}, open("ch32_meep_modes.json", "w"), indent=1)
print("wrote ch32_meep_modes.json")
