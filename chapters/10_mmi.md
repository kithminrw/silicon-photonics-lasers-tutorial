---
title: "10. Y-Branches and Multimode Interference Couplers"
parent: "Part III · Passive Devices"
nav_order: 10
permalink: /part-3/ch10/
chapter: 10
---

# <span class="chapnum">Chapter 10</span>Y-Branches and Multimode Interference Couplers

Splitting light evenly sounds trivial; doing it over a wide band with tiny loss takes some care.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain the Y-branch, and why a combiner fed from one arm passes only half the power;
- compute which modes an abrupt junction excites, and explain the snaking of an offset input;
- derive the self-imaging lengths of a multimode waveguide;
- design 1 × 2 and 2 × 2 MMIs and estimate their bandwidth and fabrication tolerance;
- choose between directional couplers, Y-branches, MMIs and adiabatic couplers.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Y-branch or MMI, and how long must the MMI be?

</div>

## <span class="secnum">10.1</span>Y-branches

A Y-branch splits one waveguide into two by widening it gradually and separating it into two arms. If the transition is adiabatic ([Chapter 8]({% link chapters/08_bends.md %})), the fundamental mode of the input evolves into the even supermode of the two arms, which carries half the power in each: a 50/50 splitter, symmetric by construction and therefore broadband.

Run backwards, the same device is a combiner, and here it holds a surprise. Feed light into only one arm and it is the sum of an even and an odd supermode of the arms, in equal parts. Only the even supermode evolves into the output's fundamental mode; the odd one has nowhere to go in a single-mode output and radiates away. **A symmetric Y-combiner fed from one arm passes exactly half the power**, and the same is true for two inputs out of phase. This is not a defect but the Y-junction's reciprocity, and it is why a Mach–Zehnder interferometer built from Y-branches loses its light into the substrate rather than into a second output port at its nulls ([Chapter 11]({% link chapters/11_mzi.md %})).

