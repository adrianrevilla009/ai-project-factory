# AI Project Factory — Brief de contexto para Claude Code

> **Nota de vigencia (2026-11-09).** Este brief es el documento de partida. Desde entonces el alcance cambió: la fábrica es solo de guías, sin plantillas, CLI, orquestador ni servidores MCP propios (ADR-0038); las skills están en estructura plana (ADR-0028); las decisiones abiertas del §3 están cerradas en los ADR 0032–0037; y la antigua marca de «pendiente de verificar» ya no existe: lo no comprobable se declara «no comprobado». Para el estado real, ver `README.md`, `catalog/adr/` y `CHANGELOG.md`.


> Documento de traspaso. Resume las decisiones tomadas en la fase de planificación con el usuario.
> **Objetivo:** montar el repositorio "fábrica" que, a partir de un dominio y unos requisitos, permita generar proyectos corporativos de gran escala, de calidad profesional, con agentes, skills, hooks, plantillas y gates humanos.
> **Estado actual:** solo planificación. No existe nada creado todavía.

---

## 0. Cómo debes usar este documento (instrucciones para Claude Code)

1. **Lee todo antes de crear nada.** Después, propón un plan de la Oleada 0 (sección 12) y espera aprobación humana.
2. **Empieza SOLO por la Oleada 0.** No escribas el contenido de los ~300 skills de golpe. El inventario (sección 7) es un mapa, no una orden de generación.
3. **No inventes versiones, flags ni APIs.** Verifica contra la documentación oficial vigente: versiones de Java, Spring Boot, Hibernate, Istio, Kubernetes, Terraform y proveedores, y sobre todo **el formato actual de configuración de Claude Code** (hooks, frontmatter de subagentes, ubicación y formato de skills, `.mcp.json`, permisos). Si algo no se puede verificar, márcalo como `TODO-VERIFY` en el archivo.
4. **Honestidad ante todo.** Nada en la fábrica puede afirmar que algo funciona en AWS real: no se va a desplegar (ver sección 3, decisión D4 y sección 4.6).
5. **Commits pequeños y atómicos**, con Conventional Commits. Una pieza por commit.
6. **Los gates humanos son sagrados.** Al terminar cada fase, detente y pide revisión. No avances por tu cuenta.
7. Todo contenido normativo/legal se trata como **borrador por confirmar**, con fuente oficial y fecha de verificación. Nunca de memoria.
8. Idioma: documentación humana en **español**; identificadores, nombres de archivo y código en **inglés**.

---

## 1. Propósito y alcance

Hay **dos capas distintas**, no hay que confundirlas:

```
CAPA 1: LA FÁBRICA (este repositorio)
  Estándares, skills, agentes, prompts, hooks, MCPs, plantillas, validadores, aplicación de referencia.
        │  genera
        ▼
CAPA 2: PROYECTOS GENERADOS
  El producto final (backend Java, frontend React, infra, docs...) + su propia configuración de agentes
  (.claude/, CLAUDE.md, hooks) para que los agentes sigan trabajando bien dentro de cada proyecto.
```

El repositorio es, esencialmente, **una colección enchufable de buenas prácticas** (skills) más la maquinaria para aplicarlas de forma repetible: entrevista → selección de módulos → generación determinista → implementación por agentes especialistas → revisión → gates humanos.

La fábrica es un **producto**: tiene dueño, versiones, changelog y los proyectos generados apuntan a una versión concreta de ella.

**Resultado esperado de un proyecto generado:** que un revisor externo, en un cuarto de hora, vea una aplicación end-to-end muy bien montada: se levanta en local con un comando, con datos de demo, dashboards, documentación, ADRs, informes de calidad/seguridad y la infraestructura AWS preparada (no desplegada).

---

## 2. Principios rectores

1. **Todo lo que afecta al comportamiento** (código, datos, configuración, prompts, modelos) es versionado, reproducible y auditable.
2. **Determinista donde se pueda, LLM donde haga falta.** El esqueleto (≈80 %) sale de plantillas (Copier). El LLM rellena lo variable (lógica de negocio, adaptación, documentación).
3. **Si una regla se puede comprobar con un script, no es un prompt.** Va a hooks, policies o tests. Los skills son para lo que requiere criterio.
4. **Humano en el bucle** en cada gate. Los agentes aceleran, no sustituyen la responsabilidad.
5. **Local primero, cloud preparado y verificado sin gastar.**
6. **Núcleo portable, adaptadores en los bordes** (arquitectura hexagonal): el dominio no conoce AWS ni ninguna herramienta concreta.
7. **Construir por capas.** Estructura pensada completa, piezas activadas por fases.
8. **La fábrica se testea a sí misma**, incluida una aplicación de referencia viva.

---

## 3. Decisiones cerradas

