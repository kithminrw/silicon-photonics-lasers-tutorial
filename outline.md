---
title: Tutorial Outline
layout: default
nav_order: 2
permalink: /outline/
---

# Tutorial Outline

The whole tutorial on one page: every part, chapter and section, and the interactive demos (also listed on their own on the [demos page]({% link demos.md %})).
{: .chapterlead }

## Part I · Foundations

Light as an electromagnetic wave, the Gaussian beams and fibres that carry it to a chip, and the materials (silicon, silicon nitride, lithium niobate, barium titanate, indium phosphide) that photonic chips are made of.

### [1. Why Integrated Photonics?]({% link chapters/01_why.md %})

*When does light beat copper, and what does a photonic chip need to do it?*

1.1 Light versus charge · 1.2 Applications · 1.3 Why silicon, and why not only silicon · 1.4 Anatomy of a photonic integrated circuit · 1.5 Optical power and decibels · 1.6 The two running examples · 1.7 How to use this tutorial

Demos: Power budget

### [2. Electromagnetic Theory for Photonics]({% link chapters/02_em.md %})

*What does light do at an interface, and how does that lead to confinement?*

2.1 Maxwell's equations in matter · 2.2 The wave equation and plane waves · 2.3 Refractive index, absorption and dispersion · 2.4 Polarisation and power · 2.5 Reflection and refraction · 2.6 Total internal reflection and evanescent waves · 2.7 Phase velocity, group velocity and group index

Demos: Polarisation ellipse; Snell, Fresnel and total internal reflection; Wave packet

### [3. Gaussian Beams and Optical Fibres]({% link chapters/03_gaussian.md %})

*How much light gets from one Gaussian mode into another?*

3.1 The paraxial wave equation · 3.2 The Gaussian beam · 3.3 Beam transformation with q and ABCD · 3.4 Optical fibres · 3.5 Mode overlap and coupling efficiency · 3.6 Gaussian beams in photonic chips

Demos: Gaussian beam and lens; Fibre modes

### [4. Materials and Platforms: Si, SiN, TFLN, BTO and InP]({% link chapters/04_platforms.md %})

*Which platform for which job?*

4.1 What a platform must provide · 4.2 The materials · 4.3 Silicon-on-insulator · 4.4 Silicon nitride · 4.5 Thin-film lithium niobate · 4.6 Barium titanate · 4.7 Indium phosphide and other III–Vs · 4.8 Choosing and combining platforms

Demos: Platform comparator

## Part II · Waveguides

How a strip of high-index material guides light: slab and channel waveguides on SOI and other platforms, the losses that limit them, and the bends, tapers and transitions that route light around a chip.

### [5. The Slab Waveguide]({% link chapters/05_slab.md %})

*What sets the number of guided modes and their effective index?*

5.1 The ray picture and transverse resonance · 5.2 TE and TM modes · 5.3 Effective index and normalised parameters · 5.4 Cut-off and the single-mode condition · 5.5 Confinement and the evanescent field · 5.6 Group index of a slab mode

Demos: Slab-waveguide mode solver

### [6. Channel Waveguides on SOI and Beyond]({% link chapters/06_soi.md %})

*Which width and etch depth give single-mode, low-loss, compact routing?*

6.1 Geometries · 6.2 The effective-index method · 6.3 Numerical mode solvers · 6.4 Effective and group index of SOI waveguides · 6.5 Single-mode conditions and polarisation · 6.6 Other platforms · 6.7 Sensitivity to fabrication

Demos: Effective-index explorer; Full-vectorial 2D mode solver

### [7. Loss, Dispersion and Nonlinearity]({% link chapters/07_loss.md %})

*What limits a waveguide's propagation loss, and how do you measure it?*

7.1 Loss mechanisms and units · 7.2 Sidewall-roughness scattering · 7.3 Absorption · 7.4 Substrate leakage · 7.5 Dispersion · 7.6 Nonlinear effects · 7.7 Measuring loss · 7.8 Nonlinear devices: frequency conversion and microcombs

Demos: Cutback simulator; Sidewall-roughness scattering

### [8. Bends, Tapers and Transitions]({% link chapters/08_bends.md %})

*How tight can a bend be, and how short a taper?*

