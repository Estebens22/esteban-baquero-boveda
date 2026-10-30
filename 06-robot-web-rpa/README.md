# 06 · Robot que opera la web (RPA)

**Estado:** Experimento · **Tema:** Automatización

Un robot que usa la web como tú: navega, lee formularios, los llena, los envía y extrae datos — **con ética**. Aprende haciendo: el kit corre en 10 segundos con solo Python, sin instalar nada.

## Qué vas a construir
- **El navegador controlado** — leer formularios, tablas y títulos del HTML con la librería estándar.
- **Los pasos repetibles** — llenar un formulario sin borrar sus campos ocultos ni el token anti-CSRF, y enviarlo.
- **El manejo de errores y reintentos** — backoff creciente y pausa entre pedidos para no martillar el servidor.

## Corre el ejemplo
```bash
cd kit
python3 rpa.py --demo
python3 rpa.py form https://ejemplo.co
```

## La idea en una línea
Cuando **no hay API**, el robot opera la interfaz — con límites y responsabilidad. Si hay API, usa la API.

## Los errores clásicos (honesto)
- **Pisar el token anti-CSRF** al llenar el form → el kit parte de los campos del form y solo sobreescribe los tuyos.
- **Martillar el servidor** → pausa entre pedidos y backoff; la causa #1 de bloqueo es ir muy rápido.
- **Ignorar `robots.txt` y los ToS** → el kit respeta `robots.txt`; el criterio ético es tuyo (ver `kit/ETICA.md`).

## El límite honesto
Esto opera por HTTP, **no renderiza JavaScript**. Para sitios 100% JS toca un navegador real (Playwright/Selenium) — mismo flujo de pasos, otra caja que ejecuta.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
