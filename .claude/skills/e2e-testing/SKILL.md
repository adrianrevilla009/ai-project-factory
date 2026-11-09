---
name: e2e-testing
description: "Usar al diseñar o escribir tests end-to-end de flujos críticos (UI y API encadenada) y decidir qué NO debe cubrirse a ese nivel."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Tests end-to-end

## Cuándo aplicar y cuándo no
- Aplica a un conjunto pequeño de recorridos críticos de negocio (alta, login, compra, pago) que atraviesan varios componentes.
- No aplica a validar reglas de negocio de detalle, casos límite o combinaciones: eso va en unit/integración (pirámide, ver `test-strategy`).

## Reglas
- **MUST** limitar la suite e2e a flujos críticos (orientativo: decenas, no cientos) y mantener cada test independiente.
- **MUST** ejecutar contra un entorno efímero y reproducible (Kubernetes local con kind, ADR-0005), con datos creados por el propio test.
- **MUST** usar selectores estables (`data-testid` o roles accesibles), no XPath frágil ni textos que cambian.
- **MUST** esperar condiciones (auto-wait del framework o Awaitility), nunca sleeps fijos.
- **MUST NOT** depender de servicios de terceros reales; sustituirlos por dobles (WireMock).
- **MUST NOT** compartir estado ni orden entre tests e2e.
- **MUST** guardar artefactos al fallar (captura, traza, vídeo, logs de servicios).
- **SHOULD** probar la API directamente cuando el flujo no necesita UI, y reservar la UI para lo que solo la UI puede romper.
- **SHOULD** aplicar `flaky-test-management` a cualquier test e2e inestable: se arregla o se elimina, no se reintenta a ciegas.
- **SHOULD** el frontend usar Playwright o Cypress según decisión del proyecto (comprobar versión y elección en la capa frontend).

## Por qué
Los e2e son lentos, caros y frágiles, pero son los únicos que detectan fallos de integración entre capas reales. Una suite pequeña y estable da confianza; una grande e inestable se ignora.

## Ejemplos
### Mal
```typescript
await page.click('//div[3]/div/button[2]');
await page.waitForTimeout(5000);
expect(await page.textContent('.msg')).toBe('Hecho');
```
### Bien
```typescript
test('customer places an order', async ({ page, request }) => {
  const customer = await request.post('/api/test-support/customers', { data: { name: 'Test Customer' } });
  await page.goto('/orders/new');
  await page.getByTestId('product-select').selectOption('SKU-example-1');
  await page.getByRole('button', { name: 'Confirm order' }).click();
  await expect(page.getByTestId('order-status')).toHaveText('CONFIRMED');
});
```
El endpoint `test-support` solo existe en el perfil de test, nunca en producción.

## Criterios de decisión y trampas
### Cómo decidir
- ¿E2E de UI o de API? De API para flujos de negocio encadenados; de UI solo para los recorridos críticos del usuario.
- Entorno efímero en Kubernetes local (kind, ADR-0005) con datos propios; selectores por rol o `data-testid`.
### Trampas frecuentes
- Suites con cientos de tests que repiten lo que cubren las capas bajas.
- Depender de servicios de terceros reales.
- Datos compartidos entre tests.
- `sleep` fijos en lugar de esperas por condición.
- No guardar traza ni vídeo cuando falla.
- Tolerar fallos intermitentes.
### Evidencia
- Una lista de los flujos críticos con el test E2E que cubre cada uno.

## Checklist de revisión
- [ ] El flujo es crítico y no es cubrible a nivel inferior.
- [ ] Datos propios, sin orden entre tests, sin terceros reales.
- [ ] Selectores estables y esperas por condición.
- [ ] Artefactos de fallo guardados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión del alcance de la suite e2e | 3 | agente `qa-engineer` (`.claude/agents/quality/qa-engineer.md`) |
| Lint de selectores y sleeps en tests frontend | 1 | pendiente (`policies/frontend-boundaries/`) |
| Regla Semgrep: `Thread.sleep` en tests Java | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `test-strategy`, `api-testing`, `flaky-test-management`, `test-data-management`, `wiremock-and-stubbing`.
- Fuentes: práctica de la pirámide de tests (Fowler, https://martinfowler.com/articles/practical-test-pyramid.html; Playwright (https://playwright.dev/docs/best-practices (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
