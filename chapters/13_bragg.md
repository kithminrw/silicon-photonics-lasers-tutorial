---
title: "13. Bragg Gratings and Photonic Crystals"
parent: "Part III · Passive Devices"
nav_order: 13
permalink: /part-3/ch13/
chapter: 13
---

# <span class="chapnum">Chapter 13</span>Bragg Gratings and Photonic Crystals

A periodic change of index reflects one band of wavelengths and passes the rest: the integrated version of a dielectric mirror.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- state the Bragg condition and choose a grating period;
- relate the stop-band and peak reflectivity to the coupling coefficient κ and the length;
- model a grating with coupled-mode theory and with transfer matrices;
- add up the round trips of a Fabry–Pérot cavity into the Airy function, and read off its FSR, finesse, Q and peak transmission;
- apodise a grating and build cavities from Bragg mirrors and phase-shifted gratings;
- describe contra-directional couplers, the subwavelength regime and photonic crystals.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How long and how strong must a grating be for a given reflectivity and bandwidth?

</div>

## <span class="secnum">13.1</span>Periodic waveguides and the Bragg condition

Corrugate the sidewalls of a waveguide with period $$\Lambda$$ ([Figure 13.1](#fig-13-1)), so that its effective index alternates slightly. Each period reflects a tiny fraction of the light; the reflections add in phase when the round trip over one period is a whole wavelength in the guide, the **Bragg condition**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Bragg condition (first order)</div>

$$\lambda_B = 2\,n_\mathrm{eff}\,\Lambda$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.1 · The period for 1550 nm</div>

In a 500 × 220 nm silicon strip ($$n_\mathrm{eff} = 2.446$$, [Chapter 6]({% link chapters/06_soi.md %})), a first-order grating at 1550 nm needs $$\Lambda = 1550/(2 \times 2.446) = 316.8$$ nm, which is why the SiEPIC EBeam PDK's Bragg grating defaults to 317 nm {% include cite.html keys="ebeampdk" %}. Because the corrugation lowers the average width, the real $$n_\mathrm{eff}$$ is a little lower, and the measured Bragg wavelength shifts accordingly. A second-order grating, with twice the period, also reflects but radiates part of the light vertically: the principle of the grating coupler ([Chapter 15]({% link chapters/15_gc.md %})).

</div>

<figure id="fig-13-1">
  <img src="{{ '/assets/figs/ch13_geometry.svg' | relative_url }}" style="width:600px" alt="Top view to scale of six periods of a sidewall-corrugated 500 nm silicon waveguide with a 316.8 nm period and 50 nm corrugations, with the forward wave and the small reflections from each period drawn as arrows, and below it the effective index along the guide as a square wave with its sinusoidal first Fourier component">
  <figcaption><span class="capnum">Figure 13.1.</span> <strong>A sidewall Bragg grating, to scale.</strong> (a) Six periods of a 500 nm wide silicon strip with \(\Lambda = 316.8\) nm, drawn with the 50 nm sidewall corrugation of the PDK's strongest gratings. Each period reflects a little of the forward wave; the reflections add in phase at \(\lambda_B = 2n_\mathrm{eff}\Lambda\). (b) To the mode, the grating is an effective index that alternates by \(\Delta n\) every half period; its first Fourier component, at the period \(\Lambda\), is what couples the forward and backward waves. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">13.2</span>Coupled-mode theory of gratings

The periodic perturbation couples the forward and backward modes of the waveguide with a **coupling coefficient** $$\kappa$$ (per unit length), set by the corrugation depth and the field at the sidewall. With the detuning from the Bragg condition $$\delta = \beta - \pi/\Lambda$$, coupled-mode theory gives the reflectivity of a uniform grating of length $$L$$ {% include cite.html keys="yariv1973" %}. Its most useful results are:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Uniform grating: peak reflectivity and bandwidth</div>

$$R_\mathrm{peak} = \tanh^2(\kappa L), \qquad \Delta\lambda_\mathrm{null} = \frac{\lambda^2}{n_gL}\sqrt{\left(\frac{\kappa L}{\pi}\right)^2 + 1} \ \xrightarrow{\ \kappa L \gg 1\ }\ \frac{\lambda^2\kappa}{\pi n_g}$$

</div>

So $$\kappa L$$ sets the reflectivity, and $$\kappa$$ alone sets the width of the stop-band of a long grating; $$L$$ only sharpens its edges ([Figure 13.2](#fig-13-2)). Inside the stop-band light cannot propagate (its wavevector becomes complex, [Figure 13.3](#fig-13-3)), which is the one-dimensional version of a photonic band gap.

<figure id="fig-13-2">
  <img src="{{ '/assets/figs/ch13_kappaL.svg' | relative_url }}" style="width:600px" alt="Reflection spectra of uniform gratings. Left: kappa fixed at 12.6 per millimetre and 150, 300, 750 and 1500 periods, with peak reflectivities rising from 29 to 100 percent and the flat top filling the 2.3 nm stop band. Right: length fixed at 95 micrometres and kappa of 12.6, 40 and 140 per millimetre, with the reflection band widening to about 26 nm">
  <figcaption><span class="capnum">Figure 13.2.</span> <strong>Length sets the height, κ the width.</strong> Reflectivity of uniform gratings from coupled-mode theory. (a) At \(\kappa = 12.6\ \mathrm{mm^{-1}}\), more periods raise the peak to \(\tanh^2(\kappa L)\) (29, 69, 99 and 100 %) and square its edges, while the band narrows towards, but not below, the 2.3 nm stop band (shaded). (b) At a fixed 95 µm (300 periods), a stronger κ widens the band; at the PDK's 140 \(\mathrm{mm^{-1}}\) it is 26 nm wide between its first nulls. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.2 · Reflectivity and bandwidth</div>

With $$\kappa = 12.6$$ mm⁻¹ and 300 periods ($$L = 95$$ µm), $$\kappa L = 1.2$$ and $$R_\mathrm{peak} = \tanh^2(1.2) = 69\ \%$$, with a null-to-null bandwidth of $$2.4025/(4.18 \times 95) \times \sqrt{0.146 + 1} \approx 6.5$$ nm. For 99 % reflection, $$\tanh^2(\kappa L) = 0.99$$ needs $$\kappa L = 3.0$$, so 238 µm, or 750 periods, at the same κ. The PDK documents coupling coefficients up to about $$1.4\times10^5\ \mathrm{m^{-1}}$$ (140 mm⁻¹) for 50 nm sidewall corrugations, which gives a stop-band of order $$\lambda^2\kappa/(\pi n_g) \approx 25$$ nm {% include cite.html keys="ebeampdk" %}.

</div>

<figure id="fig-13-3">
  <img src="{{ '/assets/figs/ch13_band.svg' | relative_url }}" style="width:600px" alt="Band diagram of an infinite grating: wavelength against the real part of the Bloch wavenumber near the edge of the zone, with two branches separated by a gap of 25.6 nm for kappa 140 per millimetre and 2.3 nm for 12.6 per millimetre, and beside it the imaginary part of the wavenumber, which is non-zero only inside the gap and peaks at kappa at its centre">
  <figcaption><span class="capnum">Figure 13.3.</span> <strong>The stop-band as a band gap.</strong> Bloch waves of an endless grating, from coupled-mode theory: \((K - \pi/\Lambda)^2 = \delta^2 - \kappa^2\). (a) Outside the stop-band the wavenumber is real and the grating only bends the dispersion; inside it (shaded for 140 \(\mathrm{mm^{-1}}\): 25.6 nm wide; 2.3 nm for 12.6 \(\mathrm{mm^{-1}}\)) no real solution exists. (b) There the wave decays instead, at a rate that peaks at κ in the middle of the gap: a grating of a few \(1/\kappa\) is already a good mirror. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">13.3</span>The transfer-matrix method

Real gratings are rarely uniform, so they are modelled by cutting them into sections, each described by the 2 × 2 matrix that relates forward and backward amplitudes at its two ends, and multiplying the matrices. The reflectivity of the whole grating is read from the product. This **transfer-matrix method** handles apodisation, chirp and phase shifts with no extra effort, and it is what the demo below computes, section by section.

**Try it.** Change the period, coupling and number of periods, apodise the grating or add a quarter-wave shift, and probe the field along it at any wavelength.

{% include demos/bragg.html %}

## <span class="secnum">13.4</span>Apodisation and chirp

A uniform grating's spectrum has strong **side lobes**, because its abrupt ends act like a rectangular window in a Fourier transform. Tapering the coupling smoothly from zero at the ends to a maximum in the middle, **apodisation**, suppresses them by tens of decibels ([Figure 13.4](#fig-13-4)), exactly as a window function does in signal processing. The main peak pays for it in a way that depends on the grating's strength. A weak grating ($$\kappa L$$ of order 1) has a spectrum close to the Fourier transform of $$\kappa(z)$$, so, as with a window, its peak becomes lower and broader: for the grating of Example 13.2 a Gaussian taper with the same maximum κ drops it from 69 % to 19 % and widens it from 3.9 to 5.6 nm at half maximum. A strong grating ($$\kappa L \approx 10$$) has a stop-band set by κ, and its peak becomes only slightly lower and a little narrower ([Lab 5]({% link labs/lab05_bragg.md %})). In sidewall gratings the coupling is tapered by varying the corrugation width or by misaligning the corrugations on the two sidewalls, which partly cancels them.

<figure id="fig-13-4">
  <img src="{{ '/assets/figs/ch13_apod.svg' | relative_url }}" style="width:600px" alt="Left: coupling coefficient along a 95 micrometre grating, constant for the uniform grating and Gaussian for the apodised ones, with peaks of 12.6 and 32 per millimetre. Right: their reflection spectra in decibels: the uniform grating has side lobes about 10 dB below its peak, the apodised gratings have none above minus 50 dB">
  <figcaption><span class="capnum">Figure 13.4.</span> <strong>Apodisation.</strong> The 300-period grating of Example 13.2, uniform and with the Gaussian coupling profile of the demo. (a) The coupling along the grating. (b) Reflectivity in dB: the uniform grating's strongest side lobe is 10.4 dB below its peak, the apodised gratings' are more than 50 dB down. At the same maximum κ the peak falls from 69 % to 19 % and widens from 3.9 to 5.6 nm (FWHM); raising κ by 2.57 restores the 69 % peak, at 7.7 nm. Coupled-mode theory, 300 sections. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

**Chirping** the period along the grating makes different wavelengths reflect at different depths, which broadens the stop-band and gives a wavelength-dependent delay: a dispersion compensator on a chip.

## <span class="secnum">13.5</span>The Fabry–Pérot cavity

A grating is a mirror. Put two mirrors face to face on a waveguide and they make a **Fabry–Pérot cavity**: the oldest optical resonator, and the one inside every edge-emitting laser ([Chapter 24]({% link chapters/24_fp.md %})). A ring ([Chapter 12]({% link chapters/12_rings.md %})) is a travelling-wave resonator: the light goes round in one direction. A Fabry–Pérot cavity is a standing-wave resonator: the light bounces back and forth, and the forward and backward waves together form a standing wave with nodes every $$\lambda/(2n_\mathrm{eff})$$.

**Adding up the bounces.** Let light meet mirror 1 (power reflectance $$R_1$$), cross the cavity of length $$L$$ with single-pass power transmission $$A = e^{-\alpha L}$$, and meet mirror 2 ($$R_2$$). Part of it leaves and the rest goes back for another round trip. Each round trip multiplies the field inside by $$\rho\,e^{-j\phi}$$, where $$\rho = \sqrt{R_1R_2}\,A$$ and the round-trip phase is $$\phi = 2\beta L = 4\pi n_\mathrm{eff}L/\lambda$$ (any phase the mirrors add on reflection is included in it). The transmitted fields therefore form a geometric series. Its sum is the **Airy function** {% include cite.html keys="salehteich" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Fabry–Pérot transmission (Airy function)</div>

$$T = \frac{(1 - R_1)(1 - R_2)\,A}{(1 - \rho)^2 + 4\rho\sin^2(\phi/2)}, \qquad \rho = \sqrt{R_1R_2}\,A$$

</div>

The cavity resonates where the round trip is a whole number of wavelengths, $$2n_\mathrm{eff}L = m\lambda$$. Everything else follows from the formula ([Figure 13.5](#fig-13-5)):

- **Free spectral range.** $$\mathrm{FSR} = \lambda^2/(2n_gL)$$, the same as a ring whose circumference is $$2L$$.
- **Finesse and Q.** The peaks are $$\mathrm{FSR}/F$$ wide, with finesse $$F = \pi/\left(2\arcsin\left[(1 - \rho)/(2\sqrt{\rho})\right]\right) \approx \pi\sqrt{\rho}/(1 - \rho)$$ (the approximation holds for $$\rho$$ near 1). The quality factor is $$Q = \lambda/\Delta\lambda_\mathrm{FWHM} = (2n_gL/\lambda)\,F$$.
- **Photon lifetime.** The energy inside falls by $$\rho^2$$ per round trip, so it decays with $$\tau_p = L/[v_g\ln(1/\rho)] = 1/[v_g(\alpha + \alpha_m)]$$. Here $$\alpha_m = \ln(1/R_1R_2)/(2L)$$ is the mirror loss that Chapter 24 uses for lasers. At high finesse $$Q = \omega\tau_p$$, as for a ring.
- **Peak transmission and reflection.** On resonance the cavity reflects $$(\sqrt{R_1} - \sqrt{R_2}\,A)^2/(1 - \rho)^2$$, which vanishes when $$R_1 = R_2A^2$$: the front mirror then leaks as fast as everything behind it loses. This is the Fabry–Pérot form of critical coupling ([Sections 12.2 and 12.3]({% link chapters/12_rings.md %})). The light that is not reflected is transmitted, $$T_\mathrm{max} = (1 - R_1)(1 - R_2)A/(1 - \rho)^2$$, or absorbed inside. A lossless cavity with equal mirrors therefore transmits everything on resonance, however high its mirrors. With loss, even a matched cavity absorbs part of the light, and an unbalanced one also sends part of it back.
- **Contrast.** $$T_\mathrm{max}/T_\mathrm{min} = [(1 + \rho)/(1 - \rho)]^2$$. Below $$\rho = 3 - 2\sqrt{2} \approx 0.17$$ the transmission never falls to half its peak and the finesse is not defined. That is the regime of weak, unwanted cavities.

<figure id="fig-13-5">
  <img src="{{ '/assets/figs/ch13_fp.svg' | relative_url }}" style="width:620px" alt="a: Fabry-Perot transmission against round-trip phase for equal lossless mirrors of reflectance 0.30, 0.70 and 0.95, with finesses 2.3, 8.7 and 61; all reach 1 on resonance, and the free spectral range and the full width at half maximum are marked. b: transmission of a cavity between two Bragg gratings against wavelength from transfer matrices, with resonances at 0 and plus or minus 1.66 nanometres inside the stop band of one grating, against the Airy formula with reflectance 0.69 and an effective length of 166 micrometres">
  <figcaption><span class="capnum">Figure 13.5.</span> <strong>The Fabry–Pérot cavity.</strong> (a) The Airy function for equal lossless mirrors. Every peak reaches 100 %, but its width, FSR/F, shrinks as the mirrors rise: R = 0.30 (a cleaved facet) gives F = 2.3 and shallow fringes, 0.95 gives F = 61. (b) The cavity of Worked Example 13.3: two 300-period gratings (R = 69 %, dotted, the reflectance of one) around a 100.3 µm spacer. Transfer matrices of the whole structure (blue) give a 204 pm resonance at 1550 nm (Q ≈ 7600), exactly as the Airy formula does with R = 0.69 and an effective length of 166 µm that includes the light's penetration into the gratings (dashed). Away from the Bragg wavelength the mirrors weaken: the neighbours sit at ±1.66 nm instead of ±1.73 nm and are 0.44 nm wide, and outside the stop-band the model fails. Coupled-mode transfer matrices as in Figure 13.6. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

**Mirrors on a chip.** Any reflector will do, and each has its uses:

- **Facets.** A cleaved or etched facet reflects $$((n - 1)/(n + 1))^2$$, about 0.3 for InP, enough for a laser ([Chapter 24]({% link chapters/24_fp.md %})). Dielectric coatings raise it (HR) or remove it (AR).
- **Bragg gratings.** A grating reflects $$\tanh^2(\kappa L_g)$$ over its stop-band only (Section 13.2). The light reaches into it a **penetration depth** $$L_p = \tanh(\kappa L_g)/(2\kappa)$$ at the Bragg wavelength, so the cavity behaves as if it were $$L_\mathrm{eff} = L + L_{p1} + L_{p2}$$ long. Gratings are the mirrors of DBR lasers ([Chapter 26]({% link chapters/26_tunable.md %})).
- **Loop mirrors.** Join the two outputs of a 2 × 2 coupler with a waveguide loop and the light comes back: the loop reflects $$4\kappa^2(1 - \kappa^2)$$ for a power coupling $$\kappa^2$$, all of it for a 3 dB coupler, over the coupler's whole bandwidth ([Chapter 9]({% link chapters/09_couplers.md %})).
- **Phase-shifted gratings.** Both mirrors are halves of one grating (Section 13.6).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.3 · A cavity between two Bragg mirrors</div>

Place two copies of the 300-period grating of Example 13.2 ($$\kappa L_g = 1.20$$, $$R = 69.4$$ %) on either side of a spacer 316.5 periods long (100.3 µm). The extra half period puts one resonance on the Bragg wavelength.

- **Effective length.** $$L_p = \tanh(1.198)/(2 \times 12.6\ \mathrm{mm^{-1}}) = 33.1$$ µm, so $$L_\mathrm{eff} = 100.3 + 2 \times 33.1 = 166.4$$ µm.
- **FSR.** $$1.55^2/(2 \times 4.18 \times 166.4\ \mu\mathrm{m}) = 1.73$$ nm.
- **Width.** Without loss $$\rho = R = 0.694$$ and $$F = 8.50$$, so the FWHM is 203 pm, $$Q \approx 7600$$, and the photon lifetime $$Q\lambda/(2\pi c)$$ is 6.3 ps.
- **Check.** Transfer matrices of the whole structure give 204 pm at 1550.00 nm ([Figure 13.5](#fig-13-5)b). The neighbours at ±1.66 nm are 0.44 nm wide, because there each grating reflects only 46 %. Such a cavity filters only inside the stop-band.
- **Loss.** With 2 dB/cm of waveguide loss, $$A = 0.992$$ over $$L_\mathrm{eff}$$ and $$\rho = 0.689$$: the peak falls to 96 % and the finesse to 8.3.

</div>

**Fringes as a measurement.** Any two reflections on a waveguide make a cavity, wanted or not, and its fringes carry information:

- **Loss.** Between two facets of known reflectance $$R$$, the fringe contrast $$K = (T_\mathrm{max} - T_\mathrm{min})/(T_\mathrm{max} + T_\mathrm{min}) = 2\rho/(1 + \rho^2)$$ gives $$\rho$$ and hence $$\alpha = \ln(R/\rho)/L$$. Unlike a cutback, the result does not depend on how well light is coupled in: this is the Fabry–Pérot method {% include cite.html keys="regener1985" %}.
- **Unwanted reflections.** Two grating couplers or facets on one waveguide ripple its transmission with a period $$\lambda^2/(2n_gL)$$ (Section 15.5 of [Chapter 15]({% link chapters/15_gc.md %}), [Lab 9]({% link labs/lab09_analysis.md %})). The period tells how far apart the reflectors are; the depth tells how strong they are.
- **Gain.** Put gain in the cavity and $$A$$ becomes a single-pass gain $$G > 1$$. As $$\rho = \sqrt{R_1R_2}\,G$$ approaches 1 the denominator of the Airy function vanishes. $$\sqrt{R_1R_2}\,G = 1$$ is the threshold condition of [Chapter 24]({% link chapters/24_fp.md %}). Below threshold the cavity filters the chip's own spontaneous emission. The ratio $$r$$ of the peaks to the valleys of that spectrum gives the gain: $$\sqrt{R_1R_2}\,G = (\sqrt{r} - 1)/(\sqrt{r} + 1)$$, the Hakki–Paoli method {% include cite.html keys="hakki1975" %}. The gain ripple of an SOA ([Section 28.5]({% link chapters/28_soa.md %})) is the same formula.

**Try it.** Choose a cavity, then change its mirrors, length and loss, and move the probe across a resonance. The passes inside the cavity, the transmitted fields adding up pass by pass, and the spectrum all follow.

{% include demos/fp.html %}

[Lab 13]({% link labs/lab13_fp.md %}) does all of this in Python: the Airy function, this Bragg-mirror cavity by transfer matrices, and loss and gain read from simulated measurements.

## <span class="secnum">13.6</span>Phase-shifted gratings

Insert a quarter-wave section, a phase shift of half a period, in the middle of a uniform grating, and the two halves become two mirrors facing each other with exactly the right spacing for one resonance at the Bragg wavelength. A narrow transmission peak opens in the middle of the stop-band ([Figure 13.6](#fig-13-6)). The **λ/4-shifted grating** is a compact, high-Q filter and the heart of the single-mode **DFB laser** ([Chapter 26]({% link chapters/26_tunable.md %})). Two separate gratings with a spacer between them form the Fabry–Pérot cavity of Section 13.5, the mirrors of the **DBR laser**; the λ/4-shifted grating is the limit in which the spacer shrinks to a quarter wave.

<figure id="fig-13-6">
  <img src="{{ '/assets/figs/ch13_cavity.svg' | relative_url }}" style="width:600px" alt="Left: transmission of a 750-period grating, uniform and with a quarter-wave shift in the middle; the shifted grating has a narrow transmission peak of 258 pm width at the centre of the stop band. Right: the optical intensity along the grating on a log scale: in the shifted grating on resonance it grows to ten times the input at the shift and falls back to one at the far end, while in the uniform grating at the Bragg wavelength it decays from the input">
  <figcaption><span class="capnum">Figure 13.6.</span> <strong>A λ/4-shifted grating.</strong> 750 periods at \(\kappa = 12.6\ \mathrm{mm^{-1}}\) (\(\kappa L = 3.0\)). (a) The shift opens a transmission peak 258 pm wide (\(Q \approx 6000\)) in the middle of the stop-band. (b) Forward plus backward intensity along the grating: at the Bragg wavelength the uniform grating's field dies away from the input, while on resonance the shifted grating's field builds up tenfold towards the shift, where the two mirrors meet, and leaves at the far end with the full input power. Coupled-mode transfer matrices. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">13.7</span>Contra-directional couplers and SWG metamaterials

A Bragg grating reflects into the same waveguide, so the reflected light must be separated with a circulator, which does not exist on silicon. A **contra-directional coupler** solves this ([Figure 13.7](#fig-13-7)): two waveguides of different widths are coupled through a grating whose period matches the sum of their propagation constants, $$\lambda = \Lambda(n_{\mathrm{eff},1} + n_{\mathrm{eff},2})$$, so the reflected band leaves through the other waveguide. It is an add-drop filter with a flat top and no free spectral range, unlike a ring, and is used for wideband WDM channels.

<figure id="fig-13-7">
  <img src="{{ '/assets/figs/ch13_contradc.svg' | relative_url }}" style="width:600px" alt="Left: top view to scale of a contra-directional coupler, a 550 nm and a 450 nm silicon waveguide 150 nm apart with corrugations on their facing sidewalls at a 318 nm period, with the input and through ports on the wide guide and the drop port leaving backwards on the narrow guide. Right: wavenumber against wavelength for twice the wide guide's propagation constant, the sum of both and twice the narrow guide's, crossing the grating wavenumber at 1581, 1550 and 1521 nm">
  <figcaption><span class="capnum">Figure 13.7.</span> <strong>A contra-directional coupler.</strong> (a) Top view to scale of an illustrative design: 550 and 450 nm wide strips 150 nm apart, with 40 nm corrugations on the facing sidewalls. The period, 318 nm, matches \(\lambda = \Lambda(n_{\mathrm{eff},1} + n_{\mathrm{eff},2})\) at 1550 nm, so that band is reflected into the narrow guide and leaves backwards. (b) Phase matching, with \(n_\mathrm{eff}\) and \(n_g\) of the uncoupled strips from the femwell sweep of Chapter 6: the grating also reflects each guide into itself, but at 1581 nm (wide) and 1521 nm (narrow), well away from the drop band. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

When the period is much shorter than the Bragg period, $$\Lambda \ll \lambda/(2n_\mathrm{eff})$$, nothing is reflected at all: the segmented waveguide behaves as a homogeneous **subwavelength-grating (SWG) metamaterial** whose index is set by the fill factor ([Chapter 6]({% link chapters/06_soi.md %})).

## <span class="secnum">13.8</span>Photonic crystals

Periodicity in two or three dimensions extends these ideas. A silicon slab perforated with a lattice of holes ([Figure 13.8](#fig-13-8)) has a **photonic band gap** for in-plane light; removing a row of holes makes a waveguide whose modes can be slowed to group indices of tens or more (slow light), and removing a few holes makes a cavity with Q in the millions and a mode volume of about a cubic wavelength. Photonic-crystal cavities and waveguides are research favourites for sensing, nonlinear optics and ultra-small lasers, but their sensitivity to fabrication keeps them out of most foundry PDKs.

<figure id="fig-13-8">
  <img src="{{ '/assets/figs/ch13_phc.svg' | relative_url }}" style="width:600px" alt="Top views to scale of a silicon slab with a triangular lattice of air holes, 400 nm apart: on the left one row of holes is missing, forming a line-defect waveguide along which light is guided; on the right only three holes are missing, forming a small cavity">
  <figcaption><span class="capnum">Figure 13.8.</span> <strong>Photonic-crystal waveguide and cavity.</strong> Top views to scale of a silicon slab with a triangular lattice of air holes (illustrative: lattice constant 400 nm, hole radius 120 nm). (a) A missing row of holes is a line-defect waveguide (W1): light in the band gap cannot leave it sideways. (b) Three missing holes make an L3 cavity, with a mode volume of about a cubic wavelength. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: Bragg grating number of periods](https://s3.amazonaws.com/fip-12/Number-of-Periods/index.html), [corrugation width](https://s3.amazonaws.com/fip-12/Corrugation-Width/index.html) and [cavity length](https://s3.amazonaws.com/fip-12/Cavity-Length/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="yariv1973,chrostowski2015,ebeampdk,okamoto,salehteich,regener1985,hakki1975" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Bragg condition $$\lambda_B = 2n_\mathrm{eff}\Lambda$$: 316.8 nm period in a 500 × 220 nm silicon strip at 1550 nm.
- Peak reflectivity $$\tanh^2(\kappa L)$$; a long grating's stop-band is $$\lambda^2\kappa/(\pi n_g)$$ wide.
- Transfer matrices model non-uniform gratings; apodisation removes side lobes, chirp spreads the stop-band.
- Two mirrors make a Fabry–Pérot cavity: FSR $$\lambda^2/(2n_gL)$$, finesse $$\approx \pi\sqrt{\rho}/(1 - \rho)$$ with $$\rho = \sqrt{R_1R_2}\,e^{-\alpha L}$$, no reflection on resonance when $$R_1 = R_2e^{-2\alpha L}$$, and 100 % transmission only without loss and with equal mirrors. A Bragg mirror adds its penetration depth to the length; fringe contrast measures loss (Fabry–Pérot method) and gain (Hakki–Paoli).
- A λ/4 shift makes a narrow cavity resonance in the stop-band: the basis of DFB lasers.
- Contra-directional couplers drop a band into a second waveguide; SWGs and photonic crystals extend periodicity to metamaterials and band gaps.

</div>

## Check yourself

{% include quiz.html %}
