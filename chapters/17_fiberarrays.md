---
title: "17. Fibre Arrays, Photonic Wire Bonds and Packaging"
parent: "Part IV · Coupling and Packaging"
nav_order: 17
permalink: /part-4/ch17/
chapter: 17
---

# <span class="chapnum">Chapter 17</span>Fibre Arrays, Photonic Wire Bonds and Packaging

Much of a photonic chip's cost is in getting light in and out reliably; this chapter is about the hardware that does it.
{: .chapterlead }

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe fibre arrays: V-grooves, 127 and 250 µm pitch, polish angle, PM fibres;
- lay out couplers for a fibre array (pitch, loopbacks, test labels);
- derive alignment tolerances from Gaussian overlap and compare search algorithms;
- describe fibre attach, photonic wire bonds and 3D-printed micro-optics;
- outline laser attach, co-packaged optics and design-for-packaging rules.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How tolerant is a coupling interface, and how do you find the peak quickly?

</div>

## <span class="secnum">17.1</span>Fibre arrays

Construction, pitch, angle, PM fibres and loopbacks.

## <span class="secnum">17.2</span>Alignment

Tolerances from Gaussian overlap; spiral, gradient and hill-climbing searches; aligning many ports at once.

**Try it.** Fibre-array alignment: find the coupling peak with as few moves as possible, then read the 1 dB tolerance.

{% include demos/align.html %}

## <span class="secnum">17.3</span>Attaching fibres

UV epoxy, shrinkage shift and reliability.

## <span class="secnum">17.4</span>Photonic wire bonds and micro-optics

3D-printed polymer waveguides and lenses {% include cite.html keys="lindenmann2012" %}.

## <span class="secnum">17.5</span>Laser and chip assembly

Flip-chip, micro-optics and wafer-level packaging.

## <span class="secnum">17.6</span>Co-packaged optics

From pluggable modules to optics beside the switch chip.

## <span class="secnum">17.7</span>Design rules for test and packaging

Design-for-test rules of the SiEPIC openEBL flow, packaging templates.

## Interactive demos

- **Fibre-array alignment**: find the coupling peak with as few moves as possible, then read the 1 dB tolerance. *(built, shown above)*

## Reading

{% include reflist.html keys="lindenmann2012,chrostowski2015,openebl" %}
