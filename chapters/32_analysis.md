---
title: "32. Data Analysis"
parent: "Part VII · Fabrication, Testing and Data Analysis"
nav_order: 32
permalink: /part-7/ch32/
chapter: 32
---

# <span class="chapnum">Chapter 32</span>Data Analysis

Turning raw spectra into numbers you can trust: loss, group index, Q and coupling, with their statistics.
{: .chapterlead }

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- remove the grating-coupler envelope from measured spectra;
- extract propagation loss from cutback data with uncertainties;
- extract the group index from interferometers and rings;
- fit ring resonances and Bragg gratings;
- analyse variability across a wafer and feed it back into compact models.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you extract physical parameters, with error bars, from measured spectra?

</div>

## <span class="secnum">32.1</span>Data formats and open datasets

Measurement files from openEBL runs.

## <span class="secnum">32.2</span>Calibrating out the grating couplers

Baselines and envelopes.

## <span class="secnum">32.3</span>Propagation loss by cutback

Linear fits and their uncertainty.

## <span class="secnum">32.4</span>Group index from interferometers and rings

FSR and peak finding.

## <span class="secnum">32.5</span>Fitting ring resonances

All-pass and add-drop fits; resolving t and a {% include cite.html keys="shi2012" %}.

## <span class="secnum">32.6</span>Bragg-grating parameters

κ from the bandwidth.

## <span class="secnum">32.7</span>Statistics across a wafer

Distributions and corners.

## <span class="secnum">32.8</span>Back to compact models

Closing the design loop.

## Interactive demos

- **Ring-fit playground**: fit a noisy resonance and see how the uncertainty in t and a depends on the noise. *(planned)*
- **Cutback fit**: fit loss from noisy data and watch the error bar shrink. *(planned)*

## Reading

{% include reflist.html keys="phot1x,chrostowski2015,shi2012,openebl" %}
