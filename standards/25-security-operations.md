# Estándares · 25-security-operations

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## bug-bounty-and-disclosure

- **MUST** publicar un canal de reporte en `/.well-known/security.txt` con `Contact` y `Expires` (RFC 9116), más enlace a la política.
- **MUST** redactar una política con: sistemas dentro y fuera de alcance, acciones prohibidas (DoS, ingeniería social, acceso a datos de terceros), formato del reporte y compromiso de respuesta.
- **MUST** incluir cláusula de safe harbor revisada por asesoría jurídica (texto legal: borrador por confirmar).
- **MUST** definir tiempos de servicio: acuse en pocos días, triaje con severidad, comunicación de estado y plazo de corrección; los valores concretos los fija el programa (ejemplo: acuse 3 días, triaje 10).
- **MUST** enrutar los reportes válidos al registro de `vulnerability-management-program` con SLA, y cerrar el ciclo con el reportero.
- **MUST** canalizar reportes por un buzón/herramienta dedicada con acceso restringido; los detalles son confidenciales hasta la corrección.
- **SHOULD** empezar con VDP sin recompensas y pasar a bounty (privado, luego público) cuando haya capacidad de triaje.
- **SHOULD** coordinar divulgación pública con un plazo acordado (referencia: ISO/IEC 29147 y 30111; comprobar contenido).
- **MUST NOT** emprender acciones legales contra investigadores que actúen de buena fe dentro de la política.
- **MUST NOT** prometer recompensas sin presupuesto y baremo publicados.

## cspm-and-posture

- **MUST** escanear tanto el código (IaC/manifiestos, en CI) como el estado vivo (cuentas y clústeres, periódicamente): el segundo detecta deriva y cambios manuales.
- **MUST** usar herramientas con licencia abierta por defecto: Prowler (cloud, Apache-2.0) y Kubescape (Kubernetes, Apache-2.0); documentar cualquier alternativa de pago como excepción.
- **MUST** mapear cada hallazgo a un framework de referencia (CIS Benchmark, NSA-CISA, MITRE ATT&CK) para priorizar y dar evidencia.
- **MUST** asignar a cada hallazgo propietario, severidad y SLA de corrección (ver `vulnerability-sla-and-incident-response`).
- **MUST** gestionar excepciones con caducidad, justificación y aprobador; una excepción sin fecha es un hallazgo ignorado.
- **SHOULD** ejecutar el escaneo con credenciales de solo lectura dedicadas, nunca con administrador.
- **SHOULD** medir tendencia (hallazgos abiertos por severidad y antigüedad), no solo el recuento puntual.
- **MUST NOT** almacenar informes con identificadores de cuenta o secretos en repositorios públicos.
- **MUST NOT** declarar "cumple CIS" a partir de un escaneo parcial; indicar versión del benchmark y alcance.

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

## encryption-standards

- **MUST** mantener un catálogo corto de algoritmos aprobados y prohibir el resto: AES-GCM (128/256) o ChaCha20-Poly1305 para cifrado autenticado; SHA-256 o superior para hash; RSA >= 3072 o curvas P-256/Ed25519 para firma e intercambio; Argon2id, scrypt o bcrypt para contraseñas.
- **MUST NOT** usar MD5, SHA-1 para seguridad, DES/3DES, RC4, ECB, RSA < 2048 ni PKCS#1 v1.5 para cifrado nuevo.
- **MUST** exigir TLS 1.2 como mínimo y preferir 1.3 en todo tráfico externo e interno (referencia: NIST SP 800-52 Rev. 2, comprobar al fijar la versión).
- **MUST** cifrar en reposo todos los datos con clasificación sensible, con claves gestionadas por KMS/Vault, nunca en el repositorio ni en la imagen.
- **MUST** usar librerías estándar (JCA/Bouncy Castle revisado) y APIs de alto nivel; MUST NOT implementar primitivas propias ni reutilizar IV/nonce.
- **SHOULD** preferir módulos con validación FIPS 140-3 si lo exige el cliente o la normativa (comprobar requisito concreto).
- **SHOULD** inventariar el uso de criptografía (CBOM simple) para poder migrar; planificar agilidad criptográfica: algoritmo configurable, no cableado.
- **SHOULD** preparar la migración post-cuántica: los estándares FIPS 203 (ML-KEM), 204 (ML-DSA) y 205 (SLH-DSA) se publicaron en 2024; adoptar en modo híbrido cuando el ecosistema (TLS, JDK) lo soporte (comprobar soporte en el JDK usado).
- **MUST** revisar el catálogo al menos una vez al año.

