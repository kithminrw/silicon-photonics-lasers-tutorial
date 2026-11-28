---
title: "4. Materials and Platforms: Si, SiN, TFLN, BTO and InP"
parent: "Part I · Foundations"
nav_order: 4
permalink: /part-1/ch04/
chapter: 4
---

# <span class="chapnum">Chapter 4</span>Materials and Platforms: Si, SiN, TFLN, BTO and InP

Silicon is the workhorse, but no single material does everything: the platform is chosen by what the chip must do.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- list what a photonic platform must provide: guiding, tuning, modulating, detecting, generating and amplifying light;
- compare Si, SiN, thin-film LiNbO₃, BaTiO₃ and InP by index, transparency, loss, electro-optic and thermo-optic response, and gain;
- describe the layer stack and typical waveguide of each platform;
- distinguish monolithic, hybrid and heterogeneous integration;
- find the foundry and MPW routes and the open PDKs that this tutorial uses.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which platform for which job, and when is one platform not enough?

</div>

## <span class="secnum">4.1</span>What a platform must provide

A photonic platform is a material system plus a manufacturing process plus a design kit. A complete transceiver needs six functions from it: **guide** light with low loss and tight bends, **tune** it slowly (for calibration and locking), **modulate** it fast, **detect** it, **generate** it and **amplify** it. [Table 4.1](#tab-4-1) shows which platforms provide which functions natively; the gaps are why most real products combine materials.

**Table 4.1. Native capabilities of the main platforms.** ● native, ◐ only with an added material or a bonded or attached chip, ○ not available.
{: .tabcaption #tab-4-1 }

| Function | Si (SOI) | SiN | TFLN | BTO on Si | InP |
|---|---|---|---|---|---|
| Low-loss guiding, tight bends | ● tight bends, moderate loss | ● lowest loss, larger bends | ● | ● | ● larger bends |
| Thermal tuning | ● efficient | ● weaker | ● | ● | ● |
| Fast modulation | ● carrier depletion | ○ | ● Pockels | ● Pockels | ● electro-absorption, QCSE |
| Detection at 1310/1550 nm | ● germanium | ◐ | ◐ | ◐ via Si/Ge | ● InGaAs |
| Light generation and gain | ◐ III–V attached or bonded | ◐ | ◐ | ◐ | ● |
| CMOS-foundry manufacturing | ● | ● | ○ | ◐ | ○ |

## <span class="secnum">4.2</span>The materials

[Table 4.2](#tab-4-2) collects the material properties behind Table 4.1, and [Figure 4.1](#fig-4-1) shows where each material is transparent. The short-wavelength edge of transparency is set by the bandgap: a photon with more energy than the gap is absorbed, so the edge is at $$\lambda_g = hc/E_g = 1.24/E_g[\mathrm{eV}]$$ µm.

**Table 4.2. Photonic materials at 1550 nm.** Approximate room-temperature values; deposited and thin-film materials vary with process.
{: .tabcaption #tab-4-2 }

| Material | Index | Bandgap | Thermo-optic dn/dT | Electro-optic effect |
|---|---|---|---|---|
| Silicon | 3.48 | 1.12 eV, indirect | ≈ 1.8 × 10⁻⁴ /K | free-carrier plasma dispersion only {% include cite.html keys="soref1987" %} |
| Silica | 1.44 | ≈ 9 eV | ≈ 1 × 10⁻⁵ /K | none |
| Silicon nitride | ≈ 2.0 | ≈ 5 eV | ≈ 2.5 × 10⁻⁵ /K | none (stress-optic and thermal tuning) |
| Lithium niobate | 2.21 (o), 2.14 (e) | ≈ 4 eV | — | Pockels, r₃₃ ≈ 30 pm/V {% include cite.html keys="zhu2021" %} |
| Barium titanate | ≈ 2.3 | ≈ 3.2 eV | — | Pockels, hundreds of pm/V in thin films {% include cite.html keys="abel2019" %} |
| Indium phosphide | 3.17 | 1.34 eV, direct | — | weak Pockels; electro-absorption in quantum wells |
| Germanium | ≈ 4.3 | 0.66 eV indirect, 0.80 eV direct | — | Franz–Keldysh electro-absorption |

<figure id="fig-4-1">
  <img src="{{ '/assets/figs/ch04_windows.svg' | relative_url }}" style="width:720px" alt="Approximate transparency windows of photonic materials from their bandgap edges, with the O and C bands marked">
  <figcaption><span class="capnum">Figure 4.1.</span> <strong>Where the materials are transparent.</strong> Each bar starts at the bandgap edge \(\lambda_g = 1.24/E_g\) µm and continues into the mid-infrared (arrows); silica absorbs strongly beyond about 3.5 µm. Germanium's direct gap at 0.80 eV puts its edge right at the C band, which is why it detects there. Drawn by <code>figsrc/part1_figs.py</code>.</figcaption>
</figure>

Three properties decide most platform choices:

- **Index contrast** sets how tightly light is confined, and therefore how small waveguides and bends can be ([Figure 4.3](#fig-4-3)). Silicon against silica ($$\Delta n \approx 2$$) is at one extreme; InGaAsP against InP ($$\Delta n \approx 0.2$$ in the vertical direction) at the other, which is why InP waveguides are etched deeply to confine light sideways.
- **The electro-optic effect** decides how fast and efficiently a phase can be changed. Only non-centrosymmetric crystals (LiNbO₃, BaTiO₃, the III–Vs) have a Pockels effect, a change of index proportional to the applied field. Silicon must instead move free carriers, which changes both index and absorption.
- **The bandgap** decides absorption and gain. Light can only be generated efficiently in a direct-gap semiconductor, and detected in one whose gap is below the photon energy.

## <span class="secnum">4.3</span>Silicon-on-insulator

The standard silicon-photonics wafer is **SOI**: a crystalline silicon film on a buried oxide on a silicon handle wafer. The film is most often 220 nm thick, a value that grew out of early CMOS-compatible processes and is now the default of most foundry PDKs; 300–340 nm films are used for lower loss and easier coupling, and 3 µm films (VTT) for very low loss and polarisation-independent operation {% include cite.html keys="vttpdk" %}. The BOX is 2–3 µm thick, enough to keep the guided mode from leaking into the silicon handle at 1550 nm (thinner BOX is a problem at longer wavelengths, [Chapter 7]({% link chapters/07_loss.md %})).

A full silicon-photonics process adds partial etches for rib waveguides and grating couplers, implants for p–n junction modulators, germanium epitaxy for detectors, metal heaters and two or more metal layers, and sometimes a silicon nitride layer above the silicon. Its strengths are density (bends of a few micrometres), fast and mature modulators and detectors, and the volume and statistics of CMOS fabs. Its weaknesses are the ones listed in [Chapter 1]({% link chapters/01_why.md %}): no laser, propagation losses of 1–3 dB/cm in strip waveguides, two-photon absorption, and high sensitivity to temperature and to nanometre variations.

Silicon photonics is available through many foundries and MPW services, among them AMF, AIM Photonics, imec, GlobalFoundries, Tower Semiconductor, CORNERSTONE, VTT, and Applied Nanotools with SiEPICfab for electron-beam prototyping {% include cite.html keys="siew2021,openebl" %}. Their PDKs differ in film thickness, layers and rules; the open ones are listed in [Section 4.8](#tab-4-3).

## <span class="secnum">4.4</span>Silicon nitride

Silicon nitride (Si₃N₄) deposited by low-pressure chemical vapour deposition (LPCVD) has an index of about 2.0 and a bandgap of about 5 eV, so it is transparent from the visible to the mid-infrared and has neither two-photon absorption nor free-carrier absorption at telecom wavelengths {% include cite.html keys="blumenthal2018" %}. Its moderate index contrast with silica brings two benefits: sidewall roughness scatters less light, so propagation losses can be orders of magnitude below silicon's, and the modes are larger and less sensitive to fabrication. Very thin, weakly confining films (under 100 nm) reach losses below 0.1 dB/m at the cost of millimetre bends; thick films (around 800 nm) give tight confinement and the anomalous dispersion needed for frequency combs.

Silicon nitride also handles high optical powers and has a thermo-optic coefficient about seven times smaller than silicon's, which makes passive filters more stable. What it lacks is any fast modulation, detection or gain of its own. It is therefore used for low-loss routing, filters, delay lines, high-Q resonators for narrow-linewidth lasers ([Chapter 26]({% link chapters/26_tunable.md %})), visible-light photonics for biophotonics and quantum technologies, and as a second layer in silicon platforms. Dedicated SiN foundries include LioniX and Ligentec, and CORNERSTONE and several silicon foundries offer SiN layers.

## <span class="secnum">4.5</span>Thin-film lithium niobate

Lithium niobate has been the material of telecom modulators for decades because of its strong Pockels effect (r₃₃ ≈ 30 pm/V), but bulk LiNbO₃ waveguides made by diffusion are weakly confining and centimetres long. **Thin-film lithium niobate** (TFLN, or lithium niobate on insulator, LNOI) bonds a film a few hundred nanometres thick onto silica and etches ridge waveguides into it, gaining strong confinement and placing the electrodes micrometres from the light {% include cite.html keys="zhu2021" %}. The result is modulators with drive voltages compatible with CMOS electronics and electro-optic bandwidths beyond 100 GHz {% include cite.html keys="wang2018tfln" %}, low propagation loss, and strong second-order nonlinearity for frequency conversion.

TFLN has no detectors or gain of its own, and lithium is not welcome in CMOS fabs, so the material is processed in dedicated lines. Luxtelligence and HyperLight are among the foundries; Luxtelligence's PDK is open, and three of its devices appear in the [3D gallery]({% link devices-3d.md %}) {% include cite.html keys="lxtpdk" %}. Its typical waveguide is etched halfway into the film, so the ridge sits on a thin slab ([Figure 4.2](#fig-4-2)).

## <span class="secnum">4.6</span>Barium titanate

Barium titanate (BaTiO₃, BTO) is a ferroelectric perovskite with one of the largest known Pockels coefficients. Grown as an epitaxial film on silicon, it retains effective coefficients of hundreds of picometres per volt {% include cite.html keys="abel2019" %}, an order of magnitude more than lithium niobate. Because the film can be deposited on silicon wafers, BTO promises Pockels modulators and phase shifters inside a silicon-photonics process, with very low static power, which matters for large switching and computing meshes where thousands of thermal phase shifters would otherwise burn watts.

The integration is demanding: the film must be grown on a template layer and bonded, its crystal domains must be oriented for the field direction of the electrodes, and the effective coefficient depends on frequency and processing. Typical devices place a silicon or silicon nitride waveguide on or under a thin BTO film, so that part of the mode sees the BTO. BTO is earlier in its industrial development than the other platforms here, and no open PDK exists yet.

## <span class="secnum">4.7</span>Indium phosphide and other III–Vs

Indium phosphide and the alloys lattice-matched to it, InGaAsP and InGaAlAs, have direct bandgaps that can be tuned across the telecom bands. A single InP wafer can therefore carry lasers, semiconductor optical amplifiers, electro-absorption and Mach–Zehnder modulators, photodetectors and passive waveguides, all monolithically integrated {% include cite.html keys="coldren" %}. Generic InP foundry platforms, such as those at Fraunhofer HHI and SMART Photonics, offer these through MPW runs.

The price is in the passive parts. The vertical index contrast between an InGaAsP core and InP cladding is small, so waveguides are wide and deeply etched, bends are tens to hundreds of micrometres, propagation losses are a few dB/cm, and the substrates are small (75–100 mm) and expensive. This is why the dominant approach for high-volume products combines InP gain with silicon or silicon nitride circuits, by attaching, bonding or growing III–V material on silicon ([Chapter 27]({% link chapters/27_lasersonsi.md %})). Gallium arsenide plays the same role for quantum-dot lasers near 1310 nm and for shorter wavelengths, and germanium is the detector material of silicon photonics.

## <span class="secnum">4.8</span>Choosing and combining platforms

[Figure 4.2](#fig-4-2) draws typical waveguides of each platform at the same scale. The silicon strip is the smallest by far; the InP ridge is the largest, because its low vertical contrast forces a thick core.

<figure id="fig-4-2">
  <img src="{{ '/assets/figs/ch04_xsections.svg' | relative_url }}" style="width:760px" alt="Typical waveguide cross-sections of Si strip, Si rib, SiN, TFLN, BTO on Si and InP, drawn to the same scale">
  <figcaption><span class="capnum">Figure 4.2.</span> <strong>Typical waveguides, to scale.</strong> Silicon strip (500 × 220 nm) and rib (90 nm slab) on buried oxide; a moderately confining SiN waveguide; a TFLN ridge etched halfway into a 400 nm film; a schematic BTO-on-silicon waveguide (arrangements vary); and an InP deep ridge through a 0.5 µm InGaAsP core. Light blue is silica. Dimensions are representative, not those of a particular process. Drawn by <code>figsrc/part1_figs.py</code>.</figcaption>
</figure>

The contrast sets the size of the mode itself as well as that of the waveguide ([Figure 4.3](#fig-4-3)): no silicon-nitride, lithium-niobate or InP core, however thin or thick, squeezes the light as tightly as silicon in oxide.

<figure id="fig-4-3">
  <img src="{{ '/assets/figs/ch04_modesize.svg' | relative_url }}" style="width:640px" alt="(a) Mode width against core thickness on log axes for Si in SiO2, LiNbO3 in SiO2, Si3N4 in SiO2 and InGaAsP in InP, each with a minimum: 0.32, 0.64, 0.73 and 0.90 µm. (b) Vertical intensity profiles at the typical thicknesses of 220, 400, 400 and 500 nm, with widths of 0.33, 0.65, 0.73 and 0.90 µm">
  <figcaption><span class="capnum">Figure 4.3.</span> <strong>Index contrast sets the mode size.</strong> (a) Width of the fundamental TE mode (1/e² of the intensity) of slab waveguides at 1550 nm against core thickness, for the material pairs of Figure 4.2 (lithium niobate with its extraordinary index); dotted where the slab guides a second mode. Every curve has a minimum, 0.32 µm for silicon in oxide and 0.64–0.90 µm for the others, which scales as \(\lambda/\mathrm{NA}\) with \(\mathrm{NA} = \sqrt{n_1^2 - n_2^2}\); thinner cores only push the light out into the cladding. (b) The intensity profiles at the typical thicknesses (dots in a), to one scale: the field's tail reaches 101 nm into the cladding for silicon, 253 nm for SiN and 311 nm for InGaAsP in InP. Exact slab solutions. Drawn by <code>figsrc/ch04_figs.py</code>.</figcaption>
</figure>

**Try it.** Compare any two platforms: their cross-sections, typical loss and bend radius, index contrast and native capabilities.

{% include demos/platforms.html %}

When no single platform does everything, the chip combines them. The vocabulary is worth fixing early:

- **Monolithic** integration builds every function in one material and process: an InP PIC with lasers, or a silicon PIC with germanium detectors.
- **Hybrid** integration assembles finished chips: a laser die flip-chipped or butt-coupled to a silicon chip, or attached through micro-optics.
- **Heterogeneous** integration bonds unprocessed material, such as an InP die or wafer, onto a patterned silicon wafer and then processes it there with wafer-scale lithography, so that the III–V devices are aligned to the silicon circuits lithographically {% include cite.html keys="komljenovic2016" %}.
- **Micro-transfer printing** sits between the two: finished micro-devices are picked from their source wafer and printed onto the target wafer in parallel.

[Chapter 27]({% link chapters/27_lasersonsi.md %}) compares these for lasers. Silicon nitride layers in silicon processes, TFLN bonded onto silicon, and BTO grown on silicon are all heterogeneous combinations of the same kind ([Figure 4.4](#fig-4-4)).

<figure id="fig-4-4">
  <img src="{{ '/assets/figs/ch04_combined.svg' | relative_url }}" style="width:640px" alt="Cross-section of one silicon-on-insulator wafer carrying four materials, to scale: a silicon nitride waveguide 200 nm above a narrow silicon tip, a silicon nitride waveguide alone, a lithium niobate film bonded over a silicon nitride waveguide with two metal electrodes 5 µm apart, and an InP stack with quantum wells bonded over a silicon waveguide in an opening of the oxide, with n and p contacts">
  <figcaption><span class="capnum">Figure 4.4.</span> <strong>Several materials on one silicon wafer.</strong> A representative heterogeneous stack, to scale: a silicon nitride layer 200 nm above the 220 nm silicon, coupled to it where a narrow silicon tip runs under a SiN waveguide; a SiN waveguide on its own; a lithium niobate film bonded onto the planarised oxide over a SiN waveguide, with electrodes 5 µm apart for a Pockels phase shifter; and an InP stack with quantum wells bonded onto a silicon waveguide through a thin layer, in an opening of the oxide (Chapter 27). Dimensions are representative, not those of a particular process, and the devices sit far apart on a real chip. Drawn by <code>figsrc/ch04_figs.py</code>.</figcaption>
</figure>

### Open PDKs used in this tutorial

Process design kits ([Chapter 30]({% link chapters/30_flow.md %})) are usually under non-disclosure agreements. A few are open source, and this tutorial uses only those for its layouts, labs and 3D models.

**Table 4.3. Open photonic PDKs used in this tutorial.** All MIT-licensed; see [Appendix D]({% link appendices/d_tools.md %}) for links.
{: .tabcaption #tab-4-3 }

| PDK | Platform | Used for |
|---|---|---|
| SiEPIC EBeam PDK {% include cite.html keys="ebeampdk" %} and its gdsfactory version, ubcpdk {% include cite.html keys="ubcpdk" %} | 220 nm SOI (and SiN), electron-beam lithography, openEBL runs | the labs' first chip, 3D models, measured data |
| CORNERSTONE, via cspdk {% include cite.html keys="cspdk" %} | 220 and 340 nm SOI, SiN, Ge-on-Si | 3D models, cross-platform comparisons |
| Luxtelligence LNOI400, via lnoi400 {% include cite.html keys="lxtpdk" %} | thin-film lithium niobate | 3D models, modulator examples |
| VTT, via gvtt {% include cite.html keys="vttpdk" %} | 3 µm thick SOI | thick-SOI examples |

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Choose the platform from the function that is hardest to get. If you need density and volume, start in silicon and bring in the laser. If you need the lowest loss or visible wavelengths, SiN. If you need the fastest, most linear modulator, TFLN, or BTO where it is available. If you need gain everywhere, InP. For the reference link, silicon carries the modulators, filters and detectors, and the laser comes from III–V material ([Chapter 27]({% link chapters/27_lasersonsi.md %})).

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Silicon photonics in 220 nm SOI, with germanium photodetectors, carrier-depletion ring modulators and metal heaters, and four III–V lasers brought in from outside the silicon. The passive devices of the labs' first chip use the same 220 nm platform.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: waveguide materials](https://s3.amazonaws.com/fip-1/Materials/index.html) and [wavelength selection](https://s3.amazonaws.com/fip-1/Wavelength/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="siew2021,blumenthal2018,zhu2021,abel2019,komljenovic2016,shekhar2024,coldren" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A platform must guide, tune, modulate, detect, generate and amplify light; none does all six natively.
- Silicon: highest contrast and CMOS volume, no laser or Pockels effect. SiN: lowest loss and widest transparency, no fast modulation or detection. TFLN and BTO: strong Pockels modulation. InP: everything including gain, with larger, lossier passives on small wafers.
- The bandgap sets the short-wavelength transparency edge, $$\lambda_g = 1.24/E_g$$ µm; germanium's direct gap at 0.80 eV puts its edge at the C band.
- Monolithic, hybrid, heterogeneous and transfer-printed integration combine platforms; most modern transceivers are silicon with attached or bonded III–V lasers.
- This tutorial uses only open PDKs: SiEPIC EBeam, CORNERSTONE, Luxtelligence and VTT.

</div>

## Check yourself

{% include quiz.html %}
