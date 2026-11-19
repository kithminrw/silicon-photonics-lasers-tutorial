"""ch34_drc.py -- the DRC example of Chapter 34: a small test layout with deliberate mistakes, checked by the rule
deck figsrc/ch34_deck.lydrc.

Three steps (all lengths in micrometres, database unit 1 nm):

  1. make the test layout (needs KLayout's Python module, e.g. in the photonics-labs container):
       python ch34_drc.py make                -> figsrc/ch34_test.gds, figsrc/ch34_geom.json
  2. run the rule deck with the KLayout application in batch mode:
       klayout -b -r ch34_deck.lydrc -rd input=ch34_test.gds -rd report=ch34_test.lyrdb
  3. read the report (plain Python):
       python ch34_drc.py parse               -> figsrc/ch34_drc.json (markers per rule, for the figures)

  python ch34_drc.py check   repeats every rule of the deck with KLayout's Python Region API, as a cross-check.
  python ch34_drc.py pulley  the pulley coupler drawn on the 1 nm and 5 nm grids, against 0, 2 and 5 nm of tolerance
  python ch34_drc.py engine  edge-pair and sizing checks on small shapes, for the figure of the DRC engine

The process ("toy SOI") and its rule values are illustrative, chosen for this example; they are not any foundry's.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GDS = os.path.join(HERE, "ch34_test.gds")
GEOM = os.path.join(HERE, "ch34_geom.json")
RDB = os.path.join(HERE, "ch34_test.lyrdb")
OUT = os.path.join(HERE, "ch34_drc.json")

DBU = 0.001                       # 1 nm database unit
GRID = 0.005                      # 5 nm manufacturing grid of the toy process
L_SI, L_SLAB, L_HTR, L_M, L_FP = (1, 0), (2, 0), (11, 0), (12, 0), (99, 0)

# ring parameters (shared by the figures)
RING = dict(R=5.0, w=0.5, gap=0.2, step_ring=2.5, step_bus=1.0)


def ring_pts(cx, cy, r, step, a0=0.0, a1=360.0):
    """Points on a circle of radius r every `step` degrees from a0 to a1 (a1 excluded for a full circle)."""
    n = int(round((a1 - a0) / step))
    full = abs((a1 - a0) - 360.0) < 1e-9
    ks = range(n) if full else range(n + 1)
    return [(cx + r * math.cos(math.radians(a0 + k * step)), cy + r * math.sin(math.radians(a0 + k * step))) for k in ks]


def snap(v, g):
    return round(v / g) * g


def make():
    import klayout.db as kdb
    ly = kdb.Layout()
    ly.dbu = DBU
    top = ly.create_cell("CH34_TEST")
    li = {k: ly.layer(*v) for k, v in dict(si=L_SI, slab=L_SLAB, htr=L_HTR, m=L_M, fp=L_FP).items()}
    feats = []                                   # (name, x, y) annotation anchors for the figure

    def to_dpts(pts):
        return [kdb.DPoint(x, y) for x, y in pts]

    def poly(layer, pts, raw=False):
        p = kdb.DPolygon(to_dpts(pts), raw)
        top.shapes(li[layer]).insert(p)

    def rect(layer, x0, y0, x1, y1):
        top.shapes(li[layer]).insert(kdb.DBox(x0, y0, x1, y1))

    def wg(x0, x1, y, w):
        rect("si", x0, y - w / 2, x1, y + w / 2)

    # floorplan (design area)
    rect("fp", 0, 0, 90, 58)

    # --- row A (y = 52): widths, tapers, the floorplan edge
    wg(3, 17, 52, 0.50); feats.append(("A1 waveguide 500 nm", 10, 52))
    wg(21, 31, 52, 0.12); feats.append(("A2 waveguide 120 nm", 26, 52))
    wg(33, 35, 52, 0.50); poly("si", [(35, 51.75), (44, 52), (35, 52.25)])
    feats.append(("A3 taper to a point", 39.5, 52))
    wg(47, 49, 52, 0.50); poly("si", [(49, 51.75), (59, 51.91), (59, 52.09), (49, 52.25)])
    feats.append(("A4 taper, 180 nm tip", 54, 52))
    wg(78, 95, 52, 0.50); feats.append(("A5 crosses the floorplan", 86.5, 52))

    # --- row B (y = 40): couplers, a grating, small shapes
    for (xa, gap, nm) in ((3, 0.200, "B1 coupler, 200 nm gap"), (21, 0.160, "B2 coupler, 160 nm gap")):
        y1 = 40 + gap / 2 + 0.25
        y2 = 40 - gap / 2 - 0.25
        wg(xa, xa + 14, y1, 0.5); wg(xa, xa + 14, y2, 0.5)
        feats.append((nm, xa + 7, 40))
    # sidewall Bragg grating drawn as ONE polygon: 500 nm core, 50 nm teeth, period 320 nm, teeth 160 nm long
    xg0, n_teeth, per, tl, dw = 41.0, 10, 0.32, 0.16, 0.05
    top_edge = [(39.0, 40.25)]
    for k in range(n_teeth):
        xs = xg0 + k * per
        top_edge += [(xs, 40.25), (xs, 40.25 + dw), (xs + tl, 40.25 + dw), (xs + tl, 40.25)]
    top_edge.append((xg0 + n_teeth * per + 2.0, 40.25))
    bot_edge = [(x, 80.0 - y) for (x, y) in top_edge]           # mirror about y = 40
    poly("si", top_edge + bot_edge[::-1])
    feats.append(("B3 Bragg grating, 160 nm notches", xg0 + n_teeth * per / 2, 40))
    rect("si", 52.4, 39.9, 52.6, 40.1); feats.append(("B4 0.2 x 0.2 um square", 52.5, 40))
    # a 3 um waveguide whose outline was built from the top edge and the bottom edge, the latter not reversed
    poly("si", [(56, 40.25), (59, 40.25), (56, 39.75), (59, 39.75)], raw=True); feats.append(("B5 self-intersecting", 57.5, 40))

    # --- row C (y ~ 18): rings with R = 5 um, w = 0.5 um, 200 nm gap
    R, w, gap = RING["R"], RING["w"], RING["gap"]
    # C1: ring with a straight bus, vertices computed in floating point and rounded only to the 1 nm database unit
    cx, cy = 12.0, 12.0 + 0.25 + gap + R + w / 2
    wg(4, 20, 12.0, 0.5)
    outer = ring_pts(cx, cy, R + w / 2, RING["step_ring"])
    inner = ring_pts(cx, cy, R - w / 2, RING["step_ring"])
    p = kdb.DPolygon(to_dpts(outer))
    p.insert_hole(to_dpts(inner))
    top.shapes(li["si"]).insert(p)
    feats.append(("C1 ring, not snapped", cx, cy))
    ring1 = dict(cx=cx, cy=cy)
    # C2: pulley (wrap-around) coupler: ring and a concentric bus arc, every vertex snapped to the 5 nm grid
    cx2, cy2 = 40.0, cy
    outer = [(snap(x, GRID), snap(y, GRID)) for x, y in ring_pts(cx2, cy2, R + w / 2, RING["step_ring"])]
    inner = [(snap(x, GRID), snap(y, GRID)) for x, y in ring_pts(cx2, cy2, R - w / 2, RING["step_ring"])]
    p = kdb.DPolygon(to_dpts(outer))
    p.insert_hole(to_dpts(inner))
    top.shapes(li["si"]).insert(p)
    rb_in, rb_out = R + w / 2 + gap, R + w / 2 + gap + 0.5
    arc_in = ring_pts(cx2, cy2, rb_in, RING["step_bus"], 225, 315)
    arc_out = ring_pts(cx2, cy2, rb_out, RING["step_bus"], 225, 315)
    pts = [(snap(x, GRID), snap(y, GRID)) for x, y in arc_out + arc_in[::-1]]
    poly("si", pts)
    feats.append(("C2 pulley coupler, snapped to 5 nm", cx2, cy2))
    ring2 = dict(cx=cx2, cy=cy2)

    # --- row D (y = 4): rib waveguide in its slab, heater with metal contacts
    wg(60, 80, 4.0, 0.5)
    rect("slab", 59, 2.75, 81, 4.75)          # encloses the rib by 1.0 um below and at the ends, 0.5 um above
    feats.append(("D1 rib in slab: 1.0 / 0.5 um", 70, 4))
    wg(58, 86, 10.0, 0.5)
    rect("htr", 62, 9.0, 82, 11.0)            # 2 um wide heater over a waveguide
    rect("m", 58, 7.5, 63, 12.5)              # left contact pad: overlaps the heater by 1.0 um
    rect("m", 81.5, 7.5, 86.5, 12.5)          # right contact pad: overlaps it by only 0.5 um
    feats.append(("D2 heater and contacts", 72, 10))

    ly.write(GDS)

    # geometry for the figures: every polygon per layer, hulls and holes in um
    geom = {}
    for name, l in li.items():
        lst = []
        for sh in top.shapes(l).each():
            if sh.is_box() or sh.is_polygon() or sh.is_simple_polygon():
                dp = sh.dpolygon
                lst.append(dict(hull=[(q.x, q.y) for q in dp.each_point_hull()],
                                holes=[[(q.x, q.y) for q in dp.each_point_hole(h)] for h in range(dp.holes())]))
        geom[name] = lst
    geom["features"] = feats
    geom["rings"] = dict(C1=ring1, C2=ring2, **RING)
    with open(GEOM, "w") as f:
        json.dump(geom, f, indent=0)
    print("wrote", GDS, "and", GEOM)


# ---------------------------------------------------------------- the deck's rules, again, in Python
def check():
    """Every rule of ch34_deck.lydrc, with the Region API of KLayout's Python module (same engine)."""
    import klayout.db as kdb
    ly = kdb.Layout(); ly.read(GDS); top = ly.top_cell()
    reg = lambda l: kdb.Region(top.begin_shapes_rec(ly.layer(*l)))
    si, slab, htr, m, fp = (reg(l) for l in (L_SI, L_SLAB, L_HTR, L_M, L_FP))
    d = lambda um: int(round(um / ly.dbu))
    E = kdb.Metrics.Euclidian
    res = {
        "SI.W.1": si.width_check(d(0.150), False, E, 90).count(),
        "SI.S.1": si.isolated_check(d(0.200), False, E, 90).count(),
        "SI.N.1": si.notch_check(d(0.200), False, E, 90).count(),
        "SI.A.1": si.with_area(0, int(0.1 / ly.dbu ** 2), False).count(),
        "SI.ANG.1": si.corners(-180.0, -150.0, 1, True, False).count(),
        "SI.GRID.1": si.grid_check(d(GRID), d(GRID)).count(),
        "SI.ODD.1": kdb.Region(top.begin_shapes_rec(ly.layer(*L_SI))).strange_polygon_check().count(),
        "SI.FP.1": (si - fp).count(),
        "SLAB.EN.1": slab.enclosing_check(si, d(1.0), False, E, 90).count(),
        "M.OV.1": m.overlap_check(htr, d(1.0), False, E, 90).count(),
    }
    for k, v in res.items():
        print(f"{k:10s} {v}")
    return res


