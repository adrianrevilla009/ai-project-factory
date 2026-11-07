# Estándares · 26-enterprise-capabilities

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## identity-and-customer-management

- **MUST** delegar autenticación y almacén de credenciales en Keycloak (D-closed); el servicio de negocio NUNCA guarda contraseñas ni hashes.
- **MUST** separar identidad (Keycloak: `sub`, credenciales, MFA) de cliente de negocio (tabla `customer` propia) enlazados por `sub` inmutable, no por email.
- **MUST** crear el registro `customer` de forma idempotente en el primer login o por evento, con clave única sobre `identity_subject`.
- **MUST** tratar el email como atributo mutable y verificado, nunca como clave primaria.
- **SHOULD** usar la Admin REST API de Keycloak solo desde un servicio de backend con cliente de servicio de mínimo privilegio.
- **SHOULD** modelar roles gruesos en Keycloak y permisos de dominio en el servicio.
- **MUST NOT** duplicar en la BD de negocio datos de credenciales ni sincronizar contraseñas.
- **MUST NOT** confiar en claims editables por el usuario (ej. atributos de perfil sin protección) para autorizar.

## notifications

- **MUST** desacoplar el origen del envío: el caso de uso emite un evento (outbox, ver `outbox-and-cdc`) y un consumidor `notification-service` envía.
- **MUST** garantizar idempotencia con `notification_key` (evento + destinatario + canal) y restricción única; reintentos no duplican mensajes.
- **MUST** respetar preferencias y consentimiento por canal y propósito (`consent-and-dsar-management`); las transaccionales se distinguen de las de marketing.
- **MUST** reintentar con backoff y DLQ (`dlq-retries-poison-messages`); fallo del proveedor no bloquea la transacción de negocio.
- **MUST** usar plantillas versionadas con i18n (`i18n-and-localization`); sin concatenar texto en código.
- **MUST NOT** registrar en logs el cuerpo, teléfono o email completos (PII).
- **MUST NOT** incluir secretos o tokens de larga vida en enlaces; usar tokens de un solo uso con caducidad.
- **SHOULD** abstraer proveedores tras `NotificationChannelPort` (SMTP local con MailHog/Mailpit en dev; el proveedor real de AWS, p. ej. SES, no se emula localmente y queda TODO-VERIFY).

## rules-engines

- **MUST** empezar por código (patrón Strategy / specification) y justificar por escrito el salto a un motor.
- **MUST** comprobar licencia del motor elegido (D16). Drools/KIE y DMN de Camunda/Flowable: licencia y versión TODO-VERIFY en documentación oficial.
- **MUST** aislar el motor tras un puerto `PricingRulesPort`; entrada y salida son DTOs inmutables.
- **MUST** versionar reglas junto al código y probarlas con casos tabulares (given/expected).
- **MUST** registrar qué versión de reglas decidió cada resultado (trazabilidad, ver `audit-trail-and-activity-log`).
- **MUST NOT** permitir que reglas editadas en caliente lleguen a producción sin revisión y pruebas.
- **MUST NOT** dar acceso a servicios/BD al motor desde las reglas (efectos laterales).
- **SHOULD** preferir tablas de decisión (DMN) cuando negocio las mantiene.

## workflow-bpm

- **MUST** decidir el motor por licencia antes de adoptarlo (D16, sin licencias de pago por defecto). Camunda 8 self-managed usa licencia propietaria y exige Enterprise para producción según https://docs.camunda.io/docs/reference/licenses/ (2026-11-07). Camunda 7 CE y Flowable OSS: licencia y estado de mantenimiento TODO-VERIFY.
- **MUST** mantener el motor tras una interfaz propia (`ApprovalProcessPort`); el dominio no importa clases del motor.
- **MUST** versionar los `.bpmn` en el repo y migrar instancias en vuelo de forma explícita.
- **MUST** hacer idempotentes los service tasks (pueden reejecutarse tras fallo).
- **MUST NOT** meter reglas de negocio complejas en expresiones del BPMN; delegarlas a código testeado o `rules-engines`.
- **MUST NOT** compartir la BD del motor con tablas de negocio sin esquema separado.
- **SHOULD** usar correlación por `businessKey` y no guardar datos personales en variables de proceso.
- **SHOULD** definir timeouts y boundary events para tareas humanas.
