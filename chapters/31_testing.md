---
title: "31. Testing Photonic Chips"
parent: "Part VII · Fabrication, Testing and Data Analysis"
nav_order: 31
permalink: /part-7/ch31/
chapter: 31
---

# <span class="chapnum">Chapter 31</span>Testing Photonic Chips

Measurement closes the loop: a design is only as good as the data that comes back from the chip.
{: .chapterlead }

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- assemble a passive test setup: tunable laser, detectors, polarisation control, fibre array and temperature stage;
- describe automated probe stations and design-for-test rules;
- calibrate and reference measurements;
- test active devices and lasers (IV, LIV, spectra, SMSR, RIN, linewidth);
- measure high-speed behaviour (S-parameters, eye diagrams, BER).

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you trust a measured spectrum?

</div>

## <span class="secnum">31.1</span>The passive test setup

Laser sweeps, detectors, polarisation and temperature.

## <span class="secnum">31.2</span>Automated testing and design for test

Probe stations, test routines and layout rules {% include cite.html keys="siepiclab" %}.

## <span class="secnum">31.3</span>Calibration and de-embedding

Loopbacks and references.

## <span class="secnum">31.4</span>Testing active devices

IV, heaters and modulators at DC.

## <span class="secnum">31.5</span>Testing lasers

LIV, optical spectra, SMSR, RIN and linewidth.

## <span class="secnum">31.6</span>High-speed testing

S-parameters, eye diagrams and BER.

## <span class="secnum">31.7</span>Wafer-scale testing

Statistics across dies and wafers.

## Interactive demos

- **Virtual test bench**: sweep a tunable laser through a grating coupler and ring, with noise, fringes and polarisation drift. *(planned)*

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter (they open on their authors' sites):

- [VM-Lab game: Illuminator (build a sensing circuit)](https://s3.amazonaws.com/vmlab-app-2/Main/index.html)

</div>

## Reading

{% include reflist.html keys="siepiclab,openebl,phot1x" %}
