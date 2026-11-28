"""xsec_devices.py -- the layer stacks of the dimensioned cross-sections of Section 24.9, as lists of shapes.

Each shape is a dict: key (its layer), poly (outline, um), n (refractive index at the device's wavelength, or None
for shapes drawn only), col (fill colour) and optional drawing hints. Later shapes are painted over earlier ones.
The stacks are those of Table 24.1, Table 27.1, Worked Example 24.2 and tools/export_stacks.py: generic and
illustrative, not any company's process. Pure Python, so the mode solver (xsec_modes.py, run where SciPy works)
and the drawing (xsec_figs.py) share them.
"""

COL = {
    "ninp": "#C9D6E3", "pinp": "#EBD9BC", "sch": "#C9B6E2", "mqw": "#7A55B0", "qw": "#6B3FA0", "estop": "#B08E5A",
    "cap": "#7A6A55", "sin": "#9FD3C7", "bcb": "#EEE8D6", "metal": "#C98A1C", "fe": "#DCD5EA", "grating": "#A58BC9",
    "si": "#9DB3CC", "ox": "#DCE9F7", "sisub": "#C9D3DF", "bond": "#B9C9DC", "implant": "#E0C4A0", "dbrh": "#D7C6A3",
    "dbrl": "#F3EBD8", "cav": "#E6D7F2", "alox": "#4F9E8C", "alas": "#C8B48A", "gaas": "#D7C6A3", "slab": "#D6E2C4",
    "nlayer": "#C9D6E3",
}

# refractive indices at 1550 nm (InP family, silicon) and 850 nm (GaAs family)
N_INP, N_Q, N_CAP, N_SIN, N_BCB, N_OX, N_SI = 3.167, 3.36, 3.6, 1.98, 1.54, 1.444, 3.476
N_MQW5 = (5 * 10 * 3.55 + 4 * 10 * 3.36) / 90       # 5 x 10 nm wells between 10 nm barriers, averaged over the 90 nm
N_MQW2 = (2 * 8 * 3.55 + 3 * 10 * 3.36) / 46        # 2 x 8 nm wells, three 10 nm barriers (slab-coupled amplifier)
N_SLAB = 3.23                                       # InGaAsP with a 1.0 um band gap
N_GRAT = (N_Q + N_INP) / 2                          # InGaAsP grating teeth half the period: averaged


def rect(key, x0, x1, y0, y1, n, col=None, **kw):
    return dict(key=key, poly=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)], n=n, col=col or COL.get(key, "#DDDDDD"), **kw)


def poly(key, pts, n, col=None, **kw):
    return dict(key=key, poly=[tuple(p) for p in pts], n=n, col=col or COL.get(key, "#DDDDDD"), **kw)


# ---------------------------------------------------------------- ridge laser (Table 24.1; y = 0 at the epi top)
def ridge(RW=2.0, half=8.0, metal=(-3.0, 7.0)):
    s = [rect("ninp", -half, half, -60, -2.12, N_INP),
         rect("sch", -half, half, -2.12, -2.08, N_Q),
         rect("mqw", -half, half, -2.08, -1.99, N_MQW5, wells=(5, 0.010, 0.010)),
         rect("sch", -half, half, -1.99, -1.95, N_Q),
         rect("pinp", -half, half, -1.95, -1.62, N_INP),
         rect("estop", -half, half, -1.62, -1.60, N_Q),
         rect("pinp", -RW / 2, RW / 2, -1.60, -0.15, N_INP),
         rect("cap", -RW / 2, RW / 2, -0.15, 0.0, N_CAP)]
    for sg in (-1, 1):
        x0, x1 = sorted((sg * RW / 2, sg * half)); s.append(rect("sin", x0, x1, -1.60, -1.40, N_SIN))
        w0, w1 = sorted((sg * RW / 2, sg * (RW / 2 + 0.2))); s.append(rect("sin", w0, w1, -1.40, 0.0, N_SIN))
        b0, b1 = sorted((sg * (RW / 2 + 0.2), sg * half)); s.append(rect("bcb", b0, b1, -1.40, 0.0, N_BCB))
    s.append(rect("metal", metal[0], metal[1], 0.0, 0.3, 1.0))
    return s


