---
name: global-tables-and-write-region-rules
description: "Usar al replicar DynamoDB entre regiones (Global Tables): modo de consistencia, conflictos last-writer-wins y región de escritura por agregado o tenant."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Global Tables y región de escritura por agregado

## Cuándo aplicar y cuándo no
- Aplica a cualquier tabla DynamoDB (event store incluido) con réplicas en más de una región (ADR-0006, ADR-0007).
- No aplica a tablas de una sola región ni a la replicación de Aurora (ver `read-replicas-and-routing`).

## Reglas
- **MUST** elegir el modo de consistencia al crear la tabla; no se puede cambiar después: MREC (por defecto, asíncrono) o MRSC (síncrono, exactamente tres regiones).
- **MUST** con MREC asumir replicación asíncrona y conflictos "last writer wins" por ítem: la versión esperada del event store solo protege dentro de una región.
- **MUST** fijar UNA región de escritura por agregado (o por tenant) y documentarla; las demás réplicas solo leen o actúan como standby.
- **MUST** imponer la región de escritura con IAM/enrutado (política que deniega escritura en otras regiones, enrutado por tenant), no solo por convención.
- **MUST NOT** hacer escrituras concurrentes del mismo agregado en dos regiones con MREC.
- **MUST NOT** asumir atomicidad de `TransactWriteItems` entre regiones con MREC: solo es atómica en la región de origen.
- **SHOULD** evaluar MRSC solo si se exige RPO cero y lecturas fuertes multi-región; asumir mayor latencia de escritura y sus restricciones (sin transacciones, sin TTL, sin LSI).
- **MUST** definir el procedimiento de conmutación (failover) de la región de escritura de un agregado y probarlo en simulación antes de confiar en él.
- **MUST** probar conmutación y conflictos solo en pruebas y simulaciones; la fábrica no despliega (ADR-0004): preparado para AWS, no verificado en real.

## Por qué
Con MREC, una lectura fuerte solo devuelve lo último si el ítem se escribió por última vez en esa región, y la resolución de conflictos es por marca de tiempo: dos comandos concurrentes en regiones distintas pueden perder uno silenciosamente. Fijar el escritor por agregado elimina la clase de conflicto. MRSC cambia latencia y funciones por consistencia.

## Ejemplos
### Mal
```yaml
# Ambas regiones aceptan comandos del mismo pedido (active-active ciego, MREC)
route: { eu-west-1: all-tenants, eu-central-1: all-tenants }
```
### Bien
```yaml
# docs/data/write-regions.yaml
consistency_mode: MREC            # inmutable tras crear la tabla
aggregates:
  order:  { write_region_by: tenant, mapping: { tenant-a: eu-west-1, tenant-b: eu-central-1 } }
  ledger: { write_region: eu-west-1, standby: eu-central-1, failover: "runbook-ledger-failover" }
```
```json
{ "Effect": "Deny", "Action": ["dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:DeleteItem"],
  "Resource": "arn:aws:dynamodb:eu-central-1:111111111111:table/events",
  "Condition": {"StringEquals": {"aws:PrincipalTag/write-region": "eu-west-1"}} }
```
La condición es ilustrativa (cuenta de ejemplo); adaptar y validar con el simulador de políticas de IAM (comprobar al fijar la versión).

## Checklist de revisión
- [ ] Modo MREC/MRSC decidido y justificado.
- [ ] Región de escritura por agregado/tenant documentada y forzada por IAM o enrutado.
- [ ] No hay transacciones que se asuman atómicas entre regiones.
- [ ] Hay runbook de conmutación con idempotencia ante duplicados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del mapa de regiones de escritura en el gate de arquitectura | 4 | `gates/` |
| Política OPA sobre el plan de Terraform (tablas con réplicas sin mapa de escritura) | 1 | pendiente en `policies/opa-conftest/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dynamodb-event-store`, `consistency-and-cap-tradeoffs`, `idempotency-and-deduplication`, `multi-tenant-architecture`.
- Fuentes (consultadas 2026-11-07): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html (modos MREC/MRSC, last writer wins, tres regiones para MRSC, sin transacciones ni TTL en MRSC); https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html. La lista de regiones con MRSC cambia: comprobar al diseñar.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
