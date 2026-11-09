---
name: helm-standards
description: "Usar al crear o revisar charts Helm: estructura, values, versionado, schema, lint y reglas para no meter secretos ni lógica excesiva en templates."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Estándares Helm

## Cuándo aplicar y cuándo no
- Aplica a charts propios del proyecto y a la forma de consumir charts de terceros.
- No aplica a overlays Kustomize (ver `kustomize-overlays`) ni a la sincronización GitOps (ver bloque 17).

## Reglas
- **MUST** un chart genérico de servicio reutilizable (library o chart base) en lugar de copiar templates por servicio.
- **MUST** incluir `values.schema.json` para validar values y fallar pronto.
- **MUST** versionar el chart (`version`, SemVer) separado de `appVersion`; **MUST NOT** publicar charts con versión mutable.
- **MUST** pasar `helm lint` y `helm template | kubeconform` (o equivalente) en CI.
- **MUST NOT** guardar secretos en `values.yaml`; usar referencias a Secrets creados por external-secrets o Vault (ver `cluster-addons-baseline`).
- **MUST** exponer en values: imagen (repositorio + tag/digest), resources, probes, réplicas, securityContext con defaults seguros del `workload-baseline`.
- **SHOULD** limitar la lógica en templates: sin `lookup` ni condicionales anidados profundos; helpers en `_helpers.tpl`.
- **SHOULD** fijar charts de terceros por versión exacta y revisar sus values; **MUST NOT** usar `latest` ni rangos abiertos.
- **SHOULD** usar un values por entorno (`values-prod.yaml`) con solo las diferencias.
- **MUST** pensar en el diff: los hooks de Helm y `lookup` complican GitOps; documentarlos si se usan.

## Por qué
Charts copiados divergen y cada uno reabre los mismos errores de seguridad. El schema convierte typos en errores de CI, no en incidentes.

## Ejemplos
### Mal
```yaml
# values.yaml
image: registry.example.com/orders:latest
dbPassword: changeme-real-password
```
### Bien
```yaml
# values.yaml
image: { repository: registry.example.com/orders, tag: "1.4.2" }
resources:
  requests: { cpu: 500m, memory: 1Gi }
  limits: { memory: 1Gi }
existingSecret: orders-db   # creado por external-secrets, no por el chart
```
```json
{ "$schema": "http://json-schema.org/draft-07/schema#", "type": "object",
  "required": ["image", "resources"],
  "properties": { "image": { "type": "object", "required": ["repository", "tag"] } } }
```
```text
helm lint charts/service -f charts/service/values-prod.yaml
helm template orders charts/service | kubeconform -strict -summary
```

## Criterios de decisión y trampas
### Cómo decidir
- Un chart por servicio con valores explícitos y esquema de validación; versiona el chart y la aplicación por separado cuando sus ritmos difieren.
- Plantillas simples: la lógica compleja es una señal de que falta un operador o un componente.
### Trampas frecuentes
- Plantillas con lógica enrevesada.
- Valores sin validar.
- Charts que despliegan recursos de varios servicios.
- Secretos en los valores.
- Subcharts sin versión fija.
### Evidencia
- El chart pasa validación de esquema y de manifiestos en CI.

## Checklist de revisión
- [ ] Chart base reutilizado; `values.schema.json` presente.
- [ ] version y appVersion coherentes.
- [ ] Sin secretos ni `latest` en values.
- [ ] lint y kubeconform en CI.
- [ ] Charts de terceros fijados por versión.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| `helm lint` + kubeconform en CI | 1 | pipeline del proyecto generado (ver `quality-gates`) |
| Detección de secretos en values | 1 | `secret-scanning-and-leak-response` |
| Revisión de templates | 3 | agente revisor de manifiestos |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `kustomize-overlays`, `workload-baseline`, `cluster-addons-baseline`, `container-and-k8s-security`.
- Fuentes: documentación de Helm (chart best practices, schema).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
