---
title: "A. Formula Sheet"
parent: Appendices
nav_order: 1
permalink: /appendices/a/
---

# Appendix A. Formula Sheet

The key equations of the tutorial on one page, in the notation used throughout, with the chapter that derives each.
{: .chapterlead }

## Units and power

| Quantity | Formula | Chapter |
|---|---|---|
| Power in dBm | $$P_\mathrm{dBm} = 10\log_{10}(P/1\ \mathrm{mW})$$ | [1]({% link chapters/01_why.md %}) |
| Loss in dB | $$L_\mathrm{dB} = 10\log_{10}(P_\mathrm{in}/P_\mathrm{out})$$ | [1]({% link chapters/01_why.md %}) |
| Optical modulation amplitude | $$\mathrm{OMA} = 2P_\mathrm{avg}(\mathrm{ER} - 1)/(\mathrm{ER} + 1)$$ | [1]({% link chapters/01_why.md %}), [20]({% link chapters/20_modulators.md %}) |
| Loss conversion | $$\alpha\ [\mathrm{dB/cm}] = 4.343\,\alpha\ [\mathrm{cm^{-1}}]$$ | [7]({% link chapters/07_loss.md %}) |
| Photon energy | $$E = hc/\lambda = 1.2398/\lambda[\mu\mathrm{m}]\ \mathrm{eV}$$ | [22]({% link chapters/22_emission.md %}) |

## Waves, interfaces and beams

| Quantity | Formula | Chapter |
|---|---|---|
| Fresnel reflection, normal incidence | $$R = \left(\frac{n_1 - n_2}{n_1 + n_2}\right)^2$$ | [2]({% link chapters/02_em.md %}) |
| Critical angle | $$\sin\theta_c = n_2/n_1$$ | [2]({% link chapters/02_em.md %}) |
| Gaussian beam radius | $$w(z) = w_0\sqrt{1 + (z/z_R)^2}, \quad z_R = \pi nw_0^2/\lambda$$ | [3]({% link chapters/03_gaussian.md %}) |
| Coupling of two Gaussian modes | $$\eta = \left(\frac{2w_1w_2}{w_1^2 + w_2^2}\right)^2 e^{-2d^2/(w_1^2 + w_2^2)}$$ | [3]({% link chapters/03_gaussian.md %}), [17]({% link chapters/17_fiberarrays.md %}) |
| 1 dB lateral tolerance | $$d_\mathrm{1dB} = \sqrt{0.115\,(w_1^2 + w_2^2)}$$ | [17]({% link chapters/17_fiberarrays.md %}) |

## Waveguides

| Quantity | Formula | Chapter |
|---|---|---|
| Slab V-number | $$V = k_0d\sqrt{n_1^2 - n_2^2}$$ | [5]({% link chapters/05_slab.md %}) |
| Single-mode slab (symmetric) | $$d < \lambda/(2\sqrt{n_1^2 - n_2^2})$$ | [5]({% link chapters/05_slab.md %}) |
| Evanescent decay | $$\gamma = k_0\sqrt{n_\mathrm{eff}^2 - n_2^2}$$ | [5]({% link chapters/05_slab.md %}) |
| Group index | $$n_g = n_\mathrm{eff} - \lambda\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}\lambda$$ | [6]({% link chapters/06_soi.md %}) |
| Resonance shift from fabrication | $$\Delta\lambda = (\lambda/n_g)(\partial_W n_\mathrm{eff}\,\Delta W + \partial_t n_\mathrm{eff}\,\Delta t)$$ | [6]({% link chapters/06_soi.md %}), [35]({% link chapters/35_fab.md %}) |
| Two-photon absorption | $$\alpha_\mathrm{TPA} = \beta_\mathrm{TPA}I$$ | [7]({% link chapters/07_loss.md %}) |

## Couplers, interferometers, rings and gratings

