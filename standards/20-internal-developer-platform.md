# Estándares · 20-internal-developer-platform

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## backstage

- **MUST** que cada componente desplegable tenga un `catalog-info.yaml` en la raíz de su repositorio, con `spec.type`, `spec.lifecycle` y `spec.owner` (los tres son obligatorios para `Component`).
- **MUST** que `spec.owner` apunte a un grupo/equipo del catálogo, nunca a una persona individual ni a un valor vacío.
- **MUST** declarar dependencias (`dependsOn`, `providesApis`, `consumesApis`) para que el grafo del catálogo refleje la realidad.
- **MUST** publicar documentación con TechDocs (docs-as-code: `mkdocs.yml` + `docs/` en el mismo repo) en vez de wikis externas.
- **SHOULD** definir scorecards como reglas objetivas y automáticas (owner presente, runbook enlazado, SLO declarado, cobertura de SBOM), nunca como puntuación subjetiva.
- **SHOULD** usar autenticación OIDC contra Keycloak (D-identidad) y no el proveedor de invitados fuera de desarrollo local.
- **MUST NOT** usar plugins de pago por defecto (D16); preferir el núcleo OSS de Backstage.
- **MUST NOT** editar entidades a mano en la UI: la fuente de verdad es Git.

## developer-experience-metrics

- **MUST** medir a nivel de equipo/servicio, nunca ranking de individuos.
- **MUST** combinar métricas de flujo (las cuatro de DORA) con señales cualitativas (encuesta trimestral corta de satisfacción y fricciones).
- **MUST** definir cada métrica con fórmula, fuente de datos y qué evento cuenta (qué es "despliegue", qué es "fallo").
- **MUST** medir también tiempo hasta el primer despliegue de un desarrollador nuevo y tiempo de creación de un servicio con el golden path.
- **SHOULD** obtener datos de forma automática (Git, CI, GitOps, incidentes), no de hojas manuales.
- **SHOULD** usar tendencias y mediana/percentiles, no medias de un solo dato.
- **MUST NOT** usar una métrica como objetivo contractual (ley de Goodhart): se falsea.
- **MUST NOT** publicar datos de encuestas identificables.

## ephemeral-environments

- **MUST** un namespace por PR con nombre derivado (`pr-<número>`), etiquetas `owner` y `ttl`, y `ResourceQuota` + `LimitRange` + `NetworkPolicy` por defecto deny.
- **MUST** destrucción automática al cerrar el PR y por TTL máximo (p. ej. 48 h) como red de seguridad.
- **MUST** datos sintéticos o anonimizados; MUST NOT copiar datos de producción (`pii-and-data-classification`).
- **MUST** secretos propios del entorno, de menor privilegio y de corta vida; nunca reutilizar los de staging/prod.
- **SHOULD** desplegar por GitOps (ApplicationSet con generador de PR en Argo CD) en vez de scripts imperativos.
- **SHOULD** limitar el nº de entornos simultáneos y escalar a cero fuera de horario.
- **SHOULD** comentar en el PR la URL y el estado del entorno.
- **MUST NOT** exponer el entorno a Internet sin autenticación.

## golden-paths-governance

- **MUST** que cada golden path tenga dueño (equipo), versión semántica, changelog y fecha de revisión.
- **MUST** que el camino sea más fácil que la alternativa: si desviarse es más cómodo, el camino ha fallado.
- **MUST** separar lo obligatorio (seguridad, observabilidad, trazabilidad de dueño) de lo recomendado (framework, estructura).
- **MUST** documentar el proceso de desviación: ADR corto con motivo, riesgo, dueño y fecha de caducidad.
- **SHOULD** medir adopción y satisfacción (ver `developer-experience-metrics`) y retirar caminos que nadie usa.
- **SHOULD** anunciar cambios incompatibles con un periodo de migración y herramientas de actualización automática.
- **MUST NOT** convertir el camino en un gate manual: el cumplimiento se comprueba con policies automáticas.
- **MUST NOT** mantener caminos zombis sin dueño.

## software-templates

- **MUST** que la plantilla sea `kind: Template` con `apiVersion: scaffolder.backstage.io/v1beta3`, con `parameters`, `steps` (cada uno con `id`, `name`, `action`, `input`) y `output`.
- **MUST** que lo generado incluya: `catalog-info.yaml` con owner, pipeline CI, Dockerfile multistage, `docs/` + `mkdocs.yml`, y configuración de seguridad (SBOM, escaneo).
- **MUST** pedir `owner` con el selector de propietarios del catálogo (`OwnerPicker`), no texto libre.
- **MUST** versionar la plantilla (tag Git) y registrar en el servicio generado qué versión de plantilla lo creó.
- **SHOULD** mantener la plantilla mínima: lo opcional va en parámetros con valores por defecto seguros.
- **SHOULD** probar la plantilla en CI generando un servicio de muestra y ejecutando su build.
- **MUST NOT** incluir secretos ni credenciales reales en el esqueleto; solo referencias.
- **MUST NOT** dejar plantillas sin dueño: una plantilla obsoleta propaga deuda a cada servicio nuevo.
