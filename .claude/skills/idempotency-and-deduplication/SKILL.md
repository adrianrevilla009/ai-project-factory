---
name: idempotency-and-deduplication
description: Usar al diseñar endpoints POST reintentables, consumidores de mensajes o jobs que pueden repetirse; claves de idempotencia y deduplicación.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Idempotencia y deduplicación

## Cuándo aplicar y cuándo no
- Aplica a operaciones con efectos (pagos, pedidos, emails), consumidores de colas/eventos y jobs con reintentos.
- No aplica a lecturas ni a operaciones naturalmente idempotentes (`PUT` de estado completo, `DELETE`).

## Reglas
- **MUST** asumir entrega *at-least-once*: todo consumidor y todo endpoint con reintento debe tolerar duplicados.
- **MUST** exigir en `POST` con efecto una clave de cliente (cabecera `Idempotency-Key`; el estándar IETF es borrador, TODO-VERIFY) y guardarla con el resultado.
- **MUST** hacer la reserva de la clave atómica con una restricción `UNIQUE` en la misma transacción que el efecto; no "consultar y luego insertar".
- **MUST** que la misma clave con cuerpo distinto devuelva error (422/409), y con el mismo cuerpo devuelva la respuesta original.
- **MUST** deduplicar mensajes por id de evento (tabla `processed_message` con `UNIQUE(message_id, consumer)`) en la misma transacción que el efecto.
- **MUST** definir retención/TTL de las claves y limpiarlas.
- **MUST NOT** deduplicar solo en memoria ni en caché volátil.
- **MUST NOT** implementar doble escritura Postgres+NoSQL para guardar las claves; una sola fuente de verdad.
- **SHOULD** combinar con *outbox* para publicar eventos de forma exactamente-una-vez-efectiva.

## Por qué
Timeouts y reintentos de red hacen que el cliente no sepa si la operación ocurrió; reintentar sin idempotencia cobra dos veces. Una comprobación previa tiene carrera; solo una restricción de unicidad transaccional es fiable.

## Ejemplos
### Mal
```java
@PostMapping("/payments")
Payment pay(@RequestBody PayRequest r) {
    return paymentService.charge(r);        // un reintento cobra dos veces
}
```
### Bien
```sql
CREATE TABLE idempotency_key (
  key         text PRIMARY KEY,
  request_hash text NOT NULL,
  response    jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
);
```
```java
@Transactional
public Payment pay(String key, PayRequest r) {
    try {
        keys.insert(key, hash(r));          // UNIQUE: falla si ya existe
    } catch (DuplicateKeyException e) {
        var prev = keys.find(key);
        if (!prev.requestHash().equals(hash(r))) throw new IdempotencyKeyReusedException(key);
        return prev.response();             // mismo resultado, sin repetir el efecto
    }
    var p = charge(r);
    keys.saveResponse(key, p);
    return p;
}
```

## Checklist de revisión
- [ ] Cada POST con efecto exige clave.
- [ ] Reserva con `UNIQUE` en la misma transacción que el efecto.
- [ ] Consumidores deduplican por id de mensaje.
- [ ] Hash de petición comparado; TTL definido.
- [ ] Test de doble envío concurrente.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Test de doble envío concurrente (patrón en `concurrency-testing`) | 1 | tests del proyecto generado |
| Revisión de endpoints/consumidores con efecto | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `distributed-locking`, `concurrency-testing`, `event-driven`, `sagas-and-process-managers`.
- Fuentes: borrador IETF "Idempotency-Key HTTP Header Field" — TODO-VERIFY estado (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
