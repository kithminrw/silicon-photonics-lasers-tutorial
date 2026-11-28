---
title: "39. Beyond Datacom: Sensing, LiDAR, Quantum and Computing"
parent: "Part IX · Systems and Applications"
nav_order: 39
permalink: /part-9/ch39/
chapter: 39
---

# <span class="chapnum">Chapter 39</span>Beyond Datacom: Sensing, LiDAR, Quantum and Computing

The same building blocks make biosensors, beam steerers, quantum processors and optical neural networks.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain evanescent-field biosensing with rings, and compute sensitivity and limit of detection;
- describe optical phased arrays and FMCW LiDAR;
- outline integrated quantum photonics: sources, circuits and detectors;
- outline photonic computing with programmable MZI meshes, and how errors limit them;
- compare on-chip spectrometers, and use the Sagnac effect to size a chip gyroscope;
- name the microwave-photonic, visible and mid-infrared applications and platforms.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What changes when the chip is a sensor, a beam steerer or a processor instead of a transceiver?

</div>

## <span class="secnum">39.1</span>Biosensing with evanescent fields

Part of a waveguide mode travels outside the core, in the evanescent field ([Chapter 5]({% link chapters/05_slab.md %})). If the cladding is a fluid, a change in the fluid's index, or molecules binding to the waveguide surface, changes the mode's effective index. A ring resonator turns that into a resonance shift ([Chapter 12]({% link chapters/12_rings.md %})). Its **bulk sensitivity** is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Bulk sensitivity and limit of detection of a ring sensor</div>

$$S = \frac{\mathrm{d}\lambda}{\mathrm{d}n_c} = \frac{\lambda}{n_g}\,\frac{\partial n_\mathrm{eff}}{\partial n_c}, \qquad \mathrm{LOD} = \frac{3\sigma_\lambda}{S}$$

</div>

with $$\sigma_\lambda$$ the noise in tracking the resonance. Computed with femwell for a 500 × 220 nm silicon strip in water (<code>figsrc/ch39_sensor.py</code>), $$S$$ is 54 nm per refractive-index unit (RIU) for TE light and 206 nm/RIU for TM. TM's field reaches far further into the water above the strip ([Figure 39.1](#fig-39-1)), so half of a change in the water's index appears in its effective index, against 15 % for TE. Thinner or slotted waveguides and subwavelength gratings push more of the field into the analyte still.

<figure id="fig-39-1">
  <img src="{{ '/assets/figs/ch39_sensor.svg' | relative_url }}" style="width:640px" alt="Power density of the TE0 and TM0 modes of a 500 by 220 nm silicon strip on oxide covered by water at 1550 nm: the TE mode stays mostly inside the silicon and spreads sideways, the TM mode reaches much further into the water above and the oxide below; insets give effective indices 2.426 and 1.703, index sensitivities 0.15 and 0.50, and bulk sensitivities 54 and 206 nm per RIU">
  <figcaption><span class="capnum">Figure 39.1.</span> <strong>Where the sensor's light is.</strong> Power density of (a) the TE<sub>0</sub> and (b) the TM<sub>0</sub> mode of the 500 × 220 nm silicon strip on oxide under water, at 1550 nm, computed with femwell (the same model as the sensitivities, on a coarser mesh, which smooths the jumps of the TM field at the top and bottom faces); contours at half and 1/e² of the peak. The TE mode sits mostly in the silicon; the TM mode's tail reaches about twice as far into the water (decay length 229 against 121 nm), so a change in the water's index moves its effective index 0.50 times as much, against 0.15 for TE. Drawn by <code>figsrc/ch39_figs.py</code> from <code>figsrc/ch39_fields.py</code>.</figcaption>
</figure>

