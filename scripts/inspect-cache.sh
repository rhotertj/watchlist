#!/bin/bash
set -e

ENV=${1:-dev}

if [ "$ENV" = "prod" ]; then
    CONTAINER="wa-redis-prod"
elif [ "$ENV" = "dev" ]; then
    CONTAINER="wa-redis-dev"
else
    echo "Usage: $0 [dev|prod]"
    echo "Default: dev"
    exit 1
fi

if ! docker ps | grep -q "$CONTAINER"; then
    echo "Error: Redis container ($CONTAINER) is not running"
    exit 1
fi

echo "=== Redis Cache Info ($ENV) ==="
echo ""
echo "Memory Usage:"
docker exec "$CONTAINER" redis-cli INFO memory | grep "used_memory_human"
echo ""
echo "Key Statistics:"
docker exec "$CONTAINER" redis-cli INFO keyspace
echo ""
echo "Sample Keys:"
docker exec "$CONTAINER" redis-cli --scan --pattern "*" | head -20
echo ""
echo "Total Keys:"
docker exec "$CONTAINER" redis-cli DBSIZE
