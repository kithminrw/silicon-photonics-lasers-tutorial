---
title: "6. Channel Waveguides on SOI and Beyond"
parent: "Part II · Waveguides"
nav_order: 6
permalink: /part-2/ch06/
chapter: 6
---

# <span class="chapnum">Chapter 6</span>Channel Waveguides on SOI and Beyond

Real waveguides confine light in two dimensions, and their cross-section is the first design decision on every photonic chip.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe strip, rib, slot and subwavelength-grating waveguides;
- apply the effective-index method, and know where it fails;
- run a numerical mode solver and read its output;
- quote the effective index, group index and single-mode width of standard SOI waveguides at 1310 and 1550 nm;
- compare waveguide cross-sections on SiN, TFLN, thick SOI and InP, and estimate how fabrication errors shift them.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which width and etch depth give single-mode, low-loss, compact routing?

</div>

## <span class="secnum">6.1</span>Geometries

Four cross-sections cover most silicon photonics (drawn to scale in [Figure 6.2](#fig-6-2)):

- **Strip** (or wire): the silicon film etched through to the oxide, typically 500 × 220 nm at 1550 nm. Strongest confinement, tightest bends (a few micrometres), highest scattering loss.
- **Rib** (or ridge): a partial etch leaves a thin slab beside the waveguide, for example 90 nm of a 220 nm film. Lower lateral contrast, so the mode spreads, scatters less and tolerates width errors better, but bends must be larger. The slab also gives electrical access to the waveguide, which is why modulators and detectors use ribs ([Chapters 19–21]({% link chapters/19_eo.md %})).
- **Slot**: two silicon rails with a narrow gap. For the mode polarised across the gap, the normal component of $$\mathbf{D}$$ is continuous, so $$\mathbf{E}$$ jumps by $$n_\mathrm{Si}^2/n_\mathrm{gap}^2$$ and concentrates in the low-index slot ([Figure 6.4d](#fig-6-4)): useful for sensing and for nonlinear or electro-optic claddings.
- **Subwavelength grating (SWG)**: silicon segments with a period well below the Bragg period, which act as an artificial material whose index is set by the fill factor. Used for mode shaping, broadband couplers and sensors.

## <span class="secnum">6.2</span>The effective-index method

A rectangular waveguide has no closed-form modes, but it can be approximated by two slab problems ([Chapter 5]({% link chapters/05_slab.md %})):

1. **Vertical slabs.** Solve the slab of the core region (thickness $$t$$) for its effective index $$n_\mathrm{I}$$, and the slab of the region beside it (the remaining slab $$s$$ of a rib, or just cladding for a strip) for $$n_\mathrm{II}$$.
2. **Lateral slab.** Solve a slab of width $$W$$ with core index $$n_\mathrm{I}$$ and cladding index $$n_\mathrm{II}$$. For a TE-like mode, whose electric field is horizontal, the field is normal to the lateral interfaces, so this second slab uses the **TM** boundary conditions; for a TM-like mode, the reverse.

The result is the **effective-index method (EIM)**, worked through for a rib in [Figure 6.3](#fig-6-3). It is fast, intuitive and surprisingly good for ribs and wide guides. For small, high-contrast strips it overestimates the effective index and underestimates the single-mode width, because it assumes the field separates into a vertical and a lateral profile, which is not true in the corners, and because the lateral slab it builds (core index 2.85 against oxide) has more contrast than the real strip. For 500 × 220 nm at 1550 nm it gives $$n_\mathrm{eff} = 2.49$$ and a TE1 cut-off at about 320 nm, against 2.446 and about 450 nm from a full solver.

**Try it.** Change the width, thickness, etch depth and wavelength; the cross-section shows the waveguide to scale with its mode.

{% include demos/eim.html %}

## <span class="secnum">6.3</span>Numerical mode solvers

For design you solve the full vectorial wave equation on the cross-section numerically. **Finite-difference eigenmode** (FDE) solvers discretise the cross-section on a grid; **finite-element** solvers use a mesh that follows the interfaces. Both return each mode's effective index, field and polarisation. The open-source finite-element solver femwell is used for the numbers in this chapter {% include cite.html keys="gdsfactory" %}; MPB, and the eigenmode solvers built into commercial tools, do the same job.

Three habits make a mode solver trustworthy:

- **Converge the mesh.** Refine until the effective index stops changing in the fourth decimal; the field near the silicon corners needs the finest mesh.
- **Make the domain large enough.** The evanescent tails must decay before the boundary, or the boundary perturbs the mode; leaky modes need absorbing (PML) boundaries.
- **Include dispersion.** Use wavelength-dependent indices, and compute the group index from effective indices at neighbouring wavelengths, $$n_g = n_\mathrm{eff} - \lambda\,\Delta n_\mathrm{eff}/\Delta\lambda$$.

## <span class="secnum">6.4</span>Effective and group index of SOI waveguides

[Figure 6.1](#fig-6-1) shows the modes of 220 nm silicon strips in oxide against width, computed with femwell, and [Table 6.1](#tab-6-1) collects the numbers for the standard waveguides.

<figure id="fig-6-1">
  <img src="{{ '/assets/figs/ch06_strip.svg' | relative_url }}" style="width:720px" alt="Effective index of TE0, TM0, TE1 and TM1 modes and group index of TE0 and TM0 against width for 220 nm silicon strips">
  <figcaption><span class="capnum">Figure 6.1.</span> <strong>220 nm silicon strips in oxide, full-vectorial (femwell).</strong> (a) Effective index at 1550 nm against width; TE1 is guided above about 450 nm. (b) Group index of TE0 and TM0 at 1550 nm and of TE0 at 1310 nm; the TE group index peaks near 4.4 for widths of 350–400 nm and falls slowly for wider strips. Drawn by <code>figsrc/part2_figs.py</code> from <code>figsrc/ch06_sweep.py</code>.</figcaption>
</figure>

**Table 6.1. Standard SOI waveguides (220 nm silicon in oxide).** Full-vectorial femwell results.
{: .tabcaption #tab-6-1 }

| Waveguide | Wavelength | Mode | n_eff | n_g |
|---|---|---|---|---|
| Strip 500 nm | 1550 nm | TE0 | 2.446 | 4.18 |
| Strip 500 nm | 1550 nm | TM0 | 1.771 | 3.74 |
| Strip 500 nm | 1310 nm | TE0 | 2.712 | 4.16 |
| Strip 500 nm | 1310 nm | TM0 | 2.165 | 4.67 |
| Rib 500 nm, 90 nm slab | 1550 nm | TE0 | 2.568 | 3.89 |

The strip and the rib of the table are drawn to scale in [Figure 6.2](#fig-6-2), with the slot and the subwavelength grating of Section 6.1. [Figure 6.3](#fig-6-3) applies the effective-index method of Section 6.2 to the rib.

<figure id="fig-6-2">
  <img src="{{ '/assets/figs/ch06_geometries.svg' | relative_url }}" style="width:600px" alt="Four drawings to scale: a 500 by 220 nanometre silicon strip on oxide, a rib with a 90 nanometre slab, a slot waveguide of two 250 nanometre rails with a 100 nanometre gap, and a top view of a subwavelength grating of 100 nanometre segments with a 200 nanometre period">
  <figcaption><span class="capnum">Figure 6.2.</span> <strong>The silicon waveguide geometries of Section 6.1, to scale.</strong> (a) The 500 × 220 nm strip, etched through to the buried oxide. (b) The rib: the same ridge with a 90 nm slab left beside it. (c) A slot waveguide: two 250 nm rails with a 100 nm gap. (d) A subwavelength grating in top view: 100 nm silicon segments with a 200 nm period, fed by a strip. The period is well below the Bragg period, which is at least 317 nm here (\(\lambda/2n_\mathrm{eff}\) of the solid strip). Slot and grating dimensions are illustrative. Drawn by <code>figsrc/ch06_figs.py</code>.</figcaption>
</figure>

<figure id="fig-6-3">
  <img src="{{ '/assets/figs/ch06_eim.svg' | relative_url }}" style="width:600px" alt="The rib cross-section split into region I under the ridge and region II beside it; the vertical slab fields of the two regions with indices 2.848 and 2.103; and the lateral slab between them with its field and effective index 2.600">
  <figcaption><span class="capnum">Figure 6.3.</span> <strong>The effective-index method, step by step</strong>, for the rib of Table 6.1 (TE-like mode, 1550 nm). (a) The cross-section, to scale, is split into region I under the ridge and region II beside it. (b) Step 1: each region is solved as a vertical slab, giving \(n_\mathrm{I} = 2.848\) and \(n_\mathrm{II} = 2.103\). (c) Step 2: a lateral slab of width 500 nm with core index \(n_\mathrm{I}\) and cladding \(n_\mathrm{II}\) (dashed), solved with TM boundary conditions because the TE-like mode's electric field is normal to the sidewalls, gives \(n_\mathrm{eff} = 2.600\), against 2.568 from femwell. For the strip (\(n_\mathrm{II} = 1.444\)) the same steps give 2.491 against 2.446. Drawn by <code>figsrc/ch06_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 6.1 · What the group index buys you</div>

The 500 × 220 nm strip has $$n_\mathrm{eff} = 2.446$$ but $$n_g = 4.18$$ at 1550 nm. Light takes $$n_gL/c = 4.18 \times 1\ \mathrm{cm}/c = 139$$ ps to cross a centimetre, and an interferometer with an arm-length difference $$\Delta L$$ has a free spectral range $$\lambda^2/(n_g\Delta L)$$: 100 µm gives $$1.55^2/(4.18 \times 100) = 5.7$$ nm ([Chapter 11]({% link chapters/11_mzi.md %})). Using $$n_\mathrm{eff}$$ by mistake would predict 9.8 nm, a 70 % error. Whenever a spectrum's period matters, use the group index.

</div>

## <span class="secnum">6.5</span>Single-mode conditions and polarisation

A 220 nm film is single-mode vertically at 1550 nm ([Chapter 5]({% link chapters/05_slab.md %})), so the strip's higher-order modes are lateral. At 1550 nm the second TE mode (TE1) appears at a width of about 450 nm; at 500 nm it is guided but weakly ($$n_\mathrm{eff} = 1.49$$, barely above the oxide), and it is stripped by the first bend. That is why 500 nm is the usual compromise: wide enough for low scattering loss and a little tolerance, narrow enough to be effectively single-mode. At 1310 nm the same arguments give widths of about 350–400 nm.

The TE and TM modes have very different effective indices (2.45 and 1.77 at 500 nm), so the strip is strongly **birefringent** ([Figure 6.4](#fig-6-4)): TE and TM light see different phases, couplers and resonances, and grating couplers are designed for one polarisation only ([Chapter 15]({% link chapters/15_gc.md %})). Where a TE and a TM mode would have equal indices, for example near widths where the curves of Figure 6.1 cross for other film thicknesses or in asymmetric claddings, they **hybridise** into mixed modes; polarisation rotators exploit exactly this ([Chapter 14]({% link chapters/14_wdm.md %})).

<figure id="fig-6-4">
  <img src="{{ '/assets/figs/ch06_fields.svg' | relative_url }}" style="width:600px" alt="Four intensity maps to scale: the TE0 mode of the 500 by 220 nanometre strip filling the core, its TM0 mode lying mostly in the oxide just above and below it, the rib's TE0 mode spreading into the slab, and the slot's TE0 mode concentrated in the 100 nanometre gap">
  <figcaption><span class="capnum">Figure 6.4.</span> <strong>Full-vectorial mode fields at 1550 nm</strong> (femwell), \(|E|^2\) on one colour scale, silicon outlined, to scale. (a) The 500 × 220 nm strip's TE0 (\(n_\mathrm{eff} = 2.446\)) fills the core; its main field \(E_x\) is normal to the sidewalls and jumps up just outside them. (b) Its TM0 (1.771): the main field \(E_y\) is normal to the top and bottom faces, jumps there by \((n_\mathrm{Si}/n_\mathrm{ox})^2\), and much of the mode lies in the oxide just above and below the core. (c) The rib of Table 6.1 (2.568): the mode spreads sideways into the 90 nm slab. (d) The slot of Figure 6.2 (1.844): \(E_x\) in the 100 nm gap is three times its largest value inside the rails. In the strip, \(|E_z|\) reaches about half of the peak field: neither mode is purely transverse. Drawn by <code>figsrc/ch06_figs.py</code> from <code>figsrc/ch06_fields.py</code> (a coarse mesh; the strip and rib indices agree with Table 6.1).</figcaption>
</figure>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Route with 500 × 220 nm strips (TE, 1550 nm): $$n_\mathrm{eff} = 2.446$$, $$n_g = 4.18$$. Use the group index for every free spectral range and delay in Part III.

</div>

## <span class="secnum">6.6</span>Other platforms

The same tools apply to every platform; only the numbers change ([Chapter 4]({% link chapters/04_platforms.md %}), Figure 4.2):

- **Silicon nitride.** With $$n \approx 2.0$$, single-mode SiN strips are around 1 µm wide and 300–800 nm thick; a 1.2 × 0.4 µm guide has an effective index of about 1.67 and an evanescent tail of about 300 nm, three times longer than silicon's.
- **Thick SOI.** In 3 µm silicon, rib waveguides of a few micrometres are single-mode because their shallow etch makes the higher-order lateral modes leak into the slab; the mode is large, fibre-friendly and almost polarisation-independent {% include cite.html keys="vttpdk" %}.
- **Thin-film lithium niobate.** Ridges etched halfway into a 300–600 nm film guide modes that overlap the electro-optic film strongly; the crystal's birefringence makes TE and TM very different, and the crystal cut sets which one sees $$r_{33}$$ ([Chapter 19]({% link chapters/19_eo.md %})).
- **InP.** The small vertical contrast of InGaAsP on InP needs a thick core and deep etching for lateral confinement; the mode is micrometres across.

## <span class="secnum">6.7</span>Sensitivity to fabrication

Strong confinement makes silicon waveguides sensitive to their dimensions. For the 500 × 220 nm strip at 1550 nm, femwell gives $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}W = 1.6\times10^{-3}$$ per nanometre of width and $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}t = 3.7\times10^{-3}$$ per nanometre of film thickness ([Figure 6.5](#fig-6-5)). A resonator's wavelength shifts as $$\Delta\lambda/\lambda = \Delta n_\mathrm{eff}/n_g$$, so a 1 nm width error moves a ring resonance at 1550 nm by $$1550 \times 1.6\times10^{-3}/4.18 = 0.6$$ nm, and a 1 nm thickness error by 1.4 nm. Wafers vary by several nanometres in thickness and lithography by several in width, which is why identical rings across a die land at different wavelengths and why every resonator needs tuning ([Chapters 18 and 29]({% link chapters/29_fab.md %})).

<figure id="fig-6-5">
  <img src="{{ '/assets/figs/ch06_sensitivity.svg' | relative_url }}" style="width:600px" alt="Two plots against strip width from 0.25 to 1 micrometre: the change of effective index per nanometre of width falls steeply for TE and slowly for TM while the change per nanometre of thickness stays near 3.4 to 3.7 times 10 to the minus 3; and the corresponding ring resonance shift per nanometre, 0.60 nm for width and 1.37 nm for thickness at 500 nm">
  <figcaption><span class="capnum">Figure 6.5.</span> <strong>Fabrication sensitivity of 220 nm silicon strips at 1550 nm.</strong> (a) Change of effective index per nanometre of width, from the femwell sweep of Figure 6.1 (TE0 \(1.6\times10^{-3}\) at 500 nm, TM0 \(0.7\times10^{-3}\)), and per nanometre of film thickness (TE0: femwell \(3.7\times10^{-3}\) at 500 nm; dashed, the trend from the effective-index method, which reads about 7 % lower). (b) The resulting shift of a ring resonance, \(\lambda\,\Delta n_\mathrm{eff}/n_g\), for TE0: 0.60 nm per nm of width and 1.37 nm per nm of thickness at 500 nm. Wider strips hardly notice width errors (0.09 nm per nm at 1 µm), but their thickness sensitivity stays. Drawn by <code>figsrc/ch06_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

Wider waveguides are less sensitive to width errors (the curve flattens), lose less to scattering and keep their mode away from the sidewalls; narrow ones bend more tightly. A common recipe is to route bends and couplers in 500 nm strips and long straight sections in 1–3 µm strips connected by adiabatic tapers ([Chapter 8]({% link chapters/08_bends.md %})).

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [mustafa.sh: browser waveguide mode solver](https://mustafa.sh/tools/waveguide-mode-solver) {% include cite.html keys="mustafash" %}
- [VM-Lab: core width and height](https://s3.amazonaws.com/fip-1/Geometry-1/index.html) and [higher-order modes](https://s3.amazonaws.com/fip-1/Polarization/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="chrostowski2015,okamoto,gdsfactory,cspdk,vttpdk" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Strips confine most and bend tightest; ribs scatter less, tolerate errors and give electrical access; slots and SWGs engineer where the field sits.
- The effective-index method solves two slabs (with swapped polarisation in the second); it overestimates n_eff for small high-contrast strips but captures the trends.
- 500 × 220 nm silicon at 1550 nm: TE0 n_eff = 2.446, n_g = 4.18; TM0 n_eff = 1.771; TE1 appears near 450 nm width.
- Use the group index, not the effective index, for free spectral ranges and delays.
- A 1 nm width error shifts a silicon resonance by about 0.6 nm; a 1 nm thickness error by about 1.4 nm.

</div>
