---
name: authz-rbac-abac-rebac
description: "Usar al diseñar o revisar autorización: elegir RBAC, ABAC o ReBAC, aislamiento por tenant, denegar por defecto y evitar IDOR/BOLA en servicios Spring Boot."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Autorización: RBAC, ABAC y ReBAC

## Cuándo aplicar y cuándo no
- Aplica a cualquier decisión "¿puede este sujeto hacer esto sobre este recurso?".
- No aplica a la identidad del sujeto (ver `authn-oidc-oauth2`); aquí se asume ya autenticado.

## Reglas
- **MUST** denegar por defecto; los permisos se conceden explícitamente.
- **MUST** autorizar en el servidor y en cada petición; ocultar un botón en React no es control de acceso.
- **MUST** comprobar propiedad/tenant del recurso concreto, no solo el rol (evita IDOR/BOLA).
- **MUST** usar RBAC para permisos gruesos (roles por función), ABAC cuando dependa de atributos (tenant, estado, importe) y ReBAC cuando dependa de relaciones (propietario, miembro del equipo).
- **MUST** centralizar la decisión en un componente (`PermissionEvaluator`/servicio de política), no esparcir `if (role...)`.
- **MUST** derivar el tenant del token autenticado, **MUST NOT** aceptarlo de un parámetro o cabecera del cliente.
- **SHOULD** devolver 404 (no 403) cuando revelar la existencia del recurso sea sensible.
- **SHOULD** registrar las denegaciones (`audit-trail-and-security-logging`).
- **MUST NOT** codificar roles en cadenas dispersas; usar constantes o enum.

## Por qué
El control de acceso roto es la categoría más frecuente en APIs. Los roles solos no impiden que el usuario A lea el pedido del usuario B. Elegir el modelo más simple que exprese la regla evita políticas inmanejables; ReBAC solo compensa con grafos de permisos reales (si se usa un motor externo).

## Ejemplos
### Mal
```java
@GetMapping("/invoices/{id}")
@PreAuthorize("hasRole('USER')")             // cualquiera con rol USER lee cualquier factura
public Invoice get(@PathVariable Long id) { return repo.findById(id).orElseThrow(); }
```
### Bien
```java
@GetMapping("/invoices/{id}")
@PreAuthorize("hasAuthority('SCOPE_invoices:read')")
public InvoiceResponse get(@PathVariable Long id) {
    return invoiceService.getVisibleTo(id, currentUser());   // 404 si no es visible
}

@Service
class InvoiceService {
    Optional<Invoice> find(Long id, CurrentUser u) {
        return repo.findByIdAndTenantId(id, u.tenantId())           // ABAC: tenant
                   .filter(i -> i.ownerId().equals(u.id()) || u.hasRole(Role.FINANCE)); // propiedad o rol
    }
}
```
Test obligatorio:
```java
@Test
void otherTenantInvoice_returns404() throws Exception {
    mvc.perform(get("/invoices/{id}", invoiceOfTenantB).with(jwtForTenant("example-a")))
       .andExpect(status().isNotFound());
}
```

## Checklist de revisión
- [ ] Hay política de denegar por defecto (`anyRequest().authenticated()` o más estricta).
- [ ] Todo acceso por id filtra por tenant/propietario.
- [ ] El tenant sale del token, no del cliente.
- [ ] Existe test de acceso cruzado por recurso.
- [ ] La lógica de permisos está centralizada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: repositorios de entidades con tenant solo con método `...AndTenantId` | 2 | pendiente (`policies/archunit/`) |
| Test de acceso cruzado por recurso | 2 | tests del proyecto generado |
| Revisión de modelo de permisos | 3 | agente `code-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `method-and-endpoint-security`, `owasp-top10-and-api-top10`, `authn-oidc-oauth2`, `zero-trust`.
- Fuentes: OWASP Authorization Cheat Sheet (cheatsheetseries.owasp.org); documentación de Spring Security (method security).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
