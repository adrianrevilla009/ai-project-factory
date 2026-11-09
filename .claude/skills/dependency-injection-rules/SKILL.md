---
name: dependency-injection-rules
description: "Usar al escribir o revisar beans Spring: inyección por constructor, sin field injection, sin dependencias circulares ni service locator."
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Reglas de inyección de dependencias

## Cuándo aplicar y cuándo no
- Aplica a todo `@Component`, `@Service`, `@Controller`, `@Configuration` y beans de `@Bean`.
- No aplica a tests de slice donde `@MockitoBean`/`@Autowired` en el test es el mecanismo del framework.

## Reglas
- **MUST** inyectar por constructor con campos `final`; con un único constructor no hace falta `@Autowired`.
- **MUST NOT** usar `@Autowired` sobre campos ni setters en código de producción.
- **MUST NOT** usar `ApplicationContext.getBean(...)` como service locator.
- **MUST NOT** introducir dependencias circulares; refactorizar (extraer un tercer bean o publicar un evento). No activar `spring.main.allow-circular-references`.
- **SHOULD** limitar un bean a ~5 dependencias; más indica responsabilidades mezcladas.
- **SHOULD** inyectar interfaces o tipos mínimos necesarios, no implementaciones concretas ni `EntityManager` en controladores.
- **MUST** usar `@Qualifier` o un tipo propio cuando existan varios beans del mismo tipo; no depender del nombre del parámetro.
- **MUST NOT** usar Lombok (`@RequiredArgsConstructor`) (D27); escribir el constructor.

## Por qué
La inyección por constructor hace explícitas las dependencias, permite objetos inmutables y tests sin contexto Spring, y falla al arrancar si falta algo. Los ciclos esconden acoplamiento; Spring Boot los prohíbe por defecto desde 2.6 y activarlos solo tapa el problema.

## Ejemplos
### Mal
```java
@Service
class InvoiceService {
    @Autowired
    private InvoiceRepository repository;   // field injection

    void close(long id) {
        var mailer = SpringContext.getBean(Mailer.class); // service locator
    }
}
```
### Bien
```java
@Service
class InvoiceService {
    private final InvoiceRepository repository;
    private final Mailer mailer;

    InvoiceService(InvoiceRepository repository, Mailer mailer) {
        this.repository = repository;
        this.mailer = mailer;
    }
}

// Test sin Spring
var service = new InvoiceService(fakeRepository, fakeMailer);
```

## Criterios de decisión y trampas
### Cómo decidir
- Inyección por constructor siempre; los campos finales dejan claro lo que la clase necesita.
- Si un constructor recibe demasiadas dependencias, la clase hace demasiado.
### Trampas frecuentes
- Inyección por campo: dependencias ocultas y pruebas que necesitan el contenedor.
- Dependencias circulares «resueltas» con inyección perezosa.
- Servicios con estado mutable compartido entre peticiones.
- Localizadores de servicios estáticos.
- `@Autowired` por costumbre en constructores únicos.
### Evidencia
- Las clases se pueden instanciar en una prueba unitaria sin Spring.

## Checklist de revisión
- [ ] Ningún `@Autowired` en campos o setters.
- [ ] Campos `final`, constructor explícito, sin Lombok.
- [ ] Sin `getBean` ni ciclos; `allow-circular-references` ausente.
- [ ] Beans con pocas dependencias.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: `@Autowired` sobre campo | 1 | `policies/semgrep/spring-field-injection.yaml` |
| Revisión de cohesión (nº de dependencias) | 3 | agente `code-reviewer` |

> Estado: reglas probadas con `semgrep --test` (casos en `tests/semgrep/`); detectan patrones sintácticos, no flujos de datos.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `project-layout`, `domain-events-in-spring`, `solid`, `testing-slices`.
- Fuentes oficiales: Spring Framework Reference, "Dependency Injection" (docs.spring.io).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
