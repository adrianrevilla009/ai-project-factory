# standards

Las reglas de cada bloque de skills reunidas en una sola página, para leerlas de corrido sin abrir cada `SKILL.md`.

## Contenido
Un fichero por bloque, `NN-nombre-del-bloque.md`, con 31 en total (por ejemplo, `01-java-language.md`, `13-kubernetes-and-istio.md` o `27-frontend-react.md`). Cada uno agrupa, skill por skill, las reglas `MUST`, `SHOULD`, `MAY` y `MUST NOT`. Para saber cuántas skills tiene cada bloque, ver [`.claude/README.md`](../.claude/README.md).

## Cómo se generan
Los produce `make index` a partir de las skills (`factory/tools/build_index.py`). **No se editan a mano**: la fuente de verdad es cada `SKILL.md`, y `make validate` falla si estas páginas están desactualizadas.

## Para qué sirven
- Leer todas las normas de un tema de una vez (por ejemplo, toda la seguridad de aplicación).
- Revisar la coherencia entre skills de un bloque.
- Cargar un bloque entero en el contexto de un agente cuando conviene más que cargar las skills una a una.

Solo contienen las reglas: los ejemplos, los criterios de decisión, los checklists y la tabla de Enforcement están en cada skill.
