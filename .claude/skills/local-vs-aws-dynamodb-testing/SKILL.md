---
name: local-vs-aws-dynamodb-testing
description: "Usar al probar código DynamoDB con DynamoDB Local o Testcontainers: qué cubre el emulador, qué NO reproduce y cómo declarar ese límite."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Testing local vs AWS en DynamoDB

## Cuándo aplicar y cuándo no
- Aplica a tests de integración de repositorios DynamoDB (`dynamodb-data-modeling`, `dynamodb-event-store`) y a su configuración de perfiles.
- No aplica a Postgres (ver `db-testing`). La fábrica nunca despliega ni prueba en AWS real (ADR-0004).

## Reglas
- **MUST** probar contra DynamoDB Local (jar o imagen Docker oficial) en perfil `test`/`local`, con endpoint tomado de configuración y no fijo en código de producción.
- **MUST** declarar en el README del proyecto generado los límites del emulador y marcar el resultado como "preparado para AWS, no verificado en real".
- **MUST** tener en cuenta estas diferencias documentadas por AWS: throughput aprovisionado ignorado (no hay throttling), `Scan` paralelo no soportado (`Segment`/`TotalSegments` ignorados), lecturas casi siempre parecen fuertes, no se lanzan `TransactionConflictException`, límite de 1 MB en consultas sobre índices calculado distinto, nombres de tabla sin distinción de mayúsculas, sin PITR, sin tags, sin soporte de vector indexes.
- **MUST** simular con un doble (mock/stub del cliente) los errores que el emulador no genera: `TransactionConflictException`, `ProvisionedThroughputExceededException`, `ThrottlingException`; verificar reintentos y backoff.
- **MUST NOT** deducir capacidad, costes ni latencias de los tests locales.
- **MUST NOT** usar credenciales reales; usar literales `example`/`changeme` (el emulador exige clave y región, solo alfanuméricas en la clave).
- **SHOULD** crear tablas por código o script en `@BeforeAll`, con el mismo esquema/índices que el IaC (ver Terraform del proyecto) y una comprobación de que coinciden.
- **SHOULD** no depender de la forma de los shards de Streams: AWS indica que pueden diferir localmente.

## Por qué
El emulador acelera el desarrollo y valida modelo de acceso y condiciones, pero omite justo lo que más falla en producción: throttling, conflictos transaccionales, particionado y consistencia. Declararlo evita falsa confianza.

## Ejemplos
### Mal
```java
// Endpoint local fijo en codigo de produccion
DynamoDbClient client = DynamoDbClient.builder()
    .endpointOverride(URI.create("http://localhost:8000")).build();
```
### Bien
```java
@Bean
DynamoDbClient dynamoDbClient(@Value("${app.dynamodb.endpoint:}") String endpoint) {
    var b = DynamoDbClient.builder().region(Region.EU_WEST_1);
    if (!endpoint.isBlank()) {
        b.endpointOverride(URI.create(endpoint))
         .credentialsProvider(StaticCredentialsProvider.create(
             AwsBasicCredentials.create("examplekey", "examplesecret"))); // solo perfil local/test
    }
    return b.build();
}
```
```text
docker run -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -inMemory -sharedDb
```
El nombre de la imagen y los flags `-inMemory` y `-sharedDb` figuran en la guía de AWS; confirmar el tag de imagen vigente. Ejemplo en bloque de texto, no ejecutado.

## Checklist de revisión
- [ ] Endpoint y credenciales de emulador solo en perfil local/test.
- [ ] README lista los límites del emulador.
- [ ] Errores de throttling/conflicto cubiertos con dobles.
- [ ] Esquema de test == esquema del IaC.
- [ ] Ninguna afirmación de rendimiento o coste basada en el emulador.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: `endpointOverride` a localhost en `src/main` | 1 | `policies/semgrep/dynamodb-local-endpoint-in-main.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Revisión de cobertura de errores no emulados | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dynamodb-data-modeling`, `dynamodb-event-store`, `global-tables-and-write-region-rules`, `db-testing`, `outbox-and-cdc`.
- Fuentes (verificadas 2026-11-07): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html · https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.UsageNotes.html
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
