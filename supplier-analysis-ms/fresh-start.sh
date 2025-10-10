#!/bin/bash
set -e

echo "🔄 Starting fresh Docker Compose setup..."

# Check if required files exist
echo "🔍 Checking required files..."
required_files=(
    "app/api/custom_json_encoders.py"
    "app/api/__init__.py"
    "app/__init__.py"
    "app/main.py"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    printf '%s\n' "${missing_files[@]}"
    echo ""
    echo "Please ensure all required files are present before running fresh-start.sh"
    exit 1
fi

echo "✅ All required files present"

# Stop all containers
echo "⏹️  Stopping all containers..."
docker-compose down

# Remove containers and networks
echo "🗑️  Removing containers and networks..."
docker-compose down --remove-orphans

# Build without cache
echo "🔨 Building images without cache..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 20

# Check Neo4j health first
echo "🏥 Checking Neo4j health..."
for i in {1..10}; do
    if curl -s http://localhost:7474 > /dev/null 2>&1; then
        echo "✅ Neo4j is accessible!"
        break
    else
        echo "⏳ Waiting for Neo4j... (attempt $i/10)"
        sleep 3
    fi
done

# Check API health
echo "🧪 Testing API health..."
for i in {1..15}; do
    if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "✅ API is healthy!"
        echo "🎯 Testing suppliers endpoint..."
        if curl -s http://localhost:8001/api/suppliers | head -c 100 > /dev/null 2>&1; then
            echo "✅ Suppliers endpoint working!"
        fi
        break
    else
        echo "⏳ Waiting for API... (attempt $i/15)"
        sleep 5
    fi
done

echo "🎉 Fresh start complete!"
echo ""
echo "Available endpoints:"
echo "  - API Docs: http://localhost:8001/docs"
echo "  - Health Check: http://localhost:8001/api/health"
echo "  - Neo4j Browser: http://localhost:7474 (neo4j/password)"
echo "  - Suppliers: http://localhost:8001/api/suppliers"
echo "  - Alternative: http://localhost:8001/suppliers (redirects to /api/suppliers)"
echo ""
echo "📊 Current status:"
echo "  - Neo4j: $(curl -s http://localhost:7474 > /dev/null 2>&1 && echo '✅ Running' || echo '❌ Not accessible')"
echo "  - API: $(curl -s http://localhost:8001/api/health > /dev/null 2>&1 && echo '✅ Running' || echo '❌ Not accessible')"
