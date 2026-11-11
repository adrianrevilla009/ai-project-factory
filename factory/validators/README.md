# validators

Los comprobadores automáticos de la fábrica. `run_all.py` los ejecuta todos, imprime cada hallazgo con su fichero y falla si hay algún error; es lo que corre `make validate`, el pre-commit y el CI. Se prueban en [`tests/validators/`](../../tests/validators/README.md).

## Qué comprueba cada uno
| Módulo | Qué valida |
|---|---|
| `skill_structure.py` | Cada skill tiene el frontmatter correcto (`name` igual a la carpeta, `description` corta, nivel y fecha válidos), todas las secciones obligatorias, ejemplos de código y una tabla de Enforcement con un mecanismo real |
| `honest_claims.py` | Rechaza afirmaciones como «listo para producción en AWS» o «probado en AWS» y exige una etiqueta de madurez en las carpetas con Terraform. Una línea puede excluirse con el marcador `honest-claims: ignore` al citar un mal ejemplo |
| `schemas_and_adrs.py` | Los esquemas JSON y YAML son válidos; existen los ADR 0001–0027; el catálogo de servidores MCP es coherente (roles y skills reales, versiones fijadas, sin credenciales literales); los enlaces de `knowledge/` y de los golden paths apuntan a skills y ADR existentes; y el mapa de módulos cubre todos los que activa la entrevista |
| `references.py` | Las referencias cruzadas entre skills (`Relacionados`, «ver `skill`») apuntan a skills, agentes o comandos reales, y las rutas de la fábrica que citan existen salvo que la fila diga «pendiente» |
| `code_blocks.py` | Los bloques de código de las skills son sintácticamente válidos: YAML, JSON, XML, Python, HCL (con `terraform fmt`, si está instalado) y bash. Java y TypeScript no se comprueban porque son fragmentos ilustrativos con `...` |
| `readmes.py` | Todas las carpetas principales tienen un README con contenido real, las cifras que citan los documentos (skills, agentes, comandos, hooks, ADR, gates) coinciden con el repositorio y los enlaces relativos no están rotos |
| `common.py` | Utilidades compartidas: la clase de hallazgo y el recorrido de ficheros |
| `run_all.py` | Ejecuta todos los anteriores. `make validate` añade la comprobación de que el índice y los estándares generados están al día (`build_index.py --check`) |

## Cómo se añade un validador
1. Un módulo con una función `validate_all(root)` que devuelva una lista de hallazgos (`Finding`) y un `__main__` para ejecutarlo solo.
2. Regístralo en `run_all.py`.
3. Añade sus pruebas con un caso correcto y otro que deba fallar.
4. Documéntalo en la tabla de arriba.

Un validador debe fallar solo por algo que de verdad sea un error: un aviso ignorado por ruido acaba desactivando el control.
