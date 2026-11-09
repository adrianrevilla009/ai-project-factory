---
name: webhooks
description: "Usar al emitir o recibir webhooks: firma HMAC, anti-replay, reintentos, idempotencia y protección SSRF."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Webhooks

## Cuándo aplicar y cuándo no
- Aplica a endpoints que reciben callbacks de terceros y a servicios que notifican a URLs registradas por clientes.
- No aplica a eventos internos por broker (ver `kafka-producers-consumers`).

## Reglas
### Receptor
- **MUST** verificar la firma HMAC-SHA256 sobre el **cuerpo crudo** (bytes) antes de parsear, con comparación en tiempo constante (`MessageDigest.isEqual`).
- **MUST** validar un timestamp firmado y rechazar fuera de una ventana (p. ej. 5 minutos) contra replay.
- **MUST** responder 2xx rápido y procesar en asíncrono; **MUST** deduplicar por `eventId` (ver `delivery-semantics`).
- **MUST NOT** confiar en la IP origen como único control ni registrar el secreto o el cuerpo con PII.
### Emisor
- **MUST** firmar cada entrega, incluir `eventId` y timestamp, y reintentar con backoff exponencial hasta un máximo, luego marcar fallida.
- **MUST** proteger contra SSRF: solo HTTPS, resolver DNS y rechazar IPs privadas/loopback/link-local (incl. metadatos de nube), sin seguir redirecciones ciegamente.
- **MUST** timeouts cortos de conexión y lectura.
- **SHOULD** permitir rotación de secretos con dos secretos válidos a la vez.
- **SHOULD** exponer log de entregas y reenvío manual al cliente.

## Por qué
Una URL pública sin firma permite a cualquiera inyectar eventos falsos. Sin ventana temporal, una captura válida se repite. Un emisor que acepta cualquier URL se convierte en proxy hacia la red interna (SSRF). Los reintentos implican duplicados: el receptor debe ser idempotente.

## Ejemplos
### Mal
```java
@PostMapping("/hooks/payments")
ResponseEntity<Void> hook(@RequestBody PaymentEvent e, @RequestHeader("X-Sig") String sig) {
    if (sig.equals(computeHmac(e.toString()))) { service.apply(e); } // equals no constante, re-serializa
    return ResponseEntity.ok().build();
}
```
### Bien
```java
@PostMapping("/hooks/payments")
ResponseEntity<Void> hook(@RequestBody byte[] raw,
                          @RequestHeader("X-Timestamp") long ts,
                          @RequestHeader("X-Signature") String sig) {
    if (Math.abs(clock.instant().getEpochSecond() - ts) > 300) { return ResponseEntity.status(400).build(); }
    byte[] expected = hmacSha256(secret, ts + "." + new String(raw, UTF_8));
    if (!MessageDigest.isEqual(expected, HexFormat.of().parseHex(sig))) {
        return ResponseEntity.status(401).build();
    }
    inbox.enqueue(raw);                     // procesamiento asíncrono e idempotente
    return ResponseEntity.accepted().build();
}
```
```text
# secreto solo de ejemplo en configuración de test
webhook.secret=changeme-example-secret
```

## Checklist de revisión
- [ ] Firma verificada sobre bytes crudos, comparación constante.
- [ ] Ventana de timestamp y deduplicación por `eventId`.
- [ ] Respuesta rápida; trabajo asíncrono.
- [ ] Emisor con reintentos acotados, timeouts y defensa SSRF.
- [ ] Rotación de secreto documentada; el secreto vive en gestor de secretos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: comparación de firma/HMAC con `String.equals` | 1 | `policies/semgrep/webhook-signature-equals.yaml` |
| Tests de firma inválida, replay y duplicado | 1 | tests del proyecto generado (pendiente) |
| Revisión de seguridad de endpoints | 3 | agente `code-reviewer` |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `delivery-semantics`, `idempotency-keys`, `deserialization-xxe-ssrf-traversal`, `secrets-management`.
- Fuentes: RFC 2104 (HMAC); OWASP SSRF Prevention Cheat Sheet.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
