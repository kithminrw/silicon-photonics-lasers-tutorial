---
title: "3. Gaussian Beams and Optical Fibres"
parent: "Part I · Foundations"
nav_order: 3
permalink: /part-1/ch03/
chapter: 3
---

# <span class="chapnum">Chapter 3</span>Gaussian Beams and Optical Fibres

The beam that leaves a laser and the mode that travels down a fibre are both, to a very good approximation, Gaussian.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the paraxial wave equation and its Gaussian-beam solution;
- compute a beam's radius, wavefront curvature, Rayleigh range, divergence and Gouy phase;
- propagate a beam through lenses with the complex q-parameter and ABCD matrices;
- describe standard single-mode fibre: V-number, cut-off, mode-field diameter, loss and dispersion bands;
- compute the coupling efficiency between two modes, including size mismatch, offset and tilt.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much light gets from one Gaussian mode into another, and how precisely must the two be aligned?

</div>

## <span class="secnum">3.1</span>The paraxial wave equation

A laser beam is not a plane wave: it has a finite width, and so it must spread. To describe it, write the field as a fast carrier times a slowly varying envelope, $$E = A(x,y,z)\,e^{-jkz}$$ with $$k = nk_0$$, and substitute into the Helmholtz equation of [Chapter 2]({% link chapters/02_em.md %}):

$$\nabla_T^2 A + \frac{\partial^2A}{\partial z^2} - 2jk\frac{\partial A}{\partial z} = 0.$$

If the envelope changes little over a wavelength along $$z$$, $$\lvert \partial^2A/\partial z^2\rvert  \ll \lvert 2k\,\partial A/\partial z\rvert $$, and the middle term can be dropped. What remains is the **paraxial wave equation**,

$$\nabla_T^2 A = 2jk\frac{\partial A}{\partial z},$$

which has the same form as the diffusion equation and the Schrödinger equation. It holds for beams whose rays make small angles with the axis, which in practice means divergence half-angles below about 20–30°.

## <span class="secnum">3.2</span>The Gaussian beam

The lowest-order solution of the paraxial equation is the **Gaussian beam**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">The Gaussian beam</div>

$$A(r,z) = A_0\,\frac{w_0}{w(z)}\exp\!\left(-\frac{r^2}{w(z)^2}\right)\exp\!\left(-\frac{jkr^2}{2R(z)}\right)e^{j\zeta(z)}$$

$$w(z) = w_0\sqrt{1 + (z/z_R)^2},\qquad R(z) = z\left[1 + (z_R/z)^2\right],\qquad \zeta(z) = \arctan(z/z_R),\qquad z_R = \frac{\pi w_0^2 n}{\lambda_0}$$

</div>

Here $$r$$ is the distance from the axis, $$w(z)$$ the **beam radius** (where the intensity has fallen to $$1/e^2$$ of its peak; twice it is the mode-field diameter, MFD), $$w_0$$ the radius at the **waist**, $$R(z)$$ the radius of curvature of the wavefronts, and $$\zeta(z)$$ the **Gouy phase**, an extra phase of π/2 that the beam slips through on each side of its focus.

