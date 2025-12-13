#!/bin/bash

ENV=${1:-dev}

if [ "$ENV" = "prod" ]; then
    REDIS_CONTAINER="wa-redis-prod"
    BACKEND_CONTAINER="wa-backend-prod"
    BACKEND_PORT="8100"
elif [ "$ENV" = "dev" ]; then
    REDIS_CONTAINER="wa-redis-dev"
    BACKEND_CONTAINER="wa-backend-dev"
    BACKEND_PORT="8000"
else
    echo "Usage: $0 [dev|prod]"
    echo "Default: dev"
    exit 1
fi

echo "=== Health Check ($ENV) ==="
echo ""

# Check Redis
echo -n "Redis ($REDIS_CONTAINER): "
if docker ps | grep -q "$REDIS_CONTAINER"; then
    if docker exec "$REDIS_CONTAINER" redis-cli ping > /dev/null 2>&1; then
        echo "✓ Running"
    else
        echo "✗ Container running but Redis not responding"
    fi
else
    echo "✗ Not running"
fi

# Check Backend
echo -n "Backend ($BACKEND_CONTAINER): "
if docker ps | grep -q "$BACKEND_CONTAINER"; then
    echo "✓ Container running"
    echo -n "  API health endpoint: "
    if curl -s "http://localhost:$BACKEND_PORT/health" | grep -q "healthy"; then
        echo "✓ Responding"
    else
        echo "✗ Not responding"
    fi
else
    echo "✗ Not running"
fi

# Check Frontend (dev only)
if [ "$ENV" = "dev" ]; then
    echo -n "Frontend (dev server): "
    if curl -s "http://localhost:5173" > /dev/null 2>&1; then
        echo "✓ Running on port 5173"
    else
        echo "- Not running (start with: make dev-frontend)"
    fi
fi

echo ""
echo "=== Port Status ==="
if [ "$ENV" = "dev" ]; then
    echo "Backend API:  http://localhost:8000"
    echo "Frontend:     http://localhost:5173"
    echo "Redis:        localhost:6380"
else
    echo "Backend API:  http://localhost:8100"
    echo "Redis:        localhost:6379"
fi
