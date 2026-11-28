"""Write demos.md: every interactive demo, grouped by part and chapter, linked to the demo on its page.

Run from the repository root after adding or moving a demo:  python tools/make_demos_page.py
Names and one-line descriptions live in DESC below; a demo without an entry falls back to its aria-label.
"""
import os, re, sys

DESC = {
    'budget': ('Power budget', 'Follow one wavelength of the reference link from laser to receiver and see where the decibels go.'),
    'polar': ('Polarisation ellipse', 'Combine two field components with any amplitude and phase, and watch linear, circular and elliptical polarisation appear.'),
    'fresnel': ('Snell, Fresnel and total internal reflection', 'Reflection and transmission at an interface for both polarisations, with Brewster\'s angle and the critical angle.'),
    'packet': ('Wave packet', 'Phase and group velocity of a pulse travelling through a dispersive medium.'),
    'gaussian': ('Gaussian beam and lens', 'Focus a Gaussian beam into a fibre and see how waist, distance and wavefront curvature set the coupling.'),
    'fiber': ('Fibre modes', 'The guided modes of a step-index fibre against the V number, and the single-mode cut-off.'),
    'platforms': ('Platform comparator', 'Put two photonic platforms side by side: index contrast, loss, bend radius and what each can do.'),
    'slab': ('Slab-waveguide mode solver', 'Solve the TE and TM modes of an asymmetric slab and watch new modes appear as the film thickens.'),
    'eim': ('Effective-index explorer', 'Reduce a strip or rib waveguide to two slab problems and find where it turns multimode.'),
    'modesolver': ('Full-vectorial 2D mode solver', 'A finite-difference eigenmode solver running in your browser: effective and group index, field components and mode area of strips and ribs.'),
    'roughness': ('Sidewall-roughness scattering', 'How the field at the sidewalls sets the scattering loss, and why wider waveguides lose less.'),
    'cutback': ('Cutback simulator', 'Extract propagation loss from noisy measurements of waveguides of different lengths.'),
    'bend': ('Circular and Euler bends', 'Compare bend shapes, their curvature and the mode mismatch at the junctions.'),
    'adiabatic': ('Taper adiabaticity', 'Test a taper against the adiabatic criterion and see how its shape sets the length it needs.'),
    'dc': ('Directional coupler', 'Watch power move between two waveguides as the gap, length and wavelength change.'),
    'mmi': ('MMI self-imaging', 'Find the lengths at which a multimode section reproduces its input as one, two or more images.'),
    'mzi': ('Mach–Zehnder interferometer', 'Path difference, free spectral range and extinction of an unbalanced interferometer.'),
    'ring': ('Ring resonator', 'Exact through and drop spectra: coupling, loss, Q, extinction and critical coupling.'),
    'bragg': ('Bragg grating', 'The reflection spectrum of a waveguide grating by transfer matrices, with apodisation and phase shifts.'),
    'fp': ('Fabry–Pérot cavity', 'Two mirrors and many round trips: the Airy spectrum, finesse, Q, peak transmission and the approach to threshold, with the transmitted fields added up pass by pass.'),
    'demux': ('Four-ring demultiplexer', 'Separate the reference link\'s four wavelengths with cascaded rings, then heat, detune and lock them.'),
    'gc': ('Grating-coupler phase matching', 'Period, angle and wavelength of a grating coupler, and how the top cladding changes them.'),
    'gceff': ('Grating-coupler efficiency budget', 'Directionality, mode overlap and apodisation: where the light of a grating coupler goes.'),
    'taper': ('Inverse-taper edge coupler', 'Narrow a silicon tip to expand the mode and match it to lensed, high-NA or standard fibre.'),
    'couple': ('Alignment tolerance', 'Coupling between two Gaussian modes against lateral offset, tilt and gap.'),
    'align': ('Fibre-array alignment', 'Align a fibre array to two grating couplers by hand, as on a probe station.'),
    'faml': ('Facet-attached microlenses', 'Expand an edge coupler\'s mode with printed lenses and compare the alignment tolerances with a lensed fibre.'),
    'heater': ('Thermo-optic phase shifter', 'Heater power, temperature rise, phase and response time of a heated waveguide.'),
    'lock': ('Ring locking', 'Keep a ring on its laser line with a heater and a feedback loop while the room temperature drifts.'),
    'pn': ('PN depletion phase shifter', 'Doping, bias and junction position against phase efficiency, loss and capacitance.'),
    'pockels': ('Pockels phase shifter', 'Electrode gap, field overlap and push–pull drive of thin-film lithium niobate and barium titanate shifters.'),
    'mzm': ('MZM and eye diagram', 'Drive a Mach–Zehnder modulator at speed and watch the eye open and close.'),
    'ringmod': ('Ring modulator', 'Detuning, drive and Q of a silicon ring modulator: extinction, loss, linewidth and modulation bandwidth.'),
    'pdbw': ('Photodiode bandwidth', 'Transit time, capacitance and responsivity of a germanium photodiode.'),
    'rx': ('Receiver sensitivity', 'Noise, Q factor and bit-error ratio of an optical receiver.'),
    'levels': ('Level-system model', 'Pump two-, three- and four-level systems and see when inversion and gain appear.'),
    'gainspec': ('Gain spectrum', 'Semiconductor gain against carrier density and temperature.'),
    'laser': ('Laser rate equations', 'Light–current curve, switch-on transient and temperature of a Fabry–Pérot laser, with self-heating.'),
    'dyn': ('Modulation response, RIN and linewidth', 'Small-signal response, relative intensity noise and linewidth of a laser against bias.'),
    'vernier': ('Vernier ring laser', 'Tune a laser over a wide range with two rings of slightly different size.'),
    'hybrid': ('III–V/Si supermodes', 'How light is shared between III–V gain and silicon as the silicon width changes, drawn as signed fields.'),
    'soa': ('SOA gain and noise figure', 'Gain saturation and noise figure of a semiconductor optical amplifier.'),
    'circuit': ('Circuit simulator', 'Chain S-parameter models of couplers, delays and rings into circuits and see their spectra.'),
    'fdtd': ('FDTD in the browser', 'A real 2D finite-difference time-domain simulation: resolution, the Courant limit and absorbing boundaries.'),
    'wafer': ('Wafer-map Monte Carlo', 'Thickness and width variation across a wafer, and the ring wavelengths and heater power it costs.'),
    'wafermc': ('Wafer-map Monte Carlo', 'Thickness and width variation across a wafer, and the ring wavelengths and heater power it costs.'),
    'testbench': ('Virtual test bench', 'Sweep a laser across a ring and measure it as in the lab, with real instrument limits.'),
    'ringfit': ('Ring-fit playground', 'Fit ring spectra to extract loss and coupling, and meet the coupling ambiguity.'),
    'linkbudget': ('Link budget', 'Close the reference link\'s power budget with its penalties and margin.'),
    'biosensor': ('Ring biosensor', 'The shift of a ring resonance with the analyte\'s refractive index, and the limit of detection.'),
    'opa': ('Optical phased array', 'Steer a beam by setting the phases of an array of emitters.'),
}

