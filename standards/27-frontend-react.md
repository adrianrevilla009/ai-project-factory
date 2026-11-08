# Estándares · 27-frontend-react

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## accessibility

- **MUST** usar elementos semánticos nativos (`button`, `a`, `label`, `table`, `nav`, `main`) antes que `div` con roles ARIA; la primera regla de ARIA es no usarlo si existe un elemento nativo.
- **MUST** que toda funcionalidad sea operable con teclado, con foco visible y orden lógico (WCAG 2.2: 2.4.7, 2.4.11 foco no oculto).
- **MUST** asociar cada campo con su `<label>` y enlazar errores con `aria-describedby`; anunciar errores de formulario y cambios de ruta (región `aria-live` o gestión de foco al `h1`).
- **MUST** respetar contraste mínimo AA (4,5:1 texto normal, 3:1 texto grande y componentes de UI) y no transmitir información solo por color.
- **MUST** que los objetivos táctiles midan al menos 24x24 px CSS (WCAG 2.2: 2.5.8).
- **MUST** que modales/diálogos atrapen y devuelvan el foco; preferir `<dialog>` o una librería de primitivas accesibles ya adoptada por el design system.
- **MUST NOT** usar `div`/`span` con `onClick` ni `tabIndex` positivo; **MUST NOT** deshabilitar `outline` sin alternativa.
- **MUST NOT** pedir transcribir o recordar contraseñas sin alternativa (autenticación accesible, 3.3.8); permitir pegar y gestores de contraseñas.
- **SHOULD** respetar `prefers-reduced-motion` y permitir zoom/reflow hasta 400 %.
- **SHOULD** ejecutar axe automatizado en tests de componente y en E2E; lo automático cubre solo una parte de los criterios, el resto exige revisión manual con teclado y lector de pantalla.

## api-client-from-openapi

- **MUST** que el contrato OpenAPI sea la fuente de verdad; el frontend no redefine tipos de la API a mano.
- **MUST** generar tipos/cliente con una herramienta (p. ej. openapi-typescript + openapi-fetch, u Orval; comprobar elección y versión) y confirmar el comando en `package.json`.
- **MUST** ubicar el código generado en `src/shared/api/generated/`, marcado como generado y excluido de lint/formato.
- **MUST NOT** editar a mano el código generado; se cambia el contrato y se regenera.
- **MUST** regenerar en CI y fallar si el resultado difiere del commiteado (drift).
- **MUST** centralizar base URL, cabeceras, timeouts y manejo de 401 en un único cliente en `src/shared/api`.
- **MUST** cada feature envuelva el cliente en funciones de su `api/` y las consuma vía TanStack Query (`state-management`).
- **SHOULD** validar en ejecución con Zod las respuestas críticas si el backend no es de confianza total.
- **MUST NOT** hardcodear URLs de entorno; usar variables `VITE_*` (solo valores públicos, nunca secretos).

## auth-and-session

- **MUST** usar Authorization Code con PKCE; nunca flujo implícito ni password grant.
- **SHOULD** preferir el patrón BFF: el backend-for-frontend hace el intercambio OIDC, guarda los tokens y entrega al navegador una cookie de sesión `HttpOnly; Secure; SameSite` (`bff-and-api-gateway`).
- **MUST NOT** guardar access/refresh tokens en `localStorage`/`sessionStorage` ni en el store persistido.
- **MUST** si no hay BFF (SPA pura), mantener el access token solo en memoria y documentar el riesgo en un ADR; refresh token en navegador: comprobar con la guía vigente de OAuth 2.0 for Browser-Based Apps.
- **MUST** con sesión por cookie, proteger mutaciones frente a CSRF (cabecera personalizada o token) y enviar `credentials: 'include'` solo al propio origen/BFF.
- **MUST** obtener el usuario actual de un endpoint (`/me`) y guardarlo como server-state, no decodificar JWT en el cliente para decidir permisos.
- **MUST** tratar 401 centralizadamente (redirigir a login) y 403 como pantalla de acceso denegado.
- **MUST** que la UI oculte, nunca proteja: todo permiso se vuelve a comprobar en el backend.
- **MUST NOT** poner `client_secret` ni secretos en el bundle (las variables `VITE_*` son públicas).

