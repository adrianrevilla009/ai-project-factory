---
name: pipeline-architecture
description: "Usar al diseñar el pipeline CI/CD de un proyecto generado: etapas, orden de gates, separación CI/CD y artefactos inmutables."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Arquitectura del pipeline CI/CD

## Cuándo aplicar y cuándo no
- Aplica al diseñar o revisar el pipeline de un proyecto generado (GitHub Actions, D20).
- No aplica a la sintaxis concreta de workflows (ver `github-actions`) ni al despliegue declarativo (bloque 17, GitOps).
- La fábrica no despliega nunca (ADR-0004): el pipeline se entrega como guía y se valida estáticamente.

## Reglas
- **MUST** separar CI (construir, probar, publicar artefacto) de CD (promover). CD no reconstruye: promueve el mismo digest.
- **MUST** construir el artefacto una sola vez y promoverlo por digest inmutable (`sha256:`), nunca por tag mutable como `latest`.
- **MUST** ordenar etapas de lo barato a lo caro: lint/unit, build, seguridad estática, integración/contrato, imagen y escaneo, preview, rendimiento, promoción.
- **MUST** hacer que cada gate sea bloqueante y devuelva código de salida distinto de cero; ningún gate "informativo" en la rama principal sin excepción registrada.
- **MUST** que el pipeline sea la única vía a entornos compartidos; sin despliegues manuales desde portátiles.
- **SHOULD** paralelizar jobs independientes y usar `needs:` solo para dependencias reales.
- **SHOULD** que el pipeline sea reproducible en local (`make verify` o equivalente) para depurar sin hacer push.
- **MUST NOT** mezclar en un mismo job build y despliegue ni compartir credenciales de despliegue con jobs de PR de forks.

## Por qué
Un artefacto reconstruido por entorno ya no es el que se probó. Un orden barato-primero da feedback rápido y reduce coste de runners. La separación CI/CD permite que la promoción sea auditable y reversible (`rollback-strategy`).

## Ejemplos
### Mal
```text
build-dev -> deploy-dev
build-pre (otra compilación) -> deploy-pre
build-prod (otra compilación) -> deploy-prod
```
### Bien
```text
PR:    lint+unit -> sast/sca -> integration+contract -> image+scan -> preview
main:  (lo anterior) -> publish image@sha256 + SBOM + firma -> perf gate
CD:    promote same digest: dev -> staging -> prod (aprobación por entorno)
       cada paso: migración -> deploy -> smoke -> verificación -> (rollback)
```

## Criterios de decisión y trampas
### Cómo decidir
- Construye una vez y promociona el mismo artefacto por su digest; si reconstruyes por entorno, lo que probaste no es lo que despliegas.
- Ordena las etapas de lo barato a lo caro para fallar rápido; paraleliza las que no dependen entre sí.
- Monorepo o repos múltiples: en monorepo, ejecuta solo lo afectado por el cambio y mantén el pipeline completo en la rama principal.
### Trampas frecuentes
- Pipelines de 40 minutos que se saltan «solo esta vez».
- Un gate informativo que nunca bloquea: nadie lo mira.
- Lógica de negocio del despliegue en scripts del CI que no se pueden ejecutar en local.
- Etapas que dependen de estado dejado por ejecuciones anteriores.
- Un único pipeline gigante que nadie se atreve a tocar.
### Evidencia
- El mismo digest pasa por todos los entornos y cada gate se puede ejecutar en local con un comando.

## Checklist de revisión
- [ ] Un solo build por versión; promoción por digest.
- [ ] Etapas ordenadas barato -> caro y todos los gates bloqueantes.
- [ ] CI y CD en workflows separados con permisos distintos.
- [ ] No hay despliegue fuera del pipeline.
- [ ] Hay camino de rollback documentado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Política Conftest sobre workflows (permisos, pinning) | 1 | `policies/opa-conftest/github-actions-pinning.rego` (escrita, no ejecutada) |
| Regla Rego "imagen por digest, no por tag" | 1 | pendiente |
| Revisión de arquitectura del pipeline | 3 | agente `code-reviewer` / gate-3 (`gates/gate-3-pull-request.md`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `github-actions`, `quality-gates`, `security-gates`, `rollback-strategy`, `supply-chain`, `release-versioning-changelog`.
- Fuentes: ADR-0020 (`catalog/adr/0020-ci-con-github-actions.md`); documentación de GitHub Actions https://docs.github.com/en/actions (consultada 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
