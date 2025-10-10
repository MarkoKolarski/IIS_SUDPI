from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from fastapi.responses import JSONResponse, Response
from typing import List, Dict, Any, Optional
import logging
from datetime import date

from app import crud
from app.schemas import (
    SupplierCreate, SupplierUpdate, Supplier,
    ComplaintCreate, ComplaintUpdate, Complaint,
    CertificateCreate, Certificate,
    MaterialCreate, ReportRequest
)
from app.services.analysis import SupplierAnalysisService
from app.services.report import ReportGenerator

router = APIRouter()
analysis_service = SupplierAnalysisService()
report_generator = ReportGenerator()

# Health check endpoint
@router.get("/health")
def health_check():
    """Check if the service is running"""
    try:
        # Test connection to Neo4j
        neo4j_db.run_query("RETURN 1 as test")
        return {"status": "ok", "neo4j_status": "connected"}
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}

# Supplier endpoints
@router.post("/suppliers/", response_model=Dict[str, Any])
def create_supplier(supplier: SupplierCreate):
    """Create a new supplier"""
    try:
        supplier_dict = supplier.dict()
        result = crud.create_supplier(supplier_dict)
        return {"message": "Supplier created successfully", "data": result}
    except Exception as e:
        logging.error(f"Error creating supplier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating supplier: {str(e)}")

@router.get("/suppliers/", response_model=List[Dict[str, Any]])
def get_suppliers():
    """Get all suppliers"""
    try:
        return crud.get_all_suppliers()
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
        return supplier
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
        return result
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
        return {"message": "Material created successfully", "data": result}
    except Exception as e:
        logging.error(f"Error creating material: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating material: {str(e)}")

# Complaint endpoints
@router.post("/complaints/", response_model=Dict[str, Any])
def create_complaint(complaint: ComplaintCreate):
    """Create a new complaint"""
    try:
        complaint_dict = complaint.dict()
        # Generate complaint ID if not provided
        if not complaint_dict.get("complaint_id"):
            # Get max complaint ID from existing complaints
            existing_complaints = crud.get_supplier_complaints(complaint_dict["supplier_id"])
            max_id = 0
            for c in existing_complaints:
                if "complaint_id" in c and isinstance(c["complaint_id"], int) and c["complaint_id"] > max_id:
                    max_id = c["complaint_id"]
            complaint_dict["complaint_id"] = max_id + 1
        
        # Set reception date to today if not provided
        if not complaint_dict.get("reception_date"):
            complaint_dict["reception_date"] = date.today()
        
        # Set default status if not provided
        if not complaint_dict.get("status"):
            complaint_dict["status"] = "prijem"
            
        result = crud.create_complaint(complaint_dict)
        
        # Also update supplier rating based on complaint severity
        supplier_id = complaint_dict["supplier_id"]
        severity = complaint_dict["severity"]
        supplier = crud.get_supplier(supplier_id)
        
        if supplier:
            current_rating = float(supplier.get("rating", 10.0))
            
            # Calculate penalty based on severity
            if severity <= 3:
                penalty = severity * 0.3
            elif severity <= 7:
                penalty = severity * 0.3
            else:
                penalty = severity * 0.3
                
            # Update rating
            new_rating = max(0, min(10, current_rating - penalty))
            crud.update_supplier(supplier_id, {
                "rating": new_rating,
                "rating_date": date.today().isoformat()
            })
            
            return {
                "message": "Complaint created successfully, supplier rating updated",
                "data": result,
                "previous_rating": current_rating,
                "new_rating": new_rating
            }
            
        return {"message": "Complaint created successfully", "data": result}
    except Exception as e:
        logging.error(f"Error creating complaint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating complaint: {str(e)}")

