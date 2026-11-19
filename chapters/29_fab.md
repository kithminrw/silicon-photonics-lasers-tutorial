---
title: "29. Fabrication"
parent: "Part VII · Fabrication, Testing and Data Analysis"
nav_order: 29
permalink: /part-7/ch29/
chapter: 29
---

# <span class="chapnum">Chapter 29</span>Fabrication

A photonic chip is made with the same tools as a microprocessor, but its devices care about nanometres in different ways.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe SOI wafer manufacture and the main process steps: lithography, etch, cladding, doping, metals and germanium;
- compare DUV lithography with electron-beam lithography;
- describe SiN deposition, TFLN etching and III–V bonding;
- turn width and thickness variations into wavelength shifts across a wafer;
- apply design-for-manufacturing practices and choose a multi-project-wafer route.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do nanometre variations turn into nanometre wavelength shifts?

</div>

## <span class="secnum">29.1</span>SOI wafers

Silicon photonics starts from **silicon-on-insulator** wafers: a thin crystalline silicon film (220 nm for most photonics) on a buried oxide (2 µm or more) on a thick silicon handle. They are made by the **Smart Cut** process ([Figure 29.1](#fig-29-1)). A silicon wafer is oxidised and implanted with hydrogen to a depth just beyond the desired film thickness; it is bonded face down to a handle wafer; a heat treatment splits it along the implanted layer, leaving the thin film on the oxide; polishing and annealing finish the surface, and the rest of the donor wafer is reused. The film thickness is uniform to a few nanometres across a 200 or 300 mm wafer, and, as Section 29.6 shows, those few nanometres matter.

<figure id="fig-29-1">
  <img src="{{ '/assets/figs/ch29_soi.svg' | relative_url }}" style="width:600px" alt="Left: an SOI wafer to scale, a thin 220 nm silicon film on a 2 micrometre buried oxide on a silicon handle that is shortened with a break. Right: six small sketches of the Smart Cut process: oxidise the donor wafer, implant hydrogen ions to form a dashed implanted layer, flip and bond face down onto the handle wafer, anneal so the donor splits along the implanted layer, polish and anneal the smooth film, and reuse the thinner donor.">
  <figcaption><span class="capnum">Figure 29.1.</span> <strong>An SOI wafer and how it is made.</strong> (a) The wafer to scale: a 220 nm silicon film on a 2 µm buried oxide on a silicon handle about 0.7 mm thick (shown shortened); the film is about 1/3300 of the wafer's thickness. (b) Smart Cut: the donor wafer is oxidised and implanted with hydrogen just below the future film, bonded face down to the handle, split along the implanted layer by annealing, then polished and annealed; the rest of the donor is reused. Panel b is not to scale. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.2</span>Lithography

Lithography transfers the layout to the wafer ([Figure 29.2](#fig-29-2)):

- **Deep-ultraviolet (DUV) projection lithography** images a mask onto photoresist with a 248 nm or 193 nm laser, the latter also in **immersion** (with water between lens and wafer) for the smallest features. Foundry photonics uses it for its throughput and repeatability: a whole wafer in minutes, every die identical. Features down to about 100–150 nm print with 248 and 193 nm dry tools, smaller with immersion. Below about the wavelength the image is blurred: corners round, small gaps narrow, and dense and isolated features print differently. Models of this (**optical proximity correction**) adjust the mask to compensate ([Figure 29.3](#fig-29-3)).
- **Electron-beam lithography (EBL)** writes the pattern directly with a focused electron beam. It needs no mask and resolves features of 10–20 nm, but it writes one shape at a time, so it is slow and suited to prototypes and small runs. Electrons scattered in the resist and substrate expose areas near each shape (the **proximity effect**), corrected by adjusting the dose. The SiEPIC openEBL runs use electron-beam lithography {% include cite.html keys="openebl" %}.

<figure id="fig-29-2">
  <img src="{{ '/assets/figs/ch29_litho.svg' | relative_url }}" style="width:600px" alt="Six cross-sections in two rows: photoresist spun on the silicon film over buried oxide; the resist exposed through a mask with a dark chrome line over the future waveguide; after development resist remains only over the waveguide; ions etch away the unprotected silicon; the resist stripped leaves a silicon strip; oxide cladding deposited over the strip.">
  <figcaption><span class="capnum">Figure 29.2.</span> <strong>Patterning a strip waveguide.</strong> (1) Photoresist is spun onto the SOI wafer; (2) it is exposed through a mask (or written by an electron beam); (3) with a positive resist the exposed areas dissolve in the developer, leaving resist over the waveguide; (4) a plasma etch removes the unprotected silicon; (5) the resist is stripped; (6) oxide cladding is deposited and planarised. Not to scale. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

<figure id="fig-29-3">
  <img src="{{ '/assets/figs/ch29_opc.svg' | relative_url }}" style="width:600px" alt="Two top views of a 1 by 2 MMI with a 500 nm input, a wide body, and two 500 nm outputs 150 nm apart, the lower one tapering to a 150 nm tip. Dashed outlines show the mask, blue fill the printed shape. (a) Mask equal to the layout: the printed corners are rounded, the gap between the outputs narrows from 150 to 120 nm and closes near the body, and the tip ends 45 nm short. (b) Corrected mask with square serifs on the body's outer corners, red notches at its inner corners, slightly biased gap edges and a hammerhead on the tip: the printed shape follows the layout closely; scale bar 500 nm.">
  <figcaption><span class="capnum">Figure 29.3.</span> <strong>Proximity effects and their correction</strong>, in a simple model of projection lithography: the mask is blurred by a Gaussian and the resist prints where the image exceeds half its full value. The blur (σ = 89 nm) is chosen so that the narrowest isolated line that still prints is 120 nm, within the 100–150 nm of dry DUV tools. (a) Printing the layout as drawn rounds the corners, narrows the 150 nm gap to 120 nm and pulls the 150 nm tip back by 45 nm. (b) Serifs, notches, a 12 nm wider gap on the mask and a hammerhead restore the gap (145 nm) and the tip (within 10 nm). Real proximity correction uses calibrated models of the optics and the resist. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.3</span>Etching and cladding

Plasma etching transfers the resist pattern into the silicon. A **full etch** down to the buried oxide makes strip waveguides; a **partial etch** (often 70 nm for grating couplers and 130 nm or so for rib waveguides) makes the shallow features ([Figure 29.4](#fig-29-4)). The etch leaves sidewalls a few degrees off vertical and slightly rough. The roughness scatters light and sets most of the propagation loss of strips ([Chapter 7]({% link chapters/07_loss.md %})). Oxide cladding is then deposited and planarised. Some processes leave the waveguides air-clad, for sensing ([Chapter 34]({% link chapters/34_apps.md %})) or for tighter confinement.

<figure id="fig-29-4">
  <img src="{{ '/assets/figs/ch29_etch.svg' | relative_url }}" style="width:600px" alt="Three cross-sections to scale in oxide: a 500 by 220 nm silicon strip etched down to the buried oxide; a 500 nm rib 220 nm tall standing on a 90 nm slab after a 130 nm etch; and grating-coupler teeth 70 nm deep on a 150 nm slab with a period of about 0.61 µm.">
  <figcaption><span class="capnum">Figure 29.4.</span> <strong>Three etch depths in 220 nm SOI, to scale.</strong> (a) A full etch to the buried oxide makes 500 × 220 nm strips. (b) A 130 nm etch leaves a 90 nm slab: the rib waveguides of modulators. (c) A 70 nm etch makes the teeth of a grating coupler, here cut along the grating, with the 607 nm period of Chapter 15. Sidewalls are drawn a few degrees off vertical. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.4</span>Doping, metals and germanium

Active silicon photonics adds the CMOS front-end and back-end steps ([Figure 29.5](#fig-29-5)):

- **Implants** of boron and phosphorus at several doses make the PN junctions of modulators, with heavier doping near the contacts ([Chapter 19]({% link chapters/19_eo.md %})), followed by an activation anneal.
- **Germanium** is grown selectively by epitaxy in windows opened down to the silicon, then annealed to reduce its dislocation density ([Chapter 21]({% link chapters/21_pd.md %})); it must be grown after the high-temperature implant anneals.
- **Contacts and metals**: silicide contacts to the doped silicon and germanium, resistive metal (TiN, W) for heaters ([Chapter 18]({% link chapters/18_thermal.md %})), and one to several layers of aluminium or copper interconnect, with openings for pads and for the grating couplers.

<figure id="fig-29-5">
  <img src="{{ '/assets/figs/ch29_stack.svg' | relative_url }}" style="width:600px" alt="Cross-section at true scale of an active silicon photonics chip over a 2 micrometre buried oxide: a rib phase shifter with p++, p, n and n++ regions in its slab; a germanium photodiode 4 micrometres wide and 0.5 micrometres thick on a p-doped silicon pad; a strip waveguide with a TiN heater 1.9 micrometres above it; a shallow-etched grating coupler under an oxide window. Tungsten contacts rise to metal 1, vias join metal 2, and a pad opening exposes metal 2 above the phase shifter. Brackets mark the front end and the back end.">
  <figcaption><span class="capnum">Figure 29.5.</span> <strong>An active SOI process in cross-section, at true scale.</strong> Front end, in the 220 nm film: a rib phase shifter with p, n and heavily doped contact regions in its 90 nm slab, a vertical germanium photodiode (4 µm wide, 0.5 µm thick) on a p-doped silicon pad, a strip waveguide and a shallow-etched grating coupler. Back end: tungsten contacts, a TiN heater 1.9 µm above the waveguide (contacted at its ends, outside this plane), two metal levels joined by vias, a pad opening, and an oxide window over the grating coupler. Device dimensions follow Chapters 18, 19 and 21; the metal thicknesses are illustrative. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.5</span>Other platforms

- **Silicon nitride** is deposited, either by low-pressure CVD at high temperature (low loss, but high stress that limits film thickness unless managed) or by plasma-enhanced CVD at low temperature (compatible with finished electronics, but with more hydrogen-related absorption near 1520 nm), then annealed and etched ([Chapter 4]({% link chapters/04_platforms.md %})).
- **Thin-film lithium niobate** is bonded onto oxide by an ion-slicing process like Smart Cut, and etched by argon-ion milling, which leaves sloped sidewalls ([Chapter 4]({% link chapters/04_platforms.md %})).
- **III–V materials** are bonded onto processed silicon wafers and patterned afterwards ([Chapter 27]({% link chapters/27_lasersonsi.md %})).

## <span class="secnum">29.6</span>Process variation

No two dies come out identical. Across a wafer, the SOI thickness varies smoothly, often as a bowl or a tilt; the lithography dose and focus vary from field to field; and etch rates vary with pattern density. Within a die, neighbouring structures differ by smaller, random amounts. [Chapter 6]({% link chapters/06_soi.md %}) computed the sensitivities with femwell for a 500 × 220 nm strip: $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}W = 1.6\times10^{-3}$$ per nm and $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}t = 3.7\times10^{-3}$$ per nm ([Figure 29.6](#fig-29-6)).

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Resonance shift from fabrication errors</div>

$$\Delta\lambda = \frac{\lambda}{n_g}\left(\frac{\partial n_\mathrm{eff}}{\partial W}\,\Delta W + \frac{\partial n_\mathrm{eff}}{\partial t}\,\Delta t\right) \approx 0.6\ \frac{\mathrm{nm}}{\mathrm{nm}}\,\Delta W + 1.4\ \frac{\mathrm{nm}}{\mathrm{nm}}\,\Delta t$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 29.1 · Ring resonances across a wafer</div>

If the silicon thickness varies by 6 nm from the centre of a wafer to its edge, and the width by another 6 nm through the lithography dose, the ring resonances spread by up to $$1.4 \times 6 + 0.6 \times 6 \approx 12$$ nm where the two add, more than three channel spacings of the reference link. Random die-to-die width variation of 1.5 nm adds ±0.9 nm. Every ring must be tuned, and since heaters only red-shift ([Chapter 18]({% link chapters/18_thermal.md %})), the reddest die sets the design offset (it needs no heating) and the bluest die, a full spread away, sets the heater budget. The demo turns such maps into numbers.

</div>

<figure id="fig-29-6">
  <img src="{{ '/assets/figs/ch29_sens.svg' | relative_url }}" style="width:600px" alt="(a) Colour map of the ring-resonance shift over width error and thickness error, each from minus 8 to plus 8 nm: red for red shifts, blue for blue shifts, with straight contour lines every 3.2 nm (one channel spacing) sloping down to the right, steeper in thickness than in width. A dot at plus 6 nm in both marks plus 12 nm; a small dashed ellipse at the origin marks a random width spread of sigma 1.5 nm. (b) Resonance shift per nm of width against waveguide width, falling from 1.06 at 400 nm to 0.60 at 500 nm and 0.09 at 1000 nm; a dot marks 1.37 nm per nm of thickness at 500 nm, and a dashed line the slab limit of 1.39 nm per nm of thickness.">
  <figcaption><span class="capnum">Figure 29.6.</span> <strong>How width and thickness errors move a ring's resonance.</strong> (a) The shift \(0.6\,\Delta W + 1.4\,\Delta t\) of the key equation; contours every 3.2 nm, the reference link's channel spacing. The corner of Worked Example 29.1 (+6 nm in both) is 12 nm away, while the random width scatter (σ = 1.5 nm) alone stays within one channel. (b) The sensitivities against waveguide width, from the femwell width sweep of Chapter 6: widening the strip from 500 nm to 1 µm cuts the width sensitivity from 0.60 to 0.09 nm per nm, but the thickness sensitivity stays near 1.4 nm per nm (1.37 at 500 nm; 1.39 for a 220 nm slab, the limit of a very wide guide, from a slab mode solver). Wide waveguides tame width errors, never thickness errors. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

**Try it.** Change the wafer-scale thickness and width variations and the random component, and generate new wafers; the map, the distribution and the bluest die's cross-section update.

{% include demos/wafermc.html %}

Interferometers suffer less: a balanced MZI sees the same error in both arms, so only the *difference* between the arms matters, a few tens of micrometres apart. Within-die variation is therefore what limits MZI lattices and the ring-to-ring matching of WDM filters, while wafer-scale variation is what tuning must absorb.

## <span class="secnum">29.7</span>Design for manufacturing

Designers reduce the impact of variation in several ways:

- **Choose tolerant geometries.** Wider waveguides are less sensitive to width ([Figure 29.6](#fig-29-6)b); in the delay arms of an interferometer, wide multimode sections with narrow tapers at the bends cut width sensitivity several-fold. Rib waveguides are less sensitive than strips to sidewall roughness.
- **Match what must match.** Place devices that must agree, such as the two arms of an MZI, close together and in the same orientation, with the same surroundings.
- **Design for tuning.** Assume every resonant device will be tuned, and budget the heater power for the measured spread.
- **Respect the density rules.** Foundries require minimum and maximum pattern densities (**fill**) for even etching and polishing; automatic fill must keep away from waveguides.
- **Simulate corners.** Run the circuit simulation at the process corners (thick/wide, thin/narrow) and with Monte Carlo variation using the foundry's statistics.

## <span class="secnum">29.8</span>Access

Few designers own a fab. Instead, **multi-project wafer** (MPW) runs share the cost of a wafer among many designs. Foundries and research institutes offer runs several times a year with a PDK ([Chapter 30]({% link chapters/30_flow.md %})), and turnarounds from a few weeks for electron-beam prototyping to several months for full active processes. The openEBL runs, built on open-source PDKs and tools, let students and researchers submit passive designs through GitHub and get back measurement data {% include cite.html keys="openebl" %}: the route of "your first chip".

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Submit to an openEBL run (electron-beam lithography, 220 nm SOI, full etch). Expect a few nanometres of width bias between design and fabrication, and plan for it: include rings with several gaps and widths, and duplicate key structures in different parts of the chip to see the within-die variation.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [AIM Photonics / MIT VM-Lab simulation library](https://www.aimphotonics.com/simulation-library) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="chrostowski2015,siew2021,openebl" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- SOI wafers come from Smart Cut; the film thickness varies by a few nanometres across a wafer.
- DUV lithography gives throughput and repeatability; electron-beam lithography gives resolution and flexibility for prototypes.
- Process steps: lithography, full and partial etch, cladding, implants, germanium epitaxy, contacts, heaters and metal.
- A ring moves by about 0.6 nm per nm of width and 1.4 nm per nm of thickness: wafer-scale variation spreads resonances by several nanometres, so tuning is mandatory.
- Design for manufacturing: tolerant geometries, matched layouts, tuning budgets, fill rules, corners; MPW runs and openEBL give access.

</div>
