---
title: "34. Beyond Datacom: Sensing, LiDAR, Quantum and Computing"
parent: "Part VIII · Systems and Applications"
nav_order: 34
permalink: /part-8/ch34/
chapter: 34
---

# <span class="chapnum">Chapter 34</span>Beyond Datacom: Sensing, LiDAR, Quantum and Computing

The same building blocks make biosensors, beam steerers, quantum processors and optical neural networks.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain evanescent-field biosensing with rings, and compute sensitivity and limit of detection;
- describe optical phased arrays and FMCW LiDAR;
- outline integrated quantum photonics: sources, circuits and detectors;
- outline photonic computing with interferometer meshes;
- name the microwave-photonic, visible and mid-infrared applications and platforms.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What changes when the chip is a sensor, a beam steerer or a processor instead of a transceiver?

</div>

## <span class="secnum">34.1</span>Biosensing with evanescent fields

Part of a waveguide mode travels outside the core, in the evanescent field ([Chapter 5]({% link chapters/05_slab.md %})). If the cladding is a fluid, a change in the fluid's index, or molecules binding to the waveguide surface, changes the mode's effective index. A ring resonator turns that into a resonance shift ([Chapter 12]({% link chapters/12_rings.md %})). Its **bulk sensitivity** is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Bulk sensitivity and limit of detection of a ring sensor</div>

$$S = \frac{\mathrm{d}\lambda}{\mathrm{d}n_c} = \frac{\lambda}{n_g}\,\frac{\partial n_\mathrm{eff}}{\partial n_c}, \qquad \mathrm{LOD} = \frac{3\sigma_\lambda}{S}$$

</div>

with $$\sigma_\lambda$$ the noise in tracking the resonance. Computed with femwell for a 500 × 220 nm silicon strip in water (<code>figsrc/ch34_sensor.py</code>), $$S$$ is 54 nm per refractive-index unit (RIU) for TE light and 206 nm/RIU for TM. TM's field reaches far further into the water above the strip, so half of a change in the water's index appears in its effective index, against 15 % for TE. Thinner or slotted waveguides and subwavelength gratings push more of the field into the analyte still.

The shift alone does not set the detection limit; the precision of tracking the resonance does. A higher Q gives a narrower dip whose centre can be found more precisely. Temperature control is essential: at 75 pm/K ([Chapter 18]({% link chapters/18_thermal.md %})), a millikelvin drift is comparable to the signal from a $$10^{-6}$$ RIU change, so sensors use reference rings, which see the temperature but not the analyte. For molecular detection the waveguide surface is coated with capture molecules, antibodies or DNA probes, that bind only the target.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 34.1 · Limit of detection</div>

If the resonance can be tracked to $$\sigma_\lambda = 1$$ pm, the limit of detection is $$3 \times 10^{-3}/206 = 1.5\times10^{-5}$$ RIU for TM, and $$5.6\times10^{-5}$$ RIU for TE. A change of $$5\times10^{-4}$$ RIU, roughly a few milligrams per millilitre of protein, shifts a TM resonance by 103 pm, many times its 1 pm noise.

</div>

**Try it.** Change the analyte index, the Q and the tracking noise, for TE and TM.

{% include demos/biosensor.html %}

## <span class="secnum">34.2</span>LiDAR and optical phased arrays

**Optical phased arrays** (OPAs) steer a beam without moving parts. A row of grating emitters, each fed through its own phase shifter ([Chapter 18]({% link chapters/18_thermal.md %})), radiates waves that add up in the direction where the path difference compensates the phase step: $$\sin\theta = \Delta\phi\,\lambda/(2\pi d)$$ for emitters a pitch $$d$$ apart. The beam's width is set by the aperture: about $$0.886\,\lambda/(Nd)$$ radians between the half-power points, broadening as $$1/\cos\theta$$ when steered. The central difficulty is **grating lobes**: unless $$d \le \lambda/2$$ (0.78 µm at 1550 nm), the same phases add up in other directions too, and silicon waveguides couple when packed that closely. Designs use non-uniform spacing, waveguides of alternating widths that do not couple, or accept a limited steering range. Steering in the other direction comes from the wavelength, through the emitters' grating angle ([Chapter 15]({% link chapters/15_gc.md %})).

**Try it.** Change the number of emitters, their pitch and the phase step; watch the main beam steer and the grating lobes appear.

{% include demos/opa.html %}

**FMCW LiDAR** measures distance coherently. The laser frequency is swept linearly by a bandwidth $$B$$ in a time $$T$$; light returning from a target at range $$R$$ is delayed by $$2R/c$$, and beats with the outgoing light at

$$f_b = \frac{2RB}{cT},$$

which a photodiode and an FFT measure. The range resolution is $$c/(2B)$$, and the Doppler shift gives the target's velocity in the same measurement. The laser must stay coherent over the round trip ([Chapter 25]({% link chapters/25_dynamics.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 34.2 · An FMCW chirp</div>

