#pragma once

#include <Arduino.h>
#include "EstadoLeds.h"

class IndicadorLeds {
public:
    IndicadorLeds(uint8_t pinRojo, uint8_t pinAmarillo, uint8_t pinVerde);
    void iniciar();
    void aplicar(bool cambiarRojo, bool rojo,
                 bool cambiarAmarillo, bool amarillo,
                 bool cambiarVerde, bool verde);
    void apagar();
    const EstadoLeds& estado() const;

private:
    uint8_t pinRojo_;
    uint8_t pinAmarillo_;
    uint8_t pinVerde_;
    EstadoLeds estado_;
    void escribirSalidas() const;
};
