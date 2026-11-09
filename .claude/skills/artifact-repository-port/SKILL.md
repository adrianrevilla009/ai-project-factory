---
name: artifact-repository-port
description: "Usar al diseñar o cambiar cómo el pipeline publica, promueve, retiene y traza artefactos (imágenes OCI, JAR, npm) tras un puerto agnóstico del repositorio."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Puerto de repositorio de artefactos

## Cuándo aplicar y cuándo no
- Aplica al definir el contrato entre el pipeline y el repositorio de artefactos (publicar, promover, retener, trazar) y al elegir adaptador.
- No aplica a la configuración interna de un producto concreto (ver sus runbooks) ni al registro runtime en AWS (ECR), que es el origen de pull en ejecución.

## Reglas
- **MUST** definir el puerto con cuatro capacidades: `publish(artifact, digest)`, `promote(digest, from, to)`, `retain(policy)` y `trace(digest) -> {commit, build, sbom, signature}`.
- **MUST** identificar artefactos por digest (`sha256`), nunca por tag mutable; los tags son alias de conveniencia.
- **MUST** que el adaptador por defecto sea sin licencia de pago (D16): Harbor para imágenes OCI; Nexus Community o Reposilite para Maven/npm. Artifactory/Xray solo como adaptador opcional.
- **MUST** que el pipeline dependa del puerto (ficheros `repository-port.yaml`), no de URLs ni CLIs de un producto en los workflows.
- **MUST** que el pull en runtime (EKS) venga de ECR con replicación cross-region; **MUST NOT** hacer pull desde Harbor en runtime.
- **MUST** guardar junto a cada digest: SBOM, firma y procedencia (ver `sbom`, `image-signing-and-provenance`).
- **SHOULD** una sola vía de escritura: solo CI publica; los humanos solo leen.
- **MUST NOT** afirmar que un adaptador está verificado en real: la fábrica no despliega (ADR-0004); es "preparado para AWS, no verificado en real".

## Por qué
Cambiar de Harbor a Artifactory (o al revés) no debe tocar 40 workflows. Si el contrato es promoción por digest + trazabilidad, el producto es intercambiable. Separar "registro de construcción" (Harbor, escaneo, firma) de "registro runtime" (ECR) evita que una caída del primero tumbe el escalado de pods.

## Ejemplos
### Mal
```yaml
# workflow acoplado al producto
- run: docker push harbor.example.com/shop/orders:latest
- run: curl -u admin:changeme https://harbor.example.com/api/v2.0/projects/shop/repositories/orders/artifacts/latest/labels
```
### Bien
```yaml
# repository-port.yaml (contrato; el adaptador lo interpreta)
port: artifact-repository
adapter: harbor            # harbor | nexus | reposilite | artifactory (opcional)
publish:
  by: digest
  require: [sbom, signature, provenance]
promote:
  path: [dev, staging, prod]
  mechanism: re-tag-by-digest   # sin rebuild
retain:
  policy: retention-and-cleanup
trace:
  fields: [git_commit, build_id, sbom_ref, signature_ref]
runtime_pull:
  registry: ecr
  replication: cross-region
```

## Criterios de decisión y trampas
### Cómo decidir
- Accede a los artefactos mediante un puerto implementable con distintos repositorios; elige la implementación por licencia, coste y funciones.
- Documenta qué funciones de pago no se asumen.
### Trampas frecuentes
- Dependencia directa de un producto en cada pipeline.
- Repositorios sin copia de seguridad.
- Permisos de escritura amplios.
- Sin política de retención.
- Funciones de pago asumidas.
### Evidencia
- Cambiar de repositorio toca una configuración y no cada pipeline.

## Checklist de revisión
- [ ] Los workflows usan el puerto, sin URLs de producto hardcodeadas.
- [ ] Todo artefacto se referencia por digest.
- [ ] El adaptador por defecto no requiere licencia de pago.
- [ ] El runtime hace pull de ECR, no de Harbor.
- [ ] Cada digest tiene SBOM, firma y procedencia enlazados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: `FROM` sin tag/digest o con `latest` | 1 | `policies/opa-conftest/dockerfile.rego` |
| Verificación de firma en admisión | 1 | `policies/kyverno/verify-image-signatures.yaml` |
| Revisión del `repository-port.yaml` y adaptadores | 3 | agente `code-reviewer` (regla de revisión humana del adaptador) |
| Regla Conftest que exija digest en manifiestos | 1 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `promotion-between-environments`, `retention-and-cleanup`, `sbom`, `image-signing-and-provenance`, `supply-chain`.
- Fuentes: Harbor https://goharbor.io/docs/ ; ECR replication https://docs.aws.amazon.com/AmazonECR/latest/userguide/replication.html (verificado 2026-11-07). Contrato `repository-port.yaml`: diseño propio de la fábrica, no es un estándar.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
