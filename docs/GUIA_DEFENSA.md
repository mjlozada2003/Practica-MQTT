# Preparación de defensa individual — SIS-234 Grupo 6

Cada integrante debe explicar hardware, firmware, MQTT, app y servidor MCP.

1. **¿Por qué divisor en ECHO?** El HC-SR04 entrega una señal de hasta 5 V,
   mientras el ESP32 trabaja a 3,3 V. Con 1 kΩ arriba y 2 kΩ a GND, la salida
   ideal es 5×2/(1+2)=3,33 V. No conectar el pin Echo directamente.
2. **¿Cómo mide?** `pulseIn` cuenta la duración del eco; distancia en cm =
   microsegundos ×0,01715. El factor considera el trayecto ida y vuelta.
   Sin eco devuelve lectura inválida; no se inventa un valor.
3. **¿Qué hace `millis()`?** Programa mediciones y reintentos sin una espera
   fija larga, permitiendo procesar el bucle MQTT entre lecturas.
4. **¿Qué es el broker?** HiveMQ público distribuye mensajes entre clientes
   según tópicos. Panel y MCP no envían comandos directamente al ESP32.
5. **¿Por qué el prefijo?** `sis234/2026-2/grupo6` reduce colisiones entre
   grupos sobre el broker compartido; no constituye autenticación.
6. **¿Para qué sirven retain y LWT?** Los estados retenidos permiten a un
   suscriptor nuevo ver el último valor. LWT permite al broker publicar
   `en_linea:false` si la sesión del ESP32 se pierde de forma inesperada.
7. **¿Qué QoS se usa?** El MCP publica comandos con QoS 1 y el celular con
   QoS 0. ESP32 solicita QoS 1 en su suscripción; PubSubClient publica sus
   propios mensajes con QoS 0. QoS 1 no implica ejecución física garantizada:
   para eso se usa `ack_id`.
8. **¿Cómo funciona `ack_id`?** MCP genera un UUID y envía comando; el ESP32
   valida el JSON, aplica los LEDs y publica estado con el mismo ID. El MCP
   espera la confirmación correlacionada. Si vence 3 s, informa «enviado, no
   confirmado» y no presupone el estado del LED.
9. **¿Qué pasa con un JSON inválido?** `ParserComandoLeds` rechaza comandos
   corruptos, tipos distintos a booleanos o colores desconocidos.
10. **¿Cómo se recupera una caída?** WiFi y MQTT reintentan con espera creciente
    (backoff), y el bridge MCP invalida datos al desconectarse del broker o
    recibir estado offline. Los valores retenidos de un arranque válido ya
    no se borran al recibir online.
11. **¿Qué es MCP y `stdio`?** Claude invoca herramientas del servidor local.
    El protocolo pasa por stdin/stdout; los logs van a stderr para no romperlo.
12. **¿Por qué `cm:null`?** Una lectura sin eco, antigua o no disponible no
    debe reemplazarse con un número inventado.
13. **¿Qué mide la latencia?** Los CSV miden el tiempo hasta el ACK MQTT,
    no directamente el cambio luminoso. La tanda previa del script tuvo 6/30
    comandos sobre 1 s; la tanda del panel observada tuvo 0/10.
14. **¿Por qué 1000 ms?** El grupo decidió mantener una lectura por segundo,
    que es la cadencia comprobada previamente. La auditoría sugiere 2 Hz,
    pero el grupo no adoptó esa referencia; explicar esa limitación si se
    pregunta. `WiFi.setSleep(false)` busca reducir latencia de recepción
    de comandos, con mayor consumo energético.
15. **¿Y el servomotor del ejemplo?** Este objeto inteligente controla tres
    LEDs; no tiene servo. Es una limitación honesta del prototipo.

## Recordatorios de entrega

- Mostrar pruebas, no afirmar mejoras de latencia hasta re-medidas.
- Comprobar `git shortlog -sne --all`: los tres integrantes deben participar.
- Revisar que no existan contraseñas en archivos versionados ni en el historial.
- Llevar la versión de código y el firmware físico sincronizados.
