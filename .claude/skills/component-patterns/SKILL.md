---
name: component-patterns
description: "Usar al diseñar o revisar componentes y hooks React: composición, compound components, hooks propios, render props y cuándo memoizar."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Patrones de componentes

## Cuándo aplicar y cuándo no
- Aplica al crear componentes reutilizables, extraer lógica a hooks o revisar componentes que crecen.
- No aplica a componentes de una sola pantalla sin reutilización prevista: no abstraer antes de tiempo.

## Reglas
- **MUST** usar componentes de función con hooks; sin clases salvo error boundaries si no se usa `react-error-boundary`.
- **MUST** preferir composición (`children`, slots) a herencia y a props booleanas en cascada (`isPrimary`, `isLarge`...).
- **SHOULD** usar compound components (contexto interno) para widgets con partes coordinadas: `Tabs`, `Menu`, `Dialog`.
- **SHOULD** extraer a un hook propio (`useX`) la lógica con estado/efectos que se repite; el componente queda como vista.
- **MAY** usar render props o `children` como función cuando el padre debe controlar el renderizado de cada elemento.
- **MUST** respetar las reglas de hooks: llamadas incondicionales, solo en componentes o hooks.
- **MUST** `key` estable y única en listas (id de dominio, nunca el índice si el orden cambia).
- **MUST NOT** definir componentes dentro de otros componentes (se remontan en cada render).
- **MUST NOT** usar `useEffect` para derivar estado ni para responder a eventos; usar el handler del evento.
- **SHOULD** medir antes de memoizar (`memo`, `useMemo`, `useCallback`); ver `frontend-performance`.
- **SHOULD** que un componente tenga una sola razón de cambio y menos de ~150 líneas.

## Por qué
La composición mantiene la API de un componente pequeña y estable; las props booleanas se multiplican en combinaciones imposibles. Los efectos mal usados provocan renders en cascada y errores de sincronización difíciles de depurar. Las reglas de hooks son requisito del motor de React, no estilo.

## Ejemplos
### Mal
```tsx
function Page() {
  const Row = ({ o }: { o: Order }) => <li>{o.id}</li>;   // componente anidado
  const [total, setTotal] = useState(0);
  useEffect(() => setTotal(items.reduce((a, i) => a + i.price, 0)), [items]); // derivable
  return <ul>{items.map((o, i) => <Row key={i} o={o} />)}</ul>;
}
<Button primary large outline />
```
### Bien
```tsx
function Page({ items }: { items: Order[] }) {
  const total = items.reduce((a, i) => a + i.price, 0);
  return <ul>{items.map(o => <OrderRow key={o.id} order={o} />)}</ul>;
}

<Tabs defaultValue="open">
  <Tabs.List><Tabs.Trigger value="open">Abiertos</Tabs.Trigger></Tabs.List>
  <Tabs.Panel value="open"><OpenOrders /></Tabs.Panel>
</Tabs>

function useDebouncedValue<T>(value: T, ms: number): T { /* hook reutilizable */ }
```

## Checklist de revisión
- [ ] Sin componentes definidos dentro de componentes.
- [ ] Sin `useEffect` para estado derivable; `key` estable.
- [ ] Lógica repetida extraída a hooks; API por composición.
- [ ] Memoización justificada con medición.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| `eslint-plugin-react-hooks` (rules-of-hooks, exhaustive-deps) | 1 | pendiente (configuración del proyecto generado) |
| `react/no-unstable-nested-components`, `react/no-array-index-key` | 1 | pendiente (eslint-plugin-react; TODO-VERIFY nombres) |
| Revisión de API de componentes | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `design-system-and-tokens`, `state-management`, `frontend-architecture`, `frontend-performance`.
- Fuentes: documentación de React (react.dev: "You Might Not Need an Effect", Rules of Hooks) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
