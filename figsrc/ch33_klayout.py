"""KLayout experiments for Chapter 33 (run in Docker: klayout 0.30.13; writes figsrc/ch33_klayout.json).

    MSYS_NO_PATHCONV=1 docker exec -w /repo photonics-labs /opt/conda/envs/labs/bin/python figsrc/ch33_klayout.py

A. reads the tiny GDS written by ch33_gdsii.py back with KLayout, as an independent check of that writer;
B. runs the chapter's KLayout example (ring filters: a bus waveguide and a ring, instanced three times) and
   measures what it drew;
C. draws the multi-layer heater-ring cell of Figure 33.1 on SiEPIC EBeam PDK layer numbers;
D. writes 10 000 rings with and without hierarchy, as GDS and OASIS, and measures the file sizes;
E. checks three behaviours the chapter describes: holes in GDSII, the vertex limit, time stamps,
   and what happens when two files with the same cell name are read into one layout.
GDS files go to a temporary folder; only the numbers and the outlines for the figures are kept.
"""
import json
import math
import os
import sys
import tempfile
import time

import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ch33_gdsii  # noqa: E402

TMP = tempfile.mkdtemp(prefix="ch33_")
OUT = {}


def polys(cell, layer, dbu):
    """Outlines of a cell's shapes on one layer, flattened, in micrometres (hull and holes)."""
    out = []
    for it in cell.begin_shapes_rec(layer):
        p = it.shape().polygon
        if p is None:
            continue
        p = p.transformed(it.trans())
        out.append([[[q.x * dbu, q.y * dbu] for q in p.each_point_hull()]]
                   + [[[q.x * dbu, q.y * dbu] for q in p.each_point_hole(h)] for h in range(p.holes())])
    return out


# ---------------------------------------------------------------- A. the tiny GDS, read back by KLayout
def part_a():
    path = os.path.join(TMP, "tiny.gds")
    data = ch33_gdsii.build_tiny()
    open(path, "wb").write(data)
    ly = kdb.Layout()
    ly.read(path)
    top = ly.top_cell()
    res = {"bytes": len(data), "records": len(ch33_gdsii.records(data)), "dbu": ly.dbu,
           "top": top.name, "cells": sorted(c.name for c in ly.each_cell())}
    insts = []
    for inst in top.each_inst():
        a = inst.cell_inst
        insts.append({"cell": ly.cell(inst.cell_index).name, "trans": str(a.trans), "regular_array": a.is_regular_array(),
                      "na": a.na, "nb": a.nb, "a": str(a.a), "b": str(a.b)})
    res["instances"] = insts
    shapes = []
    for li in ly.layer_indexes():
        info = ly.get_info(li)
        for s in top.shapes(li).each():
            shapes.append({"layer": f"{info.layer}/{info.datatype}", "type": "path" if s.is_path() else
                           "text" if s.is_text() else "polygon", "text": s.text.string if s.is_text() else None,
                           "width": s.path_width if s.is_path() else None,
                           "points": [[q.x, q.y] for q in s.path.each_point()] if s.is_path() else None})
    res["top_shapes"] = shapes
    wg = ly.cell("WG")
    res["wg_box"] = str(wg.bbox())
    res["top_bbox_um"] = [top.dbbox().left, top.dbbox().bottom, top.dbbox().right, top.dbbox().top]
    # outlines for the figure: flatten everything on 1/0, and the label
    li = ly.layer(1, 0)
    res["outlines"] = polys(top, li, ly.dbu)
    for it in top.begin_shapes_rec(ly.layer(1, 0)):
        pass
    res["label_um"] = [0.0, 381.0]
    OUT["tiny"] = res
    print("A. tiny GDS read by KLayout:", json.dumps({k: v for k, v in res.items() if k != "outlines"}, indent=None)[:900])


# ---------------------------------------------------------------- B. the chapter's KLayout example
# ---- listing starts (shown in Section 33.3; keep in step with the chapter)
def example(path):
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
    ly.write(path)
    return ly
# ---- listing ends


