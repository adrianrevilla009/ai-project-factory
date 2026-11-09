---
name: license-compliance
description: "Usar al añadir dependencias, montar el informe de licencias en el build o revisar si una licencia de terceros es aceptable (AGPL, SSPL, GPL, licencias de pago)."
metadata:
  block: "09-build-supply-chain"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Cumplimiento de licencias de dependencias

## Cuándo aplicar y cuándo no
- Aplica a toda dependencia nueva o actualizada (Maven y npm), a imágenes base y a herramientas de plataforma elegidas por el agente.
- No aplica a la licencia del propio proyecto generado (decisión del cliente) ni a asesoría legal: este skill es un borrador operativo, la política definitiva la confirma el área legal con fuente oficial.

## Reglas
- **MUST** mantener una lista de licencias permitidas, a revisar y prohibidas en un único fichero versionado del proyecto (`legal/license-policy.yaml`).
- **MUST** permitir por defecto solo licencias permisivas: Apache-2.0, MIT, BSD-2/3-Clause, ISC, EPL-2.0, MPL-2.0 (a nivel de fichero, sin modificar).
- **MUST** tratar como "revisión humana" LGPL, EPL con exclusión secundaria y licencias duales.
- **MUST NOT** introducir AGPL, SSPL, BUSL, Commons Clause ni licencias de pago por defecto (D16); si se necesita una, abrir ADR.
- **MUST** generar el informe de licencias en cada build de CI y fallar si aparece una licencia prohibida o desconocida.
- **MUST** registrar toda excepción con dependencia, versión, motivo, aprobador y fecha de caducidad.
- **SHOULD** cruzar el informe con el SBOM (`sbom-generation`) para cubrir dependencias transitivas.
- **MUST NOT** copiar código de repositorios externos al proyecto sin verificar su licencia.

## Por qué
Una dependencia transitiva AGPL puede obligar a publicar el código del servicio. Descubrirlo antes de la auditoría cuesta un cambio de librería; después, una reescritura. Un fichero de política explícito hace que la decisión sea revisable y no dependa de la memoria del agente.

## Ejemplos
### Mal
```xml
<!-- Se añade una librería sin mirar su licencia ni la de sus transitivas -->
<dependency>
  <groupId>com.example</groupId>
  <artifactId>fancy-reports</artifactId>
  <version>2.1.0</version>
</dependency>
```
### Bien
```yaml
# legal/license-policy.yaml (borrador, confirmar con legal)
allowed: [Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, EPL-2.0]
review:  [LGPL-2.1, LGPL-3.0, MPL-2.0, CDDL-1.1]
denied:  [AGPL-3.0, SSPL-1.0, BUSL-1.1, GPL-3.0-only]
exceptions:
  - dependency: "com.example:legacy-codec:1.4.2"
    license: LGPL-3.0
    reason: "enlace dinámico, sin modificar"
    approved_by: "legal-reviewer"
    expires: "2027-03-31"
```
```text
# CI (esquema): generar informe -> comparar con la política -> fallar si denied/unknown
mvn -B verify          # incluye el plugin de informe de licencias
```

## Checklist de revisión
- [ ] Cada dependencia nueva tiene licencia identificada, también las transitivas.
- [ ] Ninguna licencia `denied` ni `unknown` en el informe.
- [ ] Las excepciones tienen aprobador y caducidad.
- [ ] No hay componentes de pago por defecto (D16).

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de dependencias nuevas | 3 | agente `code-reviewer` |
| Comparación informe de licencias vs. política en CI | 1 | pendiente (script del proyecto generado) |
| Aprobación de excepciones | 4 | revisión humana (legal) |

> Estado: sin artefacto automático en la fábrica todavía; el fichero de política es plantilla de guía.

## Relacionados, fuentes y mantenimiento
- Relacionados: `sbom-generation`, `dependency-hygiene`, `dependency-security`, `supply-chain`.
- Fuentes: lista SPDX de licencias (spdx.org/licenses) y textos oficiales de cada licencia; consultadas 2026-11-07.
- Normativa/legal: borrador por confirmar con fuente oficial y asesoría legal.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
