import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver
from tidy3d.plugins.dispersion import FastDispersionFitter

lam0 = 1.55                       # lengths in micrometres
freq0 = td.C_0 / lam0             # frequencies in hertz

# materials: silicon (Li 1980 formula) fitted with poles, silica (Malitson) as a Sellmeier model
wl = np.linspace(1.4, 1.7, 31)
n_si = np.sqrt(11.6858 + 0.939816 / wl**2 + 0.00810461 * 1.1071**2 / (wl**2 - 1.1071**2))
si, rms = FastDispersionFitter(wvl_um=wl, n_data=n_si).fit(max_num_poles=2, tolerance_rms=1e-5)
sio2 = td.Sellmeier(coeffs=[(0.6961663, 0.0684043**2), (0.4079426, 0.1162414**2),
                            (0.8974794, 9.896161**2)])

# a 500 x 220 nm strip along x, centred on y = 0, from z = 0 to 0.22, clad in oxide
core = td.Structure(geometry=td.Box(center=(0, 0, 0.11), size=(td.inf, 0.5, 0.22)), medium=si)
sim = td.Simulation(
    center=(0, 0, 0.11), size=(2, 3, 3), medium=sio2, structures=[core],
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=30, wavelength=lam0),
    boundary_spec=td.BoundarySpec.all_sides(td.PML()),
    run_time=1e-12,
)
plane = td.Box(center=(0, 0, 0.11), size=(0, 3, 3))      # the cross-section, normal to x
spec = td.ModeSpec(num_modes=2, target_neff=3.0, group_index_step=True)
modes = ModeSolver(simulation=sim, plane=plane, mode_spec=spec, freqs=[freq0]).solve()

print("n_eff  ", modes.n_eff.values.round(4))
print("n_g    ", modes.n_group.values.round(3))
print("TE frac", modes.pol_fraction.te.values.round(3))
