# Evidencias de requisitos no funcionales

Crear `docs/evidencias/resultados/` localmente y guardar allí capturas, videos y
salidas crudas. Esa carpeta está ignorada para evitar subir archivos pesados sin
revisión. Los resultados consolidados que sí se entreguen deben copiarse de
forma deliberada a una carpeta versionada o resumirse en el README principal.

Procedimiento mínimo:

- Exactitud: cinco mediciones en 5, 10, 20 y 30 cm.
- Frecuencia: mantener 1 publicación por segundo; contar aproximadamente 30 mensajes en 30 s. La referencia de 2 Hz no se adopta.
- Latencia: medir diez comandos desde el panel y diez desde Claude; registrar porcentaje <1000 ms sin suponer cumplimiento.
- Estabilidad: 15 minutos sin reinicios ni bloqueos.
- Reconexión: registrar hora de corte, restauración y recuperación automática.


## Evidencias recibidas el 29/10/2026

- [Resumen de resultados observados](RESULTADOS_2026-10-29.md).
- [CSV de mediciones registradas](mediciones_2026-10-29.csv).
- [Procedimiento de medicion de latencia](GUIA_MEDICION_LATENCIA.md).
- [Captura Gauge](capturas/gauge_iot_mqtt_panel_2026-10-29.jpg).
- [Captura Claude MCP](capturas/claude_mcp_en_ejecucion_2026-10-29.png).

El script `scripts/medir_latencia_mqtt_v3.py` permite automatizar pruebas nuevas.
Ya existen CSV con 30 comandos y 10 observaciones MQTT previas a los cambios,
en `scripts/latencias_automaticas.csv` y `scripts/latencias_movil.csv`.
La latencia nueva y la prueba visual fisica siguen pendientes.
