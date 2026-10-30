/*
 * walker.ino — controlador de patas del robot bípedo (boceto para ESP32).
 *
 * El "cerebro" (la política RL) corre en una Raspberry Pi / PC y manda por serial
 * los ángulos de cada articulación. Este firmware los recibe y mueve los servos,
 * con límites de seguridad por articulación. En un bípedo real son >= 6 servos
 * (2 cadera, 2 rodilla, 2 tobillo); aquí se muestra el patrón con un arreglo.
 *
 * Seguridad: SIEMPRE limitar el ángulo por servo (clamp). Un comando fuera de rango
 * puede trabar o quemar un servo. Energiza los servos con fuente aparte, GND común.
 */
#include <ESP32Servo.h>

const int N = 6;                       // articulaciones
const int PIN[N]   = {13, 12, 14, 27, 26, 25};
const int MINA[N]  = {30, 30, 20, 20, 40, 40};   // límite inferior por servo (grados)
const int MAXA[N]  = {150,150,160,160,140,140};  // límite superior por servo
Servo servo[N];

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < N; i++) { servo[i].attach(PIN[i]); servo[i].write(90); }
}

void loop() {
  // Protocolo: una línea "a0 a1 a2 a3 a4 a5\n" con los ángulos objetivo.
  if (Serial.available()) {
    for (int i = 0; i < N; i++) {
      int a = Serial.parseInt();
      a = constrain(a, MINA[i], MAXA[i]);   // clamp de seguridad por articulación
      servo[i].write(a);
    }
  }
}
