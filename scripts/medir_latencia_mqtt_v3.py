"""Mediciones MQTT de Grupo 6.

Dependencia: python -m pip install 'paho-mqtt>=2.1,<3'

Modos:
  automatico: publica comandos con UUID y mide publish local -> ACK correlacionado.
  observar: detecta comandos del movil/Claude y la publicacion de estado posterior.

Advertencia: no mide directamente pulsacion en pantalla -> LED fisico;
el ACK es estado informado por el firmware del ESP32.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import statistics
import threading
import time
import uuid

import paho.mqtt.client as mqtt

BASE = "sis234/2026-2/grupo6"
COLORES = ("rojo", "amarillo", "verde")


def marca() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


class Medidor:
    def __init__(self, cliente: mqtt.Client, base: str, modo: str) -> None:
        self.cliente = cliente
        self.base = base
        self.modo = modo
        self.conectado = threading.Event()
        self.suscrito = threading.Event()
        self.condicion = threading.Condition()
        self.pendientes: dict[str, dict] = {}
        self.orden_pendientes: list[str] = []
        self.resultados: list[dict] = []
        self.estado_inicial: dict | None = None
        self.cliente.on_connect = self.on_connect
        self.cliente.on_subscribe = self.on_subscribe
        self.cliente.on_message = self.on_message
        self.cliente.on_connect_fail = self.on_connect_fail
        self.cliente.on_disconnect = self.on_disconnect

    def on_connect(self, cliente, userdata, flags, reason_code, properties) -> None:
        del userdata, flags, properties
        if getattr(reason_code, "is_failure", False):
            print(f"[MQTT] CONNACK rechazado: {reason_code}", flush=True)
            return
        self.conectado.set()
        print("[MQTT] Conectado al broker (CONNACK recibido)", flush=True)
        rc, mid = cliente.subscribe([(self.base + "/actuadores/leds/cmd", 0),
                                     (self.base + "/actuadores/leds/estado", 0)])
        if rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"[MQTT] Fallo al solicitar SUBSCRIBE: codigo {rc}", flush=True)

    def on_connect_fail(self, cliente, userdata) -> None:
        del cliente, userdata
        print("[MQTT] No se pudo abrir la conexion TCP; reintentando...", flush=True)

    def on_disconnect(self, cliente, userdata, disconnect_flags, reason_code, properties) -> None:
        del cliente, userdata, disconnect_flags, properties
        if str(reason_code) != "Normal disconnection":
            print(f"[MQTT] Conexion perdida: {reason_code}", flush=True)

    def on_subscribe(self, cliente, userdata, mid, reason_codes, properties) -> None:
        del cliente, userdata, mid, properties
        if not reason_codes or any(getattr(c, "is_failure", False) for c in reason_codes):
            print(f"[MQTT] SUBACK no aceptado: {reason_codes}", flush=True)
            return
        print("[MQTT] Suscripcion confirmada (SUBACK recibido)", flush=True)
        self.suscrito.set()

    def on_message(self, cliente, userdata, msg) -> None:
        del cliente, userdata
        try:
            dato = json.loads(msg.payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return
        if not isinstance(dato, dict):
            return
        ahora = time.monotonic()
        with self.condicion:
            if msg.topic == self.base + "/actuadores/leds/cmd":
                if self.modo == "automatico" or msg.retain:
                    return
                cambios = {k: v for k, v in dato.items() if k in COLORES and type(v) is bool}
                if not cambios:
                    return
                clave = dato.get("id") if isinstance(dato.get("id"), str) else str(uuid.uuid4())
                # En modo observador, la hora de inicio es la observacion del
                # comando en el broker; NO la pulsacion en el telefono.
                self.pendientes[clave] = {
                    "id": clave, "numero": len(self.resultados) + len(self.pendientes) + 1,
                    "cambios": cambios, "inicio": ahora, "hora_inicio": marca(),
                }
                self.orden_pendientes.append(clave)
                print("Comando visto:", cambios)
            elif msg.topic == self.base + "/actuadores/leds/estado":
                if msg.retain:
                    self.estado_inicial = dato
                    return
                if self.estado_inicial is None:
                    self.estado_inicial = dato
                ack = dato.get("ack_id")
                clave = ack if isinstance(ack, str) and ack in self.pendientes else None
                if clave is None and self.modo != "automatico":
                    # Los switches del movil no envian ID; asociacion por orden
                    # y coincidencia del estado solicitado (una orden a la vez).
                    for k in self.orden_pendientes:
                        solicitud = self.pendientes.get(k)
                        if solicitud and all(dato.get(c) is v for c, v in solicitud["cambios"].items()):
                            clave = k
                            break
                if clave is None:
                    return
                pendiente = self.pendientes.pop(clave)
                if clave in self.orden_pendientes:
                    self.orden_pendientes.remove(clave)
                coincide = all(dato.get(c) is v for c, v in pendiente["cambios"].items())
                latencia = round((ahora - pendiente["inicio"]) * 1000, 1)
                fila = {
                    "modo": self.modo, "numero": pendiente["numero"],
                    "cambio": json.dumps(pendiente["cambios"], ensure_ascii=False),
                    "hora_inicio": pendiente["hora_inicio"], "hora_confirmacion": marca(),
                    "latencia_ms": latencia, "confirmado": coincide,
                    "ack_id": ack if isinstance(ack, str) else "",
                    "nota": "ACK firmware; no mide luz LED",
                }
                self.resultados.append(fila)
                self.condicion.notify_all()
                print(f"Confirmado={coincide} latencia={latencia:.1f} ms cambio={pendiente['cambios']}")

    def automatico(self, cantidad: int, led: str, timeout: float) -> None:
        for n in range(cantidad):
            estado = n % 2 == 0
            identificador = str(uuid.uuid4())
            cambios = {led: estado}
            payload = {"id": identificador, **cambios}
            with self.condicion:
                t = time.monotonic()
                self.pendientes[identificador] = {
                    "id": identificador, "numero": n + 1, "inicio": t,
                    "hora_inicio": marca(), "cambios": cambios,
                }
                self.orden_pendientes.append(identificador)
            resultado = self.cliente.publish(
                self.base + "/actuadores/leds/cmd",
                json.dumps(payload, separators=(",", ":")), qos=1, retain=False,
            )
            if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
                self.fallar(identificador, "MQTT publish rc=" + str(resultado.rc))
            else:
                with self.condicion:
                    self.condicion.wait_for(lambda: identificador not in self.pendientes,
                                            timeout=timeout)
                    if identificador in self.pendientes:
                        self.fallar(identificador, "Sin confirmacion dentro del timeout")
            time.sleep(0.25)

    def fallar(self, clave: str, motivo: str) -> None:
        # La condicion es un RLock (Condition por defecto), admite llamada
        # desde un bloque with self.condicion de la misma hebra.
        with self.condicion:
            p = self.pendientes.pop(clave, None)
            if p is None:
                return
            if clave in self.orden_pendientes:
                self.orden_pendientes.remove(clave)
            self.resultados.append({
                "modo": self.modo, "numero": p["numero"],
                "cambio": json.dumps(p["cambios"], ensure_ascii=False),
                "hora_inicio": p["hora_inicio"], "hora_confirmacion": "",
                "latencia_ms": "", "confirmado": False, "ack_id": "",
                "nota": motivo,
            })
            print("FALLO:", motivo, p["cambios"])
            self.condicion.notify_all()

    def observar(self, cantidad: int, duracion: int) -> None:
        print(f"Observando hasta {cantidad} respuestas o {duracion} segundos.")
        print("Pulsa ON/OFF en el movil (o envia orden desde Claude), una a la vez.")
        fin = time.monotonic() + duracion
        with self.condicion:
            while len(self.resultados) < cantidad and time.monotonic() < fin:
                self.condicion.wait(timeout=0.2)
        for clave in list(self.pendientes):
            self.fallar(clave, "No se observo confirmacion durante ventana de prueba")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--modo", choices=["automatico", "observar"], default="automatico")
    p.add_argument("--broker", default="broker.hivemq.com")
    p.add_argument("--puerto", type=int, default=1883)
    p.add_argument("--base", default=BASE)
    p.add_argument("--cantidad", type=int, default=10)
    p.add_argument("--led", choices=COLORES, default="rojo")
    p.add_argument("--timeout", type=float, default=3.0)
    p.add_argument("--duracion", type=int, default=120)
    p.add_argument("--espera-conexion", type=float, default=40.0,
                   help="Segundos maximos para esperar CONNACK y SUBACK (default: 40)")
    p.add_argument("--salida", default="latencias_mqtt.csv")
    a = p.parse_args()
    if a.cantidad <= 0 or a.timeout <= 0 or a.duracion <= 0 or a.espera_conexion <= 0:
        p.error("cantidad, timeout, duracion y espera-conexion deben ser positivos")
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                          client_id="sis234-g6-latencia-" + uuid.uuid4().hex[:12])
    medidor = Medidor(cliente, a.base.rstrip("/"), a.modo)
    print(f"Broker MQTT: {a.broker}:{a.puerto} | Modo: {a.modo}")
    print("PRECAUCION: el modo automatico ACTIVA Y DESACTIVA un LED real.")
    prueba_iniciada = False
    cliente.reconnect_delay_set(min_delay=1, max_delay=8)
    try:
        # Paho MQTT Client.connect_async() programa la conexion y devuelve None.
        # No se debe tratar None como un error. La verificacion real se efectua
        # mediante CONNACK (on_connect) y SUBACK (on_subscribe).
        cliente.connect_async(a.broker, a.puerto, 30)
        cliente.loop_start()
        fin = time.monotonic() + a.espera_conexion
        while not medidor.suscrito.is_set():
            restante = fin - time.monotonic()
            if restante <= 0:
                etapa = "SUBACK" if medidor.conectado.is_set() else "CONNACK / conexion TCP"
                raise RuntimeError(
                    f"Timeout esperando {etapa} tras {a.espera_conexion:g} s. "
                    f"Verifica el puerto con Test-NetConnection {a.broker} -Port {a.puerto}"
                )
            if not medidor.suscrito.wait(min(5, restante)):
                print("[MQTT] Esperando conexion/suscripcion...", flush=True)
        prueba_iniciada = True
        # Permitir la llegada de los estados retained sin contarlos como ACK.
        time.sleep(0.5)
        if a.modo == "automatico":
            medidor.automatico(a.cantidad, a.led, a.timeout)
        else:
            medidor.observar(a.cantidad, a.duracion)
    finally:
        cliente.disconnect()
        cliente.loop_stop()
        if not prueba_iniciada:
            print("No se ejecutaron comandos: no se genera CSV de resultados.")
        else:
            guardar_resultados(a.salida, medidor.resultados)


def guardar_resultados(archivo: str, resultados: list[dict]) -> None:
    salida = Path(archivo)
    salida.parent.mkdir(parents=True, exist_ok=True)
    columnas = ["modo", "numero", "cambio", "hora_inicio", "hora_confirmacion",
                "latencia_ms", "confirmado", "ack_id", "nota"]
    with salida.open("w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(resultados)
    print("CSV guardado en:", salida.resolve())
    validas = [float(f["latencia_ms"]) for f in resultados
               if f["confirmado"] and f["latencia_ms"] != ""]
    print(f"Exitos: {len(validas)}/{len(resultados)}")
    if validas:
        print(f"Promedio: {statistics.mean(validas):.1f} ms | "
              f"Maximo: {max(validas):.1f} ms | "
              f"Cumplen <1000ms: {sum(v < 1000 for v in validas)}/{len(validas)}")
    print("Nota: no mide toque de pantalla -> encendido fisico del LED.")


if __name__ == "__main__":
    main()
