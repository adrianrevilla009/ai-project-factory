---
name: connascence-and-coupling
description: "Usar al evaluar acoplamiento entre módulos o servicios, o al decidir dónde está justificado el acoplamiento fuerte; guía el diseño de dependencias."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Connascence y acoplamiento

## Cuándo aplicar y cuándo no
- Aplica al revisar dependencias entre paquetes/módulos/servicios, al trocear un componente o al justificar duplicar código frente a compartirlo.
- No aplica como métrica automática única; es una herramienta de razonamiento, no una puntuación.

## Reglas
- **MUST** evaluar cada dependencia por fuerza, grado y localidad: acoplamiento fuerte solo si los elementos están cerca (mismo módulo/equipo).
- **MUST** convertir connascence fuerte a débil al cruzar fronteras: de nombre/tipo (estática) a contrato explícito; evitar de ejecución, temporalidad y valor entre servicios.
- **MUST NOT** compartir entre contexts clases de dominio, entidades JPA ni esquemas de BD (ver `ddd-strategic`).
- **MUST NOT** crear ciclos de dependencia entre paquetes o módulos.
- **SHOULD** preferir duplicar un DTO pequeño entre servicios antes que una librería compartida que obligue a desplegar a la vez.
- **SHOULD** reducir parámetros posicionales y literales mágicos (connascence de posición y de significado) con tipos y enums.
- **SHOULD** considerar acoplamiento temporal en llamadas síncronas en cadena; evaluar asincronía (ver `event-driven`).
- **SHOULD** registrar en ADR los acoplamientos fuertes aceptados y su razón.

## Por qué
No se trata de eliminar el acoplamiento sino de gestionarlo: el coste de cambio crece con la fuerza del acoplamiento y la distancia entre los elementos. Un `String` con significado oculto dentro de una clase es aceptable; el mismo entre dos servicios de equipos distintos es una avería esperando.

## Ejemplos
### Mal
```java
// Posición + significado entre servicios distintos
paymentClient.charge("42", 1999, "EUR", true, false);

// Entidad compartida en librería común
import com.acme.common.model.Customer;   // usada por 5 servicios
```
### Bien
```java
public record ChargeRequest(CustomerId customerId, Money amount, CaptureMode capture) {}
paymentClient.charge(new ChargeRequest(customerId, Money.eur(1999), CaptureMode.IMMEDIATE));
```
Orden de fuerza, de menor a mayor (resumen):
```text
Nombre < Tipo < Significado < Posición < Algoritmo   (estáticas, detectables al compilar/leer)
Ejecución < Temporalidad < Valor < Identidad          (dinámicas, difíciles de ver)
```
Criterio práctico: fuerte y cercano = OK; fuerte y lejano = rediseñar o ADR.

## Checklist de revisión
- [ ] No hay ciclos entre paquetes/módulos.
- [ ] Ningún modelo de dominio o entidad compartido entre contexts.
- [ ] Contratos entre servicios explícitos y versionados.
- [ ] Parámetros posicionales/mágicos sustituidos por tipos.
- [ ] Acoplamientos fuertes aceptados documentados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: ausencia de ciclos entre slices | 1 | pendiente: `policies/archunit/` (ver `layering-rules-archunit`) |
| dependency-cruiser para frontend | 1 | pendiente: `policies/frontend-boundaries/` |
| Revisión de acoplamiento en PR | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `solid`, `ddd-strategic`, `hexagonal`, `evolutionary-architecture-fitness-functions`.
- Fuentes: Page-Jones, "What Every Programmer Should Know About OO Design" (1995); connascence.io..
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
