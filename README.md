# Open-Photonics: Silicon Photonics and Lasers, from Waveguides to Tested Chips

An open, interactive tutorial on integrated photonics. It starts from Maxwell's equations and builds up
to waveguides, passive devices, fibre coupling, modulators and detectors, semiconductor lasers and lasers
on silicon, and the fabrication, testing and data analysis that turn a layout into a working chip,
across the **Si, SiN, thin-film LiNbO₃ (TFLN), BaTiO₃ (BTO) and InP** platforms.

**Read it online:** <https://www.kithminrw.com/silicon-photonics-lasers-tutorial/>

> **Status: draft v0.1 (November 2026).** All eight parts are written; the other parts are detailed outlines that
> are being filled in. Corrections are very welcome (see [Contributing](#contributing)).

## What makes it different

- **Interactive demos in every chapter.** Small physical models that run in the browser with no
  installation: change a slider and watch the light. Forty-two are built so far, including a slab-waveguide
  mode solver, exact fibre LP modes, Fresnel reflection and evanescent fields, Gaussian-beam coupling,
  directional couplers, MMI self-imaging, Mach–Zehnder interferometers, ring resonators, Bragg gratings by
  transfer matrix, grating-coupler phase matching and efficiency budget, an inverse-taper edge coupler from
  femwell modes, Gaussian alignment tolerances, a fibre-array alignment game, heater cross-sections
  with computed temperature maps, ring locking, a PN depletion phase shifter, MZM eye diagrams, a ring
  modulator, photodiode bandwidth, receiver sensitivity, level systems, semiconductor gain spectra, laser
  dynamics and linewidth, III–V/Si supermodes, an SOA, a wafer-map Monte Carlo, a circuit simulator, a virtual
  test bench, ring fitting, the full link budget, a biosensor, an optical phased array, a laser rate-equation
  simulator and a Vernier tunable laser.
- **Real devices in 3D.** Devices from open process design kits (SiEPIC EBeam, CORNERSTONE, Luxtelligence
  TFLN) extruded from their layouts with their PDK layer stacks, which you can rotate, slice by layer
  and stretch vertically, with credit to the people who designed them.
- **One design–fabrication–test thread.** A first passive chip in 220 nm SOI, of the kind made in the
  SiEPIC openEBL runs, is laid out, submitted and analysed with free tools; a four-wavelength reference
  link (4 × 50 Gb/s over 2 km) ties the active devices and lasers together.
- **Open material only.** Built from open-source PDKs and tools, open-access papers and public datasets.
  Textbooks, courses and papers that are not open are cited and linked, never copied.

## Contents

| Part | Chapters | State |
|---|---|---|
| Preface and course map | audience, reading paths, the whole outline on one page | written |
| I. Foundations | 1 Why integrated photonics · 2 Electromagnetic theory · 3 Gaussian beams and fibres · 4 Materials and platforms | **written** |
| II. Waveguides | 5 Slab waveguide · 6 Channel waveguides · 7 Loss, dispersion, nonlinearity · 8 Bends, tapers, transitions | **written** |
| III. Passive devices | 9 Couplers · 10 Y-branches and MMIs · 11 MZIs · 12 Rings · 13 Bragg gratings · 14 WDM and polarisation | **written** |
| IV. Coupling and packaging | 15 Grating couplers · 16 Edge couplers · 17 Fibre arrays and packaging | **written** |
| V. Active devices | 18 Thermo-optic tuning · 19 Electro-optic effects · 20 Modulators · 21 Photodetectors | **written** |
| VI. Lasers and amplifiers | 22 Absorption, emission, gain · 23 Semiconductor gain · 24 Fabry–Pérot laser · 25 Dynamics and noise · 26 Tunable lasers · 27 Lasers on silicon · 28 SOAs | **written** |
| VII. Fabrication, testing, data | 29 Fabrication · 30 Design flow and open PDKs · 31 Testing · 32 Data analysis | **written** |
| VIII. Systems | 33 Links and transceivers · 34 Sensing, LiDAR, quantum, computing | **written** |
| Hands-on labs | 12 labs: simulate, make (openEBL), lasers and links | planned |
| PDK devices in 3D | 13 devices from three open PDKs | working |
| Appendices | A formulas · B materials · C glossary · D open tools, PDKs, data · E reading and free simulations | in progress |

## Run it locally

The site is plain Markdown built with [Jekyll](https://jekyllrb.com) and the
[just-the-docs](https://just-the-docs.com) theme. With Ruby 3.1 or newer:

```bash
bundle install
bundle exec jekyll serve
```

Or with Docker, without installing Ruby:

```bash
docker run --rm -p 4000:4000 -v "$PWD":/site -w /site ruby:3.3 bash -c "bundle install && bundle exec jekyll serve --host 0.0.0.0"
```

Then open <http://localhost:4000/silicon-photonics-lasers-tutorial/>. (An arm64 container may add an
`aarch64-linux` platform to `Gemfile.lock`; leave that change out of commits.)

## Repository layout

```
index.md, preface.md, course-map.md   home page, preface, the whole outline on one page
chapters/NN_name.md                   one page per chapter
parts/part-N.md                       one page per part
appendices/                           appendices A–E
devices-3d.md                         the 3D gallery (reads _data/devices3d.json)
references.md, _data/references.yml   the reference list; a citation's number is its position in the file
_includes/demos/*.html                the interactive demos (plain JavaScript, no dependencies)
assets/js/demos.js                    shared plotting and slider helpers for the demos
assets/figs/                          figures (SVG)
assets/models/*.glb                   3D models of open-PDK devices
figsrc/                               Python scripts that draw the figures (style: figstyle.py)
tools/export_3d.py                    exports PDK devices to glTF with gdsfactory
_config.yml, _sass/, _includes/       site settings, "Wafer" colour theme, dark mode, KaTeX maths
.github/workflows/pages.yml           builds and deploys the site on every push to main
```

## Contributing

Spotted a mistake, a broken demo or a missing credit? Please
[open an issue](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/issues) or a pull request.

When writing a page:

- **Maths** goes in `$$...$$` (KaTeX). Inside inline maths, write `\lvert x \rvert` rather than `|x|`:
  a bare `|` makes the Markdown parser read the line as a table. Inside raw-HTML figure captions, write
  `\(...\)` instead of `$$...$$`, which the parser leaves untouched there.
- **Boxes** use `<div class="tbox tbox-TYPE" markdown="1">` with a `<div class="tbox-title">` line;
  types are `keyeq`, `example`, `insight`, `pitfall`, `tryit`, `derivation`, `specnote`, `objectives`, `takeaways`.
- **Links** between pages use `{% link chapters/06_soi.md %}`, so a broken link fails the build.
- **Citations** use `{% include cite.html keys="key1,key2" %}`; add new references at the end of
  `_data/references.yml` so existing numbers stay the same.
- **Every device demo shows its geometry**: a top view or cross-section that redraws as the sliders move,
  to scale where possible (label any stretched axis), drawn with `BD.wg`, `BD.sbend`, `BD.dim` and `BD.scalebar`.
- **Demos** are self-contained `_includes/demos/NAME.html` files that use the helpers in
  `assets/js/demos.js` (`BD.bind` for sliders, `BD.seg` for buttons, `BD.frame` and `BD.line` for plots,
  `BD.observe` to redraw on resize). Keep the models simple, and say in the caption when a number comes
  from an illustrative fit rather than a solver.
- **Sources:** cite and link; do not copy text or figures from books, courses or papers. Use only
  openly licensed PDKs, code and data, and credit their authors.

### Regenerating figures and 3D models

```bash
python3.12 -m venv .venv && .venv/bin/pip install numpy matplotlib gdsfactory ubcpdk cspdk trimesh
.venv/bin/python figsrc/part1_figs.py            # Part I figures -> assets/figs/
.venv/bin/python tools/export_3d.py              # SiEPIC EBeam and CORNERSTONE models -> assets/models/
```

The Luxtelligence TFLN models need that PDK in its own environment, because it pins its own gdsfactory
version: clone [Luxtelligence/lxt_pdk_gf](https://github.com/Luxtelligence/lxt_pdk_gf), install it with
`pip install -e .` into `.venv-lxt`, and run `.venv-lxt/bin/python tools/export_3d.py --pdk lxt`.

## Credits

The tutorial's organisation draws on the open teaching material of the field, in particular
L. Chrostowski and M. Hochberg's *Silicon Photonics Design* (Cambridge University Press) and the UBCx
edX course built around it, the SiEPIC openEBL design–fabrication–test program, the AIM Photonics
Academy courses and the MIT Virtual Manufacturing Lab simulations, and the open PDKs and tools of the
SiEPIC and gdsfactory communities. These are cited and linked, not reproduced; the full list is on the
[References](https://www.kithminrw.com/silicon-photonics-lasers-tutorial/references/) page.

The 3D models are derived from:

- [SiEPIC EBeam PDK](https://github.com/SiEPIC/SiEPIC_EBeam_PDK) (MIT), via [ubcpdk](https://github.com/gdsfactory/ubc) (MIT);
- [CORNERSTONE PDK for gdsfactory](https://github.com/gdsfactory/cspdk) (MIT);
- [Luxtelligence LNOI400 PDK](https://github.com/Luxtelligence/lxt_pdk_gf) (MIT).

Each device keeps its licence, and its designers and papers are named on the 3D page.

## AI assistance

This tutorial is being written with the help of AI tools and may contain mistakes. Please report any you
find through an issue.

## Licence

Text, figures and pages: [CC BY 4.0](LICENSE). Code (demos, scripts, site configuration):
[MIT](LICENSE-CODE). Neither covers the works the tutorial cites or the third-party PDK devices in
`assets/models/`, which keep their own licences.
