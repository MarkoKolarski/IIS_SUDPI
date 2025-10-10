#!/bin/bash
set -e

echo "⚡ Quick restart for development..."

# Function to check if container exists
container_exists() {
    docker ps -a --format "table {{.Names}}" | grep -q "^$1$"
}

# Function to check if container is running
container_running() {
    docker ps --format "table {{.Names}}" | grep -q "^$1$"
}

# Stop containers
echo "⏹️  Stopping containers..."
if container_running "supplier-analysis-ms"; then
    docker-compose stop supplier-analysis-ms
else
    echo "Container supplier-analysis-ms not running"
fi

# Remove only the app container to force rebuild
echo "🔄 Removing app container..."
if container_exists "supplier-analysis-ms"; then
    docker-compose rm -f supplier-analysis-ms
else
    echo "Container supplier-analysis-ms doesn't exist"
fi

# Check if required files exist
echo "🔍 Checking required files..."
required_files=(
    "app/api/custom_json_encoders.py"
    "app/api/__init__.py"
    "app/__init__.py"
    "requirements.txt"
    "Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required files present"

# Rebuild and start
echo "🔨 Rebuilding and starting..."
docker-compose up --build -d supplier-analysis-ms

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Check if container is running
if container_running "supplier-analysis-ms"; then
    echo "✅ Container started successfully"
    
    # Wait a bit more for the app to initialize
    echo "⏳ Waiting for application to initialize..."
    sleep 10
    
    # Test the health endpoint
    echo "🧪 Testing health endpoint..."
    for i in {1..12}; do
        if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
            echo "✅ Application is healthy!"
            break
        else
            echo "⏳ Waiting for application... (attempt $i/12)"
            sleep 5
        fi
    done
    
    echo "⚡ Quick restart complete!"
    echo ""
    echo "📋 Showing recent logs..."
    docker-compose logs --tail=20 supplier-analysis-ms
else
    echo "❌ Container failed to start"
    echo "📋 Showing logs for debugging..."
    docker-compose logs --tail=50 supplier-analysis-ms
    exit 1
fi
