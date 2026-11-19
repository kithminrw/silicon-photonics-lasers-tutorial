"""gdsfactory experiments for Chapter 33 (run in Docker: gdsfactory 9.51, sax 0.18; writes figsrc/ch33_gdsfactory.json).

    MSYS_NO_PATHCONV=1 docker exec -w /repo photonics-labs /opt/conda/envs/labs/bin/python figsrc/ch33_gdsfactory.py

1. the chapter's listing: a cross-section, an MZI between two grating couplers on the 127 um pitch, routed;
2. its netlist, extracted from the layout, simulated with SAX to check the free spectral range;
3. a small chip floorplan (Figure 33.6) and a bundle route from the fibre-array pitch to a dense device
   (Figure 33.7), whose outlines, ports and route lengths go to the JSON file for ch33_figs.py.
Uses gdsfactory's generic PDK (layer 1/0 for the waveguide core); GDS files go to a temporary folder.
"""
import json
import math
import os
import sys
import tempfile
import time

import numpy as np

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="ch33gf_")
OUT = {}

# ---- listing starts (Section 33.4; keep in step with the chapter)
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
# ---- listing ends


def outlines(c, layers, nd=3):
    """Merged outlines of a component per layer, in um, rounded: {"L/D": [[hull, hole, ...], ...]}."""
    out = {}
    dbu = c.kcl.dbu
    for ln, dt in layers:
        li = c.kcl.layout.find_layer(ln, dt)             # KLayout's own lookup: None if the layer is absent
        if li is None:
            continue
        reg = gf.kdb.Region(c.kdb_cell.begin_shapes_rec(li)).merged()
        polys = []
        for p in reg.each():
            rings = [[[round(q.x * dbu, nd), round(q.y * dbu, nd)] for q in p.each_point_hull()]]
            rings += [[[round(q.x * dbu, nd), round(q.y * dbu, nd)] for q in p.each_point_hole(h)] for h in range(p.holes())]
            polys.append(rings)
        out[f"{ln}/{dt}"] = polys
    return out


def ports_of(refs_ports):
    return [{"name": p.name, "x": round(p.dcenter[0], 3), "y": round(p.dcenter[1], 3), "o": p.orientation,
             "w": p.dwidth, "type": p.port_type} for p in refs_ports]


def part1_2():
    c = mzi_with_couplers()
    c.write_gds(os.path.join(TMP, "mzi_with_couplers.gds"))
    net = c.get_netlist()
    comps = {}
    for v in net["instances"].values():
        comps[v["component"]] = comps.get(v["component"], 0) + 1
    res = {"name": c.name, "bbox": [c.dxmin, c.dymin, c.dxmax, c.dymax], "instances": comps,
           "n_nets": len(net["nets"]), "ports": net["ports"], "outline": outlines(c, [(1, 0)]),
           "netlist_sample": {k: {"component": v["component"]} for k, v in list(net["instances"].items())[:4]},
           "nets_sample": net["nets"][:3], "labels": [[label.string, label.x * c.kcl.dbu, label.y * c.kcl.dbu] for label in
                                                     [s.text for s in c.kdb_cell.shapes(c.kcl.layer(10, 0)).each() if s.is_text()]],
           "inst_ports": [dict(ports_of(i.ports)[k], inst=i.name) for i in c.insts for k in range(len(i.ports))], "placement_sample": {k: net["placements"][k] for k in list(net["placements"])[:2]}}
    # ---- circuit simulation of the extracted netlist with SAX: each leaf cell gets a simple model
    import sax
    import jax.numpy as jnp
    L_bend = gf.components.bend_euler(cross_section=xs).info["length"]

    def straight(wl=1.55, length=10.0, neff=2.446, ng=4.18, wl0=1.55, loss_dB_cm=2.0):
        n = neff - (ng - neff) * (wl - wl0) / wl0            # n_eff(lambda) to first order, from n_g (Chapter 6)
        amp = 10 ** (-loss_dB_cm * length * 1e-4 / 20)
        return sax.reciprocal({("o1", "o2"): amp * jnp.exp(2j * jnp.pi * n * length / wl)})

    def bend_euler(wl=1.55):
        return straight(wl=wl, length=L_bend)

    def mmi1x2(wl=1.55):                                      # ideal 50/50 splitter
        return sax.reciprocal({("o1", "o2"): 0.5 ** 0.5, ("o1", "o3"): 0.5 ** 0.5})

    def gc(wl=1.55):                                          # ideal coupler: the envelope is left out
        return sax.reciprocal({("o1", "o2"): 1.0})

    models = {"straight": straight, "bend_euler": bend_euler, "mmi1x2": mmi1x2,
              "grating_coupler_elliptical": gc, "grating_coupler_elliptical_te": gc}
    rnet = c.get_netlist(recursive=True)
    circuit, _ = sax.circuit(netlist=rnet, models=models)
    wl = np.linspace(1.535, 1.565, 6001)
    S = circuit(wl=wl)
    keys = sorted({k[0] for k in S.keys()})
    T = np.abs(np.asarray(S["in", "out"])) ** 2
    mins = [i for i in range(1, len(T) - 1) if T[i] < T[i - 1] and T[i] <= T[i + 1] and T[i] < 0.5]
    lam_min = wl[mins] * 1e3
    fsr = np.diff(lam_min)
    near = int(np.argmin(np.abs(lam_min[:-1] + fsr / 2 - 1550)))
    res["sax"] = {"ports": keys, "minima_nm": lam_min.round(3).tolist(), "fsr_nm": fsr.round(3).tolist(),
                  "fsr_near_1550_nm": float(fsr[near]), "fsr_formula_nm": 1550 ** 2 / (4.18 * 100e3),
                  "wl_nm": (wl[::20] * 1e3).round(3).tolist(), "T_dB": (10 * np.log10(T[::20] + 1e-12)).round(3).tolist(),
                  "L_bend_um": L_bend, "n_recursive_cells": len(rnet)}
    OUT["mzi_test"] = res
    print(f"1-2. {c.name}: {comps}; {len(net['nets'])} nets; SAX FSR near 1550 nm {fsr[near]:.3f} nm "
          f"(formula {1550 ** 2 / (4.18 * 100e3):.3f}); {time.time() - T0:.0f} s")


