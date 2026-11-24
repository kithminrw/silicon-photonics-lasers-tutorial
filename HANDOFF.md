# HANDOFF — Open-Photonics (pick up here)

> **Out of date in places.** These working notes were last written on 18 Nov 2026. On 19 Nov a new Part VII
> (Design, Simulation and Layout, Ch 29–34) was added and the later chapters renumbered (Fabrication 35, Testing 36,
> Data Analysis 37, Links 38, Applications 39); 171 figures, Labs 2–12, six more demos (48 in all), sections 25.10
> and 27.9, number checks of every chapter and an IP audit followed. Chapter numbers below use the old numbering;
> the git log from 19 Nov onwards has the details.

Last updated: 18 November 2026 (layout pass over all 42 demos; numbers in Ch 22–34 checked). Repository scaffolded, full outline, **Part I (Ch 1–4) written**, 17 demos and
the 3D gallery working; pushed to `main` and live at https://www.kithminrw.com/silicon-photonics-lasers-tutorial/
(the user decided to keep the repository name; a rename to photonics-tutorial was considered and dropped).

## 1. The goal

An open, interactive tutorial website on silicon photonics and lasers (Jekyll + just-the-docs, Markdown
pages, no LaTeX book), with
**many interactive demos** and **open-PDK devices in 3D** (like skillsurf.org/art_of_aicd/devices-3d/),
crediting their designers. Use only material that is open source or already shared publicly; cite and
link everything else, never copy.

Topics the user asked for, and where they live: waveguide fundamentals on SOI (Part II), EM theory (Ch 2),
passive devices (Part III), active devices (Part V), fibre arrays (Ch 17), laser fundamentals and deep dive
(Part VI, Ch 22–27), SOAs and PDs (Ch 28, 21), Gaussian beams (Ch 3), fabrication (Ch 29), testing (Ch 31),
data analysis (Ch 32), platforms Si/SiN/BTO/InP/TFLN (Ch 4, plus platform sections in Ch 6, 19, 20, 27).

## 2. Where we stopped

