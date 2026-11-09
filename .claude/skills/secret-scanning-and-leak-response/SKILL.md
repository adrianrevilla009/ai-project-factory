---
name: secret-scanning-and-leak-response
description: "Usar al configurar escaneo de secretos (pre-commit, CI, histórico) y al responder a una fuga: revocar, rotar, investigar y prevenir recurrencia."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "hook"
---

# Escaneo de secretos y respuesta a fugas

## Cuándo aplicar y cuándo no
- Aplica a todo repositorio generado, al pipeline de CI y a cualquier incidente en que un secreto aparezca en commit, log, ticket o chat.
- No aplica al diseño de dónde guardar secretos (ver `secrets-management`) ni a la rotación técnica en Vault (ver `rotation-and-leases`).

## Reglas
- **MUST** ejecutar un escáner de secretos con licencia OSS (p. ej. gitleaks, MIT) en pre-commit y en CI sobre cada PR; el job de CI bloquea el merge.
- **MUST** escanear también el histórico completo al adoptar el repositorio y de forma periódica, con baseline versionado para hallazgos aceptados y revisados.
- **MUST** mantener una configuración de reglas del proyecto (`.gitleaks.toml`) con reglas propias de los formatos internos de token.
- **MUST** tratar cualquier hallazgo real como comprometido: 1) revocar/rotar primero, 2) revisar los logs de auditoría por uso indebido, 3) limpiar el historial si procede, 4) post-mortem y regla de detección nueva. Borrar el commit no basta.
- **MUST NOT** desactivar el escáner con `SKIP=` ni con allowlists amplias; las excepciones llevan justificación y caducidad en PR.
- **MUST** usar en ejemplos y tests literales falsos con `example` o `changeme`, y registrarlos en la allowlist estrecha por ruta.
- **MUST** tener runbook de fuga con responsable, canal y plazos (SLA según `vulnerability-sla-and-incident-response`).
- **SHOULD** activar el secret scanning/push protection de la plataforma Git si está disponible sin coste, además del escáner propio.
- **SHOULD** escanear también imágenes, artefactos de build y logs de CI.
- **SHOULD** medir tiempo de rotación tras detección y número de falsos positivos.

## Por qué
Un secreto publicado se explota en minutos; la revocación inmediata es la única mitigación fiable. Un escáner solo en CI llega tarde (el secreto ya está en la rama remota); el pre-commit evita el commit y CI cubre quien lo omite.

## Ejemplos
### Mal
```text
git commit -m "fix" --no-verify          # salta el hook
SKIP=gitleaks git commit -m "wip"
# allowlist: regex ".*" para silenciar falsos positivos
```
### Bien
```yaml
#.pre-commit-config.yaml (rev)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.2
    hooks:
      - id: gitleaks
```
```text
# CI (resumen): gitleaks git -v   # escanea el historial; el job falla si hay hallazgos
```
```toml
# .gitleaks.toml: allowlist estrecha para valores falsos documentados
[allowlist]
description = "valores falsos de ejemplo"
regexes = ['''changeme[\w-]*''', '''example[\w-]*''']
```
Sintaxis de `.gitleaks.toml`.

## Criterios de decisión y trampas
### Cómo decidir
- Detecta secretos antes del commit y en el repositorio; ante una fuga, revoca y rota primero, limpia el historial después.
- Un procedimiento ensayado y un responsable.
### Trampas frecuentes
- Borrar el secreto del historial y no revocarlo.
- Escáneres con tanto ruido que se ignoran.
- Sin procedimiento de rotación rápida.
- Descubrir la fuga por un tercero.
- Secretos que se copian a herramientas de colaboración.
### Evidencia
- Un simulacro de fuga con tiempo de revocación medido.

## Checklist de revisión
- [ ] Escáner en pre-commit y en CI bloqueante; histórico escaneado.
- [ ] Baseline y allowlist estrechas, con justificación.
- [ ] Runbook de fuga: revocar, auditar, limpiar, post-mortem.
- [ ] Ejemplos con `example`/`changeme`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook que bloquea literales con aspecto de secreto al escribir | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Regla Semgrep: literal sensible en ficheros de configuración | 1 | `policies/semgrep/config-literal-secret-in-properties.yaml` |
| Job gitleaks en CI y pre-commit del proyecto generado | 1 | pendiente (workflow del proyecto generado) |
| Revisión del post-mortem de fugas | 4 | humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `secrets-management`, `rotation-and-leases`, `audit-and-break-glass`, `supply-chain`, `vulnerability-sla-and-incident-response`.
- Fuentes: https://github.com/gitleaks/gitleaks (consultada 2026-11-07: licencia MIT, comandos `git`/`dir`/`stdin`, `.gitleaks.toml`, pre-commit).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
