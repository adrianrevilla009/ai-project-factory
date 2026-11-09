---
name: openapi-contract-first
description: "Usar al crear o cambiar una API HTTP: el contrato OpenAPI se escribe y revisa antes que el código y se valida en CI."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# OpenAPI contract-first

## Cuándo aplicar y cuándo no
- Aplica a toda API REST nueva o con cambios de superficie (rutas, esquemas, errores).
- No aplica a prototipos descartables ni a endpoints internos de operación (actuator).

## Reglas
- **MUST** versionar el contrato en el repo del servicio: `src/main/resources/openapi/<service>.yaml` (OpenAPI 3.x), revisado en el mismo PR que el código.
- **MUST** escribir el contrato antes de la implementación y generar interfaces/DTOs desde él (p. ej. `openapi-generator-maven-plugin` con `interfaceOnly`), no al revés.
- **MUST** definir `operationId` únicos, `summary`, respuestas de error (`application/problem+json`) y `examples` en cada operación.
- **MUST** reutilizar esquemas con `$ref` en `components`; **MUST NOT** duplicar esquemas inline.
- **MUST** pasar un linter (Spectral) y un chequeo de ruptura (`backward-compatibility-rules`) en CI.
- **SHOULD** declarar `security` por operación y `servers` sin URLs reales de producción.
- **MUST NOT** generar el contrato desde anotaciones como fuente de verdad (springdoc) salvo para detectar deriva: el contrato escrito manda.
- **SHOULD** validar en test que la respuesta real cumple el contrato (validador de request/response contra el YAML).

## Por qué
Con contract-first, front-end, QA y consumidores trabajan en paralelo con mocks, y los cambios rompientes se ven en el diff del YAML en lugar de descubrirse en producción. El código generado elimina la deriva entre doc e implementación.

## Ejemplos
### Mal
```java
// El contrato "sale" de las anotaciones; nadie lo revisa
@Operation(summary = "get")
@GetMapping("/getOrder")
public Object get(@RequestParam String id) { ... }
```
### Bien
```yaml
openapi: 3.0.3
info: { title: Orders API, version: 1.0.0 }
paths:
  /orders/{orderId}:
    get:
      operationId: getOrder
      summary: Obtiene un pedido
      parameters:
        - { name: orderId, in: path, required: true, schema: { type: string, format: uuid } }
      responses:
        "200": { description: OK, content: { application/json: { schema: { $ref: "#/components/schemas/Order" } } } }
        "404": { $ref: "#/components/responses/NotFound" }
```
```xml
<plugin>
  <groupId>org.openapitools</groupId>
  <artifactId>openapi-generator-maven-plugin</artifactId>
  <!-- version gestionada en el parent-pom -->
  <configuration>
    <inputSpec>${project.basedir}/src/main/resources/openapi/orders.yaml</inputSpec>
    <generatorName>spring</generatorName>
    <configOptions><interfaceOnly>true</interfaceOnly><useSpringBoot3>true</useSpringBoot3></configOptions>
  </configuration>
</plugin>
```

## Criterios de decisión y trampas
### Cómo decidir
- El contrato se escribe y se revisa antes del código y es la fuente de generación y de pruebas.
- Valida las respuestas reales contra el contrato en las pruebas.
### Trampas frecuentes
- Contrato generado a posteriori que describe lo que hay, no lo que debe haber.
- Código y contrato que divergen sin avisar.
- Ejemplos inexistentes o incorrectos.
- Esquemas con todo opcional.
- Cambios incompatibles sin revisión del contrato.
### Evidencia
- El contrato está en el repositorio, validado en CI y verificado contra el servicio.

## Checklist de revisión
- [ ] El YAML cambia en el mismo PR que el código.
- [ ] `operationId`, ejemplos y errores definidos.
- [ ] Sin esquemas duplicados; `$ref` a `components`.
- [ ] Lint y diff de compatibilidad en verde.
- [ ] Los controladores implementan la interfaz generada.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Spectral + diff de ruptura en CI del proyecto generado | 1 | pendiente: ruleset en `policies/` y pipeline del proyecto |
| Revisión de PR (contrato antes que código) | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rest-design-guidelines`, `backward-compatibility-rules`, `sdk-generation`, `contract-testing-pact`.
- Fuentes: OpenAPI Specification (spec.openapis.org), OpenAPI Generator, Spectral) en la documentación del generador (2026-11-07 no comprobado.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
