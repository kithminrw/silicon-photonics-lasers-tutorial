"""Figures and numbers for Chapter 14 (WDM filters and polarisation management).

Run from the worktree root:   python -I -X utf8 figsrc/ch14_figs.py
Writes assets/figs/ch14_*.svg (and PNG previews if $FIGPREVIEW is set) and prints every number the figures and
captions use.

Reference link (Chapter 1, Table 1.3): four channels on the 400 GHz ITU grid, 193.9 to 192.7 THz. Ring
demultiplexer of Worked Example 14.1: n_g = 4.18, FSR = 4 x 3.2 nm = 12.8 nm, so L = 44.9 um (R = 7.15 um), and
FWHM 0.64 nm (Q_L ~ 2400) for -20 dB at the neighbouring channel (Lorentzian estimate).
"""
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
C0 = 299792.458                            # nm * THz
NG, NEFF, LAM = 4.18, 2.446, 1550.0        # nm units below
F_CH = [193.9, 193.5, 193.1, 192.7]        # THz
L_CH = [C0 / f for f in F_CH]
SPACING = 3.2                              # nm (400 GHz)
FSR = 4 * SPACING
L_RING = LAM ** 2 / (NG * FSR) * 1e-3      # um
R_RING = L_RING / (2 * np.pi)
FWHM = 2 * SPACING / np.sqrt(99)           # nm, -20 dB at 3.2 nm for a Lorentzian
LOSS_DB = 2.0


def a_of(loss_db, L_um):
    return np.exp(-loss_db * 100 / 4.343 * L_um * 1e-6 / 2)


A_RING = a_of(LOSS_DB, L_RING)


def coupling_for_fwhm(fw_nm):
    """Self-coupling t (both couplers equal) giving the wanted add-drop FWHM."""
    k = fw_nm * np.pi * NG * L_RING * 1e3 / LAM ** 2          # (1 - x)/sqrt(x) with x = t^2 a
    x = ((-k + np.sqrt(k * k + 4)) / 2) ** 2
    return np.sqrt(x / A_RING)


T_RING = coupling_for_fwhm(FWHM)


def ring_fields(lam, lres, t=T_RING, a=A_RING):
    """Through and drop field transmissions of a symmetric add-drop ring resonant at lres (nm)."""
    phi = -2 * np.pi * NG * L_RING * 1e3 * (lam - lres) / lres ** 2
    e = np.exp(-1j * phi)
    den = 1 - t * t * a * e
    return (t - t * a * e) / den, -(1 - t * t) * np.sqrt(a) * np.exp(-1j * phi / 2) / den


def numbers():
    print("channels (nm):", [f"{l:.2f}" for l in L_CH], " spacings:", [f"{L_CH[i+1]-L_CH[i]:.2f}" for i in range(3)])
    print(f"ring: FSR {FSR} nm -> L {L_RING:.2f} um, R {R_RING:.3f} um; FWHM {FWHM:.3f} nm -> Q_L {LAM/FWHM:.0f}")
    print(f"couplers: t {T_RING:.4f}, kappa^2 {100*(1-T_RING**2):.1f} % each; a {A_RING:.5f}")
    _, d0 = ring_fields(np.array([LAM]), LAM)
    _, d1 = ring_fields(np.array([LAM + SPACING]), LAM)
    _, d2 = ring_fields(np.array([LAM + 2 * SPACING]), LAM)
    print(f"single ring drop: peak {10*np.log10(abs(d0[0])**2):.2f} dB, at +3.2 nm {10*np.log10(abs(d1[0])**2):.1f} dB "
          f"(Lorentzian {10*np.log10(1/(1+(2*SPACING/FWHM)**2)):.1f} dB), at +6.4 nm {10*np.log10(abs(d2[0])**2):.1f} dB")
    dr = (SPACING / LAM) * (NG / NEFF) * R_RING * 1000
    print(f"radius step per channel (no heater): {dr:.1f} nm")


