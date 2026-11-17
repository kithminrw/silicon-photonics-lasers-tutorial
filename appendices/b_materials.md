---
title: "B. Material Constants"
parent: Appendices
nav_order: 2
permalink: /appendices/b/
---

# Appendix B. Material Constants

Approximate room-temperature values of the photonic materials in this tutorial.
{: .chapterlead }

<p><span class="status status-outline">draft</span> Typical values for orientation; film properties depend on how the material is deposited or grown, so check the cited sources and your PDK before designing.</p>

**Table B.1. Photonic materials near 1550 nm.**
{: .tabcaption #tab-b-1 }

| Material | Index at 1550 nm | Bandgap | Notes |
|---|---|---|---|
| Silicon (Si) | 3.48 | 1.12 eV, indirect | thermo-optic dn/dT ≈ 1.8 × 10⁻⁴ /K; two-photon absorption at 1550 nm |
| Silica (SiO₂) | 1.44 | ≈ 9 eV | dn/dT ≈ 1 × 10⁻⁵ /K; cladding and buried oxide |
| Silicon nitride (Si₃N₄, LPCVD) | ≈ 2.0 | ≈ 5 eV | dn/dT ≈ 2.5 × 10⁻⁵ /K; transparent from the visible to the mid-infrared |
| Lithium niobate (LiNbO₃) | n_o ≈ 2.21, n_e ≈ 2.14 | ≈ 4 eV | Pockels r₃₃ ≈ 30 pm/V {% include cite.html keys="zhu2021" %} |
| Barium titanate (BaTiO₃) | ≈ 2.3 | ≈ 3.2 eV | thin-film Pockels coefficients of hundreds of pm/V {% include cite.html keys="abel2019" %} |
| Indium phosphide (InP) | 3.17 | 1.34 eV, direct | substrate for 1310 and 1550 nm lasers |
| Gallium arsenide (GaAs) | 3.37 | 1.42 eV, direct | substrate for quantum-dot lasers |
| Germanium (Ge) | ≈ 4.3 | 0.66 eV indirect, 0.80 eV direct | absorbs through the C band: photodetectors |

To be added: Sellmeier coefficients, thermo-optic and electro-optic tensors, nonlinear coefficients, and carrier-dispersion constants for silicon.
