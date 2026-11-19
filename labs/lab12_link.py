"""Lab 12: close the reference link budget (Open-Photonics, Chapters 1, 2, 14, 21 and 33).

Run it from a terminal:
    python lab12_link.py              # prints every checkpoint and saves lab12_link.png
    python lab12_link.py --no-plot    # numbers only

It needs NumPy, and Matplotlib for the figure. Powers are in dBm, losses and penalties in dB.
The lab page explains each part: https://www.kithminrw.com/silicon-photonics-lasers-tutorial/labs/lab-12/
"""
import math
import sys

import numpy as np

C = 299792458.0             # speed of light, m/s
Q_E = 1.602176634e-19       # electron charge, C

# The reference link (Chapter 1, Table 1.3)
GRID_THZ = np.array([193.9, 193.5, 193.1, 192.7])   # four slots of the 400 GHz ITU grid
CHANNELS_NM = C / GRID_THZ / 1e3                    # 1546.12, 1549.32, 1552.52, 1555.75 nm
BIT_RATE = 50e9             # per lane, NRZ
N_LANES = 4
FIBRE_KM = 2.0
TARGET_BER = 1e-12
TARGET_MARGIN = 3.0         # dB, after all penalties
TARGET_ENERGY = 5.0         # pJ/bit, whole link


# ---------------------------------------------------------------------------------------------------------
# Part A. The budget, block by block (Chapter 1, Example 1.1; Chapter 33, Table 33.1)
# ---------------------------------------------------------------------------------------------------------
P_LASER = 10.0              # dBm per lane in the transmitter waveguide
FIBRE_DB_PER_KM = 0.2       # standard single-mode fibre in the C band (Chapter 3)


def link_blocks(km=FIBRE_KM, gc=3.0, fibre_db_per_km=FIBRE_DB_PER_KM):
    """Each block's loss in dB for one wavelength, in the order the light meets them (Table 33.1)."""
    return [("ring modulator", 3.0),
            ("other rings, routing", 0.8),
            ("TX grating coupler", gc),
            (f"{km:g} km of fibre", fibre_db_per_km * km),
            ("two connectors", 1.0),
            ("RX grating coupler", gc),
            ("demux ring, routing", 1.5)]


# Allowances of Table 33.1, in dB. The extinction-ratio penalty is not here: it is inside the sensitivity.
PENALTIES = {"crosstalk": 0.5, "dispersion": 0.5, "drift and locking": 1.0, "ageing": 1.0}


def power_levels(p_laser, blocks):
    """Power (dBm) after each block. Losses multiply, so in decibels the budget is a running subtraction."""
    return p_laser - np.cumsum([loss for _, loss in blocks])


def margin(p_rx, sens, penalties):
    """margin = P_launch - sum(losses) - sum(penalties) - P_sens (the key equation of Section 33.2)."""
    return p_rx - sum(penalties.values()) - sens


# ---------------------------------------------------------------------------------------------------------
# Part B. Bit-error ratio, Q and sensitivity (Chapter 21, Section 21.6 and Worked Example 21.2)
# ---------------------------------------------------------------------------------------------------------
RESP = 0.9                  # Ge PIN responsivity, A/W
I_N = 20e-12                # TIA input-referred noise current density, A/sqrt(Hz)
I_DARK = 0.1e-6             # dark current, A (the Chapter 21 demo's value)
ER_DB = 4.0                 # extinction ratio of the ring modulator (Chapter 20)


def ber_from_q(q):
    """NRZ with Gaussian noise: BER = (1/2) erfc(Q / sqrt 2)."""
    return 0.5 * math.erfc(q / math.sqrt(2))


def q_for_ber(ber):
    """The Q that gives a bit-error ratio, by bisection: BER falls steadily as Q rises."""
    lo, hi = 0.0, 20.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ber_from_q(mid) > ber:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def levels(p_dbm, er_db):
    """Powers (W) of the "1" and "0" levels for an average power p_dbm and an extinction ratio r = P1/P0."""
    p = 1e-3 * 10 ** (p_dbm / 10)
    r = 10 ** (er_db / 10)                          # er_db = math.inf gives a perfect "0"
    p0 = 2 * p / (r + 1)
    return 2 * p - p0, p0


