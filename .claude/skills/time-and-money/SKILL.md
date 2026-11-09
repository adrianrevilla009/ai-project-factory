---
name: time-and-money
description: Usar al manejar fechas, zonas horarias, duraciones, relojes, importes o divisas en Java; evita java.util.Date, double para dinero y tiempo no testeable.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Tiempo y dinero

## Cuándo aplicar y cuándo no
- Aplica a cualquier campo de fecha/hora, cálculo de plazos, precios, impuestos, totales y conversión de divisa.
- No aplica a mediciones de rendimiento (usar `System.nanoTime`) ni a cálculo científico donde `double` es apropiado.

## Reglas
- **MUST** usar `java.time` (`Instant`, `LocalDate`, `ZonedDateTime`, `Duration`); **MUST NOT** usar `Date`, `Calendar` ni `SimpleDateFormat` (no seguro entre hilos).
- **MUST** almacenar y transmitir instantes en UTC (`Instant`, ISO-8601); convertir a zona local solo en presentación.
- **MUST** indicar `ZoneId` explícito; **MUST NOT** depender de la zona por defecto del servidor.
- **MUST** inyectar `java.time.Clock` en lugar de llamar a `Instant.now()` en lógica de negocio, para poder fijar el tiempo en tests.
- **MUST NOT** usar `double`/`float` para dinero; usar `BigDecimal` con escala y `RoundingMode` explícitos, o enteros en unidad mínima (céntimos).
- **MUST** crear `BigDecimal` con `BigDecimal.valueOf(...)` o desde `String`, nunca `new BigDecimal(double)`.
- **MUST** modelar el dinero como `Money(BigDecimal amount, Currency currency)` y rechazar operaciones entre divisas distintas.
- **MUST** comparar `BigDecimal` con `compareTo`, no `equals` (distingue escala).
- **SHOULD** usar `Duration` para intervalos y `Period` para calendario; **MUST NOT** sumar 24 h para "un día" en zonas con cambio horario.

## Por qué
`0.1 + 0.2 != 0.3` en binario: los céntimos se pierden. Una fecha sin zona se interpreta distinto según el servidor. Con `Clock` inyectado los tests de caducidades son deterministas. Normativa fiscal de redondeo: borrador por confirmar con fuente oficial según jurisdicción.

## Ejemplos
### Mal
```java
double total = 0.1 + 0.2;
BigDecimal price = new BigDecimal(19.99);                  // 19.989999999999998436...
Date expires = new Date(System.currentTimeMillis() + 86_400_000L);
boolean expired = Instant.now().isAfter(token.expiresAt()); // no testeable
```
### Bien
```java
public record Money(BigDecimal amount, Currency currency) {
    public Money {
        Objects.requireNonNull(currency, "currency");
        amount = amount.setScale(currency.getDefaultFractionDigits(), RoundingMode.HALF_EVEN);
    }
    public Money plus(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException("currency mismatch");
        return new Money(amount.add(other.amount), currency);
    }
}

class TokenService {
    private final Clock clock;
    TokenService(Clock clock) { this.clock = clock; }
    boolean isExpired(Token t) { return clock.instant().isAfter(t.expiresAt()); }
}
// test: Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC)
```

## Checklist de revisión
- [ ] Solo `java.time`; instantes en UTC.
- [ ] `Clock` inyectado; ningún `now()` en dominio.
- [ ] Dinero con `BigDecimal`/`Money`, escala y redondeo explícitos.
- [ ] Sin `new BigDecimal(double)` ni `equals` entre `BigDecimal`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Reglas Semgrep: dinero como double, `new BigDecimal(...)`, API de fechas legada (heurísticas sin ejecutar) | 1 | `policies/semgrep/java-language-pitfalls.yaml` |
| Revisión del modelo de dinero | 3 | agente `code-reviewer` (pendiente de definir) |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos. La regla de `new BigDecimal` solo marca argumentos tipados `double`/`float` o literales con decimales.

## Relacionados, fuentes y mantenimiento
- Relacionados: `immutability-and-value-objects`, `strings-encoding-locale`, `concurrency-testing`.
- Fuentes: Javadoc de `java.time.Clock`, `java.math.BigDecimal` — no verificado en línea.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
