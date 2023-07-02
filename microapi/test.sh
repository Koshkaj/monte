#!/bin/sh

set -eux

docker exec -it $(docker ps -q --filter="name=backend") pytest