# ------------------------------------------------------------------ Figure 14.1: grids
def fig_grids():
    cw = [1271, 1291, 1311, 1331]
    lan_f = [231.4, 230.6, 229.8, 229.0]
    lan = [C0 / f for f in lan_f]
    print("LAN-WDM (nm):", [f"{x:.2f}" for x in lan], "spacing", [f"{lan[i+1]-lan[i]:.2f}" for i in range(3)])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.3, 3.5), gridspec_kw=dict(height_ratios=[1, 1.35], hspace=0.95))
    rows = [("CWDM, 20 nm", cw, C3, 2), ("LAN-WDM, 800 GHz", lan, C2, 1), ("DWDM, 400 GHz", L_CH, C1, 0)]
    a1.axvspan(1260, 1360, color=GRID, alpha=0.6, lw=0); a1.axvspan(1530, 1565, color=GRID, alpha=0.6, lw=0)
    a1.text(1310, 3.05, "O band", ha="center", fontsize=6.6, color=MUTED); a1.text(1547.5, 3.05, "C band", ha="center", fontsize=6.6, color=MUTED)
    for name, ls, col, y in rows:
        for l in ls:
            a1.plot([l, l], [y - 0.3, y + 0.3], color=col, lw=1.4)
        a1.text(1365 if y > 0 else 1520, y, name, va="center", ha="left" if y > 0 else "right", fontsize=7, color=col)
    a1.set_xlim(1255, 1575); a1.set_ylim(-0.6, 3.5); a1.set_yticks([]); a1.grid(axis="y", visible=False)
    a1.spines["left"].set_visible(False)
    finish(a1, "Wavelength (nm)")
    tag(a1, "a")
    # zoom on the reference link: 100 GHz ITU grid, the four 400 GHz channels and their ~50 GHz signal width
    fgrid = np.round(np.arange(192.5, 194.11, 0.1), 2)
    for f in fgrid:
        a2.plot([C0 / f] * 2, [0, 0.35], color=MUTED, lw=0.6)
    for i, (f, l) in enumerate(zip(F_CH, L_CH)):
        lo, hi = C0 / (f + 0.025), C0 / (f - 0.025)
        a2.add_patch(Rectangle((lo, 0), hi - lo, 1.0, fc=C1, alpha=0.25, lw=0))
        a2.plot([l, l], [0, 1.0], color=C1, lw=1.4)
        a2.text(l, 1.12, f"λ$_{i+1}$\n{l:.2f}", ha="center", va="bottom", fontsize=6.8, color=INK, linespacing=1.1)
    dim(a2, (L_CH[1], 0.62), (L_CH[2], 0.62), "")
    a2.text((L_CH[1] + L_CH[2]) / 2, 0.70, f"{L_CH[2]-L_CH[1]:.2f} nm\n400 GHz", ha="center", va="bottom", fontsize=6.6, color=INK, linespacing=1.0)
    print(f"50 GHz signal width at 1550 nm: {LAM**2*0.05/C0:.2f} nm")
    a2.set_xlim(1544.5, 1557.5); a2.set_ylim(0, 1.75); a2.set_yticks([]); a2.grid(False)
    a2.spines["left"].set_visible(False)
    finish(a2, "Wavelength (nm)")
    sec = a2.secondary_xaxis("top", functions=(lambda l: C0 / np.maximum(l, 1e-9), lambda f: C0 / np.maximum(f, 1e-9)))
    sec.set_xticks(F_CH); sec.set_xticklabels([f"{f:.1f}" for f in F_CH]); sec.set_xlabel("Frequency (THz)", fontsize=8)
    a2.text(1547.7, 0.5, "100 GHz grid", ha="center", va="center", fontsize=6.2, color=MUTED, bbox=dict(fc="white", ec="none", pad=0.5))
    tag(a2, "b")
    save(fig, "ch14_grids")


