#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --user -r requirements-dev.txt
# CLI de Claude Code por npm (Node 22 o posterior); versión fija, nunca `latest`.
CLAUDE_CODE_VERSION="2.1.319"
npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"
# Docker por socket del host (ADR-0030): equivale a root en el host; no montar credenciales cloud.
echo "devcontainer listo. Ejecuta: make check"
