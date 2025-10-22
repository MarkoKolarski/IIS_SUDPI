from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import connection, transaction
from django.utils import timezone
from .decorators import allowed_users
from .models import Faktura, StavkaFakture, Proizvod, Ugovor, Dobavljac, Izvestaj
from decimal import Decimal
import json
import time
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def dodaj_stavku_fakture(request):
    """
    ZADATAK 1: Test trigera AZURIRAJ_FAKTURU_NAKON_UNOSA
    Dodaje novu stavku fakture i automatski ažurira iznos fakture preko trigera
    """
    try:
        faktura_id = request.data.get('faktura_id')
        proizvod_id = request.data.get('proizvod_id')
        naziv_sf = request.data.get('naziv_sf')
        kolicina_sf = request.data.get('kolicina_sf')
        cena_po_jed = request.data.get('cena_po_jed')

        logger.info(f"Primljeni parametri: faktura_id={faktura_id}, proizvod_id={proizvod_id}, naziv_sf={naziv_sf}, kolicina_sf={kolicina_sf}, cena_po_jed={cena_po_jed}")

        if not all([faktura_id, proizvod_id, naziv_sf, kolicina_sf, cena_po_jed]):
            return Response(
                {'error': 'Svi parametri su obavezni'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validacija da li faktura i proizvod postoje
        try:
            faktura = Faktura.objects.get(sifra_f=faktura_id)
            logger.info(f"Pronađena faktura: {faktura_id}")
        except Faktura.DoesNotExist:
            logger.error(f"Faktura sa ID {faktura_id} ne postoji")
            return Response({'error': f'Faktura sa ID {faktura_id} ne postoji'}, status=status.HTTP_404_NOT_FOUND)

        try:
            proizvod = Proizvod.objects.get(sifra_pr=proizvod_id)
            logger.info(f"Pronađen proizvod: {proizvod_id}")
        except Proizvod.DoesNotExist:
            logger.error(f"Proizvod sa ID {proizvod_id} ne postoji")
            return Response({'error': f'Proizvod sa ID {proizvod_id} ne postoji'}, status=status.HTTP_404_NOT_FOUND)

        stari_iznos = faktura.iznos_f

        # Konverzija tipova podataka
        try:
            kolicina_sf = int(kolicina_sf)
            cena_po_jed = float(cena_po_jed)
            logger.info(f"Konvertovani tipovi: kolicina_sf={kolicina_sf} (int), cena_po_jed={cena_po_jed} (float)")
        except (ValueError, TypeError) as e:
            logger.error(f"Greška pri konverziji tipova: {str(e)}")
            return Response(
                {'error': f'Pogrešan format podataka. Količina mora biti broj, cena mora biti decimalon broj. Greška: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            with connection.cursor() as cursor:
                try:
                    sql = """
                        INSERT INTO STAVKA_FAKTURE (SIFRA_SF, NAZIV_SF, KOLICINA_SF, CENA_PO_JED, FAKTURA_ID, PROIZVOD_ID)
                        VALUES (STAVKA_FAKTURE_SEQ.NEXTVAL, %s, %s, %s, %s, %s)
                    """
                    logger.info(f"Izvršavanje SQL INSERT u STAVKA_FAKTURE")
                    logger.info(f"Parametri: naziv_sf={naziv_sf}, kolicina_sf={kolicina_sf}, cena_po_jed={cena_po_jed}, faktura_id={faktura_id}, proizvod_id={proizvod_id}")
                    
                    cursor.execute(sql, [naziv_sf, kolicina_sf, cena_po_jed, faktura_id, proizvod_id])
                    logger.info(f"Stavka fakture uspešno insertovana")
                except Exception as e:
                    logger.error(f"Greška pri INSERT-u stavke fakture: {str(e)}", exc_info=True)
                    raise

        # Osvežavanje fakture iz baze
        faktura.refresh_from_db()
        novi_iznos = faktura.iznos_f
        logger.info(f"Faktura osvežena - stari iznos: {stari_iznos}, novi iznos: {novi_iznos}")

        return Response({
            'success': True,
            'message': 'Stavka fakture uspešno dodata. Triger je automatski ažurirao iznos fakture.',
            'stari_iznos': float(stari_iznos),
            'novi_iznos': float(novi_iznos),
            'razlika': float(novi_iznos - stari_iznos),
            'faktura_id': faktura_id
        })

    except Exception as e:
        logger.error(f"Neočekivana greška u dodaj_stavku_fakture: {str(e)}", exc_info=True)
        return Response({'error': f'Greška: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def get_fakture_za_stavke(request):
    """
    Vraća listu faktura koje nisu isplaćene za dodavanje stavki
    """
    try:
        fakture = Faktura.objects.exclude(status_f='isplacena').select_related('ugovor__dobavljac')[:50]
        
        data = [{
            'sifra_f': f.sifra_f,
            'iznos_f': float(f.iznos_f),
            'status_f': f.status_f,
            'dobavljac': f.ugovor.dobavljac.naziv if f.ugovor and f.ugovor.dobavljac else 'N/A'
        } for f in fakture]

        return Response({'fakture': data})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def get_proizvodi(request):
    """
    Vraća listu proizvoda za stavke fakture
    """
    try:
        proizvodi = Proizvod.objects.all()[:100]
        
        data = [{
            'sifra_pr': p.sifra_pr,
            'naziv_pr': p.naziv_pr
        } for p in proizvodi]

        return Response({'proizvodi': data})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def izracunaj_dug_dobavljaca(request):
    """
    ZADATAK 2: Poziva PL/SQL funkciju IZRACUNAJ_DUG_DOBAVLJACU
    Vraća sve dobavljače sa njihovim ukupnim dugom
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    SIFRA_D,
                    NAZIV,
                    IZRACUNAJ_DUG_DOBAVLJACU(SIFRA_D) AS UKUPAN_DUG
                FROM DOBAVLJAC
                ORDER BY IZRACUNAJ_DUG_DOBAVLJACU(SIFRA_D) DESC
            """)
            
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

        return Response({
            'dobavljaci': results,
            'ukupan_dug_svi': sum(float(d['UKUPAN_DUG']) for d in results)
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def test_indeksa_bez_indeksa(request):
    """
    ZADATAK 3: Testira performanse upita BEZ indeksa
    """
    try:
        with connection.cursor() as cursor:
            start_time = time.time()
            
            cursor.execute("""
                SELECT COUNT(*) as CNT, AVG(IZNOS_F) as AVG_IZNOS
                FROM FAKTURA 
                WHERE STATUS_F IN ('primljena', 'verifikovana') 
                  AND ROK_PLACANJA_F < SYSDATE
            """)
            
            result = cursor.fetchone()
            execution_time = time.time() - start_time

        return Response({
            'count': result[0],
            'avg_iznos': float(result[1]) if result[1] else 0,
            'execution_time_seconds': execution_time,
            'sa_indeksom': False
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def test_indeksa_sa_indeksom(request):
    """
    ZADATAK 3: Testira performanse upita SA indeksom
    """
    try:
        with connection.cursor() as cursor:
            start_time = time.time()
            
            cursor.execute("""
                SELECT COUNT(*) as CNT, AVG(IZNOS_F) as AVG_IZNOS
                FROM FAKTURA 
                WHERE STATUS_F IN ('primljena', 'verifikovana') 
                  AND ROK_PLACANJA_F < SYSDATE
            """)
            
            result = cursor.fetchone()
            execution_time = time.time() - start_time

        return Response({
            'count': result[0],
            'avg_iznos': float(result[1]) if result[1] else 0,
            'execution_time_seconds': execution_time,
            'sa_indeksom': True
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def generiši_test_fakture(request):
    """
    ZADATAK 3: Generiše 800,000 test faktura za testiranje indeksa
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DECLARE
                    v_ugovor_id UGOVOR.SIFRA_U%TYPE;
                BEGIN
                    SELECT SIFRA_U INTO v_ugovor_id FROM UGOVOR FETCH FIRST 1 ROWS ONLY;

                    FOR i IN 1..800000 LOOP
                        INSERT INTO FAKTURA (SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F, STATUS_F, UGOVOR_ID)
                        VALUES (
                            FAKTURA_SEQ.NEXTVAL,
                            TRUNC(DBMS_RANDOM.VALUE(1000, 50000), 2),
                            SYSDATE - TRUNC(DBMS_RANDOM.VALUE(1, 365)),
                            CASE 
                                WHEN DBMS_RANDOM.VALUE(0, 100) < 10 THEN 
                                    SYSDATE - TRUNC(DBMS_RANDOM.VALUE(1, 90))
                                ELSE 
                                    SYSDATE + TRUNC(DBMS_RANDOM.VALUE(60, 180))
                            END,
                            CASE TRUNC(DBMS_RANDOM.VALUE(0, 10))
                                WHEN 0 THEN 'primljena'
                                WHEN 1 THEN 'verifikovana'
                                ELSE 'isplacena'
                            END,
                            v_ugovor_id
                        );
                    END LOOP;
                    COMMIT;
                END;
            """)

        return Response({
            'success': True,
            'message': 'Uspešno generisano 800,000 test faktura'
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def kreiraj_indeks(request):
    """
    ZADATAK 3: Kreira indeks IDX_FAKTURA_STATUS_ROK
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE 'DROP INDEX IDX_FAKTURA_STATUS_ROK';
                EXCEPTION
                    WHEN OTHERS THEN NULL;
                END;
            """)
            
            cursor.execute("""
                CREATE INDEX IDX_FAKTURA_STATUS_ROK ON FAKTURA(STATUS_F, ROK_PLACANJA_F)
            """)

        return Response({
            'success': True,
            'message': 'Indeks IDX_FAKTURA_STATUS_ROK uspešno kreiran'
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def obrisi_indeks(request):
    """
    ZADATAK 3: Briše indeks IDX_FAKTURA_STATUS_ROK
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE 'DROP INDEX IDX_FAKTURA_STATUS_ROK';
                EXCEPTION
                    WHEN OTHERS THEN NULL;
                END;
            """)

        return Response({
            'success': True,
            'message': 'Indeks IDX_FAKTURA_STATUS_ROK uspešno obrisan'
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def generisi_mesecni_izvestaj(request):
    """
    ZADATAK 4: Poziva proceduru GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI
    """
    try:
        mesec = request.data.get('mesec')
        godina = request.data.get('godina')
        kreator_id = request.user.sifra_k

        if not mesec or not godina:
            return Response(
                {'error': 'Mesec i godina su obavezni parametri'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with connection.cursor() as cursor:
            cursor.execute("""
                BEGIN
                    GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI(:mesec, :godina, :kreator_id);
                END;
            """, [mesec, godina, kreator_id])

        izvestaj = Izvestaj.objects.filter(
            tip_i='finansijski',
            kreirao_id=kreator_id
        ).order_by('-datum_i').first()

        if izvestaj:
            sadrzaj = json.loads(izvestaj.sadrzaj_i)
            return Response({
                'success': True,
                'izvestaj': sadrzaj,
                'datum_kreiranja': izvestaj.datum_i
            })
        else:
            return Response({
                'success': False,
                'message': 'Izveštaj nije kreiran. Možda nema dovoljno podataka za izabrani period.'
            })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@allowed_users(['finansijski_analiticar'])
def poslednji_izvestaj(request):
    """
    ZADATAK 4: Vraća poslednji generisani izveštaj
    """
    try:
        izvestaj = Izvestaj.objects.filter(
            tip_i='finansijski'
        ).order_by('-datum_i').first()

        if not izvestaj:
            return Response({
                'message': 'Nema dostupnih izveštaja'
            }, status=status.HTTP_404_NOT_FOUND)

        sadrzaj = json.loads(izvestaj.sadrzaj_i)
        
        return Response({
            'izvestaj': sadrzaj,
            'datum_kreiranja': izvestaj.datum_i,
            'kreirao': izvestaj.kreirao_id
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
