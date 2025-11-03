PYTEST ?= pytest
PYTEST_OPTS ?= -q
COVERAGE ?= coverage
RUFF ?= ruff
PDOC ?= pdoc3

.PHONY: help test unit_test perf_test coverage lint doc clean

.DEFAULT_GOAL := help

help:
	@echo "Usage:"
	@echo "  make test        # lance tous les tests (pytest)"
	@echo "  make unit_test   # lance tous les tests sauf les tests marqués 'perf' (pytest -m 'not perf')"
	@echo "  make perf_test   # lance uniquement les tests marqués 'perf' (pytest -m perf)"
	@echo "  make coverage    # génère le rapport de couverture (coverage html)"
	@echo "  make lint        # vérifie la qualité du code (ruff check)"
	@echo "  make doc         # génère la documentation HTML (pdoc3)"
	@echo "  make clean       # nettoie les artefacts (coverage html dir, docs)"

test:
	$(PYTEST) $(PYTEST_OPTS)

unit_test:
	$(PYTEST) $(PYTEST_OPTS) -m "not perf"

perf_test:
	$(PYTEST) $(PYTEST_OPTS) -m perf

coverage:
	$(COVERAGE) run -m pytest && $(COVERAGE) html

lint:
	$(RUFF) check .

doc:
	$(PDOC) --html --output-dir docs

clean:
	@rm -rf .coverage htmlcov docs