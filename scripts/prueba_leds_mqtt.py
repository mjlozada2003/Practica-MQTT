"""Prueba real de comandos LEDs / confirmaciones MQTT del Grupo 6.

Ejecutar: python prueba_leds_mqtt.py
Necesita: pip install paho-mqtt

No valida por si solo el estado luminoso visible: observar los LEDs.
"""

import json
import threading
import time
import uuid

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PUERTO = 1883
BASE = "sis234/2026-2/grupo6"
TOPIC_CMD = f"{BASE}/actuadores/leds/cmd"
TOPIC_ESTADO = f"{BASE}/actuadores/leds/estado"
TOPIC_DISPOSITIVO = f"{BASE}/dispositivo/estado"
TIMEOUT = 3.0


class PruebaLeds:
    def __init__(self):
        self.condicion = threading.Condition()
        self.suscrito = False
        self.en_linea = None
        self.confirmaciones = {}
        self.cliente = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="grupo6-test-leds-" + uuid.uuid4().hex[:12],
        )
        self.cliente.on_connect = self._conectar
        self.cliente.on_subscribe = self._suscripcion
        self.cliente.on_message = self._mensaje
        self.cliente.on_disconnect = self._desconexion

    def _conectar(self, cliente, userdata, flags, codigo, propiedades):
        if codigo != 0:
            print(f"ERROR conexion MQTT: {codigo}", flush=True)
            return
        self.suscrito = False
        self.en_linea = None
        self.confirmaciones.clear()
        cliente.subscribe([(TOPIC_ESTADO, 1), (TOPIC_DISPOSITIVO, 1)])
        print("MQTT conectado; esperando confirmacion de suscripcion...", flush=True)

    def _suscripcion(self, cliente, userdata, mid, codigos, propiedades):
        if any(c.is_failure for c in codigos):
            print(f"ERROR SUBACK: {codigos}", flush=True)
            return
        with self.condicion:
            self.suscrito = True
            self.condicion.notify_all()
        print("Suscripcion confirmada por HiveMQ.", flush=True)

    def _desconexion(self, cliente, userdata, flags, codigo, propiedades):
        with self.condicion:
            self.suscrito = False
            self.en_linea = None
            self.condicion.notify_all()
        print(f"Desconexion de HiveMQ: {codigo}", flush=True)

    def _mensaje(self, cliente, userdata, mensaje):
        try:
            datos = json.loads(mensaje.payload.decode("utf-8"))
            if not isinstance(datos, dict):
                return
            with self.condicion:
                if mensaje.topic == TOPIC_DISPOSITIVO:
                    estado = datos.get("en_linea")
                    if type(estado) is bool:
                        self.en_linea = estado
                        self.condicion.notify_all()
                elif mensaje.topic == TOPIC_ESTADO:
                    ack_id = datos.get("ack_id")
                    if isinstance(ack_id, str):
                        self.confirmaciones[ack_id] = (datos, time.monotonic())
                        self.condicion.notify_all()
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass

    def esperar_listo(self, segundos=10):
        fin = time.monotonic() + segundos
        with self.condicion:
            while not (self.suscrito and self.en_linea is True):
                resto = fin - time.monotonic()
                if resto <= 0:
                    raise TimeoutError(
                        "No se confirmo suscripcion y estado en_linea=true. "
                        "Comprueba que el ESP32 esta encendido y conectado."
                    )
                self.condicion.wait(resto)

    def ejecutar_comando(self, titulo, cambios, espera_visual=1.0):
        identificador = uuid.uuid4().hex
        payload = json.dumps({"id": identificador, **cambios}, separators=(",", ":"))
        print(f"\n{titulo} | comando: {payload}", flush=True)
        inicio = time.monotonic()
        resultado = self.cliente.publish(TOPIC_CMD, payload, qos=1, retain=False)
        if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Fallo al publicar comando MQTT: {mqtt.error_string(resultado.rc)}")
        with self.condicion:
            fin = inicio + TIMEOUT
            while identificador not in self.confirmaciones:
                if not self.suscrito or self.en_linea is False:
                    raise RuntimeError("Se perdio la conexion MQTT o el ESP32 se desconecto")
                restante = fin - time.monotonic()
                if restante <= 0:
                    raise TimeoutError(f"No llego ACK correlacionado para {titulo} en {TIMEOUT}s")
                self.condicion.wait(restante)
            datos, instante_ack = self.confirmaciones.pop(identificador)
        estado = {k: datos.get(k) for k in ("rojo", "amarillo", "verde")}
        coinciden = all(estado[k] is valor for k, valor in cambios.items())
        latencia_ms = (instante_ack - inicio) * 1000
        print(f"ACK: {datos}", flush=True)
        print(f"Latencia de comando a ACK: {latencia_ms:.1f} ms", flush=True)
        if not coinciden:
            raise AssertionError(f"Estado devuelto NO coincide con cambios solicitados: {cambios}")
        print("Resultado: ACK correcto. OBSERVAR estado fisico del LED.", flush=True)
        if espera_visual:
            time.sleep(espera_visual)
        return latencia_ms


def main():
    prueba = PruebaLeds()
    latencias = []
    pruebas = [
        ("00 Todos apagados", {"rojo": False, "amarillo": False, "verde": False}),
        ("01 Solo rojo", {"rojo": True, "amarillo": False, "verde": False}),
        ("02 Solo amarillo", {"rojo": False, "amarillo": True, "verde": False}),
        ("03 Solo verde", {"rojo": False, "amarillo": False, "verde": True}),
        ("04 Los tres encendidos", {"rojo": True, "amarillo": True, "verde": True}),
        ("05 Todos apagados", {"rojo": False, "amarillo": False, "verde": False}),
    ]
    conectado = False
    iniciado = False
    cantidad = 0
    try:
        prueba.cliente.connect(BROKER, PUERTO, keepalive=30)
        conectado = True
        prueba.cliente.loop_start()
        iniciado = True
        prueba.esperar_listo()
        print("ESP32 en linea. Prueba de 6 estados; cada estado dura 1 segundo.")
        for titulo, cambios in pruebas:
            latencias.append(prueba.ejecutar_comando(titulo, cambios))
            cantidad += 1
        print("\n=== RESULTADOS ===")
        print(f"Confirmaciones correctas: {cantidad}/6")
        print(f"Latencia ACK promedio: {sum(latencias)/len(latencias):.1f} ms")
        print(f"Latencia ACK maxima: {max(latencias):.1f} ms")
        print("Comprobacion visual de LEDs: pendiente de observacion humana.")
        print("ATENCION: ACK no demuestra por si solo la latencia fisica luminosa.")
    except (RuntimeError, TimeoutError, AssertionError, OSError) as e:
        print(f"\nPRUEBA INCOMPLETA: {e}", flush=True)
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por usuario.", flush=True)
    finally:
        if iniciado and prueba.suscrito and prueba.en_linea is True:
            try:
                print("\nRestableciendo estado: todos apagados...", flush=True)
                prueba.ejecutar_comando(
                    "Apagado final", {"rojo": False, "amarillo": False, "verde": False},
                    espera_visual=0,
                )
            except (RuntimeError, TimeoutError, AssertionError, KeyboardInterrupt) as e:
                print(f"ADVERTENCIA: no se pudo confirmar apagado final: {e}")
        if conectado:
            prueba.cliente.disconnect()
        if iniciado:
            prueba.cliente.loop_stop()


if __name__ == "__main__":
    main()