def q_factor(p_dbm, er_db=ER_DB, i_n=I_N, bit_rate=BIT_RATE, shot=True):
    """Q = (I1 - I0) / (sigma1 + sigma0) for a PIN receiver: TIA thermal noise plus shot noise of each level.

    The noise bandwidth is 0.7 times the bit rate, 35 GHz at 50 Gb/s (Chapter 21).
    """
    bw = 0.7 * bit_rate
    p1, p0 = levels(p_dbm, er_db)
    i1, i0 = RESP * p1, RESP * p0
    var_th = i_n ** 2 * bw                          # the TIA: the same on both levels
    s1 = math.sqrt(var_th + (2 * Q_E * (i1 + I_DARK) * bw if shot else 0.0))
    s0 = math.sqrt(var_th + (2 * Q_E * (i0 + I_DARK) * bw if shot else 0.0))
    return (i1 - i0) / (s1 + s0)


def sensitivity(target_ber=TARGET_BER, **kw):
    """Lowest average received power (dBm) that meets the target BER, by bisection on q_factor."""
    q_target = q_for_ber(target_ber)
    lo, hi = -40.0, 10.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if q_factor(mid, **kw) < q_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def er_penalty(er_db):
    """Extra average power a finite extinction ratio costs a thermal-noise-limited receiver:
    OMA = 2 P (r - 1)/(r + 1), against 2 P for a perfect "0"."""
    r = 10 ** (er_db / 10)
    return 10 * math.log10((r + 1) / (r - 1))


# ---------------------------------------------------------------------------------------------------------
# Part C. Crosstalk from the ring demultiplexer (Chapter 14, Worked Example 14.1)
# ---------------------------------------------------------------------------------------------------------
SPACING_GHZ = 400.0
FSR_GHZ = 4 * SPACING_GHZ   # cyclic demultiplexer: FSR of four channel spacings (12.8 nm)
REJECTION_DB = 20.0         # adjacent-channel rejection target (Table 1.3)


def fwhm_for_rejection(spacing=SPACING_GHZ, rejection_db=REJECTION_DB):
    """Lorentzian FWHM that rejects a channel `spacing` away by rejection_db: (2 spacing/FWHM)^2 = 10^(rej/10) - 1."""
    return 2 * spacing / math.sqrt(10 ** (rejection_db / 10) - 1)


def drop(df, fwhm, fsr=FSR_GHZ):
    """Drop-port response of a ring (peak 1): a Lorentzian around whichever resonance is nearest.

    df is the detuning in GHz. A ring's resonances repeat every FSR in frequency, so the detuning is
    first folded into -FSR/2 ... +FSR/2.
    """
    d = (np.asarray(df, dtype=float) + fsr / 2) % fsr - fsr / 2
    return 1 / (1 + (2 * d / fwhm) ** 2)


def crosstalk(fwhm, grid_ghz=1e3 * GRID_THZ, fsr=FSR_GHZ):
    """Fraction of the other channels' power that leaks through each drop ring, for the worst ring."""
    return max(sum(float(drop(fj - fi, fwhm, fsr)) for j, fj in enumerate(grid_ghz) if j != i)
               for i, fi in enumerate(grid_ghz))


def crosstalk_penalty(x):
    """Incoherent crosstalk (the beat notes fall far outside the receiver's bandwidth). At the worst pattern,
    the neighbours' "1"s land on our "0"s, closing the eye by the fraction x of its height."""
    return -10 * math.log10(1 - x)


