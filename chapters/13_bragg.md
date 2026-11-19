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
- apodise a grating and build cavities from phase-shifted gratings;
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

**Try it.** Change the period, coupling and number of periods, apodise the grating or add a quarter-wave shift; the geometry shows a magnified stretch linked to the whole grating.

{% include demos/bragg.html %}

## <span class="secnum">13.4</span>Apodisation and chirp

A uniform grating's spectrum has strong **side lobes**, because its abrupt ends act like a rectangular window in a Fourier transform. Tapering the coupling smoothly from zero at the ends to a maximum in the middle, **apodisation**, suppresses them by tens of decibels ([Figure 13.4](#fig-13-4)), exactly as a window function does in signal processing. The main peak pays for it in a way that depends on the grating's strength. A weak grating ($$\kappa L$$ of order 1) has a spectrum close to the Fourier transform of $$\kappa(z)$$, so, as with a window, its peak becomes lower and broader: for the grating of Example 13.2 a Gaussian taper with the same maximum κ drops it from 69 % to 19 % and widens it from 3.9 to 5.6 nm at half maximum. A strong grating ($$\kappa L \approx 10$$) has a stop-band set by κ, and its peak becomes only slightly lower and a little narrower ([Lab 5]({% link labs/lab05_bragg.md %})). In sidewall gratings the coupling is tapered by varying the corrugation width or by misaligning the corrugations on the two sidewalls, which partly cancels them.

<figure id="fig-13-4">
  <img src="{{ '/assets/figs/ch13_apod.svg' | relative_url }}" style="width:600px" alt="Left: coupling coefficient along a 95 micrometre grating, constant for the uniform grating and Gaussian for the apodised ones, with peaks of 12.6 and 32 per millimetre. Right: their reflection spectra in decibels: the uniform grating has side lobes about 10 dB below its peak, the apodised gratings have none above minus 50 dB">
  <figcaption><span class="capnum">Figure 13.4.</span> <strong>Apodisation.</strong> The 300-period grating of Example 13.2, uniform and with the Gaussian coupling profile of the demo. (a) The coupling along the grating. (b) Reflectivity in dB: the uniform grating's strongest side lobe is 10.4 dB below its peak, the apodised gratings' are more than 50 dB down. At the same maximum κ the peak falls from 69 % to 19 % and widens from 3.9 to 5.6 nm (FWHM); raising κ by 2.57 restores the 69 % peak, at 7.7 nm. Coupled-mode theory, 300 sections. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

**Chirping** the period along the grating makes different wavelengths reflect at different depths, which broadens the stop-band and gives a wavelength-dependent delay: a dispersion compensator on a chip.

## <span class="secnum">13.5</span>Cavities

