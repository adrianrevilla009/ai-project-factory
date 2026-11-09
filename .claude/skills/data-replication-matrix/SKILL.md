---
name: data-replication-matrix
description: "Usar al decidir cómo se replica cada almacén entre eu-west-1 y eu-central-1 (Aurora, DynamoDB, MSK, S3, caché, secretos) y qué RPO real ofrece cada uno."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Matriz de replicación de datos

## Cuándo aplicar y cuándo no
- Aplica al diseñar tier 0-2 con datos persistentes y al añadir un nuevo almacén.
- No aplica a datos reconstruibles (caché, proyecciones) salvo para decidir si se reconstruyen.
- Diseño: preparado para AWS, no verificado en real. En local **no se reproduce**: failover global de Aurora, Global Tables fiables, replicación MSK entre regiones, Object Lock completo, claves multi-región.

## Reglas
- **MUST** rellenar esta matriz por servicio y revisarla con negocio:

| Almacén | Mecanismo | RPO típico | Nota |
|---|---|---|---|
| Postgres | Aurora Global Database | segundos (asíncrona) | secundaria solo lectura hasta promover |
| Event store | DynamoDB Global Tables | segundos (MREC) | **región de escritura por agregado** |
| Kafka | MSK + replicación entre regiones | minutos | traducción de offsets al conmutar |
| Objetos | S3 CRR + versionado + Object Lock | minutos | RTC si se exige SLA |
| Caché | reconstruir o Global Datastore | n/a | preferir reconstruir |
| Secretos/claves | Vault por región + KMS multi-región | n/a | Transit **no** se comparte |
| Imágenes | ECR replicado | minutos | runtime no depende de Harbor |

- **MUST** en event sourcing con Global Tables fijar **una región de escritura por agregado/tenant**. En modo MREC los conflictos se resuelven por "last writer wins" y las condiciones evalúan contra la versión local, así que el control de concurrencia por versión solo protege dentro de una región.
- **MUST NOT** escribir el mismo agregado en ambas regiones a la vez en MREC.
- **SHOULD** valorar MRSC (consistencia fuerte multi-región, RPO cero) solo si el caso lo exige: exactamente 3 regiones (o 2 + testigo), sin TTL ni transacciones, mayor latencia de escritura.
- **MUST NOT** hacer doble escritura Postgres + NoSQL para "replicar" (4.5): cada agregado tiene una única fuente de verdad.
- **MUST** monitorizar el retraso (ReplicationLatency en MREC, AuroraGlobalDBRPOLag) y alertar frente al RPO del tier.
- **MUST** que los backups con Vault Lock cubran también corrupción lógica, que la replicación propaga.

## Por qué
La replicación asíncrona copia también los errores y los borrados. El tier fija el RPO, pero el RPO real lo da el lag medido. Dos regiones escribiendo el mismo agregado produce divergencia silenciosa.

## Ejemplos
### Mal
```java
// Cualquier región puede añadir eventos al mismo agregado
dynamo.putItem(r -> r.tableName("events")
    .item(eventItem(aggregateId, version, payload))
    .conditionExpression("attribute_not_exists(pk)")); // solo vale dentro de una región
```
### Bien
```java
// aggregate -> región de escritura, decidido por tenant y almacenado en config
Region owner = writeRegionResolver.ownerOf(aggregateId); // p. ej. eu-west-1
if (!owner.equals(currentRegion)) {
    throw new WrongWriteRegionException(aggregateId, owner); // enrutar a la región dueña
}
dynamo.putItem(r -> r.tableName("events")
    .item(eventItem(aggregateId, version, payload))
    .conditionExpression("attribute_not_exists(pk) AND attribute_not_exists(sk)"));
```

## Checklist de revisión
- [ ] Cada almacén aparece en la matriz con mecanismo y RPO medido.
- [ ] Región de escritura por agregado definida y enrutada.
- [ ] Sin doble escritura entre Postgres y NoSQL.
- [ ] Alertas de lag y backups inmutables independientes de la replicación.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de la matriz por el revisor de arquitectura | 3 | agente `code-reviewer` / revisión humana |
| Regla ArchUnit: escritura de eventos solo vía `WriteRegionGuard` | 1 | pendiente (`policies/archunit/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `global-tables-and-write-region-rules`, `multi-region-patterns`, `failover-and-failback-runbooks`, `backup-vault-immutability-and-restore-tests`.
- Fuentes: DynamoDB global tables, https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html (2026-11-07); Aurora Global Database, https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html (2026-11-07). MSK y S3.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
