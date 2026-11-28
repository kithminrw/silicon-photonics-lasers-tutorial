"""Figures for Chapter 17 (fibre arrays, photonic wire bonds and packaging).

Run from the repository root:   python -I -X utf8 figsrc/ch17_figs.py [name ...]
Writes assets/figs/ch17_*.svg and prints every number the figures and captions use.

Geometry: standard fibre (125 um cladding, 8.2 um core, 10.4 um mode at 1550 nm; Chapter 3), 127 um array pitch,
V-grooves in (100) silicon with {111} walls at 54.74 degrees to the surface (Section 17.1). Everything else is
schematic and says so.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: E402,F401
from geomstyle import *     # noqa: E402,F401

R_CL, R_CO, MFD = 62.5, 4.1, 10.4
PITCH = 127.0
WALL = math.degrees(math.atan(math.sqrt(2)))      # {111} to (100): 54.74 deg
N_GL = 1.444


# =====================================================================================================
# Figure 17.1: cross-section of an eight-fibre V-groove array, to scale
# =====================================================================================================
def vgroove(W):
    """Groove of opening W: apex depth, fibre-centre height above the surface, contact point along the wall."""
    a = math.radians(WALL)
    h = W / 2 * math.tan(a)
    d = R_CL / math.cos(a)               # apex to fibre centre (the wall's normal makes WALL with the vertical)
    return h, d - h


def fig_vgroove():
    N, W, LAND = 8, 120.0, 7.0
    h, yc = vgroove(W)
    T_SUB, T_LID = 140.0, 110.0
    span = (N - 1) * PITCH
    x0, x1 = -span / 2 - 120, span / 2 + 120
    ytop_f = yc + R_CL
    y0, y1 = -h - T_SUB, ytop_f + T_LID + 8
    W_IN = 6.3
    fig = plt.figure(figsize=(W_IN, W_IN * (y1 - y0) / (x1 - x0)))
    ax = fig.add_axes([0, 0, 1, 1]); frameless(ax, (x0, x1), (y0, y1))
    xs = [(-span / 2 + i * PITCH) for i in range(N)]
    # V-groove chip: (100) silicon with grooves
    pts = [(x0 + 20, y0)]
    pts += [(x0 + 20, 0)]
    for xc in xs:
        pts += [(xc - W / 2, 0), (xc, -h), (xc + W / 2, 0)]
    pts += [(x1 - 20, 0), (x1 - 20, y0)]
    poly(ax, pts, "si", z=1)
    # epoxy filling the space between chip, fibres and lid
    box(ax, x0 + 20, 0, x1 - x0 - 40, ytop_f, "epoxy", z=0)
    for xc in xs:
        poly(ax, [(xc - W / 2, 0), (xc, -h), (xc + W / 2, 0)], "epoxy", z=0.5)
    poly(ax, pts, "si", z=1)
    # lid
    box(ax, x0 + 20, ytop_f, x1 - x0 - 40, T_LID, "glass", z=2, ec=MUTED, lw=0.5)
    # fibres
    for xc in xs:
        ax.add_patch(Circle((xc, yc), R_CL, fc=MAT["glass"], ec=MUTED, lw=0.5, zorder=3))
        ax.add_patch(Circle((xc, yc), R_CO, fc=MAT["core"], ec="none", zorder=4))
    # dimensions and labels
    for xc in xs[:2]:
        ax.plot([xc, xc], [yc, ytop_f + T_LID * 0.62], color=MUTED, lw=0.5, ls=(0, (2, 2)), zorder=5)
    dim(ax, (xs[0], ytop_f + T_LID * 0.55), (xs[1], ytop_f + T_LID * 0.55), "127 µm", fs=FS_SMALL, bg=None, text_off=(0, 9))
    dim(ax, (xs[2] - R_CL, yc), (xs[2] + R_CL, yc), "", fs=FS_SMALL)
    label(ax, xs[2], yc + 14, "125 µm", fs=FS_SMALL, bg=MAT["glass"])
    callout(ax, (xs[3] + 3, yc + 3), (xs[3] + 40, yc + 38), "core 8.2 µm", ha="left")
    label(ax, 0, ytop_f + T_LID * 0.25, "glass lid", fs=FS)
    label(ax, 0, -h - T_SUB * 0.55, "silicon V-groove chip", fs=FS)
    callout(ax, ((xs[5] + xs[6]) / 2, ytop_f * 0.55), ((xs[5] + xs[6]) / 2 + 10, ytop_f + 30), "epoxy", ha="center")
    # wall angle on the last groove
    xg = xs[-1] + W / 2
    ax.plot([xg - 48, xg], [0, 0], color=INK, lw=0.6, ls=(0, (2, 2)), zorder=6)
    aa = np.radians(np.linspace(180, 180 + WALL, 30))
    aa = np.radians(np.linspace(180 - 0, 180 + WALL, 30))
    ax.plot(xg + 30 * np.cos(aa), 30 * np.sin(aa), color=INK, lw=0.8, zorder=6)
    callout(ax, (xg - 27, -16), (xs[-1] - 10, -h - 26), f"{WALL:.1f}° walls: the {{111}} crystal planes", ha="center")
    scalebar(ax, x1 - 140, y0 + 18, 100, "100 µm")
    note(ax, "to scale; lid and chip thickness illustrative", "lower left")
    save(fig, "ch17_vgroove")
    print(f"Fig 17.1: wall angle {WALL:.2f} deg; groove opening {W:.0f} um (land {PITCH - W:.0f} um), apex depth {h:.1f} um, "
          f"fibre centre {yc:.1f} um above the surface, top {ytop_f:.1f} um; gap between fibres {PITCH - 2 * R_CL:.0f} um")


# =====================================================================================================
# Figure 17.2: fibre arrays over grating couplers: angle-polished, and low-profile (TIR)
# =====================================================================================================
def _chip(ax, x0, x1, gc_x, t_ox=10, depth=55):
    box(ax, x0, -depth, x1 - x0, depth - t_ox, "sub")
    box(ax, x0, -t_ox, x1 - x0, t_ox, "ox")
    box(ax, gc_x - 16, -t_ox * 0.45, 32, 2.6, "si", z=3)
    for k in range(9):
        box(ax, gc_x - 15 + k * 3.6, -t_ox * 0.45 + 1.6, 1.6, 1.0, "ox", z=4)


def fig_arrays():
    TH = 8.0
    th_air = math.degrees(math.asin(N_GL * math.sin(math.radians(TH))))
    phi_pol = 45 - TH / 2                       # low-profile polish angle (face to fibre axis) for a beam TH from vertical
    inc = 90 - phi_pol
    crit = math.degrees(math.asin(1 / N_GL))
    fig = plt.figure(figsize=(6.3, 2.9))
    a1 = fig.add_axes([0.0, 0.0, 0.47, 1.0]); frameless(a1, (-150, 190), (-60, 250))
    a2 = fig.add_axes([0.51, 0.0, 0.49, 1.0]); frameless(a2, (-215, 140), (-60, 250))
    # ---- (a) angle-polished array: fibres at TH from vertical, end face parallel to the chip
    GAP, GCX = 40.0, 0.0
    _chip(a1, -150, 190, GCX)
    t = math.radians(TH); u = np.array([math.sin(t), math.cos(t)]); n = np.array([math.cos(t), -math.sin(t)])
    ta = math.radians(th_air)
    xe = GCX + GAP * math.tan(ta)                # where the beam leaves the array face
    P0 = np.array([xe, GAP])
    Lb = 300

    def strip(c0, c1, mat, z=2, **kw):          # band between offsets c0 and c1 across the axis, cut by the face y = GAP
        a0 = P0 + n * c0 - u * (n[1] * c0 / u[1]) * 0; a0 = P0 + n * c0; a0 = a0 + u * ((GAP - a0[1]) / u[1])
        b0 = P0 + n * c1; b0 = b0 + u * ((GAP - b0[1]) / u[1])
        poly(a1, [a0, b0, b0 + u * Lb, a0 + u * Lb], mat, z=z, **kw)
    strip(-125, -62.5, "si")
    strip(62.5, 140, "glass", ec=MUTED, lw=0.5)
    strip(-62.5, 62.5, "glass", ec=MUTED, lw=0.5)
    strip(-4.1 * 2, 4.1 * 2, "core", z=3)
    a1.plot([P0[0] - 140, P0[0] + 160], [GAP, GAP], color=INK, lw=0.9, zorder=4)
    # beam: in the fibre along u, in air at th_air, in the oxide at TH again
    yb = -5.5
    xb = GCX + 5.5 * math.tan(t)
    poly(a1, [(xe - 8, GAP), (xe + 8, GAP), (GCX + 8, 0), (GCX - 8, 0)], AMBER, alpha=0.5, z=3)
    a1.plot([xe, xe], [GAP, GAP + 150], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=5)
    aa = np.radians(np.linspace(90 - TH, 90, 20))
    a1.plot(xe + 135 * np.cos(aa), GAP + 135 * np.sin(aa), color=INK, lw=0.8, zorder=5)
    label(a1, xe - 6, GAP + 160, f"fibres at {TH:.0f}°", fs=FS_SMALL, ha="center")
    a1.plot([GCX, GCX], [0, GAP + 2], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=5)
    label(a1, GCX - 12, GAP / 2, f"{th_air:.1f}°\nin air", fs=FS_SMALL, ha="right")
    callout(a1, (P0[0] + 120, GAP), (120, 18), "end face polished\nparallel to the chip", ha="center")
    label(a1, -135, 222, "V-groove\nchip", fs=FS_SMALL, ha="left")
    label(a1, 160, 222, "lid", fs=FS_SMALL, ha="center")
    callout(a1, (GCX + 14, -4), (60, -35), "grating coupler", ha="left")
    label(a1, -140, -30, "PIC", fs=FS_SMALL, ha="left")
    panel(a1, "a", 0.0, 1.0)
    # ---- (b) low-profile array: fibre parallel to the chip, end polished at phi_pol, TIR turns the light down
    Y = 75.0                                    # fibre axis height above the chip
    XT = 0.0                                    # where the axis meets the polished face
    p = math.radians(phi_pol)
    # glass block above the fibre, fibre below it; the polished face is a plane at phi_pol to the axis
    def face_x(y):                              # x of the face at height y (it descends towards the chip side, +x)
        return XT - (y - Y) / math.tan(p)
    yb0, yb1 = Y - 62.5, 240
    poly(a2, [(face_x(Y + 62.5), Y + 62.5), (face_x(yb1), yb1), (-215, yb1), (-215, Y + 62.5)], "glass", ec=MUTED, lw=0.5, z=2)
    poly(a2, [(face_x(yb0), yb0), (face_x(Y + 62.5), Y + 62.5), (-215, Y + 62.5), (-215, yb0)], "glass", ec=MUTED, lw=0.5, z=2)
    poly(a2, [(face_x(Y - 4.1 * 2), Y - 8.2), (face_x(Y + 8.2), Y + 8.2), (-215, Y + 8.2), (-215, Y - 8.2)], "core", z=3)
    _chip(a2, -215, 140, XT + (Y) * math.tan(math.radians(TH)) * 0 + Y * math.tan(math.radians(TH)))
    # light: along the axis to the face, reflected down at TH from vertical (forward-leaning)
    d = np.array([math.sin(math.radians(TH)), -1.0 * math.cos(math.radians(TH))])
    x_gc = XT + Y * math.tan(math.radians(TH)) * 1.0
    arrow(a2, (-170, Y), (-60, Y), col=AMBER, lw=1.6, ms=9)
    poly(a2, [(XT - 8, Y), (XT + 8, Y), (x_gc + 8, 0), (x_gc - 8, 0)], AMBER, alpha=0.5, z=3)
    a2.plot([XT, XT], [Y, Y - 70], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=5)
    callout(a2, (face_x(Y + 20), Y + 20), (70, 175), f"end polished at {phi_pol:.0f}°:\ntotal internal reflection\n(incidence {inc:.0f}° > {crit:.1f}°)", ha="center")
    label(a2, XT - 10, 30, f"{TH:.0f}° from\nvertical", fs=FS_SMALL, ha="right")
    label(a2, -205, 222, "glass block", fs=FS_SMALL, ha="left")
    label(a2, -205, Y + 22, "fibre", fs=FS_SMALL, ha="left")
    callout(a2, (x_gc + 14, -4), (60, -35), "grating coupler", ha="left")
    panel(a2, "b", 0.0, 1.0)
    note(a2, "schematic; angles to scale", "lower right")
    save(fig, "ch17_arrays")
    print(f"Fig 17.2: fibres at {TH} deg, face parallel to chip: {th_air:.2f} deg in air, {TH} deg in the oxide; "
          f"low-profile polish {phi_pol:.1f} deg, incidence {inc:.1f} deg vs critical {crit:.2f} deg; beam {TH} deg from vertical")


# =====================================================================================================
# Figure 17.3: a photonic wire bond and printed micro-lenses (schematic side views)
# =====================================================================================================
def fig_pwb():
    fig = plt.figure(figsize=(6.3, 2.3))
    a1 = fig.add_axes([0.0, 0.0, 0.5, 1.0]); frameless(a1, (0, 100), (0, 62), equal=False)
    a2 = fig.add_axes([0.52, 0.0, 0.48, 1.0]); frameless(a2, (0, 100), (0, 62), equal=False)
    # (a) photonic wire bond between an InP laser and a silicon chip on a common submount
    box(a1, 2, 4, 96, 8, "al")
    box(a1, 6, 12, 34, 22, "inp"); box(a1, 6, 28.5, 34, 2.2, "q", z=2); box(a1, 6, 34, 34, 2.0, "metal", z=2)
    box(a1, 56, 12, 40, 14, "sub"); box(a1, 56, 26, 40, 4, "ox"); box(a1, 56, 30, 40, 1.0, "si", z=2); box(a1, 56, 31, 40, 3, "oxtop")
    xs = np.linspace(40, 60, 100)
    ys = 29.6 + (30.5 - 29.6) * (1 - np.cos(np.pi * (xs - 40) / 20)) / 2 + 9 * np.sin(np.pi * (xs - 40) / 20)
    a1.fill_between(np.linspace(38, 62, 50), 20, 44, color=MAT["polymer"], alpha=0.55, lw=0, zorder=1)
    ribbon(a1, xs, ys, 1.6, VIOLET, z=4)
    label(a1, 23, 22, "InP laser", fs=FS_SMALL)
    callout(a1, (30, 29.6), (24, 44), "active region", ha="center")
    label(a1, 76, 19, "Si PIC", fs=FS_SMALL)
    callout(a1, (90, 30.5), (84, 44), "waveguide", ha="center")
    callout(a1, (50, 38.6), (50, 54), "photonic wire bond: a polymer waveguide\nwritten in 3D where the chips actually are", ha="center")
    label(a1, 50, 7.8, "submount", fs=FS_SMALL)
    panel(a1, "a", 0.0, 1.0)
    # (b) printed micro-lenses on a laser facet and on a fibre end
    box(a2, 2, 14, 26, 22, "inp"); box(a2, 2, 24, 26, 2.0, "q", z=2)
    th = np.linspace(-np.pi / 2, np.pi / 2, 40)
    poly(a2, np.c_[28 + 5.5 * np.cos(th), 25 + 8 * np.sin(th)], "polymer", z=3, ec=VIOLET, lw=0.6)
    box(a2, 64, 13, 34, 24, "glass", ec=MUTED, lw=0.5); box(a2, 64, 23.6, 34, 2.8, "core", z=2)
    poly(a2, np.c_[64 - 5.5 * np.cos(th), 25 + 8 * np.sin(th)], "polymer", z=3, ec=VIOLET, lw=0.6)
    # beam: diverging from the laser facet, collimated by its lens, refocused by the fibre's lens
    a2.fill_between([28, 31.5], [24.6, 18.0], [25.4, 32.0], color=AMBER, alpha=0.45, lw=0, zorder=2)
    a2.fill_between([31.5, 60.5], [18.0, 18.0], [32.0, 32.0], color=AMBER, alpha=0.45, lw=0, zorder=2)
    a2.fill_between([60.5, 66], [18.0, 24.4], [32.0, 25.6], color=AMBER, alpha=0.45, lw=0, zorder=2)
    label(a2, 14, 30.5, "laser", fs=FS_SMALL)
    label(a2, 82, 31.5, "fibre", fs=FS_SMALL)
    callout(a2, (31, 30), (24, 47), "printed lens\non the laser facet", ha="center")
    callout(a2, (60, 30), (70, 47), "printed lens\non the fibre end", ha="center")
    label(a2, 46, 12, "wider beam in the gap:\nlooser alignment", fs=FS_SMALL)
    panel(a2, "b", 0.0, 1.0)
    note(a2, "schematic", "lower right")
    save(fig, "ch17_pwb")
    print("Fig 17.3: schematic (no numbers)")


# =====================================================================================================
# Section 17.5: facet-attached microlenses (FaML). One shared model for Figure 17.4, the text and the faml demo.
# A printed lens is a polymer body on the facet (n = 1.53, the resist index reported by Xu et al. 2023) in which the
# device's Gaussian mode expands from waist w0 to the target waist W; its far end is an ellipsoid of eccentricity
# 1/n whose far focus sits at the centre of curvature of the arriving wavefront, which turns that wavefront flat
# (a Cartesian oval for a point source inside the lens, collimating into air). The beam leaves with its waist W at
# the apex. Paraxial Gaussian optics; aberrations, the edge coupler's own loss and its ellipticity are left out.
# =====================================================================================================
LAM, N_LENS = 1.55, 1.53
W_CHIP, W_FIB, W_EXP = 1.25, 5.2, 12.5          # 1/e^2 radii: edge coupler (MFD 2.5 um), SMF-28 (10.4 um), expanded beam (25 um)


def faml_lens(w0, W, n=N_LENS, lam=LAM):
    """Length of polymer that expands waist w0 to W, the wavefront radius there, and the collimating ellipse (a, b, c)."""
    zr = math.pi * n * w0 ** 2 / lam
    L = zr * math.sqrt((W / w0) ** 2 - 1)
    R = L * (1 + (zr / L) ** 2)
    e = 1 / n
    a = R / (1 + e)
    return dict(zr=zr, L=L, R=R, a=a, b=a * math.sqrt(1 - e * e), c=a * e, rs=(n - 1) / n * R)


def faml_profile(w0, W, x_apex, facing=+1, rb=None, npts=80):
    """Outline (x, y) of a lens whose apex is at x_apex, emitting towards +x (facing=+1) or -x (-1). rb: body radius."""
    P = faml_lens(w0, W); rb = rb or 1.6 * W
    xs_f = x_apex - facing * P["R"]                    # far focus: the centre of curvature of the arriving wavefront
    xc = xs_f + facing * P["c"]
    ys = np.linspace(-rb, rb, npts)
    xcap = xc + facing * P["a"] * np.sqrt(np.clip(1 - (ys / P["b"]) ** 2, 0, 1))
    x_base = x_apex - facing * P["L"]                  # the facet the lens stands on
    return np.r_[x_base, xcap, x_base], np.r_[-rb, ys, rb], P


def eta_offset(d, w1, w2):
    return math.exp(-2 * d * d / (w1 * w1 + w2 * w2))


def eta_tilt(th, w1, w2, n=1.0, lam=LAM):
    return math.exp(-2 * (math.pi * n * th / lam) ** 2 * w1 * w1 * w2 * w2 / (w1 * w1 + w2 * w2))


def eta_gap(g, w, n=1.0, lam=LAM):
    zr = math.pi * n * w * w / lam
    return 1 / (1 + (g / (2 * zr)) ** 2)


def tol1db(f, hi):
    lo = 0.0
    for _ in range(80):
        m = (lo + hi) / 2
        if f(m) > 10 ** -0.1: lo = m
        else: hi = m
    return (lo + hi) / 2


def faml_numbers():
    pc, pf = faml_lens(W_CHIP, W_EXP), faml_lens(W_FIB, W_EXP)
    out = {}
    for name, w in (("lensed", W_CHIP), ("faml", W_EXP)):
        out[name] = dict(d=tol1db(lambda d: eta_offset(d, w, w), 50), th=math.degrees(tol1db(lambda t: eta_tilt(t, w, w), 1.0)),
                         g=tol1db(lambda g: eta_gap(g, w), 5000), zr=math.pi * w * w / LAM)
        out[name]["rot"] = math.degrees(out[name]["d"] / (7 * PITCH))
    Rf = ((N_LENS - 1) / (N_LENS + 1)) ** 2; Rs = ((N_GL - 1) / (N_GL + 1)) ** 2
    out["fresnel_faml"] = -20 * math.log10(1 - Rf); out["fresnel_lensed"] = -20 * math.log10(1 - Rs)
    out["chip"], out["fibre"] = pc, pf
    return out


def fig_faml():
    F = faml_numbers(); pc, pf = F["chip"], F["fibre"]
    GAP = 150.0
    Lc, Lf = pc["L"], pf["L"]; xa = Lc + GAP; xF = xa + Lf
    fig = plt.figure(figsize=(6.3, 3.85))
    # ---------------- (a) side view to scale
    X0, X1, Y0, Y1 = -72, xF + 64, -78, 78
    ax = fig.add_axes([0.0, 0.43, 1.0, 0.57]); frameless(ax, (X0, X1), (Y0, Y1))
    XE = 112                                                          # where the chip was diced, beyond the trench
    box(ax, X0, Y0, -X0, Y0 * -1 - 2.1, "sub")                        # substrate below the BOX
    box(ax, 0, Y0, XE, -60 - Y0, "sub")                               # ledge left by the deep trench
    box(ax, X0, -2.1, -X0, 2.0, "ox"); box(ax, X0, 0.11, -X0, 2.9, "oxtop")
    ax.plot([X0, 0], [0, 0], color=MAT["si"], lw=1.1, zorder=3, solid_capstyle="butt")
    # fibre array: one fibre in its groove, lid above, V-groove chip below
    box(ax, xF, -62.5, X1 - xF, 125, "glass", ec=MUTED, lw=0.5, z=2)
    box(ax, xF, -4.1, X1 - xF, 8.2, "core", z=3)
    box(ax, xF, 62.5, X1 - xF, Y1 - 62.5, "glass", ec=MUTED, lw=0.5, z=2)
    box(ax, xF, Y0, X1 - xF, -62.5 - Y0, "si", z=2)
    # the two lenses
    x, y, _ = faml_profile(W_CHIP, W_EXP, Lc, +1); poly(ax, np.c_[x, y], "polymer", ec=VIOLET, lw=0.6, z=4)
    x, y, _ = faml_profile(W_FIB, W_EXP, xa, -1); poly(ax, np.c_[x, y], "polymer", ec=VIOLET, lw=0.6, z=4)
    # the beam (1/e^2 radius): expanding in the chip lens, collimated in the gap, focused by the fibre lens
    z1 = np.linspace(0, Lc, 120); w1 = W_CHIP * np.sqrt(1 + (z1 / pc["zr"]) ** 2)
    zr_air = math.pi * W_EXP ** 2 / LAM
    z2 = np.linspace(Lc, xa, 60); w2 = W_EXP * np.sqrt(1 + ((z2 - Lc) / zr_air) ** 2)
    z3 = np.linspace(xa, xF, 160); w3 = W_FIB * np.sqrt(1 + ((xF - z3) / pf["zr"]) ** 2)
    xb = np.r_[X0, z1, z2, z3, X1]; wb = np.r_[W_CHIP, w1, w2, w3, W_FIB]
    ax.fill_between(xb, -wb, wb, color=AMBER, alpha=0.5, lw=0, zorder=5)
    ax.plot([X0, X1], [0, 0], color=MUTED, lw=0.5, ls=(0, (3, 3)), zorder=6)
    # labels
    callout(ax, (-40, 0.5), (-68, 30), "Si edge coupler\nMFD 2.5 µm", ha="left")
    callout(ax, (Lc * 0.55, 18), (14, 58), f"printed lens on the chip facet\nn = {N_LENS}, {Lc:.0f} µm long", ha="left")
    label(ax, (Lc + xa) / 2, 21, f"collimated beam\nMFD {2 * W_EXP:.0f} µm", fs=FS_SMALL)
    dim(ax, (Lc, -30), (xa, -30), f"air gap {GAP:.0f} µm", bg=None, text_off=(0, -7))
    callout(ax, (xa + Lf * 0.55, 19), (xa + Lf * 0.25, 52), f"printed lens on the fibre, {Lf:.0f} µm long", ha="left")
    label(ax, xF + 32, 34, "fibre\narray", fs=FS_SMALL)
    callout(ax, (xF + 14, -2), (xF + 30, -36), "SMF core\nMFD 10.4 µm", ha="center")
    label(ax, -36, -45, "Si chip", fs=FS_SMALL)
    label(ax, XE / 2 + 4, -69, "deep-etched trench", fs=FS_SMALL)
    scalebar(ax, XE + 40, -68, 100, "100 µm")
    label(ax, XE + 205, -68, "to scale", fs=6.0, col=MUTED, italic=True)
    panel(ax, "a", 0.0, 1.0)
    # ---------------- (b)-(d) tolerances
    axs = [fig.add_axes([0.075 + k * 0.33, 0.085, 0.255, 0.27]) for k in range(3)]
    cols = {"lensed": C2, "faml": C1}
    names = {"lensed": "lensed fibre on taper", "faml": "FaML pair"}
    ws = {"lensed": W_CHIP, "faml": W_EXP}
    d = np.linspace(0, 10, 400); t = np.linspace(0, 15, 400); g = np.logspace(-1, 3, 400)
    for k in ("lensed", "faml"):
        w = ws[k]
        axs[0].plot(d, [10 * math.log10(eta_offset(v, w, w)) for v in d], color=cols[k], label=names[k])
        axs[1].plot(t, [10 * math.log10(eta_tilt(math.radians(v), w, w)) for v in t], color=cols[k])
        axs[2].plot(g, [10 * math.log10(eta_gap(v, w)) for v in g], color=cols[k])
    for a_ in axs:
        a_.axhline(-1, color=MUTED, lw=0.7, ls=(0, (3, 3))); a_.set_ylim(-6, 0.3); a_.set_yticks([-6, -4, -2, -1, 0])
    axs[2].set_xscale("log"); axs[2].set_xlim(0.1, 1000)
    axs[0].set_xlim(0, 10); axs[1].set_xlim(0, 15)
    finish(axs[0], "lateral offset (µm)", "coupling change (dB)"); finish(axs[1], "tilt (°)"); finish(axs[2], "gap (µm)")
    a0 = axs[0]
    a0.text(F["lensed"]["d"] + 0.5, -0.45, f"±{F['lensed']['d']:.2f} µm", color=C2, fontsize=6.6, ha="left", va="top")
    a0.text(F["faml"]["d"] - 0.25, -1.35, f"±{F['faml']['d']:.1f} µm", color=C1, fontsize=6.6, ha="right", va="top")
    axs[1].text(F["faml"]["th"] + 0.8, -0.45, f"{F['faml']['th']:.2f}°", color=C1, fontsize=6.6, ha="left", va="top")
    axs[1].text(F["lensed"]["th"] - 0.3, -1.35, f"{F['lensed']['th']:.1f}°", color=C2, fontsize=6.6, ha="right", va="top")
    axs[2].text(F["lensed"]["g"] / 1.3, -1.35, f"{F['lensed']['g']:.1f} µm", color=C2, fontsize=6.6, ha="right", va="top")
    axs[2].text(F["faml"]["g"] / 1.25, -1.35, f"{F['faml']['g']:.0f} µm", color=C1, fontsize=6.6, ha="right", va="top")
    axs[0].legend(loc="lower left", fontsize=6.3, handlelength=1.4)
    for a_, s in zip(axs, "bcd"): tag(a_, s)
    save(fig, "ch17_faml")
    print(f"Fig 17.4: chip lens {Lc:.1f} um (zR {pc['zr']:.2f} um in polymer, wavefront R {pc['R']:.1f} um, apex radius {pc['rs']:.1f} um,"
          f" ellipse a {pc['a']:.1f} b {pc['b']:.1f}); fibre lens {Lf:.1f} um (zR {pf['zr']:.1f}, R {pf['R']:.1f}, apex radius {pf['rs']:.1f})")
    for k in ("lensed", "faml"):
        v = F[k]
        print(f"  {k:7s} w {ws[k]:5.2f}: 1 dB offset +-{v['d']:.2f} um, tilt {v['th']:.2f} deg, gap {v['g']:.1f} um (zR {v['zr']:.1f} um),"
              f" rotation of an 8-fibre array about one end {v['rot']:.3f} deg")
    print(f"  Fresnel, two uncoated surfaces: polymer {F['fresnel_faml']:.2f} dB, silica {F['fresnel_lensed']:.2f} dB;"
          f" truncation at 1.6 W {100 * math.exp(-2 * 1.6 ** 2):.2f} %")
    for W in (5.0, 10.0, 12.5, 20.0):
        print(f"  W = {W:4.1f} um: chip lens {faml_lens(W_CHIP, W)['L']:6.1f} um, fibre lens {faml_lens(W_FIB, W)['L'] if W > W_FIB else float('nan'):6.1f} um,"
              f" 1 dB offset {math.sqrt(0.115 * 2 * W * W):.2f} um, tilt {math.degrees(tol1db(lambda t: eta_tilt(t, W, W), 1.0)):.2f} deg")


# =====================================================================================================
# Figure 17.5: how facet-attached microlenses are made (schematic)
# =====================================================================================================
def _chip_edge(ax, x0=4, xf=46, yw=52, bot=24, floor=32):
    """Side view of a chip ending at a deep-etched facet at xf (schematic heights)."""
    box(ax, x0, bot, xf - x0, yw - 4 - bot, "sub")
    box(ax, xf, bot, 22, floor - bot, "sub")
    box(ax, x0, yw - 4, xf - x0, 3.4, "ox"); box(ax, x0, yw - 0.6, xf - x0, 1.2, "si", z=2); box(ax, x0, yw + 0.6, xf - x0, 4, "oxtop")


def _lens_shape(ax, xf, yw, L=15, rb=8, z=4, alpha=1.0, ls="-", facing=1):
    t = np.linspace(-1, 1, 60)
    xs = np.r_[xf, xf + facing * (L - 6 + 6 * np.sqrt(1 - t ** 2)), xf]
    ys = np.r_[yw - rb, yw + rb * t, yw + rb]
    poly(ax, np.c_[xs, ys], "polymer", ec=VIOLET, lw=0.7, z=z, alpha=alpha, ls=ls)


def fig_famlprint():
    fig = plt.figure(figsize=(6.3, 1.95))
    W_ = 0.25
    titles = ["1 · find the waveguide", "2 · write the lens", "3 · develop", "4 · assemble"]
    texts = ["camera finds the waveguide\nend or printed markers\n(to about 0.1 µm)",
             "the fs-laser focus hardens\nthe resist only where it is\nbrightest: voxel by voxel",
             "solvent washes away the\nunexposed resist; optional\nUV flood cure",
             "camera or mechanical stops\nplace the parts: the wide\nbeam forgives µm errors"]
    yw, xf, floor = 52, 46, 32
    for k in range(4):
        ax = fig.add_axes([k * W_, 0.0, W_ - 0.008, 0.9]); frameless(ax, (0, 100), (0, 80), equal=False)
        ax.text(2, 79, titles[k], fontsize=FS, color=INK, fontweight="bold", va="top")
        label(ax, 50, 10, texts[k], fs=FS_SMALL)
        if k < 3:
            _chip_edge(ax, xf=xf, yw=yw, floor=floor)
        if k == 0:
            box(ax, 62, 62, 16, 8, "#DDE3EC", ec=INK, lw=0.6, z=5); poly(ax, [(67, 62), (73, 62), (75, 58), (65, 58)], "#C5CEDB", ec=INK, lw=0.6, z=5)
            arrow(ax, (68, 57), (xf + 2.5, yw + 2.5), col=BLUE, lw=0.8, ms=6, ls=(0, (2, 2)))
            ax.plot([xf - 5, xf + 5], [yw, yw], color=RED, lw=0.7, zorder=6); ax.plot([xf, xf], [yw - 5, yw + 5], color=RED, lw=0.7, zorder=6)
            ax.add_patch(Circle((xf, yw), 3.0, fc="none", ec=RED, lw=0.7, zorder=6))
            label(ax, 84, 72, "camera", fs=FS_SMALL)
        elif k == 1:
            t = np.linspace(0, np.pi / 2, 40)
            poly(ax, np.c_[np.r_[xf, xf + 30 * np.cos(t)], np.r_[floor, floor + 30 * np.sin(t)]], "#EADFF3", alpha=0.9, z=3)
            _lens_shape(ax, xf, yw, z=4, alpha=0.35, ls=(0, (2, 2)))
            xfo, yfo = xf + 9, yw + 4
            poly(ax, [(xfo - 8, 76), (xfo + 8, 76), (xfo + 5, 67), (xfo - 5, 67)], "#C5CEDB", ec=INK, lw=0.6, z=6)
            poly(ax, [(xfo - 5, 67), (xfo + 5, 67), (xfo, yfo)], RED, alpha=0.35, z=5)
            ax.add_patch(Ellipse((xfo, yfo), 1.6, 3.0, fc=RED, ec="none", zorder=7))
            callout(ax, (xfo + 5, 72), (84, 72), "objective", ha="center")
            callout(ax, (xf + 24, floor + 16), (86, 50), "liquid\nresist", ha="center")
        elif k == 2:
            _lens_shape(ax, xf, yw)
            for yy in (60, 66):
                arrow(ax, (xf + 24, yy), (xf + 36, yy + 4), col=MUTED, lw=0.8, ms=6)
            callout(ax, (xf + 10, yw - 5), (84, 42), "solid lens,\naligned to the\nwaveguide", ha="center")
        else:
            box(ax, 2, 20, 96, 4, "al")
            box(ax, 2, 24, 24, 22, "sub"); box(ax, 2, 46, 24, 3.4, "ox"); box(ax, 2, 49.4, 24, 1.2, "si", z=2); box(ax, 2, 50.6, 24, 4, "oxtop")
            _lens_shape(ax, 26, 50, L=10, rb=6)
            box(ax, 74, 24, 24, 44, "glass", ec=MUTED, lw=0.5); box(ax, 74, 48.8, 24, 2.4, "core", z=2)
            _lens_shape(ax, 74, 50, L=10, rb=6, facing=-1)
            box(ax, 36, 45.5, 28, 9, AMBER, alpha=0.5, z=3)
            for x_, sg in ((26, 1), (74, -1)):
                poly(ax, [(x_, 24), (x_ + sg * 6, 24), (x_, 30)], "epoxy", ec=MUTED, lw=0.4, z=5)
            label(ax, 50, 33, "glue clear\nof the beam", fs=FS_SMALL)
            label(ax, 14, 35, "chip", fs=FS_SMALL); label(ax, 86, 38, "fibre\narray", fs=FS_SMALL)
    save(fig, "ch17_famlprint")
    print("Fig 17.5: schematic (no numbers beyond the ~0.1 um alignment of Xu et al. 2023)")


# =====================================================================================================
# Figure 17.6: flip-chip laser on a silicon chip, height set by pedestals (schematic cross-section)
# =====================================================================================================
def fig_flipchip():
    """Cleaner construction: heights chosen so that the laser's active layer lines up with the Si waveguide."""
    fig = plt.figure(figsize=(6.3, 2.5))
    ax = fig.add_axes([0, 0, 1, 1]); frameless(ax, (0, 160), (-2, 66), equal=False)
    Y_SUB, T_BOX, T_SI, T_CL = 22.0, 5.0, 1.6, 5.0         # schematic heights (layers exaggerated)
    y_wg = Y_SUB + T_BOX + T_SI / 2                           # waveguide centre
    XR = 96
    # PIC
    box(ax, 2, 2, 156, Y_SUB - 2, "sub")
    box(ax, XR, Y_SUB, 160 - XR - 2, T_BOX, "ox"); box(ax, XR, Y_SUB + T_BOX, 160 - XR - 2, T_SI, "si", z=2)
    box(ax, XR, Y_SUB + T_BOX + T_SI, 160 - XR - 2, T_CL, "oxtop")
    box(ax, 2, Y_SUB, 5, T_BOX + T_SI + T_CL, "sub")
    # the laser, flipped: bottom contact, p-cladding, active layer at y_wg, then the InP substrate
    T_CON, T_PCL, T_ACT = 0.9, 2.4, 1.2
    y_act0 = y_wg - T_ACT / 2
    y_bot = y_act0 - T_PCL - T_CON                            # bottom of the laser die
    LX0, LX1 = 16, XR - 1.0
    box(ax, LX0, y_bot, LX1 - LX0, T_CON, "metal", z=4)
    box(ax, LX0, y_bot + T_CON, LX1 - LX0, T_PCL, "inp", z=4)
    box(ax, LX0, y_act0, LX1 - LX0, T_ACT, "q", z=4)
    box(ax, LX0, y_act0 + T_ACT, LX1 - LX0, 60 - (y_act0 + T_ACT), "inp", z=4)
    # pedestals: the die rests on them, so their height sets the vertical alignment
    for xp in (22, 78):
        box(ax, xp, Y_SUB, 7, y_bot - Y_SUB, "si", ec=INK, lw=0.6, z=3)
    for xp in (38, 56):
        box(ax, xp, Y_SUB, 11, y_bot - Y_SUB, "metal", alpha=0.7, z=3)
    # light from the laser into the edge coupler
    arrow(ax, (LX1 - 18, y_wg), (XR + 16, y_wg), col=RED, lw=1.4, ms=9, z=8)
    # labels
    label(ax, (LX0 + LX1) / 2, 46, "III–V laser, flipped (epitaxy down)", fs=FS)
    callout(ax, (30, y_wg + 0.2), (26, 38), "active region", ha="center")
    callout(ax, (25.5, Y_SUB + 1.5), (12, 12), "pedestal: sets the height", ha="left")
    callout(ax, (43.5, Y_SUB + 1.5), (52, 8), "solder", ha="left")
    callout(ax, (XR + 0.3, y_wg), (110, 45), "edge coupler at the\nrecess wall", ha="center")
    label(ax, 128, 12, "Si PIC", fs=FS)
    label(ax, 128, Y_SUB + T_BOX / 2, "BOX", fs=FS_SMALL)
    label(ax, 128, Y_SUB + T_BOX + T_SI + T_CL / 2, "cladding", fs=FS_SMALL)
    callout(ax, (8, Y_SUB + 3), (8, 40), "recess etched\ninto the PIC", ha="center")
    note(ax, "schematic, layers exaggerated", "lower right")
    save(fig, "ch17_flipchip")
    print("Fig 17.6: schematic (no numbers)")


