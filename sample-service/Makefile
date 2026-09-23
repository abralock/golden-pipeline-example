# Makefile contract (platform standard v1). Same 5 targets in every code repo:
#   make setup | lint | test | coverage | build
# CI runs: make setup && make lint && make coverage, then make build on main.
# `coverage` MUST write reports/junit.xml and reports/coverage.xml (Cobertura/JaCoCo).
PY ?= python3

.PHONY: setup lint test coverage build clean

setup:
	$(PY) -m pip install -q -e ".[dev]"

lint:
	$(PY) -m ruff check src tests

test:
	$(PY) -m pytest -q

coverage:
	mkdir -p reports
	$(PY) -m pytest -q --junitxml=reports/junit.xml \
	  --cov=src --cov-report=xml:reports/coverage.xml --cov-report=term-missing

build:
	$(PY) -m pip wheel -q --no-deps -w dist .

clean:
	rm -rf reports dist build *.egg-info src/*.egg-info .pytest_cache .coverage
