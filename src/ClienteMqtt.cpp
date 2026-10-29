#include "ClienteMqtt.h"

#include <ArduinoJson.h>

ClienteMqtt* ClienteMqtt::instancia_ = nullptr;

ClienteMqtt::ClienteMqtt(const char* broker, uint16_t puerto,
                         uint16_t keepalive, const char* prefijoCliente,
                         const char* topicDistancia, const char* topicComando,
                         const char* topicEstado,
                         const char* topicDisponibilidad,
                         uint32_t esperaBaseMs, uint32_t esperaMaximaMs)
    : cliente_(wifiClient_), broker_(broker), puerto_(puerto),
      keepalive_(keepalive), prefijoCliente_(prefijoCliente),
      topicDistancia_(topicDistancia), topicComando_(topicComando),
      topicEstado_(topicEstado), topicDisponibilidad_(topicDisponibilidad),
      esperaBaseMs_(esperaBaseMs), esperaMaximaMs_(esperaMaximaMs),
      esperaActualMs_(esperaBaseMs) {}

void ClienteMqtt::iniciar(ManejadorComando alRecibirComando,
                          ManejadorConexion alConectar) {
    alRecibirComando_ = alRecibirComando;
    alConectar_ = alConectar;
    instancia_ = this;
    clientId_ = String(prefijoCliente_) + WiFi.macAddress();
    clientId_.replace(":", "");
    cliente_.setServer(broker_, puerto_);
    cliente_.setCallback(ClienteMqtt::recibirMensaje);
    cliente_.setKeepAlive(keepalive_);
    cliente_.setBufferSize(512);
    cliente_.setSocketTimeout(1);
}

void ClienteMqtt::actualizar(bool wifiConectada) {
    if (!wifiConectada) {
        if (cliente_.connected()) cliente_.disconnect();
        primerIntento_ = true;
        return;
    }

    if (cliente_.connected()) {
        cliente_.loop();
        esperaActualMs_ = esperaBaseMs_;
        primerIntento_ = true;
        return;
    }

    const unsigned long ahora = millis();
    if (!primerIntento_ && ahora - ultimoIntentoMs_ < esperaActualMs_) return;
    const bool eraPrimerIntento = primerIntento_;
    primerIntento_ = false;
    ultimoIntentoMs_ = ahora;
    conectar();
    if (!cliente_.connected() && !eraPrimerIntento) {
        esperaActualMs_ = min(esperaActualMs_ * 2U, esperaMaximaMs_);
    }
}

bool ClienteMqtt::conectada() { return cliente_.connected(); }

bool ClienteMqtt::publicarDistancia(float distanciaCm, bool valida) {
    if (!cliente_.connected()) return false;
    JsonDocument documento;
    if (valida) documento["cm"] = roundf(distanciaCm * 100.0F) / 100.0F;
    else documento["cm"] = nullptr;
    documento["valida"] = valida;
    char payload[96];
    const size_t longitud = serializeJson(documento, payload, sizeof(payload));
    return longitud > 0 && cliente_.publish(topicDistancia_, payload, true);
}

bool ClienteMqtt::publicarEstadoLeds(const EstadoLeds& estado,
                                     const char* ackId) {
    if (!cliente_.connected()) return false;
    JsonDocument documento;
    documento["rojo"] = estado.rojo;
    documento["amarillo"] = estado.amarillo;
    documento["verde"] = estado.verde;
    if (ackId != nullptr && ackId[0] != '\0') documento["ack_id"] = ackId;
    char payload[192];
    const size_t longitud = serializeJson(documento, payload, sizeof(payload));
    return longitud > 0 && cliente_.publish(topicEstado_, payload, true);
}

void ClienteMqtt::recibirMensaje(char* topic, byte* payload,
                                  unsigned int length) {
    if (instancia_ == nullptr || instancia_->alRecibirComando_ == nullptr) return;
    if (strcmp(topic, instancia_->topicComando_) != 0) return;
    instancia_->alRecibirComando_(payload, length);
}

void ClienteMqtt::conectar() {
    Serial.printf("[MQTT] Conectando a %s:%u como %s\n", broker_, puerto_,
                  clientId_.c_str());
    const bool ok = cliente_.connect(clientId_.c_str(), topicDisponibilidad_, 0,
                                     true, "{\"en_linea\":false}");
    if (!ok) {
        Serial.printf("[MQTT] Fallo estado=%d\n", cliente_.state());
        return;
    }
    // PubSubClient devuelve true si pudo enviar SUBSCRIBE, no confirma SUBACK.
    if (!cliente_.subscribe(topicComando_, 1)) {
        Serial.printf("[MQTT] ERROR: no se pudo enviar SUBSCRIBE a %s "
                      "(estado=%d). Reintentando conexion.\n",
                      topicComando_, cliente_.state());
        cliente_.disconnect();
        return;
    }
    Serial.printf("[MQTT] Solicitud SUBSCRIBE enviada: %s (QoS 1)\n",
                  topicComando_);

    if (!cliente_.publish(topicDisponibilidad_, "{\"en_linea\":true}", true)) {
        Serial.printf("[MQTT] ERROR: no se pudo publicar disponibilidad "
                      "(estado=%d). Reintentando conexion.\n",
                      cliente_.state());
        cliente_.disconnect();
        return;
    }
    esperaActualMs_ = esperaBaseMs_;
    Serial.println("[MQTT] Conexion activa y disponibilidad publicada");
    if (alConectar_ != nullptr) alConectar_();
}
