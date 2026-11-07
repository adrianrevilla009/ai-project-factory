---
name: secrets-management
description: Usar al manejar contraseñas, tokens, claves API o certificados en código, configuración, CI o despliegue, y al elegir dónde guardarlos y cómo rotarlos.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "hook"
---

# Gestión de secretos

## Cuándo aplicar y cuándo no
- Aplica a cualquier credencial: BD, brokers, APIs de terceros, claves de firma, certificados, tokens de CI.
- No aplica a configuración no sensible (URLs públicas, flags) ni al diseño de cifrado (ver `crypto-tls-mtls-key-rotation`).

## Reglas
- **MUST NOT** commitear secretos reales (código, `application.yml`, `.env`, Terraform, tfstate, imágenes Docker, logs).
- **MUST** inyectar secretos en runtime desde un gestor: AWS Secrets Manager o SSM Parameter Store (preparado para AWS, no verificado en real) y Vault OSS u OpenBao u otro gestor sin licencia de pago como equivalente local (D16). No se reproduce en local la integración IAM/KMS de AWS.
- **MUST** usar credenciales efímeras cuando exista la opción (roles IAM, IRSA, credenciales dinámicas de BD) antes que claves estáticas.
- **MUST** poder rotar cada secreto sin redespliegue de código y con plan documentado (frecuencia, responsable, procedimiento).
- **MUST** tratar como comprometido y rotar de inmediato cualquier secreto que haya llegado a un commit, log o chat; borrar el historial no basta.
- **MUST** ejecutar escaneo de secretos en pre-commit y en CI.
- **MUST NOT** pasar secretos por argumentos de línea de comandos, variables de build (`ARG`) ni imprimirlos en logs/trazas.
- **SHOULD** preferir ficheros montados o API del gestor frente a variables de entorno (se filtran en volcados y `/proc`).
- **SHOULD** un secreto por servicio y entorno, con permisos de lectura mínimos.
- **MUST** usar en ejemplos y tests valores falsos con `example` o `changeme`.

## Por qué
Un secreto en el repositorio queda en el historial, en forks y en cachés de CI. Los secretos estáticos y compartidos no se pueden revocar sin romper todo. Los efímeros acotan el daño y hacen la rotación rutinaria.

## Ejemplos
### Mal
```yaml
spring:
  datasource:
    password: Sup3rS3cret!        # en el repositorio
```
### Bien
```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}      # inyectado en runtime; valor fuera del repo
  config:
    import: "optional:aws-secretsmanager:/example-app/prod/db"   # TODO-VERIFY starter y sintaxis (Spring Cloud AWS)
```
```text
# .env.example (si, se versiona; .env real no)
DB_PASSWORD=changeme
```
```text
# Respuesta ante fuga: 1) revocar/rotar  2) revisar uso en logs de auditoria
# 3) limpiar historial si procede  4) post-mortem y regla de deteccion
```

## Checklist de revisión
- [ ] No hay secretos en repo, imágenes ni logs; `.env` en `.gitignore`.
- [ ] Origen del secreto en runtime documentado, con permisos mínimos.
- [ ] Plan de rotación definido y probado.
- [ ] Escáner de secretos activo en pre-commit y CI.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook de seguridad que bloquea literales que parecen secretos | 2 | `.claude/hooks/` (revisar nombre exacto del hook existente, TODO-VERIFY) |
| Escáner de secretos en CI (p. ej. gitleaks, licencia OSS) | 1 | pendiente (workflow de CI del proyecto generado) |
| Revisión humana de la política de rotación | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `crypto-tls-mtls-key-rotation`, `cloud-iam-least-privilege`, `audit-trail-and-security-logging`, `container-and-k8s-security`.
- Fuentes: OWASP Secrets Management Cheat Sheet, documentación de AWS Secrets Manager y de Vault/OpenBao, consultadas 2026-11-07, TODO-VERIFY URLs y licencias vigentes.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
