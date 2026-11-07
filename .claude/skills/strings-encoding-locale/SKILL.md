---
name: strings-encoding-locale
description: Usar al manipular String, bytes, charsets, formato de números/fechas, comparaciones de texto o regex en Java; evita bugs de codificación y de Locale.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Strings, codificación y Locale

## Cuándo aplicar y cuándo no
- Aplica a conversión texto/bytes, lectura/escritura de ficheros, HTTP, comparación y normalización de texto, formateo de números, y regex.
- No aplica a cadenas puramente ASCII internas (claves técnicas) donde no hay conversión de charset ni de caso.

## Reglas
- **MUST** indicar el charset explícito en toda conversión: `s.getBytes(StandardCharsets.UTF_8)`, `new String(bytes, StandardCharsets.UTF_8)`, `Files.readString(path, UTF_8)`.
- **MUST** usar UTF-8 en ficheros, HTTP, BD y mensajería; no depender de `file.encoding` del sistema.
- **MUST** pasar `Locale` explícito a `toLowerCase`/`toUpperCase`/`String.format` cuando el resultado es un identificador técnico: usar `Locale.ROOT` (evita el problema del turco: `"TITLE".toLowerCase()` produce "tıtle" con `tr`).
- **MUST** usar `Locale` del usuario solo para presentación; formatos intercambiables (JSON, CSV, logs) usan `Locale.ROOT`/ISO-8601.
- **MUST NOT** comparar texto del usuario con `==` ni con `equals` cuando importa el caso o los acentos; usar `equalsIgnoreCase` para ASCII o `java.text.Normalizer` (NFC) + `Collator` para texto humano.
- **MUST NOT** concatenar con `+` dentro de bucles; usar `StringBuilder` o `String.join`.
- **MUST NOT** construir SQL, HTML, rutas o comandos concatenando entrada del usuario (ver `sql-injection-prevention`).
- **SHOULD** usar `isBlank()`, `strip()` (Unicode) en lugar de `trim()` y `split` con regex cuando basta con otra API.
- **MUST** precompilar los `Pattern` reutilizados (`static final`) y evitar regex con retroceso catastrófico sobre entrada externa (ReDoS).

## Por qué
El charset por defecto varía entre máquinas y contenedores: un texto correcto en el portátil se corrompe en el servidor. Con el locale por defecto en turco, `toUpperCase` rompe comparaciones de identificadores. Un mismo carácter acentuado puede tener dos representaciones Unicode, y sin normalizar la igualdad falla.

## Ejemplos
### Mal
```java
byte[] data = name.getBytes();                          // charset de la plataforma
String key = header.toLowerCase();                      // depende del Locale por defecto
String sql = "select * from users where name = '" + name + "'";
if (input.matches("(a+)+$")) { ... }                    // regex con backtracking catastrófico
```
### Bien
```java
private static final Pattern ORDER_ID = Pattern.compile("[A-Z]{3}-\\d{6}");

byte[] data = name.getBytes(StandardCharsets.UTF_8);
String key = header.toLowerCase(Locale.ROOT);
String normalized = Normalizer.normalize(input, Normalizer.Form.NFC);
boolean valid = ORDER_ID.matcher(normalized).matches();
String price = NumberFormat.getCurrencyInstance(userLocale).format(amount);
```

## Checklist de revisión
- [ ] Todas las conversiones bytes/texto indican `StandardCharsets.UTF_8`.
- [ ] `toLowerCase/toUpperCase/format` técnicos usan `Locale.ROOT`.
- [ ] Texto humano comparado con normalización y `Collator`.
- [ ] Patrones precompilados y sin riesgo de ReDoS.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep `java-default-charset-string` (sin ejecutar, TODO-VERIFY) | 1 | `policies/semgrep/java-language-pitfalls.yaml` |
| Revisión de formatos y regex | 3 | agente `code-reviewer` (pendiente de definir) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `time-and-money`, `sql-injection-prevention`, `owasp-top10-and-api-top10`.
- Fuentes: Javadoc de `java.nio.charset.StandardCharsets`, `java.text.Normalizer`, `java.util.Locale` — no verificado en línea. Nota: el comportamiento por defecto de charset cambió en JDK recientes (UTF-8 por defecto): TODO-VERIFY versión; la regla sigue siendo ser explícito.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
