---
title: "11. Mach–Zehnder Interferometers"
parent: "Part III · Passive Devices"
nav_order: 11
permalink: /part-3/ch11/
chapter: 11
---

# <span class="chapnum">Chapter 11</span>Mach–Zehnder Interferometers

Split, delay, recombine: the Mach–Zehnder interferometer turns a phase difference into a change of intensity, and it is everywhere in photonics.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the transfer function of balanced and unbalanced MZIs from coupler and waveguide matrices;
- relate the free spectral range to the group index and the arm-length difference;
- find the extinction ratio for non-ideal splitters and unequal losses;
- describe tunable MZI switches and lattice filters;
- use an MZI as a test structure to measure the group index.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How does the arm-length difference set the spectrum, and what limits the extinction?

</div>

## <span class="secnum">11.1</span>Interference and optical phase

A wave that travels a length $$L$$ of waveguide picks up a phase $$\phi = \beta L = 2\pi n_\mathrm{eff}L/\lambda$$. Two waves that meet add as fields, so the result depends on their phase difference: in phase they interfere constructively, a half-wave apart destructively. An interferometer splits light into two paths, lets their phases differ, and recombines them, turning a phase difference into a change of power. Because $$\lambda$$ is about 1.5 µm and $$n_\mathrm{eff}$$ about 2.4, a length difference of only 0.32 µm in a silicon waveguide is already half a wavelength.

## <span class="secnum">11.2</span>The MZI transfer function

The Mach–Zehnder interferometer (MZI) is two couplers joined by two arms. Each element is a matrix acting on the pair of field amplitudes in the two waveguides ([Chapter 9]({% link chapters/09_couplers.md %})): a lossless coupler with power coupling $$\kappa^2$$ and through coupling $$t^2 = 1 - \kappa^2$$ is

$$C = \begin{pmatrix} t & -j\kappa \\ -j\kappa & t\end{pmatrix},$$

and the arms multiply each field by $$a_i e^{-j\phi_i}$$, with $$a_i$$ the field transmission (loss) and $$\phi_i$$ the phase. The output is $$C_2\,\mathrm{diag}(a_1e^{-j\phi_1}, a_2e^{-j\phi_2})\,C_1$$ applied to the input. With ideal 50/50 couplers and equal losses $$a$$, light entering one port leaves the two outputs as

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">MZI with ideal 50/50 couplers</div>

$$P_\mathrm{bar} = a^2\sin^2\frac{\Delta\phi}{2}, \qquad P_\mathrm{cross} = a^2\cos^2\frac{\Delta\phi}{2}, \qquad \Delta\phi = \phi_2 - \phi_1$$

</div>

The two outputs are complementary: power that leaves one appears at the other. (Which output is called "bar" and which "cross" depends on the coupler phases; with the −j convention above, a balanced MZI sends everything to the cross port.)

When the couplers are not 50/50, the two arms carry unequal fields and can no longer cancel completely, so the nulls fill in. For couplers with power ratios $$\kappa_1^2$$ and $$\kappa_2^2$$ the **extinction ratio** of the cross port is

$$\mathrm{ER}_\mathrm{cross} = \left(\frac{t_1\kappa_2 + \kappa_1 t_2}{t_1\kappa_2 - \kappa_1 t_2}\right)^2,$$

which is infinite only when the couplers are equal, $$\kappa_1^2 = \kappa_2^2$$; the bar port's nulls are perfect instead when $$\kappa_1^2 + \kappa_2^2 = 1$$. Unequal arm losses unbalance the fields in the same way, which is why a long unbalanced arm slowly fills the nulls.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 11.1 · How good must the splitters be?</div>

With a perfect first coupler (50/50) and a second at 55/45, the cross port has $$t_1\kappa_2 = \sqrt{0.5}\sqrt{0.55} = 0.524$$ and $$\kappa_1t_2 = \sqrt{0.5}\sqrt{0.45} = 0.474$$, so ER = $$(0.998/0.050)^2 = 398$$, or 26 dB. At 60/40, ER drops to 20 dB. A switch that must block a channel by 30 dB needs couplers matched to within a few per cent, or a calibration, which is what tunable couplers and the "double MZI" are for.

</div>

## <span class="secnum">11.3</span>Unbalanced MZIs

