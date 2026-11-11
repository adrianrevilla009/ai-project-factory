# .github

La configuración de GitHub del repositorio: integración continua, responsables del código y plantilla de PR.

| Fichero | Qué hace |
|---|---|
| `workflows/ci.yml` | Se ejecuta en cada push a `main` y en cada PR, con dos trabajos: **`validate`** (instala las dependencias y ejecuta `make validate` y `make test`) y **`policies`** (instala Semgrep 1.184.0 y ejecuta `make policy-test`) |
| `CODEOWNERS` | Quién debe revisar los cambios: hoy una única persona para todo el repositorio y, explícitamente, para `gates/` y `.claude/hooks/`, que son lo más sensible. Se amplía cuando haya más personas |
| `pull_request_template.md` | La plantilla de PR: qué cambia, por qué y una checklist (`make check` en verde, sin afirmaciones sobre AWS real, versiones y flags verificados o declarados «no comprobados», ADR si hay una decisión relevante) |

## Cómo está endurecido el CI
- Las acciones de terceros están **fijadas por el SHA del commit**, no por una etiqueta mutable (decisión D20).
- El workflow pide solo `contents: read`.
- No hay secretos ni despliegues: el CI únicamente valida.

Qué comprueba `make validate` y `make test`: [`factory/validators/`](../factory/validators/README.md) y [`tests/`](../tests/README.md).
