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

Wavelength channels follow standard grids. **CWDM** spaces them 20 nm apart (for example 1271, 1291, 1311 and 1331 nm in four-channel data-centre transceivers), loose enough for uncooled lasers and simple filters. **LAN-WDM** uses 800 GHz (about 4.5 nm) spacing near 1310 nm. **DWDM** uses the ITU frequency grid with 100, 50 GHz or finer spacing in the C band {% include cite.html keys="itug694" %}; the reference link uses its 400 GHz (3.2 nm) slots ([Chapter 1]({% link chapters/01_why.md %})). A multiplexer or demultiplexer must pass each channel with low insertion loss and a flat enough passband for the signal (about 50 GHz wide at 50 Gb/s), reject its neighbours (crosstalk below about −20 dB), and stay on its channel over temperature.

## <span class="secnum">14.2</span>Ring and MZI-lattice multiplexers

A row of add-drop rings on one bus, each tuned to one channel, is the most compact demultiplexer ([Chapter 12]({% link chapters/12_rings.md %})). Each ring drops its channel and passes the others; heaters hold each ring on its channel. A single ring has a Lorentzian drop response,

$$T_\mathrm{drop}(\Delta\lambda) = \frac{T_0}{1 + (2\Delta\lambda/\Delta\lambda_\mathrm{FWHM})^2},$$

which fixes the trade between passband and crosstalk.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 14.1 · A ring demultiplexer for the reference link</div>

**Free spectral range.** For a cyclic four-channel demultiplexer the rings' FSR should be four channel spacings, $$4 \times 3.2 = 12.8$$ nm, so that each ring's next resonance falls one full set of channels away. With $$n_g = 4.18$$, $$L = \lambda^2/(n_g\,\mathrm{FSR}) = 2.4025/(4.18 \times 0.0128) = 44.9$$ µm: a radius of 7.2 µm.

**Bandwidth and crosstalk.** For −20 dB of rejection of the neighbouring channel 3.2 nm away, $$(2 \times 3.2/\Delta\lambda_\mathrm{FWHM})^2 = 99$$, so $$\Delta\lambda_\mathrm{FWHM} \le 0.64$$ nm, a loaded Q of about 2400. A 50 Gb/s NRZ signal occupies about 0.4 nm, so a 0.6 nm passband passes it with little filtering penalty. Such a low Q means a strongly over-coupled ring with small gaps ([Chapter 9]({% link chapters/09_couplers.md %})), which also keeps the drop loss low.

</div>

The Lorentzian's slow roll-off is the weakness of single rings. **Second- and higher-order filters** (two or more coupled rings) give flat tops and much steeper skirts. **MZI lattices** ([Chapter 11]({% link chapters/11_mzi.md %})) do the same with cascaded interferometers: an interleaver splits odd and even channels, and a tree of them separates many.

## <span class="secnum">14.3</span>Arrayed-waveguide and echelle gratings

For many channels, dispersive devices scale better. An **arrayed-waveguide grating** (AWG) splits the light in a free-propagation region into an array of waveguides whose lengths increase in equal steps; at the far side they interfere like a diffraction grating, and each wavelength focuses onto a different output waveguide {% include cite.html keys="okamoto" %}. An **echelle grating** does the same with an etched reflective grating in a slab. Both demultiplex tens of channels in one device, with passive, flat-ish passbands, but they are larger than rings and sensitive to phase errors in silicon's high-contrast waveguides, which raise crosstalk.

## <span class="secnum">14.4</span>Crosstalk, flat-top responses and tuning

In practice a demultiplexer's crosstalk is set less by its ideal response than by imperfections: phase errors in AWGs, side lobes, backscatter in rings and the thermal drift of every resonant device. Ring-based WDM therefore depends on **control**: each ring needs a heater and a monitor (a photodiode tap or the drop signal itself) in a feedback loop that keeps it locked to its laser line ([Chapter 18]({% link chapters/18_thermal.md %})). Because silicon rings drift by 70–80 pm/K, a 50 K range moves them by more than one 3.2 nm channel; schemes that let each ring lock to whichever channel is nearest, then reassign channels in the electronics, save heater power.

## <span class="secnum">14.5</span>Polarisation splitters and rotators

A silicon strip is strongly birefringent ([Chapter 6]({% link chapters/06_soi.md %})), and grating couplers accept one polarisation only, but light arriving from a standard fibre has an unknown, drifting polarisation ([Chapter 2]({% link chapters/02_em.md %})). Two devices handle it:

- **Polarisation splitters** separate TE and TM. A common design is an asymmetric directional coupler phase-matched for TM but not TE: TM crosses to the second waveguide while TE stays.
- **Polarisation rotators** turn TM into TE. In silicon the usual trick uses mode hybridisation: in a waveguide with a vertically asymmetric cross-section (a partial etch or a different upper cladding), the TM0 mode and the TE1 mode exchange character along an adiabatic taper, so TM0 becomes TE1; an asymmetric coupler then converts TE1 in the wide guide into TE0 in a narrow one ([Chapter 8]({% link chapters/08_bends.md %})). Together this is a **polarisation splitter-rotator** (PSR).

## <span class="secnum">14.6</span>Polarisation diversity

A **polarisation-diversity** receiver splits the incoming light into its two polarisations, rotates one, and processes both copies on identical TE circuits, adding the detected signals at the end. A **two-dimensional grating coupler** does the splitting and rotation in one step: it couples the two fibre polarisations into two orthogonal TE waveguides. The cost is a doubled circuit and the need for the two paths to match.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Ring demultiplexer: four add-drop rings of about 7.2 µm radius (FSR 12.8 nm), over-coupled to a loaded Q of about 2400 (0.64 nm passband) for −20 dB adjacent-channel rejection, each with a heater and a locking loop. TE only; the receiver uses a TE grating coupler and polarisation-maintaining fibre in the lab.

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
- A four-channel ring demultiplexer on a 3.2 nm grid needs rings of FSR 12.8 nm (R ≈ 7.2 µm) and a loaded Q of about 2400 for −20 dB crosstalk.
- Higher-order rings and MZI lattices flatten the passband and sharpen the skirts; AWGs and echelles scale to many channels.
- Every resonant demultiplexer needs heaters and locking loops against thermal drift.
- Polarisation splitter-rotators and 2D grating couplers make silicon circuits work with fibre's arbitrary polarisation.

</div>
