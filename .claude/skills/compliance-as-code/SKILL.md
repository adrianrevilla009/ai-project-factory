---
name: compliance-as-code
description: "Usar al convertir requisitos de cumplimiento AWS en controles verificables: Config rules, conformance packs, Checkov/Conftest en CI y evidencias."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Cumplimiento como código

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica al mapear un requisito (interno o normativo) a un control automatizado en tres capas: CI (preventivo), SCP (preventivo en cuenta) y Config/Security Hub (detectivo).
- No aplica a interpretar normativa: cualquier marco (ENS, ISO 27001, RGPD) es borrador por confirmar con fuente oficial.

## Reglas
- **MUST** que cada control tenga: id, requisito de origen, capa (CI/SCP/Config), responsable y modo de evidencia.
- **MUST** ejecutar en CI, sobre el plan de Terraform, Checkov y Conftest/OPA; el fallo bloquea el merge.
- **MUST** reflejar los controles detectivos como Config rules o conformance packs gestionados por Terraform.
- **MUST** registrar excepciones en fichero versionado con motivo, dueño y fecha de caducidad; nunca `#checkov:skip` sin referencia.
- **SHOULD** preferir checks nativos de Checkov antes de escribir custom; los custom van en `policies/iac-checks/`.
- **SHOULD** generar evidencias (informe de CI, estado de Config) como artefactos retenibles.
- **MUST NOT** declarar "cumple" un marco normativo: la fábrica solo ofrece controles técnicos; la conformidad la decide una revisión humana externa.
- **MUST NOT** afirmar que un control funciona en AWS real: estado máximo "validado estáticamente".

## Por qué
Un control sin automatización se olvida; uno solo detectivo llega tarde. Tres capas dan defensa en profundidad y trazabilidad de la excepción.

## Ejemplos
### Mal
```hcl
resource "aws_s3_bucket" "b" {
  #checkov:skip=CKV_AWS_18
  bucket = "example-b"
}
```
### Bien
```hcl
resource "aws_s3_bucket" "b" {
  #checkov:skip=CKV_AWS_18:EXC-2026-014 logs de acceso en bucket central, caduca 2027-03-31
  bucket = "example-b"
}
```
```rego
package main

deny contains msg if {
  some r in input.resource_changes
  r.type == "aws_db_instance"
  not r.change.after.storage_encrypted
  msg := sprintf("%s: RDS sin cifrado", [r.address])
}
```

## Checklist de revisión
- [ ] Cada control tiene id, origen, capa y dueño.
- [ ] CI ejecuta Checkov y Conftest sobre el plan.
- [ ] Excepciones con motivo, id y caducidad.
- [ ] Ninguna afirmación de conformidad legal.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checks IaC custom | 1 | `policies/iac-checks/` (README; checks concretos pendientes) |
| Políticas Rego | 1 | `policies/opa-conftest/` (README; reglas concretas pendientes) |
| Validador de afirmaciones honestas | 2 | `factory/validators/honest_claims.py` |
| Aprobación de excepciones | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `scp-guardrails`, `org-cloudtrail-config-securityhub-guardduty`, `tagging-cost-allocation-budgets`, `verify-before-asserting`.
- Fuentes: documentación de Checkov, OPA/Conftest y AWS Config conformance packs (2026-11-07) — comprobar URLs; marcos normativos: borrador por confirmar.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
