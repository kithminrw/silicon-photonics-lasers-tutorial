---
title: "30. Design Flow and Open PDKs"
parent: "Part VII · Fabrication, Testing and Data Analysis"
nav_order: 30
permalink: /part-7/ch30/
chapter: 30
---

# <span class="chapnum">Chapter 30</span>Design Flow and Open PDKs

From an idea to a GDS file: the design flow, the tools, and the open process design kits that let anyone tape out.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe the photonic design flow from concept to tape-out;
- explain what a PDK contains: layers, cells, compact models and rules;
- lay out with KLayout and SiEPIC-Tools, or as code with gdsfactory;
- choose a component solver (mode solver, EME, FDTD) and simulate circuits with S-parameters;
- verify a design and submit it to an openEBL run.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What happens between a simulation and a manufacturable layout?

</div>

## <span class="secnum">30.1</span>The design flow

A photonic design moves through the same stages as an electronic one, with different physics at each:

1. **Concept**: the function, its specifications and a block diagram (for example the reference link of [Chapter 1]({% link chapters/01_why.md %})).
2. **Component simulation**: the cross-sections and devices, with mode solvers and propagation solvers (Section 30.5).
3. **Compact models**: each device reduced to a frequency-dependent scattering matrix, often fitted to simulation or measurement.
4. **Circuit simulation**: the devices connected, and the circuit's response computed from the compact models (Section 30.6).
5. **Layout**: the geometry drawn on the foundry's layers, from PDK cells and routed waveguides (Sections 30.3–30.4).
6. **Verification**: design-rule checks, connectivity checks and design-for-test rules (Section 30.7).
7. **Tape-out**: the GDS file sent to the foundry (Section 30.8), then testing ([Chapter 31]({% link chapters/31_testing.md %})) and analysis ([Chapter 32]({% link chapters/32_analysis.md %})), whose results update the compact models.

## <span class="secnum">30.2</span>Process design kits

A **process design kit** (PDK) is the foundry's description of its process, packaged for design tools:

- the **layer table**: which GDS layer is the full etch, the partial etch, each implant, each metal;
- **cells** and parameterised cells (PCells): grating couplers, edge couplers, Y-branches, MMIs, rings, modulators, photodiodes, pads, each validated on silicon;
- **compact models** of those cells for circuit simulation;
- **design rules**: minimum widths, gaps, enclosures and densities;
- often a **layer stack** (thicknesses and materials) for simulation, and design-for-test rules.

Most commercial PDKs are under non-disclosure agreements. This tutorial uses only open ones: the SiEPIC EBeam PDK {% include cite.html keys="ebeampdk" %} and its gdsfactory version {% include cite.html keys="ubcpdk" %}, the CORNERSTONE PDKs {% include cite.html keys="cspdk" %} and the Luxtelligence TFLN PDK {% include cite.html keys="lxtpdk" %}. Their devices, credited to their designers, are shown in the [3D gallery]({% link devices-3d.md %}), extruded from their layouts with their published layer stacks.

## <span class="secnum">30.3</span>Layout with KLayout and SiEPIC-Tools

**KLayout** is an open-source layout viewer and editor {% include cite.html keys="klayout" %}. The **SiEPIC-Tools** package adds what photonic layout needs {% include cite.html keys="siepictools" %}: placing PDK cells, routing waveguides between their ports with bends of the right radius, extracting a netlist from the layout (which device connects to which), running a circuit simulation from that netlist, and checking the design-for-test rules. Interactive layout suits small designs and is how most openEBL submissions are made.

## <span class="secnum">30.4</span>Layout as code with gdsfactory

**gdsfactory** builds layouts from Python (or YAML) code {% include cite.html keys="gdsfactory" %}. A component is a function of its parameters; a circuit is a composition of components and routes; a PDK is a Python package of components, layers and models. Writing layout as code makes parameter sweeps, variations and regression tests easy. A family of 20 rings with different gaps is a loop. It also connects directly to simulators: mode solvers, FDTD and circuit simulation from the same description. The 3D models in the gallery were generated with gdsfactory from the open PDKs.

## <span class="secnum">30.5</span>Component simulation

Three kinds of solver cover most needs, from fast to general:

