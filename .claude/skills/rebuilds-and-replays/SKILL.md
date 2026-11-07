---
name: rebuilds-and-replays
description: "Usar al reconstruir proyecciones o read models de un sistema event-sourced desde el log de eventos (rebuild, replay, blue/green de proyecciones)."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Rebuilds y replays de proyecciones

Subskill de `event-sourcing`. Complementa `projections-and-read-models` y `event-versioning-and-upcasting`.

## Cuándo aplicar y cuándo no
- Aplica cuando una proyección cambia de forma, tiene un bug de datos, o se crea una nueva vista sobre eventos ya existentes.
- No aplica a sistemas sin log de eventos como fuente de verdad (ahí el "rebuild" es una migración de esquema; ver `schema-migrations`).

## Reglas
- **MUST** poder reconstruir cualquier proyección desde el log completo; si no se puede, no es una proyección sino una segunda fuente de verdad (prohibido por 4.5, sin doble escritura).
- **MUST** hacer el rebuild en una proyección nueva (versión N+1) y conmutar la lectura al terminar (blue/green); nunca vaciar la vista en uso.
- **MUST** guardar el checkpoint (último `global_position` aplicado) en la misma transacción que el efecto en la vista, para reanudar sin duplicar.
- **MUST** que los handlers de proyección sean idempotentes y deterministas: sin `Instant.now()`, sin llamadas a servicios externos, sin leer otras vistas.
- **MUST** que un replay no dispare efectos laterales (emails, publicación a Kafka, webhooks); separar proyectores de reacciones (`process managers`).
- **SHOULD** procesar en lotes y limitar el ritmo para no competir con el tráfico de lectura/escritura del almacén de eventos.
- **SHOULD** medir y documentar la duración del rebuild completo con volumen realista; es un runbook, no una sorpresa.
- **MUST NOT** depender de la retención de un broker (p. ej. 24 h en DynamoDB Streams) para reconstruir: la fuente es el event store.

## Por qué
Poder reconstruir es la razón de ser del event sourcing. Un rebuild que requiere parar el sistema, o que reenvía correos, convierte la ventaja en riesgo. Los checkpoints transaccionales dan semántica "efecto exactamente una vez" sobre entrega al-menos-una-vez.

## Ejemplos
### Mal
```java
// Rebuild destructivo y con efectos laterales
orderSummaryRepository.deleteAll();
eventStore.readAll().forEach(e -> {
    projector.apply(e);
    mailer.send(e.customerId(), "Order updated"); // efecto lateral en replay
});
```
### Bien
```java
@Transactional
void applyBatch(String projection, List<StoredEvent> batch) {
    for (StoredEvent e : batch) {
        projector.apply(e);               // puro, idempotente, escribe en orders_summary_v2
    }
    long last = batch.get(batch.size() - 1).globalPosition();
    checkpoints.save(projection, last);   // misma transaccion que el efecto
}
// Al terminar: lecturas apuntan a orders_summary_v2; v1 se elimina tras ventana de rollback.
```

## Checklist de revisión
- [ ] La proyección se reconstruye en una versión nueva y se conmuta al final.
- [ ] Checkpoint y efecto comparten transacción.
- [ ] Handlers sin reloj, sin I/O externo, sin efectos laterales.
- [ ] Hay runbook con duración medida y plan de rollback.
- [ ] Hay un test que reconstruye desde cero y compara con la vista viva.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test de reconstrucción "vista viva == vista reconstruida" | 3 | tests del proyecto generado (pendiente de plantilla en la fábrica; ver `testing-event-sourced-systems`) |
| Revisión de handlers de proyección | 3 | agente `code-reviewer` |
| Regla Semgrep contra `Instant.now()` en proyectores | pendiente | `policies/semgrep/` (no existe aún) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `projections-and-read-models`, `snapshots`, `event-versioning-and-upcasting`, `idempotency-and-deduplication`.
- Fuentes: DynamoDB Streams retiene registros hasta 24 h — https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html (verificado 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
