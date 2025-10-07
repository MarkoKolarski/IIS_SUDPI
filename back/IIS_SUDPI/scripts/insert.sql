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

-- ============================================
-- 2. FINANSIJSKI ANALITIČAR (specifični zapisi)
-- ============================================

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (1, 1);

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (2, 2);

INSERT INTO finansijski_analiticar (id, korisnik_id)
VALUES (3, 3);

-- ============================================
-- 3. DOBAVLJAČ
-- ============================================

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (1, 'Agro Invest DOO', 'kontakt@agroinvest.rs', '123456789', 'Pšenično brašno tip 500', 85.50, 5, 7.20, TO_DATE('2025-09-15', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (2, 'Mlekoprodukt AD', 'info@mlekoprodukt.rs', '987654321', 'UHT mleko 3.2%', 125.00, 3, 9.50, TO_DATE('2025-09-20', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (3, 'Voće Srbija DOO', 'prodaja@vocesrbija.rs', '456789123', 'Jabuke Idared', 65.00, 2, 8.80, TO_DATE('2025-09-10', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (4, 'Hemija Sever DOO', 'office@hemijasever.rs', '789123456', 'Natrijum benzoat', 450.00, 7, 9.10, TO_DATE('2025-08-25', 'YYYY-MM-DD'), 1);

INSERT INTO dobavljac (sifra_d, naziv, email, PIB_d, ime_sirovine, cena, rok_isporuke, ocena, datum_ocenjivanja, izabran)
VALUES (5, 'Šećerana Crvenka', 'info@secerana.rs', '321654987', 'Kristal šećer', 95.00, 4, 9.00, TO_DATE('2025-09-18', 'YYYY-MM-DD'), 1);

-- ============================================
-- 4. UGOVOR
-- ============================================

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (1, TO_DATE('2025-01-10', 'YYYY-MM-DD'), TO_DATE('2026-01-10', 'YYYY-MM-DD'), 'aktivan', 
'Isporuka brašna u količini min 1000kg mesečno. Cena fiksna za prvih 6 meseci. Rok plaćanja 30 dana.', 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (2, TO_DATE('2025-02-15', 'YYYY-MM-DD'), TO_DATE('2026-02-15', 'YYYY-MM-DD'), 'aktivan',
'Isporuka UHT mleka 2x nedeljno. Minimalna količina 500L po isporuci. Rok plaćanja 15 dana.', 2);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (3, TO_DATE('2024-10-01', 'YYYY-MM-DD'), TO_DATE('2025-10-01', 'YYYY-MM-DD'), 'aktivan',
'Sezonska isporuka voća. Kvalitet mora biti I klasa. Rok plaćanja 45 dana.', 3);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (4, TO_DATE('2024-05-20', 'YYYY-MM-DD'), TO_DATE('2025-05-20', 'YYYY-MM-DD'), 'istekao',
'Isporuka hemikalija sa sertifikatima. Plaćanje avansno 50%.', 4);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (5, TO_DATE('2025-03-01', 'YYYY-MM-DD'), TO_DATE('2025-09-01', 'YYYY-MM-DD'), 'otkazan',
'Isporuka šećera - ugovor raskinut zbog kašnjenja u isporuci.', 5);

-- Dodatni ugovor za Agro Invest (integralno brašno)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (6, TO_DATE('2024-08-01', 'YYYY-MM-DD'), TO_DATE('2025-08-01', 'YYYY-MM-DD'), 'aktivan',
'Prošireni ugovor za isporuku integralnog brašna. Minimalna količina 200kg mesečno. Rok plaćanja 30 dana.', 1);

-- Dodatni ugovor za Mlekoprodukt (pavlaka i mlečni derivati)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (7, TO_DATE('2025-01-20', 'YYYY-MM-DD'), TO_DATE('2026-01-20', 'YYYY-MM-DD'), 'aktivan',
'Dodatni ugovor za isporuku pavlake i drugih mlečnih derivata. Isporuka 1x nedeljno. Rok plaćanja 15 dana.', 2);

-- Obnovljeni ugovor za Voće Srbija (pokriva avg-sept 2025)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (8, TO_DATE('2025-06-01', 'YYYY-MM-DD'), TO_DATE('2026-06-01', 'YYYY-MM-DD'), 'aktivan',
'Obnovljeni sezonski ugovor za isporuku voća - leto/jesen 2025. Povećane količine. Kvalitet I klasa. Rok plaćanja 45 dana.', 3);

-- Glavni godišnji ugovor za Šećerana Crvenka (mart-jun 2025)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (9, TO_DATE('2025-01-15', 'YYYY-MM-DD'), TO_DATE('2026-01-15', 'YYYY-MM-DD'), 'aktivan',
'Godišnji ugovor za isporuku kristal šećera. Mesečne isporuke 1000-2000kg. Cena fiksna. Rok plaćanja 30 dana.', 5);

-- Obnovljeni ugovor za Hemija Sever (nakon isteklog)
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (10, TO_DATE('2025-06-01', 'YYYY-MM-DD'), TO_DATE('2026-06-01', 'YYYY-MM-DD'), 'aktivan',
'Obnovljeni ugovor za isporuku hemikalija i aditiva. Svi proizvodi sa sertifikatima. Rok plaćanja 30 dana.', 4);

-- Dodatni ugovor za Agro Invest (treći ugovor - za veće količine) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (11, TO_DATE('2024-06-15', 'YYYY-MM-DD'), TO_DATE('2025-06-15', 'YYYY-MM-DD'), 'aktivan',
'Specijalni ugovor za industrijske količine brašna. Isporuka 2x mesečno. Rok plaćanja 30 dana.', 1);

-- Dodatni ugovor za Agro Invest (četvrti ugovor - sezonski) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (12, TO_DATE('2025-04-01', 'YYYY-MM-DD'), TO_DATE('2025-12-31', 'YYYY-MM-DD'), 'aktivan',
'Sezonski ugovor za prolećnu/letnju sezonu. Povećane količine. Rok plaćanja 30 dana.', 1);

-- Dodatni ugovor za Voće Srbija (treći ugovor - zimska sezona) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (13, TO_DATE('2024-12-01', 'YYYY-MM-DD'), TO_DATE('2025-11-30', 'YYYY-MM-DD'), 'aktivan',
'Zimski ugovor za isporuku konzerviranog voća. Rok plaćanja 45 dana.', 3);

-- Dodatni ugovor za Šećerana Crvenka (treći ugovor - specijalni) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (14, TO_DATE('2025-02-01', 'YYYY-MM-DD'), TO_DATE('2026-02-01', 'YYYY-MM-DD'), 'aktivan',
'Specijalni ugovor za fin šećer u prahu. Mesečne isporuke. Rok plaćanja 30 dana.', 5);

-- Dodatni ugovor za Šećerana Crvenka (četvrti ugovor - industrijski) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (15, TO_DATE('2025-07-01', 'YYYY-MM-DD'), TO_DATE('2026-07-01', 'YYYY-MM-DD'), 'aktivan',
'Industrijski ugovor za velike količine šećera. Kvartalne isporuke. Rok plaćanja 30 dana.', 5);

-- Dodatni ugovor za Šećerana Crvenka (peti ugovor - rezervni) - BEZ PENALA
INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (16, TO_DATE('2024-11-01', 'YYYY-MM-DD'), TO_DATE('2025-10-31', 'YYYY-MM-DD'), 'aktivan',
'Rezervni ugovor za hitne isporuke šećera. Po potrebi. Rok plaćanja 15 dana.', 5);

-- ============================================
-- 5. PENAL (REBALANSOVANO - različite stope kršenja)
-- ============================================

-- AGRO INVEST - 4 PENALA na 3 od 4 ugovora (75% stopa kršenja - CRVENO)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (1, 'Nedostajuća dokumentacija - sertifikat kvaliteta', 8500.00, TO_DATE('2025-08-15', 'YYYY-MM-DD'), 1);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (2, 'Isporučena količina manja od ugovorene (850kg umesto 1000kg)', 12000.00, TO_DATE('2025-09-05', 'YYYY-MM-DD'), 1);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (3, 'Kašnjenje u isporuci od 3 dana', 9000.00, TO_DATE('2025-07-20', 'YYYY-MM-DD'), 6);

INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (4, 'Kvalitet brašna ispod standarda - vraćena pošiljka', 15500.00, TO_DATE('2025-05-25', 'YYYY-MM-DD'), 12);

-- VOĆE SRBIJA - 1 PENAL na 1 od 3 ugovora (33% stopa kršenja - ŽUTO/UPOZORENJE)  
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (5, 'Kašnjenje u isporuci od 2 dana', 7500.00, TO_DATE('2025-07-10', 'YYYY-MM-DD'), 3);

-- ŠEĆERANA CRVENKA - 1 PENAL na 1 od 5 ugovora (20% stopa kršenja - ZELENO/DOBRO)
INSERT INTO penal (sifra_p, razlog_p, iznos_p, datum_p, ugovor_id)
VALUES (6, 'Ekstremno kašnjenje u isporuci od 14 dana + nekompletna dokumentacija', 25000.00, TO_DATE('2025-06-20', 'YYYY-MM-DD'), 5);

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
VALUES (1, 85500.00, TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2025-10-01', 'YYYY-MM-DD'), 'verifikovana', NULL, 1);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (2, 62500.00, TO_DATE('2025-09-10', 'YYYY-MM-DD'), TO_DATE('2025-09-25', 'YYYY-MM-DD'), 'isplacena', NULL, 2);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (3, 32500.00, TO_DATE('2025-09-15', 'YYYY-MM-DD'), TO_DATE('2025-10-30', 'YYYY-MM-DD'), 'primljena', 'Čeka se verifikacija kvaliteta isporučene robe', 3);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (4, 22500.00, TO_DATE('2025-08-20', 'YYYY-MM-DD'), TO_DATE('2025-09-20', 'YYYY-MM-DD'), 'verifikovana', NULL, 4);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (5, 47500.00, TO_DATE('2025-09-20', 'YYYY-MM-DD'), TO_DATE('2025-10-05', 'YYYY-MM-DD'), 'primljena', 'Neslaganje između fakturisane i isporučene količine', 5);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (6, 125000.00, TO_DATE('2025-09-05', 'YYYY-MM-DD'), TO_DATE('2025-09-20', 'YYYY-MM-DD'), 'isplacena', NULL, 2);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (7, 15750.00, TO_DATE('2025-07-10', 'YYYY-MM-DD'), TO_DATE('2025-08-10', 'YYYY-MM-DD'), 'odbijena', 'Neusaglašenost sa ugovorom - penalizovana isporuka', 3);

-- Dodatne fakture za Voće Srbija DOO (ugovor_id = 8)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (8, 39000.00, TO_DATE('2025-08-05', 'YYYY-MM-DD'), TO_DATE('2025-09-19', 'YYYY-MM-DD'), 'isplacena', NULL, 8);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (9, 45500.00, TO_DATE('2025-08-20', 'YYYY-MM-DD'), TO_DATE('2025-10-04', 'YYYY-MM-DD'), 'isplacena', NULL, 8);

-- Dodatne fakture za Šećerana Crvenka (ugovor_id = 9)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (10, 95000.00, TO_DATE('2025-03-15', 'YYYY-MM-DD'), TO_DATE('2025-04-14', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (11, 142500.00, TO_DATE('2025-04-10', 'YYYY-MM-DD'), TO_DATE('2025-05-10', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (12, 190000.00, TO_DATE('2025-05-05', 'YYYY-MM-DD'), TO_DATE('2025-06-04', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (13, 118750.00, TO_DATE('2025-06-12', 'YYYY-MM-DD'), TO_DATE('2025-07-12', 'YYYY-MM-DD'), 'isplacena', NULL, 9);

-- Dodatne fakture za Agro Invest (novi ugovori 11 i 12)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (14, 95000.00, TO_DATE('2025-05-15', 'YYYY-MM-DD'), TO_DATE('2025-06-14', 'YYYY-MM-DD'), 'isplacena', NULL, 11);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (15, 110000.00, TO_DATE('2025-06-05', 'YYYY-MM-DD'), TO_DATE('2025-07-05', 'YYYY-MM-DD'), 'isplacena', NULL, 11);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (16, 87500.00, TO_DATE('2025-07-12', 'YYYY-MM-DD'), TO_DATE('2025-08-11', 'YYYY-MM-DD'), 'isplacena', NULL, 6);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (17, 102000.00, TO_DATE('2025-08-22', 'YYYY-MM-DD'), TO_DATE('2025-09-21', 'YYYY-MM-DD'), 'isplacena', NULL, 12);

-- Dodatne fakture za nove ugovore
-- Faktura za Voće Srbija DOO (ugovor 13 - zimski)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (18, 52000.00, TO_DATE('2025-01-15', 'YYYY-MM-DD'), TO_DATE('2025-03-01', 'YYYY-MM-DD'), 'isplacena', NULL, 13);

-- Fakture za Šećerana Crvenka (novi ugovori 14,15,16)
INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (19, 76000.00, TO_DATE('2025-03-10', 'YYYY-MM-DD'), TO_DATE('2025-04-09', 'YYYY-MM-DD'), 'isplacena', NULL, 14);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (20, 285000.00, TO_DATE('2025-08-15', 'YYYY-MM-DD'), TO_DATE('2025-09-14', 'YYYY-MM-DD'), 'isplacena', NULL, 15);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (21, 47500.00, TO_DATE('2025-01-20', 'YYYY-MM-DD'), TO_DATE('2025-02-04', 'YYYY-MM-DD'), 'isplacena', NULL, 16);

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
VALUES (1, TO_TIMESTAMP('2025-09-12 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-001', 'uspesna', 2);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (2, TO_TIMESTAMP('2025-09-22 14:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-002', 'uspesna', 6);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (3, TO_TIMESTAMP('2025-09-25 09:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-003', 'na_cekanju', 1);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (4, TO_TIMESTAMP('2025-09-20 16:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-004', 'na_cekanju', 4);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (5, TO_TIMESTAMP('2025-07-15 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-005', 'neuspesna', 7);

-- Transakcije za nove fakture Voće Srbija DOO
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (6, TO_TIMESTAMP('2025-09-10 13:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-006', 'uspesna', 8);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (7, TO_TIMESTAMP('2025-09-28 10:50:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-007', 'uspesna', 9);

-- Transakcije za nove fakture Šećerana Crvenka
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (8, TO_TIMESTAMP('2025-04-12 09:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-04-008', 'uspesna', 10);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (9, TO_TIMESTAMP('2025-05-08 14:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-05-009', 'uspesna', 11);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (10, TO_TIMESTAMP('2025-06-02 11:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-06-010', 'uspesna', 12);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (11, TO_TIMESTAMP('2025-07-10 15:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-011', 'uspesna', 13);

-- Transakcije za nove fakture Agro Invest
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (12, TO_TIMESTAMP('2025-06-10 11:40:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-06-012', 'uspesna', 14);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (13, TO_TIMESTAMP('2025-07-02 09:20:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-07-013', 'uspesna', 15);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (14, TO_TIMESTAMP('2025-08-08 14:55:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-08-014', 'uspesna', 16);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (15, TO_TIMESTAMP('2025-09-18 10:10:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-015', 'uspesna', 17);

-- Transakcije za nove fakture
INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (16, TO_TIMESTAMP('2025-02-28 14:25:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-02-016', 'uspesna', 18);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (17, TO_TIMESTAMP('2025-04-07 11:15:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-04-017', 'uspesna', 19);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (18, TO_TIMESTAMP('2025-09-12 16:45:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-09-018', 'uspesna', 20);

INSERT INTO transakcija (sifra_t, datum_t, potvrda_t, status_t, faktura_id)
VALUES (19, TO_TIMESTAMP('2025-02-03 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'TRX-2025-02-019', 'uspesna', 21);

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
VALUES (6, 'SIMULACIJA Šećerana Crvenka', 'salebecej1@gmail.com', '32165498721', 'Kristal šećer', 95.00, 4, 9.00, TO_DATE('2025-09-18', 'YYYY-MM-DD'), 1);

INSERT INTO ugovor (sifra_u, datum_potpisa_u, datum_isteka_u, status_u, uslovi_u, dobavljac_id)
VALUES (17, TO_DATE('2025-01-10', 'YYYY-MM-DD'), TO_DATE('2026-01-10', 'YYYY-MM-DD'), 'aktivan', 
'Isporuka brašna u količini min 1000kg mesečno. Cena fiksna za prvih 6 meseci. Rok plaćanja 30 dana.', 6);

INSERT INTO faktura (sifra_f, iznos_f, datum_prijema_f, rok_placanja_f, status_f, razlog_cekanja_f, ugovor_id)
VALUES (22, 85500.00, TO_DATE('2025-09-01', 'YYYY-MM-DD'), TO_DATE('2025-10-01', 'YYYY-MM-DD'), 'verifikovana', NULL, 17);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (23, 'Pšenično brašno T-500', 1500, 90.50, 'Mesečna isporuka - septembar 2025', 22, 1);

INSERT INTO stavka_fakture (sifra_sf, naziv_sf, kolicina_sf, cena_po_jed, opis_sf, faktura_id, proizvod_id)
VALUES (24, 'Pšenično brašno T-500', 1000, 85.50, 'Mesečna isporuka - oktobar 2025', 22, 1);

-- ============================================
-- COMMIT
-- ============================================
COMMIT;

-- ============================================
-- RESETOVANJE SEKVENCI NA MAX(ID)+1
-- ============================================

-- Korisnik
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_k), 0) INTO v_max_id FROM korisnik;
    SELECT korisnik_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE korisnik_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT korisnik_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE korisnik_seq INCREMENT BY 1';
    END IF;
END;
/

-- Finansijski analitičar
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(id), 0) INTO v_max_id FROM finansijski_analiticar;
    SELECT finansijski_analiticar_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE finansijski_analiticar_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT finansijski_analiticar_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE finansijski_analiticar_seq INCREMENT BY 1';
    END IF;
END;
/

-- Dobavljač
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_d), 0) INTO v_max_id FROM dobavljac;
    SELECT dobavljac_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE dobavljac_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT dobavljac_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE dobavljac_seq INCREMENT BY 1';
    END IF;
END;
/

-- Ugovor
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_u), 0) INTO v_max_id FROM ugovor;
    SELECT ugovor_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE ugovor_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT ugovor_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE ugovor_seq INCREMENT BY 1';
    END IF;
END;
/

-- Penal
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_p), 0) INTO v_max_id FROM penal;
    SELECT penal_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE penal_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT penal_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE penal_seq INCREMENT BY 1';
    END IF;
END;
/

-- Kategorija proizvoda
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_kp), 0) INTO v_max_id FROM kategorija_proizvoda;
    SELECT kategorija_proizvoda_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE kategorija_proizvoda_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT kategorija_proizvoda_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE kategorija_proizvoda_seq INCREMENT BY 1';
    END IF;
END;
/

-- Proizvod
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_pr), 0) INTO v_max_id FROM proizvod;
    SELECT proizvod_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE proizvod_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT proizvod_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE proizvod_seq INCREMENT BY 1';
    END IF;
END;
/

-- Faktura
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_f), 0) INTO v_max_id FROM faktura;
    SELECT faktura_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE faktura_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT faktura_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE faktura_seq INCREMENT BY 1';
    END IF;
END;
/

-- Stavka fakture
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_sf), 0) INTO v_max_id FROM stavka_fakture;
    SELECT stavka_fakture_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE stavka_fakture_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT stavka_fakture_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE stavka_fakture_seq INCREMENT BY 1';
    END IF;
END;
/

-- Transakcija
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_t), 0) INTO v_max_id FROM transakcija;
    SELECT transakcija_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE transakcija_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT transakcija_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE transakcija_seq INCREMENT BY 1';
    END IF;
END;
/

-- Dashboard
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_d), 0) INTO v_max_id FROM dashboard;
    SELECT dashboard_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE dashboard_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT dashboard_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE dashboard_seq INCREMENT BY 1';
    END IF;
END;
/

-- Izvestaj
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_i), 0) INTO v_max_id FROM izvestaj;
    SELECT izvestaj_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE izvestaj_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT izvestaj_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE izvestaj_seq INCREMENT BY 1';
    END IF;
END;
/

-- Notifikacija
DECLARE
    v_max_id NUMBER;
    v_nextval NUMBER;
    v_diff NUMBER;
BEGIN
    SELECT NVL(MAX(sifra_n), 0) INTO v_max_id FROM notifikacija;
    SELECT notifikacija_seq.NEXTVAL INTO v_nextval FROM dual;
    v_diff := (v_max_id + 1) - v_nextval;
    IF v_diff != 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE notifikacija_seq INCREMENT BY ' || v_diff;
        EXECUTE IMMEDIATE 'SELECT notifikacija_seq.NEXTVAL FROM dual';
        EXECUTE IMMEDIATE 'ALTER SEQUENCE notifikacija_seq INCREMENT BY 1';
    END IF;
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