"""Publica lecturas inventadas como lo harían los nodos.

Sirve para probar el servidor sin hardware. Usa la misma configuración que
`mqtt_a_sql.py`.

    python local/simular_nodos.py --ciclos 3 --periodo 2
"""

import argparse
import os
import random
import sys
import time
from pathlib import Path

import paho.mqtt.client as mqtt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lecturas import TEMAS_SUELO
from mqtt_a_sql import cargar_env


def lecturas():
    yield "limon/temperatura", f"{random.uniform(18, 32):.2f}"
    yield "limon/humedad", f"{random.uniform(35, 80):.2f}"
    yield "limon/volumen", f"{random.choice([0, 0, 0.4, 1.1]):.2f}"
    for tema in TEMAS_SUELO:
        yield tema, str(random.randint(20, 70))


def main():
    opciones = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    opciones.add_argument("--ciclos", type=int, default=1, help="cuántas veces publicar")
    opciones.add_argument("--periodo", type=float, default=30.0, help="segundos entre ciclos")
    opciones = opciones.parse_args()

    cargar_env(Path(__file__).resolve().parent.parent / ".env")
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="limon-simulador")
    cliente.username_pw_set(os.environ.get("MQTT_USUARIO"), os.environ.get("MQTT_CLAVE"))
    cliente.connect(os.environ.get("MQTT_SERVIDOR", "127.0.0.1"), int(os.environ.get("MQTT_PUERTO", "1883")))
    cliente.loop_start()

    for ciclo in range(opciones.ciclos):
        if ciclo:
            time.sleep(opciones.periodo)
        for tema, texto in lecturas():
            cliente.publish(tema, texto, qos=1).wait_for_publish()
            print(f"{tema} <- {texto}")

    cliente.loop_stop()
    cliente.disconnect()


if __name__ == "__main__":
    main()
