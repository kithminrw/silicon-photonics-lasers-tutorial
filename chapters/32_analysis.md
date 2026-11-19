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

The first step is always the same ([Chapter 31]({% link chapters/31_testing.md %})): subtract, in decibels, the loopback measured on the same chip, or a smooth envelope fitted to the device's own spectrum away from its features. A low-order polynomial (in dB against wavelength) fitted to the loopback's peak region works well ([Figure 32.1](#fig-32-1)); outside the couplers' band, where the signal approaches the noise floor, the data are discarded. What remains is the device's response, with residual fringes and noise. Fitting the envelope to the device itself needs care: it must follow only the slow variation, never the features being measured.

<figure id="fig-32-1">
  <img src="{{ '/assets/figs/ch32_calib.svg' | relative_url }}" style="width:600px" alt="(a) Synthetic detected power from 1500 to 1600 nm: the loopback is a smooth arch peaking at minus 8 dBm near 1550 nm, with a dashed third-order fit over 1512 to 1581 nm; the device spectrum follows the same arch with deep MZI fringes about 5.7 nm apart; outside the fit window the regions are shaded and marked discarded. (b) The device minus the fit, plotted only inside the window: fringes peaking near 0 dB and dipping to about minus 28 dB, with peaks drifting from slightly above 0 dB at short wavelengths to about minus 1 dB at long ones.">
  <figcaption><span class="capnum">Figure 32.1.</span> <strong>Calibrating a measured spectrum</strong> (synthetic data). (a) An unbalanced MZI (\(\Delta L\) = 100 µm, as in Chapter 30) between two grating couplers, and the loopback on the same chip, swept with 0 dBm of laser power. A third-order polynomial is fitted to the loopback where it is within 10 dB of its peak (1512–1581 nm); outside, little light passes and the MZI's troughs sink towards the detector floor, so those data are discarded. (b) The device spectrum minus the fit, in dB: the MZI alone, with residual fringes and a tilt of about 1 dB, because the device's couplers here differ slightly from the loopback's (centre 1.5 nm away, 0.15 dB more loss). Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">32.3</span>Propagation loss by cutback

Measure waveguides of several lengths with the same couplers and bends; the insertion loss grows linearly with length, and the slope is the propagation loss ([Chapter 7]({% link chapters/07_loss.md %})). A least-squares fit of loss against length gives the slope with a standard error

$$\sigma_\alpha = \frac{\sigma_y}{\sqrt{\sum_i (L_i - \bar L)^2}},$$

where $$\sigma_y$$ is the scatter of the points about the line, mostly coupler-to-coupler variation. The lever is the spread of lengths: a few centimetres of spiral resolve a few tenths of a dB/cm where a few millimetres cannot. Fitting at each wavelength gives the loss spectrum ([Figure 32.2](#fig-32-2)). The cutback demo of [Chapter 7]({% link chapters/07_loss.md %}) shows the error bar shrinking as the lengths spread.

<figure id="fig-32-2">
  <img src="{{ '/assets/figs/ch32_cutback.svg' | relative_url }}" style="width:600px" alt="(a) Synthetic transmission spectra from 1520 to 1580 nm of four spirals 0.5, 1.5, 2.5 and 3.5 cm long: parabolic grating-coupler envelopes peaking near 1550 nm, about 2 dB apart per centimetre, with small fringes. (b) Loss fitted at each wavelength: for spirals of 0.5 to 3.5 cm a blue line near 2 dB/cm with a narrow error band; for spirals of 1 to 4 mm an amber line wandering between 0 and 2 dB/cm inside a band several dB/cm wide; a dotted line marks the true 2.0 dB/cm.">
  <figcaption><span class="capnum">Figure 32.2.</span> <strong>Cutback, wavelength by wavelength</strong> (synthetic data). (a) Four spirals with the same couplers; each structure's couplers differ a little in loss and centre wavelength (0.3 dB scatter, illustrative). (b) A least-squares fit of loss against length at every wavelength gives the loss spectrum, shown ±1 standard error. With lengths of 0.5–3.5 cm, \(\sum(L_i-\bar L)^2\) = 5 cm² and \(\sigma_\alpha\) ≈ 0.13 dB/cm, so the 2.0 dB/cm loss is resolved; with 1–4 mm it is 0.05 cm², \(\sigma_\alpha\) ≈ 1.3 dB/cm, and the coupler scatter, which varies slowly with wavelength, biases the whole spectrum. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">32.4</span>Group index from interferometers and rings

The fringe spacing of an unbalanced MZI and the free spectral range of a ring both give the group index directly:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Group index from a measured FSR</div>

$$n_g = \frac{\lambda^2}{\mathrm{FSR}\cdot\Delta L}\ \ \text{(MZI)}, \qquad n_g = \frac{\lambda^2}{\mathrm{FSR}\cdot L}\ \ \text{(ring of circumference } L\text{)}$$

</div>

Finding the peaks or troughs automatically, measuring their spacing, and plotting $$n_g$$ against wavelength gives the dispersion too ([Figure 32.3](#fig-32-3)). The measured group index is one of the best checks of the fabricated cross-section, since it depends on the width and thickness ([Chapter 6]({% link chapters/06_soi.md %})). Two MZIs with different $$\Delta L$$ separate the device's arm difference from any imbalance in the couplers.

<figure id="fig-32-3">
  <img src="{{ '/assets/figs/ch32_ng.svg' | relative_url }}" style="width:600px" alt="(a) The calibrated MZI response from 1535 to 1565 nm with five troughs near minus 28 dB marked by open red circles, and an arrow marking the spacing between two troughs as the FSR. (b) Group index against wavelength from 1515 to 1580 nm: points from the measured FSRs scatter between 4.176 and 4.188 around a rising straight femwell line through 4.184 at 1550 nm.">
  <figcaption><span class="capnum">Figure 32.3.</span> <strong>Group index from the fringe spacing</strong> (synthetic data, the calibrated MZI of Figure 32.1). (a) Troughs are found automatically as local minima of the lightly smoothed trace, refined with a parabola. (b) Each pair of neighbouring troughs gives \(n_g = \lambda^2/(\mathrm{FSR}\cdot\Delta L)\): 13 troughs, FSRs of 5.5–5.95 nm, \(n_g\) between 4.176 and 4.188, scattered about the femwell group index of the 500 × 220 nm strip (4.184 at 1550 nm, rising by 0.17 per µm of wavelength). The scatter of a few thousandths comes from locating the troughs; the dispersion is just visible above it. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">32.5</span>Fitting ring resonances

A ring's through-port resonance contains its round-trip loss $$a$$ and its self-coupling $$t$$ ([Chapter 12]({% link chapters/12_rings.md %})). Fitting the all-pass formula, after calibration, extracts them, and from them the propagation loss, the coupling and the Q, from a device a fraction of a millimetre long {% include cite.html keys="shi2012" %}. The fit has a catch: the formula is symmetric in $$a$$ and $$t$$, so every resonance has two equally good solutions, one under-coupled and one over-coupled. Section 12.5 lists the ways to resolve it: a series of rings with different gaps (the coupling changes, the loss does not; [Figure 32.4](#fig-32-4)), an add-drop ring, or the phase response.

**Try it.** Fit a noisy resonance and look at the misfit map: two valleys, mirrored about critical coupling. Add noise and see the valleys broaden.

{% include demos/ringfit.html %}

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 32.1 · Telling the two solutions apart</div>

Suppose three rings of 10 µm radius with gaps of 200, 250 and 300 nm are fitted (illustrative numbers). Each gives two solutions. In one set the losses are 2.1, 1.9 and 2.0 dB/cm and the couplings fall steeply with the gap; in the other the "losses" are 8.6, 3.6 and 1.5 dB/cm and the "couplings" barely change. Loss cannot depend on a coupling gap several micrometres from most of the ring, so the first set is the physical one, here close to the 2 dB/cm and the couplings of [Table 12.1]({% link chapters/12_rings.md %}#tab-12-1).

</div>

<figure id="fig-32-4">
  <img src="{{ '/assets/figs/ch32_ringgap.svg' | relative_url }}" style="width:600px" alt="(a) Synthetic through-port resonances of three 10 micrometre rings over plus and minus 40 pm: the 200 nm gap gives a broad dip to about 0.37, the 250 nm gap a narrower dip to about 0.1, the 300 nm gap the narrowest and deepest dip, near 0.02; noisy points with fitted curves. (b) Fitted loss against gap for the two solutions: solution 1 flat at 2.1, 1.9 and 2.0 dB/cm; solution 2 falling from 8.6 to 3.6 to 1.5 dB/cm. (c) Fitted power coupling against gap: solution 1 falling from 1.24 to 0.52 to 0.22 percent; solution 2 nearly flat near 0.3 percent.">
  <figcaption><span class="capnum">Figure 32.4.</span> <strong>Telling the two solutions apart with a gap series</strong> (Worked Example 32.1, illustrative numbers, synthetic data). (a) Through-port resonances of the three rings with their fits: the 200 nm gap is over-coupled (broad, 4 dB deep), the 300 nm gap slightly under-coupled (narrow, 17 dB deep). Each curve is fitted equally well by \((a, t)\) and by \((t, a)\). (b) The fitted loss: solution 1 stays near 2 dB/cm, solution 2 changes four-fold with the gap. (c) The fitted coupling: solution 1 falls steeply with the gap, from 1.24 to 0.22 %, as a coupler should; solution 2 barely changes. Solution 1 is the physical one. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">32.6</span>Bragg-grating parameters

A Bragg grating's reflection or transmission spectrum gives its centre wavelength, which tracks $$n_\mathrm{eff}$$, and its stop-band width, which gives the coupling coefficient ([Chapter 13]({% link chapters/13_bragg.md %}), [Figure 32.5](#fig-32-5)):

$$\kappa \approx \frac{\pi n_g\,\Delta\lambda}{\lambda^2}\quad (\kappa L \gg 1).$$

Fitting the full transfer-matrix model to the spectrum extracts κ, $$n_\mathrm{eff}$$ and the loss together, and checks the assumption of a uniform grating. A sidewall grating's measured κ is usually smaller than the drawn corrugation predicts, because lithography rounds the small teeth.

<figure id="fig-32-5">
  <img src="{{ '/assets/figs/ch32_bragg.svg' | relative_url }}" style="width:600px" alt="(a) Synthetic reflection spectrum in dB of a uniform Bragg grating from 1530 to 1560 nm: a flat-topped stop band at 0 dB between dotted lines at its first nulls, 7.5 nm apart, with many side lobes falling from minus 10 dB on either side and nulls cut by a noise floor near minus 40 dB. Labels: centre 1547.4 nm gives n_eff = lambda over 2 Lambda = 2.441; kappa approximately pi n_g delta lambda over lambda squared = 41 per mm. (b) The ratio of the simple estimate of kappa to the true kappa against kappa L on a log axis, falling from above 3.5 near kappa L of 0.8 towards 1; marked points: Example 13.2 at kappa L 1.2 with a factor 2.81, and panel a at kappa L 12.7 with 1.03.">
  <figcaption><span class="capnum">Figure 32.5.</span> <strong>Reading κ and \(n_\mathrm{eff}\) from a Bragg spectrum</strong> (synthetic data, illustrative grating: 1000 periods of 317 nm, κ = 40 mm⁻¹, \(n_\mathrm{eff}\) 0.008 below the plain strip's). (a) The first nulls beside the stop band are 7.5 nm apart; their centre, 1547.4 nm, gives \(n_\mathrm{eff} = \lambda/2\Lambda\) = 2.441, and the simple formula with \(n_g\) = 4.18 gives κ ≈ 41 mm⁻¹. (b) The formula overestimates κ by \(\sqrt{1 + (\pi/\kappa L)^2}\), the finite-length factor of Chapter 13: 3 % for this grating (κL = 12.7), but a factor 2.8 for the weak grating of Example 13.2 (κL = 1.2), where \(\kappa = \sqrt{(\pi n_g\Delta\lambda/\lambda^2)^2 - (\pi/L)^2}\) must be used instead. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">32.7</span>Statistics across a wafer

One device is an anecdote; a wafer map is data. Measuring the same structure on every die gives distributions of resonance wavelength, loss, coupling and group index ([Chapter 29]({% link chapters/29_fab.md %})). Their means show the fabrication bias, their spreads the variation, and their spatial patterns the cause. Splitting the variation into wafer-scale and within-die parts tells the designer what tuning must absorb and what matching can achieve ([Figure 32.6](#fig-32-6)). Correlations matter too: if the group index and the resonance shift together, both point to the thickness.

<figure id="fig-32-6">
  <img src="{{ '/assets/figs/ch32_wafer.svg' | relative_url }}" style="width:600px" alt="(a) Synthetic ring-resonance shifts of 113 dies against their distance from the wafer centre, rising from about minus 6 nm at the centre to plus 5 nm at the edge, with a fitted parabolic bowl and a shaded band of plus and minus 1.1 nm around it. (b) Histograms of the shifts about their mean: all variation spreads from minus 6 to plus 6 nm with sigma 2.9 nm; after the bowl is removed the residuals cluster within about plus and minus 2.5 nm with sigma 1.1 nm.">
  <figcaption><span class="capnum">Figure 32.6.</span> <strong>Splitting wafer variation</strong> (synthetic data). Ring resonances on 113 dies of a 200 mm wafer, generated with the variations of Worked Example 29.1 (6 nm of thickness and of width from centre to edge, plus a random width scatter of σ = 1.5 nm) and the sensitivities 0.6 and 1.4 nm per nm. (a) A bowl fitted against the die's radius captures the wafer-scale part, 11.6 nm from centre to edge, which tuning must absorb. (b) What remains, σ = 1.1 nm, is mostly the random width scatter (0.9 nm alone) plus small tilts: the die-to-die part, which matching and tuning margins must cover. Drawn by <code>figsrc/ch32_figs.py</code>.</figcaption>
</figure>

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
