---
title: "29. Design Principles and Simulation Workflows"
parent: "Part VII · Design, Simulation and Layout"
nav_order: 29
permalink: /part-7/ch29/
chapter: 29
---

# <span class="chapnum">Chapter 29</span>Design Principles and Simulation Workflows

A design is not finished when it works in one simulation. It is finished when it meets its specification on most of the dies, at every temperature it will see, and you can show why.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- flow a system specification down to component targets and tolerances, and keep budgets with visible margin;
- choose architectures and design points that tolerate fabrication variation;
- pick the cheapest model that answers each question, and estimate what a simulation will cost before you run it;
- treat every simulation as an experiment: test convergence, sweep parameters and compute sensitivities;
- predict yield with corners and Monte Carlo, and outline optimisation and inverse design;
- build compact models, know where they are valid, and close the loop with measurements;
- keep simulation work reproducible, and design for manufacturing and for test.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you get from a system specification to a design that works on most of the dies, with the least simulation?

</div>

## <span class="secnum">29.1</span>From specification to component targets

Experienced designers rarely start with a simulator. They start with the specification and work out what each block must do, long before choosing a geometry. Systems engineering draws this as a **V** ([Figure 29.1](#fig-29-1)). Going down the left arm, the system specification is divided among blocks as budgets, each block's share becomes targets for its components, and each target becomes device parameters: widths, gaps, lengths, doping. At the bottom, simulation finds a design point. Going up the right arm, each level is checked against the specification of its own level: the device against its targets, the circuit against the block's budget, the chip against the system. [Chapter 30]({% link chapters/30_flow.md %}) shows the same flow from the side of the tools; this chapter is about the decisions.

<figure id="fig-29-1">
  <img src="{{ '/assets/figs/ch29_workflow.svg' | relative_url }}" style="width:700px" alt="A V-shaped diagram. Left arm, top to bottom, shaded blue: system specification (Table 1.3: rate, reach, BER, margin, energy per bit); architecture and budgets; component targets (FSR, coupling window, Q, extinction, insertion loss); device design (cheapest model first: formula, mode solver, EME, 2.5D FDTD). At the bottom, a design point reached by a loop of converge, sweep, sensitivities, corners and Monte Carlo. Right arm, bottom to top, shaded green: device verified (full-wave check, corners and Monte Carlo); circuit verified (compact models with their variation); layout verified (DRC, connectivity, test structures, Chapters 33 and 34); chip measured (test and analysis, Chapters 36 and 37), shaded cream. Dashed arrows run from each right-arm box back to the left-arm box at the same level, asking whether it meets the spec at that level. A red line runs from chip measured down to circuit verified: measured bias, indices and losses update the models.">
  <figcaption><span class="capnum">Figure 29.1.</span> <strong>The design-and-simulation workflow as a V.</strong> The specification is broken down level by level (left), a design point is found by simulation (bottom), and each level is verified against its own specification on the way up (right, dashed arrows). Measurements of the fabricated chip update the models used for the next design (red). The loop at the bottom is the subject of Sections 29.4 and 29.5. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

**Budgets.** A budget divides one system quantity among the blocks and keeps part of it in reserve. The reference link of [Chapter 1]({% link chapters/01_why.md %}) has four: optical power (Worked Example 1.1 spends 12.7 dB of loss and keeps 9.3 dB of margin before penalties), wavelength (each ring must be tunable over the thermal drift plus the fabrication spread), energy (5 pJ/bit, or 1 W for 200 Gb/s), and crosstalk. Three habits make budgets useful. Every entry has an owner and a source: an estimate, a simulation or a measurement, and estimates are replaced as the design matures, as [Chapter 38]({% link chapters/38_links.md %}) does when it closes the link with 5.9 dB of margin. Margin is held in one visible place, not hidden in every block. And every number is either a nominal value or a worst case, never an unlabelled mixture of the two.

**Flow-down.** [Figure 29.2](#fig-29-2) follows three of the reference link's targets down to device parameters. The demultiplexer's crosstalk target becomes a range of coupling for its rings, and that range becomes a gap and a coupling length; the ring modulator's extinction and loss become a resonance shift per volt and two quality factors; the temperature range becomes a heater range. Each arrow is one equation from an earlier chapter, and the next worked example walks down one branch.

<figure id="fig-29-2">
  <img src="{{ '/assets/figs/ch29_flowdown.svg' | relative_url }}" style="width:700px" alt="A tree with four levels labelled system, block, component and device. Top: the reference link, 4 by 50 Gb/s NRZ over 2 km, BER below 10 to the minus 12, margin at least 3 dB, at most 5 pJ per bit, 20 to 70 degrees Celsius. Blocks: demultiplexer (crosstalk at most minus 20 dB, drop loss at most 1 dB, four channels 3.2 nm apart), ring modulator (extinction at least 4 dB at 2 Vpp, insertion loss at most 3 dB), thermal control (rings on channel from 20 to 70 degrees, inside the energy budget). Components: free spectral range 4 times 3.2 = 12.8 nm; coupling per coupler kappa squared between 9.3 and 13.1 percent; tuning about 50 pm per volt with Q_i 15 000 and Q_L 8000; tuning range of 3.75 nm of drift plus the fabrication spread. Devices: ring length 44.9 micrometres (radius 7.15) for group index 4.18; coupler with 200 nm gap and 8.2 micrometre effective length; a lateral junction made L- or U-shaped; a TiN heater at 0.26 nm per mW whose range is set by the locking scheme. Each box names the chapter or example that sets it.">
  <figcaption><span class="capnum">Figure 29.2.</span> <strong>Flowing the reference link's targets down to devices.</strong> Each level turns the targets above it into targets for the level below, with one equation each: the channel plan sets the free spectral range and so the ring length ([Chapter 14]({% link chapters/14_wdm.md %})); crosstalk and passband set the coupling window (Worked Example 29.1); extinction and loss set the modulator's tuning efficiency and quality factors ([Chapter 20]({% link chapters/20_modulators.md %})); the temperature range, the fabrication spread and the locking scheme set the heater ([Chapter 18]({% link chapters/18_thermal.md %}), Worked Example 29.3). Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 29.1 · From a crosstalk target to a coupling window</div>

**Ring length.** Four channels 3.2 nm apart and a cyclic demultiplexer need an FSR of 12.8 nm, so $$L = \lambda^2/(n_g\,\mathrm{FSR}) = 44.9$$ µm with $$n_g = 4.18$$ ([Chapter 14]({% link chapters/14_wdm.md %})).

**Upper limit.** In the drop port of a symmetric add-drop ring with 2 dB/cm of loss ([Chapter 12]({% link chapters/12_rings.md %})), a neighbouring channel a quarter of an FSR away is suppressed by −20 dB when the power coupling of each coupler is $$\kappa^2 = 13.1$$ %. More coupling widens the resonance and lets more of the neighbour through. (Chapter 14's Lorentzian estimate, 14.5 %, comes out at −19.1 dB in this periodic model.)

**Lower limit.** A 50 Gb/s NRZ signal occupies about 0.4 nm. Asking for a passband (FWHM) no narrower than that gives $$\kappa^2 \ge 9.3$$ %.

**The window and its centre.** The coupling must lie between 9.3 and 13.1 %, and the design should sit in the middle: 11.0 %, the geometric mean, which leaves the same factor of 1.19 to each limit. There the crosstalk is −21.6 dB, the passband 0.48 nm and the drop loss 0.08 dB, well inside the 1 dB target.

**The device.** With the cross-over length $$L_x = 37.85$$ µm of a 200 nm gap ([Chapter 9]({% link chapters/09_couplers.md %})), $$\kappa^2 = \sin^2(\pi L_c/2L_x) = 0.110$$ needs an effective coupling length $$L_c = 8.2$$ µm: 5.7 µm of straight coupler plus the 2.5 µm that the bends add.

**The tolerance.** Near this point $$\mathrm{d}\ln\kappa^2/\mathrm{d}\ln L_x = -1.92$$, and $$L_x$$ grows by 0.89 % per nanometre of gap (Section 29.4). The window, a factor of 1.19 either way, therefore allows ±10 nm of gap error, or ±13 nm of thickness error, if each acted alone. A target has become a geometry with a tolerance, and the tolerance is generous: this coupler is not where the demultiplexer will fail.

</div>

## <span class="secnum">29.2</span>Architecture and margins

Most of a design's robustness is decided before any simulation, by the choice of architecture. A demultiplexer of rings is the smallest option, but every ring is resonant and moves by 0.6 nm per nanometre of width error ([Chapter 6]({% link chapters/06_soi.md %})), so it needs a heater and a control loop; an MZI lattice or an AWG is larger but has no single resonance to lose ([Chapter 14]({% link chapters/14_wdm.md %})). A ring modulator is small and efficient but must be held on its laser line; a Mach–Zehnder modulator is larger and needs more drive power but tolerates far more ([Chapter 20]({% link chapters/20_modulators.md %})). Against variation, a designer has three choices for each parameter: make the device **tolerant** of it (wide waveguides, adiabatic or bias-tolerant couplers, Section 29.4), make it **tunable** (heaters and locking loops), or make the system **adapt** around it (assigning channels to whichever ring is nearest, Worked Example 29.3). The control strategy is part of the architecture.

**Margin** is the distance between the nominal performance and the specification limit, and it only means something when compared with the spread of the performance. If a performance $$y$$ varies from die to die with mean $$\mu$$ and standard deviation $$\sigma$$, roughly as a Gaussian, the fraction of dies inside the limits $$L$$ and $$U$$ is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Yield of a Gaussian performance between two limits</div>

$$Y = \Phi\!\left(\frac{U - \mu}{\sigma}\right) - \Phi\!\left(\frac{L - \mu}{\sigma}\right),\qquad \Phi(z) = \tfrac{1}{2}\left[1 + \mathrm{erf}\!\left(z/\sqrt{2}\right)\right]$$

</div>

A design centred in a window of half-width $$k\sigma$$ passes $$2\Phi(k) - 1$$ of the dies: 68.3 % for $$k = 1$$, 95.4 % for $$k = 2$$ and 99.73 % for $$k = 3$$. Two consequences follow. **Design centring**: for a given spread, the best nominal is the middle of the window, not the edge that a nominal optimisation drifts towards; Worked Example 29.1 put the coupling at the geometric middle because the coupling spreads by a factor, not by an amount. **Margin in sigmas**: a nominal 1 dB from the limit is generous if the spread is 0.1 dB and useless if it is 1 dB, so margins are quoted against the spread, which only Section 29.5's statistics can give.

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Margin stacking</div>

If every block designer adds a private safety margin, and every tolerance is combined at its worst case, the system ends up with far more margin than it needs, paid for in laser power, heater power or area. Hold margin openly at the level where it is spent (the link budget), combine independent variations statistically (Section 29.5), and label every number as nominal or worst case.

</div>

## <span class="secnum">29.3</span>Choosing the level of model

Photonic models form a ladder, from fast and narrow to slow and general ([Figure 29.3](#fig-29-3)); [Chapter 31]({% link chapters/31_simulators.md %}) explains how each works and [Chapter 32]({% link chapters/32_simtools.md %}) how to run them.

- **Closed-form formulas**: coupled-mode theory, the ring and Fabry–Pérot formulas, link budgets. They take microseconds and are exact only for idealised geometry, but they show trends, set budgets and check every other model.
- **Mode solvers** (finite-difference or finite-element eigenmode, FDE/FEM) find the modes of one cross-section in seconds to a minute: effective and group indices, supermodes, overlaps. They assume the structure does not change along its length.
- **Eigenmode expansion** (EME) cuts a device into sections of constant cross-section and joins their modes. It suits long, slowly varying devices (tapers, couplers, MMIs), and a length sweep costs almost nothing once the sections are solved; it is limited by the number of modes kept.
- **2.5D (variational) FDTD** collapses the vertical direction into an effective index and runs FDTD in the plane of the chip. It handles any in-plane shape in minutes, but misses radiation out of the plane and into the substrate.
- **3D FDTD** solves Maxwell's equations on a grid in time with almost no assumptions: gratings, reflections, scattering. For a device tens of micrometres long it costs days of processor time and tens of gigabytes.
- **Compact models** reduce each device to its S-matrix against wavelength, so a circuit simulator can evaluate thousands of devices in milliseconds ([Chapter 30]({% link chapters/30_flow.md %})). They are only as accurate as what they were fitted to, and only within the range they were fitted over (Section 29.7).

<figure id="fig-29-3">
  <img src="{{ '/assets/figs/ch29_costmap.svg' | relative_url }}" style="width:720px" alt="(a) Six rows, from bottom to top: formula, compact model, mode solver, EME, 2.5D FDTD and 3D FDTD, with an arrow pointing up labelled fewer assumptions, against a logarithmic time axis from 100 nanoseconds to 10 million seconds with marks at one second, one minute, one hour and one day. Each row has a dot at the time of one evaluation of the ring coupler on one core: a fraction of a microsecond for the formula, about 10 microseconds for the compact model, 5.7 seconds for the mode solver, 8.8 minutes for EME, 1.8 minutes for 2.5D FDTD and 1.6 days for 3D FDTD, each with what it assumes in grey italics. (b) Bars on a logarithmic time axis for one design, a 20-gap sweep and a 1000-die Monte Carlo, for mode solver plus coupled-mode theory, EME and 3D FDTD: the Monte Carlo takes about two minutes with the mode solver, six days with EME and about four years with 3D FDTD.">
  <figcaption><span class="capnum">Figure 29.3.</span> <strong>What each level of model costs</strong>, for the ring coupler of Worked Example 29.1. (a) Time for one evaluation on one CPU core, rising by nearly twelve orders of magnitude from a formula to 3D FDTD, against what each level assumes (grey italics). The mode-solver and EME times are measured femwell solves; the FDTD times are estimates from the speed and memory per cell measured with MEEP (Worked Example 29.2); the compact model is the ring's drop port at 1000 wavelengths. The formula and the compact model are timed as Python calls. (b) The same costs for three design tasks: a cheap model built from 19 mode solves does a Monte Carlo of 1000 dies in about two minutes, while 3D FDTD would need about four years on one core. Timings on one core of a desktop workstation, good to a factor of two or so. Drawn by <code>figsrc/ch29_figs.py</code> from <code>figsrc/ch29_sims.py</code> (femwell, MEEP).</figcaption>
</figure>

The rule is to use the cheapest model that answers the question, then to verify the final design once with a model that makes fewer assumptions. A cheap model checked against an expensive one at a few points can be trusted for the thousands of evaluations that sweeps and Monte Carlo need; an expensive model run without such a plan answers one question slowly.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 29.2 · Which solver for the ring's coupler?</div>

Take the coupler of Worked Example 29.1, with S-bends like those of [Figure 9.3]({% link chapters/09_couplers.md %}#fig-9-3): 31.7 µm long and 5.2 µm wide.

**Mode solver and coupled-mode theory.** One femwell supermode solve on a 2771-node mesh takes about 6 s on one core; after that, $$\kappa^2$$ for any length is a formula. The Monte Carlo model of Section 29.5 needs 19 solves: about 2 minutes.

**EME.** Cutting each S-bend into 20 sections gives 41 cross-sections, each needing about 12 modes (13 s with femwell): about 9 minutes, after which the straight length can be swept for free.

**3D FDTD.** With 1 µm of padding and 1 µm of absorbing layer around the device, the domain is 35.7 × 9.2 × 4.2 µm. A 20 nm grid (about 22 cells per wavelength in silicon) has 1783 × 460 × 211 = 1.7 × 10⁸ cells; at 171 bytes per cell, MEEP's measured figure, that is 30 GB. The time step is limited by the Courant condition; at MEEP's default $$\Delta t = 0.5\,\Delta x/c = 0.033$$ fs, a run long enough for light to cross the domain twice and the source pulse to pass, 1.25 ps, is 37 000 steps, or 6.5 × 10¹² cell updates. At the 4.8 × 10⁷ updates per second measured on one core, that is 37 hours, or about 3 hours on 12 cores if the speed scaled perfectly. Halving the cell size multiplies the cost by 16: eight times the cells and twice the steps ([Chapter 31]({% link chapters/31_simulators.md %})).

**Verdict.** Design and Monte Carlo with the mode solver and coupled-mode theory; check the bends' contribution with EME (9 minutes) or 2.5D FDTD (2 minutes); run 3D FDTD once, on the final geometry, as the verification of [Figure 29.1](#fig-29-1)'s right arm.

</div>

## <span class="secnum">29.4</span>Simulations are experiments

Every simulated number is a measurement with an error bar, set by the grid, the size of the computational window, the run time, the number of modes and the material data. Experienced designers make **convergence testing** a habit: refine each numerical parameter until the quantity they need changes by much less than the tolerance they care about, and record the value they settled on. Three rules help.

- **Converge the quantity you need, not a proxy.** A coupler depends on $$n_\mathrm{even} - n_\mathrm{odd}$$, which is 0.8 % of either index, so it needs a hundred times the relative accuracy of $$n_\mathrm{eff}$$ itself.
- **Small differences of two simulations are noisy.** A sensitivity computed by re-meshing two geometries inherits the meshing noise of both. Use a step large enough for the change to dominate the noise, keep the mesh the same between the two runs, or use perturbation or adjoint methods (Section 29.6).
- **Check the window and boundaries too**, not only the grid: modes that touch the window edge, absorbing layers too close to the device, an FDTD run stopped before the fields decay.

[Figure 29.4](#fig-29-4) shows the habit for the coupler. Refining the femwell mesh from 80 to 10 nm raises $$L_x$$ by 0.9 %; below about 45 nm it approaches its limit roughly as the first power of the mesh size, and at the 25 nm used in [Chapter 9]({% link chapters/09_couplers.md %}) it is 0.16 % below the extrapolated value. That is a 0.3 % error in $$\kappa^2$$, negligible against the window of Worked Example 29.1 (−16 to +19 %): converged enough means converged relative to the tolerance. Enlarging the window from 3 × 2 µm to 10 × 6 µm changes it by only 0.03 %. Its sensitivity to a width bias, a small difference of two solves, scatters by up to 13 % between coarse meshes and settles to −0.067 %/nm only when the mesh is fine.

<figure id="fig-29-4">
  <img src="{{ '/assets/figs/ch29_convergence.svg' | relative_url }}" style="width:640px" alt="(a) Cross-over length against mesh size from 80 down to 10 nm (axis reversed), rising from 37.54 to 37.89 micrometres; the five finest points follow a dashed fitted curve towards an extrapolated 37.91 micrometres, shown with a band of plus or minus 0.1 percent; three points are labelled 1286, 2771 and 7583 nodes. (b) The sensitivity of ln L_x to a width bias against mesh size: minus 0.062 at 80 nm and minus 0.076 at 60 nm, then between minus 0.065 and minus 0.068 percent per nm for finer meshes, with a band showing minus 0.067 plus or minus 0.001 for the finest four.">
  <figcaption><span class="capnum">Figure 29.4.</span> <strong>Convergence as a habit</strong>: femwell supermodes of two 500 × 220 nm strips with a 200 nm gap at 1550 nm (TE), against the element size at the cores. (a) The cross-over length converges smoothly from below; the dashed line is a fit \(L_\infty - Ch^p\) with \(p\) = 1.1, fitted to the five finest meshes; three mesh sizes are labelled with their number of nodes. (b) The sensitivity of \(\ln L_x\) to a width bias (both strips 5 nm wider, the gap 5 nm narrower, and the reverse) is a small difference of two solves on two different meshes: it scatters at coarse meshes and only settles, to within ±0.001 %/nm, below about 25 nm. Drawn by <code>figsrc/ch29_figs.py</code> from <code>figsrc/ch29_sims.py</code> (femwell).</figcaption>
</figure>

**Sweeps.** One parameter at a time is the way to learn how a device behaves. A full grid over $$d$$ parameters with $$n$$ points each costs $$n^d$$ runs, so for more than two or three parameters designers use a coarse grid or a planned set of points, fit a smooth response surface, and refine near the design point. Sweep the design parameters (the gap) and the process parameters (the thickness) together: the design point should be one where the process parameters matter least.

**Sensitivities.** The central difference $$\partial y/\partial x \approx [y(x + h) - y(x - h)]/2h$$ turns a sweep into a sensitivity, and the tolerance analysis of Worked Example 29.1 is built from them. For the ring coupler at 1550 nm, femwell gives:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Sensitivities of the coupler (500 × 220 nm strips, 200 nm gap)</div>

$$\frac{\partial\ln L_x}{\partial W} = +0.83\ \frac{\%}{\mathrm{nm}},\quad \frac{\partial\ln L_x}{\partial g} = +0.89\ \frac{\%}{\mathrm{nm}},\quad \frac{\partial\ln L_x}{\partial t} = +0.70\ \frac{\%}{\mathrm{nm}},\quad \frac{\partial\ln L_x}{\partial\lambda} = -0.43\ \frac{\%}{\mathrm{nm}}$$

</div>

For the ring itself, [Chapter 6]({% link chapters/06_soi.md %})'s femwell values, $$\partial n_\mathrm{eff}/\partial W = 1.58\times10^{-3}$$ and $$\partial n_\mathrm{eff}/\partial t = 3.7\times10^{-3}$$ per nanometre, move the resonance by $$\lambda\,\partial n_\mathrm{eff}/n_g$$: 0.59 nm per nanometre of width and 1.37 nm per nanometre of thickness, the 0.6 and 1.4 that [Chapter 35]({% link chapters/35_fab.md %}) and this chapter's Monte Carlo use in round numbers.

Sensitivities reveal tolerant designs. A lithography bias does not change the width alone: both strips grow by the same amount as the gap between them shrinks, because their centres stay where they were drawn. A wider strip confines its mode more and couples less; a narrower gap couples more. At 500 nm the two effects nearly cancel, leaving only −0.07 %/nm, and they cancel exactly at 482 nm ([Figure 29.5](#fig-29-5)b). Rib-waveguide couplers designed this way against width, height, gap and etch-depth variations at once have shown up to four times less spread of coupling across a wafer than strip couplers {% include cite.html keys="mikkelsen2014" %}. The thickness, which layout cannot compensate, is then the variation that matters ([Figure 29.5](#fig-29-5)a).

<figure id="fig-29-5">
  <img src="{{ '/assets/figs/ch29_sensitivity.svg' | relative_url }}" style="width:640px" alt="(a) Tornado chart of the change of kappa squared in percent, with bars for the low and high end of each variable: width alone plus or minus 7.5 nm with the gap held, about plus 13 and minus 11 percent; gap alone plus or minus 5 nm, about plus 9 and minus 8; thickness plus or minus 3 nm, about plus and minus 4; channel from 1546 to 1556 nm, about plus and minus 4; width bias plus or minus 7.5 nm, about plus and minus 1. Dashed red lines mark the window at minus 16 and plus 19 percent. (b) Sensitivity of ln L_x per nanometre against strip width from 350 to 650 nm at a 200 nm gap: width alone falls from 1.3 to 0.57 percent per nm, gap alone rises from 0.68 to 0.97, and the width bias, their difference, falls from plus 0.62 to minus 0.41 and crosses zero at 482 nm, marked bias-tolerant.">
  <figcaption><span class="capnum">Figure 29.5.</span> <strong>Sensitivity and tolerance of the ring coupler.</strong> (a) Tornado chart: the change of \(\kappa^2\) from its centred value of 11.0 % when one variable moves to the low (blue) or high (red) end of its range, from the femwell model; red dashed lines, the window of Worked Example 29.1. A width error with the gap held, or a gap error on its own, would use much of the window; a lithography bias, which narrows the gap as it widens the strips, hardly moves it. Of the variations that really occur, the thickness and the systematic change across the four channels are the largest. (b) The sensitivity of \(\ln L_x\) to width alone, gap alone and a width bias, against the strip width at a 200 nm gap: the bias term changes sign at 482 nm, a bias-tolerant coupler. Drawn by <code>figsrc/ch29_figs.py</code> from <code>figsrc/ch29_sims.py</code> (femwell).</figcaption>
</figure>

## <span class="secnum">29.5</span>Corners, Monte Carlo and yield

**Corners.** The simplest variation analysis simulates the design at combinations of the extremes, the **process corners**: thick and wide, thin and narrow, and so on, $$2^d$$ runs for $$d$$ variables, at the extremes of temperature too. Corners are cheap and bound any response that changes monotonically with each variable. They have two weaknesses. They say nothing about responses with an optimum inside the range (a ring's extinction peaks at critical coupling, [Chapter 12]({% link chapters/12_rings.md %})). And they stack every variable at its extreme at once, which for independent variables is pessimistic: the chance that all of them sit at three sigma together is tiny. For the ring resonance on the wafers of [Chapter 35]({% link chapters/35_fab.md %}), with standard deviations of 2.1 nm in width and 1.4 nm in thickness, stacking three-sigma corners gives ±9.8 nm, while independent variations would spread by only ±7.1 nm (three sigma, added in quadrature). On those wafers, though, the two are correlated (coefficient 0.66), because the thickness and the width vary across the wafer in the same bowl, and the true three-sigma spread is ±9.0 nm, close to the corners. Know the correlations before choosing between corners and statistics.

**Monte Carlo.** Instead of extremes, draw many dies from the process statistics, with their wafer-scale, die-to-die and within-die parts and their correlations, evaluate a fast model for each, and count those that meet the specification. The yield $$Y$$ estimated from $$N$$ dies has a standard error $$\sqrt{Y(1 - Y)/N}$$: 1000 dies resolve 99 % to ±0.3 %, but proving 99.9 % needs about a hundred times more, so that enough failures are seen to be counted. This is why Monte Carlo runs on compact or reduced models, never directly on 3D FDTD ([Figure 29.3](#fig-29-3)b). With correlated variation across a chip, the dies are drawn with spatially correlated parameters, so that neighbouring devices vary together {% include cite.html keys="lu2017variability" %}.

[Figure 29.6](#fig-29-6) applies both to the demultiplexer. The coupler model is a fit to 19 femwell solves over width bias and thickness (rms error 6 × 10⁻⁵ in $$\ln L_x$$), plus the shift of $$L_x$$ at each channel; the wafers are those of Worked Example 35.1 and [Figure 37.6]({% link chapters/37_analysis.md %}#fig-37-6): 177 wafers of 113 dies, each die with four rings. Centred in its window, the coupling of every ring on every die stays between 10.3 and 12.0 %: the yield is 100 %. Designed for 14.5 %, as Chapter 14's Lorentzian estimate suggested, no die meets the crosstalk target. Even an independent gap error of σ = 3 nm, on top of everything else, would still leave 98 % of the dies inside the window. The ring resonances are a different story: they spread over about 12 nm, and whether a die works depends on the heater and on how the rings are locked.

<figure id="fig-29-6">
  <img src="{{ '/assets/figs/ch29_montecarlo.svg' | relative_url }}" style="width:640px" alt="(a) Histograms of the coupling of the four ring couplers on 20 001 dies. Centred in the window, the couplings lie between 10.3 and 12.0 percent, all between the dashed limits at 9.3 percent (passband at least 0.4 nm) and 13.1 percent (crosstalk at most minus 20 dB): 100 percent of dies pass. Designed for 14.5 percent, they lie between 13.5 and 15.7 percent, all beyond the crosstalk limit: 0 percent pass. (b) Histogram of the fabrication shift of the ring resonance, from about minus 8.5 to plus 6 nm; a shaded band from minus 5.7 to plus 3.3 nm and a lighter band beyond plus 7.1 nm are covered by a 12.75 nm heater range: 87 percent of dies.">
  <figcaption><span class="capnum">Figure 29.6.</span> <strong>Monte Carlo histograms with their specification limits</strong>, 20 001 dies on the synthetic wafers of Worked Example 35.1 (thickness and width bowls of 6 nm from centre to edge, a random width scatter of σ = 1.5 nm). (a) The coupling of all four demultiplexer rings, from the femwell model of \(L_x\) over width bias, thickness and channel: centred in the window (blue), every coupler passes; designed for 14.5 % (amber), none meets −20 dB of crosstalk. (b) The fabrication shift of the ring resonance, \(0.6\,\Delta W + 1.4\,\Delta t\) nm: with each ring held on its own channel, a heater range of 12.75 nm (3.75 nm of drift plus 9.0 nm for the spread) covers the dies in the shaded band, and those one FSR (12.8 nm) away, which use the ring's next resonance (lighter band, dotted edge): 87 % of the dies. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 29.3 · How much heater range do the demultiplexer rings need?</div>

A heater only red-shifts a ring, at 0.26 nm/mW ([Chapter 18]({% link chapters/18_thermal.md %})), and from 20 to 70 °C the ring drifts 3.75 nm to the red by itself. Let the rings be designed some distance blue of their channels; fabrication then moves each die's rings by the shift of [Figure 29.6](#fig-29-6)b. Three ways of locking them give very different requirements ([Figure 29.7](#fig-29-7)):

**Own channel.** Each ring must stay on its own channel at every temperature: at 70 °C it must still be blue of it, and at 20 °C the heater must cover the whole distance. The heater range must span the 3.75 nm of drift plus the fabrication spread (but never more than one FSR of spread, since a ring that far off can use its next resonance). For 99 % of dies that is 15.8 nm, or 61 mW per ring.

**Nearest channel, chosen at start-up.** Because the rings' FSR is exactly four channel spacings, a ring can serve any channel, and the electronics can reorder the data. Choosing, once, the nearest channel to the red that works over the whole temperature range reduces the fabrication spread to at most one channel spacing: 6.95 nm (3.75 + 3.2), or 27 mW, covers every die.

**Nearest channel, re-locked as the chip warms.** If a ring may hop to the next channel when its heater runs out, it never needs more than one channel spacing: 3.2 nm, or 12 mW, plus some hysteresis.

The mean heater power, which sets the energy, falls in the same order: 32, 13 and 6 mW per ring. For eight rings at 200 Gb/s the last is 0.25 pJ/bit (Chapter 18's 0.8 pJ/bit counts every heater at its maximum). Chapter 18's budget of 20 mW per ring (5.4 nm) is enough for the re-locking scheme, would serve 53 % of dies with a channel fixed at start-up, and 17 % with own-channel locking. No nanometre of fabrication tolerance was bought here: the architecture did the work.

</div>

<figure id="fig-29-7">
  <img src="{{ '/assets/figs/ch29_tuning.svg' | relative_url }}" style="width:640px" alt="(a) Percentage of dies whose rings stay on a channel from 20 to 70 degrees Celsius against the heater tuning range from 2.5 to 20 nm, with heater power from 10 to 77 mW on a top axis. Re-locking to the nearest channel as the chip warms jumps from 0 to 100 percent at 3.2 nm; the nearest channel fixed at start-up rises in a straight line from 3.75 nm to 100 percent at 6.95 nm; own-channel locking rises slowly and reaches 99 percent near 16 nm. (b) Bars of heater power per ring for 99 percent of dies, maximum and mean: 61 and 32 mW for own channel, 27 and 13 mW for the nearest channel fixed at start-up, 12 and 6 mW for re-locking.">
  <figcaption><span class="capnum">Figure 29.7.</span> <strong>Yield against heater range for three ways of locking the rings</strong> (Worked Example 29.3), on the Monte Carlo dies of Figure 29.6b, with the design offset chosen for the best yield. (a) The fraction of dies whose rings stay on a channel from 20 to 70 °C, against the heater's tuning range (bottom) and power (top). (b) The heater power per ring needed for 99 % of the dies: the maximum, which sizes the heater and its driver, and the mean over dies and temperatures, which sets the energy per bit. The four rings of a die are assumed to share its error. Drawn by <code>figsrc/ch29_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">29.6</span>Optimisation and inverse design

When a design has more than two or three free parameters, sweeping gives way to optimisation: a **figure of merit** (insertion loss, crosstalk, bandwidth, or a weighted sum with penalties for violated limits) is minimised over the parameters.

- **Derivative-free methods** (Nelder–Mead, particle swarms, Bayesian optimisation) need only the figure of merit and suit a handful of parameters, but each step costs one or more full simulations.
- **Gradient-based methods** need the derivative of the figure of merit with respect to every parameter. The **adjoint method** gives all of them from just two simulations, one forward and one with sources placed at the monitors, whatever the number of parameters {% include cite.html keys="lalaukeraly2013" %}. That makes it possible to treat every pixel of a design region as a parameter.
- **Inverse design** (topology optimisation) does exactly that, and finds compact, non-intuitive devices: a wavelength splitter of 2.8 × 2.8 µm was an early example {% include cite.html keys="piggott2015,molesky2018" %}. The constraints are what make it manufacturable: minimum feature sizes and gaps, binarised (fully etched or not) pixels, and the design rules of [Chapter 34]({% link chapters/34_verification.md %}).

Two cautions apply to every optimiser. It optimises what you wrote, not what you meant: a nominal optimum is often the edge of a cliff, so optimise the yield or the worst case over process corners (**robust optimisation**); the centring of Worked Example 29.1 is the simplest case. And it exploits numerical artefacts, so verify every optimised design with a finer mesh and, ideally, a different solver. [Chapter 32]({% link chapters/32_simtools.md %}) shows adjoint optimisation in practice.

## <span class="secnum">29.7</span>Compact models and their validity

A **compact model** reduces a device to its S-matrix as a function of wavelength and of a few parameters (gap, temperature, voltage), fitted to simulation sweeps or measurements, so that a circuit of many devices can be simulated in milliseconds ([Chapter 30]({% link chapters/30_flow.md %}), {% include cite.html keys="bogaerts2018" %}). A waveguide is an effective index and a group index, $$n_\mathrm{eff}(\lambda) \approx n_\mathrm{eff,0} - (n_g - n_\mathrm{eff,0})(\lambda - \lambda_0)/\lambda_0$$; a coupler is $$\kappa^2(\lambda, g)$$ from an exponential fit of $$L_x$$; a ring is built from both in the circuit.

Every compact model has a range of validity, and extrapolation is its classic failure. An exponential fit of [Chapter 9]({% link chapters/09_couplers.md %})'s femwell $$L_x$$ between 150 and 300 nm of gap is within 0.6 % of the solver inside that range, but 5.6 % off at 100 nm and 3.2 % off at 400 nm. Other limits are hidden in the model's assumptions: a single mode and one polarisation; no reflections, unless the model has return ports (grating couplers reflect, and their reflections make fringes in a measured MZI, [Chapter 36]({% link chapters/36_testing.md %})); linear response, so no thermal or free-carrier nonlinearity at high power; and one temperature. A good PDK states the ranges, and a careful designer checks that the circuit stays inside them.

**Statistical compact models** carry the variation with them: corner models (the S-matrix at the thick and wide or thin and narrow process corner), or models whose parameters (width bias, thickness) are drawn for each instance in a circuit Monte Carlo, with neighbouring instances correlated {% include cite.html keys="lu2017variability" %}. They are how Section 29.5's analysis scales from one device to a chip.

## <span class="secnum">29.8</span>Closing the loop with measurement

The last arrow of [Figure 29.1](#fig-29-1) is the most valuable: measurements of the fabricated chip update the models. Plan it before tape-out, by placing test structures that measure what the models need ([Chapters 36]({% link chapters/36_testing.md %}) and [37]({% link chapters/37_analysis.md %})): cutbacks for loss, interferometers and rings for the group index, gap series for coupling, width series for the bias. Then compare distributions, not single devices: a mean offset from the prediction points to a bias or a wrong model parameter, a wider spread to the process.

Measurements also answer inverse questions. A ring's resonance moves with both width and thickness, so one ring cannot tell them apart; two rings of different widths can, because a 1 µm strip barely notices its width ([Figure 29.8](#fig-29-8)). From femwell, a ring of 500 nm strip moves by 0.59 and 1.38 nm per nanometre of width and thickness, one of 1 µm strip by 0.08 and 1.39. Two measured shifts give two equations,

$$\begin{pmatrix}\Delta\lambda_{500}\\ \Delta\lambda_{1000}\end{pmatrix} = \begin{pmatrix}0.59 & 1.38\\ 0.08 & 1.39\end{pmatrix}\begin{pmatrix}\Delta W\\ \Delta t\end{pmatrix},$$

whose solution is the chip's width and thickness errors. With each resonance known to ±0.05 nm (an illustrative uncertainty, about what ±0.7 K of stage temperature alone would cause), the width comes out to ±0.14 nm and the thickness to ±0.04 nm (one sigma). The width error goes back into the layout as a drawn bias; the thickness goes into the models for the next design. Fitting width and height to measured spectra in this way is also how statistical models are calibrated against a real process {% include cite.html keys="lu2017variability" %}.

<figure id="fig-29-8">
  <img src="{{ '/assets/figs/ch29_loop.svg' | relative_url }}" style="width:640px" alt="(a) Thickness error against width error, from minus 8 to plus 2 nm of width and 0 to 6 nm of thickness. A steep blue line shows the errors that explain the 500 nm ring's measured shift of plus 1.78 nm, and a nearly flat amber line those that explain the 1 micrometre ring's plus 3.84 nm, each with dotted lines for the measurement uncertainty. They cross at minus 4 nm of width and plus 3 nm of thickness, where a small shaded ellipse marks the three-sigma uncertainty: plus or minus 0.4 nm of width and 0.13 nm of thickness. (b) Bars of the ring resonance shift per nanometre: 0.59 per nm of width and 1.38 per nm of thickness for the 500 nm strip; 0.08 and 1.39 for the 1 micrometre strip.">
  <figcaption><span class="capnum">Figure 29.8.</span> <strong>Separating width and thickness errors with two rings</strong> (illustrative errors: 4 nm narrower and 3 nm thicker than drawn). (a) Each measured resonance shift allows a line of width and thickness errors (dotted: ±3 × 0.05 nm of measurement uncertainty); the two lines cross at the chip's errors, with the three-sigma uncertainty ellipse shaded. (b) The resonance shift per nanometre of width and of thickness for rings of 500 nm and 1 µm strip (femwell, 1550 nm): the wide strip barely notices its width, but both notice the thickness. Drawn by <code>figsrc/ch29_figs.py</code> from <code>figsrc/ch29_sims.py</code> (femwell).</figcaption>
</figure>

## <span class="secnum">29.9</span>Reproducible simulation

A simulation that cannot be rerun cannot be checked, compared with the next tape-out or handed to a colleague. The practices that make scientific computing reliable apply directly {% include cite.html keys="wilson2014" %}:

- **Scripts, not clicks.** Every result comes from a script that builds the geometry, runs the solver and post-processes, with all parameters in one place. Graphical sessions are fine for exploring, but the result that goes into a design review is the one the script produces.
- **Version control.** Scripts, layout code and small result files live in a repository such as git; every tape-out is a tag, and every change to a design is a reviewed difference.
- **Recorded settings.** Store with each result the solver and its version, the mesh or grid, the window and boundary layers, the material data and their source, the wavelength points, the run time or convergence criterion, the random seed of any Monte Carlo, and the hardware and run time.
- **Pinned environments.** Record the versions of every package (an environment file or a container image), so the same script gives the same answer next year.
- **Regression tests.** When a tool or a PDK changes, rerun the key simulations and compare with the stored results.

This tutorial follows the same rules. Every figure is drawn by a script in <code>figsrc/</code>; the femwell and MEEP runs of this chapter are in <code>figsrc/ch29_sims.py</code>, run in a container with fixed versions (femwell 0.1.12 {% include cite.html keys="femwell" %}, MEEP 1.35.1 {% include cite.html keys="meep" %}), and their results are stored as JSON beside it. One check comes for free: at its 25 nm mesh it reproduces the 37.85 µm of [Chapter 9]({% link chapters/09_couplers.md %}) exactly.

## <span class="secnum">29.10</span>Design for manufacturing and for test

**Design for manufacturing** turns this chapter's analysis into layout habits; [Chapter 35]({% link chapters/35_fab.md %}) (Section 35.7) gives the process view, and [Chapters 33]({% link chapters/33_layout.md %}) and [34]({% link chapters/34_verification.md %}) the layout practice and the rule checks.

- Use the PDK's validated cells where they exist: a measured cell beats a simulated one.
- Prefer tolerant geometries: bias-tolerant couplers, wide waveguides in long arms, adiabatic couplers or MMIs where the split must be broadband.
- Keep away from the minimum rules: the process is least controlled at the smallest widths and gaps.
- Match what must match: devices that must agree close together, in the same orientation, with the same surroundings and pattern density.
- Budget for tuning, centre every design in its window, and parameterise the layout so that a measured bias can be applied to the next tape-out.

**Design for test** makes the chip measurable ([Chapters 34]({% link chapters/34_verification.md %}) and [36]({% link chapters/36_testing.md %})):

- Every device that matters can be measured on its own, or through a tap and a monitor photodiode.
- Loopbacks calibrate the fibre couplers; parameter series (gap, width, length) extract the models; copies in different corners of the die measure the within-die variation.
- The test station's rules are followed: couplers on the fibre-array pitch in one orientation, machine-readable labels, pads on the probe-card grid ([Chapter 17]({% link chapters/17_fiberarrays.md %})).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Add what closes the loop: rings of 500 nm and 1 µm strip side by side, to separate width and thickness (Section 29.8); a gap series of rings or couplers; cutback spirals and a loopback; and a copy of the key structures in a second corner of the chip. Keep the layout script, the simulation scripts and their settings in one repository, and tag the version you submit.

</div>

## Reading

{% include reflist.html keys="chrostowski2015,bogaerts2018,lu2017variability,mikkelsen2014,lalaukeraly2013,piggott2015,molesky2018,wilson2014,femwell,meep" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Work down from the specification: budgets with visible margin, then component targets, then device parameters with tolerances; verify each level against its own specification on the way up.
- Margin only means something against the spread: centre the design in its window, and do not stack worst cases of independent variations.
- Use the cheapest model that answers the question (a formula, a mode solver, EME) and verify the final design once with 3D FDTD; for one ring coupler the costs range from under a microsecond to 1.6 days on one core.
- Make convergence a habit, and converge the quantity you need: small differences and sensitivities need finer meshes than the quantities themselves.
- Corners bound monotonic responses but are pessimistic for independent variables; Monte Carlo on a fast model gives the yield, with an error of $$\sqrt{Y(1-Y)/N}$$.
- Architecture beats tolerance: a bias-tolerant coupler and a locking strategy that lets rings use the nearest channel turn a fabrication problem into a design choice.
- Compact models are valid only where they were fitted; measurements close the loop and keep the models honest; scripts, version control and recorded settings make it all reproducible.

</div>
