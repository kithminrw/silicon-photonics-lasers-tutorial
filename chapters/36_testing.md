---
title: "36. Testing Photonic Chips"
parent: "Part VIII · Fabrication, Testing and Data Analysis"
nav_order: 36
permalink: /part-8/ch36/
chapter: 36
---

# <span class="chapnum">Chapter 36</span>Testing Photonic Chips

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

## <span class="secnum">36.1</span>The passive test setup

A passive photonic chip is characterised by its transmission spectrum. The standard setup has five parts ([Figure 36.1](#fig-36-1)):

- a **tunable laser** that sweeps across the band (for example 1500–1600 nm) in fine steps, a picometre or less, with its wavelength measured or triggered;
- **polarisation control**: a paddle or electronic polarisation controller, or polarisation-maintaining fibre, to put the light in the TE (or TM) mode the grating couplers accept ([Chapter 15]({% link chapters/15_gc.md %}));
- **fibre coupling** to the chip: a fibre array over the grating couplers, or lensed fibres at the edge couplers, on motorised stages ([Chapter 17]({% link chapters/17_fiberarrays.md %}));
- **detectors**: power meters or photodiodes synchronised with the sweep, with a dynamic range of 60 dB or more;
- a **temperature-controlled stage**, because a silicon ring drifts by 75 pm/K ([Chapter 18]({% link chapters/18_thermal.md %})) and a measurement without it drifts with the room.

<figure id="fig-36-1">
  <img src="{{ '/assets/figs/ch36_setup.svg' | relative_url }}" style="width:600px" alt="Block diagram of a passive test setup. A tunable laser sweeping 1500 to 1600 nm feeds a tap to a reference detector and a polarisation controller with three paddles; polarisation-maintaining fibre leads to a fibre array held over the chip's grating couplers. The chip sits on a temperature-controlled stage on motorised XYZ stages, with a temperature controller. The return fibre goes to power meters or photodetectors. A computer below connects to the laser, reference detector, stages, temperature controller and detectors, and a dashed trigger line links the laser to the detectors.">
  <figcaption><span class="capnum">Figure 36.1.</span> <strong>A passive test setup.</strong> Optical paths in red, electrical and control lines in blue. The tap and reference detector record the laser's own power for normalisation; the trigger makes the detectors sample in step with the wavelength sweep, so each reading has its wavelength. Not to scale. Drawn by <code>figsrc/ch36_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">36.2</span>Automated testing and design for test

A chip with dozens of test structures, or a wafer with hundreds of dies, is measured by an automated probe station. It moves the fibre array from one structure to the next using the layout coordinates, aligns to each automatically (a search for first light, then optimisation, as in [Chapter 17]({% link chapters/17_fiberarrays.md %})), runs the sweep the structure's label asks for, and stores the result. The SiEPIC program publishes its probe-station software, SiEPIClab {% include cite.html keys="siepiclab" %}. Automation only works if the layout follows **design-for-test** rules: couplers on the array pitch in a fixed orientation, machine-readable labels, alignment loopbacks, and electrical pads on a probe-card grid ([Chapter 30]({% link chapters/30_flow.md %}), [Figure 36.2](#fig-36-2)).

<figure id="fig-36-2">
  <img src="{{ '/assets/figs/ch36_dft.svg' | relative_url }}" style="width:600px" alt="Top view to scale of six grating couplers in a row at 127 micrometre pitch, each under a fibre of the array drawn as a 125 micrometre cladding circle with a 10 micrometre mode field at its centre; the circles almost touch. Couplers 1 and 2 are joined by a semicircular loopback; couplers 3 and 4 by a tall U-shaped bus with a ring beside it, drawn three times enlarged; couplers 5 and 6 by a double spiral for cutback measurements. Vertical machine-readable labels such as opt_in_TE_1550_ring250 sit beside the input couplers.">
  <figcaption><span class="capnum">Figure 36.2.</span> <strong>A row of test structures designed for test.</strong> The grating couplers sit on the fibre array's 127 µm pitch, under fibres whose 125 µm claddings almost touch, so one placement of the array reaches a whole group of couplers. A loopback (two couplers and a short waveguide) is used to align the array and to calibrate; the device under test, here the 250 nm-gap ring of Table 12.1, and a cutback spiral (one of several lengths) follow, each with a machine-readable label. To scale except the ring and its gap (×3); waveguides drawn as lines. Drawn by <code>figsrc/ch36_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">36.3</span>Calibration and de-embedding

What the detector sees is the device's response multiplied by everything else on the path: the laser's power against wavelength, the fibres and connectors, and above all the two grating couplers, each of which loses a few decibels and has a 30–40 nm wide passband ([Chapter 15]({% link chapters/15_gc.md %})). Removing those is **de-embedding**:

- normalise to the laser's own output (a reference detector);
- measure a **loopback** (two couplers joined by a short waveguide) on the same chip, and divide the device's spectrum by it;
- or fit a smooth envelope to the device's own off-resonance spectrum.

The loopback assumes that its couplers equal the device's. Fabrication variation and slightly different fibre positions make that approximate, a source of a few tenths of a decibel of error in absolute loss. Relative measurements, such as resonance shapes and wavelengths and the slope of a cutback, are far more robust than absolute ones.

**Try it.** Sweep the virtual laser through a ring between two grating couplers; change the polarisation, the coupler reflections and the averaging, and switch to the loopback-calibrated view.

{% include demos/testbench.html %}

Three artefacts appear in real data and in the demo: **fringes** from reflections between the couplers ([Chapter 15]({% link chapters/15_gc.md %})), which can be mistaken for weak resonances; a **polarisation** error, which lowers the whole spectrum and can add a TM resonance series; and **noise** near the band edges, where little light gets through.

## <span class="secnum">36.4</span>Testing active devices

Active devices add electrical probes, a needle or a probe card on the pads ([Figure 36.3](#fig-36-3)):

- **Heaters**: the IV curve gives the resistance; the resonance shift against power gives the tuning efficiency and $$P_\pi$$ ([Chapter 18]({% link chapters/18_thermal.md %})).
- **Modulators and junctions**: the IV curve checks the diode; spectra at several reverse biases give the resonance shift or phase per volt, hence $$V_\pi L$$ and the loss against bias ([Chapter 19]({% link chapters/19_eo.md %})).
- **Photodiodes**: dark current against bias, and photocurrent against known input power, give the responsivity ([Chapter 21]({% link chapters/21_pd.md %})).

<figure id="fig-36-3">
  <img src="{{ '/assets/figs/ch36_probe.svg' | relative_url }}" style="width:600px" alt="Top-view sketch of a chip with a ring modulator beside a U-shaped bus between two grating couplers under a fibre array, connected to a laser and a detector. A heater arc on the ring's left is wired to two square pads touched by two DC needles from a source-measure unit. The ring's PN junction is wired to three pads labelled G, S, G, touched by a GSG probe from the right; the probe connects through a bias tee, fed by a DC bias supply, to a network analyser.">
  <figcaption><span class="capnum">Figure 36.3.</span> <strong>Probing an active device.</strong> DC needles on the heater's pads, driven by a source-measure unit, give its IV curve and the resonance shift against power; a ground–signal–ground (GSG) probe on the junction's pads carries a DC bias, through a bias tee, for IV curves and spectra at several biases, and the RF signal of a network analyser for S-parameters (Section 36.6). The fibre array stays on the grating couplers throughout. Not to scale. Drawn by <code>figsrc/ch36_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">36.5</span>Testing lasers

A laser's characterisation starts with the **LIV** sweep, output power and voltage against current, which gives the threshold, slope efficiency, series resistance and roll-over ([Chapter 24]({% link chapters/24_fp.md %}), [Figure 36.4](#fig-36-4)), at several temperatures for $$T_0$$. An optical spectrum analyser measures the spectrum and the **side-mode suppression ratio** ([Chapter 26]({% link chapters/26_tunable.md %})). An electrical spectrum analyser on a fast photodiode measures **RIN**, and a delayed self-heterodyne interferometer, or a beat note against a reference laser, the **linewidth** ([Chapter 25]({% link chapters/25_dynamics.md %})). Optical isolation between the laser and the measurement is essential, or the instrument's own reflections disturb what it measures. Reliability testing, from burn-in to accelerated life tests at high temperature and current and the qualification tests built on them, is covered in Section 27.9 of [Chapter 27]({% link chapters/27_lasersonsi.md %}).

<figure id="fig-36-4">
  <img src="{{ '/assets/figs/ch36_liv.svg' | relative_url }}" style="width:600px" alt="(a) Block diagram: a current source with voltage sense drives a laser on a temperature controller; its light passes a lens and fibre and an isolator, then splits to a power meter, an optical spectrum analyser, a fast photodiode with an electrical spectrum analyser, and a delayed self-heterodyne interferometer. (b) Synthetic output power and voltage against current at 25 degrees C: power is near zero up to a threshold of 19.0 mA and then rises linearly with slope 0.21 W/A; voltage rises steeply to about 0.85 V and then linearly with dV/dI equal to 5.0 ohm. (c) Power against current at 25, 45, 65 and 85 degrees C, thresholds moving right; an inset plots threshold against temperature on a log scale with a straight-line fit giving T0 = 60 K.">
  <figcaption><span class="capnum">Figure 36.4.</span> <strong>Testing a laser.</strong> (a) The instruments behind an isolator: power meter, optical and electrical spectrum analysers, and a delayed self-heterodyne interferometer for the linewidth. (b) A synthetic L–I–V of the Fabry–Pérot laser of Chapter 24 (threshold 19 mA, 0.21 W/A per facet, 0.85 V, 5 Ω; no self-heating), with a little noise. A straight-line fit above threshold returns the threshold where it crosses zero, 19.0 mA, and the slope efficiency; above threshold the junction voltage is clamped, so dV/dI is the series resistance, 5.0 Ω. (c) The same at four heat-sink temperatures; the fitted thresholds against temperature give \(T_0\) = 60 K. Drawn by <code>figsrc/ch36_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">36.6</span>High-speed testing

Modulators and photodiodes are characterised in the frequency domain with a lightwave component analyser, a vector network analyser with a calibrated optical transmitter and receiver, which gives the electro-optic or opto-electronic **S-parameters** and the 3 dB bandwidth ([Figure 36.5](#fig-36-5)). In the time domain, a pattern generator drives the modulator and a sampling oscilloscope records the **eye diagram** ([Chapter 20]({% link chapters/20_modulators.md %})); an error detector counts errors to measure the **bit-error ratio** against received power, the sensitivity curve of [Chapter 21]({% link chapters/21_pd.md %}). RF probes, cables and bias tees must be de-embedded like the grating couplers.

<figure id="fig-36-5">
  <img src="{{ '/assets/figs/ch36_rf.svg' | relative_url }}" style="width:600px" alt="Two block diagrams. (a) Frequency domain: a CW laser feeds the modulator under test, driven through a GSG probe from a bias tee that adds DC bias to the swept RF drive from a network analyser's port 1; the modulator's light enters a calibrated photoreceiver whose output returns to port 2; the network analyser and photoreceiver form a lightwave component analyser. (b) Time domain: a pattern generator drives a driver amplifier, a bias tee and the modulator, which a CW laser feeds; its light passes an attenuator and splits to a sampling oscilloscope for the eye and to a receiver and error detector for the bit-error ratio; a dashed clock and pattern reference line runs from the pattern generator to the oscilloscope and error detector.">
  <figcaption><span class="capnum">Figure 36.5.</span> <strong>High-speed tests of a modulator.</strong> (a) In the frequency domain, a lightwave component analyser (a network analyser with a calibrated photoreceiver) sweeps the RF drive and measures the electro-optic \(S_{21}\), hence the 3 dB bandwidth. (b) In the time domain, a pattern generator and driver modulate the light; a sampling oscilloscope records the eye, and an error detector counts errors as the attenuator lowers the received power, giving the sensitivity curve. Optical paths in red, electrical in blue. Not to scale. Drawn by <code>figsrc/ch36_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">36.7</span>Wafer-scale testing

The grating coupler's great advantage is that the whole wafer can be tested before dicing ([Chapter 15]({% link chapters/15_gc.md %})). Measuring the same structures on every die gives **wafer maps** of propagation loss, ring resonance wavelength, coupler efficiency and responsivity. These maps reveal the process variation of [Chapter 35]({% link chapters/35_fab.md %}), screen out bad dies before packaging, and feed the statistics of [Chapter 37]({% link chapters/37_analysis.md %}).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

The openEBL chips are measured on an automated probe station: a swept tunable laser, TE polarisation through a polarisation-maintaining fibre array at 127 µm pitch, a temperature-controlled stage, and a sweep of each labelled structure. Expect the raw spectra of [Chapter 37]({% link chapters/37_analysis.md %}): envelopes from the couplers, fringes, and the devices' responses on top.

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
