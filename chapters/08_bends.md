---
title: "8. Bends, Tapers and Transitions"
parent: "Part II · Waveguides"
nav_order: 8
permalink: /part-2/ch08/
chapter: 8
---

# <span class="chapnum">Chapter 8</span>Bends, Tapers and Transitions

Chips route light around corners and between widths and layers, and every transition is a chance to lose it.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain why bends radiate, and estimate the smallest safe radius for a platform;
- explain the mode mismatch at a straight–bend junction and how Euler bends remove it;
- design adiabatic tapers between widths;
- compute junction loss from mode overlap;
- describe waveguide crossings, mode converters and transitions between layers.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How tight can a bend be, and how short a taper?

</div>

## <span class="secnum">8.1</span>Radiation loss in bends

A straight waveguide guides because its mode travels slower than light in the cladding would. In a bend of radius $$R$$, the parts of the mode further from the centre must travel faster to keep the wavefronts radial. At a distance $$x$$ outward from the waveguide, the phase velocity they would need is that of an index $$n_\mathrm{eff}R/(R + x)$$, and beyond the point where this falls below the cladding index, the field can no longer keep up and radiates away.

The standard way to see this is the **conformal transformation**: a bent waveguide behaves like a straight one whose index profile is tilted, $$n'(x) = n(x)\,(1 + x/R)$$. The tilt raises the cladding index on the outside of the bend until, at the **radiation caustic**

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Radiation caustic of a bend</div>

$$x_r = R\left(\frac{n_\mathrm{eff}}{n_\mathrm{clad}} - 1\right),$$

</div>

it exceeds the mode index and the evanescent tail turns into a radiating wave. The power lost per unit length is set by how much of the tail is left at the caustic, roughly $$e^{-2\gamma x_r}$$ with $$\gamma = k_0\sqrt{n_\mathrm{eff}^2 - n_\mathrm{clad}^2}$$ the decay constant of the tail. Bend loss therefore falls exponentially with radius, $$\alpha_\mathrm{bend} \approx C_1e^{-C_2R}$$, a form first worked out by Marcuse.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 8.1 · How many decay lengths to the caustic?</div>

For the TE mode of a 500 × 220 nm silicon strip ($$n_\mathrm{eff} = 2.446$$, $$\gamma = 8.0\ \mu\mathrm{m}^{-1}$$), $$x_r = R(2.446/1.444 - 1) = 0.69R$$. At $$R = 2$$ µm the caustic is 1.39 µm away, $$\gamma x_r = 11$$ decay lengths, and almost nothing radiates. For the TM mode ($$n_\mathrm{eff} = 1.771$$, $$\gamma = 4.2\ \mu\mathrm{m}^{-1}$$), even $$R = 5$$ µm gives only $$\gamma x_r = 4.7$$: TM modes need much larger bends. A moderately confining SiN waveguide (1.2 × 0.4 µm, $$n_\mathrm{eff} \approx 1.67$$, $$1/\gamma \approx 290$$ nm) reaches $$\gamma x_r = 11$$ only at $$R = 20$$ µm. The number $$\gamma x_r$$ is a quick way to compare platforms: a 2 µm silicon bend and a 20 µm SiN bend radiate about equally.

</div>

In practice, silicon strip waveguides have negligible radiation loss at 1550 nm for radii above about 2–3 µm (TE), silicon ribs need tens of micrometres because their lateral contrast is low, moderately confining SiN needs tens of micrometres, and weakly confining SiN needs millimetres ([Chapter 4]({% link chapters/04_platforms.md %})). In a bend the mode also leans outward, so its field at the outer sidewall grows and so does scattering ([Chapter 7]({% link chapters/07_loss.md %})).

## <span class="secnum">8.2</span>Mode mismatch at straight–bend junctions

Where a straight waveguide meets a circular bend, the mode changes shape abruptly: in the bend it is shifted outward and slightly narrower. The overlap between the straight and bent modes is less than one, so a little power is lost or converted into higher-order modes at each junction, twice per bend. For tight bends this junction loss can exceed the radiation loss.

Two remedies are common. A small **lateral offset** between the straight guide and the bend aligns the two modes' centres. A better one is to avoid the abrupt change of curvature altogether with an **Euler bend** (a clothoid), whose curvature rises linearly with path length from zero to a maximum and falls back again, so the mode can adapt continuously. Bézier bends do the same with polynomial curves.

**Try it.** Compare a circular and an Euler 90° bend with the same footprint; the curvature plot shows the jump that the Euler bend removes.

{% include demos/bend.html %}

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

For the same footprint, a full Euler bend reaches a smaller minimum radius than the circular bend it replaces and is longer, but it has no curvature jumps. In silicon strips, where radiation is negligible above a few micrometres, removing the junction mismatch usually wins, and Euler bends are the default in many PDKs and in gdsfactory's routing. In weakly confining platforms, where radiation dominates, the minimum radius matters more.

</div>

## <span class="secnum">8.3</span>Tapers and adiabaticity

