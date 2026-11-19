"""Lab 4: MZI and ring circuits with S-parameters (Open-Photonics, Chapters 11, 12 and 30).

Run it from a terminal:
    python lab04_sax.py              # prints every checkpoint and saves lab04_sax.png
    python lab04_sax.py --numpy      # use the script's own NumPy circuit solver even if SAX is installed
    python lab04_sax.py --no-plot    # numbers only

It needs NumPy and Matplotlib. SAX (pip install sax, which brings JAX) is optional: without it, every circuit
is solved by the NumPy function np_circuit below, which takes the same netlists and models.
Lengths are in micrometres, wavelengths too.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-04/
"""
import json
import sys

import numpy as np

try:
    if "--numpy" in sys.argv:
        raise ImportError
    import jax.numpy as xp          # the models are written once, for JAX (SAX) or NumPy
    import sax
    HAVE_SAX = True
except ImportError:
    xp, sax, HAVE_SAX = np, None, False

N_EFF, N_G, LAM = 2.446, 4.18, 1.55   # 500 x 220 nm strip, TE0 at 1550 nm (Table 6.1)


# ---------------------------------------------------------------------------------------------------------
# Part A. Compact models (Chapter 30, Section 30.6)
# ---------------------------------------------------------------------------------------------------------
def reciprocal(s):
    """Add the reverse direction of every entry: a passive, non-magnetic device is reciprocal."""
    return {**s, **{(b, a): v for (a, b), v in s.items()}}


def waveguide(wl=LAM, length=10.0, neff=N_EFF, ng=N_G, loss_db_cm=0.0, wl0=LAM):
    """A straight waveguide: field transmission a e^{-j beta L}.

    n_eff falls linearly with wavelength at the rate the group index sets, dn_eff/dlam = -(n_g - n_eff)/lam
    (Chapter 2), so the phase has the right slope (n_g) as well as the right value (n_eff) at wl0.
    """
    ne = neff - (ng - neff) * (wl - wl0) / wl0
    amp = 10 ** (-loss_db_cm * length * 1e-4 / 20)          # dB/cm of power -> field amplitude over length um
    return reciprocal({("in0", "out0"): amp * xp.exp(-2j * xp.pi * ne * length / wl)})


def coupler(wl=LAM, coupling=0.5):
    """A lossless directional coupler with power coupling kappa^2 = coupling (Chapter 9 convention).

        in0 ---\\___/--- out0        out0 = t in0 - j kappa in1
        in1 ---/   \\--- out1        out1 = -j kappa in0 + t in1
    """
    one = xp.ones_like(xp.asarray(wl, dtype=float))
    t, k = xp.sqrt(1 - coupling) * one, -1j * xp.sqrt(coupling) * one
    return reciprocal({("in0", "out0"): t, ("in0", "out1"): k, ("in1", "out0"): k, ("in1", "out1"): t})


def ring(wl=LAM, coupling=0.005, radius=10.0, loss_db_cm=2.0, neff=N_EFF, ng=N_G):
    """An all-pass ring as one compact model: the closed form of Section 12.2 for the through field.

    With the coupler above and a loop of field transmission w = a e^{-j phi}, the light that circulates any
    number of times adds up to (t - w)/(1 - t w). Part C checks it against the same ring built as a circuit.
    """
    t = xp.sqrt(1 - coupling)
    w = waveguide(wl, 2 * np.pi * radius, neff, ng, loss_db_cm)[("in0", "out0")]
    return reciprocal({("in0", "out0"): (t - w) / (1 - t * w)})


MODELS = {"waveguide": waveguide, "coupler": coupler, "ring": ring}


