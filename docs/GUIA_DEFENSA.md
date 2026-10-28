# Guía de defensa individual

Cada integrante debe poder explicar, sin limitarse a su propio aporte:

- Flujo publicación/suscripción y función del broker.
- Tópicos, payloads, QoS, Retain, LWT y Client IDs únicos.
- Por qué telemetría usa QoS 0 y comandos se publican con QoS 1.
- Por qué los comandos no son retained y los estados sí.
- Circuito del HC-SR04, divisor de Echo y resistencias de LEDs.
- Medición ultrasónica, timeout y rango de 2–30 cm.
- Bucle no bloqueante, intervalo de 1 Hz y reconexión progresiva.
- Validación JSON y conservación de campos omitidos.
- Hilo MQTT de Python, `Condition`, UUID, `ack_id` y timeout de 900 ms.
- Configuración `stdio` de Claude Desktop y prohibición de logs en stdout.
- Cómo se midieron exactitud, latencia, frecuencia y estabilidad.
- Aporte propio verificable mediante commits de su cuenta.

Realizar dos rondas de preguntas aleatorias. Una persona muestra un archivo o
componente creado principalmente por otra y debe explicarlo con precisión.
