---
name: frontend-i18n-and-formatting
description: "Usar al añadir textos, fechas, números, monedas o idiomas a la UI React: catálogos de mensajes, formato con Intl y RTL."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# i18n y formateo en el frontend React

## Cuándo aplicar y cuándo no
- Aplica a todo texto visible, fechas, números, monedas, plurales y listas en la UI.
- No aplica a logs, claves de API ni mensajes internos no visibles. La parte de negocio (idiomas soportados por tenant) está en `i18n-and-localization`; el lado Java en `strings-encoding-locale`.

## Reglas
- **MUST** externalizar todo texto visible a catálogos por idioma (clave estable, sin concatenar frases).
- **MUST** usar formato ICU MessageFormat (o equivalente de la librería elegida) para plurales y género; **MUST NOT** construir plurales con `n === 1 ? ... : ...`.
- **MUST** formatear fechas, números y monedas con `Intl.*` (`DateTimeFormat`, `NumberFormat`, `ListFormat`, `RelativeTimeFormat`) con el locale activo.
- **MUST** transmitir y almacenar fechas en ISO 8601 UTC y convertirlas solo al mostrarlas; la moneda viaja como código ISO 4217 + importe, nunca como string formateado.
- **MUST** cargar cada catálogo de idioma bajo demanda (code splitting), no todos en el bundle inicial.
- **MUST** fijar `<html lang>` y `dir` según el locale activo; **SHOULD** usar propiedades CSS lógicas (`margin-inline-start`) para soportar RTL.
- **SHOULD** tener un idioma de referencia y un test que falle si faltan claves en otros idiomas.
- **MUST NOT** incrustar HTML en traducciones; usar componentes de interpolación de la librería.

## Por qué
Las frases concatenadas y los plurales manuales funcionan en un idioma y se rompen en el siguiente (polaco o árabe tienen más de dos formas plurales). `Intl` es nativo y evita librerías de fechas pesadas. Cargar todos los idiomas penaliza el LCP de todos. Librería concreta (react-i18next, FormatJS/react-intl, Lingui): decisión por proyecto, comprobar en ADR del proyecto.

## Ejemplos
### Mal
```tsx
<p>{count} item{count !== 1 ? "s" : ""} for {price.toFixed(2)} €</p>
<span>{new Date(order.createdAt).toLocaleDateString()}</span>
```
### Bien
```tsx
const intl = useIntl();
<p>{intl.formatMessage({ id: "cart.summary" }, { count, price })}</p>
// en.json: "cart.summary": "{count, plural, one {# item} other {# items}} for {price, number, ::currency/EUR}"
<span>{intl.formatDate(order.createdAt, { dateStyle: "medium" })}</span>
```
### Catálogo bajo demanda
```ts
export async function loadMessages(locale: string) {
  return (await import(`./messages/${locale}.json`)).default;
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Claves estables y mensajes completos con marcadores; nunca concatenes frases.
- Fechas y números con `Intl` según la configuración regional; el servidor y el almacenamiento en ISO 8601 UTC.
- Pensar en i18n desde el primer componente es barato; añadirlo después, caro.
### Trampas frecuentes
- Plurales con `if (n === 1)`: otros idiomas tienen más formas.
- Traducir cadenas partidas que pierden el contexto.
- Suponer que el texto traducido mide lo mismo (alemán, finés) y romper el diseño.
- Hardcodear el formato de moneda.
- Olvidar los idiomas de derecha a izquierda.
### Evidencia
- Una pseudo-localización en CI detecta textos sin externalizar y desbordamientos.

## Checklist de revisión
- [ ] Ningún literal visible fuera de los catálogos.
- [ ] Plurales y fechas pasan por ICU/`Intl`.
- [ ] `lang` y `dir` del documento cambian con el idioma.
- [ ] El bundle inicial solo contiene el idioma activo.
- [ ] Test de paridad de claves entre idiomas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| ESLint `no-restricted-syntax` / plugin de literales JSX | 1 | `policies/frontend-boundaries/` (pendiente) |
| Test de paridad de claves de catálogos | 1 | tests del proyecto generado |
| Revisión de textos y RTL | 3 | revisión humana / agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `i18n-and-localization`, `strings-encoding-locale`, `time-and-money`, `accessibility`, `routing-and-code-splitting`.
- Fuentes: MDN `Intl` (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl) solo a nivel de existencia de API; librerías (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
