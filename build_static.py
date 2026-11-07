#!/usr/bin/env python3
"""Genera la página estática 'CO21 · Café con pieza' a partir de dos JSON de Square.

Uso: python3 -I build_static.py tickets_co21.json categorias_co21.json salida.html
  tickets_co21.json:    lista de filas con claves Sales.order_id, Sales.local_date, Sales.local_hour,
                        Sales.item_quantities, Sales.team_member_collected_by_name, Sales.net_sales
  categorias_co21.json: lista de filas con claves ProductMixReport.item_name, ProductMixReport.category_name
"""
import json, re, sys, datetime

tickets_path, cats_path, out_path = sys.argv[1:4]
tickets = json.load(open(tickets_path))
cats = json.load(open(cats_path))

CAFE_CATS = {"Cafeteria Especialidad", "Bebida Caliente"}
BOLL_CATS = {"Bolleria Artesana", "Bolleria"}
cafe, boll = set(), set()
for c in cats:
    n, k = c.get("ProductMixReport.item_name"), c.get("ProductMixReport.category_name")
    if not n: continue
    if k in CAFE_CATS and not re.match(r"^(Extra|Babyccino|Plus)", n): cafe.add(n)
    if k in BOLL_CATS: boll.add(n)

rows, seen = [], set()
for t in tickets:
    oid, items = t.get("Sales.order_id"), t.get("Sales.item_quantities")
    if not oid or oid in seen or not items: continue
    seen.add(oid)
    names = [re.sub(r" x [\d.]+$", "", p) for p in items.split(", ")]
    rows.append({
        "d": str(t["Sales.local_date"])[:10],
        "h": int(float(t["Sales.local_hour"] or 0)),
        "c": 1 if any(n in cafe for n in names) else 0,
        "b": 1 if any(n in boll for n in names) else 0,
        "n": round(float(t.get("Sales.net_sales") or 0), 2),
        "w": t.get("Sales.team_member_collected_by_name") or "",
    })
rows.sort(key=lambda r: (r["d"], r["h"]))
max_date = max(r["d"] for r in rows) if rows else ""
generated = datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=1))).strftime("%d/%m/%Y %H:%M")

DATA = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))

HTML = r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CO21 · Café con pieza</title>
<style>
:root { --color-fg: #1f1f1c; --color-fg-muted: #6b6a64; --color-bg: #f7f6f2; --color-panel: #ffffff; --color-border-line: #e3e1da; --color-ok: #2f7a3e; --color-warn: #a2690f; --color-bad: #b8322d;
  --grid: #ecebe5; --axis: #c9c7bf; --ref: #9a988f; --muted-bar: #cfcdc4; --accent: #4f6fb5; --pop: #ffffff; --border: #d6d4cc;
  --radius: 12px; --pad-xs: 4px; --pad-sm: 8px; --pad-md: 12px; --pad-lg: 16px; --pad-xl: 24px; --gap-xs: 4px; --gap-sm: 8px; --gap-md: 12px; --gap-lg: 20px;
  --fs-caption: 13px; --fs-body: 15px; --fs-heading: 18px; --fs-title: 26px; --fw-medium: 600; --font-sans: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; --font-serif: Georgia, "Times New Roman", serif; }
