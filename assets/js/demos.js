/* Shared helpers for the interactive demos (_includes/demos/*.html). No dependencies. */
(function () {
  if (window.BD) return;
  var C = { grid: 'rgba(140,190,240,.14)', axis: 'rgba(170,205,240,.62)', blue: '#7fb8f0', gold: '#e0b85a',
            red: '#f08a6a', green: '#7fe0a0', teal: '#7fd0b8', white: '#ffffff', dim: 'rgba(170,205,240,.45)' };
  var FONT = '9.5px "IBM Plex Mono", monospace';

  function setup(c) {
    var dpr = window.devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
    var g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    g.font = FONT; g.lineJoin = 'round';
    return { g: g, w: w, h: h };
  }
  function lg(v) { return Math.log10(v); }
  /* plot frame: o = {x:[min,max], y:[min,max], xlog, ylog, xt:[[v,'label']], yt:[...], xl, yl, pad:{l,r,t,b}} */
  function frame(d, o) {
    var p = Object.assign({ l: 48, r: 12, t: 30, b: 26 }, o.pad || {}), g = d.g;   // t: 30 keeps the top tick label clear of the panel tag
    var x0 = o.xlog ? lg(o.x[0]) : o.x[0], x1 = o.xlog ? lg(o.x[1]) : o.x[1];
    var y0 = o.ylog ? lg(o.y[0]) : o.y[0], y1 = o.ylog ? lg(o.y[1]) : o.y[1];
    var X = function (v) { var u = o.xlog ? lg(Math.max(v, 1e-300)) : v; return p.l + (d.w - p.l - p.r) * (u - x0) / (x1 - x0); };
    var Y = function (v) { var u = o.ylog ? lg(Math.max(v, 1e-300)) : v; return d.h - p.b - (d.h - p.t - p.b) * (u - y0) / (y1 - y0); };
    g.strokeStyle = C.grid; g.lineWidth = 1; g.fillStyle = C.axis;
    // ticks outside the axis range are skipped; tick labels are kept inside the canvas (an end label slides inwards)
    (o.xt || []).forEach(function (t) { var x = X(t[0]); if (x < p.l - 0.5 || x > d.w - p.r + 0.5) return; g.beginPath(); g.moveTo(x, p.t); g.lineTo(x, d.h - p.b); g.stroke();
      var hw = g.measureText(t[1]).width / 2; g.textAlign = 'center'; g.fillText(t[1], Math.min(Math.max(x, hw + 2), d.w - hw - 2), d.h - p.b + 12); });
    (o.yt || []).forEach(function (t) { var y = Y(t[0]); if (y < p.t - 0.5 || y > d.h - p.b + 0.5) return; g.beginPath(); g.moveTo(p.l, y); g.lineTo(d.w - p.r, y); g.stroke();
      var wide = g.measureText(t[1]).width > p.l - 7; g.textAlign = wide ? 'left' : 'right'; g.fillText(t[1], wide ? 2 : p.l - 5, y + 3); });
    g.textAlign = 'right'; if (o.xl) g.fillText(o.xl, d.w - p.r, d.h - 4);
    g.textAlign = 'left'; if (o.yl) g.fillText(o.yl, 4, p.t - 8 + 0);
    g.textAlign = 'left';
    return { X: X, Y: Y, p: p, d: d, clipIn: function () { g.save(); g.beginPath(); g.rect(p.l, p.t, d.w - p.l - p.r, d.h - p.t - p.b); g.clip(); },
             clipOut: function () { g.restore(); } };
  }
  function line(f, xs, ys, col, w, dash) {
    var g = f.d.g; f.clipIn(); g.strokeStyle = col; g.lineWidth = w || 1.6; g.setLineDash(dash || []); g.beginPath();
    var started = false;
    for (var i = 0; i < xs.length; i++) {
      if (!isFinite(ys[i])) { started = false; continue; }
      var x = f.X(xs[i]), y = f.Y(ys[i]);
      if (!started) { g.moveTo(x, y); started = true; } else g.lineTo(x, y);
    }
    g.stroke(); g.setLineDash([]); f.clipOut();
  }
  function hline(f, y, col, dash, label) {
    var g = f.d.g, yy = f.Y(y); if (!(yy >= f.p.t - 0.5 && yy <= f.d.h - f.p.b + 0.5)) return;   // off the plot: draw nothing
    g.strokeStyle = col; g.setLineDash(dash || [5, 4]); g.lineWidth = 1.1;
    g.beginPath(); g.moveTo(f.p.l, yy); g.lineTo(f.d.w - f.p.r, yy); g.stroke(); g.setLineDash([]);
    if (label) { g.fillStyle = col; g.textAlign = 'right'; g.fillText(label, f.d.w - f.p.r - 2, yy - 4); g.textAlign = 'left'; }
  }
  function vline(f, x, col, dash, label, dy) {   // dy: move the label down (to clear another line's label)
    var g = f.d.g, xx = f.X(x); if (!(xx >= f.p.l - 0.5 && xx <= f.d.w - f.p.r + 0.5)) return;   // off the plot: draw nothing
    g.strokeStyle = col; g.setLineDash(dash || [5, 4]); g.lineWidth = 1.1;
    g.beginPath(); g.moveTo(xx, f.p.t); g.lineTo(xx, f.d.h - f.p.b); g.stroke(); g.setLineDash([]);
    if (label) { g.fillStyle = col; var left = xx + 4 + g.measureText(label).width > f.d.w - 2;   // flip to the left of the line near the right edge
      g.textAlign = left ? 'right' : 'left'; g.fillText(label, left ? xx - 4 : xx + 4, f.p.t + 10 + (dy || 0)); g.textAlign = 'left'; }
  }
  function dot(f, x, y, col, r) { var g = f.d.g; g.fillStyle = col; g.beginPath(); g.arc(f.X(x), f.Y(y), r || 3.5, 0, 7); g.fill(); }
  function logticks(a, b, unit) {
    var t = [];
    for (var e = Math.floor(lg(a)); e <= Math.ceil(lg(b)); e++) { var v = Math.pow(10, e); if (v >= a * 0.999 && v <= b * 1.001) t.push([v, eng(v) + (unit || '')]); }
    return t;
  }
  function eng(v) {
    var a = Math.abs(v); if (a === 0) return '0';
    var s = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p'], [1e-15, 'f']];
    for (var i = 0; i < s.length; i++) if (a >= s[i][0] * 0.9995) { var x = v / s[i][0]; return (Math.abs(x) >= 100 ? x.toFixed(0) : Math.abs(x) >= 10 ? x.toFixed(1).replace(/\.0$/, '') : x.toPrecision(2).replace(/\.?0+$/, '')) + ' ' + s[i][1]; }
    return v.toExponential(1);
  }
  function fft(re, im) {                 // in place, radix 2
    var n = re.length;
    for (var i = 1, j = 0; i < n; i++) { var bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit;
      if (i < j) { var t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
    for (var len = 2; len <= n; len <<= 1) {
      var ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
      for (var s = 0; s < n; s += len) { var cr = 1, ci = 0;
        for (var k = 0; k < len / 2; k++) {
          var ar = re[s + k + len / 2] * cr - im[s + k + len / 2] * ci, ai = re[s + k + len / 2] * ci + im[s + k + len / 2] * cr;
          re[s + k + len / 2] = re[s + k] - ar; im[s + k + len / 2] = im[s + k] - ai; re[s + k] += ar; im[s + k] += ai;
          var nr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nr; } } }
  }
  function gauss() { var u = 1 - Math.random(), v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function rng(seed) { var s = seed >>> 0 || 1; return function () { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) / 4294967296); }; }
  /* sliders: <input type=range data-k="name">; map(v) converts the raw value; fmt(x) formats it */
  function bind(root, spec, onchange) {
    var st = {};
    Object.keys(spec).forEach(function (k) {
      var el = root.querySelector('[data-k="' + k + '"]'), out = root.querySelector('[data-v="' + k + '"]'), s = spec[k];
      var upd = function () { st[k] = s.map ? s.map(parseFloat(el.value)) : parseFloat(el.value); if (out) out.textContent = s.fmt ? s.fmt(st[k]) : st[k]; };
      upd(); el.addEventListener('input', function () { upd(); onchange(k); });
    });
    return st;
  }
  function seg(root, name, onchange) {      // segmented buttons with data-<name>
    var bs = root.querySelectorAll('[data-' + name + ']'), val = null;
    bs.forEach(function (b) { if (b.getAttribute('aria-pressed') === 'true') val = b.getAttribute('data-' + name);
      b.addEventListener('click', function () { bs.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        onchange(b.getAttribute('data-' + name)); }); });
    return val;
  }
  function toggle(btn, onchange) {
    btn.addEventListener('click', function () { var on = btn.getAttribute('aria-pressed') !== 'true'; btn.setAttribute('aria-pressed', on ? 'true' : 'false'); onchange(on); });
    return btn.getAttribute('aria-pressed') === 'true';
  }
  function observe(root, draw) {
    var raf = 0, go = function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); };
    try { draw(); } catch (e) { if (window.console) console.error(e); }   // first draw now, not on the next frame
    if (window.ResizeObserver) new ResizeObserver(go).observe(root); else window.addEventListener('resize', go);
    return go;
  }
  /* ---- geometry views (top views and cross-sections that redraw with the sliders) */
  var GEO = { si: '#9db3cc', sin: '#e0b060', ln: '#ee9aaa', ox: 'rgba(160,200,240,.13)', heat: '#e08a3a', metal: '#d8dce4',
              glow: 'rgba(255,214,120,', edge: 'rgba(215,230,247,.6)' };
  function nice(v) { var e = Math.pow(10, Math.floor(Math.log10(v))), m = v / e; return (m >= 5 ? 5 : m >= 2 ? 2 : 1) * e; }
  function scalebar(g, x, y, pxPerUm, maxPx) {   // a 1-2-5 scale bar no longer than maxPx, labelled in um or nm
    var um = nice(maxPx / pxPerUm), px = um * pxPerUm, lab = um >= 1 ? um + ' µm' : Math.round(um * 1000) + ' nm';
    g.strokeStyle = C.white; g.lineWidth = 1.5; g.beginPath(); g.moveTo(x, y); g.lineTo(x + px, y);
    g.moveTo(x, y - 3); g.lineTo(x, y + 3); g.moveTo(x + px, y - 3); g.lineTo(x + px, y + 3); g.stroke(); g.lineWidth = 1;
    g.fillStyle = C.white; g.textAlign = 'center'; g.fillText(lab, x + px / 2, y - 5); g.textAlign = 'left';
  }
  function dim(g, x0, y0, x1, y1, label, col, off) {   // dimension line with arrowheads and a label
    col = col || C.gold; off = off || 0; g.strokeStyle = col; g.fillStyle = col; g.lineWidth = 1;
    g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
    var a = Math.atan2(y1 - y0, x1 - x0), L = Math.hypot(x1 - x0, y1 - y0), h = Math.min(5, L / 3);
    [[x0, y0, a + Math.PI], [x1, y1, a]].forEach(function (p) { g.beginPath(); g.moveTo(p[0], p[1]);
      g.lineTo(p[0] - h * Math.cos(p[2] - 0.45), p[1] - h * Math.sin(p[2] - 0.45)); g.lineTo(p[0] - h * Math.cos(p[2] + 0.45), p[1] - h * Math.sin(p[2] + 0.45)); g.fill(); });
    if (label) { g.textAlign = 'center'; var mx = (x0 + x1) / 2, my = (y0 + y1) / 2; var dx = -Math.sin(a), dy = Math.cos(a), o = off || -7;
      g.fillText(label, mx + dx * o, my + dy * o + 3); g.textAlign = 'left'; }
  }
  function wg(g, pts, widthPx, col) {   // a waveguide drawn as a thick polyline
    g.strokeStyle = col || GEO.si; g.lineWidth = Math.max(1.2, widthPx); g.lineCap = 'butt'; g.lineJoin = 'round';
    g.beginPath(); pts.forEach(function (p, i) { if (i) g.lineTo(p[0], p[1]); else g.moveTo(p[0], p[1]); }); g.stroke(); g.lineWidth = 1; g.lineCap = 'butt';
  }
  function sbend(x0, y0, x1, y1, n) {   // points of a cosine S-bend from (x0,y0) to (x1,y1)
    var pts = []; n = n || 24; for (var i = 0; i <= n; i++) { var t = i / n; pts.push([x0 + (x1 - x0) * t, y0 + (y1 - y0) * (1 - Math.cos(Math.PI * t)) / 2]); } return pts;
  }
  function wgr(g, pts, widthPx, col, rPx, cap) {   // a waveguide polyline with rounded corners (radius clamped to fit each corner)
    g.strokeStyle = col || GEO.si; g.lineWidth = Math.max(1.2, widthPx); g.lineJoin = 'round'; g.lineCap = cap || 'round';
    g.beginPath(); g.moveTo(pts[0][0], pts[0][1]);
    for (var i = 1; i < pts.length - 1; i++) {
      var a = pts[i - 1], b = pts[i], c = pts[i + 1], r = Math.min(rPx || 0, Math.hypot(b[0] - a[0], b[1] - a[1]) / 2, Math.hypot(c[0] - b[0], c[1] - b[1]) / 2);
      if (r > 0.5) g.arcTo(b[0], b[1], c[0], c[1], r); else g.lineTo(b[0], b[1]);
    }
    g.lineTo(pts[pts.length - 1][0], pts[pts.length - 1][1]); g.stroke(); g.lineWidth = 1; g.lineCap = 'butt';
  }
  function glow(g, pts, power, rPx) {   // a soft light underlay along a waveguide path, brighter for more power
    if (power <= 0.005) return; wgr(g, pts, 9, 'rgba(255,214,120,' + (0.12 + 0.55 * Math.min(1, power)).toFixed(3) + ')', rPx, 'butt');   // butt caps: no bright beads where segments meet
  }
  function label(g, s, x, y, col, align) { g.fillStyle = col || C.axis; g.textAlign = align || 'left'; g.fillText(s, x, y); g.textAlign = 'left'; }
  function edges(g, pts, half, col) {   // the two edges of a waveguide of half-width `half` px drawn along a polyline
    g.strokeStyle = col || 'rgba(215,230,247,.5)'; g.lineWidth = 1;
    [1, -1].forEach(function (sg) {
      g.beginPath();
      for (var i = 0; i < pts.length; i++) {
        var a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
        var x = pts[i][0] - sg * half * dy / l, y = pts[i][1] + sg * half * dx / l;
        if (i) g.lineTo(x, y); else g.moveTo(x, y);
      }
      g.stroke();
    });
  }
  function pill(el, text, kind) {   // a status pill: no text hides it; kind 'ok' | 'bad' | 'warn'
    if (!el) return; el.hidden = !text; el.textContent = text || ''; el.className = 'bd-pill' + (kind ? ' ' + kind : '');
  }

  /* ---- live field view. A complex field E(x, y), one sample per CSS pixel of a box on a canvas, drawn as
     Re{E e^{jωt}} (the book's convention: a guided wave goes as e^{-jβz}, so its crests move towards +z):
     red positive, blue negative, transparent at zero over the dark panel. ImageData, so a 600 × 150 px box
     costs about a millisecond. It animates with requestAnimationFrame only while the canvas is on screen and
     the page is visible; with prefers-reduced-motion it starts paused on a still frame (the play button
     still lets a reader start it).
       var F = BD.field(canvas, { button: el, overlay: function (g, d) {…}, hz: 1.2 });
       F.grid(x, y, w, h);             // the field box in canvas CSS px; clears the field
       F.guide(points, { half, decay, amp(i), phase(i) });   // add a guided mode along a polyline
       F.render();                     // normalise and draw a frame now (call after each change)
     Any other field (a mode solver's, an analytic one) can be written straight into F.re / F.im (row-major,
     F.nx × F.ny, sample (i, j) centred at canvas px x + i + 0.5, y + j + 0.5) between grid() and render().
     F.mask (optional Float32Array, same size, 0…1, reset by grid()) multiplies the field as drawn, e.g. to
     dim the cladding. overlay(g, d) draws everything else on the canvas (outlines with BD.edges, labels)
     after each frame; F.ms is the median time of the last 31 animation frames in ms; F.play(on) pauses or
     plays from code. */
  var RM = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var LUT = null;
  function fieldLut() {   // 511 RGBA entries for v = -1 … 1: blue (negative) through transparent to red (positive)
    var lut = new Uint32Array(511), le = new Uint8Array(new Uint32Array([1]).buffer)[0] === 1;
    for (var i = 0; i < 511; i++) {
      var v = (i - 255) / 255, a = Math.pow(Math.abs(v), 0.8), c = v >= 0 ? [255, 84, 62] : [72, 160, 255];
      var wt = Math.max(0, a - 0.7) / 0.3 * 0.55;   // the strongest crests whiten a little
      var r = Math.round(c[0] + (255 - c[0]) * wt), gg = Math.round(c[1] + (255 - c[1]) * wt), b = Math.round(c[2] + (255 - c[2]) * wt), A = Math.round(255 * a);
      lut[i] = le ? ((A << 24) | (b << 16) | (gg << 8) | r) >>> 0 : ((r << 24) | (gg << 16) | (b << 8) | A) >>> 0;
    }
    return lut;
  }
  function modeU(V) {   // u tan u = V on (0, π/2): even slab-like mode, cos inside, exponential tails outside
    var lo = 0, hi = Math.PI / 2 - 1e-9;
    for (var k = 0; k < 40; k++) { var m = (lo + hi) / 2; if (m * Math.tan(m) < V) lo = m; else hi = m; }
    return (lo + hi) / 2;
  }
  function crests(periodPx, minPx) {   // display spacing: real crests if they are at least minPx apart, else 1 per n wavelengths
    var n = Math.max(1, Math.ceil((minPx || 6) / periodPx - 1e-9));
    return { n: n, px: periodPx * n, note: n > 1 ? '1 crest per ' + n + ' λ' : '' };
  }
  function field(canvas, o) {
    o = o || {};
    if (!LUT) LUT = fieldLut();
    var oc = document.createElement('canvas'), ox = oc.getContext('2d'), img = null, u32 = null, inv = 0, btn = null, fts = [];
    var F = { canvas: canvas, nx: 0, ny: 0, rect: null, re: null, im: null, t: 0, hz: o.hz || 1.2, ms: 0,
              playing: !(RM && RM.matches), visible: true, overlay: o.overlay || null, raf: 0, last: 0 };
    F.grid = function (x, y, w, h) {
      var nx = Math.max(1, Math.round(w)), ny = Math.max(1, Math.round(h)), n = nx * ny;
      if (nx !== F.nx || ny !== F.ny) {
        F.nx = nx; F.ny = ny; F.re = new Float32Array(n); F.im = new Float32Array(n);
        F.d2 = new Float32Array(n); F.sk = new Int32Array(n); F.st = new Float32Array(n);
        oc.width = nx; oc.height = ny; img = ox.createImageData(nx, ny); u32 = new Uint32Array(img.data.buffer);
      } else { F.re.fill(0); F.im.fill(0); }
      F.rect = [x, y, nx, ny]; F.mask = null;
      return F;
    };
    F.guide = function (pts, g) { guide(F, pts, g); return F; };
    F.render = function () {
      var m = 0, re = F.re, im = F.im, mk = F.mask;
      for (var i = 0; i < re.length; i++) { var a = (re[i] * re[i] + im[i] * im[i]) * (mk ? mk[i] * mk[i] : 1); if (a > m) m = a; }
      inv = m > 0 ? 1 / Math.sqrt(m) : 0; paint(false); kick();
    };
    function paint(timed) {   // timed: an animation frame (F.ms averages those only)
      if (!F.rect) return;
      var t0 = performance.now(), wt = 2 * Math.PI * F.hz * F.t, c = Math.cos(wt), s = Math.sin(wt), k = 254.999 * inv, re = F.re, im = F.im, n = re.length, lut = LUT;
      if (F.mask) { var mk = F.mask; for (var i = 0; i < n; i++) u32[i] = lut[((re[i] * c - im[i] * s) * mk[i] * k + 255.5) | 0]; }
      else for (i = 0; i < n; i++) u32[i] = lut[((re[i] * c - im[i] * s) * k + 255.5) | 0];   // Re{E e^{jωt}}
      ox.putImageData(img, 0, 0);
      var d = setup(canvas); d.g.imageSmoothingEnabled = true; d.g.drawImage(oc, F.rect[0], F.rect[1], F.rect[2], F.rect[3]);
      if (F.overlay) F.overlay(d.g, d);
      if (timed) { fts.push(performance.now() - t0); if (fts.length > 31) fts.shift(); if (fts.length > 7) F.ms = fts.slice().sort(function (a, b) { return a - b; })[fts.length >> 1]; }   // median of the last 31 frames
    }
    function live() { return F.playing && F.visible && !document.hidden && F.rect; }
    function tick(ts) {
      F.raf = 0; if (!live()) return;
      if (F.last) F.t += Math.min(0.1, (ts - F.last) / 1000);   // a long gap (tab away) does not jump the phase
      F.last = ts; paint(true); F.raf = requestAnimationFrame(tick);
    }
    function kick() { if (live() && !F.raf) { F.last = 0; F.raf = requestAnimationFrame(tick); } }
    function stop() { if (F.raf) cancelAnimationFrame(F.raf); F.raf = 0; }
    function sync() {
      if (!btn) return; btn.setAttribute('data-on', F.playing ? '1' : '0');
      btn.setAttribute('aria-label', (F.playing ? 'Pause' : 'Play') + ' the field animation');
      btn.lastChild.textContent = F.playing ? 'pause' : 'play';
    }
    F.play = function (on) { F.playing = !!on; sync(); if (on) kick(); else stop(); };
    var host = o.button === false ? null : (o.button || canvas.parentNode);
    if (host) {
      btn = document.createElement('button'); btn.type = 'button'; btn.className = 'bd-play';
      btn.appendChild(document.createElement('span')); btn.lastChild.className = 'w';
      btn.addEventListener('click', function () { F.play(!F.playing); });
      host.insertBefore(btn, host.firstChild); sync();
    }
    if (window.IntersectionObserver) new IntersectionObserver(function (es) {
      F.visible = es[es.length - 1].isIntersecting; if (F.visible) kick(); else stop(); }).observe(canvas);
    document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); else kick(); });
    if (RM) { var onRM = function () { if (RM.matches) F.play(false); }; if (RM.addEventListener) RM.addEventListener('change', onRM); else if (RM.addListener) RM.addListener(onRM); }
    return F;
  }
  /* add one guided mode to F along a polyline pts (canvas CSS px): profile(d) × amp(s) × e^{-j phase(s)}, where d is
     the distance from the path, half the core half-width and decay the 1/e length of the tails (both px), amp(i) a
     slowly varying complex amplitude [re, im] and phase(i) the accumulated phase (radians) at vertex i, both
     interpolated along each segment (or beta: radians per px of path). Each pixel takes its nearest segment. */
  function guide(F, pts, o) {
    var nx = F.nx, ny = F.ny, X0 = F.rect[0], Y0 = F.rect[1], a = o.half, dl = o.decay, R = a + 5 * dl, R2 = R * R;
    var u = modeU(a / dl), ca = Math.cos(u), n = pts.length, cum = [0], ar = [], ai = [], ph = [], i, j, k;
    for (i = 1; i < n; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    for (i = 0; i < n; i++) { var A = o.amp ? o.amp(i, cum[i]) : [1, 0]; ar.push(A[0]); ai.push(A[1]); ph.push(o.phase ? o.phase(i, cum[i]) : (o.beta || 0) * cum[i]); }
    var d2 = F.d2, sk = F.sk, st = F.st, bi0 = nx, bi1 = -1, bj0 = ny, bj1 = -1;
    d2.fill(R2); sk.fill(-1);
    for (k = 0; k < n - 1; k++) {
      var x0 = pts[k][0] - X0, y0 = pts[k][1] - Y0, dx = pts[k + 1][0] - pts[k][0], dy = pts[k + 1][1] - pts[k][1], L2 = dx * dx + dy * dy;
      if (!(L2 > 0)) continue;
      var i0 = Math.max(0, Math.floor(Math.min(x0, x0 + dx) - R)), i1 = Math.min(nx - 1, Math.ceil(Math.max(x0, x0 + dx) + R));
      var j0 = Math.max(0, Math.floor(Math.min(y0, y0 + dy) - R)), j1 = Math.min(ny - 1, Math.ceil(Math.max(y0, y0 + dy) + R));
      if (i0 < bi0) bi0 = i0; if (i1 > bi1) bi1 = i1; if (j0 < bj0) bj0 = j0; if (j1 > bj1) bj1 = j1;
      for (j = j0; j <= j1; j++) {
        var py = j + 0.5 - y0, row = j * nx;
        for (i = i0; i <= i1; i++) {
          var px = i + 0.5 - x0, t = (px * dx + py * dy) / L2; t = t < 0 ? 0 : t > 1 ? 1 : t;
          var ex = px - t * dx, ey = py - t * dy, e2 = ex * ex + ey * ey;
          if (e2 < d2[row + i]) { d2[row + i] = e2; sk[row + i] = k; st[row + i] = t; }
        }
      }
    }
    var re = F.re, im = F.im;
    for (j = bj0; j <= bj1; j++) for (i = bi0; i <= bi1; i++) {
      var p = j * nx + i, s = sk[p]; if (s < 0) continue;
      var tt = st[p], d = Math.sqrt(d2[p]), pr = d <= a ? Math.cos(u * d / a) : ca * Math.exp(-(d - a) / dl);
      var Ar = ar[s] + tt * (ar[s + 1] - ar[s]), Ai = ai[s] + tt * (ai[s + 1] - ai[s]), P = ph[s] + tt * (ph[s + 1] - ph[s]), cp = Math.cos(P), sp = Math.sin(P);
      re[p] += pr * (Ar * cp + Ai * sp); im[p] += pr * (Ai * cp - Ar * sp);   // (Ar + jAi) e^{-jP}
    }
  }

  /* ---- "Check yourself" questions (.bd-check): one listener for the whole page, so no per-demo script */
  function checkClick(e) {
    var b = e.target && e.target.closest ? e.target.closest('.bd-check-opts button') : null; if (!b) return;
    var box = b.closest('.bd-check'), fb = box.querySelector('.bd-check-fb'), ok = b.hasAttribute('data-correct');
    b.setAttribute('data-state', ok ? 'right' : 'wrong');
    if (ok) box.querySelectorAll('.bd-check-opts button').forEach(function (o) { if (o !== b) o.removeAttribute('data-state'); });
    if (fb) {
      var why = b.getAttribute('data-why') || (ok ? box.getAttribute('data-why') : '') || (ok ? '' : 'Try another answer.');
      fb.innerHTML = '';
      var tag = document.createElement('span'); tag.className = ok ? 'ok' : 'bad'; tag.textContent = ok ? 'Right. ' : 'Not quite. ';
      fb.appendChild(tag); fb.appendChild(document.createTextNode(why));
    }
  }
  function checkInit() {
    document.querySelectorAll('.bd-check').forEach(function (box) {
      if (box.getAttribute('data-wired')) return; box.setAttribute('data-wired', '1');
      box.querySelectorAll('.bd-check-opts button').forEach(function (b) { b.type = 'button'; });
      var fb = box.querySelector('.bd-check-fb'); if (fb && !fb.hasAttribute('aria-live')) fb.setAttribute('aria-live', 'polite');
    });
  }
  document.addEventListener('click', checkClick);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', checkInit); else checkInit();

  window.BD = { C: C, setup: setup, frame: frame, line: line, hline: hline, vline: vline, dot: dot, logticks: logticks,
                eng: eng, fft: fft, gauss: gauss, rng: rng, bind: bind, seg: seg, toggle: toggle, observe: observe,
                GEO: GEO, nice: nice, scalebar: scalebar, dim: dim, wg: wg, wgr: wgr, glow: glow, sbend: sbend, label: label,
                edges: edges, pill: pill, field: field, crests: crests };
})();
