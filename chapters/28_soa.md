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

Take the gain medium of [Chapter 24]({% link chapters/24_fp.md %}) and remove the feedback: the facets are anti-reflection coated and the waveguide is angled to them. Below the current at which it would lase, light passing through is amplified once and leaves. That is a **semiconductor optical amplifier** (SOA). On a III–V chip, or bonded onto silicon ([Chapter 27]({% link chapters/27_lasersonsi.md %})), it can boost a transmitter, compensate the loss of a long circuit, or raise a weak signal before detection.

## <span class="secnum">28.2</span>Gain and saturation

Along the amplifier, the signal power $$P$$ grows with the net modal gain:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Single-pass gain with saturation</div>

$$\frac{\mathrm{d}P}{\mathrm{d}z} = \left(\frac{\Gamma g_0}{1 + P/P_\mathrm{sat}} - \alpha_i\right)P, \qquad G_0 = e^{(\Gamma g_0 - \alpha_i)L}$$

</div>

At low power the gain is exponential in the length. As the signal grows, stimulated emission consumes carriers faster than the current replaces them, and the local gain falls ([Chapter 22]({% link chapters/22_emission.md %})). The saturation power $$P_\mathrm{sat} = h\nu A/(\Gamma a\tau)$$ is larger for a big mode area $$A$$, a short carrier lifetime $$\tau$$ and a low differential gain $$a$$. The amplifier's usable output is quoted as the **output power at which the gain has dropped by 3 dB**.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 28.1 · A 1 mm SOA</div>

With a small-signal modal gain $$\Gamma g_0 = 35$$ cm⁻¹, $$\alpha_i = 5$$ cm⁻¹, $$L = 1$$ mm and $$P_\mathrm{sat} = 12$$ mW, the small-signal gain is $$e^{30 \times 0.1} = 20$$, or 13.0 dB. Integrating the saturating equation gives a −3 dB output power of 8.7 dBm, reached with about −1.3 dBm in. Doubling the length to 2 mm gives 26 dB of small-signal gain but saturates at a similar output: saturation is set by the end of the amplifier, where the power is highest.

</div>

**Try it.** Change the input power, length, drive and saturation power; the top view shows the light growing and the gain saturating towards the output.

{% include demos/soa.html %}

## <span class="secnum">28.3</span>Noise figure

An amplifier cannot amplify without adding noise. Spontaneous emission in the gain medium is amplified along with the signal (amplified spontaneous emission, ASE), and beats with it at the detector. The **noise figure** compares the signal-to-noise ratio before and after the amplifier:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Noise figure of an optical amplifier</div>

$$F = 2n_{sp}\,\frac{G - 1}{G}\,\frac{\Gamma g}{\Gamma g - \alpha_i} \ \xrightarrow{\ G \gg 1,\ n_{sp} = 1,\ \alpha_i = 0\ }\ 2\ \ (3\ \mathrm{dB})$$

</div>

Even a perfectly inverted amplifier ($$n_{sp} = 1$$) has a 3 dB noise figure: a fundamental quantum limit. Real SOAs have $$n_{sp} \approx 1.5$$–2.5 and internal loss, giving 5–7 dB; the example above gives 6.5 dB. Coupling loss at the input adds directly to the noise figure, decibel for decibel, which is why a pre-amplifier must be coupled efficiently.

## <span class="secnum">28.4</span>Dynamics and patterning

The SOA's gain recovers with the carrier lifetime, from 100 ps to a nanosecond. A long run of "1"s saturates the gain and the following bits see less of it, so the amplified data acquire **pattern-dependent** distortion at gigabit rates, worst when the amplifier is saturated. The same speed is useful: one signal can modulate the gain seen by another (cross-gain modulation), or its phase (cross-phase modulation), for all-optical wavelength conversion and switching. Four-wave mixing in the SOA generates new frequencies.

## <span class="secnum">28.5</span>Polarisation and reflections

Quantum-well gain is polarised (TE for compressive strain, [Chapter 23]({% link chapters/23_gain.md %})), so an SOA fed from a fibre would have polarisation-dependent gain; tensile-strained or mixed-strain wells balance it. On a chip, where the light is already TE, it does not matter.

Reflections matter more. Any residual facet reflectivity turns the SOA into a weak Fabry–Pérot cavity, rippling the gain with wavelength by

$$\frac{G_\mathrm{max}}{G_\mathrm{min}} = \left(\frac{1 + G\sqrt{R_1R_2}}{1 - G\sqrt{R_1R_2}}\right)^2.$$

For 20 dB of gain and 10⁻⁴ reflectivity at each end, the ripple is 0.17 dB; at 10⁻³ it is 1.7 dB, and the amplifier is close to lasing. Anti-reflection coatings alone rarely reach 10⁻⁴, so SOAs combine them with waveguides angled at 7–10° to the facet, the same trick as the edge couplers of [Chapter 16]({% link chapters/16_edge.md %}), and with transparent window regions.

## <span class="secnum">28.6</span>SOAs in photonic circuits

An SOA can sit in three places, each with its own requirement:

- **Booster**, after the laser and modulator: high output power, so it runs saturated. Fine for one channel; for WDM, saturation causes crosstalk between channels.
- **In-line**, to make up for the loss of a long circuit, such as a switch matrix or a phased array: moderate gain, low noise, linear.
- **Pre-amplifier**, before the detector: low noise figure and high gain, unsaturated. It improves receiver sensitivity like an APD ([Chapter 21]({% link chapters/21_pd.md %})), but adds ASE that needs optical filtering.

Each also adds power consumption and heat, and its own temperature drift.

## <span class="secnum">28.7</span>Erbium and other amplifiers

The **erbium-doped fibre amplifier** (EDFA) is the amplifier of long-haul telecom. Its 10 ms excited-state lifetime ([Chapter 22]({% link chapters/22_emission.md %})) makes the gain respond to the average power, not the bits, so there is no patterning and no crosstalk between WDM channels. Its noise figure is close to the 3 dB limit (4–5 dB in practice), and its gain does not depend on polarisation. It is pumped optically (980 or 1480 nm) and is metres long. Erbium-doped waveguides of aluminium oxide or silicon nitride bring the same physics onto chips, with gains of tens of decibels over centimetres reported. SOAs win on size, electrical pumping and wavelength range (any band the semiconductor can be engineered for).

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

A 1 mm SOA gives about 13 dB of small-signal gain, a −3 dB output power near 9 dBm and a noise figure of about 6.5 dB. Longer devices add gain but little output power; the noise figure cannot go below 3 dB. Put boosters where saturation is acceptable, and pre-amplifiers where the noise figure counts.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

No SOA: the budget of [Chapter 1]({% link chapters/01_why.md %}) closes with about 9 dB of margin ([Chapter 21]({% link chapters/21_pd.md %})). An SOA would be the first upgrade for a longer reach or more channels.

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
