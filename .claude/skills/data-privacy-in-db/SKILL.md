---
name: data-privacy-in-db
description: "Usar al almacenar datos personales (PII) en SQL: clasificación, minimización, cifrado, enmascarado, retención y supresión."
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Privacidad de datos en base de datos

## Cuándo aplicar y cuándo no
- Aplica a toda tabla o columna que contenga datos personales (nombre, email, teléfono, dirección, identificadores, datos de salud o financieros).
- No aplica a datos puramente técnicos sin relación con personas. La clasificación general está en `pii-and-data-classification`.

Nota normativa: lo relativo a RGPD/LOPDGDD u otras normas es borrador por confirmar con fuente oficial y asesoría legal (TODO-VERIFY, no verificado 2026-11-07).

## Reglas
- **MUST** clasificar cada columna personal (público/interno/PII/sensible) en el diseño; documentar propósito y plazo de retención por columna o tabla.
- **MUST** minimizar: no almacenar lo que no se necesita; no copiar PII a tablas de informes, logs ni cachés sin necesidad.
- **MUST** cifrar en tránsito (TLS hacia la BD) y en reposo (cifrado de disco/volumen del proveedor); para campos especialmente sensibles, cifrado a nivel de aplicación con claves fuera de la BD (ver `secrets-management`, `crypto-tls-mtls-key-rotation`).
- **MUST NOT** guardar contraseñas ni secretos en claro; usar hash adaptativo (ver `authn-oidc-oauth2`) y delegar la identidad al IdP (Keycloak) cuando sea posible.
- **MUST NOT** copiar datos de producción a desarrollo/test; usar datos sintéticos o anonimizados de forma irreversible.
- **MUST** poder cumplir una petición de supresión/acceso: localizar todos los datos de un sujeto y borrarlos o anonimizarlos, incluidas copias, historial y archivos (ver `auditing-soft-delete-history`, `partitioning-and-archival`).
- **MUST** limitar el acceso: roles de BD de mínimo privilegio, sin cuentas de aplicación con DDL; vistas o columnas restringidas para soporte/analítica.
- **SHOULD** enmascarar PII en logs, trazas y mensajes de error; no incluirla en claves de caché ni en URLs.
- **SHOULD** pseudonimizar (id interno) en datos analíticos y separar la tabla de identidad de los datos de actividad.
- **SHOULD** registrar accesos a datos sensibles (ver `audit-trail-and-security-logging`).

## Por qué
Cuantos más sitios tiene un dato personal, más difícil es protegerlo y borrarlo. El borrado lógico, los backups, los índices de búsqueda y las cachés son copias. Diseñar la localización y supresión desde el modelo cuesta poco; añadirla después cuesta mucho. El cifrado de disco no protege frente a un acceso SQL legítimo pero abusivo: eso lo cubren los permisos y la auditoría.

## Ejemplos
### Mal
```sql
CREATE TABLE report_customer_export AS SELECT * FROM customer;   -- copia completa de PII
UPDATE customer SET deleted = true WHERE id = 42;                 -- "supresion" que conserva los datos
```
```java
log.info("Created customer {}", customer);   // toString con email y telefono
```
### Bien
```sql
-- supresion: anonimizar PII y conservar la fila para integridad referencial
UPDATE customer
SET email = 'deleted-' || id || '@example.invalid',
    full_name = 'DELETED',
    phone = NULL,
    anonymized_at = now()
WHERE id = :id;

CREATE VIEW support_customer_v AS
SELECT id, country, created_at FROM customer;     -- soporte sin PII directa
GRANT SELECT ON support_customer_v TO support_ro;
```
```java
log.info("Created customer id={}", customer.getId());
```

## Checklist de revisión
- [ ] Columnas PII clasificadas, con propósito y retención.
- [ ] Sin copias innecesarias de PII (informes, cachés, logs, test).
- [ ] Cifrado en tránsito y reposo; campos sensibles valorados.
- [ ] Existe procedimiento probado de acceso/supresión que cubre historial y archivos.
- [ ] Roles de BD de mínimo privilegio.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: logging de entidades con PII | 1 | pendiente (`policies/semgrep/`) |
| Hook de seguridad contra secretos en literales | 2 | `.claude/hooks/` (ver reglas de secretos de la fábrica) |
| Revisión humana de clasificación y retención | 4 | PR + responsable de privacidad |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pii-and-data-classification`, `auditing-soft-delete-history`, `partitioning-and-archival`, `multi-tenancy`, `caching`.
- Fuentes: texto oficial del RGPD (EUR-Lex) y guías de la autoridad de control — TODO-VERIFY, pendiente de confirmar con fuente oficial; no verificado 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
