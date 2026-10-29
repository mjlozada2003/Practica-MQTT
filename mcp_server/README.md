# Servidor MCP MQTT

Puente local entre Claude Desktop y el ESP32 mediante el broker MQTT. Expone
`obtener_distancia`, `obtener_estado_leds` y `controlar_leds`.

## Preparación

```powershell
Copy-Item .env.example .env
uv sync --group dev
uv run pytest
uv run servidor-mqtt-mcp
```

El servidor utiliza `stdio`: no agregar `print()` ni logs dirigidos a stdout.
Los mensajes de diagnóstico se envían a stderr mediante `logging`.

**Confirmación de comandos.** La plantilla `.env.example` configura
`MQTT_ACK_TIMEOUT_SECONDS=3.0`. Si tu `.env` ya existe con 0.9, modifica
ese valor manualmente y reinicia Claude Desktop. Al vencer el plazo,
`controlar_leds` responde con `enviado:true, confirmado:false` y un mensaje
para verificar el estado posteriormente. **No significa que el LED haya
cambiado**. Con `ack_id` correcto devuelve `confirmado:true`.

## Lectura invalida (`cm: null`)

La herramienta `obtener_distancia` ahora devuelve un resultado estructurado cuando
el sensor reporta una lectura nula, desactualizada o el ESP32 esta desconectado:

```json
{"cm": null, "valida": false, "mensaje": "No existe una medicion valida disponible."}
```

La salida evita una excepcion MCP inesperada y no inventa una medicion. Este
cambio afecta solo la presentacion de `obtener_distancia`.
Reiniciar Claude Desktop para cargar el codigo actualizado.
