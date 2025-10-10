import logging
import os
import time
import sys
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neo4j.exceptions import ServiceUnavailable
from fastapi.responses import JSONResponse
from neo4j.time import Date as Neo4jDate, DateTime as Neo4jDateTime
from fastapi.encoders import jsonable_encoder
from pydantic.json import ENCODERS_BY_TYPE
from contextlib import asynccontextmanager


# Add custom encoders for Neo4j types
ENCODERS_BY_TYPE[Neo4jDate] = lambda v: date(v.year, v.month, v.day).isoformat()
ENCODERS_BY_TYPE[Neo4jDateTime] = lambda v: f"{v.year:04d}-{v.month:02d}-{v.day:02d}T{v.hour:02d}:{v.minute:02d}:{v.second:02d}.{v.nanosecond // 1000000:03d}Z"

from app.api.routes import router as api_router
from app.database import neo4j_db
from app.api.custom_json_encoders import serialize_neo4j_types

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

# Override default JSONResponse class to handle Neo4j Date objects
class CustomJSONResponse(JSONResponse):
    def render(self, content):
        # Serialize Neo4j types in the content
        if content is not None:
            content = serialize_neo4j_types(content)
            content = jsonable_encoder(content)
        return super().render(content)

# Create the FastAPI application
app = FastAPI(
    title="Supplier Analysis Microservice",
    description="Microservice for analyzing supplier quality and reputation",
    version="1.0.0",
    default_response_class=CustomJSONResponse
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(api_router, prefix="/api")

# Startup event
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
def shutdown_db_client():
    """
    Close the Neo4j connection when the application shuts down.
    """
    try:
        neo4j_db.close()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting up...")
    startup_db_client
    
    yield  # ← app runs while paused here
    
    # Shutdown logic
    print("Shutting down...")
    shutdown_db_client
    
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
