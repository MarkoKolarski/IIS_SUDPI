import logging
import tempfile
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .models import Dobavljac, Reklamacija, Sertifikat, User
from .decorators import allowed_users
from .services.supplier_analysis_service import SupplierAnalysisService

logger = logging.getLogger(__name__)
supplier_service = SupplierAnalysisService()

@api_view(['GET'])
@permission_classes([AllowAny])
def check_service_health(request):
    """
    Check if the supplier analysis microservice is available
    """
    health_status = supplier_service.health_check()
    return Response({"status": "online" if health_status else "offline"})

@api_view(['GET'])
@permission_classes([AllowAny])
def sync_suppliers(request):
    """
    Synchronize suppliers between Django and the microservice
    """
    try:
        # Get all suppliers from Django
        django_suppliers = Dobavljac.objects.all()
        
        success_count = 0
        error_count = 0
        
        for supplier in django_suppliers:
            # Format supplier data for the microservice
            supplier_data = {
                "supplier_id": supplier.sifra_d,
                "name": supplier.naziv,
                "email": supplier.email,
                "pib": supplier.PIB_d,
                "material_name": supplier.ime_sirovine,
                "price": float(supplier.cena),
                "delivery_time": supplier.rok_isporuke,
                "rating": float(supplier.ocena),
                "rating_date": supplier.datum_ocenjivanja.isoformat(),
                "selected": supplier.izabran
            }
            
            # Check if supplier exists in microservice
            existing_supplier = supplier_service.get_supplier(supplier.sifra_d)
            
            if existing_supplier:
                # Update existing supplier
                result = supplier_service.update_supplier(supplier.sifra_d, supplier_data)
            else:
                # Create new supplier
                result = supplier_service.create_supplier(supplier_data)
            
            if result:
                success_count += 1
            else:
                error_count += 1
        
        return Response({
            "message": "Supplier synchronization completed",
            "success_count": success_count,
            "error_count": error_count,
            "total_suppliers": len(django_suppliers)
        })
            
    except Exception as e:
        logger.error(f"Error synchronizing suppliers: {str(e)}")
        return Response(
            {"error": f"Error synchronizing suppliers: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def sync_complaints(request):
    """
    Synchronize complaints between Django and the microservice
    """
    try:
        # Get all complaints from Django
        django_complaints = Reklamacija.objects.all().select_related('kontrolor', 'dobavljac')
        
        success_count = 0
        error_count = 0
        
        for complaint in django_complaints:
            # Format complaint data for the microservice
            complaint_data = {
                "complaint_id": complaint.reklamacija_id,
                "supplier_id": complaint.dobavljac.sifra_d,
                "controller_id": complaint.kontrolor.korisnik.sifra_k,
                "problem_description": complaint.opis_problema,
                "severity": complaint.jacina_zalbe,
                "duration": complaint.vreme_trajanja,
                "status": complaint.status,
                "reception_date": complaint.datum_prijema.isoformat()
            }
            
            # Create complaint in microservice
            result = supplier_service.create_complaint(complaint_data)
            
            if result:
                success_count += 1
            else:
                error_count += 1
        
        return Response({
            "message": "Complaint synchronization completed",
            "success_count": success_count,
            "error_count": error_count,
            "total_complaints": len(django_complaints)
        })
            
    except Exception as e:
        logger.error(f"Error synchronizing complaints: {str(e)}")
        return Response(
            {"error": f"Error synchronizing complaints: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def sync_certificates(request):
    """
    Synchronize certificates between Django and the microservice
    """
    try:
        # Get all certificates from Django
        django_certificates = Sertifikat.objects.all().select_related('dobavljac')
        
        success_count = 0
        error_count = 0
        
        for certificate in django_certificates:
            # Format certificate data for the microservice
            certificate_data = {
                "certificate_id": certificate.sertifikat_id,
                "supplier_id": certificate.dobavljac.sifra_d,
                "name": certificate.naziv,
                "type": certificate.tip,
                "issue_date": certificate.datum_izdavanja.isoformat(),
                "expiry_date": certificate.datum_isteka.isoformat()
            }
            
            # Create certificate in microservice
            result = supplier_service.create_certificate(certificate_data)
            
            if result:
                success_count += 1
            else:
                error_count += 1
        
        return Response({
            "message": "Certificate synchronization completed",
            "success_count": success_count,
            "error_count": error_count,
            "total_certificates": len(django_certificates)
        })
            
    except Exception as e:
        logger.error(f"Error synchronizing certificates: {str(e)}")
        return Response(
            {"error": f"Error synchronizing certificates: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_supplier_report(request, supplier_id):
    """
    Get a PDF report for a specific supplier
    """
    try:
        # Verify the supplier exists in Django
        supplier = Dobavljac.objects.filter(sifra_d=supplier_id).first()
        if not supplier:
            return Response(
                {"error": "Supplier not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the report from the microservice
        report_content = supplier_service.get_supplier_report(supplier_id)
        
        if not report_content:
            return Response(
                {"error": "Failed to generate report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(report_content)
            temp_path = temp_file.name
        
        # Return the file as an attachment
        response = FileResponse(
            open(temp_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="supplier_report_{supplier_id}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating supplier report: {str(e)}")
        return Response(
            {"error": f"Error generating supplier report: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def get_supplier_comparison_report(request):
    """
    Get a PDF report comparing multiple suppliers
    """
    try:
        supplier_ids = request.data.get('supplier_ids', [])
        
        if not supplier_ids or len(supplier_ids) < 2:
            return Response(
                {"error": "At least two supplier IDs must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify all suppliers exist in Django
        for supplier_id in supplier_ids:
            if not Dobavljac.objects.filter(sifra_d=supplier_id).exists():
                return Response(
                    {"error": f"Supplier with ID {supplier_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get the report from the microservice
        report_content = supplier_service.get_supplier_comparison_report(supplier_ids)
        
        if not report_content:
            return Response(
                {"error": "Failed to generate comparison report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(report_content)
            temp_path = temp_file.name
        
        # Return the file as an attachment
        response = FileResponse(
            open(temp_path, 'rb'),
            content_type='application/pdf'
        )
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="supplier_comparison_{timestamp}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating supplier comparison report: {str(e)}")
        return Response(
            {"error": f"Error generating supplier comparison report: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_material_suppliers_report(request, material_name):
    """
    Get a PDF report of all suppliers for a specific material
    """
    try:
        # Get the report from the microservice
        report_content = supplier_service.get_material_suppliers_report(material_name)
        
        if not report_content:
            return Response(
                {"error": "Failed to generate material suppliers report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(report_content)
            temp_path = temp_file.name
        
        # Return the file as an attachment
        response = FileResponse(
            open(temp_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="material_suppliers_{material_name}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating material suppliers report: {str(e)}")
        return Response(
            {"error": f"Error generating material suppliers report: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def create_complaint_with_rating(request):
    """
    Create a complaint and update supplier rating in both systems (transactional)
    """
    try:
        # Extract data from the request
        supplier_id = request.data.get('dobavljac_id')
        problem_description = request.data.get('opis_problema')
        severity = int(request.data.get('jacina_zalbe', 1))
        duration = int(request.data.get('vreme_trajanja', 1))
        
        if not supplier_id or not problem_description:
            return Response(
                {"error": "Supplier ID and problem description are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the supplier from Django
        try:
            supplier = Dobavljac.objects.get(sifra_d=supplier_id)
        except Dobavljac.DoesNotExist:
            return Response(
                {"error": "Supplier not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the controller - use a default if not authenticated
        if hasattr(request, 'user') and hasattr(request.user, 'kontrolor_kvaliteta'):
            kontrolor = request.user.kontrolor_kvaliteta
        else:
            # Use the first controller available or create a dummy one
            kontrolors = User.objects.filter(tip_k='kontrolor_kvaliteta')
            if kontrolors.exists():
                kontrolor = kontrolors.first().kontrolor_kvaliteta
            else:
                return Response(
                    {"error": "No controllers found in the system"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # 1. Create the complaint in Django
        django_complaint = Reklamacija.objects.create(
            kontrolor=kontrolor,
            dobavljac=supplier,
            status='prijem',
            opis_problema=problem_description,
            vreme_trajanja=duration,
            jacina_zalbe=severity
        )
        
        # 2. Create the complaint in the microservice
        ms_complaint_data = {
            "complaint_id": django_complaint.reklamacija_id,
            "supplier_id": supplier_id,
            "controller_id": kontrolor.korisnik.sifra_k,
            "problem_description": problem_description,
            "severity": severity,
            "duration": duration,
            "status": "prijem"
        }
        
        ms_result = supplier_service.create_complaint(ms_complaint_data)
        
        if not ms_result:
            # If microservice creation fails, rollback Django transaction
            django_complaint.delete()
            return Response(
                {"error": "Failed to create complaint in the microservice"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update supplier rating in Django based on response from microservice
        new_rating = ms_result.get('new_rating')
        if new_rating is not None:
            supplier.ocena = new_rating
            supplier.datum_ocenjivanja = datetime.now().date()
            supplier.save()
        
        return Response({
            "message": "Complaint created successfully in both systems",
            "django_complaint_id": django_complaint.reklamacija_id,
            "previous_rating": ms_result.get('previous_rating'),
            "new_rating": new_rating
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating complaint with rating update: {str(e)}")
        return Response(
            {"error": f"Error creating complaint with rating update: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_supplier_risk_analysis(request):
    """
    Get supplier risk analysis from the microservice
    """
    try:
        risk_patterns = supplier_service.get_supplier_risk_patterns()
        
        if not risk_patterns:
            return Response(
                {"error": "Failed to retrieve risk patterns from microservice"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(risk_patterns)
        
    except Exception as e:
        logger.error(f"Error getting supplier risk analysis: {str(e)}")
        return Response(
            {"error": f"Error getting supplier risk analysis: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_alternative_suppliers(request, material_name):
    """
    Get alternative suppliers for a material
    """
    try:
        min_rating = float(request.GET.get('min_rating', 0.0))
        
        alternatives = supplier_service.get_alternative_suppliers(material_name, min_rating)
        
        if not alternatives:
            return Response(
                {"error": "Failed to retrieve alternative suppliers from microservice"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(alternatives)
        
    except Exception as e:
        logger.error(f"Error getting alternative suppliers: {str(e)}")
        return Response(
            {"error": f"Error getting alternative suppliers: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