## hardening-baselines

- **MUST** elegir una línea base publicada (CIS Benchmark de la tecnología y versión concretas) y registrar cuál y qué perfil (Level 1 / Level 2).
- **MUST** aplicar la línea base como código (imagen construida, módulo Terraform, manifiesto), no como lista manual que se ejecuta una vez.
- **MUST** documentar cada desviación: control, motivo, riesgo aceptado, aprobador y fecha de revisión.
- **MUST** medir conformidad de forma automática y periódica, y tratar la regresión como hallazgo con SLA.
- **MUST** usar imágenes mínimas (distroless o equivalente) y usuario no root en contenedores.
- **SHOULD** empezar por Level 1 (impacto operativo bajo) y adoptar Level 2 donde el riesgo lo justifique.
- **SHOULD** versionar la línea base y revisarla cuando el benchmark o la tecnología cambien de versión mayor.
- **MUST NOT** aplicar un benchmark entero a ciegas en producción sin probarlo antes en un entorno equivalente.
- **MUST NOT** afirmar conformidad total con CIS; indicar el porcentaje de controles pasados y las excepciones.

## iam-governance-and-pam

- **MUST** tener una fuente de verdad de identidades (IdP corporativo, p. ej. Keycloak, D-decisiones de la fábrica) y provisionar/retirar accesos desde ella, no a mano en cada sistema.
- **MUST** automatizar joiner-mover-leaver: alta con rol base, cambio de puesto retira accesos anteriores, baja revoca en el mismo día laborable.
- **MUST** recertificar accesos privilegiados al menos trimestralmente y el resto al menos anualmente; el revisor es el responsable del negocio, no quien tiene el acceso.
- **MUST** separar funciones: quien solicita, quien aprueba y quien ejecuta un cambio crítico no pueden ser la misma persona.
- **MUST** usar cuentas administrativas nominales y separadas de la cuenta diaria; MFA resistente a phishing donde sea posible.
- **MUST** dar acceso privilegiado just-in-time, con caducidad y motivo registrado (ver `break-glass-and-jit-access`).
- **MUST NOT** compartir cuentas administrativas ni dejar credenciales de servicio sin propietario asignado.
- **SHOULD** inventariar identidades no humanas (service accounts, tokens, claves) con propietario y fecha de rotación.
- **SHOULD** grabar o auditar las sesiones privilegiadas y enviar los registros a un almacén inmutable (ver `audit-trail-and-security-logging`).
- **MUST NOT** conceder `Action: "*"` sobre `Resource: "*"` en políticas IAM salvo rol break-glass documentado.

## ids-ips-waf-edr

- **MUST** desplegar cada control primero en modo detección/solo registro, medir falsos positivos con tráfico real y solo después activar bloqueo.
- **MUST** elegir cada capa por la amenaza que cubre: WAF para HTTP (reglas OWASP CRS sobre ModSecurity/Coraza), IDS/IPS para tráfico de red (p. ej. Suricata), EDR/runtime para hosts y contenedores (p. ej. Falco; Wazuh como agente), en OSS por defecto.
- **MUST** enviar los eventos de todos los controles al SIEM (ver `siem-and-detection-engineering`).
- **MUST** versionar reglas y excepciones (exclusiones por ruta/regla) con justificación y caducidad; nada de desactivar una regla "porque molesta".
- **MUST** definir un procedimiento de bypass de emergencia y quién puede activarlo.
- **SHOULD** ajustar el nivel de paranoia del WAF por aplicación y probarlo en CI con peticiones legítimas de contratos OpenAPI.
- **SHOULD** actualizar firmas/reglas de forma automática con revisión del diff.
- **MUST NOT** considerar el WAF como arreglo de una vulnerabilidad: la vulnerabilidad sigue en el registro con su SLA.
- **MUST NOT** inspeccionar tráfico cifrado de usuarios sin base legal y aviso (privacidad: borrador por confirmar).

