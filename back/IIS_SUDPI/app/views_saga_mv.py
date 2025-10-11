from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .saga_orchestrator_mv import saga_orchestrator
from .models import Dobavljac, Reklamacija, KontrolorKvaliteta, User

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def demo_successful_saga(request):
    """
    Demonstrate a successful saga - Create supplier with contract
    """
    try:
        # Get next supplier ID
        max_sifra = Dobavljac.objects.aggregate(Max('sifra_d'))['sifra_d__max'] or 0
        next_sifra = max_sifra + 1
        
        supplier_data = {
            'sifra_d': next_sifra,
            'naziv': f'Demo Supplier {next_sifra}',
            'email': f'demo{next_sifra}@supplier.com',
            'PIB_d': f'12345678{next_sifra:02d}',
            'ime_sirovine': 'Demo Material',
            'cena': 100.00,
            'rok_isporuke': 7,
            'ocena': 8.5,
            'datum_ocenjivanja': timezone.now().date(),
            'izabran': False
        }
        
        contract_data = {
            'datum_potpisa_u': timezone.now().date(),
            'datum_isteka_u': timezone.now().date() + timedelta(days=365),
            'status_u': 'aktivan',
            'uslovi_u': 'Demo contract terms and conditions'
        }
        
        # Create and execute saga
        saga_id = saga_orchestrator.create_supplier_with_contract_saga(
            supplier_data, 
            contract_data,
            force_failure=False
        )
        
        result = saga_orchestrator.execute_saga(saga_id)
        
        return Response({
            "message": "Successful saga demonstration completed",
            "saga_id": saga_id,
            "result": result,
            "demonstration": "This saga successfully created a supplier, contract, and synced to microservice"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in successful saga demo: {str(e)}")
        return Response(
            {"error": f"Error in successful saga demo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def demo_failed_saga_with_rollback(request):
    """
    Demonstrate a failed saga with rollback - Create supplier but fail at microservice sync
    """
    try:
        # Get next supplier ID
        max_sifra = Dobavljac.objects.aggregate(Max('sifra_d'))['sifra_d__max'] or 0
        next_sifra = max_sifra + 1
        
        supplier_data = {
            'sifra_d': next_sifra,
            'naziv': f'Rollback Demo Supplier {next_sifra}',
            'email': f'rollback{next_sifra}@supplier.com',
            'PIB_d': f'98765432{next_sifra:02d}',
            'ime_sirovine': 'Rollback Material',
            'cena': 150.00,
            'rok_isporuke': 5,
            'ocena': 7.5,
            'datum_ocenjivanja': timezone.now().date(),
            'izabran': False
        }
        
        contract_data = {
            'datum_potpisa_u': timezone.now().date(),
            'datum_isteka_u': timezone.now().date() + timedelta(days=365),
            'status_u': 'aktivan',
            'uslovi_u': 'Rollback demo contract terms'
        }
        
        # Create and execute saga with forced failure
        saga_id = saga_orchestrator.create_supplier_with_contract_saga(
            supplier_data, 
            contract_data,
            force_failure=True  # This will cause failure at microservice step
        )
        
        result = saga_orchestrator.execute_saga(saga_id)
        
        # Verify rollback - supplier should not exist
        supplier_exists = Dobavljac.objects.filter(PIB_d=supplier_data['PIB_d']).exists()
        
        return Response({
            "message": "Failed saga with rollback demonstration completed",
            "saga_id": saga_id,
            "result": result,
            "supplier_exists_after_rollback": supplier_exists,
            "demonstration": "This saga failed at microservice sync and rolled back all changes"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in failed saga demo: {str(e)}")
        return Response(
            {"error": f"Error in failed saga demo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def demo_complaint_saga_success(request):
    """
    Demonstrate successful complaint creation with rating update
    """
    try:
        # Get an existing supplier or create one
        supplier = Dobavljac.objects.first()
        if not supplier:
            supplier = Dobavljac.objects.create(
                naziv='Test Supplier for Complaint',
                email='test@supplier.com',
                PIB_d='123456789',
                ime_sirovine='Test Material',
                cena=100.00,
                rok_isporuke=7,
                ocena=8.0,
                datum_ocenjivanja=timezone.now().date(),
                izabran=False
            )
        
        original_rating = supplier.ocena
        
        complaint_data = {
            'dobavljac_id': supplier.sifra_d,
            'opis_problema': 'Demo complaint - quality issues with delivered materials',
            'jacina_zalbe': 6,
            'vreme_trajanja': 3
        }
        
        # Create and execute saga
        saga_id = saga_orchestrator.create_complaint_with_rating_saga(
            complaint_data,
            force_db_failure=False,
            force_ms_failure=False
        )
        
        result = saga_orchestrator.execute_saga(saga_id)
        
        # Check the updated rating
        supplier.refresh_from_db()
        new_rating = supplier.ocena
        
        return Response({
            "message": "Successful complaint saga demonstration completed",
            "saga_id": saga_id,
            "result": result,
            "rating_change": {
                "original_rating": float(original_rating),
                "new_rating": float(new_rating),
                "difference": float(original_rating - new_rating)
            },
            "demonstration": "This saga successfully created a complaint and updated supplier rating"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in complaint saga demo: {str(e)}")
        return Response(
            {"error": f"Error in complaint saga demo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def demo_complaint_saga_rollback(request):
    """
    Demonstrate complaint saga with rollback due to microservice failure
    """
    try:
        # Get an existing supplier or create one
        supplier = Dobavljac.objects.first()
        if not supplier:
            supplier = Dobavljac.objects.create(
                naziv='Test Supplier for Rollback',
                email='rollback@supplier.com',
                PIB_d='987654321',
                ime_sirovine='Rollback Material',
                cena=120.00,
                rok_isporuke=10,
                ocena=7.5,
                datum_ocenjivanja=timezone.now().date(),
                izabran=False
            )
        
        original_rating = supplier.ocena
        
        complaint_data = {
            'dobavljac_id': supplier.sifra_d,
            'opis_problema': 'Rollback demo complaint - this will fail at microservice',
            'jacina_zalbe': 8,
            'vreme_trajanja': 5
        }
        
        # Create and execute saga with forced microservice failure
        saga_id = saga_orchestrator.create_complaint_with_rating_saga(
            complaint_data,
            force_db_failure=False,
            force_ms_failure=True  # This will cause rollback
        )
        
        result = saga_orchestrator.execute_saga(saga_id)
        
        # Check that rating was restored
        supplier.refresh_from_db()
        current_rating = supplier.ocena
        
        # Verify no complaint was created
        complaint_exists = Reklamacija.objects.filter(
            opis_problema=complaint_data['opis_problema']
        ).exists()
        
        return Response({
            "message": "Complaint saga rollback demonstration completed",
            "saga_id": saga_id,
            "result": result,
            "rating_restored": float(current_rating) == float(original_rating),
            "complaint_exists": complaint_exists,
            "demonstration": "This saga failed at microservice and rolled back complaint and rating changes"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in complaint rollback demo: {str(e)}")
        return Response(
            {"error": f"Error in complaint rollback demo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def demo_visit_scheduling_saga(request):
    """
    Demonstrate visit scheduling saga with validation
    """
    try:
        # Ensure we have the required data
        supplier = Dobavljac.objects.first()
        if not supplier:
            supplier = Dobavljac.objects.create(
                naziv='Visit Demo Supplier',
                email='visit@supplier.com',
                PIB_d='111222333',
                ime_sirovine='Visit Material',
                cena=80.00,
                rok_isporuke=14,
                ocena=9.0,
                datum_ocenjivanja=timezone.now().date(),
                izabran=False
            )
        
        # Ensure we have a quality controller
        if not KontrolorKvaliteta.objects.exists():
            user = User.objects.filter(tip_k='kontrolor_kvaliteta').first()
            if not user:
                user = User.objects.create(
                    ime_k='Demo',
                    prz_k='Controller',
                    mail_k='demo.controller@company.com',
                    tip_k='kontrolor_kvaliteta'
                )
            KontrolorKvaliteta.objects.create(korisnik=user)
        
        # Schedule visit for tomorrow
        tomorrow = timezone.now() + timedelta(days=1)
        visit_end = tomorrow + timedelta(hours=2)
        
        visit_data = {
            'dobavljac_id': supplier.sifra_d,
            'datum_od': tomorrow.isoformat(),
            'datum_do': visit_end.isoformat()
        }
        
        force_overlap = request.data.get('force_overlap', False)
        
        # Create and execute saga
        saga_id = saga_orchestrator.schedule_visit_with_validation_saga(
            visit_data,
            force_overlap=force_overlap
        )
        
        result = saga_orchestrator.execute_saga(saga_id)
        
        demo_message = (
            "This saga failed due to overlapping visit times and rolled back all changes"
            if force_overlap else
            "This saga successfully scheduled a visit with validation"
        )
        
        return Response({
            "message": "Visit scheduling saga demonstration completed",
            "saga_id": saga_id,
            "result": result,
            "force_overlap": force_overlap,
            "demonstration": demo_message
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in visit scheduling demo: {str(e)}")
        return Response(
            {"error": f"Error in visit scheduling demo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_saga_status(request, saga_id):
    """
    Get the current status of a saga
    """
    try:
        saga_status = saga_orchestrator.get_saga_status(saga_id)
        
        if "error" in saga_status:
            return Response(saga_status, status=status.HTTP_404_NOT_FOUND)
        
        return Response(saga_status, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting saga status: {str(e)}")
        return Response(
            {"error": f"Error getting saga status: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def list_active_sagas(request):
    """
    List all active sagas
    """
    try:
        active_sagas = []
        
        for saga_id, saga in saga_orchestrator.active_sagas.items():
            active_sagas.append({
                "saga_id": saga_id,
                "name": saga.name,
                "status": saga.status.value,
                "created_at": saga.created_at.isoformat(),
                "completed_at": saga.completed_at.isoformat() if saga.completed_at else None,
                "steps_count": len(saga.steps),
                "completed_steps": len([s for s in saga.steps if s.status.value == "completed"]),
                "failed_steps": len([s for s in saga.steps if s.status.value == "failed"])
            })
        
        return Response({
            "active_sagas": active_sagas,
            "total_count": len(active_sagas)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing sagas: {str(e)}")
        return Response(
            {"error": f"Error listing sagas: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def demo_all_saga_patterns(request):
    """
    Run all saga demonstrations in sequence to show different patterns
    """
    try:
        results = {}
        
        # 1. Successful saga
        try:
            max_sifra = Dobavljac.objects.aggregate(Max('sifra_d'))['sifra_d__max'] or 0
            next_sifra = max_sifra + 1
            
            supplier_data = {
                'sifra_d': next_sifra,
                'naziv': f'All Demo Supplier {next_sifra}',
                'email': f'alldemo{next_sifra}@supplier.com',
                'PIB_d': f'55566677{next_sifra:02d}',
                'ime_sirovine': 'All Demo Material',
                'cena': 200.00,
                'rok_isporuke': 12,
                'ocena': 8.8,
                'datum_ocenjivanja': timezone.now().date(),
                'izabran': False
            }
            
            contract_data = {
                'datum_potpisa_u': timezone.now().date(),
                'datum_isteka_u': timezone.now().date() + timedelta(days=365),
                'status_u': 'aktivan',
                'uslovi_u': 'All demo contract terms'
            }
            
            saga_id = saga_orchestrator.create_supplier_with_contract_saga(
                supplier_data, contract_data, force_failure=False
            )
            
            result = saga_orchestrator.execute_saga(saga_id)
            results["successful_saga"] = {"saga_id": saga_id, "success": result["success"]}
            
        except Exception as e:
            results["successful_saga"] = {"error": str(e)}
        
        # 2. Failed saga with rollback
        try:
            max_sifra = Dobavljac.objects.aggregate(Max('sifra_d'))['sifra_d__max'] or 0
            next_sifra = max_sifra + 1
            
            supplier_data = {
                'sifra_d': next_sifra,
                'naziv': f'Fail Demo Supplier {next_sifra}',
                'email': f'faildemo{next_sifra}@supplier.com',
                'PIB_d': f'99988877{next_sifra:02d}',
                'ime_sirovine': 'Fail Demo Material',
                'cena': 300.00,
                'rok_isporuke': 8,
                'ocena': 6.5,
                'datum_ocenjivanja': timezone.now().date(),
                'izabran': False
            }
            
            contract_data = {
                'datum_potpisa_u': timezone.now().date(),
                'datum_isteka_u': timezone.now().date() + timedelta(days=365),
                'status_u': 'aktivan',
                'uslovi_u': 'Fail demo contract terms'
            }
            
            saga_id = saga_orchestrator.create_supplier_with_contract_saga(
                supplier_data, contract_data, force_failure=True
            )
            
            result = saga_orchestrator.execute_saga(saga_id)
            supplier_exists = Dobavljac.objects.filter(PIB_d=supplier_data['PIB_d']).exists()
            
            results["failed_saga"] = {
                "saga_id": saga_id, 
                "success": result["success"],
                "supplier_rolled_back": not supplier_exists
            }
            
        except Exception as e:
            results["failed_saga"] = {"error": str(e)}
        
        return Response({
            "message": "All saga patterns demonstration completed",
            "results": results,
            "demonstration": "This ran both successful and failed saga patterns to show rollback capabilities"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in all saga demo: {str(e)}")
        return Response(
            {"error": f"Error in all saga demo: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
