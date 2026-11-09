---
name: mtls-strict-and-peer-auth
description: "Usar al activar o auditar mTLS en la malla Istio: PeerAuthentication STRICT, migración desde PERMISSIVE y excepciones por puerto."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# mTLS estricto y PeerAuthentication

## Cuándo aplicar y cuándo no
- Aplica a todo tráfico este-oeste entre cargas dentro de la malla.
- No aplica al tráfico externo hacia el gateway (ahí TLS lo termina el `Gateway`) ni a cargas fuera de la malla, que necesitan excepción explícita.

## Reglas
- **MUST** definir un `PeerAuthentication` de malla en el namespace raíz (`istio-system`) con `mtls.mode: STRICT`.
- **MUST** usar `PERMISSIVE` solo como paso temporal de migración, con fecha de retirada anotada.
- **MUST NOT** usar `mode: DISABLE` salvo excepción por puerto con ADR (p. ej. un agente de métricas externo).
- **MUST** completar la inyección/inclusión en la malla de los clientes antes de pasar a STRICT; si no, se cortan peticiones.
- **SHOULD** acompañar mTLS con `AuthorizationPolicy`: mTLS autentica, no autoriza.
- **SHOULD** apoyarse en la rotación automática de certificados de Istio y no montar certificados propios (ver `crypto-tls-mtls-key-rotation`).
- **MUST** documentar qué se reproduce en local (mTLS funciona igual en kind/minikube) y qué no (integración con CA de AWS: preparado para AWS, no verificado en real).

## Por qué
Con PERMISSIVE un atacante dentro del clúster sigue hablando en claro con los servicios y no hay identidad verificable para autorizar. STRICT da identidad SPIFFE por workload, base de zero-trust.

## Ejemplos
### Mal
```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: istio-system }
spec:
  mtls:
    mode: PERMISSIVE   # "temporal" desde hace meses
```
### Bien
```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: istio-system }
spec:
  mtls:
    mode: STRICT
---
# Excepción acotada por puerto, con justificación
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: legacy-metrics
  namespace: observability
  annotations: { example.com/adr: "ADR-xxxx" }
spec:
  selector: { matchLabels: { app: legacy-exporter } }
  mtls: { mode: STRICT }
  portLevelMtls:
    9100: { mode: PERMISSIVE }
```
Versión de API (`security.istio.io/v1`).

## Criterios de decisión y trampas
### Cómo decidir
- Activa mTLS estricto por fases: permisivo para descubrir quién habla en claro, estricto cuando todo está en la malla.
- Las excepciones son explícitas y temporales.
### Trampas frecuentes
- Estricto de golpe y caída de cargas fuera de la malla.
- Dejar permisivo indefinidamente.
- Excepciones por puerto sin dueño.
- Asumir que mTLS es autorización.
- Certificados raíz sin plan de rotación.
### Evidencia
- Un informe de tráfico en claro que baja a cero antes de pasar a estricto.

## Checklist de revisión
- [ ] Existe PeerAuthentication STRICT a nivel de malla.
- [ ] Ningún PERMISSIVE/DISABLE sin ADR y fecha.
- [ ] Clientes ya dentro de la malla antes de endurecer.
- [ ] Hay AuthorizationPolicy complementaria.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: deniega PERMISSIVE/DISABLE | 1 | `policies/opa-conftest/istio-mesh-security.rego` |
| `istioctl analyze` en CI del proyecto generado | 1 | pipeline del proyecto (pendiente) |
| Revisión de excepciones | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `authorization-policies`, `zero-trust`, `crypto-tls-mtls-key-rotation`, `sidecar-vs-ambient-decision`.
- Fuentes: istio.io/latest/docs/concepts/security/ y reference de PeerAuthentication.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