def part_b():
    path = os.path.join(TMP, "ring_filters.gds")
    example(path)
    ly = kdb.Layout()
    ly.read(path)                                     # check the file, not the objects in memory
    top = ly.top_cell()
    si = ly.layer(1, 0)
    res = {"bytes": os.path.getsize(path), "cells": sorted(c.name for c in ly.each_cell()), "top": top.name,
           "instances": [[ly.cell(i.cell_index).name, i.dcplx_trans.disp.x, i.dcplx_trans.disp.y] for i in top.each_inst()]}
    meas = []
    for name in res["cells"]:
        if not name.startswith("ring"):
            continue
        c = ly.cell(name)
        shapes = list(c.shapes(si).each())
        ring = [s.polygon for s in shapes if s.polygon.num_points() > 4][0]
        bus = [s.polygon for s in shapes if s.polygon.num_points() == 4][0]
        # minimum distance between ring and bus, from KLayout's separation check (in dbu)
        ep = kdb.Region(ring).separation_check(kdb.Region(bus), 1000)
        gap = min(e.distance() for e in ep.each()) * ly.dbu
        # the ring as stored in GDS: hull points and holes after the round trip
        meas.append({"cell": name, "gap_um": gap, "ring_points": ring.num_points(), "ring_holes": ring.holes(),
                     "ring_hull_points": ring.num_points_hull(), "ring_area_um2": ring.area() * ly.dbu ** 2})
    res["rings"] = meas
    n, ro, ri = 256, 10.25, 9.75
    res["sagitta_outer_nm"] = ro * (1 - math.cos(math.pi / n)) * 1e3
    res["ideal_area_um2"] = math.pi * (ro ** 2 - ri ** 2)
    res["outlines"] = polys(top, si, ly.dbu)
    res["texts"] = [[s.text.string, s.text.x * ly.dbu, s.text.y * ly.dbu] for s in top.shapes(ly.layer(10, 0)).each()]
    OUT["example"] = res
    print("B. example:", json.dumps({k: v for k, v in res.items() if k != "outlines"})[:1200])


# ---------------------------------------------------------------- C. a heater ring on SiEPIC EBeam layers
LAYERS = {"Si": (1, 0), "M1_heater": (11, 0), "M2_router": (12, 0), "M_Open": (13, 0), "Text": (10, 0),
          "DevRec": (68, 0), "PinRec": (1, 10), "FloorPlan": (99, 0)}


