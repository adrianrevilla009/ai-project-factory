# Estándares · 30-engineering-process

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## adr

- **MUST** escribir un ADR por decisión, numerado secuencialmente `NNNN-titulo-en-kebab.md`, y no reutilizar números.
- **MUST** incluir: `**Estado:**` (`propuesto`, `aceptado`, `rechazado`, `sustituido`), `**Fecha:**`, Contexto, Decisión, Por qué (opciones consideradas y descartadas) y Consecuencias (incluidas las negativas).
- **MUST** tratar los ADR aceptados como inmutables: para cambiar de criterio, crear un ADR nuevo y marcar el anterior `sustituido` con enlace cruzado.
- **MUST** enlazar el ADR desde el PR que lo implementa y desde la documentación afectada.
- **MUST** documentar al menos dos alternativas reales y por qué se descartaron.
- **SHOULD** incluir cómo se verificará la decisión (test de arquitectura, policy, métrica).
- **SHOULD** redactarlo en el mismo PR que el cambio o antes, nunca meses después.
- **MUST NOT** editar el cuerpo de un ADR aceptado para "corregir" la historia; solo estado y enlaces.
- **MUST NOT** contradecir una decisión cerrada D1-D27 sin ADR que la sustituya y aprobación humana.

## api-docs

- **MUST** que la fuente de verdad sea el fichero de contrato versionado (`docs/api/openapi.yaml`, `docs/api/asyncapi.yaml`), no una wiki.
- **MUST** que cada operación tenga `summary`, `operationId` único, respuestas de error documentadas y al menos un ejemplo realista.
- **MUST** documentar autenticación (esquema OIDC/Keycloak), paginación, idempotencia y límites cuando existan.
- **MUST** que los cambios incompatibles pasen por `api-versioning-deprecation` y se anoten en el changelog.
- **SHOULD** generar el spec desde el código solo si se revisa el diff en el PR; con contract-first, generar el código desde el spec.
- **SHOULD** publicar el spec renderizado (Swagger UI/Redoc) junto al servicio en entornos no productivos.
- **MUST NOT** exponer la UI de documentación sin autenticación en entornos compartidos.
- **MUST NOT** incluir datos personales reales en ejemplos.

## c4-and-arc42

- **MUST** mantener como mínimo los niveles C4 1 (System Context) y 2 (Container); el nivel 3 (Component) solo para contenedores complejos. El nivel 4 (Code) no se dibuja a mano: se genera o se omite.
- **MUST** que cada elemento del diagrama tenga nombre, tecnología y responsabilidad en una línea; cada flecha, un verbo y el protocolo (`HTTPS/JSON`, `Kafka`).
- **MUST** usar arc42 como esqueleto de documentación: contexto y alcance, restricciones, estrategia de solución, vista de bloques, vista de ejecución, vista de despliegue, conceptos transversales, decisiones (enlazar ADR), calidad, riesgos, glosario.
- **MUST** que la sección de decisiones de arc42 enlace a los ADR en lugar de duplicarlos.
- **MUST** que los diagramas sean código versionado (ver `diagrams-as-code`) y se actualicen en el mismo PR que el cambio.
- **SHOULD** añadir un diagrama de despliegue C4 que distinga lo local (kind/k3d) de lo previsto para AWS, indicando que lo segundo está "preparado para AWS, no verificado en real".
- **SHOULD** añadir diagramas dinámicos solo para flujos críticos (alta de pedido, pago).
- **MUST NOT** representar en el diagrama de despliegue servicios AWS sin equivalente local sin marcar qué no se reproduce en local (ver matriz de paridad).
- **MUST NOT** mezclar niveles de abstracción en un mismo diagrama.

## changelog-release-notes

- **MUST** mantener `CHANGELOG.md` con sección `Unreleased` arriba y versiones con fecha ISO `YYYY-MM-DD`.
- **MUST** agrupar por tipo: Added, Changed, Deprecated, Removed, Fixed, Security.
- **MUST** que los cambios incompatibles lleven la etiqueta `BREAKING`, el impacto y los pasos de migración.
- **MUST** que las notas de release se escriban para el consumidor (qué cambia para él), no para el desarrollador.
- **SHOULD** generar el borrador desde Conventional Commits y editarlo a mano antes de publicar.
- **SHOULD** enlazar PRs, ADRs y entradas del contrato OpenAPI afectadas.
- **MUST NOT** volcar el `git log` crudo como changelog.
- **MUST NOT** publicar notas que afirmen verificación en AWS real; la fábrica no despliega.

