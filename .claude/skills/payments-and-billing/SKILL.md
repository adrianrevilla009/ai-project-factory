---
name: payments-and-billing
description: "Usar al integrar pasarelas de pago, modelar importes, cobros recurrentes, facturacion o conciliacion; cubre dinero, idempotencia y webhooks."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Pagos y facturación

## Cuándo aplicar y cuándo no
- Aplica a cobros, reembolsos, suscripciones, facturas, conciliación y webhooks de un proveedor de pagos (PSP).
- No aplica a pasarelas bancarias internas ni a contabilidad completa (ERP; ver `integrations-erp-crm`). La normativa fiscal y PCI es un borrador por confirmar con fuente oficial.

## Reglas
- **MUST** representar dinero como `BigDecimal` o unidades menores (`long`) junto a un código de moneda ISO 4217; nunca `double`/`float`.
- **MUST** enviar una clave de idempotencia en cada operación de cobro/reembolso y persistirla con el pedido.
- **MUST** tratar el webhook del PSP como fuente de verdad del estado del pago; la redirección del navegador solo informa.
- **MUST** verificar la firma del webhook sobre el cuerpo crudo, con comparación en tiempo constante, y rechazar marcas de tiempo antiguas.
- **MUST** deduplicar webhooks por `event.id` (los PSP reintentan y entregan desordenado) y procesarlos de forma idempotente.
- **MUST** modelar el pago como máquina de estados explícita (`PENDING -> AUTHORIZED -> CAPTURED -> REFUNDED/FAILED`) con transiciones validadas.
- **MUST NOT** almacenar PAN, CVV ni datos de tarjeta; usar tokenización/hosted fields del PSP para quedar fuera del alcance PCI en lo posible.
- **MUST NOT** hacer dual-write entre la BD y el PSP sin outbox o reconciliación (ver `outbox-and-cdc`).
- **SHOULD** ejecutar una conciliación periódica (job) entre registros propios y el informe del PSP.
- **SHOULD** emitir facturas como documentos inmutables numerados; las correcciones son notas de abono, no ediciones.
- **SHOULD** usar el sandbox del PSP en local; no reproducir el PSP real en local.

## Por qué
El dinero en coma flotante acumula errores de redondeo. Las redes fallan: sin idempotencia un reintento cobra dos veces. Stripe documenta que reintentar con la misma clave devuelve la respuesta guardada, que las claves pueden purgarse tras 24 horas y que las claves aceptan hasta 255 caracteres; otros PSP difieren, verificar el del proyecto.

## Ejemplos
### Mal
```java
double total = price * quantity;                       // error de redondeo
psp.charge(customerToken, total);                      // sin idempotencia
@PostMapping("/psp/webhook")
void hook(@RequestBody Event e) { orders.markPaid(e.orderId()); } // sin firma, sin dedupe
```
### Bien
```java
record Money(BigDecimal amount, Currency currency) {
    Money { amount = amount.setScale(currency.getDefaultFractionDigits(), RoundingMode.HALF_EVEN); }
}

var key = "charge-" + order.id() + "-" + order.attempt();   // estable entre reintentos
PaymentIntent pi = psp.charge(order.token(), order.total(), key);

@PostMapping("/psp/webhook")
ResponseEntity<Void> hook(@RequestBody byte[] raw, @RequestHeader("Stripe-Signature") String sig) {
    Event e = signatureVerifier.verifyOrThrow(raw, sig);        // cuerpo crudo + tolerancia temporal
    if (!processedEvents.tryInsert(e.id())) return ResponseEntity.ok().build(); // duplicado
    payments.apply(e);                                          // transición validada
    return ResponseEntity.ok().build();
}
```
El nombre de cabecera `Stripe-Signature` es de Stripe; adaptarlo al PSP elegido.

## Checklist de revisión
- [ ] Sin `double`/`float` en importes; moneda explícita.
- [ ] Idempotencia en cobros y reembolsos.
- [ ] Webhook con firma, tolerancia temporal y dedupe por id.
- [ ] Máquina de estados de pago con transiciones inválidas rechazadas.
- [ ] Sin datos de tarjeta en BD, logs ni trazas.
- [ ] Job de conciliación definido.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep: importes en `double`/`float` (heurística por nombre) | 1 | `policies/semgrep/java-money-floating-point.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Semgrep: firma de webhook comparada con `equals` | 1 | `policies/semgrep/webhook-signature-equals.yaml` |
| Revisión de flujo de pago y PCI | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `time-and-money`, `idempotency-keys`, `webhooks`, `sagas-and-process-managers`, `outbox-and-cdc`, `pii-and-data-classification`.
- Fuentes: Stripe, Idempotent requests, https://docs.stripe.com/api/idempotent_requests y Webhooks, https://docs.stripe.com/webhooks (verificado 2026-11-07). PCI DSS y facturación electrónica.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
