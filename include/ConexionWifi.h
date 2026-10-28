#pragma once

#include <Arduino.h>
#include <WiFi.h>

class ConexionWifi {
public:
    ConexionWifi(const char* ssid, const char* clave,
                 uint32_t esperaBaseMs, uint32_t esperaMaximaMs);
    void iniciar();
    void actualizar();
    bool conectada() const;

private:
    const char* ssid_;
    const char* clave_;
    uint32_t esperaBaseMs_;
    uint32_t esperaMaximaMs_;
    uint32_t esperaActualMs_;
    unsigned long ultimoIntentoMs_ = 0;
    bool primerIntento_ = true;
    bool estabaConectada_ = false;
};
