# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the Open-Photonics authors
"""Lab 9: make the simulated openEBL-style measurement files (Open-Photonics, Chapters 31 and 32).

The files imitate the sweep files an openEBL chip returns (Chapter 32, Section 32.1), with the imperfections
of Chapter 31: the grating couplers' envelope, Fabry-Perot fringes between the couplers, 1 % power noise, a
detector floor and a little wavelength jitter. The devices are those of "your first chip": a loopback, an
unbalanced MZI, three all-pass rings with the gaps of Table 12.1, and a cutback set.

Run it from a terminal:
    python lab09_make_data.py         # writes data/lab09_*.csv next to this script (about 200 kB)

NumPy only. The seed is fixed, so every run writes the same files. Each file's header starts with lines
'# True ...' that give the values used to make it; lab09_analysis.py reads them to check its answers.
The lab page explains everything: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-09/
"""
import pathlib

import numpy as np

SEED = 9
OUT = pathlib.Path(__file__).resolve().parent / "data"

# ---- the "true" chip (Chapters 6, 7, 11, 12 and 15) -------------------------------------------------------
LAM0 = 1550.0                    # nm, reference wavelength
NEFF0 = 2.4459                   # 500 x 220 nm strip at 1550 nm (femwell, Chapter 6)
NG0 = 4.1836                     # its group index at 1550 nm (femwell; "4.18" in the chapters)
DNG = 1.12e-4                    # dn_g/dlambda per nm: the straight line through femwell's 4.157 (1310) and 4.184
LOSS = 2.0                       # propagation loss, dB/cm (Table 12.1)
P_LASER = 0.0                    # laser power, dBm

GC_IL, GC_CENTRE, GC_BW1 = 6.0, 1548.0, 32.0    # one grating coupler: peak loss (dB), centre (nm), 1 dB bandwidth (nm)
GC_SIGMA_DB, GC_SIGMA_NM = 0.25, 0.5            # spread of a structure's coupler pair: loss (dB), centre (nm)
GC_REFL = -18.0                  # amplitude reflection of each coupler back into the chip, dB (R = 1.6 %)
NOISE = 0.01                     # relative power noise, 1 %
FLOOR = -62.0                    # detector floor, dBm
JITTER_PM, OFFSET_PM = 0.1, 3.0  # rms wavelength jitter of each point, and rms offset of each sweep, in pm

BROAD = (1480.0, 1600.0, 0.1)    # broadband sweeps: start, stop, step (nm)
FINE_HALF, FINE_STEP = 0.5, 0.001  # ring sweeps: +-0.5 nm around a resonance in 1 pm steps

RING_R = 10.0                    # ring radius, um
GAPS = (0.20, 0.25, 0.30)        # coupling gaps, um (Table 12.1)
MZI_DL = 100.0                   # MZI arm-length difference, um (Chapter 11's example)
MZI_SPLIT = 0.53                 # power fraction of each Y-branch into the short arm
Y_LOSS = 0.3                     # excess loss of each Y-branch, dB
CUTBACK_CM = (0.25, 0.5, 1.0, 2.0, 4.0)   # waveguide lengths between the couplers
ROUTE_UM = 300.0                 # waveguide between the couplers of the loopback, MZI and rings


def n_eff(lam, dn=0.0):
    """Effective index at lam (nm) whose group index is NG0 + DNG (lam - LAM0).

    n_g = n - lam dn/dlam means d(n/lam)/dlam = -n_g/lam^2; integrating from LAM0 gives this closed form.
    dn shifts the whole curve, as a small width error would (it also adds dn to the group index).
    """
    g0 = NG0 - DNG * LAM0
    return dn + lam * (NEFF0 / LAM0 - g0 * (1 / LAM0 - 1 / lam) - DNG * np.log(lam / LAM0))


def n_group(lam, dn=0.0):
    return NG0 + DNG * (lam - LAM0) + dn


def kappa2(radius, gap, lam=1.55):
    """Power coupling of a ring's point coupler: the Chapter 9 coupler model used by the ring demo (Chapter 12)."""
    dn = 0.0205 * np.exp(-8.75 * (gap - 0.2))
    lx = lam / (2 * dn)
    leff = np.sqrt(2 * np.pi * radius / 8.75)
    return np.sin(min(np.pi / 2, np.pi * leff / (2 * lx))) ** 2


def a_round_trip(length_um, loss=LOSS):
    """Field transmission of one pass, a^2 = exp(-alpha L)."""
    return 10 ** (-loss * length_um * 1e-4 / 20)


