/* Viewer cards for the generic laser stacks (_includes/stack3d.html): load on click, hide layers from the legend
   (shift- or alt-click shows one layer alone), switch to the exploded model, stretch the height, reset the camera.
   SPDX-License-Identifier: MIT. Copyright (c) 2026 the Open-Photonics authors. */
(function () {
  if (window.ST3D) return; window.ST3D = 1;
  function wire(card) {
    var v = card.querySelector('model-viewer'), saved = {}, hidden = {};
    var poster = v.querySelector('.d3-poster');
    if (poster) poster.addEventListener('click', function () { v.dismissPoster(); });
    function apply() {
      if (!v.model) return;
      v.model.materials.forEach(function (m) {
        var pbr = m.pbrMetallicRoughness;
        if (!saved[m.name]) saved[m.name] = pbr.baseColorFactor.slice();
        var on = !hidden[m.name], c = saved[m.name].slice();
        c[3] = on ? saved[m.name][3] : 0;
        m.setAlphaMode(on && saved[m.name][3] >= 1 ? 'OPAQUE' : 'BLEND');
        pbr.setBaseColorFactor(c);
      });
    }
    v.addEventListener('load', function () {
      saved = {}; apply();
      // the exploded model is taller: frame it whole, from the same direction
      var o = v.getAttribute('data-orbit').split(' '), ex = v.getAttribute('src') === v.getAttribute('data-src-x');
      v.cameraOrbit = ex ? o[0] + ' ' + o[1] + ' 100%' : o.join(' '); v.cameraTarget = 'auto auto auto'; v.jumpCameraToGoal();
    });
    var layers = card.querySelectorAll('[data-layer]');
    layers.forEach(function (btn) {
      btn.addEventListener('click', function (ev) {
        var solo = ev.shiftKey || ev.altKey;
        layers.forEach(function (o) {
          var on = solo ? (o === btn) : (o === btn ? o.getAttribute('aria-pressed') !== 'true' : o.getAttribute('aria-pressed') === 'true');
          o.setAttribute('aria-pressed', on ? 'true' : 'false'); hidden[o.getAttribute('data-layer')] = !on;
        });
        apply();
      });
    });
    function group(sel, fn) {
      var bs = card.querySelectorAll(sel);
      bs.forEach(function (b) { b.addEventListener('click', function () { bs.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); }); fn(b); }); });
    }
    group('[data-view]', function (b) {
      var src = v.getAttribute(b.getAttribute('data-view') === 'x' ? 'data-src-x' : 'data-src');
      if (v.getAttribute('src') !== src) v.setAttribute('src', src);
      v.dismissPoster();
    });
    group('[data-zs]', function (b) { v.setAttribute('scale', '1 ' + b.getAttribute('data-zs') + ' 1'); if (v.updateFraming) v.updateFraming(); });
    var reset = card.querySelector('.d3-reset');
    if (reset) reset.addEventListener('click', function () {
      v.cameraOrbit = v.getAttribute('data-orbit'); v.cameraTarget = 'auto auto auto'; v.fieldOfView = 'auto'; v.jumpCameraToGoal();
    });
  }
  function init() { document.querySelectorAll('.st-card').forEach(wire); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
