# 🗺️ Node Finder

> A powerful Django REST API for creating graph networks and finding paths between nodes, with lightning-fast async processing powered by Celery.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/mustafagomaa/nodeFinder/actions/workflows/ci.yml/badge.svg)](https://github.com/mustafagomaa/nodeFinder/actions/workflows/ci.yml)
[![Pre-commit](https://github.com/mustafagomaa/nodeFinder/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/mustafagomaa/nodeFinder/actions/workflows/pre-commit.yml)

## 🌟 What This Does

We've included a handy **Makefile** to make your life easier. Here are the most common commands:

### All Available Commands

Run `make help` to see all available commands:

```
🗺️  Node Finder - Development Commands
========================================

📦 SETUP & MANAGEMENT:
  make setup         - 🚀 First-time setup (build + migrate + superuser)
  make up            - ▶️  Start all services in development mode
  make down          - ⏹️  Stop all services
  make restart       - 🔄 Restart all services
  make build         - 🔨 Build all Docker images
  make clean         - 🧹 Stop services and remove volumes (DESTRUCTIVE!)

🔍 MONITORING & LOGS:
  make logs          - 📜 Show logs for all services
  make logs-django   - 🐍 Show Django logs only
  make logs-celery   - 🌿 Show Celery worker logs only
  make logs-flower   - 🌸 Show Flower logs only
  make status        - ℹ️  Show running containers status

🧪 TESTING & QUALITY:
  make test          - ✅ Run tests in Django container
  make test-local    - 📊 Run tests with coverage report
  make test-nodes    - 🔗 Run only nodes app tests

🛠️  DEVELOPMENT TOOLS:
  make shell         - 🐚 Open Django shell in container
  make migrate       - 📋 Run database migrations
  make makemigrations- 📝 Create new Django migrations
  make collectstatic - 📦 Collect static files
  make superuser     - 👤 Create Django superuser account

🌐 QUICK ACCESS:
  make dev           - 🏃 Quick development start (up + logs)
  make api-docs      - 📚 Open API documentation in browser
  make celery-flower - 🌸 Open Flower (Celery monitor) in browser

🏭 PRODUCTION:
  make prod-up       - 🚀 Start production services
  make prod-down     - ⏹️  Stop production services
  make prod-build    - 🔨 Build production images
  make prod-logs     - 📜 Show production logs

💡 TIPS:
   • First time? Run: make setup
   • Daily dev work: make up, then make api-docs
   • Stuck? Try: make clean && make setup
   • Check what's running: make status
```

### Manual Docker Setup (if you prefer the old school way)

```bash
# 1. Build and start all services
docker-compose -f docker-compose.local.yml up --build

# 2. In another terminal, run migrations
docker-compose -f docker-compose.local.yml exec django python manage.py migrate

# 3. Create a superuser (optional)
docker-compose -f docker-compose.local.yml exec django python manage.py createsuperuser
```

## 🌐 What You Get

Once everything's running, you can access:

- **🔗 API Base**: http://localhost:8000/api/
- **📚 Interactive Docs**: http://localhost:8000/api/docs/ (Swagger UI - try it out!)
- **🌸 Task Monitor**: http://localhost:5555/ (Flower - see your async tasks)
- **⚙️ Admin Panel**: http://localhost:8000/admin/ (Django admin)
- **📬 Postman Collection**: [Test all endpoints with our ready-to-use collection](https://www.postman.com/red-shuttle-467151/workspace/nodefinder/collection/23296523-529c9b7e-d196-422d-96c9-a6f2a891361e?action=share&source=copy-link&creator=23296523)

## 🎯 Try It Out!

### Option 1: Use The Postman Collection (Recommended! 📬)

Import our [Postman collection](https://www.postman.com/red-shuttle-467151/workspace/nodefinder/collection/23296523-529c9b7e-d196-422d-96c9-a6f2a891361e?action=share&source=copy-link&creator=23296523) for a ready-to-use testing environment with all endpoints pre-configured!

### Option 2: curl commands

Here's a quick example to get you started:

```bash
# 1. Create some nodes
curl -X POST http://localhost:8000/api/nodes/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Home"}'

curl -X POST http://localhost:8000/api/nodes/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Work"}'

curl -X POST http://localhost:8000/api/nodes/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Coffee Shop"}'

# 2. Connect them
curl -X POST http://localhost:8000/api/nodes/nodes/connect/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "Home", "to_node": "Coffee Shop"}'

curl -X POST http://localhost:8000/api/nodes/nodes/connect/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "Coffee Shop", "to_node": "Work"}'

# 3. Find the path from Home to Work
curl -X POST http://localhost:8000/api/nodes/path/find/ \
  -H "Content-Type: application/json" \
  -d '{"from_node": "Home", "to_node": "Work"}'

# Result: ["Home", "Coffee Shop", "Work"]
```

Or just visit http://localhost:8000/api/docs/ and try it in the interactive interface!

## 🧪 Testing & Quality

We care about code quality! Here's how to check everything's working:

```bash
# Run all tests
make test

# Run tests with coverage report
make test-local

# Just test the nodes app
make test-nodes

# Check the logs if something's wrong
make logs
```

Our tests cover **90%** of the codebase, so you can trust that things work as expected!

This will show you all available commands organized by category, with helpful descriptions and emojis to make development more enjoyable!

## 🏗️ What's Under the Hood

- **Django 5.1** - The web framework that makes this all possible
- **PostgreSQL** - Reliable database for your nodes and connections
- **Redis** - Lightning-fast broker for async tasks
- **Celery** - Background task processing that scales
- **Nginx** - Production-ready web server
- **Docker** - Everything containerized for easy deployment

## 🤝 Async Processing

We include async pathfinding to demonstrate background task processing:

**Async Path Finding** (`/path/async/`) - Processes path finding with a 5-second delay to simulate complex calculations, perfect for demonstrating long-running background tasks.

Returns a `task_id` that you can use to check results later using `/path/async/result/`!

## 🐞 Troubleshooting

**Services won't start?**

```bash
make clean  # This resets everything
make setup  # Start fresh
```

**Database issues?**

```bash
make down
docker volume prune  # Remove old data
make up
make migrate
```

**Need to see what's happening?**

```bash
make logs          # All services
make logs-django   # Just Django
make logs-celery   # Just Celery worker
```

_Built with ❤️ using Django, Celery, and Red Bull 𓄀_
