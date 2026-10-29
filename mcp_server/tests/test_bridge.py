from __future__ import annotations

import json
import threading
import time
from types import SimpleNamespace

import pytest

from servidor_mcp.bridge import (
    ConfiguracionMqtt,
    ErrorObjetoInteligente,
    PuenteMqtt,
)
from servidor_mcp.service import ServicioObjetoInteligente


class ResultadoPublicacion:
    rc = 0


class ClienteFalso:
    def __init__(self) -> None:
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.publicaciones: list[tuple[str, str, int, bool]] = []

    def reconnect_delay_set(self, min_delay: int, max_delay: int) -> None:
        self.reintentos = (min_delay, max_delay)

    def publish(self, topic: str, payload: str, qos: int, retain: bool):
        self.publicaciones.append((topic, payload, qos, retain))
        return ResultadoPublicacion()


def mensaje(topic: str, datos: dict) -> SimpleNamespace:
    return SimpleNamespace(topic=topic, payload=json.dumps(datos).encode())


def puente_listo(timeout: float = 0.15) -> tuple[PuenteMqtt, ClienteFalso]:
    configuracion = ConfiguracionMqtt(timeout_ack=timeout)
    cliente = ClienteFalso()
    puente = PuenteMqtt(configuracion, cliente=cliente)  # type: ignore[arg-type]
    puente._broker_conectado = True
    puente._dispositivo_en_linea = True
    return puente, cliente


def test_distancia_valida_y_antiguedad() -> None:
    puente, _ = puente_listo()
    puente._al_recibir(
        None,
        None,
        mensaje(puente.configuracion.topic_distancia, {"cm": 12.34, "valida": True}),
    )
    resultado = puente.obtener_distancia()
    assert resultado["cm"] == 12.34
    assert resultado["valida"] is True
    assert resultado["antiguedad_ms"] >= 0


def test_no_inventa_distancia_con_dispositivo_desconectado() -> None:
    puente, _ = puente_listo()
    puente._dispositivo_en_linea = False
    with pytest.raises(ErrorObjetoInteligente, match="desconectado"):
        puente.obtener_distancia()


def test_servicio_exige_al_menos_un_led() -> None:
    puente, _ = puente_listo()
    servicio = ServicioObjetoInteligente(puente)
    with pytest.raises(ValueError, match="al menos"):
        servicio.controlar_leds()


def test_comando_espera_ack_correlacionado() -> None:
    puente, cliente = puente_listo(timeout=0.5)

    def confirmar() -> None:
        while not cliente.publicaciones:
            time.sleep(0.001)
        payload = json.loads(cliente.publicaciones[0][1])
        puente._al_recibir(
            None,
            None,
            mensaje(
                puente.configuracion.topic_estado_leds,
                {
                    "rojo": True,
                    "amarillo": False,
                    "verde": False,
                    "ack_id": payload["id"],
                },
            ),
        )

    hilo = threading.Thread(target=confirmar)
    hilo.start()
    resultado = puente.controlar_leds({"rojo": True})
    hilo.join()
    assert resultado["confirmado"] is True
    assert resultado["rojo"] is True
    assert cliente.publicaciones[0][2:] == (1, False)


def test_ack_incorrecto_termina_en_timeout() -> None:
    puente, cliente = puente_listo(timeout=0.03)

    def confirmar_otro() -> None:
        while not cliente.publicaciones:
            time.sleep(0.001)
        puente._al_recibir(
            None,
            None,
            mensaje(
                puente.configuracion.topic_estado_leds,
                {
                    "rojo": True,
                    "amarillo": False,
                    "verde": False,
                    "ack_id": "otro-id",
                },
            ),
        )

    hilo = threading.Thread(target=confirmar_otro)
    hilo.start()
    resultado = puente.controlar_leds({"rojo": True})
    hilo.join()
    assert resultado["enviado"] is True
    assert resultado["confirmado"] is False
    assert resultado["ack_id"] != "otro-id"
    assert "desconocido" in resultado["mensaje"]


def test_sin_ack_devuelve_estado_no_confirmado() -> None:
    puente, _ = puente_listo(timeout=0.01)
    resultado = puente.controlar_leds({"rojo": True})
    assert resultado["confirmado"] is False
    assert "rojo" not in resultado


def test_retenciones_al_arrancar_no_borran_estado_por_online() -> None:
    puente, _ = puente_listo()
    puente._dispositivo_en_linea = False
    puente._actualizar_distancia({"cm": 18.5, "valida": True})
    puente._actualizar_leds({"rojo": False, "amarillo": True, "verde": False})
    puente._actualizar_dispositivo({"en_linea": True})
    assert puente.obtener_distancia()["cm"] == 18.5
    assert puente.obtener_estado_leds()["amarillo"] is True


def test_retencion_offline_invalida_cache_incluso_al_arrancar() -> None:
    puente, _ = puente_listo()
    puente._dispositivo_en_linea = False
    puente._actualizar_leds({"rojo": True, "amarillo": False, "verde": False})
    puente._actualizar_dispositivo({"en_linea": False})
    puente._actualizar_dispositivo({"en_linea": True})
    with pytest.raises(ErrorObjetoInteligente, match="Aun no se recibio"):
        puente.obtener_estado_leds()


def test_payload_invalido_no_reemplaza_estado() -> None:
    puente, _ = puente_listo()
    puente._al_recibir(
        None,
        None,
        mensaje(
            puente.configuracion.topic_estado_leds,
            {"rojo": True, "amarillo": False, "verde": True},
        ),
    )
    puente._al_recibir(
        None,
        None,
        mensaje(
            puente.configuracion.topic_estado_leds,
            {"rojo": "si", "amarillo": False, "verde": False},
        ),
    )
    assert puente.obtener_estado_leds()["verde"] is True
