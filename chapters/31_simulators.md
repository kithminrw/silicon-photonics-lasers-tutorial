---
title: "31. How Photonic Simulators Work"
parent: "Part VII · Design, Simulation and Layout"
nav_order: 31
permalink: /part-7/ch31/
chapter: 31
---

# <span class="chapnum">Chapter 31</span>How Photonic Simulators Work

Every simulator turns Maxwell's equations into arithmetic on a grid; knowing how it does so tells you which one to use, how fine a grid to ask for, and when to distrust the answer.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain how every photonic solver discretises Maxwell's equations, and how its choice of domain (frequency or time) and of dimensions sets what it can do;
- describe how finite-difference and finite-element mode solvers, eigenmode expansion and beam propagation work, and where each one fails;
- write the FDTD update equations on the Yee grid, and derive its stability (Courant) limit and its numerical dispersion;
- explain perfectly matched layers, pulsed sources and Fourier-transform monitors, dispersive materials, subpixel averaging and symmetry;
- run a convergence study, and estimate the memory and run time of a 3D simulation before starting it;
- decide when 2D or 2.5D (variational) FDTD, FDFD, coupled-mode theory, transfer matrices, a circuit solver or a multiphysics solver will do the job.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which solver, and how fine a grid, gives an answer you can trust in a time you can afford?

</div>

## <span class="secnum">31.1</span>What every simulator does

All the devices of this tutorial obey the same two curl equations ([Chapter 2]({% link chapters/02_em.md %})): in a non-magnetic dielectric with relative permittivity $$\varepsilon_r(\mathbf{r})$$,

$$\nabla\times\mathbf{E} = -\mu_0\frac{\partial\mathbf{H}}{\partial t}, \qquad \nabla\times\mathbf{H} = \varepsilon_0\varepsilon_r\frac{\partial\mathbf{E}}{\partial t}.$$

A computer cannot store a field at infinitely many points, so every solver does three things.

1. **It discretises space.** The fields are kept at a finite set of points (a grid) or as a finite set of simple functions on small patches (a mesh), and each derivative becomes a difference between neighbours. Maxwell's equations become a large, sparse set of algebraic equations, one or a few per grid point.
2. **It chooses a domain.** A *frequency-domain* solver assumes fields that oscillate as $$e^{j\omega t}$$ and solves for one wavelength at a time, either an eigenproblem (which modes exist?) or a linear system (what does this source produce?). A *time-domain* solver starts from a source and steps the fields forward in time; a short pulse carries a whole band of wavelengths through the device at once.
3. **It chooses which dimensions to keep.** A waveguide that does not change along its length needs only its cross-section; a planar device can sometimes be folded into a 2D top view; a grating coupler that sends light up out of the chip needs all three dimensions.

