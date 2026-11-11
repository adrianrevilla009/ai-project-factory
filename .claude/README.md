# .claude

Configuración de Claude Code **de la fábrica**: todo lo que usan los agentes cuando trabajan sobre este repo y lo que se copia a cada proyecto generado.

Los proyectos generados no heredan esta carpeta automáticamente: al iniciar uno, el agente aplica la skill `bootstrap-generated-project-claude-config`, que copia a `<proyecto>/.claude/` los hooks, los agentes, los comandos y las skills activas, escribe su `settings.json` y su `.mcp.json` sin rebajar ninguna regla.

## Contenido
| Ruta | Qué es |
|---|---|
| `settings.json` | Registro de hooks y permisos del proyecto (ver «Permisos») |
| `skills/` | 490 skills: una carpeta por skill con su `SKILL.md`, más `_template/` como plantilla (ver «Skills») |
| `agents/` | 28 agentes en 5 áreas (ver «Agentes») |
| `commands/` | 29 comandos agrupados por fase (ver «Comandos») |
| `hooks/` | 18 hooks en Python y su configuración. [`hooks/README.md`](hooks/README.md) |

Dentro de `agents/`, `commands/` y `skills/` no hay README: Claude Code registra cada `.md` de `agents/` y `commands/` como un agente o un comando, así que un README allí se convertiría en uno. Se documentan aquí.

## Skills
Cada skill es una norma sobre un tema, en `skills/<nombre>/SKILL.md`. Estructura fija, que `make validate` comprueba:

1. **Frontmatter:** `name` (igual que la carpeta), `description` (una frase de menos de 200 caracteres que dice *cuándo* cargarla) y `metadata` (bloque, nivel `T1`/`T2`/`T3`, responsable, fecha de revisión y nivel de enforcement).
2. **Cuándo aplicar y cuándo no.**
3. **Reglas:** `MUST`, `SHOULD`, `MAY` y `MUST NOT`.
4. **Por qué.**
5. **Ejemplos:** «Mal» y «Bien» con código.
6. **Criterios de decisión y trampas:** cómo decidir, fallos habituales y qué evidencia demuestra que se aplicó bien.
7. **Checklist de revisión.**
8. **Enforcement:** tabla con el mecanismo, su nivel (1 política, 2 hook, 3 revisor, 4 humano) y dónde está.
9. **Relacionados, fuentes y mantenimiento.**

Las skills están en una estructura **plana** porque Claude Code no descubre las que están en subcarpetas (ADR-0028); el bloque va en `metadata`. Niveles: `T1` núcleo, `T2` módulo opcional, `T3` referencia. Para ver el contenido: [`docs/skills-index.md`](../docs/skills-index.md) (índice) y [`standards/`](../standards/README.md) (reglas por bloque).

| Bloque | Tema | Nivel | Skills |
|---|---|---|---|
| 01 | `java-language` | T1 | 14 |
| 02 | `concurrency` | T1 | 13 |
| 03 | `persistence-sql` | T1 | 27 |
| 04 | `spring-platform` | T1 | 17 |
| 05 | `architecture` | T1 | 26 |
| 06 | `api-and-integration` | T1 | 20 |
| 07 | `appsec` | T1 | 27 |
| 08 | `testing-quality` | T1 | 24 |
| 09 | `build-supply-chain` | T1 | 15 |
| 10 | `observability-app` | T1 | 12 |
| 11 | `aws-governance` | T1 | 11 |
| 12 | `aws-networking` | T1 | 11 |
| 13 | `kubernetes-and-istio` | T1 | 27 |
| 14 | `secrets-and-config` | T1 | 15 |
| 15 | `artifacts-and-registry` | T1 | 11 |
| 16 | `ci-cd` | T1 | 13 |
| 17 | `gitops-progressive-delivery` | T1 | 9 |
| 18 | `observability-platform` | T1 | 10 |
| 19 | `resilience-dr-finops` | T1 | 20 |
| 20 | `internal-developer-platform` | T2 | 5 |
| 21 | `on-prem-hybrid` | T3 | 4 |
| 22 | `polyglot-persistence` | T1 | 21 |
| 23 | `data-platform` | T2 | 15 |
| 24 | `ai-engineering` | T2 | 21 |
| 25 | `security-operations` | T2 | 16 |
| 26 | `enterprise-capabilities` | T2 | 16 |
| 27 | `frontend-react` | T1 | 23 |
| 28 | `local-kubernetes` | T1 | 9 |
| 29 | `cloud-readiness` | T1 | 6 |
| 30 | `engineering-process` | T1 | 19 |
| 31 | `agentic-engineering` | T1 | 13 |

