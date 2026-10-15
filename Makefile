# Atalhos do monorepo. Rode `make help` para ver tudo.
.DEFAULT_GOAL := help
.PHONY: help setup lint fmt test

help: ## Lista os comandos
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  make %-8s %s\n", $$1, $$2}'

setup: ## Instala o pre-commit e os hooks (pre-commit + commit-msg)
	@command -v pre-commit >/dev/null || uv tool install pre-commit
	pre-commit install --install-hooks

lint: ## Roda todos os hooks em todos os arquivos
	pre-commit run --all-files

fmt: ## Formata o código (ruff, prettier, terraform fmt)
	pre-commit run ruff-format --all-files || true
	pre-commit run prettier --all-files || true
	pre-commit run terraform_fmt --all-files || true

test: ## Roda os testes do backend e do web
	@if [ -f backend/pyproject.toml ]; then cd backend && uv run pytest; else echo "backend: n/a"; fi
	@if [ -f web/package.json ]; then npm --prefix web test; else echo "web: n/a"; fi
