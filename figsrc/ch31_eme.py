"""Eigenmode expansion (EME) of a linear taper, for Chapter 31 (Figure 31.3, Section 31.3).

The taper of Chapter 8's adiabatic-taper demo: a 220 nm silicon strip widening linearly from 0.5 to 3 um at 1550 nm,
reduced to 2D by the effective-index method (lateral slab: core 2.8482, the 220 nm film's TE0 index, against oxide
1.4440; TE-like light, so the lateral problem has TM boundary conditions), in a 12 um box with H = 0 on its walls.

The algorithm is the textbook bidirectional EME:
  1. cut the taper into N sections of constant width (the width at each section's middle);
  2. in each section solve the lateral modes by finite differences: d/dx (1/eps dH/dx) + k^2 H = beta^2 H / eps;
  3. at each interface match the transverse fields with overlap integrals, giving the interface's reflection and
     transmission matrices,  T_AB = 2 (O_BA^T + O_AB)^-1,  R_AB = O_BA^T T_AB - I,  with O_AB[i, j] = int e_Ai h_Bj dx;
  4. join interfaces and propagation phases exp(-j beta L/N) with the Redheffer star product into one S-matrix.
Modes are normalised to unit power (int e h dx = 1, with e = beta H / eps the transverse E in these units). Only even
modes are kept, since the input is the symmetric TE0, so the half box x >= 0 suffices (dH/dx = 0 at x = 0). Changing
the taper's length changes only the propagation phases, so a length sweep reuses the interface matrices.

Run:  python -I -X utf8 figsrc/ch31_eme.py   ->  figsrc/ch31_eme.json   (NumPy only, a few minutes)
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAM, N_CORE, N_CLAD = 1.55, 2.8482, 1.4440
W0, W1, BOX, DX = 0.5, 3.0, 12.0, 0.01
K = 2 * np.pi / LAM
XH = np.arange(0, BOX / 2 + DX / 2, DX)       # half box; node weights 1/2 at x = 0 (trapezoid rule over the folded box)
WT = np.ones(XH.size); WT[0] = 0.5
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:6.1f} s]", *a, flush=True)


def inv_eps_avg(a, b, w):
    """Average of 1/eps over [a, b] (arrays) for a core of width w centred at 0."""
    inside = np.clip(np.minimum(b, w / 2) - np.maximum(a, -w / 2), 0, None)
    return (inside / N_CORE ** 2 + (b - a - inside) / N_CLAD ** 2) / (b - a)


def inv_eps_node(w):
    return inv_eps_avg(XH - DX / 2, XH + DX / 2, w)


_CACHE = {}


def modes(w, nmodes, lam=LAM):
    """The first nmodes even modes of a core of width w (solved once for 40 modes, then cached)."""
    key = (round(w, 10), lam)
    if key not in _CACHE:
        _CACHE[key] = solve_modes(w, 40, lam)
    return _CACHE[key][:nmodes]


def solve_modes(w, nmodes, lam=LAM):
    """Even TM lateral modes of a core of width w: list of (beta, H on XH), unit power, sorted by beta^2 descending."""
    am = inv_eps_avg(XH[:-1], XH[1:], w)                    # 1/eps on the half-cells between nodes
    n = XH.size - 1                                         # unknowns: all nodes but the wall
    bn = inv_eps_node(w)[:n] * WT[:n]
    off = am[:n - 1] / DX ** 2
    diag = -(np.concatenate([[0.0], am[:n - 1]]) + am[:n]) / DX ** 2 + (2 * np.pi / lam) ** 2 * WT[:n]
    A = np.diag(diag) + np.diag(off, 1) + np.diag(off, -1)
    s = 1 / np.sqrt(bn)
    lam, v = np.linalg.eigh(s[:, None] * A * s[None, :])    # B^-1/2 A B^-1/2 with B = diag(bn): symmetric
    out = []
    for i in np.argsort(-lam)[:nmodes]:
        H = np.concatenate([s * v[:, i], [0.0]])
        beta = np.sqrt(lam[i] + 0j)
        if beta.imag > 0: beta = -beta                       # evanescent modes decay for exp(-j beta z)
        norm = 2 * beta * np.sum(WT * H ** 2 * inv_eps_node(w)) * DX   # int e h dx over the whole box
        out.append((beta, H / np.sqrt(norm)))
    return out


def overlap(mA, wA, mB, wB):
    """O_AB[i, j] = int e_Ai h_Bj dx over the whole box, e = beta H / eps."""
    eA = np.array([b * H * inv_eps_node(wA) * WT for b, H in mA])
    hB = np.array([H for _, H in mB])
    return 2 * DX * eA @ hB.T


def interface(mA, wA, mB, wB):
    OAB, OBA = overlap(mA, wA, mB, wB), overlap(mB, wB, mA, wA)
    TAB = 2 * np.linalg.inv(OBA.T + OAB); RAB = OBA.T @ TAB - np.eye(len(mA))
    TBA = 2 * np.linalg.inv(OAB.T + OBA); RBA = OAB.T @ TBA - np.eye(len(mB))
    return (RAB, TAB, TBA, RBA)


def star(S1, S2):
    """Redheffer star product of S-matrices given as (R11, T21, T12, R22), port 1 on the left, port 2 on the right."""
    R11a, T21a, T12a, R22a = S1
    R11b, T21b, T12b, R22b = S2
    I = np.eye(R22a.shape[0])
    M1 = np.linalg.inv(I - R11b @ R22a)
    M2 = np.linalg.inv(I - R22a @ R11b)
    return (R11a + T12a @ R11b @ M1 @ T21a, T21b @ M1 @ T21a, T12a @ M2 @ T12b, R22b + T21b @ R22a @ M2 @ T12b)


def prop(betas, L):
    P = np.diag(np.exp(-1j * np.asarray(betas) * L))
    Z = np.zeros_like(P)
    return (Z, P, P, Z)


class Taper:
    def __init__(self, nsec, nmodes):
        self.ws = [W0] + [W0 + (k + 0.5) * (W1 - W0) / nsec for k in range(nsec)] + [W1]
        self.ms = [modes(w, nmodes) for w in self.ws]
        self.ifs = [interface(self.ms[k], self.ws[k], self.ms[k + 1], self.ws[k + 1]) for k in range(len(self.ws) - 1)]
        self.nsec = nsec

    def S(self, L):
        S = self.ifs[0]
        for k in range(1, self.nsec + 1):
            S = star(S, prop([b for b, _ in self.ms[k]], L / self.nsec))
            S = star(S, self.ifs[k])
        return S

    def out_powers(self, L):
        """Power in each output mode and the power reflected into the input TE0, for TE0 launched at the narrow end."""
        R11, T21, _, _ = self.S(L)
        return np.abs(T21[:, 0]) ** 2, np.abs(R11[0, 0]) ** 2


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    res = {"lam": LAM, "n_core": N_CORE, "n_clad": N_CLAD, "w0": W0, "w1": W1, "box": BOX, "dx": DX}
    m0, m1 = modes(W0, 4), modes(W1, 4)
    res["neff_in"] = float((m0[0][0] / K).real)
    res["neff_out"] = [float((b / K).real) for b, _ in m1[:3]]
    log("n_eff in", res["neff_in"], " out (TE0, TE2, TE4)", res["neff_out"])
    NS, NM = (40, 12) if quick else (200, 24)
    tp = Taper(NS, NM)
    log(f"taper with {NS} sections and {NM} even modes ready")
    Ls = np.round(np.concatenate([np.arange(1, 10, 0.5), np.arange(10, 61, 1.0)]), 3)
    res["L"] = Ls.tolist(); res["P_TE0"], res["P_TE2"], res["P_TE4"], res["R"] = [], [], [], []
    t1 = time.time()
    for L in Ls:
        P, R = tp.out_powers(L)
        res["P_TE0"].append(float(P[0])); res["P_TE2"].append(float(P[1])); res["P_TE4"].append(float(P[2])); res["R"].append(float(R))
        res.setdefault("P_sum", []).append(float(np.sum(P[[b.imag == 0 for b, _ in tp.ms[-1]]]) + R))
    res["sweep_s_per_length"] = (time.time() - t1) / len(Ls)
    for L in [4, 10, 20, 40]:
        i = int(np.argmin(np.abs(Ls - L)))
        log(f"L = {L} um: TE0 {res['P_TE0'][i]:.5f}, TE2 {res['P_TE2'][i]:.5f}, TE4 {res['P_TE4'][i]:.2e}, R {res['R'][i]:.1e}")
    res["profiles"] = []                                     # local TE0 profiles for the drawing
    for w in [0.5, 1.125, 1.75, 2.375, 3.0]:
        b, H = modes(w, 1)[0]
        H = np.real(H) / np.abs(H).max()
        res["profiles"].append({"w": w, "neff": float((b / K).real), "x": XH[::4].tolist(), "H": np.round(H[::4], 4).tolist()})
    res["conv_sections"] = []                               # convergence at L = 20 um
    for ns in ([1, 2, 4, 8, 16, 32] if quick else [1, 2, 4, 8, 16, 32, 64, 128, 200, 400]):
        t1 = time.time()
        P, R = Taper(ns, NM).out_powers(20.0)
        res["conv_sections"].append({"n": ns, "P_TE0": float(P[0]), "P_TE2": float(P[1]), "cpu_s": time.time() - t1})
        log(f"sections {ns:3d}: TE0 {P[0]:.5f} TE2 {P[1]:.5f}  ({time.time() - t1:.1f} s)")
    res["conv_modes"] = []
    for nm in [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 40]:
        P, R = Taper(NS, nm).out_powers(20.0)
        res["conv_modes"].append({"n": nm, "P_TE0": float(P[0]), "P_TE2": float(P[1]) if nm > 1 else 0.0})
        log(f"modes {nm:3d}: TE0 {P[0]:.5f}" + (f" TE2 {P[1]:.5f}" if nm > 1 else ""))
    if not quick:
        json.dump(res, open(os.path.join(HERE, "ch31_eme.json"), "w"), indent=1)
        log("wrote ch31_eme.json")
