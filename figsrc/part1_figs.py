"""Figures for Part I (Chapters 2-4). Run: .venv/bin/python figsrc/part1_figs.py

Prints the numbers quoted in the text (indices, group indices, coupling efficiencies, fibre parameters).
"""
import numpy as np
from matplotlib.patches import Rectangle, Polygon
from figstyle import *

# ------------------------------------------------------------------ Sellmeier models (lambda in um)
def n_si(l):       # H. H. Li (1980), 293 K, valid 1.2-14 um
    l1 = 1.1071
    return np.sqrt(11.6858 + 0.939816 / l**2 + 0.00810461 * l1**2 / (l**2 - l1**2))

def n_sio2(l):     # I. H. Malitson (1965), fused silica
    return np.sqrt(1 + 0.6961663 * l**2 / (l**2 - 0.0684043**2) + 0.4079426 * l**2 / (l**2 - 0.1162414**2)
                   + 0.8974794 * l**2 / (l**2 - 9.896161**2))

def n_sin(l):      # K. Luke et al. (2015), LPCVD Si3N4
    return np.sqrt(1 + 3.0249 * l**2 / (l**2 - 0.1353406**2) + 40314 * l**2 / (l**2 - 1239.842**2))

def n_ln(l, ray):  # D. E. Zelmon et al. (1997), congruent LiNbO3
    A = {"e": (2.9804, 0.02047, 0.5981, 0.0666, 8.9543, 416.08), "o": (2.6734, 0.01764, 1.2290, 0.05914, 12.614, 474.6)}[ray]
    return np.sqrt(1 + A[0] * l**2 / (l**2 - A[1]) + A[2] * l**2 / (l**2 - A[3]) + A[4] * l**2 / (l**2 - A[5]))

def group_index(f, l, h=1e-4):
    return f(l) - l * (f(l + h) - f(l - h)) / (2 * h)

MATS = [("Si", n_si, 1.2, C1), ("Si$_3$N$_4$", n_sin, 0.4, C3), ("LiNbO$_3$ ($n_e$)", lambda l: n_ln(l, "e"), 0.45, C4),
        ("LiNbO$_3$ ($n_o$)", lambda l: n_ln(l, "o"), 0.45, C5), ("SiO$_2$", n_sio2, 0.4, C2)]


def fig_dispersion():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    for name, f, lmin, col in MATS:
        l = np.linspace(lmin, 2.0, 400)
        a.plot(l, f(l), color=col, label=name)
        b.plot(l, group_index(f, l), color=col)
    for ax in (a, b):
        for lb in (1.31, 1.55):
            ax.axvline(lb, color=MUTED, lw=0.7, ls=":")
        ax.set_xlim(0.4, 2.0)
    a.set_ylim(1.3, 3.8); b.set_ylim(1.3, 4.6)
    a.text(1.315, 3.72, "1310", fontsize=6.5, color=MUTED); a.text(1.555, 3.72, "1550", fontsize=6.5, color=MUTED)
    finish(a, "Wavelength (µm)", "Refractive index $n$", legend=True, loc="center right")
    finish(b, "Wavelength (µm)", "Material group index $n_g$")
    tag(a, "a"); tag(b, "b")
    fig.tight_layout(w_pad=2.5)
    savefig(fig, "ch02_dispersion")
    print("\nindex and material group index at 1310 / 1550 nm:")
    for name, f, _, _ in MATS:
        print(f"  {name:22s} n = {f(1.31):.4f} / {f(1.55):.4f}   n_g = {group_index(f, 1.31):.3f} / {group_index(f, 1.55):.3f}")


# ------------------------------------------------------------------ Gaussian overlaps
def eta_size(w1, w2):
    return (2 * w1 * w2 / (w1**2 + w2**2))**2

def eta_offset(w1, w2, d):
    return eta_size(w1, w2) * np.exp(-2 * d**2 / (w1**2 + w2**2))

def eta_tilt(w1, w2, th, lam=1.55, n=1.0):
    return eta_size(w1, w2) * np.exp(-2 * (np.pi * n * th)**2 * w1**2 * w2**2 / (lam**2 * (w1**2 + w2**2)))