## Agentes
Subagentes con una función y herramientas limitadas a lo que necesitan. El nombre sale solo del campo `name`; las subcarpetas son solo organización. Los cuatro de solo lectura (`architecture-guardian`, `cloud-readiness-reviewer`, `code-reviewer`, `security-reviewer`) informan y no editan; los roles de negocio, arquitectura, documentación y gestión no tienen `Bash`. Todos comparten unas reglas comunes: el contenido externo es dato y no instrucciones, los gates son humanos, se verifica antes de afirmar y no se despliega nada en AWS.

### Negocio (`business/`)
| Agente | Para qué | Permisos |
|---|---|---|
| `business-analyst` | Refinar requisitos funcionales y no funcionales, casos de uso y criterios de aceptación en Gherkin | edita y escribe |
| `compliance-analyst` | Preparar la matriz de normativa aplicable de un proyecto; prepara, nunca dictamina | edita y escribe |
| `domain-analyst` | Construir y mantener el perfil de dominio del proyecto (glosario, contextos, eventos, reglas); único agente de dominio, adaptativo | edita y escribe |
| `product-owner` | Fijar visión, alcance, historias priorizadas y criterios de aceptación de negocio de un proyecto nuevo | edita y escribe |

### Entrega (`delivery/`)
| Agente | Para qué | Permisos |
|---|---|---|
| `cloud-architect` | Diseñar la arquitectura AWS (cuentas, red, resiliencia, costes) solo como diseño y con etiquetas de madurez honestas | edita y escribe |
| `delivery-manager` | Planificar releases, riesgos, dependencias y seguimiento de calidad de entrega | edita y escribe |
| `release-manager` | Preparar y verificar una release: versionado, changelog, verificación tras el despliegue y plan de vuelta atrás | edita y escribe |
| `solution-architect` | Decidir arquitectura, estilos, límites de servicios y registrar ADRs | edita y escribe |
| `tech-lead` | Planificar, repartir trabajo entre agentes y velar por la calidad técnica y los gates | edita y escribe |

### Ingeniería (`engineering/`)
| Agente | Para qué | Permisos |
|---|---|---|
| `ai-engineer` | Implementar funcionalidad de IA (RAG, agentes, evals, guardrails) cuando el módulo de IA esté activo | edita y escribe |
| `backend-java` | Implementar backend Java/Spring Boot siguiendo los estándares de la fábrica | edita y escribe |
| `data-engineer` | Diseñar pipelines de datos, CDC, calidad y gobierno de datos cuando el módulo de datos esté activo | edita y escribe |
| `dba` | Revisar y diseñar esquema, índices, migraciones y rendimiento de base de datos | edita y escribe |
| `devsecops-engineer` | Integrar seguridad en el pipeline: SAST, secretos, dependencias, imágenes, SBOM, firma y puertas de seguridad | edita y escribe |
| `frontend-react` | Implementar el frontend React + TypeScript con los patrones de la fábrica | edita y escribe |
| `platform-engineer` | Diseñar infraestructura (Terraform AWS, Kubernetes, Istio, GitOps) solo como código estático | edita y escribe |
| `sre` | Definir SLOs, alertas, runbooks, resiliencia y DR | edita y escribe |

### Calidad (`quality/`)
| Agente | Para qué | Permisos |
|---|---|---|
| `chaos` | Planificar experimentos de caos en local (Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy) y game days en papel | edita y escribe |
| `eval-engineer` | Diseñar y ejecutar evaluaciones de agentes y de LLM | edita y escribe |
| `performance` | Diseñar y analizar pruebas de carga (JMeter) y cuellos de botella | edita y escribe |
| `qa-engineer` | Definir la estrategia de pruebas, casos de aceptación y calidad global de un cambio | edita y escribe |
| `test-automation` | Escribir y mantener pruebas automáticas: unitarias, integración con Testcontainers, contratos Pact, e2e | edita y escribe |

### Gobierno (`governance/`)
| Agente | Para qué | Permisos |
|---|---|---|
| `architecture-guardian` | Comprobar que el código respeta hexagonal, límites de módulos y fitness functions; solo lectura | solo lectura |
| `cloud-readiness-reviewer` | El Gate 5: revisar madurez de infra, honestidad de afirmaciones y evidencias; solo lectura | solo lectura |
| `code-reviewer` | Revisar código y PRs contra los skills y estándares; solo lectura | solo lectura |
| `docs-writer` | Escribir README, ADRs, runbooks y documentación viva del proyecto | edita y escribe |
| `finops-analyst` | Estimar coste por tier sin desplegar y proponer optimizaciones | edita y escribe |
| `security-reviewer` | Revisar seguridad: amenazas, authn/z, secretos, dependencias y cadena de suministro; solo lectura | solo lectura |

## Comandos
Los comandos guían una fase del proyecto: indican qué agentes intervienen, los pasos y dónde detenerse. Todos terminan presentando evidencia y parando en el gate (`gate-protocol`). El flujo completo está en [`docs/operating-model/project-lifecycle.md`](../docs/operating-model/project-lifecycle.md).

