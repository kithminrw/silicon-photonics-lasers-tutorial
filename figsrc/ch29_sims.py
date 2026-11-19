"""Simulations behind Chapter 29. Supermodes of the demultiplexer ring's coupler (femwell): mesh and window
convergence, sensitivities to width, gap, thickness and wavelength, the bias-tolerant width, and a small grid for the
Monte Carlo model; single strips for the width/thickness separation of Section 29.8; and the cost of each solver
(femwell solve times, MEEP's FDTD speed and memory per cell). Two 220 nm silicon strips of width W, gap g, in oxide,
TE, meshed as in Chapter 9 (figsrc/ch09_supermodes.py). Writes figsrc/ch29_sims.json, read by figsrc/ch29_figs.py.

    MSYS_NO_PATHCONV=1 docker exec -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -w /repo \\
        photonics-labs /opt/conda/envs/labs/bin/python figsrc/ch29_sims.py [part ...]

parts: convergence domain sens tolerant grid strip (physics, 8 solves in parallel); time25 eme bench (timings: run
them alone on a quiet machine; the chapter's numbers come from such a run, femwell 0.1.12, MEEP 1.35.1).
"""
import json, os, sys, time
from collections import OrderedDict
import numpy as np
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from femwell_modes import n_si, n_sio2

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ch29_sims.json")


def pair(w=0.5, gap=0.2, t=0.22, lam=1.55, res=0.025, resmax=0.25):
    """Even and odd TE supermodes of two strips; returns (n_even, n_odd, number of mesh nodes, seconds)."""
    t0 = time.process_time()
    a = box(-gap / 2 - w, 0, -gap / 2, t); b = box(gap / 2, 0, gap / 2 + w, t)
    polys = OrderedDict(left=a, right=b, clad=box(-3.5, -2.0, 3.5, 2.0))
    resolutions = dict(left={"resolution": res, "distance": 0.6}, right={"resolution": res, "distance": 0.6})
    mesh = from_meshio(mesh_from_OrderedDict(polys, resolutions, default_resolution_max=resmax))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(lam) ** 2
    for k in ("left", "right"):
        eps[basis0.get_dofs(elements=k)] = n_si(lam) ** 2
    ms = compute_modes(basis0, eps, wavelength=lam, num_modes=4, order=2)
    te = sorted([float(np.real(m.n_eff)) for m in ms if m.te_fraction > 0.5], reverse=True)
    return te[0], te[1], int(mesh.p.shape[1]), time.process_time() - t0


def lx(ne, no, lam=1.55):
    return lam / (2 * (ne - no))


def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


def store(key, val):
    d = load(); d[key] = val
    json.dump(d, open(OUT, "w"), indent=1)


def _run(args):
    kw = args
    ne, no, nodes, sec = pair(**kw)
    return dict(kw, n_even=ne, n_odd=no, Lx=lx(ne, no, kw.get("lam", 1.55)), nodes=nodes, sec=sec)


def runall(jobs, procs=8):
    from multiprocessing import Pool
    with Pool(procs) as pool:
        return pool.map(_run, jobs)


H = 0.005          # finite-difference step, 5 nm


def part_convergence():
    """Mesh convergence of L_x and of its sensitivity to a width bias (W + d, gap - d) at W 500, gap 200, t 220 nm."""
    ress = [0.08, 0.06, 0.045, 0.035, 0.025, 0.018, 0.013, 0.010]
    jobs = []
    for r in ress:
        for d in (-H, 0.0, H):
            jobs.append(dict(w=0.5 + d, gap=0.2 - d, res=r))
    out = runall(jobs)
    rows = []
    for i, r in enumerate(ress):
        m, z, p = out[3 * i: 3 * i + 3]
        dl = (np.log(p["Lx"]) - np.log(m["Lx"])) / (2 * H * 1000)        # per nm of bias
        rows.append(dict(res=r, Lx=z["Lx"], dn=z["n_even"] - z["n_odd"], n_even=z["n_even"], nodes=z["nodes"], sec=z["sec"],
                         dlnLx_dbias=dl))
        print(f"res {r*1000:5.1f} nm: nodes {z['nodes']:6d}  {z['sec']:6.1f} s  n_even {z['n_even']:.5f}  dn {z['n_even']-z['n_odd']:.6f}"
              f"  L_x {z['Lx']:.3f} um  dlnLx/dbias {dl*100:+.4f} %/nm", flush=True)
    store("convergence", rows)