## conventional-commits

- **MUST** usar la forma `<tipo>[(ámbito)][!]: <descripción>` en imperativo, minúsculas, sin punto final, ≤ 72 caracteres.
- **MUST** usar tipos del conjunto: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. La especificación solo exige `feat` y `fix`; el resto es convención del equipo.
- **MUST** marcar cambios incompatibles con `!` antes de los dos puntos y/o un pie `BREAKING CHANGE: <descripción>` (en mayúsculas).
- **MUST** hacer commits pequeños y atómicos: una pieza lógica por commit, el build en verde en cada uno.
- **SHOULD** usar el cuerpo para el porqué (no el qué) y pies para `Refs: PAY-123` / `Closes #45`.
- **SHOULD** usar como ámbito el módulo o bounded context (`feat(billing): ...`).
- **MUST NOT** mezclar refactor y cambio funcional en un mismo commit.
- **MUST NOT** usar mensajes vacíos de significado (`wip`, `fix stuff`, `changes`).

## definition-of-ready-and-done

### Definition of Ready (para empezar)
- **MUST** tener valor/objetivo claro y criterios de aceptación verificables (ver `requirements-engineering`).
- **MUST** tener requisitos no funcionales relevantes explícitos (latencia, seguridad, datos personales).
- **MUST** estar dimensionada para caber en una iteración corta; si no, dividirla.
- **MUST** tener dependencias identificadas (otros equipos, contratos, datos) y sin bloqueo abierto.
- **SHOULD** tener un enfoque técnico acordado; si implica decisión de arquitectura, existe ADR en `proposed`.
### Definition of Done (para cerrar)
- **MUST** cumplir todos los criterios de aceptación con tests automáticos que los demuestren.
- **MUST** pasar el pipeline completo: build, tests, lint, SAST, dependencias, cobertura según `coverage-policy`.
- **MUST** estar revisada y aprobada por PR (ver `pr-rules`).
- **MUST** tener docs actualizadas (README vivo, API docs, runbook si cambia la operación, ADR si hubo decisión) y entrada de changelog.
- **MUST** tener observabilidad mínima: logs estructurados, métricas y alertas afectadas revisadas.
- **MUST NOT** declarar "hecho" con deuda oculta: lo que se difiere se registra en el `tech-debt-register`.
- **MUST NOT** afirmar madurez de nube superior a "preparado para AWS, no verificado en real" (ADR-0004).

## diagrams-as-code

- **MUST** guardar la fuente del diagrama como texto en el repo, junto a la documentación que ilustra; una imagen exportada sin fuente no se acepta.
- **MUST** usar herramientas de licencia abierta y gratuita (D16): Mermaid, PlantUML, Structurizr DSL (Structurizr Lite/CLI).
- **MUST** elegir una herramienta por tipo de diagrama y documentarlo en el README de docs; no mezclar tres sintaxis para lo mismo.
- **MUST** que cada diagrama tenga título, leyenda si usa colores/formas y nivel de abstracción único (ver `c4-and-arc42`).
- **MUST** mantener el diagrama en el mismo PR que el cambio que lo invalida.
- **SHOULD** preferir Mermaid en Markdown cuando basta, porque GitHub lo renderiza sin pasos extra.
- **SHOULD** modelar C4 una sola vez (modelo Structurizr) y derivar varias vistas, en lugar de redibujar.
- **SHOULD** limitar el diagrama a ~15 elementos; dividir en vistas si crece.
- **MUST NOT** incluir secretos, IPs reales ni identificadores de cuenta en diagramas.
- **MUST NOT** dibujar infraestructura AWS como "verificada"; se rotula "preparado para AWS, no verificado en real".

## domain-discovery

