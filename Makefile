# AI Project Factory — Makefile (Oleada 0)
PY ?= python3

.PHONY: help setup validate test check local-up gen cloud-check

help: ## Lista de objetivos
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

setup: ## Instala dependencias de desarrollo (Python)
	$(PY) -m pip install -r requirements-dev.txt

validate: ## Ejecuta los validadores de la fábrica
	$(PY) factory/validators/run_all.py

test: ## Tests de hooks y validadores
	$(PY) -m pytest tests -q

check: validate test ## validate + test

local-up: ## [Oleada 3] Levanta el entorno Kubernetes local
	@echo "TODO: pendiente (Oleada 3, local-k8s)"; exit 1

gen: ## [Oleada 1+] Genera un proyecto desde las plantillas
	@echo "TODO: pendiente (Oleada 1+, factory/cli)"; exit 1

cloud-check: ## [Oleada 3] Validación estática de infra (nunca despliega)
	@echo "TODO: pendiente (Oleada 3, cloud-readiness)"; exit 1
