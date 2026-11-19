---
title: "33. Layout with KLayout and GDSII"
parent: "Part VII · Design, Simulation and Layout"
nav_order: 33
permalink: /part-7/ch33/
chapter: 33
---

# <span class="chapnum">Chapter 33</span>Layout with KLayout and GDSII

A layout is a set of polygons on numbered layers, written to a file from which the foundry makes its masks. This chapter opens that file record by record, draws into it with KLayout and with code, and shows what a grid of nanometres does to a curved waveguide.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- explain how the layers and datatypes of a layout become masks and process steps;
- read a GDSII file as a stream of records, and reason about its units, integer coordinates, limits and hierarchy;
- view, edit and script layouts in KLayout, and use SiEPIC-Tools for waveguides, pins and netlists;
- build, route and netlist a layout as code with gdsfactory, and simulate the netlist;
- draw curved waveguides on a grid knowing the errors, and floorplan, route and label a chip.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How does a drawing become masks, and what do the file format and its grid do to a curved waveguide?

</div>

## <span class="secnum">33.1</span>What a layout is for

A foundry patterns a wafer in a sequence of steps: expose a resist through a mask (or write it with an electron beam), etch or deposit, strip, repeat ([Chapter 35]({% link chapters/35_fab.md %})). Each patterning step needs one picture: where the resist should be exposed. The **layout** is the collection of those pictures, one per **layer**, drawn as polygons. A layer is named by two small integers, the **layer number** and the **datatype**, written as 1/0, 11/0, 1/10. The process design kit ([Chapter 30]({% link chapters/30_flow.md %})) says what each pair means.

