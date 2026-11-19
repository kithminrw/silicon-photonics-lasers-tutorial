"""Lab 9: analyse measured openEBL data (Open-Photonics, Chapter 32), here simulated files that imitate it.

Run it from a terminal, with the data files in a folder data/ beside this script:
    python lab09_make_data.py           # once: writes data/lab09_*.csv (or download them from the lab page)
    python lab09_analysis.py            # prints every checkpoint and saves lab09_analysis.png
    python lab09_analysis.py --no-plot  # numbers only

It needs NumPy, and Matplotlib for the figure. The fits are written out here (Levenberg-Marquardt on a
numerical Jacobian), so SciPy is not needed. Wavelengths are in nm and powers in dBm, as in openEBL files.
load_spectrum also reads real openEBL CSV files, which store each variable as a row (see the lab page).
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-09/
"""
import pathlib
import re
import sys

import numpy as np

DATA = pathlib.Path(__file__).resolve().parent / "data"
RING_R = 10.0          # ring radius, um (from the layout)
MZI_DL = 100.0         # MZI arm-length difference, um (from the layout)
NG_GUESS = 4.18        # only to start the fringe search; the MZI measures the real value


# ---------------------------------------------------------------------------------------------------------
# Part A. Reading a sweep file, and the grating couplers' envelope (Chapter 32, Sections 32.1 and 32.2)
# ---------------------------------------------------------------------------------------------------------
def load_spectrum(path, channel=None):
    """Wavelength (nm), power (dBm) and the header of one sweep file.

    Reads both layouts: columns (a row of labels 'wavelength,channel_1', then numbers, as the simulated files)
    and rows (real openEBL files: a line 'wavelength,1475,1475.008,...', then 'channel_1,...', 'channel_2,...').
    Header lines start with '#' and hold 'key: value'. Without `channel`, the strongest channel is returned:
    the detector that saw the device's output.
    """
    meta, rows = {}, []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if s.startswith("#"):
                key, _, val = s.lstrip("#").strip().partition(":")
                if val:
                    meta[key.strip()] = val.strip()
            elif s:
                rows.append([c.strip() for c in s.split(",") if c.strip()])

    def is_number(c):
        try:
            float(c)
            return True
        except ValueError:
            return False

    if len(rows[0]) > 1 and is_number(rows[0][1]):                     # rows: label, then values
        table = {r[0]: np.array(r[1:], float) for r in rows if not is_number(r[0])}
    else:                                                               # columns: labels, then numbers
        data = np.array(rows[1:], float)
        table = {lab: data[:, k] for k, lab in enumerate(rows[0])}
    wl = next(v for k, v in table.items() if k.lower().startswith("wavelength"))
    if wl.max() < 1e-3:                                                 # metres
        wl = wl * 1e9
    chans = {k: v for k, v in table.items() if k.lower().startswith("channel")}
    name = channel or max(chans, key=lambda k: np.nanmax(chans[k]))
    return wl, chans[name], meta


def true_value(meta, key):
    """First number of a '# True key:' header line (simulated files only), or None."""
    m = re.search(r"-?\d+\.?\d*(e-?\d+)?", meta.get("True " + key, ""))
    return float(m.group()) if m else None


def coupler_envelope(wl, p, within_db=6.0):
    """Fit a parabola in dB to the top of a loopback: its peak, its centre and one coupler's 1 dB bandwidth.

    A Gaussian passband is a parabola in dB. The loopback holds two couplers, so it falls by 2 dB where
    each coupler falls by 1 dB: p = peak - 8 ((wl - centre) / BW1)^2.
    """
    top = p > p.max() - within_db
    c2, c1, c0 = np.polyfit(wl[top] - 1550, p[top], 2)
    centre = 1550 - c1 / (2 * c2)
    return {"peak": c0 - c1 ** 2 / (4 * c2), "centre": centre, "bw1": np.sqrt(-8 / c2),
            "poly": lambda x: np.polyval([c2, c1, c0], x - 1550)}