| Quantity | Formula | Chapter |
|---|---|---|
| Cross-over length | $$L_x = \lambda/(2\Delta n) = \pi/(2\kappa)$$ | [9]({% link chapters/09_couplers.md %}) |
| Coupler power transfer | $$P_\mathrm{cross} = \sin^2(\pi L/2L_x)$$ | [9]({% link chapters/09_couplers.md %}) |
| MMI beat length | $$L_\pi = 4n_rW_e^2/(3\lambda)$$ | [10]({% link chapters/10_mmi.md %}) |
| Interferometer FSR | $$\mathrm{FSR} = \lambda^2/(n_g\,\Delta L)$$ | [11]({% link chapters/11_mzi.md %}) |
| MZI transmission | $$T = \cos^2(\Delta\phi/2)$$ | [11]({% link chapters/11_mzi.md %}), [20]({% link chapters/20_modulators.md %}) |
| Ring FSR | $$\mathrm{FSR} = \lambda^2/(n_gL)$$ | [12]({% link chapters/12_rings.md %}) |
| All-pass ring | $$T = \frac{a^2 - 2at\cos\phi + t^2}{1 - 2at\cos\phi + a^2t^2}$$ | [12]({% link chapters/12_rings.md %}) |
| Ring linewidth | $$\Delta\lambda = \frac{(1 - at)\lambda^2}{\pi n_gL\sqrt{at}}, \quad Q = \lambda/\Delta\lambda$$ | [12]({% link chapters/12_rings.md %}) |
| Intrinsic Q | $$Q_i = 2\pi n_g/(\lambda\alpha)$$ | [12]({% link chapters/12_rings.md %}) |
| Bragg wavelength | $$\lambda_B = 2n_\mathrm{eff}\Lambda$$ | [13]({% link chapters/13_bragg.md %}) |
| Bragg peak reflectivity | $$R = \tanh^2(\kappa L)$$ | [13]({% link chapters/13_bragg.md %}) |
| Bragg stop band ($$\kappa L \gg 1$$) | $$\Delta\lambda \approx \lambda^2\kappa/(\pi n_g)$$ | [13]({% link chapters/13_bragg.md %}) |
| Fabry–Pérot transmission | $$T = \frac{(1 - R_1)(1 - R_2)A}{(1 - \rho)^2 + 4\rho\sin^2(\phi/2)}, \quad \rho = \sqrt{R_1R_2}\,A$$ | [13]({% link chapters/13_bragg.md %}) |
| Fabry–Pérot FSR and finesse | $$\mathrm{FSR} = \lambda^2/(2n_gL), \quad F = \frac{\pi}{2\arcsin[(1 - \rho)/(2\sqrt{\rho})]} \approx \frac{\pi\sqrt{\rho}}{1 - \rho}$$ | [13]({% link chapters/13_bragg.md %}) |
| Bragg-mirror penetration depth | $$L_p = \tanh(\kappa L_g)/(2\kappa), \quad L_\mathrm{eff} = L + L_{p1} + L_{p2}$$ | [13]({% link chapters/13_bragg.md %}) |
| Fringe contrast and loss (Fabry–Pérot method) | $$K = 2\rho/(1 + \rho^2), \quad \alpha = \ln(R/\rho)/L$$ | [13]({% link chapters/13_bragg.md %}) |
| Second-harmonic power (undepleted, phase-matched) | $$P_{2\omega} = \eta\,P_\omega^2L^2$$; coherence length $$L_c = \lambda/[4(n_{2\omega} - n_\omega)]$$ | [7]({% link chapters/07_loss.md %}) |
| Vernier FSR | $$\mathrm{FSR}_V = \mathrm{FSR}_1\mathrm{FSR}_2/\lvert\mathrm{FSR}_1 - \mathrm{FSR}_2\rvert$$ | [26]({% link chapters/26_tunable.md %}) |

## Coupling to fibres

