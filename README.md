# Práctica MQTT — Objeto inteligente con aplicación móvil y MCP

Sistema de SIS-234 que integra un ESP32, un sensor ultrasónico HC-SR04, tres LEDs,
IoT MQTT Panel y Claude Desktop. El ESP32 publica distancias y recibe comandos
mediante un broker MQTT en la nube. La aplicación móvil y el servidor MCP se
conectan al mismo broker.

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

El firmware está en `src/` e `include/`; el servidor Python, en
`mcp_server/src/servidor_mcp/`; el panel exportado, en `mobile/export/`.

## Hardware

| Componente | Conexión |
|---|---|
| HC-SR04 Trigger | GPIO 14 |
| HC-SR04 Echo | GPIO 27 mediante divisor 1 kΩ/2 kΩ |
| LED rojo | GPIO 33 + resistencia 220 Ω |
| LED amarillo | GPIO 25 + resistencia 220 Ω |
| LED verde | GPIO 26 + resistencia 220 Ω |

El HC-SR04 se alimenta a 5 V y todos los componentes comparten GND. El divisor se
conecta `Echo → 1 kΩ → nodo GPIO 27 → 2 kΩ → GND`. El rango de medición configurado
es de 2 a 30 cm. Fuera del rango o sin eco se publica una lectura inválida.

## Tópicos y mensajes MQTT

Broker: `broker.hivemq.com:1883`, MQTT 3.1.1, sin usuario ni contraseña.
Prefijo de todos los tópicos: `sis234/2026-2/grupo6/`.

| Sufijo del tópico | Publica → recibe | QoS | Retain | Mensaje |
|---|---|---|---|---|
| `sensor/distancia` | ESP32 → móvil/MCP | 0 | Sí | `{"cm":18.4,"valida":true}` |
| `actuadores/leds/cmd` | móvil/MCP → ESP32 | móvil: 0; MCP: 1 | No | `{"rojo":true}` |
| `actuadores/leds/estado` | ESP32 → móvil/MCP | 0 | Sí | `{"rojo":true,"amarillo":false,"verde":false}` |
| `dispositivo/estado` | ESP32/LWT → móvil/MCP | 0 | Sí | `{"en_linea":true}` |

El tópico completo de distancia, por ejemplo, es
`sis234/2026-2/grupo6/sensor/distancia`. Una lectura inválida se publica como
`{"cm":null,"valida":false}`. El LWT informa `{"en_linea":false}` cuando el broker
detecta una desconexión inesperada del ESP32.

Los comandos aceptan uno o varios colores con valores booleanos; los omitidos
conservan su estado. Se rechazan JSON inválido, campos desconocidos y tipos
incorrectos. El MCP añade un `id` al comando; el firmware lo devuelve como
`ack_id` en el estado para correlacionar la confirmación.

## Valores declarados y comportamiento

| Atributo | Valor declarado |
|---|---|
| Estabilidad | 15 minutos de operación continua sin reinicios ni bloqueos |
| Exactitud | Error máximo ±3 cm en el rango de 2–30 cm |
| Respuesta del actuador | Menos de 1 segundo desde la aplicación móvil |
| Publicación | 1 lectura/s, intervalo configurado de 1000 ms |
| Reconexión | Automática de WiFi y MQTT, con espera progresiva entre intentos |

Estos valores son los objetivos del sistema. Los resultados registrados y sus
límites se detallan al final de este documento.

## Preparación del ESP32

Se necesita PlatformIO y una conexión WiFi compatible con el ESP32. Desde la
raíz del repositorio, crear la configuración local una sola vez:

```powershell
Copy-Item include/ConfiguracionEjemplo.h include/Configuracion.h
```

Completar `WIFI_SSID` y `WIFI_PASSWORD` en `include/Configuracion.h`.
Ese archivo está excluido de Git. La plantilla contiene los pines, tópicos,
rango de medición e intervalo de publicación.

Compilar, cargar y abrir el monitor serie; reemplazar `COM3` por el puerto real:

