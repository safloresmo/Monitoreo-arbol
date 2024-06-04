#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define SENSOR_FLUJO_PIN D5 // El pin D5 (GPIO14) del ESP8266 donde se conecta el sensor de flujo
volatile int pulsosPorLitro = 450; // Este valor puede variar dependiendo del sensor de flujo
volatile unsigned int pulsos = 0; // Contador de pulsosx
unsigned long tiempoAnterior = 0; // Para calcular el tiempo entre pulsos

WiFiClient espClient;
PubSubClient client(espClient);
 
const char* ssid = "Gilga_IOT"; // Cambia esto por tu SSID
const char* password = "GilgaRedIOT2.4G"; // Cambia esto por tu contraseña
const char* mqtt_server = "192.168.0.100"; // IP del Broker MQTT
const char* mqtt_user = "gilga"; // Usuario MQTT
const char* mqtt_password = "raspberry"; // Contraseña MQTT

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  // Ahora está conectado
}

void ICACHE_RAM_ATTR contarPulsos() {
  pulsos++;
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
      // Conectado al broker MQTT
    } else {
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Aquí se manejan los mensajes MQTT entrantes
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pinMode(SENSOR_FLUJO_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SENSOR_FLUJO_PIN), contarPulsos, RISING);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (millis() - tiempoAnterior > 30000) { // Cambio de 1000 a 60000 para actualizar cada minuto
    tiempoAnterior = millis();
    detachInterrupt(digitalPinToInterrupt(SENSOR_FLUJO_PIN));

    float litros = pulsos / (float)pulsosPorLitro; // Calcular el volumen en litros
    pulsos = 0;

    attachInterrupt(digitalPinToInterrupt(SENSOR_FLUJO_PIN), contarPulsos, RISING);

    char litrosString[10];
    dtostrf(litros, 1, 2, litrosString);
    Serial.println("litrosString");
    client.publish("limon/volumen", litrosString); // Publica los litros al MQTT
  }
}