def fig_overlap():
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    d = np.linspace(0, 8, 300)
    for w2, lab, col in [(5.2, "SMF to SMF (5.2 µm)", C1), (2.5, "SMF to 2.5 µm spot", C2), (1.5, "SMF to 1.5 µm spot", C4)]:
        a.plot(d, 10 * np.log10(eta_offset(5.2, w2, d)), color=col, label=lab)
    a.axhline(-1, color=MUTED, lw=0.7, ls="--")
    a.set_ylim(-12, 0.5); a.set_xlim(0, 8)
    finish(a, "Lateral offset $d$ (µm)", "Coupling (dB)", legend=True, loc="lower left")
    r = np.logspace(-1, 1, 300)
    b.semilogx(r, 10 * np.log10(eta_size(1.0, r)), color=C1)
    for rr in (0.5, 2.0):
        b.plot(rr, 10 * np.log10(eta_size(1, rr)), "o", color=C2, ms=4)
        b.annotate(f"{10*np.log10(eta_size(1, rr)):.2f} dB", (rr, 10 * np.log10(eta_size(1, rr))), textcoords="offset points",
                   xytext=(6, -10 if rr > 1 else -10), fontsize=7, color=INK)
    b.set_ylim(-14, 0.5)
    finish(b, "Waist ratio $w_2/w_1$", "Coupling (dB)")
    tag(a, "a"); tag(b, "b")
    fig.tight_layout(w_pad=2.5)
    savefig(fig, "ch03_overlap")
    print("\ncoupling: SMF->1.5um spot %.2f dB, SMF->2.5um %.2f dB" % (10 * np.log10(eta_size(5.2, 1.5)), 10 * np.log10(eta_size(5.2, 2.5))))
    print("1 dB lateral tolerance SMF-SMF: %.2f um" % np.sqrt(0.1151 * 2 * 5.2**2))
    print("1 dB tilt tolerance SMF-SMF in air: %.2f deg" % np.degrees(np.sqrt(np.log(10**0.1)) * 1.55 / (np.pi * 5.2)))


# ------------------------------------------------------------------ standard single-mode fibre
def fibre_numbers():
    a, n2, delta = 4.1, 1.4440, 0.0036          # core radius (um), cladding index at 1550, relative index step
    n1 = n2 / np.sqrt(1 - 2 * delta)
    NA = np.sqrt(n1**2 - n2**2)
    print("\nfibre: n1 = %.4f, NA = %.3f, cutoff = %.0f nm" % (n1, NA, 1000 * 2 * np.pi * a * NA / 2.405))
    for lam in (1.31, 1.55):
        V = 2 * np.pi * a * NA / lam
        w = a * (0.65 + 1.619 * V**-1.5 + 2.879 * V**-6)
        print("  lambda %.2f: V = %.3f, MFD (Marcuse) = %.2f um" % (lam, V, 2 * w))