## build-and-deploy

- **MUST** fijar versión de Node y de pnpm (`packageManager` en `package.json`, `.nvmrc`) y instalar con `pnpm install --frozen-lockfile` en CI.
- **MUST** construir una vez y promocionar el mismo artefacto entre entornos (`environment-promotion`); la configuración de entorno se resuelve en runtime (p. ej. `/config.json` servido sin caché), no recompilando.
- **MUST** servir `assets/*` con hash en el nombre con `Cache-Control: public, max-age=31536000, immutable` y `index.html` con `no-cache` (revalida siempre).
- **MUST** subir primero los assets con hash y por último `index.html`; invalidar en CloudFront solo `/index.html` y `/config.json`, no `/*`.
- **MUST** mantener el bucket S3 privado con acceso solo desde CloudFront (Origin Access Control), HTTPS obligatorio y cabeceras de seguridad (`security-frontend`).
- **MUST** devolver `index.html` para rutas de cliente (respuestas de error personalizadas 403/404 -> `/index.html` con 200, o función de borde) sin ocultar 404 de assets reales.
- **SHOULD** multi-región con bucket réplica (replicación entre regiones) y origin group de CloudFront con failover; documentar RTO/RPO (`tier-model-and-rpo-rto`).
- **SHOULD** publicar source maps solo en el sistema de errores (`observability-frontend`), no en el bucket público.
- **MUST NOT** incluir secretos en variables `VITE_*`: todo lo prefijado se incrusta en el bundle público.

## component-patterns

- **MUST** usar componentes de función con hooks; sin clases salvo error boundaries si no se usa `react-error-boundary`.
- **MUST** preferir composición (`children`, slots) a herencia y a props booleanas en cascada (`isPrimary`, `isLarge`...).
- **SHOULD** usar compound components (contexto interno) para widgets con partes coordinadas: `Tabs`, `Menu`, `Dialog`.
- **SHOULD** extraer a un hook propio (`useX`) la lógica con estado/efectos que se repite; el componente queda como vista.
- **MAY** usar render props o `children` como función cuando el padre debe controlar el renderizado de cada elemento.
- **MUST** respetar las reglas de hooks: llamadas incondicionales, solo en componentes o hooks.
- **MUST** `key` estable y única en listas (id de dominio, nunca el índice si el orden cambia).
- **MUST NOT** definir componentes dentro de otros componentes (se remontan en cada render).
- **MUST NOT** usar `useEffect` para derivar estado ni para responder a eventos; usar el handler del evento.
- **SHOULD** medir antes de memoizar (`memo`, `useMemo`, `useCallback`); ver `frontend-performance`.
- **SHOULD** que un componente tenga una sola razón de cambio y menos de ~150 líneas.

## design-system-and-tokens

- **MUST** definir tokens semánticos (`color.text.primary`, `space.4`, `radius.md`) como variables CSS en un único lugar de `src/shared/ui/tokens`.
- **MUST NOT** usar valores literales (`#3b82f6`, `13px`) en componentes de feature; solo tokens.
- **MUST** separar tokens primitivos (paleta) de semánticos (uso); los temas (claro/oscuro) redefinen solo los semánticos.
- **MUST** que los componentes base (`Button`, `Input`, `Dialog`...) vivan en `src/shared/ui`, sin lógica de negocio ni llamadas a API.
- **SHOULD** documentar cada componente base en Storybook con sus variantes y estados (foco, deshabilitado, error).
- **SHOULD** apoyar primitivas accesibles ya probadas (p. ej. Radix UI, React Aria) antes que reimplementar diálogos o menús.
- **MUST** cumplir contraste mínimo de WCAG 2.2 en los pares de tokens (comprobar ratios) y verificarlo en Storybook.
- **MUST NOT** copiar componentes entre features: si se repite dos veces con intención común, sube a `shared/ui`.
- **SHOULD** versionar cambios de tokens con nota de migración si hay varios consumidores.

## error-handling-and-boundaries

