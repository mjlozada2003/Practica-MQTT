#pragma once

#include <ArduinoJson.h>
#include <cstddef>
#include <cstdint>
#include <cstring>

struct ComandoLeds {
    bool cambiarRojo = false;
    bool cambiarAmarillo = false;
    bool cambiarVerde = false;
    bool rojo = false;
    bool amarillo = false;
    bool verde = false;
    bool tieneId = false;
    char id[65] = {};
};

class ParserComandoLeds {
public:
    static bool interpretar(const uint8_t* payload, std::size_t length,
                            ComandoLeds& salida) {
        JsonDocument documento;
        const DeserializationError error = deserializeJson(documento, payload, length);
        if (error || !documento.is<JsonObject>()) return false;

        ComandoLeds temporal;
        for (JsonPair par : documento.as<JsonObject>()) {
            const char* clave = par.key().c_str();
            JsonVariant valor = par.value();
            if (std::strcmp(clave, "id") == 0) {
                if (!valor.is<const char*>()) return false;
                const char* id = valor.as<const char*>();
                const std::size_t longitud = std::strlen(id);
                if (longitud == 0 || longitud >= sizeof(temporal.id)) return false;
                std::memcpy(temporal.id, id, longitud + 1);
                temporal.tieneId = true;
            } else if (std::strcmp(clave, "rojo") == 0) {
                if (!valor.is<bool>()) return false;
                temporal.cambiarRojo = true;
                temporal.rojo = valor.as<bool>();
            } else if (std::strcmp(clave, "amarillo") == 0) {
                if (!valor.is<bool>()) return false;
                temporal.cambiarAmarillo = true;
                temporal.amarillo = valor.as<bool>();
            } else if (std::strcmp(clave, "verde") == 0) {
                if (!valor.is<bool>()) return false;
                temporal.cambiarVerde = true;
                temporal.verde = valor.as<bool>();
            } else {
                return false;
            }
        }

        if (!temporal.cambiarRojo && !temporal.cambiarAmarillo &&
            !temporal.cambiarVerde) return false;
        salida = temporal;
        return true;
    }
};
