---
name: release-automation
description: "Usar al diseñar el pipeline de release: versión desde Conventional Commits, changelog, tag, artefactos firmados con SBOM y publicación sin pasos manuales ni despliegue desde la fábrica."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Automatización de releases

## Cuándo aplicar y cuándo no
- Aplica al definir cómo un commit en la rama principal se convierte en versión, tag, artefactos y notas de release.
- No aplica al despliegue en entornos: la fábrica nunca despliega (ADR-0004) y el proyecto generado queda "preparado para AWS, no verificado en real".

## Reglas
- **MUST** derivar el tipo de incremento (major/minor/patch) de Conventional Commits y de `versioning-semver-snapshots`, no de decisión manual ad hoc.
- **MUST** hacer la release desde CI sobre la rama principal limpia y con la verificación completa en verde; **MUST NOT** liberar desde una máquina local.
- **MUST** generar changelog automático a partir de los commits y crear un tag anotado `vX.Y.Z`.
- **MUST** publicar en cada release: artefactos, SBOM (`sbom-generation`), informe de licencias y, si aplica, imagen con digest (`container-images`).
- **SHOULD** usar versiones CI-friendly (`${revision}` con `flatten-maven-plugin`) o `maven-release-plugin`; elegir una y documentarla en un ADR.
- **MUST** hacer la release idempotente: re-ejecutarla sobre el mismo tag no debe producir artefactos distintos (`reproducible-builds`).
- **MUST NOT** reescribir ni borrar un tag publicado; corregir con una nueva versión patch.
- **MUST** exigir aprobación humana antes de promocionar a entornos productivos (gate); el agente MUST NOT crear ni editar `approvals/*.json`.
- **SHOULD** limitar secretos de publicación a un entorno protegido de CI con permisos mínimos.

## Por qué
Una release manual depende de quién la haga y de su estado; una automatizada es repetible, auditable y rápida de revertir hacia delante. Los gates humanos se mantienen porque promocionar a producción es una decisión de negocio, no de build.

## Ejemplos
### Mal
```text
# En el portátil de alguien
mvn release:prepare release:perform -DskipTests
git tag -f v1.2.0 && git push --force origin v1.2.0
```
### Bien
```yaml
# Esquema de job de release (adaptar al motor de CI)
release:
  if: branch == main && tag == ""
  steps:
    - run: ./mvnw -B verify                      # tests, enforcer, SBOM, licencias
    - run: tools/compute-next-version.sh         # pendiente: script del proyecto, lee Conventional Commits
    - run: ./mvnw -B -Drevision=$NEXT_VERSION deploy   # repositorio de artefactos corporativo
    - run: git tag -a "v$NEXT_VERSION" -m "release $NEXT_VERSION" && git push origin "v$NEXT_VERSION"
    - run: tools/publish-release-notes.sh        # pendiente: changelog + enlaces a SBOM
```
```text
feat(orders): add cancellation endpoint      -> minor
fix(payments): handle duplicate webhook      -> patch
feat(api)!: remove v1 order payload          -> major
```

## Criterios de decisión y trampas
### Cómo decidir
- Automatiza la versión, el registro de cambios, el artefacto y la publicación desde la rama principal a partir de commits convencionales.
- La release es un evento reproducible, no un ritual manual.
### Trampas frecuentes
- Releases manuales con pasos olvidados.
- Etiquetas que no corresponden a lo publicado.
- Publicar desde una máquina local.
- Sin posibilidad de repetir la release.
- Registro de cambios editado a mano e incompleto.
### Evidencia
- Una release de prueba se ejecuta de principio a fin sin intervención manual.

## Checklist de revisión
- [ ] La versión sale de los commits, no se edita a mano.
- [ ] Release solo desde CI y rama principal.
- [ ] Tag anotado; nunca se reescribe.
- [ ] Artefactos + SBOM + licencias adjuntos.
- [ ] Promoción a producción pasa por gate humano.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validación de mensajes Conventional Commits | 2 | hook de commit (`.claude/hooks/`, pendiente de confirmar nombre) |
| Revisión del pipeline de release | 3 | agente `code-reviewer` |
| Protección de tags y rama principal | 1 | pendiente (configuración del repositorio del proyecto) |
| Aprobación de promoción | 4 | gate humano |

## Relacionados, fuentes y mantenimiento
- Relacionados: `versioning-semver-snapshots`, `sbom-generation`, `reproducible-builds`, `container-images`, `license-compliance`.
- Fuentes: conventionalcommits.org, semver.org, documentación de maven-release-plugin y flatten-maven-plugin.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
