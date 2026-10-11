"""Convierte los mensajes de los nodos en filas para la base de datos."""

import math

TEMA_TEMPERATURA = "limon/temperatura"
TEMA_HUMEDAD = "limon/humedad"
TEMA_VOLUMEN = "limon/volumen"
TEMAS_SUELO = {
    "limon/suelo": "Suelo",
    "limon/suelo2": "Suelo2",
    "limon/suelo3": "Suelo3",
}
TEMAS = [TEMA_TEMPERATURA, TEMA_HUMEDAD, TEMA_VOLUMEN, *TEMAS_SUELO]

# La temperatura y la humedad del aire salen del mismo nodo una tras otra. Si
# pasa más tiempo que este entre las dos, es que una se perdió.
SEPARACION_MAXIMA = 10.0


class Lecturas:
    """Recibe los mensajes y dice qué fila hay que guardar con cada uno."""

    def __init__(self):
        # Lecturas del aire a la espera de su pareja: tema -> (valor, instante).
        self._aire = {}

    def procesar(self, tema, texto, instante):
        """Devuelve `(tabla, valores)` o `None` si todavía no hay nada que guardar.

        `instante` es el momento de llegada, en segundos. Lanza `ValueError`
        si el mensaje no trae un número.
        """
        valor = float(texto)
        if not math.isfinite(valor):
            raise ValueError(f"valor no válido: {texto!r}")

        if tema == TEMA_VOLUMEN:
            return "Flujo", (valor,)
        if tema in TEMAS_SUELO:
            return TEMAS_SUELO[tema], (valor,)
        if tema in (TEMA_TEMPERATURA, TEMA_HUMEDAD):
            return self._emparejar(tema, valor, instante)
        raise ValueError(f"tema desconocido: {tema}")

    # La temperatura y la humedad se guardan juntas en una sola fila.
    def _emparejar(self, tema, valor, instante):
        self._aire[tema] = (valor, instante)
        if len(self._aire) < 2:
            return None

        temperatura, cuando_temperatura = self._aire[TEMA_TEMPERATURA]
        humedad, cuando_humedad = self._aire[TEMA_HUMEDAD]
        if abs(cuando_temperatura - cuando_humedad) > SEPARACION_MAXIMA:
            # La más vieja se quedó sin pareja: se descarta.
            self._aire = {tema: (valor, instante)}
            return None

        self._aire = {}
        return "Temperatura", (humedad, temperatura)
