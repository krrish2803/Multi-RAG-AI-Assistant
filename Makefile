.PHONY: up down build seed logs test lint eval

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build --no-cache

logs:
	docker compose logs -f backend frontend

seed:
	docker compose exec backend python -m scripts.seed_users
	docker compose exec backend python -m scripts.seed_documents

test:
	docker compose exec backend pytest -v

lint:
	docker compose exec backend ruff check .

eval:
	docker compose exec backend python -m scripts.run_evaluation

restart:
	docker compose restart backend frontend

clean:
	docker compose down
	docker compose build --no-cache
