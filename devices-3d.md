---
title: PDK Devices in 3D
nav_order: 11
permalink: /devices-3d/
---

# PDK Devices in 3D

Real devices from open process design kits, extruded from their layouts so you can turn them over and see what the masks make.
{: .chapterlead }

<link rel="stylesheet" href="{{ '/assets/css/devices3d.css' | relative_url }}">
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4.0.0/dist/model-viewer.min.js"></script>

Every model on this page is drawn by its PDK's own [gdsfactory](https://github.com/gdsfactory/gdsfactory) implementation, and each layer is extruded to the thickness and height given by that PDK's layer stack. Heights are to scale, with no vertical exaggeration unless you choose one below. The oxide cladding and the substrate are left out so that you can see the silicon, nitride or lithium niobate; a translucent plate marks the top of the buried oxide. The script that makes the models is [`tools/export_3d.py`](https://github.com/kithminrw/photonics-tutorial/blob/main/tools/export_3d.py).

**Credit.** The devices belong to their designers and PDKs, named on each card. They are shown here under the PDKs' open-source licences (all MIT), with the papers that describe them; please cite those papers, not this page, when you use a design.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">How to use the viewers</div>

Drag to rotate, right-drag or two-finger drag to pan, and scroll or pinch to zoom once you have clicked into a viewer. Click a layer in a legend to hide or show it. The vertical-stretch buttons apply to every viewer: a 220 nm film is thin next to a 10 µm ring, and stretching it helps you see the etch steps.

</div>

<div class="d3-toolbar" role="group" aria-label="Vertical stretch for all viewers">
  <span>vertical stretch</span>
  <button type="button" data-zs="1" aria-pressed="true">1× (true scale)</button>
  <button type="button" data-zs="4" aria-pressed="false">4×</button>
  <button type="button" data-zs="15" aria-pressed="false">15×</button>
</div>

{% assign groups = "SiEPIC EBeam PDK|CORNERSTONE PDK|Luxtelligence LNOI400 PDK" | split: "|" %}
{% for gname in groups %}
{% assign devs = site.data.devices3d | where: "pdk", gname %}
{% if devs.size > 0 %}
{% assign d0 = devs | first %}
<h2 id="{{ gname | slugify }}">{{ gname }}</h2>

{% if gname == "SiEPIC EBeam PDK" %}
The SiEPIC EBeam PDK {% include cite.html keys="ebeampdk" %} is the open kit behind the edX course *Silicon Photonics Design, Fabrication and Data Analysis* and the openEBL runs {% include cite.html keys="openebl" %}: 220 nm SOI at 1550 nm, patterned by electron-beam lithography. Its fixed cells are hardware-validated designs from the UBC group and collaborators; the models here come through its gdsfactory implementation, ubcpdk {% include cite.html keys="ubcpdk" %}.
{% elsif gname == "CORNERSTONE PDK" %}
CORNERSTONE is a UK rapid-prototyping service with several platforms. Its gdsfactory implementation, cspdk {% include cite.html keys="cspdk" %}, covers 220 nm and 340 nm SOI, silicon nitride and others; here are a rib-waveguide 220 nm SOI pair and a 300 nm SiN pair, to compare the same building blocks across platforms.
{% elsif gname == "Luxtelligence LNOI400 PDK" %}
Luxtelligence's LNOI400 PDK {% include cite.html keys="lxtpdk" %} is for thin-film lithium niobate: a 400 nm LN film etched halfway, so every ridge sits on a 200 nm slab. Lithium niobate's Pockels effect makes it the platform for fast, low-voltage modulators (Chapters 19–20).
{% endif %}

<div class="d3-grid">
{% for d in devs %}
  <figure class="d3-card" id="dev-{{ d.slug }}">
    <model-viewer class="d3-view" src="{{ '/assets/models/' | append: d.file | relative_url }}" alt="3D model of {{ d.title }} from the {{ d.pdk }}"
      camera-controls touch-action="pan-y" interaction-prompt="none" loading="lazy" reveal="auto"
      camera-orbit="35deg 58deg auto" shadow-intensity="0" exposure="1.05" environment-image="neutral" data-orbit="35deg 58deg auto">
      <button type="button" slot="poster" class="d3-poster">Load 3D model ({{ d.kb }} kB)</button>
    </model-viewer>
    <figcaption>
      <b class="d3-title">{{ d.title }}</b>
      <span class="d3-meta">{{ d.platform }} · {{ d.size_um[0] }} × {{ d.size_um[1] }} µm · cell <code>{{ d.cell }}</code></span>
      <span class="d3-blurb">{{ d.blurb }}</span>
      <span class="d3-credit"><b>Design:</b> {{ d.designers }}. <b>From:</b> <a href="{{ d.pdk_url }}">{{ d.pdk }}</a> ({{ d.licence }}), via {{ d.via }}.{% if d.refs %}{% assign rk = d.refs | join: "," %} {% include cite.html keys=rk %}{% endif %}</span>
      <span class="d3-legend" role="group" aria-label="Layers">
        {% for l in d.layers %}<button type="button" data-layer="{{ l[0] }}" aria-pressed="true" title="{{ l[1].material }}: {{ l[1].thickness_um }} µm thick at z = {{ l[1].zmin_um }} µm"><i style="background:{{ l[1].colour }}"></i>{{ l[0] }} · {{ l[1].thickness_um | times: 1000 | round }} nm</button>{% endfor %}
        <button type="button" class="d3-reset">reset view</button>
      </span>
    </figcaption>
  </figure>
{% endfor %}
</div>
{% endif %}
{% endfor %}

## Coming next

- **VTT 3 µm SOI.** VTT's public gdsfactory PDK {% include cite.html keys="vttpdk" %} draws its rib and strip waveguides with add and subtract mask layers but publishes no layer stack, so its devices will be added once the etch depths can be taken from a public source.
- **More SiEPIC devices:** Bragg gratings, contra-directional couplers, the laser-integration cells of the Shuksan run {% include cite.html keys="shuksan" %}, and active devices with doping layers.
- **InP and BTO.** There is no open InP or BTO PDK with published layouts yet; this page will add one when there is. Commercial PDKs, including OpenLight's heterogeneous InP-on-silicon platform, are under licence and are not shown.

## How the models are made

For each device the script asks the PDK for the cell, keeps the patterned layers of its layer stack (dropping the substrate, buried oxide and cladding), and extrudes every polygon between that layer's `zmin` and `zmin + thickness` with gdsfactory's `to_3d`. It then recolours the layers by material (silicon blue-grey, silicon nitride amber, lithium niobate rose, heaters bronze, metals grey), adds the translucent BOX plate, rotates the scene so that the wafer normal points up, and writes a binary glTF file {% include cite.html keys="modelviewer" %} with one named material per layer, which is what lets the legend hide layers. Partially etched layers appear as separate slabs, so the 70 nm shallow etch of a grating coupler or the 200 nm LN slab under a ridge can be seen directly.

<script>
(function () {
  var views = Array.prototype.slice.call(document.querySelectorAll('.d3-view'));
  // vertical stretch for every viewer (glTF is y-up after the export's rotation)
  var zbtn = document.querySelectorAll('[data-zs]');
  zbtn.forEach(function (b) {
    b.addEventListener('click', function () {
      zbtn.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      var k = b.getAttribute('data-zs');
      views.forEach(function (v) { v.setAttribute('scale', '1 ' + k + ' 1'); if (v.updateFraming) v.updateFraming(); });
    });
  });
  views.forEach(function (v) {
    var card = v.closest('.d3-card'), saved = {};
    var poster = v.querySelector('.d3-poster');
    if (poster) poster.addEventListener('click', function () { v.dismissPoster(); });
    card.querySelectorAll('[data-layer]').forEach(function (btn) {
      btn.addEventListener('click', function (ev) {
        if (!v.model) return;
        var name = btn.getAttribute('data-layer'), buttons = card.querySelectorAll('[data-layer]');
        var solo = ev.shiftKey || ev.altKey;
        buttons.forEach(function (o) {
          var on = solo ? (o === btn) : (o === btn ? o.getAttribute('aria-pressed') !== 'true' : o.getAttribute('aria-pressed') === 'true');
          o.setAttribute('aria-pressed', on ? 'true' : 'false');
          v.model.materials.forEach(function (m) {
            if (m.name !== o.getAttribute('data-layer')) return;
            var pbr = m.pbrMetallicRoughness;
            if (!saved[m.name]) saved[m.name] = pbr.baseColorFactor.slice();
            var c = saved[m.name].slice(); c[3] = on ? saved[m.name][3] : 0;
            m.setAlphaMode(on && saved[m.name][3] >= 1 ? 'OPAQUE' : 'BLEND');
            pbr.setBaseColorFactor(c);
          });
        });
      });
    });
    var reset = card.querySelector('.d3-reset');
    if (reset) reset.addEventListener('click', function () {
      v.cameraOrbit = v.getAttribute('data-orbit'); v.cameraTarget = 'auto auto auto'; v.fieldOfView = 'auto'; v.jumpCameraToGoal();
    });
  });
})();
</script>
