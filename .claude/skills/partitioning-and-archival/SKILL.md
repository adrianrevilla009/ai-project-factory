---
name: partitioning-and-archival
description: Usar al decidir particionado de tablas grandes en PostgreSQL o una estrategia de retención, archivado y purga de datos.
metadata:
  block: "03-persistence-sql"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Particionado y archivado

## Cuándo aplicar y cuándo no
- Aplica a tablas de crecimiento continuo (eventos, logs de negocio, movimientos) con una política de retención clara.
- No aplica a tablas que caben cómodamente en memoria/disco con índices correctos; particionar antes de tiempo añade complejidad.

## Reglas
- **MUST** justificar el particionado con un problema medido (purga costosa, mantenimiento, consultas siempre acotadas por rango) y registrarlo en un ADR.
- **MUST** elegir una clave de partición que aparezca en las consultas habituales (normalmente fecha) para que haya poda de particiones; verificarlo con `EXPLAIN`.
- **MUST** tener en cuenta que la clave primaria y los índices únicos de una tabla particionada deben incluir la clave de partición.
- **MUST** automatizar la creación de particiones futuras y la retirada de antiguas; una partición que falta rompe las inserciones.
- **MUST** definir retención por tipo de dato (negocio, legal, PII) con base en requisitos confirmados; plazos legales son borrador por confirmar con fuente oficial.
- **MUST NOT** purgar con `DELETE` masivo cuando la partición permite `DETACH`/`DROP`.
- **SHOULD** archivar antes de borrar (exportar a almacenamiento barato, formato abierto) cuando haya obligación de conservar; verificar que el archivo se puede restaurar y leer.
- **SHOULD** que las migraciones de particionado se hagan con expand/contract y copia por lotes (ver `schema-migrations`, `batching-and-bulk-ops`).
- **SHOULD** respetar supresión de datos personales también en los archivos (ver `data-privacy-in-db`).

## Por qué
El particionado no acelera por sí solo: ayuda cuando las consultas se acotan por la clave y cuando la retención se aplica por partición completa, que es casi instantánea frente a millones de `DELETE` (con bloat y vacuum). Mal elegido, multiplica planes, índices y casos límite.

## Ejemplos
### Mal
```sql
-- purga diaria que bloquea y genera bloat
DELETE FROM audit_event WHERE occurred_at < now() - interval '2 years';
```
### Bien
```sql
CREATE TABLE audit_event (
  id          uuid        NOT NULL,
  occurred_at timestamptz NOT NULL,
  payload     jsonb       NOT NULL,
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE audit_event_2026_11 PARTITION OF audit_event
  FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

-- retencion: exportar y retirar la particion antigua
ALTER TABLE audit_event DETACH PARTITION audit_event_2024_11;
-- tras verificar el archivo: DROP TABLE audit_event_2024_11;
```
El `DROP` va solo en migraciones/jobs revisados, nunca ejecutado desde un agente.

## Checklist de revisión
- [ ] ADR con el problema medido y la clave elegida.
- [ ] Las consultas habituales filtran por la clave (poda comprobada).
- [ ] Creación/retirada de particiones automatizada y monitorizada.
- [ ] Retención definida y archivado restaurable.
- [ ] PKs y únicos incluyen la clave de partición.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Alerta/test de existencia de particiones futuras | 1 | pendiente (proyecto generado) |
| Revisión humana de plazos de retención | 4 | PR + responsable de datos |

## Relacionados, fuentes y mantenimiento
- Relacionados: `indexing-and-query-plans`, `schema-migrations`, `data-privacy-in-db`, `auditing-soft-delete-history`.
- Fuentes: documentación de PostgreSQL (Table Partitioning).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
