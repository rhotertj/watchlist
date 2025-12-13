#!/bin/bash
set -e

echo "Clearing development Redis cache..."

if ! docker ps | grep -q wa-redis-dev; then
    echo "Error: Development Redis container (wa-redis-dev) is not running"
    echo "Start it with: docker-compose -f docker-compose.dev.yaml up -d redis"
    exit 1
fi

docker exec wa-redis-dev redis-cli FLUSHALL

echo "✓ Development cache cleared!"
