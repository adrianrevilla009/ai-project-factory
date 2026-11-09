# Catálogo de patrones

Capa de navegación sobre las skills: para cada patrón, qué problema resuelve, cuándo **no** usarlo y dónde está la regla detallada. Las skills mandan; esto ayuda a encontrarlas. Un patrón mal aplicado es un antipatrón: mira también [`anti-patterns.md`](anti-patterns.md).

## Arquitectura y diseño
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Hexagonal (puertos y adaptadores) | Dominio testeable y aislado de framework e infraestructura | CRUD trivial sin lógica de negocio | `hexagonal`, `clean-architecture`, `layering-rules-archunit` |
| Monolito modular | Límites claros sin el coste operativo de los microservicios | Equipos que ya necesitan desplegar y escalar por separado | `modular-monolith`, `microservices-decision-guide` |
| Strangler fig | Migrar un legado sin reescritura total | Cuando el legado se puede apagar de una vez | `strangler-fig-migration`, `anti-corruption-layer` |
| Capa anticorrupción | Que el modelo de un sistema externo no contamine el propio | Integración con un sistema que ya habla tu modelo | `anti-corruption-layer`, `ddd-strategic` |
| BFF | Una API a medida de cada cliente | Un solo cliente con necesidades simples | `bff-and-api-gateway` |
| CQRS | Lecturas y escrituras con necesidades distintas | Lecturas y escrituras simétricas | `cqrs`, `cqrs-read-models-and-search` |
| Event sourcing | Los eventos son el negocio (auditoría, reproducción, temporalidad) | Solo quieres auditoría: basta un registro de auditoría | `event-sourcing`, `when-to-use-and-when-not`, `audit-trail-without-event-sourcing` |
| Outbox + CDC | Publicar eventos sin escritura doble | Un único almacén que ya es el log de eventos | `outbox-and-cdc`, `delivery-semantics` |
| Saga | Consistencia entre servicios sin transacción distribuida | Todo cabe en una transacción local | `sagas-and-process-managers`, `consistency-and-sagas` |
| Arquitectura celular | Limitar el radio de impacto de un fallo | Cargas pequeñas sin requisito de aislamiento | `cell-based-architecture`, `static-stability-and-cell-architecture` |
| Eventos de dominio en proceso | Desacoplar reacciones dentro de un módulo | Cuando necesitas garantía entre procesos (usa outbox) | `domain-events-in-spring`, `event-driven` |

## Datos
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Enrutado a réplicas de lectura | Descargar la base primaria | Lecturas que exigen consistencia inmediata | `read-replicas-and-routing` |
| Bloqueo optimista | Conflictos de escritura raros sin bloquear | Contención alta sobre las mismas filas | `optimistic-locking`, `pessimistic-locking` |
| Paginación por keyset | Paginar tablas grandes sin degradarse | Necesitas saltar a una página arbitraria | `pagination`, `pagination-filter-sort` |
| Borrado lógico con historia | Recuperar y auditar datos | Datos sujetos a supresión real (RGPD) | `auditing-soft-delete-history`, `data-privacy-in-db` |
| Migración expand/contract | Cambiar el esquema sin parar ni romper versiones antiguas | Esquema aún sin datos ni consumidores | `schema-migrations`, `database-migration-step` |
| Cache-aside | Lecturas caras y repetidas | Datos que cambian más rápido de lo que se leen | `caching`, `cache-strategies` |
| Cifrado de sobre | Cifrar muchos datos con claves rotables | Datos que no necesitan cifrado propio | `envelope-encryption-and-kms` |
| Multi-tenencia (fila, esquema o base) | Aislar clientes en un mismo sistema | Un solo cliente | `multi-tenancy`, `multi-tenant-architecture` |

## Integración y APIs
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Clave de idempotencia | Reintentos seguros | Operaciones naturalmente idempotentes | `idempotency-keys`, `idempotency-and-deduplication` |
| Reintento con DLQ | Aislar mensajes venenosos | Mensajes que nunca deben perderse sin intervención humana (alerta, no descarte) | `dlq-retries-poison-messages` |
| Esquema con registro y compatibilidad | Evolucionar eventos sin romper consumidores | Un productor y un consumidor desplegados siempre juntos | `schema-registry-and-evolution`, `backward-compatibility-rules` |
| API contract-first | Contrato como fuente de verdad | Prototipos desechables | `openapi-contract-first`, `contract-testing-pact` |
| Webhook firmado | Notificar a terceros con autenticidad | Consumidores internos con bus de eventos | `webhooks` |
| Lector tolerante | Aceptar campos nuevos sin romper | Contratos que deben validarse de forma estricta por seguridad | `backward-compatibility-rules` |

