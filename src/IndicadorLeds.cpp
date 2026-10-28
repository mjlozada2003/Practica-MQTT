#include "IndicadorLeds.h"

IndicadorLeds::IndicadorLeds(uint8_t pinRojo, uint8_t pinAmarillo,
                             uint8_t pinVerde)
    : pinRojo_(pinRojo), pinAmarillo_(pinAmarillo), pinVerde_(pinVerde) {}

void IndicadorLeds::iniciar() {
    pinMode(pinRojo_, OUTPUT);
    pinMode(pinAmarillo_, OUTPUT);
    pinMode(pinVerde_, OUTPUT);
    apagar();
}

void IndicadorLeds::aplicar(bool cambiarRojo, bool rojo,
                            bool cambiarAmarillo, bool amarillo,
                            bool cambiarVerde, bool verde) {
    estado_.aplicar(cambiarRojo, rojo, cambiarAmarillo, amarillo,
                    cambiarVerde, verde);
    escribirSalidas();
}

void IndicadorLeds::apagar() {
    estado_ = EstadoLeds{};
    escribirSalidas();
}

const EstadoLeds& IndicadorLeds::estado() const { return estado_; }

void IndicadorLeds::escribirSalidas() const {
    digitalWrite(pinRojo_, estado_.rojo ? HIGH : LOW);
    digitalWrite(pinAmarillo_, estado_.amarillo ? HIGH : LOW);
    digitalWrite(pinVerde_, estado_.verde ? HIGH : LOW);
}