def part_c():
    """A 10 um ring with a 3 um heater, its leads and two probe pads, on the EBeam layer numbers.
    Widths follow the minimums of SiEPIC_EBeam_DRC.lydrc where they apply (M1 3 um, M2 5 um, M2 over M1 3 um,
    M_Open 10 um); pad size and pitch are illustrative choices."""
    ly = kdb.Layout()
    ly.dbu = 0.001
    L = {k: ly.layer(*v) for k, v in LAYERS.items()}
    c = ly.create_cell("ring_heater")
    R, w, gap, n = 10.0, 0.5, 0.2, 256

    def arc(r, a0, a1, m):
        return [kdb.DPoint(r * math.cos(a0 + (a1 - a0) * k / m), r * math.sin(a0 + (a1 - a0) * k / m)) for k in range(m + 1)]

    ring = kdb.DPolygon([kdb.DPoint(p.x, p.y) for p in arc(R + w / 2, 0, 2 * math.pi, n)[:-1]])
    ring.insert_hole(arc(R - w / 2, 0, 2 * math.pi, n)[:-1])
    c.shapes(L["Si"]).insert(ring)
    yb = -(R + w + gap)                               # bus below the ring
    xb = 40.0
    c.shapes(L["Si"]).insert(kdb.DBox(-xb, yb - w / 2, xb, yb + w / 2))
    # heater: a 3 um wide arc over the ring, open at the bottom where the bus couples, with M1 stubs out to contact tabs
    hw, a0, a1 = 3.0, math.radians(-30), math.radians(210)
    heater = arc(R + hw / 2, a0, a1, 200) + arc(R - hw / 2, a1, a0, 200)
    c.shapes(L["M1_heater"]).insert(kdb.DPolygon(heater))
    xt, yt = 18.0, R * math.sin(a0)                    # tab centres at (+-18, -5)
    for s in (1, -1):
        c.shapes(L["M1_heater"]).insert(kdb.DBox(min(s * R * math.cos(a0), s * xt), yt - hw / 2, max(s * R * math.cos(a0), s * xt), yt + hw / 2))
        c.shapes(L["M1_heater"]).insert(kdb.DBox(s * xt - 4, yt - 4, s * xt + 4, yt + 4))       # 8 x 8 um tab
    # M2 leads from the tabs up to two 50 um pads, 100 um apart
    pad, pitch, ypad = 50.0, 100.0, 85.0
    for s in (-1, 1):
        x, xp = s * xt, s * pitch / 2
        c.shapes(L["M2_router"]).insert(kdb.DBox(x - 3.5, yt - 3.5, x + 3.5, yt + 3.5))          # over the tab
        c.shapes(L["M2_router"]).insert(kdb.DPath([kdb.DPoint(x, yt), kdb.DPoint(x, 35.0), kdb.DPoint(xp, 35.0),
                                                   kdb.DPoint(xp, ypad)], 6.0))
        c.shapes(L["M2_router"]).insert(kdb.DBox(xp - pad / 2, ypad - pad / 2, xp + pad / 2, ypad + pad / 2))
        c.shapes(L["M_Open"]).insert(kdb.DBox(xp - pad / 2 + 5, ypad - pad / 2 + 5, xp + pad / 2 - 5, ypad + pad / 2 - 5))
    # SiEPIC-style pins at the bus ends (20 nm paths across the port, pointing out) and the device recognition box
    for x, d in ((-xb, -1), (xb, 1)):
        c.shapes(L["PinRec"]).insert(kdb.DPath([kdb.DPoint(x - d * 0.01, yb), kdb.DPoint(x + d * 0.01, yb)], w))
        c.shapes(L["PinRec"]).insert(kdb.DText("opt1" if d < 0 else "opt2", kdb.DTrans(x, yb)))
    c.shapes(L["DevRec"]).insert(kdb.DBox(-xb, yb - 2.0, xb, R + 3.0))
    c.shapes(L["Text"]).insert(kdb.DText("opt_in_TE_1550_device_demo_ringheater", kdb.DTrans(-xb, yb)))
    c.shapes(L["FloorPlan"]).insert(kdb.DBox(-pitch / 2 - pad / 2 - 10, yb - 15, pitch / 2 + pad / 2 + 10, ypad + pad / 2 + 10))
    path = os.path.join(TMP, "ring_heater.gds")
    ly.write(path)
    ly2 = kdb.Layout()
    ly2.read(path)
    top = ly2.top_cell()
    res = {"layers": {}, "texts": [], "paths": []}
    for name, (ln, dt) in LAYERS.items():
        li = ly2.find_layer(ln, dt)
        if li is None:
            continue
        res["layers"][name] = {"ld": [ln, dt], "polys": polys(top, li, ly2.dbu)}
        for s in top.shapes(li).each():
            if s.is_text():
                res["texts"].append([name, s.text.string, s.text.x * ly2.dbu, s.text.y * ly2.dbu])
    OUT["heater"] = res
    print("C. heater ring layers:", {k: len(v["polys"]) for k, v in res["layers"].items()})


# ---------------------------------------------------------------- D. 10 000 rings: hierarchy and file size
def ring_cell(ly, n):
    c = ly.create_cell("ring")
    R, w, gap, L = 10.0, 0.5, 0.2, 30.0
    pts = lambda r: [kdb.DPoint(r * math.sin(2 * math.pi * k / n), r * math.cos(2 * math.pi * k / n)) for k in range(n)]
    ring = kdb.DPolygon(pts(R + w / 2))
    ring.insert_hole(pts(R - w / 2))
    si = ly.layer(1, 0)
    c.shapes(si).insert(ring)
    yb = R + w + gap
    c.shapes(si).insert(kdb.DBox(-L / 2, yb - w / 2, L / 2, yb + w / 2))
    return c


def write_both(ly, stem):
    """Sizes of GDS, plain OASIS (no shape arrays, no compression) and compact OASIS (level 2, CBLOCKs)."""
    o = kdb.SaveLayoutOptions()
    o.gds2_write_timestamps = False
    g = os.path.join(TMP, stem + ".gds")
    ly.write(g, o)
    sizes = [os.path.getsize(g)]
    for lev, cb in ((0, False), (2, True)):
        oo = kdb.SaveLayoutOptions()
        oo.format = "OASIS"
        oo.oasis_compression_level = lev
        oo.oasis_write_cblocks = cb
        s = os.path.join(TMP, f"{stem}_{lev}.oas")
        ly.write(s, oo)
        sizes.append(os.path.getsize(s))
    return sizes


