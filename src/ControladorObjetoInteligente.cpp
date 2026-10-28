#include "ControladorObjetoInteligente.h"

#include "ComandoLeds.h"

ControladorObjetoInteligente* ControladorObjetoInteligente::instancia_ = nullptr;

ControladorObjetoInteligente::ControladorObjetoInteligente(
    SensorUltrasonico& sensor, IndicadorLeds& leds, ConexionWifi& wifi,
    ClienteMqtt& mqtt, uint32_t intervaloPublicacionMs)
    : sensor_(sensor), leds_(leds), wifi_(wifi), mqtt_(mqtt),
      intervaloPublicacionMs_(intervaloPublicacionMs) {}

void ControladorObjetoInteligente::iniciar() {
    instancia_ = this;
    sensor_.iniciar();
    leds_.iniciar();
    wifi_.iniciar();
    mqtt_.iniciar(ControladorObjetoInteligente::recibirComando,
                  ControladorObjetoInteligente::alConectarMqtt);
}

void ControladorObjetoInteligente::actualizar() {
    wifi_.actualizar();
    mqtt_.actualizar(wifi_.conectada());
    if (!mqtt_.conectada()) return;

    const unsigned long ahora = millis();
    if (!primeraPublicacion_ &&
        ahora - ultimaPublicacionMs_ < intervaloPublicacionMs_) return;

    primeraPublicacion_ = false;
    ultimaPublicacionMs_ = ahora;
    float distanciaCm = 0.0F;
    const bool valida = sensor_.medir(distanciaCm);
    mqtt_.publicarDistancia(distanciaCm, valida);
    if (valida) Serial.printf("[Sensor] distancia_cm=%.2f\n", distanciaCm);
    else Serial.println("[Sensor] lectura no valida");
}

void ControladorObjetoInteligente::recibirComando(const byte* payload,
                                                   unsigned int length) {
    if (instancia_ != nullptr) instancia_->procesarComando(payload, length);
}

void ControladorObjetoInteligente::alConectarMqtt() {
    if (instancia_ == nullptr) return;
    instancia_->mqtt_.publicarEstadoLeds(instancia_->leds_.estado());
    instancia_->primeraPublicacion_ = true;
}

void ControladorObjetoInteligente::procesarComando(const byte* payload,
                                                    unsigned int length) {
    ComandoLeds comando;
    if (!ParserComandoLeds::interpretar(payload, length, comando)) {
        Serial.println("[Comando] JSON o esquema invalido");
        return;
    }

    leds_.aplicar(comando.cambiarRojo, comando.rojo,
                  comando.cambiarAmarillo, comando.amarillo,
                  comando.cambiarVerde, comando.verde);
    mqtt_.publicarEstadoLeds(leds_.estado(),
                             comando.tieneId ? comando.id : nullptr);
    Serial.printf("[Comando] aplicado rojo=%d amarillo=%d verde=%d\n",
                  leds_.estado().rojo, leds_.estado().amarillo,
                  leds_.estado().verde);
}
