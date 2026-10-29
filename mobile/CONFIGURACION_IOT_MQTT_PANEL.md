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

## Paneles

### Distancia actual — Gauge

- Subscribe topic: `sis234/2026-2/grupo6/sensor/distancia`
- Payload is JSON: sí.
- JSON path: `$.cm`.
- QoS: 0.
- Mínimo: 0; máximo: 30; unidad: cm.

### Historial — Line Graph (opcional, no incluido en la exportación)

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

### Indicadores adicionales (opcionales, no incluidos en la exportación)

Crear tres LED Indicator suscritos a
`sis234/2026-2/grupo6/actuadores/leds/estado`, con JSON paths `$.rojo`,
`$.amarillo` y `$.verde`. Estos indicadores representan el estado confirmado
por el ESP32, no solamente la orden enviada.

Crear un cuarto indicador suscrito a
`sis234/2026-2/grupo6/dispositivo/estado`, JSON path `$.en_linea`.

## Exportación

La exportación está incluida en [panel_grupo6_export.json](export/panel_grupo6_export.json).
Contiene un Gauge y tres switches; el Gauge cumple la visualización gráfica solicitada.

1. Importar el archivo en IoT MQTT Panel.
2. Revisar la conexión: broker `broker.hivemq.com`, puerto `1883`, sin usuario ni contraseña.
3. Asignar un Client ID único por teléfono antes de conectar.
4. Verificar que el Gauge cambie y que cada switch controle el LED correspondiente.

El campo `host`, vacío en la exportación original, se completó con el broker público
documentado. Si se vuelve a exportar el panel, revisar conexión y datos privados
antes de reemplazar el archivo versionado.
