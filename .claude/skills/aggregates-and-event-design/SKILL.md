---
name: aggregates-and-event-design
description: "Usar al diseñar agregados y eventos de un sistema con event sourcing: límites del stream, nombres, contenido, metadatos y comandos; subskill de event-sourcing."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Agregados y diseño de eventos

## Cuándo aplicar y cuándo no
- Aplica al definir streams, eventos y la lógica de decisión de un agregado event-sourced.
- No aplica a eventos de integración entre servicios sin event sourcing (ver `asyncapi-event-contracts`). Subskill de `event-sourcing`.

## Reglas
- **MUST** un stream por agregado; el agregado es el límite de consistencia y de concurrencia (versión esperada).
- **MUST** nombrar eventos en pasado y con lenguaje del dominio (`PolicyIssued`, no `PolicyUpdated`).
- **MUST** hacer los eventos inmutables y autosuficientes para el negocio (`record` en Java, sin Lombok).
- **MUST** separar comando (intención, puede rechazarse) de evento (hecho, no se rechaza): `decide(state, command) -> events`, `evolve(state, event) -> state`.
- **MUST** mantener `evolve` puro, sin I/O, reloj ni aleatoriedad; el tiempo y los ids entran en el evento.
- **MUST** incluir `eventId`, `aggregateId`, `version`, `occurredAt`, `correlationId`, `causationId`, `schemaVersion`.
- **MUST NOT** guardar en el evento el estado completo "por comodidad" ni referencias a otros agregados que deban leerse para interpretarlo.
- **MUST NOT** guardar datos personales sin estrategia de supresión (`gdpr-and-immutable-events`).
- **SHOULD** mantener los streams acotados (si crecen sin fin, diseñar cierre del ciclo de vida o snapshots).
- **SHOULD** corregir con eventos compensatorios (`PaymentReversed`), nunca editando.

## Por qué
Un evento es contrato y registro histórico permanente: un mal nombre o un contenido ambiguo se arrastra años. Un `evolve` impuro hace imposibles las reconstrucciones deterministas y las pruebas.

## Ejemplos
### Mal
```java
record AccountUpdated(String accountId, Map<String, Object> fields) {}   // intención difusa
BigDecimal apply(AccountUpdated e) { return Instant.now()... }           // reloj dentro de evolve
```
### Bien
```java
public sealed interface AccountEvent {
    record AccountOpened(String eventId, String accountId, String currency, Instant occurredAt) implements AccountEvent {}
    record MoneyDeposited(String eventId, String accountId, long amountCents, Instant occurredAt) implements AccountEvent {}
    record MoneyWithdrawn(String eventId, String accountId, long amountCents, Instant occurredAt) implements AccountEvent {}
}

static List<AccountEvent> decide(AccountState s, Withdraw cmd, Clock clock, IdGen ids) {
    if (s.balanceCents() < cmd.amountCents()) throw new InsufficientFundsException(s.accountId());
    return List.of(new MoneyWithdrawn(ids.next(), s.accountId(), cmd.amountCents(), clock.instant()));
}

static AccountState evolve(AccountState s, AccountEvent e) {
    return switch (e) {
        case MoneyDeposited d -> s.withBalance(s.balanceCents() + d.amountCents());
        case MoneyWithdrawn w -> s.withBalance(s.balanceCents() - w.amountCents());
        case AccountOpened o -> AccountState.opened(o.accountId(), o.currency());
    };
}
```

## Checklist de revisión
- [ ] Un stream por agregado y límite de consistencia claro.
- [ ] Eventos en pasado, inmutables, con metadatos completos.
- [ ] `decide` valida, `evolve` es puro.
- [ ] Sin PII sin estrategia de supresión.
- [ ] Correcciones como eventos compensatorios.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: paquete `..event..` sin dependencias de infraestructura ni `Instant.now()` | 1 | pendiente en `policies/archunit/` |
| Revisión de eventos y `evolve` | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `ddd-tactical`, `event-versioning-and-upcasting`, `dynamodb-event-store`, `immutability-and-value-objects`, `testing-event-sourced-systems`.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
