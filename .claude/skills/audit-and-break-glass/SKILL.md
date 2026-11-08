---
name: audit-and-break-glass
description: "Usar al configurar auditoría de Vault (audit devices) y al diseñar el acceso de emergencia (break-glass, root token, claves de unseal) con trazabilidad."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Auditoría de Vault y acceso break-glass

## Cuándo aplicar y cuándo no
- Aplica al diseño operativo de cada clúster Vault OSS (uno por región, D10) y a los procedimientos de emergencia.
- No aplica a la auditoría de aplicación (ver `audit-trail-and-security-logging`) ni al DR del clúster (ver `vault-and-keycloak-dr`).

## Reglas
- **MUST** habilitar al menos dos audit devices (p. ej. `file` y `syslog`/`socket`) en cada clúster: si ninguno puede escribir, Vault rechaza la petición.
- **MUST** enviar los logs de auditoría fuera del nodo Vault (agregador de logs con retención y acceso restringido); quien administra Vault no puede borrarlos.
- **MUST** monitorizar fallos de escritura del audit device y alertar: es indisponibilidad del servicio, no un detalle.
- **MUST NOT** usar `log_raw` salvo diagnóstico puntual aprobado: expone valores sin hash.
- **MUST** revocar el root token tras el bootstrap; generar uno nuevo solo con `vault operator generate-root` y quórum de claves, y revocarlo al terminar.
- **MUST** definir break-glass como procedimiento documentado: política `break-glass` nominal, TTL corto, activación con doble aprobación, alerta inmediata al activarse y revisión posterior obligatoria.
- **MUST** repartir las claves de unseal/recovery entre custodios distintos (Shamir) y registrar quién las custodia, sin guardarlas juntas.
- **SHOULD** ensayar el break-glass al menos semestralmente en un entorno no productivo.
- **SHOULD** alertar sobre uso de rutas sensibles (`sys/audit`, `sys/policies`, `sys/generate-root`).

## Por qué
Vault garantiza escribir cada petición en al menos un audit device; por eso hace falta redundancia o un fallo de disco detiene todos los secretos. Los valores sensibles se registran con HMAC-SHA256, así que el log es compartible con el SOC sin filtrar secretos. Un root token vivo o un acceso de emergencia sin rastro anula el resto del modelo de políticas.

## Ejemplos
### Mal
```text
vault audit enable file file_path=/vault/audit.log     # un único device, en el mismo disco
# root token guardado en el wiki "por si acaso"
```
### Bien
```text
vault audit enable -path=file_local file file_path=/vault/audit/audit.log
vault audit enable -path=syslog_sink syslog tag="vault" facility="AUTH"
vault token revoke <root-token-example>                # tras el bootstrap
```
```hcl
# policy break-glass: solo se asigna mediante workflow con doble aprobación, TTL <= 1h
path "secret/data/example-app/*" { capabilities = ["read", "list"] }
```

## Checklist de revisión
- [ ] Dos o más audit devices activos por clúster y logs exportados fuera del nodo.
- [ ] Alerta si falla la escritura de auditoría.
- [ ] No existe root token vivo; procedimiento `generate-root` documentado.
- [ ] Break-glass con doble aprobación, TTL corto y revisión posterior.
- [ ] Custodios de claves de unseal identificados y separados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de configuración Vault (audit devices >= 2, sin `log_raw`) | 3 | agente `code-reviewer` sobre el IaC/Helm del proyecto generado |
| Regla Rego/Conftest que exija 2 audit devices en el values de Vault | 1 | pendiente (`policies/opa-conftest/`) |
| Aprobación humana del procedimiento break-glass y del ensayo | 4 | PR + acta |

## Relacionados, fuentes y mantenimiento
- Relacionados: `deployment-ha`, `policies`, `vault-and-keycloak-dr`, `audit-trail-and-security-logging`.
- Fuentes: https://developer.hashicorp.com/vault/docs/audit (consultada 2026-11-07: mínimo un device operativo, recomendación de dos, HMAC-SHA256). Licencia BUSL y alternativa OpenBao: ADR-0031, comprobar con revisión legal. Diseño preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