# =====================================================================================================
# Figure 17.7: pluggable modules against co-packaged optics (schematic top views of a switch board)
# =====================================================================================================
def fig_cpo():
    PCB, PKG = "#EEF1F4", "#DDE3EA"
    fig = plt.figure(figsize=(6.3, 2.75))
    a1 = fig.add_axes([0.0, 0.0, 0.49, 1.0]); frameless(a1, (0, 100), (0, 92))
    a2 = fig.add_axes([0.51, 0.0, 0.49, 1.0]); frameless(a2, (0, 100), (0, 92))
    for ax in (a1, a2):
        box(ax, 8, 4, 90, 80, PCB, ec=MUTED, lw=0.6)
        box(ax, 2, 4, 6, 80, "#C9D0DA", ec=MUTED, lw=0.6)
        label(ax, 5, 88, "front panel", fs=FS_SMALL, ha="left")
    # (a) pluggable: modules at the front panel, long electrical traces from the switch chip
    ys = [12, 26, 40, 54, 68]
    block(a1, 66, 44, 22, 22, "switch\nASIC", fc=PKG, fs=FS)
    for y in ys:
        block(a1, 9, y + 3, 14, 9, "", fc="#F7E7C6", ec=AMBER, lw=0.8)
        for k in (-1.2, 1.2):
            a1.plot([16, 30, 55], [y + 3 + k, y + 3 + k, 44 + (y - 40) * 0.25 + k], color=ELEC, lw=0.8, zorder=2)
        a1.plot([-2, 2], [y + 3, y + 3], color=OPT, lw=1.4, zorder=2)
    label(a1, 10, 77.5, "pluggable modules", fs=FS_SMALL, ha="left", va="bottom")
    dim(a1, (16, 6.5), (55, 6.5), "electrical: tens of cm", fs=FS_SMALL, col=ELEC, bg=PCB)
    panel(a1, "a", 0.0, 1.0)
    # (b) co-packaged optics: optical engines on the switch package, lasers in front-panel modules
    block(a2, 64, 44, 40, 40, "", fc=PKG, ec=INK, lw=0.8)
    block(a2, 64, 44, 16, 16, "switch\nASIC", fc="#C9D0DA", fs=FS)
    eng = [(64, 59), (64, 29), (49, 44), (79, 44)]
    for (x, y) in eng:
        block(a2, x, y, 8 if x in (49, 79) else 12, 12 if x in (49, 79) else 8, "", fc="#F7E7C6", ec=AMBER, lw=0.8, z=4)
    a2.plot([56, 60], [44, 44], color=ELEC, lw=1.4, zorder=5)
    label(a2, 64, 67.5, "optical engines (PIC + driver)", fs=FS_SMALL)
    # fibres from engines to the front panel, and laser feeds from the external laser modules
    for (x, y), yf in zip(eng, (70, 20, 46, 58)):
        a2.plot([x - 2, 30, 8], [y, yf, yf], color=OPT, lw=1.0, zorder=3)
    for yl in (12, 76):
        block(a2, 12, yl, 12, 8, "laser", fc="#F2D4CF", ec=RED, lw=0.8, fs=FS_SMALL)
        a2.plot([18, 40, 58], [yl, yl, 44 + (yl - 44) * 0.45], color=OPT, lw=0.9, ls=(0, (3, 2)), zorder=3)
    label(a2, 25, 88, "lasers in front-panel modules, fed in by fibre", fs=FS_SMALL, ha="left")
    callout(a2, (57, 44), (50, 90 - 82), "electrical: millimetres", col=ELEC, ha="center")
    panel(a2, "b", 0.0, 1.0)
    note(a2, "schematic", "lower right")
    save(fig, "ch17_cpo")
    print("Fig 17.7: schematic (no numbers beyond the chapter's 'tens of cm' and 'millimetres')")


