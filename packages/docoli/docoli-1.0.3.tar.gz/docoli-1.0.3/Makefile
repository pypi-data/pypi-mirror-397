SHELL := /usr/bin/env bash

.PHONY: help test test-verbose clean

PY ?= python
TEST_DIR ?= tests
TEST_PATTERN ?= "test_*.py"

# Always test the current working tree, never site-packages
export PYTHONPATH := $(CURDIR)/src

help:
	@echo "Targets:"
	@echo "  make test         - run unit tests (unittest, working tree)"
	@echo "  make test-verbose - run unit tests verbose (working tree)"
	@echo "  make clean        - remove caches"

test:
	PYTHONPATH=$(PYTHONPATH) $(PY) -m unittest discover -s $(TEST_DIR) -p $(TEST_PATTERN)

test-verbose:
	PYTHONPATH=$(PYTHONPATH) $(PY) -m unittest discover -s $(TEST_DIR) -p $(TEST_PATTERN) -v

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -print0 | xargs -0 -r rm -rf
	find . -type f -name "*.pyc" -delete

build: 
	python -m build