"""A full-vectorial finite-difference eigenmode (FDE) solver on a Yee grid, for Chapter 31 (Figure 31.2 and Section 31.2).

The same formulation as the in-browser solver of Chapter 6 (demos/modesolver.html), here on uniform grids: E_x and E_y
are the unknowns, the other four components are eliminated, and with fields ~ exp(-j beta z)

    beta^2 E_x = k^2 eps_x E_x + Ux Phi - Vy Psi,     beta^2 E_y = k^2 eps_y E_y + Uy Phi + Vx Psi,
    Phi = eps_z^-1 (Vx eps_x E_x + Vy eps_y E_y),       Psi = Ux E_y - Uy E_x,

where U are forward differences (from E-type points to H-type points) and V = -U^T backward ones. Positions in a cell:
E_x at (cell centre in x, grid line in y), E_y at (grid line, cell centre), E_z at grid nodes, H_z at cell centres.
Tangential E is zero on the window's edges (a metal box several decay lengths from the core).

The 500 x 220 nm silicon strip in oxide at 1550 nm (TE0), on uniform grids from 40 nm to 8 nm, with the permittivity at
each field point either sampled (staircase) or averaged over the cell around the point (harmonic mean across an
interface, arithmetic along it). The strip is offset from the grid by (13, 7) nm so that no grid line follows its walls.

Run (Docker container, needs SciPy):  python -u figsrc/ch31_fde.py  ->  figsrc/ch31_fde.json
                                     python -u figsrc/ch31_fde.py sweep  ->  figsrc/ch31_fde_sweep.json (strip and ribs against width)
"""
import json, os, sys, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

HERE = os.path.dirname(os.path.abspath(__file__))
LAM, N_SI, N_OX = 1.55, 3.4764, 1.4440
W, T = 0.50, 0.22
XC, YC = 0.013, 0.007                 # core centre (um), off the grid lines
LX, LY = 2.4, 1.8                     # window (um)
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f} s]", *a, flush=True)


def overlap(a, b, lo, hi):
    """Length of [a, b] inside [lo, hi] (arrays a, b)."""
    return np.clip(np.minimum(b, hi) - np.maximum(a, lo), 0, None)


def eps_at(X, Y, h, comp, mode):
    """Permittivity seen by field component comp ('x', 'y', 'z') at points (X, Y)."""
    e1, e2 = N_SI ** 2, N_OX ** 2
    x0, x1, y0, y1 = XC - W / 2, XC + W / 2, YC - T / 2, YC + T / 2
    if mode == "stair":
        inside = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
        return np.where(inside, e1, e2)
    fx = overlap(X - h / 2, X + h / 2, x0, x1) / h          # fraction of the cell around the point inside the core, in x
    fy = overlap(Y - h / 2, Y + h / 2, y0, y1) / h
    harm = lambda f: 1 / (f / e1 + (1 - f) / e2)
    if comp == "x":   # normal to the side walls: harmonic across x, arithmetic along y
        return fy * harm(fx) + (1 - fy) * e2
    if comp == "y":
        return fx * harm(fy) + (1 - fx) * e2
    return e2 + fx * fy * (e1 - e2)


def eps_sub(X, Y, h, comp, rects, M=10):
    """Averaged permittivity for any union of silicon rectangles (x0, x1, y0, y1) in oxide, from M x M samples of the
    cell around each point: harmonic mean along the field direction, arithmetic across it (arithmetic for E_z)."""
    e1, e2 = N_SI ** 2, N_OX ** 2
    o = (np.arange(M) + 0.5) / M * h - h / 2
    xs = X[..., None, None] + o[None, None, None, :]          # [..., row (y), column (x)]
    ys = Y[..., None, None] + o[None, None, :, None]
    inside = np.zeros(np.broadcast_shapes(xs.shape, ys.shape), bool)
    for x0, x1, y0, y1 in rects:
        inside |= (xs > x0) & (xs < x1) & (ys > y0) & (ys < y1)
    e = np.where(inside, e1, e2)
    if comp == "x":
        return np.mean(1 / np.mean(1 / e, axis=-1), axis=-1)
    if comp == "y":
        return np.mean(1 / np.mean(1 / e, axis=-2), axis=-1)
    return np.mean(e, axis=(-1, -2))


