export PIPENV_VENV_IN_PROJECT=true
export PYTHONPATH=src
export MYPYPATH=src

path?=spec/spec_*.py

all: help

.PHONY: help
help:
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sed -e "s/| \(.*\)$$/| $$(printf "\033")[37m\1$$(printf "\033")[0m/g"
	@printf '\nAvailable variables:\n'
	@grep -E '^[a-zA-Z_-]+\?=.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = "?="}; {printf "\033[36m%-20s\033[0m default: %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the project
	pipenv sync --bare

.PHONY: fmt
fmt: ## Format
	pipenv run -- black src spec
	pipenv run -- isort --profile black src spec

.PHONY: local
local: ## Starts local uvicorn
	DRADIS_TOKEN=fake pipenv run -- uvicorn --reload --reload-dir src main:app
	@echo 'Do not forget to pass the token using: "Authorization: Bearer fake"'

.PHONY: setup
setup:
	pipenv sync --dev --bare

.PHONY: sh
sh: ## Open a pipenv shell
	pipenv shell

.PHONY: test
test: setup ## Test the project | make test path=spec/spec_lifen.py
	pipenv run -- black --check src spec
	pipenv run -- isort --profile black --check-only src spec
	pipenv run -- flake8 --append-config .flake8.conf src spec
	pipenv run -- mypy --explicit-package-bases .
	DRADIS_TOKEN=fake pipenv run -- python3 -m unittest $(path)