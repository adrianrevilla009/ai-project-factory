---
name: routing-and-code-splitting
description: "Usar al definir rutas en React Router, guards de navegación y carga diferida (lazy) de rutas para dividir el bundle."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Rutas y code splitting

## Cuándo aplicar y cuándo no
- Aplica a la definición del router, layouts, rutas protegidas y división del bundle por ruta.
- No aplica a optimización fina de imágenes o fuentes (ver `frontend-performance`).

## Reglas
- **MUST** definir el router en `src/app` y que cada ruta importe su página desde la API pública de una feature.
- **MUST** cargar páginas con `React.lazy` + `Suspense` (o el `lazy` del router) por ruta; el shell y la primera ruta quedan en el bundle inicial.
- **MUST NOT** hacer `lazy` de componentes diminutos: el coste de la petición supera el ahorro.
- **MUST** tener una ruta comodín (404) y un `errorElement` por layout (`error-handling-and-boundaries`).
- **MUST** tratar los guards de ruta como UX, no seguridad: la autorización real vive en el backend (`auth-and-session`).
- **SHOULD** usar rutas anidadas con layouts compartidos y `<Outlet />`.
- **SHOULD** precargar (prefetch) la ruta probable al hacer hover/foco en el enlace.
- **SHOULD** vigilar el tamaño de chunks con el presupuesto definido en `frontend-performance`.
- **MUST** que los parámetros de ruta se validen (son `string | undefined`).

## Por qué
Sin división, el usuario descarga todo el código en la primera visita. Dividir por ruta es el corte natural: coincide con la navegación y con los límites de feature. Los guards del cliente se saltan con las DevTools; solo informan a la UI. Verificar la API exacta de la versión de React Router (data routers, `lazy`) — TODO-VERIFY.

## Ejemplos
### Mal
```tsx
import { OrdersPage } from '@/features/orders';
import { ReportsPage } from '@/features/reports';   // todo en el bundle inicial
<Route path="/admin" element={user.isAdmin ? <AdminPage /> : null} />  // "seguridad" solo en UI
```
### Bien
```tsx
const OrdersPage = lazy(() => import('@/features/orders/pages/orders-page'));

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    errorElement: <RouteError />,
    children: [
      { path: 'orders', element: <Suspense fallback={<PageSkeleton />}><OrdersPage /></Suspense> },
      { path: '*', element: <NotFound /> },
    ],
  },
]);
```
Nota: el `import()` dinámico apunta a un fichero por defecto de la página; ese módulo es el único acceso permitido fuera del `index.ts` y debe documentarse como excepción en la config de límites.

## Checklist de revisión
- [ ] Cada ruta de página es lazy; el bundle inicial solo trae el shell.
- [ ] Hay 404 y `errorElement`.
- [ ] Los guards no sustituyen a la autorización del backend.
- [ ] Parámetros de ruta validados.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Presupuesto de bundle en CI (ver skill de rendimiento) | 1 | pendiente (lo define el proyecto generado) |
| Revisión del árbol de rutas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `frontend-architecture`, `frontend-performance`, `auth-and-session`, `error-handling-and-boundaries`.
- Fuentes: documentación de React (`lazy`, `Suspense`) y React Router (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
