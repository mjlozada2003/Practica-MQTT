# Guía rápida de demo — SIS-234 Grupo 6

Esta guía describe una **secuencia de demostración**; no certifica que las
pruebas con el firmware corregido ya hayan sido ejecutadas.

## Antes de comenzar

1. Compilar y subir el firmware con la configuración **local** de WiFi; verificar
   que `SENSOR_PUBLISH_INTERVAL_MS = 1000` (1 Hz) en `Configuracion.h`.
2. Actualizar `mcp_server/.env` local: `MQTT_ACK_TIMEOUT_SECONDS=3.0`; reiniciar
   totalmente Claude Desktop después de modificar código o configuración.
3. Abrir el monitor serie a 115200 baudios. Confirmar conexión WiFi/MQTT,
   suscripción enviada y disponibilidad `en_linea:true`.
4. Importar el panel: si el export tiene `host` y `clientId` vacíos, asignar
   `broker.hivemq.com:1883` y un Client ID único. Evitar comandos simultáneos
   desde celular y Claude mientras se mide latencia.
5. Comprobar divisor de tensión en ECHO, resistencias de los LEDs y GND común.
   No mostrar claves en VS Code, terminales, capturas o transmisión de pantalla.

## Secuencia ante el docente

| Paso | Mostrar y decir | Evidencia |
|---|---|---|
| 1. Sensado | Mover un objeto dentro de 2–30 cm; observar publicación JSON por MQTT | Monitor serie y tópico `sensor/distancia` |
| 2. Visualización | Abrir el Gauge de IoT MQTT Panel; se actualiza con `$.cm` | Panel del teléfono |
| 3. Actuación móvil | Encender/apagar uno de los tres LEDs; confirmar color real | LED y tópico `actuadores/leds/estado` |
| 4. Consulta Claude | «¿A qué distancia está el objeto ahora?» | Tool `obtener_distancia`, con dato válido o explicación de `cm:null` |
| 5. Control Claude | «Enciende el rojo y apaga los otros dos» | Tool `controlar_leds` y `ack_id`; `confirmado:false` obliga a comprobar |
| 6. Solicitud no soportada | «Mueve el servomotor a 90 grados» | Explicar que el objeto tiene tres LEDs, no servo; no inventar capacidad |
| 7. Reconexión | Cortar y restaurar WiFi; esperar reintentos y volver a controlar | Disponibilidad LWT y monitor serie; medir el tiempo real |
| 8. Estabilidad | Mantener sistema activo 10–15 min mientras se ejecuta la demo | Log continuo y conteo de mensajes |

## Cómo medir sin exagerar los resultados

- Ejecutar **30 comandos** con `scripts/medir_latencia_mqtt_v3.py` después de
  reflashear. El script mide publicación → ACK, no el instante de luz física.
- Contar publicaciones en 30 s: a 1 Hz se esperan aproximadamente 30 mensajes.
- Para «toque del móvil → luz física», usar video a 60 fps que incluya dedo y
  LED en el mismo plano, y medir 10 cambios.
- Documentar cualquier fallo o muestra superior a 1000 ms. El timeout del MCP
  de 3 s facilita una respuesta honesta, **no prueba** un RNF de 1 s.

Los resultados anteriores y sus limitaciones están en
[RESULTADOS_2026-10-29.md](evidencias/RESULTADOS_2026-10-29.md).
