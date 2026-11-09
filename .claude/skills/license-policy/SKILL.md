---
name: license-policy
description: "Usar al decidir qué licencias de dependencias se permiten, cómo se comprueban a partir del SBOM y cómo se gestionan excepciones (copyleft, no comerciales)."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Política de licencias

## Cuándo aplicar y cuándo no
- Aplica a dependencias directas y transitivas (Maven, npm, paquetes del SO en imágenes) y a componentes de infraestructura que se adopten.
- No aplica a asesoría legal: la lista de licencias admitidas es un borrador por confirmar con el asesor legal de la organización.

## Reglas
- **MUST** mantener una lista versionada en tres categorías: permitidas (p. ej. Apache-2.0, MIT, BSD), a revisar (p. ej. MPL-2.0, LGPL, EPL) y prohibidas (p. ej. AGPL, SSPL, licencias "no comercial"). Contenido por confirmar con legal.
- **MUST** evaluar licencias automáticamente desde el SBOM CycloneDX (Dependency-Track las evalúa con políticas de licencia) o con Trivy `--scanners license` (confirmado en la referencia CLI, 2026-11-07).
- **MUST** fallar el gate ante licencia prohibida o desconocida/ausente (`NOASSERTION`) hasta resolverla.
- **MUST** registrar excepciones en un fichero versionado con justificación, aprobador y caducidad.
- **MUST NOT** adoptar componentes con licencia de pago o de uso restringido por defecto (D16); si hay alternativa OSS, usarla.
- **SHOULD** vigilar cambios de licencia en actualizaciones (relicenciados a BSL/SSPL) en la revisión de upgrades.
- **SHOULD** generar un fichero de avisos (`THIRD-PARTY-NOTICES`) en releases distribuidos.
- **MUST** tratar la licencia del propio proyecto generado como decisión del dueño, no del agente.

## Por qué
Una dependencia AGPL en un servicio SaaS puede obligar a publicar código propio; descubrirlo en una auditoría es caro. Automatizar sobre el SBOM hace la comprobación barata y repetible. El agente no sustituye al asesor legal: solo detecta y escala.

## Ejemplos
### Mal
```text
# se añade sin mirar la licencia
mvn dependency:add com.example:shiny-lib:1.0.0
```
### Bien
```yaml
# license-policy.yaml (borrador, pendiente de confirmar con legal)
allowed: [Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC]
review:  [MPL-2.0, LGPL-2.1-only, LGPL-3.0-only, EPL-2.0]
denied:  [AGPL-3.0-only, SSPL-1.0]
unknown: fail
exceptions:
  - component: "pkg:maven/com.example/legacy-lib"
    license: LGPL-3.0-only
    reason: "enlazado dinámico, sin modificaciones"
    approved_by: "legal@example.com"
    expires: "2027-06-30"
```
```text
trivy fs --scanners license --severity HIGH,CRITICAL .
```

## Checklist de revisión
- [ ] Lista de licencias versionada y marcada como pendiente de legal.
- [ ] Gate de licencias en CI con licencia desconocida = fallo.
- [ ] Excepciones con aprobador y caducidad.
- [ ] Sin componentes de pago por defecto.
- [ ] Avisos de terceros generados en releases.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Gate de licencias sobre SBOM / Trivy | 1 | pipeline del proyecto generado (pendiente en `gates/`) |
| Regla Conftest sobre `license-policy.yaml` (exceptions con `expires`) | 1 | pendiente (`policies/opa-conftest/`) |
| Confirmación legal de la lista | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sbom`, `third-party-risk`, `dependency-security`, `supply-chain`.
- Fuentes: SPDX license list https://spdx.org/licenses/ ; Trivy https://trivy.dev/latest/docs/ (2026-11-07). Normativa/legal: borrador por confirmar.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
