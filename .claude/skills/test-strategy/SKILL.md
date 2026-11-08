---
name: test-strategy
description: "Usar al definir o revisar qué tipos de test escribir, en qué proporción y en qué fase del pipeline se ejecutan (pirámide, slices, E2E mínimos)."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Estrategia de testing

## Cuándo aplicar y cuándo no
- Aplica al arrancar un servicio, al planificar una historia y al revisar un PR que añade tests o los elimina.
- No aplica al detalle de una técnica concreta (ver `unit-testing-java`, `integration-testing-testcontainers`, `e2e-testing`).

## Reglas
- **MUST** seguir una pirámide: muchos tests unitarios rápidos, algunos de integración con dependencias reales, muy pocos E2E.
- **MUST** asignar cada test a una capa explícita por convención de nombre: `*Test` (unitario, Surefire) y `*IT` (integración, Failsafe).
- **MUST** que los tests unitarios no toquen red, disco ni reloj real y corran en segundos.
- **MUST** probar cada riesgo en la capa más barata que lo detecta (regla de negocio: unitario; mapeo SQL: integración con BD real; contrato entre servicios: contract test).
- **SHOULD** usar slices de Spring (`@WebMvcTest`, `@DataJpaTest`) antes que `@SpringBootTest` completo (ver `testing-slices`).
- **SHOULD** definir en el `README` del proyecto qué se ejecuta en cada fase: PR (unit + IT + estática), nightly (mutación, rendimiento corto), release (E2E, carga).
- **MUST NOT** compensar tests unitarios ausentes con E2E lentos.
- **MUST NOT** borrar o ignorar (`@Disabled`) un test para poner el build en verde sin ticket enlazado.

## Por qué
El coste de un test crece con su alcance: tiempo, fragilidad y diagnóstico. Una pirámide invertida (mucho E2E) da builds de 40 minutos y fallos aleatorios que el equipo aprende a ignorar. Poner cada riesgo en la capa más barata mantiene el feedback rápido y los fallos localizables.

## Ejemplos
### Mal
```text
src/test: 3 unit tests, 120 @SpringBootTest que levantan todo el contexto,
40 escenarios Selenium. Build PR: 35 min. Nadie sabe qué cubre cada uno.
```
### Bien
```text
domain/      -> *Test puro JUnit 5 + AssertJ (ms)
web/         -> @WebMvcTest (slice)
persistence/ -> *IT con Testcontainers PostgreSQL
integraciones-> contract tests (Pact) + WireMock
E2E          -> 5-10 recorridos críticos, solo en release
```
```xml
<!-- Surefire corre *Test; Failsafe corre *IT en la fase verify (versiones: comprobar al fijar la versión) -->
<plugin><artifactId>maven-surefire-plugin</artifactId></plugin>
<plugin><artifactId>maven-failsafe-plugin</artifactId></plugin>
```

## Checklist de revisión
- [ ] Cada cambio de comportamiento tiene test en la capa más barata posible.
- [ ] Unit e IT se separan por convención de nombre y fase.
- [ ] No hay `@Disabled` sin ticket ni `Thread.sleep` (usar Awaitility).
- [ ] El tiempo de la fase PR está dentro del presupuesto acordado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep contra `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |
| Hook que exige tests verdes al parar | 2 | `.claude/hooks/stop/` (pendiente, Oleada 1) |
| Revisión de proporción y capa de los tests | 3 | agente `code-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `testing-slices`, `unit-testing-java`, `integration-testing-testcontainers`, `contract-testing`, `e2e-testing`, `coverage-policy`.
- Fuentes: documentación de Maven Surefire/Failsafe y Spring Boot Testing (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
