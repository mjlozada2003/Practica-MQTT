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
| `actuadores/leds/cmd` | panel/MCP → ESP32 | panel: 0, MCP: 1 / no | `{"rojo":true}` |
| `actuadores/leds/estado` | ESP32 → panel/MCP | 0 / sí | Estado completo y `ack_id` opcional |
| `dispositivo/estado` | ESP32/LWT → panel/MCP | 0 / sí | `{"en_linea":true}` |

Los tópicos de la tabla se concatenan al prefijo. Los comandos pueden incluir
uno o varios LEDs; un campo omitido conserva su estado. El ESP32 rechaza JSON
inválido, tipos no booleanos y campos desconocidos.

## Requisitos no funcionales declarados

| Atributo | Valor declarado | Método de verificación |
|---|---:|---|
| Estabilidad | 15 minutos | Operación continua sin reinicios/bloqueos |
| Exactitud | Error máximo ±3 cm en 2–30 cm | Cinta métrica en 5, 10, 20 y 30 cm |
| Respuesta | <1 segundo | Panel/Claude → broker → LED confirmado |
| Publicación | 1 lectura/s | Conteo durante 30 segundos |
| Reconexión | Automática | Corte y restauración de WiFi/MQTT |

La frecuencia declarada y probada es de 1 Hz. La rúbrica escrita menciona 2 Hz
como referencia; se mantiene 1 Hz considerando la aclaración del docente sobre
la frecuencia de publicación. El control de LEDs se atiende entre mediciones.

## Preparar y cargar el firmware

1. Copiar `include/ConfiguracionEjemplo.h` como `include/Configuracion.h`.
2. Completar solo SSID y contraseña en el archivo local.
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
Importar [el panel exportado](mobile/export/panel_grupo6_export.json), que incluye
un Gauge y tres switches. La conexión usa `broker.hivemq.com:1883`; asignar un
Client ID distinto en cada teléfono y comprobar lectura y control después de importar.

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
| `controlar_leds` | `rojo?`, `amarillo?`, `verde?` | Cambia LEDs y espera `ack_id` hasta 900 ms |

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

Cada integrante debe realizar commits desde su propia cuenta. Antes de publicar:

```powershell
pwsh -File scripts/auditar_secretos.ps1
```

No se requiere informe técnico. El repositorio, configuraciones y prototipo son
la referencia para la Demo y la defensa individual.