# ---------------------------------------------------------------- buried-heterostructure DFB laser (y = 0 at the epi top)
def bh(MW=1.5, half=8.0):
    s = [rect("ninp", -half, half, -60, -3.27, N_INP),
         rect("ninp", -MW / 2, MW / 2, -3.27, -2.47, N_INP),                      # mesa, etched 0.8 um into the n-InP
         rect("sch", -MW / 2, MW / 2, -2.47, -2.43, N_Q),
         rect("mqw", -MW / 2, MW / 2, -2.43, -2.34, N_MQW5, wells=(5, 0.010, 0.010)),
         rect("sch", -MW / 2, MW / 2, -2.34, -2.30, N_Q),
         rect("pinp", -MW / 2, MW / 2, -2.30, -2.20, N_INP),
         rect("grating", -MW / 2, MW / 2, -2.20, -2.15, N_GRAT),
         rect("pinp", -MW / 2, MW / 2, -2.15, -2.00, N_INP)]
    for sg in (-1, 1):
        x0, x1 = sorted((sg * MW / 2, sg * half)); s.append(rect("fe", x0, x1, -3.27, -2.00, N_INP))
    s += [rect("pinp", -half, half, -2.00, -0.20, N_INP), rect("cap", -half, half, -0.20, 0.0, N_CAP)]
    for sg in (-1, 1):
        x0, x1 = sorted((sg * 2.0, sg * half)); s.append(rect("sin", x0, x1, 0.0, 0.2, N_SIN))
    s += [rect("metal", -2.0, 2.0, 0.0, 0.2, 1.0), rect("metal", -6.0, 6.0, 0.2, 0.6, 1.0)]
    return s


# ---------------------------------------------------------------- slab-coupled, large-mode amplifier (illustrative)
SCOW = dict(ts=3.0, nw=3, tw=0.008, tb=0.010)        # three wells: with four or more, the well stack guides a mode of its own


def set_scow(ts, nw):
    SCOW.update(ts=ts, nw=nw); _scow_derived()


def _scow_derived():
    global SCOW_STACK, SCOW_WELLS, SCOW_FILL, N_MQWS
    SCOW_WELLS = SCOW["nw"] * SCOW["tw"]; SCOW_STACK = SCOW_WELLS + (SCOW["nw"] + 1) * SCOW["tb"]
    SCOW_FILL = SCOW_WELLS / SCOW_STACK; N_MQWS = (SCOW_WELLS * 3.55 + (SCOW_STACK - SCOW_WELLS) * 3.36) / SCOW_STACK


_scow_derived()


def scow(RW=5.0, half=12.0, etch=1.0):
    """A low-confinement SOA in the spirit of the slab-coupled optical waveguide amplifier: a thick InGaAsP slab
    carries the mode, a few wells sit at its top, and a 5 um ridge etched 1 um into the slab holds it sideways."""
    yq1 = -1.35; yq0 = yq1 - SCOW_STACK; ts = SCOW["ts"]
    s = [rect("ninp", -half, half, -60, yq0 - ts, N_INP),
         rect("slab", -half, half, yq0 - ts, yq0 - etch, N_SLAB),
         rect("slab", -RW / 2, RW / 2, yq0 - etch, yq0, N_SLAB),
         rect("mqw", -RW / 2, RW / 2, yq0, yq1, N_MQWS, wells=(SCOW["nw"], SCOW["tw"], SCOW["tb"])),
         rect("pinp", -RW / 2, RW / 2, yq1, -0.15, N_INP),
         rect("cap", -RW / 2, RW / 2, -0.15, 0.0, N_CAP)]
    yf = yq0 - etch
    for sg in (-1, 1):
        x0, x1 = sorted((sg * RW / 2, sg * half)); s.append(rect("sin", x0, x1, yf, yf + 0.2, N_SIN))
        w0, w1 = sorted((sg * RW / 2, sg * (RW / 2 + 0.2))); s.append(rect("sin", w0, w1, yf + 0.2, 0.0, N_SIN))
        b0, b1 = sorted((sg * (RW / 2 + 0.2), sg * half)); s.append(rect("bcb", b0, b1, yf + 0.2, 0.0, N_BCB))
    s.append(rect("metal", -RW / 2 - 1.0, RW / 2 + 1.0, 0.0, 0.3, 1.0))
    return s


