from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.apps import apps
from datetime import date, timedelta, datetime
from decimal import Decimal
from .models import Artikal, Popust, Skladiste, Temperatura, Vozilo, Isporuka, Upozorenje, User
from .views import posalji_notifikaciju
import logging

# Postavi logging
logger = logging.getLogger(__name__)


def check_and_update_skladiste_status(skladiste):
    """
    Proveri i ažuriraj status rizika skladišta na osnovu poslednje temperature
    """
    # Dobij poslednju temperaturu za ovo skladište
    poslednja_temp = Temperatura.objects.filter(
        skladiste=skladiste
    ).order_by('-vreme_merenja').first()
    
    if not poslednja_temp:
        return False
    
    stari_status = skladiste.status_rizika_s
    
    # Odredi novi status na osnovu temperature
    if poslednja_temp.vrednost > 6:
        novi_status = 'visok'
    elif poslednja_temp.vrednost >= 4:
        novi_status = 'umeren'
    else:
        novi_status = 'nizak'
    
    # Promeni status ako je potrebno
    if stari_status != novi_status:
        # Direktno ažuriranje u bazi
        Skladiste.objects.filter(sifra_s=skladiste.sifra_s).update(status_rizika_s=novi_status)
        logger.info(f"Skladište {skladiste.sifra_s} ({skladiste.mesto_s}): {stari_status} → {novi_status} (temperatura: {poslednja_temp.vrednost}°C)")
        return True
    
    return False


def update_all_skladista_status():
    """
    Manuelno ažuriranje statusa svih skladišta na osnovu poslednje temperature
    Poziva se kada god treba da se proveri stanje svih skladišta
    """
    skladista = Skladiste.objects.all()
    updated_count = 0
    
    for skladiste in skladista:
        try:
            was_changed = check_and_update_skladiste_status(skladiste)
            if was_changed:
                updated_count += 1
        except Exception as e:
            logger.error(f"Greška pri proveri skladišta {skladiste.sifra_s}: {str(e)}")
    
    return updated_count


def update_all_artikli_status():
    """
    Manuelno ažuriranje statusa svih artikala na osnovu roka trajanja
    Poziva se kada god treba da se proveri stanje svih artikala
    """
    artikli = Artikal.objects.all()
    updated_count = 0
    
    for artikal in artikli:
        try:
            was_changed = check_and_update_artikel_status(artikal)
            if was_changed:
                updated_count += 1
        except Exception as e:
            logger.error(f"Greška pri proveri artikla {artikal.sifra_a}: {str(e)}")
    
    return updated_count


def check_all_skladista_status():
    """
    Proveri i ažuriraj status rizika za sva skladišta
    """
    skladista = Skladiste.objects.all()
    promenjenih_skladista = 0
    
    for skladiste in skladista:
        try:
            was_changed = check_and_update_skladiste_status(skladiste)
            if was_changed:
                promenjenih_skladista += 1
        except Exception as e:
            logger.error(f"Greška pri proveri skladišta {skladiste.sifra_s}: {str(e)}")
    
    return promenjenih_skladista


@receiver(post_save, sender=Temperatura)
def check_skladiste_on_temperatura_save(sender, instance, created, **kwargs):
    """
    Signal koji se pokreće kada se doda nova temperatura
    Automatski ažurira status rizika skladišta
    """
    try:
        was_changed = check_and_update_skladiste_status(instance.skladiste)
        
        if created and was_changed:
            logger.info(f"Status skladišta {instance.skladiste.mesto_s} ažuriran nakon dodavanja temperature {instance.vrednost}°C")
            
    except Exception as e:
        logger.error(f"Greška pri proveri skladišta nakon temperature: {str(e)}")


def check_and_update_artikel_status(artikal):

    """
    Proveri i ažuriraj status artikla na osnovu roka trajanja
    """
    danas = date.today()
    datum_za_7_dana = danas + timedelta(days=7)
    
    stari_status = artikal.status_trajanja
    novi_status = stari_status
    
    # Proveri status na osnovu roka trajanja
    if artikal.rok_trajanja_a < danas:
        # Rok je već prošao
        novi_status = 'istekao'
    elif artikal.rok_trajanja_a <= datum_za_7_dana:
        # Rok ističe za 7 ili manje dana
        novi_status = 'istice'
    else:
        # Još uvek je aktivan
        novi_status = 'aktivan'
    
    # Promeni status ako je potrebno
    if stari_status != novi_status:
        artikal.status_trajanja = novi_status
        artikal.save()
        
        logger.info(f"Artikal {artikal.sifra_a} ({artikal.naziv_a}): {stari_status} → {novi_status}")
        
        # Kreiraj popust za artikle koji ističu (samo za novo promenjene)
        if novi_status == 'istice' and stari_status != 'istice':
            create_discount_for_artikel(artikal)
    
    return novi_status != stari_status


def create_discount_for_artikel(artikal):
    """
    Kreira popust za artikal koji ističe
    """
    danas = date.today()
    
    # Proverava da li već postoji popust za ovaj artikal u tom periodu
    postojeci_popust = Popust.objects.filter(
        artikli=artikal,
        datum_pocetka_vazenja_p__lte=danas,
        datum_kraja_vazenja_p__gte=danas
    ).first()
    
    if not postojeci_popust:
        # Izračunaj popust cenu (50% od osnovne cene)
        popust_cena = artikal.osnovna_cena_a * Decimal('0.5')
        
        # Kreiraj novi popust
        popust = Popust.objects.create(
            predlozena_cena_a=popust_cena,
            datum_pocetka_vazenja_p=danas,
            datum_kraja_vazenja_p=artikal.rok_trajanja_a
        )
        # Dodeli artikal popustu
        popust.artikli.add(artikal)
        
        logger.info(
            f"Kreiran popust za artikal {artikal.sifra_a}: "
            f"{artikal.osnovna_cena_a} → {popust_cena} "
            f"(važeće od {danas} do {artikal.rok_trajanja_a})"
        )
        return popust
    else:
        logger.info(
            f"Popust već postoji za artikal {artikal.sifra_a} "
            f"u periodu {postojeci_popust.datum_pocetka_vazenja_p} - {postojeci_popust.datum_kraja_vazenja_p}"
        )
        return postojeci_popust


