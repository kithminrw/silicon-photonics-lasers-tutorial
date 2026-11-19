---
title: "17. Fibre Arrays, Photonic Wire Bonds and Packaging"
parent: "Part IV · Coupling and Packaging"
nav_order: 17
permalink: /part-4/ch17/
chapter: 17
---

# <span class="chapnum">Chapter 17</span>Fibre Arrays, Photonic Wire Bonds and Packaging

Much of a photonic chip's cost is in getting light in and out reliably; this chapter is about the hardware that does it.
{: .chapterlead }

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn to</div>

- describe fibre arrays: V-grooves, 127 µm pitch, polish angle, PM fibres;
- lay out couplers for a fibre array, with loopbacks and test labels;
- derive alignment tolerances from Gaussian overlap, and compare search algorithms;
- describe fibre attach, photonic wire bonds and 3D-printed micro-optics;
- outline laser attach, co-packaged optics and design-for-packaging rules.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How tolerant is a coupling interface, and how do you find the peak quickly?

</div>

## <span class="secnum">17.1</span>Fibre arrays

A **fibre array** holds several fibres in precise, parallel positions. The fibres are stripped to their 125 µm glass cladding and laid in **V-grooves**, etched in silicon (where the crystal planes give walls at exactly 54.7°) or machined in glass. A lid is glued on top and the end face is polished. The groove pitch is usually **127 µm**, just over one cladding diameter, so that neighbouring fibres do not touch; arrays with 250 µm pitch carry fibres with their coating left on. The grooves place each core within a fraction of a micrometre of its nominal position, so a whole row of couplers on the chip can be aligned at once ([Figure 17.1](#fig-17-1)).

<figure id="fig-17-1">
  <img src="{{ '/assets/figs/ch17_vgroove.svg' | relative_url }}" style="width:600px" alt="To-scale cross-section of an eight-fibre array: 125 micrometre fibres with 8.2 micrometre cores resting in V-grooves etched in silicon on a 127 micrometre pitch, groove walls at 54.7 degrees, a glass lid pressed on top and epoxy filling the gaps">
  <figcaption><span class="capnum">Figure 17.1.</span> <strong>An eight-fibre V-groove array in cross-section, to scale.</strong> Fibres stripped to their 125 µm cladding (core 8.2 µm) {% include cite.html keys="itug652" %} lie in grooves etched in silicon on a 127 µm pitch, 2 µm apart. The groove walls are {111} crystal planes at 54.7° to the surface; with 120 µm openings (illustrative) the grooves are 85 µm deep and each fibre centre sits 23 µm above the surface, so a glass lid pressed onto the fibres and epoxy hold them. The lid and chip thicknesses are illustrative. Drawn by <code>figsrc/ch17_figs.py</code>.</figcaption>
</figure>

For grating couplers the array meets the chip at the coupler's angle, about 8° from vertical ([Chapter 15]({% link chapters/15_gc.md %})). Its end face is **polished at that angle**, so that the face is parallel to the chip and every fibre sits at the same height. Because the face is flat, the light refracts as it leaves the glass: an array polished at 8° launches at about 11.6° in air, so a coupler designed for a cleaved fibre at 8° in air (Worked Example 15.1) needs fibres polished at about 5.5°, or a design for the steeper beam. Low-profile arrays instead polish the fibres at about 40° and use total internal reflection at the polished face to turn the light through about 80–85°, so the array can lie flat on the chip ([Figure 17.2](#fig-17-2)). For edge couplers the array butts against the polished chip facet ([Chapter 16]({% link chapters/16_edge.md %})).

<figure id="fig-17-2">
  <img src="{{ '/assets/figs/ch17_arrays.svg' | relative_url }}" style="width:600px" alt="Two schematic side views of fibre arrays over a grating coupler. a: fibres held at 8 degrees from vertical between a V-groove chip and a lid, the end face polished parallel to the chip, the beam refracting to 11.6 degrees in the air gap. b: a low-profile array lying flat, its fibre end polished at 41 degrees so that total internal reflection sends the light down at 8 degrees from vertical">
  <figcaption><span class="capnum">Figure 17.2.</span> <strong>Fibre arrays over grating couplers (schematic, angles to scale).</strong> (a) Fibres held at 8° from the vertical with the end face polished parallel to the chip. Because the face is flat, the light refracts as it leaves the glass, \(\sin\theta_\mathrm{air} = 1.444\sin 8°\): it crosses an air gap at 11.6° and reaches the oxide at 8° again. Filling the gap with index-matching epoxy removes the reflections but not the tilt, since \(n\sin\theta\) is the same in every flat layer; so the coupler is designed for the angle the light actually has, or the fibres are polished at about 5.5°. (b) A low-profile array lies flat; its fibres end in a face polished at about 41°, where total internal reflection (incidence 49°, beyond silica's 43.8° critical angle in air) turns the light down at 8° from the vertical inside the glass, 11.6° once it leaves into air (a 42° polish would give 8° in air). Drawn by <code>figsrc/ch17_figs.py</code>.</figcaption>
</figure>

Grating couplers accept one polarisation. A standard fibre scrambles polarisation, so test arrays often use **polarisation-maintaining (PM) fibres**, whose stress rods hold linearly polarised light along one axis. The rods are aligned to the grooves, so every fibre delivers TE light to its coupler.

The layout on the chip must match the array ([Figure 17.6](#fig-17-6)): couplers on the 127 µm grid, all facing the same way, and a **loopback**, the two outermost couplers joined by a waveguide. The loopback is aligned first: when its power peaks, the whole array is aligned, because the other fibres share its rigid geometry.

## <span class="secnum">17.2</span>Alignment

**Tolerances from Gaussian overlap.** The coupling between two Gaussian modes of 1/e² radii $$w_1$$ and $$w_2$$, offset laterally by $$d$$ or tilted by $$\theta$$ in a medium of index $$n$$, follows from their overlap integral ([Chapter 3]({% link chapters/03_gaussian.md %})) {% include cite.html keys="kogelnik1966" %}:

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Misalignment loss of two Gaussian modes</div>

$$\eta = \left(\frac{2w_1w_2}{w_1^2 + w_2^2}\right)^2 \exp\!\left(-\frac{2d^2}{w_1^2 + w_2^2}\right) \exp\!\left(-\frac{2\pi^2n^2\theta^2}{\lambda^2}\,\frac{w_1^2w_2^2}{w_1^2 + w_2^2}\right)$$

</div>

The 1 dB offset is $$d_\mathrm{1dB} = \sqrt{0.115\,(w_1^2 + w_2^2)}$$: tolerance grows with the mode size. The tilt term is the reverse: a large mode has a narrow far field, so it is sensitive to angle. A gap between the two waists adds a third loss, because the beam spreads over a Rayleigh range $$z_R = \pi nw^2/\lambda$$ ([Chapter 3]({% link chapters/03_gaussian.md %})).

<div class="tbox tbox-example" markdown="1">
<div class="tbox-title">Worked Example 17.1 · Grating against edge coupling</div>

A fibre over a grating coupler: $$w_1 = 5.2$$ µm (SMF-28) and $$w_2 \approx 4.6$$ µm (the coupler's beam). Then $$d_\mathrm{1dB} = \sqrt{0.115 \times (27.0 + 21.2)} = 2.35$$ µm, and a gap of 10 µm in air costs only 0.05 dB. A lensed fibre on an inverse taper, both with 2.5 µm spots ($$w = 1.25$$ µm), gives $$d_\mathrm{1dB} = \sqrt{0.115 \times 3.1} = 0.60$$ µm, four times tighter; its Rayleigh range in air is only 3.2 µm, so a 3 µm gap already costs 0.9 dB. For an array, rotation adds up along its length. The two outer fibres of an eight-fibre array are 7 × 127 = 889 µm apart, so a rotation of 2.35/889 rad = 0.15° costs the outer coupler 1 dB with gratings, and only 0.04° with small edge spots.

</div>

**Try it.** Choose a preset and move the fibre off its peak in offset, tilt and gap; the curves show how fast the coupling falls along each axis.

{% include demos/couple.html %}

**Finding the peak.** Far from a coupler the power meter reads only noise, so there is no gradient to follow. Alignment therefore runs in two phases. **First light** comes from a blind search, typically a spiral whose pitch is smaller than the mode diameter. Then **optimisation** climbs the gradient: hill-climbing in steps that halve as the peak approaches, or gradient and model-fitting methods that fit a Gaussian to a few measured points and jump to its centre. Automated test stations add the angles, the gap and the rotation of the array, and align input and output together through a loopback. With a calibrated stage and a known chip position, the first-light search can be skipped altogether, which is what makes wafer-scale testing fast ([Chapter 36]({% link chapters/36_testing.md %})).

**Try it.** Find the peak with as few moves as possible, then let the automatic spiral and hill-climb do it.

{% include demos/align.html %}

## <span class="secnum">17.3</span>Attaching fibres

To make a permanent package, the aligned array is glued to the chip, usually with a **UV-curable epoxy** that hardens in seconds once the alignment is right. Three things then matter {% include cite.html keys="carroll2016" %}:

- **Shrinkage.** The epoxy shrinks as it cures and can pull the fibre by up to a micrometre or so, which is serious for edge coupling with sub-micrometre tolerances. Assemblers pre-offset the fibre, use thin bond lines and low-shrinkage adhesives, or keep the power monitored and correct during the cure.
- **The optical path.** An index-matched epoxy in the gap removes the facet reflections and lengthens the Rayleigh range; an epoxy outside the path holds the array mechanically and keeps the optical gap clean.
- **Reliability.** The bond must hold the alignment through temperature cycles, humidity and years of service. Passive optical components are qualified against standards such as Telcordia GR-1221.

## <span class="secnum">17.4</span>Photonic wire bonds and micro-optics

Active alignment with sub-micrometre precision is slow and expensive. **Photonic wire bonds** remove it. The chip and fibre are fixed roughly in place, the actual positions of their waveguide ends are measured with a camera, and a polymer waveguide is written between them in three dimensions by two-photon lithography. Its shape follows whatever path is needed ([Figure 17.3](#fig-17-3)) {% include cite.html keys="lindenmann2012" %}. The same technique prints **free-form micro-optics** directly onto facets: lenses and mirrors that reshape and redirect the beam of a laser or a fibre. Coupling efficiencies up to 88 % between an InP laser and a single-mode fibre have been reported this way {% include cite.html keys="dietrich2018" %}. Both relax the alignment from sub-micrometre to a few micrometres and suit hybrid assemblies of chips from different platforms.

<figure id="fig-17-3">
  <img src="{{ '/assets/figs/ch17_pwb.svg' | relative_url }}" style="width:600px" alt="Two schematic side views. a: an InP laser and a silicon chip on a common submount joined by an arched polymer waveguide, a photonic wire bond, from the laser's active region to the silicon waveguide. b: a laser with a printed lens on its facet and a fibre with a printed lens on its end, the beam widened in the gap between them">
  <figcaption><span class="capnum">Figure 17.3.</span> <strong>A photonic wire bond and printed micro-optics (schematic).</strong> (a) An InP laser and a silicon chip are fixed on a submount without precise alignment; a polymer waveguide written in three dimensions by two-photon lithography joins the laser's active region to the silicon waveguide wherever they actually are. (b) Lenses printed on a laser facet and on a fibre end widen the beam in the gap, which relaxes the alignment. Drawn by <code>figsrc/ch17_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">17.5</span>Laser and chip assembly

A silicon chip needs a light source, an electrical connection and, often, temperature control:

- **Laser attach.** A III-V laser die can be **flip-chip** bonded face down onto the silicon chip, its height set by lithographically defined pedestals and its position by alignment marks, so that its facet butts against an edge coupler ([Figure 17.4](#fig-17-4)). Alternatively a micro-optical bench of ball lenses and an isolator couples a packaged laser, or the laser is integrated on the wafer ([Chapter 27]({% link chapters/27_lasersonsi.md %})).
- **Electrical.** Wire bonds or flip-chip bumps connect modulators and photodiodes to their drivers and amplifiers. At tens of gigabits per second the length of every connection matters, which is why driver chips sit next to, or on top of, the photonic chip ([Chapter 38]({% link chapters/38_links.md %})).
- **Thermal.** Rings and lasers drift with temperature ([Chapter 18]({% link chapters/18_thermal.md %})), so packages include heaters, thermistors and sometimes thermo-electric coolers.

<figure id="fig-17-4">
  <img src="{{ '/assets/figs/ch17_flipchip.svg' | relative_url }}" style="width:600px" alt="Schematic cross-section of a III-V laser die bonded epitaxy-down into a recess etched in a silicon photonic chip, resting on pedestals with solder between, its active region level with the silicon waveguide at the recess wall, where the light enters an edge coupler">
  <figcaption><span class="capnum">Figure 17.4.</span> <strong>A flip-chip laser on a silicon chip (schematic, layers exaggerated).</strong> The III–V die is bonded epitaxy-down into a recess etched into the PIC. It rests on pedestals whose height places its active region level with the silicon waveguide, and solder makes the electrical contact; alignment marks set the lateral position. The light butt-couples into an edge coupler at the recess wall. Drawn by <code>figsrc/ch17_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">17.6</span>Co-packaged optics

In a data centre switch today, the optics live in **pluggable modules** on the front panel, and the electrical signals travel tens of centimetres across the circuit board to reach them. As switch bandwidths grow, driving those traces costs a large share of the power. **Co-packaged optics** moves the photonic chips onto the same package as the switch chip ([Figure 17.5](#fig-17-5)), shortening the electrical links to millimetres and lowering the energy per bit. The lasers often stay in a replaceable external module at the front panel and feed the package through fibre, because lasers are the part most likely to fail. The difficulties are packaging ones: attaching hundreds of fibres reliably, testing chips before they are committed to an expensive package, and keeping the optics cool beside a hot processor.

<figure id="fig-17-5">
  <img src="{{ '/assets/figs/ch17_cpo.svg' | relative_url }}" style="width:600px" alt="Two schematic top views of a switch board. a: pluggable modules at the front panel connected to the switch chip by long electrical traces. b: optical engines on the switch package around the switch chip, millimetres away, with fibres to the front panel and lasers in front-panel modules feeding the engines through fibre">
  <figcaption><span class="capnum">Figure 17.5.</span> <strong>Pluggable modules against co-packaged optics (schematic top views of a switch board).</strong> (a) Pluggable modules at the front panel, reached by electrical traces tens of centimetres long. (b) Co-packaged optics: optical engines (photonic chip and driver) on the switch package, millimetres from the switch chip; fibres run to the front panel, and lasers in replaceable front-panel modules feed the engines through fibre. Drawn by <code>figsrc/ch17_figs.py</code>.</figcaption>
</figure>

## <span class="secnum">17.7</span>Design rules for test and packaging

Chips that will be tested automatically and packaged by someone else follow **design-for-test** and **design-for-packaging** rules. In the SiEPIC flow used by the openEBL runs {% include cite.html keys="siepictools,openebl" %}, the rules include ([Figure 17.6](#fig-17-6)a):

- grating couplers on a 127 µm pitch, arranged in a vertical column and all facing the same way, so that one fibre array reaches them;
- a text label at the input coupler of each circuit, naming the measurement (wavelength, polarisation, device), which the automated test station reads to know where to align and what to sweep;
- a limited number of couplers above and below the labelled input, matching the fibres of the array.

Packaging houses publish similar templates ([Figure 17.6](#fig-17-6)b): edge couplers at fixed positions along a polished edge, keep-out zones near the facet, bond pads on a standard pitch along the other edges, and the fibre-array footprint on a fixed grid. Following a template from the start lets a chip go to a standard package without a custom design.

<figure id="fig-17-6">
  <img src="{{ '/assets/figs/ch17_layout.svg' | relative_url }}" style="width:600px" alt="a: to-scale top view of eight focusing grating couplers in a column on a 127 micrometre pitch under a fibre-array footprint, all facing the same way, with a loopback joining the top and bottom couplers, an add-drop ring and an MZI using the couplers between, and text labels such as opt_in_TE_1550_ring1 at each circuit's input. b: an illustrative packaging template with edge couplers along a polished edge, a keep-out zone and a fibre array there, and rows of bond pads along the other edges">
  <figcaption><span class="capnum">Figure 17.6.</span> <strong>Layout for test and packaging.</strong> (a) Eight focusing grating couplers on the 127 µm pitch of a fibre array, to scale, all facing the same way: a loopback joins the outermost pair, a ring and an MZI use the couplers between, and a text label at each circuit's input coupler, in the SiEPIC style, tells the automated station what to measure. (b) A packaging template (illustrative): edge couplers at fixed positions along the polished edge behind a keep-out zone, and bond pads on a standard pitch along the other edges. Drawn by <code>figsrc/ch17_figs.py</code>.</figcaption>
</figure>

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Your first chip</div>

Place every circuit's couplers on the 127 µm column of the fibre array, with a test label on each input and a loopback on the outermost pair. Keep the couplers away from the chip edge and from metal, and leave space for the fibre array's footprint above them.

</div>

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Explore further</div>

- [SiEPIC openEBL design repositories](https://github.com/SiEPIC), with example layouts that pass the design-for-test checks {% include cite.html keys="openebl" %}

</div>

## Reading

{% include reflist.html keys="carroll2016,marchetti2019,lindenmann2012,dietrich2018,kogelnik1966,chrostowski2015,openebl" %}

<div class="tbox tbox-takeaways" markdown="1">
<div class="tbox-title">Key takeaways</div>

- Fibre arrays hold fibres in V-grooves on a 127 µm pitch, angle-polished for grating couplers; PM fibres deliver one polarisation.
- The 1 dB lateral tolerance is $$\sqrt{0.115\,(w_1^2 + w_2^2)}$$: about ±2.4 µm for a grating coupler, ±0.6 µm for a lensed fibre on a taper.
- Large modes tolerate offsets but not tilt; small modes the reverse, and they diverge quickly across a gap.
- Alignment needs a blind search for first light, then hill-climbing; a loopback aligns a whole array.
- Epoxy shrinkage, reliability and the cost of active alignment drive packaging; photonic wire bonds and printed micro-optics relax it.
- Co-packaged optics moves the photonics next to the switch chip; design-for-test and packaging templates should be followed from the first layout.

</div>
