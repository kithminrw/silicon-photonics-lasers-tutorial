"""Figures for Chapter 8 (bends, tapers and transitions). Run from the worktree root:
    python -I -X utf8 figsrc/ch08_figs.py [conformal bendloss taper crossing escalator converter]
Writes assets/figs/ch08_*.svg and prints every number used in the figures and captions.

Bends: a 1D model. The waveguide is replaced by a slab of its width whose core index is set so that the slab's
fundamental mode has the waveguide's effective index (Chapter 6 values: Si strip TE 2.446, TM 1.771; SiN
1.2 x 0.4 um 1.67), so the evanescent decay constant gamma is the waveguide's. The bend is the conformal
transformation n'(x) = n(x)(1 + x/R); the leaky mode is found by finite differences with a PML on the outside.
Tapers: the effective-index method (vertical slab, then a lateral slab with TM boundary conditions), as in the
eim demo. Mode converter: femwell data of figsrc/ch06_sweep.json.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *
from part2_figs import slab_modes, slab_F

N_SI, N_OX, LAM = 3.476, 1.444, 1.55
K0 = 2 * np.pi / LAM
HERE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ 1D bend solver
def equiv_core(neff, W, ncl=N_OX, lam=LAM):
    lo, hi = neff, 4.0
    for _ in range(80):
        c = (lo + hi) / 2
        if slab_modes(c, ncl, ncl, W, lam)[0] < neff: lo = c
        else: hi = c
    return (lo + hi) / 2


def tridiag_solve(a, b, c, d):
    """Solve a tridiagonal system (sub-diagonal a[1:], diagonal b, super-diagonal c[:-1]), complex."""
    n = len(b); cp = np.zeros(n, complex); dp = np.zeros(n, complex)
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < n - 1 else 0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = np.zeros(n, complex); x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def bend_mode(nc, W, R, ncl=N_OX, lam=LAM, h=0.008, pml=2.0, smax=4.0, xin=1.5, guess=None):
    """Leaky mode of a slab (core nc, width W, centred at x = 0) bent with radius R (np.inf: straight).
    Returns x, complex field, complex n_eff referred to the guide centre."""
    k0 = 2 * np.pi / lam
    ne0 = slab_modes(nc, ncl, ncl, W, lam)[0]
    if np.isfinite(R):
        xr = R * (ne0 / ncl - 1)
        x0, x1 = -min(W / 2 + xin, 0.6 * R), max(xr + 2.0, W / 2 + 2.0)
    else:
        x0, x1 = -(W / 2 + xin), W / 2 + xin
    xp = x1; x1 = x1 + pml
    x = np.arange(x0, x1 + h / 2, h); n = len(x)
    nn = np.where(np.abs(x) <= W / 2, nc, ncl) * ((1 + x / R) if np.isfinite(R) else 1)
    def s(xx):
        sig = np.where(xx > xp, smax * ((xx - xp) / pml)**2, 0.0)
        return 1 - 1j * sig
    sj, sp, sm = s(x), s(x + h / 2), s(x - h / 2)
    a = 1 / (sj * sm * h**2); c = 1 / (sj * sp * h**2); b = -(a + c) + (k0 * nn)**2
    sigma = (k0 * (guess or ne0))**2 * (1 + 1e-6)
    v = np.exp(-((x) / W)**2).astype(complex)
    lamb = sigma
    for it in range(40):
        w = tridiag_solve(a, b - sigma, c, v)
        lam_new = sigma + np.dot(v, v) / np.dot(v, w)
        v = w / np.sqrt(np.dot(w, w))
        if abs(lam_new - lamb) < 1e-13 * abs(lam_new) and it > 3: lamb = lam_new; break
        lamb = lam_new
        if it >= 3: sigma = lamb                                  # Rayleigh-quotient shift once close
    beta = np.sqrt(lamb)
    k = np.argmax(np.abs(v)); v = v / v[k]
    return x, v, beta / k0


def loss_db90(ne, R, lam=LAM):
    k0 = 2 * np.pi / lam
    return 4.343 * 2 * k0 * abs(ne.imag) * np.pi * R / 2


CASES = {"si_te": ("Si strip, TE", 2.446, 0.5, C1), "si_tm": ("Si strip, TM", 1.771, 0.5, C2), "sin": ("SiN 1.2 × 0.4 µm", 1.67, 1.2, C3)}


# ------------------------------------------------------------------ Figure: conformal transformation
def fig_conformal():
    name, ne, W, col = CASES["si_te"]
    nc = equiv_core(ne, W); R = 2.0
    g = K0 * np.sqrt(ne**2 - N_OX**2); xr = R * (ne / N_OX - 1)
    xs, Es, ns_ = bend_mode(nc, W, np.inf, xin=4.0)
    xb, Eb, nb = bend_mode(nc, W, R)
    print(f"[conformal] equivalent core index {nc:.4f}; straight n_eff {ns_.real:.4f}; gamma {g:.2f}/um; x_r = {xr:.3f} um = {xr/R:.3f} R; "
          f"gamma x_r = {g*xr:.1f}")
    print(f"[conformal] R = {R}: bent n_eff (at guide centre) {nb.real:.4f} + {abs(nb.imag):.2e}i, loss {loss_db90(nb, R):.2e} dB/90deg")
    Is, Ib = np.abs(Es)**2, np.abs(Eb)**2
    pk_s = xs[np.argmax(Is)]; pk_b = xb[np.argmax(Ib)]
    cs = np.trapezoid(xs * Is, xs) / np.trapezoid(Is, xs); cb = np.trapezoid((xb * Ib)[xb < xr], xb[xb < xr]) / np.trapezoid(Ib[xb < xr], xb[xb < xr])
    print(f"[conformal] peak shift {1000*(pk_b-pk_s):.0f} nm, centroid shift {1000*(cb-cs):.0f} nm")
    fig, (a, b, c) = plt.subplots(3, 1, figsize=(6.3, 4.6), sharex=True, gridspec_kw=dict(height_ratios=[1.1, 1, 1]))
    x = np.linspace(-1.0, 3.0, 2000)
    n0 = np.where(np.abs(x) <= W / 2, ne * 0 + nc, N_OX)
    a.plot(x, n0, color=MUTED, lw=1.0, ls="--", label="straight, $n(x)$")
    a.plot(x, n0 * (1 + x / R), color=C1, lw=1.5, label=r"bent, $n(x)(1 + x/R)$")
    a.axhline(ne, color=C4, lw=0.9, ls=":")
    a.text(-0.97, ne + 0.06, rf"$n_\mathrm{{eff}}$ = {ne:.3f}", fontsize=6.8, color=C4, va="bottom")
    a.axvline(xr, color=INK, lw=0.7)
    a.annotate(rf"caustic $x_r$ = {xr:.2f} µm", (xr, ne), xytext=(xr + 0.12, 3.6), fontsize=6.8, color=INK, va="center",
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a.set_ylim(1.2, 4.3)
    finish(a, None, "Index", legend=True, loc="upper left")
    a.legend(loc="upper left", fontsize=6.5)
    b.plot(xs, Is / Is.max(), color=MUTED, ls="--", lw=1.2, label="straight")
    b.plot(xb, Ib / Ib.max(), color=C1, lw=1.5, label=f"bent, R = {R:.0f} µm")
    for ax in (a, b, c):
        ax.axvspan(-W / 2, W / 2, color=MAT["si"], alpha=0.35, lw=0, zorder=0)
    b.set_ylim(0, 1.1)
    b.annotate("the mode leans outward", (pk_b, 1.0), xytext=(0.55, 0.75), fontsize=6.8, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    finish(b, None, r"$|E|^2$", legend=True, loc="upper right")
    c.plot(xs, 10 * np.log10(Is / Is.max()), color=MUTED, ls="--", lw=1.2)
    c.plot(xb[xb < xr + 2.0], 10 * np.log10(Ib / Ib.max())[xb < xr + 2.0], color=C1, lw=1.2)
    c.axvline(xr, color=INK, lw=0.7)
    lev = 10 * np.log10(np.exp(-2 * g * (xr - W / 2)))
    c.text(xr + 0.1, -60, "beyond the caustic the tail\nradiates instead of decaying", fontsize=6.8, color=INK, va="center")
    c.set_ylim(-140, 5); c.set_xlim(-1.0, 3.0)
    finish(c, "Distance from the guide centre, towards the outside of the bend (µm)", r"$|E|^2$ (dB)")
    for ax, t in zip((a, b, c), "abc"): tag(ax, t)
    print(f"[conformal] straight-tail level at the caustic exp(-2 gamma (x_r - W/2)) = {lev:.0f} dB; bent field there "
          f"{10*np.log10(Ib[np.argmin(np.abs(xb-xr))]/Ib.max()):.0f} dB")
    fig.tight_layout(h_pad=0.6)
    save(fig, "ch08_conformal")


# ------------------------------------------------------------------ Figure: bend loss against radius
def overlap(x1, E1, x2, E2):
    xs = np.linspace(max(x1[0], x2[0]), min(x1[-1], x2[-1]), 6000)
    a = np.interp(xs, x1, E1.real) + 1j * np.interp(xs, x1, E1.imag)
    b = np.interp(xs, x2, E2.real) + 1j * np.interp(xs, x2, E2.imag)
    return abs(np.trapezoid(a * b, xs))**2 / (np.trapezoid(np.abs(a)**2, xs) * np.trapezoid(np.abs(b)**2, xs))


def fig_bendloss():
    radii = {"si_te": np.geomspace(0.8, 10.5, 22), "si_tm": np.geomspace(2, 40, 18), "sin": np.geomspace(6, 120, 18)}
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.35, 1]))
    res = {}
    for key, (name, ne, W, col) in CASES.items():
        nc = equiv_core(ne, W); g = K0 * np.sqrt(ne**2 - N_OX**2)
        xs, Es, _ = bend_mode(nc, W, np.inf, xin=4.0)
        L, J, gx = [], [], []
        for R in radii[key]:
            x, E, nb = bend_mode(nc, W, R, h=0.01 if R > 30 else 0.008)
            L.append(loss_db90(nb, R)); gx.append(g * R * (ne / N_OX - 1))
            J.append(-10 * np.log10(overlap(xs, Es, x, E)))
        L, J, gx = map(np.array, (L, J, gx)); res[key] = (radii[key], L, J, gx)
        ok = L > 1e-7
        a.loglog(radii[key][ok], L[ok], color=col, label=name)
        print(f"[bendloss] {name}: equivalent core {nc:.4f}, gamma {g:.2f}/um, 1/gamma {1000/g:.0f} nm")
        for R, l, j, q in zip(radii[key], L, J, gx):
            print(f"    R {R:6.2f} um  gamma x_r {q:5.1f}  radiation {l:.2e} dB/90  junction {j:.3f} dB each")
    # the gamma x_r = 11 points of Worked Example 8.1
    for key, R in (("si_te", 2.0), ("sin", 20.0)):
        name, ne, W, col = CASES[key]; nc = equiv_core(ne, W); g = K0 * np.sqrt(ne**2 - N_OX**2)
        x, E, nb = bend_mode(nc, W, R); l = loss_db90(nb, R)
        a.plot(R, l, "o", color=col, ms=4.5, zorder=5)
        a.annotate(rf"$\gamma x_r$ = {g*R*(ne/N_OX-1):.0f}", (R, l), xytext=(5, 4), textcoords="offset points", fontsize=6.8, color=col)
        print(f"[bendloss] {name} at R = {R}: gamma x_r {g*R*(ne/N_OX-1):.1f}, radiation {l:.2e} dB/90")
    a.set_xlim(0.8, 120); a.set_ylim(1e-6, 30)
    a.set_xticks([1, 2, 5, 10, 20, 50, 100]); a.set_xticklabels(["1", "2", "5", "10", "20", "50", "100"])
    finish(a, "Bend radius R (µm)", "Radiation loss (dB per 90°)", legend=True, loc="upper right")
    # (b) silicon TE: radiation (1D model) against the two junction losses of a circular 90 deg bend (femwell overlaps)
    R_, L_, J_, _ = res["si_te"]
    b.semilogy(R_, L_, color=C1, label="radiation (1D model)")
    # (the 1D model gives about twice the full-vectorial junction loss; printed, not drawn)
    print(f"[bendloss] 1D model, Si TE at R = 2: two junctions {np.interp(2, R_, 2*J_):.3f} dB")
    p = os.path.join(HERE, "ch08_bend.json")
    if os.path.exists(p):
        F = json.load(open(p))
        Rf = np.array([r["R"] for r in F["runs"]]); Jf = np.array([r["junction_dB"] for r in F["runs"]])
        b.semilogy(Rf, 2 * Jf, "o--", color=C4, ms=3.5, label="two junctions (femwell)")
        for r in F["runs"]:
            print(f"[bendloss] femwell R {r['R']}: n straight {r['n_straight']:.4f}, bent {r['n_bent']:.4f}, junction {r['junction_dB']:.4f} dB each, "
                  f"peak shift {1000*r['peak_shift']:.0f} nm, centroid shift {1000*r['centroid_shift']:.0f} nm")
        Lf = np.interp(Rf, R_, L_)
        k = np.where(2 * Jf > Lf)[0]
        if len(k): print(f"[bendloss] femwell junctions exceed 1D radiation from R = {Rf[k[0]]} um")
    b.set_xlim(0.8, 10.5); b.set_ylim(1e-4, 30)
    b.set_xscale("log"); b.set_xticks([1, 2, 5, 10]); b.set_xticklabels(["1", "2", "5", "10"])
    finish(b, "Bend radius R (µm)", "Loss per 90° bend (dB)", legend=True, loc="upper right")
    b.legend(loc="upper right", fontsize=6.3)
    b.text(0.03, 0.04, "Si strip, TE", transform=b.transAxes, fontsize=7, color=INK)
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.0)
    save(fig, "ch08_bendloss")


# ------------------------------------------------------------------ effective-index method helpers (tapers)
def nI_vert(lam=LAM, t=0.22):
    return slab_modes(N_SI, N_OX, N_OX, t, lam)[0]


def lateral(W, m, nI, nII=N_OX, lam=LAM):
    ms = slab_modes(nI, nII, nII, W, lam, tm=True)
    return ms[m] if len(ms) > m else np.nan


def lateral_field(W, nI, x, nII=N_OX, lam=LAM):
    """TE-like fundamental lateral field (H-type slab, the E_x profile is H_y/n^2; here the shape of H_y)."""
    ne = lateral(W, 0, nI, nII, lam); k0 = 2 * np.pi / lam
    ka, g = k0 * np.sqrt(nI**2 - ne**2), k0 * np.sqrt(ne**2 - nII**2)
    return np.where(np.abs(x) <= W / 2, np.cos(ka * x), np.cos(ka * W / 2) * np.exp(-g * (np.abs(x) - W / 2)))


def fig_taper():
    nI = nI_vert()
    Ws = np.linspace(0.5, 3.0, 251)
    n0 = np.array([lateral(W, 0, nI) for W in Ws]); n2 = np.array([lateral(W, 2, nI) for W in Ws])
    n2c = np.where(np.isnan(n2), N_OX, n2)               # below the TE2 cut-off: the radiation modes start at the cladding index
    wc = Ws[np.where(~np.isnan(n2))[0][0]]
    allowed = (Ws / 2) * K0 * (n0 - n2c) / (2 * np.pi)
    print(f"[taper] EIM n_I {nI:.4f}; TE0 at 0.5 um {n0[0]:.4f}, at 3 um {n0[-1]:.4f}; TE2 guided above W = {wc:.2f} um; "
          f"TE2 at 3 um {n2[-1]:.4f}")
    print(f"[taper] allowed d rho/dz at 0.5 um {allowed[0]:.3f}, at 1 um {np.interp(1.0, Ws, allowed):.3f}, at 3 um {allowed[-1]:.3f}; peak {allowed.max():.3f} at W = {Ws[allowed.argmax()]:.2f} um")
    slopes = {L: 2.5 / (2 * L) for L in (20, 40)}
    for L, sl in slopes.items():
        M = allowed / sl
        print(f"[taper] linear {L} um: slope {sl:.4f}, margin min {M.min():.2f} (at W = {Ws[M.argmin()]:.2f}), max {M.max():.2f}")
    Mmin = (allowed / slopes[20]).min()
    # constant-margin profile with the same worst-case margin as the 20 um linear taper: dz = M 2 pi/(rho dbeta) d rho
    dz = Mmin / allowed * np.gradient(Ws / 2)
    z = np.concatenate([[0], np.cumsum(0.5 * (dz[1:] + dz[:-1]))])
    Lcm = z[-1]
    print(f"[taper] constant-margin taper (margin {Mmin:.2f}): length {Lcm:.1f} um vs 20 um linear")
    fig = plt.figure(figsize=(6.3, 3.5))
    # (a) top view to scale
    ax = fig.add_axes([0.0, 0.6, 1.0, 0.4]); frameless(ax, (-1.6, 22.5), (-2.3, 2.3))
    box(ax, -1.6, -2.3, 24.1, 4.6, "oxtop", z=0)
    wg_straight(ax, -1.6, 0, 0, 0.5); wg_taper(ax, 0, 20, 0, 0.5, 3.0); wg_straight(ax, 20, 22.5, 0, 3.0)
    zz = np.interp(np.linspace(0, Lcm, 200), z, z); ww = np.interp(zz, z, Ws)
    ax.plot(zz, ww / 2, color=C4, lw=1.0, ls="--", zorder=4); ax.plot(zz, -ww / 2, color=C4, lw=1.0, ls="--", zorder=4)
    ax.plot([Lcm, 22.5], [1.5, 1.5], color=C4, lw=1.0, ls="--", zorder=4); ax.plot([Lcm, 22.5], [-1.5, -1.5], color=C4, lw=1.0, ls="--", zorder=4)
    for zp in (0, 5, 10, 15, 20):
        W = 0.5 + 2.5 * zp / 20
        h = W / 2 + 0.45
        xx = np.linspace(-h, h, 400); f = lateral_field(W, nI, xx)**2
        ax.plot(zp + 1.5 * f / f.max(), xx, color=RED, lw=1.0, zorder=5)
        ax.plot([zp, zp], [-h, h], color=RED, lw=0.4, ls=":", zorder=5)
    label(ax, 0.3, -1.95, "local TE$_0$ mode profile", fs=6.8, col=RED, ha="left", va="center")
    label(ax, 0.3, 1.95, f"dashed: constant-margin profile, {Lcm:.1f} µm long", fs=6.8, col=C4, ha="left", va="center")
    scalebar(ax, 17.5, -2.15, 2.0, "2 µm", above=True)
    panel(ax, "a", 0.0, 1.0)
    # (b) Love's criterion
    b = fig.add_axes([0.1, 0.1, 0.86, 0.42])
    b.plot(Ws, allowed, color=C1, label=r"criterion, $\rho(\beta_1 - \beta_2)/2\pi$")
    for L, ls in ((20, "-"), (40, "--")):
        b.axhline(slopes[L], color=C2, ls=ls, lw=1.2, label=f"linear taper, {L} µm")
    b.axvline(wc, color=MUTED, lw=0.6, ls=":")
    b.text(wc + 0.03, 0.012, f"TE$_2$ guided above {wc:.2f} µm", fontsize=6.5, color=MUTED, va="center")
    b.set_xlim(0.5, 3.0); b.set_ylim(0, 0.32)
    finish(b, "Local width W (µm)", r"d$\rho$/d$z$", legend=True, loc="upper right")
    tag(b, "b")
    save(fig, "ch08_taper")


# ------------------------------------------------------------------ Figure: crossings
def gauss_fit_w(W, nI):
    """1/e^2 half-width of the Gaussian that best overlaps the EIM lateral mode of width W."""
    x = np.linspace(-4, 4, 4001); f = lateral_field(W, nI, x)
    best = (0, 0)
    for w in np.linspace(0.1, 2.0, 381):
        gg = np.exp(-(x / w)**2)
        eta = np.trapezoid(f * gg, x)**2 / (np.trapezoid(f**2, x) * np.trapezoid(gg**2, x))
        if eta > best[0]: best = (eta, w)
    return best[1], best[0]


def cross_eta(w0, L, n, lam=LAM):
    """1D overlap of a Gaussian beam (waist w0 at the entrance) after free diffraction over L in a slab of index n, with the
    same waveguide mode (waist w0) on the far side."""
    x = np.linspace(-6, 6, 6001); zr = np.pi * w0**2 * n / lam
    q = L + 1j * zr; k = 2 * np.pi * n / lam
    u = np.exp(-1j * k * x**2 / (2 * q)) / np.sqrt(q)
    g = np.exp(-(x / w0)**2)
    return abs(np.trapezoid(u * g, x))**2 / (np.trapezoid(np.abs(u)**2, x) * np.trapezoid(g**2, x)), zr


def fig_crossing():
    nI = nI_vert()
    w_n, e_n = gauss_fit_w(0.5, nI); Wexp = 1.6; w_e, e_e = gauss_fit_w(Wexp, nI)
    eta_n, zr_n = cross_eta(w_n, 0.5, nI); eta_e, zr_e = cross_eta(w_e, Wexp, nI)
    print(f"[crossing] slab index {nI:.3f}; 500 nm mode ~ Gaussian w = {w_n:.3f} um (overlap {e_n:.3f}), z_R {zr_n:.2f} um; "
          f"{Wexp} um section: w = {w_e:.3f} um (overlap {e_e:.3f}), z_R {zr_e:.2f} um")
    print(f"[crossing] diffraction across the opening: plain {-10*np.log10(eta_n):.2f} dB, expanded {-10*np.log10(eta_e):.2f} dB")
    wtab = [(W, gauss_fit_w(W, nI)[0]) for W in np.linspace(0.5, Wexp, 12)]
    wloc = lambda W: np.interp(W, [a for a, _ in wtab], [b for _, b in wtab])
    S0, S1 = 0.8, 3.0                          # expander: 1.6 um wide at |s| = 0.8 um, back to 0.5 um at |s| = 3 um
    def expander(s):
        return np.where(s > S1, 0.5, 0.5 + (Wexp - 0.5) * np.sqrt(np.clip(1 - ((s - S0) / (S1 - S0))**2, 0, 1)))
    fig = plt.figure(figsize=(6.3, 2.75))
    H = 3.3
    for i, (expanded, tagc) in enumerate(((False, "a"), (True, "b"))):
        ax = fig.add_axes([0.505 * i, 0.0, 0.495, 1.0]); frameless(ax, (-H, H), (-2.6, 2.9))
        box(ax, -H, -2.6, 2 * H, 5.5, "oxtop", z=0)
        if not expanded:
            for ang in (0, 90):
                pts = np.array([[-H, -0.25], [H, -0.25], [H, 0.25], [-H, 0.25]])
                if ang: pts = pts[:, ::-1]
                poly(ax, pts, "si", z=2)
            x0 = -0.25; w0 = w_n
            xin = np.linspace(-H, x0, 50); win = np.full_like(xin, w0)
        else:
            s = np.linspace(S0, H, 300); wid = expander(s)
            for ang in (0, 90):
                for sgn in (-1, 1):
                    pts = np.vstack([np.c_[sgn * s, wid / 2], np.c_[sgn * s[::-1], -wid[::-1] / 2]])
                    if ang: pts = pts[:, ::-1]
                    poly(ax, pts, "si", z=2)
                pts = np.array([[-S0 - 0.01, -Wexp / 2], [S0 + 0.01, -Wexp / 2], [S0 + 0.01, Wexp / 2], [-S0 - 0.01, Wexp / 2]])
                if ang: pts = pts[:, ::-1]
                poly(ax, pts, "si", z=2)
            x0 = -S0; w0 = w_e
            xin = np.linspace(-H, x0, 120); win = wloc(expander(-xin))
        # beam (1/e^2 half-width): guided up to the opening, then free diffraction in the slab (Gaussian beam)
        zr = np.pi * w0**2 * nI / LAM
        xo = np.linspace(x0, -x0, 80); wo = w0 * np.sqrt(1 + ((xo - x0) / zr)**2)
        xs_ = np.concatenate([xin, xo]); ws_ = np.concatenate([win, wo])
        ax.fill_between(xs_, -ws_, ws_, color=RED, alpha=0.3, lw=0, zorder=4)
        ax.plot(xs_, ws_, color=RED, lw=0.7, zorder=4); ax.plot(xs_, -ws_, color=RED, lw=0.7, zorder=4)
        # the part of the spread beam that the output guide must recapture
        ax.plot([-x0, -x0], [-wo[-1], wo[-1]], color=RED, lw=1.0, zorder=5)
        arrow(ax, (-3.1, 0), (-2.3, 0), col=INK, lw=1.0, ms=7)
        eta = eta_e if expanded else eta_n
        txt = (f"expanded to {Wexp} µm: the beam\nspreads little across the opening" if expanded
               else "500 nm mode: the beam spreads\nfast across the open intersection")
        label(ax, 0.0, -2.25, txt, fs=6.8, va="center")
        scalebar(ax, 1.6, 2.35, 1.0, "1 µm", above=True)
        panel(ax, tagc, 0.02, 0.98)
        print(f"[crossing] {'expanded' if expanded else 'plain'}: opening {2*abs(x0):.2f} um, beam {w0:.3f} -> {wo[-1]:.3f} um, "
              f"Gaussian estimate {-10*np.log10(eta):.2f} dB")
    save(fig, "ch08_crossing")


# ------------------------------------------------------------------ Figure: Si-to-SiN escalator
def sin_eim(W, t=0.4, nsn=1.996, lam=LAM):
    nIs = slab_modes(nsn, N_OX, N_OX, t, lam)[0]
    return lateral(W, 0, nIs)


def fig_escalator():
    T = json.load(open(os.path.join(HERE, "ch16_taper.json")))          # femwell TE0 of 220 nm Si strips, 80-500 nm wide
    T = sorted([(o["width"], o["neff"]) for o in T if o["pol"] == "TE"])
    Wsi = np.array([a for a, _ in T]); nsi_te = np.array([b for _, b in T])
    print(f"[escalator] SiN 1.2 x 0.4 um by EIM: {sin_eim(1.2):.3f} (chapter: about 1.67); SiN 0.3 um tip: {sin_eim(0.3):.3f}")
    u = np.linspace(0, 1, 201)
    wsi = 0.5 - 0.32 * u                     # Si 500 -> 180 nm
    wsn = 0.3 + 0.9 * u                      # SiN 0.3 -> 1.2 um
    n_si = np.interp(wsi, Wsi, nsi_te); n_sn = np.array([sin_eim(w) for w in wsn])
    k = np.argmin(np.abs(n_si - n_sn))
    print(f"[escalator] isolated-guide indices cross at u = {u[k]:.2f}: Si width {1000*wsi[k]:.0f} nm, SiN width {1000*wsn[k]:.0f} nm, n = {n_si[k]:.3f}")
    print(f"[escalator] Si 500 nm {n_si[0]:.3f} -> 180 nm {n_si[-1]:.3f}; SiN {n_sn[0]:.3f} -> {n_sn[-1]:.3f}")
    fig = plt.figure(figsize=(6.3, 3.7))
    # (a) side view, schematic
    ax = fig.add_axes([0.0, 0.66, 1.0, 0.33]); frameless(ax, (-0.5, 10.5), (-0.6, 1.9), equal=False)
    box(ax, -0.5, -0.6, 11, 0.6, "ox", z=0); box(ax, -0.5, 0, 11, 1.9, "oxtop", z=0)
    box(ax, -0.5, 0, 7.5, 0.3, "si", z=2)                        # Si layer ends in a tip (side view: constant thickness)
    box(ax, 2.0, 0.75, 8.5, 0.45, "sin", z=2)
    for xc, yc in ((0.6, 0.15), (4.5, 0.55), (9.0, 0.97)):
        ax.add_patch(Ellipse((xc, yc), 1.3, 0.55 if xc < 4 else 0.75, fc=RED, alpha=0.28, ec=RED, lw=0.6, zorder=4))
    arrow(ax, (1.4, 0.3), (3.8, 0.5), col=RED, lw=0.9, ms=6); arrow(ax, (5.3, 0.62), (8.2, 0.92), col=RED, lw=0.9, ms=6)
    label(ax, 0.05, 1.55, "side view", fs=6.8, ha="left", italic=True, col=MUTED)
    label(ax, 7.1, 0.15, "Si (tapers to a tip)", fs=6.5, ha="left", va="center")
    label(ax, 2.1, 1.38, "SiN (tapers up)", fs=6.5, ha="left", va="center")
    label(ax, 10.4, -0.32, "oxide", fs=6.5, ha="right", va="center")
    note(ax, "schematic, not to scale", loc="lower left")
    panel(ax, "a", 0.0, 1.0)
    # (b) top view, schematic
    bx = fig.add_axes([0.0, 0.41, 1.0, 0.23]); frameless(bx, (-0.5, 10.5), (-0.9, 0.9), equal=False)
    box(bx, -0.5, -0.9, 11, 1.8, "oxtop", z=0)
    poly(bx, [(-0.5, -0.25), (2.0, -0.25), (7.0, -0.09), (7.0, 0.09), (2.0, 0.25), (-0.5, 0.25)], "si", z=2)
    poly(bx, [(2.0, -0.15), (7.0, -0.6), (10.5, -0.6), (10.5, 0.6), (7.0, 0.6), (2.0, 0.15)], "sin", alpha=0.75, z=3)
    label(bx, 0.05, 0.62, "top view", fs=6.8, ha="left", italic=True, col=MUTED)
    dim(bx, (2.0, -0.78), (7.0, -0.78), "transition", lw=0.6)
    panel(bx, "b", 0.0, 1.0)
    # (c) indices along the transition, aligned with the transition drawn above (x = 2 ... 7)
    x2f = lambda xd: (xd + 0.5) / 11.0
    c = fig.add_axes([x2f(2.0), 0.09, x2f(7.0) - x2f(2.0), 0.24])
    up = (0.5 - Wsi[(Wsi >= 0.18) & (Wsi <= 0.5)]) / 0.32
    c.plot(up, nsi_te[(Wsi >= 0.18) & (Wsi <= 0.5)], "o", color=C1, ms=2.5)
    c.plot(u, n_si, color=C1, label="Si strip, 500 → 180 nm\n(femwell)")
    c.plot(u, n_sn, color=C2, label="SiN 400 nm thick,\n0.3 → 1.2 µm (EIM)")
    c.plot(u[k], n_si[k], "o", color=INK, ms=4)
    c.set_xlim(0, 1); c.set_ylim(1.4, 2.5); c.set_xticks([0, 0.5, 1]); c.set_xticklabels(["start", "middle", "end"])
    finish(c, None, r"$n_\mathrm{eff}$")
    c.legend(loc="center left", bbox_to_anchor=(1.03, 0.5), fontsize=6.5)
    tag(c, "c")
    save(fig, "ch08_escalator")


# ------------------------------------------------------------------ Figure: TE0 -> TE1 mode converter
def fig_converter():
    S = json.load(open(os.path.join(HERE, "ch06_sweep.json")))
    W = np.array(S["widths"])
    te0 = np.array([max(n for n, f in ms if f > 0.5) for ms in S["neff1550"]])
    te1 = np.array([sorted([n for n, f in ms if f > 0.5], reverse=True)[1] if sum(f > 0.5 for n, f in ms) > 1 else np.nan for ms in S["neff1550"]])
    Wb = 1.0; target = te1[np.argmin(np.abs(W - Wb))]
    Wa = np.interp(target, te0, W)
    print(f"[converter] TE1 of the {Wb} um guide: {target:.4f}; TE0 phase-matched width {1000*Wa:.0f} nm")
    fig = plt.figure(figsize=(6.3, 2.5))
    # (a) top view, to scale
    ax = fig.add_axes([0.0, 0.0, 0.55, 1.0]); frameless(ax, (-1.0, 13.0), (-2.2, 3.3))
    box(ax, -1.0, -2.2, 14.0, 5.5, "oxtop", z=0)
    gap = 0.2; yb = 0.0; ya = Wb / 2 + gap + Wa / 2
    wg_straight(ax, -1.0, 13.0, yb, Wb)
    xs_, ys_ = sbend_xy(-1.0, ya + 1.2, 3.0, -1.2); ribbon(ax, xs_, ys_, Wa, "si")
    wg_straight(ax, 1.97, 10.03, ya, Wa)
    xs_, ys_ = sbend_xy(10.0, ya, 3.0, 1.2); ribbon(ax, xs_, ys_, Wa, "si")
    # field sketches: TE0 in the narrow guide (input), TE1 in the wide guide (output)
    yy = np.linspace(-0.9, 0.9, 200)
    ax.plot(0.6 + 0.9 * np.exp(-(yy / 0.22)**2), ya + 1.0 + yy * 0.5, color=RED, lw=1.0, zorder=5)
    f1 = (yy / 0.3) * np.exp(-(yy / 0.42)**2); f1 /= np.abs(f1).max()
    ax.plot(11.8 + 0.6 * f1, yb + yy * 0.7, color=RED, lw=1.0, zorder=5); ax.plot([11.8, 11.8], [yb - 0.65, yb + 0.65], color=RED, lw=0.4, ls=":", zorder=5)
    label(ax, 0.2, ya + 1.95, f"TE$_0$ in, W = {1000*Wa:.0f} nm", fs=6.5, ha="left")
    label(ax, 12.9, yb - 1.25, f"TE$_1$ out, W = {Wb:.1f} µm", fs=6.5, ha="right")
    label(ax, 6.0, -1.25, "coupling region (phase-matched)", fs=6.5)
    dim(ax, (2.0, ya + 0.55), (10.0, ya + 0.55), "", lw=0.5)
    scalebar(ax, 0.0, -2.0, 2.0, "2 µm")
    note(ax, "gap and length illustrative", loc="lower right")
    panel(ax, "a", 0.0, 1.0)
    # (b) phase matching
    b = fig.add_axes([0.66, 0.17, 0.32, 0.75])
    b.plot(W, te0, "o-", color=C1, ms=2.5, label="TE$_0$")
    b.plot(W, te1, "o-", color=C3, ms=2.5, label="TE$_1$")
    b.plot([Wa, Wb], [target, target], ":", color=INK, lw=0.9)
    b.plot([Wa], [target], "o", color=INK, ms=4); b.plot([Wb], [target], "o", color=INK, ms=4)
    b.annotate(f"{1000*Wa:.0f} nm", (Wa, target), xytext=(Wa + 0.07, target - 0.25), fontsize=6.8, ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xlim(0.25, 1.0); b.set_ylim(1.4, 2.8)
    finish(b, "Width (µm)", r"$n_\mathrm{eff}$ (1550 nm)", legend=True, loc="lower right")
    tag(b, "b")
    save(fig, "ch08_converter")


if __name__ == "__main__":
    which = sys.argv[1:] or ["conformal", "bendloss", "taper", "crossing", "escalator", "converter"]
    for w in which:
        globals()["fig_" + w]()
