---
name: application-recovery-controller-and-health-checks
description: "Usar al diseñar la conmutación de tráfico entre regiones o AZ: routing controls y zonal shift de ARC, health checks de Route 53 y qué evitar en el plano de control."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Application Recovery Controller y health checks

## Cuándo aplicar y cuándo no
- Aplica a la capa de entrada (Route 53, CloudFront, Global Accelerator) de servicios tier 0-2.
- No aplica a tier 3. ARC añade coste: ver `finops-of-resilience`.
- Diseño: preparado para AWS, no verificado en real. Local: el gateway Istio no reproduce DNS ni balanceo gestionado.

## Reglas
- **MUST** conmutar tráfico con acciones de plano de datos. Para failover manual usar interruptores de ARC (routing controls, que gobiernan health checks de Route 53 sin comprobar salud), no cambiar pesos por la API de control.
- **MUST** guardar los endpoints del clúster ARC y credenciales de operación en el runbook, probadas fuera de la región afectada.
- **MUST** health checks "profundos" (dependencias críticas) para decidir salud, y "superficiales" para liveness; **MUST NOT** hacer que un health check público consulte la BD en cada llamada sin caché.
- **SHOULD** usar zonal shift/autoshift para sacar una AZ degradada, solo si hay capacidad N+1 (ver `multi-az-patterns`).
- **SHOULD** usar readiness checks para comparar capacidad y configuración entre regiones.
- **MUST** conmutación manual con aprobación para el failover regional; la automática por alarma solo con umbrales conservadores, por falsos positivos.
- **MUST NOT** depender de Auto Scaling u operaciones de plano de control en la ruta crítica de conmutación sin capacidad previa (ver `static-stability-and-cell-architecture`).
- **SHOULD** TTL de DNS bajo en los registros de conmutación, documentado y medido.

## Por qué
Los planos de datos tienen objetivos de disponibilidad mayores que los de control; si el failover exige crear o editar recursos, puede fallar justo cuando hace falta. El whitepaper de DR recomienda interruptores de ARC para failover manual por Route 53 y advierte del uso cuidadoso de la conmutación automática.

## Ejemplos
### Mal
```hcl
# Failover cambiando pesos a mano (operación de plano de control)
resource "aws_route53_record" "api_primary" {
  weighted_routing_policy { weight = 100 }
}
```
### Bien
```hcl
resource "aws_route53_health_check" "primary_switch" {
  type                = "RECOVERY_CONTROL"
  routing_control_arn = var.primary_routing_control_arn   # interruptor ARC
}

resource "aws_route53_record" "api_primary" {
  failover_routing_policy { type = "PRIMARY" }
  set_identifier  = "primary"
  health_check_id = aws_route53_health_check.primary_switch.id
}
```
Argumentos del recurso `aws_route53_health_check` con `RECOVERY_CONTROL`: TODO-VERIFY contra el proveedor Terraform.

## Checklist de revisión
- [ ] Conmutación regional por routing control, no por edición de DNS.
- [ ] Health checks profundos y superficiales separados.
- [ ] Endpoints ARC y credenciales de operación probados offline.
- [ ] Capacidad N+1 antes de usar zonal shift.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov custom: registros de failover con health check | 1 | pendiente (`policies/iac-checks/`) |
| Revisión de arquitectura | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `failover-and-failback-runbooks`, `multi-az-patterns`, `static-stability-and-cell-architecture`.
- Fuentes: https://docs.aws.amazon.com/r53recovery/latest/dg/what-is-route-53-recovery.html y whitepaper DR (https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html), 2026-11-07. Regiones de los endpoints del clúster ARC: TODO-VERIFY.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