The **Rayleigh range** $$z_R$$ is the distance over which the beam stays nearly collimated: there its area has doubled ([Figure 3.1](#fig-3-1)). Far from the waist the beam spreads as a cone with half-angle

$$\theta_0 \approx \frac{\lambda_0}{\pi n w_0}.$$

A small spot diverges fast and a large one slowly, a direct consequence of diffraction. The fraction of the power inside a radius $$w$$ is $$1 - e^{-2} = 86.5\ \%$$. Real beams are not perfect Gaussians; the factor $$M^2 \geq 1$$ by which a beam diverges faster than a Gaussian of the same waist measures how far from ideal it is.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.1 · Two spots, two divergences</div>

The output of a semiconductor laser or a silicon edge coupler might have $$w_0 = 1.5$$ µm. At 1550 nm in air its Rayleigh range is $$\pi(1.5)^2/1.55 = 4.6$$ µm and it diverges at $$\theta_0 = 1.55/(\pi\times1.5) = 0.33$$ rad, or 19°. The mode of a standard single-mode fibre has $$w_0 \approx 5.2$$ µm: $$z_R = 55$$ µm and $$\theta_0 = 5.4°$$. Butt-coupling the small spot straight into the fibre therefore needs a gap well below 5 µm, and even then the spot sizes do not match (Section 3.5). A lens, or a mode converter on the chip, is needed.

</div>

<figure id="fig-3-1">
  <img src="{{ '/assets/figs/ch03_beam.svg' | relative_url }}" style="width:640px" alt="(a) Field of a Gaussian beam with a 1.5 µm waist at 1550 nm, drawn to scale over 32 µm, with the beam radius, the 19 degree asymptotes, the Rayleigh range of 4.6 µm on each side, and a curved wavefront of radius 9.1 µm at the Rayleigh range. (b) Beam radius against distance for waists of 1.5 and 5.2 µm. (c) Normalised beam radius, wavefront radius and Gouy phase against z over z_R">
  <figcaption><span class="capnum">Figure 3.1.</span> <strong>Anatomy of a Gaussian beam.</strong> (a) The field of the 1.5 µm spot of Worked Example 3.1 at 1550 nm in air, to scale: the beam radius w(z) (dashed) grows from \(w_0\) to \(\sqrt{2}\,w_0\) at \(\pm z_R\) = ±4.6 µm and then follows the asymptotes at θ<sub>0</sub> = 19° (dotted). The wavefronts are flat at the waist and most curved at \(z_R\), where \(R = 2z_R\). (b) The two spots of Worked Example 3.1: the 1.5 µm spot is wider than the 5.2 µm fibre mode beyond only 16 µm. (c) Beam radius, wavefront radius and Gouy phase against \(z/z_R\), the same for every Gaussian beam. Drawn by <code>figsrc/ch03_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">3.3</span>Beam transformation with q and ABCD

The beam radius and the wavefront curvature combine into one complex number, the **q-parameter**:

$$\frac{1}{q(z)} = \frac{1}{R(z)} - j\frac{\lambda_0}{\pi n w(z)^2}, \qquad q(z) = z + jz_R \ \ \text{(measured from the waist)}.$$

Its power is that any paraxial optical system described by a ray-transfer matrix $$\begin{pmatrix}A & B\\ C & D\end{pmatrix}$$ transforms it by one rule {% include cite.html keys="kogelnik1966" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">The ABCD law</div>

$$q_2 = \frac{Aq_1 + B}{Cq_1 + D}, \qquad \text{free space } d:\ \begin{pmatrix}1 & d\\ 0 & 1\end{pmatrix}, \qquad \text{thin lens } f:\ \begin{pmatrix}1 & 0\\ -1/f & 1\end{pmatrix}$$

</div>

Chaining matrices for a sequence of elements and applying the law once gives the beam anywhere. For a beam with waist $$w_0$$ a distance $$d_1$$ before a thin lens, the lens forms a new waist $$w_0' = M w_0$$ at a distance $$d_2$$ behind it, with

$$M = \frac{f}{\sqrt{(d_1 - f)^2 + z_R^2}}, \qquad d_2 = f + \frac{(d_1 - f)f^2}{(d_1 - f)^2 + z_R^2}.$$

When $$z_R \ll \lvert d_1 - f\rvert $$ these reduce to the familiar ray-optics magnification and imaging condition ([Figure 3.2](#fig-3-2)).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.2 · Imaging a laser spot onto a fibre</div>

Image the 1.5 µm spot of Example 3.1 ($$z_R = 4.6$$ µm) with a lens of focal length $$f = 100$$ µm placed $$d_1 = 130$$ µm away:

$$M = \frac{100}{\sqrt{30^2 + 4.6^2}} = 3.30, \qquad w_0' = 4.94\ \mu\mathrm{m}, \qquad d_2 = 100 + \frac{30\times100^2}{30^2 + 4.6^2} = 426\ \mu\mathrm{m}.$$

A fibre with $$w = 5.2$$ µm placed 426 µm behind the lens collects 99.7 % of the light (Section 3.5). Micro-lenses and ball lenses in laser packages do exactly this.

</div>

<figure id="fig-3-2">
  <img src="{{ '/assets/figs/ch03_lens.svg' | relative_url }}" style="width:640px" alt="(a) Schematic of a source waist imaged by a thin lens to a new waist, with the distances d1 and d2 and the ray-transfer matrices of free space, the lens and free space. (b) Lens-to-waist distance and (c) magnification against the source-to-lens distance for a 1.5 µm spot and a 100 µm lens, for Gaussian beams and ray optics, with Worked Example 3.2 marked at d1 = 130 µm">
  <figcaption><span class="capnum">Figure 3.2.</span> <strong>Imaging a waist with a lens.</strong> (a) The source waist, the thin lens and the image waist, with the ray-transfer matrix of each section (schematic). (b) Where the image waist forms and (c) its magnification, against the source-to-lens distance, for the 1.5 µm spot (\(z_R\) = 4.6 µm) and \(f\) = 100 µm. Gaussian beams (solid) follow ray optics (dashed) except within a few \(z_R\) of \(d_1 = f\): there ray optics sends the image to infinity, while a Gaussian waist forms at most \(f + f^2/2z_R\) ≈ 1.2 mm behind the lens and its magnification peaks at \(f/z_R\) ≈ 22. Worked Example 3.2 (dot) is in the ray-optics regime: M = 3.30 and \(d_2\) = 426 µm, against 433 µm from ray optics. Drawn by <code>figsrc/ch03_figs.py</code>.</figcaption>
</figure>

**Try it.** Focus the source with the lens, move the fibre, and watch the coupling and its tolerance.

{% include demos/gaussian.html %}

## <span class="secnum">3.4</span>Optical fibres

A step-index fibre has a core of radius $$a$$ and index $$n_1$$ inside a cladding of index $$n_2$$, slightly lower. Its guiding strength is summed up by the **numerical aperture** and the **V-number**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Numerical aperture, V-number and single-mode condition</div>

$$\mathrm{NA} = \sqrt{n_1^2 - n_2^2} \approx n_1\sqrt{2\Delta}, \qquad V = \frac{2\pi a}{\lambda_0}\,\mathrm{NA}, \qquad \text{single-mode for } V < 2.405$$

</div>

with $$\Delta = (n_1 - n_2)/n_1$$. Because $$\Delta$$ is small (0.3–0.4 % in standard fibre), the modes are almost linearly polarised and are labelled LP$$_{lm}$$ {% include cite.html keys="gloge1971" %}. Solving the wave equation in the core (Bessel functions $$J_l$$) and the cladding (modified Bessel functions $$K_l$$) and matching them at $$r = a$$ gives the characteristic equation

$$u\,\frac{J_{l-1}(u)}{J_l(u)} = -w\,\frac{K_{l-1}(w)}{K_l(w)}, \qquad u^2 + w^2 = V^2,$$

where $$u$$ and $$w$$ are the transverse wavenumbers in the core and cladding scaled by $$a$$. The fundamental mode LP$$_{01}$$ is always guided; the next, LP$$_{11}$$, appears at $$V = 2.405$$, the first zero of $$J_0$$. The **cut-off wavelength** $$\lambda_c = 2\pi a\,\mathrm{NA}/2.405$$ is the shortest wavelength at which the fibre is single-mode.

Near cut-off the LP$$_{01}$$ field is close to a Gaussian ([Figure 3.3](#fig-3-3)), and its radius is well approximated by **Marcuse's formula** {% include cite.html keys="marcuse1977" %}:

$$\frac{w}{a} \approx 0.65 + \frac{1.619}{V^{3/2}} + \frac{2.879}{V^6}.$$

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.3 · Standard single-mode fibre</div>

Take a core radius of 4.1 µm and $$\Delta = 0.36\ \%$$, close to standard (G.652) fibre {% include cite.html keys="itug652" %}. With $$n_2 = 1.444$$, $$n_1 = 1.449$$ and NA = 0.123. The cut-off is $$\lambda_c = 2\pi\times4.1\times0.123/2.405 = 1.32$$ µm, so this model fibre is single-mode above about 1.32 µm. Real G.652 fibre is specified by its cabled cut-off, at most 1260 nm, so in practice it is single-mode across the whole O band. At 1550 nm, $$V = 2.04$$ and Marcuse gives $$w = 5.10$$ µm, an MFD of 10.2 µm; at 1310 nm, $$V = 2.42$$ and MFD = 9.0 µm. Data sheets quote about 10.4 and 9.2 µm, measured rather than modelled.

</div>

<figure id="fig-3-3">
  <img src="{{ '/assets/figs/ch03_fibre.svg' | relative_url }}" style="width:640px" alt="(a) End face of a standard single-mode fibre to scale: a 250 µm coating, 125 µm cladding and 8.2 µm core, and a zoom on the core showing the mode intensity, mode-field diameters of 10.2 µm at 1550 nm and 9.0 µm at 1310 nm, and a 500 by 220 nm silicon wire at the same scale. (b) LP01 field against radius at 1310 and 1550 nm with the Gaussian approximations, the core shaded">
  <figcaption><span class="capnum">Figure 3.3.</span> <strong>Standard single-mode fibre.</strong> (a) An end face to scale: an 8.2 µm core in 125 µm of cladding {% include cite.html keys="itug652" %}, inside a typical 250 µm coating; the zoom shows the mode intensity at 1550 nm, the mode-field diameters at 1550 nm (10.2 µm) and 1310 nm (9.0 µm), and a 500 × 220 nm silicon wire at the same scale. (b) The exact LP<sub>01</sub> field of the step-index model of Worked Example 3.3 at both wavelengths, with Marcuse's Gaussians (dashed). At the longer wavelength the field reaches further into the cladding; the Gaussians still overlap the exact fields by 99.2 % (1550 nm) and 99.7 % (1310 nm). Drawn by <code>figsrc/ch03_figs.py</code>.</figcaption>
</figure>

**Try it.** Change the core radius, NA and wavelength, and see which LP modes are guided and how well LP01 matches a Gaussian.

{% include demos/fiber.html %}

Silica fibre is used in six telecom bands: O (1260–1360 nm), E (1360–1460), S (1460–1530), C (1530–1565), L (1565–1625) and U (1625–1675 nm), the last mostly for monitoring. Loss is about 0.35 dB/km in the O band and about 0.2 dB/km in the C band, where it is lowest; the C and L bands are also where erbium-doped amplifiers work. Chromatic dispersion is close to zero near 1310 nm and about 17 ps/(nm·km) at 1550 nm ([Chapter 2]({% link chapters/02_em.md %}), [Figure 3.4](#fig-3-4)).

<figure id="fig-3-4">
  <img src="{{ '/assets/figs/ch03_bands.svg' | relative_url }}" style="width:640px" alt="(a) Fibre loss falling from 0.40 dB/km at 1260 nm to 0.17 dB/km at 1625 nm, through 0.35 dB/km at 1310 nm and 0.2 dB/km at 1550 nm, with the O, E, S, C and L bands shaded. (b) Chromatic dispersion of the step-index fibre model rising from about −3 to 21 ps/(nm·km), zero at 1296 nm and 17.1 at 1550 nm, with the dispersion of silica alone for comparison">
  <figcaption><span class="capnum">Figure 3.4.</span> <strong>Loss and dispersion across the bands.</strong> (a) Loss modelled as Rayleigh scattering (∝ λ<sup>−4</sup>) plus a constant, set to the typical 0.35 dB/km at 1310 nm and 0.2 dB/km at 1550 nm; real fibre also absorbs in the infrared beyond about 1.6 µm, and near 1383 nm unless it is of the low-water-peak kind. (b) Chromatic dispersion of the step-index model of Worked Example 3.3, from the exact LP<sub>01</sub> effective index with Malitson's silica in core and cladding {% include cite.html keys="malitson1965" %}: 17.1 ps/(nm·km) at 1550 nm and zero at 1296 nm. The waveguide's own dispersion moves the zero from silica's 1272 nm (dashed) to longer wavelengths. Drawn by <code>figsrc/ch03_figs.py</code>.</figcaption>
</figure>

Three special fibres appear in photonic-chip work. **Polarisation-maintaining (PM)** fibres have stress rods that make them strongly birefringent, so light launched along one axis stays there; fibre arrays for testing grating couplers usually use them ([Chapter 17]({% link chapters/17_fiberarrays.md %})). **High-NA** fibres have small cores and spots of about 3–4 µm, closer to on-chip modes. **Lensed fibres** have a shaped tip that focuses the mode to a spot of about 2–3 µm for edge coupling ([Chapter 16]({% link chapters/16_edge.md %})).

## <span class="secnum">3.5</span>Mode overlap and coupling efficiency

When light in one mode $$E_1$$ arrives at a plane where it must enter another mode $$E_2$$, such as at a fibre facet or a waveguide junction, the fraction of power coupled is the **overlap integral**:

$$\eta = \frac{\left\lvert \iint E_1E_2^*\,\mathrm{d}A\right\rvert ^2}{\iint\lvert E_1\rvert ^2\,\mathrm{d}A\iint\lvert E_2\rvert ^2\,\mathrm{d}A}.$$

The rest is reflected or radiated. For two circular Gaussian modes with radii $$w_1$$ and $$w_2$$, flat wavefronts and parallel axes, the integral has closed forms:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Coupling between Gaussian modes</div>

$$\eta = \underbrace{\left(\frac{2w_1w_2}{w_1^2 + w_2^2}\right)^2}_{\text{size mismatch}}\;\underbrace{\exp\!\left(-\frac{2d^2}{w_1^2 + w_2^2}\right)}_{\text{lateral offset } d}\;\underbrace{\exp\!\left(-\frac{2\pi^2n^2\theta^2w_1^2w_2^2}{\lambda_0^2(w_1^2 + w_2^2)}\right)}_{\text{tilt } \theta}$$

</div>

and two equal modes separated by an axial gap $$z$$ couple $$\eta = 1/\left[1 + (z/2z_R)^2\right]$$. [Figure 3.5](#fig-3-5) plots the first two factors.

<figure id="fig-3-5">
  <img src="{{ '/assets/figs/ch03_overlap.svg' | relative_url }}" style="width:720px" alt="Coupling efficiency against lateral offset for three spot sizes, and against waist ratio">
  <figcaption><span class="capnum">Figure 3.5.</span> <strong>Coupling between Gaussian modes.</strong> (a) Against lateral offset, from a standard fibre mode (w = 5.2 µm) into modes of 5.2, 2.5 and 1.5 µm; the dashed line is 1 dB below a perfect match. (b) Against the ratio of the waists, at zero offset: a factor of two either way costs 1.9 dB. Drawn by <code>figsrc/part1_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 3.4 · Mismatch and tolerance</div>

Butt-coupling a standard fibre ($$w = 5.2$$ µm) to a 1.5 µm on-chip spot gives $$\eta = (2\times5.2\times1.5/29.29)^2 = 0.28$$, or −5.5 dB, before any misalignment; a 2.5 µm spot gives −2.1 dB. Between two standard fibres, the 1 dB tolerances are a lateral offset of $$d = \sqrt{0.115\times2\times5.2^2} = 2.5$$ µm and a tilt of 2.6° in air. Because the tolerances scale with the spot size, an edge coupler that expands its mode to match the fibre is both more efficient and easier to align.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Coupling to fibre is a mode-matching problem. On-chip silicon modes are a few hundred nanometres across and fibre modes ten micrometres, a factor of about twenty-five in diameter: without help, almost all the light is lost. Every fibre coupler in Part IV is a way of building a large, Gaussian-like mode on the chip, by diffraction from a grating ([Chapter 15]({% link chapters/15_gc.md %})) or by an inverse taper that lets the mode expand ([Chapter 16]({% link chapters/16_edge.md %})), and the alignment tolerances of Chapter 17 follow from the same overlap integral.

</div>

## <span class="secnum">3.6</span>Gaussian beams in photonic chips

Gaussian beams turn up wherever light leaves a waveguide. A **grating coupler** radiates a beam about the size of a fibre mode, tilted by around 10° from the vertical; its profile is closer to an exponential than to a Gaussian unless the grating is apodised, which costs about 1 dB of overlap ([Chapter 15]({% link chapters/15_gc.md %})). An **edge coupler** produces a spot of a few micrometres at the facet, matched to a lensed or high-NA fibre ([Chapter 16]({% link chapters/16_edge.md %})). A **semiconductor laser** emits an elliptical, strongly diverging beam, often tens of degrees in one direction and less in the other, which micro-optics reshape for a fibre or for a silicon chip ([Chapter 27]({% link chapters/27_lasersonsi.md %})). And 3D-printed micro-lenses and photonic wire bonds now let the beam be shaped right at the chip ([Chapter 17]({% link chapters/17_fiberarrays.md %})).

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: optical fibre mode explorer](https://s3.amazonaws.com/fip-16/Fiber-Mode-Explorer/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="kogelnik1966,salehteich,siegman,snyderlove,gloge1971,marcuse1977" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A Gaussian beam is set by its waist: $$z_R = \pi w_0^2n/\lambda_0$$ and $$\theta_0 = \lambda_0/(\pi nw_0)$$. Small spots diverge fast.
- The q-parameter and ABCD matrices propagate a beam through lenses and gaps; a lens images a waist with magnification $$f/\sqrt{(d_1 - f)^2 + z_R^2}$$.
- Standard single-mode fibre is single-mode for $$V < 2.405$$ (cut-off about 1.3 µm) and has an MFD of about 10.4 µm at 1550 nm and 9.2 µm at 1310 nm.
- Coupling is a mode overlap. A waist mismatch of two costs 1.9 dB; a 5.2 µm to 1.5 µm mismatch costs 5.5 dB; between fibres the 1 dB tolerance is about 2.5 µm laterally and 2.6° in tilt.
- Fibre couplers exist to build a large, Gaussian-like mode on the chip.

</div>

## Problems

1. **A lensed-fibre spot.** A lensed fibre focuses 1550 nm light in air to a waist $$w_0 = 1.25$$ µm. Find its Rayleigh range and divergence half-angle, and its beam radius, wavefront radius and Gouy phase 10 µm beyond the waist. If an edge coupler with the same mode size sits 2 µm from the waist instead of at it, what fraction of the power couples?

    <details markdown="1">
    <summary>Solution</summary>

    The Rayleigh range is $$z_R = \pi w_0^2/\lambda_0 = \pi(1.25)^2/1.55 = 3.17$$ µm and the divergence $$\theta_0 = \lambda_0/(\pi w_0) = 1.55/(\pi\times1.25) = 0.395$$ rad, or 22.6°. At $$z = 10$$ µm,

    $$w = 1.25\sqrt{1 + (10/3.17)^2} = 4.14\ \mu\mathrm{m}, \qquad R = 10\left[1 + (3.17/10)^2\right] = 11.0\ \mu\mathrm{m}, \qquad \zeta = \arctan(10/3.17) = 1.26\ \mathrm{rad}.$$

    Two equal modes 2 µm apart couple $$\eta = 1/\left[1 + (2/6.33)^2\right] = 0.91$$, a loss of 0.41 dB. A spot this small diverges near the limit of the paraxial picture (20–30°), and the chip facet must sit within a couple of micrometres of its waist.

    </details>

2. **A high-NA fibre.** A high-NA fibre has a core radius $$a = 1.5$$ µm and NA = 0.35. Find its cut-off wavelength and its V-number at 1550 nm, then use Marcuse's formula for its mode radius and MFD. How well does it butt-couple to a 1.5 µm on-chip spot, compared with standard fibre (Worked Example 3.4)?

    <details markdown="1">
    <summary>Solution</summary>

    The cut-off is $$\lambda_c = 2\pi a\,\mathrm{NA}/2.405 = 2\pi\times1.5\times0.35/2.405 = 1.37$$ µm, so the fibre is single-mode at 1550 nm, where $$V = 2\pi\times1.5\times0.35/1.55 = 2.13$$. Marcuse's formula gives

    $$\frac{w}{a} = 0.65 + \frac{1.619}{2.13^{3/2}} + \frac{2.879}{2.13^6} = 0.65 + 0.522 + 0.031 = 1.20,$$

    so $$w = 1.80$$ µm and the MFD is 3.6 µm. The size-mismatch factor to a 1.5 µm spot is $$\eta = [2\times1.80\times1.5/(1.80^2 + 1.5^2)]^2 = 0.97$$, a loss of 0.15 dB, against 5.5 dB for standard fibre. A fibre with a small mode does the mode matching for the chip; the mismatch then moves to the joint between this fibre and standard fibre.

    </details>

3. **Matching a laser spot to a fibre.** With the 1.5 µm spot of Worked Example 3.2 ($$z_R = 4.6$$ µm) and the same lens ($$f = 100$$ µm), choose the source-to-lens distance $$d_1$$ that makes the image waist equal to the fibre's 5.2 µm, and find where the fibre must sit. Compare $$d_2$$ with what ray optics predicts.

    <details markdown="1">
    <summary>Solution</summary>

    The magnification must be $$M = 5.2/1.5 = 3.467$$. From $$M = f/\sqrt{(d_1 - f)^2 + z_R^2}$$,

    $$(d_1 - f)^2 = \left(\frac{f}{M}\right)^2 - z_R^2 = 28.85^2 - 4.6^2 = 811\ \mu\mathrm{m}^2, \qquad d_1 = 100 + 28.5 = 128.5\ \mu\mathrm{m}.$$

    The other root, $$d_1 = 71.5$$ µm, puts the source inside the focal length and gives only a virtual waist in front of the lens. Then $$d_2 = f + (d_1 - f)f^2/[(d_1 - f)^2 + z_R^2] = 100 + 28.48\times100^2/832 = 442$$ µm, against $$1/(1/f - 1/d_1) = 451$$ µm from ray optics. Moving the source 1.5 µm closer to the lens than in Worked Example 3.2 moves the image waist 16 µm further away: the image side is the forgiving one, because the fibre mode's Rayleigh range is 55 µm.

    </details>

4. **The alignment trade-off.** For two equal Gaussian modes of radius $$w$$, use the offset and tilt factors of the coupling equation to find the lateral offset $$d_\mathrm{1dB}$$ and the tilt $$\theta_\mathrm{1dB}$$ that each cost 1 dB. Show that their product does not depend on $$w$$, and evaluate it at 1550 nm in air. What does this mean for an edge coupler that expands its mode?

    <details markdown="1">
    <summary>Solution</summary>

    With $$w_1 = w_2 = w$$ the offset factor is $$\exp(-d^2/w^2)$$ and the tilt factor $$\exp(-\pi^2n^2\theta^2w^2/\lambda_0^2)$$. A 1 dB loss is a factor $$10^{-0.1} = e^{-0.230}$$, so

    $$d_\mathrm{1dB} = 0.480\,w, \qquad \theta_\mathrm{1dB} = 0.480\,\frac{\lambda_0}{\pi nw}, \qquad d_\mathrm{1dB}\,\theta_\mathrm{1dB} = 0.230\,\frac{\lambda_0}{\pi n}.$$

    At 1550 nm in air the product is 0.114 µm·rad. For standard fibre ($$w = 5.2$$ µm) it splits into 2.5 µm and 0.045 rad (2.6°), as in Worked Example 3.4; for a 1.5 µm spot, into 0.72 µm and 0.158 rad (9.0°). Expanding a mode relaxes the lateral tolerance and tightens the angular one in proportion, because diffraction fixes the product, just as it fixes $$w_0\theta_0 = \lambda_0/\pi n$$.

    </details>

## Check yourself

{% include quiz.html %}
