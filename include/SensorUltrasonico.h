#pragma once

#include <Arduino.h>

class SensorUltrasonico {
public:
    SensorUltrasonico(uint8_t pinDisparo, uint8_t pinEco,
                      float distanciaMinimaCm, float distanciaMaximaCm);
    void iniciar();
    bool medir(float& distanciaCm) const;

private:
    uint8_t pinDisparo_;
    uint8_t pinEco_;
    float distanciaMinimaCm_;
    float distanciaMaximaCm_;
    static constexpr unsigned long TIMEOUT_ECHO_US = 30000UL;
};
