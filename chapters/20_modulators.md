---
title: "20. Modulators"
parent: "Part V · Active Devices"
nav_order: 20
permalink: /part-5/ch20/
chapter: 20
---

# <span class="chapnum">Chapter 20</span>Modulators

A modulator writes data onto light; its speed, swing and loss set the reach and energy of an optical link.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- define modulator metrics: extinction ratio, OMA, insertion loss, bandwidth and energy per bit;
- design lumped and travelling-wave MZMs, with velocity and impedance matching;
- design ring modulators, and trade their Q against bandwidth and extinction;
- compare EAMs, TFLN and BTO modulators;
- read NRZ, PAM4 and coherent eye and constellation diagrams, and see what the driver sees.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Mach–Zehnder or ring modulator for a four-wavelength link?

</div>

## <span class="secnum">20.1</span>Modulator metrics

An intensity modulator switches between a high power $$P_1$$ and a low power $$P_0$$. Its quality is described by a handful of numbers:

- **Extinction ratio**, $$\mathrm{ER} = P_1/P_0$$, usually in dB.
- **Optical modulation amplitude**, $$\mathrm{OMA} = P_1 - P_0$$: what the receiver actually sees ([Chapter 1]({% link chapters/01_why.md %})).
- **Insertion loss**: the average transmitted power relative to the input, including the loss of biasing part-way down the transfer curve.
- **Bandwidth**: the frequency at which the electro-optic response falls by 3 dB.
- **Energy per bit**: the electrical energy spent per bit, in the modulator and its driver.
- **Chirp**: unwanted phase modulation that comes with the amplitude modulation and interacts with fibre dispersion.

For PAM4 links, the standards add **TDECQ**, a measure of how much the transmitter's eye closure costs a reference receiver. The first two metrics combine into one key relation:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">OMA, and the energy of a capacitive modulator</div>

$$\mathrm{OMA} = 2P_\mathrm{avg}\,\frac{\mathrm{ER} - 1}{\mathrm{ER} + 1}, \qquad E_\mathrm{bit} \approx \tfrac{1}{4}\,C\,V_{pp}^2\ \ \text{(NRZ, lumped)}$$

</div>

The energy expression counts charging the modulator's capacitance $$C$$ on the transitions of random NRZ data, which occur half the time. A travelling-wave modulator terminated in a resistor $$R$$ instead burns about $$V_{pp}^2/(4R)$$ continuously, whatever the data.

## <span class="secnum">20.2</span>Mach–Zehnder modulators

A **Mach–Zehnder modulator** (MZM) puts phase shifters in both arms of an interferometer ([Chapter 11]({% link chapters/11_mzi.md %})). With a phase difference $$\Delta\phi$$ between the arms, the output is

$$T = \cos^2\!\left(\frac{\Delta\phi}{2}\right), \qquad \Delta\phi = \phi_b + \pi\,\frac{V}{V_\pi}.$$

It is biased at **quadrature**, $$\phi_b = \pi/2$$, where the response is steepest and most linear, and driven with a swing $$V_{pp}$$ around it. A heater usually sets the bias, because the arms are never perfectly balanced. Driving the two arms in opposite directions (**push–pull**) halves the voltage needed and cancels the chirp.

A 3 mm phase shifter is as long as the wavelength of a 25 GHz signal on its electrodes (about 3 mm), so it cannot be treated as a lumped capacitor. **Travelling-wave electrodes** carry the drive signal along the arms as a transmission line terminated in its characteristic impedance, usually 50 Ω. Three conditions set the bandwidth:

- **Velocity matching.** The electrical wave must keep pace with the light: its index $$n_\mathrm{RF}$$ must be close to the optical group index $$n_g$$. Otherwise the light slips out of phase with the drive, and the response falls off at $$f \approx 1.4c/(\pi L\,\lvert n_\mathrm{RF} - n_g\rvert)$$.
- **Impedance matching.** The line must match the driver and the termination, or reflections ripple the response.
- **RF loss.** The electrodes, loaded by the doped junction, attenuate the drive increasingly with frequency, roughly as $$\sqrt{f}$$, so a longer modulator is slower.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 20.1 · A silicon travelling-wave MZM</div>

