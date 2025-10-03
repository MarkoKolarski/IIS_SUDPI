from django.core.management.base import BaseCommand
from app.signals import check_all_skladista_status
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Proveri i ažuriraj status rizika za sva skladišta na osnovu najnovije temperature'

    def handle(self, *args, **options):
        self.stdout.write("=== POKRETANJE PROVERE STATUSA SKLADIŠTA ===")
        
        promenjenih_skladista = check_all_skladista_status()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Provera završena: {promenjenih_skladista} skladišta je promenilo status"
            )
        )
        
        # Prikaži trenutno stanje
        from app.models import Skladiste
        nizak_rizik = Skladiste.objects.filter(status_rizika_s='nizak').count()
        umeren_rizik = Skladiste.objects.filter(status_rizika_s='umeren').count() 
        visok_rizik = Skladiste.objects.filter(status_rizika_s='visok').count()
        
        self.stdout.write(f"Trenutno stanje skladišta:")
        self.stdout.write(f"- Nizak rizik: {nizak_rizik}")
        self.stdout.write(f"- Umeren rizik: {umeren_rizik}")
        self.stdout.write(f"- Visok rizik: {visok_rizik}")
        self.stdout.write("=== ZAVRŠETAK PROVERE ===")