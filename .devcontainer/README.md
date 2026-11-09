# .devcontainer

Entorno aislado para trabajar con agentes sobre la fábrica (ADR-0030, D26).

- `Dockerfile` — parte de `mcr.microsoft.com/devcontainers/python:3.12` fijada por digest y añade `make`, `jq`, `git`, `curl`, `iptables`, `ipset`, `dig` y `docker.io`. El usuario `vscode` solo puede ejecutar como root el script del firewall.
- `devcontainer.json` — instala Node 22 con una feature de dev container (el CLI de Claude Code lo necesita), añade `NET_ADMIN`/`NET_RAW` (necesarios para el firewall), monta `/var/run/docker.sock` y ejecuta `post-create.sh` (dependencias de Python y el CLI de Claude Code con versión fija) y `firewall/init-firewall.sh`.
- `firewall/init-firewall.sh` — resuelve los dominios de `firewall/allowlist.txt` a un `ipset` y rechaza el resto del tráfico saliente.

## Límites que debes conocer
- **El firewall no se ha ejecutado en un contenedor real.** Trátalo como borrador hasta probarlo (`curl` a un dominio fuera de la allowlist debe fallar).
- Resuelve IPs una sola vez al arrancar: dominios con IPs rotativas (CDN) pueden quedar bloqueados o desactualizados.
- Montar el socket de Docker equivale a dar root sobre el host. No montes credenciales cloud en este contenedor.
- Para ampliar la allowlist, añade el dominio a `allowlist.txt` y justifícalo en el PR.
