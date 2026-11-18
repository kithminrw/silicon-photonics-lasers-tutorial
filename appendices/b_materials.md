---
title: "B. Material Constants"
parent: Appendices
nav_order: 2
permalink: /appendices/b/
---

# Appendix B. Material Constants

Approximate room-temperature values of the photonic materials in this tutorial, and the constants its calculations use.
{: .chapterlead }

These are typical values for orientation. Film properties depend on how the material is deposited or grown, so check the cited sources and your PDK before designing.

## Optical and electronic properties

**Table B.1. Photonic materials near 1550 nm.**
{: .tabcaption #tab-b-1 }

| Material | Index at 1550 nm | Band gap | Notes |
|---|---|---|---|
| Silicon (Si) | 3.48 | 1.12 eV, indirect | two-photon absorption at 1550 nm; no Pockels effect |
| Silica (SiO₂) | 1.44 | ≈ 9 eV | cladding and buried oxide |
| Silicon nitride (Si₃N₄, LPCVD) | ≈ 2.0 | ≈ 5 eV | transparent from the visible to the mid-infrared |
| Lithium niobate (LiNbO₃) | n<sub>o</sub> ≈ 2.21, n<sub>e</sub> ≈ 2.14 | ≈ 4 eV | Pockels r<sub>33</sub> ≈ 31 pm/V {% include cite.html keys="zhu2021" %} |
| Barium titanate (BaTiO₃) | ≈ 2.3 | ≈ 3.2 eV | thin-film Pockels coefficients of hundreds of pm/V {% include cite.html keys="abel2019" %} |
| Indium phosphide (InP) | 3.17 | 1.34 eV, direct | substrate for 1310 and 1550 nm lasers |
| Gallium arsenide (GaAs) | 3.37 | 1.42 eV, direct | substrate for quantum-dot lasers |
| Germanium (Ge) | ≈ 4.3 | 0.66 eV indirect, 0.80 eV direct | absorbs through the C band: photodetectors |
| Water | 1.318 | | the analyte medium of [Chapter 34]({% link chapters/34_apps.md %}) |

## Dispersion models

The figure scripts in <code>figsrc/</code> use these published Sellmeier fits:

**Table B.2. Sellmeier models used for the computed numbers.**
{: .tabcaption #tab-b-2 }

| Material | Model | Source |
|---|---|---|
| Silicon | $$n^2 = 11.6858 + \frac{0.939816}{\lambda^2} + \frac{0.00810461\,\lambda_1^2}{\lambda^2 - \lambda_1^2}$$, $$\lambda_1 = 1.1071$$ µm | Li {% include cite.html keys="li1980" %} |
| Fused silica | three-term Sellmeier (0.6961663, 0.4079426, 0.8974794; 0.0684043, 0.1162414, 9.896161 µm) | Malitson {% include cite.html keys="malitson1965" %} |
| Silicon nitride | two-term Sellmeier for LPCVD films | Luke et al. {% include cite.html keys="luke2015" %} |
| Lithium niobate | extraordinary and ordinary Sellmeier fits | Zelmon et al. {% include cite.html keys="zelmon1997" %} |

## Thermal and thermo-optic properties

**Table B.3. Thermo-optic and thermal constants (room temperature).** The thermal conductivities and heat capacities are those of the heater model of [Chapter 18]({% link chapters/18_thermal.md %}).
{: .tabcaption #tab-b-3 }

| Material | dn/dT (1/K) | Thermal conductivity (W/m·K) | Volumetric heat capacity (J/m³·K) |
|---|---|---|---|
| Silicon | 1.8 × 10⁻⁴ | 148 (bulk) | 1.63 × 10⁶ |
| Silica | 1 × 10⁻⁵ | 1.38 | 1.60 × 10⁶ |
| Silicon nitride | 2.5 × 10⁻⁵ | 20–30 (film) | ≈ 2 × 10⁶ |
| TiN (heater) | | 28 (film) | 2.85 × 10⁶ |
| Air | | 0.026 | 1.2 × 10³ |
| Waveguide (500 × 220 nm Si strip, femwell) | dn<sub>eff</sub>/dT = 2.0 × 10⁻⁴ | | |

## Silicon as an electro-optic and nonlinear material

**Table B.4. Silicon at 1550 nm.**
{: .tabcaption #tab-b-4 }

| Quantity | Value | Chapter |
|---|---|---|
| Plasma dispersion, electrons | Δn = −8.8 × 10⁻²² ΔN, Δα = 8.5 × 10⁻¹⁸ ΔN cm⁻¹ | [19]({% link chapters/19_eo.md %}) {% include cite.html keys="soref1987" %} |
| Plasma dispersion, holes | Δn = −8.5 × 10⁻¹⁸ ΔP<sup>0.8</sup>, Δα = 6.0 × 10⁻¹⁸ ΔP cm⁻¹ | [19]({% link chapters/19_eo.md %}) |
| Relative permittivity (DC) | 11.7 | [19]({% link chapters/19_eo.md %}) |
| Intrinsic carrier density | 1.0 × 10¹⁰ cm⁻³ | [19]({% link chapters/19_eo.md %}) |
| Kerr coefficient n<sub>2</sub> | ≈ 6 × 10⁻¹⁸ m²/W (SiN ≈ 2.5 × 10⁻¹⁹) | [7]({% link chapters/07_loss.md %}) |
| Two-photon absorption β<sub>TPA</sub> | 0.5–1 cm/GW | [7]({% link chapters/07_loss.md %}) |
| Radiative recombination B | ≈ 10⁻¹⁴ cm³/s (InGaAsP ≈ 10⁻¹⁰) | [22]({% link chapters/22_emission.md %}) |

## III–V gain material

**Table B.5. Parameters of the laser models (InGaAsP-like, 1550 nm).** Illustrative textbook values, used consistently in Chapters 23–25.
{: .tabcaption #tab-b-5 }

| Quantity | Value |
|---|---|
| Electron and hole effective masses | 0.045 m₀ and 0.46 m₀ |
| Kane energy E<sub>p</sub> | 25 eV |
| Band-gap temperature coefficient | −0.35 meV/K (about +0.5 nm/K) |
| Recombination coefficients A, B, C | 10⁸ s⁻¹, 10⁻¹⁰ cm³/s, 3 × 10⁻²⁹ cm⁶/s |
| Transparency density (bulk model) | 1.3 × 10¹⁸ cm⁻³ |
| Differential gain (bulk model, 3 × 10¹⁸ cm⁻³) | 4.7 × 10⁻¹⁶ cm² |
| Logarithmic gain fit (laser demo) | g = 1500 cm⁻¹ · ln(N / 2 × 10¹⁸ cm⁻³) |
| Gain compression ε | 2 × 10⁻¹⁷ cm³ |
| Characteristic temperature T₀ | ≈ 60 K |
| Germanium saturation velocity | ≈ 6 × 10⁶ cm/s (photodiode transit time) |

## Physical constants

| Constant | Value |
|---|---|
| Speed of light c | 2.998 × 10⁸ m/s |
| Planck constant h | 6.626 × 10⁻³⁴ J·s |
| Elementary charge q | 1.602 × 10⁻¹⁹ C |
| Boltzmann constant k | 1.381 × 10⁻²³ J/K (kT = 25.9 meV at 300 K) |
| Vacuum permittivity ε₀ | 8.854 × 10⁻¹² F/m |
| Electron mass m₀ | 9.109 × 10⁻³¹ kg |
