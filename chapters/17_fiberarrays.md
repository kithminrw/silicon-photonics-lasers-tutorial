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

A **fibre array** holds several fibres in precise, parallel positions. The fibres are stripped to their 125 µm glass cladding and laid in **V-grooves**, etched in silicon (where the crystal planes give walls at exactly 54.7°) or machined in glass. A lid is glued on top and the end face is polished. The groove pitch is usually **127 µm**, just over one cladding diameter, so that neighbouring fibres do not touch; arrays with 250 µm pitch carry fibres with their coating left on. The grooves place each core within a fraction of a micrometre of its nominal position, so a whole row of couplers on the chip can be aligned at once.

For grating couplers the array meets the chip at the coupler's angle, about 8° from vertical ([Chapter 15]({% link chapters/15_gc.md %})). Its end face is **polished at that angle**, so that the face is parallel to the chip and every fibre sits at the same height. Low-profile arrays instead polish the fibres at about 40° and use total internal reflection at the polished face to turn the light through 90°, so the array can lie flat on the chip. For edge couplers the array butts against the polished chip facet ([Chapter 16]({% link chapters/16_edge.md %})).

Grating couplers accept one polarisation. A standard fibre scrambles polarisation, so test arrays often use **polarisation-maintaining (PM) fibres**, whose stress rods hold linearly polarised light along one axis. The rods are aligned to the grooves, so every fibre delivers TE light to its coupler.

The layout on the chip must match the array: couplers on the 127 µm grid, all facing the same way, and a **loopback**, the two outermost couplers joined by a waveguide. The loopback is aligned first: when its power peaks, the whole array is aligned, because the other fibres share its rigid geometry.

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

**Finding the peak.** Far from a coupler the power meter reads only noise, so there is no gradient to follow. Alignment therefore runs in two phases. **First light** comes from a blind search, typically a spiral whose pitch is smaller than the mode diameter. Then **optimisation** climbs the gradient: hill-climbing in steps that halve as the peak approaches, or gradient and model-fitting methods that fit a Gaussian to a few measured points and jump to its centre. Automated test stations add the angles, the gap and the rotation of the array, and align input and output together through a loopback. With a calibrated stage and a known chip position, the first-light search can be skipped altogether, which is what makes wafer-scale testing fast ([Chapter 31]({% link chapters/31_testing.md %})).

**Try it.** Find the peak with as few moves as possible, then let the automatic spiral and hill-climb do it.

{% include demos/align.html %}

## <span class="secnum">17.3</span>Attaching fibres

To make a permanent package, the aligned array is glued to the chip, usually with a **UV-curable epoxy** that hardens in seconds once the alignment is right. Three things then matter {% include cite.html keys="carroll2016" %}:

- **Shrinkage.** The epoxy shrinks as it cures and can pull the fibre by up to a micrometre or so, which is serious for edge coupling with sub-micrometre tolerances. Assemblers pre-offset the fibre, use thin bond lines and low-shrinkage adhesives, or keep the power monitored and correct during the cure.
- **The optical path.** An index-matched epoxy in the gap removes the facet reflections and lengthens the Rayleigh range; an epoxy outside the path holds the array mechanically and keeps the optical gap clean.
- **Reliability.** The bond must hold the alignment through temperature cycles, humidity and years of service. Passive optical components are qualified against standards such as Telcordia GR-1221.

## <span class="secnum">17.4</span>Photonic wire bonds and micro-optics

Active alignment with sub-micrometre precision is slow and expensive. **Photonic wire bonds** remove it. The chip and fibre are fixed roughly in place, the actual positions of their waveguide ends are measured with a camera, and a polymer waveguide is written between them in three dimensions by two-photon lithography. Its shape follows whatever path is needed {% include cite.html keys="lindenmann2012" %}. The same technique prints **free-form micro-optics** directly onto facets: lenses and mirrors that reshape and redirect the beam of a laser or a fibre. Coupling efficiencies up to 88 % between an InP laser and a single-mode fibre have been reported this way {% include cite.html keys="dietrich2018" %}. Both relax the alignment from sub-micrometre to a few micrometres and suit hybrid assemblies of chips from different platforms.

## <span class="secnum">17.5</span>Laser and chip assembly

A silicon chip needs a light source, an electrical connection and, often, temperature control:

- **Laser attach.** A III-V laser die can be **flip-chip** bonded face down onto the silicon chip, its height set by lithographically defined pedestals and its position by alignment marks, so that its facet butts against an edge coupler. Alternatively a micro-optical bench of ball lenses and an isolator couples a packaged laser, or the laser is integrated on the wafer ([Chapter 27]({% link chapters/27_lasersonsi.md %})).
- **Electrical.** Wire bonds or flip-chip bumps connect modulators and photodiodes to their drivers and amplifiers. At tens of gigabits per second the length of every connection matters, which is why driver chips sit next to, or on top of, the photonic chip ([Chapter 33]({% link chapters/33_links.md %})).
- **Thermal.** Rings and lasers drift with temperature ([Chapter 18]({% link chapters/18_thermal.md %})), so packages include heaters, thermistors and sometimes thermo-electric coolers.

## <span class="secnum">17.6</span>Co-packaged optics

In a data centre switch today, the optics live in **pluggable modules** on the front panel, and the electrical signals travel tens of centimetres across the circuit board to reach them. As switch bandwidths grow, driving those traces costs a large share of the power. **Co-packaged optics** moves the photonic chips onto the same package as the switch chip, shortening the electrical links to millimetres and lowering the energy per bit. The lasers often stay in a replaceable external module at the front panel and feed the package through fibre, because lasers are the part most likely to fail. The difficulties are packaging ones: attaching hundreds of fibres reliably, testing chips before they are committed to an expensive package, and keeping the optics cool beside a hot processor.

## <span class="secnum">17.7</span>Design rules for test and packaging

Chips that will be tested automatically and packaged by someone else follow **design-for-test** and **design-for-packaging** rules. In the SiEPIC flow used by the openEBL runs {% include cite.html keys="siepictools,openebl" %}, the rules include:

- grating couplers on a 127 µm pitch, arranged in a vertical column and all facing the same way, so that one fibre array reaches them;
- a text label at the input coupler of each circuit, naming the measurement (wavelength, polarisation, device), which the automated test station reads to know where to align and what to sweep;
- a limited number of couplers above and below the labelled input, matching the fibres of the array.

Packaging houses publish similar templates: edge couplers at fixed positions along a polished edge, keep-out zones near the facet, bond pads on a standard pitch along the other edges, and the fibre-array footprint on a fixed grid. Following a template from the start lets a chip go to a standard package without a custom design.

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