| # | Tema | Decisión |
|---|---|---|
| D1 | Lenguaje primera versión | **Java** (LTS vigente, verificar) con Spring Boot |
| D2 | Build | **Maven** multi-módulo con parent POM y **BOM corporativo** |
| D3 | Nube | **AWS**, diseñada **resiliente**: multi-AZ, multi-región, DR |
| D4 | Despliegue real en AWS | **NO se despliega nunca**, ni en sandbox. Local real + AWS diseñado y validado estáticamente |
| D5 | Entorno local | **Kubernetes local** (kind o k3d; elegir uno y fijarlo en un ADR), no Docker Compose |
| D6 | Regiones AWS | **eu-west-1 (principal) y eu-central-1 (secundaria)**, parametrizadas en Terraform. Verificar disponibilidad de todos los servicios en ambas |
| D7 | Tier de resiliencia por defecto | **Warm standby**; activo-activo solo por petición explícita |
| D8 | IaC | **Terraform** (módulos, entornos por cuenta) |
| D9 | Service mesh | **Istio** (decidir sidecar vs ambient en ADR) |
| D10 | Secretos / cifrado | **Vault de código abierto, un clúster independiente por región** (sin replicación Enterprise). Variante Enterprise solo como documentación opcional. Registrar ADR sobre licencia (BUSL) y alternativa OpenBao |
| D11 | Configuración | **GitOps + Vault** por defecto. **Spring Cloud Config Server = módulo opcional** con guía de decisión |
| D12 | Identidad | **Keycloak** (BD en Aurora Global; en failover se asume reinicio de sesión) |
| D13 | Persistencia | **Políglota por defecto: SQL + NoSQL.** Aurora PostgreSQL (estado) + **DynamoDB (event store / clave-valor)**. OpenSearch (búsqueda/logs analíticos) y Redis (caché) como módulos |
| D14 | Patrones de datos | **Outbox** y **Event Sourcing** son patrones de primera clase (ver 4.5) |
| D15 | Frontend | **React + TypeScript** con su propio bloque de patrones |
| D16 | Artefactos / registro | **Sin licencias de pago.** Puerto neutro `artifact-repository-port`: **Harbor** (imágenes/charts) + repositorio Maven/npm gratuito (evaluar Nexus Community o Reposilite). Artifactory = adaptador opcional |
| D17 | Escaneo y SBOM | **Trivy + Grype + OWASP Dependency-Check**; **CycloneDX** + **Dependency-Track**. Xray = opcional |
| D18 | Contenedores | **Docker multi-stage**, imágenes mínimas, no-root, FS de solo lectura |
| D19 | Testing | **Testcontainers, Pact (+Pact Broker), JMeter, Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy, WireMock, ArchUnit, PIT**; LocalStack para lo emulable |
| D20 | CI | **GitHub Actions** (reutilizable, OIDC, acciones fijadas por SHA) |
| D21 | GitOps / entrega | **Argo CD + Argo Rollouts** (Flux y Spinnaker como T3) |
| D22 | Observabilidad | **OpenTelemetry + Prometheus + Grafana + Loki + Tempo**; SLOs y dashboards como código |
| D23 | Políticas | **OPA/Conftest + Kyverno**; Checkov/Trivy para IaC; Semgrep para código |
| D24 | Agentes de dominio | **Uno solo, adaptativo** (`domain-analyst`), que lee un *perfil de dominio* por proyecto. **No** un agente por sector |
| D25 | Normativa | **Marco que se rellena según el dominio**, no contenido fijo. Un solo `compliance-analyst` |
| D26 | Entorno de trabajo | **Dev containers** para aislar la ejecución, con firewall de salida (allowlist) |
| D27 | Lombok | **Prohibido** (usar records y builders explícitos) |

**Decisiones abiertas (no inventar; proponer opciones en ADR y pedir confirmación):**
- Istio sidecar vs ambient.
- CNI en EKS: VPC CNI vs Cilium (compatibilidad con Istio).
- kind vs k3d.
- Repositorio Maven/npm gratuito concreto.
- SPA (Vite) vs SSR (Next.js) por defecto en React.
- Si se incluye, desactivado por defecto, un `terraform plan` contra una cuenta AWS vacía (sin crear recursos) como comprobación adicional. Requiere credenciales de solo lectura. **Por defecto: NO.**

---

## 4. Reglas de diseño transversales

### 4.1 Niveles de skill

- **T1 · Núcleo:** va en todo proyecto generado.
- **T2 · Módulo:** solo si la entrevista lo activa (datos, IA, capacidades enterprise, operaciones de seguridad…).
- **T3 · Referencia:** conocimiento de repaso/radar sin plantilla; se promueve si un proyecto real lo pide.

### 4.2 Anatomía obligatoria de cada skill

Cada skill es una carpeta con `SKILL.md` (+ `references/` y `examples/`). El `SKILL.md` contiene:

1. **Cuándo aplicar y cuándo no.**
2. **Reglas** (MUST / SHOULD / MUST NOT).
3. **Por qué** (el razonamiento, para poder discutirlo).
4. **Ejemplos bueno/malo** en código real.
5. **Checklist de revisión.**
6. **Enforcement:** cómo se comprueba automáticamente (regla ArchUnit, Semgrep, hook, policy OPA/Kyverno, test) o si es revisión humana.
7. **Skills relacionados, fuentes, dueño, fecha de última revisión, nivel (T1/T2/T3).**

La descripción (frontmatter) debe ser **corta y precisa**, para que el agente cargue solo los skills relevantes. Un skill sin ningún mecanismo de enforcement es una sugerencia, no un estándar.

### 4.3 Cuatro niveles de enforcement

1. **Policy-as-code / plugin de build** (determinista, bloquea el CI).
2. **Hook del agente** (determinista, en tiempo de edición).
3. **Agente revisor** (requiere criterio).
4. **Humano en el gate.**

### 4.4 Conexión skill → resto del sistema

Un skill no vive aislado: alimenta hooks, policies, catálogo y plantillas. Mantener este mapeo explícito. Ejemplos:

| Regla | Skill | Catálogo/Policy | Hook | Plantilla |
|---|---|---|---|---|
| No Lombok | `no-lombok` | `forbidden-libraries` + Enforcer | `forbidden-deps` | POM sin Lombok |
| Sin N+1 | `n-plus-one` | test que cuenta queries | `require-green-tests` | base de tests de repositorio |
| Sin concatenar SQL | `sql-injection-prevention` | regla Semgrep | PostToolUse lint | — |
| BOM y versiones | `bom-management` | `catalog/bom` | `forbidden-deps` | parent POM |
| Hexagonal | `hexagonal` | tests ArchUnit | `architecture-guard` | layout de paquetes |
| Probes y límites K8s | `workload-baseline` | política Kyverno/OPA | — | chart base |
| SBOM y firma | `supply-chain` | política de CI | — | workflow de Actions |
| Gate humano | `gate-protocol` | `approval-record.schema` | `enforce-gate-approval` | `.claude/` del proyecto |

### 4.5 Persistencia: reglas de oro

- **Cada agregado tiene UNA única fuente de verdad.**
- **Outbox:** el estado vive en Postgres; el evento se guarda en la **misma transacción** en una tabla outbox y se publica después (Debezium o publicador propio). Atomicidad *dentro de una sola BD*.
- **Event sourcing:** el almacén de eventos (DynamoDB) **es** la fuente de verdad; se publica desde el propio almacén (Streams). Se usa solo donde los eventos son el negocio (saldos, pólizas, expedientes, pedidos con historia).
- **Prohibido:** la doble escritura "a la vez" en Postgres y NoSQL. No es atómica.
- Event sourcing **no es lo mismo que auditoría**: para auditar basta un audit trail inmutable, más barato. El skill de decisión debe ayudar a elegir.
- **Multi-región con DynamoDB Global Tables:** replicación asíncrona; el control de concurrencia por versión solo protege dentro de una región → fijar **región de escritura por agregado/tenant**. Verificar contra la documentación vigente de AWS si existe opción de consistencia fuerte multi-región.
- Proyecciones (Postgres, OpenSearch) se alimentan de eventos. Cifrado por sujeto y destrucción de claves para GDPR en eventos inmutables.

