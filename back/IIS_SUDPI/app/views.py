import random
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
#from .models import Faktura, User, Dobavljac, Penal, Ugovor, StavkaFakture, Proizvod, Poseta, Reklamacija, KontrolorKvaliteta, FinansijskiAnaliticar, NabavniMenadzer, LogistickiKoordinator, SkladisniOperater, Administrator, Skladiste, Artikal, Zalihe, Popust, Transakcija
import requests
from datetime import timedelta
from django.utils import timezone
from .models import Rampa, TerminUtovara, Ruta, Notifikacija, Isporuka,Temperatura, Upozorenje, Vozilo, Vozac, Servis, Faktura, User, Dobavljac, Penal, StavkaFakture, Proizvod, Poseta, Reklamacija, KontrolorKvaliteta, FinansijskiAnaliticar, NabavniMenadzer, LogistickiKoordinator, SkladisniOperater, Administrator, Skladiste, Artikal, Zalihe, Popust, Transakcija, Izvestaj
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
    NotifikacijaSerializer,
    RampaSerializer,
    TerminUtovaraSerializer
)
from rest_framework import generics, filters
from django.db import transaction
from .decorators import allowed_users
from django.core.mail import send_mail
from django.conf import settings
import logging
import uuid
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate

# Postavi logging
logger = logging.getLogger(__name__)

def index(request):
    html = render_to_string("index.js", {})
    return HttpResponse(html)
    
class LoginView(DjangoLoginView):
    """
    Custom login view for the application
    """
    template_name = 'app/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Determine where to redirect user after login based on user type"""
        user = self.request.user
        if user.tip_k == 'finansijski_analiticar':
            return reverse_lazy('dashboard_finansijski_analiticar')
        elif user.tip_k == 'kontrolor_kvaliteta':
            return reverse_lazy('visits-list')
        elif user.tip_k == 'nabavni_menadzer':
            return reverse_lazy('dobavljaci-list')
        elif user.tip_k == 'skladisni_operater':
            return reverse_lazy('artikli-list')
        elif user.tip_k == 'administrator':
            return reverse_lazy('admin:index')
        return reverse_lazy('index')

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
def api_login(request):
    """
    API endpoint za login koji vraća JWT token (bez CSRF zaštite)
    """
    email = request.data.get('mail_k')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'detail': 'Email i password su obavezni.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
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
        return Response({
            'detail': 'Neispravna email adresa ili lozinka.'
        }, status=status.HTTP_401_UNAUTHORIZED)

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


# ========== SIMULACIJA PLAĆANJA - HELPER FUNKCIJE ==========

def send_payment_notification(dobavljac_email, faktura):
    """
    Slanje email notifikacije dobavljaču o pokretanju plaćanja
    """
    try:
        subject = f"Notifikacija: Pokrenuto plaćanje za fakturu {faktura.sifra_f}"
        message = f"""
        Poštovani,
        
        Obaveštavamo Vas da je pokrenuto plaćanje za sledeću fakturu:
        
        Broj fakture: {faktura.sifra_f}
        Iznos: {faktura.iznos_f} RSD
        Datum prijema: {faktura.datum_prijema_f}
        Rok plaćanja: {faktura.rok_placanja_f}
        
        Transakcija je u toku. Dobićete potvrdu nakon uspešne isplate.
        
        Srdačan pozdrav,
        Sistem za upravljanje nabavkom
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [dobavljac_email],
            fail_silently=False,
        )
        logger.info(f"Email notifikacija poslata na {dobavljac_email} za fakturu {faktura.sifra_f}")
        return True
    except Exception as e:
        logger.error(f"Greška pri slanju email notifikacije: {str(e)}")
        return False


def send_confirmation_notification(dobavljac_email, transakcija, faktura):
    """
    Slanje email potvrde o uspešnoj transakciji
    """
    try:
        subject = f"Potvrda plaćanja: Faktura {faktura.sifra_f}"
        message = f"""
        Poštovani,
        
        Plaćanje je uspešno izvršeno!
        
        Detalji transakcije:
        - Broj potvrde: {transakcija.potvrda_t}
        - Faktura: {faktura.sifra_f}
        - Iznos: {faktura.iznos_f} RSD
        - Datum transakcije: {transakcija.datum_t.strftime('%d.%m.%Y %H:%M')}
        - Status: {transakcija.get_status_t_display()}
        
        Sredstva su uspešno preneta na Vaš račun.
        
        Srdačan pozdrav,
        Sistem za upravljanje nabavkom
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [dobavljac_email],
            fail_silently=False,
        )
        logger.info(f"Email potvrde poslat na {dobavljac_email} za transakciju {transakcija.potvrda_t}")
        return True
    except Exception as e:
        logger.error(f"Greška pri slanju email potvrde: {str(e)}")
        return False

