/* Demo layout audit: finds canvas labels that are cut off at a panel edge, labels that overlap each other or a
   panel tag (.bd-tag), panel tags that wrap onto two lines, script errors, demos that draw nothing and horizontal
   page scroll, for every demo on the given pages, at the given window widths, with every slider at both ends and
   every mode button.

   It only sees text boxes: a label crossing a drawn line or curve still needs a look (screenshot).

   Use: serve the site (bundle exec jekyll serve), open any page of it, paste this file into the browser console,
   then run for example
       await demoAudit([375, 900, 1280], ['part-6/ch22', 'part-7/ch31'])
   Window widths are iframe widths, so desktop scrollbars apply: 375 gives 298 px panels, as on a 360 px phone. */
(function () {
  function install() {   // runs inside each page: wraps fillText/clearRect to log where every label is drawn
    if (window.__au) return;
    var P = CanvasRenderingContext2D.prototype, ft = P.fillText, cr = P.clearRect, log = new Map();
    P.clearRect = function (x, y, w, h) { var c = this.canvas; if (x <= 0 && y <= 0 && w >= c.clientWidth - 1 && h >= c.clientHeight - 1) log.set(c, []); return cr.apply(this, arguments); };
    P.fillText = function (s, x, y) {
      var c = this.canvas, m = this.measureText(s), T = this.getTransform(), d = window.devicePixelRatio || 1;
      var pts = [[x - m.actualBoundingBoxLeft, y - m.actualBoundingBoxAscent], [x + m.actualBoundingBoxRight, y - m.actualBoundingBoxAscent],
                 [x - m.actualBoundingBoxLeft, y + m.actualBoundingBoxDescent], [x + m.actualBoundingBoxRight, y + m.actualBoundingBoxDescent]]
        .map(function (p) { return [(T.a * p[0] + T.c * p[1] + T.e) / d, (T.b * p[0] + T.d * p[1] + T.f) / d]; });
      var xs = pts.map(function (p) { return p[0]; }), ys = pts.map(function (p) { return p[1]; });
      if (!log.has(c)) log.set(c, []);
      log.get(c).push({ s: String(s), l: Math.min.apply(null, xs), r: Math.max.apply(null, xs), t: Math.min.apply(null, ys), b: Math.max.apply(null, ys) });
      return ft.apply(this, arguments);
    };
    function issues(root) {
      var out = [], ov = function (a, b) { return Math.min(a.r, b.r) - Math.max(a.l, b.l) > 1 && Math.min(a.b, b.b) - Math.max(a.t, b.t) > 1; };
      if (root.scrollWidth > root.clientWidth + 1) out.push('DEMO-OVERFLOW ' + root.scrollWidth + ' > ' + root.clientWidth);
      var drawn = 0; root.querySelectorAll('canvas').forEach(function (c) { drawn += (log.get(c) || []).length; });
      if (!drawn) out.push('NO-DRAW (no label drawn: the demo script probably failed)');
      root.querySelectorAll('canvas').forEach(function (c) {
        var L = (log.get(c) || []).filter(function (e) { return e.s.trim(); }), w = c.clientWidth, h = c.clientHeight, cb = c.getBoundingClientRect();
        var tags = Array.prototype.map.call(c.parentElement.querySelectorAll('.bd-tag'), function (t) { var r = t.getBoundingClientRect();
          return { s: t.textContent, l: r.left - cb.left, r: r.right - cb.left, t: r.top - cb.top, b: r.bottom - cb.top }; });
        tags.forEach(function (t) { if (t.b - t.t > 16) out.push('TAG-WRAP "' + t.s + '"'); });
        L.forEach(function (e) { if (e.l < -0.5 || e.r > w + 0.5 || e.t < -0.5 || e.b > h + 0.5) out.push('OUT "' + e.s + '"'); });
        L.forEach(function (e) { tags.forEach(function (t) { if (ov(e, t)) out.push('ON-TAG "' + e.s + '" x "' + t.s + '"'); }); });
        for (var i = 0; i < L.length; i++) for (var j = i + 1; j < L.length; j++) if (L[i].s !== L[j].s && ov(L[i], L[j])) out.push('OVERLAP "' + L[i].s + '" x "' + L[j].s + '"');
      });
      return out;
    }
    window.__au = { issues: issues };
  }
  window.demoAudit = async function (widths, pages) {
    var base = location.pathname.split('/').slice(0, 2).join('/') + '/', res = [];
    for (var wi = 0; wi < widths.length; wi++) for (var pi = 0; pi < pages.length; pi++) {
      var f = document.createElement('iframe'); f.style.cssText = 'position:absolute;left:0;top:0;width:' + widths[wi] + 'px;height:900px;border:0';
      document.body.appendChild(f);
      await new Promise(function (r) { f.onload = r; f.src = base + pages[pi] + '/'; });
      var W = f.contentWindow, errs = [], seen = new Map(); await W.document.fonts.ready;
      W.addEventListener('error', function (e) { errs.push(e.message); });
      var ce = W.console.error; W.console.error = function (e) { errs.push(String(e && e.message || e)); return ce.apply(W.console, arguments); };   // BD.observe logs a failed draw
      W.eval('(' + install.toString() + ')()');
      W.document.querySelectorAll('.bd').forEach(function (root) {
        var fire = function (inp) { inp.dispatchEvent(new W.Event('input', { bubbles: true })); };
        var grab = function (state) { root.querySelectorAll('input[type=range]').forEach(fire);
          var noSl = !root.querySelector('input[type=range]');   // without sliders nothing redraws until a button is clicked
          W.__au.issues(root).filter(function (s) { return !(noSl && state === 'default' && /^NO-DRAW/.test(s)); }).forEach(function (s) { var k = root.id + ': ' + s.replace(/-?\d+(\.\d+)?/g, '#'); if (!seen.has(k)) seen.set(k, state); }); };
        grab('default');
        root.querySelectorAll('input[type=range]').forEach(function (inp) { var v0 = inp.value;
          [inp.min, inp.max].forEach(function (v) { inp.value = v; fire(inp); grab(inp.dataset.k + '=' + v); }); inp.value = v0; fire(inp); });
        root.querySelectorAll('.bd-seg').forEach(function (sg) { var bs = Array.from(sg.querySelectorAll('button')), on = bs.find(function (b) { return b.getAttribute('aria-pressed') === 'true'; });
          bs.forEach(function (b) { b.click(); grab(b.textContent.trim()); }); if (on) on.click(); });
        root.querySelectorAll('.bd-toggle').forEach(function (t) { t.click(); grab('toggle'); t.click(); });
      });
      var head = pages[pi] + ' @' + widths[wi] + (W.document.documentElement.scrollWidth > W.innerWidth ? ' H-SCROLL' : '') + (errs.length ? ' ERROR ' + errs[0] : '');
      res.push(head + (seen.size ? '\n  ' + Array.from(seen).map(function (e) { return e[0] + '   <' + e[1] + '>'; }).join('\n  ') : ' ok'));
      f.remove();
    }
    return res.join('\n');
  };
})();
