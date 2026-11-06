#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --user -r requirements-dev.txt
# Docker por socket del host (ADR-0030): equivale a root en el host; no montar credenciales cloud.
echo "devcontainer listo. Ejecuta: make check"
