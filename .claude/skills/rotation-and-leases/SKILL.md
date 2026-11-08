---
name: rotation-and-leases
description: "Usar al diseñar la rotación de secretos y el ciclo de vida de leases de Vault (TTL, renovación, revocación) y la tolerancia de las apps a credenciales que cambian."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Vault: rotación y leases

## Cuándo aplicar y cuándo no
- Aplica a secretos dinámicos (BD, PKI, tokens), secretos estáticos rotados y al comportamiento de la app ante cambios.
- No aplica a rotación de claves de cifrado de datos (ver `transit-encryption`, `envelope-encryption-and-kms`) ni a respuesta ante fuga (ver `secret-scanning-and-leak-response`, pendiente).

## Reglas
- **MUST** dar a todo secreto un TTL: `default_ttl` corto y `max_ttl` acotado por motor/rol. **MUST NOT** emitir leases sin caducidad.
- **MUST** que el cliente renueve el lease antes de que expire (hacia ~2/3 del TTL) y, al llegar a `max_ttl`, solicite credenciales nuevas en vez de fallar.
- **MUST** que el pool de conexiones soporte la rotación: crear conexiones con credenciales nuevas y drenar las antiguas (HikariCP: `maxLifetime` menor que el TTL del lease, menos margen).
- **MUST** coordinar el TTL de la credencial con `maxLifetime` y con el tiempo de arranque de la app; un TTL menor que el arranque causa bucles de fallo.
- **SHOULD** usar revocación por prefijo (`vault lease revoke -prefix`) en respuesta a incidentes, y comprobar su efecto en la BD.
- **MUST** rotar secretos estáticos (API keys de terceros, roles estáticos de BD) con periodo definido y propietario; la rotación **MUST** ser automática o con runbook probado.
- **MUST** monitorizar: leases activos, fallos de renovación, expiraciones inminentes, errores de autenticación tras rotar.
- **MUST** asumir que, tras un failover regional (D10), los leases del Vault caído no existen en el otro: las apps piden credenciales nuevas al Vault local (ver `dynamic-database-credentials` para el orden BD, luego motor).
- **SHOULD** evitar rotar `root` de BD y claves de unseal en horas punta; planificar ventanas.
- **MUST NOT** usar rotación como sustituto de revocar un secreto comprometido: revocar primero.

## Por qué
Rotar sin tolerancia en el cliente convierte la seguridad en caídas: el pool mantiene la contraseña vieja y fallan las conexiones cuando se revoca. TTL cortos reducen la ventana de exposición, a cambio de exigir renovación robusta y observabilidad.

## Ejemplos
### Mal
```yaml
# application.yml: pool con vida mayor que el lease
spring:
  datasource:
    hikari:
      max-lifetime: 86400000   # 24 h; el lease dura 1 h
```
```text
vault write database/roles/orders-rw db_name=orders default_ttl=0 max_ttl=0
```
### Bien
```yaml
spring:
  config:
    import: optional:configtree:/vault/secrets/
  datasource:
    username: ${username}
    password: ${password}
    hikari:
      max-lifetime: 2400000    # 40 min < lease de 1 h
      connection-timeout: 5000
```
```text
vault write database/roles/orders-rw db_name=orders default_ttl=1h max_ttl=4h
vault lease revoke -prefix database/creds/orders-rw   # solo en incidente, con aviso a la app
```
VSO con `rolloutRestartTargets` (ver `injection-patterns`) reinicia el Deployment al cambiar el secreto. La relación exacta entre refresh de VSO y TTL: comprobar al fijar la versión.

## Checklist de revisión
- [ ] Todos los roles tienen `default_ttl` y `max_ttl`.
- [ ] `maxLifetime` del pool menor que el TTL; reconexión probada con rotación forzada.
- [ ] Alertas sobre fallos de renovación y expiración.
- [ ] Runbook de revocación por prefijo y de rotación de estáticos.
- [ ] Caso de failover regional contemplado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Test de integración de rotación (Testcontainers Postgres + Vault) | 1 | pendiente: tests del proyecto generado |
| Conftest: roles sin TTL | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de TTL vs `maxLifetime` | 3 | revisión humana (code-reviewer) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dynamic-database-credentials`, `injection-patterns`, `connection-pooling`, `pki-and-cert-issuance`, `secrets-management`.
- Fuentes (2026-11-07): https://developer.hashicorp.com/vault/docs/concepts/lease ; https://developer.hashicorp.com/vault/docs/secrets/databases (comprobar comandos de revocación en la versión fijada).
- Estado: diseño; preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
