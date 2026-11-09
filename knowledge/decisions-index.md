# Índice de decisiones

«Tengo que decidir X»: dónde está el criterio. Las decisiones ya cerradas están en los ADR (`catalog/adr/`); las que dependen del proyecto, en la skill indicada. Si un ADR tiene estado «aceptado (defecto)», conviene revisarlo.

## Arquitectura
| Decisión | Dónde decidir |
|---|---|
| Monolito modular o microservicios | `microservices-decision-guide`, `modular-monolith` |
| Orquestación o coreografía | `sagas-and-process-managers`, `event-driven` |
| Outbox, event sourcing o solo auditoría | `when-to-use-and-when-not`, `outbox-and-cdc`, `audit-trail-without-event-sourcing` · ADR-0014 |
| Modelo de multi-tenencia | `multi-tenancy`, `multi-tenant-architecture` |
| Bloqueo en base de datos o distribuido | `pessimistic-locking`, `distributed-locking` |
| Reactivo, bloqueante o hilos virtuales | `reactive-vs-blocking`, `virtual-threads`, `threads-executors-and-pools` |
| Imagen nativa o JVM | `startup-and-native`, `jvm-in-containers` |
| Identificadores | `id-generation` |

## Datos
| Decisión | Dónde decidir |
|---|---|
| Qué almacén usar | `datastore-selection-guide`, `polyglot-operations-cost` · ADR-0013 |
| JPA, jOOQ o JDBC | `jdbc-and-jooq`, `spring-data-rules`, `jpa-entity-design` |
| DynamoDB frente a relacional | `dynamodb-data-modeling`, `dynamodb-event-store`, `global-tables-and-write-region-rules` |
| Qué y dónde cachear | `caching`, `cache-strategies` |
| Lago, almacén o lakehouse | `data-lake-and-lakehouse`, `warehouse-options` |
| Búsqueda | `search-and-discovery`, `cqrs-read-models-and-search` |

## APIs e integración
| Decisión | Dónde decidir |
|---|---|
| REST, gRPC, GraphQL o eventos | `rest-design-guidelines`, `grpc-protobuf`, `graphql`, `asyncapi-event-contracts` |
| Kafka, RabbitMQ o SQS | `kafka-producers-consumers`, `rabbitmq-sqs` |
| Cómo versionar y retirar una API | `api-versioning-deprecation`, `backward-compatibility-rules` |

## Plataforma y nube
| Decisión | Dónde decidir |
|---|---|
| Tier de resiliencia y multi-región | `tier-model-and-rpo-rto`, `multi-az-patterns`, `multi-region-patterns` · ADR-0007 |
| Estructura de cuentas AWS | `organization-and-ou-design`, `control-tower-and-account-factory` |
| Sidecar o ambient en Istio | `sidecar-vs-ambient-decision` · ADR-0032 |
| CNI en EKS | `eks-networking` · ADR-0033 |
| Kubernetes local (kind o k3d) | `cluster-tooling` · ADR-0034 |
| Terraform u OpenTofu | ADR-0008 |
| Vault, OpenBao o servicios gestionados | `secrets-management`, `envelope-encryption-and-kms` · ADR-0010, ADR-0031 |
| Repositorio de artefactos | `artifact-repository-port` · ADR-0035 |
| Dónde termina el TLS y qué protege el borde | `alb-nlb-and-tls-termination`, `waf-shield-and-cloudfront` |

## Entrega
| Decisión | Dónde decidir |
|---|---|
| Motor de CI | `alternatives` · ADR-0020 |
| Argo CD, Flux o Spinnaker | `argo-cd`, `flux-comparison`, `spinnaker-comparison` · ADR-0021 |
| Estrategia de despliegue progresivo | `canary-and-traffic-splitting`, `argo-rollouts` |
| Política de actualización de dependencias | `renovate-dependabot-policy`, `upgrade-policy` |
| Construir, comprar o adoptar una librería | `library-selection-and-tech-radar-process`, `third-party-risk` |

## Frontend
| Decisión | Dónde decidir |
|---|---|
| SPA o renderizado en servidor | `rendering-strategy-decision` · ADR-0036 |
| Dónde vive cada estado | `state-management` |
| Micro-frontends | `micro-frontends` |
| Cómo generar el cliente de la API | `api-client-from-openapi` |

## Calidad
| Decisión | Dónde decidir |
|---|---|
| Qué probar en cada nivel | `test-strategy`, `tdd`, `bdd` |
| Cuánta cobertura y qué más medir | `coverage-policy`, `mutation-testing` |
| Cómo probar contratos | `contract-testing-pact`, `contract-gate` |
| Cuándo hacer pruebas de carga y de caos | `performance-testing`, `chaos-engineering` |
| JMeter o Gatling para la carga | `performance-testing`, `gatling-load-testing` · D19 |
| Qué herramientas de análisis estático y de seguridad combinar | `static-analysis`, `security-testing-sast-dast`, `codeql-sast`, `sonarqube-quality-gate` |

## IA y agentes
| Decisión | Dónde decidir |
|---|---|
| RAG, agentes o ninguno | `rag-architecture`, `agents-and-tool-calling`, `vector-store-selection` |
| Qué servidores MCP añadir | `mcp-governance` · `catalog/mcp-servers.yaml` |
| Cuántos subagentes y con qué contexto | `subagent-design`, `parallel-work-and-worktrees` |
| Cuándo parar y pedir a una persona | `gate-protocol` |
