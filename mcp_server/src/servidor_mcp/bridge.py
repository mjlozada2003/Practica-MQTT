"""Cliente MQTT concurrente y almacén del estado confirmado del ESP32."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
import threading
import time
import uuid
from typing import Any

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ConfiguracionMqtt:
    broker: str = "broker.hivemq.com"
    puerto: int = 1883
    keepalive: int = 30
    topic_base: str = "sis234/2026-2/grupo6"
    timeout_ack: float = 0.9
    antiguedad_maxima_distancia: float = 3.5

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionMqtt":
        return cls(
            broker=os.getenv("MQTT_BROKER", cls.broker),
            puerto=int(os.getenv("MQTT_PORT", str(cls.puerto))),
            keepalive=int(os.getenv("MQTT_KEEPALIVE", str(cls.keepalive))),
            topic_base=os.getenv("MQTT_TOPIC_BASE", cls.topic_base).rstrip("/"),
            timeout_ack=float(
                os.getenv("MQTT_ACK_TIMEOUT_SECONDS", str(cls.timeout_ack))
            ),
            antiguedad_maxima_distancia=float(
                os.getenv(
                    "MQTT_MAX_DISTANCE_AGE_SECONDS",
                    str(cls.antiguedad_maxima_distancia),
                )
            ),
        )

    @property
    def topic_distancia(self) -> str:
        return f"{self.topic_base}/sensor/distancia"

    @property
    def topic_comando(self) -> str:
        return f"{self.topic_base}/actuadores/leds/cmd"

    @property
    def topic_estado_leds(self) -> str:
        return f"{self.topic_base}/actuadores/leds/estado"

    @property
    def topic_dispositivo(self) -> str:
        return f"{self.topic_base}/dispositivo/estado"


class ErrorObjetoInteligente(RuntimeError):
    """Error operativo que Claude debe comunicar claramente al usuario."""


class PuenteMqtt:
    def __init__(
        self,
        configuracion: ConfiguracionMqtt,
        cliente: mqtt.Client | None = None,
    ) -> None:
        self.configuracion = configuracion
        client_id = f"sis234-g6-mcp-{uuid.uuid4().hex[:12]}"
        self.cliente = cliente or mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=mqtt.MQTTv311,
        )
        self.cliente.on_connect = self._al_conectar
        self.cliente.on_disconnect = self._al_desconectar
        self.cliente.on_message = self._al_recibir
        self.cliente.reconnect_delay_set(min_delay=2, max_delay=30)

        self._condicion = threading.Condition()
        self._broker_conectado = False
        self._dispositivo_en_linea = False
        self._distancia: float | None = None
        self._instante_distancia: float | None = None
        self._estado_leds: dict[str, bool] | None = None
        self._confirmaciones: dict[str, dict[str, bool]] = {}
        self._iniciado = False

    def iniciar(self) -> None:
        if self._iniciado:
            return
        logger.info(
            "Conectando al broker MQTT %s:%d",
            self.configuracion.broker,
            self.configuracion.puerto,
        )
        self.cliente.connect_async(
            self.configuracion.broker,
            self.configuracion.puerto,
            self.configuracion.keepalive,
        )
        self.cliente.loop_start()
        self._iniciado = True

    def detener(self) -> None:
        if not self._iniciado:
            return
        self.cliente.disconnect()
        self.cliente.loop_stop()
        self._iniciado = False

    def obtener_distancia(self) -> dict[str, Any]:
        with self._condicion:
            if not self._dispositivo_en_linea:
                raise ErrorObjetoInteligente("El ESP32 esta desconectado.")
            if (
                self._distancia is None
                or self._instante_distancia is None
            ):
                raise ErrorObjetoInteligente("No existe una medicion valida disponible.")
            edad = time.monotonic() - self._instante_distancia
            if edad > self.configuracion.antiguedad_maxima_distancia:
                raise ErrorObjetoInteligente(
                    f"La ultima medicion esta desactualizada ({edad:.2f} s)."
                )
            return {
                "cm": round(self._distancia, 2),
                "valida": True,
                "en_linea": True,
                "antiguedad_ms": round(edad * 1000),
            }

    def obtener_estado_leds(self) -> dict[str, Any]:
        with self._condicion:
            if not self._dispositivo_en_linea:
                raise ErrorObjetoInteligente("El ESP32 esta desconectado.")
            if self._estado_leds is None:
                raise ErrorObjetoInteligente("Aun no se recibio el estado de los LEDs.")
            return {**self._estado_leds, "en_linea": True}

    def controlar_leds(self, cambios: dict[str, bool]) -> dict[str, Any]:
        if not cambios:
            raise ValueError("Se debe indicar al menos un LED.")
        if set(cambios) - {"rojo", "amarillo", "verde"}:
            raise ValueError("El comando contiene un LED desconocido.")
        if any(type(valor) is not bool for valor in cambios.values()):
            raise ValueError("Los estados de los LEDs deben ser booleanos.")

        with self._condicion:
            if not self._broker_conectado:
                raise ErrorObjetoInteligente("El servidor MCP no esta conectado al broker.")
            if not self._dispositivo_en_linea:
                raise ErrorObjetoInteligente("El ESP32 esta desconectado.")

        identificador = str(uuid.uuid4())
        mensaje: dict[str, Any] = {"id": identificador, **cambios}
        inicio = time.monotonic()
        resultado = self.cliente.publish(
            self.configuracion.topic_comando,
            json.dumps(mensaje, separators=(",", ":")),
            qos=1,
            retain=False,
        )
        if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
            raise ErrorObjetoInteligente(
                f"No se pudo publicar el comando: {mqtt.error_string(resultado.rc)}"
            )

        limite = inicio + self.configuracion.timeout_ack
        with self._condicion:
            while identificador not in self._confirmaciones:
                restante = limite - time.monotonic()
                if restante <= 0:
                    raise ErrorObjetoInteligente(
                        "El ESP32 no confirmo el comando dentro de "
                        f"{round(self.configuracion.timeout_ack * 1000)} ms."
                    )
                self._condicion.wait(restante)
            estado = self._confirmaciones.pop(identificador)

        if any(estado[nombre] != valor for nombre, valor in cambios.items()):
            raise ErrorObjetoInteligente("La confirmacion no coincide con el comando.")
        return {
            **estado,
            "confirmado": True,
            "latencia_ms": round((time.monotonic() - inicio) * 1000),
            "ack_id": identificador,
        }

    def _al_conectar(self, client: mqtt.Client, userdata: Any, flags: Any,
                     reason_code: Any, properties: Any) -> None:
        del userdata, flags, properties
        if getattr(reason_code, "is_failure", False):
            logger.error("Conexion MQTT rechazada: %s", reason_code)
            return
        with self._condicion:
            self._broker_conectado = True
            self._condicion.notify_all()
        client.subscribe(
            [
                (self.configuracion.topic_distancia, 0),
                (self.configuracion.topic_estado_leds, 0),
                (self.configuracion.topic_dispositivo, 0),
            ]
        )
        logger.info("Conectado y suscrito a los topicos del grupo 6")

    def _al_desconectar(self, client: mqtt.Client, userdata: Any,
                        disconnect_flags: Any, reason_code: Any,
                        properties: Any) -> None:
        del client, userdata, disconnect_flags, properties
        with self._condicion:
            self._broker_conectado = False
            self._condicion.notify_all()
        logger.warning("Desconexion MQTT: %s; se reintentara automaticamente", reason_code)

    def _al_recibir(self, client: mqtt.Client, userdata: Any, mensaje: Any) -> None:
        del client, userdata
        try:
            datos = json.loads(mensaje.payload.decode("utf-8"))
            if not isinstance(datos, dict):
                raise ValueError("el payload no es un objeto JSON")
            if mensaje.topic == self.configuracion.topic_distancia:
                self._actualizar_distancia(datos)
            elif mensaje.topic == self.configuracion.topic_estado_leds:
                self._actualizar_leds(datos)
            elif mensaje.topic == self.configuracion.topic_dispositivo:
                self._actualizar_dispositivo(datos)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as error:
            logger.warning("Payload MQTT invalido en %s: %s", mensaje.topic, error)

    def _actualizar_distancia(self, datos: dict[str, Any]) -> None:
        valida = datos.get("valida")
        cm = datos.get("cm")
        if type(valida) is not bool:
            raise ValueError("valida debe ser booleano")
        if valida and (isinstance(cm, bool) or not isinstance(cm, (int, float))):
            raise ValueError("cm debe ser numerico cuando la medicion es valida")
        if not valida and cm is not None:
            raise ValueError("cm debe ser null cuando la medicion no es valida")
        with self._condicion:
            self._distancia = float(cm) if valida else None
            self._instante_distancia = time.monotonic()
            self._condicion.notify_all()

    def _actualizar_leds(self, datos: dict[str, Any]) -> None:
        estado: dict[str, bool] = {}
        for nombre in ("rojo", "amarillo", "verde"):
            valor = datos.get(nombre)
            if type(valor) is not bool:
                raise ValueError(f"{nombre} debe ser booleano")
            estado[nombre] = valor
        ack_id = datos.get("ack_id")
        if ack_id is not None and not isinstance(ack_id, str):
            raise ValueError("ack_id debe ser texto")
        with self._condicion:
            self._estado_leds = estado
            if ack_id:
                self._confirmaciones[ack_id] = estado.copy()
                if len(self._confirmaciones) > 32:
                    self._confirmaciones.pop(next(iter(self._confirmaciones)))
            self._condicion.notify_all()

    def _actualizar_dispositivo(self, datos: dict[str, Any]) -> None:
        en_linea = datos.get("en_linea")
        if type(en_linea) is not bool:
            raise ValueError("en_linea debe ser booleano")
        with self._condicion:
            self._dispositivo_en_linea = en_linea
            self._condicion.notify_all()
