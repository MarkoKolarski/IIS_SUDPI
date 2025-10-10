from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from fastapi.responses import JSONResponse, Response
from typing import List, Dict, Any, Optional
import logging
from datetime import date, datetime
from neo4j.time import Date as Neo4jDate

from app import crud
from app.schemas import (
    SupplierCreate, SupplierUpdate, Supplier,
    ComplaintCreate, ComplaintUpdate, Complaint,
    CertificateCreate, Certificate,
    MaterialCreate, ReportRequest,
    SupplierComparisonRequest, MaterialSuppliersReportRequest
)
from app.services.analysis import SupplierAnalysisService
from app.services.report import ReportGenerator
from app.database import get_neo4j_connection
from app.api.custom_json_encoders import serialize_neo4j_types

router = APIRouter()
analysis_service = SupplierAnalysisService()
report_generator = ReportGenerator()

# Helper function to ensure proper serialization
def safe_serialize(data):
    """Ensure data is properly serialized before returning"""
    return serialize_neo4j_types(data)

# Health check endpoint
@router.get("/health")
def health_check():
    """Check if the service is running"""
    try:
        # Test connection to Neo4j
        neo4j_db = get_neo4j_connection()
        neo4j_db.run_query("RETURN 1 as test")
        return {"status": "ok", "neo4j_status": "connected"}
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/clear", response_model=Dict[str, Any])
def clear_database():
    """Clear the entire database"""
    try:
        crud.clear_database()
        return {"status": "success", "message": "Database cleared"}
    except Exception as e:
        logging.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")

