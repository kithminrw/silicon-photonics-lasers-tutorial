"""Export generic, explorable 3D models of the passive and active devices of the chapters (glTF, .glb).

Like tools/export_stacks.py, nothing here comes from a PDK (the PDK devices have their own gallery): each model is a
learning concept built from boxes, extruded outlines and solids of revolution, with the dimensions the chapters
use, so that the 3D views and the 2D figures agree. Thicknesses are to scale (z up, micrometres); lengths and widths
are cut short where a real device is long. Every waveguide is drawn as one merged outline before it is extruded, so
straight pieces, bends, tapers and couplers always join.

  waveguides  Ch 6   Si strip, Si rib and SiN strip side by side
  routing     Ch 8   a crossing with multimode expanders, a 90-degree bend and a taper
  dc          Ch 9   directional coupler: S-bends, a 200 nm gap, 10 um of coupling
  mmi         Ch 10  1 x 2 MMI, 6 um wide and 32.8 um long, with tapered access guides
  mzi         Ch 11  unbalanced MZI: Y-branches, a delay loop, a TiN heater on the other arm
  ring        Ch 12  add-drop ring, R = 10 um, 200 nm gaps, a TiN heater with pads
  bragg       Ch 13  sidewall Bragg grating, period 317 nm, quarter-wave shifted
  gc          Ch 15  focusing grating coupler, 70 nm shallow etch, period 607 nm, with the beam at 8 degrees
  edge        Ch 16  inverse-taper edge coupler at a facet, with the expanding beam
  faml        Ch 17  facet-attached microlenses on a chip facet and on a fibre end, with the collimated beam between
  tfln        Ch 19, 20  thin-film lithium niobate ridge between gold electrodes
  mzm         Ch 20  silicon travelling-wave MZM segment: two PN arms under ground-signal-ground electrodes
  ringmod     Ch 20  depletion ring modulator, R = 7.2 um, junction on 80 % of the ring
  ecl         Ch 26  III-V/Si external-cavity laser: RSOA, edge coupler, phase heater, two Vernier rings, loop mirror
  flipchip    Ch 27  a laser flip-chip bonded into an etched pocket, butt-coupled to a silicon waveguide

Run from the repository root (numpy, trimesh and shapely):  python3 -I tools/export_devices.py [names]
Names export only those models; the manifest _data/stacks3d.json keeps every other entry.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.affinity import rotate as srot
from shapely.ops import unary_union

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from export_stacks import MAT, Model, OUT, ROOT   # noqa: E402

MAT.update({
    "sinwg":  ("silicon nitride waveguide", (0.90, 0.70, 0.38, 1.0), 0.05, "low-loss core: 1.2 × 0.4 µm"),
    "ln":     ("lithium niobate film", (0.93, 0.58, 0.66, 1.0), 0.05, "x-cut, 600 nm: the Pockels effect changes its index"),
    "gold":   ("gold electrodes", (0.98, 0.80, 0.33, 1.0), 0.9, "carry the drive voltage; their field crosses the waveguide"),
    "fclad":  ("fibre cladding", (0.80, 0.90, 0.98, 0.30), 0.0, "125 µm of silica, cut short"),
    "fcore":  ("fibre core", (0.98, 0.78, 0.40, 1.0), 0.0, "8.2 µm germanium-doped core"),
    "lens":   ("printed microlens", (0.72, 0.60, 0.95, 0.55), 0.0, "two-photon-printed polymer lens, shaped to expand and collimate the beam"),
    "beam":   ("light beam (illustrative)", (1.0, 0.36, 0.22, 0.30), 0.0, "where the light goes; drawn, not computed"),
    "solder": ("AuSn solder", (0.78, 0.78, 0.82, 1.0), 0.8, "melts to bond the laser chip and carry its current"),
    "inp":    ("InP chip body", (0.66, 0.73, 0.86, 1.0), 0.05, "the laser or amplifier chip, cut short"),
    "siwg":   ("silicon (220 nm)", (0.16, 0.24, 0.42, 1.0), 0.05, "the silicon layer: waveguides, couplers, rings and gratings"),
    "cladd":  ("oxide cladding", (0.55, 0.75, 0.95, 0.12), 0.0, "deposited oxide around and above the waveguides"),
    "act":    ("active region (quantum wells)", (0.85, 0.12, 0.10, 1.0), 0.05, "the gain: carriers recombine here and amplify the light"),
    "bondpad": ("gold bond pads", (0.98, 0.80, 0.33, 1.0), 0.9, "on the pocket floor: carry the current to the laser"),
})
TS, T, SLAB, ZC = 0.22, 0.22, 0.09, 2.2          # Si thickness, slab, top of the oxide cladding

_prism = Model.prism


def _prism_clean(self, poly, z0, z1, mat, group):
    """Model.prism, dropping the slivers that boolean operations on outlines can leave (they extrude to empty meshes)."""
    for g in getattr(poly, "geoms", [poly]):
        if g.geom_type == "Polygon" and g.area > 1e-4:
            _prism(self, g, z0, z1, mat, group)


Model.prism = _prism_clean


# ------------------------------------------------------------------ outlines
def path(pts, w, res=12):
    return LineString(pts).buffer(w / 2, cap_style=2, join_style=1, resolution=res)


def arc(cx, cy, r, a0, a1, n=48):
    t = np.linspace(math.radians(a0), math.radians(a1), n)
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in t]


def sbend(x0, y0, L, H, n=40):
    """S-bend from (x0, y0) to (x0 + L, y0 + H) with zero slope at both ends (raised cosine)."""
    return [(x0 + L * s, y0 + H * (s - math.sin(2 * math.pi * s) / (2 * math.pi))) for s in np.linspace(0, 1, n)]


def annulus(cx, cy, r0, r1, res=64):
    return Point(cx, cy).buffer(r1, resolution=res).difference(Point(cx, cy).buffer(r0, resolution=res))


def sector(cx, cy, r0, r1, a0, a1, n=64):
    outer = arc(cx, cy, r1, a0, a1, n); inner = arc(cx, cy, r0, a1, a0, n) if r0 > 0 else [(cx, cy)]
    return Polygon(outer + inner)


def taper(x0, x1, y, w0, w1):
    return Polygon([(x0, y - w0 / 2), (x1, y - w1 / 2), (x1, y + w1 / 2), (x0, y + w0 / 2)])


def U(*ps):
    return unary_union([p for p in ps if p is not None and not p.is_empty])


# ------------------------------------------------------------------ layers
def soi_base(m, area, zsub=-3.0):
    m.prism(area, zsub, -2.0, "sisub", 0)
    m.prism(area, -2.0, 0.0, "box", 1)


def strip_layer(m, area, core, zc=ZC, grp=2):
    """A strip waveguide layer `core` (Si, 220 nm) in oxide: the core, and the cladding around and above it."""
    m.prism(core, 0.0, T, "siwg", grp)
    m.prism(area.difference(core), 0.0, T, "cladd", grp + 1)
    m.prism(area, T, zc, "cladd", grp + 1)


def heater(m, poly, pads, zh=T + 1.7, th=0.12, zc=ZC, grp=4):
    """TiN heater `poly` 1.7 um above the silicon, with square pads (cx, cy, half-size): vias and metal-1 pads above."""
    m.prism(poly, zh, zh + th, "tin18", grp)
    for cx, cy, hs in pads:
        m.box(cx - hs, cx + hs, cy - hs, cy + hs, zh, zh + th, "tin18", grp)
        for dx in (-0.5, 0.5):
            for dy in (-0.5, 0.5):
                m.box(cx + dx - 0.15, cx + dx + 0.15, cy + dy - 0.15, cy + dy + 0.15, zh + th, zc, "wplug", grp + 1)
        m.box(cx - hs - 0.3, cx + hs + 0.3, cy - hs - 0.3, cy + hs + 0.3, zc, zc + 0.6, "metal1", grp + 2)


def rotz(mesh, a):
    mesh.apply_transform(trimesh.transformations.rotation_matrix(a, [0, 0, 1]))
    return mesh


def along_x(mesh):
    """Turn a mesh built along +z to lie along +x."""
    mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    return mesh


def frustum(r0, r1, L, sections=40):
    return trimesh.creation.revolve(np.array([[0, 0], [r0, 0], [r1, L], [0, L]], float), sections=sections)


def cap(a, Rc, sections=48):
    """Spherical-cap lens of aperture radius a and radius of curvature Rc, flat face on z = 0, bulging to +z."""
    h = Rc - math.sqrt(Rc * Rc - a * a)
    rs = np.linspace(a, 0, 24)
    prof = [[0, 0], [a, 0]] + [[r, math.sqrt(Rc * Rc - r * r) - (Rc - h)] for r in rs[1:]]
    return trimesh.creation.revolve(np.array(prof, float), sections=sections), h


def entry(m, **meta):
    return m.export(meta.pop("dz", 0.6), meta)


# ------------------------------------------------------------------ passive devices
def waveguides():
    m = Model("waveguides")
    area = sbox(-7.5, 0, 7.5, 12); soi_base(m, area)
    strip = sbox(-4.25, 0, -3.75, 12); slab = sbox(-2.0, 0, 2.0, 12); rib = sbox(-0.25, 0, 0.25, 12); sin = sbox(3.9, 0, 5.1, 12)
    m.prism(strip, 0, T, "siwg", 2); m.prism(slab, 0, SLAB, "siwg", 2); m.prism(rib, SLAB, T, "siwg", 2); m.prism(sin, 0, 0.4, "sinwg", 2)
    m.prism(area.difference(U(strip, slab, sin)), 0, SLAB, "cladd", 3)
    m.prism(area.difference(U(strip, rib, sin)), SLAB, T, "cladd", 3)
    m.prism(area.difference(sin), T, 0.4, "cladd", 3)
    m.prism(area, 0.4, ZC, "cladd", 3)
    return entry(m, slug="waveguides", title="Three channel waveguides", short="waveguides",
                 blurb="Left to right: a 500 × 220 nm silicon strip, a 500 nm silicon rib on a 90 nm slab, and a 1.2 × 0.4 µm silicon-nitride strip, all on a 2 µm buried oxide under oxide cladding. Hide the cladding to compare them; stretch the height to see the slab. The strip confines the light most, the rib leaves a slab for electrical contacts, and the nitride guide spreads its mode furthest and loses least.",
                 orbit="-35deg 62deg 80%")


def routing():
    m = Model("routing")
    w = 0.5
    xs = U(taper(-4, -1.5, 0, w, 1.2), sbox(-1.5, -0.6, 1.5, 0.6), taper(1.5, 4, 0, 1.2, w))
    cross = U(xs, srot(xs, 90, origin=(0, 0)))
    west = U(path([(-8, 0), (-4, 0)], w), taper(-16, -8, 0, 2.0, w), path([(-19, 0), (-16, 0)], 2.0))
    east = path([(4, 0), (6, 0)] + arc(6, 5, 5, -90, 0) + [(11, 12)], w)
    north = path([(0, 4), (0, 12)], w); south = path([(0, -12), (0, -4)], w)
    core = U(cross, west, east, north, south)
    area = sbox(-19, -12, 13, 12); soi_base(m, area); strip_layer(m, area, core)
    return entry(m, slug="routing", title="Routing: a crossing, a bend and a taper", short="bend, taper, crossing",
                 blurb="Silicon strips 500 nm wide. In the middle, a crossing: each guide widens to 1.2 µm through linear expanders, so its mode narrows less where the other guide cuts through it. To the right, a 90° bend of 5 µm radius; to the left, a linear taper from 0.5 to 2 µm into a multimode guide, long enough to be adiabatic (Section 8.3).",
                 orbit="-20deg 58deg 85%")


def dc():
    m = Model("dc")
    w, gap, H = 0.5, 0.2, 2.0
    y = (gap + w) / 2
    up = path([(-18, y + H)] + sbend(-15, y + H, 10, -H) + [(5, y)] + sbend(5, y, 10, H) + [(18, y + H)], w)
    lo = path([(-18, -y - H)] + sbend(-15, -y - H, 10, H) + [(5, -y)] + sbend(5, -y, 10, -H) + [(18, -y - H)], w)
    core = U(up, lo); area = sbox(-18, -4.5, 18, 4.5); soi_base(m, area); strip_layer(m, area, core)
    return entry(m, slug="dc", title="Directional coupler", short="directional coupler",
                 blurb="Two 500 nm strips brought within 200 nm of each other by raised-cosine S-bends, side by side for 10 µm. In the gap their evanescent fields overlap, and power beats from one guide to the other with the cross-over length of Chapter 9; the S-bends start and stop the coupling smoothly. Zoom in on the gap: it is narrower than a waveguide.",
                 orbit="-25deg 60deg 85%")


def mmi():
    m = Model("mmi")
    W, L, wa, w = 6.0, 32.8, 1.5, 0.5
    core = U(path([(-12, 0), (-8, 0)], w), taper(-8, 0, 0, w, wa), sbox(0, -W / 2, L, W / 2),
             *[U(taper(L, L + 8, s * 1.51, wa, w), path([(L + 8, s * 1.51)] + sbend(L + 8, s * 1.51, 12, s * 2.49) + [(L + 24, s * 4.0)], w)) for s in (-1, 1)])
    area = sbox(-12, -6, L + 24, 6); soi_base(m, area); strip_layer(m, area, core)
    return entry(m, slug="mmi", title="1 × 2 multimode-interference splitter", short="1 × 2 MMI",
                 blurb="A 6 µm wide multimode section, 32.8 µm long: the best length of Figure 10.5. A tapered 1.5 µm access guide launches the light at the centre; the modes of the wide section beat, and two images of the input form at ±1.51 µm from the centre at the far end, where two tapered outputs collect them and S-bends separate them.",
                 orbit="-25deg 60deg 85%")


def mzi():
    m = Model("mzi")
    w = 0.5
    yb = lambda x0, s: path([(x0, 0)] + sbend(x0, 0, 12, s * 6) + [(x0 + 12.5, s * 6)], w)
    yb2 = lambda x0, s: path([(x0 - 0.5, s * 6)] + sbend(x0, s * 6, 12, -s * 6) + [(x0 + 12, 0)], w)
    upper = path([(12, 6), (40, 6)], w)
    r = 3.0
    lower = path([(12, -6), (15, -6)] + arc(15, -9, r, 90, 0, 16) + [(18, -11)] + arc(21, -11, r, 180, 270, 16) + [(31, -14)]
                 + arc(31, -11, r, 270, 360, 16) + [(34, -9)] + arc(37, -9, r, 180, 90, 16) + [(40, -6)], w)
    core = U(path([(-6, 0), (0, 0)], w), yb(0, 1), yb(0, -1), upper, lower, yb2(40, 1), yb2(40, -1), path([(52, 0), (58, 0)], w))
    area = sbox(-6, -18, 58, 11); soi_base(m, area); strip_layer(m, area, core)
    heater(m, sbox(14.4, 5.0, 37.6, 7.0), [(13.4, 6.0, 1.2), (38.6, 6.0, 1.2)])
    return entry(m, slug="mzi", title="Unbalanced Mach–Zehnder interferometer with a heater", short="MZI",
                 blurb="A Y-branch splits the light into two arms that a second Y-branch recombines. The lower arm takes a detour, the path difference ΔL that makes the transmission a periodic filter with a free spectral range λ²/(n_g ΔL); the upper arm carries a TiN heater 1.7 µm above it, with pads and vias at its ends, that slides the fringes (Chapter 11). Arm lengths are cut short.",
                 orbit="-25deg 58deg 85%")


def ring():
    m = Model("ring")
    R, w, gap = 10.0, 0.5, 0.2
    yb = R + w / 2 + gap + w / 2
    core = U(annulus(0, 0, R - w / 2, R + w / 2, 96), path([(-16, -yb), (16, -yb)], w), path([(-16, yb), (16, yb)], w))
    area = sbox(-16, -14, 20, 14); soi_base(m, area); strip_layer(m, area, core)
    h = U(sector(0, 0, R - 0.75, R + 0.75, 22, 338, 96), path([(R * math.cos(math.radians(22)), R * math.sin(math.radians(22))), (16, 3.8)], 1.5),
          path([(R * math.cos(math.radians(338)), -R * math.sin(math.radians(22))), (16, -3.8)], 1.5))
    heater(m, h, [(17.0, 3.8, 1.2), (17.0, -3.8, 1.2)])
    return entry(m, slug="ring", title="Add-drop ring resonator with a heater", short="add-drop ring",
                 blurb="A 10 µm radius ring between two bus waveguides, each 200 nm away. Light at a resonance builds up in the ring and leaves through the drop port; the rest passes the through port (Chapter 12). A TiN heater follows the ring 1.7 µm above it and tunes the resonance at about 0.1 nm per mW; its leads run to pads on the right.",
                 orbit="-20deg 58deg 85%")


def bragg():
    m = Model("bragg")
    per, w, dw, N = 0.317, 0.5, 0.05, 24
    pieces, x = [path([(-6, 0), (0, 0)], w)], 0.0
    for half in range(2):
        for k in range(N):
            pieces.append(sbox(x, -(w + dw) / 2, x + per / 2, (w + dw) / 2)); pieces.append(sbox(x + per / 2, -(w - dw) / 2, x + per, (w - dw) / 2)); x += per
        if half == 0:
            pieces.append(sbox(x, -(w + dw) / 2, x + per / 2, (w + dw) / 2)); x += per / 2      # the quarter-wave (half-period) shift
    pieces.append(path([(x, 0), (x + 6, 0)], w))
    core = U(*pieces); area = sbox(-6, -3, x + 6, 3); soi_base(m, area); strip_layer(m, area, core)
    return entry(m, slug="bragg", title="Quarter-wave-shifted Bragg grating", short="Bragg grating",
                 blurb="A 500 nm strip whose width alternates by 50 nm every half period of 317 nm, which reflects a band around 1550 nm (Chapter 13). In the middle one wide tooth is half a period long instead of a quarter: the quarter-wave shift that opens a single transmission peak in the stop band. Only 48 periods are drawn; real gratings have hundreds. Zoom in to see the teeth.",
                 orbit="-25deg 60deg 80%")


def gc():
    m = Model("gc")
    w, per, r0, r1, ha = 0.5, 0.607, 15.0, 26.0, 20.0
    fan = Polygon([(0, -w / 2)] + arc(0, 0, r1, -ha, ha, 64) + [(0, w / 2)])
    full = U(path([(-8, 0), (0.2, 0)], w), Polygon([(0, -w / 2)] + arc(0, 0, r0, -ha, ha, 48) + [(0, w / 2)]))
    teeth = U(*[sector(0, 0, r0 + k * per + per / 2, r0 + (k + 1) * per, -ha, ha, 28) for k in range(int((r1 - r0) / per))])
    etched = fan.difference(Polygon([(0, -w / 2)] + arc(0, 0, r0, -ha, ha, 48) + [(0, w / 2)]))
    area = sbox(-8, -11, 29, 11); soi_base(m, area)
    m.prism(full, 0, T, "siwg", 2); m.prism(etched, 0, 0.15, "siwg", 2); m.prism(teeth, 0.15, T, "siwg", 2)
    m.prism(area.difference(U(full, etched)), 0, 0.15, "cladd", 3); m.prism(area.difference(U(full, teeth)), 0.15, T, "cladd", 3); m.prism(area, T, ZC, "cladd", 3)
    b = trimesh.creation.cylinder(radius=5.2, height=26, sections=48)             # the beam starts on the grating itself
    b.apply_translation([0, 0, 13]); b.apply_transform(trimesh.transformations.rotation_matrix(math.radians(8), [0, 1, 0]))
    b.apply_translation([20.5, 0, T]); m.add(b, "beam", 5)
    return entry(m, slug="gc", title="Focusing grating coupler", short="grating coupler",
                 blurb="A 500 nm waveguide opens into a fan whose curved teeth, etched 70 nm into the silicon with a 607 nm period, focus as well as diffract: the compact focusing coupler of Chapter 15. The light leaves upwards about 8° from the vertical into a beam the size of a fibre mode (10.4 µm, red), where a fibre would sit.",
                 orbit="-30deg 62deg 90%")


def edge():
    m = Model("edge")
    area = sbox(-30, -8, 0, 8); m.prism(area, -3.0, -2.0, "sisub", 0); m.prism(area, -2.0, 0.0, "box", 1)
    core = U(path([(-30, 0), (-25, 0)], 0.5), taper(-25, 0, 0, 0.5, 0.18))
    m.prism(core, 0, T, "siwg", 2); m.prism(area.difference(core), 0, T, "cladd", 3); m.prism(area, T, 3.0, "cladd", 3)
    b = along_x(frustum(1.3, 4.5, 16)); b.apply_translation([0, 0, 0.11]); m.add(b, "beam", 5)
    return entry(m, slug="edge", title="Inverse-taper edge coupler", short="edge coupler",
                 blurb="The silicon strip narrows from 500 to 180 nm towards the polished facet. Too narrow to hold the light, it lets the mode spread into the oxide around it, until at the facet it is a few micrometres across and matches a lensed fibre or a fibre array; the beam (red) leaves the facet and spreads (Chapter 16). The taper, a few hundred micrometres long in practice, is cut short.",
                 orbit="-55deg 65deg 85%")


def faml():
    m = Model("faml")
    area = sbox(-90, -75, 0, 75)                                                    # a chip piece on the fibre's scale
    m.prism(area, -70.0, -2.0, "sisub", 0); m.prism(area, -2.0, 0.0, "box", 1)
    core = U(path([(-90, 0), (-30, 0)], 0.5), taper(-30, 0, 0, 0.5, 0.18))
    m.prism(core, 0, T, "siwg", 2); m.prism(area.difference(core), 0, T, "cladd", 3); m.prism(area, T, 3.0, "cladd", 3)
    lc, hc = cap(18.0, 30.0); along_x(lc); lc.apply_translation([0, 0, 0.11]); m.add(lc, "lens", 4)          # on the chip facet
    gapx = 120.0
    fl, hf = cap(30.0, 48.0); along_x(fl); fl.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [0, 0, 1]))
    fl.apply_translation([gapx, 0, 0.11]); m.add(fl, "lens", 4)                                             # on the fibre end, facing the chip
    cl = along_x(trimesh.creation.cylinder(radius=62.5, height=100, sections=64)); cl.apply_translation([gapx + 50, 0, 0.11]); m.add(cl, "fclad", 6)
    co = along_x(trimesh.creation.cylinder(radius=4.1, height=100.4, sections=32)); co.apply_translation([gapx + 50, 0, 0.11]); m.add(co, "fcore", 6)
    bm = along_x(frustum(12.0, 13.0, gapx - hc - hf)); bm.apply_translation([hc, 0, 0.11]); m.add(bm, "beam", 5)
    return entry(m, slug="faml", title="Facet-attached microlenses", short="FaML",
                 blurb="A lens printed on the chip's facet expands the edge coupler's few-micrometre mode into a beam about 25 µm wide; a second lens printed on the end of the fibre (or on each fibre of an array) catches it and focuses it into the 8.2 µm core. The wide beam between them makes the alignment far more tolerant than butt coupling (Section 17.5). Lens shapes and the 120 µm gap are illustrative; the fibre is cut short.",
                 orbit="-40deg 70deg 100%", dz=8.0)


# ------------------------------------------------------------------ active devices
def tfln():
    m = Model("tfln")
    area = sbox(-12, 0, 12, 30)
    m.prism(area, -3.0, -2.0, "sisub", 0); m.prism(area, -2.0, 0.0, "box", 1)
    m.prism(area, 0.0, 0.3, "ln", 2); m.box(-0.75, 0.75, 0, 30, 0.3, 0.6, "ln", 2)
    for s in (-1, 1):
        x0, x1 = sorted((s * 2.75, s * 11.0)); m.box(x0, x1, 0, 30, 0.3, 1.1, "gold", 3)
    return entry(m, slug="tfln", title="Thin-film lithium niobate phase shifter", short="TFLN phase shifter",
                 blurb="A ridge etched 300 nm into a 600 nm x-cut lithium-niobate film on oxide, with gold electrodes on the slab 2.75 µm either side. The voltage between them puts a field across the ridge, and the Pockels effect changes its index in proportion: a pure phase shift, with no loss added and no carriers to slow it down (Sections 19.3 and 20.5).",
                 orbit="-30deg 62deg 80%")


def mzm():
    m = Model("mzm")
    L = 40.0; area = sbox(-15, 0, 15, L); soi_base(m, area)
    si_lo, si_hi = [], []
    for xc, pside in ((-5.0, -1), (5.0, 1)):     # p side away from the centre (towards the grounds), n side towards the signal
        for xa, xb, mat in ((xc + pside * 2.2, xc + pside * 1.2, "pp"), (xc + pside * 1.2, xc, "pdop"), (xc, xc - pside * 1.2, "ndop"), (xc - pside * 1.2, xc - pside * 2.2, "nn")):
            a, b = sorted((xa, xb)); m.box(a, b, 0, L, 0, SLAB, mat, 2); si_lo.append(sbox(a, 0, b, L))
        a, b = sorted((xc, xc + pside * 0.25)); m.box(a, b, 0, L, SLAB, T, "pdop", 2)
        a, b = sorted((xc, xc - pside * 0.25)); m.box(a, b, 0, L, SLAB, T, "ndop", 2); si_hi.append(sbox(xc - 0.25, 0, xc + 0.25, L))
        for xm in (xc + pside * 1.7, xc - pside * 1.7):
            y = 1.0
            while y <= L - 1:
                m.box(xm - 0.11, xm + 0.11, y - 0.11, y + 0.11, SLAB, 2.6, "wplug", 4); y += 2.0
    m.prism(area.difference(U(*si_lo)), 0, SLAB, "cladd", 3); m.prism(area.difference(U(*si_hi)), SLAB, T, "cladd", 3); m.prism(area, T, 3.4, "cladd", 3)
    for xa, xb in ((-7.8, -6.1), (6.1, 7.8), (-3.9, 3.9)):            # metal 1: p contacts outside, one n contact strip joining both arms
        m.box(xa, xb, 0, L, 2.6, 3.2, "metal1", 5)
    for xm in (-6.95, 6.95, -2.0, 2.0):
        y = 2.0
        while y <= L - 2:
            m.box(xm - 0.15, xm + 0.15, y - 0.15, y + 0.15, 3.2, 4.0, "wplug", 6); y += 4.0
    for xa, xb in ((-14.0, -6.1), (-2.5, 2.5), (6.1, 14.0)):          # ground-signal-ground on metal 2
        m.box(xa, xb, 0, L, 4.0, 5.2, "metal2", 7)
    return entry(m, slug="mzm", title="Silicon travelling-wave Mach–Zehnder modulator", short="travelling-wave MZM",
                 blurb="A 40 µm piece of the two arms of a depletion-mode MZM (Chapter 20). Each arm is the PN rib of Figure 19.2, its p side towards a ground electrode and its n side towards the signal electrode in the middle, which drives both arms at once in push-pull. The ground–signal–ground lines on metal 2 form a transmission line that carries the drive along with the light. Hide the cladding and the metal to see the junctions.",
                 orbit="-30deg 60deg 85%", dz=0.7)


def ringmod():
    m = Model("ringmod")
    R, w, gap = 7.2, 0.5, 0.2
    a0, a1 = -54.0, 234.0                                   # the junction covers 80 % of the ring, away from the bus
    yb = -(R + w / 2 + gap + w / 2)
    area = sbox(-12, -10, 12, 11); soi_base(m, area)
    bus = path([(-12, yb), (12, yb)], w)
    m.prism(bus, 0, T, "siwg", 2)
    rib_p = sector(0, 0, R - w / 2, R, a0, a1, 96); rib_n = sector(0, 0, R, R + w / 2, a0, a1, 96)
    rib_i = annulus(0, 0, R - w / 2, R + w / 2, 96).difference(sector(0, 0, R - w / 2 - 0.01, R + w / 2 + 0.01, a0, a1, 96))
    slab_p = sector(0, 0, R - 1.2, R - w / 2, a0, a1, 96); slab_pp = sector(0, 0, R - 2.2, R - 1.2, a0, a1, 96)
    slab_n = sector(0, 0, R + w / 2, R + 1.2, a0, a1, 96); slab_nn = sector(0, 0, R + 1.2, R + 2.2, a0, a1, 96)
    for poly, mat in ((slab_pp, "pp"), (slab_p, "pdop"), (slab_n, "ndop"), (slab_nn, "nn")):
        m.prism(poly, 0, SLAB, mat, 2)
    m.prism(rib_p, 0, T, "pdop", 2); m.prism(rib_n, 0, T, "ndop", 2); m.prism(rib_i, 0, T, "siwg", 2)
    lo = U(bus, rib_p, rib_n, rib_i, slab_p, slab_pp, slab_n, slab_nn); hi = U(bus, rib_p, rib_n, rib_i)
    m.prism(area.difference(lo), 0, SLAB, "cladd", 3); m.prism(area.difference(hi), SLAB, T, "cladd", 3); m.prism(area, T, 3.4, "cladd", 3)
    for rr in (R - 1.7, R + 1.7):
        for ang in np.arange(a0 + 12, a1 - 6, 24):
            x, y = rr * math.cos(math.radians(ang)), rr * math.sin(math.radians(ang))
            m.box(x - 0.11, x + 0.11, y - 0.11, y + 0.11, SLAB, 2.6, "wplug", 4)
    m.prism(sector(0, 0, R - 2.3, R - 1.1, a0 + 4, a1 - 4, 96), 2.6, 3.2, "metal1", 5)
    m.prism(U(sector(0, 0, R + 1.1, R + 2.3, a0 + 4, a1 - 4, 96), path([(0, R + 1.7), (0, 10.8)], 1.2)), 2.6, 3.2, "metal1", 5)
    m.prism(path([(-(R - 1.7) * math.cos(math.radians(30)), (R - 1.7) * math.sin(math.radians(30))), (-11.5, 9.5)], 1.0), 3.4, 4.0, "metal2", 6)
    m.box(-(R - 1.7) * math.cos(math.radians(30)) - 0.2, -(R - 1.7) * math.cos(math.radians(30)) + 0.2,
          (R - 1.7) * math.sin(math.radians(30)) - 0.2, (R - 1.7) * math.sin(math.radians(30)) + 0.2, 3.2, 3.4, "wplug", 6)
    return entry(m, slug="ringmod", title="Depletion ring modulator", short="ring modulator",
                 blurb="The 7.2 µm ring of Worked Example 20.2, 200 nm from its bus. Over 80 % of its circumference a lateral junction runs along the ring: p on the inside, n on the outside, with heavily doped strips and rows of plugs further out. Reverse bias widens the depletion region, shifts the resonance and switches the light at the through port. Near the bus the ring is left undoped. The p contact rises through a via to metal 2.",
                 orbit="-25deg 58deg 85%", dz=0.7)


def ecl():
    m = Model("ecl")
    # the reflective SOA, cut short: InP with an active stripe, a p-InP ridge and its contact (angled facet drawn straight)
    m.box(-40, -2, -9, 9, -6.0, 0.0, "inp", 0); m.box(-40, -2, -9, 9, 0.0, 0.2, "act", 1)
    m.box(-40, -2, -9, 9, 0.2, 0.55, "pinp", 1); m.box(-40, -2, -1.25, 1.25, 0.55, 2.0, "pinp", 2)
    m.box(-40, -2, -1.25, 1.25, 2.0, 2.15, "cap", 2); m.box(-38, -4, -2.0, 2.0, 2.15, 2.45, "pmetal", 3)
    w = 0.5; R1, R2, g = 10.0, 11.0, 0.2
    y1 = R1 + w + g; yd = 2 * y1                                   # ring 1 centre height; drop guide height
    c2 = yd + R2 + w + g; yd2 = c2 + R2 + w + g
    core = U(taper(0, 10, 0, 0.18, w), path([(10, 0), (62, 0)], w),
             annulus(36, y1, R1 - w / 2, R1 + w / 2, 96), path([(14, yd), (76, yd)], w),
             annulus(52, c2, R2 - w / 2, R2 + w / 2, 96), path([(30, yd2), (74, yd2)], w),
             annulus(74, yd2 + 6.0, 6.0 - w / 2, 6.0 + w / 2, 64))
    area = sbox(0, -8, 90, yd2 + 16); soi_base(m, area); strip_layer(m, area, core)
    heater(m, U(sbox(13, -0.75, 25, 0.75), path([(13, 0), (13, -3.5)], 1.0), path([(25, 0), (25, -3.5)], 1.0)), [(13, -3.5, 1.0), (25, -3.5, 1.0)])
    pol = lambda cx, cy, r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    e1, e2 = pol(36, y1, R1, 135), pol(36, y1, R1, 225)        # ring-1 heater: the left side of the ring, leads to pads on the left
    heater(m, U(sector(36, y1, R1 - 0.75, R1 + 0.75, 135, 225, 64), path([e1, (20, e1[1])], 1.0), path([e2, (20, e2[1])], 1.0)),
           [(20, e1[1], 1.0), (20, e2[1], 1.0)], grp=7)
    f1, f2 = pol(52, c2, R2, 45), pol(52, c2, R2, -45)         # ring-2 heater: the right side, leads to pads on the right
    heater(m, U(sector(52, c2, R2 - 0.75, R2 + 0.75, -45, 45, 64), path([f1, (68, f1[1])], 1.0), path([f2, (68, f2[1])], 1.0)),
           [(68, f1[1], 1.0), (68, f2[1], 1.0)], grp=10)
    return entry(m, slug="ecl", title="III–V/silicon external-cavity laser", short="external-cavity laser",
                 blurb="The laser of Figure 26.4. A reflective SOA (left, cut short; its angled facet is drawn straight) is butt-coupled to an inverse-taper edge coupler. On the silicon, the light passes a phase heater, drops through ring 1 (R = 10 µm) into a guide that leads to ring 2 (R = 11 µm), and reaches a loop mirror that sends it back. The two rings pass light only where their resonances coincide, the Vernier effect of Section 26.5; heaters on the rings, each with its leads and pads, choose the wavelength.",
                 orbit="-15deg 55deg 95%", dz=1.0)


def flipchip():
    m = Model("flipchip")
    area = sbox(-30, -16, 26, 16); pocket = sbox(-8, -12, 22, 12)
    m.prism(area.difference(pocket), -12.0, -2.0, "sisub", 0); m.prism(pocket, -12.0, -6.0, "sisub", 0)
    m.prism(area.difference(pocket), -2.0, 0.0, "box", 1)
    core = path([(-30, 0), (-8, 0)], 0.5)
    m.prism(core, 0, T, "siwg", 2); m.prism(area.difference(pocket).difference(core), 0, T, "cladd", 3); m.prism(area.difference(pocket), T, 2.5, "cladd", 3)
    for yc in (-6.0, 6.0):
        m.box(-5, 19, yc - 3, yc + 3, -6.0, -5.7, "bondpad", 4); m.box(-4, 18, yc - 2.4, yc + 2.4, -5.7, -4.4, "solder", 4)
    # the laser, flipped (p side down): p-metal, p-InP, a buried active stripe level with the silicon core, n-InP above
    m.box(-7.5, 20, -10, 10, -4.4, -4.1, "pmetal", 5); m.box(-7.5, 20, -10, 10, -4.1, -3.9, "cap", 5)
    m.box(-7.5, 20, -10, 10, -3.9, 0.02, "pinp", 6); m.box(-7.5, 20, -1.0, 1.0, 0.02, 0.20, "act", 6)
    for s in (-1, 1):
        a, b = sorted((s * 1.0, s * 10.0)); m.box(-7.5, 20, a, b, 0.02, 0.20, "pinp", 6)
    m.box(-7.5, 20, -10, 10, 0.20, 8.0, "inp", 7); m.box(-6, 18.5, -8, 8, 8.0, 8.3, "nmetal", 8)
    return entry(m, slug="flipchip", title="Flip-chip laser in a silicon pocket", short="flip-chip laser",
                 blurb="A pocket is etched through the cladding and the buried oxide into the substrate, and a laser chip is bonded into it upside down on AuSn solder, its active stripe at the height of the silicon waveguide, whose end faces the laser's facet across a gap of half a micrometre (Section 27.2). The pocket depth and the solder thickness set the vertical alignment; the bonder sets the lateral one. The laser, really a few hundred micrometres long, is cut short.",
                 orbit="-40deg 62deg 90%", dz=1.5)


ALL = {"waveguides": waveguides, "routing": routing, "dc": dc, "mmi": mmi, "mzi": mzi, "ring": ring, "bragg": bragg, "gc": gc,
       "edge": edge, "faml": faml, "tfln": tfln, "mzm": mzm, "ringmod": ringmod, "ecl": ecl, "flipchip": flipchip}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(ALL)
    man = ROOT / "_data" / "stacks3d.json"
    old = {e["slug"]: e for e in json.loads(man.read_text(encoding="utf-8"))} if man.exists() else {}
    new = {}
    for n in names:
        e = ALL[n]()
        e["credit"] = "Generic, illustrative device drawn for this tutorial, not from any PDK; thicknesses to scale, lengths cut short."
        new[e["slug"]] = e
    order = list(old) + [k for k in new if k not in old]
    man.write_text(json.dumps([new.get(k, old.get(k)) for k in order], indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote _data/stacks3d.json:", ", ".join(order))
