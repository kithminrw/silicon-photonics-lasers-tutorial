"""Figures for Chapter 24 (the Fabry-Perot laser and the rate equations), Sections 24.1-24.7.

Run from the repository root:  python -I -X utf8 figsrc/ch24_figs.py
Writes assets/figs/ch24_ridge.svg, ch24_threshold.svg, ch24_clamp.svg, ch24_turnon.svg, ch24_modes.svg and ch24_process.svg
(Section 24.9), and prints
every number the figures and captions use. (The VCSEL figures of Section 24.8 come from figsrc/ch2x_lasers.py.)

The laser is the 400 um InGaAsP Fabry-Perot laser of Worked Example 24.1 with the parameters of the laser and dyn demos
(FP in ch2x_lasers.py). The ridge cross-section uses the illustrative layer stack of figsrc/ch23_figs.py (Figure 23.3b)
and an effective-index estimate of the mode.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *
from ch2x_lasers import FP, fp_op
from ch23_figs import slab_te, stack_sch, TS, N_INP, N_Q125, N_WELL

QE, CL = 1.602e-19, 3e10                          # C, cm/s
P_ = FP; VG = CL / P_["ng"]; V = P_["L"] * P_["w"] * P_["d"]
AM = np.log(1 / P_["R"] ** 2) / (2 * P_["L"]); TP = 1 / (VG * (P_["ai"] + AM))
GTH = (P_["ai"] + AM) / P_["Gam"]; NTH = P_["Ntr"] * np.exp(GTH / P_["g0"])
HV = 1.2398 / P_["lam"] * QE                      # J
BETA = 1e-4


def rrec(N):
    return P_["A"] * N + P_["B"] * N ** 2 + P_["C"] * N ** 3


ITH = QE * V / P_["eta"] * rrec(NTH)


def p_facet(S):
    """Output power from one facet (W) at photon density S (cm^-3)."""
    return 0.5 * S * V / P_["Gam"] * VG * AM * HV


# ================================================================== Figure 24.1: the ridge laser
HRES, HP = 0.35, 1.80                             # p-InP left beside the ridge, and on the ridge (um)


def ridge_mode():
    L, act = stack_sch(TS)
    nc, fy = slab_te(L + [(HP, N_INP)], N_INP, ncl_top=1.0)             # under the ridge (top: contact, air)
    no, _ = slab_te(L + [(HRES, N_INP)], N_INP, ncl_top=1.54)          # beside it (top: BCB)
    nx, fx = slab_te([(2.0, nc)], no)                                   # lateral slab, 2 um wide
    y = np.linspace(-3, 4, 140001); Iy = fy(y) ** 2             # 0.05 nm steps: the wells are 10 nm thick
    x = np.linspace(-8, 10, 36001); Ix = fx(x) ** 2
    ina = np.zeros_like(y, bool)
    for a, b in act: ina |= (y >= a) & (y < b)
    Gy = Iy[ina].sum() / Iy.sum(); Gx = Ix[(x >= 0) & (x < 2)].sum() / Ix.sum()
    return dict(nc=nc, no=no, nx=nx, fx=fx, fy=fy, Gy=Gy, Gx=Gx, G=Gy * Gx, tot=sum(t for t, _ in L), L=L, act=act)


def fig_ridge():
    m = ridge_mode()
    print(f"ridge: n_eff under ridge {m['nc']:.4f}, beside {m['no']:.4f} (dn {m['nc']-m['no']:.4f}); lateral-mode n_eff {m['nx']:.4f};"
          f" Gamma_y {m['Gy']:.3f} x Gamma_x {m['Gx']:.3f} = {m['G']:.3f} (chapter: 0.06)")
    fig = plt.figure(figsize=(6.3, 2.75))
    # ---------------- (a) perspective sketch, not to scale
    ax = fig.add_axes([0.0, 0.0, 0.53, 1.0]); frameless(ax, (-0.6, 10.6), (-1.4, 6.6))
    c30, s30 = 0.62 * np.cos(np.radians(28)), 0.62 * np.sin(np.radians(28))

    def P(x, y, z):                              # oblique projection: x along the cavity, y across, z up
        return (x + y * c30, z + y * s30)

    def face(pts, fc, ec=INK, lw=0.5, z=2, alpha=1.0):
        poly(ax, [P(*p) for p in pts], fc, ec=ec, lw=lw, z=z, alpha=alpha)
    Lx, Wy, Hz = 7.2, 5.0, 1.6                    # chip length, width, substrate height (drawing units)
    za, ha = 1.6, 0.18                            # active layer height and thickness
    zc = za + ha + 0.25                           # top of the residual cladding
    rw, rh = 0.55, 0.75                           # ridge width and height (exaggerated)
    y0 = Wy / 2 - rw / 2
    # bottom contact
    face([(0, 0, -0.18), (Lx, 0, -0.18), (Lx, 0, 0), (0, 0, 0)], MAT["metal"], z=1)
    face([(Lx, 0, -0.18), (Lx, Wy, -0.18), (Lx, Wy, 0), (Lx, 0, 0)], MAT["metal"], z=1)
    # substrate + active + cladding: front face (y = 0 plane is the side; the output facet is x = Lx)
    face([(0, 0, 0), (Lx, 0, 0), (Lx, 0, zc), (0, 0, zc)], "#DCD6C8", z=2)                  # side wall
    face([(Lx, 0, 0), (Lx, Wy, 0), (Lx, Wy, zc), (Lx, 0, zc)], MAT["inp"], z=3)            # output facet
    face([(Lx, 0, za), (Lx, Wy, za), (Lx, Wy, za + ha), (Lx, 0, za + ha)], MAT["q"], ec="none", z=4)
    face([(0, 0, za), (Lx, 0, za), (Lx, 0, za + ha), (0, 0, za + ha)], MAT["q"], ec="none", z=3)
    face([(0, 0, zc), (Lx, 0, zc), (Lx, Wy, zc), (0, Wy, zc)], "#E6E1D5", z=2)              # top surface
    # ridge with its contact
    face([(0, y0, zc), (Lx, y0, zc), (Lx, y0, zc + rh), (0, y0, zc + rh)], "#D4CDBC", z=5)
    face([(Lx, y0, zc), (Lx, y0 + rw, zc), (Lx, y0 + rw, zc + rh), (Lx, y0, zc + rh)], MAT["inp"], z=6)
    face([(0, y0, zc + rh), (Lx, y0, zc + rh), (Lx, y0 + rw, zc + rh), (0, y0 + rw, zc + rh)], MAT["metal"], z=6)
    # lasing spot on the facet under the ridge and the output beams
    cx, cy = P(Lx, Wy / 2, za + ha / 2)
    ax.add_patch(Ellipse((cx, cy), 0.55, 0.22, fc=RED, ec="none", alpha=0.85, zorder=7))
    for spread, al in ((0.9, 0.18), (0.45, 0.35)):
        poly(ax, [(cx, cy), (cx + 2.3, cy + spread), (cx + 2.3, cy - spread)], RED, alpha=al, z=6)
    arrow(ax, (cx + 0.3, cy), (cx + 2.6, cy), col=RED, lw=1.3, ms=9)
    # current
    tx, ty = P(Lx * 0.45, Wy / 2, zc + rh)
    arrow(ax, (tx, ty + 1.2), (tx, ty + 0.05), col=BLUE, lw=1.2, ms=8)
    label(ax, tx + 0.15, ty + 1.05, "current $I$", ha="left", col=BLUE, fs=FS_SMALL)
    # labels
    callout(ax, P(Lx * 0.3, Wy / 2 + rw / 2, zc + rh), (0.6, 5.7), "p contact on the ridge", ha="left")
    callout(ax, P(0.25, 0, za + ha / 2), (-0.45, 4.3), "active region (MQW)", ha="left")
    callout(ax, P(Lx, Wy * 0.78, 0.7), (8.7, 0.45), "cleaved facet,\n$R$ ≈ 0.32", ha="left")
    label(ax, *P(Lx * 0.42, 0, 0.75), "n-InP substrate", fs=FS_SMALL, rot=0)
    callout(ax, P(0.6, 0, -0.09), (-0.45, -1.05), "n contact", ha="left")
    label(ax, cx + 2.15, cy + 1.15, "light out", col=RED, fs=FS_SMALL)
    # length dimension along the near bottom edge
    p0, p1 = P(0, 0, -0.55), P(Lx, 0, -0.55)
    dim(ax, p0, p1, "$L$ = 400 µm")
    note(ax, "not to scale", loc="lower right")
    panel(ax, "a", 0.0, 1.0)
    # ---------------- (b) cross-section to scale with the mode
    bx_ = fig.add_axes([0.56, 0.04, 0.44, 0.92]); frameless(bx_, (-4.2, 4.2), (-1.3, 3.0))
    tot = m["tot"]; ytop_res = tot + HRES; ytop = tot + HP
    box(bx_, -4.2, -1.3, 8.4, 1.3, "inp")                                        # n-InP substrate
    box(bx_, -4.2, 0, 8.4, tot, "q")                                             # SCH + wells
    wa, wb = m["act"][0][0], m["act"][-1][1]                                     # the 5 wells (90 nm) drawn as one band
    box(bx_, -4.2, wa, 8.4, wb - wa, "mqw", alpha=0.75)
    box(bx_, -4.2, tot, 8.4, HRES, "inp")                                        # residual p-InP
    box(bx_, -1.0, ytop_res, 2.0, HP - HRES, "inp")                              # ridge
    box(bx_, -1.0, ytop, 2.0, 0.15, "#6E6250")                                   # p+ InGaAs cap
    box(bx_, -1.6, ytop + 0.15, 3.2, 0.30, "metal")                              # contact
    for s in (-1, 1):                                                            # BCB beside the ridge
        x0 = 1.0 if s > 0 else -4.2
        box(bx_, x0, ytop_res, 3.2, ytop + 0.15 - ytop_res, "bcb")
    box(bx_, -4.2, ytop_res - 0.0, 8.4, 0.04, "ox")                              # thin passivation
    # mode intensity (effective-index estimate)
    xx = np.linspace(-4.2, 4.2, 421); yy = np.linspace(-1.3, 3.0, 431)
    I = (m["fx"](xx + 1.0) ** 2)[None, :] * (m["fy"](yy) ** 2)[:, None]; I /= I.max()
    cs = bx_.contour(xx, yy, I, levels=[0.1, 0.3, 0.5, 0.7, 0.9], colors=[BLUE], linewidths=0.7, zorder=8)
    # labels
    label(bx_, -1.6, -0.75, "n-InP", fs=FS_SMALL)
    label(bx_, 0.0, 1.35, "p-InP\nridge", fs=FS_SMALL, z=9)
    label(bx_, -2.9, ytop_res + 0.6, "BCB", fs=FS_SMALL)
    label(bx_, 2.4, ytop + 0.32, "p contact", fs=FS_SMALL, ha="left")
    callout(bx_, (2.6, tot / 2), (2.2, -0.75), "SCH + 5 wells", ha="left")
    callout(bx_, (0.55, 0.45), (2.0, 0.95), f"mode, Γ = {m['G']:.2f}", col=BLUE, ha="left")
    dim(bx_, (-1.0, ytop + 0.7), (1.0, ytop + 0.7), "2 µm")
    scalebar(bx_, -3.9, -1.1, 1.0, "1 µm")
    note(bx_, "to scale", loc="lower right")
    panel(bx_, "b", 0.0, 1.0)
    save(fig, "ch24_ridge")
    return m


# ================================================================== Figure 24.2: threshold
def fig_threshold():
    L = P_["L"]; R = P_["R"]
    net_th = AM                                       # Gamma g - alpha_i at threshold, per cm
    per_pass = np.exp(net_th * L)
    print(f"alpha_m = {AM:.2f} /cm, g_th = {GTH:.0f} /cm, N_th = {NTH:.3e}; one pass x{per_pass:.3f} ({10*np.log10(per_pass):.2f} dB),"
          f" mirror x{R} ({10*np.log10(R):.2f} dB); tau_p {TP*1e12:.2f} ps")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.25, 1]))
    for frac, col, ls, lab in ((1.0, C1, "-", "at threshold: $\\Gamma g = \\alpha_i + \\alpha_m$"),
                               (0.9, MUTED, "--", "modal gain 10 % lower")):
        net = frac * GTH * P_["Gam"] - P_["ai"]
        zs, ps = [], []; p = 1.0; zc = 0.0
        for k in range(4):                            # four passes = two round trips
            z = np.linspace(0, L, 60)
            zs.append(zc + z * 1e4); ps.append(10 * np.log10(p * np.exp(net * z)))
            p *= np.exp(net * L); zc += L * 1e4
            zs.append([zc, zc]); ps.append([10 * np.log10(p), 10 * np.log10(p * R)]); p *= R
        a.plot(np.concatenate(zs), np.concatenate(ps), color=col, ls=ls, lw=1.6 if frac == 1 else 1.1, label=lab)
        if frac == 0.9: print(f"10 % less modal gain: power after two round trips {10*np.log10(p):.1f} dB")
    for k in range(5):
        a.axvline(400 * k, color=GRID, lw=0.8, zorder=0)
    for k, txt in ((1, "front facet $R_1$"), (2, "rear facet $R_2$"), (3, "front"), (4, "rear")):
        a.text(400 * k + (8 if k < 4 else -8), 5.6, txt, ha="left" if k < 4 else "right", va="top", fontsize=6.3, color=MUTED)
    a.text(150, 3.4, f"gain ×{per_pass:.2f}\nper pass", ha="center", va="bottom", fontsize=6.4, color=INK)
    a.text(415, 2.6, f"facet ×{R:.2f}", ha="left", va="center", fontsize=6.4, color=INK)
    a.set_xlim(0, 1600); a.set_ylim(-7, 6); a.set_xticks([0, 400, 800, 1200, 1600])
    finish(a, "Distance travelled, unfolded (µm)", "Power (dB, rel. start)", legend=True, loc="lower left")
    a.legend(loc="lower left", fontsize=6.4)
    tag(a, "a")
    # (b) modal gain against N and the loss lines for three cavity lengths
    N = np.linspace(1.5e18, 5e18, 300)
    b.plot(N / 1e18, P_["Gam"] * P_["g0"] * np.log(N / P_["Ntr"]), color=C2, lw=1.8, label="modal gain $\\Gamma g(N)$")
    for Lu, col in ((200, C4), (400, C1), (1000, C3)):
        am = np.log(1 / R ** 2) / (2 * Lu * 1e-4); loss = P_["ai"] + am; Nt = P_["Ntr"] * np.exp(loss / P_["Gam"] / P_["g0"])
        b.axhline(loss, color=col, lw=1.0, ls="--")
        b.plot(Nt / 1e18, loss, "o", color=col, ms=4, zorder=5)
        b.text(1.55 if Lu < 1000 else 2.85, loss + 1.5 if Lu < 1000 else loss - 1.5, f"{Lu} µm: $\\alpha_i + \\alpha_m$ = {loss:.1f} cm$^{{-1}}$", fontsize=6.3, color=col, va="bottom" if Lu < 1000 else "top")
        print(f"L = {Lu} um: alpha_m {am:.1f}, total {loss:.1f} /cm, N_th {Nt:.3e}, I_th {QE*Lu*1e-4*P_['w']*P_['d']/P_['eta']*rrec(Nt)*1e3:.1f} mA,"
              f" eta_d {P_['eta']*am/(P_['ai']+am):.2f}")
    b.axhline(P_["ai"], color=MUTED, lw=0.7, ls=":")
    b.text(4.95, P_["ai"] - 1.5, "internal loss $\\alpha_i$", fontsize=6.3, color=MUTED, ha="right", va="top")
    b.set_xlim(1.5, 5.0); b.set_ylim(0, 100)
    finish(b, "Carrier density N (10$^{18}$ cm$^{-3}$)", "Modal gain or loss (cm$^{-1}$)")
    b.text(4.95, 96, "$\\Gamma g(N)$", fontsize=7, color=C2, ha="right", va="top")
    tag(b, "b")
    fig.tight_layout(w_pad=1.8)
    save(fig, "ch24_threshold")


# ================================================================== Figure 24.3: clamping
def steady_curve():
    """Steady state of the rate equations (with gain compression and spontaneous emission), parametric in S."""
    g0, Ntr, G, eps = P_["g0"], P_["Ntr"], P_["Gam"], P_["eps"]
    Ss = np.geomspace(1e5, 2.5e15, 800); Ns, Is = [], []
    for S in Ss:
        # photon balance G vg g(N, S) - 1/tp + G beta B N^2 / S = 0 is monotonic in N: bisect
        lo, hi = 1e14, 2 * NTH
        for _ in range(100):
            N = np.sqrt(lo * hi)
            f = G * VG * g0 * np.log(N / Ntr) / (1 + eps * S) - 1 / TP + G * BETA * P_["B"] * N ** 2 / S
            if f > 0: hi = N
            else: lo = N
        gs = g0 * np.log(N / Ntr) / (1 + eps * S)
        Ns.append(N); Is.append(QE * V / P_["eta"] * (rrec(N) + VG * gs * S))
    return np.array(Is), np.array(Ns), Ss


def fig_clamp():
    I, N, S = steady_curve(); Pf = p_facet(S)
    i50 = np.argmin(abs(I - 50e-3)); i20 = np.argmin(abs(I - 20e-3)); i5 = np.argmin(abs(I - 5e-3))
    sl = (Pf[np.argmin(abs(I - 60e-3))] - Pf[np.argmin(abs(I - 30e-3))]) / (I[np.argmin(abs(I - 60e-3))] - I[np.argmin(abs(I - 30e-3))])
    print(f"I_th = {ITH*1e3:.2f} mA; at 50 mA: P/facet {Pf[i50]*1e3:.2f} mW, N {N[i50]:.4e} (N_th {NTH:.4e}, +{100*(N[i50]/NTH-1):.2f} %);"
          f" slope 30-60 mA {sl:.3f} W/A; at 5 mA P/facet {Pf[i5]*1e9:.1f} nW, N/N_th {N[i5]/NTH:.2f}; at 20 mA {Pf[i20]*1e3:.3f} mW")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    sel = I <= 61e-3
    # below threshold: no photons in the mode, so N follows from I = qV R(N)/eta alone (extend the curve to I = 0)
    Nlow = np.linspace(1e16, N[0], 200); Ilow = QE * V / P_["eta"] * rrec(Nlow)
    a.plot(np.r_[Ilow, I[sel]] * 1e3, np.r_[Nlow, N[sel]] / 1e18, color=C1)
    a.axhline(NTH / 1e18, color=MUTED, lw=0.7, ls="--"); a.axvline(ITH * 1e3, color=MUTED, lw=0.6, ls=":")
    a.text(1.5, NTH / 1e18 + 0.08, f"clamped at $N_\\mathrm{{th}}$ = {NTH/1e18:.2f} × 10$^{{18}}$ cm$^{{-3}}$", fontsize=6.6, color=INK, va="bottom")
    a.text(ITH * 1e3 + 1, 0.4, f"$I_\\mathrm{{th}}$ = {ITH*1e3:.0f} mA", fontsize=6.6, color=MUTED)
    a.text(8, 0.75, "below threshold, nearly\nall of $I$ recombines:\n$I \\approx qV R(N)/\\eta_i$", fontsize=6.5, color=INK)
    a.text(40, 2.6, "above: each extra\nelectron makes a photon", fontsize=6.5, color=INK, ha="center")
    a.set_xlim(0, 60); a.set_ylim(0, 4.0)
    finish(a, "Current (mA)", "Carrier density N (10$^{18}$ cm$^{-3}$)")
    tag(a, "a")
    b.semilogy(I[sel] * 1e3, Pf[sel] * 1e3, color=C2)
    b.axvline(ITH * 1e3, color=MUTED, lw=0.6, ls=":")
    b.plot(I[i50] * 1e3, Pf[i50] * 1e3, "o", color=C2, ms=4)
    b.annotate(f"50 mA: slope\n{sl:.2f} W/A per facet", xy=(I[i50] * 1e3, Pf[i50] * 1e3), xytext=(30, 0.06), fontsize=6.6, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.text(3, 2e-4, "spontaneous emission\ninto the lasing mode", fontsize=6.5, color=INK)
    b.text(ITH * 1e3 + 1.5, 4e-3, "stimulated\nemission", fontsize=6.5, color=INK, ha="left")
    b.set_xlim(0, 60); b.set_ylim(1e-5, 30)
    finish(b, "Current (mA)", "Output per facet (mW, log scale)")
    tag(b, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "ch24_clamp")


# ================================================================== Figure 24.4: turn-on delay and relaxation oscillations
def simulate_step(Is, t_end=3e-9, dt=0.1e-12):
    Is = np.asarray(Is, float); g0, Ntr, G, eps = P_["g0"], P_["Ntr"], P_["Gam"], P_["eps"]
    N = np.zeros_like(Is); S = np.full_like(Is, 1.0)

    def der(N, S):
        g = g0 * np.log(np.maximum(N, 1e12) / Ntr) / (1 + eps * S)
        return (P_["eta"] * Is / (QE * V) - rrec(N) - VG * g * S, G * VG * g * S - S / TP + G * BETA * P_["B"] * N ** 2)
    n = int(round(t_end / dt)); ts, Ns, Ss = [], [], []
    for k in range(n + 1):
        if k % 10 == 0: ts.append(k * dt); Ns.append(N.copy()); Ss.append(S.copy())
        k1 = der(N, S); k2 = der(N + dt / 2 * k1[0], S + dt / 2 * k1[1]); k3 = der(N + dt / 2 * k2[0], S + dt / 2 * k2[1]); k4 = der(N + dt * k3[0], S + dt * k3[1])
        N = N + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); S = np.maximum(S + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]), 1e-3)
    return np.array(ts), np.array(Ns).T, np.array(Ss).T


def fig_turnon():
    TAUN = NTH / rrec(NTH)
    cur = [30e-3, 40e-3, 50e-3]; cols = [C3, C1, C2]
    t, N, S = simulate_step(cur)
    fig = plt.figure(figsize=(6.3, 3.3))
    a = fig.add_axes([0.08, 0.60, 0.50, 0.33]); b = fig.add_axes([0.08, 0.13, 0.50, 0.40], sharex=a)
    c = fig.add_axes([0.70, 0.13, 0.29, 0.80])
    for k, (I, col) in enumerate(zip(cur, cols)):
        a.plot(t * 1e9, N[k] / NTH, color=col, lw=1.2)
        b.plot(t * 1e9, p_facet(S[k]) * 1e3, color=col, lw=1.3, label=f"{I*1e3:.0f} mA")
        td = t[np.argmax(N[k] >= NTH)]
        tf = TAUN * np.log(I / (I - ITH))
        pk = np.argmax(p_facet(S[k]))
        # ringing frequency from the spacing of the first two power peaks
        pw = p_facet(S[k]); idx = [j for j in range(1, len(pw) - 1) if pw[j] > pw[j - 1] and pw[j] >= pw[j + 1] and pw[j] > 0.2 * pw.max()]
        fring = 1 / (t[idx[1]] - t[idx[0]]) if len(idx) > 1 else np.nan
        print(f"{I*1e3:.0f} mA: N reaches N_th at {td*1e9:.3f} ns (formula tau_n ln(I/(I-Ith)) = {tf*1e9:.3f} ns, tau_n {TAUN*1e9:.2f} ns);"
              f" first peak {pw[pk]*1e3:.1f} mW at {t[pk]*1e9:.2f} ns; ringing {fring/1e9:.2f} GHz; final {pw[-1]*1e3:.2f} mW, f_r {fp_op(I)['fr']/1e9:.2f} GHz")
    a.axhline(1, color=MUTED, lw=0.6, ls="--"); a.text(2.95, 1.03, "$N_\\mathrm{th}$", fontsize=6.6, color=MUTED, ha="right", va="bottom")
    a.set_ylim(0, 1.25); a.set_ylabel("$N/N_\\mathrm{th}$"); a.tick_params(axis="x", labelbottom=False)
    tag(a, "a")
    k = 1; td = t[np.argmax(N[k] >= NTH)]
    for ax in (a, b):
        ax.axvline(td * 1e9, color=C1, lw=0.6, ls=":")
    b.text(td * 1e9 + 0.04, 33, f"$\\tau_d$ = {td*1e9:.2f} ns at 40 mA", fontsize=6.6, color=C1, ha="left", va="top")
    b.set_xlim(0, 3); b.set_ylim(0, 35)
    finish(b, "Time after the current step (ns)", "Output per facet (mW)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.4, title="step 0 → I", title_fontsize=6.4)
    tag(b, "b")
    # (c) delay against current: simulation against the formula
    Ic = np.linspace(22e-3, 120e-3, 40)
    t2, N2, _ = simulate_step(Ic, t_end=2.5e-9, dt=0.2e-12)
    tds = np.array([t2[np.argmax(N2[k] >= NTH)] for k in range(len(Ic))])
    c.plot(Ic * 1e3, tds * 1e9, "o", color=C1, ms=3, label="rate equations")
    If = np.linspace(20.5e-3, 120e-3, 300)
    c.plot(If * 1e3, TAUN * np.log(If / (If - ITH)) * 1e9, color=INK, lw=1.0, label="$\\tau_n \\ln[I/(I - I_\\mathrm{th})]$")
    c.axvline(ITH * 1e3, color=MUTED, lw=0.6, ls=":")
    c.set_xlim(0, 120); c.set_ylim(0, 2.5)
    finish(c, "Current (mA)", "Turn-on delay $\\tau_d$ (ns)", legend=True, loc="upper right")
    c.legend(loc="upper right", fontsize=6.2)
    c.text(ITH * 1e3 + 2, 0.12, "$I_\\mathrm{th}$", fontsize=6.6, color=MUTED)
    tag(c, "c")
    print(f"delay at 40 mA from the sweep: {np.interp(40e-3, Ic, tds)*1e9:.3f} ns; at 120 mA {tds[-1]*1e12:.0f} ps")
    save(fig, "ch24_turnon")


# ================================================================== Figure 24.5: longitudinal modes under the gain
def fig_modes():
    lam0 = 1550.0; dlam = lam0 ** 2 / (2 * P_["ng"] * P_["L"] * 1e7)       # nm
    Dg = 30.0                                                              # nm: the laser demo's parabolic gain width
    loss = P_["ai"] + AM
    gm = lambda l: loss * (1 - ((l - lam0) / Dg) ** 2)
    nmodes = int(np.floor(Dg / dlam)) * 2 + 1
    print(f"mode spacing {dlam:.3f} nm ({CL/(2*P_['ng']*P_['L'])/1e9:.1f} GHz); modes with positive modal gain: {nmodes};"
          f" neighbour deficit {loss - gm(lam0 + dlam):.4f} /cm ({100*(loss-gm(lam0+dlam))/loss:.3f} % of the loss);"
          f" 5 modes away {loss - gm(lam0 + 5*dlam):.3f} /cm")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.35, 1]))
    l = np.linspace(1505, 1595, 1000)
    gl = gm(l); gl[gl < -10] = np.nan
    a.plot(l, gl, color=C2, lw=1.6, label="modal gain $\\Gamma g(\\lambda)$")
    a.axhline(loss, color=C1, lw=1.0, ls="--", label="loss $\\alpha_i + \\alpha_m$")
    lm = lam0 + dlam * np.arange(-60, 61)
    lm = lm[(lm > 1505) & (lm < 1595)]
    a.vlines(lm, -20, -13, color=INK, lw=0.5)
    a.text(1550, -22, f"cavity modes, one every {dlam:.2f} nm", fontsize=6.4, color=INK, va="top", ha="center")
    a.axvspan(lam0 - 4, lam0 + 4, color=GRID, alpha=0.6, lw=0, zorder=0)
    a.text(lam0, 55, "zoom (b)", fontsize=6.3, color=MUTED, ha="center")
    a.set_xlim(1505, 1595); a.set_ylim(-28, 62)
    finish(a, "Wavelength (nm)", "Gain or loss (cm$^{-1}$)")
    a.legend(loc="upper left", fontsize=6.4)
    tag(a, "a")
    lz = lm[(lm > lam0 - 4.2) & (lm < lam0 + 4.2)]
    dz = gm(lz) - loss
    b.bar(lz, dz, width=0.25, color=C2, edgecolor="none")
    b.plot(np.linspace(lam0 - 4.2, lam0 + 4.2, 200), gm(np.linspace(lam0 - 4.2, lam0 + 4.2, 200)) - loss, color=C2, lw=0.8, ls=":")
    b.axhline(0, color=C1, lw=1.0, ls="--")
    b.annotate("", xy=(lam0 + dlam, 0.06), xytext=(lam0, 0.06), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=5, shrinkA=0, shrinkB=0))
    b.text(lam0 + dlam / 2, 0.09, f"{dlam:.2f} nm", fontsize=6.4, ha="center", va="bottom", color=INK)
    b.annotate(f"neighbours: {loss - gm(lam0 + dlam):.3f} cm$^{{-1}}$\nbelow the loss", xy=(lam0 - dlam, gm(lam0 - dlam) - loss),
               xytext=(lam0 - 4.0, -0.45), fontsize=6.4, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xlim(lam0 - 4.3, lam0 + 4.3); b.set_ylim(-0.9, 0.25)
    b.set_xticks([1546, 1548, 1550, 1552, 1554])
    finish(b, "Wavelength (nm)", "Modal gain − loss (cm$^{-1}$)")
    tag(b, "b")
    fig.tight_layout(w_pad=1.8)
    save(fig, "ch24_modes")


# ================================================================== Figure 24.8: making a ridge laser (Section 24.9)
def fig_process():
    """Six schematic cross-sections of the ridge laser of Figure 24.1 from the epitaxial wafer to coated bars."""
    fig = plt.figure(figsize=(6.3, 3.55))
    titles = ["1 · grow the layers", "2 · etch the ridge", "3 · passivate", "4 · planarise, open the ridge",
              "5 · contacts, thin, back metal", "6 · cleave into bars, coat"]
    notes = ["MOVPE on an n-InP wafer:\nwells, claddings, contact layer",
             "SiO₂ mask; dry etch, then a wet\netch that stops on the etch stop",
             "SiN over every etched surface",
             "spin BCB, etch it back to the\nridge top, open the SiN there",
             "Ti/Pt/Au on the ridge and pad;\nwafer thinned to ~100 µm, n metal",
             "cleaved facets are mirrors;\nHR at the back, AR or none in front"]
    X0, X1 = -5.0, 5.0
    z_sub, z_buf, z_act, t_act, z_res, z_es = -1.6, -0.5, 0.0, 0.35, 0.35, 0.95
    z_top, z_cap = 2.35, 2.6                      # schematic heights (layers exaggerated)
    RW = 1.2
    for k in range(6):
        r, c = divmod(k, 3)
        ax = fig.add_axes([c / 3 + 0.004, 0.52 - r * 0.5, 1 / 3 - 0.012, 0.44]); frameless(ax, (-5.3, 5.3), (-3.6, 4.6), equal=False)
        ax.text(-5.2, 4.55, titles[k], fontsize=FS, color=INK, fontweight="bold", va="top")
        label(ax, 0, -2.85, notes[k], fs=FS_SMALL)
        if k == 5:
            # a laser bar seen from above: chips side by side, ridges running front to back, coatings on the facets
            for i in range(5):
                x = -4.5 + i * 1.8
                box(ax, x, -1.4, 1.8, 4.2, "#E6E1D5", ec=INK, lw=0.5, z=2)
                box(ax, x + 0.75, -1.4, 0.3, 4.2, "inp", ec=INK, lw=0.3, z=3)
                box(ax, x + 0.3, -0.2, 1.2, 1.8, "metal", alpha=0.85, z=4)
            box(ax, -4.5, 2.8, 9.0, 0.35, "#9FD3E0", z=5); box(ax, -4.5, -1.75, 9.0, 0.35, "#F2D4CF", z=5)
            label(ax, 0, 3.55, "HR coating (back facet)", fs=FS_SMALL); label(ax, 4.75, -1.58, "AR", fs=FS_SMALL, ha="left")
            for i in range(1, 5):
                ax.plot([-4.5 + i * 1.8] * 2, [-1.75, 3.15], color=RED, lw=0.7, ls=(0, (2, 2)), zorder=6)
            arrow(ax, (0, -1.85), (0, -2.35), col=RED, lw=1.0, ms=6)
            continue
        # epitaxial stack (full width), with the ridge cut from step 2 on
        box(ax, X0, -2.0 if k < 4 else -2.0, X1 - X0, z_buf - (-2.0), "inp", z=1)
        box(ax, X0, z_buf, X1 - X0, -z_buf, "inp", z=1, alpha=0.85)
        box(ax, X0, z_act, X1 - X0, t_act, "q", z=2); box(ax, X0, z_act + 0.13, X1 - X0, 0.09, "mqw", z=3)
        if k == 0:
            box(ax, X0, z_res, X1 - X0, z_top - z_res, "#DCD6C8", z=2)
            ax.plot([X0, X1], [z_es, z_es], color="#8E7F5A", lw=1.2, zorder=3)
            box(ax, X0, z_top, X1 - X0, z_cap - z_top, "#6E6250", z=3)
            callout(ax, (3.6, z_act + 0.17), (5.25, 1.15), "wells", ha="right")
            callout(ax, (3.6, z_es), (5.25, 1.9), "etch stop", ha="right")
            callout(ax, (-3.6, z_cap - 0.1), (-3.0, 3.6), "p++ InGaAs", ha="left")
            label(ax, -2.5, 1.65, "p-InP", fs=FS_SMALL); label(ax, -2.5, -1.25, "n-InP", fs=FS_SMALL)
            continue
        box(ax, X0, z_res, X1 - X0, z_es - z_res, "#DCD6C8", z=2)
        ax.plot([X0, X1], [z_es, z_es], color="#8E7F5A", lw=1.2, zorder=3)
        box(ax, -RW / 2, z_es, RW, z_top - z_es, "#DCD6C8", z=2)
        box(ax, -RW / 2, z_top, RW, z_cap - z_top, "#6E6250", z=3)
        if k == 1:
            box(ax, -RW / 2 - 0.05, z_cap, RW + 0.1, 0.35, "ox", ec=MUTED, lw=0.5, z=4)
            for xs in (-2.6, 2.6):
                arrow(ax, (xs, 3.9), (xs, z_es + 0.15), col=BLUE, lw=1.0, ms=7)
            label(ax, 0, 3.75, "SiO₂ mask", fs=FS_SMALL)
            continue
        tn = 0.16                                   # SiN: floor, ridge walls, ridge top (opened from step 4)
        box(ax, X0, z_es, X1 - X0, tn, "sin", z=4, alpha=0.9)
        for sg in (-1, 1):
            box(ax, sg * RW / 2 if sg > 0 else -RW / 2 - tn, z_es, tn, z_cap - z_es, "sin", z=4, alpha=0.9)
        if k == 2:
            box(ax, -RW / 2 - tn, z_cap, RW + 2 * tn, tn, "sin", z=4, alpha=0.9)
            continue
        for sg in (-1, 1):
            x0 = RW / 2 + tn if sg > 0 else X0
            box(ax, x0, z_es + tn, X1 - RW / 2 - tn, z_cap - z_es - tn, "bcb", z=3)
        if k == 3:
            label(ax, -3.0, 1.8, "BCB", fs=FS_SMALL)
            arrow(ax, (0, 3.9), (0, z_cap + 0.1), col=BLUE, lw=1.0, ms=7)
            label(ax, 0.35, 3.6, "open", fs=FS_SMALL, ha="left")
            continue
        # k == 4: contacts and back metal; the substrate drawn thinner
        box(ax, -1.6, z_cap, 3.2, 0.3, "metal", z=5); box(ax, 1.6, z_cap, 3.0, 0.3, "metal", z=5)
        box(ax, X0, -2.3, X1 - X0, 0.3, "metal", z=5)
        label(ax, 3.1, 3.25, "pad on BCB", fs=FS_SMALL)
        label(ax, -3.0, 3.25, "Ti/Pt/Au", fs=FS_SMALL)
        label(ax, 0, -1.25, "n-InP", fs=FS_SMALL)
    fig.text(0.995, 0.005, "schematic: layers and ridge exaggerated", ha="right", va="bottom", fontsize=6.0, color=MUTED, style="italic")
    save(fig, "ch24_process")
    print("Fig 24.8: schematic (layer names and order as in Table 24.1)")


if __name__ == "__main__":
    o = fp_op(50e-3)
    print(f"FP laser: V = {V:.2e} cm3, alpha_m {AM:.2f} /cm, g_th {GTH:.1f} /cm, N_th {NTH:.3e}, I_th {ITH*1e3:.2f} mA,"
          f" slope/facet {o['slope']:.3f} W/A, tau_p {TP*1e12:.2f} ps, tau_n = N_th/R {NTH/rrec(NTH)*1e9:.2f} ns")
    only = sys.argv[1:]
    for fn in (fig_ridge, fig_threshold, fig_clamp, fig_turnon, fig_modes, fig_process):
        if not only or fn.__name__ in only:
            fn()
