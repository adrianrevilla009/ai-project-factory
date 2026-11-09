---
name: gatling-load-testing
description: "Usar al elegir Gatling como alternativa a JMeter para pruebas de carga como código, y al escribir simulaciones con modelo abierto y criterios derivados del SLO."
metadata:
  block: "08-testing-quality"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Gatling: pruebas de carga como código

## Cuándo aplicar y cuándo no
- Aplica cuando el equipo prefiere escribir las pruebas de carga como código (Java, Kotlin o TypeScript) con revisión por PR, o cuando la interfaz gráfica de JMeter estorba.
- No aplica por defecto: la herramienta de carga acordada es JMeter (D19, `performance-testing`). Mantener dos sin motivo duplica esfuerzo.
- No sustituye a las pruebas de rendimiento de componentes ni al análisis de perfiles de la JVM.

## Reglas
- **MUST** decidir en un ADR si se usa Gatling en lugar de JMeter, con el motivo; no hay dos herramientas para lo mismo sin una razón.
- **MUST** usar la edición Community, bajo Apache 2.0 y gratuita también para uso comercial; los protocolos de gRPC, MQTT, GraphQL y JDBC son módulos aparte con otra licencia (Gatling Enterprise Component License) y no se asumen (D16; verificado el 2026-11-09 en la documentación de licencias de Gatling).
- **MUST NOT** depender de funciones de Gatling Enterprise (informes en vivo, comparación de ejecuciones, equipos y SSO, generación distribuida) por defecto.
- **MUST** guardar las simulaciones como código en el repositorio, junto al criterio de aceptación que verifican.
- **SHOULD** usar un modelo de carga abierto (llegadas por segundo) para servicios que reciben tráfico independiente de las respuestas; un modelo cerrado (usuarios concurrentes) solo si los usuarios reales esperan a la respuesta antes de actuar.
- **MUST** definir aserciones derivadas del SLO (tasa de error y latencia) para que el job falle por sí mismo, sin interpretar a mano un informe.
- **MUST** calentar el sistema y descartar ese tramo del análisis; comparar con la línea base anterior y guardar el commit, el entorno y la configuración.
- **MUST NOT** ejecutar contra producción ni contra servicios de terceros reales.
- **SHOULD** ejecutar un smoke corto en cada PR y las pruebas completas en un entorno dedicado (`performance-gate`).

## Por qué
La carga como código se revisa, se versiona y se reproduce, que es justo lo que falla con las pruebas montadas a mano en una interfaz gráfica. El modelo de carga importa más de lo que parece: con un modelo cerrado, un sistema lento recibe menos peticiones y la prueba lo hace parecer mejor de lo que es.

## Ejemplos
### Mal
```java
// Sin aserciones, carga cerrada que oculta la degradación y objetivo fijo en el código
setUp(scn.injectClosed(constantConcurrentUsers(50).during(60))
    .protocols(http.baseUrl("https://prod.example.com")));
```
### Bien
```java
public class OrdersSimulation extends Simulation {
  HttpProtocolBuilder protocol = http.baseUrl(System.getProperty("baseUrl"));

  ScenarioBuilder createOrder = scenario("crear pedido")
      .exec(http("POST /orders").post("/orders")
          .header("Content-Type", "application/json")
          .body(StringBody("{\"sku\":\"A-1\",\"quantity\":1}"))
          .check(status().is(201)));

  {
    setUp(createOrder.injectOpen(
            rampUsersPerSec(1).to(20).during(60),     // calentamiento
            constantUsersPerSec(20).during(300)))     // carga esperada
        .protocols(protocol)
        .assertions(global().failedRequests().percent().lt(1.0));
  }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- ¿Ya tienes JMeter en uso y funciona? Quédate: el cambio solo compensa si el problema es mantener y revisar las pruebas.
- ¿Equipo de Java, Kotlin o TypeScript que quiere pruebas como código? Gatling encaja.
- ¿Necesitas gRPC, MQTT, GraphQL o JDBC? Comprueba su licencia antes: no son Apache 2.0.
- ¿Necesitas generación distribuida desde varias máquinas? Es de la edición de pago; valora ejecutar varias instancias tú mismo o usar JMeter distribuido.
### Trampas frecuentes
- Modelo cerrado que oculta la degradación (la «omisión coordinada»).
- Medir con un generador saturado.
- Datos de prueba que caben todos en caché.
- Medias en lugar de percentiles.
- Resultados sin versión del código ni del entorno, imposibles de comparar.
- Una simulación sin aserciones: nadie sabe si «pasó».
### Evidencia
- Las aserciones de la simulación enlazan al SLO y el informe de cada ejecución se guarda con el commit y el entorno.

## Checklist de revisión
- [ ] Hay un ADR que justifica Gatling en lugar de JMeter.
- [ ] Solo se usan módulos con licencia compatible con D16.
- [ ] El modelo de carga se corresponde con cómo llegan las peticiones reales.
- [ ] Las aserciones salen del SLO.
- [ ] No se ejecuta contra producción ni contra terceros reales.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Aserciones de la simulación que fallan el job | 2 | pipeline del proyecto generado (pendiente) |
| Revisión del modelo de carga y de los criterios | 3 | agente `performance` |
| Decisión de apartarse de JMeter | 4 | persona responsable de arquitectura, por ADR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `performance-testing`, `performance-gate`, `slo-sli-error-budgets`, `capacity-and-load-modeling`, `test-data-management`.
- Fuentes: documentación y licencias de Gatling (consultadas el 2026-11-09); el plugin de Maven y el módulo de gráficos existen en Maven Central.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
