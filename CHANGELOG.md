# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) · Versionado SemVer.

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
