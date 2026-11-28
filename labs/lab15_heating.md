---
title: "Lab 15. Self-heating and roll-over"
parent: Hands-On Labs
nav_order: 15
permalink: /labs/lab-15/
---

# <span class="chapnum">Lab 15 · Lasers and links</span>Self-Heating and Thermal Roll-Over of a Laser on Silicon

Solve a laser's light, current and temperature together, reproduce Worked Example 27.1 and the roll-over of Figure 27.5, and find out what a hotter package and a thermal shunt do.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- solve the self-heating equations of Section 27.6 by fixed-point iteration;
- trace L–I curves for several thermal impedances and find where they roll over;
- see how the heat-sink temperature lowers the output and the maximum power;
- size the thermal impedance a laser needs to reach a target power at 85 °C.

</div>

## What you need

- [Chapter 24]({% link chapters/24_fp.md %}) (Section 24.5) and [Chapter 27]({% link chapters/27_lasersonsi.md %}) (Section 27.6).
- Python 3.11 or newer with NumPy and Matplotlib.
- The script <a href="{{ '/labs/lab15_heating.py' | relative_url }}" download><code>lab15_heating.py</code></a>.
- About an hour.

Run `python lab15_heating.py`. The laser is the model of Figure 27.5: a threshold of 20 mA without heating, $$V = 0.9\ \mathrm{V} + 6\ \Omega \times I$$, $$T_0$$ = 60 K, and a slope efficiency chosen so that at 100 mA and 80 K/W it emits the 20 mW of Worked Example 27.1.

## <span class="secnum">L15.1</span>One operating point

The threshold depends on the temperature, the temperature on the dissipated power $$IV - P$$, and the power on the threshold. `operate` goes round that loop until it stops changing, with half-steps so that it does not oscillate:

```python
        Ith = ITH0 * math.exp((dT + T_extra) / T0)
        P = max(0.0, ETA * (I - Ith))
        dT_new = Z * (I * (V0 + RS * I) - P)
        dT = 0.5 * dT + 0.5 * dT_new
```

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

Slope efficiency 0.2624 W/A. At 100 mA and 80 K/W: 20.00 mW out, 130 mW dissipated, 10.40 K hot, threshold 23.79 mA (19 % above 20 mA); the gain peak moves 5.0 nm and a single-mode laser 1.0 nm (Worked Example 27.1: 20 mW, 130 mW, 10.4 K, 19 %, about 5 and 1 nm).

</div>

## <span class="secnum">L15.2</span>Roll-over

As the current rises, so does the heat, faster than the light: the dissipated power grows as $$I^2R$$ while the threshold grows exponentially with the temperature. Eventually more current lowers the output.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

Without heating the output still rises at 700 mA (178 mW). At 40 K/W it peaks at 132.6 mW at 672 mA; at 80 K/W at 78.1 mW at 423 mA; at 160 K/W at 42.5 mW at 256 mA. At the peak the laser runs about 90 to 130 K above its heat sink. Figure 27.5b: 78 mW near 420 mA at 80 K/W, while the 40 K/W curve keeps rising over its range, to 600 mA.

</div>

## <span class="secnum">L15.3</span>A hotter heat sink

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

At 80 K/W: 20.0, 15.9 and 9.0 mW at 100 mA for heat sinks at 25, 55 and 85 °C; maximum output 78.1, 59.9 and 39.0 mW, at 423, 369 and 311 mA.

</div>

## <span class="secnum">L15.4</span>What a thermal shunt buys

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

At 85 °C, 80 K/W gives at most 39.0 mW and needs 153 mA for 20 mW, running 20.7 K hot. Halving the impedance to 40 K/W, as a thermal shunt through the BOX can (Figure 27.5a), doubles the maximum to 82.0 mW and reaches 20 mW at 140 mA, only 8.9 K hot.

</div>

<figure id="fig-l15-1">
  <img src="{{ '/assets/figs/lab15_expected.png' | relative_url }}" style="width:700px" alt="Two plots from the lab script: output against current for thermal impedances of 0, 40, 80 and 160 kelvin per watt, the higher ones rolling over at lower powers, with the worked-example point at 100 milliamps and 20 milliwatts; and output against current at 80 kelvin per watt for heat sinks at 25, 55 and 85 degrees Celsius">
  <figcaption><span class="capnum">Figure L15.1.</span> <strong>What the script draws.</strong> (a) L–I curves at a 25 °C heat sink for four thermal impedances; the dot is Worked Example 27.1. (b) At 80 K/W, a hotter heat sink lowers both the output at a given current and the roll-over point. Drawn by <code>lab15_heating.py</code>.</figcaption>
</figure>

## Exercises

1. **Hot package.** At 85 °C and 100 mA, what do 80, 40 and 20 K/W give in output and temperature rise?
2. **Lower series resistance.** Halve `RS` to 3 Ω. Where does the 80 K/W laser roll over now?
3. **A thermal budget.** What thermal impedance lets the laser give 20 mW at 85 °C while running no more than 10 K above its heat sink?

<details markdown="1">
<summary>Answers</summary>

1. 9.0 mW and 11.3 K at 80 K/W; 10.6 mW and 5.6 K at 40 K/W; 11.3 mW and 2.8 K at 20 K/W.
2. At 118.9 mW and 616 mA, against 78.1 mW at 423 mA: the $$I^2R$$ heating was most of the dissipated power at high current.
3. About 44 K/W, reaching 20 mW at 141 mA. A shunt that brings a bonded laser near that value is worth its area.

</details>

## Going further

- [Lab 10]({% link labs/lab10_rate_equations.md %}) has the full rate equations; add this thermal loop to its steady state, with the transparency density growing with temperature as Lab 10 already does.
- Worked Example 27.5 in [Section 27.9]({% link chapters/27_lasersonsi.md %}#279reliability-how-lasers-age-and-fail) turns the temperature rise into lost lifetime.
