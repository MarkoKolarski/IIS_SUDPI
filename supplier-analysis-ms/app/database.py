from neo4j import GraphDatabase
import logging
from typing import Any, Dict, List, Optional
import os
import time
from neo4j.exceptions import ServiceUnavailable

# Configure logging to ensure it's set up
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jConnection:
    """
    Neo4j database connection class.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
            cls._instance.driver = None
            cls._instance._connected = False
        return cls._instance

    def connect(self, max_retries=5, retry_interval=2):
        """
        Connect to Neo4j with retry mechanism
        """
        if self._connected and self.driver is not None:
            logger.info("Neo4j already connected, skipping connection attempt")
            return True
            
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        username = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        logger.info(f"Attempting to connect to Neo4j at {uri} with user {username}")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connection attempt {attempt+1}/{max_retries}")
                self.driver = GraphDatabase.driver(uri, auth=(username, password))
                # Test the connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"Successfully connected to Neo4j at {uri}")
                self._connected = True
                return True
            except ServiceUnavailable as e:
                logger.warning(f"Neo4j connection attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
            except Exception as e:
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
        
        logger.error(f"Failed to connect to Neo4j after {max_retries} attempts")
        self._connected = False
        return False

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None
            self._connected = False
            logger.info("Neo4j connection closed")

    def _ensure_connection(self):
        """Ensure we have a valid connection before executing queries"""
        if not self._connected or self.driver is None:
            logger.info("No active connection, attempting to connect...")
            self.connect()

    def run_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.
        """
        try:
            self._ensure_connection()
                
            if self.driver is None:
                logger.error("Cannot run query, Neo4j connection not available")
                return []
                
            with self.driver.session() as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            # Try to reconnect
            self._connected = False
            self.connect()
            raise

    def execute_write(self, query: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a Cypher write query and return the result.
        """
        try:
            self._ensure_connection()
                
            if self.driver is None:
                logger.error("Cannot execute write, Neo4j connection not available")
                return None
                
            with self.driver.session() as session:
                result = session.write_transaction(
                    lambda tx: tx.run(query, params).data()
                )
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Neo4j write error: {e}")
            # Try to reconnect
            self._connected = False
            self.connect()
            raise

    def execute_read(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher read query and return the results.
        """
        try:
            self._ensure_connection()
                
            if self.driver is None:
                logger.error("Cannot execute read, Neo4j connection not available")
                return []
                
            with self.driver.session() as session:
                result = session.read_transaction(
                    lambda tx: tx.run(query, params).data()
                )
                return result
        except Exception as e:
            logger.error(f"Neo4j read error: {e}")
            # Try to reconnect
            self._connected = False
            self.connect()
            raise

    def create_constraints(self):
        """
        Create necessary constraints in Neo4j.
        """
        if self.driver is None:
            logger.warning("Cannot create constraints, Neo4j connection not available")
            return False
            
        try:
            # First check if constraints already exist
            constraints_query = "SHOW CONSTRAINTS"
            constraints = self.run_query(constraints_query)
            
            # Create unique constraint on supplier_id if it doesn't exist
            if not any(c.get('name') == 'unique_supplier_id' for c in constraints):
                logger.info("Creating unique constraint on Supplier.supplier_id")
                self.run_query("CREATE CONSTRAINT unique_supplier_id IF NOT EXISTS FOR (s:Supplier) REQUIRE s.supplier_id IS UNIQUE")
            
            # Create unique constraint on material_id if it doesn't exist
            if not any(c.get('name') == 'unique_material_id' for c in constraints):
                logger.info("Creating unique constraint on Material.material_id")
                self.run_query("CREATE CONSTRAINT unique_material_id IF NOT EXISTS FOR (m:Material) REQUIRE m.material_id IS UNIQUE")
            
            # Create unique constraint on complaint_id if it doesn't exist
            if not any(c.get('name') == 'unique_complaint_id' for c in constraints):
                logger.info("Creating unique constraint on Complaint.complaint_id")
                self.run_query("CREATE CONSTRAINT unique_complaint_id IF NOT EXISTS FOR (c:Complaint) REQUIRE c.complaint_id IS UNIQUE")
            
            # Create unique constraint on certificate_id if it doesn't exist
            if not any(c.get('name') == 'unique_certificate_id' for c in constraints):
                logger.info("Creating unique constraint on Certificate.certificate_id")
                self.run_query("CREATE CONSTRAINT unique_certificate_id IF NOT EXISTS FOR (cert:Certificate) REQUIRE cert.certificate_id IS UNIQUE")
            
            logger.info("All constraints created or already exist")
            return True
        except Exception as e:
            logger.error(f"Error creating constraints: {e}")
            raise

# Remove global instance creation - make it lazy
_neo4j_instance = None

def get_neo4j_connection():
    """Get or create the Neo4j connection instance"""
    global _neo4j_instance
    if _neo4j_instance is None:
        logger.info("Creating Neo4j connection instance")
        _neo4j_instance = Neo4jConnection()
    return _neo4j_instance

# For backward compatibility - create actual instance, not property
neo4j_db = get_neo4j_connection()

def get_db():
    """
    Dependency to get the Neo4j database connection
    """
    try:
        db = get_neo4j_connection()
        yield db
    finally:
        pass  # Connection will be closed on application shutdown