def ring_kappa2(gap, radius=10.0, lam=LAM):
    """kappa^2 of a ring-to-bus point coupler from the femwell-fitted coupler model of Chapter 9 (ring demo).

    Two straight 500 nm strips at gap g have n_even - n_odd = 0.0205 exp(-8.75 (g - 0.2)); along the curved gap
    g + z^2/(2R) the coupling adds up to that of a straight coupler sqrt(2 pi R / 8.75) long.
    """
    dn = 0.0205 * np.exp(-8.75 * (gap - 0.2))
    l_eff = np.sqrt(2 * np.pi * radius / 8.75)
    return np.sin(np.pi * l_eff * dn / lam) ** 2          # sin^2(pi L / (2 L_x)) with L_x = lam / (2 dn)


# ---------------------------------------------------------------------------------------------------------
# Netlists: instances, the model and settings of each, connections, and the circuit's own ports
# ---------------------------------------------------------------------------------------------------------
def mzi_netlist(dl=100.0, k1=0.5, k2=0.5):
    """Unbalanced MZI as in the Chapter 30 demo: the upper arm is dl longer; the lower arm joins the couplers."""
    return {"instances": {"dc1": {"component": "coupler", "settings": {"coupling": k1}},
                          "delay": {"component": "waveguide", "settings": {"length": dl}},
                          "dc2": {"component": "coupler", "settings": {"coupling": k2}}},
            "connections": {"dc1,out0": "delay,in0", "delay,out0": "dc2,in0", "dc1,out1": "dc2,in1"},
            "ports": {"in": "dc1,in0", "in2": "dc1,in1", "bar": "dc2,out0", "cross": "dc2,out1"}}


def lattice_netlist(dl=100.0, ks=(0.78, 0.84, 0.70)):
    """Two-stage lattice of the Chapter 30 demo: couplers ks with delays dl and 2 dl in the upper arm."""
    inst = {f"dc{i + 1}": {"component": "coupler", "settings": {"coupling": k}} for i, k in enumerate(ks)}
    inst["d1"] = {"component": "waveguide", "settings": {"length": dl}}
    inst["d2"] = {"component": "waveguide", "settings": {"length": 2 * dl}}
    return {"instances": inst,
            "connections": {"dc1,out0": "d1,in0", "d1,out0": "dc2,in0", "dc1,out1": "dc2,in1",
                            "dc2,out0": "d2,in0", "d2,out0": "dc3,in0", "dc2,out1": "dc3,in1"},
            "ports": {"in": "dc1,in0", "in2": "dc1,in1", "bar": "dc3,out0", "cross": "dc3,out1"}}


def allpass_netlist(kappa2, radius=10.0, loss_db_cm=2.0):
    """All-pass ring: the coupler's second waveguide is closed on itself by a loop 2 pi R long."""
    return {"instances": {"dc": {"component": "coupler", "settings": {"coupling": kappa2}},
                          "loop": {"component": "waveguide",
                                   "settings": {"length": 2 * np.pi * radius, "loss_db_cm": loss_db_cm}}},
            "connections": {"dc,out1": "loop,in0", "loop,out0": "dc,in1"},
            "ports": {"in": "dc,in0", "through": "dc,out0"}}


def adddrop_netlist(k1, k2, radius=10.0, loss_db_cm=2.0):
    """Add-drop ring: two couplers joined by two half rings. The ring runs in1 -> out1 through each coupler."""
    half = {"component": "waveguide", "settings": {"length": np.pi * radius, "loss_db_cm": loss_db_cm}}
    return {"instances": {"dc1": {"component": "coupler", "settings": {"coupling": k1}},
                          "dc2": {"component": "coupler", "settings": {"coupling": k2}},
                          "top": half, "bottom": dict(half)},
            "connections": {"dc1,out1": "top,in0", "top,out0": "dc2,in1",
                            "dc2,out1": "bottom,in0", "bottom,out0": "dc1,in1"},
            "ports": {"in": "dc1,in0", "through": "dc1,out0", "add": "dc2,in0", "drop": "dc2,out0"}}


