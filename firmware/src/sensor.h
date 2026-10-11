// Lo que cada tipo de nodo tiene que saber hacer.
#pragma once

#include <PubSubClient.h>

void iniciarSensor();
void publicarLecturas(PubSubClient &mqtt);
