---
name: iam-governance-and-pam
description: "Usar al diseñar o revisar el gobierno de identidades: ciclo joiner-mover-leaver, recertificación de accesos, cuentas privilegiadas (PAM) y separación de funciones."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Gobierno de identidades y accesos privilegiados (IGA / PAM)

## Cuándo aplicar y cuándo no
- Aplica al definir quién obtiene acceso, cómo se revisa y cómo se gestionan cuentas privilegiadas de personas y de máquinas.
- No aplica al diseño técnico de autenticación de la aplicación (ver `authn-oidc-oauth2`) ni a permisos cloud concretos (ver `cloud-iam-least-privilege`).

## Reglas
- **MUST** tener una fuente de verdad de identidades (IdP corporativo, p. ej. Keycloak, D-decisiones de la fábrica) y provisionar/retirar accesos desde ella, no a mano en cada sistema.
- **MUST** automatizar joiner-mover-leaver: alta con rol base, cambio de puesto retira accesos anteriores, baja revoca en el mismo día laborable.
- **MUST** recertificar accesos privilegiados al menos trimestralmente y el resto al menos anualmente; el revisor es el responsable del negocio, no quien tiene el acceso.
- **MUST** separar funciones: quien solicita, quien aprueba y quien ejecuta un cambio crítico no pueden ser la misma persona.
- **MUST** usar cuentas administrativas nominales y separadas de la cuenta diaria; MFA resistente a phishing donde sea posible.
- **MUST** dar acceso privilegiado just-in-time, con caducidad y motivo registrado (ver `break-glass-and-jit-access`).
- **MUST NOT** compartir cuentas administrativas ni dejar credenciales de servicio sin propietario asignado.
- **SHOULD** inventariar identidades no humanas (service accounts, tokens, claves) con propietario y fecha de rotación.
- **SHOULD** grabar o auditar las sesiones privilegiadas y enviar los registros a un almacén inmutable (ver `audit-trail-and-security-logging`).
- **MUST NOT** conceder `Action: "*"` sobre `Resource: "*"` en políticas IAM salvo rol break-glass documentado.

## Por qué
Los incidentes por credenciales abusadas suelen venir de accesos acumulados que nadie revisó: el empleado que cambió de equipo y conservó permisos, o la cuenta de servicio olvidada. La recertificación y el JIT acotan el radio de daño y dejan evidencia para auditoría.

## Ejemplos
### Mal
```text
Ticket: "dar admin a María en prod, urgente". Sin caducidad, sin aprobador, sin revisión.
La cuenta "svc-deploy" la usan 5 personas con la misma contraseña (changeme-example).
```
### Bien
```yaml
# access-policy.example.yaml (documento de gobierno, no código ejecutable)
role: prod-db-admin
grant: just-in-time
max_duration: 4h
approver: data-owner        # distinto del solicitante
requires: [mfa, ticket]
recertification: quarterly
session_audit: true
leaver_sla: same-business-day
```

## Criterios de decisión y trampas
### Cómo decidir
- Ciclo de vida de identidades (alta, cambio, baja), revisión periódica de accesos y acceso privilegiado temporal, registrado y con aprobación.
- Separa cuentas de uso diario y de administración.
### Trampas frecuentes
- Accesos que nunca se retiran.
- Cuentas privilegiadas permanentes.
- Revisiones de formalidad.
- Cuentas compartidas.
- Sin registro de acciones privilegiadas.
### Evidencia
- Una revisión de accesos con retirada efectiva y un registro de sesiones privilegiadas.

## Checklist de revisión
- [ ] Existe un proceso JML con SLA de baja medido.
- [ ] Hay calendario de recertificación con responsables y evidencias guardadas.
- [ ] Ninguna cuenta privilegiada es compartida ni permanente sin justificación.
- [ ] Las cuentas de servicio tienen propietario y rotación.
- [ ] Las políticas IAM no contienen administrador comodín.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest sobre el plan: deniega `Action "*"` + `Resource "*"` (estático, nada se despliega) | 1 | `policies/opa-conftest/iam-no-wildcard-admin.rego` |
| Recertificación y JML | 4 | revisión humana (proceso, sin artefacto automático) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `break-glass-and-jit-access`, `audit-and-break-glass`, `cloud-iam-least-privilege`, `identity-center-sso`, `rbac-and-service-accounts`.
- Fuentes: NIST SP 800-53 familia AC (control de acceso); cadencias de recertificación son recomendación de la fábrica, a confirmar con la política de la organización.
- Cloud: preparado para AWS, no verificado en real. En local no se reproduce IAM de AWS; Keycloak solo cubre identidad de aplicación.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
