---
title: "Lab 17. SOA gain, saturation and noise"
parent: Hands-On Labs
nav_order: 17
permalink: /labs/lab-17/
---

# <span class="chapnum">Lab 17 · Lasers and links</span>A Semiconductor Optical Amplifier: Gain, Saturation, Noise and Patterning

Integrate an SOA's saturating gain along its length, compute its noise figure and ASE, watch a saturated amplifier distort a bit pattern, and see what a large-mode design buys.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- integrate $$\mathrm{d}P/\mathrm{d}z = [\Gamma g_0/(1 + P/P_\mathrm{sat}) - \alpha_i]P$$ and find the −3 dB output power (Section 28.2);
- compute the noise figure, the ASE and the OSNR of the amplifier (Section 28.3);
- model patterning with the carrier-reservoir equation for the integrated gain (Section 28.4);
- compare the laser-stack SOA with the slab-coupled, large-mode SOA of Figure 24.13.

</div>

## What you need

- [Chapter 28]({% link chapters/28_soa.md %}) and [Section 24.9]({% link chapters/24_fp.md %}).
- Python 3.11 or newer with NumPy and Matplotlib.
- The script <a href="{{ '/labs/lab17_soa.py' | relative_url }}" download><code>lab17_soa.py</code></a>.
- About an hour.

Run `python lab17_soa.py`. The amplifier is that of Worked Example 28.1: $$\Gamma g_0$$ = 35 cm⁻¹, $$\alpha_i$$ = 5 cm⁻¹, $$P_\mathrm{sat}$$ = 12 mW, $$n_{sp}$$ = 2 and a 200 ps gain recovery.

## <span class="secnum">L17.1</span>Gain and saturation

`amp` integrates the saturating equation along the amplifier with fourth-order Runge–Kutta steps; `p3db` bisects for the input at which the gain has fallen 3 dB.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

0.5, 1 and 2 mm give 6.5, 13.0 and 26.1 dB of small-signal gain, and −3 dB output powers of 10.5, 8.7 and 8.3 dBm, reached with 7.0, −1.3 and −14.7 dBm in (Worked Example 28.1 and Figure 28.2). The output saturates at about the same power whatever the length, because the end of the amplifier, where the power is highest, sets it.

</div>

## <span class="secnum">L17.2</span>Noise figure and ASE

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

The 1 mm amplifier has a noise figure of 6.47 dB with $$n_{sp}$$ = 2, tending to 6.69 dB at high gain; an ideal amplifier of the same gain would have 2.79 dB. Its ASE is −41.5 dBm per 0.1 nm, so a −15 dBm signal leaves at −2.0 dBm with an OSNR of 39.5 dB in 0.1 nm. A 3 dB input coupler raises the noise figure to 9.47 dB (Figure 28.3).

</div>

## <span class="secnum">L17.3</span>Patterning

The carrier-reservoir model follows the integrated gain $$h = \ln G$$: $$\mathrm{d}h/\mathrm{d}t = (h_0 - h)/\tau - P_\mathrm{in}(e^h - 1)/E_\mathrm{sat}$$, with $$E_\mathrm{sat} = P_\mathrm{sat}\tau$$.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

With 1 mW "ones" and 0.05 mW "zeros" at 10 Gb/s the gain swings between 9.9 and 12.6 dB (Figure 28.4), and the mean output is 6.0 mW. A faster recovery, 100 ps, follows the pattern more closely (9.9–12.7 dB); a slow one, 1 ns, responds mostly to the average power and swings less (10.1–11.5 dB), the reason erbium amplifiers, with millisecond lifetimes, do not pattern at all.

</div>

## <span class="secnum">L17.4</span>A large-mode amplifier

The slab-coupled design of Figure 24.13 has a tenth of the confinement and ten times the mode area. Part D scales the modal gain by 0.69/7.32 and the saturation power by 10.3, and takes an internal loss of 0.5 cm⁻¹ (illustrative: little of its mode is in doped layers).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

With a modal gain of 3.30 cm⁻¹ the amplifier needs 10.7 mm for the same 13.0 dB, but its −3 dB output rises from 8.7 to 18.8 dBm, and its noise figure stays near 6.5 dB.

</div>

<figure id="fig-l17-1">
  <img src="{{ '/assets/figs/lab17_expected.png' | relative_url }}" style="width:760px" alt="Three plots from the lab script: gain against output power for 0.5, 1 and 2 millimetre amplifiers, each flat then falling, with dots at the 3 dB points; noise figure against small-signal gain, rising towards about 6.7 decibels for the real amplifier and 3 decibels for an ideal one; and the gain against time for a 10 gigabit per second pattern, swinging between about 9.9 and 12.6 decibels">
  <figcaption><span class="capnum">Figure L17.1.</span> <strong>What the script draws.</strong> (A) Gain against output power for three lengths, with the −3 dB points. (B) Noise figure against small-signal gain, for the amplifier and for an ideal one. (C) The gain following a 10 Gb/s pattern in the saturated 1 mm amplifier. Drawn by <code>lab17_soa.py</code>.</figcaption>
</figure>

## Exercises

1. **More drive.** Raise $$\Gamma g_0$$ to 45 cm⁻¹ in the 1 mm amplifier. What are the new small-signal gain and −3 dB output power?
2. **Booster or pre-amplifier?** For a −25 dBm input, which of the three lengths gives the best output OSNR, and which the most output power without entering saturation?
3. **Patterning budget.** Keeping the "zero" at 5 % of the "one", at what "one" level does the 1 mm amplifier's gain swing exceed 1 dB at 10 Gb/s?

<details markdown="1">
<summary>Answers</summary>

1. 17.4 dB of small-signal gain, but the −3 dB output stays at 8.7 dBm, now reached with −5.7 dBm in: more drive buys gain, not output power, while $$P_\mathrm{sat}$$ is unchanged.
2. The output OSNR is the input power minus the noise figure, up to a constant, so the 0.5 mm amplifier, with 5.6 dB against 6.5 and 6.7 dB, gives the best OSNR, by about 1 dB. The 2 mm amplifier gives the most power: 1.1 dBm out, still far below its 8.3 dBm −3 dB point.
3. About 0.2 mW: the swing is 0.96 dB at 0.2 mW and 1.31 dB at 0.3 mW. Below that the average output is a small fraction of $$P_\mathrm{sat}$$ and the gain hardly moves.

</details>

## Going further

- [Lab 10]({% link labs/lab10_rate_equations.md %}) solves the laser's rate equations; an SOA is the same medium without the mirrors.
- The SOA demo of [Section 28.2]({% link chapters/28_soa.md %}) shows the gain saturating along the amplifier.
