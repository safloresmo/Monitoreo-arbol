// Temperatura y humedad del aire con un DHT11.
#include "config.h"

#ifdef NODO_AMBIENTE

#include <DHT.h>

#include "sensor.h"

static DHT dht(PIN_DHT, DHT11);

void iniciarSensor() {
  dht.begin();
}

void publicarLecturas(PubSubClient &mqtt) {
  float humedad = dht.readHumidity();
  float temperatura = dht.readTemperature();
  if (isnan(humedad) || isnan(temperatura)) {
    Serial.println("El DHT11 no respondió");
    return;
  }

  char texto[12];
  dtostrf(temperatura, 1, 2, texto);
  mqtt.publish("limon/temperatura", texto);
  Serial.printf("Temperatura: %s °C\n", texto);

  dtostrf(humedad, 1, 2, texto);
  mqtt.publish("limon/humedad", texto);
  Serial.printf("Humedad: %s %%\n", texto);
}

#endif