# Supplier endpoints
@router.post("/suppliers/", response_model=Dict[str, Any])
def create_supplier(supplier: SupplierCreate):
    """Create a new supplier"""
    try:
        supplier_dict = supplier.dict()
        # Handle date conversion
        if isinstance(supplier_dict.get('rating_date'), date):
            supplier_dict['rating_date'] = supplier_dict['rating_date'].isoformat()
        
        # First check if supplier exists - if it does, update it
        try:
            existing = crud.get_supplier(supplier_dict['supplier_id'])
            if existing:
                result = crud.update_supplier(supplier_dict['supplier_id'], supplier_dict)
                return {"message": "Supplier updated successfully", "data": safe_serialize(result)}
        except Exception:
            # If error happens during check, continue with create attempt
            pass
            
        result = crud.create_supplier(supplier_dict)
        return {"message": "Supplier created successfully", "data": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error creating supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating supplier: {str(e)}")

@router.get("/suppliers/", response_model=List[Dict[str, Any]])
def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = crud.get_all_suppliers()
        return safe_serialize(suppliers)
    except Exception as e:
        logging.error(f"Error fetching suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching suppliers: {str(e)}")

@router.get("/suppliers/{supplier_id}", response_model=Dict[str, Any])
def get_supplier(supplier_id: int = Path(..., description="The ID of the supplier to get")):
    """Get a supplier by ID"""
    try:
        supplier = crud.get_supplier(supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return safe_serialize(supplier)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching supplier: {str(e)}")

@router.put("/suppliers/{supplier_id}", response_model=Dict[str, Any])
def update_supplier(
    supplier_data: SupplierUpdate,
    supplier_id: int = Path(..., description="The ID of the supplier to update")
):
    """Update a supplier"""
    try:
        # Check if supplier exists
        supplier = crud.get_supplier(supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
            
        # Update the supplier
        result = crud.update_supplier(supplier_id, supplier_data.dict(exclude_unset=True))
        return safe_serialize(result)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating supplier: {str(e)}")

@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int = Path(..., description="The ID of the supplier to delete")):
    """Delete a supplier"""
    try:
        # Check if supplier exists
        supplier = crud.get_supplier(supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
            
        # Delete the supplier
        crud.delete_supplier(supplier_id)
        return {"message": "Supplier deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting supplier: {str(e)}")

# Material endpoints
@router.post("/materials/", response_model=Dict[str, Any])
def create_material(material: MaterialCreate):
    """Create a new material"""
    try:
        material_dict = material.dict()
        result = crud.create_material(material_dict)
        return {"message": "Material created successfully", "data": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error creating material: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating material: {str(e)}")

# Complaint endpoints
@router.post("/complaints/", response_model=Dict[str, Any])
def create_complaint(complaint: ComplaintCreate):
    """Create a new complaint"""
    try:
        complaint_dict = complaint.dict()
        complaint_dict["status"] = "prijem"
        
        # Ensure reception_date is set
        if "reception_date" not in complaint_dict or complaint_dict["reception_date"] is None:
            complaint_dict["reception_date"] = date.today().isoformat()
        elif isinstance(complaint_dict.get('reception_date'), date):
            complaint_dict["reception_date"] = complaint_dict["reception_date"].isoformat()
            
        result = crud.create_complaint(complaint_dict)
        return {"message": "Complaint created successfully", "data": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error creating complaint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating complaint: {str(e)}")

@router.get("/suppliers/{supplier_id}/complaints", response_model=List[Dict[str, Any]])
def get_supplier_complaints(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Get all complaints for a supplier"""
    try:
        complaints = crud.get_supplier_complaints(supplier_id)
        return safe_serialize(complaints)
    except Exception as e:
        logging.error(f"Error fetching complaints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching complaints: {str(e)}")

@router.get("/complaints/", response_model=List[Dict[str, Any]])
def get_all_complaints():
    """Get all complaints"""
    try:
        complaints = crud.get_all_complaints()
        return safe_serialize(complaints)
    except Exception as e:
        logging.error(f"Error fetching all complaints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching all complaints: {str(e)}")

# Certificate endpoints
@router.post("/certificates/", response_model=Dict[str, Any])
def create_certificate(certificate: CertificateCreate):
    """Create a new certificate"""
    try:
        certificate_dict = certificate.dict()
        
        # Generate certificate ID if not provided
        if not certificate_dict.get("certificate_id"):
            # Get max certificate ID from existing certificates
            existing_certificates = crud.get_all_certificates()
            max_id = 0
            for c in existing_certificates:
                if "certificate_id" in c and isinstance(c["certificate_id"], int) and c["certificate_id"] > max_id:
                    max_id = c["certificate_id"]
            certificate_dict["certificate_id"] = max_id + 1
            
        result = crud.create_certificate(certificate_dict)
        
        # Check if it was an update operation
        if "certificate_id" in certificate_dict:
            existing = crud.get_certificate(certificate_dict["certificate_id"])
            if existing:
                return {"message": "Certificate updated successfully", "data": safe_serialize(result)}
        
        return {"message": "Certificate created successfully", "data": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error creating certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating certificate: {str(e)}")

@router.get("/certificates/", response_model=List[Dict[str, Any]])
def get_all_certificates():
    """Get all certificates"""
    try:
        certificates = crud.get_all_certificates()
        return safe_serialize(certificates)
    except Exception as e:
        logging.error(f"Error fetching all certificates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching all certificates: {str(e)}")

@router.get("/certificates/{certificate_id}", response_model=Dict[str, Any])
def get_certificate(certificate_id: int = Path(..., description="The ID of the certificate to get")):
    """Get a certificate by ID"""
    try:
        certificate = crud.get_certificate(certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        return safe_serialize(certificate)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching certificate: {str(e)}")

@router.put("/certificates/{certificate_id}", response_model=Dict[str, Any])
def update_certificate(
    certificate_data: CertificateCreate,
    certificate_id: int = Path(..., description="The ID of the certificate to update")
):
    """Update a certificate"""
    try:
        # Check if certificate exists
        certificate = crud.get_certificate(certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
            
        # Update the certificate
        certificate_dict = certificate_data.dict()
        result = crud.update_certificate(certificate_id, certificate_dict)
        return {"message": "Certificate updated successfully", "data": safe_serialize(result)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating certificate: {str(e)}")

@router.delete("/certificates/{certificate_id}")
def delete_certificate(certificate_id: int = Path(..., description="The ID of the certificate to delete")):
    """Delete a certificate"""
    try:
        # Check if certificate exists
        certificate = crud.get_certificate(certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
            
        # Delete the certificate
        crud.delete_certificate(certificate_id)
        return {"message": "Certificate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting certificate: {str(e)}")

# Analysis endpoints
@router.get("/analysis/alternative-suppliers/{material_name}")
def get_alternative_suppliers(
    material_name: str = Path(..., description="The name of the material"),
    min_rating: float = Query(0.0, description="Minimum rating threshold")
):
    """Find alternative suppliers for a material"""
    try:
        suppliers = crud.find_alternative_suppliers(material_name, min_rating)
        return {"suppliers": safe_serialize(suppliers), "count": len(suppliers)}
    except Exception as e:
        logging.error(f"Error finding alternative suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding alternative suppliers: {str(e)}")

@router.get("/analysis/better-suppliers/{supplier_id}")
def get_better_suppliers(
    supplier_id: int = Path(..., description="The ID of the supplier"),
    rating_increase: float = Query(1.0, description="Minimum rating increase")
):
    """Find suppliers with better ratings for the same material"""
    try:
        suppliers = crud.find_better_suppliers(supplier_id, rating_increase)
        return {"suppliers": safe_serialize(suppliers), "count": len(suppliers)}
    except Exception as e:
        logging.error(f"Error finding better suppliers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding better suppliers: {str(e)}")

@router.get("/analysis/supplier-relationships/{supplier_id}")
def get_supplier_relationships(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Analyze relationships between suppliers through common materials"""
    try:
        result = crud.analyze_supplier_relationships(supplier_id)
        if not result:
            return {"message": "No relationships found", "data": {}}
        return {"data": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error analyzing supplier relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing supplier relationships: {str(e)}")

@router.get("/analysis/rating-history/{supplier_id}")
def get_supplier_rating_history(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Track the rating history of a supplier based on complaints"""
    try:
        result = crud.track_supplier_rating_history(supplier_id)
        if not result:
            return {"message": "No rating history found", "data": {}}
        return {"data": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error fetching supplier rating history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching supplier rating history: {str(e)}")

@router.get("/analysis/risk-patterns")
def get_supplier_risk_patterns():
    """Identify risk patterns in supplier complaints"""
    try:
        result = crud.identify_supplier_risk_patterns()
        return {"patterns": safe_serialize(result), "count": len(result)}
    except Exception as e:
        logging.error(f"Error identifying supplier risk patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error identifying supplier risk patterns: {str(e)}")

@router.get("/analysis/supplier-analytics/{supplier_id}")
def get_supplier_analytics(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Get comprehensive analytics for a supplier"""
    try:
        result = analysis_service.get_supplier_analytics(supplier_id)
        if not result:
            raise HTTPException(status_code=404, detail="Supplier not found or no analytics available")
        return safe_serialize(result)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting supplier analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting supplier analytics: {str(e)}")

@router.get("/analysis/complaint-trends")
def get_complaint_trends(days: int = Query(90, description="Number of days to analyze")):
    """Analyze complaint trends over a period of time"""
    try:
        result = analysis_service.analyze_complaint_trends(days)
        return {"trends": safe_serialize(result), "days_analyzed": days}
    except Exception as e:
        logging.error(f"Error analyzing complaint trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing complaint trends: {str(e)}")

@router.get("/analysis/supplier-ranking")
def get_supplier_ranking(material_name: Optional[str] = Query(None, description="Filter by material name")):
    """Get ranking of suppliers by material, rating, and price"""
    try:
        result = analysis_service.get_supplier_ranking_by_material(material_name)
        return {"rankings": safe_serialize(result)}
    except Exception as e:
        logging.error(f"Error getting supplier rankings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting supplier rankings: {str(e)}")

@router.get("/analysis/supplier-recommendations/{supplier_id}")
def get_supplier_recommendations(
    supplier_id: int = Path(..., description="The ID of the supplier"),
    min_rating: float = Query(5.0, description="Minimum rating threshold")
):
    """Get recommendations for alternative suppliers"""
    try:
        result = analysis_service.recommend_alternative_suppliers(supplier_id, min_rating)
        return {"recommendations": safe_serialize(result), "count": len(result)}
    except Exception as e:
        logging.error(f"Error getting supplier recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting supplier recommendations: {str(e)}")

@router.get("/analysis/supplier-performance-trends")
def get_supplier_performance_trends():
    """Get advanced supplier performance analysis with trends"""
    try:
        result = crud.analyze_supplier_performance_trends()
        return {"trends": safe_serialize(result), "count": len(result)}
    except Exception as e:
        logging.error(f"Error analyzing supplier performance trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing supplier performance trends: {str(e)}")

@router.get("/analysis/material-market-dynamics")
def get_material_market_dynamics():
    """Get material market dynamics analysis"""
    try:
        result = crud.analyze_material_market_dynamics()
        return {"market_analysis": safe_serialize(result), "count": len(result)}
    except Exception as e:
        logging.error(f"Error analyzing material market dynamics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing material market dynamics: {str(e)}")

# Report endpoints
@router.get("/reports/supplier/{supplier_id}", response_class=Response)
def generate_supplier_report(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Generate a PDF report for a specific supplier"""
    try:
        # Check if supplier exists
        supplier = crud.get_supplier(supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
            
        # Generate the report
        pdf_data = report_generator.generate_supplier_report(supplier_id)
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=supplier_report_{supplier_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating supplier report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating supplier report: {str(e)}")

@router.post("/reports/supplier-comparison", response_class=Response)
def generate_supplier_comparison_report(request: SupplierComparisonRequest):
    """Generate a PDF report comparing multiple suppliers"""
    try:
        supplier_ids = request.supplier_ids
        
        # Validate that suppliers exist
        existing_suppliers = []
        for supplier_id in supplier_ids:
            supplier = crud.get_supplier(supplier_id)
            if supplier:
                existing_suppliers.append(supplier_id)
            else:
                logging.warning(f"Supplier with ID {supplier_id} not found, skipping")
        
        if len(existing_suppliers) < 2:
            raise HTTPException(
                status_code=400, 
                detail=f"At least two valid suppliers are required. Found {len(existing_suppliers)} valid suppliers."
            )
            
        # Generate the report with existing suppliers only
        pdf_data = report_generator.generate_supplier_comparison_report(existing_suppliers)
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=supplier_comparison.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating supplier comparison report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating supplier comparison report: {str(e)}")

# Add a GET endpoint for testing
@router.get("/reports/supplier-comparison-test/{supplier_id1}/{supplier_id2}", response_class=Response)
def generate_supplier_comparison_report_test(
    supplier_id1: int = Path(..., description="First supplier ID"),
    supplier_id2: int = Path(..., description="Second supplier ID")
):
    """Generate a test PDF report comparing two suppliers (GET method for easy testing)"""
    try:
        supplier_ids = [supplier_id1, supplier_id2]
        
        # Validate that suppliers exist
        for supplier_id in supplier_ids:
            supplier = crud.get_supplier(supplier_id)
            if not supplier:
                raise HTTPException(status_code=404, detail=f"Supplier with ID {supplier_id} not found")
            
        # Generate the report
        pdf_data = report_generator.generate_supplier_comparison_report(supplier_ids)
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=supplier_comparison_{supplier_id1}_{supplier_id2}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating supplier comparison report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating supplier comparison report: {str(e)}")

@router.post("/reports/material", response_class=Response)
def generate_material_suppliers_report_post(request: MaterialSuppliersReportRequest):
    """Generate a PDF report of all suppliers for a specific material (POST method for UTF-8 support)"""
    try:
        material_name = request.material_name
        min_rating = request.min_rating or 0.0
        
        # Get suppliers for this material with minimum rating filter
        suppliers = crud.find_alternative_suppliers(material_name, min_rating)
        
        # Generate the report
        pdf_data = report_generator.generate_material_suppliers_report(material_name)
        
        # Create a safe filename
        safe_filename = material_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '_-.')
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=material_suppliers_{safe_filename}.pdf"}
        )
    except Exception as e:
        logging.error(f"Error generating material suppliers report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating material suppliers report: {str(e)}")

@router.get("/reports/material/{material_name}", response_class=Response)
def generate_material_suppliers_report(material_name: str = Path(..., description="The name of the material")):
    """Generate a PDF report of all suppliers for a specific material"""
    try:
        # URL decode the material name to handle UTF-8 characters
        import urllib.parse
        decoded_material_name = urllib.parse.unquote(material_name, encoding='utf-8')
        
        # Generate the report with the decoded name
        pdf_data = report_generator.generate_material_suppliers_report(decoded_material_name)
        
        # Create a safe filename by replacing problematic characters
        safe_filename = decoded_material_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Remove or replace other problematic characters
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '_-.')
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=material_suppliers_{safe_filename}.pdf"}
        )
    except Exception as e:
        logging.error(f"Error generating material suppliers report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating material suppliers report: {str(e)}")

@router.get("/reports/performance-trends", response_class=Response)
def generate_performance_trends_report():
    """Generate a comprehensive performance trends report"""
    
    pdf_data = report_generator.generate_performance_trends_report()
    
    try:
        # Generate the report
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=performance_trends_report.pdf"}
        )
    except Exception as e:
        logging.error(f"Error generating performance trends report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating performance trends report: {str(e)}")

@router.get("/reports/risk-analysis", response_class=Response)
def generate_risk_analysis_report():
    """Generate a comprehensive risk analysis report"""
    try:
        # Generate the report
        pdf_data = report_generator.generate_risk_analysis_report()
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=risk_analysis_report.pdf"}
        )
    except Exception as e:
        logging.error(f"Error generating risk analysis report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating risk analysis report: {str(e)}")
