---
name: auth-and-session
description: "Usar al implementar login, sesión y rutas protegidas en React: OIDC con PKCE, patrón BFF con cookie de sesión, sin tokens en localStorage."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Autenticación y sesión en el frontend

## Cuándo aplicar y cuándo no
- Aplica a login/logout, obtención del usuario actual, renovación de sesión y ocultación de UI por rol.
- No aplica al diseño del servidor de autorización (Keycloak, D-decisiones) ni a las reglas de autorización del backend: ver `authn-oidc-oauth2` y `authz-rbac-abac-rebac`.

## Reglas
- **MUST** usar Authorization Code con PKCE; nunca flujo implícito ni password grant.
- **SHOULD** preferir el patrón BFF: el backend-for-frontend hace el intercambio OIDC, guarda los tokens y entrega al navegador una cookie de sesión `HttpOnly; Secure; SameSite` (`bff-and-api-gateway`).
- **MUST NOT** guardar access/refresh tokens en `localStorage`/`sessionStorage` ni en el store persistido.
- **MUST** si no hay BFF (SPA pura), mantener el access token solo en memoria y documentar el riesgo en un ADR; refresh token en navegador: comprobar con la guía vigente de OAuth 2.0 for Browser-Based Apps.
- **MUST** con sesión por cookie, proteger mutaciones frente a CSRF (cabecera personalizada o token) y enviar `credentials: 'include'` solo al propio origen/BFF.
- **MUST** obtener el usuario actual de un endpoint (`/me`) y guardarlo como server-state, no decodificar JWT en el cliente para decidir permisos.
- **MUST** tratar 401 centralizadamente (redirigir a login) y 403 como pantalla de acceso denegado.
- **MUST** que la UI oculte, nunca proteja: todo permiso se vuelve a comprobar en el backend.
- **MUST NOT** poner `client_secret` ni secretos en el bundle (las variables `VITE_*` son públicas).

## Por qué
Cualquier script que corra en la página (XSS, dependencia comprometida) lee `localStorage`; una cookie `HttpOnly` no es legible por JS. El BFF mantiene los tokens fuera del navegador. Ocultar un botón no impide llamar a la API.

## Ejemplos
### Mal
```ts
localStorage.setItem('access_token', token);
const isAdmin = jwtDecode(token).roles.includes('admin');
{isAdmin && <DeleteButton />}   // y el endpoint DELETE no comprueba el rol
```
### Bien
```ts
// la sesión es una cookie HttpOnly emitida por el BFF; el cliente solo pregunta quién es
export const useMe = () =>
  useQuery({ queryKey: ['me'], queryFn: () => api.GET('/bff/me'), retry: false });

function RequireAuth({ children }: { children: ReactNode }) {
  const { data, isPending, isError } = useMe();
  if (isPending) return <PageSkeleton />;
  if (isError) return <Navigate to="/bff/login" replace />;
  return <>{children}</>;       // UX; el backend autoriza cada llamada
}
```

## Checklist de revisión
- [ ] PKCE; sin tokens en almacenamiento web.
- [ ] Cookie `HttpOnly; Secure; SameSite` y protección CSRF si hay BFF.
- [ ] Permisos reales en backend; la UI solo oculta.
- [ ] Sin secretos en variables `VITE_*`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: token en web storage | 1 | `policies/semgrep/frontend-token-in-web-storage.yaml` |
| Regla Semgrep: `dangerouslySetInnerHTML` | 1 | `policies/semgrep/frontend-dangerously-set-inner-html.yaml` |
| Revisión del flujo de login y de endpoints protegidos | 3 | agente `security-reviewer` (si existe; si no, revisión humana) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `security-frontend`, `authn-oidc-oauth2`, `jwt-and-sessions`, `bff-and-api-gateway`, `authz-rbac-abac-rebac`.
- Fuentes: RFC 7636 (PKCE); IETF OAuth 2.0 for Browser-Based Apps (estado del borrador (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
