---
name: canary-and-traffic-splitting
description: "Usar al desplegar progresivamente (canary, blue/green, mirroring) con reparto de tráfico por pesos en Istio o Gateway API."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Canary y reparto de tráfico

## Cuándo aplicar y cuándo no
- Aplica a cambios con riesgo de regresión visible por el usuario en servicios con tráfico suficiente para medir.
- No aplica a migraciones de esquema incompatibles: el reparto de tráfico no arregla un cambio destructivo de base de datos (ver `schema-migrations`).

## Reglas
- **MUST** desplegar la versión nueva como Deployment aparte con etiqueta `version`, sin tocar la estable.
- **MUST** repartir con pesos explícitos que sumen 100 y empezar con porcentaje bajo (p. ej. 5 %).
- **MUST** definir antes criterios de promoción y de rollback (tasa de error, latencia p99) medidos en métricas de la malla.
- **MUST** poder volver a 100 % estable con un solo cambio de manifiesto.
- **SHOULD** usar `HTTPRoute.backendRefs[].weight` (Gateway API) y reservar `VirtualService` para lo que no cubra (comprobar al fijar la versión).
- **SHOULD** usar mirroring para probar con tráfico real sin efectos visibles, solo en operaciones idempotentes y de lectura.
- **MUST NOT** hacer canary con efectos secundarios no idempotentes duplicados (mirroring de pagos).
- **SHOULD** valorar un controlador de entrega progresiva OSS (p. ej. Argo Rollouts o Flagger; comprobar compatibilidad) frente a ediciones manuales.

## Por qué
Un 5 % de tráfico a la versión nueva limita el radio de impacto y da datos reales. Sin criterios previos, la promoción se decide por sensación.

## Ejemplos
### Mal
```yaml
# Se cambia la imagen del Deployment estable: 100 % del tráfico al instante
spec:
  template:
    spec:
      containers: [{ name: orders, image: registry.example/orders:2.0.0 }]
```
### Bien
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: orders, namespace: orders }
spec:
  parentRefs: [{ name: public, namespace: istio-ingress }]
  rules:
    - backendRefs:
        - { name: orders-v1, port: 8080, weight: 95 }
        - { name: orders-v2, port: 8080, weight: 5 }
```

## Checklist de revisión
- [ ] Versiones separadas con etiqueta `version`.
- [ ] Pesos suman 100; inicio bajo.
- [ ] Criterios de promoción/rollback escritos y con métrica.
- [ ] Sin efectos duplicados en mirroring.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de plan de rollout | 3 | agente `code-reviewer` |
| Aprobación de promoción a producción | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `traffic-management`, `gateway-api`, `mesh-observability`, `backward-compatibility-rules`.
- Fuentes: istio.io/latest/docs/tasks/traffic-management/traffic-shifting/ y gateway-api.sigs.k8s.io (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
