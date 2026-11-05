#!/usr/bin/env python3
"""Baja de Square Reporting los dos JSON que necesita build_static.py.

Uso: SQUARE_ACCESS_TOKEN=... python3 fetch_square.py tickets_co21.json categorias_co21.json
Requiere un token con permiso REPORTING_READ.
"""
import json, os, sys, time, urllib.request

TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN")
if not TOKEN:
    sys.exit("Falta SQUARE_ACCESS_TOKEN")
URL = "https://connect.squareup.com/reporting/v1/load"
LOCATION = "Casa Comtal (CO21)"

Q_TICKETS = {"query": {
    "measures": ["Sales.net_sales"],
    "dimensions": ["Sales.order_id", "Sales.local_date", "Sales.local_hour", "Sales.item_quantities", "Sales.team_member_collected_by_name"],
    "filters": [{"member": "Sales.location_name", "operator": "equals", "values": [LOCATION]}],
    "timeDimensions": [{"dimension": "Sales.reporting_day", "dateRange": "last 91 days"}],
    "limit": 12000, "timezone": "Europe/Madrid"}}

Q_CATS = {"query": {
    "measures": ["ProductMixReport.items_sold_quantity"],
    "dimensions": ["ProductMixReport.item_name", "ProductMixReport.category_name"],
    "filters": [{"member": "ProductMixReport.location_name", "operator": "equals", "values": [LOCATION]}],
    "timeDimensions": [{"dimension": "ProductMixReport.reporting_day", "dateRange": "last 91 days"}],
    "limit": 1000, "timezone": "Europe/Madrid"}}


def load(query, tries=20):
    body = json.dumps(query).encode()
    for i in range(tries):
        req = urllib.request.Request(URL, data=body, method="POST", headers={
            "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.loads(r.read().decode())
        if isinstance(res, dict) and res.get("error") == "Continue wait":
            time.sleep(3); continue
        if "data" not in res:
            sys.exit(f"Respuesta inesperada de Square: {json.dumps(res)[:500]}")
        return res["data"]
    sys.exit("Square no terminó la consulta a tiempo")


out_t, out_c = sys.argv[1:3]
tickets = load(Q_TICKETS)
cats = load(Q_CATS)
if len(tickets) < 3000:
    sys.exit(f"Pocos tickets ({len(tickets)}); no actualizo")
if len(cats) < 40:
    sys.exit(f"Pocas categorías ({len(cats)}); no actualizo")
json.dump(tickets, open(out_t, "w"), ensure_ascii=False)
json.dump(cats, open(out_c, "w"), ensure_ascii=False)
print(f"ok {len(tickets)} tickets, hasta {max(r['Sales.local_date'] for r in tickets)}; {len(cats)} artículos")
