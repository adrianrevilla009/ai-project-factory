---
name: config-by-environment
description: "Usar al organizar la configuración por entorno (dev/stage/prod) con GitOps + Vault (D11): qué va en Git, qué en Vault y cómo se inyecta en Spring Boot."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Configuración por entorno (GitOps + Vault)

## Cuándo aplicar y cuándo no
- Aplica a toda configuración que cambie entre entornos o regiones de un servicio Spring Boot desplegado en Kubernetes.
- No aplica al diseño de `@ConfigurationProperties` (ver `configuration-properties`) ni a la configuración con servidor central (ver `spring-cloud-config-module`, opcional).

## Reglas
- **MUST** seguir D11: la configuración no secreta vive en Git (overlays por entorno, aplicados por GitOps); los secretos viven en Vault y nunca en Git.
- **MUST** mantener el artefacto inmutable: la misma imagen se promueve entre entornos; solo cambian configuración y secretos.
- **MUST** separar por capas: `application.yml` (defectos seguros) < overlay de entorno < overlay de región < secretos inyectados. Solo se sobrescribe lo necesario.
- **MUST** referenciar secretos con placeholders (`${DB_PASSWORD}`) o ficheros montados; el valor lo inyecta Vault (ver `injection-patterns`).
- **MUST** validar la configuración al arrancar (`@Validated` + fallo rápido) para que un valor ausente rompa el despliegue, no la primera petición.
- **MUST NOT** usar perfiles de Spring para esconder diferencias de comportamiento de negocio; los perfiles solo seleccionan infraestructura.
- **MUST NOT** poner valores `prod` por defecto en el repositorio de código del servicio; el repo de entornos (GitOps) es la fuente.
- **SHOULD** que cada cambio de configuración pase por PR con revisión y quede auditado en Git.
- **SHOULD** documentar cada clave con propietario, valores permitidos y si es sensible.

## Por qué
Menos componentes que un servidor de configuración y auditoría gratuita vía Git (ADR-0011). Separar "qué" (Git) de "secreto" (Vault) permite revisar cambios sin ver credenciales y revertir con `git revert`. En local no se reproduce la integración IAM/KMS de AWS: se usa Vault dev o ficheros `.env.example`.

## Ejemplos
### Mal
```yaml
# application-prod.yml dentro del repo del servicio
spring:
  datasource:
    url: jdbc:postgresql://prod-db.internal:5432/orders
    password: Pr0dPassw0rd
```
### Bien
```yaml
# application.yml (defectos seguros, sin secretos)
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}      # inyectado por Vault en runtime
```
```yaml
# repo GitOps: envs/prod/eu-west-1/values.yaml (sin secretos)
config:
  DB_URL: jdbc:postgresql://orders-db.example.internal:5432/orders
vault:
  role: orders-service
  secretPath: secret/data/orders/prod/db
```
```text
# .env.example (local)
DB_PASSWORD=changeme
```

## Checklist de revisión
- [ ] Ningún secreto ni valor de producción en el repo del servicio.
- [ ] Misma imagen en todos los entornos; solo cambian overlays.
- [ ] Arranque falla rápido ante configuración inválida.
- [ ] Cambios de config en PR sobre el repo GitOps.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: literal sensible en `application*.yml/properties` | 1 | `policies/semgrep/config-literal-secret-in-properties.yaml` |
| Hook que bloquea literales con aspecto de secreto | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Revisión de overlays por entorno | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `secrets-management`, `configuration-properties`, `injection-patterns`, `twelve-factor`, `secrets-in-gitops`, `spring-cloud-config-module`.
- Fuentes: ADR-0011; Spring Boot reference, Externalized Configuration. Diseño preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
