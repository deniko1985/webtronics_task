#!/usr/bin/env bash
docker exec -it webtronics_task alembic revision --autogenerate -m "Added required tables"
docker exec -it webtronics_task alembic upgrade head
