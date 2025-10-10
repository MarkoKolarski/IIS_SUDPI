from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging

from app.database import get_neo4j_connection
from neo4j.exceptions import ClientError, ConstraintError

# Get the Neo4j connection instance
def get_db():
    return get_neo4j_connection()

# Add a function to clear the database
def clear_database() -> bool:
    """
    Clear all data from the Neo4j database.
    Returns True if successful, raises an exception otherwise.
    """
    try:
        # Delete all nodes and relationships in the database
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        neo4j_db = get_db()
        neo4j_db.execute_write(query)
        logging.info("Database cleared successfully")
        return True
    except Exception as e:
        logging.error(f"Error clearing database: {e}")
        raise ValueError(f"Failed to clear database: {e}")

# Supplier CRUD Operations
def create_supplier(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new supplier node in Neo4j
    """
    neo4j_db = get_db()
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
    neo4j_db = get_db()
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
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query)
    return [record['s'] for record in result]

def update_supplier(supplier_id: int, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a supplier
    """
    neo4j_db = get_db()
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
    neo4j_db = get_db()
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
    neo4j_db = get_db()
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
    neo4j_db = get_db()
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
    neo4j_db = get_db()
    
    # Generate complaint_id if not provided
    if 'complaint_id' not in complaint_data:
        # Get the highest existing complaint_id and add 1
        max_id_query = """
        MATCH (c:Complaint)
        RETURN COALESCE(MAX(c.complaint_id), 0) AS max_id
        """
        result = neo4j_db.execute_read(max_id_query)
        max_id = result[0]['max_id'] if result else 0
        complaint_data['complaint_id'] = max_id + 1
    
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

# Certificate CRUD Operations
def create_certificate(certificate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new certificate node and link it to a supplier
    """
    neo4j_db = get_db()
    
    try:
        # Check if certificate with this ID already exists
        certificate_id = certificate_data['certificate_id']
        existing = get_certificate(certificate_id)
        
        if existing:
            # If certificate exists, update it instead of creating a new one
            return update_certificate(certificate_id, certificate_data)
        
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
        MERGE (s)-[r:HAS_CERTIFICATE]->(cert)
        RETURN s, r, cert
        """
        
        neo4j_db.execute_write(relation_query, {
            "supplier_id": certificate_data["supplier_id"],
            "certificate_id": certificate_data["certificate_id"]
        })
        
        return result
        
    except ClientError as e:
        # Handle Neo4j constraint violations
        if "ConstraintValidation" in str(e) and "already exists" in str(e):
            logging.warning(f"Certificate constraint violation detected: {e}. Attempting to update instead.")
            try:
                return update_certificate(certificate_data['certificate_id'], certificate_data)
            except Exception as update_error:
                logging.error(f"Error updating certificate after constraint violation: {update_error}")
                raise ValueError(f"Failed to create or update certificate: {update_error}")
        else:
            logging.error(f"Neo4j client error: {e}")
            raise ValueError(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error creating certificate: {e}")
        raise ValueError(f"Error creating certificate: {e}")

def get_certificate(certificate_id: int) -> Dict[str, Any]:
    """
    Get a certificate by ID
    """
    query = """
    MATCH (cert:Certificate {certificate_id: $certificate_id})
    RETURN cert
    """
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query, {"certificate_id": certificate_id})
    return result[0]['cert'] if result else None

def update_certificate(certificate_id: int, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a certificate
    """
    neo4j_db = get_db()
    set_clauses = []
    
    for key, value in certificate_data.items():
        if value is not None and key != 'certificate_id':  # Don't update the ID
            if isinstance(value, date):
                value = value.isoformat()
            set_clauses.append(f"cert.{key} = ${key}")
            
    if not set_clauses:
        return get_certificate(certificate_id)
        
    query = f"""
    MATCH (cert:Certificate {{certificate_id: $certificate_id}})
    SET {', '.join(set_clauses)}
    RETURN cert
    """
    
    params = certificate_data.copy()
    params['certificate_id'] = certificate_id
    
    # Convert dates to strings
    if isinstance(params.get('issue_date'), date):
        params['issue_date'] = params['issue_date'].isoformat()
    if isinstance(params.get('expiry_date'), date):
        params['expiry_date'] = params['expiry_date'].isoformat()
    
    result = neo4j_db.execute_write(query, params)
    return result

def delete_certificate(certificate_id: int) -> bool:
    """
    Delete a certificate
    """
    query = """
    MATCH (cert:Certificate {certificate_id: $certificate_id})
    DETACH DELETE cert
    """
    neo4j_db = get_db()
    neo4j_db.execute_write(query, {"certificate_id": certificate_id})
    return True

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
    neo4j_db = get_db()
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
    neo4j_db = get_db()
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
    
    neo4j_db = get_db()
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
    
    neo4j_db = get_db()
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
    
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query)
    return result

def get_supplier_complaints(supplier_id: int) -> List[Dict[str, Any]]:
    """
    Get all complaints for a supplier
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})-[:HAS_COMPLAINT]->(c:Complaint)
    RETURN c
    """
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return [record['c'] for record in result]

def get_supplier_certificates(supplier_id: int) -> List[Dict[str, Any]]:
    """
    Get all certificates for a supplier
    """
    query = """
    MATCH (s:Supplier {supplier_id: $supplier_id})-[:HAS_CERTIFICATE]->(cert:Certificate)
    RETURN cert
    """
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
    return [record['cert'] for record in result]

# Complex Query 6: Advanced supplier performance analysis with multiple WITH clauses
def analyze_supplier_performance_trends() -> List[Dict[str, Any]]:
    """
    Analyze supplier performance trends using multiple WITH clauses for complex aggregations
    """
    query = """
    MATCH (s:Supplier)
    OPTIONAL MATCH (s)-[:HAS_COMPLAINT]->(c:Complaint)
    OPTIONAL MATCH (s)-[:HAS_CERTIFICATE]->(cert:Certificate)
    
    WITH s, 
         count(c) AS complaint_count,
         avg(c.severity) AS avg_complaint_severity,
         count(cert) AS certificate_count,
         collect(DISTINCT c.reception_date) AS complaint_dates,
         collect(DISTINCT cert.expiry_date) AS cert_expiry_dates
    
    WITH s, complaint_count, avg_complaint_severity, certificate_count,
         CASE 
           WHEN complaint_count = 0 THEN 10.0
           ELSE s.rating - (complaint_count * 0.5) - (avg_complaint_severity * 0.3)
         END AS calculated_performance_score,
         
         // Calculate certificate status
         CASE
           WHEN certificate_count = 0 THEN 'no_certificates'
           WHEN any(expiry IN cert_expiry_dates WHERE date(expiry) < date() + duration({days: 30})) THEN 'certificates_expiring'
           ELSE 'certificates_valid'
         END AS certificate_status,
         
         // Calculate complaint trend
         CASE
           WHEN complaint_count = 0 THEN 'excellent'
           WHEN complaint_count <= 2 AND avg_complaint_severity <= 5 THEN 'good'
           WHEN complaint_count <= 4 OR avg_complaint_severity <= 7 THEN 'concerning'
           ELSE 'critical'
         END AS complaint_trend
    
    WITH s, complaint_count, certificate_count, calculated_performance_score,
         certificate_status, complaint_trend,
         
         // Final composite score calculation
         calculated_performance_score * 0.6 +
         CASE certificate_status
           WHEN 'certificates_valid' THEN 3.0
           WHEN 'certificates_expiring' THEN 1.0
           ELSE 0.0
         END +
         CASE complaint_trend
           WHEN 'excellent' THEN 1.0
           WHEN 'good' THEN 0.5
           WHEN 'concerning' THEN -0.5
           ELSE -1.0
         END AS final_composite_score,
         
         // Performance category
         CASE 
           WHEN calculated_performance_score >= 8.5 AND certificate_status = 'certificates_valid' THEN 'premium'
           WHEN calculated_performance_score >= 7.0 THEN 'reliable'
           WHEN calculated_performance_score >= 5.0 THEN 'acceptable'
           ELSE 'problematic'
         END AS performance_category
    
    RETURN s.supplier_id AS supplier_id,
           s.name AS supplier_name,
           s.material_name AS material,
           s.rating AS original_rating,
           calculated_performance_score,
           final_composite_score,
           performance_category,
           complaint_count,
           certificate_count,
           certificate_status,
           complaint_trend,
           
           // Recommendation based on composite analysis
           CASE performance_category
             WHEN 'premium' THEN 'Highly recommended - excellent track record'
             WHEN 'reliable' THEN 'Recommended - good performance'
             WHEN 'acceptable' THEN 'Consider with caution - average performance'
             ELSE 'Not recommended - performance issues detected'
           END AS recommendation
           
    ORDER BY final_composite_score DESC, s.material_name ASC
    """
    
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query)
    return result

# Complex Query 7: Material market analysis with advanced WITH operations
def analyze_material_market_dynamics() -> List[Dict[str, Any]]:
    """
    Analyze market dynamics for each material using complex WITH operations
    """
    query = """
    MATCH (s:Supplier)
    WITH s.material_name AS material,
         collect(s) AS suppliers,
         count(s) AS supplier_count,
         avg(s.price) AS avg_price,
         min(s.price) AS min_price,
         max(s.price) AS max_price,
         avg(s.rating) AS avg_rating,
         max(s.rating) AS max_rating,
         avg(s.delivery_time) AS avg_delivery_time
    
    WITH material, suppliers, supplier_count, avg_price, min_price, max_price, 
         avg_rating, max_rating, avg_delivery_time,
         
         // Calculate price volatility
         CASE 
           WHEN max_price = min_price THEN 0.0
           ELSE (max_price - min_price) / avg_price * 100
         END AS price_volatility_percent,
         
         // Market competitiveness score
         CASE
           WHEN supplier_count >= 5 THEN 'highly_competitive'
           WHEN supplier_count >= 3 THEN 'competitive'
           WHEN supplier_count = 2 THEN 'limited_competition'
           ELSE 'monopolistic'
         END AS market_competitiveness
    
    WITH material, supplier_count, avg_price, min_price, max_price,
         avg_rating, max_rating, avg_delivery_time, price_volatility_percent, market_competitiveness,
         suppliers,
         
         // Quality vs Price analysis - split into separate operations
         [s IN suppliers WHERE s.rating >= 8.0 AND s.price <= avg_price * 1.1 | s] AS premium_value_suppliers,
         [s IN suppliers WHERE s.price = min_price | s] AS cheapest_suppliers
    
    WITH material, supplier_count, avg_price, min_price, max_price,
         avg_rating, max_rating, avg_delivery_time, price_volatility_percent, market_competitiveness,
         suppliers, premium_value_suppliers, cheapest_suppliers,
         
         // Get highest rated suppliers separately
         [s IN suppliers WHERE s.rating = max_rating | s] AS highest_rated_suppliers
    
    UNWIND suppliers AS supplier
    OPTIONAL MATCH (supplier)-[:HAS_COMPLAINT]->(c:Complaint)
    
    WITH material, supplier_count, avg_price, min_price, max_price,
         avg_rating, avg_delivery_time, price_volatility_percent, market_competitiveness,
         premium_value_suppliers, cheapest_suppliers, highest_rated_suppliers,
         supplier, count(c) AS supplier_complaints
    
    WITH material, supplier_count, avg_price, min_price, max_price,
         avg_rating, avg_delivery_time, price_volatility_percent, market_competitiveness,
         premium_value_suppliers, cheapest_suppliers, highest_rated_suppliers,
         avg(supplier_complaints) AS avg_complaints_per_supplier,
         
         // Market risk assessment
         CASE
           WHEN avg_rating >= 8.0 AND price_volatility_percent <= 20 THEN 'low_risk'
           WHEN avg_rating >= 6.0 AND price_volatility_percent <= 40 THEN 'medium_risk'
           ELSE 'high_risk'
         END AS market_risk
    
    RETURN material,
           supplier_count,
           round(avg_price, 2) AS average_price,
           round(min_price, 2) AS minimum_price,
           round(max_price, 2) AS maximum_price,
           round(avg_rating, 2) AS average_rating,
           round(avg_delivery_time, 1) AS average_delivery_days,
           round(price_volatility_percent, 2) AS price_volatility_percent,
           market_competitiveness,
           market_risk,
           round(avg_complaints_per_supplier, 2) AS avg_complaints_per_supplier,
           size(premium_value_suppliers) AS premium_value_supplier_count,
           size(cheapest_suppliers) AS cheapest_supplier_count,
           size(highest_rated_suppliers) AS highest_rated_supplier_count,
           
           // Strategic recommendations
           CASE market_competitiveness
             WHEN 'highly_competitive' THEN 'Excellent supplier options - negotiate aggressively'
             WHEN 'competitive' THEN 'Good supplier options - standard procurement approach'
             WHEN 'limited_competition' THEN 'Limited options - build relationships with existing suppliers'
             ELSE 'Single/few suppliers - consider supply chain diversification'
           END AS procurement_strategy
           
    ORDER BY supplier_count DESC, average_rating DESC
    """
    
    neo4j_db = get_db()
    result = neo4j_db.execute_read(query)
    return result
