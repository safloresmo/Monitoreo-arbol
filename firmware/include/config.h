#pragma once

#include <Arduino.h>

#if defined(NODO_AMBIENTE) + defined(NODO_FLUJO) + defined(NODO_SUELO) != 1
#error "Elige un solo tipo de nodo: NODO_AMBIENTE, NODO_FLUJO o NODO_SUELO"
#endif

// Cada cuánto se leen y se publican los sensores.
const unsigned long PERIODO_MS = 30000;
const unsigned long REINTENTO_MQTT_MS = 5000;

#if defined(NODO_AMBIENTE)
#define NOMBRE_NODO "ambiente"
const uint8_t PIN_DHT = D4;
#endif

#if defined(NODO_FLUJO)
#define NOMBRE_NODO "flujo"
const uint8_t PIN_FLUJO = D5;
// Depende del sensor; 450 es lo habitual en los de media pulgada.
const float PULSOS_POR_LITRO = 450.0;
#endif

#if defined(NODO_SUELO)
#define NOMBRE_NODO "suelo"
#ifndef TEMA_SUELO
#error "Falta TEMA_SUELO: el tema en el que publica este nodo"
#endif
const uint8_t PIN_SUELO = A0;
// Lectura del sensor en seco y dentro del agua. Con estos valores sale la
// escala sin calibrar; conviene medir los de cada sensor y ponerlos aquí.
const int SUELO_SECO = 1023;
const int SUELO_MOJADO = 0;
#endif
