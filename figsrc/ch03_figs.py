"""Figures for Chapter 3 (Gaussian beams and optical fibres).

Run from the repository root:   python -I -X utf8 figsrc/ch03_figs.py
Writes assets/figs/ch03_beam.svg, ch03_lens.svg, ch03_fibre.svg, ch03_bands.svg and prints the numbers they show.
The fibre is the chapter's step-index model of standard single-mode fibre (a = 4.1 µm, Δ = 0.36 %, n2 = 1.444 at
1550 nm; Worked Example 3.3). LP01 is solved exactly (weakly guiding Bessel solution); the Bessel functions are
evaluated from their integral representations, so no SciPy is needed.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *      # noqa: F401,E402
from geomstyle import *     # noqa: F401,E402
import matplotlib  # noqa: E402
from part1_figs import n_sio2   # noqa: E402  (Malitson)

LAM = 1.55

# ------------------------------------------------------------------ Bessel functions without SciPy
_TJ = np.linspace(0, np.pi, 401)
_TK = np.linspace(0, 12, 2401)


def J(n, x):
    x = np.atleast_1d(np.asarray(x, float)); shp = x.shape; x = x.ravel()
    return (np.trapezoid(np.cos(n * _TJ[None, :] - x[:, None] * np.sin(_TJ[None, :])), _TJ, axis=1) / np.pi).reshape(shp)


def K(n, x):
    x = np.atleast_1d(np.asarray(x, float)); shp = x.shape; x = x.ravel()
    return np.trapezoid(np.exp(-x[:, None] * np.cosh(_TK[None, :])) * np.cosh(n * _TK[None, :]), _TK, axis=1).reshape(shp)


# ------------------------------------------------------------------ LP01 of a step-index fibre
A_CORE, DELTA = 4.1, 0.0036


def fibre_indices(lam):
    n2 = n_sio2(lam) * 1.444 / n_sio2(1.55)          # cladding: silica, scaled to the chapter's 1.444 at 1550 nm
    n1 = n2 / np.sqrt(1 - 2 * DELTA)                   # core: same Δ at every wavelength
    return n1, n2


def lp01(lam, a=A_CORE):
    """(V, u, w, n_eff) of LP01: u J1(u)/J0(u) = w K1(w)/K0(w), u^2 + w^2 = V^2."""
    n1, n2 = fibre_indices(lam)
    V = 2 * np.pi * a / lam * np.sqrt(n1 ** 2 - n2 ** 2)
    f = lambda u: u * J(1, u)[0] / J(0, u)[0] - np.sqrt(V ** 2 - u ** 2) * K(1, np.sqrt(V ** 2 - u ** 2))[0] / K(0, np.sqrt(V ** 2 - u ** 2))[0]
    lo, hi = 1e-6, min(V, 2.4048) - 1e-9
    for _ in range(80):
        m = (lo + hi) / 2
        if f(lo) * f(m) <= 0: hi = m
        else: lo = m
    u = (lo + hi) / 2; w = np.sqrt(V ** 2 - u ** 2)
    b = 1 - u ** 2 / V ** 2
    return V, u, w, np.sqrt(n2 ** 2 + b * (n1 ** 2 - n2 ** 2))


def lp01_field(r, lam, a=A_CORE):
    V, u, w, _ = lp01(lam, a)
    r = np.asarray(r, float); R = np.abs(r) / a
    out = np.where(R <= 1, J(0, u * np.minimum(R, 1)) / J(0, u)[0], K(0, w * np.maximum(R, 1)) / K(0, w)[0])
    return out / (1 / J(0, u)[0])                       # 1 on the axis


def marcuse_w(lam, a=A_CORE):
    V = lp01(lam, a)[0]
    return a * (0.65 + 1.619 * V ** -1.5 + 2.879 * V ** -6)


# ------------------------------------------------------------------ Figure: anatomy of a Gaussian beam
def fig_beam():
    w0, lam = 1.5, LAM                                   # the 1.5 µm spot of Worked Example 3.1
    zR = np.pi * w0 ** 2 / lam; th0 = lam / (np.pi * w0)
    k = 2 * np.pi / lam
    print("beam: w0 %.2f µm, zR %.2f µm, theta0 %.3f rad = %.1f°, R(zR) = %.2f µm" % (w0, zR, th0, np.degrees(th0), 2 * zR))
    w0b = 5.2; zRb = np.pi * w0b ** 2 / lam
    zc = np.sqrt((w0b ** 2 - w0 ** 2) / (w0 ** 2 / zR ** 2 - w0b ** 2 / zRb ** 2))
    print("SMF spot: w0 %.1f µm, zR %.1f µm, theta0 %.1f°; the two beams are equally wide at z = %.1f µm" %
          (w0b, zRb, np.degrees(lam / (np.pi * w0b)), zc))
    fig = plt.figure(figsize=(6.3, 4.55))
    a = fig.add_axes([0.0, 0.42, 1.0, 0.58])
    Z0, X0 = 16.0, 6.4
    z = np.linspace(-Z0, Z0, 1400); x = np.linspace(-X0, X0, 560)
    ZZ, XX = np.meshgrid(z, x)
    w = w0 * np.sqrt(1 + (ZZ / zR) ** 2)
    invR = ZZ / (ZZ ** 2 + zR ** 2)
    E = (w0 / w) * np.exp(-XX ** 2 / w ** 2) * np.cos(k * ZZ + k * XX ** 2 * invR / 2 - np.arctan(ZZ / zR))
    a.imshow(E, extent=(-Z0, Z0, -X0, X0), origin="lower", cmap=SIGNED_CMAP, vmin=-1, vmax=1, aspect="equal", interpolation="bilinear", zorder=0)
    frameless(a, xlim=(-Z0, Z0), ylim=(-X0 - 1.6, X0 + 0.3))
    zz = np.linspace(-Z0, Z0, 400); ww = w0 * np.sqrt(1 + (zz / zR) ** 2)
    a.plot(zz, ww, color=INK, lw=1.0, ls="--"); a.plot(zz, -ww, color=INK, lw=1.0, ls="--")
    a.plot(zz, th0 * np.abs(zz), color=INK, lw=0.6, ls=":"); a.plot(zz, -th0 * np.abs(zz), color=INK, lw=0.6, ls=":")
    for zp in (-zR, zR):
        a.plot([zp, zp], [-X0, X0], color=MUTED, lw=0.6, ls=(0, (2, 2)))
    # the wavefront through z = zR is a sphere of radius R = 2 zR centred at z = -zR
    t = np.radians(np.linspace(-15, 15, 50)); Rr = 2 * zR
    a.plot(-zR + Rr * np.cos(t), Rr * np.sin(t), color=AMBER, lw=1.6)
    label(a, zR + 0.4, 3.5, "wavefront at $z_R$:\n$R = 2z_R$ = %.1f µm" % (2 * zR), fs=6.6, ha="left", col=INK, bg="white")
    dim(a, (0, -w0), (0, w0), "", fs=6.4)
    label(a, 0.45, -0.6, "$2w_0$ = %.0f µm" % (2 * w0), fs=6.6, ha="left", bg="white")
    dim(a, (-zR, -X0 - 0.55), (zR, -X0 - 0.55), "$2z_R$ = %.1f µm" % (2 * zR), fs=6.6)
    label(a, -8.0, 4.7, "$w(z)$", fs=7, ha="left", va="bottom", bg="white")
    a.annotate("", (-9.5, w0 * np.sqrt(1 + (9.5 / zR) ** 2)), (-8.0, 4.6), arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    ang = np.linspace(0, th0, 30)
    a.plot(11 * np.cos(ang), 11 * np.sin(ang), color=INK, lw=0.7)
    label(a, 11.5, 1.55, "θ$_0$ = %.0f°" % np.degrees(th0), fs=6.6, ha="left", bg="white")
    a.plot([0, 13], [0, 0], color=INK, lw=0.4)
    scalebar(a, Z0 - 6.2, -X0 - 1.25, 5.0, "5 µm")
    note(a, "to scale; field Re{E} at one instant", loc="lower left")
    panel(a, "a", 0.0, 1.0)
    # (b) two spots
    b = fig.add_axes([0.085, 0.08, 0.38, 0.27])
    zb = np.linspace(0, 100, 500)
    for w_, col, lab in ((w0, C4, "$w_0$ = 1.5 µm (laser, edge coupler)"), (w0b, C1, "$w_0$ = 5.2 µm (SMF mode)")):
        zr_ = np.pi * w_ ** 2 / lam
        b.plot(zb, w_ * np.sqrt(1 + (zb / zr_) ** 2), color=col, label=lab)
        b.plot([zr_], [w_ * np.sqrt(2)], "o", color=col, ms=3.5)
    b.annotate("$z_R$", (zR, w0 * np.sqrt(2)), xytext=(10, 1.0), fontsize=6.6, color=C4, arrowprops=dict(arrowstyle="-", color=C4, lw=0.5))
    b.annotate("$z_R$", (zRb, w0b * np.sqrt(2)), xytext=(68, 4.2), fontsize=6.6, color=C1, arrowprops=dict(arrowstyle="-", color=C1, lw=0.5))
    b.set_xlim(0, 100); b.set_ylim(0, 36)
    finish(b, "Distance from the waist $z$ (µm)", "Beam radius $w$ (µm)", legend=True, loc="upper left")
    b.legend(loc="upper left", fontsize=6.4, handlelength=1.4)
    tag(b, "b")
    # (c) universal curves
    c = fig.add_axes([0.6, 0.08, 0.38, 0.27])
    u = np.linspace(0, 3, 400)
    c.plot(u, np.sqrt(1 + u ** 2), color=C1, label="$w/w_0$")
    uu = u[u > 0.12]
    c.plot(uu, uu * (1 + 1 / uu ** 2) / 2, color=C2, label="$R/(2z_R)$")
    c.plot(u, np.arctan(u) / (np.pi / 4), color=C3, label="Gouy phase ζ / (π/4)")
    c.axvline(1, color=MUTED, lw=0.6, ls=":")
    c.set_xlim(0, 3); c.set_ylim(0, 3.2)
    finish(c, "$z/z_R$", "Normalised value", legend=True, loc="lower right")
    c.legend(loc="lower right", fontsize=6.4, handlelength=1.4)      # clear of the R/(2z_R) curve
    tag(c, "c")
    save(fig, "ch03_beam")


# ------------------------------------------------------------------ Figure: imaging a waist with a lens
def fig_lens():
    w0, f, d1x = 1.5, 100.0, 130.0                       # Worked Example 3.2
    zR = np.pi * w0 ** 2 / LAM
    M = lambda d1: f / np.sqrt((d1 - f) ** 2 + zR ** 2)
    D2 = lambda d1: f + (d1 - f) * f ** 2 / ((d1 - f) ** 2 + zR ** 2)
    print("lens: zR %.2f µm; at d1 = %.0f µm: M = %.2f, w0' = %.2f µm, d2 = %.0f µm; ray optics d2 = %.0f µm, M = %.2f" %
          (zR, d1x, M(d1x), M(d1x) * w0, D2(d1x), f * d1x / (d1x - f), f / (d1x - f)))
    print("      at d1 = f: M = f/zR = %.1f, d2 = f; largest d2 = f + f^2/(2 zR) = %.0f µm at d1 = f + zR" % (f / zR, f + f ** 2 / (2 * zR)))
    fig = plt.figure(figsize=(6.3, 4.3))
    # (a) schematic
    a = fig.add_axes([0.0, 0.50, 1.0, 0.50])
    frameless(a, xlim=(-0.5, 10.5), ylim=(-2.35, 1.75), equal=False)
    zl, zf = 3.2, 9.0
    zs = np.linspace(0, zl, 200); ws = 0.12 * np.sqrt(1 + (zs / 0.45) ** 2)
    zt = np.linspace(zl, 10.2, 300)
    wl = 0.12 * np.sqrt(1 + (zl / 0.45) ** 2)
    # join the two envelopes at the lens: scale the image side so it starts at the beam radius on the lens
    s_img = wl / (0.40 * np.sqrt(1 + ((zl - zf) / 2.2) ** 2))
    wt = 0.40 * s_img * np.sqrt(1 + ((zt - zf) / 2.2) ** 2)
    for sg in (1, -1):
        a.plot(zs, sg * ws, color=RED, lw=1.2); a.plot(zt, sg * wt, color=RED, lw=1.2)
    a.fill_between(zs, -ws, ws, color=RED, alpha=0.12, lw=0); a.fill_between(zt, -wt, wt, color=RED, alpha=0.12, lw=0)
    a.add_patch(Ellipse((zl, 0), 0.22, 2.3, fc=MAT["glass"], ec=BLUE, lw=1.2, zorder=4))
    a.plot([-0.3, 10.3], [0, 0], color=MUTED, lw=0.5, ls="-.")
    for zz, t in ((0, "$w_0$"), (zf, "$w_0′ = Mw_0$")):
        ww = 0.12 if zz == 0 else 0.40 * s_img
        a.annotate("", (zz, ww), (zz, -ww), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
        a.text(zz + 0.1 if zz == 0 else zz, 0.0 if zz == 0 else ww + 0.18, t, fontsize=7, color=INK, ha="left" if zz == 0 else "center",
               va="center" if zz == 0 else "bottom", bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none") if zz == 0 else None)
    for z0, z1, t in ((0, zl, "$d_1$"), (zl, zf, "$d_2$")):
        a.annotate("", (z1, -1.35), (z0, -1.35), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
        a.text((z0 + z1) / 2, -1.27, t, fontsize=7.5, color=INK, ha="center", va="bottom")
    a.text(zl, 1.25, "thin lens $f$", fontsize=7, color=BLUE, ha="center", va="bottom")
    # the ray-transfer matrix of each section, drawn as a 2 x 2 array in brackets
    def mat(xc, yc, e, dx=0.24, dy=0.2):
        for i in range(2):
            for j in range(2):
                a.text(xc + (j - 0.5) * 2 * dx, yc - (i - 0.5) * 2 * dy, e[i][j], fontsize=6.8, ha="center", va="center", color=INK)
        for sgn in (-1, 1):
            xb = xc + sgn * (dx + 0.2)
            a.plot([xb - sgn * 0.06, xb, xb, xb - sgn * 0.06], [yc + 2 * dy, yc + 2 * dy, yc - 2 * dy, yc - 2 * dy], color=INK, lw=0.6)
    mat(zl / 2, -1.85, [["1", "$d_1$"], ["0", "1"]])
    mat(zl, -1.85, [["1", "0"], ["$-1/f$", "1"]], dx=0.3)
    mat((zl + zf) / 2, -1.85, [["1", "$d_2$"], ["0", "1"]])
    a.text(10.3, 1.2, "$q_2 = (Aq_1 + B)/(Cq_1 + D)$\nwith $\\mathbf{M} = \\mathbf{M}_{d_2}\\,\\mathbf{M}_f\\,\\mathbf{M}_{d_1}$",
           fontsize=7, ha="right", va="center", color=INK)
    a.text(-0.3, 1.2, "source waist\n$q_1 = jz_R$", fontsize=7, ha="left", va="center", color=INK)
    note(a, "schematic, not to scale", loc="lower right")
    panel(a, "a", 0.0, 1.0)
    # (b) image distance and (c) magnification against d1, Gaussian against ray optics
    b = fig.add_axes([0.085, 0.09, 0.38, 0.32]); c = fig.add_axes([0.6, 0.09, 0.38, 0.32])
    d1 = np.linspace(20, 300, 2000)
    ray_d2 = np.where(np.abs(d1 - f) > 1e-6, f * d1 / (d1 - f), np.nan); ray_d2[d1 < f] = np.nan
    b.plot(d1, D2(d1), color=C1, label="Gaussian beam")
    b.plot(d1, ray_d2, color=INK, lw=1.0, ls="--", label="ray optics")
    b.plot([d1x], [D2(d1x)], "o", color=C2, ms=4.5, zorder=5)
    b.annotate("Example 3.2:\n%.0f µm" % D2(d1x), (d1x, D2(d1x)), xytext=(165, 620), fontsize=6.6, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.axvline(f, color=MUTED, lw=0.6, ls=":"); b.text(f - 3, 1380, "$d_1 = f$", fontsize=6.6, color=MUTED, va="top", ha="right")
    b.text(60, 80, "virtual waist\n($d_2$ < 0)", fontsize=6.4, color=MUTED, ha="center", va="bottom")
    b.set_xlim(20, 300); b.set_ylim(0, 1400)
    finish(b, "Source to lens $d_1$ (µm)", "Lens to image waist $d_2$ (µm)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.6, handlelength=1.6)
    tag(b, "b")
    c.semilogy(d1, M(d1), color=C1)
    c.semilogy(d1, f / np.abs(d1 - f), color=INK, lw=1.0, ls="--")
    c.plot([d1x], [M(d1x)], "o", color=C2, ms=4.5, zorder=5)
    c.annotate("M = %.2f" % M(d1x), (d1x, M(d1x)), xytext=(170, 6.5), fontsize=6.6, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    c.annotate("$f/z_R$ ≈ %.0f" % (f / zR), (f, f / zR), xytext=(150, 30), fontsize=6.6, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    c.axvline(f, color=MUTED, lw=0.6, ls=":")
    c.set_xlim(20, 300); c.set_ylim(0.3, 100)
    finish(c, "Source to lens $d_1$ (µm)", "Magnification $M = w_0′/w_0$")
    tag(c, "c")
    save(fig, "ch03_lens")


# ------------------------------------------------------------------ Figure: standard single-mode fibre
def fig_fibre():
    rows = []
    for lam in (1.31, 1.55):
        V, u, w, neff = lp01(lam)
        wm = marcuse_w(lam)
        r = np.linspace(0, 40, 4001)
        E = lp01_field(r, lam)
        I = E ** 2
        r_e2 = r[np.argmax(I < np.exp(-2))]
        # overlap of the exact LP01 with its Marcuse Gaussian (2D, radial)
        G = np.exp(-r ** 2 / wm ** 2)
        eta = np.trapezoid(E * G * r, r) ** 2 / (np.trapezoid(E ** 2 * r, r) * np.trapezoid(G ** 2 * r, r))
        rows.append((lam, V, u, w, neff, wm, r_e2, eta))
        print("fibre at %.2f µm: V %.3f, u %.3f, w %.3f, n_eff %.5f, Marcuse MFD %.2f µm, exact 1/e² intensity diameter %.2f µm, "
              "overlap with the Gaussian %.4f" % (lam, V, u, w, neff, 2 * wm, 2 * r_e2, eta))
    n1, n2 = fibre_indices(1.55)
    print("fibre: n1 %.4f, n2 %.4f, NA %.4f, cut-off %.0f nm" % (n1, n2, np.sqrt(n1 ** 2 - n2 ** 2), 1e3 * 2 * np.pi * A_CORE * np.sqrt(n1 ** 2 - n2 ** 2) / 2.405))
    fig = plt.figure(figsize=(6.3, 2.9))
    # (a) end face, to scale, and a zoom into the core with a silicon wire at the same scale
    a = fig.add_axes([0.0, 0.0, 0.30, 1.0])
    frameless(a, xlim=(-130, 130), ylim=(-150, 140))
    a.add_patch(Circle((0, 0), 125, fc=MAT["polymer"], ec="none"))
    a.add_patch(Circle((0, 0), 62.5, fc=MAT["glass"], ec=MUTED, lw=0.5))
    a.add_patch(Circle((0, 0), A_CORE, fc=MAT["core"], ec="none"))
    label(a, 0, 98, "coating\nØ 250 µm", fs=6.5)
    label(a, 0, 34, "cladding\nØ 125 µm", fs=6.5)
    a.add_patch(Rectangle((-14, -14), 28, 28, fc="none", ec=INK, lw=0.6))
    label(a, 0, -142, "core Ø %.1f µm (box: zoom)" % (2 * A_CORE), fs=6.5)
    scalebar(a, -55, -112, 50, "50 µm")
    panel(a, "a", 0.02, 0.99)
    z = fig.add_axes([0.30, 0.12, 0.27, 0.82])
    frameless(z, xlim=(-14, 14), ylim=(-14, 14))
    z.add_patch(Rectangle((-14, -14), 28, 28, fc=MAT["glass"], ec=INK, lw=0.6))
    rr = np.linspace(-14, 14, 400); XX, YY = np.meshgrid(rr, rr)
    r1 = np.linspace(0, 20, 801)
    I = np.interp(np.hypot(XX, YY), r1, lp01_field(r1, 1.55)) ** 2
    rgba = np.zeros(I.shape + (4,)); rgba[..., :3] = matplotlib.colors.to_rgb(BLUE); rgba[..., 3] = 0.85 * I
    z.imshow(rgba, extent=(-14, 14, -14, 14), origin="lower", zorder=1)
    z.add_patch(Circle((0, 0), A_CORE, fc="none", ec=AMBER, lw=1.2, zorder=3))
    for (lam, V, u, w, neff, wm, re2, eta), ls in zip(rows, ((0, (2, 2)), "-")):
        z.add_patch(Circle((0, 0), wm, fc="none", ec=INK, lw=0.9, ls=ls, zorder=3))
    label(z, 0, 12.6, "MFD %.1f µm at 1550 nm (solid)" % (2 * rows[1][5]), fs=6.3, va="top")
    label(z, 0, 10.4, "MFD %.1f µm at 1310 nm (dashed)" % (2 * rows[0][5]), fs=6.3, va="top")
    label(z, 4.2, -4.6, "core", fs=6.3, col=AMBER, ha="left")
    # a 500 x 220 nm silicon wire at the same scale
    z.add_patch(Rectangle((9.75, -9.11), 0.5, 0.22, fc=MAT["si"], ec=INK, lw=0.4, zorder=4))
    callout(z, (10.0, -9.2), (10.0, -11.3), "Si wire\n500 × 220 nm", fs=6.0, ha="center", va="top")
    scalebar(z, -12.5, -12.6, 5, "5 µm")
    # (b) index and LP01 against radius
    b = fig.add_axes([0.665, 0.17, 0.32, 0.74])
    r = np.linspace(-15, 15, 1201)
    b.axvspan(-A_CORE, A_CORE, color=MAT["core"], alpha=0.5, lw=0)
    for (lam, V, u, w, neff, wm, re2, eta), col in zip(rows, (C3, C1)):
        b.plot(r, lp01_field(r, lam), color=col, label="LP$_{01}$, %d nm" % round(1e3 * lam))
        b.plot(r, np.exp(-r ** 2 / wm ** 2), color=col, lw=0.9, ls="--")
    b.text(0, 0.08, "core", ha="center", fontsize=6.5, color=AMBER)
    b.set_xlim(-15, 15); b.set_ylim(0, 1.08)
    finish(b, "Radius $r$ (µm)", "Field (normalised)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.3, handlelength=1.3, bbox_to_anchor=(1.03, 1.02))
    b.text(-14.5, 1.0, "dashed:\nGaussian\n(Marcuse)", fontsize=6.2, color=MUTED, va="top")
    tag(b, "b")
    save(fig, "ch03_fibre")
    return rows


# ------------------------------------------------------------------ Figure: loss and dispersion across the bands
def fig_bands():
    lam = np.linspace(1.24, 1.68, 221)
    neff = np.array([lp01(l)[3] for l in lam])
    h = lam[1] - lam[0]
    d2n = (neff[2:] - 2 * neff[1:-1] + neff[:-2]) / h ** 2          # 1/µm²
    D = -(lam[1:-1] * 1e-6 / 2.998e8) * d2n * 1e12 * 1e6              # s/m² -> ps/(nm km)
    nm = n_sio2(lam)
    d2m = (nm[2:] - 2 * nm[1:-1] + nm[:-2]) / h ** 2
    Dm = -(lam[1:-1] * 1e-6 / 2.998e8) * d2m * 1e12 * 1e6
    lc = lam[1:-1]
    z0 = lc[np.argmin(np.abs(D))]
    print("dispersion: D(1310) %.1f, D(1550) %.1f ps/(nm km); zero at %.0f nm; material only: D(1550) %.1f, zero at %.0f nm" %
          (np.interp(1.31, lc, D), np.interp(1.55, lc, D), 1e3 * z0, np.interp(1.55, lc, Dm), 1e3 * lc[np.argmin(np.abs(Dm))]))
    # loss: Rayleigh scattering (∝ λ^-4) plus a constant, through the chapter's 0.35 dB/km at 1310 and 0.2 dB/km at 1550 nm
    A = (0.35 - 0.20) / (1.31 ** -4 - 1.55 ** -4); B = 0.35 - A * 1.31 ** -4
    print("loss model: %.3f dB/km·µm^4 / λ^4 + %.3f dB/km; at 1310 %.2f, 1550 %.2f, 1625 %.2f dB/km" %
          (A, B, A / 1.31 ** 4 + B, A / 1.55 ** 4 + B, A / 1.625 ** 4 + B))
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.3, 3.5), sharex=True)
    BANDS = [("O", 1260, 1360), ("E", 1360, 1460), ("S", 1460, 1530), ("C", 1530, 1565), ("L", 1565, 1625)]
    cols = [C3, C5, MUTED, C1, C2]
    for ax in (a, b):
        for (n_, l0, l1), col in zip(BANDS, cols):
            ax.axvspan(l0, l1, color=col, alpha=0.13, lw=0)
    for (n_, l0, l1), col in zip(BANDS, cols):
        a.text((l0 + l1) / 2, 0.47, n_, ha="center", va="top", fontsize=8, fontweight="bold", color=INK)
    ll = np.linspace(1260, 1625, 300)
    a.plot(ll, A / (ll / 1e3) ** 4 + B, color=C1)
    a.plot([1310, 1550], [0.35, 0.20], "o", color=INK, ms=4)
    a.text(1316, 0.36, "0.35 dB/km", fontsize=6.8, va="bottom")
    a.text(1556, 0.21, "0.2 dB/km", fontsize=6.8, va="bottom")
    a.set_ylim(0, 0.5); a.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    finish(a, None, "Loss (dB/km)")
    tag(a, "a")
    b.plot(1e3 * lc, D, color=C4, label="fibre (material + waveguide)")
    b.plot(1e3 * lc, Dm, color=C4, lw=1.0, ls="--", label="silica alone")
    b.axhline(0, color=INK, lw=0.6)
    b.plot([1e3 * z0], [0], "o", color=INK, ms=4)
    b.annotate("zero near %.0f nm" % (1e3 * z0), (1e3 * z0, 0), xytext=(1345, -13), fontsize=6.8,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    d155 = np.interp(1.55, lc, D)
    b.plot([1550], [d155], "o", color=INK, ms=4)
    b.annotate("%.1f ps/(nm·km)" % d155, (1550, d155), xytext=(1440, 21), fontsize=6.8,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xlim(1260, 1625); b.set_ylim(-20, 30)
    finish(b, "Wavelength (nm)", "Dispersion $D$ (ps/(nm·km))", legend=True, loc="lower right")
    b.legend(loc="lower right", fontsize=6.6)
    tag(b, "b")
    fig.tight_layout(h_pad=0.6)
    save(fig, "ch03_bands")


if __name__ == "__main__":
    fig_beam(); fig_lens(); fig_fibre(); fig_bands()
