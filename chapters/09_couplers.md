---
title: "9. Coupled-Mode Theory and Directional Couplers"
parent: "Part III · Passive Devices"
nav_order: 9
permalink: /part-3/ch09/
chapter: 9
---

# <span class="chapnum">Chapter 9</span>Coupled-Mode Theory and Directional Couplers

Bring two waveguides close together and light moves back and forth between them; controlling that exchange is the basis of most passive devices.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- derive the coupled-mode equations for two waveguides, with and without phase mismatch;
- explain coupling with even and odd supermodes and the cross-over length;
- find the coupler length for any power split, and its dependence on gap, wavelength and polarisation;
- describe asymmetric, adiabatic and broadband couplers;
- write the 2 × 2 scattering matrix and explain its −j.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which length and gap give a 50/50 split, and how robust is it?

</div>

## <span class="secnum">9.1</span>Coupled-mode equations

Two parallel waveguides a few hundred nanometres apart feel each other through their evanescent tails ([Chapter 5]({% link chapters/05_slab.md %})). Write the total field as the two isolated modes with slowly varying amplitudes $$a_1(z)$$ and $$a_2(z)$$; the overlap of one guide's field with the other's index perturbation couples them {% include cite.html keys="yariv1973" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Coupled-mode equations</div>

$$\frac{\mathrm{d}a_1}{\mathrm{d}z} = -j\beta_1a_1 - j\kappa a_2, \qquad \frac{\mathrm{d}a_2}{\mathrm{d}z} = -j\beta_2a_2 - j\kappa a_1$$

</div>

Here $$\kappa$$ (per unit length) is the coupling coefficient. With all the light in guide 1 at $$z = 0$$, the power in guide 2 is

$$P_2(z) = \frac{\kappa^2}{\kappa^2 + \delta^2}\sin^2\!\left(\sqrt{\kappa^2 + \delta^2}\,z\right), \qquad \delta = \frac{\beta_1 - \beta_2}{2}.$$

For identical guides ($$\delta = 0$$) the power transfers completely and back again, with period $$\pi/\kappa$$. For mismatched guides it transfers only partly, a fraction $$\kappa^2/(\kappa^2 + \delta^2)$$, but faster. Phase matching is the condition for complete transfer: two waveguides of different widths barely couple, and a narrow and a wide guide can be designed to couple selectively between chosen modes ([Chapter 8]({% link chapters/08_bends.md %})).

## <span class="secnum">9.2</span>Supermodes

There is a second, exact way to see the same physics. Two coupled identical waveguides form one structure whose own modes, the **supermodes**, are the even (symmetric) and odd (antisymmetric) combinations of the single-guide modes, with effective indices $$n_\mathrm{even} > n_\mathrm{odd}$$. Light launched into one guide is half even and half odd; the two supermodes travel at different speeds, and after the length over which they slip by π relative to each other, they add up in the other guide. This **cross-over length** is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Cross-over length</div>

$$L_x = \frac{\lambda}{2\,(n_\mathrm{even} - n_\mathrm{odd})} = \frac{\pi}{2\kappa}$$

</div>

and a mode solver gives it directly: solve the pair of waveguides, read off the two indices, and subtract. This is the method used for the numbers below.

## <span class="secnum">9.3</span>The directional coupler

A directional coupler brings two waveguides together through S-bends, runs them in parallel for a length $$L$$, and separates them again. The power crossing over is

$$\frac{P_\mathrm{cross}}{P_\mathrm{in}} = \sin^2\!\left(\frac{\pi(L + L_b)}{2L_x}\right),$$

where $$L_b$$ is the extra effective length contributed by the bends, which still couple while the guides are close. A 3 dB coupler needs $$L + L_b = L_x/2$$.

[Figure 9.1](#fig-9-1) shows $$L_x$$ for two 500 × 220 nm silicon strips at 1550 nm (TE), computed with femwell. It grows exponentially with the gap, by about 2.4 times per 100 nm, because the coupling comes from tails that decay over about 100 nm.

<figure id="fig-9-1">
  <img src="{{ '/assets/figs/ch09_supermodes.svg' | relative_url }}" style="width:720px" alt="Cross-over length against gap from femwell, and the cross-coupled power of two 3 dB couplers against wavelength">
  <figcaption><span class="capnum">Figure 9.1.</span> <strong>Directional couplers of 500 × 220 nm silicon strips (TE).</strong> (a) Cross-over length against gap at 1550 nm: femwell supermode solutions (points) and an exponential fit. (b) Cross-coupled power of 3 dB couplers designed at 1550 nm, assuming the bends add 2.5 µm of effective length: the split drifts by about 0.35 % per nanometre. Drawn by <code>figsrc/part3_figs.py</code> from <code>figsrc/ch09_supermodes.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 9.1 · A 3 dB coupler in silicon</div>

At a 200 nm gap femwell gives $$n_\mathrm{even} = 2.4573$$ and $$n_\mathrm{odd} = 2.4368$$, so $$L_x = 1.55/(2 \times 0.0205) = 37.8$$ µm. With the bends adding about 2.5 µm, a 50/50 coupler needs a straight section of $$37.8/2 - 2.5 = 16.4$$ µm. At a 300 nm gap, $$L_x = 91$$ µm and the straight section grows to 43 µm. A 100 nm gap would need only about 5 µm, but small gaps are hard to fabricate reproducibly, and a 10 nm error in a 100 nm gap changes $$L_x$$ by about 10 %.

</div>

**Try it.** Set the gap, length and wavelength; the top view shows the light moving between the guides, and the cross-section the gap to scale.

{% include demos/dc.html %}

## <span class="secnum">9.4</span>Wavelength, polarisation and fabrication sensitivity

A longer wavelength pushes more of each mode into the gap, so coupling grows quickly with wavelength: femwell gives $$L_x = 47$$ µm at 1500 nm and 31 µm at 1600 nm for the 200 nm gap. A coupler designed for 50/50 at 1550 nm therefore splits 43.5/56.5 at 1530 nm and 57/43 at 1570 nm ([Figure 9.1b](#fig-9-1)), a drift of about 0.35 % per nanometre. TM modes, with longer tails, couple more strongly and have much shorter cross-over lengths. And because $$L_x$$ is exponential in the gap and sensitive to width and thickness, fabrication variations move the split from die to die.

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">What this means for your design</div>

A directional coupler is the right choice when you need a specific, possibly small, coupling ratio at one wavelength: ring resonators (whose couplers are short directional couplers, [Chapter 12]({% link chapters/12_rings.md %})), taps and monitors. It is the wrong choice for a broadband 3 dB split: across the 9.6 nm of the reference link's channels the split above moves by about ±1.7 %, and across the C band by ±6 %.

</div>

## <span class="secnum">9.5</span>Broadband and adiabatic couplers

Three tricks flatten a coupler's response:

- **Asymmetric phase control.** Using waveguides of slightly different widths in part of the coupler adds a wavelength-dependent phase that compensates the wavelength dependence of $$\kappa$$. The broadband directional coupler of the SiEPIC EBeam PDK works this way {% include cite.html keys="lu2015bdc" %}; see it in the [3D gallery]({% link devices-3d.md %}#dev-siepic-bdc).
- **Adiabatic couplers.** If one waveguide is tapered so that the input mode evolves slowly into the even or odd supermode of the symmetric section, the split ratio is set by symmetry, not by an interference length, and is nearly wavelength-independent, at the price of a device hundreds of micrometres long {% include cite.html keys="yun2013adiabatic" %}.
- **Bent couplers.** Curving the coupling region changes how the phase mismatch varies with wavelength and can cancel the dependence of $$\kappa$$ over a band.

MMIs ([Chapter 10]({% link chapters/10_mmi.md %})) are the other broadband option.

## <span class="secnum">9.6</span>The 2 × 2 scattering matrix

Whatever happens inside, a lossless, reciprocal 2 × 2 coupler connects its input and output fields by a unitary, symmetric matrix. With power coupling $$\kappa^2$$ (now meaning the coupled power fraction, not the coefficient per length) and $$t^2 = 1 - \kappa^2$$:

$$\begin{pmatrix}b_1\\ b_2\end{pmatrix} = \begin{pmatrix} t & -j\kappa \\ -j\kappa & t\end{pmatrix}\begin{pmatrix}a_1\\ a_2\end{pmatrix}.$$

The −j is not a convention to memorise but a consequence of energy conservation: unitarity requires the cross-coupled fields to be 90° out of phase with the through fields, so that $$\lvert b_1\rvert^2 + \lvert b_2\rvert^2 = \lvert a_1\rvert^2 + \lvert a_2\rvert^2$$ for every input. That quadrature phase is what makes the Mach–Zehnder interferometer and the ring resonator of the next chapters work, and it is the same matrix used in their demos.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

Free simulations by others that pair well with this chapter {% include cite.html keys="vmlab" %}:

- [VM-Lab: directional coupler gap](https://s3.amazonaws.com/fip-3/Gap-Spacing/index.html) and [full explorer](https://s3.amazonaws.com/fip-3/Full-Explorer/index.html)
- [VM-Lab: asymmetric directional coupler / mode converter](https://s3.amazonaws.com/fip-13/Mode-Converter/index.html)

</div>

## Reading

{% include reflist.html keys="yariv1973,chrostowski2015,okamoto,lu2015bdc,yun2013adiabatic" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Coupled modes exchange power with period $$\pi/\kappa$$; complete transfer needs phase matching.
- Equivalently, the even and odd supermodes beat: $$L_x = \lambda/(2\Delta n)$$.
- For 500 × 220 nm silicon strips at 1550 nm: $$L_x = 37.8$$ µm at 200 nm gap, growing 2.4× per 100 nm; a 3 dB coupler is about 16 µm long plus bends.
- A directional coupler's split drifts by about 0.35 %/nm; use asymmetric, adiabatic or MMI couplers for broadband splitting.
- A lossless coupler's matrix is unitary, and its −j cross-coupling phase is required by energy conservation.

</div>
