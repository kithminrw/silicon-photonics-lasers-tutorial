---
title: "33. Optical Links and Transceivers"
parent: "Part VIII · Systems and Applications"
nav_order: 33
permalink: /part-8/ch33/
chapter: 33
---

# <span class="chapnum">Chapter 33</span>Optical Links and Transceivers

Everything comes together in a link: laser, modulator, multiplexer, fibre, demultiplexer, detector, and the budget that connects them.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe IM-DD and coherent link architectures;
- compute a power budget with penalties and margin;
- compare WDM transceiver architectures (parallel, CWDM, ring-based DWDM);
- estimate energy per bit including the laser's wall-plug efficiency;
- check the reference link's budget block by block.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Does the reference link close, and what does each block contribute?

</div>

## <span class="secnum">33.1</span>Link architectures

- **Intensity modulation with direct detection** (IM-DD) writes the data as optical power (NRZ or PAM4, [Chapter 20]({% link chapters/20_modulators.md %})) and detects it with a photodiode ([Chapter 21]({% link chapters/21_pd.md %})). It is simple and low-power, and it rules short reaches: inside data centres, from metres to a few kilometres.
- **Coherent** links write the data onto the amplitude and phase of the field in both polarisations, and detect it by mixing with a local-oscillator laser, followed by digital signal processing that undoes dispersion and polarisation rotation. It carries more bits per symbol and reaches thousands of kilometres, at the cost of power-hungry DSP and narrow-linewidth lasers ([Chapter 25]({% link chapters/25_dynamics.md %})).

Short-reach links scale capacity in three ways: faster lanes, more fibres (**parallel single-mode**, one fibre per lane) or more wavelengths per fibre (**WDM**).

## <span class="secnum">33.2</span>Power budget and penalties

The budget of [Chapter 1]({% link chapters/01_why.md %}) subtracts each block's loss from the launched power and compares the received power with the receiver's sensitivity. A real budget also subtracts **penalties**: the extra power needed because the signal is not ideal.

- **Extinction ratio**: a finite ER wastes average power on the "0" level ([Chapter 21]({% link chapters/21_pd.md %}) already includes the 4 dB ER in its −11.6 dBm sensitivity).
- **Crosstalk**: light from neighbouring channels leaking through the demultiplexer adds noise and a power penalty. With −20 dB of adjacent-channel rejection ([Chapter 14]({% link chapters/14_wdm.md %})) the two neighbours leak about 2 % of the power, a penalty of roughly 0.1 dB; the budget allows a generous 0.5 dB.
- **Dispersion and chirp**: 2 km at 1550 nm accumulate 34 ps/nm ([Example 2.5]({% link chapters/02_em.md %})), inside the 40–60 ps/nm tolerance of 50 Gb/s NRZ but not free: a few tenths of a decibel with a chirp-free modulator, more with chirp, so the budget allows 0.5 dB. Directly modulated lasers, with their large chirp, fare much worse ([Chapter 25]({% link chapters/25_dynamics.md %})).
- **Noise and jitter**: laser RIN, electrical jitter and intersymbol interference from limited bandwidth.
- **Drift and ageing**: rings slightly off their lasers, lasers that lose power over their lifetime.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Link budget</div>

$$\text{margin} = P_\mathrm{launch} - \sum_i L_i - \sum_j \mathrm{penalty}_j - P_\mathrm{sens}$$

</div>

A link closes when the margin is positive; designers keep a few decibels in reserve for what was not modelled.

## <span class="secnum">33.3</span>WDM transceivers

- **Parallel single-mode** transceivers use one fibre per lane (four transmit and four receive), with identical lasers and modulators. Simple optics, but many fibres.
- **CWDM** transceivers multiplex four lanes 20 nm apart near 1310 nm onto one fibre, with uncooled lasers and broadband filters (MZI lattices or echelle gratings, [Chapter 14]({% link chapters/14_wdm.md %})).
- **Ring-based DWDM**, the reference link's architecture, uses ring modulators that also multiplex, and drop rings that demultiplex, on a dense grid. It is compact and energy-efficient and scales to many wavelengths, with every ring locked to its laser ([Chapter 18]({% link chapters/18_thermal.md %})).

## <span class="secnum">33.4</span>Coherent transceivers

A coherent transmitter uses an **IQ modulator**, two nested Mach–Zehnder modulators biased at null with a 90° phase shift between them, in each polarisation, combined by a polarisation rotator and combiner ([Chapter 14]({% link chapters/14_wdm.md %})). The receiver mixes the signal with a local oscillator in a **90° optical hybrid** (an MMI, [Chapter 10]({% link chapters/10_mmi.md %})) feeding balanced photodiodes, and the DSP recovers the symbols. Silicon photonics integrates the modulators, hybrids and detectors; thin-film lithium niobate offers lower-loss, more linear modulators ([Chapter 20]({% link chapters/20_modulators.md %})).

