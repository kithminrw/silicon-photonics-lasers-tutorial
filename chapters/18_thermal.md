---
title: "18. Thermo-Optic Phase Shifters"
parent: "Part V · Active Devices"
nav_order: 18
permalink: /part-5/ch18/
chapter: 18
---

# <span class="chapnum">Chapter 18</span>Thermo-Optic Phase Shifters

Heating silicon changes its index enough to tune any device, at a cost in power and speed.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- compare thermo-optic coefficients across platforms, and convert them to a waveguide's index change and a ring's drift;
- derive the power for a π shift from a thermal circuit, and see why it does not depend on length;
- compare metal and doped-silicon heaters;
- improve efficiency with trenches and undercuts, and pay for it in speed;
- handle thermal crosstalk, and lock a ring to a laser with a feedback loop.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How many milliwatts for a π shift, and how fast?

</div>

## <span class="secnum">18.1</span>The thermo-optic effect

The refractive index of every material changes with temperature. Silicon's changes by about $$1.8 \times 10^{-4}$$ per kelvin at 1550 nm, among the largest of any transparent material. Silicon nitride and silicon dioxide change by roughly ten times less (about $$2.5 \times 10^{-5}$$ and $$1 \times 10^{-5}$$ /K); lithium niobate's coefficients are a few times $$10^{-5}$$ /K and depend on the crystal axis; InP's is close to silicon's. A large coefficient is good for tuning and bad for stability.

A waveguide's effective index follows the materials it samples. femwell gives $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}T = 2.0 \times 10^{-4}$$ /K for a 500 × 220 nm silicon strip and $$1.9 \times 10^{-4}$$ /K for the rib used below (with the oxide's own coefficient included). It is slightly larger than the bulk value for the strip because $$n_\mathrm{eff}$$ responds to a change of core index more than one for one in a high-contrast guide. A resonance moves by

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Thermal drift of a resonance</div>

$$\frac{\mathrm{d}\lambda}{\mathrm{d}T} = \frac{\lambda}{n_g}\,\frac{\mathrm{d}n_\mathrm{eff}}{\mathrm{d}T}$$

</div>

which is 74 pm/K for the strip ($$n_g = 4.18$$) and 75 pm/K for the rib ($$n_g = 3.89$$): the "70–80 pm/K" quoted for silicon rings since [Chapter 1]({% link chapters/01_why.md %}). The same drift that forces every silicon ring to be controlled makes heating the cheapest way to tune.

## <span class="secnum">18.2</span>Heater types

- **Metal heaters.** A strip of TiN, tungsten or another resistive metal, a micrometre or two above the waveguide in the cladding. Simple and optically harmless if it is far enough from the mode, but the heat must cross the oxide to reach the waveguide, which makes it slower.
- **Doped-silicon heaters.** Current flows through doped silicon next to, or in, the waveguide, so the heat is made where the light is. The response starts at once and the efficiency is a little better, but doping near the mode adds free-carrier loss ([Chapter 19]({% link chapters/19_eo.md %})).
- **In-waveguide heaters.** A lightly doped waveguide with contacts on both sides is its own heater: the extreme of the previous case.

Heaters are resistors driven by a current or a voltage, often with pulse-width modulation from a digital controller. Their electrical power is what the energy budget counts.

## <span class="secnum">18.3</span>Thermal circuits

