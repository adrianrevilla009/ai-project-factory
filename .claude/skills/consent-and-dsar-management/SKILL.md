---
name: consent-and-dsar-management
description: "Usar al implementar registro de consentimientos, preferencias y solicitudes de derechos de interesados (acceso, rectificación, supresión, portabilidad) con plazos y trazabilidad. Borrador legal."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Consentimientos y gestión de DSAR

> Borrador técnico. Los plazos, bases legales y excepciones son por confirmar con asesoría legal/DPO y con la fuente oficial (texto del RGPD, Reglamento UE 2016/679, arts. 7, 12, 15-20). No es asesoramiento jurídico.

## Cuándo aplicar y cuándo no
- Aplica a banners/preferencias de consentimiento, registro de bases legales y flujos de solicitudes de acceso, rectificación, supresión, limitación, portabilidad y oposición (DSAR).
- No aplica al diseño de la política de privacidad ni a la decisión de la base legal (humana, DPO).

## Reglas
- **MUST** guardar cada consentimiento como evento inmutable: sujeto, finalidad, versión del texto, valor (otorgado/retirado), marca temporal, canal y prueba (IP/UA solo si la finalidad lo justifica).
- **MUST** modelar el consentimiento por finalidad, nunca un único "acepto todo" ni casillas premarcadas.
- **MUST** hacer la retirada tan fácil como el otorgamiento y propagarla a los servicios consumidores por evento (outbox).
- **MUST** modelar el DSAR como un caso con máquina de estados (`RECEIVED`, `IDENTITY_VERIFIED`, `IN_PROGRESS`, `COMPLETED`, `REJECTED`), fecha límite calculada y alerta previa al vencimiento (plazo base de un mes según el art. 12; comprobar prórrogas).
- **MUST** verificar la identidad del solicitante antes de entregar datos.
- **MUST** mantener un inventario de dónde vive cada dato personal (ver `pii-and-data-classification`); sin inventario no hay DSAR fiable.
- **MUST** responder el acceso/portabilidad en formato estructurado (JSON/CSV) y entregarlo por canal seguro con enlace caducable.
- **MUST** ejecutar la supresión por orquestación a todos los sistemas, con excepciones (obligación legal, litigio) registradas y justificadas; en eventos inmutables usar crypto-shredding (`gdpr-and-immutable-events`).
- **MUST NOT** guardar en el log de DSAR los datos entregados; solo metadatos y hash de la entrega.
- **SHOULD** exponer métricas: casos abiertos, edad máxima, casos próximos a vencer.

## Por qué
El regulador y el interesado piden prueba: qué se consintió, cuándo y con qué texto, y que se respondió a tiempo. Un evento inmutable por cambio permite reconstruir el estado en cualquier fecha. La orquestación explícita evita el fallo habitual: borrar en la base principal y olvidar índices, cachés, copias y analítica.

## Ejemplos
### Mal
```sql
-- solo el último estado, sin versión de texto ni historial
UPDATE users SET marketing_ok = true WHERE id = 42;
```
### Bien
```sql
CREATE TABLE consent_event (
  id            UUID PRIMARY KEY,
  subject_id    UUID        NOT NULL,
  purpose       TEXT        NOT NULL,   -- e.g. 'marketing_email'
  policy_version TEXT       NOT NULL,
  granted       BOOLEAN     NOT NULL,
  channel       TEXT        NOT NULL,
  occurred_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE dsar_case (
  id          UUID PRIMARY KEY,
  subject_id  UUID NOT NULL,
  type        TEXT NOT NULL,            -- ACCESS | ERASURE | PORTABILITY ...
  status      TEXT NOT NULL,
  received_at TIMESTAMPTZ NOT NULL,
  due_at      TIMESTAMPTZ NOT NULL
);
```

## Checklist de revisión
- [ ] Consentimiento por finalidad, versionado y append-only.
- [ ] Retirada propagada a consumidores.
- [ ] DSAR con estados, `due_at` y alertas.
- [ ] Identidad verificada antes de entregar datos.
- [ ] Supresión orquestada en todos los almacenes, con excepciones justificadas.
- [ ] Legal/DPO ha confirmado plazos y bases legales.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de modelo de datos y flujo DSAR | 3 | agente `code-reviewer` |
| Validación legal de plazos y bases | 4 | revisión humana (DPO) |
| Regla automática de tablas con PII sin inventario | 1 | pendiente |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `pii-and-data-classification`, `gdpr-and-immutable-events`, `gdpr-in-the-lake`, `data-privacy-in-db`, `retention-and-cleanup`, `outbox-and-cdc`.
- Fuentes: Reglamento (UE) 2016/679 en EUR-Lex, consultado 2026-11-07 (borrador; confirmar artículos y plazos con asesoría).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
