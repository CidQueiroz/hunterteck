#!/bin/bash
# Deploy HunterTeck to Production

set -e

echo "🚀 Starting HunterTeck Production Deployment..."

# Variables
ENVIRONMENT=${1:-production}
VERSION=$(grep version pyproject.toml | head -1 | cut -d'"' -f2)

echo "📦 Building version: $VERSION"
echo "🎯 Environment: $ENVIRONMENT"

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Run migrations/setup
echo "⚙️ Running setup..."
docker-compose run --rm backend python -m services.lead_extractor.main --setup

# Start services
echo "🟢 Starting services..."
docker-compose up -d

# Health checks
echo "🏥 Running health checks..."
sleep 5

if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo "✅ Deployment successful!"
echo "📊 Frontend: http://localhost:8501"

# Display logs
echo "\n📋 Recent logs:"
docker-compose logs --tail=10
