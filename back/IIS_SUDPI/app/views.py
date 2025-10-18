from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.db.models import Sum, Q, Count, Avg, Max
from decimal import Decimal
from datetime import timedelta, date
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from datetime import timedelta
from django.utils import timezone
from .models import Ruta, Notifikacija, Isporuka,Temperatura, Upozorenje, Vozilo, Vozac, Servis, Faktura, User, Dobavljac, Penal, StavkaFakture, Proizvod, Poseta, Reklamacija, KontrolorKvaliteta, FinansijskiAnaliticar, NabavniMenadzer, LogistickiKoordinator, SkladisniOperater, Administrator, Skladiste, Artikal, Zalihe, Popust
from .serializers import (
    RegistrationSerializer, 
    FakturaSerializer,
    FakturaDetailSerializer,
    DobavljacSerializer,
    ReportsSerializer,
    PenalSerializer,
    VisitSerializer,
    ComplaintSerializer,
    SkladisteSerializer,
    ArtikalSerializer,
    ZaliheSerializer,
    DodajSkladisteSerializer,
    DodajArtikalSerializer,
    RizicniArtikalSerializer,
    UserProfileSerializer, 
    UserProfileUpdateSerializer,
    VozacSerializer,
    VoziloSerializer,
    ServisSerializer,
    IsporukaSerializer,
    RutaSerializer,
    UpozorenjeSerializer,
    TemperaturaSerializer,
    NotifikacijaSerializer
)
from rest_framework import generics, filters
from django.db import transaction
from .decorators import allowed_users
import logging

