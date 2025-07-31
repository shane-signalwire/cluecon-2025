# Max Electric Payment Demo - Docker Makefile
# Usage: make <target>

# Variables
IMAGE_NAME = max-electric-payment-demo
CONTAINER_NAME = max-electric-app
PORT = 8080
HOST_PORT = 8080

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Max Electric Payment Demo - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make run          # Build and run the container"
	@echo "  make stop         # Stop the running container"
	@echo "  make logs         # View container logs"

.PHONY: build
build: ## Build the Docker image
	@echo "🔨 Building Docker image: $(IMAGE_NAME)"
	docker build -t $(IMAGE_NAME) .
	@echo "✅ Build complete!"

.PHONY: run-only
run-only: ## Run the container (assumes image is already built)
	@echo "🚀 Starting container: $(CONTAINER_NAME)"
	@if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		echo "⚠️  Container $(CONTAINER_NAME) is already running"; \
		echo "   Use 'make stop' to stop it first, or 'make restart' to restart"; \
	else \
		docker run -d \
			--name $(CONTAINER_NAME) \
			-p $(HOST_PORT):$(PORT) \
			--env-file env \
			$(IMAGE_NAME); \
		echo "✅ Container started on http://localhost:$(HOST_PORT)"; \
	fi

.PHONY: run
run: build run-only ## Build and run the container (one command)

.PHONY: dev
dev: ## Run container with volume mounts for development
	@echo "🔧 Starting development container with volume mounts"
	@if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		echo "⚠️  Container $(CONTAINER_NAME) is already running"; \
		make stop; \
	fi
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(HOST_PORT):$(PORT) \
		--env-file env \
		-v $$(pwd)/templates:/app/templates \
		-v $$(pwd)/static:/app/static \
		-v $$(pwd)/app.py:/app/app.py \
		$(IMAGE_NAME)
	@echo "✅ Development container started on http://localhost:$(HOST_PORT)"
	@echo "📁 Volume mounts: templates/, static/, app.py"

.PHONY: stop
stop: ## Stop and remove the running container
	@echo "🛑 Stopping container: $(CONTAINER_NAME)"
	@if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		docker stop $(CONTAINER_NAME); \
		docker rm $(CONTAINER_NAME); \
		echo "✅ Container stopped and removed"; \
	else \
		echo "ℹ️  Container $(CONTAINER_NAME) is not running"; \
	fi

.PHONY: restart
restart: stop run-only ## Restart the container

.PHONY: logs
logs: ## View container logs
	@echo "📋 Viewing logs for: $(CONTAINER_NAME)"
	@if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		docker logs -f $(CONTAINER_NAME); \
	else \
		echo "❌ Container $(CONTAINER_NAME) is not running"; \
		echo "   Use 'make run' to start it"; \
	fi

.PHONY: shell
shell: ## Open a shell inside the running container
	@echo "🐚 Opening shell in container: $(CONTAINER_NAME)"
	@if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		docker exec -it $(CONTAINER_NAME) /bin/bash; \
	else \
		echo "❌ Container $(CONTAINER_NAME) is not running"; \
		echo "   Use 'make run' to start it first"; \
	fi

.PHONY: status
status: ## Show container status
	@echo "📊 Container Status:"
	@echo ""
	@if [ $$(docker ps -q -f name=$(CONTAINER_NAME)) ]; then \
		echo "✅ Container $(CONTAINER_NAME) is RUNNING"; \
		docker ps --filter name=$(CONTAINER_NAME) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"; \
		echo ""; \
		echo "🌐 Application: http://localhost:$(HOST_PORT)"; \
	else \
		echo "❌ Container $(CONTAINER_NAME) is NOT running"; \
	fi
	@echo ""
	@echo "📦 Images:"
	@docker images | grep $(IMAGE_NAME) || echo "No images found for $(IMAGE_NAME)"

.PHONY: clean
clean: stop ## Stop container and remove image
	@echo "🧹 Cleaning up Docker resources"
	@if [ $$(docker images -q $(IMAGE_NAME)) ]; then \
		docker rmi $(IMAGE_NAME); \
		echo "✅ Image $(IMAGE_NAME) removed"; \
	else \
		echo "ℹ️  No image $(IMAGE_NAME) to remove"; \
	fi

.PHONY: clean-all
clean-all: clean ## Remove all related Docker resources (containers, images, volumes)
	@echo "🧹 Deep cleaning Docker resources"
	@docker system prune -f
	@echo "✅ Docker system pruned"

.PHONY: rebuild
rebuild: clean build ## Clean and rebuild the image

.PHONY: setup
setup: ## Initial setup - build and run for the first time
	@echo "🎯 Initial Setup - Building and starting Max Electric Payment Demo"
	@echo ""
	@make build
	@echo ""
	@make run-only
	@echo ""
	@echo "🎉 Setup Complete!"
	@echo ""
	@echo "📱 Your application is now running at: http://localhost:$(HOST_PORT)"
	@echo "📋 Use 'make logs' to view logs"
	@echo "🛑 Use 'make stop' to stop the application"

.PHONY: quick-start
quick-start: setup ## Alias for setup (build and run)

# Development helpers
.PHONY: build-no-cache
build-no-cache: ## Build the Docker image without cache
	@echo "🔨 Building Docker image without cache: $(IMAGE_NAME)"
	docker build --no-cache -t $(IMAGE_NAME) .
	@echo "✅ Build complete!"

.PHONY: update-env
update-env: ## Update environment variables (restart required)
	@echo "🔄 Environment file updated"
	@echo "⚠️  Restart container to apply changes: make restart"

# Utility targets
.PHONY: check-env
check-env: ## Check if env file exists and show variables
	@echo "🔍 Checking environment configuration:"
	@if [ -f env ]; then \
		echo "✅ env file exists"; \
		echo ""; \
		echo "📋 Environment variables:"; \
		cat env | grep -v '^#' | grep -v '^$$'; \
	else \
		echo "❌ env file not found!"; \
		echo "   Make sure you have an 'env' file in the project root"; \
	fi

.PHONY: open
open: ## Open the application in default browser
	@echo "🌐 Opening http://localhost:$(HOST_PORT)"
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:$(HOST_PORT); \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:$(HOST_PORT); \
	else \
		echo "Please open http://localhost:$(HOST_PORT) in your browser"; \
	fi

# Make sure we don't treat file names as targets
.PHONY: all
all: help 
