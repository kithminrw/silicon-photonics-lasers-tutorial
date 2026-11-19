"""Figures for Chapter 23 (semiconductor gain media).

Run from the repository root:  python -I -X utf8 figsrc/ch23_figs.py      (about a minute)
Writes assets/figs/ch23_recipe.svg, ch23_spectra.svg, ch23_hetero.svg, ch23_dos.svg, ch23_alloys.svg and
ch23_abc.svg, and prints every number the figures and captions use.

The gain model is a NumPy-only port of figsrc/ch23_gain.py (which needs SciPy): same constants, same algorithm, and it
reproduces that script's numbers (N_tr 1.3e18 cm^-3, 725 /cm at 2.7e18, dg/dN 4.7e-16 cm^2 at 3e18).
The slab-mode solver (TE, transfer matrix) is also used by figsrc/ch24_figs.py.
Alloy band gaps and lattice constants: Vurgaftman, Meyer and Ram-Mohan, J. Appl. Phys. 89, 5815 (2001).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *

HC = 1239.84                                   # eV nm

# ================================================================== gain model (port of ch23_gain.py)
HBAR, QE, M0, KB, CL, EPS0 = 1.054571817e-34, 1.602176634e-19, 9.1093837015e-31, 1.380649e-23, 2.99792458e8, 8.8541878128e-12
EG0, DEGDT, ME, MV, EP, NR, TAU = 0.80, -3.5e-4, 0.045, 0.46, 25.0, 3.5, 1e-13   # eV, eV/K, m0, m0, eV, -, s
MR = ME * MV / (ME + MV)
_X = np.linspace(0, 60, 6001)


def expit(x):
    return 0.5 * (1 + np.tanh(0.5 * np.asarray(x, float)))


def F12(eta):
    """Fermi-Dirac integral of order 1/2, normalised so that F -> exp(eta) for eta << 0."""
    return 2 / np.sqrt(np.pi) * np.sum(np.sqrt(_X) * expit(-(_X - eta))) * (_X[1] - _X[0])


def Nc(m, T):
    return 2 * (m * M0 * KB * T / (2 * np.pi * HBAR ** 2)) ** 1.5 / 1e6          # cm^-3


def eta_of(n_cm3, m, T):
    nc = Nc(m, T); lo, hi = -30.0, 80.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if nc * F12(mid) < n_cm3: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def gain(N, T=300.0, E_=None):
    """(photon energies eV, gain 1/cm, quasi-Fermi separation eV, band gap eV, unbroadened parts)."""
    Eg = EG0 + DEGDT * (T - 300); kT = KB * T / QE
    ec, ev = eta_of(N, ME, T), eta_of(N, MV, T)
    if E_ is None: E_ = np.linspace(Eg - 0.06, Eg + 0.20, 521)
    Mb2 = M0 / 6 * EP * QE
    Ex = np.linspace(Eg, Eg + 0.5, 2001); d = Ex - Eg
    rho = (1 / (2 * np.pi ** 2)) * (2 * MR * M0 / HBAR ** 2) ** 1.5 * np.sqrt(d * QE)
    fc = expit(-((MR / ME) * d / kT - ec)); fh = expit(-((MR / MV) * d / kT - ev))
    pre = np.pi * QE ** 2 * HBAR / (NR * CL * EPS0 * M0 ** 2) * Mb2 * rho
    g_unbr = pre * (fc + fh - 1)
    gam = HBAR / TAU / QE
    out = np.array([np.sum(g_unbr * (gam / np.pi) / ((Ei - Ex) ** 2 + gam ** 2)) * (Ex[1] - Ex[0]) / (Ei * QE) / 100 for Ei in E_])
    parts = dict(Ex=Ex, occ=fc + fh - 1, ec=ec, ev=ev, kT=kT)
    return E_, out, Eg + (ec + ev) * kT, Eg, parts


def peak(N, T=300.0):
    E_, g, dF, Eg, _ = gain(N, T)
    sel = E_ >= Eg; j = np.where(sel)[0][np.argmax(g[sel])]
    return g[j], E_[j]


def n_for(gtarget, T=300.0, lo=5e17, hi=1e19):
    for _ in range(40):
        mid = (lo + hi) / 2
        if peak(mid, T)[0] < gtarget: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def dos(E_rel, m):
    """3D density of states (both spins) at energy E_rel (eV) above a band edge, in cm^-3 eV^-1."""
    return (1 / (2 * np.pi ** 2)) * (2 * m * M0 / HBAR ** 2) ** 1.5 * np.sqrt(np.clip(E_rel, 0, None) * QE) * QE / 1e6


# ================================================================== TE slab modes (transfer matrix)
def slab_te(layers, ncl, lam=1.55, ncl_top=None):
    """Fundamental TE mode of a planar stack. layers: [(thickness um, n), ...] from bottom to top, between a lower
    cladding ncl and an upper cladding ncl_top (default ncl). Returns neff and E(x) (callable, x in um, x = 0 at the
    bottom of the first layer)."""
    ncl_top = ncl if ncl_top is None else ncl_top
    k0 = 2 * np.pi / lam

    def propagate(neff, upto=None):
        g = k0 * np.sqrt(max(neff ** 2 - ncl ** 2, 1e-12)); E, D = 1.0, g
        for t, n in layers:
            q2 = k0 ** 2 * (n ** 2 - neff ** 2)
            if q2 > 0:
                q = np.sqrt(q2); E, D = np.cos(q * t) * E + np.sin(q * t) / q * D, -q * np.sin(q * t) * E + np.cos(q * t) * D
            else:
                p = np.sqrt(-q2); E, D = np.cosh(p * t) * E + np.sinh(p * t) / p * D, p * np.sinh(p * t) * E + np.cosh(p * t) * D
        gt = k0 * np.sqrt(max(neff ** 2 - ncl_top ** 2, 1e-12))
        return D + gt * E
    nmax = max(n for _, n in layers); nmin = max(ncl, ncl_top)
    grid = np.linspace(nmax - 1e-9, nmin + 1e-9, 4000); f = np.array([propagate(v) for v in grid])
    i = np.where(np.sign(f[:-1]) != np.sign(f[1:]))[0][0]
    lo, hi = grid[i + 1], grid[i]
    for _ in range(80):
        mid = (lo + hi) / 2
        if np.sign(propagate(mid)) == np.sign(propagate(hi)): hi = mid
        else: lo = mid
    neff = (lo + hi) / 2

    def field(x):
        x = np.asarray(x, float); out = np.zeros_like(x)
        g = k0 * np.sqrt(neff ** 2 - ncl ** 2); E, D = 1.0, g; z = 0.0
        out[x < 0] = np.exp(g * x[x < 0])
        for t, n in layers:
            sel = (x >= z) & (x < z + t); s = x[sel] - z
            q2 = k0 ** 2 * (n ** 2 - neff ** 2)
            if q2 > 0:
                q = np.sqrt(q2); out[sel] = np.cos(q * s) * E + np.sin(q * s) / q * D
                E, D = np.cos(q * t) * E + np.sin(q * t) / q * D, -q * np.sin(q * t) * E + np.cos(q * t) * D
            else:
                p = np.sqrt(-q2); out[sel] = np.cosh(p * s) * E + np.sinh(p * s) / p * D
                E, D = np.cosh(p * t) * E + np.sinh(p * t) / p * D, p * np.sinh(p * t) * E + np.cosh(p * t) * D
            z += t
        gt = k0 * np.sqrt(neff ** 2 - ncl_top ** 2)
        out[x >= z] = E * np.exp(-gt * (x[x >= z] - z))
        return out
    return neff, field


# illustrative indices at 1550 nm: InP 3.17 (Appendix B), InGaAsP with a 1.25 um gap 3.36, well material 3.55
N_INP, N_Q125, N_WELL = 3.17, 3.36, 3.55
TS = 0.04                 # SCH thickness on each side of the wells (um): with the Chapter 24 ridge this gives Gamma ~ 0.06


def stack_dh(d=0.15):
    return [(d, N_WELL)], [(0, d)]


def stack_sch(ts=0.05, nw=5, tw=0.010, tb=0.010):
    L, act, z = [(ts, N_Q125)], [], ts
    for k in range(nw):
        L.append((tw, N_WELL)); act.append((z, z + tw)); z += tw
        if k < nw - 1: L.append((tb, N_Q125)); z += tb
    L.append((ts, N_Q125))
    return L, act


def confinement(layers, act, ncl=N_INP, ncl_top=None, span=4.0):
    neff, f = slab_te(layers, ncl, ncl_top=ncl_top)
    tot = sum(t for t, _ in layers)
    x = np.linspace(-span, tot + span, 40001); I = f(x) ** 2
    inside = np.zeros_like(x, bool)
    for a, b in act: inside |= (x >= a) & (x < b)
    return neff, f, I[inside].sum() / I.sum(), tot


# ================================================================== Figure 23.1: building the gain spectrum
NOP = 2.7e18          # the Chapter 24 laser's threshold density in this model


def fig_recipe():
    T = 300.0
    E_, g, dF, Eg, P = gain(NOP, T, E_=np.linspace(0.76, 1.06, 301))
    _, g0, _, _, _ = gain(1e10, T, E_=E_)
    kT = P["kT"]; EFc = Eg + P["ec"] * kT; EFv = -P["ev"] * kT
    gp, Ep = peak(NOP)
    print(f"N = {NOP:.2e}: E_Fc - E_c = {1000*(EFc-Eg):.0f} meV, E_Fv - E_v = {1000*EFv:+.0f} meV, dF - Eg = {1000*(dF-Eg):.0f} meV,"
          f" window {HC/dF:.0f}-{HC/Eg:.0f} nm, peak {gp:.0f} /cm at {HC/Ep:.0f} nm")
    print(f"effective densities of states Nc = {Nc(ME,T):.2e}, Nv = {Nc(MV,T):.2e} cm^-3; hole/electron DOS ratio {(MV/ME)**1.5:.1f}")
    fig = plt.figure(figsize=(6.3, 3.5))
    # ---- (a) broken energy axis: conduction band on top, valence band below
    at = fig.add_axes([0.08, 0.50, 0.30, 0.40]); ab = fig.add_axes([0.08, 0.12, 0.30, 0.30], sharex=at)
    Ec_ax = np.linspace(Eg - 0.04, Eg + 0.25, 600); Ev_ax = np.linspace(-0.12, 0.05, 400)
    rc = dos(Ec_ax - Eg, ME) / 1e19; rv = dos(-Ev_ax, MV) / 1e19
    fc = expit(-(Ec_ax - EFc) / kT); fv_hole = expit(-(EFv - Ev_ax) / kT)
    at.fill_betweenx(Ec_ax, 0, rc * fc, color=C1, alpha=0.35, lw=0)
    at.plot(rc, Ec_ax, color=C1, lw=1.0)
    ab.fill_betweenx(Ev_ax, 0, rv * fv_hole, color=C4, alpha=0.35, lw=0)
    ab.plot(rv, Ev_ax, color=C4, lw=1.0)
    nE = np.trapezoid(dos(Ec_ax - Eg, ME) * fc, Ec_ax); pE = np.trapezoid(dos(-Ev_ax, MV) * fv_hole, Ev_ax)
    print(f"check: electrons {nE:.2e}, holes {pE:.2e} cm^-3 (areas of the shaded distributions)")
    for ax, lev, txt in ((at, EFc, "$E_{Fc}$"), (ab, EFv, "$E_{Fv}$")):
        ax.axhline(lev, color=INK, lw=0.8, ls="--")
        ax.text(9.6, lev + (0.006 if ax is at else 0.004), txt, ha="right", va="bottom", fontsize=7.5, color=INK)
    at.axhline(Eg, color=MUTED, lw=0.6); ab.axhline(0, color=MUTED, lw=0.6)
    at.text(9.6, Eg - 0.006, "$E_c$", ha="right", va="top", fontsize=7.5, color=MUTED)
    ab.text(9.6, -0.004, "$E_v$", ha="right", va="top", fontsize=7.5, color=MUTED)
    at.text(2.3, Eg + 0.07, "electrons", color=C1, fontsize=7, ha="left")
    at.text(1.05, Eg + 0.20, "conduction-band\ndensity of states", color=C1, fontsize=6.3, ha="left", va="center")
    ab.text(2.4, -0.062, "holes", color=C4, fontsize=7, ha="left")
    ab.text(9.6, -0.022, "valence-band density of states\nrises off this scale", color=C4, fontsize=6.3, ha="right", va="top")
    at.set_xlim(0, 10); at.set_ylim(Eg - 0.03, Eg + 0.25); ab.set_ylim(-0.11, 0.05)
    at.spines["bottom"].set_visible(False); at.tick_params(axis="x", bottom=False, labelbottom=False)
    ab.set_yticks([-0.1, -0.05, 0, 0.05]); at.set_yticks([0.8, 0.9, 1.0])
    for ax, y in ((at, 0.0), (ab, 1.0)):            # break marks
        ax.plot([-0.03, 0.03], [y - 0.02, y + 0.02], transform=ax.transAxes, color=INK, lw=0.8, clip_on=False)
    ab.set_xlabel("States and carriers (10$^{19}$ cm$^{-3}$ eV$^{-1}$)")
    fig.text(0.005, 0.51, "Energy above the valence-band edge (eV)", rotation=90, va="center", fontsize=8.5, color=INK)
    tag(at, "a")
    # ---- (b) occupation factor, (c) gain
    bx = fig.add_axes([0.53, 0.62, 0.45, 0.28]); cx = fig.add_axes([0.53, 0.12, 0.45, 0.40], sharex=bx)
    Ex = P["Ex"]
    bx.plot(Ex, P["occ"], color=INK, lw=1.4)
    bx.axhline(0, color=MUTED, lw=0.6)
    bx.set_ylim(-1.1, 1.1); bx.set_yticks([-1, 0, 1])
    bx.set_ylabel("$f_c - f_v$")
    bx.tick_params(axis="x", labelbottom=False)
    tag(bx, "b")
    cx.plot(E_, g0, color=MUTED, ls="--", lw=1.1, label="unpumped")
    cx.plot(E_, g, color=C1, lw=1.6, label=f"N = {NOP/1e18:.1f} × 10$^{{18}}$ cm$^{{-3}}$")
    cx.plot(Ep, gp, "o", color=C1, ms=3.5)
    cx.annotate(f"peak {gp:.0f} cm$^{{-1}}$\nat {HC/Ep:.0f} nm", xy=(Ep, gp), xytext=(0.765, 1250), fontsize=6.6, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    cx.axhline(0, color=MUTED, lw=0.6)
    cx.set_ylim(-4500, 1800); cx.set_xlim(0.76, 1.06)
    finish(cx, "Photon energy $h\\nu$ (eV)", "Gain (cm$^{-1}$)", legend=True, loc="upper right")
    tag(cx, "c")
    for ax in (bx, cx):
        ax.axvspan(Eg, dF, color=TEAL, alpha=0.10, lw=0)
        ax.axvline(Eg, color=MUTED, lw=0.6, ls=":"); ax.axvline(dF, color=MUTED, lw=0.6, ls=":")
    bx.text(Eg + 0.004, 0.55, "gain window", fontsize=6.6, color=TEAL)
    bx.text(Eg - 0.004, -0.6, "$E_g$", fontsize=7, color=MUTED, ha="right")
    bx.text(dF + 0.004, 0.55, "$E_{Fc} - E_{Fv}$", fontsize=7, color=MUTED, ha="left")
    bx.text(1.055, -0.55, "absorbs", fontsize=6.6, color=MUTED, ha="right")
    save(fig, "ch23_recipe")
    return dF, Eg


# ================================================================== Figure 23.2: spectra and peak gain against density
def fig_spectra():
    E_ = np.linspace(0.74, 1.00, 521)
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.25, 1]))
    Ns = [1.0e18, 1.3e18, 2.0e18, 2.7e18, 5.0e18]
    cols = [C5, MUTED, C3, C1, C2]
    pk = []
    for N, col in zip(Ns, cols):
        _, g, dF, Eg, _ = gain(N, E_=E_)
        a.plot(HC / E_, g, color=col, lw=1.4 if N != 2.7e18 else 1.9, label=f"{N/1e18:.1f}")
        gp, Ep = peak(N); pk.append((HC / Ep, gp))
        print(f"spectrum N = {N:.1e}: peak {gp:.0f} /cm at {HC/Ep:.0f} nm")
    pk = np.array(pk)
    a.plot(pk[:, 0], pk[:, 1], color=INK, lw=0.7, ls=":", marker="o", ms=2.8, zorder=5)
    for (lp, gpk), N, col in zip(pk, Ns, cols):                 # label each curve at its peak
        if N == 1.3e18:
            a.annotate("1.3 = $N_\\mathrm{tr}$", xy=(lp, gpk), xytext=(1585, 420), fontsize=6.8, color=col, fontweight="bold",
                       arrowprops=dict(arrowstyle="-", color=col, lw=0.6))
            continue
        dx, dy = {1.0e18: (6, -150), 2.0e18: (6, 60), 2.7e18: (6, 70), 5.0e18: (8, 60)}[N]
        a.text(lp + dx, gpk + dy, f"{N/1e18:.1f}", fontsize=6.8, color=col, ha="left", va="bottom" if dy > 0 else "top", fontweight="bold")
    a.axhline(0, color=MUTED, lw=0.6)
    a.set_xlim(1250, 1650); a.set_ylim(-1500, 2000)
    a.text(1645, 1880, "N in 10$^{18}$ cm$^{-3}$", fontsize=6.6, color=INK, ha="right", va="top")
    a.text(1645, 1450, "the peak moves to shorter\nwavelengths as the bands fill", fontsize=6.6, color=MUTED, ha="right", va="top")
    finish(a, "Wavelength (nm)", "Gain (cm$^{-1}$)")
    tag(a, "a")
    # (b) peak gain against N on a log axis: a logarithmic fit is a straight line
    Ng = np.geomspace(1.0e18, 6.0e18, 26)
    gp = np.array([peak(N)[0] for N in Ng])
    sel = (Ng >= 2.0e18) & (Ng <= 4.0e18)
    s, c0 = np.polyfit(np.log(Ng[sel]), gp[sel], 1)
    Ntr_fit = np.exp(-c0 / s)
    print(f"log fit of the model, 2-4e18: g0 = {s:.0f} /cm, Ntr = {Ntr_fit:.2e}; at 2.7e18 slope g0/N = {s/2.7e18:.2e} cm^2")
    b.plot(Ng / 1e18, gp, "o", color=C1, ms=3, label="bulk model (Fig. 23.1)", zorder=4)
    xx = np.geomspace(1.0e18, 6.0e18, 100)
    b.plot(xx / 1e18, s * np.log(xx / Ntr_fit), color=C1, lw=0.9, ls="--", label=f"fit {s:.0f} ln(N/{Ntr_fit/1e18:.2f})")
    b.plot(xx / 1e18, 1500 * np.log(xx / 2e18), color=C2, lw=1.4, label="laser demo: 1500 ln(N/2.0)")
    Nth_demo = 2e18 * np.exp(725 / 1500); Nth_model = n_for(725)
    print(f"725 /cm: model {Nth_model:.3e}, demo fit {Nth_demo:.3e}; differential gain there: model"
          f" {(peak(Nth_model * 1.03)[0] - peak(Nth_model * 0.97)[0]) / (0.06 * Nth_model):.2e}, demo fit {1500 / Nth_demo:.2e} cm^2")
    b.axhline(725, color=MUTED, lw=0.6, ls=":")
    b.text(1.03, 790, "725 cm$^{-1}$ (Ch. 24 laser)", fontsize=6.4, color=MUTED)
    b.plot([Nth_model / 1e18, Nth_demo / 1e18], [725, 725], "s", color=INK, ms=3.2, zorder=5)
    b.annotate(f"{Nth_model/1e18:.1f}", xy=(Nth_model / 1e18, 725), xytext=(Nth_model / 1e18 - 0.25, 300), fontsize=6.6, ha="center",
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.annotate(f"{Nth_demo/1e18:.1f}", xy=(Nth_demo / 1e18, 725), xytext=(Nth_demo / 1e18 + 0.4, 300), fontsize=6.6, ha="center",
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    b.set_xscale("log"); b.set_xlim(1.0, 6.0); b.set_ylim(-500, 2200)
    b.set_xticks([1, 1.3, 2, 3, 4, 6]); b.set_xticklabels(["1", "1.3", "2", "3", "4", "6"]); b.minorticks_off()
    b.axhline(0, color=MUTED, lw=0.6)
    finish(b, "Carrier density N (10$^{18}$ cm$^{-3}$, log scale)", "Peak gain (cm$^{-1}$)", legend=True, loc="upper left")
    b.legend(loc="upper left", fontsize=6.3, handlelength=1.6)
    tag(b, "b")
    fig.tight_layout(w_pad=1.8)
    save(fig, "ch23_spectra")


# ================================================================== Figure 23.3: heterostructures
def _step(xs, y):
    """A piecewise-constant profile as its corner points only (keeps the SVG small)."""
    k = np.nonzero(np.diff(y))[0]
    xe = (xs[k] + xs[k + 1]) / 2
    return np.r_[xs[0], np.repeat(xe, 2), xs[-1]], np.repeat(np.r_[y[0], y[k + 1]], 2)


def fig_hetero():
    fig = plt.figure(figsize=(6.3, 3.8))
    cases = [("a", "Double heterostructure (150 nm bulk)", *stack_dh(0.15)), ("b", "Separate confinement, 5 quantum wells", *stack_sch(TS))]
    res = []
    for k, (tg, title, layers, act) in enumerate(cases):
        neff, f, G, tot = confinement(layers, act)
        res.append(G)
        print(f"{title}: total core {1000*tot:.0f} nm, active {1000*sum(b-a for a,b in act):.0f} nm, n_eff {neff:.4f}, Gamma {G:.3f}")
        x0 = -tot / 2                                     # centre the stack on x = 0
        xs = np.linspace(-1.0, 1.0, 8001); I = f(xs - x0) ** 2; I /= I.max()
        nprof = np.full_like(xs, N_INP); z = x0
        for t, n in layers:
            nprof[(xs >= z) & (xs < z + t)] = n; z += t
        # ---- band diagram (schematic energies, positions to scale but zoomed to +-0.3 um)
        ab = fig.add_axes([0.07 + 0.49 * k, 0.56, 0.42, 0.34])
        Egx = np.where(nprof == N_INP, 1.34, np.where(nprof == N_Q125, HC / 1250, 0.80))
        Ec = 0.40 * (Egx - 0.80) + 0.80; Ev = -0.60 * (Egx - 0.80)       # 40 % of each gap step in the conduction band
        ab.plot(*_step(xs, Ec), color=INK, lw=1.1); ab.plot(*_step(xs, Ev), color=INK, lw=1.1)
        for a_, b_ in act:
            xa, xb = x0 + a_, x0 + b_
            if b_ - a_ > 0.05:
                for xx in np.linspace(xa + 0.02, xb - 0.02, 4):
                    ab.plot(xx, 0.85, "o", ms=3.4, color=C1); ab.plot(xx, -0.05, "o", ms=3.4, mfc="white", mec=C4, mew=0.9)
            else:
                ab.plot([xa, xb], [0.87, 0.87], color=C1, lw=1.0); ab.plot([xa, xb], [-0.08, -0.08], color=C4, lw=1.0)
                ab.plot((xa + xb) / 2, 0.92, "o", ms=2.4, color=C1); ab.plot((xa + xb) / 2, -0.13, "o", ms=2.4, mfc="white", mec=C4, mew=0.8)
        ab.text(-0.29, 1.13, "n-InP", fontsize=6.6, color=INK); ab.text(0.29, 1.13, "p-InP", fontsize=6.6, color=INK, ha="right")
        ab.text(-0.29, 0.88, "$E_c$", fontsize=7, color=INK); ab.text(-0.29, -0.36, "$E_v$", fontsize=7, color=INK)
        if k == 0:
            ab.text(0.10, 0.62, "electrons", fontsize=6.4, color=C1); ab.text(0.10, 0.10, "holes", fontsize=6.4, color=C4)
        else:
            ab.annotate("SCH", xy=(x0 + TS / 2, 0.98), xytext=(-0.17, 0.62), fontsize=6.4, color=MUTED, ha="center",
                        arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
            ab.text(0.11, 0.62, "$n$ = 1 levels", fontsize=6.4, color=C1); ab.text(0.11, 0.08, "$n$ = 1 levels", fontsize=6.4, color=C4)
        ab.set_xlim(-0.3, 0.3); ab.set_ylim(-0.45, 1.25)
        ab.set_yticks([]); ab.spines["left"].set_visible(False)
        ab.set_xticks([-0.2, 0, 0.2]); ab.tick_params(axis="x", labelsize=6.5)
        ab.grid(False)
        ab.set_title(title, fontsize=7.6, color=INK)
        ab.text(0.3, -0.45, "energies schematic", fontsize=5.8, color=MUTED, style="italic", ha="right", va="bottom")
        tag(ab, tg)
        # ---- index and mode, wider window
        am = fig.add_axes([0.07 + 0.49 * k, 0.12, 0.42, 0.33])
        an = am.twinx()
        Xn, Yn = _step(xs, nprof)
        an.fill_between(Xn, 3.0, Yn, color="#D9DEE7", lw=0, zorder=0)
        an.plot(Xn, Yn, color=MUTED, lw=0.5)
        an.set_ylim(3.0, 3.75); an.set_yticks([3.17, 3.36, 3.55]); an.tick_params(labelsize=6.5)
        an.spines["right"].set_visible(True); an.grid(False)
        if k == 1: an.set_ylabel("Index", fontsize=7.5)
        am.set_zorder(an.get_zorder() + 1); am.patch.set_visible(False)
        for a_, b_ in act:
            am.axvspan(x0 + a_, x0 + b_, color=RED, alpha=0.30, lw=0)
        am.fill_between(xs[::16], 0, I[::16], color=C3, alpha=0.20, lw=0); am.plot(xs[::16], I[::16], color=C3, lw=1.3)
        am.set_xlim(-1.0, 1.0); am.set_ylim(0, 1.15); am.set_yticks([0, 0.5, 1])
        am.text(-0.96, 1.02, f"Γ = {G:.2f}", fontsize=7.2, color=INK, va="center")
        am.text(0.30, 0.55, "mode\nintensity", fontsize=6.4, color=C3)
        am.text(0.62, 0.12, "index", fontsize=6.4, color=MUTED)
        finish(am, "Position across the layers (µm)", "Intensity" if k == 0 else None)
    save(fig, "ch23_hetero")
    return res


# ================================================================== Figure 23.4: density of states
def fig_dos():
    Lz = 10e-9
    E = np.linspace(0, 0.40, 2001)
    rb = dos(E, ME) / 1e19
    E1 = (HBAR * np.pi / Lz) ** 2 / (2 * ME * M0) / QE
    step = ME * M0 / (np.pi * HBAR ** 2 * Lz) * QE / 1e6 / 1e19        # per subband, both spins, per unit volume
    nsub = np.floor(np.sqrt(np.maximum(E, 0) / E1)).astype(int)
    rq = nsub * step
    print(f"quantum well Lz = 10 nm, m_e = {ME} m0: E1 = {1000*E1:.1f} meV (infinite well), E2 = {4000*E1:.0f} meV,"
          f" step {step:.2f} x 1e19 cm^-3 eV^-1; bulk DOS at E1: {dos(E1, ME)/1e19:.2f}")
    fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.5), sharey=True)
    a, b, c = axs
    a.plot(1000 * E, rb, color=C1)
    a.fill_between(1000 * E, 0, rb, color=C1, alpha=0.12, lw=0)
    a.set_title("Bulk", fontsize=7.6, color=INK)
    b.plot(1000 * E, rb, color=MUTED, ls="--", lw=0.9, label="bulk")
    b.plot(1000 * E, rq, color=C1, label="10 nm well")
    b.fill_between(1000 * E, 0, rq, color=C1, alpha=0.12, lw=0)
    b.text(1000 * E1 + 6, step + 0.12, "full step at\nthe band edge", fontsize=6.4, color=INK)
    b.text(1000 * 4 * E1 - 4, 2 * step + 0.12, "$n$ = 2", fontsize=6.4, color=INK, ha="right")
    b.legend(loc="upper left", fontsize=6.3, handlelength=1.4)
    b.set_title("Quantum well", fontsize=7.6, color=INK)
    # quantum dots: discrete levels (ground state 2 states, first excited 4), broadened by the size spread (illustrative)
    lev = [(0.06, 2), (0.13, 4)]
    sig = 0.012
    rd = sum(w * np.exp(-(E - e0) ** 2 / (2 * sig ** 2)) for e0, w in lev)
    rd *= 1.2 / rd.max() * 2.0
    for e0, w in lev:
        c.plot([1000 * e0] * 2, [0, 3.6 * w / 4], color=INK, lw=1.0)
    c.plot(1000 * E, rd, color=C1)
    c.fill_between(1000 * E, 0, rd, color=C1, alpha=0.12, lw=0)
    c.text(145, 3.0, "one dot:\nsharp levels", fontsize=6.3, color=INK)
    c.text(185, 1.3, "ensemble:\nbroadened by\nthe size spread", fontsize=6.3, color=C1)
    c.set_title("Quantum dots (illustrative)", fontsize=7.6, color=INK)
    for ax, t in zip(axs, "abc"):
        ax.set_xlim(0, 400); ax.set_ylim(0, 4.2)
        tag(ax, t)
    b.set_xlabel("Energy above the band edge (meV)")
    a.set_ylabel("States (10$^{19}$ cm$^{-3}$ eV$^{-1}$)")
    c.text(395, 0.08, "arbitrary units", fontsize=6.0, color=MUTED, style="italic", ha="right", va="bottom")
    for ax, kind in zip(axs, ("bulk", "well", "dot")):                 # small sketch of the structure
        ins = ax.inset_axes({"bulk": [0.58, 0.06, 0.36, 0.32], "well": [0.38, 0.06, 0.34, 0.30], "dot": [0.62, 0.64, 0.34, 0.32]}[kind])
        ins.set_axis_off(); ins.set_xlim(0, 1); ins.set_ylim(0, 1); ins.set_aspect("equal")
        if kind == "bulk":
            ins.add_patch(Rectangle((0.2, 0.15), 0.6, 0.6, fc=MAT["q"], ec="none"))
        elif kind == "well":
            ins.add_patch(Rectangle((0.05, 0.25), 0.9, 0.5, fc=MAT["inp"], ec="none"))
            ins.add_patch(Rectangle((0.05, 0.46), 0.9, 0.08, fc=MAT["q"], ec="none"))
        else:
            ins.add_patch(Rectangle((0.05, 0.25), 0.9, 0.5, fc=MAT["inp"], ec="none"))
            for xx in (0.2, 0.42, 0.62, 0.82):
                ins.add_patch(Ellipse((xx, 0.5), 0.12, 0.08, fc=MAT["q"], ec="none"))
    fig.tight_layout(w_pad=0.8)
    save(fig, "ch23_dos")


# ================================================================== Figure 23.5: band gap against lattice constant
# Vurgaftman, Meyer and Ram-Mohan (2001): lattice constant at 300 K (A); (E0, alpha meV/K, beta K) for Gamma, X, L
BIN = {
    "GaAs": (5.65325, (1.519, 0.5405, 204), (1.981, 0.460, 204), (1.815, 0.605, 204)),
    "AlAs": (5.6611, (3.099, 0.885, 530), (2.24, 0.70, 530), (2.46, 0.605, 204)),
    "InAs": (6.0583, (0.417, 0.276, 93), (1.433, 0.276, 93), (1.133, 0.276, 93)),
    "InP": (5.8697, (1.4236, 0.363, 162), (2.384 - 0.37 * 0.3, 0, 1), (2.014 - 0.363 * 0.3, 0, 1)),
    "GaP": (5.4505, (2.777, 0, 1), (2.35, 0.5771, 372), (2.72, 0.5771, 372)),
    "GaSb": (6.0959, (0.812, 0.417, 140), (1.141, 0.475, 94), (0.875, 0.597, 140)),
    "AlSb": (6.1355, (2.386, 0.42, 140), (1.696, 0.39, 140), (2.329, 0.58, 140)),
    "InSb": (6.4794, (0.235, 0.32, 170), (0.63, 0, 1), (0.93, 0, 1)),
}
# ternary bowing parameters (Gamma, X, L); for AlGaAs and AlGaSb the Gamma bowing depends on the Al fraction
TERN = [("InAs", "GaAs", "InGaAs", (0.477, 1.4, 0.33)), ("InAs", "AlAs", "InAlAs", (0.70, 0.0, 0.0)),
        ("InAs", "InP", "InAsP", (0.10, 0.27, 0.27)), ("InP", "GaP", "InGaP", (0.65, 0.20, 1.03)),
        ("GaAs", "AlAs", "AlGaAs", ("algaas", 0.055, 0.0)), ("GaSb", "AlSb", "AlGaSb", ("algasb", 0.0, 0.0))]


def egv(p, T=300.0):
    E0, al, be = p
    return E0 - al * 1e-3 * T ** 2 / (T + be)


def bin_gaps(name):
    a, G, X, L = BIN[name]
    return a, egv(G), egv(X), egv(L)


def tern(A, B, bows, x):
    """Alloy A_x B_(1-x): lattice constant and the (Gamma, X, L) gaps with bowing."""
    aA, *gA = bin_gaps(A); aB, *gB = bin_gaps(B)
    a = x * aA + (1 - x) * aB
    out = []
    for i in range(3):
        bw = bows[i]
        if bw == "algaas": bw = -0.127 + 1.310 * (1 - x)            # x here is the GaAs fraction; Vurgaftman's x is Al
        if bw == "algasb": bw = -0.044 + 1.22 * (1 - x)
        out.append(x * gA[i] + (1 - x) * gB[i] - bw * x * (1 - x))
    return a, np.array(out)


def fig_alloys():
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    x = np.linspace(0, 1, 401)
    for A, B, name, bows in TERN:
        if name is None: continue
        pts = [tern(A, B, bows, xi) for xi in x]
        a = np.array([p[0] for p in pts]); gs = np.array([p[1] for p in pts]); eg = gs.min(axis=1); direct = gs[:, 0] <= eg + 1e-9
        for flag, ls in ((True, "-"), (False, "--")):
            yy = np.where(direct == flag, eg, np.nan)
            ax.plot(a, yy, color=MUTED, lw=1.0, ls=ls, zorder=2)
    for name in BIN:
        a, G, X, L = bin_gaps(name); eg = min(G, X, L); d = G <= eg + 1e-9
        ax.plot(a, eg, "o", ms=5, mfc=INK if d else "white", mec=INK, mew=1.0, zorder=5)
        off = {"GaAs": (-0.02, 0.07, "right"), "AlAs": (0.03, 0.06, "left"), "InAs": (0.03, -0.09, "left"), "InP": (0.045, 0.07, "left"),
               "GaP": (0.03, 0.05, "left"), "GaSb": (0.03, -0.1, "left"), "AlSb": (0.03, 0.05, "left"), "InSb": (-0.03, 0.06, "right")}[name]
        ax.text(a + off[0], eg + off[1], name, fontsize=7, color=INK, ha=off[2], zorder=6)
        print(f"{name}: a = {a:.4f} A, Eg(Gamma) {G:.3f}, X {X:.3f}, L {L:.3f} eV ({'direct' if d else 'indirect'})")
    # lattice matching to InP and GaAs
    aInP, *_ = bin_gaps("InP"); aGaAs, *_ = bin_gaps("GaAs")
    for aa, lab in ((aInP, "InP lattice"), (aGaAs, "GaAs lattice")):
        ax.axvline(aa, color=MUTED, lw=0.6, ls=":", zorder=1)
        ax.text(aa + 0.008, 2.93, lab, fontsize=6.3, color=MUTED, rotation=90, va="top")
    def matched(A, B, bows, a0):
        aA = bin_gaps(A)[0]; aB = bin_gaps(B)[0]; xm = (a0 - aB) / (aA - aB)
        return xm, tern(A, B, bows, xm)[1].min()
    xg, eInGaAs = matched("InAs", "GaAs", TERN[0][3], aInP)
    xa, eInAlAs = matched("InAs", "AlAs", TERN[1][3], aInP)
    eInP = bin_gaps("InP")[1]
    print(f"on InP: In{xg:.3f}Ga{1-xg:.3f}As {eInGaAs:.3f} eV ({HC/eInGaAs:.0f} nm); In{xa:.3f}Al{1-xa:.3f}As {eInAlAs:.3f} eV;"
          f" InP {eInP:.3f} eV ({HC/eInP:.0f} nm)")
    ax.plot([aInP - 0.012] * 2, [eInGaAs, eInP], color=C1, lw=4.0, solid_capstyle="butt", zorder=4, alpha=0.85)
    ax.plot([aInP + 0.012] * 2, [eInGaAs, eInAlAs], color=C2, lw=4.0, solid_capstyle="butt", zorder=4, alpha=0.85)
    ax.annotate("InGaAsP\non InP", xy=(aInP - 0.02, 1.10), xytext=(aInP - 0.17, 1.12), fontsize=6.8, color=C1, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=C1, lw=0.7))
    ax.annotate("AlGaInAs\non InP", xy=(aInP + 0.02, 1.20), xytext=(aInP + 0.10, 1.55), fontsize=6.8, color=C2, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=C2, lw=0.7))
    # AlGaAs on GaAs (850 nm VCSELs) and InAs dots on GaAs (strained, 1310 nm)
    eGaAs = bin_gaps("GaAs")[1]
    ax.plot(aGaAs, HC / 1310, "*", ms=8, color=C4, zorder=6)
    ax.annotate("InAs dots on GaAs\n(strained), 1310 nm", xy=(aGaAs, HC / 1310), xytext=(aGaAs - 0.03, 0.42), fontsize=6.6,
                color=C4, ha="center", arrowprops=dict(arrowstyle="-", color=C4, lw=0.6))
    for lam, lab in ((1310, "1310 nm"), (1550, "1550 nm"), (850, "850 nm")):
        ax.axhline(HC / lam, color=C3, lw=0.7, ls="--", zorder=1)
        ax.text(6.52, HC / lam + 0.015, lab, fontsize=6.4, color=C3, ha="right", va="bottom")
    ax.text(5.635, 1.72, "AlGaAs", fontsize=6.5, color=MUTED, rotation=87, ha="right")
    ax.text(5.87, 0.50, "InGaAs", fontsize=6.5, color=MUTED, rotation=-33)
    ax.set_xlim(5.4, 6.55); ax.set_ylim(0, 3.0)
    sec = ax.secondary_yaxis("right", functions=(lambda e: HC / 1000 / np.maximum(e, 1e-3), lambda l: HC / 1000 / np.maximum(l, 1e-3)))
    sec.set_yticks([0.5, 0.6, 0.8, 1.0, 1.3, 1.55, 2.0, 3.0, 5.0]); sec.set_ylabel("Wavelength (µm)")
    finish(ax, "Lattice constant (Å)", "Band gap at 300 K (eV)")
    ax.text(5.41, 0.06, "filled: direct gap   open: indirect   dashed: indirect alloy", fontsize=6.2, color=MUTED, va="bottom")
    save(fig, "ch23_alloys")


# ================================================================== Figure 23.6: recombination
A_, B_, C_ = 1e8, 1e-10, 3e-29
NTH = 2e18 * np.exp(725 / 1500)          # the Chapter 24 laser's threshold density (laser demo's log fit)


def fig_abc():
    N = np.geomspace(1e17, 1e19, 400)
    RA, RB, RC = A_ * N, B_ * N ** 2, C_ * N ** 3; R = RA + RB + RC
    d, eta = 50e-7, 0.8                           # active thickness (cm) and injection efficiency of the Chapter 24 laser
    Rth = A_ * NTH + B_ * NTH ** 2 + C_ * NTH ** 3
    print(f"N_th = {NTH:.3e}: AN {A_*NTH:.2e}, BN^2 {B_*NTH**2:.2e}, CN^3 {C_*NTH**3:.2e} (ratio "
          f"{A_*NTH/1e27:.2f} : {B_*NTH**2/1e27:.2f} : {C_*NTH**3/1e27:.2f} x 1e27); R {Rth:.2e} cm^-3 s^-1;"
          f" tau_n = N/R {NTH/Rth*1e9:.2f} ns; J_th = q d R/eta = {1.602e-19*d*Rth/eta:.0f} A/cm2;"
          f" radiative fraction {B_*NTH**2/Rth:.2f}, Auger {C_*NTH**3/Rth:.2f}, SRH {A_*NTH/Rth:.2f}")
    j = np.argmax(RB / R); print(f"radiative fraction peaks at {RB[j]/R[j]:.2f} near N = {N[j]:.2e}; B = C crossover at {B_/C_:.2e}")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    a.loglog(N, RA, color=C3, label="$AN$ (defects)"); a.loglog(N, RB, color=C1, label="$BN^2$ (radiative)")
    a.loglog(N, RC, color=C4, label="$CN^3$ (Auger)"); a.loglog(N, R, color=INK, lw=1.0, ls="--", label="total $R(N)$")
    a.axvline(NTH, color=MUTED, lw=0.6, ls=":")
    a.plot(NTH, Rth, "o", color=INK, ms=3.5)
    a.annotate(f"$N_\\mathrm{{th}}$ = {NTH/1e18:.2f} × 10$^{{18}}$\n$N/R$ = {NTH/Rth*1e9:.2f} ns", xy=(NTH, Rth),
               xytext=(1.3e17, 6e27), fontsize=6.6, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    a.set_xlim(1e17, 1e19); a.set_ylim(1e24, 1e29)
    finish(a, "Carrier density N (cm$^{-3}$)", "Recombination rate (cm$^{-3}$ s$^{-1}$)", legend=True, loc="lower right")
    a.legend(loc="lower right", fontsize=6.4)
    sec = a.secondary_yaxis("right", functions=(lambda r: 1.602e-19 * d * r / eta / 1e3, lambda jj: jj * 1e3 * eta / (1.602e-19 * d)))
    sec.set_ylabel("$qdR/\\eta_i$ (kA/cm$^2$), d = 50 nm", fontsize=7.2)
    tag(a, "a")
    Nl = np.linspace(0.2e18, 6e18, 300)
    fA, fB, fC = (A_ * Nl) / (A_ * Nl + B_ * Nl ** 2 + C_ * Nl ** 3), (B_ * Nl ** 2) / (A_ * Nl + B_ * Nl ** 2 + C_ * Nl ** 3), None
    fC = 1 - fA - fB
    b.stackplot(Nl / 1e18, fA, fB, fC, colors=[C3, C1, C4], alpha=0.30, lw=0)
    b.plot(Nl / 1e18, fA, color=C3, lw=1.0); b.plot(Nl / 1e18, fA + fB, color=C1, lw=1.0)
    b.text(0.7, 0.30, "defects", color=C3, fontsize=7, ha="center"); b.text(2.0, 0.50, "radiative", color=C1, fontsize=7, ha="center")
    b.text(4.7, 0.85, "Auger", color=C4, fontsize=7, ha="center")
    b.axvline(NTH / 1e18, color=INK, lw=0.7, ls=":"); b.text(NTH / 1e18 + 0.08, 0.04, "$N_\\mathrm{th}$", fontsize=7, color=INK)
    b.set_xlim(0.2, 6); b.set_ylim(0, 1)
    finish(b, "Carrier density N (10$^{18}$ cm$^{-3}$)", "Share of recombination")
    tag(b, "b")
    fig.tight_layout(w_pad=1.6)
    save(fig, "ch23_abc")


if __name__ == "__main__":
    only = sys.argv[1:]                    # e.g. "python figsrc/ch23_figs.py fig_dos" redraws one figure
    if not only:
        E_, g, dF, Eg, _ = gain(1e10)
        i = np.argmin(abs(E_ - (Eg + 0.05))); print(f"unpumped absorption at Eg + 50 meV: {-g[i]:.0f} /cm")
        lo, hi = 3e17, 3e18
        for _ in range(40):
            mid = (lo + hi) / 2
            if gain(mid)[1].max() < 0: lo = mid
            else: hi = mid
        print(f"transparency density {lo:.2e} cm^-3; dg/dN at 3e18 {(peak(3.1e18)[0]-peak(2.9e18)[0])/0.2e18:.2e} cm^2")
        print(f"N for 1000 /cm: 300 K {n_for(1000):.3e}, 340 K {n_for(1000, 340):.3e}")
    for fn in (fig_recipe, fig_spectra, fig_hetero, fig_dos, fig_alloys, fig_abc):
        if not only or fn.__name__ in only:
            fn()
