---
name: audit-trail-and-activity-log
description: "Usar al diseñar el registro de auditoria de negocio (quien hizo que y cuando) y el historial de actividad visible al usuario en una aplicacion empresarial."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Audit trail y activity log (funcionalidad de producto)

## Cuándo aplicar y cuándo no
- Aplica a la función de producto: historial de cambios de entidades de negocio, "quién aprobó qué", pantalla de actividad y exportación para auditores.
- No aplica a logs de seguridad de infraestructura ni cuentas de archivo de logs (ver `audit-trail-and-security-logging`, `log-archive-and-audit-account`), ni a Event Sourcing completo (ver `audit-trail-without-event-sourcing`).

## Reglas
- **MUST** registrar por evento: `occurredAt` (UTC), actor (id de usuario o servicio), `tenantId`, acción (código estable), tipo e id del recurso, resultado, `correlationId`.
- **MUST** escribir el evento de auditoría en la misma transacción que el cambio (o vía outbox); un cambio sin rastro no debe existir.
- **MUST** hacer la tabla append-only: sin `UPDATE`/`DELETE` para el rol de la aplicación.
- **MUST** guardar el delta de campos (`before`/`after`) solo de campos permitidos; los datos personales y secretos se omiten o se enmascaran.
- **MUST NOT** registrar contraseñas, tokens ni datos de tarjeta en el payload de auditoría.
- **MUST** auditar también lecturas sensibles, exportaciones y accesos denegados.
- **SHOULD** definir retención por tipo de evento; la retención legal es un borrador por confirmar con asesoría.
- **SHOULD** exponer consulta paginada por keyset con filtros por actor, recurso y rango, restringida por permiso y tenant.
- **SHOULD** separar el historial de usuario (legible, traducido) de la auditoría técnica (códigos estables).
- **MUST NOT** depender de la auditoría para lógica de negocio; si el flujo la necesita, es un modelo de dominio.

## Por qué
La auditoría solo sirve si es completa, inmutable y atribuible. Escribirla fuera de la transacción deja huecos silenciosos; permitir editarla la invalida como evidencia. Con el derecho de supresión (ver `consent-and-dsar-management`) conviene guardar referencias seudonimizadas, no datos personales.

## Ejemplos
### Mal
```java
orderRepository.save(order);
log.info("order {} updated by {} name={} email={}", order.getId(), user, order.getCustomerName(), order.getEmail()); // PII en log, no atómico, mutable
```
### Bien
```sql
CREATE TABLE audit_event (
  id            UUID PRIMARY KEY,
  occurred_at   TIMESTAMPTZ NOT NULL,
  tenant_id     UUID NOT NULL,
  actor_id      TEXT NOT NULL,
  action        TEXT NOT NULL,         -- ORDER_APPROVED
  resource_type TEXT NOT NULL,
  resource_id   TEXT NOT NULL,
  outcome       TEXT NOT NULL,
  correlation_id TEXT,
  changes       JSONB                  -- solo campos permitidos
);
REVOKE UPDATE, DELETE ON audit_event FROM app_rw;
```
```java
@Transactional
public void approve(OrderId id, Actor actor) {
    var order = orders.require(id).approve();
    orders.save(order);
    audit.record(AuditEvent.of(actor, "ORDER_APPROVED", "Order", id.value(), Outcome.SUCCESS));
}
```

## Checklist de revisión
- [ ] Evento con actor, tenant, acción, recurso, resultado y correlación.
- [ ] Misma transacción u outbox; tabla append-only.
- [ ] Sin PII ni secretos en el delta.
- [ ] Lecturas sensibles y exportaciones auditadas.
- [ ] Consulta restringida por permiso y tenant; retención definida.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test de integración: cambio sin evento falla (patrón a incluir en el proyecto generado) | 1 | tests del proyecto generado (pendiente) |
| Revisión de PII en payloads de auditoría | 3 | agente `code-reviewer` |
| Retención legal | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `audit-trail-and-security-logging`, `auditing-soft-delete-history`, `audit-and-break-glass`, `outbox-and-cdc`, `pii-and-data-classification`, `gdpr-and-immutable-events`.
- Fuentes: OWASP Logging Cheat Sheet, https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
