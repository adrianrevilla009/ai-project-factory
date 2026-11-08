---
name: gateway-api
description: "Usar al exponer servicios HTTP con Kubernetes Gateway API (Gateway, HTTPRoute) y decidir su relación con los recursos Istio."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Gateway API

## Cuándo aplicar y cuándo no
- Aplica a toda entrada nueva de tráfico norte-sur y a reglas de enrutado HTTP entre servicios.
- No aplica a clústeres que aún no tengan los CRDs de Gateway API instalados: instalarlos es un paso previo explícito (TODO-VERIFY canal estándar y versión).

## Reglas
- **MUST** preferir `Gateway` + `HTTPRoute` (API estándar) sobre `Ingress` en proyectos nuevos; Istio la implementa con `gatewayClassName: istio`.
- **MUST** separar roles: el equipo de plataforma posee `Gateway`; los equipos de servicio poseen sus `HTTPRoute`.
- **MUST** restringir qué namespaces pueden adjuntar rutas con `allowedRoutes`.
- **MUST** terminar TLS en el `Gateway` con un `Secret` gestionado por cert-manager; nunca certificados en el repo.
- **SHOULD** usar `VirtualService`/`DestinationRule` de Istio solo para lo que Gateway API no cubra todavía (TODO-VERIFY cobertura vigente).
- **MUST NOT** mezclar `Ingress` y `Gateway` para el mismo host.

## Por qué
Gateway API es estándar de Kubernetes, portable entre implementaciones y con modelo de roles explícito; evita anotaciones propietarias. Mantener una sola vía por host evita reglas contradictorias.

## Ejemplos
### Mal
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /   # anotación propietaria
```
### Bien
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: public, namespace: istio-ingress }
spec:
  gatewayClassName: istio
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      hostname: api.example.com
      tls:
        mode: Terminate
        certificateRefs: [{ name: api-example-tls }]
      allowedRoutes:
        namespaces:
          from: Selector
          selector: { matchLabels: { gateway-access: "true" } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: orders, namespace: orders }
spec:
  parentRefs: [{ name: public, namespace: istio-ingress }]
  hostnames: [api.example.com]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /orders } }]
      backendRefs: [{ name: orders, port: 8080 }]
```

## Checklist de revisión
- [ ] `Gateway` en namespace de plataforma, `allowedRoutes` restringido.
- [ ] TLS con certificado de cert-manager.
- [ ] Sin `Ingress` duplicando el host.
- [ ] Versión de CRDs documentada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: `Gateway` sin `allowedRoutes` o `Ingress` nuevo (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión de rutas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `ingress-and-egress-gateways`, `traffic-management`, `canary-and-traffic-splitting`, `bff-and-api-gateway`.
- Fuentes: gateway-api.sigs.k8s.io y istio.io/latest/docs/tasks/traffic-management/ingress/gateway-api/ (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
