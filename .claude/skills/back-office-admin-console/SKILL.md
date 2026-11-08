---
name: back-office-admin-console
description: "Usar al diseñar o revisar una consola de administración / back-office (soporte, operaciones, impersonación, acciones masivas) con permisos, auditoría y aprobación de acciones sensibles."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Consola de administración / back-office

## Cuándo aplicar y cuándo no
- Aplica a pantallas y APIs internas para soporte, operaciones, finanzas o administradores de plataforma: búsqueda de clientes, correcciones manuales, impersonación, acciones masivas.
- No aplica al panel de autoservicio del cliente final ni a herramientas de observabilidad (Grafana, etc.).

## Reglas
- **MUST** servir la consola como aplicación y API separadas del frontend público (otro host, otro cliente OIDC en Keycloak, otro conjunto de roles). Nunca un flag `isAdmin` dentro de la app pública.
- **MUST** autorizar en el servidor cada endpoint `/admin/**` con permisos granulares (`customer:read`, `refund:approve`), no solo con un rol grueso `ADMIN`.
- **MUST** exigir MFA y sesiones cortas para los usuarios de back-office.
- **MUST** registrar cada acción de escritura en el audit trail (quién, qué, sobre quién, motivo, antes/después) con motivo obligatorio en texto libre o código.
- **MUST** aplicar cuatro ojos (solicitante != aprobador) a acciones sensibles: reembolsos sobre umbral, cambio de datos bancarios, borrado, cambio de rol.
- **MUST** limitar y registrar la impersonación: tiempo máximo, banner visible, sin acceso a credenciales ni a cambio de contraseña/MFA, token marcado con `act` (claim de actor) para que el audit distinga al agente del usuario.
- **MUST** enmascarar por defecto datos personales y sensibles (IBAN, documento) y exigir "revelar" como acción auditada.
- **SHOULD** que las acciones masivas sean asíncronas, con previsualización (dry-run), límite de filas y registro de resultado por fila.
- **MUST NOT** exponer entidades JPA directamente; usar DTO específicos de admin.
- **MUST NOT** reutilizar tokens del frontend público para llamar a la API de admin.

## Por qué
El back-office concentra el mayor poder y el menor escrutinio: es el vector típico de fraude interno y de fuga de datos. Separar el cliente OIDC, afinar permisos y auditar el motivo convierte el abuso en detectable. Los cuatro ojos y el dry-run reducen errores humanos masivos. La política concreta de umbrales es decisión de negocio (por confirmar).

## Ejemplos
### Mal
```java
@GetMapping("/admin/users/{id}")
@PreAuthorize("isAuthenticated()")
public UserEntity get(@PathVariable Long id) { // entidad completa, sin auditar
    return repo.findById(id).orElseThrow();
}
```
### Bien
```java
@PostMapping("/admin/refunds/{id}/approve")
@PreAuthorize("hasAuthority('refund:approve')")
public void approve(@PathVariable UUID id, @Valid @RequestBody ApprovalRequest req,
                    @AuthenticationPrincipal Jwt jwt) {
    refundService.approve(id, jwt.getSubject(), req.reason()); // lanza si solicitante == aprobador
}

// en el servicio
if (refund.requestedBy().equals(approverId)) {
    throw new FourEyesViolationException(refund.id());
}
auditLog.record(AuditEvent.of("REFUND_APPROVED", approverId, refund.id(), reason));
```

## Checklist de revisión
- [ ] Cliente OIDC, host y roles de admin separados de los públicos.
- [ ] Permisos granulares por endpoint, probados con test de acceso denegado.
- [ ] Toda escritura genera evento de auditoría con motivo.
- [ ] Acciones sensibles con cuatro ojos.
- [ ] Impersonación acotada, visible y distinguible en logs.
- [ ] Datos sensibles enmascarados; "revelar" auditado.
- [ ] Acciones masivas con dry-run y límite.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de endpoints `/admin/**` sin autorización granular | 3 | agente `code-reviewer` |
| Regla Semgrep `/admin/**` sin `@PreAuthorize` | 1 | pendiente (`policies/semgrep/`) |
| Definición de umbrales de cuatro ojos | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `authz-rbac-abac-rebac`, `audit-trail-and-activity-log`, `audit-and-break-glass`, `access-control-masking-and-retention`, `rbac-and-service-accounts`.
- Fuentes: RFC 8693 (claim `act`, token exchange) y OWASP ASVS, verificadas 2026-11-07 solo a nivel de concepto; ASVS vigente: 5.0.0.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
