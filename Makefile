# AI Project Factory — Makefile (Oleada 0)
PY ?= python3

.PHONY: help setup validate test check

help: ## Lista de objetivos
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

setup: ## Instala dependencias de desarrollo (Python)
	$(PY) -m pip install -r requirements-dev.txt

validate: ## Ejecuta los validadores de la fábrica
	$(PY) factory/validators/run_all.py

test: ## Tests de hooks y validadores
	$(PY) -m pytest tests -q

check: validate test ## validate + test
