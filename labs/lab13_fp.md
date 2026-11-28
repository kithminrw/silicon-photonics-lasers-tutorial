---
title: "Lab 13. Fabry–Pérot cavities"
parent: Hands-On Labs
nav_order: 13
permalink: /labs/lab-13/
---

# <span class="chapnum">Lab 13 · Simulate and measure</span>Fabry–Pérot Cavities: Airy Spectra, Bragg Mirrors and Fringe Analysis

Add up the round trips of a Fabry–Pérot cavity, check the result against the transfer matrices of a real Bragg-mirror cavity, and then turn the method round: read a waveguide's loss and a laser's gain from the fringes in measured spectra.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- compute the Airy transmission and reflection of a cavity, its finesse (exactly and approximately) and the effect of unequal mirrors and loss;
- model the Bragg-mirror cavity of Worked Example 13.3 with coupled-mode transfer matrices, and test the penetration-depth picture against it;
- extract the propagation loss of a cleaved waveguide from its fringe contrast (the Fabry–Pérot method), and see what limits it;
- extract a laser's net modal gain below threshold from its emission fringes (the Hakki–Paoli method), and see how the spectrometer's resolution biases it.

</div>

## What you need

- [Chapter 13]({% link chapters/13_bragg.md %}) (Sections 13.2, 13.3 and 13.5) and [Chapter 24]({% link chapters/24_fp.md %}) (Sections 24.1 and 24.2).
- Python 3.11 or newer with NumPy and Matplotlib: `pip install numpy matplotlib`.
- The script <a href="{{ '/labs/lab13_fp.py' | relative_url }}" download><code>lab13_fp.py</code></a>.
- About two hours, including the exercises.

Run it from a terminal in the folder where you saved it:

```
python lab13_fp.py
```

It prints a checkpoint for each part below, with the chapter's value beside it, and saves the figure `lab13_fp.png` in a few seconds. Inside, lengths and wavelengths are in micrometres; the printout converts to nm, pm and dB/cm. The "measurements" of Parts C and D are simulated, with a fixed random seed, so your numbers match the ones below.

## <span class="secnum">L13.1</span>The Airy function

Light that enters through mirror 1 makes round trips; each returns $$\rho = \sqrt{R_1R_2}\,A$$ of the field's power, turned by the round-trip phase $$\phi$$. The function `airy` sums the series in closed form (Section 13.5):

```python
    rho = math.sqrt(R1 * R2) * A                          # what one round trip returns, in amplitude squared
    s2 = np.sin(np.asarray(phi) / 2) ** 2
    den = (1 - rho) ** 2 + 4 * rho * s2
    T = (1 - R1) * (1 - R2) * A / den
    R = ((math.sqrt(R1) - math.sqrt(R2) * A) ** 2 + 4 * math.sqrt(R1 * R2) * A * s2) / den
```

`finesse` uses the exact width of an Airy peak, $$F = \pi/\left(2\arcsin[(1 - \rho)/(2\sqrt{\rho})]\right)$$, and `finesse_approx` the familiar $$\pi\sqrt{\rho}/(1 - \rho)$$. The script also measures the width numerically, and checks that a lossless cavity conserves energy, $$T + R = 1$$.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

Lossless equal mirrors: finesse 2.27, 8.71 and 61.23 for $$R$$ = 0.30, 0.70 and 0.95 (Figure 13.5a: 2.3, 8.7 and 61.2). The approximation gives 2.46, 8.76 and 61.24: it is good only at high finesse. Every peak reaches $$T = 1$$, and $$T + R - 1$$ stays below 3 × 10⁻¹⁶. Unequal mirrors, 0.95 and 0.60: 33.3 % on resonance (the fp demo: 33 %); 0.60 and 0.60: 100 %.

</div>

## <span class="secnum">L13.2</span>A cavity between two Bragg mirrors

