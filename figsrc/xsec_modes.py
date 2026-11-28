"""Modes of the dimensioned cross-sections of Section 24.9 -> figsrc/xsec_modes.json.

Run where NumPy and SciPy (sparse eigensolver) work, from the repository root, for example in the EDA container:
  docker run --rm --entrypoint /bin/bash -v "$PWD":/w -w /w hpretl/iic-osic-tools:2026.10 -lc "python3 figsrc/xsec_modes.py"

Edge emitters (ridge, buried heterostructure, ridge SOA, slab-coupled SOA): the fundamental mode of the scalar
Helmholtz equation on the facet, by finite differences (five-point Laplacian, field zero on the window edge,
shift-invert Lanczos), adequate for these weakly guiding InP waveguides. Quantum wells are an averaged layer; their
confinement is the stack's share of the power times the wells' fill factor.
VCSEL: the effective-index model (Hadley 1995): transfer matrices give the cavity resonance with the 30 nm layer as
AlAs (aperture) and as AlOx (outside); the oxidised region resonates at a shorter wavelength, and its effective index is
lower by dn/n = dlambda/lambda; the lateral mode is then the LP01 mode of a step-index guide of the aperture's radius.
Stored: the numbers, and each intensity map cropped to where it exceeds 1e-3 and sampled more coarsely.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl
from scipy.special import j0, j1, k0, k1
from scipy.optimize import brentq
import xsec_devices as D

HERE = os.path.dirname(os.path.abspath(__file__))
_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")


def inside(px, py, pts):
    x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts]); res = np.zeros(px.shape, bool); j = len(pts) - 1
    for i in range(len(pts)):
        dy = y[j] - y[i]
        with np.errstate(divide="ignore", invalid="ignore"):
            xc = (x[j] - x[i]) * (py - y[i]) / np.where(dy == 0, 1e-300, dy) + x[i]
        res ^= ((y[i] > py) != (y[j] > py)) & (px < xc); j = i
    return res


def solve(shapes, xw, yw, dx, dy, lam, nbg=1.0, pick=None, nev=6, ntarget=None):
    x = np.arange(xw[0] + dx / 2, xw[1], dx); y = np.arange(yw[0] + dy / 2, yw[1], dy)
    X, Y = np.meshgrid(x, y); n = np.full(X.shape, nbg); key = np.full(X.shape, "", dtype=object)
    for s in shapes:
        if s["n"] is None: continue
        m = inside(X, Y, s["poly"]); n[m] = s["n"]; key[m] = s["key"]
    ny, nx = n.shape; N = nx * ny; kk = 2 * np.pi / lam
    main = -2 / dx ** 2 - 2 / dy ** 2 + (kk * n.ravel()) ** 2
    ex = np.full(N - 1, 1 / dx ** 2); ex[np.arange(1, ny) * nx - 1] = 0
    ey = np.full(N - nx, 1 / dy ** 2)
    A = sp.diags([main, ex, ex, ey, ey], [0, 1, -1, nx, -nx], format="csc")
    # several modes near the target index; keep the one with the most power in the 'pick' layers (keys, |x| limit):
    # this skips slab modes of layers such as a full-width InGaAs contact layer, which absorbs strongly in reality
    vals, vecs = spl.eigsh(A, k=nev, sigma=(kk * (ntarget or n.max())) ** 2, which="LM")
    best, bi = -1, 0
    for i in range(nev):
        I = vecs[:, i].reshape(ny, nx) ** 2; msk = np.isin(key, list(pick[0])) & (np.abs(X) <= pick[1]) if pick else np.ones_like(I, bool)
        f = I[msk].sum() / I.sum()
        if f > best: best, bi = f, i
    E = vecs[:, bi].reshape(ny, nx); E /= E.flat[np.argmax(np.abs(E))]
    return dict(x=x, y=y, X=X, Y=Y, key=key, E=E, I=E ** 2, neff=float(np.sqrt(vals[bi]) / kk), lam=lam, dx=dx, dy=dy)


def frac(m, keys, xlim=None, fill=1.0):
    msk = np.isin(m["key"], list(keys))
    if xlim is not None: msk &= (np.abs(m["X"]) <= xlim)
    return float(fill * m["I"][msk].sum() / m["I"].sum())


def span(v, c):
    lev = np.exp(-2) * v.max(); above = np.where(v >= lev)[0]; lo, hi = above.min(), above.max(); d = c[1] - c[0]
    xl = c[lo] - d * (v[lo] - lev) / (v[lo] - v[lo - 1]) if lo > 0 else c[0]
    xh = c[hi] + d * (v[hi] - lev) / (v[hi] - v[hi + 1]) if hi < len(c) - 1 else c[-1]
    return float(xh - xl)


def fwhm_ff(E, dx, dy, lam, pad=8):
    ny, nx = E.shape
    F = np.abs(np.fft.fftshift(np.fft.fft2(E, s=(ny * pad, nx * pad)))) ** 2
    kx = np.fft.fftshift(np.fft.fftfreq(nx * pad, d=dx)) * 2 * np.pi; ky = np.fft.fftshift(np.fft.fftfreq(ny * pad, d=dy)) * 2 * np.pi
    kk = 2 * np.pi / lam; cy, cx = np.unravel_index(np.argmax(F), F.shape)
    def fw(p, k):
        ok = np.abs(k) < kk; th = np.degrees(np.arcsin(k[ok] / kk)); q = p[ok] * np.cos(np.radians(th)) ** 2
        a = th[q >= q.max() / 2]; return float(a.max() - a.min())
    return fw(F[cy, :], kx), fw(F[:, cx], ky)


def pack(m, step=(2, 2)):
    I = m["I"] / m["I"].max(); rows = np.where(I.max(axis=1) > 1e-3)[0]; cols = np.where(I.max(axis=0) > 1e-3)[0]
    r0, r1, c0, c1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
    sub = I[r0:r1:step[1], c0:c1:step[0]]
    return dict(x=[round(float(v), 4) for v in m["x"][c0:c1:step[0]]], y=[round(float(v), 4) for v in m["y"][r0:r1:step[1]]],
                I=[[round(float(v), 4) for v in row] for row in sub])


def edge(name, shapes, xw, yw, dx, dy, keys, fill, xlim=None, step=(2, 2), area=None, pick=None, ntarget=3.3):
    m = solve(shapes, xw, yw, dx, dy, 1.55, pick=pick or ({"mqw", "sch", "slab"}, xlim or 99), ntarget=ntarget)
    j, i = np.unravel_index(np.argmax(m["I"]), m["I"].shape)
    w, h = span(m["I"][j, :], m["x"]), span(m["I"][:, i], m["y"])
    fx, fy = fwhm_ff(m["E"], dx, dy, 1.55)
    g = frac(m, keys, xlim, fill)
    aeff = float(m["I"].sum() ** 2 / (m["I"] ** 2).sum() * dx * dy)
    out = dict(neff=m["neff"], gamma=g, w=w, h=h, xp=float(m["x"][i]), yp=float(m["y"][j]), ffx=fx, ffy=fy, aeff=aeff, map=pack(m, step))
    if area is not None: out["A_over_gamma"] = area / g
    print(f"{name}: n_eff {m['neff']:.4f}, Gamma {g*100:.2f} %, 1/e2 {w:.2f} x {h:.2f} um, peak ({m['x'][i]:+.2f}, {m['y'][j]:+.3f}), "
          f"far field {fx:.1f} x {fy:.1f} deg, A_eff {aeff:.2f} um2" + (f", A/Gamma {area/g:.2f} um2" if area else ""))
    return out


# ---------------------------------------------------------------- VCSEL
def tmm_field_centre(layers, lam, which):
    """|E|^2 at the cavity centre for light incident from the top, by characteristic matrices from the substrate up."""
    E, H = 1.0 + 0j, VCn("nsub") + 0j
    zc = None; z = 0.0; vals = []
    for name, d, na, no in reversed(layers):
        n = na if which == "ap" else no
        if name == "cav":
            kd = 2 * np.pi * n / lam * d / 2
            M = np.array([[np.cos(kd), 1j * np.sin(kd) / n], [1j * n * np.sin(kd), np.cos(kd)]]); e, _ = M @ np.array([E, H]); vals.append(abs(e) ** 2)
        kd = 2 * np.pi * n / lam * d
        M = np.array([[np.cos(kd), 1j * np.sin(kd) / n], [1j * n * np.sin(kd), np.cos(kd)]]); E, H = M @ np.array([E, H])
    # normalise to the incident wave from air: E_top = E, H_top = H -> incident amplitude (E + H)/2 (n_air = 1)
    inc = abs((E + H) / 2) ** 2
    return vals[0] / inc


def VCn(k): return D.VC[k]


def vcsel():
    L = D.vcsel_layers(); lam0 = D.VC["lam"]
    lams = np.linspace(0.835, 0.865, 3001)
    res = {}
    for which in ("ap", "ox"):
        f = np.array([tmm_field_centre(L, l, which) for l in lams]); i = int(f.argmax())
        ll = np.linspace(lams[max(i - 2, 0)], lams[min(i + 2, len(lams) - 1)], 801)
        f2 = np.array([tmm_field_centre(L, l, which) for l in ll]); res[which] = float(ll[f2.argmax()])
    dlam = res["ap"] - res["ox"]; dn_rel = dlam / res["ap"]
    n1 = D.VC["nc"]; n2 = n1 * (1 - dn_rel); a = D.VC["r_ap"]; kk = 2 * np.pi / res["ap"]
    V = kk * a * np.sqrt(n1 ** 2 - n2 ** 2)
    f = lambda u: u * j1(u) / j0(u) - np.sqrt(V ** 2 - u ** 2) * k1(np.sqrt(V ** 2 - u ** 2)) / k0(np.sqrt(V ** 2 - u ** 2))
    u = brentq(f, 1e-6, min(2.4048 - 1e-6, V - 1e-6)); w = np.sqrt(V ** 2 - u ** 2)
    r = np.linspace(0, 3 * a, 1201)
    Er = np.where(r <= a, j0(u * r / a), j0(u) / k0(w) * k0(np.maximum(w * r / a, 1e-12)))
    Ir = Er ** 2; d_e2 = 2 * float(r[np.argmin(np.abs(Ir - np.exp(-2) * Ir[0]))])
    gam_lat = float(_trapz(Ir[r <= a] * r[r <= a], r[r <= a]) / _trapz(Ir * r, r))
    # far field: FFT of the 2D field on a grid
    g = np.arange(-12, 12, 0.05); X, Y = np.meshgrid(g, g); R = np.hypot(X, Y)
    E2 = np.interp(R, r, Er, right=0.0)
    ffx, _ = fwhm_ff(E2, 0.05, 0.05, res["ap"], pad=4)
    vnext = 2.4048   # LP11 cut-off: V above it guides more modes
    print(f"vcsel: resonance {res['ap']*1e3:.2f} nm in the aperture, {res['ox']*1e3:.2f} nm under the oxide (shift {dlam*1e3:.2f} nm): "
          f"dn/n {dn_rel*100:.3f} %, V {V:.2f} ({'multimode' if V > vnext else 'single-mode'}), LP01 u {u:.3f} w {w:.3f}; "
          f"1/e2 diameter {d_e2:.2f} um; {gam_lat*100:.0f} % of the power inside the aperture; far field FWHM {ffx:.1f} deg")
    return dict(lam_ap=res["ap"], lam_ox=res["ox"], dlam=dlam, dn_rel=dn_rel, V=V, u=float(u), w=float(w), d_e2=d_e2, gam_lat=gam_lat,
                ff=ffx, r=[round(float(v), 4) for v in r[::4]], I=[round(float(v), 5) for v in (Ir / Ir[0])[::4]])


if __name__ == "__main__":
    if "--scan" in sys.argv:                                   # try slab-coupled variants: slab thickness, wells
        for ts in (2.5, 3.0, 3.5):
            for nw in (3, 4, 5):
                D.set_scow(ts, nw)
                edge(f"scow slab {ts} wells {nw}", D.scow(), (-10, 10), (-9.0, 0.6), 0.06, 0.02, {"mqw"}, D.SCOW_FILL, xlim=2.5, area=5.0 * D.SCOW_WELLS)
        sys.exit()
    out = {}
    out["ridge"] = edge("ridge", D.ridge(), (-5, 5), (-5.0, 0.6), 0.04, 0.01, {"mqw"}, 50 / 90, xlim=1.0, area=2.0 * 0.050)
    # the BH window stops 0.25 um below its full-width InGaAs contact layer: that layer absorbs strongly at 1550 nm, which
    # this real-index solver cannot represent, and left in it would hybridise with the laser mode as a lossless slab guide
    out["bh"] = edge("bh", D.bh(), (-4, 4), (-6.0, -0.45), 0.03, 0.01, {"mqw"}, 50 / 90, xlim=0.75, area=1.5 * 0.050)
    out["soa_ridge"] = edge("soa ridge", D.ridge(RW=2.5, metal=(-2.25, 2.25)), (-5, 5), (-5.0, 0.6), 0.04, 0.01, {"mqw"}, 50 / 90,
                            xlim=1.25, area=2.5 * 0.050)
    out["soa_scow"] = edge("soa slab-coupled", D.scow(), (-10, 10), (-9.0, 0.6), 0.06, 0.02, {"mqw"}, D.SCOW_FILL, xlim=2.5,
                           step=(2, 2), area=5.0 * D.SCOW_WELLS)
    out["vcsel"] = vcsel()
    json.dump(out, open(os.path.join(HERE, "xsec_modes.json"), "w"), separators=(",", ":"))
    print("wrote figsrc/xsec_modes.json")
