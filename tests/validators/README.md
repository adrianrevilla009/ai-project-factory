# validators

Las pruebas de los validadores de [`factory/validators/`](../../factory/validators/README.md) y de las definiciones de agentes y comandos.

| Fichero | Qué cubre |
|---|---|
| `test_validators.py` | Cada validador con un caso que **debe fallar** y otro que **debe pasar**: estructura de skills, afirmaciones sobre AWS, esquemas y ADR, catálogo MCP, enlaces de `knowledge/`, mapa de módulos, bloques de código, referencias cruzadas y README. Incluye la comprobación de que el índice generado está al día |
| `test_agents.py` | Cada agente y cada comando: frontmatter válido, herramientas conocidas, skills citadas que existen, reglas comunes presentes, revisores sin permisos de escritura y roles de negocio sin shell, y comandos que remiten a agentes reales y mantienen las reglas de gate |

Además, varias pruebas ejecutan el validador sobre el repositorio real: si alguien rompe una convención (una skill sin sección, una referencia rota), falla `make test` y no solo `make validate`.
