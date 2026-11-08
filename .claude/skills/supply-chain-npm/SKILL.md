---
name: supply-chain-npm
description: "Usar al añadir, actualizar o auditar dependencias npm/pnpm del frontend: lockfile, scripts de instalación, typosquatting, auditoría y SBOM."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Cadena de suministro npm

## Cuándo aplicar y cuándo no
- Aplica a `package.json`, `pnpm-lock.yaml`, `.npmrc`, pipelines de CI del frontend y a cada dependencia nueva.
- No aplica a Maven (`dependency-security`, `bom-management`). La política general está en `supply-chain`, `sbom` y `license-policy`; aquí solo lo específico de npm.

## Reglas
- **MUST** versionar el lockfile y usar instalación reproducible en CI (`pnpm install --frozen-lockfile`; con npm, `npm ci`).
- **MUST** desactivar la ejecución de scripts de ciclo de vida de dependencias por defecto y permitir solo una lista explícita (pnpm: `onlyBuiltDependencies`; comprobar comportamiento por defecto en la versión usada).
- **MUST** instalar desde el registro privado/proxy de la organización con scope propio reservado, para evitar confusión de dependencias (`remote-repos-and-dependency-confusion-protection`, `private-registry`).
- **MUST** revisar cada dependencia nueva: mantenimiento, licencia, tamaño, dependencias transitivas, nombre exacto (typosquatting) y si hay alternativa nativa.
- **MUST** ejecutar auditoría (`pnpm audit`) y SCA en CI con SLA de corrección (`vulnerability-sla-and-incident-response`); **MUST** generar SBOM CycloneDX del build (`sbom-generation`).
- **MUST NOT** usar rangos abiertos (`*`, `latest`) ni dependencias desde URL/git sin commit fijo; **MUST NOT** hacer `curl | sh` en el build.
- **SHOULD** aplicar un periodo de espera para versiones recién publicadas (pnpm `minimumReleaseAge`; comprobar disponibilidad) y actualizar con Renovate/Dependabot según `renovate-dependabot-policy`.
- **SHOULD** verificar firmas/procedencia cuando el registro las ofrezca (`npm audit signatures`; comprobar alcance con pnpm).
- **SHOULD** separar `dependencies` de `devDependencies` y mantener el árbol pequeño.

## Por qué
Los paquetes npm ejecutan código en instalación y con frecuencia son objetivo de secuestro de cuentas, typosquatting y confusión de dependencias. Un lockfile reproducible más scripts bloqueados reduce el radio de impacto de un paquete comprometido.

## Ejemplos
### Mal
```json
{ "dependencies": { "left-padder": "*", "internal-utils": "latest", "tool": "github:someone/tool" } }
```
### Bien
```ini
#.npmrc (ejemplo; comprobar claves)
registry=https://npm.example.internal/
@acme:registry=https://npm.example.internal/
```
```json
{
  "packageManager": "pnpm@x.y.z",
  "pnpm": { "onlyBuiltDependencies": ["esbuild"] },
  "dependencies": { "react": "19.0.0" }
}
```
```text
pnpm install --frozen-lockfile && pnpm audit --prod
```
(`x.y.z` y versiones: placeholders; fijar las reales del proyecto.)

## Checklist de revisión
- [ ] Lockfile versionado e instalación congelada en CI.
- [ ] Scripts de instalación bloqueados salvo lista explícita.
- [ ] Registro/scope interno configurado.
- [ ] Dependencia nueva justificada (licencia, mantenimiento, tamaño, nombre).
- [ ] Auditoría y SBOM en el pipeline.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Auditoría + SCA + SBOM en CI | 2 | pipeline del proyecto generado (pendiente); ver `sbom-generation` |
| Renovate/Dependabot con espera y agrupación | 2 | `renovate-dependabot-policy` |
| Revisión de dependencia nueva | 3 | agente `code-reviewer` |
| Regla específica en la fábrica | - | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `supply-chain`, `security-frontend`, `sbom`, `license-policy`, `dependency-hygiene`, `private-registry`.
- Fuentes: documentación de pnpm (settings) y npm (audit) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
