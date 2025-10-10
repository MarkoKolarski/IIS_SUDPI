import pytest
import requests
import os
import json
from datetime import date, timedelta

# Set the base URL for the API
BASE_URL = os.environ.get("API_URL", "http://localhost:8001/api")

def test_health_check():
    """Test that the API is running"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_get_supplier():
    """Test creating a supplier and getting it back"""
    # Create a test supplier
    supplier_data = {
        "supplier_id": 9999,
        "name": "Test Supplier",
        "email": "test@example.com",
        "pib": "TEST12345",
        "material_name": "Test Material",
        "price": 100.50,
        "delivery_time": 10,
        "rating": 8.5,
        "rating_date": date.today().isoformat(),
        "selected": False
    }
    
    # Create the supplier
    response = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data)
    assert response.status_code == 200
    assert "Supplier created successfully" in response.json()["message"]
    
    # Get the supplier back
    response = requests.get(f"{BASE_URL}/suppliers/{supplier_data['supplier_id']}")
    assert response.status_code == 200
    assert response.json()["name"] == supplier_data["name"]
    assert response.json()["email"] == supplier_data["email"]
    
    # Clean up - delete the supplier
    response = requests.delete(f"{BASE_URL}/suppliers/{supplier_data['supplier_id']}")
    assert response.status_code == 200

def test_create_complaint_and_update_rating():
    """Test creating a complaint and checking if it updates the supplier's rating"""
    # Create a test supplier
    supplier_data = {
        "supplier_id": 9998,
        "name": "Rating Test Supplier",
        "email": "rating@example.com",
        "pib": "RATE12345",
        "material_name": "Rating Material",
        "price": 200.75,
        "delivery_time": 15,
        "rating": 9.0,
        "rating_date": date.today().isoformat(),
        "selected": False
    }
    
    # Create the supplier
    response = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data)
    assert response.status_code == 200
    
    # Create a complaint against this supplier
    complaint_data = {
        "supplier_id": supplier_data["supplier_id"],
        "controller_id": 1,
        "problem_description": "Test complaint for rating adjustment",
        "severity": 8,  # High severity to ensure rating drops
        "duration": 5,
        "status": "prijem"
    }
    
    # Create the complaint
    response = requests.post(f"{BASE_URL}/complaints/", json=complaint_data)
    assert response.status_code == 200
    
    # Verify rating was updated
    assert "previous_rating" in response.json()
    assert "new_rating" in response.json()
    assert float(response.json()["previous_rating"]) > float(response.json()["new_rating"])
    
    # Check the supplier's updated rating
    response = requests.get(f"{BASE_URL}/suppliers/{supplier_data['supplier_id']}")
    assert response.status_code == 200
    assert float(response.json()["rating"]) < supplier_data["rating"]
    
    # Clean up
    requests.delete(f"{BASE_URL}/suppliers/{supplier_data['supplier_id']}")

def test_get_alternative_suppliers():
    """Test getting alternative suppliers for a material"""
    # Create several test suppliers for the same material
    material_name = "Common Test Material"
    supplier_ids = []
    
    for i in range(1, 4):
        supplier_data = {
            "supplier_id": 9990 + i,
            "name": f"Alternative Supplier {i}",
            "email": f"alt{i}@example.com",
            "pib": f"ALT{i}12345",
            "material_name": material_name,
            "price": 100.0 + (i * 50),
            "delivery_time": 10 + i,
            "rating": 6.0 + i,
            "rating_date": date.today().isoformat(),
            "selected": False
        }
        response = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data)
        assert response.status_code == 200
        supplier_ids.append(supplier_data["supplier_id"])
    
    # Get alternative suppliers for this material
    response = requests.get(f"{BASE_URL}/analysis/alternative-suppliers/{material_name}")
    assert response.status_code == 200
    assert "suppliers" in response.json()
    assert len(response.json()["suppliers"]) >= 3
    
    # Clean up
    for supplier_id in supplier_ids:
        requests.delete(f"{BASE_URL}/suppliers/{supplier_id}")

