#!/bin/bash
set -e

echo "Waiting for Neo4j and microservice to be ready..."
sleep 10

echo "Initializing database with sample data..."
docker exec supplier-analysis-ms python -m app.init_db

echo "Checking if the service is available..."
curl http://localhost:8001/api/health

echo "Database initialization complete. Service should now be accessible from the frontend."
