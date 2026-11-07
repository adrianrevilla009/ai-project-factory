# ADR-0038: Alcance del repositorio: solo guías, sin plantillas ni app de referencia

- **Estado:** aceptado
- **Fecha:** 2026-11-07

## Contexto
El brief original (§5, D-principios) incluía `templates/` (Copier), `reference-app/`, CLI/generadores y tests de generación. El dueño aclaró que este repositorio solo debe contener las guías.

## Decisión
La fábrica contiene únicamente guías consumibles por agentes: skills, agentes, comandos, hooks, policies (reglas OPA/Kyverno/Semgrep/ArchUnit como ficheros), estándares, catálogo, gates, marcos de dominio/normativa y validadores. Se eliminan `templates/`, `reference-app/`, `factory/cli`, `factory/generators` y los tests que generan o ejecutan proyectos. Java, React, Terraform, etc. aparecen solo como código de ejemplo dentro de los skills. Sustituye a las partes del brief que los mencionan (principio 2 "Copier", §5, §11 en lo que dependa de la app de referencia, y la Oleada 1 "reference-app").

## Consecuencias
- No hace falta toolchain Java/Maven para este repo.
- Desaparece el control "skills vs app de referencia"; los ejemplos de cada skill deben ser autocontenidos y revisarse por humanos/agentes.
- El `.claude/`, hooks y `CLAUDE.md` de un proyecto generado los producen los agentes siguiendo skills (a escribir), no plantillas.
- El enforcement sigue siendo posible como ficheros de policy y hooks reutilizables.

## Ampliación (2026-11-07)
Se eliminan también `factory/mcp-servers` y `factory/orchestrator` (código ejecutable de producto). El estado de gates lo hacen cumplir los hooks y los registros de aprobación; la gobernanza de MCP se cubre con el skill `mcp-governance` y `.mcp.json` queda vacío por defecto (permisos mínimos).
