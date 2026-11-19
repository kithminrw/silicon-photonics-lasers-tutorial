# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 7: lay out your first chip (Open-Photonics, Chapter 30).

Run it from a terminal:
    python lab07_layout.py              # prints every checkpoint, writes the GDS and lab07_layout.png
    python lab07_layout.py --no-plot    # GDS and numbers only
    python lab07_layout.py --show       # also sends the chip to a running KLayout (klive), if there is one

It needs gdsfactory 9 and ubcpdk 3 (the SiEPIC EBeam PDK for gdsfactory), and Matplotlib for the figure:
    pip install "gdsfactory==9.51.0" "ubcpdk==3.3.5" matplotlib
Lengths are in micrometres. Change USER below to your own name (letters and digits only) before you submit.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-07/
"""
import math
import sys

import gdsfactory as gf
import klayout.db as kdb
from ubcpdk import PDK
from ubcpdk.config import PATH as UBC_PATH
from ubcpdk.import_gds import import_gds

PDK.activate()

USER = "YourName"           # your edX or GitHub name: it goes into every label and the file name
PREFIX = "EBeam"            # openEBL file-name prefix: EBeam_ (edX), ELEC413_, SiEPIC_Passives_ or openEBL_
TOP_NAME = f"{PREFIX}_{USER}_firstchip"

# ---------------------------------------------------------------------------------------------------------
# Part A. The openEBL rules this layout follows (sources on the lab page)
# ---------------------------------------------------------------------------------------------------------
FLOORPLAN = (605.0, 410.0)  # design area, um (siepic.ca/openebl; run_submission_checks.py: 605000 x 410000 dbu)
LAYER_SI = (1, 0)           # silicon, full 220 nm etch
LAYER_TEXT = (10, 0)        # text labels for automated measurement
LAYER_FLOORPLAN = (99, 0)   # marks the design area
GC = "ebeam_gc_te1550"      # the PDK's TE grating coupler, a black-box cell: never rename, edit or rotate it
GC_PITCH = 127.0            # fibre-array pitch (DFT.xml: gc-pitch 127)
XS = "strip"                # 500 x 220 nm strip, 10 um bend radius (Euler bends)

# The circuit (Chapters 6, 11, 12 and 7)
LAM, NG = 1.55, 4.18        # um; TE0 group index of the 500 x 220 nm strip (Chapter 6, femwell)
MZI_DL = 100.0              # MZI arm-length difference: FSR = lam^2 / (n_g dL) = 5.75 nm (Chapter 11)
RING_R = 10.0               # ring radius (Table 12.1)
RING_GAPS = (0.20, 0.25, 0.30)
SPIRALS = {"spiral1": (6, 20.0), "spiral2": (10, 50.0), "spiral3": (14, 60.0)}   # name: (loops, straight um)
SPIRAL_PITCH = 2.0          # centre-to-centre spacing of neighbouring spiral turns

# Floorplan: four columns of grating couplers, two devices (four couplers) per column
COLUMNS = [("loopback", "ring200"), ("ring250", "ring300"), ("mzi", "spiral1"), ("spiral2", "spiral3")]
Y_PAIRS = (20.0, 263.0)     # y of the lower coupler of the bottom and of the top device in each column
X_FIRST = 45.0              # x of the first column's coupler ports (each coupler reaches 40 um to the left)
COLUMN_GAP = 45.0           # from the right edge of one column's devices to the next column's coupler ports
LAYER_DEVREC = (68, 0)      # device recognition: SiEPIC-Tools finds a component by its DevRec shape...
LAYER_PINREC = (1, 10)      # ... and its connections by PinRec pins at its ports


def um(route):
    """Length of a gdsfactory route in um (routes count their length in database units of 1 nm)."""
    return route.length * gf.kcl.dbu


def siepic(component):
    """One flat SiEPIC component: its silicon, one DevRec polygon and a PinRec pin at every port.

    SiEPIC-Tools (and openEBL's verification) trace a circuit from pin to pin. gdsfactory's routed straights
    and bends, and the parts inside its rings and spirals, carry no pins, so without this the netlist is empty.
    """
    c = gf.Component()
    ref = c << component
    c.add_ports(ref.ports)
    c.flatten()
    li = c.kcl.layer(*LAYER_DEVREC)
    devrec = kdb.Region(c.shapes(li)).merged()
    if devrec.count() > 1 or sum(p.num_points() for p in devrec.each()) > 4000:
        devrec = kdb.Region(devrec.bbox())          # one DevRec polygon, small enough for GDS: else the bbox
    c.shapes(li).clear()
    c.shapes(li).insert(devrec)
    pins = c.kcl.layer(*LAYER_PINREC)
    for i, p in enumerate(c.ports):                 # a 20 nm path across the port, pointing out, as SiEPIC draws it
        (x, y), a = p.dcenter, math.radians(p.orientation)
        dx, dy = 0.01 * math.cos(a), 0.01 * math.sin(a)
        c.shapes(pins).insert(kdb.DPath([kdb.DPoint(x - dx, y - dy), kdb.DPoint(x + dx, y + dy)], p.width))
        c.shapes(pins).insert(kdb.DText(f"opt{i + 1}", kdb.DTrans(x, y)))
    for k, v in component.info.model_dump().items():   # keep length, radius, ... for the router
        c.info[k] = v
    return c


def pdk_cell(name):
    """A fixed cell of the EBeam PDK, as in its GDS file. (ubcpdk's own version turns the PinRec paths into
    boxes, and SiEPIC-Tools only recognises pins drawn as paths.)"""
    return import_gds(UBC_PATH.gds_ebeam / f"{name}.gds", convert_paths_to_polygons=False)


@gf.cell
def straight_pins(**kw):
    return siepic(gf.c.straight(**kw))


@gf.cell
def bend_pins(**kw):
    return siepic(gf.c.bend_euler(**kw))


# ---------------------------------------------------------------------------------------------------------
# Part B. Two couplers on the fibre-array pitch, and the loopback (Chapters 15 and 17)
# ---------------------------------------------------------------------------------------------------------
def coupler_pair(name):
    """A device cell with two couplers 127 um apart, facing east: input (upper) at (0, 127), output at (0, 0)."""
    c = gf.Component(name)
    gc_out = c << pdk_cell(GC)
    gc_in = c << pdk_cell(GC)
    gc_in.dmove((0, GC_PITCH))
    c.info["routes"] = []                          # (what, length in um) of every routed waveguide
    return c, gc_in, gc_out


def route(c, p1, p2, what, **kw):
    r = gf.routing.route_single(c, p1, p2, cross_section=XS, straight=straight_pins, bend=bend_pins, **kw)
    c.info["routes"] = c.info["routes"] + [(what, um(r))]
    return r


def loopback(name="loopback"):
    """Two couplers joined by the shortest waveguide: the coupler reference for every other device."""
    c, gc_in, gc_out = coupler_pair(name)
    route(c, gc_in.ports["o1"], gc_out.ports["o1"], "coupler to coupler")
    return c


# ---------------------------------------------------------------------------------------------------------
# Part C. An unbalanced Mach-Zehnder interferometer (Chapter 11)
# ---------------------------------------------------------------------------------------------------------
def mzi(name="mzi", dl=MZI_DL, arm=50.0):
    """Two Y-branches; the long arm dips down by `depth` so that it is dl longer than the straight arm."""
    c, gc_in, gc_out = coupler_pair(name)
    y1 = c << pdk_cell("ebeam_y_1550")
    p = y1.ports["o1"].dcenter
    y1.dmove((10.0 - p[0], GC_PITCH - p[1]))       # splitter input 10 um east of the input coupler
    y2 = c << pdk_cell("ebeam_y_1550")
    y2.drotate(180)                                 # combiner faces back: its o3 (upper) and o2 (lower) face west
    a, b = y1.ports["o2"].dcenter, y2.ports["o3"].dcenter
    y2.dmove((a[0] + arm - b[0], a[1] - b[1]))      # straight arm of length `arm`
    bend = gf.get_component("bend_euler", cross_section=XS)
    extra = 4 * (2 * bend.info["dy"] - bend.info["length"])   # four Euler bends are shorter than their corners
    depth = (dl + extra) / 2                         # the dip adds 2 x depth, less what the bends save
    route(c, gc_in.ports["o1"], y1.ports["o1"], "input")
    route(c, y1.ports["o2"], y2.ports["o3"], "short arm")
    s, e = y1.ports["o3"].dcenter, y2.ports["o2"].dcenter
    r = bend.info["dy"]
    route(c, y1.ports["o3"], y2.ports["o2"], "long arm",
          waypoints=[(s[0] + r, s[1]), (s[0] + r, s[1] - depth), (e[0] - r, e[1] - depth), (e[0] - r, e[1])])
    route(c, y2.ports["o1"], gc_out.ports["o1"], "output")
    arms = dict(c.info["routes"])
    c.info["dL"] = arms["long arm"] - arms["short arm"]
    return c


# ---------------------------------------------------------------------------------------------------------
# Part D. All-pass rings with three gaps (Chapter 12)
# ---------------------------------------------------------------------------------------------------------
@gf.cell
def ring_cell(gap=0.2, radius=RING_R):
    """ubcpdk's ring_single as a circle (no straight sections), as one SiEPIC component."""
    return siepic(gf.get_component("ring_single", gap=gap, radius=radius, length_x=0.0, length_y=0.0,
                                   cross_section=XS))


def ring(name, gap, radius=RING_R):
    """A point-coupled circular ring below a straight bus between the two couplers."""
    c, gc_in, gc_out = coupler_pair(name)
    rg = c << ring_cell(gap=gap, radius=radius)
    rg.dmirror_y()                                  # ring below the bus, away from the next device up
    p = rg.ports["o1"].dcenter
    rg.dmove((25.0 - p[0], GC_PITCH - p[1]))
    route(c, gc_in.ports["o1"], rg.ports["o1"], "input")
    route(c, rg.ports["o2"], gc_out.ports["o1"], "output")
    c.info["routes"] = c.info["routes"] + [("bus", rg.ports["o2"].dcenter[0] - rg.ports["o1"].dcenter[0])]
    c.info["gap"], c.info["ring_length"] = gap, 2 * math.pi * radius
    return c


# ---------------------------------------------------------------------------------------------------------
# Part E. Cutback spirals (Chapter 7)
# ---------------------------------------------------------------------------------------------------------
@gf.cell
def spiral_cell(loops=6, straight=20.0):
    """ubcpdk's racetrack spiral with straight leads out to its bounding box, as one SiEPIC component."""
    c = gf.Component()
    s = c << gf.get_component("spiral_racetrack", straight_length=straight, spacings=(SPIRAL_PITCH,) * loops,
                              cross_section=XS)
    bb = s.dbbox()
    lead_in = c << gf.c.straight(length=s.ports["o1"].dcenter[0] - bb.left, cross_section=XS)
    lead_in.connect("o2", s.ports["o1"])
    lead_out = c << gf.c.straight(length=bb.right - s.ports["o2"].dcenter[0], cross_section=XS)
    lead_out.connect("o1", s.ports["o2"])
    c.add_port("o1", port=lead_in.ports["o1"])
    c.add_port("o2", port=lead_out.ports["o2"])
    c.info["length"] = s.cell.info["length"] + lead_in.cell.info["length"] + lead_out.cell.info["length"]
    return siepic(c)


def spiral(name, loops, straight):
    """A racetrack spiral, in and back out, between the two couplers."""
    c, gc_in, gc_out = coupler_pair(name)
    sp = c << spiral_cell(loops=loops, straight=straight)
    p = sp.ports["o1"].dcenter
    sp.dmove((5.0 - p[0], GC_PITCH - p[1]))         # its input 5 um east of the coupler
    route(c, gc_in.ports["o1"], sp.ports["o1"], "input")
    route(c, sp.ports["o2"], gc_out.ports["o1"], "output")
    c.info["routes"] = c.info["routes"] + [("spiral", sp.cell.info["length"])]
    return c


def build_devices(ring_gaps=RING_GAPS, dl=MZI_DL, suffix=""):
    """Every device, keyed by its name in COLUMNS; `suffix` keeps cell names unique if you build two chips."""
    devs = {"loopback": loopback("loopback" + suffix), "mzi": mzi("mzi" + suffix, dl=dl)}
    for key, g in zip(("ring200", "ring250", "ring300"), ring_gaps):
        devs[key] = ring(key + suffix, g)
    for key, (n, s) in SPIRALS.items():
        devs[key] = spiral(key + suffix, n, s)
    return devs


# ---------------------------------------------------------------------------------------------------------
# Part F. The floorplan, the labels and the GDS file
# ---------------------------------------------------------------------------------------------------------
def label_text(name, user=USER):
    """opt_in_<polarisation>_<wavelength>_<type>_<deviceID>_<params>, as SiEPIC-Tools reads it."""
    return f"opt_in_TE_1550_device_{user}_{name}"


def build_chip(top_name=TOP_NAME, ring_gaps=RING_GAPS, dl=MZI_DL, move_label=None, move_device=None, suffix=""):
    """The whole chip. move_label = (name, dx, dy) and move_device = (name, dx, dy) break it on purpose (Lab 8)."""
    devs = build_devices(ring_gaps, dl, suffix)
    chip = gf.Component(top_name)
    chip.add_polygon([(0, 0), (FLOORPLAN[0], 0), FLOORPLAN, (0, FLOORPLAN[1])], layer=LAYER_FLOORPLAN)
    placed, x = {}, X_FIRST
    for column in COLUMNS:
        width = 0.0
        for name, y0 in zip(column, Y_PAIRS):
            d = devs[name]
            ref = chip << d
            dx, dy = (move_device[1:] if move_device and move_device[0] == name else (0.0, 0.0))
            ref.dmove((x + dx, y0 + dy))
            in_xy = (x + dx, y0 + dy + GC_PITCH)
            lx, ly = (move_label[1:] if move_label and move_label[0] == name else (0.0, 0.0))
            chip.add_label(label_text(name), position=(in_xy[0] + lx, in_xy[1] + ly), layer=LAYER_TEXT)
            placed[name] = dict(cell=d, ref=ref, gc_in=in_xy, gc_out=(x + dx, y0 + dy), label=label_text(name))
            width = max(width, d.dbbox().right)
        x = math.ceil(x + width + COLUMN_GAP)        # next column, on a whole micrometre
    return chip, placed


def silicon_bbox(chip):
    """Bounding box of the silicon layer, as the openEBL submission check measures it."""
    return kdb.Region(chip.kdb_cell.begin_shapes_rec(chip.kcl.layer(*LAYER_SI))).bbox().to_dtype(chip.kcl.dbu)


def write_gds(chip, path=None):
    return chip.write_gds(path or f"{chip.name}.gds", with_metadata=False)


def main(plot=True, show=False):
    print("Lab 7: lay out your first chip (gdsfactory + ubcpdk, the SiEPIC EBeam PDK)\n")
    chip, placed = build_chip()

    # ---- Part A
    print("A. The openEBL rules this layout follows")
    print(f"   design area {FLOORPLAN[0]:.0f} x {FLOORPLAN[1]:.0f} um on layer {LAYER_FLOORPLAN[0]}/{LAYER_FLOORPLAN[1]};"
          f" silicon on {LAYER_SI[0]}/{LAYER_SI[1]}, labels on {LAYER_TEXT[0]}/{LAYER_TEXT[1]}")
    print(f"   grating coupler '{GC}', unrotated, on a {GC_PITCH:.0f} um pitch; top cell '{chip.name}'")
    print(f"   label format: {label_text('<name>')}\n")

    # ---- Part B
    lb = placed["loopback"]["cell"]
    print("B. Couplers and the loopback")
    print(f"   input coupler 127 um above the output one; loopback waveguide {lb.info['routes'][0][1]:.1f} um\n")

    # ---- Part C
    m = placed["mzi"]["cell"]
    arms = dict(m.info["routes"])
    fsr = 1e3 * LAM ** 2 / (NG * m.info["dL"])
    print("C. The unbalanced MZI")
    print(f"   short arm {arms['short arm']:.3f} um, long arm {arms['long arm']:.3f} um: dL = {m.info['dL']:.3f} um"
          f" (target {MZI_DL:.0f})")
    print(f"   FSR = lam^2 / (n_g dL) = {LAM ** 2:.4f} / ({NG} x {m.info['dL'] * 1e-3:.4f} mm) = {fsr:.2f} nm"
          "   (Chapter 11: 5.75 nm for 100 um)\n")

    # ---- Part D
    print("D. Rings (R = 10 um, point-coupled)")
    for k in ("ring200", "ring250", "ring300"):
        d = placed[k]["cell"]
        print(f"   {k}: gap {1e3 * d.info['gap']:.0f} nm, circumference {d.info['ring_length']:.2f} um,"
              f" FSR {1e3 * LAM ** 2 / (NG * d.info['ring_length']):.2f} nm   (Table 12.1; Chapter 12: 9.1 nm)")
    print()

    # ---- Part E
    print("E. Waveguide length per device (routes + spirals; fixed PDK cells not counted)")
    for name, p in placed.items():
        tot = sum(l for _, l in p["cell"].info["routes"])
        p["length"] = tot
        print(f"   {name:<9} {tot:8.1f} um   " + ", ".join(f"{w} {l:.1f}" for w, l in p["cell"].info["routes"]))
    cut = sorted(placed[k]["length"] for k in ("loopback", "spiral1", "spiral2", "spiral3"))
    print(f"   cutback set: {', '.join(f'{1e-3 * l:.2f}' for l in cut)} mm; at 2 dB/cm the longest adds"
          f" {0.2 * 1e-3 * (cut[-1] - cut[0]):.2f} dB over the loopback\n")

    # ---- Part F
    bb = silicon_bbox(chip)
    fits = bb.left >= 0 and bb.bottom >= 0 and bb.right <= FLOORPLAN[0] and bb.top <= FLOORPLAN[1]
    print("F. Floorplan, labels and the GDS")
    print(f"   {len(placed)} devices, {2 * len(placed)} grating couplers in {len(COLUMNS)} columns")
    print(f"   silicon footprint x {bb.left:.1f} .. {bb.right:.1f}, y {bb.bottom:.1f} .. {bb.top:.1f} um"
          f" ({bb.width():.1f} x {bb.height():.1f} um)")
    print(f"   fits the {FLOORPLAN[0]:.0f} x {FLOORPLAN[1]:.0f} um floorplan: {'yes' if fits else 'NO'}"
          f" (margins {bb.left:.1f}, {FLOORPLAN[0] - bb.right:.1f}, {bb.bottom:.1f}, {FLOORPLAN[1] - bb.top:.1f} um)")
    print("   labels (at the input coupler of each device):")
    for name, p in placed.items():
        print(f"     {p['label']:<40} at ({p['gc_in'][0]:.0f}, {p['gc_in'][1]:.0f})")
    path = write_gds(chip)
    print(f"   wrote {path.name}, top cell {chip.name}")

    if show:
        chip.show()                                  # needs KLayout running with the klive package
    if plot:
        draw(path, placed)


def polygons(cell, layer, trans=None):
    """Every polygon of `layer` under a klayout cell, flattened, as lists of (x, y) in um."""
    import klayout.db as kdb
    ly = cell.layout()
    li = ly.find_layer(*layer)
    if li is None:
        return []
    it = cell.begin_shapes_rec(li)
    out = []
    while not it.at_end():
        sh = it.shape()
        if sh.is_polygon() or sh.is_box() or sh.is_path():
            t = (trans or kdb.DCplxTrans()) * it.dtrans()
            poly = sh.dpolygon.transformed(t)
            out.append([(p.x, p.y) for p in poly.each_point_hull()])
        it.next()
    return out


def draw(gds_path, placed):
    import klayout.db as kdb
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Rectangle

    ly = kdb.Layout()
    ly.read(str(gds_path))
    top = ly.top_cell()
    colours = {"loopback": "tab:grey", "mzi": "tab:purple", "ring": "tab:blue", "spiral": "tab:green"}
    fig = plt.figure(figsize=(11.5, 5.5))
    ax = fig.add_axes([0.05, 0.08, 0.60, 0.86])
    axm = fig.add_axes([0.70, 0.56, 0.28, 0.38])
    axr = fig.add_axes([0.70, 0.08, 0.28, 0.38])

    gc_polys, dev_polys = [], {}
    for inst in top.each_inst():
        name = inst.cell.name
        kind = next(k for k in colours if name.startswith(k))
        for sub in inst.cell.each_inst():
            tr = inst.dcplx_trans * sub.dcplx_trans
            polys = polygons(sub.cell, LAYER_SI, tr)
            (gc_polys if sub.cell.name == GC else dev_polys.setdefault(kind, [])).extend(polys)
    for a in (ax, axm, axr):
        a.add_collection(PolyCollection(gc_polys, facecolor="0.55", edgecolor="none"))
        for kind, polys in dev_polys.items():
            a.add_collection(PolyCollection(polys, facecolor=colours[kind], edgecolor=colours[kind], linewidth=0.4))
        a.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), *FLOORPLAN, fill=False, ec="k", lw=1.2, ls="--"))
    for name, p in placed.items():
        x, y = p["gc_in"]
        ax.plot([x], [y], marker="o", ms=4, color="tab:red")
        ax.text(x + 4, y + 6, name, fontsize=7.5, color="tab:red")
    x0, y0 = placed["loopback"]["gc_out"]
    ax.annotate("", xy=(x0 - 22, y0), xytext=(x0 - 22, y0 + GC_PITCH),
                arrowprops=dict(arrowstyle="<->", color="k", lw=0.8))
    ax.text(x0 - 20, y0 + GC_PITCH / 2, "127 µm", fontsize=8, rotation=90, va="center")
    ax.set(xlim=(-10, FLOORPLAN[0] + 10), ylim=(-10, FLOORPLAN[1] + 10), xlabel="x (µm)", ylabel="y (µm)",
           title=f"(a) {top.name}: {FLOORPLAN[0]:.0f} × {FLOORPLAN[1]:.0f} µm, {len(placed)} devices")
    ax.text(FLOORPLAN[0] / 2, FLOORPLAN[1] / 2, "design area (floorplan, layer 99/0)", fontsize=8, ha="center",
            va="center", color="0.4")
    ax.plot([], [], "o", color="tab:red", ms=4, label="opt_in label (input coupler)")
    ax.legend(fontsize=8, loc="lower right", framealpha=0.9)

    # (b) the MZI and (c) a ring's coupler
    mx, my = placed["mzi"]["gc_out"]
    axm.set(xlim=(mx - 45, mx + 130), ylim=(my + 50, my + 145), xlabel="x (µm)",
            title=f"(b) MZI, ΔL = {placed['mzi']['cell'].info['dL']:.1f} µm")
    rx, ry = placed["ring200"]["gc_in"]
    cx = rx + 25.0 + RING_R                          # the bus reaches the coupler 25 + R um east of the input port
    axr.set(xlim=(cx - 3, cx + 3), ylim=(ry - 2.2, ry + 0.8), xlabel="x (µm)",
            title="(c) ring coupler, 200 nm gap")
    axr.annotate("", xy=(cx, ry - 0.25), xytext=(cx, ry - 0.45), arrowprops=dict(arrowstyle="<->", color="k", lw=0.8,
                 shrinkA=0, shrinkB=0))
    axr.text(cx + 0.15, ry - 0.36, "200 nm gap", fontsize=8, va="center")
    axr.text(cx - 2.8, ry, "bus, 500 nm", fontsize=8, color="w", va="center")
    axr.text(cx - 2.8, ry - 1.9, f"ring, R = {RING_R:.0f} µm", fontsize=8, va="center")
    fig.savefig("lab07_layout.png", dpi=150)
    print("Saved the figure as lab07_layout.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv, show="--show" in sys.argv)
