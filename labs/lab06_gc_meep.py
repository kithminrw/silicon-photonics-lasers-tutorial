"""Lab 6: a grating coupler in 2D FDTD with MEEP (Open-Photonics, Chapter 15).

Run it from a terminal, on Linux or macOS (on Windows, in WSL or Docker):
    python lab06_gc_meep.py                   # every checkpoint (six FDTD runs) and the figure lab06_gc_meep.png
    python lab06_gc_meep.py --quick           # the same on a coarse grid, 20 pixels per um instead of 30
    python lab06_gc_meep.py --no-plot         # numbers only
    python lab06_gc_meep.py --resolution 60   # any grid, for a convergence check

It needs MEEP (conda install -c conda-forge pymeep), NumPy, and Matplotlib for the figure. All lengths are in
micrometres, so MEEP's unit of frequency is c/(1 um) and a frequency f is the vacuum wavelength 1/f.
MEEP may run on several threads (OpenMP); OMP_NUM_THREADS=1 holds it to one core, as for the times on the lab page.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-06/
"""
import sys
import time

import numpy as np

N_SI, N_OX = 3.476, 1.444   # silicon and silica at 1550 nm (no material dispersion in this lab)
T_SI, ETCH = 0.22, 0.07     # silicon thickness and shallow-etch depth
FF = 0.5                    # fill factor: the unetched fraction of each period
T_BOX = 2.0                 # buried-oxide thickness
N_PER = 30                  # number of grating periods
THETA_AIR = 8.0             # fibre angle from the normal, in air (degrees)
W0 = 5.2                    # fibre mode field radius: SMF-28, mode field diameter 10.4 um
LAM0 = 1.55
LAM_MIN, LAM_MAX = 1.45, 1.65   # wavelength range of every run

# The phase-matching model of the chapter's demo (gc.html): slab indices of the 220 and 150 nm films and their
# group indices, with the grating index taken as the fill-factor average
DEMO_N = (2.848, 2.539)
DEMO_NG = (3.58, 3.40)


# ---------------------------------------------------------------------------------------------------------
# Part A. The phase-matching estimate (Chapter 15, Section 15.1, Worked Example 15.1)
# ---------------------------------------------------------------------------------------------------------
def slab_te(d, n1=N_SI, n2=N_OX, n3=N_OX, lam=LAM0):
    """Effective index of the TE0 mode of a slab, by bisection on the eigenvalue equation (Lab 1)."""
    k0 = 2 * np.pi / lam

    def F(neff):
        kappa = k0 * np.sqrt(n1**2 - neff**2)
        return kappa * d - np.arctan(k0 * np.sqrt(neff**2 - n2**2) / kappa) - np.arctan(k0 * np.sqrt(neff**2 - n3**2) / kappa)
    a, b = max(n2, n3) + 1e-12, n1 - 1e-12
    for _ in range(60):
        c = 0.5 * (a + b)
        a, b = (c, b) if F(c) > 0 else (a, c)
    return 0.5 * (a + b)


def slab_group_index(d, n3=N_OX, dlam=0.005):
    """n_g = n_eff - lam dn_eff/dlam with constant material indices, as in the FDTD: waveguide dispersion only."""
    dn = (slab_te(d, n3=n3, lam=LAM0 + dlam) - slab_te(d, n3=n3, lam=LAM0 - dlam)) / (2 * dlam)
    return slab_te(d, n3=n3) - LAM0 * dn