# ---------------------------------------------------------------------------------------------------------
# Part F. The same netlist in plain NumPy
# ---------------------------------------------------------------------------------------------------------
def np_circuit(netlist, models=MODELS):
    """Return a function wl -> S-parameters of the circuit, as sax.circuit does, in plain NumPy.

    Every port of every instance gets an index. With a the waves going into the ports and b the waves
    coming out, the instances together give b = S a, with S block-diagonal. A connection between ports u and
    v says a_u = b_v and a_v = b_u: a_int = P b_int for the internal ports. Eliminating them leaves
        S_circuit = S_ee + S_ei P (I - S_ii P)^-1 S_ie,
    one small linear solve per wavelength, which also handles loops such as a ring.
    """
    def evaluate(wl=LAM):
        wl = np.atleast_1d(np.asarray(wl, dtype=float))
        ports, blocks = [], []
        for name, inst in netlist["instances"].items():
            s = models[inst["component"]](wl=wl, **inst.get("settings", {}))
            names = sorted({p for pair in s for p in pair})
            ports += [f"{name},{p}" for p in names]
            blk = np.zeros((len(wl), len(names), len(names)), dtype=complex)
            for (p_in, p_out), v in s.items():             # s[(p_in, p_out)]: from p_in to p_out
                blk[:, names.index(p_out), names.index(p_in)] = np.broadcast_to(np.asarray(v), wl.shape)
            blocks.append(blk)
        n = len(ports)
        S = np.zeros((len(wl), n, n), dtype=complex)
        i0 = 0
        for blk in blocks:
            m = blk.shape[1]
            S[:, i0:i0 + m, i0:i0 + m] = blk
            i0 += m
        ext = [ports.index(p) for p in netlist["ports"].values()]
        internal = [i for i in range(n) if i not in ext]
        P = np.zeros((len(internal), len(internal)))
        for u, v in netlist["connections"].items():
            iu, iv = internal.index(ports.index(u)), internal.index(ports.index(v))
            P[iu, iv] = P[iv, iu] = 1
        Sii, Sie = S[:, internal][:, :, internal], S[:, internal][:, :, ext]
        Sei, See = S[:, ext][:, :, internal], S[:, ext][:, :, ext]
        X = np.linalg.solve(np.eye(len(internal)) - Sii @ P, Sie)
        Sc = See + Sei @ P @ X
        names = list(netlist["ports"])
        return {(a, b): Sc[:, j, i] for i, a in enumerate(names) for j, b in enumerate(names)}
    return evaluate


_BUILT = {}


def circuit(netlist):
    """sax.circuit when SAX is installed, else the NumPy solver; either way a function of wl.

    Each netlist is built once and kept, since SAX analyses the netlist and JAX compiles it on first use.
    """
    if not HAVE_SAX:
        return np_circuit(netlist)
    key = json.dumps(netlist, sort_keys=True)
    if key not in _BUILT:
        _BUILT[key] = sax.circuit(netlist, MODELS)[0]
    return _BUILT[key]


def power(S, a, b):
    return np.abs(np.asarray(S[(a, b)])) ** 2


def db(x):
    return 10 * np.log10(np.maximum(x, 1e-12))


# ---------------------------------------------------------------------------------------------------------
# Measuring spectra
# ---------------------------------------------------------------------------------------------------------
def minima(wl, y):
    """Wavelengths of the local minima of y, refined by a parabola through the three lowest samples."""
    i = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1
    out = []
    for k in i:
        y0, y1, y2 = y[k - 1], y[k], y[k + 1]
        out.append(wl[k] + 0.5 * (wl[1] - wl[0]) * (y0 - y2) / (y0 - 2 * y1 + y2))
    return np.array(out)


