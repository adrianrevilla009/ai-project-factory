# semgrep

Los casos con los que se prueban las reglas de [`policies/semgrep/`](../../policies/semgrep/README.md). Se ejecutan con `make policy-test`, que lanza `semgrep --test --config policies/semgrep tests/semgrep` y requiere Semgrep instalado (el CI instala la versión 1.184.0).

## Cómo funcionan
- Cada fichero de prueba se llama como su regla (`java-no-lombok.yaml` → `java-no-lombok.java`) y contiene código con anotaciones en comentarios:
  - `ruleid: <id>` en la línea anterior a lo que **debe detectarse**.
  - `ok: <id>` en la línea anterior a lo que **no debe detectarse**.
- Cada regla tiene al menos un caso positivo; las que lo necesitan, también uno negativo.
- Las reglas con filtro de rutas (`paths`) tienen sus casos en la ruta que las activa; por eso las migraciones SQL están en `db/migration/`.
- En los ficheros SQL las anotaciones se escriben con `#`, porque Semgrep no reconoce `--` como comentario de anotación.

## Cómo añadir una regla
1. Escribe la regla en `policies/semgrep/`.
2. Crea su fichero de prueba con el mismo nombre y las anotaciones `ruleid` y `ok`.
3. Ejecuta `make policy-test` hasta que pase.
