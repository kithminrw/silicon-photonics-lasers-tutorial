---
title: "33. Hands-On Labs"
parent: "Part VII · Fabrication, Testing and Data Analysis"
nav_order: 33
permalink: /part-7/ch33/
chapter: 33
---

# <span class="chapnum">Chapter 33</span>Hands-On Labs

Learning by doing, with free tools only.
{: .chapterlead }

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

The labs use free, open-source tools only. Each lists the chapters it supports; the scripts will live in [`labs/`](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs).

**Table 33.1. The labs.**
{: .tabcaption #tab-33-1 }

| Lab | Title | Chapters | Tools and what you do |
|---|---|---|---|
| 1 | Slab and channel waveguide modes in Python | 5–6 | NumPy/SciPy; the slab solver of Chapter 5, then the effective-index method |
| 2 | Mode solving with femwell | 6–7 | femwell (FEM, open source): n_eff, n_g and loss against width |
| 3 | Directional coupler and MMI design | 9–10 | MEEP (FDTD) or an EME solver; supermodes, beat length, self-imaging |
| 4 | MZI and ring circuits with S-parameters | 11–12 | SAX: compact models and spectra |
| 5 | Bragg gratings with transfer matrices | 13 | Python: apodisation, phase-shifted cavities |
| 6 | A grating coupler in 2D FDTD | 15 | MEEP: efficiency and bandwidth against period and etch depth |
| 7 | Lay out your first chip | 30 | KLayout with SiEPIC-Tools and the SiEPIC EBeam PDK, or gdsfactory with ubcpdk |
| 8 | Verify and submit to openEBL | 30 | GitHub-based submission with automatic verification |
| 9 | Analyse measured openEBL data | 32 | Python: loss, group index and Q from open measurement data |
| 10 | Laser rate equations | 24–25 | Python: L–I, turn-on transients, modulation response, RIN |
| 11 | Design a Vernier tunable laser | 26 | Python: two ring filters, gain and tuning map |
| 12 | Close the reference link budget | 34 | Python: power budget and BER of the four-wavelength link |
{: .lab-table }

Labs 7–9 follow the SiEPIC openEBL workflow {% include cite.html keys="openebl" %}: designs in the SiEPIC EBeam PDK are submitted through a GitHub repository, fabricated by electron-beam lithography, measured on an automated probe station, and the data are published back to the repository. The edX course *Silicon Photonics Design, Fabrication and Data Analysis* follows the same cycle {% include cite.html keys="phot1x" %}.

## Reading

{% include reflist.html keys="phot1x,gdsfactory,meep,sax,openebl" %}
