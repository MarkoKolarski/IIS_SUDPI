"""
TEST SKRIPTA ZA SAGA PATTERN TRANSAKCIONU OBRADU

Testira kreiranje Faktura + Transakcija koristeći Saga pattern orkestraciju.

Preduslovi:
1. Django server mora biti pokrenut (python manage.py runserver)
2. Mikroservis mora biti pokrenut (docker-compose up -d ili python app/main.py)
3. Mora postojati Ugovor u Oracle bazi

Komande:
    python test_saga.py
"""

import httpx
import json
import random
from datetime import datetime, timedelta

# Konfiguracija
DJANGO_URL = "http://localhost:8000"
MIKROSERVIS_URL = "http://localhost:8001"

# Test kredencijali (prilagodi svojim kredencijalima)
TEST_USERNAME = "1@gmail.com"
TEST_PASSWORD = "1Qwertz*"


def get_jwt_token():
    """Dobij JWT token za autentifikaciju"""
    print("\n[1/5] Dobijanje JWT tokena...")
    
    try:
        response = httpx.post(
            f"{DJANGO_URL}/api/login/",
            json={
                "mail_k": TEST_USERNAME,
                "password": TEST_PASSWORD
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print(f"✓ JWT token dobijen: {token[:30]}...")
            return token
        else:
            print(f"✗ Greška pri login-u: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Greška: {str(e)}")
        return None


def test_saga_status():
    """Testira /api/saga/status/ endpoint"""
    print("\n[2/5] Provera Saga status endpointa...")
    
    try:
        response = httpx.get(
            f"{DJANGO_URL}/api/saga/status/",
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Saga pattern aktivan")
            print(f"  Pattern: {data.get('pattern')}")
            print(f"  Mikroservis: {data.get('mikroservis_url')}")
            print(f"  Baze podataka: {len(data.get('baze_podataka', []))}")
            return True
        else:
            print(f"✗ Greška: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Greška: {str(e)}")
        return False


def test_mikroservis_health():
    """Testira da li mikroservis radi"""
    print("\n[3/5] Provera mikroservisa...")
    
    try:
        response = httpx.get(f"{MIKROSERVIS_URL}/health", timeout=5.0)
        
        if response.status_code == 200:
            print(f"✓ Mikroservis je aktivan")
            return True
        else:
            print(f"✗ Mikroservis nije dostupan: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Mikroservis nije dostupan: {str(e)}")
        return False


def test_create_faktura_with_payment(token, ugovor_id=1):
    """Testira kreiranje fakture sa plaćanjem (Saga pattern)"""
    print("\n[4/5] Testiranje Saga transakcije (Faktura + Transakcija)...")
    
    # Pripremi test podatke sa JEDINSTVENOM potvrdnom
    datum_danas = datetime.now().strftime("%Y-%m-%d")
    datum_rok = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Generiši JEDINSTVENU potvrdu (timestamp + mikrosekundne + random broj)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    random_suffix = random.randint(1000, 9999)
    potvrda = f"TEST-SAGA-{timestamp}-{random_suffix}"
    
    test_data = {
        "ugovor_id": ugovor_id,
        "iznos": 250000.00,
        "datum_prijema": datum_danas,
        "rok_placanja": datum_rok,
        "potvrda_transakcije": potvrda,
        "status_transakcije": "uspesna"
    }
    
    print(f"  Test podaci:")
    print(f"    - Ugovor ID: {test_data['ugovor_id']}")
    print(f"    - Iznos: {test_data['iznos']} RSD")
    print(f"    - Potvrda: {test_data['potvrda_transakcije']}")
    
    try:
        response = httpx.post(
            f"{DJANGO_URL}/api/saga/faktura-sa-placanjem/",
            json=test_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0
        )
        
        print(f"\n  Status kod: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ SAGA TRANSAKCIJA USPEŠNA!")
            print(f"\n  Rezultat:")
            print(f"    - Faktura ID: {data['data']['faktura_id']}")
            print(f"    - Transakcija ID: {data['data']['transakcija_id']}")
            print(f"    - InfluxDB status: {data['data']['influxdb_status']}")
            print(f"\n  Saga log ({len(data['saga_log'])} koraka):")
            for i, log in enumerate(data['saga_log'], 1):
                print(f"    {i}. {log}")
            return True
            
        elif response.status_code == 500:
            data = response.json()
            print(f"✗ SAGA TRANSAKCIJA NEUSPEŠNA - Izvršen rollback")
            print(f"\n  Greška: {data.get('error')}")
            print(f"\n  Saga log ({len(data.get('saga_log', []))} koraka):")
            for i, log in enumerate(data.get('saga_log', []), 1):
                print(f"    {i}. {log}")
            return False
            
        else:
            print(f"✗ Neočekivani status kod: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Greška: {str(e)}")
        return False


def test_create_penal(token, ugovor_id=1):
    """Testira kreiranje penala (Saga pattern)"""
    print("\n[5/5] Testiranje Saga transakcije (Penal)...")
    
    test_data = {
        "ugovor_id": ugovor_id,
        "razlog": "TEST - Kašnjenje u isporuci robe",
        "iznos": 50000.00
    }
    
    print(f"  Test podaci:")
    print(f"    - Ugovor ID: {test_data['ugovor_id']}")
    print(f"    - Iznos: {test_data['iznos']} RSD")
    print(f"    - Razlog: {test_data['razlog']}")
    
    try:
        response = httpx.post(
            f"{DJANGO_URL}/api/saga/penal/",
            json=test_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0
        )
        
        print(f"\n  Status kod: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ SAGA TRANSAKCIJA USPEŠNA!")
            print(f"\n  Rezultat:")
            print(f"    - Penal ID: {data['data']['penal_id']}")
            print(f"    - InfluxDB status: {data['data']['influxdb_status']}")
            print(f"\n  Saga log ({len(data['saga_log'])} koraka):")
            for i, log in enumerate(data['saga_log'], 1):
                print(f"    {i}. {log}")
            return True
            
        elif response.status_code == 500:
            data = response.json()
            print(f"✗ SAGA TRANSAKCIJA NEUSPEŠNA - Izvršen rollback")
            print(f"\n  Greška: {data.get('error')}")
            return False
            
        else:
            print(f"✗ Neočekivani status kod: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Greška: {str(e)}")
        return False


def main():
    """Glavna test funkcija"""
    print("=" * 70)
    print("TESTIRANJE SAGA PATTERN TRANSAKCIONE OBRADE PODATAKA")
    print("=" * 70)
    print("\nOrkestracija između Oracle DB (Django) i InfluxDB (Mikroservis)")
    
    # 1. Dobij JWT token
    token = get_jwt_token()
    if not token:
        print("\n✗ Test neuspešan - nema JWT tokena")
        print("\nProveri:")
        print("  1. Da li je Django server pokrenut? (python manage.py runserver)")
        print("  2. Da li kredencijali u TEST_USERNAME/TEST_PASSWORD važe?")
        return
    
    # 2. Proveri Saga status
    if not test_saga_status():
        print("\n✗ Test neuspešan - Saga status nije dostupan")
        return
    
    # 3. Proveri mikroservis
    if not test_mikroservis_health():
        print("\n✗ Test neuspešan - Mikroservis nije dostupan")
        print("\nProveri:")
        print("  1. Da li je mikroservis pokrenut? (cd back/FinancialEventsAnalysisService && docker-compose up -d)")
        print("  2. Da li je InfluxDB dostupan na localhost:8086?")
        return
    
    # 4. Testiraj Saga transakciju (Faktura + Transakcija)
    success_faktura = test_create_faktura_with_payment(token, ugovor_id=1)
    
    # 5. Testiraj Saga transakciju (Penal)
    success_penal = test_create_penal(token, ugovor_id=1)
    
    # Finalni rezultat
    print("\n" + "=" * 70)
    print("REZULTATI TESTIRANJA")
    print("=" * 70)
    
    if success_faktura and success_penal:
        print("\n✓✓✓ SVI TESTOVI USPEŠNI ✓✓✓")
        print("\nSaga pattern funkcioniše ispravno!")
        print("Podaci su uspešno upisani u obe baze (Oracle + InfluxDB)")
    else:
        print("\n✗ NEKI TESTOVI NISU PROŠLI")
        print(f"  - Faktura + Transakcija: {'✓' if success_faktura else '✗'}")
        print(f"  - Penal: {'✓' if success_penal else '✗'}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