### 4.6 Madurez de la infraestructura AWS (honestidad obligatoria)

Como **no se despliega**, la madurez máxima es el nivel 2:

1. **Definido:** existe el código.
2. **Validado estáticamente:** pasa `terraform validate`, tflint, formato, escaneo de IaC (Checkov/Trivy), políticas OPA sobre el plan, tests con proveedores simulados.

(Los niveles "probado en sandbox" y "probado en producción" **no existen** en esta fábrica.)

- Cada componente de infra lleva su etiqueta de madurez en su documentación.
- La documentación dice **"preparado para AWS, no verificado en real"**.
- El validador de la fábrica **rechaza** afirmaciones como "listo para producción en AWS".
- Riesgo asumido y a documentar en el README: el código puede fallar la primera vez que se aplique (permisos, límites de cuenta, orden de dependencias). Mitigación: versiones de proveedores fijadas, políticas estrictas, advertencia visible.
- Entregable de valor: **informe de coste estimado sin desplegar** (Infracost o equivalente sobre el plan) por cada tier.

### 4.7 Normativa y dominio: se descubren, no se hardcodean

- **`domain-framework/`**: cómo se construye el *perfil de dominio* de cada proyecto (glosario, actores, procesos, contextos delimitados, eventos de negocio, reglas, integraciones, riesgos, KPIs, normativa candidata). Cada afirmación lleva fuente o se marca como **supuesto**. Lo valida un experto de negocio en el Gate 0.
- **`compliance-framework/`**: cuestionario de aplicabilidad, esquema de ficha de norma (jurisdicción, disparadores, obligaciones, fuente oficial, **fecha de verificación**, responsable), librería de controles técnicos genéricos, mapeo obligación→control→skill/policy/test→evidencia.
- **El agente prepara, no dictamina.** Un humano de legal/cumplimiento valida en el Gate 0 y queda registrado.
- Las fichas de normas concretas (DORA, ENS, PCI, AI Act, GDPR…) se crean **bajo demanda** como "borradores por confirmar".
- Las normas **activan cosas concretas** (p. ej. residencia de datos → SCP que limita regiones; derecho de supresión + event sourcing → cifrado por sujeto).
- Al cerrar un proyecto, `lessons-capture` puede guardar el perfil de dominio como **semilla reutilizable** en `knowledge/`.

---

## 5. Árbol de carpetas de la fábrica

```
ai-project-factory/
├── CLAUDE.md                       # constitución corta: reglas que nunca se olvidan
├── README.md · CHANGELOG.md · VERSION
├── Makefile                        # make local-up, make gen, make validate, make cloud-check
│
├── .devcontainer/
│   ├── devcontainer.json · Dockerfile · post-create.sh
│   ├── features/
│   └── firewall/                   # allowlist de red de salida
│
├── .mcp.json                       # MCPs habilitados, con permisos mínimos
│
├── .claude/
│   ├── settings.json
│   ├── agents/
│   │   ├── business/               # product-owner · business-analyst
│   │   │                           # domain-analyst (único, adaptativo) · compliance-analyst (único)
│   │   ├── delivery/               # tech-lead · solution-architect · delivery-manager
│   │   ├── engineering/            # backend-java · frontend-react · data-engineer · ai-engineer
│   │   │                           # dba · platform-engineer · sre
│   │   ├── quality/                # qa-engineer · test-automation · performance · chaos · eval-engineer
│   │   └── governance/             # code-reviewer · architecture-guardian · security-reviewer
│   │                               # cloud-readiness-reviewer · finops-analyst · docs-writer
│   ├── commands/
│   │   ├── 00-intake/              # project-init · project-discover · capability-select
│   │   ├── 01-plan/                # project-plan · project-plan-review · project-plan-test
│   │   ├── 02-implement/           # project-implement · implement-review · implement-test
│   │   ├── 03-pull-request/        # pr-create · pr-review · pr-fix · pr-merge-ready
│   │   ├── 04-release/             # release-prepare · release-verify
│   │   ├── 05-cloud-readiness/     # cloud-readiness-check · cost-estimate · dr-tabletop
│   │   ├── 06-close/               # project-retro · lessons-capture
│   │   └── maintenance/            # add-service · add-capability · audit-project
│   │                               # upgrade-project · dependency-update · skill-review
│   ├── skills/                     # 31 bloques (sección 7)
│   └── hooks/
│       ├── session-start/          # carga contexto, perfil de dominio, skills activos
│       ├── pre-tool-use/           # block-secrets · block-forbidden-paths · block-dangerous-commands
│       │                           # enforce-gate-approval · prompt-injection-guard
│       ├── post-tool-use/          # format · lint · architecture-guard · forbidden-deps
│       │                           # update-docs · maturity-label-check
│       ├── stop/                   # require-green-tests · require-docs-updated
│       └── audit/                  # log-actions
│
├── gates/
│   ├── gate-0-intake.md            # incluye validación de perfil de dominio y normativa
│   ├── gate-1-plan.md · gate-2-implementation.md · gate-3-pull-request.md
│   ├── gate-4-release.md · gate-5-cloud-readiness.md
│   ├── checklists/
│   └── approval-record.schema.json
│
├── capabilities/
│   ├── capabilities.yaml           # matriz: qué respuesta activa qué módulo
│   ├── interview/                  # guiones de entrevista
│   └── modules-map.yaml            # módulo → plantilla + skills + policies + tests + dashboards
│
├── catalog/
│   ├── approved-libraries.yaml · forbidden-libraries.yaml
│   ├── bom/                        # BOM corporativo Java y lockfiles npm
│   ├── tech-radar.yaml
│   ├── golden-paths/
│   ├── resilience-tiers.yaml       # tier → estrategia, RPO/RTO, coste
│   ├── parity-matrix.yaml          # AWS ↔ local, qué NO se reproduce
│   └── adr/                        # decisiones de licencia, stack y alternativas
│
├── standards/                      # normativa interna, legible por personas
├── policies/                       # lo mismo, ejecutable
│   ├── opa-conftest/ · kyverno/ · semgrep/ · archunit/
│   ├── frontend-boundaries/        # ESLint y dependency-cruiser
│   └── iac-checks/                 # reglas Checkov/Trivy
│
├── compliance-framework/
│   ├── applicability-questionnaire.yaml
│   ├── regulation-entry.schema.yaml · control-library/
│   ├── obligation-to-control-mapping.schema.yaml
│   ├── templates/ · research-protocol.md
│
├── domain-framework/
│   ├── domain-profile.schema.yaml · discovery-protocol.md
│   ├── assumptions-register.schema · validation-checklist.md
│
├── prompts/                        # system · tasks · review · interviews
│
├── templates/                      # plantillas deterministas (Copier)
│   ├── base/
│   ├── backend-java-spring/        # multi-módulo, parent POM, BOM, hexagonal
│   ├── frontend-react/
│   ├── modules/                    # event-sourcing · outbox · rag · agents · idp-documents
│   │                               # search · workflow · notifications · data-platform · multi-tenant
│   ├── local-k8s/                  # perfiles mínimo/completo, Tilt/Skaffold, datos de demo
│   ├── infra-aws/                  # Terraform: gobierno, redes, EKS, Aurora, DynamoDB, MSK, ECR, DR
│   ├── kubernetes/                 # base + overlays · Helm · Istio · Argo CD / Rollouts
│   ├── ci-cd/github-actions/
│   ├── testing/                    # Testcontainers · Pact · JMeter · chaos · Toxiproxy
│   ├── security/                   # Trivy · Dependency-Track · gitleaks · ZAP
│   ├── observability/              # OTel · Prometheus · Grafana · Loki · Tempo, dashboards y SLO
│   ├── devcontainer/ · claude-config/ · docs/ · compliance/ · domain/
│
├── reference-app/                  # aplicación de referencia viva, generada con la propia fábrica
│   ├── services/ · web/ · infra/ · local/
│   ├── docs/ · reports/            # cobertura, mutación, carga, caos, SBOM, escaneos
│   └── README.md                   # con el estado de madurez de cada pieza
│
├── knowledge/
│   ├── projects-registry/ · lessons-learned/ · domain-profile-seeds/
│   ├── patterns-library/ · anti-patterns/ · decisions-index/
│
├── factory/
│   ├── cli/                        # factory new · upgrade · audit · doctor
│   ├── orchestrator/               # estado de gates y aprobaciones
│   ├── validators/                 # estructura, estándares, madurez, afirmaciones honestas
│   ├── generators/
│   └── mcp-servers/                # component-catalog · standards-lookup · lessons-search
│
├── tests/
│   ├── generated-project-smoke/    # genera, levanta en local y verifica
│   ├── template-matrix/            # combinaciones de módulos
│   ├── skills-vs-reference-app/    # ¿lo que dice cada skill lo cumple la app de referencia?
│   ├── hooks/ · validators/
│   └── agent-evals/                # ¿los agentes respetan reglas y gates?
│
├── docs/                           # arquitectura, adr, operating-model (RACI), onboarding, runbooks
└── .github/                        # workflows de la fábrica, CODEOWNERS, plantillas de PR
```