def front(s):
    m = re.match(r'---\n(.*?)\n---', s, re.S)
    return dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.M)) if m else {}

def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chapters = sorted((f for f in os.listdir('chapters') if re.match(r'\d+_.*\.md$', f)), key=lambda f: int(f.split('_')[0]))
    parts, total, missing = [], 0, []
    for f in chapters:
        s = open('chapters/' + f, encoding='utf-8').read().replace('\r\n', '\n')
        fm = front(s)
        demos = re.findall(r'\{%\s*include demos/([a-z0-9_]+)\.html\s*%\}', s)
        if not demos: continue
        entries = []
        for d in demos:
            src = open(f'_includes/demos/{d}.html', encoding='utf-8').read()
            mid = re.search(r'<div class="bd"[^>]*\bid="([^"]+)"', src)
            lab = re.search(r'aria-label="Interactive demo: ([^"]+)"', src)
            name, desc = DESC.get(d, (None, None))
            if not name:
                missing.append(d)
                name = (lab.group(1) if lab else d).capitalize(); desc = ''
            anchor = '#' + mid.group(1) if mid else ''
            entries.append((name, fm['permalink'] + anchor, desc))
        total += len(entries)
        part = fm.get('parent', '')
        if not parts or parts[-1][0] != part: parts.append((part, []))
        parts[-1][1].append((fm['title'], fm['permalink'], entries))
    out = ['---', 'title: Interactive Demos', 'nav_order: 2.5', 'permalink: /demos/', '---', '',
           '# Interactive Demos', '',
           f'All {total} demos of the tutorial on one page. Each runs in your browser with no installation, computes its '
           'pictures and numbers from a small model of the device, and reproduces the chapter\'s own numbers at its '
           'default settings. The link takes you to the demo inside its chapter, where the text explains what it shows.',
           '{: .chapterlead }', '']
    for part, chs in parts:
        out += ['## ' + part.replace(' · ', ' · '), '']
        for title, perm, entries in chs:
            out += [f'### [{title}]({{{{ \'{perm}\' | relative_url }}}})', '']
            for name, link, desc in entries:
                url = "{{ '" + link.split('#')[0] + "' | relative_url }}" + ('#' + link.split('#')[1] if '#' in link else '')
                out.append(f'- [{name}]({url}){": " + desc if desc else ""}')
            out.append('')
    open('demos.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
    print(f'demos.md: {total} demos in {sum(len(c) for _, c in parts)} chapters', '; no description for: ' + ', '.join(missing) if missing else '')

if __name__ == '__main__':
    main()
