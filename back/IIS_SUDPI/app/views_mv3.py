from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Dobavljac, Reklamacija, Sertifikat
from .decorators import allowed_users

def supplier_analysis_dashboard(request):
    """
    View for the supplier analysis dashboard integrating with the Neo4j microservice
    """
    return render(request, 'app/supplier_analysis.html')

@csrf_exempt
@require_http_methods(["POST"])
def supplier_complaint_transaction(request):
    """
    Create a complaint that updates supplier rating - uses saga pattern with Neo4j microservice
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
        
    try:
        # Get data from the request
        data = request.POST
        supplier_id = data.get('supplier_id')
        problem_description = data.get('problem_description')
        severity = int(data.get('severity', 1))
        
        if not supplier_id or not problem_description:
            return JsonResponse({"error": "Missing required fields"}, status=400)
            
        # Begin transaction by creating a complaint in Neo4j first
        # If that fails, no Django DB changes will be made
        from .services.supplier_analysis_service import SupplierAnalysisService
        service = SupplierAnalysisService()
        
        # Format data for the microservice
        complaint_data = {
            "supplier_id": int(supplier_id),
            "controller_id": request.user.kontrolor_kvaliteta.korisnik.sifra_k if hasattr(request.user, 'kontrolor_kvaliteta') else 1,
            "problem_description": problem_description,
            "severity": severity,
            "duration": int(data.get('duration', 1)),
            "status": "prijem"
        }
        
        # Call the microservice endpoint that implements the saga pattern
        result = service.create_complaint(complaint_data)
        
        if not result:
            return JsonResponse({"error": "Failed to create complaint in the microservice"}, status=500)
            
        return JsonResponse({
            "success": True,
            "message": "Complaint created successfully",
            "previous_rating": result.get("previous_rating"),
            "new_rating": result.get("new_rating")
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
