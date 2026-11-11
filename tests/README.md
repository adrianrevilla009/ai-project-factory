# tests

Las pruebas de la **maquinaria** de la fábrica: hooks, validadores, reglas de Semgrep y comportamiento de los agentes. No prueban el contenido de las skills (eso lo comprueban los validadores); prueban que las herramientas que lo hacen cumplir funcionan.

## Contenido
| Carpeta | Qué prueba | Cómo se ejecuta |
|---|---|---|
| [`hooks/`](hooks/README.md) | Cada hook, lanzado como en producción con un evento JSON | `make test` |
| [`validators/`](validators/README.md) | Los validadores y la definición de agentes y comandos | `make test` |
| [`agent-evals/`](agent-evals/README.md) | El comportamiento esperado de los agentes: casos de hook ejecutables y escenarios con rúbrica | `make test` (los escenarios con modelo solo se validan por estructura) |
| [`semgrep/`](semgrep/README.md) | Las reglas de `policies/semgrep/` con casos positivos y negativos | `make policy-test` (requiere Semgrep) |

## Comandos
```bash
make test          # pytest tests: hooks, validadores y agent-evals
make check         # make validate + make test
make policy-test   # semgrep --test sobre policies/semgrep y tests/semgrep
python3 -m pytest tests/hooks -q      # solo una carpeta
```

## Convenciones
- **Sin secretos literales:** los valores de prueba que parecen credenciales se construyen en tiempo de ejecución, para que ningún fichero del repo contenga uno.
- **Cada regla, con su caso negativo:** una prueba que solo comprueba que algo se bloquea no basta; hay que comprobar también lo que debe pasar.
- **Aisladas:** cada prueba usa una carpeta temporal y no depende del orden ni del estado del repo.
- **Qué no hay:** pruebas de código de proyectos generados (la fábrica no tiene ninguno) ni evaluación automática de respuestas de un modelo.
