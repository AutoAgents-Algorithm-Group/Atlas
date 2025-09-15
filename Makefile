# Fullstack FrankStyle Makefile

.PHONY: install dev prod

# Default target shows available commands
help:
	@echo "Available commands:"
	@echo "  make install     - Install frontend and backend dependencies"
	@echo "  make dev         - Start development environment"
	@echo "  make prod        - Start production environment"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@echo "🔧 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "🔧 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed successfully!"

# Development environment
dev:
	@echo "🚀 Starting development environment..."
	@echo "📱 Frontend will be available at http://localhost:4000"
	@echo "🔧 Backend will be available at http://localhost:9000"
	@echo "📚 API Documentation at http://localhost:9000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop both services"
	@trap 'kill %1 %2' INT; \
	cd backend && uvicorn API.main:app --host 0.0.0.0 --port 8000 --reload & \
	cd frontend && npm run dev & \
	wait

# Production environment
prod:
	@echo "🚀 Starting production services inside container..."
	@echo "Starting backend service..."
	cd backend && uvicorn API.main:app --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend service..."
	cd frontend && npm start &
	@echo "✅ Production services started inside container!"
	@echo "📱 Application: http://localhost:4000"
	@echo "🔧 API: http://localhost:9000"
	wait