Practical Y-branches face a fabrication limit: the gap between the arms cannot close to zero, and the blunt tip scatters. The compact Y-junction of the SiEPIC EBeam PDK solved this by optimising the shape of a short taper with particle-swarm optimisation in 3D FDTD, reaching an insertion loss of about 0.28 dB {% include cite.html keys="zhang2013,ebeampdk" %}. You can turn it over in the [3D gallery]({% link devices-3d.md %}#dev-siepic-ybranch).

## <span class="secnum">10.2</span>Mode excitation at an abrupt junction

When a narrow waveguide meets a wide one abruptly, its mode $$E_\mathrm{in}$$ is projected onto the modes $$\phi_\nu$$ of the wide section, with amplitudes given by overlap integrals ([Chapter 8]({% link chapters/08_bends.md %})):

$$c_\nu = \frac{\int E_\mathrm{in}\,\phi_\nu^*\,\mathrm{d}x}{\int\lvert\phi_\nu\rvert^2\,\mathrm{d}x}.$$

Symmetry decides a lot. A centred input is even, so it has zero overlap with every odd mode ($$\nu = 1, 3, 5, \dots$$) and excites only even ones. An input offset from the centre excites both; the even and odd modes then beat against each other as they travel, and the intensity snakes from side to side across the wide guide. The pattern is fixed in space, not travelling: it is the interference of modes with different propagation constants.

## <span class="secnum">10.3</span>Self-imaging in a multimode waveguide

The multimode section of width $$W$$ supports many modes. In the effective-index picture it is a slab of index $$n_r$$ (the vertical slab index of the film, [Chapter 6]({% link chapters/06_soi.md %})) in a cladding $$n_c$$, and its modes are close to sines across an **effective width** that includes the penetration of the field into the cladding,

$$W_e = W + \frac{\lambda_0}{\pi}\left(\frac{n_c}{n_r}\right)^{2\sigma}\left(n_r^2 - n_c^2\right)^{-1/2}, \qquad \sigma = \begin{cases} 0 & \text{field parallel to the side walls,} \\ 1 & \text{field normal to the side walls.} \end{cases}$$

The TE-like modes of an SOI waveguide have their electric field normal to the side walls: in the effective-index method of [Chapter 6]({% link chapters/06_soi.md %}) their lateral slab is TM. So they take $$\sigma = 1$$, and the field reaches only $$(n_c/n_r)^2 \approx 0.26$$ times as far into the oxide as a field parallel to the walls would.

The propagation constants of these modes are spaced quadratically, $$\beta_0 - \beta_\nu \approx \nu(\nu + 2)\pi/(3L_\pi)$$, with the **beat length** of the two lowest modes

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">MMI beat length</div>

$$L_\pi = \frac{\pi}{\beta_0 - \beta_1} \approx \frac{4n_rW_e^2}{3\lambda_0}$$

</div>

Because $$\nu(\nu + 2)$$ is always either even or odd times a fixed step, all the modes come back into a definite phase relation at regular lengths, and the input field is reproduced: **self-imaging** {% include cite.html keys="soldano1995" %}. Three regimes follow from which modes the input excites:

- **General interference** (any input): a mirrored single image at $$3L_\pi$$, a direct one at $$6L_\pi$$, and $$N$$-fold images at $$3L_\pi/N$$ in between, such as two images at $$3L_\pi/2$$, the basis of the 2 × 2 MMI.
- **Paired interference** (input at $$\pm W_e/6$$, where some modes are not excited): images at $$L_\pi$$, two-fold at $$L_\pi/2$$; shorter 2 × 2 couplers.
- **Symmetric interference** (centred input, only even modes): $$N$$-fold images at $$3L_\pi/(4N)$$, four times shorter; a 1 × 2 splitter needs only $$3L_\pi/8$$.

**Try it.** Change the MMI's width, length and input offset, and watch the self-images form in the field and in the intensity map.

{% include demos/mmi.html %}

## <span class="secnum">10.4</span>MMI design

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 10.1 · A 1 × 2 MMI in 220 nm silicon</div>

Take a 6 µm wide multimode section in 220 nm silicon at 1550 nm (TE), with $$n_r = 2.85$$ (the slab index of [Chapter 5]({% link chapters/05_slab.md %})) and $$n_c = 1.444$$. The field is normal to the side walls, so $$\sigma = 1$$ and the effective width is $$W_e = 6 + (1.55/\pi)(1.444/2.85)^2/\sqrt{2.85^2 - 1.444^2} = 6 + 0.052 = 6.052$$ µm, so

$$L_\pi = \frac{4 \times 2.85 \times 6.052^2}{3 \times 1.55} = 89.8\ \mu\mathrm{m}.$$

A centred input gives two images at $$3L_\pi/8 = 33.7$$ µm, at $$\pm W_e/4 = \pm1.51$$ µm from the centre, where the two output waveguides start. A 2 × 2 MMI by general interference needs $$3L_\pi/2 = 135$$ µm; by paired interference, with inputs at $$\pm W_e/6$$, $$L_\pi/2 = 45$$ µm. Taking $$\sigma = 0$$ by mistake would give $$W_e = 6.20$$ µm and a 1 × 2 MMI 35.4 µm long, 1.7 µm too long, which costs about 1 dB ([Lab 3]({% link labs/lab03_couplers.md %})).

</div>

Three practical points shape a real MMI:

- **Tapered access waveguides.** Widening the input and output waveguides to 1–2 µm where they meet the multimode section makes the images sharper and the device less sensitive to the exact length, and reduces the loss from the higher-order modes that the ideal theory neglects.
- **Tolerance.** $$L_\pi$$ grows with $$W_e^2$$, so a 1 % width error moves the images by 2 % of the length, about 0.7 µm in Example 10.1; the image region is roughly that long, so a few tens of nanometres of width error are tolerable.
- **Bandwidth.** $$L_\pi$$ is inversely proportional to wavelength, so the images drift as the wavelength changes; short MMIs (small $$W$$, symmetric interference) are the most broadband. Excess losses of a few tenths of a dB and imbalances of a few per cent over tens of nanometres are typical of good designs.

## <span class="secnum">10.5</span>Comparing splitters

**Table 10.1. Choosing a 3 dB splitter in silicon photonics.**
{: .tabcaption #tab-10-1 }

| Device | Ports | Bandwidth | Strengths | Weaknesses |
|---|---|---|---|---|
| Directional coupler ([Ch 9]({% link chapters/09_couplers.md %})) | 2 × 2 | narrow | any ratio, compact, low loss | ratio drifts with wavelength and gap |
| Y-branch | 1 × 2 | broad | 50/50 by symmetry, small | tip limited by lithography; one-arm combining loses 3 dB |
| MMI | 1 × N, N × N | moderate to broad | robust to fabrication, any N | longer, small excess loss and imbalance |
| Adiabatic coupler | 2 × 2 | broad | ratio set by symmetry, very broadband | long (hundreds of µm) |

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

For a 1 × 2 split on your first chip, the PDK's Y-branch is the safe choice: small, broadband and measured. For a 2 × 2 coupler that must work across the four channels of the reference link, an MMI or an adiabatic coupler beats a directional coupler, whose split ratio drifts by a few per cent per nanometre ([Chapter 9]({% link chapters/09_couplers.md %})).

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter {% include cite.html keys="vmlab" %}:

- [VM-Lab: Y-branch splitter](https://s3.amazonaws.com/fip-4/Splitter/index.html) and [combiner](https://s3.amazonaws.com/fip-4/Combiner/index.html)
- [VM-Lab: waveguide interfaces (mode excitation)](https://s3.amazonaws.com/fip-1/Interfaces/index.html)
- [VM-Lab: MMI geometry](https://s3.amazonaws.com/fip-9/Geometry/index.html) and [wavelength and polarisation](https://s3.amazonaws.com/fip-9/Wavelength-and-Polarization/index.html)

</div>

## Reading

{% include reflist.html keys="soldano1995,zhang2013,chrostowski2015,okamoto" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- An adiabatic Y-branch splits 50/50 by symmetry; as a combiner fed from one arm it passes only half the power.
- An abrupt junction excites the wide section's modes by overlap; centred inputs excite only even modes.
- Self-imaging: $$L_\pi \approx 4n_rW_e^2/(3\lambda_0)$$; images at $$3L_\pi$$ (general), $$L_\pi$$ (paired) and $$3L_\pi/(4N)$$ (symmetric).
- A 6 µm silicon MMI has $$L_\pi = 90$$ µm (TE, $$\sigma = 1$$): a 1 × 2 splitter is 34 µm long, a 2 × 2 coupler 45–135 µm.
- Use Y-branches for compact 1 × 2 splits, MMIs or adiabatic couplers for broadband 2 × 2 splits.

</div>
