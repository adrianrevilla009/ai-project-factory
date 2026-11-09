---
name: contract-testing-pact
description: "Usar al implantar contract testing consumer-driven con Pact (JVM): contratos, verificación del proveedor, broker y can-i-deploy."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Contract testing con Pact

## Cuándo aplicar y cuándo no
- Aplica a integraciones HTTP (y mensajería) entre servicios que se despliegan de forma independiente y tienen consumidores identificables.
- No aplica a APIs públicas con consumidores desconocidos (usar OpenAPI + `backward-compatibility-rules`) ni sustituye a tests end-to-end puntuales. Visión general de estrategia: skill `contract-testing` (bloque 08).

## Reglas
- **MUST** que el consumidor genere el pact desde un test que ejerce su cliente real contra un mock, describiendo solo lo que realmente usa.
- **MUST** que el proveedor verifique todos los pacts de sus consumidores en CI con estados (`@State`) deterministas.
- **MUST** publicar pacts y resultados en un Pact Broker (OSS) etiquetados con commit y rama, y usar `can-i-deploy` como puerta antes de promover.
- **MUST NOT** usar matchers por valor exacto donde basta el tipo (`like`, regex); **MUST NOT** incluir datos reales ni PII.
- **MUST NOT** probar lógica de negocio del proveedor desde el pact; solo forma y semántica del contrato.
- **SHOULD** usar `pending pacts` y `work in progress pacts` para que un contrato nuevo no rompa la build del proveedor.
- **SHOULD** pact de mensajes para eventos, junto al esquema (`schema-registry-and-evolution`).
- **SHOULD** el proveedor ejecute la verificación con el servicio real levantado en el slice de test (Spring Boot test), con dependencias externas simuladas.

## Por qué
Los tests de integración en entorno compartido son lentos y frágiles. El contrato dirigido por el consumidor detecta roturas antes de desplegar y documenta qué campos se usan realmente, lo que permite evolucionar el proveedor con seguridad. Coordenadas y anotaciones de Pact JVM deben contrastarse con su documentación.

## Ejemplos
### Mal
```java
// test de consumidor que exige valores exactos y toda la respuesta
.body("{\"id\":42,\"name\":\"Juan Perez\",\"email\":\"juan@real-client.com\",\"internalFlag\":true}")
```
### Bien (consumidor)
```java
@Pact(consumer = "billing-service", provider = "customer-service")
V4Pact customerPact(PactDslWithProvider b) {
    return b.given("customer 42 exists")
        .uponReceiving("get customer")
        .path("/customers/42").method("GET")
        .willRespondWith().status(200)
        .body(newJsonBody(o -> {
            o.integerType("id", 42);
            o.stringType("name", "example name");
        }).build())
        .toPact(V4Pact.class);
}
```
### Bien (proveedor)
```java
@Provider("customer-service")
@PactBroker
class CustomerContractVerificationTest {
    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verify(PactVerificationContext ctx) { ctx.verifyInteraction(); }

    @State("customer 42 exists")
    void customerExists() { repo.save(new Customer(42L, "example name")); }
}
```
```text
pact-broker can-i-deploy --pacticipant billing-service --version $GIT_SHA --to-environment staging
```

## Checklist de revisión
- [ ] El pact lo genera el cliente real; solo campos usados; matchers por tipo.
- [ ] El proveedor verifica en CI con estados deterministas.
- [ ] Broker con versiones/ramas; `can-i-deploy` bloquea promoción.
- [ ] Sin PII ni datos reales en pacts.
- [ ] Pending/WIP pacts activados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Verificación del proveedor y `can-i-deploy` en pipeline | 1 | pipeline del proyecto generado (pendiente) |
| Revisión de pacts nuevos | 3 | agente `code-reviewer` |

> Estado: sin artefacto en este repositorio todavía (pendiente). La fábrica no despliega ni opera un broker.

## Relacionados, fuentes y mantenimiento
- Relacionados: `contract-testing`, `openapi-contract-first`, `backward-compatibility-rules`, `api-testing`.
- Fuentes: documentación de Pact (docs.pact.io: consumer tests, provider verification, can-i-deploy, pending pacts), consultada 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
