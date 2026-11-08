---
name: logs-and-traces-stores
description: "Usar al configurar Loki (logs) y Tempo (trazas): almacenamiento en objeto, retención, etiquetas e indexado."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Almacenes de logs y trazas (Loki y Tempo)

## Cuándo aplicar y cuándo no
- Aplica al desplegar/configurar Loki y Tempo y al decidir qué etiquetas llevan los logs.
- No aplica a las métricas derivadas de trazas (ver `tempo-and-service-graphs`) ni al aislamiento por tenant (ver `multi-tenant-observability`).

## Reglas
- **MUST** usar almacenamiento de objetos (S3 en AWS, MinIO en local) para chunks y bloques; el disco local solo para WAL/caché.
- **MUST** habilitar retención de Loki en el compactor: `compactor.retention_enabled: true`, `compactor.delete_request_store` y `limits_config.retention_period`; sin `retention_enabled` el compactor solo compacta.
- **MUST** usar periodo de índice de 24h (requisito de la retención) y esquema TSDB (versión de `schema` por confirmar: TODO-VERIFY).
- **MUST** mantener pocas etiquetas de Loki, de baja cardinalidad (`namespace`, `app`, `level`); IDs de usuario, de traza o de petición van en el cuerpo del log, no como etiqueta.
- **MUST** fijar retención de bloques de trazas en Tempo (compactor) con un valor menor que el de logs.
- **SHOULD** correlacionar logs y trazas con `trace_id` en el cuerpo (JSON) y derived fields en Grafana.
- **SHOULD** retención diferenciada por flujo (`retention_stream`) para logs de auditoría frente a debug.
- **MUST NOT** guardar PII ni secretos en logs (ver `logging-rules`).

## Por qué
Loki indexa etiquetas, no contenido: una etiqueta de alta cardinalidad multiplica los streams y degrada ingestión y consulta. Sin retención explícita el bucket crece sin límite y el coste es el principal riesgo. Las trazas son voluminosas y poco útiles pasados días, de ahí retención corta.

## Ejemplos
### Mal
```yaml
# promtail/collector: etiqueta por usuario y por traza
labels: { user_id: "{{ .user }}", trace_id: "{{ .trace }}" }
```
### Bien
```yaml
compactor:
  working_directory: /data/retention
  retention_enabled: true
  retention_delete_delay: 2h
  delete_request_store: s3
limits_config:
  retention_period: 744h          # 31 dias
  retention_stream:
    - selector: '{level="debug"}'
      priority: 1
      period: 72h
```
```text
{namespace="payments", app="orders-api", level="error"} |= "trace_id=4bf92f3577b34da6"
```

## Checklist de revisión
- [ ] Almacén de objetos configurado; credenciales por rol/secreto, no literales.
- [ ] `retention_enabled` y `delete_request_store` presentes.
- [ ] Etiquetas de logs limitadas y sin IDs únicos.
- [ ] Retención de Tempo definida.
- [ ] `trace_id` en logs estructurados.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Regla Conftest para Loki sin retención | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de etiquetas de logs | 3 | agente revisor |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `logging-rules`, `cardinality-and-cost-governance`, `tempo-and-service-graphs`, `multi-tenant-observability`.
- Fuentes oficiales: https://grafana.com/docs/loki/latest/operations/storage/retention/ (verificado 2026-11-07: claves del compactor, índice 24h, `retention_stream`). Config de retención de Tempo (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Preparado para AWS, no verificado en real. En local MinIO sustituye a S3: no se reproducen políticas de bucket, KMS ni lifecycle de S3.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
