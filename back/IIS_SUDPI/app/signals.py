from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.apps import apps
from datetime import date, timedelta
from decimal import Decimal
from .models import Artikal, Popust
import logging

# Postavi logging
logger = logging.getLogger(__name__)


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
    Proverava sve artikle u bazi
    """
    # Proveri da li je signal poslat od naše app
    if sender.name == 'app':
        try:
            logger.info("=== POKRETANJE AUTOMATSKE PROVERE SVIH ARTIKALA ===")
            
            # Dobij sve artikle
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
            
            # Statistike
            aktivni = Artikal.objects.filter(status_trajanja='aktivan').count()
            isticu = Artikal.objects.filter(status_trajanja='istice').count()
            istekli = Artikal.objects.filter(status_trajanja='istekao').count()
            
            logger.info(f"Automatska provera završena: {promenjenih_artikala} artikala promenjeno")
            logger.info(f"Kreiran{'' if kreiranih_popusta == 1 else 'o'} {kreiranih_popusta} popust{'a' if kreiranih_popusta != 1 else ''}")
            logger.info(f"Trenutno stanje - Aktivni: {aktivni}, Ističu: {isticu}, Istekli: {istekli}")
            logger.info("=== ZAVRŠETAK AUTOMATSKE PROVERE ===")
            
        except Exception as e:
            logger.error(f"Greška pri automatskoj proveri na startup-u: {str(e)}")


def manual_check_all_artikli():
    """
    Funkcija za ručno pokretanje provere svih artikala (za testiranje)
    """
    logger.info("=== RUČNO POKRETANJE PROVERE SVIH ARTIKALA ===")
    
    artikli = Artikal.objects.all()
    promenjenih_artikala = 0
    kreiranih_popusta = 0
    
    for artikal in artikli:
        try:
            was_changed = check_and_update_artikel_status(artikal)
            if was_changed:
                promenjenih_artikala += 1
                
                if artikal.status_trajanja == 'istice':
                    kreiranih_popusta += 1
                    
        except Exception as e:
            logger.error(f"Greška pri proveri artikla {artikal.sifra_a}: {str(e)}")
    
    logger.info(f"Ručna provera završena: {promenjenih_artikala} artikala promenjeno")
    logger.info(f"Kreiran{'' if kreiranih_popusta == 1 else 'o'} {kreiranih_popusta} popust{'a' if kreiranih_popusta != 1 else ''}")
    logger.info("=== ZAVRŠETAK RUČNE PROVERE ===")
    
    return {
        'promenjenih_artikala': promenjenih_artikala,
        'kreiranih_popusta': kreiranih_popusta
    }