# capabilities

Traduce las respuestas de la entrevista de intake en módulos activos del proyecto.

- `capabilities.yaml` — preguntas de la entrevista (`id`, texto, tipo, valor por defecto) y qué módulos activa cada respuesta.
- `modules-map.yaml` — enlaza cada módulo (siempre activo o activable) con sus bloques y skills, políticas, pruebas y tableros. `make validate` comprueba que todo lo citado existe y que cada módulo que activa `capabilities.yaml` está aquí.
- `interview/intake-script.md` — guion que sigue `project-discover` para hacer las preguntas y registrar las respuestas.

El resultado de la entrevista va a `.factory/state.json` del proyecto generado (`active_modules`) y lo lee el hook `load_context` en cada sesión.
