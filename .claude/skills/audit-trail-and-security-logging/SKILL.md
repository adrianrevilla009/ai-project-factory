---
name: audit-trail-and-security-logging
description: Usar al decidir qué eventos de seguridad y auditoría registrar, con qué campos, y cómo protegerlos de manipulación y de fugas de datos.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Auditoría y logging de seguridad

## Cuándo aplicar y cuándo no
- Aplica a eventos de autenticación, autorización, cambios de configuración y de datos sensibles, acciones administrativas y accesos a datos restringidos.
- No aplica al logging operativo general (ver `structured-logging`) ni a métricas de negocio.

## Reglas
- **MUST** registrar como mínimo: login correcto/fallido, logout, cambios de credenciales/MFA, denegaciones de autorización, cambios de rol/permisos, accesos a datos `RESTRICTED`, acciones administrativas y errores de validación repetidos.
- **MUST** incluir en cada evento: instante UTC, tipo de evento, actor (id interno), recurso, acción, resultado, origen (IP/servicio) y `traceId`/correlación.
- **MUST NOT** registrar contraseñas, tokens, claves, números de tarjeta ni PII innecesaria (ver `pii-and-data-classification`).
- **MUST** neutralizar la inyección en logs: no escribir saltos de línea ni caracteres de control de entrada externa; preferir logs JSON estructurados.
- **MUST** separar el log de auditoría del log técnico, con acceso de solo escritura para la aplicación y lectura restringida.
- **MUST** hacerlo resistente a manipulación: envío casi en tiempo real a un destino aparte (cuenta de logs distinta; en AWS, preparado para AWS no verificado en real), inmutabilidad/retención y control de integridad. En local solo se reproduce el envío a un colector, no la inmutabilidad real.
- **MUST** definir retención según requisito (a confirmar con fuente legal) y alertar sobre eventos críticos (fuerza bruta, escalada de privilegios).
- **SHOULD** emitir los eventos de auditoría desde la capa de aplicación (dominio), no solo desde el proxy, para capturar la intención.
- **SHOULD** garantizar que el fallo del log de auditoría no pase en silencio para operaciones críticas.

## Por qué
Sin registro no hay detección ni investigación; con registro manipulable o lleno de datos sensibles, el log se convierte en el problema. La auditoría responde quién hizo qué, sobre qué y cuándo.

## Ejemplos
### Mal
```java
log.info("User " + username + " login with password " + password + " from " + request.getHeader("X-Forwarded-For"));
```
### Bien
```java
@Component
class AuditLogger {
    private static final Logger AUDIT = LoggerFactory.getLogger("AUDIT");

    void authzDenied(String actorId, String resource, String action) {
        AUDIT.atWarn()
             .addKeyValue("event", "AUTHZ_DENIED")
             .addKeyValue("actor", actorId)
             .addKeyValue("resource", resource)
             .addKeyValue("action", action)
             .addKeyValue("traceId", MDC.get("traceId"))
             .log("authorization denied");
    }
}
```
```json
{"ts":"2026-11-07T10:15:30Z","event":"AUTHZ_DENIED","actor":"u-123","resource":"order/987","action":"READ","result":"DENIED","traceId":"4bf92f3577b34da6"}
```
Usar `logger` con `addKeyValue` requiere SLF4J 2.x.

## Criterios de decisión y trampas
### Cómo decidir
- Registra quién, qué, cuándo y desde dónde de cada acción de seguridad relevante, de forma inmutable y separada de los registros de aplicación.
- Define qué eventos se registran con el equipo de seguridad.
### Trampas frecuentes
- Registros editables por la propia aplicación.
- Registrar datos sensibles en la auditoría.
- Sin sincronización de relojes.
- Auditoría que nadie revisa ni alerta.
- Retención menor que la exigida.
### Evidencia
- Una prueba comprueba que cada acción sensible deja un registro completo.

## Checklist de revisión
- [ ] Los eventos mínimos de la regla están cubiertos y probados.
- [ ] Ningún secreto ni PII innecesaria en los eventos.
- [ ] Entrada externa saneada antes de loguear.
- [ ] Destino de auditoría separado, con retención y alertas definidas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Reglas Semgrep de logging (stack trace, concatenación) | 1 | `policies/semgrep/java-logging.yaml` |
| Test que verifica evento de auditoría en acciones sensibles | 1 | tests del proyecto generado (se implementa en el proyecto generado) |
| Revisión de cobertura de eventos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `structured-logging`, `pii-and-data-classification`, `org-cloudtrail-config-securityhub-guardduty`, `vulnerability-sla-and-incident-response`.
- Fuentes: OWASP Logging Cheat Sheet y Logging Vocabulary.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