[Figure 33.1](#fig-33-1) shows a ring with a heater drawn on the layer numbers of the SiEPIC EBeam PDK {% include cite.html keys="ebeampdk" %}. Only four of its layers are fabricated. **Si 1/0** is the silicon that stays: everything not covered by a 1/0 polygon is etched down to the buried oxide, so a waveguide is drawn as its core, 500 nm wide. **M1_heater 11/0**, **M2_router 12/0** and **M_Open 13/0** are the heater metal, the routing metal, and the window opened in the top oxide over each pad (the openEBL passive runs of Labs 7 and 8 fabricate only 1/0). The other layers are never fabricated. They carry information for the design tools: test labels (Text 10/0), the outline of each device (DevRec 68/0), its ports (PinRec 1/10), paths that are to become waveguides (Waveguide 1/99) and the design area (FloorPlan 99/0).

<figure id="fig-33-1">
  <img src="{{ '/assets/figs/ch33_layers.svg' | relative_url }}" style="width:720px" alt="Left: top view to scale of a 10 micrometre ring with a 500 nm bus below it, a 3 micrometre wide heater arc over the ring open at the bottom, M1 stubs and tabs at both ends, 6 micrometre M2 leads up to two 50 micrometre pads 100 micrometres apart, each pad under a hatched oxide window; a dashed teal device-recognition box around ring and bus, red pins at the bus ends labelled opt1 and opt2, the test label opt_in_TE_1550_device_demo_ringheater at the left end, and a dashed floor-plan box around everything; scale bar 20 micrometres. Right: a table of nine layers with swatches, layer and datatype numbers and what each is for; the first four (Si 1/0, M1_heater 11/0, M2_router 12/0, M_Open 13/0) are fabricated, the other five (Text 10/0, DevRec 68/0, PinRec 1/10, Waveguide 1/99, FloorPlan 99/0) are for the design tools only.">
  <figcaption><span class="capnum">Figure 33.1.</span> <strong>A cell and its layers.</strong> (a) A ring (radius 10 µm, 500 nm wide, 200 nm gap) with a heater, drawn by <code>figsrc/ch33_klayout.py</code> on the layer numbers of the SiEPIC EBeam PDK {% include cite.html keys="ebeampdk" %} and read back from the GDS file. The metal widths respect the minimums of the PDK's rule deck (3 µm for M1, 5 µm for M2, 3 µm of M2 over M1, 10 µm for openings); the pad size (50 µm) and pitch (100 µm) are illustrative. (b) What each layer is for. A drawn 1/0 polygon is silicon that stays; the layers below the dashed line are never fabricated but tell the design tools where labels, devices, ports and the design area are. Drawn by <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

Three kinds of layer appear in every PDK. **Drawn layers** are the ones designers draw. **Derived layers** are computed from them by Boolean operations, so that a mask need not be drawn directly: a partial-etch mask, for instance, may be the drawn rib region minus the drawn core, and a foundry can add sizing, fill or proximity correction on the way to the mask (Chapter 34 covers this layer derivation and its checks). **Annotation layers** carry labels, outlines and pins. The datatype is often used to separate purposes on one layer number: in the EBeam PDK, 1/0 is silicon and 1/10 marks the silicon's ports.

## <span class="secnum">33.2</span>GDSII as data

Most photonic layouts travel as **GDSII**, the binary stream format of Calma's GDSII layout systems, which outlived them to become the industry's common language. Its reference is Calma's *GDSII Stream Format Manual*, Release 6.0 (1987): short, and worth reading {% include cite.html keys="calma1987" %}. A GDSII file is a **stream of records**. Each record begins with a 4-byte header: two bytes giving the record's total length in bytes (header included), one byte naming the record type and one byte naming the type of data that follows. The data types are few: none, a 16-bit bit array, 2-byte and 4-byte signed integers, 8-byte reals and ASCII strings (a 4-byte real is defined but unused). Integers are big-endian two's complement, records always have an even length, and a string of odd length is padded with a null byte.

The records nest like brackets. A file is a **library**: HEADER (the stream version), BGNLIB (two time stamps), LIBNAME, UNITS, then any number of **structures** (cells), then ENDLIB. Each structure runs from BGNSTR (two more time stamps) and STRNAME to ENDSTR and holds **elements**, each ended by ENDEL:

- **BOUNDARY**, a polygon: a LAYER, a DATATYPE and an XY record listing its vertices, the last equal to the first;
- **PATH**, a centre line with a WIDTH and a PATHTYPE (flush, round or extended ends);
- **SREF**, one placement of another structure, named by SNAME, with an optional STRANS (reflection about the x axis, applied before rotation), MAG and ANGLE (degrees, counter-clockwise);
- **AREF**, a regular array of placements: COLROW gives the numbers of columns and rows, and its XY holds three points, the origin and the origin displaced by all the columns and by all the rows;
- **TEXT**, a string at a point, on a layer and a text type.

To see all of this concretely, `figsrc/ch33_gdsii.py` writes a tiny library byte by byte with nothing but Python's `struct` module: a cell `WG` containing one 10 × 0.5 µm waveguide, and a cell `TOP` with an array of four `WG` 127 µm apart, one `WG` turned by 90°, a path and a label. The file is 424 bytes in 40 records ([Figure 33.2](#fig-33-2)); KLayout reads it back and finds exactly that.

<figure id="fig-33-2">
  <img src="{{ '/assets/figs/ch33_records.svg' | relative_url }}" style="width:760px" alt="Top: one 44-byte record drawn as a row of boxes: 00 2C (length), 10 (record type XY), 03 (data type four-byte integer), then ten four-byte integers holding five x, y pairs in nanometres: (0, minus 250), (10000, minus 250), (10000, 250), (0, 250), (0, minus 250). Bottom: the whole file in two columns, one row per record, with its byte offset, first eight bytes in hexadecimal, record name and decoded value: HEADER 600, BGNLIB, LIBNAME CH33.DB, UNITS 0.001 micrometre and 1e-9 metre per database unit, the structure WG with one BOUNDARY on layer 1 datatype 0, and the structure TOP with an AREF of WG of 1 column by 4 rows, an SREF of WG at 90 degrees, a PATH 500 wide on layer 1 and a TEXT opt_in_TE_1550_demo on layer 10, then ENDSTR and ENDLIB at offset 420. Rows are shaded by kind: library, structure, element and records inside an element.">
  <figcaption><span class="capnum">Figure 33.2.</span> <strong>A GDSII file, record by record.</strong> (a) The XY record of the waveguide's BOUNDARY taken apart: a 2-byte length (44 bytes), the record type (0x10, XY), the data type (3, 4-byte signed integers) and five vertices in database units of 1 nm; the fifth repeats the first. (b) The whole 424-byte file, written by <code>figsrc/ch33_gdsii.py</code> following the Release 6.0 manual {% include cite.html keys="calma1987" %} and read back by KLayout 0.30.13 as a check. Drawn by <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

**Units.** Every coordinate is an integer number of **database units** (dbu). The UNITS record holds two reals: the size of a database unit in user units, and in metres. Photonic PDKs commonly use a 1 nm database unit and micrometres as user units, so UNITS holds 0.001 and 10<sup>−9</sup>; the EBeam technology file sets the same 0.001 µm {% include cite.html keys="ebeampdk" %}. The reals are not IEEE numbers but base-16 floating point: a sign bit, a 7-bit exponent of 16 in excess-64 form and a 56-bit fraction {% include cite.html keys="calma1987" %}. The manual's own bytes for 0.001 end in A7EF, while KLayout, gdstk and `ch33_gdsii.py` all write A7F0: the same number to about 16 significant figures, rounded differently in the last bit. Two correct GDS files of the same layout need not be identical byte for byte (Section 33.7).

**Integer coordinates.** Coordinates are 4-byte signed integers, so they run from −2 147 483 648 to +2 147 483 647 database units. The largest coordinate in metres is

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Coordinate range of GDSII</div>

$$x_\mathrm{max} = (2^{31} - 1)\,\delta,$$

where $$\delta$$ is the database unit: ±2.15 m at 1 nm, ±0.215 m at 0.1 nm, ±2.15 mm at 1 pm.

</div>

With 1 nm units, $$x_\mathrm{max}$$ is seven times the diameter of a 300 mm wafer (3 × 10<sup>8</sup> dbu), and the resolution, 1 nm, is far below what lithography prints. That is why 1 nm is the usual choice. A finer unit buys nothing printable and shrinks the range: at 1 pm, nothing larger than 4.3 mm across can be described. Every vertex lies on the database grid by construction, a fact that matters for curves (Section 33.5).

**Limits.** [Table 33.1](#tab-33-1) lists the limits of Release 6.0 beside what a modern tool accepts. Real files exceed the old ones routinely, and most tools have followed; a strict reader at a foundry may not have.

**Table 33.1. Limits of GDSII, as specified and in practice.** Release 6.0 values from the manual {% include cite.html keys="calma1987" %}; KLayout values from its documentation {% include cite.html keys="klayoutapi" %} and from tests in `figsrc/ch33_klayout.py` with KLayout 0.30.13.
{: .tabcaption #tab-33-1 }

| Quantity | Release 6.0 | KLayout 0.30 (default) |
|---|---|---|
| Coordinate | 4-byte signed integer (±2<sup>31</sup> dbu) | the same |
| Vertices per BOUNDARY or PATH | 200 coordinate pairs | polygons split above 8000 points; or unlimited with several XY records (a non-standard option) |
| Record length | 2-byte count (32 767 bytes if read as signed) | lengths up to 65 535 bytes read as unsigned, with a warning |
| Layer, datatype, text type | 0–63 | layer numbers up to 65 535 written and read back; 70 000 refused |
| Structure name | 32 characters: A–Z, a–z, 0–9, `_`, `?`, `$` | names shortened only beyond 32 000 characters |
| Array (AREF) size | at most 32 767 columns and 32 767 rows | the same (a 2-byte COLROW record) |
| Holes in polygons | none: a BOUNDARY is one closed outline | holes joined to the outline by cut lines when writing |
{: .lab-table }

Two of these limits shape layouts. A BOUNDARY has **no holes**: a ring is stored as one outline that runs round the outer edge, crosses to the inner edge along a **cut line**, runs round the inner edge the other way and crosses back ([Figure 33.4](#fig-33-4)). And polygons have a **vertex limit**. A Bragg grating of 1500 periods drawn as one polygon has 12 000 vertices; KLayout writes it as two polygons of 6000 points by default, as 64 polygons of at most 188 points with the limit set to 200, or as one polygon spread over several XY records if asked. The merged area is identical every time, but the default file contains XY records of 48 012 bytes, which a reader that treats the length as signed cannot read. Its largest records stay under 32 767 bytes if the limit is set to about 4000 points.

**Hierarchy.** A layout is a tree of cells. A cell is drawn once and placed many times by reference, each SREF costing a few tens of bytes and each AREF a single element however many copies it places. A file is then a description of the tree, not of the flattened picture; tools flatten only when they must (fracturing for the mask writer, some checks). [Worked Example 33.1](#we-33-1) puts numbers on this.

<div class="tbox tbox-example" markdown="1" id="we-33-1">
<div class="tbox-title">Worked Example 33.1 · Ten thousand rings, three ways</div>

A 10 µm ring with its bus is drawn with 228 vertices per circle (a 1 nm sagitta, Worked Example 33.2) and placed 10 000 times on a 100 × 100 grid with 40 × 30 µm spacing. In GDS the ring is one polygon of 459 points plus a 4-point bus: its cell alone is a 3 874-byte file.

- **One AREF.** The whole file is 3 966 bytes: the array adds 92 bytes (an AREF of 52 bytes and the top cell's own 40).
- **10 000 SREFs.** 283 914 bytes: each placement costs exactly 28 bytes (SREF 4, SNAME "ring" 8, XY 12, ENDEL 4).
- **Flat.** 37 680 106 bytes, 37.7 MB: 3 768 bytes per ring, nearly all of it the ring's 460 XY points at 8 bytes each.

The flat file is 9 500 times larger than the array, for the same geometry: an XOR of the two, flattened, is empty ([Figure 33.3](#fig-33-3)). Now let the 10 000 rings all differ, say in gap. Each needs its own cell, and the hierarchy saves nothing; that is the price of sweeping every parameter on a chip.

</div>

<figure id="fig-33-3">
  <img src="{{ '/assets/figs/ch33_hierarchy.svg' | relative_url }}" style="width:700px" alt="Left: two cell trees. Hierarchical: TOP points by one arrow, labelled 1 array instance 100 by 100 at 40 by 30 micrometres, to a single cell ring holding one 459-point ring and one 4-point bus. Flat: TOP with lines fanning out to many small copies of a ring, labelled 20 000 polygons in the top cell. Right: horizontal bars on a logarithmic axis from 1 kB to 300 MB for three layouts and three formats: one AREF, GDSII 4.0 kB, OASIS 2.2 kB, compacted OASIS 1.7 kB; 10 000 SREFs, GDSII 284 kB, OASIS 68 kB, compacted 1.8 kB; flat, GDSII 37.7 MB, OASIS 280 kB, compacted 1.7 kB.">
  <figcaption><span class="capnum">Figure 33.3.</span> <strong>Hierarchy and file size.</strong> (a) The same 10 000 rings stored as one cell placed by one array instance, or flattened into 20 000 polygons in the top cell; the XOR of the two layouts is empty. (b) File sizes written by KLayout 0.30.13 (<code>figsrc/ch33_klayout.py</code>): GDSII without time stamps; OASIS plain (compression level 0, no CBLOCKs); and OASIS compacted (level 2, which finds repeated shapes, with each cell compressed). Drawn by <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

**Cell names.** GDSII references cells by name, and a library cannot hold two cells with the same name. When two designs are merged, as openEBL merges every submission into one layout ([Lab 8]({% link labs/lab08_submit.md %})), two cells called `ring` collide. The result depends on the tool's policy, and the default can be silent. In a test, two files, each with its own cell `ring` (radii 10 µm and 5 µm), were read into one KLayout layout: with the default policy, which adds the second cell's shapes to the first, the merged `ring` held both rings and both designs now showed two rings; with the rename policy the second became `ring$1` and both were correct {% include cite.html keys="klayoutapi" %}. Give every cell a name that is unique to its design and its parameters, for instance with your name as a prefix; gdsfactory does this automatically (Section 33.4).

**OASIS.** GDSII's records were designed for tapes, not for compactness. **OASIS**, the Open Artwork System Interchange Standard, standardised by SEMI as P39, was designed to replace it for mask data {% include cite.html keys="semip39" %}. It stores integers in as many bytes as they need, points as differences from the previous point, rectangles as special shapes, and repeated shapes and placements as repetitions, and it can compress each cell {% include cite.html keys="reich2003,klayoutapi" %}. In Worked Example 33.1, even plain OASIS shrinks the flat layout from 37.7 MB to 280 kB, and the compacted file is 1.7 kB whatever the hierarchy, because the writer recognises the regular arrays itself. KLayout reads and writes both formats; openEBL accepts either ([Lab 7]({% link labs/lab07_layout.md %})), and a foundry's submission rules say which it wants.

## <span class="secnum">33.3</span>KLayout

**KLayout** is an open-source viewer and editor for GDSII, OASIS and several other layout formats, built to handle large layouts quickly, with a scripting interface to nearly all of its functions {% include cite.html keys="klayout" %}. Five of its features matter most for photonics.

- **Layer properties.** A layout file stores only numbers. A **layer properties file** (`.lyp`, XML) maps each layer/datatype pair to a name, colour, fill pattern and visibility; a **technology file** (`.lyt`) bundles the properties file with the database unit and reader options. The EBeam PDK ships both: its `.lyt` sets a 0.001 µm database unit and allows big records and multi-XY records when reading {% include cite.html keys="ebeampdk" %}.
- **Cells and hierarchy.** The cell tree lists every cell and what it contains. The view shows a chosen number of hierarchy levels, so the inside of a PDK cell can be hidden or shown; a cell can be opened as if it were the top.
- **PCells.** A **parameterised cell** is a cell computed by code from its parameters, held in a library: a waveguide from a path and a width, a ring from a radius and a gap. A GDS file stores only the geometry, which every tool can read; KLayout adds a structure called `$$$CONTEXT_INFO$$$`, whose property records name the library, the PCell and its parameter values, so that KLayout can regenerate the cell later (we checked this with the DONUT PCell of KLayout's Basic library).
- **Rulers.** Rulers snap to vertices and edges and measure distances, pitches and angles: the 127 µm between couplers, the gap of a ring.
- **Scripting.** Macros in Python or Ruby run inside KLayout and drive the editor, the design-rule checker ([Chapter 34]({% link chapters/34_verification.md %})) and the netlister. The same layout database is available outside KLayout as the standalone Python package `klayout` (`pip install klayout`), whose module `klayout.db` holds layouts, cells, shapes and readers and writers; the older combined module `pya` remains for compatibility {% include cite.html keys="klayoutapi" %}.

The script below uses `klayout.db` to draw a ring filter, a ring and a bus waveguide, as a cell; makes three variants with different gaps; places them 127 µm apart; and writes GDS. It ran with KLayout 0.30.13; the file it wrote was read back and measured ([Figure 33.4](#fig-33-4)).

```python
import math
import klayout.db as kdb

ly = kdb.Layout()
ly.dbu = 0.001  # database unit: 1 nm
SI, TEXT = ly.layer(1, 0), ly.layer(10, 0)  # Si and Text layers of the SiEPIC EBeam PDK

def circle(r, n):  # n vertices on a circle (um), one at the top
    return [kdb.DPoint(r * math.sin(2 * math.pi * k / n), r * math.cos(2 * math.pi * k / n))
            for k in range(n)]

def ring_filter(r=10.0, w=0.5, gap=0.2, length=30.0, n=256):
    cell = ly.create_cell(f"ring_r{r:g}_g{round(gap * 1000)}")  # named by its parameters
    ring = kdb.DPolygon(circle(r + w / 2, n))
    ring.insert_hole(circle(r - w / 2, n))
    cell.shapes(SI).insert(ring)
    yb = r + w + gap  # centre line of the bus, above the ring
    cell.shapes(SI).insert(kdb.DBox(-length / 2, yb - w / 2, length / 2, yb + w / 2))
    return cell

top = ly.create_cell("TOP")
for i, gap in enumerate((0.15, 0.20, 0.25)):  # three variants, 127 um apart
    top.insert(kdb.DCellInstArray(ring_filter(gap=gap), kdb.DTrans(0, i * 127.0)))
    label = kdb.DText(f"gap {gap * 1000:.0f} nm", kdb.DTrans(-15.0, i * 127.0 - 15.0))
    top.shapes(TEXT).insert(label)
ly.write("ring_filters.gds")
```

The `D` classes (`DPoint`, `DBox`, `DPolygon`, `DTrans`) take micrometres and are converted to integer database units when inserted; the plain classes (`Point`, `Box`, `Polygon`) take database units directly. Read back, the file has four cells, the three ring cells placed at y = 0, 127 and 254 µm, and the gaps measured by KLayout's separation check are exactly 150, 200 and 250 nm. Each ring, inserted as a polygon with a hole, comes back as one polygon of 515 points with no hole.

<figure id="fig-33-4">
  <img src="{{ '/assets/figs/ch33_klayout.svg' | relative_url }}" style="width:720px" alt="Left: the three ring cells drawn to scale in a column, 127 micrometres apart, labelled gap 150, 200 and 250 nm and with their cell names ring_r10_g150, ring_r10_g200 and ring_r10_g250. Middle: one ring with its bus, outline drawn in blue, with a short red segment near the top marking the cut line that joins the inner edge to the outer; a note says one polygon of 515 points, two edges of 256 joined by a cut, no holes; scale bar 5 micrometres; a red box marks the gap. Right: zoom on the gap, x from minus 650 to 650 nm: the bus edge at 450 nm above the 10 micrometre line, the polygon edge of the ring with vertices about 250 nm apart lying just under the dashed ideal circle, and a red arrow marking the measured gap of 200 nm.">
  <figcaption><span class="capnum">Figure 33.4.</span> <strong>What the KLayout script drew,</strong> read back from its GDS file. (a) The three cells as placed, to scale. (b) One ring: a single polygon whose inner edge is joined to the outer by a cut line (red), because GDSII has no holes. (c) The coupling gap: vertices 251 nm apart on the 1 nm grid, one at the top, so the gap is exactly the drawn 200 nm; between vertices the polygon lies inside the circle by up to 0.77 nm. Drawn by <code>figsrc/ch33_figs.py</code> from <code>figsrc/ch33_klayout.py</code>.</figcaption>
</figure>

**SiEPIC-Tools** adds what KLayout lacks for photonics {% include cite.html keys="siepictools" %}. Its **Waveguide PCell** turns a path into a waveguide: the path's corners become bends of the radius set by the waveguide type (5 µm, Bézier-shaped, for the PDK's 500 nm strip), and the cross-section adds the DevRec outline. Drawn interactively, a path on the Waveguide layer 1/99 is converted by the *path to waveguide* command, which also snaps the path's ends to nearby pins. **Pins** are short paths on PinRec 1/10 across each port, pointing out of the device, with a text naming the port; **DevRec** 68/0 outlines each device. From them SiEPIC-Tools finds which device connects to which, checks the connections and labels, and exports a **netlist** for circuit simulation. The same steps run from Python, without the KLayout window:

```python
import pya  # KLayout's Python module, as SiEPIC-Tools uses it
import siepic_ebeam_pdk  # registers the EBeam technology and libraries
from SiEPIC.utils.layout import new_layout
from SiEPIC.verification import layout_check

top, ly = new_layout("EBeam", "TOP", GUI=False, overwrite=True)
gc = ly.create_cell("ebeam_gc_te1550", "EBeam")  # the PDK's grating coupler (a fixed cell)
for y in (0.0, 127.0):
    top.insert(pya.DCellInstArray(gc, pya.DTrans(0.0, y)))
pts = [pya.DPoint(0, 0), pya.DPoint(20, 0), pya.DPoint(20, 127), pya.DPoint(0, 127)]
path = pya.DPath(pts, 0.5)
wg = ly.create_cell("Waveguide", "EBeam",
                    {"path": path, "waveguide_type": "Strip TE 1550 nm, w=500 nm"})
top.insert(pya.DCellInstArray(wg, pya.DTrans()))
label = "opt_in_TE_1550_device_demo_loopback"
top.shapes(ly.layer(10, 0)).insert(pya.DText(label, pya.DTrans(0.0, 127.0)))
errors = layout_check(cell=top, verbose=False)  # pins, connections and labels
netlist = top.spice_netlist_export(opt_in_selection_text=[label])[0]
```

With SiEPIC 0.5.31 and the EBeam PDK 0.4.53 this loopback passes the check with 0 errors. The netlist has three components, two `ebeam_gc_te1550` couplers and one `ebeam_wg_integral_1550` waveguide joining them through nets `N$0` and `N$1`, and records the waveguide's length, 163.897 µm: the 167 µm path less what its two 5 µm bends cut from the corners. [Lab 7]({% link labs/lab07_layout.md %}) draws a whole chip with the same PDK cells from gdsfactory instead, adding SiEPIC-style pins to every routed piece, and [Lab 8]({% link labs/lab08_submit.md %}) runs SiEPIC-Tools' verification on it as openEBL does.

## <span class="secnum">33.4</span>Layout as code with gdsfactory

[Chapter 30]({% link chapters/30_flow.md %}) introduced **gdsfactory** {% include cite.html keys="gdsfactory" %}; here are the pieces that make it a layout tool.

- **Components.** A component is a cell made by a Python function. Decorated with `@gf.cell`, the function is cached: called twice with the same parameters it returns the same cell, and the cell's name is built from the function's name and its parameters (`mzi_with_couplers_DL100_…`), so two variants never collide and an identical variant is never stored twice. A cached cell is locked: changing it afterwards raises an error, so all of its geometry must come from its parameters.
- **Ports.** Every component carries named **ports**: a centre, a width, an **orientation** in degrees (0 points east, out of the component), a layer and a type (optical, electrical, or vertical for a fibre). Optical ports are named `o1`, `o2`, … `ref.connect("o1", other.ports["o2"])` moves and turns a reference until its port faces the other, centre on centre.
- **Cross-sections.** A cross-section describes a waveguide across its width: the core's width and layer, any extra sections (a slab, a cladding opening, an exclusion zone) and the default bend radius. Straights, bends and routes are all drawn from one, so changing the waveguide means changing one object.
- **Routing.** `route_single` joins two ports with a Manhattan route, straights and bends of the cross-section's radius (Euler bends by default); `route_bundle` routes many ports at once at a set separation; waypoints and steps steer a route, and there are electrical and all-angle routers.
- **Netlists.** `get_netlist()` reads the circuit back out of the layout: the instances with their settings, their placements, the **nets** (which port touches which) and the component's external ports. A netlist can also be written as YAML and turned into a layout.

The listing builds the test cell of [Figure 33.5](#fig-33-5): an MZI with a 100 µm arm-length difference between two grating couplers on the fibre-array pitch, routed and labelled. It uses gdsfactory's generic PDK; [Lab 7]({% link labs/lab07_layout.md %}) does the same with the SiEPIC EBeam PDK through ubcpdk {% include cite.html keys="ubcpdk" %}.

```python
import gdsfactory as gf

gf.gpdk.PDK.activate()  # generic PDK: waveguide core on layer 1/0
# a 500 nm strip on layer 1/0, with 10 um (Euler) bends
xs = gf.cross_section.cross_section(width=0.5, layer=(1, 0), radius=10)
PITCH = 127.0  # fibre-array pitch (um)


@gf.cell
def mzi_with_couplers(delta_length: float = 100.0,
                      label: str = "opt_in_TE_1550_device_demo_mzi") -> gf.Component:
    c = gf.Component()
    mzi = c << gf.components.mzi(delta_length=delta_length, cross_section=xs)
    gc_out = c << gf.components.grating_coupler_elliptical_te(cross_section=xs)
    gc_in = c << gf.components.grating_coupler_elliptical_te(cross_section=xs)
    for gc, y in ((gc_out, 0.0), (gc_in, PITCH)):
        gc.drotate(180)  # grating west, port o1 facing east
        gc.dmove((0.0, y))
    mzi.dmove((70.0, 100.0))  # its port o1 lands at (60, 100)
    gf.routing.route_single(c, gc_in.ports["o1"], mzi.ports["o1"], cross_section=xs)
    gf.routing.route_single(c, mzi.ports["o2"], gc_out.ports["o1"], cross_section=xs)
    c.add_label(label, position=gc_in.ports["o1"].dcenter, layer=(10, 0))
    c.add_port("in", port=gc_in.ports["o2"])  # the fibre ports, for circuit simulation
    c.add_port("out", port=gc_out.ports["o2"])
    return c
```

The netlist extracted from this cell has eleven instances, the MZI cell, the two couplers and the two routes as four straights and four Euler bends, joined by ten nets. Because it comes from the drawn geometry, it includes the routes, whose lengths the designer never typed in. Give each leaf cell a compact model and **SAX** {% include cite.html keys="sax" %} computes the circuit's response:

```python
import sax
netlist = mzi_with_couplers().get_netlist(recursive=True)  # instances, nets, ports
models = {"straight": straight, "bend_euler": bend_euler, "mmi1x2": mmi1x2,
          "grating_coupler_elliptical": gc}                 # one model per leaf cell
circuit, _ = sax.circuit(netlist=netlist, models=models)
T = abs(circuit(wl=wl)["in", "out"]) ** 2
```

Here `straight` returns $$e^{j2\pi n_\mathrm{eff}(\lambda)L/\lambda}$$ with the strip's $$n_\mathrm{eff}$$ = 2.446 and $$n_g$$ = 4.18 ([Chapter 6]({% link chapters/06_soi.md %})) and 2 dB/cm, `bend_euler` is a straight of the bend's length, the MMI is an ideal splitter, and the couplers are ideal so that only the interferometer shows. The simulated fringes are 5.74 nm apart near 1550 nm, against $$\lambda^2/(n_g\Delta L)$$ = 5.75 nm ([Chapter 11]({% link chapters/11_mzi.md %})).

<figure id="fig-33-5">
  <img src="{{ '/assets/figs/ch33_gdsfactory.svg' | relative_url }}" style="width:720px" alt="Left: the layout of the test cell to scale: two grating couplers on the left, 127 micrometres apart, labelled in (top) and out (bottom), a route from the input coupler to an MZI whose long arm dips down between the couplers, and a route from the MZI output back round to the output coupler; red arrows mark the optical ports o1 and o2 of the couplers and of the MZI, pointing out of each component; the label opt_in_TE_1550_device_demo_mzi sits on the input coupler; a note lists the extracted netlist: 4 bend_euler, 4 straight, 2 grating couplers, 1 mzi, 10 nets. Right: simulated transmission in decibels from 1535 to 1565 nm, fringes between 0 and below minus 30 dB, with the spacing of two minima near 1550 nm marked 5.74 nm and the formula value 5.75 nm.">
  <figcaption><span class="capnum">Figure 33.5.</span> <strong>From code to layout to circuit.</strong> (a) The cell drawn by the listing, read from its GDS file: ports (red) point out of their components, and the label marks the input coupler. (b) Transmission from the <code>in</code> to the <code>out</code> fibre port, computed by SAX from the netlist extracted from the layout, with simple compact models (strip waveguide with \(n_\mathrm{eff}\) 2.446, \(n_g\) 4.18 and 2 dB/cm, ideal splitters and couplers): the minima near 1550 nm are 5.74 nm apart, against 5.75 nm from \(\lambda^2/(n_g\Delta L)\). Drawn by <code>figsrc/ch33_figs.py</code> from <code>figsrc/ch33_gdsfactory.py</code> (gdsfactory 9.51, SAX 0.18).</figcaption>
</figure>

Layout as code pays off when a design is a family: a sweep of gaps is a loop, and every variant is named, placed and routed by the same rules. Interactive layout pays off when a design is one of a kind, or when you need to see it while you draw. The two meet in the file: gdsfactory writes GDS through KLayout's own database, and its cells open in KLayout like any other.

## <span class="secnum">33.5</span>Curves on a grid

Photonic layouts are full of curves, and a GDS file can hold only polygons with vertices on the database grid. A curve is therefore drawn twice approximately: once by **discretising** it into straight segments, and again by **snapping** each vertex to the grid {% include cite.html keys="orcutt2010,bogaerts2018" %}.

**Discretising.** A chord across an arc of angle $$\theta$$ on a circle of radius $$R$$ falls inside the arc by the **sagitta**:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Sagitta and vertex count</div>

$$s = R\left(1 - \cos\frac{\theta}{2}\right) \approx \frac{R\theta^2}{8}, \qquad N = \left\lceil \frac{\pi}{\arccos(1 - s_\mathrm{max}/R)} \right\rceil \approx \pi\sqrt{\frac{R}{2 s_\mathrm{max}}}$$

$$N$$ vertices per full circle keep the sagitta below $$s_\mathrm{max}$$; on average the polygon lies $$2s/3$$ inside the circle.

</div>

The vertex count grows only as the square root of the radius over the error, so even a large ring needs only hundreds of vertices. Some CMOS foundries accept only Manhattan edges on a 1 to 5 nm design grid; a curve must then be sliced into rectangles, and sliced uniformly a 10 µm ring 500 nm wide on a 1 nm grid becomes about 40 000 rectangles per layer. Slicing more coarsely where the edge is nearly straight, and storing a quarter of the ring once and placing it four times, keeps such data manageable {% include cite.html keys="orcutt2010" %}.

<div class="tbox tbox-example" markdown="1" id="we-33-2">
<div class="tbox-title">Worked Example 33.2 · How many vertices does a 10 µm ring need?</div>

The outer edge of a 10 µm ring 500 nm wide has $$R$$ = 10.25 µm. For a sagitta of at most 1 nm, $$N = \lceil \pi/\arccos(1 - 0.001/10.25)\rceil$$ = 225 vertices per circle; rounding up to a multiple of four, 228, puts vertices on the axes and gives $$s$$ = 0.97 nm. Halving the error to 0.5 nm needs 319, a quarter of it 450, 0.1 nm needs 712. With 228 vertices on each edge, the ring is one GDS polygon of 459 points, well within the 8000 of Table 33.1, but beyond the 200 of Release 6.0.

The chords also make the ring slightly small. Averaged round the circle, each edge lies two thirds of its sagitta inside its circle: 0.65 nm on the outer edge, 0.62 nm on the inner. The width changes by only 0.03 nm, but the ring's centre line moves in by 0.63 nm, and its resonances shift by $$\Delta\lambda = \lambda\,(n_\mathrm{eff}/n_g)\,\Delta R/R$$ = 1550 nm × 0.585 × 0.63 nm / 10 µm = 0.06 nm towards the blue. That is small beside the ±0.9 nm that a 1.5 nm die-to-die width variation causes ([Chapter 35]({% link chapters/35_fab.md %})), but it is systematic: a simulation of the perfect circle and a measurement of the drawn polygon differ by it every time. It can be removed by placing the vertices slightly outside the circle, at the radius that gives the polygon the circle's mean radius.

</div>

**Snapping.** The database unit is the finest grid a file can hold. A foundry also has a **manufacturing grid**, on which its rules require every vertex to lie: 1 or 5 nm in CMOS foundries, depending on the process generation {% include cite.html keys="orcutt2010" %}; and a vertex off it is a rule violation ([Chapter 34]({% link chapters/34_verification.md %})). Each vertex therefore moves to the nearest grid point, by up to half a grid step in x and in y: up to 0.71 nm radially on a 1 nm grid. Below a sagitta of about half a grid step, more vertices no longer make the curve more accurate; they only add points ([Figure 33.6](#fig-33-6)c). Snapping also changes the **width**, because the two edges of a bend snap independently.

<figure id="fig-33-6">
  <img src="{{ '/assets/figs/ch33_gridarc.svg' | relative_url }}" style="width:720px" alt="Four panels. (a) The outer edge of a 10 micrometre bend over 1 micrometre of its length, error in nanometres: the ideal arc as a dashed line at zero, chords between vertices on the arc dipping to minus 0.77 nm between vertices, and the snapped polygon whose vertices sit up to half a nanometre off the arc. (b) Width minus 500 nm along a 90 degree bend with 256 vertices per circle: within plus or minus 1 nm on a 1 nm grid, rms 0.26 nm; spikes to plus or minus 5 nm on a 5 nm grid, rms 1.95 nm. (c) Logarithmic plot against the number of vertices per circle from 32 to 4096: the sagitta falls as one over N squared and crosses 1 nm at 225; the rms width error levels off near 0.3 nm on the 1 nm grid and near 1.8 nm on the 5 nm grid. (d) The joint after a 30 degree bend, nanometre by nanometre on a grid of dots: the bend's snapped corner and the corner of a straight placed at the snapped port differ by 1 nm, leaving a thin wedge between the two shapes; the exact corner lies between them.">
  <figcaption><span class="capnum">Figure 33.6.</span> <strong>A curve on a grid.</strong> A circular bend of radius 10 µm and width 500 nm, drawn with 256 vertices per circle. (a) The outer edge against the ideal arc: chords sag by up to 0.77 nm between vertices; snapping to a 1 nm grid moves each vertex by up to 0.5 nm in x and y. (b) The local width along the bend, snapped to a 1 nm and a 5 nm grid. (c) Sagitta and rms width error against the number of vertices: beyond about 200 vertices the grid, not the polygon, sets the error. (d) A 30° bend of radius 10 µm ends at an off-grid point; a straight started from the snapped port and the bend's own snapped end face disagree by 1 nm at one corner. Computed by <code>figsrc/ch33_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-example" markdown="1" id="we-33-3">
<div class="tbox-title">Worked Example 33.3 · A 1 nm and a 5 nm grid on a 10 µm bend</div>

Take a 90° circular bend of radius 10 µm and width 500 nm with 256 vertices per circle (a sagitta of 0.77 nm), snap its two edges to a grid, and measure the local width at 20 000 points along it, every 0.8 nm. On a **1 nm grid** the width error has an rms of 0.26 nm and stays within −0.6 and +0.8 nm (1.4 nm peak to peak); with 4096 vertices per circle it is no better, 0.32 nm rms, because the grid now sets it. On a **5 nm grid** the rms is 1.95 nm and the width swings between −4.4 and +4.8 nm, changing from vertex to vertex every 0.25 µm.

Is this roughness? Real etched sidewalls wander by a few nanometres rms over tens of nanometres ([Chapter 7]({% link chapters/07_loss.md %})), and electron-beam lithography blurs anything much finer than 10–20 nm ([Chapter 35]({% link chapters/35_fab.md %})). The 1 nm grid's error is several times smaller than the real roughness and is smoothed away by the lithography: it is harmless. The 5 nm grid's error is as large as the real roughness and has the same scale as the vertex spacing, so it can print as a periodic width ripple; with a 5 nm grid, use more vertices only if the foundry's own fracturing smooths them, and check rings and gratings, whose phase accumulates over many periods.

</div>

**Off-grid ports.** A grid also breaks joints. A 30° bend of radius 10 µm ends at (5.000, 1.33975) µm, which is not on a 1 nm grid. If the bend is snapped as one polygon and the next straight starts from the port rounded to (5.000, 1.340) µm, their end faces disagree: in [Figure 33.6](#fig-33-6)d one corner differs by 1 nm, leaving a wedge-shaped gap up to 1 nm across. Such slivers are invisible in the viewer, fail design-rule checks, and scatter. Manhattan routing (ports at 0°, 90°, 180°, 270° on grid points) avoids them entirely, which is one reason PDKs and routers prefer it. All-angle routing, which gdsfactory and KLayout both support, needs care: draw a whole route as one polygon, or make the pieces overlap slightly rather than abut.

**Bends.** In the layout an **Euler bend** ([Chapter 8]({% link chapters/08_bends.md %})) {% include cite.html keys="cherchi2013" %} differs from a circular one in more than shape. gdsfactory's default 90° Euler bend with a 10 µm "radius" (the size of its footprint) is 16.637 µm long and reaches a minimum radius of 7.061 µm in its middle, against 15.708 µm and 10 µm for the circular bend of the same footprint; its polygon has 224 points against 124. Its smaller minimum radius is the one the design rules and the bend-loss model must accept, and its length is the one the route length (and an MZI's ΔL) must count.

## <span class="secnum">33.6</span>Floorplans, routing and labels

**Ports, pins and orientation.** A connection is legal only when two ports coincide, face each other (their orientations differ by 180°) and have the same width and cross-section. gdsfactory stores ports as data on the component; SiEPIC-Tools draws them as pins in the layout (Section 33.3), so they survive in the GDS file and any tool can find them; plain GDS has no notion of a port at all, which is why a layout imported without its pins cannot be netlisted. Whatever the tool, the conventions are the same: orientations point out of the device, names are stable (`o1`, `o2`, … or `opt1`, `opt2`, …), and every port lies on the grid.

**Floorplanning.** The floorplan fixes the die, the design area, and where light and current enter. For a chip measured through a fibre array ([Chapter 17]({% link chapters/17_fiberarrays.md %})) every grating coupler sits on a 127 µm pitch, in one column, all facing the same way, with the outermost pair joined by a loopback for alignment. Electrical pads sit on the pitch of the probe that will land on them, away from the fibre array's body. [Figure 33.7](#fig-33-7) shows a small floorplan to scale: a 1000 × 800 µm die with six couplers spanning 5 × 127 = 635 µm; a loopback joining the outermost two round the whole die; an MZI and a ring with a heater between the inner pairs, each labelled at its input; and two 80 µm probe pads on a 100 µm pitch for the heater. An eight-fibre array would span 7 × 127 = 889 µm and need a taller die.

<figure id="fig-33-7">
  <img src="{{ '/assets/figs/ch33_floorplan.svg' | relative_url }}" style="width:700px" alt="A 1000 by 800 micrometre die drawn to scale. On the left, a column of six grating couplers 127 micrometres apart, dimensioned, labelled fibre array. The bottom and top couplers are joined by a loopback waveguide that runs right along the bottom of the die, up the right side and back along the top. Between the second and third couplers from the bottom sits an MZI with a 100 micrometre arm difference; between the fourth and fifth, a small ring with a heater, whose two metal leads run up and right to two 80 micrometre square probe pads 100 micrometres apart. Red dots and monospace text mark the labels opt_in_TE_1550_device_demo_loopback, _mzi and _ringheater on the input couplers. Scale bar 100 micrometres.">
  <figcaption><span class="capnum">Figure 33.7.</span> <strong>A small floorplan, to scale.</strong> The chip drawn by <code>figsrc/ch33_gdsfactory.py</code> with gdsfactory's generic PDK and read back from its GDS file: six grating couplers in one column on the fibre-array pitch, a loopback joining the outermost pair round the die, the MZI test cell of Figure 33.5 and a ring with a heater, each with an <code>opt_in</code> label (red) at its input coupler; the heater's leads run to two probe pads 100 µm apart. The die size, pad size and pad pitch are illustrative. Drawn by <code>figsrc/ch33_figs.py</code> from <code>figsrc/ch33_gdsfactory.py</code>.</figcaption>
</figure>

**Routing.** Routes are Manhattan where they can be, with bends no tighter than the PDK allows, and spaced so that neighbours do not couple: [Chapter 9]({% link chapters/09_couplers.md %}) gives the coupling length against the gap, and a few micrometres between 500 nm strips is safe over millimetres. A **bundle** routes many ports at once at a constant separation, which is how a fibre array's 127 µm pitch is brought down to a device's few micrometres ([Figure 33.8](#fig-33-8)). Its routes differ in length, here by up to 138 µm, which matters wherever their phases or delays must agree. Routes that must cross use a **crossing** cell, which widens the mode before the intersection so that it diffracts little while it crosses ([Chapter 8]({% link chapters/08_bends.md %})); the EBeam PDK's loses under 0.2 dB {% include cite.html keys="ebeampdk,sanchis2009" %}, and a good floorplan needs few of them. The lengths of routes are part of the circuit: in an MZI they set ΔL, so they are taken from the drawn layout (Section 33.4), not from a sketch.

<figure id="fig-33-8">
  <img src="{{ '/assets/figs/ch33_routing.svg' | relative_url }}" style="width:700px" alt="Left: four grating couplers 127 micrometres apart on the left, their ports marked by red arrows pointing east, routed as a bundle: each route turns north or south, runs vertically, and turns east into four parallel waveguides 5 micrometres apart that end at device ports marked by red arrows pointing west; each coupler is labelled with its route length, 418.3, 296.3, 312.3 and 434.3 micrometres from the bottom; a red box marks where the bundle turns. Right: zoom on that box, 45 by 45 micrometres: two routes coming down and two coming up, at x of 10 and 15.5 micrometres, each turning east through a 10 micrometre Euler bend into parallel waveguides 5 micrometres apart, the bends nested inside one another; scale bar 10 micrometres.">
  <figcaption><span class="capnum">Figure 33.8.</span> <strong>A bundle route.</strong> (a) Four couplers on the 127 µm pitch joined by <code>route_bundle</code> to four device ports 5 µm apart, with 10 µm Euler bends; ports (red) point out of their components. The four routes are 296.3 to 434.3 µm long: a bundle keeps its spacing but does not match lengths unless asked to. (b) Where the bundle turns, the bends nest, so the separation is kept through the turn. Drawn by <code>figsrc/ch33_figs.py</code> from <code>figsrc/ch33_gdsfactory.py</code>.</figcaption>
</figure>

**Labels and naming.** Automated test needs to know what each device is and where its input is. openEBL's convention is a text label on layer 10/0 at the input coupler, `opt_in_<polarisation>_<wavelength>_<type>_<deviceID>_<parameters>`, such as `opt_in_TE_1550_device_demo_mzi`; the prober aligns to it, sweeps the matching laser and records the couplers of the same circuit ([Lab 7]({% link labs/lab07_layout.md %}), Table L7.1). [Chapter 34]({% link chapters/34_verification.md %}) covers the rules that check these labels. Device names in labels, cell names and file names should agree, contain no spaces, and identify the designer.

**Metal and heaters.** Heaters are drawn over the waveguide they tune, on the heater layer, with wider, lower-resistance metal leading to pads ([Chapter 18]({% link chapters/18_thermal.md %})). Their widths and overlaps follow the PDK's rules, as in Figure 33.1; leads keep clear of rings and couplers they should not heat; pads sit on a probe pitch and under a pad opening. A heater's resistance is set by its drawn length and width, so they too are computed, not guessed.

**Fill and exclusion.** Chemical-mechanical polishing and etching are uniform only if the density of each layer is similar everywhere, so foundries set minimum and maximum densities over windows of the die and add **fill**, small dummy shapes, where a layout is too empty. Fill near a waveguide would scatter or absorb light, so photonic layouts carry **exclusion** (keep-out) zones around optical devices where no fill may go. In one CMOS foundry study, metal had to be kept 2–3 µm away from the waveguides laterally but only about 1 µm vertically, and because the density had to be uniform only over 25–150 µm, adding denser metal around the photonic regions met the minimum densities of 15–25 % {% include cite.html keys="orcutt2010" %}. The EBeam PDK has a Keep out layer, 202/0, among its layers {% include cite.html keys="ebeampdk" %}; in a CMOS-style foundry the fill and exclusion layers and their distances come from the PDK's rules.

## <span class="secnum">33.7</span>Hierarchy hygiene and version control

A clean layout is easier to check, merge and reuse. Six habits matter.

1. **One top cell**, named for the design. Delete stray top cells before submitting; openEBL's checks require exactly one ([Lab 7]({% link labs/lab07_layout.md %})).
2. **Unique, meaningful cell names**, prefixed with the designer or project, so that a merge cannot collide (Section 33.2). Never rename, edit or move the origin of a foundry's black-box cells, which are swapped for the real geometry at the foundry.
3. **No duplicated geometry**: a device used twice is one cell placed twice, and a parameter sweep is one function called with different parameters.
4. **No needless flattening.** Keep PCells and PDK cells as cells; flatten only what the foundry asks for.
5. **Placements on the grid**, rotations by multiples of 90° for cells holding Manhattan geometry, and one database unit (1 nm) throughout. Writing a layout with a different database unit rescales it, and rounding can then distort it {% include cite.html keys="klayoutapi" %}. Coarse grids used inside cells should be locked to one global grid, so that neighbouring cells cannot create spacing errors between them {% include cite.html keys="orcutt2010" %}.
6. **Pins, DevRec and labels kept with their devices**, so that the netlist can be extracted after any edit.

**Version control.** A GDS file is binary, and the same layout can be written in different bytes: BGNLIB and BGNSTR carry time stamps (two writes a second apart differed in four bytes; with KLayout's time stamps switched off, the files were identical), cells may be written in a different order, and the last bit of a real can differ between writers (Section 33.2). So track the **source** of the layout, the script or the PCell parameters with the PDK's version, in Git, and compare layouts **geometrically**, with an XOR of the flattened layers, not byte by byte. Generated GDS files can be kept for reference (Git LFS suits large ones) and checked in tests against the previous version; gdsfactory's `difftest`, for instance, stores a reference GDS for each cell and runs an XOR against it whenever the cell is regenerated. openEBL itself takes submissions as pull requests and runs its checks on every commit ([Lab 8]({% link labs/lab08_submit.md %})).

<div class="tbox tbox-pitfall" markdown="1">
<div class="tbox-title">Layouts that look right and are wrong</div>

A viewer shows geometry, not intent. Each problem met in this chapter looks fine at a glance: a cell merged into its namesake, so that two designs each show two rings; a polygon of 12 000 vertices split at the default limit into 48 kB records that a strict reader would refuse; a 1 nm wedge between a 30° bend and the next straight; a GDS file that differs from yesterday's only in four bytes of time stamp, so that an unchanged design looks changed. Each is caught by a check that reads the data ([Chapter 34]({% link chapters/34_verification.md %})), not by looking.

</div>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

The chip of [Labs 7]({% link labs/lab07_layout.md %}) and [8]({% link labs/lab08_submit.md %}) uses everything in this chapter: layers 1/0, 10/0 and 99/0 of the EBeam PDK with a 1 nm database unit; PDK couplers placed as cells on the 127 µm pitch; routes of 500 nm strip with 10 µm Euler bends whose lengths are read from the layout; rings drawn as polygons whose gaps land on vertices; one top cell; `opt_in` labels on 10/0; and a GDS file checked by SiEPIC-Tools before it is submitted.

</div>

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- A layout is one picture per patterning step, on numbered layers (layer/datatype); some layers are fabricated, others only guide the tools (labels, device outlines, pins, floorplan).
- GDSII is a stream of length-prefixed records: library, structures (cells), elements (boundary, path, SREF, AREF, text). Coordinates are 32-bit integers in database units, usually 1 nm, giving ±2.15 m of range.
- Release 6.0 allowed 200 vertices, layers 0–63 and 32-character names; tools now go far beyond, so check what your foundry's reader accepts. GDSII has no holes: rings are stored with a cut line.
- Hierarchy keeps files small: 10 000 rings take 4 kB as an array, 284 kB as single placements and 37.7 MB flat. OASIS is the compact successor.
- KLayout views, edits, measures and scripts layouts (`klayout.db` in Python); SiEPIC-Tools adds waveguides from paths, pins, connectivity checks and netlists; gdsfactory builds layouts as code with ports, cross-sections, routing and netlists for circuit simulation.
- A 10 µm ring needs about 225 vertices for a 1 nm sagitta; below about half a grid step, the grid, not the vertex count, limits accuracy (0.3 nm rms width error on a 1 nm grid, about 2 nm on a 5 nm grid). Off-grid ports create nanometre slivers: route Manhattan where possible.
- Floorplan couplers on the 127 µm fibre pitch with a loopback, label inputs for test, keep fill out of optical zones, keep the hierarchy clean, and version the code that makes the GDS.

</div>

## Reading

{% include reflist.html keys="calma1987,semip39,reich2003,klayout,klayoutapi,siepictools,ebeampdk,gdsfactory,ubcpdk,sax,bogaerts2018,orcutt2010,cherchi2013,sanchis2009,chrostowski2015" %}
