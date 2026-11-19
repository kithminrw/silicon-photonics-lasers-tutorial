---
title: "16. Edge Couplers and Spot-Size Converters"
parent: "Part IV · Coupling and Packaging"
nav_order: 16
permalink: /part-4/ch16/
chapter: 16
---

# <span class="chapnum">Chapter 16</span>Edge Couplers and Spot-Size Converters

Coupling at the chip edge is broadband and low-loss, at the price of a prepared facet and tight alignment.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- estimate butt-coupling loss from mode overlap;
- explain how an inverse taper expands the mode, and choose a tip width;
- describe multi-stage, SiN, polymer, SWG and suspended couplers;
- handle facet reflections with angled waveguides, coatings and index matching;
- choose fibres for edge coupling, and compare edge and grating couplers.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How narrow must the taper tip be to match a 3 µm or a 10 µm spot?

</div>

## <span class="secnum">16.1</span>Edge-coupling basics

An **edge coupler** brings the waveguide to a polished or etched facet at the chip edge and couples it end-on, or **butt-couples** it, to a fibre or a laser. There is no grating and no resonance, so the coupling is broadband and can work for both polarisations. Its efficiency is the overlap of the two modes at the facet ([Chapter 3]({% link chapters/03_gaussian.md %})); for Gaussian-like modes of 1/e² radii $$w_x, w_y$$ and a fibre of radius $$w_f$$,

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Butt coupling of two Gaussian modes</div>

$$\eta = \frac{4}{\left(\dfrac{w_x}{w_f} + \dfrac{w_f}{w_x}\right)\left(\dfrac{w_y}{w_f} + \dfrac{w_f}{w_y}\right)}$$

</div>