- **MUST** tener un error boundary global en `src/app` y otros por zona (layout, widget independiente) para que un fallo no tumbe toda la pantalla.
- **MUST** que cada boundary ofrezca una acción de recuperación (reintentar, volver) y no muestre trazas ni mensajes internos al usuario.
- **MUST** tratar los errores de red como estado de UI: cada consulta/mutación muestra carga, vacío y error explícitos.
- **MUST** interpretar las respuestas de error del backend como Problem Details (RFC 9457; `error-handling-problem-details`) y mostrar `title`/`detail` solo si son aptos para usuario.
- **MUST NOT** capturar y tragar errores (`catch {}` vacío); relanzar, mostrar o reportar.
- **MUST** los errores de carga de chunk lazy (despliegue nuevo) llevar a recarga controlada.
- **SHOULD** usar `react-error-boundary` (o un `errorElement` del router) en lugar de clases propias; comprobar API vigente.
- **SHOULD** reportar errores a un servicio de observabilidad con identificador de correlación, sin PII ni tokens (`logging-rules`).
- **MUST NOT** esperar que un boundary capture errores de eventos, `setTimeout` o promesas; esos se gestionan donde ocurren.

## feature-flags-ui

- **MUST** acceder a los flags mediante una abstracción única (cliente OpenFeature y hooks propios), nunca leyendo el proveedor directamente en componentes.
- **MUST** definir valor por defecto seguro (feature apagada) para cuando el proveedor falle o tarde; la app debe funcionar sin proveedor.
- **MUST** evaluar el flag una vez por vista y evitar flicker: resolver antes del primer render de la zona afectada (carga inicial o esqueleto), no mostrar A y luego B.
- **MUST NOT** usar un flag como control de seguridad: la UI oculta, el backend autoriza (`authz-rbac-abac-rebac`); un flag expuesto en el cliente es visible y manipulable.
- **MUST NOT** enviar al proveedor PII innecesaria en el contexto de evaluación; usar identificadores seudónimos y atributos mínimos.
- **MUST** dar a cada flag dueño, fecha de caducidad y ticket de retirada; eliminar el código muerto de ambas ramas al consolidar.
- **SHOULD** limitar el número de flags activos y evitar combinatoria (flags anidados); nombrar con convención `area.feature`.
- **SHOULD** testear ambas ramas (Vitest con proveedor en memoria) y registrar la variante en la telemetría (`observability-frontend`).

## forms-and-validation

- **MUST** usar React Hook Form con `zodResolver` y un esquema Zod por formulario; el tipo del formulario sale de `z.infer`.
- **MUST** que la validación del cliente sea ayuda de UX: el backend valida siempre (`input-validation-output-encoding`).
- **MUST** mostrar los errores junto al campo, enlazados con `aria-invalid` y `aria-describedby`, y mover el foco al primer error al enviar.
- **MUST** deshabilitar el envío mientras `isSubmitting` para evitar dobles envíos; la idempotencia real es del backend (`idempotency-keys`).
- **MUST** mapear los errores 400/422 del servidor (Problem Details) a campos con `setError`.
- **SHOULD** compartir el esquema entre formulario y cliente API solo si procede del contrato OpenAPI; no duplicar reglas a mano (comprobar generación de Zod desde OpenAPI).
- **SHOULD** valores por defecto explícitos en `defaultValues`; sin inputs no controlados mezclados.
- **MUST NOT** guardar contraseñas ni datos sensibles en el estado global ni en el almacenamiento del navegador.
- **MUST NOT** usar `any` en los handlers (`typescript-strict-rules`).

## frontend-architecture

- **MUST** organizar `src/` en tres capas: `src/app` (arranque, router, providers), `src/features/<name>` (casos de uso) y `src/shared` (UI genérica, utilidades, cliente API).
- **MUST** respetar la dirección `app -> features -> shared`; nunca al revés.
- **MUST NOT** importar de una feature a otra; la composición ocurre en `src/app` o en una página.
- **MUST** exponer cada feature solo por su `index.ts`; el resto es interno.
- **MUST NOT** crear carpetas globales por tipo (`components/`, `hooks/`, `utils/` con todo mezclado).
- **SHOULD** dentro de una feature: `api/`, `components/`, `hooks/`, `types.ts`, tests junto al código.
- **SHOULD** subir a `shared` solo tras el segundo uso real (no anticipar).
- **MUST NOT** ciclos de importación.

## frontend-i18n-and-formatting

