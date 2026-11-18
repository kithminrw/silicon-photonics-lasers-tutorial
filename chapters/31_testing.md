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

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- assemble a passive test setup: tunable laser, detectors, polarisation control, fibre array and temperature stage;
- describe automated probe stations and design-for-test rules;
- calibrate and reference measurements;
- test active devices and lasers (IV, LIV, spectra, SMSR, RIN, linewidth);
- measure high-speed behaviour (S-parameters, eye diagrams, BER) and run wafer-scale tests.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you trust a measured spectrum?

</div>

## <span class="secnum">31.1</span>The passive test setup

A passive photonic chip is characterised by its transmission spectrum. The standard setup has five parts:

- a **tunable laser** that sweeps across the band (for example 1500–1600 nm) in fine steps, a picometre or less, with its wavelength measured or triggered;
- **polarisation control**: a paddle or electronic polarisation controller, or polarisation-maintaining fibre, to put the light in the TE (or TM) mode the grating couplers accept ([Chapter 15]({% link chapters/15_gc.md %}));
- **fibre coupling** to the chip: a fibre array over the grating couplers, or lensed fibres at the edge couplers, on motorised stages ([Chapter 17]({% link chapters/17_fiberarrays.md %}));
- **detectors**: power meters or photodiodes synchronised with the sweep, with a dynamic range of 60 dB or more;
- a **temperature-controlled stage**, because a silicon ring drifts by 75 pm/K ([Chapter 18]({% link chapters/18_thermal.md %})) and a measurement without it drifts with the room.

## <span class="secnum">31.2</span>Automated testing and design for test

A chip with dozens of test structures, or a wafer with hundreds of dies, is measured by an automated probe station. It moves the fibre array from one structure to the next using the layout coordinates, aligns to each automatically (a search for first light, then optimisation, as in [Chapter 17]({% link chapters/17_fiberarrays.md %})), runs the sweep the structure's label asks for, and stores the result. The SiEPIC program publishes its probe-station software, SiEPIClab {% include cite.html keys="siepiclab" %}. Automation only works if the layout follows **design-for-test** rules: couplers on the array pitch in a fixed orientation, machine-readable labels, alignment loopbacks, and electrical pads on a probe-card grid ([Chapter 30]({% link chapters/30_flow.md %})).

## <span class="secnum">31.3</span>Calibration and de-embedding

What the detector sees is the device's response multiplied by everything else on the path: the laser's power against wavelength, the fibres and connectors, and above all the two grating couplers, each of which loses a few decibels and has a 30–40 nm wide passband ([Chapter 15]({% link chapters/15_gc.md %})). Removing those is **de-embedding**:

- normalise to the laser's own output (a reference detector);
- measure a **loopback** (two couplers joined by a short waveguide) on the same chip, and divide the device's spectrum by it;
- or fit a smooth envelope to the device's own off-resonance spectrum.

The loopback assumes that its couplers equal the device's. Fabrication variation and slightly different fibre positions make that approximate, a source of a few tenths of a decibel of error in absolute loss. Relative measurements, such as resonance shapes and wavelengths and the slope of a cutback, are far more robust than absolute ones.

**Try it.** Sweep the virtual laser through a ring between two grating couplers; change the polarisation, the coupler reflections and the averaging, and switch to the loopback-calibrated view.

{% include demos/testbench.html %}

Three artefacts appear in real data and in the demo: **fringes** from reflections between the couplers ([Chapter 15]({% link chapters/15_gc.md %})), which can be mistaken for weak resonances; a **polarisation** error, which lowers the whole spectrum and can add a TM resonance series; and **noise** near the band edges, where little light gets through.

## <span class="secnum">31.4</span>Testing active devices

Active devices add electrical probes, a needle or a probe card on the pads:

- **Heaters**: the IV curve gives the resistance; the resonance shift against power gives the tuning efficiency and $$P_\pi$$ ([Chapter 18]({% link chapters/18_thermal.md %})).
- **Modulators and junctions**: the IV curve checks the diode; spectra at several reverse biases give the resonance shift or phase per volt, hence $$V_\pi L$$ and the loss against bias ([Chapter 19]({% link chapters/19_eo.md %})).
- **Photodiodes**: dark current against bias, and photocurrent against known input power, give the responsivity ([Chapter 21]({% link chapters/21_pd.md %})).

## <span class="secnum">31.5</span>Testing lasers

A laser's characterisation starts with the **LIV** sweep, output power and voltage against current, which gives the threshold, slope efficiency, series resistance and roll-over ([Chapter 24]({% link chapters/24_fp.md %})), at several temperatures for $$T_0$$. An optical spectrum analyser measures the spectrum and the **side-mode suppression ratio** ([Chapter 26]({% link chapters/26_tunable.md %})). An electrical spectrum analyser on a fast photodiode measures **RIN**, and a delayed self-heterodyne interferometer, or a beat note against a reference laser, the **linewidth** ([Chapter 25]({% link chapters/25_dynamics.md %})). Optical isolation between the laser and the measurement is essential, or the instrument's own reflections disturb what it measures.

## <span class="secnum">31.6</span>High-speed testing

Modulators and photodiodes are characterised in the frequency domain with a lightwave component analyser, a vector network analyser with a calibrated optical transmitter and receiver, which gives the electro-optic or opto-electronic **S-parameters** and the 3 dB bandwidth. In the time domain, a pattern generator drives the modulator and a sampling oscilloscope records the **eye diagram** ([Chapter 20]({% link chapters/20_modulators.md %})); an error detector counts errors to measure the **bit-error ratio** against received power, the sensitivity curve of [Chapter 21]({% link chapters/21_pd.md %}). RF probes, cables and bias tees must be de-embedded like the grating couplers.

## <span class="secnum">31.7</span>Wafer-scale testing

The grating coupler's great advantage is that the whole wafer can be tested before dicing ([Chapter 15]({% link chapters/15_gc.md %})). Measuring the same structures on every die gives **wafer maps** of propagation loss, ring resonance wavelength, coupler efficiency and responsivity. These maps reveal the process variation of [Chapter 29]({% link chapters/29_fab.md %}), screen out bad dies before packaging, and feed the statistics of [Chapter 32]({% link chapters/32_analysis.md %}).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

The openEBL chips are measured on an automated probe station: a swept tunable laser, TE polarisation through a polarisation-maintaining fibre array at 127 µm pitch, a temperature-controlled stage, and a sweep of each labelled structure. Expect the raw spectra of [Chapter 32]({% link chapters/32_analysis.md %}): envelopes from the couplers, fringes, and the devices' responses on top.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab game: Illuminator (build a sensing circuit)](https://s3.amazonaws.com/vmlab-app-2/Main/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="siepiclab,openebl,phot1x,chrostowski2015" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Passive setup: swept tunable laser, polarisation control, fibre array, synchronised detectors and a temperature-controlled stage.
- Automated probe stations need design-for-test layouts; SiEPIClab is open source.
- De-embed the couplers with a loopback or a fitted envelope; trust relative quantities more than absolute losses.
- Lasers: LIV, spectrum and SMSR, RIN and linewidth; high-speed devices: S-parameters, eyes and BER.
- Wafer-scale testing with grating couplers maps the process variation before dicing.

</div>
