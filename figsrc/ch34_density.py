"""ch34_density.py -- density, fill and layer derivation for Chapter 34 (KLayout's Python module, e.g. in the
photonics-labs container):

  python ch34_density.py        -> figsrc/ch34_density.json, figsrc/ch34_derive.json,
                                   figsrc/ch34_die.oas and figsrc/ch34_die_fill.oas (inputs of ch34_density.lydrc)

1. A 1 mm x 1 mm die of a passive SOI chip (grating couplers, routing, a spiral, rings, MZIs, a sub-wavelength
   block), its silicon density in 100 um windows stepped by 50 um, then the same after dummy fill (2 um squares on a
   4 um pitch, kept 3 um from any silicon and 10 um from the grating couplers). The density rule (20-80 %) is the
   illustrative rule of the chapter's toy process.
2. Layer derivation: drawn core and slab layers -> full-etch and shallow-etch masks; a trench-style alternative; and
   the sliver that a 5 nm misalignment between two drawn layers leaves on a derived layer.
"""
import json
import math
import os

import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
DBU = 0.001
W = 0.5                                   # waveguide width (um)
DIE = 1000.0
WIN, STEP = 100.0, 50.0                   # density window and step (um)
RULE = (0.20, 0.80)
FILL_SQ, FILL_PITCH, KEEP_SI, KEEP_GC = 2.0, 4.0, 3.0, 10.0


def um(v):
    return int(round(v / DBU))


def path_region(pts, w=W):
    return kdb.Region(kdb.DPath([kdb.DPoint(x, y) for x, y in pts], w).to_itype(DBU).polygon())