# ------------------------------------------------------------------ Figure 14.2: ring demultiplexer
def fig_demux():
    fig = plt.figure(figsize=(6.3, 3.95))
    ax = fig.add_axes([0.0, 0.55, 1.0, 0.45])
    R, w = R_RING, 0.5
    pitch = 36.0; xs = [i * pitch for i in range(4)]
    frameless(ax, (-34, 3 * pitch + 30), (-9, 31))
    yb = 0.0; cy = R + w + 0.15
    wg_straight(ax, -32, 3 * pitch + 28, yb, w, "si")
    arrow(ax, (-32, -3.0), (-22, -3.0), col=RED, lw=1.0, ms=7)
    label(ax, -32, -6.3, "λ$_1$ … λ$_4$ in", ha="left", fs=7)
    arrow(ax, (3 * pitch + 18, -3.0), (3 * pitch + 28, -3.0), col=RED, lw=1.0, ms=7)
    label(ax, 3 * pitch + 28, -6.3, "through", ha="right", fs=7)
    for i, x in enumerate(xs):
        wg_arc(ax, x, cy, R + 0.0, 1.6, -60, 240, "tin", alpha=0.55, z=3)
        wg_ring(ax, x, cy, R, w, "si", z=2)
        yd = cy + R + w + 0.15
        wg_straight(ax, x - 9.5, x + 9.0, yd, w, "si")
        box(ax, x - 9.5 - 15, yd - 2.0, 15, 4.0, "ge", z=3)
        label(ax, x - 17, yd, "PD", fs=6.6, col="white" if False else INK)
        arrow(ax, (x + 5, yd + 1.6), (x - 3, yd + 1.6), col=SERIES[i], lw=1.0, ms=6)
        label(ax, x - 17, yd + 4.6, f"λ$_{i+1}$ = {L_CH[i]:.2f} nm", fs=6.6, col=SERIES[i])
    callout(ax, (xs[3] + R * np.cos(np.radians(-30)), cy + R * np.sin(np.radians(-30))), (xs[3] + 14, cy - 2), "heater", fs=6.6)
    dim(ax, (xs[0], cy), (xs[0] + R * np.cos(np.radians(150)), cy + R * np.sin(np.radians(150))), "")
    label(ax, xs[0] - 8.3, cy + 0.6, f"R = {R:.2f} µm", fs=6.3, ha="right", va="center")
    scalebar(ax, 3 * pitch + 8, 26, 10, "10 µm")
    panel(ax, "a", x=0.0, y=1.0)
    # spectra at the four drop ports, cascaded along the bus
    b = fig.add_axes([0.085, 0.1, 0.84, 0.38])
    lam = np.linspace(1531, 1571, 40001)
    thru = np.ones_like(lam, complex)
    for i, lr in enumerate(L_CH):
        t, d = ring_fields(lam, lr)
        D = np.abs(thru * d) ** 2
        b.plot(lam, 10 * np.log10(np.maximum(D, 1e-6)), color=SERIES[i], lw=1.3)
        xt = [10 * np.log10(np.abs(thru[np.argmin(np.abs(lam - lc))] * d[np.argmin(np.abs(lam - lc))]) ** 2) for lc in L_CH]
        print(f"drop {i+1} at the four channels (dB): " + ", ".join(f"{x:.1f}" for x in xt))
        thru = thru * t
    Tt = np.abs(thru) ** 2
    print("through port after four rings at the channels (dB):", ", ".join(f"{10*np.log10(Tt[np.argmin(np.abs(lam-lc))]):.1f}" for lc in L_CH))
    for i, l in enumerate(L_CH):
        b.axvline(l, color=SERIES[i], lw=0.6, ls=":")
    b.axhline(-20, color=MUTED, lw=0.7, ls=(0, (4, 2)))
    b.text(1571.4, -20, "−20 dB", fontsize=6.6, color=MUTED, va="center", ha="left", clip_on=False)
    for k in (-1, 1):
        x = L_CH[0] + k * FSR
        b.annotate("", xy=(x, 1.2), xytext=(L_CH[0], 1.2), arrowprops=dict(arrowstyle="<|-|>", color=C1, lw=0.7, mutation_scale=6)) if k == 1 else None
    b.text(L_CH[0] + FSR / 2, 1.6, f"FSR {FSR:.1f} nm", ha="center", va="bottom", fontsize=6.6, color=C1)
    b.set_xlim(1531, 1571); b.set_ylim(-32, 4.5)
    finish(b, "Wavelength (nm)", "Drop-port transmission (dB)")
    tag(b, "b")
    save(fig, "ch14_demux")