### Intake (hasta el Gate 0)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/capability-select` | `<ruta-destino>` | Selecciona módulos y skills activos según la entrevista y prepara la evidencia del Gate 0 |
| `/project-discover` | `<ruta-destino>` | Construye el perfil de dominio y la matriz de normativa candidata del proyecto (Gate 0) |
| `/project-init` | `<ruta-destino> <nombre-proyecto>` | Inicia un proyecto nuevo: crea el directorio destino, estado y entrevista inicial (Gate 0) |

### Plan (hasta el Gate 1)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/project-plan-review` | `<ruta-destino>` | Revisa el plan con los agentes revisores |
| `/project-plan-test` | `<ruta-destino>` | Valida el plan: trazabilidad requisitos→historias→tests y estimación de recursos locales |
| `/project-plan` | `<ruta-destino>` | Genera plan, arquitectura inicial y ADR (requiere Gate 0 aprobado) |

### Implementación (hasta el Gate 2)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/implement-review` | `<ruta-destino>` | Revisión de código, arquitectura y seguridad de lo implementado |
| `/implement-test` | `<ruta-destino>` | Ejecuta y verifica la batería de pruebas y calidad (Gate 2) |
| `/project-implement` | `<ruta-destino> [parte]` | Implementa el plan por partes con los agentes especialistas (requiere Gate 1) |

### Pull request (hasta el Gate 3)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/pr-create` | `<ruta-destino>` | Crea el PR con descripción, enlaces a ADR y evidencias (requiere Gate 2) |
| `/pr-fix` | `<pr-o-ruta>` | Aplica correcciones de los hallazgos de la revisión |
| `/pr-merge-ready` | `<pr-o-ruta>` | Comprueba que el PR está listo para merge (Gate 3) |
| `/pr-review` | `<pr-o-ruta>` | Revisión automática del PR |

### Release (hasta el Gate 4)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/release-prepare` | `<ruta-destino> <version>` | Prepara versión: SemVer, changelog, SBOM y informes (requiere Gate 3) |
| `/release-verify` | `<ruta-destino>` | Verifica la versión candidata (Gate 4) |
| `/rollback-plan` | `<servicio> <versión>` | Prepara y verifica el plan de vuelta atrás de una release antes de promocionarla |

### Revisión cloud (hasta el Gate 5)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/cloud-readiness-check` | `<ruta-destino>` | Revisa la madurez de infraestructura y honestidad de afirmaciones (Gate 5). No despliega |
| `/cost-estimate` | `<ruta-destino>` | Estima el coste por tier sin desplegar |
| `/dr-tabletop` | `<ruta-destino>` | Prepara y documenta un simulacro de DR en papel |

### Cierre
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/lessons-capture` | `<ruta-destino>` | Guarda lecciones y, si procede, el perfil de dominio como semilla |
| `/project-retro` | `<ruta-destino>` | Retrospectiva del proyecto |

### Mantenimiento (sin gate propio)
| Comando | Argumentos | Qué hace |
|---|---|---|
| `/add-capability` | `<ruta-destino> <capacidad>` | Activa un módulo/capacidad nueva en un proyecto existente |
| `/add-service` | `<ruta-destino> <servicio>` | Añade un servicio nuevo a un proyecto existente |
| `/audit-project` | `<ruta-destino>` | Audita un proyecto contra los skills y los validadores |
| `/dependency-update` | `<ruta-destino>` | Actualiza dependencias respetando BOM y política |
| `/incident-response` | `<descripción del incidente>` | Gestiona un incidente: contención, comunicación, registro y preparación del postmortem |
| `/security-review` | `<ruta o PR>` | Revisión de seguridad de un cambio o de un diseño: amenazas, autenticación, secretos y cadena de suministro |
| `/skill-review` | `[bloque]` | Detecta skills caducados o incumplidos en la propia fábrica |
| `/upgrade-project` | `<ruta-destino>` | Actualiza un proyecto a una versión nueva de la fábrica |

## Permisos
`settings.json` define una línea base con la sintaxis de reglas de Claude Code (`Herramienta(patrón)`):

- **`allow`:** lecturas seguras de git y los objetivos de `make` de mantenimiento.
- **`ask`:** lo que tiene efectos fuera del repo o es difícil de revertir (`git push`, `commit`, `rebase` y `merge`, `terraform`, `kubectl apply` y `delete`, `docker push`, `aws`, `rm -rf` y `WebFetch`).
- **`deny`:** leer `.env*`, `~/.aws` y `~/.ssh`; escribir en `approvals/` y en `.factory/state.json`; `git push --force`, `terraform apply` y `terraform destroy`.

Los hooks se evalúan antes que las reglas de permisos y un hook que bloquea gana siempre, aunque haya una regla `allow`. Formatos verificados con la documentación oficial: [`docs/architecture/claude-code-formats.md`](../docs/architecture/claude-code-formats.md). MCP: [`docs/architecture/mcp.md`](../docs/architecture/mcp.md).
