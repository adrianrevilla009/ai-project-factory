---
name: promotion-between-environments
description: "Usar al definir cómo un artefacto avanza de dev a staging y prod: misma imagen por digest, sin rebuild, con gates y evidencias."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Promoción de artefactos entre entornos

## Cuándo aplicar y cuándo no
- Aplica a la promoción de imágenes OCI y paquetes entre repositorios/proyectos (dev, staging, prod) en el repositorio de artefactos.
- No aplica a la promoción de configuración en GitOps (ver `environment-promotion`, bloque 17) ni a releases de librerías públicas.

## Reglas
- **MUST** construir una sola vez; promover el mismo digest (`sha256`) entre entornos. **MUST NOT** reconstruir para prod.
- **MUST** promover copiando/re-etiquetando por digest hacia el proyecto del siguiente entorno (p. ej. `shop-dev` -> `shop-staging` -> `shop-prod`).
- **MUST** exigir antes de cada promoción: escaneo sin hallazgos bloqueantes, firma válida, SBOM presente (ver `image-scanning`, `image-signing-and-provenance`).
- **MUST** registrar en cada promoción: digest, origen, destino, quién/qué pipeline, evidencia de gate. La promoción a prod requiere aprobación humana (gate sagrado).
- **MUST** que la promoción a prod replique a ECR (cross-region) para el pull runtime; el manifiesto GitOps referencia el digest.
- **SHOULD** tags de entorno (`prod`) solo como alias informativos; **MUST NOT** desplegar por tag.
- **MUST NOT** permitir push manual a los proyectos de staging/prod; solo la identidad del pipeline de promoción.

## Por qué
Si prod ejecuta bytes distintos de los probados en staging, las pruebas no valen nada. El digest es la prueba de identidad; reconstruir introduce dependencias flotantes y timestamps. Limitar la escritura a la identidad de CI hace auditable cada salto.

## Ejemplos
### Mal
```text
# prod se reconstruye con el tag del commit
docker build -t registry.example.com/shop-prod/orders:1.4.2 .
docker push registry.example.com/shop-prod/orders:1.4.2
```
### Bien
```text
# promoción por digest, misma imagen
DIGEST=sha256:0000000000000000000000000000000000000000000000000000000000000000   # example
cosign verify registry.example.com/shop-staging/orders@$DIGEST \
  --certificate-identity-regexp 'https://github.com/example-org/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
crane copy registry.example.com/shop-staging/orders@$DIGEST \
           registry.example.com/shop-prod/orders:1.4.2
```
`crane copy` conserva el digest. Comprobar sintaxis exacta de `crane` y que el adaptador elegido preserve las firmas (referrers/tags `.sig`).

## Checklist de revisión
- [ ] El digest de prod coincide con el probado en staging.
- [ ] Gate de escaneo, firma y SBOM antes de promover.
- [ ] Aprobación humana registrada para prod.
- [ ] Solo la identidad de pipeline puede escribir en staging/prod.
- [ ] El despliegue referencia digest, no tag.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Admisión: solo imágenes firmadas y fijadas por digest | 1 | `policies/kyverno/verify-image-signatures.yaml` |
| Regla de repositorio: permisos de escritura solo a CI | 3 | revisión de configuración del adaptador |
| Aprobación de prod | 4 | revisión humana (`gates/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `artifact-repository-port`, `image-scanning`, `admission-verification`, `environment-promotion`.
- Fuentes: ECR replication https://docs.aws.amazon.com/AmazonECR/latest/userguide/replication.html (2026-11-07): solo replica contenido subido tras configurarla; usar backfill para lo previo.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