def part_domain():
    """Effect of the computational window (cladding box half-width x half-height) at res 25 nm."""
    rows = []
    for hw, hh in ((1.5, 1.0), (2.5, 1.5), (3.5, 2.0), (5.0, 3.0)):
        global pair
        ne, no, nodes, sec = pair_box(hw, hh)
        rows.append(dict(hw=hw, hh=hh, Lx=lx(ne, no), n_even=ne, nodes=nodes, sec=sec))
        print(f"window {2*hw:.0f} x {2*hh:.0f} um: L_x {lx(ne, no):.3f} um, n_even {ne:.5f}, {nodes} nodes, {sec:.1f} s", flush=True)
    store("domain", rows)


def pair_box(hw, hh, w=0.5, gap=0.2, t=0.22, lam=1.55, res=0.025):
    t0 = time.process_time()
    a = box(-gap / 2 - w, 0, -gap / 2, t); b = box(gap / 2, 0, gap / 2 + w, t)
    polys = OrderedDict(left=a, right=b, clad=box(-hw, -hh, hw, hh))
    resolutions = dict(left={"resolution": res, "distance": 0.6}, right={"resolution": res, "distance": 0.6})
    mesh = from_meshio(mesh_from_OrderedDict(polys, resolutions, default_resolution_max=0.25))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(lam) ** 2
    for k in ("left", "right"):
        eps[basis0.get_dofs(elements=k)] = n_si(lam) ** 2
    ms = compute_modes(basis0, eps, wavelength=lam, num_modes=4, order=2)
    te = sorted([float(np.real(m.n_eff)) for m in ms if m.te_fraction > 0.5], reverse=True)
    return te[0], te[1], int(mesh.p.shape[1]), time.process_time() - t0


RES = 0.025        # mesh size at the cores for the production runs (as Chapter 9); see part_convergence


def part_sens():
    """Central-difference sensitivities of ln L_x at W 500, gap 200, t 220 nm, 1550 nm."""
    base = dict(w=0.5, gap=0.2, t=0.22, lam=1.55, res=RES)
    steps = dict(w=H, gap=H, t=H, lam=0.01)
    jobs = [base]
    for k, h in steps.items():
        jobs += [dict(base, **{k: base[k] - h}), dict(base, **{k: base[k] + h})]
    jobs += [dict(base, w=0.5 - H, gap=0.2 + H), dict(base, w=0.5 + H, gap=0.2 - H)]      # width bias, centres fixed
    out = runall(jobs)
    res = dict(Lx0=out[0]["Lx"], n_even=out[0]["n_even"], n_odd=out[0]["n_odd"])
    names = list(steps) + ["bias"]
    hs = list(steps.values()) + [H]
    for i, (k, h) in enumerate(zip(names, hs)):
        m, p_ = out[1 + 2 * i], out[2 + 2 * i]
        d = (np.log(p_["Lx"]) - np.log(m["Lx"])) / (2 * h * 1000)          # per nm
        res["dlnLx_d" + k] = d
        print(f"sens {k}: L_x {m['Lx']:.3f} / {p_['Lx']:.3f} um -> dlnLx/d{k} {d*100:+.3f} %/nm", flush=True)
    print(f"sens base L_x {res['Lx0']:.3f} um", flush=True)
    store("sens", res)


def part_tolerant():
    """ln L_x sensitivities to width alone, gap alone and a width bias (centres fixed) against the strip width."""
    ws = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
    jobs = []
    for w in ws:
        b = dict(w=w, gap=0.2, res=RES)
        jobs += [b, dict(b, w=w - H), dict(b, w=w + H), dict(b, gap=0.2 - H), dict(b, gap=0.2 + H),
                 dict(b, w=w - H, gap=0.2 + H), dict(b, w=w + H, gap=0.2 - H)]
    out = runall(jobs)
    rows = []
    for i, w in enumerate(ws):
        o = out[7 * i: 7 * i + 7]
        f = lambda a, b: (np.log(o[b]["Lx"]) - np.log(o[a]["Lx"])) / (2 * H * 1000)
        r = dict(w=w, Lx=o[0]["Lx"], dW=f(1, 2), dgap=f(3, 4), dbias=f(5, 6))
        rows.append(r)
        print(f"tolerant W {w*1000:.0f} nm: L_x {r['Lx']:.2f} um; dlnLx/dW {r['dW']*100:+.3f}, /dgap {r['dgap']*100:+.3f}, "
              f"/dbias {r['dbias']*100:+.3f} %/nm", flush=True)
    store("tolerant", rows)


