# policies

Reglas ejecutables que respaldan filas «policy» o «hook» de las tablas de Enforcement de las skills. Son **ejemplos escritos y revisados a mano, ninguno se ha ejecutado todavía** contra su herramienta; el contenido de `metadata.note` de cada regla Semgrep lo indica.

| Carpeta | Herramienta | Contenido | Cómo se usa |
|---|---|---|---|
| `semgrep/` | Semgrep | 36 ficheros: Java (Lombok, concurrencia, criptografía débil, deserialización), JPA, Spring, Kafka, SQL, LLM, frontend, dbt/Airflow, DynamoDB | `semgrep --config policies/semgrep <ruta>` |
| `opa-conftest/` | Conftest (Rego) | Pinning de GitHub Actions, Dockerfile, IAM sin comodín de admin, tags obligatorios, Argo CD, secretos en GitOps, Istio, AWS Backup Vault Lock, etiquetas de madurez | `conftest test <fichero> -p policies/opa-conftest` |
| `kyverno/` | Kyverno | `workload-baseline` (requests/limits, probes, seccomp) y `verify-image-signatures` | `kubectl apply` en modo Audit primero |
| `archunit/` | ArchUnit (Java) | Aislamiento del dominio, arquitectura hexagonal y límites entre módulos | Se copian al proyecto generado como tests JUnit |
| `frontend-boundaries/` | ESLint, dependency-cruiser | Fronteras entre `app`/`features`/`shared` y TypeScript estricto | Se copian a la raíz del proyecto generado |
| `maven-enforcer/` | Maven Enforcer | Lista de dependencias prohibidas | Se integra en el `pom.xml` del proyecto generado |

Qué falta, de forma explícita: ejecutar cada política con su herramienta y casos de prueba; las comprobaciones de IaC (Checkov/tfsec) que varias skills marcan como «pendiente». Hasta entonces, una regla escrita aquí no demuestra que se cumpla nada.
