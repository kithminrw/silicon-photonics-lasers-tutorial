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
- measure propagation loss with cutbacks, spirals and resonators, with an error bar.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What limits a waveguide's propagation loss, and how do you measure it reliably?

</div>

## <span class="secnum">7.1</span>Loss mechanisms and units

A guided mode loses power exponentially, $$P(z) = P(0)\,e^{-\alpha z}$$, and its loss is quoted in dB per unit length, $$\alpha_\mathrm{dB} = 4.343\,\alpha$$ ([Chapter 2]({% link chapters/02_em.md %})). Silicon strip waveguides lose typically 1–3 dB/cm, rib waveguides and wider strips less than 1 dB/cm, and low-confinement silicon nitride down to about 0.1 dB/m {% include cite.html keys="blumenthal2018" %}. On a chip a few millimetres across, 2 dB/cm is a small part of the budget; in a delay line, a long spiral or a high-Q resonator it dominates.

The loss has four sources, and the rest of the chapter takes them in turn: **scattering** from rough sidewalls, **absorption** in the materials and in anything doped or metallic near the mode, **leakage** into the substrate through a finite buried oxide, and **radiation** from bends and discontinuities ([Chapter 8]({% link chapters/08_bends.md %})).

## <span class="secnum">7.2</span>Sidewall-roughness scattering

Etching never leaves a perfectly smooth sidewall. Its edge wanders by a few nanometres (the rms roughness $$\sigma$$) over a correlation length $$L_c$$ of tens of nanometres, and each bump acts as a small dipole that radiates part of the guided light out of the waveguide. Payne and Lacey derived the loss of a slab with such roughness {% include cite.html keys="payne1994" %}; its essential scaling is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Scattering loss scaling</div>

$$\alpha_\mathrm{scat} \propto \sigma^2\,\left(n_1^2 - n_2^2\right)^2\,\lvert E_s\rvert^2\,F(L_c),$$

</div>

where $$E_s$$ is the normalised mode field at the sidewall and $$F$$ a function of the correlation length that peaks when the roughness spectrum couples the mode efficiently to radiation. Three design rules follow:

- **Roughness counts twice.** Halving $$\sigma$$ cuts the loss by four; this is why lithography and etch quality matter so much.
- **Index contrast is expensive.** The $$(n_1^2 - n_2^2)^2$$ factor is about 28 times larger for silicon in oxide than for silicon nitride in oxide, which is the main reason SiN waveguides are so much less lossy.
- **Keep the field away from the sidewall.** Widening a silicon strip from 500 nm to 1–3 µm lowers the field at its edges and cuts the loss several-fold. Wide waveguides are multimode, so they are used for long straight runs, entered and left through adiabatic tapers ([Chapter 8]({% link chapters/08_bends.md %})). A rib waveguide, whose shallow etch leaves only a small sidewall, achieves the same.

Polarisation matters too. A TE mode in a strip has its strongest field at the etched sidewalls, while a TM mode concentrates at the top and bottom surfaces, which are the polished film and buried-oxide interfaces and are far smoother. For the same cross-section the TM mode therefore scatters less, but it is less confined and leaks and bends worse (Sections 7.4 and 8.1).

## <span class="secnum">7.3</span>Absorption

Undoped silicon and silica are transparent at 1310 and 1550 nm, but any free carriers absorb. In silicon at 1550 nm the free-carrier absorption is {% include cite.html keys="soref1987" %}

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Free-carrier absorption in silicon at 1550 nm</div>

$$\Delta\alpha\ [\mathrm{cm^{-1}}] = 8.5\times10^{-18}\,\Delta N_e + 6.0\times10^{-18}\,\Delta N_h \quad (\text{carrier densities in cm}^{-3})$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.1 · The cost of doping</div>

A p-type region doped to $$10^{18}\ \mathrm{cm^{-3}}$$ absorbs $$6.0\times10^{-18}\times10^{18} = 6\ \mathrm{cm^{-1}}$$, or $$4.343\times6 = 26$$ dB/cm, for the fraction of the mode that overlaps it. A depletion modulator ([Chapter 20]({% link chapters/20_modulators.md %})) dopes its waveguide to around this level on purpose, which is why its insertion loss is several dB even though it is only millimetres long, and why contacts are placed on heavily doped regions kept well away from the mode.

</div>

Metals absorb much more strongly. Heaters and electrodes are therefore kept a micrometre or more above or beside the waveguide ([Chapter 18]({% link chapters/18_thermal.md %})), so that the evanescent tail, decaying over about 100 nm, has vanished before it reaches them.

## <span class="secnum">7.4</span>Substrate leakage

The buried oxide separates the waveguide from the silicon handle wafer, which has a higher index than the mode's effective index. Wherever the evanescent tail reaches the handle, light tunnels into it and is lost. The tail decays as $$e^{-\gamma x}$$ with $$\gamma = k_0\sqrt{n_\mathrm{eff}^2 - n_\mathrm{ox}^2}$$, so the leaked power scales as

$$\alpha_\mathrm{leak} \propto e^{-2\gamma t_\mathrm{BOX}}.$$

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.2 · How thick must the buried oxide be?</div>

