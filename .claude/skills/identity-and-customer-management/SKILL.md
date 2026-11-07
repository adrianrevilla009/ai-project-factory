---
name: identity-and-customer-management
description: "Usar al diseñar identidad de usuarios/clientes (registro, perfil, federación, roles) sobre Keycloak y su separación del modelo de cliente de negocio."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Identidad y gestión de clientes

## Cuándo aplicar y cuándo no
- Aplica a registro, login, perfil, recuperación de cuenta, federación (LDAP/IdP externo) y relación entre usuario autenticado y "cliente" de negocio.
- No aplica a la validación de tokens en el resource server (ver `authn-oidc-oauth2`) ni a permisos finos por recurso (autorización de dominio).

## Reglas
- **MUST** delegar autenticación y almacén de credenciales en Keycloak; el servicio de negocio NUNCA guarda contraseñas ni hashes.
- **MUST** separar identidad (Keycloak: `sub`, credenciales, MFA) de cliente de negocio (tabla `customer` propia) enlazados por `sub` inmutable, no por email.
- **MUST** crear el registro `customer` de forma idempotente en el primer login o por evento, con clave única sobre `identity_subject`.
- **MUST** tratar el email como atributo mutable y verificado, nunca como clave primaria.
- **SHOULD** usar la Admin REST API de Keycloak solo desde un servicio de backend con cliente de servicio de mínimo privilegio.
- **SHOULD** modelar roles gruesos en Keycloak y permisos de dominio en el servicio.
- **MUST NOT** duplicar en la BD de negocio datos de credenciales ni sincronizar contraseñas.
- **MUST NOT** confiar en claims editables por el usuario (ej. atributos de perfil sin protección) para autorizar.

## Por qué
Mezclar identidad y cliente hace imposible federar, fusionar cuentas o cambiar de IdP. El `sub` es estable; el email cambia. Keycloak soporta federación de usuarios, identity brokering y Admin REST API según su guía oficial (https://www.keycloak.org/docs/latest/server_admin/, consultada 2026-11-07). La feature "organizations" existe en la guía; su madurez por versión es TODO-VERIFY.

## Ejemplos
### Mal
```java
// Clave por email, contraseña propia
@Entity class Customer { @Id String email; String passwordHash; }
```
### Bien
```java
@Entity
@Table(name = "customer", uniqueConstraints = @UniqueConstraint(columnNames = "identity_subject"))
class Customer {
    @Id UUID id;
    @Column(name = "identity_subject", nullable = false) String identitySubject; // claim "sub"
    String displayName;
    String email; // mutable, verificado por el IdP
}
```
```sql
INSERT INTO customer (id, identity_subject, email)
VALUES (gen_random_uuid(), :sub, :email)
ON CONFLICT (identity_subject) DO NOTHING;
```

## Checklist de revisión
- [ ] Ninguna tabla de negocio guarda credenciales.
- [ ] `identity_subject` único y no nulo.
- [ ] Alta de cliente idempotente.
- [ ] Cliente de servicio de Keycloak con roles mínimos.
- [ ] Borrado/anonimización de cliente coordinado con `consent-and-dsar-management`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep de secretos en config | 1 | `policies/semgrep/config-literal-secret-in-properties.yaml` |
| Regla Semgrep contra columnas `password` en entidades | 1 | pendiente |
| Revisión de modelo de identidad | 3 | agente `code-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `authn-oidc-oauth2`, `pii-and-data-classification`, `consent-and-dsar-management`, `multi-tenancy`.
- Fuentes: documentación Keycloak Server Administration (2026-11-07). Local: Keycloak en contenedor; no se reproduce la HA/DR de AWS (ver `vault-and-keycloak-dr`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
