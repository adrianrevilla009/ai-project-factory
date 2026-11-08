---
name: data-lake-and-lakehouse
description: "Usar al diseñar un data lake o lakehouse: zonas raw/curated, formatos de tabla abiertos (Iceberg/Delta/Parquet), particionado, compactación, catálogo y evolución de esquema."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Data lake y lakehouse

## Cuándo aplicar y cuándo no
- Aplica al almacenar datos analíticos en objeto (S3/MinIO) con formato de tabla abierto.
- No aplica a datos transaccionales (van a la BD operacional) ni a un warehouse gestionado sin lago (ver `warehouse-options`).

## Reglas
- **MUST** separar zonas por prefijo/bucket: `raw` (inmutable), `curated` (limpio, tipado), `consumption` (marts); permisos distintos por zona.
- **MUST** usar un formato de tabla abierto con transacciones (Apache Iceberg por defecto; Delta Lake como alternativa OSS) sobre Parquet, no ficheros sueltos CSV/JSON en curated.
- **MUST** particionar por una columna de baja cardinalidad y filtro frecuente (fecha); **MUST NOT** particionar por ID o timestamp con milisegundos.
- **MUST** planificar compactación de ficheros pequeños y expiración de snapshots; documentar la frecuencia.
- **MUST** registrar las tablas en un catálogo (REST, JDBC o Glue) y no depender de rutas hardcodeadas.
- **MUST** cifrar en reposo y bloquear acceso público a los buckets.
- **MUST NOT** permitir escrituras concurrentes de varios motores sin catálogo común que arbitre commits.
- **SHOULD** gestionar evolución de esquema con las operaciones del formato (añadir/renombrar columnas), no reescribiendo ficheros.
- **SHOULD** definir retención por zona (ver `access-control-masking-and-retention`).

## Por qué
Un lago sin formato de tabla es un "pantano": sin ACID, sin evolución de esquema ni borrados fiables (clave para RGPD, ver `gdpr-in-the-lake`). Iceberg documenta evolución de esquema, particionado oculto, branching/tagging y soporte de Spark, Flink, Trino, DuckDB y otros; catálogos REST, JDBC, Nessie y Glue. Fuente: https://iceberg.apache.org/docs/latest/ (consultado 2026-11-07). Detalles de ACID, time travel y comandos de mantenimiento: comprobar en la versión fijada.

## Ejemplos
### Mal
```text
s3://acme-lake/data/sales/2026-11-07-10-32-11-123/part-0001.csv   # partición por timestamp, CSV sin catálogo
bucket policy: Principal "*" (lectura pública)
```
### Bien
```sql
-- Spark SQL sobre catálogo Iceberg (sintaxis comprobar por versión)
CREATE TABLE lake.curated.sales (
  sale_id bigint, customer_id bigint, amount decimal(12,2), sold_at timestamp)
USING iceberg
PARTITIONED BY (days(sold_at));
```
```hcl
resource "aws_s3_bucket_public_access_block" "lake" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Checklist de revisión
- [ ] Zonas separadas con permisos distintos y raw inmutable.
- [ ] Formato de tabla abierto + catálogo; sin ficheros sueltos en curated.
- [ ] Partición por fecha (baja cardinalidad); plan de compactación/expiración.
- [ ] Cifrado y bloqueo de acceso público.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Checkov: bucket S3 sin cifrado o con acceso público | 1 | checks estándar de Checkov sobre Terraform; reglas propias en `policies/iac-checks/` |
| Revisión de particionado y esquema de tabla nueva | 3 | revisión humana |
| Job de compactación monitorizado | 2 | pendiente (proyecto generado) |

En local: MinIO + Iceberg/Parquet con Spark, Trino o DuckDB. No se reproducen IAM de S3, Lake Formation ni Glue Catalog con fidelidad; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `warehouse-options`, `data-modeling`, `data-governance-and-classification`, `data-platform-cost`.
- Fuentes: documentación Apache Iceberg (URL arriba, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
