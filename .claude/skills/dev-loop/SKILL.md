---
name: dev-loop
description: "Usar al configurar el bucle de desarrollo inner-loop en Kubernetes local con Tilt o Skaffold: rebuild, sync, port-forward y límites del hot reload en Java."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Bucle de desarrollo en Kubernetes local (Tilt / Skaffold)

## Cuándo aplicar y cuándo no
- Aplica cuando el desarrollador itera sobre un servicio dentro del clúster local (ver `cluster-tooling`).
- No aplica a la mayoría de iteraciones de lógica: ahí es más rápido ejecutar la app en el IDE contra dependencias locales (`local-profiles` mínimo) y tests con Testcontainers.

## Reglas
- **MUST** elegir una sola herramienta por proyecto (Tilt o Skaffold) y documentarla; no mantener ambos ficheros.
- **MUST** reutilizar los mismos manifiestos/Helm/Kustomize que usará GitOps (`helm-standards`, `kustomize-overlays`) con un overlay `local`; no escribir YAML paralelo solo para el bucle.
- **MUST** construir con el mismo Dockerfile multistage que CI (`docker-multistage`) y publicar al registro local.
- **MUST** definir `make dev` como único punto de entrada.
- **SHOULD** limitar el live-update a recursos estáticos o classes recargables; para Java el rebuild de imagen con caché de capas es el camino fiable (comprobar soporte de sync por herramienta).
- **SHOULD** declarar en el fichero qué recursos arrancan por defecto, respetando el perfil de `local-profiles`.
- **MUST NOT** commitear credenciales ni tokens en el Tiltfile/skaffold.yaml; usar secretos de ejemplo (`changeme`) para el perfil local.
- **MUST NOT** ejecutar el bucle contra un contexto que no sea de clúster local.

## Por qué
Si el bucle usa manifiestos distintos de los desplegados, "funciona en local" no significa nada. Y un bucle lento (minutos por cambio) hace que el equipo vuelva a ejecutar solo en IDE y el clúster local se pudra.

## Ejemplos
### Mal
```python
# Tiltfile con YAML duplicado y contexto libre
k8s_yaml('local-only/deployment.yaml')
docker_build('shop', '.')
```
### Bien
```python
# Tiltfile
allow_k8s_contexts('kind-acme-shop')
docker_build('localhost:5001/shop-api', '.', dockerfile='Dockerfile')
k8s_yaml(kustomize('deploy/overlays/local'))
k8s_resource('shop-api', port_forwards=8080, resource_deps=['postgres'])
```
```yaml
# skaffold.yaml (alternativa)
apiVersion: skaffold/v4beta11   # comprobar apiVersion vigente
kind: Config
build:
  artifacts:
    - image: localhost:5001/shop-api
manifests:
  kustomize:
    paths: [deploy/overlays/local]
deploy:
  kubectl: {}
```

## Checklist de revisión
- [ ] Una sola herramienta; `make dev` documentado.
- [ ] Reutiliza el overlay `local` de los manifiestos reales.
- [ ] Contexto restringido a clúster local.
- [ ] Sin secretos reales en los ficheros.
- [ ] Tiempo de ciclo medido y anotado en el README.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de Tiltfile/skaffold.yaml | 3 | agente `code-reviewer` |
| Escaneo de secretos en commits | 2 | skill `secret-scanning-and-leak-response` (hooks) |
| Medición del ciclo | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cluster-tooling`, `local-profiles`, `docker-multistage`, `kustomize-overlays`, `devcontainer-integration`.
- Fuentes: documentación de Tilt (https://docs.tilt.dev) y Skaffold (https://skaffold.dev/docs) — comprobar versiones y API vigente, no consultadas en esta revisión.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
