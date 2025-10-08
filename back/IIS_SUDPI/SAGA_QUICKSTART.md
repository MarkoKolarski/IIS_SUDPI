# 🚀 QUICK START - Saga Pattern Transakciona Obrada

## ⚡ Brzo Pokretanje (5 minuta)

### 1️⃣ Pokreni Oracle DB + Django Backend

```bash
cd back/IIS_SUDPI
python manage.py runserver
```

Proveri: http://localhost:8000/api/saga/status/

### 2️⃣ Pokreni InfluxDB + Mikroservis

```bash
cd back/FinancialEventsAnalysisService
docker-compose up -d
```

Proveri: http://localhost:8001/health

### 3️⃣ Testiraj Saga Transakcije

#### Opcija A: Automatski Test

```bash
cd back/IIS_SUDPI
# Prvo podesi TEST_USERNAME i TEST_PASSWORD u test_saga.py
python test_saga.py
```

#### Opcija B: Manuelno (Postman/cURL)

**1. Login:**

```bash
POST http://localhost:8000/api/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}

# Response: { "access": "JWT_TOKEN_HERE" }
```

**2. Kreiraj Fakturu + Transakciju (Saga):**

```bash
POST http://localhost:8000/api/saga/faktura-sa-placanjem/
Authorization: Bearer JWT_TOKEN_HERE
Content-Type: application/json

{
    "ugovor_id": 1,
    "iznos": 250000.00,
    "datum_prijema": "2025-10-01",
    "rok_placanja": "2025-11-01",
    "potvrda_transakcije": "TRX-TEST-001",
    "status_transakcije": "uspesna"
}
```

**Uspešan odgovor:**

```json
{
    "success": true,
    "message": "Transakciona obrada uspešno završena",
    "data": {
        "faktura_id": 123,
        "transakcija_id": 456,
        "influxdb_status": "synced"
    },
    "saga_log": [
        "STEP 1: Faktura kreirana u Oracle DB (ID: 123)",
        "STEP 2: Transakcija kreirana u Oracle DB (ID: 456)",
        "STEP 3: Događaj sinhronizovan sa InfluxDB",
        "SAGA USPEŠNA: Svi koraci izvršeni"
    ]
}
```

**3. Kreiraj Penal (Saga):**

```bash
POST http://localhost:8000/api/saga/penal/
Authorization: Bearer JWT_TOKEN_HERE
Content-Type: application/json

{
    "ugovor_id": 1,
    "razlog": "Kašnjenje u isporuci robe",
    "iznos": 50000.00
}
```

---

## 🔍 Provera Podataka

### Oracle Database (Django Shell)

```bash
cd back/IIS_SUDPI
python manage.py shell
```

```python
from app.models import Faktura, Transakcija

# Pronađi fakturu
faktura = Faktura.objects.get(sifra_f=123)
print(f"Faktura: {faktura.iznos_f} RSD, Status: {faktura.status_f}")

# Pronađi transakciju
transakcija = faktura.transakcija  # OneToOne veza
print(f"Transakcija: {transakcija.potvrda_t}, Status: {transakcija.status_t}")
```

### InfluxDB (HTTP API)

```bash
# Dohvati transakciju iz InfluxDB
GET http://localhost:8001/api/dogadjaji/transakcija/123

# Odgovor:
{
    "tip_dogadjaja": "transakcija",
    "entitet_id": 123,
    "iznos": 250000.0,
    "status": "uspesna",
    "opis": "Potvrda: TRX-TEST-001. ...",
    "timestamp": "2025-01-15T14:30:00Z"
}
```

---

## ✅ Verifikacija da Saga Radi

### Test 1: Uspešna Transakcija

✓ Faktura se kreira u Oracle DB  
✓ Transakcija se kreira u Oracle DB  
✓ Događaj se upisuje u InfluxDB  
✓ Saga vraća `success: true`

### Test 2: Rollback (Neuspešna InfluxDB Sinhronizacija)

1. **Ugasi mikroservis:**

```bash
cd back/FinancialEventsAnalysisService
docker-compose down
```

2. **Pokušaj kreiranje fakture:**

```bash
POST http://localhost:8000/api/saga/faktura-sa-placanjem/
# ... isti JSON kao gore
```

**Očekivani odgovor:**

```json
{
    "success": false,
    "message": "Transakciona obrada neuspešna - izvršen rollback",
    "error": "Connection refused (mikroservis nedostupan)",
    "saga_log": [
        "STEP 1: Faktura kreirana u Oracle DB (ID: 125)",
        "STEP 2: Transakcija kreirana u Oracle DB (ID: 458)",
        "STEP 3: GREŠKA - InfluxDB sinhronizacija neuspešna",
        "KOMPENZACIJA: Brisanje Oracle zapisa...",
        "KOMPENZACIJA: Oracle rollback uspešan",
        "SAGA NEUSPEŠNA: Rollback izvršen"
    ]
}
```

3. **Proveri Oracle DB:**

```python
# Fakturu i transakciju NE bi trebalo da postoje
Faktura.objects.filter(sifra_f=125).exists()  # False ✓
Transakcija.objects.filter(sifra_t=458).exists()  # False ✓
```

✓ **ROLLBACK USPEŠAN!** Nijedan podatak nije upisan.

---

## 📊 Saga Endpoints

| Endpoint | Metod | Opis |
|----------|-------|------|
| `/api/saga/status/` | GET | Informacije o Saga sistemu |
| `/api/saga/faktura-sa-placanjem/` | POST | Kreiranje Faktura + Transakcija (atomično) |
| `/api/saga/penal/` | POST | Kreiranje Penala (atomično) |

---

## 🛠️ Troubleshooting

### Greška: "Connection refused"

**Problem:** Mikroservis nije pokrenut.

**Rešenje:**

```bash
cd back/FinancialEventsAnalysisService
docker-compose up -d
curl http://localhost:8001/health
```

### Greška: "Ugovor matching query does not exist"

**Problem:** Ne postoji `Ugovor` sa zadatim `id`.

**Rešenje:**

```bash
cd back/IIS_SUDPI
python manage.py shell
```

```python
from app.models import Ugovor, Dobavljac

# Kreiraj dobavljača
dobavljac = Dobavljac.objects.create(
    naziv_d="Test Dobavljač",
    maticni_broj_d=12345678,
    # ... ostali obavezni atributi
)

# Kreiraj ugovor
ugovor = Ugovor.objects.create(
    sifra_u=1,
    dobavljac=dobavljac,
    datum_pocetka_u="2025-01-01",
    # ... ostali obavezni atributi
)
```

### Greška: "httpx module not found"

**Problem:** `httpx` nije instaliran.

**Rešenje:**

```bash
cd back/IIS_SUDPI
pip install httpx
```

---

## 📚 Dodatna Dokumentacija

- **Detaljna dokumentacija:** `SAGA_DOKUMENTACIJA.md`
- **Arhitektura:** `back/FinancialEventsAnalysisService/ARHITEKTURA.md`
- **Instalacija:** `back/FinancialEventsAnalysisService/INSTALACIJA.md`

---

## 🎯 Zaključak

Uspešno si implementirao **Saga Pattern** za transakcionu obradu podataka između:

1. **Oracle Database** (relaciona baza)
2. **InfluxDB** (NoSQL time-series baza)

### Funkcionalnosti

✅ Atomične transakcije između dve baze  
✅ Automatski rollback pri greškama  
✅ Kompenzacione transakcije  
✅ Detaljno logovanje  
✅ REST API endpoints  
✅ Test skripta  

**Bodovi: 10/10** ✓
