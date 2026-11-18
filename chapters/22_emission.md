---
title: "22. Light Meets Matter: Absorption, Emission and Gain"
parent: "Part VI · Lasers and Amplifiers"
nav_order: 22
permalink: /part-6/ch22/
chapter: 22
---

# <span class="chapnum">Chapter 22</span>Light Meets Matter: Absorption, Emission and Gain

A laser is an amplifier with feedback; this chapter builds the amplifier from the physics of how electrons absorb and emit light.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe absorption, spontaneous emission and stimulated emission;
- derive the Einstein relations, and connect the spontaneous lifetime to the gain cross-section;
- explain why a two-level system cannot be inverted, and how three- and four-level systems are;
- define the gain coefficient and its lineshape;
- explain why silicon is a poor light emitter, and what germanium, III–V semiconductors and erbium offer instead.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What does it take for a material to amplify light?

</div>

## <span class="secnum">22.1</span>Photons and energy levels

Light of frequency $$\nu$$ comes in quanta of energy $$E = h\nu = hc/\lambda$$: 0.80 eV at 1550 nm and 0.95 eV at 1310 nm. A photon also carries momentum $$h/\lambda$$, but at these wavelengths it is a thousand times smaller than the momenta of electrons in a crystal, so an optical transition leaves the electron's crystal momentum essentially unchanged. That small fact decides which materials can emit light efficiently (Section 22.5).

An atom or ion has discrete energy levels. A solid has bands of allowed energies separated by gaps: the filled **valence band**, the mostly empty **conduction band**, and between them the **band gap** $$E_g$$. Light interacts with matter when a photon's energy matches the energy difference between two states the electron can occupy.

## <span class="secnum">22.2</span>Absorption and emission

Take two levels, 1 below 2, separated by $$h\nu$$, with populations $$N_1$$ and $$N_2$$ per unit volume. Einstein recognised three processes:

- **Absorption**: a photon lifts an electron from 1 to 2, at a rate $$B_{12}\rho(\nu)N_1$$ proportional to the spectral energy density of the light $$\rho(\nu)$$.
- **Stimulated emission**: a photon induces the drop from 2 to 1 and a second photon is emitted, identical in frequency, direction, phase and polarisation, at a rate $$B_{21}\rho(\nu)N_2$$. This is the amplifying process: the **L** and **A** of LASER.
- **Spontaneous emission**: the electron drops on its own, at a rate $$A_{21}N_2$$, emitting a photon in a random direction and phase. Its inverse $$\tau_{sp} = 1/A_{21}$$ is the spontaneous lifetime.