- **MUST** descubrir primero los **eventos de dominio** en pasado (`PedidoPagado`, `ReembolsoSolicitado`) en una línea temporal, antes de hablar de tablas o servicios.
- **MUST** pasar por las tres fases: Big Picture (eventos y tensiones), Process Modeling (comandos, actores, políticas, read models) y Software Design (agregados y límites).
- **MUST** capturar **hotspots** (dudas, conflictos, reglas desconocidas) como preguntas abiertas con dueño, no resolverlos a mano alzada.
- **MUST** derivar candidatos a bounded context y agregados a partir de los clústeres de eventos y de cambios de lenguaje, no de la organización actual por defecto.
- **MUST** registrar el **lenguaje ubicuo** en un glosario versionado; un término = un significado por contexto.
- **SHOULD** invitar a negocio, desarrollo y operación; sin expertos de dominio, el resultado es una hipótesis.
- **SHOULD** convertir los resultados en artefactos del repo: glosario, mapa de contextos, eventos candidatos, ADR de los límites elegidos.
- **MUST NOT** tratar el resultado como diseño final: los límites se revisan con evidencia.
- **MUST NOT** introducir normativa como hecho: lo regulatorio detectado se anota "por confirmar con fuente oficial".

## git-workflow

- **MUST** tener una única rama de integración (`main`), siempre desplegable en el sentido de que su pipeline está en verde.
- **MUST** trabajar en ramas cortas (objetivo: menos de 2 días de vida, un cambio pequeño) que se integran a `main` mediante PR.
- **MUST** nombrar ramas `<tipo>/<id-ticket>-<slug>` (`feat/PAY-123-refund-endpoint`), con los mismos tipos que `conventional-commits`.
- **MUST** ocultar trabajo incompleto detrás de un feature flag, no detrás de una rama larga viva.
- **MUST** hacer rebase de la rama sobre `main` antes del PR; el merge se hace en modo squash (un commit convencional por PR).
- **MUST NOT** hacer force push a `main` ni a ramas compartidas; **MUST NOT** `git reset --hard` sin revisar qué se pierde.
- **MUST NOT** commitear secretos, binarios generados ni `target/` / `node_modules/`.
- **SHOULD** proteger `main`: PR obligatorio, checks requeridos, sin push directo, historial lineal.
- **SHOULD** etiquetar releases con tags SemVer anotados `vMAJOR.MINOR.PATCH` desde `main` (o `release/*` si se soportan varias versiones).
- **SHOULD** borrar la rama tras el merge.

## lessons-learned-and-retro

- **MUST** hacer postmortem escrito para todo incidente con impacto a usuarios o pérdida de datos, en un plazo acordado (p. ej. 5 días laborables).
- **MUST** formato sin culpables: se analizan sistemas y decisiones, no personas.
- **MUST** incluir línea temporal, impacto, causas contribuyentes, qué funcionó, qué no y qué dio suerte.
- **MUST** que cada acción tenga dueño, fecha y enlace a su ticket; se revisan en la siguiente retro.
- **MUST** que las lecciones reutilizables actualicen skills, runbooks, checklist de PRR o ADRs; si no cambia nada, no se aprendió.
- **SHOULD** publicar los postmortems en `docs/postmortems/` para consulta del equipo.
- **MUST NOT** incluir secretos, datos personales ni nombres de personas como causa.
- **MUST NOT** cerrar la retro sin acciones concretas o sin decidir explícitamente no actuar.

## library-selection-and-tech-radar-process

- **MUST** comprobar primero si el stack ya aprobado cubre la necesidad (Java + Spring Boot + Maven, Terraform, Istio, Keycloak.); las decisiones cerradas D1-D27 no se reabren aquí.
- **MUST** evaluar: necesidad real, madurez y actividad del mantenimiento, licencia, seguridad (CVEs, SBOM), tamaño de dependencias transitivas, integración con el stack y coste de salida.
- **MUST** licencia compatible y sin coste por defecto (D16); las licencias de pago o copyleft fuerte requieren decisión humana en ADR.
- **MUST** registrar la decisión en un ADR cuando la librería sea estructural o difícil de reemplazar.
- **MUST NOT** añadir Lombok (D27) ni una librería que duplique una ya aprobada.
- **MUST** clasificar en el radar: Adopt, Trial, Assess, Hold, con fecha y dueño; revisar el radar cada trimestre.
- **SHOULD** probar con una prueba de concepto acotada antes de pasar a Adopt.
- **SHOULD** aislar la librería tras un puerto/adaptador para reducir el coste de salida.
- **MUST NOT** fijar versiones por criterio propio: usar el BOM y verificar en documentación oficial.

## living-readme

