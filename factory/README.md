# factory

El código Python que mantiene la coherencia de la propia fábrica (ADR-0029). **No genera proyectos** (ADR-0038): solo comprueba que las guías, los datos y la documentación siguen siendo correctos y coherentes entre sí.

## Contenido
| Carpeta | Qué hay |
|---|---|
| [`validators/`](validators/README.md) | Los validadores, que se ejecutan con `make validate` y en el CI |
| `tools/build_index.py` | Genera `docs/skills-index.md` y las páginas de `standards/` a partir de las skills y del inventario |

## `build_index.py`
Lee `catalog/skills-inventory.yaml` y cada `SKILL.md` y genera:

- `docs/skills-index.md`: las skills por bloque, con descripción, nivel y cuántas hay de las previstas.
- `standards/NN-bloque.md`: las reglas `MUST`, `SHOULD`, `MAY` y `MUST NOT` de todas las skills de cada bloque.

Uso: `make index` los regenera y `python3 factory/tools/build_index.py --check` falla si están desactualizados, que es lo que hace `make validate`. Los ficheros generados no se editan a mano.

## Cuándo ejecutarlo
Después de crear, renombrar o cambiar las reglas de una skill: `make index` y después `make check`.
