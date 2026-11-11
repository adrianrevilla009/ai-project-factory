# maven-enforcer

Un ejemplo de configuración de `maven-enforcer-plugin` para el `pom` padre de un proyecto generado: hace que el build **falle** si aparece una dependencia prohibida o si se usa una versión de Maven o de Java inferior a la acordada.

**Estado: ejemplo sin ejecutar.**

| Fichero | Qué impone |
|---|---|
| `banned-dependencies.example.xml` | Dependencias prohibidas, derivadas de [`catalog/forbidden-libraries.yaml`](../../catalog/README.md) (la fuente de verdad: si cambia el catálogo, cambia esto), y versiones mínimas de Maven y de Java |

Skills de origen: `enforcer-rules` y `no-lombok`. La versión del plugin la fija el BOM del proyecto.

La misma lista de librerías prohibidas se hace cumplir además con el hook `forbidden_deps` al editar el fichero de dependencias y con la regla Semgrep `java-no-lombok`.
