test:
	docker exec -it $(docker ps -q --filter="name=backend") pytest

dev:
	docker-compose -f docker-compose.yml up --build -d

prod:
	docker-compose -f docker-compose-prod.yml up --build -d --scale backend=2

restart:
	docker-compose -f docker-compose.yml restart

logs:
	docker-compose -f docker-compose.yml logs -f

down:
	docker-compose -f docker-compose.yml down --remove-orphans

.PHONY: dev down test restart logs
