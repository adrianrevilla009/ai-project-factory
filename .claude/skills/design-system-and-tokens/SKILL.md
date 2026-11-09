---
name: design-system-and-tokens
description: "Usar al crear o mantener el sistema de diseño: tokens (color, espaciado, tipografía), componentes base documentados en Storybook y temas."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Sistema de diseño y tokens

## Cuándo aplicar y cuándo no
- Aplica a proyectos con varias pantallas o equipos que necesitan UI coherente.
- No aplica a una pantalla única o a demos; entonces basta con una librería de componentes ya hecha sin capa propia.

## Reglas
- **MUST** definir tokens semánticos (`color.text.primary`, `space.4`, `radius.md`) como variables CSS en un único lugar de `src/shared/ui/tokens`.
- **MUST NOT** usar valores literales (`#3b82f6`, `13px`) en componentes de feature; solo tokens.
- **MUST** separar tokens primitivos (paleta) de semánticos (uso); los temas (claro/oscuro) redefinen solo los semánticos.
- **MUST** que los componentes base (`Button`, `Input`, `Dialog`...) vivan en `src/shared/ui`, sin lógica de negocio ni llamadas a API.
- **SHOULD** documentar cada componente base en Storybook con sus variantes y estados (foco, deshabilitado, error).
- **SHOULD** apoyar primitivas accesibles ya probadas (p. ej. Radix UI, React Aria) antes que reimplementar diálogos o menús.
- **MUST** cumplir contraste mínimo de WCAG 2.2 en los pares de tokens (comprobar ratios) y verificarlo en Storybook.
- **MUST NOT** copiar componentes entre features: si se repite dos veces con intención común, sube a `shared/ui`.
- **SHOULD** versionar cambios de tokens con nota de migración si hay varios consumidores.

## Por qué
Los tokens convierten decisiones de diseño en datos: cambiar la marca o añadir modo oscuro es editar un fichero. Storybook sirve de catálogo vivo y de entorno de prueba aislado para estados difíciles de reproducir en la app.

## Ejemplos
### Mal
```css
.orderCard { background: #f5f5f5; color: #333; padding: 13px; border-radius: 6px; }
```
### Bien
```css
:root { --color-neutral-100: #f5f5f5; --space-3: 0.75rem; }
:root {
  --surface-subtle: var(--color-neutral-100);
  --text-primary: #1a1a1a;
}
[data-theme='dark'] { --surface-subtle: #1f1f1f; --text-primary: #f2f2f2; }

.orderCard { background: var(--surface-subtle); color: var(--text-primary); padding: var(--space-3); }
```
```tsx
// Button.stories.tsx (Storybook, formato CSF)
export default { title: 'shared/Button', component: Button };
export const Disabled = { args: { children: 'Guardar', disabled: true } };
```

## Criterios de decisión y trampas
### Cómo decidir
- Tokens primitivos (paleta) separados de semánticos (uso): los temas redefinen los semánticos y nada más.
- Construye un componente base cuando haya tres usos; antes, copia.
- Versiona el sistema de diseño y documenta cada cambio incompatible.
### Trampas frecuentes
- Valores literales (colores, píxeles) en componentes de feature.
- Componentes base con lógica de negocio.
- Variantes por props booleanas que se multiplican.
- Un tema oscuro que solo invierte colores y rompe el contraste.
- Documentación en un sitio que nadie actualiza.
### Evidencia
- Un linter que prohíbe valores literales y una revisión de contraste de los pares de tokens.

## Checklist de revisión
- [ ] Sin colores ni medidas literales en features.
- [ ] Tokens primitivos y semánticos separados; tema oscuro cubierto.
- [ ] Componentes base con historia por variante/estado.
- [ ] Contraste verificado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Stylelint (p. ej. `declaration-property-value-disallowed-list` para colores literales) | 1 | pendiente (configuración del proyecto generado; comprobar regla) |
| Addon a11y de Storybook / axe en CI | 1 | pendiente (proyecto generado) |
| Revisión visual de nuevos componentes | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `component-patterns`, `frontend-architecture`, `frontend-i18n-and-formatting`, `frontend-performance`.
- Fuentes: documentación de Storybook, WCAG 2.2 (W3C) — comprobar enlaces y versiones (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