## <span class="secnum">33.5</span>Energy per bit

The figure of merit of a short-reach link is its total energy per transmitted bit. For a WDM link it adds up as

$$E_\mathrm{bit} = \frac{N_\lambda P_\mathrm{opt}/\eta_\mathrm{wp} + P_\mathrm{heaters} + P_\mathrm{drivers} + P_\mathrm{RX}}{\text{total bit rate}}$$

The laser term is usually the largest, because the optical power in the waveguide is divided by a **wall-plug efficiency** $$\eta_\mathrm{wp}$$ of 10–20 % once coupling losses and the laser's own efficiency ([Chapter 24]({% link chapters/24_fp.md %})) are counted. Every decibel of loss saved in the link can be turned into laser power saved. Heaters come next for ring-based designs ([Chapter 18]({% link chapters/18_thermal.md %})). Modulators themselves are almost free: 20 fJ/bit for a ring ([Chapter 20]({% link chapters/20_modulators.md %})).

## <span class="secnum">33.6</span>Co-packaged optics

As switch and accelerator chips pass tens of terabits per second, driving signals across a circuit board to pluggable modules costs too much power. **Co-packaged optics** places the photonic chips on the same package as the switch, with millimetre-long electrical connections ([Chapter 17]({% link chapters/17_fiberarrays.md %})). The lasers often stay outside, in replaceable modules, feeding the package through fibre. Ring-based WDM, with its small size and low energy per bit, is a natural fit, which is why the reference link is built that way.

## <span class="secnum">33.7</span>The reference link, block by block

[Table 33.1](#tab-33-1) closes the budget set in [Chapter 1]({% link chapters/01_why.md %}) with the numbers each chapter produced; where no chapter computed a value, Chapter 1's estimate or an allowance stands.

**Table 33.1. The reference link: 4 × 50 Gb/s NRZ over 2 km, one wavelength.**
{: .tabcaption #tab-33-1 }

| Block | Value | Chapter |
|---|---|---|
| Laser power in the transmitter waveguide | +10 dBm | 1 (target), 24–27 |
| Ring modulator insertion loss | −3.0 dB (4 dB ER at 2 Vpp, about 50 pm/V) | 19, 20 |
| Other rings and routing | −0.8 dB | 1 (estimate) |
| Transmit grating coupler | −3.0 dB (−4 dB for the measured PDK design) | 15 |
| 2 km of fibre and two connectors | −0.4 dB, −1.0 dB | 3; 1 (connectors, estimate) |
| Receive grating coupler | −3.0 dB | 15 |
| Demultiplexing ring and routing | −1.5 dB | 1 (estimate), 14 |
| **Received power** | **−2.7 dBm** | 1 |
| Receiver sensitivity at BER 10⁻¹² (4 dB ER) | −11.6 dBm | 21 |
| Penalties: crosstalk, dispersion, drift and locking, ageing | 0.5 + 0.5 + 1.0 + 1.0 dB | allowances (2, 14, 18) |
| **Margin** | **5.9 dB** | |
| Energy: lasers (15 % wall plug), heaters, TIAs, drivers, modulators | 1.33 + 0.80 + 1.0 + 0.5 + 0.02 = 3.65 pJ/bit | 18, 20; TIAs and drivers: typical values |

The link closes with 5.9 dB of margin and uses about 3.7 pJ/bit against the 5 pJ/bit target. The weakest points are the ones the earlier chapters flagged: the ring modulator's tight trade between extinction, loss and bandwidth ([Chapter 20]({% link chapters/20_modulators.md %})), the grating couplers (with the measured PDK design at −4 dB each, the margin drops to 3.9 dB), and the heater power, which depends on the fabrication spread ([Chapter 29]({% link chapters/29_fab.md %})). The margin could also be spent on cutting the laser power: 2.9 dB less light per lane saves 0.65 pJ/bit and still leaves the 3 dB the targets ask for.

**Try it.** Change any block, the laser's wall-plug efficiency or the heater power, and watch the budget and the energy per bit.

{% include demos/linkbudget.html %}

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab game: DataBytes Inc. (run a data centre)](https://s3.amazonaws.com/vmlab-app-1/index.html) {% include cite.html keys="vmlab" %}

</div>

## Reading

{% include reflist.html keys="shekhar2024,chrostowski2015,sun2015" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- IM-DD rules short reaches; coherent links carry more per symbol over long distances with DSP.
- Margin = launch power − losses − penalties − sensitivity; keep a few decibels in reserve.
- Parallel, CWDM and ring-based DWDM trade fibres, filters and control.
- Energy per bit is dominated by laser wall-plug power and, for rings, heaters; modulators are nearly free.
- The reference link closes with 5.9 dB of margin at about 3.7 pJ/bit; its tight spots are the ring modulator, the couplers and the heaters.

</div>
