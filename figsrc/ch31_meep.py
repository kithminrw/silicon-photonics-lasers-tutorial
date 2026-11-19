"""Small MEEP (2D FDTD) runs for Chapter 31 (How Photonic Simulators Work). Each part writes figsrc/ch31_meep_<part>.json.

Run one part at a time in the Docker container, single-threaded:
    MSYS_NO_PATHCONV=1 docker exec -e OMP_NUM_THREADS=1 -w /repo photonics-labs /opt/conda/envs/labs/bin/python -u figsrc/ch31_meep.py conv

parts
  conv   effective index of the 220 nm silicon slab (TE0 and TM0, 1550 nm) on grids of 10-120 pixels per um, with and
         without subpixel smoothing, against the exact slab solution (Figure 31.8)
  pml    reflection of the slab's TE0 mode from the end of the cell: PML, a graded scalar absorber, and an abrupt lossy
         block, against their thickness (Figure 31.6)
  bragg  a sidewall Bragg grating (2D, effective-index top view): one pulsed run against continuous-wave runs at single
         wavelengths (Figure 31.7)
  bend   90-degree bends (2D, effective-index top view): the field at 1550 nm from a pulsed run, and the loss of a
         1 um bend against resolution, with and without subpixel smoothing (Figure 31.9)
  cost   cell updates per second and bytes per cell of a small 3D run (Worked Example 31.3)

Units: lengths in um, frequencies in 1/um (MEEP units with a = 1 um, so f = 1/lambda). Constant indices at 1550 nm:
silicon 3.4764, silica 1.4440 (the Sellmeier values of Labs 1-3); the 220 nm film's TE0 index 2.8482 is the core index
of the 2D top views (effective-index method, Chapter 6), with oxide around it.
"""
import json, os, sys, time, resource
import numpy as np
import meep as mp

HERE = os.path.dirname(os.path.abspath(__file__))
N_SI, N_OX, N_I = 3.4764, 1.4440, 2.8482
T_SI, LAM0 = 0.22, 1.55
F0 = 1 / LAM0
mp.verbosity(0)
T0 = time.time()
QUICK = os.environ.get("QUICK") == "1"


def log(*a):
    print(f"[{time.time() - T0:7.1f} s]", *a, flush=True)


def dump(part, out):
    p = os.path.join(HERE, f"ch31_meep_{part}{'_quick' if QUICK else ''}.json")
    json.dump(out, open(p, "w"), indent=1)
    log("wrote", p)


