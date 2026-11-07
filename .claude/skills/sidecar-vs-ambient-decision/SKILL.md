---
name: sidecar-vs-ambient-decision
description: "Usar al elegir o revisar el modo de dataplane de Istio (sidecar o ambient) según ADR-0032; por defecto sidecar."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Sidecar vs ambient (ADR-0032)

## Cuándo aplicar y cuándo no
- Aplica al diseñar la malla de un proyecto nuevo o al plantear migrar de modo.
- No aplica a proyectos sin malla: ver si realmente se necesita (mTLS, autorización L7, tráfico) antes de adoptar Istio.

## Reglas
- **MUST** usar **sidecar por defecto** (ADR-0032): modo más maduro y documentado.
- **MUST** registrar en un ADR del proyecto cualquier desviación a ambient, con la verificación de madurez realizada.
- **SHOULD** valorar ambient solo si la sobrecarga de recursos por pod es un problema medido y la versión de Istio elegida lo declara estable (TODO-VERIFY estado vigente de ambient, de waypoint y de compatibilidad con la versión).
- **MUST NOT** mezclar sidecar y ambient en un mismo namespace sin haber leído la guía de coexistencia (TODO-VERIFY).
- **MUST** documentar el modo elegido en el README de plataforma del proyecto.

## Por qué
Sidecar: un proxy Envoy por pod, coste de CPU/memoria por réplica, pero comportamiento bien conocido, L7 en cada pod y depuración madura. Ambient: `ztunnel` por nodo para L4/mTLS y `waypoint` opcional para L7, menos sobrecarga pero modelo operativo distinto. ADR-0032 lo deja como alternativa documentada, pendiente de confirmación humana.

| Criterio | Sidecar (defecto) | Ambient (alternativa, TODO-VERIFY) |
|---|---|---|
| Madurez | Alta | Verificar en la versión elegida |
| Recursos | Proxy por pod | Componentes por nodo + waypoint |
| L7 | En cada pod | Solo con waypoint |
| Activación | Etiqueta de inyección | Etiqueta `istio.io/dataplane-mode=ambient` (TODO-VERIFY) |

## Ejemplos
### Mal
```yaml
# Se activa ambient "porque consume menos" sin medir ni registrar decisión
apiVersion: v1
kind: Namespace
metadata:
  name: orders
  labels:
    istio.io/dataplane-mode: ambient
```
### Bien
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: orders
  labels:
    istio-injection: enabled   # sidecar por defecto; con revisiones: istio.io/rev (TODO-VERIFY)
```

## Checklist de revisión
- [ ] Modo documentado y coherente con ADR-0032.
- [ ] Si hay ambient: ADR de proyecto con medición y verificación de madurez.
- [ ] Ningún namespace con ambas etiquetas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de ADR de proyecto ante cualquier uso de ambient | 3 | agente `architecture-reviewer` (si existe; si no, revisión humana) |
| Conftest: namespace con `istio.io/dataplane-mode` sin ADR (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `mtls-strict-and-peer-auth`, `istio-upgrades-and-ops`, `multi-cluster-mesh`.
- Fuentes: ADR-0032 (`catalog/adr/0032-istio-sidecar-vs-ambient.md`); istio.io/latest/docs/ambient/ — TODO-VERIFY, 2026-11-07 sin verificación en vivo.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