A 1 GHz sweep in 10 µs gives a range resolution of $$3\times10^8/(2\times10^9) = 15$$ cm, and a target at 100 m beats at $$2 \times 100 \times 10^9/(3\times10^8 \times 10^{-5}) = 67$$ MHz. The round trip of 200 m needs a coherence length $$c/(\pi\Delta\nu) > 200$$ m: a linewidth below about 0.5 MHz, which the narrow-linewidth lasers of [Chapter 26]({% link chapters/26_tunable.md %}) provide.

</div>

## <span class="secnum">34.3</span>Quantum photonics

Integrated photonics is one of the leading platforms for quantum information with light:

- **Sources**: spontaneous four-wave mixing in silicon or silicon-nitride rings converts two pump photons into a signal–idler pair, heralded single photons and entangled pairs, on a chip ([Chapter 7]({% link chapters/07_loss.md %}) describes the nonlinearity).
- **Circuits**: meshes of MZIs implement arbitrary unitary transformations on photons in many waveguides, the linear optics of quantum gates and boson sampling, with heaters as the knobs ([Chapter 11]({% link chapters/11_mzi.md %})).
- **Detectors**: superconducting nanowire single-photon detectors on waveguides, near unity efficiency, but cryogenic.

Loss is the enemy: every lost photon is a lost qubit, so low-loss SiN and careful coupling ([Chapters 15]({% link chapters/15_gc.md %}) and [16]({% link chapters/16_edge.md %})) matter even more than in datacom.

## <span class="secnum">34.4</span>Photonic computing

A mesh of $$N(N-1)/2$$ MZIs, each with two phase shifters, plus $$N$$ phase shifters at its outputs, can implement any $$N\times N$$ unitary matrix ([Chapter 11]({% link chapters/11_mzi.md %})). Light passing through it performs a matrix–vector multiplication in one pass, at the speed of light and with little energy per operation once the weights are set. That is attractive for the linear layers of neural networks. Other architectures use WDM, with rings weighting each wavelength before a photodiode sums them, or delay lines. The challenges are the conversions in and out of the optical domain, the precision (a few bits) set by noise and fabrication errors ([Chapter 29]({% link chapters/29_fab.md %})), and the nonlinear functions that light does poorly.

## <span class="secnum">34.5</span>Microwave photonics and frequency combs

Light can carry and process radio-frequency signals. Ring filters ([Chapter 12]({% link chapters/12_rings.md %})) tunable over gigahertz, true-time delays for phased-array antennas, and low-noise optoelectronic oscillators are all built from the same blocks. **Kerr frequency combs** in high-Q silicon-nitride rings convert a continuous laser into hundreds of equally spaced lines by four-wave mixing. They are sources for dense WDM ([Chapter 26]({% link chapters/26_tunable.md %})), for spectroscopy, for optical clocks and for low-noise microwave generation from the comb spacing.

## <span class="secnum">34.6</span>Visible and mid-infrared photonics

Silicon absorbs below 1.1 µm and its oxide absorbs beyond about 3.5 µm, so other wavelengths need other platforms ([Chapter 4]({% link chapters/04_platforms.md %})):

- **Visible and near-infrared**: silicon nitride, aluminium nitride, aluminium oxide and titanium dioxide, for biophotonics, displays, and the lasers that control trapped ions and atoms in quantum computers and clocks.
- **Mid-infrared** (2–10 µm), where many molecules have their fingerprint absorption lines: germanium on silicon, silicon on sapphire or suspended silicon, and chalcogenide glasses, for gas and chemical sensing.

The physics of this tutorial carries over unchanged; only the materials, dimensions and losses change.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

The building blocks stay the same, but the figure of merit changes. A sensor optimises the fraction of field in the analyte and the stability of a resonance against temperature. A beam steerer needs dense, low-crosstalk emitters and many fast phase shifters. A quantum processor needs the lowest possible loss and single-photon detection. A computer needs precision, efficient conversions and calibration of large meshes. The design methods, the physics, the open tools and the test-and-analysis loop of this tutorial apply to all of them.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab game: Illuminator (build a sensing circuit)](https://s3.amazonaws.com/vmlab-app-2/Main/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="shekhar2024,chrostowski2015,bogaerts2012" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Ring biosensors: $$S = (\lambda/n_g)\,\partial n_\mathrm{eff}/\partial n_c$$; 54 nm/RIU (TE) and 206 nm/RIU (TM) for a silicon strip in water; LOD = 3σ/S: 1.5 × 10⁻⁵ RIU (TM) and 5.6 × 10⁻⁵ RIU (TE) at 1 pm.
- Optical phased arrays steer with phase steps; pitches above λ/2 bring grating lobes.
- FMCW LiDAR: resolution c/(2B), beat frequency 2RB/(cT), and a laser coherent over the round trip.
- Quantum photonics needs pair sources, MZI meshes, single-photon detectors and very low loss; photonic computing uses meshes for matrix multiplication.
- Combs, microwave photonics, and visible and mid-infrared platforms extend the same building blocks.

</div>
