.PHONY: help list test setup lint validate

help: ## Show this help message
	@echo "Sindri Test Project - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

list: ## List all available Sindri commands
	sindri list

test: ## Run tests via Sindri
	sindri run test

setup: ## Run setup via Sindri
	sindri run setup

lint: ## Run lint via Sindri
	sindri run lint

validate: ## Run validate via Sindri
	sindri run validate

