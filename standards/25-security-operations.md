# Estándares · 25-security-operations

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## dast-and-attack-simulation

- **MUST** definir el objetivo solo en un plan versionado (`zap-plan.yaml`) con `includePaths` y exclusiones; nunca aceptar la URL por parámetro libre.
- **MUST** ejecutar el escaneo activo únicamente contra entornos propios con datos sintéticos; en producción solo el escaneo pasivo/baseline.
- **MUST** autenticar el escaneo con una cuenta de prueba dedicada y de privilegio mínimo, cuyas credenciales vengan del gestor de secretos del CI.
- **MUST** importar la definición OpenAPI para cubrir endpoints de API además del spider.
- **MUST** tratar el informe como entrada del registro de vulnerabilidades: hallazgos nuevos de severidad alta rompen el pipeline de la rama principal; el resto se registra.
- **SHOULD** usar el Automation Framework de ZAP (`-autorun` con YAML) en lugar de scripts ad hoc; ver jobs `openapi`, `spider`, `activeScan`, `report`.
- **SHOULD** limitar la tasa de peticiones y la duración para no degradar el entorno compartido.
- **SHOULD** mantener alertas de falsos positivos con filtros (`alertFilter`) justificados y con caducidad.
- **MUST NOT** ejecutar fuzzing o escaneo activo contra dependencias SaaS ni contra el IdP compartido.

## penetration-testing-program

- **MUST** disponer de un documento de autorización firmado antes de cualquier prueba: alcance (dominios, IPs, cuentas, entornos), exclusiones, ventana horaria, contactos de emergencia, tipo de prueba (caja negra/gris/blanca) y reglas de compromiso (RoE).
- **MUST** preferir un entorno de staging con datos sintéticos; si se prueba producción, acordar límites (sin denegación de servicio, sin exfiltración real de datos, sin ingeniería social salvo autorización expresa).
- **MUST** confirmar la titularidad: si el sistema está en un proveedor cloud, comprobar su política vigente de pruebas de seguridad (TODO-VERIFY por proveedor).
- **MUST** definir un canal de parada inmediata y un contacto del SOC/on-call informado de la ventana.
- **MUST** exigir informe con hallazgo, evidencia reproducible, impacto, severidad y recomendación, más un resumen ejecutivo.
- **MUST** abrir cada hallazgo en el registro de `vulnerability-management-program` con SLA y programar un retest.
- **SHOULD** basar la metodología en referencias públicas (OWASP WSTG, NIST SP 800-115, PTES) y en ASVS para el nivel de cobertura.
- **SHOULD** rotar proveedor o equipo cada pocos ciclos y combinar con pruebas internas continuas (DAST, SAST).
- **MUST NOT** almacenar credenciales o datos extraídos durante la prueba fuera del repositorio cifrado acordado; destruirlos al cerrar.
- **MUST NOT** ampliar el alcance durante la prueba sin adenda firmada.

## vulnerability-management-program

- **MUST** mantener un inventario de activos y componentes (SBOM por servicio) como entrada: sin inventario no hay cobertura medible.
- **MUST** priorizar por riesgo real, no solo por CVSS: combinar severidad, explotabilidad conocida (catálogo KEV de CISA, puntuación EPSS), exposición (internet/interno) y criticidad del dato.
- **MUST** fijar SLAs de remediación por prioridad y registrarlos en un documento versionado; ejemplo de partida: crítica explotada 7 días, alta 30, media 90, baja siguiente ciclo (valores a ajustar y aprobar por el responsable de seguridad).
- **MUST** gestionar excepciones con ticket, justificación, control compensatorio, responsable y fecha de caducidad; nunca excepciones indefinidas.
- **MUST** deduplicar hallazgos en un único registro (ID, activo, fuente, estado, fecha de detección, fecha límite).
- **SHOULD** usar VEX (estado "not_affected" con justificación) para descartar falsos positivos de dependencias de forma auditable.
- **SHOULD** medir: tiempo medio de remediación por prioridad, % dentro de SLA, antigüedad del backlog, cobertura de activos escaneados.
- **MUST NOT** cerrar un hallazgo sin verificar el arreglo con un reescaneo.
- **MUST NOT** ocultar fallos de SLA: se reportan a dirección con la misma periodicidad que los éxitos.
