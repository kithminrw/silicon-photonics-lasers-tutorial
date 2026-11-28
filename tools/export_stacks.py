"""Export generic laser, SOA and VCSEL layer stacks to glTF (.glb) for Section 24.9 ("Inside the chip").

Unlike tools/export_3d.py, nothing here comes from a PDK: there is no open InP PDK with published layouts. Each model
is a short, cropped piece of a device, built from boxes and extruded polygons with the generic, illustrative layer
stacks the chapters already use, so that the 3D views and the 2D figures agree:

  ridge   Fabry-Perot ridge laser of Figure 24.1: the separate-confinement stack of Figure 23.3b (5 x 10 nm wells,
          10 nm barriers, 40 nm SCH layers), a 2 um p-InP ridge 1.80 um tall, etched to 0.35 um above the wells,
          p++ InGaAs cap 0.15 um, SiN passivation, BCB planarisation, Ti/Pt/Au contact with a pad arm on the BCB.
  bh      buried-heterostructure DFB laser: a 1.5 um mesa etched through the wells into the n-InP, regrown with
          semi-insulating Fe:InP, an InGaAsP grating (period 242 nm) above the wells, p-InP overgrowth, contact window.
  hetero  III-V-on-silicon laser of Table 27.1: 500 nm Si strip (0.5 um wide under the gain section, widening to 1.5 um),
          30 nm bonding oxide, 110 nm n-InP contact layer 12 um wide, 3 um mesa (300 nm MQW region, 1.5 um p-InP,
          100 nm p-InGaAs) tapering to a 0.6 um tip, n contacts beside the mesa, proton-implanted mesa edges.
  soa     output end of an angled-waveguide SOA (Figure 28.1): a 2.5 um ridge at 8 degrees to the facet normal, an
          unpumped InP window region 12 um long where the wells stop, and an AR coating on the facet.
  vcsel   oxide-aperture VCSEL of Figure 24.6, cut open: 34-pair n-DBR and 20-pair p-DBR (AlGaAs, n = 3.52 / 3.05 at
          850 nm, quarter-wave layers), a one-wavelength cavity with three 8 nm wells, a 30 nm AlAs layer oxidised
          to a 6 um aperture, a 20 um mesa and a ring contact.

Thicknesses are to scale (z up, micrometres); lengths and widths are cropped (a real laser is 250-1000 um long and
a few hundred micrometres wide; its substrate is thinned to about 100 um). Each model is written twice: assembled,
and "exploded", with the layer groups lifted apart. A manifest, _data/stacks3d.json, gives the page its legends.

Run from the repository root (needs numpy, trimesh and shapely only):
    python3 -I tools/export_stacks.py
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox
from trimesh.visual.material import PBRMaterial

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "models"

# material: (label, RGBA 0-1, metallic, role shown in the legend's tooltip)
MAT = {
    "pmetal":  ("p contact, Ti/Pt/Au", (0.95, 0.76, 0.33, 1.0), 0.85, "injects holes; ohmic on the p++ InGaAs"),
    "nmetal":  ("n contact, AuGe/Ni/Au", (0.86, 0.70, 0.36, 1.0), 0.85, "injects electrons"),
    "cap":     ("p++ InGaAs contact layer", (0.32, 0.20, 0.18, 1.0), 0.05, "narrow gap and heavy doping: a low-resistance contact"),
    "pinp":    ("p-InP cladding", (0.93, 0.74, 0.64, 1.0), 0.05, "confines the light from above and carries the holes"),
    "estop":   ("InGaAsP etch stop", (0.50, 0.40, 0.26, 1.0), 0.05, "stops the ridge etch at a fixed height"),
    "sch":     ("InGaAsP SCH and barriers", (0.46, 0.38, 0.22, 1.0), 0.05, "guides the light onto the wells and feeds them carriers"),
    "qw":      ("quantum wells", (0.85, 0.12, 0.10, 1.0), 0.05, "the gain: carriers recombine here and amplify the light"),
    "ninp":    ("n-InP buffer and cladding", (0.66, 0.73, 0.86, 1.0), 0.05, "confines the light from below and carries the electrons"),
    "sub":     ("n-InP substrate (cut short)", (0.50, 0.56, 0.68, 1.0), 0.05, "mechanical support, thinned to about 100 µm"),
    "sin":     ("SiN passivation", (0.86, 0.62, 0.25, 0.75), 0.05, "seals the etched surfaces and insulates them"),
    "bcb":     ("BCB planarisation", (0.80, 0.86, 0.80, 0.40), 0.0, "low-permittivity polymer: flat surface, low pad capacitance"),
    "feinp":   ("Fe:InP, semi-insulating", (0.58, 0.58, 0.56, 1.0), 0.05, "regrown beside the mesa: blocks current, buries the wells"),
    "grating": ("InGaAsP grating", (0.36, 0.28, 0.14, 1.0), 0.05, "DFB feedback: a period of 242 nm selects one wavelength"),
    "window":  ("InP window (no wells)", (0.80, 0.80, 0.80, 1.0), 0.05, "unpumped and transparent: the beam spreads before the facet"),
    "ar":      ("AR coating", (0.45, 0.85, 0.92, 0.45), 0.0, "anti-reflection layers on the facet"),
    "implant": ("proton-implanted p-InP", (0.70, 0.58, 0.88, 0.9), 0.05, "made resistive by H⁺ implantation: steers current to the centre"),
    "mqw":     ("MQW region", (0.85, 0.12, 0.10, 1.0), 0.05, "wells and barriers, 300 nm: the gain"),
    "nlayer":  ("n-InP contact layer", (0.66, 0.73, 0.86, 1.0), 0.05, "thin and wide: electrons flow sideways to the mesa"),
    "bond":    ("bonding oxide", (0.55, 0.75, 0.95, 0.5), 0.0, "30 nm of oxide joining the III–V to the silicon"),
    "si":      ("silicon waveguide", (0.47, 0.58, 0.76, 1.0), 0.05, "carries the light outside the gain section"),
    "ox":      ("oxide (BOX and fill)", (0.55, 0.75, 0.95, 0.22), 0.0, "buried oxide and the fill around the waveguide"),
    "sisub":   ("Si substrate (cut short)", (0.62, 0.70, 0.80, 1.0), 0.05, "the silicon wafer"),
    "gaas":    ("n-GaAs substrate (cut short)", (0.88, 0.90, 0.93, 1.0), 0.05, "the GaAs wafer"),
    "dbrh":    ("DBR, high-index AlGaAs", (0.86, 0.88, 0.92, 1.0), 0.05, "quarter-wave layers, n = 3.52: half of each mirror pair"),
    "dbrl":    ("DBR, low-index AlGaAs", (0.30, 0.36, 0.52, 1.0), 0.05, "quarter-wave layers, n = 3.05: the other half"),
    "cav":     ("AlGaAs cavity", (0.72, 0.66, 0.82, 1.0), 0.05, "one wavelength thick; the wells sit at its centre"),
    "alox":    ("aluminium oxide (oxidised AlAs)", (0.99, 0.98, 0.93, 1.0), 0.0, "insulating ring: funnels current and light into the aperture"),
    "alas":    ("AlAs aperture (unoxidised)", (0.35, 0.62, 0.86, 1.0), 0.05, "the 6 µm conducting disc left in the middle"),
}


class Model:
    def __init__(self, slug):
        self.slug, self.parts = slug, []     # (mesh, material key, group)

    def add(self, mesh, mat, group):
        self.parts.append((mesh, mat, group))

    def box(self, x0, x1, y0, y1, z0, z1, mat, group):
        if x1 - x0 <= 1e-9 or y1 - y0 <= 1e-9 or z1 - z0 <= 1e-9:
            return
        m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
        m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
        self.add(m, mat, group)

    def prism(self, poly, z0, z1, mat, group):
        """Extrude a shapely polygon (x, y) between z0 and z1."""
        if poly.is_empty or z1 - z0 <= 1e-9:
            return
        geoms = getattr(poly, "geoms", [poly])
        for p in geoms:
            m = trimesh.creation.extrude_polygon(p, z1 - z0)
            m.apply_translation([0, 0, z0])
            self.add(m, mat, group)

    def export(self, explode_dz, meta):
        entry = dict(meta, slug=self.slug)
        used = []
        for exploded in (False, True):
            sc = trimesh.Scene()
            meshes = {}
            for mesh, mat, grp in self.parts:
                mm = mesh.copy()
                if exploded:
                    mm.apply_translation([0, 0, grp * explode_dz])
                meshes.setdefault(mat, []).append(mm)
            for mat, ms in meshes.items():
                label, rgba, metal, role = MAT[mat]
                g = trimesh.util.concatenate(ms)
                g.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(
                    name=mat, baseColorFactor=[int(255 * c) for c in rgba], metallicFactor=metal,
                    roughnessFactor=0.4 if metal > 0.5 else 0.65, alphaMode="BLEND" if rgba[3] < 1 else "OPAQUE", doubleSided=True))
                sc.add_geometry(g, geom_name=mat)
                if mat not in used:
                    used.append(mat)
            if not exploded:
                (bx0, by0, bz0), (bx1, by1, bz1) = sc.bounds
            sc.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))   # glTF is y-up
            name = f"stack-{self.slug}{'-x' if exploded else ''}.glb"
            sc.export(OUT / name)
            entry["file_x" if exploded else "file"] = name
            entry["kb_x" if exploded else "kb"] = round((OUT / name).stat().st_size / 1024)
        # legend in stacking order of first appearance from the bottom up, metals last
        order = sorted(used, key=lambda k: (MAT[k][2] > 0.5, min(p[0].bounds[0][2] for p in self.parts if p[1] == k)))
        entry["layers"] = [{"key": k, "label": MAT[k][0], "role": MAT[k][3],
                            "colour": "#%02x%02x%02x" % tuple(int(255 * c) for c in MAT[k][1][:3])} for k in order]
        entry["size_um"] = [round(bx1 - bx0, 1), round(by1 - by0, 1), round(bz1 - bz0, 2)]
        print(f"{self.slug:7s} {entry['size_um']} um  {entry['kb']} kB / exploded {entry['kb_x']} kB  layers={len(order)}")
        return entry


# ------------------------------------------------------------------------------------------------ helpers
def sch_mqw(m, x0, x1, y0, y1, z, group, nw=5, tw=0.010, tb=0.010, ts=0.040):
    """Separate-confinement stack of Figure 23.3b from height z; returns its top."""
    m.box(x0, x1, y0, y1, z, z + ts, "sch", group); z += ts
    for k in range(nw):
        m.box(x0, x1, y0, y1, z, z + tw, "qw", group); z += tw
        if k < nw - 1:
            m.box(x0, x1, y0, y1, z, z + tb, "sch", group); z += tb
    m.box(x0, x1, y0, y1, z, z + ts, "sch", group)
    return z + ts


# ------------------------------------------------------------------------------------------------ models
def ridge():
    m = Model("ridge")
    L, Y, RW = 30.0, 8.0, 2.0                       # length, half width, ridge width
    m.box(0, L, -Y, Y, -4.4, -4.0, "nmetal", 0)
    m.box(0, L, -Y, Y, -4.0, -0.5, "sub", 1)
    m.box(0, L, -Y, Y, -0.5, 0.0, "ninp", 2)
    zt = sch_mqw(m, 0, L, -Y, Y, 0.0, 3)            # 0.17
    zr = zt + 0.33
    m.box(0, L, -Y, Y, zt, zr, "pinp", 4)
    m.box(0, L, -Y, Y, zr, zr + 0.02, "estop", 4); zr += 0.02          # residual cladding 0.35 um in all
    ztop = zt + 1.80
    m.box(0, L, -RW / 2, RW / 2, zr, ztop, "pinp", 5)
    m.box(0, L, -RW / 2, RW / 2, ztop, ztop + 0.15, "cap", 5); ztop += 0.15
    t = 0.2                                          # SiN on the floor and the ridge walls (open on the ridge top)
    for s in (-1, 1):
        m.box(0, L, *sorted((s * RW / 2, s * Y)), zr, zr + t, "sin", 6)
        m.box(0, L, *sorted((s * RW / 2, s * (RW / 2 + t))), zr + t, ztop, "sin", 6)
        m.box(0, L, *sorted((s * (RW / 2 + t), s * Y)), zr + t, ztop, "bcb", 7)
    m.box(0, L, -3.0, 3.0, ztop, ztop + 0.3, "pmetal", 8)
    m.box(12, L, 3.0, 7.0, ztop, ztop + 0.3, "pmetal", 8)            # arm towards a bond pad on the BCB
    return m.export(0.9, dict(
        title="Ridge-waveguide Fabry–Pérot laser (InP)", short="ridge laser",
        blurb="The laser of Figure 24.1 and Worked Example 24.1. The p-InP ridge is etched down to an etch-stop layer 0.35 µm above the wells, which stay unetched under the whole chip; the ridge's small index step guides the light sideways, and the current spreads a little beyond it. BCB fills the etched area so the contact can cross it to a pad.",
        orbit="-75deg 68deg 75%"))


def bh():
    m = Model("bh")
    L, Y, MW = 24.0, 8.0, 1.5
    PER = 0.2422                                     # 1550 nm / (2 x 3.2)
    m.box(0, L, -Y, Y, -4.4, -4.0, "nmetal", 0)
    m.box(0, L, -Y, Y, -4.0, -1.0, "sub", 1)
    m.box(0, L, -Y, Y, -1.0, -0.8, "ninp", 2)
    m.box(0, L, -MW / 2, MW / 2, -0.8, 0.0, "ninp", 2)                   # mesa: etched 0.8 um into the n-InP
    zt = sch_mqw(m, 0, L, -MW / 2, MW / 2, 0.0, 3)
    m.box(0, L, -MW / 2, MW / 2, zt, zt + 0.10, "pinp", 4)
    zg = zt + 0.10
    n = int(L / PER)
    for k in range(n):                                                   # grating teeth, overgrown with p-InP
        m.box(k * PER, k * PER + PER / 2, -MW / 2, MW / 2, zg, zg + 0.05, "grating", 4)
        m.box(k * PER + PER / 2, (k + 1) * PER, -MW / 2, MW / 2, zg, zg + 0.05, "pinp", 4)
    zm = zg + 0.05 + 0.15
    m.box(0, L, -MW / 2, MW / 2, zg + 0.05, zm, "pinp", 4)
    for s in (-1, 1):
        m.box(0, L, *sorted((s * MW / 2, s * Y)), -0.8, zm, "feinp", 3)
    m.box(0, L, -Y, Y, zm, zm + 1.8, "pinp", 5); zm += 1.8
    m.box(0, L, -Y, Y, zm, zm + 0.2, "cap", 6); zm += 0.2
    for s in (-1, 1):
        m.box(0, L, *sorted((s * 2.0, s * Y)), zm, zm + 0.2, "sin", 7)
    m.box(0, L, -2.0, 2.0, zm, zm + 0.2, "pmetal", 8)
    m.box(0, L, -6.0, 6.0, zm + 0.2, zm + 0.6, "pmetal", 8)
    return m.export(0.9, dict(
        title="Buried-heterostructure DFB laser (InP)", short="buried heterostructure",
        blurb="A mesa 1.5 µm wide is etched through the wells and regrown on both sides with semi-insulating Fe:InP, so the active region is buried in InP on every side: no exposed surface, current only through the mesa, strong guiding. An InGaAsP grating above the wells, period 242 nm, gives the feedback of a DFB laser (Chapter 26).",
        orbit="-75deg 68deg 75%"))


def hetero():
    m = Model("hetero")
    L, Y, XG = 50.0, 7.0, 20.0                       # length, half width, end of the gain section
    TSI, TB = 0.5, 0.03
    m.box(0, L, -Y, Y, -3.0, -2.0, "sisub", 0)
    m.box(0, L, -Y, Y, -2.0, 0.0, "ox", 1)
    wsi = lambda x: 0.5 if x <= XG else 0.5 + (x - XG) / (L - XG) * 1.0
    si = Polygon([(0, -0.25), (XG, -0.25), (L, -wsi(L) / 2), (L, wsi(L) / 2), (XG, 0.25), (0, 0.25)])
    m.prism(si, 0, TSI, "si", 2)
    m.prism(sbox(0, -Y, L, Y).difference(si), 0, TSI, "ox", 2)
    m.box(0, L, -Y, Y, TSI, TSI + TB, "bond", 3)
    z = TSI + TB
    m.box(0, L, -6.0, 6.0, z, z + 0.11, "nlayer", 4); z += 0.11
    wm = lambda x: 3.0 if x <= XG else 3.0 - (x - XG) / (L - XG) * 2.4
    mesa = Polygon([(0, -1.5), (XG, -1.5), (L, -wm(L) / 2), (L, wm(L) / 2), (XG, 1.5), (0, 1.5)])
    m.prism(mesa, z, z + 0.30, "mqw", 5); zq = z + 0.30
    # p-InP: in the gain section its outer 0.75 um on each side is proton-implanted (top part)
    taper = mesa.intersection(sbox(XG, -Y, L, Y))
    m.prism(taper, zq, zq + 1.5, "pinp", 6)
    m.box(0, XG, -0.75, 0.75, zq, zq + 1.5, "pinp", 6)
    for s in (-1, 1):
        y0, y1 = sorted((s * 0.75, s * 1.5))
        m.box(0, XG, y0, y1, zq, zq + 0.3, "pinp", 6)
        m.box(0, XG, y0, y1, zq + 0.3, zq + 1.5, "implant", 6)
    zc = zq + 1.5
    m.prism(mesa, zc, zc + 0.10, "cap", 7); zc += 0.10
    # SiN on the mesa walls and the n-layer between the mesa and the n contacts; contacts in the gain section
    t = 0.15
    for s in (-1, 1):
        wall = Polygon([(0, s * 1.5), (XG, s * 1.5), (L, s * wm(L) / 2), (L, s * (wm(L) / 2 + t)), (XG, s * (1.5 + t)), (0, s * (1.5 + t))])
        m.prism(wall, z, zc, "sin", 8)
        m.box(0, L, *sorted((s * (1.5 + t), s * 3.4)), z, z + t, "sin", 8)
        m.box(0, XG - 1, *sorted((s * 3.6, s * 5.6)), z, z + 0.5, "nmetal", 9)
    m.box(0, XG - 1, -1.4, 1.4, zc, zc + 0.4, "pmetal", 9)
    return m.export(0.8, dict(
        title="III–V-on-silicon laser: gain section and taper", short="III–V on silicon",
        blurb="The stack of Table 27.1. Under the gain section (front, with contacts) the silicon strip is 0.5 µm wide and the light lives in the III–V mesa; along the taper the mesa narrows to a 0.6 µm tip while the silicon widens to 1.5 µm, and the light moves down into the silicon (Figure 27.2). Both contacts are on top: electrons flow sideways through the thin n-InP layer, and implanted mesa edges steer the holes to the centre.",
        orbit="-62deg 64deg 80%"))


def soa():
    m = Model("soa")
    L, Y, RW, ANG, XW = 40.0, 10.0, 2.5, 8.0, 12.0
    ta = math.tan(math.radians(ANG)); hw = RW / 2 / math.cos(math.radians(ANG))
    yc = lambda x: (x - L / 2) * ta
    m.box(0, L, -Y, Y, -4.4, -4.0, "nmetal", 0)
    m.box(0, L, -Y, Y, -4.0, -0.5, "sub", 1)
    m.box(0, L, -Y, Y, -0.5, 0.0, "ninp", 2)
    zt = sch_mqw(m, XW, L, -Y, Y, 0.0, 3)                                 # wells stop 12 um before the facet
    m.box(0, XW, -Y, Y, 0.0, zt, "window", 3)
    zr = zt + 0.33
    m.box(0, L, -Y, Y, zt, zr, "pinp", 4)
    m.box(0, L, -Y, Y, zr, zr + 0.02, "estop", 4); zr += 0.02
    ztop = zt + 1.80
    ridge = Polygon([(0, yc(0) - hw), (L, yc(L) - hw), (L, yc(L) + hw), (0, yc(0) + hw)])
    m.prism(ridge, zr, ztop, "pinp", 5)
    m.prism(ridge, ztop, ztop + 0.15, "cap", 5); ztop += 0.15
    t = 0.2
    floor = sbox(0, -Y, L, Y).difference(ridge)
    m.prism(floor, zr, zr + t, "sin", 6)
    walls = ridge.buffer(t, join_style=2).intersection(sbox(0, -Y, L, Y)).difference(ridge)
    m.prism(walls, zr + t, ztop, "sin", 6)
    m.prism(floor.difference(ridge.buffer(t, join_style=2)), zr + t, ztop, "bcb", 7)
    pm = Polygon([(XW + 2, yc(XW + 2) - 2.5), (L, yc(L) - 2.5), (L, yc(L) + 2.5), (XW + 2, yc(XW + 2) + 2.5)])
    m.prism(pm, ztop, ztop + 0.3, "pmetal", 8)
    m.box(-0.27, 0, -Y, Y, -4.0, ztop, "ar", 9)
    return m.export(0.9, dict(
        title="Angled-waveguide SOA: the output facet", short="SOA facet",
        blurb="The output end of the SOA of Figure 28.1. The ridge crosses the chip at 8° to the facet normal, so what the AR coating fails to suppress is reflected away from the waveguide. The wells stop 12 µm before the facet: in the unpumped InP window the beam spreads, so even less of the reflection finds its way back. The contact ends before the window.",
        orbit="-62deg 60deg 80%"))


def vcsel(seg=56):
    m = Model("vcsel")
    lam, nh, nl = 0.850, 3.52, 3.05
    th, tl = lam / (4 * nh), lam / (4 * nl)
    R_MESA, R_OUT, R_AP = 10.0, 16.0, 3.0
    wedge = Polygon([(0, 0)] + [(40 * math.cos(math.radians(a)), 40 * math.sin(math.radians(a))) for a in np.linspace(0, 270, 28)])   # 270-degree cut-away

    def disc(r, r_in=0.0):
        p = Point(0, 0).buffer(r, resolution=seg // 4)
        if r_in > 0:
            p = p.difference(Point(0, 0).buffer(r_in, resolution=seg // 4))
        return p.intersection(wedge)

    m.prism(disc(R_OUT), -1.5, 0.0, "gaas", 0)
    z = 0.0
    for k in range(34):                                                    # n-DBR, wide
        m.prism(disc(R_OUT), z, z + th, "dbrh", 1); z += th
        m.prism(disc(R_OUT), z, z + tl, "dbrl", 1); z += tl
    zc = z; tc = lam / 3.40                                                # one-wavelength cavity, three 8 nm wells in the middle
    zw = zc + tc / 2 - (3 * 0.008 + 2 * 0.010) / 2
    m.prism(disc(R_MESA), zc, zw, "cav", 2)
    for k in range(3):
        m.prism(disc(R_MESA), zw, zw + 0.008, "qw", 2); zw += 0.008
        if k < 2:
            m.prism(disc(R_MESA), zw, zw + 0.010, "cav", 2); zw += 0.010
    m.prism(disc(R_MESA), zw, zc + tc, "cav", 2)
    z = zc + tc
    for k in range(20):                                                    # p-DBR in the mesa; the first low layer holds the AlAs
        m.prism(disc(R_MESA), z, z + th, "dbrh", 3); z += th
        if k == 0:
            m.prism(disc(R_MESA), z, z + 0.020, "dbrl", 3)
            m.prism(disc(R_AP), z + 0.020, z + 0.050, "alas", 3)
            m.prism(disc(R_MESA, R_AP), z + 0.020, z + 0.050, "alox", 3)
            m.prism(disc(R_MESA), z + 0.050, z + tl, "dbrl", 3)
        else:
            m.prism(disc(R_MESA), z, z + tl, "dbrl", 3)
        z += tl
    m.prism(disc(8.0, 4.0), z, z + 0.3, "pmetal", 4)
    m.prism(disc(15.0, 12.0), zc, zc + 0.3, "nmetal", 4)
    return m.export(0.6, dict(
        title="Oxide-aperture VCSEL, cut open", short="VCSEL",
        blurb="The VCSEL of Figure 24.6 and Worked Example 24.2, with a quarter cut away. Under 20 p-type mirror pairs a one-wavelength cavity holds three wells, and below it 34 n-type pairs. One AlAs layer, oxidised in from the wall of the 20 µm mesa, leaves a 6 µm conducting aperture that funnels current and light into the centre; the light leaves through the ring contact.",
        orbit="45deg 64deg 85%"))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    entries = [ridge(), bh(), hetero(), soa(), vcsel()]
    for e in entries:
        e["credit"] = "Generic, illustrative stack drawn for this tutorial (not any company's process); thicknesses to scale, length and width cut short."
    (ROOT / "_data" / "stacks3d.json").write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote _data/stacks3d.json")
