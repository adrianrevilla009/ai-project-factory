---
name: audit-trail-without-event-sourcing
description: "Usar cuando se necesita historial de cambios o auditoría de negocio y se duda entre event sourcing y alternativas más simples (tabla de auditoría, Envers, CDC, temporal tables)."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Audit trail sin event sourcing

## Cuándo aplicar y cuándo no
- Aplica cuando el requisito es "quién cambió qué y cuándo", trazabilidad o consulta de versiones anteriores, pero el estado actual sigue siendo la fuente de verdad.
- No aplica cuando el negocio necesita reconstruir el estado en cualquier instante y derivar vistas del historial: entonces evaluar `when-to-use-and-when-not` y `event-sourcing`. Auditoría de seguridad (login, accesos): ver `audit-trail-and-security-logging`.

## Reglas
- **MUST** elegir la opción más simple que cumpla: (1) tabla `*_audit` escrita en la misma transacción; (2) Hibernate Envers; (3) CDC a un almacén de auditoría de solo-anexar; (4) tablas temporales si el motor las ofrece.
- **MUST** registrar actor (`user_id` o servicio), instante, acción, entidad e id, y diff o valores antes/después.
- **MUST** escribir la auditoría en la misma transacción que el cambio (o vía CDC del WAL); NUNCA como segundo paso best-effort.
- **MUST** que la tabla de auditoría sea de solo-anexar: sin `UPDATE`/`DELETE` para el rol de la aplicación.
- **MUST NOT** copiar PII completa al historial sin política de retención y borrado (ver `gdpr-and-immutable-events`, `retention-and-cleanup`).
- **SHOULD** particionar por fecha para poder archivar (ver `partitioning-and-archival`).
- **SHOULD** documentar en ADR por qué no se usa event sourcing.

## Por qué
El 90 % de las peticiones de "auditoría" se resuelven con una tabla o con CDC, sin pagar el coste permanente del event sourcing (versionado, proyecciones, rebuilds). El historial es un efecto secundario consultable, no el modelo.

## Ejemplos
### Mal
```java
// Auditoria "luego", fuera de la transaccion, sin actor
orders.save(order);
try { auditClient.post("order updated " + order.id()); } catch (Exception ignored) {}
```
### Bien
```sql
create table order_audit (
  audit_id bigint generated always as identity primary key,
  order_id uuid not null, action text not null, actor text not null,
  changed_at timestamptz not null default now(),
  before jsonb, after jsonb
);
revoke update, delete on order_audit from app_role;
```
```java
@Transactional
public void changeStatus(UUID id, OrderStatus next, String actor) {
    Order o = orders.findById(id).orElseThrow();
    var before = snapshot(o);
    o.changeStatus(next);
    audits.save(new OrderAudit(id, "STATUS_CHANGED", actor, before, snapshot(o)));
}
```

## Checklist de revisión
- [ ] La auditoría está en la misma transacción o proviene del WAL (CDC).
- [ ] Incluye actor, instante, entidad, antes/después.
- [ ] El rol de la aplicación no puede modificar ni borrar auditoría.
- [ ] Retención y PII definidas.
- [ ] ADR si se rechazó event sourcing.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Migración con `revoke update, delete` en tablas `*_audit` | 3 | revisión de migraciones (`schema-migrations`) |
| Regla Rego/Conftest sobre migraciones sin REVOKE en `*_audit` | pendiente | `policies/opa-conftest/` (no existe aún) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `when-to-use-and-when-not`, `auditing-soft-delete-history`, `audit-trail-and-security-logging`, `outbox-and-cdc`.
- Fuentes: documentación de Hibernate Envers (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