## incident-response-playbooks-and-forensics

- **MUST** basar el ciclo de respuesta en un marco publicado: NIST SP 800-61 Rev. 3 (abril 2025, sustituye a Rev. 2) alineado con CSF 2.0.
- **MUST** tener un playbook por escenario probable (credencial filtrada, ransomware, fuga de datos, cuenta cloud comprometida) con roles, decisiones y criterios de escalado.
- **MUST** definir quién declara el incidente, quién lidera, quién comunica y quién decide contención; incluir contactos fuera de banda.
- **MUST** preservar evidencia antes de erradicar: copiar logs, snapshots y memoria cuando sea viable, con hash y registro de quién la manejó (cadena de custodia).
- **MUST** guardar la evidencia en almacenamiento de solo escritura y acceso restringido.
- **MUST** consultar a legales/DPO desde el inicio si hay datos personales: los plazos de notificación son un borrador por confirmar con fuente oficial (p. ej. RGPD, 72 h a la autoridad; comprobar texto vigente).
- **SHOULD** ejecutar simulacros (tabletop) al menos una vez al año y actualizar los playbooks con lo aprendido.
- **SHOULD** sincronizar relojes (NTP) y conservar logs suficientes para reconstruir la línea temporal.
- **MUST NOT** apagar o reconstruir un sistema afectado sin haber decidido qué evidencia se pierde.
- **MUST NOT** usar canales posiblemente comprometidos (correo corporativo) para coordinar un incidente de cuenta comprometida.

## penetration-testing-program

- **MUST** disponer de un documento de autorización firmado antes de cualquier prueba: alcance (dominios, IPs, cuentas, entornos), exclusiones, ventana horaria, contactos de emergencia, tipo de prueba (caja negra/gris/blanca) y reglas de compromiso (RoE).
- **MUST** preferir un entorno de staging con datos sintéticos; si se prueba producción, acordar límites (sin denegación de servicio, sin exfiltración real de datos, sin ingeniería social salvo autorización expresa).
- **MUST** confirmar la titularidad: si el sistema está en un proveedor cloud, comprobar su política vigente de pruebas de seguridad (comprobar por proveedor).
- **MUST** definir un canal de parada inmediata y un contacto del SOC/on-call informado de la ventana.
- **MUST** exigir informe con hallazgo, evidencia reproducible, impacto, severidad y recomendación, más un resumen ejecutivo.
- **MUST** abrir cada hallazgo en el registro de `vulnerability-management-program` con SLA y programar un retest.
- **SHOULD** basar la metodología en referencias públicas (OWASP WSTG, NIST SP 800-115, PTES) y en ASVS para el nivel de cobertura.
- **SHOULD** rotar proveedor o equipo cada pocos ciclos y combinar con pruebas internas continuas (DAST, SAST).
- **MUST NOT** almacenar credenciales o datos extraídos durante la prueba fuera del repositorio cifrado acordado; destruirlos al cerrar.
- **MUST NOT** ampliar el alcance durante la prueba sin adenda firmada.

## pki-and-certificate-lifecycle

