# Makefile for claude-code-release-cadence
# [Created with AI: Claude Code with Opus 4.6]

VENV := .venv
INSTALL_STAMP := $(VENV)/.install_timestamp

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(INSTALL_STAMP): pyproject.toml
	uv sync --dev
	touch $(INSTALL_STAMP)

.PHONY: install-dev
install-dev: $(INSTALL_STAMP) ## Install package in development mode with dev dependencies

.PHONY: fetch
fetch: $(INSTALL_STAMP) ## Fetch fresh data from npm/GitHub/web
	uv run python -m claude_code_release_cadence --fetch-only

.PHONY: build
build: $(INSTALL_STAMP) ## Build dashboard and exports from existing data
	uv run python -m claude_code_release_cadence --build-only

.PHONY: all
all: $(INSTALL_STAMP) ## Fetch data, then build dashboard and exports
	uv run python -m claude_code_release_cadence

.PHONY: test-unit
test-unit: $(INSTALL_STAMP) ## Run pytest unit tests
	uv run pytest tests/ -v

.PHONY: test-typing
test-typing: $(INSTALL_STAMP) ## Run mypy type checking
	uv run mypy src/

.PHONY: test
test: test-typing test-unit ## Run all tests (typing + unit)

.PHONY: check
check: lint test ## Run all linters and tests

.PHONY: lint
lint: lint-py lint-md lint-css lint-js ## Run all linters and format checkers

.PHONY: lint-py
lint-py: $(INSTALL_STAMP)
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

.PHONY: lint-md
lint-md: ## Check Markdown formatting with Prettier
	npx --yes prettier --check '**/*.md'

.PHONY: lint-css
lint-css: ## Check CSS formatting with Prettier
	npx --yes prettier --check 'src/**/*.css'

.PHONY: lint-js
lint-js: ## Check JS formatting with Prettier
	npx --yes prettier --check 'src/**/*.js'

.PHONY: format
format: format-py format-md format-css format-js ## Run all formatters

.PHONY: format-py
format-py: $(INSTALL_STAMP)
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

.PHONY: format-md
format-md: ## Format Markdown files with Prettier
	npx --yes prettier --write '**/*.md'

.PHONY: format-css
format-css: ## Format CSS files with Prettier
	npx --yes prettier --write 'src/**/*.css'

.PHONY: format-js
format-js: ## Format JS files with Prettier
	npx --yes prettier --write 'src/**/*.js'

.PHONY: bump-version
bump-version: ## Bump version to current America/Los_Angeles timestamp
	bash scripts/bump-version.sh

.PHONY: open
open: ## Open generated dashboard in browser
	xdg-open public/index.html 2>/dev/null || open public/index.html 2>/dev/null || echo "Open public/index.html in your browser"

.PHONY: clean
clean: ## Remove build output
	rm -rf public/ data/cooked/

.PHONY: purge
purge: clean ## Remove public, data, venv, and caches
	rm -rf $(VENV) data/raw/ *.egg-info/ .mypy_cache/ .pytest_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: install-hooks
install-hooks: $(INSTALL_STAMP) ## Install pre-commit git hooks
	uv run pre-commit install

.PHONY: cloc
cloc: ## Count lines of code
	cloc --vcs=git --exclude-dir=.venv,legacy,data,public --exclude-lang=CSV,Text,Markdown,JSON .

.PHONY: cloc-files
cloc-files: ## Count lines of code per file
	cloc --vcs=git --exclude-dir=.venv,legacy,data,public --exclude-lang=CSV,Text,Markdown,JSON --by-file .

.PHONY: tree
tree: ## Show git file tree
	git ls-files | tree --fromfile -a --filesfirst
