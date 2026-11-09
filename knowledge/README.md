# knowledge

Conocimiento transversal de la fábrica, en dos capas.

## Catálogos (escritos, revisables)
Capa de navegación sobre las 490 skills. No sustituyen a las skills: te llevan a ellas desde un problema.

| Documento | Responde a |
|---|---|
| [`patterns.md`](patterns.md) | «¿Hay un patrón conocido para esto, y cuándo no debo usarlo?» |
| [`anti-patterns.md`](anti-patterns.md) | «Esto me suena a mala idea: ¿por qué y qué hago en su lugar?» |
| [`decisions-index.md`](decisions-index.md) | «Tengo que decidir X: ¿dónde está el criterio y qué decisiones ya están cerradas?» |

`make validate` comprueba que toda skill y todo ADR citados existan, así que los enlaces no se rompen en silencio. Al añadir o renombrar una skill, actualiza aquí las filas que la mencionen.

## Memoria de proyectos (se rellena sola)
El comando de cierre de lecciones (fase 06-close) propone aquí, para revisión humana, cambios a skills o hooks y perfiles de dominio reutilizables, y solo con permiso del cliente y sin datos sensibles. Las subcarpetas (`lessons-learned/`, `domain-profile-seeds/`) se crean al escribir la primera. Hoy no hay ninguna porque aún no se ha cerrado ningún proyecto. El hook de gates permite editar `knowledge/` en cualquier fase.