The shift alone does not set the detection limit; the precision of tracking the resonance does. A higher Q gives a narrower dip whose centre can be found more precisely. Temperature control is essential: at 75 pm/K ([Chapter 18]({% link chapters/18_thermal.md %})), a millikelvin drift is comparable to the signal from a $$10^{-6}$$ RIU change, so sensors use reference rings, which see the temperature but not the analyte. For molecular detection the waveguide surface is coated with capture molecules, antibodies or DNA probes, that bind only the target.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 39.1 · Limit of detection</div>

If the resonance can be tracked to $$\sigma_\lambda = 1$$ pm, the limit of detection is $$3 \times 10^{-3}/206 = 1.5\times10^{-5}$$ RIU for TM, and $$5.6\times10^{-5}$$ RIU for TE. A change of $$5\times10^{-4}$$ RIU, roughly a few milligrams per millilitre of protein, shifts a TM resonance by 103 pm, many times its 1 pm noise.

</div>

**Try it.** Change the analyte index, the Q and the tracking noise, for TE and TM.

{% include demos/biosensor.html %}

## <span class="secnum">39.2</span>LiDAR and optical phased arrays

**Optical phased arrays** (OPAs) steer a beam without moving parts ([Figure 39.2](#fig-39-2)). A row of grating emitters, each fed through its own phase shifter ([Chapter 18]({% link chapters/18_thermal.md %})), radiates waves that add up in the direction where the path difference compensates the phase step: $$\sin\theta = \Delta\phi\,\lambda/(2\pi d)$$ for emitters a pitch $$d$$ apart. The beam's width is set by the aperture: about $$0.886\,\lambda/(Nd)$$ radians between the half-power points, broadening as $$1/\cos\theta$$ when steered. The central difficulty is **grating lobes**: unless $$d \le \lambda/2$$ (0.78 µm at 1550 nm), the same phases add up in other directions too, and silicon waveguides couple when packed that closely. Designs use non-uniform spacing, waveguides of alternating widths that do not couple, or accept a limited steering range. Steering in the other direction comes from the wavelength, through the emitters' grating angle ([Chapter 15]({% link chapters/15_gc.md %})).

<figure id="fig-39-2">
  <img src="{{ '/assets/figs/ch39_opa.svg' | relative_url }}" style="width:640px" alt="(a) Top view of an eight-channel optical phased array: a tree of splitters, a phase shifter on every arm, and a fan-in to closely spaced grating emitters. (b) Far field of 16 emitters steered to 20 degrees: with a pitch of half a wavelength one beam 6.75 degrees wide; with a 2 µm pitch a beam 2.6 degrees wide and an equally strong grating lobe at minus 25.7 degrees">
  <figcaption><span class="capnum">Figure 39.2.</span> <strong>An optical phased array.</strong> (a) Layout of an eight-channel array (schematic): a splitter tree feeds every emitter through its own phase shifter, and the waveguides fan in to the emitter pitch \(d\). (b) Far field of 16 emitters steered to 20° (array factor). At \(d = \lambda/2\) the beam is 6.75° wide and alone; at \(d\) = 2 µm it is 2.6° wide, as \(0.886\,\lambda/(Nd\cos\theta)\) predicts, but a grating lobe as strong as the main beam appears at −25.7°. Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

**Try it.** Change the number of emitters, their pitch and the phase step; watch the main beam steer and the grating lobes appear.

{% include demos/opa.html %}

**FMCW LiDAR** measures distance coherently. The laser frequency is swept linearly by a bandwidth $$B$$ in a time $$T$$; light returning from a target at range $$R$$ is delayed by $$2R/c$$, and beats with the outgoing light at

$$f_b = \frac{2RB}{cT},$$

which a photodiode and an FFT measure ([Figure 39.3](#fig-39-3)). The range resolution is $$c/(2B)$$, and the Doppler shift gives the target's velocity in the same measurement. The laser must stay coherent over the round trip ([Chapter 25]({% link chapters/25_dynamics.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 39.2 · An FMCW chirp</div>

A 1 GHz sweep in 10 µs gives a range resolution of $$3\times10^8/(2\times10^9) = 15$$ cm, and a target at 100 m beats at $$2 \times 100 \times 10^9/(3\times10^8 \times 10^{-5}) = 67$$ MHz. The round trip of 200 m needs a coherence length $$c/(\pi\Delta\nu) > 200$$ m: a linewidth below about 0.5 MHz, which the narrow-linewidth lasers of [Chapter 26]({% link chapters/26_tunable.md %}) provide.

</div>

<figure id="fig-39-3">
  <img src="{{ '/assets/figs/ch39_fmcw.svg' | relative_url }}" style="width:640px" alt="(a) Sawtooth frequency sweep of 1 GHz in 10 µs, with the echo from 100 m delayed by 0.667 µs. (b) Zoom showing the 66.7 MHz frequency difference between outgoing and returning light. (c) Spectrum of the beat signal with peaks at 26.7 MHz for a target at 40 m and 66.7 MHz for one at 100 m, with a range axis on top">
  <figcaption><span class="capnum">Figure 39.3.</span> <strong>FMCW ranging.</strong> (a) The laser frequency is swept by 1 GHz in 10 µs (Worked Example 39.2); the echo from a target at 100 m returns 0.667 µs later. (b) At any instant the echo and the outgoing light differ by \(f_b = 2RB/(cT)\) = 66.7 MHz. (c) The spectrum of the beat signal over one sweep (Hann window) for targets at 40 m and 100 m, the nearer one with an illustrative half amplitude: each range becomes a frequency, 0.667 MHz per metre, and the 100 kHz frequency resolution of a 10 µs record is the 15 cm range resolution \(c/2B\). Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">39.3</span>Quantum photonics

Integrated photonics is one of the leading platforms for quantum information with light ([Figure 39.4](#fig-39-4)):

- **Sources**: spontaneous four-wave mixing in silicon or silicon-nitride rings converts two pump photons into a signal–idler pair, heralded single photons and entangled pairs, on a chip ([Chapter 7]({% link chapters/07_loss.md %}) describes the nonlinearity).
- **Circuits**: meshes of MZIs implement arbitrary unitary transformations on photons in many waveguides, the linear optics of quantum gates and boson sampling, with heaters as the knobs ([Chapter 11]({% link chapters/11_mzi.md %})).
- **Detectors**: superconducting nanowire single-photon detectors on waveguides, near unity efficiency, but cryogenic.

Loss is the enemy: every lost photon is a lost qubit, so low-loss SiN and careful coupling ([Chapters 15]({% link chapters/15_gc.md %}) and [16]({% link chapters/16_edge.md %})) matter even more than in datacom.

<figure id="fig-39-4">
  <img src="{{ '/assets/figs/ch39_quantum.svg' | relative_url }}" style="width:640px" alt="(a) Schematic of a quantum-photonic chip: a pump laser split to two microring photon-pair sources, pump filters and signal-idler splitters, a mesh of MZIs, and four superconducting nanowire detectors in a cryogenic region. (b) Spectrum of four-wave mixing: idler and signal lines placed symmetrically about the pump">
  <figcaption><span class="capnum">Figure 39.4.</span> <strong>A quantum-photonic circuit.</strong> (a) A pump laser drives two microring sources in which spontaneous four-wave mixing creates photon pairs; filters remove the pump and separate signal from idler; a mesh of MZIs set by heaters performs the linear-optical transformation; superconducting nanowire single-photon detectors (SNSPDs), cooled to cryogenic temperature, count the photons. (b) Energy conservation in the source: two pump photons become a signal and an idler photon placed symmetrically about the pump. Schematic. Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">39.4</span>Photonic computing

A mesh of $$N(N-1)/2$$ MZIs, each with two phase shifters, plus $$N$$ phase shifters at its outputs, can implement any $$N\times N$$ unitary matrix ([Chapter 11]({% link chapters/11_mzi.md %}), [Figure 39.5](#fig-39-5)). Light passing through it performs a matrix–vector multiplication in one pass, at the speed of light and with little energy per operation once the weights are set. That is attractive for the linear layers of neural networks. Other architectures use WDM, with rings weighting each wavelength before a photodiode sums them, or delay lines. The challenges are the conversions in and out of the optical domain, the precision (a few bits) set by noise and fabrication errors ([Chapter 35]({% link chapters/35_fab.md %})), and the nonlinear functions that light does poorly.

<figure id="fig-39-5">
  <img src="{{ '/assets/figs/ch39_mesh.svg' | relative_url }}" style="width:640px" alt="(a) One MZI cell: an external phase shifter phi, a 50:50 coupler, an internal phase shifter theta and a second 50:50 coupler. (b) A rectangular mesh of 15 such cells on six waveguides, in six alternating columns, followed by six output phase shifters, mapping inputs x1 to x6 to outputs y1 to y6">
  <figcaption><span class="capnum">Figure 39.5.</span> <strong>An MZI mesh for linear algebra.</strong> (a) The unit cell: two 50:50 couplers around an internal phase θ, which sets the split between bar and cross, and an external phase φ: together any 2 × 2 unitary. (b) A rectangular mesh for N = 6: 15 cells and 6 output phase shifters, 36 phases in all, as many as the real parameters of a 6 × 6 unitary. Light entering as the vector x leaves as y = Ux in one pass. Schematic. Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

**Programming a mesh.** Reck and colleagues showed that any unitary matrix can be factored into a sequence of 2 × 2 transformations, one per MZI, arranged as a triangle {% include cite.html keys="reck1994" %}. Clements and colleagues rearranged the same MZIs into the rectangle of [Figure 39.5b](#fig-39-5). There every path crosses the same number of cells, N, instead of anywhere from 1 to 2N − 3, so the paths lose equal amounts of light and the mesh is half as deep {% include cite.html keys="clements2016" %}. Programming the mesh means computing each MZI's two phases from the target matrix and setting its heaters. Wired as hexagons or squares instead of a one-way rectangle, the same cells become general programmable circuits, configured in software as filters, switches or delay lines {% include cite.html keys="bogaerts2020" %}.

**Errors.** Every phase shifter is set with some error, and every coupler splits a little off 50:50. The errors add up along each path, so at the same component quality a large mesh builds its matrix less faithfully than a small one. An imperfect coupler also limits how completely an MZI can switch: splitting 45:55, it can no longer send all its light to one output. Meshes are therefore calibrated after fabrication, or set up by self-configuring algorithms that use only measurements at their outputs and so correct for coupler errors within a range {% include cite.html keys="miller2015" %}. A programmable silicon MZI processor of this kind has performed the matrix multiplications of a small neural network that recognised vowels {% include cite.html keys="shen2017" %}.

**Try it.** Build a 4 × 4, 6 × 6 or 8 × 8 matrix, then add phase and splitter errors and compare what the mesh builds with what it was set for.

{% include demos/mesh.html %}

## <span class="secnum">39.5</span>Microwave photonics and frequency combs

Light can carry and process radio-frequency signals. Ring filters ([Chapter 12]({% link chapters/12_rings.md %})) tunable over gigahertz, true-time delays for phased-array antennas, and low-noise optoelectronic oscillators are all built from the same blocks. **Kerr frequency combs** in high-Q silicon-nitride rings convert a continuous laser into hundreds of equally spaced lines by four-wave mixing ([Figure 39.6](#fig-39-6)). They are sources for dense WDM ([Chapter 26]({% link chapters/26_tunable.md %})), for spectroscopy, for optical clocks and for low-noise microwave generation from the comb spacing.

<figure id="fig-39-6">
  <img src="{{ '/assets/figs/ch39_comb.svg' | relative_url }}" style="width:600px" alt="(a) A silicon nitride ring beside a bus waveguide, with a continuous-wave pump entering and a comb leaving; the line spacing equals the ring's free spectral range. (b) Schematic comb spectrum: equally spaced lines under a sech-squared envelope centred on a stronger pump line">
  <figcaption><span class="capnum">Figure 39.6.</span> <strong>A Kerr microcomb.</strong> (a) A continuous-wave pump coupled into a high-Q silicon-nitride ring creates, by four-wave mixing, new lines on the ring's resonances, spaced by its free spectral range. (b) The spectrum of a soliton comb: equally spaced lines under a sech² envelope around the pump. Schematic, without scales. Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">39.6</span>On-chip spectrometers

A spectrometer measures how a light's power is spread over wavelength. On a chip it trades resolution, bandwidth, footprint and throughput against each other {% include cite.html keys="yang2021spec" %}. There are three families:

- **dispersive**: an arrayed-waveguide or echelle grating ([Chapter 14]({% link chapters/14_wdm.md %})) sends each wavelength to its own output. Its resolution improves with the spread of path lengths across it, so a fine resolution needs a large device.
- **Fourier-transform**: an array of MZIs with delays 0, ΔL, 2ΔL, … samples the interferogram of the input at many path differences at once, without moving parts, and the spectrum is its Fourier transform ([Figure 39.7](#fig-39-7)) {% include cite.html keys="florjanczyk2007" %}. Coiling the delays into silicon spirals, 32 MZIs have resolved 40 pm over a 0.75 nm range in 12 mm² {% include cite.html keys="velasco2013" %}.
- **computational**: a disordered or multimode structure scrambles the light into a speckle pattern that differs from one wavelength to the next. A calibration matrix maps spectra to patterns, and inverting it recovers an unknown spectrum. A disordered silicon structure a few tens of micrometres across resolved 0.75 nm near 1500 nm this way {% include cite.html keys="redding2013" %}.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Fourier-transform spectrometer of N MZIs with delay step ΔL</div>

$$\delta\lambda \approx \frac{\lambda^2}{N\,n_g\,\Delta L}, \qquad \text{bandwidth} \approx \frac{N}{2}\,\delta\lambda$$

</div>

The resolution is set by the longest delay, about $$N\Delta L$$; the group index appears because it sets how fast each MZI's phase changes with wavelength. N samples give N/2 independent channels, so the bandwidth grows only with the number of MZIs.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 39.3 · A 45 pm Fourier-transform spectrometer</div>

Thirty-two MZIs on silicon wires ($$n_g = 4.2$$) with a delay step of 0.40 mm have a longest delay of 12.4 mm and a resolution of $$(1.55\ \mu\mathrm{m})^2/(32 \times 4.2 \times 0.40\ \mathrm{mm}) = 45$$ pm. Their 32 samples give 16 channels, a band of 0.72 nm. Light outside the band folds back into it, so a filter in front must remove it. Twice the bandwidth at the same resolution needs twice as many MZIs.

</div>

<figure id="fig-39-7">
  <img src="{{ '/assets/figs/ch39_spectrometer.svg' | relative_url }}" style="width:640px" alt="(a) Schematic of a Fourier-transform spectrometer: light splits among 32 MZIs, MZI k having one arm longer by k delay steps, drawn as loops that grow with k, each followed by a photodiode. (b) The output difference of each MZI against its number, an oscillating interferogram starting at 1. (c) The input spectrum, two narrow lines 100 picometres apart and a broader band, and the spectrum recovered from the 32 samples: the two lines resolved but broadened to about 45 picometres, the broad band matched.">
  <figcaption><span class="capnum">Figure 39.7.</span> <strong>A Fourier-transform spectrometer.</strong> (a) Light splits among 32 MZIs; MZI k has one arm longer by k·ΔL, and detectors read its outputs (schematic). (b) The difference between the two outputs of each MZI for the input of (c): the interferogram, sampled at path differences n<sub>g</sub>kΔL, with ΔL = 0.40 mm and n<sub>g</sub> = 4.2 (Worked Example 39.3). (c) The input spectrum (two lines 100 pm apart and a broader band, illustrative) and the spectrum recovered from the 32 samples by a cosine transform with a Hann window. The lines are resolved but broadened to the instrument's 45 pm resolution; the 0.72 nm shown is the band the 32 samples cover without aliasing. Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">39.7</span>Optical gyroscopes

Light sent both ways around a rotating loop takes slightly longer in one direction than in the other. This **Sagnac effect** shifts the phase of one direction against the other by

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Sagnac phase of an N-turn loop</div>

$$\Delta\phi = \frac{8\pi N A\,\Omega}{\lambda c}$$

</div>

for N turns enclosing an area A, rotating at Ω, at the vacuum wavelength λ; the waveguide's index drops out. Fibre-optic gyroscopes wind about a kilometre of fibre into a coil and help navigate aircraft and ships. On a chip, area is scarce: a spiral of length ℓ at a mean radius r encloses $$NA = \ell r/2$$, because each turn, $$2\pi r$$ long, encloses $$\pi r^2$$ ([Figure 39.8](#fig-39-8)).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 39.4 · Feeling the Earth turn</div>

The Earth turns at 15°/h, $$7.29\times10^{-5}$$ rad/s. A spiral 1 m long at a mean radius of 2.5 mm gives $$\Delta\phi = 4\pi\ell r\Omega/(\lambda c) = 4.9\times10^{-9}$$ rad at 1550 nm. A 1 km fibre coil of 4 cm radius gives $$7.9\times10^{-5}$$ rad, 16,000 times more.

</div>

A longer spiral collects more phase but loses more light. The detected power falls as $$e^{-\alpha\ell}$$, and the shot-noise-limited phase noise grows as $$1/\sqrt{P}$$, so the signal-to-noise ratio grows as $$\ell e^{-\alpha\ell/2}$$, which peaks at $$\ell = 2/\alpha$$, a loss of 8.7 dB. Chip gyroscopes therefore need the lowest-loss waveguides: at 0.1 dB/cm the best spiral is 0.87 m long, at 0.01 dB/cm 8.7 m ([Figure 39.8b](#fig-39-8)). Backscattering, the Kerr effect and thermal drift limit real devices further. Reciprocity helps against drift: a passive silicon network whose two paths share their thermal fluctuations and fabrication errors detected phase shifts about 30 times smaller than earlier integrated gyroscopes {% include cite.html keys="khial2018" %}.

**Resonant and laser gyroscopes.** A ring turns the Sagnac effect into a frequency splitting between its clockwise and anticlockwise resonances, $$\Delta\nu = 4A\Omega/(n_g\lambda P)$$ for an area A and a perimeter P, or $$D\Omega/(n_g\lambda)$$ for a circle of diameter D. For D = 18 mm and $$n_g$$ = 1.5 at 1550 nm, the Earth's rotation splits the resonances by only 0.56 Hz. Brillouin lasers in high-Q rings lase both ways with sub-hertz linewidths, and their beat note measures that splitting: a chip-scale ring laser gyroscope of this kind has measured the Earth's rotation {% include cite.html keys="lai2020" %}.

<figure id="fig-39-8">
  <img src="{{ '/assets/figs/ch39_gyro.svg' | relative_url }}" style="width:640px" alt="(a) Schematic of a chip gyroscope: a spiral waveguide of four turns with light circulating clockwise and anticlockwise; its outer end and, crossing under the turns on a second layer, its inner end lead to a 2 by 2 coupler with a laser and a detector. (b) Log-log plot of the smallest rotation rate resolved in one second against spiral length for waveguide losses of 1, 0.1 and 0.01 dB per centimetre: each curve falls with length, reaches a minimum at 9 centimetres, 0.87 metres and 8.7 metres, then rises; only the 0.01 dB per centimetre curve reaches the Earth's rotation rate of 15 degrees per hour.">
  <figcaption><span class="capnum">Figure 39.8.</span> <strong>A chip gyroscope and its limit.</strong> (a) A 2 × 2 coupler sends light both ways around an N-turn spiral, whose inner end crosses under the turns on a second waveguide layer (dashed, between two interlayer transitions); rotation at Ω delays one direction against the other, and the detector reads the phase difference (schematic). (b) The smallest rotation rate such a gyroscope resolves in 1 s, limited by shot noise, for a spiral at a mean radius of 2.5 mm with 1 mW launched, against its length, for three waveguide losses. The Sagnac phase grows with length while the detected power falls, so each loss has a best length, 2/α (dots), where the spiral loses 8.7 dB: 9 cm, 0.87 m and 8.7 m. Only the 0.01 dB/cm spiral reaches the Earth's rotation rate. Ideal detector; backscattering, the Kerr effect, polarisation and drift, which limit real devices, are left out. Drawn by <code>figsrc/ch39_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">39.8</span>Visible and mid-infrared photonics

Silicon absorbs below 1.1 µm and its oxide absorbs beyond about 3.5 µm, so other wavelengths need other platforms ([Chapter 4]({% link chapters/04_platforms.md %})):

- **Visible and near-infrared**: silicon nitride, aluminium nitride, aluminium oxide and titanium dioxide, for biophotonics, displays, and the lasers that control trapped ions and atoms in quantum computers and clocks.
- **Mid-infrared** (2–10 µm), where many molecules have their fingerprint absorption lines: germanium on silicon, silicon on sapphire or suspended silicon, and chalcogenide glasses, for gas and chemical sensing.

The physics of this tutorial carries over unchanged; only the materials, dimensions and losses change.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

The building blocks stay the same, but the figure of merit changes. A sensor optimises the fraction of field in the analyte and the stability of a resonance against temperature. A beam steerer needs dense, low-crosstalk emitters and many fast phase shifters. A quantum processor needs the lowest possible loss and single-photon detection. A computer needs precision, efficient conversions and calibration of large meshes. A spectrometer trades resolution against footprint, and a gyroscope needs enclosed area and the lowest loss. The design methods, the physics, the open tools and the test-and-analysis loop of this tutorial apply to all of them.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab game: Illuminator (build a sensing circuit)](https://s3.amazonaws.com/vmlab-app-2/Main/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="shekhar2024,chrostowski2015,bogaerts2012,bogaerts2020,clements2016,yang2021spec" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Ring biosensors: $$S = (\lambda/n_g)\,\partial n_\mathrm{eff}/\partial n_c$$; 54 nm/RIU (TE) and 206 nm/RIU (TM) for a silicon strip in water; LOD = 3σ/S: 1.5 × 10⁻⁵ RIU (TM) and 5.6 × 10⁻⁵ RIU (TE) at 1 pm.
- Optical phased arrays steer with phase steps; pitches above λ/2 bring grating lobes.
- FMCW LiDAR: resolution c/(2B), beat frequency 2RB/(cT), and a laser coherent over the round trip.
- Quantum photonics needs pair sources, MZI meshes, single-photon detectors and very low loss; photonic computing uses meshes for matrix multiplication.
- A rectangular mesh of N(N−1)/2 MZIs builds any N × N unitary; phase and splitter errors add up along its N columns, so large meshes need calibration.
- Fourier-transform spectrometers: δλ ≈ λ²/(N n_g ΔL) and N/2 channels; 32 MZIs with 0.40 mm steps resolve 45 pm over 0.72 nm.
- Sagnac phase 8πNAΩ/(λc): chip gyroscopes lack area, and loss sets the best spiral length, 2/α.
- Combs, microwave photonics, and visible and mid-infrared platforms extend the same building blocks.

</div>

## Check yourself

{% include quiz.html %}
