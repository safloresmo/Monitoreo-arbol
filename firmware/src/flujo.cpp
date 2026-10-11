// Agua de riego con un sensor de flujo de pulsos.
#include "config.h"

#ifdef NODO_FLUJO

#include "sensor.h"

static volatile unsigned long pulsos = 0;

static void IRAM_ATTR contarPulso() {
  pulsos++;
}

void iniciarSensor() {
  pinMode(PIN_FLUJO, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_FLUJO), contarPulso, RISING);
}

// Publica los litros que pasaron desde la publicación anterior.
void publicarLecturas(PubSubClient &mqtt) {
  noInterrupts();
  unsigned long contados = pulsos;
  pulsos = 0;
  interrupts();

  char texto[12];
  dtostrf(contados / PULSOS_POR_LITRO, 1, 2, texto);
  if (mqtt.publish("limon/volumen", texto)) {
    Serial.printf("Volumen: %s L\n", texto);
  } else {
    // No salió: el agua contada se suma a la próxima publicación.
    noInterrupts();
    pulsos += contados;
    interrupts();
  }
}

#endif
