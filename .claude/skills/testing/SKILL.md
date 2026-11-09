---
name: testing
description: "Usar al escribir o revisar tests del frontend React: Vitest, Testing Library, MSW, Playwright, regresión visual y accesibilidad."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Testing del frontend

## Cuándo aplicar y cuándo no
- Aplica a componentes, hooks, features y flujos E2E del frontend React.
- No aplica a tests del backend (`test-strategy`, `unit-testing-java`). Para contratos con el API ver `contract-testing`; para E2E genérico ver `e2e-testing`.

## Reglas
- **MUST** testear comportamiento visible para el usuario con Testing Library: consultas por rol/label (`getByRole`, `getByLabelText`), nunca por clase CSS ni estructura interna.
- **MUST** simular la red con MSW a nivel de petición (handlers por escenario), no mockeando `fetch` ni el cliente generado; los handlers se tipan con el contrato OpenAPI (`api-client-from-openapi`).
- **MUST** usar `userEvent` (no `fireEvent`) para interacciones, y `findBy*`/`waitFor` en lugar de `setTimeout`/sleeps.
- **MUST** tener pocos E2E con Playwright para flujos críticos (login, alta, pago), contra backend simulado o entorno efímero; cada test es independiente y crea sus datos.
- **MUST** que el CI falle ante tests rojos, snapshots obsoletos y violaciones axe (ver `accessibility`).
- **MUST NOT** usar snapshots de DOM grandes como test principal; **MUST NOT** testear detalles de implementación (estado interno, llamadas a hooks).
- **SHOULD** usar regresión visual (capturas de Playwright o Storybook) solo en componentes del design system, con entorno de render fijo.
- **SHOULD** mantener la pirámide: muchos tests de componente/hook, algunos de integración con MSW, pocos E2E.
- **SHOULD** tratar tests inestables con `flaky-test-management`, no con reintentos ciegos.

## Por qué
Los tests acoplados a la implementación se rompen en cada refactor y no detectan regresiones reales. Consultar por rol además valida accesibilidad básica. MSW permite reutilizar los mismos handlers en tests, Storybook y desarrollo.

## Ejemplos
### Mal
```tsx
const { container } = render(<OrderList />);
expect(container.querySelector(".row:nth-child(2) .btn")).toBeTruthy();
global.fetch = vi.fn().mockResolvedValue({ json: () => [] });
```
### Bien
```tsx
import { http, HttpResponse } from "msw";
import { server } from "../test/server";

it("shows an error when the API fails", async () => {
  server.use(http.get("/api/orders", () => HttpResponse.json({ title: "Boom" }, { status: 500 })));
  render(<OrderList />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/no se pudo/i);
  await userEvent.click(screen.getByRole("button", { name: /reintentar/i }));
});
```
```ts
// vitest.config.ts (fragmento)
test: { environment: "jsdom", setupFiles: ["./src/test/setup.ts"], coverage: { provider: "v8" } }
```

## Criterios de decisión y trampas
### Cómo decidir
- Prueba lo que ve y hace el usuario (rol, texto, etiqueta), no el estado interno ni los nombres de clases.
- Red simulada a nivel de petición para que el cliente real se ejecute en las pruebas.
- Pocos E2E sobre flujos críticos; el resto, pruebas de componentes y de integración.
- Pruebas visuales solo para componentes del sistema de diseño.
### Trampas frecuentes
- Probar detalles de implementación (estado interno, llamadas a funciones privadas).
- Instantáneas gigantes que se aprueban sin leer.
- `fireEvent` en lugar de interacciones de usuario realistas.
- Esperas fijas.
- Mockear el módulo de red en vez de la petición.
### Evidencia
- Las consultas por rol o etiqueta pasan, y si cambia la estructura sin cambiar el comportamiento, las pruebas no se rompen.

## Checklist de revisión
- [ ] Consultas por rol/label; sin selectores CSS.
- [ ] Red simulada con MSW, handlers por escenario.
- [ ] Sin sleeps; esperas por `findBy*`.
- [ ] E2E limitados a flujos críticos y aislados.
- [ ] axe y regresión visual donde aplica.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `eslint-plugin-testing-library` y `jest-dom` en lint | 1 | configuración del proyecto generado (pendiente) |
| `vitest run` + Playwright en CI | 2 | pipeline del proyecto generado (pendiente) |
| Umbral de cobertura | 2 | ver `coverage-policy` |
| Revisión de calidad de tests | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `accessibility`, `api-client-from-openapi`, `e2e-testing`, `contract-testing`, `flaky-test-management`, `coverage-policy`.
- Fuentes: https://vitest.dev, https://testing-library.com, https://mswjs.io, https://playwright.dev.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
