"""Bulk semiconductor gain from parabolic bands (Chapter 23): an InGaAsP-like material with a 1550 nm band gap.
k-conserving transitions, Fermi-Dirac occupation with quasi-Fermi levels set by the carrier density (N = P),
one conduction and one valence band, Kane matrix element, Lorentzian intraband broadening.
Run: .venv/bin/python figsrc/ch23_gain.py
"""
import numpy as np
from scipy.constants import hbar, e, m_e, k, c, epsilon_0
from scipy.special import expit

EG0, DEGDT, ME, MV, EP, NR, TAU = 0.80, -3.5e-4, 0.045, 0.46, 25.0, 3.5, 1e-13   # eV, eV/K, m0, m0, eV, -, s
MR = ME * MV / (ME + MV)


def F12(eta):   # Fermi-Dirac integral of order 1/2, normalised so F -> exp(eta) for eta << 0
    x = np.linspace(0, 60, 6001); dx = x[1] - x[0]
    return 2 / np.sqrt(np.pi) * np.sum(np.sqrt(x) * expit(-(x - eta))) * dx


def eta_of(n_cm3, m, T):
    Nc = 2 * (m * m_e * k * T / (2 * np.pi * hbar ** 2)) ** 1.5 / 1e6          # cm^-3
    lo, hi = -30, 80
    for _ in range(80):
        mid = (lo + hi) / 2
        if Nc * F12(mid) < n_cm3: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def gain(N, T=300.0, E=None):
    Eg = EG0 + DEGDT * (T - 300); kT = k * T / e
    ec, ev = eta_of(N, ME, T), eta_of(N, MV, T)
    if E is None: E = np.linspace(Eg - 0.06, Eg + 0.20, 521)
    Mb2 = m_e / 6 * EP * e                                    # |M_b|^2 in kg J
    Ex = np.linspace(Eg, Eg + 0.5, 2001); dE = (Ex[1] - Ex[0]) * e   # transition energies (J grid)
    d = Ex - Eg
    rho = (1 / (2 * np.pi ** 2)) * (2 * MR * m_e / hbar ** 2) ** 1.5 * np.sqrt(d * e)   # 1/(m^3 J)
    fc = expit(-((MR / ME) * d / kT - ec)); fh = expit(-((MR / MV) * d / kT - ev))
    g_unbr = np.pi * e ** 2 * hbar / (NR * c * epsilon_0 * m_e ** 2) * Mb2 * rho * (fc + fh - 1)     # times 1/(hbar omega) below
    gam = hbar / TAU / e                                      # eV, Lorentzian half width
    out = []
    for Ei in E:
        L = (gam / np.pi) / ((Ei - Ex) ** 2 + gam ** 2)        # 1/eV
        out.append(np.sum(g_unbr * L) * (Ex[1] - Ex[0]) / (Ei * e) / 100)   # 1/cm
    return E, np.array(out), Eg + (ec + ev) * kT, Eg


if __name__ == "__main__":
    E, g, dF, Eg = gain(1e10)
    i = np.argmin(abs(E - (Eg + 0.05)))
    print(f"unpumped absorption at Eg + 50 meV: {-g[i]:.0f} /cm")
    peaks = {}
    for N in (1.0e18, 1.5e18, 2.0e18, 3.0e18, 4.0e18, 5.0e18):
        E, g, dF, Eg = gain(N)
        sel = E >= Eg; j = np.where(sel)[0][np.argmax(g[sel])]; peaks[N] = g[j]
        print(f"N = {N:.1e}: peak gain {g[j]:7.0f} /cm at {E[j]:.4f} eV ({1239.84/E[j]:.0f} nm); dF - Eg = {1000*(dF-Eg):.0f} meV")
    # transparency density: peak gain crosses zero
    lo, hi = 3e17, 3e18
    for _ in range(40):
        mid = (lo + hi) / 2
        if gain(mid)[1].max() < 0: lo = mid
        else: hi = mid
    print(f"transparency density (peak gain = 0): {lo:.2e} cm^-3")
    a = (gain(3.1e18)[1].max() - gain(2.9e18)[1].max()) / 0.2e18
    print(f"differential gain at 3e18: {a:.2e} cm^2")
    for T in (300, 340):
        lo, hi = 5e17, 1e19
        for _ in range(40):
            mid = (lo + hi) / 2
            if gain(mid, T)[1].max() < 1000: lo = mid
            else: hi = mid
        print(f"T = {T} K: N for 1000 /cm peak gain = {lo:.2e} cm^-3")
