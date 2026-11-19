---
title: "Lab 6. A grating coupler in 2D FDTD"
parent: Hands-On Labs
nav_order: 6
permalink: /labs/lab-06/
---

# <span class="chapnum">Lab 6 · Simulate</span>A Grating Coupler in 2D FDTD

Build the shallow-etched grating coupler of Chapter 15 in MEEP, launch the waveguide mode into it, and measure what the chapter can only estimate: where the light goes, how much of it a fibre collects and over what bandwidth, which period puts the peak at 1550 nm, and what the buried oxide does to it all.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- build a 2D cross-section of a uniform shallow-etched grating coupler in MEEP and launch the waveguide's TE mode into it;
- measure where the power goes: up, down into the substrate, on along the waveguide, and back;
- overlap the emitted field with a tilted Gaussian fibre mode, and find the peak wavelength, the peak efficiency and the 1 dB bandwidth;
- sweep the period and the fibre angle, and test the phase-matching condition against the simulation;
- change the buried-oxide thickness and compare the directionality with the thin-sheet model of the chapter's demo;
- check how far the answers still move on a finer grid.

</div>

## What you need

- [Chapter 15]({% link chapters/15_gc.md %}) (Sections 15.1 to 15.5); [Lab 1]({% link labs/lab01_slab.md %}) helps.
- Python with MEEP, NumPy and Matplotlib. On Linux or macOS: `conda install -c conda-forge pymeep matplotlib`. MEEP has no native Windows package: on Windows, run the same command inside WSL (the Windows Subsystem for Linux) or in a Docker container with conda. The lab was tested with MEEP 1.35.1 and Python 3.12 on Linux.
- The script <a href="{{ '/labs/lab06_gc_meep.py' | relative_url }}" download><code>lab06_gc_meep.py</code></a> (also in the repository's [`labs/` folder](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs)).
- About two hours, including the exercises, plus a few minutes of computing.

Run it from a terminal in the folder where you saved it, first on a coarse grid, then in full:

```
python lab06_gc_meep.py --quick
python lab06_gc_meep.py
```

The full run makes six FDTD simulations on a grid of 30 pixels per micrometre. On one core of the test machine it took about 3½ minutes (202 s of CPU time); `--quick` uses 20 pixels per micrometre and took under a minute (40 s of CPU time). MEEP may spread its work over several threads; `OMP_NUM_THREADS=1` holds it to one core, as for these times. Each run prints a checkpoint for each part below, with the chapter's value beside it, and saves the figure `lab06_gc_meep.png`; `--no-plot` skips the figure, and `--resolution 60` runs on any other grid. The checkpoints quote the full run, and Part L6.6 shows how far its numbers are from a converged grid. All lengths are in micrometres, so MEEP's unit of frequency is $$c/(1\ \mu\mathrm{m})$$ and a frequency $$f$$ is the wavelength $$1/f$$.

## <span class="secnum">L6.1</span>The phase-matching estimate

Worked Example 15.1 picks the period from the phase-matching condition, $$n_\mathrm{eff} - \sin\theta_\mathrm{air} = \lambda/\Lambda$$, with the grating's index taken as the fill-factor average of two slab indices: the unetched 220 nm film and the 150 nm film left under the grooves. `slab_te` is the bisection solver of Lab 1, cut down to TE0. `phase_matched_wavelength` turns the condition round, $$\lambda = \Lambda\,[n_\mathrm{eff}(\lambda) - \sin\theta]$$, and lets each slab index fall with wavelength at the rate its group index sets, exactly as the chapter's demo does. The equation has $$\lambda$$ on both sides, so the function iterates it.

MEEP's silicon and oxide have constant indices, so the group index that matters here is that of the waveguide dispersion alone: 3.58 for the 220 nm film and 3.40 for the 150 nm film, the values in the demo. (With silicon's material dispersion the 220 nm film's group index is 3.70, Lab 1.)

The average of two slab indices is not the only plausible estimate. `stack_te` solves a slab made of layers, and the script also tries a 150 nm silicon film under a 70 nm layer whose permittivity is the fill-factor average of silicon and oxide, the layer a weak perturbation would see. The two estimates differ by almost 5 nm in period; the simulation will decide between them.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

The TE slab indices at 1550 nm are 2.848 (220 nm) and 2.539 (150 nm), which average to 2.694 (Worked Example 15.1: 2.848, 2.539 and 2.694). For a fibre at 8° in air the period is 606.8 nm (Chapter 15: 0.607 µm), and the beam leaves the grating at 5.53° in the oxide (Chapter 15: 5.5°). The group indices without material dispersion are 3.58 and 3.40, the demo's values. Averaging the permittivity of the etched layer instead gives $$n_\mathrm{eff} = 2.674$$ and a period of 611.4 nm.

</div>

## <span class="secnum">L6.2</span>The coupler in MEEP

A real coupler's grating is about 12 µm wide, as wide as the fibre's mode, so a cut along the waveguide through its middle is a fair 2D model. In that cut, $$x$$ runs along the waveguide and $$y$$ upwards, and the slab's TE mode has its electric field out of the plane, $$E_z$$, parallel to the grating lines. MEEP calls fields with $$E_z$$ the odd-$$z$$ parity, `mp.ODD_Z`.

`simulate` builds the stack from the bottom: a silicon substrate, 2 µm of buried oxide (BOX), the 220 nm silicon film, and oxide cladding above it (the default material). Thirty grooves, 70 nm deep and half a period wide, are cut into the film from $$x = 0$$; the guide runs on unetched before and after them. An eigenmode source launches the slab's TE0 mode from the left:

```python
    geometry.append(mp.Block(mp.Vector3(2 * sx, T_SI, mp.inf), center=V(cx, T_SI / 2), material=si))
    geometry += [mp.Block(mp.Vector3((1 - ff) * period, etch + 0.1, mp.inf),
                          center=V((i + (1 + ff) / 2) * period, T_SI - etch + (etch + 0.1) / 2), material=cl)
                 for i in range(n_per)]                                                          # the grooves
    ...
    source = mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=2 * df), center=V(X_SRC, (y_lo + y_hi) / 2),
                                size=mp.Vector3(0, y_hi - y_lo), direction=mp.X, eig_band=1, eig_parity=mp.ODD_Z)
```

Why grooves of cladding cut into a full slab, rather than 70 nm silicon teeth standing on a 150 nm slab? MEEP smooths the permittivity of every pixel that an interface crosses (subpixel smoothing), and that is what lets a 70 nm etch, about two pixels deep here, be resolved at all. But where two touching objects of the same material meet inside a pixel, the smoothing mixes in the background material, and leaves a thin low-index seam inside the silicon. The seam comes and goes as the grid shifts. In a first version of this lab, such seams, and an outline of the whole silicon profile as one polygon (`mp.Prism`), both made the peak jump by up to tens of nanometres from one grid to the next. With grooves, every interface MEEP smooths is silicon against cladding. The lesson is general: look at `sim.get_array(component=mp.Dielectric)` before trusting a thin-film FDTD model, and make sure the answer settles as the grid is refined (L6.6).

The cell is about 23 × 5.6 µm (700 × 170 pixels), surrounded by 1 µm of PML, perfectly matched layers that absorb whatever reaches them. The Gaussian pulse covers 1450–1650 nm, and the script records five things against wavelength:

- a **mode monitor** in the input guide, 0.6 µm after the source: `get_eigenmode_coefficients` splits the field there into the forward mode, the input power by which every other power is divided, and the backward mode, the **reflection**;
- the **upward flux** through a line 0.6 µm above the silicon, along the whole grating;
- the **downward flux** through a line in the substrate, 0.2 µm below the BOX: the power lost there;
- the flux that passes **through** the grating along the guide;
- the fields $$E_z$$ and $$H_x$$ along the upward line, for the fibre overlap of L6.3.

The run ends when the field at the end of the grating has fallen to $$10^{-3}$$ of its largest value. Plot (a) of the figure shows the result at 1550 nm: the guided mode fading along the grating, the beam leaving it upwards at a small forward angle, and the standing wave in the BOX between the light going down and its reflection from the substrate.

The **directionality** is the fraction of the emitted power that goes up, up/(up + down), as in Section 15.2. `decay_rate` fits a straight line to $$\ln\lvert E_z\rvert^2$$ along the upward line: the emitted power falls as $$e^{-2\alpha z}$$, so the slope is $$-2\alpha$$, the grating strength of Section 15.3.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

The 607 nm grating, at its peak wavelength: 67.2 % of the input goes up, 31.6 % down, 1.3 % passes the end of the grating and 0.44 % is reflected; together 100.6 %. The directionality is 68.0 % (Chapter 15's thin-sheet model: 62 % on a 2 µm BOX). The grating strength is $$\alpha = 0.125\ \mu\mathrm{m}^{-1}$$, or $$1/\alpha = 8.0$$ µm (Chapter 15: the best uniform grating has $$1/\alpha = 1.46\,w_0 = 7.6$$ µm).

</div>

The powers add up to within 0.6 %, a check on the whole bookkeeping; the excess probably comes from the source, whose mode MEEP computes with a separate mode solver on a slightly different discretisation, so that a little of its light radiates instead of being guided. With $$1/\alpha$$ within 5 % of the optimum, the 70 nm etch at 50 % fill is about as strong as a uniform grating should be.

## <span class="secnum">L6.3</span>Into the fibre

The fibre does not collect all of the upward power, only the part that matches its mode. `fibre_overlap` overlaps the field on the line with a Gaussian beam of waist $$w_0 = 5.2$$ µm (SMF-28's 10.4 µm mode field diameter), centred at $$x_f$$ and tilted by the fibre's angle. The cladding is taken as unbounded above the chip, as if the fibre were index-matched to it, so 8° in air becomes $$\theta_c = 5.53°$$ in the oxide (Snell's law, Section 15.1). On the line, the fibre's mode is

$$e_z(x) = \exp\left[-\frac{(x - x_f)^2\cos^2\theta_c}{w_0^2} + jk_0n_c\sin\theta_c\,(x - x_f)\right], \qquad h_x = n_c\cos\theta_c\,e_z,$$

with $$k_0n_c\sin\theta_c = k_0\sin\theta_\mathrm{air}$$: a beam leaving at the fibre's angle has exactly the phase slope that phase matching gives the grating's emission. The fraction of the power crossing the line that enters the fibre is

$$\eta = \frac{\mathrm{Re}\left[\left(\int E_z h_x^*\,\mathrm{d}x\right)\left(\int e_z H_x^*\,\mathrm{d}x\right) \Big/ \int E_z H_x^*\,\mathrm{d}x\right]}{\mathrm{Re}\int e_z h_x^*\,\mathrm{d}x},$$

where the fibre mode's power in the denominator is integrated over all $$x$$, not just over the line: the fibre's mode extends beyond the end of the line even though the grating's field does not. The **coupling efficiency** is the upward power times $$\eta$$. `coupling` moves the fibre along the grating to where the best wavelength couples most, then holds it there for the whole spectrum, as on a probe station. `peak` fits a parabola through the top 0.5 dB of the spectrum for the peak wavelength and efficiency, and finds where the efficiency is 1 dB down on each side.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

The best fibre position is 4.3 µm from the start of the grating, and 83.4 % of the upward power enters the fibre (Chapter 15: at best about 80 %, with the fibre 3.8 µm from the start). The coupling efficiency peaks at 1559.2 nm at −2.51 dB, or 56.1 % (Chapter 15: 1550 nm by phase matching; −3.0 dB in the thin-sheet budget of Table 15.1). The 1 dB bandwidth is 42.7 nm (Section 15.4: about 42 nm from the fibre's angular acceptance; measured couplers 30–40 nm). The back-reflection into the waveguide is −23.6 dB at the peak and −26.2 dB at 1550 nm, and rises to −4.3 dB at 1622 nm, near the second-order Bragg wavelength $$n_\mathrm{eff}\Lambda = 1635$$ nm.

</div>

Every part of the budget agrees with the chapter's simple models to within a few tenths of a decibel: the directionality is 0.4 dB better than the thin sheet's and the overlap 0.1–0.2 dB better than the exponential's, so the total is 0.5 dB better than Table 15.1's −3.0 dB. Plot (b) shows why the overlap beats the 80 % bound: the beam on the line does not jump to its full strength at the first groove, as an exponential does, but rises over the first micrometre, which a Gaussian matches better. The 1 dB bandwidth is the chapter's 42 nm almost exactly. Measured couplers do worse on all counts (the demo's caption quotes −3 to −5 dB): this is a perfect 2D grating, with no transverse overlap, no fabrication errors, no roughness and an index-matched fibre.

The back-reflection is small at the peak because an 8° fibre keeps the coupler away from the second-order Bragg condition, $$\Lambda = \lambda/n_\mathrm{eff}$$. That condition is met at 1622 nm, where the grating reflects more than a third of the light back into the waveguide: the dip in the 607 nm spectrum of plot (c) and the red dotted curve. Exercise 1 moves that reflection onto the peak.

## <span class="secnum">L6.4</span>Period and angle: phase matching tested

Phase matching predicts how the peak moves. Differentiating $$\lambda = \Lambda(n_\mathrm{eff} - \sin\theta)$$ with $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}\lambda = -(n_g - n_\mathrm{eff})/\lambda$$ gives

$$\frac{\mathrm{d}\lambda}{\mathrm{d}\Lambda} = \frac{(n_\mathrm{eff} - \sin\theta)^2}{n_g - \sin\theta} \approx 1.95,$$

so each nanometre of period moves the peak by about two nanometres. `main` runs two more gratings, 20 nm shorter and 20 nm longer, fits a straight line through the three peaks and solves it for the period that peaks at 1550 nm. The fibre angle needs no new simulation: the field above the grating is already known, so `coupling(run, theta_air=a)` simply overlaps it with a fibre at another angle. Turned round, Section 15.4's $$\mathrm{d}\theta/\mathrm{d}\lambda$$ gives $$\mathrm{d}\lambda/\mathrm{d}\theta = -\lambda\cos\theta/(n_g - \sin\theta) \approx -8$$ nm per degree.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

Periods of 587, 607 and 627 nm peak at 1519.5, 1559.2 and 1597.6 nm (phase-matching estimates 1511.1, 1550.4 and 1589.0 nm), at −2.90, −2.51 and −2.65 dB. The slope is 1.95 nm per nm, the same as phase matching's 1.95. A 1550 nm peak needs a period of 602.5 nm (Worked Example 15.1: 607 nm by the averaged index, and "nearer 630 nm" by a full simulation). The 607 nm grating's peak, 9.2 nm above 1550 nm, corresponds to a grating index $$\lambda/\Lambda + \sin\theta = 2.708$$ against the averaged 2.694. From 4° to 12° the peak moves from 1589.7 to 1526.8 nm, −7.87 nm per degree, against −7.99 nm per degree from Section 15.4.

</div>

Phase matching gets the slopes right: the FDTD peaks follow the averaged-index line of plot (d) at a constant offset. The offset, 9 nm at 30 pixels per µm, is mostly the grid's. Light on an FDTD grid travels slightly too slowly (numerical dispersion), and the smoothing of a groove only two pixels deep is approximate, so every effective index comes out a little high and every peak a little red. Part L6.6 refines the grid: the 607 nm grating's peak falls to 1550.9 nm at 60 pixels per µm and 1550.2 nm at 100, within a nanometre of the averaged-index estimate of 1550.4 nm. Converged, the period for 1550 nm is therefore 607 nm to within a nanometre, and the permittivity-averaged estimate of Checkpoint A (611 nm) is the worse of the two.

This does not bear out Worked Example 15.1's remark that a full simulation of the same grating puts the period nearer 630 nm. In this 2D simulation a 630 nm period would put the oxide-clad grating's peak near 1595 nm, 45 nm too far. Air above the grating and a steeper fibre both lengthen the period towards 630 nm (Exercise 2). What the averaged index cannot give, the simulation does: the efficiency, the bandwidth, the reflection, and how sensitive they all are to the BOX.

## <span class="secnum">L6.5</span>The buried oxide

In Section 15.2's thin-sheet model the directionality swings with the BOX thickness $$t$$, with a period $$\lambda/(2n_\mathrm{ox}\cos\theta_\mathrm{ox}) = 0.539$$ µm, because the light reflected from the substrate returns in or out of phase with the light emitted upwards. `main` reruns the 607 nm grating with the BOX a quarter of that period thinner, and one and two quarters thicker (1.730, 1.865, 2.000 and 2.135 µm), and `fit_box` fits a sinusoid with the chapter's period through the four directionalities at 1550 nm. Four points a quarter-period apart fix the mean, the swing and the phase of the sinusoid.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint E</div>

At 1550 nm the directionality is 40.7, 66.7, 67.7 and 40.2 % for BOX thicknesses of 1.730, 1.865, 2.000 and 2.135 µm (thin-sheet model: 54, 70, 62 and 31 %), and the coupling into the fibre is −5.98, −3.14, −2.70 and −5.42 dB. The fitted sinusoid swings between 35 and 73 % and peaks at 1.93 and 2.47 µm (thin-sheet model: 29–71 %, best at 1.89 and 2.43 µm).

</div>

The thin sheet is a good model of a real grating's directionality: the FDTD swings almost as far, with the same period, shifted by 40 nm of BOX. Most likely the shift is the phase that a sheet of zero thickness leaves out: the light emitted downwards leaves from the grooves and teeth, not from one plane, and crosses the 150–220 nm of silicon before it enters the BOX. The swing is a little smaller because the grating itself sends somewhat more light up than down; a grating whose teeth sit on top of the film is not symmetric.

The lesson of Section 15.2 is sharper in the simulation than in the model. A BOX 135 nm thicker than 2 µm, a quarter of the period, costs 2.7 dB at 1550 nm, and one 270 nm thinner 3.3 dB. The usual 2 µm BOX happens to sit near a maximum for this grating at 1550 nm; a coupler moved to another wafer stack has to be redesigned, or it can lose several decibels.

## <span class="secnum">L6.6</span>How fine a grid?

An FDTD answer is only as good as its grid. `python lab06_gc_meep.py --resolution 60` reruns the whole lab on a finer grid; the table below runs just the 607 nm grating of Checkpoints B and C, on grids from 20 to 100 pixels per micrometre.

**Table L6.1. Grid convergence for the 607 nm grating on a 2 µm BOX.** One simulation per grid; the CPU times, for one core of the test machine, are approximate.
{: .tabcaption #tab-l6-1 }

| Pixels per µm | Peak (nm) | Into the fibre (dB) | 1 dB bandwidth (nm) | Directionality | Overlap | CPU time |
|---|---|---|---|---|---|---|
| 20 (`--quick`) | 1574.2 | −2.35 | 39.9 | 70.6 % | 83.4 % | 4 s |
| 30 (default) | 1559.2 | −2.51 | 42.7 | 68.0 % | 83.4 % | 25 s |
| 40 | 1556.8 | −2.58 | 42.5 | 67.1 % | 83.5 % | 53 s |
| 50 | 1553.7 | −2.64 | 42.9 | 66.5 % | 83.6 % | 2 min |
| 60 | 1550.9 | −2.68 | 43.1 | 65.9 % | 83.5 % | 2½ min |
| 80 | 1550.6 | −2.68 | 43.1 | 65.9 % | 83.5 % | 5 min |
| 100 | 1550.2 | −2.68 | 43.0 | 65.9 % | 83.5 % | 10 min |

The default grid puts the peak 9 nm too far to the red and the efficiency 0.17 dB too high; the overlap and the bandwidth have converged already. From 60 pixels per µm on, the peak moves by less than a nanometre and the efficiency by less than 0.01 dB. The cost grows as the cube of the resolution: twice as many pixels in each of two directions, and a time step half as long. That is why the default is coarse: every comparison in this lab is between runs on the same grid, and their offsets largely cancel. The slope of the peak against the period, for instance, comes out at phase matching's 1.95 even on the default grid.

The quick grid, with under one and a half pixels across the etch, is a smoke test: it runs everything in under a minute and gets the trends right, but its peak is 24 nm off.

<figure id="fig-l6-1">
  <img src="{{ '/assets/figs/lab06_expected.png' | relative_url }}" style="width:760px" alt="Five plots from the lab script: the field amplitude over the cross-section of the grating coupler at 1550 nm; the field along the overlap line against the fibre's Gaussian mode; coupling-efficiency spectra for three periods with the back-reflection; peak wavelength against period from FDTD and from phase matching; and directionality against buried-oxide thickness from FDTD and from the thin-sheet model">
  <figcaption><span class="capnum">Figure L6.1.</span> <strong>What the script draws</strong> (30 pixels per µm). (a) \(\lvert E_z\rvert\) at 1550 nm for the 607 nm grating: the guided mode fades along the grating as the beam leaves upwards; below, the standing wave in the BOX. (b) The intensity on the overlap line at the peak wavelength against the fibre's mode, each with unit area. (c) Coupling into the fibre for three periods; the dashed line is 1 dB below the 607 nm peak, and the red dotted curve is the reflection, highest near the second-order Bragg wavelength. (d) Peak wavelength against period: FDTD (dots) and phase matching with the averaged index (line), with the same slope. (e) Directionality at 1550 nm against BOX thickness: FDTD, a fitted sinusoid, and the thin-sheet model of the chapter's demo.</figcaption>
</figure>

## Exercises

Each exercise needs one more run of `simulate`, under a minute at the default 30 pixels per µm: import the script (`import lab06_gc_meep as gc`) and call its functions. The answers quote that grid, so expect peaks about 9 nm to the red of a converged grid (L6.6).

1. **Straight up.** Phase matching for a vertical fibre needs $$\Lambda = \lambda/n_\mathrm{eff} = 575$$ nm. Run `simulate(0.575)` and `coupling(run, theta_air=0)`. What are the peak efficiency, the bandwidth and the back-reflection at the peak? Compare them with the 8° design and explain with Section 15.1.
2. **Where do 630 nm periods come from?** Many early shallow-etched couplers had no top oxide: air above the grating, and a fibre tilted by about 10°. Run `simulate(0.63, clad=1.0)` and `coupling(run, theta_air=10)`. Where is the peak? What period does the averaged-index estimate give for an air-clad grating (`slab_te(d, n3=1.0)`) at 10°, and at 8°?
3. **A bottom mirror.** `simulate(0.607, mirror=True)` puts a perfect metal under the 2 µm BOX. What happens to the directionality, the grating strength and the coupling into the fibre? Compare with the bottom-mirror row of Table 15.1.
4. **A deeper etch.** Etch 120 nm instead of 70 (`etch=0.12`). The 100 nm film's TE index is 2.189, so the averaged-index period is 651 nm. Find the grating strength, the best fibre position, the overlap, the peak efficiency, the bandwidth and the reflection, and explain each change.
5. **A shorter grating.** With 15 periods instead of 30 (`n_per=15`), how much light passes the end of the grating unused, and what does that cost at the peak?

<details markdown="1">
<summary>Answers</summary>

1. The vertical coupler peaks at 1558.6 nm at −3.95 dB, with a 1 dB bandwidth of only 21.4 nm, and reflects −4.4 dB, 36 % of the light, back into the waveguide at its peak (the 8° design: −2.51 dB, 42.7 nm and −23.6 dB). Only 32.7 % of the light goes up. At $$\Lambda = \lambda/n_\mathrm{eff}$$ the first diffraction order leaves vertically and the second order couples the forward mode into the backward one: the second-order Bragg reflection of Section 15.1, here at 1549 nm, right on the peak. Its stop-band cuts into the spectrum, which is why the band is narrow, and the overlap with the fibre falls to 57 %, partly because the reflected light also emits straight up, with its own profile. The same grating with an 8° fibre peaks at 1495.5 nm (−3.48 dB, −24.1 dB of reflection), clear of the Bragg reflection.
2. With air above, the slab indices fall to 2.831 and 2.505 (average 2.668), and the averaged-index period is 621.4 nm at 10° and 613.0 nm at 8°. The 630 nm air-clad grating peaks at 1577.6 nm with a 10° fibre (−2.92 dB, 43.1 nm) and at 1592.7 nm with an 8° fibre. Allowing for the grid's 9 nm, a 630 nm air-clad grating at 10° peaks near 1568 nm; air cladding and a steeper fibre both lengthen the period, which is where periods near 630 nm come from. The directionality falls to 60 %: with air above, the grating radiates relatively more into the denser oxide below.
3. Nothing is lost into the substrate any more: the directionality is 100 % and 98.7 % of the light goes up, so the coupling rises to −0.81 dB at 1562.6 nm (−1.09 dB at 1550 nm). What remains is the overlap, 83.8 % (−0.77 dB): a uniform grating still emits a non-Gaussian beam. The mirror also changes the grating: the light returning from it interferes with the grating's own emission, and the grating strength rises from 0.125 to 0.174 µm⁻¹. The 1 dB bandwidth widens to 50.1 nm. Table 15.1's bottom-mirror row reaches −0.22 dB because it is apodised as well; apodisation and a mirror together are what the best couplers use.
4. The grating strength nearly doubles, to 0.234 µm⁻¹ ($$1/\alpha = 4.3$$ µm), so the light leaves in a shorter beam: the fibre moves in to 3.2 µm from the start and the overlap falls to 79.5 %. The peak is at 1567.9 nm (the averaged-index estimate does worse for a deeper etch) at −3.12 dB, the directionality is 63.6 %, and the reflection rises to −15.2 dB at the peak, since every tooth now reflects more. The 1 dB bandwidth widens to 52.2 nm. Partly the grating's group index is lower, 3.30 averaged instead of 3.49, so the beam swings less with wavelength; mostly the shorter beam has a wider angular spread, so the fibre tolerates more swing. A strong grating trades efficiency for bandwidth.
5. 12.0 % of the light passes the end of the 9.1 µm grating unused ($$e^{-2\alpha L} = 0.10$$ for $$\alpha = 0.125$$), and the peak efficiency falls from −2.51 to −2.90 dB, at 1557.5 nm. The overlap of what is emitted rises slightly, to 86.0 %, and the 1 dB bandwidth widens to 49.1 nm, both because the truncated beam is shorter. Table 15.1's "too weak" row makes the same point: the grating must be long enough to emit nearly everything, about $$2/\alpha$$ or more.

</details>

## Going further

- **Apodise.** Give each groove its own width, so that the grating strength grows along the grating as Section 15.3 prescribes, $$\alpha(z) = G(z)/(2[1 - \int_0^z G\,\mathrm{d}z'])$$. The overlap should climb from 83 % towards 95 %; the period must follow the local fill factor to stay phase-matched.
- **The other polarisation.** With `eig_parity=mp.EVEN_Z` the slab's TM mode ($$H_z$$, with $$E_x$$ and $$E_y$$) is launched instead, and the overlap uses $$H_z$$ and $$E_x$$. Find where this grating couples TM light, and how weakly it does at 1550 nm (Section 15.4).
- **Inverse design.** MEEP's adjoint solver (`meep.adjoint`) computes the gradient of the coupling efficiency with respect to every groove at once, so all of them can be optimised together; its documentation has worked examples.
- **From a layout.** The gplugins package of gdsfactory sets up MEEP grating-coupler simulations like this one from a layout; [Lab 7]({% link labs/lab07_layout.md %}) lays out a chip with the PDK's own couplers.
- [Lab 9]({% link labs/lab09_analysis.md %}) analyses measured openEBL spectra: compare a grating-coupler loopback's peak, 1 dB bandwidth and fringes with this lab's.
