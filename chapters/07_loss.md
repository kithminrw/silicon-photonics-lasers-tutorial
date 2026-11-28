---
title: "7. Loss, Dispersion and Nonlinearity"
parent: "Part II · Waveguides"
nav_order: 7
permalink: /part-2/ch07/
chapter: 7
---

# <span class="chapnum">Chapter 7</span>Loss, Dispersion and Nonlinearity

A waveguide's job is to get light from A to B unchanged; this chapter is about everything that gets in the way.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- classify the loss mechanisms of a waveguide: sidewall scattering, absorption, substrate leakage and radiation;
- explain how scattering loss scales with roughness, width and polarisation;
- estimate free-carrier absorption from doping and the leakage through a buried oxide;
- describe dispersion and the nonlinear effects that matter in silicon at 1550 nm;
- measure propagation loss with cutbacks, spirals and resonators, with an error bar;
- explain phase matching, quasi-phase-matching by periodic poling, and how a microring makes a Kerr frequency comb.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What limits a waveguide's propagation loss, and how do you measure it reliably?

</div>

## <span class="secnum">7.1</span>Loss mechanisms and units

A guided mode loses power exponentially, $$P(z) = P(0)\,e^{-\alpha z}$$, and its loss is quoted in dB per unit length, $$\alpha_\mathrm{dB} = 4.343\,\alpha$$ ([Chapter 2]({% link chapters/02_em.md %})). Silicon strip waveguides lose typically 1–3 dB/cm, rib waveguides and wider strips less than 1 dB/cm, and low-confinement silicon nitride down to about 0.1 dB/m {% include cite.html keys="blumenthal2018" %}. On a chip a few millimetres across, 2 dB/cm is a small part of the budget; in a delay line, a long spiral or a high-Q resonator it dominates.