# ------------------------------------------------------------------ exact slab modes
def slab_neff(lam, d, n1, n2, tm=False):
    """Fundamental (even) mode of a symmetric slab, by bisection on kappa tan(kappa d/2) = r gamma."""
    k = 2 * np.pi / lam
    r = (n1 / n2) ** 2 if tm else 1.0

    def g(n):
        ka, ga = k * np.sqrt(n1 ** 2 - n ** 2), k * np.sqrt(n ** 2 - n2 ** 2)
        return ka * np.tan(ka * d / 2) - r * ga

    # the fundamental mode lies where kappa d/2 < pi/2
    lo = max(n2, np.sqrt(max(n1 ** 2 - (np.pi / (k * d)) ** 2, n2 ** 2))) + 1e-12
    hi = n1 - 1e-12
    for _ in range(200):
        mid = (lo + hi) / 2
        if g(mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2


# ------------------------------------------------------------------ part: conv
def part_conv():
    out = {"lam": LAM0, "t": T_SI, "n_si": N_SI, "n_ox": N_OX, "runs": []}
    res_list = [10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120] if not QUICK else [10, 20]
    for pol in ["TE", "TM"]:
        tm = pol == "TM"
        n_ex = slab_neff(LAM0, T_SI, N_SI, N_OX, tm)
        kx = n_ex / LAM0                       # Bloch wavenumber that the exact mode has at 1550 nm
        f_ex = F0                              # so the exact mode has frequency 1/1.55 um at that wavenumber
        out[pol] = {"n_exact": n_ex, "kx": kx, "f_exact": f_ex}
        log(pol, "exact n_eff", n_ex, "f", f_ex, "(1/f =", 1 / f_ex, ")")
        comp = mp.Hz if tm else mp.Ez
        for avg in [True, False]:
            for res in res_list:
                dpml, sy, sx = 1.0, 5.0, 0.5
                sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=res, k_point=mp.Vector3(kx),
                                    geometry=[mp.Block(mp.Vector3(mp.inf, T_SI, mp.inf), center=mp.Vector3(0, 0.013),
                                                       material=mp.Medium(index=N_SI))],
                                    default_material=mp.Medium(index=N_OX), eps_averaging=avg,
                                    boundary_layers=[mp.PML(dpml, direction=mp.Y)],
                                    sources=[mp.Source(mp.GaussianSource(f_ex, fwidth=0.2 * f_ex), component=comp,
                                                       center=mp.Vector3(0.05, 0.03))])
                h = mp.Harminv(comp, mp.Vector3(-0.07, 0.0), f_ex, 0.2 * f_ex)
                t1 = time.time()
                sim.run(mp.after_sources(h), until_after_sources=100)
                modes = sorted(h.modes, key=lambda m: -abs(m.amp))
                if not modes:
                    log(pol, avg, res, "no mode"); continue
                f = modes[0].freq
                n = kx / f
                out["runs"].append({"pol": pol, "avg": avg, "res": res, "f": f, "n_eff": n,
                                    "dn": n - kx / f_ex, "cpu_s": time.time() - t1})
                log(f"{pol} avg={avg} res={res}: n_eff {n:.6f}  error {n - kx / f_ex:+.2e}  ({time.time() - t1:.1f} s)")
    dump("conv", out)


# ------------------------------------------------------------------ part: pml
def slab_geometry():
    return [mp.Block(mp.Vector3(mp.inf, T_SI, mp.inf), center=mp.Vector3(), material=mp.Medium(index=N_SI))]


def part_pml():
    """TE0 of the 220 nm slab (Ez) runs into the right-hand end of the cell. The left end and the top and bottom have
    thick PML; the right end, the last d um of a fixed cell, is the boundary under test. A mode monitor between the
    source and that end measures the backward mode. The grid is the same in every run, so the small backward signal that
    the mode decomposition reports even for a perfect absorber (the discretised mode is not exactly the solver's mode) is
    the same in every run too: it is measured once, with 6 um of PML, and subtracted coherently."""
    res = 25
    df = 0.25 * F0
    out = {"res": res, "lam": LAM0, "band_um": [1 / (F0 + df / 2), 1 / (F0 - df / 2)], "kinds": {}}
    nfreq = 41
    px = [2, 3, 5, 8, 12, 19, 25, 38, 50, 75, 100, 150] if not QUICK else [5, 25]
    x_src, x_mon, x_left, x_right = -2.5, -1.0, -5.0, 7.0    # 2 um of PML on the left; the boundary ends at x = 7 um
    sx, cx, sy = x_right - x_left, (x_right + x_left) / 2, 4.0

    def run(kind, d):
        layers = [mp.PML(1.0, direction=mp.Y), mp.PML(2.0, direction=mp.X, side=mp.Low)]
        geom = slab_geometry()
        if kind == "pml":
            layers.append(mp.PML(d, direction=mp.X, side=mp.High))
        elif kind == "absorber":
            layers.append(mp.Absorber(d, direction=mp.X, side=mp.High))
        else:
            # an abrupt lossy region: both materials get the same conductivity, sigma_D = 0.2 x 2 pi f, so that
            # eps -> eps (1 + 0.2 i) and each index gains an imaginary part of about 0.1 n; the cell's metal wall
            # is behind it
            sig = 0.2 * 2 * np.pi * F0
            geom += [mp.Block(mp.Vector3(d, mp.inf, mp.inf), center=mp.Vector3(x_right - d / 2, 0),
                              material=mp.Medium(index=N_OX, D_conductivity=sig)),
                     mp.Block(mp.Vector3(d, T_SI, mp.inf), center=mp.Vector3(x_right - d / 2, 0),
                              material=mp.Medium(index=N_SI, D_conductivity=sig))]
        sim = mp.Simulation(cell_size=mp.Vector3(sx, sy + 2), resolution=res, geometry_center=mp.Vector3(cx, 0),
                            geometry=geom, default_material=mp.Medium(index=N_OX), boundary_layers=layers,
                            sources=[mp.EigenModeSource(mp.GaussianSource(F0, fwidth=df), center=mp.Vector3(x_src, 0),
                                                        size=mp.Vector3(0, sy), direction=mp.X, eig_band=1,
                                                        eig_parity=mp.ODD_Z)])
        mon = sim.add_mode_monitor(F0, df, nfreq, mp.ModeRegion(center=mp.Vector3(x_mon, 0), size=mp.Vector3(0, sy)))
        sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(x_mon, 0), 1e-10))
        c = sim.get_eigenmode_coefficients(mon, [1], eig_parity=mp.ODD_Z).alpha[0]
        return c[:, 0], c[:, 1], np.array(mp.get_flux_freqs(mon))

    a_ref, b_ref, freqs = run("pml", 6.0)
    i0 = int(np.argmin(np.abs(freqs - F0)))
    out["lam"] = (1 / freqs).tolist()
    out["floor_raw"] = (np.abs(b_ref) ** 2 / np.abs(a_ref) ** 2).tolist()
    log(f"reference (6 um PML): raw backward/forward at 1550 nm {out['floor_raw'][i0]:.2e}")
    for kind in ["pml", "absorber", "block"]:
        out["kinds"][kind] = []
        for n in px:
            d = n / res
            t1 = time.time()
            a, b, _ = run(kind, d)
            R = np.abs(b - b_ref) ** 2 / np.abs(a_ref) ** 2
            out["kinds"][kind].append({"d": d, "R1550": float(R[i0]), "Rmax": float(R.max()), "R": R.tolist(),
                                       "fwd_change": float(np.max(np.abs(a / a_ref - 1))), "cpu_s": time.time() - t1})
            log(f"{kind:8s} d={d:4.2f}: R(1550) {R[i0]:.2e}, max {R.max():.2e}  ({time.time() - t1:.1f} s)")
    dump("pml", out)


