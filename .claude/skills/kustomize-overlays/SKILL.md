---
name: kustomize-overlays
description: "Usar al organizar manifiestos con Kustomize: base y overlays por entorno, patches, generators y cuándo preferirlo o combinarlo con Helm."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Overlays con Kustomize

## Cuándo aplicar y cuándo no
- Aplica a manifiestos propios con variaciones por entorno (dev, staging, prod) y a parches sobre salida de charts de terceros.
- No aplica a la creación de charts reutilizables (ver `helm-standards`).

## Reglas
- **MUST** estructura `base/` (común) + `overlays/<env>/` (solo diferencias); **MUST NOT** duplicar la base en cada overlay.
- **MUST** que los overlays modifiquen con patches pequeños (strategic merge o JSON 6902) y `images:` para versiones; **MUST NOT** copiar ficheros enteros.
- **MUST** que `kustomize build overlays/<env>` produzca YAML válido y pase kubeconform en CI para cada entorno.
- **MUST NOT** incluir secretos en `secretGenerator` con valores reales; usar external-secrets/Vault (ver `cluster-addons-baseline`).
- **SHOULD** fijar `namespace`, `labels` comunes y `nameSuffix`/`namePrefix` solo si hacen falta; evitarlos si rompen referencias.
- **SHOULD** usar `configMapGenerator` con hash para forzar rollout al cambiar config.
- **SHOULD** no mezclar Helm y Kustomize sin motivo: si se hace, `helm template` a base y parchear, documentado.
- **MUST** mantener las diferencias entre entornos pequeñas y visibles en un diff (paridad dev/prod).

## Por qué
Los overlays hacen visible qué cambia entre entornos. Una base copiada cuatro veces acaba siendo cuatro bases distintas y los bugs sólo aparecen en prod.

## Ejemplos
### Mal
```text
envs/dev/deployment.yaml     (copia completa)
envs/prod/deployment.yaml    (copia completa, ya divergente)
```
### Bien
```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: [../../base]
images:
  - name: registry.example.com/orders
    newTag: "1.4.2"
patches:
  - target: { kind: Deployment, name: orders }
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 3
```
```text
for e in dev staging prod; do kustomize build overlays/$e | kubeconform -strict -summary; done
```

## Checklist de revisión
- [ ] Base única y overlays con solo diferencias.
- [ ] Build de cada overlay validado en CI.
- [ ] Sin secretos reales en generators.
- [ ] Versiones de imagen vía `images:`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| `kustomize build` + kubeconform por entorno en CI | 1 | pipeline del proyecto generado (pendiente de plantilla en la fábrica) |
| Revisión de overlays | 3 | agente revisor de manifiestos |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `helm-standards`, `workload-baseline`, `config-by-environment`, `cluster-addons-baseline`.
- Fuentes: documentación de Kustomize / kubectl (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
