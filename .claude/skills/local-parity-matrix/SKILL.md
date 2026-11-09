---
name: local-parity-matrix
description: "Usar al documentar o revisar la equivalencia AWS-local de un proyecto y lo que el Kubernetes local no reproduce; fuente: catalog/parity-matrix.yaml."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Matriz de paridad AWS-local en el proyecto

## Cuándo aplicar y cuándo no
- Aplica al escribir el README de un proyecto generado, el diseño de un perfil local o cualquier texto que compare local con AWS.
- No aplica al mantenimiento de la matriz de la fábrica (ver `parity-matrix-maintenance`) ni a decisiones de coste.

## Reglas
- **MUST** que el proyecto incluya una tabla AWS / local / no reproducido derivada de `catalog/parity-matrix.yaml`, sin quitar filas que usen sus servicios.
- **MUST** usar estas equivalencias por defecto: EKS = kind (ADR-0034, k3d alternativa); Aurora PostgreSQL = CloudNativePG; DynamoDB = DynamoDB Local; MSK = Strimzi; S3 = MinIO; ElastiCache = Redis; ALB + Route 53 = Istio gateway (Gateway API); KMS / Secrets Manager = Vault en modo dev; IAM / IRSA = RBAC; CloudWatch = Prometheus, Grafana, Loki, Tempo.
- **MUST** declarar como no reproducido: WAF, Shield y CloudFront (todo); multi-región y DR (solo simulacro documental, ver `dr-tabletop-exercises`); nodos gestionados y autoscaling real de EKS; failover global de Aurora; replicación entre regiones de MSK y S3; claves multi-región; modelo de identidades AWS; DNS y balanceo gestionados.
- **MUST** recordar que Testcontainers sigue siendo necesario: el clúster local ejecuta el sistema completo, no sustituye los tests de integración.
- **SHOULD** enlazar cada fila a la prueba que sí cubre el comportamiento reproducible.
- **MUST NOT** presentar "funciona en local" como evidencia de comportamiento en AWS.

## Por qué
La matriz fija expectativas: qué se puede comprobar en el portátil y qué queda como riesgo declarado. Sin ella, un resultado verde en kind se lee como garantía de resiliencia que nunca se midió.

## Ejemplos
### Mal
```markdown
Probamos el failover de base de datos en local, así que la recuperación está cubierta.
```
### Bien
```markdown
| AWS | Local | No reproducido |
|---|---|---|
| Aurora PostgreSQL | CloudNativePG | Failover global, réplicas Aurora |
| WAF, Shield, CloudFront | (ninguno) | Todo |
| Multi-región y DR | (ninguno) | Solo simulacro documental (tabletop) |
```

## Checklist de revisión
- [ ] Hay tabla de paridad en el README y coincide con la matriz de la fábrica.
- [ ] Cada servicio AWS del diseño tiene fila, incluidos los sin equivalente local.
- [ ] Se menciona que Testcontainers no se sustituye.
- [ ] No hay frases que impliquen verificación en AWS real.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Esquema y consistencia del catálogo | 1 | `factory/validators/schemas_and_adrs.py` |
| Afirmaciones honestas | 1 | `factory/validators/honest_claims.py` |
| Comparación tabla del proyecto vs. matriz | 3 | revisión humana (script pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `aws-emulation`, `local-profiles`, `parity-matrix-maintenance`, `maturity-labels`.
- Fuentes: `catalog/parity-matrix.yaml`, `catalog/adr/0034-kubernetes-local-kind-vs-k3d.md`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
