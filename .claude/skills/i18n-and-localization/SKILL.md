---
name: i18n-and-localization
description: "Usar al preparar el backend para varios idiomas y regiones: mensajes, locale, zonas horarias, formatos, moneda y contenido traducible almacenado. Complementa frontend-i18n-and-formatting."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# i18n y localización (backend y datos)

## Cuándo aplicar y cuándo no
- Aplica a APIs, validaciones, correos, PDFs y datos con texto traducible o fechas/importes mostrados a usuarios de distintos locales.
- No aplica a la capa de UI React (ver `frontend-i18n-and-formatting`) ni a logs internos, que van en un idioma fijo.

## Reglas
- **MUST** resolver el locale por petición (cabecera `Accept-Language` o preferencia del usuario) con un `LocaleResolver` único y un locale por defecto explícito.
- **MUST** devolver errores de API con un `code` estable y legible por máquina; el texto traducido es complementario (`ProblemDetail` con `code`), nunca el contrato.
- **MUST** externalizar mensajes en `messages_<locale>.properties` (`MessageSource`), sin cadenas de usuario concatenadas en código; usar placeholders con `MessageFormat`/ICU y plurales.
- **MUST** almacenar instantes en UTC (`Instant`/`timestamptz`) y convertir a la zona del usuario solo al presentar; guardar el `ZoneId` del usuario, no un offset.
- **MUST** guardar importes como cantidad decimal más código ISO 4217 de moneda; formatear según locale al presentar.
- **MUST** usar `Locale.ROOT` o `Locale.ENGLISH` en operaciones técnicas (`toLowerCase`, `String.format` de identificadores) para evitar el fallo del turco.
- **MUST** usar UTF-8 en todo (BD, ficheros, HTTP, `spring.messages.encoding`).
- **SHOULD** modelar contenido traducible como tabla hija `<entity>_translation(entity_id, locale, ...)` con fallback documentado (`es-MX` -> `es` -> default).
- **SHOULD** usar BCP 47 (`es-ES`) como formato de locale en API y BD.
- **MUST NOT** ordenar ni comparar texto de usuario con `compareTo` cuando importa el idioma; usar `Collator`.
- **MUST NOT** asumir que el nombre tiene "nombre + apellido" ni validar teléfonos/direcciones con una regex de un solo país.

## Por qué
Los errores de i18n aparecen tarde y caros: fechas desplazadas un día, importes con coma mal interpretada, mensajes que el cliente de la API parsea por texto. Separar código estable de texto traducido y guardar UTC mantiene el contrato intacto al añadir idiomas.

## Ejemplos
### Mal
```java
String msg = "El pedido " + id + " no existe";           // sin i18n
String key = name.toLowerCase();                         // depende del locale por defecto
LocalDateTime created = LocalDateTime.now();             // sin zona
```
### Bien
```java
String msg = messageSource.getMessage("order.notFound", new Object[]{id}, locale);
String key = name.toLowerCase(Locale.ROOT);
Instant created = Instant.now();

ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, msg);
pd.setProperty("code", "ORDER_NOT_FOUND");
```
```properties
# messages_es.properties
order.notFound=El pedido {0} no existe
```

## Checklist de revisión
- [ ] Un `LocaleResolver` y un locale por defecto explícitos.
- [ ] Errores con `code` estable más texto traducido.
- [ ] Sin cadenas de usuario hardcodeadas ni concatenadas.
- [ ] Instantes en UTC; zona del usuario guardada como `ZoneId`.
- [ ] Moneda ISO 4217 junto al importe.
- [ ] `toLowerCase`/`toUpperCase` con `Locale.ROOT` en lógica técnica.
- [ ] UTF-8 de extremo a extremo.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep: `toLowerCase()` sin `Locale` (no ejecutada aún); regla de `LocalDateTime.now()` pendiente | 1 | `policies/semgrep/java-language-pitfalls.yaml` |
| Revisión de mensajes y contratos de error | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `frontend-i18n-and-formatting`, `api-docs`, `openapi-contract-first`, `document-and-report-generation`.
- Fuentes: documentación de Spring Framework (MessageSource, LocaleResolver, ProblemDetail); BCP 47 (RFC 5646); ISO 4217.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