```powershell
pio run -e esp32doit-devkit-v1
pio run -e esp32doit-devkit-v1 -t upload --upload-port COM3
pio device monitor -p COM3 -b 115200
```

## Aplicación móvil: IoT MQTT Panel

Importar [panel_grupo6_export.json](mobile/export/panel_grupo6_export.json).
Incluye un Gauge de distancia y tres switches para los LEDs.

| Campo de conexión | Valor |
|---|---|
| Broker | `broker.hivemq.com` |
| Puerto | `1883` |
| MQTT | 3.1.1 |
| Usuario/contraseña | Vacíos |
| Client ID | Un valor distinto por teléfono, como `sis234-g6-panel-kath` |

El Gauge se suscribe a `sis234/2026-2/grupo6/sensor/distancia`, utiliza JSONPath
`$.cm`, rango 0–30 y unidad cm.

Los switches publican en `sis234/2026-2/grupo6/actuadores/leds/cmd`, con QoS 0 y
Retain desactivado. Se suscriben al estado en
`sis234/2026-2/grupo6/actuadores/leds/estado`.

| Switch | JSONPath del estado | Plantilla JSON de publicación |
|---|---|---|
| Rojo | `$.rojo` | `{"rojo":<payload>}` |
| Amarillo | `$.amarillo` | `{"amarillo":<payload>}` |
| Verde | `$.verde` | `{"verde":<payload>}` |

Activar `Payload is JSON Data`; usar `true` para ON y `false` para OFF, sin
comillas. Las plantillas anteriores reciben esos valores en `<payload>`.
Con tópicos completos, desactivar el prefijo del dashboard para cada control.
Después de importar, comprobar conexión, actualización del Gauge y los tres LEDs.

## Servidor MCP y Claude Desktop

Se necesita Python 3.10 o superior, `uv` y Claude Desktop. Desde la raíz:

```powershell
Set-Location mcp_server
Copy-Item .env.example .env
uv sync --group dev
uv run servidor-mqtt-mcp
```

Crear `.env` una sola vez. Permite configurar broker, puerto, keepalive,
prefijo de tópicos, espera del ACK y antigüedad máxima de la distancia. Los
valores predeterminados son 1883, 30 s, `sis234/2026-2/grupo6`, 3 s para ACK
y 3.5 s de antigüedad máxima. `.env` está excluido de Git.
Si ya existe un `.env` local, actualizar `MQTT_ACK_TIMEOUT_SECONDS=3.0`:
copiar la plantilla no modifica ese archivo existente.

Para conectar Claude, utilizar la sección `mcpServers` de
[claude_desktop_config.example.json](config/claude_desktop_config.example.json)
en la configuración local de Claude Desktop. Reemplazar las rutas por la ruta
absoluta de `uv.exe` y la carpeta `mcp_server` de este proyecto. Si hay otros
servidores configurados, conservarlos. Cerrar Claude completamente y volver a abrirlo.

El servidor usa `stdio` para MCP y envía sus logs a `stderr`.

| Herramienta | Parámetros | Propósito |
|---|---|---|
| `obtener_distancia` | Ninguno | Devuelve cm, validez, disponibilidad y antigüedad de la lectura |
| `obtener_estado_leds` | Ninguno | Consulta el estado de los tres LEDs reportado por el ESP32 |
| `controlar_leds` | `rojo`, `amarillo`, `verde`: booleanos opcionales | Cambia los colores indicados y espera su `ack_id` hasta 3 s |

Si no hay una distancia disponible, `obtener_distancia` devuelve `cm: null`,
`valida: false` y un `mensaje` explicativo. La antigüedad de la lectura no es la
latencia de un comando. La confirmación de LEDs corresponde al estado informado
por el firmware.
Si el comando no recibe ACK a tiempo, `controlar_leds` devuelve
`enviado: true, confirmado: false`: la publicación fue aceptada localmente,
pero el estado físico queda desconocido. Las distancias MQTT retenidas no se
consideran mediciones recientes; el MCP espera la siguiente publicación nueva.

