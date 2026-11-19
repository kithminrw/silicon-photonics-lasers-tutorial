"""SiEPIC-Tools example for Chapter 33 (run in Docker: SiEPIC 0.5.31, siepic_ebeam_pdk 0.4.53, klayout 0.30.13).

    MSYS_NO_PATHCONV=1 docker exec -w /repo photonics-labs /opt/conda/envs/labs/bin/python figsrc/ch33_siepic.py

Places two of the EBeam PDK's grating couplers on the 127 um pitch, joins them with a Waveguide PCell drawn
from a path (what SiEPIC-Tools' "path to waveguide" does with paths on the Waveguide layer, 1/99), adds a test
label, runs the functional layout check and exports the netlist. Writes figsrc/ch33_siepic.json.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- listing starts (Section 33.3; keep in step with the chapter)
import pya  # KLayout's Python module, as SiEPIC-Tools uses it
import siepic_ebeam_pdk  # noqa: F401  registers the EBeam technology and libraries
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
# ---- listing ends

if __name__ == "__main__":
    comps = top.find_components()
    lines = [ln.strip() for ln in netlist.splitlines() if ln.strip() and not ln.strip().startswith(".param")]
    m = re.search(r"wg_length=([0-9.eE+-]+)", netlist)
    res = {"errors": errors, "components": [c.component for c in comps],
           "netlist_lines": lines, "wg_length_um": float(m.group(1)) * 1e6 if m else None,
           "wg_params": {k: str(v) for k, v in wg.pcell_parameters_by_name().items() if k in ("waveguide_type", "radius", "width")},
           "gc_bbox_um": [gc.dbbox().left, gc.dbbox().bottom, gc.dbbox().right, gc.dbbox().top]}
    with open(os.path.join(HERE, "ch33_siepic.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
