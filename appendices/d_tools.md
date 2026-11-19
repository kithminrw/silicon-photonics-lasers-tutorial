---
title: "D. Open Tools, PDKs and Data"
parent: Appendices
nav_order: 4
permalink: /appendices/d/
---

# Appendix D. Open Tools, PDKs and Data

Everything the labs use is free; this is where to find it.
{: .chapterlead }

## Open process design kits

**Table D.1. Open photonic PDKs.** Licences as stated in each repository (November 2026).
{: .tabcaption #tab-d-1 }

| PDK | Platform | Licence | Where |
|---|---|---|---|
| SiEPIC EBeam PDK | 220 nm SOI (and SiN), electron-beam lithography; used by openEBL and the edX course | MIT | [SiEPIC/SiEPIC_EBeam_PDK](https://github.com/SiEPIC/SiEPIC_EBeam_PDK) |
| ubcpdk | the SiEPIC EBeam PDK for gdsfactory | MIT | [gdsfactory/ubc](https://github.com/gdsfactory/ubc) |
| SiEPICfab Shuksan PDK | laser-integration MPW run (SiEPICfab) | MIT | [SiEPIC/SiEPICfab_Shuksan_PDK](https://github.com/SiEPIC/SiEPICfab_Shuksan_PDK) |
| cspdk | CORNERSTONE: 220 and 340 nm SOI, SiN, Ge-on-Si, suspended Si | MIT | [gdsfactory/cspdk](https://github.com/gdsfactory/cspdk) |
| gvtt | VTT 3 µm thick SOI | MIT | [gdsfactory/vtt](https://github.com/gdsfactory/vtt) |
| lnoi400 / ltoi300 | Luxtelligence thin-film lithium niobate and tantalate | MIT | [Luxtelligence/lxt_pdk_gf](https://github.com/Luxtelligence/lxt_pdk_gf) |
| sky130ph | a photonics experiment on SkyWater 130 nm (archived) | MIT | [gdsfactory/sky130ph](https://github.com/gdsfactory/sky130ph) |

Commercial foundry PDKs (AMF, AIM, imec, GlobalFoundries, Tower and OpenLight, among others) are available under licence from the foundries and are not reproduced here.

## Layout and verification

- [KLayout](https://www.klayout.de): layout viewer and editor, with Python scripting.
- [SiEPIC-Tools](https://github.com/SiEPIC/SiEPIC-Tools): waveguide routing, netlist extraction, verification and circuit simulation for KLayout (MIT).
- [gdsfactory](https://github.com/gdsfactory/gdsfactory): layout as Python code, with PDK plug-ins (MIT).

## Simulation

- Mode solvers: [femwell](https://github.com/HelgeGehring/femwell) (finite elements), [MPB](https://github.com/NanoComp/mpb) (band structures and modes), [meow](https://github.com/gdsfactory/meow) (eigenmode expansion).
- FDTD: [MEEP](https://github.com/NanoComp/meep) {% include cite.html keys="meep" %}.
- Circuits: [SAX](https://github.com/flaport/sax) {% include cite.html keys="sax" %}, [opics](https://github.com/SiEPIC/opics).
- Gratings and filters: [contraDC](https://github.com/SiEPIC/contraDC) (contra-directional couplers), [legume](https://github.com/fancompute/legume) (photonic-crystal slabs).

## Test and data

- [SiEPIClab](https://github.com/SiEPIC/SiEPIClab): control software for automated probe stations {% include cite.html keys="siepiclab" %}.
- openEBL repositories: each run's GitHub repository holds the submitted designs and, after testing, a link in its README to the measurement data on a UBC file share. For example [openEBL-2024-05](https://github.com/SiEPIC/openEBL-2024-05) and [openEBL-2024-10-SiN](https://github.com/SiEPIC/openEBL-2024-10-SiN) (MIT).
- UBC ELEC 413 semiconductor-laser course designs and data: [UBC-ELEC413-2025Fall](https://github.com/SiEPIC/UBC-ELEC413-2025Fall) (MIT).

## This tutorial's own code

- `tools/export_3d.py` exports the [3D gallery]({% link devices-3d.md %}) models from the open PDKs.
- The interactive demos are plain JavaScript in `_includes/demos/` with the shared helpers in `assets/js/demos.js` (MIT).
