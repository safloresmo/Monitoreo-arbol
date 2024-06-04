#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Configuración del sensor de humedad del suelo
const int sensorHumedadPin = A0; // Pin analógico para el sensor de humedad

// Variables para WiFi y MQTT
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;

// Reemplaza con tus credenciales de red y configuración de MQTT
const char* ssid = "Gilga_IOT"; // Cambia esto por tu SSID
const char* password = "GilgaRedIOT2.4G"; // Cambia esto por tu contraseña
const char* mqtt_server = "192.168.0.100"; // IP del Broker MQTT
const char* mqtt_user = "gilga"; // Usuario MQTT
const char* mqtt_password = "raspberry"; // Contraseña MQTT

// Función para conectar al WiFi
void setup_wifi() {
  delay(1000);
  Serial.begin(9600);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

// Función para reconectar al broker MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
      Serial.println("conectado");
      // Suscripciones MQTT van aquí, si son necesarias
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" intentar de nuevo en 5 segundos");
      delay(5000);
    }
  }
}

// Función de callback para MQTT (no es necesaria si solo publicas datos)
void callback(char* topic, byte* payload, unsigned int length) {
  // Se ejecuta cuando se recibe un mensaje en un topic suscrito
}

void setup() {
  setup_wifi(); // Inicializa la conexión WiFi
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  int valorSensor = analogRead(sensorHumedadPin);
  int humedad = map(valorSensor, 0, 1023, 100, 0);
  char humedadString[8];
  itoa(humedad, humedadString, 10); // Convierte el entero a cadena.
  Serial.print("Humedad del suelo: ");
  Serial.print(humedadString);
  Serial.println("%");
  client.publish("limon/suelo3", humedadString);
  Serial.println("Datos publicados");

  delay(30000); // Espera 1 segundo antes de la siguiente publicación
}
