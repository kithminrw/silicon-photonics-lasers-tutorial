"""Figures and numbers for Part II (Chapters 5-8). Run: .venv/bin/python figsrc/part2_figs.py
Chapter 6's femwell figure needs figsrc/ch06_sweep.json (from ch06_sweep.py)."""
import json, os
import numpy as np
from figstyle import *

N_SI, N_OX = 3.476, 1.444


# ------------------------------------------------------------------ exact asymmetric slab (TE and TM)
def slab_F(ne, n1, n2, n3, d, lam, tm):
    k0 = 2 * np.pi / lam
    ka = k0 * np.sqrt(max(n1**2 - ne**2, 1e-18)); g2 = k0 * np.sqrt(max(ne**2 - n2**2, 0)); g3 = k0 * np.sqrt(max(ne**2 - n3**2, 0))
    p2, p3 = (g2 * n1**2 / n2**2, g3 * n1**2 / n3**2) if tm else (g2, g3)
    return ka * d - np.arctan(p2 / ka) - np.arctan(p3 / ka)


def slab_modes(n1, n2, n3, d, lam, tm=False):
    lo, hi, out = max(n2, n3) + 1e-9, n1 - 1e-9, []
    Flo = slab_F(lo, n1, n2, n3, d, lam, tm)
    m = 0
    while Flo > m * np.pi and m < 40:
        a, b = lo, hi
        for _ in range(70):
            c = (a + b) / 2
            if slab_F(c, n1, n2, n3, d, lam, tm) > m * np.pi: a = c
            else: b = c
        out.append((a + b) / 2); m += 1
    return out


def fig_bV():
    """Universal b-V curves of the symmetric slab, TE modes m = 0..3."""
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    V = np.linspace(0.01, 12, 600)
    for m in range(4):
        bs = []
        for v in V:   # symmetric TE: V sqrt(1-b) = m pi + 2 atan(sqrt(b/(1-b)))
            f = lambda b: v * np.sqrt(1 - b) - m * np.pi - 2 * np.arctan(np.sqrt(b / (1 - b)))
            if f(1e-12) <= 0: bs.append(np.nan); continue
            a, c = 1e-12, 1 - 1e-12
            for _ in range(60):
                mid = (a + c) / 2
                if f(mid) > 0: a = mid
                else: c = mid
            bs.append((a + c) / 2)
        ax.plot(V, bs, color=SERIES[m], label=f"TE{m}")
    v0 = 2 * np.pi / 1.55 * 0.22 * np.sqrt(N_SI**2 - N_OX**2)
    b0 = (slab_modes(N_SI, N_OX, N_OX, 0.22, 1.55)[0]**2 - N_OX**2) / (N_SI**2 - N_OX**2)
    ax.plot(v0, b0, "o", color=INK, ms=5); ax.annotate("220 nm Si\nat 1550 nm", (v0, b0), xytext=(8, -26), textcoords="offset points", fontsize=7)
    for m in range(1, 4): ax.axvline(m * np.pi, color=MUTED, lw=0.6, ls=":")
    ax.set_xlim(0, 12); ax.set_ylim(0, 1)
    finish(ax, "V = k₀d √(n₁² − n₂²)", "b = (n_eff² − n₂²)/(n₁² − n₂²)", legend=True, loc="lower right")
    savefig(fig, "ch05_bV")
    print(f"220 nm Si slab at 1550: V = {v0:.3f}, b = {b0:.3f}")


def fig_neff_thickness():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    ds = np.linspace(0.02, 1.0, 300)
    for tm, ls in ((False, "-"), (True, "--")):
        curves = {}
        for d in ds:
            for m, ne in enumerate(slab_modes(N_SI, N_OX, N_OX, d, 1.55, tm)):
                curves.setdefault(m, ([], []))[0].append(d); curves[m][1].append(ne)
        for m, (x, y) in curves.items():
            if m < 3: a.plot(x, y, ls, color=SERIES[m], label=("TM" if tm else "TE") + str(m))
    a.axvline(0.22, color=MUTED, lw=0.7, ls=":")
    a.set_xlim(0, 1); a.set_ylim(N_OX, N_SI)
    finish(a, "Silicon thickness d (µm)", "Effective index", legend=True, loc="lower right")
    # group index of TE0 and TM0 against thickness (waveguide + material dispersion)
    def nsi(l):
        l1 = 1.1071; return np.sqrt(11.6858 + 0.939816 / l**2 + 0.00810461 * l1**2 / (l**2 - l1**2))
    def nox(l):
        return np.sqrt(1 + 0.6961663 * l**2 / (l**2 - 0.0684043**2) + 0.4079426 * l**2 / (l**2 - 0.1162414**2) + 0.8974794 * l**2 / (l**2 - 9.896161**2))
    for tm, col in ((False, C1), (True, C2)):
        gs = []
        for d in ds:
            n = lambda l: (slab_modes(nsi(l), nox(l), nox(l), d, l, tm) or [np.nan])[0]
            gs.append(n(1.55) - 1.55 * (n(1.555) - n(1.545)) / 0.01)
        b.plot(ds, gs, color=col, label="TM0" if tm else "TE0")
    b.axhline(3.59, color=MUTED, lw=0.7, ls=":"); b.text(0.62, 3.62, "bulk Si, 3.59", fontsize=7, color=MUTED)
    b.axvline(0.22, color=MUTED, lw=0.7, ls=":")
    b.set_xlim(0, 1); b.set_ylim(2.5, 5)
    finish(b, "Silicon thickness d (µm)", "Group index n_g", legend=True, loc="upper right")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.5)
    savefig(fig, "ch05_neff")


