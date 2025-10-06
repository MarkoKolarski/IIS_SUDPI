"""
Saga Orchestrator za transakcionu obradu podataka

Implementira Saga pattern (Orkestracija) između Oracle baze (Django) i InfluxDB (Mikroservis).

Scenario: Kreiranje fakture sa plaćanjem
- Korak 1: Kreiraj fakturu u Oracle bazi
- Korak 2: Kreiraj transakciju u Oracle bazi  
- Korak 3: Pošalji događaj u InfluxDB
- Ako neki korak ne uspe → Rollback (kompenzacione transakcije)
"""

import httpx
import logging
from django.db import transaction as db_transaction
from django.db.models import Max
from django.utils import timezone
from typing import Dict, Any, Tuple
from decimal import Decimal

from .models import Faktura, Transakcija, Ugovor

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    """
    Orkestrator Saga transakcije za kreiranje fakture sa plaćanjem
    
    Koordinira sledeće korake:
    1. Lokalna transakcija u Oracle DB (Faktura + Transakcija)
    2. Mikroservis poziv ka InfluxDB (finansijski događaj)
    3. Kompenzacione transakcije u slučaju greške
    """
    
    def __init__(self, mikroservis_url: str = "http://localhost:8001"):
        self.mikroservis_url = mikroservis_url
        self.saga_log = []  # Log svih koraka za debugging
        
    def log_step(self, step: str, status: str, details: str = ""):
        """Loguje korak Saga transakcije"""
        log_entry = {
            "timestamp": timezone.now().isoformat(),
            "step": step,
            "status": status,
            "details": details
        }
        self.saga_log.append(log_entry)
        logger.info(f"[SAGA] {step}: {status} - {details}")
    
    def create_faktura_with_payment(
        self, 
        ugovor_id: int,
        iznos: Decimal,
        datum_prijema: str,
        rok_placanja: str,
        potvrda_transakcije: str,
        status_transakcije: str = "uspesna"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Glavna Saga funkcija: Kreira fakturu sa plaćanjem (transakciona obrada)
        
        Args:
            ugovor_id: ID ugovora
            iznos: Iznos fakture
            datum_prijema: Datum prijema fakture
            rok_placanja: Rok za plaćanje
            potvrda_transakcije: Broj potvrde transakcije
            status_transakcije: Status transakcije (uspesna/neuspesna/na_cekanju)
            
        Returns:
            (success, result_data)
        """
        
        faktura = None
        transakcija = None
        influx_sent = False
        
        self.log_step("SAGA_START", "INFO", "Pokretanje Saga transakcije")
        
        try:
            # ============================================================
            # KORAK 1: Kreiraj fakturu u Oracle bazi (Django)
            # ============================================================
            self.log_step("STEP_1_START", "INFO", "Kreiranje fakture u Oracle DB")
            
            with db_transaction.atomic():
                # Dohvati ugovor
                try:
                    ugovor = Ugovor.objects.get(sifra_u=ugovor_id)
                except Ugovor.DoesNotExist:
                    self.log_step("STEP_1_FAILED", "ERROR", f"Ugovor {ugovor_id} ne postoji")
                    return False, {
                        "error": "Ugovor ne postoji",
                        "saga_log": self.saga_log
                    }
                
                # Hardkoduj ID - Dobavi MAX(sifra_f) i dodaj 1
                max_faktura_id = Faktura.objects.aggregate(
                    Max('sifra_f')
                )['sifra_f__max'] or 0
                next_faktura_id = max_faktura_id + 1
                
                # Kreiraj fakturu sa eksplicitnim ID-em
                faktura = Faktura(
                    sifra_f=next_faktura_id,
                    iznos_f=iznos,
                    datum_prijema_f=datum_prijema,
                    rok_placanja_f=rok_placanja,
                    status_f='primljena',
                    ugovor=ugovor
                )
                faktura.save()
                
                self.log_step(
                    "STEP_1_SUCCESS", 
                    "SUCCESS", 
                    f"Faktura {faktura.sifra_f} kreirana u Oracle DB"
                )
            
            # ============================================================
            # KORAK 2: Kreiraj transakciju u Oracle bazi (Django)
            # ============================================================
            self.log_step("STEP_2_START", "INFO", "Kreiranje transakcije u Oracle DB")
            
            with db_transaction.atomic():
                # Hardkoduj ID - Dobavi MAX(sifra_t) i dodaj 1
                max_transakcija_id = Transakcija.objects.aggregate(
                    Max('sifra_t')
                )['sifra_t__max'] or 0
                next_transakcija_id = max_transakcija_id + 1
                
                # Kreiraj transakciju sa eksplicitnim ID-em
                transakcija = Transakcija(
                    sifra_t=next_transakcija_id,
                    potvrda_t=potvrda_transakcije,
                    status_t=status_transakcije,
                    faktura=faktura
                )
                transakcija.save()
                
                # Ažuriraj status fakture na osnovu transakcije
                if status_transakcije == "uspesna":
                    faktura.status_f = 'isplacena'
                elif status_transakcije == "neuspesna":
                    faktura.status_f = 'odbijena'
                else:
                    faktura.status_f = 'verifikovana'
                
                faktura.save()
                
                self.log_step(
                    "STEP_2_SUCCESS", 
                    "SUCCESS", 
                    f"Transakcija {transakcija.sifra_t} kreirana u Oracle DB"
                )
            
            # ============================================================
            # KORAK 3: Pošalji događaj u InfluxDB mikroservis
            # ============================================================
            self.log_step("STEP_3_START", "INFO", "Slanje događaja u InfluxDB mikroservis")
            
            mikroservis_data = {
                "faktura_id": faktura.sifra_f,
                "iznos": float(iznos),
                "status": status_transakcije,
                "potvrda": potvrda_transakcije,
                "opis": f"Plaćanje fakture {faktura.sifra_f} po ugovoru {ugovor.sifra_u}"
            }
            
            try:
                response = httpx.post(
                    f"{self.mikroservis_url}/api/dogadjaji/transakcija",
                    json=mikroservis_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    influx_sent = True
                    self.log_step(
                        "STEP_3_SUCCESS", 
                        "SUCCESS", 
                        "Događaj uspešno poslat u InfluxDB"
                    )
                else:
                    raise Exception(f"Mikroservis vratio status {response.status_code}: {response.text}")
                    
            except httpx.RequestError as e:
                self.log_step("STEP_3_FAILED", "ERROR", f"HTTP greška: {str(e)}")
                raise Exception(f"Greška pri komunikaciji sa mikroservisom: {str(e)}")
            
            # ============================================================
            # SAGA USPEŠNA - Svi koraci prošli
            # ============================================================
            self.log_step("SAGA_SUCCESS", "SUCCESS", "Saga transakcija uspešno završena")
            
            return True, {
                "message": "Transakciona obrada uspešno završena",
                "faktura_id": faktura.sifra_f,
                "transakcija_id": transakcija.sifra_t,
                "influxdb_status": "synced",
                "saga_log": self.saga_log
            }
            
        except Exception as e:
            # ============================================================
            # SAGA NEUSPEŠNA - Rollback (kompenzacione transakcije)
            # ============================================================
            self.log_step("SAGA_FAILED", "ERROR", f"Greška: {str(e)}")
            self.log_step("ROLLBACK_START", "INFO", "Pokretanje kompenzacionih transakcija")
            
            # Kompenzaciona transakcija 1: Obriši transakciju iz Oracle DB
            if transakcija:
                try:
                    with db_transaction.atomic():
                        transakcija.delete()
                        self.log_step("ROLLBACK_STEP_1", "SUCCESS", "Transakcija obrisana iz Oracle DB")
                except Exception as rollback_error:
                    self.log_step("ROLLBACK_STEP_1", "ERROR", f"Rollback greška: {str(rollback_error)}")
            
            # Kompenzaciona transakcija 2: Obriši fakturu iz Oracle DB
            if faktura:
                try:
                    with db_transaction.atomic():
                        faktura.delete()
                        self.log_step("ROLLBACK_STEP_2", "SUCCESS", "Faktura obrisana iz Oracle DB")
                except Exception as rollback_error:
                    self.log_step("ROLLBACK_STEP_2", "ERROR", f"Rollback greška: {str(rollback_error)}")
            
            # Kompenzaciona transakcija 3: Obriši događaj iz InfluxDB (ako je poslat)
            if influx_sent:
                try:
                    # InfluxDB ne podržava tačno brisanje pojedinačnog događaja,
                    # ali možemo da označimo događaj kao "otkazan"
                    cancel_data = {
                        "faktura_id": faktura.sifra_f if faktura else 0,
                        "iznos": 0.0,
                        "status": "otkazan",
                        "potvrda": f"ROLLBACK-{potvrda_transakcije}",
                        "opis": f"ROLLBACK: Transakcija otkazana zbog greške u Saga procesu"
                    }
                    
                    httpx.post(
                        f"{self.mikroservis_url}/api/dogadjaji/transakcija",
                        json=cancel_data,
                        timeout=5.0
                    )
                    self.log_step("ROLLBACK_STEP_3", "SUCCESS", "Otkazni događaj poslat u InfluxDB")
                except Exception as rollback_error:
                    self.log_step("ROLLBACK_STEP_3", "ERROR", f"Rollback greška: {str(rollback_error)}")
            
            self.log_step("ROLLBACK_END", "INFO", "Kompenzacione transakcije završene")
            
            return False, {
                "error": str(e),
                "message": "Transakciona obrada neuspešna - izvršen rollback",
                "saga_log": self.saga_log
            }


class PenalSagaOrchestrator:
    """
    Saga orkestrator za kreiranje penala
    
    Scenario: Kreiranje penala zbog kršenja ugovora
    - Korak 1: Kreiraj penal u Oracle bazi
    - Korak 2: Pošalji događaj u InfluxDB
    - Ako neki korak ne uspe → Rollback
    """
    
    def __init__(self, mikroservis_url: str = "http://localhost:8001"):
        self.mikroservis_url = mikroservis_url
        self.saga_log = []
    
    def log_step(self, step: str, status: str, details: str = ""):
        """Loguje korak Saga transakcije"""
        log_entry = {
            "timestamp": timezone.now().isoformat(),
            "step": step,
            "status": status,
            "details": details
        }
        self.saga_log.append(log_entry)
        logger.info(f"[SAGA-PENAL] {step}: {status} - {details}")
    
    def create_penal_with_sync(
        self,
        ugovor_id: int,
        razlog: str,
        iznos: Decimal
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Saga funkcija: Kreira penal sa sinhronizacijom u InfluxDB
        
        Args:
            ugovor_id: ID ugovora
            razlog: Razlog penala
            iznos: Iznos penala
            
        Returns:
            (success, result_data)
        """
        
        penal = None
        influx_sent = False
        
        self.log_step("SAGA_START", "INFO", "Pokretanje Saga transakcije za penal")
        
        try:
            # ============================================================
            # KORAK 1: Kreiraj penal u Oracle bazi
            # ============================================================
            self.log_step("STEP_1_START", "INFO", "Kreiranje penala u Oracle DB")
            
            with db_transaction.atomic():
                from .models import Penal, Ugovor
                
                try:
                    ugovor = Ugovor.objects.get(sifra_u=ugovor_id)
                except Ugovor.DoesNotExist:
                    self.log_step("STEP_1_FAILED", "ERROR", f"Ugovor {ugovor_id} ne postoji")
                    return False, {
                        "error": "Ugovor ne postoji",
                        "saga_log": self.saga_log
                    }
                
                # Hardkoduj ID - Dobavi MAX(sifra_p) i dodaj 1
                max_penal_id = Penal.objects.aggregate(
                    Max('sifra_p')
                )['sifra_p__max'] or 0
                next_penal_id = max_penal_id + 1
                
                # Kreiraj penal sa eksplicitnim ID-em
                penal = Penal(
                    sifra_p=next_penal_id,
                    razlog_p=razlog,
                    iznos_p=iznos,
                    ugovor=ugovor
                )
                penal.save()
                
                self.log_step(
                    "STEP_1_SUCCESS",
                    "SUCCESS",
                    f"Penal {penal.sifra_p} kreiran u Oracle DB"
                )
            
            # ============================================================
            # KORAK 2: Pošalji događaj u InfluxDB
            # ============================================================
            self.log_step("STEP_2_START", "INFO", "Slanje događaja u InfluxDB")
            
            mikroservis_data = {
                "ugovor_id": ugovor.sifra_u,
                "iznos": float(iznos),
                "razlog": razlog,
                "status": "kreiran"
            }
            
            try:
                response = httpx.post(
                    f"{self.mikroservis_url}/api/dogadjaji/penal",
                    json=mikroservis_data,
                    timeout=10.0
                )
                
                if response.status_code == 201:
                    influx_sent = True
                    self.log_step("STEP_2_SUCCESS", "SUCCESS", "Događaj poslat u InfluxDB")
                else:
                    raise Exception(f"Mikroservis vratio status {response.status_code}")
                    
            except httpx.RequestError as e:
                self.log_step("STEP_2_FAILED", "ERROR", f"HTTP greška: {str(e)}")
                raise Exception(f"Greška pri komunikaciji sa mikroservisom: {str(e)}")
            
            # ============================================================
            # SAGA USPEŠNA
            # ============================================================
            self.log_step("SAGA_SUCCESS", "SUCCESS", "Saga transakcija uspešno završena")
            
            return True, {
                "message": "Penal uspešno kreiran i sinhronizovan",
                "penal_id": penal.sifra_p,
                "influxdb_status": "synced",
                "saga_log": self.saga_log
            }
            
        except Exception as e:
            # ============================================================
            # ROLLBACK
            # ============================================================
            self.log_step("SAGA_FAILED", "ERROR", f"Greška: {str(e)}")
            self.log_step("ROLLBACK_START", "INFO", "Pokretanje rollback-a")
            
            # Obriši penal iz Oracle DB
            if penal:
                try:
                    with db_transaction.atomic():
                        penal.delete()
                        self.log_step("ROLLBACK_STEP_1", "SUCCESS", "Penal obrisan iz Oracle DB")
                except Exception as rollback_error:
                    self.log_step("ROLLBACK_STEP_1", "ERROR", f"Rollback greška: {str(rollback_error)}")
            
            # Pošalji otkazni događaj u InfluxDB
            if influx_sent:
                try:
                    cancel_data = {
                        "ugovor_id": ugovor_id,
                        "iznos": 0.0,
                        "razlog": f"ROLLBACK: {razlog}",
                        "status": "otkazan"
                    }
                    httpx.post(
                        f"{self.mikroservis_url}/api/dogadjaji/penal",
                        json=cancel_data,
                        timeout=5.0
                    )
                    self.log_step("ROLLBACK_STEP_2", "SUCCESS", "Otkazni događaj poslat")
                except Exception as rollback_error:
                    self.log_step("ROLLBACK_STEP_2", "ERROR", f"Rollback greška: {str(rollback_error)}")
            
            self.log_step("ROLLBACK_END", "INFO", "Rollback završen")
            
            return False, {
                "error": str(e),
                "message": "Transakciona obrada neuspešna - izvršen rollback",
                "saga_log": self.saga_log
            }
