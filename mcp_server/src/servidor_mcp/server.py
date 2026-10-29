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

from .bridge import ConfiguracionMqtt, ErrorObjetoInteligente, PuenteMqtt
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


def _consultar_distancia_segura() -> dict[str, Any]:
    """Return a structured no-reading result for expected device conditions.

    Keep programming errors visible: only ErrorObjetoInteligente is translated.
    An invalid/null, stale, or unavailable reading is never replaced by an old
    cached number or an invented distance.
    """
    try:
        return servicio.obtener_distancia()
    except ErrorObjetoInteligente as error:
        logger.info("Medicion no disponible para Claude: %s", error)
        return {"cm": None, "valida": False, "mensaje": str(error)}


@mcp.tool()
def obtener_distancia() -> dict[str, Any]:
    """Consulta la distancia reciente del HC-SR04 (cm) mediante MQTT.

    Si el sensor no tiene eco, la lectura es invalida, esta desactualizada o
    el dispositivo esta desconectado, devuelve cm=null, valida=false y una
    explicacion en mensaje. No inventes una distancia en esos casos.
    """
    return _consultar_distancia_segura()


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
