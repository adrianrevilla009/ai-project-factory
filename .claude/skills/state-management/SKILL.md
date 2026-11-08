---
name: state-management
description: "Usar al decidir dónde vive el estado en React: server-state (TanStack Query), client-state (Zustand/Redux Toolkit), URL y formularios."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Gestión de estado

## Cuándo aplicar y cuándo no
- Aplica al añadir datos que se comparten entre componentes, vienen del backend o sobreviven a la navegación.
- No aplica al estado local efímero de un componente (`useState` es correcto: un toggle, un input no enviado).

## Reglas
- **MUST** clasificar cada dato antes de elegir herramienta: server-state, URL-state, form-state, client-state global o local.
- **MUST** gestionar server-state con TanStack Query (caché, invalidación, reintentos), no copiarlo a Redux/Zustand.
- **MUST** poner en la URL (query params, path) lo que debe ser enlazable/recargable: filtros, página, orden, pestaña.
- **MUST** dejar el form-state a React Hook Form (`forms-and-validation`).
- **SHOULD** usar Zustand o Redux Toolkit solo para estado de cliente verdaderamente global (UI shell, preferencias, wizard multipaso); elegir uno por proyecto.
- **MUST** definir claves de query en una factoría por feature, y invalidar tras mutaciones.
- **MUST NOT** guardar tokens o datos sensibles en el store persistido (`auth-and-session`).
- **MUST NOT** sincronizar con `useEffect` un estado derivable: calcularlo durante el render.
- **SHOULD** usar selectores en el store para evitar renders innecesarios.

## Por qué
Copiar datos del servidor a un store crea una segunda fuente de verdad que caduca. Una librería de server-state ya resuelve caché, deduplicación y reintento. La URL como estado da enlaces compartibles y botón "atrás" correcto. Nombres de API (`useQuery`, `invalidateQueries`, `queryKey`) a verificar contra la versión instalada (TODO-VERIFY v5).

## Ejemplos
### Mal
```tsx
const [orders, setOrders] = useState<Order[]>([]);
useEffect(() => { fetch('/api/orders').then(r => r.json()).then(setOrders); }, []);
const [page, setPage] = useState(1); // se pierde al recargar
```
### Bien
```tsx
export const orderKeys = {
  all: ['orders'] as const,
  list: (page: number) => [...orderKeys.all, 'list', page] as const,
};

const [params, setParams] = useSearchParams();
const page = Number(params.get('page') ?? '1');
const { data, isPending } = useQuery({
  queryKey: orderKeys.list(page),
  queryFn: () => ordersApi.list({ page }),
});

const create = useMutation({
  mutationFn: ordersApi.create,
  onSuccess: () => queryClient.invalidateQueries({ queryKey: orderKeys.all }),
});
```

## Checklist de revisión
- [ ] Cada dato clasificado; server-state en TanStack Query.
- [ ] Filtros/paginación en la URL.
- [ ] Sin `useEffect` para sincronizar o derivar estado.
- [ ] Un solo store global y sin datos sensibles persistidos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Plugin ESLint de TanStack Query / `react-hooks/exhaustive-deps` | 1 | pendiente (configuración del proyecto generado; TODO-VERIFY nombres) |
| Revisión de clasificación del estado | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `forms-and-validation`, `api-client-from-openapi`, `routing-and-code-splitting`, `auth-and-session`.
- Fuentes: documentación de TanStack Query, Zustand, Redux Toolkit (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
