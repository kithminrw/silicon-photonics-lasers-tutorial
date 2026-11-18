---
title: "23. Semiconductor Gain Media"
parent: "Part VI · Lasers and Amplifiers"
nav_order: 23
permalink: /part-6/ch23/
chapter: 23
---

# <span class="chapnum">Chapter 23</span>Semiconductor Gain Media

Inject electrons and holes into a direct-bandgap semiconductor and it amplifies light near its bandgap; the details set the laser's wavelength, efficiency and temperature behaviour.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- use band structure, density of states and quasi-Fermi levels;
- apply the Bernard–Duraffourg condition for gain;
- compute the gain spectrum against carrier density and find the transparency density;
- explain quantum wells and dots, optical confinement and the material systems for 1310 and 1550 nm;
- include recombination with the ABC model, and the effect of temperature.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How many carriers does it take to reach gain, and where is the gain peak?

</div>

## <span class="secnum">23.1</span>Bands, density of states and occupation

Near the band edges of a direct-gap semiconductor, electron energies are close to parabolic in crystal momentum $$k$$:

$$E_c(k) = E_g + \frac{\hbar^2k^2}{2m_e}, \qquad E_v(k) = -\frac{\hbar^2k^2}{2m_h},$$

with effective masses $$m_e$$ and $$m_h$$ (about 0.045 and 0.46 free-electron masses for an InGaAsP alloy with a 1550 nm gap). Counting the states in $$k$$-space gives a **density of states** that grows as the square root of the energy above each band edge. The light electron mass gives the conduction band few states, so it fills quickly; the heavy holes have many.

The occupation of each state follows the Fermi–Dirac distribution. In equilibrium a single Fermi level describes both bands. Under current injection, electrons and holes each come to equilibrium among themselves in a fraction of a picosecond, far faster than they recombine, so each band gets its own **quasi-Fermi level**, $$E_{Fc}$$ and $$E_{Fv}$$, set by the electron and hole densities $$N$$ and $$P$$. In an undoped active region $$N = P$$.

## <span class="secnum">23.2</span>Quasi-Fermi levels and the condition for gain