def fringe_cavity(wl, residual_db, ng=NG_GUESS, lengths=np.arange(20.0, 2000.0, 1.0)):
    """Find the Fabry-Perot cavity behind a ripple: fit A cos + B sin of 4 pi n_g L / lambda for each L.

    Fringes between two reflections a distance L apart repeat every lambda^2 / (2 n_g L), so the best L
    says where the reflections are, and the amplitude gives the peak-to-peak ripple.
    """
    nu = 1 / wl
    amp = np.empty(lengths.size)
    for k, L in enumerate(lengths):
        ph = 4 * np.pi * ng * L * 1e3 * nu
        M = np.column_stack([np.cos(ph), np.sin(ph), np.ones_like(ph)])
        c = np.linalg.lstsq(M, residual_db, rcond=None)[0]
        amp[k] = np.hypot(c[0], c[1])
    k = np.argmax(amp)
    return lengths[k], 2 * amp[k]


# ---------------------------------------------------------------------------------------------------------
# Part B. Group index from an unbalanced MZI (Section 32.4, Chapter 11)
# ---------------------------------------------------------------------------------------------------------
def calibrate(wl, p, wl_ref, p_ref):
    """Device minus loopback, in dB: the couplers' envelope cancels (Section 32.2)."""
    return p - np.interp(wl, wl_ref, p_ref)


def fringe_troughs(wl, t_lin, fsr_guess):
    """Wavelengths of the MZI's troughs, with each fringe's highest and lowest transmission.

    Take the lowest point of each fringe, then fit A + B cos(2 pi x / FSR) + C sin(2 pi x / FSR) to the
    points within a quarter of an FSR of it: an MZI's output is a sinusoid in the phase, so the fit's
    minimum is the trough, between the sampled points, and A -+ sqrt(B^2 + C^2) are its extremes.
    """
    step = wl[1] - wl[0]
    half = int(0.4 * fsr_guess / step)
    lows = [i for i in range(half, wl.size - half) if t_lin[i] == t_lin[i - half:i + half + 1].min()]
    out, tmin, tmax = [], [], []
    for i in lows:
        sel = np.abs(wl - wl[i]) <= fsr_guess / 4
        ph = 2 * np.pi * (wl[sel] - wl[i]) / fsr_guess
        A, B, C = np.linalg.lstsq(np.column_stack([np.ones_like(ph), np.cos(ph), np.sin(ph)]), t_lin[sel], rcond=None)[0]
        out.append(wl[i] + np.arctan2(-C, -B) * fsr_guess / (2 * np.pi))   # B cos + C sin is lowest at phase atan2(-C, -B)
        tmin.append(A - np.hypot(B, C))
        tmax.append(A + np.hypot(B, C))
    return np.array(out), np.array(tmin), np.array(tmax)


def line_fit(x, y):
    """Least-squares line y = c0 + c1 x with the standard errors of both (Section 32.3)."""
    n, xm = x.size, x.mean()
    sxx = ((x - xm) ** 2).sum()
    c1 = ((x - xm) * (y - y.mean())).sum() / sxx
    c0 = y.mean() - c1 * xm
    sy = np.sqrt(((y - c0 - c1 * x) ** 2).sum() / (n - 2))     # scatter of the points about the line
    return c0, c1, sy * np.sqrt(1 / n + xm ** 2 / sxx), sy / np.sqrt(sxx), sy


def mzi_group_index(wl, cal_db, dl_um, ng_guess=NG_GUESS):
    """n_g = lambda^2 / (FSR dL) from each pair of neighbouring troughs, and a straight line through them."""
    t = 10 ** (cal_db / 10)
    lam_c = 0.5 * (wl[0] + wl[-1])
    troughs, tmin, tmax = fringe_troughs(wl, t, lam_c ** 2 / (ng_guess * dl_um * 1e3))
    fsr = np.diff(troughs)
    mid = 0.5 * (troughs[1:] + troughs[:-1])
    ng = mid ** 2 / (fsr * dl_um * 1e3)
    g0, g1, s0, s1, _ = line_fit(mid - 1550, ng)
    er = np.median(10 * np.log10(tmax / tmin))
    return {"troughs": troughs, "mid": mid, "fsr": fsr, "ng": ng, "ng1550": g0, "slope": g1, "s_ng": s0, "s_slope": s1,
            "er": er}