| Quantity | Formula | Chapter |
|---|---|---|
| Grating-coupler phase matching | $$n_\mathrm{eff} - \sin\theta_\mathrm{air} = \lambda/\Lambda$$ | [15]({% link chapters/15_gc.md %}) |
| BOX directionality period | $$\Delta t = \lambda/(2n_\mathrm{ox}\cos\theta_\mathrm{ox})$$ | [15]({% link chapters/15_gc.md %}) |
| Grating-coupler angular dispersion | $$\mathrm{d}\theta/\mathrm{d}\lambda = -(n_g - \sin\theta)/(\lambda\cos\theta)$$ | [15]({% link chapters/15_gc.md %}) |
| Butt coupling (elliptical mode) | $$\eta = 4/[(w_x/w_f + w_f/w_x)(w_y/w_f + w_f/w_y)]$$ | [16]({% link chapters/16_edge.md %}) |
| 1 dB lateral offset of two Gaussian modes | $$d_\mathrm{1dB} = \sqrt{0.115\,(w_1^2 + w_2^2)}$$ | [17]({% link chapters/17_fiberarrays.md %}) |
| Facet-lens length (waist $$w_0$$ to $$W$$) | $$L = z_R\sqrt{(W/w_0)^2 - 1}, \quad z_R = \pi n w_0^2/\lambda$$ | [17]({% link chapters/17_fiberarrays.md %}) |
| Expanded-beam 1 dB tolerances | $$d = 0.48\,W, \quad \theta = 0.153\,\lambda/W, \quad g = 1.02\,\pi W^2/\lambda$$ | [17]({% link chapters/17_fiberarrays.md %}), [36]({% link chapters/36_testing.md %}) |

## Active devices

| Quantity | Formula | Chapter |
|---|---|---|
| Thermal resonance drift | $$\mathrm{d}\lambda/\mathrm{d}T = (\lambda/n_g)\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}T$$ | [18]({% link chapters/18_thermal.md %}) |
| Heater power for π | $$P_\pi = \lambda G'/(2\,\mathrm{d}n_\mathrm{eff}/\mathrm{d}T)$$ | [18]({% link chapters/18_thermal.md %}) |
| Plasma dispersion (Si, 1550 nm) | $$\Delta n = -(8.8\times10^{-22}\Delta N + 8.5\times10^{-18}\Delta P^{0.8})$$ | [19]({% link chapters/19_eo.md %}) |
| Free-carrier absorption (Si) | $$\Delta\alpha = 8.5\times10^{-18}\Delta N + 6.0\times10^{-18}\Delta P\ \ \mathrm{cm^{-1}}$$ | [19]({% link chapters/19_eo.md %}) |
| Depletion width | $$W = \sqrt{2\varepsilon(V_{bi} + V)(N_A + N_D)/(qN_AN_D)}$$ | [19]({% link chapters/19_eo.md %}) |
| Pockels effect | $$\Delta n = -\tfrac{1}{2}n^3rE, \quad V_\pi L = \lambda g/(n^3r\Gamma)$$ | [19]({% link chapters/19_eo.md %}) |
| Capacitive modulator energy (NRZ) | $$E_\mathrm{bit} \approx \tfrac{1}{4}CV_{pp}^2$$ | [20]({% link chapters/20_modulators.md %}) |
| Photon-lifetime bandwidth of a ring | $$f \approx c/(\lambda Q_L)$$ | [20]({% link chapters/20_modulators.md %}) |
| Responsivity | $$\mathcal{R} = \eta q\lambda/(hc) \approx \eta\,\lambda[\mu\mathrm{m}]/1.24\ \mathrm{A/W}$$ | [21]({% link chapters/21_pd.md %}) |
| Photodiode bandwidth | $$f^{-2} \approx f_t^{-2} + f_{RC}^{-2}, \quad f_t \approx 0.45v_\mathrm{sat}/d$$ | [21]({% link chapters/21_pd.md %}) |
| Bit-error ratio | $$\mathrm{BER} = \tfrac{1}{2}\mathrm{erfc}(Q/\sqrt{2}), \quad Q = (I_1 - I_0)/(\sigma_1 + \sigma_0)$$ | [21]({% link chapters/21_pd.md %}) |
| APD excess noise | $$F = kM + (1 - k)(2 - 1/M)$$ | [21]({% link chapters/21_pd.md %}) |

## Lasers and amplifiers

