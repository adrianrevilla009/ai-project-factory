---
name: typescript-strict-rules
description: "Usar al configurar tsconfig/ESLint o escribir tipos en TypeScript/React: modo strict, sin any, validación en los bordes y uniones discriminadas."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# TypeScript estricto

## Cuándo aplicar y cuándo no
- Aplica a todo código `.ts/.tsx` del proyecto React generado, incluida la configuración de `tsconfig.json`.
- No aplica a ficheros generados (cliente OpenAPI): se excluyen del lint, no se editan a mano.

## Reglas
- **MUST** activar `"strict": true` desde el primer commit; nunca "migrar a strict después".
- **SHOULD** añadir `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride` y `verbatimModuleSyntax` (comprobar disponibilidad según versión de TypeScript).
- **MUST NOT** usar `any`; para datos desconocidos usar `unknown` y estrechar.
- **MUST NOT** usar `!` (non-null) ni `as` para silenciar el compilador; `@ts-expect-error` solo con descripción.
- **MUST** tratar todo dato externo (respuesta HTTP, `localStorage`, `URLSearchParams`, `postMessage`) como `unknown` y validarlo (Zod u otro esquema) en el borde.
- **SHOULD** modelar estados con uniones discriminadas, no con varios booleanos.
- **SHOULD** tipar con `satisfies` configuraciones literales para mantener la inferencia.
- **MUST** que `tsc --noEmit` y ESLint pasen en CI.

## Por qué
Los tipos solo protegen si no hay agujeros: un `any` o un `as` desactiva la comprobación aguas abajo. Las respuestas de red son la mayor fuente de mentiras de tipos: el compilador cree lo que se le declara. Validar en el borde convierte el tipo en un hecho.

## Ejemplos
### Mal
```ts
const res = await fetch('/api/orders/1');
const order = (await res.json()) as Order;          // mentira en tiempo de compilación
type State = { loading: boolean; error?: string; data?: Order }; // combinaciones imposibles
const first = items[0]!.id;
```
### Bien
```ts
import { z } from 'zod';

const OrderSchema = z.object({ id: z.string(), total: z.number() });
type Order = z.infer<typeof OrderSchema>;

const order: Order = OrderSchema.parse(await res.json());

type State =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; data: Order };

const first = items[0];
if (first === undefined) return null;
```
```json
{ "compilerOptions": { "strict": true, "noUncheckedIndexedAccess": true, "noEmit": true } }
```

## Criterios de decisión y trampas
### Cómo decidir
- `strict` desde el primer commit; migrar después sale siempre más caro.
- Cuando el dato viene de fuera (red, almacenamiento), valídalo en el borde con un esquema y confía en el tipo solo dentro.
- Prefiere uniones discriminadas a banderas booleanas combinadas.
### Trampas frecuentes
- `as` y `!` para silenciar un error: mueven el fallo a tiempo de ejecución.
- Tipos de la API escritos a mano que divergen del contrato.
- `enum` numéricos con valores implícitos que cambian al reordenar.
- Desactivar una regla del linter en un fichero entero.
- Confundir que compile con que los datos sean correctos.
### Evidencia
- `tsc --noEmit` y el linter sin errores en CI, y cero `any` explícitos fuera de código generado.

## Checklist de revisión
- [ ] `strict: true` y `tsc --noEmit` en CI.
- [ ] Sin `any`, `!`, `as` injustificados ni `@ts-ignore`.
- [ ] Datos externos validados en el borde.
- [ ] Estados como uniones discriminadas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| ESLint typescript-eslint strict type-checked + reglas anti-`any`/`!`/`ts-ignore` | 1 | `policies/frontend-boundaries/eslint.typescript-strict.example.mjs` |
| `tsc --noEmit` en pipeline del proyecto generado | 1 | pipeline del proyecto (pendiente, lo define el proyecto) |
| Revisión de casts en PR | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `forms-and-validation`, `api-client-from-openapi`, `frontend-architecture`, `null-safety`.
- Fuentes: TypeScript handbook (tsconfig reference) y typescript-eslint (strict-type-checked) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
