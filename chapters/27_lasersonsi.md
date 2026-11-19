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
- explain how directly modulated microring lasers combine source, modulator and WDM, and what limits them;
- explain how lasers age and fail, and estimate their life and failure rate from accelerated tests.

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

Reliability follows temperature: III–V lasers age faster when hot, so the thermal impedance also sets how long a laser lives. [Section 27.9](#279reliability-how-lasers-age-and-fail) explains how lasers age and fail and how their life is measured, and its Worked Example 27.5 works out what the 80 K/W of this example costs in life.

## <span class="secnum">27.7</span>Open laser-integration projects

Laser integration has mostly been the domain of companies, but open projects now let students and researchers design lasers on silicon. The **SiEPICfab Shuksan** process design kit, released under the MIT licence, supports a multi-project run with laser integration {% include cite.html keys="shuksan" %}. UBC's **ELEC 413** course designs semiconductor lasers on these runs and publishes its designs and measurements {% include cite.html keys="elec413" %}, a source of real L–I curves and spectra for the analysis of [Chapter 37]({% link chapters/37_analysis.md %}).

## <span class="secnum">27.8</span>Directly modulated microring lasers

Most silicon transceivers modulate a continuous laser externally. A research alternative removes the modulator: make the laser itself a ring on silicon, and modulate its current directly {% include cite.html keys="palermo721l12,liang2020" %}. A heterogeneous **microring laser** is a III–V ring tens of micrometres across, bonded over a silicon bus waveguide that collects its light {% include cite.html keys="liang2009" %}. It needs no facets or Bragg mirrors, its small volume gives a low threshold, and its diameter sets its wavelengths. A row of rings of slightly different sizes on one bus is then a WDM transmitter with one directly modulated laser per channel and no separate multiplexer ([Figure 27.6](#fig-27-6)).

The ring's sensitivity is also its difficulty. A 40 µm ring with $$n_g = 3.7$$ has modes 3.69 nm apart at 1310 nm, but making it 0.1 % larger moves every mode by 1.31 nm, so lithography alone cannot place the channels, and each ring needs tuning, by a heater or by a MOS capacitor built into the ring {% include cite.html keys="liang2016,liang2020" %}. With an effective-index change of $$2\times10^{-4}$$ per kelvin, the modes also drift by 0.07 nm/K as the ring heats with its own drive current, so a thermal shunt (Section 27.6) matters as much as for any laser on silicon. Driving such a laser raises every problem of [Chapter 25]({% link chapters/25_dynamics.md %}): its response is fast and ringing on rising edges and slow on falling ones, so its CMOS driver equalises the two edges separately, designed against a compact model of the ring {% include cite.html keys="fan2019" %}. Quantum-dot gain ([Section 27.5](#275monolithic-growth)) lowers the threshold and steadies it against temperature {% include cite.html keys="wan2018,liang2020" %}, and injection locking from an external master laser extends the modulation bandwidth several times {% include cite.html keys="fan2020" %}.

<figure id="fig-27-6">
  <img src="{{ '/assets/figs/ch27_microring.svg' | relative_url }}" style="width:600px" alt="Top: top view to scale of four III-V microrings, 40 micrometres across, bonded over one straight silicon bus, each with a central contact labelled lambda 1 to lambda 4 and a heater arc on its far side; diameters D1 to D4 differ by fractions of a per cent; four wavelengths leave the bus on the right; 20 micrometre scale bar. Bottom: mode positions near 1310 nanometres for a 40 micrometre ring, 3.69 nanometres apart, and for a ring 0.1 per cent larger, every mode shifted by 1.31 nanometres.">
  <figcaption><span class="capnum">Figure 27.6.</span> <strong>A microring-laser WDM transmitter.</strong> (a) Four III–V microrings, 40 µm across and drawn to scale, bonded over one silicon bus; each has its own drive current and a heater (or a MOS capacitor) for tuning, and diameters differing by fractions of a per cent set their wavelengths. (b) Modes of a 40 µm ring with n<sub>g</sub> = 3.7 near 1310 nm, 3.69 nm apart, and of a ring 0.1 % larger: every mode moves by 1.31 nm, a third of the mode spacing, so lithography alone cannot place the channels. Drawn by <code>figsrc/ch27_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">27.9</span>Reliability: how lasers age and fail

A transceiver's laser must keep working for the life of the equipment, many years, and it is the part most likely not to (Section 27.1). Reliability engineering asks three questions about it. How does a laser fail: what physical process ends its life? How many lasers fail, and when: what are the statistics of a population? And how can months of testing predict years of use? This section answers them for the lasers of Part VI, Fabry–Pérot and DFB edge emitters, directly modulated lasers and EMLs, VCSELs and lasers on silicon, and builds on the self-heating of Section 27.6 {% include cite.html keys="fukuda1991,ueda1996" %}.

### How lasers fail

Lasers degrade at three speeds {% include cite.html keys="fukuda1991,ueda1996" %}: **gradually**, over thousands of hours; **rapidly**, over hours to hundreds of hours; and **suddenly**, in an instant. [Figure 27.7](#fig-27-7) marks where each strikes.

**Gradual degradation.** Each time an electron and a hole recombine at a defect without emitting light, about an electronvolt of energy goes into the lattice at that one spot. The kick can help the defect move, react with another or multiply: a **recombination-enhanced defect reaction** {% include cite.html keys="kimerling1978" %}. A running laser therefore makes new non-radiative centres, slowly, and faster when it is hot and its current density is high. More non-radiative recombination is a larger $$A$$ in the recombination rate $$R(N)$$ of [Chapter 24]({% link chapters/24_fp.md %}), so the threshold current rises; defects that absorb light, or a p-dopant such as zinc diffusing into the wells, also lower the slope efficiency {% include cite.html keys="buffolo2021" %}. At constant current the output falls; under automatic power control the current rises. The change is smooth, so it can be measured and extrapolated ([Figure 27.9](#fig-27-9)).

**Rapid degradation.** In GaAs/AlGaAs lasers a dislocation that reaches the active region can grow, by recombination-enhanced climb, into a network of dislocation loops within hours. It shows in the emission as **dark-line defects**, and it was the main failure of the early continuous-wave GaAs lasers {% include cite.html keys="petroff1973" %}. Substrates and growth with few dislocations cured it, and InGaAsP/InP lasers are far less prone to it {% include cite.html keys="ueda1996" %}. It returns wherever GaAs-based layers carry dislocations: in VCSELs, and in lasers grown on silicon.

**Sudden failure at the facet.** A cleaved facet is a surface, rich in states where carriers recombine and light is absorbed. The heat narrows the band gap there, so the facet absorbs more light and heats further, a runaway that can melt it within microseconds: **catastrophic optical damage** (COD) {% include cite.html keys="tomm2011" %}. AlGaAs facets also oxidise as they run, which slowly raises their absorption until a gradual change ends suddenly. Dielectric facet coatings, the AR and HR coatings of [Chapter 24]({% link chapters/24_fp.md %}) and [Chapter 26]({% link chapters/26_tunable.md %}), passivate the surface. COD limits high-power lasers most; bonded lasers on silicon, whose light leaves through a silicon facet, avoid it altogether (below).

**Electrostatic discharge.** A person or tool charged to a few hundred volts that touches a laser's leads drives through it a current pulse far beyond its rating. The human-body model of ESD testing discharges 100 pF through 1.5 kΩ {% include cite.html keys="js001" %}: at 1000 V that is a 0.67 A peak and 50 µJ, in a pulse that decays in 150 ns. Reverse pulses, which break the junction down over a small area, do the most damage {% include cite.html keys="zhang2023esd" %}. The damage can be immediate, or latent: a small damaged region that grows later like any other defect. Lasers are therefore handled with ESD precautions, and their ESD threshold is part of qualification.

**Edge emitters and DMLs.** Fabry–Pérot and DFB lasers share all of these mechanisms. A directly modulated laser ([Chapter 25]({% link chapters/25_dynamics.md %})) runs at a high bias for speed, and degradation accelerates with current (see below), so it ages faster than a continuous-wave laser feeding an external modulator. Its ageing also lowers the slope efficiency, which shrinks the extinction ratio unless the driver tracks it ([Section 25.9]({% link chapters/25_dynamics.md %}#259output-stages-and-temperature-control)).

**EMLs.** In an EML ([Section 20.4]({% link chapters/20_modulators.md %}#204electro-absorption-modulators)) the DFB runs continuously at moderate current; the new stress is in the modulator, which works by absorbing light. Each absorbed 1550 nm photon (0.80 eV) frees at most one electron, 1.25 A/W, so absorbing 5 mW makes 6.25 mA of photocurrent, and at a reverse bias of 2 V the modulator dissipates $$P_\mathrm{abs} + I_\mathrm{ph}V = 5 + 12.5 = 17.5$$ mW, concentrated near its input, where the light is strongest. The heat moves the absorption edge to longer wavelengths, so the modulator absorbs more and heats more: a thermal instability that limits the optical power it can take {% include cite.html keys="coenen2023" %}. The junction where the laser's and the modulator's active layers meet, a regrown butt joint or a selectively grown transition {% include cite.html keys="coldren" %}, under an isolating gap between the two contacts, is one more interface to qualify.

**VCSELs.** The oxide aperture that makes a VCSEL efficient ([Section 24.8]({% link chapters/24_fp.md %}#248the-vertical-cavity-surface-emitting-laser)) is also its weak point. The oxide shrinks as it forms, and at its tip, a fraction of a micrometre from the quantum wells, the stress can exceed what GaAs withstands and nucleate dislocations that grow into dark lines {% include cite.html keys="coppeta2023" %}. Current crowds into the aperture: the 6 µm VCSEL of Section 24.8 at 8 mA carries 28 kA/cm², and a 4 µm one at the same current 64 kA/cm², 2.25 times more. Wear-out accelerates with current density, and larger apertures generally last longer {% include cite.html keys="hawkins2002,guenter2013" %}. In non-hermetic packages, moisture adds failure modes under bias (dislocation growth, cracks, degradation of the aperture surface) that unbiased damp-heat storage does not reveal {% include cite.html keys="xie2003" %}. And the small area makes VCSELs sensitive to ESD: in one study, human-body-model pulses degraded oxide VCSELs from 200 V forward and −50 V reverse, with dark lines spreading from the edge of the aperture {% include cite.html keys="zhang2023esd" %}. A 200 V pulse peaks at 133 mA, nine times the current at which the VCSEL of Section 24.8 rolls over.

**Bonded lasers on silicon.** Heterogeneous lasers use the same III–V layers as conventional ones, so they share their gradual mechanisms, the growth of non-radiative centres and the diffusion of dopants {% include cite.html keys="buffolo2021" %}. Bonding added one more: early devices formed thermally induced defects at the bond interface, and a strained superlattice between the interface and the active region raised the yield and cut premature failures in ageing at up to 85 °C {% include cite.html keys="srinivasan2013,buffolo2021" %}. In exchange the light leaves through a silicon facet, with no III–V facet to oxidise or melt, which allows non-hermetic packaging: one manufacturer, shipping millions of such transceivers a year, reported 36 lasers aged at 80 °C and 150 mA for over 19,000 h with negligible drift of the current needed for 10 mW {% include cite.html keys="jones2019,buffolo2021" %}. Their particular stress is heat on the BOX (Worked Example 27.5). Flip-chipped and printed lasers are conventional lasers, facets included, and age like them.

**Lasers grown on silicon** contain dislocations from the 4 % lattice mismatch (Section 27.5). GaAs quantum-well lasers on silicon failed suddenly from dark-line defects, typically within hundreds of hours, and the longest reported life was about 200 h {% include cite.html keys="jung2018" %}. Quantum dots changed that. At $$7.3\times10^6$$ cm⁻² the threading dislocations are on average 3.7 µm apart, while dots at up to $$6\times10^{10}$$ cm⁻² are 41 nm apart, some 8,200 dots for every dislocation. A carrier in a quantum well diffuses several micrometres in its plane, far enough to find a dislocation; in a dot layer it is captured within about a micrometre {% include cite.html keys="norman2019" %}. Less recombination then happens at dislocations, and less energy feeds their growth {% include cite.html keys="liu2015qd,buffolo2021" %}. The tolerance is not complete: at room temperature some carriers escape from the dots into the thin wetting layer and reach dislocations, and one misfit dislocation darkens a strip about 1 µm wide {% include cite.html keys="selvidge2019" %}. Life still depends strongly on the dislocation density: lowering it from $$2.8\times10^8$$ to $$7.3\times10^6$$ cm⁻² (from 0.6 to 3.7 µm apart) lengthened the extrapolated life by about five orders of magnitude, to more than $$10^7$$ h at 35 °C {% include cite.html keys="jung2018" %}. The limit now is misfit dislocations lying near the dots, formed as the wafer cools because III–V and silicon contract differently, and lengthened during operation by recombination-enhanced climb {% include cite.html keys="mukherjee2020,selvidge2020" %}. Trapping layers that hold them away from the dots, together with threading densities near $$10^6$$ cm⁻², gave an extrapolated median life of over 22 years at 80 °C {% include cite.html keys="shang2021" %}.

<figure id="fig-27-7">
  <img src="{{ '/assets/figs/ch27_rel_sites.svg' | relative_url }}" style="width:660px" alt="Four schematic cross-sections with numbered failure sites. (a) An edge-emitting laser along its cavity: n-InP, a quantum-well active layer and p-InP between contacts, a blue rear coating and a violet front coating, light leaving the front facet, where an orange hot spot is marked 1 facet: oxidation, COD; other labels: 2 coating, 3 active region: non-radiative defects grow, dark lines in GaAs, 4 p-dopant diffusion. (b) An EML: a DFB section with a grating and an EAM section with different wells, a gap in the top contact marked 5 isolation gap, the interface of the two active layers marked 6 laser-modulator junction, and a hot spot at the EAM input marked 7 photocurrent heating, thermal runaway. (c) An oxide VCSEL: Bragg mirrors, quantum wells and an oxide layer whose tips are marked 8 oxide tip: strain, dislocations start, with a dislocation line running down through the wells; 9 mesa wall: humidity; 10 small area: ESD. (d) Left: a bonded III-V laser on SOI with 11 bond interface: voids, defects, 12 BOX: heat, 13 mesa walls, and the note no III-V facet. Right: a quantum-dot laser grown on silicon with threading dislocations rising from the substrate, most stopped by a filter layer, marked 14, and a misfit dislocation just under the dot layer marked 15 misfit dislocation near the dots, REDC.">
  <figcaption><span class="capnum">Figure 27.7.</span> <strong>Where lasers fail.</strong> (a) A Fabry–Pérot or DFB edge emitter along its cavity: 1 the output facet, where surface recombination and absorption can run away into catastrophic optical damage, and where AlGaAs oxidises; 2 the dielectric coatings that passivate the facets (AR front, HR rear); 3 the active region, where non-radiative defects multiply (gradual degradation) or, in GaAs-based lasers, dislocations grow into dark lines (rapid degradation); 4 the p-dopant, diffusing towards the wells. (b) An EML: 5 the isolation gap between the DFB and modulator contacts; 6 the junction between the two active layers; 7 the modulator's input, where the photocurrent of the absorbed light heats it. (c) An oxide VCSEL: 8 the oxide tip, where the shrinkage of the oxide strains the layers next to the wells and dislocations can start; 9 the mesa wall, exposed to moisture in a non-hermetic package; 10 its small area, which makes it sensitive to ESD. (d) Lasers on silicon. Bonded: 11 the bond interface (voids, thermally induced defects); 12 the BOX, which traps the heat (Section 27.6); 13 the etched mesa walls, where the active layer meets a surface; the light leaves through the silicon, so there is no III–V facet. Grown: 14 threading dislocations from the lattice mismatch, most turned aside by filter layers; 15 misfit dislocations near the dots, which lengthen by recombination-enhanced climb (REDC). Schematic, not to scale. Drawn by <code>figsrc/ch27_rel.py</code>.</figcaption>
</figure>

### Life statistics: the bathtub curve

One laser's life cannot be predicted; a population's can. Its **failure rate**, or hazard rate, $$h(t)$$ is the fraction of the surviving lasers that fail per hour at age $$t$$ {% include cite.html keys="nistreliability" %}. For lasers it is tiny, so it is counted in **FIT**, failures per $$10^9$$ device-hours. Over a population's life the failure rate traces a **bathtub** ([Figure 27.8](#fig-27-8)):

- **Infant mortality.** A few weak lasers, with growth or processing defects, contamination or ESD damage, fail early, and as they die out the rate falls. A Weibull distribution with a shape parameter $$\beta < 1$$ describes them.
- **Random failures.** A low, roughly constant rate $$\lambda$$ from rare events. A constant rate means exponential survival, $$R(t) = e^{-\lambda t}$$, with a mean time to failure MTTF = $$1/\lambda$$. That MTTF is not a life: 100 FIT is an MTTF of $$10^7$$ h, or 1,141 years, yet a data centre with $$10^5$$ such lasers loses 88 of them a year.
- **Wear-out.** Gradual degradation eventually carries every laser past its end-of-life limit. The times at which it does are spread over a factor of a few, and are usually described by a **lognormal** distribution: $$\ln t$$ is normally distributed about the logarithm of the median life $$t_{50}$$, with standard deviation $$\sigma$$ {% include cite.html keys="nistreliability,fukuda1991" %}.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Failure rate and the lognormal life distribution</div>

$$h(t) = \frac{f(t)}{1 - F(t)}, \qquad F(t) = \Phi\!\left(\frac{\ln(t/t_{50})}{\sigma}\right), \qquad 1\ \mathrm{FIT} = \frac{1\ \text{failure}}{10^{9}\ \text{device-hours}}$$

</div>

Here $$F(t)$$ is the fraction failed by time $$t$$, $$f = \mathrm{d}F/\mathrm{d}t$$ the density of failure times and $$\Phi$$ the standard normal distribution; a lognormal population has an MTTF of $$t_{50}e^{\sigma^2/2}$$.

**Burn-in.** Infant failures are screened out before shipping: every laser runs for a short time hot and at high current, is measured again, and those that failed or drifted are rejected {% include cite.html keys="fukuda1991" %}. In the model of [Figure 27.8](#fig-27-8), with 1 % weak lasers, 48 h at 100 °C is worth 1,800 h of use (at the 0.61 eV of Worked Example 27.4), removes 98.6 % of the weak lasers, and lowers the failure rate at the start of service from 450,000 FIT to 180 FIT. The cost is a sliver of wear-out life.

**The spread matters as much as the median.** For lognormal populations with the same median life of about a million hours, a narrow spread ($$\sigma$$ = 0.5) wears out at 0.04 FIT at 10 years, a wide one ($$\sigma$$ = 1) at 203 FIT ([Figure 27.8](#fig-27-8)b): the first lasers of a widely spread population wear out decades before the median one.

<figure id="fig-27-8">
  <img src="{{ '/assets/figs/ch27_rel_bathtub.svg' | relative_url }}" style="width:640px" alt="(a) Failure rate in FIT against operating time from 1 hour to 1 million hours, both on logarithmic axes, with a top axis marking 1, 10 and 100 years. Without burn-in the rate falls from about 450,000 FIT through infant mortality to a flat random floor of 10 FIT between about 5,000 and 80,000 hours, then rises through lognormal wear-out to about 1,000 FIT at a million hours. After a 48 hour burn-in at 100 degrees the curve starts at about 180 FIT and joins the floor. Dotted lines show the random and wear-out parts alone. (b) Wear-out failure rate against years at 40 degrees on a logarithmic axis for sigma 0.5, 0.62 and 1.0: the wider the spread, the earlier and steeper the rise.">
  <figcaption><span class="capnum">Figure 27.8.</span> <strong>The bathtub curve.</strong> (a) Failure rate of a model laser population built from three distributions: 1 % weak lasers with early failures (Weibull, β = 0.5, scale 100 h), random failures at 10 FIT for every laser, and lognormal wear-out with the \(t_{50}\) = 1.06 × 10⁶ h and σ = 0.62 of Worked Example 27.4. Without screening, the rate starts at 450,000 FIT, falls through infant mortality to the random floor, and rises through wear-out after about ten years (top axis). A burn-in of 48 h at 100 °C, worth 1,800 h of use at 0.61 eV, removes 98.6 % of the weak lasers and starts the service life at 180 FIT (dashed). (b) The wear-out rate for the same median life and three spreads: 0.04, 2.1 and 203 FIT at 10 years for σ = 0.5, 0.62 and 1.0. Model parameters illustrative. Drawn by <code>figsrc/ch27_rel.py</code>.</figcaption>
</figure>

### End of life and automatic power control

A laser has failed when it can no longer meet its specification, so its **end of life** is a limit on a drifting parameter, chosen for the product: for example a rise of the operating current at constant power by 20 % or 50 % for a laser under power control, or a fall of the output by 1 or 2 dB at constant current. Research papers on lasers on silicon often use a doubling of the threshold current {% include cite.html keys="jung2018,shang2021" %}.

**Power control hides ageing, and reveals it.** The automatic power control of [Section 25.9]({% link chapters/25_dynamics.md %}#259output-stages-and-temperature-control) holds the output constant, so the link sees nothing as the threshold climbs: the drive current rises instead. A transceiver that reports its laser's bias current shows the ageing long before the light changes. The end comes when the driver runs out of current, or when the extra current, through self-heating, raises the threshold faster than the loop can follow and the laser rolls over (Section 27.6), a feedback that is strongest on SOI (Worked Example 27.5). Power control can also mislead: a loop that reads a monitor photodiode behind the rear facet holds the rear power, and if the two facets age differently, the front power drifts while the loop reports that all is well.

**Life tests.** [Figure 27.9](#fig-27-9) shows a life test, with synthetic data: twelve lasers at each of three junction temperatures, held at constant power for 5000 h, their operating current read periodically. The rise grows roughly as $$\sqrt{t}$$, a straight line of slope 1/2 on log–log axes. Each laser's fit is extrapolated to the +20 % end-of-life line, and its time to failure is plotted on a lognormal probability scale, where a lognormal population falls on a straight line whose middle is $$t_{50}$$ and whose slope gives $$\sigma$$. Real life tests extrapolate such fitted drifts in the same way {% include cite.html keys="fukuda1991,jung2018" %}, and the extrapolation assumes that no new mechanism appears after the test ends.

<figure id="fig-27-9">
  <img src="{{ '/assets/figs/ch27_rel_ageing.svg' | relative_url }}" style="width:640px" alt="(a) Rise of operating current in per cent against ageing time on logarithmic axes from 100 hours to 500,000 hours. Thin lines show twelve lasers at each of 70, 85 and 100 degrees during a shaded 5000 hour test, rising as straight lines of slope one half; dashed lines extend the median laser at each temperature to a horizontal end-of-life line at plus 20 per cent, which they reach at about 27,000, 66,000 and 144,000 hours. (b) Cumulative failures in per cent on a probability scale against extrapolated time to failure on a logarithmic axis: three straight rows of points with fitted lines, the hotter the further left.">
  <figcaption><span class="capnum">Figure 27.9.</span> <strong>A life test under power control (synthetic data).</strong> (a) The rise of the current needed for constant output, for twelve lasers at each of three junction temperatures during a 5000 h test (thin lines, shaded period), drawn from a model with a drift growing as \(\sqrt{t}\), an activation energy of 0.60 eV, a lognormal spread between lasers and 0.12 % of measurement noise. Each laser's record is fitted with \(A\sqrt{t}\) and extrapolated to the end-of-life line at +20 %; the dashed lines and dots are the median laser at each temperature, which reaches it after 27,400 h at 100 °C, 65,900 h at 85 °C and 143,800 h at 70 °C. (b) The 36 extrapolated times to failure on a lognormal probability scale, where a lognormal distribution is a straight line: its 50 % point is \(t_{50}\), and its slope gives σ = 0.55 to 0.65. Drawn by <code>figsrc/ch27_rel.py</code>.</figcaption>
</figure>

### Accelerated testing

Wear-out at the use temperature takes decades, so tests make it happen faster, hotter and at higher current. A thermally activated process runs at a rate proportional to $$e^{-E_a/kT}$$, with an **activation energy** $$E_a$$ set by its mechanism, and the time to failure shrinks by the **acceleration factor** AF:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Acceleration factor</div>

$$\mathrm{AF} = \exp\!\left[\frac{E_a}{k}\left(\frac{1}{T_\mathrm{use}} - \frac{1}{T_\mathrm{stress}}\right)\right]\left(\frac{I_\mathrm{stress}}{I_\mathrm{use}}\right)^{n}, \qquad t_\mathrm{use} = \mathrm{AF}\cdot t_\mathrm{stress}$$

</div>

with the temperatures in kelvin at the junction, self-heating included, and $$k = 8.617\times10^{-5}$$ eV/K {% include cite.html keys="nistreliability" %}. The current (or current-density) term, with exponent $$n$$, captures the faster growth of defects at higher injection; facet mechanisms are accelerated by optical power instead. The activation energies of failure mechanisms span roughly 0.3 to 1.5 eV {% include cite.html keys="nistreliability" %}; VCSEL wear-out models have long used about 0.7 eV with a modest current exponent {% include cite.html keys="guenter2013" %}, and 845 nm VCSELs for silicon photonics gave 0.43–0.68 eV {% include cite.html keys="zenari2026" %}. Because $$E_a$$ sits in an exponent, it is both the most important and the least certain number of a reliability estimate ([Figure 27.10](#fig-27-10)a).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 27.2 · What does 5000 h at 85 °C prove?</div>

From an 85 °C stress (358.15 K) to use at 40 °C (313.15 K), $$1/T_\mathrm{use} - 1/T_\mathrm{stress} = 4.01\times10^{-4}$$ K⁻¹. With $$E_a$$ = 0.4, 0.5 and 0.7 eV, $$E_a/k$$ = 4,640, 5,800 and 8,120 K, and the acceleration factors are $$e^{1.86} = 6.4$$, $$e^{2.33} = 10.3$$ and $$e^{3.26} = 26.0$$. A 5000 h test at 85 °C therefore stands for 32,000 h (3.7 years), 51,000 h (5.9 years) or 130,000 h (14.8 years) at 40 °C: the same test proves four times more or less, depending on an activation energy that is rarely known better than this. Running it at 1.5 times the use current as well, with $$n = 2$$, multiplies the acceleration by 2.25 (to 59 for 0.7 eV), if the current exponent is right. Either way, a 5000 h test without failures shows that nothing goes wrong early; the years beyond come only from extrapolating the drift (Worked Example 27.4).

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 27.3 · An upper bound from zero failures</div>

Suppose 25 lasers run 2000 h at 85 °C and none fails. The best estimate of the failure rate is zero, but the test cannot exclude a small one. For random failures at a rate $$\lambda$$, the upper confidence bound after $$r$$ failures in $$T$$ device-hours is $$\lambda < \chi^2(\mathrm{CL};\,2r+2)/(2T)$$ {% include cite.html keys="nistreliability" %}; for $$r = 0$$ the chi-square value with two degrees of freedom is simply $$-2\ln(1-\mathrm{CL})$$: 1.833 at 60 % confidence and 4.605 at 90 %.

- Without acceleration, $$T = 25 \times 2000\ \mathrm{h} = 5\times10^4$$ h, and $$\lambda < 1.833/(2\times5\times10^4\ \mathrm{h}) = 1.8\times10^{-5}$$ h⁻¹: 18,300 FIT at 60 % confidence (46,000 FIT at 90 %).
- If the failures are thermally activated with 0.5 eV, each test hour is worth 10.3 hours at 40 °C: $$T = 5.1\times10^5$$ h and $$\lambda <$$ 1,790 FIT (4,490 FIT). With 0.7 eV: 704 FIT (1,770 FIT).
- To demonstrate 100 FIT at 60 % confidence with 5000 h at 85 °C takes $$0.916/(10^{-7}\ \mathrm{h^{-1}} \times 5000\ \mathrm{h} \times \mathrm{AF})$$ = 179 lasers at 0.5 eV, or 70 at 0.7 eV.

A qualification test thus bounds the random failure rate only to hundreds or thousands of FIT. Rates of a few FIT can only come from wear-out models and from the many device-hours of lasers in the field, and they assume that the random failures are accelerated like the wear-out, which a test cannot show.

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 27.4 · From drift to FIT</div>

In the life test of [Figure 27.9](#fig-27-9), the median laser at 85 °C drifted by 5.25 % in 5000 h. If the drift grows as $$\sqrt{t}$$, it reaches the +20 % limit after $$5000\ \mathrm{h} \times (20/5.25)^2 \approx 72{,}000$$ h. Fitting every laser's whole record instead gives times to failure with a median of 65,900 h and $$\sigma$$ = 0.65 at 85 °C. The medians at 70, 85 and 100 °C fall on one Arrhenius line with $$E_a$$ = 0.61 eV ([Figure 27.10](#fig-27-10)b), which extrapolates to $$t_{50} = 1.06\times10^6$$ h (121 years) at 40 °C, with a pooled $$\sigma$$ = 0.62.

The wear-out failure rate at a given age follows from the lognormal. At 10 years ($$8.77\times10^4$$ h), $$z = \ln(t/t_{50})/\sigma = -4.04$$, so $$F = \Phi(z)$$ = 27 ppm have failed, and

$$h = \frac{\varphi(z)}{\sigma t\,[1 - \Phi(z)]} = \frac{1.15\times10^{-4}}{0.62 \times 8.77\times10^{4}\ \mathrm{h}} = 2.1\times10^{-9}\ \mathrm{h^{-1}} = 2.1\ \mathrm{FIT},$$

with $$\varphi$$ the standard normal density. The rate climbs to 16 FIT at 15 years, 53 FIT at 20 and 113 FIT at 25: wear-out is negligible for a decade and then dominates. The same lasers with their junctions at 70 °C instead of 40 °C would have a median life of 17 years, and 20 % of them would fail within 10 years: the use temperature matters as much as the test.

</div>

<figure id="fig-27-10">
  <img src="{{ '/assets/figs/ch27_rel_arrhenius.svg' | relative_url }}" style="width:640px" alt="(a) Acceleration factor relative to 40 degrees against stress temperature from 40 to 125 degrees, on a logarithmic axis, for activation energies of 0.4, 0.5, 0.7 and 1.0 electronvolts; at 85 degrees the curves reach 6.4, 10.3, 26.0 and 105. (b) Median life on a logarithmic axis against 1000 over temperature, with a top axis in degrees: three points with error bars at 70, 85 and 100 degrees on a straight dashed line, labelled slope Ea = 0.61 eV, extended to a square at 40 degrees labelled 1.1 times 10 to the 6 hours, 121 years.">
  <figcaption><span class="capnum">Figure 27.10.</span> <strong>Temperature acceleration.</strong> (a) The acceleration factor of a stress at temperature \(T\) over use at 40 °C, for activation energies of 0.4 to 1.0 eV: at 85 °C it is 6.4, 10.3, 26.0 and 105 (Worked Example 27.2). (b) Arrhenius plot of the median lives of <a href="#fig-27-9">Figure 27.9</a> (error bars ±σ/√12): \(\ln t_{50}\) is a straight line against \(1/T\) with slope \(E_a/k\). The fit gives 0.61 eV (the synthetic data were drawn with 0.60 eV) and extrapolates to \(t_{50}\) = 1.06 × 10⁶ h, 121 years, at 40 °C. Drawn by <code>figsrc/ch27_rel.py</code>.</figcaption>
</figure>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Accelerating the wrong mechanism</div>

Acceleration works only if the stress speeds up the mechanism that limits life in use, and no other. Too hot, or too much current, and a test can trigger failures the field never sees (solder and contacts, thermal roll-over, COD), or hide a mechanism with a lower activation energy that dominates at the use temperature; a life extrapolated with the wrong $$E_a$$ can be wrong by an order of magnitude ([Figure 27.10](#fig-27-10)a). Test at several temperatures and currents, check that the failure modes are the same, and put the junction temperature, not the oven's, into the Arrhenius factor.

</div>

### Qualification

Before a laser goes into telecommunications equipment, its supplier qualifies it, usually against Telcordia's GR-468-CORE, the generic reliability-assurance requirements for optoelectronic devices in such equipment {% include cite.html keys="gr468" %}. It distinguishes operating environments, from temperature-controlled central offices to uncontrolled outdoor cabinets, and qualification programmes based on it combine mechanical tests (shock, vibration), environmental tests (temperature cycling, hot and cold storage, damp heat), an ESD threshold, and the accelerated ageing of operating devices. Public descriptions give the flavour: accelerated ageing at +70 to +85 °C for 2000 to 5000 h; temperature cycling between −40 °C and +70 or +85 °C, 100 cycles for central-office and 500 for remote-terminal equipment; and samples such as 25 laser modules aged at +85 °C for 2000 h with no failure allowed {% include cite.html keys="ewing2001" %}, the case of Worked Example 27.3. Damp heat is commonly 85 °C and 85 % relative humidity; for non-hermetic parts, VCSEL arrays and lasers on silicon among them, it must also be run under bias to reveal moisture-driven failures {% include cite.html keys="xie2003" %}. Passing shows that a design has no early-life or early wear-out problem; the failure rate quoted to customers comes from extrapolated wear-out (Worked Example 27.4) and from field returns. Bonded and grown lasers on silicon face the same tests, at the highest temperature they will see.

### Heat and life on silicon

Section 27.6 showed that the BOX makes a laser on SOI run hotter. That shortens its life twice over.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 27.5 · What does 80 K/W cost in life?</div>

Take the laser of Worked Example 27.1 and [Figure 27.5](#fig-27-5) on a 70 °C heat sink, held at 20 mW by power control, and compare three thermal impedances: 80 K/W on SOI, 40 K/W with a thermal shunt, and an illustrative 20 K/W for the same laser on its own InP substrate.

- **Hotter.** The laser needs 100.0, 98.0 and 97.1 mA, dissipates 130, 126 and 124 mW, and runs 10.4, 5.0 and 2.5 K above the heat sink: at 80.4, 75.0 and 72.5 °C. Between 80.4 and 72.5 °C, the Arrhenius factor with 0.5 eV (0.7 eV) shortens the life of the SOI laser to 0.69 (0.59) of the InP laser's.
- **Less margin.** Under power control, ageing raises the threshold, the loop raises the current, and the extra current heats the laser and raises the threshold further. Solving the self-heating equations of Section 27.6 with the threshold raised to $$(1+\delta)I_\mathrm{th,0}$$ shows that the operating current reaches +20 % when the threshold has risen by $$\delta$$ = 90.4 % at 20 K/W, but already at 73.5 % at 80 K/W. If the threshold rises as $$\sqrt{t}$$, the time to get there scales as $$\delta^2$$: $$(73.5/90.4)^2 = 0.66$$.
- **Together**, the SOI laser lives 0.45 (0.39) times as long as the one on InP. A thermal shunt recovers much of the loss: at 40 K/W the factor is 0.78 (0.74).

</div>

The same holds for VCSELs bonded or printed on silicon, whose small footprint already gives them a high thermal impedance: larger apertures, with lower thermal impedance, push the onset of fast degradation to higher currents {% include cite.html keys="zenari2026" %}.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

For low volumes and flexibility, an **external** laser or a **flip-chipped** known-good die. For high volumes with many lasers per chip, **heterogeneous** integration, which makes them all at once, lithographically aligned. **Micro-transfer printing** sits between the two, adding tested devices at high density. **Monolithic** quantum-dot growth promises the lowest cost at scale, once the coupling problem is solved. Every approach must manage heat on the insulating BOX, which also sets how long the lasers live (Section 27.9).

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Four flip-chipped DFB lasers, tested before assembly and butt-coupled to edge couplers ([Chapter 16]({% link chapters/16_edge.md %})), each on a thermal shunt through the BOX. A heterogeneous version is the high-volume alternative.

</div>

## Reading

{% include reflist.html keys="liang2010,komljenovic2016,zhou2015,shuksan,elec413,palermo721l12,fukuda1991,ueda1996,buffolo2021,gr468,nistreliability" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Lasers reach silicon off-chip, flip-chipped, bonded, transfer-printed or grown; each trades cost, density, coupling and heat.
- In heterogeneous lasers the fundamental supermode moves from the III–V to the silicon as the silicon widens: in the example, from 52 % in the MQW region and 1 % in silicon at 0.4 µm to 14 % and 78 % at 1.5 µm, crossing near 0.85 µm.
- Adiabatic tapers sweep through the crossing to transfer the light with little loss.
- Self-heating, ΔT = Z<sub>th</sub>(IV − P<sub>out</sub>), is worse on the BOX; thermal shunts help.
- Open PDKs and course data (SiEPICfab Shuksan, UBC ELEC 413) make laser integration accessible.
- Surface-emitting VCSELs can be flip-chipped over grating couplers, but only long-wavelength ones suit silicon waveguides.
- Directly modulated microring lasers give one laser per WDM channel without modulators (modes 3.69 nm apart for a 40 µm ring), at the price of tuning (1.31 nm per 0.1 % of diameter), self-heating and edge-dependent dynamics.
- Lasers fail gradually (non-radiative defects multiply, the threshold rises), rapidly (dark-line defects in GaAs-based layers) or suddenly (catastrophic optical damage at facets, ESD). VCSELs add oxide-tip stress, humidity and ESD sensitivity; EMLs add photocurrent heating in the modulator.
- Failure rates are counted in FIT (failures per 10⁹ device-hours) and trace a bathtub: infant mortality, screened by burn-in; random failures; lognormal wear-out. An MTTF is not a life: 100 FIT is 1,141 years, yet 88 failures a year among 10⁵ lasers.
- Arrhenius acceleration from 85 °C to 40 °C is 6.4, 10.3 and 26.0 for 0.4, 0.5 and 0.7 eV, so a 5000 h test stands for 3.7 to 14.8 years; zero failures in 25 lasers × 2000 h bounds the random rate only to 700–1,800 FIT (60 % confidence).
- Under power control ageing shows as a rising current; extrapolating it to an end-of-life limit gives a lognormal life and its FIT rate year by year (2.1 FIT at 10 years, 53 FIT at 20 years in the example).
- Quantum dots tolerate threading dislocations far better than quantum wells (some 8,200 dots per dislocation at 7.3 × 10⁶ cm⁻²); misfit dislocations near the dots now limit their life. Bonded lasers have no III–V facet, but the BOX's heat costs life: 80 K/W instead of 20 K/W more than halves it in the example.

</div>