# ---------------------------------------------------------------------------------------------------------
# Part D. Dispersion: a 50 Gb/s NRZ eye through 2 km of fibre (Chapter 2, Worked Example 2.5)
# ---------------------------------------------------------------------------------------------------------
D_FIBRE = 17.0              # ps/(nm km) at 1550 nm
LAM = 1550e-9
SPB = 32                    # samples per bit
F_TX = 0.70 * BIT_RATE      # transmitter (driver + modulator): Gaussian response, 3 dB at 35 GHz
F_RX = 0.75 * BIT_RATE      # receiver: fourth-order Bessel-Thomson, 3 dB at 37.5 GHz (the NRZ reference receiver)


def prbs(order=9):
    """Pseudo-random bit sequence of 2^order - 1 bits (PRBS9: x^9 + x^5 + 1): every pattern of `order` bits
    except all zeros appears once, so every short run of bits that causes intersymbol interference is there."""
    tap = {7: 6, 9: 5, 11: 9}[order]
    reg, out = [1] * order, []
    for _ in range(2 ** order - 1):
        out.append(reg[-1])
        reg = [reg[order - 1] ^ reg[tap - 1]] + reg[:-1]
    return np.array(out)


BITS = prbs(9)


def gaussian_lowpass(f, f3db):
    """Amplitude response with |H|^2 = 1/2 at f3db."""
    return np.exp(-0.5 * math.log(2) * (f / f3db) ** 2)


def bessel4_lowpass(f, f3db):
    """Fourth-order Bessel-Thomson low-pass; 2.1140 is where the normalised filter is 3 dB down."""
    s = 1j * 2.1140 * f / f3db
    return 105 / (s ** 4 + 10 * s ** 3 + 45 * s ** 2 + 105 * s + 105)


def received_waveform(disp_ps_nm, bits=BITS, er_db=ER_DB, f_tx=F_TX, f_rx=F_RX, ring_fwhm=None):
    """Detected signal (average power 1) after a chirp-free modulator, the fibre and the receiver.

    The sequence repeats, so FFTs give the filters and the fibre exactly. The fibre multiplies the field's
    spectrum by exp(-i beta2 L w^2 / 2), with beta2 L = -D L lambda^2 / (2 pi c). ring_fwhm (GHz) adds the
    drop ring, centred on the channel: its field response 1/(1 + 2i f/FWHM) is the Lorentzian of Part C.
    """
    n = len(bits) * SPB
    f = np.fft.fftfreq(n, 1 / (SPB * BIT_RATE))
    drive = np.real(np.fft.ifft(np.fft.fft(np.repeat(bits, SPB).astype(float)) * gaussian_lowpass(f, f_tx)))
    p1, p0 = levels(30.0, er_db)                    # 30 dBm = 1 W: average power 1 (only ratios matter here)
    power = p0 + (p1 - p0) * drive
    field = np.sqrt(np.clip(power, 0, None))        # chirp-free: a real, positive field
    beta2L = -disp_ps_nm * 1e-3 * LAM ** 2 / (2 * np.pi * C)      # ps/nm = 1e-3 s/m; beta2L in s^2
    spectrum = np.fft.fft(field) * np.exp(-0.5j * beta2L * (2 * np.pi * f) ** 2)
    if ring_fwhm:
        spectrum = spectrum / (1 + 2j * f / (ring_fwhm * 1e9))
    field = np.fft.ifft(spectrum)
    detected = np.abs(field) ** 2                   # square-law photodiode
    return np.real(np.fft.ifft(np.fft.fft(detected) * bessel4_lowpass(f, f_rx)))


def eye_opening(wave, bits=BITS, best_sample=False):
    """Vertical eye opening at the best sampling time: the lowest "1" minus the highest "0"."""
    eye = wave.reshape(len(bits), SPB)
    openings = [eye[bits == 1, k].min() - eye[bits == 0, k].max() for k in range(SPB)]
    return (max(openings), int(np.argmax(openings))) if best_sample else max(openings)


