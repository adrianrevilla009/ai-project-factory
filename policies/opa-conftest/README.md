# opa-conftest

Nueve políticas en Rego para [Conftest](https://www.conftest.dev), que evalúa ficheros de configuración (YAML, JSON, HCL, Dockerfile) contra reglas. Cada política `deny` un patrón que las skills prohíben.

**Estado: escritas y sin ejecutar.** Conftest y OPA no están instalados en el entorno de la fábrica; cada proyecto debe ejecutarlas y ajustarlas a la versión que adopte antes de fiarse de ellas.

| Fichero | Qué comprueba | Skill de origen |
|---|---|---|
| `github-actions-pinning.rego` | Toda acción de terceros en un flujo de GitHub Actions está fijada por SHA de 40 caracteres | `github-actions` |
| `dockerfile.rego` | Dockerfiles: la imagen base lleva etiqueta o digest, no usa `latest`, y el usuario final no es administrador | `container-images`, `docker-multistage` |
| `gitops-no-plain-secrets.rego` | Ningún `Secret` de Kubernetes con datos en claro en un repositorio GitOps | `secrets-in-gitops` |
| `argocd-gitops.rego` | Las aplicaciones de Argo CD no usan el proyecto `default` y los proyectos no admiten `*` como repositorio de origen ni como espacio de nombres de destino | `argo-cd`, `argo-rollouts` |
| `istio-mesh-security.rego` | Malla Istio: mTLS en modo estricto y políticas de autorización sin identidades comodín | `mtls-strict-and-peer-auth`, `authorization-policies` |
| `iam-no-wildcard-admin.rego` | Ninguna política de IAM concede la acción `*` sobre el recurso `*` | `cloud-iam-least-privilege` |
| `required-tags.rego` | Los recursos de un plan de Terraform llevan las etiquetas obligatorias | `tagging-cost-allocation-budgets` |
| `backup-vault-lock.rego` | Todo almacén de copias de AWS Backup tiene bloqueo de retención | `backup-vault-immutability-and-restore-tests` |
| `maturity-label.rego` | Un registro de madurez solo usa etiquetas permitidas y ninguna afirma verificación en AWS real | `maturity-labels`, `honest-claims-policy` |

## Uso
```bash
conftest test <fichero> -p policies/opa-conftest
conftest test --parser dockerfile -p policies/opa-conftest Dockerfile
conftest test --parser hcl2 -p policies/opa-conftest infra/
```
Las políticas usan la sintaxis moderna de Rego (`import rego.v1`), que exige una versión reciente de OPA y de Conftest.

## Convenciones
- Un fichero por tema, con la skill de origen y un ejemplo de uso en la cabecera.
- Los mensajes de `deny` explican qué corregir.
- Antes de adoptarlas, añade casos de prueba con la herramienta (`conftest verify`).
