---
title: Home
layout: default
nav_order: 0
permalink: /
---

<div class="hero">
  <div class="hero-text">
    <p class="eyebrow">Open-Photonics · Si · SiN · TFLN · BTO · InP</p>
    <h1>Silicon Photonics and Lasers, from Waveguides to Tested Chips</h1>
    <p class="fs-5">An open, interactive tutorial on integrated photonics: electromagnetic theory and Gaussian beams, waveguides on SOI, passive devices, coupling to fibre, modulators and detectors, lasers from first principles to lasers on silicon, and the fabrication, testing and data analysis that turn a layout into a working chip.</p>
    <p>
      <a class="btn btn-primary mr-2" href="{% link preface.md %}">Start reading</a>
      <a class="btn mr-2" href="{% link course-map.md %}">See the course map</a>
      <a class="btn mr-2" href="{% link devices-3d.md %}">PDK devices in 3D</a>
      <a class="btn" href="https://github.com/kithminrw/silicon-photonics-lasers-tutorial">Source on GitHub</a>
    </p>
  </div>
</div>

<div class="key-numbers">
  <div><b>220 nm</b><span>the standard SOI film</span></div>
  <div><b>3.48 / 1.44</b><span>index of Si and SiO₂ at 1550 nm</span></div>
  <div><b>1310 · 1550</b><span>O and C bands (nm)</span></div>
  <div><b>127 µm</b><span>fibre-array pitch</span></div>
  <div><b>34</b><span>chapters in eight parts</span></div>
</div>

A photonic integrated circuit does with light what an electronic chip does with charge: it generates, routes, filters, modulates and detects signals, on a wafer, in volume. This tutorial builds that picture from the ground up. Every concept follows the same pattern: a short derivation, a worked example with real numbers, an interactive demo you can play with, and a *what this means for your design* box. Where the open process design kits allow it, you can turn the real device over in 3D.

<figure class="chain-figure">
  <img src="{{ '/assets/figs/pic-chain.svg' | relative_url }}" alt="The building blocks of a photonic link, from laser to photodetector, with the chapters that cover each">
  <figcaption>The blocks of a photonic link and the chapters that cover each. The reference link of Chapters 1 and 33 is a four-wavelength version of this chain.</figcaption>
</figure>

## What is inside

<div class="card-grid">
  <div class="card"><span class="card-label">Part I · Ch 1–4 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-1.md %}">Foundations</a></h3><p>Why integrated photonics, electromagnetic theory, Gaussian beams and fibres, and the Si, SiN, TFLN, BTO and InP platforms.</p></div>
  <div class="card"><span class="card-label">Part II · Ch 5–8 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-2.md %}">Waveguides</a></h3><p>Slab and channel waveguides on SOI and other platforms, loss and dispersion, bends, tapers and transitions.</p></div>
  <div class="card"><span class="card-label">Part III · Ch 9–14 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-3.md %}">Passive devices</a></h3><p>Directional couplers, Y-branches and MMIs, Mach–Zehnder interferometers, rings, Bragg gratings, WDM and polarisation devices.</p></div>
  <div class="card"><span class="card-label">Part IV · Ch 15–17 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-4.md %}">Coupling and packaging</a></h3><p>Grating and edge couplers, fibre arrays, photonic wire bonds and packaging.</p></div>
  <div class="card"><span class="card-label">Part V · Ch 18–21 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-5.md %}">Active devices</a></h3><p>Thermo-optic tuning, electro-optic effects in each platform, modulators, photodetectors and receivers.</p></div>
  <div class="card"><span class="card-label">Part VI · Ch 22–28 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-6.md %}">Lasers and amplifiers</a></h3><p>Gain from first principles, the Fabry–Pérot laser and its rate equations, noise and linewidth, tunable lasers, lasers on silicon and SOAs.</p></div>
  <div class="card"><span class="card-label">Part VII · Ch 29–32 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-7.md %}">Fabrication, testing and data</a></h3><p>Fabrication and its variations, the design flow and open PDKs, test setups and data analysis.</p></div>
  <div class="card"><span class="card-label">Part VIII · Ch 33–34 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-8.md %}">Systems and applications</a></h3><p>Optical links and transceivers, and the sensing, LiDAR, quantum and computing systems built from the same blocks.</p></div>
  <div class="card"><span class="card-label">Labs · 12 <span class="status status-outline">planned</span></span><h3><a href="{% link labs.md %}">Hands-on labs</a></h3><p>Simulate devices with free solvers, lay out and submit an openEBL chip, analyse real measurements, and model lasers and the reference link.</p></div>
  <div class="card"><span class="card-label">Gallery and appendices</span><h3><a href="{% link devices-3d.md %}">PDK devices in 3D</a></h3><p>Devices from the SiEPIC EBeam, CORNERSTONE and Luxtelligence open PDKs, with credit to their designers; plus formulas, constants, a glossary and a directory of open tools.</p></div>
</div>

## Interactive demos

Each chapter has one or more demos that run in the browser with no installation: a link power budget, polarisation and wave packets, a slab-waveguide mode solver, Fresnel reflection and total internal reflection, Gaussian beams and fibre coupling, fibre modes, a platform comparator, directional couplers, MMI self-imaging, Mach–Zehnder interferometers, ring resonators, Bragg gratings by transfer matrix, grating-coupler phase matching, a fibre-array alignment game, a laser rate-equation simulator and a Vernier tunable laser, with more to come. The [course map]({% link course-map.md %}) lists them all. Where a free simulation by someone else already does the job well, such as the MIT and AIM Photonics Academy virtual-lab simulations, the chapter links to it.

## About

The tutorial's organisation draws on the open teaching material of the field, above all Chrostowski and Hochberg's *Silicon Photonics Design* and the UBC edX course built around it, the SiEPIC openEBL design–fabrication–test cycle, the AIM Photonics Academy courses and the open PDKs of SiEPIC and gdsfactory. It cites these works and links to them; it does not copy them. Every source is on the [References]({% link references.md %}) page.

**How this tutorial is made.** It is being developed with the help of AI tools, and this draft may contain mistakes. If you spot one, please open a [GitHub issue](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/issues), and we will correct it.

This is a living draft (v0.1, November 2026): all eight parts (Chapters 1–34) are written, with forty-two interactive demos and the 3D gallery; the hands-on labs are the next part to be written.