# ------------------------------------------------------------------ Figure 14.4: AWG and echelle (schematic)
def fig_awg_echelle():
    fig = plt.figure(figsize=(6.3, 2.75))
    ax = fig.add_axes([0.0, 0.0, 0.56, 1.0]); frameless(ax, (-5.6, 5.6), (-3.6, 3.2))
    wa = 0.09; n = 9; r0, dr = 1.9, 0.26
    rk = r0 + dr * np.arange(n)
    yc = -0.6                                          # centre of the nested arcs
    for sgn, nm in ((-1, "in"), (1, "out")):
        cx = sgn * (rk[0] + rk[-1]) / 2; cy = yc - 1.9                 # focal point of the star coupler
        face = np.c_[sgn * rk, np.full(n, yc)]
        ang = np.degrees(np.arctan2(face[:, 1] - cy, face[:, 0] - cx))
        rho = np.hypot(face[:, 0] - cx, face[:, 1] - cy).max()
        th = np.radians(np.linspace(ang.min() - 4, ang.max() + 4, 60))
        poly(ax, np.vstack([[cx, cy], np.c_[cx + rho * np.cos(th), cy + rho * np.sin(th)]]), "si", z=2)
        for k in range(n):                                              # short radial stubs up to the arcs
            a_ = np.radians(ang[k]); p0 = np.array([cx + rho * np.cos(a_), cy + rho * np.sin(a_)])
            ribbon(ax, [p0[0], face[k, 0]], [p0[1], max(face[k, 1], p0[1])], wa, "si")
        label(ax, cx, cy - 0.35, "free-propagation\nregion", fs=6.3, va="top")
        if nm == "in":
            ribbon(ax, [-5.5, cx], [cy, cy], wa, "si"); label(ax, -5.5, cy + 0.25, "in", fs=6.8, ha="left", va="bottom")
        else:
            for j, dy in enumerate((0.42, 0.14, -0.14, -0.42)):
                xx = np.linspace(cx, 5.3, 40); yy = cy + dy * (xx - cx) / (5.3 - cx)
                ribbon(ax, xx, yy, wa, "si")
                ax.text(5.35, yy[-1], f"λ$_{4-j}$", fontsize=6.6, va="center", ha="left", color=SERIES[3 - j])
    for k in range(n):                                                  # arrayed waveguides: semicircles, step pi*dr
        t = np.linspace(np.pi, 0, 200)
        ribbon(ax, rk[k] * np.cos(t), yc + rk[k] * np.sin(t), wa, "si")
    dim(ax, (0, yc + rk[0]), (0, yc + rk[-1]), "")
    label(ax, 0.15, yc + (rk[0] + rk[-1]) / 2, "", fs=6.3)
    label(ax, 0, yc + rk[-1] + 0.3, "arrayed waveguides: each π × spacing = ΔL longer", fs=6.6, va="bottom")
    panel(ax, "a", x=0.0, y=1.0)
    # echelle grating
    b = fig.add_axes([0.58, 0.0, 0.42, 1.0]); frameless(b, (-0.6, 5.2), (-3.4, 3.4))
    Rg = 4.2
    th = np.radians(np.linspace(-38, 38, 200))
    gx, gy = Rg * np.cos(th), Rg * np.sin(th)
    poly(b, np.vstack([[[0.05, -0.55], [0.05, 0.55]], np.c_[gx, gy][::-1]]), "si", z=1)
    nf = 16; tt = np.radians(np.linspace(-36, 36, nf + 1))
    for i in range(nf):
        p0 = Rg * np.array([np.cos(tt[i]), np.sin(tt[i])]); p1 = Rg * np.array([np.cos(tt[i + 1]), np.sin(tt[i + 1])])
        m = p0 + 0.55 * (p1 - p0) + 0.12 * np.array([np.cos(tt[i]), np.sin(tt[i])])
        poly(b, [p0, m, p1, p1 + 0.12 * np.array([np.cos(tt[i + 1]), np.sin(tt[i + 1])]), p0 + 0.12 * np.array([np.cos(tt[i]), np.sin(tt[i])])], "metal", z=2)
    ribbon(b, [-0.55, 0.05], [0.42, 0.42], 0.09, "si")
    for k, yo in enumerate((-0.12, -0.32, -0.52)):
        ribbon(b, [-0.55, 0.05], [yo, yo], 0.09, "si")
    for ang in np.radians([-30, 0, 30]):
        gp = Rg * np.array([np.cos(ang), np.sin(ang)])
        b.plot([0.05, gp[0]], [0.42, gp[1]], color=RED, lw=0.6, alpha=0.8, zorder=3)
        b.plot([gp[0], 0.05], [gp[1], -0.12], color=C1, lw=0.6, ls=(0, (3, 2)), zorder=3)
        b.plot([gp[0], 0.05], [gp[1], -0.52], color=C2, lw=0.6, ls=(0, (3, 2)), zorder=3)
    label(b, -0.55, 0.62, "in", fs=6.8, ha="left")
    label(b, -0.58, -0.85, "outputs", fs=6.8, ha="left", va="top")
    label(b, 2.0, 2.75, "etched, reflecting\ngrating facets", fs=6.6)
    label(b, 2.0, -2.0, "slab", fs=6.8, col=MUTED)
    note(b, "schematics, not to scale", loc="lower right")
    panel(b, "b", x=0.0, y=1.0)
    save(fig, "ch14_awg")