Requiring that the three rates reproduce the thermal equilibrium of the levels (Boltzmann) and of the radiation (Planck) gives the **Einstein relations** {% include cite.html keys="salehteich,siegman" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Einstein relations (equal degeneracies)</div>

$$B_{12} = B_{21}, \qquad \frac{A_{21}}{B_{21}} = \frac{8\pi n^3h\nu^3}{c^3}$$

</div>

The first says that absorption and stimulated emission are the same process run in opposite directions, with the same strength. The second ties the spontaneous rate to the stimulated one: a transition that emits spontaneously fast also amplifies strongly. It is the reason short-wavelength lasers are hard (the spontaneous rate grows as $$\nu^3$$), and the reason a laser always carries some spontaneous-emission noise ([Chapter 25]({% link chapters/25_dynamics.md %})).

## <span class="secnum">22.3</span>Population inversion and gain

A beam of photon flux density travelling through the medium gains from stimulated emission and loses to absorption. Because $$B_{12} = B_{21}$$, the net growth depends only on the population difference:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Gain coefficient</div>

$$\gamma(\nu) = \sigma(\nu)\,(N_2 - N_1), \qquad \sigma(\nu) = \frac{\lambda^2}{8\pi n^2\,\tau_{sp}}\,g(\nu)$$

</div>

where $$\sigma$$ is the **transition cross-section** and $$g(\nu)$$ the normalised lineshape (Section 22.4). The intensity grows as $$e^{\gamma z}$$ when $$\gamma > 0$$, which needs **population inversion**, $$N_2 > N_1$$. In thermal equilibrium the lower level is always the fuller one, so inversion must be pumped. How hard depends on the level scheme:

- **Two levels**: the pump drives absorption and stimulated emission equally, so at best $$N_2 \to N_1$$: transparency, never gain.
- **Three levels** (pump 1 → 3, fast 3 → 2, laser 2 → 1): the lower laser level is the ground state, so more than half of all the atoms must be pumped out of it before there is any gain. The pump rate must exceed the spontaneous rate.
- **Four levels** (pump 0 → 3, fast 3 → 2, laser 2 → 1, fast 1 → 0): the lower laser level empties as fast as it fills, so any pumping gives inversion.

**Try it.** Pump each system and watch the populations and the inversion; then add a strong signal and see the inversion, and the gain, saturate.

{% include demos/levels.html %}

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 22.1 · Pumping erbium</div>

Erbium ions in silica glass emit near 1530 nm from a level with a spontaneous lifetime of about 10 ms, and the transition ends on the ground state: a three-level system. Transparency needs a pump rate comparable to $$1/\tau_{sp} = 100$$ s⁻¹. With a pump absorption cross-section of about $$2.5\times10^{-21}$$ cm² at 980 nm (photon energy $$2.0\times10^{-19}$$ J), that takes an intensity of about $$2.0\times10^{-19}/(2.5\times10^{-21} \times 0.01) \approx 8$$ kW/cm². In a fibre core of 20 µm², it is a couple of milliwatts. The long lifetime makes erbium easy to invert and slow to respond, which is why erbium-doped fibre amplifiers do not distort fast data ([Chapter 28]({% link chapters/28_soa.md %})).

</div>

Inversion has a second, subtler limit. Stimulated emission by the amplified light itself takes atoms out of the upper level, so a strong signal pulls the inversion down. The gain then falls as $$\gamma = \gamma_0/(1 + I/I_\mathrm{sat})$$: **gain saturation**. It is what stabilises a laser's power above threshold ([Chapter 24]({% link chapters/24_fp.md %})) and limits an amplifier's output ([Chapter 28]({% link chapters/28_soa.md %})).

## <span class="secnum">22.4</span>Lineshape and gain spectrum

No transition has a single frequency. The lineshape $$g(\nu)$$ comes from two kinds of broadening:

- **Homogeneous broadening** affects every emitter alike. The finite lifetime of the states, and collisions or phonons that interrupt the phase, give a Lorentzian line. A strong signal at one frequency saturates the whole line.
- **Inhomogeneous broadening** comes from emitters that differ: ions at different sites in a glass, or quantum dots of different sizes. Each emitter has its own centre frequency, and the line is the sum, usually close to a Gaussian. A signal saturates only the emitters that match it, burning a "hole" in the gain spectrum.

The cross-section formula says that a broad line has a small peak cross-section: the same total strength is spread over more frequencies. Semiconductors are a special case: their gain spectrum is shaped mostly by how the bands fill with carriers ([Chapter 23]({% link chapters/23_gain.md %})), and it is tens of nanometres wide, which is what makes widely tunable lasers possible ([Chapter 26]({% link chapters/26_tunable.md %})).

## <span class="secnum">22.5</span>Direct and indirect band gaps

In a semiconductor, the lowest conduction-band states and the highest valence-band states may sit at the same crystal momentum (a **direct gap**, as in GaAs and InP-based alloys) or at different momenta (an **indirect gap**, as in silicon and germanium). Because the photon carries almost no momentum, an electron at the bottom of an indirect conduction band cannot drop to the top of the valence band by emitting a photon alone. It needs a phonon to supply the momentum, a far less likely three-body process.

The consequence is in the radiative recombination coefficient: about $$10^{-10}$$ cm³/s in InGaAsP but about $$10^{-14}$$ cm³/s in silicon. At $$10^{18}$$ carriers per cm³ the radiative lifetime is 10 ns in InGaAsP and 100 µs in silicon, so in silicon defects and Auger recombination, which take microseconds or less, win almost every time: silicon emits a percent of its electrons as light at best, usually far less. Other routes to light on silicon follow:

- **Germanium** is indirect too, but its direct valley lies only 0.14 eV above the indirect one; tensile strain and heavy n-doping push electrons into it, and germanium lasers have been shown, though inefficient {% include cite.html keys="zhou2015" %}.
- **Erbium** ions in oxides or nitrides emit at 1530 nm through an atomic transition that does not care about silicon's bands, and make optical amplifiers on a chip, but not efficient electrically pumped lasers.
- **III–V semiconductors** (InP, GaAs and their alloys) have direct gaps across the telecom bands and make the lasers of silicon photonics, brought onto the chip by the methods of [Chapter 27]({% link chapters/27_lasersonsi.md %}).

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

A material amplifies light when more of its emitters are in the upper state of a transition than in the lower one, at the photon's energy. That needs a strong, fast radiative transition (a large cross-section, which comes with a short spontaneous lifetime), a level scheme that can be inverted (four-level-like, or a semiconductor's bands), and a pump fast enough to beat spontaneous emission and nonradiative losses. Direct-gap III–V semiconductors meet all three under electrical injection; silicon meets none.

</div>

## Reading

{% include reflist.html keys="salehteich,siegman,coldren,zhou2015" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Absorption, stimulated emission and spontaneous emission; Einstein: $$B_{12} = B_{21}$$ and $$A_{21}/B_{21} = 8\pi n^3h\nu^3/c^3$$.
- Gain $$\gamma = \sigma(N_2 - N_1)$$ needs population inversion; the cross-section is $$\lambda^2g(\nu)/(8\pi n^2\tau_{sp})$$.
- Two-level systems cannot invert; three-level systems need more than half pumped; four-level systems invert at any pump.
- Strong signals saturate the gain, $$\gamma_0/(1 + I/I_\mathrm{sat})$$; lines are broadened homogeneously or inhomogeneously.
- Indirect-gap silicon emits poorly (B ≈ 10⁻¹⁴ against 10⁻¹⁰ cm³/s for InGaAsP), so lasers on silicon use III–V gain.

</div>
