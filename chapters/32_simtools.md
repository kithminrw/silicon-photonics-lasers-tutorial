---
title: "32. Simulation Tools in Practice"
parent: "Part VII · Design, Simulation and Layout"
nav_order: 32
permalink: /part-7/ch32/
chapter: 32
---

# <span class="chapnum">Chapter 32</span>Simulation Tools in Practice

Knowing how a solver works is half the job. The other half is setting it up so that the answer is right, knowing what the run will cost before you start it, and moving the result on to the next stage of the design. This chapter tours the tools photonic designers use, commercial and open, and the habits that make any of them trustworthy.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- name the products of the Ansys Lumerical suite, the solvers each contains, and the data passed between them;
- describe a Lumerical project and drive it from its script language or from Python;
- build, check and cost a Tidy3D simulation in Python before anything is sent to the cloud, and run its local mode solver;
- choose among the open tools (MEEP, MPB, femwell, SAX) and tie them to a layout with gdsfactory and gplugins;
- follow a set-up, run and check routine that works in any tool, and recognise the common mistakes;
- estimate the cells, time steps and memory of a 3D FDTD run, and set up the same problem in three tools.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

You need the loss of a 2 µm-radius silicon bend to within 0.01 dB. Which tool, which settings, and how do you know the answer is right?

</div>

## <span class="secnum">32.1</span>From a solver to a tool

