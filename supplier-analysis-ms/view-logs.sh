#!/bin/bash

# Default to showing app logs
SERVICE=${1:-supplier-analysis-ms}
LINES=${2:-50}

echo "📋 Showing logs for $SERVICE (last $LINES lines)..."
echo "Press Ctrl+C to stop following logs"
echo ""

case $SERVICE in
    "app" | "ms" | "microservice")
        docker-compose logs -f --tail=$LINES supplier-analysis-ms
        ;;
    "neo4j" | "db" | "database")
        docker-compose logs -f --tail=$LINES supplier_neo4j
        ;;
    "all" | "both")
        docker-compose logs -f --tail=$LINES
        ;;
    *)
        docker-compose logs -f --tail=$LINES $SERVICE
        ;;
esac