**Aplicación de referencia viva:** código real, generado por la propia fábrica, que se levanta con un comando y pasa todos los gates en el CI de la fábrica. Cada skill apunta a código real de ella; si un skill dice algo que la referencia no cumple, el CI lo detecta. Sin esto, los skills se pudren.

---

## 6. Flujo con gates humanos

```
 GATE 0        GATE 1       GATE 2          GATE 3        GATE 4       GATE 5               CIERRE
 Intake        Plan         Implementación  Pull Request  Release      Cloud readiness
   │             │              │               │            │              │
 init ─► discover ─► capability-select ─► plan ─► plan-review ─► plan-test ─► 👤
                                              implement ─► impl-review ─► impl-test ─► 👤
                                                      pr-create ─► pr-review ─► pr-fix ─► 👤
                                                                   release-prepare ─► release-verify ─► 👤
                                                              cloud-readiness-check ─► cost-estimate ─► dr-tabletop ─► 👤
                                                                                                   retro ─► lessons-capture
```

- Cada 👤 es un **visto bueno humano registrado** (`approval-record.schema.json`).
- El hook `enforce-gate-approval` impide avanzar sin ese registro: es código, no una petición en un prompt.
- **Gate 0** incluye validar el perfil de dominio (experto de negocio) y la matriz de normativa (legal/cumplimiento).
- **Gate 5** (nuevo) es la preparación para cloud: checklist y estado de madurez de cada componente. **No implica desplegar.**
- Hay que definir en `docs/operating-model/` (RACI) quién aprueba qué en cada gate.

### Flujo de `/project-init` (resumen)

1. Entrevista de requisitos → rellena `capabilities.yaml`, perfil de dominio y matriz de normativa.
2. `architect` produce plan y ADR inicial; punto de control humano.
3. Se seleccionan módulos (`modules-map.yaml`) y skills activos (T1 + T2 elegidos).
4. Copier genera esqueleto base + módulos, con `.claude/` y hooks configurados.
5. Subagentes especialistas implementan por partes; hooks vigilan cada edición.
6. Revisores (`code-reviewer`, `security-reviewer`, `architecture-guardian`) auditan.
7. Validadores y tests deciden pasa/no pasa.

Preguntas de la entrevista que activan capacidades (entre otras): ¿multi-tenant?, ¿búsqueda?, ¿analítica?, ¿documentos/OCR?, ¿chatbot/RAG?, ¿workflow/BPM?, ¿pagos?, ¿notificaciones?, ¿tiempo real?, ¿back-office?, ¿necesita historial completo (event sourcing)?, ¿tier de resiliencia?, ¿frontend?, ¿datos de categorías especiales?

---

## 7. Inventario de skills (mapa de contenido)

Cada línea es un skill (carpeta con `SKILL.md`). Nivel entre paréntesis por bloque.

### 01 · java-language (T1)
modern-java-idioms, immutability-and-value-objects, null-safety, exceptions-and-error-handling, collections-and-streams, equals-hashcode-tostring, time-and-money, strings-encoding-locale, generics-and-api-design, no-lombok, logging-rules, jvm-in-containers, profiling-and-leaks, code-style-and-naming

### 02 · concurrency (T1)
threads-executors-and-pools, virtual-threads, structured-concurrency-and-scoped-values, completablefuture-patterns, java-memory-model, locks-and-synchronization, concurrent-collections, distributed-locking, idempotency-and-deduplication, backpressure-and-bulkheads, scheduling-and-batch, async-and-context-propagation, concurrency-testing

