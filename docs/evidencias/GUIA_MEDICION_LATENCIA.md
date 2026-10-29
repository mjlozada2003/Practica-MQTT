# Medición MQTT de latencia — scripts del Grupo 6

## Qué mide y qué NO mide

- `--modo automatico` publica desde Python comandos `{"id": "uuid", "rojo": true/false}` y correlaciona la respuesta de `actuadores/leds/estado` con el campo `ack_id`. Tiempo con `time.monotonic`: justo antes de invocar `publish()` hasta recibir el ACK en la misma computadora. Mide ida+vuelta MQTT y respuesta del firmware, **no** la luz física del LED ni la pulsación móvil.
- `--modo observar` se suscribe al comando publicado por IoT MQTT Panel o Claude y detecta el estado posterior. Estima **comando visto por el observador en el broker → estado confirmado visto en el broker**. No puede medir la espera desde la pulsación de la pantalla hasta la llegada al broker, ni tiempo físico de iluminación.
- Las órdenes móviles no traen `id`: asociar una orden a la vez; no tocar otros controles durante el ensayo. Claude sí puede enviar `id`.
- `ack_id` es la confirmación informada por el programa del ESP32, no una medición óptica independiente.

## Instalación (PowerShell Windows)

```powershell
cd C:\IoT-MQTT\Yisus\Practica-MQTT\mcp_server
.\.venv\Scripts\python.exe -m pip show paho-mqtt
```

Si `pip show` no funciona (entornos `uv` sin pip), usar `uv run python -c "import paho.mqtt.client"` y ejecutar el script con `uv run python ...`. Para un entorno Python normal:

```powershell
python -m pip install "paho-mqtt>=2.1,<3"
```

## Prueba automática de 10 órdenes (cambia físicamente el LED rojo)

Ejecutar desde la raíz del repositorio:

```powershell
python .\scripts\medir_latencia_mqtt.py --modo automatico --cantidad 10 --led rojo --salida latencias_automaticas.csv
```

Con `uv` desde la carpeta `mcp_server`:

```powershell
uv run python ..\scripts\medir_latencia_mqtt.py --modo automatico --cantidad 10 --led rojo --salida latencias_automaticas.csv
```

No usar el móvil o Claude para alterar simultáneamente el mismo LED. El script alterna ON/OFF. Validar que llegue a 10 respuestas sin timeout. El CSV contiene hora de envío, hora de confirmación, latencia y estado.

## Observar 10 acciones del celular

```powershell
python .\scripts\medir_latencia_mqtt.py --modo observar --cantidad 10 --duracion 120 --salida latencias_movil_observadas.csv
```

Con el script esperando, activar y desactivar un solo LED desde IoT MQTT Panel una acción a la vez. Si hay un fallo, conservar la fila de timeout. Reportar la métrica como **«orden observada → confirmación observada»**, NO «toque → LED físico».

## Medición física extremo a extremo

Para evaluar estrictamente la referencia de **≤1000 ms** desde tocar el celular hasta que el LED real se ilumina o se apaga:

1. Grabar un video a 60 fps o más con **celular (toque)** y **LED físico** visibles simultáneamente.
2. Para 10 activaciones, anotar fotograma de inicio del toque y primer fotograma de cambio visible en LED.
3. `latencia_ms = (fotograma_led - fotograma_toque) * 1000 / fps`.
4. Conservar el video sin cortes y guardar tabla CSV. Un video a 60 fps tiene resolución temporal de unos 16.7 ms (sin considerar el instante real del toque).

Esto sí es una medida visual aproximada de la latencia física completa. Ni los timestamps de HiveMQ con resolución 1 segundo ni la edad de lectura MCP sirven para reemplazarla.

## Seguridad

Usa un broker MQTT público TCP sin cifrar; evita publicar credenciales. IDs MQTT únicos para cada proceso. El script modifica LEDs en el modo automático; retirar la opción si no se desea accionar el hardware.
