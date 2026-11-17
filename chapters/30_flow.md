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

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe the photonic design flow from concept to tape-out;
- explain what a PDK contains: layers, cells, compact models and rules;
- lay out with KLayout and SiEPIC-Tools, or as code with gdsfactory;
- choose a component solver (FDE, EME, FDTD) and simulate circuits with S-parameters;
- verify and submit a design to an openEBL run.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What happens between a simulation and a manufacturable layout?

</div>

## <span class="secnum">30.1</span>The design flow

Concept, component simulation, compact models, circuit simulation, layout, verification, tape-out.

## <span class="secnum">30.2</span>Process design kits

Layers, PCells, compact models, design rules; the open PDKs in this tutorial and the [3D gallery]({% link devices-3d.md %}).

## <span class="secnum">30.3</span>Layout with KLayout and SiEPIC-Tools

Interactive layout with waveguide routing and netlist extraction.

## <span class="secnum">30.4</span>Layout as code with gdsfactory

Python and YAML layouts, PDK plug-ins.

## <span class="secnum">30.5</span>Component simulation

Mode solvers, eigenmode expansion and FDTD (MEEP).

## <span class="secnum">30.6</span>Circuit simulation

S-parameters, SAX and compact models.

## <span class="secnum">30.7</span>Verification

DRC, connectivity and design-for-test checks.

## <span class="secnum">30.8</span>Tape-out through openEBL

Submitting through GitHub and getting data back.

## Interactive demos

- **S-matrix circuit simulator**: chain couplers and waveguides in the browser and see the spectrum. *(planned)*

## Reading

{% include reflist.html keys="gdsfactory,siepictools,ebeampdk,ubcpdk,cspdk,sax,meep,klayout,openebl" %}