def stack_te(layers, n_sub=N_OX, n_cov=N_OX, lam=LAM0):
    """TE0 index of a stack of layers [(index, thickness), ...] listed from the bottom up.

    E_y and dE_y/dy are carried up through the layers (cos/sin where the mode oscillates, cosh/sinh where it
    decays), starting from a field that decays into the substrate; a mode must also decay into the cover.
    The highest root of that condition is TE0.
    """
    k0 = 2 * np.pi / lam

    def F(neff):
        E, D = 1.0, k0 * np.sqrt(neff**2 - n_sub**2)
        for n, t in layers:
            q2 = k0**2 * (n**2 - neff**2)
            if q2 > 0:
                q = np.sqrt(q2)
                E, D = E * np.cos(q * t) + D * np.sin(q * t) / q, -E * q * np.sin(q * t) + D * np.cos(q * t)
            else:
                p = np.sqrt(-q2)
                E, D = E * np.cosh(p * t) + D * np.sinh(p * t) / p, E * p * np.sinh(p * t) + D * np.cosh(p * t)
        return D + k0 * np.sqrt(neff**2 - n_cov**2) * E
    grid = np.linspace(max(n for n, _ in layers) - 1e-9, max(n_sub, n_cov) + 1e-9, 2000)
    i = next(k for k in range(len(grid) - 1) if np.sign(F(grid[k])) != np.sign(F(grid[k + 1])))
    a, b = grid[i + 1], grid[i]
    for _ in range(60):
        c = 0.5 * (a + b)
        a, b = (c, b) if np.sign(F(c)) == np.sign(F(a)) else (a, c)
    return 0.5 * (a + b)


def phase_matched_wavelength(period, theta_air=THETA_AIR, ff=FF):
    """The demo's estimate: lambda = Lambda (n_eff(lambda) - sin theta), n_eff the fill-factor average of the slabs.

    Each slab index falls with wavelength at the rate its group index sets, so the equation is solved by iteration.
    """
    s = np.sin(np.radians(theta_air))

    def neff(lam):
        hi = DEMO_N[0] - (DEMO_NG[0] - DEMO_N[0]) * (lam - LAM0) / LAM0
        lo = DEMO_N[1] - (DEMO_NG[1] - DEMO_N[1]) * (lam - LAM0) / LAM0
        return ff * hi + (1 - ff) * lo
    lam = LAM0
    for _ in range(50):
        lam = period * (neff(lam) - s)
    return lam


# ---------------------------------------------------------------------------------------------------------
# Part B. The FDTD model: a uniform shallow-etched grating launched from the waveguide (Sections 15.1-15.3)
# ---------------------------------------------------------------------------------------------------------
# x runs along the waveguide, with x = 0 at the first groove's tooth; y is vertical, with y = 0 at the bottom of the
# silicon. The 2D model is a slice through the middle of a 12 um wide grating: the out-of-plane field Ez is the TE
# polarisation of the slab (electric field parallel to the layers and to the grating lines).
D_PML, X_IN, X_OUT, T_SUB, T_CLAD = 1.0, 2.0, 1.0, 0.4, 1.0
X_SRC, X_MODE = -1.6, -1.0           # eigenmode source and the mode monitor that measures the input and reflection
Y_UP = T_SI + 0.6                    # the line above the grating where the fibre's mode is overlapped