@media (prefers-color-scheme: dark) { :root { --color-fg: #ecebe6; --color-fg-muted: #a4a39c; --color-bg: #171715; --color-panel: #222220; --color-border-line: #35352f; --color-ok: #6fc07e; --color-warn: #e0a23a; --color-bad: #ef6a64; --grid: #2b2b27; --axis: #4a4a43; --ref: #7a786f; --muted-bar: #4a4a43; --accent: #7f9ce0; --pop: #2c2c29; --border: #4a4a43; } }
html, body { margin: 0; background: var(--color-bg); color: var(--color-fg); }
#dash-root { padding: 16px; max-width: 980px; margin: 0 auto; }
.ca { font-family: var(--font-sans); font-variant-numeric: tabular-nums; font-size: var(--fs-body); line-height: 1.45; }
.ca h1 { font-family: var(--font-serif); font-weight: 400; font-size: var(--fs-title); margin: 0 0 var(--gap-xs); }
.ca .lead { color: var(--color-fg-muted); margin: 0 0 var(--gap-lg); }
.ca .upd { font-size: var(--fs-caption); color: var(--color-fg-muted); margin: 0 0 var(--gap-md); }
.ca .tiles { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: var(--gap-sm); margin-bottom: var(--gap-md); }
.ca .tile { background: var(--color-panel); border: 1px solid var(--color-border-line); border-radius: var(--radius); padding: var(--pad-md); min-width: 0; }
.ca .tile .lbl { font-size: var(--fs-caption); color: var(--color-fg-muted); margin: 0 0 var(--gap-xs); }
.ca .tile .big { font-family: var(--font-serif); font-weight: 400; font-size: clamp(1.5rem, 7vw, 2.4rem); line-height: 1.1; margin: 0; white-space: nowrap; }
.ca .tile .sub { font-size: var(--fs-caption); color: var(--color-fg-muted); margin: var(--gap-xs) 0 0; }
.ca .card { background: var(--color-panel); border: 1px solid var(--color-border-line); border-radius: var(--radius); padding: var(--pad-lg); margin-bottom: var(--gap-lg); }
.ca .card h2 { font-size: var(--fs-heading); font-weight: var(--fw-medium); margin: 0 0 var(--gap-xs); }
.ca .card .note { font-size: var(--fs-caption); color: var(--color-fg-muted); margin: 0 0 var(--gap-md); }
.ca table { width: 100%; border-collapse: collapse; }
.ca th { text-align: right; font-weight: 400; color: var(--color-fg-muted); font-size: var(--fs-caption); padding: var(--pad-xs) 0; border-bottom: 1px solid var(--color-border-line); }
.ca th:first-child, .ca td:first-child { text-align: left; }
.ca td { text-align: right; padding: var(--pad-sm) 0; border-bottom: 1px solid var(--color-border-line); }
.ca tr:last-child td { border-bottom: 0; }
.ca .pill { display: inline-block; padding: .1rem .5rem; border-radius: 999px; font-weight: var(--fw-medium); }
.ca .ok { color: var(--color-ok); } .ca .win { color: var(--color-ok); font-weight: var(--fw-medium); } .ca .lose { color: var(--color-fg-muted); } .ca .cur { font-style: italic; } .ca .warn { color: var(--color-warn); } .ca .bad { color: var(--color-bad); }
.ca .chart { min-height: 220px; position: relative; }
.ca .tip { position: absolute; pointer-events: none; background: var(--pop); border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.12); padding: var(--pad-xs) var(--pad-sm); font-size: var(--fs-caption); display: none; }
.ca .tip .d { color: var(--color-fg-muted); }
.ca .tramos { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: var(--gap-sm); }
.ca .tramo { border: 1px solid var(--color-border-line); border-radius: var(--radius); padding: var(--pad-sm); text-align: center; }
.ca .tramo .t { font-size: var(--fs-caption); color: var(--color-fg-muted); }
.ca .tramo .v { font-family: var(--font-serif); font-size: 1.4rem; }
.ca .tramo.hit { border-color: var(--color-ok); background: color-mix(in srgb, var(--color-ok) 10%, transparent); }
.ca .def { font-size: var(--fs-caption); color: var(--color-fg-muted); }
.ca .ideas-wrap { margin: 0 -16px var(--gap-lg); }
.ca .ideas-t { font-size: var(--fs-caption); color: var(--color-fg-muted); margin: 0 16px var(--gap-xs); font-weight: var(--fw-medium); }
.ca .ideas-t span { font-weight: 400; }
.ca .ideas { display: flex; gap: var(--gap-sm); overflow-x: auto; scroll-snap-type: x mandatory; padding: 0 16px 6px; scrollbar-width: none; }
.ca .ideas::-webkit-scrollbar { display: none; }
.ca .idea { flex: 0 0 78%; max-width: 300px; scroll-snap-align: start; background: #fff7e6; color: #4a3a12; border: 1px solid #ecd9a8; border-radius: var(--radius); padding: var(--pad-md) var(--pad-lg); font-size: var(--fs-body); line-height: 1.4; }
.ca .idea b { display: block; font-weight: var(--fw-medium); margin-bottom: 4px; }
@media (prefers-color-scheme: dark) { .ca .idea { background: #2e2616; color: #f0e3c2; border-color: #4d3f1c; } }
@media (max-width: 480px) { .ca table { font-size: 14px; } .ca .tile .lbl, .ca .tile .sub { font-size: 12px; } .ca .pod .val { font-size: 1.4rem; } .ca .p1 .val { font-size: 1.7rem; } }
.ca .podio { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: var(--gap-sm); align-items: end; margin-bottom: var(--gap-sm); }
.ca .pod { background: var(--color-bg); border: 1px solid var(--color-border-line); border-radius: var(--radius); padding: var(--pad-md) var(--pad-sm); text-align: center; }
.ca .pod.p1 { order: 2; padding-top: var(--pad-xl); padding-bottom: var(--pad-xl); border-color: #C9A227; }
.ca .pod.p2 { order: 1; } .ca .pod.p3 { order: 3; }
.ca .medal { display: block; font-size: 2rem; line-height: 1; margin-bottom: var(--gap-xs); }
.ca .p1 .medal { font-size: 2.8rem; }
.ca .pod .nom { font-weight: var(--fw-medium); }
.ca .pod .val { font-family: var(--font-serif); font-size: 1.6rem; line-height: 1.1; color: #B8891B; }
.ca .p1 .val { font-size: 2rem; }
.ca .pod .det { font-size: var(--fs-caption); color: var(--color-fg-muted); }
.ca .liga { display: grid; gap: var(--gap-xs); }
.ca .jug { display: grid; grid-template-columns: 2.2rem 1fr auto; gap: var(--gap-sm); align-items: center; padding: var(--pad-sm) var(--pad-md); background: var(--color-bg); border: 1px solid var(--color-border-line); border-radius: var(--radius); }
.ca .jug .medal { font-size: 1.1rem; margin: 0; text-align: center; font-family: var(--font-serif); }
.ca .jug .nom { font-weight: var(--fw-medium); }
.ca .jug .det { font-size: var(--fs-caption); color: var(--color-fg-muted); }
.ca .jug .val { font-family: var(--font-serif); font-size: 1.4rem; color: #B8891B; text-align: right; }
.ca .jug .val small { display: block; font-family: var(--font-sans); font-size: var(--fs-caption); color: var(--color-fg-muted); }
.ca .jug.fuera { opacity: .6; }
.ca .mejor { font-size: var(--fs-caption); color: var(--color-fg-muted); margin: var(--gap-sm) 0 0; }
</style>
</head>
<body>
<div id="dash-root">
__BODY__
</div>
<script>__D3__</script>
<script>
window.CA_ROWS = __DATA__;
window.CA_UPDATED = "__UPDATED__";
window.CA_MAXDATE = "__MAXISO__";
window.dash = {
  colors: ["#4f6fb5", "#c98a4b", "#2f7a3e", "#9b5ea8", "#b8322d", "#2a8f8f", "#a2690f", "#6b6a64"],
  _data: {}, _calcs: [], _fns: [],
  data(id) { return {status: "ok", data: this._data[id] || []}; },
  calc(id, o) { this._calcs.push([id, o.inputs, o.fn]); },
  onData(fn) { this._fns.push(fn); },
  run() { for (const [id, inputs, fn] of this._calcs) this._data[id] = fn(...inputs.map(i => this._data[i] || [])); this._fns.forEach(f => f()); }
};
</script>
<script>
__SCRIPT__
</script>
<script>
dash.run();
let _rt; window.addEventListener("resize", () => { clearTimeout(_rt); _rt = setTimeout(() => dash._fns.forEach(f => f()), 150); });
</script>
</body>
</html>
'''

# Cuerpo y script de la página del tablero (inlined)
body = '<div class="ca">\n  <h1>CO21 · Café con pieza</h1>\n  <p class="lead" id="lead">De cada 10 cafés que servís, ¿cuántos salen con una pieza?</p>\n\n  <div class="tiles">\n    <div class="tile">\n      <p class="lbl">Esta semana <span id="semana-rango"></span></p>\n      <p class="big" data-source="resumen" data-field="attach_semana_txt" data-row="0">—</p>\n      <p class="sub">de cada 10 · antes <span data-source="resumen" data-field="attach_base_txt" data-row="0">—</span></p>\n    </div>\n    <div class="tile">\n      <p class="lbl">Cafés sin pieza</p>\n      <p class="big" data-source="resumen" data-field="solos_semana" data-row="0">—</p>\n      <p class="sub"><span data-source="resumen" data-field="solos_dia" data-row="0">—</span> al día</p>\n    </div>\n    <div class="tile">\n      <p class="lbl">Ticket medio</p>\n      <p class="big" data-source="resumen" data-field="ticket_semana_txt" data-row="0">—</p>\n      <p class="sub">antes <span data-source="resumen" data-field="ticket_base_txt" data-row="0">—</span></p>\n    </div>\n  </div>\n\n  <div class="ideas-wrap">\n    <p class="ideas-t">Ideas para hoy <span>· desliza</span></p>\n    <div class="ideas">\n      <div class="idea"><b>Pregunta con nombre</b>No "¿algo más?". Di la pieza: "¿te pongo una medialuna con el latte?"</div>\n      <div class="idea"><b>Una sola sugerencia</b>Ofrece una pieza, no la vitrina entera. Elegir cansa; aceptar es fácil.</div>\n      <div class="idea"><b>La pieza del día</b>Escríbela en la pizarra y dila a todos. Una historia corta: "recién salida", "la de Germán".</div>\n      <div class="idea"><b>Antes de cobrar</b>Sugiere mientras preparas el café, no cuando ya tiene la tarjeta fuera.</div>\n      <div class="idea"><b>Sobremesa y cierre</b>Ahí es donde más cafés salen solos. Prueba "algo dulce para después".</div>\n      <div class="idea"><b>Para llevar, también</b>El que va con prisa acepta rápido: "¿un croissant para el camino?"</div>\n      <div class="idea"><b>Caliente a la vista</b>La bandeja recién hecha al lado de la caja vende sola. Repón pronto los huecos.</div>\n      <div class="idea"><b>Un no es un no</b>Sugerir una vez, con una sonrisa. Nunca insistir.</div>\n    </div>\n  </div>\n\n  <div class="card">\n    <h2>Leaderboard · últimos 100 cafés</h2>\n    <p class="note">El premio se reparte por igual; esta tabla es por el orgullo.</p>\n    <div class="podio" id="podio"></div>\n    <div class="liga" id="liga"></div>\n  </div>\n\n  <div class="card">\n    <h2>¿A qué hora se escapan?</h2>\n    <p class="note">Esta semana frente a las 4 anteriores. Rojo: donde más cafés salen solos.</p>\n    <table>\n      <thead><tr><th>Franja</th><th>Antes</th><th>Ahora</th><th>Solos/día</th></tr></thead>\n      <tbody id="tandas-body"></tbody>\n    </table>\n  </div>\n\n  <div class="card">\n    <h2>Semana a semana</h2>\n    <p class="note">🏆 = 5 o más de cada 10 con el ticket medio igual o mejor que las 4 semanas anteriores.</p>\n    <table>\n      <thead><tr><th>Semana del</th><th>De cada 10</th><th>Ticket</th><th></th></tr></thead>\n      <tbody id="semanas-body"></tbody>\n    </table>\n  </div>\n\n  <div class="card">\n    <h2>Día a día</h2>\n    <p class="note">Cada barra, un día. La línea de puntos: las 4 semanas anteriores.</p>\n    <div class="chart" id="chart"><div class="tip" id="tip"></div></div>\n  </div>\n\n  <p class="def">Un "café" es un ticket con café, té o bebida caliente; va "con pieza" si además lleva bollería. Semanas de lunes a domingo. Datos de la caja de CO21 hasta ayer.</p>\n</div>\n'
script = '\nwindow.caTandas = [["Desayuno 7–10h",7,10],["Mediodía 11–13h",11,13],["Sobremesa 14–15h",14,15],["Merienda 16–18h",16,18],["Cierre 19–21h",19,21]];\nwindow.caCafeCats = new Set(["Cafeteria Especialidad","Bebida Caliente"]);\nwindow.caBollCats = new Set(["Bolleria Artesana","Bolleria"]);\nconst fmtPct = v => (v == null || isNaN(v)) ? "—" : (Math.round(v * 1000) / 10).toLocaleString("es-ES", {maximumFractionDigits: 1}) + "%";\nconst fmt10 = v => (v == null || isNaN(v)) ? "—" : (Math.round(v * 100) / 10).toLocaleString("es-ES", {minimumFractionDigits: 1, maximumFractionDigits: 1});\nconst fmtEur2 = v => (v == null || isNaN(v)) ? "—" : v.toLocaleString("es-ES", {minimumFractionDigits: 2, maximumFractionDigits: 2}) + " €";\nconst fmtN = v => (v == null || isNaN(v)) ? "—" : Math.round(v).toLocaleString("es-ES");\nconst fmtN1 = v => (v == null || isNaN(v)) ? "—" : (Math.round(v * 10) / 10).toLocaleString("es-ES", {maximumFractionDigits: 1});\nwindow.caApodos = {"Maria de los Milagros": "Mili", "Nicolás": "Nico"};\nwindow.caExcluir = ["NICOLAS", "Nicolle"];\nconst DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"];\n\nwindow.caPeriods = function () {\n  const now = new Date();\n  const d = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));\n  const dow = (d.getUTCDay() + 6) % 7;\n  const mon = new Date(d); mon.setUTCDate(d.getUTCDate() - dow);\n  const baseStart = new Date(mon); baseStart.setUTCDate(mon.getUTCDate() - 28);\n  const iso = x => x.toISOString().slice(0, 10);\n  return {weekStart: iso(mon), baseStart: iso(baseStart), baseEnd: iso(new Date(mon.getTime() - 86400000)), today: iso(d)};\n};\n\nwindow.caClassify = function (tickets, categorias) {\n  const cafe = new Set(), boll = new Set();\n  for (const c of categorias) {\n    const n = c["ProductMixReport.item_name"], k = c["ProductMixReport.category_name"];\n    if (!n) continue;\n    if (window.caCafeCats.has(k) && !/^(Extra|Babyccino|Plus)/.test(n)) cafe.add(n);\n    if (window.caBollCats.has(k)) boll.add(n);\n  }\n  const out = [], seen = new Set();\n  for (const t of tickets) {\n    const id = t["Sales.order_id"], items = t["Sales.item_quantities"];\n    if (!id || seen.has(id) || !items) continue;\n    seen.add(id);\n    const names = items.split(", ").map(p => p.replace(/ x [\\d.]+$/, ""));\n    const hasC = names.some(n => cafe.has(n)), hasB = names.some(n => boll.has(n));\n    const h = Number(t["Sales.local_hour"]);\n    const tanda = window.caTandas.find(([, a, b]) => h >= a && h <= b);\n    out.push({date: String(t["Sales.local_date"]).slice(0, 10), tanda: tanda ? tanda[0] : null, cafe: hasC, boll: hasB, net: Number(t["Sales.net_sales"]) || 0, who: t["Sales.team_member_collected_by_name"] || null});\n  }\n  out.sort((a, b) => a.date < b.date ? -1 : a.date > b.date ? 1 : 0);\n  return out;\n};\n\ndash.calc("tandas", {\n  title: "Café con pieza por franja",\n  description: "Por franja horaria, qué parte de los tickets con café llevan bollería: esta semana (desde el lunes) y las 4 semanas anteriores.",\n  inputs: ["tickets_co21", "categorias_co21"],\n  fn: (tickets_co21, categorias_co21) => {\n    const P = window.caPeriods(), rows = window.caClassify(tickets_co21, categorias_co21);\n    const wdays = new Set(rows.filter(r => r.date >= P.weekStart).map(r => r.date)).size || 1;\n    const bdays = new Set(rows.filter(r => r.date >= P.baseStart && r.date <= P.baseEnd).map(r => r.date)).size || 1;\n    return window.caTandas.map(([name]) => {\n      const w = rows.filter(r => r.tanda === name && r.cafe && r.date >= P.weekStart);\n      const b = rows.filter(r => r.tanda === name && r.cafe && r.date >= P.baseStart && r.date <= P.baseEnd);\n      const wb = w.filter(r => r.boll).length, bb = b.filter(r => r.boll).length;\n      return {tanda: name, attach_base_pct: b.length ? bb / b.length : null, attach_semana_pct: w.length ? wb / w.length : null,\n        cafe_tk_dia: w.length / wdays, solos_dia: (w.length - wb) / wdays, cafe_tk_base_dia: b.length / bdays};\n    });\n  }\n});\ndash.calc("diario", {\n  title: "Café con pieza por día",\n  description: "Cada día: tickets con café, cuántos llevan pieza y el porcentaje.",\n  inputs: ["tickets_co21", "categorias_co21"],\n  fn: (tickets_co21, categorias_co21) => {\n    const rows = window.caClassify(tickets_co21, categorias_co21).filter(r => r.cafe);\n    const byDay = {};\n    for (const r of rows) { const d = byDay[r.date] || (byDay[r.date] = {date: r.date, cafe_tk: 0, con_pieza: 0}); d.cafe_tk++; if (r.boll) d.con_pieza++; }\n    return Object.values(byDay).sort((a, b) => a.date < b.date ? -1 : 1).map(d => ({...d, attach_pct: d.cafe_tk ? d.con_pieza / d.cafe_tk : null}));\n  }\n});\ndash.calc("liga", {\n  title: "Leaderboard",\n  description: "Por persona que cobró el ticket: sus últimos 100 tickets con café y cuántos llevaban pieza. Solo quien llega a 100.",\n  inputs: ["tickets_co21", "categorias_co21"],\n  fn: (tickets_co21, categorias_co21) => {\n    const rows = window.caClassify(tickets_co21, categorias_co21).filter(r => r.cafe && r.who && !window.caExcluir.some(x => r.who.startsWith(x)));\n    const by = {};\n    for (const r of rows) (by[r.who] = by[r.who] || []).push(r);\n    return Object.entries(by).filter(([, rs]) => rs.length >= 100).map(([quien, rs]) => {\n      const last = rs.slice(-100);\n      const con = last.filter(r => r.boll).length;\n      return {quien, cafe_tk: 100, con_pieza: con, solos: 100 - con, attach_pct: con / 100, desde: last[0].date};\n    }).sort((a, b) => b.attach_pct - a.attach_pct).map((p, i) => ({...p, puesto: i + 1}));\n  }\n});\ndash.calc("semanas", {\n  title: "Premio por semana",\n  description: "Por semana de lunes a domingo: qué parte de los tickets con café llevan pieza, ticket medio, y el tramo de premio ganado (25/45/70 € al llegar a 50/55/60 %) si el ticket medio no baja frente a las 4 semanas anteriores. Las semanas anteriores al 26 oct 2026 se evalúan con la misma regla aunque no hubiera premio.",\n  inputs: ["tickets_co21", "categorias_co21"],\n  fn: (tickets_co21, categorias_co21) => {\n    const rows = window.caClassify(tickets_co21, categorias_co21);\n    const weekOf = d => { const x = new Date(d + "T00:00:00Z"); const dow = (x.getUTCDay() + 6) % 7; x.setUTCDate(x.getUTCDate() - dow); return x.toISOString().slice(0, 10); };\n    const W = {};\n    for (const r of rows) { const k = weekOf(r.date); const w = W[k] || (W[k] = {semana: k, tk: 0, net: 0, cafe: 0, boll: 0, dias: new Set()}); w.tk++; w.net += r.net; w.dias.add(r.date); if (r.cafe) { w.cafe++; if (r.boll) w.boll++; } }\n    const weeks = Object.values(W).sort((a, b) => a.semana < b.semana ? -1 : 1);\n    const today = window.caPeriods().today;\n    return weeks.filter((w, i) => i > 0 || w.dias.size >= 6).map((w, i) => {\n      const attach = w.cafe ? w.boll / w.cafe : null, ticket = w.tk ? w.net / w.tk : null;\n      const prev = weeks.slice(Math.max(0, i - 4), i);\n      const baseTk = prev.reduce((s, p) => s + p.tk, 0), baseNet = prev.reduce((s, p) => s + p.net, 0);\n      const baseTicket = baseTk ? baseNet / baseTk : null;\n      const actual = w.semana === weekOf(today);\n      const completa = !actual && w.dias.size >= 6;\n      const activa = true;\n      let premio = null;\n      if (activa && attach != null && ticket != null && baseTicket != null && ticket >= baseTicket) premio = attach >= .60 ? 70 : attach >= .55 ? 45 : attach >= .50 ? 25 : 0;\n      else if (activa && attach != null) premio = 0;\n      const estado = actual ? "en curso" : !completa ? "incompleta" : premio > 0 ? "ganada" : "no ganada";\n      return {semana: w.semana, dias: w.dias.size, tickets: w.tk, cafe_tk: w.cafe, con_pieza: w.boll, attach_pct: attach, ticket, ticket_base: baseTicket, premio, estado,\n        premio_txt: estado === "en curso" ? "en juego" : premio > 0 ? "🏆" : "😢"};\n    });\n  }\n});\ndash.calc("resumen", {\n  title: "Resumen de la semana",\n  description: "Semana en curso frente a las 4 semanas anteriores: café con pieza, cafés solos, piezas de más (tickets convertidos × 2,50 €) y ticket medio.",\n  inputs: ["tickets_co21", "categorias_co21"],\n  fn: (tickets_co21, categorias_co21) => {\n    const P = window.caPeriods(), rows = window.caClassify(tickets_co21, categorias_co21);\n    const w = rows.filter(r => r.date >= P.weekStart), b = rows.filter(r => r.date >= P.baseStart && r.date <= P.baseEnd);\n    const wc = w.filter(r => r.cafe), bc = b.filter(r => r.cafe);\n    const wdays = new Set(w.map(r => r.date)).size || 1;\n    const aW = wc.length ? wc.filter(r => r.boll).length / wc.length : null;\n    const aB = bc.length ? bc.filter(r => r.boll).length / bc.length : null;\n    const convertidos = (aW != null && aB != null) ? (aW - aB) * wc.length : null;\n    const tW = w.length ? w.reduce((s, r) => s + r.net, 0) / w.length : null;\n    const tB = b.length ? b.reduce((s, r) => s + r.net, 0) / b.length : null;\n    const solos = wc.length - wc.filter(r => r.boll).length;\n    return [{attach_semana_txt: aW == null ? "—" : (Math.round(aW * 100) / 10).toLocaleString("es-ES", {minimumFractionDigits: 1}), attach_semana_pct: aW, attach_base_pct: aB, attach_base_txt: aB == null ? "—" : (Math.round(aB * 100) / 10).toLocaleString("es-ES", {minimumFractionDigits: 1}),\n      solos_semana: solos, solos_dia: Math.round(solos / wdays),\n      convertidos: convertidos == null ? null : Math.round(convertidos), ganado: convertidos == null ? null : convertidos * 2.5,\n      ganado_txt: convertidos == null ? "—" : (convertidos >= 0 ? "+" : "−") + Math.abs(Math.round(convertidos)) + " piezas · " + (convertidos * 2.5 >= 0 ? "+" : "−") + Math.abs(Math.round(convertidos * 2.5)).toLocaleString("es-ES") + " €",\n      ticket_semana: tW, ticket_semana_txt: tW == null ? "—" : tW.toLocaleString("es-ES", {minimumFractionDigits: 2, maximumFractionDigits: 2}) + " €",\n      ticket_base: tB, ticket_base_txt: tB == null ? "—" : tB.toLocaleString("es-ES", {minimumFractionDigits: 2, maximumFractionDigits: 2}) + " €",\n      week_start: P.weekStart, today: P.today, dias_semana: wdays}];\n  }\n});\n\nfunction fillMarks(id, row) {\n  document.querySelectorAll(`[data-source="${id}"][data-field]`).forEach(el => {\n    el.classList.remove("dash-skeleton");\n    const f = el.dataset.field;\n    const v = row ? row[f] : null;\n    if (v == null) { el.textContent = "—"; return; }\n    if (typeof v === "number") { el.textContent = fmtN(v); return; }\n    el.textContent = String(v);\n  });\n}\nfunction cls(v) { return v == null ? "" : v >= .5 ? "ok" : v >= .4 ? "warn" : "bad"; }\nfunction drawChart(diario, base) {\n  const box = document.getElementById("chart");\n  const tip = document.getElementById("tip");\n  d3.select(box).selectAll("svg").remove();\n  diario = diario.slice(-35);\n  if (!diario.length) return;\n  const W = Math.max(280, box.clientWidth), H = 220, m = {t: 12, r: 8, b: 28, l: 36};\n  const svg = d3.select(box).append("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`);\n  const days = diario.map(d => d.date);\n  const x = d3.scaleBand().domain(days).range([m.l, W - m.r]).padding(0.25);\n  const y = d3.scaleLinear().domain([0, Math.max(0.7, d3.max(diario, d => d.attach_pct || 0))]).range([H - m.b, m.t]);\n  const P = window.caPeriods();\n  svg.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(d3.format(".0%")).tickSize(-(W - m.l - m.r))).attr("font-size", null).attr("font-family", null)\n    .call(g => g.select(".domain").remove()).call(g => g.selectAll("line").attr("stroke", "var(--cds-chart-grid)")).call(g => g.selectAll("text").attr("fill", "var(--color-fg-muted)").style("font-size", "var(--cds-font-size-caption)"));\n  const tickDays = days.filter((d, i) => i % 7 === 0);\n  svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(tickDays).tickFormat(d => d3.utcFormat("%-d %b")(new Date(d))).tickSize(0)).attr("font-size", null).attr("font-family", null)\n    .call(g => g.select(".domain").attr("stroke", "var(--cds-chart-axis)")).call(g => g.selectAll("text").attr("fill", "var(--color-fg-muted)").style("font-size", "var(--cds-font-size-caption)").attr("dy", "1.2em"));\n  svg.append("g").selectAll("rect").data(diario).join("rect")\n    .attr("x", d => x(d.date)).attr("width", x.bandwidth()).attr("rx", 3)\n    .attr("y", d => y(d.attach_pct || 0)).attr("height", d => Math.max(0, y(0) - y(d.attach_pct || 0)))\n    .attr("fill", d => d.date >= P.weekStart ? dash.colors[0] : "var(--cds-chart-muted)")\n    .on("mousemove", (ev, d) => { tip.style.display = "block"; tip.innerHTML = ""; const a = document.createElement("div"); a.className = "d"; a.textContent = d3.utcFormat("%a %-d %b")(new Date(d.date)); const b = document.createElement("div"); b.textContent = `${fmtPct(d.attach_pct)} · ${fmtN(d.con_pieza)} de ${fmtN(d.cafe_tk)} cafés`; tip.append(a, b); const r = box.getBoundingClientRect(); tip.style.left = Math.min(ev.clientX - r.left + 10, r.width - 170) + "px"; tip.style.top = (ev.clientY - r.top - 44) + "px"; })\n    .on("mouseleave", () => { tip.style.display = "none"; });\n  if (base != null) svg.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(base)).attr("y2", y(base)).attr("stroke", "var(--cds-chart-reference)").attr("stroke-dasharray", "4 4");\n}\ndash.onData(() => {\n  const r = dash.data("resumen"), t = dash.data("tandas"), d = dash.data("diario"), l = dash.data("liga");\n  const row = r.status === "ok" && r.data && r.data[0] ? r.data[0] : null;\n  fillMarks("resumen", row);\n  const rango = document.getElementById("semana-rango");\n  rango.textContent = row ? `· ${d3.utcFormat("%-d %b")(new Date(row.week_start))} – ${d3.utcFormat("%-d %b")(new Date(window.CA_MAXDATE || row.today))}` : "";\n  const lead = document.getElementById("lead");\n  if (row && row.attach_semana_pct != null && row.attach_base_pct != null) {\n    const a = Math.round(row.attach_semana_pct * 100) / 10, b = Math.round(row.attach_base_pct * 100) / 10;\n    lead.textContent = `Esta semana ${fmt10(a / 10)} de cada 10 cafés salen con pieza (antes ${fmt10(b / 10)}). ${fmtN(row.solos_dia)} cafés al día se van solos.`;\n  } else lead.textContent = "De cada 10 cafés que servís, ¿cuántos salen con una pieza?";\n\n  const liga = document.getElementById("liga"), podio = document.getElementById("podio");\n  liga.textContent = ""; podio.textContent = "";\n  const js = l.status === "ok" && Array.isArray(l.data) ? l.data : [];\n  const apodo = j => Object.entries(window.caApodos).find(([k]) => j.quien.startsWith(k))?.[1] || j.quien.split(" ")[0];\n  js.filter(j => j.puesto <= 3).forEach(j => {\n    const el = document.createElement("div"); el.className = "pod p" + j.puesto;\n    const m = document.createElement("div"); m.className = "medal"; m.textContent = ["🥇","🥈","🥉"][j.puesto - 1];\n    const nom = document.createElement("div"); nom.className = "nom"; nom.textContent = apodo(j);\n    const val = document.createElement("div"); val.className = "val"; val.textContent = fmt10(j.attach_pct);\n    const det = document.createElement("div"); det.className = "det"; det.textContent = "de cada 10";\n    el.append(m, nom, val, det); podio.append(el);\n  });\n  js.filter(j => j.puesto > 3).forEach(j => {\n    const el = document.createElement("div"); el.className = "jug";\n    const m = document.createElement("div"); m.className = "medal"; m.textContent = j.puesto + "º";\n    const mid = document.createElement("div"); const nom = document.createElement("div"); nom.className = "nom"; nom.textContent = apodo(j); mid.append(nom);\n    const val = document.createElement("div"); val.className = "val"; val.textContent = fmt10(j.attach_pct); const sm = document.createElement("small"); sm.textContent = "de cada 10"; val.append(sm);\n    el.append(m, mid, val); liga.append(el);\n  });\n  if (!js.length) { const p = document.createElement("div"); p.className = "det"; p.textContent = "Nadie llega aún a 100 cafés."; liga.append(p); }\n\n  const body = document.getElementById("tandas-body");\n  body.textContent = "";\n  const rows = t.status === "ok" && Array.isArray(t.data) ? t.data : [];\n  for (const q of rows) {\n    const tr = document.createElement("tr");\n    const c = [q.tanda.replace(/ .*$/, ""), fmtPct(q.attach_base_pct), fmtPct(q.attach_semana_pct), fmtN1(q.solos_dia)];\n    c.forEach((v, i) => { const td = document.createElement("td"); if (i === 2) { const s = document.createElement("span"); s.className = "pill " + cls(q.attach_semana_pct); s.textContent = v; td.append(s); } else td.textContent = v; tr.append(td); });\n    body.append(tr);\n  }\n  const sb = document.getElementById("semanas-body");\n  sb.textContent = "";\n  const sem = dash.data("semanas");\n  const srows = sem.status === "ok" && Array.isArray(sem.data) ? sem.data.slice(-8).reverse() : [];\n  for (const q of srows) {\n    const tr = document.createElement("tr");\n    const c = [d3.utcFormat("%-d %b")(new Date(q.semana)), fmt10(q.attach_pct), fmtEur2(q.ticket), q.premio_txt];\n    c.forEach((v, i) => { const td = document.createElement("td"); if (i === 3) { const sp = document.createElement("span"); sp.className = q.estado === "en curso" ? "cur" : ""; sp.textContent = v; td.append(sp); } else td.textContent = v; tr.append(td); });\n    sb.append(tr);\n  }\n  drawChart(d.status === "ok" && Array.isArray(d.data) ? d.data : [], row ? row.attach_base_pct : null);\n});\n'

# Adaptaciones para la versión estática
body = body.replace('<p class="lead" id="lead">', '<p class="upd">Actualizado el __UPDATED__ · datos hasta el __MAXDATE__</p>\n  <p class="lead" id="lead">')
# clasificación precalculada
script = script.replace(
    script[script.index('window.caClassify = function'):script.index('dash.calc("tandas"')],
    '''window.caClassify = function () {
  return window.CA_ROWS.slice().sort((a, b) => a.d < b.d ? -1 : a.d > b.d ? 1 : a.h - b.h).map(r => { const tanda = window.caTandas.find(([, a, b]) => r.h >= a && r.h <= b); return {date: r.d, tanda: tanda ? tanda[0] : null, cafe: !!r.c, boll: !!r.b, net: r.n, who: r.w || null}; });
};

''')
# tokens del dashboard → tokens propios
for a, b in [("var(--cds-chart-grid)", "var(--grid)"), ("var(--cds-chart-axis)", "var(--axis)"), ("var(--cds-chart-reference)", "var(--ref)"), ("var(--cds-chart-muted)", "var(--muted-bar)"), ("var(--cds-font-size-caption)", "var(--fs-caption)")]:
    script = script.replace(a, b)
script = script.replace('box.classList.toggle("dash-skeleton", d.status === "loading");', '')

import os
_d3p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d3.min.js")
d3js = open(_d3p).read() if os.path.exists(_d3p) else None
html = HTML.replace("__D3__", d3js if d3js else '</script><script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script><script>').replace("__BODY__", body).replace("__SCRIPT__", script).replace("__DATA__", DATA).replace("__MAXISO__", max_date).replace("__UPDATED__", generated).replace("__MAXDATE__", datetime.date.fromisoformat(max_date).strftime("%d/%m/%Y") if max_date else "")
open(out_path, "w").write(html)
print(f"ok {len(rows)} tickets, hasta {max_date}, {len(html)} bytes → {out_path}")