8.1 Radiation loss in bends · 8.2 Mode mismatch at straight–bend junctions · 8.3 Tapers and adiabaticity · 8.4 Overlap integrals and butt coupling · 8.5 Waveguide crossings · 8.6 Transitions between layers

Demos: Circular and Euler bends; Taper adiabaticity

## Part III · Passive Devices

The building blocks that split, combine, filter and route light without power: directional couplers, Y-branches and MMIs, Mach–Zehnder interferometers, ring resonators, Bragg gratings, and WDM and polarisation devices.

### [9. Coupled-Mode Theory and Directional Couplers]({% link chapters/09_couplers.md %})

*Which length and gap give a 50/50 split, and how robust is it?*

9.1 Coupled-mode equations · 9.2 Supermodes · 9.3 The directional coupler · 9.4 Wavelength, polarisation and fabrication sensitivity · 9.5 Broadband and adiabatic couplers · 9.6 The 2 × 2 scattering matrix

Demos: Directional coupler

### [10. Y-Branches and Multimode Interference Couplers]({% link chapters/10_mmi.md %})

*Y-branch or MMI, and how long must the MMI be?*

10.1 Y-branches · 10.2 Mode excitation at an abrupt junction · 10.3 Self-imaging in a multimode waveguide · 10.4 MMI design · 10.5 Comparing splitters

Demos: MMI self-imaging

### [11. Mach–Zehnder Interferometers]({% link chapters/11_mzi.md %})

*How does the arm-length difference set the spectrum?*

11.1 Interference and optical phase · 11.2 The MZI transfer function · 11.3 Unbalanced MZIs · 11.4 Tuning · 11.5 Cascaded and lattice filters · 11.6 MZIs as test structures

Demos: Mach–Zehnder interferometer

### [12. Ring Resonators]({% link chapters/12_rings.md %})

*How do coupling and loss shape a ring's resonance?*

12.1 Resonance condition · 12.2 The all-pass ring · 12.3 The add-drop ring · 12.4 Quality factor and finesse · 12.5 Extracting parameters from measurements · 12.6 Non-idealities · 12.7 Applications

Demos: Ring resonator

### [13. Bragg Gratings and Photonic Crystals]({% link chapters/13_bragg.md %})

*How long and how strong must a grating be for a given reflectivity and bandwidth?*

13.1 Periodic waveguides and the Bragg condition · 13.2 Coupled-mode theory of gratings · 13.3 The transfer-matrix method · 13.4 Apodisation and chirp · 13.5 The Fabry–Pérot cavity · 13.6 Phase-shifted gratings · 13.7 Contra-directional couplers and SWG metamaterials · 13.8 Photonic crystals

Demos: Bragg grating · Fabry–Pérot cavity

### [14. WDM Filters and Polarisation Management]({% link chapters/14_wdm.md %})

*How do you separate four wavelengths with low crosstalk?*

14.1 WDM grids and requirements · 14.2 Ring and MZI-lattice multiplexers · 14.3 Arrayed-waveguide and echelle gratings · 14.4 Crosstalk, flat-top responses and tuning · 14.5 Polarisation splitters and rotators · 14.6 Polarisation diversity · 14.7 Mode-division multiplexing

Demos: Four-ring demultiplexer

## Part IV · Coupling and Packaging

Getting light on and off the chip: grating couplers, edge couplers, fibre arrays, photonic wire bonds and the packaging that turns a die into a product.

### [15. Grating Couplers]({% link chapters/15_gc.md %})

*Which period and angle couple 1550 nm TE light into a fibre tilted at 8°, and how much of the light can you expect to get?*

15.1 Phase matching · 15.2 Directionality · 15.3 Mode matching to the fibre · 15.4 Bandwidth and polarisation · 15.5 Back-reflection · 15.6 Focusing, SWG and 2D grating couplers · 15.7 Grating couplers in practice

Demos: Grating-coupler phase matching · Grating-coupler efficiency budget

### [16. Edge Couplers and Spot-Size Converters]({% link chapters/16_edge.md %})

*How narrow must the taper tip be to match a 3 µm or a 10 µm spot?*

16.1 Edge-coupling basics · 16.2 Inverse tapers · 16.3 Multi-stage couplers and overlays · 16.4 Facets · 16.5 Fibres at the edge · 16.6 Edge against grating couplers

