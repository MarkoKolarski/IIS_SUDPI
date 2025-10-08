from django.conf import settings
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.utils import timezone
from .models import Dobavljac, Poseta, Reklamacija
from .serializers import DobavljacSerializer, VisitSerializer, ComplaintSerializer
import pytz
from django.conf import settings
from .decorators import allowed_users

class suppliers(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Dobavljac.objects.all()
    serializer_class = DobavljacSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['naziv', 'ime_sirovine', 'PIB_d']

    def check_permissions(self, request):
        super().check_permissions(request)
        allowed_types = ['administrator', 'nabavni_menadzer', 'kontrolor_kvaliteta']
        
        # For GET methods, all three roles are allowed
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            if request.user.tip_k not in allowed_types:
                self.permission_denied(
                    request,
                    message='Samo administrator, nabavni menadžer i kontrolor kvaliteta mogu pristupiti ovim podacima.'
                )
        # For POST, PUT, DELETE methods, only administrator is allowed
        elif request.method in ['POST', 'PUT', 'DELETE']:
            if request.user.tip_k != 'administrator':
                self.permission_denied(
                    request,
                    message='Samo administrator može menjati podatke dobavljača.'
                )

    def post(self, request):
        try:
            # Check if PIB already exists
            if Dobavljac.objects.filter(PIB_d=request.data.get('PIB_d')).exists():
                return Response({
                    'error': 'Dobavljač sa ovim PIB-om već postoji'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the max sifra_d value and increment by 1
            max_sifra = Dobavljac.objects.aggregate(Max('sifra_d'))['sifra_d__max'] or 0
            next_sifra = max_sifra + 1
            
            # Add sifra_d to request data
            request_data = request.data.copy()
            request_data['sifra_d'] = next_sifra

            serializer = self.get_serializer(data=request_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Dobavljač je uspešno kreiran',
                    'supplier': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, sifra_d=None):
        try:
            supplier = self.get_object(sifra_d)
            supplier.delete()
            return Response({
                'message': 'Dobavljač je uspešno obrisan'
            }, status=status.HTTP_200_OK)
        except Dobavljac.DoesNotExist:
            return Response({
                'error': 'Dobavljač nije pronađen'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, sifra_d):
        return get_object_or_404(Dobavljac, sifra_d=sifra_d)

    def get(self, request, sifra_d=None, *args, **kwargs):
        if sifra_d is not None:
            supplier = self.get_object(sifra_d)
            serializer = self.get_serializer(supplier)
            return Response(serializer.data)
        return super().get(request, *args, **kwargs)

    def put(self, request, sifra_d=None):
        if request.user.tip_k != 'administrator':
            return Response({
                'error': 'Samo administrator može ažurirati podatke dobavljača'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            supplier = self.get_object(sifra_d)
            serializer = self.get_serializer(supplier, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['kontrolor_kvaliteta'])
def visits_list(request):
    """
    API endpoint za prikaz liste zakazanih poseta
    """
    try:
        # First check if user is kontrolor_kvaliteta
        if not hasattr(request.user, 'kontrolor_kvaliteta'):
            return Response(
                {'error': 'Samo kontrolor kvaliteta može pristupiti ovom endpoint-u'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        kontrolor = request.user.kontrolor_kvaliteta
        visits = Poseta.objects.filter(kontrolor=kontrolor).select_related('dobavljac')
        
        # Filter by status if provided
        status_filter = request.GET.get('status')
        if status_filter:
            visits = visits.filter(status=status_filter)
            
        # Filter by date range if provided
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from and date_to:
            visits = visits.filter(datum_od__range=[date_from, date_to])
        
        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju poseta', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@allowed_users(['kontrolor_kvaliteta'])
def visit_detail(request, visit_id):
    """
    API endpoint za detalje posete i ažuriranje statusa
    """
    try:
        visit = get_object_or_404(Poseta, poseta_id=visit_id)
        
        if request.method == 'PUT':
            new_status = request.data.get('status')
            if new_status in dict(Poseta.STATUS_CHOICES):
                visit.status = new_status
                visit.save()
        
        return Response({
            'poseta_id': visit.poseta_id,
            'datum_od': visit.datum_od,
            'datum_do': visit.datum_do,
            'status': visit.status,
            'dobavljac': visit.dobavljac.naziv,
            'dobavljac_id': visit.dobavljac.sifra_d
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['kontrolor_kvaliteta'])
def busy_visit_slots(request):
    """
    API endpoint za dobijanje zauzetih termina
    """
    try:
        # Get all visits that are not cancelled
        busy_slots = Poseta.objects.exclude(status='otkazana').values('datum_od', 'datum_do')
        return Response(list(busy_slots), status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju zauzetih termina', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['kontrolor_kvaliteta'])
def create_visit(request):
    """
    API endpoint za kreiranje nove posete
    """
    try:
        kontrolor = request.user.kontrolor_kvaliteta
        datum_od = request.data.get('datum_od')
        datum_do = request.data.get('datum_do')
        dobavljac_id = request.data.get('dobavljac_id')
        
        # Parse datetime strings properly
        from datetime import datetime
        from django.utils import timezone
        import pytz

        # First convert to naive datetime by removing timezone info
        naive_od = datetime.fromisoformat(datum_od.replace('Z', '')).replace(tzinfo=None)
        naive_do = datetime.fromisoformat(datum_do.replace('Z', '')).replace(tzinfo=None)
        
        # Then make them timezone aware
        datum_od = timezone.make_aware(naive_od)
        datum_do = timezone.make_aware(naive_do)
        now = timezone.now()

        # Check if visit is in the past
        if datum_od < now:
            return Response(
                {'error': 'Ne možete zakazati posetu u prošlosti (BE)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for overlapping visits
        if settings.BUSINESS_LOGIC_IN_DJANGO.get('visit_overlap', True):
            overlapping_visits = Poseta.objects.filter(
                datum_od__lt=datum_do,
                datum_do__gt=datum_od
            ).exclude(status='otkazana')
        
            if overlapping_visits.exists():
                return Response(
                    {'error': 'Termin je već zauzet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        dobavljac = get_object_or_404(Dobavljac, sifra_d=dobavljac_id)
        
        visit = Poseta.objects.create(
            kontrolor=kontrolor,
            dobavljac=dobavljac,
            datum_od=datum_od,
            datum_do=datum_do,
            status='zakazana'
        )
        
        return Response({
            'message': 'Poseta je uspešno kreirana',
            'poseta_id': visit.poseta_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['kontrolor_kvaliteta'])
def complaints_list(request):
    """
    API endpoint za prikaz liste reklamacija
    """
    try:
        # First check if user is kontrolor_kvaliteta
        if not hasattr(request.user, 'kontrolor_kvaliteta'):
            return Response(
                {'error': 'Samo kontrolor kvaliteta može pristupiti ovom endpoint-u'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        kontrolor = request.user.kontrolor_kvaliteta
        complaints = Reklamacija.objects.filter(kontrolor=kontrolor).select_related('dobavljac')
        
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju reklamacija', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['kontrolor_kvaliteta'])
def create_complaint(request):
    """
    API endpoint za kreiranje nove reklamacije
    """
    try:
        if not hasattr(request.user, 'kontrolor_kvaliteta'):
            return Response(
                {'error': 'Samo kontrolor kvaliteta može podneti reklamaciju'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        kontrolor = request.user.kontrolor_kvaliteta
        dobavljac_id = request.data.get('dobavljac_id')
        jacina_zalbe = int(request.data.get('jacina_zalbe', 1))
        
        try:
            dobavljac = Dobavljac.objects.get(sifra_d=dobavljac_id)
            
            new_rating = dobavljac.ocena
            
            # Ako je konfiguracija postavljena da se koristi Django logika
            if settings.BUSINESS_LOGIC_IN_DJANGO.get('supplier_rating', True):
                # Calculate rating penalty based on complaint strength
                # For jacina_zalbe 1-3: small impact (0.3-0.9)
                # For jacina_zalbe 4-7: medium impact (1.2-2.1)
                # For jacina_zalbe 8-10: high impact (2.4-3.0)
                if jacina_zalbe <= 3:
                    penalty = jacina_zalbe * 0.3
                elif jacina_zalbe <= 7:
                    penalty = jacina_zalbe * 0.3
                else:
                    penalty = jacina_zalbe * 0.3
                
                # Update supplier's rating
                new_rating = max(0, min(10, float(dobavljac.ocena) - penalty))
                dobavljac.ocena = new_rating
                dobavljac.datum_ocenjivanja = timezone.now().date()
                dobavljac.save()
            # Ako je False, rating će biti ažuriran kroz PL/SQL trigger

            # Create complaint data
            complaint_data = {
                'dobavljac': dobavljac.sifra_d,
                'opis_problema': request.data.get('opis_problema'),
                'jacina_zalbe': jacina_zalbe,
                'vreme_trajanja': request.data.get('vreme_trajanja', 1)
            }
            
            serializer = ComplaintSerializer(data=complaint_data)
            if serializer.is_valid():
                serializer.save(
                    kontrolor=kontrolor,
                    status='prijem'
                )
                return Response({
                    'message': 'Reklamacija je uspešno kreirana',
                    'complaint': serializer.data,
                    'new_rating': new_rating
                }, status=status.HTTP_201_CREATED)
                
            return Response(
                {'error': 'Nevalidni podaci', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Dobavljac.DoesNotExist:
            return Response(
                {'error': 'Dobavljač nije pronađen'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return Response(
            {'error': 'Greška pri kreiranju reklamacije', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )