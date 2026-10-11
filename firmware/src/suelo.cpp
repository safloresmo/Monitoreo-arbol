// Humedad del suelo con un sensor analógico.
#include "config.h"

#ifdef NODO_SUELO

#include "sensor.h"

static_assert(SUELO_SECO != SUELO_MOJADO, "La calibración necesita dos lecturas distintas");

void iniciarSensor() {}

void publicarLecturas(PubSubClient &mqtt) {
  int lectura = analogRead(PIN_SUELO);
  long humedad = constrain(map(lectura, SUELO_SECO, SUELO_MOJADO, 0, 100), 0, 100);

  char texto[8];
  ltoa(humedad, texto, 10);
  mqtt.publish(TEMA_SUELO, texto);
  Serial.printf("Humedad del suelo: %s %% (lectura %d)\n", texto, lectura);
}

#endif
