import logging
import uuid
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .models import (
    Dobavljac, Reklamacija, Sertifikat, User, KontrolorKvaliteta,
    Ugovor, Faktura, Transakcija, Penal, Poseta
)
from .services.supplier_analysis_service import SupplierAnalysisService

logger = logging.getLogger(__name__)

class SagaStatus(Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

class StepStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    step_id: str
    name: str
    execute_func: callable
    compensate_func: callable
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = None
    execution_time: datetime = None
    compensation_time: datetime = None

@dataclass
class SagaTransaction:
    saga_id: str
    name: str
    status: SagaStatus
    steps: List[SagaStep]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class SagaOrchestrator:
    def __init__(self):
        self.active_sagas: Dict[str, SagaTransaction] = {}
        self.supplier_service = SupplierAnalysisService()

    def create_saga(self, name: str, steps: List[SagaStep]) -> str:
        """Create a new saga transaction"""
        saga_id = str(uuid.uuid4())
        saga = SagaTransaction(
            saga_id=saga_id,
            name=name,
            status=SagaStatus.STARTED,
            steps=steps,
            created_at=timezone.now()
        )
        self.active_sagas[saga_id] = saga
        logger.info(f"Created saga {saga_id}: {name}")
        return saga_id

    def execute_saga(self, saga_id: str) -> Dict[str, Any]:
        """Execute all steps in a saga"""
        if saga_id not in self.active_sagas:
            raise ValueError(f"Saga {saga_id} not found")

        saga = self.active_sagas[saga_id]
        saga.status = SagaStatus.IN_PROGRESS
        
        try:
            # Execute steps sequentially
            for step in saga.steps:
                self._execute_step(saga, step)
                
            # All steps completed successfully
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = timezone.now()
            logger.info(f"Saga {saga_id} completed successfully")
            
            return {
                "success": True,
                "saga_id": saga_id,
                "status": saga.status.value,
                "results": [step.result for step in saga.steps]
            }
            
        except Exception as e:
            logger.error(f"Saga {saga_id} failed: {str(e)}")
            saga.status = SagaStatus.FAILED
            saga.error_message = str(e)
            
            # Trigger compensation
            compensation_result = self._compensate_saga(saga)
            
            return {
                "success": False,
                "saga_id": saga_id,
                "status": saga.status.value,
                "error": str(e),
                "compensation": compensation_result
            }

    def _execute_step(self, saga: SagaTransaction, step: SagaStep):
        """Execute a single step"""
        step.status = StepStatus.EXECUTING
        step.execution_time = timezone.now()
        
        try:
            logger.info(f"Executing step {step.step_id}: {step.name}")
            step.result = step.execute_func()
            step.status = StepStatus.COMPLETED
            logger.info(f"Step {step.step_id} completed successfully")
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            logger.error(f"Step {step.step_id} failed: {str(e)}")
            raise

    def _compensate_saga(self, saga: SagaTransaction) -> Dict[str, Any]:
        """Compensate (rollback) all completed steps in reverse order"""
        saga.status = SagaStatus.COMPENSATING
        compensation_results = []
        
        # Compensate in reverse order
        completed_steps = [s for s in saga.steps if s.status == StepStatus.COMPLETED]
        
        for step in reversed(completed_steps):
            try:
                step.status = StepStatus.COMPENSATING
                step.compensation_time = timezone.now()
                
                logger.info(f"Compensating step {step.step_id}: {step.name}")
                compensation_result = step.compensate_func()
                
                step.status = StepStatus.COMPENSATED
                compensation_results.append({
                    "step_id": step.step_id,
                    "success": True,
                    "result": compensation_result
                })
                
            except Exception as comp_error:
                logger.error(f"Compensation failed for step {step.step_id}: {str(comp_error)}")
                compensation_results.append({
                    "step_id": step.step_id,
                    "success": False,
                    "error": str(comp_error)
                })
        
        saga.status = SagaStatus.COMPENSATED
        return {
            "compensated_steps": len(compensation_results),
            "results": compensation_results
        }

    def get_saga_status(self, saga_id: str) -> Dict[str, Any]:
        """Get current status of a saga"""
        if saga_id not in self.active_sagas:
            return {"error": "Saga not found"}
            
        saga = self.active_sagas[saga_id]
        return {
            "saga_id": saga_id,
            "name": saga.name,
            "status": saga.status.value,
            "created_at": saga.created_at.isoformat(),
            "completed_at": saga.completed_at.isoformat() if saga.completed_at else None,
            "error_message": saga.error_message,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "execution_time": step.execution_time.isoformat() if step.execution_time else None,
                    "compensation_time": step.compensation_time.isoformat() if step.compensation_time else None,
                    "error": step.error
                }
                for step in saga.steps
            ]
        }

    # Specific saga implementations for supplier management

    def create_supplier_with_contract_saga(self, supplier_data: Dict, contract_data: Dict, 
                                         force_failure: bool = False) -> str:
        """Create a new supplier with contract - demonstrates successful saga"""
        
        def create_supplier():
            if Dobavljac.objects.filter(PIB_d=supplier_data['PIB_d']).exists():
                raise ValueError(f"Supplier with PIB {supplier_data['PIB_d']} already exists")
            
            supplier = Dobavljac.objects.create(**supplier_data)
            return {"supplier_id": supplier.sifra_d, "supplier_name": supplier.naziv}

        def compensate_supplier():
            supplier = Dobavljac.objects.filter(PIB_d=supplier_data['PIB_d']).first()
            if supplier:
                supplier.delete()
                return {"action": "supplier_deleted", "pib": supplier_data['PIB_d']}
            return {"action": "supplier_not_found"}

        def create_contract():
            supplier_result = saga.steps[0].result
            supplier = Dobavljac.objects.get(sifra_d=supplier_result["supplier_id"])
            
            contract = Ugovor.objects.create(
                dobavljac=supplier,
                **contract_data
            )
            return {"contract_id": contract.sifra_u, "supplier_id": supplier.sifra_d}

        def compensate_contract():
            if len(saga.steps) > 1 and saga.steps[1].result:
                contract_result = saga.steps[1].result
                contract = Ugovor.objects.filter(sifra_u=contract_result["contract_id"]).first()
                if contract:
                    contract.delete()
                    return {"action": "contract_deleted", "contract_id": contract_result["contract_id"]}
            return {"action": "contract_not_found"}

        def sync_to_microservice():
            if force_failure:
                raise Exception("Forced failure in microservice sync for demonstration")
                
            supplier_result = saga.steps[0].result
            supplier = Dobavljac.objects.get(sifra_d=supplier_result["supplier_id"])
            
            # Sync to microservice
            ms_data = {
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
            
            result = self.supplier_service.create_supplier(ms_data)
            if not result:
                raise Exception("Failed to sync supplier to microservice")
                
            return {"microservice_sync": True, "supplier_id": supplier.sifra_d}

        def compensate_microservice():
            if len(saga.steps) > 2 and saga.steps[2].result:
                supplier_result = saga.steps[0].result
                supplier_id = supplier_result["supplier_id"]
                
                # In a real scenario, we'd call microservice to delete the supplier
                # For now, we'll just log it
                logger.info(f"Would delete supplier {supplier_id} from microservice")
                return {"action": "microservice_cleanup", "supplier_id": supplier_id}
            return {"action": "microservice_not_synced"}

        steps = [
            SagaStep("create_supplier", "Create Supplier in DB", create_supplier, compensate_supplier),
            SagaStep("create_contract", "Create Contract", create_contract, compensate_contract),
            SagaStep("sync_microservice", "Sync to Microservice", sync_to_microservice, compensate_microservice)
        ]

        saga_id = self.create_saga("Create Supplier with Contract", steps)
        saga = self.active_sagas[saga_id]
        
        return saga_id

    def create_complaint_with_rating_saga(self, complaint_data: Dict, force_db_failure: bool = False,
                                        force_ms_failure: bool = False) -> str:
        """Create complaint and update rating - demonstrates compensation"""
        
        original_rating = None
        
        def create_complaint():
            nonlocal original_rating
            
            supplier = Dobavljac.objects.get(sifra_d=complaint_data['dobavljac_id'])
            original_rating = supplier.ocena
            
            if force_db_failure:
                raise Exception("Forced database failure for demonstration")
            
            # Get or create a controller
            kontrolor = KontrolorKvaliteta.objects.first()
            if not kontrolor:
                user = User.objects.filter(tip_k='kontrolor_kvaliteta').first()
                if not user:
                    raise Exception("No quality controller found")
                kontrolor = KontrolorKvaliteta.objects.create(korisnik=user)
            
            complaint = Reklamacija.objects.create(
                kontrolor=kontrolor,
                dobavljac=supplier,
                opis_problema=complaint_data['opis_problema'],
                jacina_zalbe=complaint_data['jacina_zalbe'],
                vreme_trajanja=complaint_data.get('vreme_trajanja', 1),
                status='prijem'
            )
            
            return {
                "complaint_id": complaint.reklamacija_id,
                "supplier_id": supplier.sifra_d,
                "original_rating": original_rating
            }

        def compensate_complaint():
            if saga.steps[0].result:
                complaint_id = saga.steps[0].result["complaint_id"]
                complaint = Reklamacija.objects.filter(reklamacija_id=complaint_id).first()
                if complaint:
                    complaint.delete()
                    return {"action": "complaint_deleted", "complaint_id": complaint_id}
            return {"action": "complaint_not_found"}

        def update_supplier_rating():
            complaint_result = saga.steps[0].result
            supplier = Dobavljac.objects.get(sifra_d=complaint_result["supplier_id"])
            
            # Calculate new rating based on complaint severity
            penalty = complaint_data['jacina_zalbe'] * 0.3
            new_rating = max(0, min(10, float(supplier.ocena) - penalty))
            
            supplier.ocena = new_rating
            supplier.datum_ocenjivanja = timezone.now().date()
            supplier.save()
            
            return {
                "supplier_id": supplier.sifra_d,
                "old_rating": complaint_result["original_rating"],
                "new_rating": new_rating
            }

        def compensate_rating():
            if saga.steps[1].result and original_rating is not None:
                supplier_id = saga.steps[1].result["supplier_id"]
                supplier = Dobavljac.objects.filter(sifra_d=supplier_id).first()
                if supplier:
                    supplier.ocena = original_rating
                    supplier.save()
                    return {"action": "rating_restored", "rating": original_rating}
            return {"action": "rating_not_restored"}

        def sync_complaint_to_microservice():
            if force_ms_failure:
                raise Exception("Forced microservice failure for demonstration")
                
            complaint_result = saga.steps[0].result
            rating_result = saga.steps[1].result
            
            ms_complaint_data = {
                "complaint_id": complaint_result["complaint_id"],
                "supplier_id": complaint_result["supplier_id"],
                "controller_id": 1,  # Simplified for demo
                "problem_description": complaint_data['opis_problema'],
                "severity": complaint_data['jacina_zalbe'],
                "duration": complaint_data.get('vreme_trajanja', 1),
                "status": "prijem"
            }
            
            result = self.supplier_service.create_complaint(ms_complaint_data)
            if not result:
                raise Exception("Failed to sync complaint to microservice")
                
            return {"microservice_sync": True, "complaint_id": complaint_result["complaint_id"]}

        def compensate_microservice_complaint():
            if saga.steps[2].result:
                complaint_id = saga.steps[0].result["complaint_id"]
                logger.info(f"Would delete complaint {complaint_id} from microservice")
                return {"action": "microservice_complaint_cleanup", "complaint_id": complaint_id}
            return {"action": "microservice_not_synced"}

        steps = [
            SagaStep("create_complaint", "Create Complaint", create_complaint, compensate_complaint),
            SagaStep("update_rating", "Update Supplier Rating", update_supplier_rating, compensate_rating),
            SagaStep("sync_complaint", "Sync to Microservice", sync_complaint_to_microservice, compensate_microservice_complaint)
        ]

        saga_id = self.create_saga("Create Complaint with Rating Update", steps)
        saga = self.active_sagas[saga_id]
        
        return saga_id

    def schedule_visit_with_validation_saga(self, visit_data: Dict, force_overlap: bool = False) -> str:
        """Schedule visit with overlap validation - demonstrates validation failure"""
        
        def validate_visit_time():
            from datetime import datetime
            
            datum_od = datetime.fromisoformat(visit_data['datum_od'].replace('Z', ''))
            datum_do = datetime.fromisoformat(visit_data['datum_do'].replace('Z', ''))
            
            datum_od = timezone.make_aware(datum_od.replace(tzinfo=None))
            datum_do = timezone.make_aware(datum_do.replace(tzinfo=None))
            
            if force_overlap:
                # Create an overlapping visit first
                kontrolor = KontrolorKvaliteta.objects.first()
                supplier = Dobavljac.objects.first()
                
                Poseta.objects.create(
                    kontrolor=kontrolor,
                    dobavljac=supplier,
                    datum_od=datum_od,
                    datum_do=datum_do,
                    status='zakazana'
                )
            
            # Check for overlaps
            overlapping = Poseta.objects.filter(
                datum_od__lt=datum_do,
                datum_do__gt=datum_od
            ).exclude(status='otkazana')
            
            if overlapping.exists():
                raise Exception("Visit time slot is already occupied")
            
            return {
                "validation": "passed", 
                "datum_od": datum_od.isoformat(), 
                "datum_do": datum_do.isoformat()
            }

        def compensate_validation():
            return {"action": "validation_compensation_not_needed"}

        def create_visit():
            # Get saga instance through the created saga_id
            current_saga = self.active_sagas[saga_id]
            validation_result = current_saga.steps[0].result
            
            kontrolor = KontrolorKvaliteta.objects.first()
            supplier = Dobavljac.objects.get(sifra_d=visit_data['dobavljac_id'])
            
            # Parse datetime strings back to datetime objects
            datum_od = datetime.fromisoformat(validation_result["datum_od"].replace('Z', ''))
            datum_do = datetime.fromisoformat(validation_result["datum_do"].replace('Z', ''))
            
            if datum_od.tzinfo is None:
                datum_od = timezone.make_aware(datum_od)
            if datum_do.tzinfo is None:
                datum_do = timezone.make_aware(datum_do)
            
            visit = Poseta.objects.create(
                kontrolor=kontrolor,
                dobavljac=supplier,
                datum_od=datum_od,
                datum_do=datum_do,
                status='zakazana'
            )
            
            return {"visit_id": visit.poseta_id, "supplier_id": supplier.sifra_d}

        def compensate_visit():
            current_saga = self.active_sagas[saga_id]
            if len(current_saga.steps) > 1 and current_saga.steps[1].result:
                visit_id = current_saga.steps[1].result["visit_id"]
                visit = Poseta.objects.filter(poseta_id=visit_id).first()
                if visit:
                    visit.delete()
                    return {"action": "visit_deleted", "visit_id": visit_id}
            return {"action": "visit_not_found"}

        def send_notification():
            current_saga = self.active_sagas[saga_id]
            visit_result = current_saga.steps[1].result
            
            # Simulate notification sending
            logger.info(f"Sending notification for visit {visit_result['visit_id']}")
            
            return {"notification_sent": True, "visit_id": visit_result["visit_id"]}

        def compensate_notification():
            current_saga = self.active_sagas[saga_id]
            if len(current_saga.steps) > 2 and current_saga.steps[2].result:
                visit_id = current_saga.steps[2].result["visit_id"]
                logger.info(f"Would cancel notification for visit {visit_id}")
                return {"action": "notification_cancelled", "visit_id": visit_id}
            return {"action": "notification_not_sent"}

        steps = [
            SagaStep("validate_time", "Validate Visit Time", validate_visit_time, compensate_validation),
            SagaStep("create_visit", "Create Visit", create_visit, compensate_visit),
            SagaStep("send_notification", "Send Notification", send_notification, compensate_notification)
        ]

        saga_id = self.create_saga("Schedule Visit with Validation", steps)
        
        return saga_id

# Global orchestrator instance
saga_orchestrator = SagaOrchestrator()
