# BOM — Lista de materiales de la Caja de Meeseeks

Lo mínimo para tener la caja viva sobre tu escritorio. Precios de referencia (varían).
El holograma es un **Pepper's ghost**: una lámina transparente a 45° refleja una
pantalla o un LED que va dentro del cilindro. Barato y sorprendente.

| # | Pieza | Para qué | Cant. | Aprox. USD |
|---|-------|----------|-------|-----------|
| 1 | ESP32 DevKit (WROOM-32) | el cerebro embebido (lee botón, maneja holograma) | 1 | 6 |
| 2 | Botón gigante arcade (60 mm) | el "apriétame" que invoca al ayudante | 1 | 3 |
| 3 | Lámina de acrílico/PET transparente | el espejo a 45° del Pepper's ghost | 1 | 2 |
| 4 | Pantalla pequeña o tira/anillo LED WS2812 | la "imagen" del ayudante dentro del cilindro | 1 | 3–8 |
| 5 | Transistor MOSFET (p. ej. IRLZ44N) o módulo relé | encender/apagar la luz del holograma desde un pin | 1 | 2 |
| 6 | Micrófono USB o módulo I2S (INMP441) | que te escuche (STT) | 1 | 4 |
| 7 | DFPlayer Mini + altavoz 3 W (o altavoz del PC) | que te responda (TTS) | 1 | 5 |
| 8 | Fuente 5 V / 2 A + cable USB | alimentación | 1 | 4 |
| 9 | Cables dupont + mini protoboard | conexiones | — | 3 |
| 10 | Filamento PLA (~120 g) | la caja + el cilindro + la tapa del botón | — | 3 |
| 11 | Tornillos M2/M3 | ensamble | — | 2 |

**Total aproximado: ~35–45 USD** (según uses pantalla o tira LED; sin PC para STT/TTS).

Notas:
- El **STT y el TTS** pueden correr en tu PC (el cerebro `meeseeks.py` ya habla con la IA);
  el DFPlayer es opcional si prefieres que la voz salga del altavoz del computador.
- El micrófono I2S va a pines digitales; un micrófono USB se conecta directo al PC — más simple para empezar.
- La luz del holograma puede tironear corriente: contrólala con el MOSFET/relé, **no** directo desde el pin del ESP32.
- Masa común (GND) entre ESP32, botón, holograma y micrófono.
