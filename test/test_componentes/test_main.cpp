#include <unity.h>

#include "CalculoDistancia.h"
#include "ComandoLeds.h"
#include "EstadoLeds.h"

void test_conversion_distancia() {
    TEST_ASSERT_FLOAT_WITHIN(
        0.01F, 17.15F, CalculoDistancia::desdeDuracionMicrosegundos(1000));
}

void test_limites_distancia() {
    TEST_ASSERT_TRUE(CalculoDistancia::dentroDelRango(2.0F, 2.0F, 30.0F));
    TEST_ASSERT_TRUE(CalculoDistancia::dentroDelRango(30.0F, 2.0F, 30.0F));
    TEST_ASSERT_FALSE(CalculoDistancia::dentroDelRango(1.99F, 2.0F, 30.0F));
    TEST_ASSERT_FALSE(CalculoDistancia::dentroDelRango(30.01F, 2.0F, 30.0F));
}

void test_leds_independientes_y_campos_omitidos() {
    EstadoLeds estado;
    estado.aplicar(true, true, false, false, true, true);
    TEST_ASSERT_TRUE(estado.rojo);
    TEST_ASSERT_FALSE(estado.amarillo);
    TEST_ASSERT_TRUE(estado.verde);
    estado.aplicar(false, false, true, true, false, false);
    TEST_ASSERT_TRUE(estado.rojo);
    TEST_ASSERT_TRUE(estado.amarillo);
    TEST_ASSERT_TRUE(estado.verde);
}

void test_parser_acepta_comando_parcial_con_id() {
    const char json[] = "{\"id\":\"abc-123\",\"rojo\":true,\"verde\":false}";
    ComandoLeds comando;
    TEST_ASSERT_TRUE(ParserComandoLeds::interpretar(
        reinterpret_cast<const uint8_t*>(json), sizeof(json) - 1, comando));
    TEST_ASSERT_TRUE(comando.tieneId);
    TEST_ASSERT_EQUAL_STRING("abc-123", comando.id);
    TEST_ASSERT_TRUE(comando.cambiarRojo);
    TEST_ASSERT_FALSE(comando.cambiarAmarillo);
    TEST_ASSERT_TRUE(comando.cambiarVerde);
}

void test_parser_rechaza_esquemas_invalidos() {
    const char tipoInvalido[] = "{\"rojo\":\"si\"}";
    const char campoDesconocido[] = "{\"azul\":true}";
    const char sinLed[] = "{\"id\":\"abc\"}";
    ComandoLeds comando;
    TEST_ASSERT_FALSE(ParserComandoLeds::interpretar(
        reinterpret_cast<const uint8_t*>(tipoInvalido),
        sizeof(tipoInvalido) - 1, comando));
    TEST_ASSERT_FALSE(ParserComandoLeds::interpretar(
        reinterpret_cast<const uint8_t*>(campoDesconocido),
        sizeof(campoDesconocido) - 1, comando));
    TEST_ASSERT_FALSE(ParserComandoLeds::interpretar(
        reinterpret_cast<const uint8_t*>(sinLed), sizeof(sinLed) - 1, comando));
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_conversion_distancia);
    RUN_TEST(test_limites_distancia);
    RUN_TEST(test_leds_independientes_y_campos_omitidos);
    RUN_TEST(test_parser_acepta_comando_parcial_con_id);
    RUN_TEST(test_parser_rechaza_esquemas_invalidos);
    return UNITY_END();
}