| Item | State |
|---|---|
| Site (just-the-docs, "Wafer" theme: indigo + teal; dark mode; KaTeX; no logo) | builds cleanly |
| Home, preface, course map, references | written |
| Part I, Ch 1–4 | **written** (17 Nov 2026): full text, 5 figures (`figsrc/part1_figs.py` + `assets/figs/ch01_reflink.svg`), worked examples, reference-link targets (Table 1.3) |
| Part II, Ch 5–8 | **written** (18 Nov 2026): slab theory with exact TE/TM solver numbers (220 nm: TE0 2.848, TM0 2.053, TE1 cut-off 245 nm, 1/γ 101 nm, Γ 0.81, n_g 3.70/3.96); strips from **femwell** (`figsrc/femwell_modes.py`, `ch06_sweep.py`): 500 × 220 TE0 2.446 / n_g 4.18, TM0 1.771 / 3.74, 1310 TE0 2.712 / 4.16, rib 500/220/90 TE0 2.568 / 3.89, TE1 guided from ~450 nm; loss (scaling, FCA, BOX leakage 7 dB/100 nm TE vs 3.6 TM, TPA); bends (caustic γx_r: Si 2 µm ≈ SiN 20 µm), tapers, crossings; new demos eim, cutback, bend |
| Part III, Ch 9–14 | **written** (18 Nov 2026): supermodes from femwell (`figsrc/ch09_supermodes.py`): L_x 37.8 µm at 200 nm gap, ×2.4 per 100 nm, Δn ∝ λ^7.7, 3 dB coupler 16.4 µm + bends, drift 0.35 %/nm; dc and ring demos refitted to it; MMI (L_π 89.8 µm for 6 µm, σ = 1 for TE-like modes; corrected 18 Nov from 94.3 µm with σ = 0); MZI (cross-port ER formula, bar null when κ1²+κ2²=1); rings (Table 12.1: 10 µm ring, gaps 200/250/300 nm); Bragg (Λ 316.8 nm, κL, PDK κ up to 1.4e5 /m); WDM demux design for the reference link (R ≈ 7.2 µm, FSR 12.8 nm, Q_L ≈ 2400) |
| Part IV, Ch 15–17 | **written** (Nov 2026): grating couplers (Λ ≈ 607 nm averaged-index / ~630 nm full sim for 8°; BOX directionality period 0.54 µm, thin-sheet model 29–71 %, 62 % at 2 µm; uniform overlap ≤ 80 % at 1/α = 1.46 w₀; Table 15.1 budget; 1 dB BW ≈ 42 nm model, SiEPIC wiki 4.1 dB / 30.6 nm for an apodised SWG design); edge couplers from **femwell** inverse-taper sweep (`figsrc/ch16_taper.py` → `ch16_taper.json`, moments and overlaps on quadrature points; TE mode spreads below ~140 nm, TM below ~100 nm); fibre arrays, Gaussian tolerances (±2.35 µm GC, ±0.60 µm lensed), epoxy, PWB, CPO, SiEPIC DFT rules |
| Part V, Ch 18–21 | **written** (Nov 2026): femwell dn_eff/dT 2.0e-4 (strip, 74 pm/K) and 1.89e-4 (rib); heater cross-sections by **scikit-fem** (`figsrc/ch18_heater.py` → `ch18_heater.json`: TiN plain/trench/undercut P_pi 26/16.4/4.5 mW, 10–90 % 17/21/180 µs; doped 22/15.6/4.3 mW; undercut modelled as a continuous oxide membrane); PN depletion from femwell perturbation weights (`figsrc/ch19_pn.py` → `ch19_pn.json`; 5e17: VpiL 1.37 V·cm at 2 V, 13 dB/cm; 1e18: 1.13, 28); TFLN VpiL 2.6 V·cm push-pull (g 5 µm, Γ 0.5); Si TW MZM 3 mm: Vpi 4.7 V, ER 6.1 dB at 2 Vpp, IL 6.3 dB, 0.4 pJ/bit; ring modulator target (≥ 4 dB at 2 Vpp, ≤ 3 dB IL) needs ~50 pm/V and Q_L ≈ 8000 (24 GHz): tight; Ge PD 15×4 µm, 0.5 µm: 48 GHz; receiver −11.6 dBm at 1e-12 (ER 4 dB, 20 pA/√Hz), −14.7 dBm with KP4 |
| Part VI, Ch 22–28 | **written** (Nov 2026): levels/Einstein/Er example; bulk gain model `figsrc/ch23_gain.py` (N_tr 1.3e18, dg/dN 4.7e-16 cm², 725 /cm at 2.7e18; laser demo's log fit gives 3.2e18); FP laser (I_th 19 mA, 0.21 W/A/facet, T0 60 K, τ_d 0.9 ns at 40 mA); dynamics at 50 mA (f_r 4.7 GHz, f3dB 7.2 GHz, K 314 ps → 28 GHz, Henry linewidth 2.1 MHz at 6.5 mW, α = 4); Vernier 10/11 µm Si rings FSR_V 92 nm, gearing 11; III–V/Si supermodes by femwell `figsrc/ch27_hybrid.py` (fundamental: MQW 52 % → 14 %, Si 1 % → 78 % from 0.4 → 1.5 µm, equal near 0.85 µm; partner mode erratic, drawn as points); SOA 1 mm: 13 dB, 8.7 dBm at −3 dB, NF 6.5 dB |
| Part VII, Ch 29–32 | **written**: fab and variation (0.6/1.4 nm per nm); design flow and open PDKs; testing; analysis (Worked Example 32.1 uses illustrative fit numbers) |
| Part VIII, Ch 33–34 | **written**: reference link closed in Table 33.1 (−2.7 dBm received, 5.9 dB margin after 3.0 dB penalties, dispersion included, 3.65 pJ/bit vs 5 target); sensors by femwell `figsrc/ch34_sensor.py` (strip in water: S 54 nm/RIU TE, 206 TM), OPA, FMCW worked example |
| Appendices | A (formula sheet), B (materials, Sellmeier sources, thermal and laser-model constants), C (glossary) now **written**; D and E written earlier |
| Demos (`_includes/demos/`) | **42 built**: budget (Ch 1), polar, fresnel, packet (2), gaussian, fiber (3), platforms (4), slab (5), eim, cutback (6–7), bend (8), dc (9), mmi (10), mzi (11), ring (12), bragg (13), gc, gceff (15), taper (16), couple, align (17), heater, lock (18), pn (19), mzm, ringmod (20), pdbw, rx (21), levels (22), gainspec (23), laser (24), dyn (25), vernier (26), hybrid (27), soa (28), wafermc (29), circuit (30), testbench (31), ringfit (32), linkbudget (33), biosensor, opa (34) |
| 3D gallery (`devices-3d.md`) | 13 devices: SiEPIC EBeam ×6, CORNERSTONE ×4 (Si 220 rib, SiN 300), Luxtelligence TFLN ×3 |
| Appendices | D (open tools/PDKs/data) and E (reading + free simulations) written; A, B, C started |

Checks done: every demo loads without console errors; numbers checked by hand (slab n_eff 2.847 for
220 nm Si, TE1 cut-off 245–250 nm; Si/SiO₂ critical angle 24.4°; FP laser I_th 19 mA, 0.21 W/A per
facet; ring FSR 9.1 nm at R = 10 µm; Bragg peak R = tanh²κL). No horizontal scroll at 375 px; light
and dark themes both checked.

Layout check of all 42 demos, 18 Nov 2026, with `tools/demo_audit.js` (every slider at both ends, every mode
button) at window widths 375, 414, 700, 900 and 1280 px, plus a screenshot of every demo at 375 px: no script
errors, no horizontal scroll, no label cut off at a panel edge or overlapping another label or a panel tag, and
every panel tag on one line. The Vernier demo (Ch 26) used to throw on panels under 300 px (it reserved a fixed
300 px); it now sizes its drawing from the room it needs and has a compact layout under 520 px. At 320 px
(first-generation iPhone SE) a few labels still crowd: ringfit's two-ring sketch, the link margin bars,
gainspec's density axis. Left as they are (readable, but a label sits on a drawn shape at phone width): the MMI's
"upper/lower %" over the MMI body's corner, the photodiode's "intrinsic Ge" over a contact, the grating-coupler
efficiency side view's "grating 20 µm" over the teeth, and legends crossing curves in a few plots. Slider moves cost 2–17 ms (ringfit's χ² grid is the slowest, 34 ms at
worst); gainspec's Fermi table now takes 6 ms instead of 35 ms (substitution x = t², range −10 < η < 30;
readouts unchanged except 632 → 631 /cm at 2.5 × 10¹⁸, 300 K).

