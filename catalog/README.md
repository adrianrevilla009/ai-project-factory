# catalog

Los datos de referencia que consultan los agentes, los hooks y los validadores. Son YAML y Markdown versionados, no código: cambiarlos cambia lo que la fábrica exige.

## Contenido
| Fichero o carpeta | Qué contiene | Quién lo usa |
|---|---|---|
| [`adr/`](adr/README.md) | Las 38 decisiones de arquitectura de la fábrica. 0001–0027 son las D1–D27 del brief | Personas y agentes (contexto); el validador comprueba que existan |
| `skills-inventory.yaml` | La lista maestra de skills: 31 bloques, 490 skills y el nivel (`T1`, `T2`, `T3`) de cada bloque | `build_index.py` (índice y estándares) y los validadores |
| `forbidden-libraries.yaml` | Dependencias vetadas con el motivo y la alternativa: Lombok, Log4j 1.x, Commons Collections 3, Joda-Time y Moment.js | Hook `forbidden_deps` y Maven Enforcer |
| `approved-libraries.yaml` | Librerías de partida por categoría (Java y frontend). **Sin versiones:** las fija el BOM de cada proyecto | Agentes y `/dependency-update` |
| `resilience-tiers.yaml` | Los tiers de resiliencia 0–3 con su estrategia, RPO, RTO y uso; el defecto es el tier 1; regiones primaria y secundaria; reglas por componente | Skills de resiliencia y DR, `/cost-estimate` |
| `parity-matrix.yaml` | Qué componente local sustituye a cada servicio de AWS (12 filas) y qué **no** reproduce | Skills de AWS y de Kubernetes local, Gate 5 |
| `tech-radar.yaml` | Tecnologías en `adopt`, `trial`, `assess` o `hold` con el ADR que las respalda | `solution-architect` |
| `mcp-servers.yaml` | Los 11 servidores MCP candidatos para proyectos generados: propósito, origen, acceso, credenciales, roles y skills | Bootstrap del proyecto; lo valida `make validate` |
| [`golden-paths/`](golden-paths/README.md) | Recorridos recomendados de extremo a extremo, como listas ordenadas de skills | Agentes de planificación |

## Reglas para cambiarlo
- **Cada cambio se justifica**: si cambia una decisión, con un ADR; si añade una librería prohibida o un servidor MCP, con el motivo en el propio fichero.
- **Sin versiones concretas de terceros** salvo que estén verificadas y fechadas; las versiones viven en el BOM del proyecto (skill `bom-management`).
- **Todo lo que citan debe existir:** `make validate` comprueba, entre otros, que los roles y skills del catálogo MCP sean reales, que sus versiones estén fijadas y que no haya credenciales literales.
- Los cambios se anotan en el `CHANGELOG`.

## Relación con otras carpetas
Las skills explican la norma y el catálogo guarda los datos que la hacen cumplir. Por ejemplo, la skill `no-lombok` es la norma, `forbidden-libraries.yaml` son los datos y el hook `forbidden_deps` es el mecanismo.
