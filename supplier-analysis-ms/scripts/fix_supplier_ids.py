"""
Script to fix duplicate supplier IDs in Neo4j database
"""
import sys
import os
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import neo4j_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_duplicate_supplier_ids():
    """Find all suppliers with duplicate IDs"""
    query = """
    MATCH (s1:Supplier)
    MATCH (s2:Supplier)
    WHERE s1.supplier_id = s2.supplier_id AND id(s1) <> id(s2)
    RETURN s1.supplier_id as id, collect(id(s1)) as node_ids
    """
    result = neo4j_db.run_query(query)
    return result

def get_max_supplier_id():
    """Get the maximum supplier ID currently in use"""
    query = "MATCH (s:Supplier) RETURN max(s.supplier_id) as max_id"
    result = neo4j_db.run_query(query)
    return result[0]['max_id'] if result else 0

def fix_duplicate_supplier_ids():
    """Fix suppliers with duplicate IDs by assigning new IDs"""
    logger.info("Looking for suppliers with duplicate IDs...")
    duplicates = find_duplicate_supplier_ids()
    
    if not duplicates:
        logger.info("No duplicates found!")
        return 0
    
    logger.info(f"Found {len(duplicates)} duplicate supplier IDs")
    
    # Get the maximum current ID
    max_id = get_max_supplier_id()
    next_id = max_id + 1
    
    fixed_count = 0
    
    for duplicate in duplicates:
        dup_id = duplicate['id']
        node_ids = duplicate['node_ids']
        
        # Skip the first node (keep original ID) and update the rest
        for i, node_id in enumerate(node_ids[1:], 1):
            new_id = next_id
            next_id += 1
            
            # Update the supplier ID
            update_query = """
            MATCH (s:Supplier) 
            WHERE id(s) = $node_id 
            SET s.supplier_id = $new_id
            """
            neo4j_db.run_query(update_query, {"node_id": node_id, "new_id": new_id})
            
            logger.info(f"Updated duplicate ID {dup_id} to {new_id} for node {node_id}")
            fixed_count += 1
    
    logger.info(f"Fixed {fixed_count} duplicate supplier IDs")
    return fixed_count

if __name__ == "__main__":
    try:
        count = fix_duplicate_supplier_ids()
        logger.info(f"Total duplicates fixed: {count}")
    except Exception as e:
        logger.error(f"Error fixing duplicate supplier IDs: {e}")
        sys.exit(1)
