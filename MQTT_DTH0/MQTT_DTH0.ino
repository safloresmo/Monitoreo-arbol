#include <Arduino.h>        //Libreria para que funcione
#include <ESP8266WiFi.h>           //Libreria para wifi
#include <PubSubClient.h>    //Libreria mosquitto
#include <Adafruit_Sensor.h>//Libreria de sensores
#include <DHT.h>            //Libreria del sensor

#define DHTPIN D4           //Pin donde está conectado el sensor DHT11
#define DHTTYPE DHT11       //Tipo de sensor DHT

DHT dht(DHTPIN, DHTTYPE);       //Inicializa el tipo de sensor y el pin al que se está conectado
float temperatura = 0;          //Variable donde se guardara el valor de la temperatura del sensor
float humedad = 0;              //Variable donde se guardara el valor de la humedad del sensor
char tempString[12];            //Variable temperatura que se mandara el broker (se tienen que mandar en tipo char)
char humString[8];              //Variable humedad que se mandara el broker (se tienen que mandar en tipo char)
WiFiClient espClient;           //Crea un cliente para conectarse a Wi-Fi
PubSubClient client(espClient); //Crea un cliente para publicar y suscribirse a MQTT
long lastMsg = 0;               //Variable usada más adelante
char msg[50];                   //Variable usada mas adelante

//---------		Credenciales WiFi		--------

const char* ssid = "Gilga_IOT"; //Nombre de la red Wi-Fi
const char* password = "GilgaRedIOT2.4G"; //Contraseña de la red

//---------	Direccion IP del Broker MQTT	--------
const char* mqtt_server = "192.168.0.100"; //Direccion IP del Broker
const char* mqtt_user = "gilga";    //Usuario para conectar al broker
const char* mqtt_password = "raspberry";       //Contraseña de dicho usuario

//----------------		VOID SETUP_WIFI()		------------
//			Realiza conexion con el wifi
void setup_wifi(){
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid,password);    //Hace la conexión a Wi-Fi con el Nombre de red y contraseña
  while(WiFi.status() != WL_CONNECTED){
    delay(1000);
    Serial.print(".");          //Mientras no se conecte se mostrará un punto
  }                             //Se conecto
  Serial.println("");
  Serial.println("Wifi conectado");
  Serial.println("IP adreess: ");
  Serial.println(WiFi.localIP());//Muestra la IP asignada
}

//------------------VOID CALLBACK()--------------Realiza conexion MQTT(Suscriber: recibe datos)
void callback(char* topic, byte* message, unsigned int lenght){
  Serial.print("Mensaje recibido en topic: ");
  Serial.print(topic);              //Se muestra el topico de donde se manda el mensaje
  Serial.print(", Mensaje: ");
  String messageTemp;               //Se crea una variable para guardar el mensaje recibido
  for (int i = 0;i < lenght;i++){
    Serial.print((char)message[i]); //Se extrae el mensaje caracter por caracter y se imprime
    messageTemp += (char)message[i];
  }
  Serial.println();
}  

void setup() {                         //Se inicializa lo que necesito
  Serial.begin(9600);                  //Velocidad de conexion ESP32-Terminal
  dht.begin();                         //Necesario para recibir datos del sensor
  setup_wifi();                        //Función para conectarse a Wifi
  client.setServer (mqtt_server, 1883);//Establece conexión con el servidor MQTT
  client.setCallback(callback);//Cada que llegue un mensaje se ejecutara la funcion callback, para mostrar mensajes
}

//------------------------VOID RECONNECT----------------Reconexion en caso de fallo
void reconnect(){
  while (!client.connected()){    //Mientras no se conecte...
    Serial.print("Intentando conexion MQTT...");
    if (client.connect("ESP32Client",mqtt_user, mqtt_password)){//Conecta con el usuario y contraseña admitidos
      Serial.println("Conectado");
      client.subscribe("canalabierto");//Se suscribe al topic "canalabierto"
      //Se puede suscribir a más canales

    }
    else {//Si no se puede conectar se intentara de nuevo
      Serial.print("Fallo rc= ");
      Serial.print(client.state());
      Serial.println(" Se intentará de nuevo e 5 segundos");
      delay(5000); 
    }
  }
}

void loop(){//Código que se ejecutara continuamente
  if (!client.connected()){
    reconnect();//Si no se está conectado al broker, establece conexión
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 30000){//Tiempo de muestreo, en este caso, cada 5 segundos se leera el sensor
    lastMsg = now;

    humedad = dht.readHumidity();//Lee el valor de humedad del sensor y lo guarda en una variable 
    temperatura = dht.readTemperature();//Lee el valor de temperatura del sensor y lo guarda en una variable

    if (!isnan(humedad) && !isnan(temperatura)) {//revisar si se estan recibiendo datos del sensor
     //************Señal 1 que se enviara************
    dtostrf(temperatura,1,2,tempString);//Cambia los decimales de la variable float a una cadena de caracteres (char)
    Serial.print("Temperatura: ");
    Serial.println(tempString);
    client.publish("limon/temperatura",tempString); //Publica al topic 'esp32/sensores/temperature'

    //************	Señal 2 que se enviar	a************
    dtostrf(humedad,1,2,humString);//Cambia los decimales de la variable float a una cadena de caracteres (char)
    Serial.print("Humedad: ");
    Serial.println(humString);
    client.publish("limon/humedad",humString); //Publica al topic 'esp32/sensores/humidity

  }
  }
}