- **MUST** externalizar todo texto visible a catálogos por idioma (clave estable, sin concatenar frases).
- **MUST** usar formato ICU MessageFormat (o equivalente de la librería elegida) para plurales y género; **MUST NOT** construir plurales con `n === 1 ? ... : ...`.
- **MUST** formatear fechas, números y monedas con `Intl.*` (`DateTimeFormat`, `NumberFormat`, `ListFormat`, `RelativeTimeFormat`) con el locale activo.
- **MUST** transmitir y almacenar fechas en ISO 8601 UTC y convertirlas solo al mostrarlas; la moneda viaja como código ISO 4217 + importe, nunca como string formateado.
- **MUST** cargar cada catálogo de idioma bajo demanda (code splitting), no todos en el bundle inicial.
- **MUST** fijar `<html lang>` y `dir` según el locale activo; **SHOULD** usar propiedades CSS lógicas (`margin-inline-start`) para soportar RTL.
- **SHOULD** tener un idioma de referencia y un test que falle si faltan claves en otros idiomas.
- **MUST NOT** incrustar HTML en traducciones; usar componentes de interpolación de la librería.

## frontend-performance

- **MUST** definir objetivos en el percentil 75 por móvil y escritorio: LCP <= 2,5 s, INP <= 200 ms, CLS <= 0,1 (https://web.dev/articles/vitals, consultado 2026-11-07).
- **MUST** fijar un presupuesto de bundle (JS inicial gzip/brotli por ruta) y hacer fallar el CI si se supera; el valor numérico lo decide el proyecto (comprobar con datos reales).
- **MUST** medir con datos de campo (RUM, ver `observability-frontend`) además de laboratorio (Lighthouse).
- **MUST** reservar espacio para imágenes y medios (`width`/`height` o `aspect-ratio`) para evitar CLS; **SHOULD** usar `loading="lazy"` salvo en la imagen LCP.
- **MUST NOT** importar librerías enteras para una función (usar imports por módulo o alternativas ligeras); revisar el análisis de bundle ante cada dependencia nueva.
- **SHOULD** virtualizar listas largas y mover trabajo pesado a Web Workers o `startTransition`/`useDeferredValue` para proteger INP.
- **SHOULD** medir antes de memoizar: `React.memo`/`useMemo` solo con evidencia del profiler.
- **SHOULD** servir assets con hash y `Cache-Control: immutable` (ver `build-and-deploy`) y fuentes con `font-display: swap`.

## micro-frontends

- **MUST** documentar en un ADR el problema organizativo que resuelve, alternativas (monorepo con límites por feature, librerías internas) y coste asumido.
- **MUST** definir contratos explícitos entre host y remotos: rutas, eventos/props versionados, tipos compartidos publicados; sin acceso a estado interno ajeno.
- **MUST** compartir como singleton solo lo imprescindible (React, router) con rangos de versión acordados; una divergencia de React entre remotos rompe hooks.
- **MUST** unificar sesión, design system y tokens (`design-system-and-tokens`) y una sola política CSP/seguridad (`security-frontend`); cada remoto con aislamiento de estilos.
- **MUST** que el host degrade con elegancia si un remoto no carga (error boundary + fallback) y que haya observabilidad por remoto (`observability-frontend`).
- **MUST NOT** comunicar remotos mediante estado global mutable ni variables en `window`; usar eventos tipados o props.
- **SHOULD** versionar y desplegar remotos de forma inmutable con rollback independiente (`build-and-deploy`) y probar contratos en CI (`contract-testing`).
- **SHOULD** medir el coste: bytes duplicados, tiempo de carga extra y esfuerzo de coordinación (`frontend-performance`).

## observability-frontend

- **MUST** enviar telemetría a un colector propio por OTLP/HTTP (o endpoint de la plataforma) con CORS restringido a los orígenes de la app; nunca claves de backends de pago en el bundle.
- **MUST** propagar `traceparent` solo hacia orígenes propios (lista explícita, p. ej. `propagateTraceHeaderCorsUrls` en la instrumentación de fetch; comprobar nombre exacto) para unir la traza del navegador con la del backend.
- **MUST** medir LCP, INP y CLS en campo con la librería `web-vitals` (`onLCP`, `onINP`, `onCLS`) y enviarlas con la versión de release y la ruta (plantilla, no URL con ids).
- **MUST** capturar errores no gestionados (`window.onerror`, `unhandledrejection`, error boundaries; ver `error-handling-and-boundaries`) con release y mapas de código fuente subidos al sistema de errores, no públicos.
- **MUST NOT** enviar PII, tokens, cuerpos de petición, contenido de formularios ni query strings completas; sanear antes de enviar y respetar el consentimiento (`data-privacy-in-db`, normativa: borrador por confirmar).
- **MUST NOT** crear atributos de alta cardinalidad (id de usuario, URL completa) como dimensiones de métricas (`cardinality-and-cost-governance`).
- **SHOULD** muestrear (p. ej. porcentaje de sesiones) y usar `navigator.sendBeacon`/`keepalive` al descargar la página.
- **SHOULD** definir SLOs de experiencia (p. ej. % de cargas con LCP bueno) en `dashboards-and-slos-as-code`.
- El soporte de OTel JS en navegador tiene partes marcadas como experimentales: fijar versiones y revisar el estado (comprobar https://opentelemetry.io/docs/languages/js/).

## pwa-and-offline

- **MUST** documentar el requisito offline: qué funciona sin red, qué datos se guardan, cuánto tiempo y quién los borra.
- **MUST** precachear solo el app shell con hash (generado por Workbox/`vite-plugin-pwa`) y usar estrategia explícita por tipo de recurso (cache-first para assets con hash, network-first o stale-while-revalidate para datos).
- **MUST NOT** cachear respuestas autenticadas, con datos personales o con `Cache-Control: no-store`, ni peticiones de auth/sesión; **MUST** vaciar cachés y almacenamiento local al cerrar sesión.
- **MUST** tener flujo de actualización: detectar nuevo service worker, avisar al usuario y recargar de forma controlada; servir `sw.js` con `no-cache` (ver `build-and-deploy`).
- **MUST** tener un "kill switch": un service worker de reemplazo que se desregistra y limpia cachés, probado antes de lanzar.
- **MUST** gestionar escrituras offline con cola persistente (IndexedDB), idempotencia (`idempotency-keys`) y resolución de conflictos definida; **MUST NOT** asumir orden ni entrega única.
- **MUST** exigir HTTPS (los service workers solo operan en contextos seguros) y mantener la CSP (`security-frontend`).
- **SHOULD** cifrar o minimizar datos sensibles en el dispositivo; el almacenamiento del navegador es accesible a scripts del mismo origen.
- **SHOULD** declarar un manifiesto web válido y probar instalación en los navegadores objetivo; el soporte varía por plataforma (comprobar al fijar la versión).

## realtime

- **MUST** elegir SSE si el flujo es solo servidor -> cliente (reconexión automática y `Last-Event-ID` integrados); WebSocket solo si hay mensajería bidireccional de baja latencia.
- **MUST** autenticar con la sesión por cookie HttpOnly (patrón BFF, `auth-and-session`) o con un ticket de un solo uso y vida corta; el navegador no permite cabeceras personalizadas en `EventSource` ni en `new WebSocket`.
- **MUST NOT** poner tokens de larga vida en la URL (acaban en logs y proxies); **MUST** validar `Origin` en el servidor WebSocket.
- **MUST** reconectar con backoff exponencial y jitter, reanudar desde el último evento (id) y tolerar duplicados (`idempotency-and-deduplication`).
- **MUST** tratar los mensajes como invalidaciones o deltas sobre la caché de servidor: `queryClient.invalidateQueries` o `setQueryData`, no un segundo almacén de estado paralelo.
- **MUST** cerrar la conexión al desmontar, al cerrar sesión y en pestañas ocultas si no es necesaria; una sola conexión compartida por app, no una por componente.
- **MUST** validar el esquema de cada mensaje (Zod) antes de usarlo; ignorar tipos desconocidos (compatibilidad hacia delante).
- **SHOULD** usar latidos (heartbeat) menores que el timeout de inactividad de balanceadores y proxies (en ALB el valor por defecto es 60 s; comprobar al fijar la versión) y comprobar el comportamiento del CDN con respuestas en streaming.
- **SHOULD** tener degradación: si falla el canal, volver a polling y mostrar estado "sin conexión".
- Sobre HTTP/1.1 los navegadores limitan conexiones por dominio (alrededor de 6); con HTTP/2 se relaja (comprobar al fijar la versión).

## rendering-strategy-decision

- **MUST** partir de SPA con Vite (ADR-0036, aceptado por defecto y revisable por el dueño).
- **MUST** documentar en un ADR del proyecto cualquier salida del defecto, con el requisito que la fuerza.
- **MAY** elegir SSR/Next.js solo con requisito medible: SEO de contenido público indexable, previsualizaciones sociales por URL, o LCP inicial que la SPA no alcanza tras optimizar (`frontend-performance`).
- **MUST NOT** elegir SSR por moda ni "por si acaso".
- **MUST** que las apps tras login (backoffice, paneles) sean SPA: el SEO no aporta.
- **SHOULD** si hay páginas públicas aisladas, valorar prerender estático de esas rutas antes que SSR global.
- **MUST** declarar el coste operativo de SSR (servidor Node en ejecución, caché, observabilidad) en el ADR.
- **MUST** mantener el contrato API independiente del renderizado (`openapi-contract-first`).

## routing-and-code-splitting

- **MUST** definir el router en `src/app` y que cada ruta importe su página desde la API pública de una feature.
- **MUST** cargar páginas con `React.lazy` + `Suspense` (o el `lazy` del router) por ruta; el shell y la primera ruta quedan en el bundle inicial.
- **MUST NOT** hacer `lazy` de componentes diminutos: el coste de la petición supera el ahorro.
- **MUST** tener una ruta comodín (404) y un `errorElement` por layout (`error-handling-and-boundaries`).
- **MUST** tratar los guards de ruta como UX, no seguridad: la autorización real vive en el backend (`auth-and-session`).
- **SHOULD** usar rutas anidadas con layouts compartidos y `<Outlet />`.
- **SHOULD** precargar (prefetch) la ruta probable al hacer hover/foco en el enlace.
- **SHOULD** vigilar el tamaño de chunks con el presupuesto definido en `frontend-performance`.
- **MUST** que los parámetros de ruta se validen (son `string | undefined`).

## security-frontend

- **MUST NOT** usar `dangerouslySetInnerHTML`, `innerHTML` ni `eval`/`new Function` con datos no confiables; si es inevitable, sanear con una librería de sanitización mantenida (p. ej. DOMPurify,) y revisión explícita.
- **MUST NOT** construir URLs desde entrada de usuario sin validar el esquema (`javascript:`); permitir solo `https:`/`mailto:` en enlaces dinámicos.
- **MUST** publicar una CSP estricta basada en nonce o hash, `object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'` (salvo necesidad), sin `unsafe-inline` ni `unsafe-eval` (MDN CSP, 2026-11-07).
- **MUST** desplegar la CSP primero en `Content-Security-Policy-Report-Only` con endpoint de informes y pasar a enforce tras revisar.
- **SHOULD** activar Trusted Types (`require-trusted-types-for 'script'`) en proyectos nuevos.
- **MUST NOT** guardar tokens ni PII en `localStorage`/`sessionStorage`; ver `auth-and-session`.
- **MUST** añadir `rel="noopener noreferrer"` a enlaces `target="_blank"` externos y `sandbox` a iframes de terceros.
- **SHOULD** usar Subresource Integrity en scripts/estilos de CDN externos; **SHOULD** minimizar scripts de terceros.
- **MUST NOT** incluir secretos en variables `VITE_*`/`NEXT_PUBLIC_*`: todo lo del bundle es público.

## state-management

- **MUST** clasificar cada dato antes de elegir herramienta: server-state, URL-state, form-state, client-state global o local.
- **MUST** gestionar server-state con TanStack Query (caché, invalidación, reintentos), no copiarlo a Redux/Zustand.
- **MUST** poner en la URL (query params, path) lo que debe ser enlazable/recargable: filtros, página, orden, pestaña.
- **MUST** dejar el form-state a React Hook Form (`forms-and-validation`).
- **SHOULD** usar Zustand o Redux Toolkit solo para estado de cliente verdaderamente global (UI shell, preferencias, wizard multipaso); elegir uno por proyecto.
- **MUST** definir claves de query en una factoría por feature, y invalidar tras mutaciones.
- **MUST NOT** guardar tokens o datos sensibles en el store persistido (`auth-and-session`).
- **MUST NOT** sincronizar con `useEffect` un estado derivable: calcularlo durante el render.
- **SHOULD** usar selectores en el store para evitar renders innecesarios.

## supply-chain-npm

- **MUST** versionar el lockfile y usar instalación reproducible en CI (`pnpm install --frozen-lockfile`; con npm, `npm ci`).
- **MUST** desactivar la ejecución de scripts de ciclo de vida de dependencias por defecto y permitir solo una lista explícita (pnpm: `onlyBuiltDependencies`; comprobar comportamiento por defecto en la versión usada).
- **MUST** instalar desde el registro privado/proxy de la organización con scope propio reservado, para evitar confusión de dependencias (`remote-repos-and-dependency-confusion-protection`, `private-registry`).
- **MUST** revisar cada dependencia nueva: mantenimiento, licencia, tamaño, dependencias transitivas, nombre exacto (typosquatting) y si hay alternativa nativa.
- **MUST** ejecutar auditoría (`pnpm audit`) y SCA en CI con SLA de corrección (`vulnerability-sla-and-incident-response`); **MUST** generar SBOM CycloneDX del build (`sbom-generation`).
- **MUST NOT** usar rangos abiertos (`*`, `latest`) ni dependencias desde URL/git sin commit fijo; **MUST NOT** hacer `curl | sh` en el build.
- **SHOULD** aplicar un periodo de espera para versiones recién publicadas (pnpm `minimumReleaseAge`, disponible desde pnpm 10.16 y activado por defecto con 1 día en pnpm 11; verificado el 2026-11-08 en pnpm.io) y actualizar con Renovate/Dependabot según `renovate-dependabot-policy`.
- **SHOULD** verificar firmas/procedencia cuando el registro las ofrezca (`npm audit signatures`; comprobar alcance con pnpm).
- **SHOULD** separar `dependencies` de `devDependencies` y mantener el árbol pequeño.

## testing

- **MUST** testear comportamiento visible para el usuario con Testing Library: consultas por rol/label (`getByRole`, `getByLabelText`), nunca por clase CSS ni estructura interna.
- **MUST** simular la red con MSW a nivel de petición (handlers por escenario), no mockeando `fetch` ni el cliente generado; los handlers se tipan con el contrato OpenAPI (`api-client-from-openapi`).
- **MUST** usar `userEvent` (no `fireEvent`) para interacciones, y `findBy*`/`waitFor` en lugar de `setTimeout`/sleeps.
- **MUST** tener pocos E2E con Playwright para flujos críticos (login, alta, pago), contra backend simulado o entorno efímero; cada test es independiente y crea sus datos.
- **MUST** que el CI falle ante tests rojos, snapshots obsoletos y violaciones axe (ver `accessibility`).
- **MUST NOT** usar snapshots de DOM grandes como test principal; **MUST NOT** testear detalles de implementación (estado interno, llamadas a hooks).
- **SHOULD** usar regresión visual (capturas de Playwright o Storybook) solo en componentes del design system, con entorno de render fijo.
- **SHOULD** mantener la pirámide: muchos tests de componente/hook, algunos de integración con MSW, pocos E2E.
- **SHOULD** tratar tests inestables con `flaky-test-management`, no con reintentos ciegos.

## typescript-strict-rules

- **MUST** activar `"strict": true` desde el primer commit; nunca "migrar a strict después".
- **SHOULD** añadir `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride` y `verbatimModuleSyntax` (comprobar disponibilidad según versión de TypeScript).
- **MUST NOT** usar `any`; para datos desconocidos usar `unknown` y estrechar.
- **MUST NOT** usar `!` (non-null) ni `as` para silenciar el compilador; `@ts-expect-error` solo con descripción.
- **MUST** tratar todo dato externo (respuesta HTTP, `localStorage`, `URLSearchParams`, `postMessage`) como `unknown` y validarlo (Zod u otro esquema) en el borde.
- **SHOULD** modelar estados con uniones discriminadas, no con varios booleanos.
- **SHOULD** tipar con `satisfies` configuraciones literales para mantener la inferencia.
- **MUST** que `tsc --noEmit` y ESLint pasen en CI.
