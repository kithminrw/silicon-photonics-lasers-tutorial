---
title: "12. Ring Resonators"
parent: "Part III · Passive Devices"
nav_order: 12
permalink: /part-3/ch12/
chapter: 12
---

# <span class="chapnum">Chapter 12</span>Ring Resonators

Loop a waveguide back on itself and you get a filter, a sensor, a modulator or a laser mirror, depending on what you do with it.
{: .chapterlead }

<p><span class="status status-outline">outline</span> This chapter is an outline: the sections, demos and reading are planned, and the text is still to be written.</p>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the all-pass and add-drop transfer functions;
- define FSR, finesse, loaded and intrinsic Q and extinction ratio;
- explain under-, critical and over-coupling;
- extract loss and coupling from a measured resonance;
- explain split resonances and thermal drift, and list the applications of rings.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do coupling and loss shape a ring's resonance?

</div>

## <span class="secnum">12.1</span>Resonance condition

mλ = n_eff L, and the FSR.

## <span class="secnum">12.2</span>The all-pass ring

Self-coupling t, round-trip amplitude a; under-, critical and over-coupling.

**Try it.** Ring resonator: radius, coupling and loss; all-pass or add-drop; Q, FSR and extinction, and the build-up inside the ring.

{% include demos/ring.html %}

## <span class="secnum">12.3</span>The add-drop ring

The drop port and its bandwidth.

## <span class="secnum">12.4</span>Quality factor and finesse

Loaded, intrinsic and coupling Q, photon lifetime and field build-up.

## <span class="secnum">12.5</span>Extracting parameters from measurements

Lorentzian fits and the t ↔ a ambiguity (Chapter 32).

## <span class="secnum">12.6</span>Non-idealities

Backscattering and split resonances, thermal drift (about 80 pm/K in Si), dispersion.

## <span class="secnum">12.7</span>Applications

WDM filters, sensors, modulators and Vernier pairs.

## Interactive demos

- **Ring resonator**: radius, coupling and loss; all-pass or add-drop; Q, FSR and extinction, and the build-up inside the ring. *(built, shown above)*

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter (they open on their authors' sites):

- [VM-Lab: ring resonator wavelength](https://s3.amazonaws.com/fip-6/Wavelength/index.html)
- [VM-Lab: ring coupling gap](https://s3.amazonaws.com/fip-6/Coupling-Gap/index.html)
- [VM-Lab: all-pass ring](https://s3.amazonaws.com/fip-6/All-Pass-Ring/index.html)
- [mustafa.sh: ring resonator designer](https://mustafa.sh/tools/ring-resonator-simulator)

</div>

## Reading

{% include reflist.html keys="bogaerts2012,chrostowski2015,shi2012" %}
