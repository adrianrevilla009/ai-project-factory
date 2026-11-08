# tests

`make test` ejecuta `pytest tests`. Cubre la maquinaria de la fábrica, no el contenido de las skills.

- `hooks/test_hooks.py` — hooks PreToolUse: secretos, comandos peligrosos y registros de aprobación de gates.
- `hooks/test_hooks_extra.py` — hooks de SessionStart, PostToolUse, Stop y auditoría.
- `validators/test_validators.py` — validadores de skills y de claims sobre AWS, esquemas, ADRs y frescura del índice generado.

Cada hook se prueba como en producción: se lanza como subproceso con un evento JSON por stdin y se comprueba el código de salida. Los secretos de prueba se construyen en tiempo de ejecución para que ningún fichero del repo contenga uno literal.

Aún no existen evaluaciones de comportamiento de los agentes (la skill `agent-evals` describe el formato propuesto).
