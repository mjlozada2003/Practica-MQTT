#include "SensorUltrasonico.h"

#include "CalculoDistancia.h"

SensorUltrasonico::SensorUltrasonico(uint8_t pinDisparo, uint8_t pinEco,
                                     float distanciaMinimaCm,
                                     float distanciaMaximaCm)
    : pinDisparo_(pinDisparo), pinEco_(pinEco),
      distanciaMinimaCm_(distanciaMinimaCm),
      distanciaMaximaCm_(distanciaMaximaCm) {}

void SensorUltrasonico::iniciar() {
    pinMode(pinDisparo_, OUTPUT);
    pinMode(pinEco_, INPUT);
    digitalWrite(pinDisparo_, LOW);
}

bool SensorUltrasonico::medir(float& distanciaCm) const {
    digitalWrite(pinDisparo_, LOW);
    delayMicroseconds(2);
    digitalWrite(pinDisparo_, HIGH);
    delayMicroseconds(10);
    digitalWrite(pinDisparo_, LOW);

    const unsigned long duracion = pulseIn(pinEco_, HIGH, TIMEOUT_ECHO_US);
    if (duracion == 0) return false;
    distanciaCm = CalculoDistancia::desdeDuracionMicrosegundos(duracion);
    return CalculoDistancia::dentroDelRango(
        distanciaCm, distanciaMinimaCm_, distanciaMaximaCm_);
}
