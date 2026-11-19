---
title: "14. WDM Filters and Polarisation Management"
parent: "Part III · Passive Devices"
nav_order: 14
permalink: /part-3/ch14/
chapter: 14
---

# <span class="chapnum">Chapter 14</span>WDM Filters and Polarisation Management

Wavelength-division multiplexing puts many channels on one waveguide, and polarisation devices deal with fibres that scramble polarisation.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- name the WDM grids and what a multiplexer must achieve on them;
- design a ring demultiplexer: free spectral range, bandwidth and crosstalk;
- compare ring rows, MZI lattices, arrayed-waveguide and echelle gratings, and contra-directional couplers;
- explain how polarisation splitters and rotators work;
- describe polarisation-diversity receivers.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you separate the four wavelengths of the reference link with low crosstalk?

</div>

## <span class="secnum">14.1</span>WDM grids and requirements

Wavelength channels follow standard grids ([Figure 14.1](#fig-14-1)). **CWDM** spaces them 20 nm apart (for example 1271, 1291, 1311 and 1331 nm in four-channel data-centre transceivers), loose enough for uncooled lasers and simple filters. **LAN-WDM** uses 800 GHz (about 4.5 nm) spacing near 1310 nm. **DWDM** uses the ITU frequency grid with 100, 50 GHz or finer spacing in the C band {% include cite.html keys="itug694" %}; the reference link uses its 400 GHz (3.2 nm) slots ([Chapter 1]({% link chapters/01_why.md %})). A multiplexer or demultiplexer must pass each channel with low insertion loss and a flat enough passband for the signal (about 50 GHz wide at 50 Gb/s), reject its neighbours (crosstalk below about −20 dB), and stay on its channel over temperature.

<figure id="fig-14-1">
  <img src="{{ '/assets/figs/ch14_grids.svg' | relative_url }}" style="width:600px" alt="Top: a wavelength axis from 1260 to 1570 nm with four CWDM channels 20 nm apart and four LAN-WDM channels about 4.5 nm apart in the O band, and four DWDM channels in the C band. Bottom: the four reference-link channels at 1546.12, 1549.32, 1552.52 and 1555.75 nm, 400 GHz apart, on the 100 GHz ITU grid, each with a shaded 50 GHz signal width, with a frequency axis in terahertz on top">
  <figcaption><span class="capnum">Figure 14.1.</span> <strong>WDM grids.</strong> (a) Four-channel CWDM (20 nm) and LAN-WDM (800 GHz, about 4.5 nm) grids sit in the O band; DWDM channels sit in the C band. (b) The reference link: four channels 400 GHz (3.2 nm) apart on the ITU frequency grid {% include cite.html keys="itug694" %} (ticks every 100 GHz), each shaded over the ≈ 50 GHz (0.4 nm) that a 50 Gb/s NRZ signal occupies. LAN-WDM channels as in IEEE 802.3ba {% include cite.html keys="ieee8023ba" %}. Drawn by <code>figsrc/ch14_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">14.2</span>Ring and MZI-lattice multiplexers

A row of add-drop rings on one bus, each tuned to one channel, is the most compact demultiplexer ([Chapter 12]({% link chapters/12_rings.md %}), [Figure 14.2](#fig-14-2)). Each ring drops its channel and passes the others; heaters hold each ring on its channel. A single ring has a Lorentzian drop response,

$$T_\mathrm{drop}(\Delta\lambda) = \frac{T_0}{1 + (2\Delta\lambda/\Delta\lambda_\mathrm{FWHM})^2},$$

which fixes the trade between passband and crosstalk.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 14.1 · A ring demultiplexer for the reference link</div>

**Free spectral range.** For a cyclic four-channel demultiplexer the rings' FSR should be four channel spacings, $$4 \times 3.2 = 12.8$$ nm, so that each ring's next resonance falls one full set of channels away. With $$n_g = 4.18$$, $$L = \lambda^2/(n_g\,\mathrm{FSR}) = 2.4025/(4.18 \times 0.0128) = 44.9$$ µm: a radius of 7.15 µm.

**Bandwidth and crosstalk.** For −20 dB of rejection of the neighbouring channel 3.2 nm away, $$(2 \times 3.2/\Delta\lambda_\mathrm{FWHM})^2 = 99$$, so $$\Delta\lambda_\mathrm{FWHM} \le 0.64$$ nm, a loaded Q of about 2400. A 50 Gb/s NRZ signal occupies about 0.4 nm, so a 0.6 nm passband passes it, though not for free: the narrow drop ring slows the edges enough to close the eye by about 1 dB, which the driver's equalisation recovers ([Lab 12]({% link labs/lab12_link.md %})). Such a low Q means a strongly over-coupled ring: 14.5 % of the power must cross each coupler, which a ring touching a straight bus would reach only with a gap of about 37 nm, so the couplers are racetracks or pulley couplers ([Chapter 9]({% link chapters/09_couplers.md %})). The strong coupling also keeps the drop loss low.

</div>

<figure id="fig-14-2">
  <img src="{{ '/assets/figs/ch14_demux.svg' | relative_url }}" style="width:600px" alt="Top: layout to scale of four add-drop rings of 7.15 micrometre radius along one bus waveguide, each with a heater arc over it and a drop waveguide leading to a germanium photodiode, labelled with the four channel wavelengths. Bottom: the drop-port spectra of the four rings from 1531 to 1571 nm in decibels, each peaking at its channel and again 12.8 nm away, with a dashed line at minus 20 dB">
  <figcaption><span class="capnum">Figure 14.2.</span> <strong>A four-ring demultiplexer for the reference link.</strong> (a) Layout to scale: four add-drop rings of 7.15 µm radius (\(L = 44.9\) µm) on one bus, each with a heater and a drop waveguide to a 15 × 4 µm germanium photodiode; the coupling gaps are too narrow to see. Heaters, or radii stepped by about 25 nm, put each ring on its channel. (b) The four drop ports, cascaded along the bus, with symmetric couplers of \(\kappa^2 = 14.5\) % (FWHM 0.64 nm, \(Q_L \approx 2400\)) and 2 dB/cm. Each ring's next resonance falls one FSR, 12.8 nm, away, on an empty grid slot. Because the response is periodic, the first ring passes its neighbour λ\(_2\) and, through its next order, λ\(_4\) at −19 dB, a little more than the Lorentzian estimate of −20 dB. Drawn by <code>figsrc/ch14_figs.py</code>.</figcaption>
</figure>

**Try it.** The rings of Figure 14.2 on one bus, with their heaters. Lower κ² until the worst crosstalk meets −20 dB; switch the heaters off and warm the chip from 20 to 70 °C to watch the rings drift across their channels; then lock them again, to their own channels or to the nearest ones, and compare the heater power. Pick a channel to see its light leave the bus at its ring.

{% include demos/demux.html %}

The Lorentzian's slow roll-off is the weakness of single rings. **Second- and higher-order filters** (two or more coupled rings) give flat tops and much steeper skirts ([Figure 14.3](#fig-14-3)). **MZI lattices** ([Chapter 11]({% link chapters/11_mzi.md %})) do the same with cascaded interferometers: an interleaver splits odd and even channels, and a tree of them separates many.

<figure id="fig-14-3">
  <img src="{{ '/assets/figs/ch14_flattop.svg' | relative_url }}" style="width:600px" alt="Left: drop-port transmission in decibels against detuning for first, second and third order maximally flat filters with the same 0.64 nm bandwidth, rejecting the neighbouring channel 3.2 nm away by 20, 40 and 60 dB. Right: the same responses within 0.6 nm of the channel, where the higher orders are flatter across a shaded 0.4 nm signal band">
  <figcaption><span class="capnum">Figure 14.3.</span> <strong>Lorentzian against flat-top channels.</strong> Ideal maximally flat (Butterworth) drop responses of order 1 (one ring: the Lorentzian of Worked Example 14.1), 2 and 3 (two and three coupled rings), all 0.64 nm wide at −3 dB. (a) The neighbouring channel, 3.2 nm away, is rejected by 20, 40 and 60 dB. (b) Across the ≈ 0.4 nm of a 50 Gb/s NRZ signal (shaded) the single ring loses up to 1.4 dB at the band edges, the third-order filter 0.24 dB. Drawn by <code>figsrc/ch14_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">14.3</span>Arrayed-waveguide and echelle gratings

For many channels, dispersive devices scale better. An **arrayed-waveguide grating** (AWG, [Figure 14.4a](#fig-14-4)) splits the light in a free-propagation region into an array of waveguides whose lengths increase in equal steps; at the far side they interfere like a diffraction grating, and each wavelength focuses onto a different output waveguide {% include cite.html keys="okamoto" %}. An **echelle grating** ([Figure 14.4b](#fig-14-4)) does the same with an etched reflective grating in a slab. Both demultiplex tens of channels in one device, with passive, flat-ish passbands, but they are larger than rings and sensitive to phase errors in silicon's high-contrast waveguides, which raise crosstalk.

<figure id="fig-14-4">
  <img src="{{ '/assets/figs/ch14_awg.svg' | relative_url }}" style="width:600px" alt="Left: schematic of an arrayed-waveguide grating, an input waveguide, a fan-shaped free-propagation region, nine nested semicircular array waveguides of increasing length, a second free-propagation region and four output waveguides labelled lambda 1 to 4. Right: schematic of an echelle grating, a slab region with input and output waveguides on one side and a curved, saw-toothed reflecting grating on the other, with rays from the input reflected to different outputs for two wavelengths">
  <figcaption><span class="capnum">Figure 14.4.</span> <strong>Dispersive demultiplexers</strong> (schematics, not to scale). (a) Arrayed-waveguide grating: the first free-propagation region spreads the input over the array, whose waveguides grow longer in equal steps ΔL; the second region focuses each wavelength onto its own output. (b) Echelle grating: an etched, reflecting grating, curved to focus, sends each wavelength from the input back to its own output along the same edge of the slab. Drawn by <code>figsrc/ch14_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">14.4</span>Crosstalk, flat-top responses and tuning

In practice a demultiplexer's crosstalk is set less by its ideal response than by imperfections: phase errors in AWGs, side lobes, backscatter in rings and the thermal drift of every resonant device. Ring-based WDM therefore depends on **control**: each ring needs a heater and a monitor (a photodiode tap or the drop signal itself) in a feedback loop that keeps it locked to its laser line ([Chapter 18]({% link chapters/18_thermal.md %})). Because silicon rings drift by about 75 pm/K, a 50 K range moves them by more than one 3.2 nm channel; schemes that let each ring lock to whichever channel is nearest, then reassign channels in the electronics, save heater power.

## <span class="secnum">14.5</span>Polarisation splitters and rotators

A silicon strip is strongly birefringent ([Chapter 6]({% link chapters/06_soi.md %})), and grating couplers accept one polarisation only, but light arriving from a standard fibre has an unknown, drifting polarisation ([Chapter 2]({% link chapters/02_em.md %})). Two devices handle it:

- **Polarisation splitters** separate TE and TM. A common design is an asymmetric directional coupler phase-matched for TM but not TE: TM crosses to the second waveguide while TE stays.
- **Polarisation rotators** turn TM into TE. In silicon the usual trick uses mode hybridisation: in a waveguide with a vertically asymmetric cross-section (a partial etch or a different upper cladding), the TM0 mode and the TE1 mode exchange character along an adiabatic taper, so TM0 becomes TE1; an asymmetric coupler then converts TE1 in the wide guide into TE0 in a narrow one ([Chapter 8]({% link chapters/08_bends.md %})). Together this is a **polarisation splitter-rotator** (PSR, [Figure 14.5](#fig-14-5)).

<figure id="fig-14-5">
  <img src="{{ '/assets/figs/ch14_psr.svg' | relative_url }}" style="width:600px" alt="Schematic top view of a polarisation splitter-rotator: a strip carrying TE0 and TM0 enters a bilevel taper with a partially etched slab on both sides, where TM0 becomes TE1, continues as a wide strip, and passes an asymmetric directional coupler where TE1 crosses into the TE0 mode of a narrow waveguide that bends away, while TE0 continues straight on; below, cross-sections A, B and C of the strip, the rib and the two coupled strips">
  <figcaption><span class="capnum">Figure 14.5.</span> <strong>A polarisation splitter-rotator</strong> (top view schematic, not to scale; cross-sections A–C to scale with illustrative widths). TE0 passes straight through. TM0 turns into TE1 in the bilevel taper, where the partially etched slab at the bottom of the guide (cross-section B) breaks its up-down symmetry; the asymmetric coupler then hands TE1 of the wide guide to TE0 of the narrow one, whose width is chosen to phase-match it. Drawn by <code>figsrc/ch14_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">14.6</span>Polarisation diversity

A **polarisation-diversity** receiver ([Figure 14.6](#fig-14-6)) splits the incoming light into its two polarisations, rotates one, and processes both copies on identical TE circuits, adding the detected signals at the end. A **two-dimensional grating coupler** does the splitting and rotation in one step: it couples the two fibre polarisations into two orthogonal TE waveguides. The cost is a doubled circuit and the need for the two paths to match.

<figure id="fig-14-6">
  <img src="{{ '/assets/figs/ch14_diversity.svg' | relative_url }}" style="width:600px" alt="Two block diagrams. Top: fibre light of any polarisation enters an edge coupler and polarisation splitter-rotator, whose two TE outputs pass through two identical TE circuits to two photodiodes whose currents are summed into the data. Bottom: the same with a two-dimensional grating coupler in place of the edge coupler and splitter-rotator">
  <figcaption><span class="capnum">Figure 14.6.</span> <strong>Polarisation diversity.</strong> (a) An edge coupler and a polarisation splitter-rotator turn the two fibre polarisations into two TE signals; (b) a two-dimensional grating coupler does both in one element. Each copy passes through an identical TE circuit and the two photocurrents are added (one channel shown). Drawn by <code>figsrc/ch14_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Ring demultiplexer: four add-drop rings of about 7.15 µm radius (FSR 12.8 nm), over-coupled to a loaded Q of about 2400 (0.64 nm passband) for about −20 dB adjacent-channel rejection (−19 dB once each ring's next order is counted; a slightly higher Q gains the last decibel), each with a heater and a locking loop. TE only; the receiver uses a TE grating coupler and polarisation-maintaining fibre in the lab.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: asymmetric directional coupler / mode converter](https://s3.amazonaws.com/fip-13/Mode-Converter/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="okamoto,chrostowski2015,bogaerts2012,itug694" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- WDM grids: CWDM (20 nm), LAN-WDM (800 GHz), DWDM (ITU grid, 400 GHz to 50 GHz and below).
- A four-channel ring demultiplexer on a 3.2 nm grid needs rings of FSR 12.8 nm (R ≈ 7.15 µm) and a loaded Q of about 2400 for about −20 dB crosstalk (−19 dB once the rings' next orders are counted).
- Higher-order rings and MZI lattices flatten the passband and sharpen the skirts; AWGs and echelles scale to many channels.
- Every resonant demultiplexer needs heaters and locking loops against thermal drift.
- Polarisation splitter-rotators and 2D grating couplers make silicon circuits work with fibre's arbitrary polarisation.

</div>
