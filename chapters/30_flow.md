---
title: "30. Design Flow and Open PDKs"
parent: "Part VII · Design, Simulation and Layout"
nav_order: 30
permalink: /part-7/ch30/
chapter: 30
---

# <span class="chapnum">Chapter 30</span>Design Flow and Open PDKs

From an idea to a GDS file: the design flow, the tools and files that carry a design along it, and the open process design kits that let anyone tape out.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe the photonic design flow from concept to tape-out, and which chapter of Part VII covers each stage;
- explain what a PDK contains: layers, cells, compact models, rules and the layer stack;
- build layouts from PDK cells, interactively in KLayout with SiEPIC-Tools or as code with gdsfactory;
- place component and circuit simulation in the flow, and simulate a circuit from compact models and a netlist;
- list the checks a design passes before tape-out, and submit it to an openEBL run.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which tools and files carry a design from a simulation to a manufacturable layout?

</div>

## <span class="secnum">30.1</span>The design flow

A photonic design moves through the same stages as an electronic one, with different physics at each ([Figure 30.1](#fig-30-1)):

1. **Concept**: the function, its specifications and a block diagram (for example the reference link of [Chapter 1]({% link chapters/01_why.md %})), broken down into budgets and component targets ([Chapter 29]({% link chapters/29_design.md %})).
2. **Component simulation**: the cross-sections and devices, with mode solvers and propagation solvers (Section 30.5; [Chapters 31]({% link chapters/31_simulators.md %}) and [32]({% link chapters/32_simtools.md %})).
3. **Compact models**: each device reduced to a frequency-dependent scattering matrix, often fitted to simulation or measurement.
4. **Circuit simulation**: the devices connected, and the circuit's response computed from the compact models (Section 30.6).
5. **Layout**: the geometry drawn on the foundry's layers, from PDK cells and routed waveguides (Sections 30.3–30.4; [Chapter 33]({% link chapters/33_layout.md %})).
6. **Verification**: design-rule checks, connectivity checks and design-for-test rules (Section 30.7; [Chapter 34]({% link chapters/34_verification.md %})).
7. **Tape-out**: the GDS file sent to the foundry (Section 30.8), then fabrication ([Chapter 35]({% link chapters/35_fab.md %})), testing ([Chapter 36]({% link chapters/36_testing.md %})) and analysis ([Chapter 37]({% link chapters/37_analysis.md %})), whose results update the compact models.

<figure id="fig-30-1">
  <img src="{{ '/assets/figs/ch30_flow.svg' | relative_url }}" style="width:600px" alt="Block diagram of the design flow as a loop. Top row, left to right: concept and specification, component simulation, compact models, circuit simulation, layout, each with its tools. Down to the bottom row, right to left: verification, tape-out, fabrication, test, analysis. A red arrow returns from analysis to compact models, labelled measured effective and group index, loss and coupling update the models; a dashed arrow from circuit simulation back to component simulation is labelled iterate until the circuit meets the spec.">
  <figcaption><span class="capnum">Figure 30.1.</span> <strong>The design flow is a loop.</strong> The designer's stages (light blue) run from the specification to the GDS file; fabrication, test and analysis (cream) follow. Two loops close it: simulation is repeated until the circuit meets its specification, and the measured indices, losses and couplings update the compact models for the next design. Not to scale. Drawn by <code>figsrc/ch30_figs.py</code>.</figcaption>
</figure>

This chapter follows a design through the tools and files of the flow. The decisions behind it (budgets, margins, which model to trust, how many dies will work) are the subject of [Chapter 29]({% link chapters/29_design.md %}); the solvers, the layout and the checks each have a chapter of their own in this part.

## <span class="secnum">30.2</span>Process design kits

A **process design kit** (PDK) is the foundry's description of its process, packaged for design tools ([Figure 30.2](#fig-30-2)):

- the **layer table**: which GDS layer is the full etch, the partial etch, each implant, each metal;
- **cells** and parameterised cells (PCells): grating couplers, edge couplers, Y-branches, MMIs, rings, modulators, photodiodes, pads, each validated on silicon;
- **compact models** of those cells for circuit simulation;
- **design rules**: minimum widths, gaps, enclosures and densities;
- often a **layer stack** (thicknesses and materials) for simulation, and design-for-test rules.

<figure id="fig-30-2">
  <img src="{{ '/assets/figs/ch30_pdk.svg' | relative_url }}" style="width:600px" alt="Six cards showing what a PDK contains: a layer table of colour swatches with names and GDS layer numbers; cells and parameterised cells (grating coupler, Y-branch, ring with radius and gap); compact models (a two-port S-matrix and a grating-coupler transmission curve against wavelength); design rules (minimum width, minimum gap, enclosure and density); a layer stack (buried oxide 2 micrometres, silicon 220 nm with a 90 nm slab, heater, metal); and design-for-test rules (couplers on a 127 micrometre pitch with a machine-readable label). Each card names the tool that uses it.">
  <figcaption><span class="capnum">Figure 30.2.</span> <strong>What a process design kit contains</strong>, and which tool uses each part: the layer table (layout and DRC), validated cells and PCells (layout), compact models (circuit simulation), design rules (DRC), the layer stack (mode and FDTD solvers) and design-for-test rules (the test station). The GDS layer numbers are illustrative; every PDK defines its own. Drawn by <code>figsrc/ch30_figs.py</code>.</figcaption>
</figure>

Most commercial PDKs are under non-disclosure agreements. This tutorial uses only open ones: the SiEPIC EBeam PDK {% include cite.html keys="ebeampdk" %} and its gdsfactory version {% include cite.html keys="ubcpdk" %}, the CORNERSTONE PDKs {% include cite.html keys="cspdk" %} and the Luxtelligence TFLN PDK {% include cite.html keys="lxtpdk" %}. Their devices, credited to their designers, are shown in the [3D gallery]({% link devices-3d.md %}), extruded from their layouts with their published layer stacks.

## <span class="secnum">30.3</span>Layout with KLayout and SiEPIC-Tools

**KLayout** is an open-source layout viewer and editor {% include cite.html keys="klayout" %}, and **SiEPIC-Tools** adds what photonic layout needs {% include cite.html keys="siepictools" %}: placing PDK cells, routing waveguides between their ports, extracting a netlist from the layout, simulating the circuit from it, and checking the design-for-test rules. Interactive layout suits small designs and is how most openEBL submissions are made. Whatever the tool, a layout is a hierarchy of cells: PDK cells placed as they are, waveguides drawn by parameterised cells, all inside a test cell with its label ([Figure 30.3](#fig-30-3)). [Chapter 33]({% link chapters/33_layout.md %}) covers the GDSII format, KLayout and its scripting, and photonic layout practice in depth.

<figure id="fig-30-3">
  <img src="{{ '/assets/figs/ch30_layout.svg' | relative_url }}" style="width:600px" alt="Left: top view of a test cell: two grating couplers 127 micrometres apart on the left, the lower one feeding a Y-branch, two arms of which the upper makes a hairpin 100 micrometres longer, a second Y-branch, and a routed waveguide with 5 micrometre bends running back to the upper coupler. Dashed boxes mark the PDK cells' device-recognition regions, red marks their pins, a text label opt_in_TE_1550_MZI1 sits by a coupler, and a floor-plan rectangle encloses everything; scale bar 50 micrometres. Right: the cell hierarchy, TOP containing MZI1, which contains two ebeam_gc_te1550 cells, two ebeam_y_1550 cells and four Waveguide PCells.">
  <figcaption><span class="capnum">Figure 30.3.</span> <strong>A test cell and its hierarchy.</strong> (a) An unbalanced MZI between two grating couplers on the 127 µm fibre-array pitch, laid out in the style of the SiEPIC EBeam PDK (its cell names, simplified outlines): positions to scale, waveguides drawn as lines. The long arm's hairpin adds exactly 100 µm. Each PDK cell carries a device-recognition box and pins, which let the tools extract the netlist; the text label tells the test station what to measure. (b) The cell hierarchy: fixed PDK cells and parameterised waveguide cells inside the test cell, inside the chip {% include cite.html keys="ebeampdk,siepictools" %}. Drawn by <code>figsrc/ch30_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">30.4</span>Layout as code with gdsfactory

**gdsfactory** builds layouts from Python (or YAML) code {% include cite.html keys="gdsfactory" %}. A component is a function of its parameters; a circuit is a composition of components and routes; a PDK is a Python package of components, layers and models. Writing layout as code makes parameter sweeps, variations and regression tests easy. A family of 20 rings with different gaps is a loop, and the design is a script that can be versioned and rerun ([Chapter 29]({% link chapters/29_design.md %}), Section 29.9). It also connects directly to simulators: mode solvers, FDTD and circuit simulation from the same description. The 3D models in the gallery were generated with gdsfactory from the open PDKs, and [Lab 7]({% link labs/lab07_layout.md %}) lays out the first chip of this tutorial with it; [Chapter 33]({% link chapters/33_layout.md %}) goes further.

## <span class="secnum">30.5</span>Component simulation

Three kinds of solver cover most component simulation, from fast to general ([Figure 30.4](#fig-30-4)): **mode solvers** (finite-difference or finite-element eigenmode, FDE/FEM) find the modes of a cross-section; **eigenmode expansion** (EME) propagates light through a device that changes along its length, section by section; and **finite-difference time-domain** (FDTD) solves Maxwell's equations on a grid in time for any geometry, in two dimensions, in 2.5D with an effective index, or in full 3D. This tutorial's numbers come from the open finite-element solver femwell (the strip modes of [Chapter 6]({% link chapters/06_soi.md %}), the supermodes of [Chapters 9]({% link chapters/09_couplers.md %}) and [27]({% link chapters/27_lasersonsi.md %}), the inverse tapers of [Chapter 16]({% link chapters/16_edge.md %}), the PN junction of [Chapter 19]({% link chapters/19_eo.md %})) and from MEEP, the open-source FDTD standard {% include cite.html keys="meep" %}.

<figure id="fig-30-4">
  <img src="{{ '/assets/figs/ch30_solvers.svg' | relative_url }}" style="width:600px" alt="Three sketches. (a) Mode solver: the cross-section of a silicon strip in oxide covered by a triangular mesh that is finer near the core, with contours of the mode intensity around the strip. (b) Eigenmode expansion: the top view of a taper approximated by six sections of constant width, separated by dashed lines, each with its local mode profile drawn as a red curve that widens with the section; arrows mark forward and backward modes matched at each interface. (c) FDTD: a waveguide on a square grid with a snapshot of a pulse's oscillating field, red and blue, travelling along it.">
  <figcaption><span class="capnum">Figure 30.4.</span> <strong>Three kinds of solver.</strong> (a) A mode solver meshes one cross-section (finely where the field changes fast) and returns its modes. (b) Eigenmode expansion cuts a device that varies along its length into sections of constant cross-section, finds each section's modes and matches them at the interfaces, giving the device's S-matrix. (c) FDTD steps the fields on a grid through time, here a pulse travelling along a waveguide; it handles any geometry at the highest cost. Schematic: meshes, fields and grids not to scale. Drawn by <code>figsrc/ch30_figs.py</code>.</figcaption>
</figure>

Which solver to use for which question, and what each costs, is a design decision ([Chapter 29]({% link chapters/29_design.md %}), Section 29.3). How the solvers work, from the Yee cell of FDTD to the mode matching of EME, is in [Chapter 31]({% link chapters/31_simulators.md %}); setting up and checking real runs, in commercial and open tools, is in [Chapter 32]({% link chapters/32_simtools.md %}).

## <span class="secnum">30.6</span>Circuit simulation

A circuit of tens or thousands of devices is too large for any field solver. Instead, each device becomes a **compact model**, its scattering matrix as a function of wavelength. For a directional coupler this is a 4 × 4 matrix whose cross terms carry the $$-j\kappa$$ of [Chapter 9]({% link chapters/09_couplers.md %}); for a waveguide, a phase $$e^{-j\beta L}$$ with $$\beta(\lambda)$$ from its effective and group indices. A circuit simulator connects the matrices according to the netlist and solves for the response at the circuit's ports ([Figure 30.5](#fig-30-5)). **SAX** does this in Python, with automatic differentiation for optimisation {% include cite.html keys="sax" %}; KLayout/SiEPIC-Tools links to circuit simulators from the extracted netlist; [Lab 4]({% link labs/lab04_sax.md %}) builds the models and netlists by hand. Where compact models are valid and how they carry fabrication variation into a circuit Monte Carlo is in [Chapter 29]({% link chapters/29_design.md %}) (Sections 29.5 and 29.7).

<figure id="fig-30-5">
  <img src="{{ '/assets/figs/ch30_netlist.svg' | relative_url }}" style="width:600px" alt="Top: the test cell as six S-parameter blocks with red port dots and names: gc1 and gc2 (two-port grating-coupler models), y1 and y2 (three-port Y-branch models), arm1 224.3 micrometres and arm2 124.3 micrometres (two-port straight waveguides), joined port to port. Bottom left: the netlist as text, listing instances, connections and external ports. Bottom right: simulated transmission from 1500 to 1600 nm, MZI fringes with a free spectral range of 5.7 nm under the dashed parabolic envelope of the two couplers, peaking at minus 8.2 dB near 1549 nm.">
  <figcaption><span class="capnum">Figure 30.5.</span> <strong>The test cell of Figure 30.3 as a circuit.</strong> (a) Each device becomes a block with named ports and an S-matrix: grating couplers and straight waveguides have two ports, Y-branches three. The routing waveguides to the couplers are left out here; they add only a common phase and a little loss. (b) The netlist: instances, the connections between ports, and the circuit's external ports. (c) The response computed from it, with the grating-coupler model of the SiEPIC EBeam PDK (4.1 dB peak loss, 30.6 nm 1 dB bandwidth {% include cite.html keys="ebeampdk" %}), ideal Y-branches and the femwell waveguide model of Chapter 6 (\(n_\mathrm{eff}\) 2.446, \(n_g\) 4.18, 2 dB/cm): fringes 5.7 nm apart under the couplers' envelope. Drawn by <code>figsrc/ch30_figs.py</code>.</figcaption>
</figure>

**Try it.** Build an MZI or a lattice filter from couplers and delays, see the netlist, and change the coupling ratios.

{% include demos/circuit.html %}

## <span class="secnum">30.7</span>Verification

Before tape-out, a design passes four kinds of check, each covered in depth in [Chapter 34]({% link chapters/34_verification.md %}):

- **Design-rule checks** (DRC): every shape obeys the foundry's minimum widths, gaps and enclosures; KLayout runs the PDK's rule deck.
- **Connectivity**: every waveguide port connects to something, with matched widths; no waveguide crosses another unintentionally; the extracted netlist matches the intended circuit.
- **Design for test**: grating couplers on the fibre-array pitch, all facing the same way, with test labels ([Chapter 17]({% link chapters/17_fiberarrays.md %})).
- **Simulation of the layout itself**: the circuit simulated from the netlist extracted from the drawn layout, not from the schematic, which catches routing lengths and bends that change phases. Simulate and check what was drawn, not what was meant.

## <span class="secnum">30.8</span>Tape-out through openEBL

The openEBL runs accept designs through GitHub: a designer adds a GDS file to the run's repository by pull request, automated checks run DRC and the design-for-test rules on it, and the merged designs are combined and fabricated. The chips are measured on an automated probe station and the data come back through a link in the same repository {% include cite.html keys="openebl" %}. The open designs and data of past runs are a rich source for learning, and for [Chapter 37]({% link chapters/37_analysis.md %}). [Lab 8]({% link labs/lab08_submit.md %}) runs the checks on the first chip and prepares the submission.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Draw the chip in KLayout with SiEPIC-Tools (or generate it with gdsfactory and ubcpdk): a loopback, cutback spirals, MZIs with two arm-length differences, rings with three gaps, and a Bragg grating, all on the 127 µm coupler column with test labels. Simulate the circuits from the extracted netlist, run DRC and the design-for-test check, and submit by pull request.

</div>

## Reading

{% include reflist.html keys="gdsfactory,siepictools,ebeampdk,ubcpdk,cspdk,lxtpdk,sax,meep,klayout,openebl,bogaerts2018" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Flow: concept → component simulation → compact models → circuit simulation → layout → verification → tape-out → test → back to the models; Chapters 29–37 take each stage in depth.
- A PDK holds the layers, validated cells, compact models, rules and layer stack; open PDKs (SiEPIC EBeam, CORNERSTONE, Luxtelligence) make public designs possible.
- KLayout with SiEPIC-Tools for interactive layout; gdsfactory for layout as code, which can be versioned, swept and rerun.
- Mode solvers, EME and FDTD trade speed for generality; circuits are simulated from S-matrix compact models and a netlist (SAX, SiEPIC-Tools).
- Verify with DRC, connectivity, design-for-test and layout-extracted simulation; openEBL takes designs and returns data through GitHub.

</div>

## Check yourself

{% include quiz.html %}