Ejemplos de uso en Claude: «¿A qué distancia está el objeto?», «Enciende el rojo y
apaga los demás» y «Apaga los tres LEDs».

## Pruebas y medición

Pruebas lógicas C++ desde la raíz:

```powershell
pio test -e native
```

Pruebas Python desde `mcp_server`:

```powershell
uv run pytest
```

Para verificar seis combinaciones de LEDs con ACK y observación física, desde
`mcp_server` y con el ESP32 conectado:

```powershell
uv run python ../scripts/prueba_leds_mqtt.py
```

Esta prueba cambia LEDs reales y termina solicitando que queden apagados.

Para registrar mediciones MQTT, desde `mcp_server`:

```powershell
uv run python ../scripts/medir_latencia_mqtt_v3.py --modo automatico --cantidad 10 --led rojo --salida latencias_automaticas_nuevas.csv
uv run python ../scripts/medir_latencia_mqtt_v3.py --modo observar --cantidad 10 --duracion 120 --salida latencias_movil_nuevas.csv
```

El modo `automatico` alterna el LED rojo y mide publicación local → ACK
correlacionado. El modo `observar` mide comando recibido por el observador →
estado recibido; accionar un control por vez. Ninguno mide directamente desde
el toque en el teléfono hasta el cambio físico del LED. Esa medición requiere
video o instrumentación que observe ambos eventos.

## Resultados registrados el 29/10/2026

Las evidencias incluyen lecturas y confirmaciones aportadas por el grupo,
capturas y CSV. Las doce pruebas Python pasaron con MCP 2.3.0 y paho-mqtt 2.1.0
instalados; las pruebas usan un cliente MQTT simulado.

| Referencia física | Lectura | Error absoluto |
|---|---|---|
| 5 cm | 5.08 cm | 0.08 cm |
| 10 cm | 10.03 cm | 0.03 cm |
| 20 cm | 20.12 cm | 0.12 cm |
| 30 cm | 29.95 cm | 0.05 cm |

Son muestras únicas por posición; error máximo observado 0.12 cm. No acreditan
por sí solas el error máximo de todo el rango en cualquier condición.

| Prueba | Resultado registrado | Alcance |
|---|---|---|
| Publicación | 31 mensajes entre 06:00:03 y 06:00:33; 29 válidos y 2 inválidos | Aproximadamente 1 Hz, con marcas de un segundo |
| Estabilidad | 15 minutos y 8 segundos | Continuidad sin reinicios reportada por el grupo; sin registro crudo completo |
| Reconexión WiFi | Estado offline a 05:50:05 y online a 05:50:46 | Recuperación sin reiniciar reportada; 41 s entre eventos, sin hora exacta de restauración de red |
| Consulta de Claude | 10.84 cm, antigüedad 941 ms | Consulta y control de LEDs reportados por el grupo |
| 30 comandos automáticos | Promedio 922.03 ms; máximo 1996.7 ms; 6 por encima de 1 s | Publicación local → ACK |
| 10 comandos observados del móvil | Promedio 452.0 ms; máximo 628.5 ms | Comando observado → confirmación observada |


Archivos de respaldo:

- [Mediciones resumidas](docs/evidencias/mediciones_2026-10-29.csv).
- [30 latencias automáticas con ACK](scripts/latencias_automaticas.csv).
- [10 latencias observadas del móvil](scripts/latencias_movil.csv).
- [Transcripción de 30 mediciones](scripts/Latencias_MQTT_Grupo6.csv).
- [Captura del Gauge](docs/evidencias/capturas/gauge_iot_mqtt_panel_2026-10-29.jpg).
- [Captura del servidor MCP](docs/evidencias/capturas/claude_mcp_en_ejecucion_2026-10-29.png).
- [Plantilla para nuevas mediciones](docs/evidencias/plantilla_mediciones.csv).

Las credenciales WiFi se mantienen en `include/Configuracion.h` y los ajustes
locales del MCP en `.env`. Para revisar posibles secretos desde la raíz:

```powershell
pwsh -File scripts/auditar_secretos.ps1
```