# ---------------------------------------------------------------- 3. a floorplan and a bundle route
DIE = (1000.0, 800.0)


@gf.cell
def ring_heater_with_couplers() -> gf.Component:
    c = gf.Component()
    ring = c << gf.components.ring_single_heater(gap=0.2, radius=10, cross_section=xs)
    gc_out = c << gf.components.grating_coupler_elliptical_te(cross_section=xs)
    gc_in = c << gf.components.grating_coupler_elliptical_te(cross_section=xs)
    for gc, y in ((gc_out, 0.0), (gc_in, PITCH)):
        gc.drotate(180)
        gc.dmove((0.0, y))
    ring.dmove((120.0 - ring.ports["o1"].dcenter[0], 70.0))
    gf.routing.route_single(c, gc_in.ports["o1"], ring.ports["o1"], cross_section=xs)
    gf.routing.route_single(c, ring.ports["o2"], gc_out.ports["o1"], cross_section=xs)
    # two probe pads, 100 um pitch, joined to the heater's via stacks by metal routes
    pads = []
    for k in range(2):
        p = c << gf.components.pad(size=(80.0, 80.0))
        p.dmove((420.0 + 100.0 * k, 160.0))
        pads.append(p)
    for port, pad, yh in ((ring.ports["l_e2"], pads[0], 110.0), (ring.ports["r_e2"], pads[1], 100.0)):  # 6 um M3 leads
        (x0, y0), (x1, y1) = port.dcenter, pad.ports["e4"].dcenter
        lead = gf.kdb.DPath([gf.kdb.DPoint(x0, y0), gf.kdb.DPoint(x0, yh), gf.kdb.DPoint(x1, yh), gf.kdb.DPoint(x1, y1)], 6.0)
        c.add_polygon(lead.polygon(), layer=(49, 0))
    c.add_label("opt_in_TE_1550_device_demo_ringheater", position=gc_in.ports["o1"].dcenter, layer=(10, 0))
    return c


@gf.cell
def demo_chip() -> gf.Component:
    c = gf.Component()
    c.add_polygon([(0, 0), (DIE[0], 0), (DIE[0], DIE[1]), (0, DIE[1])], layer=(99, 0))   # floorplan box
    x0, y0 = 60.0, 82.5                                   # column of couplers: port x, lowest coupler y
    loop = []
    for k in (0, 5):                                      # the loopback uses the outermost couplers
        g = c << gf.components.grating_coupler_elliptical_te(cross_section=xs)
        g.drotate(180)
        g.dmove((x0, y0 + k * PITCH))
        loop.append(g)
    m = c << mzi_with_couplers()
    m.dmove((x0, y0 + 1 * PITCH))
    r = c << ring_heater_with_couplers()
    r.dmove((x0, y0 + 3 * PITCH))
    gf.routing.route_single(c, loop[0].ports["o1"], loop[1].ports["o1"], cross_section=xs,
                            waypoints=[(DIE[0] - 60.0, y0), (DIE[0] - 60.0, y0 + 5 * PITCH)])
    c.add_label("opt_in_TE_1550_device_demo_loopback", position=loop[0].ports["o1"].dcenter, layer=(10, 0))
    return c


