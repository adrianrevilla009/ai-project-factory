---
name: wiremock-and-stubbing
description: "Usar al probar clientes HTTP contra APIs de terceros o internas simuladas con WireMock: stubs, verificación, fallos y latencia."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# WireMock y stubbing HTTP

## Cuándo aplicar y cuándo no
- Aplica a probar adaptadores HTTP salientes (RestClient, WebClient, Feign): respuestas, errores, timeouts, reintentos.
- No aplica a verificar el contrato real entre servicios propios (usar `contract-testing`): un stub solo prueba lo que tú supones.

## Reglas
- **MUST** stubear por método, ruta y, cuando importe, cabeceras y cuerpo; evitar `anyUrl()` genérico.
- **MUST** probar caminos de fallo: 4xx, 5xx, cuerpo malformado, timeout, conexión cortada (`Fault`), respuesta lenta.
- **MUST** verificar las peticiones enviadas (`verify`) cuando la salida es el comportamiento (cabecera de auth, idempotency key, cuerpo).
- **MUST** usar puerto dinámico y enlazar la URL base por propiedad; nunca puerto fijo.
- **MUST** resetear stubs entre tests (extensión JUnit 5 de WireMock o `resetAll`).
- **SHOULD** derivar los stubs de la especificación OpenAPI/contrato cuando exista, para que no diverjan.
- **SHOULD** usar escenarios con estado (`scenarios`) para probar reintentos (primero 503, luego 200).
- **MUST NOT** hacer que los tests unitarios dependan de WireMock (es de integración).
- **MUST NOT** guardar en los stubs datos reales de producción ni tokens reales.

## Por qué
Los tests contra terceros reales son lentos, inestables y a veces con coste. Un stub bien definido es determinista y permite provocar fallos imposibles de forzar con el servicio real. Su límite: si el tercero cambia, el stub sigue en verde; por eso se complementa con contract tests o una verificación periódica.

## Ejemplos
### Mal
```java
stubFor(any(anyUrl()).willReturn(ok()));           // acepta todo
// el test no comprueba qué se envió ni qué pasa si falla
```
### Bien
```java
@RegisterExtension
static WireMockExtension payments = WireMockExtension.newInstance()
    .options(wireMockConfig().dynamicPort()).build();

@DynamicPropertySource
static void props(DynamicPropertyRegistry r) {
    r.add("payments.base-url", payments::baseUrl);
}

@Test
void retriesOnce_whenGatewayReturns503() {
    payments.stubFor(post("/v1/charges").inScenario("retry").whenScenarioStateIs(STARTED)
        .willReturn(serviceUnavailable()).willSetStateTo("recovered"));
    payments.stubFor(post("/v1/charges").inScenario("retry").whenScenarioStateIs("recovered")
        .willReturn(okJson("{\"id\":\"ch_example\"}")));

    var result = client.charge(new ChargeRequest("order-1", 1500));

    assertThat(result.id()).isEqualTo("ch_example");
    payments.verify(2, postRequestedFor(urlEqualTo("/v1/charges"))
        .withHeader("Idempotency-Key", matching(".+")));
}
```
Coordenadas y versión de WireMock: comprobar al fijar la versión.

## Criterios de decisión y trampas
### Cómo decidir
- WireMock para clientes HTTP de terceros; para servicios internos con contrato, genera los stubs desde el contrato en vez de escribirlos a mano.
- El modo de grabación sirve para arrancar; revisa y limpia lo grabado.
### Trampas frecuentes
- Stubs permisivos (`anyUrl`) que aceptan peticiones incorrectas.
- Probar solo el camino feliz.
- Puertos fijos y estado compartido entre tests.
- Stubs que divergen del proveedor real porque nadie los contrasta con un contrato.
### Evidencia
- Hay tests de timeout, 5xx y cuerpo malformado, y `verify` sobre la petición enviada.

## Checklist de revisión
- [ ] Stubs específicos, sin catch-all.
- [ ] Cubiertos error, timeout y respuesta lenta.
- [ ] Peticiones verificadas donde importa.
- [ ] Puerto dinámico y reset entre tests.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: cliente HTTP sin timeout | 1 | `policies/semgrep/spring-http-client-without-timeout.yaml` |
| Revisión de cobertura de caminos de fallo | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `http-clients-and-timeouts`, `resilience`, `contract-testing`, `resilience-testing`.
- Fuentes: documentación oficial de WireMock (https://wiremock.org/docs/) — comprobar versión y API de la extensión.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