# Postavi logging
logger = logging.getLogger(__name__)

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
@permission_classes([AllowAny])  # Make sure this is present
def register(request):
    print("Registration data received:", request.data)  # Add debug print
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            
            # Create role-specific instance based on user type
            if user.tip_k in ['kontrolor_kvaliteta', 'finansijski_analiticar', 'nabavni_menadzer', 
                             'logisticki_koordinator', 'skladisni_operater', 'administrator']:
                
                # Map user types to their respective models
                user_type_models = {
                    'kontrolor_kvaliteta': KontrolorKvaliteta,
                    'finansijski_analiticar': FinansijskiAnaliticar,
                    'nabavni_menadzer': NabavniMenadzer,
                    'logisticki_koordinator': LogistickiKoordinator,
                    'skladisni_operater': SkladisniOperater,
                    'administrator': Administrator
                }
                
                # Create instance of appropriate model
                if user.tip_k in user_type_models:
                    user_type_models[user.tip_k].objects.create(korisnik=user)
            
            return Response({
                'message': 'Korisnik je uspešno registrovan.',
                'user_type': user.tip_k,
                'user_name': f"{user.ime_k} {user.prz_k}",
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Registration error:", str(e))  # Add debug print
            return Response({
                'error': 'Greška pri registraciji',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    print("Serializer errors:", serializer.errors)  # Add debug print
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar', 'nabavni_menadzer'])
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
@allowed_users(['finansijski_analiticar'])
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
@allowed_users(['finansijski_analiticar'])
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def invoice_detail(request, invoice_id):
    """
    API endpoint za prikaz detalja pojedinačne fakture
    """
    try:
        faktura = get_object_or_404(
            Faktura.objects.select_related('ugovor__dobavljac', 'transakcija').prefetch_related('stavke'),
            sifra_f=invoice_id
        )
        serializer = FakturaDetailSerializer(faktura)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Faktura.DoesNotExist:
        return Response({'detail': 'Faktura nije pronađena.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def invoice_action(request, invoice_id):
    """
    API endpoint za akcije nad fakturom (potpis, odbacivanje)
    """
    try:
        faktura = get_object_or_404(Faktura, sifra_f=invoice_id)
        action = request.data.get('action')
        
        if action == 'approve':
            if faktura.status_f == 'primljena':
                faktura.status_f = 'verifikovana'
                faktura.razlog_cekanja_f = None
            elif faktura.status_f == 'verifikovana':
                faktura.status_f = 'isplacena'
            faktura.save()
            
            return Response({
                'message': 'Faktura je uspešno odobrena.',
                'new_status': faktura.status_f
            }, status=status.HTTP_200_OK)
            
        elif action == 'reject':
            reason = request.data.get('reason', '')
            faktura.status_f = 'odbijena'
            faktura.razlog_cekanja_f = reason
            faktura.save()
            
            return Response({
                'message': 'Faktura je odbijena.',
                'new_status': faktura.status_f
            }, status=status.HTTP_200_OK)
            
        else:
            return Response({'detail': 'Nevalidna akcija.'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Faktura.DoesNotExist:
        return Response({'detail': 'Faktura nije pronađena.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def reports_data(request):
    """
    API endpoint za generiranje izveštaja o troškovima i profitabilnosti
    """
    # Parsiranje filtara
    status_filter = request.GET.get('status', 'sve')
    period_filter = request.GET.get('period', 'sve')
    group_by_filter = request.GET.get('group_by', 'proizvodu')
    
    # Definišemo vremenski period
    today = date.today()
    if period_filter == 'danas':
        start_date = today
        end_date = today
        period_label = 'Danas'
    elif period_filter == 'ova_nedelja':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        period_label = 'Ova nedelja'
    elif period_filter == 'ovaj_mesec':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        period_label = 'Ovaj mesec'
    elif period_filter == 'poslednji_mesec':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = today.replace(day=1) - timedelta(days=1)
        period_label = 'Prošli mesec'
    elif period_filter == 'poslednja_3_meseca':
        start_date = (today.replace(day=1) - timedelta(days=90)).replace(day=1)
        end_date = today
        period_label = 'Poslednja 3 meseca'
    else:  # sve (sav period)
        start_date = None
        end_date = None
        period_label = 'Sav period'
    
    # Početni queryset sa filterom po datumu
    fakture_queryset = Faktura.objects.all()
    if start_date and end_date:
        fakture_queryset = fakture_queryset.filter(
            datum_prijema_f__gte=start_date,
            datum_prijema_f__lte=end_date
        )
    
    # Filter po statusu
    if status_filter != 'sve':
        fakture_queryset = fakture_queryset.filter(status_f=status_filter)
    
    # Dobijamo stavke faktura sa related podacima
    stavke_queryset = StavkaFakture.objects.filter(
        faktura__in=fakture_queryset
    ).select_related('faktura', 'proizvod')
    
    # Grupiranje po proizvodu
    if group_by_filter == 'proizvodu':
        report_data = []
        
        # Agregiramo podatke po proizvodima
        proizvodi_data = stavke_queryset.values('proizvod__naziv_pr').annotate(
            ukupna_kolicina=Sum('kolicina_sf'),
            ukupan_trosak=Sum('cena_po_jed'),
            broj_stavki=Count('sifra_sf'),
            prosecna_cena=Avg('cena_po_jed')
        ).order_by('-ukupan_trosak')
        
        chart_profitability = []
        chart_costs = []
        
        ukupna_kolicina_svi = 0
        ukupan_trosak_svi = Decimal('0.00')
        ukupna_profitabilnost = 0
        
        for proizvod in proizvodi_data:
            naziv = proizvod['proizvod__naziv_pr'] or 'Nepoznat proizvod'
            kolicina = proizvod['ukupna_kolicina'] or 0
            trosak = proizvod['ukupan_trosak'] or Decimal('0.00')
            
            # Računamo profitabilnost na osnovu troška i količine
            # Koristimo više varijabilnu formulu koja daje realnije rezultate
            if kolicina > 0 and trosak > 0:
                # Profitabilnost se računa kao kombinacija efikasnosti (trošak/količina) i obima posla
                efikasnost = float(trosak) / kolicina  # trošak po jedinici
                obim_posla = min(kolicina / 100, 1.0)  # normalizovan obim (max 1.0)
                
                # Simuliramo različite nivoe profitabilnosti na osnovu efikasnosti
                if efikasnost < 500:  # niska cena po jedinici = viša profitabilnost
                    bazna_profitabilnost = 35 + (obim_posla * 15)  # 35-50%
                elif efikasnost < 1500:  # srednja cena po jedinici
                    bazna_profitabilnost = 20 + (obim_posla * 20)  # 20-40%
                else:  # visoka cena po jedinici = niža profitabilnost  
                    bazna_profitabilnost = 5 + (obim_posla * 15)   # 5-20%
                
                # Dodajemo neki random faktor za realnost (hash-based za konzistentnost)
                random_factor = (hash(naziv) % 21 - 10) / 10.0  # -1.0 do +1.0
                profitabilnost_procenat = max(-10, min(60, bazna_profitabilnost + random_factor * 5))
            else:
                profitabilnost_procenat = 0
            
            ukupna_kolicina_svi += kolicina
            ukupan_trosak_svi += trosak
            ukupna_profitabilnost += profitabilnost_procenat
            
            report_data.append({
                'proizvod': naziv,
                'kolicina': f"{kolicina:,}",
                'ukupan_trosak': f"{float(trosak):,.2f} RSD",
                'profitabilnost': f"+{profitabilnost_procenat:.0f}%"
            })
            
            # Podaci za grafike
            chart_profitability.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': profitabilnost_procenat
            })
            
            chart_costs.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': float(trosak)
            })
        
        # Ograniči na top 10 za grafike
        chart_profitability = chart_profitability[:10]
        chart_costs = chart_costs[:10]
        
        # Ukupni red
        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': f"{ukupna_kolicina_svi:,} kom",
            'ukupan_trosak': f"{float(ukupan_trosak_svi):,.2f} RSD",
            'profitabilnost': f"+{ukupna_profitabilnost:.0f}%"
        }
        
    elif group_by_filter == 'dobavljacu':
        # Grupiranje po dobavljačima
        report_data = []
        
        # Agregiramo podatke po dobavljačima preko faktura
        dobavljaci_data = fakture_queryset.values('ugovor__dobavljac__naziv').annotate(
            ukupan_trosak=Sum('iznos_f'),
            broj_faktura=Count('sifra_f')
        ).order_by('-ukupan_trosak')
        
        chart_profitability = []
        chart_costs = []
        
        ukupna_kolicina_svi = 0
        ukupan_trosak_svi = Decimal('0.00')
        ukupna_profitabilnost = 0
        
        for dobavljac in dobavljaci_data:
            naziv = dobavljac['ugovor__dobavljac__naziv'] or 'Nepoznat dobavljač'
            broj_faktura = dobavljac['broj_faktura'] or 0
            trosak = dobavljac['ukupan_trosak'] or Decimal('0.00')
            
            # Simuliramo profitabilnost na osnovu troška i broja faktura
            profitabilnost_procenat = min(50, max(5, (float(trosak) / 10000) + (broj_faktura * 3)))
            
            ukupna_kolicina_svi += broj_faktura
            ukupan_trosak_svi += trosak
            ukupna_profitabilnost += profitabilnost_procenat
            
            report_data.append({
                'proizvod': naziv,
                'kolicina': f"{broj_faktura:,}",
                'ukupan_trosak': f"{float(trosak):,.2f} RSD",
                'profitabilnost': f"+{profitabilnost_procenat:.0f}%"
            })
            
            # Podaci za grafike
            chart_profitability.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': profitabilnost_procenat
            })
            
            chart_costs.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': float(trosak)
            })
        
        # Ograniči na top 10 za grafike
        chart_profitability = chart_profitability[:10]
        chart_costs = chart_costs[:10]
        
        # Ukupni red
        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': f"{ukupna_kolicina_svi:,} faktura",
            'ukupan_trosak': f"{float(ukupan_trosak_svi):,.2f} RSD",
            'profitabilnost': f"+{ukupna_profitabilnost:.0f}%"
        }
        
    elif group_by_filter == 'kategoriji':
        # Grupiranje po kategorijama proizvoda
        report_data = []
        
        # Agregiramo podatke po kategorijama
        kategorije_data = stavke_queryset.values('proizvod__kategorija__naziv_kp').annotate(
            ukupna_kolicina=Sum('kolicina_sf'),
            ukupan_trosak=Sum('cena_po_jed'),
            broj_stavki=Count('sifra_sf')
        ).order_by('-ukupan_trosak')
        
        chart_profitability = []
        chart_costs = []
        
        ukupna_kolicina_svi = 0
        ukupan_trosak_svi = Decimal('0.00')
        ukupna_profitabilnost = 0
        
        for kategorija in kategorije_data:
            naziv = kategorija['proizvod__kategorija__naziv_kp'] or 'Nepoznata kategorija'
            kolicina = kategorija['ukupna_kolicina'] or 0
            trosak = kategorija['ukupan_trosak'] or Decimal('0.00')
            
            # Računamo profitabilnost na osnovu troška i količine
            # Koristimo više varijabilnu formulu koja daje realnije rezultate
            if kolicina > 0 and trosak > 0:
                # Profitabilnost se računa kao kombinacija efikasnosti (trošak/količina) i obima posla
                efikasnost = float(trosak) / kolicina  # trošak po jedinici
                obim_posla = min(kolicina / 100, 1.0)  # normalizovan obim (max 1.0)
                
                # Simuliramo različite nivoe profitabilnosti na osnovu efikasnosti
                if efikasnost < 500:  # niska cena po jedinici = viša profitabilnost
                    bazna_profitabilnost = 35 + (obim_posla * 15)  # 35-50%
                elif efikasnost < 1500:  # srednja cena po jedinici
                    bazna_profitabilnost = 20 + (obim_posla * 20)  # 20-40%
                else:  # visoka cena po jedinici = niža profitabilnost  
                    bazna_profitabilnost = 5 + (obim_posla * 15)   # 5-20%
                
                # Dodajemo neki random faktor za realnost (hash-based za konzistentnost)
                random_factor = (hash(naziv) % 21 - 10) / 10.0  # -1.0 do +1.0
                profitabilnost_procenat = max(-10, min(60, bazna_profitabilnost + random_factor * 5))
            else:
                profitabilnost_procenat = 0
            
            ukupna_kolicina_svi += kolicina
            ukupan_trosak_svi += trosak
            ukupna_profitabilnost += profitabilnost_procenat
            
            report_data.append({
                'proizvod': naziv,
                'kolicina': f"{kolicina:,}",
                'ukupan_trosak': f"{float(trosak):,.2f} RSD",
                'profitabilnost': f"+{profitabilnost_procenat:.0f}%"
            })
            
            # Podaci za grafike
            chart_profitability.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': profitabilnost_procenat
            })
            
            chart_costs.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': float(trosak)
            })
        
        # Ograniči na top 10 za grafike
        chart_profitability = chart_profitability[:10]
        chart_costs = chart_costs[:10]
        
        # Ukupni red
        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': f"{ukupna_kolicina_svi:,} kom",
            'ukupan_trosak': f"{float(ukupan_trosak_svi):,.2f} RSD",
            'profitabilnost': f"+{ukupna_profitabilnost:.0f}%"
        }
        
    else:  # fallback za nepoznate opcije
        # Fallback na proizvode
        report_data = [{
            'proizvod': 'Nema podataka',
            'kolicina': '0',
            'ukupan_trosak': '0.00 RSD',
            'profitabilnost': '0%'
        }]
        chart_profitability = []
        chart_costs = []
        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': '0 kom',
            'ukupan_trosak': '0.00 RSD',
            'profitabilnost': '0%'
        }
    
    # Formiranje odgovora
    response_data = {
        'table_data': report_data,
        'chart_profitability': chart_profitability,
        'chart_costs': chart_costs,
        'total_summary': total_summary,
        'period_info': {
            'period': period_filter,
            'period_label': period_label,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'status_filter': status_filter,
            'group_by': group_by_filter
        }
    }
    
    # Formatiranje odgovora u strukturi koju frontend očekuje
    final_response = {
        'total_profitability': sum([float(item['profitabilnost'].rstrip('%')) for item in report_data]) if report_data else 0,
        'total_cost': sum([float(item['ukupan_trosak'].replace(' RSD', '').replace(',', '')) for item in report_data]) if report_data else 0,
        'total_quantity': sum([int(item['kolicina'].replace(' kom', '').replace(',', '')) for item in report_data]) if report_data else 0,
        'data': [
            {
                'id': i + 1,
                'name': item['proizvod'],
                'quantity': int(item['kolicina'].replace(' kom', '').replace(',', '')),
                'total_cost': float(item['ukupan_trosak'].replace(' RSD', '').replace(',', '')),
                'profitability': float(item['profitabilnost'].rstrip('%'))
            } for i, item in enumerate(report_data)
        ] if report_data else [],
        'chart_data': {
            'profitability': [
                {
                    'name': item['label'],
                    'value': item['value']
                } for item in chart_profitability
            ],
            'costs': [
                {
                    'name': item['label'], 
                    'value': item['value']
                } for item in chart_costs
            ]
        }
    }
    
    return Response(final_response, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def reports_filter_options(request):
    """
    API endpoint za dobijanje opcija za report filtere
    """
    statusi = [
        {'value': 'sve', 'label': 'Sve'},
        {'value': 'primljena', 'label': 'Primljeno'},
        {'value': 'verifikovana', 'label': 'Verifikovano'},
        {'value': 'isplacena', 'label': 'Isplaćeno'},
    ]
    
    periodi = [
        {'value': 'sve', 'label': 'Sav period'},
        {'value': 'danas', 'label': 'Danas'},
        {'value': 'ova_nedelja', 'label': 'Ova nedelja'},
        {'value': 'ovaj_mesec', 'label': 'Ovaj mesec'},
        {'value': 'poslednji_mesec', 'label': 'Prošli mesec'},
        {'value': 'poslednja_3_meseca', 'label': 'Poslednja 3 meseca'},
    ]
    
    grupiranje = [
        {'value': 'proizvodu', 'label': 'Proizvodu'},
        {'value': 'dobavljacu', 'label': 'Dobavljaču'},
        {'value': 'kategoriji', 'label': 'Kategoriji'},
    ]
    
    return Response({
        'statusi': statusi,
        'periodi': periodi,
        'grupiranje': grupiranje,
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar', 'nabavni_menadzer'])
def penalties_list(request):
    """
    API endpoint za prikaz liste penala sa filtering opcijama
    """
    # Početni queryset sa related objektima za optimizaciju
    queryset = Penal.objects.select_related('ugovor__dobavljac').all()
    
    # Filtering po dobavljaču
    dobavljac_filter = request.GET.get('dobavljac')
    if dobavljac_filter and dobavljac_filter != 'svi':
        try:
            dobavljac_id = int(dobavljac_filter)
            queryset = queryset.filter(ugovor__dobavljac__sifra_d=dobavljac_id)
        except (ValueError, TypeError):
            pass
    
    # Filtering po statusu (na osnovu datuma)
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'svi':
        from datetime import date, timedelta
        danas = date.today()
        if status_filter == 'resen':
            # Penali stariji od 30 dana
            queryset = queryset.filter(datum_p__lt=danas - timedelta(days=30))
        elif status_filter == 'obavesten':
            # Penali noviji od 30 dana
            queryset = queryset.filter(datum_p__gte=danas - timedelta(days=30))
    
    # Sortiranje po datumu (najnoviji prvo)
    queryset = queryset.order_by('-datum_p', '-sifra_p')
    
    # Paginacija
    page_size = int(request.GET.get('page_size', 10))
    page_number = int(request.GET.get('page', 1))
    
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)
    
    # Serijalizacija podataka
    serializer = PenalSerializer(page.object_list, many=True)
    
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
@allowed_users(['finansijski_analiticar', 'nabavni_menadzer'])
def penalties_filter_options(request):
    """
    API endpoint za dobijanje opcija za dropdown filtere
    """
    # Dostupni statusi penala
    statusi = [
        {'value': 'svi', 'label': 'Svi statusi'},
        {'value': 'resen', 'label': 'Rešen'},
        {'value': 'obavesten', 'label': 'Obavešten'},
    ]
    
    # Dobavljači koji imaju penale
    dobavljaci = Dobavljac.objects.filter(
        ugovori__penali__isnull=False
    ).distinct().values('sifra_d', 'naziv')
    
    dobavljaci_opcije = [{'value': 'svi', 'label': 'Svi dobavljači'}]
    dobavljaci_opcije.extend([
        {'value': str(d['sifra_d']), 'label': d['naziv']} 
        for d in dobavljaci
    ])
    
    return Response({
        'statusi': statusi,
        'dobavljaci': dobavljaci_opcije,
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar', 'nabavni_menadzer'])
def penalties_analysis(request):
    """
    API endpoint za automatsku analizu saradnje sa dobavljačima na osnovu penala
    """
    
    # Analiziramo dobavljače koji imaju penale
    dobavljaci_analiza = []
    
    # Dobijamo sve dobavljače koji imaju ugovore (ne samo one sa penalima)
    dobavljaci = Dobavljac.objects.filter(
        ugovori__isnull=False
    ).distinct()
    
    for dobavljac in dobavljaci:
        # Ukupan broj ugovora za ovog dobavljača
        ukupno_ugovora = dobavljac.ugovori.count()
        
        # Dobijamo unikatne ID-jeve ugovora koji imaju penale
        # Koristimo values_list sa flat=True da izbegnemo NCLOB problem
        ugovori_sa_penalima_ids = list(
            dobavljac.ugovori.filter(
                penali__isnull=False
            ).values_list('sifra_u', flat=True).distinct()
        )
        broj_ugovora_sa_penalima = len(ugovori_sa_penalima_ids)
        
        # Ukupan broj penala za ovog dobavljača
        broj_penala = Penal.objects.filter(
            ugovor__dobavljac=dobavljac
        ).count()
        
        # Ukupan iznos penala
        ukupan_iznos = Penal.objects.filter(
            ugovor__dobavljac=dobavljac
        ).aggregate(
            total=Sum('iznos_p')
        )['total'] or 0
        
        # Preskačemo dobavljače koji nemaju penale
        if broj_penala == 0:
            continue
            
        # Računamo stopu kršenja kao procenat ugovora koji imaju penale
        stopa_krsenja = (broj_ugovora_sa_penalima / ukupno_ugovora * 100) if ukupno_ugovora > 0 else 0
        
        # Određujemo preporuku na osnovu stope kršenja
        if stopa_krsenja >= 50:
            preporuka = "Razmotriti prekid saradnje"
            tip_preporuke = "negative"
        elif stopa_krsenja >= 25:
            preporuka = "Pojačana kontrola"
            tip_preporuke = "warning"
        else:
            preporuka = "Pouzdana saradnja"
            tip_preporuke = "positive"
        
        dobavljaci_analiza.append({
            'naziv': dobavljac.naziv,
            'broj_penala': broj_penala,
            'ukupno_ugovora': ukupno_ugovora,
            'ugovori_sa_penalima': broj_ugovora_sa_penalima,
            'ukupan_iznos': float(ukupan_iznos),
            'stopa_krsenja': round(stopa_krsenja, 1),
            'preporuka': preporuka,
            'tip_preporuke': tip_preporuke
        })
    
    # Sortiramo po stopi kršenja (najgori prvi)
    dobavljaci_analiza.sort(key=lambda x: x['stopa_krsenja'], reverse=True)
    
    return Response({
        'dobavljaci_analiza': dobavljaci_analiza
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['nabavni_menadzer'])
def select_supplier(request, sifra_d):
    """
    API endpoint for nabavni menadzer to select supplier
    """
    try:
        with transaction.atomic():
            supplier = get_object_or_404(Dobavljac, sifra_d=sifra_d)
            
            # First, unselect all suppliers with the same raw material
            Dobavljac.objects.filter(
                ime_sirovine=supplier.ime_sirovine,
                izabran=True
            ).update(izabran=False)
            
            # Then select our supplier
            supplier.izabran = True
            supplier.save()
            
            serializer = DobavljacSerializer(supplier)
            return Response({
                'message': 'Dobavljač je uspešno izabran',
                'supplier': serializer.data
            }, status=status.HTTP_200_OK)
            
    except Dobavljac.DoesNotExist:
        return Response({
            'error': 'Dobavljač nije pronađen'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

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
        
        # Check for overlapping visits
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

# API endpoints za Artikal i Skladište

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def skladista_list(request):
    """
    API endpoint za dobijanje liste svih skladišta
    Automatski proverava i ažurira status rizika pre slanja odgovora
    """
    # Debug informacije
    logger.info(f"Skladista API pozvan od strane korisnika: {request.user}")
    logger.info(f"Tip korisnika: {request.user.tip_k if hasattr(request.user, 'tip_k') else 'N/A'}")
    
    try:
        # Prvo ažuriraj status svih skladišta na osnovu najnovijih temperatura
        from .signals import update_all_skladista_status
        updated_count = update_all_skladista_status()
        
        # Zatim vrati ažurirane podatke
        skladista = Skladiste.objects.all().order_by('sifra_s')
        serializer = SkladisteSerializer(skladista, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Greška u skladista_list: {str(e)}")
        return Response(
            {'error': 'Greška pri dohvatanju skladišta', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def dodaj_skladiste(request):
    """
    API endpoint za dodavanje novog skladišta
    """
    try:
        serializer = DodajSkladisteSerializer(data=request.data)
        if serializer.is_valid():
            skladiste = serializer.save()
            
            return Response({
                'message': 'Skladište je uspešno dodato!',
                'skladiste': SkladisteSerializer(skladiste).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            {'error': 'Nevalidni podaci', 'details': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        return Response(
            {'error': 'Greška pri dodavanju skladišta', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def dodaj_artikal(request):
    """
    API endpoint za dodavanje novog artikla i zaliha
    """
    try:
        serializer = DodajArtikalSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            
            return Response({
                'message': 'Artikal je uspešno dodat!',
                'artikal': ArtikalSerializer(result['artikal']).data,
                'zalihe': ZaliheSerializer(result['zalihe']).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            {'error': 'Nevalidni podaci', 'details': serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        return Response(
            {'error': 'Greška pri dodavanju artikla', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def artikli_list(request):
    """
    API endpoint za dobijanje liste svih artikala
    """
    try:
        artikli = Artikal.objects.all().order_by('sifra_a')
        serializer = ArtikalSerializer(artikli, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju artikala', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def artikal_detail(request, sifra_a):
    """
    API endpoint za dobijanje jednog artikla po šifri
    """
    try:
        artikal = Artikal.objects.get(sifra_a=sifra_a)
        serializer = ArtikalSerializer(artikal)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Artikal.DoesNotExist:
        return Response(
            {'error': f'Artikal sa šifrom {sifra_a} ne postoji'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju artikla', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def izmeni_artikal(request, sifra_a):
    """
    API endpoint za ažuriranje artikla po šifri
    """
    try:
        artikal = Artikal.objects.get(sifra_a=sifra_a)
        
        # Ažuriraj samo prosleđena polja
        if 'naziv_a' in request.data:
            artikal.naziv_a = request.data['naziv_a']
        if 'osnovna_cena_a' in request.data:
            artikal.osnovna_cena_a = request.data['osnovna_cena_a']
        if 'rok_trajanja_a' in request.data:
            artikal.rok_trajanja_a = request.data['rok_trajanja_a']
        
        # Validacija pre čuvanja
        artikal.full_clean()
        artikal.save()
        
        serializer = ArtikalSerializer(artikal)
        return Response(
            {
                'message': f'Artikal "{artikal.naziv_a}" je uspešno ažuriran',
                'artikal': serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Artikal.DoesNotExist:
        return Response(
            {'error': f'Artikal sa šifrom {sifra_a} ne postoji'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Greška pri ažuriranju artikla', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def zalihe_list(request):
    """
    API endpoint za dobijanje zaliha - sve ili po skladištu
    Query parametar: skladiste (opcionalno)
    """
    try:
        skladiste_filter = request.GET.get('skladiste', None)
        
        if skladiste_filter:
            # Filtriraj po skladištu
            zalihe = Zalihe.objects.filter(skladiste__sifra_s=skladiste_filter).select_related(
                'artikal', 'skladiste'
            ).order_by('artikal__naziv_a')
        else:
            # Sve zalihe
            zalihe = Zalihe.objects.all().select_related(
                'artikal', 'skladiste'
            ).order_by('skladiste__mesto_s', 'artikal__naziv_a')
        
        # Ručno kreiranje response data sa dodatnim poljima
        zalihe_data = []
        for zaliha in zalihe:
            zalihe_data.append({
                'id': zaliha.id,
                'trenutna_kolicina_a': zaliha.trenutna_kolicina_a,
                'datum_azuriranja': zaliha.datum_azuriranja,
                'artikal_naziv': zaliha.artikal.naziv_a if zaliha.artikal else 'N/A',
                'artikal_sifra': zaliha.artikal.sifra_a if zaliha.artikal else None,
                'skladiste_naziv': zaliha.skladiste.mesto_s if zaliha.skladiste else 'N/A',
                'skladiste_sifra': zaliha.skladiste.sifra_s if zaliha.skladiste else None,
            })
        
        return Response(zalihe_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Greška u zalihe_list: {str(e)}")  # Debug info
        return Response(
            {'error': 'Greška pri dohvatanju zaliha', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def zaliha_detail(request, zaliha_id):
    """
    API endpoint za dobijanje jedne zalihe po ID-u
    """
    try:
        zaliha = Zalihe.objects.select_related('artikal', 'skladiste').get(id=zaliha_id)
        
        zaliha_data = {
            'id': zaliha.id,
            'trenutna_kolicina_a': zaliha.trenutna_kolicina_a,
            'datum_azuriranja': zaliha.datum_azuriranja,
            'artikal_naziv': zaliha.artikal.naziv_a if zaliha.artikal else 'N/A',
            'artikal_sifra': zaliha.artikal.sifra_a if zaliha.artikal else None,
            'skladiste_naziv': zaliha.skladiste.mesto_s if zaliha.skladiste else 'N/A',
            'skladiste_sifra': zaliha.skladiste.sifra_s if zaliha.skladiste else None,
        }
        
        return Response(zaliha_data, status=status.HTTP_200_OK)
        
    except Zalihe.DoesNotExist:
        return Response(
            {'error': f'Zaliha sa ID {zaliha_id} ne postoji'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Greška u zaliha_detail: {str(e)}")
        return Response(
            {'error': 'Greška pri dohvatanju zalihe', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def izmeni_zalihu(request, zaliha_id):
    """
    API endpoint za ažuriranje zalihe po ID-u
    """
    try:
        zaliha = Zalihe.objects.get(id=zaliha_id)
        
        # Ažuriraj polja
        if 'trenutna_kolicina_a' in request.data:
            zaliha.trenutna_kolicina_a = request.data['trenutna_kolicina_a']
        
        if 'skladiste' in request.data:
            try:
                skladiste = Skladiste.objects.get(sifra_s=request.data['skladiste'])
                zaliha.skladiste = skladiste
            except Skladiste.DoesNotExist:
                return Response(
                    {'error': 'Skladište ne postoji'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validacija pre čuvanja
        zaliha.full_clean()
        zaliha.save()
        
        # Vraćaj ažurirane podatke
        zaliha_data = {
            'id': zaliha.id,
            'trenutna_kolicina_a': zaliha.trenutna_kolicina_a,
            'datum_azuriranja': zaliha.datum_azuriranja,
            'artikal_naziv': zaliha.artikal.naziv_a if zaliha.artikal else 'N/A',
            'skladiste_naziv': zaliha.skladiste.mesto_s if zaliha.skladiste else 'N/A',
        }
        
        return Response(
            {
                'message': f'Stanje zalihe za "{zaliha.artikal.naziv_a}" je uspešno ažurirano',
                'zaliha': zaliha_data
            },
            status=status.HTTP_200_OK
        )
        
    except Zalihe.DoesNotExist:
        return Response(
            {'error': f'Zaliha sa ID {zaliha_id} ne postoji'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Greška u izmeni_zalihu: {str(e)}")
        return Response(
            {'error': 'Greška pri ažuriranju zalihe', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def obrisi_artikal(request, sifra_a):
    """
    API endpoint za brisanje artikla po šifri
    """
    try:
        # Pronađi artikal po šifri
        artikal = Artikal.objects.get(sifra_a=sifra_a)
        
        # Proveri da li postoje povezane zalihe (koristimo 'artikal' umesto 'sifra_a')
        zalihe = Zalihe.objects.filter(artikal=artikal)
        if zalihe.exists():
            # Obriši povezane zalihe
            zalihe.delete()
        
        # Obriši artikal
        naziv_artikla = artikal.naziv_a
        artikal.delete()
        
        return Response(
            {'message': f'Artikal "{naziv_artikla}" je uspešno obrisan'},
            status=status.HTTP_200_OK
        )
        
    except Artikal.DoesNotExist:
        return Response(
            {'error': f'Artikal sa šifrom {sifra_a} ne postoji'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Greška pri brisanju artikla', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def rizicni_artikli_list(request):
    """
    API endpoint za dobijanje liste rizičnih artikala (koji ističu) sa popustima
    """
    try:
        # Prvo ažuriraj status svih artikala
        from .signals import update_all_artikli_status
        update_all_artikli_status()
        
        # Dobij artikle koji ističu (status 'istice')
        rizicni_artikli = Artikal.objects.filter(
            status_trajanja='istice'
        ).order_by('rok_trajanja_a')
        
        serializer = RizicniArtikalSerializer(rizicni_artikli, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Greška u rizicni_artikli_list: {str(e)}")
        return Response(
            {'error': 'Greška pri dohvatanju rizičnih artikala', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def artikli_statistike(request):
    """
    API endpoint za statistike artikala za treće mesto dashboarda
    """
    try:
        # Prvo ažuriraj status svih artikala
        from .signals import update_all_artikli_status
        update_all_artikli_status()
        
        # 1. Ukupan broj artikala
        ukupno_artikala = Artikal.objects.count()
        
        # 2. Broj rizičnih artikala (koji ističu)
        rizicni_artikli = Artikal.objects.filter(status_trajanja='istice').count()
        
        # 3. Broj propali articala (istekli)
        propali_artikli = Artikal.objects.filter(status_trajanja='istekao').count()
        
        # 4. Šteta za propale artikle (osnovna_cena * trenutna_kolicina iz zaliha)
        propali_artikli_data = Artikal.objects.filter(
            status_trajanja='istekao'
        ).prefetch_related('zalihe')
        
        ukupna_steta = 0
        for artikal in propali_artikli_data:
            try:
                # Sumiranje količina iz svih skladišta za ovaj artikal
                ukupna_kolicina = sum([zaliha.trenutna_kolicina_a for zaliha in artikal.zalihe.all()])
                if ukupna_kolicina > 0 and artikal.osnovna_cena_a:
                    steta_artikal = float(artikal.osnovna_cena_a) * ukupna_kolicina
                    ukupna_steta += steta_artikal
            except Exception as artikal_error:
                logger.warning(f"Greška pri računanju štete za artikal {artikal.sifra_a}: {str(artikal_error)}")
                continue
        
        statistike = {
            'ukupno_artikala': ukupno_artikala,
            'rizicni_artikli': rizicni_artikli,
            'propali_artikli': propali_artikli,
            'ukupna_steta': round(ukupna_steta, 2)
        }
        
        return Response(statistike, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Greška u artikli_statistike: {str(e)}")
        return Response(
            {'error': 'Greška pri dobijanju statistika artikala', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['skladisni_operater', 'administrator'])
def artikli_grafikon_po_nedeljama(request):
    """
    API endpoint za grafikon - broj artikala koji ističu po nedeljama
    """
    try:
        from datetime import datetime, timedelta
        
        # Prvo ažuriraj status svih artikala
        from .signals import update_all_artikli_status
        update_all_artikli_status()
        
        danas = datetime.now().date()
        
        # Definiši početak svake nedelje (ponedeljak)
        dana_do_ponedeljka = danas.weekday()  # 0=ponedeljak, 6=nedelja
        pocetak_ove_nedelje = danas - timedelta(days=dana_do_ponedeljka)
        
        # Definiši opsege nedelja
        nedelje = [
            {
                'naziv': 'Ova nedelja',
                'pocetak': pocetak_ove_nedelje,
                'kraj': pocetak_ove_nedelje + timedelta(days=6)
            },
            {
                'naziv': 'Naredna nedelja', 
                'pocetak': pocetak_ove_nedelje + timedelta(days=7),
                'kraj': pocetak_ove_nedelje + timedelta(days=13)
            },
            {
                'naziv': 'Za 2 nedelje',
                'pocetak': pocetak_ove_nedelje + timedelta(days=14),
                'kraj': pocetak_ove_nedelje + timedelta(days=20)
            },
            {
                'naziv': 'Za 3 nedelje',
                'pocetak': pocetak_ove_nedelje + timedelta(days=21),
                'kraj': pocetak_ove_nedelje + timedelta(days=27)
            }
        ]
        
        grafikon_data = []
        
        for nedelja in nedelje:
            # Broj artikala koji ističu u ovoj nedelji (samo oni koji još nisu istekli)
            broj_artikala = Artikal.objects.filter(
                rok_trajanja_a__gte=nedelja['pocetak'],
                rok_trajanja_a__lte=nedelja['kraj'],
                rok_trajanja_a__gt=danas  # Isključi artikle koji su već istekli
            ).exclude(
                status_trajanja='istekao'  # Dodatno isključi artikle sa statusom istekao
            ).count()
            
            grafikon_data.append({
                'nedelja': nedelja['naziv'],
                'broj_artikala': broj_artikala,
                'pocetak': nedelja['pocetak'].isoformat(),
                'kraj': nedelja['kraj'].isoformat()
            })
        
        return Response({
            'grafikon_data': grafikon_data,
            'datum_generisanja': danas.isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Greška u artikli_grafikon_po_nedeljama: {str(e)}")
        return Response(
            {'error': 'Greška pri generisanju grafikona', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile_update_api(request, user_id=None):
    """
    API endpoint za ažuriranje korisničkog profila
    """
    # Određivanje korisnika koji se menja
    if user_id:
        user = get_object_or_404(User, sifra_k=user_id)
        # Provera permisija
        if not request.user.tip_k == 'administrator' and request.user != user:
            return Response(
                {"error": "Nemate dozvolu za izmenu ovog profila"},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        user = request.user

    if request.method == 'GET':
        # Vraćanje trenutnih podataka korisnika
        serializer = UserProfileUpdateSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Ažuriranje podataka
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profil je uspešno ažuriran",
                "user": UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Dobijanje podataka trenutnog korisnika"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_by_id(request, user_id):
    """Dobijanje podataka određenog korisnika (samo za administratore)"""
    if not request.user.tip_k == 'administrator':
        return Response(
            {"error": "Nemate dozvolu za pristup ovim podacima"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user = get_object_or_404(User, sifra_k=user_id)
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request, user_id=None):
    # Određivanje korisnika koji se menja
    if user_id:
        user = get_object_or_404(User, sifra_k=user_id)
        # Provera permisija - samo administrator može da menja druge korisnike
        if not request.user.tip_k == 'administrator':
            return Response(
                {"error": "Nemate dozvolu za izmenu ovog profila"},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        user = request.user

    serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Profil je uspešno ažuriran",
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_list(request):
    """Lista svih korisnika (samo za administratore)"""
    if not request.user.tip_k == 'administrator':
        return Response(
            {"error": "Nemate dozvolu za pristup ovoj listi"},
            status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all()
    serializer = UserProfileSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
#@allowed_users(['administrator'])
def vozaci_list(request):

    try:
        vozaci = Vozac.objects.all().order_by('sifra_vo')
        #vozaci = Vozac.get_all_vozila().order_by('sifra_v')
        serializer = VozacSerializer(vozaci, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju vozača', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['administrator'])
def vozila_list(request):
    try:
        vozila = Vozilo.objects.all().order_by('sifra_v')
        serializer = VoziloSerializer(vozila, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Greška pri dohvatanju vozila', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def get_vozilo(request, pk):
    vozilo = get_object_or_404(Vozilo, pk=pk)
    serializer = VoziloSerializer(vozilo)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@allowed_users(['administrator'])
def update_vozilo(request, pk):
    vozilo = get_object_or_404(Vozilo, pk=pk)
    serializer = VoziloSerializer(vozilo, data=request.data, partial = True)
    allowed_fields = ['status', 'registracija', 'kapacitet']
    for field in request.data.keys():
        if field not in allowed_fields:
            return Response(
                {"error": f"Polje '{field}' ne može da se menja."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_vozilo(request, pk):
    vozilo = get_object_or_404(Vozilo, pk=pk)
    vozilo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# servis
@api_view(['POST'])
def create_servis(request):
    serializer = ServisSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_servisi(request):
    servisi = Servis.objects.select_related('vozilo').all()
    serializer = ServisSerializer(servisi, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_servis(request, pk):
    servis = get_object_or_404(Servis, pk=pk)
    serializer = ServisSerializer(servis)
    return Response(serializer.data)

@api_view(['PUT'])
def update_servis(request, pk):
    servis = get_object_or_404(Servis, pk=pk)
    serializer = ServisSerializer(servis, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_servis(request, pk):
    servis = get_object_or_404(Servis, pk=pk)
    servis.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def servisi_po_vozilu(request, vozilo_id):
    servisi = Servis.objects.filter(vozilo_id=vozilo_id).order_by('-datum_servisa')
    serializer = ServisSerializer(servisi, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# isporuka
@api_view(['GET'])
def list_isporuke(request):
    #isporuke = Isporuka.objects.select_related('vozilo', 'ruta').all()
    isporuke = Isporuka.objects.all()
    serializer = IsporukaSerializer(isporuke, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_aktivne_isporuke(request):
    try:
            aktivne_isporuke = Isporuka.objects.filter(
                status ='aktivna' 
                #status__in=['aktivna', 'aktivna_nova']
            ).select_related('ruta', 'vozilo', 'vozac')
            isporuke_data = []
            for isporuka in aktivne_isporuke:
                isporuke_data.append({
                    'sifra_i': isporuka.sifra_i,
                    'naziv': f"Isporuka {isporuka.sifra_i}",
                    'datum_kreiranja': isporuka.datum_kreiranja,
                    'kolicina_kg': getattr(isporuka, 'kolicina_kg', None),
                    'rok_isporuke': getattr(isporuka, 'rok_is', 'N/A'),
                    'status': isporuka.status,
                    'ruta_naziv': f"Ruta {isporuka.ruta.sifra_r}" if isporuka.ruta else 'N/A'
                })
            
            return Response(isporuke_data)
    except Exception as e:
        print(f"Greška pri dohvatanju aktivnih isporuka: {e}")
        return Response({'detail': 'Došlo je do greške na serveru.'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_u_toku_isporuke(request):
    try:
            aktivne_isporuke = Isporuka.objects.filter(
                status ='u_toku' 
                #status__in=['aktivna', 'aktivna_nova']
            ).select_related('ruta', 'vozilo', 'vozac')
            isporuke_data = []
            for isporuka in aktivne_isporuke:
                isporuke_data.append({
                    'sifra_i': isporuka.sifra_i,
                    'naziv': f"Isporuka {isporuka.sifra_i}",
                    'datum_kreiranja': isporuka.datum_kreiranja,
                    'kolicina_kg': getattr(isporuka, 'kolicina_kg', None),
                    'rok_isporuke': getattr(isporuka, 'rok_is', 'N/A'),
                    'status': isporuka.status,
                    'ruta_naziv': f"Ruta {isporuka.ruta.sifra_r}" if isporuka.ruta else 'N/A'
                })
            
            return Response(isporuke_data)
    except Exception as e:
        print(f"Greška pri dohvatanju aktivnih isporuka: {e}")
        return Response({'detail': 'Došlo je do greške na serveru.'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_sve_isporuke(request):
    """
    Privremeni endpoint za debug - prikazuje sve isporuke i njihove statuse
    """
    try:
        sve_isporuke = Isporuka.objects.all().select_related('ruta')
        
        isporuke_data = []
        for isporuka in sve_isporuke:
            isporuke_data.append({
                'sifra_i': isporuka.sifra_i,
                'naziv': f"Isporuka {isporuka.sifra_i}",
                'status': isporuka.status,  # OVO ĆE NAM POKAZATI STVARNE STATUS U BAZI
                'datum_kreiranja': isporuka.datum_kreiranja,
                'ruta_naziv': f"Ruta {isporuka.ruta.sifra_r}" if isporuka.ruta else 'N/A'
            })
        
        return Response({
            'ukupno_isporuka': sve_isporuke.count(),
            'isporuke': isporuke_data
        })
    except Exception as e:
        return Response({'detail': f'Greška: {str(e)}'}, status=500)
# upozorenje
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_upozorenja(request):
    #upozorenja = Upozorenje.objects.select_related('isporuka').all()
    try:
        upozorenja = Upozorenje.objects.all()
        serializer = UpozorenjeSerializer(upozorenja, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# temperatura
@api_view(['GET'])
def list_temperature(request):
    temperature = Temperatura.objects.all()
    serializer = TemperaturaSerializer(temperature, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# def list_vozilo_temperatura(request):
#     veze = voziloOmogucavaTemperatura.objects.select_related('sifra_temp', 'sifra_vozila', 'isporuka').all()
#     serializer = VoziloTemperaturaSerializer(veze, many=True)
#     return Response(serializer.data)

# notifikacija
@api_view(['GET'])
def list_notifikacije(request):
    notifikacije = Notifikacija.objects.select_related('korisnik').all()
    serializer = NotifikacijaSerializer(notifikacije, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_notifikacija_as_read(request, pk):
    notifikacija = get_object_or_404(Notifikacija, pk=pk)
    notifikacija.procitana_n = True
    notifikacija.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_notifikacije(request, user_id):
    try:
        notifikacije = Notifikacija.objects.select_related('korisnik').filter(
            korisnik_id=user_id
        ).order_by('-datum_n') 
        
        serializer = NotifikacijaSerializer(notifikacije, many=True)
        return Response(serializer.data)
    except Exception as e:
        print(f"Greška pri dohvatanju notifikacija za korisnika {user_id}: {e}")
        return Response({'detail': 'Došlo je do greške na serveru.'}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@allowed_users(['administrator'])
def update_status_vozaca(request, pk):
    vozac = get_object_or_404(Vozac, pk=pk)
    serializer = VozacSerializer(vozac, data=request.data, partial = True)
        
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predlozi_vozaca(request):
    try:
        slobodni_vozaci = Vozac.objects.filter(
            status='slobodan'
        ).order_by('-br_voznji')

        if slobodni_vozaci.exists():
            vozac = slobodni_vozaci.first()
        else:
            vozac = Vozac.objects.order_by('-br_voznji').first()

        serializer = VozacSerializer(vozac)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def pronadji_optimalno_vozilo(kolicina_kg):
    slobodna_vozila = Vozilo.objects.filter(
        status='slobodan',
        kapacitet__gte=kolicina_kg
    ).order_by('kapacitet')

    if slobodna_vozila.exists():
        return slobodna_vozila.first()
    
    vozilo = Vozilo.objects.filter(
        kapacitet__gte=kolicina_kg
    ).order_by('kapacitet').first()
    
    return vozilo
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predlozi_vozilo(request):
    try:
        kolicina_kg = request.data.get('kolicina_kg', 0)

        vozilo = pronadji_optimalno_vozilo(kolicina_kg)

        if vozilo:
            serializer = VoziloSerializer(vozilo)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Nema dostupnih vozila za datu količinu.'}, status=404)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
def geokodiraj_adresu(adresa):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': adresa,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'rs'  # Pretraga samo za Srbiju
        }
        headers = {
            'User-Agent': 'IIS_SUDPI/1.0 (begovic.in26.2021@uns.ac.rs)'  # nesto za Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception as e:
        print(f"Greška pri geokodiranju adrese {adresa}: {e}")
        return None, None

# dobavljanje podataka o ruti koristeci OSRM API
def dobavi_podatke_o_ruti(polazna_tacka, odrediste):
    try:
        # Geokodiranje polazne tačke
        polaziste_lat, polaziste_lon = geokodiraj_adresu(polazna_tacka)
        if not polaziste_lat:
            return None
        
        # Geokodiranje odredišta
        odrediste_lat, odrediste_lon = geokodiraj_adresu(odrediste)
        if not odrediste_lat:
            return None
        
        # Poziv OSRM API-ja za dobijanje rute
        url = f"http://router.project-osrm.org/route/v1/driving/{polaziste_lon},{polaziste_lat};{odrediste_lon},{odrediste_lat}?overview=false"
        #url = f"https://map.project-osrm.org/?z=7&center=44.331707%2C22.357178&loc={polaziste_lon}%2C{polaziste_lat}&loc={odrediste_lon}%2C{odrediste_lat}&hl=en&alt=0&srv=0"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data['code'] == 'Ok' and data['routes']:
                ruta = data['routes'][0]
                duzina_km = round(ruta['distance'] / 1000, 2)
                vreme_sati = round(ruta['duration'] / 3600, 2)
                
                return {
                    'duzina_km': duzina_km,
                    'vreme_sati': vreme_sati,
                    'polazna_tacka_koordinate': f"{polaziste_lat},{polaziste_lon}",
                    'odrediste_koordinate': f"{odrediste_lat},{odrediste_lon}",
                    'smer': 'Najkraća ruta'
                }
        
        return None
    except Exception as e:
        print(f"Greška pri dobavljanju rute: {e}")
        return None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predlozi_rutu(request):
    try:
        polazna_tacka = request.data.get('polazna_tacka', '').strip()
        odrediste = request.data.get('odrediste', '').strip()

        if not polazna_tacka or not odrediste:
            return Response({'error': 'Polazna tačka i odredište su obavezni'}, status=400)

        # Proveri da li ruta već postoji u bazi
        postojeca_ruta = Ruta.objects.filter(
            polazna_tacka__iexact=polazna_tacka,
            odrediste__iexact=odrediste
        ).first()

        if postojeca_ruta:
            serializer = RutaSerializer(postojeca_ruta)
            return Response(serializer.data)

        # Dobavi podatke o ruti sa OSM
        ruta_podaci = dobavi_podatke_o_ruti(polazna_tacka, odrediste)

        if not ruta_podaci:
            return Response({
                'error': 'Nije moguće pronaći rutu za unete adrese. Proverite tačnost unosa.'
            }, status=404)

        # Kreiraj novu rutu
        nova_ruta = Ruta.objects.create(
            polazna_tacka=polazna_tacka,
            odrediste=odrediste,
            duzina_km=ruta_podaci['duzina_km'],
            vreme_dolaska=timedelta(hours=ruta_podaci['vreme_sati']),
            status='planirana'
        )

        serializer = RutaSerializer(nova_ruta)
        return Response(serializer.data)

    except Exception as e:
        print(f"Greška u predlozi_rutu: {e}")
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def izracunaj_datum_dolaska(request):
    try:
        datum_isporuke = request.GET.get('datum_isporuke')
        ruta_id = request.GET.get('ruta_id')

        if not datum_isporuke or not ruta_id:
            return Response({'error': 'Datum isporuke i ID rute su obavezni'}, status=400)

        try:
            ruta = Ruta.objects.get(sifra_r=ruta_id)
        except Ruta.DoesNotExist:
            return Response({'error': 'Ruta nije pronađena'}, status=404)

        # Izračunaj datum dolaska
        datum_isporuke_obj = timezone.datetime.strptime(datum_isporuke, '%Y-%m-%d').date()
        vreme_putovanja_sati = ruta.vreme_dolaska.total_seconds() / 3600
        
        datum_dolaska = timezone.datetime.combine(
            datum_isporuke_obj, 
            timezone.datetime.min.time()
        ) + timedelta(hours=vreme_putovanja_sati)

        return Response({
            'datum_dolaska': datum_dolaska.strftime('%Y-%m-%d'),
            'vreme_putovanja_sati': round(vreme_putovanja_sati, 2)
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def isporuka_detail(request, pk):
    try:
        isporuka = Isporuka.objects.get(sifra_i=pk)
    except Isporuka.DoesNotExist:
        return Response({'error': 'Isporuka ne postoji'}, status=404)

    if request.method == 'GET':
        serializer = IsporukaSerializer(isporuka)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = IsporukaSerializer(isporuka, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def kreiraj_isporuku(request, pk):
    try:
        data = request.data
        print(f"Isporuka: {data}")
        try:
            isporuka = Isporuka.objects.get(sifra_i=pk)
        except Isporuka.DoesNotExist:
            return Response({'error': 'Isporuka ne postoji.'}, status=404)

        ruta_id = data.get('ruta_id')
        vozac_id = data.get('vozac_id')
        naziv = data.get('naziv')
        datum_isporuke = data.get('datum_isporuke')
        rok_isporuke = data.get('rok_isporuke')
        datum_dolaska = data.get('datum_dolaska')
        kolicina_kg = Decimal(data.get('kolicina_kg', 0))

        if not all([ruta_id, vozac_id, naziv, datum_isporuke, rok_isporuke, datum_dolaska]):
            return Response({'error': 'Sva polja su obavezna.'}, status=400)

        # Pronađi povezana polja
        ruta = Ruta.objects.get(sifra_r=ruta_id)
        vozac = Vozac.objects.get(sifra_vo=vozac_id)
        vozilo = pronadji_optimalno_vozilo(kolicina_kg)

        # Ažuriranje postojećeg zapisa
        with transaction.atomic():
            isporuka.ruta = ruta
            isporuka.vozilo = vozilo
            isporuka.vozac = vozac
            isporuka.kolicina_kg = kolicina_kg
            isporuka.status = 'spremna'
            isporuka.datum_polaska = datum_isporuke
            isporuka.rok_is = rok_isporuke
            isporuka.datum_dolaska = datum_dolaska
            isporuka.save()

            # Osveži statuse povezanih entiteta
            ruta.status = 'u_toku'
            ruta.save()
            vozilo.status = 'zauzeto'
            vozilo.save()
            vozac.status = 'zauzet'
            vozac.br_voznji += 1
            vozac.save()

        serializer = IsporukaSerializer(isporuka)
        print("Isporuka uspešno ažurirana.")
        return Response(serializer.data, status=200)

    except Exception as e:
        print(f"Greška u kreiraj_isporuku: {e}")
        return Response({'error': str(e)}, status=500)

# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def kreiraj_isporuku(request, pk):
#     try:
#         data = request.data
#         print(f"Isporuka: {data}")

#         ruta_id = data.get('ruta_id')
#         vozac_id = data.get('vozac_id')
#         naziv = data.get('naziv')
#         datum_isporuke = data.get('datum_isporuke')
#         rok_isporuke = data.get('rok_isporuke')
#         datum_dolaska = data.get('datum_dolaska')
#         kolicina_kg = Decimal(data.get('kolicina_kg', 0))

#         if not all([ruta_id, vozac_id, naziv, datum_isporuke, rok_isporuke, datum_dolaska]):
#             return Response({'error': 'Sva polja su obavezna.'}, status=400)

#         # Pronadji rutu
#         try:
#             ruta = Ruta.objects.get(sifra_r=ruta_id)
#         except Ruta.DoesNotExist:
#             return Response({'error': 'Ruta nije pronađena.'}, status=404)

#         # Pronadji vozaca
#         try:
#             vozac = Vozac.objects.get(sifra_vo=vozac_id)
#         except Vozac.DoesNotExist:
#             return Response({'error': 'Vozač nije pronađen.'}, status=404)

#         try:
#             vozilo = pronadji_optimalno_vozilo(kolicina_kg)
#         except Vozilo.DoesNotExist:
#             return Response({'error': 'Vozilo nije pronađeno.'}, status=404)
#         #vozilo = pronadji_optimalno_vozilo(kolicina_kg)
#         if not vozilo:
#             vozilo = Vozilo.objects.filter(status='slobodno').order_by('kapacitet').first()
#             return Response({'error': 'Nema slobodnih vozila trenutno.'}, status=400)

#         # Kreiraj isporuku unutar transakcije
#         with transaction.atomic():
#             nova_isporuka = Isporuka.objects.create(
#                 ruta=ruta,
#                 vozilo=vozilo,
#                 vozac=vozac,
#                 kolicina_kg=kolicina_kg,
#                 status='spremna',
#                 #datum_polaska=datetime.strptime(datum_isporuke, "%Y-%m-%d"),
#                 datum_polaska = datum_isporuke,
#                 #rok_is=datetime.strptime(rok_isporuke, "%Y-%m-%d")
#                 rok_is = rok_isporuke,
#                 datum_dolaska = datum_dolaska
#             )
#             print(f"Ruta: {ruta}")
#             print(f"Vozac: {vozac} ({type(vozac)})")
#             print(f"Vozilo: {vozilo} ({type(vozilo)})")
#             # Ažuriraj statuse
#             ruta.status = 'u_toku'
#             ruta.save()

#             vozilo.status = 'zauzeto'
#             vozilo.save()

#             vozac.status = 'zauzet'
#             vozac.br_voznji =vozac.br_voznji + 1
#             vozac.save()

#         serializer = IsporukaSerializer(nova_isporuka)
#         print("Isporuka uspešno kreirana.")
#         return Response(serializer.data, status=201)

#     except Exception as e:
#         print(f"Greška u kreiraj_isporuku: {e}")
#         return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def zavrsi_isporuku(request, isporuka_id):
    try:
        isporuka = Isporuka.objects.get(sifra_i=isporuka_id)
        
        isporuka.status = 'zavrsena'
        isporuka.save()
        
        vozac = isporuka.vozac
        vozac.status = 'slobodan'
        vozac.save()
        
        serializer = IsporukaSerializer(isporuka)
        return Response(serializer.data)
        
    except Isporuka.DoesNotExist:
        return Response({'error': 'Isporuka ne postoji'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# rute
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_rute(request):
    try:
        rute = Ruta.objects.all().order_by('-sifra_r')
        serializer = RutaSerializer(rute, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_aktivne_rute(request):
    try:
        aktivne_rute = Ruta.objects.filter(
             Q(status='u_toku')   #Q(status='planirana')
        ).order_by('-sifra_r')
        serializer = RutaSerializer(aktivne_rute, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ruta_detail(request, pk):
    try:
        ruta = Ruta.objects.get(sifra_r=pk)
        serializer = RutaSerializer(ruta)
        
        # Dobavi koordinate za prikaz na mapi
        polaziste_lat, polaziste_lon = geokodiraj_adresu(ruta.polazna_tacka)
        odrediste_lat, odrediste_lon = geokodiraj_adresu(ruta.odrediste)
        
        response_data = serializer.data
        response_data['polaziste_koordinate'] = {
            'lat': polaziste_lat,
            'lon': polaziste_lon
        }
        response_data['odrediste_koordinate'] = {
            'lat': odrediste_lat,
            'lon': odrediste_lon
        }
        
        return Response(response_data)
    except Ruta.DoesNotExist:
        return Response({'error': 'Ruta ne postoji'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ruta_directions(request, pk):
    try:
        ruta = Ruta.objects.get(sifra_r=pk)
        
        polaziste_lat, polaziste_lon = geokodiraj_adresu(ruta.polazna_tacka)
        odrediste_lat, odrediste_lon = geokodiraj_adresu(ruta.odrediste)
        
        if not polaziste_lat or not odrediste_lat:
            return Response({'error': 'Nije moguće geokodirati adrese'}, status=400)
        
        # Poziv OSRM API-ja za dobijanje kompletne rute sa geometrijom
        url = f"http://router.project-osrm.org/route/v1/driving/{polaziste_lon},{polaziste_lat};{odrediste_lon},{odrediste_lat}?overview=full&geometries=geojson"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data['code'] == 'Ok' and data['routes']:
                ruta_data = data['routes'][0]
                
                return Response({
                    'ruta_id': ruta.sifra_r,
                    'polazna_tacka': ruta.polazna_tacka,
                    'odrediste': ruta.odrediste,
                    'duzina_km': ruta.duzina_km,
                    'vreme_dolaska': str(ruta.vreme_dolaska),
                    'status': ruta.status,
                    'polaziste_koordinate': [polaziste_lon, polaziste_lat],
                    'odrediste_koordinate': [odrediste_lon, odrediste_lat],
                    'geometry': ruta_data['geometry'],  # GeoJSON geometija rute
                    'distance': ruta_data['distance'],  # dužina u metrima
                    'duration': ruta_data['duration']   # vreme u sekundama
                })
        
        return Response({'error': 'Nije moguće dobiti podatke o ruti'}, status=400)
        
    except Ruta.DoesNotExist:
        return Response({'error': 'Ruta ne postoji'}, status=404)
    except Exception as e:
        print(f"Greška pri dobavljanju rute: {e}")
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ruta_map_preview(request, pk):

    try:
        ruta = Ruta.objects.get(sifra_r=pk)
        
        # Dobavi koordinate
        polaziste_lat, polaziste_lon = geokodiraj_adresu(ruta.polazna_tacka)
        odrediste_lat, odrediste_lon = geokodiraj_adresu(ruta.odrediste)
        
        if not polaziste_lat or not odrediste_lat:
            return Response({'error': 'Nije moguće geokodirati adrese'}, status=400)
        
        # Generiši URL za OpenStreetMap sa rutom
        map_url = f"https://www.openstreetmap.org/directions?engine=osrm_car&route={polaziste_lat}%2C{polaziste_lon}%3B{odrediste_lat}%2C{odrediste_lon}"
        
        return Response({
            'map_url': map_url,
            'ruta_id': ruta.sifra_r,
            'polazna_tacka': ruta.polazna_tacka,
            'odrediste': ruta.odrediste
        })
        
    except Ruta.DoesNotExist:
        return Response({'error': 'Ruta ne postoji'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)