- **Mode solvers** (finite-difference or finite-element eigenmode, FDE/FEM) find the modes of a cross-section: effective and group indices, confinement, overlaps. This tutorial's numbers come from the open finite-element solver femwell: the strip modes of [Chapter 6]({% link chapters/06_soi.md %}), the supermodes of [Chapters 9]({% link chapters/09_couplers.md %}) and [27]({% link chapters/27_lasersonsi.md %}), the inverse tapers of [Chapter 16]({% link chapters/16_edge.md %}), the PN junction of [Chapter 19]({% link chapters/19_eo.md %}).
- **Eigenmode expansion (EME)** propagates light through a device that changes along its length by expanding the field in local modes at each section. It is fast for tapers, MMIs and couplers.
- **Finite-difference time-domain (FDTD)** solves Maxwell's equations directly on a grid in time, for any geometry, including gratings and reflections. It is the most general and the most expensive; MEEP is the open-source standard {% include cite.html keys="meep" %}. Two-dimensional FDTD with an effective index ([Chapter 6]({% link chapters/06_soi.md %})) is a quick first pass for grating couplers.

## <span class="secnum">30.6</span>Circuit simulation

A circuit of tens or thousands of devices is too large for any field solver. Instead, each device becomes a **compact model**, its scattering matrix as a function of wavelength. For a directional coupler this is a 4 × 4 matrix whose cross terms carry the $$-j\kappa$$ of [Chapter 9]({% link chapters/09_couplers.md %}); for a waveguide, a phase $$e^{-j\beta L}$$ with $$\beta(\lambda)$$ from its effective and group indices. A circuit simulator connects the matrices according to the netlist and solves for the response at the circuit's ports. **SAX** does this in Python, with automatic differentiation for optimisation {% include cite.html keys="sax" %}; KLayout/SiEPIC-Tools links to circuit simulators from the extracted netlist.

**Try it.** Build an MZI or a lattice filter from couplers and delays, see the netlist, and change the coupling ratios.

{% include demos/circuit.html %}

## <span class="secnum">30.7</span>Verification

Before tape-out, a design is checked:

- **Design-rule checks** (DRC): every shape obeys the foundry's minimum widths, gaps and enclosures; KLayout runs the PDK's rule deck.
- **Connectivity**: every waveguide port connects to something, with matched widths; no waveguide crosses another unintentionally; the extracted netlist matches the intended circuit.
- **Design for test**: grating couplers on the fibre-array pitch, all facing the same way, with test labels ([Chapter 17]({% link chapters/17_fiberarrays.md %})).
- **Simulation of the layout itself**: the circuit simulated from the netlist extracted from the drawn layout, not from the schematic, which catches routing lengths and bends that change phases.

## <span class="secnum">30.8</span>Tape-out through openEBL

The openEBL runs accept designs through GitHub: a designer adds a GDS file to the run's repository by pull request, automated checks run DRC and the design-for-test rules on it, and the merged designs are combined and fabricated. The chips are measured on an automated probe station and the data come back through the same repository {% include cite.html keys="openebl" %}. The open designs and data of past runs are a rich source for learning, and for [Chapter 32]({% link chapters/32_analysis.md %}).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Draw the chip in KLayout with SiEPIC-Tools (or generate it with gdsfactory and ubcpdk): a loopback, cutback spirals, MZIs with two arm-length differences, rings with three gaps, and a Bragg grating, all on the 127 µm coupler column with test labels. Simulate the circuits from the extracted netlist, run DRC and the design-for-test check, and submit by pull request.

</div>

## Reading

{% include reflist.html keys="gdsfactory,siepictools,ebeampdk,ubcpdk,cspdk,lxtpdk,sax,meep,klayout,openebl" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Flow: concept → component simulation → compact models → circuit simulation → layout → verification → tape-out → test → back to the models.
- A PDK holds the layers, validated cells, compact models, rules and layer stack; open PDKs (SiEPIC EBeam, CORNERSTONE, Luxtelligence) make public designs possible.
- KLayout with SiEPIC-Tools for interactive layout; gdsfactory for layout as code.
- Mode solvers, EME and FDTD trade speed for generality; circuits are simulated from S-matrix compact models (SAX).
- Verify with DRC, connectivity, design-for-test and layout-extracted simulation; openEBL takes designs and returns data through GitHub.

</div>
