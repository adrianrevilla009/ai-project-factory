# .devcontainer

Un entorno de trabajo aislado y reproducible para ejecutar agentes de IA sobre la fábrica (ADR-0030, D26). La idea: el agente trabaja dentro de un contenedor con la salida de red restringida, de modo que un error o una inyección de instrucciones tenga un radio de daño limitado.

## Contenido
| Fichero | Qué hace |
|---|---|
| `Dockerfile` | Parte de `mcr.microsoft.com/devcontainers/python:3.12`, fijada por digest, y añade `make`, `jq`, `git`, `curl`, `iptables`, `ipset`, `dig` y `docker.io`. El usuario `vscode` solo puede ejecutar como administrador el script del firewall |
| `devcontainer.json` | Instala Node 22 con una feature (el CLI de Claude Code lo necesita), añade las capacidades `NET_ADMIN` y `NET_RAW` (necesarias para el firewall), monta el socket de Docker y ejecuta `post-create.sh` y el firewall al arrancar |
| `post-create.sh` | Instala las dependencias de Python y el CLI de Claude Code con **versión fija** |
| `firewall/init-firewall.sh` | Resuelve los dominios de `allowlist.txt` a un `ipset` y rechaza el resto del tráfico saliente |
| `firewall/allowlist.txt` | Los dominios permitidos: GitHub, PyPI, npm, Maven Central y los de Anthropic |

## Cómo se usa
Abre la carpeta del repositorio con un cliente compatible con dev containers (VS Code, por ejemplo) y elige «Reabrir en contenedor». Después, `make check` valida todo.

## Límites que debes conocer
- **El firewall no se ha ejecutado en un contenedor real.** Trátalo como un borrador hasta probarlo: una petición a un dominio fuera de la allowlist debe fallar.
- Resuelve las direcciones IP **una sola vez** al arrancar: los dominios con IP rotativas (CDN) pueden quedar bloqueados o desactualizados.
- La allowlist no incluye los registros de imágenes de contenedores, así que `kind` no puede descargar imágenes dentro del contenedor hasta que se añadan.
- **Montar el socket de Docker equivale a dar administrador sobre el equipo anfitrión.** No montes credenciales de nube en este contenedor.
- Para ampliar la allowlist, añade el dominio a `allowlist.txt` y justifícalo en el PR.
