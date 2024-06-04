import mysql.connector  # Para hablar con la base de datos
import paho.mqtt.client as mqtt  # Para comunicarse usando MQTT, que es como enviar mensajes entre dispositivos
from datetime import datetime  # Para saber la fecha y hora

# Configuración de la base de datos
db = mysql.connector.connect(
    host="192.168.0.100",  # La dirección donde está la base de datos
    user="ssh",            # El nombre de usuario para entrar a la base de datos
    password="raspberry",  # La contraseña para entrar
    database="limon"       # El nombre de la base de datos que vamos a usar
)

# Configuración del cliente MQTT
mqtt_host = "192.168.0.100"  # La dirección del lugar que maneja los mensajes MQTT
mqtt_user = "gilga"          # El nombre de usuario para MQTT
mqtt_password = "raspberry"  # La contraseña para MQTT

# Aquí vamos a guardar los valores de los sensores
valores_sensores = {
    'humedad': None,
    'temperatura': None,
    'lph': None
}

def on_connect(client, userdata, flags, rc):
    print("¡Conectado! Código de respuesta: " + str(rc))  # Nos dice que la conexión fue exitosa
    # Nos suscribimos a estos temas para recibir actualizaciones
    client.subscribe("limon/humedad")
    client.subscribe("limon/temperatura")
    client.subscribe("limon/volumen")
    client.subscribe("limon/suelo")
    client.subscribe("limon/suelo2")
    client.subscribe("limon/suelo3")

def on_message(client, userdata, msg):
    global valores_sensores  # Usamos la variable global
    topic = msg.topic  # El tema del mensaje
    payload = msg.payload.decode('utf-8')  # Lo que viene en el mensaje
    print(f"Recibí '{payload}' de '{topic}'")
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # La hora y fecha actual
    
    # Guardamos la información dependiendo de donde viene
    if topic == "limon/temperatura":
        valores_sensores['temperatura'] = payload
    elif topic == "limon/humedad":
        valores_sensores['humedad'] = payload
    elif topic == "limon/volumen":
        valores_sensores['lph'] = payload
        insertar_flujo(current_time, valores_sensores['lph'])  # Guardamos el flujo en la base de datos
    elif topic == "limon/suelo":
        insertar_humedad_suelo(current_time, payload)  # Guardamos la humedad del suelo en la base de datos
    elif topic == "limon/suelo2":
        insertar_humedad_suelo2(current_time, payload)  # Guardamos la humedad del suelo en la base de datos
    elif topic == "limon/suelo3":
        insertar_humedad_suelo3(current_time, payload)  # Guardamos la humedad del suelo en la base de datos    
    
    
    # Si tenemos tanto la humedad como la temperatura, guardamos ambos en la base de datos
    if valores_sensores['humedad'] is not None and valores_sensores['temperatura'] is not None:
        insertar_sensores(current_time, valores_sensores['humedad'], valores_sensores['temperatura'])
        valores_sensores['humedad'] = None  # Reiniciamos los valores
        valores_sensores['temperatura'] = None

# Funciones para guardar datos en la base de datos
def insertar_sensores(tiempo, humedad, temperatura):
    cursor = db.cursor()  # Creamos un cursor para ejecutar consultas
    cursor.execute(
        "INSERT INTO Temperatura (time, HumedadA, Temperatura) VALUES (%s, %s, %s)",
        (tiempo, humedad, temperatura)
    )
    db.commit()  # Confirmamos la operación
    print("He guardado los datos de los sensores en la base de datos.")
    

def insertar_flujo(tiempo, lph):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Flujo (time, LpH) VALUES (%s, %s)",
        (tiempo, lph)
    )
    db.commit()
    print("He guardado los datos de flujo en la base de datos.")
    valores_sensores['lph'] = None  # Reiniciamos el valor de LpH

def insertar_humedad_suelo(tiempo, humedad_suelo):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Suelo (time, Humedad) VALUES (%s, %s)",
        (tiempo, humedad_suelo)
    )
    db.commit()
    print("He guardado la humedad del suelo en la base de datos.")

def insertar_humedad_suelo2(tiempo, humedad_suelo):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Suelo2 (time, Humedad) VALUES (%s, %s)",
        (tiempo, humedad_suelo)
    )
    db.commit()
    print("He guardado la humedad del suelo 2 en la base de datos.")

def insertar_humedad_suelo3(tiempo, humedad_suelo):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Suelo3 (time, Humedad) VALUES (%s, %s)",
        (tiempo, humedad_suelo)
    )
    db.commit()
    print("He guardado la humedad del suelo 3 en la base de datos.")

client = mqtt.Client()  # Creamos un nuevo cliente MQTT
client.username_pw_set(mqtt_user, mqtt_password)  # Configuramos el usuario y contraseña
client.on_connect = on_connect  # Qué hacer cuando nos conectemos
client.on_message = on_message  # Qué hacer cuando recibamos un mensaje

client.connect(mqtt_host, 1883, 60)  # Nos conectamos al servidor MQTT
client.loop_forever()  # Mantenemos la conexión abierta siempre