def resonance(fn, port, near=LAM, fsr=0.0092, n=40001):
    """Find the resonance nearest `near`, then measure it on a fine grid: (lam_res, T_min, FWHM).

    The FWHM is the full width where the dip 1 - T (or the peak, for a drop port) is half its height.
    """
    wl = np.linspace(near - fsr / 2, near + fsr / 2, 4001)
    T = power(fn(wl=wl), "in", port)
    dip = port != "drop"
    k = np.argmin(T) if dip else np.argmax(T)
    wl = np.linspace(wl[k] - 2e-4, wl[k] + 2e-4, n)          # +-200 pm around it, in 0.01 pm steps
    T = power(fn(wl=wl), "in", port)
    h = (1 - T) if dip else T
    k = np.argmax(h)
    above = np.where(h >= h[k] / 2)[0]
    lo, hi = above[0], above[-1]                            # interpolate both half-height crossings
    x_lo = wl[lo - 1] + (wl[lo] - wl[lo - 1]) * (h[k] / 2 - h[lo - 1]) / (h[lo] - h[lo - 1])
    x_hi = wl[hi] + (wl[hi + 1] - wl[hi]) * (h[k] / 2 - h[hi]) / (h[hi + 1] - h[hi])
    return wl[k], T[k], x_hi - x_lo


def flat_top(wl, cross_db, centre=(1.545, 1.555), drop_db=1.0):
    """Width of the passband around its highest point between `centre`, down to drop_db below it (interpolated)."""
    inside = np.where((wl > centre[0]) & (wl < centre[1]))[0]
    im = inside[np.argmax(cross_db[inside])]
    lev = cross_db[im] - drop_db
    a, c = im, im
    while cross_db[a] > lev:
        a -= 1
    while cross_db[c] > lev:
        c += 1
    xa = wl[a] + (wl[a + 1] - wl[a]) * (lev - cross_db[a]) / (cross_db[a + 1] - cross_db[a])
    xc = wl[c - 1] + (wl[c] - wl[c - 1]) * (lev - cross_db[c - 1]) / (cross_db[c] - cross_db[c - 1])
    return xc - xa


def shallowest_minimum(y):
    """The highest of the local minima of y: for a flat-top filter, the dip between its two peaks."""
    return y[np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1].max()


