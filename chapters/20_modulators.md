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
- read NRZ, PAM4 and coherent eye and constellation diagrams, and see what the driver sees;
- explain a ring modulator's dynamics: bandwidth peaking with detuning, unequal edges, and pre-emphasis for carrier injection;
- drive, linearise and lock a ring modulator.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Mach–Zehnder or ring modulator for a four-wavelength link?

</div>

## <span class="secnum">20.1</span>Modulator metrics

An intensity modulator switches between a high power $$P_1$$ and a low power $$P_0$$. Its quality is described by a handful of numbers ([Figure 20.1](#fig-20-1)):

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

<figure id="fig-20-1">
  <img src="{{ '/assets/figs/ch20_metrics.svg' | relative_url }}" style="width:600px" alt="An optical NRZ waveform for a 16-bit pattern at 50 Gb/s switching between P1 at 0.72 and P0 at 0.28 of the input power, with the average power at 0.5; brackets mark the OMA between the levels and the 3 dB insertion loss between the input power and the average, and the extinction ratio is 4.0 dB">
  <figcaption><span class="capnum">Figure 20.1.</span> <strong>What the metrics measure.</strong> The output of a modulator that just meets the reference-link target, 4 dB extinction at 3 dB insertion loss, for a 50 Gb/s NRZ pattern. The levels are 0.72 and 0.28 of the input power; the insertion loss is counted from the input power to the average, 0.50; the OMA, 0.43 of the input power, is 0.86 times the average power. Smoothed edges are illustrative. Drawn by <code>figsrc/ch20_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">20.2</span>Mach–Zehnder modulators

A **Mach–Zehnder modulator** (MZM) puts phase shifters in both arms of an interferometer ([Chapter 11]({% link chapters/11_mzi.md %})). With a phase difference $$\Delta\phi$$ between the arms, the output is

$$T = \cos^2\!\left(\frac{\Delta\phi}{2}\right), \qquad \Delta\phi = \phi_b + \pi\,\frac{V}{V_\pi}.$$

It is biased at **quadrature**, $$\phi_b = \pi/2$$, where the response is steepest and most linear, and driven with a swing $$V_{pp}$$ around it. A heater usually sets the bias, because the arms are never perfectly balanced. Driving the two arms in opposite directions (**push–pull**) halves the voltage needed and cancels the chirp.

A 3 mm phase shifter is as long as the wavelength of a 25 GHz signal on its electrodes (about 3 mm), so it cannot be treated as a lumped capacitor. **Travelling-wave electrodes** carry the drive signal along the arms as a transmission line terminated in its characteristic impedance, usually 50 Ω ([Figure 20.2](#fig-20-2)). Three conditions set the bandwidth:

- **Velocity matching.** The electrical wave must keep pace with the light: its index $$n_\mathrm{RF}$$ must be close to the optical group index $$n_g$$. Otherwise the light slips out of phase with the drive, and the response falls off at $$f \approx 1.4c/(\pi L\,\lvert n_\mathrm{RF} - n_g\rvert)$$.
- **Impedance matching.** The line must match the driver and the termination, or reflections ripple the response.
- **RF loss.** The electrodes, loaded by the doped junction, attenuate the drive increasingly with frequency, roughly as $$\sqrt{f}$$, so a longer modulator is slower.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 20.1 · A silicon travelling-wave MZM</div>

With $$V_\pi L = 1.4$$ V·cm ([Chapter 19]({% link chapters/19_eo.md %})), a 3 mm modulator has $$V_\pi = 4.7$$ V. Driven with 2 Vpp at quadrature, it gives an extinction ratio of 6.1 dB, and its insertion loss is 6.3 dB: 3.3 dB of free-carrier and waveguide loss over 3 mm, plus 3 dB for sitting at quadrature. With $$n_g = 3.9$$ and $$n_\mathrm{RF} \approx 3.6$$, velocity mismatch alone would allow about 150 GHz; RF loss in the junction-loaded line is what limits real silicon MZMs to around 30–50 GHz at this length. The 50 Ω termination burns $$V_{pp}^2/(4R) = 20$$ mW: 0.4 pJ/bit at 50 Gb/s, before the driver's own losses.

</div>

<figure id="fig-20-2">
  <img src="{{ '/assets/figs/ch20_mzm.svg' | relative_url }}" style="width:600px" alt="Top: schematic top view of a Mach-Zehnder modulator with a splitter, two arms, signal and ground electrode strips running along the arms from a driver to a 50 ohm termination, a DC bias line between the arms, a heater on one arm, and arrows for the RF wave and the light travelling the same way. Bottom: cross-section through the two arms, to scale, with two PN rib waveguides back to back sharing an n-plus-plus region in the middle, vias up to the signal electrode on the left, the ground on the right and a DC bias contact in the middle">
  <figcaption><span class="capnum">Figure 20.2.</span> <strong>A travelling-wave silicon MZM.</strong> (a) Top view (not to scale): the drive enters the electrodes at the input end and travels with the light to a 50 Ω termination, so the light sees the same part of the signal all along the arms if \(n_\mathrm{RF} \approx n_g\); a heater sets the bias point. (b) Cross-section A–A′, to scale for the silicon (the 500 × 220 nm ribs and lateral junctions of Chapter 19): in this series push–pull arrangement the two junctions sit back to back between the signal and ground lines, and a DC bias \(V_b\) on the shared n⁺⁺ region keeps both reverse-biased. The drive \(v\) divides between them, adding to one junction's bias and taking from the other's, so the arms' phases move in opposite directions. Electrode heights and the arm spacing are illustrative. Drawn by <code>figsrc/ch20_figs.py</code>.</figcaption>
</figure>

**Try it.** Change the length, the swing and the bias, compare silicon with thin-film LiNbO₃, and switch to PAM4. The top view shows the travelling-wave electrodes at their length.

{% include demos/mzm.html %}

## <span class="secnum">20.3</span>Ring modulators

A **ring modulator** puts the PN junction in an all-pass ring ([Chapter 12]({% link chapters/12_rings.md %}), [Figure 20.3](#fig-20-3)). The laser sits on the side of a resonance; a voltage shifts the resonance and with it the transmitted power. The shift per volt is

$$\frac{\mathrm{d}\lambda}{\mathrm{d}V} = \frac{\lambda\,F}{n_g}\,\frac{\mathrm{d}n_\mathrm{eff}}{\mathrm{d}V},$$

where $$F$$ is the fraction of the ring covered by the junction. The resonator multiplies a small index change into a large change of transmission, so a ring a few micrometres across does what a millimetre-long MZM does. Its capacitance is tiny, about 20 fF, and so is its energy: $$\tfrac{1}{4} \times 20\ \mathrm{fF} \times (2\ \mathrm{V})^2 = 20$$ fJ/bit, twenty times less than the MZM above.

The price is a set of coupled trade-offs:

- **Q against bandwidth.** A narrow resonance turns a small shift into a large extinction. But light lives in the ring for a photon lifetime $$\tau = Q\lambda/(2\pi c)$$, and the optical bandwidth is limited to about $$c/(\lambda Q_L)$$: 24 GHz at $$Q_L = 8000$$. That combines with the electrical RC limit.
- **Coupling against depth.** A doped ring has an intrinsic $$Q_i$$ of only 10 000–30 000. A loaded Q far below that means strong over-coupling and a shallow dip ([Chapter 12]({% link chapters/12_rings.md %})), which caps the extinction.
- **Heat.** A ring drifts by 75 pm/K, its own absorbed light heats it (**self-heating**), and every ring needs a heater and a locking loop ([Chapter 18]({% link chapters/18_thermal.md %})).

In return, rings are wavelength-selective: four rings on one bus, each on its own channel, modulate four wavelengths and multiplex them in one step. That is the architecture of the reference link.

<figure id="fig-20-3">
  <img src="{{ '/assets/figs/ch20_ring.svg' | relative_url }}" style="width:600px" alt="Left: top view of a 7.2 micrometre ring modulator over a bus waveguide, with p doping on the inside and n doping on the outside of the ring along 80 percent of it, rows of contact vias on inner p-plus-plus and outer n-plus-plus rings, and the dashed outline of a TiN heater above the ring. Right: three small cross-sections of the rib showing a lateral junction in the middle, a junction offset towards the n side, and an L-shaped junction that turns under the n region">
  <figcaption><span class="capnum">Figure 20.3.</span> <strong>A depletion ring modulator.</strong> (a) Top view to scale: the 7.2 µm ring of Worked Example 20.2 (FSR 13.7 nm), with its junction along 80 % of the circumference, away from the bus coupler; contact vias on p⁺⁺ and n⁺⁺ rings inside and outside, and a TiN heater above the ring for tuning and locking (outline). The 200 nm gap and the contact radii are illustrative. (b)–(d) Junction shapes in the 500 × 220 nm rib: the lateral junction of Table 19.1, a junction offset towards the n side so that more of the mode sits in the p-type silicon, and an L-shaped junction that runs under part of the rib, so more of the mode is crossed by the depletion edge. U-shaped junctions wrap it further. Doping profiles schematic. Drawn by <code>figsrc/ch20_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 20.2 · The reference-link ring modulator</div>

The target is an extinction of at least 4 dB with a 2 Vpp drive and at most 3 dB of insertion loss, at 50 Gb/s ([Chapter 1]({% link chapters/01_why.md %})). The lateral 10¹⁸ cm⁻³ junction of Table 19.1 changes $$n_\mathrm{eff}$$ by $$5.7\times10^{-5}$$ per volt around 2 V. Covering 80 % of a 7.2 µm ring, it shifts the resonance by $$1550 \times 0.8 \times 5.7\times10^{-5}/3.89 = 18$$ pm/V. That is too little: with $$Q_i = 15\,000$$ and $$Q_L = 8000$$ it gives under 2 dB of extinction within the loss budget. An L- or U-shaped junction doubles the efficiency to about 40 pm/V and reaches 3.8 dB, but at 3.2 dB of loss, just over the budget. About 50 pm/V meets the target: 4.3 dB at 3.0 dB. Even then the photon lifetime limits the optical bandwidth to about 24 GHz. For 50 Gb/s NRZ this has to be stretched by the bandwidth peaking that a detuned ring shows, and by equalisation in the driver. The target is achievable but tight, and [Chapter 33]({% link chapters/33_links.md %}) checks the whole budget again.

</div>

**Try it.** Find a junction efficiency, intrinsic and loaded Q, and laser detuning that meet the reference-link target, and see what it costs in bandwidth.

{% include demos/ringmod.html %}

## <span class="secnum">20.4</span>Electro-absorption modulators

An **electro-absorption modulator** (EAM) modulates the absorption directly ([Chapter 19]({% link chapters/19_eo.md %})). On silicon, a short GeSi section using the Franz–Keldysh effect sits in the waveguide ([Figure 20.4](#fig-20-4)). On InP, a quantum-well section using the quantum-confined Stark effect is integrated with a DFB laser in one chip, the **electro-absorption modulated laser** (EML) of many transceivers. EAMs are a few tens of micrometres long, with small capacitance and drive voltages of a volt or two. Their drawbacks are a narrow optical band near the absorption edge, which moves with temperature, some chirp, and the photocurrent they generate as they absorb.

<figure id="fig-20-4">
  <img src="{{ '/assets/figs/ch20_eam.svg' | relative_url }}" style="width:600px" alt="Left: top view of a germanium-silicon electro-absorption modulator, a 40 micrometre long GeSi stripe butt-coupled into a silicon waveguide through short tapers, between p-plus-plus and n-plus-plus silicon regions with rows of contacts. Right: cross-section through the GeSi stripe between the doped silicon regions, with a red arrow for the lateral field across it">
  <figcaption><span class="capnum">Figure 20.4.</span> <strong>A GeSi electro-absorption modulator.</strong> (a) Top view: a GeSi section a few tens of micrometres long sits in the silicon waveguide, with short tapers at both ends and heavily doped silicon on either side. (b) Cross-section B–B′: a reverse bias across the lateral PIN puts a field through the GeSi, moving its absorption edge onto the operating wavelength (<a href="{% link chapters/19_eo.md %}#fig-19-5">Figure 19.5</a>). To scale, with illustrative dimensions (40 µm long, 0.8 µm wide). Drawn by <code>figsrc/ch20_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">20.5</span>TFLN and BTO modulators

Pockels modulators change the index instantly and without loss. Thin-film lithium niobate MZMs combine $$V_\pi L$$ of about 2–3 V·cm in push–pull with sub-dB/cm loss, and electrodes that can be velocity-matched, giving bandwidths above 100 GHz with CMOS-level drive voltages {% include cite.html keys="wang2018tfln,zhu2021" %}. Their response is linear, which suits coherent IQ modulation and analogue links. Their challenges are integration with silicon circuits, and the slow drift of the bias point in LN. Barium titanate on silicon offers an even larger Pockels coefficient in a silicon process {% include cite.html keys="abel2019" %}, with film quality and long-term stability still being worked out ([Chapter 4]({% link chapters/04_platforms.md %})).

## <span class="secnum">20.6</span>Modulation formats

- **NRZ** (on–off keying): two levels, one bit per symbol ([Figure 20.5](#fig-20-5)). Its eye diagram, all bits overlaid on two symbol periods, has one opening whose height and width set the error rate.
- **PAM4**: four levels, two bits per symbol, at half the symbol rate for the same bit rate. Its three eyes share the swing, each a third as tall as an NRZ eye, which costs about $$10\log_{10}3 = 4.8$$ dB of optical power. A modulator's nonlinear response squeezes the outer eyes, so drivers pre-distort the levels.
- **Coherent IQ**: two nested MZMs, each biased at null, write the in-phase and quadrature parts of the field. A 90° phase between them maps symbols onto a **constellation** in the complex plane: QPSK, 16-QAM and beyond, often in both polarisations. The receiver needs a local oscillator and digital signal processing, which only pays for itself over long distances or very high rates.

<figure id="fig-20-5">
  <img src="{{ '/assets/figs/ch20_formats.svg' | relative_url }}" style="width:600px" alt="Left: the same 16 bits sent at 50 Gb/s as NRZ, two levels at 50 gigabaud, and as PAM4, four levels at 25 gigabaud with each symbol labelled by its bit pair. Top right: schematic IQ modulator, two Mach-Zehnder modulators biased at null in the arms of an outer interferometer, with a 90 degree phase shifter on one. Bottom right: QPSK constellation of four points with Gray-coded labels on the I-Q plane, over the 16 points of 16-QAM">
  <figcaption><span class="capnum">Figure 20.5.</span> <strong>Modulation formats.</strong> (a) NRZ: the 16 bits at 50 Gb/s, one bit per 20 ps symbol. (b) PAM4: the same bits in pairs (Gray code), one of four levels per 40 ps symbol, at half the symbol rate; each eye is a third of the swing, a 4.8 dB penalty. (c) An IQ modulator (schematic): two MZMs biased at null write the in-phase and quadrature fields, combined with a 90° phase between them. (d) The QPSK constellation it writes, with Gray-coded bit pairs, and the 16 points of 16-QAM. Drawn by <code>figsrc/ch20_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">20.7</span>Driver and modulator co-design

The electronics sees the modulator very differently depending on its type:

- **A terminated MZM** is a resistive load. The driver must deliver a few volts into 50 Ω at tens of gigahertz, which costs power and needs a SiGe or III-V driver, or a **segmented** MZM whose short sections are each driven by small CMOS inverters, acting like an optical DAC.
- **A ring or EAM** is a small capacitor, which suits CMOS drivers directly. The ring's resonance, though, makes its response depend on wavelength, temperature and the data pattern, so it needs equalisation and a thermal loop in the driver chip (Sections 20.8 and 20.9).

Every millimetre of wire between the driver and the modulator adds inductance and capacitance, which is why drivers are flip-chipped or 3D-stacked on top of the photonic die, or built into it ([Chapter 1]({% link chapters/01_why.md %})).

## <span class="secnum">20.8</span>Ring-modulator dynamics

At the operating point of Worked Example 20.2, the laser sits 109 pm, or 0.56 linewidths, blue of the resonance, where the insertion loss is 3.0 dB. How fast the ring follows its drive depends on that same detuning {% include cite.html keys="palermo721l11" %}. A coupled-mode model, one resonant mode whose stored field decays at half the linewidth and leaks into the bus, gives the small-signal response of [Figure 20.6](#fig-20-6):

- With the laser at the centre of the resonance, the ring behaves as a single pole at half its linewidth: 12.1 GHz for the 24.2 GHz linewidth of $$Q_L = 8000$$.
- Detuned, the response peaks. The light leaking out of the ring beats with the laser at the detuning frequency, so modulation near that frequency is enhanced. At the reference detuning the peak is 2.6 dB at 15 GHz and the 3 dB bandwidth is 38 GHz; a full linewidth away it would be 86 GHz.

The price is extinction. The further the laser sits from the resonance, the less a given shift changes the transmission: with 2 Vpp at 50 pm/V, 12 dB at 0.35 linewidths, about 4 dB at the reference point, and 1 dB at a full linewidth. The operating point is therefore a three-way compromise between extinction, loss and speed. [Chapter 33]({% link chapters/33_links.md %}) conservatively models this transmitter as a single pole at the 24 GHz linewidth.

<figure id="fig-20-6">
  <img src="{{ '/assets/figs/ch20_rrm_response.svg' | relative_url }}" style="width:720px" alt="Left: small-signal modulation response of the reference ring for laser detunings from 0.15 to 1 linewidth, rising from a 12 GHz single pole to strongly peaked responses. Right: 3 dB bandwidth rising and extinction at 2 Vpp falling with detuning, with the operating point of Worked Example 20.2 at 0.56 linewidths and 38 GHz">
  <figcaption><span class="capnum">Figure 20.6.</span> <strong>A detuned ring is faster but extinguishes less.</strong> (a) Small-signal response of the output power of the reference ring (\(Q_i = 15\,000\), \(Q_L = 8000\)) to a sinusoidal shift of its resonance, for the laser placed 0.15 to 1 linewidth blue of the resonance. (b) The 3 dB bandwidth (solid) and the extinction for a 2 Vpp, 50 pm/V drive (dashed) against the detuning; the dot is the operating point of Worked Example 20.2. Single-mode coupled-mode theory, no electrical (RC) limit. Drawn by <code>figsrc/ch20_rrm.py</code>.</figcaption>
</figure>

A 2 Vpp swing moves the resonance by 100 pm, half a linewidth, so the small-signal picture is only a guide: across the swing the detuning varies from 0.30 to 0.82 linewidths, and the speed with it. [Figure 20.7](#fig-20-7) shows the two edges for ideal voltage steps. When the reverse bias rises, the resonance moves away from the laser and the stored light escapes, beating with the laser: the output rises in 5.8 ps (10 to 90 %), overshooting by 42 %. When the bias falls, the resonance moves onto the laser and the ring must fill up: the output falls in 11.4 ps, with only 6 % overshoot. Rising and falling transitions therefore leave different intersymbol interference behind them, which a single linear equaliser cannot cancel at once.

<figure id="fig-20-7">
  <img src="{{ '/assets/figs/ch20_rrm_edges.svg' | relative_url }}" style="width:560px" alt="Normalised output-power transitions of the reference ring for a rising and a falling 2 V step: the rising edge is fast with a large overshoot, the falling edge slower and smoother">
  <figcaption><span class="capnum">Figure 20.7.</span> <strong>A ring modulator's edges are unequal.</strong> Output power of the reference ring after ideal 2 V steps, normalised from its old to its new level. Moving the resonance away from the laser (blue) takes 5.8 ps from 10 to 90 % with 42 % overshoot; moving it onto the laser (red) takes 11.4 ps with 6 %. Coupled-mode theory at the operating point of Worked Example 20.2, no electrical limit. Drawn by <code>figsrc/ch20_rrm.py</code>.</figcaption>
</figure>

### Carrier injection and pre-emphasis

[Chapter 19]({% link chapters/19_eo.md %}) described the other silicon junction, a forward-biased PIN diode that floods the waveguide with electrons and holes. In a ring it is very efficient {% include cite.html keys="palermo721l11" %}. With the core weight of Chapter 19's mode (0.92) and the Soref–Bennett relations, $$2.7\times10^{17}$$ cm⁻³ of each carrier in the core of a 7.2 µm ring moves the resonance 291 pm blue, one and a half linewidths. Holding them there against recombination, with a 1 ns lifetime, takes 172 µA, about 155 µW at 0.9 V. The carriers also absorb: the intrinsic Q falls from 15 000 to 11 200.

Speed is the problem. The stored charge follows

$$\frac{\mathrm{d}Q}{\mathrm{d}t} = I - \frac{Q}{\tau},$$

so with the holding current alone the charge reaches only 9.5 % of its final value in a 100 ps bit at 10 Gb/s. Driving harder does not help ([Figure 20.8](#fig-20-8), red): five times the holding current shifts the ring quickly at first, but the charge keeps piling up during runs of "1"s and drains with the 1 ns lifetime, so the "0"s after a run stay bright and the eye closes. **Pre-emphasis** shapes the current instead (blue). A short forward pulse at each rising edge delivers the charge of a "1" in 40 ps, the holding current keeps it, and a reverse pulse at each falling edge sweeps it out. The pulse needs 25 times the holding current, but because a diode's current grows exponentially with its voltage, that takes only about 0.12 V more forward bias (ideality factor 1.5, series resistance neglected). The optical eye opens fully: the lowest "1" transmits 0.87, the highest "0" 0.004. The pulse width, the pulse depth and the DC bias all trade against each other, and a model that couples the diode's charge to the ring's optics is what lets a designer choose them.

<figure id="fig-20-8">
  <img src="{{ '/assets/figs/ch20_injection.svg' | relative_url }}" style="width:720px" alt="Top: stored charge in a carrier-injection ring at 10 Gb/s, which piles up and drains slowly under a plain NRZ current but switches cleanly between zero and the one level with pre-emphasis pulses. Bottom: the ring's transmission, closed for the plain drive and fully open with pre-emphasis">
  <figcaption><span class="capnum">Figure 20.8.</span> <strong>Pre-emphasis for a carrier-injection ring.</strong> Top: stored charge, in units of the charge that shifts the resonance by 1.5 linewidths, for a 10 Gb/s pattern (shaded bits are "1"). A plain NRZ current of five times the holding current (red) piles charge up and drains it with the 1 ns carrier lifetime; the holding current with 40 ps forward and reverse pulses on the edges (blue) switches it cleanly. Bottom: the transmission of the ring, with the laser at the unbiased resonance; the carriers' absorption is included. Charge-control model, quasi-static ring (its 6.6 ps photon lifetime is far shorter than a bit). Drawn by <code>figsrc/ch20_rrm.py</code>.</figcaption>
</figure>

## <span class="secnum">20.9</span>Driving, linearising and locking a ring

**High-swing drivers.** A depletion ring with half the reference ring's efficiency, 25 pm/V, needs 4 Vpp for the same 100 pm shift, four times the energy (80 fJ/bit at 20 fF), and more voltage than a thin-oxide CMOS transistor can switch {% include cite.html keys="palermo721l11" %}. Two techniques get there:

- **Stacking.** Output stages with cascoded transistors between two supply rails let each transistor see only part of the swing. Merging the main and post-cursor taps into one stack, rather than putting a stack in every segment, keeps any transistor from being overstressed during transitions and cuts the output capacitance.
- **Differential, AC-coupled drive.** Driving the cathode and the anode in antiphase doubles the swing across the junction, and coupling capacitors let each terminal sit at its own DC bias through a large resistor, so the junction stays reverse-biased whatever the supplies. With 2 pF coupling capacitors, 50 kΩ bias resistors and 70 fF of ring and pad capacitance, 97 % of the swing (−0.3 dB) reaches the ring, the high-pass corner is at 1.6 MHz, and a run of 72 identical bits at 50 Gb/s droops by only 1.4 %.

Because the two edges differ ([Figure 20.7](#fig-20-7)), ring drivers use an **asymmetric FFE**: the post-cursor tap is set separately for rising and falling transitions, or for the "1" and "0" levels.

**PAM4 on a ring.** The Lorentzian bends the ring's transfer curve. At the reference operating point, four equally spaced drive voltages give three eyes in the ratio 1.34 : 0.99 : 0.67 ([Figure 20.9](#fig-20-9)). The smallest eye sets the error rate, a penalty of 1.8 dB on top of PAM4's 4.8 dB. Pre-distorting the drive, with levels at 0, 0.48, 1.08 and 2 V instead of 0, 0.67, 1.33 and 2 V, makes the eyes equal again. Transmitters do this with a DAC-based output stage and a look-up table that also applies a nonlinear FFE, or with a ring whose phase shifter is split into two segments, driven by the most and the least significant bit with independently set swings: an optical DAC {% include cite.html keys="palermo721l11,palermo721l13" %}.

<figure id="fig-20-9">
  <img src="{{ '/assets/figs/ch20_pam4.svg' | relative_url }}" style="width:560px" alt="Transmission of the reference ring against drive voltage across the 2 Vpp swing, a concave curve; four equally spaced voltages give unequal output levels, while four pre-distorted voltages give equally spaced levels">
  <figcaption><span class="capnum">Figure 20.9.</span> <strong>PAM4 on a ring modulator.</strong> Transmission of the reference ring across its 2 Vpp swing at the operating point of Worked Example 20.2. Equally spaced drive voltages (red dots) give eyes in the ratio 1.34 : 0.99 : 0.67, a 1.8 dB penalty for the smallest; pre-distorted voltages of 0, 0.48, 1.08 and 2 V (blue squares) give equal eyes. Static Lorentzian model of the ring demo. Drawn by <code>figsrc/ch20_rrm.py</code>.</figcaption>
</figure>

**Locking with data on.** Locking a modulator differs from locking a drop filter ([Chapter 18]({% link chapters/18_thermal.md %})): data are on, and the target is not the resonance but a detuning. A common loop holds the average through-port power at a reference that a DAC sets, as a fraction of the input power {% include cite.html keys="palermo721l11" %}. At the reference point the average transmission is 0.50 and changes by 0.0046 per picometre of detuning, so even a 0.1 K drift (7.5 pm) moves it by 0.034: a strong error signal, and a monotonic one on the blue side of the resonance, where the loop runs. On the red side the slope reverses, so at start-up the controller heats the ring through the dip before it closes the loop. Two actuators can share the work:

- **Heaters** shift the ring red only, over a whole free spectral range, at about 0.26 nm/mW, but in tens of microseconds ([Chapter 18]({% link chapters/18_thermal.md %})).
- **Bias** is fast. A depletion ring's DC bias moves it 50 pm per volt at almost no power, but ±1 V covers only ±0.67 K of drift, so bias suits fine, fast correction. An injection ring's forward bias moves it blue far more efficiently than heat (0.28 nm for about 150 µW, against 1.1 mW for a heater), but its carriers add loss: the intrinsic Q falls from 15 000 to 11 300.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Answer to the design question</div>

For a four-wavelength link the ring wins on size, energy (tens of femtojoules per bit against hundreds) and built-in multiplexing. The price is thermal control and a tight trade between Q, extinction and bandwidth. The MZM is broadband, needs no locking and has a large, clean eye, but it costs millimetres of chip, a few decibels more loss, a power-hungry driver, and a separate multiplexer. Short-reach WDM links with tight energy budgets choose rings; links that need robustness or coherent formats choose MZMs.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Reference-link choice</div>

Four depletion ring modulators with U-shaped junctions (about 50 pm/V), $$Q_L \approx 8000$$, driven with 2 Vpp NRZ by a CMOS driver with equalisation, each locked by its own heater loop. Expected: about 4 dB extinction at about 3 dB insertion loss, roughly 20 fJ/bit in the modulator.

</div>

## Reading

{% include reflist.html keys="reed2010,wang2018tfln,zhu2021,chrostowski2015,sackinger2005,palermo721l11" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Extinction ratio, OMA, insertion loss, bandwidth and energy per bit describe a modulator; OMA = 2P<sub>avg</sub>(ER − 1)/(ER + 1).
- A 3 mm silicon MZM has V<sub>π</sub> ≈ 4.7 V: 2 Vpp gives about 6 dB of extinction at 6.3 dB of loss and about 0.4 pJ/bit in its termination.
- Travelling-wave electrodes need velocity and impedance matching; RF loss limits long silicon MZMs.
- Ring modulators use about 20 fJ/bit, but their Q trades extinction against bandwidth (c/λQ) and they need thermal locking.
- TFLN gives low-loss, linear, > 100 GHz modulators; EAMs are short but narrow-band; PAM4 halves the symbol rate for a 4.8 dB penalty.
- A detuned ring's response peaks: the reference ring's small-signal bandwidth rises from 12 GHz on resonance to 38 GHz at its operating point, at the cost of extinction. Its edges are unequal (5.8 and 11.4 ps), so drivers use asymmetric FFE.
- Carrier-injection rings are efficient but held back by the 1 ns carrier lifetime; pre-emphasis pulses of about 25 times the holding current open the eye.
- A ring bends PAM4 levels (a 1.8 dB penalty for the smallest eye) unless the drive is pre-distorted; ring modulators lock to an average-power reference with heaters, and fine-tune with bias.

</div>
