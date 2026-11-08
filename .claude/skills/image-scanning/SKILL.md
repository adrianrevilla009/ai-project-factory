---
name: image-scanning
description: "Usar al configurar el escaneo de vulnerabilidades de imágenes y dependencias con Trivy o Grype: umbrales, exclusiones con caducidad y gate de CI."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Escaneo de imágenes (Trivy / Grype)

## Cuándo aplicar y cuándo no
- Aplica al pipeline de build/promoción de imágenes OCI y al escaneo periódico del registro.
- No aplica a SAST/DAST (ver `security-testing-sast-dast`) ni a SLAs de remediación (ver `vulnerability-sla-and-incident-response`).

## Reglas
- **MUST** usar escáneres sin licencia de pago por defecto: Trivy y/o Grype (D16). Xray/Prisma solo como adaptador opcional.
- **MUST** escanear en CI tras el build y antes de publicar/promover; **MUST** bloquear con `CRITICAL` y `HIGH` con corrección disponible.
- **MUST** reescanear periódicamente imágenes ya publicadas (aparecen CVE nuevas); Harbor puede programar escaneo, y Dependency-Track vigila los SBOM.
- **MUST** gestionar excepciones en un fichero versionado (`.trivyignore` o VEX) con motivo, responsable y fecha de caducidad; **MUST NOT** ignorar sin caducidad.
- **MUST** fijar la versión del escáner y actualizar su base de datos de forma controlada (comprobar política de caché de DB en CI).
- **SHOULD** usar imágenes base mínimas (ver `docker-multistage`) para reducir superficie.
- **SHOULD** activar también escaneo de misconfiguraciones y secretos en la imagen (`--scanners vuln,secret`).
- **MUST** guardar el informe (SARIF/JSON) como evidencia del gate.

## Por qué
Una imagen limpia el día del build no lo está un mes después. Bloquear solo lo corregible evita paralizar equipos por CVE sin parche, mientras que el reescaneo cubre las nuevas. Las excepciones sin caducidad se convierten en deuda invisible.

## Ejemplos
### Mal
```text
trivy image registry.example.com/shop/orders:latest || true
```
### Bien
```text
trivy image \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  --exit-code 1 \
  --ignorefile .trivyignore \
  --format sarif --output trivy.sarif \
  registry.example.com/shop/orders@sha256:<digest>
```
Flags `--severity`, `--ignore-unfixed`, `--exit-code`, `--ignorefile`, `--format`, `--scanners`, `--vex` verificados en https://trivy.dev/latest/docs/references/configuration/cli/trivy_image/ (2026-11-07). Equivalente Grype: `grype <imagen> --fail-on high` (comprobar al fijar la versión).
```text
# .trivyignore: motivo y caducidad en comentario (revisado por el gate de higiene)
# CVE-2099-0001 sin parche; owner=team-shop; expires=2027-01-31
CVE-2099-0001
```

## Checklist de revisión
- [ ] Gate bloquea HIGH/CRITICAL corregibles; `|| true` no existe.
- [ ] Excepciones con motivo, owner y caducidad.
- [ ] Reescaneo periódico configurado.
- [ ] Informe SARIF/JSON archivado.
- [ ] Versión del escáner fijada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Gate de CI con `--exit-code 1` | 1 | workflow del proyecto generado (plantilla en `github-actions`) |
| Detección de `|| true` tras el escáner | 1 | pendiente (`policies/semgrep/`) |
| Revisión de excepciones caducadas | 3 | agente `security-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sbom`, `docker-multistage`, `dependency-security`, `vulnerability-sla-and-incident-response`, `security-gates`.
- Fuentes: Trivy https://trivy.dev/latest/docs/ ; Grype https://github.com/anchore/grype (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
