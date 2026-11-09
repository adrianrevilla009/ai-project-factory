---
name: dynamodb-data-modeling
description: "Usar al diseñar tablas, claves e índices de DynamoDB a partir de patrones de acceso (single-table vs multi-table, GSI, hot partitions)."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Modelado de datos en DynamoDB

## Cuándo aplicar y cuándo no
- Aplica a cualquier tabla DynamoDB nueva o cambio de claves/índices (event store incluido).
- No aplica a modelado relacional (ver `db-design-conventions`) ni a elegir si usar DynamoDB (ver `datastore-selection-guide`).

## Reglas
- **MUST** listar primero los patrones de acceso (consulta, frecuencia, consistencia, orden) y derivar de ellos claves e índices; no modelar entidades primero.
- **MUST** resolver cada patrón con `GetItem`/`Query`; **MUST NOT** usar `Scan` en rutas de negocio.
- **MUST** elegir una partition key de alta cardinalidad y reparto uniforme; **MUST NOT** usar claves de baja cardinalidad (`status`, fecha del día) como partition key.
- **SHOULD** usar prefijos tipados en las claves (`ORDER#123`, `CUSTOMER#9`) y un sort key que permita `begins_with` y rangos.
- **SHOULD** empezar con una tabla por bounded context (single-table por agregado relacionado solo si el equipo lo domina); no mezclar contextos en una tabla por "ahorrar".
- **MUST** tratar los GSI como eventualmente consistentes y como coste de escritura adicional; límite por defecto de 20 GSI por tabla (ver fuente).
- **MUST** paginar con `LastEvaluatedKey` y limitar el tamaño de respuesta; **MUST NOT** asumir joins ni agregaciones.
- **MUST** usar escrituras condicionales (`conditionExpression`) para unicidad y concurrencia optimista.
- **MUST** respetar el tamaño máximo de ítem (400 KB); los blobs van a S3 con referencia.

## Por qué
DynamoDB escala por diseño de claves, no por consultas flexibles: un patrón de acceso no previsto implica un GSI nuevo o un backfill. Un `Scan` cuesta en proporción al tamaño de la tabla, y una partition key caliente limita el rendimiento aunque haya capacidad global.

## Ejemplos
### Mal
```java
// Partition key = status: casi todo el tráfico cae en "OPEN"
dynamo.scan(ScanRequest.builder().tableName("orders")
    .filterExpression("customer_id = :c").build());
```
### Bien
```java
// Patrón: "pedidos de un cliente, más recientes primero"
// PK = CUSTOMER#<id>, SK = ORDER#<isoInstant>#<orderId>
QueryRequest q = QueryRequest.builder()
    .tableName("orders")
    .keyConditionExpression("pk = :pk AND begins_with(sk, :p)")
    .expressionAttributeValues(Map.of(
        ":pk", AttributeValue.fromS("CUSTOMER#" + customerId),
        ":p", AttributeValue.fromS("ORDER#")))
    .scanIndexForward(false)
    .limit(50)
    .build();
```

## Criterios de decisión y trampas
### Cómo decidir
- Modela desde los patrones de acceso: define primero las consultas y diseña claves e índices para servirlas; una tabla por servicio suele bastar.
- Elige modo bajo demanda o aprovisionado según la previsibilidad de la carga.
### Trampas frecuentes
- Diseñar como si fuera relacional.
- Claves que concentran el tráfico en una partición.
- Escaneos completos como patrón de lectura.
- Índices secundarios por cada consulta imaginable.
- Ítems enormes en vez de referencias a almacenamiento de objetos.
### Evidencia
- Cada patrón de acceso tiene su consulta, su clave y una prueba con datos realistas.

## Checklist de revisión
- [ ] Hay tabla de patrones de acceso en el ADR o README del módulo.
- [ ] Ninguna ruta de negocio usa `Scan`.
- [ ] Partition keys con cardinalidad alta; revisado el riesgo de hot partition.
- [ ] Cada GSI justificado por un patrón concreto.
- [ ] Unicidad/versión con `conditionExpression`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: uso de `scan` (aviso) | 1 | `policies/semgrep/dynamodb-scan-forbidden.yaml` |
| Revisión de patrones de acceso y claves | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dynamodb-event-store`, `global-tables-and-write-region-rules`, `local-vs-aws-dynamodb-testing`, `datastore-selection-guide`.
- Fuentes (consultadas 2026-11-07): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html (20 GSI por tabla por defecto; 5 LSI). El límite de 400 KB por ítem y el de ítems por transacción.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
