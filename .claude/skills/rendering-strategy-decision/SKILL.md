---
name: rendering-strategy-decision
description: "Usar al decidir cómo renderiza una app React: SPA con Vite (defecto, ADR-0036) frente a SSR/Next.js, y qué evidencia justifica cambiar."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Decisión de estrategia de renderizado

## Cuándo aplicar y cuándo no
- Aplica al arrancar un frontend nuevo o cuando alguien propone migrar a SSR/Next.js.
- No aplica a la elección de librerías dentro de la SPA (ver `state-management`, `routing-and-code-splitting`).

## Reglas
- **MUST** partir de SPA con Vite (ADR-0036, aceptado por defecto y revisable por el dueño).
- **MUST** documentar en un ADR del proyecto cualquier salida del defecto, con el requisito que la fuerza.
- **MAY** elegir SSR/Next.js solo con requisito medible: SEO de contenido público indexable, previsualizaciones sociales por URL, o LCP inicial que la SPA no alcanza tras optimizar (`frontend-performance`).
- **MUST NOT** elegir SSR por moda ni "por si acaso".
- **MUST** que las apps tras login (backoffice, paneles) sean SPA: el SEO no aporta.
- **SHOULD** si hay páginas públicas aisladas, valorar prerender estático de esas rutas antes que SSR global.
- **MUST** declarar el coste operativo de SSR (servidor Node en ejecución, caché, observabilidad) en el ADR.
- **MUST** mantener el contrato API independiente del renderizado (`openapi-contract-first`).

## Por qué
La SPA se sirve como estáticos (S3+CloudFront previsto, preparado para AWS, no verificado en real; en local, cualquier servidor estático) y no necesita runtime de servidor. SSR añade un proceso a operar, hidratación y fronteras servidor/cliente. Compensa solo si el requisito lo exige. Matriz AWS↔local: en local no se reproduce CloudFront ni su caché de borde.

## Ejemplos
### Mal
```text
ADR: "Usamos Next.js porque es lo estándar." (sin requisito de SEO, app tras login)
```
### Bien
```text
ADR-P-012: SPA/Vite para el backoffice (tras OIDC, sin SEO).
ADR-P-013: sitio de catálogo público -> Next.js; requisito: indexación y OG tags por producto;
coste asumido: contenedor Node, caché, métricas; revisar a los 6 meses.
```
Árbol rápido: ¿contenido público que debe indexarse o compartirse con metadatos por URL? No -> SPA. Sí -> ¿basta prerender estático? Sí -> SPA + prerender. No -> SSR.

## Criterios de decisión y trampas
### Cómo decidir
- Parte de SPA con Vite (ADR-0036). SSR solo con un requisito medible: contenido público que debe indexarse, previsualizaciones sociales o primera carga crítica en redes lentas.
- Para una aplicación detrás de login, SSR casi nunca compensa su complejidad operativa.
- Si solo unas pocas páginas públicas necesitan SEO, considera generarlas de forma estática en lugar de renderizar toda la app en servidor.
### Trampas frecuentes
- Elegir SSR por moda o «por si acaso».
- Mezclar SSR con estado global sin cuidar la hidratación (discrepancias entre servidor y cliente).
- Olvidar que SSR añade un servidor que operar, escalar y monitorizar.
- Decidir sin medir la primera carga con datos reales.
### Evidencia
- Un ADR que nombra el requisito concreto (métrica o SEO) que justifica salir del defecto.

## Checklist de revisión
- [ ] La decisión está en un ADR con requisito medible.
- [ ] Las apps autenticadas internas son SPA.
- [ ] Se declaró el coste operativo si hay SSR.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión humana del ADR de renderizado (decisión del dueño, ADR-0036) | 4 | `catalog/adr/0036-react-por-defecto-spa-vite-vs-ssr-next-js.md` |

No hay mecanismo automático: es una decisión de arquitectura.

## Relacionados, fuentes y mantenimiento
- Relacionados: `frontend-architecture`, `frontend-performance`, `security-frontend`, `bff-and-api-gateway`.
- Fuentes: ADR-0036; documentación de Vite y Next.js (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