def allpass(lam, a, t, length_um, dn):
    phi = 2 * np.pi * n_eff(lam, dn) * length_um * 1e3 / lam
    c = np.cos(phi)
    return (a * a - 2 * a * t * c + t * t) / (1 - 2 * a * t * c + (a * t) ** 2)


def fringes(lam, length_um):
    """Fabry-Perot transmission between the two couplers, normalised to an average of 1."""
    x = 10 ** (2 * GC_REFL / 20) * a_round_trip(length_um) ** 2     # field round trip: R times the round-trip loss
    phi = 4 * np.pi * n_eff(lam) * length_um * 1e3 / lam
    return (1 - x * x) / (1 + x * x - 2 * x * np.cos(phi))


def measure(lam_set, device, fp_um, rng):
    """One sweep: the device between two couplers, with every imperfection. Returns dBm and the random draws."""
    draws = {"coupler-pair loss offset": rng.normal(0, GC_SIGMA_DB), "coupler centre offset": rng.normal(0, GC_SIGMA_NM),
             "sweep wavelength offset": rng.normal(0, OFFSET_PM)}
    lam = lam_set + 1e-3 * (draws["sweep wavelength offset"] + JITTER_PM * rng.standard_normal(lam_set.size))
    d = (lam - GC_CENTRE - draws["coupler centre offset"]) / GC_BW1
    envelope_db = -2 * (GC_IL + 4 * d ** 2) - draws["coupler-pair loss offset"]     # two couplers, 1 dB down at +-BW/2
    signal = 10 ** ((P_LASER + envelope_db) / 10) * fringes(lam, fp_um) * device(lam)
    floor = 10 ** (FLOOR / 10)
    p = signal * (1 + NOISE * rng.standard_normal(lam.size)) + floor * (1 + 0.6 * rng.standard_normal(lam.size))
    return 10 * np.log10(np.maximum(p, floor / 20)), draws


def write(name, device_id, lam, p_dbm, truths, draws):
    lines = ["# SIMULATED DATA, not a measurement: Open-Photonics Lab 9, written by lab09_make_data.py (seed %d)." % SEED,
             "# It imitates an openEBL sweep file. The 'True' lines give the values used to make it."]
    lines += ["# True %s:\t%s" % kv for kv in truths]
    lines += ["# True %s:\t%.3f %s" % (k, v, "pm" if "wavelength" in k else ("nm" if "centre" in k else "dB"))
              for k, v in draws.items()]
    lines += ["# Test:\tLaser Sweep (sweepLaser)", "# User:\tsimulated", "# Device ID:\t %s" % device_id, "# Settings:",
              "#\tLaser power:\t%.1f dBm" % P_LASER, "#\tWavelength step-size:\t%g nm" % (lam[1] - lam[0]).round(6),
              "#\tStart wavelength:\t%g nm" % lam[0], "#\tStop wavelength:\t%g nm" % lam[-1], "wavelength,channel_1"]
    body = "\n".join("%.3f,%.3f" % (x, y) for x, y in zip(lam, p_dbm))
    (OUT / name).write_text("\n".join(lines) + "\n" + body + "\n", encoding="utf-8", newline="\n")
    return (OUT / name).stat().st_size


