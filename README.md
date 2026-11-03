# Tablero CO21 · Café con pieza

Página estática para el equipo de Casa Comtal (CO21): % de tickets con café que llevan pieza, premio semanal y leaderboard mensual.

- `co21-7f3k/index.html` — la página publicada (datos incrustados, hasta ayer).
- `build_static.py` — generador: `python3 -I build_static.py tickets.json categorias.json co21-7f3k/index.html`.
- Una tarea programada de Claude baja los datos de Square cada día a las 6:10 y hace push de la página regenerada.
- Publicación: Cloudflare Pages conectado a este repo (build command vacío, output `/`).