def dispersion_penalty(disp_ps_nm, **kw):
    """Eye-closure penalty (dB) against back-to-back with the same transmitter and receiver.

    A thermal-noise-limited receiver needs its eye opening back, so the optical penalty is the ratio of
    openings in dB. Infinity once the eye has closed.
    """
    eo0, eo = eye_opening(received_waveform(0.0, **kw)), eye_opening(received_waveform(disp_ps_nm, **kw))
    return 10 * math.log10(eo0 / eo) if eo > 0 else math.inf


def dispersion_for_penalty(pen_db, lo=0.0, hi=100.0, **kw):
    """Accumulated dispersion (ps/nm) at which the penalty reaches pen_db, by bisection."""
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if dispersion_penalty(mid, **kw) < pen_db:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------------------------------------
# Part E. Energy per bit, and margin traded for laser power (Chapter 33, Section 33.5)
# ---------------------------------------------------------------------------------------------------------
WALL_PLUG = 0.15            # laser wall-plug efficiency
HEATER_MW = 20.0            # per ring, at the worst case (Chapter 18, Worked Example 18.2)
N_RINGS = 8                 # four modulators and four drop rings
E_TIA, E_DRIVER, E_RING = 1.0, 0.5, 0.02            # pJ/bit: typical TIA and driver values; ring (Chapter 20)


def energy_per_bit(p_laser=P_LASER, wall_plug=WALL_PLUG, heater_mw=HEATER_MW):
    """Each term of E_bit = (N P_opt / eta_wp + P_heaters + P_drivers + P_RX) / total bit rate, in pJ/bit."""
    rate = N_LANES * BIT_RATE
    return {"lasers": N_LANES * 1e-3 * 10 ** (p_laser / 10) / wall_plug / rate * 1e12,
            "heaters": N_RINGS * heater_mw * 1e-3 / rate * 1e12,
            "TIAs": E_TIA, "drivers": E_DRIVER, "modulators": E_RING}


