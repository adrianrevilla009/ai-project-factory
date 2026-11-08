---
name: transactions
description: Usar al definir límites transaccionales con @Transactional (propagación, rollback, self-invocation, llamadas externas).
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Transacciones con Spring

## Cuándo aplicar y cuándo no
- Aplica a servicios que escriben en BD o necesitan lecturas consistentes.
- No aplica a coordinación entre servicios distintos (ver `sagas-and-process-managers`); no hay transacción distribuida por defecto.

## Reglas
- **MUST** colocar `@Transactional` en la capa de servicio/caso de uso, no en controladores ni repositorios.
- **MUST** marcar `readOnly = true` en los casos de uso de solo lectura.
- **MUST NOT** llamar a HTTP, colas o ficheros dentro de una transacción abierta: mantiene conexión y bloqueos durante la latencia externa. Usar outbox o ejecutar tras el commit (`@TransactionalEventListener(phase = AFTER_COMMIT)`).
- **MUST NOT** invocar un método `@Transactional` desde la misma clase (self-invocation): el proxy no interviene. Extraer a otro bean.
- **MUST** recordar que por defecto solo hace rollback con `RuntimeException`/`Error`; las excepciones comprobadas requieren `rollbackFor`.
- **MUST NOT** capturar y tragarse una excepción dentro de la transacción esperando que continúe; puede quedar marcada como solo-rollback.
- **SHOULD** mantener transacciones cortas, con el menor número de filas y bloqueos posible.
- **MUST** usar `REQUIRES_NEW` solo con justificación escrita (auditoría, outbox de errores) y consciente del segundo uso de conexión.
- **MUST NOT** usar `@Transactional` en métodos `private` o `final` esperando efecto.

## Por qué
La transacción es la unidad de consistencia y también de coste: retiene una conexión del pool y posibles bloqueos. Los fallos más comunes son silenciosos: proxy no aplicado, rollback que no ocurre, conexión retenida durante una llamada HTTP.

## Ejemplos
### Mal
```java
@Service
class CheckoutService {
    @Transactional
    public void checkout(Long id) {
        orderRepo.markPaid(id);
        paymentClient.charge(id);      // HTTP dentro de la transacción
        this.sendReceipt(id);          // self-invocation: su @Transactional no se aplica
    }
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    void sendReceipt(Long id) { }
}
```
### Bien
```java
@Service
class CheckoutService {
    private final OrderRepository orders;
    private final ApplicationEventPublisher events;

    @Transactional(rollbackFor = PaymentRejectedException.class)
    public void checkout(Long id) throws PaymentRejectedException {
        Order order = orders.getReferenceById(id);
        order.markPaid();
        events.publishEvent(new OrderPaid(id)); // un listener AFTER_COMMIT hace la llamada externa
    }
}
```

## Checklist de revisión
- [ ] `@Transactional` solo en servicios, con `readOnly` donde corresponde.
- [ ] Sin I/O externo dentro de la transacción.
- [ ] Sin self-invocation de métodos transaccionales.
- [ ] `rollbackFor` para excepciones comprobadas.
- [ ] Cada `REQUIRES_NEW` justificado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: `@Transactional` solo en paquete de servicios | 1 | pendiente (`policies/archunit/`) |
| Test de integración de rollback | 2 | tests del proyecto generado |
| Revisión de límites transaccionales | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `isolation-levels-and-anomalies`, `persistence-context-and-flush`, `domain-events-in-spring`, `connection-pooling`.
- Fuentes: Spring Framework reference (Transaction Management, declarative) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
