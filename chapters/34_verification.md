---
title: "34. Verification and Tape-Out"
parent: "Part VII · Design, Simulation and Layout"
nav_order: 34
permalink: /part-7/ch34/
chapter: 34
---

# <span class="chapnum">Chapter 34</span>Verification and Tape-Out

A layout that looks right can still be impossible to make, broken in ways no one can see, or impossible to test. Verification finds these problems before the foundry does: design-rule checks, connectivity and layout-versus-schematic checks, design-for-test rules, and the foundry's own sign-off.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- name what goes wrong between a layout and a working chip, and the check that catches each fault;
- read a rule deck: widths, spaces, notches, enclosures, overlaps, angles, grids and densities;
- explain how a DRC engine finds violations with edges, edge pairs, sizing and polygon Booleans;
- write a small KLayout rule deck, run it without the user interface, and read its report;
- tell real errors from the false errors that curved photonic shapes produce, and handle waivers;
- check a photonic circuit's connectivity and compare its extracted netlist with the intended circuit;
- prepare a design for a multi-project wafer run: derived layers, fill, test labels and the tape-out package.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you know, before the chips come back, that the file you send is the chip you meant?

</div>

## <span class="secnum">34.1</span>What can go wrong

A foundry builds what the file says, not what the designer meant. [Table 34.1](#tab-34-1) lists the faults that most often separate the two. Some are features the process cannot print: a line narrower than the lithography resolves breaks or disappears, a gap too narrow closes, and loose fragments can land on other designs, which is one reason a foundry usually rejects a layout that is not clean {% include cite.html keys="klayoutdrc" %}. Others leave the geometry printable but the circuit wrong: a waveguide that stops 50 nm short of a port looks perfect at normal zoom. A shape on a layer the process does not have is simply ignored, since the masks are derived from named layers ([Section 34.8](#sec-34-8)); a misspelled test label leaves a working device that the automated probe station cannot measure ([Chapter 36]({% link chapters/36_testing.md %})); and a file with two top cells, or with cell names that collide with another designer's, may be rejected outright.

**Table 34.1. What goes wrong, and what catches it.**
{: .tabcaption #tab-34-1 }

| Fault | Example | Caught by | Section |
|---|---|---|---|
| Unmanufacturable geometry | 120 nm line; 160 nm gap; acute taper tip; sliver | design-rule check (DRC) | 34.2–34.5 |
| Manufacturable but wrong for the process | slab enclosing a rib by too little; metal barely overlapping a heater | two-layer DRC rules | 34.2, 34.4 |
| Broken optical connection | component moved 50 nm after routing; 350 nm waveguide on a 500 nm port | connectivity check, LVS | 34.6 |
| Wrong circuit | arm-length difference not the one simulated; device missing | layout versus schematic (LVS), extracted simulation | 34.6 |
| Untestable device | label missing or misspelled; coupler rotated or off pitch | design-for-test check | 34.7 |
| Uneven etch or polish | large empty regions, very dense blocks | density rule, fill | 34.8 |
| Malformed or misplaced file | two top cells; unknown layer; off-grid vertex; design outside its area | file checks at submission | 34.8 |

The cost of a fault found late is mostly time. A multi-project wafer (MPW) run shares one mask set among many designs, so a design that misses a run waits for the next: openEBL runs come about three times a year (see [Lab 8]({% link labs/lab08_submit.md %})) {% include cite.html keys="openebl" %}, so a design rejected at submission loses about four months, and a design that is accepted but broken loses the run and the measurement time as well. Worse, a broken layout produces data that look like device physics: a disconnected waveguide is easily mistaken for a lossy one.

Verification is therefore a set of checks, each looking for one kind of fault, run by the designer after every change and repeated by the foundry or the run's automated checks ([Figure 34.1](#fig-34-1)). No single check sees everything: [Lab 8]({% link labs/lab08_submit.md %}) shows a 50 nm gap that only the DRC deck catches and a misplaced label that only SiEPIC-Tools catches.

<figure id="fig-34-1">
  <img src="{{ '/assets/figs/ch34_flow.svg' | relative_url }}" style="width:680px" alt="Flow diagram. A layout block on the left feeds five checks stacked in a column: design-rule check (widths, gaps, enclosures, angles, grid, density), connectivity (pins meet, widths match, no overlapping cells), layout versus schematic (extracted netlist equals intended circuit), design for test (labels, coupler pitch and orientation) and extracted simulation (lengths and bends as drawn). Their results join at a diamond labelled markers reviewed. A red path returns from the diamond to the layout, labelled error: fix the layout, run every check again; a violet note above the diamond says false or intended: waive, with a reason. A clean arrow leads to foundry sign-off (layer map and derived masks, density and fill, manufacturing grid, die size and keep-outs, the foundry's DRC) and then to the tape-out package (GDS or OASIS file, layer map, DRC report, waivers, design notes, test plan), which goes to the foundry's MPW run.">
  <figcaption><span class="capnum">Figure 34.1.</span> <strong>The verification flow.</strong> The designer runs five kinds of check on the layout after every change. Each marker they report is either an error, fixed in the layout before everything is run again, or a false or intended violation, waived with a written reason. A clean layout then passes the foundry's sign-off checks and leaves as a tape-out package. Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">34.2</span>Design rules

A **design rule** is a geometric condition that the process can meet reliably. Each comes from a physical limit ([Chapter 35]({% link chapters/35_fab.md %})): lithography cannot resolve features below a certain size and rounds corners; etching narrow trenches is slower and less reliable than etching open areas; two masks never align perfectly, so a shape on one layer must overlap or enclose a shape on another with some margin; and chemical-mechanical polishing (CMP) leaves dense and sparse areas at different heights. The rules are collected in the process design kit ([Chapter 30]({% link chapters/30_flow.md %})), and as a **rule deck**, a script that checks them, for the verification tool.

[Figure 34.2](#fig-34-2) draws each common kind of rule with a violation, and [Table 34.2](#tab-34-2) lists them with their reasons. Most foundry rule values are under non-disclosure agreements. The open SiEPIC EBeam PDK's deck, for its electron-beam process, sets a minimum silicon width of 60 nm and a minimum space of 70 nm {% include cite.html keys="ebeampdk" %}; processes using deep-ultraviolet lithography have larger minima, since dry 248 and 193 nm tools print features down to about 100–150 nm ([Chapter 35]({% link chapters/35_fab.md %})). The examples in this chapter use an illustrative "toy" SOI process with round numbers of that order, not any foundry's.

<figure id="fig-34-2">
  <img src="{{ '/assets/figs/ch34_rules.svg' | relative_url }}" style="width:680px" alt="Twelve small drawings in three rows of four, each with its violation marked in red. (a) Width: a waveguide with a narrow neck, w less than w min. (b) Space: two parallel waveguides too close. (c) Notch: one polygon with a narrow slot. (d) Enclosure: a slab around a rib core, too narrow on the top side (red) and wide enough on the bottom (teal). (e) Overlap: a metal pad overlapping the end of a heater by too little. (f) Extension: an implant that ends barely beyond the end of a waveguide. (g) Area and holes: a tiny isolated square and a tiny hole in a large shape, both circled. (h) Density: a dashed window containing two thin lines, rho equals silicon area over window area, below the minimum. (i) Acute angle: a taper drawn to a sharp point, with the tip angle marked. (j) Off-grid vertex: a polygon on a grid of dots with one corner between grid points. (k) Self-intersection: a four-point outline whose edges 2 to 3 and 4 to 1 cross. (l) Zero-width spike: a line going out from a rectangle and back along itself.">
  <figcaption><span class="capnum">Figure 34.2.</span> <strong>Twelve kinds of design rule</strong>, each drawn with a violation (red). (a)–(c) single-layer dimension rules: a width inside one shape, a space between two shapes, and a notch, the space inside one shape. (d)–(f) two-layer rules: enclosure, overlap and extension. (g)–(h) area and density rules. (i)–(l) shape rules: acute angles, vertices off the manufacturing grid, outlines that cross themselves, and zero-width spikes. Schematic, not to scale. Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

**Table 34.2. Kinds of design rule, why they exist, and the rules of this chapter's example deck.**
{: .tabcaption #tab-34-2 }

| Rule | What is measured | Why it exists | Example deck (toy process) |
|---|---|---|---|
| Width | distance across a shape | narrow lines print thin, break or lift off | Si ≥ 150 nm (SI.W.1) |
| Space | distance between two shapes | narrow gaps close or etch incompletely | Si ≥ 200 nm (SI.S.1) |
| Notch | space inside one shape | as space; slots and corrugations | Si ≥ 200 nm (SI.N.1) |
| Enclosure | how far one layer extends around another | mask misalignment; e.g. the slab around a rib | slab around Si ≥ 1 µm (SLAB.EN.1) |
| Overlap | width of the overlap of two layers | contact area; e.g. metal on a heater | metal on heater ≥ 1 µm (M.OV.1) |
| Extension | how far a shape continues past another's edge | misalignment at ends; e.g. an implant past a waveguide | (not in the deck) |
| Area, hole area | area of a shape or a hole | tiny islands and holes do not print or lift off | Si shape ≥ 0.1 µm² (SI.A.1) |
| Density | fraction of a window covered | etch loading, polishing | Si 20–80 % in 100 µm windows (Section 34.8) |
| Acute angle | angle at a convex corner | sharp tips round off and break | no Si corner under 30° (SI.ANG.1) |
| Grid | vertex coordinates | the mask writer's address grid | vertices on a 5 nm grid (SI.GRID.1) |
| Polygon validity | outline crosses or overlaps itself | ambiguous inside and outside | none (SI.ODD.1) |
| Placement | shapes inside the design area | the die is shared | Si inside the floorplan (SI.FP.1) |

Some rules are **recommended** rather than required: breaking them is allowed but lowers yield. Photonic designs also push rules that electronic designs rarely touch. The gap of a directional coupler or a ring ([Chapters 9]({% link chapters/09_couplers.md %}) and [12]({% link chapters/12_rings.md %})) sets its coupling exponentially, so designers place it deliberately at or near the minimum space; the corrugations of a Bragg grating ([Chapter 13]({% link chapters/13_bragg.md %})) are notches by definition; and nearly every photonic shape is curved, which, as Section 34.5 shows, produces violations that are not real.

## <span class="secnum">34.3</span>How a DRC engine works

A DRC engine does not look at pictures. It works on polygons and their edges, with a few operations from which every rule is built {% include cite.html keys="klayoutdrc" %}:

- **Merging and Booleans.** Shapes on a layer are first **merged**: overlapping or touching polygons, from any cell of the hierarchy, become one region. AND, OR, NOT and XOR between layers produce new regions. Efficient engines sweep a line across the layout and keep only the edges it crosses, so that the work grows as $$N\log N$$ with the number of edges $$N$$ rather than as $$N^2$$ {% include cite.html keys="lauther1981" %}.
- **Edges and edge pairs.** Each polygon is a closed list of oriented edges (in KLayout clockwise, so the inside is on the right of each edge). A **width check** looks for pairs of edges of the same shape whose inner sides face each other and that come closer than the rule; a **space check** looks for pairs whose outer sides face each other. Each violation is reported as an **edge pair**, the two offending pieces of edge, which the viewer draws as a marker ([Figure 34.3](#fig-34-3)a).
- **Sizing.** Growing or shrinking every edge by a distance is the other basic tool. Shrinking a shape by half the minimum width and growing it back removes every part narrower than the minimum; what the original has and the regrown shape lacks is the violation ([Figure 34.3](#fig-34-3)b). Sizing also draws keep-out zones and fill areas (Section 34.8).

Two settings change what counts as a violation. The **metric**: with the Euclidean metric (KLayout's default) the distance between two edges is the shortest distance between any of their points, so two shapes that only meet corner to corner can violate a space rule; with the projection metric only the parts of the edges that face each other count ([Figure 34.3](#fig-34-3)c). The **angle limit**: two edges meeting at a corner are, near the corner, arbitrarily close, so a width check would flag every corner. KLayout therefore skips edge pairs that enclose an angle of 90° or more by default; a corner sharper than 90°, even 89°, is still checked and always fails {% include cite.html keys="klayoutdrc" %}. The SiEPIC EBeam deck lowers the limit to 80° for this reason {% include cite.html keys="ebeampdk" %}.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Width, space and density checks</div>

An edge pair $$(e_1, e_2)$$ violates a width rule $$w_\mathrm{min}$$ if the edges belong to one shape, their inner sides face each other, and

$$d(e_1, e_2) = \min_{\mathbf{p}\in e_1,\ \mathbf{q}\in e_2} \lVert\mathbf{p}-\mathbf{q}\rVert < w_\mathrm{min} ;$$

a space rule is the same with outer sides facing. The density of a layer in a window $$W$$ is

$$\rho_W = \frac{A(\mathrm{layer}\cap W)}{A(W)}, \qquad \rho_\mathrm{min} \le \rho_W \le \rho_\mathrm{max} \ \text{for every window.}$$

</div>

<figure id="fig-34-3">
  <img src="{{ '/assets/figs/ch34_engine.svg' | relative_url }}" style="width:640px" alt="Three panels computed with KLayout. (a) A dog-bone shape, two 1 micrometre squares joined by a 120 nanometre neck, with arrows on every edge showing their clockwise direction and a red rectangle marking the edge pair along the neck: one edge pair below 150 nm. (b) The same shape shrunk by 75 nm on every side (blue squares, inside the dashed original outline); the neck has vanished, and the difference between the original and the shape grown back is the neck itself, in red. (c) Three rectangles: two stacked 150 nm apart face to face, marked by both a red Euclidean and a dashed blue projection marker; and a third diagonally offset so that its corner is 141 nm from a corner of the first, marked only by the red Euclidean marker.">
  <figcaption><span class="capnum">Figure 34.3.</span> <strong>Two ways to find a narrow neck, and two metrics.</strong> (a) Edges run clockwise with the inside on their right; the width check finds the pair of neck edges 120 nm apart, below a 150 nm rule. (b) Shrinking by 75 nm and growing back (sizing) removes the neck; the difference is the violation. (c) A 200 nm space rule: two rectangles 150 nm apart face to face violate it in both metrics, while a corner 141 nm from another corner violates it only in the Euclidean metric. All shapes and results from KLayout's Region API (<code>figsrc/ch34_drc.py engine</code>). Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

Large layouts need two more tricks. A ring placed a hundred times need only be checked once, plus its surroundings, which KLayout's hierarchical "deep" mode exploits; its "tiled" mode evaluates the layout tile by tile, spread over several processor cores {% include cite.html keys="klayoutdrc" %}.

## <span class="secnum">34.4</span>Running DRC in KLayout

KLayout's DRC scripts are written in a small language built on Ruby {% include cite.html keys="klayout,klayoutdrc" %}. A layer is fetched with `input(layer, datatype)`; a check is a method of the layer, such as `width` or `space`; and `output` sends its markers to a **report database** (a `.lyrdb` file) under a rule name and a description. Here is the whole deck of the toy process, the script inside `figsrc/ch34_deck.lydrc`; every function and option in it is checked against KLayout's DRC reference {% include cite.html keys="klayoutdrc" %}:

```ruby
source($input)                      # the layout to check (-rd input=...)
report("Chapter 34 toy SOI deck", $report)

si   = input(1, 0)     # silicon core (full etch)
slab = input(2, 0)     # slab kept by the partial etch (rib waveguides)
htr  = input(11, 0)    # heater
mtl  = input(12, 0)    # metal routing and pads
fp   = input(99, 0)    # floorplan: the design area

# dimension rules: a value is an error when it is LESS than the rule
si.width(150.nm).output("SI.W.1", "Si width >= 150 nm")
si.isolated(200.nm).output("SI.S.1", "Si space between shapes >= 200 nm")
si.notch(200.nm).output("SI.N.1", "Si space within one shape (notch) >= 200 nm")

# shape rules
si.with_area(nil, 0.1).output("SI.A.1", "Si shape area >= 0.1 um2")
si.corners(-180.0 .. -150.0).output("SI.ANG.1", "No convex Si corner sharper than 30 deg")
si.ongrid(5.nm).output("SI.GRID.1", "Si vertices on the 5 nm manufacturing grid")
si.odd_polygons.output("SI.ODD.1", "No self-intersecting Si polygons")

# placement and two-layer rules
(si - fp).output("SI.FP.1", "Si inside the floorplan")
slab.enclosing(si, 1.um).output("SLAB.EN.1", "Slab encloses Si by >= 1 um")
mtl.overlap(htr, 1.um).output("M.OV.1", "Metal overlaps heater by >= 1 um")
```

A few lines need a word. `isolated` is the space check between different shapes and `notch` the one within a shape; `space` would do both. `with_area(nil, 0.1)` selects shapes with an area below 0.1 µm². `corners` measures the turn at each vertex: KLayout's outlines run clockwise, so a convex corner is a right turn, a negative angle, and a turn sharper than −150° is a corner whose inside angle is below 30°. `ongrid` reports every vertex not on the grid, and `odd_polygons` every outline that crosses or overlaps itself. `si - fp` is a Boolean NOT: whatever silicon lies outside the floorplan.

The deck runs without the user interface (`-b`, batch mode, which also skips reading and writing the configuration file), with `-rd` defining the Ruby variables `$input` and `$report` {% include cite.html keys="klayoutdrc" %}:

```
klayout -b -r ch34_deck.lydrc -rd input=ch34_test.gds -rd report=ch34_test.lyrdb
```

The report opens in KLayout's marker browser, or can be read as XML, as `figsrc/ch34_drc.py parse` does. The test layout, made by `figsrc/ch34_drc.py make` with KLayout's Python module, holds fourteen features on a 90 × 58 µm floorplan, most with one deliberate mistake ([Figure 34.4](#fig-34-4)). We ran the deck with the KLayout application, version 0.30.5, and ran the same ten rules again through the Python module's `Region` class, version 0.30.13 (`ch34_drc.py check`), which exposes the same engine:

```python
si = kdb.Region(top.begin_shapes_rec(ly.layer(1, 0)))     # all silicon, merged, in 1 nm units
si.width_check(150).count(), si.isolated_check(200).count(), si.grid_check(5, 5).count()
```

The two agree rule by rule.

<figure id="fig-34-4">
  <img src="{{ '/assets/figs/ch34_markers.svg' | relative_url }}" style="width:720px" alt="(a) The 90 by 58 micrometre test layout inside a dashed floorplan, with red DRC markers. Row A at the top: A1 a 500 nm waveguide (clean); A2 a 120 nm waveguide (SI.W.1); A3 a taper drawn to a point (SI.W.1 and SI.ANG.1); A4 a taper with a 180 nm tip (clean); A5 a waveguide crossing the floorplan's right edge (SI.FP.1). Row B: B1 a coupler with a 200 nm gap (clean); B2 a coupler with a 160 nm gap (SI.S.1); B3 a Bragg grating (SI.N.1 times 18); B4 a tiny square (SI.A.1); B5 a self-intersecting shape (SI.ODD.1 once, SI.W.1 six times, SI.N.1 four times, SI.ANG.1 four times). Row C: C1 a ring covered in red dots (SI.GRID.1 times 272) and C2 a ring with a wrap-around bus coupler, red markers in its gap (SI.S.1 times 58 and SI.W.1 twice). Row D: D2 a heater with metal pads (M.OV.1 at the right pad) and D1 a rib waveguide in its slab (SLAB.EN.1). Scale bar 10 micrometres. Below, three close-ups: (b) C2's gap with red edge-pair markers across it at several vertices; (c) B3's grating with red markers in every notch between teeth, top and bottom; (d) B5, two thin triangles meeting at a point, covered by overlapping red markers.">
  <figcaption><span class="capnum">Figure 34.4.</span> <strong>The example deck on its test layout.</strong> (a) Fourteen features (blue silicon, light slab, orange heater, yellow metal) and the 373 markers the deck reports (red), labelled with their rules; A1, A4 and B1 are clean. (b)–(d) Close-ups: the pulley coupler C2, drawn with its gap at exactly the 200 nm minimum and its vertices snapped to the 5 nm grid, where the snapping narrows the gap below 200 nm at some vertices; the notches between the teeth of the Bragg grating B3; and the shape B5, whose outline crosses itself. Geometry from <code>figsrc/ch34_drc.py</code>; markers from the report of <code>figsrc/ch34_deck.lydrc</code> run by KLayout 0.30.5. Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 34.1 · Reading a DRC report</div>

The deck reports 373 markers in ten rules: SI.W.1 10, SI.S.1 59, SI.N.1 22, SI.A.1 1, SI.ANG.1 5, SI.GRID.1 272, SI.ODD.1 1, SI.FP.1 1, SLAB.EN.1 1 and M.OV.1 1. Sorted by feature rather than by rule, they tell a shorter story:

- **Real errors, nine of them, 295 markers.** The 120 nm waveguide (A2, one width marker). The taper drawn to a point (A3): its tip angle is $$2\arctan(0.25/9) = 3.2°$$, and it is narrower than 150 nm over its last $$9 \times 150/500 = 2.7$$ µm, so it fails both the width and the angle rules; the taper with a 180 nm tip (A4) passes both. The waveguide crossing the floorplan (A5), the 160 nm coupler gap (B2) and the 0.04 µm² square (B4), one marker each. One shape whose outline was built from its top edge and its bottom edge without reversing the second (B5): it becomes two slivers touching at a point, and that single mistake trips four rules with 15 markers. One ring drawn without snapping (C1): 272 off-grid vertices, one marker each, all from one mistake. The slab around the rib (D1) is 1.0 µm wide below the waveguide, which passes, and 0.5 µm above it, which fails; the right contact pad (D2) overlaps the heater by 0.5 µm.
- **Intended, 18 markers.** The Bragg grating (B3) has teeth 160 nm long and 160 nm apart: each of the 9 gaps on each side is a notch narrower than 200 nm. The corrugation is the device. The lithography will round it, so the deck is right to warn, but the fix is a waiver or a grating cell from the PDK, not a redesign.
- **False, 60 markers.** The pulley coupler (C2) has its gap drawn at exactly 200 nm and every vertex snapped to the 5 nm grid; snapping moves the vertices by up to 2.5 nm in each direction, and the gap dips to 197.8 nm at some of them (58 space markers). At the two cut ends of the bus, edges meet at angles just below 90° (87.4° at one chord after snapping), which the width check examines and flags (2 markers). Section 34.5 explains both and why neither matters optically.

The clean features show what the rules do *not* flag: the coupler B1, with its straight gap at exactly 200 nm, passes, because a violation is a distance below the rule. Two lessons: count **mistakes**, not markers (here 9 errors behind 295 markers), and fix the shapes that break several rules first, since they are usually malformed rather than merely too small.

</div>

## <span class="secnum">34.5</span>Curved geometry, grids and waivers

Electronic layouts are mostly rectangles; photonic layouts are mostly curves. A GDS file stores a curve as a polygon whose vertices are integers in the **database unit**, often 1 nm, and the foundry's mask writer works on a **manufacturing grid** that may be the same or coarser. [Chapter 33]({% link chapters/33_layout.md %}) (Section 33.5) shows how a curve is discretised and snapped; here the question is what the checks make of the result. Three effects produce markers that are not real errors {% include cite.html keys="cao2014drc,orcutt2010" %}:

- **Chords.** Each segment of a polygonal arc lies inside the true circle by the sagitta $$R(1-\cos(\Delta\theta/2))$$: 1.25 nm for the outer edge of a ring of radius 5.25 µm drawn with 2.5° steps. Two concentric arcs drawn with different steps, as a ring and its wrap-around bus usually are, then come closer than intended between vertices.
- **Rounding and snapping.** Every vertex moves to the grid, by up to half a grid step in each direction. A gap or a width drawn at exactly the rule then falls a fraction of a nanometre, or a few nanometres, below it at some vertices.
- **Corners near 90°.** A corner meant to be square is often slightly acute once a curve is a polygon: at the radial cut end of an arc drawn in 1° steps, the end edge and the first chord of the outer edge meet at 89.5°, and snapping tilts short chords by a degree or more either way. A width check with the default 90° angle limit examines edges meeting below 90°, and near their corner they are always closer than the minimum.

<figure id="fig-34-5">
  <img src="{{ '/assets/figs/ch34_curved.svg' | relative_url }}" style="width:720px" alt="(a) Ring C1 of the test layout with all its 288 vertices: 272 red dots off the 5 nm grid and 16 teal circles on it, the latter near 0, 90, 180 and 270 degrees. (b) A 20 by 20 nanometre square around one vertex: a fine 1 nm grid and a coarser 5 nm grid, the exact vertex position (a cross), the stored position rounded to 1 nm (red dot, almost on the cross) and the position snapped to 5 nm (teal circle, about 3 nm away, joined by an arrow). (c) The gap between the ring and its wrap-around bus at each ring vertex under the bus, from 226 to 314 degrees: exact vertices (grey) between 199.8 and 200.0 nm; rounded to 1 nm (blue) between 199.3 and 200.2 nm; snapped to 5 nm (red) jumping between 197.8 and 202.2 nm; dashed line at the 200 nm rule and dotted line at 198 nm, the rule with 2 nm of tolerance.">
  <figcaption><span class="capnum">Figure 34.5.</span> <strong>Curves on a grid make false errors.</strong> (a) The unsnapped ring C1 (radius 5 µm, width 500 nm, a vertex every 2.5°, rounded to the 1 nm database unit): 272 of its 288 vertices are off a 5 nm grid. (b) One vertex: rounding to 1 nm moves it by less than 0.5 nm, snapping to 5 nm by up to 2.5 nm in x and y. (c) The gap of the pulley coupler C2, drawn at exactly the 200 nm minimum, at each ring vertex under its bus. With exact vertices the bus's 1° chords already bring it to 199.79 nm; rounding to 1 nm gives down to 199.3 nm (92 space markers at 200 nm, none at 198 nm); snapping to 5 nm gives 197.8 to 202.2 nm (58 markers at 200 nm, 8 at 198 nm, none at 195 nm). Counts from KLayout's space check (<code>figsrc/ch34_drc.py pulley</code>); gaps computed in <code>figsrc/ch34_figs.py</code>, which draws the figure.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 34.2 · A ring drawn without snapping</div>

Ring C1 has a centre radius of 5 µm and a width of 500 nm, with a vertex every 2.5°: 144 vertices on each edge, 288 in all. Computed in floating point and rounded only to the 1 nm database unit, a vertex lands on a 5 nm grid only if both of its coordinates happen to be multiples of 5 nm. For coordinates that fall at random, that chance is $$(1/5)^2 = 1/25$$, so about $$288 \times 24/25 = 276$$ vertices should be off the grid. Counting them in the drawn ring gives 272 off and 16 on, which is exactly what the deck's `ongrid(5.nm)` reported (SI.GRID.1): 94 %. The 16 on-grid ones are the vertices on the axes and a few near them. No amount of extra vertices fixes this; only drawing on the 5 nm grid does.

Snapping every vertex to 5 nm removes the 272 markers but moves each vertex by up to 2.5 nm in x and in y. On the pulley coupler C2, drawn at the 200 nm minimum, the gap at the ring's vertices then ranges from 197.8 to 202.2 nm, and the deck reports 58 space violations. Does a 2.2 nm dip matter? The coupling of two waveguides falls off with the gap roughly as $$e^{-\gamma g}$$, with $$\gamma \approx k_0\sqrt{n_\mathrm{eff}^2-n_\mathrm{clad}^2} = (2\pi/1.55\ \mu\mathrm{m})\sqrt{2.446^2-1.444^2} = 8.0\ \mu\mathrm{m}^{-1}$$ for the 500 × 220 nm strip of [Chapter 6]({% link chapters/06_soi.md %}). A 2.2 nm dip raises the local coupling by about $$8.0 \times 0.0022 = 1.8$$ %, at a few isolated points. Averaged over ±30° around the coupling point, where most of the coupling happens, the gap is 199.90 nm for exact vertices and 199.77 nm after snapping: a change of 0.13 nm, far below the 1.5 nm die-to-die width variation of [Chapter 35]({% link chapters/35_fab.md %}). The violations are false. A 2 nm tolerance in the rule leaves 8 of the 58, a 5 nm tolerance none.

</div>

There are four ways to deal with false errors, and they can be combined:

1. **A tolerance in the rule.** The SiEPIC EBeam deck checks its 60 nm and 70 nm rules 2 nm below their values, with a comment that designers aim for exactly the minimum {% include cite.html keys="ebeampdk" %}. A tolerance is blunt: it also passes a real 198.5 nm gap.
2. **A lower angle limit**, so that corners a little below 90° are not examined: the EBeam deck uses 80°.
3. **Drawing for the rules.** Generate curves directly on the manufacturing grid, keep ports on grid points and at multiples of 90° where possible, and do not draw gaps and widths at exactly the minimum unless the device needs it. Equation-based checks in commercial verification tools measure curved edges against the intended curve instead of the polygon, which removes most of these errors at the source {% include cite.html keys="cao2014drc" %}.
4. **Waivers.** A waiver records that a specific marker was reviewed and accepted, with the reason. In KLayout, markers are waived in the marker browser and saved as a waiver database (the report's name with `.w` added); later runs apply the waivers to markers with the same shape, rule and cell, so renaming a cell silently drops them {% include cite.html keys="klayoutdrc" %}. Foundries accept waivers only for rules they agree can be broken, and the waivers travel with the design (Section 34.8).

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">A waiver is a decision, not a filter</div>

Waive a marker only when you can say why it does no harm, write that reason down, and check the waiver again after every change to the layout. Waiving all markers of a rule because most are false hides the one that is real, and a deck with large tolerances does the same thing silently. If a device type always produces the same violations (grating teeth, coupler gaps, taper tips), the better fix is a PDK cell that the foundry has qualified, or a marker layer that tells the deck which rule applies there.

</div>

## <span class="secnum">34.6</span>Connectivity and layout versus schematic

DRC checks shapes; it does not know that a shape is a waveguide meant to join two devices. In electronics, **layout versus schematic** (LVS) extracts the devices and the nets that connect them from the layers of the layout, and compares the resulting netlist with the schematic's. Photonics needs the same, with differences {% include cite.html keys="pond2014flow,bogaerts2018" %}:

- **Devices are cells, not layer combinations.** A transistor is recognised where polysilicon crosses an active area; a Y-branch or a grating coupler is a PDK cell, recognised by a device-recognition shape and by **pins** at its ports. SiEPIC-Tools draws these as DevRec (layer 68/0) and PinRec (1/10) shapes, and builds the netlist by matching pins that coincide {% include cite.html keys="siepictools" %}.
- **Nets are point-to-point.** An optical net joins exactly two ports; a waveguide is itself a component with two pins.
- **Parameters matter as much as topology.** A ring with the right connections but the wrong gap, or an MZI with the wrong arm-length difference, is the wrong circuit. Photonic LVS must therefore extract lengths, widths, radii and gaps, including those of curved shapes {% include cite.html keys="cao2015lvs" %}.

SiEPIC-Tools' `layout_check`, which openEBL's automated checks run ([Lab 8]({% link labs/lab08_submit.md %})), extracts the netlist and checks four groups of things: **components** (none found, shapes outside any component, flattened cells, overlapping DevRec shapes, invalid pins), **waveguides** (paths, bend radius, enough points in bends, ends that can meet a pin), **connectivity** (disconnected pins, connected pins of different widths), and the **design-for-test** rules of Section 34.7 {% include cite.html keys="siepictools" %}. It has no width or space rules: those belong to the DRC deck.

To see what each kind of check finds, `figsrc/ch34_connect.py` builds an MZI from the EBeam PDK's cells with SiEPIC-Tools' routing functions, then three copies with one mistake each, and runs `layout_check` and the EBeam deck's silicon width and space rules (60 and 70 nm, 2 nm tolerance, 80° angle limit, couplers excluded) on all four ([Figure 34.6](#fig-34-6), [Table 34.3](#tab-34-3)).

<figure id="fig-34-6">
  <img src="{{ '/assets/figs/ch34_connect.svg' | relative_url }}" style="width:720px" alt="(a) Top view of an MZI test circuit made of SiEPIC EBeam PDK cells: two grating couplers 127 micrometres apart on the left, each feeding a Y-branch through a 20 micrometre waveguide, and two arms joining the Y-branches, the longer reaching out to x of about 105 micrometres. Dashed outlines mark each cell's DevRec shape and teal dots its pins. Red circles numbered 1 to 3 mark the second Y-branch's input, the first waveguide and the middle of the long arm. (b) Close-up 1: after the second Y-branch was moved 50 nm upward, its silicon is offset by 50 nm from the waveguide's end; the pins at the joint are red. Note: SiEPIC-Tools reports 6 disconnected pins and opt_in label missing; netlist 5 of 8 nets; DRC finds no width or space error. (c) Close-up 2: a 350 nm waveguide meeting the 500 nm input of the Y-branch, with teal pins at the joint. Note: 2 mismatched pins, pin widths 500 and 350; 8 of 8 nets; DRC clean. (d) Close-up 3: a stray Y-branch lying across the long arm, the overlap of their DevRec shapes shaded red, the stray cell's pins red. Note: 1 overlapping component and 3 disconnected pins; DRC 5 space errors.">
  <figcaption><span class="capnum">Figure 34.6.</span> <strong>Connectivity errors that DRC cannot see.</strong> (a) An MZI test circuit of eight cells (two grating couplers, two Y-branches, four waveguides) from the SiEPIC EBeam PDK, routed with SiEPIC-Tools, with its DevRec outlines and pins; the netlist has 8 nets. (b) Moving the second Y-branch by 50 nm after routing leaves its three pins and the three waveguide ends open. (c) Routing the input with a 350 nm waveguide type joins pins of different widths. (d) A stray Y-branch dropped on the long arm overlaps it. Teal: pins on a net; red: pins left open. Layout and results from SiEPIC 0.5.31, siepic_ebeam_pdk 0.4.53 and KLayout 0.30.13 (<code>figsrc/ch34_connect.py</code>); PDK cells MIT licence {% include cite.html keys="ebeampdk,siepictools" %}. Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

**Table 34.3. One mistake each: what DRC and SiEPIC-Tools report.**
{: .tabcaption #tab-34-3 }

| Layout | EBeam width / space markers | SiEPIC-Tools `layout_check` | Extracted netlist |
|---|---|---|---|
| as routed | 0 / 0 | 0 errors | 8 components, 8 nets |
| second Y-branch moved 50 nm after routing | 0 / 0 | 6 disconnected pins; 1 "opt_in label: missing" | 8 components, 5 nets |
| input routed with a 350 nm waveguide type | 0 / 0 | 2 mismatched pins (500 and 350 nm) | 8 components, 8 nets |
| stray Y-branch on the long arm | 0 / 5 | 1 overlapping component; 3 disconnected pins | 9 components, 8 nets |

The first two mistakes are invisible to DRC: the silicon still overlaps where the Y-branch moved, and a 350 nm waveguide is a legal shape. Yet the first breaks three of the circuit's eight optical connections, and since the circuit traced from the labelled coupler now stops after one waveguide, the remaining devices also appear unlabelled. The second makes an abrupt step in width that scatters and reflects light at both ends of the waveguide.

**Comparing with the intended circuit.** The netlist extracted from the layout can be compared with the schematic, the netlist the circuit was simulated with ([Chapter 30]({% link chapters/30_flow.md %})). In the moved-Y-branch layout the comparison finds the three nets from the second Y-branch (`opt1`, `opt2`, `opt3`) missing. Parameters are compared too: the extracted arm lengths are 128.397 µm and 209.397 µm, so the arm-length difference is 81.0 µm, and with $$n_g$$ = 4.18 the free spectral range is $$\lambda^2/(n_g\,\Delta L) = (1.55\ \mu\mathrm{m})^2/(4.18 \times 81.0\ \mu\mathrm{m}) = 7.1$$ nm. Had the schematic asked for the 100 µm of Chapter 30 (a 5.7 nm FSR), the topology would match and only the parameter comparison would catch the difference. This is the argument for **schematic-driven layout**, in which the layout is generated from the circuit netlist or checked against it continuously, and for simulating the netlist extracted from the layout rather than the one drawn by hand {% include cite.html keys="pond2014flow,bogaerts2018" %}.

**Electrical LVS.** Heaters ([Chapter 18]({% link chapters/18_thermal.md %})), modulators ([Chapter 20]({% link chapters/20_modulators.md %})) and photodiodes ([Chapter 21]({% link chapters/21_pd.md %})) add an ordinary electrical circuit, which is checked the electronic way. Conducting layers (doped silicon, heater metal, vias, routing metal, pads) are connected through their contacts; devices are extracted (a heater as a resistor, a PN junction as a diode or capacitor); and the netlist is compared with the intended one. KLayout's LVS, built on its DRC language since version 0.26, does this, and its resistor extractor computes the resistance as the number of squares times the sheet resistance {% include cite.html keys="klayoutlvs" %}: the 20 µm × 2 µm heater of the test layout (D2) is 10 squares. Electrical LVS catches shorts between neighbouring heaters, open contacts, pads assigned to the wrong device, and pads that do not match the probe card or wire-bond plan.

## <span class="secnum">34.7</span>Design-for-test rules

A chip from an MPW run is measured by an automated probe station that aligns a fibre array to each circuit in turn ([Chapters 17]({% link chapters/17_fiberarrays.md %}) and [36]({% link chapters/36_testing.md %})). It can only measure what it can find, so the layout carries machine-readable instructions and obeys the geometry of the fibre array. The SiEPIC EBeam PDK writes these rules in its `DFT.xml` file, and SiEPIC-Tools checks them along each labelled circuit {% include cite.html keys="ebeampdk,siepictools" %}:

- **Test labels.** Each circuit has one text label on the text layer, of the form `opt_in_TE_1550_device_<designer>_<name>`, giving polarisation, wavelength and a unique name. It must lie within 10 µm of the input coupler's port; the station places the laser fibre there.
- **Coupler geometry.** Grating couplers sit in one column on the 127 µm pitch of the fibre array, all unrotated (the couplers are designed for a fibre tilted one way); at most one coupler above and two below the labelled one, matching the array's detector fibres; and couplers of different circuits at least 60 µm apart, so that the station cannot lock onto the wrong one.
- **Test structures.** A loopback (two couplers joined by a waveguide) beside each group of devices calibrates the coupler response ([Chapter 37]({% link chapters/37_analysis.md %})); cut-back sets of waveguides of different lengths give propagation loss; and every label is different, so that data cannot be attributed to the wrong device.

For electrical probing the same applies to pads: on the probe's pitch, in the order the probe card expects, and away from the fibre array's body. [Lab 8]({% link labs/lab08_submit.md %}) checks a whole chip against these rules with 40 checks of its own and SiEPIC-Tools' verification, and breaks the chip on purpose to see each check fire.

## <span class="secnum" id="sec-34-8">34.8</span>Foundry sign-off

When the designer's checks pass, the foundry, or the run's automated checks, takes over. Its checks look less at devices and more at the file and the masks that will be made from it.

**Layer derivation and merging.** Designers draw the layers that are easiest to think in; the masks are derived from them by Boolean operations. In a two-etch SOI process, for example, the designer draws the waveguide core and the regions where the slab is kept, and the foundry derives the full-etch mask (everything outside both) and the shallow-etch mask (slab outside the core) ([Figure 34.7](#fig-34-7)). Before deriving, every layer is merged: overlapping waveguides, devices and routing become single shapes, so overlaps are harmless as long as they are intended. Derived layers can break rules that the drawn layers obey. A slab taper that starts at exactly the width of the core leaves knife edges in the shallow-etch mask, here 450 nm long and narrower than 150 nm; a slab drawn 5 nm from a waveguide leaves a 5 nm line in the full-etch mask. Checking the drawn layers alone would miss both, so decks check derived layers too. Some processes draw only a trench around each waveguide and keep the rest of the silicon, which changes both the masks and the density.

<figure id="fig-34-7">
  <img src="{{ '/assets/figs/ch34_derive.svg' | relative_url }}" style="width:680px" alt="Four panels of a 40 by 14 micrometre window. (a) Drawn layers: two horizontal 500 nm cores, a strip waveguide at the top and a rib waveguide below; around the rib, a light slab region entered through a taper that starts at the core width; next to the strip guide, a small slab rectangle drawn by hand. (b) Derived masks: the full-etch region, dark grey, covering everything outside the cores and slab; the shallow-etch region, mid grey, the slab minus the core. Labels: full etch equals window minus core plus slab; shallow equals slab minus core. (c) Trench style: dark 2 micrometre trenches on both sides of each core, with the rest of the window light silicon; label: etch equals core sized by 2 micrometres minus core; the rest stays silicon. (d) Two close-ups: left, where the slab taper starts at the core width, two red knife-edge slivers 450 nm long along the core; right, with the vertical scale stretched about 11 times, a red 5 nm line between the strip core and the hand-drawn slab.">
  <figcaption><span class="capnum">Figure 34.7.</span> <strong>From drawn layers to masks.</strong> (a) Drawn: two waveguide cores and the slab kept around one of them. (b) Derived by Booleans: the full etch is the window minus core and slab; the shallow etch is the slab minus the core. (c) A trench-style process etches only 2 µm around each core: in this window 57 % of the area is etched instead of 76 %. (d) Two slivers on derived layers, found by sizing in KLayout (red): knife edges where the slab taper begins at exactly the core width (shallow etch), and a 5 nm line where a slab was drawn 5 nm from a core (full etch). All Booleans and checks from KLayout's Region API (<code>figsrc/ch34_density.py</code>). Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

**Density and fill.** Dry etching and polishing both depend on how much of the surrounding area is patterned. Measured over a wafer made with 193 nm lithography, the width of silicon waveguides correlated most with the pattern density within a radius of 200 µm, with a correlation coefficient of 0.57 {% include cite.html keys="xing2020density" %}. Foundries therefore set minimum and maximum densities in windows of a given size, and designers or the foundry add **dummy fill**: small shapes in empty areas, kept far enough from waveguides not to touch the light {% include cite.html keys="kahng1999fill" %}. KLayout computes such densities with `with_density`, which tiles the layout with windows {% include cite.html keys="klayoutdrc" %}.

<figure id="fig-34-8">
  <img src="{{ '/assets/figs/ch34_density.svg' | relative_url }}" style="width:720px" alt="(a) A 1 by 1 millimetre die: six grating couplers on a 127 micrometre pitch on the left with shaded keep-out zones, a loopback, a square spiral about 250 micrometres across, a bus with three rings, two MZIs near the right edge, and a small square sub-wavelength block; silicon density 1.2 percent. (b) Close-up of the lower-left corner after fill: a regular array of small grey squares everywhere except within 3 micrometres of the waveguides and within 10 micrometres of the couplers; scale bar 50 micrometres. (c) Map of silicon density in 100 micrometre windows before fill, 0 to 18 percent, dark everywhere except the spiral and the sub-wavelength block; 361 of 361 windows below 20 percent. (d) The same after fill: about 23 to 25 percent almost everywhere, a red contour at 20 percent enclosing the spiral, where the density stays near 10 percent; 35 of 361 windows below 20 percent.">
  <figcaption><span class="capnum">Figure 34.8.</span> <strong>Density and fill on a 1 mm die.</strong> (a) A passive test die (couplers, loopback, spiral, rings, MZIs, a sub-wavelength block): 1.2 % silicon. Shaded: 10 µm keep-out around the couplers. (b) Dummy fill, 2 µm squares on a 4 µm pitch, kept 3 µm from all silicon. (c) Density in 100 µm windows stepped by 50 µm, before fill: every window is below the illustrative 20 % minimum. (d) After fill: 35 windows still fail (red contour), all over the spiral, whose 5 µm pitch leaves no room for fill. Densities from KLayout's Region API (<code>figsrc/ch34_density.py</code>); the KLayout application running <code>figsrc/ch34_density.lydrc</code> finds the same 361 and 35 failing windows. Drawn by <code>figsrc/ch34_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 34.3 · Filling a 1 mm die</div>

The die of [Figure 34.8](#fig-34-8) holds 11 667 µm² of silicon in 1 mm²: a density of 1.17 %. A waveguide 0.5 µm wide covers 0.5 µm² per micrometre of length, so a whole centimetre of it covers only 5000 µm², 0.5 % of a square millimetre: passive photonic layouts are almost empty. Checked in 100 µm windows stepped by 50 µm (19 × 19 = 361 windows) against an illustrative rule of 20–80 %, every window fails; the densest, over the sub-wavelength block (60 × 60 µm at 50 %), reaches $$1800/10\,000 = 18$$ %.

Fill of 2 µm squares on a 4 µm pitch covers 25 % of any open area. Kept 3 µm from all silicon and 10 µm from the couplers, 55 098 squares fit, adding 220 392 µm²; the die's density rises to 23.2 % and 326 windows now pass. The 35 that still fail all lie over the spiral, whose 0.5 µm guides on a 5 µm pitch cover 10 % and leave 4.5 µm gaps, less than the 0.5 + 3 + 2 + 3 = 8.5 µm pitch needed to fit one square between keep-outs. The remedies are a wider spiral pitch, a smaller keep-out where the foundry allows it, or a density waiver for that region.

Is 3 µm enough? Outside the strip, the guided field decays as $$e^{-\gamma x}$$ with $$\gamma$$ = 8.0 µm⁻¹ (Worked Example 34.2), so at 3 µm it has fallen to $$e^{-24} = 3.7\times10^{-11}$$ of its value at the core's edge: the fill is optically invisible to straight waveguides. Bends, whose field shifts outwards, and couplers, which are meant to be sensitive, deserve larger keep-outs. For comparison, the same die drawn trench-style keeps 92.8 % of its silicon, and its density problem is the opposite one.

</div>

One subtlety of KLayout's tiling: with a window larger than its step, each window is centred on a step-sized cell, so `tile_origin` names the first cell, half a step inside the first window. Given (0, 0), every window moved by 25 µm and the count of failing windows doubled, through windows hanging over the die's edge; comparing the markers' positions with the intended windows showed it.

**The manufacturing grid.** A mask writer places shapes on its address grid. If the database unit is finer than the grid, vertices can fall between grid points (Worked Example 34.2), and the foundry either rejects them or snaps them, with the effects of Section 34.5 applied without the designer's control. Check the grid with the deck, and draw on it.

**Die size and exclusion zones.** An MPW run sells fixed areas. openEBL's checks, for example, accept exactly one top cell and silicon within 605 × 410 µm ([Lab 8]({% link labs/lab08_submit.md %})) {% include cite.html keys="openebl" %}. Dies are separated by dicing streets, so a band at the die edge must stay empty, except where the PDK allows edge couplers to reach a facet; reticle boundaries, alignment marks and the foundry's own test structures take further space.

**What the foundry checks on the file.** Typical submission checks: one top cell; only layers of the layer map; no empty or zero-size cells, unresolved references or polygons that cross themselves; vertices on the grid; the design inside its area; the PDK's black-box cells present and unmodified, since the foundry replaces them with the real geometry; and cell names that cannot collide with other designs when the run's files are merged. The last matters more than it sounds: KLayout, for one, merges two cells of the same name from different files into one cell by default {% include cite.html keys="klayoutapi" %}, so a cell called `ring` in two designs becomes one cell holding both rings. Prefix cell names with your own. Then the foundry runs its full rule deck, which is the one that counts.

**The tape-out package.** What leaves the designer's hands is more than a layout:

- the layout file, GDSII or OASIS ([Chapter 33]({% link chapters/33_layout.md %})). OASIS stores repeated shapes compactly {% include cite.html keys="semip39,reich2003" %}: the filled die of Worked Example 34.3, written flat with its 55 399 shapes, is 3.56 MB as GDSII and 4.1 kB as OASIS (a GDSII array reference for the fill would also shrink it);
- the layer map, if the file's layers are not those of the PDK;
- the DRC report of the final file, with the waivers and their reasons;
- design notes: the top cell's name, the list of devices and their labels, what each is for, and anything unusual (non-PDK cells, deliberate rule violations);
- a test plan: which devices to measure, with which polarisation and wavelength range, and which pads to probe;
- a record of the exact version: the commit of the scripts that made the file and a checksum of the file, so that the layout can be regenerated and the data matched to it later ([Chapter 29]({% link chapters/29_design.md %})).

## <span class="secnum">34.9</span>A pre-fabrication checklist

[Table 34.4](#tab-34-4) collects the checks of this chapter in the order in which they are usually run. Most take minutes, and each one run before submission is a fault that cannot cost a fabrication run.

**Table 34.4. Before you submit to an MPW run.**
{: .tabcaption #tab-34-4 }

| # | Check | How | Pass when |
|---|---|---|---|
| 1 | Correct PDK and rule deck version | compare with the run's instructions | versions match the run |
| 2 | One top cell, named as the run asks; unique cell names | layout viewer; file check script | one top cell; your prefix on every cell |
| 3 | Only allowed layers | list the layers in the file | every layer is in the layer map |
| 4 | Design inside its area, floorplan shape present | DRC placement rule; bounding box | nothing outside; size within the limit |
| 5 | Full rule deck, drawn and derived layers | DRC in batch mode, from the final file | zero markers, or each one waived in writing |
| 6 | Grid and polygon validity | `ongrid`, `odd_polygons` (or the PDK's equivalents) | no off-grid vertices, no self-intersections |
| 7 | Density | density rule, fill if needed | every window within limits; fill kept from waveguides |
| 8 | Connectivity | SiEPIC-Tools `layout_check` or equivalent | no disconnected or mismatched pins, no overlaps |
| 9 | Netlist matches the circuit | compare extracted netlist and parameters with the schematic | same nets; lengths, gaps and radii as simulated |
| 10 | Layout-extracted simulation | simulate the extracted netlist | response as designed (FSR, extinction, loss) |
| 11 | Electrical LVS (if any heaters, modulators, detectors) | LVS against the electrical netlist | no shorts or opens; pads as in the probe plan |
| 12 | Design for test | label format and position; coupler pitch, column, orientation, spacing | every device labelled, unique, measurable |
| 13 | Test structures | loopbacks, cut-backs, reference devices present | each group has its calibration structures |
| 14 | Break it on purpose | introduce one mistake per check (Lab 8) | every check you rely on fires |
| 15 | Package | file, layer map, report and waivers, notes, test plan, commit and checksum | the run's own checks pass on the submitted file |

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Try it</div>

[Lab 8]({% link labs/lab08_submit.md %}) runs the openEBL checks and SiEPIC-Tools' verification on the chip of Lab 7 and breaks it four ways. To try the deck of this chapter, copy its listing into a file `deck.lydrc` or `deck.drc` and run it with `klayout -b -r` on any layout with silicon on layer 1/0; then add a rule of your own, for example a minimum bend radius or a separation between silicon and heater metal, and draw a test shape that breaks it.

</div>

## Reading

{% include reflist.html keys="klayoutdrc,klayoutlvs,ebeampdk,siepictools,openebl,cao2014drc,cao2015lvs,pond2014flow,bogaerts2018,lauther1981,kahng1999fill,xing2020density,orcutt2010,klayoutapi,semip39,reich2003" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Verification is several checks, each for one kind of fault: DRC for shapes, connectivity and LVS for circuits, design-for-test rules for measurability, sign-off for the file and the masks. None of them sees everything.
- A DRC engine merges shapes, applies Booleans and sizing, and reports edge pairs closer than a rule; the metric and the angle limit decide what counts.
- A KLayout deck is a short script: `input`, a check such as `width`, `space`, `notch`, `enclosing`, `overlap`, `ongrid` or `with_density`, and `output` to a report; run it with `klayout -b -r deck.lydrc -rd input=…`.
- Count mistakes, not markers: in this chapter's test, 9 real mistakes made 295 of 373 markers, an intended grating 18, and a snapped coupler at exactly the minimum gap 60 false ones.
- Curves on a grid produce false errors at the minimum; handle them with tolerances, angle limits, drawing on the grid, and written waivers, never by blanket suppression.
- Connectivity faults are invisible to DRC: a component moved 50 nm or a waveguide of the wrong width passes every width and space rule. Check pins, widths, overlaps, and the extracted netlist's parameters against the schematic.
- Before an MPW run, follow a checklist: rule deck, derived layers, grid, density and fill, connectivity, LVS, labels and couplers, unique cell names, and a package with the report, waivers and the exact version of the design.

</div>
