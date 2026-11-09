---
name: ingress-and-egress-gateways
description: "Usar al configurar la entrada y salida de tráfico de la malla Istio: gateway de ingress, egress controlado y ServiceEntry."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Gateways de ingress y egress

## Cuándo aplicar y cuándo no
- Aplica a todo tráfico que cruza el borde de la malla, en ambos sentidos.
- No aplica al tráfico interno entre servicios (ver `traffic-management`).

## Reglas
- **MUST** desplegar el gateway de ingress en un namespace propio (`istio-ingress`), separado de `istio-system`, con su propio escalado y PDB.
- **MUST** definir la entrada con Gateway API (ver `gateway-api`); `Gateway` de Istio clásico solo si hay una carencia documentada.
- **MUST** configurar `outboundTrafficPolicy.mode: REGISTRY_ONLY` en entornos con requisito de egress controlado y declarar cada destino externo con `ServiceEntry`.
- **SHOULD** enrutar por un gateway de egress los destinos externos que requieran auditoría o IP fija.
- **MUST** aplicar `AuthorizationPolicy` al propio gateway (qué hosts y rutas se aceptan).
- **MUST NOT** exponer dashboards de administración (Kiali, Prometheus) por el gateway público.
- **MUST** indicar que en local (kind/minikube) el balanceador es simulado (p. ej. port-forward o MetalLB) y que el balanceador real de AWS no se reproduce: preparado para AWS, no verificado en real.

## Por qué
Sin egress controlado, un pod comprometido exfiltra a cualquier destino. Declarar destinos con `ServiceEntry` deja inventario y permite políticas y métricas.

## Ejemplos
### Mal
```yaml
# Malla abierta: cualquier salida permitida y sin inventario
meshConfig:
  outboundTrafficPolicy:
    mode: ALLOW_ANY
```
### Bien
```yaml
meshConfig:
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY
---
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata: { name: payments-provider, namespace: orders }
spec:
  hosts: [api.payments.example.com]
  location: MESH_EXTERNAL
  resolution: DNS
  ports: [{ number: 443, name: https, protocol: TLS }]
```
Ubicación exacta de `meshConfig` según método de instalación.

## Criterios de decisión y trampas
### Cómo decidir
- Entrada y salida controladas con pasarelas dedicadas: la salida hacia Internet solo por una pasarela con lista permitida y registro.
- Escala y protege las pasarelas como un servicio crítico.
### Trampas frecuentes
- Salida libre desde cada carga.
- Una pasarela única sin alta disponibilidad.
- Sin registro del tráfico saliente.
- Listas permitidas con comodines.
- Mezclar tráfico de entrada y salida en el mismo punto sin aislamiento.
### Evidencia
- Una prueba intenta salir a un destino no permitido y falla.

## Checklist de revisión
- [ ] Ingress en namespace propio con PDB y HPA.
- [ ] `REGISTRY_ONLY` y `ServiceEntry` por destino externo.
- [ ] Políticas de autorización en el gateway.
- [ ] Ninguna UI de operación expuesta públicamente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: `ALLOW_ANY` en meshConfig (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión de destinos externos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `gateway-api`, `authorization-policies`, `zero-trust`, `dos-and-rate-limiting`.
- Fuentes: istio.io/latest/docs/tasks/traffic-management/egress/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