The loss has four sources, and the rest of the chapter takes them in turn: **scattering** from rough sidewalls, **absorption** in the materials and in anything doped or metallic near the mode, **leakage** into the substrate through a finite buried oxide, and **radiation** from bends and discontinuities ([Chapter 8]({% link chapters/08_bends.md %})), as sketched in [Figure 7.1](#fig-7-1).

<figure id="fig-7-1">
  <img src="{{ '/assets/figs/ch07_mechanisms.svg' | relative_url }}" style="width:600px" alt="Cross-section of a silicon strip on a 2 micrometre buried oxide with a heater above, showing sidewall scattering, absorption in metal, substrate leakage through the oxide and absorption in the core; and a top view of a rough waveguide entering a bend that radiates on its outer side">
  <figcaption><span class="capnum">Figure 7.1.</span> <strong>Where a waveguide loses light.</strong> (a) Cross-section of a strip, not to scale: the core and its TE0 intensity contours (5, 25, 50 and 80 % of the peak, femwell, 500 × 220 nm strip) are enlarged three times and the buried oxide is shortened. Rough sidewalls (exaggerated) scatter light out, where the field normal to them jumps up (the small loops just outside the core); the evanescent tail is absorbed wherever it meets metal or doped silicon, and tunnels through the buried oxide into the silicon substrate; free carriers and two-photon absorption act inside the core. (b) Top view to scale: the sidewalls scatter along the whole length, and a 2 µm bend radiates from its outer side. Drawn by <code>figsrc/ch07_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">7.2</span>Sidewall-roughness scattering

Etching never leaves a perfectly smooth sidewall. Its edge wanders by a few nanometres (the rms roughness $$\sigma$$) over a correlation length $$L_c$$ of tens of nanometres, and each bump acts as a small dipole that radiates part of the guided light out of the waveguide. Payne and Lacey derived the loss of a slab with such roughness {% include cite.html keys="payne1994" %}; its essential scaling is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Scattering loss scaling</div>

$$\alpha_\mathrm{scat} \propto \sigma^2\,\left(n_1^2 - n_2^2\right)^2\,\lvert E_s\rvert^2\,F(L_c),$$

</div>

where $$E_s$$ is the normalised mode field at the sidewall and $$F$$ a function of the correlation length that peaks when the roughness spectrum couples the mode efficiently to radiation. Three design rules follow:

- **Roughness counts twice.** Halving $$\sigma$$ cuts the loss by four; this is why lithography and etch quality matter so much.
- **Index contrast is expensive.** The $$(n_1^2 - n_2^2)^2$$ factor is about 28 times larger for silicon in oxide than for silicon nitride in oxide, which is the main reason SiN waveguides are so much less lossy.
- **Keep the field away from the sidewall.** Widening a silicon strip from 500 nm to 1–3 µm lowers the field at its edges, which cuts the sidewall scattering 5-fold at 1 µm and 30-fold at 2 µm, and the measured loss several-fold ([Figure 7.2](#fig-7-2)). Wide waveguides are multimode, so they are used for long straight runs, entered and left through adiabatic tapers ([Chapter 8]({% link chapters/08_bends.md %})). A rib waveguide, whose shallow etch leaves only a small sidewall, achieves the same.

<figure id="fig-7-2">
  <img src="{{ '/assets/figs/ch07_scattering.svg' | relative_url }}" style="width:600px" alt="Lateral intensity profiles of the fundamental mode for 500 nanometre, 1 and 2 micrometre wide strips with the sidewall values marked, and the relative sidewall-scattering loss against width falling to 0.20 at 1 micrometre, 0.033 at 2 and 0.011 at 3">
  <figcaption><span class="capnum">Figure 7.2.</span> <strong>Why wider strips scatter less.</strong> The Payne–Lacey model applied to the lateral slab of the effective-index method (core index 2.848 from the 220 nm film, oxide either side) {% include cite.html keys="payne1994" %}. (a) Lateral \(|E|^2\) of the fundamental mode, normalised to unit power, for three widths; the dots mark the field at the sidewalls, which falls from 0.55 µm\(^{-1}\) at 500 nm to 0.11 at 1 µm and 0.019 at 2 µm. (b) Sidewall-scattering loss relative to the 500 nm strip: 0.20 at 1 µm, 0.033 at 2 µm and 0.011 at 3 µm, the same within 5 % for correlation lengths from 20 to 100 nm and set almost entirely by \(|E_s|^2\) (dotted). This is the sidewall contribution only: top-surface roughness and absorption do not fall with width, which is why measured losses fall several-fold rather than by these factors. Drawn by <code>figsrc/ch07_figs.py</code>.</figcaption>
</figure>

**Try it.** Widen the strip and watch the field at its sidewalls fall, and the scattering loss with it; then change the roughness, its correlation length, the wavelength and the cladding. The top view shows the light that the rough walls scatter out of the guide.

{% include demos/roughness.html %}

Polarisation matters too. A TE mode in a strip has its strongest field at the etched sidewalls, while a TM mode concentrates at the top and bottom surfaces, which are the polished film and buried-oxide interfaces and are far smoother. For the same cross-section the TM mode therefore scatters less, but it is less confined and leaks and bends worse (Sections 7.4 and 8.1).

## <span class="secnum">7.3</span>Absorption

Undoped silicon and silica are transparent at 1310 and 1550 nm, but any free carriers absorb ([Figure 7.3](#fig-7-3)). In silicon at 1550 nm the free-carrier absorption is {% include cite.html keys="soref1987" %}

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Free-carrier absorption in silicon at 1550 nm</div>

$$\Delta\alpha\ [\mathrm{cm^{-1}}] = 8.5\times10^{-18}\,\Delta N_e + 6.0\times10^{-18}\,\Delta N_h \quad (\text{carrier densities in cm}^{-3})$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.1 · The cost of doping</div>

A p-type region doped to $$10^{18}\ \mathrm{cm^{-3}}$$ absorbs $$6.0\times10^{-18}\times10^{18} = 6\ \mathrm{cm^{-1}}$$, or $$4.343\times6 = 26$$ dB/cm, for the fraction of the mode that overlaps it. A depletion modulator ([Chapter 20]({% link chapters/20_modulators.md %})) dopes its waveguide to around this level on purpose, which is why its insertion loss is several dB even though it is only millimetres long, and why contacts are placed on heavily doped regions kept well away from the mode.

</div>

<figure id="fig-7-3">
  <img src="{{ '/assets/figs/ch07_fca.svg' | relative_url }}" style="width:360px" alt="Free-carrier absorption in decibels per centimetre against carrier density on log axes for electrons and holes, with 26 dB/cm marked for holes at 10 to the 18 per cubic centimetre and shaded bands for modulator and contact doping">
  <figcaption><span class="capnum">Figure 7.3.</span> <strong>Free-carrier absorption in silicon at 1550 nm</strong>, from the coefficients above {% include cite.html keys="soref1987" %}. \(10^{18}\ \mathrm{cm^{-3}}\) of holes absorb 26 dB/cm, of electrons 37 dB/cm. Shaded: the doping of depletion modulators (\(5\times10^{17}\)–\(10^{18}\ \mathrm{cm^{-3}}\), Chapter 19) and typical heavily doped contact regions (\(10^{19}\)–\(10^{20}\ \mathrm{cm^{-3}}\)), where the absorption reaches thousands of dB/cm. Drawn by <code>figsrc/ch07_figs.py</code>.</figcaption>
</figure>

Metals absorb much more strongly. Heaters and electrodes are therefore kept a micrometre or more above or beside the waveguide ([Chapter 18]({% link chapters/18_thermal.md %})), so that the evanescent tail, decaying over about 100 nm, has vanished before it reaches them.

## <span class="secnum">7.4</span>Substrate leakage

The buried oxide separates the waveguide from the silicon handle wafer, which has a higher index than the mode's effective index. Wherever the evanescent tail reaches the handle, light tunnels into it and is lost ([Figure 7.4](#fig-7-4)). The tail decays as $$e^{-\gamma x}$$ with $$\gamma = k_0\sqrt{n_\mathrm{eff}^2 - n_\mathrm{ox}^2}$$, so the leaked power scales as

$$\alpha_\mathrm{leak} \propto e^{-2\gamma t_\mathrm{BOX}}.$$

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.2 · How thick must the buried oxide be?</div>

For a 500 × 220 nm strip at 1550 nm, the TE mode has $$n_\mathrm{eff} = 2.446$$ ([Chapter 6]({% link chapters/06_soi.md %})), so $$\gamma = (2\pi/1.55)\sqrt{2.446^2 - 1.444^2} = 8.0\ \mu\mathrm{m}^{-1}$$. Every extra 100 nm of oxide reduces the leakage by $$e^{2\times8.0\times0.1} = 5$$, or 7 dB. The TM mode ($$n_\mathrm{eff} = 1.77$$) has $$\gamma = 4.2\ \mu\mathrm{m}^{-1}$$, and gains only 3.6 dB per 100 nm: it leaks far more for the same oxide. At 1310 nm the TE mode is more confined ($$\gamma = 11\ \mu\mathrm{m}^{-1}$$, 9.6 dB per 100 nm). This is why a 2 µm BOX is enough for TE at 1550 nm, while weakly confined modes (TM in narrow strips, longer wavelengths, narrow tapers, grating couplers) call for 3 µm; the 500 nm strip's own TM mode leaks only about 0.002 dB/cm through 2 µm ([Lab 2]({% link labs/lab02_femwell.md %})).

</div>

<figure id="fig-7-4">
  <img src="{{ '/assets/figs/ch07_leakage.svg' | relative_url }}" style="width:600px" alt="Left: the tail intensity of the strip mode decaying in decibels through a 2 micrometre buried oxide, reaching the substrate 139 dB down for TE at 1550 nm, 191 dB for TE at 1310 nm and 72 dB for TM. Right: substrate leakage in dB/cm against BOX thickness on a log scale for the three cases">
  <figcaption><span class="capnum">Figure 7.4.</span> <strong>Substrate leakage through the buried oxide</strong> (500 × 220 nm strip). (a) The evanescent tail decays as \(e^{-2\gamma x}\) and reaches the substrate under a 2 µm BOX 139 dB down for TE at 1550 nm (\(\gamma = 8.0\ \mu\mathrm{m}^{-1}\)), 191 dB down at 1310 nm, but only 72 dB down for TM (\(\gamma = 4.2\ \mu\mathrm{m}^{-1}\)). (b) Leakage loss against BOX thickness from a one-dimensional leaky-mode calculation: a film over the BOX and the silicon substrate, its index chosen so that the mode has the strip's effective index (2.446 TE, 1.771 TM, 2.712 TE at 1310 nm), with an outgoing wave in the substrate. The slopes are the 7, 3.6 and 9.6 dB per 100 nm of Worked Example 7.2. With 1 µm of BOX, TE loses 0.015 dB/cm and TM 25 dB/cm; with 2 µm, TE less than \(10^{-8}\) dB/cm and TM 0.006 dB/cm. This one-dimensional model leaks two to three times faster than the full strip: femwell gives TM 12 dB/cm through 1 µm and 0.002 dB/cm through 2 µm (Worked Example 7.2, Lab 2). Modes closer to the oxide index leak faster still. Drawn by <code>figsrc/ch07_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">7.5</span>Dispersion

The group index varies with wavelength, and so pulses spread: the group-velocity dispersion $$\beta_2 = \mathrm{d}^2\beta/\mathrm{d}\omega^2$$ of [Chapter 2]({% link chapters/02_em.md %}). In a silicon wire, waveguide dispersion is so strong that $$\beta_2$$ is orders of magnitude larger than in fibre, and its sign and size can be tuned by the cross-section: wider and thicker guides move towards the material's normal dispersion, narrow ones towards anomalous. For a few millimetres of waveguide carrying tens of gigabits per second this is negligible. It matters for long delay lines and, above all, for nonlinear optics, where the phase matching of four-wave mixing and the formation of frequency combs require anomalous dispersion, engineered with the waveguide's width and thickness, especially in thick silicon nitride.

What does matter in every interferometric device is the **group index** itself, which sets free spectral ranges and time delays ([Chapters 11–12]({% link chapters/11_mzi.md %})).

## <span class="secnum">7.6</span>Nonlinear effects

A milliwatt in a silicon wire is about 1 MW/cm² ([Chapter 2]({% link chapters/02_em.md %})), and at such intensities three nonlinear effects appear ([Figure 7.5](#fig-7-5)):

- **The Kerr effect** changes the index in proportion to intensity, $$\Delta n = n_2I$$, with $$n_2 \approx 6\times10^{-18}\ \mathrm{m^2/W}$$ in silicon and about $$2.5\times10^{-19}\ \mathrm{m^2/W}$$ in silicon nitride. It causes self-phase modulation and drives four-wave mixing.
- **Two-photon absorption** (TPA): at 1550 nm two photons together (1.6 eV) exceed silicon's 1.12 eV bandgap, so silicon absorbs in proportion to intensity, $$\alpha_\mathrm{TPA} = \beta_\mathrm{TPA}I$$, with $$\beta_\mathrm{TPA}$$ of about 0.5–1 cm/GW.
- **Free-carrier absorption from TPA**: each absorbed pair of photons creates an electron–hole pair, which absorbs further (Section 7.3) until it recombines, after a lifetime of nanoseconds or less.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.3 · When does silicon become nonlinear?</div>

With an effective area of 0.1 µm² ($$10^{-9}\ \mathrm{cm^2}$$), 100 mW gives $$I = 0.1/10^{-9} = 10^8\ \mathrm{W/cm^2} = 0.1\ \mathrm{GW/cm^2}$$, so $$\alpha_\mathrm{TPA} \approx 0.7 \times 0.1 = 0.07\ \mathrm{cm^{-1}}$$, or 0.3 dB/cm: comparable to the linear loss. At 1 W it is ten times more, plus the free-carrier absorption it creates. Silicon waveguides therefore saturate: after 1 cm the output levels off near 80 mW for a 1 ns carrier lifetime and 230 mW for 0.1 ns ([Figure 7.5](#fig-7-5)), while silicon nitride, with no TPA at telecom wavelengths, carries watts. This is one reason high-power and nonlinear photonics favour SiN ([Chapter 4]({% link chapters/04_platforms.md %})).

</div>

<figure id="fig-7-5">
  <img src="{{ '/assets/figs/ch07_tpa.svg' | relative_url }}" style="width:600px" alt="Left: two-photon absorption and the free-carrier absorption it causes against power from 1 milliwatt to 1 watt, compared with the linear loss band of 1 to 3 dB/cm. Right: output power after 1 cm of silicon wire against input power, saturating near 80 to 230 mW, against a straight line for linear loss only">
  <figcaption><span class="capnum">Figure 7.5.</span> <strong>Two-photon absorption limits the power in a silicon wire</strong> (\(A_\mathrm{eff} = 0.1\ \mu\mathrm{m}^2\), 1550 nm, as in Worked Example 7.3). (a) Loss against power. TPA with \(\beta_\mathrm{TPA} = 0.7\) cm/GW (dotted: 0.5 and 1 cm/GW) gives 0.3 dB/cm at 100 mW and 3 dB/cm at 1 W. The free carriers it creates (one electron and one hole per absorbed pair, absorbing as in Section 7.3) grow with the square of the power: 1.7 dB/cm at 100 mW for a carrier lifetime of 1 ns, 0.17 dB/cm for 0.1 ns. (b) Output after 1 cm of wire with 2 dB/cm of linear loss: it saturates near 80 mW (1 ns) or 230 mW (0.1 ns), while a waveguide without TPA, such as SiN, stays linear. Drawn by <code>figsrc/ch07_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">7.7</span>Measuring loss

Loss is small per millimetre and the fibre couplers are large and variable, so measuring it takes care. Four methods are common:

- **Cutback.** Measure several waveguides of different lengths, each between identical grating couplers, and fit insertion loss against length: the slope is the propagation loss and the intercept twice the coupler loss. Coupler-to-coupler variation is the main error, and it averages down with more structures and longer lengths.
- **Spirals.** Folding centimetres of waveguide into a compact spiral gives a large length span on a small area, at the cost of including some bend loss.
- **Resonators.** The intrinsic Q of a ring depends only on the propagation loss, $$Q_i = 2\pi n_g/(\lambda\alpha)$$ ([Chapter 12]({% link chapters/12_rings.md %})), so fitting a ring's resonance measures loss in a few hundred micrometres, independently of the couplers {% include cite.html keys="shi2012" %}.
- **Reflectometry.** Optical frequency-domain reflectometry maps the backscatter along a waveguide and reads the loss from its decay.

**Try it.** Measure the loss of a chip by cutback; change the number of structures, their lengths and the coupler variation, and watch the error bar.

{% include demos/cutback.html %}

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

On your first chip, the cutback set is the reference everything else is measured against: put at least four lengths spanning a centimetre or more between identical couplers, and add a ring or two as an independent check. [Chapter 37]({% link chapters/37_analysis.md %}) fits real openEBL data this way.

</div>

## <span class="secnum">7.8</span>Nonlinear devices: frequency conversion and microcombs

The effects of Section 7.6 are a nuisance in a transmitter. Designed for, they make light at new frequencies. Two families matter on chips.

**Second-order processes.** In materials without a centre of symmetry, such as lithium niobate, aluminium nitride, GaAs and BTO, the polarisation has a term in $$E^2$$ ($$\chi^{(2)}$$). Two photons at $$\omega$$ can merge into one at $$2\omega$$ (**second-harmonic generation**, SHG). Sum- and difference-frequency generation and optical parametric amplification work the same way. Silicon and silicon nitride are centrosymmetric and lack these processes ([Chapter 19]({% link chapters/19_eo.md %})). The difficulty is **phase matching**. The second harmonic made at each point adds in phase with what was made earlier only if $$n(2\omega) = n(\omega)$$, and dispersion forbids that. After a **coherence length** $$L_c = \lambda/[4(n_{2\omega} - n_\omega)]$$ the new light starts to cancel the old ([Figure 7.6](#fig-7-6)a). In bulk lithium niobate, for 1550 → 775 nm, $$L_c$$ is about 10 µm. **Quasi-phase-matching** flips the sign of the nonlinearity every coherence length by **periodic poling**: high-voltage pulses through patterned electrodes reverse the crystal's ferroelectric domains. The power then grows almost as if phase-matched, at $$(2/\pi)^2$$ of the ideal. In bulk the period would be about 21 µm. Thin-film LN waveguides add their own dispersion and need about 4 µm, but they confine the light so tightly that their efficiency rises by more than an order of magnitude: 2600 %/W/cm² was reported for SHG at 1550 nm {% include cite.html keys="wang2018ppln" %}.

**Third-order processes.** The Kerr effect is present in every material. In **four-wave mixing**, two pump photons become a signal and an idler photon placed symmetrically about the pump, $$2\omega_p = \omega_s + \omega_i$$. Its phase matching depends on the waveguide's group-velocity dispersion. Gain near the pump needs **anomalous** dispersion, which in silicon nitride means films about 800 nm thick or more, a dispersion-engineering task like those of [Chapter 6]({% link chapters/06_soi.md %}). In a high-Q ring the mixing feeds itself. Above a threshold pump power, the ring oscillates on the resonances on either side of the pump, the new lines mix further, and a **microcomb** grows: a row of lines exactly one FSR apart. Tuned carefully into the resonance, the comb can lock into a **dissipative Kerr soliton**: a single pulse circulating in the ring with a smooth sech² spectrum ([Figure 7.6](#fig-7-6)b) {% include cite.html keys="gaeta2019,kippenberg2004" %}. The threshold scales as

$$P_\mathrm{th} \propto \frac{n^2V_\mathrm{eff}}{n_2\,\lambda\,Q_L^2},$$

up to a factor of order one that depends on the coupling, with $$V_\mathrm{eff}$$ the mode volume. The $$Q^2$$ is why ultra-low-loss silicon nitride ([Chapter 4]({% link chapters/04_platforms.md %})) is the microcomb platform. Silicon's two-photon absorption (Section 7.6) rules it out at 1550 nm.

<figure id="fig-7-6">
  <img src="{{ '/assets/figs/ch07_nonlinear.svg' | relative_url }}" style="width:620px" alt="a: second-harmonic power against length in units of the coherence length: phase matched growing as the square of length, not phase matched oscillating near zero, and quasi-phase-matched growing in steps close to two over pi squared of the phase-matched curve. b: an illustrative soliton microcomb spectrum: lines 0.8 nanometres apart under a smooth envelope falling from minus 20 dB, with the pump line near 0 dB">
  <figcaption><span class="capnum">Figure 7.6.</span> <strong>Frequency conversion and microcombs.</strong> (a) Second-harmonic power along a waveguide (undepleted pump, arbitrary units). Without phase matching it grows for one coherence length and then cancels itself. Flipping the nonlinearity every \(L_c\) (periodic poling) makes it grow in steps that follow \((2/\pi)^2\) of the phase-matched curve (dashed). (b) An illustrative soliton microcomb: lines one FSR (100 GHz, 0.8 nm) apart under a sech² envelope, with the remaining pump on top. Drawn by <code>figsrc/ch07_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.4 · Two nonlinear devices on a chip</div>

- **Frequency doubling in thin-film LN.** With the reported 2600 %/W/cm² ($$\eta$$ = 26 W⁻¹ cm⁻²), an undepleted pump gives $$P_{2\omega} = \eta P_\omega^2L^2$$. For 10 mW in a 4 mm waveguide, $$P_{2\omega} = 26 \times 0.01^2 \times 0.4^2 = 0.42$$ mW, 4 % of the pump. At higher powers the pump depletes and the formula overestimates.
- **A 100 GHz microcomb in SiN.** An FSR of 100 GHz with $$n_g \approx 2.1$$ needs a round trip of $$c/(n_g\,\mathrm{FSR}) = 1.43$$ mm, a ring of 227 µm radius. With a 1 µm² mode, $$n \approx 1.9$$ and $$n_2 = 2.5\times10^{-19}$$ m²/W (Section 7.6), the scaling gives $$n^2V_\mathrm{eff}/(n_2\lambda Q_L^2) \approx 13$$ mW at $$Q_L = 10^6$$ and 0.13 mW at $$10^7$$. Each tenfold improvement in Q lowers the threshold a hundredfold.

</div>

Such sources serve the rest of the tutorial. A microcomb is a dense-WDM light source with lines locked together (Section 26.7 of [Chapter 26]({% link chapters/26_tunable.md %})), and a broadband source for LiDAR and spectroscopy. Below threshold, four-wave mixing makes pairs of single photons, the source of many integrated quantum-photonic circuits ([Chapter 39]({% link chapters/39_apps.md %})).

## Reading

{% include reflist.html keys="payne1994,soref1987,shi2012,chrostowski2015,blumenthal2018,wang2018ppln,gaeta2019,kippenberg2004" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Silicon strips lose 1–3 dB/cm, mostly to sidewall scattering, which grows as $$\sigma^2(n_1^2 - n_2^2)^2$$ and with the field at the sidewall; wide strips, ribs and SiN lose less.
- Free carriers absorb: $$10^{18}\ \mathrm{cm^{-3}}$$ of holes costs about 26 dB/cm of overlapping mode. Keep doping and metal away from the light.
- Substrate leakage falls as $$e^{-2\gamma t_\mathrm{BOX}}$$: 7 dB per 100 nm of BOX for TE at 1550 nm, only 3.6 dB for TM.
- Silicon becomes nonlinear at tens to hundreds of milliwatts (Kerr, two-photon and free-carrier absorption); SiN does not absorb two photons at 1550 nm.
- Measure loss by cutback with several lengths and an error bar, and confirm it with a ring.
- Designed nonlinear devices make new frequencies: periodically poled thin-film LN doubles 1550 nm light (quasi-phase-matching, about 4 µm periods), and high-Q SiN rings turn one pump into a microcomb above a threshold that falls as 1/Q².

</div>

## Problems

1. **Loss of a depletion phase shifter.** In a rib phase shifter, 30 % of the mode overlaps a p region with $$5\times10^{17}\ \mathrm{cm^{-3}}$$ holes and 30 % overlaps an n region with $$5\times10^{17}\ \mathrm{cm^{-3}}$$ electrons; ignore the depletion region. Find the free-carrier loss in dB/cm and over a 3 mm phase shifter. What fraction of the mode may overlap a $$10^{20}\ \mathrm{cm^{-3}}$$ p-type contact if that contact is to add no more than 0.1 dB/cm?

    <details markdown="1">
    <summary>Solution</summary>

    The holes absorb $$6.0\times10^{-18}\times5\times10^{17} = 3.0\ \mathrm{cm^{-1}}$$ and the electrons $$8.5\times10^{-18}\times5\times10^{17} = 4.25\ \mathrm{cm^{-1}}$$. Weighted by the overlaps, $$\alpha = 0.3\times3.0 + 0.3\times4.25 = 2.18\ \mathrm{cm^{-1}}$$, or $$4.343\times2.18 = 9.4$$ dB/cm, and 2.8 dB over 3 mm. The contact absorbs $$6.0\times10^{-18}\times10^{20} = 600\ \mathrm{cm^{-1}}$$, or 2600 dB/cm, so its overlap must stay below $$0.1/2600 = 3.8\times10^{-5}$$. The doped core costs almost 3 dB by design, while the contacts must sit where less than four parts in $$10^5$$ of the mode's power remain, which is why they are kept well away from it.

    </details>

2. **A cutback measurement.** Five waveguides between identical grating couplers are 0, 0.5, 1.0, 1.5 and 2.0 cm long and have insertion losses IL of 10.3, 11.6, 12.3, 13.6 and 14.4 dB. Fit a straight line by least squares to find the propagation loss with its standard error, and the loss of one coupler. What intrinsic Q should a ring made of the same waveguide show at 1550 nm ($$n_g = 4.18$$)?

    <details markdown="1">
    <summary>Solution</summary>

    The mean length is 1.0 cm and the mean loss 12.44 dB. The sums are $$\sum(L - \bar L)^2 = 2.5\ \mathrm{cm^2}$$ and $$\sum(L - \bar L)(\mathrm{IL} - \overline{\mathrm{IL}}) = 5.10\ \mathrm{dB\,cm}$$, so the slope is $$5.10/2.5 = 2.04$$ dB/cm and the intercept $$12.44 - 2.04\times1.0 = 10.40$$ dB, or 5.2 dB per coupler. The residuals are −0.10, +0.18, −0.14, +0.14 and −0.08 dB; their variance is $$s^2 = 0.088/(5 - 2) = 0.029\ \mathrm{dB^2}$$, and the slope's standard error $$\sqrt{s^2/2.5} = 0.11$$ dB/cm. The loss is therefore $$2.04 \pm 0.11$$ dB/cm, or $$\alpha = 2.04/4.343 = 0.47\ \mathrm{cm^{-1}}$$, and a ring should show

    $$Q_i = \frac{2\pi n_g}{\lambda\alpha} = \frac{2\pi\times4.18}{1.55\times10^{-4}\ \mathrm{cm}\times0.47\ \mathrm{cm^{-1}}} = 3.6\times10^5.$$

    A coupler-to-coupler scatter of about 0.15 dB leaves a 5 % uncertainty even over a 2 cm span; a ring with an intrinsic Q near $$3.6\times10^5$$ would confirm the number independently.

    </details>

3. **How thick a buried oxide for TM?** The one-dimensional model of Figure 7.4 gives 25 dB/cm of substrate leakage for the strip's TM mode through 1 µm of BOX, falling by 3.6 dB for every further 100 nm (Worked Example 7.2). Choose the BOX thickness that brings the TM leakage below 0.01 dB/cm. How does the answer change if you start from femwell's 12 dB/cm at 1 µm instead?

    <details markdown="1">
    <summary>Solution</summary>

    The leakage must fall by a factor $$25/0.01 = 2500$$, or $$10\log_{10}2500 = 34.0$$ dB. At 3.6 dB per 100 nm that takes 0.94 µm more oxide, so $$t_\mathrm{BOX} \approx 1.94$$ µm; $$e^{2\gamma\Delta t} = 2500$$ with $$\gamma = 4.2\ \mu\mathrm{m}^{-1}$$ gives the same within rounding. Choose 2 µm, where the model gives 0.006 dB/cm. From femwell's 12 dB/cm the factor is 1200, or 30.8 dB, which takes 0.86 µm, so 1.86 µm would do. The standard 2 µm BOX is just enough for the 500 nm strip's TM mode; a narrower strip or a longer wavelength, with a smaller $$\gamma$$, needs the 3 µm of Worked Example 7.2.

    </details>

4. **The coherence length.** In second-harmonic generation the pump at wavelength $$\lambda$$ has wavenumber $$k_\omega = 2\pi n_\omega/\lambda$$ and the harmonic $$k_{2\omega} = 2\pi n_{2\omega}/(\lambda/2)$$. Show that the harmonic made along the guide adds in phase over a length $$L_c = \lambda/[4(n_{2\omega} - n_\omega)]$$. Then use the numbers of Section 7.8, a coherence length of about 10 µm in bulk lithium niobate and a 4 µm poling period in thin film, to find the index mismatch in each case.

    <details markdown="1">
    <summary>Solution</summary>

    The pump drives a polarisation at $$2\omega$$ that varies as $$e^{-j2k_\omega z}$$, while the harmonic it radiates travels as $$e^{-jk_{2\omega}z}$$. Their relative phase grows as $$\Delta k\,z$$, with

    $$\Delta k = k_{2\omega} - 2k_\omega = \frac{4\pi}{\lambda}\left(n_{2\omega} - n_\omega\right).$$

    New light adds to the old while $$\Delta k\,z < \pi$$, so $$L_c = \pi/\Delta k = \lambda/[4(n_{2\omega} - n_\omega)]$$. In bulk, $$L_c \approx 10$$ µm gives $$n_{2\omega} - n_\omega = 1.55/(4\times10) = 0.039$$. In thin film, poling flips the sign every coherence length, so a 4 µm period means $$L_c = 2$$ µm and an effective-index mismatch of $$1.55/(4\times2) = 0.19$$. The waveguide adds its own dispersion to the material's, so the mismatch is five times larger and the poling period five times shorter.

    </details>

## Check yourself

{% include quiz.html %}
