from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Importuj signale kada se aplikacija učita
        import app.signals
        
        # Pokreni početnu proveru svih skladišta
        self._check_initial_skladista_status()
    
        self._test_signali()

    def _check_initial_skladista_status(self):
        """
        Proveri i ažuriraj status svih skladišta prilikom pokretanja
        """
        try:
            from .models import Skladiste, Temperatura
            
            print("=== POKRETANJE AUTOMATSKE PROVERE SKLADIŠTA ===")
            
            skladista = Skladiste.objects.all()
            promenjenih = 0
            
            for skladiste in skladista:
                # Dobij najnoviju temperaturu
                najnovija_temp = Temperatura.objects.filter(
                    skladiste=skladiste
                ).order_by('-vreme_merenja').first()
                
                if najnovija_temp:
                    # Određi novi status
                    if najnovija_temp.vrednost > 6:
                        novi_status = 'visok'
                    elif najnovija_temp.vrednost > 4:
                        novi_status = 'umeren'
                    else:
                        novi_status = 'nizak'
                    
                    # Ažuriraj ako je potrebno
                    if skladiste.status_rizika_s != novi_status:
                        stari_status = skladiste.status_rizika_s
                        skladiste.status_rizika_s = novi_status
                        skladiste.save()
                        promenjenih += 1
                        
                        print(f"Ažuriran status: {skladiste.mesto_s} - {stari_status} → {novi_status} (temp: {najnovija_temp.vrednost}°C)")
            
            print(f"Provera završena: {promenjenih} skladišta ažurirano")
            print("=== ZAVRŠETAK AUTOMATSKE PROVERE ===")
            
        except Exception as e:
            print(f"Greška pri početnoj proveri skladišta: {e}")
    def _test_signali(self):
        """
        Test funkcija za proveru da li signali rade ispravno
        """
        try:
            from .models import Vozilo, Isporuka, User
            from datetime import datetime, timedelta, date
            from django.utils import timezone
            
            print("=== POKRETANJE TESTA SIGNALA - vozilo ===")
            
            # Kreiraj test vozilo
            test_vozilo = Vozilo.objects.create(
                marka='TestMarka',
                model='TestModel',
                status='slobodno',
                registracija=date.today(),
                kapacitet=1000
            )
            print(f"Kreirano test vozilo: {test_vozilo.marka} {test_vozilo.model} sa statusom {test_vozilo.status}")
            
            
            print("=== POKRETANJE TESTA SIGNALA - isporuka ===")
            
            nova_isporuka = Isporuka.objects.create(
                #sifra_i="TEST001",
                kolicina_kg = 300,
                status = 'aktivna',
                datum_polaska = timezone.now(),
                rok_is = timezone.now() + timedelta(days=4),
                datum_dolaska = timezone.now() + timedelta(days=2),
                vozilo=test_vozilo,
                #datum_isporuke=datetime.now(),
                #odrediste="Test destinacija",
                #koordinator=koordinator
            )
            print(f"✅ Test 2: Kreirana test isporuka → signal aktiviran!")

            # Promeni status vozila da izazove signal
            test_vozilo.status = 'u_kvaru'
            test_vozilo.save()
            print(f"Ažuriran status test vozila na: {test_vozilo.status}")
            

            print("=== ZAVRŠETAK TESTA SIGNALA ===")
            
        except Exception as e:
            print(f"Greška pri testiranju signala: {e}")