For a 500 × 220 nm strip at 1550 nm, the TE mode has $$n_\mathrm{eff} = 2.446$$ ([Chapter 6]({% link chapters/06_soi.md %})), so $$\gamma = (2\pi/1.55)\sqrt{2.446^2 - 1.444^2} = 8.0\ \mu\mathrm{m}^{-1}$$. Every extra 100 nm of oxide reduces the leakage by $$e^{2\times8.0\times0.1} = 5$$, or 7 dB. The TM mode ($$n_\mathrm{eff} = 1.77$$) has $$\gamma = 4.2\ \mu\mathrm{m}^{-1}$$, and gains only 3.6 dB per 100 nm: it leaks far more for the same oxide. At 1310 nm the TE mode is more confined ($$\gamma = 11\ \mu\mathrm{m}^{-1}$$, 9.6 dB per 100 nm). This is why a 2 µm BOX is enough for TE at 1550 nm, while TM devices, longer wavelengths and weakly confined modes (narrow tapers, grating couplers) call for 3 µm.

</div>

## <span class="secnum">7.5</span>Dispersion

The group index varies with wavelength, and so pulses spread: the group-velocity dispersion $$\beta_2 = \mathrm{d}^2\beta/\mathrm{d}\omega^2$$ of [Chapter 2]({% link chapters/02_em.md %}). In a silicon wire, waveguide dispersion is so strong that $$\beta_2$$ is orders of magnitude larger than in fibre, and its sign and size can be tuned by the cross-section: wider and thicker guides move towards the material's normal dispersion, narrow ones towards anomalous. For a few millimetres of waveguide carrying tens of gigabits per second this is negligible. It matters for long delay lines and, above all, for nonlinear optics, where the phase matching of four-wave mixing and the formation of frequency combs require anomalous dispersion, engineered with the waveguide's width and thickness, especially in thick silicon nitride.

What does matter in every interferometric device is the **group index** itself, which sets free spectral ranges and time delays ([Chapters 11–12]({% link chapters/11_mzi.md %})).

## <span class="secnum">7.6</span>Nonlinear effects

A milliwatt in a silicon wire is about 1 MW/cm² ([Chapter 2]({% link chapters/02_em.md %})), and at such intensities three nonlinear effects appear:

- **The Kerr effect** changes the index in proportion to intensity, $$\Delta n = n_2I$$, with $$n_2 \approx 6\times10^{-18}\ \mathrm{m^2/W}$$ in silicon and about $$2.5\times10^{-19}\ \mathrm{m^2/W}$$ in silicon nitride. It causes self-phase modulation and drives four-wave mixing.
- **Two-photon absorption** (TPA): at 1550 nm two photons together (1.6 eV) exceed silicon's 1.12 eV bandgap, so silicon absorbs in proportion to intensity, $$\alpha_\mathrm{TPA} = \beta_\mathrm{TPA}I$$, with $$\beta_\mathrm{TPA}$$ of about 0.5–1 cm/GW.
- **Free-carrier absorption from TPA**: each absorbed pair of photons creates an electron–hole pair, which absorbs further (Section 7.3) until it recombines, after a lifetime of nanoseconds or less.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 7.3 · When does silicon become nonlinear?</div>

With an effective area of 0.1 µm² ($$10^{-9}\ \mathrm{cm^2}$$), 100 mW gives $$I = 0.1/10^{-9} = 10^8\ \mathrm{W/cm^2} = 0.1\ \mathrm{GW/cm^2}$$, so $$\alpha_\mathrm{TPA} \approx 0.7 \times 0.1 = 0.07\ \mathrm{cm^{-1}}$$, or 0.3 dB/cm: comparable to the linear loss. At 1 W it is ten times more, plus the free-carrier absorption it creates. Silicon waveguides therefore saturate at a few hundred milliwatts, while silicon nitride, with no TPA at telecom wavelengths, carries watts. This is one reason high-power and nonlinear photonics favour SiN ([Chapter 4]({% link chapters/04_platforms.md %})).

</div>

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

On your first chip, the cutback set is the reference everything else is measured against: put at least four lengths spanning a centimetre or more between identical couplers, and add a ring or two as an independent check. [Chapter 32]({% link chapters/32_analysis.md %}) fits real openEBL data this way.

</div>

## Reading

{% include reflist.html keys="payne1994,soref1987,shi2012,chrostowski2015,blumenthal2018" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Silicon strips lose 1–3 dB/cm, mostly to sidewall scattering, which grows as $$\sigma^2(n_1^2 - n_2^2)^2$$ and with the field at the sidewall; wide strips, ribs and SiN lose less.
- Free carriers absorb: $$10^{18}\ \mathrm{cm^{-3}}$$ of holes costs about 26 dB/cm of overlapping mode. Keep doping and metal away from the light.
- Substrate leakage falls as $$e^{-2\gamma t_\mathrm{BOX}}$$: 7 dB per 100 nm of BOX for TE at 1550 nm, only 3.6 dB for TM.
- Silicon becomes nonlinear at tens to hundreds of milliwatts (Kerr, two-photon and free-carrier absorption); SiN does not absorb two photons at 1550 nm.
- Measure loss by cutback with several lengths and an error bar, and confirm it with a ring.

</div>
