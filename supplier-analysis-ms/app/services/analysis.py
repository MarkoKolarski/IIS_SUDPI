from typing import List, Dict, Any, Optional
from app.database import neo4j_db
import logging

class SupplierAnalysisService:
    @staticmethod
    def get_supplier_analytics(supplier_id: int) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a supplier
        """
        query = """
        MATCH (s:Supplier {supplier_id: $supplier_id})
        OPTIONAL MATCH (s)-[:HAS_COMPLAINT]->(c:Complaint)
        OPTIONAL MATCH (s)-[:HAS_CERTIFICATE]->(cert:Certificate)
        
        WITH s, 
             count(c) AS complaint_count,
             collect(c {.*, id: id(c)}) AS complaints,
             collect(cert {.*, id: id(cert)}) AS certificates
        
        RETURN s {.*, id: id(s)},
               complaint_count,
               complaints,
               certificates,
               CASE 
                 WHEN complaint_count = 0 THEN 'low_risk'
                 WHEN complaint_count <= 2 THEN 'medium_risk'
                 ELSE 'high_risk'
               END AS risk_assessment
        """
        
        result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
        return result[0] if result else None

    @staticmethod
    def analyze_complaint_trends(days: int = 90) -> List[Dict[str, Any]]:
        """
        Analyze complaint trends over a period of time
        """
        query = """
        MATCH (c:Complaint)
        WHERE date(c.reception_date) >= date() - duration({days: $days})
        WITH date(c.reception_date) AS complaint_date,
             count(c) AS daily_complaints
        
        RETURN complaint_date,
               daily_complaints,
               avg(daily_complaints) OVER (
                   ORDER BY complaint_date
                   ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
               ) AS seven_day_moving_avg
        ORDER BY complaint_date
        """
        
        return neo4j_db.execute_read(query, {"days": days})

    @staticmethod
    def get_supplier_ranking_by_material(material_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ranking of suppliers by material type, rating and price
        """
        where_clause = "WHERE s.material_name = $material_name" if material_name else ""
        
        query = f"""
        MATCH (s:Supplier)
        {where_clause}
        OPTIONAL MATCH (s)-[:HAS_COMPLAINT]->(c:Complaint)
        WITH s.material_name AS material_name,
             s,
             count(c) AS complaint_count
        
        WITH material_name,
             collect({{
                supplier_id: s.supplier_id,
                name: s.name,
                rating: s.rating,
                price: s.price,
                complaint_count: complaint_count,
                score: s.rating - (complaint_count * 0.2)
             }}) AS suppliers
        
        UNWIND suppliers AS supplier
        WITH material_name, supplier
        ORDER BY supplier.score DESC
        
        WITH material_name, collect(supplier) AS ranked_suppliers
        
        RETURN material_name, ranked_suppliers
        """
        
        params = {"material_name": material_name} if material_name else {}
        return neo4j_db.execute_read(query, params)

    @staticmethod
    def find_supplier_relationships(supplier_id: int) -> Dict[str, Any]:
        """
        Find relationships between suppliers through common materials and prices
        """
        query = """
        MATCH (s1:Supplier {supplier_id: $supplier_id})
        MATCH (s2:Supplier)
        WHERE s2.supplier_id <> s1.supplier_id
          AND s2.material_name = s1.material_name
        
        WITH s1, s2,
             abs(s1.price - s2.price) / 
                 CASE WHEN s1.price > 0 THEN s1.price ELSE 1 END AS price_similarity,
             abs(s1.rating - s2.rating) / 10 AS rating_difference
        
        WITH s1, s2, price_similarity, rating_difference,
             1 - (price_similarity * 0.7 + rating_difference * 0.3) AS similarity_score
        
        WHERE similarity_score > 0.6
        
        RETURN s1.supplier_id AS source_id,
               s1.name AS source_name,
               s1.material_name AS material,
               collect({
                 supplier_id: s2.supplier_id,
                 name: s2.name,
                 similarity: similarity_score,
                 price_diff_percent: 100 * (s2.price - s1.price) / 
                                    CASE WHEN s1.price > 0 THEN s1.price ELSE 1 END,
                 rating_diff: s2.rating - s1.rating
               }) AS related_suppliers
        ORDER BY s1.material_name
        """
        
        result = neo4j_db.execute_read(query, {"supplier_id": supplier_id})
        return result[0] if result else None

    @staticmethod
    def recommend_alternative_suppliers(supplier_id: int, minimum_rating: float = 5.0) -> List[Dict[str, Any]]:
        """
        Recommend alternative suppliers with better or similar ratings
        """
        query = """
        MATCH (s1:Supplier {supplier_id: $supplier_id})
        MATCH (s2:Supplier)
        WHERE s2.supplier_id <> s1.supplier_id
          AND s2.material_name = s1.material_name
          AND s2.rating >= $minimum_rating
        
        WITH s1, s2,
             (1 - abs(s1.price - s2.price) / CASE WHEN s1.price > 0 THEN s1.price ELSE 1 END) * 50 +
             (s2.rating / 10) * 30 +
             (CASE WHEN s2.delivery_time <= s1.delivery_time THEN 20 ELSE
                  20 * s1.delivery_time / CASE WHEN s2.delivery_time > 0 THEN s2.delivery_time ELSE 1 END
              END) AS score
        
        RETURN s2.supplier_id AS supplier_id,
               s2.name AS name,
               s2.material_name AS material_name,
               s2.price AS price,
               s1.price AS original_price,
               s2.rating AS rating,
               s1.rating AS original_rating,
               s2.delivery_time AS delivery_time,
               s1.delivery_time AS original_delivery_time,
               score,
               CASE
                 WHEN s2.rating > s1.rating AND s2.price <= s1.price THEN 'Better quality and price'
                 WHEN s2.rating > s1.rating AND s2.price > s1.price THEN 'Better quality but more expensive'
                 WHEN s2.rating = s1.rating AND s2.price < s1.price THEN 'Same quality but cheaper'
                 WHEN s2.rating < s1.rating AND s2.price < s1.price THEN 'Lower quality but cheaper'
                 ELSE 'Alternative option'
               END AS recommendation_type
        ORDER BY score DESC
        LIMIT 5
        """
        
        return neo4j_db.execute_read(query, {
            "supplier_id": supplier_id,
            "minimum_rating": minimum_rating
        })
