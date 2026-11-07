# Estándares · 21-on-prem-hybrid

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## hybrid-identity-and-networking

- **MUST** un único proveedor de identidad de referencia (Keycloak) federado por OIDC; las cuentas de servicio usan identidades de carga de trabajo, no claves estáticas.
- **MUST** planificar rangos CIDR sin solapes entre sitios, nube y pods/servicios antes de conectar nada.
- **MUST** cifrado en tránsito (VPN IPsec o enlace dedicado más TLS/mTLS) y mínimo privilegio en rutas y firewalls.
- **MUST** DNS híbrido con zonas y reenvío condicional documentados.
- **SHOULD** un segundo camino de red para redundancia.
- **MUST NOT** abrir rangos completos entre sitios; permitir solo puertos y destinos necesarios (`zero-trust`).

## kubernetes-on-prem

- **MUST** control plane HA: 3 o más nodos (número impar) detrás de un balanceador estable para `kube-apiserver`; el endpoint del balanceador debe coincidir con `ControlPlaneEndpoint` de kubeadm.
- **MUST** decidir topología etcd (apilado: menos máquinas; externo: más separación y más infraestructura) y documentarlo en un ADR.
- **MUST** copias de seguridad de etcd probadas con restauración periódica.
- **MUST** plan de actualización por versión menor, de una en una, con nodos de prueba primero.
- **SHOULD** CNI con soporte de NetworkPolicy; Istio como malla (D-cerradas).
- **MUST NOT** exponer el API server a Internet sin restricción de red y autenticación OIDC (Keycloak).

## private-registry

- **MUST** proyectos privados por equipo, con cuentas robot de mínimo privilegio para CI; MUST NOT usar credenciales personales en pipelines.
- **MUST** escaneo de vulnerabilidades al subir y política que bloquee despliegue por severidad (ver `image-scanning`).
- **MUST** desplegar solo imágenes por digest y firmadas (ver `image-signing-and-provenance`).
- **SHOULD** proyecto de caché proxy para registros públicos, evitando dependencias directas de Internet.
- **SHOULD** políticas de retención de tags y réplica a un segundo sitio.
- **MUST NOT** usar el tag `latest` en despliegues.

## storage-and-load-balancing

- **MUST** usar un driver CSI con `StorageClass` explícita; declarar `reclaimPolicy` y `volumeBindingMode: WaitForFirstConsumer` para respetar topología.
- **MUST** documentar el modelo de replicación y durabilidad del almacenamiento elegido (p. ej. Ceph/Rook, Longhorn) y probar la pérdida de un nodo.
- **MUST** respaldar volúmenes con VolumeSnapshots y copia externa; la réplica no es backup.
- **MUST** una solución de LoadBalancer bare-metal (p. ej. MetalLB) con rangos de IP reservados y documentados. TODO-VERIFY modo (L2/BGP) según la red.
- **SHOULD** usar Gateway API (`gateway-api`) para entrada de tráfico.
- **MUST NOT** usar `hostPath` para datos de aplicación.
