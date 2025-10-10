import logging
import time
import os
import sys
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_neo4j_connection():
    """Test connection to Neo4j"""
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            for record in result:
                logger.info(f"Connection successful: {record['test']}")
                
        driver.close()
        return True
    except ServiceUnavailable as e:
        logger.warning(f"Neo4j not available: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error connecting to Neo4j: {str(e)}")
        return False

def wait_for_neo4j(max_retries=30, retry_interval=2):
    """Wait for Neo4j to be ready"""
    for i in range(max_retries):
        logger.info(f"Attempting to connect to Neo4j (attempt {i+1}/{max_retries})...")
        if check_neo4j_connection():
            logger.info("Neo4j is ready!")
            return True
        time.sleep(retry_interval)
    
    logger.error(f"Failed to connect to Neo4j after {max_retries} attempts")
    return False

if __name__ == "__main__":
    if wait_for_neo4j():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
