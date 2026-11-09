---
name: workflow-bpm
description: "Usar al introducir procesos de larga duración, aprobaciones humanas o BPMN (Camunda/Flowable) en lugar de máquinas de estado ad hoc."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Workflow y BPM (Camunda / Flowable)

## Cuándo aplicar y cuándo no
- Aplica a procesos con esperas humanas, temporizadores, compensaciones o auditoría de pasos que los negocios quieren ver como diagrama.
- No aplica a flujos cortos y síncronos, ni a coreografía simple entre servicios (usar eventos/sagas, ver `sagas`).

## Reglas
- **MUST** decidir el motor por licencia antes de adoptarlo (D16, sin licencias de pago por defecto). Camunda 8 self-managed usa licencia propietaria y exige Enterprise para producción según https://docs.camunda.io/docs/reference/licenses/ (2026-11-07). Camunda 7 CE y Flowable OSS: licencia y estado de mantenimiento.
- **MUST** mantener el motor tras una interfaz propia (`ApprovalProcessPort`); el dominio no importa clases del motor.
- **MUST** versionar los `.bpmn` en el repo y migrar instancias en vuelo de forma explícita.
- **MUST** hacer idempotentes los service tasks (pueden reejecutarse tras fallo).
- **MUST NOT** meter reglas de negocio complejas en expresiones del BPMN; delegarlas a código testeado o `rules-engines`.
- **MUST NOT** compartir la BD del motor con tablas de negocio sin esquema separado.
- **SHOULD** usar correlación por `businessKey` y no guardar datos personales en variables de proceso.
- **SHOULD** definir timeouts y boundary events para tareas humanas.

## Por qué
Un motor BPM añade operación (jobs, incidentes, migraciones). Se justifica solo si la visibilidad del proceso y las esperas largas pesan más. Las variables de proceso persisten en historial: ahí se filtra PII fácilmente.

## Ejemplos
### Mal
```java
// Lógica del motor dispersa en el dominio
@Service class OrderService { @Autowired ProcessEngine engine; /* ... */ }
```
### Bien
```java
public interface ApprovalProcessPort {
    String start(String businessKey, ApprovalRequest request);
    void complete(String taskId, Decision decision);
}
// Adaptador en infrastructure/workflow; el dominio solo ve el puerto.
```
```java
// Service task idempotente
public void execute(String businessKey) {
    if (invoiceRepository.existsByBusinessKey(businessKey)) return;
    invoiceRepository.save(Invoice.forKey(businessKey));
}
```

## Checklist de revisión
- [ ] Licencia del motor revisada y aceptada.
- [ ] Dominio aislado del motor por un puerto.
- [ ] BPMN versionado, plan de migración de instancias.
- [ ] Service tasks idempotentes, sin PII en variables.
- [ ] Alerta de incidentes/jobs fallidos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: el dominio no depende de paquetes del motor | 1 | pendiente (`policies/archunit/`) |
| Revisión de licencia y diseño | 3 | revisión humana (ADR) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sagas`, `rules-engines`, `idempotency-keys`, `pii-and-data-classification`.
- Fuentes: Camunda licencias (2026-11-07). Flowable. Local: el motor corre en contenedor; sin HA de AWS.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
