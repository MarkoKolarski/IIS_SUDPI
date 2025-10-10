from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class SupplierBase(BaseModel):
    name: str
    email: str
    pib: str
    material_name: str
    price: float
    delivery_time: int
    rating: float
    rating_date: date
    selected: bool = False

class SupplierCreate(SupplierBase):
    supplier_id: int

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    material_name: Optional[str] = None
    price: Optional[float] = None
    delivery_time: Optional[int] = None
    rating: Optional[float] = None
    rating_date: Optional[date] = None
    selected: Optional[bool] = None

class Supplier(SupplierBase):
    supplier_id: int
    
    class Config:
        from_attributes = True

class MaterialBase(BaseModel):
    name: str
    price: float
    quality_score: Optional[float] = None

class MaterialCreate(MaterialBase):
    material_id: str

class Material(MaterialBase):
    material_id: str
    suppliers: List[int] = []
    
    class Config:
        from_attributes = True

class ComplaintBase(BaseModel):
    problem_description: str
    severity: int
    duration: int
    status: str

class ComplaintCreate(ComplaintBase):
    supplier_id: int
    controller_id: int
    reception_date: Optional[date] = None  # Make reception_date optional

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    problem_description: Optional[str] = None

class Complaint(ComplaintBase):
    complaint_id: int
    supplier_id: int
    controller_id: int
    reception_date: date
    
    class Config:
        from_attributes = True

class CertificateBase(BaseModel):
    name: str
    type: str
    issue_date: date
    expiry_date: date

class CertificateCreate(CertificateBase):
    supplier_id: int

class Certificate(CertificateBase):
    certificate_id: int
    supplier_id: int
    
    class Config:
        from_attributes = True

class ReportRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    supplier_ids: Optional[List[int]] = None
    include_complaints: bool = True
    include_certificates: bool = True
    
class SupplierRelationship(BaseModel):
    supplier_id: int
    name: str
    related_suppliers: List[Dict[str, Any]]
    common_materials: List[Dict[str, Any]]
    
class SupplierRatingHistory(BaseModel):
    supplier_id: int
    name: str
    ratings: List[Dict[str, Any]]
    
class AlternativeSupplier(BaseModel):
    supplier_id: int
    name: str
    material_name: str
    price: float
    rating: float
    similarity_score: float

class SupplierComparisonRequest(BaseModel):
    supplier_ids: List[int] = Field(..., min_items=2, description="List of supplier IDs to compare (minimum 2)")
    
class MaterialSuppliersReportRequest(BaseModel):
    material_name: str = Field(..., description="Name of the material")
    min_rating: Optional[float] = Field(0.0, ge=0.0, le=10.0, description="Minimum rating filter")