def part_d():
    # vertices per circle: the fewest that keep the chord sagitta within 1 nm on the 10.25 um outer edge
    e, R_out = 0.001, 10.25
    n = math.ceil(math.pi / math.acos(1 - e / R_out))
    n += (-n) % 4                                      # a multiple of 4 puts vertices on the axes
    NX = NY = 100
    pitch_x, pitch_y = 40.0, 30.0
    res = {"n_vertices_per_circle": n, "nx": NX, "ny": NY, "pitch_um": [pitch_x, pitch_y]}
    variants = {}
    # (1) one ring cell, one array instance (an AREF in GDS)
    ly = kdb.Layout(); ly.dbu = 0.001
    rc = ring_cell(ly, n)
    top = ly.create_cell("TOP")
    top.insert(kdb.DCellInstArray(rc, kdb.DTrans(), kdb.DVector(pitch_x, 0), kdb.DVector(0, pitch_y), NX, NY))
    variants["array"] = write_both(ly, "rings_aref")
    # (2) one ring cell, 10 000 single instances (SREFs)
    ly = kdb.Layout(); ly.dbu = 0.001
    rc = ring_cell(ly, n)
    top = ly.create_cell("TOP")
    for i in range(NX):
        for j in range(NY):
            top.insert(kdb.DCellInstArray(rc, kdb.DTrans(i * pitch_x, j * pitch_y)))
    variants["sref"] = write_both(ly, "rings_sref")
    # (3) flat: every ring's polygons copied into the top cell
    top.flatten(True)
    variants["flat"] = write_both(ly, "rings_flat")
    # one ring cell alone, for the per-ring cost
    ly1 = kdb.Layout(); ly1.dbu = 0.001
    ring_cell(ly1, n)
    variants["one_ring"] = write_both(ly1, "one_ring")
    # check: the flat and hierarchical files hold the same geometry (XOR of the flattened layouts is empty)
    la = kdb.Layout(); la.read(os.path.join(TMP, "rings_aref.gds"))
    lf = kdb.Layout(); lf.read(os.path.join(TMP, "rings_flat_2.oas"))
    ra = kdb.Region(la.top_cell().begin_shapes_rec(la.layer(1, 0)))
    rf = kdb.Region(lf.top_cell().begin_shapes_rec(lf.layer(1, 0)))
    res["xor_empty"] = (ra ^ rf).is_empty()
    res["polygons_flat"] = rf.count()
    # how the ring is stored in GDS: one polygon whose hole is joined to the hull by a cut line
    ring_gds = [s.polygon for s in la.cell("ring").shapes(la.layer(1, 0)).each() if s.polygon.num_points() > 4][0]
    res["ring_in_gds"] = {"points": ring_gds.num_points(), "holes": ring_gds.holes()}
    res["sizes_bytes"] = {k: {"gds": v[0], "oas_plain": v[1], "oas_compact": v[2]} for k, v in variants.items()}
    OUT["hierarchy"] = res
    print("D. hierarchy:", json.dumps(res))


