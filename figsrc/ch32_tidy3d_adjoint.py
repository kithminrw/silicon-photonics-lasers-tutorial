"""Chapter 32, Section 32.5 step 9: the adjoint-optimisation listing, as printed in the chapter, with a local check.

    MSYS_NO_PATHCONV=1 docker exec -w /repo/figsrc photonics-labs /opt/t3d/bin/python ch32_tidy3d_adjoint.py

tidy3d 2.12.2. The listing's last line (value_and_grad of a function that calls web.run) needs an account and runs two
cloud simulations, so it is commented out here. What runs here: the bend set-up of ch32_tidy3d_bend.py, then the
parametrised simulation is built and validated, and autograd traces derivatives through its geometry.
"""
exec(open("ch32_tidy3d_bend.py").read().split("sim.validate_pre_upload()")[0])   # the bend set-up: sim, si, R, w, t

# ---------------------------------------------------------------- the listing in the chapter
import autograd.numpy as anp
import numpy as np
from autograd import value_and_grad
import tidy3d as td
import tidy3d.web as web

th = np.linspace(-np.pi / 2, 0, 61)                         # points along the arc
nodes = np.linspace(-np.pi / 2, 0, 7)                       # where the widths are set
B = np.array([np.interp(th, nodes, np.eye(7)[k]) for k in range(7)]).T   # linear interpolation

def make_sim(widths):
    wt = anp.dot(B, widths)                                 # width along the arc
    ro, ri = R + wt / 2, R - wt / 2
    outer = anp.stack([ro * anp.cos(th), ro * anp.sin(th)], axis=1)
    inner = anp.stack([ri[::-1] * anp.cos(th[::-1]), ri[::-1] * anp.sin(th[::-1])], axis=1)
    arc = td.PolySlab(vertices=anp.concatenate([outer, inner]), slab_bounds=(-t / 2, t / 2), axis=2)
    straights = [td.Box.from_bounds(rmin=(-9, -R - w / 2, -t / 2), rmax=(0, -R + w / 2, t / 2)),
                 td.Box.from_bounds(rmin=(R - w / 2, 0, -t / 2), rmax=(R + w / 2, 9, t / 2))]
    return sim.updated_copy(structures=[td.Structure(geometry=g, medium=si) for g in straights + [arc]])

def transmission(widths):                                   # power in the output TE0 mode at 1550 nm
    data = web.run(make_sim(widths), task_name="bend_opt", verbose=False)
    amp = data["out"].amps.sel(direction="+", mode_index=0).isel(f=2)
    return anp.abs(amp.values) ** 2

# T, dT_dw = value_and_grad(transmission)(0.5 * np.ones(7))   # one forward and one adjoint run (needs an account)

# ---------------------------------------------------------------- the local check
widths = 0.5 * np.ones(7)
make_sim(widths).validate_pre_upload()
area = lambda w_: anp.sum(make_sim(w_).structures[2].geometry.vertices[:, 0] ** 2)   # any function of the geometry
print("built and validated; autograd traces the geometry:", value_and_grad(area)(widths)[1].round(3))
