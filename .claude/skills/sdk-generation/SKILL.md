---
name: sdk-generation
description: "Usar al generar SDKs/clientes de API desde OpenAPI (Java, TypeScript): herramienta, versionado, módulo separado y qué no editar a mano."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Generación de SDKs

## Cuándo aplicar y cuándo no
- Aplica cuando un servicio publica un contrato OpenAPI y otros equipos o el frontend React consumen clientes generados.
- No aplica a APIs sin contrato formal (primero `openapi-contract-first`) ni a clientes triviales de un solo endpoint.

## Reglas
- **MUST** generar el SDK desde el OpenAPI versionado del proveedor; la especificación es la fuente de verdad (ver `openapi-contract-first`).
- **MUST** fijar la versión exacta del generador (p. ej. OpenAPI Generator, licencia Apache-2.0) y su configuración en el repo; **MUST NOT** usar versiones flotantes.
- **MUST NOT** editar a mano el código generado; las personalizaciones van en plantillas, `.openapi-generator-ignore` o envoltorios propios.
- **MUST** publicar el SDK como artefacto separado (módulo Maven / paquete npm) con SemVer alineado al contrato: cambio incompatible = major.
- **MUST** regenerar en CI y fallar si el código generado versionado difiere de la salida (no hay deriva); preferible no versionar el código generado y construirlo en build.
- **MUST** que el generador Java no introduzca Lombok (D27): comprobar opciones y dependencias resultantes.
- **MUST** timeouts, reintentos solo idempotentes y propagación de `traceparent` configurables en el cliente.
- **SHOULD** mantener los tests de contrato (`contract-testing-pact`) contra el SDK generado.
- **SHOULD** registrar credenciales fuera del SDK; el SDK recibe un proveedor de token, no secretos embebidos.
- **SHOULD** documentar en el README del SDK versión del contrato, compatibilidad y política de deprecación.

## Por qué
Un cliente escrito a mano diverge del contrato y rompe en ejecución. Un generador sin versión fija produce diffs inexplicables entre builds. Editar el código generado se pierde en la siguiente regeneración. Las opciones del generador varían por versión: contrastar con su documentación.

## Ejemplos
### Mal
```xml
<plugin>
  <groupId>org.openapitools</groupId>
  <artifactId>openapi-generator-maven-plugin</artifactId>
  <version>LATEST</version>
</plugin>
```
```java
// edición manual en target/generated-sources/.../ApiClient.java -> se pierde al regenerar
```
### Bien
```xml
<plugin>
  <groupId>org.openapitools</groupId>
  <artifactId>openapi-generator-maven-plugin</artifactId>
  <version><!-- comprobar fijar versión exacta vigente --></version>
  <executions><execution>
    <goals><goal>generate</goal></goals>
    <configuration>
      <inputSpec>${project.basedir}/../api/openapi.yaml</inputSpec>
      <generatorName>java</generatorName>
      <library>native</library>
      <apiPackage>com.example.customers.client.api</apiPackage>
      <modelPackage>com.example.customers.client.model</modelPackage>
    </configuration>
  </execution></executions>
</plugin>
```
```java
// envoltorio propio: política de resiliencia y mapeo de errores fuera del código generado
class CustomerClient {
    private final CustomersApi api;
    Customer get(String id) { return mapper.toDomain(api.getCustomer(id)); }
}
```

## Checklist de revisión
- [ ] SDK generado desde el OpenAPI del repo; generador con versión fija.
- [ ] Nada editado a mano en lo generado; personalización por plantillas/envoltorios.
- [ ] SemVer del SDK alineado al contrato; publicado como artefacto aparte.
- [ ] CI detecta deriva; sin Lombok; sin secretos embebidos.
- [ ] Timeouts y trazado configurables.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Maven Enforcer / revisión: versión del plugin no flotante | 1 | `policies/opa-conftest/` o enforcer del parent (pendiente) |
| Job CI de deriva del código generado | 1 | pipeline del proyecto generado (pendiente) |
| Revisión del módulo SDK | 3 | agente `code-reviewer` |

> Estado: artefactos pendientes; revisión humana mientras tanto.

## Relacionados, fuentes y mantenimiento
- Relacionados: `openapi-contract-first`, `api-versioning-deprecation`, `versioning-semver-snapshots`, `contract-testing-pact`.
- Fuentes: documentación de OpenAPI Generator (plugin Maven, generador `java`, `.openapi-generator-ignore`) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
