---
title: Preface
nav_order: 1
permalink: /preface/
chapter: 0
---

# Preface

Photonics is easiest to learn when you can change a number and watch what the light does.
{: .chapterlead }

## Who this is for

This tutorial is for undergraduate and early-graduate engineers and physicists who want to design photonic integrated circuits, and for electronics designers who want to understand the optical half of an electronic–photonic system. You need the electromagnetics and semiconductor physics of a first engineering degree and enough Python to run a script. Everything else is built up from there.

It is also a set of notes written while learning: the organisation follows the order in which the ideas are needed to design, make and measure a chip, not the order of a physics course.

## What you will be able to do

- solve for the modes of slab and channel waveguides and choose a waveguide cross-section on SOI, SiN, TFLN and other platforms;
- design the passive building blocks: couplers, splitters, interferometers, rings, gratings and multiplexers;
- couple light between fibres and chips and budget the losses;
- choose and size phase shifters, modulators and detectors;
- explain how a semiconductor laser works, from gain to linewidth, and how lasers are integrated with silicon;
- lay out a chip with open tools, have it fabricated through an open MPW run, and extract physical parameters from the measured data.

## How each chapter works

Every chapter opens with what you will learn and the design question it answers. Each concept then follows the same pattern: a short derivation, a worked example with real numbers, and a *what this means for your design* box. Coloured boxes mark key equations, worked examples, pitfalls and things to try.

Most chapters have an **interactive demo**: a navy panel with sliders that runs a small model of the device in your browser. The demos are deliberately simple models, chosen so that you can see the physics; where a design needs a full simulation, the chapter says so and the labs show how. Where a free simulation by someone else already does the job well, the chapter links to it in an *Explore further* box.

The **[PDK devices in 3D]({% link devices-3d.md %})** page shows real devices from open process design kits as rotatable 3D models, with credit to the people who designed them.

## Two running examples

**Your first chip** is a passive chip in 220 nm SOI at 1550 nm with grating couplers on a 127 µm pitch, of the kind made in the SiEPIC openEBL runs {% include cite.html keys="openebl" %}. The labs lay it out, verify it and analyse the measurements, so that you go through a whole design–fabrication–test cycle with free tools.

**The reference link** is a four-wavelength WDM transmitter and receiver: lasers, modulators, a multiplexer, a fibre, a demultiplexer and photodetectors. Chapter 1 sets its draft targets, Parts V and VI design its active blocks, and Chapter 33 closes its power budget.

## Reading paths

- **Physics first:** Parts I and II, then the passive devices of Part III and the lasers of Part VI.
- **Chip designer:** Chapters 1, 4, 5 and 6, then Parts III and IV, Chapter 30 (design flow) and Chapter 32 (data analysis), with the labs.
- **Lasers:** Chapters 1–4, then Part VI from Chapter 22, with Chapters 12–13 (rings and gratings) for the tunable lasers of Chapter 26.
- **Test and measurement:** Chapters 7, 12, 15 and 17, then Chapters 31 and 32.

## Open material only

The tutorial is open (text and figures CC BY 4.0, code MIT), and it uses only material that its authors have published openly or that is licensed for reuse: open-source PDKs and tools, open-access papers, and public datasets. Textbooks, courses and papers that are not open are cited and linked, never copied. Commercial PDKs are described only from what their owners have made public. If you think something here should be credited differently, please tell us.

## Acknowledgements

The organisation of this tutorial owes much to Lukas Chrostowski and Michael Hochberg's *Silicon Photonics Design* {% include cite.html keys="chrostowski2015" %} and the UBC edX course built around it {% include cite.html keys="phot1x" %}, to the SiEPIC program's open PDK and openEBL runs {% include cite.html keys="ebeampdk,openebl" %}, to the AIM Photonics Academy courses and the MIT virtual-lab simulations {% include cite.html keys="aimacademy,vmlab" %}, to the gdsfactory community's open PDKs {% include cite.html keys="gdsfactory" %}, and to Mustafa Hammood's browser tools {% include cite.html keys="mustafash" %}. Any mistakes are ours.