def solve(h, mode, n_guess=2.5, want_fields=False, rects=None):
    nx, ny = int(round(LX / h)), int(round(LY / h))
    xl = -LX / 2 + h * np.arange(nx + 1); yl = -LY / 2 + h * np.arange(ny + 1)
    xc, yc = (xl[:-1] + xl[1:]) / 2, (yl[:-1] + yl[1:]) / 2
    xn, yn = xl[1:-1], yl[1:-1]                               # interior grid lines
    k = 2 * np.pi / LAM

    def dnc(n):   # interior nodes (n - 1) -> cells (n): (f[i+1] - f[i]) / h, the boundary nodes being zero
        return (sp.eye(n, n - 1, k=0) - sp.eye(n, n - 1, k=-1)) / h

    Dx, Dy = dnc(nx).tocsr(), dnc(ny).tocsr()
    Ix_c, Ix_n, Iy_c, Iy_n = sp.eye(nx), sp.eye(nx - 1), sp.eye(ny), sp.eye(ny - 1)
    # E_x at (xc, yn), E_y at (xn, yc), E_z at (xn, yn), H_z at (xc, yc); arrays indexed [y, x], flattened row-major
    VxEx = sp.kron(Iy_n, -Dx.T)          # (xc, yn) -> (xn, yn)
    VyEy = sp.kron(-Dy.T, Ix_n)          # (xn, yc) -> (xn, yn)
    UxPhi = sp.kron(Iy_n, Dx)            # (xn, yn) -> (xc, yn)
    UyPhi = sp.kron(Dy, Ix_n)            # (xn, yn) -> (xn, yc)
    UxEy = sp.kron(Iy_c, Dx)             # (xn, yc) -> (xc, yc)
    UyEx = sp.kron(Dy, Ix_c)             # (xc, yn) -> (xc, yc)
    VyPsi = sp.kron(-Dy.T, Ix_c)         # (xc, yc) -> (xc, yn)
    VxPsi = sp.kron(Iy_c, -Dx.T)         # (xc, yc) -> (xn, yc)
    Xx, Yx = np.meshgrid(xc, yn); Xy, Yy = np.meshgrid(xn, yc); Xz, Yz = np.meshgrid(xn, yn)
    epf = (lambda X, Y, c: eps_at(X, Y, h, c, mode)) if rects is None else (lambda X, Y, c: eps_sub(X, Y, h, c, rects))
    ex = sp.diags(epf(Xx, Yx, "x").ravel())
    ey = sp.diags(epf(Xy, Yy, "y").ravel())
    ezi = sp.diags(1 / epf(Xz, Yz, "z").ravel())
    Pxx = k ** 2 * ex + UxPhi @ ezi @ VxEx @ ex + VyPsi @ UyEx
    Pxy = UxPhi @ ezi @ VyEy @ ey - VyPsi @ UxEy
    Pyx = UyPhi @ ezi @ VxEx @ ex - VxPsi @ UyEx
    Pyy = k ** 2 * ey + UyPhi @ ezi @ VyEy @ ey + VxPsi @ UxEy
    P = sp.bmat([[Pxx, Pxy], [Pyx, Pyy]]).tocsc()
    nexn = Xx.size
    vals, vecs = sla.eigs(P, k=3, sigma=(k * n_guess) ** 2, which="LM")
    best = None
    for v, vec in zip(vals, vecs.T):
        ne = np.sqrt(v.real) / k
        fx = np.sum(np.abs(vec[:nexn]) ** 2) / np.sum(np.abs(vec) ** 2)
        if fx > 0.5 and (best is None or ne > best[0]):
            best = (ne, fx, vec)
    out = {"h": h, "mode": mode, "nx": nx, "ny": ny, "unknowns": int(P.shape[0]), "nnz": int(P.nnz),
           "n_eff": float(best[0]), "ex_fraction": float(best[1])}
    if want_fields:
        Ex = np.real(best[2][:nexn] * np.exp(-1j * np.angle(best[2][np.argmax(np.abs(best[2][:nexn]))]))).reshape(Xx.shape)
        out["Ex"] = np.round(Ex / np.abs(Ex).max(), 4).tolist()
        out["xc"], out["yn"] = xc.tolist(), yn.tolist()
    return out