## 3. Decisions made

- **Markdown site, no LaTeX book.** Site name "Open-Photonics" (not "Open-Photonics Tutorial"; changed at the user's request 2026-11-17). Personal project: no organisation branding.
- **Uppercase labels:** demo headers (`.bd-head`) and some box titles are CSS-uppercased, which turns `µ` into a capital Mu ("127 MM"). Wrap units there as `<span class="nc">µm</span>`.
- **Maths:** never put a bare `|` inside inline `$$...$$` (kramdown reads the line as a table); use `\lvert \rvert`.
  In raw-HTML figcaptions write `\(...\)` instead of `$$...$$`.
- **Two running examples:** (1) "your first chip", an openEBL-style passive 220 nm SOI chip at 1550 nm,
  which the labs lay out, submit and analyse; (2) "the reference link": 4 λ on the 400 GHz grid
  (1546.12–1555.75 nm), 4 × 50 Gb/s NRZ, 2 km SMF, BER < 1e-12, margin ≥ 3 dB, ≤ 5 pJ/bit (Table 1.3, draft).
  First-pass budget (Ex. 1.1): 10 dBm laser, 12.7 dB loss, −2.7 dBm received, 9.3 dB margin vs −12 dBm
  sensitivity. Dispersion: 34 ps/nm at 2 km is inside the ~40–60 ps/nm tolerance of chirp-free 50G NRZ (Ex. 2.5).
- **Demo models are deliberately simple** and say so in their captions when a number comes from an
  illustrative fit (directional-coupler Δn(g, λ) anchored to L_x ≈ 30 µm at 200 nm gap; grating coupler
  uses averaged slab indices, so its period comes out ~607 nm instead of the ~630 nm of real 70 nm-etch
  couplers; laser uses textbook InGaAsP parameters).
- **External simulations are linked, not embedded**: MIT VM-Lab / AIM Photonics Academy sims (from the
  ETOP 2023 handout), PhET, mustafa.sh tools.

- **Every device demo shows its 2D geometry** (user request, 17 Nov 2026): a top view or cross-section that
  redraws with the sliders, to scale where possible (say so when an axis is stretched), using the helpers
  `BD.wg`, `BD.sbend`, `BD.dim`, `BD.scalebar`, `BD.label` and `BD.GEO` colours in `assets/js/demos.js`.
  Done for slab, MMI, MZI, ring (slider is now the gap; κ² from the Ch 9 coupler model), coupler, Bragg,
  grating coupler, fibre, Vernier and Fabry–Pérot demos.
- **Demo layout rules** (18 Nov 2026). Panels as narrow as 298 px must work (a 360 px phone; also each of
  the two side-by-side panels just above the stacking width). So: a panel tag (`.bd-tag`) is one line of at most
  ~48 characters; a label near an edge measures itself and flips or slides inwards (see levels, opa, gainspec,
  hybrid); long names get a short form on narrow panels (testbench, linkbudget). Shared fixes in
  `assets/js/demos.js` and `demos.css`: `BD.frame` skips ticks outside the axis range and slides end tick labels
  inside the canvas; `BD.hline`/`BD.vline` draw nothing off the plot, and a `vline` label flips left near the
  right edge; `BD.vline(f, x, col, dash, label, dy)` moves a label down a row when two lines are close (Fresnel
  θc/θB, coupler); the default plot top `pad.t` is 30 (was 22), so the top tick label clears the panel tag;
  `.bd-row` stacks by the demo's own width (container query, 640 px), not the window's, so 800–960 px
  windows with the sidebar open no longer squeeze each panel to ~220 px; readout values do not break inside.
  Watch for name clashes when adding a `var` inside a demo's `draw()`: a `var` is visible in the whole function,
  so reusing an existing name (`cross` and `lx` in the coupler demo) silently breaks the demo.
- **Labs layout** (18 Nov 2026): each lab is a page in `labs/` (`parent: Hands-On Labs`, permalink `/labs/lab-NN/`,
  title "Lab N. …") beside its script; `labs/` is now part of the build (only `labs/*.png` excluded), so the
  scripts download from the site, and `_config.yml` gives the lab pages the default layout. Checkpoints use the
  `tbox-specnote` box; answers sit in `<details markdown="1">`.
- **Hands-On Labs is its own section** (`labs.md`, nav between Part VIII and the 3D gallery), not a chapter;
  Part VII is Ch 29–32 and Part VIII Ch 33–34 (Links, Applications). The reference link closes in **Ch 33**.

## 4. Sources and what may be used

| Source | Use |
|---|---|
| Chrostowski & Hochberg, *Silicon Photonics Design* (Cambridge) | cite only; organisation guide |
| UBCx Phot1x edX course, AIM Photonics Academy courses | cite/link only |
| SiEPIC EBeam PDK, ubcpdk, cspdk, gvtt, Luxtelligence lxt_pdk_gf | **MIT**: 3D models and layouts may be shown, with credit |
| openEBL repos, UBC ELEC 413 repos (SiEPIC GitHub) | **MIT**: designs and measurement data usable for Ch 32 / labs |
| IEEE 11030682 = Hammood, Shekhar, Chrostowski, "SiEPIC openEBL", ETOP 2025 | cite |
| MIT VM-Lab simulations (ETOP 2023 handout) | link only |
| Lecture slides and handouts that are not openly licensed | topic coverage only; not reproduced |
| OpenLight PASIC PDK | not public: describe only from public press/website; no 3D |

## 5. Next steps

**Stopped here on 18 Nov 2026 at the user's request, after writing Parts VI–VIII and appendices A–C.** What remains:

1. **Numbers in Chapters 22–34: checked 18 Nov 2026** (every calculated value recomputed in Python, demos ported
   and compared at their defaults; ~280 numbers). Fixed: Ch 23 peak-wavelength range (1480→1357 nm) and the
   absorption reference point; Ch 24 facet reflectivity (0.30 at n = 3.4); the laser demo now gives the threshold
   itself T₀ = 60 K (transparency density scaled with 143 K; it used to give an effective ~25 K); Ch 25 linewidth
   formula uses the modal gain Γg_th; Ch 26 Vernier FSR 91 nm and the demo's "supermodes compete" caption now
   tests the gain at the next coincidence; Ch 27 self-heating 10.4 K / 19 %, "MQW region" not "wells"; Ch 28 P_sat's
   A, n_sp = 2, margin before/after penalties; Ch 29 and the wafer demo: the reddest die sets the offset, the bluest
   needs the most heater power (the demo now marks the bluest die); Ch 31 test bench: 250 nm-gap ring of Table 12.1
   and 1 pm steps in the zoom (measured extinction 11.1 dB, true 10.9); Ch 30 circuit demo: -1 dB width
   interpolated (1.73 nm); Ch 32 mirror "losses" 8.6/3.6/1.5 dB/cm; Ch 33 adds the 0.5 dB dispersion penalty that
   Example 2.5 promises (margin 5.9 dB; −4 dB couplers 3.9 dB; laser cut 2.9 dB saves 0.65 pJ/bit), says which
   Table 33.1 values are Chapter 1 estimates or allowances, and calls the 0.5 dB crosstalk penalty generous
   (estimate ≈ 0.1 dB); Ch 34 beam width 0.886 λ/(Nd), N output phase shifters in an MZI mesh, oxide to 3.5 µm,
   both LODs; Ch 15 link label to Ch 25. Untouched on purpose: values that are illustrative choices.
2. **Labs** (`labs.md`): **Lab 1 written** (18 Nov 2026): `labs/lab01_slab.md` + `labs/lab01_slab.py`, NumPy only,
   reproduces the Ch 5–6 numbers (2.8478 / 2.0533, 101 nm, Γ 0.810, 245.1 nm, n_g 3.70 / 3.96; EIM 2.491 against
   femwell 2.446) and draws `assets/figs/lab01_expected.png`. Write the other eleven the same way: a page with
   checkpoints, exercises and answers, beside a script that prints each checkpoint next to the chapter's value.
   Next easiest without new installs: Labs 5 (Bragg transfer matrices), 10 (rate equations), 11 (Vernier) and
   12 (link budget), all NumPy. Lab 9 needs openEBL measurement data from the SiEPIC GitHub (MIT): ask the user
   before downloading it. Labs 2–4 and 6 need femwell, SAX and MEEP, which are not installed on this machine.
3. Optional extras: a Pockels demo for Ch 19; a 2D MEEP FDTD check of the grating coupler (Ch 15); a self-heating
   option in the laser demo (Ch 27 text covers it with a worked example).
4. 3D gallery: add VTT once etch depths can be sourced publicly (gvtt has no layer stack); add SiEPIC Bragg gratings,
   contra-DCs, Shuksan laser cells; check the CORNERSTONE "laser_full" cells.
5. Hosting: the user's personal GitHub Pages, https://www.kithminrw.com/silicon-photonics-lasers-tutorial/
   (a personal project: no organisation name, logo or links). Pushing to `main` deploys.

## 6. Environment notes

- Preview: a `photonics-jekyll` entry in the session-root `.claude/launch.json` (Docker `ruby:3.3`,
  port 4002, gems in a named Docker volume). An arm64 container adds `aarch64-linux` to
  `Gemfile.lock`; revert that line before committing. On an x86_64 machine `Gemfile.lock` stays unchanged.
  Docker must be running; the repository is mounted at `/srv/jekyll`, `--force_polling` makes regeneration
  notice edits; the site is at http://localhost:4002/silicon-photonics-lasers-tutorial/.
- Python: `.venv` (Python 3.12: gdsfactory 9.51, ubcpdk, cspdk, trimesh) and `.venv-lxt` (Luxtelligence PDK,
  installed editable from `../.photonics-src/lxt_pdk_gf`, next to this repository). Both gitignored.
- Outline pages were generated once by a throw-away script; edit the Markdown directly from now on.
