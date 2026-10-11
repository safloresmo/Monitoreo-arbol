import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lecturas import TEMAS, Lecturas


def test_flujo_y_suelo_se_guardan_al_llegar():
    lecturas = Lecturas()
    assert lecturas.procesar("limon/volumen", "1.25", 0.0) == ("Flujo", (1.25,))
    assert lecturas.procesar("limon/suelo", "40", 0.0) == ("Suelo", (40.0,))
    assert lecturas.procesar("limon/suelo2", "41", 0.0) == ("Suelo2", (41.0,))
    assert lecturas.procesar("limon/suelo3", "42", 0.0) == ("Suelo3", (42.0,))


def test_el_aire_se_guarda_en_una_sola_fila():
    lecturas = Lecturas()
    assert lecturas.procesar("limon/temperatura", "24.50", 0.0) is None
    assert lecturas.procesar("limon/humedad", "61.00", 0.1) == ("Temperatura", (61.0, 24.5))
    # La pareja ya se usó: la siguiente lectura vuelve a esperar.
    assert lecturas.procesar("limon/humedad", "62.00", 30.0) is None
    assert lecturas.procesar("limon/temperatura", "25.00", 30.1) == ("Temperatura", (62.0, 25.0))


def test_una_lectura_del_aire_sin_pareja_se_descarta():
    lecturas = Lecturas()
    assert lecturas.procesar("limon/temperatura", "24.00", 0.0) is None
    # La humedad de ese ciclo se perdió; llega el ciclo siguiente.
    assert lecturas.procesar("limon/temperatura", "25.00", 30.0) is None
    assert lecturas.procesar("limon/humedad", "60.00", 30.1) == ("Temperatura", (60.0, 25.0))

    assert lecturas.procesar("limon/humedad", "70.00", 60.0) is None
    assert lecturas.procesar("limon/temperatura", "26.00", 90.0) is None
    assert lecturas.procesar("limon/humedad", "71.00", 90.1) == ("Temperatura", (71.0, 26.0))


@pytest.mark.parametrize("texto", ["", "nan", "inf", "abc", "12,5"])
def test_un_mensaje_que_no_es_un_numero_se_rechaza(texto):
    with pytest.raises(ValueError):
        Lecturas().procesar("limon/suelo", texto, 0.0)


def test_un_tema_desconocido_se_rechaza():
    with pytest.raises(ValueError):
        Lecturas().procesar("limon/otro", "1", 0.0)


def test_todos_los_temas_se_procesan():
    lecturas = Lecturas()
    for tema in TEMAS:
        lecturas.procesar(tema, "1", 0.0)