def main(plot=True):
    print("Lab 4: MZI and ring circuits with S-parameters (lengths and wavelengths in um)")
    print(f"   circuit solver: {'SAX ' + sax.__version__ + ' (JAX)' if HAVE_SAX else 'NumPy (np_circuit)'}\n")

    # ---- Part A
    wl = np.array([LAM - 1e-4, LAM + 1e-4])                  # +-0.1 nm: the phase of 100 um moves by 0.2 rad
    ph = np.unwrap(np.angle(np.asarray(waveguide(wl=wl, length=100.0)[("in0", "out0")])))
    ng_back = (LAM**2 / (2 * np.pi * 100.0)) * (ph[1] - ph[0]) / (wl[1] - wl[0])
    s = coupler(wl=LAM, coupling=0.3)
    col = abs(complex(s[("in0", "out0")])) ** 2 + abs(complex(s[("in0", "out1")])) ** 2
    L = 2 * np.pi * 10
    a = 10 ** (-2.0 * L * 1e-4 / 20)
    print("A. Compact models")
    print(f"   waveguide: n_eff(1500 nm) = {N_EFF - (N_G - N_EFF) * (1.5 - LAM) / LAM:.4f}, n_eff(1600 nm) = "
          f"{N_EFF - (N_G - N_EFF) * (1.6 - LAM) / LAM:.4f}; group index from its phase slope = {ng_back:.4f}")
    print(f"   coupler, 30 %: |t|^2 + |kappa|^2 = {col:.6f} (lossless)")
    print(f"   10 um ring at 2 dB/cm: round-trip field transmission a = {a:.5f}, intrinsic Q = "
          f"{2 * np.pi * N_G / (LAM * 2.0 * 100 / 4.343 * 1e-6):.3g}   (Chapter 12: 0.99855 and 3.7e5)\n")

    # ---- Part B: the unbalanced MZI
    mzi = circuit(mzi_netlist(100.0))
    wl = np.linspace(1.53, 1.57, 8001)
    S = mzi(wl=wl)
    bar, cross = power(S, "in", "bar"), power(S, "in", "cross")
    nulls = minima(wl, bar)
    k = np.argmin(abs(nulls - LAM))
    pair = nulls[k:k + 2] if nulls[k] < LAM else nulls[k - 1:k + 1]
    fsr = pair[1] - pair[0]
    s0 = mzi(wl=np.array([LAM]))
    print("B. Unbalanced MZI, dL = 100 um, two 50 % couplers")
    print(f"   FSR between the bar-port nulls at {1000 * pair[0]:.2f} and {1000 * pair[1]:.2f} nm: {1000 * fsr:.3f} nm;"
          f" lam^2/(n_g dL) = {1000 * LAM**2 / (N_G * 100):.3f} nm   (Chapter 11: 5.75 nm)")
    print(f"   with n_eff instead of n_g it would be {1000 * LAM**2 / (N_EFF * 100):.2f} nm   (Chapter 6: 9.8 nm)")
    print(f"   n_g read back from the FSR (Section 11.6): {np.mean(pair)**2 / (fsr * 100):.3f}")
    print(f"   at 1550 nm: bar {db(power(s0, 'in', 'bar'))[0]:.2f} dB, cross {db(power(s0, 'in', 'cross'))[0]:.2f} dB"
          f"   (Chapter 30 demo: -4.9 and -1.7 dB)")
    print(f"   extinction of the bar port {db(bar.max() / bar.min()):.0f} dB; bar + cross = "
          f"{(bar + cross).min():.6f} to {(bar + cross).max():.6f}\n")

    # ---- Part C: the all-pass ring of Table 12.1
    print("C. All-pass ring, R = 10 um, 2 dB/cm (Table 12.1: 1.23 / 0.52 / 0.22 %, 22.3 / 11.7 / 7.4 pm,")
    print("   Q 70 000 / 132 000 / 211 000, extinction 4.1 / 11.0 / 16.7 dB)")
    table = {}
    for gap in (0.20, 0.25, 0.30):
        K = ring_kappa2(gap)
        ap = circuit(allpass_netlist(K))
        lr, tmin, fw = resonance(ap, "through")
        t = np.sqrt(1 - K)
        fw_formula = (1 - a * t) * lr**2 / (np.pi * N_G * L * np.sqrt(a * t))
        regime = "over-coupled" if t < a else "under-coupled"
        table[gap] = (K, lr, tmin, fw)
        print(f"   gap {1000 * gap:.0f} nm: kappa^2 = {100 * K:.2f} %, t = {t:.5f} ({regime}); resonance at "
              f"{1000 * lr:.3f} nm: extinction {-db(tmin):.1f} dB, FWHM {1e6 * fw:.1f} pm (formula {1e6 * fw_formula:.1f}),"
              f" Q = {lr / fw:,.0f}")
    ring_c = circuit(allpass_netlist(ring_kappa2(0.25)))
    wl = np.linspace(1.535, 1.565, 30001)
    S = ring_c(wl=wl)
    s_model = np.asarray(ring(wl=wl, coupling=ring_kappa2(0.25))[("in0", "out0")])
    print(f"   the closed-form ring model against the circuit, 1535-1565 nm: largest difference "
          f"{np.max(np.abs(np.asarray(S['in', 'through']) - s_model)):.1e}")
    dips = minima(wl, power(S, "in", "through"))
    k = np.argmin(abs(dips - LAM))
    print(f"   FSR between resonances at {1000 * dips[k - 1]:.2f}, {1000 * dips[k]:.2f} and {1000 * dips[k + 1]:.2f} nm:"
          f" {1000 * (dips[k] - dips[k - 1]):.2f} and {1000 * (dips[k + 1] - dips[k]):.2f} nm;"
          f" lam^2/(n_g L) at 1550 nm = {1000 * LAM**2 / (N_G * L):.2f} nm   (Chapter 12: 9.15 nm)\n")

    # ---- Part D: the add-drop ring
    K = ring_kappa2(0.25)
    ad = circuit(adddrop_netlist(K, K))
    lr, dmax, fw = resonance(ad, "drop")
    s = ad(wl=np.array([lr]))
    t = np.sqrt(1 - K)
    drop_formula = (1 - t**2) ** 2 * a / (1 - t * t * a) ** 2
    print("D. Add-drop ring, R = 10 um, 250 nm gaps on both sides, 2 dB/cm")
    print(f"   drop peak {db(dmax):.2f} dB (Section 12.3 formula {db(drop_formula):.2f} dB), through port on resonance "
          f"{db(power(s, 'in', 'through'))[0]:.1f} dB")
    q_i = 2 * np.pi * N_G / (lr * 2.0 * 100 / 4.343 * 1e-6)             # intrinsic Q at 2 dB/cm
    k_ap, lr_ap, _, fw_ap = table[0.25]
    q_c = 1 / (fw_ap / lr_ap - 1 / q_i)                                 # 1/Q_L = 1/Q_i + 1/Q_c for the all-pass ring
    print(f"   drop FWHM {1e6 * fw:.1f} pm, loaded Q = {lr / fw:,.0f}; with Q_i = {q_i:,.0f} and the all-pass ring's"
          f" Q_c = {q_c:,.0f} per coupler, 1/Q_L = 1/Q_i + 2/Q_c gives {1 / (1 / q_i + 2 / q_c):,.0f}\n")

    # ---- Part E: the two-stage lattice filter
    wl = np.linspace(1.53, 1.57, 40001)
    x_mzi = db(power(circuit(mzi_netlist(100.0))(wl=wl), "in", "cross"))
    x_lat = db(power(circuit(lattice_netlist(100.0))(wl=wl), "in", "cross"))
    w_mzi, w_lat = flat_top(wl, x_mzi), flat_top(wl, x_lat)
    print("E. Two-stage lattice filter, couplers 78 / 84 / 70 %, delays 100 and 200 um")
    print(f"   cross-port passband within 1 dB: lattice {1000 * w_lat:.2f} nm, plain MZI {1000 * w_mzi:.2f} nm"
          f"   (Chapter 30 demo: 2.9 and 1.7 nm)")
    peaks = x_lat[np.where((x_lat[1:-1] > x_lat[:-2]) & (x_lat[1:-1] >= x_lat[2:]))[0] + 1]
    fsr = LAM**2 / (N_G * 100)
    one = np.linspace(LAM - fsr / 2, LAM + fsr / 2, 20001)            # one period around 1550 nm
    y_lat = db(power(circuit(lattice_netlist(100.0))(wl=one), "in", "cross"))
    y_mzi = db(power(circuit(mzi_netlist(100.0))(wl=one), "in", "cross"))
    print(f"   lattice: two peaks at {peaks.max():.2f} dB with a {peaks.max() - shallowest_minimum(x_lat):.2f} dB dip between them;"
          f" null {x_lat.min():.1f} dB   (Chapter 30 demo: a -20 dB stop band)")
    edges = [1000 * fsr * (1 - np.mean(y > y.max() - 1) - np.mean(y < -10)) / 2 for y in (y_lat, y_mzi)]
    print(f"   each edge falls from -1 to -10 dB in {edges[0]:.2f} nm (MZI {edges[1]:.2f} nm); below -10 dB for "
          f"{1000 * fsr * np.mean(y_lat < -10):.2f} nm of each {1000 * fsr:.2f} nm period (MZI {1000 * fsr * np.mean(y_mzi < -10):.2f} nm)\n")

    # ---- Part F: NumPy against SAX
    print("F. The same netlists in plain NumPy (np_circuit)")
    if HAVE_SAX:
        wl = np.linspace(1.545, 1.555, 2001)
        for name, net in (("MZI", mzi_netlist(100.0)), ("lattice", lattice_netlist(100.0)),
                          ("all-pass ring", allpass_netlist(ring_kappa2(0.25))),
                          ("add-drop ring", adddrop_netlist(K, K))):
            Ss, Sn = sax.circuit(net, MODELS)[0](wl=wl), np_circuit(net)(wl=wl)
            err = max(np.max(np.abs(np.asarray(Ss[key]) - Sn[key])) for key in Sn)
            print(f"   {name:14s}: largest difference between SAX and NumPy over {len(Sn)} S-parameters = {err:.1e}")
    else:
        print("   SAX is not installed (or --numpy was given): every number above came from np_circuit.")

    if plot:
        make_figure(table)


