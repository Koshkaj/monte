#!/bin/sh

set -eux

docker-compose -f docker-compose.prod.yml up --build -d 
