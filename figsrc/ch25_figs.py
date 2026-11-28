"""Figures for Chapter 25 (laser dynamics, noise and linewidth), Sections 25.2-25.5.

Run from the repository root:  python -I -X utf8 figsrc/ch25_figs.py
Writes assets/figs/ch25_chirp.svg, ch25_rin.svg, ch25_linewidth.svg and ch25_feedback.svg, and prints every number
the figures and captions use. (Figures 25.1, 25.6 and 25.7 come from figsrc/ch2x_lasers.py.)

The laser is the Chapter 24 Fabry-Perot laser with the parameters of the dyn demo (FP in ch2x_lasers.py): alpha = 4,
n_sp = 1.8, gain compression 2e-17 cm^3. RIN uses the dyn demo's simplified Langevin model.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from figstyle import *
from geomstyle import *
from ch2x_lasers import FP

QE, CL = 1.602e-19, 3e10
P_ = FP; VG = CL / P_["ng"]; V = P_["L"] * P_["w"] * P_["d"]
AM = np.log(1 / P_["R"] ** 2) / (2 * P_["L"]); TP = 1 / (VG * (P_["ai"] + AM))
GTH = (P_["ai"] + AM) / P_["Gam"]; NTH = P_["Ntr"] * np.exp(GTH / P_["g0"])
HV = 1.2398 / P_["lam"] * QE
ALPHA, NSP, BETA = 4.0, 1.8, 1e-4


def rrec(N):
    return P_["A"] * N + P_["B"] * N ** 2 + P_["C"] * N ** 3


ITH = QE * V / P_["eta"] * rrec(NTH)


def op(I):
    """Small-signal operating point at current I (A), as in the dyn demo."""
    S = P_["Gam"] * TP * P_["eta"] * (I - ITH) / (QE * V); a = P_["g0"] / NTH
    tdn = 1 / (P_["A"] + 2 * P_["B"] * NTH + 3 * P_["C"] * NTH ** 2)
    wr2 = VG * a * S / (TP * (1 + P_["eps"] * S)); K = 4 * np.pi ** 2 * (TP + P_["eps"] / (VG * a))
    fr = np.sqrt(wr2) / (2 * np.pi); gam = K * fr ** 2 + 1 / tdn
    Np = S * V / P_["Gam"]; Ptot = Np * HV * VG * AM; Rsp = VG * (P_["ai"] + AM) * NSP
    return dict(S=S, wr2=wr2, gam=gam, fr=fr, K=K, Np=Np, P=Ptot, Pf=Ptot / 2, Rsp=Rsp, tdn=tdn)


def rin_intrinsic(o, f):
    w = 2 * np.pi * f; gN = 1 / o["tdn"]
    return 4 * o["Rsp"] * (gN ** 2 + w ** 2) / (o["Np"] * ((o["wr2"] - w ** 2) ** 2 + w ** 2 * o["gam"] ** 2))


# ================================================================== Figure 25.2: chirp of a directly modulated laser
def fig_chirp():
    I0, I1, BR = 30e-3, 70e-3, 2.5e9
    bits = np.array([0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0])
    dt = 0.1e-12; spb = int(round(1 / BR / dt)); tr = 25e-12               # 25 ps current edges (raised cosine)
    raw = np.repeat(np.where(bits == 1, I1, I0), spb).astype(float)
    k = int(tr / dt); ker = np.sin(np.linspace(0, np.pi, k)) ; ker /= ker.sum()
    Idrv = np.convolve(np.r_[np.full(k, I0), raw, np.full(k, raw[-1])], ker, mode="same")[k:-k]
    g0, Ntr, G, eps = P_["g0"], P_["Ntr"], P_["Gam"], P_["eps"]
    # start in the steady state of the zero level
    S = G * TP * P_["eta"] * (I0 - ITH) / (QE * V); N = Ntr * np.exp(GTH * (1 + eps * S) / g0)
    for _ in range(int(3e-9 / dt)):                                        # settle
        g = g0 * np.log(N / Ntr) / (1 + eps * S)
        dN = P_["eta"] * I0 / (QE * V) - rrec(N) - VG * g * S; dS = G * VG * g * S - S / TP + G * BETA * P_["B"] * N ** 2
        N += dt * dN; S += dt * dS

    def der(N, S, I):
        g = g0 * np.log(N / Ntr) / (1 + eps * S)
        return P_["eta"] * I / (QE * V) - rrec(N) - VG * g * S, G * VG * g * S - S / TP + G * BETA * P_["B"] * N ** 2
    Ns, Ss = np.empty(len(Idrv)), np.empty(len(Idrv))
    for i, I in enumerate(Idrv):
        k1 = der(N, S, I); k2 = der(N + dt / 2 * k1[0], S + dt / 2 * k1[1], I)
        k3 = der(N + dt / 2 * k2[0], S + dt / 2 * k2[1], I); k4 = der(N + dt * k3[0], S + dt * k3[1], I)
        N += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); S += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        Ns[i], Ss[i] = N, S
    t = np.arange(len(Idrv)) * dt
    Pf = 0.5 * Ss * V / G * VG * AM * HV
    chirp = ALPHA / (4 * np.pi) * (G * VG * g0 * np.log(Ns / Ntr) - 1 / TP)          # index follows N (uncompressed gain)
    adiab = ALPHA / (4 * np.pi) * eps * Ss / TP                                       # the alpha/(4 pi) kappa P term
    trans = ALPHA / (4 * np.pi) * np.gradient(np.log(Ss), dt)
    lv = lambda I: 0.5 * (G * TP * P_["eta"] * (I - ITH) / (QE * V)) * V / G * VG * AM * HV
    print(f"chirp: levels {I0*1e3:.0f}/{I1*1e3:.0f} mA at {BR/1e9:.1f} Gb/s; steady powers per facet {lv(I0)*1e3:.2f} / {lv(I1)*1e3:.2f} mW")
    print(f"  adiabatic chirp at the levels {ALPHA/(4*np.pi)*eps*G*TP*P_['eta']*(I0-ITH)/(QE*V)/TP/1e9:.2f} /"
          f" {ALPHA/(4*np.pi)*eps*G*TP*P_['eta']*(I1-ITH)/(QE*V)/TP/1e9:.2f} GHz (difference"
          f" {ALPHA/(4*np.pi)*eps*G*TP*P_['eta']*(I1-I0)/(QE*V)/TP/1e9:.2f} GHz)")
    print(f"  simulated: chirp {chirp.min()/1e9:.1f} to {chirp.max()/1e9:.1f} GHz (p-p {(chirp.max()-chirp.min())/1e9:.1f} GHz);"
          f" power {Pf.min()*1e3:.2f}-{Pf.max()*1e3:.2f} mW; check total - adiabatic vs transient term, rms diff"
          f" {np.sqrt(np.mean((chirp - adiab - trans)[50:-50] ** 2))/1e9:.2f} GHz")
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.3, 3.4), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.15]))
    tn = t * 1e9
    a.plot(tn, Pf * 1e3, color=C1, lw=1.3)
    a.set_ylabel("Power per facet (mW)")
    ax2 = a.twinx(); ax2.plot(tn, Idrv * 1e3, color=MUTED, lw=0.8, ls=":"); ax2.set_ylim(0, 160)
    ax2.set_yticks([30, 70]); ax2.set_ylabel("Drive (mA)", color=MUTED); ax2.tick_params(colors=MUTED); ax2.grid(False)
    ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(MUTED)
    for j, bt in enumerate(bits):
        a.text((j + 0.5) / BR * 1e9, 21.5, str(bt), ha="center", va="center", fontsize=6.6, color=MUTED)
    a.set_ylim(0, 23.5)
    tag(a, "a")
    b.plot(tn, chirp / 1e9, color=C4, lw=1.2, label="frequency shift Δν(t)")
    b.plot(tn, adiab / 1e9, color=INK, lw=1.0, ls="--", label=r"adiabatic part $\frac{\alpha}{4\pi}\kappa P$")
    b.axhline(0, color=MUTED, lw=0.5)
    b.set_ylim(-13.5, 16)                              # room under the trace for the legend
    ad0 = ALPHA / (4 * np.pi) * eps * G * TP * P_["eta"] * (I0 - ITH) / (QE * V) / TP
    ad1 = ALPHA / (4 * np.pi) * eps * G * TP * P_["eta"] * (I1 - ITH) / (QE * V) / TP
    b.text(3.55, 3.6, f"adiabatic: {ad1/1e9:.1f} GHz on a 1,\n{ad0/1e9:.1f} GHz on a 0", fontsize=6.4, color=INK, ha="center", va="bottom")
    b.annotate("transient chirp\nat the edges", xy=(0.43, chirp[np.argmin(abs(t - 0.43e-9))] / 1e9), xytext=(1.35, 11.0), fontsize=6.6, color=INK,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    finish(b, "Time (ns)", "Δν (GHz)", legend=True, loc="lower right")
    b.legend(loc="lower right", fontsize=6.4, ncol=2)
    b.set_xlim(0, len(bits) / BR * 1e9)
    tag(b, "b")
    fig.tight_layout(h_pad=0.6)
    save(fig, "ch25_chirp")


# ================================================================== Figure 25.3: RIN against power
def fig_rin():
    Is = np.linspace(ITH * 1.03, 160e-3, 300)
    Pf, lf, pk, shot = [], [], [], []
    f = np.linspace(0.05e9, 60e9, 6000)
    for I in Is:
        o = op(I); r = rin_intrinsic(o, f)
        Pf.append(o["Pf"]); lf.append(rin_intrinsic(o, 100e6)); pk.append(r.max()); shot.append(2 * HV / o["Pf"])
    Pf, lf, pk, shot = map(np.array, (Pf, lf, pk, shot))
    db = lambda x: 10 * np.log10(x)
    for I in (25e-3, 50e-3, 120e-3):
        o = op(I); r = rin_intrinsic(o, f)
        print(f"RIN at {I*1e3:.0f} mA ({o['Pf']*1e3:.2f} mW/facet): 100 MHz intrinsic {db(rin_intrinsic(o,100e6)):.1f}, peak {db(r.max()):.1f} dB/Hz"
              f" at {f[r.argmax()]/1e9:.1f} GHz, shot floor {db(2*HV/o['Pf']):.1f} dB/Hz, 100 MHz with shot noise"
              f" {db(rin_intrinsic(o,100e6) + 2*HV/o['Pf']):.1f} dB/Hz")
    j = np.argmin(abs(lf - shot)); print(f"intrinsic low-frequency RIN meets the shot-noise floor at {Pf[j]*1e3:.2f} mW per facet")
    sl = np.polyfit(np.log10(Pf[(Pf > 0.5e-3) & (Pf < 3e-3)]), db(lf[(Pf > 0.5e-3) & (Pf < 3e-3)]), 1)[0]
    print(f"low-frequency RIN slope {sl:.1f} dB/decade (1/P^3 = -30)")
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    ax.semilogx(Pf * 1e3, db(pk), color=C4, label="peak, at $f_r$")
    ax.semilogx(Pf * 1e3, db(lf + shot), color=C1, label="at 100 MHz")
    ax.semilogx(Pf * 1e3, db(lf), color=C1, lw=0.9, ls="--", label="at 100 MHz, laser only")
    ax.semilogx(Pf * 1e3, db(shot), color=MUTED, lw=1.0, ls=":", label="shot noise $2h\\nu/P$")
    ax.axhline(-140, color=C3, lw=0.7, ls="-.")
    ax.text(2.0, -139, "reference link: −140 dB/Hz", fontsize=6.4, color=C3, va="bottom")
    ax.text(6.0, -172.5, "$\\propto 1/P^3$", fontsize=6.6, color=C1, rotation=-30)
    ax.set_xlim(0.3, 20); ax.set_ylim(-190, -110)
    ax.set_xticks([0.3, 1, 3, 10, 20]); ax.set_xticklabels(["0.3", "1", "3", "10", "20"])
    finish(ax, "Output power per facet (mW)", "RIN (dB/Hz)", legend=True, loc="upper right")
    ax.legend(loc="upper right", fontsize=6.3)
    save(fig, "ch25_rin")


# ================================================================== Figure 25.4: linewidth
def fig_linewidth():
    P0 = 6.5e-3
    dnu_st = VG ** 2 * HV * (P_["ai"] + AM) * NSP * AM / (8 * np.pi * P0)
    dnu = dnu_st * (1 + ALPHA ** 2)
    print(f"linewidth at {P0*1e3} mW per facet: Schawlow-Townes {dnu_st/1e6:.3f} MHz, Henry (alpha = {ALPHA}) {dnu/1e6:.2f} MHz"
          f" (x{1+ALPHA**2:.0f}); coherence time 1/(pi dnu) {1/(np.pi*dnu)*1e9:.0f} ns / {1/(np.pi*dnu_st)*1e6:.2f} us")
    fig, (a, b) = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.15]))
    f = np.linspace(-6e6, 6e6, 2001)
    for d, col, lab in ((dnu, C4, f"α = {ALPHA:.0f}: {dnu/1e6:.1f} MHz"), (dnu_st, C1, f"α = 0: {dnu_st/1e6:.2f} MHz")):
        L = (d / 2 / np.pi) / (f ** 2 + (d / 2) ** 2)
        a.plot(f / 1e6, L / L.max(), color=col, label=lab)
    a.annotate("", xy=(dnu / 2e6, 0.5), xytext=(-dnu / 2e6, 0.5), arrowprops=dict(arrowstyle="<|-|>", color=C4, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))
    a.text(0, 0.44, "FWHM", fontsize=6.4, color=C4, ha="center", va="top")
    a.set_xlim(-6, 6); a.set_ylim(0, 1.15)
    finish(a, "Optical frequency offset (MHz)", "Field spectrum (each norm. to its peak)", legend=True, loc="upper right")
    a.legend(loc="upper right", fontsize=6.4)
    tag(a, "a")
    rng = np.random.default_rng(7)
    T, n = 1e-6, 500; dt = T / n; t = np.arange(n + 1) * dt
    for d, col, nrun in ((dnu, C4, 4), (dnu_st, C1, 2)):
        for r in range(nrun):
            phi = np.r_[0, np.cumsum(rng.normal(0, np.sqrt(2 * np.pi * d * dt), n))]
            b.plot(t * 1e9, phi, color=col, lw=0.8, alpha=0.9)
        sd = np.sqrt(2 * np.pi * d * t)
        b.fill_between(t * 1e9, -sd, sd, color=col, alpha=0.10, lw=0)
    tc = 1 / (np.pi * dnu)
    b.axvline(tc * 1e9, color=C4, lw=0.6, ls=":")
    b.text(tc * 1e9 + 15, 6.2, f"coherence time\n1/(πΔν) = {tc*1e9:.0f} ns", fontsize=6.4, color=C4, va="center")
    b.text(985, 7.6, "shaded: ±1 standard deviation,\n$\\sqrt{2\\pi\\Delta\\nu\\, t}$", fontsize=6.2, color=MUTED, ha="right", va="center")
    b.set_xlim(0, 1000); b.set_ylim(-9, 9); b.set_yticks([-8, -4, 0, 4, 8])
    finish(b, "Time (ns)", "Phase drift φ(t) (rad)")
    tag(b, "b")
    fig.tight_layout(w_pad=1.8)
    save(fig, "ch25_linewidth")


# ================================================================== Figure 25.5: regimes of optical feedback
def fig_feedback():
    fig = plt.figure(figsize=(6.3, 2.75))
    # (top) the set-up
    s = fig.add_axes([0.0, 0.70, 1.0, 0.30]); frameless(s, (0, 20), (0, 2.4))
    block(s, 3.0, 1.2, 3.2, 0.9, "laser", fc="#F3E6D6")
    arrow(s, (4.7, 1.38), (13.3, 1.38), col=RED, lw=1.3, ms=9)
    arrow(s, (13.3, 1.0), (4.7, 1.0), col=RED, lw=0.9, ms=7, ls=(0, (3, 2)))
    s.add_patch(Rectangle((13.5, 0.5), 0.25, 1.4, fc=MUTED, ec="none"))
    label(s, 14.0, 1.2, "reflection: connector, facet,\ngrating coupler, chip edge", ha="left", fs=FS_SMALL)
    label(s, 9.0, 1.7, "output $P$", col=RED, fs=FS_SMALL)
    label(s, 9.0, 0.62, "fed back: $f_\\mathrm{ext}P$, after a delay", col=RED, fs=FS_SMALL)
    panel(s, "a", 0.0, 1.0)
    # (bottom) the regimes along the feedback axis
    ax = fig.add_axes([0.05, 0.16, 0.92, 0.48])
    regs = [(-90, -70, "I", "line narrows or\nbroadens with the\nfeedback phase", "#E6EEF8"),
            (-70, -45, "II", "mode hops between\nexternal-cavity modes", "#D8E4F3"),
            (-45, -40, "III", "", "#DDEFE6"),
            (-40, -10, "IV", "coherence collapse: linewidth\nbroadens to gigahertz, RIN rises\nby tens of decibels", "#F6DCD6"),
            (-10, 0, "V", "stable\nexternal\ncavity", "#DDEFE6")]
    for x0, x1, rn, txt, col in regs:
        ax.axvspan(x0, x1, ymin=0, ymax=1, color=col, lw=0)
        ax.axvline(x0, color="white", lw=1.2)
        ax.text((x0 + x1) / 2, 0.86, rn, ha="center", va="center", fontsize=8, color=INK, fontweight="bold")
        if txt:
            ax.text((x0 + x1) / 2, 0.45, txt, ha="center", va="center", fontsize=6.4, color=INK)
    ax.annotate("III: narrow,\nstable", xy=(-42.5, 0.62), xytext=(-52, 0.12), fontsize=6.4, color=INK, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.annotate("", xy=(-30, 0.04), xytext=(-40, 0.04), arrowprops=dict(arrowstyle="<|-|>", color=C4, lw=0.8, mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.text(-35, 0.07, "onset of collapse,\ntypical lasers", fontsize=6.0, color=C4, ha="center", va="bottom")
    ax.plot([-20, -15], [0.04, 0.04], color=INK, lw=3, solid_capstyle="butt", zorder=5)
    ax.text(-17.5, 0.08, "grating-coupler\nreflection (Ch. 15)", fontsize=6.0, color=INK, ha="center", va="bottom")
    ax.set_xlim(-90, 0); ax.set_ylim(0, 1)
    ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.grid(False)
    ax.set_xticks(np.arange(-90, 1, 10))
    ax.set_xlabel("Fraction of the output fed back into the laser, $f_\\mathrm{ext}$ (dB)")
    ax.text(0.0, 1.03, "b", transform=ax.transAxes, fontweight="bold", fontsize=9.5, color=INK, ha="right", va="bottom")
    save(fig, "ch25_feedback")


if __name__ == "__main__":
    o = op(50e-3)
    print(f"FP laser at 50 mA: I_th {ITH*1e3:.2f} mA, f_r {o['fr']/1e9:.2f} GHz, K {o['K']*1e12:.0f} ps, P/facet {o['Pf']*1e3:.2f} mW,"
          f" demo linewidth Rsp(1+a^2)/(4 pi Np) = {o['Rsp']*(1+ALPHA**2)/(4*np.pi*o['Np'])/1e6:.2f} MHz")
    only = sys.argv[1:]
    for fn in (fig_chirp, fig_rin, fig_linewidth, fig_feedback):
        if not only or fn.__name__ in only:
            fn()
