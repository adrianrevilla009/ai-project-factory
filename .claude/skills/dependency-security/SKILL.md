---
name: dependency-security
description: Usar al añadir, actualizar o auditar dependencias Maven/npm y al gestionar CVE conocidos en bibliotecas de terceros.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Seguridad de dependencias

## Cuándo aplicar y cuándo no
- Aplica a dependencias directas y transitivas (Maven, npm), imágenes base y plugins de build.
- No aplica a la procedencia y firma de artefactos (ver `supply-chain`) ni a la política de actualización automatizada (ver `renovate-dependabot-policy`).

## Reglas
- **MUST** ejecutar análisis de composición (SCA) en cada PR y de forma periódica sobre la rama principal: OWASP Dependency-Check (OSS) u OSV-Scanner; Trivy para imágenes. Sin herramientas de pago por defecto (D16).
- **MUST** hacer fallar el build ante vulnerabilidades con severidad `CRITICAL` (y `HIGH` explotables) sin excepción aprobada y con fecha de caducidad.
- **MUST** fijar versiones (sin rangos `LATEST`/`RELEASE`/`^` abiertos en producción) y usar un BOM/`dependencyManagement` común.
- **MUST** usar lockfile (`package-lock.json`) y `npm ci` en CI.
- **MUST** documentar cada excepción (suppression) con CVE, motivo, responsable y fecha de revisión; **MUST NOT** suprimir de forma global.
- **MUST** evaluar alcance real: la vulnerabilidad solo importa si el código vulnerable es alcanzable; registrar la conclusión.
- **SHOULD** minimizar dependencias; eliminar las no usadas (`mvn dependency:analyze`).
- **SHOULD** preferir bibliotecas mantenidas (actividad, releases, múltiples mantenedores) y revisar nuevas dependencias antes de añadirlas.
- **MUST** verificar que el paquete existe y es el correcto antes de instalarlo (typosquatting, nombres inventados por un LLM).
- **SHOULD** usar un repositorio proxy interno (Nexus/Artifactory OSS u otro sin licencia de pago) como único origen.

## Por qué
La mayor parte del código en ejecución es de terceros. Una CVE publicada se explota en días; sin inventario ni escaneo no se sabe si se está expuesto. Las dependencias transitivas son la fuente habitual de sorpresas.

## Ejemplos
### Mal
```xml
<dependency>
  <groupId>com.example</groupId><artifactId>lib</artifactId>
  <version>LATEST</version>
</dependency>
<!-- suppression global sin motivo -->
<suppress><cvssBelow>10</cvssBelow></suppress>
```
### Bien
```xml
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <version></version>
  <configuration>
    <failBuildOnCVSS>7</failBuildOnCVSS>
    <suppressionFiles><suppressionFile>dc-suppressions.xml</suppressionFile></suppressionFiles>
  </configuration>
</plugin>
```
```xml
<!-- dc-suppressions.xml: excepcion acotada y con caducidad -->
<suppress until="2027-01-31Z">
  <notes>CVE-0000-00000 example: ruta vulnerable no alcanzable. Owner: team-x. Ticket: SEC-123.</notes>
  <packageUrl regex="true">^pkg:maven/com\.example/lib@1\.2\..*$</packageUrl>
  <cve>CVE-0000-00000</cve>
</suppress>
```

## Checklist de revisión
- [ ] SCA en CI con umbral de fallo definido.
- [ ] Versiones fijadas y lockfile usado.
- [ ] Excepciones con motivo, dueño y caducidad.
- [ ] Dependencia nueva revisada (mantenimiento, licencia, nombre correcto).

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Dependency-Check/OSV-Scanner en CI | 1 | pendiente (workflow del proyecto generado) |
| Enforcer: sin versiones dinámicas | 1 | pendiente (reglas del parent pom, ver `enforcer-rules`) |
| Revisión humana de excepciones | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `supply-chain`, `dependency-hygiene`, `renovate-dependabot-policy`, `license-compliance`, `vulnerability-sla-and-incident-response`.
- Fuentes: documentación de OWASP Dependency-Check y OSV-Scanner; versiones y parámetros.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
