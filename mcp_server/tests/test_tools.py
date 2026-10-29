"""Pruebas de integracion ligera del contrato de salida de obtener_distancia."""

import pytest

from servidor_mcp.bridge import ConfiguracionMqtt, PuenteMqtt
from servidor_mcp.service import ServicioObjetoInteligente


class ClienteFalso:
    def reconnect_delay_set(self, min_delay: int, max_delay: int) -> None:
        pass


def test_bridge_indica_error_esperado_para_null() -> None:
    """El bridge sigue rechazando la lectura sin inventar centimetros."""
    from servidor_mcp.bridge import ErrorObjetoInteligente

    puente = PuenteMqtt(ConfiguracionMqtt(), cliente=ClienteFalso())
    puente._dispositivo_en_linea = True
    puente._actualizar_distancia({"cm": None, "valida": False})
    with pytest.raises(ErrorObjetoInteligente, match="No existe una medicion valida"):
        ServicioObjetoInteligente(puente).obtener_distancia()


def test_mcp_convierte_error_de_null_en_respuesta_estructurada(monkeypatch) -> None:
    """No debe escapar una excepcion al ejecutar la herramienta MCP."""
    from servidor_mcp import server

    def sin_lectura():
        from servidor_mcp.bridge import ErrorObjetoInteligente
        raise ErrorObjetoInteligente("No existe una medicion valida disponible.")

    monkeypatch.setattr(server.servicio, "obtener_distancia", sin_lectura)
    # El SDK aplica su decorador a la funcion, por ello comprobamos la funcion
    # registrada en el modulo solo si conserva el callable Python directo.
    if not callable(server.obtener_distancia):
        pytest.skip("El SDK MCP encapsulo la funcion; probar mediante cliente MCP")
    resultado = server.obtener_distancia()
    assert resultado["cm"] is None
    assert resultado["valida"] is False
    assert "No existe una medicion valida" in resultado["mensaje"]
