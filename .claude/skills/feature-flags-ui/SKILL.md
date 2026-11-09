---
name: feature-flags-ui
description: "Usar al condicionar UI o rutas React con feature flags (OpenFeature): evaluación, carga inicial, flicker, limpieza y por qué un flag no protege."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Feature flags en la UI

## Cuándo aplicar y cuándo no
- Aplica a flags que cambian la interfaz: lanzamientos graduales, experimentos, kill switches de una feature.
- No aplica al modelo general de flags del backend (`feature-flags-openfeature`). Los permisos no son flags: ver `auth-and-session`.

## Reglas
- **MUST** acceder a los flags mediante una abstracción única (cliente OpenFeature y hooks propios), nunca leyendo el proveedor directamente en componentes.
- **MUST** definir valor por defecto seguro (feature apagada) para cuando el proveedor falle o tarde; la app debe funcionar sin proveedor.
- **MUST** evaluar el flag una vez por vista y evitar flicker: resolver antes del primer render de la zona afectada (carga inicial o esqueleto), no mostrar A y luego B.
- **MUST NOT** usar un flag como control de seguridad: la UI oculta, el backend autoriza (`authz-rbac-abac-rebac`); un flag expuesto en el cliente es visible y manipulable.
- **MUST NOT** enviar al proveedor PII innecesaria en el contexto de evaluación; usar identificadores seudónimos y atributos mínimos.
- **MUST** dar a cada flag dueño, fecha de caducidad y ticket de retirada; eliminar el código muerto de ambas ramas al consolidar.
- **SHOULD** limitar el número de flags activos y evitar combinatoria (flags anidados); nombrar con convención `area.feature`.
- **SHOULD** testear ambas ramas (Vitest con proveedor en memoria) y registrar la variante en la telemetría (`observability-frontend`).

## Por qué
Los flags desacoplan despliegue de lanzamiento, pero cada uno duplica caminos de código y tests. Sin caducidad se acumulan y nadie sabe cuál está vivo. El cliente es entorno no confiable, por eso no sirve para seguridad.

## Ejemplos
### Mal
```tsx
if (localStorage.getItem("betaCheckout") === "true") return <NewCheckout />; // el usuario lo activa a mano
if (flags.adminPanel) return <AdminPanel />; // "seguridad" por flag
```
### Bien
```tsx

import { useBooleanFlagValue } from "@openfeature/react-sdk";

export function Checkout() {
  const newFlow = useBooleanFlagValue("checkout.new-flow", false); // defecto seguro
  return newFlow ? <NewCheckout /> : <LegacyCheckout />;
}
```
```text
# registro de flag (en el repo o catalogo del proveedor)
checkout.new-flow | owner: team-checkout | expira: 2027-01-31 | retirar: TICKET-123 (example)
```

## Criterios de decisión y trampas
### Cómo decidir
- El flag controla la visibilidad; la autorización real la decide el servidor.
- Valor por defecto seguro (apagado) si el proveedor falla o tarda.
- Retira los flags de vida corta cuando se despliega la funcionalidad.
### Trampas frecuentes
- Flags que viven años y acumulan combinaciones sin probar.
- Parpadeo de interfaz al resolver el flag tarde.
- Usar un flag como control de seguridad.
- Lógica de flags repartida por todos los componentes.
- No registrar qué usuarios vieron qué variante, lo que impide analizar errores.
### Evidencia
- Cada flag tiene dueño y fecha de retirada.

## Checklist de revisión
- [ ] Acceso por abstracción y valor por defecto seguro.
- [ ] Sin flicker en la carga inicial.
- [ ] El flag no sustituye a una comprobación de autorización en backend.
- [ ] Dueño, caducidad y ticket de retirada.
- [ ] Tests de ambas ramas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Informe de flags caducados en CI | 2 | pipeline del proyecto generado (pendiente) |
| Revisión humana de uso como control de acceso | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `feature-flags-openfeature`, `auth-and-session`, `testing`, `observability-frontend`, `canary-and-traffic-splitting`.
- Fuentes: https://openfeature.dev.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