def part_grid():
    """L_x on a grid of width bias and thickness error (for the Monte Carlo model), and at the four channels."""
    ds = [-0.008, -0.004, 0.0, 0.004, 0.008]
    ts = [-0.004, 0.0, 0.004]
    jobs = [dict(w=0.5 + d, gap=0.2 - d, t=0.22 + dt, res=RES) for d in ds for dt in ts]
    lams = [1.54612, 1.54932, 1.55252, 1.55575]
    jobs += [dict(res=RES, lam=l) for l in lams]
    out = runall(jobs)
    g = [dict(bias=round(d * 1000, 1), dt=round(dt * 1000, 1), Lx=o["Lx"]) for (d, dt), o in zip([(d, dt) for d in ds for dt in ts], out)]
    for r in g:
        print(f"grid bias {r['bias']:+.0f} nm, dt {r['dt']:+.0f} nm: L_x {r['Lx']:.3f} um", flush=True)
    ch = [dict(lam=l, Lx=o["Lx"]) for l, o in zip(lams, out[len(g):])]
    for r in ch:
        print(f"channel {r['lam']*1000:.2f} nm: L_x {r['Lx']:.3f} um", flush=True)
    store("grid", g); store("channels", ch)


def _strip(args):
    """TE0 effective index of one strip in oxide, meshed like pair()."""
    w, lam, t = args
    polys = OrderedDict(core=box(-w / 2, 0, w / 2, t), clad=box(-3.5, -2.0, 3.5, 2.0))
    mesh = from_meshio(mesh_from_OrderedDict(polys, dict(core={"resolution": RES, "distance": 0.6}), default_resolution_max=0.25))
    basis0 = Basis(mesh, ElementTriP0())
    eps = basis0.zeros() + n_sio2(lam) ** 2
    eps[basis0.get_dofs(elements="core")] = n_si(lam) ** 2
    ms = compute_modes(basis0, eps, wavelength=lam, num_modes=3, order=2)
    return max(float(np.real(m.n_eff)) for m in ms if m.te_fraction > 0.5)


def part_strip():
    """Single strips of 500 nm and 1 um: n_eff, n_g and the sensitivities to width and thickness (for Section 29.8)."""
    from multiprocessing import Pool
    rows = []
    jobs = []
    for w in (0.5, 1.0):
        jobs += [(w, 1.55, 0.22), (w - H, 1.55, 0.22), (w + H, 1.55, 0.22), (w, 1.55, 0.22 - H), (w, 1.55, 0.22 + H),
                 (w, 1.54, 0.22), (w, 1.56, 0.22)]
    with Pool(8) as pool:
        out = pool.map(_strip, jobs)
    for i, w in enumerate((0.5, 1.0)):
        n0, wm, wp, tm, tp, lm, lp = out[7 * i: 7 * i + 7]
        ng = n0 - 1.55 * (lp - lm) / 0.02
        r = dict(w=w, neff=n0, ng=ng, dn_dW=(wp - wm) / (2 * H * 1000), dn_dt=(tp - tm) / (2 * H * 1000))
        r["shift_W"] = 1550 * r["dn_dW"] / ng; r["shift_t"] = 1550 * r["dn_dt"] / ng
        rows.append(r)
        print(f"strip W {w*1000:.0f} nm: n_eff {n0:.4f}, n_g {ng:.3f}, dn/dW {r['dn_dW']:.3e}/nm, dn/dt {r['dn_dt']:.3e}/nm; "
              f"ring shift {r['shift_W']:.3f} nm/nm (W), {r['shift_t']:.3f} nm/nm (t)", flush=True)
    store("strip", rows)


