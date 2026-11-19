---
title: "12. Ring Resonators"
parent: "Part III · Passive Devices"
nav_order: 12
permalink: /part-3/ch12/
chapter: 12
---

# <span class="chapnum">Chapter 12</span>Ring Resonators

Loop a waveguide back on itself and you get a filter, a sensor, a modulator or a laser mirror, depending on what you do with it.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the all-pass and add-drop transfer functions from a coupler and a round trip;
- define the free spectral range, finesse, loaded and intrinsic Q and extinction ratio;
- explain under-, critical and over-coupling;
- extract loss and coupling from a measured resonance, and see why one spectrum is ambiguous;
- explain split resonances and thermal drift, and list the applications of rings.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do coupling and loss shape a ring's resonance, and which gap gives the resonance you want?

</div>

## <span class="secnum">12.1</span>Resonance condition

A ring of radius $$R$$ and circumference $$L = 2\pi R$$ ([Figure 12.1](#fig-12-1)) is resonant when light returns in phase after one round trip, $$\beta L = 2\pi m$$, that is when

$$m\lambda_m = n_\mathrm{eff}L, \qquad m = 1, 2, 3, \dots$$

Adjacent resonances are separated by the **free spectral range**, which, as for the MZI ([Chapter 11]({% link chapters/11_mzi.md %})), involves the group index:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Free spectral range of a ring</div>

$$\mathrm{FSR} = \frac{\lambda^2}{n_gL}$$

</div>

A 10 µm radius silicon ring ($$L = 62.8$$ µm, $$n_g = 4.18$$) has FSR = $$1.55^2/(4.18 \times 62.8) = 9.15$$ nm. For the four channels of the reference link, spread over 9.6 nm, the FSR must exceed that span; [Chapter 14]({% link chapters/14_wdm.md %}) makes it four channel spacings (12.8 nm), so that each ring's next resonance lands on an empty slot, which calls for rings of 7.15 µm radius or less.


<figure id="fig-12-1">
  <img src="{{ '/assets/figs/ch12_geometry.svg' | relative_url }}" style="width:600px" alt="Top views, to scale, of an all-pass ring and an add-drop ring of 10 micrometre radius made of 500 nm wide silicon waveguides, with the input, through, drop and add ports and the coupler and round-trip parameters labelled, and a cross-section of the 200 nm coupling gap between two 500 by 220 nm strips">
  <figcaption><span class="capnum">Figure 12.1.</span> <strong>Ring geometries, to scale.</strong> (a) An all-pass ring: a 10 µm radius ring of 500 nm wide silicon strip beside one bus, 200 nm away (too narrow to see at this scale). The coupler passes a field fraction \(t\) straight on and crosses \(\kappa\) over; one round trip transmits \(a\) with phase \(\phi = \beta L\). (b) The add-drop ring adds a second bus, whose coupler (\(t_2\), \(\kappa_2\)) sends the resonant light to the drop port. (c) Cross-section at the closest approach: two 500 × 220 nm strips 200 nm apart in oxide. Drawn by <code>figsrc/ch12_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">12.2</span>The all-pass ring

Couple the ring to a single bus waveguide ([Figure 12.1a](#fig-12-1)) through a short directional coupler with field self-coupling $$t$$ and cross-coupling $$\kappa$$ ($$t^2 + \kappa^2 = 1$$, [Chapter 9]({% link chapters/09_couplers.md %})), and let $$a$$ be the field transmission of one round trip ($$a^2 = e^{-\alpha L}$$) and $$\phi = \beta L$$ its phase. Summing the light that circulates any number of times gives the through-port transmission {% include cite.html keys="bogaerts2012" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">All-pass ring</div>

$$T(\phi) = \frac{a^2 - 2at\cos\phi + t^2}{1 - 2at\cos\phi + (at)^2}$$

</div>

Off resonance $$T \approx 1$$; on resonance ($$\phi = 2\pi m$$) it dips to $$T_\mathrm{min} = (a - t)^2/(1 - at)^2$$. The dip reaches zero when $$t = a$$, **critical coupling**: the light coupled back out of the ring then exactly cancels the light that passed by, because the coupler's loss of transmission equals the ring's loss per round trip. For $$t > a$$ the ring is **under-coupled** (it loses more than it couples, giving a narrow, shallow dip); for $$t < a$$ it is **over-coupled** (a broad, shallow dip). [Figure 12.2](#fig-12-2) shows the three regimes for the ring of Table 12.1.

<figure id="fig-12-2">
  <img src="{{ '/assets/figs/ch12_regimes.svg' | relative_url }}" style="width:600px" alt="Two plots against detuning from resonance for gaps of 200, 250, 283 and 300 nm: the through-port transmission in decibels, deepest at the 283 nm critical gap, and the through-port phase, which turns by nearly 2 pi for the over-coupled rings, jumps by pi at critical coupling and swings and returns for the under-coupled ring">
  <figcaption><span class="capnum">Figure 12.2.</span> <strong>Under-, critical and over-coupling.</strong> Through-port transmission (a) and phase (b) of the 10 µm ring at 2 dB/cm for the gaps of Table 12.1 and for the critical gap, 283 nm, where \(t = a\) in the coupler model of Chapter 9. The dip is deepest at critical coupling. Across the resonance the phase of an over-coupled ring turns by a full 2π, while that of an under-coupled ring swings and returns: a phase measurement tells the two apart (Section 12.5). Drawn by <code>figsrc/ch12_figs.py</code>.</figcaption>
</figure>

**Try it.** Change the radius, gap and loss, and tune the laser across a resonance to watch the light build up in the ring.

{% include demos/ring.html %}

## <span class="secnum">12.3</span>The add-drop ring

A second bus on the other side of the ring ([Figure 12.1b](#fig-12-1)), with couplings $$t_2$$ and $$\kappa_2$$, drops the resonant light into a separate port:

$$T_\mathrm{through} = \frac{t_2^2a^2 - 2t_1t_2a\cos\phi + t_1^2}{1 - 2t_1t_2a\cos\phi + (t_1t_2a)^2}, \qquad T_\mathrm{drop} = \frac{(1 - t_1^2)(1 - t_2^2)\,a}{1 - 2t_1t_2a\cos\phi + (t_1t_2a)^2}.$$

With equal couplers and no loss, the drop port takes all the power on resonance and nothing off resonance ([Figure 12.3](#fig-12-3)): a bandpass filter. Rings in series on a bus, each with its own resonance, make a multiplexer or demultiplexer, exactly the receiver of the reference link ([Chapter 14]({% link chapters/14_wdm.md %})).


<figure id="fig-12-3">
  <img src="{{ '/assets/figs/ch12_adddrop.svg' | relative_url }}" style="width:460px" alt="Drop-port and through-port transmission in decibels against detuning for a 10 micrometre add-drop ring with two 200 nm gaps, lossless and at 2 dB per centimetre: the drop port peaks at 0 dB without loss and about minus 1 dB with loss, and the through-port dip is complete without loss and about 20 dB deep with loss">
  <figcaption><span class="capnum">Figure 12.3.</span> <strong>An add-drop ring.</strong> Drop (blue) and through (amber) ports of the 10 µm ring with two identical 200 nm gaps. Without loss (dashed) the drop port takes all the power on resonance and the through port falls to zero. At 2 dB/cm the drop peak is 0.96 dB down and the through port keeps 19.6 dB of extinction. The second coupler broadens the resonance to 40 pm (\(Q_L \approx 38\,000\)). Drawn by <code>figsrc/ch12_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">12.4</span>Quality factor and finesse

The width of a resonance is described by its full width at half maximum, its **quality factor** $$Q = \lambda/\Delta\lambda_\mathrm{FWHM}$$, and its **finesse** $$F = \mathrm{FSR}/\Delta\lambda_\mathrm{FWHM}$$ ([Figure 12.4](#fig-12-4)). For the all-pass ring

$$\Delta\lambda_\mathrm{FWHM} = \frac{(1 - at)\,\lambda^2}{\pi n_gL\sqrt{at}}.$$

<figure id="fig-12-4">
  <img src="{{ '/assets/figs/ch12_anatomy.svg' | relative_url }}" style="width:600px" alt="Left: the through-port transmission of the 10 micrometre ring from 1529 to 1566 nm, with narrow dips labelled by their orders m equals 98 to 101 and free spectral ranges of 9.00, 9.11 and 9.22 nm between them. Right: one resonance near 1551.4 nm magnified, with its 11.7 pm full width at half maximum, its 11.0 dB extinction and a loaded Q of 132 000">
  <figcaption><span class="capnum">Figure 12.4.</span> <strong>Free spectral range, linewidth and Q.</strong> The 10 µm ring with a 250 nm gap at 2 dB/cm (Table 12.1). (a) One resonance per order \(m\), where \(m\lambda = n_\mathrm{eff}L\); the FSR grows from 9.00 to 9.22 nm across the band because it scales with \(\lambda^2\). (b) The resonance at 1551.40 nm: FWHM 11.7 pm and extinction 11.0 dB, so \(Q_L = 132\,000\) and the finesse \(F = \mathrm{FSR}/\mathrm{FWHM}\) is about 780. Drawn by <code>figsrc/ch12_figs.py</code>.</figcaption>
</figure>

$$Q$$ is also $$2\pi$$ times the number of optical cycles the energy survives in the ring, and the photon lifetime is $$\tau = Q\lambda/(2\pi c)$$. The **loaded** Q combines two loss channels: the intrinsic loss of the ring and the coupling out,

$$\frac{1}{Q_L} = \frac{1}{Q_i} + \frac{1}{Q_c}, \qquad Q_i = \frac{2\pi n_g}{\lambda\alpha},$$

and at critical coupling $$Q_c = Q_i$$, so $$Q_L = Q_i/2$$. Near resonance the circulating power builds up above the input by $$\kappa^2/(1 - at)^2$$, which reaches several hundred in good silicon rings: a milliwatt in the bus becomes hundreds of milliwatts in the ring, enough for nonlinear effects ([Chapter 7]({% link chapters/07_loss.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 12.1 · Choosing the gap of a 10 <span class="nc">µm</span> ring</div>

For a 10 µm radius silicon ring with 2 dB/cm of loss ($$a = 0.99855$$, $$Q_i = 3.7\times10^5$$) and the coupler model of Chapter 9, [Table 12.1](#tab-12-1) shows three gaps. A 200 nm gap over-couples (κ² = 1.2 %, $$t = 0.9938 < a$$): a broad 22 pm resonance only 4 dB deep. At 250 nm (κ² = 0.52 %) the ring is still slightly over-coupled, with an 11 dB dip and $$Q_L = 1.3\times10^5$$. At 300 nm (κ² = 0.22 %, $$t = 0.99892 > a$$) it is slightly under-coupled: a 7.4 pm resonance, 17 dB deep, with $$Q_L = 2.1\times10^5$$. Critical coupling at 250 nm would need 3.6 dB/cm of loss. Because the loss is not known until the chip is measured, test chips sweep the gap ([Figure 12.5](#fig-12-5)).

</div>

**Table 12.1. A 10 µm silicon ring at 1550 nm, 2 dB/cm loss.** Coupling from the femwell-fitted coupler model of Chapter 9.
{: .tabcaption #tab-12-1 }

| Gap | κ² | Regime | FWHM | Loaded Q | Extinction |
|---|---|---|---|---|---|
| 200 nm | 1.23 % | over-coupled | 22.3 pm | 70 000 | 4.1 dB |
| 250 nm | 0.52 % | slightly over-coupled | 11.7 pm | 132 000 | 11.0 dB |
| 300 nm | 0.22 % | slightly under-coupled | 7.4 pm | 211 000 | 16.7 dB |

<figure id="fig-12-5">
  <img src="{{ '/assets/figs/ch12_gapdesign.svg' | relative_url }}" style="width:600px" alt="Left: coupling Q, intrinsic Q and loaded Q of the 10 micrometre ring against coupling gap from 150 to 400 nm on a log scale, with the coupling and intrinsic Q equal at 283 nm. Right: extinction against gap for losses of 1, 2 and 3.6 dB per centimetre, each peaking sharply at its critical gap of 323, 283 and 250 nm">
  <figcaption><span class="capnum">Figure 12.5.</span> <strong>Choosing the gap.</strong> (a) Coupling, intrinsic and loaded Q of the 10 µm ring against the gap, at 2 dB/cm; the dots are Table 12.1. \(Q_c = Q_i\), critical coupling, at 283 nm. (b) Extinction against the gap for three losses: the critical gap moves from 250 nm at 3.6 dB/cm to 323 nm at 1 dB/cm, so a gap chosen before the loss is known can land on either side of it. Coupling from the Chapter 9 coupler model. Drawn by <code>figsrc/ch12_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">12.5</span>Extracting parameters from measurements

Fitting a measured through-port resonance with the all-pass formula gives $$a$$ and $$t$$, and so the propagation loss and the coupling, in a device a fraction of a millimetre long {% include cite.html keys="shi2012" %}. There is a catch: $$T(\phi)$$ is symmetric in $$a$$ and $$t$$, so an under-coupled ring with $$(a, t)$$ and an over-coupled one with $$(t, a)$$ give identical spectra. The ambiguity is resolved by measuring more than one spectrum: a series of rings with different gaps (the coupling changes, the loss does not), an add-drop ring (whose drop port breaks the symmetry), or the phase response ([Figure 12.2b](#fig-12-2)). [Chapter 32]({% link chapters/32_analysis.md %}) fits real data this way.

## <span class="secnum">12.6</span>Non-idealities

- **Split resonances.** Sidewall roughness backscatters a little light into the counter-propagating mode of the ring. In high-Q rings the clockwise and counter-clockwise modes then couple and split each resonance into a doublet ([Figure 12.6](#fig-12-6)).
- **Thermal drift.** Silicon's thermo-optic coefficient moves a ring's resonances by about 70–80 pm per kelvin, several times a typical resonance width ([Chapter 18]({% link chapters/18_thermal.md %})).
- **Fabrication.** A 1 nm change of width or thickness moves the resonance by about 0.6 or 1.4 nm ([Chapter 6]({% link chapters/06_soi.md %})), so rings never land exactly where designed.
- **Dispersion and bending.** The FSR changes slowly with wavelength because $$n_g$$ does, and in small rings the bend changes $$n_\mathrm{eff}$$ and adds loss ([Chapter 8]({% link chapters/08_bends.md %})).

<figure id="fig-12-6">
  <img src="{{ '/assets/figs/ch12_split.svg' | relative_url }}" style="width:600px" alt="Left: through-port transmission of a high-Q ring against detuning with no backscatter, a single dip, and with backscatter splittings of one and three linewidths, where the dip becomes a doublet. Right: the power reflected back to the input, zero without backscatter and peaking at about 18 percent with it, with a sketch of the clockwise and counter-clockwise modes coupled by a scatterer">
  <figcaption><span class="capnum">Figure 12.6.</span> <strong>Split resonances.</strong> Coupled-mode model of the 300 nm-gap ring of Table 12.1 (FWHM 7.4 pm) with backscattering that couples its counter-clockwise and clockwise modes, for illustrative coupling strengths. (a) Once the splitting reaches the linewidth the dip turns into a doublet, each half shallower. (b) Light scattered into the clockwise mode leaves by the input port as a reflection, up to 18 % here. Drawn by <code>figsrc/ch12_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">12.7</span>Applications

Rings are the most versatile passive device in silicon photonics: WDM filters and multiplexers ([Chapter 14]({% link chapters/14_wdm.md %})), compact modulators that shift their resonance with carriers ([Chapter 20]({% link chapters/20_modulators.md %})), evanescent-field sensors that track a resonance as molecules bind ([Chapter 34]({% link chapters/34_apps.md %})), the wavelength-selective mirrors of tunable lasers, where two rings of slightly different radius form a Vernier filter ([Chapter 26]({% link chapters/26_tunable.md %})), and high-Q resonators for frequency combs and narrow-linewidth lasers.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Include all-pass rings of 10 µm radius with gaps of 200, 250 and 300 nm, and an add-drop ring. Their spectra give the propagation loss independently of the cutback, the coupling against gap, and the group index from the FSR.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [VM-Lab: ring resonator wavelength](https://s3.amazonaws.com/fip-6/Wavelength/index.html), [coupling gap](https://s3.amazonaws.com/fip-6/Coupling-Gap/index.html) and [all-pass ring](https://s3.amazonaws.com/fip-6/All-Pass-Ring/index.html) {% include cite.html keys="vmlab" %}
- [mustafa.sh: ring resonator designer](https://mustafa.sh/tools/ring-resonator-simulator) {% include cite.html keys="mustafash" %}

</div>

## Reading

{% include reflist.html keys="bogaerts2012,chrostowski2015,shi2012,yariv" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Resonances at $$m\lambda = n_\mathrm{eff}L$$, spaced by FSR = $$\lambda^2/(n_gL)$$: 9.15 nm for a 10 µm silicon ring.
- All-pass ring: $$T = (a^2 - 2at\cos\phi + t^2)/(1 - 2at\cos\phi + a^2t^2)$$; critical coupling at $$t = a$$ gives a full null.
- $$Q_i = 2\pi n_g/(\lambda\alpha)$$ depends only on loss; $$Q_L = Q_i/2$$ at critical coupling.
- For a 10 µm ring at 2 dB/cm, gaps from 200 to 300 nm move from over- to under-coupling; sweep the gap on a test chip.
- One through-port spectrum cannot tell under- from over-coupling; use several gaps or an add-drop ring.

</div>
