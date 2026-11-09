# AI Project Factory — Makefile 
PY ?= python3

.PHONY: help setup validate test check index policy-test

help: ## Lista de objetivos
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

setup: ## Instala dependencias de desarrollo (Python)
	$(PY) -m pip install -r requirements-dev.txt

validate: ## Ejecuta los validadores de la fábrica (incluye índice/estándares al día)
	$(PY) factory/validators/run_all.py
	$(PY) factory/tools/build_index.py --check

index: ## Regenera docs/skills-index.md y standards/*.md desde los skills
	$(PY) factory/tools/build_index.py

test: ## Tests de hooks y validadores
	$(PY) -m pytest tests -q

policy-test: ## Prueba las reglas Semgrep con los casos de tests/semgrep (requiere semgrep)
	semgrep --test --config policies/semgrep tests/semgrep --metrics=off

check: validate test ## validate + test