def send_penalty_notification(dobavljac_email, penal, ugovor, razlog_detalji=""):
    """
    Slanje email notifikacije dobavljaču o kršenju ugovora i dodeljenom penalu
    """
    try:
        subject = f"OBAVEŠTENJE: Kršenje ugovora {ugovor.sifra_u} - Dodeljen penal"
        message = f"""
        Poštovani,
        
        Obaveštavamo Vas da je evidentirano kršenje uslova ugovora, te je na osnovu toga dodeljen penal.
        
        ═══════════════════════════════════════════════
        DETALJI UGOVORA:
        ═══════════════════════════════════════════════
        - Broj ugovora: {ugovor.sifra_u}
        - Datum potpisa: {ugovor.datum_potpisa_u.strftime('%d.%m.%Y')}
        - Datum isteka: {ugovor.datum_isteka_u.strftime('%d.%m.%Y')}
        - Status ugovora: {ugovor.get_status_u_display()}
        
        ═══════════════════════════════════════════════
        DETALJI PENALA:
        ═══════════════════════════════════════════════
        - Broj penala: {penal.sifra_p}
        - Razlog: {penal.razlog_p}
        - Iznos penala: {penal.iznos_p} RSD
        - Datum evidentiranja: {penal.datum_p.strftime('%d.%m.%Y')}
        
        {razlog_detalji}
        
        ═══════════════════════════════════════════════
        SLEDEĆI KORACI:
        ═══════════════════════════════════════════════
        1. Iznos penala će biti odbijen od naredne isplate
        2. Molimo Vas da preduzmete mere kako bi se ovakve situacije izbegavale u budućnosti
        3. Za dodatna pitanja ili žalbe, kontaktirajte našeg nabavnog menadžera
        
        NAPOMENA: Učestala kršenja ugovora mogu dovesti do prekida poslovne saradnje.
        
        Srdačan pozdrav,
        Sistem za upravljanje nabavkom
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [dobavljac_email],
            fail_silently=False,
        )
        logger.info(f"Email o penalu poslat na {dobavljac_email} za ugovor {ugovor.sifra_u}, penal {penal.sifra_p}")
        return True
    except Exception as e:
        logger.error(f"Greška pri slanju email obaveštenja o penalu: {str(e)}")
        return False


def check_contract_violations():
    """
    Proverava sve aktivne ugovore i detektuje kršenja od strane dobavljača:
    - Istekli ugovori koji nisu označeni kao istekli (administrativna greška)
    
    Returns:
        list: Lista dictionary-ja sa detaljima o prekršajima
    """
    violations = []
    danas = date.today()
    
    try:
        # 1. PROVERA: Aktivni ugovori koji su istekli
        istekli_ugovori = Ugovor.objects.filter(
            status_u='aktivan',
            datum_isteka_u__lt=danas
        ).select_related('dobavljac')
        
        for ugovor in istekli_ugovori:
            violations.append({
                'ugovor': ugovor,
                'tip_krsenja': 'istek_ugovora',
                'razlog': f'Ugovor je istekao {ugovor.datum_isteka_u.strftime("%d.%m.%Y")}, ali nije zatvoren',
                'iznos_penala': Decimal('5000.00'),  # Fiksni penal za neažurirane ugovore
                'detalji': f'Ugovor br. {ugovor.sifra_u} je trebao biti zatvoren pre {(danas - ugovor.datum_isteka_u).days} dana.'
            })
        
        logger.info(f"Provera kršenja ugovora završena. Pronađeno {len(violations)} kršenja.")
        return violations
        
    except Exception as e:
        logger.error(f"Greška pri proveri kršenja ugovora: {str(e)}")
        return []


def auto_create_penalty(violation_data):
    """
    Automatski kreira penal za dato kršenje i šalje email obaveštenje dobavljaču
    
    Args:
        violation_data: Dictionary sa podacima o kršenju (iz check_contract_violations)
        
    Returns:
        tuple: (success: bool, penal: Penal or None, error_message: str or None)
    """
    try:
        ugovor = violation_data['ugovor']
        dobavljac = ugovor.dobavljac
        
        # Kreiraj penal
        with transaction.atomic():
            from django.db.models import Max
            max_penal_id = Penal.objects.aggregate(Max('sifra_p'))['sifra_p__max'] or 0
            next_penal_id = max_penal_id + 1
            
            penal = Penal.objects.create(
                sifra_p=next_penal_id,
                razlog_p=violation_data['razlog'],
                iznos_p=violation_data['iznos_penala'],
                ugovor=ugovor
            )
            
            # Ako je kršenje 'istek_ugovora', ažuriraj status ugovora
            if violation_data['tip_krsenja'] == 'istek_ugovora':
                ugovor.status_u = 'istekao'
                ugovor.save()
            
            logger.info(f"Automatski kreiran penal {penal.sifra_p} za ugovor {ugovor.sifra_u}")
        
        # Pošalji email obaveštenje dobavljaču
        email_sent = send_penalty_notification(
            dobavljac_email=dobavljac.email,
            penal=penal,
            ugovor=ugovor,
            razlog_detalji=f"\n{violation_data.get('detalji', '')}\n"
        )
        
        if email_sent:
            logger.info(f"Email obaveštenje uspešno poslato za penal {penal.sifra_p}")
        else:
            logger.warning(f"Email obaveštenje nije poslato za penal {penal.sifra_p}")
        
        return True, penal, None
        
    except Exception as e:
        error_msg = f"Greška pri automatskom kreiranju penala: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['nabavni_menadzer', 'finansijski_analiticar', 'administrator'])
def check_and_create_penalties(request):
    """
    API endpoint za automatsku proveru kršenja ugovora i kreiranje penala
    
    Ova funkcija:
    1. Proverava sve aktivne ugovore i detektuje kršenja
    2. Automatski kreira penale za svako kršenje
    3. Šalje email obaveštenja dobavljačima
    
    Može se pozvati ručno ili automatski (npr. putem schedulera)
    
    Returns:
        JSON sa detaljima o kreiranim penalima i greškama
    """
    try:
        # Proveri kršenja ugovora
        violations = check_contract_violations()
        
        if not violations:
            return Response({
                'message': 'Nije pronađeno nijedno kršenje ugovora',
                'violations_found': 0,
                'penalties_created': 0,
                'errors': []
            }, status=status.HTTP_200_OK)
        
        # Kreiraj penale za svako kršenje
        created_penalties = []
        errors = []
        
        for violation in violations:
            success, penal, error_msg = auto_create_penalty(violation)
            
            if success:
                created_penalties.append({
                    'penal_id': penal.sifra_p,
                    'ugovor_id': violation['ugovor'].sifra_u,
                    'dobavljac': violation['ugovor'].dobavljac.naziv,
                    'tip_krsenja': violation['tip_krsenja'],
                    'iznos': float(violation['iznos_penala']),
                    'razlog': violation['razlog']
                })
            else:
                errors.append({
                    'ugovor_id': violation['ugovor'].sifra_u,
                    'dobavljac': violation['ugovor'].dobavljac.naziv,
                    'error': error_msg
                })
        
        # Pripremi odgovor
        response_data = {
            'message': f'Provera završena. Kreirano {len(created_penalties)} penala.',
            'violations_found': len(violations),
            'penalties_created': len(created_penalties),
            'penalties': created_penalties,
            'errors': errors
        }
        
        # Loguj rezultat
        logger.info(f"Automatska provera penala: {len(violations)} kršenja, {len(created_penalties)} penala kreirano")
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Greška pri automatskoj proveri i kreiranju penala: {str(e)}")
        return Response({
            'error': 'Greška pri proveri kršenja ugovora',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['nabavni_menadzer', 'finansijski_analiticar', 'administrator'])
def preview_contract_violations(request):
    """
    API endpoint za pregled kršenja ugovora BEZ kreiranja penala
    
    Koristi se za pregled šta bi se desilo kada se pozove check_and_create_penalties
    
    Returns:
        JSON sa listom pronađenih kršenja
    """
    try:
        violations = check_contract_violations()
        
        violations_data = []
        for violation in violations:
            violations_data.append({
                'ugovor_id': violation['ugovor'].sifra_u,
                'dobavljac': violation['ugovor'].dobavljac.naziv,
                'dobavljac_email': violation['ugovor'].dobavljac.email,
                'tip_krsenja': violation['tip_krsenja'],
                'razlog': violation['razlog'],
                'iznos_penala': float(violation['iznos_penala']),
                'detalji': violation['detalji'],
                'datum_potpisa': violation['ugovor'].datum_potpisa_u.strftime('%d.%m.%Y'),
                'datum_isteka': violation['ugovor'].datum_isteka_u.strftime('%d.%m.%Y'),
                'status_ugovora': violation['ugovor'].status_u
            })
        
        return Response({
            'message': f'Pronađeno {len(violations)} kršenja ugovora',
            'violations_count': len(violations),
            'violations': violations_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Greška pri pregledu kršenja ugovora: {str(e)}")
        return Response({
            'error': 'Greška pri pregledu kršenja ugovora',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_transaction(faktura):
    """
    Kreiranje transakcije za fakturu - automatsko skidanje sredstava
    Ako transakcija već postoji, ažurira je na 'uspesna' i vraća je
    Takođe ažurira status fakture i briše razlog čekanja
    """
    try:
        # Prvo proveri da li transakcija već postoji
        if hasattr(faktura, 'transakcija') and faktura.transakcija:
            logger.info(f"Transakcija već postoji za fakturu {faktura.sifra_f}, ažuriram status")
            
            # ← AŽURIRAJ STATUS postojeće transakcije na 'uspesna'
            postojeca_transakcija = faktura.transakcija
            if postojeca_transakcija.status_t != 'uspesna':
                postojeca_transakcija.status_t = 'uspesna'
                postojeca_transakcija.datum_t = timezone.now()  # Ažuriraj i datum
                postojeca_transakcija.save()
                logger.info(f"Status transakcije {postojeca_transakcija.potvrda_t} promenjen na 'uspesna'")
            
            # ← AŽURIRAJ FAKTURU: status i obriši razlog čekanja
            if faktura.status_f != 'isplacena' or faktura.razlog_cekanja_f is not None:
                faktura.status_f = 'isplacena'
                faktura.razlog_cekanja_f = None  # Obriši razlog čekanja
                faktura.save()
                logger.info(f"Faktura {faktura.sifra_f}: status = 'isplacena', razlog_cekanja = None")
            
            return postojeca_transakcija
        
        # Dobavi maksimalnu sifra_t i dodaj 1
        from django.db.models import Max
        max_sifra = Transakcija.objects.aggregate(Max('sifra_t'))['sifra_t__max']
        nova_sifra = (max_sifra or 0) + 1
        
        # Generisanje jedinstvenog broja potvrde
        potvrda_broj = f"TRX-{uuid.uuid4().hex[:12].upper()}"
        
        # Proveri da li potvrda_broj već postoji (dupla provera)
        while Transakcija.objects.filter(potvrda_t=potvrda_broj).exists():
            potvrda_broj = f"TRX-{uuid.uuid4().hex[:12].upper()}"
        
        # Kreiranje nove transakcije sa eksplicitnim ID-om
        transakcija = Transakcija.objects.create(
            sifra_t=nova_sifra,
            faktura=faktura,
            potvrda_t=potvrda_broj,
            status_t='uspesna',
            datum_t=timezone.now()
        )
        
        logger.info(f"Transakcija {potvrda_broj} (ID: {nova_sifra}) kreirana za fakturu {faktura.sifra_f}")
        return transakcija
    except Exception as e:
        logger.error(f"Greška pri kreiranju transakcije: {str(e)}")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def simulate_payment(request, invoice_id):
    """
    API endpoint za simulaciju plaćanja sa notifikacijama i automatskim skidanjem sredstava
    
    Tok simulacije:
    1. Slanje notifikacije dobavljaču o pokretanju plaćanja
    2. Automatsko skidanje sredstava (kreiranje transakcije)
    3. Ažuriranje statusa fakture na 'isplacena'
    4. Slanje potvrde transakcije dobavljaču
    """
    try:
        # Pronalaženje fakture
        faktura = get_object_or_404(Faktura, sifra_f=invoice_id)
        
        # Provera da li je faktura u odgovarajućem statusu
        if faktura.status_f == 'isplacena':
            # Ako je već isplaćena i ima transakciju, vrati podatke postojeće transakcije
            if hasattr(faktura, 'transakcija') and faktura.transakcija:
                transakcija = faktura.transakcija
                return Response({
                    'success': True,
                    'message': 'Faktura je već isplaćena',
                    'transaction': {
                        'id': transakcija.sifra_t,
                        'confirmation_number': transakcija.potvrda_t,
                        'status': transakcija.get_status_t_display(),
                        'date': transakcija.datum_t.isoformat(),
                        'amount': float(faktura.iznos_f)
                    },
                    'invoice': {
                        'id': faktura.sifra_f,
                        'new_status': faktura.get_status_f_display(),
                        'supplier': faktura.ugovor.dobavljac.naziv
                    },
                    'notifications': {
                        'payment_notification_sent': False,
                        'confirmation_sent': False,
                        'recipient': faktura.ugovor.dobavljac.email
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Faktura je već isplaćena ali nema povezanu transakciju',
                    'current_status': faktura.status_f
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if faktura.status_f == 'odbijena':
            return Response({
                'error': 'Ne možete izvršiti plaćanje odbijene fakture',
                'current_status': faktura.status_f
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Dobavljač povezan sa fakturom
        dobavljac = faktura.ugovor.dobavljac
        dobavljac_email = dobavljac.email if hasattr(dobavljac, 'email') and dobavljac.email else 'noreply@example.com'
        
        # Koristi transakciju za atomarnost
        with transaction.atomic():
            # KORAK 1: Slanje notifikacije o pokretanju plaćanja
            notification_sent = send_payment_notification(dobavljac_email, faktura)
            
            # KORAK 2: Kreiranje transakcije (automatsko skidanje sredstava)
            transakcija = create_transaction(faktura)
            
            # KORAK 3: Ažuriranje statusa fakture
            faktura.status_f = 'isplacena'
            faktura.razlog_cekanja_f = None  # Očisti razlog čekanja ako postoji
            faktura.save()
            
            # KORAK 4: Slanje potvrde transakcije
            confirmation_sent = send_confirmation_notification(dobavljac_email, transakcija, faktura)
        
        # Priprema odgovora
        response_data = {
            'success': True,
            'message': 'Plaćanje uspešno izvršeno',
            'transaction': {
                'id': transakcija.sifra_t,
                'confirmation_number': transakcija.potvrda_t,
                'status': transakcija.get_status_t_display(),
                'date': transakcija.datum_t.isoformat(),
                'amount': float(faktura.iznos_f)
            },
            'invoice': {
                'id': faktura.sifra_f,
                'new_status': faktura.get_status_f_display(),
                'supplier': dobavljac.naziv
            },
            'notifications': {
                'payment_notification_sent': notification_sent,
                'confirmation_sent': confirmation_sent,
                'recipient': dobavljac_email
            }
        }
        
        logger.info(f"Simulacija plaćanja uspešna za fakturu {invoice_id}, transakcija {transakcija.potvrda_t}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Faktura.DoesNotExist:
        return Response({
            'error': 'Faktura nije pronađena'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Greška pri simulaciji plaćanja: {str(e)}")
        return Response({
            'error': 'Greška pri izvršavanju plaćanja',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


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
            nova_kolicina = request.data['trenutna_kolicina_a']
            # Validacija količine
            if nova_kolicina is None or nova_kolicina < 0:
                return Response(
                    {'error': 'Količina mora biti pozitivna vrednost'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            zaliha.trenutna_kolicina_a = nova_kolicina
        
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
        try:
            zaliha.full_clean()
            zaliha.save()
        except Exception as validation_error:
            return Response(
                {'error': f'Greška validacije: {str(validation_error)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        import traceback
        traceback.print_exc()
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
                    'datum_polaska': getattr(isporuka, 'datum_polaska', 'N/A'),
                    'status': isporuka.status,
                    'ruta_naziv': f"Ruta {isporuka.ruta.sifra_r}" if isporuka.ruta else 'N/A',
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

@api_view(['GET'])
def upozorenja_detail(request, pk):
    upozorenje = get_object_or_404(Upozorenje, pk=pk)
    serializer = UpozorenjeSerializer(upozorenje)
    return Response(serializer.data)

@api_view(['POST'])
def upozorenja_create(request):
    serializer = UpozorenjeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def upozorenja_update(request, pk):
    upozorenje = get_object_or_404(Upozorenje, pk=pk)
    serializer = UpozorenjeSerializer(upozorenje, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

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
def posalji_notifikaciju(korisnik, poruka, link=None):
    Notifikacija.objects.create(
        korisnik=korisnik,
        poruka_n=poruka,
        link_n=link,
        procitana_n=False,
        datum_n=timezone.now()
    )

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
            #serializer.save()
            serializer.update(isporuka, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

def datetime(*args, **kwargs):
    raise NotImplementedError

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

        #ruta_id = data.get('ruta_id')
        #vozac_id = data.get('vozac_id')
        naziv = data.get('naziv')
        datum_isporuke = data.get('datum_isporuke')
        rok_isporuke = data.get('rok_isporuke')
        datum_dolaska = data.get('datum_dolaska')
        #kolicina_kg = Decimal(data.get('kolicina_kg'))

        if not all([naziv, datum_isporuke, rok_isporuke, datum_dolaska]):
            return Response({'error': 'Sva polja su obavezna.'}, status=400)

        # Pronađi povezana polja
        #ruta = Ruta.objects.get(sifra_r=ruta_id)
        #vozac = Vozac.objects.get(sifra_vo=vozac_id)
        #vozilo = pronadji_optimalno_vozilo(kolicina_kg)

        # Ažuriranje postojećeg zapisa
        with transaction.atomic():
            #isporuka.ruta = ruta
            #isporuka.vozilo = vozilo
            #isporuka.vozac = vozac
            #isporuka.kolicina_kg = kolicina_kg
            isporuka.status = 'u_toku'
            isporuka.datum_polaska = datum_isporuke
            isporuka.rok_is = rok_isporuke
            isporuka.datum_dolaska = datum_dolaska
            isporuka.save()

            # Osveži statuse povezanih entiteta
            # ruta.status = 'u_toku'
            # ruta.save()
            # vozilo.status = 'zauzeto'
            # vozilo.save()
            # vozac.status = 'zauzet'
            # vozac.br_voznji += 1
            # vozac.save()
        #datum = datetime(isporuka.datum_polaska).toLocaleDateString()
        posalji_notifikaciju(request.user,
                             f"Nova isporuka {isporuka.sifra_i} je planirana za {isporuka.datum_polaska}."
        )
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
    
# spremanje isporuke
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pronadji_skladiste_preko_isporuke(request, isporuka_id):
    try:
        isporuka = Isporuka.objects.get(sifra_i=isporuka_id)
        ruta = isporuka.ruta
        if not ruta:
            return Response({'error': 'Isporuka nema dodeljenu rutu'}, status=404)
        
        odrediste = ruta.polazna_tacka
        
        skladiste = Skladiste.objects.filter(
            mesto_s__iexact=odrediste
            #mesto_s__in=odrediste
        ).first()
        
        if not skladiste:
            return Response({'error': 'Nije pronađeno skladište za dato odredište'}, status=404)
        
        serializer = SkladisteSerializer(skladiste)
        return Response(serializer.data)
        
    except Isporuka.DoesNotExist:
        return Response({'error': 'Isporuka ne postoji'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rampe_list(request):
    skladiste_id = request.GET.get('skladiste')
    status = request.GET.get('status')
    
    queryset = Rampa.objects.all()
    
    if skladiste_id:
        queryset = queryset.filter(skladiste_id=skladiste_id)
    if status:
        queryset = queryset.filter(status=status)
    
    data = [{
        'sifra_rp': r.sifra_rp,
        'oznaka': r.oznaka,
        'status': r.status,
        'skladiste': r.skladiste.mesto_s
    } for r in queryset]
    
    return Response(data)
def get_vreme_utovara(kolicina_kg):
    if not kolicina_kg:
        raise ValueError("Količina je obavezna za izračunavanje vremena utovara.")
    
    try:
        osnovno_vreme = 0.5  
        dodatak_po_toni = 0.1 
        kolicina_tona = float(kolicina_kg) / 1000
        vreme_utovara = osnovno_vreme + (kolicina_tona * dodatak_po_toni)
        return vreme_utovara
    except ValueError:
        raise ValueError("Količina mora biti broj.")
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def izracunaj_vreme_utovara(request):
    kolicina = request.GET.get('kolicina')
    #vozilo_id = request.GET.get('vozilo')
    
    try:
        vreme_utovara = get_vreme_utovara(kolicina)
        
        return Response({'vreme_utovara': round(vreme_utovara, 2)})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def kreiraj_notifikaciju(request):
    poruka = request.data.get('poruka_n')
    tip = request.data.get('tip')
    
    # prvi korisnik sa tom ulogom
    from django.contrib.auth.models import User
    try:
        koordinator = User.objects.filter(groups__name='Logisticki koordinator').first()
        if koordinator:
            Notifikacija.objects.create(
                poruka_n=poruka,
                korisnik=koordinator,
                link_n='/dashboard'
            )
            return Response({'status': 'Notifikacija poslata'})
        else:
            return Response({'error': 'Koordinator nije pronađen'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_aktivne_rampe(request):
    try:
            skladiste = request.GET.get('skladiste', None)
            aktivne = Rampa.objects.filter(
                status ='slobodna' ,
                skladiste_id=skladiste
                #status__in=['aktivna', 'aktivna_nova']
            ).select_related('skladiste')
            rampe_data = []
            for rampa in aktivne:
                rampe_data.append({
                    'sifra_rp': rampa.sifra_rp,
                    'oznaka': rampa.oznaka,
                    'status': rampa.status,
                    'skladiste_mesto': rampa.skladiste.mesto_s if rampa.skladiste else 'N/A'
                })
            
            
            return Response(rampe_data)
    except Exception as e:
        print(f"Greška pri dohvatanju slobodnih rampi: {e}")
        return Response({'detail': 'Došlo je do greške na serveru.'}, status=500)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_aktivna_rampa(request):
    try:
        # aktivne =  Rampa.objects.filter(
        #     status='slobodna'
        # ).select_related('skladiste')
        skladiste = request.GET.get('skladiste', None)
        aktivne = Rampa.objects.filter(
            status ='slobodna' ,
            skladiste_id=skladiste
            #status__in=['aktivna', 'aktivna_nova']
        ).select_related('skladiste')
        if aktivne.exists():
            rampa = aktivne.first()
        else:
            Upozorenje.objects.create(
                poruka_u="Nema slobodnih rampi u sistemu!",
                datum_u=timezone.now()
            )

        serializer = RampaSerializer(rampa)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from threading import Timer

def zakazi_oslobadjanje_rampe(rampa, vreme_utovara_h):
    sekunde = vreme_utovara_h * 3600
    Timer(sekunde, lambda: rampa.oslobodi()).start()

def azuriraj_status_rampe(isporuka):

    slobodna_rampa = Rampa.objects.filter(status='slobodna').first()
    if not slobodna_rampa:
        return
    vreme_utovara_sati = get_vreme_utovara(isporuka.kolicina_kg)
    slobodna_rampa.zauzmi(vreme_utovara_sati)
    zakazi_oslobadjanje_rampe(slobodna_rampa, vreme_utovara_sati)
    slobodna_rampa.status = 'zauzeta'
    serializer = RampaSerializer(slobodna_rampa)
    TerminUtovara.objects.create(
        isporuka=isporuka,
        rampa=slobodna_rampa,
        vreme_utovara=timezone.now(),
        trajanje_utovara=timedelta(hours=vreme_utovara_sati)
    )

def azuriraj_rutu_vreme_polaska(isporuka):
    if not isporuka.ruta:
        return
    
    ruta = isporuka.ruta
    vreme_utovara_h = get_vreme_utovara(isporuka.kolicina_kg)
    delta_utovara = timedelta(hours=vreme_utovara_h)

    if hasattr(ruta, 'vreme_polaska') and ruta.vreme_polaska:
        ruta.vreme_polaska += delta_utovara
    else:
        ruta.vreme_polaska = timezone.now() + delta_utovara

    ruta.save()
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def spremi_isporuku(request, pk):
    try:
        isporuka = Isporuka.objects.get(sifra_i=pk)
    except Isporuka.DoesNotExist:
        return Response({'error': 'Isporuka ne postoji'}, status=404)
    isporuka.status = 'u_toku'
    serializer = IsporukaSerializer(isporuka, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        azuriraj_status_rampe(isporuka)
        azuriraj_rutu_vreme_polaska(isporuka)

        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def rampa_detail(request, pk):
    try:
        rampa = Rampa.objects.get(sifra_rp=pk)
    except Rampa.DoesNotExist:
        return Response({'error': 'Rampa ne postoji'}, status=404)

    if request.method == 'GET':
        serializer = RampaSerializer(rampa)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RampaSerializer(rampa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def ruta_spremna(request, pk):
    try:
        vremeUtovara = float(request.data.get('vreme_utovara'))
        #isporuka = Isporuka.objects.get(sifra_i=pk)
        ruta = Ruta.objects.get(sifra_r=pk)
        #ruta_id = isporuka.ruta
        #ruta = Ruta.objects.get(sifra_r=ruta_id)
        # Ensure we have a numeric value for hours
        delta = timedelta(hours=vremeUtovara)

        if ruta.vreme_dolaska is None:
            ruta.vreme_dolaska = delta
        else:
            ruta.vreme_dolaska = ruta.vreme_dolaska + delta


        ruta.save()

        serializer = RutaSerializer(ruta)
        return Response(serializer.data)
    except Ruta.DoesNotExist:
        return Response({'error': 'Ruta ne postoji'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
@api_view(['POST'])
@login_required
def generisi_izvestaj(request):
    tip_izvestaja = request.data.get('tip_izvestaja')
    datum = request.data.get('datum')
    selected_upozorenja = request.data.get('selected_upozorenja', [])
    sadrzaj = request.data.get('sadrzaj', '')

    # Kreiraj PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom stilovi
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkgreen,
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.darkgreen,
        spaceAfter=12,
    )
    
    normal_style = styles['Normal']
    
    # Sadržaj PDF-a
    content = []
    
    # Naslov
    content.append(Paragraph("IZVEŠTAJ - LOGISTIČKI SISTEM", title_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Osnovne informacije
    content.append(Paragraph(f"Datum izveštaja: {datum}", normal_style))
    content.append(Paragraph(f"Tip izveštaja: {dict(Izvestaj.TIP_CHOICES).get(tip_izvestaja, tip_izvestaja)}", normal_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Ako postoje odabrana upozorenja
    if selected_upozorenja:
        content.append(Paragraph("Obuhvaćena upozorenja:", heading_style))
        
        upozorenja_data = [['Tip', 'Poruka', 'Vreme', 'Isporuka']]
        for upozorenje_id in selected_upozorenja:
            try:
                upozorenje = Upozorenje.objects.get(sifra_u=upozorenje_id)
                upozorenja_data.append([
                    #upozorenje.get_tip_display(),
                    upozorenje.tip,
                    upozorenje.poruka,
                    upozorenje.vreme.strftime('%d.%m.%Y %H:%M'),
                    str(upozorenje.isporuka)
                ])
            except Upozorenje.DoesNotExist:
                continue
        
        if len(upozorenja_data) > 1:
            table = Table(upozorenja_data, colWidths=[1.5*inch, 3*inch, 1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkgreen),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.green)
            ]))
            content.append(table)
            content.append(Spacer(1, 0.3*inch))
   
    content.append(Paragraph("Dodatne informacije:", heading_style))
    content.append(Paragraph(f"{sadrzaj}", normal_style))
    content.append(Spacer(1, 0.2*inch))
    # Dodatni sadržaj izveštaja
    content.append(Paragraph("Rezime:", heading_style))
    content.append(Paragraph(f"Izveštaj je generisan automatski putem sistema za praćenje logistike. "
                           f"Ukupno obuhvaćenih upozorenja: {len(selected_upozorenja)}.", normal_style))
    
    # Build PDF
    doc.build(content)
    
    # Vrati PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="izvestaj_{datum}.pdf"'
    
    # Sačuvaj izveštaj u bazi
    izvestaj = Izvestaj.objects.create(
        tip_i=tip_izvestaja,
        sadrzaj_i=f"Izveštaj generisan {datum}. Odabrana upozorenja: {selected_upozorenja}",
        kreirao=request.user
    )
    
    return response
