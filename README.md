# Práctica MQTT — Objeto inteligente con aplicación móvil y MCP

Sistema de SIS-234 que integra un ESP32, sensor ultrasónico HC-SR04, tres LEDs,
IoT MQTT Panel y Claude Desktop. Toda interacción con el objeto inteligente
pasa por el broker MQTT público; no existe comunicación directa desde la
aplicación o Claude hacia el ESP32.

## Integrantes

- María Jesús Lozada Peralta
- Samuel Jarro Rodriguez
- Katherine Montaño Mejia

## Arquitectura

```text
HC-SR04 + 3 LEDs <--GPIO--> ESP32 <--MQTT--> broker.hivemq.com
                                           ^              ^
                                           |              |
                                  IoT MQTT Panel    Servidor MCP <--stdio--> Claude
```

## Hardware

| Componente | Conexión |
|---|---|
| HC-SR04 Trigger | GPIO 14 |
| HC-SR04 Echo | GPIO 27 mediante divisor 1 kΩ/2 kΩ |
| LED rojo | GPIO 33 + resistencia 220 Ω |
| LED amarillo | GPIO 25 + resistencia 220 Ω |
| LED verde | GPIO 26 + resistencia 220 Ω |

El HC-SR04 se alimenta a 5 V. Todos los componentes comparten GND. El divisor se
conecta `Echo → 1 kΩ → nodo GPIO 27 → 2 kΩ → GND`; no conectar Echo directamente
al ESP32.

## Protocolo MQTT

Broker `broker.hivemq.com:1883`, MQTT 3.1.1, prefijo
`sis234/2026-2/grupo6`.

| Tópico | Flujo | QoS / Retain | Payload |
|---|---|---|---|
| `sensor/distancia` | ESP32 → panel/MCP | 0 / sí | `{"cm":18.4,"valida":true}` |
| `actuadores/leds/cmd` | panel/MCP → ESP32 | MCP QoS 1; panel QoS 0; ESP32 suscribe QoS 1 / no | `{"rojo":true}` |
| `actuadores/leds/estado` | ESP32 → panel/MCP | 0 / sí | Estado completo y `ack_id` opcional |
| `dispositivo/estado` | ESP32/LWT → panel/MCP | 0 / sí | `{"en_linea":true}` |

Los tópicos de la tabla se concatenan al prefijo. Los comandos pueden incluir
uno o varios LEDs; un campo omitido conserva su estado. El ESP32 rechaza JSON
inválido, tipos no booleanos y campos desconocidos.
PubSubClient publica telemetria y estados con QoS 0. La calidad efectiva
de entrega del comando depende del emisor; el broker publico TCP no usa TLS.

## Requisitos no funcionales declarados

| Atributo | Valor declarado | Método de verificación |
|---|---:|---|
| Estabilidad | 15 minutos | Operación continua sin reinicios/bloqueos |
| Exactitud | Error máximo ±3 cm en 2–30 cm | Cinta métrica en 5, 10, 20 y 30 cm |
| Respuesta app → ACK (referencia) | <1 segundo | 10 observaciones previas: 303–629 ms, solo orden vista → ACK |
| Respuesta script/MCP → ACK (referencia) | <1 segundo | 30 pruebas previas: 543–1997 ms, 6/30 superaron 1 s |
| Publicación (configuración del grupo) | 1 lectura/s (1000 ms) | Conteo registrado: 31 mensajes en 30 s |
| Reconexión | Automática | Corte y restauración de WiFi/MQTT |

El grupo **mantiene 1 Hz (1000 ms)**: se registraron 31 mensajes en 30 s.
La auditoria menciona 2 Hz como referencia, pero no se adoptara ese cambio.
La decision prioriza conservar la cadencia probada y debe justificarse en la
defensa si el docente pregunta por el objetivo de 2 Hz. Si existe
`include/Configuracion.h` local, mantener alli tambien
`SENSOR_PUBLISH_INTERVAL_MS = 1000`. Tras reflashear, repetir las pruebas de
latencia y estabilidad sin atribuirles resultados de la version anterior.
El bucle MQTT procesa comandos entre lecturas. `WiFi.setSleep(false)` puede
reducir latencia a costa de mayor consumo; no se ha re-medido tras cambiarlo.

