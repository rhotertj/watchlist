#!/bin/bash
set -e

# Things to watch out for:
# docker containers for dev and prod need to exist for us to copy to and from their volumes
# /data/dump.rdb is automatically loaded at container startup by redis
# dev may not be running when copying, dump would be overwritten at shutdown


echo "### Syncing Redis cache from production to development..."

# Start prod redis, to copy files
docker compose -f docker-compose.prod.yaml up -d redis --force-recreate

echo "### Creating Redis backup from production..."
docker exec wa-redis-prod redis-cli SAVE

DUMP_DIR="tmp-cache-sync"
mkdir -p $DUMP_DIR

# Copy from prod volume
docker cp wa-redis-prod:/data/dump.rdb "$DUMP_DIR/dump.rdb"

# create container without starting it, inject dump
docker compose -f docker-compose.dev.yaml up -d  --force-recreate --no-start redis
docker cp "$DUMP_DIR/dump.rdb" "wa-redis-dev:/data/"

echo "### Starting development Redis..."
docker compose -f docker-compose.dev.yaml up -d redis

echo "### ✓ Cache sync complete!"

make inspect-cache-dev
