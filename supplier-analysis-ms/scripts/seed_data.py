import sys
import os
import random
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import neo4j_db
from app import crud

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_database():
    """
    Clear all data from the database
    """
    logger.info("Clearing existing data...")
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    neo4j_db.run_query(query)
    logger.info("Database cleared")

def create_suppliers(count=20):
    """
    Create sample suppliers
    """
    logger.info(f"Creating {count} suppliers...")
    
    suppliers = []
    material_names = [
        "Wheat Flour", "Sugar", "Salt", "Yeast", "Butter", 
        "Cocoa Powder", "Vanilla Extract", "Baking Powder", "Milk", "Eggs",
        "Chocolate Chips", "Nuts", "Fruit Jam", "Honey", "Cream", 
        "Coffee Beans", "Tea Leaves", "Rice", "Corn Starch", "Vegetable Oil"
    ]
    
    for i in range(1, count + 1):
        material_name = material_names[i % len(material_names)]
        
        # Generate a price based on material
        base_price = {
            "Wheat Flour": 100, "Sugar": 80, "Salt": 30, "Yeast": 50, "Butter": 200,
            "Cocoa Powder": 300, "Vanilla Extract": 250, "Baking Powder": 70, "Milk": 120, "Eggs": 150,
            "Chocolate Chips": 280, "Nuts": 500, "Fruit Jam": 180, "Honey": 350, "Cream": 220,
            "Coffee Beans": 450, "Tea Leaves": 380, "Rice": 130, "Corn Starch": 90, "Vegetable Oil": 160
        }.get(material_name, 100)
        
        price = round(base_price * (0.8 + random.random() * 0.4), 2)  # +/- 20% variation
        
        # Generate a random rating between 5 and 10
        rating = round(5 + random.random() * 5, 1)
        
        # Generate a random delivery time between 1 and 30 days
        delivery_time = random.randint(1, 30)
        
        # Generate a random rating date in the past 90 days
        rating_date = (date.today() - timedelta(days=random.randint(1, 90))).isoformat()
        
        supplier = {
            "supplier_id": i,
            "name": f"Supplier {i}",
            "email": f"supplier{i}@example.com",
            "pib": f"PIB{100000000 + i}",
            "material_name": material_name,
            "price": price,
            "delivery_time": delivery_time,
            "rating": rating,
            "rating_date": rating_date,
            "selected": random.random() < 0.2  # 20% chance of being selected
        }
        
        try:
            result = crud.create_supplier(supplier)
            suppliers.append(supplier)
            logger.info(f"Created supplier: {supplier['name']} (ID: {supplier['supplier_id']})")
        except Exception as e:
            logger.error(f"Error creating supplier {i}: {e}")
    
    return suppliers

def create_materials(suppliers):
    """
    Create materials based on supplier materials
    """
    logger.info("Creating materials...")
    
    # Get unique materials from suppliers
    unique_materials = set()
    for supplier in suppliers:
        unique_materials.add(supplier["material_name"])
    
    materials = []
    for i, material_name in enumerate(unique_materials, 1):
        material = {
            "material_id": f"MAT{i:03d}",
            "name": material_name,
            "price": round(random.uniform(50, 500), 2),
            "quality_score": round(random.uniform(3, 10), 1)
        }
        
        try:
            result = crud.create_material(material)
            materials.append(material)
            logger.info(f"Created material: {material['name']} (ID: {material['material_id']})")
            
            # Link suppliers of this material to the material node
            for supplier in suppliers:
                if supplier["material_name"] == material_name:
                    crud.link_supplier_to_material(supplier["supplier_id"], material["material_id"])
                    logger.info(f"Linked supplier {supplier['name']} to material {material['name']}")
        except Exception as e:
            logger.error(f"Error creating material {material_name}: {e}")
    
    return materials

