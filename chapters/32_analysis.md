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

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- remove the grating-coupler envelope from measured spectra;
- extract propagation loss from cutback data with uncertainties;
- extract the group index from interferometers and rings;
- fit ring resonances and Bragg gratings, and recognise when a fit is ambiguous;
- analyse variability across a wafer and feed it back into compact models.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you extract physical parameters, with error bars, from measured spectra?

</div>

## <span class="secnum">32.1</span>Data formats and open datasets

A passive measurement is a table of wavelength against detected power, usually in dBm, for each detector channel and each structure, with metadata: the structure's label and position, the laser power, the temperature, the polarisation. The openEBL runs return their data this way, as files in the run's repository, alongside the layouts that produced them {% include cite.html keys="openebl" %}. Because the designs are open too, anyone can compare measurement with intent: the most useful dataset there is for learning analysis. The UBC ELEC 413 repositories add laser data ([Chapter 27]({% link chapters/27_lasersonsi.md %})).

## <span class="secnum">32.2</span>Calibrating out the grating couplers

The first step is always the same ([Chapter 31]({% link chapters/31_testing.md %})): subtract, in decibels, the loopback measured on the same chip, or a smooth envelope fitted to the device's own spectrum away from its features. A low-order polynomial (in dB against wavelength) fitted to the loopback's peak region works well; outside the couplers' band, where the signal approaches the noise floor, the data are discarded. What remains is the device's response, with residual fringes and noise. Fitting the envelope to the device itself needs care: it must follow only the slow variation, never the features being measured.

## <span class="secnum">32.3</span>Propagation loss by cutback

Measure waveguides of several lengths with the same couplers and bends; the insertion loss grows linearly with length, and the slope is the propagation loss ([Chapter 7]({% link chapters/07_loss.md %})). A least-squares fit of loss against length gives the slope with a standard error

$$\sigma_\alpha = \frac{\sigma_y}{\sqrt{\sum_i (L_i - \bar L)^2}},$$

where $$\sigma_y$$ is the scatter of the points about the line, mostly coupler-to-coupler variation. The lever is the spread of lengths: a few centimetres of spiral resolve a few tenths of a dB/cm where a few millimetres cannot. Fitting at each wavelength gives the loss spectrum. The cutback demo of [Chapter 7]({% link chapters/07_loss.md %}) shows the error bar shrinking as the lengths spread.

## <span class="secnum">32.4</span>Group index from interferometers and rings

The fringe spacing of an unbalanced MZI and the free spectral range of a ring both give the group index directly:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Group index from a measured FSR</div>

$$n_g = \frac{\lambda^2}{\mathrm{FSR}\cdot\Delta L}\ \ \text{(MZI)}, \qquad n_g = \frac{\lambda^2}{\mathrm{FSR}\cdot L}\ \ \text{(ring of circumference } L\text{)}$$

</div>

Finding the peaks or troughs automatically, measuring their spacing, and plotting $$n_g$$ against wavelength gives the dispersion too. The measured group index is one of the best checks of the fabricated cross-section, since it depends on the width and thickness ([Chapter 6]({% link chapters/06_soi.md %})). Two MZIs with different $$\Delta L$$ separate the device's arm difference from any imbalance in the couplers.

## <span class="secnum">32.5</span>Fitting ring resonances

A ring's through-port resonance contains its round-trip loss $$a$$ and its self-coupling $$t$$ ([Chapter 12]({% link chapters/12_rings.md %})). Fitting the all-pass formula, after calibration, extracts them, and from them the propagation loss, the coupling and the Q, from a device a fraction of a millimetre long {% include cite.html keys="shi2012" %}. The fit has a catch: the formula is symmetric in $$a$$ and $$t$$, so every resonance has two equally good solutions, one under-coupled and one over-coupled. Section 12.5 lists the ways to resolve it: a series of rings with different gaps (the coupling changes, the loss does not), an add-drop ring, or the phase response.

**Try it.** Fit a noisy resonance and look at the misfit map: two valleys, mirrored about critical coupling. Add noise and see the valleys broaden.

{% include demos/ringfit.html %}

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.1 · Telling the two solutions apart</div>

Suppose three rings of 10 µm radius with gaps of 200, 250 and 300 nm are fitted (illustrative numbers). Each gives two solutions. In one set the losses are 2.1, 1.9 and 2.0 dB/cm and the couplings fall steeply with the gap; in the other the "losses" are 8.6, 3.6 and 1.5 dB/cm and the "couplings" barely change. Loss cannot depend on a coupling gap several micrometres from most of the ring, so the first set is the physical one, here close to the 2 dB/cm and the couplings of [Table 12.1]({% link chapters/12_rings.md %}#tab-12-1).

</div>

## <span class="secnum">32.6</span>Bragg-grating parameters

A Bragg grating's reflection or transmission spectrum gives its centre wavelength, which tracks $$n_\mathrm{eff}$$, and its stop-band width, which gives the coupling coefficient ([Chapter 13]({% link chapters/13_bragg.md %})):

$$\kappa \approx \frac{\pi n_g\,\Delta\lambda}{\lambda^2}\quad (\kappa L \gg 1).$$

Fitting the full transfer-matrix model to the spectrum extracts κ, $$n_\mathrm{eff}$$ and the loss together, and checks the assumption of a uniform grating. A sidewall grating's measured κ is usually smaller than the drawn corrugation predicts, because lithography rounds the small teeth.

## <span class="secnum">32.7</span>Statistics across a wafer

One device is an anecdote; a wafer map is data. Measuring the same structure on every die gives distributions of resonance wavelength, loss, coupling and group index ([Chapter 29]({% link chapters/29_fab.md %})). Their means show the fabrication bias, their spreads the variation, and their spatial patterns the cause. Splitting the variation into wafer-scale and within-die parts tells the designer what tuning must absorb and what matching can achieve. Correlations matter too: if the group index and the resonance shift together, both point to the thickness.

## <span class="secnum">32.8</span>Back to compact models

The final step closes the loop of [Chapter 30]({% link chapters/30_flow.md %}). The measured effective and group indices, losses and coupling against gap are fitted into compact models with their variation (means, spreads, corners), which the next design uses. The extracted width bias goes into the layout itself, as a corrected drawing. Each tape-out makes the models better, and the next design more likely to work first time.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

From one openEBL chip: the coupler envelope from the loopback; the propagation loss from the cutback spirals; the group index from the MZIs' fringes and the rings' FSRs; the loss and coupling of each ring gap, resolved by the gap series; the Bragg grating's κ. Then compare each with the femwell numbers of [Chapter 6]({% link chapters/06_soi.md %}) and the models of Chapters 9–13.

</div>

## Reading

{% include reflist.html keys="phot1x,chrostowski2015,shi2012,openebl" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Calibrate first: subtract the loopback or a fitted envelope; drop data near the noise floor.
- Cutback: loss is the slope of insertion loss against length; its error bar shrinks with the spread of lengths.
- $$n_g = \lambda^2/(\mathrm{FSR}\cdot L)$$ from rings and MZIs checks the fabricated cross-section.
- Ring fits give loss and coupling but have two mirror solutions; a gap series resolves them.
- Wafer statistics separate bias, wafer-scale and within-die variation; the results become the next design's compact models.

</div>