def simulate(period, t_box=T_BOX, res=30, n_per=N_PER, etch=ETCH, ff=FF, clad=N_OX, mirror=False, nfreq=41,
             field_map=False):
    """Run one FDTD simulation and return the power flows and the field above the grating, against wavelength.

    clad is the index above the silicon (1.0 for an air-clad chip); mirror=True puts a perfect metal under the BOX.
    Every power is a fraction of the incident mode's power, measured by mode decomposition at X_MODE.
    """
    import meep as mp
    mp.verbosity(0)
    L = n_per * period
    snap = lambda length: np.ceil(length * res - 1e-9) / res     # whole pixels: x = 0 and y = 0 lie on grid lines
    x_left, y_bot = -snap(X_IN + D_PML), -snap(t_box + T_SUB + D_PML)
    sx, sy = snap(L + X_OUT + D_PML - x_left), snap(T_SI + T_CLAD + D_PML - y_bot)
    x_right, y_top = x_left + sx, y_bot + sy
    cx, cy = x_left + sx / 2, y_bot + sy / 2           # the cell centre in these coordinates

    def V(x, y):
        return mp.Vector3(x - cx, y - cy)

    si, ox, cl = mp.Medium(index=N_SI), mp.Medium(index=N_OX), mp.Medium(index=clad)
    geometry = [mp.Block(mp.Vector3(2 * sx, -t_box - y_bot + 1, mp.inf), center=V(cx, (y_bot - 1 - t_box) / 2),
                         material=mp.metal if mirror else si)]                                   # substrate
    if clad != N_OX:                                                                             # buried oxide
        geometry.append(mp.Block(mp.Vector3(2 * sx, t_box, mp.inf), center=V(cx, -t_box / 2), material=ox))
    # A full 220 nm slab with grooves of cladding cut into it, so that every interface MEEP smooths is silicon
    # against cladding. (Stacking 70 nm silicon teeth on a 150 nm silicon slab leaves a low-index seam where the
    # two blocks meet inside a pixel, and one polygon for the whole profile was smoothed badly in our tests.)
    geometry.append(mp.Block(mp.Vector3(2 * sx, T_SI, mp.inf), center=V(cx, T_SI / 2), material=si))
    geometry += [mp.Block(mp.Vector3((1 - ff) * period, etch + 0.1, mp.inf),
                          center=V((i + (1 + ff) / 2) * period, T_SI - etch + (etch + 0.1) / 2), material=cl)
                 for i in range(n_per)]                                                          # the grooves
    fmin, fmax = 1 / LAM_MAX, 1 / LAM_MIN
    fcen, df = (fmin + fmax) / 2, fmax - fmin
    y_lo, y_hi = -1.0, 1.0                             # the waveguide's cross-section, clear of the substrate
    source = mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=2 * df), center=V(X_SRC, (y_lo + y_hi) / 2),
                                size=mp.Vector3(0, y_hi - y_lo), direction=mp.X, eig_band=1, eig_parity=mp.ODD_Z)
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=res, geometry=geometry, sources=[source],
                        boundary_layers=[mp.PML(D_PML)], default_material=cl)
    x0 = -0.6                                          # the horizontal monitors start after the mode monitor
    x1 = x0 + np.floor((L + X_OUT - x0) * res + 1e-9) / res    # and span whole pixels, as all monitors here do
    mode = sim.add_mode_monitor(fcen, df, nfreq, mp.ModeRegion(center=V(X_MODE, (y_lo + y_hi) / 2),
                                                               size=mp.Vector3(0, y_hi - y_lo)))
    up = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=V((x0 + x1) / 2, Y_UP), size=mp.Vector3(x1 - x0)))
    down = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=V((x0 + x1) / 2, -t_box - T_SUB / 2),
                                                       size=mp.Vector3(x1 - x0), weight=-1))
    out = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=V(L + X_OUT / 2, (y_lo + y_hi) / 2),
                                                      size=mp.Vector3(0, y_hi - y_lo)))
    line = sim.add_dft_fields([mp.Ez, mp.Hx], fcen, df, nfreq, center=V((x0 + x1) / 2, Y_UP),
                              size=mp.Vector3(x1 - x0))
    fmap = None
    if field_map:
        fmap = sim.add_dft_fields([mp.Ez], [1 / LAM0], center=V(cx, cy), size=mp.Vector3(sx - 2 * D_PML, sy - 2 * D_PML))
    t0 = time.time()
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, V(L + X_OUT / 2, T_SI / 2), 1e-3))
    coef = sim.get_eigenmode_coefficients(mode, [1], eig_parity=mp.ODD_Z)
    freqs = np.array(mp.get_flux_freqs(up))
    p_in = np.abs(coef.alpha[0, :, 0]) ** 2
    order = np.argsort(1 / freqs)                       # ascending wavelength
    run = {"lam": (1 / freqs)[order], "period": period, "t_box": t_box, "clad": clad, "n_per": n_per,
           "up": (np.array(mp.get_fluxes(up)) / p_in)[order],
           "down": (np.array(mp.get_fluxes(down)) / p_in)[order],
           "T": (np.array(mp.get_fluxes(out)) / p_in)[order],
           "R": (np.abs(coef.alpha[0, :, 1]) ** 2 / p_in)[order]}
    xs = sim.get_array_metadata(dft_cell=line)[0]
    run["x"] = np.asarray(xs) + cx
    run["Ez"] = np.array([sim.get_dft_array(line, mp.Ez, i) for i in range(nfreq)])[order]
    run["Hx"] = np.array([sim.get_dft_array(line, mp.Hx, i) for i in range(nfreq)])[order]
    if field_map:
        run["map"] = np.abs(sim.get_dft_array(fmap, mp.Ez, 0)).T
        run["eps"] = sim.get_array(component=mp.Dielectric, center=V(cx, cy),
                                   size=mp.Vector3(sx - 2 * D_PML, sy - 2 * D_PML)).T
        run["extent"] = (x_left + D_PML, x_right - D_PML, y_bot + D_PML, y_top - D_PML)
    run["seconds"] = time.time() - t0
    return run


