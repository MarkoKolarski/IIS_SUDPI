from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from datetime import timedelta
from django.shortcuts import get_object_or_404
import requests
from .models import Ruta, Notifikacija, Isporuka, Temperatura, Upozorenje, Vozilo, Vozac, Servis, User, Dobavljac, KontrolorKvaliteta, FinansijskiAnaliticar, NabavniMenadzer, LogistickiKoordinator, SkladisniOperater, Administrator, Skladiste, Artikal, Zalihe
from .serializers import (
    RegistrationSerializer,
    DobavljacSerializer,
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
from django.db import transaction
from .decorators import allowed_users
import logging
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy

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
        skladista = Skladiste.objects.all().order_by('sifra_sk')
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
            zalihe = Zalihe.objects.filter(skladiste__sifra_sk=skladiste_filter).select_related(
                'artikal', 'skladiste'
            ).order_by('artikal__naziv_a')
        else:
            # Sve zalihe
            zalihe = Zalihe.objects.all().select_related(
                'artikal', 'skladiste'
            ).order_by('skladiste__mesto_sk', 'artikal__naziv_a')

        # Ručno kreiranje response data sa dodatnim poljima
        zalihe_data = []
        for zaliha in zalihe:
            zalihe_data.append({
                'id': zaliha.id,
                'trenutna_kolicina_a': zaliha.trenutna_kol_z,
                'datum_azuriranja': zaliha.datum_azuriranja_z,
                'artikal_naziv': zaliha.artikal.naziv_a if zaliha.artikal else 'N/A',
                'artikal_sifra': zaliha.artikal.sifra_a if zaliha.artikal else None,
                'skladiste_naziv': zaliha.skladiste.mesto_sk if zaliha.skladiste else 'N/A',
                'skladiste_sifra': zaliha.skladiste.sifra_sk if zaliha.skladiste else None,
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
            'trenutna_kolicina_a': zaliha.trenutna_kol_z,
            'datum_azuriranja': zaliha.datum_azuriranja_z,
            'artikal_naziv': zaliha.artikal.naziv_a if zaliha.artikal else 'N/A',
            'artikal_sifra': zaliha.artikal.sifra_a if zaliha.artikal else None,
            'skladiste_naziv': zaliha.skladiste.mesto_sk if zaliha.skladiste else 'N/A',
            'skladiste_sifra': zaliha.skladiste.sifra_sk if zaliha.skladiste else None,
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
            zaliha.trenutna_kol_z = nova_kolicina

        if 'skladiste' in request.data:
            try:
                skladiste = Skladiste.objects.get(sifra_sk=request.data['skladiste'])
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
            'trenutna_kolicina_a': zaliha.trenutna_kol_z,
            'datum_azuriranja': zaliha.datum_azuriranja_z,
            'artikal_naziv': zaliha.artikal.naziv_a if zaliha.artikal else 'N/A',
            'skladiste_naziv': zaliha.skladiste.mesto_sk if zaliha.skladiste else 'N/A',
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
            status_trajanja_a='istice'
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
        rizicni_artikli = Artikal.objects.filter(status_trajanja_a='istice').count()

        # 3. Broj propali articala (istekli)
        propali_artikli = Artikal.objects.filter(status_trajanja_a='istekao').count()

        # 4. Šteta za propale artikle (osnovna_cena * trenutna_kolicina iz zaliha)
        propali_artikli_data = Artikal.objects.filter(
            status_trajanja_a='istekao'
        ).prefetch_related('zalihe')

        ukupna_steta = 0
        for artikal in propali_artikli_data:
            try:
                # Sumiranje količina iz svih skladišta za ovaj artikal
                ukupna_kolicina = sum([zaliha.trenutna_kol_z for zaliha in artikal.zalihe.all()])
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
                status_trajanja_a='istekao'  # Dodatno isključi artikle sa statusom istekao
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
    notifikacije = Notifikacija.objects.prefetch_related('korisnici').all()
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
        notifikacije = Notifikacija.objects.prefetch_related('korisnici').filter(
            korisnici__sifra_k=user_id
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