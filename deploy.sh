#!/bin/bash

set -e

IMAGE_NAME="shopping-cart-api"
DATABASE_URL="${DATABASE_URL}"

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

echo "=========================================="
echo "  BLUE-GREEN DEPLOYMENT"
echo "=========================================="

# Determine which color is currently live
BLUE_RUNNING=$(docker ps --filter "name=cart-blue" --format "{{.Names}}" 2>/dev/null)
GREEN_RUNNING=$(docker ps --filter "name=cart-green" --format "{{.Names}}" 2>/dev/null)

if [ -n "$BLUE_RUNNING" ]; then
    CURRENT="blue"
    NEW="green"
    CURRENT_PORT=8001
    NEW_PORT=8002
else
    CURRENT="green"
    NEW="blue"
    CURRENT_PORT=8002
    NEW_PORT=8001
fi

echo "Current live: $CURRENT (port $CURRENT_PORT)"
echo "Deploying to: $NEW (port $NEW_PORT)"

# Step 1: Build new image
echo ""
echo "Step 1: Building new Docker image..."
docker build -t $IMAGE_NAME .

# Step 2: Stop and remove the NEW container if it exists from a previous deploy
echo ""
echo "Step 2: Cleaning up old $NEW container..."
docker stop "cart-$NEW" 2>/dev/null || true
docker rm "cart-$NEW" 2>/dev/null || true

# Step 3: Start the NEW container
echo ""
echo "Step 3: Starting $NEW container on port $NEW_PORT..."
docker run -d \
    -p $NEW_PORT:8000 \
    -e DATABASE_URL="$DATABASE_URL" \
    --name "cart-$NEW" \
    $IMAGE_NAME

# Step 4: Wait for NEW container to be healthy
echo ""
echo "Step 4: Waiting for $NEW container to be healthy..."
sleep 10

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$NEW_PORT/ 2>/dev/null)

if [ "$HEALTH_CHECK" != "200" ]; then
    echo "ERROR: $NEW container is not healthy (HTTP $HEALTH_CHECK)"
    echo "Rolling back - stopping $NEW container"
    docker stop "cart-$NEW" 2>/dev/null || true
    docker rm "cart-$NEW" 2>/dev/null || true
    exit 1
fi

echo "$NEW container is healthy!"

# Step 5: Switch Nginx to point to NEW container
echo ""
echo "Step 5: Switching traffic to $NEW..."
sudo tee /etc/nginx/conf.d/shopping-cart.conf > /dev/null << NGINX_EOF
upstream backend {
    server 127.0.0.1:$NEW_PORT;
}

server {
    listen 8000;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX_EOF

sudo nginx -s reload

echo "Traffic switched to $NEW!"

# Step 6: Stop old container
echo ""
echo "Step 6: Stopping old $CURRENT container..."
docker stop "cart-$CURRENT" 2>/dev/null || true
docker rm "cart-$CURRENT" 2>/dev/null || true

echo ""
echo "=========================================="
echo "  DEPLOYMENT COMPLETE"
echo "  Live: $NEW (port $NEW_PORT)"
echo "=========================================="