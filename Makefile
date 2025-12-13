.PHONY: help dev-up dev-down dev-logs prod-up prod-down prod-logs sync-cache clear-dev-cache inspect-cache-dev inspect-cache-prod dev-backend dev-frontend

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development environment
dev-up: ## Start development environment (Redis + backend)
	docker-compose -f docker-compose.dev.yaml up -d

dev-down: ## Stop development environment
	docker-compose -f docker-compose.dev.yaml down

dev-logs: ## Show development logs
	docker-compose -f docker-compose.dev.yaml logs -f

dev-frontend: ## Run frontend dev server
	cd frontend && pnpm run dev

dev: dev-up dev-frontend ## Start full dev environment (Docker backend + local frontend)

# Cache management
sync-cache: ## Sync production cache to development
	./scripts/sync-cache-prod-to-dev.sh

clear-dev-cache: ## Clear development cache
	./scripts/clear-dev-cache.sh

inspect-cache-dev: ## Inspect development cache statistics
	./scripts/inspect-cache.sh dev

inspect-cache-prod: ## Inspect production cache statistics
	./scripts/inspect-cache.sh prod

# Build
build-backend: ## Build backend Docker image
	cd backend && docker build -t wa-backend:latest .

lint-frontend: ## Lint frontend code
	cd frontend && pnpm lint

format-frontend: ## Format frontend code
	cd frontend && pnpm format

check-frontend: ## Type check frontend
	cd frontend && pnpm check

# Health checks
health-dev: ## Check development environment health
	./scripts/health-check.sh dev

health-prod: ## Check production environment health
	./scripts/health-check.sh prod

# Cleanup
clean-volumes: ## Remove all Docker volumes (DANGEROUS!)
	@echo "This will remove all Redis data. Press Ctrl+C to cancel..."
	@sleep 5
	docker-compose -f docker-compose.dev.yaml down -v
	docker-compose -f docker-compose.prod.yaml down -v
