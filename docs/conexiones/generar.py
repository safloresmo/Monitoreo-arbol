"""Dibuja los diagramas de conexiones de los nodos.

Coloca las piezas de `piezas/` y traza los cables entre sus pines. Las
ilustraciones de la NodeMCU y del sensor de suelo son de la biblioteca de
piezas de Fritzing (CC BY-SA 3.0).

    python docs/conexiones/generar.py
"""

import re
from pathlib import Path

AQUI = Path(__file__).parent

ROJO, NEGRO, AMARILLO = "#d8262c", "#3a3a3a", "#f2c200"

# Centro de los pines de la NodeMCU, en las unidades de su dibujo.
NODEMCU = {
    "A0": (3.08, 17.34),
    "GND_IZQ": (3.08, 110.47),
    "VIN": (3.08, 117.57),
    "D4": (67.36, 45.99),
    "D5": (67.36, 67.47),
    "GND_DER": (67.36, 110.47),
    "3V3_DER": (67.36, 117.57),
    "3V3_MEDIO": (67.36, 53.15),
    "GND_MEDIO": (67.36, 60.31),
}
DHT11 = {"DAT": (4.1, 8.96), "VCC": (4.1, 16.12), "GND": (4.1, 23.28)}
FLUJO = {"NEGRO": (48.6, 11.0), "ROJO": (54.0, 11.0), "AMARILLO": (59.4, 11.0)}
# El sensor de suelo se dibuja girado, con los pines hacia la izquierda.
SUELO = {"SIG": (10.2, 22.03), "GND": (10.2, 32.46), "VCC": (10.2, 42.88)}


def pieza(nombre, x, y, giro=0):
    """Devuelve el dibujo de una pieza colocado en `(x, y)`."""
    texto = (AQUI / "piezas" / f"{nombre}.svg").read_text()
    ancho, alto = (float(n) for n in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', texto).groups())
    cuerpo = texto[texto.index(">", texto.index("<svg")) + 1 : texto.rindex("</svg>")]
    cuerpo = re.sub(r"<desc>.*?</desc>", "", cuerpo, flags=re.S)
    if giro == -90:
        # El borde de arriba pasa a la izquierda.
        return f'<g transform="translate({x} {y + ancho}) rotate(-90)">{cuerpo}</g>'
    return f'<g transform="translate({x} {y})">{cuerpo}</g>'


def en(pines, x, y):
    return {nombre: (px + x, py + y) for nombre, (px, py) in pines.items()}


def cable(color, *puntos):
    trazo = " ".join(f"{x:.2f},{y:.2f}" for x, y in puntos)
    comun = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return (
        f'<polyline points="{trazo}" {comun} stroke="#000000" stroke-opacity="0.45" stroke-width="3.4"/>'
        f'<polyline points="{trazo}" {comun} stroke="{color}" stroke-width="2.4"/>'
    )


def etiqueta(texto, x, y):
    return (
        f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Verdana, sans-serif" '
        f'font-size="3.4" fill="#333333">{texto}</text>'
    )


def guardar(nombre, ancho, alto, *partes):
    escala = 4
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho * escala}" height="{alto * escala}" '
        f'viewBox="0 0 {ancho} {alto}">'
        f'<rect width="{ancho}" height="{alto}" fill="#ffffff"/>' + "".join(partes) + "</svg>\n"
    )
    (AQUI / f"{nombre}.svg").write_text(svg)


def ambiente():
    placa = en(NODEMCU, 12, 10)
    sensor = en(DHT11, 122, 47)
    guardar(
        "ambiente",
        190,
        158,
        pieza("nodemcu", 12, 10),
        pieza("dht11", 122, 47),
        cable(AMARILLO, placa["D4"], sensor["DAT"]),
        cable(ROJO, placa["3V3_MEDIO"], sensor["VCC"]),
        cable(NEGRO, placa["GND_MEDIO"], sensor["GND"]),
    )


def flujo():
    placa = en(NODEMCU, 26, 10)
    sensor = en(FLUJO, 8, 160)
    negro, rojo, amarillo = sensor["NEGRO"], sensor["ROJO"], sensor["AMARILLO"]
    guardar(
        "flujo",
        124,
        228,
        pieza("nodemcu", 26, 10),
        pieza("sensor_flujo", 8, 160),
        cable(NEGRO, placa["GND_IZQ"], (10, placa["GND_IZQ"][1]), (10, 158), (negro[0], 158), negro),
        cable(ROJO, placa["VIN"], (17, placa["VIN"][1]), (17, 152), (rojo[0], 152), rojo),
        cable(AMARILLO, placa["D5"], (108, placa["D5"][1]), (108, 158), (amarillo[0], 158), amarillo),
    )


def suelo():
    placa = en(NODEMCU, 22, 18)
    sensor = en(SUELO, 134, 86)
    # Los cables tapan los nombres impresos en el sensor: se repiten al lado.
    nombres = [etiqueta(pin, 124.5, sensor[pin][1] - 2.6) for pin in ("SIG", "GND", "VCC")]
    guardar(
        "suelo",
        316,
        166,
        pieza("nodemcu", 22, 18),
        pieza("sensor_suelo", 134, 86, giro=-90),
        cable(AMARILLO, placa["A0"], (10, placa["A0"][1]), (10, 8), (108, 8), (108, sensor["SIG"][1]), sensor["SIG"]),
        cable(NEGRO, placa["GND_DER"], (114, placa["GND_DER"][1]), (114, sensor["GND"][1]), sensor["GND"]),
        cable(ROJO, placa["3V3_DER"], (120, placa["3V3_DER"][1]), (120, sensor["VCC"][1]), sensor["VCC"]),
        *nombres,
    )


if __name__ == "__main__":
    ambiente()
    flujo()
    suelo()
