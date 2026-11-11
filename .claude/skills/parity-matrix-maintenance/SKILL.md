---
name: parity-matrix-maintenance
description: "Usar al añadir, cambiar o retirar un servicio AWS o su equivalente local y mantener catalog/parity-matrix.yaml coherente con los skills afectados."
metadata:
  block: "29-cloud-readiness"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Mantenimiento de la matriz de paridad

## Cuándo aplicar y cuándo no
- Aplica cuando un cambio introduce, sustituye o elimina un servicio AWS, un emulador local o un límite conocido.
- No aplica a la redacción de la matriz en un proyecto concreto (ver `local-parity-matrix`).

## Reglas
- **MUST** que toda fila de `catalog/parity-matrix.yaml` tenga `aws`, `local` (o `null` si no hay equivalente) y `not_reproduced` no vacío.
- **MUST** actualizar en el mismo cambio los skills que citan la fila (por ejemplo `aws-emulation`, `local-profiles`, `local-parity-matrix`) y `last_reviewed`.
- **MUST** que un servicio sin equivalente local tenga `local: null` y `not_reproduced` explícito, nunca eliminarse de la matriz.
- **MUST** declarar «no comprobado» el estado de un emulador mientras no esté contrastado con su documentación oficial (caso Streams de DynamoDB en LocalStack).
- **MUST** respetar ADR-0034 (kind por defecto, k3d alternativa) al editar la fila de EKS.
- **SHOULD** revisar la matriz al cambiar versión de un operador (CloudNativePG, Strimzi) o la política de licencias de un emulador (LocalStack, D16).
- **SHOULD** registrar el cambio en un ADR si altera una decisión cerrada D1 a D27.
- **MUST NOT** cambiar `local` a algo con licencia de pago por defecto.
- **MUST NOT** borrar un `not_reproduced` para "limpiar" la matriz.

## Por qué
La matriz es la fuente única de qué no se prueba en local. Si deriva de los skills, los proyectos generados heredan promesas falsas de fidelidad.

## Ejemplos
### Mal
```yaml
- { aws: S3, local: MinIO, not_reproduced: "" }
```
### Bien
```yaml
- { aws: S3, local: MinIO, not_reproduced: "Replicación, Object Lock completo" }
- { aws: "WAF, Shield, CloudFront", local: null, not_reproduced: "Todo" }
```
```text
Cambio: nueva fila SQS. Actualizar también aws-emulation y local-parity-matrix, y last_reviewed.
```

## Criterios de decisión y trampas
### Cómo decidir
- Revisa la matriz con una frecuencia fija y ante cambios en un emulador o servicio; cada fila cita su fuente.
- Declara «no comprobado» lo que no esté contrastado.
### Trampas frecuentes
- Una matriz que envejece.
- Filas sin fuente.
- Cambios sin revisión.
- Presentar la matriz como evidencia de funcionamiento real.
- Sin dueño.
### Evidencia
- Cada fila tiene fecha y fuente y hay un responsable de la revisión periódica.

## Checklist de revisión
- [ ] Todas las filas con `not_reproduced` no vacío.
- [ ] Skills afectados actualizados en el mismo cambio.
- [ ] Sin licencias de pago nuevas por defecto.
- [ ] comprobar donde falte comprobación oficial.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validación de esquemas del catálogo | 1 | `factory/validators/schemas_and_adrs.py` (comprobar que cubre `parity-matrix.yaml`) |
| Coherencia matriz vs. skills | 3 | revisión humana (script pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `local-parity-matrix`, `aws-emulation`, `local-profiles`, `honest-claims-policy`.
- Fuentes: `catalog/parity-matrix.yaml`, `catalog/adr/0034-kubernetes-local-kind-vs-k3d.md`.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
