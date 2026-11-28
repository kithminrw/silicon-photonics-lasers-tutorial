"""Figures for Chapter 7 (loss, dispersion and nonlinearity). Run from the worktree root:
    python -I -X utf8 figsrc/ch07_figs.py
Writes assets/figs/ch07_mechanisms.svg, ch07_scattering.svg, ch07_fca.svg, ch07_leakage.svg, ch07_tpa.svg and
prints every number used in the figures and captions. The mechanisms drawing uses the femwell TE0 field of the
500 x 220 nm strip from figsrc/ch06_fields.json.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from part2_figs import slab_modes

N_SI, N_OX, LAM = 3.476, 1.444, 1.55
HERE = os.path.dirname(os.path.abspath(__file__))


def nsi(l):
    l1 = 1.1071; return np.sqrt(11.6858 + 0.939816 / l**2 + 0.00810461 * l1**2 / (l**2 - l1**2))


def nox(l):
    return np.sqrt(1 + 0.6961663 * l**2 / (l**2 - 0.0684043**2) + 0.4079426 * l**2 / (l**2 - 0.1162414**2) + 0.8974794 * l**2 / (l**2 - 9.896161**2))


# ------------------------------------------------------------------ Figure: loss mechanisms
def fig_mechanisms():
    p = os.path.join(HERE, "ch06_fields.json")
    if os.path.exists(p):                                   # femwell TE0 of the strip
        S = json.load(open(p))
        gx = np.linspace(*S["grid"]["x"]); gy = np.linspace(*S["grid"]["y"])
        I = np.array(S["strip"]["te"]["I"], float).reshape(len(gy), len(gx)) / 999
        print("[mechanisms] contours from the femwell field (ch06_fields.json)")
    else:                                                   # fallback: separable effective-index field
        k0 = 2 * np.pi / LAM
        nI = slab_modes(N_SI, N_OX, N_OX, 0.22, LAM)[0]; ne = slab_modes(nI, N_OX, N_OX, 0.5, LAM, tm=True)[0]
        kv, gv = k0 * np.sqrt(N_SI**2 - nI**2), k0 * np.sqrt(nI**2 - N_OX**2)
        kl, gl = k0 * np.sqrt(nI**2 - ne**2), k0 * np.sqrt(ne**2 - N_OX**2)
        gx = np.linspace(-1, 1, 161); gy = np.linspace(-0.6, 0.82, 115)
        yc = gy - 0.11
        fy = np.where(np.abs(yc) <= 0.11, np.cos(kv * yc), np.cos(kv * 0.11) * np.exp(-gv * (np.abs(yc) - 0.11)))
        fx = np.where(np.abs(gx) <= 0.25, np.cos(kl * gx), np.cos(kl * 0.25) * np.exp(-gl * (np.abs(gx) - 0.25)))
        I = np.outer(fy**2, fx**2); I /= I.max()
        print("[mechanisms] contours from the separable effective-index field (no ch06_fields.json)")
    fig = plt.figure(figsize=(6.3, 3.2))
    # (a) cross-section, schematic: core and mode enlarged 3x (same factor in x and y), BOX shortened
    s = 3.0
    ax = fig.add_axes([0.0, 0.0, 0.49, 0.98]); frameless(ax, (-3.0, 3.0), (-3.3, 3.0))
    box(ax, -3.0, -3.3, 6.0, 0.5, "sub"); box(ax, -3.0, -2.8, 6.0, 2.8, "ox"); box(ax, -3.0, 0, 6.0, 3.0, "oxtop")
    for yb in (-2.05, -2.2):                                   # break marks: the BOX is drawn shortened
        xz = np.linspace(-3.0, 3.0, 41); ax.plot(xz, yb + 0.05 * (-1.0) ** np.arange(41), color=MUTED, lw=0.6, zorder=2)
    rng = np.random.default_rng(3)
    ys = np.linspace(0, 0.22 * s, 14)
    left = -0.25 * s + 0.05 * rng.standard_normal(len(ys)); right = 0.25 * s + 0.05 * rng.standard_normal(len(ys))
    left[0] = left[-1] = -0.25 * s; right[0] = right[-1] = 0.25 * s
    poly(ax, np.vstack([np.c_[right, ys], np.c_[left[::-1], ys[::-1]]]), "si", z=2)
    ax.contour(gx * s, gy * s, I, levels=[0.05, 0.25, 0.5, 0.8], colors=[RED], linewidths=[0.5, 0.6, 0.7, 0.8], alpha=0.9, zorder=3)
    box(ax, -1.4, 2.3, 2.8, 0.22, "tin", z=2)
    label(ax, 0, 2.62, "heater / metal", fs=6.5, va="bottom")
    yc = 0.11 * s
    for sgn in (-1, 1):
        for ang in (30, 0, -30):
            a_ = np.radians(ang); x0 = sgn * (0.25 * s + 0.08)
            arrow(ax, (x0, yc), (x0 + sgn * 0.75 * np.cos(a_), yc + 0.75 * np.sin(a_)), col=AMBER, lw=0.9, ms=6)
    label(ax, 1.75, 1.0, "sidewall\nscattering", fs=6.5, ha="left")
    arrow(ax, (0, -0.95), (0, -3.05), col=BLUE, lw=1.1, ms=7, ls=(0, (3, 2)))
    label(ax, 0.12, -1.0, "tail tunnels through\nthe BOX into the\nsubstrate: leakage", fs=6.5, ha="left", va="top")
    arrow(ax, (0, 1.75), (0, 2.25), col=VIOLET, lw=1.0, ms=6, ls=(0, (3, 2)))
    label(ax, 0.12, 1.95, "absorption where the tail\nmeets metal or doped Si", fs=6.5, ha="left", va="center")
    callout(ax, (-0.35, 0.25), (-2.85, -0.55), "free carriers and TPA\nabsorb in the core", fs=6.3, ha="left", va="top")
    label(ax, -2.9, -3.05, "Si substrate", fs=6.5, ha="left", va="center")
    label(ax, -2.9, -2.45, "buried oxide", fs=6.5, ha="left", va="center")
    label(ax, -2.55, 2.9, "oxide cladding", fs=6.5, ha="left", va="top")
    note(ax, "not to scale", loc="lower right")
    panel(ax, "a", 0.0, 1.0)
    # (b) top view, to scale: a rough straight guide into a bend that radiates from its outer side
    bx = fig.add_axes([0.51, 0.0, 0.49, 0.98]); frameless(bx, (-0.3, 5.6), (-1.3, 4.9))
    box(bx, -0.3, -1.3, 5.9, 6.2, "oxtop", z=0)
    R, xc = 2.0, 2.0
    xs = np.linspace(-0.3, xc, 120)
    w = 0.5 + 0.15 * np.convolve(rng.standard_normal(140), np.ones(10) / 10, "same")[:120]
    poly(bx, np.vstack([np.c_[xs, w / 2], np.c_[xs[::-1], -w[::-1] / 2]]), "si", z=2)
    wg_arc(bx, xc, R, R, 0.5, -90.5, 0, "si")
    box(bx, xc + R - 0.25, R - 0.01, 0.5, 2.95, "si", z=2)
    for t in np.radians([-65, -42, -20]):
        p0 = (xc + (R + 0.32) * np.cos(t), R + (R + 0.32) * np.sin(t))
        d_ = (-np.sin(t), np.cos(t))
        p1 = (p0[0] + 0.35 * d_[0] + 0.5 * np.cos(t), p0[1] + 0.35 * d_[1] + 0.5 * np.sin(t))
        arrow(bx, p0, p1, col=RED, lw=0.9, ms=6)
    for xx in (0.3, 0.9, 1.5):
        arrow(bx, (xx, 0.33), (xx + 0.15, 0.9), col=AMBER, lw=0.8, ms=5)
        arrow(bx, (xx, -0.33), (xx + 0.15, -0.9), col=AMBER, lw=0.8, ms=5)
    arrow(bx, (-0.25, 0), (0.2, 0), col=INK, lw=0.9, ms=6)
    label(bx, 0.95, 1.15, "rough sidewalls scatter", fs=6.5)
    label(bx, 2.45, -0.8, "the bend radiates outward", fs=6.5, ha="left", va="top")
    scalebar(bx, 0.0, 4.2, 1.0, "1 µm")
    note(bx, "top view to scale; roughness exaggerated", loc="lower right")
    panel(bx, "b", 0.0, 1.0)
    save(fig, "ch07_mechanisms")


# ------------------------------------------------------------------ Figure: sidewall scattering (Payne-Lacey on the lateral slab)
def sym_slab_te(nc, ncl, W, lam):
    ne = slab_modes(nc, ncl, ncl, W, lam)[0]
    k0 = 2 * np.pi / lam
    ka, g = k0 * np.sqrt(nc**2 - ne**2), k0 * np.sqrt(ne**2 - ncl**2)
    return ne, ka, g


def edge_field2(nc, ncl, W, lam):
    """phi^2 at the sidewall for the TE0 mode of a symmetric slab, normalised to int phi^2 dx = 1 (units 1/um)."""
    ne, ka, g = sym_slab_te(nc, ncl, W, lam)
    a = W / 2
    norm = a + np.sin(2 * ka * a) / (2 * ka) + np.cos(ka * a)**2 / g          # int cos^2 inside + tails
    return ne, np.cos(ka * a)**2 / norm


def payne_lacey(nc, ncl, W, lam, Lc, sigma=1.0):
    """Payne-Lacey loss (arbitrary units) with an exponential autocorrelation: phi^2(d) (n1^2-n2^2)^2 k0^3/(4 pi n1) int R(beta - n2 k0 cos t) dt."""
    ne, p2 = edge_field2(nc, ncl, W, lam)
    k0 = 2 * np.pi / lam; beta = ne * k0
    t = np.linspace(0, np.pi, 2001)
    Rt = 2 * sigma**2 * Lc / (1 + Lc**2 * (beta - ncl * k0 * np.cos(t))**2)
    return p2 * (nc**2 - ncl**2)**2 * k0**3 / (4 * np.pi * nc) * np.trapezoid(Rt, t)


def fig_scattering():
    nI = slab_modes(N_SI, N_OX, N_OX, 0.22, LAM)[0]          # vertical slab of the core region (effective-index method)
    print(f"[scattering] lateral slab core index n_I = {nI:.4f}")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.15]))
    for W, col in ((0.5, C1), (1.0, C2), (2.0, C3)):
        ne, ka, g = sym_slab_te(nI, N_OX, W, LAM)
        x = np.linspace(-1.6, 1.6, 1601)
        E = np.where(np.abs(x) <= W / 2, np.cos(ka * x), np.cos(ka * W / 2) * np.exp(-g * (np.abs(x) - W / 2)))
        E2 = E**2 / np.trapezoid(E**2, x)
        a.plot(x, E2, color=col, label=f"W = {1000*W:.0f} nm")
        ys = np.cos(ka * W / 2)**2 / np.trapezoid(E**2, x)
        a.plot([-W / 2, W / 2], [ys, ys], "o", color=col, ms=4)
        print(f"[scattering] W {W}: n_eff(lateral TE slab) {ne:.4f}, sidewall |E|^2 {ys:.3f} /um")
    a.set_xlim(-1.6, 1.6); a.set_ylim(0, 3.6)
    a.text(-1.55, 3.4, "dots: field at\nthe sidewalls", ha="left", va="top", fontsize=6.5, color=MUTED)
    finish(a, "Lateral position (µm)", r"$|E|^2$ (unit power, µm$^{-1}$)", legend=True, loc="upper right")
    Ws = np.linspace(0.3, 3.0, 136)
    for Lc in (0.02, 0.05, 0.1):
        for W in (1.0, 2.0, 3.0):
            print(f"[scattering] Lc {1000*Lc:.0f} nm: loss(W={W})/loss(500 nm) = {payne_lacey(nI, N_OX, W, LAM, Lc)/payne_lacey(nI, N_OX, 0.5, LAM, Lc):.3f}")
    Lc = 0.05
    al = np.array([payne_lacey(nI, N_OX, W, LAM, Lc) for W in Ws])
    r = al / payne_lacey(nI, N_OX, 0.5, LAM, Lc)
    b.plot(Ws, r, color=C1, label=rf"Payne–Lacey, $L_c$ = 20–100 nm")
    es = np.array([edge_field2(nI, N_OX, W, LAM)[1] for W in Ws]) / edge_field2(nI, N_OX, 0.5, LAM)[1]
    b.plot(Ws, es, ":", color=MUTED, lw=1.2, label=r"$|E_s|^2$ alone")
    for W in (1.0, 2.0, 3.0):
        v = payne_lacey(nI, N_OX, W, LAM, Lc) / payne_lacey(nI, N_OX, 0.5, LAM, Lc)
        b.plot(W, v, "o", color=C1, ms=4)
        b.annotate(f"{v:.2f}" if v >= 0.1 else f"{v:.3f}", (W, v), xytext=(4, 5) if W < 2.9 else (-2, 10), textcoords="offset points", fontsize=7, color=C1, ha="left" if W < 2.9 else "right")
    b.axvline(0.5, color=MUTED, lw=0.6, ls=":")
    b.set_yscale("log"); b.set_xlim(0.3, 3.0); b.set_ylim(0.01, 2)
    b.set_yticks([0.01, 0.03, 0.1, 0.3, 1]); b.set_yticklabels(["0.01", "0.03", "0.1", "0.3", "1"])
    finish(b, "Strip width W (µm)", "Scattering loss / loss at 500 nm", legend=True, loc="upper right")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch07_scattering")
    # contrast factor
    print(f"[scattering] (n1^2-n2^2)^2 Si/SiO2 over SiN/SiO2: {(N_SI**2-N_OX**2)**2/(1.996**2-N_OX**2)**2:.1f}")


# ------------------------------------------------------------------ Figure: free-carrier absorption
def fig_fca():
    N = np.logspace(16, 20, 200)
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    ax.loglog(N, 4.343 * 8.5e-18 * N, color=C1, label=r"electrons, 8.5$\times$10$^{-18}$ N$_e$")
    ax.loglog(N, 4.343 * 6.0e-18 * N, color=C4, label=r"holes, 6.0$\times$10$^{-18}$ N$_h$")
    v = 4.343 * 6.0e-18 * 1e18
    ax.plot(1e18, v, "o", color=C4, ms=4)
    ax.annotate(f"{v:.0f} dB/cm", (1e18, v), xytext=(6, -12), textcoords="offset points", fontsize=7, color=C4)
    print(f"[fca] holes 1e18: {6.0e-18*1e18:.1f} /cm = {v:.1f} dB/cm; electrons 1e18: {4.343*8.5e-18*1e18:.1f} dB/cm; "
          f"1e20 holes: {4.343*6e-18*1e20:.0f} dB/cm; 1e16: {4.343*6e-18*1e16:.2f} dB/cm")
    ax.axvspan(1e19, 1e20, color=GRID, alpha=0.6, lw=0)
    ax.text(3.2e19, 0.15, "contacts\n(p$^{++}$, n$^{++}$)", fontsize=6.3, color=MUTED, ha="center", va="bottom")
    ax.axvspan(5e17, 1e18, color="#F6E7CC", alpha=0.8, lw=0)
    ax.text(7e17, 0.15, "modulator\ndoping", fontsize=6.3, color=MUTED, ha="center", va="bottom")
    ax.set_xlim(1e16, 1e20); ax.set_ylim(0.1, 1e4)
    finish(ax, r"Carrier density (cm$^{-3}$)", "Absorption (dB/cm)")
    ax.legend(loc="upper left", fontsize=6.3, frameon=True, framealpha=0.95, edgecolor="none")
    save(fig, "ch07_fca")


# ------------------------------------------------------------------ Figure: substrate leakage (1D leaky slab)
def equiv_film(neff_target, d, lam, tm):
    """Film index of a symmetric oxide-clad slab of thickness d whose fundamental mode has n_eff = neff_target."""
    no = nox(lam); lo, hi = neff_target, 4.0
    for _ in range(80):
        c = (lo + hi) / 2
        if slab_modes(c, no, no, d, lam, tm)[0] < neff_target: lo = c
        else: hi = c
    return (lo + hi) / 2


def leaky_neff(nf, d, t, lam, tm, ns, no, guess):
    """Complex n_eff of the leaky mode by Newton iteration. TM uses H_y with (1/n^2) dH/dx continuous."""
    k0 = 2 * np.pi / lam
    def D(ne):
        gc = np.sqrt((k0 * ne)**2 - k0**2 * no**2 + 0j)
        f, g = 1.0 + 0j, -gc / (no**2 if tm else 1.0)        # g = f'/n^2 (TM) or f' (TE), continuous across interfaces
        for n, h in ((nf, d), (no, t)):
            qq = np.sqrt(k0**2 * n**2 - (k0 * ne)**2 + 0j); w = n**2 if tm else 1.0
            fp = g * w
            f, fp = f * np.cos(qq * h) - fp / qq * np.sin(qq * h), f * qq * np.sin(qq * h) + fp * np.cos(qq * h)
            g = fp / w
        ks = np.sqrt(k0**2 * ns**2 - (k0 * ne)**2 + 0j)
        return g - 1j * ks / (ns**2 if tm else 1.0) * f       # substrate: f ~ exp(+i ks x) for x below the BOX (outgoing)
    ne = complex(guess)
    for _ in range(60):
        h = 1e-7
        dD = (D(ne + h) - D(ne - h)) / (2 * h)
        step = D(ne) / dD
        ne -= step
        if abs(step) < 1e-15: break
    return ne


def fig_leakage():
    d = 0.22
    cases = [("TE, 1550 nm", 1.55, False, 2.446, C1), ("TM, 1550 nm", 1.55, True, 1.771, C2), ("TE, 1310 nm", 1.31, False, 2.712, C3)]
    ts = np.linspace(0.4, 3.0, 53)
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.25]))
    for name, lam, tm, nt, col in cases:
        no, ns = nox(lam), nsi(lam)
        nf = equiv_film(nt, d, lam, tm)
        k0 = 2 * np.pi / lam; g = k0 * np.sqrt(nt**2 - no**2)
        al = []
        for t in ts:
            ne = leaky_neff(nf, d, t, lam, tm, ns, no, nt)
            al.append(4.343 * 2 * k0 * abs(ne.imag) * 1e4)          # dB/cm
        al = np.array(al)
        b.semilogy(ts, np.where(al > 1e-7, al, np.nan), color=col, label=name)      # below ~1e-8 dB/cm: rounding floor
        i2 = np.argmin(np.abs(ts - 2.0)); i3 = np.argmin(np.abs(ts - 3.0)); i1 = np.argmin(np.abs(ts - 1.0))
        slope = 10 * np.log10(al[np.argmin(np.abs(ts - 1.5))] / al[np.argmin(np.abs(ts - 1.6))])
        print(f"[leakage] {name}: equivalent film index {nf:.4f}, gamma {g:.2f}/um, e^-2gamma per 100 nm {8.686*g*0.1:.1f} dB; "
              f"computed slope {slope:.1f} dB/100 nm; loss at 1 um {al[i1]:.3g}, 2 um {al[i2]:.3g}, 3 um {al[i3]:.3g} dB/cm")
        # (a) vertical |E|^2 profile through the BOX, in dB, for a 2 um BOX
        x = np.linspace(-2.0, 0.8, 800)
        prof = np.where(x > d, np.exp(-2 * g * (x - d)), np.where(x >= 0, 1.0, np.exp(2 * g * x)))
        a.plot(10 * np.log10(prof), x, color=col, lw=1.4, label=name)
        vs = 10 * np.log10(np.exp(-2 * g * 2.0))
        a.plot(vs, -2.0, "o", color=col, ms=4, zorder=5)
        a.annotate(f"{vs:.0f} dB", (vs, -2.0), xytext=(3, -4), textcoords="offset points", fontsize=6.5, color=col, ha="left", va="top")
        print(f"[leakage] {name}: tail intensity at the substrate (2 um BOX) {vs:.0f} dB")
    a.axhspan(-2.3, -2.0, color=MAT["sub"], lw=0, zorder=0); a.axhspan(-2.0, 0, color=MAT["ox"], lw=0, zorder=0)
    a.axhspan(0, d, color=MAT["si"], lw=0, zorder=0); a.axhspan(d, 0.8, color=MAT["oxtop"], lw=0, zorder=0)
    a.text(-3, -2.43, "Si substrate", fontsize=6.5, va="center", ha="right"); a.text(-207, -1.0, "BOX 2 µm", fontsize=6.5, va="center")
    a.text(-207, 0.5, "oxide", fontsize=6.5, va="center"); a.text(-207, 0.11, "Si", fontsize=6.5, va="center")
    a.set_xlim(-210, 5); a.set_ylim(-2.55, 0.8); a.grid(False)
    a.axhspan(-2.55, -2.3, color=MAT["sub"], lw=0, zorder=0)
    finish(a, r"Tail intensity $|E|^2$ (dB)", "Height (µm)")
    b.axvline(2.0, color=MUTED, lw=0.6, ls=":")
    b.set_xlim(0.4, 3.0); b.set_ylim(1e-6, 1e3)
    b.set_yticks([1e-6, 1e-4, 1e-2, 1, 1e2])
    finish(b, "BOX thickness (µm)", "Substrate leakage (dB/cm)", legend=True, loc="upper right")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch07_leakage")


# ------------------------------------------------------------------ Figure: two-photon absorption
def fig_tpa():
    hv = 6.62607e-34 * 2.99792e8 / 1.55e-6          # J
    Aeff = 1e-9                                       # cm^2 (0.1 um^2)
    sig = 8.5e-18 + 6.0e-18                           # cm^2, one electron plus one hole
    P = np.logspace(-3, 0, 300)                       # W
    I = P / Aeff
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    for beta, ls in ((0.5e-9, ":"), (0.7e-9, "-"), (1.0e-9, ":")):
        a.loglog(P * 1e3, 4.343 * beta * I, ls, color=C1, lw=1.6 if ls == "-" else 1.0,
                 label=r"TPA, $\beta_\mathrm{TPA}$ = 0.7 cm/GW (0.5–1)" if ls == "-" else None)
    for tau, ls in ((1e-9, "-"), (1e-10, "--")):
        Nc = 0.7e-9 * I**2 * tau / (2 * hv)
        a.loglog(P * 1e3, 4.343 * sig * Nc, ls, color=C4, label=f"FCA from TPA, τ = {tau*1e9:g} ns")
    a.axhspan(1, 3, color=GRID, alpha=0.8, lw=0)
    a.text(1.3, 3.3, "linear loss of a Si strip, 1–3 dB/cm", fontsize=6.5, color=MUTED, va="bottom")   # above the band, clear of the FCA line
    i = np.argmin(np.abs(P - 0.1))
    print(f"[tpa] 100 mW: I = {I[i]:.2e} W/cm^2, alpha_TPA = {0.7e-9*I[i]:.3f} /cm = {4.343*0.7e-9*I[i]:.2f} dB/cm; "
          f"1 W: {4.343*0.7e-9*I[-1]:.1f} dB/cm")
    for tau in (1e-9, 1e-10):
        Nc = 0.7e-9 * I**2 * tau / (2 * hv)
        print(f"[tpa] FCA tau {tau*1e9:g} ns: N at 100 mW {Nc[i]:.2e} cm^-3 -> {4.343*sig*Nc[i]:.2f} dB/cm; at 1 W {4.343*sig*Nc[-1]:.0f} dB/cm")
    a.set_xlim(1, 1000); a.set_ylim(1e-3, 1e3)
    finish(a, "Power in the waveguide (mW)", "Loss (dB/cm)", legend=True, loc="upper left")
    a.legend(loc="upper left", fontsize=6.3)
    # (b) output against input for 1 cm, linear loss 2 dB/cm
    al0 = 2.0 / 4.343
    def out(Pin, beta, tau, L=1.0, n=2000):
        p = Pin; dz = L / n
        def f(p):
            Ii = p / Aeff; Nc = beta * Ii**2 * tau / (2 * hv)
            return -(al0 + beta * Ii + sig * Nc) * p
        for _ in range(n):
            k1 = f(p); k2 = f(p + dz / 2 * k1); k3 = f(p + dz / 2 * k2); k4 = f(p + dz * k3)
            p += dz / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        return p
    Pin = np.logspace(-3, 0.3, 120)
    b.loglog(Pin * 1e3, Pin * 10**(-0.2) * 1e3, color=MUTED, lw=1.2, label="linear loss only (2 dB)")
    b.loglog(Pin * 1e3, [1e3 * out(p, 0.7e-9, 0) for p in Pin], color=C1, label="+ TPA")
    for tau, ls in ((1e-9, "-"), (1e-10, "--")):
        po = np.array([out(p, 0.7e-9, tau) for p in Pin])
        b.loglog(Pin * 1e3, po * 1e3, ls, color=C4, label=f"+ TPA and FCA, τ = {tau*1e9:g} ns")
        print(f"[tpa] 1 cm, tau {tau*1e9:g} ns: max output {1e3*po.max():.0f} mW at input {1e3*Pin[po.argmax()]:.0f} mW; "
              f"out at 100 mW in {1e3*out(0.1, 0.7e-9, tau):.1f} mW, at 1 W in {1e3*out(1.0, 0.7e-9, tau):.1f} mW")
    print(f"[tpa] 1 cm, TPA only: out at 1 W in {1e3*out(1.0, 0.7e-9, 0):.0f} mW, at 100 mW {1e3*out(0.1, 0.7e-9, 0):.1f} mW")
    b.set_xlim(1, 2000); b.set_ylim(1, 2000)
    finish(b, "Input power (mW)", "Output after 1 cm (mW)", legend=True, loc="upper left")
    b.legend(loc="upper left", fontsize=6.3)
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch07_tpa")


# ------------------------------------------------------------------ Figure 7.6: frequency conversion and microcombs (Section 7.8)
def fig_nonlinear():
    """(a) Second-harmonic field growth along a waveguide: phase matched, not phase matched (coherence length L_c),
    and quasi-phase-matched by flipping the nonlinear coefficient every L_c (periodic poling). Undepleted pump,
    normalised so that the phase-matched power is z^2. (b) An illustrative soliton microcomb: lines one FSR
    (100 GHz) apart under a sech^2 envelope, with the pump line on top."""
    n_e1, n_e2 = 2.1379, 2.1748                    # bulk LiNbO3, extraordinary, at 1550 and 775 nm (approximate)
    Lam_bulk = 1.55 / (2 * (n_e2 - n_e1))
    print(f"Fig 7.6: bulk LN first-order QPM period for 1550 -> 775 nm: {Lam_bulk:.1f} um (coherence length {Lam_bulk / 2:.1f} um);"
          " thin-film waveguides need about 4 um (Wang et al. 2018)")
    Lc = 1.0                                        # lengths in units of the coherence length
    z = np.linspace(0, 8 * Lc, 4001); dz = z[1] - z[0]
    dk = np.pi / Lc
    E_pm = z
    E_np = np.abs(np.cumsum(np.exp(1j * dk * z)) * dz)
    sign = np.where(np.floor(z / Lc) % 2 == 0, 1.0, -1.0)
    E_qpm = np.abs(np.cumsum(sign * np.exp(1j * dk * z)) * dz)
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.15]))
    a.plot(z, E_pm ** 2, color=C3, lw=1.4, label="phase matched")
    a.plot(z, E_qpm ** 2, color=C1, lw=1.6, label="quasi-phase-matched (poled)")
    a.plot(z, (2 / np.pi) ** 2 * z ** 2, color=C1, lw=0.8, ls=(0, (2, 2)))
    a.plot(z, E_np ** 2, color=C2, lw=1.4, label="not phase matched")
    for k in range(1, 8):
        a.axvline(k * Lc, color=GRID, lw=0.6, zorder=0)
    a.set_xlim(0, 8); a.set_ylim(0, 30)
    a.text(7.9, (2 / np.pi) ** 2 * 64 + 1.0, "× (2/π)²", fontsize=6.4, color=C1, ha="right", va="bottom")
    finish(a, "Length (coherence lengths $L_c$)", "Second-harmonic power (arb.)")
    a.legend(loc="upper left", fontsize=6.4, handlelength=1.2, handletextpad=0.5, borderaxespad=0.3)   # clear of the phase-matched curve
    # (b) comb
    f = np.arange(-30, 31)                          # line index, 100 GHz apart
    env = 1 / np.cosh(f / 9.0) ** 2
    P = 10 * np.log10(env) - 20
    b.vlines(f * 0.8, -60, P, color=C1, lw=1.0)
    b.vlines([0], -60, [-3], color=C4, lw=1.6)
    b.plot(f * 0.8, P, color=C1, lw=0.6, ls=(0, (2, 2)))
    b.annotate("pump", xy=(0, -3), xytext=(6, -2), fontsize=6.6, color=C4, arrowprops=dict(arrowstyle="-", color=C4, lw=0.6))
    b.text(24, -6, "lines one FSR apart:\n100 GHz = 0.8 nm", fontsize=6.4, ha="right", va="top", color=INK)
    b.set_xlim(-25, 25); b.set_ylim(-60, 2)
    finish(b, "Frequency offset from the pump (nm)", "Line power (dB, arb.)")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch07_nonlinear")
    i8 = np.searchsorted(z, 8 * Lc) - 1
    print(f"  at 8 L_c: phase matched {E_pm[i8] ** 2:.1f}, QPM {E_qpm[i8] ** 2:.1f} (ratio {E_qpm[i8] ** 2 / E_pm[i8] ** 2:.3f}, (2/pi)^2 = {(2 / np.pi) ** 2:.3f}),"
          f" not matched {E_np[i8] ** 2:.2f}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["mechanisms", "scattering", "fca", "leakage", "tpa", "nonlinear"]
    for w in which:
        globals()["fig_" + w]()
