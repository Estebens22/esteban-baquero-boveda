/*
 * Frank — firmware para ESP32 (o Arduino con servo + NeoPixel).
 *
 * Qué hace:
 *   - Lee el micrófono (nivel de sonido) y, si pasa el umbral, avisa "speech".
 *   - Recibe por serial los comandos del cerebro (frank.py):
 *         S<angulo> L<rrggbb> "<frase>"
 *     y mueve la cabeza (servo), pinta los ojos (LED) y "dice" la frase
 *     (aquí la sacamos por serial; conecta un DFPlayer/altavoz si quieres voz real).
 *
 * El cerebro decide QUÉ reacción; este firmware solo la ejecuta en el mundo físico.
 *
 * Librerías (desde el Library Manager del IDE de Arduino):
 *   - ESP32Servo
 *   - Adafruit_NeoPixel
 */
#include <ESP32Servo.h>
#include <Adafruit_NeoPixel.h>

// --- Pines (ver pinout.md). Cámbialos según tu cableado. ---
const int PIN_SERVO = 13;   // servo de la cabeza
const int PIN_LED   = 12;   // DIN del anillo/pixeles de los ojos
const int PIN_MIC   = 34;   // salida analógica del módulo de micrófono (solo ADC1 en ESP32)
const int NUM_LEDS  = 2;    // dos ojos

// --- Calibración (el mundo físico no es el ideal del papel; ajústala) ---
const int SERVO_TRIM   = 0;     // suma/resta grados si Frank mira torcido
const int MIC_BASELINE = 1800;  // lectura ADC en silencio (mídela con el Monitor Serie)
const int MIC_TRIGGER  = 600;   // cuánto debe subir sobre el baseline para contar como voz

Servo head;
Adafruit_NeoPixel eyes(NUM_LEDS, PIN_LED, NEO_GRB + NEO_KHZ800);
unsigned long lastSound = 0;

void setup() {
  Serial.begin(115200);
  head.attach(PIN_SERVO);
  head.write(90 + SERVO_TRIM);      // reposo
  eyes.begin();
  setEyes(0x1133aa);                // calmo
  Serial.println("Frank listo.");
}

void setEyes(long rgb) {
  for (int i = 0; i < NUM_LEDS; i++)
    eyes.setPixelColor(i, eyes.Color((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF));
  eyes.show();
}

// Procesa una línea:  S124 Lffcc00 "hola"
void runCommand(String line) {
  int sPos = line.indexOf('S');
  int lPos = line.indexOf('L');
  int qPos = line.indexOf('"');
  if (sPos < 0 || lPos < 0) return;

  int angle = line.substring(sPos + 1, line.indexOf(' ', sPos)).toInt();
  long rgb  = strtol(line.substring(lPos + 1, lPos + 7).c_str(), NULL, 16);
  head.write(constrain(angle + SERVO_TRIM, 0, 180));
  setEyes(rgb);

  if (qPos >= 0) {
    String phrase = line.substring(qPos + 1, line.lastIndexOf('"'));
    Serial.print("Frank dice: "); Serial.println(phrase);  // conecta un altavoz aquí
  }
}

void loop() {
  // 1) ¿alguien habló? avisa al cerebro con el nivel normalizado 0..1
  int mic = analogRead(PIN_MIC);
  int over = mic - MIC_BASELINE;
  if (over > MIC_TRIGGER && millis() - lastSound > 400) {
    float level = (float)(over - MIC_TRIGGER) / (4095 - MIC_BASELINE - MIC_TRIGGER);
    if (level > 1) level = 1;
    Serial.print("EVENT speech "); Serial.println(level, 2);
    lastSound = millis();
  }

  // 2) ¿llegó un comando del cerebro? ejecútalo
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length()) runCommand(line);
  }
}
