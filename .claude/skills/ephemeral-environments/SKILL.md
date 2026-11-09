---
name: ephemeral-environments
description: "Usar al diseñar entornos efímeros por pull request (namespace temporal, datos sintéticos, destrucción automática) en Kubernetes."
metadata:
  block: "20-internal-developer-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Entornos efímeros por PR

## Cuándo aplicar y cuándo no
- Aplica cuando se quiere validar un cambio de extremo a extremo antes del merge, sin colas para un entorno de staging compartido.
- No aplica a servicios con dependencias que no se pueden replicar (hardware, licencias de pago por instancia); ahí usar dobles de contrato (`contract-testing-pact`).
- La fábrica no despliega (ADR-0004): esto describe el diseño para el proyecto generado, validado estáticamente.

## Reglas
- **MUST** un namespace por PR con nombre derivado (`pr-<número>`), etiquetas `owner` y `ttl`, y `ResourceQuota` + `LimitRange` + `NetworkPolicy` por defecto deny.
- **MUST** destrucción automática al cerrar el PR y por TTL máximo (p. ej. 48 h) como red de seguridad.
- **MUST** datos sintéticos o anonimizados; MUST NOT copiar datos de producción (`pii-and-data-classification`).
- **MUST** secretos propios del entorno, de menor privilegio y de corta vida; nunca reutilizar los de staging/prod.
- **SHOULD** desplegar por GitOps (ApplicationSet con generador de PR en Argo CD) en vez de scripts imperativos.
- **SHOULD** limitar el nº de entornos simultáneos y escalar a cero fuera de horario.
- **SHOULD** comentar en el PR la URL y el estado del entorno.
- **MUST NOT** exponer el entorno a Internet sin autenticación.

## Por qué
Los entornos compartidos son cuellos de botella y fuente de "funciona en staging". Los efímeros dan feedback aislado, pero sin TTL ni cuotas acaban siendo un coste silencioso (`finops`) y una superficie de ataque olvidada.

## Ejemplos
### Mal
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: feature-test      # sin dueño, sin TTL, sin cuota
```
### Bien
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pr-482
  labels:
    owner: team-orders
    ttl-hours: "48"
    environment: ephemeral
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: pr-quota, namespace: pr-482 }
spec:
  hard: { requests.cpu: "2", requests.memory: 4Gi, pods: "20" }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: pr-482 }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## Criterios de decisión y trampas
### Cómo decidir
- Entornos efímeros por cambio cuando permiten revisar y probar de verdad; con límites de coste, tiempo de vida y datos sintéticos.
- Los mismos manifiestos que producción.
### Trampas frecuentes
- Entornos que viven semanas.
- Datos reales en entornos efímeros.
- Recursos compartidos que un entorno puede romper.
- Sin límite de coste.
- Dependencias que no se pueden replicar.
### Evidencia
- Un recuento de entornos activos, coste y edad.

## Checklist de revisión
- [ ] Namespace con labels owner/ttl, quota, limitrange y default-deny.
- [ ] Limpieza al cerrar PR y por TTL.
- [ ] Datos sintéticos; secretos propios.
- [ ] Acceso autenticado.
- [ ] Coste acotado (máximo de entornos).

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno: namespaces `pr-*` exigen labels owner/ttl y quota | 1 | pendiente (`policies/kyverno/`) |
| Policy GitOps sin secretos en claro | 1 | `policies/opa-conftest/gitops-no-plain-secrets.rego` |
| Revisión del diseño de datos de prueba | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `promotion-between-environments`, `test-data-management`, `finops`, `container-and-k8s-security`.
- Fuentes: Argo CD ApplicationSet, generador Pull Request.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
