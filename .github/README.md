# .github

- `workflows/ci.yml` — en cada push a `main` y en cada PR ejecuta `make setup`, `make validate` y `make test`. Las acciones están fijadas por SHA del commit (no por tag) y el workflow solo pide `contents: read`.
- `CODEOWNERS` — hoy un único responsable para todo el repo y, explícitamente, para `gates/` y `.claude/hooks/`. Ampliar cuando haya más personas.
- `pull_request_template.md` — qué cambia, por qué, y checklist: `make check` en verde, sin afirmaciones sobre AWS real, versiones verificadas o marcadas, ADR si hay decisión relevante.
