# Golden paths

Un *golden path* es el camino recomendado para un tipo de trabajo frecuente: una lista **ordenada** de skills y decisiones que, seguida de principio a fin, produce un resultado coherente. No son plantillas (ADR-0038): no contienen código, solo el orden en que un agente debe leer y aplicar las normas.

## Cómo usarlos
- Un agente que planifica un servicio, un evento o un frontend los usa como índice de lectura: empieza por el primer paso y sigue en orden.
- Cada paso es una skill o una decisión. En cada una, se leen sus reglas, se aplican y se comprueban con su checklist.
- Quien necesite salirse del camino lo documenta en un ADR del proyecto.

`make validate` comprueba que todas las skills citadas existen.

## GP-1 · Servicio Java de negocio
1. **Decidir la forma:** `microservices-decision-guide` (¿monolito modular primero?).
2. **Estructura:** `hexagonal` y `project-layout`.
3. **Persistencia:** `jpa-entity-design`, `transactions` y `n-plus-one`.
4. **API:** `error-handling-problem-details` y `openapi-contract-first`.
5. **Seguridad:** `authn-oidc-oauth2` y `method-and-endpoint-security`.
6. **Pruebas:** `integration-testing-testcontainers` y `contract-testing`.
7. **Observabilidad:** `otel-fundamentals-and-semconv` y `slo-sli-error-budgets`.
8. **Despliegue:** `workload-baseline` y `container-images`.

## GP-2 · Evento de dominio fiable
1. **Elegir el modelo de datos:** `datastore-selection-guide`.
2. **Publicar sin pérdidas:** `outbox-and-cdc` si el estado está en una base relacional, o `event-sourcing` si los eventos son el negocio.
3. **Garantías de entrega:** `delivery-semantics` y `dlq-retries-poison-messages`.
4. **Evolución del contrato:** `schema-registry-and-evolution`.

## GP-3 · Frontend React
1. **Arquitectura:** `frontend-architecture`.
2. **Tipos:** `typescript-strict-rules`.
3. **Estado:** `state-management`.
4. **Sesión y autenticación:** `auth-and-session`, con un servidor intermedio.
5. **Pruebas:** `testing`.
6. **Construcción y despliegue:** `build-and-deploy`.

## GP-4 · Infraestructura AWS preparada (no desplegada)
1. **Cuentas y barreras:** `organization-and-ou-design`.
2. **Red:** `vpc-multi-az-layers`.
3. **Cargas en Kubernetes:** `workload-baseline`.
4. **Evidencia:** `static-verification-ladder` y `maturity-labels`.
5. **Coste y recuperación:** `cost-estimation` y `dr-tabletop-exercises`.

Todo lo que produce este camino se etiqueta «preparado para AWS, no verificado en real».