Worked Example 13.3 treats each grating as a mirror of reflectance $$\tanh^2(\kappa L_g)$$ placed a penetration depth $$L_p = \tanh(\kappa L_g)/(2\kappa)$$ inside it. Part B tests that picture against the coupled-mode transfer matrices of Section 13.3, with the grating of Worked Example 13.2: a 500 × 220 nm strip, $$\kappa$$ = 12.6 mm⁻¹, 300 periods of 316.8 nm. A uniform grating is a single matrix, and a spacer is the same matrix with $$\kappa = 0$$:

```python
    d = delta(lam, alpha)
    G = section(N * PER, d, KAP)
    S = section(Ns * PER, d, 0.0)
    Q = np.array([[np.full_like(d, -1j), 0 * d], [0 * d, np.full_like(d, 1j)]])
    M = mul(mul(mul(G, S), Q), G)
    return 1 / np.abs(M[0, 0]) ** 2                            # B = 0 beyond the far end: t = 1 / M11
```

The matrix `Q` adds a quarter wave each way, so the spacer is 316.5 periods long and one resonance falls on the Bragg wavelength. A loss enters as an imaginary part of the detuning, `delta(lam, alpha)`.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

$$\kappa L_g$$ = 1.198, $$R$$ = 69.4 %, $$L_p$$ = 33.1 µm, spacer 100.28 µm, $$L_\mathrm{eff}$$ = 166.4 µm. The Airy picture gives an FSR of 1.727 nm, finesse 8.50, FWHM 203 pm, $$Q$$ = 7626 and a photon lifetime of 6.27 ps. The transfer matrices give a resonance at 1550.000 nm, 204.0 pm wide, and neighbours at −1.656 and +1.659 nm, 0.44 nm wide (Worked Example 13.3: 33.1 µm, 166.4 µm, 1.73 nm, 8.50, 203 pm, 7600, 6.3 ps; 204 pm, ±1.66 nm, 0.44 nm). With 2 dB/cm: the Airy picture gives a peak of 0.959 and finesse 8.32; the transfer matrices, with the loss in every section, 0.956 and 208 pm (Worked Example 13.3: 96 % and 8.3).

</div>

The penetration-depth picture is exact at the Bragg wavelength and drifts away from it: the neighbours are closer than one Airy FSR (1.66 against 1.73 nm), because the light reaches deeper into the gratings off the Bragg wavelength, and they are broader, because each grating reflects only 46 % there.

## <span class="secnum">L13.3</span>Loss from the fringes

A waveguide between two cleaved facets is a weak Fabry–Pérot cavity. Its fringe contrast $$K = (T_\mathrm{max} - T_\mathrm{min})/(T_\mathrm{max} + T_\mathrm{min}) = 2\rho/(1 + \rho^2)$$ gives $$\rho = (1 - \sqrt{1 - K^2})/K$$, and with the facet reflectance known, the loss $$\alpha = \ln(R/\rho)/L$$. The coupling efficiency cancels from the ratio, which is the method's attraction {% include cite.html keys="regener1985" %}. `measure_cleaved` simulates a 2 mm III–V waveguide ($$n_g$$ = 3.6, $$R$$ = 0.30, 3 dB/cm) swept over 2 nm in 0.5 pm steps, with 0.5 % detector noise and a coupling that drifts by ±10 % across the sweep. `fringe_contrast` smooths the trace a little and takes the largest and smallest values in each free spectral range:

```python
    Ps = np.convolve(P, np.ones(smooth) / smooth, mode="same")
    edges = np.arange(lam[0] + smooth * (lam[1] - lam[0]), lam[-1] - fsr, fsr)
    for e in edges:
        m = (lam >= e) & (lam < e + fsr)
        hi, lo = Ps[m].max(), Ps[m].min()
        K.append((hi - lo) / (hi + lo)); lc.append(e + fsr / 2)
```

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

