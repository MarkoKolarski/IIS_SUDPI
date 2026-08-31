-- ============================================
-- ORACLE INSERT SKRIPTA ZA FINANSIJSKI SISTEM
-- Ekstenzija fajla: .sql
-- DRUGA ITERACIJA (avgust 2026): usklađeno sa suženim EER-om isključivo za
-- finansijsko-analitički podsistem (dobavljači, katalog/cenovnik, ugovori/
-- penali, fakture/stavke, transakcije, izveštavanje, kontrolna tabla).
-- Skup podataka je namerno kompaktniji nego u prvoj iteraciji (manje
-- istorijskih/volume-testing redova) - dovoljan da pokrije kontrolnu tablu,
-- listu/detalje faktura, simulaciju plaćanja, izveštaje i penale, bez
-- nepotrebnog obima. notifikacija/se_salje su nepromenjeni pa su preneti
-- neizmenjeni sa prethodne verzije.
-- ============================================

-- Brisanje postojećih podataka (opcionalno) - redosled poštuje FK zavisnosti
-- DELETE FROM se_salje;
-- DELETE FROM notifikacija;
-- DELETE FROM predmet_izvestaja;
-- DELETE FROM ocena_dobavljaca;
-- DELETE FROM merenje;
-- DELETE FROM prikazuje;
-- DELETE FROM izvestaj;
-- DELETE FROM kreiranje;
-- DELETE FROM kontrolna_tabla;
-- DELETE FROM metrika;
-- DELETE FROM promena_statusa;
-- DELETE FROM transakcija;
-- DELETE FROM racun;
-- DELETE FROM stavka_fakture;
-- DELETE FROM cenovnik;
-- DELETE FROM proizvod_dobavljaca;
-- DELETE FROM proizvod;
-- DELETE FROM kategorija_proizvoda;
-- DELETE FROM faktura;
-- DELETE FROM penal;
-- DELETE FROM ugovor;
-- DELETE FROM dobavljac;
-- DELETE FROM valuta;
-- DELETE FROM jedinica_mere;
-- DELETE FROM finansijski_analiticar;
-- DELETE FROM korisnik;

-- ============================================
-- 1. KORISNIK (Finansijski analitičar)
-- ============================================