# =====================================================================================================
# Figure 17.8: a test layout for a fibre array (to scale), and a packaging template (illustrative)
# =====================================================================================================
def _gc(ax, x, y, L=30.0, half=20.0):
    """Focusing grating coupler footprint: a sector with its apex (the waveguide end) at (x, y), opening to -x."""
    ph = np.radians(np.linspace(-half, half, 12))
    poly(ax, np.vstack([[[x, y]], np.c_[x - L * np.cos(ph), y + L * np.sin(ph)]]), "si", z=3)
    for r in np.arange(14, L, 1.8):
        ax.plot(x - r * np.cos(ph), y + r * np.sin(ph), color="#7C93B0", lw=0.35, zorder=4)


def fig_layout():
    fig = plt.figure(figsize=(6.3, 3.7))
    a1 = fig.add_axes([0.0, 0.0, 0.56, 1.0]); frameless(a1, (-150, 560), (-95, 1040))
    N = 8
    ys = [i * PITCH for i in range(N)][::-1]           # top to bottom
    # fibre array footprint over the column
    a1.add_patch(Rectangle((-120, -40), 170, (N - 1) * PITCH + 80, fc="none", ec=MUTED, lw=0.8, ls=(0, (4, 3)), zorder=2))
    label(a1, -35, -62, "fibre array footprint", fs=FS_SMALL, col=MUTED)
    WG = dict(color="#5F7896", lw=0.9, zorder=3)
    for y in ys:
        _gc(a1, 0.0, y)
        a1.plot([0, 40], [y, y], **WG)
    # loopback: outermost pair
    a1.plot([40, 430, 430, 40], [ys[0], ys[0], ys[-1], ys[-1]], **WG)
    label(a1, 438, (ys[0] + ys[-1]) / 2, "loopback\n(outermost\npair)", fs=FS_SMALL, ha="left")
    # circuit 1: add-drop ring; input GC2, drop GC3, through GC4
    r = PITCH / 2 - 6
    rc = (200, (ys[1] + ys[2]) / 2)
    a1.add_patch(Circle(rc, r, fc="none", ec="#5F7896", lw=0.9, zorder=3))
    a1.plot([40, 300, 300, 40], [ys[1], ys[1], ys[3], ys[3]], **WG)
    a1.plot([40, 270], [ys[2], ys[2]], **WG)
    label(a1, rc[0], rc[1], "ring", fs=FS_SMALL, col=MUTED)
    # circuit 2: MZI; input GC5, outputs GC6 and GC7
    y4 = ys[4]
    a1.plot([40, 130], [y4, y4], **WG)
    a1.plot([130, 165, 285, 320], [y4, y4 + 28, y4 + 28, y4], **WG)
    a1.plot([130, 165, 285, 320], [y4, y4 - 28, y4 - 28, y4], **WG)
    box(a1, 315, y4 - 14, 22, 28, "si", z=3)
    a1.plot([337, 390, 390, 40], [y4 + 8, y4 + 8, ys[6], ys[6]], **WG)
    a1.plot([337, 365, 365, 40], [y4 - 8, y4 - 8, ys[5], ys[5]], **WG)
    label(a1, 225, y4 + 52, "MZI", fs=FS_SMALL, col=MUTED)
    # test labels at each circuit's input coupler
    for y, txt in ((ys[1], "opt_in_TE_1550_ring1"), (ys[4], "opt_in_TE_1550_mzi1")):
        label(a1, -128, y + 36, txt, fs=6.0, ha="left", col=RED)
    label(a1, -95, 1030, "all couplers face the same way;\na test label at each input", fs=FS_SMALL, ha="left", va="top")
    dim(a1, (75, ys[6]), (75, ys[7]), "", fs=FS_SMALL)
    label(a1, 83, (ys[6] + ys[7]) / 2, "127 µm", fs=FS_SMALL, ha="left")
    scalebar(a1, 380, -80, 100, "100 µm")
    panel(a1, "a", 0.0, 1.0)
    # (b) packaging template: edge couplers on one polished edge, pads on the others (illustrative)
    a2 = fig.add_axes([0.58, 0.05, 0.42, 0.9]); frameless(a2, (-12, 100), (-6, 100))
    box(a2, 0, 0, 90, 90, "#EEF1F4", ec=INK, lw=0.9)
    box(a2, 0, 0, 9, 90, "#F2D4CF", alpha=0.7)
    for k in range(8):
        y = 25 + k * 5.5
        a2.plot([0, 18], [y, y], color="#5F7896", lw=0.9, zorder=3)
    box(a2, -9, 22, 9, 44, "glass", ec=MUTED, lw=0.6)
    for k in range(12):
        box(a2, 20 + k * 5.6, 83, 3.2, 3.2, "metal", z=3)
        box(a2, 20 + k * 5.6, 3.8, 3.2, 3.2, "metal", z=3)
    label(a2, 50, 77, "bond pads on a standard pitch", fs=FS_SMALL)
    label(a2, 50, 12.5, "bond pads", fs=FS_SMALL)
    callout(a2, (4.5, 72), (30, 62), "keep-out zone at\nthe polished edge", ha="left")
    callout(a2, (16, 36), (40, 42), "edge couplers at\nfixed positions", ha="left")
    callout(a2, (-6, 60), (-10, 96), "fibre array", ha="left")
    panel(a2, "b", -0.02, 1.08)
    note(a2, "illustrative", "lower right")
    save(fig, "ch17_layout")
    print(f"Fig 17.8: {N} couplers on a {PITCH:.0f} um pitch, span {(N - 1) * PITCH:.0f} um")


FIGS = {"vgroove": fig_vgroove, "arrays": fig_arrays, "pwb": fig_pwb, "faml": fig_faml, "famlprint": fig_famlprint,
        "flipchip": fig_flipchip, "cpo": fig_cpo, "layout": fig_layout}

if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for nme in names:
        FIGS[nme]()
