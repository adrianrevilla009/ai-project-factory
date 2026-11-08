---
name: cluster-addons-baseline
description: "Usar al definir el conjunto mínimo de addons de un clúster Kubernetes: cert-manager, external-dns, external-secrets, metrics-server, CNI/CSI, y su ciclo de vida."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Baseline de addons del clúster

## Cuándo aplicar y cuándo no
- Aplica al crear un clúster nuevo y al revisar qué componentes de plataforma lleva.
- No aplica a las aplicaciones del negocio ni a la configuración del mesh (ver `istio-upgrades-and-ops`).

## Reglas
- **MUST** mantener una lista explícita de addons con versión fijada, dueño y namespace: CNI, CSI, CoreDNS, metrics-server, cert-manager, external-dns, external-secrets, ingress/gateway (ver `gateway-api`).
- **MUST** instalar los addons por GitOps/IaC, nunca con `kubectl apply` manual; **MUST NOT** usar manifiestos remotos con `latest`.
- **MUST** ejecutar los addons en el pool de sistema con requests, PDB y réplicas >= 2 (ver `workload-baseline`).
- **MUST** dar a cada addon que llama a la nube una identidad propia de mínimo privilegio (ver `rbac-and-service-accounts`); external-dns solo sobre las zonas que gestiona.
- **MUST NOT** guardar secretos en Git: external-secrets lee de Vault OSS (o gestor de la nube) y crea el Secret; ver `injection-patterns`.
- **SHOULD** usar cert-manager con un issuer interno (CA propia/Vault PKI) y certificados con renovación automática; alertar antes de caducar.
- **SHOULD** versionar CRDs de addons y actualizarlos antes que sus controladores (ver `cluster-upgrades-and-drift`).
- **MUST** declarar qué NO se reproduce en local: sin Route 53, sin ACM/KMS; usar CoreDNS/dnsmasq, CA self-signed y Vault dev.

## Por qué
Los addons son la base de la que dependen todas las apps: un cert-manager desactualizado o un DNS roto afecta a todos los equipos a la vez. Lista y versiones explícitas hacen predecible el clúster.

## Ejemplos
### Mal
```text
kubectl apply -f https://example.com/cert-manager/latest/install.yaml
```
### Bien
```yaml
# platform/addons.yaml (extracto, versiones a verificar)
addons:
  - name: cert-manager
    chart: cert-manager
    version: "TODO-VERIFY"
    namespace: cert-manager
  - name: external-secrets
    chart: external-secrets
    version: "TODO-VERIFY"
    namespace: external-secrets
  - name: external-dns
    chart: external-dns
    version: "TODO-VERIFY"
    namespace: external-dns
    scope: "zonas gestionadas solo del entorno"
```

## Checklist de revisión
- [ ] Lista de addons con versión, dueño y namespace.
- [ ] Instalados por GitOps/IaC.
- [ ] Identidad de nube de mínimo privilegio por addon.
- [ ] Sin secretos en Git.
- [ ] Limitaciones locales declaradas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión del inventario de addons | 3 | agente revisor de manifiestos |
| Escaneo de secretos en el repo | 1 | `secret-scanning-and-leak-response` |

Policy de versiones fijadas: pendiente.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `helm-standards`, `cluster-upgrades-and-drift`, `injection-patterns`, `pki-and-cert-issuance`, `dns-route53-private-and-hybrid`.
- Fuentes: documentación de cert-manager, external-dns y External Secrets Operator (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
