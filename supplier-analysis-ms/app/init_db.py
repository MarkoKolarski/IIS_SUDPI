import logging
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.wait_for_neo4j import wait_for_neo4j
from scripts.seed_data import clear_database, create_suppliers, create_materials, create_complaints, create_certificates

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize the database with sample data
    """
    try:
        # Wait for Neo4j to be available
        if not wait_for_neo4j():
            logger.error("Failed to connect to Neo4j")
            sys.exit(1)
        
        # Clear database
        logger.info("Clearing existing data...")
        clear_database()
        
        # Create sample data
        logger.info("Creating sample data...")
        suppliers = create_suppliers(20)
        materials = create_materials(suppliers)
        complaints = create_complaints(suppliers, 3)
        certificates = create_certificates(suppliers, 2)
        
        logger.info(f"Database initialization completed successfully!")
        logger.info(f"Created {len(suppliers)} suppliers")
        logger.info(f"Created {len(materials)} materials")
        logger.info(f"Created {len(complaints)} complaints")
        logger.info(f"Created {len(certificates)} certificates")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    initialize_database()
