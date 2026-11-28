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
- describe the regimes of optical feedback, and how to narrow the linewidth;
- compare lasers by their D- and K-factors, and describe the circuit model a driver designer uses;
- set the bias and modulation currents of a directly modulated laser, trading extinction ratio against turn-on delay, ringing and chirp;
- explain how a laser driver equalises the laser and holds its output constant over temperature;
- compare VCSELs, directly modulated lasers, EMLs and silicon transmitters by bandwidth, chirp, reach, temperature control and energy per bit.

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

A VCSEL reaches such speeds at a few milliamperes ([Figure 25.1](#fig-25-1)). Substituting the steady-state photon density into $$f_r$$ gives $$f_r \approx D\sqrt{I - I_\mathrm{th}}$$, with the **D-factor** $$D = \frac{1}{2\pi}\sqrt{\Gamma v_g a\eta_i/(qV)}$$: the smaller the active volume, the more photons per unit volume each milliampere buys. The VCSEL of [Section 24.8]({% link chapters/24_fp.md %}#248the-vertical-cavity-surface-emitting-laser), with 59 times less volume, has $$D = 6.1$$ GHz/√mA against 0.85 GHz/√mA for the Chapter 24 laser. At 8 mA it has $$f_r = 17.5$$ GHz and a 3 dB bandwidth of 20.7 GHz, including the electrical parasitics of Section 25.8 (25.1 GHz without them). Two effects end the climb. The damping grows as $$Kf_r^2$$, with $$K = 0.23$$ ns for this VCSEL, which caps the bandwidth near 38 GHz. Self-heating acts first: above 12 mA the warm active region loses gain, and $$f_r$$ peaks at 20.2 GHz and falls. At low bias the response is weakly damped: at 1 mA it peaks 10.2 dB high at 5.2 GHz, which matters when the zero level of a modulated laser is set low (Section 25.7).

<figure id="fig-25-1">
  <img src="{{ '/assets/figs/ch25_bw.svg' | relative_url }}" style="width:640px" alt="VCSEL modulation response at four bias currents, relaxation frequency against the square root of current above threshold for the VCSEL and the Fabry-Perot laser, and damping rate against relaxation frequency squared">
  <figcaption><span class="capnum">Figure 25.1.</span> <strong>Bias-dependent bandwidth.</strong> (a) Small-signal response of the VCSEL of Section 24.8 at 1, 2, 4 and 8 mA, including its electrical parasitics: weakly damped and slow at low bias, flatter and faster at high bias. (b) \(f_r\) grows as \(\sqrt{I - I_\mathrm{th}}\), with \(D\) = 6.1 GHz/√mA for the VCSEL and 0.85 GHz/√mA for the Chapter 24 laser; self-heating bends the VCSEL's curve over above 12 mA. (c) Damping rate against \(f_r^2\) between 1 and 8 mA: a straight line whose slope is the K-factor (0.23 ns) and whose intercept is \(\gamma_0\) (2.8 ns⁻¹), the way these parameters are extracted from measurements. Drawn by <code>figsrc/ch2x_lasers.py</code>.</figcaption>
</figure>

## <span class="secnum">25.2</span>Chirp and the α-factor

In a semiconductor, a change of carrier density changes the refractive index as well as the gain ([Chapter 19]({% link chapters/19_eo.md %}) describes the same physics in silicon). The ratio of the two is the **linewidth-enhancement factor**,

$$\alpha = -\frac{4\pi}{\lambda}\,\frac{\mathrm{d}n/\mathrm{d}N}{\mathrm{d}g/\mathrm{d}N},$$

typically 2–6 for quantum-well lasers. Under direct modulation the frequency then follows the power, $$\Delta\nu(t) = \frac{\alpha}{4\pi}\left(\frac{\mathrm{d}\ln P}{\mathrm{d}t} + \kappa P\right)$$: a transient term at the edges of each bit and an adiabatic term that follows the power level ([Figure 25.2](#fig-25-2)). This **chirp** broadens the spectrum. Over dispersive fibre it smears the pulses, which is why directly modulated lasers are confined to short reaches or to the dispersion-free 1310 nm window, and longer links use external modulators ([Chapter 20]({% link chapters/20_modulators.md %})).

<figure id="fig-25-2">
  <img src="{{ '/assets/figs/ch25_chirp.svg' | relative_url }}" style="width:640px" alt="Output power of a directly modulated laser for a 2.5 gigabit per second bit pattern, with overshoot and ringing on each rising edge, and its optical frequency shift: spikes of up to 14 gigahertz at the edges on top of a small step that follows the power level">
  <figcaption><span class="capnum">Figure 25.2.</span> <strong>Chirp of a directly modulated laser.</strong> The Chapter 24 laser driven between 30 and 70 mA at 2.5 Gb/s (25 ps current edges), from the rate equations with \(\alpha\) = 4. (a) Output power per facet (steady levels 2.3 and 10.6 mW) and the drive current (dotted). (b) The optical frequency shift: transient chirp at every edge and through the relaxation ringing, from −8.7 to +14.2 GHz, on top of the adiabatic part (dashed), which follows the power through gain compression and is 2.4 GHz on a 1 and 0.5 GHz on a 0. Drawn by <code>figsrc/ch25_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">25.3</span>Relative intensity noise

Spontaneous emission adds photons with random phases, and the discreteness of carriers and photons adds shot noise. The result is **relative intensity noise**, the power spectral density of the intensity fluctuations normalised to the mean power squared, in dB/Hz. Because the noise sources are filtered by the same laser dynamics, RIN peaks at the relaxation-oscillation frequency and falls at higher power, roughly as $$1/P^3$$ below the peak, until it meets the shot-noise floor $$2h\nu/P$$ ([Figure 25.3](#fig-25-3)). Good DFB lasers reach below −150 dB/Hz. Intensity-modulated links need RIN well below the receiver's other noise ([Chapter 21]({% link chapters/21_pd.md %})); analogue and coherent links are more demanding still.

<figure id="fig-25-3">
  <img src="{{ '/assets/figs/ch25_rin.svg' | relative_url }}" style="width:460px" alt="Relative intensity noise against output power per facet: the peak at the relaxation frequency falls slowly, the low-frequency noise falls as one over power cubed until it meets the shot-noise floor near 5 milliwatts">
  <figcaption><span class="capnum">Figure 25.3.</span> <strong>Intensity noise against power</strong> for the Chapter 24 laser, from the demo's simplified noise model. The noise at low frequency (here 100 MHz) falls by 30 dB per decade of power, as \(1/P^3\) (dashed: the laser's own noise), and meets the shot-noise floor \(2h\nu/P\) of the detected facet (dotted) at 5.2 mW. The peak at the relaxation frequency stays far higher: −131 dB/Hz at 4.7 GHz at 50 mA (6.5 mW per facet), where the low-frequency RIN is −162 dB/Hz with the shot noise. The dash-dotted line is the −140 dB/Hz the reference link asks for. Drawn by <code>figsrc/ch25_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">25.4</span>Phase noise and linewidth

Each spontaneous photon that joins the lasing mode adds a small random phase, and the phase random-walks: the laser line has a finite width. Schawlow and Townes derived it for lasers in general; Henry showed that in semiconductors the coupling of gain and index enhances it by $$1 + \alpha^2$$ {% include cite.html keys="henry1982" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Schawlow–Townes–Henry linewidth</div>

$$\Delta\nu = \frac{v_g^2\,h\nu\,\Gamma g_\mathrm{th}\,n_{sp}\,\alpha_m}{8\pi P_0}\,(1 + \alpha^2)$$

</div>

with $$\Gamma g_\mathrm{th} = \alpha_i + \alpha_m$$ the modal gain at threshold, $$P_0$$ the power from one facet of a symmetric laser and $$n_{sp}$$ the population-inversion factor. The linewidth falls as $$1/P_0$$, since each spontaneous photon matters less among more photons. It also falls with lower cavity loss, which means longer photon lifetimes.

**Try it.** Raise the bias, shorten the cavity and change α. The plots show the modulation response, the RIN and the linewidth against power.

{% include demos/dyn.html %}

For the Chapter 24 laser at 6.5 mW per facet, $$n_{sp} = 1.8$$ and $$\alpha = 4$$, the linewidth is 2.1 MHz. Without the α-factor it would be 0.12 MHz, seventeen times narrower ([Figure 25.4](#fig-25-4)). Megahertz linewidths are fine for intensity-modulated links. Coherent links with high-order formats need about 100 kHz or less, FMCW LiDAR needs coherence over its ranging distance ([Chapter 39]({% link chapters/39_apps.md %})), and atomic and quantum applications need hertz.

<figure id="fig-25-4">
  <img src="{{ '/assets/figs/ch25_linewidth.svg' | relative_url }}" style="width:620px" alt="Lorentzian field spectra 2.1 megahertz and 0.12 megahertz wide, and simulated random walks of the optical phase over one microsecond for the two linewidths, the broader line's phase wandering much faster">
  <figcaption><span class="capnum">Figure 25.4.</span> <strong>Linewidth and phase noise</strong> of the Chapter 24 laser at 6.5 mW per facet. (a) The field spectrum is a Lorentzian: 2.1 MHz wide with \(\alpha\) = 4, against the 0.12 MHz Schawlow–Townes width without the gain–index coupling. (b) What the width means in time: the phase drifts in a random walk whose variance grows as \(2\pi\Delta\nu\,t\) (shaded: ±1 standard deviation). Simulated walks for 2.1 MHz (red) lose the memory of their phase within the coherence time \(1/(\pi\Delta\nu)\) = 154 ns; for 0.12 MHz (blue) it is 2.6 µs. Drawn by <code>figsrc/ch25_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">25.5</span>Optical feedback

Light reflected back into a laser, from a fibre connector, a grating coupler or a chip facet, interferes with the lasing field. Depending on its strength and delay, it can narrow the line slightly, cause mode hopping, or drive the laser into **coherence collapse** ([Figure 25.5](#fig-25-5)), where the linewidth explodes to gigahertz and the RIN rises by tens of decibels. Collapse can begin at feedback levels of about −40 to −30 dB for typical lasers. Fibre-coupled lasers use **optical isolators**, which pass light one way only through the Faraday effect in magnetic garnets (Section 27.10 of [Chapter 27]({% link chapters/27_lasersonsi.md %}) explains why isolators are hard to put on a chip); on silicon there is no practical integrated isolator yet. Lasers on chip must therefore tolerate their own reflections: low-reflection couplers ([Chapter 15]({% link chapters/15_gc.md %})), angled facets, quantum-dot gain with its small α-factor, or a deliberately strong, controlled feedback that dominates the stray reflections.

<figure id="fig-25-5">
  <img src="{{ '/assets/figs/ch25_feedback.svg' | relative_url }}" style="width:620px" alt="A laser sending light to a reflector that returns a fraction of it, and a scale of the fed-back fraction from minus 90 to 0 decibels divided into five regimes: phase-dependent narrowing or broadening, mode hopping, a narrow stable window, coherence collapse from about minus 40 decibels, and stable external-cavity operation above about minus 10 decibels">
  <figcaption><span class="capnum">Figure 25.5.</span> <strong>Regimes of optical feedback.</strong> (a) A reflection anywhere in front of the laser returns a fraction \(f_\mathrm{ext}\) of its output after a round-trip delay. (b) The five regimes classified by Tkach and Chraplyvy for DFB lasers {% include cite.html keys="tkach1986" %}, against the fed-back fraction. Collapse begins at about −40 to −30 dB for typical lasers; a grating coupler on the same chip reflects −20 to −15 dB (<a href="{% link chapters/15_gc.md %}">Chapter 15</a>), so an unprotected on-chip laser can land in regime IV. Only a deliberately strong, well-controlled feedback (regime V, an external cavity) is stable again. The boundaries are approximate: they move with the laser, its α-factor and the distance to the reflector. Drawn by <code>figsrc/ch25_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">25.6</span>Narrowing the linewidth

The linewidth formula suggests the cures: more photons in the cavity, and lower loss per round trip. An **external cavity**, with the gain chip coupled to a long, low-loss silicon or silicon-nitride waveguide circuit, stores the light for longer. To first order, the linewidth falls with the square of the ratio of the total optical length to the gain section's. Detuning the lasing mode onto the slope of a ring filter adds a further reduction. With high-Q silicon-nitride rings, **self-injection locking**, where the ring's backscatter locks the laser to the ring's resonance, has reached sub-kilohertz fundamental linewidths in chip-scale lasers {% include cite.html keys="xiang2021" %}. These designs are the subject of the next chapter.

## <span class="secnum">25.7</span>Driving a laser: bias, modulation and extinction ratio

Above threshold the output follows the current along a straight line, so a directly modulated laser is driven with current. In a **current-mode driver**, a differential pair steers a modulation current $$I_\mathrm{mod}$$ either through the laser or into a dummy load, and a separate source supplies the bias {% include cite.html keys="palermo721l08,sackinger2005" %}. Steering the current, rather than switching it on and off, keeps the supply current constant, so the driver does not shake its own supply. If the modulation current reaches the laser directly (DC coupling), the bias is the zero level: $$I_0 = I_\mathrm{bias}$$ and $$I_1 = I_\mathrm{bias} + I_\mathrm{mod}$$. If it passes through a capacitor (AC coupling), the bias is the average and the levels are $$I_\mathrm{bias} \pm I_\mathrm{mod}/2$$.

A real transmitter never switches the light fully off. The ratio of the two power levels is the **extinction ratio**, and their difference, the **optical modulation amplitude** (OMA), is what the receiver actually sees {% include cite.html keys="palermo721l07,sackinger2005" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Extinction ratio, OMA and the extinction-ratio penalty</div>

$$\mathrm{ER} = \frac{P_1}{P_0}, \qquad \mathrm{OMA} = P_1 - P_0 = 2\bar P\,\frac{\mathrm{ER} - 1}{\mathrm{ER} + 1}, \qquad \mathrm{penalty} = \frac{\mathrm{ER} + 1}{\mathrm{ER} - 1}$$

</div>

A receiver whose sensitivity is quoted as an average power $$\bar P$$ needs more of it when the extinction ratio is finite: 1.1 dB more at an ER of 9 dB, 2.2 dB at 6 dB and 4.8 dB at 3 dB. Many recent link specifications therefore quote the transmitter's OMA and the receiver's OMA sensitivity instead, which removes this bookkeeping {% include cite.html keys="palermo721l07,ieee8023ba" %}.

Why not set the zero level at threshold and take a large extinction ratio? [Figure 25.6](#fig-25-6) shows what goes wrong, for the VCSEL of Section 24.8 driven at 25 Gb/s with its one level at 8 mA, simulated from the rate equations:

- **Turn-on delay.** Below threshold, every 1 must first refill the carriers ([Chapter 24]({% link chapters/24_fp.md %})), which takes $$\tau_d = \tau_n\ln[(I_1 - I_0)/(I_1 - I_\mathrm{th})]$$ {% include cite.html keys="palermo721l08,konnerth1964,coldren" %}. With $$\tau_n = 2.4$$ ns this is 52 ps from $$I_0 = 0$$, longer than the 40 ps bit, and 22 ps from 0.1 mA. The delay depends on how long the laser was dark before, so it turns into data-dependent jitter.
- **Ringing.** Just above threshold the relaxation frequency is low and the damping weak (Figure 25.1a), so each rising edge overshoots and rings for several bits.
- **Chirp.** The transient chirp $$(\alpha/4\pi)\,\mathrm{d}\ln P/\mathrm{d}t$$ is largest when $$P_0$$ is small. With $$\alpha = 4$$, the peak-to-peak frequency swing is 167 GHz at $$I_0 = 0$$, 69 GHz at 2 mA and 24 GHz at 5 mA.

Raising the zero level cures all three, but lowers the extinction ratio and the OMA. In the simulation the eye is closed for $$I_0 \le 0.25$$ mA, opens at 0.5 mA, and is largest, 2.0–2.3 mW, for $$I_0$$ between 0.75 and 2.25 mA (an ER of 11 to 6 dB). Above that it shrinks with the OMA, to 1.3 mW at 5 mA, where the ER is only 2.1 dB. Driving far above threshold buys speed with power {% include cite.html keys="palermo721l08,coldren" %}.

<figure id="fig-25-6">
  <img src="{{ '/assets/figs/ch25_zerolevel.svg' | relative_url }}" style="width:640px" alt="Simulated eye height, extinction ratio and peak-to-peak chirp of a VCSEL at 25 Gb/s against the zero-level current">
  <figcaption><span class="capnum">Figure 25.6.</span> <strong>Choosing the zero level.</strong> The VCSEL of Section 24.8 at 25 Gb/s (PRBS7, one level 8 mA), simulated with its rate equations and parasitics and viewed through a reference receiver of 0.75 × the bit rate. (a) The eye height (inner opening at the best sampling instant; negative means closed) follows the OMA only once the zero level is well above threshold (dotted line); below about 0.5 mA turn-on delay and ringing close the eye. (b) The extinction ratio falls as the zero level rises. (c) So does the transient chirp (α = 4). Drawn by <code>figsrc/ch2x_lasers.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 25.2 · Setting the currents of a 25 Gb/s VCSEL</div>

Choose $$I_0 = 2$$ mA and $$I_1 = 8$$ mA: a DC-coupled driver supplies a 2 mA bias and switches 6 mA, an AC-coupled one a 5 mA bias and ±3 mA. The junction settles at 45 °C, and the levels are $$P_0 = 0.97$$ mW and $$P_1 = 4.15$$ mW: an ER of 4.28 (6.3 dB), an OMA of 3.18 mW and an average of 2.56 mW. A receiver specified by average power pays 2.1 dB for the finite ER. The eye is 2.25 mW high, 71 % of the OMA; the rest is closed by ringing and the finite bandwidth. The laser draws 10.5 mW, and its chirp of 69 GHz peak-to-peak (0.17 nm at 850 nm) is harmless over a hundred metres of multimode fibre, whose own modal dispersion dominates.

</div>

## <span class="secnum">25.8</span>The laser as a circuit, and equalisation

Laser and driver are designed together, so the laser must exist as a circuit element. A **compact model** has three parts {% include cite.html keys="palermo721l08,palermo721l12,mena1999,liang2020" %}. The electrical part is the device's impedance: the bond-pad capacitance, the series resistance of the doped mirrors or cladding, and the junction's capacitance and nonlinear diode, with its turn-on voltage. The optical part is the rate equations, or their small-signal form: a second-order low-pass with $$f_r = D\sqrt{I - I_\mathrm{th}}$$ and damping $$\gamma = Kf_r^2 + \gamma_0$$ {% include cite.html keys="coldren,olshansky1987" %}. A thermal part, a thermal resistance and capacitance driven by the dissipated power, sets the temperature on which the threshold, gain and leakage depend. Written in Verilog-A, such a model runs in the circuit simulator beside the driver's transistors.

Its parameters come from four measurements: the L–I curve gives the threshold and slope efficiency; the V–I curve the turn-on voltage and series resistance; the electrical reflection $$S_{11}$$ over frequency the parasitic network; and the modulation response $$S_{21}$$ at several biases gives $$D$$, $$K$$ and $$\gamma_0$$. Plotting the fitted damping against $$f_r^2$$ gives a straight line, whose slope is $$K$$ and whose intercept is $$\gamma_0$$: 0.23 ns and 2.8 ns⁻¹ for the example VCSEL ([Figure 25.1](#fig-25-1)c). The simulations in this chapter use such a model: a 120 fF pad, 70 Ω of mirror resistance and a 250 fF junction with a diode (ideality 2) in front of the rate equations of Section 24.8, at the junction temperature set by the average dissipated power.

The laser with its parasitics is a low-pass channel that rings, and a channel can be equalised at the transmitter, as electrical serial links do {% include cite.html keys="palermo720l07,dally1997" %}. A **feed-forward equaliser** (FFE, or FIR filter) in the driver sets each bit's current from the bit and its neighbours,

$$I[n] = \frac{I_0 + I_1}{2} + \frac{I_1 - I_0}{2}\sum_k c_k\,d[n - k], \qquad d = \pm 1,$$

with one differential pair per tap, its tail current setting the weight $$c_k$$, all summed at the laser {% include cite.html keys="palermo721l08,rylyakov2012" %}. Choosing $$\sum_k c_k = 1$$ leaves the steady 0 and 1 levels, and hence the extinction ratio and average power, unchanged; the taps reshape only the transitions. Two constraints remain: the total current must stay above threshold, or the turn-on delay returns, and below the current the laser tolerates.

[Figure 25.7](#fig-25-7) shows why this is worth doing. At 5 mA average current (levels of 2 and 8 mA) the 25 Gb/s eye is open, 71 % of the OMA. Lowering the average to 3 mA (1 and 5 mA) cools the junction from 45 to 35 °C, which lengthens the laser's life, but leaves the zero level ringing near 5 GHz, and the eye shrinks to 29 %. A four-tap FIR, $$c = (-0.1, 0.9, 0.1, 0.1)$$ for the bit before, the bit itself and the two after, reopens it to 52 %, with the current staying between 0.6 and 5.4 mA. These taps, the best of a grid search on this model, are not the classic pre-emphasis that boosts every transition. They push the current slightly the wrong way one bit before each transition, then step towards the new level over the next two bits, which cuts the drive by 18 % at 6.25 GHz, near the zero level's relaxation frequency, while passing DC and the 12.5 GHz Nyquist frequency unchanged. The equaliser inverts whatever the laser does. When the laser and its parasitics are too slow rather than ringing, classic pre-emphasis wins: at 40 Gb/s with the 2 and 8 mA levels, the same search returns a negative first post-cursor, $$(-0.1, 1.1, -0.1, 0.1)$$, and lifts the eye from 17 % to 33 % of the OMA.

<figure id="fig-25-7">
  <img src="{{ '/assets/figs/ch25_eyes.svg' | relative_url }}" style="width:660px" alt="Simulated 25 gigabit per second VCSEL eye diagrams at 5 milliamperes average, at 3 milliamperes average, and at 3 milliamperes with a four-tap FIR equaliser">
  <figcaption><span class="capnum">Figure 25.7.</span> <strong>Equalising a VCSEL at 25 Gb/s.</strong> Simulated optical eyes (PRBS7, reference receiver at 0.75 × the bit rate) of the VCSEL of Section 24.8. Left: levels of 2 and 8 mA; the eye opening (arrow) is 71 % of the OMA. Centre: levels of 1 and 5 mA, to save power; the weakly damped zero level closes the eye to 29 %. Right: the same levels with a four-tap FIR in the driver, \(c = (-0.1, 0.9, 0.1, 0.1)\): 52 %. Drawn by <code>figsrc/ch2x_lasers.py</code>.</figcaption>
</figure>

A linear FIR treats rising and falling edges alike, but a laser does not: it rises from the zero level, where it is slow and weakly damped, and falls from the one level, where it is fast. Drivers for VCSELs and directly modulated ring lasers therefore give the edges separate taps, one acting only after rising edges and one only after falling edges, each of either sign {% include cite.html keys="palermo721l12,palermo721l08,ohhata2010,raj2016,fan2019" %}. In the 3 mA case above, a single tap that softens falling edges alone, holding the first 0 after each 1 at 30 % of the swing above the zero level, lifts the eye from 29 % to 46 % of the OMA. For four-level PAM4 signals the levels themselves sit at different biases, and drivers use level-dependent taps or look-up tables. A different, optical cure is **injection locking**: light injected from a master laser locks the laser's frequency and raises its resonance several times above $$f_r$$, extending the bandwidth of lasers that are slow on their own {% include cite.html keys="palermo721l12,lau2009,chrostowski2006,fan2020" %}.

## <span class="secnum">25.9</span>Output stages and temperature control

**The output stage.** The driver's output transistors must stay saturated above the laser's forward voltage, 2.2 V for the VCSEL at 8 mA, so laser drivers in CMOS use thick-oxide transistors on a higher supply than the logic, or a separate driver chip {% include cite.html keys="palermo721l08" %}. A laser at the end of a bond wire or a short line is a poor impedance match, so the driver usually terminates the line with an on-chip resistor that absorbs reflections. That resistor also takes current {% include cite.html keys="sackinger2005,galal2003" %}: a 50 Ω termination beside a laser with 80 Ω of differential resistance passes only 38 % of the modulation current to the laser, so 6 mA of modulation needs 15.6 mA from the driver. **Active back-termination**, which drives the far end of the termination resistor with a replica of the output so that no signal current flows in it, and **voltage-mode** drivers recover most of that waste {% include cite.html keys="palermo721l08,palermo720l05,morley2005,tsai2008" %}. Inductive peaking {% include cite.html keys="mohan2000" %} and a continuous-time equaliser in the output stage extend the bandwidth further.

**Temperature.** As a laser warms, its threshold rises ([Chapter 24]({% link chapters/24_fp.md %})) and its slope efficiency falls. A driver holds the average power with **automatic power control** (APC): a monitor photodiode, on an edge emitter's rear facet or a tap, feeds a slow loop that sets the bias {% include cite.html keys="sackinger2005" %}. That fixes $$\bar P$$ but not the extinction ratio, so the modulation current must also follow the slope efficiency, either from a look-up table indexed by a temperature sensor or by a second loop that measures the modulation amplitude in the monitor photocurrent. The same loop hides a laser's ageing as a slowly rising current, which is how its end of life is usually defined ([Chapter 27]({% link chapters/27_lasersonsi.md %}), Section 27.9).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 25.3 · Holding the light constant from 25 to 85 °C</div>

**The Chapter 24 laser.** For $$P_0 = 1$$ mW and $$P_1 = 5$$ mW per facet (ER 7 dB) at 25 °C, the currents are 24.0 and 43.1 mA ($$I_\mathrm{mod}$$ = 19.1 mA). At 85 °C the threshold is 52.2 mA, so the same powers need 57.0 and 76.1 mA. Without APC, both of the old currents would sit below the hot threshold and the laser would go dark. In this model the slope efficiency does not change with temperature, so APC alone, moving the bias by 33 mA, restores both levels.

**The VCSEL.** For $$P_0 = 0.8$$ mW and $$P_1 = 3.2$$ mW (an average of 2 mW, ER 6 dB), the currents are 1.68 and 6.20 mA at 25 °C ambient, with the junction at 39 °C. At 85 °C ambient the junction reaches 103 °C; the threshold has moved only from 0.17 to 0.26 mA, but leakage has cut the slope from 0.53 to 0.46 W/A. The currents become 2.00 and 7.21 mA: the modulation current must grow 15 %, from 4.52 to 5.21 mA. With APC alone, holding 2 mW average but leaving $$I_\mathrm{mod}$$ at its 25 °C value, the extinction ratio drops from 6.0 to 5.0 dB.

</div>

**Modulator drivers.** External modulators need voltage rather than current: the travelling-wave electrode of a Mach–Zehnder modulator is a terminated line that needs a swing of volts, and a ring modulator is a small capacitor ([Chapter 20]({% link chapters/20_modulators.md %})). Their drivers are voltage-mode circuits, and the laser behind them needs only the bias half of a laser driver.

## <span class="secnum">25.10</span>Laser transmitters compared: VCSELs, DMLs and EMLs

The dynamics of this chapter decide which transmitter a link can use. Three laser transmitters carry most intensity-modulated links ([Figure 25.8](#fig-25-8)). A **VCSEL** and a **directly modulated laser** (DML) put the data on the laser's own current; an **electro-absorption modulated laser** (EML) keeps its laser on and switches the light in a modulator on the same chip. A silicon-photonics transmitter does the same as an EML with separate parts: a continuous-wave laser in front of a silicon Mach–Zehnder or ring modulator ([Chapter 20]({% link chapters/20_modulators.md %})).

<figure id="fig-25-8">
  <img src="{{ '/assets/figs/ch25_tx_devices.svg' | relative_url }}" style="width:680px" alt="Five drawings. (a) Cross-section of an oxide-aperture VCSEL, 24 micrometres across, with its 34-pair and 20-pair Bragg mirrors, cavity, oxide aperture, ring contact and current paths, light leaving upwards. (b) Side view of a 150 micrometre DFB laser with an HR rear facet, an AR front facet, quantum wells and a grating, driven by a bias plus data current, emitting light with coloured, chirped edges. (c) Side view of an EML: a 300 micrometre DFB section with a grating and DC current, a 50 micrometre isolation section with a trench in the upper cladding, and a 100 micrometre electro-absorption modulator with a reverse bias plus data voltage. (d) Top view of the EML chip, 450 by 250 micrometres, with a large DFB bond pad, a small EAM pad and an off-chip 50 ohm termination. (e) Schematic of a silicon transmitter: a CW laser feeding a Mach-Zehnder modulator with travelling-wave electrodes, a 50 ohm termination and a grating coupler.">
  <figcaption><span class="capnum">Figure 25.8.</span> <strong>Three laser transmitters and a silicon one.</strong> (a) The VCSEL of Section 24.8: widths to scale, heights doubled; the current (dashed) is funnelled through the 6 µm oxide aperture and modulates the light leaving the top. (b) A DML: a 150 µm DFB laser, the model of Worked Example 25.4, whose current carries both bias and data; its output is chirped, blue-shifted on rising edges and red-shifted on falling ones (Section 25.2). (c) An EML: a DFB section runs continuously and an electro-absorption modulator (EAM) on the same InP chip switches the light; the EAM's quantum wells, grown with a wider band gap by butt-joint regrowth or selective-area growth {% include cite.html keys="aoki1993,li2025eml" %}, absorb when a reverse field shifts their absorption edge (QCSE, <a href="{% link chapters/19_eo.md %}">Chapter 19</a>). A trench in the upper cladding isolates the two contacts. (d) The EML from above: a small EAM pad keeps the capacitance low, and a 50 Ω resistor beside the chip terminates the drive line. (b)–(d) Lengths to scale (the ridge in (d) drawn three times wider); layer thicknesses in (b) and (c) not to scale; dimensions illustrative. (e) A silicon transmitter (schematic): a CW laser, a travelling-wave MZM (Figure 20.2) or a ring (Figure 20.3), and a grating coupler. Drawn by <code>figsrc/ch25_tx.py</code>.</figcaption>
</figure>

**The VCSEL.** A VCSEL is modulated through its current like any laser in Sections 25.1 and 25.7, but its tiny volume makes it fast for little current: the design of Section 24.8 has $$D = 6.1$$ GHz/√mA, reaches 20.7 GHz at 8 mA and runs at 25 Gb/s on 10.5 mW (Worked Example 25.2). It emits 850 nm light from its surface into multimode fibre, whose modal dispersion limits the reach to a few hundred metres (Section 24.8): IEEE 802.3 specifies 10GBASE-SR at 10.3 GBd for 300 m of OM3 and 400 m of OM4 fibre, and 25GBASE-SR and the four-lane 100GBASE-SR4 at 25.8 GBd for 70 and 100 m {% include cite.html keys="ieee8023,larsson2011,tatum2015" %}. Because VCSELs are tested on the wafer and sit side by side at the pitch of a fibre ribbon, parallel links such as 100GBASE-SR4 use arrays of them. At 1310 and 1550 nm a VCSEL needs mirrors that InP-based materials provide poorly; wafer-fused GaAs mirrors on InP active regions have reached 13 GHz and 37 Gb/s at 1550 nm {% include cite.html keys="babichev2023" %}, but long-wavelength VCSELs remain rare in data links.

**The DML.** An edge-emitting laser modulated through its current is a DML: a DFB laser ([Section 26.2]({% link chapters/26_tunable.md %}#262dfb-lasers)) for single-mode fibre, or a cheaper Fabry–Pérot laser where a few nanometres of spectrum do not matter. Its active volume is 10 to 60 times a VCSEL's, so it needs tens of milliamperes. The DML of this section is a 150 µm DFB laser built for speed, simulated with the rate equations of Section 24.3: six 6 nm strained quantum wells with $$g_0 = 2400$$ cm⁻¹, an effective mirror loss of 35 cm⁻¹ (grating and HR-coated rear facet), the gain compression of the Chapter 24 laser, and $$\alpha = 3$$. Its differential gain at threshold is $$1.0\times10^{-15}$$ cm², twice the Chapter 24 laser's, and its active volume, $$8.1\times10^{-12}$$ cm³, five times smaller, so $$D = 3.0$$ GHz/√mA and $$K = 0.195$$ ns. Driven between 20 and 60 mA, it has $$f_r$$ = 12.6 and 21.7 GHz at the two levels, an extinction ratio of 5.1 dB and 15.0 mW of average output. Its chirp is that of Section 25.2: its frequency swings 40 GHz peak to peak at 10 Gb/s and 62 GHz at 25 Gb/s, mostly in transient spikes at the edges, and an adiabatic step of 8.2 GHz, or 66 pm at 1550 nm, separates the two levels. Research DMLs that exploit a second, photon–photon resonance and detuned loading have passed 65 GHz of bandwidth with reduced chirp {% include cite.html keys="matsui2021" %}.

A DFB's wavelength drifts by about 0.1 nm/K (Section 26.2), 7 nm over a case temperature of 0–70 °C. That fits inside the 13 nm window of each lane of the 100G CWDM4 MSA, whose four lanes sit 20 nm apart from 1271 to 1331 nm {% include cite.html keys="cwdm4msa" %}, so CWDM transmitters can run uncooled. The four LAN-WDM lanes of 100GBASE-LR4, about 4.5 nm apart near 1300 nm, are each only about 2.1 nm wide (2.06–2.10 nm) {% include cite.html keys="ieee8023" %}: a DFB crosses the narrowest in 21 K, so such transmitters hold their lasers' temperature.

**The EML.** An EML separates the jobs. The DFB section runs at a constant current, so its frequency, power and linewidth stay put, and the electro-absorption modulator of [Section 20.4]({% link chapters/20_modulators.md %}#204electro-absorption-modulators) does the switching. The EAM is a reverse-biased PIN diode, and its speed is set by its capacitance and its carriers, not by any resonance:

- **Capacitance.** A 100 µm × 2 µm junction with a 0.3 µm intrinsic region ($$\varepsilon_r = 12.4$$) has $$C_j = \varepsilon_0\varepsilon_rA/d = 73$$ fF; with a 40 fF pad, 113 fF. Driven from 50 Ω, its RC bandwidth is $$1/(2\pi RC) = 28$$ GHz; a 50 Ω resistor in parallel with the modulator, which also terminates the line, halves the resistance the capacitance sees and doubles that to 56 GHz.
- **Carriers.** Each absorbed photon leaves an electron and a hole that must escape the wells and cross the intrinsic region, in 3 ps for electrons and 6 ps for holes at their saturated velocities, a limit near 70–150 GHz. At high optical power the slow holes pile up and screen the field, which compresses the extinction and slows the response; wells designed for fast hole escape reduce the pile-up {% include cite.html keys="aoki1993" %}.

Reported EMLs reach 3 dB bandwidths from about 30 to above 100 GHz with short or travelling-wave modulators, low-capacitance pads and peaking {% include cite.html keys="li2025eml" %}. The EAM chirps too, because a change of absorption comes with a change of index. Koyama and Iga described it with a modulator α-parameter, $$\Delta\nu = (\alpha_\mathrm{EAM}/4\pi)\,\mathrm{d}\ln P/\mathrm{d}t$$, the transient term of Section 25.2 without the adiabatic one {% include cite.html keys="koyama1988" %}. For an EAM, $$\alpha_\mathrm{EAM}$$ is small and depends on where the laser line sits on the absorption edge, and so on the bias: near the absorption peak it is close to zero or even negative, in the tail it can approach +2 {% include cite.html keys="piprek2002" %}. A negative value helps over anomalous fibre. The price is temperature. The absorption edge follows the band gap, about 0.5 nm/K like the gain peak of Section 24.5, while the DFB line moves 0.1 nm/K; their separation changes by 0.4 nm/K, 28 nm over 70 K, which changes the extinction and the insertion loss. Most EMLs therefore sit on a thermoelectric cooler (TEC), and uncooled EMLs need modulators designed for a wide range of detuning {% include cite.html keys="li2025eml" %}.

**Silicon and lithium niobate.** A silicon transmitter is an EML taken apart: the laser is a separate or bonded chip ([Chapter 27]({% link chapters/27_lasersonsi.md %})), and the modulator is a push–pull MZM, with no chirp, or a ring, with a little ([Chapter 20]({% link chapters/20_modulators.md %})). One laser can feed several modulators, and rings multiplex wavelengths as they modulate, as in the reference link. For coherent links, IQ modulators in InP, silicon or thin-film lithium niobate write amplitude and phase ([Section 38.4]({% link chapters/38_links.md %})); the 400ZR implementation agreement, for example, carries 400 Gb/s as dual-polarisation 16-QAM at about 60 GBd over amplified DWDM links of up to 120 km {% include cite.html keys="oif400zr" %}.

[Table 25.1](#tab-25-1) collects what separates the four.

**Table 25.1. Four transmitters at a glance (numbers from this tutorial's examples).**
{: .tabcaption #tab-25-1 }

| | VCSEL | DML | EML | Silicon MZM or ring |
|---|---|---|---|---|
| Data carried by | laser current | laser current | EAM voltage; laser on DC | modulator voltage; laser on DC |
| Bandwidth set by | $$f_r$$, damping, parasitics: 20.7 GHz at 8 mA | $$f_r$$ and damping: $$f_r$$ = 12.6–21.7 GHz here | EAM capacitance and carrier escape: 28–56 GHz here | MZM: RF loss, about 30–50 GHz; ring: photon lifetime and RC (Ch 20) |
| Chirp | transient and adiabatic | transient and adiabatic: 40 GHz peak to peak at 10 Gb/s | transient only; $$\alpha_\mathrm{EAM}$$ from slightly negative to about +2, set by the bias | none (push–pull MZM), small (ring) |
| Extinction ratio | 6.3 dB (Worked Example 25.2) | 5.1 dB here | 10 dB in this section's model | 6.3 dB (MZM), 4 dB (ring), Ch 20 |
| Wavelength and fibre | 850 nm, multimode | O band (or C band), single-mode | O or C band, single-mode | O or C band, single-mode |
| Temperature | uncooled; mode drifts 0.065 nm/K | uncooled for CWDM; 0.1 nm/K | usually on a TEC | heaters hold the MZM bias or the ring |
| Making and packaging | tested on the wafer; arrays; round beam | cleaved and tested in bars; lens into single-mode fibre | larger chip, TEC and package | wafer-scale circuits; laser attach and fibre coupling (Ch 17, 27) |

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 25.4 · How far does a chirped laser reach?</div>

Send the DML above and an EML through standard fibre, and compare them with a chirp-free modulator. The DML's field comes from its rate equations with the chirp of Section 25.2; the EAM's power switches between −3 and −13 dB of the CW laser's (10 dB extinction) behind its 56 GHz RC pole, with $$\alpha_\mathrm{EAM} = +0.5$$ or −0.5; the chirp-free case, $$\alpha = 0$$, is what a push–pull MZM approaches. The fibre is an all-pass filter on the field, $$\exp(-j\beta_2\omega^2L/2)$$, with $$\beta_2 = -D\lambda^2/(2\pi c)$$, −21.7 ps²/km at 17 ps/(nm·km) ([Chapter 3]({% link chapters/03_gaussian.md %})) {% include cite.html keys="agrawal2021" %}. A reference receiver, a fourth-order Bessel filter at 0.75 times the bit rate, ends the link, and the penalty is the closure of the eye's height relative to back-to-back, the ISI penalty of [Chapter 38]({% link chapters/38_links.md %}). Taking 1 dB as the limit ([Figure 25.9](#fig-25-9)):

- **At 10 Gb/s and 1550 nm**, the DML reaches 252 ps/nm, or 15 km. The EML with $$\alpha_\mathrm{EAM} = +0.5$$ reaches 673 ps/nm (40 km), the chirp-free modulator 994 ps/nm (58 km), and the EML with $$\alpha_\mathrm{EAM} = -0.5$$ 1473 ps/nm (87 km), because its chirp first compresses the pulses. At a 2 dB limit the four reach 32, 50, 74 and 109 km.
- **At 25 Gb/s** all shrink: 34, 105, 157 and 230 ps/nm, or 2.0, 6.2, 9.2 and 13.5 km at 1550 nm. The chirp-free tolerance scales as $$1/B^2$$: 157 ps/nm × (25/10)² = 982 ps/nm, against 994 ps/nm at 10 Gb/s, at the low end of the 1000–1600 ps/nm of [Worked Example 2.5]({% link chapters/02_em.md %}). The same model puts the reference link's 34 ps/nm at 50 Gb/s at about 0.5 dB (0.47 dB for an ideal chirp-free transmitter), the 0.5 dB that [Table 38.1]({% link chapters/38_links.md %}#tab-38-1) allows.
- **In the O band** the same 25 Gb/s DML hardly notices the fibre. With the zero-dispersion wavelength anywhere between 1300 and 1324 nm and a slope of 0.093 ps/(nm²·km), as IEEE 802.3 and the CWDM4 MSA assume {% include cite.html keys="ieee8023,cwdm4msa" %}, 2 km accumulate −11.9 to +6.7 ps/nm across the CWDM4 lanes, and 10 km at 1310 nm at most 13 ps/nm: penalties of 0.1 dB. Even 10 km at the 1264.5 nm edge of the lowest lane (−59 ps/nm) cost only 0.7 dB.

Why the DML fails first {% include cite.html keys="koch1984,agrawal2021" %}: its rising edges are blue-shifted and its falling edges red-shifted, and at 1550 nm blue light travels faster. Each 1 spreads into its neighbours, and on top, runs of ones, 66 pm bluer than runs of zeros, arrive $$66\ \mathrm{pm}\times425\ \mathrm{ps/nm} = 28$$ ps earlier after 25 km, more than a quarter of a 100 ps bit. Below the zero-dispersion wavelength the signs reverse, and the 10 Gb/s DML tolerates −549 ps/nm; at 25 Gb/s its steep, strongly chirped edges limit it on both sides (1 dB at −56 and +34 ps/nm). This is why DMLs live in the O band, and why longer reaches at 1550 nm call for EMLs or MZMs.

</div>

<figure id="fig-25-9">
  <img src="{{ '/assets/figs/ch25_tx_dispersion.svg' | relative_url }}" style="width:680px" alt="Three 10 gigabit per second eye diagrams: the DML back to back, the DML after 25 kilometres at 1550 nanometres with a 1.4 dB penalty, and the EML after 25 kilometres with 0.2 dB. Below, dispersion penalty against accumulated dispersion at 10 and 25 gigabits per second for the DML, the EML with alpha plus and minus 0.5, and a chirp-free modulator, with a 1 dB line and a top axis in kilometres at 1550 nanometres.">
  <figcaption><span class="capnum">Figure 25.9.</span> <strong>Chirp against dispersion.</strong> (a)–(c) Eyes at 10 Gb/s through the reference receiver (0.75 × the bit rate), each scaled to its own levels: the DML of Worked Example 25.4 back to back and after 25 km at 1550 nm (425 ps/nm), where its chirp costs 1.4 dB; the EML with \(\alpha_\mathrm{EAM}\) = +0.5 loses 0.2 dB over the same fibre. (d), (e) Eye-closure penalty against accumulated dispersion at 10 and 25 Gb/s; the top axis converts to kilometres at 17 ps/(nm·km). The DML is limited first, the EML with a small positive α next; a chirp-free modulator (black) and a negatively chirped EAM (blue), which pre-compresses the pulses, go furthest. The scales of (e) are those of (d) divided by 6.25, so equal shapes mean the \(1/B^2\) scaling of dispersion. Each curve ends where it first passes 2.5 dB; the penalty counts the loss of eye height only, not of eye width. Rate equations, EAM, fibre and receiver models in <code>figsrc/ch25_tx.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 25.5 · Energy per bit of five transmitters at 25 Gb/s</div>

Count the electrical power of each transmitter at 25 Gb/s NRZ, using the tutorial's own devices where it has them ([Figure 25.10](#fig-25-10)). Drivers are modelled the same way for all: a current-mode output stage on a 3.3 V supply with a matched back-termination (Section 25.9) {% include cite.html keys="sackinger2005,palermo721l08" %}. Serialisers, clocks and pre-drivers, common to all, are left out.

- **VCSEL** (Worked Example 25.2): the laser takes 10.5 mW. Its driver supplies 2 mA of bias and steers 15.6 mA, of which the 50 Ω termination takes the share that leaves 6 mA for the laser (Section 25.9): 58 mW in all, or 2.3 pJ/bit; the laser alone is 0.42 pJ/bit.
- **DML** (20 and 60 mA, a forward voltage of $$0.9\ \mathrm{V} + 5\ \Omega\times I$$): 46 mW in the laser. With a 20 Ω series resistor matching it to a 25 Ω line and a 25 Ω back-termination, only half the switched current reaches the laser, so the driver steers 80 mA plus 20 mA of bias: 330 mW, 13.2 pJ/bit.
- **EML**: the DFB section at 60 mA draws 72 mW and sends 22.9 mW into the EAM. A 2 Vpp swing across the EAM's 50 Ω termination dissipates $$V_{pp}^2/(4R) = 20$$ mW ([Chapter 20]({% link chapters/20_modulators.md %})), and the back-terminated driver needs $$2\ \mathrm{V}/25\ \Omega = 80$$ mA, 264 mW. The absorbed light becomes photocurrent, 12 mA in a 1 at 0.5 V of reverse bias and 23 mA in a 0 at 2.5 V: another 32 mW. At a 70 °C case, a TEC holding the chip at 45 °C, its hot side 5 K above the case, must pump the 117 mW that all this deposits on it; the best coefficient of performance a Bi₂Te₃ cooler ($$ZT \approx 0.8$$) can reach across 30 K is 1.1 {% include cite.html keys="goldsmid2016" %}, so the cooler draws at least 105 mW (none at 25 °C). Total: 473 mW, 18.9 pJ/bit.
- **Silicon MZM** (Worked Example 20.1): the CW laser for +10 dBm in the waveguide at 15 % wall-plug efficiency draws 66.7 mW ([Section 38.5]({% link chapters/38_links.md %}#385energy-per-bit)); the 50 Ω termination and its driver are the EML's, 264 mW; the bias heater averages half of $$P_\pi$$, 13 mW ([Chapter 18]({% link chapters/18_thermal.md %})). Total: 344 mW, 13.7 pJ/bit.
- **Silicon ring** (Worked Example 20.2): the same laser, 20 fJ/bit in the ring (0.5 mW), a CMOS driver at the typical 0.5 pJ/bit of Table 38.1 (12.5 mW) and up to 20 mW of heater: 100 mW, 4.0 pJ/bit.

The drivers of 50 Ω loads dominate: 244–284 mW of the DML's, EML's and MZM's totals. Without them the ranking is the lasers' own: 0.4 pJ/bit for the VCSEL, 1.8 for the DML, 3.5 for the ring, 4.0 for the MZM and 9.1 for the cooled EML. Segmented MZMs and modulators driven directly from CMOS avoid the 50 Ω interface, and uncooled EMLs drop the TEC. The transmitters do not launch the same light either: 2.6 mW average into multimode fibre for the VCSEL, 15 mW from the DML chip, 6.3 mW from the EML chip, and +0.7 dBm (MZM) or +3.2 dBm (ring, Table 38.1) into fibre after a grating coupler. And most of these powers barely depend on the bit rate: run the same EML at 53 GBd with PAM4, 106 Gb/s, and if its driver's power stayed the same, its energy per bit would fall about four-fold ([Section 38.11]({% link chapters/38_links.md %})).

</div>

<figure id="fig-25-10">
  <img src="{{ '/assets/figs/ch25_tx_energy.svg' | relative_url }}" style="width:640px" alt="Stacked horizontal bars of energy per bit at 25 gigabits per second for five transmitters: VCSEL 2.3, DML 13.2, cooled EML 18.9, silicon MZM 13.7 and silicon ring 4.0 picojoules per bit, divided into laser, modulator load, driver overhead and TEC or heater.">
  <figcaption><span class="capnum">Figure 25.10.</span> <strong>Where a transmitter's power goes</strong>, at 25 Gb/s NRZ, for the assumptions of Worked Example 25.5: lasers (blue), what the modulator itself dissipates (termination, ring switching, EAM photocurrent; teal), the rest of the driver's output stage on a 3.3 V supply with matched back-termination (hatched, an estimate), and the TEC at a 70 °C case or the silicon heaters (red). The bars compare architectures, not products: real drivers, bias points and launch powers differ. Drawn by <code>figsrc/ch25_tx.py</code>.</figcaption>
</figure>

**Where each is used.** [Figure 25.11](#fig-25-11) places Ethernet's optical interfaces, and two others, by symbol rate and reach. The standards specify the optical interface (wavelength, power, extinction, dispersion and the transmitter penalty), not the device; the transmitters named here are the common implementations {% include cite.html keys="palermo721l01,tatum2015,li2025eml" %}:

- **Up to a few hundred metres of multimode fibre**, VCSEL links: 10GBASE-SR, 25GBASE-SR and, with arrays, 100GBASE-SR4 {% include cite.html keys="ieee8023" %}.
- **Up to about 10 km in the O band at 10–26 GBd**, DMLs: 10GBASE-LR and 25GBASE-LR at 1310 nm, the CWDM4 MSA's 2 km, uncooled, and 100GBASE-LR4's 10 km, with the lasers' temperature held for its narrow lanes {% include cite.html keys="ieee8023,cwdm4msa" %}. There the dispersion is too small to punish the chirp (Worked Example 25.4). EMLs and silicon MZMs serve some of these links too.
- **Faster or longer**: at 53 GBd PAM4 (100 Gb/s per lane, 100GBASE-DR, FR1, LR1 and 400GBASE-DR4, FR4, LR4-6), EMLs and silicon MZMs, whose bandwidth does not cost current and whose chirp is small; and at 1550 nm, where 10GBASE-ER reaches 40 km on engineered links, EMLs.
- **Beyond tens of kilometres of DWDM**, coherent transceivers with IQ modulators, where digital signal processing undoes the dispersion ([Chapter 38]({% link chapters/38_links.md %})).

The lines in Figure 25.11 are the 1 dB reach of a chirp-free NRZ transmitter from Worked Example 25.4, scaled as $$1/B^2$$ to three fibre dispersions. At 53 GBd they give 2.1 km at 1550 nm, 5.9 km on the worst CWDM lane and 27 km at 1310 nm, before any chirp is counted: consistent with the four-wavelength 100 Gb/s-per-lane links stopping at 2 and 6 km while the single-wavelength one at 1311 nm reaches 10 km.

<figure id="fig-25-11">
  <img src="{{ '/assets/figs/ch25_tx_map.svg' | relative_url }}" style="width:680px" alt="Log-log map of reach against symbol rate per lane, from 2 to 130 gigabaud and 30 metres to 300 kilometres, with Ethernet interfaces as markers: multimode 850 nanometre links at 70 to 400 metres, O-band single-mode links at 500 metres to 10 kilometres, 10GBASE-ER at 40 kilometres and 400ZR at 120 kilometres, and three falling lines for the chirp-free dispersion limit at 1550 nanometres, on the worst CWDM lane and at 1310 nanometres.">
  <figcaption><span class="capnum">Figure 25.11.</span> <strong>Where each transmitter is typically used.</strong> Markers: reach against symbol rate per lane for IEEE 802.3 interfaces {% include cite.html keys="ieee8023" %} (10GBASE-SR, 300 m on OM3 to 400 m on OM4; 25GBASE-SR and 100GBASE-SR4, 70–100 m; 10GBASE-LR, 25GBASE-LR and 100GBASE-LR4, 10 km; 10GBASE-ER, 40 km on engineered links; 100GBASE-DR and 400GBASE-DR4, 500 m; 100GBASE-FR1 and 400GBASE-FR4, 2 km; 400GBASE-LR4-6, 6 km; 100GBASE-LR1, 10 km), the 100G CWDM4 MSA (2 km) {% include cite.html keys="cwdm4msa" %} and the OIF 400ZR coherent interface (up to 120 km) {% include cite.html keys="oif400zr" %}. Open markers are PAM4. Grey text: the transmitters commonly used there; the standards do not prescribe them. Lines: the 1 dB dispersion limit of chirp-free NRZ from Worked Example 25.4 (935 ps/nm at 10.3 GBd, scaled as \(1/B^2\)) at 17 ps/(nm·km), on the 1264.5 nm edge of the CWDM band (5.9 ps/(nm·km)) and at 1310 nm (1.3 ps/(nm·km)), both for the worst-case fibre of IEEE 802.3; PAM4 tolerates somewhat less, and chirp less again. Coherent links undo dispersion digitally and are not bound by these lines. Drawn by <code>figsrc/ch25_tx.py</code>.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

- Up to a few hundred metres of multimode fibre: VCSELs, alone or in arrays, at the lowest energy and cost; their bandwidth costs current, and their reach is set by the fibre's modes.
- Single-mode, up to 2–10 km in the O band at 10–26 GBd: DMLs, uncooled on a 20 nm CWDM grid; their chirp is harmless where the dispersion is near zero.
- At 1550 nm, or at 50 GBd and beyond: a low-chirp transmitter, an EML (cooled, unless designed for a wide temperature range) or a silicon or lithium-niobate MZM. A negative $$\alpha_\mathrm{EAM}$$ adds reach on anomalous fibre.
- Many wavelengths on one chip, or co-packaged optics: a CW laser with silicon modulators, rings where energy matters most (Chapter 38).
- Dense WDM over tens of kilometres and more: coherent IQ transmitters.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

The reference link does not modulate its lasers directly: four continuous-wave lasers at 1550 nm feed ring modulators ([Chapter 20]({% link chapters/20_modulators.md %})), so chirp and relaxation oscillations do not limit it. The requirements on its lasers are RIN below about −140 dB/Hz, and tolerance of the grating couplers' back-reflections ([Chapter 15]({% link chapters/15_gc.md %})). Each needs only a constant current under automatic power control (Section 25.9).

</div>

## Reading

{% include reflist.html keys="coldren,henry1982,xiang2021,palermo721l07,palermo721l08,palermo721l12,palermo720l07,palermo720l05,agrawal2021,larsson2011,li2025eml" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Direct modulation responds like a damped oscillator: $$f_r \propto \sqrt{I - I_\mathrm{th}}$$, and damping $$Kf_r^2$$ caps the bandwidth near $$2\pi\sqrt{2}/K$$ (28 GHz for the Chapter 24 laser).
- The α-factor couples gain and index: it causes chirp and broadens the linewidth by $$1 + \alpha^2$$.
- RIN peaks at $$f_r$$ and falls with power towards the shot-noise floor.
- Linewidth $$\propto (1 + \alpha^2)/P$$: about 2 MHz for the example laser at 6.5 mW.
- Feedback above about −40 dB can destabilise a laser; long low-loss external cavities and self-injection locking narrow the line by orders of magnitude.
- $$f_r = D\sqrt{I - I_\mathrm{th}}$$ with $$D \propto 1/\sqrt{V}$$: 6.1 GHz/√mA for the example VCSEL against 0.85 for the edge emitter. A compact model (parasitics, rate equations or $$D$$, $$K$$, $$\gamma_0$$, a thermal node) lets laser and driver be simulated together.
- ER = $$P_1/P_0$$ and OMA = $$P_1 - P_0$$; an average-power receiver pays $$(\mathrm{ER}+1)/(\mathrm{ER}-1)$$, 2.2 dB at 6 dB. A zero level near threshold brings turn-on delay (52 ps from 0 mA), ringing and chirp (167 GHz peak-to-peak); a high one wastes ER. The 25 Gb/s VCSEL eye is best for zero levels of 0.75–2.25 mA.
- A FIR equaliser in the driver must invert the laser's own response: at 3 mA average it reopened the VCSEL's eye from 29 % to 52 % of the OMA. Rising and falling edges need different taps.
- APC tracks the threshold with the bias; the modulation current must also track the slope efficiency (+15 % for the VCSEL from 25 to 85 °C), or the extinction ratio falls.
- VCSELs serve multimode links up to a few hundred metres, DMLs the O band, EMLs and MZMs longer or faster links. At 1550 nm and a 1 dB penalty, the example DML reaches 15 km at 10 Gb/s and 2 km at 25 Gb/s, an EML with $$\alpha_\mathrm{EAM} = +0.5$$ 40 and 6 km, a chirp-free modulator 58 and 9 km; in the O band the same DML loses 0.1 dB over 2 km. Drivers for 50 Ω loads and coolers dominate the energy of EMLs and MZMs; a VCSEL's laser spends 0.4 pJ/bit at 25 Gb/s.

</div>

## Check yourself

{% include quiz.html %}
