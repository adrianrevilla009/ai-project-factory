---
name: gdpr-and-immutable-events
description: "Usar al diseñar eventos inmutables (event sourcing, logs, outbox) que contienen datos personales y hay que atender supresión o rectificación."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# RGPD y eventos inmutables

Subskill de `event-sourcing`. Normativa: borrador por confirmar con fuente oficial y asesoría legal (RGPD, art. 17); este skill es técnico, no jurídico.

## Cuándo aplicar y cuándo no
- Aplica a cualquier evento persistido de forma inmutable que pueda contener datos personales (nombre, email, IP, dirección).
- No aplica a eventos sin datos personales (p. ej. `StockAdjusted` con SKU y cantidad) ni a datos anonimizados de forma irreversible desde el origen.

## Reglas
- **MUST** clasificar los campos de cada tipo de evento (ver `pii-and-data-classification`) antes de definirlo; el payload mínimo es el que no necesita PII.
- **MUST** guardar los datos personales fuera del evento (tabla de perfil mutable) y referenciarlos por `subjectId` opaco, o cifrarlos con una clave por sujeto (crypto-shredding).
- **MUST** que borrar al sujeto sea destruir su clave o su fila de perfil; el evento sigue siendo válido y reproducible con el dato "olvidado".
- **MUST** que las proyecciones y copias derivadas (búsqueda, caché, data lake) también purguen al sujeto; documentar el mapa de copias.
- **MUST** custodiar las claves por sujeto en KMS/Vault OSS con copia de seguridad coherente: restaurar una copia antigua NO debe resucitar una clave destruida (registrar los borrados y reaplicarlos).
- **MUST NOT** reescribir ni borrar eventos del store para cumplir una supresión salvo decisión explícita con ADR; rompe hashes, versiones y proyecciones.
- **MUST NOT** poner PII en claves de stream, tipos de evento, cabeceras o logs.
- **SHOULD** definir plazos de retención por categoría y automatizar la destrucción de claves.

## Por qué
La inmutabilidad choca con el derecho de supresión. La salida técnica habitual es que el log no contenga el dato en claro: sin clave o sin referencia, el evento deja de identificar a nadie. Reescribir historia es frágil y caro; el cifrado por sujeto lo convierte en una operación pequeña y auditable. Si el cifrado cumple el requisito legal en cada jurisdicción es cuestión a confirmar con fuente oficial.

## Ejemplos
### Mal
```java
public record CustomerRegistered(String customerId, String fullName, String email, String iban) {}
// PII en claro, inmutable y replicado a vistas y al lago
```
### Bien
```java
public record CustomerRegistered(String customerId, String subjectId, byte[] encryptedProfile, String keyId) {}

void forgetSubject(String subjectId) {
    keyStore.destroy(subjectId);             // crypto-shredding
    forgottenLog.append(subjectId, clock.instant()); // reaplicar tras restaurar backups
    projectionPurger.purge(subjectId);       // vistas, indice de busqueda, cache
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Reconcilia inmutabilidad y supresión con datos personales fuera del evento (referencias) o cifrados por sujeto cuyas claves se destruyen; la norma exacta la valida una persona de legal.
- Decide el enfoque en el diseño, no al recibir la primera solicitud.
### Trampas frecuentes
- Datos personales en claro dentro de eventos inmutables.
- Borrar eventos y romper la reconstrucción.
- Claves compartidas por muchos sujetos.
- Copias y proyecciones que no se alcanzan con la supresión.
- Suponer que cifrar basta sin gestionar las claves.
### Evidencia
- Una prueba de supresión de extremo a extremo: eventos, proyecciones, copias y registros.

## Checklist de revisión
- [ ] Cada evento tiene sus campos clasificados; ninguno lleva PII sin cifrar o referenciar.
- [ ] Existe procedimiento y prueba de "olvidar sujeto" extremo a extremo (store, vistas, búsqueda, caché).
- [ ] Restaurar un backup no recupera claves destruidas.
- [ ] Sin PII en claves de stream, cabeceras ni logs.
- [ ] ADR si se descarta el cifrado por sujeto.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de definiciones de eventos contra clasificación PII | 3 | agente `code-reviewer` + `pii-and-data-classification` |
| Test de "forget subject" que comprueba que no queda PII legible | 3 | tests del proyecto generado (pendiente) |
| Validación legal del criterio de supresión | 4 | revisión humana (DPO/legal) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `pii-and-data-classification`, `data-privacy-in-db`, `secrets-management`, `retention-and-cleanup`.
- Fuentes: texto del RGPD en EUR-Lex (art. 17); no se ha consultado en esta revisión.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
