# Kit — Robot que opera la web (RPA)

Corre con **solo Python** (librería estándar, sin instalar nada).

```bash
python3 rpa.py --demo                    # self-check offline (no toca la red)
python3 rpa.py get   https://ejemplo.co  # descarga y muestra el título
python3 rpa.py form  https://ejemplo.co  # lista formularios y sus campos
python3 rpa.py table https://ejemplo.co  # extrae la primera tabla
```

## Las 3 piezas que construyes
1. **El navegador controlado** — parsers con `html.parser`: leen formularios, tablas y títulos del HTML que manda el servidor.
2. **Los pasos repetibles** — `fill()` llena un formulario **sin pisar** sus campos ocultos ni el token anti-CSRF; `submit()` lo envía por GET o POST resolviendo el `action` relativo.
3. **El manejo de errores y reintentos** — `backoff()` crece (1s, 2s, 4s…) ante fallos transitorios, y hay una pausa entre pedidos para no martillar el servidor.

## El límite honesto
Esto opera la web por **HTTP, no renderiza JavaScript**. Sirve para la mayoría de formularios y páginas con HTML en el servidor. Si el sitio arma todo con JS en el navegador, ahí sí toca un navegador real (Playwright/Selenium) — mismo flujo de pasos, otra caja que ejecuta.

## Antes de correrlo contra un sitio real
Lee `ETICA.md`. El robot **respeta `robots.txt`**, se identifica con un User-Agent claro y espera entre pedidos. La ética es tuya, no del script: automatiza lo que tienes permiso de automatizar.