- **MUST** automatizar emisión y renovación (ACME con cert-manager en Kubernetes, o la CA gestionada del proveedor); la renovación manual no escala.
- **MUST** asumir validez cada vez más corta: la CA/Browser Forum aprobó (ballot SC-081v3, 2025-04-11) máximos de 200 días desde 2026-03-15, 100 días desde 2027-03-15 y 47 días desde 2029-03-15 para certificados TLS públicos (fuente secundaria; comprobar en cabforum.org).
- **MUST** mantener un inventario de certificados con dueño, entorno, fecha de caducidad y método de renovación, y alertar con antelación (p. ej. 30/14/7 días) sobre cualquier certificado sin renovar.
- **MUST** proteger la clave privada de la CA raíz fuera de línea; emitir con CA intermedias de ámbito limitado (por entorno o dominio).
- **MUST** generar claves en el sistema que las usa (CSR) y no copiarlas por correo ni tickets; claves privadas nunca en Git.
- **MUST** definir revocación y respuesta ante compromiso: quién revoca, en cuánto tiempo y cómo se reemite.
- **SHOULD** usar certificados de vida corta para mTLS interno (la malla Istio emite y rota los suyos) en lugar de certificados manuales.
- **SHOULD** monitorizar Certificate Transparency de los dominios propios para detectar emisiones no autorizadas.
- **SHOULD** usar registros CAA para limitar qué CA puede emitir para el dominio.
- **MUST NOT** usar certificados autofirmados en producción para tráfico entre servicios sin CA de confianza distribuida; MUST NOT desactivar la validación de certificados en clientes.

## ransomware-resilience

- **MUST** mantener copias inmutables (WORM) en una cuenta/dominio de administración distinto del de producción, de modo que unas credenciales de producción comprometidas no puedan borrarlas (ver `backup-vault-immutability-and-restore-tests`).
- **MUST** seguir el principio 3-2-1 como mínimo: 3 copias, 2 medios o dominios distintos, 1 aislada/inmutable.
- **MUST** probar la restauración completa de los sistemas críticos periódicamente y medir el RTO real frente al objetivo (ver `tier-model-and-rpo-rto`).
- **MUST** limitar privilegios y movimiento lateral: segmentación de red, cuentas administrativas separadas, MFA, sin credenciales de dominio en estaciones normales.
- **MUST** proteger el plano de control de las copias con MFA y aprobación de dos personas para borrar o acortar la retención.
- **MUST** mantener un plan de recuperación priorizado (qué se restaura primero) y reconstruir desde imágenes y código conocidos, no desde sistemas sospechosos.
- **SHOULD** vigilar señales tempranas: cifrado masivo de ficheros, borrado de snapshots, desactivación de agentes de seguridad.
- **SHOULD** conservar el plan de comunicación y los contactos legales fuera de los sistemas que pueden quedar cifrados.
- **MUST NOT** basar la estrategia en pagar el rescate; decisión y asesoramiento legal corresponden a la dirección y a los asesores, no a este skill.
- **MUST NOT** montar los repositorios de copia como volúmenes escribibles desde las cargas de producción.

## security-champions-and-training

- **MUST** nombrar al menos un champion por equipo de producto, voluntario y con tiempo explícito (p. ej. 10 % del sprint), con respaldo de su responsable.
- **MUST** definir el rol: punto de contacto con seguridad, primer revisor en cambios sensibles, difusión de hallazgos; el champion NO es el único responsable de la seguridad del equipo.
- **MUST** dar formación específica por rol y stack (desarrolladores Java/React, SRE, QA), con ejercicios prácticos sobre vulnerabilidades reales de esa pila.
- **MUST** incluir en el onboarding: gestión de secretos, revisión de dependencias, reporte de incidentes y canal para dudas.
- **MUST** realimentar la formación con datos: los hallazgos recurrentes (SAST, revisiones, incidentes) determinan los temas.
- **SHOULD** reunir a los champions con cadencia regular (mensual o quincenal) y publicar notas.
- **SHOULD** reconocer la labor: objetivos, evaluación de desempeño o visibilidad, no solo trabajo extra.
- **SHOULD** medir con indicadores de resultado: tiempo de corrección, repetición de tipos de vulnerabilidad, participación en revisiones; no solo asistencia a cursos.
- **MUST NOT** usar entornos o datos de producción para ejercicios prácticos; solo laboratorios propios y aislados.
- **MUST NOT** culpar a individuos por errores reportados; el reporte temprano debe ser seguro (cultura sin culpa).

## siem-and-detection-engineering

