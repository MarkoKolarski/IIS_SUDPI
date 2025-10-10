#!/bin/sh
set -e

echo "Waiting for Neo4j to be ready..."
# Give Neo4j a chance to start up (simple wait approach)
sleep 15

echo "Checking and fixing duplicate supplier IDs..."
python -m scripts.seed_data

echo "Starting supplier analysis microservice..."
exec "$@"
