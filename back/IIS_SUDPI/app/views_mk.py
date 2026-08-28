"""
View-i podsistema finansijskog analitičara (FA).

Sadrži: kontrolnu tablu, listu/detalje faktura, verifikaciju/odbacivanje,
simulaciju plaćanja, izveštaje, preglede penala i automatsku proveru
kršenja ugovora. JSON odgovori ka frontendu su nepromenjeni; ispod njih:
- Faktura.status_f menja se ISKLJUČIVO preko Faktura.promeni_status(), koja
  upisuje istorijat u PromenaStatusa (razlog čekanja/odbijanja se sada čita
  odatle, ne iz posebne kolone na Fakturi).
- StavkaFakture ide preko ProizvodDobavljaca (kataloška stavka dobavljača),
  ne direktno na Proizvod.
- Kontrolna tabla (bivši Dashboard) i izveštaji upisuju stvarne Metrika/
  Merenje/PredmetIzvestaja redove umesto JSON snapshot-a (Deo D).
"""
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Sum, Q, Count, Avg, Max, Case, When, Value, IntegerField
from django.db.models.functions import TruncMonth
from decimal import Decimal
from datetime import timedelta, date, datetime
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
import logging
import re
import unicodedata
import uuid
from threading import Thread

from django.db import transaction, IntegrityError
from django.core.mail import send_mail, get_connection
from django.conf import settings

from .decorators import allowed_users
from .models import (
    Faktura, Ugovor, Dobavljac, Penal, StavkaFakture, Transakcija,
    KontrolnaTabla, Kreiranje, Metrika, Merenje, JedinicaMere,
    Izvestaj, PredmetIzvestaja, OcenaDobavljaca,
)
from .serializers_mk import (
    FakturaSerializer, FakturaDetailSerializer, PenalSerializer,
)

logger = logging.getLogger(__name__)


