---
name: cdc-and-streaming
description: "Usar al alimentar la plataforma de datos desde BD transaccionales con CDC (Debezium/Kafka Connect) o streaming: slots, snapshots, orden, esquemas y reprocesado."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# CDC y streaming hacia la plataforma de datos

## Cuándo aplicar y cuándo no
- Aplica cuando el lago/warehouse necesita cambios de una BD operacional casi en tiempo real, o cuando se consumen eventos Kafka como fuente analítica.
- No aplica si una carga batch diaria basta (ver `batch-orchestration`) ni a eventos de dominio entre microservicios (ver `domain-events-in-spring`, `event-driven`).

## Reglas
- **MUST** leer cambios del log de la BD (WAL/binlog) con un conector CDC; **MUST NOT** hacer polling de `updated_at` si hay que capturar borrados.
- **MUST** definir la clave de partición Kafka = clave primaria de la fila, para preservar el orden por entidad.
- **MUST** tratar el consumo como at-least-once: el destino es idempotente (upsert por PK + versión/LSN) o deduplica.
- **MUST** monitorizar el lag del slot de replicación y fijar un límite de WAL retenido; un slot abandonado llena el disco de la BD operacional.
- **MUST** publicar el esquema (Avro/JSON Schema/Protobuf) en un registro con compatibilidad `BACKWARD` como mínimo.
- **MUST** tener un plan de re-snapshot y reprocesado documentado (retención de topics, topic de DLQ).
- **MUST NOT** escribir el mismo dato en dos stores desde la aplicación (4.5): CDC lee de una única fuente de verdad.
- **SHOULD** usar el patrón outbox cuando el evento deba ser semántico y no un espejo de tablas (ver `domain-events-in-spring`).
- **SHOULD** enmascarar o excluir columnas PII en el propio conector (`column.exclude.list`) antes de que lleguen al topic.

## Por qué
CDC por log da borrados, orden y baja carga en origen, pero acopla el analítico al modelo físico y deja un slot que retiene WAL mientras el consumidor no avance. La entrega es at-least-once, así que la idempotencia es del destino. Debezium con PostgreSQL soporta `pgoutput` (estándar desde PostgreSQL 10) y `decoderbufs`. Fuente: https://debezium.io/documentation/reference/stable/connectors/postgresql.html (consultado 2026-11-07). El nombre exacto de propiedades de heartbeat y límites de WAL: TODO-VERIFY en la versión usada.

## Ejemplos
### Mal
```json
{ "name": "orders-cdc",
  "config": { "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.password": "changeme-example", "table.include.list": "public.*" } }
```
Todas las tablas, PII incluida, sin control de esquema ni de slot.
### Bien
```json
{ "name": "orders-cdc",
  "config": { "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "plugin.name": "pgoutput",
    "database.password": "${file:/secrets/db.properties:password}",
    "table.include.list": "public.orders,public.order_lines",
    "column.exclude.list": "public.orders.customer_email",
    "slot.name": "orders_cdc_slot" } }
```
Lista explícita, PII excluida, secreto por referencia. Verificar nombres de propiedades contra la versión (TODO-VERIFY).
### Consumidor idempotente
```sql
insert into lake.orders (id, status, source_lsn)
values (:id, :status, :lsn)
on conflict (id) do update set status = excluded.status, source_lsn = excluded.source_lsn
where lake.orders.source_lsn < excluded.source_lsn;
```

## Checklist de revisión
- [ ] Tablas y columnas incluidas son una lista explícita; PII excluida o enmascarada.
- [ ] Clave del topic = PK; compatibilidad de esquema configurada.
- [ ] Destino idempotente; existe DLQ y runbook de re-snapshot.
- [ ] Alerta por lag de slot y WAL retenido.
- [ ] Sin doble escritura desde la aplicación.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: auto-commit de offsets activado | 1 | `policies/semgrep/kafka-auto-commit.yaml` |
| Alerta de lag/WAL del slot | 2 | pendiente (alertas del proyecto generado) |
| Revisión de la lista de tablas/columnas del conector | 3 | revisión humana (data owner) |

En local se reproduce con Postgres + Kafka + Kafka Connect en contenedores. No se reproduce MSK/MSK Connect ni su operación gestionada; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `kafka-producers-consumers`, `asyncapi-event-contracts`, `data-contracts-and-lineage`, `gdpr-in-the-lake`.
- Fuentes: documentación Debezium (URL arriba, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
