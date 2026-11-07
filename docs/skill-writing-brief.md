# Brief para escritores de skills (uso interno de agentes)

Contexto: este repositorio contiene SOLO guías (ADR-0038). Un skill es una carpeta plana `.claude/skills/<name>/SKILL.md` (ADR-0028). Inventario: `catalog/skills-inventory.yaml`.

## Obligatorio
1. Lee `CLAUDE.md`, `.claude/skills/_template/SKILL.md`, `.claude/skills/n-plus-one/SKILL.md` (ejemplo de calidad) y `.claude/skills/skill-authoring-guide/SKILL.md`.
2. Copia la anatomía exacta: frontmatter (`name` = carpeta, `description` ≤ 200 caracteres, que diga CUÁNDO cargarlo; `metadata` con `block`, `tier`, `owner: "factory-owner"`, `last_reviewed: "2026-11-07"`, `enforcement`), y secciones `## Cuándo aplicar y cuándo no`, `## Reglas` (MUST/SHOULD/MUST NOT), `## Por qué`, `## Ejemplos` (Mal/Bien con código real en bloques ```), `## Checklist de revisión`, `## Enforcement` (tabla con mecanismo, nivel 1-4 y ruta; o "revisión humana" explícita), `## Relacionados, fuentes y mantenimiento`.
3. Idioma: prosa en español; identificadores, nombres de fichero y código en inglés.
4. Longitud: 50–150 líneas por skill. Concretos, accionables, sin relleno ni generalidades. Ejemplos autocontenidos y realistas.
5. NO inventes versiones, flags ni APIs. Si puedes, verifica con documentación oficial (WebSearch/WebFetch); si no, marca `TODO-VERIFY`. Cita fuentes oficiales con fecha 2026-11-07 cuando las uses. No copies texto de repositorios externos.
6. Honestidad AWS: nada "listo para producción en AWS", "probado en AWS", etc. Fórmula: "preparado para AWS, no verificado en real". La fábrica nunca despliega (ADR-0004). Normativa/legal: borrador por confirmar con fuente oficial.
7. Decisiones cerradas D1–D27 (`catalog/adr/`): sin Lombok, sin doble escritura Postgres+NoSQL, sin licencias de pago por defecto (Vault OSS, Harbor, etc.), Java+Spring Boot+Maven, Terraform, Istio, Keycloak, etc. Si el tema toca la matriz AWS↔local, di explícitamente qué NO se reproduce en local.
8. Enforcement: si una regla es comprobable, referencia un artefacto real en el repo. Si el artefacto no existe todavía, créalo cuando sea pequeño (regla Semgrep en `policies/semgrep/`, Rego en `policies/opa-conftest/`, Kyverno en `policies/kyverno/`, regla ArchUnit como `.java` de ejemplo en `policies/archunit/`, ESLint/dependency-cruiser en `policies/frontend-boundaries/`, Checkov custom en `policies/iac-checks/`) o márcalo como "pendiente" en la tabla. No referencies rutas que no existan sin decir "pendiente".
9. Los ejemplos con credenciales falsas deben contener las palabras `example` o `changeme` en el literal (un hook de seguridad bloquea literales que parezcan secretos reales). Los comandos peligrosos solo en bloques de texto, nunca ejecutados.
10. Solo escribe dentro de `.claude/skills/<name>/` (y `policies/` para artefactos de enforcement). NO hagas git commit, NO modifiques otros ficheros. Si un skill ya existe, no lo sobrescribas.
11. Al terminar ejecuta `python3 factory/validators/run_all.py` y corrige tus errores (ignora los de otros skills en curso). Informa en una línea: nº de skills creados y TODO-VERIFY relevantes.

Cada skill puede tener `references/` y `examples/` solo si aportan valor real.