### 03 · persistence-sql (T1)
jpa-entity-design, id-generation, lazy-vs-eager, n-plus-one, joins-and-fetch-joins, projections-and-dtos, query-strategy, sql-injection-prevention, pagination, transactions, isolation-levels-and-anomalies, optimistic-locking, pessimistic-locking, persistence-context-and-flush, batching-and-bulk-ops, caching, connection-pooling, multi-tenancy (discriminador/@TenantId, schema, BD por tenant, RLS, tests de fugas, pools por tenant), auditing-soft-delete-history, schema-migrations (Flyway, expand/contract), indexing-and-query-plans, db-design-conventions, read-replicas-and-routing, partitioning-and-archival, jdbc-and-jooq, db-testing, data-privacy-in-db

### 04 · spring-platform (T1)
project-layout (Spring Modulith), dependency-injection-rules, configuration-properties, controllers-and-validation, error-handling-problem-details (RFC 9457), mapping-mapstruct, spring-data-rules, actuator-and-health, graceful-shutdown-lifecycle, http-clients-and-timeouts, resilience (Resilience4j), domain-events-in-spring, reactive-vs-blocking, startup-and-native, testing-slices, file-upload-and-streaming, upgrade-policy

### 05 · architecture (T1)
hexagonal, clean-architecture, layering-rules-archunit, modular-monolith, microservices-decision-guide, anti-corruption-layer, strangler-fig-migration, bff-and-api-gateway, cell-based-architecture, solid, gof-patterns-in-practice, code-smells-and-refactoring, quality-attributes-atam, ddd-strategic, ddd-tactical, cqrs, event-sourcing, event-driven, sagas-and-process-managers, consistency-and-cap-tradeoffs, scalability-patterns, multi-tenant-architecture, twelve-factor, connascence-and-coupling, evolutionary-architecture-fitness-functions, tech-debt-management

### 06 · api-and-integration (T1)
rest-design-guidelines, openapi-contract-first, api-versioning-deprecation, pagination-filter-sort, idempotency-keys, rate-limiting-quotas, grpc-protobuf, graphql, asyncapi-event-contracts, backward-compatibility-rules, kafka-producers-consumers, schema-registry-and-evolution, dlq-retries-poison-messages, delivery-semantics, rabbitmq-sqs, webhooks, batch-file-sftp-integration, soap-legacy-integration, contract-testing-pact, sdk-generation

### 07 · appsec (T1)
secure-sdlc-nist-ssdf, asvs-mapping, owasp-top10-and-api-top10, threat-modeling-stride, authn-oidc-oauth2, authz-rbac-abac-rebac, jwt-and-sessions, method-and-endpoint-security, input-validation-output-encoding, security-headers-cors-csrf, dos-and-rate-limiting, zero-trust, security-testing-sast-dast, injection-families, deserialization-xxe-ssrf-traversal, file-upload-security, secrets-management, crypto-tls-mtls-key-rotation, pii-and-data-classification, audit-trail-and-security-logging, dependency-security, supply-chain (SBOM, SLSA, cosign), container-and-k8s-security, cloud-iam-least-privilege, llm-security, vulnerability-sla-and-incident-response

### 08 · testing-quality (T1)
test-strategy, tdd, bdd, unit-testing-java, integration-testing-testcontainers, localstack-aws, wiremock-and-stubbing, api-testing, architecture-testing-archunit, contract-testing, static-analysis (Checkstyle, PMD, SpotBugs, Error Prone, quality gates), code-review-guidelines, mutation-testing (PIT), property-based-testing (jqwik), flaky-test-management, test-data-management, coverage-policy, performance-testing (JMeter: baseline, soak, spike), chaos-engineering (Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy, game days), resilience-testing, e2e-testing, canary-analysis-and-synthetic-monitoring

### 09 · build-supply-chain (T1)
maven-multimodule-layout, parent-pom, bom-management, versioning-semver-snapshots, enforcer-rules, dependency-hygiene, renovate-dependabot-policy, reproducible-builds, license-compliance, sbom-generation (CycloneDX), maven-wrapper-and-toolchains, build-caching-and-speed, container-images, jdk-distribution-and-upgrade-cadence, release-automation

### 10 · observability-app (T1)
otel-fundamentals-and-semconv, otel-java-agent-vs-sdk, metrics-micrometer, structured-logging, tracing, jvm-observability, db-and-kafka-observability, golden-signals-red-use, alerting-symptom-based, slo-sli-error-budgets, llm-observability, on-call-and-runbook-links

### 11 · aws-governance (T1, solo diseño)
organization-and-ou-design, control-tower-and-account-factory, identity-center-sso, scp-guardrails, org-cloudtrail-config-securityhub-guardduty, log-archive-and-audit-account, kms-multi-region-keys, tagging-cost-allocation-budgets, break-glass-and-jit-access, compliance-as-code, regions-and-data-residency

### 12 · aws-networking (T1, solo diseño)
cidr-planning-and-ipam, vpc-multi-az-layers, transit-gateway-hub-and-spoke, private-endpoints-and-egress-control, dns-route53-private-and-hybrid, alb-nlb-and-tls-termination, waf-shield-and-cloudfront, global-accelerator-and-failover-routing, eks-networking, flow-logs-and-network-observability, cross-region-connectivity-and-cost

### 13 · kubernetes-and-istio (T1)
cluster-topology, node-pools-and-capacity, workload-baseline (requests/limits, probes, PDB, topology spread, seccomp), namespaces-quotas-multitenancy, rbac-and-service-accounts, pod-security-and-admission, helm-standards, kustomize-overlays, operators (CloudNativePG, Strimzi), autoscaling (HPA, VPA, KEDA), cluster-addons-baseline (cert-manager, external-dns, external-secrets), cluster-upgrades-and-drift, backup-and-restore (Velero), multi-cluster-and-dr, runtime-security (Falco), cost-visibility (OpenCost), gateway-api,
istio/: sidecar-vs-ambient-decision, mtls-strict-and-peer-auth, authorization-policies, traffic-management, ingress-and-egress-gateways, canary-and-traffic-splitting, multi-cluster-mesh, mesh-observability (Kiali), mesh-vs-app-resilience (no duplicar reintentos), istio-upgrades-and-ops

### 14 · secrets-and-config (T1)
vault/: deployment-ha (Raft, auto-unseal, un clúster por región), auth-methods, policies, dynamic-database-credentials, pki-and-cert-issuance, transit-encryption, injection-patterns (VSO/agent/CSI), rotation-and-leases, audit-and-break-glass, vault-and-keycloak-dr,
config-by-environment, spring-cloud-config-module (opcional), feature-flags-openfeature, envelope-encryption-and-kms, secret-scanning-and-leak-response

