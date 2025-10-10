#!/bin/bash
set -e

echo "Waiting for Neo4j to be ready..."
# Wait for Neo4j to be ready
python -m app.wait_for_neo4j

echo "Seeding database with sample data..."
python -m scripts.seed_data

echo "Database initialization complete."
