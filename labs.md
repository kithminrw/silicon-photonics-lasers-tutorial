---
title: Hands-On Labs
layout: default
nav_order: 10.5
has_children: true
has_toc: false
permalink: /labs/
---

Labs
{: .part-label }

# Hands-On Labs
{: .part-title }

Learning by doing, with free tools only: simulate the devices, lay out and submit a chip, and analyse openEBL-style measurements.
{: .part-blurb }

<p>The labs are designed and listed below. Each lab has its own page and a script you can download from it.</p>

The seventeen labs follow three tracks. **Simulate** (Labs 1–6): mode solvers, coupled-mode and FDTD simulations, circuit models and grating couplers. **Make** (Labs 7–9): lay out a passive chip in the SiEPIC EBeam PDK, verify and submit it to an openEBL run, and analyse the measured data that comes back. **Lasers and links** (Labs 10–12): rate-equation models, a Vernier tunable laser and the budget of the reference link. Labs 13–17 cross the tracks: the Fabry–Pérot cavity measured through its fringes, coupling light into chips, the heat that limits a laser, driving a ring modulator, and an optical amplifier's gain, saturation and noise. Every tool is free and open source; the interactive demos in the chapters are a quick way to explore the same models before running a lab.

**Table L.1. The labs.** Each lab lists the chapters it supports.
{: .tabcaption #tab-l-1 }

| Lab | Title | Chapters | Tools and what you do |
|---|---|---|---|
| 1 | [Slab and channel waveguide modes in Python]({% link labs/lab01_slab.md %}) | 5–6 | NumPy: the slab solver of Chapter 5, then the effective-index method against femwell |
| 2 | [Mode solving with femwell]({% link labs/lab02_femwell.md %}) | 6–7 | femwell: n_eff, n_g and TE fraction of strips and ribs, width sweeps, substrate leakage through the BOX |
| 3 | [Directional coupler and MMI design]({% link labs/lab03_couplers.md %}) | 9–10 | NumPy: a finite-difference mode solver for supermodes and beat length, and eigenmode expansion for MMI self-imaging |
| 4 | [MZI and ring circuits with S-parameters]({% link labs/lab04_sax.md %}) | 11–12 | SAX (with a NumPy fallback): compact models, MZI, all-pass and add-drop rings, a lattice filter |
| 5 | [Bragg gratings with transfer matrices]({% link labs/lab05_bragg.md %}) | 13 | NumPy: transfer matrices, apodisation, phase-shifted cavities |
| 6 | [A grating coupler in 2D FDTD]({% link labs/lab06_gc_meep.md %}) | 15 | MEEP: efficiency, bandwidth and directionality, phase matching against period and angle, BOX thickness |
| 7 | [Lay out your first chip]({% link labs/lab07_layout.md %}) | 30, 33 | gdsfactory with ubcpdk (the SiEPIC EBeam PDK); view in KLayout |
| 8 | [Verify and submit to openEBL]({% link labs/lab08_submit.md %}) | 30, 34 | Pre-flight checks in Python and SiEPIC-Tools verification; the GitHub submission |
| 9 | [Analyse measured openEBL data]({% link labs/lab09_analysis.md %}) | 37 | NumPy: coupler envelope, group index, ring fits and the coupling ambiguity, cutback loss |
| 10 | [Laser rate equations]({% link labs/lab10_rate_equations.md %}) | 24–25 | NumPy: L–I, turn-on transients, modulation response, temperature, linewidth |
| 11 | [Design a Vernier tunable laser]({% link labs/lab11_vernier.md %}) | 26 | NumPy: two ring filters, gain, mode selection and the tuning map |
| 12 | [Close the reference link budget]({% link labs/lab12_link.md %}) | 38 | NumPy: power budget, sensitivity and BER, crosstalk and dispersion penalties, energy per bit |
| 13 | [Fabry–Pérot cavities]({% link labs/lab13_fp.md %}) | 13, 24 | NumPy: Airy spectra, a Bragg-mirror cavity by transfer matrices, loss and gain from measured fringes |
| 14 | [Coupling light into chips]({% link labs/lab14_coupling.md %}) | 17, 36 | NumPy: overlaps on a grid, test-interface tolerances, ray tracing a printed lens, fibre-array Monte Carlo |
| 15 | [Self-heating and roll-over]({% link labs/lab15_heating.md %}) | 24, 27 | NumPy: self-consistent temperature, L–I roll-over, heat-sink temperature and thermal shunts |
| 16 | [Driving a ring modulator]({% link labs/lab16_ringmod.md %}) | 12, 20 | NumPy: operating point, bandwidth against detuning, NRZ eyes from coupled-mode theory, PAM4 pre-distortion |
| 17 | [SOA gain, saturation and noise]({% link labs/lab17_soa.md %}) | 24, 28 | NumPy: saturating gain along the amplifier, noise figure and ASE, patterning, a large-mode SOA |
{: .lab-table }

## The openEBL cycle

Labs 7–9 follow the SiEPIC openEBL workflow {% include cite.html keys="openebl" %}: designs in the SiEPIC EBeam PDK are submitted through a GitHub repository, checked automatically, fabricated by electron-beam lithography, measured on an automated probe station, and the data are shared through a link in the run's repository. The edX course *Silicon Photonics Design, Fabrication and Data Analysis* follows the same cycle {% include cite.html keys="phot1x" %}. [Chapter 30]({% link chapters/30_flow.md %}) covers the design flow and [Chapter 37]({% link chapters/37_analysis.md %}) the analysis.

## What you need

- Python 3.11 or newer with NumPy and Matplotlib for Labs 1, 3, 5 and 9–15.
- [femwell](https://github.com/HelgeGehring/femwell) for Lab 2, [SAX](https://github.com/flaport/sax) for Lab 4 and [MEEP](https://github.com/NanoComp/meep) for Lab 6 (MEEP runs on Linux and macOS, or on Windows through WSL or Docker).
- [KLayout](https://www.klayout.de) with [SiEPIC-Tools](https://github.com/SiEPIC/SiEPIC-Tools) and the [SiEPIC EBeam PDK](https://github.com/SiEPIC/SiEPIC_EBeam_PDK), or [gdsfactory](https://github.com/gdsfactory/gdsfactory) with [ubcpdk](https://github.com/gdsfactory/ubc), for Labs 7–8.

[Appendix D]({% link appendices/d_tools.md %}) lists these and other open tools.

## Reading

{% include reflist.html keys="phot1x,gdsfactory,meep,sax,openebl" %}
