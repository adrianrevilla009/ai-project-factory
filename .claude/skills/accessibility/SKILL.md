---
name: accessibility
description: "Usar al construir o revisar componentes, formularios y flujos React para cumplir WCAG 2.2 AA: semántica, teclado, foco, contraste y pruebas con axe."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Accesibilidad (WCAG 2.2 AA)

## Cuándo aplicar y cuándo no
- Aplica a cualquier UI nueva o modificada: componentes del design system, formularios, modales, tablas, navegación y mensajes de error.
- No aplica a APIs ni a herramientas internas sin interfaz. Obligaciones legales concretas (p. ej. normativa europea de accesibilidad): borrador por confirmar con fuente oficial.

## Reglas
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

## Por qué
La accesibilidad barata es la que nace en el HTML semántico; añadirla al final obliga a reescribir componentes. Las pruebas automáticas detectan fallos mecánicos (etiquetas ausentes, contraste), no la usabilidad real.

## Ejemplos
### Mal
```tsx
<div className="btn" onClick={save}>Guardar</div>
<input placeholder="Email" />
```
### Bien
```tsx
<button type="button" onClick={save}>Guardar</button>
<label htmlFor="email">Email</label>
<input id="email" type="email" aria-describedby="email-err" aria-invalid={!!error} />
{error && <p id="email-err" role="alert">{error}</p>}
```
### Prueba axe en Vitest
```tsx
import { axe } from "vitest-axe";
it("form has no a11y violations", async () => {
  const { container } = render(<LoginForm />);
  expect(await axe(container)).toHaveNoViolations();
});
```

## Criterios de decisión y trampas
### Cómo decidir
- Elemento nativo primero: `button`, `a`, `label`, `table`; ARIA solo para lo que el HTML no cubre.
- El foco se gestiona en cada cambio de vista, diálogo o error; no se deja a la suerte.
- Prueba con teclado y con un lector de pantalla además de las herramientas automáticas.
### Trampas frecuentes
- `div` con `onClick` en vez de un botón.
- Quitar el contorno del foco sin sustituirlo.
- Información solo por color.
- `aria-label` que contradice el texto visible.
- Creer que pasar una herramienta automática equivale a ser accesible (solo detectan una parte de los problemas).
### Evidencia
- Una pasada con teclado y lector de pantalla por cada flujo crítico, y pruebas automáticas en CI.

## Checklist de revisión
- [ ] Todo se puede usar solo con teclado y el foco es visible.
- [ ] Controles nativos o primitivas accesibles; sin `div` clicable.
- [ ] Campos con label, errores enlazados y anunciados.
- [ ] Contraste AA y objetivos de 24x24 px.
- [ ] axe sin violaciones en tests; revisión manual de flujos críticos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `div`/`span` con `onClick` | 1 | `policies/semgrep/frontend-clickable-div.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| `eslint-plugin-jsx-a11y` en el lint del proyecto | 1 | configuración del proyecto generado (pendiente) |
| axe en Vitest y Playwright | 2 | tests del proyecto generado (pendiente) |
| Revisión manual con teclado/lector de pantalla | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `design-system-and-tokens`, `forms-and-validation`, `testing`, `component-patterns`.
- Fuentes: W3C WCAG 2.2 https://www.w3.org/TR/WCAG22/; WAI-ARIA Authoring Practices https://www.w3.org/WAI/ARIA/apg/ ; documentación de axe-core.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
