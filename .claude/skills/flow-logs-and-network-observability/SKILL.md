---
name: flow-logs-and-network-observability
description: "Usar al activar o revisar VPC Flow Logs, logs de DNS/ALB/WAF y diagnóstico de red en AWS: destino, formato, retención, coste y alertas."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Flow logs y observabilidad de red

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a toda VPC, TGW y balanceador/WAF/Resolver con logging disponible.
- No aplica a métricas de aplicación (bloque de observabilidad). En local no se reproducen flow logs; solo se puede observar tráfico con herramientas del clúster (p. ej. Hubble/Kiali según el CNI/malla), sin equivalencia.

## Reglas
- **MUST** activar `aws_flow_log` en cada VPC (idealmente a nivel de VPC, no de ENI) con `traffic_type = "ALL"` en producción.
- **MUST** enviar los logs a un bucket S3 del archivo de logs (cuenta separada, ver `log-archive-and-audit-account`), cifrado con KMS y con ciclo de vida de retención definido.
- **MUST** usar formato personalizado con campos útiles (`vpc-id`, `subnet-id`, `srcaddr`, `dstaddr`, `pkt-srcaddr`, `pkt-dstaddr`, `action`, `flow-direction`, `tcp-flags`); `pkt-*` es necesario para ver el origen real tras NAT o balanceador.
- **MUST** activar también logs de ALB/NLB, WAF, consultas del Resolver y del TGW cuando existan.
- **MUST NOT** dejar logs de red en una cuenta de carga con permisos de borrado para el equipo de aplicación.
- **SHOULD** usar intervalo de agregación de 60 s en VPC críticas y 600 s en el resto para controlar coste.
- **SHOULD** consultar con Athena (tabla particionada) y definir alertas: rechazos masivos, tráfico a puertos de administración, destinos inesperados, picos de egress.
- **SHOULD** usar Reachability Analyzer para validar rutas antes de culpar a la aplicación.

## Por qué
Sin flow logs, un incidente de exfiltración o un fallo de SG se investiga a ciegas. Los datos de red contienen metadatos sensibles (IP de usuarios): su destino, acceso y retención son una decisión de privacidad (borrador por confirmar con fuente oficial/DPO). El coste crece con el volumen; el formato y el intervalo lo controlan.

## Ejemplos
### Mal
```hcl
resource "aws_flow_log" "main" {
  vpc_id          = aws_vpc.main.id
  traffic_type    = "REJECT"                       # sin visibilidad de lo aceptado
  log_destination = aws_cloudwatch_log_group.app.arn # en la cuenta de la app, retención infinita
}
```
### Bien
```hcl
resource "aws_flow_log" "main" {
  vpc_id                   = aws_vpc.main.id
  traffic_type             = "ALL"
  log_destination_type     = "s3"
  log_destination          = "arn:aws:s3:::example-org-log-archive-euw1/flow/"
  max_aggregation_interval = 60
  log_format = join(" ", [
    "$${version}", "$${vpc-id}", "$${subnet-id}", "$${srcaddr}", "$${dstaddr}",
    "$${pkt-srcaddr}", "$${pkt-dstaddr}", "$${srcport}", "$${dstport}",
    "$${protocol}", "$${action}", "$${flow-direction}", "$${tcp-flags}",
  ])
}
```

## Checklist de revisión
- [ ] Flow logs `ALL` en cada VPC, hacia S3 del archivo de logs con KMS y retención.
- [ ] Formato con campos `pkt-*` y de dirección.
- [ ] Logs de ALB, WAF, Resolver y TGW activos donde existan.
- [ ] Alertas definidas; acceso a los logs restringido y auditado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV2_AWS_11` (flow logs en todas las VPC), `CKV_AWS_91` (access logs de ALB), `CKV_AWS_176` (logging WAF) | 1 | herramienta Checkov (IDs comprobados en la lista local) |
| Regla custom: destino en cuenta de archivo, no en la cuenta de carga | 1 | pendiente: `policies/iac-checks/` |
| Retención y base legal de logs con IP | 4 | revisión humana (borrador por confirmar) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `log-archive-and-audit-account`, `transit-gateway-hub-and-spoke`, `waf-shield-and-cloudfront`, `audit-trail-and-security-logging`, `pii-and-data-classification`.
- Fuentes: documentación oficial de VPC Flow Logs (campos y formato personalizado) y Reachability Analyzer (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