# ---------------------------------------------------------------------------------------------------------
# Part B, continued. Into the fibre: overlap with a tilted Gaussian (Section 15.3), peak and bandwidth (Section 15.4)
# ---------------------------------------------------------------------------------------------------------
def fibre_overlap(run, x_f, theta_air=THETA_AIR, w0=W0):
    """Fraction of the power crossing the line above the grating that couples into the fibre's mode.

    The fibre mode is a Gaussian of waist w0 on the line, centred at x_f, tilted by the angle in the cladding
    (Snell's law from theta_air), with the phase slope k0 n_c sin(theta_c) = k0 sin(theta_air) along x and
    Hx = n_c cos(theta_c) Ez, a plane wave's ratio. The overlap of fields (E, H) with a mode (e, h) is
    Re[(int E h*)(int e H*) / int E H*] / Re(int e h*). The simulated field is zero beyond the ends of the line, but
    the fibre's mode is not, so its power Re(int e h*) is taken over all x: n_c cos(theta_c) w0 sqrt(pi/2)/cos(theta_c).
    """
    x, E, H = run["x"], run["Ez"], run["Hx"]
    dx = x[1] - x[0]
    th = np.arcsin(np.sin(np.radians(theta_air)) / run["clad"])
    k = 2 * np.pi * run["clad"] / run["lam"][:, None]
    X = x[None, :] - x_f
    e = np.exp(-(X * np.cos(th) / w0) ** 2 + 1j * k * np.sin(th) * X)
    h = run["clad"] * np.cos(th) * e
    a = np.sum(E * np.conj(h), axis=1) * dx
    b = np.sum(e * np.conj(H), axis=1) * dx
    return np.real(a * b / (np.sum(E * np.conj(H), axis=1) * dx)) / (run["clad"] * w0 * np.sqrt(np.pi / 2))


def coupling(run, theta_air=THETA_AIR, x_f=None):
    """Coupling efficiency into the fibre against wavelength, with the fibre where it couples best (unless x_f given).

    The fibre's position is chosen once, at the best wavelength, and then held fixed, as on a probe station.
    """
    if x_f is None:
        best = lambda xf: np.max(fibre_overlap(run, xf, theta_air) * run["up"])
        grid = np.arange(0.0, run["n_per"] * run["period"], 0.25)
        x_f = grid[np.argmax([best(xf) for xf in grid])]
        a, b = x_f - 0.25, x_f + 0.25                    # golden-section refinement
        g = (np.sqrt(5) - 1) / 2
        for _ in range(25):
            c, d = b - g * (b - a), a + g * (b - a)
            a, b = (a, d) if best(c) > best(d) else (c, b)
        x_f = 0.5 * (a + b)
    return fibre_overlap(run, x_f, theta_air) * run["up"], x_f


def peak(lam, ce):
    """Peak wavelength (a parabola through the top 0.5 dB, in dB), peak efficiency in dB and the 1 dB bandwidth."""
    db = 10 * np.log10(np.maximum(ce, 1e-12))
    i = np.argmax(db)
    top = db > db[i] - 0.5
    p = np.polyfit(lam[top] - lam[i], db[top], 2)
    lam_pk = lam[i] - p[1] / (2 * p[0])
    db_pk = np.polyval(p, lam_pk - lam[i])
    edges = []
    for direction in (-1, 1):                           # walk out to the -1 dB level, then interpolate
        j = i
        while 0 < j < len(lam) - 1 and db[j + direction] > db_pk - 1:
            j += direction
        k = j + direction
        edges.append(lam[j] + (db_pk - 1 - db[j]) * (lam[k] - lam[j]) / (db[k] - db[j]))
    return lam_pk, db_pk, edges[1] - edges[0]


def at(lam, values, lam0):
    """Linear interpolation of a spectrum at wavelength lam0."""
    return np.interp(lam0, lam, values)


