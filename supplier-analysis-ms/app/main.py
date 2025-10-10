import logging
import os
import time
import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from neo4j.exceptions import ServiceUnavailable

from app.api.routes import router as api_router
from app.database import neo4j_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def wait_for_neo4j():
    """
    Wait for Neo4j to become available
    """
    max_retries = 30
    retry_interval = 2  # seconds
    
    for i in range(max_retries):
        try:
            logger.info(f"Attempting to connect to Neo4j (attempt {i+1}/{max_retries})...")
            # Try to make a simple query to check if Neo4j is ready
            neo4j_db.run_query("RETURN 1 as test")
            logger.info("Successfully connected to Neo4j!")
            return True
        except ServiceUnavailable as e:
            logger.warning(f"Neo4j not yet available: {str(e)}")
            time.sleep(retry_interval)
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {str(e)}")
            time.sleep(retry_interval)
    
    logger.error(f"Failed to connect to Neo4j after {max_retries} attempts")
    return False

# Create the FastAPI application
app = FastAPI(
    title="Supplier Analysis Microservice",
    description="Microservice for analyzing supplier quality and reputation",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(api_router, prefix="/api")

# Startup event
@app.on_event("startup")
def startup_db_client():
    """
    Create necessary constraints in Neo4j when the application starts.
    """
    try:
        # Wait for Neo4j to become available before proceeding
        if not wait_for_neo4j():
            logger.error("Could not connect to Neo4j, but continuing startup...")
            # We continue anyway to allow the app to start, it will try to reconnect on requests
        
        logger.info("Creating Neo4j constraints...")
        neo4j_db.create_constraints()
        logger.info("Neo4j constraints created successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Shutdown event
@app.on_event("shutdown")
def shutdown_db_client():
    """
    Close the Neo4j connection when the application shuts down.
    """
    try:
        neo4j_db.close()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")

# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint to check if the service is running.
    """
    return {
        "message": "Welcome to the Supplier Analysis Microservice",
        "status": "active",
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health")
def health():
    """
    Health check endpoint for monitoring services.
    """
    try:
        # Check if Neo4j is responsive
        neo4j_db.run_query("RETURN 1 as test")
        return {"status": "healthy", "neo4j_status": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "degraded", "neo4j_status": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8001)),
        reload=True if os.environ.get("DEBUG", "false").lower() == "true" else False
    )
