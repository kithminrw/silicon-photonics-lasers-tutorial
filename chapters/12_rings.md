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

A ring of radius $$R$$ and circumference $$L = 2\pi R$$ is resonant when light returns in phase after one round trip, $$\beta L = 2\pi m$$, that is when

$$m\lambda_m = n_\mathrm{eff}L, \qquad m = 1, 2, 3, \dots$$

Adjacent resonances are separated by the **free spectral range**, which, as for the MZI ([Chapter 11]({% link chapters/11_mzi.md %})), involves the group index:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Free spectral range of a ring</div>

$$\mathrm{FSR} = \frac{\lambda^2}{n_gL}$$

</div>

A 10 µm radius silicon ring ($$L = 62.8$$ µm, $$n_g = 4.18$$) has FSR = $$1.55^2/(4.18 \times 62.8) = 9.15$$ nm. For the four channels of the reference link, spread over 9.6 nm, the FSR must exceed that span, which calls for rings of about 9 µm radius or less.

## <span class="secnum">12.2</span>The all-pass ring

Couple the ring to a single bus waveguide through a short directional coupler with field self-coupling $$t$$ and cross-coupling $$\kappa$$ ($$t^2 + \kappa^2 = 1$$, [Chapter 9]({% link chapters/09_couplers.md %})), and let $$a$$ be the field transmission of one round trip ($$a^2 = e^{-\alpha L}$$) and $$\phi = \beta L$$ its phase. Summing the light that circulates any number of times gives the through-port transmission {% include cite.html keys="bogaerts2012" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">All-pass ring</div>

$$T(\phi) = \frac{a^2 - 2at\cos\phi + t^2}{1 - 2at\cos\phi + (at)^2}$$

</div>

Off resonance $$T \approx 1$$; on resonance ($$\phi = 2\pi m$$) it dips to $$T_\mathrm{min} = (a - t)^2/(1 - at)^2$$. The dip reaches zero when $$t = a$$, **critical coupling**: the light coupled back out of the ring then exactly cancels the light that passed by, because the coupler's loss of transmission equals the ring's loss per round trip. For $$t > a$$ the ring is **under-coupled** (it loses more than it couples, giving a narrow, shallow dip); for $$t < a$$ it is **over-coupled** (a broad, shallow dip).

**Try it.** Change the radius, gap and loss, and tune the laser across a resonance to watch the light build up in the ring.

{% include demos/ring.html %}

## <span class="secnum">12.3</span>The add-drop ring

A second bus on the other side of the ring, with couplings $$t_2$$ and $$\kappa_2$$, drops the resonant light into a separate port:

$$T_\mathrm{through} = \frac{t_2^2a^2 - 2t_1t_2a\cos\phi + t_1^2}{1 - 2t_1t_2a\cos\phi + (t_1t_2a)^2}, \qquad T_\mathrm{drop} = \frac{(1 - t_1^2)(1 - t_2^2)\,a}{1 - 2t_1t_2a\cos\phi + (t_1t_2a)^2}.$$

With equal couplers and no loss, the drop port takes all the power on resonance and nothing off resonance: a bandpass filter. Rings in series on a bus, each with its own resonance, make a multiplexer or demultiplexer, exactly the receiver of the reference link ([Chapter 14]({% link chapters/14_wdm.md %})).

## <span class="secnum">12.4</span>Quality factor and finesse

The width of a resonance is described by its full width at half maximum, its **quality factor** $$Q = \lambda/\Delta\lambda_\mathrm{FWHM}$$, and its **finesse** $$F = \mathrm{FSR}/\Delta\lambda_\mathrm{FWHM}$$. For the all-pass ring

$$\Delta\lambda_\mathrm{FWHM} = \frac{(1 - at)\,\lambda^2}{\pi n_gL\sqrt{at}}.$$

$$Q$$ is also $$2\pi$$ times the number of optical cycles the energy survives in the ring, and the photon lifetime is $$\tau = Q\lambda/(2\pi c)$$. The **loaded** Q combines two loss channels: the intrinsic loss of the ring and the coupling out,

$$\frac{1}{Q_L} = \frac{1}{Q_i} + \frac{1}{Q_c}, \qquad Q_i = \frac{2\pi n_g}{\lambda\alpha},$$

and at critical coupling $$Q_c = Q_i$$, so $$Q_L = Q_i/2$$. Near resonance the circulating power builds up above the input by $$\kappa^2/(1 - at)^2$$, which reaches several hundred in good silicon rings: a milliwatt in the bus becomes hundreds of milliwatts in the ring, enough for nonlinear effects ([Chapter 7]({% link chapters/07_loss.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 12.1 · Choosing the gap of a 10 <span class="nc">µm</span> ring</div>

For a 10 µm radius silicon ring with 2 dB/cm of loss ($$a = 0.99855$$, $$Q_i = 3.7\times10^5$$) and the coupler model of Chapter 9, [Table 12.1](#tab-12-1) shows three gaps. A 200 nm gap over-couples (κ² = 1.2 %, $$t = 0.9938 < a$$): a broad 22 pm resonance only 4 dB deep. At 250 nm (κ² = 0.52 %) the ring is still slightly over-coupled, with an 11 dB dip and $$Q_L = 1.3\times10^5$$. At 300 nm (κ² = 0.22 %, $$t = 0.99892 > a$$) it is slightly under-coupled: a 7.4 pm resonance, 17 dB deep, with $$Q_L = 2.1\times10^5$$. Critical coupling at 250 nm would need 3.6 dB/cm of loss. Because the loss is not known until the chip is measured, test chips sweep the gap.

</div>

**Table 12.1. A 10 µm silicon ring at 1550 nm, 2 dB/cm loss.** Coupling from the femwell-fitted coupler model of Chapter 9.
{: .tabcaption #tab-12-1 }

| Gap | κ² | Regime | FWHM | Loaded Q | Extinction |
|---|---|---|---|---|---|
| 200 nm | 1.23 % | over-coupled | 22.3 pm | 70 000 | 4.1 dB |
| 250 nm | 0.52 % | slightly over-coupled | 11.7 pm | 132 000 | 11.0 dB |
| 300 nm | 0.22 % | slightly under-coupled | 7.4 pm | 211 000 | 16.7 dB |

## <span class="secnum">12.5</span>Extracting parameters from measurements

Fitting a measured through-port resonance with the all-pass formula gives $$a$$ and $$t$$, and so the propagation loss and the coupling, in a device a fraction of a millimetre long {% include cite.html keys="shi2012" %}. There is a catch: $$T(\phi)$$ is symmetric in $$a$$ and $$t$$, so an under-coupled ring with $$(a, t)$$ and an over-coupled one with $$(t, a)$$ give identical spectra. The ambiguity is resolved by measuring more than one spectrum: a series of rings with different gaps (the coupling changes, the loss does not), an add-drop ring (whose drop port breaks the symmetry), or the phase response. [Chapter 32]({% link chapters/32_analysis.md %}) fits real data this way.

## <span class="secnum">12.6</span>Non-idealities

- **Split resonances.** Sidewall roughness backscatters a little light into the counter-propagating mode of the ring. In high-Q rings the clockwise and counter-clockwise modes then couple and split each resonance into a doublet.
- **Thermal drift.** Silicon's thermo-optic coefficient moves a ring's resonances by about 70–80 pm per kelvin, several times a typical resonance width ([Chapter 18]({% link chapters/18_thermal.md %})).
- **Fabrication.** A 1 nm change of width or thickness moves the resonance by about 0.6 or 1.4 nm ([Chapter 6]({% link chapters/06_soi.md %})), so rings never land exactly where designed.
- **Dispersion and bending.** The FSR changes slowly with wavelength because $$n_g$$ does, and in small rings the bend changes $$n_\mathrm{eff}$$ and adds loss ([Chapter 8]({% link chapters/08_bends.md %})).

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
