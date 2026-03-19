.PHONY: up down logs

up:
	docker compose up --build

down:
	docker compose down --remove-orphans

logs:
	docker compose logs -f

