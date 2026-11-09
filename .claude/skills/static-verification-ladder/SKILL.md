---
name: static-verification-ladder
description: "Usar al verificar Terraform/IaC sin desplegar: validate, tflint, Checkov/Trivy, OPA sobre HCL o plan, mock providers. Define el techo de madurez."
metadata:
  block: "29-cloud-readiness"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Escalera de verificación estática

## Cuándo aplicar y cuándo no
- Aplica a cualquier módulo Terraform de un proyecto generado y a su pipeline de CI.
- No aplica a verificación en una cuenta real: ADR-0004 prohíbe desplegar y ADR-0037 prohíbe `terraform plan` contra una cuenta AWS, vacía o no.

## Reglas
- **MUST** recorrer los peldaños en orden y detenerse en el primero que falle:
  1. `terraform fmt -check` y `terraform validate` (con `terraform init -backend=false`).
  2. `tflint` (reglas del provider AWS).
  3. Checkov o Trivy en modo config sobre el directorio (`checkov -d .`, `trivy config .`), más las reglas propias de `policies/iac-checks/`.
  4. OPA/Conftest con Rego de `policies/opa-conftest/` sobre HCL (`conftest test --parser hcl2`) o sobre JSON de plan generado con providers simulados.
  5. `terraform test` con `mock_provider` para comprobar lógica de módulos sin credenciales.
- **MUST** que ningún peldaño requiera credenciales AWS ni red hacia AWS; si lo pide, el peldaño no pertenece a la escalera.
- **MUST NOT** ejecutar `terraform plan` ni `apply` contra AWS. Un plan solo es válido con providers simulados o salida sintética.
- **MUST** reportar el resultado con la etiqueta de `maturity-labels`: llegar al peldaño 5 significa "validada estáticamente", nunca más.
- **SHOULD** versionar las excepciones de Checkov/Trivy con justificación y fecha de revisión.
- **SHOULD** ejecutar la escalera en CI y en pre-commit local (peldaños 1 a 3).

## Por qué
Cada peldaño atrapa una clase distinta de error (sintaxis, convenciones del provider, seguridad, políticas de negocio, lógica). Ninguno prueba que AWS acepte el recurso: cuotas, permisos y límites de servicio solo se ven en real. Por eso el techo declarado es "preparado para AWS, no verificado en real".

## Ejemplos
### Mal
```text
terraform plan -out=tfplan   # con credenciales de la cuenta de desarrollo (prohibido por ADR-0037)
```
### Bien
```makefile
verify-iac:
	terraform fmt -check -recursive
	terraform init -backend=false && terraform validate
	tflint --recursive
	checkov -d . --quiet
	conftest test . --parser hcl2 -p policies/opa-conftest
	terraform test
```
```text
Resultado: peldaños 1-5 superados. Madurez: validada estáticamente; preparado para AWS, no verificado en real.
```

## Checklist de revisión
- [ ] El pipeline no tiene credenciales AWS ni `plan`/`apply` reales.
- [ ] Los cinco peldaños están, o falta uno con motivo escrito.
- [ ] Las excepciones tienen justificación.
- [ ] El README del módulo lleva etiqueta de madurez.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Afirmaciones honestas y etiqueta en READMEs con Terraform | 1 | `factory/validators/honest_claims.py` |
| Hook de etiqueta al editar | 2 | `.claude/hooks/post-tool-use/maturity_label_check.py` |
| Rego de ejemplo | 1 | `policies/opa-conftest/` |
| Checkov personalizado | 1 | `policies/iac-checks/` (solo README; reglas pendientes) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `maturity-labels`, `cost-estimation`, `honest-claims-policy`, `compliance-as-code`.
- Fuentes: `catalog/adr/0004-no-desplegar-nunca-en-aws.md`, `catalog/adr/0037-terraform-plan-contra-una-cuenta-aws-vacia.md`; documentación de Terraform, tflint, Checkov, Trivy y Conftest.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
