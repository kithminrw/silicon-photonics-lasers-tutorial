---
title: "Lab 16. Driving a ring modulator"
parent: Hands-On Labs
nav_order: 16
permalink: /labs/lab-16/
---

# <span class="chapnum">Lab 16 · Lasers and links</span>Driving a Ring Modulator: Operating Point, Bandwidth, Eyes and PAM4

Find the reference ring's operating point, see how detuning trades extinction for bandwidth, draw NRZ eyes from the coupled-mode equation, and pre-distort a PAM4 drive so that its three eyes are equal.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- place the laser on the ring's slope for a given insertion loss and compute the extinction (Worked Example 20.2);
- compute the small-signal bandwidth against detuning and find the peaking of a detuned ring (Section 20.8);
- integrate the coupled-mode equation for a PRBS7 pattern and measure NRZ eyes at 25 and 50 Gb/s;
- measure the unequal PAM4 eyes of a Lorentzian and find the drive levels that equalise them (Section 20.9).

</div>

## What you need

- [Chapter 12]({% link chapters/12_rings.md %}) and [Chapter 20]({% link chapters/20_modulators.md %}) (Sections 20.3, 20.8 and 20.9).
- Python 3.11 or newer with NumPy and Matplotlib.
- The script <a href="{{ '/labs/lab16_ringmod.py' | relative_url }}" download><code>lab16_ringmod.py</code></a>.
- About an hour.

Run `python lab16_ringmod.py`. The ring is the reference-link ring of Worked Example 20.2: radius 7.2 µm, $$n_g$$ = 3.89, $$Q_i$$ = 15 000, $$Q_L$$ = 8000, a junction that moves the resonance by 50 pm/V, and a 2 Vpp drive.

## <span class="secnum">L16.1</span>The operating point

The through port is a Lorentzian dip. The script finds the detuning at which the average of the two drive levels loses 3.0 dB, and the extinction between them:

```python
def T_of_V(V, det_mid):
    return T_static(det_mid - EFF * (V - VPP / 2))
```

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

$$Q_c$$ = 17 143, a 23.5 dB dip, a 193.8 pm (24.2 GHz) linewidth and a 6.58 ps photon lifetime. For 3.0 dB of insertion loss the laser sits 109 pm, 0.56 linewidths, blue of the resonance, and the extinction is 4.28 dB: the 4.3 dB at 3.0 dB of Worked Example 20.2.

</div>

## <span class="secnum">L16.2</span>Bandwidth against detuning

A small sinusoidal shift of the resonance modulates the output. On resonance the response falls off like a single pole at half the linewidth; detuned, the stored light beats with the input and the response peaks.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

At 0.05 linewidths the 3 dB bandwidth is 11.6 GHz (the 12 GHz of Worked Example 20.2), at 0.30 linewidths 19.7 GHz, at the 0.56-linewidth operating point 38.3 GHz with 2.6 dB of peaking at 14.8 GHz (Section 20.8: 38 GHz), and at one linewidth 85.9 GHz, but with only 0.98 dB of extinction.

</div>

## <span class="secnum">L16.3</span>NRZ eyes

`nrz_trace` steps the resonance with a PRBS7 pattern and integrates the coupled-mode equation with a fourth-order Runge–Kutta step 64 times per bit. `eye_opening` finds the sampling phase with the widest inner eye.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

With ideal 2 V steps at the operating point, the inner eye is 100 % of the static swing at 25 Gb/s and 95 % at 50 Gb/s. Closer to resonance, at 0.30 linewidths, it is 98 % and 90 % of a much larger swing (16.9 dB of extinction, but 5.5 dB of loss). A driver with a 12 ps rise time closes the 50 Gb/s eye at the operating point to 82 %. The rising edge, when the resonance steps away from the laser, takes about 7 ps: the stored light's phase starts turning at once (Figure 20.7).

</div>

## <span class="secnum">L16.4</span>PAM4 and pre-distortion

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

Equally spaced drive voltages give eyes in the ratio 1.34 : 0.99 : 0.67 from bottom to top, a penalty of 1.8 dB for the smallest on top of PAM4's 4.8 dB. Drive levels of 0, 0.48, 1.08 and 2.00 V make the three eyes equal (Figure 20.9).

</div>

<figure id="fig-l16-1">
  <img src="{{ '/assets/figs/lab16_expected.png' | relative_url }}" style="width:760px" alt="Three plots from the lab script: NRZ eye diagrams of the ring modulator at 25 and 50 gigabits per second, with transmission between about 0.27 and 0.73 and overshoot on the rising edges; and the transmission against drive voltage, a concave curve, with four equally spaced drive voltages giving unequal levels and four pre-distorted voltages giving equal ones">
  <figcaption><span class="capnum">Figure L16.1.</span> <strong>What the script draws.</strong> NRZ eyes at the operating point at 25 and 50 Gb/s, from the coupled-mode equation with ideal 2 V steps; the detuned ring overshoots on its rising edges. Right: the ring's transfer curve across the swing, with equally spaced (red) and pre-distorted (blue) PAM4 levels. Drawn by <code>lab16_ringmod.py</code>.</figcaption>
</figure>

## Exercises

1. **A more efficient junction.** Raise `EFF` to 70 pm/V and find the detuning for 3.0 dB of loss again. What extinction and bandwidth do you get?
2. **A lower Q.** Set $$Q_L$$ = 5000 (more coupling). What happens to the extinction at 3.0 dB loss and to the 50 Gb/s eye?
3. **Red side.** Put the laser 109 pm on the red side instead. Which edge is now fast, and why does the locking loop of Section 20.9 avoid this side?

<details markdown="1">
<summary>Answers</summary>

1. The laser moves a little further from the resonance, to 119 pm (0.62 linewidths), the extinction rises to 5.8 dB, and the 3 dB bandwidth to 43 GHz, because the bandwidth grows with the detuning in linewidths.
2. The linewidth widens to 310 pm and the laser sits 144 pm blue of the resonance; the same 100 pm swing is now a smaller fraction of the dip, so the extinction falls to 2.7 dB, while the bandwidth rises to 76 GHz and the 50 Gb/s eye opens fully.
3. The roles of the two edges swap, because the resonance now moves towards the laser when the bias rises. The average transmission then rises with detuning instead of falling, the opposite slope, so a loop designed for the blue side would push the ring away from its operating point.

</details>

## Going further

- [Lab 12]({% link labs/lab12_link.md %}) puts this modulator into the reference link's budget.
- The ring-modulator demo of [Section 20.3]({% link chapters/20_modulators.md %}) shows the same trade interactively.
