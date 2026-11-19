---
title: "Lab 2. Mode solving with femwell"
parent: Hands-On Labs
nav_order: 2
permalink: /labs/lab-02/
---

# <span class="chapnum">Lab 2 · Simulate</span>Mode Solving with femwell

Mesh the cross-section of a silicon strip, solve Maxwell's equations on it with the open finite-element solver femwell, and reproduce Table 6.1; then sweep the width against Lab 1's effective-index method, take the group index from a wavelength derivative, and measure how much light leaks through the buried oxide.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- describe a waveguide cross-section as polygons and mesh it;
- solve for its full-vectorial modes, and tell TE-like from TM-like modes by their TE fraction;
- sweep the width, find where TE1 appears and measure the error of the effective-index method;
- compute the group index from a wavelength derivative, for a strip and a rib;
- put the silicon handle below a finite buried oxide and compute the substrate leakage of Chapter 7.

</div>

## What you need

- [Chapter 6]({% link chapters/06_soi.md %}) (Sections 6.2 to 6.5) and [Chapter 7]({% link chapters/07_loss.md %}) (Section 7.4); [Lab 1]({% link labs/lab01_slab.md %}) helps.
- Python 3.11 or newer with femwell, NumPy and Matplotlib: `pip install femwell matplotlib`. femwell brings the finite-element library scikit-fem, the mesher gmsh and shapely. On Linux, gmsh needs three system libraries: `sudo apt install libglu1-mesa libxft2 libxinerama1`, or in a conda environment `conda install -c conda-forge libglu xorg-libxft xorg-libxinerama`. Tested with Python 3.12, femwell 0.1.12, scikit-fem 12.0.2, gmsh 4.15.2, shapely 2.2.0, NumPy 2.4.6 and Matplotlib 3.11.2.
- The script <a href="{{ '/labs/lab02_femwell.py' | relative_url }}" download><code>lab02_femwell.py</code></a> (also in the repository's [`labs/` folder](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs)).
- About two hours, including the exercises.

Run it from a terminal in the folder where you saved it:

```
python lab02_femwell.py
python lab02_femwell.py --quick
```

It prints a checkpoint for each part below, with the value from the chapter beside it, and saves the figure `lab02_femwell.png`. It solves 23 cross-sections, from one to several seconds each, so the solving takes about a minute on a recent computer (65 s on ours, with four threads; the script prints its own time) and several times longer on a slow or busy one; `--quick` sweeps five widths instead of twelve and skips the slowest solve. Read each part, then the matching function in the script; change things and run it again. All lengths are in micrometres.

This is the solver behind the numbers of Chapter 6: the script follows `figsrc/femwell_modes.py` in the repository, which made Table 6.1 and Figure 6.1, with a slightly coarser mesh and a smaller window so that it runs quickly.

## <span class="secnum">L2.1</span>Mesh the cross-section and solve

femwell works on a triangular mesh of the cross-section. `cross_section` describes the waveguide as rectangles from shapely, in priority order (where two overlap, the first wins), and femwell's `mesh_from_OrderedDict` hands them to gmsh, which meshes every region and names it:

```python
polys = OrderedDict(core=box(-width / 2, 0, width / 2, t))
sizes = {"core": {"resolution": res, "distance": 0.6}}
if slab > 0:
    polys["slab"] = box(-half_w, 0, half_w, slab)
polys["clad"] = box(-half_w, t / 2 - half_h, half_w, t / 2 + half_h)
mesh = from_meshio(mesh_from_OrderedDict(polys, sizes, default_resolution_max=0.25))
```

The triangles are 50 nm in the silicon and within 0.6 µm of it, where the field changes fastest, and grow to 250 nm far away. The window is 4 µm wide and 3.2 µm tall; its edges act as walls, so it must be large enough for the field to have died away before them (Section 6.3). `solve` then gives every triangle its permittivity, with the Sellmeier indices of Lab 1 for silicon and oxide, and asks femwell for the modes:

```python
basis0 = Basis(mesh, ElementTriP0())                    # one value per triangle
epsilon = basis0.zeros() + n_ox(lam) ** 2
epsilon[basis0.get_dofs(elements="core")] = n_si(lam) ** 2
modes = compute_modes(basis0, epsilon, wavelength=lam, num_modes=num, order=2)
```

`compute_modes` solves the full vectorial wave equation for the transverse and longitudinal electric field, with second-order elements, as an eigenvalue problem for $$\beta^2$$. Each mode comes back with its effective index and its **TE fraction**, the share of $$\lvert E_x\rvert^2$$ in $$\lvert E_x\rvert^2 + \lvert E_y\rvert^2$$: close to 1 for a TE-like mode, whose electric field is horizontal, and close to 0 for a TM-like one. `solve` keeps only the modes above the oxide index, the guided ones, and `pick` finds the first or second TE-like or TM-like mode among them.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

At 1550 nm, $$n_\mathrm{Si} = 3.4764$$ and $$n_\mathrm{ox} = 1.4440$$, and the mesh has 1464 triangles. The 500 × 220 nm strip guides TE0 with $$n_\mathrm{eff} = 2.4459$$ and a TE fraction of 0.983, and TM0 with 1.7708 and 0.044 (Table 6.1: 2.446 and 1.771). A third mode, TE1, has $$n_\mathrm{eff} = 1.4929$$, only 0.049 above the oxide (Chapter 6: 1.49), and a TE fraction of 0.70: so close to cut-off, much of its field is in the oxide, where it is less purely horizontal.

</div>

Panels (a) and (b) of the figure are femwell's own intensity plots of the two modes. TE0 sits inside the silicon; TM0 spreads above and below it, because its electric field is vertical and jumps by $$n_\mathrm{Si}^2/n_\mathrm{ox}^2 = 5.8$$ outwards across the top and bottom faces, like the slot mode of Section 6.1.

## <span class="secnum">L2.2</span>Sweep the width, and the effective-index method

The script solves twelve widths from 250 to 800 nm, three modes each, and beside every one it prints the effective-index method of Lab 1, copied into the script as `slab_modes` and `eim` (with the Sellmeier indices, so it gives 2.4919 where Lab 1, with $$n_\mathrm{Si} = 3.476$$, gave 2.4914). TE1 counts as guided once it is 0.001 above the oxide index.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

TE0 rises from 1.6024 at 250 nm to 2.6893 at 800 nm, and TM0 from 1.5421 to 1.9068 (Figure 6.1). TE1 is not guided at 400 nm and is guided at 450 nm, at 1.4477, so it appears between the two (Chapter 6: about 450 nm). The EIM gives 2.492 at 500 nm against femwell's 2.446, and TE1 from 316 nm (Chapter 6: 2.49 and about 320 nm). The EIM's error falls from 0.226 at 250 nm to 0.011 at 800 nm.

</div>

Panel (c) shows both, and the two errors of Section 6.2. The EIM's TE0 is too high everywhere, most for narrow strips, and its TE1 appears 85 to 135 nm too early: the lateral slab it builds, with a core of 2.85 against oxide, confines more than the real strip does. TE1 overtakes TM0 between 650 and 700 nm; where curves come this close, the TE fraction tells you which mode is which.

## <span class="secnum">L2.3</span>Group index from a wavelength derivative

The group index needs the effective index at neighbouring wavelengths (Section 6.3), with the materials' indices at those wavelengths too. `group_index` solves the strip at 1540 and 1560 nm and takes a central difference:

```python
lo, hi = solve(width, lam - dl, **kw), solve(width, lam + dl, **kw)
...
out[pol] = (n1, n1 - lam * (n2 - n0) / (2 * dl))
```

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

TE0 $$n_g = 4.18$$ and TM0 $$n_g = 3.74$$ (Table 6.1: 4.18 and 3.74). An MZI with $$\Delta L = 100$$ µm then has FSR = $$\lambda^2/(n_g\Delta L) = 5.74$$ nm (Worked Example 6.1: 5.7 nm).

</div>

TE0's group index is 1.7 times its effective index: the effective index falls fast with wavelength, because a longer wavelength pushes more of the field into the oxide. Here, unlike in Lab 1's slab, TM0 has the lower group index. Narrowing the film to a 500 nm strip makes TE0's index depend steeply on the width, as panel (c) shows, and so on the wavelength too: its group index rises from the slab's 3.70 to 4.18. TM0, whose index changes little with width and whose power is largely in the oxide, falls from 3.96 to 3.74.

## <span class="secnum">L2.4</span>A rib

The same functions solve a rib: `solve(0.5, slab=0.09)` adds a 90 nm silicon slab across the whole window, meshed a little more coarsely than the core. `group_index` takes the slab along.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

The 500 nm rib etched to a 90 nm slab has TE0 $$n_\mathrm{eff} = 2.5683$$ and $$n_g = 3.89$$ (Table 6.1: 2.568 and 3.89). The EIM gives 2.600, as in Lab 1: 0.032 too high, against 0.046 for the strip.

</div>

`group_index` reports only TE0 for the rib. Ask for four modes and the other three are not the rib's: they are TE modes of the 90 nm slab itself, spread across the whole window, at 2.113, 2.061 and 2.025, around the slab's own index of 2.104 (Lab 1's $$n_\mathrm{II}$$). In a real wafer the slab extends for millimetres and these become a continuum; the rib's TM-like mode lies below them all, so it can couple into that continuum and leak away sideways. The rib's group index is lower than the strip's: its lateral contrast is lower (Lab 1), so the width adds less waveguide dispersion.

## <span class="secnum">L2.5</span>Substrate leakage through the buried oxide

Below the buried oxide (BOX) lies the silicon handle wafer, whose index, 3.48, is above the mode's. Light tunnels through the BOX into it and is lost (Section 7.4). To model it, `leaky_mode` adds a silicon region below a BOX of thickness $$t_\mathrm{BOX}$$. A real handle is 0.7 mm thick, so the light that enters it never comes back; to imitate that in a 1 µm layer, the layer absorbs, more and more strongly with depth:

```python
depth = (-t_box - mesh.p[1, mesh.t].mean(axis=0)[sub]) / t_sub   # 0 at the top of the handle, 1 at the bottom
epsilon[sub] = n_si(lam) ** 2 * (1 + 1j * absorb * depth**2)
mode = compute_modes(basis0, epsilon, wavelength=lam, num_modes=1, n_guess=n_guess, order=2)[0]
```

The permittivity is now complex, and so is the effective index: the power falls as $$e^{-2k_0\,\mathrm{Im}(n_\mathrm{eff})z}$$, which the function returns in dB/cm. The absorption rises gradually so that it does not reflect the light itself. For TM0 with 800 nm of BOX, the default gives 71.14 dB/cm; doubling the absorption (`absorb=4.0`) or making the layer 1.5 µm thick (`t_sub=1.5`) changes that by 0.1 %, and halving it by 1 %, so the layer is doing its job. The silicon handle also has modes of its own, many of them, and `n_guess` asks the solver for the eigenvalue nearest the strip's mode; the absorber gives the handle's modes large imaginary parts, which keeps them away from it.

The script solves TE0 and TM0 with 600 and 1000 nm of BOX and compares the slope with the estimate of Worked Example 7.2: the tail decays as $$e^{-\gamma x}$$ with $$\gamma = k_0\sqrt{n_\mathrm{eff}^2 - n_\mathrm{ox}^2}$$, so the leaked power falls by $$e^{-2\gamma t}$$, or $$20\log_{10}(e)\,\gamma \times 0.1$$ dB per 100 nm.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint E</div>

TE0 leaks 5.4 dB/cm through 600 nm of BOX and 0.0072 dB/cm through 1000 nm: 7.18 dB per 100 nm, against 6.95 dB from $$\gamma = 8.00$$ µm⁻¹ (Worked Example 7.2: 8.0 µm⁻¹ and 7 dB). TM0 leaks 412 and 12.4 dB/cm: 3.80 dB per 100 nm, against 3.61 dB from $$\gamma = 4.15$$ µm⁻¹ (Worked Example 7.2: 4.2 µm⁻¹ and 3.6 dB). Extrapolated to a 2 µm BOX, TE0 leaks $$5\times10^{-10}$$ dB/cm and TM0 0.002 dB/cm; solving TM0 directly with 2 µm of BOX gives 0.0023 dB/cm.

</div>

The simple estimate gets the slope within 3 % for TE and 5 % for TM. The leakage falls a little faster than $$e^{-2\gamma t}$$ because under a strip only 500 nm wide, the field also spreads sideways as it reaches down, which thins it further. And the comparison bears out Worked Example 7.2: TM0 gains only about half as many decibels per 100 nm of oxide as TE0, and with a 1 µm BOX it would lose 12 dB/cm. With 2 µm, both are far below the 1–3 dB/cm of sidewall scattering. Weaker modes leak much more: TM0 of a 400 nm strip at 1600 nm ($$n_\mathrm{eff} = 1.640$$, `leaky_mode(2.0, "TM", width=0.4, lam=1.6, n_guess=1.640)`) loses 0.16 dB/cm through 2 µm of BOX and 0.0003 dB/cm through 3 µm. That, and the even weaker modes of narrow tapers and grating couplers, is where the chapter's 3 µm BOX pays off.

<figure id="fig-l2-1">
  <img src="{{ '/assets/figs/lab02_expected.png' | relative_url }}" style="width:760px" alt="Four plots from the lab script: the intensity of the TE0 and TM0 modes of a 500 by 220 nanometre strip; effective index against strip width from femwell and from the effective-index method; and substrate leakage against buried-oxide thickness for TE0 and TM0 on a logarithmic scale">
  <figcaption><span class="capnum">Figure L2.1.</span> <strong>What the script draws.</strong> (a), (b) Intensity of TE0 and TM0 in the 500 × 220 nm strip; the white outline is the silicon. (c) Effective index against width at 1550 nm: femwell (dots) and the EIM of Lab 1 (dashed); the dotted line is the oxide index. (d) Substrate leakage against BOX thickness: femwell (dots), the exponential through them, and the direct TM0 solve at 2 µm (open diamond); the dotted line marks 0.1 dB/cm.</figcaption>
</figure>

## Exercises

1. **The O band.** Run `group_index(0.5, lam=1.31)`. Compare with the 1310 nm rows of Table 6.1. Why does TM0 now have the higher group index?
2. **Converge.** Solve the 500 nm strip with `res` = 0.1, 0.08, 0.05, 0.03 and 0.02. How many decimals of TE0 and TM0 can you trust at the default? Then shrink the window (`half_w=1.0, half_h=0.8`, then 1.5 and 1.2) and watch TM0 at 500 nm and TE1 at 450 nm (`num=3`). Which mode needs the large window, and why?
3. **Fabrication sensitivity.** Find $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}W$$ and $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}t$$ of TE0 by central differences over ±10 nm of width and of thickness (the `t` argument of `solve`), and the shift of a ring resonance per nanometre of each, $$\Delta\lambda = \lambda\,\Delta n_\mathrm{eff}/n_g$$ (Section 6.7).
4. **Leakage in the O band.** Worked Example 7.2 says TE0 at 1310 nm gains 9.6 dB per 100 nm of BOX. Check it with `leaky_mode(t_box, "TE", lam=1.31, n_guess=2.712)` for 400, 600 and 800 nm.
5. **Silicon nitride.** Solve a 1.2 × 0.4 µm strip of nitride ($$n = 1.996$$) in oxide: `solve(1.2, t=0.4, n_core=1.996, num=3)`. Compare its effective index and evanescent decay length $$1/\gamma$$ with Section 6.6.