Heat obeys an equation of the same form as current in a resistor network. A heater dissipating $$P$$ over a length $$L$$ raises the waveguide by $$\Delta T = P\,R_\mathrm{th}$$, with a thermal resistance $$R_\mathrm{th} = 1/(G'L)$$ set by the conductance per unit length $$G'$$ between the heater and the heat sink, mostly the silicon substrate below the BOX. The phase shift is then

$$\Delta\phi = \frac{2\pi}{\lambda}\,\frac{\mathrm{d}n_\mathrm{eff}}{\mathrm{d}T}\,\Delta T\,L = \frac{2\pi}{\lambda}\,\frac{\mathrm{d}n_\mathrm{eff}}{\mathrm{d}T}\,\frac{P}{G'},$$

and the length cancels:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Power for a π phase shift</div>

$$P_\pi = \frac{\lambda\,G'}{2\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}T}$$

</div>

A longer heater spreads the same power over more waveguide: the temperature rise falls as $$1/L$$ while the phase accumulates over $$L$$. Only the cross-section, through $$G'$$, sets $$P_\pi$$. The same network has a heat capacity $$C_\mathrm{th}$$, and the response to a step of power rises with a time constant of order $$\tau = R_\mathrm{th}C_\mathrm{th}$$.

To get numbers, the heat equation was solved over the cross-section of a 500 × 220 nm rib on a 2 µm BOX with scikit-fem, for a TiN heater 1.7 µm above the silicon and for heating in the doped rib and slab (<code>figsrc/ch18_heater.py</code>). [Table 18.1](#tab-18-1) collects the results.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 18.1 · P<sub>π</sub> of a TiN heater</div>

For the plain TiN heater, the solver gives a waveguide temperature rise of 0.158 K per mW/mm of heater, so $$G' = 6.35$$ W/(m·K). With $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}T = 1.89 \times 10^{-4}$$ /K,

$$P_\pi = \frac{1.55\times10^{-6} \times 6.35}{2 \times 1.89\times10^{-4}} = 26\ \mathrm{mW}.$$

A π shift needs $$\Delta T\,L = \lambda/(2\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}T) = 4.1$$ K·mm: 14 K over 300 µm, or 4 K over a millimetre, for the same 26 mW. The 10–90 % rise time is 17 µs.

</div>

**Table 18.1. Thermo-optic phase shifters on 220 nm SOI (2D heat-equation solutions, 1550 nm).** Rib 500 × 220 nm with a 90 nm slab, 2 µm BOX, 2.3 µm oxide cladding. Trenches run through cladding and BOX 3 µm from the waveguide; the undercut removes the substrate beneath a 24 µm wide oxide membrane.
{: .tabcaption #tab-18-1 }

| Heater | Isolation | G' (W/m·K) | P<sub>π</sub> | 10–90 % rise | P<sub>π</sub> × rise |
|---|---|---|---|---|---|
| TiN, 1.7 µm above | none | 6.35 | 26.0 mW | 17 µs | 450 mW·µs |
| TiN | deep trenches | 3.99 | 16.4 mW | 21 µs | 350 mW·µs |
| TiN | substrate undercut | 1.11 | 4.5 mW | 180 µs | 810 mW·µs |
| doped slab and rib | none | 5.40 | 22.1 mW | 14 µs | 310 mW·µs |
| doped slab and rib | deep trenches | 3.81 | 15.6 mW | 19 µs | 290 mW·µs |
| doped slab and rib | substrate undercut | 1.05 | 4.3 mW | 177 µs | 760 mW·µs |

These are idealised cross-sections, without the heater's ends, its metal leads or the openings that a real undercut needs, but they fall in the range reported for real devices: tens of milliwatts and microseconds for a plain heater, a few milliwatts and hundreds of microseconds when suspended {% include cite.html keys="chrostowski2015" %}.

**Try it.** Switch between the heaters and the isolation schemes. The cross-section is coloured by the computed temperature, and the plots compare the step responses and the six designs.

{% include demos/heater.html %}

## <span class="secnum">18.4</span>Improving efficiency

The plain heater wastes most of its power, which flows straight down through the BOX into the substrate. There are three ways to keep it near the waveguide:

- **Deep trenches** through the cladding and the BOX on both sides stop heat spreading sideways in the oxide. In Table 18.1 they cut $$P_\pi$$ from 26 to 16 mW and slow the response only a little.
- **Undercutting** the substrate beneath the waveguide removes the main heat path. The heat must then flow sideways through a thin oxide membrane, a far larger thermal resistance: $$P_\pi$$ falls six-fold, to 4.5 mW, but the response becomes ten times slower, because $$\tau = R_\mathrm{th}C_\mathrm{th}$$ grows with $$R_\mathrm{th}$$.
- **Folding the waveguide** under one heater, in a spiral or several passes, uses the same heat several times; equivalently, it raises the phase per degree. It costs footprint, and the passes must not couple.

The product $$P_\pi\tau$$ improves only a little with trenches and gets worse with an undercut (last column of Table 18.1): isolation trades speed for power. For tuning rings and holding interferometers at their bias points, where the speed is set by the environment, slow and efficient wins. For switches, the microsecond response of a plain heater matters more.

## <span class="secnum">18.5</span>Crosstalk and stabilisation

Heat does not stay where it is made. In the plain TiN cross-section a waveguide 10 µm away from the heater warms by 9 % as much as the heated one, and by 37 % at 5 µm. An undercut, which forces the heat sideways, raises the 10 µm figure to 29 %. Dense arrays of heaters therefore either space their devices out, cut trenches between them, or measure the crosstalk matrix and invert it in the controller.

A ring on a WDM channel must stay within a small fraction of its passband of its laser, whatever the room and the neighbouring heaters do. This needs a **feedback loop**: a monitor photodiode on the drop port (or a tap on the through port), and a controller that adjusts the heater. Because the optimum is a maximum, not a zero crossing, the classic controller **dithers** the heater power slightly at a known frequency; a lock-in detector then reads the sign of the slope, and an integrator climbs to the peak.

Two design rules follow from the physics. A heater can only heat, which moves a silicon ring to longer wavelengths, so each ring is fabricated **blue** of its laser by more than the largest drift it must correct, and the heater pays for the difference all the time. And the heater power for a full free spectral range is $$2P_\pi$$, whatever the ring's size, because $$P_\pi$$ does not depend on length.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 18.2 · The heater budget of the reference link</div>

A 7.2 µm ring has an FSR of 13.7 nm (rib, $$n_g = 3.89$$). With $$2P_\pi = 52$$ mW for a full FSR, the tuning efficiency is $$13.7/52 \approx 0.26$$ nm/mW. To follow a 50 K range at 75 pm/K, 3.75 nm, plus up to ±1.6 nm of fabrication error (half a channel), a ring needs up to about 5.4 nm, or 20 mW. Eight rings (four modulators, four drop filters) then need up to 160 mW: at 200 Gb/s, 0.8 pJ/bit, a sixth of the link's 5 pJ/bit target ([Chapter 1]({% link chapters/01_why.md %})). Undercut heaters would cut it to about 0.15 pJ/bit; letting each ring lock to the nearest channel and reordering the channels electronically ([Chapter 14]({% link chapters/14_wdm.md %})) cuts the fabrication term.

</div>

**Try it.** Lock a drop ring to its laser while the room temperature swings.

{% include demos/lock.html %}

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

TiN heaters with deep trenches over every ring, a monitor photodiode on each drop port, and a dither lock-in loop per ring. Rings are designed about 2 nm blue of their channel at the coolest operating temperature, and lock to the nearest channel to limit heater power.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: MZI temperature](https://s3.amazonaws.com/fip-5b/Temperature/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="chrostowski2015,bogaerts2012,siew2021" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Silicon's index rises by about 1.8 × 10⁻⁴ /K; a 500 × 220 nm strip's $$n_\mathrm{eff}$$ by 2.0 × 10⁻⁴ /K, so rings drift by about 75 pm/K.
- $$P_\pi = \lambda G'/(2\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}T)$$ does not depend on length: about 26 mW for a TiN heater on 220 nm SOI.
- Trenches and undercuts lower $$P_\pi$$ (16 and 4.5 mW) but slow the response (to 180 µs with an undercut): isolation trades speed for power.
- Doped-silicon heaters respond faster because the heat is made in the waveguide.
- Heaters only heat: rings are designed blue of their lasers, and locked with dithered feedback loops whose power is a real part of the link's energy budget.

</div>