An optical transition at photon energy $$h\nu$$ connects a conduction state and a valence state at the same $$k$$. It gives net stimulated emission when the upper state is more likely full than the lower one, $$f_c > f_v$$, which, with Fermi functions, becomes the **Bernard–Duraffourg condition** {% include cite.html keys="coldren" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Condition for gain (Bernard–Duraffourg)</div>

$$E_g < h\nu < E_{Fc} - E_{Fv}$$

</div>

The quasi-Fermi levels must be separated by more than the band gap: the semiconductor version of population inversion ([Chapter 22]({% link chapters/22_emission.md %})). Photons in the window are amplified; photons above it are still absorbed. The gain coefficient is the joint density of states, times the strength of the transition (the momentum matrix element), times the occupation factor $$f_c - f_v$$, smoothed by the intraband scattering that broadens each transition by a few meV.

## <span class="secnum">23.3</span>The gain spectrum

That recipe is computed in <code>figsrc/ch23_gain.py</code> for a bulk InGaAsP-like material with a 1550 nm gap, and live in the demo. Unpumped, it absorbs about 4000 cm⁻¹ 50 meV above the gap. As carriers are injected, the absorption near the edge bleaches; at the **transparency density** $$N_\mathrm{tr}$$ the peak gain crosses zero; beyond it the gain grows, and its peak moves to shorter wavelengths as the bands fill.

**Try it.** Raise the carrier density and the temperature. The band diagram shows the states filling up to the quasi-Fermi levels, and the spectrum shows the gain window opening.

{% include demos/gainspec.html %}

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 23.1 · Transparency and the gain needed by a laser</div>

The model gives $$N_\mathrm{tr} = 1.3\times10^{18}$$ cm⁻³. The peak gain rises to 370 cm⁻¹ at $$2\times10^{18}$$, 870 cm⁻¹ at $$3\times10^{18}$$ and 1700 cm⁻¹ at $$5\times10^{18}$$ cm⁻³, with a **differential gain** $$\mathrm{d}g/\mathrm{d}N = 4.7\times10^{-16}$$ cm² at $$3\times10^{18}$$. The Fabry–Pérot laser of [Chapter 24]({% link chapters/24_fp.md %}) needs a material gain of 725 cm⁻¹, reached at $$2.7\times10^{18}$$ cm⁻³. From $$2$$ to $$5\times10^{18}$$ cm⁻³ the peak moves from 1480 to 1357 nm; at $$2.7\times10^{18}$$ it sits at 1444 nm. In practice band-gap renormalisation (many-body effects at high density, left out here) pulls it back by a few tens of meV, so designers choose a gap somewhat longer than the laser wavelength. Near threshold the gain is often fitted as $$g = g_0\ln(N/N_\mathrm{tr})$$; the laser demo uses $$g_0 = 1500$$ cm⁻¹ and $$N_\mathrm{tr} = 2\times10^{18}$$ cm⁻³, which has the same slope but needs $$3.2\times10^{18}$$ cm⁻³.

</div>

## <span class="secnum">23.4</span>Heterostructures, quantum wells and quantum dots

A modern laser's active region is not a uniform block:

- **Double heterostructures** sandwich a thin layer of narrow-gap, higher-index material between wider-gap claddings. The band offsets trap the carriers in the thin layer, and the index step guides the light along it. Only the fraction $$\Gamma$$ of the mode that overlaps the active layer, the **optical confinement factor**, sees the gain: the **modal gain** is $$\Gamma g$$.
- **Quantum wells**, layers a few nanometres thick, quantise the motion perpendicular to the layer. The density of states becomes a staircase, with a full step at the band edge. Fewer carriers fill it, so the transparency density per well is lower and the differential gain higher. Compressive strain lightens the holes and helps further, and well gain is polarised (TE for compressive strain).
- **Quantum dots** confine the carriers in all three directions, giving atom-like levels. Lasers with dot gain have low thresholds and depend little on temperature. Because carriers cannot diffuse far to defects, they also tolerate the dislocations of growth on silicon ([Chapter 27]({% link chapters/27_lasersonsi.md %})). Their size distribution broadens the gain inhomogeneously.

## <span class="secnum">23.5</span>Material systems for 1310 and 1550 nm

- **InGaAsP on InP**: the classic telecom alloy. Its composition tunes the gap across 1.1–1.65 µm while staying lattice-matched to InP.
- **AlGaInAs on InP**: a larger conduction-band offset keeps electrons in the wells at high temperature, so lasers degrade less with heat. It is common in uncooled datacom lasers.
- **InAs/GaAs quantum dots**: emit near 1310 nm, are temperature-stable, and can be grown directly on silicon.
- Further afield: GaSb-based alloys reach the mid-infrared, GaN the visible.

## <span class="secnum">23.6</span>Recombination

Injected carriers recombine through three main channels, summarised by the **ABC model**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Recombination rate (ABC model)</div>

$$R(N) = AN + BN^2 + CN^3$$

</div>

- $$AN$$: Shockley–Read–Hall recombination at defects ($$A \approx 10^8$$ s⁻¹).
- $$BN^2$$: radiative recombination, the spontaneous emission ($$B \approx 10^{-10}$$ cm³/s).
- $$CN^3$$: Auger recombination, where the energy goes to a third carrier instead of a photon ($$C \approx 3\times10^{-29}$$ cm⁶/s at 1550 nm).

The threshold current density of a laser is $$qd\,R(N_\mathrm{th})/\eta_i$$ for an active layer of thickness $$d$$. At the densities of [Chapter 24]({% link chapters/24_fp.md %}), $$3.2\times10^{18}$$ cm⁻³, the three terms contribute in the ratio 0.3 : 1.05 : 1.0. Auger recombination is as large as the radiative term, and it grows steeply with temperature. Heat also smears the Fermi functions (the gain model needs 13 % more carriers for 1000 cm⁻¹ at 340 K than at 300 K) and lets carriers leak over the barriers. Together these make long-wavelength lasers temperature-sensitive, with characteristic temperatures $$T_0$$ of 50–70 K for InGaAsP; AlGaInAs and quantum dots do better ([Chapter 24]({% link chapters/24_fp.md %})).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Compressively strained AlGaInAs multiple quantum wells for the four lasers at 1550 nm, chosen for their temperature behaviour, since the link's transceivers are not actively cooled.

</div>

## Reading

{% include reflist.html keys="coldren,salehteich" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Injection gives each band its own quasi-Fermi level; gain needs $$E_g < h\nu < E_{Fc} - E_{Fv}$$.
- A bulk InGaAsP-like material becomes transparent at about 1.3 × 10¹⁸ cm⁻³; its differential gain is about 5 × 10⁻¹⁶ cm², and its gain peak moves to shorter wavelengths as the bands fill.
- Only the overlap Γ of the mode with the active region counts: modal gain = Γg.
- Quantum wells lower transparency and raise differential gain; quantum dots add temperature stability and defect tolerance.
- Recombination R = AN + BN² + CN³; Auger and carrier leakage make 1550 nm lasers temperature-sensitive.

</div>
