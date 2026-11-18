---
title: "26. Single-Frequency and Tunable Lasers"
parent: "Part VI · Lasers and Amplifiers"
nav_order: 26
permalink: /part-6/ch26/
chapter: 26
---

# <span class="chapnum">Chapter 26</span>Single-Frequency and Tunable Lasers

Telecom, LiDAR and sensing need one clean wavelength, often tunable, and gratings and rings give lasers that selectivity.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- design DFB lasers (κL, the quarter-wave shift, side-mode suppression);
- explain DBR lasers, tuning sections and mode hops;
- design external-cavity lasers with silicon and SiN ring filters;
- use the Vernier effect to extend the tuning range;
- explain self-injection locking and multi-wavelength sources for WDM.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do two rings select one lasing mode over a 40 nm range?

</div>

## <span class="secnum">26.1</span>Why single-frequency

A Fabry–Pérot laser spreads its power over several modes a nanometre apart ([Chapter 24]({% link chapters/24_fp.md %})). That is a problem in three ways. Fibre dispersion delays each mode differently and smears the pulses. WDM needs each channel in its own slot ([Chapter 14]({% link chapters/14_wdm.md %})). Coherent detection and FMCW sensing need one stable frequency to beat against. A **single-frequency laser** adds a wavelength-selective element that gives one mode clearly more net gain than all the others. Its quality is measured by the **side-mode suppression ratio** (SMSR), the power in the lasing mode over the strongest other mode: 35 dB or more for telecom.

## <span class="secnum">26.2</span>DFB lasers

A **distributed-feedback** (DFB) laser etches a Bragg grating ([Chapter 13]({% link chapters/13_bragg.md %})) along the whole gain section, so feedback is distributed along the cavity instead of coming from the facets. Its strength is the coupling–length product $$\kappa L$$, usually between 1 and 3: weaker and the threshold is high, stronger and the light piles up in the middle of the cavity, burning holes in the carrier density.

A uniform grating has a stop band with two equally good modes, one at each edge, so a uniform DFB laser may lase on either. A **quarter-wave shift** in the middle of the grating opens a single resonance at the centre of the stop band (as in the Bragg demo of Chapter 13). That gives one mode at the Bragg wavelength with a large gain margin over the rest, and an SMSR of 40–50 dB. With AR-coated facets, the λ/4-shifted DFB is the workhorse source of telecom and datacom. Its wavelength is fixed by the grating period and tunes only with temperature, at about 0.1 nm/K: the index changes, the gain peak does not matter.

## <span class="secnum">26.3</span>DBR lasers and tuning

A **distributed Bragg reflector** (DBR) laser separates the functions: a gain section, a passive **phase section** and a passive **Bragg mirror** section. Injecting current into the passive Bragg section lowers its index (free carriers, [Chapter 19]({% link chapters/19_eo.md %})) and moves the mirror's reflection peak by several nanometres; heaters move it the other way. The cavity modes move too, but not in step, so the lasing mode **hops** from one cavity mode to the next as the mirror peak passes them. The phase section moves the cavity modes on their own, so that together the two currents give continuous tuning.

The tuning range of a single Bragg mirror is limited by the index change, a few nanometres. **Sampled-grating DBR** lasers use two mirrors with comb-like reflection spectra of slightly different periods, and tune over 40 nm by the Vernier effect of Section 26.5.

## <span class="secnum">26.4</span>External-cavity lasers on Si and SiN

Silicon photonics offers another split: put the gain in a III–V chip and the wavelength selection in silicon or silicon nitride. A **reflective SOA** (gain chip with a high-reflection rear facet and an angled, AR-coated front) is butt-coupled, flip-chipped or bonded to a passive circuit of ring filters and a loop mirror ([Chapter 27]({% link chapters/27_lasersonsi.md %})). The passive circuit does three things a III–V chip cannot:

- **low loss over a long path**, which stores light longer and narrows the linewidth ([Chapter 25]({% link chapters/25_dynamics.md %}));
- **high-finesse ring filters**, sharper than any grating in a few square micrometres;
- **efficient heaters**, which tune the filters over their whole free spectral range for tens of milliwatts ([Chapter 18]({% link chapters/18_thermal.md %})).