- **MUST** incluir: qué es y para quién, requisitos previos con versiones, cómo arrancar en local, cómo ejecutar tests, cómo contribuir y dónde está el resto de docs.
- **MUST** que cada comando del README se pueda copiar y ejecutar tal cual desde un clon limpio.
- **MUST** actualizar el README en el mismo PR que cambia un comando, puerto, variable o requisito.
- **MUST** declarar la madurez de la parte de infraestructura: "preparado para AWS, no verificado en real" cuando aplique, y qué NO se reproduce en local.
- **SHOULD** limitar el README a una pantalla y media; el detalle va a `docs/` con enlaces.
- **SHOULD** enlazar ADRs y el contrato OpenAPI en vez de copiar su contenido.
- **MUST NOT** incluir secretos, ni siquiera de ejemplo que parezcan reales (usar `changeme`/`example`).
- **MUST NOT** duplicar información que ya tiene fuente de verdad (versión en `pom.xml`, puertos en `compose.yaml`).

## pr-rules

- **MUST** abrir PR pequeño y con un único propósito: orientativamente < 400 líneas cambiadas (sin código generado ni lockfiles).
- **MUST** titular el PR en formato Conventional Commits (será el mensaje del squash).
- **MUST** incluir en la descripción: qué cambia, por qué, cómo se probó, riesgos/rollback y enlace al ticket.
- **MUST** tener los checks requeridos en verde (build, tests, lint, SAST, escaneo de dependencias) antes de pedir revisión.
- **MUST** tener al menos una aprobación de alguien distinto del autor; cambios de seguridad, datos o IaC requieren revisor de ese ámbito.
- **MUST** resolver (no ignorar) todos los comentarios bloqueantes antes del merge.
- **MUST** actualizar docs/ADR/changelog afectados en el mismo PR.
- **MUST NOT** hacer merge con checks fallando, con `--no-verify` previo ni saltándose la protección de rama.
- **MUST NOT** aprobar un PR propio ni aprobar sin haber leído el diff completo.
- **SHOULD** usar PR en borrador para pedir feedback temprano.
- **SHOULD** responder revisiones en menos de un día laborable.

## production-readiness-review

- **MUST** ejecutar la PRR como checklist escrita, con evidencia enlazada por ítem (dashboard, test, runbook, ADR), no como conversación.
- **MUST** cubrir: SLOs y alertas por síntoma, logs/trazas/métricas, health checks, límites y timeouts, degradación controlada, backup y restore probado, capacidad, seguridad (authn/z, secretos, SBOM), runbooks y guardia asignada, plan de rollback.
- **MUST** que cada ítem sea Cumple / No cumple / No aplica (con motivo); un "No cumple" crítico bloquea el lanzamiento o requiere riesgo aceptado en `risk-register`.
- **MUST** que la aprobación sea humana; el agente prepara la checklist, nunca la firma (gates humanos).
- **MUST** etiquetar la madurez de la infraestructura: "validada estáticamente" / "preparado para AWS, no verificado en real". La fábrica nunca despliega (ADR-0004).
- **SHOULD** repetir la PRR ante cambios mayores y cada año.
- **MUST NOT** afirmar que algo está verificado en AWS real ni usar fórmulas de "listo" sin evidencia.

## requirements-engineering

- **MUST** redactar historias como `Como <rol> quiero <capacidad> para <beneficio>`; el beneficio no puede omitirse.
- **MUST** que cada historia cumpla INVEST: Independiente, Negociable, Valiosa, Estimable, Pequeña (Small), Testeable.
- **MUST** expresar criterios de aceptación como escenarios Gherkin (`Given/When/Then`) en lenguaje de dominio, sin UI ni SQL.
- **MUST** incluir al menos un escenario de error o borde por historia, no solo el camino feliz.
- **MUST** definir los NFR con número y método de medida: "p95 < 300 ms bajo 200 rps", no "rápido".
- **MUST** trazar cada requisito a un identificador (`REQ-PAY-012`) enlazado a historia, test y, si aplica, ADR.
- **SHOULD** listar supuestos y preguntas abiertas con responsable y fecha; las respuestas pendientes bloquean el DoR.
- **SHOULD** cubrir categorías de NFR: rendimiento, disponibilidad, seguridad, privacidad, auditoría, accesibilidad, operabilidad.
- **MUST NOT** inventar requisitos legales o normativos: marcarlos "borrador por confirmar" con fuente oficial y fecha.
- **MUST NOT** mezclar solución técnica en el requisito ("usar Redis") salvo restricción real, documentada como tal.

