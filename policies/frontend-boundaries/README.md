# frontend-boundaries

Configuraciones de ejemplo para hacer cumplir la arquitectura de un frontend React con TypeScript, organizado en `src/app`, `src/features` y `src/shared`.

**Estado: ejemplos sin ejecutar.** Se copian a la raíz del proyecto generado y se ajustan a la versión de cada herramienta.

| Fichero | Herramienta | Qué impone | Skill de origen |
|---|---|---|---|
| `dependency-cruiser.example.cjs` | dependency-cruiser | Sin ciclos; `shared` no importa de `features` ni de `app`; `features` no importa de `app` ni de otras `features`; el código de pruebas no entra en el de producción | `frontend-architecture` |
| `eslint.boundaries.example.mjs` | ESLint (configuración plana) | Las mismas fronteras como reglas de importación | `frontend-architecture` |
| `eslint.typescript-strict.example.mjs` | ESLint con `typescript-eslint` | TypeScript estricto: sin `any`, sin aserciones no nulas (`!`), promesas siempre gestionadas, imports de tipos explícitos y `@ts-ignore` prohibido | `typescript-strict-rules` |

## Uso
```bash
npx depcruise src --config .dependency-cruiser.cjs
npx eslint .
```
Además de estas reglas, las de Semgrep de `policies/semgrep/` cubren patrones de frontend (almacenamiento de tokens, HTML sin sanear, elementos clicables no semánticos).