# ------------------------------------------------------------------ Figure 14.3: Lorentzian against flat-top
def fig_flattop():
    d = np.linspace(-5, 5, 4001)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.5, 1]))
    sig = 0.2                                         # half of the ~0.4 nm a 50 Gb/s NRZ signal occupies
    for n, col, lab in ((1, C1, "1st order (one ring, Lorentzian)"), (2, C2, "2nd order"), (3, C3, "3rd order")):
        H = 1 / (1 + (2 * d / FWHM) ** (2 * n))
        a1.plot(d, 10 * np.log10(H), color=col, lw=1.5, label=lab)
        a2.plot(d, 10 * np.log10(H), color=col, lw=1.5)
        x3 = 10 * np.log10(1 / (1 + (2 * SPACING / FWHM) ** (2 * n)))
        xe = 10 * np.log10(1 / (1 + (2 * sig / FWHM) ** (2 * n)))
        print(f"order {n}: at 3.2 nm {x3:.1f} dB, at the edge of a 0.4 nm signal band {xe:.2f} dB")
    for x in (-SPACING, SPACING):
        a1.axvline(x, color=MUTED, lw=0.7, ls=":")
    a1.axhline(-20, color=MUTED, lw=0.7, ls=(0, (4, 2)))
    a1.text(SPACING + 0.1, -55, "neighbouring\nchannel", fontsize=6.4, color=MUTED, ha="left")
    a1.set_xlim(-5, 5); a1.set_ylim(-86, 3)
    finish(a1, "Detuning from the channel (nm)", "Drop-port transmission (dB)")
    a1.legend(loc="lower center", fontsize=6.6, borderaxespad=0.2)
    a2.axvspan(-sig, sig, color=C1, alpha=0.10, lw=0)
    a2.text(0, -2.85, "signal band\n≈ 0.4 nm", ha="center", fontsize=6.4, color=C1, va="bottom")
    a2.set_xlim(-0.6, 0.6); a2.set_ylim(-3.2, 0.2)
    finish(a2, "Detuning (nm)", "Transmission (dB)")
    tag(a1, "a"); tag(a2, "b"); fig.tight_layout(w_pad=1.8)
    save(fig, "ch14_flattop")


