---
name: local-profiles
description: "Usar al definir qué se levanta en local: perfil mínimo (servicio + Postgres + DynamoDB Local) y completo (Kafka, Vault, Istio, observabilidad)."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Perfiles locales: mínimo y completo

## Cuándo aplicar y cuándo no
- Aplica al diseñar `make local-up`, los overlays `local-min` y `local-full` y el README de arranque.
- No aplica a entornos compartidos ni a AWS; los perfiles no son entornos de promoción (`environment-promotion`).

## Reglas
- **MUST** ofrecer dos perfiles con nombre: `minimal` y `full`, seleccionables con `make local-up PROFILE=minimal|full`.
- **MUST** que `minimal` contenga solo: el servicio, Postgres (CloudNativePG u operador equivalente) y DynamoDB Local (imagen oficial de AWS, sin cuenta ni licencia).
- **MUST** que `full` añada: Kafka (Strimzi), Vault en modo dev, Istio con Gateway API, y observabilidad (Prometheus, Grafana, Loki, Tempo). MinIO y Redis solo si el servicio los usa.
- **MUST** que el servicio arranque en `minimal` sin las piezas de `full` (feature toggles / adaptadores nulos documentados), o declarar explícitamente que no es posible.
- **MUST** documentar en cada perfil qué NO reproduce respecto a AWS (ver `local-parity-matrix`).
- **SHOULD** declarar requisitos de recursos por perfil (`resource-budgets`).
- **MUST NOT** activar `full` por defecto.
- **MUST NOT** usar Vault en modo dev ni claves de ejemplo fuera del clúster local; el modo dev es solo local.

## Por qué
Un único perfil pesado hace que nadie levante el clúster; uno único ligero oculta problemas de integración (mensajería, mesh, secretos). Dos perfiles dejan elegir coste vs. fidelidad. DynamoDB Local es la opción por defecto frente a LocalStack porque LocalStack exige hoy un Auth Token para arrancar (https://docs.localstack.cloud/aws/getting-started/auth-token/, 2026-11-07), lo que choca con D16 (sin licencias de pago por defecto).

## Ejemplos
### Mal
```text
make local-up   # levanta Kafka, Istio, Vault y 6 pods de observabilidad siempre; 12 GB de RAM
```
### Bien
```makefile
PROFILE ?= minimal
local-up:
	kubectl apply -k deploy/overlays/local-$(PROFILE)
```
```yaml
# deploy/overlays/local-minimal/kustomization.yaml
resources:
  - ../../base
  - postgres-cluster.yaml     # CloudNativePG Cluster
  - dynamodb-local.yaml       # amazon/dynamodb-local, tag fijado
```
```yaml
# deploy/overlays/local-full/kustomization.yaml
resources:
  - ../local-minimal
  - kafka-strimzi.yaml
  - vault-dev.yaml
  - istio-gateway.yaml
  - observability/
```

## Criterios de decisión y trampas
### Cómo decidir
- Dos perfiles: uno ligero para el día a día y otro completo para integración (mensajería, malla, secretos); el equipo elige coste frente a fidelidad.
- Declara qué no reproduce cada perfil.
### Trampas frecuentes
- Un solo perfil pesado que nadie levanta.
- Un perfil ligero que oculta problemas de integración.
- Perfiles que divergen sin que nadie lo vea.
- Sin documentar qué falta.
- Datos y secretos reales en local.
### Evidencia
- Cada perfil documenta lo que incluye y lo que no, y se levanta con un comando.

## Checklist de revisión
- [ ] Existen overlays `local-minimal` y `local-full`; `minimal` es el defecto.
- [ ] `minimal` arranca solo con servicio + Postgres + DynamoDB Local.
- [ ] El README lista lo que cada perfil no reproduce.
- [ ] Sin dependencias de pago.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: endpoint de DynamoDB Local fuera de perfiles de test/local | 1 | `policies/semgrep/dynamodb-local-endpoint-in-main.yaml` |
| Revisión de overlays | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cluster-tooling`, `aws-emulation`, `local-parity-matrix`, `resource-budgets`, `data-seeding-and-demo-data`.
- Fuentes: `catalog/parity-matrix.yaml`; ADR-0034; fin de la edición Community de LocalStack (2026-03-23, ver `aws-emulation`).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
