---
name: generics-and-api-design
description: Usar al diseñar APIs públicas Java, interfaces, genéricos, builders y firmas de métodos para que sean pequeñas, seguras en tipos y evolucionables.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Genéricos y diseño de APIs

## Cuándo aplicar y cuándo no
- Aplica a interfaces de módulo, puertos, librerías internas y cualquier tipo público usado fuera de su paquete.
- No aplica a clases privadas de implementación ni a código de un solo uso.

## Reglas
- **MUST** minimizar la superficie pública: paquete-privado por defecto, `public` solo para la API del módulo.
- **MUST NOT** usar tipos crudos (`List` sin parámetro) ni `@SuppressWarnings("unchecked")` sin comentario que justifique la seguridad.
- **MUST** aplicar PECS: `? extends T` para productores, `? super T` para consumidores; **MUST NOT** devolver tipos con comodines.
- **MUST** devolver tipos específicos y aceptar tipos generales (`Collection<? extends Item>` entrada, `List<Item>` salida).
- **SHOULD** limitar los parámetros a 3-4; con más, usar un record de parámetros o un builder explícito (sin Lombok).
- **MUST NOT** usar parámetros booleanos que cambien el comportamiento (`save(order, true)`); usar dos métodos o un enum.
- **MUST NOT** devolver arrays ni `null` como "sin resultado" (ver `null-safety`).
- **SHOULD** preferir composición a herencia; marcar `final` o `sealed` lo que no se diseñó para extender.
- **SHOULD** que las interfaces sean pequeñas y con un propósito (segregación); no crear interfaz para cada clase sin segundo implementador.
- **MUST** documentar con Javadoc el contrato (precondiciones, excepciones, hilo-seguridad) de la API pública.
- **MUST** tratar los cambios incompatibles de API como cambio mayor (ver `backward-compatibility-rules`).

## Por qué
Cada elemento público es un compromiso futuro. Los booleanos opacos en el sitio de llamada ilegibles ocultan errores. PECS evita copiar o castear colecciones. Los tipos crudos desactivan el chequeo del compilador y trasladan el error a un `ClassCastException` en ejecución.

## Ejemplos
### Mal
```java
public List process(List items, boolean async, boolean audit, String mode, int retries) { ... }
String name = (String) rawList.get(0);
```
### Bien
```java
public record ProcessOptions(ExecutionMode mode, boolean audit, int retries) {
    public static ProcessOptions defaults() { return new ProcessOptions(ExecutionMode.SYNC, false, 3); }
}
public List<Result> process(Collection<? extends Item> items, ProcessOptions options) { ... }

public static <T> void copy(List<? extends T> src, List<? super T> dst) {
    dst.addAll(src);
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Diseña la API para quien la usa: pocos tipos, nombres claros, sin parámetros booleanos ambiguos.
- Genéricos acotados (`? extends`, `? super`) solo cuando aportan seguridad real al llamante; si complican la firma, simplifica.
- Una interfaz pública es un compromiso: añade con cuidado y retira con un plazo.
### Trampas frecuentes
- Firmas con comodines anidados ilegibles.
- Tipos crudos (`List` sin parámetro).
- Devolver tipos concretos de implementación (`ArrayList`).
- Métodos con más de cuatro parámetros del mismo tipo.
- Exponer tipos de una librería de terceros en tu API pública.
### Evidencia
- Un ejemplo de uso de cada API pública compila como parte de las pruebas.

## Checklist de revisión
- [ ] Solo lo necesario es `public`.
- [ ] Sin tipos crudos ni `unchecked` sin justificar.
- [ ] Sin parámetros booleanos ambiguos ni listas largas de parámetros.
- [ ] Javadoc con el contrato de la API pública.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Compilador con `-Xlint:rawtypes,unchecked` y `-Werror` (en el proyecto generado) | 1 | `pom.xml` del proyecto generado (pendiente) |
| Reglas ArchUnit de visibilidad entre módulos | 1 | `policies/archunit/` (pendiente) |
| Revisión de API | 3 | agente `code-reviewer` (pendiente de definir) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `null-safety`, `immutability-and-value-objects`, `backward-compatibility-rules`, `solid`, `code-style-and-naming`.
- Fuentes: Effective Java (Bloch), ítems de genéricos y diseño de métodos (libro); Java Tutorials "Generics" — no verificado en línea.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