# ---------------------------------------------------------------------------------------------------------
# Part C. Fitting a ring resonance: Lorentzian and all-pass models (Section 32.5, Chapter 12)
# ---------------------------------------------------------------------------------------------------------
def levenberg_marquardt(resid, p0, h, ok=lambda p: True, iters=200):
    """Minimise sum(resid(p)^2). h: the finite-difference step of each parameter; ok(p): a constraint.

    Gauss-Newton steps (J^T J) dp = J^T r, damped towards gradient descent when a step fails.
    Returns the parameters, their covariance s^2 (J^T J)^-1 and the sum of squares.
    """
    p = np.array(p0, float)
    r = resid(p)
    S, lam = r @ r, 1e-3

    def jac(p):
        return np.column_stack([(resid(p + h[k] * np.eye(p.size)[k]) - resid(p - h[k] * np.eye(p.size)[k])) / (2 * h[k])
                                for k in range(p.size)])
    for _ in range(iters):
        J = -jac(p)                                   # derivative of the model, since resid = data - model
        A, g = J.T @ J, J.T @ r
        while lam < 1e12:
            dp = np.linalg.solve(A + lam * np.diag(np.diag(A)), g)
            pn = p + dp
            if ok(pn):
                rn = resid(pn)
                if rn @ rn < S:
                    break
            lam *= 10
        else:
            break
        done = S - rn @ rn < 1e-12 * S
        p, r, S, lam = pn, rn, rn @ rn, lam / 10
        if done:
            break
    J = -jac(p)
    cov = (S / (r.size - p.size)) * np.linalg.inv(J.T @ J)
    return p, cov, S


def lorentz_db(x, p):
    """Baseline (a parabola in dB) plus a Lorentzian dip of depth D and full width w, centred at x0."""
    x0, w, D, b0, b1, b2 = p
    return b0 + b1 * x + b2 * x * x + 10 * np.log10(1 - D / (1 + (2 * (x - x0) / w) ** 2))


def allpass_db(x, p, fsr):
    """Baseline plus the all-pass ring of Section 12.2, with the round-trip phase 2 pi (x - x0) / FSR."""
    x0, a, t, b0, b1, b2 = p
    c = np.cos(2 * np.pi * (x - x0) / fsr)
    return b0 + b1 * x + b2 * x * x + 10 * np.log10((a * a - 2 * a * t * c + t * t) / (1 - 2 * a * t * c + (a * t) ** 2))


