#!/bin/bash
docker-compose down --volumes --remove-orphans
docker system prune -af
docker volume prune -f
docker-compose build --no-cache
docker-compose up
