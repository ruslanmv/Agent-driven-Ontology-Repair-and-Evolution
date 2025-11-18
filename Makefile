.PHONY: help install dev-install start test audit lint format type-check clean docker-build docker-run

.DEFAULT_GOAL := help

# ANSI color codes
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

help: ## Show this help message
	@echo '$(BLUE)═══════════════════════════════════════════════════════════════$(RESET)'
	@echo '$(GREEN)  ADORE - Agent-Driven Ontology Repair and Evolution$(RESET)'
	@echo '$(BLUE)═══════════════════════════════════════════════════════════════$(RESET)'
	@echo ''
	@echo '$(YELLOW)Available targets:$(RESET)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ''
	@echo '$(BLUE)═══════════════════════════════════════════════════════════════$(RESET)'

install: ## Install production dependencies using uv
	@echo '$(BLUE)Installing production dependencies...$(RESET)'
	uv pip install -e .

dev-install: ## Install development dependencies using uv
	@echo '$(BLUE)Installing development dependencies...$(RESET)'
	uv pip install -e ".[dev]"
	pre-commit install

start: ## Run ADORE CLI (interactive mode)
	@echo '$(GREEN)Starting ADORE...$(RESET)'
	uv run adore

demo: ## Run the pneumonia ontology demo
	@echo '$(GREEN)Running pneumonia example...$(RESET)'
	uv run python examples/pneumonia_example.py

test: ## Run tests with pytest
	@echo '$(BLUE)Running tests...$(RESET)'
	uv run pytest -v --cov=src/adore --cov-report=term-missing --cov-report=html

audit: ## Run all quality checks (lint, type-check, security)
	@echo '$(BLUE)Running comprehensive audit...$(RESET)'
	@echo ''
	@echo '$(YELLOW)→ Running ruff check...$(RESET)'
	uv run ruff check src/ tests/
	@echo ''
	@echo '$(YELLOW)→ Running type checker...$(RESET)'
	uv run mypy src/
	@echo ''
	@echo '$(YELLOW)→ Running security scan...$(RESET)'
	uv run pip-audit || true
	@echo ''
	@echo '$(GREEN)✓ Audit complete!$(RESET)'

lint: ## Lint code with ruff
	@echo '$(BLUE)Linting code...$(RESET)'
	uv run ruff check src/ tests/

format: ## Format code with ruff
	@echo '$(BLUE)Formatting code...$(RESET)'
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

type-check: ## Run type checking with mypy
	@echo '$(BLUE)Type checking...$(RESET)'
	uv run mypy src/

clean: ## Clean up temporary files and caches
	@echo '$(YELLOW)Cleaning up...$(RESET)'
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo '$(GREEN)Cleanup complete!$(RESET)'

docker-build: ## Build Docker image
	@echo '$(BLUE)Building Docker image...$(RESET)'
	docker build -t adore:latest .

docker-run: ## Run ADORE in Docker container
	@echo '$(GREEN)Running ADORE in Docker...$(RESET)'
	docker run -it --rm \
		-e OPENAI_API_KEY="${OPENAI_API_KEY}" \
		adore:latest

publish-test: ## Publish to Test PyPI
	@echo '$(BLUE)Publishing to Test PyPI...$(RESET)'
	uv build
	uv publish --repository testpypi

publish: ## Publish to PyPI
	@echo '$(RED)Publishing to PyPI...$(RESET)'
	uv build
	uv publish

ci: clean lint type-check test ## Run CI pipeline locally
	@echo ''
	@echo '$(GREEN)═══════════════════════════════════════════════════════════════$(RESET)'
	@echo '$(GREEN)  ✓ All CI checks passed!$(RESET)'
	@echo '$(GREEN)═══════════════════════════════════════════════════════════════$(RESET)'