def test_get_supplier_report():
    """Test generating a supplier report PDF"""
    # Create a test supplier
    supplier_data = {
        "supplier_id": 9997,
        "name": "Report Test Supplier",
        "email": "report@example.com",
        "pib": "REPORT12345",
        "material_name": "Report Material",
        "price": 150.25,
        "delivery_time": 12,
        "rating": 7.5,
        "rating_date": date.today().isoformat(),
        "selected": False
    }
    
    # Create the supplier
    response = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data)
    assert response.status_code == 200
    
    # Add some certificates
    certificate_data = {
        "supplier_id": supplier_data["supplier_id"],
        "certificate_id": 9001,
        "name": "Test Certificate",
        "type": "ISO",
        "issue_date": (date.today() - timedelta(days=365)).isoformat(),
        "expiry_date": (date.today() + timedelta(days=365)).isoformat()
    }
    response = requests.post(f"{BASE_URL}/certificates/", json=certificate_data)
    assert response.status_code == 200
    
    # Generate the report
    response = requests.get(f"{BASE_URL}/reports/supplier/{supplier_data['supplier_id']}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert len(response.content) > 0
    
    # Clean up
    requests.delete(f"{BASE_URL}/suppliers/{supplier_data['supplier_id']}")

def test_supplier_comparison_report():
    """Test generating a supplier comparison report"""
    # Create test suppliers
    supplier_ids = []
    material_name = "Comparison Material"
    
    for i in range(1, 3):
        supplier_data = {
            "supplier_id": 9980 + i,
            "name": f"Comparison Supplier {i}",
            "email": f"comp{i}@example.com",
            "pib": f"COMP{i}12345",
            "material_name": material_name,
            "price": 100.0 + (i * 30),
            "delivery_time": 5 + i,
            "rating": 5.0 + i,
            "rating_date": date.today().isoformat(),
            "selected": False
        }
        response = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data)
        assert response.status_code == 200
        supplier_ids.append(supplier_data["supplier_id"])
    
    # Generate comparison report
    response = requests.post(
        f"{BASE_URL}/reports/supplier-comparison",
        json={"supplier_ids": supplier_ids}
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert len(response.content) > 0
    
    # Clean up
    for supplier_id in supplier_ids:
        requests.delete(f"{BASE_URL}/suppliers/{supplier_id}")

def test_risk_patterns():
    """Test the risk patterns analysis"""
    # Create test suppliers
    supplier_id = 9970
    supplier_data = {
        "supplier_id": supplier_id,
        "name": "Risk Test Supplier",
        "email": "risk@example.com",
        "pib": "RISK12345",
        "material_name": "Risk Material",
        "price": 125.75,
        "delivery_time": 14,
        "rating": 8.0,
        "rating_date": date.today().isoformat(),
        "selected": False
    }
    
    # Create the supplier
    response = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data)
    assert response.status_code == 200
    
    # Create multiple complaints to generate risk pattern
    for i in range(3):  # 3 complaints should make it high risk
        complaint_data = {
            "supplier_id": supplier_id,
            "controller_id": 1,
            "problem_description": f"Risk pattern test complaint {i+1}",
            "severity": 8,  # High severity
            "duration": 5,
            "status": "prijem"
        }
        response = requests.post(f"{BASE_URL}/complaints/", json=complaint_data)
        assert response.status_code == 200
    
    # Test risk pattern analysis
    response = requests.get(f"{BASE_URL}/analysis/risk-patterns")
    assert response.status_code == 200
    
    # Find our test supplier in the results
    found = False
    for pattern in response.json().get("patterns", []):
        if pattern.get("supplier_id") == supplier_id:
            found = True
            assert pattern.get("risk_level") == "high_risk"
            assert pattern.get("complaint_count") == 3
    
    assert found, "Test supplier not found in risk patterns"
    
    # Clean up
    requests.delete(f"{BASE_URL}/suppliers/{supplier_id}")
