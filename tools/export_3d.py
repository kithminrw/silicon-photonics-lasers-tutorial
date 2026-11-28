"""Export open-PDK photonic devices to glTF (.glb) for the "PDK Devices in 3D" page.

Each device is drawn by its own PDK's gdsfactory implementation, every layer is extruded to the
thickness and height given by that PDK's layer stack (true scale, no vertical exaggeration; the page
can stretch the vertical axis), and the result is written to assets/models/<slug>.glb with one named
material per layer. Wafer-wide layers (substrate, BOX, cladding) are left out; a thin translucent plate
marks the top of the buried oxide. A manifest (_data/devices3d.json) records each device's
size, layers and colours for the page legend.

Run from the repository root:
    .venv/bin/python tools/export_3d.py                    # SiEPIC EBeam (ubcpdk) and CORNERSTONE (cspdk)
    .venv-lxt/bin/python tools/export_3d.py --pdk lxt      # Luxtelligence TFLN (lnoi400, its own venv)
    python tools/export_3d.py --pdk ebeam                 # SiEPIC Bragg grating and contra-DC (KLayout PCells)
The "ebeam" group needs siepic_ebeam_pdk and klayout beside ubcpdk; it was run in the photonics-labs Docker
container (gdsfactory 9.51, ubcpdk 3.3.5, siepic_ebeam_pdk 0.4.53, klayout 0.30.13):
    MSYS_NO_PATHCONV=1 docker exec -w /repo photonics-labs /opt/conda/envs/labs/bin/python tools/export_3d.py --pdk ebeam
The VTT 3 µm SOI PDK (gvtt 0.1.0, checked Nov 2026) still publishes no layer stack, so its devices are not
exported yet. The CORNERSTONE laser_* cells are not exported either: they hold only a silicon taper and
laser-site marker layers, with no stack levels and no laser die geometry.
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "models"

# colours by material (RGBA 0-1), shared by every PDK so the same material looks the same everywhere
MATERIAL_COLOURS = {
    "si": (0.62, 0.70, 0.80, 1.0),        # crystalline silicon: blue-grey
    "si_slab": (0.47, 0.56, 0.68, 1.0),   # partially etched silicon slab
    "si_grating": (0.52, 0.62, 0.76, 1.0),
    "sin": (0.86, 0.66, 0.30, 1.0),       # silicon nitride: amber
    "ln": (0.93, 0.55, 0.62, 0.92),       # lithium niobate: rose
    "ge": (0.45, 0.45, 0.50, 1.0),
    "tin": (0.80, 0.55, 0.25, 1.0),       # heater: bronze
    "al": (0.83, 0.85, 0.88, 1.0),        # aluminium / gold-free metal: light grey
    "au": (0.95, 0.76, 0.33, 1.0),
    "box": (0.55, 0.75, 0.95, 0.18),      # top of the buried oxide (translucent)
}
METALLIC = {"tin": 0.6, "al": 0.9, "au": 0.9}


def material_key(layer_name: str, material: str | None) -> str:
    m = (material or "").lower()
    n = layer_name.lower()
    if "slab" in n and m.startswith("si") and "n" not in m[2:3]:
        return "si_slab"
    if "grating" in n and m == "si":
        return "si_grating"
    if m in ("sin", "si3n4", "nitride") or "nitride" in n:
        return "sin"
    if m in ("ln", "linbo3", "lithium_niobate") or "ln" == n[:2]:
        return "ln"
    if m == "ge":
        return "ge"
    if m == "tin" or "heater" in n:
        return "tin"
    if m in ("au", "gold"):
        return "au"
    if m in ("aluminum", "aluminium", "al", "cu", "copper", "metal") or "metal" in n or "pad" in n or "router" in n:
        return "al"
    return "si"


def export(component, layer_stack, slug: str, meta: dict, box_margin: float = 2.0) -> dict:
    """Extrude `component` with `layer_stack`, recolour, add the BOX plate and write slug.glb."""
    # leave out the wafer-wide layers: they would bury the device in a block
    keep = {k: v for k, v in layer_stack.layers.items()
            if k.lower() not in ("substrate", "box", "clad", "cladding", "oxide", "field", "wafer")}
    ls = layer_stack.model_copy(update={"layers": keep})
    scene = component.to_3d(layer_stack=ls)

    out = trimesh.Scene()
    legend = {}
    for name, geom in scene.geometry.items():
        lname = name.rsplit("_", 1)[0] if name[-1].isdigit() else name
        lv = keep.get(lname)
        key = material_key(lname, getattr(lv, "material", None) if lv else None)
        rgba = MATERIAL_COLOURS[key]
        mat = PBRMaterial(name=lname, baseColorFactor=[int(255 * c) for c in rgba],
                          metallicFactor=METALLIC.get(key, 0.05), roughnessFactor=0.45 if key in METALLIC else 0.6,
                          alphaMode="BLEND" if rgba[3] < 1 else "OPAQUE", doubleSided=True)
        g = geom.copy()
        g.visual = trimesh.visual.TextureVisuals(material=mat)
        out.add_geometry(g, geom_name=name)
        if lv is not None:
            legend[lname] = {"colour": "#%02x%02x%02x" % tuple(int(255 * c) for c in rgba[:3]),
                             "thickness_um": round(float(lv.thickness), 3), "zmin_um": round(float(lv.zmin), 3),
                             "material": getattr(lv, "material", None)}

    # translucent plate at the top of the buried oxide, a little larger than the device
    (x0, y0, z0), (x1, y1, z1) = out.bounds
    plate = trimesh.creation.box(extents=[x1 - x0 + 2 * box_margin, y1 - y0 + 2 * box_margin, 0.04])
    plate.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, -0.02])
    rgba = MATERIAL_COLOURS["box"]
    plate.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(
        name="box_top", baseColorFactor=[int(255 * c) for c in rgba], metallicFactor=0.0, roughnessFactor=0.9,
        alphaMode="BLEND", doubleSided=True))
    out.add_geometry(plate, geom_name="box_top")

    # glTF is Y-up: rotate so that the wafer normal (z) points up in the viewer
    out.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{slug}.glb"
    out.export(path)
    (bx0, by0, bz0), (bx1, by1, bz1) = scene.bounds
    entry = dict(meta, slug=slug, file=f"{slug}.glb", size_um=[round(float(bx1 - bx0), 2), round(float(by1 - by0), 2)],
                 height_um=round(float(bz1 - bz0), 3), layers=legend, kb=round(path.stat().st_size / 1024))
    print(f"{slug:32s} {entry['size_um']} µm  {entry['kb']} kB  layers={list(legend)}")
    return entry


# ----------------------------------------------------------------------------------------------- devices
# Credits come from each PDK's documentation; papers are keys in _data/references.yml.

def siepic_ebeam():
    from ubcpdk import PDK
    PDK.activate()
    ls = PDK.layer_stack
    pdk = dict(pdk="SiEPIC EBeam PDK", platform="220 nm SOI, 1550 nm, electron-beam lithography",
               pdk_url="https://github.com/SiEPIC/SiEPIC_EBeam_PDK", via="ubcpdk (gdsfactory)", licence="MIT")
    items = [
        ("ebeam_y_1550", "siepic-ybranch", "Y-branch splitter",
         "Y. Zhang, S. Yang, A. E.-J. Lim, G.-Q. Lo, C. Galland, T. Baehr-Jones and M. Hochberg", ["zhang2013"],
         "A 50/50 splitter whose taper shape was optimised by particle-swarm optimisation in 3D FDTD; about 0.3 dB insertion loss."),
        ("ebeam_gc_te1550", "siepic-gc-te1550", "Focusing sub-wavelength grating coupler (TE, 1550 nm)",
         "Yun Wang, Lukas Chrostowski et al. (UBC)", ["wang2014gc"],
         "A fully etched, focusing grating coupler whose teeth are sub-wavelength gratings, so a single etch gives a high efficiency and low back-reflection."),
        ("ebeam_bdc_te1550", "siepic-bdc", "Broadband directional coupler",
         "Zeqin Lu, Han Yun, Yun Wang, Zhitian Chen, Fan Zhang, Nicolas A. F. Jaeger and Lukas Chrostowski", ["lu2015bdc"],
         "A 3 dB coupler made of two waveguides of different widths, whose phase control flattens the split ratio over a wide band."),
        ("ebeam_adiabatic_te1550", "siepic-adiabatic", "Adiabatic 3 dB coupler",
         "Han Yun et al. (UBC)", ["yun2013adiabatic"],
         "A 2 × 2 splitter that converts the input mode slowly into the even or odd supermode, so its split ratio barely depends on wavelength."),
        ("ebeam_crossing4", "siepic-crossing", "Waveguide crossing",
         "Wei Shi (UBC, 2011), after P. Sanchis et al.", ["sanchis2009"],
         "Elliptical mode expanders widen the mode before the crossing so it diffracts less; under 0.2 dB loss and below −40 dB crosstalk."),
    ]
    out = []
    for cell, slug, title, by, refs, blurb in items:
        out.append(export(PDK.get_component(cell), ls, slug, dict(pdk, cell=cell, title=title, designers=by, refs=refs, blurb=blurb)))
    # a parametric cell from the gdsfactory implementation
    c = PDK.get_component("ring_single_heater")
    out.append(export(c, ls, "siepic-ring-heater", dict(pdk, cell="ring_single_heater", title="Ring resonator with a TiN heater",
                      designers="gdsfactory ubcpdk contributors (parametric cell)", refs=["ubcpdk", "bogaerts2012"],
                      blurb="An all-pass ring drawn by the PDK's parametric cell, with a titanium-nitride heater above it for thermal tuning and metal routing to its pads.")))
    return out


def siepic_ebeam_pcells():
    """SiEPIC EBeam cells that ubcpdk does not implement, drawn by the PDK's own KLayout PCells.

    The PCell runs in KLayout (importing siepic_ebeam_pdk registers its "EBeam" library), the result is
    written to a temporary GDS file and read into gdsfactory, and it is then extruded with ubcpdk's layer
    stack, exactly like the other SiEPIC devices (silicon is layer 1/0 in both). The parameters are the
    PCell defaults, written out so that a change of default in a later PDK release cannot change the model
    silently; for the contra-DC they are also the first design of the PDK's compact-model table
    (CML/EBeam/source_data/contraDC/contraDC.xml). Credits: the PCell headers and version history, and the
    PDK wiki's "Component Library description" for the papers.
    """
    import importlib.metadata
    import tempfile

    import gdsfactory as gf
    import pya
    import siepic_ebeam_pdk  # noqa: F401  (registers the EBeam PCell libraries)
    from ubcpdk import PDK
    PDK.activate()
    pdk = dict(pdk="SiEPIC EBeam PDK", platform="220 nm SOI, 1550 nm, electron-beam lithography",
               pdk_url="https://github.com/SiEPIC/SiEPIC_EBeam_PDK", licence="MIT",
               via="its own KLayout parametric cell (siepic_ebeam_pdk %s)" % importlib.metadata.version("siepic_ebeam_pdk"))
    items = [
        ("ebeam_bragg_te1550",
         dict(number_of_periods=300, grating_period=0.317, corrugation_width=0.05, misalignment=0.0,
              sinusoidal=False, wg_width=0.5),
         "siepic-bragg", "Waveguide Bragg grating",
         "Lukas Chrostowski (UBC), parametric cell (2015); setting κ by sidewall misalignment from Xu Wang et al. "
         "(UBC and Lumerical)", ["wang2014bragg"],
         "A 500 nm strip whose sidewalls step in and out by 50 nm every half period: 300 periods of 317 nm (95 µm) "
         "that reflect a band near 1550 nm back down the guide. Offsetting the teeth of one sidewall against the other "
         "(the cell's misalignment parameter) sets how strongly it reflects.",
         [["Chapter 13", "/part-3/ch13/"]]),
        ("contra_directional_coupler",
         dict(number_of_periods=1000, grating_period=0.316, gap=0.1, corrugation1_width=0.05,
              corrugation2_width=0.025, AR=True, sinusoidal=False, wg1_width=0.56, wg2_width=0.44, sbend=True,
              sbend_r=15.0, sbend_length=11.0, apodization_index=10.0, port_w=0.5, rib=False, metal=False),
         "siepic-contradc", "Contra-directional coupler (add-drop filter)",
         "Mustafa Hammood (UBC), parametric cell; the device and its anti-reflection layout from Wei Shi et al. (UBC)", ["shi2013cdc", "shi2013cwdm"],
         "Two strips, 560 and 440 nm wide with a 100 nm gap, corrugated over 1000 periods of 316 nm (316 µm): the "
         "grating reflects one C-band channel from the forward mode of one guide into the backward mode of the other, an "
         "add-drop filter with no free spectral range. Each guide's two sidewalls are offset by half a period to cancel "
         "its own reflection, and a Gaussian apodisation leaves visible teeth (sidewall steps of up to 50 and 25 nm) only "
         "in the middle 80 µm or so.",
         [["Chapter 13 (Section 13.7)", "/part-3/ch13/#fig-13-7"], ["Chapter 14", "/part-3/ch14/"]]),
    ]
    out = []
    for cell, params, slug, title, by, refs, blurb, chapters in items:
        ly = pya.Layout()
        ly.dbu = 0.001
        ly.technology_name = "EBeam"
        pc = ly.create_cell(cell, "EBeam", params)
        if pc is None:
            print("  no PCell", cell)
            continue
        top = ly.create_cell(slug.replace("-", "_"))
        top.insert(pya.CellInstArray(pc.cell_index(), pya.Trans()))
        top.flatten(True)
        with tempfile.TemporaryDirectory() as tmp:
            gds = pathlib.Path(tmp) / f"{slug}.gds"
            top.write(str(gds))
            comp = gf.import_gds(gds)
        out.append(export(comp, PDK.layer_stack, slug, dict(pdk, cell=cell, title=title, designers=by, refs=refs,
                                                             blurb=blurb, chapters=chapters, params=params)))
    return out


def cornerstone():
    out = []
    from cspdk.si220 import PDK as SI
    SI.activate()
    base = dict(pdk="CORNERSTONE PDK", pdk_url="https://github.com/gdsfactory/cspdk", via="cspdk (gdsfactory)", licence="MIT")
    for cell, slug, title, blurb in [
        ("grating_coupler_rectangular_rib", "cs-si220-gc-rib", "Shallow-etch grating coupler (Si 220 nm)",
         "A rectangular grating partially etched into the 220 nm film, sitting on the 100 nm slab of a rib waveguide."),
        ("mmi2x2_rib", "cs-si220-mmi2x2-rib", "2 × 2 MMI coupler, rib waveguides (Si 220 nm)",
         "A multimode-interference coupler in rib waveguides; the 100 nm slab around the ridge is the partial etch."),
    ]:
        out.append(export(SI.get_component(cell), SI.layer_stack, slug,
                          dict(base, platform="220 nm SOI (strip and rib)", cell=cell, title=title,
                               designers="CORNERSTONE platform cells, gdsfactory implementation", refs=["cspdk"], blurb=blurb)))
    from cspdk.sin300 import PDK as SN
    SN.activate()
    for cell, slug, title, blurb in [
        ("mmi1x2", "cs-sin300-mmi1x2", "1 × 2 MMI splitter (SiN 300 nm)",
         "The same building block in 300 nm silicon nitride: the lower index contrast makes everything wider and longer."),
        ("grating_coupler_elliptical", "cs-sin300-gc", "Elliptical grating coupler (SiN 300 nm)",
         "A focusing grating coupler in silicon nitride."),
    ]:
        out.append(export(SN.get_component(cell), SN.layer_stack, slug,
                          dict(base, platform="300 nm silicon nitride", cell=cell, title=title,
                               designers="CORNERSTONE platform cells, gdsfactory implementation", refs=["cspdk"], blurb=blurb)))
    return out


def luxtelligence():
    try:
        import lnoi400
    except ImportError:
        print("lnoi400 not installed: skipping the Luxtelligence devices")
        return []
    from lnoi400 import PDK
    PDK.activate()
    base = dict(pdk="Luxtelligence LNOI400 PDK", pdk_url="https://github.com/Luxtelligence/lxt_pdk_gf", via="lnoi400 (gdsfactory)",
                licence="MIT", platform="thin-film lithium niobate on insulator (LNOI)")
    out = []
    cells = sorted(PDK.cells.keys())
    print("lnoi400 cells:", cells)
    for cell, slug, title, blurb in [
        ("directional_coupler_balanced", "lxt-dc", "Directional coupler (TFLN)",
         "Two lithium niobate ridge waveguides brought close together over a shared 200 nm slab."),
        ("mmi2x2_optimized1550", "lxt-mmi2x2", "2 × 2 MMI coupler (TFLN)",
         "A multimode-interference coupler etched halfway into a 400 nm lithium niobate film, so the ridge sits on a 200 nm slab."),
        ("gc_focusing_1550", "lxt-gc", "Focusing grating coupler (TFLN)", "A focusing grating coupler in thin-film lithium niobate."),
    ]:
        if cell not in cells:
            print("  no cell", cell)
            continue
        out.append(export(PDK.get_component(cell), PDK.layer_stack, slug,
                          dict(base, cell=cell, title=title, designers="Luxtelligence PDK cells, gdsfactory implementation",
                               refs=["lxtpdk"], blurb=blurb)))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdk", default="siepic,cornerstone",
                    help="comma-separated: siepic, cornerstone (main .venv), ebeam (needs siepic_ebeam_pdk + klayout), lxt (.venv-lxt)")
    args = ap.parse_args()
    manifest_path = ROOT / "_data" / "devices3d.json"   # read by devices-3d.md
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    run = {"siepic": siepic_ebeam, "ebeam": siepic_ebeam_pcells, "cornerstone": cornerstone, "lxt": luxtelligence}
    new = [d for name in args.pdk.split(",") for d in run[name.strip()]()]
    slugs = {d["slug"] for d in new}
    manifest = [d for d in manifest if d["slug"] not in slugs] + new
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print("wrote", manifest_path, len(manifest), "devices")