<details markdown="1">
<summary>Answers</summary>

1. TE0 2.7120 with $$n_g = 4.156$$, TM0 2.1646 with $$n_g = 4.670$$ (Table 6.1: 2.712, 4.16, 2.165 and 4.67). TE0's group index hardly changes, but TM0's rises from 3.74 to 4.67. At 1310 nm the 220 nm film is thicker compared with the wavelength, and TM0, whose field is vertical, is set mainly by the thickness: it is better confined (2.165 against 1.771), more of its power is in the silicon, and its index is on the steep part of its curve against size, so it changes fast with wavelength. That is the situation of Lab 1's slab, where TM0 had the higher group index too.
2. TE0: 2.44528, 2.44577, 2.44590, 2.44589 and 2.44586; TM0: 1.76958, 1.77076, 1.77077, 1.77072 and 1.77065. At the default 50 nm, both are within $$1\times10^{-4}$$ of the finest mesh: four decimals. TE0 does not notice the window (2.44591 in both smaller ones). TM0, whose field reaches further above and below the strip, is 1.7697 in the 2 × 1.6 µm window, 0.001 low, and 1.77076 in the 3 × 2.4 µm one, as good as the default. TE1 at 450 nm is not guided in either smaller window; it is 1.4477 in the default 4 × 3.2 µm window and 1.4495 in the 6 × 4 µm window of the chapter's own solver (`figsrc/ch06_sweep.json`). Near cut-off a mode's tail reaches far into the cladding, $$1/\gamma \approx 2$$ µm for TE1 at 450 nm, so a window that is too small pushes its index down and can push it out of the guided range altogether. Where exactly TE1 appears is the least certain number in this lab.
3. $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}W = 1.58\times10^{-3}$$ and $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}t = 3.72\times10^{-3}$$ per nanometre, so a ring resonance moves by 0.59 nm per nanometre of width and 1.38 nm per nanometre of thickness (Section 6.7: $$1.6\times10^{-3}$$, $$3.7\times10^{-3}$$, 0.6 and 1.4 nm).
4. 13.2, 0.141 and 0.0015 dB/cm: 9.85 dB per 100 nm from 400 to 600 nm and 9.80 dB from 600 to 800 nm, against 9.56 dB from $$\gamma = 11.0$$ µm⁻¹ (Worked Example 7.2: 11 µm⁻¹ and 9.6 dB). As at 1550 nm, femwell's slope is a few per cent steeper than the estimate, and the excess shrinks as the oxide gets thicker.
5. TE0 $$n_\mathrm{eff} = 1.6635$$ (Section 6.6: about 1.67) and $$1/\gamma = 299$$ nm (about 300 nm, three times silicon's 101 nm). The strip also guides TM0 (1.5823) and TE1 (1.466), but TE1 is only 0.022 above the oxide, as weakly guided as the silicon strip's TE1 at 500 nm, and the first bend strips it.

</details>

## Going further

- Add a radius: `compute_modes(..., radius=5.0)` solves a bent waveguide by a conformal transformation. With an absorbing region beyond the outer edge, as for the substrate here, its imaginary part is the bend loss of [Chapter 8]({% link chapters/08_bends.md %}).
- Solve two strips side by side: the even and odd supermodes give the coupling length of [Chapter 9]({% link chapters/09_couplers.md %}) directly, without Lab 3's effective-index reduction (the repository's `figsrc/ch09_supermodes.py` does exactly that).
- [Lab 4]({% link labs/lab04_sax.md %}) turns this lab's $$n_\mathrm{eff} = 2.446$$ and $$n_g = 4.18$$ into a compact model of the waveguide and builds MZIs and rings from it.
- The femwell documentation has worked examples beyond mode solving: heaters, PN junctions and electro-optic overlaps, the subjects of [Chapters 18 to 20]({% link chapters/18_thermal.md %}).