A taper changes a waveguide's width (or thickness) gradually, to connect a 500 nm routing waveguide to a 3 µm low-loss waveguide, an MMI or a fibre coupler. If it changes slowly enough, the fundamental mode simply follows the changing cross-section and no power is transferred to other modes: the taper is **adiabatic**. Too fast, and the local fundamental mode couples to higher-order and radiation modes.

The rule of thumb, due to Love, compares the length over which the taper changes with the beat length between the fundamental mode and the nearest mode it can couple to (for a symmetric taper, the next symmetric mode):

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Adiabatic taper criterion</div>

$$\frac{\mathrm{d}\rho}{\mathrm{d}z} < \frac{\rho\,(\beta_1 - \beta_2)}{2\pi},$$

</div>

where $$\rho$$ is the local half-width and $$\beta_1 - \beta_2$$ the local difference of propagation constants. Wherever the two modes are close in index, which is where the taper is wide, it must change slowly; where they are far apart it can change fast. A linear taper wastes length at the narrow end, so parabolic and exponential profiles, or profiles designed to satisfy the criterion everywhere with a constant margin, are shorter for the same loss. As a reference point, the SiEPIC EBeam PDK routes from 500 nm to 3 µm with linear tapers 20 and 40 µm long {% include cite.html keys="ebeampdk" %}.

## <span class="secnum">8.4</span>Overlap integrals and butt coupling

When two different waveguides meet abruptly, the fraction of power that enters the second one's mode is the overlap integral of [Chapter 3]({% link chapters/03_gaussian.md %}),

$$\eta = \frac{\left\lvert\iint E_1E_2^*\,\mathrm{d}A\right\rvert^2}{\iint\lvert E_1\rvert^2\,\mathrm{d}A\iint\lvert E_2\rvert^2\,\mathrm{d}A},$$

and the rest is reflected, radiated or launched into other modes. The same integral, between a waveguide's mode and the modes of a wider section, tells you which modes an abrupt junction excites, the starting point of the MMI of [Chapter 10]({% link chapters/10_mmi.md %}).

## <span class="secnum">8.5</span>Waveguide crossings

Planar circuits often have to cross two waveguides. A plain crossing scatters light into the crossing guide and out of the plane, because the mode is suddenly unguided sideways. Good crossings widen the mode before the intersection, with an MMI section or elliptical mode expanders, so that it diffracts less while it crosses and refocuses on the far side. The crossing in the SiEPIC EBeam PDK, based on this idea, has under 0.2 dB of loss and crosstalk below −40 dB {% include cite.html keys="ebeampdk,sanchis2009" %}; you can see it in 3D in the [gallery]({% link devices-3d.md %}#dev-siepic-crossing).

## <span class="secnum">8.6</span>Transitions between layers and modes

Platforms with two guiding layers, such as silicon nitride above silicon, move light between them with **interlayer transitions** (escalators): the lower waveguide tapers down to a narrow tip while the upper one tapers up, so the mode moves adiabatically from one to the other. The same principle of slowly crossing the effective indices underlies the edge coupler of [Chapter 16]({% link chapters/16_edge.md %}) and the III–V-to-silicon couplers of lasers on silicon ([Chapter 27]({% link chapters/27_lasersonsi.md %})).

**Mode converters** change the mode order instead of the layer. An asymmetric directional coupler, with a narrow waveguide whose TE0 index equals the TE1 index of a wider one, transfers TE0 in the narrow guide to TE1 in the wide one; chains of such couplers multiplex several modes in one waveguide. Polarisation rotators work similarly, through hybridised modes ([Chapter 14]({% link chapters/14_wdm.md %})).

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter {% include cite.html keys="vmlab" %}:

- [VM-Lab: bend radius of curvature](https://s3.amazonaws.com/fip-2/Radius-of-Curvature/index.html), [bend loss and polarisation](https://s3.amazonaws.com/fip-2/Polarization/index.html) and [Bézier bends](https://s3.amazonaws.com/fip-2/Bezier/index.html)
- [VM-Lab: waveguide escalator](https://s3.amazonaws.com/fip-14/Taper-Length/index.html) and [waveguide crossing](https://s3.amazonaws.com/fip-15/Waveguide-Crossing/index.html)

</div>

## Reading

{% include reflist.html keys="chrostowski2015,okamoto,snyderlove,sanchis2009,ebeampdk" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A bend radiates beyond the caustic $$x_r = R(n_\mathrm{eff}/n_\mathrm{clad} - 1)$$; the loss falls exponentially with $$\gamma x_r$$, so with radius.
- Silicon TE strips are fine above about 2–3 µm; TM modes, ribs and SiN need tens of micrometres, weakly confining SiN millimetres.
- Circular bends lose a little at each straight–bend junction through mode mismatch; Euler bends ramp the curvature and avoid it.
- A taper is adiabatic when its width changes slowly compared with the local beat length to the nearest coupled mode.
- Crossings, escalators and mode converters all work by managing the mode adiabatically or by phase matching.

</div>
