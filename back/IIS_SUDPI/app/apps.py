from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Importuj signale kada se aplikacija učita
        import app.signals
        
        # Pokreni početnu proveru svih skladišta
        self._check_initial_skladista_status()
    
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
