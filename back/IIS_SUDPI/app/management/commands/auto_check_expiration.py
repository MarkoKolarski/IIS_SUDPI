from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime


class Command(BaseCommand):
    help = 'Pokreće automatsku proveru isteka roka artikala - za cron job'

    def handle(self, *args, **options):
        self.stdout.write(f"[{datetime.now()}] Pokretanje automatske provere rokova...")
        
        try:
            # Pozovi glavnu komandu
            call_command('check_expiration')
            self.stdout.write(
                self.style.SUCCESS(f"[{datetime.now()}] Automatska provera završena uspešno")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[{datetime.now()}] Greška tokom automatske provere: {str(e)}")
            )
            raise e