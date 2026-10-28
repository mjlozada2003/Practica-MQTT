#pragma once

#include <Arduino.h>

// Copiar como include/Configuracion.h y completar solo los datos locales.
// Configuracion.h esta excluido de Git.
static constexpr char WIFI_SSID[] = "TU_RED_WIFI";
static constexpr char WIFI_PASSWORD[] = "TU_CLAVE_WIFI";

static constexpr char MQTT_BROKER[] = "broker.hivemq.com";
static constexpr uint16_t MQTT_PORT = 1883;
static constexpr uint16_t MQTT_KEEPALIVE_SECONDS = 30;
static constexpr char MQTT_CLIENT_PREFIX[] = "sis234-g6-esp32-";

static constexpr char TOPIC_DISTANCE[] =
    "sis234/2026-2/grupo6/sensor/distancia";
static constexpr char TOPIC_LED_COMMAND[] =
    "sis234/2026-2/grupo6/actuadores/leds/cmd";
static constexpr char TOPIC_LED_STATE[] =
    "sis234/2026-2/grupo6/actuadores/leds/estado";
static constexpr char TOPIC_DEVICE_STATE[] =
    "sis234/2026-2/grupo6/dispositivo/estado";

static constexpr uint32_t SENSOR_PUBLISH_INTERVAL_MS = 1000;
static constexpr uint32_t RECONNECT_BASE_MS = 2000;
static constexpr uint32_t RECONNECT_MAX_MS = 30000;

static constexpr uint8_t PIN_TRIGGER = 14;
static constexpr uint8_t PIN_ECHO = 27;
static constexpr uint8_t PIN_LED_RED = 33;
static constexpr uint8_t PIN_LED_YELLOW = 25;
static constexpr uint8_t PIN_LED_GREEN = 26;

static constexpr float MIN_DISTANCE_CM = 2.0F;
static constexpr float MAX_DISTANCE_CM = 30.0F;
