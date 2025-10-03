from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from app.models import Artikal, Popust


class Command(BaseCommand):
    help = 'Proverava rokove trajanja artikala i kreira popuste za one koji ističu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Prikazuje šta bi bilo promenjeno bez stvarnih izmena',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        danas = date.today()
        datum_za_7_dana = danas + timedelta(days=7)
        
        self.stdout.write(f"Pokrećem proveru rokova artikala - {danas}")
        
        # Statistike
        promenjenih_artikala = 0
        kreiranih_popusta = 0
        
        # Dobij sve artikle
        artikli = Artikal.objects.all()
        
        for artikal in artikli:
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
                if not dry_run:
                    artikal.status_trajanja = novi_status
                    artikal.save()
                
                self.stdout.write(
                    f"Artikal {artikal.sifra_a} ({artikal.naziv_a}): "
                    f"{stari_status} → {novi_status}"
                )
                promenjenih_artikala += 1
                
                # Kreiraj popust za artikle koji ističu (samo za novo promenjene)
                if novi_status == 'istice' and stari_status != 'istice':
                    # Proverava da li već postoji popust za ovaj artikal u tom periodu
                    postojeci_popust = Popust.objects.filter(
                        artikli=artikal,
                        datum_pocetka_vazenja_p__lte=danas,
                        datum_kraja_vazenja_p__gte=danas
                    ).first()
                    
                    if not postojeci_popust:
                        # Izračunaj popust cenu (50% od osnovne cene)
                        popust_cena = artikal.osnovna_cena_a * Decimal('0.5')
                        
                        if not dry_run:
                            # Kreiraj novi popust
                            popust = Popust.objects.create(
                                predlozena_cena_a=popust_cena,
                                datum_pocetka_vazenja_p=danas,
                                datum_kraja_vazenja_p=artikal.rok_trajanja_a
                            )
                            # Dodeli artikal popustu
                            popust.artikli.add(artikal)
                        
                        self.stdout.write(
                            f"  → Kreiran popust: {artikal.osnovna_cena_a} → {popust_cena} "
                            f"(važeće od {danas} do {artikal.rok_trajanja_a})"
                        )
                        kreiranih_popusta += 1
                    else:
                        self.stdout.write(
                            f"  → Popust već postoji za period {postojeci_popust.datum_pocetka_vazenja_p} - {postojeci_popust.datum_kraja_vazenja_p}"
                        )
        
        # Prikaži sažetak
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Bilo bi promenjeno {promenjenih_artikala} artikala "
                    f"i kreirano {kreiranih_popusta} popusta"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nUspešno završeno! Promenjeno {promenjenih_artikala} artikala "
                    f"i kreirano {kreiranih_popusta} popusta"
                )
            )
        
        # Dodatno: Prikaži pregled trenutnog stanja
        self.stdout.write("\n=== PREGLED STANJA ===")
        aktivni = Artikal.objects.filter(status_trajanja='aktivan').count()
        isticu = Artikal.objects.filter(status_trajanja='istice').count()
        istekli = Artikal.objects.filter(status_trajanja='istekao').count()
        
        self.stdout.write(f"Aktivni artikli: {aktivni}")
        self.stdout.write(f"Artikli koji ističu: {isticu}")
        self.stdout.write(f"Istekli artikli: {istekli}")
        
        # Prikaži aktivne popuste
        aktivni_popusti = Popust.objects.filter(
            datum_pocetka_vazenja_p__lte=danas,
            datum_kraja_vazenja_p__gte=danas
        ).count()
        self.stdout.write(f"Aktivni popusti: {aktivni_popusti}")