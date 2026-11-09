# Catálogo de antipatrones

Cada fila es algo que parece razonable y acaba costando caro. Qué verás, por qué duele y qué hacer en su lugar. Las reglas completas están en las skills enlazadas. El contrapunto está en [`patterns.md`](patterns.md).

## Código Java y concurrencia
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Capturar `Throwable` o tragar excepciones | Fallos silenciosos | Se pierde la causa y se oculta un estado roto | Capturar lo concreto, conservar la causa, traducir en el límite | `exceptions-and-error-handling` |
| Dinero con `double` | Céntimos que no cuadran | El binario no representa decimales exactos | `BigDecimal` o una clase de dinero | `time-and-money` |
| Comprobar y luego actuar sobre un mapa compartido | Corrupción esporádica | Dos hilos pasan la comprobación a la vez | Operaciones atómicas del mapa | `concurrent-collections`, `locks-and-synchronization` |
| Pools sin límite o hilos a mano | Caída por falta de memoria bajo carga | Sin tope ni cola, el sistema se ahoga | Pools acotados o hilos virtuales con límites | `threads-executors-and-pools`, `virtual-threads` |
| `Optional.get()` sin comprobar | Excepción en ejecución | Esconde la ausencia en vez de decidirla | `orElseThrow` con excepción de dominio | `null-safety` |
| Inyección por campo | Pruebas que necesitan el contenedor | Dependencias ocultas y estado mutable | Inyección por constructor | `dependency-injection-rules` |
| Abusar de Lombok | Código que depende de un procesador de anotaciones | Opaco para herramientas y revisores (ADR-0027) | Records y constructores explícitos | `no-lombok`, `immutability-and-value-objects` |

## Persistencia
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| N+1 consultas | Latencia que crece con los datos | Una consulta por fila | Fetch join, proyección o lote | `n-plus-one`, `joins-and-fetch-joins` |
| Relaciones a-uno `EAGER` | Cargas enormes sin querer | Se traen grafos completos siempre | `LAZY` y cargar lo necesario | `lazy-vs-eager` |
| Paginación con `OFFSET` profundo | Páginas lentas al final | La base recorre y descarta filas | Keyset | `pagination` |
| Concatenar SQL | Inyección | Datos tratados como código | Parámetros enlazados | `sql-injection-prevention` |
| Transacción abierta durante una llamada remota | Agotamiento del pool | Se retienen conexiones esperando a un tercero | Transacciones cortas, fuera la E/S | `transactions`, `connection-pooling` |
| Soltar o renombrar una columna en el mismo despliegue | Errores durante el rolling update | Las instancias antiguas siguen leyendo la columna | Expand/contract en varias versiones | `schema-migrations` |
| Entidad de BD como DTO de la API | Se filtran campos y se acopla el contrato al esquema | Un cambio interno rompe a los clientes | DTO y proyecciones | `projections-and-dtos` |
| Escritura doble (base y broker) | Datos y eventos que divergen | No hay atomicidad entre dos sistemas | Outbox | `outbox-and-cdc` |
| Una base compartida entre servicios | Despliegues acoplados | Nadie puede cambiar su esquema | Cada servicio con sus datos | `microservices-decision-guide`, `data-sync-pitfalls` |

## Arquitectura
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Microservicios prematuros (monolito distribuido) | Cambios que tocan siete servicios | Coste operativo sin independencia real | Monolito modular primero | `microservices-decision-guide`, `modular-monolith` |
| Event sourcing en todas partes | Complejidad sin beneficio | Proyecciones, versionado y supresión por cada agregado | Usarlo solo donde el evento es el negocio | `when-to-use-and-when-not` |
| Cadenas de llamadas síncronas | Disponibilidad que es el producto de todas | Un fallo se propaga en cascada | Eventos o aislamiento | `event-driven`, `resilience` |
| Dominio que importa el framework | No se puede probar sin contenedor | Se mezcla negocio e infraestructura | Puertos y adaptadores | `hexagonal`, `layering-rules-archunit` |
| Modelo anémico y servicios con toda la lógica | Reglas dispersas | Invariantes sin dueño | Agregados con comportamiento | `ddd-tactical` |

## APIs e integración
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Cambiar el contrato sin versionar | Clientes rotos tras un despliegue | Cambio incompatible silencioso | Versionado y deprecación con plazo | `api-versioning-deprecation`, `backward-compatibility-rules` |
| `200 OK` con el error en el cuerpo | Clientes que no detectan fallos | Rompe caché, métricas y reintentos | Códigos HTTP y Problem Details | `error-handling-problem-details`, `rest-design-guidelines` |
| Reintentos sin idempotencia | Cobros o pedidos duplicados | La misma petición se ejecuta varias veces | Claves de idempotencia | `idempotency-keys` |
| Webhook sin firma | Cualquiera puede inyectar eventos | No hay autenticidad | Firma HMAC y comparación en tiempo constante | `webhooks` |
| Mensajes venenosos reintentados sin fin | Un consumidor bloqueado | Una carga inválida detiene la cola | DLQ y alerta | `dlq-retries-poison-messages` |

