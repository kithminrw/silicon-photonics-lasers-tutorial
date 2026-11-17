---
title: "11. Mach–Zehnder Interferometers"
parent: "Part III · Passive Devices"
nav_order: 11
permalink: /part-3/ch11/
chapter: 11
---

# <span class="chapnum">Chapter 11</span>Mach–Zehnder Interferometers

Split, delay, recombine: the Mach–Zehnder interferometer turns a phase difference into a change of intensity, and it is everywhere in photonics.
{: .chapterlead }

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the transfer function of balanced and unbalanced MZIs;
- relate the free spectral range to the group index and arm-length difference;
- find the extinction ratio for non-ideal splitters;
- describe tunable MZI switches and lattice filters;
- use an MZI to measure group index.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How does the arm-length difference set the spectrum?

</div>

## <span class="secnum">11.1</span>Interference and optical phase

φ = 2πn_eff L/λ, superposition, constructive and destructive interference.

## <span class="secnum">11.2</span>The MZI transfer function

Ideal and non-ideal splitters; extinction ratio.

## <span class="secnum">11.3</span>Unbalanced MZIs

FSR = λ²/(n_g ΔL); filters.

**Try it.** Mach–Zehnder interferometer: set the arm-length difference, splitter ratio, loss and phase bias and read FSR and extinction.

{% include demos/mzi.html %}

## <span class="secnum">11.4</span>Tuning

Thermal and electro-optic phase shifters (Part V) and switches.

## <span class="secnum">11.5</span>Cascaded and lattice filters

Higher-order and flat-top responses, interleavers.

## <span class="secnum">11.6</span>MZIs as test structures

Extracting n_g and loss from measured spectra.

## Interactive demos

- **Mach–Zehnder interferometer**: set the arm-length difference, splitter ratio, loss and phase bias and read FSR and extinction. *(built, shown above)*

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter (they open on their authors' sites):

- [VM-Lab: MZI arm length](https://s3.amazonaws.com/fip-5a/Length/index.html)
- [VM-Lab: MZI wavelength](https://s3.amazonaws.com/fip-5a/Wavelength/index.html)
- [VM-Lab: MZI temperature](https://s3.amazonaws.com/fip-5b/Temperature/index.html)

</div>

## Reading

{% include reflist.html keys="chrostowski2015" %}