def shift_month(month_start, delta):
    """Pomera prvi dan u mesecu za zadati broj meseci (moze i negativan)."""
    month_index = month_start.month - 1 + delta
    year = month_start.year + (month_index // 12)
    month = (month_index % 12) + 1
    return date(year, month, 1)


def get_cost_window(offset=0, limit=6):
    """
    Vraća agregirane troškove po mesecu za prozor od "limit" meseci.
    offset=0 -> tekući + prethodnih (limit-1) meseci,
    offset=1 -> prethodni blok od limit meseci, itd.
    """
    current_month = date.today().replace(day=1)
    newest_month = shift_month(current_month, -(offset * limit))
    oldest_month = shift_month(newest_month, -(limit - 1))
    next_after_newest = shift_month(newest_month, 1)

    monthly_rows = (
        Faktura.objects.filter(
            datum_prijema_f__gte=oldest_month,
            datum_prijema_f__lt=next_after_newest,
            status_f='isplacena'
        )
        .annotate(month=TruncMonth('datum_prijema_f'))
        .values('month')
        .annotate(total=Sum('iznos_f'))
        .order_by('month')
    )

    totals_by_month = {}
    for row in monthly_rows:
        month_value = row['month']
        if hasattr(month_value, 'date'):
            month_value = month_value.date()
        month_key = month_value.replace(day=1)
        totals_by_month[month_key] = float(row['total'] or 0)

    troskovi_po_mesecima = []
    for i in range(limit):
        month_date = shift_month(oldest_month, i)
        troskovi_po_mesecima.append({
            'mesec': month_date.strftime('%m/%Y'),
            'iznos': totals_by_month.get(month_date, 0.0),
        })

    return {
        'offset': offset,
        'limit': limit,
        'window_start': oldest_month.strftime('%m/%Y'),
        'window_end': newest_month.strftime('%m/%Y'),
        'window_start_date': oldest_month,
        'window_end_date': newest_month,
        'vizualizacija_troskova': troskovi_po_mesecima,
    }


def _get_or_create_jedinica_mere(oznaka_jm, naziv_jm, tip_jm):
    jedinica, _ = JedinicaMere.objects.get_or_create(
        oznaka_jm=oznaka_jm,
        defaults={'naziv_jm': naziv_jm, 'tip_jm': tip_jm}
    )
    return jedinica


def _get_or_create_metrika(naziv_m, oznaka_jm, naziv_jm, tip_jm):
    jedinica = _get_or_create_jedinica_mere(oznaka_jm, naziv_jm, tip_jm)
    metrika, _ = Metrika.objects.get_or_create(
        naziv_m=naziv_m,
        defaults={'jedinica_mere': jedinica}
    )
    return metrika


def _get_or_create_kontrolna_tabla(fa):
    """Svaki finansijski analitičar ima tačno jednu ličnu kontrolnu tablu
    (kreira se pri prvom pristupu dashboard-u/izveštajima)."""
    kreiranje = Kreiranje.objects.filter(finansijski_analiticar=fa).select_related('kontrolna_tabla').first()
    if kreiranje:
        return kreiranje.kontrolna_tabla

    tabla = KontrolnaTabla.objects.create(
        naziv_kt=f"Kontrolna tabla - {fa.korisnik.ime_k} {fa.korisnik.prz_k}",
        opis_kt="Automatski kreirana kontrolna tabla finansijskog analitičara.",
    )
    Kreiranje.objects.get_or_create(finansijski_analiticar=fa, kontrolna_tabla=tabla)
    return tabla


def _upisi_merenje(kontrolna_tabla, metrika, vrednost, vreme=None, period_od=None, period_do=None):
    """Servisna funkcija (tačka 8.4 specifikacije): upisuje jedno merenje
    metrike na kontrolnoj tabli. Koristi update_or_create da ponovljeni poziv
    za isti (tabla, metrika, vreme) samo osveži vrednost umesto duplog reda."""
    return Merenje.objects.update_or_create(
        kontrolna_tabla=kontrolna_tabla,
        metrika=metrika,
        vreme_merenja_me=vreme or timezone.now(),
        defaults={
            'vrednost_me': vrednost,
            'period_od_me': period_od,
            'period_do_me': period_do,
        }
    )[0]


def _upisi_ocenu_dobavljaca(dobavljac, kriterijum, vrednost, period_od, period_do):
    """Servisna funkcija (tačka 8.4 specifikacije): obračun/upis ocene
    dobavljača po kriterijumu i periodu (OcenaDobavljaca)."""
    try:
        return OcenaDobavljaca.objects.update_or_create(
            dobavljac=dobavljac,
            kriterijum_od=kriterijum,
            period_od_od=period_od,
            defaults={
                'vrednost_od': vrednost,
                'period_do_od': period_do,
                'datum_ocenj_od': date.today(),
            }
        )[0]
    except Exception as e:
        logger.warning(f"Nije uspelo upisivanje ocene dobavljača {dobavljac.sifra_db}: {str(e)}")
        return None


def _save_dashboard_snapshot(fa, dashboard_data):
    """
    Deo D: kontrolna tabla prestaje da bude mrtva tabela - svaki poziv upisuje
    stvarna Merenje-a za definisane Metrika-e (zamena za stari JSON snapshot).
    Ne utiče na HTTP odgovor - greška ovde se samo loguje.
    """
    try:
        tabla = _get_or_create_kontrolna_tabla(fa)
        sada = timezone.now()
        pf = dashboard_data['pregled_finansija']

        m_placeno = _get_or_create_metrika('Ukupno plaćeno', 'RSD', 'Srpski dinar', 'NOVAC')
        m_cekanje = _get_or_create_metrika('Sredstva na čekanju', 'RSD', 'Srpski dinar', 'NOVAC')
        m_vreme = _get_or_create_metrika('Prosečno vreme plaćanja', 'dan', 'Dan', 'VREME')
        m_broj = _get_or_create_metrika('Broj faktura na čekanju', 'kom', 'Komad', 'KOLICINA')
        m_udeo = _get_or_create_metrika('Udeo sredstava na čekanju', '%', 'Procenat', 'PROCENAT')
        m_mesecni_trosak = _get_or_create_metrika('Mesečni trošak', 'RSD', 'Srpski dinar', 'NOVAC')

        _upisi_merenje(tabla, m_placeno, pf['ukupno_placeno'], vreme=sada)
        _upisi_merenje(tabla, m_cekanje, pf['na_cekanju'], vreme=sada)
        _upisi_merenje(tabla, m_vreme, pf['prosecno_vreme_placanja'], vreme=sada)
        _upisi_merenje(tabla, m_broj, pf['broj_faktura_na_cekanju'], vreme=sada)
        _upisi_merenje(tabla, m_udeo, pf['udeo_na_cekanju'], vreme=sada)

        # Mesečni trošak - jedno Merenje po mesecu iz prozora (period_od/do_me
        # nose taj mesec, vreme_merenja_me je njegov prvi dan).
        for stavka in dashboard_data['vizualizacija_troskova']:
            mesec_str, godina_str = stavka['mesec'].split('/')
            period_od = date(int(godina_str), int(mesec_str), 1)
            period_do = shift_month(period_od, 1) - timedelta(days=1)
            vreme_mesec = timezone.make_aware(datetime.combine(period_od, datetime.min.time()))
            _upisi_merenje(tabla, m_mesecni_trosak, stavka['iznos'], vreme=vreme_mesec, period_od=period_od, period_do=period_do)

        return tabla
    except Exception as e:
        logger.warning(f"Nije uspelo snimanje merenja kontrolne table: {str(e)}")
        return None


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

    broj_faktura_na_cekanju = Faktura.objects.filter(
        status_f__in=['primljena', 'verifikovana']
    ).count()

    isplacene_fakture = Faktura.objects.filter(
        status_f='isplacena'
    ).prefetch_related('transakcije')

    prosecno_vreme = 0
    if isplacene_fakture.exists():
        ukupno_dana = 0
        brojac = 0
        for faktura in isplacene_fakture:
            transakcija = faktura.transakcija
            if transakcija is not None:
                razlika = (transakcija.datum_t.date() - faktura.datum_prijema_f).days
                ukupno_dana += razlika
                brojac += 1
        prosecno_vreme = round(ukupno_dana / brojac) if brojac > 0 else 0

    pregled_finansija = {
        'ukupno_placeno': float(ukupno_placeno),
        'na_cekanju': float(na_cekanju),
        'prosecno_vreme_placanja': prosecno_vreme,
        'broj_faktura_na_cekanju': broj_faktura_na_cekanju,
        'udeo_na_cekanju': round(
            (float(na_cekanju) / float(ukupno_placeno + na_cekanju) * 100)
            if (ukupno_placeno + na_cekanju) > 0
            else 0,
            1
        ),
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
        profitabilnost = (float(dobavljac.ocena_db) * 10) + (aktivni_ugovori * 5) - (penali_count * 15)
        profitabilnost = max(0, min(100, profitabilnost))  # Ograniči na 0-100%

        dobavljaci_profitabilnost.append({
            'name': dobavljac.naziv_db,
            'profitability': f"{profitabilnost:.0f}%"
        })

        # Servisna funkcija (tačka 8.4): upiši ocenu dobavljača za kriterijum
        # BROJ_PENALA za tekući 6-mesečni period (0-10 skala, manje penala = veća ocena).
        _upisi_ocenu_dobavljaca(dobavljac, 'BROJ_PENALA', max(0, 10 - penali_count), pre_6_meseci, date.today())

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
            'supplier': faktura.ugovor.dobavljac.naziv_db,
            'amount': float(faktura.iznos_f)
        })

    # 4. VIZUALIZACIJA TROŠKOVA (tekući prozor od 6 meseci)
    chart_window = get_cost_window(offset=0, limit=6)

    dashboard_data = {
        'pregled_finansija': pregled_finansija,
        'profitabilnost_dobavljaca': dobavljaci_profitabilnost,
        'nadolazece_isplate': nadolazece_isplate,
        'vizualizacija_troskova': chart_window['vizualizacija_troskova'],
        'chart_window': {
            'offset': chart_window['offset'],
            'window_start': chart_window['window_start'],
            'window_end': chart_window['window_end'],
        }
    }

    # Deo D: snimi Merenje-a na kontrolnoj tabli samo kada je pozivalac stvarno FA
    # (NM takođe sme da vidi ovaj ekran, ali 'kreira' veza je FA-specifična u ER-u).
    if getattr(request.user, 'tip_k', None) == 'finansijski_analiticar' and hasattr(request.user, 'finansijski_analiticar'):
        _save_dashboard_snapshot(request.user.finansijski_analiticar, dashboard_data)

    return Response(dashboard_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar', 'nabavni_menadzer'])
def dashboard_finansijski_analiticar_troskovi(request):
    """
    API endpoint za dohvat troškova po mesecima u prozorima.
    Query params:
    - offset: broj prozora unazad (0 = trenutni prozor)
    - limit: broj meseci po prozoru (default 6)
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 6))
    except (TypeError, ValueError):
        return Response({'error': 'Neispravni parametri offset/limit.'}, status=status.HTTP_400_BAD_REQUEST)

    if offset < 0:
        return Response({'error': 'Offset ne može biti negativan.'}, status=status.HTTP_400_BAD_REQUEST)

    if limit < 1 or limit > 24:
        return Response({'error': 'Limit mora biti između 1 i 24.'}, status=status.HTTP_400_BAD_REQUEST)

    window = get_cost_window(offset=offset, limit=limit)
    response_payload = {
        'offset': window['offset'],
        'limit': window['limit'],
        'window_start': window['window_start'],
        'window_end': window['window_end'],
        'vizualizacija_troskova': window['vizualizacija_troskova'],
    }
    return Response(response_payload, status=status.HTTP_200_OK)


def _normalize_search_text(value):
    normalized = unicodedata.normalize('NFKD', value or '')
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch)).lower().strip()


def _parse_search_date(candidate):
    """
    Podržani oblici:
    - dd.mm
    - dd.mm.yyyy
    - yyyy
    """
    raw = (candidate or '').strip()
    if not raw:
        return None

    compact = re.sub(r'\s+', '', raw)
    compact = compact.replace('/', '.').replace('-', '.')

    if re.fullmatch(r'\d{4}', compact):
        year = int(compact)
        if 1900 <= year <= 2100:
            return {'type': 'year', 'year': year}
        return None

    full_match = re.fullmatch(r'(\d{1,2})\.(\d{1,2})\.(\d{4})\.?', compact)
    if full_match:
        day, month, year = map(int, full_match.groups())
        try:
            return {'type': 'exact_date', 'date': date(year, month, day)}
        except ValueError:
            return None

    day_month_match = re.fullmatch(r'(\d{1,2})\.(\d{1,2})\.?', compact)
    if day_month_match:
        day, month = map(int, day_month_match.groups())
        current_year = date.today().year
        try:
            return {'type': 'exact_date', 'date': date(current_year, month, day)}
        except ValueError:
            return None

    return None


def _extract_status_codes(search_query):
    normalized_query = _normalize_search_text(search_query)

    status_aliases = {
        'primljena': ['primljena', 'primljeno', 'ceka verifikaciju'],
        'verifikovana': ['verifikovana', 'verifikovano', 'ceka isplatu'],
        'isplacena': ['isplacena', 'placena', 'placeno'],
        'odbijena': ['odbijena', 'odbijeno', 'odbij'],
    }

    matched_codes = []
    for code, aliases in status_aliases.items():
        if any(alias in normalized_query for alias in aliases):
            matched_codes.append(code)

    return matched_codes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def invoice_list(request):
    """
    API endpoint za prikaz liste faktura sa filtering i search opcijama
    """
    queryset = Faktura.objects.select_related('ugovor__dobavljac').all()

    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'svi':
        queryset = queryset.filter(status_f=status_filter)

    actionable_only = request.GET.get('actionable_only')
    if actionable_only in ('1', 'true', 'True'):
        queryset = queryset.filter(status_f__in=['primljena', 'verifikovana'])

    dobavljac_filter = request.GET.get('dobavljac')
    if dobavljac_filter and dobavljac_filter != 'svi':
        try:
            dobavljac_id = int(dobavljac_filter)
            queryset = queryset.filter(ugovor__dobavljac__sifra_db=dobavljac_id)
        except (ValueError, TypeError):
            pass

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

    search_query = request.GET.get('search', '').strip()
    if search_query:
        search_filters = (
            Q(sifra_f__icontains=search_query) |
            Q(ugovor__dobavljac__naziv_db__icontains=search_query) |
            Q(iznos_f__icontains=search_query)
        )

        matched_status_codes = _extract_status_codes(search_query)
        if matched_status_codes:
            search_filters |= Q(status_f__in=matched_status_codes)

        date_candidates = [search_query]
        date_candidates.extend(token for token in search_query.split() if token)

        for candidate in date_candidates:
            parsed_date = _parse_search_date(candidate)
            if not parsed_date:
                continue

            if parsed_date['type'] == 'year':
                search_filters |= (
                    Q(datum_prijema_f__year=parsed_date['year']) |
                    Q(rok_placanja_f__year=parsed_date['year'])
                )
            elif parsed_date['type'] == 'exact_date':
                search_filters |= (
                    Q(datum_prijema_f=parsed_date['date']) |
                    Q(rok_placanja_f=parsed_date['date'])
                )

        queryset = queryset.filter(search_filters)

    queryset = queryset.annotate(
        status_sort_order=Case(
            When(status_f='primljena', then=Value(0)),
            When(status_f='verifikovana', then=Value(1)),
            When(status_f='odbijena', then=Value(2)),
            When(status_f='isplacena', then=Value(3)),
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by('status_sort_order', '-datum_prijema_f', '-sifra_f')

    page_size = int(request.GET.get('page_size', 10))
    page_number = int(request.GET.get('page', 1))

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)

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
    statusi = [
        {'value': 'svi', 'label': 'Svi statusi'},
        {'value': 'primljena', 'label': 'Čeka verifikaciju'},
        {'value': 'verifikovana', 'label': 'Čeka isplatu'},
        {'value': 'isplacena', 'label': 'Plaćeno'},
        {'value': 'odbijena', 'label': 'Odbačeno'},
    ]

    dobavljaci = Dobavljac.objects.filter(
        ugovori__fakture__isnull=False
    ).distinct().values('sifra_db', 'naziv_db')

    dobavljaci_opcije = [{'value': 'svi', 'label': 'Svi dobavljači'}]
    dobavljaci_opcije.extend([
        {'value': str(d['sifra_db']), 'label': d['naziv_db']}
        for d in dobavljaci
    ])

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
            Faktura.objects.select_related('ugovor__dobavljac').prefetch_related('stavke', 'transakcije'),
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
        faktura = get_object_or_404(Faktura.objects.prefetch_related('transakcije'), sifra_f=invoice_id)
        action = request.data.get('action')

        if action == 'approve':
            if faktura.status_f == 'primljena':
                faktura.promeni_status('verifikovana', request.user)

                return Response({
                    'message': 'Faktura je uspešno verifikovana.',
                    'new_status': faktura.status_f
                }, status=status.HTTP_200_OK)

            if faktura.status_f == 'verifikovana':
                return Response({
                    'detail': 'Za izvršenje isplate koristite simulaciju plaćanja.'
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'detail': f'Akcija approve nije dozvoljena za status {faktura.status_f}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'reject':
            reason = (request.data.get('reason') or '').strip()
            if not reason:
                return Response({
                    'detail': 'Razlog odbacivanja je obavezan.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if faktura.status_f == 'isplacena':
                return Response({
                    'detail': 'Nije moguće odbaciti već isplaćenu fakturu.'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                faktura.promeni_status('odbijena', request.user, razlog=reason)

                transaction_status = None
                postojeca_transakcija = faktura.transakcija
                if postojeca_transakcija is not None:
                    if postojeca_transakcija.status_t != 'uspesna':
                        postojeca_transakcija.status_t = 'neuspesna'
                        postojeca_transakcija.save(update_fields=['status_t'])
                    transaction_status = postojeca_transakcija.status_t

            return Response({
                'message': 'Faktura je odbijena.',
                'new_status': faktura.status_f,
                'transaction_status': transaction_status
            }, status=status.HTTP_200_OK)

        else:
            return Response({'detail': 'Nevalidna akcija.'}, status=status.HTTP_400_BAD_REQUEST)

    except Faktura.DoesNotExist:
        return Response({'detail': 'Faktura nije pronađena.'}, status=status.HTTP_404_NOT_FOUND)


def _save_report_izvestaj(fa, final_response, start_date, end_date, fakture_queryset):
    """
    Deo D: Izvestaj prestaje da bude mrtva tabela - svaki generisani izveštaj
    se upisuje i visi na Kreiranje (FA + kontrolna tabla), a fakture/dobavljači
    koje stvarno obuhvata se beleže kao PredmetIzvestaja redovi (ER: sadržaj
    izveštaja je sada relacioni, ne JSON blob). Ne utiče na HTTP odgovor.
    """
    try:
        tabla = _get_or_create_kontrolna_tabla(fa)
        kreiranje, _ = Kreiranje.objects.get_or_create(finansijski_analiticar=fa, kontrolna_tabla=tabla)

        max_sifra = Izvestaj.objects.aggregate(Max('sifra_i'))['sifra_i__max'] or 0
        izvestaj = Izvestaj.objects.create(
            sifra_i=max_sifra + 1,
            tip_i='FINANSIJSKI',
            period_od_i=start_date,
            period_do_i=end_date,
            kreiranje=kreiranje,
        )

        fakture_ids = list(fakture_queryset.values_list('sifra_f', flat=True)[:200])
        if fakture_ids:
            PredmetIzvestaja.objects.bulk_create([
                PredmetIzvestaja(izvestaj=izvestaj, tip_predmeta_pi='FAKTURA', faktura_id=fid)
                for fid in fakture_ids
            ])

            dobavljac_ids = list(
                Dobavljac.objects.filter(ugovori__fakture__sifra_f__in=fakture_ids)
                .distinct().values_list('sifra_db', flat=True)
            )
            if dobavljac_ids:
                PredmetIzvestaja.objects.bulk_create([
                    PredmetIzvestaja(izvestaj=izvestaj, tip_predmeta_pi='DOBAVLJAC', dobavljac_id=did)
                    for did in dobavljac_ids
                ])
    except Exception as e:
        logger.warning(f"Nije uspelo snimanje izveštaja: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def reports_data(request):
    """
    API endpoint za generiranje izveštaja o troškovima i profitabilnosti
    """
    status_filter = request.GET.get('status', 'sve')
    period_filter = request.GET.get('period', 'sve')
    group_by_filter = request.GET.get('group_by', 'proizvodu')

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

    fakture_queryset = Faktura.objects.all()
    if start_date and end_date:
        fakture_queryset = fakture_queryset.filter(
            datum_prijema_f__gte=start_date,
            datum_prijema_f__lte=end_date
        )

    if status_filter != 'sve':
        fakture_queryset = fakture_queryset.filter(status_f=status_filter)

    stavke_queryset = StavkaFakture.objects.filter(
        faktura__in=fakture_queryset
    ).select_related('faktura', 'proizvod_dobavljaca__proizvod')

    if group_by_filter == 'proizvodu':
        report_data = []

        proizvodi_data = stavke_queryset.values('proizvod_dobavljaca__proizvod__naziv_pr').annotate(
            ukupna_kolicina=Sum('kolicina_sf'),
            ukupan_trosak=Sum('cena_po_jed_sf'),
            broj_stavki=Count('sifra_sf'),
            prosecna_cena=Avg('cena_po_jed_sf')
        ).order_by('-ukupan_trosak')

        chart_profitability = []
        chart_costs = []

        ukupna_kolicina_svi = 0
        ukupan_trosak_svi = Decimal('0.00')
        ukupna_profitabilnost = 0

        for proizvod in proizvodi_data:
            naziv = proizvod['proizvod_dobavljaca__proizvod__naziv_pr'] or 'Nepoznat proizvod'
            kolicina = int(proizvod['ukupna_kolicina'] or 0)
            trosak = proizvod['ukupan_trosak'] or Decimal('0.00')

            if kolicina > 0 and trosak > 0:
                efikasnost = float(trosak) / kolicina
                obim_posla = min(kolicina / 100, 1.0)

                if efikasnost < 500:
                    bazna_profitabilnost = 35 + (obim_posla * 15)
                elif efikasnost < 1500:
                    bazna_profitabilnost = 20 + (obim_posla * 20)
                else:
                    bazna_profitabilnost = 5 + (obim_posla * 15)

                random_factor = (hash(naziv) % 21 - 10) / 10.0
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

            chart_profitability.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': profitabilnost_procenat
            })

            chart_costs.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': float(trosak)
            })

        chart_profitability = chart_profitability[:10]
        chart_costs = chart_costs[:10]

        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': f"{ukupna_kolicina_svi:,} kom",
            'ukupan_trosak': f"{float(ukupan_trosak_svi):,.2f} RSD",
            'profitabilnost': f"+{ukupna_profitabilnost:.0f}%"
        }

    elif group_by_filter == 'dobavljacu':
        report_data = []

        dobavljaci_data = fakture_queryset.values('ugovor__dobavljac__naziv_db').annotate(
            ukupan_trosak=Sum('iznos_f'),
            broj_faktura=Count('sifra_f')
        ).order_by('-ukupan_trosak')

        chart_profitability = []
        chart_costs = []

        ukupna_kolicina_svi = 0
        ukupan_trosak_svi = Decimal('0.00')
        ukupna_profitabilnost = 0

        for dobavljac in dobavljaci_data:
            naziv = dobavljac['ugovor__dobavljac__naziv_db'] or 'Nepoznat dobavljač'
            broj_faktura = dobavljac['broj_faktura'] or 0
            trosak = dobavljac['ukupan_trosak'] or Decimal('0.00')

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

            chart_profitability.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': profitabilnost_procenat
            })

            chart_costs.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': float(trosak)
            })

        chart_profitability = chart_profitability[:10]
        chart_costs = chart_costs[:10]

        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': f"{ukupna_kolicina_svi:,} faktura",
            'ukupan_trosak': f"{float(ukupan_trosak_svi):,.2f} RSD",
            'profitabilnost': f"+{ukupna_profitabilnost:.0f}%"
        }

    elif group_by_filter == 'kategoriji':
        report_data = []

        kategorije_data = stavke_queryset.values('proizvod_dobavljaca__proizvod__kategorija__naziv_kp').annotate(
            ukupna_kolicina=Sum('kolicina_sf'),
            ukupan_trosak=Sum('cena_po_jed_sf'),
            broj_stavki=Count('sifra_sf')
        ).order_by('-ukupan_trosak')

        chart_profitability = []
        chart_costs = []

        ukupna_kolicina_svi = 0
        ukupan_trosak_svi = Decimal('0.00')
        ukupna_profitabilnost = 0

        for kategorija in kategorije_data:
            naziv = kategorija['proizvod_dobavljaca__proizvod__kategorija__naziv_kp'] or 'Nepoznata kategorija'
            kolicina = int(kategorija['ukupna_kolicina'] or 0)
            trosak = kategorija['ukupan_trosak'] or Decimal('0.00')

            if kolicina > 0 and trosak > 0:
                efikasnost = float(trosak) / kolicina
                obim_posla = min(kolicina / 100, 1.0)

                if efikasnost < 500:
                    bazna_profitabilnost = 35 + (obim_posla * 15)
                elif efikasnost < 1500:
                    bazna_profitabilnost = 20 + (obim_posla * 20)
                else:
                    bazna_profitabilnost = 5 + (obim_posla * 15)

                random_factor = (hash(naziv) % 21 - 10) / 10.0
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

            chart_profitability.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': profitabilnost_procenat
            })

            chart_costs.append({
                'label': naziv[:20] + ('...' if len(naziv) > 20 else ''),
                'value': float(trosak)
            })

        chart_profitability = chart_profitability[:10]
        chart_costs = chart_costs[:10]

        total_summary = {
            'proizvod': 'UKUPNO:',
            'kolicina': f"{ukupna_kolicina_svi:,} kom",
            'ukupan_trosak': f"{float(ukupan_trosak_svi):,.2f} RSD",
            'profitabilnost': f"+{ukupna_profitabilnost:.0f}%"
        }

    else:  # fallback za nepoznate opcije
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

    if hasattr(request.user, 'finansijski_analiticar'):
        _save_report_izvestaj(
            request.user.finansijski_analiticar,
            final_response,
            start_date,
            end_date,
            fakture_queryset,
        )

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
    queryset = Penal.objects.select_related('ugovor__dobavljac').all()

    dobavljac_filter = request.GET.get('dobavljac')
    if dobavljac_filter and dobavljac_filter != 'svi':
        try:
            dobavljac_id = int(dobavljac_filter)
            queryset = queryset.filter(ugovor__dobavljac__sifra_db=dobavljac_id)
        except (ValueError, TypeError):
            pass

    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'svi':
        danas = date.today()
        if status_filter == 'resen':
            queryset = queryset.filter(datum_p__lt=danas - timedelta(days=30))
        elif status_filter == 'obavesten':
            queryset = queryset.filter(datum_p__gte=danas - timedelta(days=30))

    queryset = queryset.order_by('-datum_p', '-sifra_p')

    page_size = int(request.GET.get('page_size', 10))
    page_number = int(request.GET.get('page', 1))

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)

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
    statusi = [
        {'value': 'svi', 'label': 'Svi statusi'},
        {'value': 'resen', 'label': 'Rešen'},
        {'value': 'obavesten', 'label': 'Obavešten'},
    ]

    dobavljaci = Dobavljac.objects.filter(
        ugovori__penali__isnull=False
    ).distinct().values('sifra_db', 'naziv_db')

    dobavljaci_opcije = [{'value': 'svi', 'label': 'Svi dobavljači'}]
    dobavljaci_opcije.extend([
        {'value': str(d['sifra_db']), 'label': d['naziv_db']}
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
    dobavljaci_agregati = (
        Dobavljac.objects.filter(ugovori__isnull=False)
        .annotate(
            ukupno_ugovora=Count('ugovori', distinct=True),
            ugovori_sa_penalima=Count(
                'ugovori',
                filter=Q(ugovori__penali__isnull=False),
                distinct=True,
            ),
            broj_penala=Count('ugovori__penali'),
            ukupan_iznos=Sum('ugovori__penali__iznos_p'),
        )
        .filter(broj_penala__gt=0)
        .values(
            'naziv_db',
            'broj_penala',
            'ukupno_ugovora',
            'ugovori_sa_penalima',
            'ukupan_iznos',
        )
    )

    dobavljaci_analiza = []
    for row in dobavljaci_agregati:
        ukupno_ugovora = row['ukupno_ugovora'] or 0
        broj_ugovora_sa_penalima = row['ugovori_sa_penalima'] or 0
        broj_penala = row['broj_penala'] or 0
        ukupan_iznos = row['ukupan_iznos'] or Decimal('0')

        stopa_krsenja = (
            (broj_ugovora_sa_penalima / ukupno_ugovora) * 100
            if ukupno_ugovora > 0 else 0
        )

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
            'naziv': row['naziv_db'],
            'broj_penala': broj_penala,
            'ukupno_ugovora': ukupno_ugovora,
            'ugovori_sa_penalima': broj_ugovora_sa_penalima,
            'ukupan_iznos': float(ukupan_iznos),
            'stopa_krsenja': round(stopa_krsenja, 1),
            'preporuka': preporuka,
            'tip_preporuke': tip_preporuke
        })

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


def send_penalty_notification(dobavljac_email, penal, ugovor, razlog_detalji="", connection=None):
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
            connection=connection,
            fail_silently=False,
        )
        logger.info(f"Email o penalu poslat na {dobavljac_email} za ugovor {ugovor.sifra_u}, penal {penal.sifra_p}")
        return True
    except Exception as e:
        logger.error(f"Greška pri slanju email obaveštenja o penalu: {str(e)}")
        return False


def _dispatch_penalty_notifications_async(email_jobs):
    """
    Asinhrono šalje email obaveštenja kako bi API odgovor bio brz.
    """
    if not email_jobs:
        return

    try:
        penal_ids = [job['penal_id'] for job in email_jobs]
        penali_map = {
            penal.sifra_p: penal
            for penal in Penal.objects.select_related('ugovor__dobavljac').filter(sifra_p__in=penal_ids)
        }

        connection = get_connection(fail_silently=False)
        try:
            connection.open()
            for job in email_jobs:
                penal = penali_map.get(job['penal_id'])
                if penal is None:
                    logger.warning(f"Penal {job['penal_id']} nije pronađen za slanje email obaveštenja")
                    continue

                send_penalty_notification(
                    dobavljac_email=job['dobavljac_email'],
                    penal=penal,
                    ugovor=penal.ugovor,
                    razlog_detalji=job.get('razlog_detalji', ''),
                    connection=connection,
                )
        finally:
            connection.close()
    except Exception as e:
        logger.error(f"Greška pri asinhronom batch slanju emailova o penalima: {str(e)}")


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


def auto_create_penalty(violation_data, send_email=True, email_connection=None, penal_id=None):
    """
    Automatski kreira penal za dato kršenje i šalje email obaveštenje dobavljaču

    Returns:
        tuple: (success: bool, penal: Penal or None, error_message: str or None)
    """
    try:
        ugovor = violation_data['ugovor']
        dobavljac = ugovor.dobavljac

        with transaction.atomic():
            create_kwargs = {
                'razlog_p': violation_data['razlog'],
                'iznos_p': violation_data['iznos_penala'],
                'tip_penala_p': 'OSTALO',  # istek ugovora ne spada ni u jednu od preostale 3 kategorije
                'ugovor': ugovor,
            }
            if penal_id is not None:
                create_kwargs['sifra_p'] = penal_id

            try:
                penal = Penal.objects.create(**create_kwargs)
            except IntegrityError:
                if penal_id is None:
                    raise

                fresh_next_id = (Penal.objects.aggregate(max_id=Max('sifra_p'))['max_id'] or 0) + 1
                create_kwargs['sifra_p'] = fresh_next_id
                penal = Penal.objects.create(**create_kwargs)

            if violation_data['tip_krsenja'] == 'istek_ugovora' and ugovor.status_u != 'istekao':
                ugovor.status_u = 'istekao'
                ugovor.save(update_fields=['status_u'])

            logger.info(f"Automatski kreiran penal {penal.sifra_p} za ugovor {ugovor.sifra_u}")

        if send_email:
            email_sent = send_penalty_notification(
                dobavljac_email=dobavljac.email_db,
                penal=penal,
                ugovor=ugovor,
                razlog_detalji=f"\n{violation_data.get('detalji', '')}\n",
                connection=email_connection,
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
    """
    try:
        violations = check_contract_violations()

        if not violations:
            return Response({
                'message': 'Nije pronađeno nijedno kršenje ugovora',
                'violations_found': 0,
                'penalties_created': 0,
                'errors': []
            }, status=status.HTTP_200_OK)

        created_penalties = []
        errors = []
        email_jobs = []

        next_penal_id = (Penal.objects.aggregate(max_id=Max('sifra_p'))['max_id'] or 0) + 1

        for violation in violations:
            success, penal, error_msg = auto_create_penalty(
                violation,
                send_email=False,
                penal_id=next_penal_id,
            )
            next_penal_id += 1

            if success:
                created_penalties.append({
                    'penal_id': penal.sifra_p,
                    'ugovor_id': violation['ugovor'].sifra_u,
                    'dobavljac': violation['ugovor'].dobavljac.naziv_db,
                    'tip_krsenja': violation['tip_krsenja'],
                    'iznos': float(violation['iznos_penala']),
                    'razlog': violation['razlog']
                })

                email_jobs.append({
                    'penal_id': penal.sifra_p,
                    'dobavljac_email': violation['ugovor'].dobavljac.email_db,
                    'razlog_detalji': f"\n{violation.get('detalji', '')}\n",
                })
            else:
                errors.append({
                    'ugovor_id': violation['ugovor'].sifra_u,
                    'dobavljac': violation['ugovor'].dobavljac.naziv_db,
                    'error': error_msg
                })

        if email_jobs:
            jobs_payload = list(email_jobs)
            transaction.on_commit(
                lambda jobs=jobs_payload: Thread(
                    target=_dispatch_penalty_notifications_async,
                    args=(jobs,),
                    daemon=True,
                ).start()
            )

        response_data = {
            'message': f'Provera završena. Kreirano {len(created_penalties)} penala.',
            'violations_found': len(violations),
            'penalties_created': len(created_penalties),
            'penalties': created_penalties,
            'errors': errors
        }

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
    """
    try:
        violations = check_contract_violations()

        violations_data = []
        for violation in violations:
            violations_data.append({
                'ugovor_id': violation['ugovor'].sifra_u,
                'dobavljac': violation['ugovor'].dobavljac.naziv_db,
                'dobavljac_email': violation['ugovor'].dobavljac.email_db,
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


def create_transaction(faktura, korisnik):
    """
    Kreiranje transakcije za fakturu - automatsko skidanje sredstava.
    Ako transakcija već postoji, ažurira je na 'uspesna' i vraća je.
    Takođe prebacuje fakturu u status 'isplacena' preko promeni_status()
    (upisuje istorijat u PromenaStatusa - razlog čekanja se time briše, jer
    Faktura.razlog_cekanja_f sada čita razlog POSLEDNJE promene statusa).
    """
    try:
        postojeca_transakcija = faktura.transakcija
        if postojeca_transakcija is not None:
            logger.info(f"Transakcija već postoji za fakturu {faktura.sifra_f}, ažuriram status")

            if postojeca_transakcija.status_t != 'uspesna':
                postojeca_transakcija.status_t = 'uspesna'
                postojeca_transakcija.datum_t = timezone.now()
                postojeca_transakcija.iznos_t = faktura.iznos_f
                postojeca_transakcija.save()
                logger.info(f"Status transakcije {postojeca_transakcija.broj_potvrde_t} promenjen na 'uspesna'")

            if faktura.status_f != 'isplacena':
                faktura.promeni_status('isplacena', korisnik)
                logger.info(f"Faktura {faktura.sifra_f}: status = 'isplacena'")

            return postojeca_transakcija

        max_sifra = Transakcija.objects.aggregate(Max('sifra_t'))['sifra_t__max']
        nova_sifra = (max_sifra or 0) + 1

        broj_potvrde = f"TRX-{uuid.uuid4().hex[:12].upper()}"

        while Transakcija.objects.filter(broj_potvrde_t=broj_potvrde).exists():
            broj_potvrde = f"TRX-{uuid.uuid4().hex[:12].upper()}"

        transakcija = Transakcija.objects.create(
            sifra_t=nova_sifra,
            faktura=faktura,
            broj_potvrde_t=broj_potvrde,
            status_t='uspesna',
            datum_t=timezone.now(),
            iznos_t=faktura.iznos_f,
        )

        if faktura.status_f != 'isplacena':
            faktura.promeni_status('isplacena', korisnik)

        logger.info(f"Transakcija {broj_potvrde} (ID: {nova_sifra}) kreirana za fakturu {faktura.sifra_f}")
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
        faktura = get_object_or_404(Faktura, sifra_f=invoice_id)

        if faktura.status_f == 'isplacena':
            postojeca_transakcija = faktura.transakcija
            if postojeca_transakcija is not None:
                transakcija = postojeca_transakcija
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
                        'supplier': faktura.ugovor.dobavljac.naziv_db
                    },
                    'notifications': {
                        'payment_notification_sent': False,
                        'confirmation_sent': False,
                        'recipient': faktura.ugovor.dobavljac.email_db
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

        dobavljac = faktura.ugovor.dobavljac
        dobavljac_email = dobavljac.email_db if dobavljac.email_db else 'noreply@example.com'

        with transaction.atomic():
            notification_sent = send_payment_notification(dobavljac_email, faktura)

            transakcija = create_transaction(faktura, request.user)

            confirmation_sent = send_confirmation_notification(dobavljac_email, transakcija, faktura)

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
                'supplier': dobavljac.naziv_db
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