FSR 167 pm, $$\rho$$ = 0.2613 and $$K$$ = 0.4892 for the true loss. Eleven fringes give $$K$$ = 0.4900 ± 0.0064 and a loss of 2.96 ± 0.33 dB/cm. Without the drift the fringes agree to ±0.03 dB/cm; with the drift and no noise they scatter by ±0.35 dB/cm. Assuming $$R$$ = 0.28 or 0.32 instead of 0.30 gives 1.46 or 4.36 dB/cm. Three lengths, 1, 2 and 4 mm, fitted as $$\ln\rho = \ln R - \alpha L$$, give 3.21 dB/cm and $$R$$ = 0.304 without knowing $$R$$.

</div>

Two lessons. First, the coupling's drift does not cancel within a fringe: a slope across one FSR raises one side of the fringe and lowers the other, and that, not the detector noise, sets the scatter (panel c of the figure). It averages out over many fringes, and dividing the trace by its running mean removes it (Exercise 5). Second, the method is only as good as the facet reflectance: 0.02 of error in $$R$$ moves the answer by about 1.5 dB/cm on a 2 mm guide. Measuring several lengths, as in a cutback but with no dependence on the coupling, removes $$R$$ from the problem.

## <span class="secnum">L13.4</span>Gain from the fringes below threshold

Below threshold a laser chip emits spontaneous emission filtered by its own cavity, and the round trip now has gain: $$\rho = \sqrt{R_1R_2}\,G$$ with $$G = e^{(\Gamma g - \alpha_i)L}$$. The peak-to-valley ratio $$r$$ of each fringe gives $$\rho = (\sqrt{r} - 1)/(\sqrt{r} + 1)$$ and hence the net modal gain $$\Gamma g - \alpha_i = \ln(\rho/\sqrt{R_1R_2})/L$$: the Hakki–Paoli method {% include cite.html keys="hakki1975" %}. Part D uses the laser of Worked Example 24.1 (400 µm, $$R$$ = 0.32, $$n_g$$ = 3.6, $$\alpha_i$$ = 15 cm⁻¹) with the parabolic gain of the laser demo, at three currents that give a net modal gain of 10, 20 and 26 cm⁻¹ at the peak. Threshold is at 28.5 cm⁻¹, the mirror loss. `osa` then blurs the spectrum as an optical spectrum analyser with a given resolution would:

```python
    for res in (0.0, 0.02e-3, 0.06e-3, 0.1e-3):
        lg, gg = hakki_paoli(lam, osa(lam, P, res), fsr)
```

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

FSR 834 pm; $$\alpha_m$$ = 28.5 cm⁻¹ (Chapter 24: 0.83 nm and 28.5 cm⁻¹). With a perfect spectrometer the method returns 10.0, 20.0 and 26.0 cm⁻¹ at the peak. The fringes are 206, 91 and 26.4 pm wide there, and a finite resolution reads them low:

| Net gain | Fringe FWHM | 20 pm | 60 pm | 100 pm |
|---|---|---|---|---|
| 10 cm⁻¹ | 206 pm | 9.9 | 9.3 | 8.4 |
| 20 cm⁻¹ | 91 pm | 19.9 | 19.0 | 18.0 |
| 26 cm⁻¹ | 26.4 pm | 25.7 | 24.8 | 23.9 |

</div>

The closer to threshold, the narrower the fringes and the larger the error: a spectrometer that blurs the peaks lowers them and raises the valleys, so $$r$$ and the gain come out too small. Near threshold the fringes are a few tens of picometres wide, finer than many spectrum analysers resolve.