With $$V_\pi L = 1.4$$ V·cm ([Chapter 19]({% link chapters/19_eo.md %})), a 3 mm modulator has $$V_\pi = 4.7$$ V. Driven with 2 Vpp at quadrature, it gives an extinction ratio of 6.1 dB, and its insertion loss is 6.3 dB: 3.3 dB of free-carrier and waveguide loss over 3 mm, plus 3 dB for sitting at quadrature. With $$n_g = 3.9$$ and $$n_\mathrm{RF} \approx 3.6$$, velocity mismatch alone would allow about 150 GHz; RF loss in the junction-loaded line is what limits real silicon MZMs to around 30–50 GHz at this length. The 50 Ω termination burns $$V_{pp}^2/(4R) = 20$$ mW: 0.4 pJ/bit at 50 Gb/s, before the driver's own losses.

</div>

**Try it.** Change the length, the swing and the bias, compare silicon with thin-film LiNbO₃, and switch to PAM4. The top view shows the travelling-wave electrodes at their length.

{% include demos/mzm.html %}

## <span class="secnum">20.3</span>Ring modulators

A **ring modulator** puts the PN junction in an all-pass ring ([Chapter 12]({% link chapters/12_rings.md %})). The laser sits on the side of a resonance; a voltage shifts the resonance and with it the transmitted power. The shift per volt is

$$\frac{\mathrm{d}\lambda}{\mathrm{d}V} = \frac{\lambda\,F}{n_g}\,\frac{\mathrm{d}n_\mathrm{eff}}{\mathrm{d}V},$$

where $$F$$ is the fraction of the ring covered by the junction. The resonator multiplies a small index change into a large change of transmission, so a ring a few micrometres across does what a millimetre-long MZM does. Its capacitance is tiny, about 20 fF, and so is its energy: $$\tfrac{1}{4} \times 20\ \mathrm{fF} \times (2\ \mathrm{V})^2 = 20$$ fJ/bit, twenty times less than the MZM above.

The price is a set of coupled trade-offs:

- **Q against bandwidth.** A narrow resonance turns a small shift into a large extinction. But light lives in the ring for a photon lifetime $$\tau = Q\lambda/(2\pi c)$$, and the optical bandwidth is limited to about $$c/(\lambda Q_L)$$: 24 GHz at $$Q_L = 8000$$. That combines with the electrical RC limit.
- **Coupling against depth.** A doped ring has an intrinsic $$Q_i$$ of only 10 000–30 000. A loaded Q far below that means strong over-coupling and a shallow dip ([Chapter 12]({% link chapters/12_rings.md %})), which caps the extinction.
- **Heat.** A ring drifts by 75 pm/K, its own absorbed light heats it (**self-heating**), and every ring needs a heater and a locking loop ([Chapter 18]({% link chapters/18_thermal.md %})).

In return, rings are wavelength-selective: four rings on one bus, each on its own channel, modulate four wavelengths and multiplex them in one step. That is the architecture of the reference link.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 20.2 · The reference-link ring modulator</div>

The target is an extinction of at least 4 dB with a 2 Vpp drive and at most 3 dB of insertion loss, at 50 Gb/s ([Chapter 1]({% link chapters/01_why.md %})). The lateral 10¹⁸ cm⁻³ junction of Table 19.1 changes $$n_\mathrm{eff}$$ by $$5.7\times10^{-5}$$ per volt around 2 V. Covering 80 % of a 7.2 µm ring, it shifts the resonance by $$1550 \times 0.8 \times 5.7\times10^{-5}/3.89 = 18$$ pm/V. That is too little: with $$Q_i = 15\,000$$ and $$Q_L = 8000$$ it gives under 2 dB of extinction within the loss budget. An L- or U-shaped junction doubles the efficiency to about 40 pm/V and reaches 3.8 dB, but at 3.2 dB of loss, just over the budget. About 50 pm/V meets the target exactly: 4.2 dB at 3.0 dB. Even then the photon lifetime limits the optical bandwidth to about 24 GHz. For 50 Gb/s NRZ this has to be stretched by the bandwidth peaking that a detuned ring shows, and by equalisation in the driver. The target is achievable but tight, and [Chapter 33]({% link chapters/33_links.md %}) checks the whole budget again.

</div>

**Try it.** Find a junction efficiency, intrinsic and loaded Q, and laser detuning that meet the reference-link target, and see what it costs in bandwidth.

{% include demos/ringmod.html %}

## <span class="secnum">20.4</span>Electro-absorption modulators