Demos: Inverse-taper edge coupler

### [17. Fibre Arrays, Photonic Wire Bonds and Packaging]({% link chapters/17_fiberarrays.md %})

*How tolerant is a coupling interface, and how do you find the peak quickly?*

17.1 Fibre arrays · 17.2 Alignment · 17.3 Attaching fibres · 17.4 Photonic wire bonds and micro-optics · 17.5 Facet-attached microlenses · 17.6 Laser and chip assembly · 17.7 Co-packaged optics · 17.8 Design rules for test and packaging

Demos: Alignment tolerance · Fibre-array alignment · Facet-attached microlenses

## Part V · Active Devices

Tuning, modulating and detecting light: thermo-optic phase shifters, electro-optic effects in each platform, modulators, and germanium photodetectors and receivers.

### [18. Thermo-Optic Phase Shifters]({% link chapters/18_thermal.md %})

*How many milliwatts for a π shift, and how fast?*

18.1 The thermo-optic effect · 18.2 Heater types · 18.3 Thermal circuits · 18.4 Improving efficiency · 18.5 Crosstalk and stabilisation

Demos: Thermo-optic phase shifter · Ring locking

### [19. Electro-Optic Effects Across Platforms]({% link chapters/19_eo.md %})

*Which effect gives the best VπL for a given loss and bandwidth?*

19.1 Free-carrier plasma dispersion · 19.2 PN, PIN and MOS structures · 19.3 The Pockels effect · 19.4 Electro-absorption · 19.5 Figures of merit

Demos: PN depletion phase shifter · Pockels phase shifter on thin-film LiNbO₃ and BTO

### [20. Modulators]({% link chapters/20_modulators.md %})

*Mach–Zehnder or ring modulator for a four-wavelength link?*

20.1 Modulator metrics · 20.2 Mach–Zehnder modulators · 20.3 Ring modulators · 20.4 Electro-absorption modulators · 20.5 TFLN and BTO modulators · 20.6 Modulation formats · 20.7 Driver and modulator co-design · 20.8 Ring-modulator dynamics · 20.9 Driving, linearising and locking a ring

Demos: MZM and eye diagram · Ring modulator

### [21. Photodetectors and Receivers]({% link chapters/21_pd.md %})

*How much optical power does the receiver need for a target BER?*

21.1 Absorption and responsivity · 21.2 Germanium-on-silicon photodiodes · 21.3 Bandwidth · 21.4 Dark current and noise · 21.5 Avalanche photodiodes · 21.6 Receivers · 21.7 Monitor photodiodes · 21.8 Designing the receiver front end, step by step · 21.9 Equalisation, clock recovery and measuring sensitivity

Demos: Photodiode bandwidth · Receiver sensitivity

## Part VI · Lasers and Amplifiers

From the physics of gain to working lasers: emission and gain in semiconductors, the Fabry–Pérot laser and its rate equations, noise and linewidth, tunable and narrow-linewidth lasers, lasers on silicon, and semiconductor optical amplifiers.

### [22. Light Meets Matter: Absorption, Emission and Gain]({% link chapters/22_emission.md %})

*What does it take for a material to amplify light?*

22.1 Photons and energy levels · 22.2 Absorption and emission · 22.3 Population inversion and gain · 22.4 Lineshape and gain spectrum · 22.5 Direct and indirect bandgaps

Demos: Level-system model

### [23. Semiconductor Gain Media]({% link chapters/23_gain.md %})

*How many carriers does it take to reach gain, and where is the gain peak?*

23.1 Bands, density of states and occupation · 23.2 Quasi-Fermi levels and the condition for gain · 23.3 The gain spectrum · 23.4 Heterostructures, quantum wells and quantum dots · 23.5 Material systems for 1310 and 1550 nm · 23.6 Recombination

Demos: Gain spectrum

### [24. The Fabry–Pérot Laser and the Rate Equations]({% link chapters/24_fp.md %})

*What sets a laser's threshold current and slope efficiency?*

24.1 The optical cavity · 24.2 Threshold · 24.3 Rate equations · 24.4 The L–I curve and efficiency · 24.5 Temperature · 24.6 Transients · 24.7 The Fabry–Pérot spectrum · 24.8 The vertical-cavity surface-emitting laser · 24.9 Inside the chip: layer stacks in 3D