@router.get("/suppliers/{supplier_id}/complaints", response_model=List[Dict[str, Any]])
def get_supplier_complaints(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Get all complaints for a supplier"""
    try:
        return crud.get_supplier_complaints(supplier_id)
    except Exception as e:
        logging.error(f"Error fetching complaints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching complaints: {str(e)}")

# Certificate endpoints
@router.post("/certificates/", response_model=Dict[str, Any])
def create_certificate(certificate: CertificateCreate):
    """Create a new certificate"""
    try:
        certificate_dict = certificate.dict()
        # Generate certificate ID if not provided
        if not certificate_dict.get("certificate_id"):
            # Get max certificate ID from existing certificates
            existing_certificates = crud.get_supplier_certificates(certificate_dict["supplier_id"])
            max_id = 0
            for c in existing_certificates:
                if "certificate_id" in c and isinstance(c["certificate_id"], int) and c["certificate_id"] > max_id:
                    max_id = c["certificate_id"]
            certificate_dict["certificate_id"] = max_id + 1
            
        result = crud.create_certificate(certificate_dict)
        return {"message": "Certificate created successfully", "data": result}
    except Exception as e:
        logging.error(f"Error creating certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating certificate: {str(e)}")

@router.get("/suppliers/{supplier_id}/certificates", response_model=List[Dict[str, Any]])
def get_supplier_certificates(supplier_id: int = Path(..., description="The ID of the supplier")):
    """Get all certificates for a supplier"""
    try:
        return crud.get_supplier_certificates(supplier_id)
    except Exception as e:
        logging.error(f"Error fetching certificates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching certificates: {str(e)}")

# Analysis endpoints
@router.get("/analysis/alternative-suppliers/{material_name}")
def get_alternative_suppliers(
    material_name: str = Path(..., description="The name of the material"),
    min_rating: float = Query(0.0, description="Minimum rating threshold")
):
    """Find alternative suppliers for a material"""
    try:
        suppliers = crud.find_alternative_suppliers(material_name, min_rating)
        return {"suppliers": suppliers, "count": len(suppliers)}
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
        return {"suppliers": suppliers, "count": len(suppliers)}
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
        return {"data": result}
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
        return {"data": result}
    except Exception as e:
        logging.error(f"Error fetching supplier rating history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching supplier rating history: {str(e)}")

@router.get("/analysis/risk-patterns")
def get_supplier_risk_patterns():
    """Identify risk patterns in supplier complaints"""
    try:
        result = crud.identify_supplier_risk_patterns()
        return {"patterns": result, "count": len(result)}
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
        return result
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
        return {"trends": result, "days_analyzed": days}
    except Exception as e:
        logging.error(f"Error analyzing complaint trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing complaint trends: {str(e)}")

@router.get("/analysis/supplier-ranking")
def get_supplier_ranking(material_name: Optional[str] = Query(None, description="Filter by material name")):
    """Get ranking of suppliers by material, rating, and price"""
    try:
        result = analysis_service.get_supplier_ranking_by_material(material_name)
        return {"rankings": result}
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
        return {"recommendations": result, "count": len(result)}
    except Exception as e:
        logging.error(f"Error getting supplier recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting supplier recommendations: {str(e)}")

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
def generate_supplier_comparison_report(supplier_ids: List[int] = Body(..., description="List of supplier IDs to compare")):
    """Generate a PDF report comparing multiple suppliers"""
    try:
        if len(supplier_ids) < 2:
            raise HTTPException(status_code=400, detail="At least two supplier IDs must be provided")
            
        # Generate the report
        pdf_data = report_generator.generate_supplier_comparison_report(supplier_ids)
        
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

@router.get("/reports/material/{material_name}", response_class=Response)
def generate_material_suppliers_report(material_name: str = Path(..., description="The name of the material")):
    """Generate a PDF report of all suppliers for a specific material"""
    try:
        # Generate the report
        pdf_data = report_generator.generate_material_suppliers_report(material_name)
        
        # Return the PDF
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=material_suppliers_{material_name}.pdf"}
        )
    except Exception as e:
        logging.error(f"Error generating material suppliers report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating material suppliers report: {str(e)}")
