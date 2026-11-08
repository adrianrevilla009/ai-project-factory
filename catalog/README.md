# catalog

Datos que consultan agentes y hooks. Son YAML/Markdown versionados, no código.

| Fichero | Para qué sirve | Quién lo lee |
|---|---|---|
| `adr/` | 38 decisiones de arquitectura de la fábrica (0001–0027 son D1–D27 del brief). Ver su [README](adr/README.md). | Personas, validador de ADRs |
| `skills-inventory.yaml` | Lista maestra de skills por bloque, con tier (T1/T2/T3). | `build_index.py`, validadores |
| `forbidden-libraries.yaml` | Dependencias vetadas y motivo (Lombok, etc.). | hook `forbidden_deps` |
| `approved-libraries.yaml` | Librerías aprobadas por categoría. | agentes, `dependency-update` |
| `resilience-tiers.yaml` | Objetivos de RTO/RPO y redundancia por tier. | skills de resiliencia y DR |
| `parity-matrix.yaml` | Qué servicio AWS se sustituye por qué componente local y qué no reproduce. | skills AWS, gate 5 |
| `tech-radar.yaml` | Tecnologías en adopt/trial/assess/hold. | `solution-architect` |
| `golden-paths/` | Recorridos recomendados de extremo a extremo, como listas ordenadas de skills. | agentes de planificación |

Los números y versiones concretos de estos ficheros están sin verificar salvo que se indique lo contrario.
