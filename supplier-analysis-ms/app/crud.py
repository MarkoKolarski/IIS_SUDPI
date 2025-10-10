from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging

from app.database import neo4j_db
from neo4j.exceptions import ClientError, ConstraintError

# Supplier CRUD Operations
def create_supplier(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new supplier node in Neo4j
    """
    try:
        # Always check if supplier with this ID already exists first
        supplier_id = supplier_data['supplier_id']
        existing = get_supplier(supplier_id)
        
        if existing:
            # If supplier exists, update it instead of creating a new one
            logging.info(f"Supplier with ID {supplier_id} already exists. Updating instead.")
            return update_supplier(supplier_id, supplier_data)
        
        # Convert date to string format for Neo4j if needed
        if isinstance(supplier_data.get('rating_date'), date):
            supplier_data['rating_date'] = supplier_data['rating_date'].isoformat()
            
        query = """
        CREATE (s:Supplier {
            supplier_id: $supplier_id,
            name: $name,
            email: $email,
            pib: $pib,
            material_name: $material_name,
            price: $price,
            delivery_time: $delivery_time,
            rating: $rating,
            rating_date: $rating_date,
            selected: $selected
        })
        RETURN s
        """
        
        result = neo4j_db.execute_write(query, supplier_data)
        return result
    except ClientError as e:
        # More specific handling for Neo4j constraint violations
        if "ConstraintValidation" in str(e) and "already exists" in str(e):
            logging.warning(f"Constraint violation detected: {e}. Attempting to update instead.")
            try:
                return update_supplier(supplier_data['supplier_id'], supplier_data)
            except Exception as update_error:
                logging.error(f"Error updating supplier after constraint violation: {update_error}")
                raise ValueError(f"Failed to create or update supplier: {update_error}")
        else:
            logging.error(f"Neo4j client error: {e}")
            raise ValueError(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error creating supplier: {e}")
        raise ValueError(f"Error creating supplier: {e}")

def get_supplier(supplier_id: int) -> Dict[str, Any]:
    """
    Get a supplier by ID
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})
    RETURN s
    """
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return result[0]['s'] if result else None

def get_all_suppliers() -> List[Dict[str, Any]]:
    """
    Get all suppliers
    """
    query = """
    MATCH (s:Supplier)
    RETURN s
    """
    result = neo4j_db.execute_read(query)
    return [record['s'] for record in result]

def update_supplier(supplier_id: int, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a supplier
    """
    set_clauses = []
    for key, value in supplier_data.items():
        if value is not None:
            if isinstance(value, date):
                value = value.isoformat()
            set_clauses.append(f"s.{key} = ${key}")
            
    if not set_clauses:
        return get_supplier(supplier_id)
        
    query = f"""
    MATCH (s:Supplier {{supplier_id: $supplier_id}})
    SET {', '.join(set_clauses)}
    RETURN s
    """
    
    params = supplier_data.copy()
    params['supplier_id'] = supplier_id
    
    result = neo4j_db.execute_write(query, params)
    return result

def delete_supplier(supplier_id: int) -> bool:
    """
    Delete a supplier
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})
    DETACH DELETE s
    """
    neo4j_db.execute_write(query, {"supplier_id": supplier_id})
    return True

