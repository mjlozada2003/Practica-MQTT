"""Punto de entrada MCP para Claude Desktop."""

from __future__ import annotations

import logging
import sys
from typing import Any

from dotenv import load_dotenv

try:
    from mcp.server import MCPServer
except ImportError:  # Compatibilidad con la disposicion del SDK 2.x.
    from mcp.server.mcpserver import MCPServer

from .bridge import ConfiguracionMqtt, PuenteMqtt
from .service import ServicioObjetoInteligente

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

load_dotenv()
puente = PuenteMqtt(ConfiguracionMqtt.desde_entorno())
servicio = ServicioObjetoInteligente(puente)
mcp = MCPServer("objeto-inteligente-grupo6")


@mcp.tool()
def obtener_distancia() -> dict[str, Any]:
    """Obtiene la distancia actual medida por el HC-SR04.

    Devuelve centimetros, validez, disponibilidad del ESP32 y antiguedad de la
    lectura. Nunca inventa una medicion si el objeto esta desconectado.
    """
    return servicio.obtener_distancia()


@mcp.tool()
def obtener_estado_leds() -> dict[str, Any]:
    """Obtiene el estado fisico confirmado de los LEDs rojo, amarillo y verde."""
    return servicio.obtener_estado_leds()


@mcp.tool()
def controlar_leds(
    rojo: bool | None = None,
    amarillo: bool | None = None,
    verde: bool | None = None,
) -> dict[str, Any]:
    """Enciende o apaga uno o varios LEDs y espera confirmacion del ESP32.

    Solo se modifican los colores indicados; los parametros omitidos conservan
    su estado. Para apagar todos, enviar false en los tres parametros.
    """
    return servicio.controlar_leds(rojo, amarillo, verde)


def main() -> None:
    puente.iniciar()
    try:
        logger.info("Iniciando servidor MCP por stdio")
        mcp.run(transport="stdio")
    finally:
        puente.detener()
        logger.info("Servidor MCP detenido")


if __name__ == "__main__":
    main()