Los CSV de latencia miden respuesta MQTT hasta ACK de firmware, **no** el
toque exacto de pantalla ni la luz fisica. Todavia no esta demostrado el RNF
fisico extremo a extremo. [Guía de medición](docs/evidencias/GUIA_MEDICION_LATENCIA.md).

## Preparar y cargar el firmware

1. Copiar `include/ConfiguracionEjemplo.h` como `include/Configuracion.h`.
2. Completar SSID y contraseña en el archivo local y comprobar que el intervalo
   sea de 1000 ms. Nunca incluir `Configuracion.h` en ZIP o Git.
3. Compilar y cargar:

```powershell
pio run -e esp32doit-devkit-v1
pio run -e esp32doit-devkit-v1 -t upload --upload-port COM3
pio device monitor -p COM3 -b 115200
```

Pruebas lógicas C++:

```powershell
pio test -e native
```

## Configurar IoT MQTT Panel

Seguir [mobile/CONFIGURACION_IOT_MQTT_PANEL.md](mobile/CONFIGURACION_IOT_MQTT_PANEL.md).
Después de probar el panel, exportarlo a `mobile/export/` y revisar que no
contenga información privada antes de versionarlo.

## Ejecutar el servidor MCP

```powershell
Set-Location mcp_server
Copy-Item .env.example .env
uv sync --group dev
uv run pytest
uv run servidor-mqtt-mcp
```

Herramientas expuestas:

| Herramienta | Parámetros | Propósito |
|---|---|---|
| `obtener_distancia` | Ninguno | Devuelve distancia válida, disponibilidad y antigüedad |
| `obtener_estado_leds` | Ninguno | Devuelve el estado confirmado de los tres LEDs |
| `controlar_leds` | `rojo?`, `amarillo?`, `verde?` | Envía comandos y espera `ack_id` hasta 3 s; informa si falta confirmación |

Si ya existe `.env` local, actualizar **también**
`MQTT_ACK_TIMEOUT_SECONDS=3.0`: copiar la plantilla no lo reemplaza.
`enviado:true, confirmado:false` significa que el estado final del LED es
desconocido, no que se haya aplicado el comando.

Copiar `config/claude_desktop_config.example.json` a la configuracion local de
Claude Desktop, reemplazar ambas rutas absolutas y cerrar Claude completamente
antes de volver a abrirlo.

Si el sensor publica `{"cm":null,"valida":false}`, la herramienta de lectura
responde un resultado estructurado con `cm: null`, `valida: false` y `mensaje`
en lugar de fallar con un error inesperado. Requiere reiniciar Claude Desktop
tras actualizar el servidor Python.

## Verificación y defensa

- [Guía de Demo](docs/GUIA_DEMO.md)
- [Guía de defensa individual](docs/GUIA_DEFENSA.md)
- [Plantilla de evidencias](docs/evidencias/plantilla_mediciones.csv)
- [Resultados registrados en pruebas reales](docs/evidencias/RESULTADOS_2026-10-29.md)
- [Mediciones comprobadas (CSV)](docs/evidencias/mediciones_2026-10-29.csv)
- [Script de medicion MQTT](scripts/medir_latencia_mqtt_v3.py)
- [Correcciones de la auditoría y pendientes](docs/CORRECCIONES_AUDITORIA_2026-10-29.md)

Cada integrante debe realizar commits desde su propia cuenta. Antes de publicar:

```powershell
pwsh -File scripts/auditar_secretos.ps1
git ls-files | Select-String -Pattern 'Configuracion\.h|\.env$|\.venv/'
git log --all --oneline -- include/Configuracion.h mcp_server/.env
```

El auditor local revisa incluso archivos ignorados, pero el historial Git
debe inspeccionarse por separado. El ZIP original traía configuraciones
privadas; el paquete corregido las excluye. Cambiar cualquier clave expuesta.