# ---------------------------------------------------------------- III-V on silicon (Table 27.1; y = 0 at the silicon's bottom)
def hetero(wsi=0.5, half=7.0, gain=True):
    TSI, TB = 0.5, 0.03; y0 = TSI + TB
    s = [rect("sisub", -half, half, -40, -2.0, N_SI), rect("ox", -half, half, -2.0, TSI, N_OX),
         rect("si", -wsi / 2, wsi / 2, 0.0, TSI, N_SI), rect("bond", -half, half, TSI, y0, N_OX),
         rect("nlayer", -6.0, 6.0, y0, y0 + 0.11, N_INP),
         rect("mqw", -1.5, 1.5, y0 + 0.11, y0 + 0.41, 3.37),
         rect("pinp", -1.5, 1.5, y0 + 0.41, y0 + 1.91, N_INP)]
    if gain:
        for sg in (-1, 1):
            x0, x1 = sorted((sg * 0.75, sg * 1.5)); s.append(rect("implant", x0, x1, y0 + 0.71, y0 + 1.91, None))
    s.append(rect("cap", -1.5, 1.5, y0 + 1.91, y0 + 2.01, 3.6))
    for sg in (-1, 1):
        w0, w1 = sorted((sg * 1.5, sg * 1.65)); s.append(rect("sin", w0, w1, y0 + 0.11, y0 + 2.01, None))
        f0, f1 = sorted((sg * 1.65, sg * 3.4)); s.append(rect("sin", f0, f1, y0 + 0.11, y0 + 0.26, None))
        if gain:
            m0, m1 = sorted((sg * 3.6, sg * 5.6)); s.append(rect("metal", m0, m1, y0 + 0.11, y0 + 0.61, None))
    if gain:
        s.append(rect("metal", -1.4, 1.4, y0 + 2.01, y0 + 2.41, None))
    return s


# ---------------------------------------------------------------- oxide-aperture VCSEL, 850 nm (y = 0 at the epi top)
VC = dict(lam=0.85, nh=3.52, nl=3.05, nc=3.42, nsub=3.65, ntop=20, nbot=34, n_alas=2.95, n_alox=1.60,
          r_mesa=10.0, r_out=16.0, r_ap=3.0)


def vcsel_layers():
    """(name, thickness, index in the aperture, index under the oxide) from the top (air side) down, as in figsrc/ch2x_lasers.py:
    20 p pairs, low index first seen from the cavity; 30 nm of AlAs (oxidised outside the aperture) in the first low layer;
    a one-wavelength Al0.3GaAs cavity; 34 n pairs and a final low layer; GaAs substrate below."""
    lam, nh, nl = VC["lam"], VC["nh"], VC["nl"]; th, tl = lam / 4 / nh, lam / 4 / nl
    top = []
    for k in range(VC["ntop"]):                       # from the cavity upwards
        if k == 0:
            top += [("dbrl", 0.020, nl, nl), ("alas", 0.030, VC["n_alas"], VC["n_alox"]), ("dbrl", tl - 0.050, nl, nl)]
        else:
            top += [("dbrl", tl, nl, nl)]
        top += [("dbrh", th, nh, nh)]
    bot = []
    for k in range(VC["nbot"]):                       # from the cavity downwards
        bot += [("dbrl", tl, nl, nl), ("dbrh", th, nh, nh)]
    bot += [("dbrl", tl, nl, nl)]
    return list(reversed(top)) + [("cav", lam / VC["nc"], VC["nc"], VC["nc"])] + bot