INSERT INTO korisnik (sifra_k, ime_k, prz_k, mail_k, tip_k, username, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
VALUES (1, 'Marko', 'Marković', 'marko.markovic@firma.rs', 'finansijski_analiticar', 'marko.markovic@firma.rs', 'pbkdf2_sha256$260000$abc123', 0, 1, 1, SYSTIMESTAMP, 'Marko', 'Marković');

INSERT INTO korisnik (sifra_k, ime_k, prz_k, mail_k, tip_k, username, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
VALUES (2, 'Ana', 'Petrović', 'ana.petrovic@firma.rs', 'finansijski_analiticar', 'ana.petrovic@firma.rs', 'pbkdf2_sha256$260000$def456', 0, 1, 1, SYSTIMESTAMP, 'Ana', 'Petrović');

INSERT INTO korisnik (sifra_k, ime_k, prz_k, mail_k, tip_k, username, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
VALUES (3, 'Jovan', 'Nikolić', 'jovan.nikolic@firma.rs', 'finansijski_analiticar', 'jovan.nikolic@firma.rs', 'pbkdf2_sha256$260000$ghi789', 0, 1, 1, SYSTIMESTAMP, 'Jovan', 'Nikolić');

INSERT INTO korisnik (sifra_k, ime_k, prz_k, mail_k, tip_k, username, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name)
VALUES (4, 'Marko', 'Marković', '1@gmail.com', 'finansijski_analiticar', '1@gmail.com', 'pbkdf2_sha256$870000$BH9seZyFDVYcXNrepOiBDg$2Jx9Y8SO2ow7ZZLzNfhd5ziUfAsJfELZgIGjDgovChc=', 0, 1, 1, SYSTIMESTAMP, 'Marko', 'Marković');

-- ============================================
-- 2. FINANSIJSKI ANALITIČAR (PK je direktno sifra_k korisnika - ER arc)
-- ============================================

INSERT INTO finansijski_analiticar (sifra_k) VALUES (1);
INSERT INTO finansijski_analiticar (sifra_k) VALUES (2);
INSERT INTO finansijski_analiticar (sifra_k) VALUES (3);
INSERT INTO finansijski_analiticar (sifra_k) VALUES (4);

-- ============================================
-- 3. JEDINICA_MERE (šifarnik količinskih jedinica - koriste je Proizvod i
-- Metrika; NOVAC red je i dalje jedinica mere novčanih KPI-ja/Metrika, ali
-- više NIJE valuta dokumenata - vidi VALUTA ispod, Peta iteracija)
-- ============================================

INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (1, 'Srpski dinar', 'RSD', 'NOVAC');
INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (2, 'Evro', 'EUR', 'NOVAC');
INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (3, 'Komad', 'kom', 'KOLICINA');
INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (4, 'Kilogram', 'kg', 'MASA');
INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (5, 'Dan', 'dan', 'VREME');
INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (6, 'Procenat', '%', 'PROCENAT');
INSERT INTO jedinica_mere (sifra_jm, naziv_jm, oznaka_jm, tip_jm) VALUES (7, 'Litar', 'l', 'ZAPREMINA');

-- ============================================
-- 3a. VALUTA (Peta iteracija - izdvojena iz JEDINICA_MERE u zaseban TE;
-- koriste je Faktura, Cenovnik i Racun)
-- ============================================

INSERT INTO valuta (sifra_v, naziv_v, oznaka_v) VALUES (1, 'Srpski dinar', 'RSD');
INSERT INTO valuta (sifra_v, naziv_v, oznaka_v) VALUES (2, 'Evro', 'EUR');

-- ============================================
-- 4. DOBAVLJAČ
-- ============================================

INSERT INTO dobavljac (sifra_db, naziv_db, email_db, pib_db, ime_sirovine, cena, rok_isporuke, ocena_db, datum_ocenjivanja, izabran)
VALUES (1, 'Agro Invest DOO', 'salebecej1@gmail.com', '123456789', 'Pšenično brašno tip 500', 85.50, 5, 7.20, TO_DATE('2026-09-15', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_db, naziv_db, email_db, pib_db, ime_sirovine, cena, rok_isporuke, ocena_db, datum_ocenjivanja, izabran)
VALUES (2, 'Mlekoprodukt AD', 'salebecej1@gmail.com', '987654321', 'UHT mleko 3.2%', 125.00, 3, 9.50, TO_DATE('2026-09-20', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_db, naziv_db, email_db, pib_db, ime_sirovine, cena, rok_isporuke, ocena_db, datum_ocenjivanja, izabran)
VALUES (3, 'Voće Srbija DOO', 'salebecej1@gmail.com', '456789123', 'Jabuke Idared', 65.00, 2, 8.80, TO_DATE('2026-09-10', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_db, naziv_db, email_db, pib_db, ime_sirovine, cena, rok_isporuke, ocena_db, datum_ocenjivanja, izabran)
VALUES (4, 'Hemija Sever DOO', 'salebecej1@gmail.com', '789123456', 'Natrijum benzoat', 450.00, 7, 9.10, TO_DATE('2026-08-25', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_db, naziv_db, email_db, pib_db, ime_sirovine, cena, rok_isporuke, ocena_db, datum_ocenjivanja, izabran)
VALUES (5, 'Šećerana Crvenka', 'salebecej1@gmail.com', '321654987', 'Kristal šećer', 95.00, 4, 9.00, TO_DATE('2026-09-18', 'YYYY-MM-DD'), 1);

-- ============================================
-- 5. KATEGORIJA PROIZVODA (limit_kp uklonjen - ER)
-- ============================================

INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp) VALUES (1, 'Mlinarski proizvodi');
INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp) VALUES (2, 'Mlečni proizvodi');
INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp) VALUES (3, 'Voće i povrće');
INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp) VALUES (4, 'Hemikalije i aditivi');
INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp) VALUES (5, 'Šećer i zaslađivači');

-- ============================================
-- 6. PROIZVOD (Peta iteracija: pdv_stopa_pr uklonjen - PDV je premešten na
-- STAVKA_FAKTURE, vidi sekciju 12; dodato jedinica_mere_sifra_jm)
-- ============================================

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (1, 'Pšenično brašno T-500', 'Visokokvalitetno pšenično brašno tip 500 za industriju', 1, 4);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (2, 'Integralno brašno', 'Brašno od celih zrna pšenice, bogato vlaknima', 1, 4);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (3, 'UHT mleko 3.2%', 'Trajno mleko sa 3.2% mlečne masti', 2, 7);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (4, 'Pavlaka 20%', 'Pavlaka za kuvanje sa 20% mlečne masti', 2, 7);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (5, 'Jabuke Idared I klasa', 'Sveže jabuke sorte Idared, prva klasa kvaliteta', 3, 4);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (6, 'Natrijum benzoat E211', 'Konzervans za produženje roka trajanja proizvoda', 4, 4);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_proizvoda_sifra_kp, jedinica_mere_sifra_jm)
VALUES (7, 'Kristal šećer', 'Rafinirani beli kristal šećer', 5, 4);

-- ============================================
-- 7. PROIZVOD_DOBAVLJACA (gerund "nudi" - kataloška stavka dobavljača)
-- ============================================

INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (1, 1, 1, 'AGR-001');
INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (2, 1, 2, 'AGR-002');
INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (3, 2, 3, 'MLK-001');
INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (4, 2, 4, 'MLK-002');
INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (5, 3, 5, 'VOC-001');
INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (6, 4, 6, 'HEM-001');
INSERT INTO proizvod_dobavljaca (id, dobavljac_sifra_db, proizvod_sifra_pr, sifra_kod_dobavljaca_pd) VALUES (7, 5, 7, 'SEC-001');

-- ============================================
-- 8. CENOVNIK (ugovorena neto cena po kataloškoj stavci - trenutno važeća;
-- Peta iteracija: jedinica_mere_sifra_jm -> valuta_sifra_v)
-- ============================================

INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (1, 85.50, TO_DATE('2026-01-10', 'YYYY-MM-DD'), NULL, 1, 1);
INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (2, 95.00, TO_DATE('2025-08-01', 'YYYY-MM-DD'), NULL, 2, 1);
INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (3, 125.00, TO_DATE('2026-02-15', 'YYYY-MM-DD'), NULL, 3, 1);
INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (4, 180.00, TO_DATE('2026-01-20', 'YYYY-MM-DD'), NULL, 4, 1);
INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (5, 65.00, TO_DATE('2025-10-01', 'YYYY-MM-DD'), NULL, 5, 1);
INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (6, 450.00, TO_DATE('2025-05-20', 'YYYY-MM-DD'), NULL, 6, 1);
INSERT INTO cenovnik (sifra_c, cena_c, datum_od_c, datum_do_c, proizvod_dobavljaca_id, valuta_sifra_v) VALUES (7, 95.00, TO_DATE('2026-01-15', 'YYYY-MM-DD'), NULL, 7, 1);

-- ============================================
-- 9. UGOVOR (status_u: 'otkazan' -> 'raskinut'; dodato 201/202 za auto-penal demo)
-- ============================================

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (1, TO_DATE('2026-01-10', 'YYYY-MM-DD'), TO_DATE('2027-01-10', 'YYYY-MM-DD'), 'aktivan',
'Isporuka brašna u količini min 1000kg mesečno. Cena fiksna za prvih 6 meseci. Rok plaćanja 30 dana.', 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (2, TO_DATE('2026-02-15', 'YYYY-MM-DD'), TO_DATE('2027-02-15', 'YYYY-MM-DD'), 'aktivan',
'Isporuka UHT mleka 2x nedeljno. Minimalna količina 500L po isporuci. Rok plaćanja 15 dana.', 2);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (3, TO_DATE('2025-10-01', 'YYYY-MM-DD'), TO_DATE('2026-10-01', 'YYYY-MM-DD'), 'aktivan',
'Sezonska isporuka voća. Kvalitet mora biti I klasa. Rok plaćanja 45 dana.', 3);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (4, TO_DATE('2025-05-20', 'YYYY-MM-DD'), TO_DATE('2026-05-20', 'YYYY-MM-DD'), 'istekao',
'Isporuka hemikalija sa sertifikatima. Plaćanje avansno 50%.', 4);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (5, TO_DATE('2026-03-01', 'YYYY-MM-DD'), TO_DATE('2026-09-01', 'YYYY-MM-DD'), 'raskinut',
'Isporuka šećera - ugovor raskinut zbog kašnjenja u isporuci.', 5);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (6, TO_DATE('2025-08-01', 'YYYY-MM-DD'), TO_DATE('2026-08-01', 'YYYY-MM-DD'), 'aktivan',
'Prošireni ugovor za isporuku integralnog brašna. Minimalna količina 200kg mesečno. Rok plaćanja 30 dana.', 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (7, TO_DATE('2026-01-20', 'YYYY-MM-DD'), TO_DATE('2027-01-20', 'YYYY-MM-DD'), 'aktivan',
'Dodatni ugovor za isporuku pavlake i drugih mlečnih derivata. Isporuka 1x nedeljno. Rok plaćanja 15 dana.', 2);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (8, TO_DATE('2026-06-01', 'YYYY-MM-DD'), TO_DATE('2027-06-01', 'YYYY-MM-DD'), 'aktivan',
'Obnovljeni sezonski ugovor za isporuku voća - povećane količine. Kvalitet I klasa. Rok plaćanja 45 dana.', 3);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (9, TO_DATE('2026-01-15', 'YYYY-MM-DD'), TO_DATE('2027-01-15', 'YYYY-MM-DD'), 'aktivan',
'Godišnji ugovor za isporuku kristal šećera. Mesečne isporuke 1000-2000kg. Cena fiksna. Rok plaćanja 30 dana.', 5);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (10, TO_DATE('2026-06-01', 'YYYY-MM-DD'), TO_DATE('2027-06-01', 'YYYY-MM-DD'), 'aktivan',
'Obnovljeni ugovor za isporuku hemikalija i aditiva. Svi proizvodi sa sertifikatima. Rok plaćanja 30 dana.', 4);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (11, TO_DATE('2025-06-15', 'YYYY-MM-DD'), TO_DATE('2026-06-15', 'YYYY-MM-DD'), 'aktivan',
'Specijalni ugovor za industrijske količine brašna. Isporuka 2x mesečno. Rok plaćanja 30 dana.', 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (12, TO_DATE('2026-04-01', 'YYYY-MM-DD'), TO_DATE('2026-12-31', 'YYYY-MM-DD'), 'aktivan',
'Sezonski ugovor za prolećnu/letnju sezonu. Povećane količine. Rok plaćanja 30 dana.', 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (13, TO_DATE('2025-12-01', 'YYYY-MM-DD'), TO_DATE('2026-11-30', 'YYYY-MM-DD'), 'aktivan',
'Zimski ugovor za isporuku konzerviranog voća. Rok plaćanja 45 dana.', 3);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (14, TO_DATE('2026-02-01', 'YYYY-MM-DD'), TO_DATE('2027-02-01', 'YYYY-MM-DD'), 'aktivan',
'Specijalni ugovor za fin šećer u prahu. Mesečne isporuke. Rok plaćanja 30 dana.', 5);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (15, TO_DATE('2026-07-01', 'YYYY-MM-DD'), TO_DATE('2027-07-01', 'YYYY-MM-DD'), 'aktivan',
'Industrijski ugovor za velike količine šećera. Kvartalne isporuke. Rok plaćanja 30 dana.', 5);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (16, TO_DATE('2025-11-01', 'YYYY-MM-DD'), TO_DATE('2026-10-31', 'YYYY-MM-DD'), 'aktivan',
'Rezervni ugovor za hitne isporuke šećera. Po potrebi. Rok plaćanja 15 dana.', 5);

-- Namerno "aktivan" a datum_isteka_u u prošlosti - da endpoint penalties/auto-create/
-- ima šta da penalizuje na klik (kršenje "istek ugovora").
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (201, TO_DATE('2024-07-01', 'YYYY-MM-DD'), TO_DATE('2025-07-01', 'YYYY-MM-DD'), 'aktivan',
'Mesečna isporuka brašna, obavezna kompletna dokumentacija i kvalitet I klase.', 2);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_sifra_db)
VALUES (202, TO_DATE('2024-12-15', 'YYYY-MM-DD'), TO_DATE('2025-12-15', 'YYYY-MM-DD'), 'aktivan',
'Nedeljne isporuke voća, rok plaćanja 15 dana i stroga kontrola kvaliteta.', 3);

-- ============================================
-- 10. PENAL (tip_penala_p dodat; Peta iteracija: dodato faktura_sifra_f -
-- opciona veza nastao_zbog. NULL za KASNJENJE_ISPORUKE/KVALITET/OSTALO (nemaju
-- fakturu); popunjeno za KASNJENJE_PLACANJA (penal 7 - konkretna faktura zbog
-- koje je penal nastao).
-- ============================================

-- AGRO INVEST - 4 PENALA na 3 od 4 ugovora (75% stopa kršenja)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (1, 'Nedostajuća dokumentacija - sertifikat kvaliteta', 8500.00, TO_DATE('2025-11-15', 'YYYY-MM-DD'), 'KVALITET', 1, NULL);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (2, 'Isporučena količina manja od ugovorene (850kg umesto 1000kg)', 12000.00, TO_DATE('2026-03-05', 'YYYY-MM-DD'), 'OSTALO', 1, NULL);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (3, 'Kašnjenje u isporuci od 3 dana', 9000.00, TO_DATE('2026-02-20', 'YYYY-MM-DD'), 'KASNJENJE_ISPORUKE', 6, NULL);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (4, 'Kvalitet brašna ispod standarda - vraćena pošiljka', 15500.00, TO_DATE('2026-01-25', 'YYYY-MM-DD'), 'KVALITET', 12, NULL);

-- VOĆE SRBIJA - 1 PENAL na 1 od 3 ugovora (33% stopa kršenja)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (5, 'Kašnjenje u isporuci od 2 dana', 7500.00, TO_DATE('2026-03-10', 'YYYY-MM-DD'), 'KASNJENJE_ISPORUKE', 3, NULL);

-- ŠEĆERANA CRVENKA - 2 PENALA na 1 od 5 ugovora (penal 7, tip KASNJENJE_PLACANJA,
-- je dodat niže, u sekciji 11a - referencira FAKTURA, koja se tek zasejava u
-- sekciji 11, ispod)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (6, 'Ekstremno kašnjenje u isporuci od 14 dana + nekompletna dokumentacija', 25000.00, TO_DATE('2025-12-20', 'YYYY-MM-DD'), 'KASNJENJE_ISPORUKE', 5, NULL);

-- ============================================
-- 11. FAKTURA (razlog_cekanja_f uklonjen - vidi PROMENA_STATUSA;
-- Peta iteracija: jedinica_mere_sifra_jm -> valuta_sifra_v, sve u RSD)
-- ============================================

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (1, 85500.00, TO_DATE('2026-03-05', 'YYYY-MM-DD'), TO_DATE('2026-04-05', 'YYYY-MM-DD'), 'verifikovana', 1, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (2, 62500.00, TO_DATE('2026-03-02', 'YYYY-MM-DD'), TO_DATE('2026-03-17', 'YYYY-MM-DD'), 'isplacena', 2, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (3, 32500.00, TO_DATE('2026-03-18', 'YYYY-MM-DD'), TO_DATE('2026-03-29', 'YYYY-MM-DD'), 'primljena', 3, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (4, 22500.00, TO_DATE('2026-02-10', 'YYYY-MM-DD'), TO_DATE('2026-03-12', 'YYYY-MM-DD'), 'verifikovana', 4, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (5, 47500.00, TO_DATE('2026-03-22', 'YYYY-MM-DD'), TO_DATE('2026-04-18', 'YYYY-MM-DD'), 'primljena', 5, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (6, 125000.00, TO_DATE('2026-02-25', 'YYYY-MM-DD'), TO_DATE('2026-03-15', 'YYYY-MM-DD'), 'isplacena', 2, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (7, 15750.00, TO_DATE('2026-01-20', 'YYYY-MM-DD'), TO_DATE('2026-02-20', 'YYYY-MM-DD'), 'odbijena', 3, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (8, 39000.00, TO_DATE('2026-01-08', 'YYYY-MM-DD'), TO_DATE('2026-02-19', 'YYYY-MM-DD'), 'isplacena', 8, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (9, 45500.00, TO_DATE('2025-12-20', 'YYYY-MM-DD'), TO_DATE('2026-02-04', 'YYYY-MM-DD'), 'isplacena', 8, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (10, 95000.00, TO_DATE('2025-10-15', 'YYYY-MM-DD'), TO_DATE('2025-11-14', 'YYYY-MM-DD'), 'isplacena', 9, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (11, 142500.00, TO_DATE('2025-11-10', 'YYYY-MM-DD'), TO_DATE('2025-12-10', 'YYYY-MM-DD'), 'isplacena', 9, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (12, 190000.00, TO_DATE('2025-12-05', 'YYYY-MM-DD'), TO_DATE('2026-01-04', 'YYYY-MM-DD'), 'isplacena', 9, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (13, 118750.00, TO_DATE('2026-01-12', 'YYYY-MM-DD'), TO_DATE('2026-02-12', 'YYYY-MM-DD'), 'isplacena', 9, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (14, 95000.00, TO_DATE('2026-02-10', 'YYYY-MM-DD'), TO_DATE('2026-03-12', 'YYYY-MM-DD'), 'isplacena', 11, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (15, 110000.00, TO_DATE('2026-03-04', 'YYYY-MM-DD'), TO_DATE('2026-04-03', 'YYYY-MM-DD'), 'isplacena', 11, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (16, 87500.00, TO_DATE('2026-03-16', 'YYYY-MM-DD'), TO_DATE('2026-04-15', 'YYYY-MM-DD'), 'isplacena', 6, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (17, 102000.00, TO_DATE('2026-02-22', 'YYYY-MM-DD'), TO_DATE('2026-03-24', 'YYYY-MM-DD'), 'isplacena', 12, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (18, 52000.00, TO_DATE('2026-01-15', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 'isplacena', 13, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (19, 76000.00, TO_DATE('2026-03-10', 'YYYY-MM-DD'), TO_DATE('2026-04-09', 'YYYY-MM-DD'), 'isplacena', 14, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (20, 285000.00, TO_DATE('2025-12-15', 'YYYY-MM-DD'), TO_DATE('2026-01-14', 'YYYY-MM-DD'), 'isplacena', 15, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (21, 47500.00, TO_DATE('2026-02-03', 'YYYY-MM-DD'), TO_DATE('2026-02-18', 'YYYY-MM-DD'), 'isplacena', 16, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (23, 94050.00, TO_DATE('2026-03-03', 'YYYY-MM-DD'), TO_DATE('2026-04-02', 'YYYY-MM-DD'), 'isplacena', 1, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (24, 80500.00, TO_DATE('2026-03-05', 'YYYY-MM-DD'), TO_DATE('2026-03-20', 'YYYY-MM-DD'), 'isplacena', 2, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (25, 52000.00, TO_DATE('2026-02-08', 'YYYY-MM-DD'), TO_DATE('2026-03-22', 'YYYY-MM-DD'), 'isplacena', 8, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (26, 166250.00, TO_DATE('2026-01-10', 'YYYY-MM-DD'), TO_DATE('2026-02-09', 'YYYY-MM-DD'), 'isplacena', 9, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (27, 76000.00, TO_DATE('2025-12-12', 'YYYY-MM-DD'), TO_DATE('2026-01-11', 'YYYY-MM-DD'), 'isplacena', 6, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, ugovor_sifra_u, valuta_sifra_v)
VALUES (28, 36000.00, TO_DATE('2026-04-15', 'YYYY-MM-DD'), TO_DATE('2026-04-30', 'YYYY-MM-DD'), 'isplacena', 7, 1);

-- ============================================
-- 11a. PENAL nastao_zbog (Peta iteracija - dodato tek ovde, posle FAKTURA,
-- jer penal 7 referencira konkretnu fakturu preko nove veze nastao_zbog;
-- faktura 5 je i dalje 'primljena', a rok_placanja_f joj je odavno prošao)
-- ============================================

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, tip_penala_p, ugovor_sifra_u, faktura_sifra_f)
VALUES (7, 'Ugovorna kazna zbog kašnjenja u plaćanju fakture preko dogovorenog roka', 5000.00, TO_DATE('2026-05-20', 'YYYY-MM-DD'), 'KASNJENJE_PLACANJA', 5, 5);

-- ============================================
-- 12. STAVKA FAKTURE (Peta iteracija: proizvod_dobavljaca_id -> cenovnik_sifra_c
-- - veza naplaćena_po; dodato pdv_stopa_sf, premešteno sa PROIZVOD).
-- cenovnik_sifra_c ovde poklapa proizvod_dobavljaca_id iz prethodne iteracije
-- 1:1 (CENOVNIK je zasejan po jedan red po kataloškoj stavci, sa istom šifrom).
-- ============================================

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (1, 'Pšenično brašno T-500', 1000, 85.50, 10, 'Mesečna isporuka', 1, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (2, 'UHT mleko 3.2%', 500, 125.00, 10, 'Nedeljna isporuka 1', 2, 3);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (3, 'Jabuke Idared I klasa', 500, 65.00, 10, 'Sezonska isporuka', 3, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (4, 'Natrijum benzoat E211', 50, 450.00, 20, 'Redovna isporuka konzervansa', 4, 6);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (5, 'Kristal šećer', 500, 95.00, 20, 'Mesečna isporuka šećera', 5, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (6, 'UHT mleko 3.2%', 1000, 125.00, 10, 'Nedeljne isporuke 2-5', 6, 3);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (7, 'Integralno brašno', 200, 95.00, 10, 'Dodatna porudžbina', 1, 2);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (8, 'Pavlaka 20%', 100, 180.00, 20, 'Dodatak uz mleko', 2, 4);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (9, 'Jabuke Idared I klasa', 600, 65.00, 10, 'Isporuka - prva serija', 8, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (10, 'Jabuke Idared I klasa', 700, 65.00, 10, 'Isporuka - druga serija', 9, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (11, 'Kristal šećer', 1000, 95.00, 20, 'Martovska isporuka šećera', 10, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (12, 'Kristal šećer', 1500, 95.00, 20, 'Aprilska isporuka šećera', 11, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (13, 'Kristal šećer', 2000, 95.00, 20, 'Majska isporuka - povećana količina', 12, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (14, 'Kristal šećer', 1250, 95.00, 20, 'Junska isporuka šećera', 13, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (15, 'Pšenično brašno T-500', 1100, 85.50, 10, 'Industrijska isporuka', 14, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (16, 'Pšenično brašno T-500', 1250, 85.50, 10, 'Industrijska isporuka', 15, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (17, 'Integralno brašno', 900, 95.00, 10, 'Isporuka integralnog brašna', 16, 2);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (18, 'Pšenično brašno T-500', 1200, 85.50, 10, 'Sezonska isporuka', 17, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (19, 'Jabuke Idared I klasa', 800, 65.00, 10, 'Zimska isporuka', 18, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (20, 'Kristal šećer', 800, 95.00, 20, 'Fin šećer u prahu', 19, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (21, 'Kristal šećer', 3000, 95.00, 20, 'Industrijska količina - kvartalno', 20, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (22, 'Kristal šećer', 500, 95.00, 20, 'Rezervna hitna isporuka', 21, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (25, 'Pšenično brašno T-500', 1100, 85.50, 10, 'Prva serija', 23, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (26, 'UHT mleko 3.2%', 600, 125.00, 10, 'Nedeljne isporuke mleka', 24, 3);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (27, 'Pavlaka 20%', 25, 180.00, 20, 'Dodatak uz mleko', 24, 4);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (28, 'Jabuke Idared I klasa', 800, 65.00, 10, 'Jesenja isporuka jabuka', 25, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (29, 'Kristal šećer', 1750, 95.00, 20, 'Povećana količina', 26, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (30, 'Integralno brašno', 800, 95.00, 10, 'Isporuka integralnog brašna', 27, 2);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed_sf, pdv_stopa_sf, opis_sf, faktura_sifra_f, cenovnik_sifra_c)
VALUES (31, 'Pavlaka 20%', 200, 180.00, 20, 'Specijalna isporuka pavlake', 28, 4);

-- ============================================
-- 12a. RAČUN (naš račun sa kog se izvršavaju isplate - Četvrta iteracija;
-- stanje se NIKAD ne izlaže preko API-ja, koristi se samo interno pri
-- simulaciji plaćanja da proveri pokriće pre isplate.
-- Peta iteracija: jedinica_mere_sifra_jm -> valuta_sifra_v)
-- ============================================

INSERT INTO racun (sifra_r, broj_racuna_r, naziv_r, stanje_r, valuta_sifra_v)
VALUES (1, '160-0000000123456-78', 'Tekući račun - RSD', 100000.00, 1);

INSERT INTO racun (sifra_r, broj_racuna_r, naziv_r, stanje_r, valuta_sifra_v)
VALUES (2, 'RS35160005010001234567', 'Devizni račun - EUR', 5000.00, 2);

-- ============================================
-- 13. TRANSAKCIJA (potvrda_t -> broj_potvrde_t; dodat racun_sifra_r)
-- ============================================

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (1, TO_TIMESTAMP('2026-03-14 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-001', 'uspesna', 62500.00, 2, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (2, TO_TIMESTAMP('2026-03-10 14:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-002', 'uspesna', 125000.00, 6, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (3, TO_TIMESTAMP('2026-03-25 09:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-003', 'na_cekanju', 85500.00, 1, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (4, TO_TIMESTAMP('2026-03-13 16:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-004', 'na_cekanju', 22500.00, 4, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (5, TO_TIMESTAMP('2026-02-01 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-005', 'neuspesna', 15750.00, 7, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (6, TO_TIMESTAMP('2026-01-20 13:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-006', 'uspesna', 39000.00, 8, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (7, TO_TIMESTAMP('2026-01-25 10:50:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-007', 'uspesna', 45500.00, 9, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (8, TO_TIMESTAMP('2025-10-28 09:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-04-008', 'uspesna', 95000.00, 10, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (9, TO_TIMESTAMP('2025-11-25 14:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-05-009', 'uspesna', 142500.00, 11, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (10, TO_TIMESTAMP('2025-12-22 11:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-06-010', 'uspesna', 190000.00, 12, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (11, TO_TIMESTAMP('2026-01-30 15:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-011', 'uspesna', 118750.00, 13, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (12, TO_TIMESTAMP('2026-02-28 11:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-06-012', 'uspesna', 95000.00, 14, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (13, TO_TIMESTAMP('2026-03-18 09:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-013', 'uspesna', 110000.00, 15, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (14, TO_TIMESTAMP('2026-03-24 14:55:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-08-014', 'uspesna', 87500.00, 16, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (15, TO_TIMESTAMP('2026-03-23 10:10:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-015', 'uspesna', 102000.00, 17, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (16, TO_TIMESTAMP('2026-02-20 14:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-02-016', 'uspesna', 52000.00, 18, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (17, TO_TIMESTAMP('2026-03-22 11:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-04-017', 'uspesna', 76000.00, 19, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (18, TO_TIMESTAMP('2026-01-08 16:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-018', 'uspesna', 285000.00, 20, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (19, TO_TIMESTAMP('2026-02-16 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-02-019', 'uspesna', 47500.00, 21, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (20, TO_TIMESTAMP('2026-03-21 10:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-020', 'uspesna', 94050.00, 23, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (21, TO_TIMESTAMP('2026-03-19 14:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-021', 'uspesna', 80500.00, 24, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (22, TO_TIMESTAMP('2026-03-15 11:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-022', 'uspesna', 52000.00, 25, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (23, TO_TIMESTAMP('2026-02-06 09:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-023', 'uspesna', 166250.00, 26, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (24, TO_TIMESTAMP('2026-01-05 13:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-024', 'uspesna', 76000.00, 27, 1);

INSERT INTO transakcija (sifra_t, datum_t, broj_potvrde_t, status_t, iznos_t, faktura_sifra_f, racun_sifra_r)
VALUES (25, TO_TIMESTAMP('2026-04-20 15:50:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-025', 'uspesna', 36000.00, 28, 1);

-- ============================================
-- 14. PROMENA_STATUSA (istorijat - zamenjuje bivši Faktura.razlog_cekanja_f)
-- ============================================

INSERT INTO promena_statusa (sifra_ps, datum_vreme_ps, stari_status_ps, novi_status_ps, razlog_ps, faktura_sifra_f, korisnik_sifra_k)
VALUES (1, TO_TIMESTAMP('2026-03-18 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, 'primljena', 'Čeka se verifikacija kvaliteta isporučene robe', 3, 1);

INSERT INTO promena_statusa (sifra_ps, datum_vreme_ps, stari_status_ps, novi_status_ps, razlog_ps, faktura_sifra_f, korisnik_sifra_k)
VALUES (2, TO_TIMESTAMP('2026-03-22 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, 'primljena', 'Neslaganje između fakturisane i isporučene količine', 5, 2);

INSERT INTO promena_statusa (sifra_ps, datum_vreme_ps, stari_status_ps, novi_status_ps, razlog_ps, faktura_sifra_f, korisnik_sifra_k)
VALUES (3, TO_TIMESTAMP('2026-01-20 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, 'primljena', NULL, 7, 1);

INSERT INTO promena_statusa (sifra_ps, datum_vreme_ps, stari_status_ps, novi_status_ps, razlog_ps, faktura_sifra_f, korisnik_sifra_k)
VALUES (4, TO_TIMESTAMP('2026-02-01 11:05:00', 'YYYY-MM-DD HH24:MI:SS'), 'primljena', 'odbijena', 'Neusaglašenost sa ugovorom - penalizovana isporuka', 7, 1);

-- ============================================
-- 15. METRIKA (definicije - iste koje views_mk.py get_or_create-uje uživo;
-- Peta iteracija: dodate 4 metrike koje su ranije bile OCENA_DOBAVLJACA.
-- kriterijum_od slobodan tekst - sada je svaki kriterijum sopstvena Metrika)
-- ============================================

INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (1, 'Ukupno plaćeno', 'Zbir iznosa svih isplaćenih faktura', 'SUM(iznos_f) WHERE status_f=isplacena', 1);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (2, 'Sredstva na čekanju', 'Zbir iznosa faktura koje čekaju obradu/isplatu', 'SUM(iznos_f) WHERE status_f IN (primljena, verifikovana)', 1);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (3, 'Prosečno vreme plaćanja', 'Prosečan broj dana od prijema fakture do isplate', 'AVG(datum_t - datum_prijema_f)', 5);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (4, 'Broj faktura na čekanju', 'Broj faktura u statusu primljena/verifikovana', 'COUNT(*) WHERE status_f IN (primljena, verifikovana)', 3);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (5, 'Udeo sredstava na čekanju', 'Procenat sredstava na čekanju u odnosu na ukupan promet', 'na_cekanju / (ukupno_placeno + na_cekanju) * 100', 6);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (6, 'Mesečni trošak', 'Zbir isplaćenih faktura po mesecu prijema', 'SUM(iznos_f) GROUP BY mesec(datum_prijema_f)', 1);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (7, 'Broj penala', 'Broj penala dobavljača u posmatranom periodu', 'COUNT(*) FROM penal WHERE ugovor.dobavljac = :dobavljac', 3);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (8, 'Poštovanje rokova', 'Ocena poštovanja ugovorenih rokova isporuke', NULL, 6);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (9, 'Tačnost fakturisanja', 'Ocena podudarnosti fakturisane i ugovorene cene', NULL, 6);
INSERT INTO metrika (sifra_m, naziv_m, opis_m, formula_m, jedinica_mere_sifra_jm) VALUES (10, 'Odnos cena', 'Ocena konkurentnosti cena dobavljača', NULL, 6);

-- ============================================
-- 16. KONTROLNA_TABLA + KREIRANJE (bivši DASHBOARD + kreira; Peta iteracija:
-- kreiranje je sada (1,1) sa strane kontrolne table - jedan tvorac po tabli)
-- ============================================

INSERT INTO kontrolna_tabla (sifra_kt, naziv_kt, opis_kt) VALUES (1, 'Kontrolna tabla - Marko Marković', 'Lična kontrolna tabla finansijskog analitičara.');
INSERT INTO kontrolna_tabla (sifra_kt, naziv_kt, opis_kt) VALUES (2, 'Kontrolna tabla - Ana Petrović', 'Lična kontrolna tabla finansijskog analitičara.');
INSERT INTO kontrolna_tabla (sifra_kt, naziv_kt, opis_kt) VALUES (3, 'Kontrolna tabla - Jovan Nikolić', 'Lična kontrolna tabla finansijskog analitičara.');
INSERT INTO kontrolna_tabla (sifra_kt, naziv_kt, opis_kt) VALUES (4, 'Kontrolna tabla - Marko Marković', 'Lična kontrolna tabla finansijskog analitičara.');

INSERT INTO kreiranje (id, finansijski_analiticar_sifra_k, kontrolna_tabla_sifra_kt, datum_kr) VALUES (1, 1, 1, SYSTIMESTAMP - 30);
INSERT INTO kreiranje (id, finansijski_analiticar_sifra_k, kontrolna_tabla_sifra_kt, datum_kr) VALUES (2, 2, 2, SYSTIMESTAMP - 24);
INSERT INTO kreiranje (id, finansijski_analiticar_sifra_k, kontrolna_tabla_sifra_kt, datum_kr) VALUES (3, 3, 3, SYSTIMESTAMP - 18);
INSERT INTO kreiranje (id, finansijski_analiticar_sifra_k, kontrolna_tabla_sifra_kt, datum_kr) VALUES (4, 4, 4, SYSTIMESTAMP - 12);

-- ============================================
-- 17. PRIKAZUJE (Peta iteracija - nova veza KontrolnaTabla<->Metrika; svaka
-- od 4 table prikazuje istih 6 standardnih dashboard metrika)
-- ============================================

INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (1, 1, 1);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (2, 1, 2);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (3, 1, 3);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (4, 1, 4);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (5, 1, 5);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (6, 1, 6);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (7, 2, 1);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (8, 2, 2);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (9, 2, 3);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (10, 2, 4);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (11, 2, 5);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (12, 2, 6);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (13, 3, 1);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (14, 3, 2);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (15, 3, 3);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (16, 3, 4);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (17, 3, 5);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (18, 3, 6);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (19, 4, 1);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (20, 4, 2);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (21, 4, 3);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (22, 4, 4);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (23, 4, 5);
INSERT INTO prikazuje (id, kontrolna_tabla_sifra_kt, metrika_sifra_m) VALUES (24, 4, 6);

-- ============================================
-- 18. MERENJE (Peta iteracija: samostalan TE, ne visi više o kontrolnoj
-- tabli - id -> sifra_me, dodato dobavljac_sifra_db kao opciona dimenzija.
-- Merenja 1-3 su globalna (bez dimenzije, ista vrednost za sve 4 table koje
-- ih prikazuju). Merenja 4-8 nose dimenziju dobavljača i osnova su za
-- OCENA_DOBAVLJACA ispod.)
-- ============================================

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (1, 1, 373250.00, TO_TIMESTAMP('2026-03-01 08:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, NULL, NULL);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (2, 2, 185750.00, TO_TIMESTAMP('2026-03-01 08:00:00', 'YYYY-MM-DD HH24:MI:SS'), NULL, NULL, NULL);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (3, 6, 373250.00, TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), TO_DATE('2026-03-31', 'YYYY-MM-DD'), NULL);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (4, 7, 4, TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 1);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (5, 8, 6.50, TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 1);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (6, 9, 9.20, TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 2);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (7, 10, 8.00, TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 3);

INSERT INTO merenje (sifra_me, metrika_sifra_m, vrednost_me, vreme_merenja_me, period_od_me, period_do_me, dobavljac_sifra_db)
VALUES (8, 7, 1, TO_TIMESTAMP('2026-03-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 5);

-- ============================================
-- 19. OCENA_DOBAVLJACA (Peta iteracija: kriterijum_od/period_od_od/period_do_od
-- uklonjeni - kriterijum i period su sada na povezanom MERENJE; dodato
-- finansijski_analiticar_sifra_k (dao_ocenu) i merenje_sifra_me (zasniva_se_na))
-- ============================================

INSERT INTO ocena_dobavljaca (sifra_od, vrednost_od, datum_ocenj_od, dobavljac_sifra_db, finansijski_analiticar_sifra_k, merenje_sifra_me)
VALUES (1, 6.00, TO_DATE('2026-03-01', 'YYYY-MM-DD'), 1, 1, 4);

INSERT INTO ocena_dobavljaca (sifra_od, vrednost_od, datum_ocenj_od, dobavljac_sifra_db, finansijski_analiticar_sifra_k, merenje_sifra_me)
VALUES (2, 6.50, TO_DATE('2026-03-01', 'YYYY-MM-DD'), 1, 1, 5);

INSERT INTO ocena_dobavljaca (sifra_od, vrednost_od, datum_ocenj_od, dobavljac_sifra_db, finansijski_analiticar_sifra_k, merenje_sifra_me)
VALUES (3, 9.20, TO_DATE('2026-03-01', 'YYYY-MM-DD'), 2, 1, 6);

INSERT INTO ocena_dobavljaca (sifra_od, vrednost_od, datum_ocenj_od, dobavljac_sifra_db, finansijski_analiticar_sifra_k, merenje_sifra_me)
VALUES (4, 8.00, TO_DATE('2026-03-01', 'YYYY-MM-DD'), 3, 1, 7);

INSERT INTO ocena_dobavljaca (sifra_od, vrednost_od, datum_ocenj_od, dobavljac_sifra_db, finansijski_analiticar_sifra_k, merenje_sifra_me)
VALUES (5, 9.00, TO_DATE('2026-03-01', 'YYYY-MM-DD'), 5, 1, 8);

-- ============================================
-- 20. IZVEŠTAJ (visi na KREIRANJE; tip_i suženo na FINANSIJSKI/DOBAVLJACI/UGOVORI/PLACANJA)
-- ============================================

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, period_od_i, period_do_i, kreiranje_id)
VALUES (1, SYSTIMESTAMP - 2, 'FINANSIJSKI', TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2025-09-30', 'YYYY-MM-DD'), 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, period_od_i, period_do_i, kreiranje_id)
VALUES (2, SYSTIMESTAMP - 7, 'DOBAVLJACI', NULL, NULL, 2);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, period_od_i, period_do_i, kreiranje_id)
VALUES (3, SYSTIMESTAMP - 14, 'FINANSIJSKI', TO_DATE('2025-07-01', 'YYYY-MM-DD'), TO_DATE('2025-09-30', 'YYYY-MM-DD'), 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, period_od_i, period_do_i, kreiranje_id)
VALUES (4, SYSTIMESTAMP - 20, 'PLACANJA', NULL, NULL, 3);

-- ============================================
-- 21. PREDMET_IZVESTAJA (zamenjuje bivše koristi/poseduje - tačno jedan FK po redu)
-- ============================================

INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, faktura_sifra_f) VALUES (1, 'FAKTURA', 1, 1);
INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, faktura_sifra_f) VALUES (2, 'FAKTURA', 1, 2);
INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, faktura_sifra_f) VALUES (3, 'FAKTURA', 1, 6);

INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, dobavljac_sifra_db) VALUES (4, 'DOBAVLJAC', 2, 1);
INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, dobavljac_sifra_db) VALUES (5, 'DOBAVLJAC', 2, 2);
INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, dobavljac_sifra_db) VALUES (6, 'DOBAVLJAC', 2, 3);

INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, faktura_sifra_f) VALUES (7, 'FAKTURA', 3, 3);
INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, faktura_sifra_f) VALUES (8, 'FAKTURA', 3, 7);
INSERT INTO predmet_izvestaja (sifra_pi, tip_predmeta_pi, izvestaj_sifra_i, dobavljac_sifra_db) VALUES (9, 'DOBAVLJAC', 3, 1);

-- ============================================
-- 22. NOTIFIKACIJA + SE_SALJE (nepromenjeno - Notifikacija nije deo ovog EER-a)
-- ============================================

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (1, 'Nova faktura primljena: Agro Invest DOO - 85,500 RSD. Rok plaćanja: 01.10.2025', SYSTIMESTAMP - 1, 0, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (1, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (2, 'UPOZORENJE: Faktura 3 - neslaganje količine. Potrebna verifikacija!', SYSTIMESTAMP - 2, 0, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (1, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (3, 'Transakcija TRX-2025-09-001 uspešno izvršena. Iznos: 62,500 RSD', SYSTIMESTAMP - 5, 1, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (2, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (4, 'Novi penal evidentiran: Voće Srbija - kašnjenje 2 dana. Iznos: 7,500 RSD', SYSTIMESTAMP - 10, 1, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (2, 4);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (5, 'Ugovor ističe za 30 dana: Ugovor #3 sa Voće Srbija DOO. Potrebno obnoviti.', SYSTIMESTAMP - 3, 0, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (3, 5);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (6, 'ROK ZA PLAĆANJE: Faktura 1 dospeva za 5 dana', SYSTIMESTAMP, 0, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (1, 6);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (7, 'Mesečni finansijski izveštaj je generisan. Ukupan promet: 373,250 RSD', SYSTIMESTAMP - 2, 1, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (1, 7);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (8, 'Transakcija TRX-2025-07-005 neuspešna. Razlog: Nedovoljna sredstva na računu.', SYSTIMESTAMP - 15, 1, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (3, 8);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (9, 'KRITIČNO: Agro Invest DOO - više penala u kratkom periodu.', SYSTIMESTAMP - 1, 0, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (1, 9);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (10, 'Novi penal: Agro Invest - kašnjenje 7 dana. Iznos: 9,000 RSD', SYSTIMESTAMP - 4, 0, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (2, 10);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (11, 'VELIKI PENAL: Šećerana Crvenka - ekstremno kašnjenje 14 dana. Iznos: 25,000 RSD', SYSTIMESTAMP - 90, 1, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (1, 11);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n) VALUES (12, 'Novi penal: Agro Invest - kvalitet ispod standarda. Iznos: 15,500 RSD', SYSTIMESTAMP - 35, 1, NULL);
INSERT INTO se_salje (korisnik_sifra_k, notifikacija_sifra_n) VALUES (3, 12);

COMMIT;

-- ============================================
-- RESETOVANJE GENERATORA PK VREDNOSTI NA MAX(ID)+1
-- ============================================

DECLARE
    CURSOR c_tables IS
        SELECT table_name
        FROM (
            SELECT 'KORISNIK' AS table_name FROM dual UNION ALL
            SELECT 'FINANSIJSKI_ANALITICAR' FROM dual UNION ALL
            SELECT 'JEDINICA_MERE' FROM dual UNION ALL
            SELECT 'VALUTA' FROM dual UNION ALL
            SELECT 'DOBAVLJAC' FROM dual UNION ALL
            SELECT 'KATEGORIJA_PROIZVODA' FROM dual UNION ALL
            SELECT 'PROIZVOD' FROM dual UNION ALL
            SELECT 'PROIZVOD_DOBAVLJACA' FROM dual UNION ALL
            SELECT 'CENOVNIK' FROM dual UNION ALL
            SELECT 'UGOVOR' FROM dual UNION ALL
            SELECT 'PENAL' FROM dual UNION ALL
            SELECT 'FAKTURA' FROM dual UNION ALL
            SELECT 'STAVKA_FAKTURE' FROM dual UNION ALL
            SELECT 'RACUN' FROM dual UNION ALL
            SELECT 'TRANSAKCIJA' FROM dual UNION ALL
            SELECT 'PROMENA_STATUSA' FROM dual UNION ALL
            SELECT 'OCENA_DOBAVLJACA' FROM dual UNION ALL
            SELECT 'KONTROLNA_TABLA' FROM dual UNION ALL
            SELECT 'KREIRANJE' FROM dual UNION ALL
            SELECT 'METRIKA' FROM dual UNION ALL
            SELECT 'PRIKAZUJE' FROM dual UNION ALL
            SELECT 'MERENJE' FROM dual UNION ALL
            SELECT 'IZVESTAJ' FROM dual UNION ALL
            SELECT 'PREDMET_IZVESTAJA' FROM dual UNION ALL
            SELECT 'NOTIFIKACIJA' FROM dual UNION ALL
            SELECT 'SE_SALJE' FROM dual
        );

    v_seq_name          VARCHAR2(100);
    v_pk_column_name    VARCHAR2(100);
    v_max_id            NUMBER;
    v_start_with        NUMBER;
    v_sql               VARCHAR2(500);
    v_is_identity       NUMBER;

BEGIN
    FOR t IN c_tables LOOP
        v_seq_name := LOWER(t.table_name) || '_seq';

        BEGIN
            SELECT cols.column_name
            INTO v_pk_column_name
            FROM all_constraints cons
            JOIN all_cons_columns cols ON cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner
            WHERE cons.constraint_type = 'P'
              AND cons.table_name = t.table_name
              AND cons.owner = USER;

            v_sql := 'SELECT MAX(' || v_pk_column_name || ') FROM ' || t.table_name;
            EXECUTE IMMEDIATE v_sql INTO v_max_id;

            v_start_with := NVL(v_max_id, 0) + 1;

            -- Da li je PK kolona IDENTITY (Django 4.1+ na Oracle-u)?
            SELECT COUNT(*) INTO v_is_identity
            FROM user_tab_identity_cols
            WHERE table_name = t.table_name
              AND column_name = v_pk_column_name;

            IF v_is_identity > 0 THEN
                v_sql := 'ALTER TABLE ' || t.table_name || ' MODIFY ' || v_pk_column_name ||
                         ' GENERATED BY DEFAULT AS IDENTITY (START WITH ' || v_start_with || ')';
                EXECUTE IMMEDIATE v_sql;
                DBMS_OUTPUT.PUT_LINE('Restartovan IDENTITY generator: ' || t.table_name || '.' || v_pk_column_name || ' na ' || v_start_with);
            ELSE
                BEGIN
                    EXECUTE IMMEDIATE 'DROP SEQUENCE ' || v_seq_name;
                    DBMS_OUTPUT.PUT_LINE('Obrisana postojeća sekvenca: ' || v_seq_name);
                EXCEPTION
                    WHEN OTHERS THEN NULL;
                END;

                v_sql := 'CREATE SEQUENCE ' || v_seq_name || ' START WITH ' || v_start_with || ' INCREMENT BY 1 NOCACHE';
                EXECUTE IMMEDIATE v_sql;

                DBMS_OUTPUT.PUT_LINE('Kreirana/ažurirana sekvenca: ' || v_seq_name || ' sa početnom vrednošću ' || v_start_with);
            END IF;

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                DBMS_OUTPUT.PUT_LINE('UPOZORENJE: Nije pronađen primarni ključ za tabelu: ' || t.table_name || '. PK generator nije ažuriran.');
            WHEN OTHERS THEN
                DBMS_OUTPUT.PUT_LINE('GREŠKA pri obradi tabele ' || t.table_name || ': ' || SQLERRM);
        END;

    END LOOP;
END;
/

COMMIT;

-- ============================================
-- PROVERA UNETIH PODATAKA
-- ============================================

SELECT 'KORISNICI' AS tabela, COUNT(*) AS broj_redova FROM korisnik
UNION ALL SELECT 'FINANSIJSKI_ANALITICAR', COUNT(*) FROM finansijski_analiticar
UNION ALL SELECT 'JEDINICA_MERE', COUNT(*) FROM jedinica_mere
UNION ALL SELECT 'VALUTA', COUNT(*) FROM valuta
UNION ALL SELECT 'DOBAVLJACI', COUNT(*) FROM dobavljac
UNION ALL SELECT 'KATEGORIJE', COUNT(*) FROM kategorija_proizvoda
UNION ALL SELECT 'PROIZVODI', COUNT(*) FROM proizvod
UNION ALL SELECT 'PROIZVOD_DOBAVLJACA', COUNT(*) FROM proizvod_dobavljaca
UNION ALL SELECT 'CENOVNIK', COUNT(*) FROM cenovnik
UNION ALL SELECT 'UGOVORI', COUNT(*) FROM ugovor
UNION ALL SELECT 'PENALI', COUNT(*) FROM penal
UNION ALL SELECT 'FAKTURE', COUNT(*) FROM faktura
UNION ALL SELECT 'STAVKE_FAKTURE', COUNT(*) FROM stavka_fakture
UNION ALL SELECT 'RACUNI', COUNT(*) FROM racun
UNION ALL SELECT 'TRANSAKCIJE', COUNT(*) FROM transakcija
UNION ALL SELECT 'PROMENA_STATUSA', COUNT(*) FROM promena_statusa
UNION ALL SELECT 'OCENA_DOBAVLJACA', COUNT(*) FROM ocena_dobavljaca
UNION ALL SELECT 'KONTROLNE_TABLE', COUNT(*) FROM kontrolna_tabla
UNION ALL SELECT 'KREIRANJE', COUNT(*) FROM kreiranje
UNION ALL SELECT 'METRIKE', COUNT(*) FROM metrika
UNION ALL SELECT 'PRIKAZUJE', COUNT(*) FROM prikazuje
UNION ALL SELECT 'MERENJA', COUNT(*) FROM merenje
UNION ALL SELECT 'IZVESTAJI', COUNT(*) FROM izvestaj
UNION ALL SELECT 'PREDMET_IZVESTAJA', COUNT(*) FROM predmet_izvestaja
UNION ALL SELECT 'NOTIFIKACIJE', COUNT(*) FROM notifikacija
UNION ALL SELECT 'SE_SALJE', COUNT(*) FROM se_salje;