# ------------------------------------------------------------------ 2D top views (effective-index method)
CORE, CLAD = mp.Medium(index=N_I), mp.Medium(index=N_OX)


def part_bragg():
    """A sidewall grating in the 2D effective-index top view: a 0.5 um guide whose width alternates between 0.45 and
    0.55 um (25 nm into and out of each side) every half period, 60 periods. TE-like light: in-plane E, so Hz (EVEN_Z)."""
    res = int(os.environ.get("BRAGG_RES", "30"))           # the figure uses 30 pixels per um
    period, n_per, w0, dw = 0.310, 60, 0.50, 0.05          # period chosen to put the stop band near 1550 nm in this 2D model
    L = period * n_per
    pad, dpml, sy = 3.0, 1.0, 4.0
    sx = L + 2 * pad + 2 * dpml
    x_src, x_in, x_out = -L / 2 - pad + 0.5, -L / 2 - pad + 1.2, L / 2 + pad - 1.0
    fmin, fmax = 1 / 1.62, 1 / 1.48
    fc, df = (fmin + fmax) / 2, fmax - fmin
    nfreq = 281

    def geometry(grating):
        g = [mp.Block(mp.Vector3(mp.inf, w0, mp.inf), center=mp.Vector3(), material=CORE)]
        if grating:
            for i in range(n_per):
                x0 = -L / 2 + i * period
                # wide half: +25 nm on each side; narrow half: -25 nm on each side (cladding cut into the guide)
                g += [mp.Block(mp.Vector3(period / 2, dw / 2, mp.inf), center=mp.Vector3(x0 + period / 4, s * (w0 + dw / 2) / 2), material=CORE)
                      for s in (1, -1)]
                g += [mp.Block(mp.Vector3(period / 2, dw / 2, mp.inf), center=mp.Vector3(x0 + 3 * period / 4, s * (w0 - dw / 2) / 2), material=CLAD)
                      for s in (1, -1)]
        return g

    def sim_for(grating, src):
        return mp.Simulation(cell_size=mp.Vector3(sx, sy + 2 * dpml), resolution=res, geometry=geometry(grating),
                             default_material=CLAD, boundary_layers=[mp.PML(dpml)], sources=[src],
                             )

    def eig_src(time_profile):
        return mp.EigenModeSource(time_profile, center=mp.Vector3(x_src, 0), size=mp.Vector3(0, sy), direction=mp.X,
                                  eig_band=1, eig_parity=mp.EVEN_Z)

    out = {"res": res, "period": period, "n_per": n_per, "w0": w0, "dw": dw, "n_core": N_I, "n_clad": N_OX}
    if os.environ.get("BRAGG_CWONLY") == "1":          # keep the pulsed results already on disk, redo only the CW runs
        old = json.load(open(os.path.join(HERE, "ch31_meep_bragg.json")))
        out.update({k: v for k, v in old.items() if k != "cw"})
    # (1) one pulsed run with the grating, and a normalisation run without
    spectra = {}
    for grating in ([] if os.environ.get("BRAGG_CWONLY") == "1" else [False, True]):
        sim = sim_for(grating, eig_src(mp.GaussianSource(fc, fwidth=df)))
        m_in = sim.add_mode_monitor(fc, df, nfreq, mp.ModeRegion(center=mp.Vector3(x_in, 0), size=mp.Vector3(0, sy)))
        m_out = sim.add_mode_monitor(fc, df, nfreq, mp.ModeRegion(center=mp.Vector3(x_out, 0), size=mp.Vector3(0, sy)))
        t1 = time.time()
        sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Hz, mp.Vector3(x_out, 0), 1e-7))
        steps = sim.timestep()
        a_in = sim.get_eigenmode_coefficients(m_in, [1], eig_parity=mp.EVEN_Z).alpha[0]
        a_out = sim.get_eigenmode_coefficients(m_out, [1], eig_parity=mp.EVEN_Z).alpha[0]
        freqs = np.array(mp.get_flux_freqs(m_in))
        spectra[grating] = (a_in, a_out)
        out["pulse_steps_" + ("grating" if grating else "straight")] = steps
        out["pulse_time_" + ("grating" if grating else "straight")] = sim.meep_time()
        log(f"pulsed run, grating={grating}: {steps} steps, {sim.meep_time():.0f} time units, {time.time() - t1:.0f} s")
    if spectra:
        inc = np.abs(spectra[False][0][:, 0]) ** 2
        out["lam"] = (1 / freqs).tolist()
        out["T"] = (np.abs(spectra[True][1][:, 0]) ** 2 / inc).tolist()
        out["R"] = (np.abs(spectra[True][0][:, 1]) ** 2 / inc).tolist()
        out["fc"], out["df"] = fc, df
    # (2) continuous-wave runs at single wavelengths: the steady-state power through the output plane, averaged over
    # one period, against the same with no grating, after 400, 800, 1200 and 1600 um/c (the last is the value plotted)
    out["cw"] = []
    for lam in ([1.500, 1.530, 1.550, 1.575, 1.610] if res == 30 else []):
        f = 1 / lam
        pw = {}
        for grating in [False, True]:
            sim = sim_for(grating, eig_src(mp.ContinuousSource(f, width=20)))
            t1 = time.time()
            pw[grating] = []
            for tend in (400, 800, 1200, 1600):
                sim.run(until=tend - sim.meep_time())
                vals = []
                for k in range(20):
                    sim.run(until=1 / f / 20)
                    vals.append(sim.flux_in_box(mp.X, center=mp.Vector3(x_out, 0), size=mp.Vector3(0, sy)))
                pw[grating].append(float(np.mean(vals)))
            log(f"CW {lam:.3f} um grating={grating}: flux {pw[grating]} ({time.time() - t1:.0f} s)")
        Ts = [g / s0 for g, s0 in zip(pw[True], pw[False])]
        out["cw"].append({"lam": lam, "T": Ts[-1], "T_at": Ts, "t_at": [400, 800, 1200, 1600]})
        log(f"   T = {Ts}")
    dump("bragg" if res == 30 else f"bragg{res}", out)


