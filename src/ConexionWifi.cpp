#include "ConexionWifi.h"

ConexionWifi::ConexionWifi(const char* ssid, const char* clave,
                           uint32_t esperaBaseMs, uint32_t esperaMaximaMs)
    : ssid_(ssid), clave_(clave), esperaBaseMs_(esperaBaseMs),
      esperaMaximaMs_(esperaMaximaMs), esperaActualMs_(esperaBaseMs) {}

void ConexionWifi::iniciar() {
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);  // menor latencia MQTT; mayor consumo energetico
    WiFi.setAutoReconnect(true);
    primerIntento_ = true;
    actualizar();
}

void ConexionWifi::actualizar() {
    const bool ahoraConectada = WiFi.status() == WL_CONNECTED;
    if (ahoraConectada) {
        if (!estabaConectada_) {
            Serial.printf("[WiFi] Conectada. IP=%s\n",
                          WiFi.localIP().toString().c_str());
        }
        estabaConectada_ = true;
        esperaActualMs_ = esperaBaseMs_;
        primerIntento_ = true;
        return;
    }

    if (estabaConectada_) Serial.println("[WiFi] Conexion perdida");
    estabaConectada_ = false;
    const unsigned long ahora = millis();
    if (!primerIntento_ && ahora - ultimoIntentoMs_ < esperaActualMs_) return;

    const bool eraPrimerIntento = primerIntento_;
    primerIntento_ = false;
    ultimoIntentoMs_ = ahora;
    Serial.printf("[WiFi] Intentando conexion a %s\n", ssid_);
    WiFi.begin(ssid_, clave_);
    if (!eraPrimerIntento) {
        esperaActualMs_ = min(esperaActualMs_ * 2U, esperaMaximaMs_);
    }
}

bool ConexionWifi::conectada() const { return WiFi.status() == WL_CONNECTED; }
