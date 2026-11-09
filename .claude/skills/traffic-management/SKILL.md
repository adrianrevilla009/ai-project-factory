---
name: traffic-management
description: "Usar al definir VirtualService, DestinationRule, timeouts, outlier detection y pools de conexión en Istio."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Gestión de tráfico en Istio

## Cuándo aplicar y cuándo no
- Aplica al definir enrutado, timeouts, límites de conexión y expulsión de instancias fallidas dentro de la malla.
- No aplica a la lógica de reintentos de negocio (ver `mesh-vs-app-resilience`) ni a la entrada externa (ver `gateway-api`).

## Reglas
- **MUST** declarar `timeout` en cada ruta de `VirtualService`; sin él el defecto de Envoy puede no ajustarse a tu SLO (en Istio el timeout HTTP de una ruta está desactivado por defecto, según la referencia de `VirtualService`, verificado el 2026-11-08).
- **MUST** definir en `DestinationRule` `connectionPool` y `outlierDetection` para servicios críticos.
- **MUST** nombrar `subsets` por etiqueta de versión (`version`), no por IP.
- **MUST NOT** declarar el mismo host en varios `VirtualService` sin `gateways`/`hosts` coordinados: el resultado es indeterminado.
- **SHOULD** mantener `VirtualService` y `DestinationRule` junto al servicio que los posee.
- **SHOULD** validar con `istioctl analyze` antes de aplicar.
- **MUST** ajustar timeouts de forma coherente: timeout de ruta mayor que el del cliente HTTP interno falla primero en el cliente.

## Por qué
Sin límites, un servicio lento acapara conexiones y propaga la caída. La malla da estos controles de forma uniforme, pero la configuración incoherente entre capas produce fallos difíciles de diagnosticar.

## Ejemplos
### Mal
```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata: { name: orders }
spec:
  hosts: [orders]
  http:
    - route: [{ destination: { host: orders } }]   # sin timeout
```
### Bien
```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata: { name: orders, namespace: orders }
spec:
  hosts: [orders]
  http:
    - timeout: 3s
      route: [{ destination: { host: orders, subset: v1 } }]
---
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata: { name: orders, namespace: orders }
spec:
  host: orders
  subsets: [{ name: v1, labels: { version: v1 } }]
  trafficPolicy:
    connectionPool:
      http: { http1MaxPendingRequests: 100, maxRequestsPerConnection: 100 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
```
`networking.istio.io/v1` es la versión servida y almacenada (verificado el 2026-11-08); los valores numéricos se ajustan con pruebas de carga.

## Criterios de decisión y trampas
### Cómo decidir
- Tiempos máximos, reintentos acotados y detección de valores atípicos configurados por ruta con valores justificados; reparte tráfico con pesos para despliegues progresivos.
- Los reintentos de la malla y los de la aplicación no deben multiplicarse.
### Trampas frecuentes
- Reintentos en la malla y en el cliente a la vez.
- Tiempos máximos mayores que el de la petición entrante.
- Pesos que no suman o rutas que se pisan.
- Sin tiempo máximo en rutas lentas.
- Configuración por servicio sin estándar.
### Evidencia
- Una prueba con un backend lento muestra el tiempo máximo y los reintentos esperados.

## Checklist de revisión
- [ ] Timeout en cada ruta.
- [ ] `connectionPool` y `outlierDetection` en críticos.
- [ ] Un único VirtualService efectivo por host.
- [ ] `istioctl analyze` limpio.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `istioctl analyze` en CI del proyecto generado | 1 | pipeline del proyecto (pendiente) |
| Revisión de coherencia de timeouts | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `mesh-vs-app-resilience`, `resilience`, `http-clients-and-timeouts`, `canary-and-traffic-splitting`.
- Fuentes: istio.io/latest/docs/concepts/traffic-management/.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
