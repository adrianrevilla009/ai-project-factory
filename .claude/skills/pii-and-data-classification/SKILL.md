---
name: pii-and-data-classification
description: Usar al diseñar modelos de datos, logs, APIs o exportaciones que contengan datos personales, para clasificarlos, minimizarlos y protegerlos.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# PII y clasificación de datos

## Cuándo aplicar y cuándo no
- Aplica a cualquier campo que identifique o pueda identificar a una persona (nombre, email, teléfono, IP, identificadores, datos de salud o financieros) y a cómo se almacena, transmite, registra y elimina.
- No aplica a datos puramente técnicos sin relación con personas. Las obligaciones legales (RGPD u otras) son un **borrador por confirmar** con asesoría legal y la fuente oficial vigente; este skill no es consejo legal.

## Reglas
- **MUST** clasificar cada dato en un nivel (p. ej. `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) y registrar la clasificación en el modelo (anotación, esquema o catálogo de datos).
- **MUST** minimizar: no recoger, devolver ni copiar a otros servicios más PII de la necesaria.
- **MUST NOT** escribir PII ni secretos en logs, trazas, métricas, mensajes de error ni URLs (query strings); enmascarar o tokenizar.
- **MUST** cifrar en tránsito y en reposo los datos `CONFIDENTIAL`/`RESTRICTED`; cifrado a nivel de campo para los más sensibles.
- **MUST NOT** usar datos reales de producción en desarrollo, tests ni prompts a LLM; usar sintéticos o anonimizados.
- **MUST** definir retención y borrado por categoría, con procedimiento comprobable (incluidas copias de seguridad y réplicas).
- **MUST** limitar el acceso por necesidad y registrar accesos a datos `RESTRICTED` (ver `audit-trail-and-security-logging`).
- **SHOULD** pseudonimizar en analítica y separar la tabla de identificadores del resto.
- **SHOULD** respetar residencia de datos por región; en AWS depende de la configuración de la cuenta (preparado para AWS, no verificado en real).
- **MUST** no duplicar el dato personal entre Postgres y un almacén NoSQL como doble escritura (regla 4.5); un único sistema de registro.

## Por qué
El mejor control es no tener el dato: lo que no se guarda no se filtra. Los logs son el origen más frecuente de fugas de PII porque se replican, se retienen y los leen más personas que la base de datos.

## Ejemplos
### Mal
```java
log.info("Login ok for user {} email {} phone {}", id, email, phone);
```
```java
record CustomerDto(Long id, String name, String email, String nationalId, String iban) {}   // se devuelve entero a todos
```
### Bien
```java
log.info("Login ok userId={}", id);                       // identificador interno, sin PII

record CustomerSummary(Long id, String displayName, String emailMasked) {}
static String mask(String email) {
    int at = email.indexOf('@');
    return at <= 1 ? "***" : email.charAt(0) + "***" + email.substring(at);
}
```
```yaml
# data-classification.yaml (ejemplo de catalogo)
customer.email:     { level: CONFIDENTIAL, retention: "24m after account closure", log: never }
customer.nationalId: { level: RESTRICTED,  retention: "per legal basis, TBD", log: never, field_encryption: true }
```

## Checklist de revisión
- [ ] Cada campo nuevo tiene clasificación y retención.
- [ ] Ninguna PII en logs, URLs ni errores.
- [ ] DTO de respuesta devuelve solo lo necesario.
- [ ] Datos de test sintéticos; borrado verificado incluidas copias.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de modelo y logs por el agente revisor | 3 | agente `code-reviewer` |
| Regla de detección de PII en logging | 1 | pendiente (`policies/semgrep/`) |
| Confirmación legal de retención y base jurídica | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `audit-trail-and-security-logging`, `crypto-tls-mtls-key-rotation`, `llm-security`, `structured-logging`.
- Fuentes: OWASP Logging Cheat Sheet; texto legal aplicable (RGPD) por confirmar en fuente oficial EUR-Lex.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
