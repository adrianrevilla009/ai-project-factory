---
name: resource-budgets
description: "Usar al fijar CPU/RAM del clúster local y los requests/limits por perfil (minimal/full), para que el portátil del desarrollador aguante."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Presupuestos de recursos locales

## Cuándo aplicar y cuándo no
- Aplica al definir requisitos de máquina por perfil, `requests`/`limits` de los pods locales y la configuración de Docker/WSL2.
- No aplica a dimensionar capacidad en AWS (ver `capacity-and-load-modeling`); los valores locales no se extrapolan.

## Reglas
- **MUST** documentar por perfil la RAM y CPU mínimas de la máquina. Los valores numéricos son hipótesis a medir (comprobar midiendo con `kubectl top`), no cifras garantizadas.
- **MUST** que `minimal` (servicio, Postgres, DynamoDB Local) sea el perfil por defecto y quepa en un portátil de gama media.
- **MUST** que todo pod local declare `resources.requests` y `resources.limits`; sin límites un pod puede tumbar el nodo kind.
- **MUST** fijar `requests` bajos y `limits` moderados en el overlay local; no reutilizar los del diseño para AWS.
- **SHOULD** limitar réplicas a 1 en local (Kafka, Postgres, Vault dev) y declararlo como no reproducción de HA.
- **SHOULD** reducir retención y scrape interval en Prometheus/Loki/Tempo en `full`.
- **SHOULD** limitar WSL2 con `.wslconfig` (`memory`, `processors`) y avisar si se supera.
- **MUST NOT** activar `full` por defecto ni sumar componentes a `minimal` sin actualizar la tabla de presupuestos.
- **MUST NOT** afirmar que un presupuesto local demuestra el dimensionamiento real.

## Por qué
El fallo habitual del Kubernetes local es el abandono por lentitud. Un presupuesto explícito y verificable por perfil hace visible el coste de cada componente añadido.

## Ejemplos
### Mal
```yaml
containers:
  - name: kafka
    image: example/kafka:local   # sin resources: puede consumir toda la RAM del nodo
```
### Bien
```yaml
containers:
  - name: app
    image: example/app:local
    resources:
      requests: { cpu: 100m, memory: 256Mi }
      limits:   { cpu: 500m, memory: 512Mi }
```
```text
# %UserProfile%\.wslconfig (valores de ejemplo, ajustar tras medir)
[wsl2]
memory=8GB
processors=4
```

## Checklist de revisión
- [ ] Tabla RAM/CPU por perfil, con la nota de que son valores a medir.
- [ ] Todos los pods locales con requests y limits.
- [ ] `minimal` sigue siendo el defecto.
- [ ] Las réplicas únicas constan como no reproducción de HA.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno: exigir requests/limits | 1 | `policies/kyverno/workload-baseline.yaml` (verificar que cubre recursos; comprobar al fijar la versión) |
| Presupuesto por perfil | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `local-profiles`, `cluster-tooling`, `autoscaling`, `devcontainer-integration`.
- Fuentes: documentación de Kubernetes sobre gestión de recursos de contenedores (comprobar URL); `catalog/adr/0034-kubernetes-local-kind-vs-k3d.md`.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
