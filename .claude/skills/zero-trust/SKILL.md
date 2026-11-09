---
name: zero-trust
description: "Usar al diseñar la arquitectura de red e identidad de servicios: no confiar en la red interna, identidad por carga de trabajo, mTLS con Istio y mínimo privilegio."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Zero trust en arquitectura de servicios

## Cuándo aplicar y cuándo no
- Aplica al diseñar comunicación entre servicios, acceso a datos y acceso de operadores.
- No aplica como producto: es un principio ("nunca confiar, siempre verificar"); no se compra ni se declara "implantado".

## Reglas
- **MUST** autenticar y autorizar cada petición, también entre servicios internos; estar dentro de la red no concede permisos.
- **MUST** identidad por carga de trabajo (cuenta de servicio de Kubernetes, identidad SPIFFE de Istio), no por IP ni por secreto compartido.
- **MUST** mTLS entre servicios en la malla (Istio, decisión cerrada) en modo `STRICT` en namespaces de aplicación.
- **MUST** NetworkPolicy/AuthorizationPolicy con denegar por defecto y reglas explícitas origen -> destino.
- **MUST** propagar la identidad del usuario final (token) y validarla en cada servicio; **MUST NOT** confiar en una cabecera `X-User-Id` interna sin firma.
- **MUST** mínimo privilegio en acceso a datos: credenciales por servicio, solo las tablas/colas necesarias (`cloud-iam-least-privilege`).
- **SHOULD** segmentar por sensibilidad (datos personales en segmentos aparte) y registrar accesos (`audit-trail-and-security-logging`).
- **SHOULD** acceso de operadores con identidad individual, MFA y caducidad, sin credenciales compartidas.

## Por qué
El perímetro falla: un pod comprometido o un secreto filtrado da movimiento lateral si la red interna es de confianza. Verificar en cada salto limita el radio de impacto. En local (kind/minikube) la malla puede reproducirse parcialmente; la integración con IAM de AWS no se reproduce en local: preparado para AWS, no verificado en real.

## Ejemplos
### Mal
```yaml
# Cualquier pod del cluster puede llamar a payments
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: payments }
spec:
  mtls: { mode: PERMISSIVE }
```
### Bien
```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: payments }
spec:
  mtls: { mode: STRICT }
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: payments-allow-orders, namespace: payments }
spec:
  selector: { matchLabels: { app: payments } }
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/orders/sa/orders-service"]
      to:
        - operation: { methods: ["POST"], paths: ["/payments"] }
```
Versión de API de Istio y campos.

## Checklist de revisión
- [ ] mTLS `STRICT` en namespaces de aplicación.
- [ ] AuthorizationPolicy/NetworkPolicy con denegar por defecto.
- [ ] Cada servicio valida el token del usuario, no una cabecera interna.
- [ ] Credenciales de datos por servicio y mínimas.
- [ ] Acceso de operadores individual y auditado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno/Conftest: `PeerAuthentication` no `PERMISSIVE` | 1 | pendiente (`policies/kyverno/`, `policies/opa-conftest/`) |
| Exigir NetworkPolicy por namespace | 1 | pendiente (`policies/kyverno/`) |
| Revisión de arquitectura en gate de diseño | 3 | `gates/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `authn-oidc-oauth2`, `container-and-k8s-security`, `cloud-iam-least-privilege`, `crypto-tls-mtls-key-rotation`, `threat-modeling-stride`.
- Fuentes: NIST SP 800-207 (Zero Trust Architecture); documentación de Istio (PeerAuthentication, AuthorizationPolicy).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
