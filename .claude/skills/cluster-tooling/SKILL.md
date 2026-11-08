---
name: cluster-tooling
description: "Usar al crear o documentar el Kubernetes local de un proyecto: kind por defecto (ADR-0034), k3d alternativa, registro local y config reproducible."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Herramientas de clúster local (kind por defecto)

## Cuándo aplicar y cuándo no
- Aplica a cualquier proyecto que necesite ejecutar el sistema completo en Kubernetes local (desarrollo, demo, CI efímero).
- No aplica a tests de integración de un adaptador: ahí sigue mandando Testcontainers (ver `integration-testing-testcontainers`). El clúster local no los sustituye.
- No aplica a validar EKS: kind no reproduce nodos gestionados ni autoscaling real (ver `local-parity-matrix`).

## Reglas
- **MUST** usar kind por defecto (ADR-0034); k3d solo como alternativa documentada y justificada en el README del proyecto.
- **MUST** definir el clúster en un fichero versionado (`deploy/local/kind-config.yaml`), nunca con flags sueltos en comandos de wiki.
- **MUST** fijar la versión de nodo (`image: kindest/node:<tag>`) alineada con la versión de Kubernetes objetivo de EKS (comprobar tags disponibles por release de kind).
- **MUST** exponer un registro local para el bucle de desarrollo (patrón oficial de kind con `certs.d`), en vez de `kind load` en cada cambio.
- **MUST** envolver crear/destruir/reiniciar en `make local-up`, `make local-down`, `make local-reset` idempotentes.
- **SHOULD** usar un clúster por proyecto con nombre explícito (`kind create cluster --name <project>`), nunca el contexto `kind-kind` genérico.
- **SHOULD** comprobar `kubectl config current-context` antes de aplicar nada (evitar aplicar contra un clúster ajeno).
- **MUST NOT** apuntar los scripts locales a contextos que no empiecen por `kind-` o `k3d-`.
- **MUST NOT** presentar el clúster local como evidencia de que el despliegue funciona en AWS.

## Por qué
kind es la referencia de CI de Kubernetes y es simple de reproducir; k3d es más ligero pero añade divergencias de k3s (ADR-0034, decisión revisable por el dueño). Un contexto equivocado es la forma más barata de causar un incidente: el guard de contexto es una línea.

## Ejemplos
### Mal
```text
kind create cluster            # sin nombre, sin versión, sin config
kubectl apply -f k8s/          # contexto actual desconocido
```
### Bien
```yaml
# deploy/local/kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: acme-shop
nodes:
  - role: control-plane
    image: kindest/node:v1.0.0-changeme   # comprobar tag real de la release de kind
    extraPortMappings:
      - { containerPort: 30080, hostPort: 8080, protocol: TCP }
  - role: worker
containerdConfigPatches:
  - |-
    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = "/etc/containerd/certs.d"
```
```makefile
local-up:
	@kind get clusters | grep -qx acme-shop || kind create cluster --config deploy/local/kind-config.yaml
	@kubectl config current-context | grep -q '^kind-acme-shop$$'
```
El registro local sigue el script oficial de kind (contenedor `registry:2` en el puerto 5001 conectado a la red `kind`).

## Checklist de revisión
- [ ] Existe `kind-config.yaml` versionado con nombre y versión de nodo fijados.
- [ ] Hay registro local y el bucle de desarrollo no usa `kind load` manual.
- [ ] `make local-up/down/reset` son idempotentes y comprueban el contexto.
- [ ] El README lista qué NO reproduce el clúster (nodos gestionados, autoscaling real).

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de `deploy/local/` y Makefile | 3 | agente `code-reviewer` |
| Guard de contexto en el Makefile del proyecto | 2 | proyecto generado (pendiente plantilla; ADR-0038 solo guías) |
| Elección kind/k3d | 4 | ADR-0034, revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dev-loop`, `local-profiles`, `local-parity-matrix`, `resource-budgets`, `devcontainer-integration`.
- Fuentes: kind, "Local Registry" https://kind.sigs.k8s.io/docs/user/local-registry/ (verificado 2026-11-07; el parche de containerd es opcional desde kind v0.27.0 según esa página).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