def main(plot=True):
    print("Lab 12: close the reference link budget (one wavelength of 4 x 50 Gb/s NRZ over 2 km)\n")

    # ---- Part A
    blocks = link_blocks()
    lv = power_levels(P_LASER, blocks)
    p_rx = lv[-1]
    sens_table = -11.6                               # Table 33.1, from Chapter 21; Part B derives it
    print("A. The budget, block by block (Table 33.1)")
    print(f"   {'laser':<22}{P_LASER:+6.1f} dBm")
    for (name, loss), p in zip(blocks, lv):
        print(f"   {name:<22}{-loss:+6.1f} dB  ->  {p:+5.1f} dBm")
    print(f"   total loss {sum(l for _, l in blocks):.1f} dB, received {p_rx:.1f} dBm = {10 ** (p_rx / 10):.2f} mW"
          "   (Chapter 33: 12.7 dB, -2.7 dBm)")
    print(f"   margin against -12 dBm before penalties = {p_rx + 12:.1f} dB   (Example 1.1: 9.3 dB)")
    print(f"   penalties {' + '.join(f'{v:.1f}' for v in PENALTIES.values())} = {sum(PENALTIES.values()):.1f} dB;"
          f" margin = {margin(p_rx, sens_table, PENALTIES):.1f} dB   (Chapter 33: 3.0 dB and 5.9 dB)")
    print(f"   with the measured -4 dB grating couplers: received {power_levels(P_LASER, link_blocks(gc=4.0))[-1]:.1f} dBm,"
          f" margin {margin(power_levels(P_LASER, link_blocks(gc=4.0))[-1], sens_table, PENALTIES):.1f} dB"
          "   (Chapter 33: 3.9 dB)\n")

    # ---- Part B
    q12 = q_for_ber(TARGET_BER)
    sigma = I_N * math.sqrt(0.7 * BIT_RATE)
    oma = 2 * q12 * sigma / RESP
    r = 10 ** (ER_DB / 10)
    p_avg = oma / (2 * (r - 1) / (r + 1))
    s_th = sensitivity(shot=False)
    s_full = sensitivity()
    print("B. Bit-error ratio and sensitivity (R = 0.9 A/W, 20 pA/sqrt(Hz), noise bandwidth 35 GHz, 4 dB ER)")
    print(f"   Q for BER 1e-12 = {q12:.3f}; for the KP4 threshold 2.4e-4, Q = {q_for_ber(2.4e-4):.2f}"
          "   (Chapter 21: 7.03 and 3.49)")
    print(f"   sigma = {1e6 * sigma:.2f} uA, I1 - I0 = 2 Q sigma = {2e6 * q12 * sigma:.1f} uA, OMA = {1e6 * oma:.1f} uW,"
          f" OMA/average = {2 * (r - 1) / (r + 1):.3f}   (Chapter 21: 3.7 uA, 52 uA, 58 uW, 0.86)")
    print(f"   sensitivity, TIA noise only: {1e6 * p_avg:.1f} uW = {s_th:.2f} dBm   (Chapter 21: 68 uW, -11.7 dBm)")
    print(f"   with shot and dark-current noise:        {s_full:.2f} dBm   (Chapters 21 and 33: -11.6 dBm)")
    print(f"   extinction-ratio penalty at 4 dB: {er_penalty(ER_DB):.2f} dB (inside the sensitivity);"
          f" a perfect '0' gives {sensitivity(er_db=math.inf):.1f} dBm, 15 dB ER {sensitivity(er_db=15.0):.1f} dBm"
          "   (Chapter 21: -15.0 dBm)")
    print(f"   KP4 FEC: {sensitivity(2.4e-4):.1f} dBm; a 10 pA/sqrt(Hz) TIA: {sensitivity(i_n=10e-12):.1f} dBm"
          "   (Chapter 21: -14.7 and -14.5 dBm)")
    print(f"   margin before penalties with this sensitivity: {p_rx - s_full:.1f} dB   (Chapter 21: 8.9 dB)\n")

    # ---- Part C
    fwhm = fwhm_for_rejection()
    ghz_to_nm = 1e9 * LAM ** 2 / C * 1e9              # 1 GHz is 8.0 pm at 1550 nm
    x = crosstalk(fwhm)
    print("C. Crosstalk from Lorentzian drop rings on the 400 GHz grid")
    print(f"   channels: {', '.join(f'{l:.2f}' for l in CHANNELS_NM)} nm   (Table 1.3: 1546.12, 1549.32, 1552.52, 1555.75)")
    print(f"   -20 dB at 400 GHz needs FWHM = {fwhm:.1f} GHz = {fwhm * ghz_to_nm:.2f} nm, loaded Q = {C / LAM / 1e9 / fwhm:.0f};"
          f" FSR {FSR_GHZ:.0f} GHz = {FSR_GHZ * ghz_to_nm:.1f} nm"
          "   (Chapter 14: 0.64 nm, Q about 2400, 12.8 nm)")
    print(f"   leak from the neighbours at 400 GHz: {100 * float(drop(SPACING_GHZ, fwhm)):.2f} % each;"
          f" from the channel 800 GHz away: {100 * float(drop(2 * SPACING_GHZ, fwhm)):.2f} %")
    print(f"   total crosstalk {100 * x:.2f} % ({10 * math.log10(x):.1f} dB): penalty {crosstalk_penalty(x):.2f} dB"
          "   (Chapter 33: about 2 %, roughly 0.1 dB; allowance 0.5 dB)")
    eo_ring = eye_opening(received_waveform(0.0, ring_fwhm=fwhm))
    print(f"   the drop ring also filters its own channel: eye-closure penalty"
          f" {10 * math.log10(eye_opening(received_waveform(0.0)) / eo_ring):.2f} dB   (Chapter 14: 'little filtering penalty')\n")

    # ---- Part D
    disp = D_FIBRE * FIBRE_KM
    pen_d = dispersion_penalty(disp)
    d1, d2 = dispersion_for_penalty(1.0), dispersion_for_penalty(2.0)
    print("D. Dispersion: 50 Gb/s chirp-free NRZ, PRBS 2^9-1, 35 GHz transmitter, 37.5 GHz Bessel-Thomson receiver")
    print(f"   accumulated dispersion {disp:.0f} ps/nm; spread over 0.4 nm = {disp * 0.4:.1f} ps of a {1e12 / BIT_RATE:.0f} ps bit"
          "   (Example 2.5: 34 ps/nm, about 14 ps)")
    print(f"   eye opening back-to-back {eye_opening(received_waveform(0.0)):.3f}, after 2 km"
          f" {eye_opening(received_waveform(disp)):.3f} (OMA = {2 * (r - 1) / (r + 1):.3f}, average 1)")
    print(f"   eye-closure penalty at 34 ps/nm: {pen_d:.2f} dB   (Chapter 33: 'a few tenths of a decibel', allowance 0.5 dB)")
    print(f"   with a perfect extinction ratio: {dispersion_penalty(disp, er_db=math.inf):.2f} dB;"
          f" without the transmitter filter: {dispersion_penalty(disp, f_tx=1e15):.2f} dB")
    print(f"   penalty reaches 1 dB at {d1:.0f} ps/nm and 2 dB at {d2:.0f} ps/nm   (Example 2.5: tolerance 40-60 ps/nm)")
    pen_calc = dict(PENALTIES, crosstalk=round(crosstalk_penalty(x), 2), dispersion=round(pen_d, 2))
    print(f"   margin with this lab's crosstalk and dispersion penalties instead of the allowances:"
          f" {margin(p_rx, s_full, pen_calc):.1f} dB\n")

    # ---- Part E
    e = energy_per_bit()
    etot = sum(e.values())
    m0 = margin(p_rx, sens_table, PENALTIES)
    cut = m0 - TARGET_MARGIN
    e_cut = energy_per_bit(P_LASER - cut)
    print("E. Energy per bit, and margin traded for laser power")
    print(f"   {' + '.join(f'{v:.2f}' for v in e.values())} = {etot:.2f} pJ/bit"
          f" ({', '.join(e)})   (Chapter 33: 1.33 + 0.80 + 1.0 + 0.5 + 0.02 = 3.65)")
    print(f"   one laser: {10 ** (P_LASER / 10):.0f} mW of light draws {10 ** (P_LASER / 10) / WALL_PLUG:.0f} mW;"
          f" laser share {100 * e['lasers'] / etot:.0f} %   (Chapter 1: about 67 mW, 1.3 pJ/bit)")
    print(f"   cut the laser by {cut:.1f} dB to {P_LASER - cut:.1f} dBm: margin {TARGET_MARGIN:.1f} dB,"
          f" saves {etot - sum(e_cut.values()):.2f} pJ/bit, total {sum(e_cut.values()):.2f} pJ/bit"
          "   (Chapter 33: 2.9 dB, 0.65 pJ/bit)")
    print(f"   targets: margin {m0:.1f} >= {TARGET_MARGIN:.0f} dB, energy {etot:.2f} <= {TARGET_ENERGY:.0f} pJ/bit:"
          f" {'the link closes' if m0 >= TARGET_MARGIN and etot <= TARGET_ENERGY else 'the link does not close'}\n")

    if plot:
        make_figure(blocks, lv, sens_table, fwhm, disp)


