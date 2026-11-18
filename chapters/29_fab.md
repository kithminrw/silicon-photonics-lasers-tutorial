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

Silicon photonics starts from **silicon-on-insulator** wafers: a thin crystalline silicon film (220 nm for most photonics) on a buried oxide (2 µm or more) on a thick silicon handle. They are made by the **Smart Cut** process. A silicon wafer is oxidised and implanted with hydrogen to a depth just beyond the desired film thickness; it is bonded face down to a handle wafer; a heat treatment splits it along the implanted layer, leaving the thin film on the oxide; polishing and annealing finish the surface, and the rest of the donor wafer is reused. The film thickness is uniform to a few nanometres across a 200 or 300 mm wafer, and, as Section 29.6 shows, those few nanometres matter.

## <span class="secnum">29.2</span>Lithography

Lithography transfers the layout to the wafer:

- **Deep-ultraviolet (DUV) projection lithography** images a mask onto photoresist with a 248 nm or 193 nm laser, the latter also in **immersion** (with water between lens and wafer) for the smallest features. Foundry photonics uses it for its throughput and repeatability: a whole wafer in minutes, every die identical. Features down to about 100–150 nm print with 248 and 193 nm dry tools, smaller with immersion. Below about the wavelength the image is blurred: corners round, small gaps narrow, and dense and isolated features print differently. Models of this (**optical proximity correction**) adjust the mask to compensate.
- **Electron-beam lithography (EBL)** writes the pattern directly with a focused electron beam. It needs no mask and resolves features of 10–20 nm, but it writes one shape at a time, so it is slow and suited to prototypes and small runs. Electrons scattered in the resist and substrate expose areas near each shape (the **proximity effect**), corrected by adjusting the dose. The SiEPIC openEBL runs use electron-beam lithography {% include cite.html keys="openebl" %}.

## <span class="secnum">29.3</span>Etching and cladding

Plasma etching transfers the resist pattern into the silicon. A **full etch** down to the buried oxide makes strip waveguides; a **partial etch** (often 70 nm for grating couplers and 130 nm or so for rib waveguides) makes the shallow features. The etch leaves sidewalls a few degrees off vertical and slightly rough. The roughness scatters light and sets most of the propagation loss of strips ([Chapter 7]({% link chapters/07_loss.md %})). Oxide cladding is then deposited and planarised. Some processes leave the waveguides air-clad, for sensing ([Chapter 34]({% link chapters/34_apps.md %})) or for tighter confinement.

## <span class="secnum">29.4</span>Doping, metals and germanium

Active silicon photonics adds the CMOS front-end and back-end steps:

- **Implants** of boron and phosphorus at several doses make the PN junctions of modulators, with heavier doping near the contacts ([Chapter 19]({% link chapters/19_eo.md %})), followed by an activation anneal.
- **Germanium** is grown selectively by epitaxy in windows opened down to the silicon, then annealed to reduce its dislocation density ([Chapter 21]({% link chapters/21_pd.md %})); it must be grown after the high-temperature implant anneals.
- **Contacts and metals**: silicide contacts to the doped silicon and germanium, resistive metal (TiN, W) for heaters ([Chapter 18]({% link chapters/18_thermal.md %})), and one to several layers of aluminium or copper interconnect, with openings for pads and for the grating couplers.

## <span class="secnum">29.5</span>Other platforms

- **Silicon nitride** is deposited, either by low-pressure CVD at high temperature (low loss, but high stress that limits film thickness unless managed) or by plasma-enhanced CVD at low temperature (compatible with finished electronics, but with more hydrogen-related absorption near 1520 nm), then annealed and etched ([Chapter 4]({% link chapters/04_platforms.md %})).
- **Thin-film lithium niobate** is bonded onto oxide by an ion-slicing process like Smart Cut, and etched by argon-ion milling, which leaves sloped sidewalls ([Chapter 4]({% link chapters/04_platforms.md %})).
- **III–V materials** are bonded onto processed silicon wafers and patterned afterwards ([Chapter 27]({% link chapters/27_lasersonsi.md %})).

## <span class="secnum">29.6</span>Process variation

No two dies come out identical. Across a wafer, the SOI thickness varies smoothly, often as a bowl or a tilt; the lithography dose and focus vary from field to field; and etch rates vary with pattern density. Within a die, neighbouring structures differ by smaller, random amounts. [Chapter 6]({% link chapters/06_soi.md %}) computed the sensitivities with femwell for a 500 × 220 nm strip: $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}W = 1.6\times10^{-3}$$ per nm and $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}t = 3.7\times10^{-3}$$ per nm.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Resonance shift from fabrication errors</div>

$$\Delta\lambda = \frac{\lambda}{n_g}\left(\frac{\partial n_\mathrm{eff}}{\partial W}\,\Delta W + \frac{\partial n_\mathrm{eff}}{\partial t}\,\Delta t\right) \approx 0.6\ \frac{\mathrm{nm}}{\mathrm{nm}}\,\Delta W + 1.4\ \frac{\mathrm{nm}}{\mathrm{nm}}\,\Delta t$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 29.1 · Ring resonances across a wafer</div>

If the silicon thickness varies by 6 nm from the centre of a wafer to its edge, and the width by another 6 nm through the lithography dose, the ring resonances spread by up to $$1.4 \times 6 + 0.6 \times 6 \approx 12$$ nm where the two add, more than three channel spacings of the reference link. Random die-to-die width variation of 1.5 nm adds ±0.9 nm. Every ring must be tuned, and since heaters only red-shift ([Chapter 18]({% link chapters/18_thermal.md %})), the reddest die sets the design offset (it needs no heating) and the bluest die, a full spread away, sets the heater budget. The demo turns such maps into numbers.

</div>

**Try it.** Change the wafer-scale thickness and width variations and the random component, and generate new wafers; the map, the distribution and the bluest die's cross-section update.

{% include demos/wafermc.html %}

Interferometers suffer less: a balanced MZI sees the same error in both arms, so only the *difference* between the arms matters, a few tens of micrometres apart. Within-die variation is therefore what limits MZI lattices and the ring-to-ring matching of WDM filters, while wafer-scale variation is what tuning must absorb.

## <span class="secnum">29.7</span>Design for manufacturing

Designers reduce the impact of variation in several ways:

- **Choose tolerant geometries.** Wider waveguides are less sensitive to width; in the delay arms of an interferometer, wide multimode sections with narrow tapers at the bends cut width sensitivity several-fold. Rib waveguides are less sensitive than strips to sidewall roughness.
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
