# Evidencias verificadas — Práctica MQTT, Grupo 6

**Fecha:** jueves 29 de octubre de 2026  
**Fuente:** mensajes MQTT transcritos por el usuario, capturas que aportó y confirmaciones explícitas durante las pruebas.  
**Alcance:** este archivo NO representa un banco de pruebas ejecutado por el autor del documento ni sustituye el video de la Demo. Se identifican claramente pruebas observadas en capturas, valores transcritos y reportes verbales.

## 1. Hardware y conectividad

- ESP32 DOIT DevKit v1 con HC-SR04 en GPIO 14 (TRIG) y GPIO 27 (ECHO con divisor resistivo).
- LEDs rojo/amarillo/verde en GPIO 33/25/26, respectivamente.
- Broker MQTT: `broker.hivemq.com:1883`.
- Prefijo: `sis234/2026-2/grupo6`.
- El usuario confirmó envío de telemetría, recepción de comandos y funcionamiento físico independiente de los tres LEDs.

## 2. Exactitud del sensor — lecturas proporcionadas

| Referencia declarada | Lectura (cm) | Error absoluto (cm) | ¿≤3 cm? |
|---:|---:|---:|:---:|
| 5.00 | 5.08 | 0.08 | Sí |
| 10.00 | 10.03 | 0.03 | Sí |
| 20.00 | 20.12 | 0.12 | Sí |
| 30.00 | 29.95 | 0.05 | Sí |

Error absoluto medio de las cuatro muestras: **0.07 cm**. Máximo error observado: **0.12 cm**. Son **muestras únicas**; no se documentó calibración ni se aportaron cinco repeticiones por posición. Las lecturas oscilantes durante el cambio hacia 20 cm no cuentan como error con objeto inmóvil: el usuario confirmó que todavía lo acomodaba.

## 3. Frecuencia de publicación

- Registros aportados desde **06:00:03** hasta **06:00:33**, ambos incluidos: **31 mensajes** en un intervalo de 30 s entre extremos.
- **29 válidos** y **2 inválidos** (`{"cm":null,"valida":false}`).
- Cadencia observada: aproximadamente **1 publicación/s**. El cociente 31/30 es ~1.03 mensajes/s si se cuentan ambas fronteras; no constituye medición precisa por tener marcas con resolución de un segundo.
- Intervalo configurado en `ConfiguracionEjemplo.h`: **1000 ms**. La referencia del docente es ≥2 lecturas/s; **no se realizó ni se declara aquí una prueba a 2 Hz**.

## 4. Estabilidad

- Primer mensaje: **06:00:46**, distancia **5.18 cm**, válido.
- Último mensaje: **06:15:54**, distancia **5.08 cm**, válido.
- Duración observada: **15 minutos y 8 segundos**.
- Además de los dos extremos, el usuario confirmó explícitamente que continuaron llegando publicaciones aproximadamente cada segundo durante todo el intervalo y que no hubo reinicios ni desconexiones inesperadas.
- Resultado: **superado según la observación del usuario**. No se aportó registro crudo completo de 15 minutos.

## 5. Recuperación tras desconexión Wi-Fi

- **05:50:05**: `sis234/2026-2/grupo6/dispositivo/estado` → `{"en_linea":false}`.
- **05:50:46**: mismo tópico → `{"en_linea":true}`.
- El usuario confirmó que apagó y encendió Wi-Fi (sin cortar alimentación) y que, al recuperar la red, pudo publicar distancias y controlar LEDs nuevamente sin reiniciar ESP32.
- Intervalo entre eventos MQTT: **41 s**. **No equivale a la duración exacta de reconexión**, porque no se registró cuándo se restauró Wi-Fi.

## 6. App móvil — IoT MQTT Panel

- Captura aportada: [Gauge](capturas/gauge_iot_mqtt_panel_2026-10-29.jpg), muestra **15.54 cm** con hora **06:23:40**.
- Configuración efectivamente probada: Topic `sis234/2026-2/grupo6/sensor/distancia`, JSONPath `$.cm`, rango 0–30 cm.
- Tres interruptores para rojo, amarillo y verde: el usuario confirmó encendido/apagado individual exitoso.
- La función `Share via MQTT` se mostró en una captura, pero **no es prueba de exportación a archivo**. La exportación permanece pendiente.

## 7. Claude Desktop / MCP

- Captura aportada: [Servidor MCP en ejecución](capturas/claude_mcp_en_ejecucion_2026-10-29.png), nombre `objeto-inteligente-grupo6`.
- Se recibió una excepción real en `bridge.py:127`: `No existe una medicion valida disponible.` al consultar cuando `cm` era `null`.
- Después el usuario informó consulta exitosa mediante `obtener_distancia`: **10.84 cm**, lectura válida, ESP32 en línea, antigüedad **941 ms**.
- **Atención:** 941 ms es la **antigüedad de la medición**, **no** la latencia de comando.
- El usuario confirmó posteriormente: **«Claude acciona los leds»**. Se considera prueba funcional favorable comunicada por usuario; no se adjuntó traza de `ack_id` ni medición de latencia en esa ejecución.

## 8. Tareas y evidencia pendiente

1. **Latencia móvil → LED**: ejecutar 10 pruebas y registrar CSV con `scripts/medir_latencia_mqtt.py`; para afirmar end-to-end físico completo agregar video donde se vea toque y LED, o instrumentación física.
2. **Latencia Claude → ACK**: registrar 10 comandos y sus valores `latencia_ms`; corroborar visualmente LEDs.
3. **Exportación del panel**: exportar el archivo real desde Settings en IoT MQTT Panel, revisar privacidad y guardar en `mobile/export/`.
4. **Frecuencia ≥2 Hz, si se adopta el valor de referencia**: cambiar intervalo en configuración local a 500 ms, repetir conteo, estabilidad y documentar.
5. **Repeticiones de exactitud**: cinco lecturas por distancia con referencia física fija para reforzar evidencia.
6. Verificar commits por integrante en el repositorio GitHub real y registrar captura o `git shortlog -sne --all`.

## 9. Integridad de evidencias

- Ninguna cifra de latencia móvil→LED se inventó a partir de las capturas o marcas de segundos.
- Las capturas se conservaron originales. **Revisar datos visibles antes de subirlas a un repositorio público**.
- Las evidencias pertenecen a una fecha y dispositivo; los resultados de futuros cambios de firmware deben medirse de nuevo.
- Datos estructurados: [mediciones_2026-10-29.csv](mediciones_2026-10-29.csv).