### 15 · artifacts-and-registry (T1)
artifact-repository-port (contrato: promoción, retención, trazabilidad; adaptadores Harbor/Nexus/Reposilite/Artifactory), promotion-between-environments, retention-and-cleanup, remote-repos-and-dependency-confusion-protection, sbom (CycloneDX, Dependency-Track, VEX), image-scanning (Trivy/Grype), image-signing-and-provenance (cosign, SLSA), admission-verification, docker-multistage (stage-layout, minimal-runtime-images, non-root-readonly-fs, layer-cache, labels, multi-arch), license-policy, third-party-risk

### 16 · ci-cd (T1)
pipeline-architecture, github-actions (reusable-workflows, oidc-to-cloud, actions-pinning, ephemeral-runners, caching-and-matrices, environments-and-approvals), quality-gates, security-gates, contract-gate (Pact can-i-deploy), performance-gate, database-migration-step, ephemeral-preview-environments, release-versioning-changelog, deployment-verification-and-smoke, rollback-strategy, pipeline-observability-and-dora, alternatives (GitLab CI, Jenkins — T3)

### 17 · gitops-progressive-delivery (T1)
repo-strategy, argo-cd (ApplicationSets, proyectos y RBAC, sync waves, notificaciones), argo-rollouts (canary/blue-green con análisis), argo-workflows-and-events, drift-and-self-heal-policy, secrets-in-gitops, environment-promotion, flux-comparison (T3), spinnaker-comparison (T3)

### 18 · observability-platform (T1)
collector-pipelines, metrics-store-ha-retention, logs-and-traces-stores, multi-tenant-observability, alert-routing-and-oncall, dashboards-and-slos-as-code, status-page-and-comms, cardinality-and-cost-governance, observability-of-the-platform-itself, tempo-and-service-graphs

### 19 · resilience-dr-finops (T1, solo diseño)
tier-model-and-rpo-rto, multi-az-patterns, multi-region-patterns, data-replication-matrix, failover-and-failback-runbooks, application-recovery-controller-and-health-checks, static-stability-and-cell-architecture, backup-vault-immutability-and-restore-tests, fault-injection-and-game-days (en papel/tabletop), resilience-hub-assessments, eks-multi-region-and-argo-cd-multicluster, istio-multicluster-tradeoffs, dependency-mapping-and-blast-radius, finops-of-resilience, slo-error-budget-policy, capacity-and-load-modeling, incident-management-and-postmortems, change-and-release-management, load-shedding-and-degradation, finops (presupuestos, anomalías, rightsizing, coste unitario)

### 20 · internal-developer-platform (T2)
backstage (catálogo, scorecards, TechDocs), software-templates, golden-paths-governance, ephemeral-environments, developer-experience-metrics

### 21 · on-prem-hybrid (T3)
kubernetes-on-prem, storage-and-load-balancing, private-registry, hybrid-identity-and-networking

### 22 · polyglot-persistence (T1)
datastore-selection-guide, polyglot-operations-cost, dynamodb-data-modeling, dynamodb-event-store, global-tables-and-write-region-rules, mongodb-alternative (T3), event-sourcing/ (when-to-use-and-when-not, aggregates-and-event-design, event-versioning-and-upcasting, snapshots, projections-and-read-models, rebuilds-and-replays, gdpr-and-immutable-events, testing-event-sourced-systems), outbox-and-cdc, audit-trail-without-event-sourcing, cqrs-read-models-and-search (OpenSearch), consistency-and-sagas, cache-strategies (Redis), data-sync-pitfalls, local-vs-aws-dynamodb-testing (emulador + límites)

### 23 · data-platform (T2)
datastore-selection extendida, cdc-and-streaming, batch-orchestration (Airflow/Dagster), etl-vs-elt-and-dbt, data-lake-and-lakehouse, warehouse-options, data-modeling, data-quality, data-contracts-and-lineage, data-governance-and-classification, access-control-masking-and-retention, gdpr-in-the-lake, bi-and-reporting, feature-store-and-ml-data, data-observability, data-platform-cost

### 24 · ai-engineering (T2)
spring-ai-and-langchain4j, rag-architecture, rag-over-enterprise-docs, prompt-management, agents-and-tool-calling, mcp-servers-in-java, llm-gateway, guardrails-and-pii-redaction, llm-evals, token-and-cost-budgets, structured-outputs-and-streaming, human-in-the-loop, model-risk-and-ai-act-mapping, chatbot-design, intelligent-document-processing (ingesta, OCR, clasificación, extracción, revisión humana), ocr-options, document-management, vector-store-selection, classical-mlops, ai-safety-and-red-teaming, training-data-licensing-and-provenance

### 25 · security-operations (T2)
vulnerability-management-program, penetration-testing-program (solo sobre sistemas propios, con alcance y reglas de compromiso por escrito), dast-and-attack-simulation (ZAP), bug-bounty-and-disclosure, siem-and-detection-engineering, ids-ips-waf-edr, encryption-standards, pki-and-certificate-lifecycle, iam-governance-and-pam, cspm-and-posture (Kubescape, Prowler), hardening-baselines (CIS), incident-response-playbooks-and-forensics, ransomware-resilience, threat-intel-and-risk-register, third-party-and-supply-chain-risk, security-champions-and-training

### 26 · enterprise-capabilities (T2)
identity-and-customer-management, workflow-bpm (Camunda/Flowable), rules-engines, notifications, document-and-report-generation, search-and-discovery, scheduling-and-batch-jobs, import-export-and-bulk-data, payments-and-billing, audit-trail-and-activity-log, back-office-admin-console, consent-and-dsar-management, i18n-and-localization, multi-tenancy-saas-features, integrations-erp-crm, api-productization-and-developer-portal

### 27 · frontend-react (T1)
architecture (por feature, límites de módulos), typescript-strict-rules, rendering-strategy-decision (SPA/Vite vs SSR/Next), state-management (server-state con TanStack Query, client-state Zustand/Redux Toolkit, url-and-form-state), routing-and-code-splitting, forms-and-validation (React Hook Form + Zod), api-client-from-openapi, auth-and-session (OIDC PKCE + patrón BFF con sesión por cookie, tokens fuera de localStorage; la UI oculta, nunca protege), design-system-and-tokens (Storybook), component-patterns (composición, compound components, hooks, render props), error-handling-and-boundaries, accessibility (WCAG 2.2, axe), i18n-and-formatting, performance (Core Web Vitals, bundle budgets), security-frontend (XSS, CSP, dependencias npm), testing (Vitest + Testing Library, MSW, Playwright, visual regression, accesibilidad), observability-frontend (OTel navegador, RUM), build-and-deploy (pnpm, S3 + CloudFront, multi-región, invalidación), supply-chain-npm, feature-flags-ui, realtime (SSE/WebSocket), micro-frontends (T3), pwa-and-offline (T3)

