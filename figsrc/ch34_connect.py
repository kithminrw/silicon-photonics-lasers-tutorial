"""ch34_connect.py -- connectivity checking with SiEPIC-Tools, for Chapter 34.

Builds a small MZI test circuit (two grating couplers 127 um apart, two Y-branches, two arms) with the SiEPIC EBeam
PDK, then makes three copies, each with one mistake, and runs SiEPIC-Tools' layout_check on all four:

  good     the circuit as routed
  nudge    the second Y-branch moved 50 nm after routing (its pins no longer meet the waveguides)
  width    the input waveguide routed with a 350 nm (1310 nm) waveguide type instead of 500 nm
  overlap  a stray Y-branch dropped on the long arm

It writes figsrc/ch34_connect.json: per variant the silicon polygons, the components' DevRec boxes, their pins, the
extracted netlist and the errors reported. Run in the photonics-labs container (KLayout 0.30.13, SiEPIC 0.5.31,
siepic_ebeam_pdk 0.4.53):

  python ch34_connect.py
"""
import json
import os

import pya
import siepic_ebeam_pdk  # noqa: F401  (registers the EBeam technology)
import SiEPIC
from SiEPIC.scripts import connect_cell, connect_pins_with_waveguide
from SiEPIC.utils.layout import new_layout, floorplan
from SiEPIC.verification import layout_check

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ch34_connect.json")
TMP = os.environ.get("CH34_TMP", "/tmp")
WG = "Strip TE 1550 nm, w=500 nm"
WG_WRONG = "Strip TE 1310 nm, w=350 nm"


def build(variant):
    cell, ly = new_layout("EBeam", "CH34_MZI", GUI=False, overwrite=True)
    floorplan(cell, 220e3, 200e3)
    gc = ly.create_cell2("GC_TE_1550_8degOxide_BB", "EBeam")
    yb = ly.create_cell2("ebeam_y_1550", "EBeam")
    x0, y0 = 30000, 30000                                    # database units (1 nm)
    g1 = cell.insert(pya.CellInstArray(gc.cell_index(), pya.Trans(pya.Trans.R0, x0, y0)))
    g2 = cell.insert(pya.CellInstArray(gc.cell_index(), pya.Trans(pya.Trans.R0, x0, y0 + 127000)))
    t = pya.Trans(pya.Trans.R0, x0, y0 + 127000)
    cell.shapes(ly.layer(ly.TECHNOLOGY["Text"])).insert(pya.Text("opt_in_TE_1550_device_ch34_MZI1", t))
    y1 = connect_cell(g1, "opt1", yb, "opt1"); y1.transform(pya.Trans(20000, 0))
    y2 = connect_cell(g2, "opt1", yb, "opt1"); y2.transform(pya.Trans(20000, 0))
    connect_pins_with_waveguide(g1, "opt1", y1, "opt1", waveguide_type=WG_WRONG if variant == "width" else WG)
    connect_pins_with_waveguide(g2, "opt1", y2, "opt1", waveguide_type=WG)
    connect_pins_with_waveguide(y1, "opt2", y2, "opt3", waveguide_type=WG)
    connect_pins_with_waveguide(y1, "opt3", y2, "opt2", waveguide_type=WG, turtle_B=[40, -90])
    if variant == "nudge":
        y2.transform(pya.Trans(0, 50))                         # 50 nm, after routing
    if variant == "overlap":
        cell.insert(pya.CellInstArray(yb.cell_index(), pya.Trans(pya.Trans.R0, 104000, 95000)))
    return cell, ly


def polys(cell, ly, layer):
    li = ly.layer(ly.TECHNOLOGY[layer])
    r = pya.Region(cell.begin_shapes_rec(li)).merged()
    out = []
    for p in r.each():
        # (integer coordinates scaled here: to_dtype on a polygon with properties drops its holes in 0.30.13)
        f = ly.dbu
        out.append(dict(hull=[(round(q.x * f, 3), round(q.y * f, 3)) for q in p.each_point_hull()],
                        holes=[[(round(q.x * f, 3), round(q.y * f, 3)) for q in p.each_point_hole(h)] for h in range(p.holes())]))
    return out


def run(variant):
    cell, ly = build(variant)
    si_polys = polys(cell, ly, "Si")          # before the checks, which may change the layout
    # the EBeam PDK deck's silicon width and space rules (60 and 70 nm, tested 2 nm below, angle limit 80 deg),
    # on everything except the grating couplers (black boxes the foundry replaces)
    li = ly.layer(ly.TECHNOLOGY["Si"])
    it = cell.begin_shapes_rec(li)
    it.unselect_cells([c.cell_index() for c in ly.each_cell() if c.name.startswith("GC_")])
    si = pya.Region(it)
    drc = dict(width=si.width_check(58, False, pya.Metrics.Euclidian, 80).count(),
               space=si.space_check(68, False, pya.Metrics.Euclidian, 80).count())
    nets, comps = cell.identify_nets()
    rdbfile = os.path.join(TMP, f"ch34_{variant}.lyrdb")
    n_err = layout_check(cell=cell, verbose=False, GUI=True, file_rdb=rdbfile)
    # the report: category -> list of marker bounding boxes (um)
    rdb = pya.ReportDatabase("x"); rdb.load(rdbfile)
    errs = {}
    for it in rdb.each_item():
        cat = rdb.category_by_id(it.category_id()).path()
        boxes, notes = [], []
        for v in it.each_value():
            if v.is_string():
                notes.append(v.string())
                continue
            for test, get in (("is_polygon", "polygon"), ("is_path", "path"), ("is_box", "box"),
                              ("is_edge_pair", "edge_pair"), ("is_edge", "edge")):
                if getattr(v, test)():
                    b = getattr(v, get)().bbox()
                    boxes.append((b.left, b.bottom, b.right, b.top))
                    break
        errs.setdefault(cat, []).append(dict(boxes=boxes, notes=notes))
    comp_list = []
    for c in comps:
        b = c.polygon.bbox().to_dtype(ly.dbu) if c.polygon else None
        pins = []
        for p in c.pins:
            if p.path is None:
                continue
            pts = p.path.to_dtype(ly.dbu).each_point()
            pts = [(q.x, q.y) for q in pts]
            pins.append(dict(name=p.pin_name, pts=pts, width=p.path.width * ly.dbu,
                             net=None if p.net is None or p.net.idx is None else p.net.idx))
        dev = [(round(q.x, 3), round(q.y, 3)) for q in c.polygon.to_dtype(ly.dbu).each_point_hull()] if c.polygon else []
        comp_list.append(dict(idx=c.idx, name=c.basic_name, box=None if b is None else (b.left, b.bottom, b.right, b.top),
                              devrec=dev, pins=pins, params=c.params))
    netlist = []
    for n in nets:
        if n.idx is None:
            continue
        netlist.append([f"{p.component.basic_name}#{p.component.idx}.{p.pin_name}" for p in n.pins])
    res = dict(variant=variant, n_errors=n_err, errors={k: len(v) for k, v in errs.items()}, error_boxes=errs,
               n_components=len(comps), n_nets=len(netlist), netlist=netlist, components=comp_list,
               si=si_polys, drc=drc)
    print(f"{variant:8s} components {len(comps):2d}  nets {len(netlist):2d}  errors {n_err}  {res['errors']}  DRC {drc}")
    return res


if __name__ == "__main__":
    print("SiEPIC", SiEPIC.__version__, "klayout", pya.__version__ if hasattr(pya, "__version__") else "")
    out = {v: run(v) for v in ("good", "nudge", "width", "overlap")}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=0)
    print("wrote", OUT)
