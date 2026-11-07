---
name: supply-chain
description: "Usar al definir cómo se construyen, firman y verifican artefactos e imágenes (SBOM, niveles SLSA, firmas con cosign)."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Cadena de suministro: SBOM, SLSA, cosign

## Cuándo aplicar y cuándo no
- Aplica al pipeline de build/publicación de artefactos (JAR, imágenes OCI, bundles frontend) y a la verificación antes de desplegar.
- No aplica al escaneo de CVE en sí (ver `dependency-security`) ni a la generación detallada de SBOM con CycloneDX (ver `sbom-generation`).

## Reglas
- **MUST** generar un SBOM por artefacto en cada release (CycloneDX o SPDX) y conservarlo junto al artefacto.
- **MUST** construir en CI desde el commit etiquetado en un entorno efímero y sin acceso de escritura manual; **MUST NOT** publicar artefactos desde máquinas de desarrollo.
- **MUST** firmar las imágenes y artefactos con cosign (Sigstore); preferir firma sin clave (keyless/OIDC) o claves en KMS; **MUST NOT** guardar claves de firma en el repositorio.
- **MUST** emitir atestaciones de procedencia (SLSA provenance) y SBOM como atestación asociada a la imagen.
- **MUST** verificar firma y procedencia antes de admitir un artefacto en el clúster (admission control: Kyverno `verifyImages`); referenciar imágenes por digest `@sha256:`, no por tag mutable.
- **MUST** fijar acciones de CI por SHA de commit y limitar permisos del token de CI (`permissions:` mínimos).
- **SHOULD** apuntar a un nivel SLSA objetivo explícito (p. ej. nivel de build 2 → 3) y declarar el que realmente se cumple; **MUST NOT** afirmar un nivel sin evidencia.
- **SHOULD** buscar builds reproducibles (ver `reproducible-builds`).
- **SHOULD** usar registro propio (Harbor, sin licencia de pago) con política de solo imágenes firmadas.
- Honestidad: la fábrica no despliega ni firma en real; todo esto queda como "validado estáticamente".

## Por qué
Los ataques a la cadena (dependencia comprometida, pipeline manipulado, imagen sustituida) evitan los controles del código. Firmar y verificar crea un vínculo comprobable entre fuente, build y lo que corre; el SBOM permite responder en horas a "¿usamos la biblioteca X?".

## Ejemplos
### Mal
```text
docker push registry.example.com/app:latest     # desde el portatil, sin firma, tag mutable
```
### Bien
```text
# En CI, tras construir (TODO-VERIFY sintaxis con la version de cosign adoptada)
cosign sign registry.example.com/app@sha256:<digest>
cosign attest --predicate sbom.cdx.json --type cyclonedx registry.example.com/app@sha256:<digest>
```
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: verify-image-signatures }
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-cosign-signature
      match: { any: [ { resources: { kinds: [Pod] } } ] }
      verifyImages:
        - imageReferences: ["registry.example.com/*"]
          attestors: [ { entries: [ { keyless: { issuer: "https://token.actions.githubusercontent.com", subject: "https://github.com/example-org/*" } } ] } ]
```
Campos de Kyverno (`validationFailureAction`, `verifyImages`) TODO-VERIFY contra la versión elegida.

## Checklist de revisión
- [ ] SBOM generado y almacenado por release.
- [ ] Artefactos firmados; verificación obligatoria en admisión.
- [ ] Imágenes por digest; acciones de CI fijadas por SHA.
- [ ] Nivel SLSA declarado con evidencia.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno: verificar firmas de imagen | 1 | pendiente (`policies/kyverno/`) |
| Conftest: acciones sin fijar por SHA, permisos de workflow | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión humana del pipeline de release | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sbom-generation`, `reproducible-builds`, `container-images`, `container-and-k8s-security`, `dependency-security`.
- Fuentes: slsa.dev, documentación de Sigstore/cosign, CycloneDX y Kyverno, consultadas 2026-11-07, TODO-VERIFY versiones.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
