---
name: github-actions
description: "Usar al escribir o revisar workflows de GitHub Actions: reutilizables, OIDC a la nube, pinning por SHA, runners efímeros, cachés, matrices y environments."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# GitHub Actions (D20)

## Cuándo aplicar y cuándo no
- Aplica a cualquier `.github/workflows/*.yml` de un proyecto generado o de la fábrica.
- No aplica a GitLab CI/Jenkins (ver `alternatives`).
- Los SHA de los ejemplos son marcadores: **nunca** copiarlos; resolverlos con `git ls-remote` o la API al fijarlos (comprobar al fijar la versión).

## Reglas
- **MUST** fijar toda acción y workflow reutilizable de terceros por SHA de commit completo (40 hex), con el tag en comentario.
- **MUST** declarar `permissions:` de nivel superior mínimo (`contents: read`) y ampliar por job.
- **MUST** autenticarse en la nube con OIDC (`id-token: write` solo en el job que lo necesita); sin claves de acceso de larga vida en secrets.
- **MUST** restringir la confianza del lado de la nube a repo + entorno/rama (claim `sub`), no a toda la organización.
- **MUST** centralizar lógica repetida en workflows reutilizables (`on: workflow_call`) llamados con `uses:` fijado por SHA.
- **MUST** proteger despliegues con `environment:` (revisores requeridos, ramas permitidas) para dev/staging/prod.
- **MUST NOT** interpolar entradas no confiables (`github.event.pull_request.title`, nombres de rama) directamente en `run:`; pasarlas por `env:`.
- **MUST NOT** usar `pull_request_target` para ejecutar código de la PR con secretos.
- **SHOULD** usar runners efímeros (un job, una VM/contenedor) para builds sensibles; self-hosted solo efímeros y aislados.
- **SHOULD** cachear dependencias con clave que incluya el hash del lockfile, y usar `strategy.matrix` con `fail-fast` decidido a propósito.
- **SHOULD** definir `concurrency:` para cancelar ejecuciones obsoletas de PR y serializar despliegues.

## Por qué
Una acción por tag mutable puede cambiar tras un compromiso del repositorio de la acción. OIDC emite credenciales cortas por ejecución; la restricción del `sub` evita que otro repo asuma el rol. Límites documentados: hasta 10 niveles de anidamiento y 50 workflows reutilizables únicos por fichero (docs de GitHub, 2026-11-07).

## Ejemplos
### Mal
```yaml
on: pull_request_target
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "${{ github.event.pull_request.title }}"
        env:
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET }}
```
### Bien
```yaml
# .github/workflows/ci.yml (llama al reutilizable)
name: ci
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }
concurrency: { group: "ci-${{ github.ref }}", cancel-in-progress: true }
jobs:
  build:
    uses: acme/platform-workflows/.github/workflows/maven-build.yml@<SHA-40-HEX> # v1.x comprobar al fijar la versión
    with: { java-version: "21" }
```
```yaml
# reutilizable: maven-build.yml
on:
  workflow_call:
    inputs:
      java-version: { type: string, required: true }
permissions: { contents: read }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<SHA-40-HEX> # vX comprobar al fijar la versión
      - uses: actions/setup-java@<SHA-40-HEX> # vX comprobar al fijar la versión
        with: { distribution: temurin, java-version: "${{ inputs.java-version }}", cache: maven }
      - run: ./mvnw -B verify
  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: dev          # revisores/ramas se configuran en el repo
    permissions: { id-token: write, contents: read }
    steps:
      - uses: aws-actions/configure-aws-credentials@<SHA-40-HEX> # vX comprobar al fijar la versión
        with:
          role-to-assume: arn:aws:iam::111111111111:role/example-ci-dev
          aws-region: eu-west-1
```
El rol y la región son ejemplo; preparado para AWS, no verificado en real. En local no se reproduce OIDC contra AWS: se usa `act` o un runner kind sin credenciales cloud (comprobar al fijar la versión).

## Criterios de decisión y trampas
### Cómo decidir
- Fija las acciones de terceros por SHA completo; un tag es mutable y puede cambiar bajo tus pies.
- Permisos mínimos por defecto y ampliados por job; credenciales de nube por OIDC, sin claves guardadas.
- Flujos reutilizables para lo común; no copies el mismo YAML en cien repositorios.
### Trampas frecuentes
- `pull_request_target` que ejecuta código de forks con secretos.
- Interpolar entradas no confiables (títulos de PR, ramas) directamente en comandos de shell: inyección.
- Secretos accesibles a todos los jobs y no solo al que los necesita.
- Runners compartidos con estado entre ejecuciones.
- Cachés que se envenenan desde ramas no confiables.
### Evidencia
- Un análisis del workflow (por ejemplo, con las reglas de `policies/opa-conftest/github-actions-pinning.rego`) confirma que todo está fijado por SHA.

## Checklist de revisión
- [ ] Todo `uses:` externo termina en SHA de 40 hex.
- [ ] `permissions:` explícito y mínimo; `id-token: write` solo donde hay OIDC.
- [ ] Sin secrets de nube de larga vida; trust policy limitada a repo+entorno.
- [ ] Entradas no confiables vía `env:`.
- [ ] Despliegues con `environment:` y `concurrency:`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: SHA obligatorio y `permissions` | 1 | `policies/opa-conftest/github-actions-pinning.rego` (no ejecutada, comprobar al fijar la versión) |
| Workflow de la fábrica ya fijado por SHA | 1 | `.github/workflows/ci.yml` |
| Detección de inyección en `run:` (zizmor/Semgrep) | 1 | pendiente |
| Configuración de environments y trust OIDC | 4 | revisión humana (gate-5) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pipeline-architecture`, `supply-chain`, `cloud-iam-least-privilege`, `secrets-management`.
- Fuentes (2026-11-07): https://docs.github.com/en/actions/reference/workflows-and-actions/reusable-workflows ; https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect (nota: GitHub anuncia un formato de `sub` inmutable con IDs (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
