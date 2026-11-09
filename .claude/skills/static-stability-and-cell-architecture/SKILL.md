---
name: static-stability-and-cell-architecture
description: "Usar al decidir cuánta capacidad pre-aprovisionar en la secundaria y cómo limitar el radio de impacto con celdas o shards; evita depender de operaciones de control durante el fallo."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Estabilidad estática y arquitectura de celdas

## Cuándo aplicar y cuándo no
- Aplica a dimensionar la secundaria (warm standby) y a servicios multi-tenant donde un fallo no debe afectar a todos.
- No aplica a sistemas pequeños sin requisito de tier 0-1: las celdas añaden complejidad.
- Diseño: preparado para AWS, no verificado en real; las celdas no se prueban a escala en local.

## Reglas
- **MUST** que la conmutación solo requiera acciones de plano de datos: la capacidad que absorbe el tráfico inicial ya está aprovisionada (estabilidad estática).
- **MUST** dimensionar la secundaria de warm standby para la carga inicial esperada tras el failover y documentar el resto de rampa (HPA, Karpenter) como dependencia de plano de control, con cuotas reservadas.
- **SHOULD** tier 0: capacidad plena en ambas regiones (hot standby o activo-activo).
- **SHOULD** dividir servicios críticos en celdas (cada una con su propio conjunto de tenants, colas y datos) con un enrutador fino y estable; **MUST NOT** compartir estado entre celdas.
- **MUST** acotar el radio de impacto: despliegues progresivos celda a celda (ver `change-and-release-management`).
- **MUST NOT** colocar en el camino crítico de recuperación servicios que viven solo en la región afectada (registro, config, secretos, state).
- **SHOULD** medir el "tamaño máximo de celda" y limitar tenants por celda.

## Por qué
Si recuperarse exige lanzar nodos o editar configuración, un fallo regional puede impedirlo. Pre-aprovisionar cuesta (ver `finops-of-resilience`) pero convierte la recuperación en un cambio de tráfico. El whitepaper de DR describe esta disyuntiva: hot standby con capacidad suficiente frente a depender de Auto Scaling, que es plano de control.

## Ejemplos
### Mal
```yaml
# Secundaria a 0 réplicas: el failover depende de escalar y de capacidad de nodos
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api }
spec: { replicas: 0 }
```
### Bien
```yaml
# overlay eu-central-1: 30 % de la capacidad primaria ya en marcha, HPA para el resto
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api }
spec: { replicas: 4 }          # primaria: 12
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: orders-api }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: orders-api }
  minReplicas: 4
  maxReplicas: 12
```

## Criterios de decisión y trampas
### Cómo decidir
- Diseña para que el servicio siga funcionando sin depender de acciones del plano de control durante un fallo: capacidad ya aprovisionada y decisiones tomadas de antemano.
- Las celdas limitan el radio de impacto.
### Trampas frecuentes
- Depender de escalar durante la caída.
- Conmutaciones que necesitan crear recursos nuevos.
- Celdas que comparten dependencias críticas.
- Configuración que se descarga al arrancar y falla si el servicio está caído.
- Sin pruebas con el plano de control inaccesible.
### Evidencia
- Una prueba con el plano de control bloqueado comprueba que el servicio mantiene su capacidad.

## Checklist de revisión
- [ ] Capacidad inicial de la secundaria justificada con el modelo de carga.
- [ ] Cuotas de la secundaria cubren el escalado a plena capacidad.
- [ ] Ningún componente del camino de recuperación vive solo en la región caída.
- [ ] Si hay celdas: sin estado compartido y despliegue progresivo.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: `replicas` > 0 en overlay de secundaria tier 0-1 | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión de dimensionado | 3 | agente `code-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tier-model-and-rpo-rto`, `capacity-and-load-modeling`, `dependency-mapping-and-blast-radius`, `finops-of-resilience`.
- Fuente: AWS DR whitepaper, sección Warm standby, https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html (2026-11-07). Patrón de celdas.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
