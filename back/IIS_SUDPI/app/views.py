from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import timedelta, date
from django.core.paginator import Paginator
from .models import Faktura, Dobavljac, Penal
from .serializers import (
    RegistrationSerializer, 
    FakturaSerializer,
    DobavljacSerializer,
)

def index(request):
    html = render_to_string("index.js", {})
    return HttpResponse(html)
    
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('mail_k')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_model().objects.filter(mail_k=email).first()
        
        if user is not None and user.is_active and user.check_password(password):
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_type': user.tip_k,
                'user_name': f"{user.ime_k} {user.prz_k}",
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Incorrect email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Korisnik je uspešno registrovan.',
            'user_type': user.tip_k,
            'user_name': f"{user.ime_k} {user.prz_k}",
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_finansijski_analiticar(request):
    """
    API endpoint za dashboard finansijskog analitičara
    Vraća: pregled finansija, profitabilnost dobavljača, nadolazeće isplate, troškove
    """
    
    # 1. PREGLED FINANSIJA
    ukupno_placeno = Faktura.objects.filter(status_f='isplacena').aggregate(
        total=Sum('iznos_f')
    )['total'] or Decimal('0.00')
    
    na_cekanju = Faktura.objects.filter(
        status_f__in=['primljena', 'verifikovana']
    ).aggregate(
        total=Sum('iznos_f')
    )['total'] or Decimal('0.00')
    
    isplacene_fakture = Faktura.objects.filter(
        status_f='isplacena',
        transakcija__isnull=False
    )
    
    prosecno_vreme = 0
    if isplacene_fakture.exists():
        ukupno_dana = 0
        brojac = 0
        for faktura in isplacene_fakture:
            if hasattr(faktura, 'transakcija'):
                razlika = (faktura.transakcija.datum_t.date() - faktura.datum_prijema_f).days
                ukupno_dana += razlika
                brojac += 1
        prosecno_vreme = round(ukupno_dana / brojac) if brojac > 0 else 0
    
    pregled_finansija = {
        'ukupno_placeno': float(ukupno_placeno),
        'na_cekanju': float(na_cekanju),
        'prosecno_vreme_placanja': prosecno_vreme
    }
    
    # 2. PROFITABILNOST DOBAVLJAČA
    dobavljaci_profitabilnost = []
    for dobavljac in Dobavljac.objects.filter(izabran=True):

        aktivni_ugovori = dobavljac.ugovori.filter(status_u='aktivan').count()
        
        pre_6_meseci = date.today() - timedelta(days=180)
        penali_count = Penal.objects.filter(
            ugovor__dobavljac=dobavljac,
            datum_p__gte=pre_6_meseci
        ).count()
        
        # Računamo profitabilnost: (ocena * 10) + (aktivni_ugovori * 5) - (penali * 15)
        profitabilnost = (float(dobavljac.ocena) * 10) + (aktivni_ugovori * 5) - (penali_count * 15)
        profitabilnost = max(0, min(100, profitabilnost))  # Ograniči na 0-100%
        
        dobavljaci_profitabilnost.append({
            'name': dobavljac.naziv,
            'profitability': f"{profitabilnost:.0f}%"
        })
    
    dobavljaci_profitabilnost.sort(key=lambda x: float(x['profitability'].replace('%', '')), reverse=True)
    
    # 3. NADOLAZEĆE ISPLATE
    danas = date.today()
    za_30_dana = danas + timedelta(days=30)
    
    nadolazece_isplate = []
    fakture_za_isplatu = Faktura.objects.filter(
        status_f__in=['primljena', 'verifikovana'],
        rok_placanja_f__lte=za_30_dana
    ).select_related('ugovor__dobavljac').order_by('rok_placanja_f')[:10]
    
    for faktura in fakture_za_isplatu:
        nadolazece_isplate.append({
            'id': str(faktura.sifra_f),
            'supplier': faktura.ugovor.dobavljac.naziv,
            'amount': f"{float(faktura.iznos_f):.0f}€"
        })
    
    # 4. VIZUALIZACIJA TROŠKOVA (poslednih 6 meseci)
    troskovi_po_mesecima = []
    for i in range(6):
        mesec = date.today().replace(day=1) - timedelta(days=30*i)
        sledeci_mesec = (mesec.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        troskovi_mesec = Faktura.objects.filter(
            datum_prijema_f__gte=mesec,
            datum_prijema_f__lt=sledeci_mesec,
            status_f='isplacena'
        ).aggregate(total=Sum('iznos_f'))['total'] or Decimal('0.00')
        
        troskovi_po_mesecima.append({
            'mesec': mesec.strftime('%m/%Y'),
            'iznos': float(troskovi_mesec)
        })
    
    troskovi_po_mesecima.reverse()
    
    dashboard_data = {
        'pregled_finansija': pregled_finansija,
        'profitabilnost_dobavljaca': dobavljaci_profitabilnost,
        'nadolazece_isplate': nadolazece_isplate,
        'vizualizacija_troskova': troskovi_po_mesecima
    }
    
    return Response(dashboard_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_list(request):
    """
    API endpoint za prikaz liste faktura sa filtering i search opcijama
    """
    # Početni queryset sa related objektima za optimizaciju
    queryset = Faktura.objects.select_related('ugovor__dobavljac').all()
    
    # Filtering po statusu
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'svi':
        queryset = queryset.filter(status_f=status_filter)
    
    # Filtering po dobavljaču
    dobavljac_filter = request.GET.get('dobavljac')
    if dobavljac_filter and dobavljac_filter != 'svi':
        try:
            dobavljac_id = int(dobavljac_filter)
            queryset = queryset.filter(ugovor__dobavljac__sifra_d=dobavljac_id)
        except (ValueError, TypeError):
            pass
    
    # Filtering po datumu
    datum_filter = request.GET.get('datum')
    if datum_filter and datum_filter != 'svi':
        today = date.today()
        if datum_filter == 'danas':
            queryset = queryset.filter(datum_prijema_f=today)
        elif datum_filter == 'ova_nedelja':
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            queryset = queryset.filter(datum_prijema_f__range=[start_week, end_week])
        elif datum_filter == 'ovaj_mesec':
            queryset = queryset.filter(
                datum_prijema_f__year=today.year,
                datum_prijema_f__month=today.month
            )
        elif datum_filter == 'poslednji_mesec':
            last_month = today.replace(day=1) - timedelta(days=1)
            queryset = queryset.filter(
                datum_prijema_f__year=last_month.year,
                datum_prijema_f__month=last_month.month
            )
    
    # Search funkcionalnost
    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(sifra_f__icontains=search_query) |
            Q(ugovor__dobavljac__naziv__icontains=search_query) |
            Q(iznos_f__icontains=search_query)
        )
    
    # Sortiranje po datumu prijema (najnovije prvo)
    queryset = queryset.order_by('-datum_prijema_f', '-sifra_f')
    
    # Paginacija
    page_size = int(request.GET.get('page_size', 10))
    page_number = int(request.GET.get('page', 1))
    
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)
    
    # Serijalizacija podataka
    serializer = FakturaSerializer(page.object_list, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page.number,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_filter_options(request):
    """
    API endpoint za dobijanje opcija za dropdown filtere
    """
    # Dostupni statusi faktura
    statusi = [
        {'value': 'svi', 'label': 'Svi statusi'},
        {'value': 'primljena', 'label': 'Primljeno'},
        {'value': 'verifikovana', 'label': 'Čeka verifikaciju'},
        {'value': 'isplacena', 'label': 'Plaćeno'},
        {'value': 'odbijena', 'label': 'Odbačeno'},
    ]
    
    # Dobavljači koji imaju fakture
    dobavljaci = Dobavljac.objects.filter(
        ugovori__fakture__isnull=False
    ).distinct().values('sifra_d', 'naziv')
    
    dobavljaci_opcije = [{'value': 'svi', 'label': 'Svi dobavljači'}]
    dobavljaci_opcije.extend([
        {'value': str(d['sifra_d']), 'label': d['naziv']} 
        for d in dobavljaci
    ])
    
    # Opcije za datum
    datumi = [
        {'value': 'svi', 'label': 'Svi datumi'},
        {'value': 'danas', 'label': 'Danas'},
        {'value': 'ova_nedelja', 'label': 'Ova nedelja'},
        {'value': 'ovaj_mesec', 'label': 'Ovaj mesec'},
        {'value': 'poslednji_mesec', 'label': 'Prošli mesec'},
    ]
    
    return Response({
        'statusi': statusi,
        'dobavljaci': dobavljaci_opcije,
        'datumi': datumi,
    }, status=status.HTTP_200_OK)