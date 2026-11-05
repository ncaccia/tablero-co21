# Tablero CO21 · Café con pieza

Página estática para el equipo de Casa Comtal (CO21): % de tickets con café que llevan pieza, premio semanal y leaderboard mensual.

- `public/co21-7f3k/index.html` — la página publicada (datos incrustados, hasta ayer).
- `build_static.py` — generador: `python3 -I build_static.py tickets.json categorias.json public/co21-7f3k/index.html`.
- `fetch_square.py` — baja los dos JSON de Square Reporting (token con `REPORTING_READ` en el secreto `SQUARE_ACCESS_TOKEN`).
- El GitHub Action `update.yml` corre cada día a las 6:10 (Madrid): baja datos, regenera la página y hace push. También se puede lanzar a mano desde Actions → Run workflow.
- Publicación: Cloudflare Workers conectado a este repo: deploy command `npx wrangler deploy` (sirve `public/` como assets estáticos, ver `wrangler.jsonc`).
