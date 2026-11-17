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

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain the Y-branch and why a combiner fed from one arm passes only half the power;
- explain mode excitation at an abrupt junction and the snaking of an offset input;
- derive the MMI self-imaging lengths;
- design 1 × 2 and 2 × 2 MMIs and estimate their bandwidth and tolerance;
- choose between directional couplers, Y-branches and MMIs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Y-branch or MMI, and how long must the MMI be?

</div>

## <span class="secnum">10.1</span>Y-branches

Adiabatic splitting, the combiner paradox and the optimised compact Y-junction of the SiEPIC EBeam PDK {% include cite.html keys="zhang2013" %}.

## <span class="secnum">10.2</span>Mode excitation at an abrupt junction

Overlap integrals, even and odd modes, offset inputs.

## <span class="secnum">10.3</span>Self-imaging in a multimode waveguide

The beat length L_π, general, paired and symmetric interference.

**Try it.** MMI self-imaging: change the width, length and input offset and watch the interference pattern form images.

{% include demos/mmi.html %}

## <span class="secnum">10.4</span>MMI design

1 × 2 and 2 × 2 MMIs, access tapers, tolerances and bandwidth.

## <span class="secnum">10.5</span>Comparing splitters

Loss, imbalance, bandwidth and footprint of DC, Y-branch and MMI.

## Interactive demos

- **MMI self-imaging**: change the width, length and input offset and watch the interference pattern form images. *(built, shown above)*

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter (they open on their authors' sites):

- [VM-Lab: Y-branch splitter](https://s3.amazonaws.com/fip-4/Splitter/index.html)
- [VM-Lab: Y-branch combiner](https://s3.amazonaws.com/fip-4/Combiner/index.html)
- [VM-Lab: waveguide interfaces (mode excitation)](https://s3.amazonaws.com/fip-1/Interfaces/index.html)
- [VM-Lab: MMI geometry](https://s3.amazonaws.com/fip-9/Geometry/index.html)
- [VM-Lab: MMI wavelength and polarisation](https://s3.amazonaws.com/fip-9/Wavelength-and-Polarization/index.html)

</div>

## Reading

{% include reflist.html keys="soldano1995,zhang2013" %}
