# Imagen base fijada por digest (consultado en mcr.microsoft.com el 2026-11-09); al actualizarla, cambia el digest y revisa las versiones.
FROM mcr.microsoft.com/devcontainers/python:3.12@sha256:79a80515d78783e761af1db255e92767c4e887a2d56dbeb85e7753da8c12dc16
RUN apt-get update && apt-get install -y --no-install-recommends \
      make jq git curl ca-certificates iptables ipset dnsutils docker.io sudo \
    && rm -rf /var/lib/apt/lists/*
# El firewall se copia a una ruta inmutable y solo ese script puede ejecutarse como root.
COPY firewall/ /opt/firewall/
RUN chmod 0755 /opt/firewall/init-firewall.sh \
    && echo "vscode ALL=(root) NOPASSWD: /opt/firewall/init-firewall.sh" > /etc/sudoers.d/firewall \
    && chmod 0440 /etc/sudoers.d/firewall
# Node 22 (requisito del paquete npm de Claude Code) llega por la feature de dev container; el CLI se instala en post-create.sh con versión fija.
