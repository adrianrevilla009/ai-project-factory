# Golden paths

Caminos recomendados de extremo a extremo. Cada uno es una lista ordenada de skills y decisiones. Sin plantillas (ADR-0038).

## GP-1 · Servicio Java de negocio (T1)
1. `microservices-decision-guide` → ¿monolito modular primero? 2. `hexagonal` + `project-layout` 3. `jpa-entity-design`, `transactions`, `n-plus-one` 4. `error-handling-problem-details`, `openapi-contract-first` 5. `authn-oidc-oauth2`, `method-and-endpoint-security` 6. `integration-testing-testcontainers`, `contract-testing` 7. `otel-fundamentals-and-semconv`, `slo-sli-error-budgets` 8. `workload-baseline`, `container-images`.

## GP-2 · Evento de dominio fiable
Decidir con `datastore-selection-guide` → `outbox-and-cdc` (estado en Postgres) o `event-sourcing/` (eventos son el negocio) → `delivery-semantics`, `dlq-retries-poison-messages`, `schema-registry-and-evolution`.

## GP-3 · Frontend React
`architecture` (frontend-react) → `typescript-strict-rules` → `state-management` → `auth-and-session` (BFF) → `testing` → `build-and-deploy`.

## GP-4 · Infra AWS preparada (no desplegada)
`organization-and-ou-design` → `vpc-multi-az-layers` → `workload-baseline` → `static-verification-ladder` → `maturity-labels` → `cost-estimation` → `dr-tabletop-exercises`.
