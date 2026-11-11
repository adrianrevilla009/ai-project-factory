# semgrep

46 reglas de [Semgrep](https://semgrep.dev) repartidas en 36 ficheros, una por cada patrón que las skills quieren detectar en código. Son las únicas políticas de la fábrica que están **probadas**: cada regla tiene al menos un caso que debe detectar y otro que no, en [`tests/semgrep/`](../../tests/semgrep/README.md).

## Qué cubren
| Área | Ficheros |
|---|---|
| Java general | `java-no-lombok`, `java-language-pitfalls` (dinero con `double`, `new BigDecimal(double)`, API de fechas antigua, `getBytes()` sin codificación, `catch Throwable`, `Optional.get`), `java-logging`, `java-money-floating-point`, `java-weak-crypto`, `java-unsafe-deserialization`, `java-path-from-user-input` |
| Concurrencia | `java-check-then-act-map`, `java-completablefuture-default-pool`, `java-unbounded-executors`, `java-scheduled-without-lock`, `java-sleep-in-tests` |
| Persistencia | `jpa-eager-toone`, `jpa-enumerated-ordinal`, `sql-string-concat`, `sql-unsafe-migrations` |
| Spring y seguridad | `spring-field-injection`, `spring-http-client-without-timeout`, `spring-security-misconfig`, `webhook-signature-equals`, `xml-parser-xxe`, `config-literal-secret-in-properties` |
| Mensajería | `kafka-auto-commit` |
| Observabilidad | `java-metrics-cardinality` |
| IA | `llm-direct-provider-url`, `llm-log-raw-prompt`, `llm-prompt-concatenation` |
| Frontend | `frontend-clickable-div`, `frontend-dangerously-set-inner-html`, `frontend-realtime-token-in-url`, `frontend-token-in-web-storage` |
| Datos y AWS | `airflow-catchup-true`, `dbt-select-star-source`, `dynamodb-put-without-condition`, `dynamodb-scan-forbidden`, `dynamodb-local-endpoint-in-main` |

## Convenciones de una regla
- Un fichero por tema (a veces varias reglas relacionadas).
- Cada regla lleva en `metadata.skill` la skill de la que sale y, cuando hace falta, una `note` con sus límites conocidos.
- El `message` está en español y remite a la skill; los identificadores, en inglés.
- Algunas reglas limitan su alcance con `paths` (por ejemplo, las migraciones SQL o los ficheros `application*.yml`).

## Uso
```bash
semgrep --config policies/semgrep <ruta-a-analizar>   # analizar código
make policy-test                                      # probar las reglas con los casos de tests/semgrep/
```
Las reglas se copian al proyecto generado, que las ejecuta en su CI. La versión probada es Semgrep 1.184.0.

## Límites
Semgrep detecta patrones sintácticos; no sigue flujos de datos entre ficheros. Una regla puede dar falsos positivos (por ejemplo, `java-unsafe-deserialization` marca cualquier `ObjectInputStream`) y las excepciones se justifican con `nosemgrep` en el código.