def ring_region(cx, cy, r, w=W, n=256):
    outer = [kdb.DPoint(cx + (r + w / 2) * math.cos(2 * math.pi * k / n), cy + (r + w / 2) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    inner = [kdb.DPoint(cx + (r - w / 2) * math.cos(2 * math.pi * k / n), cy + (r - w / 2) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    p = kdb.DPolygon(outer); p.insert_hole(inner)
    return kdb.Region(p.to_itype(DBU))


def box(x0, y0, x1, y1):
    return kdb.Region(kdb.DBox(x0, y0, x1, y1).to_itype(DBU))


def build_die():
    si, gcr = kdb.Region(), kdb.Region()
    # six grating couplers on a 127 um pitch, facing left at x = 20..50: 15 um taper + 15 um grating, 50 % teeth
    gc_y = [182.5 + 127 * k for k in range(6)]
    for y in gc_y:
        taper = kdb.DPolygon([kdb.DPoint(50, y - W / 2), kdb.DPoint(50, y + W / 2), kdb.DPoint(35, y + 6), kdb.DPoint(35, y - 6)])
        si.insert(taper.to_itype(DBU))
        for k in range(24):
            x0 = 35 - 0.63 * (k + 1)
            si += box(x0, y - 6, x0 + 0.315, y + 6)
        gcr += box(19.88, y - 6, 50, y + 6)
    # loopback between the first two couplers
    si += path_region([(50, gc_y[0]), (120, gc_y[0]), (120, gc_y[1]), (50, gc_y[1])])
    # spiral delay line (rectangular, 5 um pitch) between couplers 3 and 4, in a 250 um square
    x0, y0, s, p = 350.0, 560.0, 250.0, 5.0
    pts = [(50, gc_y[2]), (x0, gc_y[2])]
    xa, ya, xb, yb = x0, y0, x0 + s, y0 + s
    pts += [(xa, ya)]
    while xb - xa > 30:
        pts += [(xb, ya), (xb, yb), (xa + p, yb), (xa + p, ya + p)]
        xa, ya, xb, yb = xa + p, ya + p, xb - p, yb - p
    si += path_region(pts)
    si += path_region([(50, gc_y[3]), (330, gc_y[3]), (330, 900), (xa + 40, 900), (xa + 40, yb - 20), (xa + 5, yb - 20)])
    # three all-pass rings (R = 10 um) on one bus between couplers 5 and 6
    yb5 = gc_y[4]
    si += path_region([(50, yb5), (200, yb5), (200, 300), (700, 300), (700, gc_y[5] - 60), (60, gc_y[5] - 60),
                       (60, gc_y[5]), (50, gc_y[5])])
    for k, gap in enumerate((0.2, 0.25, 0.3)):
        si += ring_region(330 + 150 * k, 300 + W + gap + 10.0, 10.0)
    # two MZIs (100 um arm difference) near the right edge, fed from the bus
    for k in range(2):
        yc = 120 + 220 * k
        si += path_region([(760, yc), (800, yc), (820, yc + 20), (900, yc + 20), (920, yc), (960, yc)])
        si += path_region([(800, yc), (820, yc - 20), (840, yc - 20), (840, yc - 70), (880, yc - 70), (880, yc - 20),
                           (900, yc - 20), (920, yc)])
    # a sub-wavelength grating block: 60 x 60 um of 0.2 um lines on a 0.4 um pitch
    for k in range(150):
        si += box(800 + 0.4 * k, 700, 800 + 0.4 * k + 0.2, 760)
    si.merge()
    gcr.merge()
    return si, gcr


def density_map(si, die):
    n = int((DIE - WIN) / STEP) + 1
    dmap = []
    for j in range(n):
        row = []
        for i in range(n):
            win = box(i * STEP, j * STEP, i * STEP + WIN, j * STEP + WIN)
            row.append((si & win).area() * DBU * DBU / (WIN * WIN))
        dmap.append(row)
    return dmap


def make_fill(si, gcr, die):
    excl = si.sized(um(KEEP_SI)) + gcr.sized(um(KEEP_GC))
    allowed = die - excl
    sq = kdb.Region()
    n = int(DIE / FILL_PITCH)
    for j in range(n):
        for i in range(n):
            x, y = i * FILL_PITCH + (FILL_PITCH - FILL_SQ) / 2, j * FILL_PITCH + (FILL_PITCH - FILL_SQ) / 2
            sq.insert(kdb.DBox(x, y, x + FILL_SQ, y + FILL_SQ).to_itype(DBU))
    fill = sq.inside(allowed)
    return fill, excl


def stats(dmap):
    flat = [v for r in dmap for v in r]
    lo = sum(v < RULE[0] for v in flat); hi = sum(v > RULE[1] for v in flat)
    return dict(n=len(flat), min=min(flat), max=max(flat), mean=sum(flat) / len(flat), below=lo, above=hi)


def write_layout(path, layers):
    ly = kdb.Layout(); ly.dbu = DBU
    top = ly.create_cell("DIE")
    for (l, d), reg in layers.items():
        top.shapes(ly.layer(l, d)).insert(reg)
    ly.write(path)
    return os.path.getsize(path)


def die_part():
    die = box(0, 0, DIE, DIE)
    si, gcr = build_die()
    d0 = density_map(si, die)
    fill, excl = make_fill(si, gcr, die)
    si_f = si + fill
    d1 = density_map(si_f, die)
    a_si = si.area() * DBU ** 2; a_fill = fill.area() * DBU ** 2
    # trench-style process: only a 2 um trench around each core is etched, the rest of the die stays silicon
    a_trench = ((si.sized(um(2.0)) - si) & die).area() * DBU ** 2
    s0, s1 = stats(d0), stats(d1)
    # OASIS files for the KLayout-application check (ch34_density.lydrc), and the sizes of the filled die
    # written flat as GDS and as OASIS
    write_layout(os.path.join(HERE, "ch34_die.oas"), {(1, 0): si, (99, 0): die})
    oas = write_layout(os.path.join(HERE, "ch34_die_fill.oas"), {(1, 0): si_f, (99, 0): die})
    gds = write_layout(os.path.join(os.environ.get("CH34_TMP", "/tmp"), "ch34_die_fill.gds"), {(1, 0): si_f, (99, 0): die})
    sizes = dict(gds=gds, oas=oas, n_shapes=si_f.count())
    # evanescent decay outside a 500 x 220 nm strip: gamma = k0 sqrt(neff^2 - nclad^2), neff from Chapter 6
    neff, nclad, lam = 2.446, 1.444, 1.55
    gamma = 2 * math.pi / lam * math.sqrt(neff ** 2 - nclad ** 2)
    res = dict(die=DIE, win=WIN, step=STEP, rule=RULE, fill=dict(sq=FILL_SQ, pitch=FILL_PITCH, keep_si=KEEP_SI, keep_gc=KEEP_GC),
               area_si=a_si, area_fill=a_fill, area_trench=a_trench, density_trench=1 - a_trench / DIE ** 2, n_fill=fill.count(), density_global=a_si / DIE ** 2,
               density_global_fill=(a_si + a_fill) / DIE ** 2, before=s0, after=s1, map_before=d0, map_after=d1,
               gamma=gamma, field_at_keepout=math.exp(-gamma * KEEP_SI), sizes=sizes,
               si=[dict(hull=[(round(q.x * DBU, 3), round(q.y * DBU, 3)) for q in p.each_point_hull()],
                        holes=[[(round(q.x * DBU, 3), round(q.y * DBU, 3)) for q in p.each_point_hole(h)] for h in range(p.holes())])
                   for p in si.each()],
               gc=[[(round(q.x * DBU, 3), round(q.y * DBU, 3)) for q in p.each_point_hull()] for p in gcr.each()])
    print("Si area %.0f um2 (%.2f %%), fill %d squares %.0f um2 -> %.2f %%" % (a_si, 100 * a_si / DIE ** 2, fill.count(), a_fill,
          100 * (a_si + a_fill) / DIE ** 2))
    print("trench style: etched %.0f um2, Si density %.1f %%" % (a_trench, 100 * (1 - a_trench / DIE ** 2)))
    print("before", s0); print("after ", s1); print("sizes", sizes, "gamma %.3f /um, field at keep-out %.2e" % (gamma, res["field_at_keepout"]))
    # fill squares near one coupler and the loopback, for the figure's close-up
    zoom = box(0, 120, 200, 360)
    res_zoom = [[(round(q.x * DBU, 3), round(q.y * DBU, 3)) for q in p.each_point_hull()] for p in (fill & zoom).each()]
    with open(os.path.join(HERE, "ch34_density.json"), "w") as f:
        res["fill_zoom"] = res_zoom
        res["map_before"] = [[round(v, 5) for v in r] for r in d0]
        res["map_after"] = [[round(v, 5) for v in r] for r in d1]
        json.dump(res, f)


def derive_part():
    """Drawn layers -> mask layers for a two-etch SOI process (strip and rib waveguides), with two slivers."""
    region = box(0, 0, 40, 14)
    core = kdb.Region()
    core += path_region([(0, 4), (40, 4)])                    # rib waveguide (in the slab) along y = 4
    core += path_region([(0, 10.5), (40, 10.5)])              # strip waveguide along y = 10.5
    # slab kept around the rib from x = 12 to 32, 2 um each side of the centre line, entered through a
    # strip-to-rib taper that starts at exactly the core width at x = 6
    slab = box(12, 2, 32, 6)
    slab += kdb.Region(kdb.DPolygon([kdb.DPoint(6, 4 - W / 2), kdb.DPoint(12, 2), kdb.DPoint(12, 6), kdb.DPoint(6, 4 + W / 2)]).to_itype(DBU))
    # a slab piece drawn by hand beside the strip guide, 5 nm off its edge
    slab += box(30, 10.75 + 0.005, 38, 12.5)
    slab.merge()
    full_etch = region - (core + slab)                       # silicon removed down to the oxide
    shallow = slab - core                                     # partial etch: leaves the slab
    trench = (core.sized(um(2.0)) - core) & region            # trench style: etch only 2 um around each core
    E = kdb.Metrics.Euclidian
    m_sh = shallow.width_check(um(0.15), False, E, 80)
    m_fe = full_etch.width_check(um(0.15), False, E, 80)
    narrow = (shallow - shallow.sized(-um(0.075)).sized(um(0.075))) + (full_etch - full_etch.sized(-um(0.075)).sized(um(0.075)))

    def polys(reg):
        return [dict(hull=[(q.x * DBU, q.y * DBU) for q in p.each_point_hull()],
                     holes=[[(q.x * DBU, q.y * DBU) for q in p.each_point_hole(h)] for h in range(p.holes())]) for p in reg.each()]

    def eps(e):
        return [[(x.first.p1.x * DBU, x.first.p1.y * DBU, x.first.p2.x * DBU, x.first.p2.y * DBU),
                 (x.second.p1.x * DBU, x.second.p1.y * DBU, x.second.p2.x * DBU, x.second.p2.y * DBU)] for x in e.each()]
    out = {nm: polys(reg) for nm, reg in dict(core=core, slab=slab, full_etch=full_etch, shallow=shallow, trench=trench,
                                               narrow=narrow).items()}
    out["markers_shallow"] = eps(m_sh)
    out["markers_full"] = eps(m_fe)
    out["areas"] = {k: v.area() * DBU ** 2 for k, v in dict(region=region, full_etch=full_etch, shallow=shallow, trench=trench).items()}
    # how long is the knife edge: where is the shallow-etch region narrower than 150 nm along the taper?
    out["knife_len"] = max((p.bbox().width() * DBU for p in (shallow - shallow.sized(-um(0.075)).sized(um(0.075))).each()), default=0)
    print("derive: markers shallow", m_sh.count(), "full", m_fe.count(), "knife length %.2f um" % out["knife_len"], "areas", out["areas"])
    with open(os.path.join(HERE, "ch34_derive.json"), "w") as f:
        json.dump(out, f)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or "derive" in sys.argv:
        derive_part()
    if len(sys.argv) < 2 or "die" in sys.argv:
        die_part()
