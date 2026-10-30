/*
 * Caja de Meeseeks — firmware para ESP32 (o Arduino con botón + LED/relé).
 *
 * Qué hace:
 *   - Lee el BOTÓN gigante. Al apretarlo (con antirrebote) avisa al cerebro:
 *         EVENT button
 *   - Recibe por serial los comandos del cerebro (meeseeks.py):
 *         H1  -> enciende la luz del holograma (el ayudante "aparece")
 *         H0  -> la apaga (el ayudante "se va")
 *
 * El holograma es un Pepper's ghost: una lámina transparente a 45° refleja una
 * pantalla/LED que va DENTRO del cilindro. Aquí controlamos su retroiluminación
 * con un pin (LED potente o relé/MOSFET hacia una tira). El cerebro decide el
 * ciclo de vida; este firmware solo lo enciende, lo apaga y detecta el botón.
 *
 * Para la VOZ real: el cerebro saca la frase por serial; conéctale un DFPlayer
 * Mini + altavoz (TTS pregrabado) o reproduce el TTS desde el PC.
 */

// --- Pines (ver pinout.md). Cámbialos según tu cableado. ---
const int PIN_BOTON     = 27;   // botón gigante a GND (usa el pull-up interno)
const int PIN_HOLOGRAMA = 14;   // LED/relé/MOSFET de la luz del holograma

// --- Calibración (el mundo físico no es el ideal del papel; ajústala) ---
const unsigned long DEBOUNCE_MS = 50;    // antirrebote del botón
const unsigned long RELANZAR_MS = 4000;  // ignora reaprietes mientras el ayudante trabaja

int estadoBoton = HIGH;
unsigned long ultimoCambio = 0;
unsigned long ultimoBoton = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BOTON, INPUT_PULLUP);   // suelto = HIGH; apretado = LOW
  pinMode(PIN_HOLOGRAMA, OUTPUT);
  digitalWrite(PIN_HOLOGRAMA, LOW);   // arranca apagado (en reposo)
  Serial.println("Meeseeks listo. Aprieta el boton.");
}

void loop() {
  // 1) ¿apretaron el botón? (con antirrebote y sin dispararse mientras trabaja)
  int lectura = digitalRead(PIN_BOTON);
  if (lectura != estadoBoton && millis() - ultimoCambio > DEBOUNCE_MS) {
    ultimoCambio = millis();
    estadoBoton = lectura;
    if (estadoBoton == LOW && millis() - ultimoBoton > RELANZAR_MS) {
      ultimoBoton = millis();
      Serial.println("EVENT button");   // el cerebro arranca el ciclo de vida
    }
  }

  // 2) ¿llegó un comando del cerebro? enciende o apaga el holograma
  if (Serial.available()) {
    String linea = Serial.readStringUntil('\n');
    linea.trim();
    if (linea == "H1") digitalWrite(PIN_HOLOGRAMA, HIGH);   // aparece
    else if (linea == "H0") digitalWrite(PIN_HOLOGRAMA, LOW);  // se va
    // (cualquier otra línea es la frase para el TTS; la maneja el PC/DFPlayer)
  }
}
