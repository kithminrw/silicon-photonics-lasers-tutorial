---
title: "Lab 7. Lay out your first chip"
parent: Hands-On Labs
nav_order: 7
permalink: /labs/lab-07/
---

# <span class="chapnum">Lab 7 · Make</span>Lay Out Your First Chip

Write the first chip of this tutorial as Python code, with gdsfactory and the SiEPIC EBeam PDK: grating couplers on the fibre-array pitch, a loopback, an unbalanced MZI, three rings and a cutback set, routed, labelled for the automated prober, and fitted into an openEBL design area.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- find the openEBL layout rules, and where each one is written down;
- place the PDK's grating couplers on the 127 µm pitch and join them with routed waveguides;
- build an MZI with a set arm-length difference, and check it from the drawn route lengths;
- add rings with three gaps and a set of cutback spirals;
- label every device for automated measurement, fit the chip into 605 × 410 µm and write the GDS file;
- open the result in KLayout.

</div>

## What you need

- [Chapter 30]({% link chapters/30_flow.md %}) (Sections 30.2 to 30.4, 30.7 and 30.8), with [Chapter 17]({% link chapters/17_fiberarrays.md %}) (Section 17.7), [Chapter 15]({% link chapters/15_gc.md %}) (Section 15.7), [Chapter 11]({% link chapters/11_mzi.md %}) (Section 11.3), [Chapter 12]({% link chapters/12_rings.md %}) (Table 12.1) and [Chapter 7]({% link chapters/07_loss.md %}) (Section 7.7).
- Python 3.11 or newer with gdsfactory, ubcpdk and Matplotlib: `pip install "gdsfactory==9.51.0" "ubcpdk==3.3.5" matplotlib`. Tested with Python 3.12, gdsfactory 9.51.0, ubcpdk 3.3.5 (the SiEPIC EBeam PDK for gdsfactory {% include cite.html keys="ubcpdk" %}), the KLayout Python module 0.30.13 that gdsfactory installs, NumPy 2.4 and Matplotlib 3.11.
- Optionally [KLayout](https://www.klayout.de) 0.29 or newer, to look at the layout (Section L7.7). The lab does not need it.
- The script <a href="{{ '/labs/lab07_layout.py' | relative_url }}" download><code>lab07_layout.py</code></a>.
- About two hours, including the exercises.

Run it from a terminal in the folder where you saved it:

```
python lab07_layout.py
```

It prints a checkpoint for each part below, writes the layout `EBeam_YourName_firstchip.gds` and saves the figure `lab07_layout.png`, in a minute or two. Read each part, then the matching function in the script; change things and run it again. All lengths are in micrometres. Before you submit anything, set `USER` at the top of the script to your own name (letters and digits only): it goes into the file name, the top cell and every label.

The chip is the "your first chip" of Chapters 6–37: a passive 220 nm SOI chip at 1550 nm, measured through grating couplers. [Lab 8]({% link labs/lab08_submit.md %}) checks it and walks through the submission, and [Lab 9]({% link labs/lab09_analysis.md %}) analyses the kind of data it returns.

## <span class="secnum">L7.1</span>The openEBL rules

openEBL is SiEPIC's free fabrication and test service for designers who have taken a SiEPIC course or workshop {% include cite.html keys="openebl" %}: a 220 nm SOI process, patterned by 100 keV electron-beam lithography at Applied Nanotools, with one full etch and an oxide cladding. Each run has its own GitHub repository, for example [SiEPIC/openEBL-2026-10](https://github.com/SiEPIC/openEBL-2026-10). Before drawing anything, collect the rules. They are spread over a web page, a README, two check scripts, a DRC deck and the PDK's design-for-test file; [Table L7.1](#tab-l7-1) gathers them, each with its source.

**Table L7.1. The openEBL layout rules this chip follows,** read from the sources on 18 November 2026. The run repositories change from run to run: read your run's README before you submit.
{: .tabcaption #tab-l7-1 }

| Rule | Value | Source |
|---|---|---|
| Design area | 605 × 410 µm | [siepic.ca/openebl](https://siepic.ca/openebl/) ("a small design area of 605 µm x 410 µm"); [`run_submission_checks.py`](https://github.com/SiEPIC/openEBL-2026-10/blob/main/run_submission_checks.py) measures the extent of layers 1/0 and 4/0 against 605000 × 410000 database units |
| Layers | Si 1/0, Text 10/0, FloorPlan 99/0; DevRec 68/0, PinRec 1/10, Waveguide 1/99 and SEM 200/0 are "virtual" | the layer table of the [run README](https://github.com/SiEPIC/openEBL-2026-10) |
| Top cell | exactly one | `run_submission_checks.py`; its name is not checked (see below) |
| Minimum feature, minimum gap | 60 nm and 70 nm on Si, each checked 2 nm below | [`SiEPIC_EBeam_DRC.lydrc`](https://github.com/SiEPIC/SiEPIC_EBeam_PDK/blob/master/klayout/EBeam/drc/SiEPIC_EBeam_DRC.lydrc) (`width(0.06-tol)`, `space(0.07-tol)`, `tol = 2e-3`), which also flags Si outside the floorplan |
| Grating couplers | 127 µm pitch, in a vertical column, unrotated; at most 1 coupler above and 2 below the labelled input; at least 60 µm apart | the PDK's [`DFT.xml`](https://github.com/SiEPIC/SiEPIC_EBeam_PDK/blob/master/klayout/EBeam/DFT.xml) (`gc-pitch`, `gc-array-orientation`, `gc-orientation`, `detectors-above-laser`, `detectors-below-laser`, `minimum-gc-spacing`) |
| Black-box cells | the couplers (`_BB` in the name, or layer 998/0) are replaced at the foundry: do not rename, edit or move their origins | run README |
| Test labels | `opt_in_<polarization>_<wavelength>_<type>_<deviceID>_<params>` on layer 10/0, within 10 µm of the input coupler's origin; wavelength and polarisation must match a laser in `DFT.xml` (TE or TM at 1550 or 1310 nm) | SiEPIC-Tools' [`find_automated_measurement_labels`](https://github.com/SiEPIC/SiEPIC-Tools) (in `SiEPIC/utils`) and `DFT.xml` (`max-distance-to-grating-coupler`) |
| File | `.gds` or `.oas` in `submissions/`, no spaces in the name, named `EBeam_username.oas` (edX), `ELEC413_…`, `SiEPIC_Passives_…` or `openEBL_username.gds` | run README; the `check_gds_files.yml` workflow |
{: .lab-table }

Three things we could not confirm, and so do not treat as rules. No check reads the top cell's name; SiEPIC's own example design names it like its file, `EBeam_<designer>_MZI`, and this lab does the same. Neither the DRC deck nor the checks set a minimum bend radius for routed waveguides; we use the PDK's 10 µm Euler bends. And the README promises a manufacturing DRC, but the workflow files we read run only `run_submission_checks.py` and SiEPIC-Tools' verification; Lab 8 runs both, and the DRC rules too.

## <span class="secnum">L7.2</span>Couplers on the pitch, and the loopback

Every device on this chip has the same frame: two of the PDK's TE grating couplers, `ebeam_gc_te1550`, one above the other, 127 µm apart, both facing east, with the input above the output ([Chapter 17]({% link chapters/17_fiberarrays.md %}), Section 17.7). A coupler's origin is its waveguide port, and its grating reaches 40 µm to the west of it. The cell is a black box: we place it, but never rename, rotate or edit it.

```python
def coupler_pair(name):
    c = gf.Component(name)
    gc_out = c << pdk_cell(GC)
    gc_in = c << pdk_cell(GC)
    gc_in.dmove((0, GC_PITCH))
    c.info["routes"] = []                          # (what, length in um) of every routed waveguide
    return c, gc_in, gc_out

def loopback(name="loopback"):
    c, gc_in, gc_out = coupler_pair(name)
    route(c, gc_in.ports["o1"], gc_out.ports["o1"], "coupler to coupler")
    return c
```

`route` calls gdsfactory's `route_single`, which draws a Manhattan route of 500 nm strip with 10 µm Euler bends, and keeps its length. The loopback is the shortest device: its spectrum is the couplers' own, and every other device's is divided by it ([Chapter 15]({% link chapters/15_gc.md %}), Section 15.7; [Lab 9]({% link labs/lab09_analysis.md %})).

One detail matters for the verification of Lab 8. SiEPIC-Tools, which openEBL runs on every submission, recognises a component by a DevRec shape (68/0) around it, and finds which component connects to which by PinRec pins (1/10) at their ports: short paths across the port, pointing out, each with a text naming it. gdsfactory's routed straights and bends, and the parts inside its rings and spirals, have DevRec but no pins, so SiEPIC-Tools would see 196 unconnected pieces and no circuit at all. (In the versions tested, ubcpdk's own `add_pins_siepic` put its pins where SiEPIC-Tools reported them as invalid.) ubcpdk also redraws the pins of the PDK's fixed cells, the coupler and the Y-branch, as boxes, which SiEPIC-Tools does not recognise, so `pdk_cell` reads those cells from the PDK's GDS files exactly as they are. And the script routes with `straight_pins` and `bend_pins`, which pass each piece through `siepic`: flatten it, keep one DevRec polygon, and draw a 20 nm pin at each port the way SiEPIC-Tools' own `make_pin` does:

```python
    for i, p in enumerate(c.ports):                 # a 20 nm path across the port, pointing out, as SiEPIC draws it
        (x, y), a = p.dcenter, math.radians(p.orientation)
        dx, dy = 0.01 * math.cos(a), 0.01 * math.sin(a)
        c.shapes(pins).insert(kdb.DPath([kdb.DPoint(x - dx, y - dy), kdb.DPoint(x + dx, y + dy)], p.width))
        c.shapes(pins).insert(kdb.DText(f"opt{i + 1}", kdb.DTrans(x, y)))
```

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

The script prints the rules it uses: a 605 × 410 µm design area on 99/0, silicon on 1/0, labels on 10/0, the coupler `ebeam_gc_te1550`, unrotated, on a 127 µm pitch, and the label format `opt_in_TE_1550_device_YourName_<name>`. The loopback waveguide is 140.3 µm long: 127 µm up, 10 µm out and back, less 3.4 µm for each Euler bend, which at 16.64 µm is shorter than the 20 µm corner it replaces.

</div>

## <span class="secnum">L7.3</span>An unbalanced MZI

The MZI of [Worked Example 11.2]({% link chapters/11_mzi.md %}) has $$\Delta L = 100$$ µm, for a free spectral range $$\mathrm{FSR} = \lambda^2/(n_g\Delta L) = 5.75$$ nm with the strip's group index of 4.18 ([Chapter 6]({% link chapters/06_soi.md %})). It is built from the PDK's Y-branch, `ebeam_y_1550`, used as splitter and, turned round, as combiner. The short arm is a 50 µm straight; the long arm leaves through the lower port, dips down and comes back up. The dip adds twice its depth, but each of its four Euler bends is 3.36 µm shorter than the corner it rounds, so the depth is set to make up for them:

```python
    bend = gf.get_component("bend_euler", cross_section=XS)
    extra = 4 * (2 * bend.info["dy"] - bend.info["length"])   # four Euler bends are shorter than their corners
    depth = (dl + extra) / 2                         # the dip adds 2 x depth, less what the bends save
    ...
    route(c, y1.ports["o3"], y2.ports["o2"], "long arm",
          waypoints=[(s[0] + r, s[1]), (s[0] + r, s[1] - depth), (e[0] - r, e[1] - depth), (e[0] - r, e[1])])
```

The script then measures $$\Delta L$$ from the two drawn routes rather than trusting the formula. This is the habit of [Section 30.7]({% link chapters/30_flow.md %}): simulate and check what was drawn, not what was meant.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

The short arm is 50.000 µm and the long arm 150.001 µm: $$\Delta L$$ = 100.001 µm, for a target of 100. The FSR is $$2.4025/(4.18 \times 0.1000\ \mathrm{mm}) = 5.75$$ nm (Worked Example 11.2: 5.75 nm). The dip is 56.7 µm deep.

</div>

## <span class="secnum">L7.4</span>Rings with three gaps

The rings are those of [Table 12.1]({% link chapters/12_rings.md %}): radius 10 µm, point-coupled to a straight bus, with gaps of 200, 250 and 300 nm, which the chapter's model puts over-coupled, slightly over-coupled and slightly under-coupled at 2 dB/cm. ubcpdk's `ring_single` draws a racetrack; with both straight sections set to zero it is a circle. It is mirrored to hang below the bus, so that it stays clear of the device above.

```python
@gf.cell
def ring_cell(gap=0.2, radius=RING_R):
    return siepic(gf.get_component("ring_single", gap=gap, radius=radius, length_x=0.0, length_y=0.0,
                                   cross_section=XS))
...
    rg = c << ring_cell(gap=gap, radius=radius)
    rg.dmirror_y()                                  # ring below the bus, away from the next device up
```

A gap of 200 nm is more than twice the 70 nm minimum, so all three are safely drawable; [Lab 8]({% link labs/lab08_submit.md %}) shrinks one below it on purpose.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

Three rings, with gaps of 200, 250 and 300 nm, each 62.83 µm round, with an FSR of 9.15 nm at $$n_g$$ = 4.18 (Chapter 12: 9.1 nm for a 10 µm ring).

</div>

## <span class="secnum">L7.5</span>A cutback set

A cutback measures loss as the slope of insertion loss against length ([Section 7.7]({% link chapters/07_loss.md %})). Long lengths need a compact shape, so three of the four devices are racetrack spirals that wind in and back out, with neighbouring turns 2 µm apart (1.5 µm of oxide between 500 nm strips, far too wide to couple over a few millimetres; [Chapter 9]({% link chapters/09_couplers.md %})). The loopback is the fourth, shortest length. The spiral sits between its two couplers. ubcpdk's spiral has its input and output ports inside its own outline, so `spiral_cell` extends both with straight leads to the edge of its bounding box, which becomes its DevRec; that keeps the routes outside it, as SiEPIC-Tools' overlap check wants:

```python
@gf.cell
def spiral_cell(loops=6, straight=20.0):
    c = gf.Component()
    s = c << gf.get_component("spiral_racetrack", straight_length=straight, spacings=(SPIRAL_PITCH,) * loops,
                              cross_section=XS)
    bb = s.dbbox()
    lead_in = c << gf.c.straight(length=s.ports["o1"].dcenter[0] - bb.left, cross_section=XS)
    lead_in.connect("o2", s.ports["o1"])
    ...
    return siepic(c)
```

The script adds up every routed waveguide in each device, and the spiral's own length, which gdsfactory records in the spiral's `info`. The Y-branches, the ring couplers and the grating couplers are fixed PDK cells and are not counted.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

The routed lengths per device: loopback 140.3 µm; each ring 230.3 µm (25.0 in, 20.0 of bus, 185.3 out); the MZI 439.9 µm (10.0 in, arms of 50.0 and 150.0, 229.9 out); the spirals 1299.0, 3006.7 and 4871.9 µm, of which 1104.9, 2772.9 and 4618.3 µm are the spirals themselves with their leads. The cutback set is 0.14, 1.30, 3.01 and 4.87 mm; at 2 dB/cm the longest adds 0.95 dB to the loopback's loss.

</div>

Chapter 7 asks for lengths spanning a centimetre or more; 605 × 410 µm does not allow it beside everything else. Exercise 4 works out what this costs in precision, and why the rings' loss is the independent check that Chapter 12 recommends.

## <span class="secnum">L7.6</span>Floorplan, labels and the GDS file

`build_chip` draws the 605 × 410 µm floorplan box on 99/0 with its corner at the origin, and places the eight devices in four columns of couplers, two devices per column. In each column the lower device's couplers are at $$y$$ = 20 and 147 µm and the upper device's at 263 and 390 µm, so neighbouring couplers of different devices are 116 µm apart in a column, and at least 101 µm apart across columns, more than the 60 µm minimum. Each column's couplers start 45 µm east of the widest device in the column before it, rounded up to a whole micrometre. Then a label goes on each device's input coupler, at its origin:

```python
def label_text(name, user=USER):
    return f"opt_in_TE_1550_device_{user}_{name}"
...
            chip.add_label(label_text(name), position=(in_xy[0] + lx, in_xy[1] + ly), layer=LAYER_TEXT)
```

The label tells the automated prober what to do: align to this coupler (the "laser" fibre, [Chapter 36]({% link chapters/36_testing.md %})), sweep the TE laser around 1550 nm, and record the couplers of the same circuit as detectors. ubcpdk's own `add_fiber_array` writes labels with hyphens, `…device_<user>-<name>`; this lab uses the underscores of SiEPIC's examples. The extra arguments `move_label` and `move_device` exist to break the chip on purpose in Lab 8.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint E</div>

Eight devices, sixteen couplers in four columns. The silicon spans $$x$$ = 12.5 to 586.5 µm and $$y$$ = 9.9 to 400.1 µm, 574.1 × 390.2 µm, which fits the 605 × 410 µm floorplan with margins of 12.5, 18.5, 9.9 and 9.9 µm (left, right, bottom, top). The labels, `opt_in_TE_1550_device_YourName_loopback` and so on, sit on the input couplers at $$x$$ = 45, 146, 247 and 394 µm, $$y$$ = 147 and 390 µm. The script writes `EBeam_YourName_firstchip.gds`, with that top cell.

</div>

<figure id="fig-l7-1">
  <img src="{{ '/assets/figs/lab07_expected.png' | relative_url }}" style="width:760px" alt="The layout drawn by the lab script: a 605 by 410 micrometre floorplan with four columns of grating couplers, a loopback, three rings, an MZI and three spirals, with red dots at the labelled input couplers; a zoom on the MZI; and a zoom on a ring's 200 nm coupling gap">
  <figcaption><span class="capnum">Figure L7.1.</span> <strong>What the script draws.</strong> (a) The chip in its design area: grating couplers (grey) on a 127 µm pitch, the loopback, the rings (blue), the MZI (purple) and the spirals of the cutback set (green); the red dots are the opt_in labels on the input couplers. (b) The MZI: two Y-branches, a 50 µm arm and a 150 µm arm with a 56.7 µm dip. (c) The coupler of the 200 nm ring, to scale. PDK cells from the SiEPIC EBeam PDK through ubcpdk (both MIT licence).</figcaption>
</figure>

## <span class="secnum">L7.7</span>The same layout in KLayout

The script's figure is drawn from the GDS file with KLayout's Python module, which comes with gdsfactory. To look at the file interactively:

1. Install [KLayout](https://www.klayout.de) (0.29 or newer). For layer names and colours, and the SiEPIC menu, install the PDK as its [installation instructions](https://github.com/siepic/SiEPIC_EBeam_PDK/wiki/Installation-instructions) say: **Tools › Manage Packages**, install **SiEPIC-Tools** and then **SiEPIC-EBeam-PDK**, and restart KLayout {% include cite.html keys="klayout,siepictools,ebeampdk" %}.
2. **File › Open** the GDS. If the layers have no names, choose **File › Layout Properties**, and set the technology to **EBeam**.
3. The cell tree shows one top cell with eight device cells under it. Show all hierarchy levels (the `*` key) to see the couplers' insides; measure the 127 µm pitch with the ruler, and zoom into a ring to see its gap.
4. With SiEPIC-Tools installed, **SiEPIC › Verification › Functional Layout Check** (shortcut V) runs the verification of Lab 8 and lists any errors.
5. To see each run at once, install the **klive** package in KLayout, keep KLayout open and run `python lab07_layout.py --show`: gdsfactory sends the chip to the open window.

## Exercises

1. **Another FSR.** Set `MZI_DL = 60`. What do the checkpoints give for $$\Delta L$$, the FSR and the depth of the dip? Which $$\Delta L$$ would put the FSR at 6.4 nm, the interleaver of Section 11.3?
2. **Racetracks.** Change the rings to `length_x=4.0`, ubcpdk's default. What are the circumference and the FSR now, and how will the extra 4 µm of straight coupler change the coupling of each gap?
3. **Bigger spirals.** How many loops can `spiral3` have (keeping 60 µm straights) before the chip leaves the floorplan? What is its length then?
4. **What the cutback can resolve.** Suppose each device's coupler loss scatters by 0.3 dB, independently ([Section 7.7]({% link chapters/07_loss.md %})). Fit a line through the four lengths of Checkpoint D: what is the standard error of the slope in dB/cm, and how does it compare with a loss of 2 dB/cm? How long must the longest spiral be for a 10 % error bar?
5. **A second chip.** Lay out a variation: rings of radius 5 µm, or a second MZI with $$\Delta L$$ = 200 µm, in place of `spiral1`. What has to change in `COLUMNS` and in `build_devices`?

<details markdown="1">
<summary>Answers</summary>

1. The long arm's route comes out 60.001 µm longer than the short one, so $$\Delta L$$ = 60.001 µm, the FSR is 9.58 nm and the dip is 36.7 µm deep: $$(60 + 13.45)/2$$, where 13.45 µm is what the four Euler bends save. An FSR of 6.4 nm needs $$\Delta L = 2.4025/(4.18 \times 0.0064) = 89.8$$ µm (Section 11.3: 90 µm).
2. $$2\pi \times 10 + 2 \times 4 = 70.83$$ µm round, so the FSR falls to 8.11 nm. The coupling grows a lot. With Chapter 9's coupler model, Table 12.1's point couplers act like 2.7 µm of parallel waveguide (from $$\kappa = \sin(\pi L_\mathrm{eff}/2L_x)$$ with $$L_x$$ = 37.8 µm at 200 nm, ×2.4 per 100 nm); 4 µm more makes 6.7 µm, and κ² rises from 1.23, 0.52 and 0.22 % to about 7.5, 3.2 and 1.3 %. Critical coupling at 2 dB/cm is 0.33 % for this length, so all three would be over-coupled; the same sweep through critical coupling would need gaps around 380 nm. These are estimates from the chapter's model, not from the layout.
3. 16 loops: the spiral device is 5797.6 µm long (5.80 mm) and the silicon reaches $$x$$ = 599.4 µm, still inside the 605 µm floorplan. 18 loops (6.79 mm) reach 612.2 µm and leave it. Keep the number of loops even: with an odd number, ubcpdk's spiral brings its output out on the other side (15 loops reach $$y$$ = 468 µm, far outside).
4. With $$L$$ = 0.014, 0.130, 0.301 and 0.487 cm, $$\sum(L_i - \bar L)^2 = 0.128$$ cm², and the slope's standard error is $$0.3/\sqrt{0.128} = 0.84$$ dB/cm: 42 % of 2 dB/cm. The error falls as the inverse of the span, so 10 % (0.2 dB/cm) needs lengths 4.2 times longer, up to 2.0 cm; four lengths spread evenly from 0 to 2 cm give the same. That is far more waveguide than fits in 605 × 410 µm beside the other devices, which is why the rings, whose loss comes from the width of one resonance rather than from comparing devices, are the better check here ([Section 12.5]({% link chapters/12_rings.md %})).
5. Write the new device in `build_devices` under a new key, for example `devs["mzi200"] = mzi("mzi200" + suffix, dl=200.0)`, and put that key in `COLUMNS` in place of `"spiral1"`; the label follows the key. The MZI with $$\Delta L$$ = 200.001 µm (FSR 2.87 nm) fits in the spiral's place: its dip, 106.7 µm deep, stays 17.5 µm above the output route, the silicon reaches $$x$$ = 585.5 µm, and Lab 8's checks all pass (40 of 40). Rings of radius 5 µm need only `radius=5.0` in `ring_cell`; their FSR doubles to 18.3 nm, and their coupling at the same gap falls, since the bus and the ring part faster.

</details>

## Going further

- [Lab 8]({% link labs/lab08_submit.md %}) runs the openEBL checks on this file, breaks it on purpose, and walks through the pull request; [Lab 9]({% link labs/lab09_analysis.md %}) analyses measurements of the same set of devices.
- Add a Bragg grating ([Chapter 13]({% link chapters/13_bragg.md %})): the KLayout PDK has a parameterised `ebeam_bragg_te1550` cell; in gdsfactory, a corrugated waveguide can be drawn from `gf.components.dbr` with the period of [Lab 5]({% link labs/lab05_bragg.md %}), 317 nm. Run Lab 8 after adding it: a corrugation is the narrowest feature on the chip.
- Simulate the layout before you submit it: extract the netlist in KLayout with SiEPIC-Tools, or simulate the gdsfactory component with SAX {% include cite.html keys="sax" %} ([Section 30.6]({% link chapters/30_flow.md %})).
- SiEPIC's own example, [`EBeam_LukasChrostowski_MZI.py`](https://github.com/SiEPIC/openEBL-2024-10/blob/main/submissions/KLayout%20Python/EBeam_LukasChrostowski_MZI.py), draws MZIs with SiEPIC-Tools' Python API instead of gdsfactory; openEBL also accepts such a script in place of a GDS file.
