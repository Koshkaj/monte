test:
	go test -v -cover ./... --race

dev:
	docker-compose -f docker-compose-dev.yml up --build -d

prod:
	docker-compose -f docker-compose.yml up --build -d --scale backend=2 parser=2

down:
	docker-compose -f docker-compose-dev.yml down --remove-orphans 

proto:
	protoc --go_out=./src/grpc --go_opt=paths=import --go-grpc_out=./src/grpc --go-grpc_opt=paths=import src/proto/*.proto

.PHONY: migrateup migratedown sqlc test run proto