def bend_run(R, res, avg=True, fields=False):
    dpml, lead = 1.0, 2.0
    x0, x1 = -lead - 0.5, R + 1.5                       # cell in x
    y0, y1 = -1.5, R + lead + 0.5                       # cell in y
    sx, sy = x1 - x0 + 2 * dpml, y1 - y0 + 2 * dpml
    cen = mp.Vector3((x0 + x1) / 2, (y0 + y1) / 2)
    fmin, fmax = 1 / 1.62, 1 / 1.48
    fc, df = (fmin + fmax) / 2, fmax - fmin
    w = 0.5
    geom = [mp.Block(mp.Vector3(lead + 0.5 + dpml + 0.1, w, mp.inf), center=mp.Vector3(x0 - dpml + (lead + 0.5 + dpml + 0.1) / 2, 0), material=CORE),
            mp.Cylinder(radius=R + w / 2, height=mp.inf, center=mp.Vector3(0, R), material=CORE),
            mp.Cylinder(radius=R - w / 2, height=mp.inf, center=mp.Vector3(0, R), material=CLAD),
            mp.Block(mp.Vector3(R + w + 0.1, 2 * R + w + 0.2, mp.inf), center=mp.Vector3(-(R + w + 0.1) / 2, R), material=CLAD),
            mp.Block(mp.Vector3(2 * R + w + 0.2, R + w + 0.1, mp.inf), center=mp.Vector3(0, R + (R + w + 0.1) / 2), material=CLAD),
            mp.Block(mp.Vector3(w, y1 + dpml - R + 0.2, mp.inf), center=mp.Vector3(R, R - 0.1 + (y1 + dpml - R + 0.2) / 2), material=CORE)]
    # (the input guide is redrawn last so the clipping blocks of the quarter circle do not cut it)
    geom.append(mp.Block(mp.Vector3(lead + 0.5 + dpml + 0.1, w, mp.inf), center=mp.Vector3(x0 - dpml + (lead + 0.5 + dpml + 0.1) / 2, 0), material=CORE))
    src = mp.EigenModeSource(mp.GaussianSource(fc, fwidth=df), center=mp.Vector3(x0 + 0.4, 0), size=mp.Vector3(0, 3.0),
                             direction=mp.X, eig_band=1, eig_parity=mp.EVEN_Z)
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), geometry_center=cen, resolution=res, geometry=geom,
                        default_material=CLAD, boundary_layers=[mp.PML(dpml)], sources=[src], eps_averaging=avg)
    nf = 21
    m_in = sim.add_mode_monitor(fc, df, nf, mp.ModeRegion(center=mp.Vector3(x0 + 1.0, 0), size=mp.Vector3(0, 3.0)))
    m_out = sim.add_mode_monitor(fc, df, nf, mp.ModeRegion(center=mp.Vector3(R, y1 - 0.4), size=mp.Vector3(3.0, 0)))
    dft = None
    if fields:
        dft = sim.add_dft_fields([mp.Hz], [F0], center=cen, size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
    t1 = time.time()
    sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Hz, mp.Vector3(R, y1 - 0.4), 1e-7))
    a_in = sim.get_eigenmode_coefficients(m_in, [1], eig_parity=mp.EVEN_Z).alpha[0]
    a_out = sim.get_eigenmode_coefficients(m_out, [1], eig_parity=mp.EVEN_Z).alpha[0]
    freqs = np.array(mp.get_flux_freqs(m_in))
    T = np.abs(a_out[:, 0]) ** 2 / np.abs(a_in[:, 0]) ** 2
    i0 = int(np.argmin(np.abs(freqs - F0)))
    r = {"R": R, "res": res, "avg": avg, "lam": (1 / freqs).tolist(), "T": T.tolist(), "T1550": float(T[i0]),
         "cpu_s": time.time() - t1}
    if fields:
        hz = sim.get_dft_array(dft, mp.Hz, 0)
        eps = sim.get_array(center=cen, size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml), component=mp.Dielectric)
        st = max(1, res // 20)
        r["field_re"] = np.round(np.real(hz)[::st, ::st] / np.abs(hz).max(), 4).tolist()
        r["eps"] = np.round(eps[::st, ::st], 3).tolist()
        r["extent"] = [x0, x1, y0, y1]
    return r


def part_bend():
    out = {"fields": [], "conv": []}
    for R in [1.0, 2.0]:
        r = bend_run(R, 40, fields=True)
        out["fields"].append(r)
        log(f"bend R={R}: T(1550) {r['T1550']:.4f} = {-10 * np.log10(r['T1550']):.3f} dB ({r['cpu_s']:.0f} s)")
    for avg in [True, False]:
        for res in ([10, 15, 20, 25, 30, 40, 50, 60, 80] if not QUICK else [10, 20]):
            r = bend_run(1.0, res, avg=avg)
            out["conv"].append({k: r[k] for k in ("R", "res", "avg", "T1550", "cpu_s")})
            log(f"conv avg={avg} res={res}: T {r['T1550']:.5f} = {-10 * np.log10(r['T1550']):.4f} dB ({r['cpu_s']:.0f} s)")
    dump("bend", out)


# ------------------------------------------------------------------ part: cost
def rss_mb():
    with open("/proc/self/status") as fh:
        for line in fh:
            if line.startswith("VmRSS"):
                return float(line.split()[1]) / 1024


def cost_one(sx, sy, sz, res):
    """One 3D run in a fresh process: resident memory before the simulation is built and after it has run, and the
    wall time per step."""
    m0 = rss_mb()
    geom = [mp.Block(mp.Vector3(mp.inf, 0.5, T_SI), center=mp.Vector3(), material=mp.Medium(index=N_SI))]
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy, sz), resolution=res, geometry=geom,
                        default_material=mp.Medium(index=N_OX), boundary_layers=[mp.PML(0.5)],
                        sources=[mp.Source(mp.GaussianSource(F0, fwidth=0.2 * F0), component=mp.Ey,
                                           center=mp.Vector3(-sx / 4, 0, 0))])
    sim.run(until=2.0)                               # build, and allocate all fields
    m1 = rss_mb()
    n0 = sim.timestep(); t1 = time.time()
    sim.run(until=sim.meep_time() + 6.0)
    dt = time.time() - t1; nsteps = sim.timestep() - n0
    cells = round(sx * res) * round(sy * res) * round(sz * res)
    print("RESULT", json.dumps({"size": [sx, sy, sz], "res": res, "cells": cells, "mem_mb": m1 - m0, "steps": nsteps,
                                "s_per_step": dt / nsteps, "updates_per_s": cells * nsteps / dt}), flush=True)


