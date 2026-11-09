---
name: error-handling-and-boundaries
description: "Usar al gestionar errores en React: error boundaries por zona, errores de red/Problem Details, estados de fallo en UI y reporte sin datos sensibles."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Gestión de errores y error boundaries

## Cuándo aplicar y cuándo no
- Aplica a errores de render, de carga de datos, de mutaciones y de carga lazy de chunks.
- No aplica a la validación de campos de formulario (ver `forms-and-validation`).

## Reglas
- **MUST** tener un error boundary global en `src/app` y otros por zona (layout, widget independiente) para que un fallo no tumbe toda la pantalla.
- **MUST** que cada boundary ofrezca una acción de recuperación (reintentar, volver) y no muestre trazas ni mensajes internos al usuario.
- **MUST** tratar los errores de red como estado de UI: cada consulta/mutación muestra carga, vacío y error explícitos.
- **MUST** interpretar las respuestas de error del backend como Problem Details (RFC 9457; `error-handling-problem-details`) y mostrar `title`/`detail` solo si son aptos para usuario.
- **MUST NOT** capturar y tragar errores (`catch {}` vacío); relanzar, mostrar o reportar.
- **MUST** los errores de carga de chunk lazy (despliegue nuevo) llevar a recarga controlada.
- **SHOULD** usar `react-error-boundary` (o un `errorElement` del router) en lugar de clases propias.
- **SHOULD** reportar errores a un servicio de observabilidad con identificador de correlación, sin PII ni tokens (`logging-rules`).
- **MUST NOT** esperar que un boundary capture errores de eventos, `setTimeout` o promesas; esos se gestionan donde ocurren.

## Por qué
Sin boundary, un error de render deja la página en blanco. Un boundary solo atrapa errores durante el render y el ciclo de vida de sus hijos, no los asíncronos, por eso el error de red se modela como estado. Mostrar detalles internos filtra información útil a un atacante.

## Ejemplos
### Mal
```tsx
try { await save(order); } catch (e) {}          // error tragado
<App />                                          // sin boundary: pantalla en blanco
<p>{error.stack}</p>
```
### Bien
```tsx
<ErrorBoundary
  FallbackComponent={({ resetErrorBoundary }) => (
    <div role="alert">
      <p>No se pudo cargar esta sección.</p>
      <button onClick={resetErrorBoundary}>Reintentar</button>
    </div>
  )}
  onError={(error, info) => reportError(error, info, { correlationId })}
>
  <OrdersWidget />
</ErrorBoundary>
```
```tsx
const { data, isPending, isError, error, refetch } = useOrders();
if (isPending) return <Skeleton />;
if (isError) return <ErrorState problem={toProblem(error)} onRetry={refetch} />;
if (data.length === 0) return <EmptyState />;
```

## Criterios de decisión y trampas
### Cómo decidir
- Un límite global para no dejar la pantalla en blanco y límites locales alrededor de piezas independientes.
- Distingue errores esperados (validación, 404, sin permisos) de inesperados (bugs): los primeros son parte de la interfaz.
- Todo error recuperable ofrece una acción: reintentar o volver.
### Trampas frecuentes
- Mostrar mensajes técnicos o trazas al usuario.
- Tragar el error en un `catch` vacío.
- Un solo límite en la raíz que tumba toda la página por un widget.
- Reintentos automáticos de operaciones no idempotentes.
- No registrar el error con contexto suficiente para reproducirlo.
### Evidencia
- Cada consulta y mutación tiene visibles sus estados de carga, vacío y error.

## Checklist de revisión
- [ ] Boundary global y por zona con recuperación.
- [ ] Carga/vacío/error contemplados en cada consulta.
- [ ] Problem Details interpretado; sin trazas al usuario.
- [ ] Sin `catch` vacío; reporte sin PII.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| ESLint `no-empty` (bloque catch vacío) | 1 | pendiente (configuración del proyecto generado) |
| Test de componente que simula fallo y espera el fallback | 3 | tests del proyecto generado |
| Revisión de zonas sin boundary | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `error-handling-problem-details`, `routing-and-code-splitting`, `forms-and-validation`, `logging-rules`, `security-frontend`.
- Fuentes: documentación de React (Error Boundaries), RFC 9457.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
