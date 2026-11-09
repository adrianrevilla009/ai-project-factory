---
name: eks-networking
description: "Usar al diseñar la red de EKS: VPC CNI, agotamiento de IPs de pods, security groups, AWS Load Balancer Controller, endpoint del API y etiquetas de subredes."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Red de EKS

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a clústeres EKS en eu-west-1/eu-central-1 y a su integración con VPC, balanceadores y DNS.
- No aplica a la malla (Istio, bloque 13) ni a NetworkPolicy de aplicación. En local (kind) NO se reproducen el VPC CNI, las IP de pods como IP de VPC, security groups for pods ni el AWS Load Balancer Controller; el CNI local es otro.

## Reglas
- **MUST** dimensionar IPs de pods: con VPC CNI cada pod consume una IP de VPC; planificar CIDR secundario (p. ej. 100.64.0.0/10) con custom networking o prefix delegation.
- **MUST** desplegar nodos en subredes privadas de todas las AZ y balanceadores en subredes etiquetadas `kubernetes.io/role/elb` (públicas) y `kubernetes.io/role/internal-elb` (privadas).
- **MUST** configurar el endpoint del API con acceso privado; si hay acceso público, limitar `public_access_cidrs` y nunca 0.0.0.0/0.
- **MUST** exponer servicios con AWS Load Balancer Controller y `target-type: ip` (ver `alb-nlb-and-tls-termination`), con el rol IRSA/Pod Identity de mínimo privilegio.
- **MUST** aplicar NetworkPolicy por defecto-denegar entre namespaces, complementando (no sustituyendo) a los SG.
- **SHOULD** usar security groups for pods solo para cargas que necesiten acceso a datos con SG propios; tiene límites por tipo de instancia.
- **SHOULD** vigilar IP libres por subred y ENI por nodo con alertas.
- **SHOULD** mantener CoreDNS dimensionado y NodeLocal DNSCache si el volumen de DNS lo justifica.

## Por qué
EKS agota subredes antes que CPU: un /24 admite pocos pods. El endpoint público abierto y las etiquetas de subred ausentes son las dos causas más comunes de clústeres expuestos o balanceadores que no se crean. Los SG y las NetworkPolicy actúan en capas distintas; se necesitan ambos.

## Ejemplos
### Mal
```hcl
resource "aws_eks_cluster" "main" {
  name     = "platform"
  role_arn = aws_iam_role.cluster.arn
  vpc_config {
    subnet_ids              = [for s in aws_subnet.public : s.id]
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }
}
```
### Bien
```hcl
resource "aws_eks_cluster" "main" {
  name     = "platform-euw1"
  role_arn = aws_iam_role.cluster.arn
  vpc_config {
    subnet_ids              = [for s in aws_subnet.private : s.id]
    endpoint_private_access = true
    endpoint_public_access  = false
  }
}

resource "aws_subnet" "private" {
  for_each          = local.azs
  vpc_id            = aws_vpc.main.id
  availability_zone = each.value
  cidr_block        = local.private_cidrs[each.key]
  tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}
```
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: orders
spec:
  podSelector: {}
  policyTypes: ["Ingress"]
```

## Checklist de revisión
- [ ] Plan de IPs de pods (CIDR secundario/prefix delegation) y alertas de IP libres.
- [ ] Subredes etiquetadas para balanceadores; nodos en privadas.
- [ ] Endpoint del API privado o con CIDR restringido.
- [ ] NetworkPolicy por defecto-denegar; Load Balancer Controller con permisos mínimos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_38` (endpoint público no abierto a 0.0.0.0/0) y `CKV_AWS_100` (sin SSH abierto en node group) | 1 | herramienta Checkov (IDs comprobados en la lista local) |
| Kyverno: exigir NetworkPolicy por namespace | 1 | pendiente: `policies/kyverno/` |
| Revisión del plan de IPs | 4 | revisión humana en PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cidr-planning-and-ipam`, `alb-nlb-and-tls-termination`, `container-and-k8s-security`, `cluster-topology`, `mtls-strict-and-peer-auth`.
- Fuentes: guía oficial de buenas prácticas de redes de Amazon EKS y documentación del VPC CNI.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
