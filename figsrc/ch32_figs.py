"""Figures of Chapter 32 (data analysis). All data are synthetic: generated here from the chapter's models and numbers,
with illustrative noise and fabrication offsets, never measured data.

    python -I -X utf8 figsrc/ch32_figs.py

ch32_calib     a raw MZI spectrum, the loopback, the polynomial envelope and the calibrated response
ch32_ng        troughs found automatically and the group index from their spacing, against femwell
ch32_cutback   cutback spectra of four spirals and the loss spectrum from per-wavelength fits (two length sets)
ch32_ringgap   Worked Example 32.1: three ring gaps, their two mirror solutions for loss and coupling
ch32_bragg     a Bragg grating's reflection spectrum, kappa and n_eff from it, and when the simple formula fails
ch32_wafer     wafer statistics: wafer-scale bowl and die-to-die scatter of ring resonances
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *
from geomstyle import *

HERE = os.path.dirname(os.path.abspath(__file__))
LAM0 = 1550.0
GC_IL, GC_BW1 = 4.1, 30.6          # SiEPIC EBeam PDK TE grating coupler (Chapter 15): peak loss dB, 1 dB bandwidth nm
DL = 100.0                          # MZI arm-length difference (um), as in Chapter 30


def disp():
    """n_eff(lambda) and n_g(lambda) of the 500 x 220 nm strip from femwell (ch32_disp.json); returns callables in nm."""
    d = json.load(open(os.path.join(HERE, "ch32_disp.json")))
    l = np.array(d["lam_um"]) * 1000; n = np.array(d["neff"]); g = np.array(d["ng"])
    pn = np.polyfit(l - LAM0, n, 3); pg = np.polyfit(l - LAM0, g, 2)
    return (lambda x: np.polyval(pn, x - LAM0)), (lambda x: np.polyval(pg, x - LAM0)), (l, n, g)


def gc_db(lam, centre=1550.0, il=GC_IL, bw=GC_BW1, skew=0.0):
    """Grating coupler loss in dB (negative): quadratic in wavelength (Gaussian), 1 dB down at +-bw/2, with a small skew."""
    x = (lam - centre) / (bw / 2)
    return -(il + x ** 2 + skew * x ** 3)


def to_dbm(p_mw):
    return 10 * np.log10(p_mw)


# ------------------------------------------------------------------ Figure 32.1 and 32.2 data
def mzi_measurement(rng):
    neff, ng, _ = disp()
    lam = np.arange(1500.0, 1600.0001, 0.01)
    PIN = 0.0                                                     # laser power, dBm
    # device couplers a little different from the loopback's (fabrication and fibre position)
    gc_dev = gc_db(lam, 1548.5, GC_IL + 0.15, GC_BW1, 0.08) * 2
    gc_lb = gc_db(lam, 1550.0, GC_IL, GC_BW1, 0.08) * 2
    rip = lambda ph, amp: 10 * np.log10(1 + amp * np.cos(ph))      # Fabry-Perot fringes between the couplers
    fr_dev = rip(4 * np.pi * 4.18 * 520.0 / (lam / 1000), 0.04)
    fr_lb = rip(4 * np.pi * 4.18 * 260.0 / (lam / 1000), 0.04)
    phi = 2 * np.pi * neff(lam) * DL / (lam / 1000)
    k = 0.48                                                      # Y-branch split ratio (imbalance sets the extinction)
    mzi = np.abs(k + (1 - k) * np.exp(-1j * phi)) ** 2
    floor = 1e-6 * (1 + 0.5 * rng.standard_normal(lam.size)) ** 2  # detector floor near -60 dBm (mW)
    p_dev = 10 ** ((PIN + gc_dev + fr_dev) / 10) * mzi * (1 + 0.004 * rng.standard_normal(lam.size)) + floor
    p_lb = 10 ** ((PIN + gc_lb + fr_lb) / 10) * (1 + 0.004 * rng.standard_normal(lam.size)) + 1e-6
    return lam, to_dbm(p_dev), to_dbm(p_lb), dict(mzi=mzi, phi=phi, neff=neff, ng=ng)


def envelope_fit(lam, lb_dbm, drop_db=10.0, order=3):
    pk = lb_dbm.max()
    win = lb_dbm > pk - drop_db
    c = np.polyfit(lam[win] - LAM0, lb_dbm[win], order)
    return np.polyval(c, lam - LAM0), win


def fig_calib():
    rng = np.random.default_rng(321)
    lam, dev, lb, m = mzi_measurement(rng)
    env, win = envelope_fit(lam, lb)
    lo, hi = lam[win].min(), lam[win].max()
    cal = dev - env
    print(f"calib: loopback peak {lb.max():.2f} dBm at {lam[lb.argmax()]:.1f} nm; fit window {lo:.1f}-{hi:.1f} nm (10 dB); "
          f"calibrated peaks {np.percentile(cal[win], 99.5):+.2f} dB; device floor {np.percentile(dev, 0.5):.1f} dBm")
    fig = plt.figure(figsize=(6.3, 4.2))
    a = fig.add_axes([0.09, 0.57, 0.88, 0.38])
    for x0, x1 in ((1500, lo), (hi, 1600)):
        a.axvspan(x0, x1, color=GRID, alpha=0.6, lw=0)
    a.plot(lam, dev, color=C1, lw=0.6, label="device: GC → MZI → GC")
    a.plot(lam, lb, color=C2, lw=0.9, label="loopback: GC → GC")
    a.plot(lam[win], env[win], color=INK, lw=1.0, ls="--", label="3rd-order fit to the loopback")
    a.set_xlim(1500, 1600); a.set_ylim(-76, -2)
    finish(a, ylabel="detected power (dBm)")
    a.legend(loc="lower center", fontsize=6.5, ncol=3, bbox_to_anchor=(0.5, -0.02))
    a.text(1503, -6, "discarded", fontsize=6.5, color=MUTED); a.text(1597, -6, "discarded", fontsize=6.5, color=MUTED, ha="right")
    tag(a, "a")
    b = fig.add_axes([0.09, 0.09, 0.88, 0.36])
    b.plot(lam[win], cal[win], color=C1, lw=0.6)
    b.set_xlim(1500, 1600); b.set_ylim(-35, 3)
    finish(b, xlabel="wavelength (nm)", ylabel="device response (dB)")
    tag(b, "b")
    save(fig, "ch32_calib")
    return lam, cal, win, m


# ------------------------------------------------------------------ Figure 32.3
def fig_ng():
    rng = np.random.default_rng(321)
    lam, dev, lb, m = mzi_measurement(rng)
    env, win = envelope_fit(lam, lb)
    cal = dev - env
    neff, ng, (lf, nf, gf) = disp()
    # automatic trough finding: local minima of a lightly smoothed trace, deeper than 10 dB below its neighbourhood
    sm = np.convolve(cal, np.ones(9) / 9, mode="same")
    idx = [i for i in range(5, lam.size - 5) if win[i] and sm[i] == sm[i - 40:i + 41].min() and sm[i] < -10]
    # refine each trough with a parabola through the smoothed points around it
    tr = []
    for i in idx:
        j = np.arange(i - 6, i + 7)
        c = np.polyfit(lam[j] - lam[i], sm[j], 2)
        tr.append(lam[i] - c[1] / (2 * c[0]))
    tr = np.array(tr)
    fsr = np.diff(tr); lc = (tr[1:] + tr[:-1]) / 2
    ng_meas = lc ** 2 / (fsr * DL * 1000)
    print(f"n_g: {len(tr)} troughs; FSR {fsr.min():.2f}-{fsr.max():.2f} nm; n_g from FSR {ng_meas.min():.3f}-{ng_meas.max():.3f}; "
          f"femwell n_g(1550) {ng(1550.0):.3f}, slope {(ng(1560)-ng(1540))/20*1000:.2f} per um")
    fig = plt.figure(figsize=(6.3, 2.5))
    a = fig.add_axes([0.08, 0.17, 0.42, 0.74])
    z = (lam > 1535) & (lam < 1565)
    a.plot(lam[z], cal[z], color=C1, lw=0.7)
    zt = (tr > 1535) & (tr < 1565)
    a.plot(tr[zt], np.interp(tr[zt], lam, sm) , "o", ms=3.5, mfc="white", mec=C4, mew=1.0, label="troughs found")
    k0 = np.where(zt)[0][2]
    a.annotate("", xy=(tr[k0 + 1], -31), xytext=(tr[k0], -31), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))
    a.text((tr[k0] + tr[k0 + 1]) / 2, -30.0, "FSR", ha="center", va="bottom", fontsize=6.5, color=INK)
    a.set_xlim(1535, 1565); a.set_ylim(-34, 3)
    finish(a, xlabel="wavelength (nm)", ylabel="device response (dB)")
    a.legend(loc="lower left", fontsize=6.5, handletextpad=0.2)
    tag(a, "a")
    b = fig.add_axes([0.6, 0.17, 0.38, 0.74])
    ll = np.linspace(1515, 1585, 100)
    b.plot(ll, ng(ll), color=INK, lw=1.0, label="femwell, 500 × 220 nm")
    b.plot(lc, ng_meas, "o", ms=3.2, color=C1, label="λ²/(FSR·ΔL)")
    b.set_xlim(1510, 1590)
    finish(b, xlabel="wavelength (nm)", ylabel="group index $n_g$")
    b.legend(loc="lower right", fontsize=6.5)
    tag(b, "b")
    save(fig, "ch32_ng")


# ------------------------------------------------------------------ Figure 32.2
def fig_cutback():
    rng = np.random.default_rng(7)
    lam = np.arange(1520.0, 1580.0001, 0.05)
    ALPHA, SIG = 2.0, 0.3                       # true loss (dB/cm) and coupler-to-coupler scatter (dB), illustrative
    sets = {"long": np.array([0.5, 1.5, 2.5, 3.5]), "short": np.array([0.1, 0.2, 0.3, 0.4])}
    def measure(L):
        out = []
        for Li in L:
            off = SIG * rng.standard_normal()                         # this structure's couplers and fibre position
            shift = 1.5 * rng.standard_normal()                       # its couplers' centre wavelength, nm
            fr = 10 * np.log10(1 + 0.012 * np.cos(4 * np.pi * 4.18 * (300 + 40 * rng.random()) / (lam / 1000)))
            il = -(gc_db(lam, 1550 + shift) * 2) + off - fr + ALPHA * Li
            out.append(il)
        return np.array(out)
    res = {}
    for name, L in sets.items():
        Y = measure(L)
        Lb = L.mean(); Sxx = np.sum((L - Lb) ** 2)
        slope = ((L - Lb)[:, None] * (Y - Y.mean(axis=0))).sum(axis=0) / Sxx
        icpt = Y.mean(axis=0) - slope * Lb
        resid = Y - (icpt + slope * L[:, None])
        sy = np.sqrt((resid ** 2).sum(axis=0) / (len(L) - 2))
        sa = sy / np.sqrt(Sxx)
        res[name] = (L, Y, slope, sa)
        i0 = np.argmin(abs(lam - 1550))
        print(f"cutback {name}: lengths {L} cm, sum (L-Lbar)^2 = {Sxx:.3f}; at 1550 nm alpha = {slope[i0]:.2f} +- {sa[i0]:.2f} dB/cm; "
              f"expected sigma_alpha = {SIG/np.sqrt(Sxx):.2f}; mean over band {slope.mean():.2f}")
    fig = plt.figure(figsize=(6.3, 2.6))
    a = fig.add_axes([0.08, 0.17, 0.4, 0.74])
    L, Y, _, _ = res["long"]
    cols = [C1, C3, C2, C4]
    for k in range(4):
        a.plot(lam, -Y[k], color=cols[k], lw=0.8, label=f"{L[k]:.1f} cm")
    a.set_xlim(1520, 1580)
    finish(a, xlabel="wavelength (nm)", ylabel="transmission (dB)")
    a.legend(loc="upper center", fontsize=6.3, ncol=4, handlelength=1.0, columnspacing=0.8)
    a.set_ylim(-18.5, -6)
    tag(a, "a")
    b = fig.add_axes([0.6, 0.17, 0.38, 0.74])
    for name, col, lab in (("short", C2, "spirals of 1–4 mm"), ("long", C1, "spirals of 0.5–3.5 cm")):
        _, _, s, sa = res[name]
        b.fill_between(lam, s - sa, s + sa, color=col, alpha=0.18, lw=0)
        b.plot(lam, s, color=col, lw=0.9, label=lab)
    b.axhline(ALPHA, color=INK, lw=0.7, ls=":")
    b.set_xlim(1520, 1580); b.set_ylim(-3, 7)
    finish(b, xlabel="wavelength (nm)", ylabel="fitted loss (dB/cm)")
    b.legend(loc="upper right", fontsize=6.3)
    b.text(1522, ALPHA - 0.25, "true 2.0 dB/cm", fontsize=6.2, color=INK, va="top")
    tag(b, "b")
    save(fig, "ch32_cutback")


# ------------------------------------------------------------------ Figure 32.4
def fig_ringgap():
    R, NG = 10.0, 4.18
    Lcm = 2 * np.pi * R * 1e-4
    FSR = LAM0 ** 2 / (NG * 2 * np.pi * R * 1000)
    gaps = np.array([200, 250, 300])
    loss_phys = np.array([2.1, 1.9, 2.0])          # Worked Example 32.1 (illustrative)
    loss_mirr = np.array([8.6, 3.6, 1.5])
    a_of = lambda dbcm: 10 ** (-dbcm * Lcm / 20)    # round-trip field transmission
    a = a_of(loss_phys); t = a_of(loss_mirr)       # the mirror solution's "a" is the physical t
    k2_phys = 1 - t ** 2; k2_mirr = 1 - a ** 2
    print(f"ring: L = {Lcm*1e4:.2f} um, FSR {FSR:.2f} nm")
    for i in range(3):
        print(f"  gap {gaps[i]}: physical {loss_phys[i]} dB/cm, kappa^2 {100*k2_phys[i]:.2f} %; mirror {loss_mirr[i]} dB/cm, kappa^2 {100*k2_mirr[i]:.2f} %; "
              f"regime {'over' if t[i] < a[i] else 'under'}-coupled")
    T = lambda dl, a_, t_: (a_ ** 2 - 2 * a_ * t_ * np.cos(2 * np.pi * dl / FSR) + t_ ** 2) / (1 - 2 * a_ * t_ * np.cos(2 * np.pi * dl / FSR) + (a_ * t_) ** 2)
    rng = np.random.default_rng(12)
    fig = plt.figure(figsize=(6.3, 2.55))
    ax = fig.add_axes([0.075, 0.18, 0.31, 0.72])
    dl = np.linspace(-0.04, 0.04, 161)
    cols = [C1, C3, C2]
    for i in range(3):
        y = T(dl, a[i], t[i]) + 0.012 * rng.standard_normal(dl.size)
        ax.plot(dl * 1000, y, ".", ms=1.8, color=cols[i])
        ax.plot(dl * 1000, T(dl, a[i], t[i]), color=cols[i], lw=1.0, label=f"{gaps[i]} nm")
        Tm = T(0, a[i], t[i]); fw = (1 - a[i] * t[i]) * LAM0 ** 2 / (np.pi * NG * 2 * np.pi * R * 1000 * np.sqrt(a[i] * t[i]))
        print(f"    resonance: extinction {-10*np.log10(Tm):.1f} dB, FWHM {fw*1000:.1f} pm, Q_L {LAM0/fw:.0f}")
        assert np.allclose(T(dl, a[i], t[i]), T(dl, t[i], a[i]))
    ax.set_xlim(-40, 40); ax.set_ylim(-0.05, 1.08)
    finish(ax, xlabel="detuning (pm)", ylabel="through-port transmission")
    ax.legend(loc="lower left", fontsize=6.3, title="gap", title_fontsize=6.3, handlelength=1.0)
    tag(ax, "a")
    b = fig.add_axes([0.47, 0.18, 0.21, 0.72])
    b.plot(gaps, loss_phys, "o-", color=C1, ms=4, label="solution 1")
    b.plot(gaps, loss_mirr, "s--", color=C4, ms=4, mfc="white", label="solution 2")
    b.set_xticks(gaps); b.set_ylim(0, 10)
    finish(b, xlabel="gap (nm)", ylabel="fitted loss (dB/cm)")
    b.legend(loc="upper right", fontsize=6.3)
    tag(b, "b")
    c = fig.add_axes([0.77, 0.18, 0.21, 0.72])
    c.plot(gaps, 100 * k2_phys, "o-", color=C1, ms=4)
    c.plot(gaps, 100 * k2_mirr, "s--", color=C4, ms=4, mfc="white")
    c.set_xticks(gaps); c.set_ylim(0, 1.4)
    finish(c, xlabel="gap (nm)", ylabel="fitted coupling κ² (%)")
    tag(c, "c")
    save(fig, "ch32_ringgap")


# ------------------------------------------------------------------ Figure 32.5
def bragg_r(lam_nm, kappa_um, L_um, Lam_um, neff, alpha_um=0.0):
    """Coupled-mode reflection of a uniform grating; neff is a callable in nm."""
    beta = 2 * np.pi * neff(lam_nm) / (lam_nm / 1000)
    d = beta - np.pi / Lam_um - 1j * alpha_um / 2
    s = np.sqrt(kappa_um ** 2 - d ** 2 + 0j)
    r = -1j * kappa_um * np.sinh(s * L_um) / (s * np.cosh(s * L_um) + 1j * d * np.sinh(s * L_um))
    return np.abs(r) ** 2


def fig_bragg():
    neff0, ng0, _ = disp()
    LAMB, KAP, NPER = 0.317, 40e-3, 1000         # PDK period (um); illustrative kappa (per um = 40 /mm) and length (periods)
    L = NPER * LAMB
    dn = -0.008                                   # the corrugation lowers the average n_eff (illustrative)
    neff = lambda x: neff0(x) + dn
    rng = np.random.default_rng(5)
    lam = np.arange(1530.0, 1560.0001, 0.005)
    R = bragg_r(lam, KAP, L, LAMB, neff)
    Rm = R * (1 + 0.01 * rng.standard_normal(lam.size)) + 10 ** (-4.0) * (1 + 0.5 * rng.standard_normal(lam.size)) ** 2
    RdB = 10 * np.log10(Rm)
    # analysis: the first nulls either side of the stop band (minima of R next to the main peak)
    ipk = np.argmax(R)
    def first_null(direction):
        i = ipk
        while 0 < i < lam.size - 1 and not (R[i] < R[i - 1] and R[i] < R[i + 1] and R[i] < 0.5 * R[ipk]):
            i += direction
        return i
    il, ir = first_null(-1), first_null(+1)
    dlam = lam[ir] - lam[il]; lc = (lam[ir] + lam[il]) / 2
    ngc = ng0(lc)
    k_simple = np.pi * ngc * dlam / (lc ** 2) * 1e3            # per um -> computed in nm units: pi n_g dlam / lam^2 (1/nm) -> per um x1e3
    k_exact = np.sqrt(k_simple ** 2 - (np.pi / L) ** 2)
    neff_ext = lc / (2 * LAMB * 1000)
    print(f"Bragg: kappa L = {KAP*L:.1f}; peak R {R[ipk]:.4f} (tanh^2 = {np.tanh(KAP*L)**2:.4f}); nulls {lam[il]:.2f} / {lam[ir]:.2f} nm -> "
          f"dlam {dlam:.2f} nm, centre {lc:.2f} nm; n_g {ngc:.3f}; kappa simple {k_simple*1e3:.1f} /mm, with finite length {k_exact*1e3:.1f} /mm "
          f"(true {KAP*1e3:.0f}); n_eff = lc/(2 Lambda) = {neff_ext:.4f} (model at lc: {neff(lc):.4f})")
    fig = plt.figure(figsize=(6.3, 2.55))
    a = fig.add_axes([0.08, 0.17, 0.45, 0.74])
    a.plot(lam, RdB, color=C1, lw=0.6)
    a.set_xlim(1530, 1560); a.set_ylim(-45, 19)
    for i in (il, ir):
        a.axvline(lam[i], color=MUTED, lw=0.6, ls=":")
    a.annotate("", xy=(lam[ir], 2.0), xytext=(lam[il], 2.0), arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))
    a.text(lc, 2.6, f"Δλ = {dlam:.1f} nm", ha="center", va="bottom", fontsize=6.5, color=INK)
    a.text(1530.5, 17.5, f"centre {lc:.1f} nm\n→ $n_\\mathrm{{eff}}$ = λ/2Λ = {neff_ext:.3f}", fontsize=6.4, color=INK, va="top")
    a.text(1559.5, 17.5, f"κ ≈ π$n_g$Δλ/λ²\n= {k_simple*1e3:.0f} mm$^{{-1}}$", fontsize=6.4, color=INK, va="top", ha="right")
    finish(a, xlabel="wavelength (nm)", ylabel="reflection (dB)")
    tag(a, "a")
    b = fig.add_axes([0.65, 0.17, 0.33, 0.74])
    kl = np.logspace(-0.3, 1.5, 200)
    b.semilogx(kl, np.sqrt(1 + (np.pi / kl) ** 2), color=C1)
    ex13 = 12.6e-3 * 95.0
    for x, txt, dx in ((ex13, "Example 13.2", 1.25), (KAP * L, "panel a", 1.0)):
        yv = np.sqrt(1 + (np.pi / x) ** 2)
        b.plot([x], [yv], "o", ms=4, mfc="white", mec=INK)
        b.text(x * dx, yv + (0.15 if dx > 1 else 0.22), f"{txt}: ×{yv:.2f}", fontsize=6.3, color=INK, ha="left" if dx > 1 else "center")
        print(f"  kappa L = {x:.2f}: simple formula overestimates kappa x{yv:.2f}")
    b.set_ylim(0.8, 3.6); b.set_xlim(0.5, 30)
    finish(b, xlabel="κL", ylabel="simple κ / true κ")
    tag(b, "b")
    save(fig, "ch32_bragg")


# ------------------------------------------------------------------ Figure 32.6
def fig_wafer():
    """Synthetic wafer: the thickness and width variations of Worked Example 29.1 (6 nm each, centre to edge) and a
    random die-to-die width of sigma 1.5 nm, turned into ring-resonance shifts with 0.6 and 1.4 nm per nm. The analysis
    fits a radial bowl (wafer-scale part) and looks at what is left (die-to-die part)."""
    DWS, DTS = 0.6, 1.4                                  # nm per nm (Chapters 6 and 29)
    rng = np.random.default_rng(29)
    R, P = 100.0, 15.0                                   # wafer radius and die pitch, mm
    g = np.arange(-R, R + 0.1, P) + P / 2
    X, Y = np.meshgrid(g, g); X, Y = X.ravel(), Y.ravel()
    keep = np.hypot(np.abs(X) + P / 2, np.abs(Y) + P / 2) <= R
    X, Y = X[keep], Y[keep]; r = np.hypot(X, Y) / R
    dt = -3.0 + 6.0 * r ** 2 + 0.6 * X / R                          # thickness: bowl, thin centre, thick edge, slight tilt (nm)
    dw = -3.0 + 6.0 * r ** 2 + 0.6 * Y / R + 1.5 * rng.standard_normal(X.size)   # width: dose bowl + tilt + random 1.5 nm
    dl = DWS * dw + DTS * dt + 0.05 * rng.standard_normal(X.size)               # resonance shift (nm), small fit error
    c = np.polyfit(r ** 2, dl, 1); fit = np.polyval(c, r ** 2); res = dl - fit
    print(f"wafer: {X.size} dies; shift sd {dl.std():.2f} nm, range {dl.max()-dl.min():.1f} nm; fitted bowl {c[0]:+.2f} nm centre to edge "
          f"(model {6*DWS + 6*DTS:.1f}); residual sd {res.std():.2f} nm (random width alone {DWS*1.5:.2f} nm)")
    fig = plt.figure(figsize=(6.3, 2.6))
    a = fig.add_axes([0.08, 0.17, 0.4, 0.74])
    rr = np.linspace(0, 1, 50)
    a.fill_between(rr * R, np.polyval(c, rr ** 2) - res.std(), np.polyval(c, rr ** 2) + res.std(), color=C1, alpha=0.15, lw=0)
    a.plot(r * R, dl, "o", ms=3, color=C1, mfc="white", mew=0.8)
    a.plot(rr * R, np.polyval(c, rr ** 2), color=INK, lw=1.0)
    a.set_xlim(0, 100)
    finish(a, xlabel="die distance from the wafer centre (mm)", ylabel="resonance shift (nm)")
    a.text(3, dl.max(), f"wafer-scale bowl:\n{c[0]:+.1f} nm centre to edge", fontsize=6.5, color=INK, va="top")
    a.text(97, dl.min(), f"band: ±{res.std():.1f} nm\n(die to die)", fontsize=6.5, color=C1, va="bottom", ha="right")
    tag(a, "a")
    b = fig.add_axes([0.6, 0.17, 0.38, 0.74])
    bins = np.arange(-8, 8.01, 0.5)
    b.hist(dl - dl.mean(), bins=bins, color=C2, alpha=0.55, label=f"all variation, σ = {dl.std():.1f} nm")
    b.hist(res, bins=bins, color=C1, alpha=0.75, label=f"after removing the bowl, σ = {res.std():.1f} nm")
    b.set_xlim(-8, 8)
    finish(b, xlabel="resonance shift from the mean (nm)", ylabel="number of dies")
    b.legend(loc="upper left", fontsize=6.3, bbox_to_anchor=(0.0, 1.02))
    b.set_ylim(0, b.get_ylim()[1] * 1.35)
    tag(b, "b")
    save(fig, "ch32_wafer")


if __name__ == "__main__":
    which = sys.argv[1:] or ["calib", "ng", "cutback", "ringgap", "bragg", "wafer"]
    for k in which:
        globals()["fig_" + k]()
