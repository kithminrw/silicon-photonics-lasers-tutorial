---
title: "28. Semiconductor Optical Amplifiers"
parent: "Part VI · Lasers and Amplifiers"
nav_order: 28
permalink: /part-6/ch28/
chapter: 28
---

# <span class="chapnum">Chapter 28</span>Semiconductor Optical Amplifiers

An SOA is a laser without mirrors: it amplifies light passing through it, and on a chip it makes up for loss.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- compute single-pass gain and the saturation output power;
- derive the noise figure and its 3 dB limit;
- explain gain dynamics, patterning and polarisation dependence;
- place SOAs in a PIC power budget (booster, in-line, pre-amplifier);
- compare SOAs with erbium-doped amplifiers.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much gain, at what output power and noise figure?

</div>

## <span class="secnum">28.1</span>From laser to amplifier

Take the gain medium of [Chapter 24]({% link chapters/24_fp.md %}) and remove the feedback: the facets are anti-reflection coated and the waveguide is angled to them ([Figure 28.1](#fig-28-1)). Below the current at which it would lase, light passing through is amplified once and leaves. That is a **semiconductor optical amplifier** (SOA). On a III–V chip, or bonded onto silicon ([Chapter 27]({% link chapters/27_lasersonsi.md %})), it can boost a transmitter, compensate the loss of a long circuit, or raise a weak signal before detection.

<figure id="fig-28-1">
  <img src="{{ '/assets/figs/ch28_geometry.svg' | relative_url }}" style="width:600px" alt="Left: top view of a 1 millimetre SOA chip with AR coatings on both facets and a straight active waveguide under a contact, crossing the chip at 8 degrees to the facet normals; light enters and leaves at about 26 degrees in air. Right: zoom on the output facet: the guide meets the facet at 8 degrees to its normal, the dashed residual reflection leaves at 16 degrees to the guide and misses it, and the output beam leaves at about 26 degrees.">
  <figcaption><span class="capnum">Figure 28.1.</span> <strong>An angled-waveguide SOA.</strong> (a) Top view of a 1 mm chip, to scale except for the waveguide, drawn 8 µm wide: the active waveguide under the contact crosses the chip at 8° to the facet normals, and both facets are AR-coated; light enters and leaves at about 26° in air. (b) At the facet (not to scale), whatever the coating fails to suppress is reflected 16° off the waveguide axis and misses the waveguide instead of feeding back into it. The 26° assumes an effective index of 3.2. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">28.2</span>Gain and saturation

Along the amplifier, the signal power $$P$$ grows with the net modal gain:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Single-pass gain with saturation</div>

$$\frac{\mathrm{d}P}{\mathrm{d}z} = \left(\frac{\Gamma g_0}{1 + P/P_\mathrm{sat}} - \alpha_i\right)P, \qquad G_0 = e^{(\Gamma g_0 - \alpha_i)L}$$

</div>

At low power the gain is exponential in the length. As the signal grows, stimulated emission consumes carriers faster than the current replaces them, and the local gain falls ([Chapter 22]({% link chapters/22_emission.md %})). The saturation power $$P_\mathrm{sat} = h\nu A/(\Gamma a\tau)$$, with $$A$$ the active region's cross-section (so that $$A/\Gamma$$ is the mode's area), is larger for a big mode area, a short carrier lifetime $$\tau$$ and a low differential gain $$a$$. The amplifier's usable output is quoted as the **output power at which the gain has dropped by 3 dB** ([Figure 28.2](#fig-28-2)).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 28.1 · A 1 mm SOA</div>

With a small-signal modal gain $$\Gamma g_0 = 35$$ cm⁻¹, $$\alpha_i = 5$$ cm⁻¹, $$L = 1$$ mm and $$P_\mathrm{sat} = 12$$ mW, the small-signal gain is $$e^{30 \times 0.1} = 20$$, or 13.0 dB. Integrating the saturating equation gives a −3 dB output power of 8.7 dBm, reached with about −1.3 dBm in. Doubling the length to 2 mm gives 26 dB of small-signal gain but saturates at a similar output: saturation is set by the end of the amplifier, where the power is highest.

</div>

<figure id="fig-28-2">
  <img src="{{ '/assets/figs/ch28_saturation.svg' | relative_url }}" style="width:600px" alt="Left: gain in decibels against output power for 0.5, 1 and 2 millimetre amplifiers; flat at 6.5, 13 and 26 decibels at low power, then falling, with dots at the minus 3 decibel points near 10.5, 8.7 and 8.3 dBm. Right: output against input power for the same lengths, each curve bending over, with dots at the minus 3 decibel points.">
  <figcaption><span class="capnum">Figure 28.2.</span> <strong>Saturation for three lengths.</strong> The amplifier of Worked Example 28.1 (Γg<sub>0</sub> = 35 cm⁻¹, α<sub>i</sub> = 5 cm⁻¹, P<sub>sat</sub> = 12 mW), integrated along its length. (a) Gain against output power: 0.5, 1 and 2 mm give 6.5, 13.0 and 26.1 dB of small-signal gain but −3 dB output powers (dots) of 10.5, 8.7 and 8.3 dBm. (b) Output against input power: the 1 mm amplifier reaches its −3 dB point with −1.3 dBm in, the 2 mm one already with −14.7 dBm. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

**Try it.** Change the input power, length, drive and saturation power; the top view shows the light growing and the gain saturating towards the output.

{% include demos/soa.html %}

## <span class="secnum">28.3</span>Noise figure

An amplifier cannot amplify without adding noise. Spontaneous emission in the gain medium is amplified along with the signal (amplified spontaneous emission, ASE), and beats with it at the detector. The **noise figure** compares the signal-to-noise ratio before and after the amplifier:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Noise figure of an optical amplifier</div>

$$F = 2n_{sp}\,\frac{G - 1}{G}\,\frac{\Gamma g}{\Gamma g - \alpha_i} \ \xrightarrow{\ G \gg 1,\ n_{sp} = 1,\ \alpha_i = 0\ }\ 2\ \ (3\ \mathrm{dB})$$

</div>

Even a perfectly inverted amplifier ($$n_{sp} = 1$$) has a 3 dB noise figure: a fundamental quantum limit. Real SOAs have $$n_{sp} \approx 1.5$$–2.5 and internal loss, giving 5–7 dB; the example above gives 6.5 dB with $$n_{sp} = 2$$ ([Figure 28.3](#fig-28-3)). Coupling loss at the input adds directly to the noise figure, decibel for decibel, which is why a pre-amplifier must be coupled efficiently.

<figure id="fig-28-3">
  <img src="{{ '/assets/figs/ch28_noise.svg' | relative_url }}" style="width:600px" alt="Left: output spectrum of the 1 millimetre SOA: a broad amplified-spontaneous-emission hump peaking at about minus 41 dBm per 0.1 nanometre, a narrow signal line at minus 2 dBm at 1550 nanometres, and a shaded optical filter band around the signal. Right: noise figure against small-signal gain: an ideal curve rising to the 3 decibel limit, a curve for n_sp 2 with internal loss passing 6.5 decibels at 13 decibels of gain, and a dashed curve 3 decibels higher for a 3 decibel input coupler.">
  <figcaption><span class="capnum">Figure 28.3.</span> <strong>ASE and noise figure.</strong> (a) Output of the 1 mm amplifier for a −15 dBm input: the −2 dBm signal sits on amplified spontaneous emission of density n<sub>sp</sub>hν(G − 1)Γg/(Γg − α<sub>i</sub>), −41.5 dBm per 0.1 nm at the gain peak with n<sub>sp</sub> = 2; the shape of the gain spectrum is illustrative. A filter around the signal removes most of the ASE before the detector. (b) Noise figure against small-signal gain, varying the length: an ideal amplifier approaches the 3 dB limit; with n<sub>sp</sub> = 2 and α<sub>i</sub> = 5 cm⁻¹ the 1 mm amplifier has 6.5 dB, tending to 6.7 dB at high gain; a 3 dB input coupler adds 3 dB. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">28.4</span>Dynamics and patterning

The SOA's gain recovers with the carrier lifetime, from 100 ps to a nanosecond. A long run of "1"s saturates the gain and the following bits see less of it, so the amplified data acquire **pattern-dependent** distortion at gigabit rates, worst when the amplifier is saturated ([Figure 28.4](#fig-28-4)). The same speed is useful: one signal can modulate the gain seen by another (cross-gain modulation), or its phase (cross-phase modulation), for all-optical wavelength conversion and switching. Four-wave mixing in the SOA generates new frequencies.

<figure id="fig-28-4">
  <img src="{{ '/assets/figs/ch28_patterning.svg' | relative_url }}" style="width:600px" alt="Top: a 10 Gb/s bit pattern, with the bits written along the top, through a saturated SOA: the input times the small-signal gain is a dashed square wave reaching 20 milliwatts, while the output's ones reach 10 to 16 milliwatts, highest for a one after a run of zeros and sagging along a long run of ones. Bottom: the gain in decibels against time, between about 9.9 and 12.6 decibels, falling during ones and recovering during zeros, always below the 13 decibel small-signal gain.">
  <figcaption><span class="capnum">Figure 28.4.</span> <strong>Patterning in a saturated SOA.</strong> A 10 Gb/s pattern with 1 mW "ones" and 0.05 mW "zeros" (in the waveguide) through the 1 mm amplifier, computed with a carrier-reservoir model of the integrated gain (P<sub>sat</sub> = 12 mW, 200 ps gain recovery, internal loss folded into the 13 dB small-signal gain) {% include cite.html keys="coldren" %}. (a) Output (blue) against the input times the small-signal gain (dashed): a "one" after a run of zeros gets the most gain, and a long run of ones pulls it down. (b) The gain swings between 9.9 and 12.6 dB with the pattern, recovering during zeros. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">28.5</span>Polarisation and reflections

Quantum-well gain is polarised (TE for compressive strain, [Chapter 23]({% link chapters/23_gain.md %})), so an SOA fed from a fibre would have polarisation-dependent gain; tensile-strained or mixed-strain wells balance it. On a chip, where the light is already TE, it does not matter.

Reflections matter more. Any residual facet reflectivity turns the SOA into a weak Fabry–Pérot cavity ([Section 13.5]({% link chapters/13_bragg.md %})), rippling the gain with wavelength by

$$\frac{G_\mathrm{max}}{G_\mathrm{min}} = \left(\frac{1 + G\sqrt{R_1R_2}}{1 - G\sqrt{R_1R_2}}\right)^2.$$

For 20 dB of gain and 10⁻⁴ reflectivity at each end, the ripple is 0.17 dB; at 10⁻³ it is 1.7 dB, and the amplifier is close to lasing ([Figure 28.5](#fig-28-5)). Anti-reflection coatings alone rarely reach 10⁻⁴, so SOAs combine them with waveguides angled at 7–10° to the facet, the same trick as the edge couplers of [Chapter 16]({% link chapters/16_edge.md %}), and with transparent window regions. The 3D model of an angled SOA facet in Section 24.9 of [Chapter 24]({% link chapters/24_fp.md %}#249inside-the-chip-layer-stacks-in-3d) shows all three.

<figure id="fig-28-5">
  <img src="{{ '/assets/figs/ch28_ripple.svg' | relative_url }}" style="width:460px" alt="Gain in decibels against wavelength offset over 1000 picometres: two sinusoid-like ripples around 20 decibels with a period of 334 picometres, a small one of 0.17 decibels for reflectivity 1e-4 and a large one of 1.7 decibels for 1e-3.">
  <figcaption><span class="capnum">Figure 28.5.</span> <strong>Gain ripple from facet reflections.</strong> Gain of a 1 mm SOA with 20 dB of single-pass gain and the same residual reflectivity R at both facets, from the equation above (n<sub>g</sub> = 3.6, so the ripple repeats every 0.33 nm): R = 10⁻⁴ gives 0.17 dB of ripple, 10⁻³ gives 1.7 dB. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">28.6</span>SOAs in photonic circuits

An SOA can sit in three places, each with its own requirement ([Figure 28.6](#fig-28-6)):

- **Booster**, after the laser and modulator: high output power, so it runs saturated. Fine for one channel; for WDM, saturation causes crosstalk between channels.
- **In-line**, to make up for the loss of a long circuit, such as a switch matrix or a phased array: moderate gain, low noise, linear.
- **Pre-amplifier**, before the detector: low noise figure and high gain, unsaturated. It improves receiver sensitivity like an APD ([Chapter 21]({% link chapters/21_pd.md %})), but adds ASE that needs optical filtering.

Each also adds power consumption and heat, and its own temperature drift.

<figure id="fig-28-6">
  <img src="{{ '/assets/figs/ch28_placement.svg' | relative_url }}" style="width:600px" alt="A link drawn as a chain of blocks: laser, modulator, SOA labelled booster, switch matrix or phased array, SOA labelled in-line, fibre, SOA labelled pre-amplifier, filter, photodiode and TIA. Under each SOA its requirement: booster, high output and runs saturated; in-line, moderate gain, linear, low noise; pre-amplifier, low noise figure, high gain, ASE filtered.">
  <figcaption><span class="capnum">Figure 28.6.</span> <strong>Where an SOA goes.</strong> A booster after the laser and modulator runs saturated for high output; an in-line amplifier makes up for a lossy circuit such as a switch matrix or a phased array; a pre-amplifier before the photodiode needs a low noise figure, and an optical filter for its ASE. Optical paths red, electrical blue. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">28.7</span>Erbium and other amplifiers

The **erbium-doped fibre amplifier** (EDFA) is the amplifier of long-haul telecom. Its 10 ms excited-state lifetime ([Chapter 22]({% link chapters/22_emission.md %})) makes the gain respond to the average power, not the bits, so there is no patterning and no crosstalk between WDM channels. Its noise figure is close to the 3 dB limit (4–5 dB in practice), and its gain does not depend on polarisation. It is pumped optically (980 or 1480 nm) and is metres long ([Figure 28.7](#fig-28-7)). Erbium-doped waveguides of aluminium oxide or silicon nitride bring the same physics onto chips, with gains of tens of decibels over centimetres reported. SOAs win on size, electrical pumping and wavelength range (any band the semiconductor can be engineered for).

<figure id="fig-28-7">
  <img src="{{ '/assets/figs/ch28_edfa.svg' | relative_url }}" style="width:600px" alt="Left: erbium energy levels: the ground manifold 4I15/2 near 0 eV, 4I13/2 near 0.81 eV with a 10 ms lifetime, and 4I11/2 near 1.27 eV. A 980 nm pump arrow rises to 4I11/2, a dashed arrow shows fast non-radiative decay to 4I13/2, a 1480 nm pump arrow rises into 4I13/2, and a red arrow down to the ground manifold is the 1530 to 1565 nm signal. Right: EDFA block diagram: signal in, isolator, WDM coupler joined by a 980 nm pump laser, a coil of erbium-doped fibre metres long, isolator, amplified signal out.">
  <figcaption><span class="capnum">Figure 28.7.</span> <strong>The erbium-doped fibre amplifier.</strong> (a) Er³⁺ levels in silica: a 980 nm pump lifts ions to <sup>4</sup>I<sub>11/2</sub>, from which they relax quickly to the long-lived <sup>4</sup>I<sub>13/2</sub> (about 10 ms); a 1480 nm pump fills the top of <sup>4</sup>I<sub>13/2</sub> directly; stimulated emission back to the ground manifold amplifies signals from 1530 to 1565 nm. Level energies are the photon energies (980 nm: 1.27 eV, 1530 nm: 0.81 eV); the widths of the manifolds are schematic. (b) An EDFA: a WDM coupler adds the pump to the signal, metres of erbium-doped fibre amplify it, and isolators at both ends block reflections. Drawn by <code>figsrc/ch28_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

A 1 mm SOA gives about 13 dB of small-signal gain, a −3 dB output power near 9 dBm and a noise figure of about 6.5 dB. Longer devices add gain but little output power; the noise figure cannot go below 3 dB. Put boosters where saturation is acceptable, and pre-amplifiers where the noise figure counts.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

No SOA: the budget of [Chapter 1]({% link chapters/01_why.md %}) closes with about 9 dB of margin before penalties ([Chapter 21]({% link chapters/21_pd.md %})) and 5.9 dB after them ([Chapter 38]({% link chapters/38_links.md %}))). An SOA would be the first upgrade for a longer reach or more channels.

</div>

## Reading

{% include reflist.html keys="coldren,salehteich" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- An SOA is an AR-coated, angled laser chip: single-pass gain $$e^{(\Gamma g_0 - \alpha_i)L}$$, saturating as $$1/(1 + P/P_\mathrm{sat})$$.
- A 1 mm example: 13 dB gain, 8.7 dBm output at −3 dB, 6.5 dB noise figure.
- The noise figure cannot beat 3 dB; input coupling loss adds to it directly.
- Fast gain dynamics cause patterning but enable wavelength conversion; facet reflections must be below about 10⁻⁴.
- EDFAs are slower, quieter and polarisation-independent; SOAs are small, electrically pumped and integrable.

</div>

## Check yourself

{% include quiz.html %}
