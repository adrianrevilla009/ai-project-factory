# factory

Código Python que mantiene la coherencia de la propia fábrica (ADR-0029). No genera proyectos (ADR-0038).

- `validators/` — se ejecutan con `make validate`:
  - `skill_structure.py` — cada skill tiene frontmatter válido, las 7 secciones, ejemplos de código y una tabla de enforcement con mecanismo real.
  - `honest_claims.py` — rechaza afirmaciones del tipo «listo para producción en AWS» y exige etiqueta de madurez en directorios con Terraform.
  - `schemas_and_adrs.py` — valida los esquemas JSON/YAML y que existan los ADRs 0001–0027.
  - `run_all.py` — los ejecuta todos y falla si alguno da error.
- `tools/build_index.py` — genera `docs/skills-index.md` y `standards/NN-*.md` a partir de las skills. Con `--check` falla si están desactualizados.
