# policies

Reglas **ejecutables** que respaldan las filas de nivel «política» (1) y «hook» (2) de las tablas de Enforcement de las skills: convierten una norma escrita en algo que una herramienta puede comprobar de forma automática.

Son ejemplos para copiar al proyecto generado, no un sistema en funcionamiento de esta fábrica (ADR-0038): cada proyecto adopta las que le apliquen, las adapta a su paquete base y a su versión de la herramienta y las ejecuta en su CI.

## Contenido y estado
| Carpeta | Herramienta | Qué contiene | Estado | Cómo se usa |
|---|---|---|---|---|
| [`semgrep/`](semgrep/README.md) | Semgrep | 46 reglas en 36 ficheros: Java, JPA, Spring, Kafka, SQL, LLM, frontend, datos y DynamoDB | **Probadas** con casos positivos y negativos (`make policy-test`) | `semgrep --config policies/semgrep <ruta>` |
| [`opa-conftest/`](opa-conftest/README.md) | Conftest (Rego) | 9 políticas sobre manifiestos, Dockerfiles, flujos de CI, Terraform y registros de madurez | Escritas, **sin ejecutar** | `conftest test <fichero> -p policies/opa-conftest` |
| [`kyverno/`](kyverno/README.md) | Kyverno | Línea base de cargas y verificación de firmas de imágenes | Escritas, **sin ejecutar** | Aplicar en modo auditoría primero |
| [`archunit/`](archunit/README.md) | ArchUnit (Java) | Aislamiento del dominio, arquitectura hexagonal y límites entre módulos | Escritas, **sin ejecutar** | Copiar al proyecto como pruebas JUnit |
| [`frontend-boundaries/`](frontend-boundaries/README.md) | ESLint y dependency-cruiser | Fronteras entre `app`, `features` y `shared`, y TypeScript estricto | Escritas, **sin ejecutar** | Copiar a la raíz del proyecto |
| [`maven-enforcer/`](maven-enforcer/README.md) | Maven Enforcer | Dependencias prohibidas, derivadas del catálogo | Escrita, **sin ejecutar** | Integrar en el `pom` padre |
| [`iac-checks/`](iac-checks/README.md) | Checkov, Conftest | **Especificación** de 28 comprobaciones de infraestructura que piden las skills | Sin escribir | Cada proyecto las implementa |

## Qué demuestra una política y qué no
Una regla que pasa sus pruebas demuestra que **detecta ese patrón**, no que el código esté libre del problema: Semgrep busca patrones sintácticos, no flujos de datos. Por eso las políticas son una capa más de defensa y conviven con los hooks, los revisores y los gates.

## Cómo añadir o cambiar una política
1. Escribe la regla y refiérela desde la tabla de Enforcement de la skill que la motiva.
2. Si es de Semgrep, añade su caso positivo (`ruleid`) y negativo (`ok`) en `tests/semgrep/` y ejecuta `make policy-test`.
3. Indica en la política la skill de la que sale y a qué proyecto se debe adaptar.
4. Anota el cambio en el `CHANGELOG`.
