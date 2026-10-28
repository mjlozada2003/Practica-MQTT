# Guía de Demo para nivel 4

## Preparación

- Ejecutar previamente el ensayo estable de 15 minutos.
- Tener cinta métrica, teléfono cargado y Claude Desktop ya configurado.
- Confirmar acceso a `broker.hivemq.com:1883` antes de entrar al aula.
- Sujetar cables, usar resistencias de 220 Ω y divisor 1 kΩ/2 kΩ en Echo.

## Secuencia

1. Mostrar que existe un solo ESP32 y describir el circuito.
2. Explicar que móvil, MCP y ESP32 se conectan únicamente al broker.
3. Colocar un objeto a una distancia conocida y mostrar Gauge y Line Graph.
4. Activar y desactivar cada LED desde los tres switches.
5. Mostrar los indicadores de estado confirmado.
6. Preguntar a Claude: «¿A qué distancia está el objeto ahora?».
7. Pedir: «Enciende el rojo y apaga los demás».
8. Probar una combinación de dos LEDs y mostrar `ack_id` y latencia.
9. Cortar la conectividad del ESP32 y mostrar `en_linea=false`.
10. Restaurar la red sin reiniciar la placa y repetir una orden.
11. Presentar las métricas medidas de exactitud, frecuencia, latencia y estabilidad.

La Demo solo termina cuando se ha evidenciado la reconexión: es una condición
explícita del nivel 4.