def fit_ring(wl, p, ng, radius_um=RING_R, centre=None, span=12):
    """Fit one through-port resonance. Returns the Lorentzian results and both all-pass solutions.

    The window is +-span FWHM around the dip (centre, or the lowest point). The baseline (couplers' envelope,
    fringes) is a parabola in dB fitted with the dip: the local envelope of Section 32.2.
    """
    sm = np.convolve(p, np.ones(5) / 5, mode="same")                  # a 5-point moving average
    sm[:2] = sm[-2:] = np.inf
    ref = wl[np.argmin(sm)] if centre is None else centre
    i0 = np.argmin(np.where(np.abs(wl - ref) < 0.05, sm, np.inf))      # the lowest point near the centre
    base = np.percentile(sm[np.isfinite(sm) & (np.abs(wl - wl[i0]) < 0.3)], 90)
    D0 = 1 - 10 ** ((sm[i0] - base) / 10)
    below = 10 ** ((sm - base) / 10) < 1 - D0 / 2                     # half-depth crossings give a first width
    j = i0
    while j < wl.size - 1 and below[j]:
        j += 1
    k = i0
    while k > 0 and below[k]:
        k -= 1
    w0 = max(wl[j] - wl[k], 2 * (wl[1] - wl[0]))
    sel = np.abs(wl - wl[i0]) < span * w0
    xc = wl[i0]
    x, y = wl[sel] - xc, p[sel]
    # Fit in linear power, scaled to about 1: near the bottom of a deep dip a tiny wavelength error is a large
    # error in dB, and a fit in dB would let those few points steer the result.
    scale = 10 ** (base / 10)
    lin = 10 ** (y / 10) / scale
    # Lorentzian
    lor, lcov, lS = levenberg_marquardt(lambda q: lin - 10 ** (lorentz_db(x, q) / 10) / scale, [0.0, w0, D0, base, 0.0, 0.0],
                                        h=np.array([1e-5, 1e-5, 1e-5, 1e-4, 1e-4, 1e-3]),
                                        ok=lambda q: q[1] > 0 and 0 < q[2] < 1)
    w, D = lor[1], lor[2]
    # the two all-pass solutions that match this width and depth (Section 12.4): a t from the FWHM ...
    fsr = xc ** 2 / (ng * 2 * np.pi * radius_um * 1e3)
    F = np.pi * w / fsr
    at = ((-F + np.sqrt(F * F + 4)) / 2) ** 2
    diff = np.sqrt(1 - D) * (1 - at)                                  # ... and |a - t| from the depth
    s = np.sqrt(diff ** 2 + 4 * at)
    hi, lo = (s + diff) / 2, (s - diff) / 2
    sols = {}
    for regime, (a0, t0) in (("under", (lo, hi)), ("over", (hi, lo))):
        side = (lambda q: q[2] > q[1]) if regime == "under" else (lambda q: q[2] < q[1])
        q, cov, S = levenberg_marquardt(lambda q: lin - 10 ** (allpass_db(x, q, fsr) / 10) / scale, [lor[0], a0, t0, *lor[3:]],
                                        h=np.array([1e-5, 1e-7, 1e-7, 1e-4, 1e-4, 1e-3]),
                                        ok=lambda q: 0 < q[1] < 1 and 0 < q[2] < 1 and side(q))
        a, t = q[1], q[2]
        L_cm = 2 * np.pi * radius_um * 1e-4
        sols[regime] = {"a": a, "t": t, "s_a": np.sqrt(cov[1, 1]), "s_t": np.sqrt(cov[2, 2]), "chi2": S,
                        "loss": -20 * np.log10(a) / L_cm, "s_loss": 20 / np.log(10) / a / L_cm * np.sqrt(cov[1, 1]),
                        "k2": 1 - t * t, "s_k2": 2 * t * np.sqrt(cov[2, 2]), "p": q}
    return {"lam0": xc + lor[0], "fwhm": w, "s_fwhm": np.sqrt(lcov[1, 1]), "Q": (xc + lor[0]) / w,
            "ext": -10 * np.log10(1 - D), "s_ext": 10 / np.log(10) * np.sqrt(lcov[2, 2]) / (1 - D), "depth": D,
            "lor": lor, "chi2_lor": lS, "x": x, "y": y, "xc": xc, "fsr": fsr, "sols": sols}


# ---------------------------------------------------------------------------------------------------------
# Part D. Under or over? Resolve the ambiguity with the gap series (Worked Example 32.1)
# ---------------------------------------------------------------------------------------------------------
def resolve_gap_series(fits):
    """Choose one solution per ring so that the loss is the same for all gaps.

    Each of the 2^N choices gives N losses; the physical one is where they agree within their error bars
    (smallest chi^2 about their weighted mean), since the gap cannot change the loss of the whole ring.
    """
    best = None
    for code in range(2 ** len(fits)):
        pick = ["over" if code >> k & 1 else "under" for k in range(len(fits))]
        ls = np.array([f["sols"][r]["loss"] for f, r in zip(fits, pick)])
        ws = 1 / np.array([f["sols"][r]["s_loss"] for f, r in zip(fits, pick)]) ** 2
        mean = (ws * ls).sum() / ws.sum()
        chi2 = (ws * (ls - mean) ** 2).sum()
        if best is None or chi2 < best[0]:
            best = (chi2, pick, mean, 1 / np.sqrt(ws.sum()))
    return best


