---
name: multi-cluster-mesh
description: "Usar al valorar o diseñar una malla Istio que abarque varios clústeres: modelos, confianza compartida y descubrimiento de servicios."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Malla multi-clúster

## Cuándo aplicar y cuándo no
- Aplica cuando hay un requisito real de aislamiento de fallos, residencia de datos o failover entre clústeres.
- No aplica por defecto: un solo clúster con varios namespaces cubre la mayoría de proyectos. La complejidad operativa es alta.

## Reglas
- **MUST** justificar en ADR del proyecto la necesidad multi-clúster antes de adoptarlo.
- **MUST** elegir modelo explícito: primario-remoto o multi-primario, red única o redes distintas.
- **MUST** compartir una raíz de confianza común: CA raíz propia y CA intermedia por clúster; nunca la CA autogenerada por defecto en producción.
- **MUST** custodiar las claves de CA según `secrets-management`; nunca en el repositorio.
- **MUST** usar nombres de red y de clúster únicos y coherentes en la configuración de cada clúster.
- **SHOULD** mantener la misma versión de Istio (o dentro de la ventana soportada) en todos los clústeres.
- **MUST NOT** tratar el multi-clúster como DR completo: los datos no se replican por la malla (ver `multi-cluster-and-dr`).
- **MUST** declarar que en local solo se simula con dos clústeres kind y que el enrutado de red real en AWS no se verifica.

## Por qué
Cada clúster extra multiplica upgrades, certificados y puntos de fallo. Sin raíz de confianza común, mTLS entre clústeres no funciona; con la CA por defecto, una fuga compromete a toda la malla.

## Ejemplos
### Mal
```yaml
# Dos clústeres con el mismo nombre de red y CA autogenerada de cada uno
global:
  meshID: mesh1
  multiCluster: { clusterName: cluster }   # idéntico en ambos
  network: net
```
### Bien
```yaml
# cluster-a (cluster-b análogo con nombres distintos)
global:
  meshID: mesh1
  multiCluster:
    clusterName: cluster-a
  network: network-a
```
Claves exactas de `values`/IstioOperator; seguir la guía oficial de la versión elegida.

## Criterios de decisión y trampas
### Cómo decidir
- Malla multiclúster solo cuando los servicios deben comunicarse entre clústeres con identidad común; valora el coste operativo y los fallos parciales.
- Descubrimiento y confianza compartidos de forma deliberada.
### Trampas frecuentes
- Conectar clústeres por defecto sin necesidad.
- Confianza raíz distinta sin plan.
- Fallos de un clúster que se propagan por la malla.
- Latencia entre regiones ignorada.
- Sin pruebas de pérdida de un clúster.
### Evidencia
- Un ensayo con un clúster fuera de servicio y la conmutación de tráfico observada.

## Checklist de revisión
- [ ] ADR con motivo y modelo elegido.
- [ ] Raíz de confianza común y claves custodiadas.
- [ ] Nombres de clúster y red únicos.
- [ ] Plan de upgrade coordinado.
- [ ] Aclarado qué no cubre (datos, DR).

## Enforcement
Revisión humana: decisión arquitectónica con coste operativo. Verificaciones automáticas (pendiente): `istioctl` de comprobación de remote secrets en el pipeline del proyecto.

| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de ADR multi-clúster | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-cluster-and-dr`, `sidecar-vs-ambient-decision`, `istio-upgrades-and-ops`, `crypto-tls-mtls-key-rotation`.
- Fuentes: istio.io/latest/docs/setup/install/multicluster/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
