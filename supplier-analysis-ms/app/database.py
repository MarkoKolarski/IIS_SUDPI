from neo4j import GraphDatabase
import logging
from typing import Any, Dict, List, Optional
import os
import time
from neo4j.exceptions import ServiceUnavailable

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
            cls._instance.connect()
        return cls._instance

    def connect(self, max_retries=5, retry_interval=2):
        """
        Connect to Neo4j with retry mechanism
        """
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        username = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(uri, auth=(username, password))
                # Test the connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"Connected to Neo4j at {uri}")
                return True
            except ServiceUnavailable as e:
                logger.warning(f"Neo4j connection attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
            except Exception as e:
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
        
        logger.error(f"Failed to connect to Neo4j after {max_retries} attempts")
        return False

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed")

    def run_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.
        """
        try:
            if self.driver is None:
                self.connect()
                
            if self.driver is None:
                logger.error("Cannot run query, Neo4j connection not available")
                return []
                
            with self.driver.session() as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            # Try to reconnect
            self.connect()
            raise

    def execute_write(self, query: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a Cypher write query and return the result.
        """
        try:
            if self.driver is None:
                self.connect()
                
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
            self.connect()
            raise

    def execute_read(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher read query and return the results.
        """
        try:
            if self.driver is None:
                self.connect()
                
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
            self.connect()
            raise

    def create_constraints(self):
        """
        Create necessary constraints in Neo4j.
        """
        if self.driver is None:
            logger.warning("Cannot create constraints, Neo4j connection not available")
            return False
            
        constraints = [
            "CREATE CONSTRAINT supplier_id IF NOT EXISTS FOR (s:Supplier) REQUIRE s.supplier_id IS UNIQUE",
            "CREATE CONSTRAINT material_id IF NOT EXISTS FOR (m:Material) REQUIRE m.material_id IS UNIQUE",
            "CREATE CONSTRAINT complaint_id IF NOT EXISTS FOR (c:Complaint) REQUIRE c.complaint_id IS UNIQUE",
            "CREATE CONSTRAINT certificate_id IF NOT EXISTS FOR (cert:Certificate) REQUIRE cert.certificate_id IS UNIQUE"
        ]
        
        success = True
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint creation error: {e}")
                    success = False
                    
        return success

neo4j_db = Neo4jConnection()
