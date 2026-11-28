---
title: "Lab 14. Coupling light into chips"
parent: Hands-On Labs
nav_order: 14
permalink: /labs/lab-14/
---

# <span class="chapnum">Lab 14 · Simulate and measure</span>Coupling Light into Chips: Overlaps, Printed Lenses and Fibre Arrays

Check the overlap formulas of Chapter 17 on a grid, rebuild the test-interface table of Chapter 36, trace rays through a printed lens, and find out how often every channel of a fibre array is aligned at once.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- compute mode overlaps numerically and compare them with the closed forms for offset, tilt and gap;
- reproduce the 1 dB tolerances of four test interfaces (Table 36.1);
- design a facet-attached lens and check, by tracing rays, that its ellipsoidal surface collimates where a sphere does not;
- run a Monte Carlo of an eight-fibre array and compare a lensed fibre array with printed lenses on both sides.

</div>

## What you need

- [Chapter 17]({% link chapters/17_fiberarrays.md %}) (Sections 17.2 and 17.5) and [Chapter 36]({% link chapters/36_testing.md %}) (Section 36.8); [Chapter 3]({% link chapters/03_gaussian.md %}) for Gaussian beams.
- Python 3.11 or newer with NumPy and Matplotlib.
- The script <a href="{{ '/labs/lab14_coupling.py' | relative_url }}" download><code>lab14_coupling.py</code></a>.
- About an hour and a half.

Run `python lab14_coupling.py`. It prints a checkpoint for each part and saves `lab14_coupling.png`.

## <span class="secnum">L14.1</span>Overlaps on a grid

`gauss_field` writes a Gaussian beam's complex field from its $$q$$ parameter, with an optional offset and tilt; `overlap` computes $$\lvert\int E_1E_2^*\rvert^2/(\int\lvert E_1\rvert^2\int\lvert E_2\rvert^2)$$ on a 601 × 601 grid. For an SMF-28 mode (5.2 µm) over a grating coupler's beam (4.6 µm), the grid and the closed form of Section 17.2 agree to five digits.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

Aligned: 0.98512 (−0.065 dB, the size mismatch). Offset 2.35 µm: 0.78338, −1.06 dB (Worked Example 17.1: 1 dB at 2.35 µm). Tilt 2°: 0.87474. A 10 µm air gap costs 0.045 dB (Worked Example 17.1: 0.05 dB).

</div>

## <span class="secnum">L14.2</span>Four test interfaces

`part_b` finds the 1 dB offset, tilt and gap of each interface by bisection.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

Grating couplers ±2.36 µm, ±2.78°, 49.7 µm; high-NA fibres ±0.91 µm, ±7.17°, 7.5 µm; lensed fibres ±0.60 µm, ±10.85°, 3.2 µm; printed lenses on both sides ±6.00 µm, ±1.09°, 322 µm (Table 36.1: the same, rounded).

</div>

## <span class="secnum">L14.3</span>A printed lens, ray by ray

`lens_design` gives the polymer length that expands a 2.5 µm mode to a 25 µm beam and the radius of the wavefront that reaches the surface. `trace` sends rays from the wavefront's centre of curvature, refracts them at the surface with the vector form of Snell's law, and returns their angle in air. The ellipse of eccentricity $$1/n$$ (Section 17.5) sends every ray out parallel to the axis. A sphere with the same apex radius agrees near the axis, but bends edge rays inwards: spherical aberration.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

Rayleigh range 4.85 µm in the resist, lens length 48.2 µm, wavefront radius 48.7 µm, apex radius 16.9 µm (Section 17.5: 48 µm and 17 µm). Rays up to 1.5 times the beam's half-angle (14.8°) leave the ellipse within 10⁻¹³ degrees of the axis. The sphere: −0.09° at 0.32 of the half-angle, −2.68° at 0.91, −8.91° at 1.20, and at 1.50 the ray misses the cap.

</div>

## <span class="secnum">L14.4</span>Every channel at once

`part_d` draws random spot errors for each of eight channels (core position and lens pointing), a rotation of the array, and angle errors, and records the worst channel of each of 20 000 arrays. The error sizes are illustrative: 0.35 µm per axis for the lensed array, 1.5 µm for printed lenses (which are placed less precisely but forgive more), 0.03° of rotation and 0.3° of pointing.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

Lensed fibre array: worst channel median 1.85 dB, 95th percentile 3.84 dB; all eight channels within 1 dB in 9.1 % of arrays. Printed lenses on both sides: median 0.45 dB, 95th percentile 0.83 dB, all within 1 dB in 98.3 %.

</div>

<figure id="fig-l14-1">
  <img src="{{ '/assets/figs/lab14_expected.png' | relative_url }}" style="width:760px" alt="Three plots from the lab script: coupling change against lateral offset for 2.5 micrometre spots, a fibre over a grating and 25 micrometre beams; rays from a point inside a printed lens leaving its ellipsoidal surface parallel to the axis; and histograms of the worst-channel loss of 20000 simulated eight-fibre arrays, spread out to several decibels for the lensed array and below one decibel for printed lenses">
  <figcaption><span class="capnum">Figure L14.1.</span> <strong>What the script draws.</strong> (a) Offset tolerance of three interfaces. (b) Rays through the collimating ellipse of the Section 17.5 lens, all leaving parallel. (c) Worst-channel loss of 20 000 simulated eight-fibre arrays. Drawn by <code>lab14_coupling.py</code>.</figcaption>
</figure>

## Exercises

1. **A wider beam.** How long must the lenses be, on the chip and on the fibre, for a 40 µm beam?
2. **A better lensed array.** Repeat Part D for the lensed array with spot errors of 0.2 and 0.1 µm. How often are all eight channels within 1 dB?
3. **Why not a sphere?** From Part C, how far off axis does an edge ray leave a spherical lens, and what does that do to the beam?

<details markdown="1">
<summary>Answers</summary>

1. 77.4 µm on the chip and 311.4 µm on the fibre (`lens_design(1.25, 20)` and `lens_design(5.2, 20)`).
2. 77.9 % at 0.2 µm (median worst channel 0.69 dB) and 96.7 % at 0.1 µm (0.23 dB): a lensed array needs about a tenth of a micrometre on every channel to match printed lenses at 1.5 µm.
3. About 3° at the beam's half-angle and 9° beyond it: the edge of the beam converges, so the beam leaving a sphere is not flat, its far field is distorted, and its overlap with the matching lens on the other side falls. Free-form printing makes the aspheric (ellipsoidal) surface as easy as a sphere.

</details>

## Going further

- The faml demo of [Section 17.5]({% link chapters/17_fiberarrays.md %}) and the alignment demo of Section 17.2 draw the same overlaps live.
- Add a tilt between the lens's axis and the waveguide to `trace`, and see how the collimated beam is steered.
