"""
Django REST API view-i za transakcionu obradu podataka (Saga pattern)

Ovi view-i koriste Saga orkestrator za koordinaciju transakcija
između Oracle baze (Django) i InfluxDB (mikroservis).
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging
from decimal import Decimal

from .saga_orchestrator import SagaOrchestrator, PenalSagaOrchestrator

logger = logging.getLogger(__name__)

MIKROSERVIS_URL = getattr(settings, 'MIKROSERVIS_URL', 'http://localhost:8001')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_faktura_with_payment_saga(request):
    """
    TRANSAKCIONA OBRADA PODATAKA (SAGA PATTERN)
    
    Kreira fakturu sa plaćanjem koristeći Saga pattern orkestraciju.
    
    Koraci:
    1. Kreiraj fakturu u Oracle DB (Django)
    2. Kreiraj transakciju u Oracle DB (Django)
    3. Pošalji događaj u InfluxDB (Mikroservis)
    4. Ako nešto ne uspe → Rollback (kompenzacione transakcije)
    
    POST /api/saga/faktura-sa-placanjem/
    
    Body:
    {
        "ugovor_id": 1,
        "iznos": 150000.00,
        "datum_prijema": "2025-10-01",
        "rok_placanja": "2025-11-01",
        "potvrda_transakcije": "TRX-2025-001",
        "status_transakcije": "uspesna"
    }
    
    Response (uspeh):
    {
        "success": true,
        "message": "Transakciona obrada uspešno završena",
        "data": {
            "faktura_id": 123,
            "transakcija_id": 456,
            "influxdb_status": "synced"
        },
        "saga_log": [...]
    }
    
    Response (neuspeh):
    {
        "success": false,
        "message": "Transakciona obrada neuspešna - izvršen rollback",
        "error": "...",
        "saga_log": [...]
    }
    """
    try:
        # Validacija zahtevanih polja
        required_fields = ['ugovor_id', 'iznos', 'datum_prijema', 'rok_placanja', 'potvrda_transakcije']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    "success": False,
                    "error": f"Polje '{field}' je obavezno"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Preuzmi parametre
        ugovor_id = request.data['ugovor_id']
        iznos = Decimal(str(request.data['iznos']))
        datum_prijema = request.data['datum_prijema']
        rok_placanja = request.data['rok_placanja']
        potvrda_transakcije = request.data['potvrda_transakcije']
        status_transakcije = request.data.get('status_transakcije', 'uspesna')
        
        # Pokreni Saga orkestraciju
        orchestrator = SagaOrchestrator(mikroservis_url=MIKROSERVIS_URL)
        
        success, result = orchestrator.create_faktura_with_payment(
            ugovor_id=ugovor_id,
            iznos=iznos,
            datum_prijema=datum_prijema,
            rok_placanja=rok_placanja,
            potvrda_transakcije=potvrda_transakcije,
            status_transakcije=status_transakcije
        )
        
        if success:
            return Response({
                "success": True,
                "message": result['message'],
                "data": {
                    "faktura_id": result['faktura_id'],
                    "transakcija_id": result['transakcija_id'],
                    "influxdb_status": result['influxdb_status']
                },
                "saga_log": result['saga_log']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": result['message'],
                "error": result['error'],
                "saga_log": result['saga_log']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Greška u Saga view-u: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_penal_saga(request):
    """
    TRANSAKCIONA OBRADA PODATAKA (SAGA PATTERN) - Penal
    
    Kreira penal koristeći Saga pattern orkestraciju.
    
    Koraci:
    1. Kreiraj penal u Oracle DB (Django)
    2. Pošalji događaj u InfluxDB (Mikroservis)
    3. Ako nešto ne uspe → Rollback
    
    POST /api/saga/penal/
    
    Body:
    {
        "ugovor_id": 1,
        "razlog": "Kašnjenje u isporuci robe",
        "iznos": 15000.00
    }
    """
    try:
        # Validacija
        required_fields = ['ugovor_id', 'razlog', 'iznos']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    "success": False,
                    "error": f"Polje '{field}' je obavezno"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Preuzmi parametre
        ugovor_id = request.data['ugovor_id']
        razlog = request.data['razlog']
        iznos = Decimal(str(request.data['iznos']))
        
        # Pokreni Saga orkestraciju
        orchestrator = PenalSagaOrchestrator(mikroservis_url=MIKROSERVIS_URL)
        
        success, result = orchestrator.create_penal_with_sync(
            ugovor_id=ugovor_id,
            razlog=razlog,
            iznos=iznos
        )
        
        if success:
            return Response({
                "success": True,
                "message": result['message'],
                "data": {
                    "penal_id": result['penal_id'],
                    "influxdb_status": result['influxdb_status']
                },
                "saga_log": result['saga_log']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": result['message'],
                "error": result['error'],
                "saga_log": result['saga_log']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Greška u Penal Saga view-u: {str(e)}")
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def saga_status(request):
    """
    Informacije o Saga transakcionoj obradi
    
    GET /api/saga/status/
    
    Javni endpoint - ne zahteva autentifikaciju
    """
    return Response({
        "message": "Saga Transakciona Obrada Podataka",
        "pattern": "Orkestracija",
        "baze_podataka": [
            {
                "tip": "Relaciona",
                "naziv": "Oracle Database",
                "lokacija": "Django (localhost:8000)"
            },
            {
                "tip": "NoSQL - Time Series",
                "naziv": "InfluxDB",
                "lokacija": "Mikroservis (localhost:8001)"
            }
        ],
        "funkcionalnosti": [
            {
                "endpoint": "POST /api/saga/faktura-sa-placanjem/",
                "opis": "Kreiranje fakture sa transakcijom (Oracle + InfluxDB)",
                "koraci": [
                    "1. Kreiraj fakturu u Oracle DB",
                    "2. Kreiraj transakciju u Oracle DB",
                    "3. Pošalji događaj u InfluxDB",
                    "4. Rollback ako nešto ne uspe"
                ]
            },
            {
                "endpoint": "POST /api/saga/penal/",
                "opis": "Kreiranje penala (Oracle + InfluxDB)",
                "koraci": [
                    "1. Kreiraj penal u Oracle DB",
                    "2. Pošalji događaj u InfluxDB",
                    "3. Rollback ako nešto ne uspe"
                ]
            }
        ],
        "mikroservis_url": MIKROSERVIS_URL,
        "mikroservis_status": "active"
    })