An **electro-absorption modulator** (EAM) modulates the absorption directly ([Chapter 19]({% link chapters/19_eo.md %})). On silicon, a short GeSi section using the Franz–Keldysh effect sits in the waveguide. On InP, a quantum-well section using the quantum-confined Stark effect is integrated with a DFB laser in one chip, the **electro-absorption modulated laser** (EML) of many transceivers. EAMs are a few tens of micrometres long, with small capacitance and drive voltages of a volt or two. Their drawbacks are a narrow optical band near the absorption edge, which moves with temperature, some chirp, and the photocurrent they generate as they absorb.

## <span class="secnum">20.5</span>TFLN and BTO modulators

Pockels modulators change the index instantly and without loss. Thin-film lithium niobate MZMs combine $$V_\pi L$$ of about 2–3 V·cm in push–pull with sub-dB/cm loss, and electrodes that can be velocity-matched, giving bandwidths above 100 GHz with CMOS-level drive voltages {% include cite.html keys="wang2018tfln,zhu2021" %}. Their response is linear, which suits coherent IQ modulation and analogue links. Their challenges are integration with silicon circuits, and the slow drift of the bias point in LN. Barium titanate on silicon offers an even larger Pockels coefficient in a silicon process {% include cite.html keys="abel2019" %}, with film quality and long-term stability still being worked out ([Chapter 4]({% link chapters/04_platforms.md %})).

## <span class="secnum">20.6</span>Modulation formats

- **NRZ** (on–off keying): two levels, one bit per symbol. Its eye diagram, all bits overlaid on two symbol periods, has one opening whose height and width set the error rate.
- **PAM4**: four levels, two bits per symbol, at half the symbol rate for the same bit rate. Its three eyes share the swing, each a third as tall as an NRZ eye, which costs about $$10\log_{10}3 = 4.8$$ dB of optical power. A modulator's nonlinear response squeezes the outer eyes, so drivers pre-distort the levels.
- **Coherent IQ**: two nested MZMs, each biased at null, write the in-phase and quadrature parts of the field. A 90° phase between them maps symbols onto a **constellation** in the complex plane: QPSK, 16-QAM and beyond, often in both polarisations. The receiver needs a local oscillator and digital signal processing, which only pays for itself over long distances or very high rates.

## <span class="secnum">20.7</span>Driver and modulator co-design

The electronics sees the modulator very differently depending on its type:

- **A terminated MZM** is a resistive load. The driver must deliver a few volts into 50 Ω at tens of gigahertz, which costs power and needs a SiGe or III-V driver, or a **segmented** MZM whose short sections are each driven by small CMOS inverters, acting like an optical DAC.
- **A ring or EAM** is a small capacitor, which suits CMOS drivers directly. The ring's resonance, though, makes its response depend on wavelength, temperature and the data pattern, so it needs equalisation and a thermal loop in the driver chip.

Every millimetre of wire between the driver and the modulator adds inductance and capacitance, which is why drivers are flip-chipped or 3D-stacked on top of the photonic die, or built into it ([Chapter 1]({% link chapters/01_why.md %})).

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

For a four-wavelength link the ring wins on size, energy (tens of femtojoules per bit against hundreds) and built-in multiplexing. The price is thermal control and a tight trade between Q, extinction and bandwidth. The MZM is broadband, needs no locking and has a large, clean eye, but it costs millimetres of chip, a few decibels more loss, a power-hungry driver, and a separate multiplexer. Short-reach WDM links with tight energy budgets choose rings; links that need robustness or coherent formats choose MZMs.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Four depletion ring modulators with U-shaped junctions (about 50 pm/V), $$Q_L \approx 8000$$, driven with 2 Vpp NRZ by a CMOS driver with equalisation, each locked by its own heater loop. Expected: about 4 dB extinction at about 3 dB insertion loss, roughly 20 fJ/bit in the modulator.

</div>

## Reading

{% include reflist.html keys="reed2010,wang2018tfln,zhu2021,chrostowski2015" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Extinction ratio, OMA, insertion loss, bandwidth and energy per bit describe a modulator; OMA = 2P<sub>avg</sub>(ER − 1)/(ER + 1).
- A 3 mm silicon MZM has V<sub>π</sub> ≈ 4.7 V: 2 Vpp gives about 6 dB of extinction at 6.3 dB of loss and about 0.4 pJ/bit in its termination.
- Travelling-wave electrodes need velocity and impedance matching; RF loss limits long silicon MZMs.
- Ring modulators use about 20 fJ/bit, but their Q trades extinction against bandwidth (c/λQ) and they need thermal locking.
- TFLN gives low-loss, linear, > 100 GHz modulators; EAMs are short but narrow-band; PAM4 halves the symbol rate for a 4.8 dB penalty.

</div>
