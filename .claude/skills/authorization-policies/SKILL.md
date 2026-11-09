---
name: authorization-policies
description: "Usar al escribir AuthorizationPolicy de Istio: deny-all por defecto, allow por identidad de servicio y reglas L7 mínimas."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# AuthorizationPolicy en Istio

## Cuándo aplicar y cuándo no
- Aplica a cada namespace con cargas en la malla.
- No sustituye la autorización de negocio (roles/permisos de usuario) en la aplicación; la malla controla qué servicio puede llamar a cuál.

## Reglas
- **MUST** partir de deny-all por namespace (`AuthorizationPolicy` sin `rules`) y añadir `ALLOW` explícitos.
- **MUST** identificar al llamante por `source.principals` (identidad SPIFFE, requiere mTLS STRICT), no por IP ni namespace solamente.
- **MUST NOT** usar `principals: ["*"]` ni `allow` sin `from`.
- **SHOULD** limitar por `operation` (`methods`, `paths`) en endpoints sensibles.
- **SHOULD** usar `DENY` para excepciones claras (p. ej. `/actuator/*` desde fuera) y `AUDIT`/`CUSTOM` solo si hay backend definido.
- **MUST** probar cada política (llamada permitida y llamada denegada esperada → 403).
- **MUST NOT** validar JWT solo en la malla ignorando la validación en el servicio (defensa en profundidad).

## Por qué
Sin deny-all, cualquier pod comprometido llama a todos. Con identidades SPIFFE, la regla sobrevive a cambios de IP y reescalados.

## Ejemplos
### Mal
```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: allow-all, namespace: orders }
spec:
  rules:
    - {}          # permite todo
```
### Bien
```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: deny-all, namespace: orders }
spec: {}
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: orders-from-bff, namespace: orders }
spec:
  selector: { matchLabels: { app.kubernetes.io/name: orders } }
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/bff/sa/bff"]
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/orders/*"]
```
`security.istio.io/v1` es la versión servida y almacenada del CRD (verificado el 2026-11-08); la semántica de `spec: {}` se contrasta con la documentación de la versión elegida.

## Checklist de revisión
- [ ] Deny-all en cada namespace de negocio.
- [ ] Cada ALLOW con `principals` concretos.
- [ ] Rutas/métodos acotados donde aplica.
- [ ] Test de acceso permitido y denegado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: deniega principals `*` | 1 | `policies/opa-conftest/istio-mesh-security.rego` |
| Conftest: namespace sin deny-all (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión de políticas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `mtls-strict-and-peer-auth`, `zero-trust`, `authz-rbac-abac-rebac`, `rbac-and-service-accounts`.
- Fuentes: istio.io/latest/docs/reference/config/security/authorization-policy/.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
