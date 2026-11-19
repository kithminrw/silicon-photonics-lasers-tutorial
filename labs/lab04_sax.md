---
title: "Lab 4. MZI and ring circuits with S-parameters"
parent: Hands-On Labs
nav_order: 4
permalink: /labs/lab-04/
---

# <span class="chapnum">Lab 4 · Simulate</span>MZI and Ring Circuits with S-Parameters

Write compact models for a waveguide, a coupler and a ring, connect them into circuits with the open circuit simulator SAX, and reproduce the MZI, ring and lattice-filter numbers of Chapters 11, 12 and 30; then solve the same netlists with twenty lines of NumPy and get the same answers.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this lab you will</div>

- write compact models as S-parameter dictionaries: a waveguide with effective index, group index and loss, a directional coupler, and a ring;
- describe a circuit as a netlist, simulate an unbalanced MZI and read the group index back from its free spectral range;
- build all-pass and add-drop rings from a coupler and a loop, and measure extinction, linewidth and Q;
- compare a two-stage lattice filter with a plain MZI;
- connect S-matrices yourself in NumPy, and check that you get SAX's answer.

</div>

## What you need

- [Chapter 11]({% link chapters/11_mzi.md %}) (Sections 11.2, 11.3 and 11.6), [Chapter 12]({% link chapters/12_rings.md %}) (Sections 12.2 to 12.4) and [Chapter 30]({% link chapters/30_flow.md %}) (Section 30.6); [Lab 2]({% link labs/lab02_femwell.md %}) for where the waveguide's numbers come from.
- Python 3.11 or newer with NumPy and Matplotlib: `pip install numpy matplotlib`. SAX is optional: `pip install sax` installs it with JAX. Without it, or with `--numpy`, the script solves every circuit with its own NumPy function and prints the same numbers. Tested with Python 3.12, SAX 0.18.2, JAX 0.9.2, NumPy 2.4.6 and Matplotlib 3.11.2.
- The script <a href="{{ '/labs/lab04_sax.py' | relative_url }}" download><code>lab04_sax.py</code></a> (also in the repository's [`labs/` folder](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/tree/main/labs)).
- About two hours, including the exercises.

Run it from a terminal in the folder where you saved it:

```
python lab04_sax.py
python lab04_sax.py --numpy
```

It prints a checkpoint for each part below, with the value from the chapter beside it, and saves the figure `lab04_sax.png`. With NumPy it takes seconds. With SAX it takes one to three minutes, most of it spent importing SAX and JAX and then, the first time each circuit is used, analysing the netlist and compiling it. Read each part, then the matching function in the script; change things and run it again. Lengths and wavelengths are in micrometres.

## <span class="secnum">L4.1</span>Compact models

A circuit simulator does not see fields, only what each device does to the waves at its ports: its **scattering matrix** (Section 30.6). SAX stores it as a dictionary from a pair of ports, (from, to), to a complex transmission, with one entry per wavelength, and a model is a Python function that returns that dictionary. The script's two basic models follow the conventions of Chapters 9 and 11, a phase $$e^{-j\beta L}$$ and cross-coupling $$-j\kappa$$:

```python
def waveguide(wl=LAM, length=10.0, neff=N_EFF, ng=N_G, loss_db_cm=0.0, wl0=LAM):
    ne = neff - (ng - neff) * (wl - wl0) / wl0
    amp = 10 ** (-loss_db_cm * length * 1e-4 / 20)          # dB/cm of power -> field amplitude over length um
    return reciprocal({("in0", "out0"): amp * xp.exp(-2j * xp.pi * ne * length / wl)})

def coupler(wl=LAM, coupling=0.5):
    one = xp.ones_like(xp.asarray(wl, dtype=float))
    t, k = xp.sqrt(1 - coupling) * one, -1j * xp.sqrt(coupling) * one
    return reciprocal({("in0", "out0"): t, ("in0", "out1"): k, ("in1", "out0"): k, ("in1", "out1"): t})
```

The waveguide's effective index falls with wavelength at the rate $$\mathrm{d}n_\mathrm{eff}/\mathrm{d}\lambda = -(n_g - n_\mathrm{eff})/\lambda$$ (Chapter 2), so its phase has both the right value and the right slope: 2.446 and 4.18 from Lab 2 and Table 6.1. Two more details: `reciprocal` adds the reverse direction of every entry, since a passive device transmits equally both ways, and `xp` is `jax.numpy` when SAX is installed, NumPy otherwise, so the same model serves both. The coupler is lossless and the same at every wavelength, like the couplers of the Chapter 30 demo.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint A</div>

The waveguide model's effective index is 2.5019 at 1500 nm and 2.3901 at 1600 nm, and the slope of its phase gives back $$n_g = 4.1800$$. The 30 % coupler conserves power: $$\lvert t\rvert^2 + \lvert\kappa\rvert^2 = 1.000000$$. A 10 µm ring at 2 dB/cm has a round-trip field transmission $$a = 0.99855$$ and an intrinsic $$Q_i = 3.68\times10^5$$ (Chapter 12: 0.99855 and $$3.7\times10^5$$).

</div>

## <span class="secnum">L4.2</span>A netlist, and the unbalanced MZI

A circuit is a **netlist**: the instances, each with its model and settings; the connections between their ports; and which ports are the circuit's own. `mzi_netlist` writes the MZI of the Chapter 30 demo, with the delay in the upper arm and the lower arm joining the couplers directly:

```python
{"instances": {"dc1": {"component": "coupler", "settings": {"coupling": k1}},
               "delay": {"component": "waveguide", "settings": {"length": dl}},
               "dc2": {"component": "coupler", "settings": {"coupling": k2}}},
 "connections": {"dc1,out0": "delay,in0", "delay,out0": "dc2,in0", "dc1,out1": "dc2,in1"},
 "ports": {"in": "dc1,in0", "in2": "dc1,in1", "bar": "dc2,out0", "cross": "dc2,out1"}}
```

`sax.circuit(netlist, MODELS)` returns a new model, a function of the wavelength (and of any instance's settings) that gives the S-parameters between the circuit's ports. The script sweeps it from 1530 to 1570 nm, finds the nulls of the bar port with `minima`, which fits a parabola through the lowest three samples of each, and measures their spacing.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint B</div>

With $$\Delta L = 100$$ µm, the bar port's nulls on either side of 1550 nm are at 1548.89 and 1554.65 nm, 5.761 nm apart; $$\lambda^2/(n_g\Delta L)$$ is 5.748 nm at 1550 nm (Chapter 11: 5.75 nm), and 5.761 nm at the midpoint of the two nulls. Reading the group index back from the measured FSR, as Section 11.6 does on a chip, gives 4.180. With $$n_\mathrm{eff}$$ instead of $$n_g$$ the FSR would be 9.82 nm (Chapter 6: 9.8 nm). At 1550 nm the bar port transmits −4.86 dB and the cross port −1.72 dB (Chapter 30 demo: −4.9 and −1.7 dB). The two outputs always add up to 1.000000, and the bar port's extinction is 104 dB, limited only by how close the wavelength grid comes to each null: with 50 % couplers and no loss the nulls are perfect.

</div>

## <span class="secnum">L4.3</span>The all-pass ring

A ring is a coupler whose second waveguide is closed on itself. As a netlist, that is a loop: the coupler's `out1` feeds a waveguide $$2\pi R$$ long whose output returns to the coupler's `in1`. SAX solves loops like any other connection, as a linear system.

```python
{"instances": {"dc": {"component": "coupler", "settings": {"coupling": kappa2}},
               "loop": {"component": "waveguide",
                        "settings": {"length": 2 * np.pi * radius, "loss_db_cm": loss_db_cm}}},
 "connections": {"dc,out1": "loop,in0", "loop,out0": "dc,in1"},
 "ports": {"in": "dc,in0", "through": "dc,out0"}}
```

`ring_kappa2` gives the coupling for each gap from the femwell-fitted coupler model of Chapter 9, as the ring demo does, and `resonance` finds the dip nearest 1550 nm, then samples ±200 pm around it in steps of 0.01 pm and interpolates where the dip is half its depth. The script also has the ring as a single compact model, `ring`: the closed form of Section 12.2 for the through field, $$(t - w)/(1 - tw)$$ with $$w = a\,e^{-j\phi}$$ the loop's transmission. Comparing the two checks the netlist and the formula against each other.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint C</div>

| Gap | κ² | $$t$$ | Regime | FWHM | Loaded Q | Extinction |
|---|---|---|---|---|---|---|
| 200 nm | 1.23 % | 0.99381 | over-coupled | 22.3 pm | 69 400 | 4.1 dB |
| 250 nm | 0.52 % | 0.99742 | over-coupled | 11.8 pm | 131 900 | 11.0 dB |
| 300 nm | 0.22 % | 0.99892 | under-coupled | 7.4 pm | 210 700 | 16.7 dB |

Table 12.1: 1.23, 0.52 and 0.22 %; 22.3, 11.7 and 7.4 pm; 70 000, 132 000 and 211 000; 4.1, 11.0 and 16.7 dB. The measured widths equal the formula of Section 12.4 to the digits shown. The resonance is at 1551.398 nm, and the next ones 9.11 nm below and 9.22 nm above it; $$\lambda^2/(n_gL)$$ is 9.15 nm at 1550 nm (Chapter 12: 9.15 nm). The closed-form model and the circuit differ by at most $$3.6\times10^{-11}$$ from 1535 to 1565 nm ($$3.8\times10^{-14}$$ with `--numpy`): the formula and the netlist are the same ring.

</div>

The 250 nm width is 11.8 pm here and 11.7 pm in Table 12.1 because the width grows as $$\lambda^2$$, and the table evaluates the formula at 1550.0 nm while this resonance is at 1551.4 nm: 11.74 against 11.76 pm. Panel (b) of the figure shows the three dips: the over-coupled 200 nm ring is broad and shallow, the slightly under-coupled 300 nm ring narrow and deep.

## <span class="secnum">L4.4</span>The add-drop ring

A second coupler on the far side of the ring turns it into a band-pass filter (Section 12.3). `adddrop_netlist` builds it from two couplers and two half rings; light runs round the ring from each coupler's `in1` to its `out1`, and the drop port is the second coupler's `out0`.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint D</div>

With 250 nm gaps on both sides and 2 dB/cm, the drop port peaks at −2.14 dB (the formula of Section 12.3: −2.14 dB), and the through port falls to −13.2 dB on resonance. The drop peak is 19.3 pm wide, a loaded Q of 80 350. From the all-pass ring of the same gap, each coupler alone has $$Q_c = 205\,600$$, and with $$Q_i = 367\,600$$, $$1/Q_L = 1/Q_i + 2/Q_c$$ predicts 80 350.

</div>

The second coupler adds a second way out of the ring, so the add-drop ring is wider than the all-pass ring of the same gap, 19.3 against 11.8 pm. A lossless add-drop ring with equal couplers would drop everything on resonance. Here 61 % is dropped and 5 % passes the through port, so the ring itself absorbs and scatters 34 %. Stronger coupling (a narrower gap) gets the light out before it is lost, at the price of a wider peak.

## <span class="secnum">L4.5</span>A two-stage lattice filter

`lattice_netlist` cascades three couplers with delays of $$\Delta L$$ and $$2\Delta L$$ in the upper arm, as the 2-stage lattice of the Chapter 30 demo does, with its suggested couplings of 78, 84 and 70 %. `flat_top` measures the cross port's passband around its highest point near 1550 nm, down to 1 dB below it, interpolating the edges as the demo does.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint E</div>

The lattice's passband is 2.88 nm wide within 1 dB, against 1.73 nm for the plain MZI (Chapter 30 demo: 2.9 and 1.7 nm). It has two peaks at −0.21 dB with a 0.94 dB dip between them, and its null reaches −20.8 dB (Chapter 30 demo: a −20 dB stop band). Each edge falls from −1 to −10 dB in 0.95 nm, against 1.42 nm for the MZI, but the lattice stays below −10 dB for only 0.95 nm of each 5.75 nm period, against 1.18 nm for the MZI.

</div>

A flatter top and steeper edges, in the same period: that is what the second stage buys (Section 11.5). It pays with a narrower stop band and a 0.94 dB ripple across the top, and the null is only 20.8 dB deep. Couplings chosen together, by a filter-design method or an optimiser, trade these against each other; Exercise 5 shows how quickly the response degrades when the couplers drift.

## <span class="secnum">L4.6</span>The same netlist in plain NumPy

What does SAX do with a netlist? `np_circuit` does the same job in about thirty lines. Give every port of every instance an index, and write the waves going into the ports as $$a$$ and those coming out as $$b$$. Together the instances give $$b = Sa$$, with $$S$$ block-diagonal, one block per instance. A connection between ports $$u$$ and $$v$$ says that what leaves one enters the other, $$a_u = b_v$$ and $$a_v = b_u$$, or $$a_\mathrm{i} = Pb_\mathrm{i}$$ for all the internal ports, with $$P$$ a permutation matrix. Split $$S$$ into internal (i) and external (e) ports and eliminate the internal waves:

$$S_\mathrm{circuit} = S_\mathrm{ee} + S_\mathrm{ei}\,P\,(I - S_\mathrm{ii}P)^{-1}\,S_\mathrm{ie}.$$

```python
X = np.linalg.solve(np.eye(len(internal)) - Sii @ P, Sie)
Sc = See + Sei @ P @ X
```

The inverse sums every path the light can take between the external ports, including any number of trips round a loop, so rings need nothing special. NumPy solves it for all wavelengths at once. SAX's default backend does the same algebra with a sparse solver, KLU, and JAX can differentiate through it, which is what an optimiser needs.

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Checkpoint F</div>

Over 1545–1555 nm, the largest difference between SAX and `np_circuit`, over all S-parameters, is $$5.7\times10^{-14}$$ for the MZI, $$2.3\times10^{-13}$$ for the lattice, $$3.3\times10^{-11}$$ for the all-pass ring and $$1.3\times10^{-11}$$ for the add-drop ring: rounding error, slightly larger near the rings' sharp resonances. Run with `--numpy` and every checkpoint above prints the same digits; only the rounding-level difference of Checkpoint C changes.

</div>

<figure id="fig-l4-1">
  <img src="{{ '/assets/figs/lab04_expected.png' | relative_url }}" style="width:760px" alt="Four plots from the lab script: bar and cross transmission of an unbalanced MZI from 1530 to 1570 nanometres; the through-port dips of three all-pass rings with 200, 250 and 300 nanometre gaps; the through and drop ports of an add-drop ring around one resonance; and the cross port of a two-stage lattice filter against a plain MZI">
  <figcaption><span class="capnum">Figure L4.1.</span> <strong>What the script draws.</strong> (a) The MZI with \(\Delta L = 100\) µm: complementary outputs with a 5.75 nm period. (b) The all-pass rings of Table 12.1 around their resonance at 1551.40 nm. (c) The add-drop ring with 250 nm gaps: drop and through ports, against the all-pass ring of the same gap (dashed). (d) Cross port of the 2-stage lattice (78/84/70 %) against the plain MZI; dotted lines at −1 and −20 dB.</figcaption>
</figure>

## Exercises

1. **Unequal couplers.** Keep the first coupler at 50 % and set the second to 55 % and then 60 % (`mzi_netlist(100.0, 0.5, 0.55)`). What extinction ratio does the cross port reach, and the bar port? Compare with Worked Example 11.1.
2. **An interleaver.** Worked Example 11.2 needs an FSR of 6.4 nm to separate the 400 GHz channels of the reference link. Find $$\Delta L$$, simulate it, and measure the FSR near 1550 nm.
3. **Under or over?** Section 12.5 says one through-port spectrum cannot tell $$(a, t)$$ from $$(t, a)$$. Take the 300 nm ring ($$t = 0.99892$$, $$a = 0.99855$$) and build its twin: a coupler with $$\kappa^2 = 1 - a^2$$ and a loop loss that gives $$a = 0.99892$$. Compare the two through-port spectra, then their phases, then the drop ports of add-drop versions of each.
4. **Critical coupling.** Worked Example 12.1 says the 250 nm ring would be critically coupled at 3.6 dB/cm. Find the loss at which its dip is deepest, by formula and by scanning `loss_db_cm` in `allpass_netlist`. What are the width and Q there?
5. **Couplers that drift.** Chapter 9's 3 dB coupler crosses 43.5 % at 1530 nm and 57 % at 1570 nm, about 0.35 % per nanometre. Give `coupler` a slope, `coupling + 3.5 * (wl - 1.55)`, and evaluate the MZI and the lattice near 1530, 1550 and 1570 nm. What happens to the nulls of each port and to the lattice's flat top?

<details markdown="1">
<summary>Answers</summary>

1. At 55 % both ports reach 26.0 dB, and at 60 % both reach 19.9 dB, as the formula of Section 11.2 gives (Worked Example 11.1: 26 and 20 dB). With a perfect first coupler the bar port suffers as much as the cross port: its nulls are perfect only when $$\kappa_1^2 + \kappa_2^2 = 1$$, and here that sum is 1.05 or 1.10.
2. $$\Delta L = 1.55^2/(4.18 \times 0.0064) = 89.8$$ µm (Worked Example 11.2: 90 µm). The bar port's nulls around 1550 nm are 6.36 and 6.41 nm apart: 6.4 nm, as designed. But the period alone does not make an interleaver: at the four channels of the reference link the bar port transmits −1.3, −5.7, −1.3 and −5.6 dB and the cross port −5.8, −1.4, −5.7 and −1.4 dB, only about 4.4 dB apart, because the fringes are not centred on the grid. A phase shifter on one arm (Section 11.4) slides them into place, which is why interleavers are tuned after fabrication.
3. The twin has $$\kappa^2 = 0.289$$ % and a loop loss of 1.490 dB/cm. The two through-port spectra differ by at most $$8\times10^{-14}$$, both 16.70 dB deep: no fit can tell them apart. The phase can: across the resonance, the under-coupled ring's phase swings by 1.68 rad and comes back, while the over-coupled twin's turns through a whole circle (6.20 rad on this grid, $$2\pi$$ in the limit). So can a drop port: built as add-drop rings with two identical couplers each, the original drops −4.46 dB in a 10.51 pm peak and the twin −2.75 dB in 11.58 pm, because the twin loses less in its ring.
4. Critical coupling needs $$a = t = \sqrt{1 - 0.005159} = 0.997417$$, a loss of 3.575 dB/cm (Worked Example 12.1: 3.6 dB/cm). Scanning in steps of 0.05 dB/cm, the dip is deepest between 3.55 and 3.6 dB/cm (49 dB); at exactly 3.575 dB/cm it is 71.6 dB deep, 15.09 pm wide, with $$Q_L = 102\,800$$, half the intrinsic Q at that loss, $$2.06\times10^5$$, as Section 12.4 says it must be.
5. In the MZI the two couplers drift together, so they stay equal and the cross port keeps perfect nulls everywhere; but $$\kappa_1^2 + \kappa_2^2$$ moves away from 1, and the bar port's nulls fill in from −42 dB near 1550 nm to −17.9 dB near 1530 nm and −18.9 dB near 1570 nm. The lattice degrades faster. Near 1530 nm the dip in its passband deepens to −1.6 dB, so its flat top within 1 dB collapses to 1.07 nm, and its nulls rise to −14.3 and −17.7 dB; near 1570 nm the top is 3.17 nm wide, but the stop band only reaches −10.2 and −8.2 dB. Wavelength-dependent coupling is why broadband lattice filters use couplers designed to drift less, such as MMIs or bent couplers, or tune each stage.

</details>

## Going further

- Fit a compact model to a solver: replace the fixed coupling with $$\sin^2(\pi L\,\Delta n(\lambda)/\lambda)$$ from femwell's supermodes ([Lab 2]({% link labs/lab02_femwell.md %}), Chapter 9) and the waveguide's 2.446 and 4.18 with a polynomial in wavelength.
- Optimise: SAX circuits are JAX functions, so `jax.grad` gives the derivative of, say, the lattice's passband ripple with respect to its three couplings. Find couplings that give a 3 nm flat top with less than 0.5 dB of ripple.
- Lay the circuits out with gdsfactory and ubcpdk ([Section 30.4]({% link chapters/30_flow.md %})), and simulate them from the layout's own netlist, with the PDK's compact models in place of these ones.
- [Lab 11]({% link labs/lab11_vernier.md %}) uses two rings like these as the mirror of a tunable laser.

