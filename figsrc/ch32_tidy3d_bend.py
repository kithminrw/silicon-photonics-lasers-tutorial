import numpy as np
import tidy3d as td

lam0, R, w, t = 1.55, 2.0, 0.5, 0.22             # micrometres
freq0 = td.C_0 / lam0
pulse = td.GaussianPulse(freq0=freq0, fwidth=freq0 / 10)
freqs = td.C_0 / np.linspace(1.50, 1.60, 5)
si, sio2 = td.Medium(permittivity=3.476**2), td.Medium(permittivity=1.444**2)

# 90-degree bend of radius R about the origin: in along +x at y = -R, out along +y at x = R
th = np.linspace(-np.pi / 2, 0, 91)
arc = np.vstack([np.c_[(R + w / 2) * np.cos(th), (R + w / 2) * np.sin(th)],
                 np.c_[(R - w / 2) * np.cos(th[::-1]), (R - w / 2) * np.sin(th[::-1])]])
guide = td.GeometryGroup(geometries=[
    td.Box.from_bounds(rmin=(-9, -R - w / 2, -t / 2), rmax=(0, -R + w / 2, t / 2)),
    td.PolySlab(vertices=arc, slab_bounds=(-t / 2, t / 2), axis=2),
    td.Box.from_bounds(rmin=(R - w / 2, 0, -t / 2), rmax=(R + w / 2, 9, t / 2))])

mode_spec = td.ModeSpec(num_modes=1)
source = td.ModeSource(center=(-1.0, -R, 0), size=(0, 2.0, 1.6), source_time=pulse,
                       direction="+", mode_spec=mode_spec, mode_index=0)
monitors = [
    td.ModeMonitor(center=(-0.5, -R, 0), size=(0, 2.0, 1.6), freqs=freqs, mode_spec=mode_spec, name="in"),
    td.ModeMonitor(center=(R, 1.0, 0), size=(2.0, 0, 1.6), freqs=freqs, mode_spec=mode_spec, name="out"),
    td.FluxMonitor(center=(R, 1.0, 0), size=(2.0, 0, 1.6), freqs=freqs, name="flux"),
]
sim = td.Simulation(
    center=(0.875, -0.875, 0), size=(4.75, 4.75, 2.0), medium=sio2,
    structures=[td.Structure(geometry=guide, medium=si)],
    sources=[source], monitors=monitors,
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=20, wavelength=lam0),
    boundary_spec=td.BoundarySpec.all_sides(td.PML()),
    symmetry=(0, 0, 1),            # TE-like mode: even about the mid-plane z = 0
    run_time=0.25e-12,
)
sim.validate_pre_upload()
print("cells", sim.num_cells, " time steps", sim.num_time_steps, " dt", sim.dt)
# with an account: import tidy3d.web as web; data = web.run(sim, task_name="bend")
#                   T = abs(data["out"].amps.sel(direction="+", mode_index=0))**2