# Material CRUD Operations
def create_material(material_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new material node
    """
    query = """
    CREATE (m:Material {
        material_id: $material_id,
        name: $name,
        price: $price,
        quality_score: $quality_score
    })
    RETURN m
    """
    result = neo4j_db.execute_write(query, material_data)
    return result

def link_supplier_to_material(supplier_id: int, material_id: str) -> Dict[str, Any]:
    """
    Create relationship between supplier and material
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})
    MATCH (m:Material {material_id: $material_id})
    MERGE (s)-[r:SUPPLIES]->(m)
    ON CREATE SET r.since = date()
    RETURN s, r, m
    """
    result = neo4j_db.execute_write(query, {
        "supplier_id": supplier_id,
        "material_id": material_id
    })
    return result

# Complaint CRUD Operations
def create_complaint(complaint_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new complaint node and link it to a supplier
    """
    # First create the complaint node
    create_query = """
    CREATE (c:Complaint {
        complaint_id: $complaint_id,
        problem_description: $problem_description,
        severity: $severity,
        duration: $duration,
        status: $status,
        reception_date: $reception_date,
        controller_id: $controller_id,
        supplier_id: $supplier_id
    })
    RETURN c
    """
    
    # Convert date to string
    if isinstance(complaint_data.get('reception_date'), date):
        complaint_data['reception_date'] = complaint_data['reception_date'].isoformat()
    else:
        complaint_data['reception_date'] = datetime.now().date().isoformat()
    
    # Create the complaint
    result = neo4j_db.execute_write(create_query, complaint_data)
    
    # Now create the relationship between supplier and complaint
    relation_query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})
    MATCH (c:Complaint {complaint_id: $complaint_id})
    CREATE (s)-[r:HAS_COMPLAINT]->(c)
    RETURN s, r, c
    """
    
    neo4j_db.execute_write(relation_query, {
        "supplier_id": complaint_data["supplier_id"],
        "complaint_id": complaint_data["complaint_id"]
    })
    
    return result

def get_supplier_complaints(supplier_id: int) -> List[Dict[str, Any]]:
    """
    Get all complaints for a supplier
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})-[:HAS_COMPLAINT]->(c:Complaint)
    RETURN c
    """
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return [record['c'] for record in result]

# Certificate CRUD Operations
def create_certificate(certificate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new certificate node and link it to a supplier
    """
    create_query = """
    CREATE (cert:Certificate {
        certificate_id: $certificate_id,
        name: $name,
        type: $type,
        issue_date: $issue_date,
        expiry_date: $expiry_date,
        supplier_id: $supplier_id
    })
    RETURN cert
    """
    
    # Convert dates to string
    if isinstance(certificate_data.get('issue_date'), date):
        certificate_data['issue_date'] = certificate_data['issue_date'].isoformat()
    
    if isinstance(certificate_data.get('expiry_date'), date):
        certificate_data['expiry_date'] = certificate_data['expiry_date'].isoformat()
    
    # Create the certificate
    result = neo4j_db.execute_write(create_query, certificate_data)
    
    # Create the relationship between supplier and certificate
    relation_query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})
    MATCH (cert:Certificate {certificate_id: $certificate_id})
    CREATE (s)-[r:HAS_CERTIFICATE]->(cert)
    RETURN s, r, cert
    """
    
    neo4j_db.execute_write(relation_query, {
        "supplier_id": certificate_data["supplier_id"],
        "certificate_id": certificate_data["certificate_id"]
    })
    
    return result

def get_supplier_certificates(supplier_id: int) -> List[Dict[str, Any]]:
    """
    Get all certificates for a supplier
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})-[:HAS_CERTIFICATE]->(cert:Certificate)
    RETURN cert
    """
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return [record['cert'] for record in result]

# Complex Query 1: Find alternative suppliers for a material
def find_alternative_suppliers(material_name: str, min_rating: float = 0.0) -> List[Dict[str, Any]]:
    """
    Find alternative suppliers for a specific material with rating above the threshold
    """
    query = """
    MATCH (s:Supplier)
    WHERE s.material_name = $material_name AND s.rating >= $min_rating
    RETURN s
    ORDER BY s.rating DESC
    """
    result = neo4j_db.execute_read(query, {
        "material_name": material_name,
        "min_rating": min_rating
    })
    return [record['s'] for record in result]

# Complex Query 2: Find suppliers with similar materials but better ratings
def find_better_suppliers(supplier_id: int, rating_increase: float = 1.0) -> List[Dict[str, Any]]:
    """
    Find suppliers that offer similar materials but have better ratings
    """
    query = """
    MATCH (s1:Supplier {supplier_id: $supplier_id})
    MATCH (s2:Supplier)
    WHERE s2.material_name = s1.material_name
      AND s2.rating >= s1.rating + $rating_increase
      AND s2.supplier_id <> s1.supplier_id
    RETURN s2,
           s2.rating - s1.rating AS rating_difference,
           CASE WHEN s2.price <= s1.price THEN 'cheaper_or_equal' ELSE 'more_expensive' END AS price_comparison
    ORDER BY s2.rating DESC
    """
    result = neo4j_db.execute_read(query, {
        "supplier_id": supplier_id,
        "rating_increase": rating_increase
    })
    
    suppliers = []
    for record in result:
        supplier = record['s2']
        supplier['rating_difference'] = record['rating_difference']
        supplier['price_comparison'] = record['price_comparison']
        suppliers.append(supplier)
        
    return suppliers

# Complex Query 3: Analyze supplier relationships through materials
def analyze_supplier_relationships(supplier_id: int) -> Dict[str, Any]:
    """
    Analyze relationships between suppliers through common materials
    """
    query = """
    MATCH (s1:Supplier {supplier_id: $supplier_id})
    MATCH (s2:Supplier)
    WHERE s2.supplier_id <> s1.supplier_id
      AND s2.material_name = s1.material_name
    WITH s1, s2,
         CASE WHEN s2.price < s1.price THEN 'cheaper'
              WHEN s2.price = s1.price THEN 'same_price'
              ELSE 'more_expensive' END AS price_relation,
         CASE WHEN s2.rating > s1.rating THEN 'better_rating'
              WHEN s2.rating = s1.rating THEN 'same_rating'
              ELSE 'worse_rating' END AS rating_relation
    
    RETURN s1.name AS supplier_name, s1.material_name,
           collect({
             id: s2.supplier_id,
             name: s2.name,
             price_relation: price_relation,
             rating_relation: rating_relation,
             material: s2.material_name,
             price: s2.price,
             rating: s2.rating
           }) AS related_suppliers
    """
    
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return result[0] if result else None

# Complex Query 4: Track supplier rating history
def track_supplier_rating_history(supplier_id: int) -> List[Dict[str, Any]]:
    """
    Track the rating history of a supplier based on complaints
    Uses WITH clause to track rating changes over time
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})-[r:HAS_COMPLAINT]->(c:Complaint)
    WITH s, c
    ORDER BY c.reception_date ASC
    WITH s.name AS supplier_name, 
         collect({date: c.reception_date, severity: c.severity, description: c.problem_description}) AS complaints
    
    RETURN supplier_name, complaints,
           10 - reduce(acc = 0.0, 
                       c IN complaints | 
                       acc + (CASE
                               WHEN c.severity <= 3 THEN 0.3 * c.severity
                               WHEN c.severity <= 7 THEN 0.3 * c.severity
                               ELSE 0.3 * c.severity 
                              END)) AS estimated_current_rating
    """
    
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return result[0] if result else None

# Complex Query 5: Identify risk patterns in supplier complaints
def identify_supplier_risk_patterns() -> List[Dict[str, Any]]:
    """
    Identify patterns of risk based on complaint frequency, severity and types
    Uses WITH for aggregation and transformations
    """
    query = """
    MATCH (s:Supplier)-[:HAS_COMPLAINT]->(c:Complaint)
    WITH s, count(c) AS complaint_count, 
         avg(c.severity) AS avg_severity,
         collect(c.problem_description) AS problems
    
    WITH s, complaint_count, avg_severity, problems,
         CASE
           WHEN complaint_count >= 3 AND avg_severity >= 8 THEN 'high_risk'
           WHEN complaint_count >= 2 OR avg_severity >= 5 THEN 'medium_risk'
           ELSE 'low_risk'
         END AS risk_level
    
    RETURN s.supplier_id AS supplier_id,
           s.name AS supplier_name,
           s.material_name AS material,
           complaint_count,
           avg_severity,
           problems,
           risk_level
    ORDER BY 
      CASE risk_level
        WHEN 'high_risk' THEN 1
        WHEN 'medium_risk' THEN 2
        ELSE 3
      END, complaint_count DESC
    """
    
    result = neo4j_db.execute_read(query)
    return result
