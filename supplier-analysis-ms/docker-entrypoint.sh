#!/bin/sh
set -e

echo "Waiting for Neo4j to be ready..."
# Give Neo4j a chance to start up (simple wait approach)
sleep 15

echo "Starting supplier analysis microservice..."
exec "$@"
