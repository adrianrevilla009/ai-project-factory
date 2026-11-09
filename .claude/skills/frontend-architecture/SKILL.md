---
name: frontend-architecture
description: "Usar al estructurar un proyecto React: carpetas por feature, límites entre módulos, API pública de cada feature y dirección de dependencias."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Arquitectura del frontend: por feature y con límites

## Cuándo aplicar y cuándo no
- Aplica a toda SPA React generada (ADR-0036: SPA/Vite por defecto) con más de una pantalla.
- No aplica a prototipos desechables de una sola vista ni a librerías de componentes publicadas (ver `design-system-and-tokens`).

## Reglas
- **MUST** organizar `src/` en tres capas: `src/app` (arranque, router, providers), `src/features/<name>` (casos de uso) y `src/shared` (UI genérica, utilidades, cliente API).
- **MUST** respetar la dirección `app -> features -> shared`; nunca al revés.
- **MUST NOT** importar de una feature a otra; la composición ocurre en `src/app` o en una página.
- **MUST** exponer cada feature solo por su `index.ts`; el resto es interno.
- **MUST NOT** crear carpetas globales por tipo (`components/`, `hooks/`, `utils/` con todo mezclado).
- **SHOULD** dentro de una feature: `api/`, `components/`, `hooks/`, `types.ts`, tests junto al código.
- **SHOULD** subir a `shared` solo tras el segundo uso real (no anticipar).
- **MUST NOT** ciclos de importación.

## Por qué
La estructura por tipo escala mal: tocar un caso de uso obliga a editar cinco carpetas. Por feature, el cambio queda localizado, se puede borrar una feature entera y los límites se comprueban con herramientas, no con memoria. Ver también `connascence-and-coupling` para el razonamiento general.

## Ejemplos
### Mal
```text
src/components/OrderTable.tsx
src/components/InvoiceTable.tsx
src/hooks/useOrders.ts
src/utils/helpers.ts
```
```ts
// features/orders/OrderPage.tsx
import { InvoiceList } from '../invoices/components/InvoiceList'; // cruce entre features
```
### Bien
```text
src/app/{main.tsx,router.tsx,providers.tsx}
src/features/orders/{index.ts,api/,components/,hooks/}
src/features/invoices/{index.ts,...}
src/shared/{ui/,lib/,api/}
```
```ts
// src/app/routes/customer-page.tsx (compone ambas features)
import { OrderList } from '@/features/orders';
import { InvoiceList } from '@/features/invoices';
```

## Criterios de decisión y trampas
### Cómo decidir
- Organiza por funcionalidad (feature), no por tipo de fichero: añadir una funcionalidad toca una carpeta, no ocho.
- Si dos features comparten algo, súbelo a `shared` solo cuando haya un segundo uso real; duplicar dos veces es más barato que una abstracción prematura.
- Cuando la aplicación crece, el límite entre features se hace cumplir con reglas de dependencias, no con convenciones.
### Trampas frecuentes
- Una carpeta `utils` o `common` que acaba conteniendo todo.
- Importaciones entre features por rutas internas.
- Un `shared` que depende de una feature (inversión de la dirección).
- Carpetas por tipo (`components`, `hooks`, `services`) que dispersan una misma funcionalidad.
- Barriles de reexportación que rompen la carga diferida y crean ciclos.
### Evidencia
- Reglas de límites ejecutadas en CI (dependency-cruiser o ESLint) y cero ciclos.

## Checklist de revisión
- [ ] Ninguna feature importa de otra ni de `app`.
- [ ] `shared` no importa de `features` ni `app`.
- [ ] Cada feature tiene `index.ts` y nadie importa sus rutas internas.
- [ ] Sin ciclos; sin carpetas globales por tipo.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| dependency-cruiser: capas, cruce entre features, ciclos | 1 | `policies/frontend-boundaries/dependency-cruiser.example.cjs` |
| ESLint `no-restricted-imports` (solo API pública) | 1 | `policies/frontend-boundaries/eslint.boundaries.example.mjs` |
| Revisión de diseño de nuevas features | 3 | agente `code-reviewer` |

Son ejemplos para copiar al proyecto generado; la fábrica no los ejecuta. Versiones de las herramientas: comprobar al fijar la versión.

## Relacionados, fuentes y mantenimiento
- Relacionados: `typescript-strict-rules`, `component-patterns`, `state-management`, `routing-and-code-splitting`, `connascence-and-coupling`.
- Fuentes: ADR-0036; documentación de dependency-cruiser y ESLint `no-restricted-imports` (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