The trouble is the size mismatch ([Figure 16.1](#fig-16-1)). A 500 × 220 nm silicon strip has a mode about 0.4 µm across; SMF-28's is 10.4 µm. femwell gives an overlap of under 1 % (−21 dB), and even a lensed fibre focused to 2.5 µm reaches only 12 % (−9 dB). Some kind of **spot-size converter** is needed to expand the waveguide mode before the facet.

<figure id="fig-16-1">
  <img src="{{ '/assets/figs/ch16_butt.svg' | relative_url }}" style="width:600px" alt="Left: to-scale facet view of the 500 by 220 nanometre silicon strip and its 0.4 micrometre mode inside the circles of a 2.5 micrometre lensed-fibre spot, a 4 micrometre UHNA mode, the 8.2 micrometre SMF-28 core and its 10.4 micrometre mode. Right: butt-coupling efficiency in dB against the chip's mode-field diameter for the three fibres, Gaussian-formula curves peaking at each fibre's own mode size, with femwell results for silicon tips as circles">
  <figcaption><span class="capnum">Figure 16.1.</span> <strong>The size mismatch.</strong> (a) Mode sizes at a facet, to scale: the 500 × 220 nm strip and its femwell mode, about 0.4 µm across, inside the 1/e² circles of a lensed fibre (2.5 µm), a UHNA fibre (4 µm) and SMF-28 (10.4 µm, core 8.2 µm {% include cite.html keys="itug652" %}). (b) Butt coupling against the chip's mode-field diameter: lines from the Gaussian formula above, circles the femwell overlaps of the silicon tips of Table 16.1, placed at the geometric mean of their two diameters. The strip couples about 1 % to SMF-28 and 12 % to a lensed fibre. Near the match the real tip modes reach 92 % where the Gaussian formula gives 98 %, because their exponential tails are not Gaussian. Drawn by <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">16.2</span>Inverse tapers

The obvious converter widens the waveguide, but a wide silicon waveguide confines light more tightly and becomes multimode. The trick, which seems backwards at first, is to **narrow** it {% include cite.html keys="almeida2003" %}. As a silicon strip is tapered towards a tip of a hundred or two nanometres, it becomes too small to hold the mode. The effective index falls towards the cladding's (1.444), the evanescent decay constant $$\gamma = k_0\sqrt{n_\mathrm{eff}^2 - n_\mathrm{ox}^2}$$ shrinks, and the mode spreads out into the oxide cladding, which acts as a larger, weakly guiding waveguide. If the taper is long enough to be **adiabatic** ([Chapter 8]({% link chapters/08_bends.md %})), the light follows the fundamental mode from 0.4 µm to several micrometres with little loss ([Figure 16.2](#fig-16-2)).

<figure id="fig-16-2">
  <img src="{{ '/assets/figs/ch16_taper.svg' | relative_url }}" style="width:600px" alt="Top and side views along a 200 micrometre linear inverse taper from 500 to 160 nanometres, with the local mode size shaded: it stays below 1 micrometre for most of the length and grows to about 4.8 micrometres in the last few tens of micrometres, matching a 4 micrometre UHNA fibre beyond the facet; in the side view the mode reaches the silicon substrate below the 2 micrometre BOX at the tip">
  <figcaption><span class="capnum">Figure 16.2.</span> <strong>An inverse taper from above and from the side.</strong> A linear taper from 500 to 160 nm over 200 µm (illustrative length), shaded with the 1/e² size of the local mode from the femwell sweep of Table 16.1, assuming the taper is slow enough to be adiabatic. The mode stays below 1 µm until the tip is about 250 nm wide, 150 µm along, then grows to 4.8 × 4.8 µm at the facet, matched to a UHNA fibre. In the side view it reaches the substrate below the 2 µm BOX, which would hold 4.2 % of its power (red). Transverse axes stretched × 6. Drawn by <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

[Table 16.1](#tab-16-1) and [Figure 16.3](#fig-16-3) show how fast the mode grows, from full-vectorial femwell solutions of 220 nm silicon tips in oxide.

**Table 16.1. Mode of a 220 nm silicon tip in oxide at 1550 nm (femwell), and its coupling to three fibres.** MFD: 1/e² intensity diameter from the second moments, horizontal × vertical. Overlaps use the full mode field; "below 2 µm" is the fraction of the mode's power more than 2 µm below the core, where a standard BOX ends. Computed by <code>figsrc/ch16_taper.py</code>.
{: .tabcaption #tab-16-1 }

| Tip | Pol. | n<sub>eff</sub> | MFD (µm) | Lensed 2.5 µm | UHNA 4 µm | SMF-28 10.4 µm | Below 2 µm |
|---|---|---|---|---|---|---|---|
| 130 nm | TE | 1.4445 | 11.8 × 14.3 ≈ | 33 % | 52 % | 90 % | 21.0 % |
| 140 nm | TE | 1.4452 | 9.1 × 9.9 | 49 % | 70 % | 89 % | 13.8 % |
| 150 nm | TE | 1.4466 | 6.6 × 6.7 | 66 % | 84 % | 77 % | 8.0 % |
| 160 nm | TE | 1.4490 | 4.8 × 4.8 | 80 % | 91 % | 60 % | 4.2 % |
| 170 nm | TE | 1.4528 | 3.7 × 3.6 | 89 % | 89 % | 44 % | 2.0 % |
| 180 nm | TE | 1.4586 | 2.9 × 2.8 | 92 % | 82 % | 32 % | 0.8 % |
| 200 nm | TE | 1.4785 | 1.9 × 1.9 | 86 % | 62 % | 17 % | 0.1 % |
| 250 nm | TE | 1.6018 | 1.0 × 0.9 | 48 % | 25 % | 4 % | 0.0 % |
| 500 nm | TE | 2.4459 | 0.4 × 0.4 | 12 % | 5 % | 1 % | 0.0 % |
| 90 nm | TM | 1.4457 | 8.3 × 7.9 | 57 % | 77 % | 84 % | 10.8 % |
| 100 nm | TM | 1.4470 | 6.2 × 6.1 | 70 % | 87 % | 73 % | 6.9 % |
| 120 nm | TM | 1.4514 | 3.9 × 4.0 | 87 % | 90 % | 48 % | 2.5 % |
| 140 nm | TM | 1.4585 | 2.8 × 2.9 | 92 % | 82 % | 32 % | 0.8 % |
| 160 nm | TM | 1.4685 | 2.2 × 2.2 | 90 % | 71 % | 22 % | 0.3 % |
| 200 nm | TM | 1.4962 | 1.5 × 1.6 | 78 % | 51 % | 12 % | 0.0 % |
| 500 nm | TM | 1.7706 | 0.8 × 0.7 | 34 % | 16 % | 3 % | 0.0 % |

<figure id="fig-16-3">
  <img src="{{ '/assets/figs/ch16_modes.svg' | relative_url }}" style="width:600px" alt="Six femwell intensity maps on the same 18 by 16 micrometre window, on a decibel colour scale: TE modes of 500, 200, 180, 160 and 140 nanometre silicon tips, growing from a 0.4 micrometre spot to about 10 micrometres, and the TM mode of a 140 nanometre tip, about 2.8 micrometres; a dashed line marks where a 2 micrometre BOX ends and dashed circles show the best-matched fibre mode with its overlap">
  <figcaption><span class="capnum">Figure 16.3.</span> <strong>The tip mode, to scale (femwell).</strong> Intensity of the fundamental mode of 220 nm silicon tips in oxide at 1550 nm, on a decibel scale and the same 18 × 16 µm window: TE at 500, 200, 180, 160 and 140 nm, and TM at 140 nm. Dashed line: where a 2 µm BOX would end (the substrate is left out of the calculation); dashed circles: the 1/e² mode of the best-matched fibre, with the overlap of Table 16.1. The TE mode grows from 0.4 µm to about 10 µm as the tip narrows from 500 to 140 nm, and 14 % of it then lies below the BOX; at 140 nm the TM mode is still only 2.8 µm across. Computed by <code>figsrc/ch16_fields.py</code>, drawn by <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 16.1 · Choosing the tip width</div>

**A 3 µm spot.** [Table 16.1](#tab-16-1) points to a TE tip of about 180 nm. The mode is 2.9 × 2.8 µm and couples 92 % (−0.36 dB) to a 2.5 µm lensed fibre, with less than 1 % of it more than 2 µm below the core. A UHNA fibre (4 µm) is best matched near 160 nm: 91 % (−0.42 dB), but 4 % of the mode already reaches beyond 2 µm.

**A 10 µm spot.** SMF-28 needs a TE tip of about 140 nm. femwell gives a 9.1 × 9.9 µm mode and 89 % overlap, but 14 % of the power lies more than 2 µm below the core. On a 2 µm BOX that light leaks into the substrate, so a single silicon taper cannot serve SMF-28 directly.

TM reaches the same spots at narrower tips: 2.8 µm at 140 nm, 4 µm at 120 nm. Even the best overlaps are about 92 %, not 100 %, because the taper's mode is not Gaussian: its exponential tails cannot match a Gaussian fibre mode exactly.

</div>

Three things limit how far a single silicon taper can go:

- **Substrate leakage.** A large mode in a 2 µm BOX reaches the silicon substrate, whose index (3.48) is above the mode's, and leaks into it ([Chapter 7]({% link chapters/07_loss.md %})). Couplers for large spots use a thicker BOX, remove the substrate under the taper, or hand the light to a second, larger waveguide (Section 16.3).
- **Polarisation.** Below about 220 nm the tip is narrower than it is tall, so TE light (field across the narrow width) escapes sooner than TM. The same tip gives two very different spots, and a polarisation-independent coupler needs a square tip or a second stage.
- **Fabrication.** Near the best tip width the spot changes by about 0.1 µm per nanometre of width, and tips of 100–200 nm are near the smallest features a foundry prints reliably. The tip width varies across a wafer, and so does the coupling.

**Try it.** Narrow the tip and watch the mode grow in the to-scale facet view; choose a fibre, and move it sideways to see the tolerance.

{% include demos/taper.html %}

## <span class="secnum">16.3</span>Multi-stage couplers and overlays

To reach a 10 µm spot without leaking, the silicon taper hands the light to a second, lower-index waveguide that is large enough to guide the expanded mode on its own ([Figure 16.4](#fig-16-4)):

- **Polymer or oxide overlays.** A waveguide of polymer or silicon oxynitride, a few micrometres across, is built over the silicon taper. The light moves into it as the silicon narrows, and the overlay carries it to the facet with a mode matched to a fibre. This was one of the first low-loss converters for silicon wires, at 0.8 dB per conversion {% include cite.html keys="shoji2002" %}.
- **Silicon nitride stages.** Most foundry platforms put a SiN layer above the silicon. A silicon taper couples into a SiN waveguide, and a SiN taper, with its lower index contrast and therefore larger modes from wider, easier tips, expands the light further; multi-tip "trident" designs shape the spot in both directions.
- **SWG metamaterial couplers.** Segmenting the taper into a subwavelength grating lowers its effective index gradually ([Chapter 13]({% link chapters/13_bragg.md %})), so the mode expands with features that are easier to print. Such couplers have reached high efficiency for both polarisations over more than 100 nm {% include cite.html keys="cheben2015" %}.
- **Suspended couplers.** Etching away the substrate under the taper, leaving a cantilever of oxide, removes the leakage path and lets the mode grow large in a symmetric cladding.

These designs and their trade-offs are reviewed by Marchetti et al. {% include cite.html keys="marchetti2019" %}.

<figure id="fig-16-4">
  <img src="{{ '/assets/figs/ch16_multistage.svg' | relative_url }}" style="width:600px" alt="Four schematic strips. a: side view of a silicon inverse taper inside a polymer overlay waveguide, the mode moving up into the overlay and carried to the facet. b: a silicon taper handing the light up to a silicon nitride waveguide, which then tapers and expands the mode at the facet. c: a suspended coupler whose substrate is etched away under the taper so the mode grows in a symmetric oxide cladding. d: top view of a segmented subwavelength-grating taper with the mode widening towards the facet">
  <figcaption><span class="capnum">Figure 16.4.</span> <strong>Beyond a single silicon taper (schematic side views; d from above).</strong> (a) The silicon tip hands the light to a polymer or oxynitride waveguide a few micrometres across, which carries it to the facet. (b) Two stages: silicon to silicon nitride, then a SiN inverse taper whose wider tip makes a larger spot. (c) A suspended coupler: with the substrate under the taper etched away, the growing mode has no high-index substrate to leak into. (d) A subwavelength-grating taper: segments shorter than the wavelength lower the effective index gradually, with features that are easier to print. Shaded: the extent of the mode. Not to scale. Drawn by <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">16.4</span>Facets

The facet must be optically flat at the coupler, and there are three ways to make it ([Figure 16.5](#fig-16-5)):

- **Dicing and polishing.** The wafer is diced, and the edge is polished in a few steps down to a fine grit. It gives excellent facets, but one chip at a time.
- **Deep etching.** A deep trench etched through the BOX and into the substrate defines the facet lithographically, at wafer scale and at any position. The chip is then diced in the trench, and the couplers can be tested on the wafer by lowering a fibre into the trench.
- **Cleaving** along a crystal plane, common for III-V lasers, which are on their own substrates.

<figure id="fig-16-5">
  <img src="{{ '/assets/figs/ch16_facets.svg' | relative_url }}" style="width:600px" alt="Two schematic side views. a: a diced and polished chip edge with a 125 micrometre fibre butted against it through index-matching gel. b: a trench etched through the oxide layers into the substrate, its wall forming the facet; a lensed fibre is lowered into the trench, whose floor lies more than 62.5 micrometres below the waveguide, and a dashed line marks where the chip will be diced later">
  <figcaption><span class="capnum">Figure 16.5.</span> <strong>Making the facet (schematic side views).</strong> (a) The chip is diced and its edge polished; a fibre butts against the facet through index-matching gel. (b) A trench etched through the oxide and the BOX into the substrate defines the facet by lithography. Its floor must lie more than a fibre radius (62.5 µm) below the waveguide, so that a fibre can be lowered in to test the couplers on the wafer; the chip is diced inside the trench afterwards. Fibres to scale; layer thicknesses × 4. Drawn by <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

At the facet, part of the light reflects. With the mode in the oxide, an oxide–air facet reflects $$R = ((1.444 - 1)/(1.444 + 1))^2 = 3.3\ \%$$ (−14.8 dB); a bare silicon strip would reflect 31 %. Reflections cause fringes in measurements and feedback into lasers ([Chapter 15]({% link chapters/15_gc.md %})), and are reduced three ways: **index-matching** gel or epoxy between facet and fibre, an **anti-reflection coating**, or an **angled waveguide** that meets the facet at a few degrees, so that the reflected beam misses the waveguide's mode ([Figure 16.6](#fig-16-6)).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 16.2 · An angled facet</div>

Tilt the waveguide by 8° at the facet. The reflected beam comes back at 16° to the waveguide axis, and couples back into a mode of radius $$w$$ with efficiency $$\exp[-(\pi n w\,\alpha/\lambda)^2]$$ for a tilt $$\alpha$$ inside the oxide ([Chapter 15]({% link chapters/15_gc.md %})). For a 3 µm spot ($$w = 1.5$$ µm), $$\pi \times 1.444 \times 1.5 \times 0.279/1.55 = 1.23$$, so the reflected light is suppressed by a further $$e^{-1.50}$$, or 6.5 dB: −21.3 dB in all. The beam leaves the chip at $$\sin^{-1}(1.444\sin 8°) = 11.6°$$ in air, so the fibre must be tilted to match. The larger the spot, the more an angle helps.

</div>

<figure id="fig-16-6">
  <img src="{{ '/assets/figs/ch16_angled.svg' | relative_url }}" style="width:600px" alt="Left: top view of a waveguide beam meeting an oxide-air facet at 8 degrees, the reflected beam returning at 16 degrees to the waveguide axis and the transmitted beam leaving at 11.6 degrees in air. Right: reflection coupled back into the mode against waveguide tilt from 0 to 12 degrees for 2, 3 and 5 micrometre spots, starting at minus 14.8 dB and falling faster for larger spots, with minus 21.3 dB marked at 8 degrees for a 3 micrometre spot">
  <figcaption><span class="capnum">Figure 16.6.</span> <strong>An angled facet (Worked Example 16.2).</strong> (a) A waveguide with a 3 µm spot meets the oxide–air facet at 8°. The 3.3 % reflected returns at 16° to the waveguide axis and misses its mode; the transmitted beam leaves at 11.6° in air, where the fibre must be. Angles to scale. (b) The reflection coupled back into the mode against the tilt, for three spot sizes: the flat facet's −14.8 dB (taken at normal incidence) times the tilt factor \(\exp[-(\pi n w\cdot 2\theta/\lambda)^2]\). At 8° a 3 µm spot is at −21.3 dB; larger spots gain more from the angle. Drawn by <code>figsrc/ch16_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">16.5</span>Fibres at the edge

The fibre is chosen to match the spot the chip can make:

- **Lensed fibres** focus SMF-28's light to a 2–3 µm waist some micrometres in front of the lens. They match a single silicon taper well but tolerate only about ±0.6 µm of offset ([Chapter 17]({% link chapters/17_fiberarrays.md %})), so they suit the lab more than a package.
- **High-NA fibres** (UHNA) have a small core and a 3–4 µm mode; a short piece, spliced to SMF-28 with a heat-diffused core, makes an adiabatic fibre-side converter.
- **Cleaved SMF-28** needs a 10 µm spot on the chip, which only multi-stage or suspended couplers provide, but it then tolerates a few micrometres of offset.
- **Fibre arrays** at 127 µm pitch serve many edge couplers at once, and V-grooves etched into the chip itself can hold fibres passively aligned to the couplers.

## <span class="secnum">16.6</span>Edge against grating couplers

**Table 16.2. Edge and grating couplers compared.** Typical values; see Chapters 15–17 {% include cite.html keys="marchetti2019" %}.
{: .tabcaption #tab-16-2 }

| | Grating coupler | Edge coupler |
|---|---|---|
| Loss per coupler | 2–5 dB; below 1 dB with bottom reflectors | 0.5–2 dB |
| 1 dB bandwidth | 30–40 nm | more than 100 nm |
| Polarisation | one (two with a 2D grating) | both possible |
| 1 dB lateral tolerance | about ±2.4 µm | ±0.6 µm (lensed fibre) to ±2 µm (large spot) |
| Wafer-scale testing | yes, anywhere on the wafer | only with etched facets and trenches |
| Position on the chip | anywhere | at a prepared edge only |
| Fabrication | shallow etch or SWG; one coupler at a time to optimise | narrow tips, often a second layer, facet preparation |
| Packaging | an angled fibre array above the chip | in-plane fibres or lasers; compact, but a facet to prepare |

Grating couplers win for testing and prototyping; edge couplers win for low loss and wide bandwidth, which is why products, and anything with a laser attached, often use them. Many chips carry both: gratings for wafer-scale test, edges for the package.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Edge couplers for the transceiver of the reference link: a two-stage Si-to-SiN converter matched to a UHNA fibre array, with angled waveguides at the facet, so that the four channels and both directions see low, flat loss. Grating couplers stay on the chip for wafer-scale test.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: edge-coupler taper](https://s3.amazonaws.com/fip-7/Taper/index.html) and [inverse taper](https://s3.amazonaws.com/fip-7/Inverse-Taper/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="marchetti2019,almeida2003,shoji2002,cheben2015,chrostowski2015" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Butt-coupling a 500 × 220 nm strip to SMF-28 loses about 20 dB: the mode must be expanded first.
- An inverse taper pushes the mode into the cladding. For TE, a 180 nm tip gives a 2.9 µm spot (92 % to a lensed fibre), 160 nm a 4.8 µm spot (UHNA fibre), and 140 nm about 10 µm.
- Large spots leak through a 2 µm BOX; SMF-sized spots need SiN or polymer stages, SWG or suspended couplers.
- TE and TM expand at different tip widths, and the tip width is a critical, fabrication-sensitive dimension.
- Facet reflections (3.3 % oxide–air) are cut by index matching, coatings and angled waveguides.
- Edge couplers offer low loss, more than 100 nm of bandwidth and both polarisations; grating couplers offer wafer-scale testing and relaxed alignment.

</div>
