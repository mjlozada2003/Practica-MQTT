"""Casos de uso independientes del protocolo MCP."""

from __future__ import annotations

from typing import Any

from .bridge import PuenteMqtt


class ServicioObjetoInteligente:
    def __init__(self, puente: PuenteMqtt) -> None:
        self.puente = puente

    def obtener_distancia(self) -> dict[str, Any]:
        return self.puente.obtener_distancia()

    def obtener_estado_leds(self) -> dict[str, Any]:
        return self.puente.obtener_estado_leds()

    def controlar_leds(
        self,
        rojo: bool | None = None,
        amarillo: bool | None = None,
        verde: bool | None = None,
    ) -> dict[str, Any]:
        valores = {"rojo": rojo, "amarillo": amarillo, "verde": verde}
        cambios = {nombre: valor for nombre, valor in valores.items() if valor is not None}
        return self.puente.controlar_leds(cambios)