def decay_rate(run, lam0, margin=2.0):
    """Grating strength alpha (field decay rate) from the slope of ln|Ez|^2 along the line above the grating."""
    i = np.argmin(np.abs(run["lam"] - lam0))
    x, I = run["x"], np.abs(run["Ez"][i]) ** 2
    L = run["n_per"] * run["period"]
    sel = (x > margin) & (x < L - margin)
    return -np.polyfit(x[sel], np.log(I[sel]), 1)[0] / 2


# ---------------------------------------------------------------------------------------------------------
# Part D. Directionality against BOX thickness: the thin-sheet model of the chapter's demo (gceff.html)
# ---------------------------------------------------------------------------------------------------------
def thin_sheet_directionality(t, lam=LAM0, theta_air=THETA_AIR, r=None):
    """A thin sheet emitting equally up and down above a reflector: up = |1 + r e^{j phi}|^2, lost = 1 - r^2."""
    r = (N_SI - N_OX) / (N_SI + N_OX) if r is None else r
    th = np.arcsin(np.sin(np.radians(theta_air)) / N_OX)
    phi = 2 * (2 * np.pi / lam) * N_OX * np.asarray(t) * np.cos(th) + np.pi
    up = 1 + r**2 + 2 * r * np.cos(phi)
    return up / (up + 1 - r**2)


def fit_box(ts, ds, lam=LAM0, theta_air=THETA_AIR):
    """Least-squares fit D(t) = a + b cos(q t) + c sin(q t), with the BOX period 2 pi/q of the chapter."""
    th = np.arcsin(np.sin(np.radians(theta_air)) / N_OX)
    q = 2 * np.pi / (lam / (2 * N_OX * np.cos(th)))
    A = np.column_stack([np.ones_like(ts), np.cos(q * ts), np.sin(q * ts)])
    a, b, c = np.linalg.lstsq(A, ds, rcond=None)[0]
    amp, ph = np.hypot(b, c), np.arctan2(c, b)
    t_best = ts.min() + (ph / q - ts.min()) % (2 * np.pi / q)     # the first maximum (q t = ph) in the sampled range
    return a, amp, t_best, 2 * np.pi / q


