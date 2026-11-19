"""Figures for Chapter 9 (coupled modes and directional couplers), placed after the existing Figure 9.1.
Run from the worktree root: python -I -X utf8 figsrc/ch09_figs.py   (set FIGPREVIEW for PNG previews)

Numbers: femwell supermodes of two 500 x 220 nm strips (figsrc/ch09_supermodes.json: L_x = 37.8 um at a 200 nm gap,
x2.4 per 100 nm, i.e. dn = 0.0205 exp(-8.75 (g - 0.2)) as in figsrc/part3_figs.py and the dc demo), and the fields
of figsrc/ch09_fields.py -> ch09_fields.json (femwell, run in the photonics-labs container).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
LAM, W, T, G0 = 1.55, 0.5, 0.22, 0.2
DN0, GAM = 0.0205, 8.75                       # fit of the femwell supermode splitting against gap (Figure 9.1a)
LX = LAM / (2 * DN0)                          # 37.8 um
LB_TEXT = 2.5                                 # extra effective length of the bends assumed in the text


def lb_of_bend(H, Ls, n=4001):
    """Effective coupling length of one raised-cosine S-bend (lateral offset H of each guide, length Ls): the local
    coupling exp(-GAM (g(z) - G0)) integrated along it, with g(z) = G0 + 2 y(z)."""
    s = np.linspace(0, Ls, n); y = H * (1 - np.cos(np.pi * s / Ls)) / 2
    return np.trapezoid(np.exp(-GAM * 2 * y), s)


def design_bends(H=2.0):
    """S-bend length that makes the two bends together add LB_TEXT of coupling length."""
    lo, hi = 1.0, 60.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if 2 * lb_of_bend(H, mid) < LB_TEXT: lo = mid
        else: hi = mid
    Ls = (lo + hi) / 2
    return Ls, 2 * Ls ** 2 / (np.pi ** 2 * H)


# ---------------------------------------------------------------------------------------------- 9.3 the 3 dB coupler to scale
def fig_topview():
    H = 2.0
    Ls, Rmin = design_bends(H)
    L50 = LX / 2 - LB_TEXT
    print(f"L_x = {LX:.2f} um; 3 dB straight section L = L_x/2 - L_b = {L50:.2f} um")
    print(f"S-bends: raised cosine, offset {H} um per guide, length {Ls:.2f} um, min radius {Rmin:.1f} um; each adds "
          f"{lb_of_bend(H, Ls):.3f} um, both {2*lb_of_bend(H, Ls):.3f} um")
    for Hh in (1.5, 2.5):
        L2, R2 = design_bends(Hh); print(f"  (offset {Hh} um would need {L2:.1f} um bends, R_min {R2:.1f} um)")
    Lst = 3.0
    z0, z1, z2, z3 = Lst, Lst + Ls, Lst + Ls + L50, Lst + 2 * Ls + L50
    zt = z3 + Lst
    yc = (G0 + W) / 2                              # guide centre offset in the coupling section (0.35 um)
    Dx, ylo, yhi = (-2.5, zt + 6.5), -3.6, 3.4
    wfig = 6.3; axw = 1.0
    hin = wfig * axw * (yhi - ylo) / (Dx[1] - Dx[0])
    fig = plt.figure(figsize=(wfig, hin + 1.55))
    ax = fig.add_axes([0.0, 1.55 / (hin + 1.55), axw, hin / (hin + 1.55)])
    frameless(ax, Dx, (ylo, yhi), equal=True)
    box(ax, 0, -yc - H - 0.9, zt, 2 * (yc + H + 0.9), "ox", z=0)
    for sg in (1, -1):
        wg_straight(ax, 0, z0, sg * (yc + H), W)
        xs, ys = sbend_xy(z0, sg * (yc + H), Ls, -sg * H); ribbon(ax, xs, ys, W, "si")
        wg_straight(ax, z1, z2, sg * yc, W)
        xs, ys = sbend_xy(z2, sg * yc, Ls, sg * H); ribbon(ax, xs, ys, W, "si")
        wg_straight(ax, z3, zt, sg * (yc + H), W)
    label(ax, -0.3, yc + H, "in", ha="right", fs=7)
    label(ax, zt + 0.3, yc + H, "through 50 %", ha="left", fs=7, col=AMBER)
    label(ax, zt + 0.3, -yc - H, "cross 50 %", ha="left", fs=7, col=BLUE)
    dim(ax, (z1, -yc - 0.75), (z2, -yc - 0.75), f"L = {L50:.1f} µm", fs=6.5, text_off=(0, -0.42))
    dim(ax, (z0, yc + H + 0.62), (z1, yc + H + 0.62), f"S-bend {Ls:.1f} µm", fs=6.5, text_off=(0, 0.42))
    dim(ax, (z3 - 0.6, yc), (z3 - 0.6, yc + H), "", fs=6.3)
    label(ax, z3 - 0.25, yc + H / 2 - 0.15, f"offset {H:.0f} µm", ha="left", fs=6.5)
    callout(ax, ((z1 + z2) / 2 - 2.0, 0.0), ((z1 + z2) / 2 - 2.0, 1.55), "gap 200 nm, guides 500 nm wide", fs=6.5, ha="center", va="bottom")
    scalebar(ax, zt - 5.0, ylo + 0.25, 5.0, "5 µm")
    ax.text(zt - 5.6, ylo + 0.3, "to scale", ha="right", va="bottom", fontsize=6.0, color=MUTED, style="italic")
    panel(ax, "a", x=0.0, y=1.0)
    # b: local coupling strength along the device
    b = fig.add_axes([(0 - Dx[0]) / (Dx[1] - Dx[0]) * axw, 0.34 / (hin + 1.55), (zt - 0) / (Dx[1] - Dx[0]) * axw, 1.05 / (hin + 1.55)])
    z = np.linspace(0, zt, 3001)
    g = np.full_like(z, np.inf)
    s1 = (z >= z0) & (z < z1); g[s1] = G0 + 2 * H * (1 - np.cos(np.pi * (z1 - z[s1]) / Ls)) / 2
    g[(z >= z1) & (z <= z2)] = G0
    s3 = (z > z2) & (z <= z3); g[s3] = G0 + 2 * H * (1 - np.cos(np.pi * (z[s3] - z2) / Ls)) / 2
    k = np.exp(-GAM * (g - G0))
    b.fill_between(z, 0, k, where=(z >= z1) & (z <= z2), color=C1, alpha=0.35, lw=0)
    b.fill_between(z, 0, k, where=((z <= z1) | (z >= z2)), color=C2, alpha=0.45, lw=0)
    b.plot(z, k, color=INK, lw=1.0)
    b.set_xlim(0, zt); b.set_ylim(0, 1.25); b.set_yticks([0, 1])
    b.set_xlabel("z (µm)", labelpad=1)
    b.set_ylabel("Δn / Δn$_0$", labelpad=2)
    lb1 = lb_of_bend(H, Ls)
    b.text(z1 - 3.2, 0.5, f"bend adds\n{lb1:.2f} µm", ha="right", va="center", fontsize=6.5, color=INK)
    b.text(z2 + 3.2, 0.5, f"bend adds\n{lb1:.2f} µm", ha="left", va="center", fontsize=6.5, color=INK)
    b.text((z1 + z2) / 2, 0.5, f"straight section {L50:.1f} µm", ha="center", va="center", fontsize=6.5, color=INK)
    tag(b, "b")
    save(fig, "ch09_dc_topview")


# ---------------------------------------------------------------------------------------------- 9.2 the supermodes (femwell)
def load_fields():
    return json.load(open(os.path.join(HERE, "ch09_fields.json")))


N_SI, N_OX = 3.4757, 1.444                       # at 1550 nm (femwell_modes.py)


def to_D(xs, line, cores):
    """D_x = n^2 E_x along the mid-height line (cores = [(x_left, x_right), ...]), renormalised to unit integral of
    D_x^2. E_x jumps by (n_Si/n_ox)^2 at the side walls; D_x is continuous there, so it draws cleanly. The samples
    within 5 nm of a wall (where the probe may fall on either side) are interpolated."""
    xs, f = np.asarray(xs), np.asarray(line, float)
    inside = np.zeros_like(xs, bool); near = np.zeros_like(xs, bool)
    for a, b in cores:
        inside |= (xs > a) & (xs < b)
        near |= (np.abs(xs - a) < 0.005) | (np.abs(xs - b) < 0.005)
    D = f * np.where(inside, N_SI ** 2, N_OX ** 2)
    D[near] = np.interp(xs[near], xs[~near], D[~near])
    return D / np.sqrt(np.trapezoid(D ** 2, xs))


def fig_supermodes():
    F = load_fields()
    S = json.load(open(os.path.join(HERE, "ch09_supermodes.json")))
    k = [i for i, (g, l) in enumerate(zip(S["gap"], S["lam"])) if abs(g - G0) < 1e-9 and abs(l - LAM) < 1e-9][0]
    ne, no = S["n_even"][k], S["n_odd"][k]
    print(f"Figure 9.1 data at 200 nm: n_even {ne:.4f}, n_odd {no:.4f}, L_x {LAM/(2*(ne-no)):.2f} um;"
          f" this field run (35 nm mesh): n_even {F['sym']['n_even']:.4f}, n_odd {F['sym']['n_odd']:.4f}, L_x {F['sym']['Lx']:.2f} um;"
          f" imaginary part of the line cuts {F['sym']['even']['imag_frac']:.1e} / {F['sym']['odd']['imag_frac']:.1e}")
    if "tm" in F:
        print(f"TM pair at 200 nm: n_even {F['tm']['n_even']:.4f}, n_odd {F['tm']['n_odd']:.4f}, L_x {F['tm']['Lx']:.2f} um")
    gx0, gx1, nx = F["grid"]["x"]; gy0, gy1, ny = F["grid"]["y"]
    fig = plt.figure(figsize=(6.3, 4.0))
    xs = np.array(F["xl"])
    for i, (key, name, n) in enumerate((("even", "even", ne), ("odd", "odd", no))):
        ax = fig.add_axes([0.005 + 0.5 * i, 0.555, 0.49, 0.40])
        M = np.array(F["sym"][key]["map"], float).reshape(int(ny), int(nx)) / 99
        ax.imshow(M, origin="lower", extent=(gx0, gx1, gy0, gy1), cmap=SIGNED_CMAP, vmin=-1, vmax=1, interpolation="bilinear")
        for x0 in (-G0 / 2 - W, G0 / 2):
            ax.add_patch(Rectangle((x0, 0), W, T, fc="none", ec=INK, lw=0.7))
        ax.set_xlim(gx0, gx1); ax.set_ylim(gy0, gy1); ax.set_aspect("equal"); ax.set_axis_off()
        ax.text(gx0 + 0.05, gy1 - 0.05, f"{name} supermode, $n_\\mathrm{{eff}}$ = {n:.4f}", ha="left", va="top", fontsize=7, color=INK)
        panel(ax, "ab"[i], x=-0.0, y=1.12)
        if i == 1:
            ax.plot([1.0, 1.5], [gy0 + 0.07] * 2, color=INK, lw=1.4, solid_capstyle="butt")
            ax.text(1.25, gy0 + 0.1, "500 nm", ha="center", va="bottom", fontsize=6.3, color=INK)
            ax.text(gx1 - 0.03, gy0 + 0.30, "$E_x$, to scale", ha="right", va="bottom", fontsize=6.0, color=MUTED, style="italic")
    # c: line cuts through the strips' mid-height
    pair = [(-G0 / 2 - W, -G0 / 2), (G0 / 2, G0 / 2 + W)]
    e, o = to_D(xs, F["sym"]["even"]["line"], pair), to_D(xs, F["sym"]["odd"]["line"], pair)
    c = fig.add_axes([0.075, 0.1, 0.40, 0.36])
    d = fig.add_axes([0.585, 0.1, 0.40, 0.36])
    for ax in (c, d):
        for x0 in (-G0 / 2 - W, G0 / 2):
            ax.axvspan(x0, x0 + W, color=MAT["si"], alpha=0.35, lw=0, zorder=0)
        ax.set_xlim(-1.4, 1.4); ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    c.plot(xs, e / np.abs(e).max(), color=C1, label="even")
    c.plot(xs, o / np.abs(o).max(), color=C2, label="odd")
    c.axhline(0, color=MUTED, lw=0.6)
    c.set_ylim(-1.15, 1.5)
    finish(c, "x (µm)", "$D_x$ at mid-height (norm.)")
    c.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.03))
    tag(c, "c")
    # d: launch in the left guide = (even + odd)/sqrt 2, and the field after L_x/2 and L_x
    Lx = LAM / (2 * (ne - no))
    sc = np.max(np.abs(e + o) ** 2) / 2
    for zf, lab, col in ((0.0, "z = 0", C1), (0.5, f"z = $L_x$/2 = {Lx/2:.1f} µm", C3), (1.0, f"z = $L_x$ = {Lx:.1f} µm", C2)):
        f = (e + o * np.exp(1j * np.pi * zf)) / np.sqrt(2)
        I = np.abs(f) ** 2 / sc
        d.plot(xs, I, color=col, label=lab, lw=1.5 if zf != 0.5 else 1.3)
        left = np.trapezoid(I[xs < 0], xs[xs < 0]) / np.trapezoid(I, xs)
        print(f"  z = {zf} L_x: fraction of |D_x|^2 in the left half {100*left:.1f} %")
    d.set_ylim(0, 1.75)
    finish(d, "x (µm)", "$|D_x|^2$ at mid-height (norm.)")
    d.legend(loc="upper center", fontsize=6.6, ncol=1, bbox_to_anchor=(0.5, 1.05), handlelength=1.6)
    tag(d, "d")
    save(fig, "ch09_supermode_fields")


# ---------------------------------------------------------------------------------------------- 9.5 adiabatic coupler
def fig_adiabatic():
    F = load_fields()
    A = F["asym"]
    xs = np.array(F["xl"])
    fig = plt.figure(figsize=(6.3, 3.5))
    # a: top view, not to scale (transverse x 10, length compressed)
    a = fig.add_axes([0.0, 0.55, 1.0, 0.45]); frameless(a, (-14, 262), (-36, 30), equal=False)
    VS = 10.0
    z1, z2, z3 = 20.0, 220.0, 240.0                # S-bends in, adiabatic taper (illustrative 200 um), S-bends out
    Hs = 1.6                                       # S-bend offset of each guide (um)
    box(a, -12, -32, 270, 58, "ox", z=0)
    def guide(xs_, ys_, ws_):
        xs_, ys_, ws_ = map(np.asarray, (xs_, ys_, ws_))
        dx_, dy_ = np.gradient(xs_), np.gradient(ys_); L_ = np.hypot(dx_, dy_); nx_, ny_ = -dy_ / L_, dx_ / L_
        top = np.c_[xs_ + nx_ * ws_ / 2, ys_ + ny_ * ws_ / 2]; bot = np.c_[xs_ - nx_ * ws_ / 2, ys_ - ny_ * ws_ / 2]
        poly(a, np.vstack([top, bot[::-1]]), "si", z=2)
    w_n0, w_w0 = A[0]["w1"], A[0]["w2"]
    zz = np.linspace(-10, 250, 1200)
    off = np.select([zz < 0, zz < z1, zz < z2, zz < z3],
                    [Hs, Hs * (1 + np.cos(np.pi * zz / z1)) / 2, 0.0, Hs * (1 - np.cos(np.pi * (zz - z2) / (z3 - z2))) / 2], Hs)
    for sgn, w0 in ((1, w_w0), (-1, w_n0)):              # wide guide on top (x > 0), narrow below
        wz = np.where(zz < z1, w0, np.where(zz < z2, w0 + (0.5 - w0) * (zz - z1) / (z2 - z1), 0.5))
        guide(zz, sgn * (G0 / 2 + wz / 2 + off) * VS, wz * VS)
    zs = [z1 + (z2 - z1) * (1 - (r["w2"] - r["w1"]) / (w_w0 - w_n0)) for r in A]
    for i, (zc, r) in enumerate(zip(zs, A)):
        a.plot([zc, zc], [-27, 21], color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=3)
        a.text(zc, 22, str(i + 1), ha="center", va="bottom", fontsize=7, color=INK, fontweight="bold")
    a.text(-12.5, (G0 / 2 + w_w0 / 2 + Hs) * VS, f"wide, {1000*w_w0:.0f} nm", ha="right", va="center", fontsize=6.5, color=INK)
    a.text(-12.5, -(G0 / 2 + w_n0 / 2 + Hs) * VS, f"narrow, {1000*w_n0:.0f} nm", ha="right", va="center", fontsize=6.5, color=INK)
    a.text(250.5, (G0 / 2 + 0.25 + Hs) * VS, "50 %", ha="left", va="center", fontsize=6.8, color=INK)
    a.text(250.5, -(G0 / 2 + 0.25 + Hs) * VS, "50 %", ha="left", va="center", fontsize=6.8, color=INK)
    a.annotate("", xy=(z2, -30), xytext=(z1, -30), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    a.text((z1 + z2) / 2, -30, "widths taper slowly to 500 nm, gap 200 nm (hundreds of µm)", ha="center", va="center", fontsize=6.5, color=INK,
           bbox=dict(boxstyle="square,pad=0.1", fc=MAT["ox"], ec="none"))
    note(a, "not to scale: transverse × 10, length compressed", loc="upper right")
    panel(a, "a", x=0.0, y=1.0)
    # b: the two supermodes at the four stations
    for i, r in enumerate(A):
        ax = fig.add_axes([0.065 + 0.237 * i, 0.10, 0.20, 0.33])
        ax.axvspan(-G0 / 2 - r["w1"], -G0 / 2, color=MAT["si"], alpha=0.4, lw=0, zorder=0)
        ax.axvspan(G0 / 2, G0 / 2 + r["w2"], color=MAT["si"], alpha=0.4, lw=0, zorder=0)
        cores = [(-G0 / 2 - r["w1"], -G0 / 2), (G0 / 2, G0 / 2 + r["w2"])]
        m1, m2 = to_D(xs, r["m1"]["line"], cores), to_D(xs, r["m2"]["line"], cores)
        m1 = m1 / np.abs(m1).max() * np.sign(m1[np.argmax(np.abs(m1))])
        j = np.argmin(np.abs(xs - (G0 / 2 + r["w2"] / 2)))
        m2 = m2 / np.abs(m2).max(); m2 = m2 if m2[j] >= 0 else -m2
        ax.plot(xs, m1, color=C1, lw=1.3)
        ax.plot(xs, m2, color=C2, lw=1.3)
        ax.axhline(0, color=MUTED, lw=0.5)
        ax.set_xlim(-0.9, 0.9); ax.set_ylim(-1.15, 1.25); ax.set_xticks([-0.5, 0, 0.5]); ax.set_yticks([])
        ax.spines["left"].set_visible(False); ax.grid(False)
        ax.set_title(f"{i+1}: {1000*r['w1']:.0f} / {1000*r['w2']:.0f} nm", fontsize=6.8, color=INK, pad=3)
        if i == 0:
            ax.set_xlabel("x (µm)", labelpad=1)
            tag(ax, "b")
        print(f"station {i+1}: widths {r['w1']:.2f}/{r['w2']:.2f} um, n_eff {r['n1']:.4f} / {r['n2']:.4f}")
    fig.text(0.99, 0.005, "blue: mode 1 (higher $n_\\mathrm{eff}$); amber: mode 2", ha="right", va="bottom", fontsize=6.5, color=INK)
    save(fig, "ch09_adiabatic")


# ---------------------------------------------------------------------------------------------- 9.6 the 2 x 2 matrix and its -j
def fig_smatrix():
    fig = plt.figure(figsize=(6.3, 2.7))
    a = fig.add_axes([0.0, 0.0, 0.52, 1.0]); frameless(a, (-2.5, 21.5), (-6.8, 6.6), equal=False)
    yU, yL = 2.6, -2.6
    for sg, y in ((1, yU), (-1, yL)):
        wg_straight(a, 0, 3.5, y, 0.45)
        xs, ys = sbend_xy(3.5, y, 3.5, -sg * 2.2); ribbon(a, xs, ys, 0.45, "si")
        wg_straight(a, 7.0, 12.0, sg * 0.4, 0.45)
        xs, ys = sbend_xy(12.0, sg * 0.4, 3.5, sg * 2.2); ribbon(a, xs, ys, 0.45, "si")
        wg_straight(a, 15.5, 19.0, y, 0.45)
    for x, y, s in ((-0.3, yU, "$a_1$"), (-0.3, yL, "$a_2$")):
        label(a, x, y, s, ha="right", fs=9)
    for x, y, s in ((19.3, yU, "$b_1$"), (19.3, yL, "$b_2$")):
        label(a, x, y, s, ha="left", fs=9)
    arrow(a, (1.0, yU + 1.6), (18.0, yU + 1.6), col=AMBER, lw=1.1, ms=8)
    label(a, 9.5, yU + 2.2, "through:  $t$", fs=8, col=AMBER, va="bottom")
    arrow(a, (1.0, yU + 0.9), (18.0, yL - 0.9), col=BLUE, lw=1.1, ms=8, connectionstyle="arc3,rad=0.0")
    label(a, 0.3, 0.0, r"cross:  $-j\kappa$", fs=8, col=BLUE, ha="left", va="center")
    label(a, 9.5, -4.9, r"$b_1 = t\,a_1 - j\kappa\,a_2$", fs=8.5)
    label(a, 9.5, -6.3, r"$b_2 = -j\kappa\,a_1 + t\,a_2$", fs=8.5)
    note(a, "not to scale", loc="upper right")
    panel(a, "a", x=0.0, y=1.0)
    # b: total output power for two equal inputs with relative phase theta
    b = fig.add_axes([0.62, 0.17, 0.36, 0.72])
    th = np.linspace(0, 2 * np.pi, 361)
    k = t = np.sqrt(0.5)
    a1, a2 = np.full_like(th, 1 / np.sqrt(2), dtype=complex), np.exp(1j * th) / np.sqrt(2)
    tot_j = np.abs(t * a1 - 1j * k * a2) ** 2 + np.abs(-1j * k * a1 + t * a2) ** 2
    tot_r = np.abs(t * a1 + k * a2) ** 2 + np.abs(k * a1 + t * a2) ** 2
    print(f"total output power, 50/50: with -j {tot_j.min():.3f}..{tot_j.max():.3f}; with a real cross term {tot_r.min():.3f}..{tot_r.max():.3f}")
    b.plot(th / np.pi, tot_r, color=C4, lw=1.4, ls=(0, (4, 2)), label=r"cross term $+\kappa$ (real)")
    b.plot(th / np.pi, tot_j, color=C1, lw=1.8, label=r"cross term $-j\kappa$")
    b.fill_between(th / np.pi, 1, tot_r, where=tot_r > 1, color=C4, alpha=0.12, lw=0)
    b.fill_between(th / np.pi, tot_r, 1, where=tot_r < 1, color=C4, alpha=0.12, lw=0)
    b.text(0.18, 1.62, "power created", fontsize=6.5, color=C4)
    b.text(0.72, 0.30, "power lost", fontsize=6.5, color=C4)
    b.set_xlim(0, 2); b.set_ylim(0, 2.45); b.set_xticks([0, 0.5, 1, 1.5, 2]); b.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
    finish(b, r"Relative phase of the inputs, $\arg(a_2/a_1)$", "Total output power")
    b.legend(loc="upper right", fontsize=6.6, bbox_to_anchor=(1.02, 1.04))
    tag(b, "b")
    save(fig, "ch09_smatrix")


if __name__ == "__main__":
    which = sys.argv[1:] or ["topview", "smatrix", "supermodes", "adiabatic"]
    if "topview" in which: fig_topview()
    if "smatrix" in which: fig_smatrix()
    if os.path.exists(os.path.join(HERE, "ch09_fields.json")):
        if "supermodes" in which: fig_supermodes()
        if "adiabatic" in which: fig_adiabatic()
