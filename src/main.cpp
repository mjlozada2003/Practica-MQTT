#include <Arduino.h>

#if __has_include("Configuracion.h")
#include "Configuracion.h"
#else
#include "ConfiguracionEjemplo.h"
#endif

#include "ClienteMqtt.h"
#include "ConexionWifi.h"
#include "ControladorObjetoInteligente.h"
#include "IndicadorLeds.h"
#include "SensorUltrasonico.h"

SensorUltrasonico sensor(PIN_TRIGGER, PIN_ECHO, MIN_DISTANCE_CM,
                         MAX_DISTANCE_CM);
IndicadorLeds leds(PIN_LED_RED, PIN_LED_YELLOW, PIN_LED_GREEN);
ConexionWifi wifi(WIFI_SSID, WIFI_PASSWORD, RECONNECT_BASE_MS,
                  RECONNECT_MAX_MS);
ClienteMqtt mqtt(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_SECONDS,
                 MQTT_CLIENT_PREFIX, TOPIC_DISTANCE, TOPIC_LED_COMMAND,
                 TOPIC_LED_STATE, TOPIC_DEVICE_STATE, RECONNECT_BASE_MS,
                 RECONNECT_MAX_MS);
ControladorObjetoInteligente objeto(sensor, leds, wifi, mqtt,
                                    SENSOR_PUBLISH_INTERVAL_MS);

void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println("[Sistema] Iniciando objeto inteligente MQTT");
    objeto.iniciar();
}

void loop() { objeto.actualizar(); }
