# Resume Adapter Makefile
# Simple commands to manage the application

.PHONY: help build up down restart logs clean install dev test health stop

# Default target - show help
help:
	@echo "Resume Adapter - Available Commands:"
	@echo ""
	@echo "  make setup      - First time setup (create .env from example)"
	@echo "  make build      - Build Docker containers"
	@echo "  make up         - Start the application"
	@echo "  make start      - Build and start (first time use)"
	@echo "  make down       - Stop the application"
	@echo "  make stop       - Stop the application (alias)"
	@echo "  make restart    - Restart the application"
	@echo "  make logs       - View logs (all services)"
	@echo "  make logs-be    - View backend logs only"
	@echo "  make logs-fe    - View frontend logs only"
	@echo "  make health     - Check backend health"
	@echo "  make clean      - Remove containers, volumes, and images"
	@echo "  make dev-be     - Run backend locally (no Docker)"
	@echo "  make dev-fe     - Run frontend locally (no Docker)"
	@echo "  make test       - Run tests (if available)"
	@echo "  make install    - Install local dependencies"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup       (creates .env file)"
	@echo "  2. Edit .env file   (add your OpenAI API key)"
	@echo "  3. make start       (builds and starts app)"
	@echo "  4. Open http://localhost:3000"
	@echo ""

# First time setup - create .env file
setup:
	@echo "🔧 Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file"; \
		echo "⚠️  IMPORTANT: Edit .env and add your OpenAI API key!"; \
		echo "   Get your key from: https://platform.openai.com/api-keys"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "✅ Created backend/.env file"; \
	fi

# Build Docker containers
build:
	@echo "🔨 Building Docker containers..."
	docker-compose build

# Start the application (detached mode)
up:
	@echo "🚀 Starting Resume Adapter..."
	docker-compose up -d
	@echo ""
	@echo "✅ Application started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "View logs with: make logs"
	@echo "Stop with: make down"

# Build and start (for first time use)
start: build up
	@echo "🎉 Resume Adapter is running!"

# Stop the application
down:
	@echo "🛑 Stopping Resume Adapter..."
	docker-compose down
	@echo "✅ Application stopped"

# Alias for down
stop: down

# Restart the application
restart:
	@echo "🔄 Restarting Resume Adapter..."
	docker-compose restart
	@echo "✅ Application restarted"

# View logs (all services)
logs:
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	docker-compose logs -f

# View backend logs only
logs-be:
	@echo "📋 Viewing backend logs (Ctrl+C to exit)..."
	docker-compose logs -f backend

# View frontend logs only
logs-fe:
	@echo "📋 Viewing frontend logs (Ctrl+C to exit)..."
	docker-compose logs -f frontend

# Check backend health
health:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "Backend Health:"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Backend is not responding"
	@echo ""
	@echo "Frontend Health:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000 || echo "❌ Frontend is not responding"
	@echo ""
	@echo "Docker Health Status:"
	@docker-compose ps

# Clean up everything
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker-compose rm -f
	@echo "✅ Cleanup complete"

# Deep clean (remove images too)
clean-all: clean
	@echo "🧹 Removing Docker images..."
	docker rmi resume-adapter-backend resume-adapter-frontend 2>/dev/null || true
	@echo "✅ Deep cleanup complete"

# Install local dependencies (for development without Docker)
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && python -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Dependencies installed"

# Run backend locally (development mode)
dev-be:
	@echo "🔧 Starting backend in development mode..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "⚠️  Created backend/.env - add your OpenAI API key!"; \
	fi
	cd backend && \
		. venv/bin/activate && \
		uvicorn main:app --reload --port 8000

# Run frontend locally (development mode)
dev-fe:
	@echo "🔧 Starting frontend in development mode..."
	cd frontend && npm run dev

# Run tests (placeholder for future tests)
test:
	@echo "🧪 Running tests..."
	@echo "⚠️  No tests configured yet"
	@echo "   Add tests to backend/tests/ and frontend/src/__tests__/"

# Quick rebuild (when you change code)
rebuild:
	@echo "🔨 Rebuilding containers..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Rebuild complete"

# Show status of containers
status:
	@echo "📊 Container Status:"
	@docker-compose ps

# Open application in browser (works on macOS and Linux)
open:
	@echo "🌐 Opening application in browser..."
	@command -v open >/dev/null 2>&1 && open http://localhost:3000 || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:3000 || \
	echo "Please open http://localhost:3000 in your browser"

# Show API documentation in browser
api-docs:
	@echo "📚 Opening API documentation..."
	@command -v open >/dev/null 2>&1 && open http://localhost:8000/docs || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8000/docs || \
	echo "Please open http://localhost:8000/docs in your browser"

# Production build (optimized)
prod: build
	@echo "🚀 Starting in production mode..."
	docker-compose up -d
	@echo "✅ Production mode active"