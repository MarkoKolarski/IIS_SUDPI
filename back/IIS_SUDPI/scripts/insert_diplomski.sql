-- ============================================
-- ORACLE INSERT SKRIPTA ZA FINANSIJSKI SISTEM
-- Ekstenzija fajla: .sql
-- ============================================

-- Brisanje postojećih podataka (opcionalno)
-- DELETE FROM notifikacija;
-- DELETE FROM transakcija;
-- DELETE FROM stavka_fakture;
-- DELETE FROM proizvod;
-- DELETE FROM kategorija_proizvoda;
-- DELETE FROM faktura;
-- DELETE FROM penal;
-- DELETE FROM ugovor;
-- DELETE FROM dobavljac;
-- DELETE FROM izvestaj;
-- DELETE FROM dashboard;
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
-- 2. FINANSIJSKI ANALITIČAR (specifični zapisi)
-- ============================================

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (1, 1);

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (2, 2);

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (3, 3);

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (4, 4);

-- ============================================
-- 3. DOBAVLJAČ
-- ============================================

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (1, 'Agro Invest DOO', 'salebecej1@gmail.com', '123456789', 'Pšenično brašno tip 500', 85.50, 5, 7.20, TO_DATE('2026-09-15', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (2, 'Mlekoprodukt AD', 'salebecej1@gmail.com', '987654321', 'UHT mleko 3.2%', 125.00, 3, 9.50, TO_DATE('2026-09-20', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (3, 'Voće Srbija DOO', 'salebecej1@gmail.com', '456789123', 'Jabuke Idared', 65.00, 2, 8.80, TO_DATE('2026-09-10', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (4, 'Hemija Sever DOO', 'salebecej1@gmail.com', '789123456', 'Natrijum benzoat', 450.00, 7, 9.10, TO_DATE('2026-08-25', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (5, 'Šećerana Crvenka', 'salebecej1@gmail.com', '321654987', 'Kristal šećer', 95.00, 4, 9.00, TO_DATE('2026-09-18', 'YYYY-MM-DD'), 1);

-- ============================================
-- 4. UGOVOR
-- ============================================

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (1, TO_DATE('2026-01-10', 'YYYY-MM-DD'), TO_DATE('2027-01-10', 'YYYY-MM-DD'), 'aktivan', 
'Isporuka brašna u količini min 1000kg mesečno. Cena fiksna za prvih 6 meseci. Rok plaćanja 30 dana.', 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (2, TO_DATE('2026-02-15', 'YYYY-MM-DD'), TO_DATE('2027-02-15', 'YYYY-MM-DD'), 'aktivan',
'Isporuka UHT mleka 2x nedeljno. Minimalna količina 500L po isporuci. Rok plaćanja 15 dana.', 2);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (3, TO_DATE('2025-10-01', 'YYYY-MM-DD'), TO_DATE('2026-10-01', 'YYYY-MM-DD'), 'aktivan',
'Sezonska isporuka voća. Kvalitet mora biti I klasa. Rok plaćanja 45 dana.', 3);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (4, TO_DATE('2025-05-20', 'YYYY-MM-DD'), TO_DATE('2026-05-20', 'YYYY-MM-DD'), 'istekao',
'Isporuka hemikalija sa sertifikatima. Plaćanje avansno 50%.', 4);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (5, TO_DATE('2026-03-01', 'YYYY-MM-DD'), TO_DATE('2026-09-01', 'YYYY-MM-DD'), 'otkazan',
'Isporuka šećera - ugovor raskinut zbog kašnjenja u isporuci.', 5);

-- Dodatni ugovor za Agro Invest (integralno brašno)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (6, TO_DATE('2025-08-01', 'YYYY-MM-DD'), TO_DATE('2026-08-01', 'YYYY-MM-DD'), 'aktivan',
'Prošireni ugovor za isporuku integralnog brašna. Minimalna količina 200kg mesečno. Rok plaćanja 30 dana.', 1);

-- Dodatni ugovor za Mlekoprodukt (pavlaka i mlečni derivati)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (7, TO_DATE('2026-01-20', 'YYYY-MM-DD'), TO_DATE('2027-01-20', 'YYYY-MM-DD'), 'aktivan',
'Dodatni ugovor za isporuku pavlake i drugih mlečnih derivata. Isporuka 1x nedeljno. Rok plaćanja 15 dana.', 2);

-- Obnovljeni ugovor za Voće Srbija (pokriva avg-sept 2025)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (8, TO_DATE('2026-06-01', 'YYYY-MM-DD'), TO_DATE('2027-06-01', 'YYYY-MM-DD'), 'aktivan',
'Obnovljeni sezonski ugovor za isporuku voća - leto/jesen 2025. Povećane količine. Kvalitet I klasa. Rok plaćanja 45 dana.', 3);

-- Glavni godišnji ugovor za Šećerana Crvenka (mart-jun 2025)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (9, TO_DATE('2026-01-15', 'YYYY-MM-DD'), TO_DATE('2027-01-15', 'YYYY-MM-DD'), 'aktivan',
'Godišnji ugovor za isporuku kristal šećera. Mesečne isporuke 1000-2000kg. Cena fiksna. Rok plaćanja 30 dana.', 5);

-- Obnovljeni ugovor za Hemija Sever (nakon isteklog)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (10, TO_DATE('2026-06-01', 'YYYY-MM-DD'), TO_DATE('2027-06-01', 'YYYY-MM-DD'), 'aktivan',
'Obnovljeni ugovor za isporuku hemikalija i aditiva. Svi proizvodi sa sertifikatima. Rok plaćanja 30 dana.', 4);

-- Dodatni ugovor za Agro Invest (treći ugovor - za veće količine) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (11, TO_DATE('2025-06-15', 'YYYY-MM-DD'), TO_DATE('2026-06-15', 'YYYY-MM-DD'), 'aktivan',
'Specijalni ugovor za industrijske količine brašna. Isporuka 2x mesečno. Rok plaćanja 30 dana.', 1);

-- Dodatni ugovor za Agro Invest (četvrti ugovor - sezonski) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (12, TO_DATE('2026-04-01', 'YYYY-MM-DD'), TO_DATE('2026-12-31', 'YYYY-MM-DD'), 'aktivan',
'Sezonski ugovor za prolećnu/letnju sezonu. Povećane količine. Rok plaćanja 30 dana.', 1);

-- Dodatni ugovor za Voće Srbija (treći ugovor - zimska sezona) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (13, TO_DATE('2025-12-01', 'YYYY-MM-DD'), TO_DATE('2026-11-30', 'YYYY-MM-DD'), 'aktivan',
'Zimski ugovor za isporuku konzerviranog voća. Rok plaćanja 45 dana.', 3);

-- Dodatni ugovor za Šećerana Crvenka (treći ugovor - specijalni) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (14, TO_DATE('2026-02-01', 'YYYY-MM-DD'), TO_DATE('2027-02-01', 'YYYY-MM-DD'), 'aktivan',
'Specijalni ugovor za fin šećer u prahu. Mesečne isporuke. Rok plaćanja 30 dana.', 5);

-- Dodatni ugovor za Šećerana Crvenka (četvrti ugovor - industrijski) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (15, TO_DATE('2026-07-01', 'YYYY-MM-DD'), TO_DATE('2027-07-01', 'YYYY-MM-DD'), 'aktivan',
'Industrijski ugovor za velike količine šećera. Kvartalne isporuke. Rok plaćanja 30 dana.', 5);

-- Dodatni ugovor za Šećerana Crvenka (peti ugovor - rezervni) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (16, TO_DATE('2025-11-01', 'YYYY-MM-DD'), TO_DATE('2026-10-31', 'YYYY-MM-DD'), 'aktivan',
'Rezervni ugovor za hitne isporuke šećera. Po potrebi. Rok plaćanja 15 dana.', 5);

-- ============================================
-- 5. PENAL (REBALANSOVANO - različite stope kršenja)
-- ============================================

-- AGRO INVEST - 4 PENALA na 3 od 4 ugovora (75% stopa kršenja - CRVENO)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (1, 'Nedostajuća dokumentacija - sertifikat kvaliteta', 8500.00, TO_DATE('2025-11-15', 'YYYY-MM-DD'), 1);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (2, 'Isporučena količina manja od ugovorene (850kg umesto 1000kg)', 12000.00, TO_DATE('2026-03-05', 'YYYY-MM-DD'), 1);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (3, 'Kašnjenje u isporuci od 3 dana', 9000.00, TO_DATE('2026-02-20', 'YYYY-MM-DD'), 6);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (4, 'Kvalitet brašna ispod standarda - vraćena pošiljka', 15500.00, TO_DATE('2026-01-25', 'YYYY-MM-DD'), 12);

-- VOĆE SRBIJA - 1 PENAL na 1 od 3 ugovora (33% stopa kršenja - ŽUTO/UPOZORENJE)  
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (5, 'Kašnjenje u isporuci od 2 dana', 7500.00, TO_DATE('2026-03-10', 'YYYY-MM-DD'), 3);

-- ŠEĆERANA CRVENKA - 1 PENAL na 1 od 5 ugovora (20% stopa kršenja - ZELENO/DOBRO)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (6, 'Ekstremno kašnjenje u isporuci od 14 dana + nekompletna dokumentacija', 25000.00, TO_DATE('2025-12-20', 'YYYY-MM-DD'), 5);

-- ============================================
-- 6. KATEGORIJA PROIZVODA
-- ============================================

INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp, limit_kp)
VALUES (1, 'Mlinarski proizvodi', 150000.00);

INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp, limit_kp)
VALUES (2, 'Mlečni proizvodi', 200000.00);

INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp, limit_kp)
VALUES (3, 'Voće i povrće', 100000.00);

INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp, limit_kp)
VALUES (4, 'Hemikalije i aditivi', 80000.00);

INSERT INTO kategorija_proizvoda (sifra_kp, naziv_kp, limit_kp)
VALUES (5, 'Šećer i zaslađivači', 120000.00);

-- ============================================
-- 7. PROIZVOD
-- ============================================

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (1, 'Pšenično brašno T-500', 'Visokokvalitetno pšenično brašno tip 500 za industriju', 1);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (2, 'Integralno brašno', 'Brašno od celih zrna pšenice, bogato vlaknima', 1);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (3, 'UHT mleko 3.2%', 'Trajno mleko sa 3.2% mlečne masti', 2);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (4, 'Pavlaka 20%', 'Pavlaka za kuvanje sa 20% mlečne masti', 2);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (5, 'Jabuke Idared I klasa', 'Sveže jabuke sorte Idared, prva klasa kvaliteta', 3);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (6, 'Natrijum benzoat E211', 'Konzervans za produženje roka trajanja proizvoda', 4);

INSERT INTO proizvod (sifra_pr, naziv_pr, opis_pr, kategorija_id)
VALUES (7, 'Kristal šećer', 'Rafinirani beli kristal šećer', 5);

-- ============================================
-- 8. FAKTURA
-- ============================================

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (1, 85500.00, TO_DATE('2026-03-05', 'YYYY-MM-DD'), TO_DATE('2026-04-05', 'YYYY-MM-DD'), 'verifikovana', NULL, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (2, 62500.00, TO_DATE('2026-03-02', 'YYYY-MM-DD'), TO_DATE('2026-03-17', 'YYYY-MM-DD'), 'isplacena', NULL, 2);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (3, 32500.00, TO_DATE('2026-03-18', 'YYYY-MM-DD'), TO_DATE('2026-03-29', 'YYYY-MM-DD'), 'primljena', 'Čeka se verifikacija kvaliteta isporučene robe', 3);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (4, 22500.00, TO_DATE('2026-02-10', 'YYYY-MM-DD'), TO_DATE('2026-03-12', 'YYYY-MM-DD'), 'verifikovana', NULL, 4);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (5, 47500.00, TO_DATE('2026-03-22', 'YYYY-MM-DD'), TO_DATE('2026-04-18', 'YYYY-MM-DD'), 'primljena', 'Neslaganje između fakturisane i isporučene količine', 5);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (6, 125000.00, TO_DATE('2026-02-25', 'YYYY-MM-DD'), TO_DATE('2026-03-15', 'YYYY-MM-DD'), 'isplacena', NULL, 2);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (7, 15750.00, TO_DATE('2026-01-20', 'YYYY-MM-DD'), TO_DATE('2026-02-20', 'YYYY-MM-DD'), 'odbijena', 'Neusaglašenost sa ugovorom - penalizovana isporuka', 3);

-- Dodatne fakture za Voće Srbija DOO (ugovor_id = 8)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (8, 39000.00, TO_DATE('2026-01-08', 'YYYY-MM-DD'), TO_DATE('2026-02-19', 'YYYY-MM-DD'), 'isplacena', NULL, 8);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (9, 45500.00, TO_DATE('2025-12-20', 'YYYY-MM-DD'), TO_DATE('2026-02-04', 'YYYY-MM-DD'), 'isplacena', NULL, 8);

-- Dodatne fakture za Šećerana Crvenka (ugovor_id = 9)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (10, 95000.00, TO_DATE('2025-10-15', 'YYYY-MM-DD'), TO_DATE('2025-11-14', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (11, 142500.00, TO_DATE('2025-11-10', 'YYYY-MM-DD'), TO_DATE('2025-12-10', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (12, 190000.00, TO_DATE('2025-12-05', 'YYYY-MM-DD'), TO_DATE('2026-01-04', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (13, 118750.00, TO_DATE('2026-01-12', 'YYYY-MM-DD'), TO_DATE('2026-02-12', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

-- Dodatne fakture za Agro Invest (novi ugovori 11 i 12)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (14, 95000.00, TO_DATE('2026-02-10', 'YYYY-MM-DD'), TO_DATE('2026-03-12', 'YYYY-MM-DD'), 'isplacena', NULL, 11);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (15, 110000.00, TO_DATE('2026-03-04', 'YYYY-MM-DD'), TO_DATE('2026-04-03', 'YYYY-MM-DD'), 'isplacena', NULL, 11);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (16, 87500.00, TO_DATE('2026-03-16', 'YYYY-MM-DD'), TO_DATE('2026-04-15', 'YYYY-MM-DD'), 'isplacena', NULL, 6);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (17, 102000.00, TO_DATE('2026-02-22', 'YYYY-MM-DD'), TO_DATE('2026-03-24', 'YYYY-MM-DD'), 'isplacena', NULL, 12);

-- Dodatne fakture za nove ugovore
-- Faktura za Voće Srbija DOO (ugovor 13 - zimski)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (18, 52000.00, TO_DATE('2026-01-15', 'YYYY-MM-DD'), TO_DATE('2026-03-01', 'YYYY-MM-DD'), 'isplacena', NULL, 13);

-- Fakture za Šećerana Crvenka (novi ugovori 14,15,16)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (19, 76000.00, TO_DATE('2026-03-10', 'YYYY-MM-DD'), TO_DATE('2026-04-09', 'YYYY-MM-DD'), 'isplacena', NULL, 14);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (20, 285000.00, TO_DATE('2025-12-15', 'YYYY-MM-DD'), TO_DATE('2026-01-14', 'YYYY-MM-DD'), 'isplacena', NULL, 15);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (21, 47500.00, TO_DATE('2026-02-03', 'YYYY-MM-DD'), TO_DATE('2026-02-18', 'YYYY-MM-DD'), 'isplacena', NULL, 16);

-- ============================================
-- 9. STAVKA FAKTURE
-- ============================================

-- Stavke za fakturu 1
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1, 'Pšenično brašno T-500', 1000, 85.50, 'Mesečna isporuka - septembar 2025', 1, 1);

-- Stavke za fakturu 2
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (2, 'UHT mleko 3.2%', 500, 125.00, 'Nedeljna isporuka 1 - septembar', 2, 3);

-- Stavke za fakturu 3
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (3, 'Jabuke Idared I klasa', 500, 65.00, 'Sezonska isporuka - jesen 2025', 3, 5);

-- Stavke za fakturu 4
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (4, 'Natrijum benzoat E211', 50, 450.00, 'Redovna isporuka konzervansa', 4, 6);

-- Stavke za fakturu 5
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (5, 'Kristal šećer', 500, 95.00, 'Mesečna isporuka šećera', 5, 7);

-- Stavke za fakturu 6
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (6, 'UHT mleko 3.2%', 1000, 125.00, 'Nedeljne isporuke 2-5 septembar', 6, 3);

-- Dodatne stavke (kombinovane fakture)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (7, 'Integralno brašno', 200, 95.00, 'Dodatna porudžbina', 1, 2);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (8, 'Pavlaka 20%', 100, 180.00, 'Dodatak uz mleko', 2, 4);

-- Stavke za fakturu 8 (Voće Srbija DOO)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (9, 'Jabuke Idared I klasa', 600, 65.00, 'Avgustovska isporuka - prva serija', 8, 5);

-- Stavke za fakturu 9 (Voće Srbija DOO)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (10, 'Jabuke Idared I klasa', 700, 65.00, 'Avgustovska isporuka - druga serija', 9, 5);

-- Stavke za fakturu 10 (Šećerana Crvenka)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (11, 'Kristal šećer', 1000, 95.00, 'Martovska isporuka šećera', 10, 7);

-- Stavke za fakturu 11 (Šećerana Crvenka)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (12, 'Kristal šećer', 1500, 95.00, 'Aprilska isporuka šećera', 11, 7);

-- Stavke za fakturu 12 (Šećerana Crvenka)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (13, 'Kristal šećer', 2000, 95.00, 'Majska isporuka šećera - povećana količina', 12, 7);

-- Stavke za fakturu 13 (Šećerana Crvenka)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (14, 'Kristal šećer', 1250, 95.00, 'Junska isporuka šećera', 13, 7);

-- Stavke za fakturu 14 (Agro Invest - ugovor 11)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (15, 'Pšenično brašno T-500', 1100, 85.50, 'Industrijska isporuka - maj 2025', 14, 1);

-- Stavke za fakturu 15 (Agro Invest - ugovor 11)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (16, 'Pšenično brašno T-500', 1250, 85.50, 'Industrijska isporuka - jun 2025', 15, 1);

-- Stavke za fakturu 16 (Agro Invest - ugovor 6)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (17, 'Integralno brašno', 900, 95.00, 'Julska isporuka integralnog brašna', 16, 2);

-- Stavke za fakturu 17 (Agro Invest - ugovor 12)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (18, 'Pšenično brašno T-500', 1200, 85.50, 'Sezonska isporuka - avgust 2025', 17, 1);

-- Stavke za fakturu 18 (Voće Srbija DOO - ugovor 13)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (19, 'Jabuke Idared I klasa', 800, 65.00, 'Zimska isporuka konzerviranog voća', 18, 5);

-- Stavke za fakturu 19 (Šećerana Crvenka - ugovor 14)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (20, 'Kristal šećer', 800, 95.00, 'Fin šećer u prahu - mart 2025', 19, 7);

-- Stavke za fakturu 20 (Šećerana Crvenka - ugovor 15)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (21, 'Kristal šećer', 3000, 95.00, 'Industrijska količina šećera - kvartalno', 20, 7);

-- Stavke za fakturu 21 (Šećerana Crvenka - ugovor 16)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (22, 'Kristal šećer', 500, 95.00, 'Rezervna hitna isporuka', 21, 7);

-- ============================================
-- 10. TRANSAKCIJA
-- ============================================

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (1, TO_TIMESTAMP('2026-03-14 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-001', 'uspesna', 2);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (2, TO_TIMESTAMP('2026-03-10 14:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-002', 'uspesna', 6);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (3, TO_TIMESTAMP('2026-03-25 09:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-003', 'na_cekanju', 1);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (4, TO_TIMESTAMP('2026-03-13 16:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-004', 'na_cekanju', 4);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (5, TO_TIMESTAMP('2026-02-01 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-005', 'neuspesna', 7);

-- Transakcije za nove fakture Voće Srbija DOO
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (6, TO_TIMESTAMP('2026-01-20 13:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-006', 'uspesna', 8);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (7, TO_TIMESTAMP('2026-01-25 10:50:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-007', 'uspesna', 9);

-- Transakcije za nove fakture Šećerana Crvenka
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (8, TO_TIMESTAMP('2025-10-28 09:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-04-008', 'uspesna', 10);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (9, TO_TIMESTAMP('2025-11-25 14:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-05-009', 'uspesna', 11);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (10, TO_TIMESTAMP('2025-12-22 11:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-06-010', 'uspesna', 12);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (11, TO_TIMESTAMP('2026-01-30 15:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-011', 'uspesna', 13);

-- Transakcije za nove fakture Agro Invest
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (12, TO_TIMESTAMP('2026-02-28 11:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-06-012', 'uspesna', 14);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (13, TO_TIMESTAMP('2026-03-18 09:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-013', 'uspesna', 15);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (14, TO_TIMESTAMP('2026-03-24 14:55:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-08-014', 'uspesna', 16);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (15, TO_TIMESTAMP('2026-03-23 10:10:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-015', 'uspesna', 17);

-- Transakcije za nove fakture
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (16, TO_TIMESTAMP('2026-02-20 14:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-02-016', 'uspesna', 18);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (17, TO_TIMESTAMP('2026-03-22 11:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-04-017', 'uspesna', 19);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (18, TO_TIMESTAMP('2026-01-08 16:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-018', 'uspesna', 20);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (19, TO_TIMESTAMP('2026-02-16 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-02-019', 'uspesna', 21);

-- ============================================
-- 11. DASHBOARD
-- ============================================

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (1, SYSTIMESTAMP, NULL, 1, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (2, SYSTIMESTAMP - 5, NULL, 2, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (3, SYSTIMESTAMP - 10, NULL, 1, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (4, SYSTIMESTAMP - 15, NULL, 3, NULL);

-- ============================================
-- 12. IZVEŠTAJ
-- ============================================

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1, SYSTIMESTAMP - 2, 'finansijski', 
'Mesečni finansijski izveštaj za septembar 2025: Ukupan promet 373,250 RSD. Plaćeno 187,500 RSD. Neplaćeno 185,750 RSD. Procenat naplate 50.1%.', 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (2, SYSTIMESTAMP - 7, 'dobavljaci',
'Analiza dobavljača: Mlekoprodukt AD - ocena 9.5 (izuzetan partner, bez penala). Voće Srbija DOO - ocena 8.8 (2 manja penala). Agro Invest DOO - ocena 7.2 (6 penala, problematičan dobavljač).', 2);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (3, SYSTIMESTAMP - 14, 'finansijski',
'Q3 2025 - Analiza penala: Ukupno 99,500 RSD. Agro Invest DOO dominira sa 85,000 RSD (6 penala). Voće Srbija 14,500 RSD (2 penala). Šećerana Crvenka 35,000 RSD (1 kritičan penal).', 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (4, SYSTIMESTAMP - 20, 'finansijski',
'Analiza rokova plaćanja: Prosečno kašnjenje 3.5 dana. Dobavljači sa najdužim rokovima: Voće Srbija 45 dana, Agro Invest 30 dana.', 3);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (5, SYSTIMESTAMP - 1, 'finansijski',
'Projekcija troškova Q4 2025: Očekivani promet 1,200,000 RSD. Budžet po kategorijama distribuiran prema limitima.', 2);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (6, SYSTIMESTAMP - 3, 'dobavljaci',
'UPOZORENJE: Agro Invest DOO - kritična analiza. 6 penala u periodu od 5 meseci (ukupno 85,000 RSD). Stopa kršenja ugovora: 50% (3 od 6 aktivnih ugovora). Preporuka: Razmotriti prekid saradnje i nalaženje alternativnog dobavljača.', 1);

-- ============================================
-- 13. NOTIFIKACIJA
-- ============================================

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1, 'Nova faktura primljena: Agro Invest DOO - 85,500 RSD. Rok plaćanja: 01.10.2025', SYSTIMESTAMP - 1, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (2, 'UPOZORENJE: Faktura 3 - neslaganje količine. Potrebna verifikacija!', SYSTIMESTAMP - 2, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (3, 'Transakcija TRX-2025-09-001 uspešno izvršena. Iznos: 62,500 RSD', SYSTIMESTAMP - 5, 1, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (4, 'Novi penal evidentiran: Voće Srbija - kašnjenje 2 dana. Iznos: 6,000 RSD', SYSTIMESTAMP - 10, 1, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (5, 'Ugovor ističe za 30 dana: Ugovor #3 sa Voće Srbija DOO. Potrebno obnoviti.', SYSTIMESTAMP - 3, 0, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (6, 'ROK ZA PLAĆANJE: Faktura 1 dospeva za 5 dana (01.10.2025)', SYSTIMESTAMP, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (7, 'Mesečni finansijski izveštaj je generisan. Ukupan promet: 373,250 RSD', SYSTIMESTAMP - 2, 1, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (8, 'Transakcija TRX-2025-07-005 neuspešna. Razlog: Nedovoljna sredstva na računu.', SYSTIMESTAMP - 15, 1, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (9, 'KRITIČNO: Agro Invest DOO - 6. penal u 5 meseci! Ukupno 85,000 RSD. Preporuka: Hitno razmotriti prekid saradnje!', SYSTIMESTAMP - 1, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (10, 'Novi penal: Agro Invest - kašnjenje 7 dana. Iznos: 18,500 RSD', SYSTIMESTAMP - 4, 0, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (11, 'VELIKI PENAL: Šećerana Crvenka - ekstremno kašnjenje 14 dana. Iznos: 35,000 RSD', SYSTIMESTAMP - 90, 1, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (12, 'Novi penal: Voće Srbija - kvalitet II umesto I klase. Iznos: 8,500 RSD', SYSTIMESTAMP - 35, 1, NULL, 3);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (6, 'SIMULACIJA Šećerana Crvenka', 'salebecej1@gmail.com', '32165498721', 'Kristal šećer', 95.00, 4, 9.00, TO_DATE('2026-09-18', 'YYYY-MM-DD'), 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (17, TO_DATE('2026-01-10', 'YYYY-MM-DD'), TO_DATE('2027-01-10', 'YYYY-MM-DD'), 'aktivan', 
'Isporuka brašna u količini min 1000kg mesečno. Cena fiksna za prvih 6 meseci. Rok plaćanja 30 dana.', 6);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (22, 85500.00, TO_DATE('2026-03-01', 'YYYY-MM-DD'), TO_DATE('2026-04-01', 'YYYY-MM-DD'), 'verifikovana', NULL, 17);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (23, 'Pšenično brašno T-500', 1500, 90.50, 'Mesečna isporuka - septembar 2025', 22, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (24, 'Pšenično brašno T-500', 1000, 85.50, 'Mesečna isporuka - oktobar 2025', 22, 1);





INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (23, 94050.00, TO_DATE('2026-03-03', 'YYYY-MM-DD'), TO_DATE('2026-04-02', 'YYYY-MM-DD'), 'isplacena', NULL, 1);

-- Faktura 24: Mlekoprodukt (ugovor 2)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (24, 80500.00, TO_DATE('2026-03-05', 'YYYY-MM-DD'), TO_DATE('2026-03-20', 'YYYY-MM-DD'), 'isplacena', NULL, 2);

-- Faktura 25: Voće Srbija (ugovor 8)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (25, 52000.00, TO_DATE('2026-02-08', 'YYYY-MM-DD'), TO_DATE('2026-03-22', 'YYYY-MM-DD'), 'isplacena', NULL, 8);

-- Faktura 26: Šećerana Crvenka (ugovor 9)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (26, 166250.00, TO_DATE('2026-01-10', 'YYYY-MM-DD'), TO_DATE('2026-02-09', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

-- Faktura 27: Agro Invest - integralno brašno (ugovor 6)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (27, 76000.00, TO_DATE('2025-12-12', 'YYYY-MM-DD'), TO_DATE('2026-01-11', 'YYYY-MM-DD'), 'isplacena', NULL, 6);

-- Faktura 28: Mlekoprodukt - pavlaka (ugovor 7)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (28, 36000.00, TO_DATE('2026-04-15', 'YYYY-MM-DD'), TO_DATE('2026-04-30', 'YYYY-MM-DD'), 'isplacena', NULL, 7);

-- ============================================
-- STAVKE FAKTURE ZA OKTOBAR
-- ============================================

-- Stavke za fakturu 23 (Agro Invest - pšenično brašno)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (25, 'Pšenično brašno T-500', 1100, 85.50, 'Oktobarska isporuka 2025 - prva serija', 23, 1);

-- Stavke za fakturu 24 (Mlekoprodukt - UHT mleko)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (26, 'UHT mleko 3.2%', 600, 125.00, 'Oktobarske nedeljne isporuke mleka', 24, 3);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (27, 'Pavlaka 20%', 25, 180.00, 'Dodatak uz mleko - oktobar', 24, 4);

-- Stavke za fakturu 25 (Voće Srbija - jabuke)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (28, 'Jabuke Idared I klasa', 800, 65.00, 'Jesenja isporuka jabuka - oktobar 2025', 25, 5);

-- Stavke za fakturu 26 (Šećerana Crvenka - šećer)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (29, 'Kristal šećer', 1750, 95.00, 'Oktobarska isporuka šećera - povećana količina', 26, 7);

-- Stavke za fakturu 27 (Agro Invest - integralno brašno)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (30, 'Integralno brašno', 800, 95.00, 'Oktobarska isporuka integralnog brašna', 27, 2);

-- Stavke za fakturu 28 (Mlekoprodukt - pavlaka)
INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (31, 'Pavlaka 20%', 200, 180.00, 'Specijalna isporuka pavlake - oktobar', 28, 4);

-- ============================================
-- TRANSAKCIJE ZA OKTOBAR 2025
-- ============================================

-- Transakcija 20: Faktura 23 (Agro Invest)
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (20, TO_TIMESTAMP('2026-03-21 10:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-020', 'uspesna', 23);

-- Transakcija 21: Faktura 24 (Mlekoprodukt)
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (21, TO_TIMESTAMP('2026-03-19 14:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-021', 'uspesna', 24);

-- Transakcija 22: Faktura 25 (Voće Srbija)
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (22, TO_TIMESTAMP('2026-03-15 11:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-022', 'uspesna', 25);

-- Transakcija 23: Faktura 26 (Šećerana Crvenka)
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (23, TO_TIMESTAMP('2026-02-06 09:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-023', 'uspesna', 26);

-- Transakcija 24: Faktura 27 (Agro Invest - integralno)
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (24, TO_TIMESTAMP('2026-01-05 13:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-024', 'uspesna', 27);

-- Transakcija 25: Faktura 28 (Mlekoprodukt - pavlaka)
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (25, TO_TIMESTAMP('2026-04-20 15:50:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-10-025', 'uspesna', 28);




-- ============================================
-- 14. DODATNI DOBAVLJACI (PROSIREN DATASET)
-- ============================================

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (101, 'Agro Global Ingredients DOO', 'kontakt@agroglobal.rs', '910000101', 'Psenicno brasno tip 400', 82.40, 4, 8.70, TO_DATE('2026-03-18', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (102, 'Balkan Dairy Alliance AD', 'office@balkandairy.rs', '910000102', 'UHT mleko 2.8%', 119.50, 3, 9.10, TO_DATE('2026-03-19', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (103, 'Frigo Transport Foods DOO', 'prodaja@frigofoods.rs', '910000103', 'Smrznuto povrce mix', 142.00, 5, 8.40, TO_DATE('2026-03-17', 'YYYY-MM-DD'), 0);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (104, 'BioFarma Plus DOO', 'team@biofarma.rs', '910000104', 'Koncentrovani prirodni sok', 210.00, 6, 7.80, TO_DATE('2026-03-15', 'YYYY-MM-DD'), 0);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (105, 'Sever Aditivi Group', 'nabavka@severaditivi.rs', '910000105', 'Limunska kiselina', 390.00, 7, 8.95, TO_DATE('2026-03-14', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (106, 'Delta Secer Trade', 'prodaja@deltasecer.rs', '910000106', 'Secer u prahu', 101.00, 4, 9.25, TO_DATE('2026-03-20', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (107, 'Green Orchard Coop', 'info@greenorchard.rs', '910000107', 'Sveze jabuke gala', 71.50, 2, 8.85, TO_DATE('2026-03-16', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (108, 'ProteinMax Feed', 'office@proteinmax.rs', '910000108', 'Sojine proteinske pahuljice', 165.00, 5, 7.60, TO_DATE('2026-03-13', 'YYYY-MM-DD'), 0);

-- ============================================
-- 15. DODATNI UGOVORI
-- ============================================
-- Ugovori 201-206 i 217-220 su namerno "aktivan" i sa datumom isteka u proslosti
-- kako bi endpoint penalties/auto-create/ imao sta da penalizuje na klik.

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (201, TO_DATE('2024-07-01', 'YYYY-MM-DD'), TO_DATE('2025-07-01', 'YYYY-MM-DD'), 'aktivan',
'Mesecna isporuka brasna, obavezna kompletna dokumentacija i kvalitet I klase.', 101);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (202, TO_DATE('2024-12-15', 'YYYY-MM-DD'), TO_DATE('2025-12-15', 'YYYY-MM-DD'), 'aktivan',
'Nedeljne isporuke mleka, rok placanja 15 dana i striktna kontrola hladnog lanca.', 102);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (203, TO_DATE('2025-01-10', 'YYYY-MM-DD'), TO_DATE('2025-09-10', 'YYYY-MM-DD'), 'aktivan',
'Isporuka smrznutog povrca, trazena temperatura transporta od -18C.', 103);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (204, TO_DATE('2025-02-01', 'YYYY-MM-DD'), TO_DATE('2025-11-01', 'YYYY-MM-DD'), 'aktivan',
'Isporuka koncentrata u bacvama, serijski broj i sertifikat obavezni.', 104);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (205, TO_DATE('2024-11-01', 'YYYY-MM-DD'), TO_DATE('2025-06-30', 'YYYY-MM-DD'), 'aktivan',
'Aditivi za prehranu, svaka serija mora imati lot i rok trajanja.', 105);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (206, TO_DATE('2025-03-01', 'YYYY-MM-DD'), TO_DATE('2025-10-31', 'YYYY-MM-DD'), 'aktivan',
'Secer i secer u prahu, kvartaalne isporuke sa dozvoljenim odstupanjem +/-3%.', 106);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (207, TO_DATE('2025-05-01', 'YYYY-MM-DD'), TO_DATE('2026-08-31', 'YYYY-MM-DD'), 'aktivan',
'Sveze voce, minimalno 2 isporuke nedeljno i obavezna deklaracija porekla.', 107);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (208, TO_DATE('2025-10-01', 'YYYY-MM-DD'), TO_DATE('2027-02-28', 'YYYY-MM-DD'), 'aktivan',
'Proteinski proizvodi, redovan laboratorijski izvestaj o sastavu.', 108);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (209, TO_DATE('2026-01-05', 'YYYY-MM-DD'), TO_DATE('2026-12-31', 'YYYY-MM-DD'), 'otkazan',
'Pilot ugovor prekinut zbog promene proizvodnog plana.', 101);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (210, TO_DATE('2024-01-01', 'YYYY-MM-DD'), TO_DATE('2024-12-31', 'YYYY-MM-DD'), 'istekao',
'Stari ugovor za mlecne proizvode, arhiviran po isteku.', 102);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (211, TO_DATE('2025-06-01', 'YYYY-MM-DD'), TO_DATE('2026-11-30', 'YYYY-MM-DD'), 'aktivan',
'Isporuka smrznutog povrca i voca, rok placanja 30 dana.', 103);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (212, TO_DATE('2025-07-15', 'YYYY-MM-DD'), TO_DATE('2027-03-31', 'YYYY-MM-DD'), 'aktivan',
'Koncentrati i aditivi, obavezna trazena viskoznost i laboratorijski nalaz.', 104);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (213, TO_DATE('2025-05-20', 'YYYY-MM-DD'), TO_DATE('2026-05-31', 'YYYY-MM-DD'), 'aktivan',
'Isporuka aditiva po kvartalnim planovima i avansno obavestenje 48h.', 105);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (214, TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2026-09-30', 'YYYY-MM-DD'), 'aktivan',
'Secer i zasladjivaci, moguce vanredne porudzbine uz najavu 72h.', 106);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (215, TO_DATE('2025-11-01', 'YYYY-MM-DD'), TO_DATE('2027-01-31', 'YYYY-MM-DD'), 'aktivan',
'Vocni program sa sezonskim korekcijama kolicina.', 107);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (216, TO_DATE('2025-12-10', 'YYYY-MM-DD'), TO_DATE('2026-04-30', 'YYYY-MM-DD'), 'aktivan',
'Proteinska komponenta za industrijsku proizvodnju, mesecne analize sastava.', 108);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (217, TO_DATE('2024-06-01', 'YYYY-MM-DD'), TO_DATE('2025-05-31', 'YYYY-MM-DD'), 'aktivan',
'Dodatni istorijski ugovor za brasno sa vecim obimom isporuka.', 101);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (218, TO_DATE('2024-09-01', 'YYYY-MM-DD'), TO_DATE('2025-08-31', 'YYYY-MM-DD'), 'aktivan',
'Dodatni istorijski ugovor za mleko i mlecne derivate.', 102);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (219, TO_DATE('2024-03-15', 'YYYY-MM-DD'), TO_DATE('2025-03-31', 'YYYY-MM-DD'), 'aktivan',
'Istorijski ugovor za voce, ostavljen aktivan za test automatskih penala.', 107);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (220, TO_DATE('2024-04-01', 'YYYY-MM-DD'), TO_DATE('2025-04-30', 'YYYY-MM-DD'), 'aktivan',
'Istorijski ugovor za koncentrate, ostavljen aktivan za test auto-penala.', 104);

-- Dugorocni ugovori za serijske podatke faktura/stavki/transakcija
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (221, TO_DATE('2024-01-01', 'YYYY-MM-DD'), TO_DATE('2027-01-01', 'YYYY-MM-DD'), 'aktivan',
'Dugorocni ugovor za brasno i pekarske proizvode.', 101);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (222, TO_DATE('2024-02-01', 'YYYY-MM-DD'), TO_DATE('2027-02-01', 'YYYY-MM-DD'), 'aktivan',
'Dugorocni ugovor za mleko i pavlaku.', 102);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (223, TO_DATE('2024-03-01', 'YYYY-MM-DD'), TO_DATE('2027-03-01', 'YYYY-MM-DD'), 'aktivan',
'Dugorocni ugovor za voce i povrce.', 103);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (224, TO_DATE('2024-04-01', 'YYYY-MM-DD'), TO_DATE('2027-04-01', 'YYYY-MM-DD'), 'aktivan',
'Dugorocni ugovor za aditive i tehnoloske dodatke.', 104);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (225, TO_DATE('2024-05-01', 'YYYY-MM-DD'), TO_DATE('2027-05-01', 'YYYY-MM-DD'), 'aktivan',
'Dugorocni ugovor za secer i zasladjivace.', 106);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (226, TO_DATE('2024-06-01', 'YYYY-MM-DD'), TO_DATE('2027-06-01', 'YYYY-MM-DD'), 'aktivan',
'Dugorocni ugovor za sezonski vocni program.', 107);

-- ============================================
-- 16. DODATNI PENALI (ISTORIJA + SKORIJI PERIOD)
-- ============================================

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (301, 'Kasnjenje isporuke 4 dana i nepotpuna otpremnica', 9800.00, TO_DATE('2025-04-12', 'YYYY-MM-DD'), 201);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (302, 'Nedostaje laboratorijski nalaz za mleko', 7600.00, TO_DATE('2025-05-08', 'YYYY-MM-DD'), 202);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (303, 'Temperaturni rezim transporta nije ispostovan', 12800.00, TO_DATE('2025-06-22', 'YYYY-MM-DD'), 203);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (304, 'Isporucena roba bez lot oznake', 6900.00, TO_DATE('2025-07-03', 'YYYY-MM-DD'), 204);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (305, 'Nedovoljna kolicina aditiva u odnosu na ugovor', 8400.00, TO_DATE('2025-03-19', 'YYYY-MM-DD'), 205);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (306, 'Kasnjenje preko 7 dana i nekompletna dokumentacija', 15000.00, TO_DATE('2025-08-11', 'YYYY-MM-DD'), 206);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (307, 'Neodgovarajuci procenat kalibra kod voca', 5300.00, TO_DATE('2025-12-14', 'YYYY-MM-DD'), 207);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (308, 'Neslaganje izmedju fakturisane i isporucene kolicine', 9700.00, TO_DATE('2026-02-05', 'YYYY-MM-DD'), 208);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (309, 'Kasna dostava robe zbog logistickog zastoja', 6200.00, TO_DATE('2026-01-17', 'YYYY-MM-DD'), 211);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (310, 'Nedostaje sertifikat o poreklu koncentrata', 7100.00, TO_DATE('2026-03-08', 'YYYY-MM-DD'), 212);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (311, 'Prekoracen dozvoljeni procenat odstupanja aditiva', 8800.00, TO_DATE('2026-02-21', 'YYYY-MM-DD'), 213);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (312, 'Nepravilno pakovanje secera u transportu', 5600.00, TO_DATE('2026-03-02', 'YYYY-MM-DD'), 214);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (313, 'Isporuka voca sa vecim procentom ostecenih jedinica', 9300.00, TO_DATE('2026-03-10', 'YYYY-MM-DD'), 215);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (314, 'Nedostaje zapisnik o prijemu proteinske komponente', 4900.00, TO_DATE('2026-03-15', 'YYYY-MM-DD'), 216);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (315, 'Neadekvatna granulacija brasna u seriji', 7800.00, TO_DATE('2025-10-09', 'YYYY-MM-DD'), 221);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (316, 'Lab rezultat mlecne masti ispod minimuma', 6600.00, TO_DATE('2025-11-19', 'YYYY-MM-DD'), 222);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (317, 'Prekid hladnog lanca tokom transporta', 14100.00, TO_DATE('2025-12-27', 'YYYY-MM-DD'), 223);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (318, 'Hemijski sastav aditiva odstupa od specifikacije', 11900.00, TO_DATE('2026-01-29', 'YYYY-MM-DD'), 224);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (319, 'Kasnjenje kvartalne isporuke secera', 8200.00, TO_DATE('2026-02-14', 'YYYY-MM-DD'), 225);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (320, 'Nepotpuna deklaracija porekla voca', 4700.00, TO_DATE('2026-03-18', 'YYYY-MM-DD'), 226);

-- ============================================
-- 17. EKSPICITNE FAKTURE IZ PROSLOSTI (12-6 MESECI)
-- ============================================

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (601, 71200.00, TO_DATE('2025-03-12', 'YYYY-MM-DD'), TO_DATE('2025-04-11', 'YYYY-MM-DD'), 'isplacena', NULL, 201);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (602, 84500.00, TO_DATE('2025-04-18', 'YYYY-MM-DD'), TO_DATE('2025-05-03', 'YYYY-MM-DD'), 'isplacena', NULL, 202);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (603, 66300.00, TO_DATE('2025-05-09', 'YYYY-MM-DD'), TO_DATE('2025-06-08', 'YYYY-MM-DD'), 'verifikovana', NULL, 203);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (604, 59250.00, TO_DATE('2025-06-21', 'YYYY-MM-DD'), TO_DATE('2025-07-21', 'YYYY-MM-DD'), 'primljena', 'Ceka potvrdu prijema i internu kontrolu kvaliteta.', 204);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (605, 73400.00, TO_DATE('2025-07-15', 'YYYY-MM-DD'), TO_DATE('2025-08-14', 'YYYY-MM-DD'), 'odbijena', 'Odbijena zbog kasnjenja i odstupanja kvaliteta.', 205);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (606, 88900.00, TO_DATE('2025-08-02', 'YYYY-MM-DD'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), 'isplacena', NULL, 206);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (607, 64800.00, TO_DATE('2025-09-11', 'YYYY-MM-DD'), TO_DATE('2025-10-11', 'YYYY-MM-DD'), 'primljena', 'Ceka komisijsko odobrenje isporuke.', 217);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (608, 80200.00, TO_DATE('2025-09-27', 'YYYY-MM-DD'), TO_DATE('2025-10-27', 'YYYY-MM-DD'), 'verifikovana', NULL, 218);

-- Blago buduci period za test filtriranja i pregleda
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (609, 91500.00, TO_DATE('2026-04-10', 'YYYY-MM-DD'), TO_DATE('2026-05-10', 'YYYY-MM-DD'), 'primljena', 'Zakazana isporuka u toku meseca.', 215);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (610, 104300.00, TO_DATE('2026-05-05', 'YYYY-MM-DD'), TO_DATE('2026-06-04', 'YYYY-MM-DD'), 'verifikovana', NULL, 216);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1601, 'Psenicno brasno T-400', 840, 84.50, 'Istorijska serija - mart 2025', 601, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1602, 'UHT mleko 2.8%', 676, 125.00, 'Istorijska serija - april 2025', 602, 3);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1603, 'Smrznuto povrce mix', 1020, 65.00, 'Istorijska serija - maj 2025', 603, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1604, 'Koncentrovani prirodni sok', 132, 449.00, 'Istorijska serija - jun 2025', 604, 6);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1605, 'Limunska kiselina', 188, 390.00, 'Istorijska serija - jul 2025', 605, 6);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1606, 'Secer u prahu', 880, 101.00, 'Istorijska serija - avgust 2025', 606, 7);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1607, 'Psenicno brasno T-400', 760, 85.26, 'Istorijska serija - septembar 2025', 607, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1608, 'UHT mleko 2.8%', 642, 124.92, 'Istorijska serija - septembar 2025', 608, 3);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1609, 'Sveze jabuke gala', 1280, 71.48, 'Buduca serija - april 2026', 609, 5);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (1610, 'Sojine proteinske pahuljice', 632, 165.03, 'Buduca serija - maj 2026', 610, 2);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (2601, TO_TIMESTAMP('2025-03-20 09:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-HIST-2601', 'uspesna', 601);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (2602, TO_TIMESTAMP('2025-04-26 12:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-HIST-2602', 'uspesna', 602);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (2603, TO_TIMESTAMP('2025-07-23 15:05:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-HIST-2603', 'neuspesna', 605);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (2604, TO_TIMESTAMP('2025-08-10 10:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-HIST-2604', 'uspesna', 606);

-- ============================================
-- 18. DODATNI DASHBOARD / IZVESTAJ / NOTIFIKACIJA
-- ============================================

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (901, SYSTIMESTAMP - 30, NULL, 1, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (902, SYSTIMESTAMP - 24, NULL, 2, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (903, SYSTIMESTAMP - 18, NULL, 3, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (904, SYSTIMESTAMP - 12, NULL, 4, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (905, SYSTIMESTAMP - 6, NULL, 1, NULL);

INSERT INTO dashboard (sifra_d, datum_d, skladisni_operater_id, finansijski_analiticar_id, nabavni_menadzer_id)
VALUES (906, SYSTIMESTAMP - 1, NULL, 2, NULL);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1001, SYSTIMESTAMP - 16, 'finansijski',
'Retro analiza mar-avg perioda: znacajno veci obim faktura i veci broj razlicitih statusa.', 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1002, SYSTIMESTAMP - 14, 'dobavljaci',
'Prosiren portfolio dobavljaca sa 8 novih partnera i razlicitim ocenama performansi.', 2);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1003, SYSTIMESTAMP - 12, 'kvalitet',
'Povecan broj kontrola kvaliteta zbog vecih sezonskih isporuka.', 3);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1004, SYSTIMESTAMP - 10, 'zalihe',
'Istorijski trend zaliha pokazuje vecu potrosnju secera i brasna u letnjem periodu.', 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1005, SYSTIMESTAMP - 8, 'temperature',
'Kontrola temperaturnih uslova transporta prosirena na nove ugovore.', 2);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1006, SYSTIMESTAMP - 5, 'finansijski',
'Komparativni prikaz isplacenih, verifikovanih i odbijenih faktura kroz vise perioda.', 4);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1007, SYSTIMESTAMP - 3, 'dobavljaci',
'Posebna analiza ugovora koji su istekli a ostali aktivni radi automatske penalizacije.', 1);

INSERT INTO izvestaj (sifra_i, datum_i, tip_i, sadrzaj_i, kreirao_id)
VALUES (1008, SYSTIMESTAMP - 1, 'finansijski',
'Plan za naredni kvartal ukljucuje i buduce fakture radi simulacije opterecenja sistema.', 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1101, 'Prosiren dataset: dodati novi dobavljaci i ugovori.', SYSTIMESTAMP - 20, 1, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1102, 'Registrovana faktura 601 iz istorijskog perioda (mart 2025).', SYSTIMESTAMP - 19, 1, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1103, 'Registrovana faktura 602 iz istorijskog perioda (april 2025).', SYSTIMESTAMP - 18, 1, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1104, 'U toku verifikacija fakture 603.', SYSTIMESTAMP - 17, 1, NULL, 4);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1105, 'Faktura 604 ceka internu kontrolu kvaliteta.', SYSTIMESTAMP - 16, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1106, 'Faktura 605 odbijena - neuspesna transakcija zabelezena.', SYSTIMESTAMP - 15, 1, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1107, 'Faktura 606 uspesno isplacena.', SYSTIMESTAMP - 14, 1, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1108, 'Napomena: Ugovori 201-206 i 217-220 su istekli ali aktivni.', SYSTIMESTAMP - 13, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1109, 'Klik na Proveri krsenja ugovora ce kreirati nove penale za istekle aktivne ugovore.', SYSTIMESTAMP - 12, 0, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1110, 'Dodat serijski blok faktura za period od 12 meseci unazad.', SYSTIMESTAMP - 11, 1, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1111, 'Dodat serijski blok sa buducim fakturama za test planiranja.', SYSTIMESTAMP - 10, 0, NULL, 4);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1112, 'Novi penal 320 evidentiran za ugovor 226.', SYSTIMESTAMP - 9, 1, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1113, 'Povecan broj transakcija radi testiranja performansi platnog toka.', SYSTIMESTAMP - 8, 0, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1114, 'Faktura 609 planirana za april 2026.', SYSTIMESTAMP - 7, 0, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1115, 'Faktura 610 planirana za maj 2026.', SYSTIMESTAMP - 6, 0, NULL, 4);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1116, 'Automatska analiza saradnje osvezena sa novim podacima.', SYSTIMESTAMP - 5, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1117, 'Podsetnik: proveriti ugovore pred istek u narednom periodu.', SYSTIMESTAMP - 2, 0, NULL, 2);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1118, 'Sistem je spreman za test klika na Proveri krsenja ugovora.', SYSTIMESTAMP - 1, 0, NULL, 3);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1119, 'Planirana isporuka: sezonski vocni paket za sledeci mesec.', SYSTIMESTAMP + 2, 0, NULL, 1);

INSERT INTO notifikacija (sifra_n, poruka_n, datum_n, procitana_n, link_n, korisnik_id)
VALUES (1120, 'Planirana finansijska revizija novih ugovora.', SYSTIMESTAMP + 5, 0, NULL, 4);
-- -- ============================================-- ============================================-- ============================================-- ============================================-- ============================================-- ============================================
-- -- ============================================
-- -- 19. MASOVNO PROSIRENJE FAKTURA/STAVKI/TRANSAKCIJA
-- -- ============================================
-- -- Ovaj blok dodaje veliki broj redova sa mesovitim statusima i datumima
-- -- (prosli period, tekuci i blago buduci period) kako bi baza bila punija.

-- DECLARE
--     v_invoice_id NUMBER := 1200;
--     v_item_id NUMBER := 2200;
--     v_tx_id NUMBER := 3200;
--     v_issue_date DATE;
--     v_due_date DATE;
--     v_status VARCHAR2(20);
--     v_reason VARCHAR2(400);
--     v_amount NUMBER(12,2);
--     v_quantity NUMBER;
-- BEGIN
--     FOR c IN (
--         SELECT 221 AS ugovor_id, 1 AS proizvod_id, 92000 AS base_amount, 1100 AS base_qty, 84.50 AS unit_price FROM dual
--         UNION ALL SELECT 222, 3, 78000, 620, 125.00 FROM dual
--         UNION ALL SELECT 223, 5, 56000, 860, 65.00 FROM dual
--         UNION ALL SELECT 224, 6, 68000, 150, 450.00 FROM dual
--         UNION ALL SELECT 225, 7, 99000, 1000, 95.00 FROM dual
--         UNION ALL SELECT 226, 2, 74000, 780, 95.00 FROM dual
--     ) LOOP
--         FOR m IN 0..15 LOOP
--             v_issue_date := ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -12 + m) + MOD(m, 6);
--             v_due_date := v_issue_date + CASE
--                 WHEN c.ugovor_id IN (222, 226) THEN 15
--                 WHEN c.ugovor_id = 223 THEN 45
--                 ELSE 30
--             END;

--             v_amount := c.base_amount + (m * 1350) + MOD(c.ugovor_id, 5) * 250;

--             IF MOD(m, 4) = 0 THEN
--                 v_status := 'isplacena';
--                 v_reason := NULL;
--             ELSIF MOD(m, 4) = 1 THEN
--                 v_status := 'verifikovana';
--                 v_reason := NULL;
--             ELSIF MOD(m, 4) = 2 THEN
--                 v_status := 'primljena';
--                 v_reason := 'Ceka internu verifikaciju i uskladjivanje ulazne dokumentacije.';
--             ELSE
--                 v_status := 'odbijena';
--                 v_reason := 'Odbijena zbog odstupanja kvaliteta ili kasnjenja isporuke.';
--             END IF;

--             INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
--             VALUES (v_invoice_id, v_amount, v_issue_date, v_due_date, v_status, v_reason, c.ugovor_id);

--             v_quantity := c.base_qty + (m * 18) + MOD(c.ugovor_id, 4) * 12;

--             INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
--             VALUES (
--                 v_item_id,
--                 'Serijska stavka ugovor ' || c.ugovor_id,
--                 v_quantity,
--                 c.unit_price,
--                 'Automatski generisana stavka za bogatiji test dataset.',
--                 v_invoice_id,
--                 c.proizvod_id
--             );

--             IF v_status = 'isplacena' THEN
--                 INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
--                 VALUES (
--                     v_tx_id,
--                     CAST(v_issue_date + 7 + MOD(m, 3) AS TIMESTAMP),
--                     'TRX-BULK-' || TO_CHAR(v_tx_id),
--                     'uspesna',
--                     v_invoice_id
--                 );
--                 v_tx_id := v_tx_id + 1;
--             ELSIF v_status = 'odbijena' THEN
--                 INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
--                 VALUES (
--                     v_tx_id,
--                     CAST(v_issue_date + 2 AS TIMESTAMP),
--                     'TRX-BULK-' || TO_CHAR(v_tx_id),
--                     'neuspesna',
--                     v_invoice_id
--                 );
--                 v_tx_id := v_tx_id + 1;
--             END IF;

--             v_invoice_id := v_invoice_id + 1;
--             v_item_id := v_item_id + 1;
--         END LOOP;
--     END LOOP;
-- END;
-- /
-- ============================================-- ============================================-- ============================================-- ============================================-- ============================================-- ============================================
-- ============================================
-- COMMIT
-- ============================================
COMMIT;

-- ============================================
-- RESETOVANJE SEKVENCI NA MAX(ID)+1
-- ============================================

DECLARE
    -- Kursor sa listom tabela, isti kao u vašem originalnom kodu
    CURSOR c_tables IS
        SELECT table_name
        FROM (
            SELECT 'KORISNIK' AS table_name FROM dual UNION ALL
            SELECT 'FINANSIJSKI_ANALITICAR' FROM dual UNION ALL
            SELECT 'DOBAVLJAC' FROM dual UNION ALL
            SELECT 'UGOVOR' FROM dual UNION ALL
            SELECT 'PENAL' FROM dual UNION ALL
            SELECT 'KATEGORIJA_PROIZVODA' FROM dual UNION ALL
            SELECT 'PROIZVOD' FROM dual UNION ALL
            SELECT 'FAKTURA' FROM dual UNION ALL
            SELECT 'STAVKA_FAKTURE' FROM dual UNION ALL
            SELECT 'TRANSAKCIJA' FROM dual UNION ALL
            SELECT 'DASHBOARD' FROM dual UNION ALL
            SELECT 'IZVESTAJ' FROM dual UNION ALL
            SELECT 'NOTIFIKACIJA' FROM dual
        );

    v_seq_name          VARCHAR2(100);
    v_pk_column_name    VARCHAR2(100);
    v_max_id            NUMBER;
    v_start_with        NUMBER;
    v_sql               VARCHAR2(500);

BEGIN
    FOR t IN c_tables LOOP
        v_seq_name := LOWER(t.table_name) || '_seq';

        BEGIN
            -- 1. Dinamički pronalazimo ime kolone koja je primarni ključ (PK)
            SELECT cols.column_name
            INTO v_pk_column_name
            FROM all_constraints cons
            JOIN all_cons_columns cols ON cons.constraint_name = cols.constraint_name AND cons.owner = cols.owner
            WHERE cons.constraint_type = 'P' -- 'P' za Primary Key
              AND cons.table_name = t.table_name
              AND cons.owner = USER; -- Gledamo samo objekte trenutnog korisnika

            -- 2. Pronalazimo maksimalnu vrednost primarnog ključa u tabeli
            v_sql := 'SELECT MAX(' || v_pk_column_name || ') FROM ' || t.table_name;
            EXECUTE IMMEDIATE v_sql INTO v_max_id;

            -- Ako je tabela prazna, v_max_id će biti NULL. U tom slučaju, počinjemo od 1.
            v_start_with := NVL(v_max_id, 0) + 1;

            -- 3. Brišemo postojeću sekvencu (ako postoji)
            BEGIN
                EXECUTE IMMEDIATE 'DROP SEQUENCE ' || v_seq_name;
                DBMS_OUTPUT.PUT_LINE('Obrisana postojeća sekvenca: ' || v_seq_name);
            EXCEPTION
                WHEN OTHERS THEN -- Greška ako sekvenca ne postoji, ignorišemo je
                    NULL;
            END;

            -- 4. Kreiramo novu sekvencu sa ispravnom početnom vrednošću
            v_sql := 'CREATE SEQUENCE ' || v_seq_name || ' START WITH ' || v_start_with || ' INCREMENT BY 1 NOCACHE';
            EXECUTE IMMEDIATE v_sql;
            
            DBMS_OUTPUT.PUT_LINE('Kreirana/ažurirana sekvenca: ' || v_seq_name || ' sa početnom vrednošću ' || v_start_with);

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                DBMS_OUTPUT.PUT_LINE('UPOZORENJE: Nije pronađen primarni ključ za tabelu: ' || t.table_name || '. Sekvenca nije ažurirana.');
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
UNION ALL
SELECT 'FINANSIJSKI_ANALITICAR', COUNT(*) FROM finansijski_analiticar
UNION ALL
SELECT 'DOBAVLJACI', COUNT(*) FROM dobavljac
UNION ALL
SELECT 'UGOVORI', COUNT(*) FROM ugovor
UNION ALL
SELECT 'PENALI', COUNT(*) FROM penal
UNION ALL
SELECT 'KATEGORIJE', COUNT(*) FROM kategorija_proizvoda
UNION ALL
SELECT 'PROIZVODI', COUNT(*) FROM proizvod
UNION ALL
SELECT 'FAKTURE', COUNT(*) FROM faktura
UNION ALL
SELECT 'STAVKE_FAKTURE', COUNT(*) FROM stavka_fakture
UNION ALL
SELECT 'TRANSAKCIJE', COUNT(*) FROM transakcija
UNION ALL
SELECT 'DASHBOARDS', COUNT(*) FROM dashboard
UNION ALL
SELECT 'IZVESTAJI', COUNT(*) FROM izvestaj
UNION ALL
SELECT 'NOTIFIKACIJE', COUNT(*) FROM notifikacija;