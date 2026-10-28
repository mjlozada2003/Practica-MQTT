#pragma once

class CalculoDistancia {
public:
    static constexpr float CENTIMETROS_POR_MICROSEGUNDO = 0.01715F;

    static float desdeDuracionMicrosegundos(unsigned long duracion) {
        return static_cast<float>(duracion) * CENTIMETROS_POR_MICROSEGUNDO;
    }

    static bool dentroDelRango(float cm, float minimo, float maximo) {
        return cm >= minimo && cm <= maximo;
    }
};