def create_complaints(suppliers, count_per_supplier=3):
    """
    Create sample complaints for suppliers
    """
    logger.info(f"Creating complaints ({count_per_supplier} per supplier)...")
    
    complaints = []
    complaint_id = 1
    
    problem_descriptions = [
        "Late delivery", "Damaged packaging", "Wrong quantity delivered",
        "Quality below standards", "Missing documentation", "Improper storage",
        "Material contamination", "Incorrect labeling", "Failed quality test",
        "Inconsistent quality", "Price discrepancy", "Communication issues"
    ]
    
    for supplier in suppliers:
        # Some suppliers have no complaints (good suppliers)
        if random.random() < 0.2:
            continue
            
        # Generate random number of complaints for this supplier (0 to count_per_supplier)
        num_complaints = random.randint(0, count_per_supplier)
        
        for i in range(num_complaints):
            # Generate a random date in the past 180 days
            reception_date = (date.today() - timedelta(days=random.randint(1, 180))).isoformat()
            
            # Generate a random severity (1-10)
            severity = random.randint(1, 10)
            
            # Duration in days
            duration = random.randint(1, 30)
            
            # Status
            status = random.choice(["prijem", "analiza", "odgovor", "zatvaranje"])
            
            # Controller ID (random between 1 and 5)
            controller_id = random.randint(1, 5)
            
            complaint = {
                "complaint_id": complaint_id,
                "problem_description": random.choice(problem_descriptions),
                "severity": severity,
                "duration": duration,
                "status": status,
                "reception_date": reception_date,
                "supplier_id": supplier["supplier_id"],
                "controller_id": controller_id
            }
            
            try:
                result = crud.create_complaint(complaint)
                complaints.append(complaint)
                logger.info(f"Created complaint {complaint_id} for supplier {supplier['name']}")
                complaint_id += 1
            except Exception as e:
                logger.error(f"Error creating complaint for supplier {supplier['supplier_id']}: {e}")
    
    return complaints

def create_certificates(suppliers, count_per_supplier=2):
    """
    Create sample certificates for suppliers
    """
    logger.info(f"Creating certificates ({count_per_supplier} per supplier)...")
    
    certificates = []
    certificate_id = 1
    
    certificate_types = ["ISO", "HACCP", "GMP", "BRC", "IFS", "ostalo"]
    certificate_names = [
        "ISO 9001:2015", "ISO 22000:2018", "HACCP Certification", 
        "Good Manufacturing Practice", "BRC Global Standard for Food Safety", 
        "IFS Food Standard", "Organic Certification", "Non-GMO Certification",
        "Halal Certification", "Kosher Certification", "Vegan Certification"
    ]
    
    for supplier in suppliers:
        # Generate random number of certificates for this supplier (1 to count_per_supplier)
        num_certificates = random.randint(1, count_per_supplier)
        
        # Randomly select certificate names without repeating
        selected_names = random.sample(certificate_names, min(num_certificates, len(certificate_names)))
        
        for i, name in enumerate(selected_names):
            # Issue date: random date in the past 1-5 years
            issue_years_ago = random.randint(1, 5)
            issue_date = (date.today() - timedelta(days=365 * issue_years_ago + random.randint(0, 364))).isoformat()
            
            # Expiry date: issue date + 1-3 years
            expiry_years = random.randint(1, 3)
            expiry_date = (date.today().replace(year=date.today().year - issue_years_ago + expiry_years)).isoformat()
            
            certificate = {
                "certificate_id": certificate_id,
                "name": name,
                "type": random.choice(certificate_types),
                "issue_date": issue_date,
                "expiry_date": expiry_date,
                "supplier_id": supplier["supplier_id"]
            }
            
            try:
                result = crud.create_certificate(certificate)
                certificates.append(certificate)
                logger.info(f"Created certificate {certificate_id} for supplier {supplier['name']}")
                certificate_id += 1
            except Exception as e:
                logger.error(f"Error creating certificate for supplier {supplier['supplier_id']}: {e}")
    
    return certificates

if __name__ == "__main__":
    try:
        # Clear existing data
        clear_database()
        
        # Create constraints
        neo4j_db.create_constraints()
        
        # Create sample data
        suppliers = create_suppliers(20)
        materials = create_materials(suppliers)
        complaints = create_complaints(suppliers, 3)
        certificates = create_certificates(suppliers, 2)
        
        logger.info(f"Data seeding completed successfully!")
        logger.info(f"Created {len(suppliers)} suppliers")
        logger.info(f"Created {len(materials)} materials")
        logger.info(f"Created {len(complaints)} complaints")
        logger.info(f"Created {len(certificates)} certificates")
        
    except Exception as e:
        logger.error(f"Error during data seeding: {e}")
    finally:
        # Close the Neo4j connection
        neo4j_db.close()
