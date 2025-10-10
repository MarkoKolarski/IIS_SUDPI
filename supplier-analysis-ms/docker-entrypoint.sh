#!/bin/sh
set -e

echo "Waiting for Neo4j to be ready..."
# Simple wait approach to give Neo4j time to start
sleep 15

echo "Starting supplier analysis microservice..."
exec "$@"
