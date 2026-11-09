---
name: sagas-and-process-managers
description: "Usar al coordinar una operación de negocio que abarca varios servicios o aggregates sin transacción distribuida: sagas, compensaciones, timeouts."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Sagas y process managers

## Cuándo aplicar y cuándo no
- Aplica a flujos de negocio con varios pasos en distintos contexts (pedido, pago, stock, envío) que deben acabar coherentes.
- No aplica si todo cabe en un aggregate/transacción local, ni como excusa para trocear un dominio que debería ser un solo módulo.

## Reglas
- **MUST NOT** usar transacciones distribuidas (2PC/XA) entre servicios.
- **MUST** definir para cada paso su acción compensatoria (o declarar explícitamente que es irreversible y colocarlo el último).
- **MUST** persistir el estado de la saga (id, paso actual, estado, deadline) para sobrevivir a reinicios.
- **MUST** hacer cada paso y cada compensación idempotentes, con reintentos y backoff.
- **MUST** definir timeouts y estado terminal (`COMPLETED`, `COMPENSATED`, `FAILED_NEEDS_MANUAL`) con alerta en el último.
- **MUST** correlacionar todos los mensajes con `sagaId`/`correlationId`.
- **SHOULD** elegir coreografía (eventos) para 2-3 participantes y orquestación (process manager explícito) para flujos más largos o con ramas.
- **SHOULD** ordenar los pasos: primero los reversibles, al final el que no se puede deshacer (ej. cobro tras reservar stock).
- **SHOULD** exponer el estado de la saga a la UI/API (consistencia eventual, ver `consistency-and-cap-tradeoffs`).

## Por qué
Sin transacción global, un fallo a medio camino deja datos incoherentes (pago cobrado sin pedido). La saga convierte esa incoherencia en un estado modelado, observable y recuperable. La complejidad es real: compensar no es "deshacer", es un nuevo hecho de negocio (reembolso).

## Ejemplos
### Mal
```java
paymentClient.charge(order);        // cobra
inventoryClient.reserve(order);     // falla -> el cliente pagó y no hay reserva ni reembolso
```
### Bien
```java
// Orquestador con estado persistido
public enum SagaState { STARTED, STOCK_RESERVED, PAID, COMPLETED, COMPENSATING, COMPENSATED, FAILED_NEEDS_MANUAL }

void on(StockReserved e) { saga.advance(e.sagaId(), STOCK_RESERVED); commands.send(new ChargePayment(e.sagaId(), e.orderId())); }
void on(PaymentFailed e) { saga.advance(e.sagaId(), COMPENSATING); commands.send(new ReleaseStock(e.sagaId(), e.orderId())); }
void on(StockReleased e) { saga.advance(e.sagaId(), COMPENSATED); }
```
```text
Pasos: ReserveStock (comp: ReleaseStock) -> ChargePayment (comp: RefundPayment) -> ScheduleShipment (irreversible, último)
```

## Criterios de decisión y trampas
### Cómo decidir
- Orquestación (un coordinador central) cuando el proceso es complejo y debe ser visible; coreografía (reacciones a eventos) cuando es simple y los servicios son autónomos.
- Cada paso tiene su acción compensatoria definida.
### Trampas frecuentes
- Sagas sin compensaciones.
- Coreografías con tantos pasos que nadie ve el flujo.
- Estado de la saga solo en memoria.
- Compensaciones que también pueden fallar sin plan.
- Asumir que la compensación deshace todo (hay efectos que no se revierten).
### Evidencia
- Un diagrama del proceso con estados, tiempos máximos y compensaciones, y pruebas de fallo en cada paso.

## Checklist de revisión
- [ ] Cada paso tiene compensación o está marcado irreversible y al final.
- [ ] Estado de saga persistido con deadline y estado terminal manual.
- [ ] Pasos idempotentes con correlationId.
- [ ] Sin 2PC/XA.
- [ ] Coreografía u orquestación elegida y justificada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del diseño de la saga (diagrama de estados) | 4 | `gates/` (arquitectura) |
| Regla Semgrep contra `@XA`/JTA multi-recurso | 1 | pendiente: `policies/semgrep/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-driven`, `consistency-and-cap-tradeoffs`, `ddd-tactical`, `microservices-decision-guide`.
- Fuentes: Garcia-Molina y Salem, "Sagas" (1987); microservices.io, "Saga" (Richardson)..
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
