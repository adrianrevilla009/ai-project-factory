---
name: observability-frontend
description: "Usar al instrumentar la SPA con OpenTelemetry del navegador, RUM, Web Vitals y reporte de errores, correlacionando con trazas del backend."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Observabilidad del frontend (OTel navegador y RUM)

## Cuándo aplicar y cuándo no
- Aplica a la instrumentación de la SPA: trazas de `fetch`, Web Vitals, errores no capturados y eventos de negocio mínimos.
- No aplica a la observabilidad del backend (`otel-fundamentals-and-semconv`, `tracing`). Presupuestos y objetivos de rendimiento: `frontend-performance`.

## Reglas
- **MUST** enviar telemetría a un colector propio por OTLP/HTTP (o endpoint de la plataforma) con CORS restringido a los orígenes de la app; nunca claves de backends de pago en el bundle.
- **MUST** propagar `traceparent` solo hacia orígenes propios (lista explícita, p. ej. `propagateTraceHeaderCorsUrls` en la instrumentación de fetch) para unir la traza del navegador con la del backend.
- **MUST** medir LCP, INP y CLS en campo con la librería `web-vitals` (`onLCP`, `onINP`, `onCLS`) y enviarlas con la versión de release y la ruta (plantilla, no URL con ids).
- **MUST** capturar errores no gestionados (`window.onerror`, `unhandledrejection`, error boundaries; ver `error-handling-and-boundaries`) con release y mapas de código fuente subidos al sistema de errores, no públicos.
- **MUST NOT** enviar PII, tokens, cuerpos de petición, contenido de formularios ni query strings completas; sanear antes de enviar y respetar el consentimiento (`data-privacy-in-db`, normativa: borrador por confirmar).
- **MUST NOT** crear atributos de alta cardinalidad (id de usuario, URL completa) como dimensiones de métricas (`cardinality-and-cost-governance`).
- **SHOULD** muestrear (p. ej. porcentaje de sesiones) y usar `navigator.sendBeacon`/`keepalive` al descargar la página.
- **SHOULD** definir SLOs de experiencia (p. ej. % de cargas con LCP bueno) en `dashboards-and-slos-as-code`.
- El soporte de OTel JS en navegador tiene partes marcadas como experimentales: fijar versiones y revisar el estado.

## Por qué
Los laboratorios no reproducen redes, dispositivos ni extensiones reales. Sin correlación con el backend, una pantalla lenta no se atribuye a API, red o render. Y el navegador es entorno hostil: todo lo que se envía es visible para el usuario.

## Ejemplos
### Mal
```ts
Sentry_like.init({ dsn: "https://key@example.invalid/1", sendDefaultPii: true });
fetch(url, { headers: { traceparent: tp } }); // a cualquier origen, incluidos terceros
```
### Bien
```ts
import { onLCP, onINP, onCLS } from "web-vitals";

const send = (m: { name: string; value: number; id: string }) =>
  navigator.sendBeacon("/rum", JSON.stringify({ ...m, release: __APP_VERSION__, route: routeTemplate() }));
onLCP(send); onINP(send); onCLS(send);
```
```ts
// Propagacion solo a la API propia
new FetchInstrumentation({ propagateTraceHeaderCorsUrls: [/^https:\/\/api\.example\.com\//] });
```

## Criterios de decisión y trampas
### Cómo decidir
- Mide experiencia real (Web Vitals, errores, trazas de las llamadas) y envíala a un colector propio.
- Muestrea: la telemetría del navegador es voluminosa; define tasas por tipo.
- La traza se propaga solo a orígenes propios.
### Trampas frecuentes
- Enviar datos personales o contenido de formularios en la telemetría.
- Propagar cabeceras de traza a terceros.
- Capturar todo sin muestreo y pagar el coste.
- Errores sin versión del código ni mapa de fuentes.
- Ignorar el consentimiento cuando la normativa lo exige.
### Evidencia
- Cada error en producción se vincula a una versión y, si procede, a una traza del servidor.

## Checklist de revisión
- [ ] Web Vitals en campo con release y ruta plantilla.
- [ ] `traceparent` solo hacia orígenes propios.
- [ ] Sin PII ni tokens en telemetría; muestreo definido.
- [ ] Source maps privados y asociados a la release.
- [ ] Colector con CORS y límites de tasa.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de payloads de telemetría (PII) | 3 | revisión humana / agente `code-reviewer` |
| Test que verifica el saneado de eventos antes de enviar | 2 | tests del proyecto generado (pendiente) |
| Regla de CORS/CSP `connect-src` del colector | 2 | ver `security-frontend` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `frontend-performance`, `error-handling-and-boundaries`, `otel-fundamentals-and-semconv`, `tracing`, `cardinality-and-cost-governance`.
- Fuentes: https://github.com/GoogleChrome/web-vitals; https://opentelemetry.io/docs/languages/js/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