[Figure 31.1](#fig-31-1) arranges the methods of this chapter by those choices. Moving right or down keeps more of the physics and costs more: a mode solver handles tens of thousands of unknowns in seconds, while a 3D FDTD run updates hundreds of millions of cells tens of thousands of times. Whatever the method, its answer belongs to the *discretised* device, not the real one. Every number it returns has to be checked by refining the discretisation until the number stops changing (Section 31.10), and every approximation (fewer dimensions, fewer modes, paraxial propagation) has to be checked against a more complete method at least once. [Chapter 29]({% link chapters/29_design.md %}) places these solvers in the design workflow and [Chapter 32]({% link chapters/32_simtools.md %}) shows the tools that implement them; this chapter is about how they work inside.

<figure id="fig-31-1">
  <img src="{{ '/assets/figs/ch31_landscape.svg' | relative_url }}" style="width:680px" alt="A table of method cards. Columns: a cross-section, 2D top or side view, the full 3D device. Rows: eigenmodes in the frequency domain, one frequency for the whole device, time stepping for all frequencies. Mode solvers FDE and FEM sit at cross-section and eigenmodes; EME and BPM in 2D eigenmodes; EME with 3D modes in 3D eigenmodes; 2D and 3D FDFD or FEM in the one-frequency row; 2D and 2.5D FDTD and 3D FDTD in the time-stepping row. Each card lists what the method returns and how its unknowns scale. An arrow along the bottom reads more of the geometry kept, more general, more costly.">
  <figcaption><span class="capnum">Figure 31.1.</span> <strong>What each kind of solver keeps.</strong> Columns: how much of the geometry the method represents. Rows: how it solves Maxwell's equations. \(N_x, N_y, N_z\) are the numbers of grid points along each axis and \(N_t\) the number of time steps. A mode solver is the cheapest and answers only questions about a uniform cross-section; 3D FDTD answers almost any question at the highest cost. Schematic. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">31.2</span>Mode solvers

A waveguide that is uniform along $$z$$ has modes whose fields vary along it only as $$e^{-j\beta z}$$. Substituting that into Maxwell's equations removes $$z$$ altogether and leaves a problem on the cross-section: find the values of $$\beta^2$$ for which a non-zero field exists. That is an **eigenvalue problem**, $$\mathbf{P}\,\mathbf{e} = \beta^2\mathbf{e}$$, in which the vector $$\mathbf{e}$$ holds the transverse fields at every grid point and the matrix $$\mathbf{P}$$ holds the discretised curls and the permittivity. Each eigenvector is a mode; its eigenvalue gives $$n_\mathrm{eff} = \beta/k_0$$.

**Finite differences on a Yee grid (FDE).** The cleanest discretisation staggers the field components inside each grid cell ([Figure 31.2a](#fig-31-2)): $$E_x$$ at the middle of the horizontal cell edges, $$E_y$$ at the middle of the vertical ones, $$E_z$$ at the corners and $$H_z$$ at the centre, which is the cross-section of the 3D Yee cell of Section 31.5. Every derivative is then a difference between two neighbouring values half a cell either side of the point where it is needed, which is accurate to second order in the cell size $$h$$. Eliminating $$E_z$$ and the three magnetic components leaves an eigenproblem for $$E_x$$ and $$E_y$$ alone {% include cite.html keys="zhu2002" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Full-vector finite-difference mode equation</div>

$$\beta^2 E_x = k_0^2\varepsilon_x E_x + U_x\Phi - V_y\Psi, \qquad \beta^2 E_y = k_0^2\varepsilon_y E_y + U_y\Phi + V_x\Psi,$$

$$\Phi = \varepsilon_z^{-1}\left(V_x\varepsilon_xE_x + V_y\varepsilon_yE_y\right), \qquad \Psi = U_xE_y - U_yE_x$$

</div>

Here $$U_x, U_y$$ are forward differences (from E points to H points), $$V_x = -U_x^\mathsf{T}$$ and $$V_y = -U_y^\mathsf{T}$$ backward ones, and $$\varepsilon_x, \varepsilon_y, \varepsilon_z$$ are the permittivities seen by each component. $$\Phi$$ is proportional to $$E_z$$ and $$\Psi$$ to $$H_z$$; where they vanish, $$E_x$$ and $$E_y$$ are uncoupled, which is why most rows of the matrix have only five non-zero entries. The full-vector mode solver of [Chapter 6]({% link chapters/06_soi.md %})'s demo, which runs in your browser, is exactly this method on a grid whose cells shrink to a few nanometres at every interface; the same equations, written for the magnetic field and for anisotropic materials, are the basis of widely used FD mode solvers {% include cite.html keys="fallahkhair2008" %}. The matrix is huge but sparse, and only the few modes with the largest $$n_\mathrm{eff}$$ are wanted, so the solver uses *shift-invert* iteration: it factorises $$\mathbf{P} - \sigma\mathbf{I}$$ once, for a guess $$\sigma = (k_0n_\mathrm{guess})^2$$ just above the expected index, and then finds the eigenvalues nearest that guess in a few solves.

**What happens at a wall.** The permittivity jumps at every interface, and the component of $$\mathbf{E}$$ normal to the interface jumps with it ($$\varepsilon E_\perp$$ is continuous, [Chapter 2]({% link chapters/02_em.md %})). If each field point simply takes the material it happens to sit in (a **staircase**), the walls effectively move by up to half a cell as the grid changes, and the answer wanders irregularly as $$h$$ is refined. If instead each field point sees the cell around it averaged the right way, the harmonic mean ($$\langle 1/\varepsilon\rangle^{-1}$$) for the component normal to a wall and the arithmetic mean for components along it, the error becomes small and smooth. [Figure 31.2c](#fig-31-2) shows both for the 500 × 220 nm strip: on uniform grids from 40 to 8 nm, the averaged values stay within 0.004 of the femwell value of Chapter 6, and within 0.0003 from 12 nm down, while the staircase values scatter from 0.05 below it to 0.07 above and are still 0.011 off at 8 nm. A third option is to put cell faces exactly on every interface and grade the cells, fine near the walls and coarse far away; that is what the in-browser solver does.

<figure id="fig-31-2">
  <img src="{{ '/assets/figs/ch31_fde.svg' | relative_url }}" style="width:700px" alt="Three panels. (a) A few grid cells near the corner of a silicon core: Ex arrows on horizontal cell edges, Ey arrows on vertical edges, Ez dots at the corners, Hz circles at cell centres; cells cut by the core's walls are shaded in between silicon and oxide. (b) The computed Ex of the TE0 mode of a 500 by 220 nm strip on the window, with the core outline and every fifth grid line, effective index 2.4436. (c) Effective index against grid step from 8 to 40 nm: the staircase values scatter between 2.40 and 2.51, the averaged values stay close to the femwell line at 2.4459.">
  <figcaption><span class="capnum">Figure 31.2.</span> <strong>A finite-difference mode solver.</strong> (a) Where the field components live in a cell of the Yee grid, near a corner of the core; cells cut by a wall get an averaged permittivity. (b) \(E_x\) of the TE0 mode of a 500 × 220 nm silicon strip in oxide at 1550 nm, solved on a 20 nm grid in a 2.4 × 1.8 µm window with metal walls (red positive). (c) \(n_\mathrm{eff}\) against grid step, with each field point's permittivity sampled (staircase) or averaged over its cell; the strip is offset by (13, 7) nm so that no grid line follows its walls. Computed by <code>figsrc/ch31_fde.py</code> (the equations above, SciPy sparse eigensolver). Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

**Finite elements (FEM).** A finite-element solver covers the cross-section with triangles that follow every interface exactly, fine where the field changes fast and coarse elsewhere, and represents the field in each triangle by low-order polynomials. Vector ("edge") elements, whose unknowns are the tangential field along each edge, enforce the right continuity at material boundaries and avoid the spurious solutions that plain nodal elements produce. Slanted sidewalls, rounded corners and thin layers cost nothing extra. The open solver femwell {% include cite.html keys="femwell" %} is of this kind; it produced most of the mode data in this tutorial, and [Lab 2]({% link labs/lab02_femwell.md %}) uses it step by step.

**What a mode solver gives, and what it cannot.** Each solve returns $$n_\mathrm{eff}$$ and the full vector field of each mode, from which follow the confinement factor, the mode area, overlaps with fibres or other modes ([Chapter 8]({% link chapters/08_bends.md %})) and the group index, either from $$n_\mathrm{eff}$$ at two nearby wavelengths, $$n_g = n_\mathrm{eff} - \lambda\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}\lambda$$, or directly from the fields. If the window is lined with absorbing layers (perfectly matched layers, Section 31.7), leaky modes acquire a complex $$n_\mathrm{eff}$$ whose imaginary part is their loss: leakage through a thin buried oxide, or the radiation of a bend solved in a coordinate system that follows the curve ([Chapter 8]({% link chapters/08_bends.md %})). What a mode solver cannot do is anything that changes along $$z$$: tapers, junctions, gratings, reflections. For those it supplies the ingredients, the modes, to the methods that follow.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.1 · The size of a mode-solver problem</div>

The window of [Figure 31.2](#fig-31-2) is 2.4 × 1.8 µm. On a 10 nm grid it has 240 × 180 cells, and with the tangential field fixed at zero on the walls there are 85 980 unknowns ($$E_x$$ and $$E_y$$). Stored as a full matrix, $$\mathbf{P}$$ would need $$85\,980^2 \times 8$$ bytes = 59 GB. It has only 438 506 non-zero entries, about five per row, which take about 5 MB, and a shift-invert solve for three modes took about 7 s on one core. The averaged grid gives $$n_\mathrm{eff} = 2.4456$$ against femwell's 2.4459; the staircase grid gives 2.4471 at 10 nm but 2.4573 at 8 nm. That 0.011 error matters: a ring resonance moves by $$\lambda\,\Delta n_\mathrm{eff}/n_g = 1550 \times 0.011/4.18 \approx 4$$ nm, almost half a free spectral range of a 10 µm ring. Sparse storage makes a mode solver cheap; averaging at the walls makes it accurate.

</div>

## <span class="secnum">31.3</span>Eigenmode expansion

Many devices are uniform along $$z$$ in pieces: an MMI is a wide guide between two narrow ones, a taper can be approximated by short steps of constant width, a grating repeats two sections. **Eigenmode expansion** (EME) exploits this {% include cite.html keys="bienstman2001,gallagher2003" %}. Inside each section of constant cross-section the field is *exactly* a sum of that section's modes, forward and backward, each travelling with its own $$e^{\mp j\beta z}$$. All the work is at the interfaces, where the tangential $$\mathbf{E}$$ and $$\mathbf{H}$$ must be continuous. Writing the fields on each side as sums of modes and projecting both conditions onto the modes gives the interface's transmission and reflection matrices:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Mode matching at an interface between sections A and B</div>

$$\mathbf{T}_{AB} = 2\left(\mathbf{O}_{BA}^\mathsf{T} + \mathbf{O}_{AB}\right)^{-1}, \qquad \mathbf{R}_{AB} = \mathbf{O}_{BA}^\mathsf{T}\,\mathbf{T}_{AB} - \mathbf{I}, \qquad (\mathbf{O}_{AB})_{ij} = \int \left(\mathbf{e}_{A,i}\times\mathbf{h}_{B,j}\right)\cdot\hat{\mathbf{z}}\,\mathrm{d}A$$

</div>

with every mode normalised to unit power. Each section contributes only a diagonal matrix of phases $$e^{-j\beta_iL}$$, and the interfaces and sections are joined as scattering matrices ([Chapter 9]({% link chapters/09_couplers.md %})), which stays numerically stable even when evanescent modes are included. The result is the device's S-matrix for every mode at every port.

**Why it is fast.** The cost is set by the number of *different* cross-sections and the number of modes $$M$$ (a mode solve per cross-section and matrix operations that grow as $$M^3$$), not by the length. Changing a section's length changes only its phases, so a sweep of lengths reuses everything else; a periodic structure needs the S-matrix of one period, combined with itself as often as there are periods; an MMI has only two interfaces ([Lab 3]({% link labs/lab03_couplers.md %}) computes one this way). Millimetre-long tapers, MMIs, directional couplers, spot-size converters and long gratings are where EME is most useful.

[Figure 31.3](#fig-31-3) takes the 0.5 → 3 µm taper of [Chapter 8]({% link chapters/08_bends.md %})'s adiabatic-taper demo, in the same 2D effective-index model, cut into 200 sections with 24 symmetric modes each. Building the 201 interfaces took about a minute; after that, each of the 69 lengths of panel (b) took 0.08 s. A 4 µm taper sends 11.7 % of the light into TE2, a 20 µm one 0.67 % (the demo's own EME check gave 0.69 %), and a 40 µm one 0.17 %.

<figure id="fig-31-3">
  <img src="{{ '/assets/figs/ch31_eme.svg' | relative_url }}" style="width:680px" alt="Top: top view of a linear taper from 0.5 to 3 micrometres over 20 micrometres, drawn as eight sections of constant width separated by dashed lines, with the local fundamental-mode profile drawn in red at five positions, widening along the taper. Bottom left: power converted into TE2 and TE4 against taper length from 1 to 60 micrometres on a log scale, falling from about 0.3 to below 0.001 for TE2, with a circle at 20 micrometres marking the Chapter 8 demo's value. Bottom right: TE2 power at 20 micrometres against the number of sections, jumping between 0.5 and 28 percent below 16 sections and settling at 0.67 percent above 32, and against the number of modes, flat at 0.64 to 0.68 percent.">
  <figcaption><span class="capnum">Figure 31.3.</span> <strong>Eigenmode expansion of a taper.</strong> (a) A linear taper from 0.5 to 3 µm is replaced by sections of constant width (8 drawn, 200 used); in each the field is a sum of that section's modes (red: the local TE0). (b) Power converted from TE0 into TE2 and TE4 against taper length, from one set of interface matrices; circle: the EME check of Chapter 8's demo at 20 µm. (c) Convergence at 20 µm: with too few sections the staircase taper is a different device and the answer is meaningless; from 32 sections on, TE2 is within 5 % of its converged 0.67 %. Even two modes give TE2 within 6 %. 2D effective-index model (core 2.848 in oxide, lateral TM conditions, 12 µm box), 1550 nm. Computed by <code>figsrc/ch31_eme.py</code>. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

**Where it fails.** EME needs the field to be well described by a modest number of modes. Light that radiates, at a sharp bend, a grating coupler or a scattering defect, is not: it belongs to a continuum of radiation modes that a closed box represents by a comb of "box modes", and absorbing boundaries make those modes complex and slow to find. Many modes are then needed and the $$M^3$$ cost grows quickly; structures that change continuously need many sections; and a 3D EME needs a full-vector mode solve for each cross-section. Truncating the set of modes also breaks energy conservation slightly: in the taper above, the output powers plus the reflection add up to 1.0017. Checking that power balance, and that the answer stops changing as sections and modes are added (panel c), is the EME version of a convergence test.

## <span class="secnum">31.4</span>Beam propagation

The **beam propagation method** (BPM) also marches along $$z$$, but with a single field rather than a set of modes {% include cite.html keys="feit1978,kawano2001" %}. Write the field as a slowly varying envelope times a carrier, $$E = u(x, y, z)\,e^{-jk_0n_\mathrm{ref}z}$$, and assume that $$u$$ changes little over a wavelength, so that $$\partial^2u/\partial z^2$$ can be dropped. The wave equation becomes first order in $$z$$: knowing $$u$$ on one plane gives it on the next, and the field is stepped through the device plane by plane, each step a 2D (or 1D) problem. BPM handles any slowly varying geometry, including continuous tapers, Y-branches and fibre-like structures, with modest memory. Its limits come from its two approximations. Being *paraxial*, it is accurate only for light travelling close to $$z$$ (wide-angle versions extend this). Being *one-way*, it ignores reflections. It suits weakly guiding waveguides, such as glass, silicon nitride and the slab regions of arrayed-waveguide gratings, better than high-contrast silicon with abrupt features.

## <span class="secnum">31.5</span>FDTD: the Yee grid and the leapfrog

The **finite-difference time-domain** method (FDTD) solves the two curl equations directly, in all three dimensions and in time, with no assumption about the geometry or the direction of the light {% include cite.html keys="yee1966,taflove2005" %}. Its idea is simple, and its success comes from where it puts the field components.

**Read the curl equations as bookkeeping.** Faraday's law says that the circulation of $$\mathbf{E}$$ around a small loop sets the rate of change of the magnetic field through it; Ampère's law says the same with $$\mathbf{H}$$ and $$\mathbf{E}$$ swapped. Yee placed each component of $$\mathbf{E}$$ at the middle of a cube's edge, along that edge, and each component of $$\mathbf{H}$$ at the centre of a face, normal to it ([Figure 31.4](#fig-31-4)). Then every $$H$$ component is ringed by exactly the four $$E$$ components whose circulation drives it, and every $$E$$ component by four $$H$$ components. A spatial derivative becomes the difference of two values one cell apart, centred on the point where it is needed. In time the same trick is played: $$\mathbf{E}$$ is known at whole steps $$n\Delta t$$, $$\mathbf{H}$$ at half steps $$(n + \tfrac{1}{2})\Delta t$$, and each is advanced past the other, like two people leapfrogging.

<figure id="fig-31-4">
  <img src="{{ '/assets/figs/ch31_yee.svg' | relative_url }}" style="width:680px" alt="(a) A cube drawn in perspective with an arrow at the middle of each of its twelve edges, pointing along the edge, labelled Ex, Ey and Ez, and arrows at the centres of three visible faces, normal to them, labelled Hx, Hy and Hz. (b) One square face with Hz at its centre pointing out of the page, and four E arrows around its edges forming a counter-clockwise loop: Ex at the bottom and top, Ey at the left and right; the circulation of E around a face is the rate of change of the H through it. (c) A lattice of position along x against time: blue dots for E at whole positions and whole time steps, red squares for H at half positions and half time steps, with arrows showing that each new E is computed from the old E at the same place and the two H values either side half a step earlier, and each H likewise.">
  <figcaption><span class="capnum">Figure 31.4.</span> <strong>Yee's grid.</strong> (a) In each cell, \(\mathbf{E}\) components sit at the middle of the edges, along them, and \(\mathbf{H}\) components at the centres of the faces, normal to them (three faces shown). (b) Seen on one face, the four \(E\) components form a loop around \(H_z\): Faraday's law in its discrete form. (c) In time, \(\mathbf{E}\) and \(\mathbf{H}\) are half a step apart: each new value needs only its own old value and its neighbours, so the update is explicit and no matrix is ever solved. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

With $$E_x$$ at $$(i + \tfrac{1}{2}, j, k)$$, $$E_y$$ at $$(i, j + \tfrac{1}{2}, k)$$, $$H_z$$ at $$(i + \tfrac{1}{2}, j + \tfrac{1}{2}, k)$$ and so on, two of the six updates read:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">FDTD update equations (the other four follow by cycling x → y → z)</div>

$$H_z\big|^{n+\frac{1}{2}}_{i+\frac{1}{2},j+\frac{1}{2},k} = H_z\big|^{n-\frac{1}{2}}_{i+\frac{1}{2},j+\frac{1}{2},k} - \frac{\Delta t}{\mu_0}\left[\frac{E_y\big|^{n}_{i+1,j+\frac{1}{2},k} - E_y\big|^{n}_{i,j+\frac{1}{2},k}}{\Delta x} - \frac{E_x\big|^{n}_{i+\frac{1}{2},j+1,k} - E_x\big|^{n}_{i+\frac{1}{2},j,k}}{\Delta y}\right]$$

$$E_x\big|^{n+1}_{i+\frac{1}{2},j,k} = E_x\big|^{n}_{i+\frac{1}{2},j,k} + \frac{\Delta t}{\varepsilon_0\varepsilon_r}\left[\frac{H_z\big|^{n+\frac{1}{2}}_{i+\frac{1}{2},j+\frac{1}{2},k} - H_z\big|^{n+\frac{1}{2}}_{i+\frac{1}{2},j-\frac{1}{2},k}}{\Delta y} - \frac{H_y\big|^{n+\frac{1}{2}}_{i+\frac{1}{2},j,k+\frac{1}{2}} - H_y\big|^{n+\frac{1}{2}}_{i+\frac{1}{2},j,k-\frac{1}{2}}}{\Delta z}\right]$$

</div>

**Why the staggering works.** Every difference is centred, so the errors are second order in $$\Delta x$$ and $$\Delta t$$: halve the cell and they fall fourfold. The discrete divergence of a discrete curl is exactly zero, so the grid never creates spurious charge, however long it runs. Tangential $$\mathbf{E}$$ and normal $$\mathbf{H}$$ fall naturally on the faces of the cells, which makes metal walls and mirror planes easy to impose. And because each new value depends only on its neighbours, a time step is a sweep through memory with a handful of multiplications per cell: nothing is inverted, and the work divides cleanly between processor cores or a graphics card.

The whole method fits in a few lines. In one dimension, with $$E$$ and $$H$$ normalised so that $$c = \Delta x = 1$$:

```python
import numpy as np
N, steps, S = 400, 2000, 0.5               # cells, time steps, Courant number c*dt/dx
n = np.ones(N); n[200:260] = 3.476         # a 60-cell slab of silicon in air: index of each E point
E, H = np.zeros(N), np.zeros(N - 1)        # E at the cell edges, H half a cell further on
for t in range(steps):
    H += S * (E[1:] - E[:-1])                        # Faraday: H changes with the curl (here d/dx) of E
    E[1:-1] += S / n[1:-1]**2 * (H[1:] - H[:-1])     # Ampere: E changes with the curl of H
    E[100] += np.exp(-((t - 150) / 40)**2) * np.sin(2 * np.pi * S * t / 40)   # soft source, 40 cells per wavelength
```

Everything else in a production code (absorbing boundaries, mode sources, Fourier-transform monitors, dispersive materials, averaging at interfaces, parallel computing) is added around this loop. MEEP, the open FDTD code used in [Lab 6]({% link labs/lab06_gc_meep.md %}) and in this chapter's figures, is a good place to see all of them {% include cite.html keys="meep" %}.

## <span class="secnum">31.6</span>Stability and numerical dispersion

**The Courant limit.** An explicit scheme has a speed limit. Inserting a plane wave $$e^{j(\omega t - \mathbf{k}\cdot\mathbf{r})}$$ into the update equations gives the scheme's own dispersion relation,

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Yee dispersion relation and the Courant limit</div>

$$\left[\frac{\sin(\omega\Delta t/2)}{v\,\Delta t}\right]^2 = \sum_{i = x, y, z}\left[\frac{\sin(k_i\Delta_i/2)}{\Delta_i}\right]^2 \quad\Longrightarrow\quad \Delta t \le \frac{1}{c\sqrt{1/\Delta x^2 + 1/\Delta y^2 + 1/\Delta z^2}}$$

</div>

where $$v = c/n$$ is the speed of light in the medium. The left side cannot exceed $$1/(v\Delta t)^2$$ for a real frequency, while the right side reaches $$\sum 1/\Delta_i^2$$ for the shortest waves the grid can hold, which alternate in sign from cell to cell. If $$\Delta t$$ is too long, those waves have no real frequency: their amplitude is multiplied by more than one at every step and the simulation explodes. Since the fastest light in the grid travels at $$c$$ (in air or, approximately, in oxide), the limit uses $$c$$. For cubic cells the **Courant number** $$S = c\Delta t/\Delta x$$ must not exceed $$1/\sqrt{3} = 0.577$$ in 3D, $$1/\sqrt{2}$$ in 2D and 1 in 1D {% include cite.html keys="taflove2005" %}. [Figure 31.5a](#fig-31-5) runs a small 3D FDTD with random initial fields just below and just above the limit: at 0.99 of it nothing grows; at 1.01 of it the field grows by a factor of 1.327 per step, as the dispersion relation predicts, and passes $$10^{14}$$ within 130 steps. Codes differ in which speed defines $$S$$: MEEP uses the vacuum speed $$c$$ and a default of $$S = 0.5$$ {% include cite.html keys="meep" %}; a grid filled with oxide or denser material can use the speed in oxide instead, as the demo of Section 31.7 does, which makes its 2D limit exactly $$1/\sqrt{2}$$ and its default 0.5 equal to 0.72 in MEEP's terms.

**Numerical dispersion.** Below the limit the scheme is stable but not exact: the same relation says that waves on the grid travel slightly too slowly, and by an amount that depends on their direction. Along a grid axis, with $$N$$ cells per wavelength in the material and $$S$$ the Courant number in that material ($$v\Delta t/\Delta x$$), the phase velocity is low by

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Numerical phase error along an axis</div>

$$\frac{\Delta v_p}{v_p} \approx -\frac{1}{6}\left(\frac{\pi}{N}\right)^2\left(1 - S^2\right)$$

</div>

and less along diagonals ([Figure 31.5b](#fig-31-5)). The error falls as $$1/N^2$$, but it accumulates with distance: every wavelength travelled adds the same phase error. In silicon at 1550 nm the wavelength is 446 nm, so 20 nm cells give $$N = 22.3$$, and with MEEP's $$S = 0.5$$ (0.144 inside silicon) light along an axis is 0.33 % too slow, along a body diagonal 0.10 %. Everything that depends on an accumulated phase, such as a resonance wavelength, an interferometer's fringe or a grating's Bragg wavelength, inherits this error, which is why the grating-coupler peak in Lab 6 sits 9 nm to the red at 30 pixels per µm and within 1 nm at 60.

<figure id="fig-31-5">
  <img src="{{ '/assets/figs/ch31_numerics.svg' | relative_url }}" style="width:680px" alt="(a) Largest field against time step for a small 3D FDTD run: at 0.99 times the Courant limit it stays flat near 1; at 1.01 times the limit it grows exponentially to 10 to the 14 within 130 steps, parallel to a dashed line marking growth by 1.327 per step. (b) Phase-velocity error against cells per wavelength in the material on log axes: three straight lines falling as one over N squared, highest along an axis, lower along a face diagonal and lowest along a body diagonal; a dotted line marks 20 nm cells in silicon at 22 cells per wavelength, where the axis error is about 0.3 percent.">
  <figcaption><span class="capnum">Figure 31.5.</span> <strong>The two numerical limits of FDTD.</strong> (a) Stability: a 16 × 16 × 16 periodic 3D grid in vacuum with random initial fields, stepped with Courant numbers 1 % below and 1 % above \(1/\sqrt{3}\); dashed: the growth rate of the shortest grid wave from the dispersion relation. (b) Accuracy: the phase velocity of the 3D Yee scheme is too low by an amount that falls as \(1/N^2\) and depends on direction; computed for silicon (Courant number 0.5 in vacuum, 0.144 in silicon). Both computed in NumPy by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.2 · How fine a grid for a ring resonance?</div>

Suppose a 3D FDTD run should place a ring's resonance within 0.1 nm. A phase-velocity error $$\delta$$ raises the effective index by about $$\delta\,n_\mathrm{eff}$$, and the resonance moves by $$\Delta\lambda = \lambda\,\delta\,n_\mathrm{eff}/n_g$$; with $$n_\mathrm{eff} = 2.45$$ and $$n_g = 4.18$$ that is $$\Delta\lambda = 908\,\delta$$ nm, so $$\delta$$ must stay below $$1.1\times10^{-4}$$. Taking the worst direction and silicon's local Courant number of 0.144, the formula above gives $$N = \pi\sqrt{(1 - 0.144^2)/(6 \times 1.1\times10^{-4})} \approx 121$$ cells per wavelength, or 3.7 nm cells. Compared with 20 nm cells that is 5.4 times finer in each direction and 5.4 times more steps: $$5.4^4 \approx 850$$ times the work. With 20 nm cells the same formula gives $$\delta = 0.33$$ % and a shift of 3 nm, a third of the 9.2 nm free spectral range of a 10 µm ring. (The slab of [Figure 31.8](#fig-31-8), on the same grid, is off by less, 0.12 % in $$n_\mathrm{eff}$$, because a fifth of its power travels in oxide and its light crosses the grid obliquely.) The practical conclusion: use FDTD for what converges quickly (coupling ratios, losses, reflections, group index) and take absolute phases from a converged mode solver, or simulate on two grids and extrapolate, since the error scales as $$\Delta x^2$$.

</div>

## <span class="secnum">31.7</span>Absorbing boundaries: the perfectly matched layer

A grid must end somewhere, and wherever it ends, light must leave as if into free space. A plain edge is a metal wall that reflects everything. An absorbing layer reflects too, for a less obvious reason: a lossy material has a different impedance from the material in front of it, so its surface acts as a mirror. In [Figure 31.6](#fig-31-6), a slab waveguide mode runs into the end of the grid. An abrupt lossy block reflects 0.4 % of the power (−24 dB) however thick it is made, which would ruin any measurement of a small reflection. Grading the loss slowly helps, because a slow change reflects little, but only once the layer is several wavelengths thick.

**Bérenger's perfectly matched layer** (PML) removes the interface reflection altogether {% include cite.html keys="berenger1994" %}. Its cleanest description is a change of coordinates {% include cite.html keys="chew1994,johnson2021pml" %}: inside the layer, the coordinate normal to the boundary is continued into the complex plane,

$$\tilde{x} = x - \frac{j}{\omega}\int_0^x\sigma(x')\,\mathrm{d}x',$$

so that a wave $$e^{-jk_xx}$$ becomes $$e^{-jk_xx}\,e^{-(k_x/\omega)\int\sigma\,\mathrm{d}x'}$$: it keeps travelling exactly as before, but decays. Because Maxwell's equations in the stretched coordinate have the same form as in the interior, the boundary between them reflects nothing, at any angle, frequency or polarisation; and because only $$x$$ is stretched, waves travelling along the layer are untouched. The wave that reaches the outer metal wall and comes back has been attenuated twice. For a loss rate graded as $$\sigma(x) = \sigma_\mathrm{max}(x/d)^m$$ in a layer of thickness $$d$$ in a medium of index $$n$$, the returning amplitude is {% include cite.html keys="taflove2005" %}

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Reflection of a PML of thickness d</div>

$$R(\theta) = \exp\!\left[-\frac{2\,n\cos\theta}{c}\,\frac{\sigma_\mathrm{max}\,d}{m + 1}\right]$$

</div>

which a code makes as small as it likes by choosing $$\sigma_\mathrm{max}$$. On a grid the layer is no longer perfect: where $$\sigma$$ rises faster than a few cells can follow, it reflects. Hence the polynomial grading ($$m \approx 2$$–3) and the need for thickness. In [Figure 31.6](#fig-31-6), a PML of 2 cells reflects 15 %, of 5 cells (0.2 µm) $$10^{-4}$$, of 12 cells $$10^{-7}$$ and of 25 cells (1 µm) $$10^{-9}$$. A scalar absorber with the same loss profile, matched only for normal incidence, needs about four times the thickness for the same reflection, because a guided mode is a superposition of waves bouncing at an angle. The factor $$\cos\theta$$ explains the PML's two weaknesses: waves that skim along it and evanescent tails are barely absorbed, so the PML must sit a fraction of a wavelength away from any structure's evanescent field; and in a medium that is not uniform along the boundary normal, such as a grating or photonic crystal running into it, the matching fails, and a thick, slowly graded absorber is the remedy {% include cite.html keys="oskooi2008" %}.

<figure id="fig-31-6">
  <img src="{{ '/assets/figs/ch31_pml.svg' | relative_url }}" style="width:680px" alt="(a) Loss against depth into a boundary layer for three absorbers: an abrupt lossy block with a constant loss starting at the interface, and a graded absorber and a PML that share the same quadratic profile. (b) Power reflected back into the guided mode against layer thickness from 0 to 6 micrometres on a log scale: the abrupt block falls from 0.7 to a floor of 0.004 beyond 1.5 micrometres; the graded absorber falls slowly from 0.15 to 1e-10 at 6 micrometres; the PML falls fastest, to 1e-4 at 0.2 micrometres, 1e-9 at 1 micrometre and about 1e-12 at 3 micrometres. A dotted line marks one guided wavelength, 0.54 micrometres.">
  <figcaption><span class="capnum">Figure 31.6.</span> <strong>Ending the grid.</strong> (a) Three absorbing layers: an abrupt block with electric loss (\(\varepsilon\) gains an imaginary part of 20 %), a graded scalar absorber with equal electric and magnetic loss (matched only at normal incidence), and a PML with the same graded profile that stretches only the coordinate normal to the boundary. (b) Power reflected into the TE0 mode of a 220 nm silicon slab (1550 nm) from each layer, against its thickness: 2D MEEP, 25 pixels per µm, reflection measured by mode decomposition and referred to a 6 µm PML. Computed by <code>figsrc/ch31_meep.py</code>. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

**Try it.** This is a 2D FDTD simulation running in your browser: the TE-like fields ($$E_x$$, $$E_y$$, $$H_z$$) of this chapter's 2D effective-index model (core 2.848 in oxide), updated cell by cell on a Yee grid inside a Bérenger PML, in a straight guide, a bend or a ring, with a continuous source or a pulse. At the default 12 cells per wavelength in silicon (45 nm cells) the straight guide's effective index comes out at 2.5115, 0.8 % above the exact 2.4917: numerical dispersion at work. Then break it on purpose. The demo defines its Courant number against the speed of light in oxide, the fastest on its grid, so its limit is exactly $$1/\sqrt{2}$$: at 0.70 the field is stable, at 0.71 a checkerboard grows by a factor of about 1.42 per step (the dispersion relation predicts 1.44) and fills the window within a few hundred steps. Turn the PML off, and the edge of the grid becomes a metal wall that reflects everything; with 4, 12 and 24 PML cells the reflection is −49, −90 and about −108 dB. Drop to 6 cells per wavelength and the effective index rises to 2.5844; in the ring, a resonance at 1585.8 nm with 12 cells moves to 1596.8 nm with 8.

{% include demos/fdtd.html %}

## <span class="secnum">31.8</span>Sources, monitors and the Fourier transform

**Sources** in FDTD are currents added to the update equations, usually as "soft" sources that add to the field rather than overwrite it, so that light returning to the source passes through. A point current is a **dipole**, the right source for emitters and for finding the resonances of a cavity. A current sheet with a Gaussian profile and a phase tilt launches a **Gaussian beam**, a model of a fibre above a grating coupler. A sheet of electric and magnetic currents shaped like a waveguide mode, computed by a mode solver at the source plane, launches that **mode** in one direction only: the electric and magnetic currents radiate together forwards and cancel backwards. This mode source is how most photonic simulations start.

**One run, many wavelengths.** A continuous source must run until the whole device has settled at one frequency; to get a spectrum you would repeat the run at every wavelength. A short **pulse** contains a band of frequencies at once, and because Maxwell's equations are linear, each frequency travels through the device independently of the others. While the simulation runs, monitors accumulate the Fourier transform of the field at the wavelengths of interest,

$$\tilde{\mathbf{E}}(\mathbf{r}, \omega) = \sum_n \mathbf{E}(\mathbf{r}, n\Delta t)\,e^{-j\omega n\Delta t}\,\Delta t,$$

a running sum that costs one multiplication per point, frequency and step. Divided by the transform of the source pulse, the result is the response at every wavelength in the pulse's band, from one simulation. [Figure 31.7](#fig-31-7) checks this on a sidewall Bragg grating. A Gaussian pulse 95 fs long (full width at half maximum of its intensity) spans 1480–1620 nm, and one run gives the transmission and reflection spectra. Separate continuous-wave runs at five single wavelengths agree: at 1550 nm, in the stop band, they give 0.254 against the pulse's 0.254; outside it they agree within 3 %, which is as well as they agree with themselves, since near the band edges the light keeps ringing between the grating's ends and the continuous-wave values still drift by a few per cent between 400 and 1600 µm/c (1.3 and 5.3 ps). Each continuous-wave point, run long enough to settle, cost more than the whole pulsed spectrum.

<figure id="fig-31-7">
  <img src="{{ '/assets/figs/ch31_pulse.svg' | relative_url }}" style="width:680px" alt="(a) Top view of the start of a sidewall Bragg grating whose width alternates between 450 and 550 nanometres with a 310 nanometre period, with the pulsed mode source and the reflection monitor on the input side and the transmission monitor on the output side. (b) The source current against time: a carrier under a Gaussian envelope peaking near 290 femtoseconds, and inset its spectrum, a peak spanning about 1450 to 1650 nanometres. (c) Power against wavelength from 1480 to 1620 nanometres: transmission near 1 outside a stop band centred near 1552 nanometres where it dips to 0.25, and reflection rising to 0.66 there; open circles from continuous-wave runs at five wavelengths lie on the transmission curve.">
  <figcaption><span class="capnum">Figure 31.7.</span> <strong>One pulsed run gives the whole spectrum.</strong> (a) A grating of 60 periods whose width alternates between 450 and 550 nm (310 nm period), in a 2D effective-index top view (core 2.848 in oxide), TE-like light; to scale. (b) The current of the pulsed mode source in time (MEEP's Gaussian source), and its spectrum. (c) Transmission and reflection from one pulsed run (Fourier-transform mode monitors, normalised to a run without the grating), and the transmission from continuous-wave runs at single wavelengths (circles: power through the output plane averaged over one period after 1600 µm/c, normalised to the same without the grating; bars: the spread of the values after 400, 800, 1200 and 1600 µm/c). MEEP, 30 pixels per µm. Computed by <code>figsrc/ch31_meep.py</code>. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

A pulse has a price: the frequency resolution of a Fourier transform is the inverse of the time it covers, so the run must last until the fields have died away. The grating needed 550 µm/c (1.8 ps) for its fields to fall to $$10^{-7}$$, against 300 µm/c without it, because light rings in its band edges. A ring resonator with an intrinsic $$Q$$ of $$10^5$$ stores light for $$\tau = Q/\omega = 82$$ ps at 1550 nm, and an FDTD run would have to last several times that; such resonances are better extracted from a short run by fitting decaying sinusoids to the time signal (harmonic inversion), or modelled with coupled-mode theory (Section 31.12).

**Monitors** record what the simulation is for:

- **Fourier-transform field monitors** store $$\tilde{\mathbf{E}}$$ and $$\tilde{\mathbf{H}}$$ on a plane or volume at chosen wavelengths: field maps such as [Figure 31.9](#fig-31-9), or the field above a grating to overlap with a fibre mode (Lab 6).
- **Flux monitors** integrate the Poynting vector, $$\tfrac{1}{2}\mathrm{Re}(\tilde{\mathbf{E}}\times\tilde{\mathbf{H}}^*)$$, over a plane: the power through it at each wavelength, regardless of its form.
- **Mode-expansion monitors** project the fields on a plane onto the modes of the waveguide there, separating forward from backward and one mode from another: the S-parameters of a device, mode by mode. Every FDTD reflection and transmission in this chapter's figures, except the continuous-wave points of Figure 31.7, was measured this way.
- **Time monitors** record the field at a point, for harmonic inversion of resonances or to decide when to stop.

Transmissions are normalised by a second run without the device, and a simulation should stop on a criterion (fields decayed below a set fraction at a monitor), not after a fixed time.

## <span class="secnum">31.9</span>Materials, meshes and symmetry

**Dispersive materials.** In the time domain a permittivity that depends on frequency is a memory: the polarisation now depends on the field a moment ago. FDTD handles this by fitting the material's $$\varepsilon(\omega)$$ over the band with a few **Lorentz** terms (and **Drude** terms, with $$\omega_k = 0$$, for metals and free carriers),

$$\varepsilon(\omega) = \varepsilon_\infty + \sum_k\frac{\Delta\varepsilon_k\,\omega_k^2}{\omega_k^2 - \omega^2 + j\omega\gamma_k},$$

and stepping, alongside the fields, the polarisation of each term, which obeys an oscillator equation $$\ddot{\mathbf{P}}_k + \gamma_k\dot{\mathbf{P}}_k + \omega_k^2\mathbf{P}_k = \varepsilon_0\Delta\varepsilon_k\omega_k^2\mathbf{E}$$: an **auxiliary differential equation** {% include cite.html keys="taflove2005" %}. A fit that is poor somewhere in the pulse's band, or has a pole inside it, gives wrong results or an unstable run, so the fit should be plotted against the data before it is trusted. Often a constant index is enough for amplitudes, but not for group delays: in Lab 6, MEEP's non-dispersive silicon gives the 220 nm slab a group index of 3.58, against 3.70 with silicon's dispersion included. Gain, saturable absorption and Kerr nonlinearity enter the same way, as extra equations for the polarisation.

**Staircases and subpixel averaging.** FDTD faces the same problem at walls as the mode solver of Section 31.2. If every pixel takes one material, a wall moves by up to half a pixel as the grid changes, and curved or slanted walls become staircases ([Figure 31.8a](#fig-31-8)). The effective index of the 220 nm slab then jumps by up to ±0.05 even at 40 pixels per µm (25 nm cells), and does not settle as the grid is refined ([Figure 31.8b, c](#fig-31-8)). **Subpixel averaging** gives each pixel that a wall crosses an effective permittivity, the arithmetic mean for field components along the wall and the harmonic mean for the component across it, oriented with the local normal; done this way the error becomes second order and smooth {% include cite.html keys="farjadpour2006" %}. MEEP does it by default. Conformal methods, which modify the update equations of the cells a wall cuts, achieve the same in other codes.

<figure id="fig-31-8">
  <img src="{{ '/assets/figs/ch31_subpixel.svg' | relative_url }}" style="width:680px" alt="(a) The same curved silicon wall drawn twice on a grid of 7 by 4 pixels: as a staircase, each pixel all silicon or all oxide, and averaged, the pixels the wall crosses shaded in between. (b) Effective index of the TE0 mode of a 220 nm silicon slab against pixels per micrometre from 10 to 120, against the exact value 2.8482: the staircase values swing between 2.71 and 3.00 at low resolution and still by up to 0.02 at 80 to 120; the averaged values, after a few erratic points below 20, fall steadily to within 0.001 of the exact value. (c) The same for TM0, exact 2.0536, with the staircase errors larger.">
  <figcaption><span class="capnum">Figure 31.8.</span> <strong>Staircase against subpixel averaging.</strong> (a) A curved wall on a grid. (b, c) Effective index of the 220 nm silicon slab in oxide at 1550 nm in 2D FDTD, from the frequency of its mode at a fixed wavenumber (Bloch-periodic cell, harmonic inversion), against the exact slab solution ([Chapter 5]({% link chapters/05_slab.md %})); the slab is offset by 13 nm from the grid. With averaging the error falls steadily, with small bumps, once the film is a few pixels thick (it is positive, because of numerical dispersion); without it, the error depends on where the walls fall between pixels. MEEP, Courant number 0.5. Computed by <code>figsrc/ch31_meep.py</code>. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

**Non-uniform meshes.** Silicon needs small cells, oxide and air larger ones, and thin layers or narrow gaps smaller still. A graded mesh, fine where the index is high or the geometry small and coarse elsewhere, saves cells. Two cautions: the Courant limit is set by the *smallest* cell, so one region of 2 nm cells shortens the time step for the whole grid; and cells should grow gradually (by no more than about 20–30 % from one to the next), because an abrupt change of cell size reflects light, like an abrupt change of index.

**Symmetry.** If the structure and the source are both symmetric about a plane, the fields are even or odd about it, and only half the grid needs to be simulated, with a magnetic or electric "wall" on the plane. A straight grating coupler fed by the TE0 mode has one such plane (through the waveguide axis, vertical); a symmetric MMI fed in its centre has one; a structure symmetric in two planes, with a source to match, needs only a quarter of the grid. Symmetry halves memory and time but must be real: an off-centre input, a tilted fibre in the wrong plane or a fabrication asymmetry breaks it. **Periodic** and **Bloch-periodic** boundaries do the same for repeated structures: one unit cell, with the field on one side equal to the field on the other times a phase $$e^{-jk\Lambda}$$, gives the band structure of a grating or photonic crystal, as in [Figure 31.8](#fig-31-8).

## <span class="secnum">31.10</span>Convergence and cost

**A convergence study** changes one numerical parameter at a time and watches the number that matters: the resolution, the thickness of the PML and its distance from the structure, the size of the mode source and monitors, the decay threshold that stops the run. [Figure 31.9](#fig-31-9) does it for the loss of a 1 µm bend in the same 2D model as the taper: 0.76 dB at 10 pixels per µm, and 0.91 ± 0.02 dB from 40 pixels per µm on, with or without averaging. (That is 81 % in the output guide's fundamental mode. The demo of Section 31.7 counts all the power through the output of the same 1 µm bend, 88 %, part of which the junctions have converted into the guide's second, odd mode: always check what a "transmission" includes.) Different quantities converge at different rates. Losses, splitting ratios and bandwidths settle quickly; absolute phases and resonance wavelengths, which carry the numerical dispersion of Section 31.6, settle slowly. In Lab 6's grating coupler, refining the grid from 20 to 100 pixels per µm moved the peak wavelength by 24 nm but the 1 dB bandwidth by 3 nm.

<figure id="fig-31-9">
  <img src="{{ '/assets/figs/ch31_bend.svg' | relative_url }}" style="width:680px" alt="(a) and (b) Snapshots of the real part of the magnetic field at 1550 nanometres in 90 degree waveguide bends of radius 1 and 2 micrometres, light entering from the left and leaving upwards: in the 1 micrometre bend, wavefronts spill outwards from the outer edge of the bend, with a loss of 0.89 decibels; in the 2 micrometre bend little light escapes, 0.16 decibels. (c) Loss of the 1 micrometre bend against pixels per micrometre from 10 to 80, with and without subpixel averaging, rising from 0.76 and 0.69 decibels at 10 to about 0.91 decibels from 40 on.">
  <figcaption><span class="capnum">Figure 31.9.</span> <strong>A 2D FDTD simulation and its convergence.</strong> (a, b) Real part of \(H_z\) at 1550 nm (TE-like light, in-plane \(\mathbf{E}\)) in 90° bends of 500 nm guides with radii 1 and 2 µm, from the Fourier transform of one pulsed run at 40 pixels per µm; the tighter bend sheds light outwards. Loss: power in the output guide's fundamental mode against the input's. (c) The loss of the 1 µm bend against resolution. 2D effective-index model, core 2.848 in oxide; MEEP. Computed by <code>figsrc/ch31_meep.py</code>. Drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

**How the cost scales.** Memory is proportional to the number of cells, $$V/\Delta x^3$$ in 3D. The number of steps is the simulated time divided by $$\Delta t$$, and the Courant limit ties $$\Delta t$$ to $$\Delta x$$. So

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">FDTD cost</div>

$$\text{memory} \propto \frac{V}{\Delta x^3}, \qquad \text{run time} \propto \frac{V}{\Delta x^3}\cdot\frac{T}{\Delta t} \propto \frac{V\,T}{\Delta x^4}\quad\text{(3D)}$$

</div>

Halving the cell size multiplies the memory by 8 and the run time by 16 in 3D (by 4 and 8 in 2D). To turn these proportions into numbers, a small 3D silicon-waveguide run in MEEP was timed and its memory measured on one core of the machine used for this chapter: about 160 bytes per cell (double precision, with its PML) and 56 million cell updates per second.

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 31.3 · A 3D grating coupler before you press run</div>

A grating coupler about 12 µm long and 12 µm wide, with its input waveguide, the silicon substrate, a 2 µm buried oxide and room above for the fibre's beam, fits in a box 20 × 16 × 6 µm; with a 1 µm PML on every side the grid covers 22 × 18 × 8 µm. Lab 6 found the 2D version converged at about 60 pixels per µm; take 50 (20 nm cells). Then:

- **cells:** $$1100 \times 900 \times 400 = 3.96\times10^8$$;
- **time step:** $$\Delta t \le \Delta x/(c\sqrt{3}) = 0.038$$ fs; at $$S = 0.5$$, $$\Delta t = 10\ \mathrm{nm}/c = 0.033$$ fs;
- **simulated time:** a pulse covering 1450–1650 nm lasts about 120 µm/c, light needs roughly as long again to cross the grating and leave, and the fields must then decay: about 300 µm/c, or 1 ps, which is **30 000 steps**;
- **memory:** $$3.96\times10^8 \times 160$$ bytes $$\approx$$ **63 GB**;
- **work:** $$3.96\times10^8 \times 30\,000 = 1.2\times10^{13}$$ cell updates; at $$5.6\times10^7$$ per second, $$2.1\times10^5$$ s, or **about 60 core-hours**: two and a half days on one core, about an hour on 64 cores if the code scales perfectly.

The mirror plane through the waveguide axis halves both (32 GB, 30 core-hours). At 30 pixels per µm the run needs 14 GB and 8 core-hours, but, judging by Lab 6's 2D runs, its peak wavelength would be about 9 nm off. The same grating as a 2D side view, as in Lab 6, has $$1100 \times 400 = 4.4\times10^5$$ cells, 900 times fewer, and runs in minutes. This is why grating couplers are designed in 2D and only checked in 3D ([Figure 31.10](#fig-31-10)), and why 3D runs go to clusters or to graphics-card solvers in the cloud ([Chapter 32]({% link chapters/32_simtools.md %})).

</div>

<figure id="fig-31-10">
  <img src="{{ '/assets/figs/ch31_cost.svg' | relative_url }}" style="width:640px" alt="Two log-log plots against pixels per micrometre from 10 to 100. (a) Memory: the 3D grating coupler rises from 0.5 GB at 10 pixels per micrometre to 500 GB at 100, crossing 16 GB near 32; with one mirror plane it is half that; the 2D side view stays below 0.2 GB. (b) Run time in core-hours: 3D rises from about 0.1 to 1000, crossing one core-day near 40 pixels per micrometre; with a mirror plane half that; the 2D side view stays below one core-hour. Dotted lines mark 20 nanometre cells, 16 GB and one core-day.">
  <figcaption><span class="capnum">Figure 31.10.</span> <strong>The cost of FDTD against resolution</strong> for the grating coupler of Worked Example 31.3: memory grows as the cube of the resolution, run time as the fourth power in 3D (the square and cube in 2D). Estimates from a measured 160 bytes per cell and 5.6 × 10⁷ cell updates per second on one core (MEEP, 3D, double precision), 300 µm/c of simulated time; the 2D curves assume half the bytes per cell. Computed and drawn by <code>figsrc/ch31_figs.py</code> from <code>figsrc/ch31_meep.py</code> (cost).</figcaption>
</figure>

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Numbers that look converged but are not</div>

- **The PML too close.** An evanescent tail or a radiating beam that reaches the PML at grazing incidence is partly reflected: keep at least half a wavelength between any structure and the PML.
- **Monitors and sources inside the PML, or across a bend.** A mode source or monitor must sit on a straight, uniform piece of waveguide, wide enough to contain the mode's tails.
- **Stopping too early.** A run stopped before the fields decay gives Fourier transforms with ripples and transmissions above 100 %.
- **Wavelengths outside the pulse.** Dividing by a source spectrum that is nearly zero amplifies noise: keep monitor wavelengths inside the pulse's band.
- **2D numbers compared with 3D measurements**, and constant-index materials used for group delays.
- **Absolute wavelengths from a coarse grid** (Worked Example 31.2).

</div>

## <span class="secnum">31.11</span>2D, 2.5D and frequency-domain solvers

**2D FDTD** assumes that nothing changes along one axis. The fields then split into two independent sets, ($$E_z$$, $$H_x$$, $$H_y$$) and ($$H_z$$, $$E_x$$, $$E_y$$), and the grid shrinks by a factor of several hundred. A 2D model is exact for a structure that really is uniform in one direction and a fair one in two cases. A **side view** along a wide device is one: Lab 6 models a 12 µm wide grating coupler by its cut along the waveguide. A **top view** of a planar chip is the other, provided the vertical direction is folded into an effective index, which is the subject of the next paragraph.

**2.5D, or variational, FDTD.** A silicon chip is a film 220 nm thick, etched in some places. At every point of the top view, the film and its claddings form a vertical slab with its own TE0 mode and effective index: 2.848 where the film is full, 2.104 where a 90 nm slab remains, and the cladding's index where it is etched through ([Chapter 6]({% link chapters/06_soi.md %})). Replacing the 3D structure by this 2D map of effective indices and running 2D FDTD on it is the effective-index method applied to a whole device ([Figure 31.11a](#fig-31-11)). The *variational* version keeps one reference vertical profile $$F(z)$$, that of the unetched film, assumes it everywhere, $$\mathbf{E}(x, y, z) \approx F(z)\,\mathbf{e}(x, y)$$, and derives the in-plane permittivity from a variational form of Maxwell's equations {% include cite.html keys="hammer2009" %}:

$$\varepsilon_\mathrm{eff}(x, y) = n_\mathrm{I}^2 + \frac{\int\left[\varepsilon(x, y, z) - \varepsilon_\mathrm{ref}(z)\right]F^2\,\mathrm{d}z}{\int F^2\,\mathrm{d}z}.$$

Where the film is present this gives $$n_\mathrm{I}^2$$; elsewhere it subtracts the part of the slab mode that has lost its silicon. For the 220 nm film, 81 % of $$\int F^2$$ lies in the silicon, so a fully etched region gets $$\varepsilon_\mathrm{eff} = 2.848^2 - 0.81(3.476^2 - 1.444^2) \approx 0.01$$, far below the oxide's 2.09: the 2D model sees an etched trench as almost a wall, a sign of how far the single-profile assumption is stretched there. Some commercial tools implement this method under the name varFDTD ([Chapter 32]({% link chapters/32_simtools.md %})).

<figure id="fig-31-11">
  <img src="{{ '/assets/figs/ch31_varfdtd.svg' | relative_url }}" style="width:680px" alt="(a) Left: cross-section of a rib waveguide, a 220 nm silicon ridge on a 90 nm slab between oxide layers, with the vertical mode profile in the ridge (red) and in the slab (amber), giving effective indices 2.848 and 2.104. An arrow leads to a top view: a ring and a bus waveguide in red on an amber background, the 2D map of effective indices on which a 2D FDTD runs. (b) The error of the effective-index method, its effective index minus the 3D mode solver's, against waveguide width from 0.3 to 1.2 micrometres on a log scale: for a strip it falls from 0.19 at 0.3 micrometres to 0.046 at 0.5 and 0.003 at 1.2; for a rib with a 90 nm slab from 0.07 to 0.033 and 0.004; for a rib with a 150 nm slab from 0.025 to 0.018 and 0.003.">
  <figcaption><span class="capnum">Figure 31.11.</span> <strong>Collapsing the vertical direction.</strong> (a) The effective-index (2.5D) idea: solve the vertical slab at each point of the chip, then simulate the top view as a 2D map of effective indices. (b) How well it works: TE0 effective index from the 2D (effective-index) model minus that of a 3D full-vector mode solver (the FDE of Figure 31.2, 10 nm grid), for 220 nm silicon strips and ribs at 1550 nm. The error is smallest where the vertical profile changes least across the guide: wide guides and shallow etches. Computed by <code>figsrc/ch31_figs.py</code> and <code>figsrc/ch31_fde.py</code>; drawn by <code>figsrc/ch31_figs.py</code>.</figcaption>
</figure>

**When it works, and when it does not.** The approximation is good when one slab mode dominates and the vertical profile changes little across the device: wide guides, shallow-etched ribs, MMIs, the free-propagation regions of arrayed-waveguide gratings, large rings. [Figure 31.11b](#fig-31-11) puts numbers on it: at 1 µm width the effective index is within 0.006 of the 3D value for strips and ribs alike; at 0.5 µm it is 0.046 too high for a strip, 0.033 for a 90 nm-slab rib and 0.018 for a 150 nm-slab rib; at 0.3 µm the strip is off by 0.19. Errors in coupling are larger than errors in index, because coupling depends on the evanescent tail, which the method gets wrong at the sidewalls: Lab 3 finds the effective-index cross-over length of a directional coupler 1.5 times too short. The method cannot represent what leaves the plane, such as a grating coupler's upward beam or leakage into the substrate, nor coupling between layers (silicon nitride over silicon), nor conversion between TE and TM. Use it for fast exploration, then confirm the final design in 3D.

**Frequency-domain FDTD (FDFD).** The Yee grid can also be used at a single frequency. Replacing $$\partial/\partial t$$ by $$j\omega$$ turns the two curl equations into one sparse linear system, $$\left(\nabla\times\nabla\times{} - k_0^2\varepsilon_r\right)\mathbf{E} = -j\omega\mu_0\mathbf{J}$$, solved once per wavelength. In 2D a direct sparse solver handles $$10^5$$–$$10^6$$ unknowns in seconds, and the frequency-domain form has advantages: a resonance is no slower to compute than anything else, $$\varepsilon(\omega)$$ is used exactly at each wavelength, and the gradient of any result with respect to every pixel's permittivity costs one more solve (the adjoint method behind inverse design). In 3D the system is too large for direct solvers and converges slowly with iterative ones, and the choice of PML formulation affects how slowly {% include cite.html keys="shin2012" %}, which is why 3D photonics usually stays in the time domain. Finite-element solvers in the frequency domain share these properties with meshes that follow curved surfaces.

## <span class="secnum">31.12</span>Semi-analytic, circuit and multiphysics solvers

**Coupled-mode theory and transfer matrices** are solvers too, with almost nothing discretised. Coupled-mode theory expands the field in a handful of known modes and reduces Maxwell's equations to a few ordinary differential equations for their amplitudes, with coupling coefficients computed from overlap integrals of mode-solver fields: two modes for a directional coupler ([Chapter 9]({% link chapters/09_couplers.md %})), a forward and a backward mode for a Bragg grating ([Chapter 13]({% link chapters/13_bragg.md %})), and an amplitude in time for a resonator ([Chapter 12]({% link chapters/12_rings.md %})) {% include cite.html keys="yariv1973" %}. Transfer matrices treat a structure as a chain of uniform pieces, each a 2 × 2 matrix, which is exact for thin-film stacks and for gratings described by effective indices ([Lab 5]({% link labs/lab05_bragg.md %})). Both run in microseconds, give formulas that show how the answer depends on each parameter, and are the natural place for sweeps, tolerances and fitting to measurements. They are only as good as their inputs and their assumptions (few modes, weak coupling, no radiation), which is why their coefficients are best taken from, and their results checked against, a field solver.

**Circuit solvers.** A circuit of tens or thousands of components is beyond any field solver. Each component becomes a compact model, its S-matrix as a function of wavelength, and a circuit solver connects them according to the netlist ([Chapter 30]({% link chapters/30_flow.md %})). In the frequency domain this is linear algebra at each wavelength, as SAX does in [Lab 4]({% link labs/lab04_sax.md %}) {% include cite.html keys="sax" %}. In the time domain, needed for modulated signals, lasers and nonlinear or active elements, each component's response is turned into a digital filter (or, for a laser, rate equations) and a sampled signal is stepped through the circuit. Circuit simulation is only as good as the compact models, so the models are fitted to field simulations and then to measurements.

**Multiphysics.** Active devices need more than Maxwell's equations, and the usual approach is a chain of solvers, each passing its result to the next.

- **Charge.** Modulators and photodiodes are solved with the semiconductor drift-diffusion equations: Poisson's equation for the potential, and continuity equations for electrons and holes with their drift, diffusion, generation and recombination. For a PN-junction modulator, the carrier densities at each bias become a change of index and absorption through the plasma-dispersion relations {% include cite.html keys="soref1987" %}, which a mode solver turns into a phase shift and loss per length ([Chapter 19]({% link chapters/19_eo.md %})). For a photodiode, the optical field from FDTD or a mode solver gives the generation rate, and the charge solver gives the current, responsivity and bandwidth ([Chapter 21]({% link chapters/21_pd.md %})).
- **Heat.** A heater's power and the stack's thermal conductivities give a temperature map from the heat equation, which the thermo-optic coefficient turns into an index map for the mode solver; a transient solve gives the time constant ([Chapter 18]({% link chapters/18_thermal.md %})). femwell solves both the heat and the mode problem on the same mesh.

## <span class="secnum">31.13</span>Choosing a method

**Table 31.1. Photonic solvers at a glance.** $$N$$ grid points per dimension, $$M$$ modes, $$S_c$$ distinct cross-sections, $$N_t$$ time steps.
{: .tabcaption #tab-31-1 }

| Method | Dimensions | Domain | Best for | Cost scales as | Pitfalls |
|---|---|---|---|---|---|
| Mode solver (FDE, FEM) | 2D cross-section | frequency (eigen) | $$n_\mathrm{eff}$$, $$n_g$$, fields, overlaps, leakage, bend loss | $$N^2$$ unknowns, sparse | staircased walls, window too small, PML modes |
| EME | 2D or 3D, via modes | frequency | long devices that change slowly or in steps: tapers, MMIs, couplers, gratings | $$S_c \cdot M^3$$; length nearly free | radiation, too few modes or sections, power balance |
| BPM | 2D or 3D, marched | frequency | weakly guiding, gently varying devices | $$N^2$$ per step | paraxial, one-way: no reflections, wide angles |
| 2D FDTD | 2D (side or top view) | time | grating couplers (side view), first designs | $$N^3$$ (cells × steps) | real devices are 3D |
| 2.5D (varFDTD) | 2D with vertical profile | time | planar devices with one slab mode: MMIs, ribs, rings | as 2D | narrow strips, vertical emission, layer coupling |
| 3D FDTD | 3D | time, broadband | any geometry; final verification | $$N^4$$ (cells × steps) | memory, run time, numerical dispersion |
| FDFD, frequency-domain FEM | 2D or 3D | one frequency | resonators, inverse design (adjoint), dispersive media | sparse solve per λ | 3D too large for direct solvers |
| CMT, transfer matrices | 1D or a few modes | frequency or time | gratings, couplers, rings, sweeps, fitting | microseconds | assumptions; coefficients from a field solver |
| Circuit (S-parameters) | netlist | frequency or time | systems of many components | number of components | only as good as the compact models |
| Charge, heat | 2D or 3D | static or transient | modulators, detectors, heaters | like FEM | coupling back to optics by hand |

The order of work follows from the table: a mode solver first, for the waveguides; EME or 2D/2.5D FDTD to explore a device; 3D FDTD to confirm the final version; compact models from the converged results; and a circuit solver for everything joined together.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

For the openEBL chip of [Chapter 30]({% link chapters/30_flow.md %}): the strip waveguide's $$n_\mathrm{eff}$$ and $$n_g$$ from a mode solver (Lab 2); the directional couplers' cross-over lengths from supermodes (Chapter 9), checked by EME or 3D FDTD with their bends; the Bragg gratings from coupled-mode theory with a coupling coefficient taken from FDTD of a few periods; the grating couplers from the PDK's measured model, or from 2D FDTD (Lab 6) if you design your own; and the MZIs and rings from SAX (Lab 4). Expect the absolute wavelengths of rings and gratings to differ from any simulation by a few nanometres, because the fabricated widths and thicknesses do ([Chapter 6]({% link chapters/06_soi.md %})).

</div>

## Reading

{% include reflist.html keys="taflove2005,yee1966,meep,berenger1994,chew1994,johnson2021pml,oskooi2008,farjadpour2006,zhu2002,fallahkhair2008,femwell,bienstman2001,gallagher2003,feit1978,kawano2001,hammer2009,shin2012,sax" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Every solver discretises space, picks the frequency or the time domain, and decides which dimensions to keep; its answer belongs to the discretised device until a convergence study says otherwise.
- Mode solvers turn a cross-section into a sparse eigenproblem; averaging the permittivity at walls makes them accurate (the 500 × 220 nm strip to within 0.0003 on a 10 nm grid).
- EME is exact inside each uniform section and cheap for long devices, since length costs almost nothing; it struggles with radiation and needs enough modes and sections.
- FDTD staggers E and H in space and time (the Yee grid), which makes it simple, explicit and second-order accurate; it is stable only for $$S \le 1/\sqrt{3}$$ in 3D, and its waves are slow by about $$(\pi/N)^2/6$$ along an axis.
- A PML absorbs without reflecting by stretching the coordinate normal to the boundary; on a grid it needs grading and about 10–25 cells.
- One pulsed run gives a whole spectrum through Fourier-transform monitors; sharp resonances need long runs or harmonic inversion.
- 3D FDTD costs memory ∝ $$\Delta x^{-3}$$ and time ∝ $$\Delta x^{-4}$$: a 3D grating coupler at 20 nm needs about 63 GB and 60 core-hours, its 2D side view minutes.
- 2.5D FDTD folds the vertical direction into an effective index: good for wide guides and shallow etches, poor for narrow strips, coupling gaps and anything that leaves the plane.

</div>
