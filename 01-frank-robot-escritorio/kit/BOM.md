# BOM — Lista de materiales de Frank

Lo mínimo para tener a Frank vivo en tu escritorio. Precios de referencia (varían).

| # | Pieza | Para qué | Cant. | Aprox. USD |
|---|-------|----------|-------|-----------|
| 1 | ESP32 DevKit (WROOM-32) | el cerebro embebido (WiFi + ADC + PWM) | 1 | 6 |
| 2 | Servo SG90 (9 g) | mueve la cabeza | 1 | 2 |
| 3 | Anillo/tira NeoPixel (2+ LEDs WS2812) | los ojos | 1 | 3 |
| 4 | Módulo micrófono MAX9814 o KY-037 | que te escuche | 1 | 3 |
| 5 | (Opcional) DFPlayer Mini + altavoz 3 W | que te hable de verdad | 1 | 5 |
| 6 | Fuente 5 V / 2 A + cable USB | alimentación | 1 | 4 |
| 7 | Cables dupont + mini protoboard | conexiones | — | 3 |
| 8 | Filamento PLA (~80 g) | la carcasa impresa | — | 2 |
| 9 | Tornillos M2/M3 + inserto para el servo | ensamble | — | 2 |

**Total aproximado: ~30 USD** (sin el altavoz opcional, ~25).

Notas:
- El micrófono va a un pin **ADC1** del ESP32 (GPIO 32–39); ADC2 no funciona con WiFi activo.
- El NeoPixel se alimenta a 5 V pero su DIN acepta la señal 3.3 V del ESP32 de cerca sin problema; a más LEDs, usa un level shifter.
- El servo SG90 puede tironear la fuente: dale su propia línea de 5 V y une las masas (GND común).
