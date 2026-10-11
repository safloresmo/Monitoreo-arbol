#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include "config.h"
#include "secretos.h"
#include "sensor.h"

static WiFiClient red;
static PubSubClient mqtt(red);
static unsigned long ultimaLectura = 0;
static unsigned long ultimoIntento = 0;
static bool primerIntento = true;

static void conectarWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_RED, WIFI_CLAVE);
  Serial.printf("\nConectando a %s", WIFI_RED);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.printf("\nConectado, IP %s\n", WiFi.localIP().toString().c_str());
}

// Un intento cada pocos segundos, sin detener el resto del programa.
static void conectarMqtt() {
  if (!primerIntento && millis() - ultimoIntento < REINTENTO_MQTT_MS) {
    return;
  }
  primerIntento = false;
  ultimoIntento = millis();

  // El nombre lleva el número de serie de la placa: si dos nodos se
  // presentan con el mismo, el broker desconecta a uno cada vez que entra
  // el otro.
  char nombre[32];
  snprintf(nombre, sizeof nombre, "limon-%s-%06x", NOMBRE_NODO, ESP.getChipId());
  if (mqtt.connect(nombre, MQTT_USUARIO, MQTT_CLAVE)) {
    Serial.printf("MQTT conectado como %s\n", nombre);
  } else {
    Serial.printf("MQTT sin conexión, estado %d\n", mqtt.state());
  }
}

void setup() {
  Serial.begin(115200);
  iniciarSensor();
  conectarWifi();
  mqtt.setServer(MQTT_SERVIDOR, MQTT_PUERTO);
}

void loop() {
  if (!mqtt.connected()) {
    conectarMqtt();
    return;
  }
  mqtt.loop();

  if (millis() - ultimaLectura >= PERIODO_MS) {
    ultimaLectura = millis();
    publicarLecturas(mqtt);
  }
}
