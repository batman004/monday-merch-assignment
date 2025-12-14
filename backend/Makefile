.PHONY: build up down logs restart clean teardown

# Build and start containers
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f api

# Restart services
restart:
	docker-compose restart

# Stop and remove volumes (clean database)
clean:
	docker-compose down -v

# Teardown: stop, remove containers, volumes, and images
teardown:
	docker-compose down -v --rmi all

# Run migrations (if needed in future)
migrate:
	docker-compose exec api python -c "from app.core.database import Base, engine; import asyncio; asyncio.run(engine.begin()).run_sync(Base.metadata.create_all)"

# Access API container shell
shell:
	docker-compose exec api /bin/bash

# Access database
db-shell:
	docker-compose exec db psql -U postgres -d monday_merch

# Single command to build, start, and show logs
fly:
	$(MAKE) build
	$(MAKE) up
	$(MAKE) logs