| Quantity | Formula | Chapter |
|---|---|---|
| Einstein relations | $$B_{12} = B_{21}, \quad A_{21}/B_{21} = 8\pi n^3h\nu^3/c^3$$ | [22]({% link chapters/22_emission.md %}) |
| Gain coefficient | $$\gamma = \sigma(N_2 - N_1), \quad \sigma = \lambda^2g(\nu)/(8\pi n^2\tau_{sp})$$ | [22]({% link chapters/22_emission.md %}) |
| Bernard–Duraffourg condition | $$E_g < h\nu < E_{Fc} - E_{Fv}$$ | [23]({% link chapters/23_gain.md %}) |
| Recombination | $$R(N) = AN + BN^2 + CN^3$$ | [23]({% link chapters/23_gain.md %}) |
| Threshold | $$\Gamma g_\mathrm{th} = \alpha_i + \frac{1}{2L}\ln\frac{1}{R_1R_2}$$ | [24]({% link chapters/24_fp.md %}) |
| Threshold current | $$I_\mathrm{th} = qVR(N_\mathrm{th})/\eta_i$$ | [24]({% link chapters/24_fp.md %}) |
| Differential efficiency | $$\eta_d = \eta_i\alpha_m/(\alpha_i + \alpha_m)$$ | [24]({% link chapters/24_fp.md %}) |
| Mode spacing | $$\Delta\lambda = \lambda^2/(2n_gL)$$ | [24]({% link chapters/24_fp.md %}) |
| Gain below threshold (Hakki–Paoli) | $$\sqrt{R_1R_2}\,G = (\sqrt{r} - 1)/(\sqrt{r} + 1)$$, $$r$$ = peak-to-valley ratio | [13]({% link chapters/13_bragg.md %}), [24]({% link chapters/24_fp.md %}) |
| Temperature dependence | $$I_\mathrm{th}(T) = I_\mathrm{th,0}\,e^{\Delta T/T_0}$$ | [24]({% link chapters/24_fp.md %}) |
| Relaxation-oscillation frequency | $$f_r = \frac{1}{2\pi}\sqrt{v_gaS/[\tau_p(1 + \varepsilon S)]}$$ | [25]({% link chapters/25_dynamics.md %}) |
| K-factor and maximum bandwidth | $$K = 4\pi^2(\tau_p + \varepsilon/v_ga), \quad f_\mathrm{max} = 2\pi\sqrt{2}/K$$ | [25]({% link chapters/25_dynamics.md %}) |
| Linewidth (Henry) | $$\Delta\nu = v_g^2h\nu g_\mathrm{th}n_{sp}\alpha_m(1 + \alpha^2)/(8\pi P_0)$$ | [25]({% link chapters/25_dynamics.md %}) |
| Self-heating | $$\Delta T = Z_\mathrm{th}(IV - P_\mathrm{out})$$ | [27]({% link chapters/27_lasersonsi.md %}) |
| SOA small-signal gain | $$G_0 = e^{(\Gamma g_0 - \alpha_i)L}$$ | [28]({% link chapters/28_soa.md %}) |
| Amplifier noise figure | $$F = 2n_{sp}(G - 1)/G \ge 2\ (3\ \mathrm{dB})$$ | [28]({% link chapters/28_soa.md %}) |

## Systems

| Quantity | Formula | Chapter |
|---|---|---|
| Coherent balanced detection (90° hybrid) | $$i_I = \mathcal{R}\sqrt{P_SP_\mathrm{LO}}\cos\Delta\phi, \quad i_Q = \mathcal{R}\sqrt{P_SP_\mathrm{LO}}\sin\Delta\phi$$ | [38]({% link chapters/38_links.md %}) |
| Link margin | $$P_\mathrm{launch} - \sum L_i - \sum \mathrm{penalties} - P_\mathrm{sens}$$ | [38]({% link chapters/38_links.md %}) |
| Ring sensor | $$S = (\lambda/n_g)\,\partial n_\mathrm{eff}/\partial n_c, \quad \mathrm{LOD} = 3\sigma_\lambda/S$$ | [39]({% link chapters/39_apps.md %}) |
| Phased-array steering | $$\sin\theta = \Delta\phi\,\lambda/(2\pi d)$$ | [39]({% link chapters/39_apps.md %}) |
| FMCW ranging | $$f_b = 2RB/(cT), \quad \Delta R = c/(2B)$$ | [39]({% link chapters/39_apps.md %}) |
