---
name: metrics-store-ha-retention
description: "Usar al dimensionar Prometheus: alta disponibilidad, retención local y almacenamiento a largo plazo vía remote write."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Almacén de métricas: HA y retención

## Cuándo aplicar y cuándo no
- Aplica al desplegar o revisar Prometheus (o Prometheus Operator) en la plataforma D22.
- No aplica a logs ni trazas (ver `logs-and-traces-stores`) ni a la definición de alertas (ver `alert-routing-and-oncall`).

## Reglas
- **MUST** fijar la retención de forma explícita: `--storage.tsdb.retention.time` y `--storage.tsdb.retention.size` (sin ninguno, el defecto es 15d).
- **MUST** poner `retention.size` por debajo de la capacidad del volumen (margen para WAL y compactación) y alertar al 80% de uso del PVC.
- **MUST** ejecutar HA como réplicas independientes que scrapean lo mismo, con `external_labels` distintos por réplica (`replica: a|b`); Prometheus no replica datos entre instancias.
- **MUST** que Alertmanager se despliegue en clúster (mínimo 3 réplicas) y que cada réplica de Prometheus envíe a todas.
- **MUST NOT** tratar el disco local como almacén histórico: más allá de la retención local, usar `remote_write` a un backend de largo plazo.
- **SHOULD** elegir el backend de largo plazo por ADR (candidatos con licencia abierta), sin licencias de pago por defecto (D16).
- **SHOULD** deduplicar en consulta por el label `replica` y no mezclar réplicas en dashboards.
- **MUST NOT** usar NFS para el TSDB local.

## Por qué
Una sola instancia es un punto único de fallo del que dependen las alertas. Dos réplicas dan HA de ingestión, no de histórico; por eso el largo plazo es otra pieza. Sin límite por tamaño, un aumento de series llena el disco y el TSDB se corrompe o para.

## Ejemplos
### Mal
```yaml
# Un único Prometheus, sin límites explícitos, sin remote write
args: ["--config.file=/etc/prometheus/prometheus.yml"]
```
### Bien
```yaml
# prometheus.yml (réplica a)
global:
  scrape_interval: 30s
  external_labels: { cluster: local-kind, replica: a }
remote_write:
  - url: http://longterm-store.observability:9009/api/v1/push
    queue_config: { max_samples_per_send: 2000 }
```
```yaml
args:
  - --storage.tsdb.retention.time=15d
  - --storage.tsdb.retention.size=40GB     # PVC de 50Gi
```

## Checklist de revisión
- [ ] Retención por tiempo y por tamaño explícitas, con margen en el PVC.
- [ ] Al menos 2 réplicas con `external_labels` diferenciadores.
- [ ] Alertmanager en clúster y apuntado desde todas las réplicas.
- [ ] Hay camino de largo plazo documentado en un ADR.
- [ ] Alerta de saturación de disco del TSDB.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Regla Conftest: Prometheus sin flags de retención o con 1 réplica | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de dimensionado | 3 | agente revisor de infraestructura |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `cardinality-and-cost-governance`, `observability-of-the-platform-itself`, `multi-tenant-observability`.
- Fuentes oficiales: https://prometheus.io/docs/prometheus/latest/storage/ (verificado 2026-11-07: flags de retención, defecto 15d, `remote_write`). Afirmaciones sobre NFS y HA: de la misma página.
- Preparado para AWS, no verificado en real. En local (kind) no se reproducen volúmenes EBS ni el backend de largo plazo real.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
