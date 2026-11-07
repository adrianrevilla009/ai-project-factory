---
name: sbom
description: "Usar al generar, almacenar y consumir SBOM (CycloneDX), cargarlos en Dependency-Track y gestionar VEX para priorizar vulnerabilidades."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# SBOM, Dependency-Track y VEX

## Cuándo aplicar y cuándo no
- Aplica a cada build de release que produzca JAR, imagen OCI o bundle frontend.
- No aplica al escaneo de CVE en sí (ver `image-scanning`, `dependency-security`) ni a la firma (ver `image-signing-and-provenance`).

## Reglas
- **MUST** generar un SBOM CycloneDX por artefacto en CI: Maven con `cyclonedx-maven-plugin`, npm con `@cyclonedx/cyclonedx-npm`, imágenes con `trivy image --format cyclonedx` (TODO-VERIFY versiones de plugins).
- **MUST** generar SBOM de aplicación (dependencias declaradas) y de imagen (paquetes del SO) por separado; son complementarios.
- **MUST** publicar el SBOM junto al digest en el repositorio de artefactos y como atestación cosign (`image-signing-and-provenance`).
- **MUST** cargar los SBOM en Dependency-Track (OSS, sin licencia de pago) por proyecto y versión, para vigilancia continua de CVE nuevos sobre builds ya publicados.
- **MUST** usar VEX (CycloneDX VEX o OpenVEX) para declarar "no afectado/mitigado" con justificación; **MUST NOT** ignorar una CVE sin VEX o excepción con caducidad.
- **SHOULD** fallar el pipeline si el SBOM no se genera o está vacío.
- **MUST NOT** incluir secretos ni rutas internas en el SBOM publicado externamente.

## Por qué
Un SBOM convierte "¿usamos log4j?" en una consulta. Sin vigilancia continua, un artefacto limpio hoy tiene CVE mañana; Dependency-Track re-evalúa SBOM almacenados. VEX evita ruido: documenta por qué una CVE presente no es explotable.

## Ejemplos
### Mal
```text
# SBOM generado a mano, una vez, sin vincular al digest
echo "spring-boot, jackson, ..." > sbom.txt
```
### Bien
```xml
<plugin>
  <groupId>org.cyclonedx</groupId>
  <artifactId>cyclonedx-maven-plugin</artifactId>
  <executions>
    <execution><phase>package</phase><goals><goal>makeAggregateBom</goal></goals></execution>
  </executions>
  <configuration><outputFormat>json</outputFormat></configuration>
</plugin>
```
```text
trivy image --format cyclonedx --output sbom-image.cdx.json registry.example.com/shop/orders@sha256:<digest>
cosign attest --type cyclonedx --predicate sbom-image.cdx.json registry.example.com/shop/orders@sha256:<digest>
```
Flag `--format cyclonedx` verificado en https://trivy.dev/latest/docs/references/configuration/cli/trivy_image/ (2026-11-07). `cosign attest --type cyclonedx`: TODO-VERIFY. Subida a Dependency-Track vía su API REST (`PUT /api/v1/bom`, TODO-VERIFY) con clave de API en secreto de CI.

## Checklist de revisión
- [ ] SBOM CycloneDX por artefacto, vinculado al digest.
- [ ] Cargado en Dependency-Track con proyecto/versión.
- [ ] Atestación cosign adjunta.
- [ ] Exclusiones documentadas en VEX con justificación y caducidad.
- [ ] El pipeline falla si falta el SBOM.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Admisión exige firma/atestaciones del namespace | 1 | `policies/kyverno/verify-image-signatures.yaml` (atestación CycloneDX: pendiente) |
| Gate de pipeline "SBOM presente" | 1 | pendiente (`gates/`) |
| Revisión de VEX | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `supply-chain`, `image-scanning`, `license-policy`, `dependency-security`.
- Fuentes: CycloneDX https://cyclonedx.org/ ; Dependency-Track https://docs.dependencytrack.org/ (TODO-VERIFY API); Trivy (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