If the two arms differ in length by $$\Delta L$$, the phase difference depends on wavelength, $$\Delta\phi = 2\pi n_\mathrm{eff}\Delta L/\lambda$$, and the outputs oscillate across the spectrum. The spacing between adjacent maxima, the **free spectral range**, follows from the change of $$\Delta\phi$$ by $$2\pi$$, and because $$n_\mathrm{eff}$$ itself depends on wavelength it involves the group index ([Chapter 2]({% link chapters/02_em.md %})):

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Free spectral range of an unbalanced MZI</div>

$$\mathrm{FSR} = \frac{\lambda^2}{n_g\,\Delta L}$$

</div>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 11.2 · A 100 <span class="nc">µm</span> imbalance</div>

In 500 × 220 nm silicon strips at 1550 nm ($$n_g = 4.18$$, [Chapter 6]({% link chapters/06_soi.md %})), $$\Delta L = 100$$ µm gives FSR = $$1.55^2/(4.18 \times 100) = 5.75$$ nm. To separate channels 3.2 nm apart (the 400 GHz grid of the reference link) as an interleaver, you need FSR = 6.4 nm, so $$\Delta L = 2.4025/(4.18 \times 0.0064) = 90$$ µm.

</div>

**Try it.** Set the arm-length difference, the splitter ratios, the loss and the phase; the top view shows the delay loop and where the light goes.

{% include demos/mzi.html %}

## <span class="secnum">11.4</span>Tuning and switching

A phase shifter on one arm slides the fringes without changing their spacing. With a balanced MZI ($$\Delta L = 0$$), a phase shift of π switches the light from one output to the other: the **MZI switch**, the building block of switch fabrics and of the interferometer meshes used for photonic computing ([Chapter 34]({% link chapters/34_apps.md %})). The phase shifter can be a heater (slow, efficient, [Chapter 18]({% link chapters/18_thermal.md %})) or an electro-optic section (fast, [Chapters 19–20]({% link chapters/19_eo.md %})); driven with data, the same MZI is a modulator.

## <span class="secnum">11.5</span>Cascaded and lattice filters

One unbalanced MZI has a sinusoidal response, which is a poor filter: its passband is rounded and its rejection grows slowly away from the nulls. Cascading MZIs, with couplers of chosen ratios and delays that are multiples of a unit $$\Delta L$$, synthesises higher-order responses, exactly as digital filters are built from delays and weights: flat-top passbands, sharp edges and interleavers that split a WDM comb into odd and even channels ([Chapter 14]({% link chapters/14_wdm.md %})). Each extra stage adds a coupler and a phase that must be accurate, so lattice filters are usually tuned with heaters after fabrication.

## <span class="secnum">11.6</span>MZIs as test structures

Because the FSR depends only on $$n_g$$ and the drawn $$\Delta L$$, an unbalanced MZI is the standard way to measure the group index on a chip: find the spacing of the fringes, and

$$n_g = \frac{\lambda^2}{\mathrm{FSR}\,\Delta L}.$$

A set of MZIs with different $$\Delta L$$ gives several estimates and an error bar; the depth of the fringes measures how well the couplers are balanced. This is one of the first things you put on a test chip and one of the first analyses of [Chapter 32]({% link chapters/32_analysis.md %}).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Include two or three unbalanced MZIs between grating couplers, with $$\Delta L$$ between about 50 and 300 µm (FSR from about 11 to 2 nm at 1550 nm), built from the PDK's Y-branches or broadband couplers. They give the group index and a check on the splitters.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter {% include cite.html keys="vmlab" %}:

- [VM-Lab: MZI arm length](https://s3.amazonaws.com/fip-5a/Length/index.html), [wavelength](https://s3.amazonaws.com/fip-5a/Wavelength/index.html) and [temperature](https://s3.amazonaws.com/fip-5b/Temperature/index.html)

</div>

## Reading

{% include reflist.html keys="chrostowski2015,okamoto,yariv" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- An MZI is coupler × arms × coupler; with 50/50 couplers the outputs go as $$\sin^2(\Delta\phi/2)$$ and $$\cos^2(\Delta\phi/2)$$.
- The free spectral range is $$\lambda^2/(n_g\Delta L)$$, with the group index: 5.75 nm for 100 µm in a silicon strip at 1550 nm.
- Unequal couplers or arm losses limit the extinction: a 55/45 coupler caps it near 26 dB.
- A phase shifter turns a balanced MZI into a switch or modulator; cascades make flat-top filters and interleavers.
- Unbalanced MZIs measure the group index on a chip: $$n_g = \lambda^2/(\mathrm{FSR}\,\Delta L)$$.

</div>