# ------------------------------------------------------------------ Figure 14.5: polarisation splitter-rotator (schematic)
def fig_psr():
    SLAB = "#C9D6E4"                                   # partially etched slab: a lighter shade of silicon
    fig = plt.figure(figsize=(6.3, 3.0))
    ax = fig.add_axes([0.0, 0.36, 1.0, 0.64]); frameless(ax, (-0.3, 16.3), (-1.55, 2.25), equal=False)
    box(ax, 0, -0.22, 2.2, 0.44, "si", z=3)
    poly(ax, [(2.2, -0.22), (4.3, -0.95), (6.4, -0.40), (6.4, 0.40), (4.3, 0.95), (2.2, 0.22)], SLAB, z=2)
    poly(ax, [(2.2, -0.22), (6.4, -0.40), (6.4, 0.40), (2.2, 0.22)], "si", z=3)
    poly(ax, [(6.4, -0.40), (12.2, -0.40), (13.6, -0.22), (16.2, -0.22), (16.2, 0.22), (13.6, 0.22), (12.2, 0.40), (6.4, 0.40)], "si", z=3)
    # narrow guide: starts from a tip beside the wide guide, runs parallel, then bends away
    gap, wn = 0.16, 0.22
    yN = 0.40 + gap + wn / 2
    xn = np.linspace(8.6, 16.2, 400)
    yn = yN + np.where(xn > 12.2, 1.3 * (1 - np.cos(np.pi * np.clip((xn - 12.2) / 2.2, 0, 1))) / 2, 0)
    wnz = wn * np.clip((xn - 8.6) / 0.8, 0.15, 1)
    top = np.c_[xn, yn + wnz / 2]; bot = np.c_[xn, yn - wnz / 2]
    poly(ax, np.vstack([top, bot[::-1]]), "si", z=3)
    for x0, x1, t in ((0, 2.2, "strip"), (2.2, 6.4, "bilevel taper\n(rib, partial etch)"), (6.4, 8.5, "wide strip"), (8.6, 12.2, "asymmetric coupler")):
        ax.plot([x0 + 0.05, x1 - 0.05], [-1.25, -1.25], color=MUTED, lw=0.7)
        label(ax, (x0 + x1) / 2, -1.42, t, fs=6.4, col=MUTED, va="top")
    label(ax, 0.1, 0.45, "TE$_0$ + TM$_0$ in", fs=7, ha="left", va="bottom")
    label(ax, 4.3, 1.05, "TM$_0$ → TE$_1$", fs=7, col=RED, va="bottom")
    label(ax, 7.4, -0.55, "TE$_0$ and TE$_1$", fs=6.6, va="top")
    label(ax, 10.4, 1.05, "TE$_1$ → narrow-guide TE$_0$", fs=6.6, col=RED, va="bottom")
    label(ax, 16.2, yN + 1.3 + 0.28, "TE$_0$ (was TM$_0$)", fs=7, col=RED, ha="right", va="bottom")
    label(ax, 16.2, -0.38, "TE$_0$ (was TE$_0$)", fs=7, ha="right", va="top")
    for x, t in ((1.1, "A"), (4.3, "B"), (10.4, "C")):
        ax.plot([x, x], [-1.05, {"A": 0.32, "B": 0.95, "C": 0.98}[t]], color=INK, lw=0.6, ls=(0, (2, 2)))
        label(ax, x, -1.12, t, fs=7, bold=True, va="top")
    legend_patches(ax, [("si", "full-height Si (220 nm)"), (SLAB, "partially etched slab")], loc="upper left", fs=6.4)
    note(ax, "top view, schematic, not to scale", loc="lower right")
    panel(ax, "a", x=0.0, y=1.08)

    def xsec(rect, items, slab=None, tag_=""):
        c = fig.add_axes(rect); frameless(c, (-1.1, 1.1), (-0.25, 0.55))
        box(c, -1.1, -0.25, 2.2, 0.25, "ox"); box(c, -1.1, 0, 2.2, 0.55, "oxtop")
        if slab: box(c, -1.1, 0, 2.2, slab, SLAB)
        for xc, wv in items: cbox(c, xc, 0, wv, 0.22, "si")
        label(c, -1.05, 0.5, tag_, fs=7, bold=True, ha="left", va="top")
        return c
    xsec([0.03, 0.02, 0.26, 0.3], [(0, 0.45)], tag_="A")
    cb = xsec([0.37, 0.02, 0.26, 0.3], [(0, 0.65)], slab=0.09, tag_="B")
    label(cb, 1.05, 0.5, "slab only below:\nno up-down symmetry", fs=5.9, ha="right", va="top", col=MUTED)
    cc = xsec([0.71, 0.02, 0.26, 0.3], [(-0.3, 0.8), (0.4, 0.3)], tag_="C")
    scalebar(cc, 0.45, -0.2, 0.5, "500 nm", above=True)
    save(fig, "ch14_psr")


