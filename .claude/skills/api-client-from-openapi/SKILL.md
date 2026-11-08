---
name: api-client-from-openapi
description: "Usar al consumir una API desde React: generar tipos/cliente desde el OpenAPI del backend, regenerar en CI y no escribir llamadas HTTP a mano."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Cliente API generado desde OpenAPI

## Cuándo aplicar y cuándo no
- Aplica a toda llamada del frontend a APIs propias que publican un contrato OpenAPI (`openapi-contract-first`).
- No aplica a APIs de terceros sin contrato (se envuelven en un adaptador con esquemas Zod).

## Reglas
- **MUST** que el contrato OpenAPI sea la fuente de verdad; el frontend no redefine tipos de la API a mano.
- **MUST** generar tipos/cliente con una herramienta (p. ej. openapi-typescript + openapi-fetch, u Orval; comprobar elección y versión) y confirmar el comando en `package.json`.
- **MUST** ubicar el código generado en `src/shared/api/generated/`, marcado como generado y excluido de lint/formato.
- **MUST NOT** editar a mano el código generado; se cambia el contrato y se regenera.
- **MUST** regenerar en CI y fallar si el resultado difiere del commiteado (drift).
- **MUST** centralizar base URL, cabeceras, timeouts y manejo de 401 en un único cliente en `src/shared/api`.
- **MUST** cada feature envuelva el cliente en funciones de su `api/` y las consuma vía TanStack Query (`state-management`).
- **SHOULD** validar en ejecución con Zod las respuestas críticas si el backend no es de confianza total.
- **MUST NOT** hardcodear URLs de entorno; usar variables `VITE_*` (solo valores públicos, nunca secretos).

## Por qué
Tipos escritos a mano derivan del backend y fallan en producción, no en compilación. Generar desde el contrato convierte un cambio incompatible en un error de `tsc`. Las variables `VITE_*` se incrustan en el bundle y son visibles para cualquiera.

## Ejemplos
### Mal
```ts
interface Order { id: number; total: string }   // copiado "de memoria"
const res = await fetch('http://localhost:8080/api/orders');
```
### Bien
```json
{ "scripts": {
  "api:generate": "openapi-typescript ./openapi/orders.yaml -o src/shared/api/generated/schema.d.ts",
  "api:check": "npm run api:generate && git diff --exit-code src/shared/api/generated"
} }
```
```ts
// src/shared/api/client.ts
import createClient from 'openapi-fetch';
import type { paths } from './generated/schema';

export const api = createClient<paths>({ baseUrl: import.meta.env.VITE_API_BASE_URL });
// uso: const { data, error } = await api.GET('/orders/{id}', { params: { path: { id } } });
```
Comandos y API de las librerías: comprobar contra su documentación.

## Checklist de revisión
- [ ] Tipos y cliente generados del OpenAPI vigente.
- [ ] `api:check` en CI sin drift.
- [ ] Cliente único con base URL por entorno.
- [ ] Nada de `fetch` suelto en componentes.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Paso CI `api:check` (regenerar y `git diff --exit-code`) | 1 | pipeline del proyecto generado (pendiente) |
| Contrato en pipeline | 1 | skill `contract-gate` |
| Revisión: sin `fetch` directo en features | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `openapi-contract-first`, `contract-testing`, `state-management`, `typescript-strict-rules`, `error-handling-problem-details`.
- Fuentes: documentación de openapi-typescript/openapi-fetch/Orval y de Vite (variables de entorno) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
