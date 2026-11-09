---
name: frontend-performance
description: "Usar al optimizar o revisar rendimiento de la SPA React: Core Web Vitals, presupuestos de bundle, imágenes, renders y medición."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Rendimiento del frontend (Core Web Vitals y bundle)

## Cuándo aplicar y cuándo no
- Aplica a pantallas nuevas, dependencias nuevas, cambios de build y revisiones de rendimiento percibido.
- No aplica al rendimiento del backend (`performance-testing`, `performance-gate`). Para el reparto de rutas, ver `routing-and-code-splitting`.

## Reglas
- **MUST** definir objetivos en el percentil 75 por móvil y escritorio: LCP <= 2,5 s, INP <= 200 ms, CLS <= 0,1 (https://web.dev/articles/vitals, consultado 2026-11-07).
- **MUST** fijar un presupuesto de bundle (JS inicial gzip/brotli por ruta) y hacer fallar el CI si se supera; el valor numérico lo decide el proyecto (comprobar con datos reales).
- **MUST** medir con datos de campo (RUM, ver `observability-frontend`) además de laboratorio (Lighthouse).
- **MUST** reservar espacio para imágenes y medios (`width`/`height` o `aspect-ratio`) para evitar CLS; **SHOULD** usar `loading="lazy"` salvo en la imagen LCP.
- **MUST NOT** importar librerías enteras para una función (usar imports por módulo o alternativas ligeras); revisar el análisis de bundle ante cada dependencia nueva.
- **SHOULD** virtualizar listas largas y mover trabajo pesado a Web Workers o `startTransition`/`useDeferredValue` para proteger INP.
- **SHOULD** medir antes de memoizar: `React.memo`/`useMemo` solo con evidencia del profiler.
- **SHOULD** servir assets con hash y `Cache-Control: immutable` (ver `build-and-deploy`) y fuentes con `font-display: swap`.

## Por qué
CWV mide experiencia real; un presupuesto automático evita la erosión lenta (cada dependencia "pequeña" suma). Memoizar sin medir añade complejidad y a veces coste. Los umbrales pueden cambiar: re-verificar en cada revisión.

## Ejemplos
### Mal
```ts
import _ from "lodash";          // todo lodash en el bundle inicial
import { Chart } from "heavy-charts";
```
```tsx
<img src={hero} />                // sin dimensiones: CLS
```
### Bien
```ts
import debounce from "lodash-es/debounce";
const Chart = lazy(() => import("./Chart")); // solo en la ruta que lo usa
```
```tsx
<img src={hero} width={1200} height={600} fetchpriority="high" alt="" />
```
### Presupuesto en CI (ejemplo, comando del proyecto)
```text
pnpm build && pnpm exec size-limit   # size-limit: comprobar herramienta elegida
```

## Criterios de decisión y trampas
### Cómo decidir
- Mide con datos de campo (usuarios reales) y de laboratorio; el laboratorio guía, el campo decide.
- Lo más barato primero: menos JavaScript, imágenes bien dimensionadas, caché correcta; después, optimizaciones de render.
- Presupuesto de rendimiento por ruta, con CI que falla al superarlo.
### Trampas frecuentes
- Optimizar sin medir.
- Memoizar por defecto.
- Cargar bibliotecas enteras por una función.
- Imágenes sin dimensiones (saltos de diseño).
- Medir solo en una máquina potente y una red rápida.
### Evidencia
- Un tablero de métricas de campo con el percentil 75 de LCP, INP y CLS por ruta.

## Checklist de revisión
- [ ] El bundle inicial por ruta está dentro del presupuesto.
- [ ] Imágenes con dimensiones; la imagen LCP no es lazy.
- [ ] Las dependencias nuevas se justifican con su coste en KB.
- [ ] Sin memoización especulativa; hay perfil que la respalda.
- [ ] Hay métricas RUM de LCP/INP/CLS en producción.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Presupuesto de bundle en CI | 1 | pipeline del proyecto generado (pendiente) |
| Lighthouse CI con aserciones | 2 | pipeline del proyecto generado (pendiente) |
| Revisión de dependencias y renders | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `routing-and-code-splitting`, `observability-frontend`, `build-and-deploy`, `rendering-strategy-decision`.
- Fuentes: https://web.dev/articles/vitals (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
