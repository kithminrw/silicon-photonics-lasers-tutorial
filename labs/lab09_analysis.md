---
title: "Lab 9. Analyse measured openEBL data"
parent: Hands-On Labs
nav_order: 9
permalink: /labs/lab-09/
---

# <span class="chapnum">Lab 9 · Make</span>Analyse Measured openEBL Data

Take the raw sweeps of a test chip, divide out the grating couplers, read the group index from an MZI's fringes, fit three ring resonances and decide which of each ring's two solutions is real, and measure the propagation loss by cutback, with an error bar on every number.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- read openEBL-style sweep files, and fit the grating couplers' envelope and the fringes between them;
- calibrate an unbalanced MZI with the loopback and extract the group index and its dispersion;
- write a Levenberg–Marquardt fit, and fit ring resonances with a Lorentzian and with the all-pass model;
- find both (a, t) solutions of each ring and resolve the ambiguity with the gap series;
- fit a cutback with its error bar, and compare the loss with the rings'.

</div>

## What you need

- [Chapter 32]({% link chapters/32_analysis.md %}) (Sections 32.1 to 32.5), with [Chapter 31]({% link chapters/31_testing.md %}) (Section 31.3), [Chapter 7]({% link chapters/07_loss.md %}) (Section 7.7), [Chapter 11]({% link chapters/11_mzi.md %}) (Sections 11.3 and 11.6) and [Chapter 12]({% link chapters/12_rings.md %}) (Sections 12.2 to 12.5, Table 12.1).
- Python 3.11 or newer with NumPy and Matplotlib: `pip install numpy matplotlib`. The fits are written out in the script, so SciPy is not needed.
- The script <a href="{{ '/labs/lab09_analysis.py' | relative_url }}" download><code>lab09_analysis.py</code></a> and the data: either the ten CSV files listed below, saved in a folder `data/` beside the script, or the generator <a href="{{ '/labs/lab09_make_data.py' | relative_url }}" download><code>lab09_make_data.py</code></a>, which writes the same files there (all three are also in the repository's [`labs/` folder](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs)).
- About two hours, including the exercises.

Run them from a terminal in the folder where you saved them:

```
python lab09_make_data.py
python lab09_analysis.py
```

The analysis prints a checkpoint for each part below, with the true value and the chapter's value beside it, and saves the figure `lab09_analysis.png` in a few seconds. Read each part, then the matching function in the script; change things and run it again. Wavelengths are in nanometres and powers in dBm, as in the openEBL files.

## The data: a simulated openEBL chip

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">These measurements are simulated</div>

The files are not measurements. `lab09_make_data.py` writes them with NumPy from a known chip, so that every number you extract can be checked against the truth; the last section of this page shows where to get real openEBL data and how to run the same analysis on it. The files copy the layout of a real openEBL sweep file's header (Section 32.1) and every imperfection of [Section 31.3]({% link chapters/31_testing.md %}).

</div>

The chip is "your first chip" of Chapters 30–32: 500 × 220 nm silicon strips with $$n_g = 4.1836$$ at 1550 nm (femwell, [Chapter 6]({% link chapters/06_soi.md %})), rising by $$1.12\times10^{-4}$$ per nm, and 2.00 dB/cm of loss. Every device sits between two grating couplers, and the generator adds what a real bench adds:

- **coupler envelope:** 6.0 dB per coupler at 1548 nm, 1 dB down 16 nm either side (a 32 nm 1 dB bandwidth), with each structure's pair of couplers off by a random 0.25 dB rms in loss and 0.5 nm in centre;
- **fringes:** each coupler reflects −18 dB in amplitude (1.6 % in power) back into the chip, so the waveguide between them is a weak Fabry–Pérot cavity;
- **noise:** 1 % of the power, and a detector floor at −62 dBm (where the couplers pass almost nothing, the trace becomes noise);
- **wavelength errors:** 0.1 pm rms of jitter on every point, and an offset of a few picometres on each sweep.

**Table L9.1. The data files.** Each starts with `#` lines: first the true values used to make it (lines `# True …`), then the sweep's settings in the layout of a real file. The laser power is 0 dBm.
{: .tabcaption #tab-l9-1 }

| File | Device | Sweep |
|---|---|---|
| [`lab09_loopback.csv`]({{ '/labs/data/lab09_loopback.csv' | relative_url }}) | two couplers joined by 300 µm of waveguide | 1480–1600 nm, 0.1 nm steps |
| [`lab09_mzi_dL100.csv`]({{ '/labs/data/lab09_mzi_dL100.csv' | relative_url }}) | MZI of two Y-branches (53/47 split, 0.3 dB each), ΔL = 100 µm | 1480–1600 nm, 0.1 nm steps |
| [`lab09_ring_r10_g200.csv`]({{ '/labs/data/lab09_ring_r10_g200.csv' | relative_url }}), [`…g250`]({{ '/labs/data/lab09_ring_r10_g250.csv' | relative_url }}), [`…g300`]({{ '/labs/data/lab09_ring_r10_g300.csv' | relative_url }}) | all-pass rings, 10 µm radius, gaps of 200, 250 and 300 nm (κ² = 1.235, 0.516 and 0.215 %) | ±0.5 nm around one resonance, 1 pm steps |
| [`lab09_cutback_02500um.csv`]({{ '/labs/data/lab09_cutback_02500um.csv' | relative_url }}), [`05000um`]({{ '/labs/data/lab09_cutback_05000um.csv' | relative_url }}), [`10000um`]({{ '/labs/data/lab09_cutback_10000um.csv' | relative_url }}), [`20000um`]({{ '/labs/data/lab09_cutback_20000um.csv' | relative_url }}), [`40000um`]({{ '/labs/data/lab09_cutback_40000um.csv' | relative_url }}) | waveguides of 0.25, 0.5, 1, 2 and 4 cm between couplers | 1480–1600 nm, 0.1 nm steps |

The couplings are those of the coupler model of [Chapter 9]({% link chapters/09_couplers.md %}) that Table 12.1 uses (it rounds them to 1.23, 0.52 and 0.22 %). Each ring has its own small error of effective index, as fabricated rings do, so the three resonances land at 1552.14, 1552.29 and 1550.29 nm. The ring files are fine sweeps of one resonance each, as you would measure after finding it in a broad sweep; the standard openEBL sweep is much coarser (Exercise 1). The top of a ring file looks like this:

```
# SIMULATED DATA, not a measurement: Open-Photonics Lab 9, written by lab09_make_data.py (seed 9).
# It imitates an openEBL sweep file. The 'True' lines give the values used to make it.
# True propagation loss:	2.00 dB/cm
...
# True kappa^2:	0.5159 %
...
# Device ID:	 OpenPhotonics_ring_r10_g250
# Settings:
#	Laser power:	0.0 dBm
#	Wavelength step-size:	0.001 nm
wavelength,channel_1
1551.800,-12.109
```

## <span class="secnum">L9.1</span>Reading a file, and the couplers' envelope

`load_spectrum` returns the wavelengths, the powers and a dictionary of the header. It reads both layouts: these files store the data in columns, while real openEBL files store each variable as a row (`wavelength,1475,1475.008,…`, then `channel_1,…`). A real file holds one row per detector channel, and without a `channel` argument the function returns the strongest, the detector that saw the device.

The loopback is the couplers alone. A Gaussian passband is a parabola in decibels, and the loopback holds two couplers, so it falls by 2 dB where each coupler falls by 1 dB. `coupler_envelope` fits that parabola to the top 6 dB, as Section 32.2 recommends:

```python
def coupler_envelope(wl, p, within_db=6.0):
    top = p > p.max() - within_db
    c2, c1, c0 = np.polyfit(wl[top] - 1550, p[top], 2)
    centre = 1550 - c1 / (2 * c2)
    return {"peak": c0 - c1 ** 2 / (4 * c2), "centre": centre, "bw1": np.sqrt(-8 / c2),
            "poly": lambda x: np.polyval([c2, c1, c0], x - 1550)}
```

What the parabola leaves is the ripple. Reflections a distance $$L$$ apart make fringes every $$\lambda^2/(2n_gL)$$, so a sinusoid in $$1/\lambda$$ fits them. `fringe_cavity` tries every $$L$$ from 20 µm to 2 mm and keeps the one whose sinusoid fits best: the period of a ripple tells you where the reflections are.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

The loopback peaks at −11.86 dBm at 1548.1 nm: 5.90 dB per coupler (true: 6.0 dB plus half of this pair's offset of −0.20 dB, so 5.90 dB, at 1548.1 nm). One coupler's 1 dB bandwidth is 32.0 nm (true 32 nm; [Chapter 31]({% link chapters/31_testing.md %}): "a 30–40 nm wide passband"). The ripple is 0.27 dB peak to peak and repeats every 0.96 nm: reflections 300 µm apart, the length of the loopback's waveguide (true: 0.27 dB, 300 µm).

</div>

## <span class="secnum">L9.2</span>Group index from the MZI

`calibrate` subtracts the loopback, in decibels, from the MZI: the couplers' envelope cancels and the MZI's own response remains (Section 32.2). Only the band where the loopback is within 10 dB of its peak is kept; outside it the signal sinks towards the floor. An MZI's output is a sinusoid in its phase, and its troughs are sharp, so `fringe_troughs` takes the lowest point of each fringe and fits $$A + B\cos(2\pi x/\mathrm{FSR}) + C\sin(2\pi x/\mathrm{FSR})$$ to the points within a quarter of an FSR around it. The fit's minimum falls between the samples:

```python
        sel = np.abs(wl - wl[i]) <= fsr_guess / 4
        ph = 2 * np.pi * (wl[sel] - wl[i]) / fsr_guess
        A, B, C = np.linalg.lstsq(np.column_stack([np.ones_like(ph), np.cos(ph), np.sin(ph)]), t_lin[sel], rcond=None)[0]
        out.append(wl[i] + np.arctan2(-C, -B) * fsr_guess / (2 * np.pi))   # B cos + C sin is lowest at phase atan2(-C, -B)
```

Each pair of neighbouring troughs gives an FSR, and the key equation of Section 32.4 turns it into a group index at their midpoint, $$n_g = \lambda^2/(\mathrm{FSR}\cdot\Delta L)$$. A straight line through those values (`line_fit`, the least-squares line with the standard errors of Section 32.3) gives $$n_g$$ at 1550 nm and its slope. The same fits give each fringe's highest and lowest transmission, and the ratio measures the splitters' balance: with power fractions $$s$$ and $$1 - s$$, the extinction is $$20\log_{10}[1/(2s - 1)]$$ (Section 11.6).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

Twelve troughs from 1517.9 to 1581.0 nm. The FSR at 1550 nm is 5.742 nm (true 5.743 nm; Chapter 11: 5.75 nm with $$n_g = 4.18$$). $$n_g = 4.1840 \pm 0.0004$$ at 1550 nm (true 4.1836; Chapters 6 and 32: 4.18), rising by $$(1.12 \pm 0.23)\times10^{-4}$$ per nm (true $$1.12\times10^{-4}$$). The fringes are 24.1 dB deep, so the Y-branches split 0.531/0.469 (true 24.3 dB and 0.530/0.470).

</div>

The error of $$n_g$$ is a ten-thousandth: an FSR measured over twelve fringes is far more precise than any one fringe. An imbalance in the arms, or a $$\Delta L$$ that differs from the drawing, would bias it instead; two MZIs with different $$\Delta L$$ separate the two (Section 32.4).

## <span class="secnum">L9.3</span>Fitting a resonance: Lorentzian

Near a resonance the all-pass ring is a Lorentzian dip on a slowly varying baseline: the couplers' envelope and a piece of a fringe. `fit_ring` fits both at once, with the baseline a parabola in decibels (the "smooth envelope fitted to the device's own spectrum" of Section 32.2) and the dip of depth $$D$$ and full width $$w$$:

```python
def lorentz_db(x, p):
    x0, w, D, b0, b1, b2 = p
    return b0 + b1 * x + b2 * x * x + 10 * np.log10(1 - D / (1 + (2 * (x - x0) / w) ** 2))
```

The fit is nonlinear in $$x_0$$, $$w$$ and $$D$$, and `levenberg_marquardt` does it in about thirty lines. Each step solves the linearised problem $$(J^\mathsf{T}J + \lambda\,\mathrm{diag}\,J^\mathsf{T}J)\,\delta p = J^\mathsf{T}r$$, with the Jacobian $$J$$ from central differences and $$r$$ the residuals. A small $$\lambda$$ makes it a Gauss–Newton step; when a step makes the fit worse, $$\lambda$$ grows tenfold and the step shrinks towards the steepest descent. At the end, $$s^2(J^\mathsf{T}J)^{-1}$$, with $$s^2$$ the residuals' variance, is the covariance matrix of the parameters, whose diagonal gives their error bars.

The starting point comes from the data: the lowest point of a five-point moving average, its depth, and the width where it crosses half that depth. The window is ±12 of those widths. The fit compares powers in milliwatts, not decibels. Near the bottom of a deep dip a wavelength error of 0.1 pm is a large error in decibels, and a fit in decibels lets those few points steer it; in linear power they weigh no more than the others. The loaded Q is $$\lambda_0/w$$ and the extinction $$-10\log_{10}(1 - D)$$.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

| Gap | FWHM | Loaded Q | Extinction | True | Table 12.1 |
|---|---|---|---|---|---|
| 200 nm | 22.60 ± 0.20 pm | 68 682 ± 593 | 4.11 ± 0.04 dB | 22.33 pm, 69 514, 4.12 dB | 22.3 pm, 70 000, 4.1 dB |
| 250 nm | 11.83 ± 0.10 pm | 131 256 ± 1072 | 10.85 ± 0.25 dB | 11.76 pm, 132 001, 10.98 dB | 11.7 pm, 132 000, 11.0 dB |
| 300 nm | 7.44 ± 0.07 pm | 208 419 ± 2028 | 15.91 ± 1.04 dB | 7.35 pm, 210 879, 16.70 dB | 7.4 pm, 211 000, 16.7 dB |

</div>

The deepest dip is the least certain: at 16.7 dB the bottom holds only 2 % of the light, and the jitter of the points on its steep sides moves the fitted depth by a decibel. Extinction ratios of deep resonances are always quoted loosely for this reason; widths and Q are robust.

## <span class="secnum">L9.4</span>Two solutions, and the gap series

The all-pass formula of Section 12.2 gives the same spectrum for $$(a, t)$$ and $$(t, a)$$. So a width and a depth fix the product $$at$$ and the difference $$\lvert a - t\rvert$$, but not which is which. From the FWHM formula of Section 12.4, with $$F = \pi w/\mathrm{FSR}$$, $$(1 - at)/\sqrt{at} = F$$, so $$\sqrt{at} = (\sqrt{F^2 + 4} - F)/2$$; and from $$T_\mathrm{min} = (a - t)^2/(1 - at)^2$$, $$\lvert a - t\rvert = \sqrt{T_\mathrm{min}}\,(1 - at)$$. The larger root is $$a$$ for an over-coupled ring and $$t$$ for an under-coupled one. `fit_ring` starts the all-pass fit from each, and keeps each fit on its own side of $$a = t$$:

```python
    # the two all-pass solutions that match this width and depth (Section 12.4): a t from the FWHM ...
    fsr = xc ** 2 / (ng * 2 * np.pi * radius_um * 1e3)
    F = np.pi * w / fsr
    at = ((-F + np.sqrt(F * F + 4)) / 2) ** 2
    diff = np.sqrt(1 - D) * (1 - at)                                  # ... and |a - t| from the depth
    s = np.sqrt(diff ** 2 + 4 * at)
    hi, lo = (s + diff) / 2, (s - diff) / 2
```

The FSR uses the group index that the MZI measured, which is why the MZI comes first: the fit measures the resonance's width in units of the FSR (Exercise 3). Each solution gives a loss, $$-20\log_{10}(a)/L$$ in dB per unit length with $$L = 2\pi R$$, and a coupling $$\kappa^2 = 1 - t^2$$.

The two solutions fit equally well, so the spectrum alone cannot choose. The gap series can (Worked Example 32.1): the gap changes the coupling, but not the loss of the ring. `resolve_gap_series` tries all $$2^3 = 8$$ ways of picking one solution per ring and keeps the one whose three losses agree best, measured by their $$\chi^2$$ about the weighted mean.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

Both solutions of every ring fit equally well (the ratio of their $$\chi^2$$ is 1.0000). The gap series picks over-, over- and under-coupled, with losses of 2.02 ± 0.01, 2.00 ± 0.02 and 2.05 ± 0.05 dB/cm ($$\chi^2 = 1.4$$ for 2 degrees of freedom), and couplings of 1.250, 0.520 and 0.214 %, which fall 5.83 times per 100 nm (true: 1.235, 0.516 and 0.215 %, over, over and under, as in Table 12.1; the Chapter 9 model falls 5.75 times). The other set has "losses" of 8.7, 3.6 and 1.5 dB/cm and "couplings" of 0.291, 0.289 and 0.296 % (Worked Example 32.1: 8.6, 3.6 and 1.5 dB/cm, couplings that barely change). The rings' weighted mean loss is 2.01 ± 0.01 dB/cm (true 2.00; Table 12.1: 2 dB/cm).

</div>

The wrong set has a clear signature: its "couplings" are all $$1 - a^2 = 0.29$$ %, the coupling that would critically couple a 2 dB/cm ring, because swapping $$a$$ and $$t$$ turns the true loss into a coupling. Plot (e) of the figure shows the two sets mirrored about the critical-coupling curve. The error bars of the ring losses are statistical only: an error in $$n_g$$, or a baseline that bends inside the window, adds to them.

## <span class="secnum">L9.5</span>Propagation loss by cutback

`insertion_loss` averages each cutback spectrum, in milliwatts, over ±1 nm around 1550 nm and subtracts it from the laser's power. `line_fit` then fits loss against length (Section 32.3):

```python
def line_fit(x, y):
    n, xm = x.size, x.mean()
    sxx = ((x - xm) ** 2).sum()
    c1 = ((x - xm) * (y - y.mean())).sum() / sxx
    c0 = y.mean() - c1 * xm
    sy = np.sqrt(((y - c0 - c1 * x) ** 2).sum() / (n - 2))     # scatter of the points about the line
    return c0, c1, sy * np.sqrt(1 / n + xm ** 2 / sxx), sy / np.sqrt(sxx), sy
```

The slope is the loss and its error is $$\sigma_y/\sqrt{\sum_i(L_i - \bar L)^2}$$, as in Section 32.3. Here $$\sigma_y$$ is almost all coupler-to-coupler variation, which no averaging over wavelength removes. Half the intercept is one coupler's loss. Repeating the fit at every wavelength from 1500 to 1595 nm gives the loss spectrum in the inset of plot (f).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint E</div>

The loss is 1.98 ± 0.06 dB/cm, with 0.18 dB of scatter about the line (true 2.00 dB/cm and 0.25 dB rms of coupler variation; Chapters 7 and 12: 2 dB/cm). The intercept, 12.10 ± 0.12 dB, gives 6.05 dB per coupler at 1550 nm (true 6.02 dB), while the loopback's own pair gives 5.91 dB. The loss spectrum stays between 1.92 and 2.03 dB/cm from 1500 to 1595 nm, ±0.06 dB/cm at each wavelength. With the rings' 2.01 ± 0.01 dB/cm, the weighted mean is 2.01 ± 0.01 dB/cm.

</div>

The cutback and the rings agree, by two independent routes: one uses centimetres of waveguide and the couplers' scatter, the other 63 µm of ring and the shape of a resonance. The loopback's couplers differ from the cutback's by 0.14 dB, as Section 31.3 warns: absolute losses carry a few tenths of a decibel of coupler variation, and slopes, widths and wavelengths do not.

<figure id="fig-l9-1">
  <img src="{{ '/assets/figs/lab09_expected.png' | relative_url }}" style="width:760px" alt="Six plots from the lab script: the raw loopback, MZI and 4 cm cutback sweeps with the coupler envelope fit; the MZI divided by the loopback with its troughs; group index against wavelength; the three ring resonances with all-pass fits; propagation loss against coupling for both solutions of each ring; and insertion loss against length for the cutback, with the loss spectrum as an inset">
  <figcaption><span class="capnum">Figure L9.1.</span> <strong>What the script draws.</strong> (a) Raw sweeps: the loopback with its parabola fit, the MZI, and the 4 cm cutback sinking towards the detector floor at the band edges. (b) The MZI minus the loopback, with the troughs found by sinusoid fits. (c) Group index from each pair of troughs, the straight-line fit and the true line. (d) The three resonances with their baselines removed, and the all-pass fits. (e) Both solutions of each ring: the chosen set (filled) at 2 dB/cm, the mirror set (open) near κ² = 0.29 %, on either side of the critical-coupling curve. (f) Cutback at 1550 nm; inset, the loss at each wavelength with its error band.</figcaption>
</figure>

## Real openEBL data

The same functions run on real measurements. This is where they are, and what they look like (checked in November 2026):

1. **Where.** Each openEBL run has a repository on the SiEPIC GitHub, named after its tape-out month, for example [openEBL-2025-05](https://github.com/SiEPIC/openEBL-2025-05), [openEBL-2025-10](https://github.com/SiEPIC/openEBL-2025-10) and [openEBL-2026-02](https://github.com/SiEPIC/openEBL-2026-02). Its README links the data (under *Measurement data* in recent runs), which sit on a UBC file server rather than in the repository itself; the link appears four to six weeks after the tape-out. The [openEBL page](https://siepic.ca/openebl/) also links the data of the past one to two years, and older runs (2017–2023) are available on request. The repositories are MIT-licensed; check the run's README for any terms on the data.
2. **Which files.** In the examples in the [SiEPIC_Analysis](https://github.com/SiEPIC/SiEPIC_Analysis) repository, the data are sorted by band, polarisation and temperature (for example `1550/TE/25C/`), then by chip, die and test (`sweepLaser`), with one folder per device. A device's folder is named after its test label: a label `opt_in_TE_1550_openEBL_yourname_MZI1` gives the folder `yourname_MZI1`. It holds the sweep as a CSV file and a MATLAB `.mat` file named by the time of the measurement, for example `17-Nov-2025 02.13.21.csv`. The same repository has a viewer that matches each file to its label in the layout by the coordinates in the file's header.
3. **What is in a file.** The header lines start with `#`: the test, the user, the start and finish times, the device ID, the device's coordinates in the layout and on the stage, and the settings. In the examples these are an HP 81680A laser and an HP 81635A detector, sweeping at 40 nm/s with −2 to 0 dBm in 8 pm steps, from 1460 or 1475 nm to about 1580 nm. The data follow as rows: `wavelength`, then the wavelengths in nm, then `channel_1`, `channel_2`, … with the power each detector received, in dBm. The `.mat` file holds the same data for MATLAB, or for Python with `scipy.io.loadmat`.

To analyse your own devices, put this script next to the files and call its functions from Python, with the dimensions from your layout:

```python
import numpy as np
import lab09_analysis as lab

wl, p, meta = lab.load_spectrum("yourname_MZI1/17-Nov-2025 02.13.21.csv")   # the strongest channel, or channel="channel_2"
print(meta["Device ID"], meta["Wavelength step-size"])
wl_lb, p_lb, _ = lab.load_spectrum("yourname_loopback/....csv")   # a loopback from the same chip
cal = lab.calibrate(wl, p, wl_lb, p_lb)
band = p_lb.max() - np.interp(wl, wl_lb, p_lb) < 10               # where the couplers pass light
mzi = lab.mzi_group_index(wl[band], cal[band], dl_um=100.0)       # your MZI's delta L
wl_r, p_r, _ = lab.load_spectrum("yourname_ring1/....csv")
ring = lab.fit_ring(wl_r, p_r, ng=mzi["ng1550"], radius_um=10.0, centre=1550.3)   # one resonance of a broad sweep
print(ring["Q"], ring["ext"], ring["sols"]["under"]["loss"], ring["sols"]["over"]["loss"])
```

`fit_ring` cuts its own window around `centre`, so it works on a full sweep. Real data add what the simulation leaves out: resonances split by backscattering ([Section 12.6]({% link chapters/12_rings.md %})), TM light from a polarisation error, and structures that failed. With 8 pm steps, resonances narrower than about 40 pm (loaded Q above about 40 000) are under-sampled, as Exercise 1 shows.

## Exercises

1. **The openEBL step.** The standard openEBL sweep uses 8 pm steps. Refit the three rings with every eighth point (`wl[::8], p[::8]`). What happens to the 300 nm ring's Q and extinction, and to the losses? Does the gap series still choose correctly? Try the other starting points `wl[2::8]`, `wl[4::8]` and `wl[6::8]` too.
2. **A short cutback.** Fit the cutback with only the three shortest waveguides (0.25, 0.5 and 1 cm). What are the loss and its error bar, and why?
3. **The wrong group index.** Fit the 250 nm ring with the slab's group index, $$n_g = 3.70$$ ([Lab 1]({% link labs/lab01_slab.md %})), instead of the MZI's: `fit_ring(wl, p, 3.70)`. How do the loss, the coupling and Q change?
4. **The critical gap.** Fit $$\ln\kappa^2$$ against the gap through the three physical couplings of Checkpoint D. Which gap would critically couple a ring with the measured loss?
5. **Q alone.** Coupled-mode theory gives the intrinsic Q from the loaded Q and the depth, $$Q_i = 2Q_L/(1 \pm \sqrt{T_\mathrm{min}})$$, with + for an under-coupled ring and − for an over-coupled one, and the loss from $$Q_i = 2\pi n_g/(\lambda\alpha)$$ (Section 12.4). Compute both answers for each ring from Checkpoint C. How do they compare with the all-pass fits?

<details markdown="1">
<summary>Answers</summary>

1. With every eighth point the 300 nm ring's 7.4 pm resonance falls between one or two samples: Q drops to 174 000 ± 17 000 and the extinction to 7.4 ± 1.8 dB (true 210 900 and 16.7 dB), and its under-coupled solution gives 3.0 ± 0.5 dB/cm. The 200 nm ring gives Q = 62 700 ± 2000 and 2.18 dB/cm. The gap series still picks the right set, but the mean loss is 2.16 ± 0.04 dB/cm, against 2.00. From the other starting points the 300 nm ring's Q ranges from 174 000 to 197 000 and its extinction from 7.4 to 14.7 dB: under-sampled fits depend on where the samples fall. Sweep high-Q rings at a step of a fifth of their width or finer, here 1–2 pm.
2. 1.49 ± 0.28 dB/cm (true 2.00), with 0.15 dB of scatter. The spread of lengths, $$\sqrt{\sum_i(L_i - \bar L)^2}$$, is 0.54 cm instead of 3.05 cm, so the same coupler scatter gives an error bar more than five times larger (Section 32.3). Adding the 2 cm waveguide gives 1.87 ± 0.14 dB/cm; the 4 cm spiral does most of the work.
3. The over-coupled solution gives 1.77 dB/cm and κ² = 0.460 %, against 2.00 dB/cm and 0.520 % with the MZI's 4.184: both fall in proportion to $$n_g$$ (3.70/4.184 = 0.884). Q stays at 131 256. The fit measures the resonance's width in units of the FSR, and $$1 - at$$ is proportional to it, so an error in $$n_g$$ passes straight into the loss and the coupling, but not into Q.
4. The couplings fall 5.83 times per 100 nm. At 2.01 dB/cm, $$a = 0.998546$$, and critical coupling needs $$\kappa^2 = 1 - a^2 = 0.291$$ %, at a gap of 283 nm (the Chapter 9 model gives 283.2 nm). A ring at that gap would give the deepest notch; Worked Example 12.1 notes that at 250 nm it would need 3.6 dB/cm.
5. For the 200 nm ring, $$Q_i = 84\,600$$ (8.69 dB/cm, under) or 364 600 (2.02 dB/cm, over). For the 250 nm ring, 204 000 (3.61 dB/cm) or 368 000 (2.00 dB/cm). For the 300 nm ring, 359 300 (2.05 dB/cm) or 496 300 (1.48 dB/cm). They are the all-pass fits' two solutions again: a Lorentzian contains the same information, and the same ambiguity. The true $$Q_i$$ is $$3.68\times10^5$$ (Chapter 12: $$3.7\times10^5$$).

</details>

## Going further

- Run the analysis on a real openEBL chip, as described above, and compare its loss, group index and couplings with these.
- The ring-fitting demo of [Chapter 32]({% link chapters/32_analysis.md %}) draws the misfit map behind Checkpoint D, and the test-bench demo of [Chapter 31]({% link chapters/31_testing.md %}) makes spectra like these in your browser.
- Add a drop port. An add-drop ring's drop port breaks the symmetry between loss and coupling ([Sections 12.3 and 12.5]({% link chapters/12_rings.md %})), so one device resolves the ambiguity. Add one to `lab09_make_data.py` and fit both ports together.
- Extract a Bragg grating's κ from its stop band (Section 32.6), with the transfer matrices of [Lab 5]({% link labs/lab05_bragg.md %}).