def pulley():
    """The pulley coupler of the test layout drawn three ways (vertices rounded to the 1 nm database unit, or
    snapped to the 5 nm grid), checked against the 200 nm space rule with 0, 2 and 5 nm of tolerance."""
    import klayout.db as kdb
    R, w, gap = RING["R"], RING["w"], RING["gap"]
    cx, cy = 40.0, 12.0 + 0.25 + gap + R + w / 2
    out = {}
    for name, g in (("dbu", DBU), ("grid", GRID)):
        q = lambda pts: [kdb.Point(int(round(snap(x, g) / DBU)), int(round(snap(y, g) / DBU))) for x, y in pts]
        ring = kdb.Polygon(q(ring_pts(cx, cy, R + w / 2, RING["step_ring"])))
        ring.insert_hole(q(ring_pts(cx, cy, R - w / 2, RING["step_ring"])))
        rb_in, rb_out = R + w / 2 + gap, R + w / 2 + gap + 0.5
        bus = kdb.Polygon(q(ring_pts(cx, cy, rb_out, RING["step_bus"], 225, 315) +
                            ring_pts(cx, cy, rb_in, RING["step_bus"], 225, 315)[::-1]))
        reg = kdb.Region([ring, bus])
        res = {}
        for tol in (0, 2, 5):
            ep = reg.isolated_check(int(round((gap - tol * 1e-3) / DBU)), False, kdb.Metrics.Euclidian, 90)
            res[f"tol{tol}"] = ep.count()
        dmin = min(e.distance() for e in reg.isolated_check(int(round((gap + 0.01) / DBU)), False, kdb.Metrics.Euclidian, 90).each())
        res["min_gap_nm"] = dmin * DBU * 1000
        res["off_grid"] = reg.grid_check(int(round(GRID / DBU)), int(round(GRID / DBU))).count()
        res["vertices"] = ring.num_points() + bus.num_points()
        out[name] = res
        print(name, res)
    with open(os.path.join(HERE, "ch34_pulley.json"), "w") as f:
        json.dump(out, f, indent=0)


