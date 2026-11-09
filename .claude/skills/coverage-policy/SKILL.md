---
name: coverage-policy
description: "Usar al definir o revisar umbrales de cobertura (JaCoCo), exclusiones y cómo interpretar la cobertura en CI sin convertirla en objetivo vacío."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Política de cobertura

## Cuándo aplicar y cuándo no
- Aplica a la configuración de JaCoCo, quality gates y a la revisión de PRs que bajan la cobertura.
- No aplica como sustituto de calidad de aserciones: para eso, ver `mutation-testing`.

## Reglas
- **MUST** medir cobertura con JaCoCo en el build Maven y publicar el informe en CI.
- **MUST** exigir un umbral mínimo en el `check` de JaCoCo: sugerido 80 % de líneas y 70 % de ramas en dominio y aplicación (valores por confirmar por proyecto).
- **MUST** aplicar la regla "el código nuevo no baja la cobertura": cobertura del diff mínima 80 % (gate del analizador usado).
- **MUST NOT** bajar el umbral para que pase el build sin ADR o decisión registrada.
- **MUST NOT** escribir tests sin aserciones para subir el número.
- **MUST** documentar las exclusiones (DTOs puros, configuración, `main`, clases generadas) en el pom, nunca con anotaciones ad hoc dispersas.
- **SHOULD** exigir más en dominio (lógica) que en adaptadores finos.
- **SHOULD** combinar con mutation testing en el dominio crítico.

## Por qué
La cobertura es un indicador negativo: poca cobertura prueba que falta test; mucha no prueba que haya calidad. Un umbral con exclusiones explícitas evita la erosión silenciosa sin incentivar tests vacíos (ley de Goodhart).

## Ejemplos
### Mal
```java
@Test
void coverageBooster() {
    new OrderService(null, null).toString(); // sube líneas, no comprueba nada
}
```
### Bien
```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <!-- versión en el parent -->
  <executions>
    <execution><goals><goal>prepare-agent</goal></goals></execution>
    <execution>
      <id>report-and-check</id>
      <phase>verify</phase>
      <goals><goal>report</goal><goal>check</goal></goals>
      <configuration>
        <excludes><exclude>**/config/**</exclude><exclude>**/*Dto.class</exclude></excludes>
        <rules><rule><element>BUNDLE</element><limits>
          <limit><counter>LINE</counter><value>COVEREDRATIO</value><minimum>0.80</minimum></limit>
          <limit><counter>BRANCH</counter><value>COVEREDRATIO</value><minimum>0.70</minimum></limit>
        </limits></rule></rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

## Criterios de decisión y trampas
### Cómo decidir
- Umbral por capa: alto en dominio, bajo en configuración; añade cobertura de ramas y cobertura del diff para código nuevo.
- Excluye código generado con justificación explícita.
### Trampas frecuentes
- Convertir el número en el objetivo: acaba produciendo tests sin aserciones.
- Excluir lo difícil de probar.
- Mismo umbral para todo el repositorio.
- Creer que un 100 % de líneas prueba el comportamiento: combínalo con mutación en el dominio.
### Evidencia
- El informe de cobertura publicado en el PR y, para el dominio, el de mutación.

## Checklist de revisión
- [ ] `jacoco:check` activo con umbrales definidos.
- [ ] Exclusiones justificadas y centralizadas.
- [ ] El diff no baja la cobertura ni añade tests sin aserciones.
- [ ] Dominio crítico revisado con mutation testing.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `jacoco:check` falla el build `verify` | 1 | `pom.xml` del proyecto generado (se implementa en el proyecto generado, ADR-0038) |
| Hook que exige tests en verde al parar | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Gate de cobertura del diff en CI | 2 | pendiente (depende del analizador del proyecto) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `mutation-testing`, `test-strategy`, `static-analysis`, `unit-testing-java`.
- Fuentes: https://www.jacoco.org/jacoco/trunk/doc/check-mojo.html.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