# ------------------------------------------------------------------ Figure 14.6: polarisation diversity
def fig_diversity():
    fig = plt.figure(figsize=(6.3, 3.3))
    for row, (rect, kind) in enumerate((([0.0, 0.52, 1.0, 0.48], "psr"), ([0.0, 0.0, 1.0, 0.48], "gc2d"))):
        ax = fig.add_axes(rect); frameless(ax, (0, 16), (0, 5), equal=False)
        yt, yb = 3.6, 1.4
        block(ax, 1.2, 2.5, 1.9, 1.1, "fibre\n(any pol.)", fs=6.8, fc="#FFFFFF")
        block(ax, 3.6, 2.5, 1.7, 1.1, "edge coupler\n+ PSR" if kind == "psr" else "2D grating\ncoupler", fs=6.8, fc="#E8EEF7")
        wire(ax, [(2.15, 2.5), (2.75, 2.5)], col=OPT)
        wire(ax, [(4.45, 2.75), (5.0, 2.75), (5.0, yt), (6.9, yt)], col=OPT)
        wire(ax, [(4.45, 2.25), (5.0, 2.25), (5.0, yb), (6.9, yb)], col=OPT)
        t1, t2 = ("TE", "TM → TE") if kind == "psr" else ("TE (pol. x)", "TE (pol. y)")
        ax.text(5.15, yt + 0.22, t1, fontsize=6.6, color=OPT, va="bottom"); ax.text(5.15, yb - 0.22, t2, fontsize=6.6, color=OPT, va="top")
        for y in (yt, yb):
            block(ax, 8.5, y, 3.2, 1.0, "identical TE circuit\n(ring demux)", fs=6.6, fc="#F3F6FB")
            wire(ax, [(10.1, y), (11.0, y)], col=OPT)
            block(ax, 11.6, y, 1.2, 0.8, "PD", fs=6.8, fc=MAT["ge"])
            yy = 2.5 + (0.22 if y > 2.5 else -0.22)
            wire(ax, [(12.2, y), (13.3, y), (13.3, yy), (13.7, yy)], col=ELEC)
        ax.add_patch(Circle((14.05, 2.5), 0.35, fc="white", ec=INK, lw=0.8, zorder=4))
        ax.text(14.05, 2.5, "+", ha="center", va="center", fontsize=9, color=INK, zorder=5)
        wire(ax, [(14.4, 2.5), (15.3, 2.5)], col=ELEC)
        ax.text(15.35, 2.5, "data", va="center", fontsize=6.8)
        panel(ax, "a" if kind == "psr" else "b", x=0.0, y=1.0)
    ax.text(15.9, 0.1, "red: optical, blue: electrical", ha="right", fontsize=6.0, color=MUTED, style="italic")
    save(fig, "ch14_diversity")


