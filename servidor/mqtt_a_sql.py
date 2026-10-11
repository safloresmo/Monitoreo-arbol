"""Guarda en MySQL lo que los nodos publican por MQTT.

La configuración se toma de las variables de entorno y, si existe, del archivo
`.env` que esté junto a este programa (ver `.env.ejemplo`).
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path

import mysql.connector
import paho.mqtt.client as mqtt

from lecturas import TEMAS, Lecturas

INSERTAR = {
    "Temperatura": "INSERT INTO Temperatura (time, HumedadA, Temperatura) VALUES (%s, %s, %s)",
    "Flujo": "INSERT INTO Flujo (time, Litros) VALUES (%s, %s)",
    "Suelo": "INSERT INTO Suelo (time, Humedad) VALUES (%s, %s)",
    "Suelo2": "INSERT INTO Suelo2 (time, Humedad) VALUES (%s, %s)",
    "Suelo3": "INSERT INTO Suelo3 (time, Humedad) VALUES (%s, %s)",
}

registro = logging.getLogger("monitoreo")


def cargar_env(ruta):
    """Lee `CLAVE=valor` por línea, sin pisar lo que ya esté en el entorno."""
    if not ruta.exists():
        return
    for linea in ruta.read_text().splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())


class Base:
    """Conexión a la base de datos que se vuelve a abrir sola si se cae."""

    def __init__(self, **datos):
        self._datos = datos
        self._conexion = None

    def guardar(self, tabla, valores):
        try:
            if self._conexion is None or not self._conexion.is_connected():
                self._conexion = mysql.connector.connect(**self._datos)
            with self._conexion.cursor() as cursor:
                cursor.execute(INSERTAR[tabla], valores)
            self._conexion.commit()
        except mysql.connector.Error as error:
            registro.error("No se pudo guardar en %s: %s", tabla, error)
            self._conexion = None
            return False
        return True


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cargar_env(Path(__file__).with_name(".env"))

    base = Base(
        host=os.environ.get("BD_SERVIDOR", "127.0.0.1"),
        port=int(os.environ.get("BD_PUERTO", "3306")),
        user=os.environ["BD_USUARIO"],
        password=os.environ["BD_CLAVE"],
        database=os.environ.get("BD_NOMBRE", "limon"),
    )
    lecturas = Lecturas()

    def al_conectar(cliente, _datos, _banderas, codigo, _propiedades):
        if codigo.is_failure:
            registro.error("El broker rechazó la conexión: %s", codigo)
            return
        # Suscribirse aquí hace que también se recupere tras una reconexión.
        cliente.subscribe([(tema, 1) for tema in TEMAS])
        registro.info("Conectado al broker, escuchando %d temas", len(TEMAS))

    def al_recibir(_cliente, _datos, mensaje):
        texto = mensaje.payload.decode("utf-8", errors="replace").strip()
        try:
            fila = lecturas.procesar(mensaje.topic, texto, time.monotonic())
        except ValueError as error:
            registro.warning("Mensaje descartado en %s: %s", mensaje.topic, error)
            return
        if fila is None:
            return
        tabla, valores = fila
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if base.guardar(tabla, (ahora, *valores)):
            registro.info("%s <- %s", tabla, valores)

    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="limon-servidor")
    cliente.username_pw_set(os.environ.get("MQTT_USUARIO"), os.environ.get("MQTT_CLAVE"))
    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir
    cliente.connect(
        os.environ.get("MQTT_SERVIDOR", "127.0.0.1"),
        int(os.environ.get("MQTT_PUERTO", "1883")),
        keepalive=60,
    )
    cliente.loop_forever()


if __name__ == "__main__":
    main()
