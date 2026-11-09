---
name: renovate-dependabot-policy
description: "Usar al configurar actualización automática de dependencias (Renovate o Dependabot): agrupación, cadencia, automerge y reglas de revisión."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Política Renovate / Dependabot

## Cuándo aplicar y cuándo no
- Aplica al crear el repositorio de un proyecto generado o al cambiar cómo se actualizan dependencias, imágenes base y GitHub Actions.
- No aplica a parches de emergencia por CVE crítico (flujo de `dependency-security`, que salta la cadencia).

## Reglas
- **MUST** tener un bot de actualización activo: Dependabot (integrado en GitHub, sin coste) o Renovate (OSS autoalojable).
- **MUST** cubrir ecosistemas: `maven`, `npm`, `docker`/imágenes base, `github-actions` y Terraform si existe.
- **MUST** agrupar en un PR: dependencias de Spring Boot, de test y minor/patch de frontend; **MUST NOT** abrir un PR por cada patch.
- **MUST** exigir CI verde y revisión humana para `major`; el automerge solo para `patch` de test/dev y con CI verde.
- **MUST** fijar cadencia (semanal) y límite de PRs abiertos (p. ej. 5).
- **MUST** que las actualizaciones del BOM corporativo se propongan sobre el BOM, no sobre versiones literales en módulos (ver `bom-management`).
- **SHOULD** fijar imágenes Docker por digest además de por tag (ver `container-images`) y dejar que el bot lo actualice.
- **MUST NOT** automergear dependencias de runtime ni plugins de build.
- **MUST NOT** guardar tokens del bot en el repo.

## Por qué
Sin automatización las dependencias envejecen hasta que un CVE obliga a saltar cinco majors de golpe. Con ruido (un PR por patch) el equipo deja de mirarlos. Agrupar y limitar mantiene la señal.

## Ejemplos
### Mal
```yaml
version: 2
updates:
  - package-ecosystem: maven
    directory: "/"
    schedule: { interval: daily }   # sin agrupar, sin límite
```
### Bien
```yaml
version: 2
updates:
  - package-ecosystem: maven
    directory: "/"
    schedule: { interval: weekly }
    open-pull-requests-limit: 5
    groups:
      spring-boot:
        patterns: ["org.springframework.boot*"]
      test-libs:
        dependency-type: development
  - package-ecosystem: github-actions
    directory: "/"
    schedule: { interval: weekly }
```
(Claves de `dependabot.yml` a contrastar con la documentación vigente de GitHub)

## Checklist de revisión
- [ ] Bot activo para todos los ecosistemas presentes.
- [ ] Agrupación y límite de PRs configurados.
- [ ] Automerge limitado a patch de test/dev.
- [ ] Majors con revisión humana y notas de migración.
- [ ] Sin secretos en la configuración.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Existencia de `dependabot.yml` o `renovate.json` en el proyecto generado | 1 | pendiente: regla de validación del proyecto generado |
| CI verde obligatorio antes de merge | 1 | protección de rama (proyecto generado) |
| Revisión de majors | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `bom-management`, `dependency-hygiene`, `dependency-security`, `container-images`, `release-automation`.
- Fuentes: documentación de GitHub Dependabot y de Renovate (docs.renovatebot.com).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