@receiver(post_save, sender=Artikal)
def check_artikel_on_save(sender, instance, created, **kwargs):
    """
    Signal koji se pokreće kada se artikal sačuva (kreiran ili ažuriran)
    """
    try:
        # Proveri status artikla odmah nakon dodavanja/ažuriranja
        was_changed = check_and_update_artikel_status(instance)
        
        if created:
            logger.info(f"Novi artikal dodat: {instance.naziv_a} (ID: {instance.sifra_a})")
            if was_changed:
                logger.info(f"Status novog artikla automatski ažuriran")
        elif was_changed:
            logger.info(f"Status artikla {instance.sifra_a} automatski ažuriran")
            
    except Exception as e:
        logger.error(f"Greška pri proveri artikla {instance.sifra_a}: {str(e)}")


@receiver(post_migrate)
def check_all_artikli_on_startup(sender, **kwargs):
    """
    Signal koji se pokreće nakon migracija (pri pokretanju aplikacije)
    Proverava sve artikle i skladišta u bazi
    """
    # Proveri da li je signal poslat od naše app
    if sender.name == 'app':
        try:
            logger.info("=== POKRETANJE AUTOMATSKE PROVERE SVIH ARTIKALA I SKLADIŠTA ===")
            
            # Proveri artikle
            artikli = Artikal.objects.all()
            promenjenih_artikala = 0
            kreiranih_popusta = 0
            
            for artikal in artikli:
                try:
                    was_changed = check_and_update_artikel_status(artikal)
                    if was_changed:
                        promenjenih_artikala += 1
                        
                        # Ako je promenjen na 'istice', popust je već kreiran u check_and_update_artikel_status
                        if artikal.status_trajanja == 'istice':
                            kreiranih_popusta += 1
                            
                except Exception as e:
                    logger.error(f"Greška pri proveri artikla {artikal.sifra_a}: {str(e)}")
            
            # Proveri skladišta
            promenjenih_skladista = check_all_skladista_status()
            
            # Statistike za artikle
            aktivni = Artikal.objects.filter(status_trajanja='aktivan').count()
            isticu = Artikal.objects.filter(status_trajanja='istice').count()
            istekli = Artikal.objects.filter(status_trajanja='istekao').count()
            
            # Statistike za skladišta
            nizak_rizik = Skladiste.objects.filter(status_rizika_s='nizak').count()
            umeren_rizik = Skladiste.objects.filter(status_rizika_s='umeren').count()
            visok_rizik = Skladiste.objects.filter(status_rizika_s='visok').count()
            
            logger.info(f"Automatska provera završena:")
            logger.info(f"- Artikli: {promenjenih_artikala} promenjeno, {kreiranih_popusta} popusta kreirano")
            logger.info(f"- Skladišta: {promenjenih_skladista} promenjeno")
            logger.info(f"Trenutno stanje artikala - Aktivni: {aktivni}, Ističu: {isticu}, Istekli: {istekli}")
            logger.info(f"Trenutno stanje skladišta - Nizak rizik: {nizak_rizik}, Umeren: {umeren_rizik}, Visok: {visok_rizik}")
            logger.info("=== ZAVRŠETAK AUTOMATSKE PROVERE ===")
            
        except Exception as e:
            logger.error(f"Greška pri automatskoj proveri na startup-u: {str(e)}")
def get_isporuka_vozilo(vozilo):
    try:
        isporuka = Isporuka.objects.get(vozilo=vozilo)
        return isporuka
    except Isporuka.DoesNotExist:
        return None
@receiver(post_save, sender=Vozilo)
def obavesti_o_kvaru(sender, instance, **kwargs):
    #prethodno = Vozilo.objects.get(pk=instance.pk) prethodno.status != instance.status
    if instance.status == 'u_kvaru':
        upozorenje = Upozorenje.objects.create(
            isporuka=get_isporuka_vozilo(instance),
            tip='kvar',
            poruka=f"Vozilo {instance.marka} {instance.model} je u kvaru.",
            vreme = datetime.now(),
            status = False,
        )
        # šalje obaveštenje lk
        isporuka = get_isporuka_vozilo(instance)
        koordinatori = User.objects.filter(tip_k='logisitcki_koordinator')
        for n in koordinatori:
            posalji_notifikaciju(
                n,
                f"Kvar na vozilu {instance.registracija}. Pogledaj detalje isporuke #{isporuka.sifra_i}.",
                link=f"/upozorenja/{upozorenje.sifra_u}"
            )

@receiver(post_save, sender=Isporuka)
def obavesti_o_novoj_isporuci(sender, instance, created, **kwargs):
    if created:
        # šalje se logističkom koordinatoru
        koordinatori = User.objects.filter(tip_k='logisticki_koordinator')
        for k in koordinatori:
            posalji_notifikaciju(
                k,
                f"Nova isporuka #{instance.sifra_i} je kreirana. Proveri raspoloživost vozila.",
                link=f"/isporuke/{instance.sifra_i}"
            )