# ------------------------------------------------------------------ transparency windows (Chapter 4)
def fig_windows():
    eV = lambda E: 1.2398 / E
    rows = [("SiO$_2$", eV(9.0), 3.5, C2, False), ("Si$_3$N$_4$", eV(5.0), None, C3, False), ("LiNbO$_3$", eV(3.9), None, C4, False),
            ("BaTiO$_3$", eV(3.2), None, C5, False), ("GaAs", eV(1.42), None, MUTED, False), ("InP", eV(1.344), None, INK, False),
            ("Si", eV(1.12), None, C1, False), ("Ge", eV(0.80), None, "#7a7f88", True)]
    fig, ax = plt.subplots(figsize=(6.3, 2.9))
    for i, (name, l0, l1, col, ge) in enumerate(rows):
        y = len(rows) - 1 - i
        x1 = l1 if l1 else 2.6
        ax.barh(y, x1 - l0, left=l0, height=0.55, color=col, alpha=0.8 if not ge else 0.35, edgecolor="none")
        if not l1:
            ax.annotate("", xy=(2.75, y), xytext=(2.55, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
        ax.text(l0 - 0.03, y, f"{1000*l0:.0f} nm", ha="right", va="center", fontsize=6.5, color=MUTED)
    ax.text(1.62, 0, "direct-gap edge: absorbs in the C band", fontsize=6.5, va="center", color=INK)
    for lb, nm in [(1.31, "O"), (1.55, "C")]:
        ax.axvline(lb, color=RED, lw=0.8, ls="--")
        ax.text(lb, len(rows) - 0.35, nm + " band", ha="center", fontsize=7, color=RED)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_xlim(0.0, 2.8); ax.set_ylim(-0.6, len(rows) - 0.1); ax.grid(axis="y", visible=False)
    finish(ax, "Wavelength (µm)")
    savefig(fig, "ch04_windows")


# ------------------------------------------------------------------ waveguide cross-sections to scale (Chapter 4)
def fig_xsections():
    fig, ax = plt.subplots(figsize=(6.6, 2.2))
    ox = "#DCE9F7"; si = "#9DB3CC"; sin = "#E0B060"; ln = "#EE9AAA"; bto = "#B8A8E0"; inp = "#C9C2B0"; q = "#8E7F5A"
    x0 = 0.0
    def lab(x, t1, t2=""):
        ax.text(x, -1.35, t1, ha="center", va="top", fontsize=7, color=INK, fontweight="bold")
        if t2: ax.text(x, -1.75, t2, ha="center", va="top", fontsize=6.3, color=MUTED)
    def box(x, w, y0, h, c, **k): ax.add_patch(Rectangle((x - w / 2, y0), w, h, color=c, lw=0, **k))
    # (1) Si strip 500 x 220 nm
    c = 1.0; box(c, 1.6, -1.0, 1.0, ox); box(c, 1.6, 0, 0.9, ox, alpha=0.5); box(c, 0.5, 0, 0.22, si); lab(c, "Si strip", "500 × 220 nm")
    # (2) Si rib, 90 nm slab
    c = 3.6; box(c, 1.6, -1.0, 1.0, ox); box(c, 1.6, 0, 0.9, ox, alpha=0.5); box(c, 1.6, 0, 0.09, si); box(c, 0.5, 0, 0.22, si); lab(c, "Si rib", "90 nm slab")
    # (3) SiN 1.2 x 0.4 um (moderate confinement)
    c = 6.4; box(c, 2.2, -1.0, 1.0, ox); box(c, 2.2, 0, 1.2, ox, alpha=0.5); box(c, 1.2, 0, 0.4, sin); lab(c, "SiN", "1.2 × 0.4 µm")
    # (4) TFLN ridge: 400 nm film, 200 nm etch, sloped sidewalls
    c = 9.4; box(c, 2.4, -1.0, 1.0, ox); box(c, 2.4, 0, 1.0, ox, alpha=0.5); box(c, 2.4, 0, 0.2, ln)
    ax.add_patch(Polygon([[c - 0.62, 0.2], [c + 0.62, 0.2], [c + 0.5, 0.4], [c - 0.5, 0.4]], color=ln, lw=0)); lab(c, "TFLN ridge", "400 nm film, half etched")
    # (5) BTO on Si: Si ridge on a thin BTO film (schematic)
    c = 12.3; box(c, 2.2, -1.0, 1.0, ox); box(c, 2.2, 0, 0.9, ox, alpha=0.5); box(c, 2.2, 0, 0.1, bto); box(c, 2.2, 0.1, 0.05, si); box(c, 0.6, 0.1, 0.17, si)
    lab(c, "BTO on Si", "schematic")
    # (6) InP deep ridge: InGaAsP core 0.5 um, 2 um wide
    c = 15.3; box(c, 2.8, -1.0, 1.0, inp); box(c, 2.0, 0, 0.5, q); box(c, 2.0, 0.5, 1.3, inp); lab(c, "InP deep ridge", "0.5 µm InGaAsP core")
    ax.plot([16.95, 16.95], [0.0, 1.0], color=INK, lw=1); ax.text(17.05, 0.5, "1 µm", va="center", fontsize=6.5, color=INK)
    ax.set_xlim(-0.1, 17.7); ax.set_ylim(-2.0, 2.0); ax.set_aspect("equal"); ax.axis("off")
    savefig(fig, "ch04_xsections")


if __name__ == "__main__":
    fig_dispersion(); fig_overlap(); fibre_numbers(); fig_windows(); fig_xsections()
