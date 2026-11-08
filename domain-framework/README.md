# domain-framework

Método para que un agente entienda el dominio de negocio antes de planificar, sin inventarlo.

- `discovery-protocol.md` — pasos de descubrimiento: glosario, contextos delimitados, eventos, procesos.
- `domain-profile.schema.yaml` — estructura del perfil de dominio que se genera.
- `assumptions-register.schema.yaml` — registro de supuestos; todo lo que no tenga fuente va aquí, con impacto y responsable.
- `validation-checklist.md` — comprobaciones del Gate 0; exige validación de un experto de negocio, con nombre y fecha.

Lo produce el agente `domain-analyst`; lo valida una persona.