def sweep(kinds):
    """TE0 against width for the strip, a rib with a 90 nm slab and a shallow rib with a 150 nm slab (220 nm film), on a
    10 nm grid, for the comparison with the effective-index method (2D / 2.5D) in Figure 31.11. Kinds already in the
    JSON file are kept."""
    path = os.path.join(HERE, "ch31_fde_sweep.json")
    out = json.load(open(path)) if os.path.exists(path) else {"h": 0.010}
    slabs = {"strip": None, "rib": 0.09, "shallow": 0.15}
    for kind in kinds:
        out[kind] = []
        out.setdefault("slabs", {})[kind] = slabs[kind]
        for w in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2]:
            x0, x1, y0, y1 = XC - w / 2, XC + w / 2, YC - T / 2, YC + T / 2
            rects = [(x0, x1, y0, y1)] + ([(-9, 9, y0, y0 + slabs[kind])] if slabs[kind] else [])
            t1 = time.time()
            r = solve(0.010, "sub", rects=rects, n_guess=2.9)
            out[kind].append({"w": w, "n_eff": r["n_eff"], "ex_fraction": r["ex_fraction"]})
            log(f"{kind} w = {w:.2f}: n_eff {r['n_eff']:.5f} (Ex share {r['ex_fraction']:.3f}, {time.time() - t1:.1f} s)")
    json.dump(out, open(path, "w"), indent=1)
    log("wrote ch31_fde_sweep.json")


if __name__ == "__main__" and "sweep" in sys.argv:
    sweep(sys.argv[2:] or ["strip", "rib", "shallow"])
elif __name__ == "__main__":
    res = {"lam": LAM, "n_si": N_SI, "n_ox": N_OX, "w": W, "t": T, "core_centre": [XC, YC], "window": [LX, LY], "runs": []}
    hs = [0.040, 0.030, 0.024, 0.020, 0.015, 0.012, 0.010, 0.008]
    if os.environ.get("QUICK") == "1": hs = [0.04, 0.02]
    for h in hs:
        for mode in ["avg", "stair"]:
            t1 = time.time()
            r = solve(h, mode)
            r["cpu_s"] = time.time() - t1
            res["runs"].append(r)
            log(f"h = {1000 * h:4.1f} nm {mode:5s}: n_eff {r['n_eff']:.6f} ({r['unknowns']} unknowns, Ex share {r['ex_fraction']:.3f}, {r['cpu_s']:.1f} s)")
    # Richardson extrapolation of the averaged results (second order) from the three finest grids
    av = sorted([r for r in res["runs"] if r["mode"] == "avg"], key=lambda r: r["h"])[:4]
    A = np.array([[1, r["h"] ** 2] for r in av]); b = np.array([r["n_eff"] for r in av])
    coef = np.linalg.lstsq(A, b, rcond=None)[0]
    res["n_extrap"] = float(coef[0]); res["c2"] = float(coef[1])
    log("extrapolated n_eff (h -> 0):", coef[0], " slope coefficient", coef[1])
    res["field"] = solve(0.020, "avg", want_fields=True)
    json.dump(res, open(os.path.join(HERE, "ch31_fde.json"), "w"), indent=1)
    log("wrote ch31_fde.json")
