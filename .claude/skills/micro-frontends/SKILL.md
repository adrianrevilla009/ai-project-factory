---
name: micro-frontends
description: "Usar solo si se plantea dividir el frontend en micro-frontends (Module Federation u otros): cuándo no hacerlo, contratos, dependencias compartidas y gobierno."
metadata:
  block: "27-frontend-react"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Micro-frontends (T3: evaluar con escepticismo)

## Cuándo aplicar y cuándo no
- Aplica cuando varios equipos autónomos despliegan partes de una misma UI a ritmos distintos y el monolito de frontend ya es un cuello de botella demostrado.
- No aplica por defecto: un equipo o una app pequeña se sirve mejor con arquitectura por feature y fronteras de módulo (`architecture`, `modular-monolith` como analogía). Decisión como ADR (`adr`).

## Reglas
- **MUST** documentar en un ADR el problema organizativo que resuelve, alternativas (monorepo con límites por feature, librerías internas) y coste asumido.
- **MUST** definir contratos explícitos entre host y remotos: rutas, eventos/props versionados, tipos compartidos publicados; sin acceso a estado interno ajeno.
- **MUST** compartir como singleton solo lo imprescindible (React, router) con rangos de versión acordados; una divergencia de React entre remotos rompe hooks.
- **MUST** unificar sesión, design system y tokens (`design-system-and-tokens`) y una sola política CSP/seguridad (`security-frontend`); cada remoto con aislamiento de estilos.
- **MUST** que el host degrade con elegancia si un remoto no carga (error boundary + fallback) y que haya observabilidad por remoto (`observability-frontend`).
- **MUST NOT** comunicar remotos mediante estado global mutable ni variables en `window`; usar eventos tipados o props.
- **SHOULD** versionar y desplegar remotos de forma inmutable con rollback independiente (`build-and-deploy`) y probar contratos en CI (`contract-testing`).
- **SHOULD** medir el coste: bytes duplicados, tiempo de carga extra y esfuerzo de coordinación (`frontend-performance`).

## Por qué
Los micro-frontends trasladan complejidad organizativa al runtime: más red, versiones divergentes, UX incoherente y depuración distribuida. Compensan solo cuando la autonomía de despliegue vale más que ese coste.

## Ejemplos
### Mal
```ts
// remoto A lee estado de remoto B
const user = (window as any).__appState.user;
```
### Bien
```ts
// host: carga perezosa con fallback
const Billing = lazy(() => import("billing/Routes"));
<ErrorBoundary fallback={<BillingUnavailable />}>
  <Suspense fallback={<Spinner />}><Billing /></Suspense>
</ErrorBoundary>
```
```ts
// contrato de evento versionado
type CartChangedV1 = { type: "cart.changed.v1"; items: number };
window.dispatchEvent(new CustomEvent<CartChangedV1>("cart.changed.v1", { detail: { type: "cart.changed.v1", items: 3 } }));
```

## Criterios de decisión y trampas
### Cómo decidir
- Solo para un problema de organización (equipos que despliegan de forma independiente), no técnico; un monorepo con límites suele bastar.
- Contratos explícitos y versionados entre la aplicación anfitriona y los módulos remotos.
- Comparte lo imprescindible (framework, router) como singleton con rangos de versión acordados.
### Trampas frecuentes
- Adoptarlos por moda con un solo equipo.
- Cada módulo con un framework y un sistema de diseño distintos.
- Duplicar dependencias grandes y engordar la carga.
- Sin sesión ni política de seguridad unificadas.
- Pruebas E2E que no cubren la integración entre módulos.
### Evidencia
- Un ADR que justifica el coste y una prueba de integración del conjunto en CI.

## Checklist de revisión
- [ ] ADR con el problema y alternativas descartadas.
- [ ] Contratos versionados y probados.
- [ ] Dependencias singleton y versiones acordadas.
- [ ] Fallback por remoto, observabilidad y rollback independientes.
- [ ] Coste en rendimiento medido.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de arquitectura / ADR | 3 | revisión humana |
| Fronteras entre módulos (dependency-cruiser) como alternativa | 1 | `policies/frontend-boundaries/dependency-cruiser.example.cjs` |
| Pruebas de contrato host-remoto | 2 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `architecture`, `adr`, `design-system-and-tokens`, `build-and-deploy`, `contract-testing`.
- Fuentes: documentación de Module Federation y de la herramienta de build elegida.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T3
