VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_ACTIVATE := $(VENV_BIN)/activate
PYTEST := $(VENV_BIN)/pytest
PYTEST_OPTS ?= -q
COVERAGE := $(VENV_BIN)/coverage
RUFF := $(VENV_BIN)/ruff
PDOC := $(VENV_BIN)/pdoc3
PYTHON := $(VENV_BIN)/python
PIP := $(PYTHON) -m pip

.PHONY: help test unit_test perf_test coverage lint doc clean run install install_dev venv

.DEFAULT_GOAL := help

# setup venv
$(VENV_ACTIVATE):
	python -m venv $(VENV)
# 	$(PIP) install --upgrade pip
	@echo "Environnement virtuel créé."

venv: $(VENV_ACTIVATE)


help:
	@echo "Usage:"
	@echo "  make test        # lance make unit_test"
	@echo "  make unit_test   # lance tous les tests sauf les tests marqués 'perf' (pytest -m 'not perf')"
	@echo "  make perf_test   # lance uniquement les tests marqués 'perf' (pytest -m perf)"
	@echo "  make coverage    # génère le rapport de couverture (coverage html)"
	@echo "  make lint        # vérifie la qualité du code (ruff check)"
	@echo "  make doc         # génère la documentation HTML (pdoc3)"
	@echo "  make clean       # nettoie les artefacts (coverage html dir, docs)"
	@echo "  make clean_all   # make clean + supprime l'environnement virtuel"
	@echo "  make run         # exécute l'application principale (python zz_app.py)"
	@echo "  make install     # installe les dépendances dans l'environnement virtuel"
	@echo "  make install_dev # installe les dépendances de développement dans l'environnement virtuel"
	@echo "  make venv        # crée un environnement virtuel"

install: venv
	$(PIP) install -r requirements.txt

install_dev: venv install
	$(PIP) install -r dev_requirements.txt

unit_test: install_dev
	$(PYTEST) $(PYTEST_OPTS) -m "not perf"

perf_test: install_dev
	$(PYTEST) $(PYTEST_OPTS) -m "perf"

test: unit_test

coverage: install_dev
	- $(COVERAGE) run -m pytest -m "not perf" 
	$(COVERAGE) report
	$(COVERAGE) html

lint:
	$(RUFF) check .

doc: install_dev
	$(PDOC) --html --output-dir docs .

clean:
	@rm -rf .coverage htmlcov docs __pycache__

clean_all: clean
	@rm -rf $(VENV)

run: install
	$(python) zz_app.py