(() => {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs || {}) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const txt = (parent, x, y, s, cls, anchor) => { const t = mk("text", { x, y, "text-anchor": anchor || "start", "dominant-baseline": "middle" }, parent); if (cls) t.setAttribute("class", cls); t.textContent = s; return t; };
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const COLORS = ["--viz-1", "--viz-2", "--viz-3"];
  const tip = document.querySelector(".viz-tip");
  const fmt = (v, d) => (v === null || v === undefined || Number.isNaN(v)) ? "—" : (d.prefix || "") + Number(v).toLocaleString("ja-JP", d.digits === undefined ? { maximumFractionDigits: 1 } : { minimumFractionDigits: d.digits, maximumFractionDigits: d.digits }) + (d.unit || "");
  const tick = (v) => Number(v).toLocaleString("ja-JP", { maximumFractionDigits: 2 });
  const textW = (s) => [...String(s)].reduce((w, ch) => w + (ch.charCodeAt(0) > 0x2e80 ? 13 : 7.4), 0);
  const nice = (m) => { if (m <= 0) return 1; const p = 10 ** Math.floor(Math.log10(m)); const n = m / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p; };

  function showTip(title, rows, x, y) {
    tip.replaceChildren();
    const t = document.createElement("div"); t.className = "t"; t.textContent = title; tip.appendChild(t);
    for (const r of rows) {
      const row = document.createElement("div"); row.className = "r";
      const i = document.createElement("i"); i.style.background = r.color; row.appendChild(i);
      const st = document.createElement("strong"); st.textContent = r.value; row.appendChild(st);
      const sp = document.createElement("span"); sp.textContent = r.label; row.appendChild(sp);
      tip.appendChild(row);
    }
    tip.style.display = "block";
    const w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.min(window.innerWidth - w - 8, Math.max(8, x + 12)) + "px";
    tip.style.top = Math.min(window.innerHeight - h - 8, Math.max(8, y - h - 10)) + "px";
  }
  const hideTip = () => { tip.style.display = "none"; };
  const at = (ev, el) => { if (ev && ev.clientX !== undefined) return [ev.clientX, ev.clientY]; const r = el.getBoundingClientRect(); return [r.left + r.width / 2, r.top]; };

  function legend(fig, series, kind) {
    if (series.length < 2) return;
    const ul = document.createElement("ul"); ul.className = "viz-legend";
    series.forEach((s, i) => { const li = document.createElement("li"); const sw = document.createElement("i"); if (kind === "line") sw.className = "line"; sw.style.background = css(COLORS[i] || "--viz-deemph"); li.appendChild(sw); li.appendChild(document.createTextNode(s.name)); ul.appendChild(li); });
    fig.insertBefore(ul, fig.firstChild);
  }
  function table(fig, d) {
    const det = document.createElement("details"); det.className = "viz-table";
    const sum = document.createElement("summary"); sum.textContent = "表で見る"; det.appendChild(sum);
    const wrap = document.createElement("div"); wrap.className = "table-wrap";
    const tb = document.createElement("table"); const thead = tb.createTHead().insertRow();
    const th0 = document.createElement("th"); th0.textContent = d.categoryLabel || ""; thead.appendChild(th0);
    d.series.forEach(s => { const th = document.createElement("th"); th.textContent = s.name + (d.unit ? "（" + d.unit + "）" : ""); thead.appendChild(th); });
    const body = tb.createTBody();
    d.categories.forEach((c, ci) => { const tr = body.insertRow(); tr.insertCell().textContent = c; d.series.forEach(s => { const td = tr.insertCell(); td.className = "num"; td.textContent = fmt(s.values[ci], { ...d, unit: "", prefix: d.prefix }); }); });
    wrap.appendChild(tb); det.appendChild(wrap); fig.appendChild(det);
  }

  function bar(fig, d, W) {
    const n = d.series.length, thick = n > 1 ? 14 : 18, gap = 2, pad = 12;
    const band = n * thick + (n - 1) * gap + pad * 2;
    const labelW = Math.min(Math.round(W * 0.42), Math.max(...d.categories.map(textW)) + 14);
    const maxV = d.max ?? nice(Math.max(...d.series.flatMap(s => s.values.filter(v => v != null)), 0));
    const valW = Math.max(...d.series.flatMap(s => s.values.map(v => textW(fmt(v, d))))) + 12;
    const x0 = labelW, x1 = W - valW, H = d.categories.length * band + 6;
    const svg = mk("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": d.title || "" });
    const sx = (v) => x0 + (Math.max(0, v) / maxV) * (x1 - x0);
    d.categories.forEach((c, ci) => {
      const top = ci * band;
      txt(svg, labelW - 10, top + band / 2, c, null, "end");
      d.series.forEach((s, si) => {
        const v = s.values[ci]; if (v == null) return;
        const y = top + pad + si * (thick + gap), xe = sx(v), w = xe - x0, r = Math.min(4, w / 2, thick / 2);
        let color = css(COLORS[si] || "--viz-deemph");
        if (n === 1 && d.emphasis && c !== d.emphasis) color = css("--viz-deemph");
        if (w > 0.5) mk("path", { d: `M${x0},${y}H${xe - r}A${r},${r} 0 0 1 ${xe},${y + r}V${y + thick - r}A${r},${r} 0 0 1 ${xe - r},${y + thick}H${x0}Z`, fill: color }, svg);
        txt(svg, xe + 6, y + thick / 2, fmt(v, d), "value");
      });
      const hit = mk("rect", { x: 0, y: top, width: W, height: band, class: "hit", tabindex: 0, "aria-label": c + " " + d.series.map(s => s.name + " " + fmt(s.values[ci], d)).join("、") }, svg);
      const rows = () => d.series.map((s, si) => ({ color: (n === 1 && d.emphasis && c !== d.emphasis) ? css("--viz-deemph") : css(COLORS[si] || "--viz-deemph"), label: s.name, value: fmt(s.values[ci], d) }));
      hit.addEventListener("pointermove", (ev) => showTip(c, rows(), ...at(ev, hit)));
      hit.addEventListener("focus", (ev) => showTip(c, rows(), ...at(null, hit)));
      hit.addEventListener("pointerleave", hideTip); hit.addEventListener("blur", hideTip);
    });
    mk("line", { x1: x0, x2: x0, y1: 0, y2: H - 6, stroke: css("--viz-axis"), "stroke-width": 1 }, svg);
    return svg;
  }

  function line(fig, d, W) {
    const H = 260, L = 52, R = Math.min(130, Math.max(60, ...d.series.map(s => textW(s.name) + 56))), T = 14, B = 30, m = d.categories.length;
    const all = d.series.flatMap(s => s.values.filter(v => v != null));
    let lo = d.zero ? 0 : Math.min(...all), hi = Math.max(...all);
    const step = nice((hi - lo || hi || 1) / 4); lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step; if (hi === lo) hi = lo + step;
    const sx = (i) => L + (m === 1 ? (W - L - R) / 2 : i * (W - L - R) / (m - 1));
    const sy = (v) => T + (1 - (v - lo) / (hi - lo)) * (H - T - B);
    const svg = mk("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": d.title || "", tabindex: 0 });
    for (let v = lo; v <= hi + step / 2; v += step) { mk("line", { x1: L, x2: W - R, y1: sy(v), y2: sy(v), stroke: css(v === lo ? "--viz-axis" : "--viz-grid"), "stroke-width": 1 }, svg); txt(svg, L - 8, sy(v), tick(v), "muted", "end"); }
    const every = Math.ceil(m / 8);
    d.categories.forEach((c, i) => { if (i % every === 0 || i === m - 1) txt(svg, sx(i), H - B + 16, c, "muted", "middle"); });
    const ends = [];
    d.series.forEach((s, si) => {
      const color = css(COLORS[si] || "--viz-deemph");
      const pts = s.values.map((v, i) => v == null ? null : [sx(i), sy(v)]);
      let path = "", pen = false; pts.forEach(p => { if (!p) { pen = false; return; } path += (pen ? "L" : "M") + p[0] + "," + p[1]; pen = true; });
      if (d.series.length === 1 && lo === 0) { const f = pts.filter(Boolean); if (f.length > 1) mk("path", { d: path + `L${f[f.length - 1][0]},${sy(lo)}L${f[0][0]},${sy(lo)}Z`, fill: color, "fill-opacity": .1 }, svg); }
      mk("path", { d: path, fill: "none", stroke: color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
      if (m <= 12) pts.forEach((p, i) => { if (p && i < m - 1) mk("circle", { cx: p[0], cy: p[1], r: 4, fill: color, stroke: css("--viz-surface"), "stroke-width": 2 }, svg); });
      const li = s.values.map((v, i) => v == null ? -1 : i).filter(i => i >= 0).pop();
      if (li !== undefined) { mk("circle", { cx: sx(li), cy: sy(s.values[li]), r: 4, fill: color, stroke: css("--viz-surface"), "stroke-width": 2 }, svg); ends.push({ y: sy(s.values[li]), x: sx(li), s, v: s.values[li] }); }
    });
    ends.sort((a, b) => a.y - b.y);
    const collide = ends.some((e, i) => i > 0 && e.y - ends[i - 1].y < 15);
    if (!collide) ends.forEach(e => txt(svg, e.x + 8, e.y, fmt(e.v, d) + (d.series.length > 1 ? " " + e.s.name : ""), "value"));
    const cross = mk("line", { y1: T, y2: H - B, stroke: css("--viz-axis"), "stroke-width": 1, visibility: "hidden" }, svg);
    const overlay = mk("rect", { x: L, y: T, width: W - L - R, height: H - T - B, fill: "transparent" }, svg);
    let idx = m - 1;
    const show = (i, ev) => {
      idx = Math.max(0, Math.min(m - 1, i));
      cross.setAttribute("x1", sx(idx)); cross.setAttribute("x2", sx(idx)); cross.setAttribute("visibility", "visible");
      const rows = d.series.map((s, si) => ({ color: css(COLORS[si] || "--viz-deemph"), label: s.name, value: fmt(s.values[idx], d) }));
      const r = svg.getBoundingClientRect(); const k = r.width / W;
      showTip(d.categories[idx], rows, ev ? ev.clientX : r.left + sx(idx) * k, ev ? ev.clientY : r.top + T * k + 40);
    };
    overlay.addEventListener("pointermove", (ev) => { const r = svg.getBoundingClientRect(); const x = (ev.clientX - r.left) * W / r.width; show(Math.round((x - L) / ((W - L - R) / Math.max(1, m - 1))), ev); });
    overlay.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
    svg.addEventListener("keydown", (ev) => { if (ev.key === "ArrowLeft") { show(idx - 1); ev.preventDefault(); } if (ev.key === "ArrowRight") { show(idx + 1); ev.preventDefault(); } });
    svg.addEventListener("focus", () => show(idx)); svg.addEventListener("blur", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
    return svg;
  }

  for (const holder of document.querySelectorAll(".viz-chart")) {
    const src = holder.querySelector('script[type="application/json"]');
    if (!src) continue;
    let d; try { d = JSON.parse(src.textContent); } catch (e) { holder.textContent = "グラフのデータを読めませんでした（JSON の形式を確認）"; continue; }
    d.series = d.series || [];
    if (!d.categories || !d.series.length) continue;
    const fig = holder.closest("figure") || holder;
    if (!d.title) { const cap = fig.querySelector("figcaption b"); if (cap) d.title = cap.textContent; }
    // 描けないデータは黙って切り捨てず、理由を示して表だけを出す（SKILL.md の決まり: 系列は 3 本まで、負の値は表）
    const hasNeg = d.type !== "line" && d.series.some(s => s.values.some(v => v != null && v < 0));
    if (d.series.length > 3 || hasNeg) {
      const msg = document.createElement("p"); msg.className = "viz-note";
      msg.textContent = d.series.length > 3 ? "系列が 4 本以上のため、グラフにせず表で示します。" : "負の値を含むため、グラフにせず表で示します。";
      holder.appendChild(msg); table(holder, d);
      holder.querySelector("details.viz-table").open = true;
      continue;
    }
    // 表示する幅で描く（縮小すると文字が小さくなるため）。幅が変わったら描き直す
    const slot = document.createElement("div"); holder.appendChild(slot);
    let lastW = 0;
    const draw = () => { const W = Math.max(300, Math.round(slot.clientWidth || 640)); if (W === lastW) return; lastW = W; slot.replaceChildren((d.type === "line" ? line : bar)(holder, d, W)); };
    draw(); new ResizeObserver(draw).observe(slot);
    legend(holder, d.series, d.type === "line" ? "line" : "bar");
    table(holder, d);
  }
  window.addEventListener("beforeprint", () => document.querySelectorAll("details.viz-table").forEach(x => x.open = true));
})();
