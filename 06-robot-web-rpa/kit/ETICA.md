# Checklist ético + guía anti-bloqueo (honesta)

Un robot que opera la web puede ahorrarte horas o meterte en problemas. La
diferencia es el criterio, no el código. Antes de apuntar `rpa.py` a un sitio
real, pasa esta lista.

## Checklist ético (sí/no antes de correr)
- [ ] **¿Tengo permiso?** Mi cuenta, mi dato, o autorización explícita del dueño del sitio.
- [ ] **¿`robots.txt` lo permite?** El kit lo respeta solo; no lo esquives a mano.
- [ ] **¿Hay una API?** Si existe, úsala — es más estable y es lo correcto. RPA es para cuando NO hay API.
- [ ] **¿Estoy respetando los Términos de Servicio** del sitio?
- [ ] **¿Mi carga es razonable?** Una pausa entre pedidos, en horario de bajo tráfico, sin paralelizar a lo bestia.
- [ ] **¿Qué datos toco?** Nada personal/sensible sin base legal. No revendo lo que extraigo.
- [ ] **¿Me identifico?** User-Agent con quién soy y cómo contactarme.

## Guía anti-bloqueo — lo honesto
Lo que de verdad evita que te bloqueen **no es ocultarte, es comportarte bien**:

1. **Baja el ritmo.** La causa #1 de bloqueo es pegarle muy rápido al servidor. Sube `DELAY`.
2. **Reintenta con backoff**, no en bucle cerrado. Un 429/503 significa "espera", no "insiste ya".
3. **Identifícate.** Un bot anónimo y agresivo se banea; uno identificado y amable casi nunca.
4. **Respeta `robots.txt` y los ToS.** Si te prohíben la zona, no entres.
5. **Cachea.** No vuelvas a pedir lo que ya tienes.

Lo que **no** vas a encontrar aquí: rotación de IPs, suplantar navegadores,
resolver CAPTCHAs ni burlar anti-bots. Eso es señal de que el sitio **no quiere
ser automatizado** — y ahí el problema ya no es técnico. Pide permiso o busca
la API.
