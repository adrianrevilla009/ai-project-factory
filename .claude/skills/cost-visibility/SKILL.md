---
name: cost-visibility
description: "Usar al definir etiquetado, asignación de costes y visibilidad de gasto por namespace/equipo en Kubernetes con OpenCost."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Visibilidad de costes con OpenCost

## Cuándo aplicar y cuándo no
- Aplica al diseñar etiquetas, namespaces y dashboards para atribuir coste a equipo/servicio/entorno.
- No aplica a la facturación real de la nube: OpenCost estima con precios de lista o configurados; la factura manda.
- En local no hay precios de nube reales: los importes son orientativos y no se reproduce la facturación AWS.

## Reglas
- **MUST** exigir en todo workload las etiquetas `app.kubernetes.io/name`, `team` y `env` (nombres propios de la organización, ajustables).
- **MUST** usar OpenCost (OSS) con Prometheus como fuente de métricas; sin licencias de pago por defecto (D16).
- **MUST** fijar `requests` en todos los pods: sin requests la asignación de coste es incorrecta.
- **SHOULD** separar el coste de recursos ociosos (`__idle__`) del coste atribuido.
- **SHOULD** revisar mensualmente los workloads con mayor diferencia entre request y uso real.
- **MUST NOT** presentar cifras de OpenCost como coste facturado en AWS; decir "estimación".
- **MUST NOT** usar etiquetas con datos personales.

## Por qué
Sin etiquetas consistentes el coste se agrupa en "otros" y nadie actúa. Sobredimensionar requests es el desperdicio más habitual y OpenCost lo hace visible.

## Ejemplos
### Mal
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders
spec:
  template:
    spec:
      containers:
        - name: orders
          image: registry.example/orders:1.0.0   # sin labels ni requests
```
### Bien
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders
  labels: { app.kubernetes.io/name: orders, team: payments, env: dev }
spec:
  selector:
    matchLabels: { app.kubernetes.io/name: orders }
  template:
    metadata:
      labels: { app.kubernetes.io/name: orders, team: payments, env: dev }
    spec:
      containers:
        - name: orders
          image: registry.example/orders:1.0.0
          resources:
            requests: { cpu: 250m, memory: 384Mi }
```

## Checklist de revisión
- [ ] Etiquetas `team`/`env`/`app.kubernetes.io/name` en pod template.
- [ ] Todos los contenedores con `requests`.
- [ ] OpenCost apunta al Prometheus correcto.
- [ ] Los informes dicen "estimación".

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno: exigir etiquetas de coste (pendiente) | 1 | `policies/kyverno/` (pendiente) |
| Conftest: requests obligatorios (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión de informes de coste | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `workload-baseline`, `autoscaling`, `namespaces-quotas-multitenancy`.
- Fuentes: documentación de OpenCost (opencost.io/docs); 2026-11-07 sin verificación en vivo.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
