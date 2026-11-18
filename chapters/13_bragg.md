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

Corrugate the sidewalls of a waveguide with period $$\Lambda$$, so that its effective index alternates slightly. Each period reflects a tiny fraction of the light; the reflections add in phase when the round trip over one period is a whole wavelength in the guide, the **Bragg condition**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Bragg condition (first order)</div>

$$\lambda_B = 2\,n_\mathrm{eff}\,\Lambda$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.1 · The period for 1550 nm</div>

In a 500 × 220 nm silicon strip ($$n_\mathrm{eff} = 2.446$$, [Chapter 6]({% link chapters/06_soi.md %})), a first-order grating at 1550 nm needs $$\Lambda = 1550/(2 \times 2.446) = 316.8$$ nm, which is why the SiEPIC EBeam PDK's Bragg grating defaults to 317 nm {% include cite.html keys="ebeampdk" %}. Because the corrugation lowers the average width, the real $$n_\mathrm{eff}$$ is a little lower, and the measured Bragg wavelength shifts accordingly. A second-order grating, with twice the period, also reflects but radiates part of the light vertically: the principle of the grating coupler ([Chapter 15]({% link chapters/15_gc.md %})).

</div>

## <span class="secnum">13.2</span>Coupled-mode theory of gratings

The periodic perturbation couples the forward and backward modes of the waveguide with a **coupling coefficient** $$\kappa$$ (per unit length), set by the corrugation depth and the field at the sidewall. With the detuning from the Bragg condition $$\delta = \beta - \pi/\Lambda$$, coupled-mode theory gives the reflectivity of a uniform grating of length $$L$$ {% include cite.html keys="yariv1973" %}. Its most useful results are:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Uniform grating: peak reflectivity and bandwidth</div>

$$R_\mathrm{peak} = \tanh^2(\kappa L), \qquad \Delta\lambda_\mathrm{null} = \frac{\lambda^2}{n_gL}\sqrt{\left(\frac{\kappa L}{\pi}\right)^2 + 1} \ \xrightarrow{\ \kappa L \gg 1\ }\ \frac{\lambda^2\kappa}{\pi n_g}$$

</div>

So $$\kappa L$$ sets the reflectivity, and $$\kappa$$ alone sets the width of the stop-band of a long grating; $$L$$ only sharpens its edges. Inside the stop-band light cannot propagate (its wavevector becomes complex), which is the one-dimensional version of a photonic band gap.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 13.2 · Reflectivity and bandwidth</div>

With $$\kappa = 12.6$$ mm⁻¹ and 300 periods ($$L = 95$$ µm), $$\kappa L = 1.2$$ and $$R_\mathrm{peak} = \tanh^2(1.2) = 69\ \%$$, with a null-to-null bandwidth of $$2.4025/(4.18 \times 95) \times \sqrt{0.146 + 1} \approx 6.5$$ nm. For 99 % reflection, $$\tanh^2(\kappa L) = 0.99$$ needs $$\kappa L = 3.0$$, so 238 µm, or 750 periods, at the same κ. The PDK documents coupling coefficients up to about $$1.4\times10^5\ \mathrm{m^{-1}}$$ (140 mm⁻¹) for 50 nm sidewall corrugations, which gives a stop-band of order $$\lambda^2\kappa/(\pi n_g) \approx 25$$ nm {% include cite.html keys="ebeampdk" %}.

</div>

## <span class="secnum">13.3</span>The transfer-matrix method

Real gratings are rarely uniform, so they are modelled by cutting them into sections, each described by the 2 × 2 matrix that relates forward and backward amplitudes at its two ends, and multiplying the matrices. The reflectivity of the whole grating is read from the product. This **transfer-matrix method** handles apodisation, chirp and phase shifts with no extra effort, and it is what the demo below computes, section by section.

**Try it.** Change the period, coupling and number of periods, apodise the grating or add a quarter-wave shift; the geometry shows a magnified stretch linked to the whole grating.

{% include demos/bragg.html %}

## <span class="secnum">13.4</span>Apodisation and chirp

A uniform grating's spectrum has strong **side lobes**, because its abrupt ends act like a rectangular window in a Fourier transform. Tapering the coupling smoothly from zero at the ends to a maximum in the middle, **apodisation**, suppresses them, at the cost of a slightly lower and narrower main peak, exactly as a window function does in signal processing. In sidewall gratings the coupling is tapered by varying the corrugation width or by misaligning the corrugations on the two sidewalls, which partly cancels them.

**Chirping** the period along the grating makes different wavelengths reflect at different depths, which broadens the stop-band and gives a wavelength-dependent delay: a dispersion compensator on a chip.

## <span class="secnum">13.5</span>Cavities

Insert a quarter-wave section, a phase shift of half a period, in the middle of a uniform grating, and the two halves become two mirrors facing each other with exactly the right spacing for one resonance at the Bragg wavelength. A narrow transmission peak opens in the middle of the stop-band. The **λ/4-shifted grating** is a compact, high-Q filter and the heart of the single-mode **DFB laser** ([Chapter 26]({% link chapters/26_tunable.md %})). Two separate gratings with a spacer between them form a Fabry–Pérot cavity, the mirrors of the **DBR laser**.

## <span class="secnum">13.6</span>Contra-directional couplers and SWG metamaterials

A Bragg grating reflects into the same waveguide, so the reflected light must be separated with a circulator, which does not exist on silicon. A **contra-directional coupler** solves this: two waveguides of different widths are coupled through a grating whose period matches the sum of their propagation constants, $$\lambda = \Lambda(n_{\mathrm{eff},1} + n_{\mathrm{eff},2})$$, so the reflected band leaves through the other waveguide. It is an add-drop filter with a flat top and no free spectral range, unlike a ring, and is used for wideband WDM channels.

When the period is much shorter than the Bragg period, $$\Lambda \ll \lambda/(2n_\mathrm{eff})$$, nothing is reflected at all: the segmented waveguide behaves as a homogeneous **subwavelength-grating (SWG) metamaterial** whose index is set by the fill factor ([Chapter 6]({% link chapters/06_soi.md %})).

## <span class="secnum">13.7</span>Photonic crystals

Periodicity in two or three dimensions extends these ideas. A silicon slab perforated with a lattice of holes has a **photonic band gap** for in-plane light; removing a row of holes makes a waveguide whose modes can be slowed to group indices of tens or more (slow light), and removing a few holes makes a cavity with Q in the millions and a mode volume of about a cubic wavelength. Photonic-crystal cavities and waveguides are research favourites for sensing, nonlinear optics and ultra-small lasers, but their sensitivity to fabrication keeps them out of most foundry PDKs.

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