### 28 · local-kubernetes (T1, núcleo del proyecto)
cluster-tooling, dev-loop (Tilt/Skaffold), local-profiles (mínimo: servicio + Postgres + DynamoDB Local; completo: + Kafka, Vault, Istio, observabilidad), aws-emulation (LocalStack, límites), local-parity-matrix, data-seeding-and-demo-data, local-gitops (opcional), resource-budgets, devcontainer-integration

### 29 · cloud-readiness (T1)
static-verification-ladder (validate, tflint, Checkov/Trivy, OPA sobre plan, mock providers), maturity-labels, cost-estimation (Infracost o equivalente), dr-tabletop-exercises, parity-matrix-maintenance, honest-claims-policy

### 30 · engineering-process (T1)
git-workflow (trunk-based), conventional-commits, pr-rules, definition-of-ready-and-done, requirements-engineering (INVEST, Gherkin, NFRs, criterios de aceptación), domain-discovery (event storming), adr, rfc-process, c4-and-arc42, diagrams-as-code, living-readme, api-docs, runbooks, changelog-release-notes, production-readiness-review, risk-register, tech-debt-register, lessons-learned-and-retro, library-selection-and-tech-radar-process

### 31 · agentic-engineering (T1)
skill-authoring-guide, claude-md-authoring, subagent-design, context-budgeting, gate-protocol, prompt-injection-defense-for-agents, mcp-governance, agent-evals, cost-control, parallel-work-and-worktrees, verify-before-asserting, handoff-artifacts-between-agents

---

## 8. Matriz de paridad AWS ↔ local

| AWS | Equivalente local | Qué NO se reproduce |
|---|---|---|
| EKS | kind o k3d | Nodos gestionados, autoscaling real |
| Aurora PostgreSQL | CloudNativePG | Failover global, réplicas Aurora |
| DynamoDB | DynamoDB Local (oficial) o LocalStack | Global Tables fiables, throttling, backups, consistencia eventual; en LocalStack los Streams no funcionan en réplicas (verificar estado actual) |
| MSK | Strimzi (Kafka) | Replicación entre regiones |
| S3 | MinIO | Replicación, Object Lock completo |
| ElastiCache | Redis | Multi-AZ real |
| ALB + Route 53 | Istio gateway (Gateway API) | DNS, balanceo gestionado |
| KMS / Secrets Manager | Vault (modo dev) | Claves multi-región |
| IAM / IRSA | RBAC de Kubernetes | Modelo de identidades AWS |
| CloudWatch | Prometheus + Grafana + Loki + Tempo | Servicios nativos |
| WAF, Shield, CloudFront | — | Nada |
| Multi-región y DR | — | Solo simulacro documental (tabletop) |

Lo que no se reproduce se escribe **explícitamente** en cada skill afectado. Testcontainers sigue siendo necesario para tests de integración; el Kubernetes local ejecuta el sistema completo, no sustituye esos tests.

---

## 9. Resiliencia AWS (diseño)

### Tiers (valores de partida, a validar con negocio)

| Tier | Estrategia | RPO | RTO | Uso |
|---|---|---|---|---|
| 0 | Activo-activo / warm standby con replicación continua | segundos | minutos | Núcleo transaccional crítico |
| **1 (defecto)** | **Warm standby** | ~minutos | < 1 h | Servicios de cara a cliente |
| 2 | Pilot light | < 1 h | horas | Back-office |
| 3 | Backup y restauración | 24 h | 24 h+ | No críticos |

Cada proyecto declara su tier y se activa la infraestructura correspondiente. Principio: **estabilidad estática** (la capacidad secundaria ya está aprovisionada; la conmutación solo requiere acciones de plano de datos).

### Por componente

| Componente | Multi-AZ | Multi-región |
|---|---|---|
| EKS | Nodos en 3 AZ, topology spread, PDB | Clúster gemelo en secundaria (Terraform + Argo CD) |
| Postgres | Aurora Multi-AZ | Aurora Global Database, promoción de la secundaria |
| Event store | DynamoDB | Global Tables, región de escritura por agregado |
| Kafka | MSK 3 AZ | Replicación entre regiones, traducción de offsets |
| Objetos | S3 | Replicación cross-region, versionado, Object Lock |
| Caché | ElastiCache Multi-AZ | Reconstruible o Global Datastore |
| Secretos/claves | Vault Raft 3 AZ | **Un clúster Vault independiente por región**; KMS multi-región |
| Imágenes | Harbor HA | **ECR con replicación cross-region nativa** (función AWS, sin licencia de terceros); el runtime despliega desde ECR, no depende del repositorio de artefactos |
| Identidad | Keycloak HA | BD en Aurora Global; reinicio de sesión asumido en failover |
| Entrada | Route 53, CloudFront, Global Accelerator | Application Recovery Controller |
| Observabilidad | Backends HA | Almacenamiento fuera del dominio de fallo |
| CI/CD e IaC state | Accesibles | Que la región caída no impida desplegar la recuperación |

### Trampas que deben quedar documentadas en skills

- **Vault Transit con clústeres independientes:** el material de claves no se comparte. Los datos que deban leerse desde ambas regiones se cifran con **claves multi-región de KMS** (cifrado de sobre), no con Transit.
- **Credenciales dinámicas de BD:** en Aurora Global la secundaria es de solo lectura hasta promoverse, y Vault no puede crear roles dinámicos allí. El runbook de failover fija un **orden**: primero promover la BD, después activar el motor de BD de Vault.
- **Event sourcing multi-región:** ver 4.5 (región de escritura por agregado).
- **Replicación de Vault, Artifactory y Xray:** son funciones de pago y **no se asumen**. Cualquier skill que las mencione debe presentarlas como variante opcional.

---

## 10. Herramientas de testing y seguridad (por defecto)

