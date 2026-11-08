# policies

Reglas ejecutables que respaldan filas «policy» o «hook» de las tablas de Enforcement de las skills. Las reglas **Semgrep** (46) están validadas y probadas con `make policy-test` (semgrep 1.184.0, casos positivos y negativos en `tests/semgrep/`). El resto son ejemplos escritos a mano que **aún no se han ejecutado** con su herramienta; cada fila de la tabla lo indica.

| Carpeta | Herramienta | Contenido | Cómo se usa |
|---|---|---|---|
| `semgrep/` | Semgrep | 36 ficheros (46 reglas): Java (Lombok, concurrencia, criptografía débil, deserialización), JPA, Spring, Kafka, SQL, LLM, frontend, dbt/Airflow, DynamoDB | `semgrep --config policies/semgrep <ruta>`; pruebas con `make policy-test` |
| `opa-conftest/` | Conftest (Rego) | Pinning de GitHub Actions, Dockerfile, IAM sin comodín de admin, tags obligatorios, Argo CD, secretos en GitOps, Istio, AWS Backup Vault Lock, etiquetas de madurez | `conftest test <fichero> -p policies/opa-conftest` |
| `kyverno/` | Kyverno | `workload-baseline` (requests/limits, probes, seccomp) y `verify-image-signatures` | `kubectl apply` en modo Audit primero |
| `archunit/` | ArchUnit (Java) | Aislamiento del dominio, arquitectura hexagonal y límites entre módulos | Se copian al proyecto generado como tests JUnit |
| `frontend-boundaries/` | ESLint, dependency-cruiser | Fronteras entre `app`/`features`/`shared` y TypeScript estricto | Se copian a la raíz del proyecto generado |
| `maven-enforcer/` | Maven Enforcer | Lista de dependencias prohibidas | Se integra en el `pom.xml` del proyecto generado |

Qué falta, de forma explícita: ejecutar y probar las políticas de Rego, Kyverno, ArchUnit y frontend; y las comprobaciones de IaC (Checkov) que varias skills marcan como «pendiente». Una regla Semgrep que pasa sus tests demuestra que detecta ese patrón sintáctico, no que el código esté libre del problema.