def make_figure(table):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    # (a) the MZI
    wl = np.linspace(1.53, 1.57, 8001)
    S = circuit(mzi_netlist(100.0))(wl=wl)
    ax[0, 0].plot(1000 * wl, db(power(S, "in", "cross")), color="tab:red", lw=1.2, label="cross")
    ax[0, 0].plot(1000 * wl, db(power(S, "in", "bar")), color="tab:blue", lw=1.2, label="bar")
    ax[0, 0].set(xlabel="wavelength (nm)", ylabel="transmission (dB)", ylim=(-40, 2),
                 title="(a) MZI, ΔL = 100 µm: FSR 5.75 nm")
    ax[0, 0].legend(loc="lower right", fontsize=8)
    # (b) the three all-pass rings around their resonances
    for (gap, (K, lr, tmin, fw)), col in zip(table.items(), ("tab:red", "tab:green", "tab:blue")):
        x = np.linspace(lr - 60e-6, lr + 60e-6, 2001)
        T = power(circuit(allpass_netlist(K))(wl=x), "in", "through")
        ax[0, 1].plot(1e6 * (x - lr), db(T), color=col, label=f"gap {1000 * gap:.0f} nm, κ² = {100 * K:.2f} %")
    ax[0, 1].set(xlabel="detuning from resonance (pm)", ylabel="through port (dB)", ylim=(-20, 1),
                 title="(b) all-pass rings of Table 12.1")
    ax[0, 1].legend(loc="lower right", fontsize=8)
    # (c) the add-drop ring around one resonance, against the all-pass ring with the same gap
    K = ring_kappa2(0.25)
    lr = table[0.25][1]
    x = np.linspace(lr - 60e-6, lr + 60e-6, 2001)
    S = circuit(adddrop_netlist(K, K))(wl=x)
    ax[1, 0].plot(1e6 * (x - lr), db(power(S, "in", "through")), color="tab:orange", label="add-drop: through")
    ax[1, 0].plot(1e6 * (x - lr), db(power(S, "in", "drop")), color="tab:blue", label="add-drop: drop")
    ax[1, 0].plot(1e6 * (x - lr), db(power(circuit(allpass_netlist(K))(wl=x), "in", "through")), color="tab:green",
                  ls="--", lw=1, label="all-pass: through")
    ax[1, 0].set(xlabel="detuning from resonance (pm)", ylabel="transmission (dB)", ylim=(-30, 1),
                 title="(c) add-drop ring, 250 nm gaps")
    ax[1, 0].legend(loc="lower right", fontsize=8)
    # (d) lattice against MZI, cross port
    wl = np.linspace(1.54, 1.56, 4001)
    ax[1, 1].plot(1000 * wl, db(power(circuit(mzi_netlist(100.0))(wl=wl), "in", "cross")), color="grey",
                  lw=1.2, label="MZI, 50 / 50 %")
    ax[1, 1].plot(1000 * wl, db(power(circuit(lattice_netlist(100.0))(wl=wl), "in", "cross")), color="tab:purple",
                  lw=1.6, label="2-stage lattice, 78 / 84 / 70 %")
    ax[1, 1].axhline(-1, color="k", ls=":", lw=0.8)
    ax[1, 1].axhline(-20, color="k", ls=":", lw=0.8)
    ax[1, 1].set(xlabel="wavelength (nm)", ylabel="cross port (dB)", ylim=(-40, 2), xticks=np.arange(1540, 1561, 5),
                 title="(d) flat top: lattice against MZI")
    ax[1, 1].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig("lab04_sax.png", dpi=150)
    print("Saved the figure as lab04_sax.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