def main(plot=True, res=30):
    t_start = time.time()
    print(f"Lab 6: a grating coupler in 2D FDTD (MEEP, {res} pixels per um; lengths in um)\n")

    # ---- Part A
    n_hi, n_lo = slab_te(T_SI), slab_te(T_SI - ETCH)
    n_avg = FF * n_hi + (1 - FF) * n_lo
    s = np.sin(np.radians(THETA_AIR))
    p_est = LAM0 / (n_avg - s)
    th_ox = np.degrees(np.arcsin(s / N_OX))
    print("A. The phase-matching estimate (Worked Example 15.1)")
    print(f"   TE slab indices at 1550 nm: 220 nm {n_hi:.3f}, 150 nm {n_lo:.3f}; average {n_avg:.3f}"
          "   (Chapter 15: 2.848, 2.539, 2.694)")
    print(f"   period for 1550 nm at {THETA_AIR:g} deg in air: {1000 * p_est:.1f} nm; angle in the oxide {th_ox:.2f} deg"
          "   (Chapter 15: 607 nm, 5.5 deg)")
    print(f"   group indices without material dispersion (as in the FDTD): {slab_group_index(T_SI):.2f} and "
          f"{slab_group_index(T_SI - ETCH):.2f}   (the demo's 3.58 and 3.40)")
    n_eps = stack_te([(N_SI, T_SI - ETCH), (np.sqrt(FF * N_SI**2 + (1 - FF) * N_OX**2), ETCH)])
    print(f"   averaging the permittivity of the etched layer instead: n_eff = {n_eps:.3f}, period "
          f"{1000 * LAM0 / (n_eps - s):.1f} nm   (not in the chapter)\n")

    # ---- Part B: the grating of Worked Example 15.1
    P0 = round(p_est, 3)
    main_run = simulate(P0, res=res, field_map=True)
    lam = main_run["lam"]
    ce, x_f = coupling(main_run)
    lam_pk, db_pk, bw = peak(lam, ce)
    up, down, T, R = (at(lam, main_run[k], lam_pk) for k in ("up", "down", "T", "R"))
    alpha = decay_rate(main_run, lam_pk)
    ov = at(lam, ce, lam_pk) / up
    print(f"B. FDTD of the {1000 * P0:.0f} nm grating, {N_PER} periods, 2 um BOX ({main_run['seconds']:.0f} s)")
    print(f"   at the peak: up {100 * up:.1f} %, down {100 * down:.1f} %, through {100 * T:.1f} %, reflected {100 * R:.2f} %,"
          f" sum {100 * (up + down + T + R):.1f} %")
    print(f"   directionality {100 * up / (up + down):.1f} %   (Chapter 15 thin-sheet model: 62 % at 2 um)")
    print(f"   grating strength alpha = {alpha:.3f} /um, 1/alpha = {1 / alpha:.1f} um   "
          f"(Chapter 15: best uniform grating 1/alpha = 1.46 w0 = 7.6 um)")
    print(f"   fibre at {THETA_AIR:g} deg, {x_f:.1f} um from the start of the grating, overlap {100 * ov:.1f} %"
          "   (Chapter 15: at best about 80 %, fibre 3.8 um from the start)")
    print(f"   peak {1000 * lam_pk:.1f} nm, coupling efficiency {db_pk:.2f} dB ({100 * 10 ** (db_pk / 10):.1f} %)"
          f"   (Chapter 15: 1550 nm by phase matching; thin-sheet budget -3.0 dB)")
    print(f"   1 dB bandwidth {1000 * bw:.1f} nm   (Chapter 15: about 42 nm from the fibre's acceptance; measured 30-40 nm)")
    print(f"   back-reflection into the waveguide {10 * np.log10(R):.1f} dB at the peak, "
          f"{10 * np.log10(at(lam, main_run['R'], LAM0)):.1f} dB at 1550 nm; strongest in range "
          f"{10 * np.log10(main_run['R'].max()):.1f} dB at {1000 * lam[np.argmax(main_run['R'])]:.0f} nm"
          f" (second-order Bragg: n_eff Lambda = {1000 * n_avg * P0:.0f} nm)\n")

    # ---- Part C: period sweep and fibre angle
    sweep = {P0: (lam_pk, db_pk, bw, main_run, ce)}
    print("C. Period sweep: the peak follows phase matching")
    for P in (P0 - 0.02, P0 + 0.02):
        r = simulate(P, res=res)
        c, _ = coupling(r)
        lp, dbp, bwp = peak(r["lam"], c)
        sweep[P] = (lp, dbp, bwp, r, c)
    for P in sorted(sweep):
        lp, dbp, bwp, r, _ = sweep[P]
        print(f"   period {1000 * P:.0f} nm: peak {1000 * lp:.1f} nm, {dbp:.2f} dB, 1 dB bandwidth {1000 * bwp:.1f} nm;"
              f" phase-matching estimate {1000 * phase_matched_wavelength(P):.1f} nm   ({r['seconds']:.0f} s)")
    Ps = np.array(sorted(sweep))
    slope, icept = np.polyfit(Ps, [sweep[P][0] for P in Ps], 1)
    est_slope = (phase_matched_wavelength(P0 + 0.02) - phase_matched_wavelength(P0 - 0.02)) / 0.04
    p1550 = (LAM0 - icept) / slope
    print(f"   d(lambda)/d(Lambda) = {slope:.2f} (FDTD) against {est_slope:.2f} (phase matching, the demo's indices)")
    print(f"   period for a 1550 nm peak: {1000 * p1550:.1f} nm   (Chapter 15: 607 nm by the averaged index;"
          " 'nearer 630 nm' by a full simulation)")
    print(f"   {1000 * P0:.0f} nm peaks {1000 * (lam_pk - LAM0):+.1f} nm from 1550 nm: the grating index lambda/Lambda +"
          f" sin(theta) is {lam_pk / P0 + s:.3f}, against the averaged {n_avg:.3f}")
    print("   fibre angle, from the same simulation (fibre moved to its best position each time):")
    angles = [4, 6, 8, 10, 12]
    ang_pk = []
    for a in angles:
        lp = peak(lam, coupling(main_run, theta_air=a)[0])[0]
        ang_pk.append(lp)
        print(f"     {a:2d} deg: peak {1000 * lp:.1f} nm   (estimate {1000 * phase_matched_wavelength(P0, theta_air=a):.1f} nm)")
    dl_dth = np.polyfit(angles, ang_pk, 1)[0]
    ng = 0.5 * (DEMO_NG[0] + DEMO_NG[1])
    est = -LAM0 * np.cos(np.radians(THETA_AIR)) / (ng - s) * np.pi / 180
    print(f"   d(lambda)/d(theta) = {1000 * dl_dth:.2f} nm/deg against -lambda cos(theta)/(n_g - sin theta) = "
          f"{1000 * est:.2f} nm/deg (Section 15.4, n_g = {ng:.2f})\n")

    # ---- Part D: the BOX thickness, a quarter of the chapter's 0.54 um period apart
    print(f"D. Directionality against BOX thickness ({1000 * P0:.0f} nm grating, at 1550 nm)")
    box_runs = []
    for t in (1.73, 1.865, 2.0, 2.135):
        r = main_run if t == T_BOX else simulate(P0, t_box=t, res=res)
        c, _ = coupling(r)
        u, d = at(r["lam"], r["up"], LAM0), at(r["lam"], r["down"], LAM0)
        box_runs.append((t, u / (u + d), 10 * np.log10(at(r["lam"], c, LAM0)), u, d))
        print(f"   BOX {t:.3f} um: up {100 * u:.1f} %, down {100 * d:.1f} %, directionality {100 * u / (u + d):.1f} %"
              f" (thin sheet {100 * thin_sheet_directionality(t):.0f} %), into the fibre {box_runs[-1][2]:.2f} dB"
              f"   ({r['seconds']:.0f} s)")
    ts, Ds = np.array([b[0] for b in box_runs]), np.array([b[1] for b in box_runs])
    mean, amp, t_best, period_t = fit_box(ts, Ds)
    print(f"   fit with the chapter's {period_t:.3f} um period: directionality {100 * (mean - amp):.0f}-{100 * (mean + amp):.0f} %,"
          f" best at {t_best:.2f} and {t_best + period_t:.2f} um   (Chapter 15 thin sheet: 29-71 %, best 1.89 and 2.43 um)\n")
    print(f"Total time {time.time() - t_start:.0f} s")
    if plot:
        make_figure(main_run, ce, x_f, lam_pk, sweep, P0, slope, icept, box_runs, (mean, amp, t_best, period_t), res)


