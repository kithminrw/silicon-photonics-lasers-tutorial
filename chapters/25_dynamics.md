---
title: "25. Laser Dynamics, Noise and Linewidth"
parent: "Part VI · Lasers and Amplifiers"
nav_order: 25
permalink: /part-6/ch25/
chapter: 25
---

# <span class="chapnum">Chapter 25</span>Laser Dynamics, Noise and Linewidth

A laser's output is never perfectly steady: its intensity and phase fluctuate, and these fluctuations limit links and sensors.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the small-signal modulation response, the relaxation-oscillation frequency and the damping;
- explain chirp and the linewidth-enhancement factor α;
- describe relative intensity noise;
- compute the Schawlow–Townes–Henry linewidth;
- describe the regimes of optical feedback, and how to narrow the linewidth.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How fast can you modulate a laser directly, and how narrow is its line?

</div>

## <span class="secnum">25.1</span>Small-signal modulation

Modulate the current of a laser biased above threshold by a small sinusoid, and linearise the rate equations of [Chapter 24]({% link chapters/24_fp.md %}) around the operating point. The photon density responds like a damped harmonic oscillator {% include cite.html keys="coldren" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Small-signal response of a directly modulated laser</div>

$$H(f) = \frac{f_r^2}{f_r^2 - f^2 + jf\gamma/(2\pi)}, \qquad f_r = \frac{1}{2\pi}\sqrt{\frac{v_g\,a\,S}{\tau_p\,(1 + \varepsilon S)}}, \qquad \gamma = Kf_r^2 + \gamma_0$$

</div>

The **relaxation-oscillation frequency** $$f_r$$ is set by the differential gain $$a = \mathrm{d}g/\mathrm{d}N$$, the photon density $$S$$ and the photon lifetime. Because $$S$$ grows linearly with $$I - I_\mathrm{th}$$, $$f_r$$ grows as $$\sqrt{I - I_\mathrm{th}}$$. Physically, carriers and photons pass energy back and forth: extra carriers raise the gain, which raises the photon density, which burns the carriers down again. The **damping** $$\gamma$$ grows as $$f_r^2$$ through the **K-factor**, $$K = 4\pi^2(\tau_p + \varepsilon/(v_ga))$$, which includes gain compression. The damping eventually flattens and lowers the response, capping the bandwidth near $$2\pi\sqrt{2}/K$$.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 25.1 · How fast is the Chapter 24 laser?</div>

With $$a = 4.6\times10^{-16}$$ cm² at threshold ($$g_0/N_\mathrm{th}$$), $$\tau_p = 2.76$$ ps and $$\varepsilon = 2\times10^{-17}$$ cm³, the laser has $$f_r = 4.7$$ GHz and a 3 dB bandwidth of 7.2 GHz at 50 mA. At 120 mA these are 8.4 and 12.6 GHz. Its K-factor is 314 ps, so no bias can take its bandwidth beyond about 28 GHz. Lasers built for direct modulation at 25–50 Gb/s use quantum wells with several times this differential gain, short cavities and small active volumes.

</div>

## <span class="secnum">25.2</span>Chirp and the α-factor

In a semiconductor, a change of carrier density changes the refractive index as well as the gain ([Chapter 19]({% link chapters/19_eo.md %}) describes the same physics in silicon). The ratio of the two is the **linewidth-enhancement factor**,

$$\alpha = -\frac{4\pi}{\lambda}\,\frac{\mathrm{d}n/\mathrm{d}N}{\mathrm{d}g/\mathrm{d}N},$$

typically 2–6 for quantum-well lasers. Under direct modulation the frequency then follows the power, $$\Delta\nu(t) = \frac{\alpha}{4\pi}\left(\frac{\mathrm{d}\ln P}{\mathrm{d}t} + \kappa P\right)$$: a transient term at the edges of each bit and an adiabatic term that follows the power level. This **chirp** broadens the spectrum. Over dispersive fibre it smears the pulses, which is why directly modulated lasers are confined to short reaches or to the dispersion-free 1310 nm window, and longer links use external modulators ([Chapter 20]({% link chapters/20_modulators.md %})).

## <span class="secnum">25.3</span>Relative intensity noise

Spontaneous emission adds photons with random phases, and the discreteness of carriers and photons adds shot noise. The result is **relative intensity noise**, the power spectral density of the intensity fluctuations normalised to the mean power squared, in dB/Hz. Because the noise sources are filtered by the same laser dynamics, RIN peaks at the relaxation-oscillation frequency and falls at higher power, roughly as $$1/P^3$$ below the peak, until it meets the shot-noise floor $$2h\nu/P$$. Good DFB lasers reach below −150 dB/Hz. Intensity-modulated links need RIN well below the receiver's other noise ([Chapter 21]({% link chapters/21_pd.md %})); analogue and coherent links are more demanding still.

## <span class="secnum">25.4</span>Phase noise and linewidth

Each spontaneous photon that joins the lasing mode adds a small random phase, and the phase random-walks: the laser line has a finite width. Schawlow and Townes derived it for lasers in general; Henry showed that in semiconductors the coupling of gain and index enhances it by $$1 + \alpha^2$$ {% include cite.html keys="henry1982" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Schawlow–Townes–Henry linewidth</div>

$$\Delta\nu = \frac{v_g^2\,h\nu\,\Gamma g_\mathrm{th}\,n_{sp}\,\alpha_m}{8\pi P_0}\,(1 + \alpha^2)$$

</div>

with $$\Gamma g_\mathrm{th} = \alpha_i + \alpha_m$$ the modal gain at threshold, $$P_0$$ the power from one facet of a symmetric laser and $$n_{sp}$$ the population-inversion factor. The linewidth falls as $$1/P_0$$, since each spontaneous photon matters less among more photons. It also falls with lower cavity loss, which means longer photon lifetimes.

**Try it.** Raise the bias, shorten the cavity and change α. The plots show the modulation response, the RIN and the linewidth against power.

{% include demos/dyn.html %}

For the Chapter 24 laser at 6.5 mW per facet, $$n_{sp} = 1.8$$ and $$\alpha = 4$$, the linewidth is 2.1 MHz. Without the α-factor it would be 0.12 MHz, seventeen times narrower. Megahertz linewidths are fine for intensity-modulated links. Coherent links with high-order formats need about 100 kHz or less, FMCW LiDAR needs coherence over its ranging distance ([Chapter 34]({% link chapters/34_apps.md %})), and atomic and quantum applications need hertz.

## <span class="secnum">25.5</span>Optical feedback

Light reflected back into a laser, from a fibre connector, a grating coupler or a chip facet, interferes with the lasing field. Depending on its strength and delay, it can narrow the line slightly, cause mode hopping, or drive the laser into **coherence collapse**, where the linewidth explodes to gigahertz and the RIN rises by tens of decibels. Collapse can begin at feedback levels of about −40 to −30 dB for typical lasers. Fibre-coupled lasers use **optical isolators**, which pass light one way only through the Faraday effect in magnetic garnets; on silicon there is no practical integrated isolator yet. Lasers on chip must therefore tolerate their own reflections: low-reflection couplers ([Chapter 15]({% link chapters/15_gc.md %})), angled facets, quantum-dot gain with its small α-factor, or a deliberately strong, controlled feedback that dominates the stray reflections.

## <span class="secnum">25.6</span>Narrowing the linewidth

The linewidth formula suggests the cures: more photons in the cavity, and lower loss per round trip. An **external cavity**, with the gain chip coupled to a long, low-loss silicon or silicon-nitride waveguide circuit, stores the light for longer. To first order, the linewidth falls with the square of the ratio of the total optical length to the gain section's. Detuning the lasing mode onto the slope of a ring filter adds a further reduction. With high-Q silicon-nitride rings, **self-injection locking**, where the ring's backscatter locks the laser to the ring's resonance, has reached sub-kilohertz fundamental linewidths in chip-scale lasers {% include cite.html keys="xiang2021" %}. These designs are the subject of the next chapter.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

The reference link does not modulate its lasers directly: four continuous-wave lasers at 1550 nm feed ring modulators ([Chapter 20]({% link chapters/20_modulators.md %})), so chirp and relaxation oscillations do not limit it. The requirements on its lasers are RIN below about −140 dB/Hz, and tolerance of the grating couplers' back-reflections ([Chapter 15]({% link chapters/15_gc.md %})).

</div>

## Reading

{% include reflist.html keys="coldren,henry1982,xiang2021" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Direct modulation responds like a damped oscillator: $$f_r \propto \sqrt{I - I_\mathrm{th}}$$, and damping $$Kf_r^2$$ caps the bandwidth near $$2\pi\sqrt{2}/K$$ (28 GHz for the Chapter 24 laser).
- The α-factor couples gain and index: it causes chirp and broadens the linewidth by $$1 + \alpha^2$$.
- RIN peaks at $$f_r$$ and falls with power towards the shot-noise floor.
- Linewidth $$\propto (1 + \alpha^2)/P$$: about 2 MHz for the example laser at 6.5 mW.
- Feedback above about −40 dB can destabilise a laser; long low-loss external cavities and self-injection locking narrow the line by orders of magnitude.

</div>
