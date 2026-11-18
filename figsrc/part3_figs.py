"""Figures for Part III. Run: .venv/bin/python figsrc/part3_figs.py (needs figsrc/ch09_supermodes.json)."""
import json, os
import numpy as np
from figstyle import *

def fig_supermodes():
    S = json.load(open(os.path.join(os.path.dirname(__file__), "ch09_supermodes.json")))
    g = np.array([x for x, l in zip(S["gap"], S["lam"]) if l == 1.55]); Lx = np.array([x for x, l in zip(S["Lx"], S["lam"]) if l == 1.55])
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL)
    a.semilogy(1000 * g, Lx, "o", color=C1, ms=4, label="femwell")
    gg = np.linspace(0.08, 0.42, 100); a.semilogy(1000 * gg, 1.55 / (2 * 0.0205 * np.exp(-8.75 * (gg - 0.2))), color=C2, lw=1.2, label="fit, ×2.4 per 100 nm")
    a.set_xlim(80, 420); a.set_yticks([10, 20, 50, 100, 200]); a.set_yticklabels(["10", "20", "50", "100", "200"]); a.minorticks_off()
    finish(a, "Gap (nm)", "Cross-over length L$_x$ (µm)", legend=True, loc="upper left")
    lam = np.linspace(1.50, 1.60, 200); LB = 2.5
    for gap, col in ((0.2, C1), (0.3, C3)):
        Lx0 = 1.55 / (2 * 0.0205 * np.exp(-8.75 * (gap - 0.2))); L50 = Lx0 / 2 - LB
        dn = 0.0205 * (lam / 1.55) ** 7.7 * np.exp(-8.75 * (1.55 / lam) * (gap - 0.2))
        b.plot(1000 * lam, 100 * np.sin(np.pi * (L50 + LB) * 2 * dn / (2 * lam)) ** 2, color=col, label=f"gap {int(1000*gap)} nm, L = {L50:.1f} µm")
    b.axhline(50, color=MUTED, lw=0.7, ls=":"); b.set_ylim(20, 80); b.set_xlim(1500, 1600)
    finish(b, "Wavelength (nm)", "Cross-coupled power (%)", legend=True, loc="upper left")
    tag(a, "a"); tag(b, "b"); fig.tight_layout(w_pad=2.5); savefig(fig, "ch09_supermodes")
    for gap in (0.2, 0.3):
        Lx0 = 1.55 / (2 * 0.0205 * np.exp(-8.75 * (gap - 0.2))); L50 = Lx0 / 2 - LB
        f = lambda l: np.sin(np.pi * (L50 + LB) * 2 * 0.0205 * (l / 1.55) ** 7.7 * np.exp(-8.75 * (1.55 / l) * (gap - 0.2)) / (2 * l)) ** 2
        print(f"gap {gap}: L50 {L50:.1f} um, cross at 1530/1550/1570 nm: {100*f(1.53):.1f} / {100*f(1.55):.1f} / {100*f(1.57):.1f} %, slope {100*(f(1.551)-f(1.549))/2:.2f} %/nm")

if __name__ == "__main__":
    fig_supermodes()