[Chapter 31]({% link chapters/31_simulators.md %}) described the numerical methods: mode solvers, eigenmode expansion, FDTD and the rest. A simulation **tool** wraps one or more of those solvers with everything else a designer needs: a way to draw or import the geometry, a database of materials with fitted dispersion models, automatic meshing with local refinement, sources and monitors that already know how to normalise their results, a way to run jobs (on a laptop, a cluster or someone else's servers), post-processing, and a scripting language so that all of it can be automated. Two tools built on the same method should give the same physics; what differs is how quickly you can set a problem up, how far you can trust the defaults, what a run costs, and how easily the result moves on to a circuit simulator.

This chapter looks at three kinds of tool. **Ansys Lumerical** is a commercial suite that runs on your own computers (or on the vendor's cloud) and covers everything from a waveguide cross-section to a circuit. **Tidy3D** is a commercial service: you describe the simulation in Python on your computer and it runs on the vendor's servers. The **open tools** (MEEP, MPB, femwell, SAX, with gdsfactory and gplugins as the glue) are free software you install and run yourself; the labs of this tutorial use them. The two commercial tools are described here only from their public documentation. Lumerical needs a licence and was not run for this chapter; Tidy3D's Python package is open source, so its objects and its local mode solver were run, but no cloud simulation was.

## <span class="secnum">32.2</span>Ansys Lumerical

### Products and solvers

The suite is sold as four products, each a design environment around one or more solvers ([Figure 32.1](#fig-32-1)) {% include cite.html keys="lumericalproducts,lumericaldocs" %}:

- **MODE** holds the waveguide solvers. The **FDE** (finite-difference eigenmode) solver finds the modes of a cross-section, straight or bent: effective and group index, loss, field profiles, overlaps. **EME** (bidirectional eigenmode expansion) propagates those modes through devices that change along their length, such as tapers, MMIs and couplers, and makes length sweeps almost free. **varFDTD** is the 2.5D method of Chapter 31: it collapses the vertical direction into effective indices and runs 2D FDTD in the plane of the chip, for planar devices too large for 3D.
- **FDTD** is the 3D (and 2D) time-domain solver, for any geometry and a whole band at once: grating couplers, Y-branches, crossings, photonic crystals. It also contains RCWA and STACK solvers for periodic and thin-film problems.
- **Multiphysics** gathers the non-optical solvers: **CHARGE** (drift–diffusion: carriers and currents in modulators and photodetectors), **HEAT** (conduction and Joule heating: heaters, self-heating), **FEEM** (a finite-element mode solver), **DGTD** (a finite-element time-domain solver) and **MQW** (gain and spontaneous emission of quantum wells, for lasers and amplifiers).
- **INTERCONNECT** is the circuit simulator, in the frequency and the time domain. It connects compact models, including libraries built with the **CML Compiler**, which is how a foundry can ship validated models of its PDK cells.

<figure id="fig-32-1">
  <img src="{{ '/assets/figs/ch32_lumerical.svg' | relative_url }}" style="width:720px" alt="Block diagram of the Ansys Lumerical suite. Left: MODE, containing the FDE, EME and varFDTD solvers, and below it FDTD, containing 3D and 2D FDTD and the RCWA and STACK solvers. Right: INTERCONNECT, with its circuit solver, S-parameter element, compact models and the CML Compiler. Red arrows from MODE and FDTD to INTERCONNECT carry the FDE waveguide data, the EME S-matrix and FDTD S-parameters from a port sweep. Bottom: Multiphysics, with CHARGE, HEAT, FEEM, DGTD and MQW; teal arrows carry carrier density and temperature to MODE and FDTD as index and loss changes, and gain to the laser and amplifier models of INTERCONNECT. A band at the bottom lists the automation: the Lumerical script language, the Python API, sweeps and optimisation, lumopt, and the project file types .lms, .fsp, .ldev and .icp.">
  <figcaption><span class="capnum">Figure 32.1.</span> <strong>The Ansys Lumerical suite and what flows between its products.</strong> Waveguide data from FDE and S-parameters from EME and FDTD become compact models in INTERCONNECT (red); carrier densities and temperatures from CHARGE and HEAT become index and loss perturbations in the optical solvers, and quantum-well gain feeds the laser and amplifier models (teal). The same script language runs in every product. Product and solver names as in the vendor's public documentation for the 2026 R1 release {% include cite.html keys="lumericalproducts,lumericaldocs" %}. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

The arrows of [Figure 32.1](#fig-32-1) are the reason to use a suite. An FDE sweep of a waveguide against wavelength becomes the waveguide element of a circuit. FDTD computes a device's S-parameters by exciting each port in turn (an "S-parameter sweep"), and the result is exported to a file that INTERCONNECT's N-port S-parameter element reads. A CHARGE simulation of a PN junction exports its electron and hole densities, which MODE or FDTD import as a spatial perturbation of the silicon's index and absorption (through the plasma-dispersion relations of [Chapter 19]({% link chapters/19_eo.md %})), so the modulator's phase and loss against voltage come out of the optical solver {% include cite.html keys="lumericaldocs" %}. Ansys has been part of Synopsys since July 2025 {% include cite.html keys="synopsys2025" %}; the products keep their Ansys Lumerical names.

### A project

A Lumerical project is a file (`.lms` for MODE, `.fsp` for FDTD, `.ldev` for Multiphysics, `.icp` for INTERCONNECT) holding a tree of objects:

- **structures**: rectangles, rings, polygons, waveguides, groups of them, or layers imported from a GDS file with a thickness and a material (the script command `gdsimport` takes the file, cell, layer, material and z range). Where two structures overlap, the one with the lower **mesh order** wins; most database materials default to the same order, so the order in the tree decides ties, which is a common source of surprise;
- the **solver region** (an FDE plane, an EME region or an FDTD volume): its extent, its boundary conditions (PML, metal, periodic, Bloch, and symmetric or anti-symmetric planes that halve the problem) and its mesh settings. The default mesh is automatic and non-uniform: the **mesh accuracy** setting, from 1 to 8, asks for about 6 points per wavelength in each material at accuracy 1 and 4 more at each step, so accuracy 2 aims at 10 {% include cite.html keys="lumericaldocs" %};
- **mesh override regions**: boxes in which you set the cell size yourself, over a thin layer, a narrow gap or a sharp tip;
- **sources**: a mode source (which solves for the waveguide mode with the built-in FDE), a Gaussian beam, a plane wave, a dipole;
- **monitors**: frequency-domain field and power monitors, mode-expansion monitors that project the field onto a waveguide mode, time monitors and movies;
- **analysis groups**: monitors bundled with a small script that turns their data into a derived result, such as a box of power monitors that adds up everything a device radiates.

You build in **layout mode**, run, and the results appear in **analysis mode** attached to the monitors; changing the geometry discards them. Parameter sweeps and optimisations are defined on the properties of objects, and FDTD offers a memory check that estimates what a run will need before it starts.

### Script and Python

Everything in the graphical interface has a command in the **Lumerical script language**, an interpreted, matrix-oriented language much like MATLAB: `addrect` adds a rectangle, `set` and `setnamed` change properties, `addfde` and `findmodes` set up and run a mode solve, `run` runs an FDTD simulation, `getresult` fetches a result, and the usual maths and plotting follow. The same commands are available from Python: the Python API, distributed with the products as the module `lumapi` and since the 2026 R1 release also as the package **PyLumerical** (`pip install ansys-lumerical-core`), opens a product session and exposes every script command as a method of it. Both need an installed, licensed product: the Python package drives it and does not replace it. **lumopt**, Lumerical's Python module for inverse design, uses the adjoint method {% include cite.html keys="lalaukeraly2013" %} to optimise shapes and permittivity maps in FDTD {% include cite.html keys="pylumerical,lumericaldocs" %}.

Here is the mode solve of the 500 × 220 nm strip of [Chapter 6]({% link chapters/06_soi.md %}) written for PyLumerical. In the `add` commands a property can be passed as a keyword argument with its spaces replaced by underscores (`x_span` for "x span"), or in a dictionary with its original name:

```python
import ansys.lumerical.core as lumapi       # PyLumerical; older installs: import lumapi from <install>/api/python

um = 1e-6                                   # Lumerical works in SI units
with lumapi.MODE(hide=True) as mode:
    # cross-section in the xy plane (y up), light travelling along z
    mode.addrect(name="cladding", x=0, x_span=6*um, y=0.11*um, y_span=6*um, z=0, z_span=1*um,
                 material="SiO2 (Glass) - Palik")
    mode.addrect(name="core", x=0, x_span=0.5*um, y_min=0, y_max=0.22*um, z=0, z_span=1*um,
                 material="Si (Silicon) - Palik")
    mode.setnamed("cladding", "override mesh order from material database", True)
    mode.setnamed("cladding", "mesh order", 3)      # higher number = lower priority: the core wins
    mode.addfde(properties={"x": 0, "x span": 3*um, "y": 0.11*um, "y span": 3*um, "z": 0})
    mode.addmesh(properties={"based on a structure": True, "structure": "core",
                             "override x mesh": True, "override y mesh": True,
                             "set maximum mesh step": True, "dx": 10e-9, "dy": 10e-9})
    mode.setanalysis("wavelength", 1.55*um)
    mode.setanalysis("number of trial modes", 4)
    mode.setanalysis("search", "near n")
    mode.setanalysis("use max index", True)
    n_found = int(mode.findmodes())
    for k in range(1, n_found + 1):
        name = "FDE::data::mode" + str(k)
        print(k, mode.getresult(name, "neff"), mode.getresult(name, "TE polarization fraction"))
```

Every command and property name in it was checked against Ansys's public documentation and examples for PyLumerical and the script language {% include cite.html keys="pylumerical,lumericaldocs" %}, but the code was **not run here**, because Lumerical needs a licence. The TE-like mode should come out first with $$n_\mathrm{eff}$$ close to the 2.446 that femwell gives (Worked Example 32.1); the exact value depends on the material data (Palik's tables here, not the formulas used in Chapter 6) and on the mesh, which is why the mesh-override step should be halved once to check that it has converged.

## <span class="secnum">32.3</span>Tidy3D

Tidy3D, from Flexcompute, is FDTD as a service. The `tidy3d` Python package, which is open source, describes and checks a simulation on your computer; the simulation itself runs on the company's servers, on GPU hardware, and the results come back as a file ([Figure 32.2](#fig-32-2)) {% include cite.html keys="tidy3ddocs,tidy3dsite" %}. A browser-based graphical interface builds, runs and views the same simulations. Besides FDTD the service offers a mode solver, EME, and heat and charge solvers. Lengths are in micrometres and frequencies in hertz.

<figure id="fig-32-2">
  <img src="{{ '/assets/figs/ch32_tidy3d.svg' | relative_url }}" style="width:720px" alt="Workflow diagram in two panels. Left panel, your computer with Python and the tidy3d package: build a td.Simulation from structures, sources, monitors, grid and boundary specifications and symmetry; validate and look at it; optionally run the local mode solver, which needs no account and no credits; and post-process and plot the results as labelled arrays. Right panel, the vendor's servers, which need an account: upload the task, estimate its cost as an upper bound in which every time step runs, run on GPU servers, which stop early at the shutoff level, and store the results as an HDF5 file holding only the monitors' data; a web GUI in a browser can build, view and run the same tasks. A blue arrow labelled download returns the results to the post-processing step, and a teal loop on the left, labelled optimise, says that a gradient costs one forward and one adjoint run.">
  <figcaption><span class="capnum">Figure 32.2.</span> <strong>The Tidy3D workflow.</strong> The simulation is built and checked in Python on your computer, where the mode solver can also run; it is uploaded, its cost estimated and then run on the vendor's GPU servers, and only the data of the monitors you asked for comes back. Inverse design closes a loop around the run: each gradient costs one forward and one adjoint simulation, however many parameters there are {% include cite.html keys="tidy3ddocs" %}. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

A **`td.Simulation`** is one Python object that contains everything:

- **structures**, each a geometry and a medium: boxes, cylinders, `PolySlab`s (polygons extruded between two heights, which can be read straight from a GDS layer), and groups of them;
- **sources**: `ModeSource` (solves for and injects a waveguide mode), `GaussianBeam`, `PlaneWave`, `PointDipole` and others, each with a time dependence, usually a `GaussianPulse` that covers the band;
- **monitors**: `ModeMonitor` (the amplitude of chosen modes through a plane: S-parameters), `FluxMonitor` (total power through a plane), `FieldMonitor` (the fields themselves, which can be large), and more;
- the **grid**: `GridSpec.auto` builds a non-uniform grid with at least `min_steps_per_wvl` cells per wavelength in each material (10 by default) and grows the cells by at most a factor of 1.4 from one to the next; boxes can force a finer grid where needed;
- the **boundaries**: PML by default, 12 layers thick on each side, or absorbers, periodic and Bloch boundaries, and electric or magnetic walls;
- **symmetry**: a mirror plane through the centre of the domain on each axis, `0` for none, `1` for even (a magnetic wall) or `−1` for odd (an electric wall). Which sign selects TE and which TM depends on the field components, so check it on the mode solver first: for the strip of Chapter 6 with a mirror plane at its mid-height, `symmetry=(0, 0, 1)` keeps the TE-like mode (TE fraction 0.98) and `(0, 0, -1)` the TM-like one (0.04);
- the **run time** and a **shutoff** level (by default the run stops once the field energy has fallen to 10⁻⁵ of its peak), and the Courant factor (0.99 of the stability limit).

Every object is checked as it is created, and `sim.validate_pre_upload()` runs the further checks the server would. The checks are worth reading: the first version of the bend of Section 32.6 drew a warning that the input waveguide sat less than half a wavelength from the PML, and moving the boundary out fixed it. The objects are immutable; to change one you make a modified copy (`sim.updated_copy(...)`), which keeps a sweep from silently altering a shared object {% include cite.html keys="tidy3ddocs" %}.

Before anything runs, the simulation knows its own size: `sim.num_cells` and `sim.num_time_steps` give the grid and the number of steps, and `sim.plot()` and `sim.plot_grid()` draw them. Running is one call, `web.run(sim, task_name=...)` after `import tidy3d.web as web`, which uploads the task, runs it and downloads the data; `web.Job` and `web.Batch` do the same in steps or for many simulations. Between upload and run, `web.estimate_cost` gives the cost in the vendor's credits, as an upper bound that assumes every time step runs; the run usually ends earlier, at the shutoff. The returned data are labelled arrays (xarray), indexed by monitor name, frequency, mode and direction.

The other solvers follow the same pattern. The **mode solver** (`ModeSolver` in `tidy3d.plugins.mode`) runs on your own computer at no cost, or on the server, where it adds sub-pixel averaging of the permittivity that the local version omits unless an optional package is installed. **EME** is available in the current release (2.12) as `td.EMESimulation`; it runs on the server, and locally with the optional `tidy3d[extras]` package and some limitations. The **S-matrix plugin** runs one FDTD simulation per port to fill a device's scattering matrix. **Inverse design** uses automatic differentiation: wrap `web.run` in a Python function of your design parameters, and the `autograd` package returns the gradient of any figure of merit with one extra (adjoint) simulation, whatever the number of parameters; the `invdes` plugin adds design regions, filters and penalties that enforce a minimum feature size, an optimiser, and export of the result to GDS {% include cite.html keys="tidy3ddocs,molesky2018" %}.

Here is the strip of Chapter 6 again, now in Tidy3D's local mode solver. It also shows how a material defined by a formula becomes a dispersive model that a time-domain solver can use: the silicon index of Li {% include cite.html keys="li1980" %} is fitted with two poles, while Malitson's silica {% include cite.html keys="malitson1965" %} is a Sellmeier model already:

```python
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
```

This code (`figsrc/ch32_tidy3d_strip.py`) was run with tidy3d 2.12.2, installed with pip in the tutorial's Docker container; it needs no account. It prints $$n_\mathrm{eff}$$ = 2.4472 and 1.7738, $$n_g$$ = 4.185 and 3.755, and TE fractions 0.983 and 0.046: the TE-like and TM-like fundamental modes.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.1 · The same strip in two mode solvers</div>

Chapter 6 found the 500 × 220 nm strip's modes with femwell, a finite-element solver on a triangular mesh: TE₀ $$n_\mathrm{eff}$$ = 2.446, $$n_g$$ = 4.18; TM₀ 1.771 and 3.74. Tidy3D's local solver, a finite-difference solver on a rectangular grid with the same material formulas, gives 2.4472 and 4.185 for TE₀ and 1.7738 and 3.755 for TM₀. The effective indices agree to 0.05 % (TE) and 0.15 % (TM), the group indices to 0.1 % and 0.4 %.

Is that agreement or luck? [Figure 32.3](#fig-32-3) repeats the solve, with both indices frozen at their 1550 nm values, on 26 automatic grids from 10 to 60 steps per wavelength (cells of 42 to 7 nm in the silicon). femwell, whose triangles follow the core's faces, does not move in the fourth decimal from 80 nm elements down to 10 nm: 2.4458. The local finite-difference solver jumps about, between 2.387 and 2.594 for TE₀, with no trend even at 7 nm cells. The cause is where the grid puts its samples. The automatic grid places grid lines on the core's top and bottom faces, so the rows of $$E_x$$ and $$E_y$$ samples that run along those faces sit exactly on the interface, and without sub-pixel averaging each row is counted as silicon or as oxide according to the last bits of a floating-point number: in this test a grid line computed as 0.21999999999999975 µm fell inside the core and one computed as 0.22000000000000020 µm did not. One row more or less of silicon is a core one cell thicker or thinner, and with $$\partial n_\mathrm{eff}/\partial t = 3.7\times10^{-3}$$ per nanometre ([Chapter 6]({% link chapters/06_soi.md %})) that moves $$n_\mathrm{eff}$$ by several hundredths. The package says as much: the local solver warns that it has no sub-pixel averaging and points to the server-side solver, which has it {% include cite.html keys="tidy3ddocs" %}. The 0.05 % agreement of the first run was luck.

MEEP's eigenmode solver, which does average the permittivity across interfaces, behaves differently again in the same test: it converges smoothly but slowly, from below, reaching 2.430 only at 12.5 nm cells. That will matter for the bend of Section 32.6. The lesson is the habit, not the tool: compare two methods, refine each, and know whether your solver averages the permittivity at interfaces.

</div>

<figure id="fig-32-3">
  <img src="{{ '/assets/figs/ch32_modeconv.svg' | relative_url }}" style="width:640px" alt="Two plots of effective index against the cell or element size in the core, from 100 nm on the left to 5 nm on the right on a log scale. (a) TE0: femwell's points form a flat line at 2.4458 from 80 to 10 nm; Tidy3D's local solver jumps between 2.39 and 2.59 with no trend; MEEP's eigenmode solver rises smoothly from 2.12 at 100 nm to 2.43 at 12.5 nm. (b) TM0: the same pattern around femwell's 1.7706, with Tidy3D's local values between 1.70 and 2.00 and MEEP's rising from 1.66 to 1.76.">
  <figcaption><span class="capnum">Figure 32.3.</span> <strong>Convergence of a mode solve in three solvers.</strong> The 500 × 220 nm strip at 1550 nm, with silicon and silica at 3.4757 and 1.4440: (a) TE₀, (b) TM₀ effective index against the size of the cells or elements in the core. femwell (blue) is flat to the fourth decimal: 2.4458 and 1.7706 (dashed). Tidy3D's local solver (amber, 26 automatic grids from 10 to 60 steps per wavelength) jumps with no trend, because it has no sub-pixel averaging and the samples on the core's faces fall on either side of the interface by rounding. MEEP's eigenmode solver (teal), with sub-pixel averaging, converges from below but slowly: TE₀ 2.349, 2.379, 2.405 and 2.430 at resolutions 20, 30, 40 and 80 px/µm. Drawn by <code>figsrc/ch32_figs.py</code> from <code>figsrc/ch32_tidy3d.py</code> (tidy3d 2.12.2, local), <code>figsrc/ch32_femwell.py</code> (femwell 0.1.12) and <code>figsrc/ch32_meep_modes.py</code> (MEEP 1.35.1).</figcaption>
</figure>

## <span class="secnum">32.4</span>Open tools

The open tools used in this tutorial's labs cover most of the same ground, with less integration and more freedom:

- **MEEP** is the open-source FDTD code from MIT, in 1, 2 and 3 dimensions with a Python interface {% include cite.html keys="meep,meepdocs" %}. It uses a uniform grid and recovers much of the accuracy lost to staircasing with sub-pixel averaging of the permittivity at interfaces {% include cite.html keys="farjadpour2006" %} ([Chapter 31]({% link chapters/31_simulators.md %})). It has eigenmode sources and mode decomposition, dispersive materials as Lorentzian fits, GDS import (`mp.get_GDSII_prisms`), an adjoint module for inverse design, and runs in parallel over MPI. [Lab 6]({% link labs/lab06_gc_meep.md %}) uses it for a grating coupler in 2D; the bend of Section 32.6 uses it in 3D.
- **MPB** computes eigenmodes in a plane-wave basis: photonic band structures, and the modes of waveguides {% include cite.html keys="mpb" %}. MEEP calls it to compute the mode that an eigenmode source launches and that a mode monitor projects onto.
- **femwell** is a finite-element solver built on scikit-fem: optical modes, including bent and leaky ones, heat flow and electrostatics, so it can chain a heater or a PN junction to a mode {% include cite.html keys="femwell" %}. Most of this tutorial's mode numbers come from it, and [Lab 2]({% link labs/lab02_femwell.md %}) shows how to use it.
- **SAX** solves circuits of S-parameter models in Python with JAX, so a circuit's response can be differentiated and optimised {% include cite.html keys="sax" %}; [Lab 4]({% link labs/lab04_sax.md %}) uses it.
- **gdsfactory** describes components and circuits as Python functions that produce layout {% include cite.html keys="gdsfactory" %}, and **gplugins** connects that layout to solvers: given a component and the PDK's layer stack (the thickness and material of each layer), it builds the 3D model and computes S-parameters with Tidy3D, MEEP or Lumerical FDTD (`gplugins.tidy3d.write_sparameters`, `gplugins.gmeep.write_sparameters_meep`, `gplugins.lumerical.write_sparameters_lumerical`), modes with femwell, Tidy3D or MPB, EME with meow, and circuits with SAX {% include cite.html keys="gplugins" %}. One description of a device then feeds the layout and every solver with the same ports and the same layer stack, which removes a whole class of transcription mistakes.

Open tools are enough for mode solving, for 2D and 2.5D simulations, for 3D runs of a few cubic micrometres such as the bend below, for circuit simulation and for research in which the solver itself is the subject. They are also transparent: every default can be read in the source, which is why they are used to check commercial results and the other way round. The commercial tools save time when the 3D runs are large and many (GPU hardware turns hours into minutes), when a multiphysics chain from carriers or heat to a circuit must work without hand-written glue, when a foundry's validated compact models are needed in a circuit simulator, and when a graphical interface and vendor support are worth more to a team than the licence. An independent comparison of Lumerical FDTD and Tidy3D on six passive SOI components found the two in close agreement, with differences of a few per cent in most quantities, and run times that depended mainly on the hardware each ran on {% include cite.html keys="liu2025" %}.

## <span class="secnum">32.5</span>Setting up a run, step by step

Whatever the tool, a trustworthy simulation goes through the same steps ([Figure 32.4](#fig-32-4)). They are written here for FDTD, the most demanding case; most also apply to mode solvers and EME.

<figure id="fig-32-4">
  <img src="{{ '/assets/figs/ch32_loop.svg' | relative_url }}" style="width:720px" alt="Flow diagram. Top row, set up: 1 geometry from the GDS or parametric code; 2 materials, a dispersion fit, then check it; 3 grid, automatic plus refinement and sub-pixel averaging; 4 sources, mode or beam, band and polarisation; 5 monitors, mode, flux and field, and normalisation; 6 boundaries, PML far enough and symmetry planes. An arrow leads down to the bottom row, run and check, which runs right to left: 7 first run, does the power add up, have the fields decayed, are there reflections; 8 converge the grid, region size, run time and mode count; 9 sweep and optimise; 10 export S-parameters to a circuit simulator; 11 record the script, versions, settings and data. Dashed red arrows from the first run and the convergence step back to the grid and the sources say that when a check fails, the set-up is fixed. A band at the bottom names the open glue: gdsfactory and gplugins feeding MEEP, Tidy3D, Lumerical, femwell, MPB and meow, then SAX.">
  <figcaption><span class="capnum">Figure 32.4.</span> <strong>Set up, run, check: the same loop in every tool.</strong> The six set-up steps define the problem; the first run is a test of the set-up, not a result; only a converged answer is swept, optimised and exported, and everything is recorded. With gdsfactory and gplugins the geometry, layer stack and ports are shared by every solver. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

**1. Geometry.** Import it from the GDS file that will be fabricated (a layer, a thickness, a material, and the sidewall angle if the tool supports it), or generate the layout and the simulation from the same parametric code. Simplify what does not matter optically, such as metal far from the light, but keep what does: the real etch depth, the slab of a rib, the rounded corners of a fabricated taper if you know them. Waveguides that leave the region must run straight through the absorbing boundary, or their ends reflect.

**2. Materials.** A time-domain solver cannot use a table of $$n(\lambda)$$ directly; it fits the table with a model it can step in time (a sum of poles, or Sellmeier, Lorentz and Drude terms), and the fit is only as good as its fitting range. Fit over the band you simulate, not much wider, and **look at the fit**. [Figure 32.5](#fig-32-5) fits the silicon formula of Li {% include cite.html keys="li1980" %} from 1.2 to 2.0 µm. On a plot of $$n(\lambda)$$ the one-pole and two-pole fits are indistinguishable from the formula; the errors are not. With one pole the index is off by up to 1.6 × 10⁻⁴ inside the 1500–1600 nm band and 9 × 10⁻⁴ at the edge of the fitting range; two poles bring both below 10⁻⁴. The material group index $$n - \lambda\,\mathrm{d}n/\mathrm{d}\lambda$$, which depends on the slope, is ten times more sensitive: one pole gets it wrong by 1.8 × 10⁻³ in the band and by several hundredths near 1.2 µm. Errors grow at the ends of the range, where no data hold the fit, so fit a little wider than your band, and no wider than you need. A mode solver at one wavelength needs only the index there, but a group index needs the dispersion too: with silicon and silica frozen at their 1550 nm indices, femwell gives the strip's TE₀ group index as 4.05 instead of 4.18, 3 % low, and every free spectral range computed from it would be 3 % too wide.

<figure id="fig-32-5">
  <img src="{{ '/assets/figs/ch32_fit.svg' | relative_url }}" style="width:640px" alt="Two plots against wavelength from 1.2 to 2.0 micrometres, with the 1.5 to 1.6 micrometre band shaded. (a) The error in silicon's refractive index of a one-pole fit, which swings between minus 9 and plus 3 parts in ten thousand and is largest at 1.2 micrometres, and of a two-pole fit, which stays within one part in ten thousand. (b) The error in the material group index: the one-pole fit reaches minus 0.04 near 1.2 micrometres and about 0.002 in the band; the two-pole fit stays near zero except at the short-wavelength end.">
  <figcaption><span class="capnum">Figure 32.5.</span> <strong>Check the material fit.</strong> The silicon index of Li (1980) between 1.2 and 2.0 µm, fitted with one pole (red) and two poles (blue). (a) Error of the fitted index; (b) error of the material group index \(n - \lambda\,\mathrm{d}n/\mathrm{d}\lambda\) computed from the fits. Grey: the 1500–1600 nm band. The errors are largest at the ends of the fitting range, and the group index, which depends on the slope, is far more sensitive than the index. Drawn by <code>figsrc/ch32_figs.py</code> from <code>figsrc/ch32_tidy3d.py</code> (tidy3d 2.12.2 <code>FastDispersionFitter</code>, a vector-fitting algorithm {% include cite.html keys="gustavsen1999" %}).</figcaption>
</figure>

**3. Grid.** Start from the tool's automatic grid, which sizes the cells by the wavelength in each material: about 10 points per wavelength (Lumerical's mesh accuracy 2, Tidy3D's default) is a first look, not an answer. Refine where the field changes fast: across a 220 nm film, in a 200 nm gap, at a tip. Remember that the grid is a product of three lists of lines, one per axis, so a fine region in $$x$$ is fine across the whole $$yz$$ plane; for a bend, which has silicon at almost every $$x$$ and $$y$$, refinement covers nearly the whole area. Sub-pixel averaging (on by default in MEEP and in Tidy3D's FDTD; in Lumerical the default "conformal variant 0" mesh refinement plays the same role) makes a coarse grid far more accurate at interfaces, but not at a tip smaller than a cell, and not every solver in a tool has it (Worked Example 32.1). Convergence, the only real test, comes at step 8.

**4. Sources.** For a waveguide device, use a **mode source**, which injects one guided mode and nothing else; check *which* mode. Solvers sort modes by effective index, and whether TE₀ or TM₀ comes first depends on the guide: in a thin, wide strip TE₀ is first, in a tall, narrow one it may not be. Read the polarisation fraction, not just the mode number. For grating couplers and edge couplers use a **Gaussian beam** with the fibre's waist, position and angle ([Chapter 3]({% link chapters/03_gaussian.md %})). The pulse's bandwidth sets the band you get from one run, and a narrow band means a long pulse and a long run. Place the source in a straight section, away from the device and the boundary.

**5. Monitors and normalisation.** A **mode monitor** gives the amplitude of chosen modes, forward and backward, through a plane: these are the S-parameters. A **flux monitor** gives all the power through a plane, guided or not. The tools normalise both by the power the source injected, so $$T = 1$$ means everything arrived. Measure reflection with a monitor between the source and the device, looking backwards. Field monitors are for looking and for debugging; recorded over a volume at many frequencies they produce gigabytes, so record only what you need. Keep monitors out of the PML and a little away from the device, so that what they see has settled into guided modes and radiation.

**6. Boundaries and symmetry.** The PML must be far enough away that the guided field's evanescent tail has decayed before reaching it: about 1 µm of oxide beside a silicon strip, more for silicon nitride or near cut-off, and more again on the outside of a bend, where the mode shifts outwards and radiates. For a grating coupler or a thin buried oxide, include the BOX's real thickness and the silicon substrate under it, because the light leaking or reflecting there is part of the answer ([Chapter 15]({% link chapters/15_gc.md %})). A **symmetry plane** halves the cells, and with them the memory and run time, but only if the structure and the source are both symmetric about it; its parity selects the polarisation, so a wrong sign silently simulates the other mode.

**7. The first run is a test.** Before trusting any number, check that the power adds up ($$T + R$$ + radiated ≈ 1 for a lossless device), that the fields decayed before the run ended (a run stopped by its time limit with energy still inside gives wrong spectra), that the reflection is small where it should be, that the injected mode is the one you meant, and that the field looks physically sensible. A straight waveguide in the same set-up should give $$T = 1$$ to within the tolerance you need; if it does not, nothing more complicated will be right.

**8. Converge.** Refine the grid until the answer changes by less than your tolerance; then move the boundaries out by half a micrometre and lengthen the run, and check again. For EME, add modes until the result stops changing.

**9. Sweep and optimise.** Only a converged set-up is worth sweeping: over the design parameters, over the fabrication corners and Monte Carlo cases of [Chapter 29]({% link chapters/29_design.md %}), or inside an adjoint optimisation {% include cite.html keys="molesky2018" %}. Sweeps parallelise trivially, which is where a cluster or a cloud service earns its cost. An adjoint optimisation in practice is a figure of merit written as a function of the design parameters, and a library that differentiates it: lumopt in Lumerical, `meep.adjoint` in MEEP, automatic differentiation in Tidy3D. Here, in Tidy3D, the parameters are the width of the bend of Section 32.6 at seven points along its arc, and the figure of merit is the power in the output TE₀ mode at 1550 nm (`sim`, `si`, `R`, `w` and `t` come from the bend's set-up, `figsrc/ch32_tidy3d_bend.py`):

```python
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

T, dT_dw = value_and_grad(transmission)(0.5 * np.ones(7))   # one forward and one adjoint run
```

The gradient `dT_dw` then drives an optimiser, with filters and penalties that keep features printable. What was checked here (`figsrc/ch32_tidy3d_adjoint.py`) is that the parametrised simulation builds and passes validation, and that derivatives trace through the geometry; the runs themselves need an account and were not made. Whatever optimiser produced it, check the final design on a finer grid, and ideally in a second tool, before trusting it ([Chapter 29]({% link chapters/29_design.md %})).

**10. Export to the circuit.** A device's S-parameters against wavelength, for every port and mode, with consistent port names, reference planes and phase conventions, are what a circuit simulator needs: INTERCONNECT's N-port element reads Lumerical's export, and SAX builds a model from any table ([Chapter 30]({% link chapters/30_flow.md %})).

**11. Record.** Keep the script under version control with the tool's version, the material data, the grid settings and the results it produced. This chapter's numbers carry their tool versions (tidy3d 2.12.2, MEEP 1.35.1) for that reason: a later release can change a default and therefore an answer {% include cite.html keys="wilson2014" %}.

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Common mistakes</div>

- **Wrong mode or polarisation:** mode 1 is not always TE₀; a symmetry plane of the wrong parity selects the other polarisation. Read the polarisation fraction.
- **Monitors in or touching the PML**, or a source inside it: the numbers are silently wrong.
- **Region too small:** the evanescent tail or the radiation from a bend reaches the PML; waveguides that end inside the region instead of passing through the boundary reflect.
- **Unconverged grid:** a result from the default grid, never refined. One refinement costs one more run.
- **Material dispersion ignored or badly fitted:** constant indices give the wrong group index, so every FSR and delay is off; a fit over too wide a band can be wrong in the band you care about.
- **The buried oxide and substrate forgotten:** a grating coupler without its substrate reflection, a thin-BOX nitride guide without its leakage.
- **Run stopped too early:** the fields had not decayed, so the spectrum ripples.
- **Units:** Lumerical uses metres, Tidy3D micrometres and hertz, MEEP a unit length of your choice with $$c = 1$$.

</div>

## <span class="secnum">32.6</span>One problem, three tools: a 2 µm bend

The worked problem: a 90° bend of radius $$R$$ = 2 µm in the 500 × 220 nm strip, clad in oxide, TE-like mode, 1500–1600 nm. Wanted: the transmission into the output guide's TE₀ mode and the reflection back into the input, at 1550 nm, to ±0.01 dB. [Chapter 8]({% link chapters/08_bends.md %}) explains why a bend this tight loses light; here the question is how to compute it well. To keep the comparison clean, silicon and oxide have constant indices, 3.476 and 1.444 (Lab 6 does the same).

The set-up is the same in every tool ([Figure 32.6](#fig-32-6)): a region 4.75 × 4.75 µm in the plane of the chip and 2 µm high, inside the absorbing layers; 1 µm of oxide between each waveguide and the PML; a mode source 1 µm before the bend; mode monitors 0.5 µm before the bend (reflection) and 1 µm after it (transmission); a mirror plane at the mid-height of the core, where the TE-like field is even; and a pulse whose spectrum covers the band. [Table 32.1](#tab-32-1) shows how each tool expresses it.

<figure id="fig-32-6">
  <img src="{{ '/assets/figs/ch32_region.svg' | relative_url }}" style="width:640px" alt="(a) Top view to scale of the simulation region: a silicon strip enters from the left, turns through 90 degrees on a 2 micrometre radius and leaves upwards, both ends running through a grey absorbing border labelled PML, 12 cells. A red line across the input guide 1 micrometre before the bend marks the mode source, with an arrow showing its direction; a blue line 0.5 micrometres before the bend is the reflection monitor and a blue line across the output guide 1 micrometre after the bend is the transmission monitor. Thin grid lines fill the region. The region inside the PML is 4.75 micrometres across; scale bar 1 micrometre. (b) The cross-section through the source: the 500 by 220 nm core in oxide, the absorbing border above, below and to the left, the 2.0 by 1.6 micrometre source plane as a red rectangle, and a dashed teal mirror plane through the middle of the core.">
  <figcaption><span class="capnum">Figure 32.6.</span> <strong>The bend's simulation region, to scale.</strong> (a) Top view. The strip turns through 90° on a 2 µm radius and runs straight through the PML (grey) at both ends; the mode source (red) is 1 µm before the bend, the reflection monitor 0.5 µm before it and the transmission monitor 1 µm after it (blue); 4.75 × 4.75 µm lies inside the PML, with 1 µm of oxide between each guide and the PML. The thin lines are every line of Tidy3D's automatic grid at 20 steps per wavelength: 22 nm wherever there is silicon at that \(x\) or \(y\), growing to 54 nm in the oxide margins. (b) The cross-section through the source: 0.89 µm of oxide above and below the 220 nm core inside the PML, the 2.0 × 1.6 µm source plane, and the mirror plane through the core's mid-height that halves the problem. Drawn by <code>figsrc/ch32_figs.py</code> from the grid of <code>figsrc/ch32_tidy3d_bend.py</code>.</figcaption>
</figure>

**Table 32.1. The bend of Figure 32.6 in three tools.** Names as in each tool's documentation {% include cite.html keys="lumericaldocs,pylumerical,tidy3ddocs,meepdocs" %}; the Tidy3D and MEEP versions are `figsrc/ch32_tidy3d_bend.py` (validated, not run) and `figsrc/ch32_meep_bend.py` (run).
{: .tabcaption #tab-32-1 }

| Step | Lumerical FDTD | Tidy3D | MEEP |
|---|---|---|---|
| Geometry | rectangles and a ring, or `gdsimport` of the layer, z from 0 to 220 nm | `Box` straights and a `PolySlab` arc in a `GeometryGroup` | `Block` straights; arc from `Cylinder`s, or `get_GDSII_prisms` |
| Materials | database entry or constant index | `Medium(permittivity=...)` or a fitted model | `Medium(index=...)` or the materials library |
| Region, boundaries | FDTD region; PML | `size`, `BoundarySpec.all_sides(PML())` | `cell_size`, `PML(1.0)` |
| Grid | auto non-uniform (mesh accuracy) + mesh override over the guide | `GridSpec.auto(min_steps_per_wvl=20)` | uniform `resolution` + sub-pixel averaging |
| Mirror plane | symmetric boundary at z min | `symmetry=(0, 0, 1)` | `Mirror(mp.Z)` |
| Source | mode source (`addmode`) | `ModeSource` | `EigenModeSource` |
| Monitors | mode-expansion and power monitors (or ports, which combine source and monitors) | `ModeMonitor`, `FluxMonitor` | mode monitors, `get_eigenmode_coefficients` |
| Runs on | your CPU or GPU; vendor cloud option | vendor's GPU servers | your CPU; MPI on a cluster |

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.2 · What will the bend cost?</div>

Count the cells first ([Figure 32.7](#fig-32-7)). Tidy3D says it directly: at 20 steps per wavelength its grid is 213 × 213 × 70 = 3.18 million cells, of which 189 × 189 × 46 = 1.64 million lie inside the PML, 22 nm in the silicon and up to 54 nm in the oxide. The mirror plane halves the computed cells, to 0.82 million inside the PML. The smallest cells set the time step, 0.042 fs, just under the stability limit $$\Delta x/(c\sqrt{3})$$ for 22 nm cells. The run must last long enough for the pulse (82 fs for a spectrum 10 % wide), the transit along the 5.1 µm path at $$n_g \approx 4.2$$ (72 fs) and the fields to drain; 250 fs is 5928 steps.

A Lumerical set-up with mesh accuracy 2 (10 points per wavelength, so 104 nm cells in the oxide at 1.5 µm) and a 22 nm mesh override over the silicon has, by this chapter's estimate, 181 × 181 × 28 = 0.92 million cells inside the PML and the same 0.042 fs step. MEEP's grid is uniform: at resolution 25 (40 nm cells) the region holds 0.71 million cells; making every cell 22 nm would need resolution 45 and 4.1 million cells, and a 0.037 fs step, since MEEP uses half the one-dimensional limit $$\Delta x/c$$. Cells (halved by the mirror) times steps gives the work: from 1.3 × 10⁹ cell updates for MEEP at 40 nm to 14 × 10⁹ for MEEP at 22 nm everywhere, with Tidy3D at 4.9 × 10⁹ and the Lumerical estimate at 2.7 × 10⁹. The non-uniform grids save mainly in the vertical direction: in the plane, the bend has silicon at almost every $$x$$ and $$y$$, so their fine lines cover nearly the whole area ([Figure 32.6](#fig-32-6)).

Two costs hide behind these counts. The absorbing layers are not free: Tidy3D's 12 PML cells per side almost double its grid, and MEEP's 1 µm of PML is three quarters of its cells at resolution 25 (2.86 million in all). And memory is modest for a device this small: six field components in double precision take 48 bytes per cell, 40 MB for Tidy3D's 0.82 million; MEEP estimated 101 MB for its resolution-25 run, and the process peaked at 389 MB with Python and its libraries. Time is the real cost. On one core of a shared workstation MEEP managed about 10⁷ cell updates per second, so its resolution-30 run took 21 minutes of CPU time, and the work grows as the fourth power of the resolution (three powers for the cells, one for the steps): halving the cells costs 16 times more.

</div>

<figure id="fig-32-7">
  <img src="{{ '/assets/figs/ch32_cost.svg' | relative_url }}" style="width:640px" alt="Two horizontal bar charts for four set-ups of the bend: Lumerical FDTD with mesh accuracy 2 and a 22 nm override (an estimate), Tidy3D with an automatic grid of 20 steps per wavelength (from the simulation object), MEEP at resolution 25 (run) and MEEP at resolution 45 (by formula). (a) Cells computed with the mirror plane, excluding the PML: 0.46, 0.82, 0.35 and 2.06 million. (b) Cell updates for 250 femtoseconds: 2.7, 4.9, 1.3 and 13.9 billion, from 5960, 5928, 3747 and 6745 time steps.">
  <figcaption><span class="capnum">Figure 32.7.</span> <strong>The same bend, four grids.</strong> (a) Cells computed inside the PML, with the mirror plane; (b) the work for 250 fs of light, cells times time steps. Lumerical: this chapter's estimate for an automatic non-uniform mesh at accuracy 2 with a 22 nm override over the silicon (the tool's own mesher will differ in detail, and its memory check gives the real figures before a run). Tidy3D: counted from the <code>Simulation</code> object of <code>figsrc/ch32_tidy3d_bend.py</code>. MEEP: resolution 25, run here, and resolution 45, which would put the others' 22 nm cells everywhere. The PML adds about 90 % (Tidy3D, 12 cells) to 300 % (MEEP, 1 µm) to these counts. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.3 · Is the answer right?</div>

The MEEP version was run at five resolutions ([Figure 32.8](#fig-32-8)). At resolution 10 (100 nm cells) it reports 0.21 dB of loss and −16 dB of reflection, with a spectrum that ripples: the coarse grid itself reflects. From resolution 15 the reflection falls below −30 dB and the loss into the output TE₀ mode at 1550 nm settles to a few hundredths of a decibel: 0.038, 0.075, 0.073 and 0.062 dB at resolutions 15, 20, 25 and 30.

The power adds up. At resolution 30, 99.26 % of the injected power crosses the output plane and 0.007 % comes back; 98.59 % is in the output TE₀ mode. The 0.67 % in between is light scattered by the bend that has not yet left the guide's neighbourhood 1 µm downstream, which the mode monitor rightly rejects, and the remaining 0.73 % left through the other boundaries.

But ±0.01 dB is not reached, and there is a reason to expect more drift. The last three resolutions spread over 0.013 dB, and the mode solver inside MEEP, which launches and analyses the guided mode, still puts the strip's TE₀ index at 2.379 at resolution 30, against femwell's 2.446 ([Figure 32.3](#fig-32-3)): on this grid the simulated waveguide is a few per cent weaker than the real one, and a weaker guide loses more in a bend. The honest result of these runs is a loss of 0.06–0.08 dB at 1550 nm (0.04–0.08 dB across 1500–1600 nm), more likely to fall than rise with refinement, and a reflection below −30 dB. Pinning it to ±0.01 dB probably needs resolution 60 or more, where the guide's index is within 1 % of femwell's: (60/30)⁴ = 16 times the 21 CPU-minutes of resolution 30, some 6 hours on one core, or minutes on a GPU service or a cluster. Run times like these, more than anything else, are what send 3D simulations to GPUs and clusters.

An independent estimate is a useful check even when it disagrees. [Chapter 8]({% link chapters/08_bends.md %}) estimated 0.24 dB for this bend by adding the mode-mismatch losses of its two straight–bend junctions. The full simulation gives less, which is plausible: light scattered at the first junction into the bend's next mode can partly return to the fundamental mode at the second, depending on the phase it gathers along the bend, so the two losses need not simply add. Chapter 8's model also says where the loss of so tight a bend comes from, the junctions rather than radiation along the arc, and so points to the fix: an Euler or offset bend.

</div>

<figure id="fig-32-8">
  <img src="{{ '/assets/figs/ch32_bendconv.svg' | relative_url }}" style="width:640px" alt="Two plots against MEEP resolution from 10 to 30 cells per micrometre. (a) Bend loss into the output TE0 mode at 1550 nm: 0.21 dB at resolution 10, then 0.038, 0.075, 0.073 and 0.062 dB at 15, 20, 25 and 30, with a shaded band for 1500 to 1600 nm that is wide at resolution 10 and about 0.04 dB wide above 15; on a second axis the reflection, minus 16 dB at resolution 10 and between minus 30 and minus 41 dB above. (b) Log-log plot of the cells computed, from 0.09 to 2.4 million, and the CPU time, from a quarter of a minute to 21 minutes, with dashed guide lines growing as the cube and the fourth power of the resolution.">
  <figcaption><span class="capnum">Figure 32.8.</span> <strong>Converging the bend in MEEP.</strong> (a) Loss into the output TE₀ mode at 1550 nm (blue line) and its range over 1500–1600 nm (band), and the reflection at 1550 nm (red, right axis), against resolution. (b) Cells computed (mirror plane used, PML included) and CPU time on one core, with guide lines growing as the cube and the fourth power of the resolution; the machine was shared and busy, so the times are indicative. Silicon and oxide at 3.476 and 1.444; 250 fs runs. Drawn by <code>figsrc/ch32_figs.py</code> from <code>figsrc/ch32_meep_bend.py</code> (MEEP 1.35.1, 3D).</figcaption>
</figure>

## <span class="secnum">32.7</span>Choosing a tool

[Table 32.2](#tab-32-2) sets the tools side by side. It is not a ranking: each is the right choice for some teams and problems, and many designers use several, checking one against another.

**Table 32.2. Photonic simulation tools at a glance.** From public documentation, November 2026 {% include cite.html keys="lumericalproducts,pylumerical,tidy3ddocs,meepdocs,mpb,femwell,sax,gplugins" %}. Licensing in general terms only.
{: .tabcaption #tab-32-2 }

| Tool | Licensing model | Solvers | Interface | Runs on | Typical uses |
|---|---|---|---|---|---|
| Ansys Lumerical | commercial licence | FDE, EME, varFDTD; 3D/2D FDTD, RCWA; CHARGE, HEAT, FEEM, DGTD, MQW; circuit (INTERCONNECT) | GUI, Lumerical script, Python (PyLumerical) | your computers and clusters, CPU or GPU; vendor cloud option | component to circuit in one suite; active devices; foundry compact-model libraries |
| Tidy3D | commercial service, paid per use; Python client open source (LGPL) | 3D/2D FDTD, mode, EME, heat, charge; adjoint inverse design | Python, web GUI | vendor's GPU servers; mode solver also locally | large 3D runs and sweeps, inverse design |
| MEEP | open source (GPL) | 1D/2D/3D FDTD, adjoint optimisation | Python (and Scheme) | your computers; MPI clusters | research, teaching, custom physics |
| MPB | open source (GPL) | plane-wave eigenmodes | Python, Scheme | your computers | band structures, waveguide modes |
| femwell | open source (GPL) | finite-element modes, heat, electrostatics | Python | your computers | cross-sections and their multiphysics |
| SAX | open source (Apache-2.0) | S-parameter circuits, differentiable | Python (JAX) | your computers | circuit simulation and optimisation |
| gdsfactory + gplugins | open source (MIT) | none of their own: layout and drivers for the solvers above | Python | your computers | one description from layout to every solver |

<p class="small">Ansys and Lumerical are trademarks of Ansys, Inc. (a Synopsys company); Tidy3D is a trademark of Flexcompute, Inc.; other product names are trademarks of their owners. They are used here only to identify the products.</p>

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A tool wraps solvers with geometry, materials, meshing, sources, monitors, job management and scripting; tools built on the same method should agree, so differences between them are set-up differences until shown otherwise.
- Ansys Lumerical: MODE (FDE, EME, varFDTD), FDTD, Multiphysics (CHARGE, HEAT, FEEM, DGTD, MQW) and INTERCONNECT, linked by S-parameters, waveguide data and imported carrier and temperature maps, all scriptable in Lumerical script or Python.
- Tidy3D: a Python object describes the whole simulation and is validated and sized locally; FDTD runs on the vendor's GPU servers after a cost estimate; the mode solver runs locally; gradients for inverse design cost one adjoint run.
- Open tools (MEEP, MPB, femwell, SAX, with gdsfactory and gplugins as the glue) cover mode solving, 2D and modest 3D FDTD and circuits, and make every default inspectable.
- In any tool: geometry, materials (check the fit), grid, source (check the mode), monitors, boundaries and symmetry; treat the first run as a test; converge before you sweep; record versions and settings.
- Converge before you believe: a finite-difference mode solve without sub-pixel averaging (here Tidy3D's local solver without its optional averaging package) scattered by ±0.1 in $$n_\mathrm{eff}$$ as its grid changed; MEEP's converged slowly from below; femwell, whose mesh follows the faces, was steady.
- The 2 µm bend: 0.06–0.08 dB at 1550 nm and reflection below −30 dB from 3D MEEP at 33–50 nm cells, not yet within ±0.01 dB; 3D FDTD cost grows as the fourth power of the resolution, and the absorbing layers can be most of a small problem.

</div>

## Reading

{% include reflist.html keys="lumericalproducts,lumericaldocs,pylumerical,synopsys2025,tidy3ddocs,tidy3dsite,liu2025,meep,meepdocs,farjadpour2006,mpb,femwell,sax,gdsfactory,gplugins,lalaukeraly2013,molesky2018,gustavsen1999,li1980,malitson1965,wilson2014" %}