## Seguridad
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Secretos en Git o en variables sin control | Credenciales filtradas | Quedan en el historial para siempre | Gestor de secretos y rotación | `secrets-management`, `secret-scanning-and-leak-response` |
| Tokens en `localStorage` | Robo por XSS | Cualquier script los lee | Cookie `HttpOnly` vía BFF | `jwt-and-sessions`, `security-frontend` |
| CORS con comodín y credenciales | Peticiones de orígenes ajenos | Se anula la política del navegador | Lista explícita de orígenes | `security-headers-cors-csrf` |
| Permisos IAM con comodines | Radio de impacto enorme | Una credencial lo permite todo | Mínimo privilegio | `cloud-iam-least-privilege` |
| Credenciales de administrador compartidas | Sin trazabilidad | No se sabe quién hizo qué | Acceso temporal y registrado | `break-glass-and-jit-access` |
| Confiar en la salida de un modelo | Inyección de prompts y datos expuestos | Texto del modelo tratado como orden | Validar, limitar y redactar | `llm-security`, `guardrails-and-pii-redaction` |

## Operación, Kubernetes y AWS
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Imágenes `latest` | Despliegues no reproducibles | No sabes qué versión corre | Etiqueta fija y digest | `container-images`, `docker-multistage` |
| Sin probes ni límites | Pods que se reinician o saturan el nodo | El orquestador no ve el estado real | Línea base de workloads | `workload-baseline` |
| `kubectl` manual en producción | Deriva entre Git y clúster | El estado real deja de ser reproducible | GitOps con autocorrección | `argo-cd`, `drift-and-self-heal-policy` |
| Afirmar «listo para producción en AWS» sin haberlo desplegado (honest-claims: ignore) | Falsa confianza | Un fallo se descubre en el primer `apply` real | Etiquetas de madurez honestas | `honest-claims-policy`, `maturity-labels` |
| Copias de seguridad que nadie ha restaurado | Descubres que no sirven cuando las necesitas | Una copia sin restauración probada no es una copia | Pruebas de restauración | `backup-vault-immutability-and-restore-tests` |
| Recuperación ante desastres sin ensayar | Procedimiento obsoleto | Nadie sabe ejecutarlo | Ejercicios de mesa y game days | `dr-tabletop-exercises`, `fault-injection-and-game-days` |
| Alertar por causas (CPU) en vez de por síntomas | Fatiga de alertas | Se ignora lo importante | Alertas por SLO | `alerting-symptom-based` |
| Etiquetas de métricas con cardinalidad alta | Coste y consultas lentas | Cada valor crea una serie nueva | Etiquetas acotadas | `cardinality-and-cost-governance` |
| Datos personales en los logs | Incidente de privacidad | Los logs se replican y se retienen | Redactar y clasificar | `structured-logging`, `pii-and-data-classification` |

## Entrega y calidad
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Ramas de larga vida | Fusiones dolorosas | La integración se pospone | Trunk-based y flags | `git-workflow` |
| Despliegues big-bang sin vuelta atrás | Incidentes largos | No se puede revertir con rapidez | Canary y plan de rollback | `canary-and-traffic-splitting`, `rollback-strategy` |
| Tolerar pruebas inestables | Nadie confía en el pipeline | Se ignoran los fallos reales | Cuarentena y corrección | `flaky-test-management` |
| La cobertura como objetivo | Pruebas que no comprueban nada | Se mide ejecución, no verificación | Mutación y revisión | `coverage-policy`, `mutation-testing` |
| `sleep` en las pruebas | Lentitud e inestabilidad | Tiempos arbitrarios | Esperas por condición | `concurrency-testing`, `flaky-test-management` |
| Mocks de todo | Pruebas verdes que no detectan nada | Se prueba el mock | Dependencias reales | `integration-testing-testcontainers` |
| Solo E2E con el camino feliz | Regresiones en los bordes | Cobertura ilusoria | Pirámide y casos límite | `test-strategy`, `e2e-testing` |

## Frontend
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Estado global para todo | Re-renderizados y acoplamiento | Cualquier cambio afecta a todo | Estado de servidor, URL y local | `state-management` |
| `div` con `onClick` | No usable con teclado ni lector de pantalla | Falla la accesibilidad | Elementos semánticos | `accessibility`, `component-patterns` |
| `dangerouslySetInnerHTML` con datos externos | XSS | Se ejecuta HTML no confiable | Sanear o evitar | `security-frontend` |
| Un paquete gigante | Carga inicial lenta | Se descarga todo | División por ruta y presupuesto de tamaño | `frontend-performance`, `routing-and-code-splitting` |

## Ingeniería con agentes
| Antipatrón | Síntoma | Por qué duele | En su lugar | Skills |
|---|---|---|---|---|
| Un agente que aprueba sus propios gates | Decisiones sin control humano | Se anula el sentido del gate | Registro firmado por una persona | `gate-protocol` |
| Afirmar sin evidencia | Resultados inventados | Nadie puede comprobarlos | Evidencia o aviso de que no se pudo comprobar | `verify-before-asserting` |
| `CLAUDE.md` enorme | El agente ignora reglas | El contexto se diluye | Corto, con enlaces a skills | `claude-md-authoring`, `context-budgeting` |
| Servidores MCP sin versión ni permisos | Cadena de suministro y acciones no deseadas | Se ejecuta código nuevo en cada arranque | Versión fija y permisos por herramienta | `mcp-governance` |
