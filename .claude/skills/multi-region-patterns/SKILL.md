---
name: multi-region-patterns
description: "Usar al diseñar la región secundaria (eu-central-1) de un servicio: warm standby, clúster gemelo, Vault por región, ECR replicado y dependencias que no deben cruzar regiones."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Patrones multi-región

## Cuándo aplicar y cuándo no
- Aplica a tier 0-2: eu-west-1 primaria, eu-central-1 secundaria (D6). Defecto Tier 1: warm standby.
- No aplica a tier 3 (basta backup con copia cross-region).
- Diseño solamente (D4): "preparado para AWS, no verificado en real". En local **no se reproduce** multi-región; solo simulacro documental (tabletop).

## Reglas
- **MUST** desplegar un clúster EKS gemelo en la secundaria con Terraform y Argo CD (mismo repo GitOps, overlay por región), a escala reducida pero funcional (warm standby).
- **MUST** un **clúster Vault independiente por región** (Raft 3 AZ cada uno). El material de claves de Transit no se comparte entre ellos.
- **MUST** cifrar con claves multi-región de KMS (cifrado de sobre) los datos que deban leerse desde ambas regiones; **MUST NOT** usar Vault Transit para eso.
- **MUST** desplegar desde **ECR con replicación cross-region nativa**; el runtime no depende de Harbor ni del repositorio de artefactos para arrancar.
- **MUST** que CI/CD y el estado de Terraform sean accesibles aunque la región primaria caiga (estado/bucket y runners en la secundaria o fuera del dominio de fallo).
- **MUST** fijar la región de escritura por agregado en datos con Global Tables (ver `data-replication-matrix`).
- **MUST NOT** asumir replicación de Vault (función de pago): es variante opcional, no el diseño base (D16).
- **SHOULD** mantener cuotas de servicio en la secundaria suficientes para escalar a producción completa.
- **SHOULD** que Keycloak use la BD de Aurora Global; asumir reinicio de sesiones en failover.

## Por qué
Una región secundaria que depende de la primaria (registro, secretos, state, DNS de control) no sirve en el desastre que debía cubrir. Vault independiente evita acoplar dominios de fallo, pero obliga a distinguir qué se cifra con qué.

## Ejemplos
### Mal
```hcl
# Un solo Vault y una sola ruta de imágenes, ambos en la primaria
provider "aws" {
  region = "eu-west-1"
}

resource "helm_release" "vault" {
  name  = "vault"
  chart = "vault"
}
# la secundaria lee imágenes de harbor.example.internal (eu-west-1)
```
### Bien
```hcl
provider "aws" {
  alias  = "secondary"
  region = "eu-central-1"
}

module "vault_secondary" {
  source    = "./modules/vault-raft"   # Vault OSS, 3 nodos en 3 AZ
  providers = { aws = aws.secondary }
}

resource "aws_ecr_replication_configuration" "this" {
  replication_configuration {
    rule {
      destination {
        region      = "eu-central-1"
        registry_id = var.account_id
      }
    }
  }
}

resource "aws_kms_key" "shared_data" {
  multi_region = true   # datos legibles desde ambas regiones (envelope)
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Elige entre copia y restauración, espera caliente y activo-activo según los objetivos; cuanto más activo, más complejidad de datos.
- Separa claramente qué se replica y qué se reconstruye.
### Trampas frecuentes
- Activo-activo sin resolver los conflictos de escritura.
- Región secundaria sin ejercitar.
- Dependencias de una región (identidad, DNS, registros de imágenes).
- Replicar sin considerar el coste.
- Suponer que todos los servicios existen en ambas regiones.
### Evidencia
- Un ensayo de conmutación y de retorno con los tiempos medidos.

## Checklist de revisión
- [ ] Clúster gemelo definido por Terraform + Argo CD.
- [ ] Un Vault por región; datos compartidos con KMS multi-región.
- [ ] ECR replicado; el runtime no depende de Harbor.
- [ ] State de IaC y CI/CD operativos con la primaria caída.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: `aws_kms_key` compartida con `multi_region = true` | 1 | pendiente (`policies/opa-conftest/`) |
| Checkov custom: ECR con replicación | 1 | pendiente (`policies/iac-checks/`) |
| Revisión de arquitectura | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-replication-matrix`, `failover-and-failback-runbooks`, `eks-multi-region-and-argo-cd-multicluster`, `static-stability-and-cell-architecture`.
- Fuentes: AWS DR whitepaper (https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html, 2026-11-07); ECR replicación y KMS multi-región.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
