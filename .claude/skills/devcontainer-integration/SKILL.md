---
name: devcontainer-integration
description: "Usar al preparar un devcontainer que traiga kind, kubectl, Helm, Tilt y el resto del tooling local para que el clúster arranque igual en cualquier máquina."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Integración con devcontainer

## Cuándo aplicar y cuándo no
- Aplica a `.devcontainer/devcontainer.json` de un proyecto generado que usa kind (ADR-0034) y los perfiles locales.
- No aplica a la fábrica (solo guías, ADR-0038) ni a CI, que usa su propia imagen.

## Reglas
- **MUST** que el devcontainer incluya el tooling del bucle local: Docker (docker-in-docker o socket del host), kind, kubectl, Helm, Kustomize y Tilt o Skaffold según `dev-loop`.
- **MUST** fijar versiones de las herramientas (feature o descarga con checksum); no usar `latest`.
- **MUST** que `make local-up` funcione dentro del devcontainer sin pasos manuales previos.
- **MUST** documentar el requisito de recursos del contenedor (ver `resource-budgets`); docker-in-docker anida un segundo nivel de consumo.
- **SHOULD** preferir el socket del host cuando el equipo acepta compartir el daemon; documentar el compromiso de aislamiento.
- **SHOULD** instalar extensiones de editor solo si aportan al flujo (YAML, Kubernetes), sin telemetría adicional.
- **MUST NOT** montar `~/.aws` ni exportar credenciales AWS al devcontainer: en local no hace falta ni se despliega (ADR-0004).
- **MUST NOT** incluir secretos en `devcontainer.json`; los valores locales son `example`/`changeme`.
- **MUST NOT** publicar puertos de dashboards (Grafana, Argo CD) a la red externa; solo `localhost`.

## Por qué
La mayor fuente de "en mi máquina funciona" en Kubernetes local son las versiones de kind, kubectl y Docker. El devcontainer fija el entorno; no montar credenciales AWS refuerza que el flujo es sin nube.

## Ejemplos
### Mal
```json
{
  "image": "mcr.microsoft.com/devcontainers/base:latest",
  "mounts": ["source=${localEnv:HOME}/.aws,target=/root/.aws,type=bind"]
}
```
### Bien
```json
{
  "name": "demo-local-k8s",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/kubectl-helm-minikube:1": { "minikube": "none" }
  },
  "postCreateCommand": "make tools-install",
  "forwardPorts": [8080]
}
```
Las features y su opción `minikube: none` se comprueban al fijar la versión; kind se instala en `make tools-install` con versión y checksum fijos.

## Checklist de revisión
- [ ] Versiones fijadas, sin `latest` en herramientas.
- [ ] `make local-up` funciona tras abrir el devcontainer.
- [ ] Sin montajes ni variables de credenciales AWS.
- [ ] Requisitos de recursos documentados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Detección de secretos al editar | 2 | `.claude/hooks/` (pre-tool-use) |
| Regla específica para devcontainer sin `latest` ni `.aws` | 1 | pendiente (`policies/`) |
| Revisión del fichero | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cluster-tooling`, `dev-loop`, `resource-budgets`, `local-profiles`.
- Fuentes: especificación Dev Containers (https://containers.dev, 2026-11-07, sin verificar detalle).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
