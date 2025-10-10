#!/bin/bash
set -e

echo "☢️  NUCLEAR RESET - This will destroy EVERYTHING!"
echo "This will remove:"
echo "  - All containers"
echo "  - All images related to this project"
echo "  - All volumes (including Neo4j data)"
echo "  - All networks"
echo "  - Docker build cache"
echo "  - Python cache files"
echo ""
read -p "Are you sure? Type 'YES' to continue: " confirmation

if [ "$confirmation" != "YES" ]; then
    echo "❌ Nuclear reset cancelled."
    exit 1
fi

echo "💣 Beginning nuclear reset..."

# Stop and remove everything related to docker-compose
echo "⏹️  Stopping and removing all compose services..."
docker-compose down --volumes --remove-orphans --rmi all 2>/dev/null || true

# Remove project-specific images
echo "🗑️  Removing project images..."
docker images | grep -E "(supplier-analysis|neo4j)" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

# Remove all stopped containers
echo "🧹 Removing all stopped containers..."
docker container prune -f

# Remove all unused images
echo "🖼️  Removing unused images..."
docker image prune -a -f

# Remove all unused volumes
echo "💾 Removing unused volumes..."
docker volume prune -f

# Remove all unused networks
echo "🌐 Removing unused networks..."
docker network prune -f

# Remove build cache
echo "🗂️  Removing build cache..."
docker builder prune -a -f

# Remove any remaining project volumes by name
echo "💽 Removing project volumes..."
docker volume ls | grep -E "(supplier|neo4j)" | awk '{print $2}' | xargs -r docker volume rm 2>/dev/null || true

# Clean Python cache
echo "🐍 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# System cleanup
echo "🧽 Final system cleanup..."
docker system prune -a -f --volumes

echo ""
echo "☢️  NUCLEAR RESET COMPLETE!"
echo "🔥 Everything has been obliterated!"
echo ""
echo "To start fresh, run:"
echo "  ./fresh-start.sh"
echo ""
echo "Or manually:"
echo "  docker-compose build --no-cache"
echo "  docker-compose up"