Demos: Laser rate equations, with self-heating · 3D models of laser, SOA and VCSEL stacks

### [25. Laser Dynamics, Noise and Linewidth]({% link chapters/25_dynamics.md %})

*How fast can you modulate a laser directly, and how narrow is its line?*

25.1 Small-signal modulation · 25.2 Chirp and the α-factor · 25.3 Relative intensity noise · 25.4 Phase noise and linewidth · 25.5 Optical feedback · 25.6 Narrowing the linewidth · 25.7 Driving a laser: bias, modulation and extinction ratio · 25.8 The laser as a circuit, and equalisation · 25.9 Output stages and temperature control · 25.10 Laser transmitters compared: VCSELs, DMLs and EMLs

Demos: Modulation response, RIN and linewidth

### [26. Single-Frequency and Tunable Lasers]({% link chapters/26_tunable.md %})

*How do two rings select one lasing mode over a 40 nm range?*

26.1 Why single-frequency · 26.2 DFB lasers · 26.3 DBR lasers and tuning · 26.4 External-cavity lasers on Si and SiN · 26.5 The Vernier effect · 26.6 Self-injection locking · 26.7 Multi-wavelength sources

Demos: Vernier ring laser

### [27. Lasers on Silicon]({% link chapters/27_lasersonsi.md %})

*Which integration approach for which volume and performance?*

27.1 Why the light source is the hard part · 27.2 External and flip-chip lasers · 27.3 Heterogeneous integration · 27.4 Micro-transfer printing · 27.5 Monolithic growth · 27.6 Thermal and reliability · 27.7 Open laser-integration projects · 27.8 Directly modulated microring lasers · 27.9 Reliability: how lasers age and fail · 27.10 Isolators and non-reciprocity

Demos: III–V/Si supermodes · Magneto-optic isolator

### [28. Semiconductor Optical Amplifiers]({% link chapters/28_soa.md %})

*How much gain, at what output power and noise figure?*

28.1 From laser to amplifier · 28.2 Gain and saturation · 28.3 Noise figure · 28.4 Dynamics and patterning · 28.5 Polarisation and reflections · 28.6 SOAs in photonic circuits · 28.7 Erbium and other amplifiers

Demos: SOA gain and noise figure

## Part VII · Design, Simulation and Layout

From a specification to a verified layout: design principles, how the simulators work, how to use them, layout in KLayout and GDSII, and the checks before tape-out.

### [29. Design Principles and Simulation Workflows]({% link chapters/29_design.md %})

*How do you get from a system specification to a design that works on most of the dies, with the least simulation?*

29.1 From specification to component targets · 29.2 Architecture and margins · 29.3 Choosing the level of model · 29.4 Simulations are experiments · 29.5 Corners, Monte Carlo and yield · 29.6 Optimisation and inverse design · 29.7 Compact models and their validity · 29.8 Closing the loop with measurement · 29.9 Reproducible simulation · 29.10 Design for manufacturing and for test

### [30. Design Flow and Open PDKs]({% link chapters/30_flow.md %})

*What happens between a simulation and a manufacturable layout?*

30.1 The design flow · 30.2 Process design kits · 30.3 Layout with KLayout and SiEPIC-Tools · 30.4 Layout as code with gdsfactory · 30.5 Component simulation · 30.6 Circuit simulation · 30.7 Verification · 30.8 Tape-out through openEBL

Demos: Circuit simulator

### [31. How Photonic Simulators Work]({% link chapters/31_simulators.md %})

*Which solver, and how fine a grid, gives an answer you can trust in a time you can afford?*

31.1 What every simulator does · 31.2 Mode solvers · 31.3 Eigenmode expansion · 31.4 Beam propagation · 31.5 FDTD: the Yee grid and the leapfrog · 31.6 Stability and numerical dispersion · 31.7 Absorbing boundaries: the perfectly matched layer · 31.8 Sources, monitors and the Fourier transform · 31.9 Materials, meshes and symmetry · 31.10 Convergence and cost · 31.11 2D, 2.5D and frequency-domain solvers · 31.12 Semi-analytic, circuit and multiphysics solvers · 31.13 Choosing a method

Demos: FDTD in the browser

### [32. Simulation Tools in Practice]({% link chapters/32_simtools.md %})

