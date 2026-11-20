"""Chapter 32, Worked Example: a 2 um-radius 90-degree bend of a 500 x 220 nm silicon strip in 3D MEEP.

The same set-up as the Tidy3D and Lumerical versions of the chapter: strip in oxide (constant indices 3.476 and
1.444, as in Lab 6), TE-like mode launched by an eigenmode source 1 um before the bend, mode monitors 0.5 um before
the bend and 1 um after it, 1 um of oxide between the guide and the PML, 0.89 um of oxide above and below the core,
a mirror plane at the core's mid-height. Prints and saves the transmission into the output TE mode at 1550 nm, the
reflection, the grid size, MEEP's own memory estimate and the CPU time.

    MSYS_NO_PATHCONV=1 docker exec -e OMP_NUM_THREADS=1 -w /repo photonics-labs \
        /opt/conda/envs/labs/bin/python figsrc/ch32_meep_bend.py 20 out.json

argument 1: resolution (pixels per um); argument 2 (optional): JSON file to write.
MEEP 1.35.1, run in the photonics-labs Docker container. Lengths in um, frequencies in c/um.
"""
import json, resource, sys, time
import numpy as np
import meep as mp

res = float(sys.argv[1]) if len(sys.argv) > 1 else 20
out = sys.argv[2] if len(sys.argv) > 2 else None
after = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0      # run time after the source has finished (um/c)

R, w, t = 2.0, 0.5, 0.22                 # bend radius, width, thickness (um)
n_si, n_ox = 3.476, 1.444
dpml, gap, zh = 1.0, 1.0, 1.0            # PML thickness; oxide between guide and PML; half-height of the domain
x0, x1 = -1.5, R + w / 2 + gap           # domain inside the PML (bend centre at the origin)
y0, y1 = -R - w / 2 - gap, 1.5
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
sx, sy, sz = x1 - x0 + 2 * dpml, y1 - y0 + 2 * dpml, 2 * zh + 2 * dpml
V = lambda x, y, z=0.0: mp.Vector3(x - cx, y - cy, z)           # chapter coordinates -> MEEP cell coordinates

si, ox = mp.Medium(index=n_si), mp.Medium(index=n_ox)
L, big = 10.0, 20.0                       # straights run well into the PML
# the quarter ring: a silicon disc, an oxide disc inside it, and oxide blocks that remove the other three quarters
# (later objects win in MEEP); then the two straights
geometry = [mp.Cylinder(radius=R + w / 2, height=t, center=V(0, 0), material=si),
            mp.Cylinder(radius=R - w / 2, height=t, center=V(0, 0), material=ox),
            mp.Block(center=V(-big / 2, 0), size=mp.Vector3(big, big, t), material=ox),
            mp.Block(center=V(big / 2, big / 2), size=mp.Vector3(big, big, t), material=ox),
            mp.Block(center=V(-L / 2, -R), size=mp.Vector3(L, w, t), material=si),
            mp.Block(center=V(R, L / 2), size=mp.Vector3(w, L, t), material=si)]

fcen = 1 / 1.55
df = 2 * np.pi * 0.1 * fcen               # Gaussian of r.m.s. width 10 % of fcen (same pulse as the Tidy3D set-up)
src = [mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=df), center=V(-1.0, -R), size=mp.Vector3(0, 2.0, 1.6),
                          eig_band=1, eig_parity=mp.EVEN_Z, eig_kpoint=mp.Vector3(1, 0, 0), eig_match_freq=True)]
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy, sz), resolution=res, geometry=geometry, sources=src,
                    default_material=mp.Medium(index=n_ox), boundary_layers=[mp.PML(dpml)],
                    symmetries=[mp.Mirror(mp.Z)])
freqs = 1 / np.linspace(1.60, 1.50, 5)
m_in = sim.add_mode_monitor(freqs, mp.FluxRegion(center=V(-0.5, -R), size=mp.Vector3(0, 2.0, 1.6)))
m_out = sim.add_mode_monitor(freqs, mp.FluxRegion(center=V(R, 1.0), size=mp.Vector3(2.0, 0, 1.6)))
f_out = sim.add_flux(freqs, mp.FluxRegion(center=V(R, 1.0), size=mp.Vector3(2.0, 0, 1.6)))

sim.init_sim()
mem_est = sim.get_estimated_memory_usage()
cpu0, wall0 = time.process_time(), time.time()
sim.run(until_after_sources=after)
cpu, wall = time.process_time() - cpu0, time.time() - wall0
steps = sim.meep_time() / sim.fields.dt

a_in = sim.get_eigenmode_coefficients(m_in, [1], eig_parity=mp.EVEN_Z).alpha[0]       # [freq, fwd/bwd]
a_out = sim.get_eigenmode_coefficients(m_out, [1], eig_parity=mp.EVEN_Z).alpha[0]
T = np.abs(a_out[:, 0]) ** 2 / np.abs(a_in[:, 0]) ** 2
Rf = np.abs(a_in[:, 1]) ** 2 / np.abs(a_in[:, 0]) ** 2
P_out = np.array(mp.get_fluxes(f_out)) / np.abs(a_in[:, 0]) ** 2   # all power through the output plane
k = len(freqs) // 2
cells = round(sx * res) * round(sy * res) * round(sz * res)
r = dict(resolution=res, cells_full=cells, cells_computed=cells // 2, time_steps=int(round(steps)),
         dt_um=sim.fields.dt, run_time_um=sim.meep_time(), mem_estimate_MB=mem_est / 2**20,
         maxrss_MB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, cpu_s=cpu, wall_s=wall,
         wavelengths_um=list(1 / freqs), T=list(T), R=list(Rf), P_out=list(P_out),
         T1550=float(T[k]), T1550_dB=float(10 * np.log10(T[k])), R1550_dB=float(10 * np.log10(Rf[k])))
print(json.dumps({k_: v for k_, v in r.items() if not isinstance(v, list)}, indent=1))
if out:
    json.dump(r, open(out, "w"), indent=1)
