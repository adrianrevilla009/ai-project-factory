# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) · Versionado SemVer.

## [0.5.0] - 2026-11-09
### Añadido
- Sección «Criterios de decisión y trampas» en las 490 skills (antes solo en 70).
- `capabilities/modules-map.yaml` enlazado con skills, políticas y pruebas reales y validado (`make validate`).
- `tests/agent-evals/`: 21 casos que ejecutan los hooks reales y 10 escenarios con rúbrica.
- Pruebas estáticas de agentes y comandos; trabajo `policies` en el CI; devcontainer con imagen fijada por digest y CLI de Claude Code con versión fija.
- Agentes `cloud-architect`, `devsecops-engineer` y `release-manager` (28) y comandos `/incident-response`, `/rollback-plan` y `/security-review` (29).
- Línea base de permisos en `.claude/settings.json` (allow, ask y deny) con la sintaxis verificada en la documentación de Claude Code.
### Cambiado
- Herramientas por rol: los agentes de negocio, arquitectura, documentación y gestión ya no tienen `Bash`; los revisores siguen siendo de solo lectura.
- ADR 0032–0037 y RACI de gates aceptados por el dueño.
- `last_reviewed` actualizado y nota de vigencia en el brief.

## [0.4.0] - 2026-11-09
### Añadido
- MCP: `catalog/mcp-servers.yaml` (11 servidores revisados, validado por `make validate`) y `docs/architecture/mcp.md`.
- Hooks `UserPromptSubmit` (secretos en prompts), `SubagentStop` (evidencia), `PreCompact` (estado) y `SessionEnd` (auditoría): 18 hooks en total.
- `knowledge/`: catálogo de patrones, de antipatrones e índice de decisiones, con enlaces validados.
- `docs/onboarding.md` y `docs/architecture/overview.md`.
- Skills `codeql-sast`, `sonarqube-quality-gate` y `gatling-load-testing` (490 en total).
- Sección «Criterios de decisión y trampas» en las 67 skills de QA, frontend, CI/CD y GitOps.
- Validadores de referencias cruzadas entre skills y de enlaces de `knowledge/`; `policies/iac-checks/` como especificación de los checks pendientes.
### Cambiado
- Desaparece la antigua marca de «pendiente de verificar»: lo que no se puede comprobar se declara «no comprobado». Eliminadas las frases «comprobar…» de las skills; los datos de herramientas de terceros se fijan en el BOM de cada proyecto.
- El bootstrap copia también agentes y comandos al proyecto generado.
- Ejemplos de Docker Compose sustituidos por el clúster kind (ADR-0005).

## [0.3.0] - 2026-11-08
### Añadido
- `make policy-test`: 46 reglas Semgrep validadas y probadas con casos positivos y negativos (`tests/semgrep/`).
- Validador `code_blocks.py`: sintaxis de los bloques yaml, json, xml, python, hcl y bash de las skills.
### Cambiado
- README reescritos con contenido concreto; eliminadas las carpetas vacías con README de relleno.
- Verificación contra fuentes oficiales y herramientas reales (propiedades de Spring Boot 4.x, recursos de Terraform AWS, CRD de Istio, IDs de Checkov, etiquetas de imágenes, URLs).
### Corregido
- Límite de tamaño de SCP (10.240), tamaño máximo de SQS (1 MiB), `-Djarmode=tools`, `failureAction` de Kyverno, ESO `v1`, fin de LocalStack Community, nombres con ámbito de subagentes, Istio ambient GA, propiedades renombradas de Spring Boot 4.
- 3 reglas Semgrep inválidas, 4 imprecisas y 8 ejemplos de código con sintaxis incorrecta.

## [0.2.0] - 2026-11-07
### Añadido
- 489 skills (31 bloques) con anatomía validada; 25 agentes; 27 comandos; hooks completos con 87+ tests; catálogo (librerías, tier, paridad, radar); policies de ejemplo; índice y estándares generados.
### Cambiado
- Alcance: solo guías, sin plantillas ni app de referencia (ADR-0038).

## [0.1.0-wave0] - 2026-11-06
### Añadido
- Estructura de carpetas de la fábrica con README por directorio.
- `CLAUDE.md`, gates 0–5 con checklists y `approval-record.schema.json`.
- Skills: plantilla, `skill-authoring-guide`, `gate-protocol`, `claude-md-authoring`, `verify-before-asserting`, `n-plus-one`.
- Esquemas de dominio y normativa, `capabilities.yaml`.
- ADRs 0001–0037 (D1–D27, adicionales y abiertas).
- Hooks `block_secrets`, `block_dangerous_commands`, `enforce_gate_approval` con tests.
- Validadores de estructura de skills, afirmaciones honestas, esquemas y ADRs.
- Dev container, Makefile, pre-commit y CI.
