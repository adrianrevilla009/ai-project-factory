---
name: integrations-erp-crm
description: "Usar al integrar con ERP o CRM externos (SAP, Odoo, Salesforce, HubSpot u otros): sincronización, mapeo, idempotencia, límites de API, conciliación y fallos del sistema externo."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Integraciones con ERP y CRM

## Cuándo aplicar y cuándo no
- Aplica a sincronización de clientes, pedidos, facturas, stock o contactos con un sistema externo que no controlamos.
- No aplica a integraciones por fichero/SFTP (ver `batch-file-sftp-integration`) ni a SOAP heredado (ver `soap-legacy-integration`), aunque comparten principios.

## Reglas
- **MUST** aislar el sistema externo tras una anti-corruption layer: un puerto propio (`ErpGateway`) y un adaptador por producto; el modelo del ERP no entra en el dominio (`anti-corruption-layer`).
- **MUST** definir la fuente de verdad por entidad y campo (quién manda: ERP o nosotros) y documentarlo; sin ello habrá conflictos de escritura.
- **MUST** guardar un mapa de identificadores `internal_id <-> external_id` por sistema y entidad.
- **MUST** hacer las llamadas salientes idempotentes (clave de idempotencia o upsert por `external_id`) y reintentables con backoff y jitter.
- **MUST** emitir los cambios a sincronizar vía outbox, no llamando al ERP dentro de la transacción de BD (`outbox-and-cdc`).
- **MUST** configurar timeouts, circuit breaker y bulkhead por integración; el ERP caído no debe tirar la aplicación.
- **MUST** respetar los límites del proveedor (cuotas, lotes) con un limitador propio; los valores concretos se leen de su documentación oficial.
- **MUST** reconciliar periódicamente (job de conciliación con informe de diferencias) y enviar fallos definitivos a una cola de revisión manual (DLQ).
- **MUST** guardar credenciales de la integración en el gestor de secretos, con OAuth2 client credentials cuando el proveedor lo ofrezca.
- **SHOULD** preferir webhooks/eventos del proveedor más sondeo incremental con marca de agua (`updated_since`) frente a cargas completas.
- **SHOULD** validar la entrada del externo como no confiable (esquema, tamaños, enums desconocidos tolerados).
- **MUST NOT** hacer doble escritura síncrona a nuestro sistema y al ERP sin mecanismo de reconciliación.
- **MUST NOT** registrar payloads con datos personales completos en logs.

## Por qué
Los ERP/CRM tienen disponibilidad, modelos y límites ajenos. Sin ACL, mapa de ids e idempotencia, un reintento duplica pedidos; sin conciliación, las divergencias se descubren en el cierre contable.

## Ejemplos
### Mal
```java
@Transactional
public void confirm(Order o) {
    repo.save(o);
    sapClient.createSalesOrder(toSap(o));   // red dentro de la tx, sin idempotencia
}
```
### Bien
```java
@Transactional
public void confirm(Order o) {
    repo.save(o);
    outbox.add("erp.order.upsert", o.id(), OrderSyncPayload.from(o)); // misma tx
}

// consumidor del outbox
public void handle(OrderSyncPayload p) {
    String externalId = idMap.find("ERP", "ORDER", p.orderId());
    erpGateway.upsertOrder(p, idempotencyKey(p.orderId(), p.version()), externalId);
}
```

## Checklist de revisión
- [ ] Puerto y adaptador; el dominio no importa tipos del ERP.
- [ ] Fuente de verdad por entidad documentada.
- [ ] Mapa de ids y llamadas idempotentes.
- [ ] Outbox en lugar de llamada en transacción.
- [ ] Timeouts, circuit breaker y límite de tasa configurados.
- [ ] Conciliación y DLQ con proceso de revisión.
- [ ] Secretos fuera del código y logs sin PII.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep: clientes HTTP sin timeout | 1 | `policies/semgrep/spring-http-client-without-timeout.yaml` |
| Regla ArchUnit: dominio sin dependencias de SDK externos | 1 | pendiente (`policies/archunit/`) |
| Revisión de fuente de verdad y conciliación | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `anti-corruption-layer`, `outbox-and-cdc`, `idempotency-keys`, `webhooks`, `backpressure-and-bulkheads`, `batch-file-sftp-integration`, `soap-legacy-integration`.
- Fuentes: documentación oficial de cada proveedor (límites, autenticación); no se asumen valores.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