<figure id="fig-l13-1">
  <img src="{{ '/assets/figs/lab13_expected.png' | relative_url }}" style="width:760px" alt="Four plots from the lab script: Airy transmission against round-trip phase for mirrors of 0.3, 0.7 and 0.95; the transmission of the Bragg-mirror cavity from transfer matrices against the Airy formula with the effective length, agreeing at the central resonance and drifting apart away from it; the simulated fringes of a 2 mm cleaved waveguide with an inset of the loss extracted from each fringe scattering around 3 dB/cm; and the net modal gain from Hakki-Paoli analysis at three currents, exact and read low with a 60 pm spectrometer">
  <figcaption><span class="capnum">Figure L13.1.</span> <strong>What the script draws.</strong> (a) The Airy function for lossless mirrors, as in Figure 13.5a. (b) The Bragg-mirror cavity of Worked Example 13.3: transfer matrices against the Airy formula with \(L_\mathrm{eff}\) = 166.4 µm, exact at 1550 nm and drifting away from it. (c) Part of the simulated sweep of a 2 mm cleaved waveguide; the inset gives the loss from each fringe, scattered around the true 3 dB/cm by the drifting coupling. (d) Net modal gain from the fringes at three currents: exact (dots, on the model's curves) and with a 60 pm spectrometer (crosses), which reads low, most of all near threshold (dotted line). Drawn by <code>lab13_fp.py</code>.</figcaption>
</figure>

## Exercises

1. **A high-finesse cavity.** With lossless mirrors of 0.99 and the effective length of Part B, what are the finesse, the FWHM and the Q?
2. **Matching a lossy cavity.** In Part B with 2 dB/cm, keep $$R_2$$ = 0.694. Which $$R_1$$ makes the reflection vanish on resonance? Is the transmission then 100 %?
3. **AR-coated facets.** Repeat Part C (no drift) with both facets at $$R$$ = 0.01. What contrast do you expect, and what loss does the script extract?
4. **Spectrometer resolution.** What resolution reads the 26 cm⁻¹ point within 1 cm⁻¹? What do the 10 and 20 cm⁻¹ points read then?
5. **Remove the drift.** Divide the Part C trace by its running mean over one FSR before taking the contrast. How much does the scatter shrink?
6. **A parasitic cavity.** Two grating couplers 1 mm apart on a silicon strip ($$n_g$$ = 4.18, 2 dB/cm) each reflect 1.6 % back into the waveguide ([Lab 9]({% link labs/lab09_analysis.md %})). What ripple, in dB, and what period do they add to the transmission?

<details markdown="1">
<summary>Answers</summary>

1. $$F$$ = 312.6, FWHM = 1.727 nm / 312.6 = 5.5 pm, $$Q = 2.8\times10^5$$.
2. $$R_1 = R_2A^2$$ = 0.683. The reflection on resonance vanishes, but the transmission is 95.9 %: the other 4.1 % is absorbed inside. With loss, matching removes the reflection, not the absorption.
3. $$\rho$$ = 0.0087, so $$K$$ = 0.017: fringes only 1.7 % deep, not much more than the detector noise. The script returns 0.10 ± 0.58 dB/cm instead of 3: the method needs reflective facets.
4. About 49 pm. The 10 and 20 cm⁻¹ points then read 9.5 and 19.3 cm⁻¹.
5. From ±0.33 to ±0.03 dB/cm, with a mean of 2.97 dB/cm: the running mean divides out the slope of the coupling.
6. $$\rho$$ = 0.0153, a ripple of 0.27 dB, repeating every 287 pm (the fp demo's "two grating couplers" preset shows it).

</details>

## Going further

- The fp demo of [Section 13.5]({% link chapters/13_bragg.md %}) draws the same Airy function, with the transmitted fields added pass by pass.
- Hakki–Paoli analysis needs resolved fringes. Methods that use the area under each fringe instead of its peak and valley tolerate a coarser spectrometer; try one on the blurred spectra of Part D.
- [Lab 5]({% link labs/lab05_bragg.md %}) builds gratings section by section; replace the uniform mirrors of Part B with apodised ones and watch the neighbours of the resonance change.
- [Lab 10]({% link labs/lab10_rate_equations.md %}) takes the same laser above threshold, where the gain clamps at the 28.5 cm⁻¹ that Part D approaches.
