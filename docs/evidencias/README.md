# Evidencias de requisitos no funcionales

Crear `docs/evidencias/resultados/` localmente y guardar allí capturas, videos y
salidas crudas. Esa carpeta está ignorada para evitar subir archivos pesados sin
revisión. Los resultados consolidados que sí se entreguen deben copiarse de
forma deliberada a una carpeta versionada o resumirse en el README principal.

Procedimiento mínimo:

- Exactitud: cinco mediciones en 5, 10, 20 y 30 cm.
- Frecuencia: contar mensajes durante 30 segundos; objetivo aproximado 30.
- Latencia: diez comandos desde el panel y diez desde Claude, todos <1000 ms.
- Estabilidad: 15 minutos sin reinicios ni bloqueos.
- Reconexión: registrar hora de corte, restauración y recuperación automática.


## Evidencias recibidas el 29/10/2026

- [Resumen de resultados observados](RESULTADOS_2026-10-29.md).
- [CSV de mediciones registradas](mediciones_2026-10-29.csv).
- [Procedimiento de medicion de latencia](GUIA_MEDICION_LATENCIA.md).
- [Captura Gauge](capturas/gauge_iot_mqtt_panel_2026-10-29.jpg).
- [Captura Claude MCP](capturas/claude_mcp_en_ejecucion_2026-10-29.png).

El script `scripts/medir_latencia_mqtt_v3.py` permite automatizar pruebas nuevas.
Ya existen [30 mediciones automáticas](../../scripts/latencias_automaticas.csv) y
[10 observaciones del móvil](../../scripts/latencias_movil.csv). La medición física
desde el toque hasta el LED y el registro específico de latencias de Claude siguen pendientes.
La exportación del panel también está [incorporada](../../mobile/export/panel_grupo6_export.json).