# ---------------------------------------------------------------------------------------------------------
# Part E. Propagation loss by cutback (Section 32.3, Chapter 7)
# ---------------------------------------------------------------------------------------------------------
def insertion_loss(wl, p, p_laser, lam=1550.0, half=1.0):
    """Insertion loss at lam: the laser power minus the received power averaged (in mW) over +-half nm."""
    sel = np.abs(wl - lam) <= half
    return p_laser - 10 * np.log10(np.mean(10 ** (p[sel] / 10)))


def length_from_name(path):
    """Cutback length in cm from a name ending in _<length>um.csv, as the SiEPIC files are named."""
    return float(re.search(r"(\d+)um", pathlib.Path(path).name).group(1)) * 1e-4


def main(plot=True):
    if not (DATA / "lab09_loopback.csv").exists():
        sys.exit(f"No data in {DATA}: run lab09_make_data.py first, or download the CSV files from the lab page.")
    print("Lab 9: analysing openEBL-style measurements (simulated data; wavelengths in nm, powers in dBm)\n")

    # ---- Part A
    wl_lb, p_lb, m_lb = load_spectrum(DATA / "lab09_loopback.csv")
    env = coupler_envelope(wl_lb, p_lb)
    p_laser = float(m_lb.get("Laser power", "0").split()[0])
    gc_peak = (p_laser - env["peak"] - 0.06) / 2                    # minus 300 um of waveguide at ~2 dB/cm
    near = np.abs(wl_lb - env["centre"]) < 25
    L_fp, ripple = fringe_cavity(wl_lb[near], p_lb[near] - env["poly"](wl_lb[near]))
    off = true_value(m_lb, "coupler-pair loss offset")
    print("A. Loopback: the grating couplers' envelope")
    print(f"   peak {env['peak']:.2f} dBm at {env['centre']:.1f} nm: {gc_peak:.2f} dB per coupler"
          f"   (true {6.0 + off / 2:.2f} dB: 6.0 dB plus half this pair's offset of {off:+.2f} dB; centre"
          f" {1548 + true_value(m_lb, 'coupler centre offset'):.1f} nm)")
    print(f"   1 dB bandwidth of one coupler {env['bw1']:.1f} nm   (true 32 nm; Chapter 31: a 30-40 nm wide passband)")
    print(f"   ripple {ripple:.2f} dB peak to peak, repeating every {1550**2 / (2 * NG_GUESS * L_fp * 1e3):.2f} nm:"
          f" reflections {L_fp:.0f} um apart   (true: 300 um, R = 1.6 %, 0.27 dB p-p)\n")

    # ---- Part B
    wl_m, p_m, m_m = load_spectrum(DATA / "lab09_mzi_dL100.csv")
    cal = calibrate(wl_m, p_m, wl_lb, p_lb)
    band = np.interp(wl_m, wl_lb, p_lb) > env["peak"] - 10            # where the couplers pass light: within 10 dB
    mzi = mzi_group_index(wl_m[band], cal[band], MZI_DL)
    ng_true, slope_true = true_value(m_m, "n_g at 1550 nm"), 1.12e-4
    fsr1550 = 1550 ** 2 / (mzi["ng1550"] * MZI_DL * 1e3)
    print("B. Unbalanced MZI, dL = 100 um, divided by the loopback")
    print(f"   {mzi['troughs'].size} troughs from {mzi['troughs'][0]:.1f} to {mzi['troughs'][-1]:.1f} nm;"
          f" FSR at 1550 nm {fsr1550:.3f} nm   (true {true_value(m_m, 'FSR at 1550 nm'):.3f}; Chapter 11: 5.75 nm)")
    print(f"   n_g(1550) = {mzi['ng1550']:.4f} +- {mzi['s_ng']:.4f}   (true {ng_true:.4f}; Chapters 6 and 32: 4.18)")
    print(f"   dn_g/dlambda = {1e4 * mzi['slope']:.2f} +- {1e4 * mzi['s_slope']:.2f} x 1e-4 per nm   (true {1e4 * slope_true:.2f})")
    split = (1 + 10 ** (-mzi["er"] / 20)) / 2                         # (s - (1 - s)) / (s + (1 - s)) = 2 s - 1
    er_true = true_value({"True x": m_m["True Y-branch split and loss"].split("extinction")[1]}, "x")
    print(f"   fringe extinction {mzi['er']:.1f} dB, so the Y-branches split {split:.3f} / {1 - split:.3f}"
          f"   (true {er_true:.1f} dB, 0.530 / 0.470; Chapter 11: the depth measures the splitters' balance)\n")

    # ---- Part C
    fits, metas = [], []
    for gap in (200, 250, 300):
        wl_r, p_r, m_r = load_spectrum(DATA / f"lab09_ring_r10_g{gap}.csv")
        ng_here = mzi["ng1550"] + mzi["slope"] * (wl_r.mean() - 1550)
        f = fit_ring(wl_r, p_r, ng_here)
        f["gap"] = gap
        fits.append(f)
        metas.append(m_r)
    table = {200: (22.3, 70000, 4.1), 250: (11.7, 132000, 11.0), 300: (7.4, 211000, 16.7)}
    print("C. Ring resonances, Lorentzian fit (10 um radius; window +-12 FWHM; baseline a parabola in dB)")
    for f, m in zip(fits, metas):
        fw, q, ex = table[f["gap"]]
        print(f"   {f['gap']} nm gap: dip at {f['lam0']:.3f} nm, FWHM {1e3 * f['fwhm']:.2f} +- {1e3 * f['s_fwhm']:.2f} pm,"
              f" Q_L {f['Q']:,.0f} +- {f['Q'] * f['s_fwhm'] / f['fwhm']:,.0f}, extinction {f['ext']:.2f} +- {f['s_ext']:.2f} dB")
        print(f"      true {true_value(m, 'FWHM'):.2f} pm, {true_value(m, 'loaded Q'):,.0f}, {true_value(m, 'extinction'):.2f} dB"
              f"   (Table 12.1: {fw} pm, {q:,}, {ex} dB)")
    print()

    # ---- Part D
    print("D. All-pass fits: two solutions per ring, equally good")
    for f, m in zip(fits, metas):
        u, o = f["sols"]["under"], f["sols"]["over"]
        print(f"   {f['gap']} nm: under-coupled a = {u['a']:.6f}, t = {u['t']:.6f}: {u['loss']:.2f} +- {u['s_loss']:.2f} dB/cm,"
              f" kappa^2 {100 * u['k2']:.3f} %")
        print(f"           over-coupled  a = {o['a']:.6f}, t = {o['t']:.6f}: {o['loss']:.2f} +- {o['s_loss']:.2f} dB/cm,"
              f" kappa^2 {100 * o['k2']:.3f} %   (chi^2 ratio {o['chi2'] / u['chi2']:.4f})")
        print(f"           true a = {true_value(m, 'a'):.6f}, t = {true_value(m, 't'):.6f}"
              f" (kappa^2 {true_value(m, 'kappa^2'):.3f} %, {m['True regime'].split(' (')[0]})")
    chi2, pick, mean, s_mean = resolve_gap_series(fits)
    other = ["over" if r == "under" else "under" for r in pick]
    phys = [f["sols"][r] for f, r in zip(fits, pick)]
    mirror = [f["sols"][r] for f, r in zip(fits, other)]
    slope_k2 = np.polyfit([f["gap"] for f in fits], np.log([s["k2"] for s in phys]), 1)[0]
    losses = ", ".join("%.2f" % s["loss"] for s in phys)
    couplings = ", ".join("%.3f" % (100 * s["k2"]) for s in phys)
    print(f"   gap series: the choice ({', '.join(pick)}) gives losses {losses} dB/cm"
          f" (chi^2 {chi2:.1f} for 2 degrees of freedom)")
    print(f"      and couplings {couplings} %, falling {np.exp(-100 * slope_k2):.2f}x per 100 nm"
          "   (Table 12.1: 1.23, 0.52, 0.22 %; Chapter 9 model: 5.75x)")
    losses = ", ".join("%.1f" % s["loss"] for s in mirror)
    couplings = ", ".join("%.3f" % (100 * s["k2"]) for s in mirror)
    print(f"   the other set: losses {losses} dB/cm, couplings {couplings} %   (Worked Example 32.1: 8.6, 3.6, 1.5 dB/cm)")
    print(f"   ring loss, weighted mean: {mean:.2f} +- {s_mean:.2f} dB/cm   (true 2.00; Table 12.1: 2 dB/cm)\n")

    # ---- Part E
    files = sorted(DATA.glob("lab09_cutback_*um.csv"))
    lengths = np.array([length_from_name(p) for p in files])
    spectra = [load_spectrum(p) for p in files]
    il = np.array([insertion_loss(w, p, p_laser) for w, p, _ in spectra])
    c0, alpha, s_c0, s_alpha, sy = line_fit(lengths, il)
    lam_grid = np.arange(1500.0, 1596.0, 1.0)
    spec = np.array([line_fit(lengths, np.array([insertion_loss(w, p, p_laser, lam=l, half=0.5) for w, p, _ in spectra]))[1:4:2]
                     for l in lam_grid])
    il_lb = insertion_loss(wl_lb, p_lb, p_laser)
    print(f"E. Cutback: {lengths.size} waveguides, {', '.join(f'{L:g}' for L in lengths)} cm, insertion loss at 1550 nm")
    print(f"   loss {alpha:.2f} +- {s_alpha:.2f} dB/cm, scatter about the line {sy:.2f} dB   (true 2.00, coupler spread 0.25 dB;"
          " Chapters 7 and 12: 2 dB/cm)")
    print(f"   intercept {c0:.2f} +- {s_c0:.2f} dB: {c0 / 2:.2f} dB per coupler at 1550 nm   (true 6.02 dB; the loopback"
          f" gives {(il_lb - 0.06) / 2:.2f})")
    print(f"   loss spectrum 1500-1595 nm: {spec[:, 0].min():.2f} to {spec[:, 0].max():.2f} dB/cm, typical error"
          f" +-{np.median(spec[:, 1]):.2f}; with the rings ({mean:.2f} +- {s_mean:.2f}), weighted mean"
          f" {(alpha / s_alpha**2 + mean / s_mean**2) / (1 / s_alpha**2 + 1 / s_mean**2):.2f}"
          f" +- {1 / np.sqrt(1 / s_alpha**2 + 1 / s_mean**2):.2f} dB/cm\n")

    if plot:
        make_figure(wl_lb, p_lb, env, wl_m, p_m, cal, band, mzi, fits, pick, spectra, lengths, il, c0, alpha, lam_grid, spec)


