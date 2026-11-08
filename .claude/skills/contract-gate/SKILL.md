---
name: contract-gate
description: "Usar al integrar Pact en el pipeline: publicar contratos, verificar proveedor y bloquear el despliegue con can-i-deploy."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Contract gate (Pact can-i-deploy)

## Cuándo aplicar y cuándo no
- Aplica a servicios con consumidores o proveedores HTTP/mensajería internos que despliegan de forma independiente.
- No aplica a cómo escribir los contratos (ver `contract-testing-pact`) ni a APIs públicas sin consumidores conocidos (usar `openapi-contract-first` y compatibilidad).

## Reglas
- **MUST** publicar los pacts del consumidor en el Pact Broker en cada build, con la versión = SHA del commit y la rama.
- **MUST** que el proveedor verifique y publique resultados de verificación en CI.
- **MUST** ejecutar `pact-broker can-i-deploy` antes de cada promoción a un entorno; código de salida distinto de 0 aborta el despliegue.
- **MUST** ejecutar `pact-broker record-deployment` tras un despliegue correcto para que el Broker conozca qué versión está en cada entorno.
- **SHOULD** usar webhooks del Broker para disparar la verificación del proveedor cuando cambia un contrato.
- **MUST NOT** usar `--ignore` ni forzar el resultado para saltarse el gate sin PR de excepción.
- **MUST NOT** depender de un Broker de pago por defecto (D16/D19): Pact Broker OSS autoalojado.

## Por qué
Los tests de contrato solo previenen roturas si se consulta la matriz de compatibilidad con lo que está realmente desplegado. Sin `record-deployment`, `can-i-deploy` decide con datos obsoletos.

## Ejemplos
### Mal
```yaml
- run: pact-broker can-i-deploy --pacticipant orders --version $GITHUB_SHA --to-environment prod || true
```
### Bien
```yaml
- name: can-i-deploy
  run: >
    pact-broker can-i-deploy --pacticipant orders --version "$GITHUB_SHA"
    --to-environment staging --retry-while-unknown 12 --retry-interval 10
- name: deploy (ver rollback-strategy)
  run: ./deploy.sh staging "$IMAGE_DIGEST"
- run: >
    pact-broker record-deployment --pacticipant orders
    --version "$GITHUB_SHA" --environment staging
```
Sintaxis base verificada en https://docs.pact.io/pact_broker/can_i_deploy (2026-11-07); `--retry-*` comprobar al fijar la versión. Variables `PACT_BROKER_BASE_URL`/token vía secret del entorno, nunca en claro.

## Checklist de revisión
- [ ] Pacts publicados con versión = commit.
- [ ] can-i-deploy bloqueante antes de cada entorno.
- [ ] record-deployment tras cada despliegue correcto.
- [ ] Sin `|| true` ni `--ignore`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Rego: workflow de CD debe contener `can-i-deploy` sin `|| true` | 1 | pendiente |
| Branch/environment protection que exige el check | 4 | revisión humana |
| Revisión del uso del Broker | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `contract-testing-pact`, `pipeline-architecture`, `backward-compatibility-rules`, `environment-promotion`.
- Fuentes: https://docs.pact.io/pact_broker/can_i_deploy (2026-11-07); ADR-0019.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
