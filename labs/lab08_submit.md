---
title: "Lab 8. Verify and submit to openEBL"
parent: Hands-On Labs
nav_order: 8
permalink: /labs/lab-08/
---

# <span class="chapnum">Lab 8 · Make</span>Verify and Submit to openEBL

Check the chip of Lab 7 the way openEBL's GitHub Actions will, first with a short script of your own and then with SiEPIC-Tools itself; break it on purpose to see each check fire; and follow the pull request that submits it, from fork to measured data.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- follow the openEBL submission, from fork to pull request, and know what each automated check does;
- check a GDS file with KLayout's Python module: top cell, floorplan, layers, minimum width and space, grating couplers, labels and overlaps;
- run SiEPIC-Tools' functional verification without the KLayout window, as the GitHub Action does;
- break the layout on purpose and read what the checks report;
- know what happens after the merge: fabrication, measurement, and where the data appear.

</div>

## What you need

- [Chapter 30]({% link chapters/30_flow.md %}) (Sections 30.7 and 30.8) and [Chapter 17]({% link chapters/17_fiberarrays.md %}) (Section 17.7), and [Lab 7]({% link labs/lab07_layout.md %}): its rules table and its script.
- Python 3.11 or newer with KLayout's Python module, which gdsfactory installs (or `pip install klayout`); gdsfactory and ubcpdk as in Lab 7 to make or break the chip; and, for Section L8.6, SiEPIC-Tools and the EBeam PDK as Python packages: `pip install SiEPIC siepic_ebeam_pdk`. Tested with Python 3.12, klayout 0.30.13, SiEPIC 0.5.31, siepic_ebeam_pdk 0.4.53, gdsfactory 9.51.0 and ubcpdk 3.3.5.
- The script <a href="{{ '/labs/lab08_checks.py' | relative_url }}" download><code>lab08_checks.py</code></a>, saved beside <a href="{{ '/labs/lab07_layout.py' | relative_url }}" download><code>lab07_layout.py</code></a> (both also in the repository's [`labs/` folder](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs)).
- For the submission itself (Section L8.8): a GitHub account, and a place in an openEBL run (see below).
- About two hours, including the exercises.

Run it from a terminal in the folder where you saved both scripts:

```
python lab08_checks.py
python lab08_checks.py --siepic
python lab08_checks.py --break gap
```

The first command checks `EBeam_YourName_firstchip.gds`, making it with Lab 7's script if it is not there, prints a checkpoint for each part below, and saves the figure `lab08_checks.png`; it takes a minute or two. `--siepic` adds SiEPIC-Tools' verification, and `--break` builds a deliberately broken copy of the chip and checks that instead (`gap`, `label`, `overlap`, `outside` or `all`). Give it any other file name to check your own design. All lengths are in micrometres.

## <span class="secnum">L8.1</span>The submission, step by step

Each openEBL run has a GitHub repository; the one for the run of October 2026 is [SiEPIC/openEBL-2026-10](https://github.com/SiEPIC/openEBL-2026-10), whose deadline, 17 October 2026, has passed. Runs come about three times a year {% include cite.html keys="openebl" %}: watch [siepic.ca/openebl](https://siepic.ca/openebl/) and the [SiEPIC GitHub organisation](https://github.com/SiEPIC) for the next one. Its README opens the runs to former and current students of SiEPIC workshops and courses, which include the edX course *Silicon Photonics Design, Fabrication and Data Analysis* {% include cite.html keys="phot1x" %}. The steps, from the README:

1. Fork the run's repository on GitHub, and enable Actions on your fork (the **Actions** tab).
2. Add your `.gds` or `.oas` file to the `submissions/` folder, named after you: `EBeam_username.oas` for edX students, `openEBL_username.gds` for past participants, and so on (Table L7.1). No spaces in the name.
3. Commit. The checks run on your fork; fix what they report until they pass.
4. Open a pull request to the run's repository. The same checks run again on it.
5. When they pass, the pull request is merged and your design is added to the run's merged layout, shown as `merge/EBeam.png` in the repository.

Instead of a GDS file you may submit a Python script that builds it, in `submissions/KLayout Python/`; it must run without the KLayout window and save a `.gds` or `.oas` file in `submissions/`.

**Table L8.1. What runs on a pull request,** from the workflow files of [openEBL-2026-10](https://github.com/SiEPIC/openEBL-2026-10/tree/main/.github/workflows), read on 18 November 2026.
{: .tabcaption #tab-l8-1 }

| Workflow | What it checks |
|---|---|
| `check_gds_files.yml` | every changed `.gds` or `.oas` is in `submissions/` and has no spaces in its name |
| `case_sensitivity.yml` | file-name case; a pull request may add only `.gds`/`.oas` in `submissions/` and `.pdf` in `reports/` |
| `run-submission-check.yml` | runs [`run_submission_checks.py`](https://github.com/SiEPIC/openEBL-2026-10/blob/main/run_submission_checks.py) on each file: exactly one top cell; the extent of layers 1/0 and 4/0 at most 605 × 410 µm; black-box cells replaced by the foundry's dummies, and no 998/0 geometry left over; every layer defined in the PDK's layer table |
| `run-verification.yml` | installs `klayout SiEPIC siepic_ebeam_pdk` on Python 3.11 and runs [`run_verification.py`](https://github.com/SiEPIC/openEBL-2026-10/blob/main/run_verification.py), which calls SiEPIC-Tools' `layout_check` and uploads the report (`.lyrdb`) as an artifact named `layout-errors` |
| `python-to-oas_gds.yml` | for a Python submission: runs the script and passes its layout to the checks above |
| `final-verification.yml` | waits for the required checks to pass, so the pull request can be merged |
| `aggregation.yml` | after verification, merges the submissions into the run's layout (`merge/EBeam_merge.py`) |
{: .lab-table }

After the deadline the merged layout is written by 100 keV electron-beam lithography at Applied Nanotools, and the chips are measured on SiEPIC's automated probe station ([Chapter 31]({% link chapters/31_testing.md %})). The openEBL page gives results "typically 4-6 weeks after tape-out date", and a link to the measurements on the homepage of the submission repository; the README says the results "will be posted in this repository", and the repository of the October 2025 run also holds SEM images in a `SEMs/` folder. We found no published time between the submission deadline and tape-out. [Lab 9]({% link labs/lab09_analysis.md %}) analyses the kind of data that comes back.

## <span class="secnum">L8.2</span>Top cell, floorplan and layers

The first block of checks repeats `run_submission_checks.py`, and adds two of our own. The script reads the GDS file with KLayout's Python module and gathers the shapes of a layer, flattened through the hierarchy, into a `Region`, KLayout's polygon set, on which Boolean operations and design-rule checks run:

```python
def region(cell, layer, skip_cells=()):
    ly = cell.layout()
    li = ly.find_layer(*layer)
    if li is None:
        return kdb.Region()
    it = cell.begin_shapes_rec(li)
    if skip_cells:
        it.unselect_cells([ly.cell(n).cell_index() for n in skip_cells if ly.has_cell(n)])
    return kdb.Region(it)
```

The openEBL check measures only the size of the bounding box of layers 1/0 and 4/0, not where it is. The DRC deck asks for more, that no silicon lies outside the floorplan box (`LayerSi.outside(LayerFP)`), and so does our script: `region(top, SI) - fp` must be empty. The allowed layers are those of the passive run's layer table, plus the two the PDK's couplers carry inside them, FbrTgt 81/0 (where the fibre goes) and BlackBox 998/0. The real check is looser: it accepts any layer of the PDK's layer table, including heaters and metal, which this run does not fabricate.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

One top cell, `EBeam_YourName_firstchip`, named like its file. The extent of 1/0 and 4/0 is 574.1 × 390.2 µm, within 605 × 410 µm; the floorplan box on 99/0 is 605.0 × 410.0 µm at (0, 0), and no silicon lies outside it. The layers used are 1/0, 1/10, 10/0, 68/0, 81/0, 99/0 and 998/0, all allowed. The couplers keep their PDK name, `ebeam_gc_te1550`.

</div>

## <span class="secnum">L8.3</span>Minimum width and space

The SiEPIC EBeam DRC deck has two size rules for silicon: features at least 60 nm wide and gaps at least 70 nm, each tested 2 nm below its value, `tol = 2e-3` µm, because "users typically shoot for exactly the min features" (comment in the deck), and with `angle_limit(80)`, which ignores the meeting of edges at sharp angles, such as the tip of a Y-branch. KLayout's `Region` has the same two checks, so the script runs exactly these rules, in Python rather than in KLayout's DRC language:

```python
    si = region(top, SI, skip_cells=gc_names)
    w = si.width_check(round((MIN_WIDTH - TOL) / dbu), False, kdb.Metrics.Euclidian, ANGLE_LIMIT)
    s = si.space_check(round((MIN_SPACE - TOL) / dbu), False, kdb.Metrics.Euclidian, ANGLE_LIMIT)
```

Each returns the pairs of edges that break the rule, with their positions, so the figure can mark them. The couplers are skipped: their sub-wavelength teeth are finer than 60 nm, and they are black boxes that the foundry replaces with its own geometry. The deck's messages say "min 60 nm" for both rules, but its space rule tests 70 nm; we follow the numbers. We could not find the workflow that runs this deck on a pull request (Table L8.1), so run it yourself in KLayout before you submit: **SiEPIC › Verification › KLayout Design Rule Check (DRC) - EBeam** (shortcut D).

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

No width and no space violations. The narrowest gap in each device under 500 nm: 200, 250 and 300 nm in the three rings, and 200 nm in the MZI. The 200 nm in the MZI is between the Y-branch's two arms where they part.

</div>

## <span class="secnum">L8.4</span>Grating couplers and labels

The design-for-test rules come from the PDK's `DFT.xml` (Table L7.1). The script walks the cell tree to find every coupler, keeping its position in the top cell, its rotation and the top-level cell (the device) it belongs to:

```python
def find_gcs(top):
    out = []
    def walk(cell, trans, device):
        for inst in cell.each_inst():
            t = trans * inst.dcplx_trans
            dev = device or inst.cell.name
            if is_gc(inst.cell.name):
                out.append(dict(device=dev, cell=inst.cell.name, x=t.disp.x, y=t.disp.y, angle=t.angle,
                                mirror=t.is_mirror()))
            else:
                walk(inst.cell, t, dev)
    walk(top, kdb.DCplxTrans(), None)
    return out
```

Then, for each label on 10/0 that starts with `opt_`: does it parse as `opt_in_<TE|TM>_<1550|1310>_device_<you>_<name>`; is it unique; is a coupler's origin within 10 µm of it; and are the other couplers of that device in the same column, at +1, −1 or −2 pitches of 127 µm from it? SiEPIC-Tools finds "the other couplers" by tracing the circuit from pin to pin; our script takes the couplers in the same top-level cell, which is how Lab 7 builds its chip, but a looser assumption for other layouts. Finally, every device must have a label.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

16 couplers in 8 devices, all unrotated, the closest pair 101.0 µm apart (at least 60). Eight labels, all different, each 0.0 µm from its device's upper coupler, with the device's other coupler 127 µm below it (−1 pitch); every device is labelled. With the checks of Section L8.5, 40 checks pass and none fail.

</div>

## <span class="secnum">L8.5</span>Overlapping devices

SiEPIC-Tools calls two components overlapping when their DevRec shapes overlap; touching is allowed. The script applies the same test to whole devices: the DevRec region of each top-level cell, intersected with every other one, must be empty. It catches a device dropped on top of another, which the DRC rules may miss where the silicon merges.

## <span class="secnum">L8.6</span>SiEPIC-Tools' own verification

`run_verification.py`, which openEBL's GitHub Action runs, is short: it reads the file, sets the EBeam technology and calls `layout_check`. KLayout's Python module, SiEPIC-Tools and the EBeam PDK all install from PyPI, so the same call runs on your machine, without the KLayout window:

```python
    import siepic_ebeam_pdk                        # registers the EBeam technology
    from SiEPIC.utils import get_technology_by_name
    from SiEPIC.verification import layout_check
    ly = kdb.Layout()
    ly.read(path)
    ly.TECHNOLOGY = get_technology_by_name("EBeam")
    nets, comps = ly.top_cell().identify_nets()      # the netlist the checks walk along
    n = layout_check(cell=ly.top_cell(), verbose=False, GUI=True, file_rdb=rdb)
```

`layout_check` extracts the netlist, which device connects to which, from the DevRec shapes (68/0) that mark each component and the PinRec pins (1/10) at its ports. It then checks components (overlaps, pins), waveguides, connectivity (disconnected or mismatched pins), and the design-for-test rules along each labelled circuit: label format, distance and uniqueness, coupler orientation and spacing, and the fibre-array configuration. It writes a report database, `.lyrdb`, which KLayout's marker browser (**Tools › Marker Browser**) opens; openEBL's Action uploads the same file.

A pass means something only if the netlist is there, so the script prints its size first. On a first version of the Lab 7 chip, drawn with gdsfactory's plain routes, `layout_check` reported 0 errors but had found 196 components and no connections at all: none of its pieces had pins, so there was no circuit to check, and the green tick was empty. With the pins and DevRec shapes that Lab 7 now draws (Section L7.2), and the PDK's own cells kept exactly as in their GDS files, the same call finds the circuits.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

`python lab08_checks.py --siepic` adds: netlist of 70 components with 63 connections; SiEPIC 0.5.31 and siepic_ebeam_pdk 0.4.53 report 0 errors, in about a second, and write `EBeam_YourName_firstchip.lyrdb`.

</div>

To see what it traces, call SiEPIC-Tools' `trim_netlist(nets, components, gc)` (from `SiEPIC.scripts`) for one coupler: from the loopback's labelled coupler it returns five components, coupler, bend, straight, bend and coupler; from a ring's, eight, with the ring among them.

## <span class="secnum">L8.7</span>Break it on purpose

A check you have never seen fail is a check you cannot trust. `--break` rebuilds the Lab 7 chip with one mistake and runs the checks on it; with `--siepic`, SiEPIC-Tools' verification too.

**Table L8.2. Four mistakes and what catches them,** as `lab08_checks.py --break <mistake> --siepic` prints them.
{: .tabcaption #tab-l8-2 }

| `--break` | The mistake | What fails (this script) | What fails (SiEPIC-Tools) |
|---|---|---|---|
| `gap` | ring200's gap shrunk to 50 nm | space ≥ 70 nm: 6 edge pairs, narrowest 50 nm | nothing (0 errors): `layout_check` has no width or space rules |
| `label` | ring250's label 15 µm below its coupler | label on a coupler (15.0 µm away); every device has a label (ring250 has none) | `opt_in label: too far away` (1 error) |
| `overlap` | spiral2 pushed 60 µm left, onto the MZI | space ≥ 70 nm (26 edge pairs, down to 0 nm where shapes touch); devices do not overlap (mzi and spiral2) | `Overlapping component` (10 errors) |
| `outside` | spiral3 pushed 40 µm right | extent within 605 × 410 µm (614.1 × 390.2 µm); all silicon inside the floorplan (5 pieces outside, up to $$x$$ = 626.5 µm) | nothing (0 errors) |
{: .lab-table }

No single check catches everything. SiEPIC-Tools' verification follows circuits and labels, so it catches the label and the overlap; it has no width or space rules and does not look at the design area. `run_submission_checks.py` catches a chip that is too big, but not one in the wrong place, and has no width or space rules either. Only the DRC deck checks the 50 nm gap, and we found no workflow that runs it: so run it, or this script, yourself. The figure shows the three mistakes of `--break all` at once.

<figure id="fig-l8-1">
  <img src="{{ '/assets/figs/lab08_expected.png' | relative_url }}" style="width:760px" alt="Two copies of the chip layout with the check results drawn on them: the Lab 7 chip with every label on its coupler and all checks passed; and a broken copy with a moved label, a ring gap below the minimum and a spiral outside the floorplan, each circled in red">
  <figcaption><span class="capnum">Figure L8.1.</span> <strong>What the script draws.</strong> (a) The Lab 7 chip: every opt_in label (green) sits on the origin of an input coupler (blue triangles are the coupler ports), and all 40 checks pass. (b) The same chip broken three ways (<code>--break all</code>): ring250's label 15 µm below its coupler (red dot, joined to the nearest coupler), ring200's gap shrunk to 50 nm, and spiral3 pushed 40 µm past the right edge of the floorplan. Red circles mark where the five failed checks point.</figcaption>
</figure>

## <span class="secnum">L8.8</span>Submitting

With the checks passing on your machine, the submission is a few commands. On GitHub, fork the run's repository (the **Fork** button) and enable Actions on the fork; then, in a terminal:

```
git clone https://github.com/<you>/openEBL-2026-10.git
cd openEBL-2026-10
cp ../EBeam_YourName_firstchip.gds submissions/EBeam_YourName_firstchip.gds
git add submissions/EBeam_YourName_firstchip.gds
git commit -m "Add EBeam_YourName_firstchip"
git push
```

Use the run that is open when you submit, and the file-name prefix your course gives you. Watch the **Actions** tab of your fork: a red cross opens to a log, and the `layout-errors` artifact holds the SiEPIC-Tools report. When everything is green, open a pull request to the SiEPIC repository (**Contribute › Open pull request**). The same checks run on it, and a SiEPIC bot greets first-time contributors and asks them to run the functional layout check (V) in KLayout. When it is merged, check that your design appears in the run's merged layout.

## Exercises

1. **Every break.** Run `--break` with `gap`, `label`, `overlap` and `outside` in turn. Which checks fail? Which of them would openEBL's GitHub checks catch, and which only the DRC deck, run by you?
2. **Four couplers.** An add-drop ring ([Section 12.3]({% link chapters/12_rings.md %})) needs four couplers in its column: input, through, drop and add. Using the rules of `DFT.xml`, which coupler must carry the label, and where must the other three be?
3. **Size, not position.** Shift every device 20 µm to the right, and leave the floorplan box where it is. Which check would `run_submission_checks.py` make, and would it pass? Which of this lab's checks fails?
4. **Your own check.** openEBL's prober can only measure what its label names, and a label with someone else's name in it is easy to copy from an example. Add a check that every label's device ID equals your `USER`, and run it on a copy of the chip with one label changed.
5. **Why these rules?** Explain each of these design-for-test rules from the prober's point of view ([Chapters 17]({% link chapters/17_fiberarrays.md %}) and [31]({% link chapters/31_testing.md %})): the couplers are never rotated; at most one coupler above and two below the labelled one; couplers at least 60 µm apart; the label within 10 µm of the coupler's origin.

<details markdown="1">
<summary>Answers</summary>

1. Table L8.2 gives the script's answers. Against openEBL's own checks: the 50 nm gap passes both GitHub checks and is caught only by the DRC deck (its space rule); the moved label is caught by SiEPIC-Tools' verification (`opt_in label: too far away`), which still traces ring250's circuit from the nearest coupler, while this script reports the device as unlabelled; the overlap is caught by SiEPIC-Tools (`Overlapping component`) and by the DRC deck's space rule where the silicon of the two devices comes within 70 nm; and the spiral outside the floorplan is caught by `run_submission_checks.py`, since the chip is now 614.1 µm wide, and by the DRC deck's boundary rule, but not by SiEPIC-Tools.
2. With at most one coupler above the labelled one and at most two below (`detectors-above-laser` 1, `detectors-below-laser` 2), four couplers fit only one way: the label goes on the second coupler from the top, with one coupler 127 µm above it and two at 127 and 254 µm below, all in one column and unrotated. Put the input there, and the through, drop and add ports on the other three; the rule fixes the positions, not which port goes where.
3. `run_submission_checks.py` computes `w > cell_Width or h > cell_Height` from the bounding box of layers 1/0 and 4/0: moving the chip does not change its size (574.1 × 390.2 µm), so it passes. This lab's "all silicon inside the floorplan" fails: the spiral column now reaches 606.5 µm, past the box's edge at 605 µm. So would the DRC deck's `LayerSi.outside(LayerFP)`. Only the size is checked automatically; keep the floorplan box at the origin and everything inside it.
4. After the label loop, for example:

   ```python
   bad = [l["text"] for l in labels if (m := LABEL_RE.match(l["text"])) and m["id"] != "YourName"]
   rep.check("labels carry your name", not bad, "all yours" if not bad else ", ".join(bad))
   ```

   To test it, change one label in a copy with KLayout's module: read the GDS, find the text on 10/0 in the top cell (`top.shapes(ly.find_layer(10, 0))`), set its `text_string`, and `ly.write` the copy. The new check fails for that one label; so does the file-name convention check if you rename the file and not its top cell.
5. The couplers are designed for a fibre tilted one way ("8degOxide" in their name), so a rotated coupler sends its light away from the fibre. The probe station's fibre array has one fibre for the laser and fixed fibres for the detectors at 127 µm spacing, one above and two below it in `DFT.xml`; a coupler outside those places has no fibre over it. Couplers closer than 60 µm can be mistaken for one another while the station searches for the best alignment (SiEPIC-Tools' source says the spacing rule is there so that the station "doesn't get confused"). And the station takes the label's coordinates as the place to put the laser fibre, which is why the label must sit on the coupler's origin, its waveguide port.

</details>

## Going further

- Install SiEPIC-Tools and the EBeam PDK in KLayout (Lab 7, Section L7.7) and run both the functional layout check (V) and the DRC (D) on your file; compare the marker browser's list with this script's output.
- Run `lab08_checks.py` on a design from a past run: every file in the `submissions/` folders of the [openEBL repositories](https://github.com/SiEPIC) is public under the MIT licence. Which of this script's assumptions (labels in the top cell, one device per top-level cell) do they break?
- [Lab 9]({% link labs/lab09_analysis.md %}) analyses the measurements of a chip like this one: the loopback, the MZI's fringes, the three rings and the cutback.