def make_figure(blocks, lv, sens, fwhm, disp):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(3, 2, figsize=(10, 11))
    pen = sum(PENALTIES.values())
    # (a) power after each block
    names = ["laser"] + [n for n, _ in blocks]
    p = np.concatenate([[P_LASER], lv])
    ax[0, 0].step(range(len(p) + 1), np.append(p, p[-1]), where="post", color="tab:blue", lw=2)
    for i, v in enumerate(p):
        ax[0, 0].text(i + 0.5, v + 0.5, f"{v:.1f}", ha="center", fontsize=8)
    ax[0, 0].axhline(sens, color="tab:red", ls=":", lw=1.2, label=f"sensitivity {sens:.1f} dBm")
    ax[0, 0].axhline(sens + pen, color="tab:red", ls="--", lw=1.2, label=f"+ {pen:.1f} dB penalties")
    ax[0, 0].annotate("", xy=(7.5, sens + pen), xytext=(7.5, p[-1]), arrowprops=dict(arrowstyle="<->", color="tab:green"))
    ax[0, 0].text(7.35, 0.5 * (p[-1] + sens + pen), f"margin\n{p[-1] - pen - sens:.1f} dB", ha="right", va="center",
                  color="tab:green", fontsize=8)
    ax[0, 0].set_xticks(np.arange(len(p)) + 0.5, names, rotation=40, ha="right", fontsize=8)
    ax[0, 0].set(xlim=(0, len(p)), ylim=(-14, 13), ylabel="power (dBm)", title="(a) power after each block, one λ")
    ax[0, 0].legend(fontsize=8, loc="upper right")
    # (b) BER against received power
    ps = np.linspace(-20, 0, 401)
    for kw, col, lab in (({}, "tab:blue", "4 dB ER, 20 pA/√Hz"), ({"er_db": math.inf}, "tab:orange", "perfect ER"),
                         ({"i_n": 10e-12}, "tab:purple", "4 dB ER, 10 pA/√Hz")):
        ax[0, 1].semilogy(ps, [max(ber_from_q(q_factor(x, **kw)), 1e-30) for x in ps], color=col, label=lab)
    ax[0, 1].semilogy(ps + pen, [max(ber_from_q(q_factor(x)), 1e-30) for x in ps], color="tab:blue", ls="--",
                      label=f"4 dB ER + {pen:.1f} dB penalties")
    ax[0, 1].axhline(TARGET_BER, color="grey", ls=":", lw=1)
    ax[0, 1].axhline(2.4e-4, color="grey", ls=":", lw=1)
    ax[0, 1].text(-0.2, 2.4e-4 * 3, "KP4 FEC threshold", fontsize=8, color="grey", ha="right")
    ax[0, 1].text(-0.2, TARGET_BER * 3, "target 10⁻¹²", fontsize=8, color="grey", ha="right")
    ax[0, 1].axvline(lv[-1], color="tab:green", ls="--", lw=1.2)
    ax[0, 1].text(lv[-1] + 0.2, 1e-15, f"received\n{lv[-1]:.1f} dBm", fontsize=8, color="tab:green")
    ax[0, 1].annotate("", xy=(sens + pen, 1e-13), xytext=(lv[-1], 1e-13),
                      arrowprops=dict(arrowstyle="<->", color="tab:green"))
    ax[0, 1].text(0.5 * (sens + pen + lv[-1]), 3e-14, f"margin {lv[-1] - pen - sens:.1f} dB", ha="center", va="top",
                  fontsize=8, color="tab:green")
    ax[0, 1].set(xlabel="average received power (dBm)", ylabel="bit-error ratio", xlim=(-20, 0), ylim=(1e-16, 1),
                 title="(b) BER against received power")
    ax[0, 1].legend(fontsize=8, loc="lower left")
    # (c) drop responses of the four rings
    lam = np.linspace(1543, 1559, 2000)
    f_ghz = C / lam                                 # GHz, with lam in nm
    for i, f0 in enumerate(1e3 * GRID_THZ):
        ax[1, 0].plot(lam, 10 * np.log10(drop(f_ghz - f0, fwhm)), lw=1.3, label=f"{CHANNELS_NM[i]:.2f} nm")
    ax[1, 0].axhline(-REJECTION_DB, color="grey", ls=":", lw=1)
    ax[1, 0].set(xlabel="wavelength (nm)", ylabel="drop transmission (dB)", ylim=(-30, 2),
                 title=f"(c) drop rings, FWHM {fwhm:.0f} GHz, FSR 12.8 nm")
    ax[1, 0].legend(fontsize=7, loc="lower right", ncol=2)
    # (d) eye diagrams, back-to-back and after 2 km
    tb = np.arange(2 * SPB + 1) / SPB
    for d, col, lab in ((0.0, "0.7", "back-to-back"), (disp, "tab:blue", f"after 2 km ({disp:.0f} ps/nm)")):
        wave = received_waveform(d)
        eo, k = eye_opening(wave, best_sample=True)
        eye = np.roll(wave, -k).reshape(-1, SPB)                    # each row starts at its best sampling time
        traces = np.hstack([eye[:-2], eye[1:-1], eye[2:, :1]])      # two bits per trace: sampled at 0, 1 and 2
        ax[1, 1].plot(tb, traces.T, color=col, lw=0.4, alpha=0.4)
        ax[1, 1].plot([], [], color=col, label=f"{lab}: opening {eo:.2f}")
    ax[1, 1].axvline(1.0, color="grey", ls=":", lw=0.8)
    ax[1, 1].set(xlabel="time (bits)", ylabel="detected power (average = 1)", xlim=(0, 2), ylim=(0.4, 1.75),
                 title="(d) the eye, chirp-free NRZ, 4 dB ER")
    ax[1, 1].legend(fontsize=8, loc="upper center", ncol=1)
    # (e) dispersion penalty against accumulated dispersion
    ds = np.linspace(0, 70, 36)
    for kw, col, lab in (({}, "tab:blue", "4 dB ER"), ({"er_db": math.inf}, "tab:orange", "perfect ER")):
        ax[2, 0].plot(ds, [dispersion_penalty(d, **kw) for d in ds], color=col, label=lab)
    ax[2, 0].axvspan(40, 60, color="0.9", label="Example 2.5: 40–60 ps/nm")
    ax[2, 0].axvline(disp, color="tab:green", ls="--", lw=1.2, label="2 km at 1550 nm")
    ax[2, 0].axhline(PENALTIES["dispersion"], color="grey", ls=":", lw=1)
    ax[2, 0].set(xlabel="accumulated dispersion (ps/nm)", ylabel="eye-closure penalty (dB)", ylim=(0, 4),
                 title="(e) dispersion penalty at 50 Gb/s")
    ax[2, 0].legend(fontsize=8, loc="upper left")
    # (f) energy per bit and margin against laser power
    pl = np.linspace(4, 14, 101)
    ax[2, 1].plot(pl, [sum(energy_per_bit(x).values()) for x in pl], color="tab:blue", label="energy per bit")
    ax[2, 1].axhline(TARGET_ENERGY, color="tab:blue", ls=":", lw=1)
    ax[2, 1].set(xlabel="laser power per lane (dBm)", ylabel="energy (pJ/bit)", ylim=(0, 7),
                 title="(f) trading margin for laser power")
    tw = ax[2, 1].twinx()
    mg = pl - sum(l for _, l in blocks) - pen - sens
    tw.plot(pl, mg, color="tab:green", label="margin")
    tw.axhline(TARGET_MARGIN, color="tab:green", ls=":", lw=1)
    tw.set(ylabel="margin (dB)", ylim=(-2, 12))
    p_min = P_LASER - (P_LASER - sum(l for _, l in blocks) - pen - sens - TARGET_MARGIN)   # laser for a 3 dB margin
    ax[2, 1].axvline(p_min, color="grey", ls="--", lw=1)
    ax[2, 1].text(p_min + 0.15, 0.4, f"{p_min:.1f} dBm: 3 dB margin,\n{sum(energy_per_bit(p_min).values()):.2f} pJ/bit",
                  fontsize=8, color="0.3")
    lines = ax[2, 1].get_lines()[:1] + tw.get_lines()[:1]
    ax[2, 1].legend(lines, [l.get_label() for l in lines], fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig("lab12_link.png", dpi=150)
    print("Saved the figure as lab12_link.png")


if __name__ == "__main__":
    main(plot="--no-plot" not in sys.argv)
