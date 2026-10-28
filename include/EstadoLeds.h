#pragma once

struct EstadoLeds {
    bool rojo = false;
    bool amarillo = false;
    bool verde = false;

    void aplicar(bool cambiarRojo, bool nuevoRojo,
                 bool cambiarAmarillo, bool nuevoAmarillo,
                 bool cambiarVerde, bool nuevoVerde) {
        if (cambiarRojo) rojo = nuevoRojo;
        if (cambiarAmarillo) amarillo = nuevoAmarillo;
        if (cambiarVerde) verde = nuevoVerde;
    }
};