def main():
    rng = np.random.default_rng(SEED)
    OUT.mkdir(exist_ok=True)
    broad = np.round(np.arange(BROAD[0], BROAD[1] + BROAD[2] / 2, BROAD[2]), 3)
    common = [("propagation loss", "%.2f dB/cm" % LOSS), ("n_g at 1550 nm", "%.4f (slope %.2e per nm)" % (NG0, DNG)),
              ("coupler peak loss", "%.1f dB each at %.1f nm, 1 dB bandwidth %.0f nm" % (GC_IL, GC_CENTRE, GC_BW1)),
              ("coupler reflection", "%.0f dB (amplitude)" % GC_REFL),
              ("noise and floor", "%.0f %% of the power, floor %.0f dBm, jitter %.1f pm rms" % (100 * NOISE, FLOOR, JITTER_PM))]
    sizes = {}

    # loopback: two couplers joined by 300 um of waveguide
    p, dr = measure(broad, lambda l: a_round_trip(ROUTE_UM) ** 2, ROUTE_UM, rng)
    sizes["lab09_loopback.csv"] = write("lab09_loopback.csv", "OpenPhotonics_loopback", broad, p,
                                        common + [("waveguide length", "%.0f um" % ROUTE_UM)], dr)

    # unbalanced MZI of two Y-branches
    def mzi(lam):
        dphi = 2 * np.pi * n_eff(lam) * MZI_DL * 1e3 / lam
        s, arm = MZI_SPLIT, a_round_trip(MZI_DL)
        field2 = s ** 2 + ((1 - s) * arm) ** 2 + 2 * s * (1 - s) * arm * np.cos(dphi)
        return field2 * 10 ** (-2 * Y_LOSS / 10) * a_round_trip(ROUTE_UM) ** 2
    p, dr = measure(broad, mzi, ROUTE_UM, rng)
    fsr = LAM0 ** 2 / (NG0 * MZI_DL * 1e3)
    arm = (1 - MZI_SPLIT) * a_round_trip(MZI_DL)
    er = 20 * np.log10((MZI_SPLIT + arm) / (MZI_SPLIT - arm))
    sizes["lab09_mzi_dL100.csv"] = write("lab09_mzi_dL100.csv", "OpenPhotonics_MZI_dL100", broad, p, common + [
        ("delta L", "%.1f um" % MZI_DL), ("FSR at 1550 nm", "%.4f nm" % fsr),
        ("Y-branch split and loss", "%.2f / %.2f, %.1f dB each (fringe extinction %.1f dB)" % (MZI_SPLIT, 1 - MZI_SPLIT, Y_LOSS, er))], dr)

    # three all-pass rings, each with a small fabrication offset of n_eff
    length = 2 * np.pi * RING_R
    a = a_round_trip(length)
    for gap in GAPS:
        k2 = kappa2(RING_R, gap)
        t = np.sqrt(1 - k2)
        dn = rng.normal(0, 0.002)
        m = np.round(n_eff(LAM0, dn) * length * 1e3 / LAM0)                    # the order nearest 1550 nm
        lam_res = LAM0
        for _ in range(30):                                                     # Newton: n_eff(l) L = m l
            lam_res -= (n_eff(lam_res, dn) * length * 1e3 - m * lam_res) / (-n_group(lam_res, dn) * length * 1e3 / lam_res)
        ng = n_group(lam_res, dn)
        fwhm = (1 - a * t) * lam_res ** 2 / (np.pi * ng * length * 1e3 * np.sqrt(a * t))
        tmin = (a - t) ** 2 / (1 - a * t) ** 2
        centre = np.round(lam_res, 1)
        lam = np.round(np.arange(centre - FINE_HALF, centre + FINE_HALF + FINE_STEP / 2, FINE_STEP), 3)
        p, dr = measure(lam, lambda l, t=t, dn=dn: allpass(l, a, t, length, dn) * a_round_trip(ROUTE_UM) ** 2, ROUTE_UM, rng)
        name = "lab09_ring_r10_g%d.csv" % round(1000 * gap)
        sizes[name] = write(name, "OpenPhotonics_ring_r10_g%d" % round(1000 * gap), lam, p, common + [
            ("ring", "radius %.1f um, gap %.0f nm, all-pass" % (RING_R, 1000 * gap)),
            ("kappa^2", "%.4f %%" % (100 * k2)), ("t", "%.6f" % t), ("a", "%.6f" % a),
            ("regime", "under-coupled (t > a)" if t > a else "over-coupled (t < a)"),
            ("resonance", "%.4f nm (before the sweep offset), n_g there %.4f" % (lam_res, ng)),
            ("FWHM", "%.2f pm" % (1e3 * fwhm)), ("loaded Q", "%.0f" % (lam_res / fwhm)),
            ("extinction", "%.2f dB" % (-10 * np.log10(tmin)))], dr)

    # cutback: straight or spiral waveguides of several lengths between identical couplers
    for L in CUTBACK_CM:
        p, dr = measure(broad, lambda l, L=L: np.full_like(l, a_round_trip(L * 1e4) ** 2), L * 1e4, rng)
        name = "lab09_cutback_%05.0fum.csv" % (L * 1e4)
        sizes[name] = write(name, "OpenPhotonics_cutback_%.0fum" % (L * 1e4), broad, p,
                            common + [("waveguide length", "%.0f um" % (L * 1e4))], dr)

    for k, v in sizes.items():
        print(f"{k:28s} {v / 1024:6.1f} kB")
    print(f"{'total':28s} {sum(sizes.values()) / 1024:6.1f} kB in {OUT}")


if __name__ == "__main__":
    main()