# ---------------------------------------------------------------- E. holes, vertex limit, time stamps, name collisions
def part_e():
    res = {}
    # E1. a Bragg grating drawn as one polygon: 1500 periods of 317 nm, +-25 nm corrugation on a 500 nm strip,
    #     4 vertices per period on each edge, so 12 000 vertices; written with three settings and read back
    ly = kdb.Layout(); ly.dbu = 0.001
    c = ly.create_cell("bragg")
    NP, a, w, dw = 1500, 317, 500, 25                  # in dbu (nm)
    top_e, bot_e = [], []
    for k in range(NP):
        x0 = k * a
        for x, h in ((x0, w // 2 + dw), (x0 + a // 2, w // 2 + dw), (x0 + a // 2, w // 2 - dw), (x0 + a, w // 2 - dw)):
            top_e.append(kdb.Point(x, h)); bot_e.append(kdb.Point(x, -h))
    poly = kdb.Polygon(top_e + bot_e[::-1])
    c.shapes(ly.layer(1, 0)).insert(poly)
    runs = {}
    for label, kw in (("default", {}), ("max200", {"gds2_max_vertex_count": 200}),
                      ("multi_xy", {"gds2_multi_xy_records": True})):
        o = kdb.SaveLayoutOptions()
        for k, v in kw.items():
            setattr(o, k, v)
        path = os.path.join(TMP, f"bragg_{label}.gds")
        ly.write(path, o)
        lr = kdb.Layout(); lr.read(path)
        got = [s.polygon.num_points() for s in lr.top_cell().shapes(lr.layer(1, 0)).each()]
        merged = kdb.Region(lr.top_cell().shapes(lr.layer(1, 0))).merged()
        data = open(path, "rb").read()
        biggest = max(len(r[4]) + 4 for r in ch33_gdsii.records(data))
        runs[label] = {"polygons": len(got), "max_points": max(got), "merged_polygons": merged.count(),
                       "area_equal": merged.area() == poly.area(), "largest_record_bytes": biggest,
                       "file_bytes": len(data)}
    res["bragg"] = {"vertices": poly.num_points(), "default_max_vertex_count": kdb.SaveLayoutOptions().gds2_max_vertex_count,
                    "runs": runs}
    # E2. time stamps: the same layout written twice, a second apart
    def write(ts):
        ly = kdb.Layout(); ly.dbu = 0.001
        ly.create_cell("A").shapes(ly.layer(1, 0)).insert(kdb.Box(0, 0, 500, 10000))
        o = kdb.SaveLayoutOptions(); o.gds2_write_timestamps = ts
        f = os.path.join(TMP, f"ts_{ts}_{time.time():.3f}.gds")
        ly.write(f, o)
        return open(f, "rb").read()
    a1 = write(True); time.sleep(1.2); a2 = write(True)
    b1 = write(False); time.sleep(1.2); b2 = write(False)
    res["timestamps"] = {"default_identical": a1 == a2, "no_timestamps_identical": b1 == b2,
                         "bytes_differing_default": sum(x != y for x, y in zip(a1, a2)), "size": len(a1)}
    # E3. two files that both contain a cell called "ring" (radius 10 and radius 5), read into one layout
    def ring_file(r, name):
        ly = kdb.Layout(); ly.dbu = 0.001
        c = ly.create_cell("ring")
        q = kdb.DPolygon([kdb.DPoint((r + .25) * math.cos(2 * math.pi * k / 64), (r + .25) * math.sin(2 * math.pi * k / 64)) for k in range(64)])
        c.shapes(ly.layer(1, 0)).insert(q)
        t = ly.create_cell(name)
        t.insert(kdb.DCellInstArray(c, kdb.DTrans()))
        f = os.path.join(TMP, name + ".gds"); ly.write(f); return f
    fa, fb = ring_file(10.0, "chipA"), ring_file(5.0, "chipB")
    out = {}
    for mode in ("AddToCell", "RenameCell"):
        ly = kdb.Layout()
        lo = kdb.LoadLayoutOptions()
        lo.cell_conflict_resolution = getattr(kdb.LoadLayoutOptions, mode)
        ly.read(fa, lo); ly.read(fb, lo)
        out[mode] = {c.name: c.shapes(ly.layer(1, 0)).size() for c in ly.each_cell()}
    res["collision"] = out
    # E4. coordinate range of a 4-byte integer at three database units
    res["coord_range_m"] = {str(d): (2 ** 31 - 1) * d for d in (1e-9, 1e-10, 1e-12)}
    OUT["checks"] = res
    print("E. checks:", json.dumps(res))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("klayout", getattr(kdb, "__version__", ""))
    parts = sys.argv[1:] or list("ABCDE")             # e.g. "C" re-runs one part and keeps the others' results
    jpath = os.path.join(HERE, "ch33_klayout.json")
    if sys.argv[1:] and os.path.exists(jpath):
        OUT.update(json.load(open(jpath, encoding="utf-8")))
    for k in parts:
        {"A": part_a, "B": part_b, "C": part_c, "D": part_d, "E": part_e}[k]()
    OUT["klayout_version"] = getattr(kdb, "__version__", "")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(OUT, f, separators=(",", ":"))
    print("wrote ch33_klayout.json")