def make_figure(run, ce, x_f, lam_pk, sweep, P0, slope, icept, box_runs, fit, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(13, 8.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])
    # (a) |Ez| at 1550 nm over the cross-section, with the silicon outlined
    ax = fig.add_subplot(gs[0, :2])
    ext = run["extent"]
    ax.imshow(run["map"], origin="lower", extent=ext, cmap="magma", aspect="auto",
              vmax=np.percentile(run["map"], 99.5))
    ax.contour(np.linspace(ext[0], ext[1], run["eps"].shape[1]), np.linspace(ext[2], ext[3], run["eps"].shape[0]),
               run["eps"], levels=[(N_OX**2 + N_SI**2) / 2], colors="w", linewidths=0.5)
    ax.axhline(Y_UP, color="c", ls=":", lw=0.8)
    ax.set(xlabel="x along the waveguide (µm)", ylabel="y (µm)",
           title=f"(a) |Ez| at 1550 nm: period {1000 * P0:.0f} nm, 70 nm etch, 2 µm BOX, oxide cladding")
    ax.text(ext[0] + 0.2, Y_UP + 0.1, "fibre overlap line", color="c", fontsize=8)
    # (b) the emitted beam against the fibre mode
    ax = fig.add_subplot(gs[0, 2])
    i = np.argmin(np.abs(run["lam"] - lam_pk))
    x, I = run["x"], np.abs(run["Ez"][i]) ** 2
    th = np.arcsin(np.sin(np.radians(THETA_AIR)) / N_OX)
    g = np.exp(-2 * ((x - x_f) * np.cos(th) / W0) ** 2)
    dx = x[1] - x[0]
    ax.plot(x, I / (I.sum() * dx), color="tab:orange", lw=1.5, label="|Ez|² on the overlap line, FDTD")
    ax.plot(x, g * np.cos(th) / (W0 * np.sqrt(np.pi / 2)), color="tab:blue", ls="--", lw=1.2, label=f"fibre mode, MFD {2 * W0:.1f} µm")
    L = run["n_per"] * run["period"]
    ax.axvspan(0, L, color="grey", alpha=0.12, lw=0, label="grating")
    ax.set(xlabel="x (µm)", ylabel="power density (1/µm)", title=f"(b) the beam at {1000 * lam_pk:.0f} nm and the fibre")
    ax.legend(fontsize=8, loc="upper right")
    # (c) spectra for every period
    ax = fig.add_subplot(gs[1, 0])
    cols = plt.cm.viridis(np.linspace(0, 0.9, len(sweep)))
    for col, P in zip(cols, sorted(sweep)):
        lp, dbp, bwp, r, c = sweep[P]
        ax.plot(1000 * r["lam"], 10 * np.log10(np.maximum(c, 1e-6)), color=col, lw=2.2 if P == P0 else 1.0,
                label=f"{1000 * P:.0f} nm")
    ax.plot(1000 * run["lam"], 10 * np.log10(run["R"]), color="tab:red", lw=0.9, ls=":",
            label=f"reflection, {1000 * P0:.0f} nm")
    ax.axhline(peak(run["lam"], ce)[1] - 1, color="grey", lw=0.6, ls="--")
    ax.set(xlabel="wavelength (nm)", ylabel="into the fibre (dB)", ylim=(-30, 0),
           title="(c) coupling efficiency against period")
    ax.legend(fontsize=7, loc="lower right", ncol=2)
    # (d) peak wavelength against period: FDTD and phase matching
    ax = fig.add_subplot(gs[1, 1])
    Ps = np.array(sorted(sweep))
    pf = np.linspace(Ps.min() - 0.005, Ps.max() + 0.005, 50)
    ax.plot(1000 * pf, 1000 * np.array([phase_matched_wavelength(p) for p in pf]), color="k", lw=1,
            label="phase matching, averaged index")
    ax.plot(1000 * Ps, 1000 * np.array([sweep[P][0] for P in Ps]), "o", color="tab:orange", label="FDTD peaks")
    ax.plot(1000 * pf, 1000 * (slope * pf + icept), color="tab:orange", lw=0.8, ls="--")
    ax.axhline(1550, color="grey", lw=0.6, ls=":")
    ax.set(xlabel="grating period (nm)", ylabel="peak wavelength (nm)", title=f"(d) peak against period, {THETA_AIR:g}° fibre")
    ax.legend(fontsize=8, loc="upper left")
    # (e) directionality against BOX thickness
    ax = fig.add_subplot(gs[1, 2])
    tf = np.linspace(1.5, 2.7, 300)
    mean, amp, t_best, per = fit
    ax.plot(tf, 100 * thin_sheet_directionality(tf), color="k", lw=1, ls="--", label="thin-sheet model (demo)")
    ax.plot(tf, 100 * (mean + amp * np.cos(2 * np.pi * (tf - t_best) / per)), color="tab:green", lw=0.9,
            label="fit to FDTD")
    ax.plot([b[0] for b in box_runs], [100 * b[1] for b in box_runs], "o", color="tab:green", label="FDTD, 1550 nm")
    ax.set(xlabel="BOX thickness (µm)", ylabel="directionality (%)", ylim=(0, 100),
           title="(e) directionality against BOX thickness")
    ax.legend(fontsize=8, loc="lower right")
    fig.suptitle(f"2D FDTD (MEEP), {res} pixels per µm", fontsize=9, x=0.99, ha="right")
    fig.tight_layout()
    fig.savefig("lab06_gc_meep.png", dpi=150)
    print("Saved the figure as lab06_gc_meep.png")


if __name__ == "__main__":
    resolution = 20 if "--quick" in sys.argv else 30
    if "--resolution" in sys.argv:
        resolution = int(sys.argv[sys.argv.index("--resolution") + 1])
    main(plot="--no-plot" not in sys.argv, res=resolution)
