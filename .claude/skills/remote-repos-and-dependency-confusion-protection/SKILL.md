---
name: remote-repos-and-dependency-confusion-protection
description: "Usar al configurar proxies de Maven/npm/OCI y repos virtuales para evitar dependency confusion, typosquatting y descargas directas de internet."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Repos remotos y protección contra dependency confusion

## Cuándo aplicar y cuándo no
- Aplica a `settings.xml` de Maven, `.npmrc`, configuración de proxy en Nexus/Reposilite/Harbor y a builds de CI.
- No aplica a la evaluación de vulnerabilidades de las dependencias (ver `dependency-security`) ni a licencias (ver `license-policy`).

## Reglas
- **MUST** que CI y desarrolladores resuelvan dependencias solo a través del repositorio corporativo (proxy/grupo); **MUST NOT** declarar `repositories` de internet directas en `pom.xml` ni registries en `.npmrc` del proyecto.
- **MUST** que los namespaces internos (`com.acme.*`, `@acme/*`) se resuelvan solo del repositorio interno: reglas de enrutado/exclusión (Nexus routing rules) o scoped registry en `.npmrc`.
- **MUST** reservar el scope npm y el groupId internos en los registros públicos cuando sea posible.
- **MUST** usar lockfiles con integridad (`package-lock.json`, `pnpm-lock.yaml`) y `npm ci`; en Maven fijar versiones y verificar checksums/firmas (TODO-VERIFY plugin de verificación).
- **MUST** deshabilitar el uso de snapshots y versiones por rango (`LATEST`, `RELEASE`, `^`) en releases.
- **SHOULD** cuarentena/retardo en nuevas versiones del proxy (p. ej. no aceptar versiones publicadas hace menos de N días; TODO-VERIFY soporte en el producto).
- **SHOULD** bloquear egress de los runners de build excepto hacia el repositorio corporativo.
- **MUST NOT** guardar credenciales en `settings.xml`/`.npmrc` versionados; usar variables de entorno.

## Por qué
Dependency confusion: si `@acme/utils` existe interno y alguien publica uno con versión mayor en el registro público, un resolutor mal configurado descarga el malicioso. Cerrar el origen de resolución y fijar el scope elimina el vector, no solo lo detecta.

## Ejemplos
### Mal
```text
# .npmrc: un solo registry público, sin scope
registry=https://registry.npmjs.org/
```
```xml
<repositories>
  <repository><id>central-mirror</id><url>https://repo1.maven.org/maven2</url></repository>
</repositories>
```
### Bien
```text
# .npmrc (credencial por entorno, no versionada)
@acme:registry=https://nexus.example.com/repository/npm-internal/
registry=https://nexus.example.com/repository/npm-group/
//nexus.example.com/repository/npm-group/:_authToken=${NPM_TOKEN}
```
```xml
<!-- settings.xml: todo pasa por el grupo corporativo -->
<mirrors>
  <mirror>
    <id>corp</id>
    <mirrorOf>*</mirrorOf>
    <url>https://nexus.example.com/repository/maven-group/</url>
  </mirror>
</mirrors>
```

## Checklist de revisión
- [ ] Sin repositorios de internet en `pom.xml` ni `.npmrc` de proyecto.
- [ ] Scope/groupId interno enrutado solo al repo interno.
- [ ] Lockfile con integridad y `npm ci` en CI.
- [ ] Sin rangos flotantes en releases.
- [ ] Sin tokens en ficheros versionados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep/Conftest: `<repositories>` en pom o registry público en `.npmrc` | 1 | pendiente (`policies/semgrep/`) |
| Hook de secretos para `_authToken` literal | 2 | `.claude/hooks/` (ver `secret-scanning-and-leak-response`) |
| Revisión de configuración del proxy | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dependency-security`, `supply-chain`, `artifact-repository-port`, `third-party-risk`.
- Fuentes: Nexus https://help.sonatype.com/en/repository-management.html (TODO-VERIFY routing rules en Community); npm scopes https://docs.npmjs.com/cli/configuring-npm/npmrc (TODO-VERIFY, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