Insert a quarter-wave section, a phase shift of half a period, in the middle of a uniform grating, and the two halves become two mirrors facing each other with exactly the right spacing for one resonance at the Bragg wavelength. A narrow transmission peak opens in the middle of the stop-band ([Figure 13.5](#fig-13-5)). The **λ/4-shifted grating** is a compact, high-Q filter and the heart of the single-mode **DFB laser** ([Chapter 26]({% link chapters/26_tunable.md %})). Two separate gratings with a spacer between them form a Fabry–Pérot cavity, the mirrors of the **DBR laser**.

<figure id="fig-13-5">
  <img src="{{ '/assets/figs/ch13_cavity.svg' | relative_url }}" style="width:600px" alt="Left: transmission of a 750-period grating, uniform and with a quarter-wave shift in the middle; the shifted grating has a narrow transmission peak of 258 pm width at the centre of the stop band. Right: the optical intensity along the grating on a log scale: in the shifted grating on resonance it grows to ten times the input at the shift and falls back to one at the far end, while in the uniform grating at the Bragg wavelength it decays from the input">
  <figcaption><span class="capnum">Figure 13.5.</span> <strong>A λ/4-shifted grating.</strong> 750 periods at \(\kappa = 12.6\ \mathrm{mm^{-1}}\) (\(\kappa L = 3.0\)). (a) The shift opens a transmission peak 258 pm wide (\(Q \approx 6000\)) in the middle of the stop-band. (b) Forward plus backward intensity along the grating: at the Bragg wavelength the uniform grating's field dies away from the input, while on resonance the shifted grating's field builds up tenfold towards the shift, where the two mirrors meet, and leaves at the far end with the full input power. Coupled-mode transfer matrices. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">13.6</span>Contra-directional couplers and SWG metamaterials

A Bragg grating reflects into the same waveguide, so the reflected light must be separated with a circulator, which does not exist on silicon. A **contra-directional coupler** solves this ([Figure 13.6](#fig-13-6)): two waveguides of different widths are coupled through a grating whose period matches the sum of their propagation constants, $$\lambda = \Lambda(n_{\mathrm{eff},1} + n_{\mathrm{eff},2})$$, so the reflected band leaves through the other waveguide. It is an add-drop filter with a flat top and no free spectral range, unlike a ring, and is used for wideband WDM channels.

<figure id="fig-13-6">
  <img src="{{ '/assets/figs/ch13_contradc.svg' | relative_url }}" style="width:600px" alt="Left: top view to scale of a contra-directional coupler, a 550 nm and a 450 nm silicon waveguide 150 nm apart with corrugations on their facing sidewalls at a 318 nm period, with the input and through ports on the wide guide and the drop port leaving backwards on the narrow guide. Right: wavenumber against wavelength for twice the wide guide's propagation constant, the sum of both and twice the narrow guide's, crossing the grating wavenumber at 1581, 1550 and 1521 nm">
  <figcaption><span class="capnum">Figure 13.6.</span> <strong>A contra-directional coupler.</strong> (a) Top view to scale of an illustrative design: 550 and 450 nm wide strips 150 nm apart, with 40 nm corrugations on the facing sidewalls. The period, 318 nm, matches \(\lambda = \Lambda(n_{\mathrm{eff},1} + n_{\mathrm{eff},2})\) at 1550 nm, so that band is reflected into the narrow guide and leaves backwards. (b) Phase matching, with \(n_\mathrm{eff}\) and \(n_g\) of the uncoupled strips from the femwell sweep of Chapter 6: the grating also reflects each guide into itself, but at 1581 nm (wide) and 1521 nm (narrow), well away from the drop band. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

When the period is much shorter than the Bragg period, $$\Lambda \ll \lambda/(2n_\mathrm{eff})$$, nothing is reflected at all: the segmented waveguide behaves as a homogeneous **subwavelength-grating (SWG) metamaterial** whose index is set by the fill factor ([Chapter 6]({% link chapters/06_soi.md %})).

## <span class="secnum">13.7</span>Photonic crystals

Periodicity in two or three dimensions extends these ideas. A silicon slab perforated with a lattice of holes ([Figure 13.7](#fig-13-7)) has a **photonic band gap** for in-plane light; removing a row of holes makes a waveguide whose modes can be slowed to group indices of tens or more (slow light), and removing a few holes makes a cavity with Q in the millions and a mode volume of about a cubic wavelength. Photonic-crystal cavities and waveguides are research favourites for sensing, nonlinear optics and ultra-small lasers, but their sensitivity to fabrication keeps them out of most foundry PDKs.

<figure id="fig-13-7">
  <img src="{{ '/assets/figs/ch13_phc.svg' | relative_url }}" style="width:600px" alt="Top views to scale of a silicon slab with a triangular lattice of air holes, 400 nm apart: on the left one row of holes is missing, forming a line-defect waveguide along which light is guided; on the right only three holes are missing, forming a small cavity">
  <figcaption><span class="capnum">Figure 13.7.</span> <strong>Photonic-crystal waveguide and cavity.</strong> Top views to scale of a silicon slab with a triangular lattice of air holes (illustrative: lattice constant 400 nm, hole radius 120 nm). (a) A missing row of holes is a line-defect waveguide (W1): light in the band gap cannot leave it sideways. (b) Three missing holes make an L3 cavity, with a mode volume of about a cubic wavelength. Drawn by <code>figsrc/ch13_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: Bragg grating number of periods](https://s3.amazonaws.com/fip-12/Number-of-Periods/index.html), [corrugation width](https://s3.amazonaws.com/fip-12/Corrugation-Width/index.html) and [cavity length](https://s3.amazonaws.com/fip-12/Cavity-Length/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="yariv1973,chrostowski2015,ebeampdk,okamoto" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Bragg condition $$\lambda_B = 2n_\mathrm{eff}\Lambda$$: 316.8 nm period in a 500 × 220 nm silicon strip at 1550 nm.
- Peak reflectivity $$\tanh^2(\kappa L)$$; a long grating's stop-band is $$\lambda^2\kappa/(\pi n_g)$$ wide.
- Transfer matrices model non-uniform gratings; apodisation removes side lobes, chirp spreads the stop-band.
- A λ/4 shift makes a narrow cavity resonance in the stop-band: the basis of DFB lasers.
- Contra-directional couplers drop a band into a second waveguide; SWGs and photonic crystals extend periodicity to metamaterials and band gaps.

</div>