def part_bench():
    """Speed and memory of MEEP's FDTD on one CPU core, for the cost estimates of Section 29.3: a silicon strip in
    oxide with a dipole source, 3D (4 x 3 x 2 um) and 2D (20 x 10 um), 25 nm cells (resolution 40 per um). Times are
    CPU times of the process (the workstation was shared), memory the rise of the peak resident size (3D only)."""
    import resource
    import meep as mp
    mp.verbosity(0)
    rows = []
    for dims in (3, 2):
        res = 40
        sz = (4.0, 3.0, 2.0) if dims == 3 else (20.0, 10.0, 0.0)
        cells = int(round(sz[0] * res)) * int(round(sz[1] * res)) * (int(round(sz[2] * res)) if dims == 3 else 1)
        geom = [mp.Block(mp.Vector3(mp.inf, 0.5, 0.22 if dims == 3 else mp.inf), material=mp.Medium(index=3.476))]
        rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        sim = mp.Simulation(cell_size=mp.Vector3(*sz), resolution=res, geometry=geom, default_material=mp.Medium(index=1.444),
                            boundary_layers=[mp.PML(0.5)], eps_averaging=True,
                            sources=[mp.Source(mp.GaussianSource(1 / 1.55, fwidth=0.1), mp.Ey, mp.Vector3(-sz[0] / 2 + 0.8, 0, 0))])
        sim.init_sim()
        sim.run(until=0.5)                                 # warm-up
        n0 = sim.timestep(); t0 = time.process_time()
        sim.run(until=10.0 if dims == 3 else 20.0)
        sec = time.process_time() - t0; steps = sim.timestep() - n0
        rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rate = cells * steps / sec
        r = dict(dims=dims, cells=cells, steps=steps, sec=sec, rate=rate, bytes_per_cell=(rss1 - rss0) * 1024 / cells,
                 courant=sim.Courant)
        rows.append(r)
        print(f"bench {dims}D: {cells} cells, {steps} steps in {sec:.1f} s -> {rate:.3g} cell-steps/s on one core; "
              f"memory {r['bytes_per_cell']:.0f} bytes/cell; Courant {sim.Courant}", flush=True)
        sim.reset_meep()
    store("bench", rows)


def part_eme():
    """CPU time of one femwell solve with many modes (as an EME section needs), strip pair at 25 nm, after a warm-up."""
    pair(res=0.06)
    rows = []
    for nm in (4, 12, 20):
        t0 = time.process_time()
        a = box(-0.6, 0, -0.1, 0.22); b = box(0.1, 0, 0.6, 0.22)
        polys = OrderedDict(left=a, right=b, clad=box(-3.5, -2.0, 3.5, 2.0))
        r_ = dict(left={"resolution": RES, "distance": 0.6}, right={"resolution": RES, "distance": 0.6})
        mesh = from_meshio(mesh_from_OrderedDict(polys, r_, default_resolution_max=0.25))
        basis0 = Basis(mesh, ElementTriP0())
        eps = basis0.zeros() + n_sio2(1.55) ** 2
        for k in ("left", "right"):
            eps[basis0.get_dofs(elements=k)] = n_si(1.55) ** 2
        compute_modes(basis0, eps, wavelength=1.55, num_modes=nm, order=2)
        sec = time.process_time() - t0
        rows.append(dict(modes=nm, sec=sec))
        print(f"eme: {nm} modes in {sec:.1f} s", flush=True)
    store("eme", rows)


def part_time25():
    """CPU time of one supermode solve at the production mesh (25 nm), three times after a warm-up solve (the first
    call of a process also pays for one-time initialisation). Run with every thread pool limited to one thread."""
    pair(res=0.06)
    secs = []
    for _ in range(3):
        ne, no, nodes, sec = pair(res=RES)
        secs.append(sec)
        print(f"time25: {nodes} nodes, {sec:.1f} s", flush=True)
    store("time25", dict(nodes=nodes, secs=secs, median=float(np.median(secs))))


def part_timing():
    ne, no, nodes, s = pair()
    print(f"timing: n_even {ne:.5f} n_odd {no:.5f} L_x {lx(ne, no):.2f} um, {nodes} nodes, {s:.1f} s", flush=True)


if __name__ == "__main__":
    for p in sys.argv[1:] or ["timing"]:
        globals()["part_" + p]()
