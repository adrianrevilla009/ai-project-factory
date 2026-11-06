# TODO-VERIFY: fijar la imagen base por digest y revisar versiones al preparar la Oleada 1.
FROM mcr.microsoft.com/devcontainers/python:3.12
RUN apt-get update && apt-get install -y --no-install-recommends \
      make jq git curl ca-certificates iptables ipset dnsutils docker.io sudo \
    && rm -rf /var/lib/apt/lists/*
# El firewall se copia a una ruta inmutable y solo ese script puede ejecutarse como root.
COPY firewall/ /opt/firewall/
RUN chmod 0755 /opt/firewall/init-firewall.sh \
    && echo "vscode ALL=(root) NOPASSWD: /opt/firewall/init-firewall.sh" > /etc/sudoers.d/firewall \
    && chmod 0440 /etc/sudoers.d/firewall
# Node para el CLI de Claude Code: TODO-VERIFY método de instalación vigente.