def numbers():
    print("\nslab numbers at 1550 nm (Si core in oxide):")
    for d in (0.22, 0.3, 0.34):
        te, tm = slab_modes(N_SI, N_OX, N_OX, d, 1.55), slab_modes(N_SI, N_OX, N_OX, d, 1.55, True)
        print(f"  d = {d}: TE {np.round(te, 4)}  TM {np.round(tm, 4)}")
    te_cut = 1.55 / (2 * np.sqrt(N_SI**2 - N_OX**2))
    print(f"  TE1/TM1 cut-off (symmetric): d = lambda/(2 NA) = {1000*te_cut:.0f} nm")
    print(f"  in air cover (asym): TE0 at 220 nm = {slab_modes(N_SI, N_OX, 1.0, 0.22, 1.55)[0]:.4f}; TM0 = {slab_modes(N_SI, N_OX, 1.0, 0.22, 1.55, True)}")
    print(f"  SiN 400 nm in oxide: TE0 = {slab_modes(1.996, N_OX, N_OX, 0.4, 1.55)[0]:.4f}, TM0 = {slab_modes(1.996, N_OX, N_OX, 0.4, 1.55, True)}")
    print(f"  SiN TE1 cut-off: {1000*1.55/(2*np.sqrt(1.996**2-N_OX**2)):.0f} nm")
    # confinement and decay of TE0 at 220 nm
    ne = slab_modes(N_SI, N_OX, N_OX, 0.22, 1.55)[0]; k0 = 2 * np.pi / 1.55
    ka, g = k0 * np.sqrt(N_SI**2 - ne**2), k0 * np.sqrt(ne**2 - N_OX**2)
    print(f"  TE0 220 nm: n_eff {ne:.4f}, kappa {ka:.3f}/um, gamma {g:.3f}/um, 1/gamma {1000/g:.0f} nm, angle {np.degrees(np.arcsin(ne/N_SI)):.1f} deg")
    x = np.linspace(-3, 3.22, 20001); d = 0.22
    E = np.where(x < 0, np.cos(ka * d / 2) * np.exp(g * (x)), np.where(x <= d, np.cos(ka * (x - d / 2)), np.cos(ka * d / 2) * np.exp(-g * (x - d))))
    print(f"  confinement (TE0, 220 nm): {np.sum(E[(x>=0)&(x<=d)]**2)/np.sum(E**2):.3f}")


# ------------------------------------------------------------------ Chapter 6: femwell width sweep
def fig_strip():
    p = os.path.join(os.path.dirname(__file__), "ch06_sweep.json")
    if not os.path.exists(p):
        print("no ch06_sweep.json yet"); return
    S = json.load(open(p)); W = np.array(S["widths"])
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    def track(key, want_te, idx):
        y = []
        for ms in S[key]:
            c = [n for n, te in ms if (te > 0.5) == want_te]
            y.append(c[idx] if len(c) > idx else np.nan)
        return np.array(y)
    for want_te, idx, col, lab, ls in ((True, 0, C1, "TE0", "-"), (False, 0, C2, "TM0", "-"), (True, 1, C3, "TE1", "-"), (False, 1, C4, "TM1", "--")):
        a.plot(W, track("neff1550", want_te, idx), ls, color=col, label=lab, marker="o", ms=2.5)
    a.axhline(1.444, color=MUTED, lw=0.7, ls=":"); a.axvline(0.5, color=MUTED, lw=0.7, ls=":")
    a.set_xlim(0.25, 1.0); a.set_ylim(1.4, 3.0)
    finish(a, "Width (µm)", "Effective index at 1550 nm", legend=True, loc="upper left")
    b.plot(W, S["ng_te1550"], color=C1, marker="o", ms=2.5, label="TE0, 1550 nm")
    b.plot(W, S["ng_tm1550"], color=C2, marker="o", ms=2.5, label="TM0, 1550 nm")
    b.plot(W, S["ng_te1310"], color=C3, marker="o", ms=2.5, label="TE0, 1310 nm")
    b.axvline(0.5, color=MUTED, lw=0.7, ls=":"); b.set_xlim(0.25, 1.0); b.set_ylim(3.0, 5.2)
    finish(b, "Width (µm)", "Group index", legend=True, loc="upper right")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.5)
    savefig(fig, "ch06_strip")
    i5 = list(np.round(W, 3)).index(0.5)
    print("\nfemwell, 500 x 220 nm:", S["neff1550"][i5], "ng TE", S["ng_te1550"][i5], "ng TM", S["ng_tm1550"][i5], "ng TE 1310", S["ng_te1310"][i5])
    te1 = track("neff1550", True, 1)
    first = W[np.where(~np.isnan(te1))[0][0]] if np.any(~np.isnan(te1)) else None
    print("TE1 first guided at width (1550):", first)


if __name__ == "__main__":
    fig_bV(); fig_neff_thickness(); numbers(); fig_strip()
