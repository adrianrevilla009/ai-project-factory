---
name: regions-and-data-residency
description: "Usar al decidir regiones AWS y residencia de datos: eu-west-1 primaria, eu-central-1 secundaria, qué replica y qué no, y disponibilidad de servicios."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Regiones y residencia de datos

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica a elegir región por recurso, definir replicación entre regiones y revisar cumplimiento de residencia UE (ADR-0006, D6).
- No aplica a topología de red entre regiones (bloque 12). En local solo hay una "región"; la replicación entre regiones NO se reproduce.

## Reglas
- **MUST** parametrizar regiones: `primary_region = "eu-west-1"` y `secondary_region = "eu-central-1"` como variables y aliases de provider; ningún literal en módulos.
- **MUST** mantener datos personales y de negocio solo en esas dos regiones; denegar el resto por SCP (ver `scp-guardrails`).
- **MUST** decidir por dato si se replica a la secundaria; la replicación es explícita, nunca por defecto.
- **MUST** respetar la regla de datos: sin doble escritura Postgres+NoSQL; replicar cada almacén con su mecanismo nativo.
- **MUST** verificar antes de diseñar que cada servicio existe en ambas regiones (TODO-VERIFY, pendiente de ADR-0006).
- **SHOULD** tratar servicios globales (IAM, Route 53, CloudFront) como excepciones documentadas; sus datos de control pueden salir de la UE (TODO-VERIFY).
- **SHOULD** documentar el RPO/RTO objetivo por servicio con la región secundaria.
- **MUST NOT** afirmar cumplimiento RGPD por usar regiones UE: es borrador por confirmar con fuente oficial y asesoría legal.
- **MUST NOT** copiar backups o logs con datos personales fuera de las dos regiones.

## Por qué
Elegir región es decidir jurisdicción, latencia y coste. Replicar por defecto duplica coste y superficie; no replicar deja sin DR. La decisión debe ser consciente y comprobable.

## Ejemplos
### Mal
```hcl
provider "aws" { region = "us-east-1" }   # literal, fuera de la UE
```
### Bien
```hcl
variable "primary_region"   { default = "eu-west-1" }
variable "secondary_region" { default = "eu-central-1" }

provider "aws" {
  region = var.primary_region
}

provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
}

resource "aws_s3_bucket_replication_configuration" "orders_docs" {
  provider = aws
  bucket   = aws_s3_bucket.orders_docs.id
  role     = aws_iam_role.replication.arn
  rule {
    id     = "to-secondary"
    status = "Enabled"
    destination { bucket = aws_s3_bucket.orders_docs_dr.arn }
  }
}
```

## Checklist de revisión
- [ ] Regiones por variable y alias, sin literales.
- [ ] Nada fuera de eu-west-1 / eu-central-1 (SCP y plan).
- [ ] Replicación decidida por dato y documentada con RPO/RTO.
- [ ] Servicios verificados en ambas regiones.
- [ ] Sin afirmación de cumplimiento legal.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: `region` distinta de las permitidas en provider | 1 | pendiente: `policies/opa-conftest/` |
| SCP de denegación por región | 1 | ver `scp-guardrails` (ejemplo en el skill) |
| Revisión legal de residencia | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `scp-guardrails`, `kms-multi-region-keys`, `log-archive-and-audit-account`, `cross-region-connectivity-and-cost`.
- Fuentes: ADR-0006 (`catalog/adr/0006-regiones-aws.md`); AWS Regional Services List (2026-11-07) — TODO-VERIFY disponibilidad de servicios; RGPD: borrador por confirmar con fuente oficial.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
