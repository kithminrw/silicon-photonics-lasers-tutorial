---
title: "27. Lasers on Silicon"
parent: "Part VI · Lasers and Amplifiers"
nav_order: 27
permalink: /part-6/ch27/
chapter: 27
---

# <span class="chapnum">Chapter 27</span>Lasers on Silicon

Silicon cannot lase efficiently, so the light source is brought in: bonded, printed, flip-chipped or grown.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- compare off-chip, flip-chip, heterogeneous, micro-transfer-printed and monolithic lasers;
- explain how light moves between a III–V gain region and a silicon waveguide through supermodes and tapers;
- estimate self-heating and the thermal impedance of a laser on silicon-on-insulator;
- describe open laser-integration projects (the SiEPICfab Shuksan run, UBC ELEC 413);
- explain how directly modulated microring lasers combine source, modulator and WDM, and what limits them.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which integration approach for which volume and performance?

</div>

## <span class="secnum">27.1</span>Why the light source is the hard part

Silicon's indirect gap rules it out as a laser material ([Chapter 22]({% link chapters/22_emission.md %})), so every silicon photonic transceiver gets its light from a III–V semiconductor ([Chapter 23]({% link chapters/23_gain.md %})). The source is often the costliest and least reliable part of the link. It is temperature-sensitive ([Chapter 24]({% link chapters/24_fp.md %})), sensitive to reflections ([Chapter 25]({% link chapters/25_dynamics.md %})), and made on small, expensive InP wafers. It is also where most of the link's power goes, once its wall-plug efficiency is counted ([Chapter 38]({% link chapters/38_links.md %})). How the III–V and the silicon are joined decides the cost, the coupling loss, the thermal behaviour and how many lasers fit on a chip ([Figure 27.1](#fig-27-1)) {% include cite.html keys="liang2010,zhou2015" %}.

<figure id="fig-27-1">
  <img src="{{ '/assets/figs/ch27_options.svg' | relative_url }}" style="width:600px" alt="Six small schematic side views of a silicon-on-insulator chip with a laser joined to it in different ways: a laser module feeding a fibre over a grating coupler; a laser die flip-chipped face down on solder into a recess, butt-coupled to the silicon waveguide; a VCSEL flip-chipped above a grating coupler, emitting downwards; bonded III-V layers on the silicon waveguide with a taper moving the light down; a printed III-V coupon with broken tethers on an adhesive layer; and a quantum-dot laser grown on a buffer in a pocket, butt-coupled to the waveguide. Red arrows show the light.">
  <figcaption><span class="capnum">Figure 27.1.</span> <strong>Six ways to bring the laser to the silicon.</strong> (a) An off-chip laser module feeding a grating coupler through a fibre. (b) A laser die flip-chipped face down into a recess, its active layer level with the silicon waveguide's edge coupler. (c) A VCSEL flip-chipped over a grating coupler. (d) Heterogeneous integration: III–V layers bonded on the silicon and processed there, with a taper moving the light down (Section 27.3). (e) Micro-transfer printing: a finished coupon, its tethers broken, printed onto an adhesive layer (Section 27.4). (f) Monolithic growth: a quantum-dot laser grown on a buffer in a pocket, butt-coupled to the waveguide (Section 27.5). Red: the light. Schematic side views, not to scale. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">27.2</span>External and flip-chip lasers

- **Off-chip sources.** A packaged laser, often in its own module, feeds the silicon chip through a fibre. It is simple, replaceable and keeps the heat away from the photonic chip, and it is the choice of many co-packaged-optics designs ([Chapter 17]({% link chapters/17_fiberarrays.md %})). The cost is fibre-coupling loss at both ends and the space for the module.
- **Flip-chip and butt coupling.** A finished laser die is placed face down on the silicon chip, aligned to an edge coupler, either passively against lithographic stops or actively ([Chapter 17]({% link chapters/17_fiberarrays.md %})). Micro-optical benches with lenses and an isolator are a variant. The laser can be tested before assembly, so only good dies are used.
- **Vertical-cavity lasers.** A VCSEL ([Section 24.8]({% link chapters/24_fp.md %}#248the-vertical-cavity-surface-emitting-laser)) emits from its surface, so it can be flip-chipped face down over a grating coupler ([Chapter 15]({% link chapters/15_gc.md %})) after being tested on its own wafer. The 850 nm VCSELs of multimode links are absorbed by silicon, though, so this needs long-wavelength VCSELs, which are harder to make, or silicon-nitride waveguides, which are transparent at 850 nm.

## <span class="secnum">27.3</span>Heterogeneous integration

In **heterogeneous** integration, unpatterned III–V material, epitaxial layers on an InP wafer or die, is bonded face down onto the processed silicon wafer, its substrate is removed, and the lasers are then defined lithographically, aligned to the silicon waveguides beneath {% include cite.html keys="komljenovic2016" %}. Bonding uses a thin oxide (molecular bonding) or a polymer such as BCB. Because the lasers are made after bonding, their alignment to the silicon is lithographic, and many lasers, amplifiers, modulators and detectors can be made at once on the full silicon wafer.

The light must move between the III–V gain region above and the silicon waveguide below. The two waveguides form one coupled structure, whose **supermodes** ([Chapter 9]({% link chapters/09_couplers.md %})) share the light according to how well matched the two guides are. Under the gain section, a narrow silicon waveguide leaves the fundamental supermode in the III–V, where it gets gain. Widening the silicon along a **taper** raises its effective index past the III–V's, and the fundamental supermode moves down into the silicon, adiabatically if the taper is long enough. The III–V mesa is then tapered to a tip and ends.

[Table 27.1](#tab-27-1) shows this for a generic stack computed with femwell (<code>figsrc/ch27_hybrid.py</code>): a 500 nm silicon strip under a 3 µm wide InP mesa with a 300 nm multiple-quantum-well region, bonded through 30 nm of oxide.

**Table 27.1. Fundamental supermode of a III–V-on-silicon waveguide against the silicon width (femwell, 1550 nm, TE).** Confinement is the fraction of the mode's energy in each region.
{: .tabcaption #tab-27-1 }

| Si width | n<sub>eff</sub> | In the MQW region | In the silicon |
|---|---|---|---|
| 0.40 µm | 3.193 | 52 % | 1 % |
| 0.60 µm | 3.198 | 52 % | 4 % |
| 0.75 µm | 3.207 | 46 % | 20 % |
| 0.85 µm | 3.218 | 37 % | 38 % |
| 1.00 µm | 3.236 | 25 % | 60 % |
| 1.50 µm | 3.273 | 14 % | 78 % |

The transfer happens over a narrow range of widths, around 0.85 µm, where the light is shared equally ([Figure 27.2](#fig-27-2)). A taper that sweeps the silicon width slowly through this range, over tens to a couple of hundred micrometres, carries the light across with little loss. The designer can also choose an intermediate width under the gain section to set the modal gain, trading gain (Γ in the MQW region) against the silicon's control of the mode, for example for a laser whose feedback comes from a silicon Bragg grating or rings.

<figure id="fig-27-2">
  <img src="{{ '/assets/figs/ch27_hetero.svg' | relative_url }}" style="width:600px" alt="Top: side view along a heterogeneous laser: silicon substrate, buried oxide and a silicon waveguide with Bragg mirrors at both ends; a bonded III-V gain section in the middle. A red band showing the light runs in the silicon at both ends and rises into the MQW region under the gain section through two taper regions; the silicon is 1.5 micrometres wide at the ends and 0.4 to 0.5 micrometres under the gain. Bottom: computed intensity of the fundamental supermode against height and silicon width from 0.5 to 1.5 micrometres: at narrow widths it sits in the MQW layer, at wide widths in the silicon, crossing near 0.85 micrometres; labels give MQW 53 per cent and Si 2 per cent at 0.5, 37 and 37 per cent at the crossing, and 14 and 78 per cent at 1.5 micrometres.">
  <figcaption><span class="capnum">Figure 27.2.</span> <strong>Moving the light between the III–V and the silicon.</strong> (a) A heterogeneous laser along its length (schematic, not to scale): between silicon Bragg mirrors the light (red) travels in the silicon at both ends and in the MQW region under the gain section, and the silicon-width tapers move it up and back down. (b) The fundamental supermode of the Table 27.1 stack as the silicon widens, from the femwell maps of <code>figsrc/ch27_hybrid.py</code>: intensity integrated across the width, against height, normalised for each width and interpolated between the computed widths (triangles). Along an adiabatic taper the light follows this mode from the MQW region (53 % there and 2 % in the silicon at 0.5 µm) into the silicon (14 % and 78 % at 1.5 µm), crossing near 0.85 µm, where each holds about 37 %. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

**Try it.** Widen the silicon and watch the computed mode move from the III–V into the silicon; compare the fundamental with its partner, whose field (drawn with its sign, red positive and blue negative) changes sign between the two guides.

{% include demos/hybrid.html %}

## <span class="secnum">27.4</span>Micro-transfer printing

**Micro-transfer printing** picks up finished, tested III–V devices (lasers, amplifiers, photodiodes), each released from its source wafer by etching a sacrificial layer, with a soft elastomer stamp, and prints them onto the silicon wafer, many at a time ([Figure 27.3](#fig-27-3)). The devices are then wired up on the target wafer. It combines the known-good-die advantage of flip-chip with the density of bonding, and uses the III–V wafer efficiently. Coupling to the silicon is through evanescent tapers or butt coupling; alignment accuracy of the printing sets the tolerances.

<figure id="fig-27-3">
  <img src="{{ '/assets/figs/ch27_printing.svg' | relative_url }}" style="width:600px" alt="Four schematic steps. 1: two finished III-V devices on their source wafer, undercut by an etched sacrificial layer and held by thin tethers to anchors. 2: an elastomer stamp with posts lifts the devices off, leaving the anchors and broken tethers. 3: the stamp lowers the devices onto a silicon-on-insulator target wafer. 4: the devices sit on the target wafer on a thin adhesive layer, wired up with metal, light coupling down into the silicon.">
  <figcaption><span class="capnum">Figure 27.3.</span> <strong>Micro-transfer printing.</strong> (1) Finished, tested devices on the III–V source wafer are released by etching a sacrificial layer beneath them and held only by thin tethers. (2) An elastomer stamp with posts presses on them and lifts them off, breaking the tethers. (3) The stamp prints them, many at a time, onto the processed silicon wafer. (4) The devices are wired up, and light couples to the silicon waveguide beneath. Schematic, not to scale. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">27.5</span>Monolithic growth

The ultimate aim is to grow the laser directly on silicon. The 4–8 % lattice mismatch and thermal mismatch between III–V and silicon create dislocations that kill conventional quantum-well lasers. **Quantum-dot** active regions tolerate them far better, because carriers are captured by the dots before they can diffuse to a defect ([Chapter 23]({% link chapters/23_gain.md %})). InAs quantum-dot lasers grown on silicon now run continuously with long lifetimes. The challenge for silicon photonics is coupling: the thick buffer layers that filter dislocations lift the active region micrometres above the silicon waveguides, so growth in recessed pockets, aligned to the waveguides, is an active field ([Figure 27.4](#fig-27-4)) {% include cite.html keys="zhou2015" %}.

<figure id="fig-27-4">
  <img src="{{ '/assets/figs/ch27_monolithic.svg' | relative_url }}" style="width:600px" alt="Left: layer stack of a quantum-dot laser grown on silicon: Si substrate, GaAs buffer with wavy threading-dislocation lines starting at the silicon, two dislocation-filter layers where most lines bend sideways and stop, n-cladding, a quantum-dot active layer drawn as a row of dots, p-cladding and contact; an arrow marks several micrometres from the substrate to the dots. Right: the same laser grown in a pocket etched through the buried oxide of an SOI wafer, its dot layer level with the silicon waveguide across a small gap, with a red arrow from the dots into the waveguide.">
  <figcaption><span class="capnum">Figure 27.4.</span> <strong>Quantum-dot lasers grown on silicon.</strong> (a) Blanket growth: the lattice mismatch starts threading dislocations at the silicon interface; strained-superlattice filter layers in the buffer turn most of them aside, so few reach the quantum dots, which tolerate the rest. The active region ends up several micrometres above the silicon. (b) Growth in a pocket etched through the BOX of an SOI wafer, with the layers chosen so that the dots are level with the silicon waveguide for butt coupling across a small gap. Schematic, not to scale. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">27.6</span>Thermal and reliability

A laser on silicon-on-insulator sits on the buried oxide, a good thermal insulator ([Chapter 18]({% link chapters/18_thermal.md %})). The heat it dissipates, $$P_\mathrm{diss} = IV - P_\mathrm{out}$$, raises its temperature by

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Self-heating</div>

$$\Delta T = Z_\mathrm{th}\,(IV - P_\mathrm{out}), \qquad I_\mathrm{th}(T) = I_\mathrm{th,0}\,e^{\Delta T/T_0}$$

</div>

with a thermal impedance $$Z_\mathrm{th}$$ that is larger on SOI than for a laser on its own InP substrate. Heat sinks through openings in the BOX (thermal shunts), and metal heat spreaders lower it ([Figure 27.5](#fig-27-5)).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 27.1 · How hot does it get?</div>

Suppose a laser with $$Z_\mathrm{th} = 80$$ K/W is driven at 100 mA and 1.5 V and emits 20 mW. It dissipates 130 mW and runs 10.4 K above its heat sink. With $$T_0 = 60$$ K its threshold is 19 % higher than if it were not self-heating, its gain peak moves by about 5 nm (and with it a Fabry–Pérot laser's wavelength; a DFB or ring laser's moves by about 1 nm), and at higher currents the extra heating can make the output roll over. Halving $$Z_\mathrm{th}$$ with a thermal shunt halves all of these. The laser demo of [Chapter 24]({% link chapters/24_fp.md %}#bdLaser) has a $$Z_\mathrm{th}$$ slider: with a 600 µm cavity on a 55 °C heat sink at 100 mA and 80 K/W it gives these numbers, and at higher currents its output rolls over.

</div>

<figure id="fig-27-5">
  <img src="{{ '/assets/figs/ch27_thermal.svg' | relative_url }}" style="width:600px" alt="Left: cross-section to scale of the bonded laser of Table 27.1 on a 2 micrometre buried oxide: substrate, BOX, silicon waveguide, n-InP contact layer with n contacts on both sides, MQW and p-InP mesa with p contact. Orange arrows carry heat from the MQW region down towards the BOX, which blocks most of it, and sideways to the right-hand n contact, whose metal shunt runs through the BOX to the substrate. Right: output power against current from 0 to 600 milliamps for no self-heating, Z_th 40 K/W and Z_th 80 K/W; the 80 K/W curve passes the marked point 20 mW, plus 10.4 K at 100 mA, peaks near 78 mW at about 420 mA and rolls over.">
  <figcaption><span class="capnum">Figure 27.5.</span> <strong>Heat on the buried oxide.</strong> (a) Cross-section of the laser of Table 27.1 on a 2 µm BOX, to scale: heat from the MQW region spreads through the III–V but crosses the BOX poorly; a metal shunt through the BOX next to the mesa gives it a path to the substrate (heat flow schematic). (b) L–I curves from the self-heating equations above, for a laser with I<sub>th,0</sub> = 20 mA, V = 0.9 V + 6 Ω × I and a slope efficiency of 0.26 W/A, chosen so that at 100 mA and Z<sub>th</sub> = 80 K/W it emits the 20 mW of Worked Example 27.1 and runs 10.4 K hot (dot). At 80 K/W the output rolls over at 78 mW near 420 mA; a shunt that halves Z<sub>th</sub> keeps it rising. Diode parameters illustrative. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

Reliability follows temperature: III–V lasers age faster when hot, through defect growth in the active region and facet degradation. Bonded and grown lasers must pass the same accelerated-ageing tests as conventional ones, at the highest operating temperature they will see.

## <span class="secnum">27.7</span>Open laser-integration projects

Laser integration has mostly been the domain of companies, but open projects now let students and researchers design lasers on silicon. The **SiEPICfab Shuksan** process design kit, released under the MIT licence, supports a multi-project run with laser integration {% include cite.html keys="shuksan" %}. UBC's **ELEC 413** course designs semiconductor lasers on these runs and publishes its designs and measurements {% include cite.html keys="elec413" %}, a source of real L–I curves and spectra for the analysis of [Chapter 37]({% link chapters/37_analysis.md %}).

## <span class="secnum">27.8</span>Directly modulated microring lasers

Most silicon transceivers modulate a continuous laser externally. A research alternative removes the modulator: make the laser itself a ring on silicon, and modulate its current directly {% include cite.html keys="palermo721l12,liang2020" %}. A heterogeneous **microring laser** is a III–V ring tens of micrometres across, bonded over a silicon bus waveguide that collects its light {% include cite.html keys="liang2009" %}. It needs no facets or Bragg mirrors, its small volume gives a low threshold, and its diameter sets its wavelengths. A row of rings of slightly different sizes on one bus is then a WDM transmitter with one directly modulated laser per channel and no separate multiplexer ([Figure 27.6](#fig-27-6)).

The ring's sensitivity is also its difficulty. A 40 µm ring with $$n_g = 3.7$$ has modes 3.69 nm apart at 1310 nm, but making it 0.1 % larger moves every mode by 1.31 nm, so lithography alone cannot place the channels, and each ring needs tuning, by a heater or by a MOS capacitor built into the ring {% include cite.html keys="liang2016,liang2020" %}. With an effective-index change of $$2\times10^{-4}$$ per kelvin, the modes also drift by 0.07 nm/K as the ring heats with its own drive current, so a thermal shunt (Section 27.6) matters as much as for any laser on silicon. Driving such a laser raises every problem of [Chapter 25]({% link chapters/25_dynamics.md %}): its response is fast and ringing on rising edges and slow on falling ones, so its CMOS driver equalises the two edges separately, designed against a compact model of the ring {% include cite.html keys="fan2019" %}. Quantum-dot gain ([Section 27.5](#275monolithic-growth)) lowers the threshold and steadies it against temperature {% include cite.html keys="wan2018,liang2020" %}, and injection locking from an external master laser extends the modulation bandwidth several times {% include cite.html keys="fan2020" %}.

<figure id="fig-27-6">
  <img src="{{ '/assets/figs/ch27_microring.svg' | relative_url }}" style="width:600px" alt="Top: top view to scale of four III-V microrings, 40 micrometres across, bonded over one straight silicon bus, each with a central contact labelled lambda 1 to lambda 4 and a heater arc on its far side; diameters D1 to D4 differ by fractions of a per cent; four wavelengths leave the bus on the right; 20 micrometre scale bar. Bottom: mode positions near 1310 nanometres for a 40 micrometre ring, 3.69 nanometres apart, and for a ring 0.1 per cent larger, every mode shifted by 1.31 nanometres.">
  <figcaption><span class="capnum">Figure 27.6.</span> <strong>A microring-laser WDM transmitter.</strong> (a) Four III–V microrings, 40 µm across and drawn to scale, bonded over one silicon bus; each has its own drive current and a heater (or a MOS capacitor) for tuning, and diameters differing by fractions of a per cent set their wavelengths. (b) Modes of a 40 µm ring with n<sub>g</sub> = 3.7 near 1310 nm, 3.69 nm apart, and of a ring 0.1 % larger: every mode moves by 1.31 nm, a third of the mode spacing, so lithography alone cannot place the channels. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

For low volumes and flexibility, an **external** laser or a **flip-chipped** known-good die. For high volumes with many lasers per chip, **heterogeneous** integration, which makes them all at once, lithographically aligned. **Micro-transfer printing** sits between the two, adding tested devices at high density. **Monolithic** quantum-dot growth promises the lowest cost at scale, once the coupling problem is solved. Every approach must manage heat on the insulating BOX.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Four flip-chipped DFB lasers, tested before assembly and butt-coupled to edge couplers ([Chapter 16]({% link chapters/16_edge.md %})), each on a thermal shunt through the BOX. A heterogeneous version is the high-volume alternative.

</div>

## Reading

{% include reflist.html keys="liang2010,komljenovic2016,zhou2015,shuksan,elec413,palermo721l12" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Lasers reach silicon off-chip, flip-chipped, bonded, transfer-printed or grown; each trades cost, density, coupling and heat.
- In heterogeneous lasers the fundamental supermode moves from the III–V to the silicon as the silicon widens: in the example, from 52 % in the MQW region and 1 % in silicon at 0.4 µm to 14 % and 78 % at 1.5 µm, crossing near 0.85 µm.
- Adiabatic tapers sweep through the crossing to transfer the light with little loss.
- Self-heating, ΔT = Z<sub>th</sub>(IV − P<sub>out</sub>), is worse on the BOX; thermal shunts help.
- Open PDKs and course data (SiEPICfab Shuksan, UBC ELEC 413) make laser integration accessible.
- Surface-emitting VCSELs can be flip-chipped over grating couplers, but only long-wavelength ones suit silicon waveguides.
- Directly modulated microring lasers give one laser per WDM channel without modulators (modes 3.69 nm apart for a 40 µm ring), at the price of tuning (1.31 nm per 0.1 % of diameter), self-heating and edge-dependent dynamics.

</div>
