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
- explain self-injection locking and multi-wavelength sources for WDM;
- explain mode locking: the repetition rate, the pulse width and the saturable absorber.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do two rings select one lasing mode over a 40 nm range?

</div>

## <span class="secnum">26.1</span>Why single-frequency

A Fabry–Pérot laser spreads its power over several modes a nanometre apart ([Chapter 24]({% link chapters/24_fp.md %})). That is a problem in three ways. Fibre dispersion delays each mode differently and smears the pulses. WDM needs each channel in its own slot ([Chapter 14]({% link chapters/14_wdm.md %})). Coherent detection and FMCW sensing need one stable frequency to beat against. A **single-frequency laser** adds a wavelength-selective element that gives one mode clearly more net gain than all the others. Its quality is measured by the **side-mode suppression ratio** (SMSR), the power in the lasing mode over the strongest other mode: 35 dB or more for telecom. (A VCSEL reaches a single longitudinal mode another way: its cavity is so short that only one mode fits under the gain, [Section 24.8]({% link chapters/24_fp.md %}#248the-vertical-cavity-surface-emitting-laser).)

## <span class="secnum">26.2</span>DFB lasers

A **distributed-feedback** (DFB) laser etches a Bragg grating ([Chapter 13]({% link chapters/13_bragg.md %})) along the whole gain section, so feedback is distributed along the cavity instead of coming from the facets. Its strength is the coupling–length product $$\kappa L$$, usually between 1 and 3: weaker and the threshold is high, stronger and the light piles up in the middle of the cavity, burning holes in the carrier density ([Figure 26.1](#fig-26-1)).

<figure id="fig-26-1">
  <img src="{{ '/assets/figs/ch26_dfb.svg' | relative_url }}" style="width:600px" alt="Top: side view of a DFB laser along its cavity, with n-InP substrate, quantum-well active region, an InGaAsP grating with a wider gap in the middle marked lambda/4 shift, p-InP, contacts and AR coatings on both facets, light leaving both ends. Bottom: intensity along the 400 micrometre cavity for kappa L of 1, 2 and 3; kappa L = 1 is highest at the facets, kappa L = 3 peaks at three times the mean in the middle.">
  <figcaption><span class="capnum">Figure 26.1.</span> <strong>A quarter-wave-shifted DFB laser.</strong> (a) Side view along the cavity: an InGaAsP grating above the quantum wells runs the whole length, with a half-period (λ/4) shift in the middle and AR coatings on both facets, so light leaves from both ends (not to scale). (b) Intensity of the lasing mode along a 400 µm cavity at threshold, from coupled-mode transfer matrices, for κL = 1, 2 and 3. A weak grating leaves the light near the facets and needs a net modal gain of 76 cm⁻¹; κL = 3 lases at 16 cm⁻¹ but piles the light up in the middle at three times its mean, where it burns holes in the carriers. Cavity length and κL illustrative. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

A uniform grating has a stop band with two equally good modes, one at each edge, so a uniform DFB laser may lase on either ([Figure 26.2](#fig-26-2)). A **quarter-wave shift** in the middle of the grating opens a single resonance at the centre of the stop band (as in the Bragg demo of Chapter 13). That gives one mode at the Bragg wavelength with a large gain margin over the rest, and an SMSR of 40–50 dB. With AR-coated facets, the λ/4-shifted DFB is the workhorse source of telecom and datacom. Its wavelength is fixed by the grating period and tunes only with temperature, at about 0.1 nm/K: the index changes, the gain peak does not matter.

<figure id="fig-26-2">
  <img src="{{ '/assets/figs/ch26_dfb_spectra.svg' | relative_url }}" style="width:600px" alt="Two transmission spectra in decibels against wavelength offset from the Bragg wavelength, each with the stop band shaded. Left, uniform grating: a dip in the stop band and two equal peaks at plus and minus 0.9 nanometres. Right, lambda/4-shifted grating: a single peak at the Bragg wavelength and much weaker side features.">
  <figcaption><span class="capnum">Figure 26.2.</span> <strong>Uniform and quarter-wave-shifted DFB spectra.</strong> Transmission of an AR-coated DFB laser (κL = 2, L = 400 µm, n<sub>g</sub> = 3.6) pumped to 95 % of its lowest threshold gain, a stand-in for its emission just below threshold. (a) The uniform grating has no mode inside its 1.06 nm stop band (shaded) and two band-edge modes 0.90 nm either side of it, with equal thresholds (net modal gain 49 cm⁻¹). (b) The λ/4 shift puts a single mode at the Bragg wavelength, with a threshold of 35 cm⁻¹; the next modes need 71 cm⁻¹. Coupled-mode transfer matrices {% include cite.html keys="coldren" %}; parameters illustrative. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">26.3</span>DBR lasers and tuning

A **distributed Bragg reflector** (DBR) laser separates the functions: a gain section, a passive **phase section** and a passive **Bragg mirror** section. Injecting current into the passive Bragg section lowers its index (free carriers, [Chapter 19]({% link chapters/19_eo.md %})) and moves the mirror's reflection peak by several nanometres; heaters move it the other way. The cavity modes move too, but not in step, so the lasing mode **hops** from one cavity mode to the next as the mirror peak passes them ([Figure 26.3](#fig-26-3)). The phase section moves the cavity modes on their own, so that together the two currents give continuous tuning.

<figure id="fig-26-3">
  <img src="{{ '/assets/figs/ch26_dbr.svg' | relative_url }}" style="width:600px" alt="Top: side view of a three-section DBR laser with gain, phase and DBR sections, each with its own current; quantum wells only under the gain section, a passive waveguide all along, a Bragg grating in the DBR section, light out of the cleaved gain-section facet. Bottom left: wavelength change against DBR index change; grey cavity-mode lines slope gently, the dashed mirror peak slopes steeply, and the lasing wavelength is a staircase with seven hops. Bottom right: the phase-section index change needed to keep a mode on the mirror peak, a sawtooth.">
  <figcaption><span class="capnum">Figure 26.3.</span> <strong>A three-section DBR laser and its tuning.</strong> (a) Gain, phase and Bragg-mirror sections share one waveguide; only the gain section has quantum wells, and each section has its own current (not to scale). (b) Lowering the index of the Bragg section moves the mirror peak (dashed) 6.5 times faster than the cavity modes (grey), which feel the change only through the mirror's penetration depth. The lasing wavelength (blue) rides on one mode, then hops by one mode spacing, 0.51 nm, to the next: seven hops over 4.3 nm. (c) The phase-section index change that keeps a mode exactly on the mirror peak gives continuous tuning; when it reaches one mode spacing (5.2 × 10⁻³ here) it resets and the next mode takes over. Illustrative laser: 400 µm gain and 150 µm phase sections, 100 µm mirror penetration, n<sub>g</sub> = 3.6. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

The tuning range of a single Bragg mirror is limited by the index change, a few nanometres. **Sampled-grating DBR** lasers use two mirrors with comb-like reflection spectra of slightly different periods, and tune over 40 nm by the Vernier effect of Section 26.5.

## <span class="secnum">26.4</span>External-cavity lasers on Si and SiN

Silicon photonics offers another split: put the gain in a III–V chip and the wavelength selection in silicon or silicon nitride. A **reflective SOA** (gain chip with a high-reflection rear facet and an angled, AR-coated front) is butt-coupled, flip-chipped or bonded to a passive circuit of ring filters and a loop mirror ([Figure 26.4](#fig-26-4); [Chapter 27]({% link chapters/27_lasersonsi.md %})). The passive circuit does three things a III–V chip cannot:

- **low loss over a long path**, which stores light longer and narrows the linewidth ([Chapter 25]({% link chapters/25_dynamics.md %}));
- **high-finesse ring filters**, sharper than any grating in a few square micrometres;
- **efficient heaters**, which tune the filters over their whole free spectral range for tens of milliwatts ([Chapter 18]({% link chapters/18_thermal.md %})).

Silicon nitride adds still lower loss, a smaller thermo-optic coefficient (more stable filters) and no two-photon absorption at high power {% include cite.html keys="xiang2021" %}.

<figure id="fig-26-4">
  <img src="{{ '/assets/figs/ch26_ecl.svg' | relative_url }}" style="width:600px" alt="Top view of an external-cavity laser. On the left, a shortened reflective SOA chip with an HR rear facet and a gain waveguide curving to meet the AR-coated front facet at an angle. On the right, a silicon chip: an inverse-taper edge coupler, a bus waveguide under a phase heater, ring 1 of 10 micrometre radius dropping light into a waveguide that runs left to ring 2 of 11 micrometre radius, whose drop waveguide runs right to a loop mirror; an output waveguide leaves the loop mirror's coupler. Heaters cover part of each ring; red arrows show the light's direction; 20 micrometre scale bar.">
  <figcaption><span class="capnum">Figure 26.4.</span> <strong>A III–V/silicon external-cavity laser, top view.</strong> A reflective SOA (HR rear facet, gain waveguide curved to meet the AR-coated front facet at 7°) is butt-coupled to an inverse-taper edge coupler. On the silicon, the light passes a phase heater, which sets a cavity mode under the filter peak, drops through ring 1 (R = 10 µm) and ring 2 (R = 11 µm), the rings of Worked Example 26.1, and reaches a loop mirror: a 2 × 2 coupler whose two outputs are joined by a loop, which sends the light back and, with an uneven split, lets part of it out. Arrows show the light on its way to the mirror; heaters on the rings tune them. Silicon layout, rings and gaps to scale (waveguides drawn 0.9 µm wide instead of 0.5 µm); the RSOA, about 1 mm long, is shortened. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">26.5</span>The Vernier effect

A single ring has many resonances one FSR apart. The gain spectrum is much wider than an FSR, so a ring alone does not pick a single mode. Two rings of slightly different radii in series pass light only where a resonance of each coincides. Like the two scales of a Vernier calliper, they line up only at intervals much larger than either FSR:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Vernier free spectral range</div>

$$\mathrm{FSR}_V = \frac{\mathrm{FSR}_1\,\mathrm{FSR}_2}{\lvert\mathrm{FSR}_1 - \mathrm{FSR}_2\rvert}$$

</div>

Heating one ring slides its comb against the other, and the coincidence jumps from one pair of resonances to the next. Moving a ring by only $$\lvert\mathrm{FSR}_1 - \mathrm{FSR}_2\rvert$$ moves the lasing wavelength by a whole FSR, a gearing of $$\mathrm{FSR}/\Delta\mathrm{FSR}$$. Tuning both rings together moves the coincidence continuously ([Figure 26.5](#fig-26-5)).

<figure id="fig-26-5">
  <img src="{{ '/assets/figs/ch26_vernier.svg' | relative_url }}" style="width:600px" alt="Top two panels: the resonance combs of ring 1 and ring 2 as tick marks from 1450 to 1650 nanometres. With the heaters off they coincide at 1458.5, 1550.0 and 1641.5 nanometres, 91 nanometres apart; after ring 2 is heated by 0.83 nanometres they coincide at 1467.7 and 1559.1 nanometres. Bottom panel: lasing wavelength against heater power on ring 2, a staircase of steps 9.15 nanometres high every 4.6 milliwatts that wraps from about 1596 down to 1504 nanometres, with a nearly flat line for both rings heated together.">
  <figcaption><span class="capnum">Figure 26.5.</span> <strong>Vernier gearing of the two rings of Worked Example 26.1.</strong> (a) Resonances of ring 1 (R = 10 µm, FSR 9.15 nm) and ring 2 (11 µm, 8.32 nm), aligned at 1550 nm with the heaters off: they coincide again only 91 nm away. (b) Heating ring 2 by one FSR difference, 0.83 nm (about 4.6 mW at 0.18 nm/mW), moves the coincidence by a whole FSR<sub>1</sub>, to 1559.1 nm. (c) Lasing wavelength, the peak of the gain times the squared product of the two drop responses, against the ring-2 heater power: steps of 9.15 nm every 4.6 mW, wrapping back by the Vernier FSR once the next coincidence is closer to the gain peak; heating both rings together tunes continuously at 0.18 nm/mW, eleven times more slowly. The combs are drawn with constant FSRs, the linear form of the key equation; ring coupling, loss and the gain window centred on 1550 nm are those of the demo below. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 26.1 · Two silicon rings for 40 nm of tuning</div>

With $$n_g = 4.18$$, rings of 10 and 11 µm radius have FSRs of 9.148 and 8.316 nm, so $$\mathrm{FSR}_V = 9.148 \times 8.316/0.832 \approx 91$$ nm: one coincidence across more than the gain bandwidth, which covers a 40 nm range with margin. Shifting ring 2 by 0.83 nm, about 5 mW with the TiN heaters of Chapter 18 (8.32 nm per 52 mW, or 0.16 nm/mW, for ring 2), moves the lasing wavelength by 9.15 nm, a gearing of 11. The price of such a large gearing is selectivity: the neighbouring coincidences, one FSR away, are only slightly misaligned, so the rings' resonances must be narrow (low coupling) for a good SMSR. The demo shows the trade.

</div>

**Try it.** Change the two radii and the heaters, and watch the combined filter pick one cavity mode under the gain.

{% include demos/vernier.html %}

## <span class="secnum">26.6</span>Self-injection locking

Feed a semiconductor laser with light reflected back from a very high-Q resonator, and the laser locks to the resonator's frequency, inheriting its stability. In chip-scale versions, the ring's own backscatter provides the feedback ([Figure 26.6](#fig-26-6)). Silicon-nitride rings with intrinsic Q in the tens of millions, coupled to III–V lasers, have narrowed the fundamental linewidth to below a kilohertz {% include cite.html keys="xiang2021" %}. Such lasers are the sources for coherent communication, FMCW LiDAR, microwave photonics and atomic sensors ([Chapter 39]({% link chapters/39_apps.md %})).

<figure id="fig-26-6">
  <img src="{{ '/assets/figs/ch26_sil.svg' | relative_url }}" style="width:600px" alt="Left: a DFB or Fabry-Perot laser without isolator butt-coupled to a silicon-nitride chip with a bus waveguide and a high-Q ring; arrows show the forward light circulating in the ring, backscattered light circulating the other way and returning along the bus to the laser, and a heater on the bus setting the feedback phase. Right: schematic spectra: a broad free-running laser line, a narrow ring transmission dip, and a much narrower locked laser line on the ring resonance.">
  <figcaption><span class="capnum">Figure 26.6.</span> <strong>Self-injection locking.</strong> (a) A laser without an isolator is butt-coupled to a high-Q silicon-nitride ring. Rayleigh backscattering inside the ring turns part of the circulating light around; it leaves the ring towards the laser, and a heater sets the phase of that feedback. (b) The feedback pulls the laser onto the ring resonance and narrows its line from the megahertz of a free-running laser ([Chapter 25]({% link chapters/25_dynamics.md %})) to below a kilohertz. Schematic, not to scale. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">26.7</span>Multi-wavelength sources

A WDM transceiver needs several wavelengths:

- **laser arrays**: separate DFB lasers, one per channel, bonded or flip-chipped, each with its own temperature and current;
- **comb sources**: one laser producing many equally spaced lines. Mode-locked quantum-dot lasers (Section 26.8), and Kerr combs generated in SiN microrings by four-wave mixing, give tens of lines on a fixed grid, which a demultiplexer separates.

Combs are attractive for dense WDM because the lines move together, so one control loop tracks them all; the price is lower power per line ([Figure 26.7](#fig-26-7)).

<figure id="fig-26-7">
  <img src="{{ '/assets/figs/ch26_multi.svg' | relative_url }}" style="width:600px" alt="Top: block diagram of four DFB lasers, each with its own current and temperature control, feeding a multiplexer onto one waveguide, beside a spectrum of four lines 400 GHz apart near 1550 nanometres. Bottom: block diagram of a pump laser driving a silicon-nitride microring Kerr comb into a demultiplexer that feeds several modulators, beside a spectrum of many equally spaced lines under a bell-shaped envelope.">
  <figcaption><span class="capnum">Figure 26.7.</span> <strong>Multi-wavelength sources.</strong> (a) A laser array: one DFB laser per channel, each with its own current and temperature, combined by a multiplexer. The four lines are the reference link's channels, 1546.12, 1549.32, 1552.52 and 1555.75 nm, 400 GHz apart {% include cite.html keys="itug694" %}. (b) A comb source: one pump laser drives a silicon-nitride microring into a Kerr comb of equally spaced lines, which a demultiplexer separates for the modulators; the 400 GHz spacing and sech² envelope are illustrative. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Four λ/4-shifted DFB lasers at 400 GHz spacing, one per channel, with the ring modulators and drop filters locked to them ([Chapter 18]({% link chapters/18_thermal.md %})). A comb source is the natural upgrade path to more channels.

</div>

## <span class="secnum">26.8</span>Mode-locked lasers

A Fabry–Pérot laser runs on many longitudinal modes at once, $$c/(2n_gL)$$ apart ([Chapter 24]({% link chapters/24_fp.md %})). Normally their phases wander independently, and their sum is a noisy but continuous output. Lock the phases to one another and the modes add up in step once per round trip: a single short pulse circulates in the cavity, and part of it leaves through a facet every time it comes round ([Figure 26.8](#fig-26-8)). Such a **mode-locked laser** is the time-domain view of the comb source of Section 26.7: a train of pulses at the repetition rate $$f_\mathrm{rep}$$ is a comb of lines $$f_\mathrm{rep}$$ apart {% include cite.html keys="haus2000" %}.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Pulse train of a mode-locked laser</div>

$$f_\mathrm{rep} = \frac{c}{2n_gL}, \qquad \tau \geq \frac{0.44}{\Delta\nu}, \qquad \frac{P_\mathrm{peak}}{P_\mathrm{mean}} \approx \frac{0.94}{f_\mathrm{rep}\,\tau}$$

</div>

Here $$\Delta\nu$$ is the locked bandwidth, $$\tau$$ the pulse's full width at half maximum, and the numbers are those of a Gaussian pulse. The cavity sets the repetition rate; the bandwidth sets the pulse width. More locked modes give shorter pulses, not a different repetition rate. The 0.44 is the time–bandwidth product of a pulse without chirp, called **transform-limited**. A chirped pulse, whose frequency changes from its front to its back, is longer for the same spectrum.

**How the phases lock.** There are three ways:

- **active**: the gain or the loss is modulated at exactly the round-trip frequency. Light that passes at the moment of lowest loss is favoured, which pulls the modes into step. This needs an RF source at $$f_\mathrm{rep}$$.
- **passive**: a short section of the waveguide is reverse biased into a **saturable absorber**, which absorbs weak light but bleaches when a pulse's leading edge arrives. The absorber saturates more easily than the gain section and recovers within picoseconds, while the gain recovers over hundreds of picoseconds. Together they open a window of net gain only around the pulse ([Figure 26.8b](#fig-26-8)), so continuous light loses and the pulse wins. No RF source is needed, so this is the usual choice on a chip.
- **hybrid**: a passive laser with a weak RF signal on its absorber, which steadies the timing of the pulses.

A **colliding-pulse** laser puts the absorber in the middle of the cavity, where two counter-propagating pulses meet, and doubles the repetition rate.

<figure id="fig-26-8">
  <img src="{{ '/assets/figs/ch26_mll.svg' | relative_url }}" style="width:640px" alt="(a) Side view of a two-section laser between cleaved facets: a long gain section under forward current and a short saturable absorber under reverse bias share one active waveguide; one pulse circulates and a train of pulses leaves. (b) Round-trip gain and loss against time through one pulse: the loss drops below the gain only for about 3 picoseconds around the pulse, shaded as the net-gain window. (c) A comb of lines 114 picometres apart under a Gaussian envelope 4 nanometres wide at 1310 nanometres. (d) Output power against time: with locked phases, 0.63 picosecond pulses every 50 picoseconds at 74 times the mean power; with random phases, noise a few times the mean.">
  <figcaption><span class="capnum">Figure 26.8.</span> <strong>A passively mode-locked laser.</strong> (a) A long gain section under forward current and a short saturable absorber under reverse bias share one waveguide between cleaved facets; one pulse circulates and leaves once per round trip (not to scale). (b) The net-gain window: round-trip gain and loss through one 1.5 ps pulse (grey) in the steady state of a model with a saturable gain and a saturable absorber. The absorber saturates more easily (pulse energy 3.5 times its saturation energy, against 0.4 for the gain) and recovers faster (3 ps against 300 ps), so the gain beats the loss only for 2.9 ps around the pulse (shaded); before and after it the net gain is negative, which keeps any light outside the pulse from growing. Illustrative parameters. (c) The comb of Worked Example 26.2: lines 114 pm apart under a Gaussian envelope 4 nm wide at 1310 nm. (d) The same lines with locked phases give 0.63 ps pulses every 50 ps, peaking at 74 times the mean power; with random phases they give noise, with peaks about 5 times the mean. Drawn by <code>figsrc/ch26_figs.py</code>.</figcaption>
</figure>

**Quantum dots and silicon.** Quantum-dot gain suits passive mode locking. The dots' spread of sizes gives a broad gain spectrum ([Chapter 23]({% link chapters/23_gain.md %})), their absorbers recover quickly, and their small α-factor keeps the pulses clean ([Chapter 25]({% link chapters/25_dynamics.md %})). Mode-locked lasers have been built with the integration schemes of [Chapter 27]({% link chapters/27_lasersonsi.md %}). Heterogeneous III–V/silicon lasers with on-chip mirrors have given pulses as short as 900 fs {% include cite.html keys="davenport2018" %}. A 20 GHz quantum-dot laser grown directly on silicon supplied 64 comb lines, each carrying 32 GBd PAM4, for 4.1 Tbit/s in total {% include cite.html keys="liu2019mll" %}. Two more numbers describe such a laser: its **timing jitter**, the random wander of the pulses from a perfect clock (82.7 fs, integrated from 4 to 80 MHz, in that laser), and the **RF linewidth** of the beat note at $$f_\mathrm{rep}$$.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 26.2 · A 20 GHz comb at 1310 nm</div>

With $$n_g = 3.5$$, a 20 GHz repetition rate needs $$L = c/(2n_gf_\mathrm{rep}) = 2.14$$ mm. The lines are $$\lambda^2 f_\mathrm{rep}/c = 114$$ pm apart. A locked bandwidth of 4 nm is 699 GHz, about 35 lines within its FWHM. Without chirp it gives Gaussian pulses $$0.44/699\ \mathrm{GHz} = 0.63$$ ps wide, peaking at $$0.94/(20\ \mathrm{GHz} \times 0.63\ \mathrm{ps}) = 74$$ times the mean power. As a WDM source, 64 lines at 32 GBd PAM4 (two bits per symbol) carry $$64 \times 64\ \mathrm{Gbit/s} = 4.1$$ Tbit/s. The power is shared, though: a laser emitting 20 mW leaves about 0.3 mW per line, before the demultiplexer's loss.

</div>

**Try it.** Lock and unlock the modes, then change the cavity length, the locked bandwidth and the chirp.

{% include demos/mll.html %}

## In 3D

The two lasers of this chapter: the III–V/silicon external-cavity laser of Figure 26.4 with its Vernier rings, and a buried-heterostructure DFB laser with its grating above the wells. Drag to turn them, scroll to zoom, click a layer in the legend to hide it (shift-click to show it alone), and switch to the exploded view or to 3× height to see the thin layers. They are generic concepts drawn with this chapter's dimensions, not devices from a PDK; real PDK devices are in the [PDK devices in 3D]({% link devices-3d.md %}) gallery.

{% include stack3d-assets.html %}
<div class="d3-grid">
{% include stack3d.html slug="ecl" %}
{% include stack3d.html slug="bh" %}
</div>

## Reading

{% include reflist.html keys="coldren,komljenovic2016,xiang2021,haus2000,davenport2018" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Single-frequency lasers need a wavelength-selective element and an SMSR of 35 dB or more.
- λ/4-shifted DFB lasers (κL ≈ 1–3) are the telecom workhorse; they tune only with temperature, about 0.1 nm/K.
- DBR lasers tune with current or heat in the mirror and phase sections, with mode hops unless the phase is controlled.
- External-cavity lasers combine III–V gain with low-loss Si or SiN filters for wide tuning and narrow lines.
- Two rings give $$\mathrm{FSR}_V = \mathrm{FSR}_1\mathrm{FSR}_2/\lvert\Delta\mathrm{FSR}\rvert$$: 91 nm for 10 and 11 µm silicon rings, with a tuning gearing of 11.
- Locked modes add up to pulses at $$f_\mathrm{rep} = c/(2n_gL)$$, about $$0.44/\Delta\nu$$ wide; a saturable absorber locks them passively, and the pulse train is a comb.

</div>

## Check yourself

{% include quiz.html %}