def part_cost():
    """A 3D silicon strip in oxide with PML on all sides, at three cell counts, each in its own process: bytes per cell
    from the slope of memory against cells, cell updates per second from the time per step."""
    import subprocess
    out = {"runs": []}
    for cfg in [(3.0, 2.5, 2.5, 20), (4.0, 3.0, 3.0, 20), (4.0, 3.0, 3.0, 30)]:
        r = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "cost1"] + [str(v) for v in cfg],
                           capture_output=True, text=True)
        line = [l for l in r.stdout.splitlines() if l.startswith("RESULT")][0]
        out["runs"].append(json.loads(line[7:]))
        log(out["runs"][-1])
    c = np.array([r["cells"] for r in out["runs"]]); m = np.array([r["mem_mb"] for r in out["runs"]])
    slope, icpt = np.polyfit(c, m * 2 ** 20, 1)
    out["bytes_per_cell"], out["overhead_mb"] = float(slope), float(icpt / 2 ** 20)
    log(f"bytes per cell {slope:.1f}, fixed overhead {icpt / 2 ** 20:.1f} MB")
    dump("cost", out)


if __name__ == "__main__":
    if sys.argv[1] == "cost1":
        cost_one(*[float(v) for v in sys.argv[2:5]], int(sys.argv[5]))
    else:
        {"conv": part_conv, "pml": part_pml, "bragg": part_bragg, "bend": part_bend, "cost": part_cost}[sys.argv[1]]()
