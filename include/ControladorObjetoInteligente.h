#pragma once

#include <Arduino.h>
#include "ClienteMqtt.h"
#include "ConexionWifi.h"
#include "IndicadorLeds.h"
#include "SensorUltrasonico.h"

class ControladorObjetoInteligente {
public:
    ControladorObjetoInteligente(SensorUltrasonico& sensor,
                                 IndicadorLeds& leds,
                                 ConexionWifi& wifi,
                                 ClienteMqtt& mqtt,
                                 uint32_t intervaloPublicacionMs);
    void iniciar();
    void actualizar();

private:
    SensorUltrasonico& sensor_;
    IndicadorLeds& leds_;
    ConexionWifi& wifi_;
    ClienteMqtt& mqtt_;
    uint32_t intervaloPublicacionMs_;
    unsigned long ultimaPublicacionMs_ = 0;
    bool primeraPublicacion_ = true;

    static ControladorObjetoInteligente* instancia_;
    static void recibirComando(const byte* payload, unsigned int length);
    static void alConectarMqtt();
    void procesarComando(const byte* payload, unsigned int length);
};