def engine():
    """Two ways a DRC engine finds a narrow neck (edge pairs and sizing), and the Euclidean and projection
    metrics of a space check, on small shapes -> figsrc/ch34_engine.json."""
    import klayout.db as kdb
    um = lambda v: int(round(v / DBU))
    bone = kdb.Region(kdb.Polygon([kdb.Point(um(x), um(y)) for x, y in
                                   [(0, 0), (1, 0), (1, 0.44), (2, 0.44), (2, 0), (3, 0), (3, 1), (2, 1), (2, 0.56),
                                    (1, 0.56), (1, 1), (0, 1)]]))
    ep = bone.width_check(um(0.15), False, kdb.Metrics.Euclidian, 90)
    shrunk = bone.sized(-um(0.075))
    opened = shrunk.sized(um(0.075))
    narrow = bone - opened
    a = kdb.Region(kdb.Box(um(0), um(0), um(1.0), um(0.5)))
    b = kdb.Region(kdb.Box(um(1.1), um(0.6), um(2.1), um(1.1)))
    c = kdb.Region(kdb.Box(um(0), um(-0.65), um(1.0), um(-0.15)))
    pair = a + b + c
    eu = pair.space_check(um(0.2), False, kdb.Metrics.Euclidian, 90)
    pr = pair.space_check(um(0.2), False, kdb.Metrics.Projection, 90)

    def polys(r):
        return [[(q.x * DBU, q.y * DBU) for q in p.each_point_hull()] for p in r.each()]

    def eps(e):
        return [[(x.first.p1.x * DBU, x.first.p1.y * DBU, x.first.p2.x * DBU, x.first.p2.y * DBU),
                 (x.second.p1.x * DBU, x.second.p1.y * DBU, x.second.p2.x * DBU, x.second.p2.y * DBU)] for x in e.each()]
    out = dict(bone=polys(bone), width_pairs=eps(ep), shrunk=polys(shrunk), opened=polys(opened), narrow=polys(narrow),
               rects=polys(pair), space_euclid=eps(eu), space_proj=eps(pr))
    print("width pairs", ep.count(), "narrow area um2", narrow.area() * DBU ** 2, "euclid", eu.count(), "projection", pr.count())
    with open(os.path.join(HERE, "ch34_engine.json"), "w") as f:
        json.dump(out, f, indent=0)


# ---------------------------------------------------------------- parse the report database
NUM = r"-?\d+(?:\.\d+)?(?:e-?\d+)?"


def parse():
    import xml.etree.ElementTree as ET
    root = ET.parse(RDB).getroot()
    cats = {}
    for c in root.iter("category"):
        nm = c.findtext("name"); ds = c.findtext("description") or ""
        if nm: cats[nm.strip("'")] = dict(description=ds, markers=[])
    for it in root.iter("item"):
        cat = (it.findtext("category") or "").strip("'")
        for v in it.iter("value"):
            s = (v.text or "").strip()
            kind = s.split(":")[0]
            nums = [float(t) for t in re.findall(NUM, s.split(":", 1)[1])] if ":" in s else []
            cats.setdefault(cat, dict(description="", markers=[]))["markers"].append(dict(kind=kind, xy=nums))
    for k, v in cats.items():
        print(f"{k:10s} {len(v['markers']):4d}  {v['description']}")
    with open(OUT, "w") as f:
        json.dump(cats, f, indent=0)
    print("wrote", OUT)


if __name__ == "__main__":
    {"make": make, "check": check, "parse": parse, "pulley": pulley, "engine": engine}[sys.argv[1] if len(sys.argv) > 1 else "make"]()
