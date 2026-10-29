# Configuración de IoT MQTT Panel

## Conexión

| Campo | Valor |
|---|---|
| Nombre | SIS234 Grupo 6 |
| Client ID | `sis234-g6-panel-<alias-del-telefono>` |
| Broker | `broker.hivemq.com` |
| Puerto | `1883` |
| Usuario/contraseña | Vacíos |
| MQTT | 3.1.1 |

No reutilizar el mismo Client ID en dos teléfonos abiertos simultáneamente.
El export real `export/panel_grupo6_export.json` deja `host` y `clientId`
vacíos por privacidad. Al importarlo, poner `broker.hivemq.com`, puerto TCP
`1883` y un Client ID único para el teléfono.

## Paneles

### Distancia actual — Gauge

- Subscribe topic: `sis234/2026-2/grupo6/sensor/distancia`
- Payload is JSON: sí.
- JSON path: `$.cm`.
- QoS: 0.
- Mínimo: 0; máximo: 30; unidad: cm.

### Historial — Line Graph (pendiente; NO figura en el export)

- Mismo tópico y JSON path del Gauge.
- QoS: 0.
- Conservar suficientes puntos para mostrar al menos 30 segundos.

### Switches rojo, amarillo y verde

Los tres publican en `sis234/2026-2/grupo6/actuadores/leds/cmd`, QoS 0
(configuracion probada en el telefono), Retain desactivado.

- Activar **Disable dashboard prefix topic** con topicos completos.
- Configurar **Subscribe Topic**: `sis234/2026-2/grupo6/actuadores/leds/estado`.
- Activar **Payload is JSON Data**.
- **Payload on**: `true` (sin comillas); **Payload off**: `false`.
- **JSON pattern for publish**: incluye `<payload>` sin comillas.

| Switch | JSONPath subscribe | JSON pattern publish |
|---|---|---|
| Rojo | `$.rojo` | `{"rojo":<payload>}` |
| Amarillo | `$.amarillo` | `{"amarillo":<payload>}` |
| Verde | `$.verde` | `{"verde":<payload>}` |

Estos ajustes publican JSON booleano valido; no usar JSON completo simultaneamente
como Payload on/off y como plantilla de publicacion.

### Indicadores confirmados (pendientes; NO figuran en el export)

Crear tres LED Indicator suscritos a
`sis234/2026-2/grupo6/actuadores/leds/estado`, con JSON paths `$.rojo`,
`$.amarillo` y `$.verde`. Estos indicadores representan el estado confirmado
por el ESP32, no solamente la orden enviada.

Crear un cuarto indicador suscrito a
`sis234/2026-2/grupo6/dispositivo/estado`, JSON path `$.en_linea`.

## Exportación

Después de probar el panel en el teléfono, usar la opción Export de la
aplicación y guardar el archivo generado en `mobile/export/`. Revisar que no
contenga datos privados antes de agregarlo a Git. El archivo real debe provenir
de la aplicación; este repositorio no fabrica un esquema de exportación.

**Export recibido:** contiene 1 Gauge y 3 Switches, sin Line Graph ni los
4 indicadores independientes propuestos arriba. Para agregarlos, configurarlos
en la aplicación y **volver a exportar** el JSON real. El icono de encendido
del LED amarillo es `switch_off` en ese archivo (cosmético); corregirlo en
la aplicación si se desea.