- **MUST** partir de casos de uso de detección ligados a amenazas del registro de riesgos, no de "activar todas las reglas del proveedor".
- **MUST** centralizar, como mínimo: autenticación (IdP, Keycloak), auditoría cloud/Kubernetes, WAF/ingress, EDR y accesos privilegiados, con reloj sincronizado y esquema común.
- **MUST** gestionar las reglas como código: repositorio, revisión por PR, versión, owner y enlace a técnica ATT&CK cuando aplique.
- **MUST** probar cada regla con eventos de ejemplo positivos y negativos antes de promoverla (tests en CI).
- **MUST** documentar para cada alerta: qué significa, qué mirar, cómo triar y cuándo escalar (runbook enlazado).
- **MUST** medir calidad: tasa de falsos positivos, tiempo hasta triaje, cobertura de técnicas; desactivar o reajustar reglas ruidosas.
- **SHOULD** usar un formato portable (Sigma) y convertirlo al motor concreto; en local, alternativa OSS como Wazuh u OpenSearch (sin licencias de pago por defecto, D16).
- **SHOULD** definir retención por tipo de log según requisitos legales (borrador por confirmar) y proteger los logs contra manipulación.
- **MUST NOT** registrar secretos, tokens ni datos personales innecesarios en los eventos centralizados.
- **MUST NOT** dejar alertas sin dueño: toda alerta pagina a alguien o se elimina.

## third-party-and-supply-chain-risk

- **MUST** mantener un inventario de terceros con: servicio, datos que trata, criticidad, propietario interno y fecha de última revisión.
- **MUST** clasificar a cada tercero por nivel de riesgo (p. ej. crítico / alto / normal) y ajustar a ello la profundidad de la due diligence.
- **MUST** pedir evidencias proporcionales antes de contratar: informes de auditoría independientes (p. ej. SOC 2, ISO/IEC 27001) y cuestionario de seguridad; validar alcance y fechas, no solo la existencia del certificado.
- **MUST** incluir en contrato: notificación de incidentes en plazo definido, derecho de auditoría o evidencias, tratamiento y devolución/borrado de datos, subencargados, cumplimiento normativo aplicable (borrador por confirmar con asesoría legal).
- **MUST** documentar un plan de salida para terceros críticos (portabilidad de datos, alternativa, tiempo estimado).
- **MUST** revisar terceros críticos al menos anualmente y ante incidentes públicos del proveedor.
- **SHOULD** limitar el acceso del tercero al mínimo necesario, con credenciales propias, caducidad y auditoría (ver `iam-governance-and-pam`).
- **SHOULD** suscribirse a los avisos de seguridad y a la página de estado de los proveedores críticos.
- **MUST NOT** compartir datos de producción o personales con un tercero sin base contractual y revisión de privacidad.
- **MUST NOT** aceptar el certificado del proveedor como sustituto de controles propios sobre los datos que le enviamos (cifrado, minimización).

## threat-intel-and-risk-register

- **MUST** elegir un conjunto pequeño de fuentes relevantes para la pila (avisos de proveedores, catálogo CISA KEV de vulnerabilidades explotadas, avisos del CERT nacional) y asignar un responsable de triarlas.
- **MUST** convertir inteligencia en acción concreta: cada aviso relevante genera una tarea (parchear, regla de detección, bloqueo) o se descarta con motivo anotado.
- **MUST** mantener un registro de riesgos único con: descripción, activo, probabilidad, impacto, propietario de negocio, tratamiento (mitigar, aceptar, transferir, evitar), fecha de revisión.
- **MUST** que un riesgo aceptado lo apruebe quien responde del negocio afectado, con fecha de caducidad.
- **MUST** revisar el registro al menos trimestralmente y tras cada incidente significativo.
- **SHOULD** usar escalas coherentes y documentadas (p. ej. 1-5) y la misma metodología en todo el registro.
- **SHOULD** vincular cada riesgo a controles y a evidencias (hallazgos CSPM, resultados de pruebas).
- **MUST NOT** tratar indicadores de compromiso de fuentes no verificadas como verdad: se validan antes de bloquear.
- **MUST NOT** incluir secretos ni datos personales en el registro de riesgos.

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
