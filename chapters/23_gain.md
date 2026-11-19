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

The quasi-Fermi levels must be separated by more than the band gap: the semiconductor version of population inversion ([Chapter 22]({% link chapters/22_emission.md %})). Photons in the window are amplified; photons above it are still absorbed. The gain coefficient is the joint density of states, times the strength of the transition (the momentum matrix element), times the occupation factor $$f_c - f_v$$, smoothed by the intraband scattering that broadens each transition by a few meV ([Figure 23.1](#fig-23-1)).

<figure id="fig-23-1">
  <img src="{{ '/assets/figs/ch23_recipe.svg' | relative_url }}" style="width:620px" alt="Left: electron and hole distributions filling the conduction and valence bands up to the quasi-Fermi levels at 2.7 times ten to the 18 per cubic centimetre. Right: the occupation factor f_c minus f_v against photon energy, positive between the band gap and the quasi-Fermi separation, and the resulting gain spectrum next to the absorption of the unpumped material">
  <figcaption><span class="capnum">Figure 23.1.</span> <strong>How the gain spectrum is built.</strong> The bulk InGaAsP-like model at \(N = P = 2.7\times10^{18}\) cm\(^{-3}\) and 300 K, the density the Chapter 24 laser needs. (a) Densities of states (lines) and carriers (shaded), with the energy axis broken across the gap. The light electrons fill their few states up to \(E_{Fc}\), 153 meV above the band edge; the heavy holes have 33 times more states, so the same number of them stay near the edge and \(E_{Fv}\) lies 24 meV inside the gap. (b) The occupation factor \(f_c - f_v\) of the states a photon connects: positive, so gain, between \(E_g\) and \(E_{Fc} - E_{Fv}\) (129 meV above the gap, 1334–1550 nm; shaded), negative above. (c) The gain is the unpumped material's absorption (dashed) times that factor, smoothed by the intraband broadening: it peaks at 726 cm\(^{-1}\) at 1444 nm. Drawn by <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">23.3</span>The gain spectrum

That recipe is computed in <code>figsrc/ch23_gain.py</code> for a bulk InGaAsP-like material with a 1550 nm gap, and live in the demo. Unpumped, it absorbs about 4000 cm⁻¹ 50 meV above the gap. As carriers are injected, the absorption near the edge bleaches; at the **transparency density** $$N_\mathrm{tr}$$ the peak gain crosses zero; beyond it the gain grows, and its peak moves to shorter wavelengths as the bands fill ([Figure 23.2](#fig-23-2)).

**Try it.** Raise the carrier density and the temperature. The band diagram shows the states filling up to the quasi-Fermi levels, and the spectrum shows the gain window opening.

{% include demos/gainspec.html %}

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 23.1 · Transparency and the gain needed by a laser</div>

The model gives $$N_\mathrm{tr} = 1.3\times10^{18}$$ cm⁻³. The peak gain rises to 370 cm⁻¹ at $$2\times10^{18}$$, 870 cm⁻¹ at $$3\times10^{18}$$ and 1700 cm⁻¹ at $$5\times10^{18}$$ cm⁻³, with a **differential gain** $$\mathrm{d}g/\mathrm{d}N = 4.7\times10^{-16}$$ cm² at $$3\times10^{18}$$. The Fabry–Pérot laser of [Chapter 24]({% link chapters/24_fp.md %}) needs a material gain of 725 cm⁻¹, reached at $$2.7\times10^{18}$$ cm⁻³. From $$2$$ to $$5\times10^{18}$$ cm⁻³ the peak moves from 1480 to 1357 nm; at $$2.7\times10^{18}$$ it sits at 1444 nm. In practice band-gap renormalisation (many-body effects at high density, left out here) pulls it back by a few tens of meV, so designers choose a gap somewhat longer than the laser wavelength. Near threshold the gain is often fitted as $$g = g_0\ln(N/N_\mathrm{tr})$$; the laser demo uses $$g_0 = 1500$$ cm⁻¹ and $$N_\mathrm{tr} = 2\times10^{18}$$ cm⁻³, which has the same slope but needs $$3.2\times10^{18}$$ cm⁻³.

</div>

<figure id="fig-23-2">
  <img src="{{ '/assets/figs/ch23_spectra.svg' | relative_url }}" style="width:620px" alt="Gain spectra of the bulk model at five carrier densities, with the peak moving from 1547 to 1357 nanometres, and the peak gain against carrier density on a logarithmic axis with the model's points, a logarithmic fit and the laser demo's fit">
  <figcaption><span class="capnum">Figure 23.2.</span> <strong>Gain against carrier density.</strong> (a) Spectra of the bulk model at 300 K for \(N\) = 1.0, 1.3, 2.0, 2.7 and \(5.0\times10^{18}\) cm\(^{-3}\): the peak (dots) rises from −138 cm\(^{-1}\) through zero at the transparency density to 369, 726 and 1713 cm\(^{-1}\), and moves from 1547 to 1357 nm. (b) Peak gain against \(N\) on a logarithmic axis, where a logarithmic fit is a straight line. Fitted between 2 and \(4\times10^{18}\), the model gives \(1367\ln(N/1.57\times10^{18})\); the laser demo's \(1500\ln(N/2.0\times10^{18})\) has nearly the same differential gain where the Chapter 24 laser works (4.6 against \(4.9\times10^{-16}\) cm\(^2\)) but reaches 725 cm\(^{-1}\) at \(3.2\times10^{18}\) instead of \(2.7\times10^{18}\) cm\(^{-3}\) (squares). Drawn by <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">23.4</span>Heterostructures, quantum wells and quantum dots

A modern laser's active region is not a uniform block:

- **Double heterostructures** sandwich a thin layer of narrow-gap, higher-index material between wider-gap claddings. The band offsets trap the carriers in the thin layer, and the index step guides the light along it. Only the fraction $$\Gamma$$ of the mode that overlaps the active layer, the **optical confinement factor**, sees the gain: the **modal gain** is $$\Gamma g$$ ([Figure 23.3](#fig-23-3)).
- **Quantum wells**, layers a few nanometres thick, quantise the motion perpendicular to the layer. The density of states becomes a staircase, with a full step at the band edge ([Figure 23.4](#fig-23-4)). Fewer carriers fill it, so the transparency density per well is lower and the differential gain higher. Compressive strain lightens the holes and helps further, and well gain is polarised (TE for compressive strain).
- **Quantum dots** confine the carriers in all three directions, giving atom-like levels. Lasers with dot gain have low thresholds and depend little on temperature. Because carriers cannot diffuse far to defects, they also tolerate the dislocations of growth on silicon ([Chapter 27]({% link chapters/27_lasersonsi.md %})). Their size distribution broadens the gain inhomogeneously.

<figure id="fig-23-3">
  <img src="{{ '/assets/figs/ch23_hetero.svg' | relative_url }}" style="width:620px" alt="Band diagrams and computed optical modes of two laser active regions: a 150 nanometre double heterostructure with a confinement factor of 0.32, and five 10 nanometre quantum wells inside a separate-confinement layer with a confinement factor of 0.09">
  <figcaption><span class="capnum">Figure 23.3.</span> <strong>Confining carriers and light.</strong> (a) A double heterostructure: 150 nm of InGaAsP (gap 0.80 eV) between InP claddings (1.34 eV). The band offsets trap electrons and holes in the layer, and its higher index guides the mode, which overlaps it by \(\Gamma\) = 0.32. (b) A separate-confinement heterostructure: five 10 nm wells with 10 nm barriers inside 40 nm layers of InGaAsP with a 1.25 µm gap. The wells hold the carriers on quantised levels; the wider layer guides the light, and the wells, 50 nm of material, see \(\Gamma\) = 0.09 of the mode. Top: band edges, energies schematic, positions to scale over ±0.3 µm. Bottom: index profile (grey; illustrative indices 3.17, 3.36 and 3.55 at 1550 nm) and the TE mode intensity computed with transfer matrices, wells shaded red. The ridge of <a href="{% link chapters/24_fp.md %}#fig-24-1">Figure 24.1</a> uses stack (b). Drawn by <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

<figure id="fig-23-4">
  <img src="{{ '/assets/figs/ch23_dos.svg' | relative_url }}" style="width:600px" alt="Density of states against energy: a square-root curve for bulk material, a staircase for a 10 nanometre quantum well that touches the bulk curve at each step, and sharp levels broadened into peaks for an ensemble of quantum dots">
  <figcaption><span class="capnum">Figure 23.4.</span> <strong>Density of states in bulk, wells and dots</strong> (conduction band, \(m_e = 0.045\,m_0\)). (a) Bulk: the states grow as the square root of the energy above the edge. (b) A 10 nm well, treated as infinitely deep: each subband adds a constant \(1.88\times10^{19}\) cm\(^{-3}\) eV\(^{-1}\), and the first step, at 84 meV, is as high as the bulk density of states there. The states a laser needs are all available at the band edge, so fewer carriers fill them. (c) Quantum dots: each dot has sharp levels (lines, a ground state with 2 states and an excited state with 4), and the spread of dot sizes broadens the ensemble into peaks; illustrative energies, arbitrary units. Drawn by <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">23.5</span>Material systems for 1310 and 1550 nm

- **InGaAsP on InP**: the classic telecom alloy. Its composition tunes the gap across 1.1–1.65 µm while staying lattice-matched to InP ([Figure 23.5](#fig-23-5)).
- **AlGaInAs on InP**: a larger conduction-band offset keeps electrons in the wells at high temperature, so lasers degrade less with heat. It is common in uncooled datacom lasers.
- **InAs/GaAs quantum dots**: emit near 1310 nm, are temperature-stable, and can be grown directly on silicon.
- Further afield: GaSb-based alloys reach the mid-infrared, GaN the visible.

<figure id="fig-23-5">
  <img src="{{ '/assets/figs/ch23_alloys.svg' | relative_url }}" style="width:620px" alt="Band gap at 300 K against lattice constant for GaP, AlAs, GaAs, InP, InAs, GaSb, AlSb and InSb with lines for their ternary alloys; vertical bars at the InP lattice constant show the InGaAsP and AlGaInAs ranges spanning the 1310 and 1550 nanometre bands">
  <figcaption><span class="capnum">Figure 23.5.</span> <strong>Band gap against lattice constant</strong> for III–V binaries (dots) and ternary alloys (lines), at 300 K. An alloy grown on InP must keep InP's lattice constant (dotted line): along it, lattice-matched InGaAs has a 0.73 eV gap (1.69 µm) and lattice-matched InAlAs 1.44 eV, so the quaternaries InGaAsP (between InGaAs and InP) and AlGaInAs (between InGaAs and InAlAs) span both telecom bands (bars). On GaAs, AlGaAs serves 850 nm VCSELs, and strained InAs dots reach 1310 nm (star). Open circles and dashed lines: indirect gaps. Computed from the band parameters of Vurgaftman et al. {% include cite.html keys="vurgaftman2001" %} (lowest of the Γ, X and L gaps, with the bowing of each ternary). Drawn by <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">23.6</span>Recombination

Injected carriers recombine through three main channels, summarised by the **ABC model**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Recombination rate (ABC model)</div>

$$R(N) = AN + BN^2 + CN^3$$

</div>

- $$AN$$: Shockley–Read–Hall recombination at defects ($$A \approx 10^8$$ s⁻¹).
- $$BN^2$$: radiative recombination, the spontaneous emission ($$B \approx 10^{-10}$$ cm³/s).
- $$CN^3$$: Auger recombination, where the energy goes to a third carrier instead of a photon ($$C \approx 3\times10^{-29}$$ cm⁶/s at 1550 nm).

The threshold current density of a laser is $$qd\,R(N_\mathrm{th})/\eta_i$$ for an active layer of thickness $$d$$. At the densities of [Chapter 24]({% link chapters/24_fp.md %}), $$3.2\times10^{18}$$ cm⁻³, the three terms contribute in the ratio 0.3 : 1.05 : 1.0 ([Figure 23.6](#fig-23-6)). Auger recombination is as large as the radiative term, and it grows steeply with temperature. Heat also smears the Fermi functions (the gain model needs 13 % more carriers for 1000 cm⁻¹ at 340 K than at 300 K) and lets carriers leak over the barriers. Together these make long-wavelength lasers temperature-sensitive, with characteristic temperatures $$T_0$$ of 50–70 K for InGaAsP; AlGaInAs and quantum dots do better ([Chapter 24]({% link chapters/24_fp.md %})).

<figure id="fig-23-6">
  <img src="{{ '/assets/figs/ch23_abc.svg' | relative_url }}" style="width:620px" alt="Defect, radiative and Auger recombination rates against carrier density on logarithmic axes, with the Chapter 24 laser's threshold marked, and the share of each channel against carrier density, Auger growing to dominate at high density">
  <figcaption><span class="capnum">Figure 23.6.</span> <strong>Where the injected carriers go</strong>, with \(A = 10^8\) s\(^{-1}\), \(B = 10^{-10}\) cm\(^3\)/s and \(C = 3\times10^{-29}\) cm\(^6\)/s. (a) The three rates grow as \(N\), \(N^2\) and \(N^3\). At the Chapter 24 laser's threshold, \(3.24\times10^{18}\) cm\(^{-3}\), the total is \(2.4\times10^{27}\) cm\(^{-3}\) s\(^{-1}\): a carrier lifetime \(N/R\) of 1.35 ns and, for a 50 nm active layer with \(\eta_i\) = 0.8, a threshold current density of 2.4 kA/cm\(^2\) (right axis). (b) The share of each channel: at threshold 14 % of the carriers recombine at defects, 44 % radiatively and 43 % by Auger; above \(B/C = 3.3\times10^{18}\) cm\(^{-3}\) Auger takes the largest share. Drawn by <code>figsrc/ch23_figs.py</code>.</figcaption>
</figure>

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
