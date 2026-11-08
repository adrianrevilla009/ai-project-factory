---
name: admission-verification
description: "Usar al definir qué imágenes admite el clúster: Kyverno verifyImages (firma, digest, atestaciones) y registros permitidos antes de ejecutar pods."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Verificación en admisión (Kyverno)

## Cuándo aplicar y cuándo no
- Aplica a políticas de admisión del clúster (EKS en AWS, kind/k3d en local) sobre Pods y workloads.
- No aplica a cómo se firma (ver `image-signing-and-provenance`) ni a seguridad general de pods (ver `container-and-k8s-security`).

## Reglas
- **MUST** exigir en admisión: imagen de un registro permitido, firma válida con identidad/issuer esperados, y referencia por digest (`mutateDigest`/`verifyDigest`).
- **MUST** rollout por fases: `Audit` en dev, luego `Enforce` en staging y prod, con informes revisados antes de pasar a `Enforce`.
- **MUST** que el registro permitido en runtime sea ECR (réplica cross-region); **MUST NOT** permitir pull desde Harbor ni registros públicos en prod.
- **MUST** definir excepciones por namespace con lista explícita (p. ej. `kube-system`) y revisión periódica; **MUST NOT** excluir un namespace de aplicación.
- **SHOULD** verificar atestaciones (SBOM/procedencia) con `attestations` para prod.
- **MUST** configurar `webhookConfiguration.timeoutSeconds` y asegurar disponibilidad HA de Kyverno; decidir de forma explícita fail-open o fail-closed y documentarla (comprobar `failurePolicy` por versión).
- **MUST** gestionar la política como código (GitOps) y probarla estáticamente (`kyverno test`, comprobar al fijar la versión).
- **MUST NOT** afirmar que la política está validada en un clúster real: queda "preparada para AWS, no verificada en real".

## Por qué
La verificación en CI se puede saltar con un `kubectl apply` manual. La admisión es el último control: aunque alguien tenga acceso al clúster, solo corre lo firmado por el pipeline. Hacerlo por fases evita bloquear workloads legítimos por una identidad mal escrita.

## Ejemplos
### Mal
```yaml
verifyImages:
  - imageReferences: ["*"]
    attestors:
      - entries:
          - keyless:
              subject: "*"
              issuer: "*"
```
(acepta cualquier firmante)
### Bien
Ver `policies/kyverno/verify-image-signatures.yaml`; extracto:
```yaml
verifyImages:
  - imageReferences: ["registry.example.com/*"]
    failureAction: Enforce
    mutateDigest: true
    verifyDigest: true
    required: true
    attestors:
      - entries:
          - keyless:
              issuer: "https://token.actions.githubusercontent.com"
              subject: "https://github.com/example-org/*"
              rekor: { url: https://rekor.sigstore.dev }
```
Campos confirmados en https://kyverno.io/docs/policy-types/cluster-policy/verify-images/sigstore/ (2026-11-07). En local (kind/k3d) NO se reproduce ECR ni la replicación; usar un registro local de prueba con la misma política.

## Checklist de revisión
- [ ] Subject e issuer concretos, sin comodines totales.
- [ ] Registros permitidos limitados a ECR en prod.
- [ ] Fase Audit completada antes de Enforce.
- [ ] Excepciones de namespace listadas y justificadas.
- [ ] Kyverno en HA con política de fallo documentada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Política de verificación de firmas | 1 | `policies/kyverno/verify-image-signatures.yaml` |
| Política de registros permitidos y sin `latest` | 1 | pendiente (`policies/kyverno/`) |
| Aprobación del paso a Enforce | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `image-signing-and-provenance`, `container-and-k8s-security`, `zero-trust`, `promotion-between-environments`.
- Fuentes: Kyverno verifyImages https://kyverno.io/docs/policy-types/cluster-policy/verify-images/sigstore/ (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
