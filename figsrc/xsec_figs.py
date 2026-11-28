"""Dimensioned facet cross-sections of the lasers and amplifiers of Section 24.9, with their computed modes.

Run from the repository root:  python -I -X utf8 figsrc/xsec_figs.py [ridge bh vcsel hetero soa]
Draws assets/figs/ch24_xsec_*.svg from the stacks of xsec_devices.py, the modes of xsec_modes.json (finite-difference
and transfer-matrix solutions, see xsec_modes.py) and, for the III-V-on-silicon laser, the femwell modes of
ch27_hybrid.json (Table 27.1). Prints the numbers the figures and captions quote.

Generic, illustrative stacks (Table 24.1, Table 27.1, Worked Example 24.2, tools/export_stacks.py): not any company's
process. Every panel is to scale (x : y = 1 : 1), in micrometres.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import save
import xsec_devices as D
from xsec_devices import COL
from xsec import draw_shapes, draw_mode, current, vdim, hdim, tag, axes_um, legend_column
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "xsec_modes.json")))
HY = json.load(open(os.path.join(HERE, "ch27_hybrid.json")))


def layout(h=4.15):
    fig = plt.figure(figsize=(6.3, h))
    a = fig.add_axes([0.075, 0.70, 0.60, 0.25])
    b = fig.add_axes([0.075, 0.075, 0.60, 0.54])
    c = fig.add_axes([0.715, 0.03, 0.285, 0.94])
    return fig, a, b, c


def zoom_box(a, x0, x1, y0, y1, lab="(b)"):
    a.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=INK, lw=0.6, ls=(0, (2, 2)), zorder=12))
    a.text(x0 + 0.12, y0 + 0.12, lab, fontsize=5.8, color=INK, zorder=12, va="bottom")


def fmt(m):
    return dict(n=f"{m['neff']:.3f}", g=f"{m['gamma']*100:.1f} %", wh=f"{m['w']:.1f} × {m['h']:.2f} µm",
                ff=f"{m['ffx']:.0f}° × {m['ffy']:.0f}°", d=f"{-m['yp']:.2f} µm")


# ====================================================================== ridge laser
def fig_ridge():
    S = D.ridge(); m = M["ridge"]; f = fmt(m)
    print(f"ridge: n_eff {f['n']}, Gamma under the ridge {f['g']}, 1/e2 {f['wh']}, far field {f['ff']}, emission {f['d']} below the epi top")
    fig, a, b, c = layout()
    draw_shapes(a, S); draw_mode(a, m["map"], star=False)
    axes_um(a, (-8, 8), (-4.0, 0.8), "(a) the facet across the chip, to scale (x : y = 1 : 1), µm")
    tag(a, -7.8, -3.62, "n-InP substrate, about 100 µm thick"); tag(a, 7.8, -3.62, "n contact underneath", ha="right")
    tag(a, -7.8, -0.75, "BCB"); tag(a, 7.8, -0.75, "BCB", ha="right"); tag(a, 3.52, 0.56, "p-metal, on to the bond pad", fs=5.6, bg=False)
    zoom_box(a, -3.4, 3.4, -3.3, 0.65)
    draw_shapes(b, S); xp, yp = draw_mode(b, m["map"], at=(m["xp"], m["yp"]))
    axes_um(b, (-3.4, 3.4), (-3.3, 0.65), "(b) the ridge: x = 0 at its centre, y = 0 at the top of the epitaxy, µm")
    current(b, [[(xx, -0.03), (xx, -1.60), (xx * 1.5, -1.98)] for xx in (-0.7, -0.25, 0.25, 0.7)])
    hdim(b, 0.40, -1.0, 1.0, "2.0")
    vdim(b, 1.85, 0.0, -1.60, "1.60, etched")
    vdim(b, 1.85, -1.60, -1.95, "0.35")
    vdim(b, -2.0, 0.0, yp, f"{-yp:.2f}", side="left")
    b.plot([-2.0, xp - 0.15], [yp, yp], color=INK, lw=0.5, ls=(0, (1, 1.5)), zorder=9)
    tag(b, -3.3, -2.85, "n-InP"); tag(b, -3.3, -1.79, "p-InP"); tag(b, -3.3, -0.8, "BCB"); tag(b, 0, -0.8, "p-InP", ha="center", bg=False)
    items = [("patch", COL["metal"], "p-metal, Ti/Pt/Au, 0.3 µm"), ("patch", COL["cap"], "p⁺⁺ InGaAs contact layer, 0.15 µm"),
             ("patch", COL["pinp"], "p-InP: ridge 1.45 µm, residual 0.33 µm"), ("patch", COL["estop"], "InGaAsP etch stop, 20 nm"),
             ("patch", COL["sin"], "SiN passivation, 0.2 µm"), ("patch", COL["bcb"], "BCB, filling the etched area"),
             ("patch", COL["sch"], "InGaAsP SCH, 40 nm each side"), ("line", COL["qw"], "5 quantum wells, 10 nm each"),
             ("patch", COL["ninp"], "n-InP buffer and substrate"), ("fill", RED, "mode: 1/e² (dashed) and half power"),
             ("star", None, "emission point: the mode's peak"), ("arrow", BLUE, "hole current, spreading a little")]
    rows = [("effective index", f["n"]), ("in the wells under the ridge", f["g"]), ("mode, 1/e² (w × h)", f["wh"]),
            ("far field, FWHM (x × y)", f["ff"]), ("emission below the epi top", f["d"])]
    legend_column(c, items, rows)
    save(fig, "ch24_xsec_ridge")


# ====================================================================== buried heterostructure
def fig_bh():
    S = D.bh(); m = M["bh"]; f = fmt(m)
    print(f"bh: n_eff {f['n']}, Gamma in the mesa {f['g']}, 1/e2 {f['wh']}, far field {f['ff']}, emission {f['d']} below the epi top")
    fig, a, b, c = layout()
    draw_shapes(a, S); draw_mode(a, m["map"], star=False)
    axes_um(a, (-8, 8), (-4.6, 0.95), "(a) the facet across the chip, to scale (x : y = 1 : 1), µm")
    tag(a, -7.8, -4.25, "n-InP substrate, about 100 µm thick"); tag(a, 7.8, -4.25, "n contact underneath", ha="right"); tag(a, -7.8, -2.65, "Fe:InP"); tag(a, 7.8, -2.65, "Fe:InP", ha="right")
    tag(a, -7.8, -1.1, "p-InP overgrowth"); tag(a, 7.8, 0.78, "p-metal", ha="right", bg=False)
    zoom_box(a, -3.2, 3.2, -3.8, 0.85)
    draw_shapes(b, S); xp, yp = draw_mode(b, m["map"], at=(m["xp"], m["yp"]))
    axes_um(b, (-3.2, 3.2), (-3.8, 0.85), "(b) the buried mesa: x = 0 at its centre, y = 0 at the top of the epitaxy, µm")
    current(b, [[(-1.5, -0.03), (-0.5, -2.0), (-0.5, -2.32)], [(-0.5, -0.03), (-0.17, -2.0), (-0.17, -2.32)],
                [(0.5, -0.03), (0.17, -2.0), (0.17, -2.32)], [(1.5, -0.03), (0.5, -2.0), (0.5, -2.32)]])
    b.plot([2.5, 2.5], [-0.03, -2.05], color=BLUE, lw=0.8, ls=(0, (2, 2)), zorder=7)
    b.plot([2.5], [-2.2], marker="x", ms=6, mew=1.3, color=RED, zorder=8)
    tag(b, 2.45, -2.75, "Fe:InP is semi-\ninsulating: no\ncurrent here", ha="center")
    hdim(b, -3.48, -0.75, 0.75, "1.5", above=False)
    vdim(b, -2.3, 0.0, yp, f"{-yp:.2f}", side="left")
    b.plot([-2.3, xp - 0.15], [yp, yp], color=INK, lw=0.5, ls=(0, (1, 1.5)), zorder=9)
    tag(b, -3.1, -0.55, "p-InP"); tag(b, -3.1, -3.62, "n-InP"); tag(b, -3.1, -2.75, "Fe:InP")
    items = [("patch", COL["metal"], "p-metal, opened onto the contact"), ("patch", COL["cap"], "p⁺⁺ InGaAs contact layer, 0.2 µm"),
             ("patch", COL["sin"], "SiN, 0.2 µm, open over the mesa"), ("patch", COL["pinp"], "p-InP: 1.8 µm overgrowth, 0.25 µm mesa"),
             ("patch", COL["grating"], "InGaAsP DFB grating, 50 nm (averaged)"), ("patch", COL["fe"], "Fe:InP, semi-insulating regrowth"),
             ("patch", COL["sch"], "InGaAsP SCH, 40 nm each side"), ("line", COL["qw"], "5 quantum wells, 10 nm each"),
             ("patch", COL["ninp"], "n-InP, mesa etched 0.8 µm into it"), ("fill", RED, "mode: 1/e² (dashed) and half power"),
             ("star", None, "emission point: the mode's peak"), ("arrow", BLUE, "hole current, funnelled into the mesa")]
    rows = [("effective index", f["n"]), ("in the wells", f["g"]), ("mode, 1/e² (w × h)", f["wh"]),
            ("far field, FWHM (x × y)", f["ff"]), ("emission below the epi top", f["d"])]
    legend_column(c, items, rows)
    save(fig, "ch24_xsec_bh")


# ====================================================================== VCSEL
def vcsel_shapes(half=22.0):
    V = D.VC; L = D.vcsel_layers(); y = 0.0; S = []; info = {}
    for name, t, na, no in L:
        y0, y1 = y - t, y
        above_cav = "cav" not in info or name == "cav"
        if name == "cav":
            info["cav"] = (y0, y1)
        r = V["r_mesa"] if ("cav" not in info or name == "cav") else half
        if name == "alas":
            S.append(D.rect("alas", -V["r_ap"], V["r_ap"], y0, y1, None))
            for sg in (-1, 1):
                x0, x1 = sorted((sg * V["r_ap"], sg * V["r_mesa"])); S.append(D.rect("alox", x0, x1, y0, y1, None))
            info["ox"] = (y0, y1)
        else:
            S.append(D.rect(name, -r, r, y0, y1, None))
        y = y0
    info["bottom"] = y
    S.insert(0, D.rect("gaas", -half, half, -60, y, None))
    for sg in (-1, 1):
        x0, x1 = sorted((sg * 4.0, sg * 8.0)); S.append(D.rect("metal", x0, x1, 0.0, 0.3, None))
        n0, n1 = sorted((sg * 12.0, sg * 15.0)); S.append(D.rect("metal", n0, n1, info["cav"][0], info["cav"][0] + 0.3, None))
    return S, info


def vcsel_map(v, info, pen=0.4):
    r = np.array(v["r"]); Ir = np.array(v["I"])
    x = np.linspace(-9, 9, 361); yc0, yc1 = info["cav"]
    y = np.linspace(yc0 - 2.0, yc1 + 2.0, 401)
    X, Y = np.meshgrid(x, y)
    lat = np.interp(np.abs(X), r, Ir, right=0.0)
    d = np.where(Y > yc1, Y - yc1, np.where(Y < yc0, yc0 - Y, 0.0))
    return dict(x=x, y=y, I=(lat * np.exp(-d / pen)).tolist())


def fig_vcsel():
    v = M["vcsel"]; S, info = vcsel_shapes(); mp = vcsel_map(v, info)
    yc0, yc1 = info["cav"]; yo0, yo1 = info["ox"]
    print(f"vcsel: p-DBR {-yc1:.2f} um, cavity {yc1-yc0:.3f} um, n-DBR {yc0-info['bottom']:.2f} um; resonance {v['lam_ap']*1e3:.1f} nm "
          f"(aperture), {v['lam_ox']*1e3:.1f} nm (oxide); dn/n {v['dn_rel']*100:.2f} %; V {v['V']:.1f}; LP01 1/e2 {v['d_e2']:.1f} um; far field {v['ff']:.0f} deg")
    fig = plt.figure(figsize=(6.3, 3.55))
    a = fig.add_axes([0.075, 0.50, 0.60, 0.44]); b = fig.add_axes([0.075, 0.07, 0.60, 0.33]); c = fig.add_axes([0.715, 0.03, 0.285, 0.94])
    draw_shapes(a, S, lw=0.12); draw_mode(a, mp, star=False)
    axes_um(a, (-17, 17), (-8.6, 1.6), "(a) the VCSEL cut through its axis, to scale (x : y = 1 : 1), µm")
    current(a, [[(sg * 5.5, -0.02), (sg * 2.2, yo1), (sg * 2.2, yc0), (sg * 6.0, yc0 - 0.55), (sg * 13.5, yc0 - 0.55), (sg * 13.5, yc0 - 0.02)] for sg in (-1, 1)])
    a.annotate("", xy=(0, 1.45), xytext=(0, 0.1), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2, mutation_scale=8), zorder=12)
    tag(a, 0.5, 1.22, "850 nm out", col=RED, bg=False)
    tag(a, -16.6, -7.9, "GaAs substrate"); tag(a, -16.6, -4.6, "n-DBR, 34 pairs"); tag(a, -9.7, -1.9, "p-DBR, 20 pairs")
    tag(a, 16.6, -1.75, "n contact", ha="right", bg=False)
    zoom_box(a, -11, 11, -4.2, 0.75)
    draw_shapes(b, S, lw=0.15); xp, yp = draw_mode(b, mp)
    axes_um(b, (-11, 11), (-4.2, 0.75), "(b) the aperture region: x = 0 on the axis, y = 0 at the top of the mirror, µm")
    current(b, [[(sg * 5.5, -0.02), (sg * 2.2, yo1), (sg * 2.2, yc0), (sg * 5.0, yc0 - 0.45), (sg * 10.6, yc0 - 0.45)] for sg in (-1, 1)])
    hdim(b, 0.42, -10, 10, "")
    b.text(0, 0.42, "20 µm mesa", ha="center", va="center", fontsize=6.2, color=INK, zorder=10,
           bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
    for sg in (-1, 1): b.plot([sg * 3.0, sg * 3.0], [yo1, -1.45], color=INK, lw=0.5, ls=(0, (1, 1.5)), zorder=9)
    hdim(b, -1.45, -3.0, 3.0, "6 µm aperture")
    vdim(b, 10.45, 0.0, yc1, f"{-yc1:.2f}", side="left")
    tag(b, -10.8, (yc0 + yc1) / 2 + 0.05, "cavity", fs=5.8)
    b.annotate("AlOx, 30 nm", xy=(6.5, (yo0 + yo1) / 2), xytext=(6.0, -1.25), fontsize=6.0, color=INK, zorder=12,
               arrowprops=dict(arrowstyle="-", color=INK, lw=0.5), bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8))
    items = [("patch", COL["metal"], "ring contacts: p on top, n on the n-DBR"), ("patch", COL["dbrh"], "Al$_{0.12}$GaAs, λ/4 = 60 nm"),
             ("patch", COL["dbrl"], "Al$_{0.9}$GaAs, λ/4 = 70 nm"), ("patch", COL["alox"], "AlOx: the 30 nm AlAs, oxidised"),
             ("patch", COL["alas"], "AlAs left in the aperture"), ("patch", COL["cav"], "Al$_{0.3}$GaAs cavity, one λ, 3 wells"),
             ("patch", COL["gaas"], "GaAs substrate"), ("fill", RED, "fundamental mode (LP$_{01}$)"),
             ("star", None, "its peak, in the cavity"), ("arrow", BLUE, "current, through the aperture")]
    rows = [("resonance in the aperture", f"{v['lam_ap']*1e3:.1f} nm"), ("resonance under the oxide", f"{v['lam_ox']*1e3:.1f} nm"),
            ("index step, Δn/n = Δλ/λ", f"{v['dn_rel']*100:.2f} %"), ("V of the aperture guide", f"{v['V']:.1f}: multimode"),
            ("LP$_{01}$ diameter, 1/e²", f"{v['d_e2']:.1f} µm"), ("far field, FWHM", f"{v['ff']:.0f}°")]
    legend_column(c, items, rows, dy=0.052)
    save(fig, "ch24_xsec_vcsel")


# ====================================================================== III-V on silicon
def femwell_map(w):
    g = HY["map"]; x = np.linspace(g["x"][0], g["x"][1], g["nx"]); y = np.linspace(g["y"][0], g["y"][1], g["ny"])
    mo = [r for r in HY["widths"] if abs(r["w"] - w) < 1e-9][0]["modes"][0]
    I = np.array(mo["map"], float).reshape(g["ny"], g["nx"])
    return dict(x=x, y=y, I=I.tolist()), mo


def fig_hetero():
    fig = plt.figure(figsize=(6.3, 3.85))
    a = fig.add_axes([0.075, 0.555, 0.60, 0.40])
    b = fig.add_axes([0.075, 0.07, 0.29, 0.40]); b2 = fig.add_axes([0.385, 0.07, 0.29, 0.40])
    c = fig.add_axes([0.715, 0.03, 0.285, 0.94])
    S = D.hetero(0.5); S2 = D.hetero(1.0, gain=False)
    mp, mo = femwell_map(0.5); mp2, mo2 = femwell_map(1.0)
    print(f"hetero: Si 0.50 um: n_eff {mo['neff']:.3f}, MQW {mo['G_mqw']*100:.0f} %, Si {mo['G_si']*100:.0f} %; "
          f"Si 1.00 um: n_eff {mo2['neff']:.3f}, MQW {mo2['G_mqw']*100:.0f} %, Si {mo2['G_si']*100:.0f} %")
    draw_shapes(a, S); draw_mode(a, mp, star=False)
    axes_um(a, (-7.2, 7.2), (-2.6, 3.4), "(a) the gain section, to scale (x : y = 1 : 1), µm; y = 0 at the silicon's base")
    y0 = 0.53
    current(a, [[(sg * 0.4, y0 + 2.0), (sg * 0.4, y0 + 0.2), (sg * 0.4, y0 + 0.055), (sg * 3.5, y0 + 0.055)] for sg in (-1, 1)])
    tag(a, -7.0, -2.3, "Si substrate"); tag(a, -7.0, -1.0, "buried oxide, 2 µm"); tag(a, 0, 3.15, "p-metal", ha="center", bg=False)
    tag(a, -4.6, 1.45, "n-metal", ha="center", bg=False); tag(a, 4.6, 1.45, "n-metal", ha="center", bg=False)
    tag(a, 2.1, 2.2, "implanted\nedges", bg=False, fs=5.8)
    a.annotate("", xy=(1.15, 2.1), xytext=(2.05, 2.2), arrowprops=dict(arrowstyle="-", color=INK, lw=0.5), zorder=12)
    zoom_box(a, -2.6, 2.6, -0.7, 2.75, "(b)")
    for ax, SS, m_, mo_, ttl in ((b, S, mp, mo, "(b) silicon 0.50 µm wide: gain section"), (b2, S2, mp2, mo2, "(c) silicon 1.00 µm wide: taper end")):
        draw_shapes(ax, SS); draw_mode(ax, m_)
        axes_um(ax, (-2.6, 2.6), (-0.7, 2.75), ttl, yl="y (µm)" if ax is b else "")
        ax.title.set_fontsize(6.6)
        tag(ax, -2.5, 0.25, f"Si {mo_['G_si']*100:.0f} %", fs=5.9); tag(ax, -2.5, 0.79, f"MQW {mo_['G_mqw']*100:.0f} %", fs=5.9)
    hdim(b, -0.45, -0.25, 0.25, "0.5"); hdim(b2, -0.45, -0.5, 0.5, "1.0")
    vdim(b, 1.85, 0.53 + 0.11, 0.53 + 0.41, "0.30", side="right")
    items = [("patch", COL["metal"], "p and n metal: both on top"), ("patch", COL["cap"], "p⁺⁺ InGaAs contact layer, 0.1 µm"),
             ("patch", COL["pinp"], "p-InP, 1.5 µm; 3 µm mesa"), ("patch", COL["implant"], "implanted, semi-insulating edges"),
             ("patch", COL["mqw"], "MQW region, 0.3 µm"), ("patch", COL["nlayer"], "n-InP contact layer, 0.11 µm"),
             ("patch", COL["sin"], "SiN passivation, 0.15 µm"), ("patch", COL["bond"], "bonding oxide, 30 nm"),
             ("patch", COL["si"], "silicon strip, 0.5 µm thick"), ("patch", COL["ox"], "oxide (BOX and cladding)"),
             ("fill", RED, "mode (femwell): 1/e² and half"), ("star", None, "the mode's peak"), ("arrow", BLUE, "current: down, then sideways")]
    rows = [("Si 0.50 µm: n_eff", f"{mo['neff']:.3f}"), ("   in MQW, in Si", f"{mo['G_mqw']*100:.0f} %, {mo['G_si']*100:.0f} %"),
            ("Si 1.00 µm: n_eff", f"{mo2['neff']:.3f}"), ("   in MQW, in Si", f"{mo2['G_mqw']*100:.0f} %, {mo2['G_si']*100:.0f} %")]
    legend_column(c, items, rows, title="Computed with femwell (Table 27.1)", dy=0.047)
    save(fig, "ch24_xsec_hetero")


# ====================================================================== SOAs: a ridge SOA and a slab-coupled, large-mode SOA
def fig_soa():
    m1, m2 = M["soa_ridge"], M["soa_scow"]
    r = m2["A_over_gamma"] / m1["A_over_gamma"]
    print(f"soa ridge: Gamma {m1['gamma']*100:.2f} %, A/Gamma {m1['A_over_gamma']:.2f} um2, 1/e2 {m1['w']:.2f} x {m1['h']:.2f}, ff {m1['ffx']:.0f} x {m1['ffy']:.0f}; "
          f"slab-coupled: Gamma {m2['gamma']*100:.2f} %, A/Gamma {m2['A_over_gamma']:.2f} um2, 1/e2 {m2['w']:.2f} x {m2['h']:.2f}, ff {m2['ffx']:.0f} x {m2['ffy']:.0f}; "
          f"P_sat ratio {r:.1f} (12 mW -> {12*r:.0f} mW, {10*np.log10(12*r):.1f} dBm)")
    fig = plt.figure(figsize=(6.3, 3.15))
    a = fig.add_axes([0.065, 0.11, 0.305, 0.80]); b = fig.add_axes([0.39, 0.11, 0.305, 0.80])
    c = fig.add_axes([0.725, 0.03, 0.275, 0.94])
    S1 = D.ridge(RW=2.5, metal=(-2.25, 2.25)); S2 = D.scow()
    for ax, S, m, ttl in ((a, S1, m1, "(a) ridge SOA: the laser's stack"), (b, S2, m2, "(b) slab-coupled SOA")):
        draw_shapes(ax, S); draw_mode(ax, m["map"])
        axes_um(ax, (-5, 5), (-6.4, 1.1), ttl, yl="y (µm)" if ax is a else "")
    current(a, [[(xx, -0.03), (xx, -1.60), (xx * 1.35, -1.98)] for xx in (-0.9, -0.3, 0.3, 0.9)])
    current(b, [[(xx, -0.03), (xx, -1.36)] for xx in (-1.8, -0.6, 0.6, 1.8)])
    hdim(a, 0.42, -1.25, 1.25, "2.5"); hdim(b, 0.42, -2.5, 2.5, "5.0")
    yq0 = -1.35 - D.SCOW_STACK
    vdim(b, 3.3, yq0 - D.SCOW["ts"], yq0, f"{D.SCOW['ts']:.1f} slab", side="right")
    b.plot([2.0, 3.3], [yq0, yq0], color=INK, lw=0.5, ls=(0, (1, 1.5)), zorder=9)          # extension line to the slab top
    tag(a, -4.9, -4.5, "n-InP"); tag(b, -4.9, -5.6, "n-InP"); tag(b, -4.9, -3.3, "InGaAsP slab"); tag(a, -4.9, -0.8, "BCB"); tag(b, -4.9, -0.8, "BCB")
    tag(a, 0, -6.0, f"Γ = {m1['gamma']*100:.1f} %, A/Γ = {m1['A_over_gamma']:.1f} µm²", ha="center")
    tag(b, 0, -6.0, f"Γ = {m2['gamma']*100:.2f} %, A/Γ = {m2['A_over_gamma']:.1f} µm²", ha="center")
    items = [("patch", COL["metal"], "p-metal"), ("patch", COL["cap"], "p⁺⁺ InGaAs contact layer"), ("patch", COL["pinp"], "p-InP cladding"),
             ("patch", COL["sin"], "SiN"), ("patch", COL["bcb"], "BCB"), ("patch", COL["sch"], "InGaAsP barriers and SCH"),
             ("line", COL["qw"], "wells: 5 × 10 nm (a), 3 × 8 nm (b)"), ("patch", COL["slab"], "n-InGaAsP slab, 1.0 µm gap"),
             ("patch", COL["ninp"], "n-InP"), ("fill", RED, "mode: 1/e² (dashed) and half"), ("star", None, "the mode's peak"),
             ("arrow", BLUE, "hole current")]
    rows = [("in the wells, Γ", f"{m1['gamma']*100:.1f} %  |  {m2['gamma']*100:.2f} %"), ("mode, 1/e² (µm)", f"{m1['w']:.1f}×{m1['h']:.1f}  |  {m2['w']:.1f}×{m2['h']:.1f}"),
            ("A/Γ (µm²)", f"{m1['A_over_gamma']:.1f}  |  {m2['A_over_gamma']:.1f}"), ("P_sat, same a and τ", f"1  |  {r:.0f}×"),
            ("far field, FWHM", f"{m1['ffx']:.0f}°×{m1['ffy']:.0f}°  |  {m2['ffx']:.0f}°×{m2['ffy']:.0f}°")]
    legend_column(c, items, rows, title="Computed: (a)  |  (b)", dy=0.054, table_dy=0.06, fs=5.9)
    save(fig, "ch24_xsec_soa")


if __name__ == "__main__":
    ALL = {"ridge": fig_ridge, "bh": fig_bh, "vcsel": fig_vcsel, "hetero": fig_hetero, "soa": fig_soa}
    for name in (sys.argv[1:] or list(ALL)):
        ALL[name]()
