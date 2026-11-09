---
name: pwa-and-offline
description: "Usar solo si la SPA necesita instalarse o funcionar sin conexión (PWA, service worker): estrategias de caché, actualizaciones, datos sensibles y cola de escrituras."
metadata:
  block: "27-frontend-react"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# PWA y offline (T3: solo con requisito explícito)

## Cuándo aplicar y cuándo no
- Aplica si hay requisito de instalación, uso sin conexión o notificaciones push, validado con usuarios.
- No aplica a una SPA corporativa que siempre requiere red: un service worker mal gestionado causa más incidencias (versiones atascadas) que beneficios.

## Reglas
- **MUST** documentar el requisito offline: qué funciona sin red, qué datos se guardan, cuánto tiempo y quién los borra.
- **MUST** precachear solo el app shell con hash (generado por Workbox/`vite-plugin-pwa`) y usar estrategia explícita por tipo de recurso (cache-first para assets con hash, network-first o stale-while-revalidate para datos).
- **MUST NOT** cachear respuestas autenticadas, con datos personales o con `Cache-Control: no-store`, ni peticiones de auth/sesión; **MUST** vaciar cachés y almacenamiento local al cerrar sesión.
- **MUST** tener flujo de actualización: detectar nuevo service worker, avisar al usuario y recargar de forma controlada; servir `sw.js` con `no-cache` (ver `build-and-deploy`).
- **MUST** tener un "kill switch": un service worker de reemplazo que se desregistra y limpia cachés, probado antes de lanzar.
- **MUST** gestionar escrituras offline con cola persistente (IndexedDB), idempotencia (`idempotency-keys`) y resolución de conflictos definida; **MUST NOT** asumir orden ni entrega única.
- **MUST** exigir HTTPS (los service workers solo operan en contextos seguros) y mantener la CSP (`security-frontend`).
- **SHOULD** cifrar o minimizar datos sensibles en el dispositivo; el almacenamiento del navegador es accesible a scripts del mismo origen.
- **SHOULD** declarar un manifiesto web válido y probar instalación en los navegadores objetivo; el soporte varía por plataforma.

## Por qué
El service worker es un proxy persistente en el navegador del usuario: un error de caché puede dejar a miles de clientes con una versión rota hasta que se desregistre. El offline con escritura introduce sincronización y conflictos, que son problemas de diseño de datos, no de frontend.

## Ejemplos
### Mal
```js
self.addEventListener("fetch", (e) => {
  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request))); // cachea /api/me, index.html eterno
});
```
### Bien
```ts
// Estrategia por ruta (Workbox)
registerRoute(({ url }) => url.pathname.startsWith("/assets/"), new CacheFirst({ cacheName: "assets" }));
registerRoute(({ url }) => url.pathname.startsWith("/api/catalog"), new StaleWhileRevalidate({ cacheName: "catalog" }));
// /api/* autenticado: sin ruta => siempre red
```
```js
// sw.js kill switch (se publica solo si hay que retirar la PWA)
self.addEventListener("activate", async () => {
  await Promise.all((await caches.keys()).map((k) => caches.delete(k)));
  await self.registration.unregister();
});
```

## Criterios de decisión y trampas
### Cómo decidir
- Define qué debe funcionar sin red antes de empezar; «offline» sin requisito es coste sin beneficio.
- Precachea solo la carcasa con hash; datos con estrategias explícitas y caducidad.
- Planifica la sincronización y los conflictos si hay escritura sin conexión.
### Trampas frecuentes
- Cachear respuestas autenticadas o con datos personales.
- Un service worker sin forma de actualizarse (usuarios atrapados en una versión vieja).
- Servir datos obsoletos sin avisar.
- Cola de escrituras sin resolución de conflictos.
- No probar la instalación en los navegadores y plataformas objetivo.
### Evidencia
- Un flujo de actualización probado y una lista de lo que se guarda en el dispositivo y cuánto tiempo.

## Checklist de revisión
- [ ] Requisito offline documentado.
- [ ] Sin cachear datos autenticados/personales; limpieza al cerrar sesión.
- [ ] Flujo de actualización y `sw.js` sin caché.
- [ ] Kill switch probado.
- [ ] Cola de escrituras idempotente con política de conflictos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del requisito y de la estrategia de caché | 3 | revisión humana |
| Test E2E de actualización y de logout (Playwright) | 2 | tests del proyecto generado (pendiente) |
| Lighthouse (instalabilidad) | 2 | pipeline del proyecto generado (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `build-and-deploy`, `security-frontend`, `frontend-performance`, `idempotency-keys`, `state-management`.
- Fuentes: MDN (Service Worker API, PWA) y documentación de Workbox.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T3
