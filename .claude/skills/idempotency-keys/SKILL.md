---
name: idempotency-keys
description: Usar al diseñar POST/acciones con efectos que un cliente puede reintentar (pagos, pedidos) o consumidores que pueden recibir duplicados.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Claves de idempotencia

## Cuándo aplicar y cuándo no
- Aplica a operaciones no idempotentes por naturaleza (POST de creación, cobros, envíos) expuestas a clientes con reintentos, y a handlers de mensajes.
- No aplica a GET/PUT/DELETE bien diseñados (ya idempotentes) ni a lecturas.

## Reglas
- **MUST** aceptar la cabecera `Idempotency-Key` (UUID generado por el cliente) en los POST que crean recursos o mueven dinero; ausente = 400 si la operación la exige.
- **MUST** guardar clave + huella (hash) del cuerpo + respuesta en la misma transacción que el efecto, en la base de datos relacional del servicio (sin doble escritura a un segundo almacén).
- **MUST** protegerlo con restricción única `(tenant, key)`; una carrera concurrente devuelve 409 o espera, nunca ejecuta dos veces.
- **MUST** devolver la respuesta original almacenada ante la misma clave y mismo cuerpo; **MUST** responder 422/409 si la clave se reutiliza con cuerpo distinto.
- **MUST** definir TTL (p. ej. 24 h, a confirmar con negocio) y limpieza programada.
- **MUST NOT** derivar la clave en servidor del contenido para operaciones que legítimamente pueden repetirse.
- **SHOULD** aplicar el mismo patrón en consumidores: tabla de `processed_message_id` (ver `delivery-semantics`).
- **SHOULD** alinear la cabecera con el borrador IETF `Idempotency-Key` (`draft-ietf-httpapi-idempotency-key-header-08`, en la cola del RFC Editor el 2026-11-08).

## Por qué
Los timeouts hacen que el cliente no sepa si la petición se ejecutó; reintentar sin clave genera pedidos o cobros duplicados. La clave convierte "al menos una vez" en efecto "exactamente una vez" observable.

## Ejemplos
### Mal
```java
@PostMapping("/payments")
Payment pay(@RequestBody PayRequest r) { return gateway.charge(r); } // un reintento cobra dos veces
```
### Bien
```java
@Transactional
public PaymentResponse pay(String tenant, String key, PayRequest r) {
    String hash = Hashing.sha256(r);
    Optional<IdempotencyRecord> prev = records.findByTenantAndKey(tenant, key);
    if (prev.isPresent()) {
        if (!prev.get().requestHash().equals(hash)) throw new IdempotencyKeyReusedException(key);
        return prev.get().response();
    }
    PaymentResponse resp = paymentService.charge(r);
    records.save(new IdempotencyRecord(tenant, key, hash, resp, Instant.now()));
    return resp; // UNIQUE(tenant, key) cubre la carrera: el segundo insert falla y se reintenta la lectura
}
```

## Checklist de revisión
- [ ] Operaciones críticas exigen `Idempotency-Key`.
- [ ] Clave, huella y efecto en la misma transacción.
- [ ] Restricción única y manejo de carrera probados.
- [ ] Mismo cuerpo = misma respuesta; cuerpo distinto = error.
- [ ] TTL y limpieza definidos; documentado en OpenAPI.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Test de concurrencia (dos peticiones con la misma clave) en el proyecto generado | 1 | pendiente: plantilla de test en `integration-testing-testcontainers` |
| Revisión de POST críticos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `delivery-semantics`, `rest-design-guidelines`, `dlq-retries-poison-messages`, `rate-limiting-quotas`.
- Fuentes: borrador IETF HTTPAPI "The Idempotency-Key HTTP Header Field" — estado y número verificados el 2026-11-08 en datatracker.ietf.org.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
