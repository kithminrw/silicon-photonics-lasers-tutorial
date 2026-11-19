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

Learning by doing, with free tools only: simulate the devices, lay out and submit a chip, and analyse real measurements.
{: .part-blurb }

<p>The labs are designed and listed below. Each written lab has its own page and a script you can download from it, also in the repository's <a href="https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs"><code>labs/</code></a> folder; the others follow.</p>

The twelve labs follow three tracks. **Simulate** (Labs 1–6): mode solvers, coupled-mode and FDTD simulations, circuit models and grating couplers. **Make** (Labs 7–9): lay out a passive chip in the SiEPIC EBeam PDK, verify and submit it to an openEBL run, and analyse the measured data that comes back. **Lasers and links** (Labs 10–12): rate-equation models, a Vernier tunable laser and the budget of the reference link. Every tool is free and open source; the interactive demos in the chapters are a quick way to explore the same models before running a lab.

**Table L.1. The labs.** Each lab lists the chapters it supports.
{: .tabcaption #tab-l-1 }

| Lab | Title | Chapters | Tools and what you do |
|---|---|---|---|
| 1 | [Slab and channel waveguide modes in Python]({% link labs/lab01_slab.md %}) | 5–6 | NumPy: the slab solver of Chapter 5, then the effective-index method against femwell |
| 2 | Mode solving with femwell | 6–7 | femwell (FEM, open source): n_eff, n_g and loss against width |
| 3 | [Directional coupler and MMI design]({% link labs/lab03_couplers.md %}) | 9–10 | NumPy: a finite-difference mode solver for supermodes and beat length, and eigenmode expansion for MMI self-imaging |
| 4 | MZI and ring circuits with S-parameters | 11–12 | SAX: compact models and spectra |
| 5 | [Bragg gratings with transfer matrices]({% link labs/lab05_bragg.md %}) | 13 | NumPy: transfer matrices, apodisation, phase-shifted cavities |
| 6 | A grating coupler in 2D FDTD | 15 | MEEP: efficiency and bandwidth against period and etch depth |
| 7 | Lay out your first chip | 30 | KLayout with SiEPIC-Tools and the SiEPIC EBeam PDK, or gdsfactory with ubcpdk |
| 8 | Verify and submit to openEBL | 30 | GitHub-based submission with automatic verification |
| 9 | Analyse measured openEBL data | 32 | Python: loss, group index and Q from open measurement data |
| 10 | [Laser rate equations]({% link labs/lab10_rate_equations.md %}) | 24–25 | NumPy: L–I, turn-on transients, modulation response, temperature, linewidth |
| 11 | [Design a Vernier tunable laser]({% link labs/lab11_vernier.md %}) | 26 | NumPy: two ring filters, gain, mode selection and the tuning map |
| 12 | [Close the reference link budget]({% link labs/lab12_link.md %}) | 33 | NumPy: power budget, sensitivity and BER, crosstalk and dispersion penalties, energy per bit |
{: .lab-table }

## The openEBL cycle

Labs 7–9 follow the SiEPIC openEBL workflow {% include cite.html keys="openebl" %}: designs in the SiEPIC EBeam PDK are submitted through a GitHub repository, checked automatically, fabricated by electron-beam lithography, measured on an automated probe station, and the data are published back to the repository. The edX course *Silicon Photonics Design, Fabrication and Data Analysis* follows the same cycle {% include cite.html keys="phot1x" %}. [Chapter 30]({% link chapters/30_flow.md %}) covers the design flow and [Chapter 32]({% link chapters/32_analysis.md %}) the analysis.

## What you need

- Python 3.11 or newer with NumPy and Matplotlib for Labs 1, 3, 5 and 9–12.
- [femwell](https://github.com/HelgeGehring/femwell), [MEEP](https://github.com/NanoComp/meep) and [SAX](https://github.com/flaport/sax) for Labs 2–4 and 6.
- [KLayout](https://www.klayout.de) with [SiEPIC-Tools](https://github.com/SiEPIC/SiEPIC-Tools) and the [SiEPIC EBeam PDK](https://github.com/SiEPIC/SiEPIC_EBeam_PDK), or [gdsfactory](https://github.com/gdsfactory/gdsfactory) with [ubcpdk](https://github.com/gdsfactory/ubc), for Labs 7–8.

[Appendix D]({% link appendices/d_tools.md %}) lists these and other open tools.

## Reading

{% include reflist.html keys="phot1x,gdsfactory,meep,sax,openebl" %}
