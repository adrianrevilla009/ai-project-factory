---
name: bug-bounty-and-disclosure
description: "Usar al definir política de divulgación de vulnerabilidades (security.txt, VDP) o un programa de bug bounty, incluyendo triaje, safe harbor y plazos."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Divulgación de vulnerabilidades y bug bounty

## Cuándo aplicar y cuándo no
- Aplica a organizaciones que exponen servicios a internet y deben ofrecer un canal para que terceros reporten fallos.
- No aplica a pruebas internas contratadas (ver `penetration-testing-program`). Un bug bounty es una decisión de negocio; la política de divulgación (VDP) es el mínimo.

## Reglas
- **MUST** publicar un canal de reporte en `/.well-known/security.txt` con `Contact` y `Expires` (RFC 9116), más enlace a la política.
- **MUST** redactar una política con: sistemas dentro y fuera de alcance, acciones prohibidas (DoS, ingeniería social, acceso a datos de terceros), formato del reporte y compromiso de respuesta.
- **MUST** incluir cláusula de safe harbor revisada por asesoría jurídica (texto legal: borrador por confirmar).
- **MUST** definir tiempos de servicio: acuse en pocos días, triaje con severidad, comunicación de estado y plazo de corrección; los valores concretos los fija el programa (ejemplo: acuse 3 días, triaje 10).
- **MUST** enrutar los reportes válidos al registro de `vulnerability-management-program` con SLA, y cerrar el ciclo con el reportero.
- **MUST** canalizar reportes por un buzón/herramienta dedicada con acceso restringido; los detalles son confidenciales hasta la corrección.
- **SHOULD** empezar con VDP sin recompensas y pasar a bounty (privado, luego público) cuando haya capacidad de triaje.
- **SHOULD** coordinar divulgación pública con un plazo acordado (referencia: ISO/IEC 29147 y 30111).
- **MUST NOT** emprender acciones legales contra investigadores que actúen de buena fe dentro de la política.
- **MUST NOT** prometer recompensas sin presupuesto y baremo publicados.

## Por qué
Sin canal, los hallazgos acaban en redes sociales o en el mercado negro. Un buen programa convierte investigadores externos en un sensor barato, pero solo si el equipo puede triar y corregir con rapidez; un bounty sin capacidad de respuesta daña la reputación.

## Ejemplos
### Mal
```text
Contacto: formulario genérico de soporte, sin política ni fecha de caducidad.
```
### Bien
```text
# https://www.example.com/.well-known/security.txt
Contact: mailto:security@example.com
Expires: 2027-06-30T00:00:00.000Z
Policy: https://www.example.com/security/disclosure-policy
Preferred-Languages: es, en
```
Campos `Contact`, `Expires`, `Policy`, `Preferred-Languages` definidos en RFC 9116.

## Checklist de revisión
- [ ] security.txt publicado, no caducado y servido por HTTPS.
- [ ] Política con alcance, exclusiones y safe harbor revisado por legal.
- [ ] Buzón de reportes con acceso restringido y SLA de respuesta.
- [ ] Flujo hacia el registro de vulnerabilidades y cierre con el reportero.
- [ ] Presupuesto y baremo definidos si hay recompensas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Comprobación de que `security.txt` existe y su `Expires` no ha vencido | 1 | pendiente (check en CI del proyecto generado) |
| Revisión legal de la política y safe harbor | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `vulnerability-management-program`, `incident-management-and-postmortems`, `penetration-testing-program`.
- Fuentes: RFC 9116 (rfc-editor.org/rfc/rfc9116); ISO/IEC 29147 y 30111.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