# ------------------------------------------------------------------ Figure 14.7: mode-division multiplexing (Section 14.7)
def fig_mdm():
    """(a) n_eff of the TE0, TE1 and TE2 modes and TM0 of 220 nm strips against width, from the femwell sweep of
    Chapter 6 (figsrc/ch06_sweep.json), and the width at which TE1 of a wide guide matches TE0 of a 0.45 um guide.
    (b) Schematic top view of a two-mode link: an asymmetric directional coupler puts TE0 of the narrow guide onto
    TE1 of the bus, and a mirror-image coupler takes it off again."""
    d = json.load(open(os.path.join(HERE, "ch06_sweep.json")))
    W = np.array(d["widths"])
    te = []
    for modes in d["neff1550"]:
        te.append(sorted([n for n, f in modes if f > 0.5], reverse=True))
    tm0 = np.array([max([n for n, f in modes if f <= 0.5] or [np.nan]) for modes in d["neff1550"]])
    def mode(k):
        return np.array([t[k] if len(t) > k else np.nan for t in te])
    te0, te1, te2 = mode(0), mode(1), mode(2)
    n_target = np.interp(0.45, W, te0)
    ok = ~np.isnan(te1)
    w_pm = np.interp(n_target, te1[ok], W[ok])
    s0 = (np.interp(0.475, W, te0) - np.interp(0.425, W, te0)) / 0.05
    s1 = (np.interp(w_pm + 0.025, W[ok], te1[ok]) - np.interp(w_pm - 0.025, W[ok], te1[ok])) / 0.05
    print(f"Fig 14.7: TE0 at 0.45 um: n_eff {n_target:.4f}; TE1 matches at w = {w_pm:.3f} um; slopes dn/dw TE0 {s0:.2f}, TE1 {s1:.2f} /um;"
          f" a common 10 nm width error mismatches by {abs(s0 - s1) * 0.01:.4f}")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.1]))
    a.plot(W, te0, color=C1, label="TE0"); a.plot(W, te1, color=C2, label="TE1"); a.plot(W, te2, color=C3, label="TE2")
    a.plot(W, tm0, color=MUTED, lw=1.0, ls=(0, (3, 2)), label="TM0")
    a.axhline(n_target, color=INK, lw=0.6, ls=":")
    a.plot([0.45], [n_target], "o", color=C1, ms=4); a.plot([w_pm], [n_target], "o", color=C2, ms=4)
    a.annotate(f"TE1 at {w_pm:.2f} µm\nmatches TE0 at 0.45 µm", xy=(w_pm, n_target), xytext=(0.52, 2.62), fontsize=6.4,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a.set_xlim(0.25, 1.0); a.set_ylim(1.4, 2.8)
    finish(a, "Strip width (µm), 220 nm Si", "Effective index at 1550 nm")
    a.legend(loc="lower right", fontsize=6.4)
    frameless(b, (0, 100), (0, 60), equal=False)
    yb = 22
    b.add_patch(Rectangle((4, yb - 2.2), 92, 4.4, fc=MAT["si"], ec="none"))
    for x0, dirn in ((14, 1), (86, -1)):
        xs = np.linspace(0, 1, 40)
        if dirn > 0:
            b.plot(4 + 10 * xs, 42 - 0 * xs, color=MAT["si"], lw=2.0)
            b.plot(14 + 8 * xs, 42 - 12 * (1 - np.cos(np.pi * xs)) / 2, color=MAT["si"], lw=2.0)
            b.plot([22, 36], [30, 30], color=MAT["si"], lw=2.0)
            b.plot(36 + 8 * xs, 30 + 12 * (1 - np.cos(np.pi * xs)) / 2, color=MAT["si"], lw=2.0)
        else:
            b.plot(56 + 8 * xs, 42 - 12 * (1 - np.cos(np.pi * xs)) / 2, color=MAT["si"], lw=2.0)
            b.plot([64, 78], [30, 30], color=MAT["si"], lw=2.0)
            b.plot(78 + 8 * xs, 30 + 12 * (1 - np.cos(np.pi * xs)) / 2, color=MAT["si"], lw=2.0)
            b.plot(86 + 10 * xs, 42 + 0 * xs, color=MAT["si"], lw=2.0)
    b.add_patch(Rectangle((22, 26.5), 14, 3.5, fc="none", ec=AMBER, lw=0.8, ls=(0, (2, 2))))
    b.add_patch(Rectangle((64, 26.5), 14, 3.5, fc="none", ec=AMBER, lw=0.8, ls=(0, (2, 2))))
    label(b, 29, 36, "mux:\nTE0 → TE1", fs=FS_SMALL, col=AMBER); label(b, 71, 36, "demux:\nTE1 → TE0", fs=FS_SMALL, col=AMBER)
    label(b, 50, yb - 7, f"multimode bus, {w_pm:.2f} µm: TE0 and TE1 together", fs=FS_SMALL)
    label(b, 4, 46, "channel 2 (TE0)", fs=FS_SMALL, ha="left"); label(b, 96, 46, "channel 2 out", fs=FS_SMALL, ha="right")
    label(b, 4, yb + 6, "channel 1 (TE0)", fs=FS_SMALL, ha="left"); label(b, 96, yb + 6, "channel 1 out", fs=FS_SMALL, ha="right")
    for xc, k in ((50, 0), (50, 1)):
        yy = np.linspace(-1, 1, 50)
        prof = np.cos(np.pi * yy / 2) if k == 0 else np.sin(np.pi * yy)
        b.plot(xc - 14 + 10 * k * 2 + 4 * prof, yb + 2.0 * yy, color=C1 if k == 0 else C2, lw=1.0)
    label(b, 40, yb - 3.5, "TE0", fs=5.8, col=C1); label(b, 60, yb - 3.5, "TE1", fs=5.8, col=C2)
    note(b, "schematic", "lower right"); panel(b, "b", 0.0, 1.0)
    tag(a, "a"); fig.tight_layout(w_pad=1.5)
    save(fig, "ch14_mdm")


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1:
        for _n in _s.argv[1:]: globals()['fig_' + _n]()
    else:
        numbers()
        fig_grids(); fig_demux(); fig_awg_echelle(); fig_flattop(); fig_psr(); fig_diversity(); fig_mdm()
