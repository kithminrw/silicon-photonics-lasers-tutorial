"""Write _data/quizzes.json: three self-check questions per chapter, shown at the end of each chapter by
_includes/quiz.html. Each question is (question, [(answer, correct, why), ...]); every answer carries its own
explanation. Facts come from the chapters' own key takeaways.

Run from the repository root after editing a question:  python3 -I tools/make_quizzes.py
"""
import json
import pathlib

T, F = True, False
Q = {
1: [
 ("Why does optics win over copper for long or fast links?", [
   ("Fibre loss does not grow with frequency, copper loss does", T, "Fibre loses about 0.2 dB/km at 1550 nm at any data rate; copper's loss rises with frequency, so beyond some distance or bandwidth optics pays for its conversion cost."),
   ("Photons are faster than electrons in a wire", F, "Both signals travel at a good fraction of c; the difference is loss and bandwidth, not speed."),
   ("Optical circuits have compact transistors and memory", F, "They do not: photonic circuits are linear and interferometric, with no compact equivalent of the transistor.")]),
 ("In decibels, how do you combine a link's laser power, losses and receiver sensitivity?", [
   ("Multiply them", F, "Multiplication is for linear ratios; in dB the same budget becomes additions and subtractions."),
   ("Subtract the losses from the launch power and compare with the sensitivity", T, "A link budget in dB is a subtraction: launch power minus losses minus penalties, compared with the sensitivity, leaves the margin."),
   ("Average them", F, "Averaging has no meaning here; powers and losses add and subtract in dB.")]),
 ("Which of these does silicon lack?", [
   ("Strong optical confinement", F, "Silicon's high index gives the strongest confinement of the common platforms."),
   ("CMOS-compatible manufacturing", F, "That is silicon's main advantage."),
   ("An efficient laser and the Pockels effect", T, "Silicon's indirect gap gives no efficient laser and its symmetric crystal no Pockels effect; other materials fill these gaps.")]),
],
2: [
 ("What is the group index of a 500 × 220 nm silicon wire at 1550 nm, roughly?", [
   ("About 2.4", F, "That is the effective index; dispersion pushes the group index higher."),
   ("About 4.2", T, "n_g = n − λ dn/dλ is about 4.2 for the wire, well above its effective index of about 2.4."),
   ("3.476, the index of bulk silicon", F, "That is the material index; a guided mode's indices differ.")]),
 ("How far does the evanescent field reach into the oxide beyond a silicon core?", [
   ("About 100 nm", T, "The field decays as e^(−γx) with 1/γ of about 100 nm, which is why couplers, sensors and scattering depend on what is near the core."),
   ("About 10 µm", F, "That is fibre-mode scale; the tail of a high-contrast silicon mode is much shorter."),
   ("Nothing reaches the oxide under total internal reflection", F, "Total internal reflection still leaves an evanescent field on the low-index side.")]),
 ("A loss of α in 1/cm corresponds to how many dB/cm?", [
   ("α", F, "Decibels and natural-log units differ by a factor."),
   ("10 α", F, "The factor is 10 log₁₀ e, not 10."),
   ("4.343 α", T, "α_dB = 10 log₁₀(e) α = 4.343 α.")]),
],
3: [
 ("What sets a Gaussian beam's divergence?", [
   ("Its waist: θ₀ = λ/(π n w₀)", T, "Small waists diverge fast; that is why small chip modes need lenses or tapers to meet a fibre."),
   ("Its power", F, "In linear optics the divergence does not depend on power."),
   ("Only the lens after it", F, "A lens changes the beam, but the divergence of a given beam is set by its waist.")]),
 ("What is the mode-field diameter of standard single-mode fibre at 1550 nm?", [
   ("About 2.5 µm", F, "That is a lensed-fibre or inverse-taper spot."),
   ("About 10.4 µm", T, "SMF-28 has an MFD of about 10.4 µm at 1550 nm and 9.2 µm at 1310 nm."),
   ("About 50 µm", F, "That is the core of multimode fibre.")]),
 ("A waist mismatch of a factor of two between two aligned Gaussian modes costs about:", [
   ("0.2 dB", F, "Too small: the overlap of mismatched waists falls quickly."),
   ("1.9 dB", T, "η = (2w₁w₂/(w₁² + w₂²))² = 0.64, 1.9 dB."),
   ("10 dB", F, "Too large for a factor of two; that would take a far bigger mismatch.")]),
],
4: [
 ("Which platform offers everything, including gain, in one material?", [
   ("Silicon", F, "Silicon has no efficient laser."),
   ("Indium phosphide", T, "InP can guide, modulate, detect and amplify, at the price of higher loss and smaller wafers."),
   ("Silicon nitride", F, "SiN has the lowest loss but no fast modulation, detection or gain.")]),
 ("Why does germanium detect C-band light?", [
   ("Its direct gap of 0.80 eV puts its absorption edge near 1550 nm", T, "λ_g = 1.24/E_g µm: 0.80 eV gives an edge at about 1.55 µm."),
   ("It has a Pockels effect", F, "Detection needs absorption, not the Pockels effect."),
   ("It is transparent at 1550 nm", F, "A detector must absorb.")]),
 ("How do most modern silicon transceivers get their light?", [
   ("From silicon lasers", F, "Silicon does not lase efficiently."),
   ("From attached or bonded III–V lasers", T, "Monolithic, hybrid, heterogeneous and transfer-printed integration bring III–V gain to silicon."),
   ("From the fibre only", F, "Some use external lasers, but most integrate or attach III–V lasers.")]),
],
5: [
 ("When is a symmetric slab waveguide single-mode?", [
   ("For V < π", T, "The first higher mode appears at V = π; 220 nm of silicon in oxide is just below the 245 nm limit at 1550 nm."),
   ("For V < 2.405", F, "2.405 is the single-mode limit of a step-index fibre."),
   ("Always", F, "Thicker films guide more modes.")]),
 ("What is the effective index of the TE0 mode of a 220 nm silicon slab in oxide at 1550 nm?", [
   ("1.44", F, "That is the oxide cladding."),
   ("2.85", T, "The slab solver gives 2.85, with n_g = 3.70 and 81 % of the power in the silicon."),
   ("3.48", F, "That is bulk silicon; a mode's index lies between core and cladding.")]),
 ("In thin silicon films, how do TM modes compare with TE modes?", [
   ("They are less confined", T, "TM's field jumps at the horizontal interfaces and spreads into the cladding, so its index and confinement are lower."),
   ("They are identical", F, "Only in a symmetric square guide could they be degenerate."),
   ("They are more confined", F, "It is the other way round in thin films.")]),
],
6: [
 ("Which index sets a ring's free spectral range?", [
   ("The effective index", F, "The FSR depends on how the phase changes with wavelength, which is the group index."),
   ("The group index", T, "FSR = λ²/(n_g L): use n_g, about 4.18 for a 500 × 220 nm strip."),
   ("The cladding index", F, "The cladding only enters through the mode.")]),
 ("A 1 nm thickness error shifts a silicon ring resonance by about:", [
   ("0.1 nm", F, "Too small: thickness matters more than width."),
   ("0.6 nm", F, "That is the shift per nm of width."),
   ("1.4 nm", T, "About 1.4 nm per nm of thickness and 0.6 nm per nm of width.")]),
 ("When does a 500 × 220 nm-style silicon strip start to guide TE1 at 1550 nm?", [
   ("Near 450 nm width", T, "TE1 appears near 450 nm, so the standard 500 nm strip is close to the multimode limit."),
   ("Near 1 µm", F, "That is far wider than needed."),
   ("Never", F, "Wider strips always guide more modes.")]),
],
7: [
 ("What mostly causes the 1–3 dB/cm loss of silicon strips?", [
   ("Sidewall-roughness scattering", T, "It grows with the index contrast and the field at the sidewall; wider strips and ribs lose less."),
   ("Material absorption of silicon", F, "Undoped silicon is transparent at 1550 nm."),
   ("Bending", F, "Straight strips lose this much too.")]),
 ("Why can silicon nitride carry watts at 1550 nm while silicon saturates?", [
   ("SiN has no two-photon absorption there", T, "Silicon absorbs two photons together at 1550 nm and the free carriers this creates absorb more; SiN's wide gap avoids both."),
   ("SiN has a larger Kerr coefficient", F, "Silicon's is larger; the problem is absorption."),
   ("SiN guides less light", F, "Weaker confinement helps a little, but the key is the absence of TPA.")]),
 ("What does periodic poling do in thin-film lithium niobate?", [
   ("Flips the nonlinearity every coherence length, so the second harmonic keeps growing", T, "Quasi-phase-matching: with periods of about 4 µm in thin-film LN, the power grows at (2/π)² of the ideal."),
   ("Removes the material's loss", F, "Poling changes the sign of the nonlinear coefficient, not the loss."),
   ("Makes it centrosymmetric", F, "It is the lack of symmetry that gives χ⁽²⁾ in the first place.")]),
],
8: [
 ("Why does an Euler bend lose less than a circular one?", [
   ("It ramps the curvature, avoiding the mode mismatch at the junctions", T, "A circular bend's sudden curvature change makes a mismatch loss at each straight–bend junction."),
   ("It is shorter", F, "It is usually longer; the gain is at the junctions."),
   ("It uses a different material", F, "The shape, not the material, makes the difference.")]),
 ("When is a taper adiabatic?", [
   ("When its width changes slowly compared with the local beat length to the nearest coupled mode", T, "Then the mode follows the geometry without coupling power into other modes."),
   ("When it is made of oxide", F, "Adiabaticity is about rate of change, not material."),
   ("Whenever it is longer than 1 µm", F, "The required length depends on the modes involved.")]),
 ("Roughly what bend radius suits a silicon TE strip?", [
   ("A few micrometres", T, "Silicon TE strips are fine above about 2–3 µm; TM, ribs and SiN need much more."),
   ("Several millimetres", F, "That is weakly confining SiN."),
   ("100 nm", F, "Far too tight: the mode would radiate.")]),
],
9: [
 ("What is the cross-over length of two 500 × 220 nm strips 200 nm apart?", [
   ("3.8 µm", F, "Ten times too short."),
   ("37.8 µm", T, "L_x = λ/(2Δn) = 37.8 µm at 200 nm gap, growing 2.4× per 100 nm of gap."),
   ("378 µm", F, "Ten times too long for this gap.")]),
 ("What does complete power transfer in a directional coupler require?", [
   ("Phase matching between the two guides", T, "Without equal propagation constants, only part of the power crosses over."),
   ("A gap below 50 nm", F, "Any gap works if the length matches; small gaps only shorten it."),
   ("Two different materials", F, "Identical guides are the usual choice.")]),
 ("Why is the cross-coupling term of a lossless coupler −j?", [
   ("Energy conservation requires the matrix to be unitary", T, "A 90° phase between bar and cross outputs keeps the total power constant."),
   ("It is a convention with no physical meaning", F, "It has consequences, for example in MZI interference."),
   ("Loss in the coupler", F, "It holds for a lossless coupler.")]),
],
10: [
 ("Fed from one arm, a Y-branch combiner passes:", [
   ("All the power", F, "Half goes into an odd mode that radiates."),
   ("Half the power", T, "By symmetry, light from one arm excites even and odd modes equally; only the even one is guided out."),
   ("None", F, "The even half still passes.")]),
 ("What is the beat length L_π of a 6 µm silicon MMI (TE)?", [
   ("About 9 µm", F, "Ten times too short."),
   ("About 90 µm", T, "L_π ≈ 4n_r W_e²/(3λ) gives 90 µm; a 1 × 2 splitter is then 34 µm long."),
   ("About 900 µm", F, "Ten times too long.")]),
 ("A centred input to an MMI excites:", [
   ("Only even modes", T, "Symmetry forbids odd modes, which gives the short symmetric-interference images."),
   ("Only odd modes", F, "A symmetric input cannot excite antisymmetric modes."),
   ("All modes equally", F, "Overlap integrals vanish for the odd modes.")]),
],
11: [
 ("The FSR of an unbalanced MZI with ΔL = 100 µm in a silicon strip at 1550 nm is about:", [
   ("5.75 nm", T, "λ²/(n_g ΔL) with n_g ≈ 4.18 gives 5.75 nm."),
   ("57.5 nm", F, "Ten times too large."),
   ("0.58 nm", F, "Ten times too small.")]),
 ("What limits an MZI's extinction?", [
   ("Unequal couplers or arm losses", T, "A 55/45 coupler caps the extinction near 26 dB."),
   ("The arm length", F, "Length sets the FSR, not the extinction."),
   ("The wavelength", F, "Only through the couplers' wavelength dependence.")]),
 ("How can an unbalanced MZI measure the group index on a chip?", [
   ("n_g = λ²/(FSR · ΔL)", T, "Measure the FSR, know ΔL, and solve for n_g."),
   ("From the extinction ratio", F, "Extinction tells about coupler balance, not n_g."),
   ("From the insertion loss", F, "Loss does not reveal the group index.")]),
],
12: [
 ("What is the FSR of a 10 µm-radius silicon ring at 1550 nm?", [
   ("About 9.15 nm", T, "FSR = λ²/(n_g L) with L = 2π × 10 µm gives about 9.15 nm."),
   ("About 0.9 nm", F, "Ten times too small."),
   ("About 91 nm", F, "That is the Vernier FSR of two rings.")]),
 ("At critical coupling (t = a), the all-pass ring:", [
   ("Has a full null on resonance", T, "The coupled-in loss exactly matches the ring's round-trip loss, and the through port goes to zero."),
   ("Transmits everything", F, "That is far from resonance."),
   ("Has its highest loaded Q", F, "Q_L = Q_i/2 at critical coupling; under-coupled rings have higher Q_L.")]),
 ("Why can one through-port spectrum not tell under- from over-coupling?", [
   ("The formula is symmetric in a and t", T, "Swapping loss and coupling gives the same spectrum; use several gaps or an add-drop ring."),
   ("The spectrum has noise", F, "Even noiseless data has the ambiguity."),
   ("Rings have no resonances", F, "They do; the ambiguity is in the fit.")]),
],
13: [
 ("What period gives a first-order Bragg grating at 1550 nm in a 500 × 220 nm silicon strip?", [
   ("316.8 nm", T, "Λ = λ/(2 n_eff) with n_eff = 2.446."),
   ("633.6 nm", F, "That would be second order."),
   ("1550 nm", F, "Bragg reflection needs Λ = λ/(2n_eff).")]),
 ("A lossless Fabry–Pérot cavity with two 99 % mirrors, on resonance, transmits:", [
   ("1 %", F, "That is one mirror; the round trips build up the light inside."),
   ("All of it", T, "(1 − R)²/(1 − R)² = 1: equal lossless mirrors transmit everything on resonance."),
   ("0.01 %", F, "Multiplying the two mirrors ignores the in-phase round trips.")]),
 ("With loss inside, what does setting R₁ = R₂e^(−2αL) achieve?", [
   ("100 % transmission", F, "Loss still absorbs part of the light."),
   ("No reflection on resonance", T, "The front mirror leaks as fast as everything behind it loses; the rest is transmitted or absorbed."),
   ("A wider FSR", F, "The FSR depends on length and group index.")]),
],
14: [
 ("What sets the DWDM channel grid?", [
   ("The ITU frequency grid (for example 100 or 400 GHz spacing)", T, "DWDM channels sit on the ITU grid; CWDM uses 20 nm spacing."),
   ("The laser's linewidth", F, "Linewidth must be far below the spacing, but it does not set it."),
   ("The fibre's mode size", F, "Unrelated to channel spacing.")]),
 ("Why does every ring demultiplexer need heaters and locking?", [
   ("Rings drift with temperature and fabrication", T, "About 75 pm/K plus nanometres of fabrication offset: they must be tuned and kept on their channels."),
   ("Heaters improve the Q", F, "Heaters tune the wavelength, not the Q."),
   ("To amplify the light", F, "Heaters do not amplify.")]),
 ("In mode-division multiplexing, what does an asymmetric directional coupler phase-match?", [
   ("TE0 of a narrow guide to TE1 of a wide bus", T, "A 0.45 µm strip's TE0 matches TE1 of a 0.93 µm bus; the bus's own TE0 passes untouched."),
   ("TE to TM", F, "That is a polarisation rotator."),
   ("Two different wavelengths", F, "Mode multiplexing works at the same wavelength.")]),
],
15: [
 ("Why are fibres tilted by 8–12° over grating couplers?", [
   ("To avoid the strong second-order Bragg reflection of vertical coupling", T, "At normal incidence the grating also reflects back into the waveguide."),
   ("To fit the fibre array", F, "Arrays can be made at any angle; the reason is optical."),
   ("To increase bandwidth", F, "Tilt does not mainly serve bandwidth.")]),
 ("A grating coupler's efficiency is the product of:", [
   ("Directionality and mode overlap", T, "How much light goes up, times how well its profile matches the fibre mode."),
   ("Period and angle", F, "Those set phase matching, not efficiency directly."),
   ("Length and width", F, "They enter through directionality and overlap.")]),
 ("What limits a grating coupler's 1 dB bandwidth to 30–40 nm?", [
   ("The fibre's angular acceptance against the grating's angular dispersion", T, "The beam angle changes with wavelength, and the fibre only accepts a narrow range of angles."),
   ("Silicon absorption", F, "Silicon is transparent across the band."),
   ("The laser", F, "Bandwidth is a property of the coupler.")]),
],
16: [
 ("Butt-coupling a 500 × 220 nm strip straight to SMF-28 loses about:", [
   ("1 dB", F, "Far too optimistic: the modes differ greatly in size."),
   ("20 dB", T, "The mode must be expanded first, by an inverse taper or a spot-size converter."),
   ("100 dB", F, "Overlap losses are large, but not this large.")]),
 ("How does an inverse taper expand the mode?", [
   ("By narrowing the silicon tip so the mode spreads into the cladding", T, "A 180 nm tip gives a 2.9 µm spot, 140 nm about 10 µm (TE)."),
   ("By widening the silicon", F, "A wider strip confines more, not less."),
   ("By adding a lens", F, "The taper alone does it; lenses are an extra option.")]),
 ("What advantage does edge coupling have over grating coupling?", [
   ("Over 100 nm bandwidth and both polarisations", T, "Grating couplers instead offer wafer-scale testing and relaxed alignment."),
   ("Wafer-scale testing before dicing", F, "That is the grating coupler's advantage."),
   ("Larger alignment tolerance", F, "Small edge spots need tighter alignment.")]),
],
17: [
 ("What is the 1 dB lateral tolerance of a lensed fibre on an inverse taper (2.5 µm spots)?", [
   ("±0.6 µm", T, "d = √(0.115 (w₁² + w₂²)): about ±0.6 µm, four times tighter than a grating coupler."),
   ("±6 µm", F, "That is a pair of printed lenses with a 25 µm beam."),
   ("±25 µm", F, "Far beyond any single-mode interface.")]),
 ("Facet-attached microlenses expand the beam to about 25 µm. What becomes harder?", [
   ("Lateral alignment", F, "It becomes ten times easier, about ±6 µm."),
   ("Holding the angle", T, "A wide beam has a narrow far field: about ±1° of tilt for 1 dB."),
   ("The gap", F, "Hundreds of micrometres of gap cost almost nothing.")]),
 ("How is the alignment of a whole fibre array found quickly?", [
   ("Align a loopback between the outer fibres", T, "When the loopback peaks, the rigid array is aligned for every channel."),
   ("Align each fibre separately", F, "The fibres are fixed in the array; aligning one pair aligns all."),
   ("Use the largest fibre", F, "All fibres are the same.")]),
],
18: [
 ("How fast does a silicon ring drift with temperature?", [
   ("About 75 pm/K", T, "dn_eff/dT ≈ 2.0 × 10⁻⁴ /K for a 500 × 220 nm strip gives about 75 pm/K."),
   ("About 7.5 nm/K", F, "A hundred times too much."),
   ("It does not drift", F, "Silicon's thermo-optic coefficient is large.")]),
 ("Does P_π of a thermo-optic phase shifter depend on its length?", [
   ("No: longer heaters spread the same total power", T, "P_π = λG'/(2 dn_eff/dT), with G' the thermal conductance per length."),
   ("Yes: twice the length halves P_π", F, "That is true of electro-optic V_π, not thermal P_π."),
   ("Yes: twice the length doubles P_π", F, "Length cancels out.")]),
 ("What do trenches and undercuts trade?", [
   ("Lower power for slower response", T, "Isolation lowers P_π (to 4.5 mW with an undercut) but slows the response (to 180 µs)."),
   ("Lower loss for higher power", F, "They concern thermal isolation, not optical loss."),
   ("Nothing: they only help", F, "Speed is the price.")]),
],
19: [
 ("In silicon, which carriers change the index more per unit of loss?", [
   ("Holes", T, "At 10¹⁸ cm⁻³, holes change the index three times more per unit loss than electrons."),
   ("Electrons", F, "It is the other way round."),
   ("Both equally", F, "They differ by about three.")]),
 ("What V_πL does a lateral PN junction at 5 × 10¹⁷ cm⁻³ give in a silicon rib?", [
   ("About 1.4 V·cm", T, "With about 13 dB/cm of loss; doping trades efficiency against loss and capacitance."),
   ("About 0.01 V·cm", F, "Far beyond silicon's plasma effect."),
   ("About 100 V·cm", F, "Far worse than real devices.")]),
 ("What makes thin-film lithium niobate attractive for modulators?", [
   ("The Pockels effect: about 2.6 V·cm push–pull, low loss, > 100 GHz", T, "A pure field effect, with no free-carrier loss and very fast."),
   ("Two-photon absorption", F, "That is a loss mechanism."),
   ("It lases", F, "LN does not provide gain here.")]),
],
20: [
 ("What is OMA in terms of average power and extinction ratio?", [
   ("2P_avg(ER − 1)/(ER + 1)", T, "The optical modulation amplitude is the difference between the one and zero levels."),
   ("P_avg × ER", F, "That overstates it."),
   ("P_avg/ER", F, "That is not the modulation amplitude.")]),
 ("What does a ring modulator's Q trade?", [
   ("Extinction against bandwidth (c/λQ)", T, "High Q gives steep slopes and extinction but limits the photon-lifetime bandwidth."),
   ("Size against colour", F, "Not a meaningful trade."),
   ("Nothing: higher Q is always better", F, "Too high a Q limits speed.")]),
 ("PAM4 instead of NRZ at the same bit rate:", [
   ("Halves the symbol rate, for a penalty of about 4.8 dB in eye amplitude", T, "Each eye is a third of the swing; the penalty is the price of half the bandwidth."),
   ("Doubles the symbol rate", F, "It halves it."),
   ("Has no penalty", F, "Smaller eyes cost decibels.")]),
],
21: [
 ("What is the maximum responsivity at 1550 nm?", [
   ("About 1.25 A/W", T, "R = η λ[µm]/1.24 with η = 1."),
   ("1 W/A", F, "Wrong units and value."),
   ("12.5 A/W", F, "Without internal gain, at most 1.25 A/W.")]),
 ("What Q factor gives a BER of 10⁻¹²?", [
   ("7.03", T, "BER = ½ erfc(Q/√2); Q = 3.49 gives the KP4 FEC threshold."),
   ("3.0", F, "Far too low."),
   ("20", F, "Far beyond what is needed.")]),
 ("What dominates the noise of short-reach receivers?", [
   ("The TIA's thermal noise", T, "Shot noise is small at these powers; the front end's thermal noise dominates."),
   ("Laser phase noise", F, "Intensity detection ignores phase."),
   ("Fibre loss", F, "Loss lowers signal; it is not a noise source.")]),
],
22: [
 ("Why can a two-level system never invert?", [
   ("Absorption and stimulated emission have equal coefficients, so pumping at most equalises the populations", T, "B₁₂ = B₂₁; three- and four-level systems are needed."),
   ("Spontaneous emission is too slow", F, "The problem is the symmetry of B coefficients."),
   ("It has no photons", F, "Not the reason.")]),
 ("Why does silicon emit light poorly?", [
   ("Its band gap is indirect: B ≈ 10⁻¹⁴ against 10⁻¹⁰ cm³/s for InGaAsP", T, "Radiative recombination needs a phonon, so it is very slow."),
   ("It is too transparent", F, "Transparency at 1550 nm is unrelated to emission at its gap."),
   ("It conducts heat too well", F, "Not the reason.")]),
 ("What does gain saturation look like?", [
   ("γ₀/(1 + I/I_sat)", T, "Strong signals use up the inversion and the gain falls."),
   ("Gain grows without limit with intensity", F, "It must saturate."),
   ("Gain is constant", F, "Only for small signals.")]),
],
23: [
 ("What is the condition for gain in a semiconductor?", [
   ("E_g < hν < E_Fc − E_Fv", T, "The quasi-Fermi-level separation must exceed the photon energy (Bernard–Duraffourg)."),
   ("hν < E_g", F, "Below the gap there is no interband transition."),
   ("Any injected current", F, "Only above transparency.")]),
 ("What counts as the modal gain of a waveguide laser?", [
   ("Γg: the material gain times the mode's overlap with the active region", T, "Only the part of the mode in the active layer sees gain."),
   ("The material gain", F, "The mode only partly overlaps the gain."),
   ("The cladding gain", F, "Claddings have no gain.")]),
 ("What do quantum dots add over quantum wells?", [
   ("Temperature stability and tolerance to defects", T, "Which is why they suit growth on silicon."),
   ("A direct gap in silicon", F, "Dots are III–V."),
   ("Higher loss", F, "Not their advantage.")]),
],
24: [
 ("What is the threshold condition of a Fabry–Pérot laser?", [
   ("Γg_th = α_i + ln(1/R₁R₂)/(2L)", T, "Gain equals internal plus mirror loss; above threshold gain and carriers clamp."),
   ("Γg_th = 0", F, "That is transparency, not threshold."),
   ("Γg_th = α_i only", F, "Mirror loss must be paid too.")]),
 ("What threshold and slope does the 400 µm example laser have?", [
   ("19 mA and 0.21 W/A per facet", T, "From the rate equations and the example's parameters."),
   ("1.9 mA and 2.1 W/A", F, "Off by ten in both."),
   ("190 mA and 0.021 W/A", F, "Off by ten in both.")]),
 ("How does a buried-heterostructure laser differ from a ridge laser?", [
   ("Its mesa is etched through the wells and buried again in regrown InP", T, "No exposed surface, current only through the mesa, strong guiding."),
   ("It has no quantum wells", F, "It has wells, buried in InP."),
   ("Its ridge stops above the wells", F, "That describes the ridge laser.")]),
],
25: [
 ("How does a laser's relaxation frequency grow with current?", [
   ("As √(I − I_th)", T, "So bandwidth rises with bias until damping caps it."),
   ("Linearly with I", F, "It grows as a square root."),
   ("It does not change", F, "It grows with the photon density.")]),
 ("How does the α-factor change the linewidth?", [
   ("It broadens it by 1 + α²", T, "Gain changes drag the index, adding phase noise."),
   ("It narrows it by α", F, "It broadens."),
   ("It has no effect", F, "It matters greatly.")]),
 ("Above about what feedback level can a laser become unstable?", [
   ("About −40 dB", T, "Coherence collapse can begin at −40 to −30 dB for typical lasers."),
   ("About −100 dB", F, "Far below the danger zone."),
   ("Only above 0 dB", F, "Much weaker feedback is enough.")]),
],
26: [
 ("What side-mode suppression do single-frequency lasers typically need?", [
   ("35 dB or more", T, "Enough that the other modes do not matter over fibre."),
   ("3 dB", F, "Far too little."),
   ("100 dB", F, "More than required.")]),
 ("How do λ/4-shifted DFB lasers tune?", [
   ("Only with temperature, about 0.1 nm/K", T, "They are the telecom workhorse but tune slowly and narrowly."),
   ("Over 100 nm by current", F, "That needs Vernier or external cavities."),
   ("They cannot tune at all", F, "Temperature tunes them a little.")]),
 ("What Vernier FSR do 10 and 11 µm silicon rings give?", [
   ("About 91 nm", T, "FSR₁FSR₂/|ΔFSR|, with a tuning gearing of 11."),
   ("About 9 nm", F, "That is one ring's FSR."),
   ("About 1 nm", F, "Far too small.")]),
],
27: [
 ("Why is self-heating worse for lasers on SOI?", [
   ("The buried oxide insulates them thermally", T, "Higher thermal impedance raises the temperature; thermal shunts help."),
   ("Silicon absorbs the light", F, "The issue is heat flow, not absorption."),
   ("SOI lasers draw no current", F, "They are electrically pumped like others.")]),
 ("In a heterogeneous laser, what moves the light from the III–V into the silicon?", [
   ("Widening the silicon along an adiabatic taper", T, "The supermode follows from the MQW region into the silicon past the crossing near 0.85 µm."),
   ("A mirror", F, "The transfer is by supermode evolution."),
   ("A grating coupler", F, "That couples to fibre.")]),
 ("Why can't a passive silicon circuit act as an isolator?", [
   ("Lorentz reciprocity: linear, unbiased structures transmit equally both ways", T, "Isolation needs a magnetic bias, time modulation or nonlinearity."),
   ("Silicon has too much loss", F, "Loss does not break reciprocity."),
   ("Rings are too large", F, "Size is irrelevant.")]),
],
28: [
 ("What turns a laser chip into an SOA?", [
   ("AR coatings and an angled waveguide that remove the feedback", T, "Light passes once and is amplified, below the lasing threshold."),
   ("A higher current", F, "Current alone would make it lase."),
   ("Removing the wells", F, "The wells provide the gain.")]),
 ("What is the lowest possible noise figure of an amplifier?", [
   ("3 dB", T, "The quantum limit of a high-gain amplifier; input coupling loss adds to it."),
   ("0 dB", F, "Amplifiers always add noise."),
   ("10 dB", F, "Real SOAs can be better.")]),
 ("How small must an SOA's facet reflections be?", [
   ("Below about 10⁻⁴", T, "Otherwise the gain ripples: 1.7 dB of ripple at 10⁻³ with 20 dB gain."),
   ("Below about 10 %", F, "Far too reflective."),
   ("Reflections do not matter", F, "They turn the SOA into a weak laser cavity.")]),
],
29: [
 ("How should independent variations be combined in a design margin?", [
   ("Not as stacked worst cases: use the spread", T, "Stacking worst cases of independent variables is pessimistic; centre the design and use statistics."),
   ("Always add all worst cases", F, "That over-designs."),
   ("Ignore them", F, "Margin must account for the spread.")]),
 ("What error does a Monte Carlo yield estimate carry?", [
   ("√(Y(1 − Y)/N)", T, "Binomial statistics: more samples, smaller error."),
   ("Y/N", F, "Not the standard error."),
   ("None", F, "Every finite sample has an error.")]),
 ("Which model should you use first?", [
   ("The cheapest that answers the question", T, "Formulas and mode solvers first; one final 3D FDTD check."),
   ("Always full 3D FDTD", F, "Too slow for design sweeps."),
   ("No model", F, "Design needs models.")]),
],
30: [
 ("What does a PDK contain?", [
   ("Layers, validated cells, compact models, rules and the layer stack", T, "Open PDKs make public designs possible."),
   ("Only a GDS template", F, "Much more than that."),
   ("Only simulation software", F, "It is foundry data, not a simulator.")]),
 ("What does gdsfactory add to layout?", [
   ("Layout as code, versioned and rerunnable", T, "Designs can be swept, tested and regenerated."),
   ("Fabrication", F, "It is a design tool."),
   ("Measurement", F, "Testing is separate.")]),
 ("How are circuits simulated?", [
   ("From S-matrix compact models and a netlist", T, "SAX and SiEPIC-Tools work this way."),
   ("Always with 3D FDTD of the whole chip", F, "Far too expensive."),
   ("They cannot be simulated", F, "Circuit simulation is routine.")]),
],
31: [
 ("When is 3D FDTD stable?", [
   ("For a Courant number S ≤ 1/√3", T, "The time step must be short enough for the grid."),
   ("Always", F, "Too large a time step diverges."),
   ("Only in 2D", F, "3D has its own limit.")]),
 ("How does 3D FDTD cost grow as the grid is refined?", [
   ("Memory ∝ Δx⁻³, time ∝ Δx⁻⁴", T, "More cells and smaller time steps."),
   ("Linearly", F, "Far faster than linear."),
   ("It does not change", F, "Finer grids cost more.")]),
 ("What is EME good at?", [
   ("Long devices, since length costs almost nothing", T, "Each uniform section is exact; it struggles with radiation."),
   ("Broadband transients", F, "That is FDTD's strength."),
   ("Nothing", F, "It is very useful for tapers and MMIs.")]),
],
32: [
 ("What should you do before sweeping a design in any tool?", [
   ("Converge the simulation", T, "Check grid and settings; differences between tools are usually set-up differences."),
   ("Sweep first, check later", F, "Unconverged sweeps mislead."),
   ("Nothing", F, "Convergence is the first habit.")]),
 ("Which open tools cover mode solving and FDTD?", [
   ("MEEP, MPB and femwell", T, "With SAX for circuits and gdsfactory as glue."),
   ("Only commercial tools", F, "Open tools cover much of the work."),
   ("Spreadsheets", F, "Not for field solvers.")]),
 ("Two tools built on the same method disagree. Most likely:", [
   ("Their set-ups differ", T, "Grids, materials, sources and monitors must match."),
   ("Physics is broken", F, "The method is the same."),
   ("One tool is always right", F, "Check the set-up first.")]),
],
33: [
 ("What are GDSII coordinates?", [
   ("32-bit integers in database units, usually 1 nm", T, "Hence a ±2.15 m range at 1 nm."),
   ("Floating-point micrometres", F, "GDSII stores integers."),
   ("Pixels", F, "It is a vector format.")]),
 ("Why use hierarchy in a layout?", [
   ("It keeps files small: 10 000 rings take 4 kB as an array, 37.7 MB flat", T, "Cells are defined once and placed many times."),
   ("It improves fabrication", F, "The mask is the same."),
   ("It is required by GDSII", F, "Flat layouts are legal, just large.")]),
 ("How does GDSII store a ring, which has a hole?", [
   ("As a polygon with a cut line", T, "GDSII has no holes."),
   ("As a circle primitive", F, "GDSII has no circles."),
   ("It cannot", F, "The cut line handles it.")]),
],
34: [
 ("Which check catches a component moved 50 nm off its waveguide?", [
   ("Connectivity and LVS, not DRC", T, "Every width and space rule can still pass."),
   ("DRC", F, "Shapes may all be legal."),
   ("None", F, "Connectivity checks catch it.")]),
 ("How should false DRC errors on curves be handled?", [
   ("With tolerances, angle limits, on-grid drawing and written waivers", T, "Never by blanket suppression."),
   ("By disabling DRC", F, "Real errors would then pass."),
   ("By ignoring all markers", F, "Count mistakes, not markers.")]),
 ("In the chapter's test, how many real mistakes made the 373 markers?", [
   ("9", T, "Most markers came from a few mistakes, an intended grating and a snapped coupler."),
   ("373", F, "Markers are not mistakes."),
   ("0", F, "There were real mistakes.")]),
],
35: [
 ("How are SOI wafers made?", [
   ("By Smart Cut", T, "Hydrogen implantation, bonding and splitting."),
   ("By growing silicon on glass", F, "Not the standard process."),
   ("By oxidising silicon fully", F, "That leaves no film.")]),
 ("Why is tuning mandatory for silicon rings?", [
   ("Wafer-scale variation spreads resonances by several nanometres", T, "About 0.6 nm per nm of width and 1.4 nm per nm of thickness."),
   ("Rings have no resonances without heaters", F, "They resonate; just at the wrong wavelength."),
   ("Tuning reduces loss", F, "It shifts wavelength.")]),
 ("What does electron-beam lithography offer over DUV?", [
   ("Resolution and flexibility for prototypes", T, "DUV gives throughput and repeatability."),
   ("Higher throughput", F, "EBL is slow."),
   ("Lower resolution", F, "It resolves finer features.")]),
],
36: [
 ("How are grating couplers de-embedded from a measurement?", [
   ("With a loopback or a fitted envelope", T, "Relative quantities are more robust than absolute losses."),
   ("They cannot be", F, "Loopbacks remove them."),
   ("By ignoring them", F, "They dominate the raw spectrum.")]),
 ("What does testing edge couplers with a lensed fibre array demand?", [
   ("About ±0.6 µm on every channel at once", T, "Printed lenses on chip and fibres widen that to about ±6 µm."),
   ("Nothing special", F, "Small spots need tight alignment."),
   ("About ±60 µm", F, "Far beyond single-mode tolerances.")]),
 ("Why are grating couplers good for wafer-scale testing?", [
   ("A fibre array can reach them anywhere on the wafer before dicing", T, "Wafer maps reveal the process variation."),
   ("They are polarisation-independent", F, "They are not."),
   ("They have the lowest loss", F, "Edge couplers can lose less.")]),
],
37: [
 ("What gives the propagation loss in a cutback measurement?", [
   ("The slope of insertion loss against length", T, "Its error bar shrinks with the spread of lengths."),
   ("The intercept", F, "The intercept is the coupler loss."),
   ("The average", F, "Not a loss measurement.")]),
 ("How is the group index measured from a ring?", [
   ("n_g = λ²/(FSR · L)", T, "It checks the fabricated cross-section."),
   ("From the extinction", F, "Extinction relates to coupling."),
   ("From the Q alone", F, "Q gives loss, not n_g.")]),
 ("A ring fit gives two mirror solutions. What resolves them?", [
   ("A series of gaps", T, "Coupling changes with gap; loss does not."),
   ("A longer sweep", F, "The ambiguity remains."),
   ("Nothing", F, "Several gaps resolve it.")]),
],
38: [
 ("In a coherent receiver, why does the local oscillator help?", [
   ("The beat current grows as √(P_S P_LO), lifting the signal above the TIA noise", T, "About 30 dB more electrical signal for −20 dBm signal and +10 dBm LO."),
   ("It adds power to the fibre", F, "It is local to the receiver."),
   ("It removes the need for photodiodes", F, "Balanced photodiodes still detect.")]),
 ("What dominates the energy per bit of the reference link?", [
   ("Laser wall-plug power and ring heaters", T, "Modulators are nearly free by comparison."),
   ("The modulators", F, "They use little energy."),
   ("The fibre", F, "Fibre is passive.")]),
 ("How much margin does the reference link close with?", [
   ("About 5.9 dB at about 3.7 pJ/bit", T, "Its tight spots are the ring modulator, the couplers and the heaters."),
   ("−3 dB", F, "It closes."),
   ("50 dB", F, "Far too optimistic.")]),
],
39: [
 ("What sets FMCW LiDAR's range resolution?", [
   ("The chirp bandwidth: c/(2B)", T, "A wider sweep resolves smaller distances."),
   ("The laser power", F, "Power sets reach, not resolution."),
   ("The fibre", F, "Unrelated.")]),
 ("What happens if an optical phased array's emitter pitch exceeds λ/2?", [
   ("Grating lobes appear", T, "The array then radiates in several directions."),
   ("Nothing", F, "Pitch matters."),
   ("The beam narrows without limit", F, "Lobes, not infinite narrowing.")]),
 ("What sensitivity does a silicon strip ring sensor in water reach, TE versus TM?", [
   ("54 and 206 nm/RIU", T, "TM's field reaches further into the water."),
   ("206 and 54 nm/RIU", F, "TM is the more sensitive one."),
   ("Both 1 nm/RIU", F, "Far too low.")]),
],
}

out = {}
for ch, qs in Q.items():
    assert len(qs) == 3, ch
    out[str(ch)] = []
    for i, (q, opts) in enumerate(qs):
        assert sum(1 for o in opts if o[1]) == 1, (ch, q)
        k = (ch * 3 + i) % len(opts)                      # rotate the answers, so the right one is not always first
        opts = opts[k:] + opts[:k]
        out[str(ch)].append({"q": q, "options": [{"t": t, "ok": ok, "why": why} for t, ok, why in opts]})
path = pathlib.Path(__file__).resolve().parents[1] / "_data" / "quizzes.json"
path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {path.name}: {sum(len(v) for v in out.values())} questions in {len(out)} chapters")