*You need the loss of a 2 µm-radius silicon bend to within 0.01 dB. Which tool, which settings, and how do you know the answer is right?*

32.1 From a solver to a tool · 32.2 Ansys Lumerical · 32.3 Tidy3D · 32.4 Open tools · 32.5 Setting up a run, step by step · 32.6 One problem, three tools: a 2 µm bend · 32.7 Choosing a tool

### [33. Layout with KLayout and GDSII]({% link chapters/33_layout.md %})

*How does a drawing become masks, and what do the file format and its grid do to a curved waveguide?*

33.1 What a layout is for · 33.2 GDSII as data · 33.3 KLayout · 33.4 Layout as code with gdsfactory · 33.5 Curves on a grid · 33.6 Floorplans, routing and labels · 33.7 Hierarchy hygiene and version control

### [34. Verification and Tape-Out]({% link chapters/34_verification.md %})

*How do you know, before the chips come back, that the file you send is the chip you meant?*

34.1 What can go wrong · 34.2 Design rules · 34.3 How a DRC engine works · 34.4 Running DRC in KLayout · 34.5 Curved geometry, grids and waivers · 34.6 Connectivity and layout versus schematic · 34.7 Design-for-test rules · 34.8 Foundry sign-off · 34.9 A pre-fabrication checklist

## Part VIII · Fabrication, Testing and Data Analysis

How photonic chips are made and measured: fabrication and its variations, test setups and data analysis.

### [35. Fabrication]({% link chapters/35_fab.md %})

*How do nanometre variations turn into nanometre wavelength shifts?*

35.1 SOI wafers · 35.2 Lithography · 35.3 Etching and cladding · 35.4 Doping, metals and germanium · 35.5 Other platforms · 35.6 Process variation · 35.7 Design for manufacturing · 35.8 Access

Demos: Wafer-map Monte Carlo

### [36. Testing Photonic Chips]({% link chapters/36_testing.md %})

*How do you trust a measured spectrum?*

36.1 The passive test setup · 36.2 Automated testing and design for test · 36.3 Calibration and de-embedding · 36.4 Testing active devices · 36.5 Testing lasers · 36.6 High-speed testing · 36.7 Wafer-scale testing · 36.8 Testing edge couplers: lensed fibre arrays

Demos: Virtual test bench

### [37. Data Analysis]({% link chapters/37_analysis.md %})

*How do you extract physical parameters, with error bars, from measured spectra?*

37.1 Data formats and open datasets · 37.2 Calibrating out the grating couplers · 37.3 Propagation loss by cutback · 37.4 Group index from interferometers and rings · 37.5 Fitting ring resonances · 37.6 Bragg-grating parameters · 37.7 Statistics across a wafer · 37.8 Back to compact models

Demos: Ring-fit playground

## Part IX · Systems and Applications

Everything together: optical links and transceivers, and the sensing, LiDAR, quantum and computing systems built from the same blocks.

### [38. Optical Links and Transceivers]({% link chapters/38_links.md %})

*Does the reference link close, and what does each block contribute?*

38.1 Link architectures · 38.2 Power budget and penalties · 38.3 WDM transceivers · 38.4 Coherent transceivers · 38.5 Energy per bit · 38.6 Co-packaged optics · 38.7 The reference link, block by block · 38.8 NRZ or PAM4 · 38.9 Drivers and equalisation · 38.10 Clocking, jitter and the timing budget · 38.11 Optimising for energy

Demos: Link budget · Coherent transmission

### [39. Beyond Datacom: Sensing, LiDAR, Quantum and Computing]({% link chapters/39_apps.md %})

*What changes when the chip is a sensor, a beam steerer or a processor instead of a transceiver?*

39.1 Biosensing with evanescent fields · 39.2 LiDAR and optical phased arrays · 39.3 Quantum photonics · 39.4 Photonic computing · 39.5 Microwave photonics and frequency combs · 39.6 Visible and mid-infrared photonics

Demos: Ring biosensor · Optical phased array

## Hands-On Labs

Twelve labs in three tracks, using free tools only: simulate (mode solvers, FDTD, circuit models), make (lay out, verify and submit an openEBL chip, then analyse its measurements), and lasers and links (rate equations, a Vernier laser, the reference-link budget). See [the labs page]({% link labs.md %}).
