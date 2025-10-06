# Sistem za automatsku proveru isteka roka artikala

Ovaj sistem automatski proverava rokove trajanja artikala i kreira popuste za one koji ističu. Sistem radi potpuno automatski u pozadini.

## Funkcionalnosti

### 1. Automatska provera rokova
- **Artikli sa statusom 'aktivan'**: Rok trajanja je više od 7 dana
- **Artikli sa statusom 'istice'**: Rok trajanja je za 7 ili manje dana
- **Artikli sa statusom 'istekao'**: Rok trajanja je već prošao

### 2. Automatsko kreiranje popusta
- Kada se artikal prebaci na status 'istice', kreira se novi popust
- Popust cena je 50% od osnovne cene artikla
- Datum početka važenja: dan kada je status promenjen na 'istice'
- Datum kraja važenja: datum isteka roka trajanja artikla
- Originalna osnovna cena artikla ostaje nepromenjena

## Automatsko pokretanje

Sistem je dizajniran da radi automatski bez ručne intervencije.

### Linux/Unix (cron job)
```bash
# Dodaj u crontab (crontab -e) da se pokreće svaki dan u 6 ujutru
0 6 * * * cd /path/to/project && python manage.py auto_check_expiration

# Ili koristi priloženu skriptu
0 6 * * * /path/to/scripts/auto_check_expiration.sh
```

### Windows (Task Scheduler)
- Koristi `scripts/auto_check_expiration.bat` skriptu
- Podesi Task Scheduler da pokreće skriptu svaki dan u 6 ujutru

### Ručno testiranje (samo za development)
```bash
# Pokretanje sa stvarnim izmenama
python manage.py check_expiration

# Pokretanje bez izmena (dry-run)
python manage.py check_expiration --dry-run

# Automatska komanda (preporučeno za produkciju)
python manage.py auto_check_expiration
```

## Primer izlaza

```
Pokrećem proveru rokova artikala - 2025-10-03
Artikal 5 (Hleb): aktivan → istice
  → Kreiran popust: 120.00 → 60.00 (važeće od 2025-10-03 do 2025-10-10)
Artikal 8 (Mleko): istice → istekao

Uspešno završeno! Promenjeno 2 artikala i kreirano 1 popusta

=== PREGLED STANJA ===
Aktivni artikli: 15
Artikli koji ističu: 3
Istekli artikli: 2
Aktivni popusti: 3
```

## Logovanje

- Logovi se čuvaju u `logs/artikel_expiration_check.log`
- Svako pokretanje se beleži sa timestamp-om
- Greške se takođe loguju za debugging

## Baza podataka

### Izmene u tabeli `artikal`:
- `status_trajanja` se ažurira automatski

### Izmene u tabeli `popust`:
- Kreiraju se novi popusti za artikle koji ističu
- `predlozena_cena_a` = 50% od `osnovna_cena_a`
- `datum_pocetka_vazenja_p` = današnji datum
- `datum_kraja_vazenja_p` = `rok_trajanja_a` iz artikla

## Napomene

- Sistem radi potpuno automatski bez potrebe za ručnom intervencijom
- Sistem ne kreira duplikate popusta za isti artikal u istom periodu
- Osnovna cena artikla se ne menja, samo se kreira zapis u tabeli popust
- Preporučuje se pokretanje jednom dnevno (npr. u 6 ujutru)
- Ideal je za postavljanje kao scheduled task koji radi u pozadini