| Objetivo | Herramienta |
|---|---|
| Integración con dependencias reales | Testcontainers (Postgres, Kafka, Redis, Keycloak, Vault) |
| Simulación AWS local | LocalStack (solo lo emulable) |
| Contratos | Pact + Pact Broker |
| Carga | JMeter |
| Caos en aplicación | Chaos Monkey for Spring Boot |
| Caos en Kubernetes | Chaos Mesh |
| Fallos de red en tests | Toxiproxy |
| Arquitectura | ArchUnit (Java) · ESLint/dependency-cruiser (frontend) |
| Mutación | PIT |
| SAST | Semgrep, CodeQL, Sonar (si disponible gratis) |
| Secretos en código | gitleaks |
| SCA y contenedores | Trivy, Grype, OWASP Dependency-Check |
| SBOM | CycloneDX + Dependency-Track |
| IaC | Checkov, Trivy, OPA/Conftest |
| DAST | OWASP ZAP |
| Postura de clúster | Kubescape |

Pentesting y ataques simulados: **solo sobre sistemas propios y entornos acordados**, con alcance y reglas de compromiso escritas. Es un skill de *programa*, no un agente que ataca libremente.

---

## 11. Checklist "wow" de un proyecto generado (verificable por el validador)

- `make local-up` levanta todo en Kubernetes local con datos de demo y dashboards ya provisionados.
- README con diagrama C4, mapa de servicios, ADRs y enlaces a cada pieza.
- Portal de API (OpenAPI) y colección de pruebas de ejemplo.
- Informes incluidos y regenerables: cobertura y mutación, carga (JMeter), caos, SBOM, escaneo de vulnerabilidades, políticas aplicadas.
- Runbooks, SLOs y alertas definidos.
- Infraestructura AWS reproducible con Terraform (etiquetada como **validada estáticamente, no desplegada**), GitOps, despliegue progresivo, informe de coste por tier.
- Registro de gates con las aprobaciones humanas.

---

## 12. Plan de ejecución por oleadas

**Oleada 0 — Fundaciones (EMPEZAR AQUÍ y detenerse para revisión):**
1. Estructura de carpetas vacía con `README.md` mínimo en cada directorio principal explicando su propósito.
2. `CLAUDE.md` de la fábrica (corto y preciso).
3. `gates/` con las definiciones de los 6 gates, checklists y `approval-record.schema.json`.
4. `.claude/skills/31-agentic-engineering/`: `skill-authoring-guide`, `gate-protocol`, `claude-md-authoring`, `verify-before-asserting`.
5. Plantilla de skill (anatomía de 4.2) y un **skill de ejemplo completo**: `n-plus-one` (con código bueno/malo, checklist, enforcement).
6. `capabilities/capabilities.yaml` inicial y esquemas de `domain-framework/` y `compliance-framework/`.
7. `catalog/adr/` con los ADRs de las decisiones D1–D27 y las decisiones abiertas como ADRs en estado "propuesto".
8. `.devcontainer/` básico + `Makefile` esqueleto + `.pre-commit-config.yaml`.
9. Hooks mínimos de seguridad (`block-secrets`, `block-dangerous-commands`, `enforce-gate-approval`) con sus tests. **Verificar antes el formato vigente de hooks de Claude Code.**
10. `factory/validators/` con el validador de "afirmaciones honestas" (madurez AWS) y validador de estructura de skills.

**Criterios de aceptación de la Oleada 0:** el repo se clona, `make validate` pasa, los validadores detectan un skill mal formado y una afirmación "listo para producción en AWS", los hooks tienen tests, y todo decisión relevante tiene ADR.

**Oleada 1 — Núcleo Java y calidad + aplicación de referencia mínima:** bloques 01, 03, 07, 08, 09 + hooks/policies asociados + `reference-app` mínima con su CI.
**Oleada 2 — Arquitectura y observabilidad:** 04, 05, 06, 10, 18 + plantillas Java completas.
**Oleada 3 — Plataforma y entrega:** 11–17, 19, 20, 28, 29, plantillas de Terraform/K8s/CI/GitOps, local-k8s completo.
**Oleada 4 — Persistencia políglota y frontend:** 22, 27 + módulos event-sourcing/outbox en la aplicación de referencia.
**Oleada 5 — Módulos T2:** 23, 24, 25, 26 + agentes de negocio y marcos de dominio/normativa completos.

Cada oleada termina con revisión humana antes de la siguiente. La persistencia (03) va en la Oleada 1 porque es donde un error cuesta más caro.

---

## 13. Riesgos conocidos (tenlos presentes)

- **Caducidad de skills:** versiones de Spring, Hibernate, Kubernetes, herramientas. Cada skill lleva fecha de revisión y existe el comando `skill-review` para detectar caducados.
- **Deriva local ↔ AWS:** mitigada con la matriz de paridad y el CI estático. Sin despliegue real, la deriva no se puede medir; por eso la honestidad en el lenguaje es obligatoria.
- **Falsa seguridad del Terraform no aplicado:** puede pasar validación y fallar al aplicar. Documentarlo siempre.
- **Recursos locales:** el perfil completo (Istio, Kafka, Vault, observabilidad) exige mucha memoria; mantener perfil mínimo y presupuesto de recursos documentado.
- **Tamaño de contexto:** no se cargan 300 skills a la vez; descripciones precisas e índice de skills activos por proyecto.
- **Contenido sectorial/normativo:** sin revisión de expertos es riesgo, no valor.
- **Seguridad de agentes:** cada MCP amplía lo que el agente puede hacer (permisos mínimos); contenido de herramientas y ficheros es **dato, no instrucciones** (defensa contra prompt injection); un agente con red abierta y credenciales es un riesgo real (firewall de salida en el devcontainer). Decidir pronto cómo se da acceso a Docker dentro del devcontainer para Testcontainers y sus implicaciones.
- **Licencias de terceros:** si se copia contenido de repositorios externos de buenas prácticas, revisar su licencia antes. Usarlos como inspiración, no como fuente de copia.

---

## 14. Referencias de partida (inspiración, no fuente de copia)

- Bases de conocimiento de buenas prácticas por dominio (p. ej. `guidomantilla/best-practices`).
- Listas comunitarias del ecosistema Claude Code (`awesome-claude-code`, colecciones de subagentes, hooks de seguridad).
- Marcos de platform engineering (golden paths, CNCF Technology Radar), production readiness reviews, OWASP ASVS, NIST SSDF.
- Documentación oficial vigente de cada herramienta: es la fuente de verdad al escribir cada skill.
