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

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe strip, rib, slot and subwavelength-grating waveguides;
- apply the effective-index method, and know when it fails;
- run a numerical mode solver and read its output;
- compute n_eff and n_g against width and wavelength, and the single-mode width for 1310 and 1550 nm;
- compare waveguide cross-sections on SiN, TFLN, thick SOI and InP.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which width and etch depth give single-mode, low-loss, compact routing?

</div>

## <span class="secnum">6.1</span>Geometries

Strip, rib (partial etch), slot and subwavelength-grating (SWG) waveguides.

## <span class="secnum">6.2</span>The effective-index method

Two slab problems in place of one 2D problem.

## <span class="secnum">6.3</span>Numerical mode solvers

Finite-difference and finite-element eigenmode solvers, boundaries and convergence; open tools such as femwell and MPB.

## <span class="secnum">6.4</span>Effective and group index of SOI waveguides

n_eff and n_g against width at 1310 and 1550 nm; typical values for 500 × 220 nm.

## <span class="secnum">6.5</span>Single-mode conditions and polarisation

TE0, TM0 and TE1 cut-offs, birefringence and mode hybridisation.

## <span class="secnum">6.6</span>Other platforms

SiN, TFLN ridges, VTT's 3 µm SOI ribs and InP deep ridges: mode sizes and bend radii compared.

## <span class="secnum">6.7</span>Sensitivity to fabrication

dn_eff/dw and dn_eff/dt, and why ±10 nm matters (Chapter 29).

## Interactive demos

- **Effective-index explorer**: n_eff and n_g against width with a single-mode map, for strip and rib waveguides. *(planned)*
- **2D mode solver**: a finite-difference solver that runs in the browser. *(planned)*

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter (they open on their authors' sites):

- [VM-Lab: core width and height (fundamental TE mode)](https://s3.amazonaws.com/fip-1/Geometry-1/index.html)
- [VM-Lab: higher-order modes](https://s3.amazonaws.com/fip-1/Polarization/index.html)
- [mustafa.sh: browser waveguide mode solver](https://mustafa.sh/tools/waveguide-mode-solver)

</div>

## Reading

{% include reflist.html keys="chrostowski2015,okamoto,cspdk,vttpdk" %}