## rfc-process

- **MUST** escribir el RFC en un documento versionado (`docs/rfc/NNNN-titulo.md`) con: resumen, motivación, propuesta, alternativas, impacto, plan de migración/rollback, riesgos y preguntas abiertas.
- **MUST** indicar estado (`borrador`, `en revisión`, `aceptado`, `rechazado`, `retirado`), autor, revisores obligatorios y fecha límite de comentarios.
- **MUST** dar un plazo de revisión mínimo (p. ej. 5 días laborables) y avisar a todos los equipos afectados.
- **MUST** que los comentarios bloqueantes se resuelvan o se registren como objeción explícita con respuesta.
- **MUST** nombrar a quien decide (persona o comité); el consenso se busca, pero la decisión tiene dueño.
- **MUST** al aceptar, crear los ADR derivados y enlazar RFC y ADR entre sí.
- **SHOULD** prototipar o medir cuando haya hipótesis de rendimiento o coste, en lugar de opinar.
- **MUST NOT** implementar a gran escala antes de aceptar el RFC (spikes acotados sí).
- **MUST NOT** usar un RFC para saltarse una decisión cerrada D1-D27 sin ADR sustitutorio y aprobación humana.

## risk-register

- **MUST** mantener un único registro versionado en el repo (`docs/risks/risk-register.md` o YAML) y revisarlo en cada hito.
- **MUST** que cada riesgo tenga id estable, descripción causa-evento-consecuencia, probabilidad, impacto, dueño nominal, respuesta (evitar, mitigar, transferir, aceptar) y fecha de revisión.
- **MUST** que aceptar un riesgo alto sea una decisión humana registrada con fecha de caducidad.
- **MUST** vincular los riesgos con ADRs, PRR y gates cuando condicionen una decisión.
- **SHOULD** usar escala simple (1-3 o 1-5) y puntuación = probabilidad x impacto, definida una vez.
- **SHOULD** cerrar riesgos con motivo (materializado, mitigado, obsoleto), sin borrarlos.
- **MUST NOT** dejar riesgos sin dueño ni fecha de revisión.
- **MUST NOT** registrar secretos ni datos personales.

## runbooks

- **MUST** un runbook por alerta que pagina; la alerta lleva la anotación `runbook_url`.
- **MUST** estructura fija: síntoma, impacto, diagnóstico (comandos de solo lectura primero), mitigación, verificación de que se resolvió, escalado, enlaces.
- **MUST** indicar para cada paso destructivo o irreversible una confirmación explícita y cómo deshacerlo.
- **MUST** indicar dueño, fecha de última ejecución/prueba y entorno al que aplica.
- **SHOULD** probar el runbook en un simulacro (game day, ver `dr-tabletop-exercises`) al menos una vez por año.
- **SHOULD** enlazar los dashboards y consultas exactas, no "mirar métricas".
- **MUST NOT** incluir secretos; referenciar el gestor de secretos.
- **MUST NOT** afirmar que un procedimiento de AWS está verificado: la fábrica no despliega; marcar "preparado para AWS, no verificado en real".

## tech-debt-register

- **MUST** registrar cada atajo consciente en `docs/tech-debt/register.md` (o issues con etiqueta `tech-debt`) en el mismo PR que lo introduce.
- **MUST** que cada entrada incluya: id, descripción, motivo del atajo, coste de pagarla, "interés" (qué duele mientras exista), dueño y fecha de revisión.
- **MUST** que los `TODO`/`FIXME` del código referencien un id del registro (`TODO(TD-012)`).
- **SHOULD** reservar capacidad fija por iteración para pagar deuda (p. ej. 10-20 %, acordado con producto).
- **SHOULD** priorizar por interés y riesgo, no por antigüedad.
- **MUST NOT** usar "deuda técnica" para ocultar trabajo incompleto que incumple la `definition-of-ready-and-done`.
- **MUST NOT** desactivar reglas de calidad (Semgrep, ArchUnit) sin entrada de deuda con caducidad.
- **MUST NOT** dejar entradas sin dueño.
