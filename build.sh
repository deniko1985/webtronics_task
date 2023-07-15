#!/bin/bash
mv ./src/.env_example ./src/.env
mkdir ./src/temp/
docker-compose up --build -d
docker exec -it postgres_webtronics_task psql -U postgres -p 5445 -c "create database webtronics_test"
docker restart webtronics_task
bash ./run_migration.sh