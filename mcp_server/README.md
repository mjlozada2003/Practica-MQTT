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