Silicon nitride adds still lower loss, a smaller thermo-optic coefficient (more stable filters) and no two-photon absorption at high power {% include cite.html keys="xiang2021" %}.

## <span class="secnum">26.5</span>The Vernier effect

A single ring has many resonances one FSR apart. The gain spectrum is much wider than an FSR, so a ring alone does not pick a single mode. Two rings of slightly different radii in series pass light only where a resonance of each coincides. Like the two scales of a Vernier calliper, they line up only at intervals much larger than either FSR:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Vernier free spectral range</div>

$$\mathrm{FSR}_V = \frac{\mathrm{FSR}_1\,\mathrm{FSR}_2}{\lvert\mathrm{FSR}_1 - \mathrm{FSR}_2\rvert}$$

</div>

Heating one ring slides its comb against the other, and the coincidence jumps from one pair of resonances to the next. Moving a ring by only $$\lvert\mathrm{FSR}_1 - \mathrm{FSR}_2\rvert$$ moves the lasing wavelength by a whole FSR, a gearing of $$\mathrm{FSR}/\Delta\mathrm{FSR}$$. Tuning both rings together moves the coincidence continuously.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 26.1 · Two silicon rings for 40 nm of tuning</div>

With $$n_g = 4.18$$, rings of 10 and 11 µm radius have FSRs of 9.148 and 8.316 nm, so $$\mathrm{FSR}_V = 9.148 \times 8.316/0.832 \approx 91$$ nm: one coincidence across more than the gain bandwidth, which covers a 40 nm range with margin. Shifting ring 2 by 0.83 nm, about 5 mW with the TiN heaters of Chapter 18 (0.18 nm/mW for a ring with a 9.15 nm FSR), moves the lasing wavelength by 9.15 nm, a gearing of 11. The price of such a large gearing is selectivity: the neighbouring coincidences, one FSR away, are only slightly misaligned, so the rings' resonances must be narrow (low coupling) for a good SMSR. The demo shows the trade.

</div>

**Try it.** Change the two radii and the heaters, and watch the combined filter pick one cavity mode under the gain.

{% include demos/vernier.html %}

## <span class="secnum">26.6</span>Self-injection locking

Feed a semiconductor laser with light reflected back from a very high-Q resonator, and the laser locks to the resonator's frequency, inheriting its stability. In chip-scale versions, the ring's own backscatter provides the feedback. Silicon-nitride rings with intrinsic Q in the tens of millions, coupled to III–V lasers, have narrowed the fundamental linewidth to below a kilohertz {% include cite.html keys="xiang2021" %}. Such lasers are the sources for coherent communication, FMCW LiDAR, microwave photonics and atomic sensors ([Chapter 34]({% link chapters/34_apps.md %})).

## <span class="secnum">26.7</span>Multi-wavelength sources

A WDM transceiver needs several wavelengths:

- **laser arrays**: separate DFB lasers, one per channel, bonded or flip-chipped, each with its own temperature and current;
- **comb sources**: one laser producing many equally spaced lines. Mode-locked quantum-dot lasers, and Kerr combs generated in SiN microrings by four-wave mixing, give tens of lines on a fixed grid, which a demultiplexer separates.

Combs are attractive for dense WDM because the lines move together, so one control loop tracks them all; the price is lower power per line.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Four λ/4-shifted DFB lasers at 400 GHz spacing, one per channel, with the ring modulators and drop filters locked to them ([Chapter 18]({% link chapters/18_thermal.md %})). A comb source is the natural upgrade path to more channels.

</div>

## Reading

{% include reflist.html keys="coldren,komljenovic2016,xiang2021" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Single-frequency lasers need a wavelength-selective element and an SMSR of 35 dB or more.
- λ/4-shifted DFB lasers (κL ≈ 1–3) are the telecom workhorse; they tune only with temperature, about 0.1 nm/K.
- DBR lasers tune with current or heat in the mirror and phase sections, with mode hops unless the phase is controlled.
- External-cavity lasers combine III–V gain with low-loss Si or SiN filters for wide tuning and narrow lines.
- Two rings give $$\mathrm{FSR}_V = \mathrm{FSR}_1\mathrm{FSR}_2/\lvert\Delta\mathrm{FSR}\rvert$$: 91 nm for 10 and 11 µm silicon rings, with a tuning gearing of 11.

</div>
