#pragma once

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include "EstadoLeds.h"

class ClienteMqtt {
public:
    using ManejadorComando = void (*)(const byte*, unsigned int);
    using ManejadorConexion = void (*)();

    ClienteMqtt(const char* broker, uint16_t puerto, uint16_t keepalive,
                const char* prefijoCliente, const char* topicDistancia,
                const char* topicComando, const char* topicEstado,
                const char* topicDisponibilidad, uint32_t esperaBaseMs,
                uint32_t esperaMaximaMs);
    void iniciar(ManejadorComando alRecibirComando,
                 ManejadorConexion alConectar);
    void actualizar(bool wifiConectada);
    bool conectada();
    bool publicarDistancia(float distanciaCm, bool valida);
    bool publicarEstadoLeds(const EstadoLeds& estado,
                            const char* ackId = nullptr);

private:
    WiFiClient wifiClient_;
    PubSubClient cliente_;
    const char* broker_;
    uint16_t puerto_;
    uint16_t keepalive_;
    const char* prefijoCliente_;
    const char* topicDistancia_;
    const char* topicComando_;
    const char* topicEstado_;
    const char* topicDisponibilidad_;
    uint32_t esperaBaseMs_;
    uint32_t esperaMaximaMs_;
    uint32_t esperaActualMs_;
    unsigned long ultimoIntentoMs_ = 0;
    bool primerIntento_ = true;
    String clientId_;
    ManejadorComando alRecibirComando_ = nullptr;
    ManejadorConexion alConectar_ = nullptr;

    static ClienteMqtt* instancia_;
    static void recibirMensaje(char* topic, byte* payload, unsigned int length);
    void conectar();
};