@gf.cell
def fanin() -> gf.Component:
    """Four couplers on the fibre-array pitch routed as a bundle to four waveguides 5 um apart."""
    c = gf.Component()
    gcs = []
    for k in range(4):
        g = c << gf.components.grating_coupler_elliptical_te(cross_section=xs)
        g.drotate(180)
        g.dmove((0.0, k * PITCH))
        gcs.append(g)
    dut = []
    for k in range(4):
        s = c << gf.components.straight(length=20.0, cross_section=xs)
        s.dmove((250.0, 175.0 + 5.0 * k))
        dut.append(s)
    routes = gf.routing.route_bundle(c, [g.ports["o1"] for g in gcs], [s.ports["o1"] for s in dut],
                                     cross_section=xs, separation=5.0, sort_ports=True)
    c.info["route_lengths"] = [round(float(r.length) * c.kcl.dbu, 3) for r in routes]
    return c


def part3():
    chip = demo_chip()
    chip.write_gds(os.path.join(TMP, "demo_chip.gds"))
    keep = [(1, 0), (2, 0), (47, 0), (49, 0), (45, 0), (41, 0), (99, 0)]
    labels = []
    it = chip.kdb_cell.begin_shapes_rec(chip.kcl.layer(10, 0))
    while not it.at_end():
        if it.shape().is_text():
            tx = it.shape().text.transformed(it.trans())
            labels.append({"text": tx.string, "x": tx.x * chip.kcl.dbu, "y": tx.y * chip.kcl.dbu})
        it.next()
    net = chip.get_netlist()
    comps = {}
    for v in net["instances"].values():
        comps[v["component"]] = comps.get(v["component"], 0) + 1
    OUT["chip"] = {"die": DIE, "bbox": [chip.dxmin, chip.dymin, chip.dxmax, chip.dymax], "outline": outlines(chip, keep),
                   "labels": labels, "top_instances": comps}
    f = fanin()
    f.write_gds(os.path.join(TMP, "fanin.gds"))
    ports = []
    for inst in f.insts:
        ports += ports_of(inst.ports)
    OUT["fanin"] = {"outline": outlines(f, [(1, 0), (2, 0)]), "ports": ports, "route_lengths": f.info["route_lengths"]}
    # bend facts for the text: vertices and length of the Euler and circular 90-degree bends of this cross-section
    be, bc = gf.components.bend_euler(cross_section=xs), gf.components.bend_circular(cross_section=xs)
    OUT["bends"] = {"euler": {"length": be.info["length"], "min_radius": be.info["min_bend_radius"],
                              "points": sum(len(p[0]) for p in outlines(be, [(1, 0)])["1/0"])},
                    "circular": {"length": bc.info["length"],
                                 "points": sum(len(p[0]) for p in outlines(bc, [(1, 0)])["1/0"])}}
    print(f"3. chip {comps}; labels {len(labels)}; fan-in route lengths {f.info['route_lengths']}; bends {OUT['bends']}; "
          f"{time.time() - T0:.0f} s")


def save_json():
    OUT["versions"] = {"gdsfactory": gf.__version__}
    with open(os.path.join(HERE, "ch33_gdsfactory.json"), "w", encoding="utf-8") as fh:
        json.dump(OUT, fh, separators=(",", ":"))


if __name__ == "__main__":
    parts = sys.argv[1:] or ["1", "3"]                     # "3" re-runs the floorplan only, keeping part 1's results
    jpath = os.path.join(HERE, "ch33_gdsfactory.json")
    if sys.argv[1:] and os.path.exists(jpath):
        OUT.update(json.load(open(jpath, encoding="utf-8")))
    code = 0
    try:
        if "1" in parts:
            part1_2(); save_json()
        if "3" in parts:
            part3(); save_json()
        print("wrote ch33_gdsfactory.json", f"{time.time() - T0:.0f} s")
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(code)                                         # do not wait for JAX's threads at shutdown