def make_figure(wl_lb, p_lb, env, wl_m, p_m, cal, band, mzi, fits, pick, spectra, lengths, il, c0, alpha, lam_grid, spec):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 3, figsize=(14, 8))
    # (a) raw spectra
    a = ax[0, 0]
    a.plot(wl_m, p_m, color="tab:orange", lw=0.6, label="MZI, ΔL = 100 µm")
    a.plot(spectra[-1][0], spectra[-1][1], color="tab:green", lw=0.6, label=f"cutback, {lengths[-1]:g} cm")
    a.plot(wl_lb, p_lb, color="tab:blue", lw=0.8, label="loopback")
    top = p_lb > p_lb.max() - 6
    a.plot(wl_lb[top], env["poly"](wl_lb[top]), "k--", lw=1, label="parabola fit (top 6 dB)")
    a.axhline(-62, color="grey", ls=":", lw=0.8)
    a.text(1599, -61, "detector floor", ha="right", va="bottom", fontsize=8, color="grey")
    a.set(xlabel="wavelength (nm)", ylabel="detected power (dBm)", title="(a) raw sweeps", ylim=(-66, -8))
    a.legend(fontsize=8, loc="lower center")
    # (b) MZI divided by the loopback
    b = ax[0, 1]
    b.plot(wl_m[band], cal[band], color="tab:orange", lw=0.8)
    b.plot(mzi["troughs"], np.full(mzi["troughs"].size, -27.0), "k^", ms=4, label="troughs (sinusoid fits)")
    b.set(xlabel="wavelength (nm)", ylabel="MZI − loopback (dB)", title="(b) MZI after calibration", ylim=(-33, 2))
    b.legend(fontsize=8, loc="lower right")
    # (c) group index against wavelength
    c = ax[0, 2]
    c.plot(mzi["mid"], mzi["ng"], "o", color="tab:orange", ms=4, label="λ² / (FSR ΔL), each pair of troughs")
    x = np.array([mzi["mid"][0], mzi["mid"][-1]])
    c.plot(x, mzi["ng1550"] + mzi["slope"] * (x - 1550), color="tab:orange", label="straight-line fit")
    c.plot(x, 4.1836 + 1.12e-4 * (x - 1550), "k:", label="true (Chapter 6, femwell)")
    c.set(xlabel="wavelength (nm)", ylabel="group index", title="(c) group index from the MZI")
    c.legend(fontsize=8)
    # (d) the three resonances
    d = ax[1, 0]
    for f, col in zip(fits, ("tab:red", "tab:purple", "tab:blue")):
        q = f["sols"]["under"]["p"]
        base = q[3] + q[4] * f["x"] + q[5] * f["x"] ** 2
        det = 1e3 * (f["x"] - q[0])
        d.plot(det, f["y"] - base, ".", color=col, ms=2, alpha=0.5)
        xf = np.linspace(f["x"].min(), f["x"].max(), 800)
        d.plot(1e3 * (xf - q[0]), allpass_db(xf, q, f["fsr"]) - (q[3] + q[4] * xf + q[5] * xf ** 2), color=col,
               label=f"{f['gap']} nm: Q_L {f['Q'] / 1e3:.0f}k, {f['ext']:.1f} dB")
    d.set(xlim=(-80, 80), xlabel="detuning from resonance (pm)", ylabel="transmission, baseline removed (dB)",
          title="(d) rings: data and all-pass fits")
    d.legend(fontsize=8, loc="lower left")
    # (e) the two solutions of each ring
    e = ax[1, 1]
    for f, r, col in zip(fits, pick, ("tab:red", "tab:purple", "tab:blue")):
        for reg in ("under", "over"):
            s = f["sols"][reg]
            e.errorbar(100 * s["k2"], s["loss"], yerr=s["s_loss"], fmt="o" if reg == r else "s", color=col,
                       mfc=col if reg == r else "none", ms=6, label=f"{f['gap']} nm gap" if reg == r else None)
    k2 = np.linspace(0.1, 1.5, 200)
    e.plot(k2, -20 * np.log10(np.sqrt(1 - k2 / 100)) / (2 * np.pi * RING_R * 1e-4), "k:", lw=1, label="critical coupling (a = t)")
    e.axhline(2.0, color="grey", lw=0.6)
    e.set(xlabel="power coupling κ² (%)", ylabel="propagation loss (dB/cm)", title="(e) both solutions; filled = chosen",
          yscale="log", ylim=(1, 15))
    e.legend(fontsize=8, loc="upper right")
    # (f) cutback
    g = ax[1, 2]
    g.plot(lengths, il, "o", color="tab:green", label="insertion loss at 1550 nm")
    xl = np.array([0, lengths.max() * 1.05])
    g.plot(xl, c0 + alpha * xl, color="tab:green", label=f"fit: {alpha:.2f} dB/cm")
    g.set(xlabel="waveguide length (cm)", ylabel="insertion loss (dB)", title="(f) cutback")
    g.legend(fontsize=8, loc="upper left")
    ins = g.inset_axes([0.55, 0.12, 0.42, 0.33])
    ins.fill_between(lam_grid, spec[:, 0] - spec[:, 1], spec[:, 0] + spec[:, 1], color="tab:green", alpha=0.25, lw=0)
    ins.plot(lam_grid, spec[:, 0], color="tab:green", lw=1)
    ins.axhline(2.0, color="k", ls=":", lw=0.8)
    ins.set_ylim(0, 4)
    ins.set_title("loss (dB/cm) against λ (nm)", fontsize=7)
    ins.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig("lab09_analysis.png", dpi=150)
    print("Saved the figure as lab09_analysis.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