## Resiliencia
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Timeout, reintento y circuit breaker | Que un fallo ajeno no tumbe al servicio | Reintentos sobre operaciones no idempotentes | `resilience`, `http-clients-and-timeouts` |
| Bulkhead y backpressure | Aislar recursos y frenar a los productores | Carga muy baja y homogénea | `backpressure-and-bulkheads` |
| Degradación controlada | Mantener lo esencial bajo carga | Servicios de todo o nada | `load-shedding-and-degradation` |
| Estabilidad estática | Funcionar sin depender de un plano de control | Aplicaciones sin requisito de disponibilidad alta | `static-stability-and-cell-architecture` |
| Warm standby multi-región | RTO y RPO acotados ante pérdida de región | Tier de resiliencia bajo | `multi-region-patterns`, `tier-model-and-rpo-rto` |
| Apagado ordenado | Desplegar sin perder peticiones | Procesos sin estado de corta vida | `graceful-shutdown-lifecycle` |

## Entrega y plataforma
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Trunk-based con feature flags | Integrar a diario sin exponer lo inacabado | Equipos sin pruebas automáticas fiables | `git-workflow`, `feature-flags-openfeature` |
| Canary con análisis automático | Detectar regresiones con tráfico real | Sin métricas de salud fiables | `canary-and-traffic-splitting`, `argo-rollouts`, `canary-analysis-and-synthetic-monitoring` |
| GitOps | Estado deseado en Git, reconciliado | Entornos efímeros sin repositorio de estado | `argo-cd`, `repo-strategy`, `drift-and-self-heal-policy` |
| Entornos efímeros | Probar cada cambio aislado | Dependencias imposibles de replicar | `ephemeral-preview-environments`, `ephemeral-environments` |
| Golden path | Camino recomendado con poco coste cognitivo | Casos que de verdad requieren salirse | `golden-paths-governance`, `software-templates` |
| Build reproducible, SBOM y firma | Confianza en lo que se despliega | Artefactos que nunca salen del equipo | `reproducible-builds`, `sbom-generation`, `image-signing-and-provenance` |
| Puertas de calidad en el pipeline | Impedir que lo malo avance | Reglas que nadie puede cumplir (acaban saltándose) | `quality-gates`, `security-gates` |

## Observabilidad
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Alertas por SLO (burn rate) | Avisar solo cuando importa al usuario | Servicios sin SLO definido | `slo-sli-error-budgets`, `alerting-symptom-based` |
| Logs estructurados con traza | Correlacionar un fallo entre servicios | Nunca: es básico | `structured-logging`, `tracing` |
| Señales doradas, RED y USE | Qué medir primero | — | `golden-signals-red-use` |

## Seguridad
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Zero trust con mTLS | No confiar en la red | — | `zero-trust`, `mtls-strict-and-peer-auth` |
| Credenciales dinámicas | Secretos efímeros y auditables | Sistemas que no admiten rotación | `dynamic-database-credentials`, `rotation-and-leases` |
| Mínimo privilegio y barreras SCP | Limitar el daño de una credencial robada | — | `cloud-iam-least-privilege`, `scp-guardrails` |
| Modelado de amenazas STRIDE | Encontrar fallos de diseño pronto | Cambios triviales sin superficie nueva | `threat-modeling-stride` |

## Frontend
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Estado en su sitio (servidor, URL, local) | Evitar un almacén global para todo | — | `state-management`, `component-patterns` |
| Sesión por cookie vía BFF | No exponer tokens al navegador | API pública consumida por terceros | `auth-and-session`, `security-frontend` |
| Tokens de diseño | Coherencia visual y temas | Prototipos de una pantalla | `design-system-and-tokens` |
| División de código por ruta | Carga inicial rápida | Aplicaciones pequeñas | `routing-and-code-splitting`, `frontend-performance` |
| Micro-frontends | Equipos que despliegan UI de forma independiente | Un solo equipo | `micro-frontends` |

## Pruebas
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Estrategia de pruebas (pirámide) | Reparto de esfuerzo entre niveles | — | `test-strategy` |
| Dependencias reales con Testcontainers | Pruebas de integración fiables | Lógica pura sin E/S | `integration-testing-testcontainers`, `db-testing` |
| Contratos dirigidos por el consumidor | Cambiar sin romper clientes | Un solo equipo con despliegue conjunto | `contract-testing-pact`, `contract-testing` |
| Mutación | Medir si las pruebas detectan fallos | Como objetivo en sí mismo | `mutation-testing`, `coverage-policy` |
| Pruebas basadas en propiedades | Casos límite que nadie pensó | Lógica sin invariantes claras | `property-based-testing` |
| Caos y game days | Descubrir debilidades antes que los usuarios | Sin observabilidad ni plan de vuelta atrás | `chaos-engineering`, `fault-injection-and-game-days` |

## Ingeniería con agentes
| Patrón | Resuelve | Cuándo NO usarlo | Skills |
|---|---|---|---|
| Gate humano | Decisiones irreversibles con una persona | Pasos reversibles y de bajo riesgo | `gate-protocol` |
| Subagente de contexto aislado | Proteger el contexto principal | Tareas pequeñas que dependen de todo lo hablado | `subagent-design`, `handoff-artifacts-between-agents` |
| Evidencia antes de afirmar | Que un agente no invente | — | `verify-before-asserting` |
