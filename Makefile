initial:
	set -eux
	git submodule update
	git submodule foreach git checkout master
	git submodule foreach git pull origin master

dev: initial
	docker-compose -f docker-compose-dev.yml up -d


full: initial
	docker-compose -f docker-compose.yml up -d


.PHONY: dev full initial