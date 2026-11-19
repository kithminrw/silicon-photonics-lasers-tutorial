"""Lab 8: check your first chip before you submit it to openEBL (Open-Photonics, Chapter 30).

Run it from a terminal, in the folder where you saved lab07_layout.py:
    python lab08_checks.py                   # checks EBeam_YourName_firstchip.gds; makes it with Lab 7 if it is missing
    python lab08_checks.py mychip.gds        # checks any GDS or OASIS file
    python lab08_checks.py --break gap       # breaks the Lab 7 chip on purpose and checks it:
                                             #   gap, label, overlap, outside, or all
    python lab08_checks.py --siepic          # also runs SiEPIC-Tools' own verification, as openEBL's GitHub Action does
    python lab08_checks.py --no-plot         # numbers only

The checks need only KLayout's Python module (it comes with gdsfactory; or pip install klayout). Making the chip
needs Lab 7's gdsfactory and ubcpdk; --siepic needs pip install SiEPIC siepic_ebeam_pdk. Lengths are in micrometres.
The lab page explains each check and where its rule comes from: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-08/
"""
import math
import os
import re
import sys
import time

import klayout.db as kdb

# ---------------------------------------------------------------------------------------------------------
# The rules, with their sources (the lab page links each one)
# ---------------------------------------------------------------------------------------------------------
FLOORPLAN = (605.0, 410.0)  # siepic.ca/openebl; run_submission_checks.py: cell_Width 605000, cell_Height 410000
EXTENT_LAYERS = [(1, 0), (4, 0)]                    # run_submission_checks.py: layers whose extent is measured
SI, TEXT, FP, DEVREC = (1, 0), (10, 0), (99, 0), (68, 0)
# Layers of the openEBL passive run (README layer table), plus the two the PDK's couplers carry inside them
ALLOWED_LAYERS = {(1, 0): "Si", (99, 0): "FloorPlan", (10, 0): "Text", (68, 0): "DevRec", (1, 10): "PinRec",
                  (1, 99): "Waveguide", (200, 0): "SEM", (81, 0): "FbrTgt (inside the couplers)",
                  (998, 0): "BlackBox (inside the couplers)"}
MIN_WIDTH, MIN_SPACE, TOL = 0.060, 0.070, 0.002     # SiEPIC_EBeam_DRC.lydrc: width(0.06 - tol), space(0.07 - tol)
ANGLE_LIMIT = 80                                    # ... angle_limit(80)
# DFT.xml of the SiEPIC EBeam PDK
GC_CELLS = ("ebeam_gc_te1550", "ebeam_gc_tm1550", "GC_TE_1550_8degOxide_BB", "GC_TM_1550_8degOxide_BB",
            "GC_TE_1310_8degOxide_BB", "GC_TM_1310_8degOxide_BB")
GC_ORIENTATION = 0          # gc-orientation: the couplers are never rotated
GC_PITCH = 127.0            # gc-pitch
GC_ARRAY_ANGLE = 90         # gc-array-orientation: the couplers of a circuit form a vertical column
GC_ABOVE, GC_BELOW = 1, 2   # detectors-above-laser, detectors-below-laser
GC_MIN_SPACING = 60.0       # minimum-gc-spacing
LABEL_MAX_DISTANCE = 10.0   # opt_in max-distance-to-grating-coupler
LASERS = {("TE", 1550), ("TM", 1550), ("TE", 1310), ("TM", 1310)}   # tunable-laser entries
LABEL_RE = re.compile(r"^opt_in_(?P<pol>[A-Z]+)_(?P<wl>\d+)_(?P<type>[A-Za-z0-9]+)_(?P<id>[A-Za-z0-9]+)_(?P<name>\S+)$")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GDS = "EBeam_YourName_firstchip.gds"
BREAKS = {  # what --break does to the Lab 7 chip (keyword arguments of lab07_layout.build_chip)
    "gap": dict(ring_gaps=(0.05, 0.25, 0.30)),                  # ring200's gap shrunk to 50 nm
    "label": dict(move_label=("ring250", 0.0, -15.0)),          # a label 15 um below its coupler
    "overlap": dict(move_device=("spiral2", -60.0, 0.0)),       # spiral2 pushed into the MZI
    "outside": dict(move_device=("spiral3", 40.0, 0.0)),        # spiral3 pushed past the right edge
}
BREAKS["all"] = {**BREAKS["gap"], **BREAKS["label"], **BREAKS["outside"]}


