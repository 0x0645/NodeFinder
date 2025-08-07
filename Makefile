.PHONY: help build up down restart logs logs-django logs-celery logs-flower clean test test-local shell migrate makemigrations collectstatic superuser

# Docker compose files
COMPOSE_FILE = docker-compose.local.yml
COMPOSE_PROD_FILE = docker-compose.yml

# Default target
help:
	@echo "🗺️  Node Finder - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "📦 SETUP & MANAGEMENT:"
	@echo "  make setup         - 🚀 First-time setup (build + migrate + superuser)"
	@echo "  make up            - ▶️  Start all services in development mode"
	@echo "  make down          - ⏹️  Stop all services"
	@echo "  make restart       - 🔄 Restart all services"
	@echo "  make build         - 🔨 Build all Docker images"
	@echo "  make clean         - 🧹 Stop services and remove volumes (DESTRUCTIVE!)"
	@echo ""
	@echo "🔍 MONITORING & LOGS:"
	@echo "  make logs          - 📜 Show logs for all services"
	@echo "  make logs-django   - 🐍 Show Django logs only"
	@echo "  make logs-celery   - 🌿 Show Celery worker logs only"
	@echo "  make logs-flower   - 🌸 Show Flower logs only"
	@echo "  make status        - ℹ️  Show running containers status"
	@echo ""
	@echo "🧪 TESTING & QUALITY:"
	@echo "  make test          - ✅ Run tests in Django container"
	@echo "  make test-local    - 📊 Run tests with coverage report"
	@echo "  make test-nodes    - 🔗 Run only nodes app tests"
	@echo ""
	@echo "🛠️  DEVELOPMENT TOOLS:"
	@echo "  make shell         - 🐚 Open Django shell in container"
	@echo "  make migrate       - 📋 Run database migrations"
	@echo "  make makemigrations- 📝 Create new Django migrations"
	@echo "  make collectstatic - 📦 Collect static files"
	@echo "  make superuser     - 👤 Create Django superuser account"
	@echo ""
	@echo "🌐 QUICK ACCESS:"
	@echo "  make dev           - 🏃 Quick development start (up + logs)"
	@echo "  make api-docs      - 📚 Open API documentation in browser"
	@echo "  make celery-flower - 🌸 Open Flower (Celery monitor) in browser"
	@echo ""
	@echo "🏭 PRODUCTION:"
	@echo "  make prod-up       - 🚀 Start production services"
	@echo "  make prod-down     - ⏹️  Stop production services"
	@echo "  make prod-build    - 🔨 Build production images"
	@echo "  make prod-logs     - 📜 Show production logs"
	@echo ""
	@echo "💡 TIPS:"
	@echo "   • First time? Run: make setup"
	@echo "   • Daily dev work: make up, then make api-docs"
	@echo "   • Stuck? Try: make clean && make setup"
	@echo "   • Check what's running: make status"

# Development commands
up:
	docker-compose -f $(COMPOSE_FILE) up -d

down:
	docker-compose -f $(COMPOSE_FILE) down

restart:
	docker-compose -f $(COMPOSE_FILE) restart

build:
	docker-compose -f $(COMPOSE_FILE) build

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-django:
	docker-compose -f $(COMPOSE_FILE) logs -f django

logs-celery:
	docker-compose -f $(COMPOSE_FILE) logs -f celeryworker

logs-flower:
	docker-compose -f $(COMPOSE_FILE) logs -f flower

# Production commands
up-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) up -d

down-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) down

logs-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

# Django management commands
shell:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py shell

migrate:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py migrate

makemigrations:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py makemigrations

collectstatic:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py collectstatic --noinput

superuser:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py createsuperuser

# Testing commands
test:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py test --settings=config.settings.test

test-local:
	docker-compose -f $(COMPOSE_FILE) exec django coverage run manage.py test --settings=config.settings.test
	docker-compose -f $(COMPOSE_FILE) exec django coverage report
	docker-compose -f $(COMPOSE_FILE) exec django coverage html

test-nodes:
	docker-compose -f $(COMPOSE_FILE) exec django python manage.py test nodes

# Utility commands
clean:
	docker-compose -f $(COMPOSE_FILE) down -v
	docker system prune -f

status:
	docker-compose -f $(COMPOSE_FILE) ps

# Database commands
db-reset:
	docker-compose -f $(COMPOSE_FILE) down -v
	docker-compose -f $(COMPOSE_FILE) up -d postgres
	sleep 5
	docker-compose -f $(COMPOSE_FILE) up -d

# Celery commands
celery-shell:
	docker-compose -f $(COMPOSE_FILE) exec celeryworker celery -A config.celery_app shell

celery-flower:
	@echo "Flower is available at: http://localhost:5555"
	@echo "Username: local"
	@echo "Password: local"

# API documentation
api-docs:
	@echo "API documentation is available at: http://localhost:8000/api/docs/"

# Development setup
setup: build up migrate
	@echo "Development environment is ready!"
	@echo "Django admin: http://localhost:8000/admin/"
	@echo "API docs: http://localhost:8000/api/docs/"
	@echo "Flower: http://localhost:5555"

# Quick development workflow
dev: down build up logs-django