class Report:
    """Collects PASS/FAIL lines and the places that failed (for the figure)."""

    def __init__(self):
        self.results, self.markers = [], []

    def check(self, name, ok, detail, where=(), tag=None):
        self.results.append((name, ok))
        print(f"   [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        if not ok:
            self.markers.extend((tag or name.strip(), xy) for xy in where)
        return ok


# ---------------------------------------------------------------------------------------------------------
# Reading the layout
# ---------------------------------------------------------------------------------------------------------
def region(cell, layer, skip_cells=()):
    """Every shape of `layer` under `cell`, flattened and merged, optionally skipping some cells (by name)."""
    ly = cell.layout()
    li = ly.find_layer(*layer)
    if li is None:
        return kdb.Region()
    it = cell.begin_shapes_rec(li)
    if skip_cells:
        it.unselect_cells([ly.cell(n).cell_index() for n in skip_cells if ly.has_cell(n)])
    return kdb.Region(it)


def layers_used(top):
    """Every layer with at least one shape (polygon, path, box or text) under the top cell."""
    ly = top.layout()
    return sorted((ly.get_info(li).layer, ly.get_info(li).datatype) for li in ly.layer_indexes()
                  if not top.begin_shapes_rec(li).at_end())


def is_gc(cell_name):
    return cell_name.startswith(GC_CELLS)


def find_gcs(top):
    """Every grating coupler instance: (device, cell name, x, y, rotation in degrees, mirrored)."""
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


def find_labels(top):
    """Every text on the Text layer that starts with opt_, at its position in the top cell."""
    ly = top.layout()
    li = ly.find_layer(*TEXT)
    out = []
    if li is None:
        return out
    it = top.begin_shapes_rec(li)
    while not it.at_end():
        if it.shape().is_text() and it.shape().text_string.startswith("opt_"):
            p = it.dtrans() * it.shape().dtext.trans.disp
            out.append(dict(text=it.shape().text_string, x=p.x, y=p.y))
        it.next()
    return out


# ---------------------------------------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------------------------------------
def check_layout(path):
    ly = kdb.Layout()
    ly.read(path)
    dbu = ly.dbu
    rep = Report()
    tops = ly.top_cells()
    top = tops[0]
    print(f"Checking {os.path.basename(path)}\n")

    # ---- A. File, top cell, floorplan and layers (run_submission_checks.py, the DRC deck)
    print("A. Top cell, floorplan and layers")
    rep.check("one top cell", len(tops) == 1, ", ".join(c.name for c in tops))
    stem = os.path.splitext(os.path.basename(path))[0]
    rep.check("top cell named after the file (convention)", top.name == stem, f"{top.name} in {stem}.gds")
    ext = kdb.Region()
    for layer in EXTENT_LAYERS:
        ext += region(top, layer)
    bb = ext.bbox().to_dtype(dbu)
    rep.check("extent of 1/0 and 4/0 within 605 x 410 um", bb.width() <= FLOORPLAN[0] and bb.height() <= FLOORPLAN[1],
              f"{bb.width():.1f} x {bb.height():.1f} um")
    fp = region(top, FP)
    fpb = fp.bbox().to_dtype(dbu)
    rep.check("floorplan box on 99/0", not fp.is_empty() and abs(fpb.width() - FLOORPLAN[0]) < 1e-3
              and abs(fpb.height() - FLOORPLAN[1]) < 1e-3, f"{fpb.width():.1f} x {fpb.height():.1f} um at"
              f" ({fpb.left:.1f}, {fpb.bottom:.1f})")
    outside = region(top, SI) - fp
    rep.check("all silicon inside the floorplan", outside.is_empty(),
              "none outside" if outside.is_empty() else f"{outside.count()} piece(s) outside, x up to"
              f" {outside.bbox().to_dtype(dbu).right:.1f} um", [(b.center().x, b.center().y) for b in
                                                                   (p.bbox().to_dtype(dbu) for p in outside.each())],
              "outside the floorplan")
    used = layers_used(top)
    bad = [l for l in used if l not in ALLOWED_LAYERS]
    rep.check("only allowed layers", not bad, "uses " + ", ".join(f"{a}/{b}" for a, b in used)
              + (f"; not allowed: {', '.join(f'{a}/{b}' for a, b in bad)}" if bad else ""))
    gc_names = sorted({c.name for c in ly.each_cell() if is_gc(c.name)})
    renamed = sorted(c.name for c in ly.each_cell() if any(c.name.startswith(g + "$") for g in GC_CELLS))
    rep.check("black-box couplers keep their PDK names", not renamed and bool(gc_names),
              ", ".join(gc_names) + (f"; renamed: {', '.join(renamed)}" if renamed else ""))
    print()

    # ---- B. Minimum width and space of the silicon (SiEPIC_EBeam_DRC.lydrc), black boxes skipped
    print("B. Minimum width and space of silicon (black-box couplers skipped: the foundry replaces them)")
    si = region(top, SI, skip_cells=gc_names)
    w = si.width_check(round((MIN_WIDTH - TOL) / dbu), False, kdb.Metrics.Euclidian, ANGLE_LIMIT)
    s = si.space_check(round((MIN_SPACE - TOL) / dbu), False, kdb.Metrics.Euclidian, ANGLE_LIMIT)
    centre = lambda ep: ((ep.first.p1.x + ep.second.p2.x) / 2 * dbu, (ep.first.p1.y + ep.second.p2.y) / 2 * dbu)
    rep.check("width >= 60 nm", w.is_empty(), f"{w.count()} violation(s)", [centre(e) for e in w.each()], "width")
    rep.check("space >= 70 nm", s.is_empty(), f"{s.count()} violation(s)" + (
              ", narrowest " + ", ".join(sorted({f"{e.distance() * dbu * 1e3:.0f} nm" for e in s.each()}))
              if not s.is_empty() else ""), [centre(e) for e in s.each()], "space < 70 nm")
    gaps = []
    for inst in top.each_inst():                     # the narrowest gap inside each device, for information
        sp = region(inst.cell, SI, skip_cells=gc_names).space_check(round(0.5 / dbu), False, kdb.Metrics.Euclidian,
                                                                    ANGLE_LIMIT)
        if not sp.is_empty():
            gaps.append(f"{inst.cell.name} {min(e.distance() for e in sp.each()) * dbu * 1e3:.0f} nm")
    print(f"   narrowest gaps under 500 nm: {', '.join(gaps) or 'none'}")
    print()

    # ---- C. Grating couplers (DFT.xml)
    print("C. Grating couplers (design-for-test rules)")
    gcs = find_gcs(top)
    devices = {}
    for g in gcs:
        devices.setdefault(g["device"], []).append(g)
    rep.check("grating couplers found", bool(gcs), f"{len(gcs)} in {len(devices)} devices")
    wrong = [g for g in gcs if round(g["angle"]) % 360 != GC_ORIENTATION or g["mirror"]]
    rep.check("all couplers unrotated", not wrong, f"{len(wrong)} rotated or mirrored", [(g["x"], g["y"]) for g in wrong],
              "rotated coupler")
    close = [(a, b) for i, a in enumerate(gcs) for b in gcs[i + 1:]
             if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < GC_MIN_SPACING]
    dmin = min(math.hypot(a["x"] - b["x"], a["y"] - b["y"]) for i, a in enumerate(gcs) for b in gcs[i + 1:])
    rep.check("couplers at least 60 um apart", not close, f"closest pair {dmin:.1f} um apart",
              [(a["x"], a["y"]) for a, b in close], "couplers too close")
    print()

    # ---- D. Labels (DFT.xml and SiEPIC-Tools' label format)
    print("D. opt_in labels")
    labels = find_labels(top)
    rep.check("labels found", bool(labels), f"{len(labels)} on layer 10/0")
    names = [l["text"] for l in labels]
    dup = sorted({n for n in names if names.count(n) > 1})
    rep.check("labels unique", not dup, "all different" if not dup else "repeated: " + ", ".join(dup))
    labelled = {}
    for l in labels:
        m = LABEL_RE.match(l["text"])
        ok = bool(m) and (m["pol"], int(m["wl"])) in LASERS and m["type"] == "device"
        g = min(gcs, key=lambda g: math.hypot(g["x"] - l["x"], g["y"] - l["y"]))
        dist = math.hypot(g["x"] - l["x"], g["y"] - l["y"])
        near = dist <= LABEL_MAX_DISTANCE
        print(f"   {l['text']:<42} ({l['x']:6.1f}, {l['y']:6.1f})  nearest coupler {dist:5.1f} um, in {g['device']}")
        rep.check("  format opt_in_<TE|TM>_<1550|1310>_device_<you>_<name>", ok,
                  f"{m['pol']} {m['wl']} nm, device ID {m['id']}, name {m['name']}" if m else "not parsed")
        rep.check("  on a coupler (<= 10 um)", near, f"{dist:.1f} um from {g['device']}'s coupler",
                  [] if near else [(l["x"], l["y"])], "label off its coupler")
        if near:
            labelled.setdefault(g["device"], []).append((l, g))
            col = devices[g["device"]]
            others = [h for h in col if h is not g]
            steps = [(h["x"] - g["x"], (h["y"] - g["y"]) / GC_PITCH) for h in others]
            ok_col = all(abs(dx) < 1e-3 and abs(k - round(k)) < 1e-5 and -GC_BELOW <= round(k) <= GC_ABOVE
                         and round(k) != 0 for dx, k in steps)
            rep.check("  its circuit's couplers on the fibre array", ok_col, "others at "
                      + ", ".join(f"{k:+.3f} x 127 um" for _, k in steps) + " (allowed: +1, -1, -2)",
                      [(h["x"], h["y"]) for h in others], "coupler off the array")
    missing = [d for d in devices if d not in labelled]
    rep.check("every device has a label", not missing, "all labelled" if not missing else "missing: " + ", ".join(missing),
              [max(((g["x"], g["y"]) for g in devices[d]), key=lambda p: p[1]) for d in missing], "no label")
    print()

    # ---- E. Devices do not overlap (DevRec, as SiEPIC-Tools checks components)
    print("E. Overlaps")
    recs = {inst.cell.name: region(inst.cell, DEVREC).transformed(inst.cplx_trans) for inst in top.each_inst()
            if not inst.cell.name.startswith("FloorPlan")}
    hits = []
    for i, a in enumerate(recs):
        for b in list(recs)[i + 1:]:
            ov = recs[a] & recs[b]
            if not ov.is_empty():
                c = ov.bbox().to_dtype(dbu).center()
                hits.append((a, b, (c.x, c.y)))
    rep.check("devices do not overlap", not hits, f"{len(recs)} devices" + (
              "; overlapping: " + ", ".join(f"{a} and {b}" for a, b, _ in hits) if hits else ""), [h[2] for h in hits],
              "overlap")
    print()
    n_fail = sum(not ok for _, ok in rep.results)
    print(f"Summary: {len(rep.results) - n_fail} checks passed, {n_fail} failed\n")
    return rep, ly


# ---------------------------------------------------------------------------------------------------------
# SiEPIC-Tools' own verification, as openEBL's run_verification.py calls it
# ---------------------------------------------------------------------------------------------------------
def run_siepic(path):
    try:
        import SiEPIC  # noqa: F401
        import siepic_ebeam_pdk  # noqa: F401  (registers the EBeam technology)
        from SiEPIC.utils import get_technology_by_name
        from SiEPIC.verification import layout_check
    except ImportError:
        print("F. SiEPIC-Tools verification skipped: pip install SiEPIC siepic_ebeam_pdk\n")
        return None
    print("F. SiEPIC-Tools functional verification (layout_check, as in openEBL's run_verification.py)")
    t0 = time.time()
    ly = kdb.Layout()
    ly.read(path)
    ly.TECHNOLOGY = get_technology_by_name("EBeam")
    rdb = os.path.splitext(os.path.basename(path))[0] + ".lyrdb"
    nets, comps = ly.top_cell().identify_nets()      # the netlist the checks walk along
    print(f"   netlist: {len(comps)} components, {len(nets)} connections")
    n = layout_check(cell=ly.top_cell(), verbose=False, GUI=True, file_rdb=rdb)
    import klayout.rdb
    db = klayout.rdb.ReportDatabase("")
    db.load(rdb)
    counts = {}
    for item in db.each_item():
        cat = db.category_by_id(item.category_id())
        name = cat.path()
        counts[name] = counts.get(name, 0) + 1
    from importlib.metadata import version
    print(f"   SiEPIC {version('SiEPIC')}, siepic_ebeam_pdk {version('siepic_ebeam_pdk')}: {n} error(s)"
          f" in {time.time() - t0:.0f} s; report {rdb}")
    for name, k in sorted(counts.items()):
        print(f"     {name}: {k}")
    print()
    return n


# ---------------------------------------------------------------------------------------------------------
def make_chip(breaks=None):
    """Build the Lab 7 chip (broken on purpose if `breaks` is given) and write it; returns the GDS path."""
    sys.path.insert(0, HERE)
    sys.dont_write_bytecode = True                  # no __pycache__ beside the scripts
    import lab07_layout as lab7
    if breaks:
        name = f"{lab7.TOP_NAME}_broken"
        chip, _ = lab7.build_chip(top_name=name, suffix="_b", **breaks)
    else:
        chip, _ = lab7.build_chip()
    return str(lab7.write_gds(chip))


def draw(results):
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Rectangle

    fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 4.6), squeeze=False)
    for ax, (title, path, rep, ly) in zip(axes[0], results):
        top = ly.top_cell()
        dbu = ly.dbu
        polys = [[(p.x * dbu, p.y * dbu) for p in poly.each_point_hull()] for poly in region(top, SI).each()]
        ax.add_collection(PolyCollection(polys, facecolor="0.55", edgecolor="0.55", linewidth=0.3))
        ax.add_patch(Rectangle((0, 0), *FLOORPLAN, fill=False, ec="k", lw=1.0, ls="--"))
        gcs = find_gcs(top)
        for l in find_labels(top):
            g = min(gcs, key=lambda g: math.hypot(g["x"] - l["x"], g["y"] - l["y"]))
            ok = math.hypot(g["x"] - l["x"], g["y"] - l["y"]) <= LABEL_MAX_DISTANCE
            ax.plot([l["x"]], [l["y"]], "o", ms=5, color="tab:green" if ok else "tab:red", zorder=3)
            if not ok:
                ax.plot([l["x"], g["x"]], [l["y"], g["y"]], color="tab:red", lw=1)
        for g in gcs:
            ax.plot([g["x"]], [g["y"]], marker=">", ms=4, color="tab:blue", zorder=3)
        shown = []
        for name, (x, y) in rep.markers:
            if any(n == name and math.hypot(x - a, y - b) < 20 for n, (a, b) in shown):
                continue                             # one marker per place
            shown.append((name, (x, y)))
            ax.plot([x], [y], marker="o", ms=16, mfc="none", mec="tab:red", mew=1.6, zorder=4)
            dxy = {"no label": (11, 5), "label off its coupler": (11, -12), "space < 70 nm": (11, -15)}.get(name, (9, 7))
            ax.annotate(name.strip(), (x, y), xytext=dxy, textcoords="offset points", fontsize=7.5,
                        color="tab:red")
        n_fail = sum(not ok for _, ok in rep.results)
        ax.set(xlim=(-10, FLOORPLAN[0] + 60), ylim=(-10, FLOORPLAN[1] + 10), aspect="equal", xlabel="x (µm)",
               ylabel="y (µm)",
               title=f"{title}: {len(rep.results) - n_fail} checks passed, {n_fail} failed")
    ax.plot([], [], ">", color="tab:blue", ms=4, label="grating coupler port")
    ax.plot([], [], "o", color="tab:green", ms=5, label="opt_in label on a coupler")
    ax.plot([], [], "o", color="tab:red", ms=5, label="label off its coupler")
    ax.plot([], [], "o", ms=10, mfc="none", mec="tab:red", label="failed check")
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig("lab08_checks.png", dpi=150)
    print("Saved the figure as lab08_checks.png")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    breaks = sys.argv[sys.argv.index("--break") + 1] if "--break" in sys.argv else None
    if breaks:
        args = [a for a in args if a != breaks]
    print("Lab 8: pre-flight checks for an openEBL submission\n")
    results = []
    if breaks:
        if breaks not in BREAKS:
            sys.exit(f"--break takes one of {', '.join(BREAKS)}")
        print(f"Breaking the Lab 7 chip on purpose: {breaks} -> {BREAKS[breaks]}")
        path = make_chip(BREAKS[breaks])
        title = f"(b) broken: {breaks}"
    else:
        path = args[0] if args else DEFAULT_GDS
        if not os.path.exists(path):
            print(f"{path} not found: making it with lab07_layout.py")
            path = make_chip()
        title = "(a) the Lab 7 chip"
    rep, ly = check_layout(path)
    results.append((title, path, rep, ly))
    plot = "--no-plot" not in sys.argv
    if plot and not breaks:                          # the figure shows the chip and the all-broken version
        print("For the figure, the same checks on a broken copy (--break all):\n")
        bpath = make_chip(BREAKS["all"])
        brep, bly = check_layout(bpath)
        results.append(("(b) broken: label, gap, outside", bpath, brep, bly))
    if "--siepic" in sys.argv:                       # last: SiEPIC-Tools adds KLayout libraries of its own
        run_siepic(path)
    if plot:
        draw(results)


if __name__ == "__main__":
    main()
