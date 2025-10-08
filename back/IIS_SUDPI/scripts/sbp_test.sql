/*
====================================================================================================================================
                            TEST SKRIPTA ZA PREDISPITNE OBAVEZE (SBP)

 Svrha ove skripte je da testira PL/SQL komponente definisane u fajlu 'sbp_procedures.sql'.
 Skripta je podeljena na sekcije koje odgovaraju zadacima iz specifikacije.

 UPUTSTVO ZA KORIŠĆENJE:
 1. Pokrenite prvo 'sbp_procedures.sql' da biste kreirali sve trigere, funkcije, indekse i procedure.
 2. Pokrenite ovu skriptu ('sbp_test.sql').
 3. Pratite izlaz u konzoli. Za testiranje indeksa, pratite posebna uputstva u sekciji za Zadatak 3.

 Pre pokretanja, obavezno omogućite ispis iz baze u vašem SQL klijentu komandom:
 SET SERVEROUTPUT ON;
====================================================================================================================================
*/
SET SERVEROUTPUT ON;

-- Početak testiranja
BEGIN
    DBMS_OUTPUT.PUT_LINE('===================================================');
    DBMS_OUTPUT.PUT_LINE(' POCETAK TESTIRANJA PL/SQL KOMPONENTI ');
    DBMS_OUTPUT.PUT_LINE('===================================================');
END;
/


/*
====================================================================================================================================
 ZADATAK 1: TESTIRANJE TRIGERA
====================================================================================================================================
*/
DECLARE
    v_faktura_id FAKTURA.SIFRA_F%TYPE;
    v_proizvod_id PROIZVOD.SIFRA_PR%TYPE;
    v_ugovor_id UGOVOR.SIFRA_U%TYPE;
BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '--- ZADATAK 1: TESTIRANJE TRIGERA ---');

    --================================================================
    -- Testiranje trigera: AZURIRAJ_STATUS_TRAJANJA_ARTIKLA
    --================================================================
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '1.1 Testiranje trigera AZURIRAJ_STATUS_TRAJANJA_ARTIKLA...');
    DBMS_OUTPUT.PUT_LINE('Unosimo tri artikla sa različitim rokovima trajanja...');

    -- Unos artikla kojem je ISTEKAO rok
    INSERT INTO ARTIKAL (SIFRA_A, NAZIV_A, OSNOVNA_CENA_A, ROK_TRAJANJA_A)
    VALUES (ARTIKAL_SEQ.NEXTVAL, 'Test Artikal - Istekao', 99.99, SYSDATE - 10);

    -- Unos artikla kojem USKORO ISTIČE rok (unutar 30 dana)
    INSERT INTO ARTIKAL (SIFRA_A, NAZIV_A, OSNOVNA_CENA_A, ROK_TRAJANJA_A)
    VALUES (ARTIKAL_SEQ.NEXTVAL, 'Test Artikal - Istice', 149.50, SYSDATE + 20);

    -- Unos artikla koji je AKTIVAN
    INSERT INTO ARTIKAL (SIFRA_A, NAZIV_A, OSNOVNA_CENA_A, ROK_TRAJANJA_A)
    VALUES (ARTIKAL_SEQ.NEXTVAL, 'Test Artikal - Aktivan', 250.00, SYSDATE + 100);

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Unos artikala završen. Proverite tabelu ARTIKAL za "Test Artikal" unose i njihov STATUS_TRAJANJA.');

    --================================================================
    -- Testiranje trigera: AZURIRAJ_FAKTURU_NAKON_UNOSA
    --================================================================
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '1.2 Testiranje trigera AZURIRAJ_FAKTURU_NAKON_UNOSA...');

    -- Potrebni su nam osnovni podaci za kreiranje fakture i stavki
    -- ISPRAVKA: Korišćenje ROWNUM = 1 umesto FETCH FIRST radi bolje kompatibilnosti
    SELECT SIFRA_U INTO v_ugovor_id FROM UGOVOR WHERE ROWNUM = 1;
    SELECT SIFRA_PR INTO v_proizvod_id FROM PROIZVOD WHERE ROWNUM = 1;

    -- Kreiranje nove fakture sa početnim iznosom 0
    INSERT INTO FAKTURA (SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F, STATUS_F, UGOVOR_ID)
    VALUES (FAKTURA_SEQ.NEXTVAL, 0, SYSDATE, SYSDATE + 30, 'primljena', v_ugovor_id)
    RETURNING SIFRA_F INTO v_faktura_id;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Kreirana je nova test faktura sa ID: ' || v_faktura_id || ' i početnim iznosom 0.');

    -- Unos prve stavke fakture
    DBMS_OUTPUT.PUT_LINE('Unos prve stavke (Količina: 2, Cena po jed: 1000). Očekivani iznos fakture: 2000.');
    INSERT INTO STAVKA_FAKTURE (SIFRA_SF, NAZIV_SF, KOLICINA_SF, CENA_PO_JED, FAKTURA_ID, PROIZVOD_ID)
    VALUES (STAVKA_FAKTURE_SEQ.NEXTVAL, 'Test Stavka 1', 2, 1000, v_faktura_id, v_proizvod_id);
    COMMIT;

    -- Unos druge stavke fakture
    DBMS_OUTPUT.PUT_LINE('Unos druge stavke (Količina: 5, Cena po jed: 300). Očekivani iznos fakture: 3500.');
    INSERT INTO STAVKA_FAKTURE (SIFRA_SF, NAZIV_SF, KOLICINA_SF, CENA_PO_JED, FAKTURA_ID, PROIZVOD_ID)
    VALUES (STAVKA_FAKTURE_SEQ.NEXTVAL, 'Test Stavka 2', 5, 300, v_faktura_id, v_proizvod_id);
    COMMIT;

    DBMS_OUTPUT.PUT_LINE('Unos stavki je završen. Proverite konačan IZNOS_F za fakturu sa ID-jem ' || v_faktura_id || '.');

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('GRESKA: Nema dovoljno osnovnih podataka (ugovor, proizvod) za testiranje. Unesite bar po jedan zapis u tabele UGOVOR i PROIZVOD.');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Neočekivana greška u testu za Zadatak 1: ' || SQLERRM);
        ROLLBACK;
END;
/

-- Prikaz rezultata testa za trigere
SELECT SIFRA_A, NAZIV_A, ROK_TRAJANJA_A, STATUS_TRAJANJA FROM ARTIKAL WHERE NAZIV_A LIKE 'Test Artikal%';
SELECT SIFRA_F, IZNOS_F, STATUS_F FROM FAKTURA WHERE SIFRA_F = (SELECT MAX(SIFRA_F) FROM FAKTURA WHERE IZNOS_F > 0);


/*
====================================================================================================================================
 ZADATAK 2: TESTIRANJE FUNKCIJE
====================================================================================================================================
*/
BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '--- ZADATAK 2: TESTIRANJE FUNKCIJE IZRACUNAJ_DUG_DOBAVLJACU ---');
    DBMS_OUTPUT.PUT_LINE('Pokretanje upita koji za svakog dobavljača prikazuje ukupan dug.');
    DBMS_OUTPUT.PUT_LINE('Rezultat će biti prikazan ispod ove poruke.');
END;
/

-- Upit koji poziva funkciju
SELECT
    SIFRA_D,
    NAZIV,
    IZRACUNAJ_DUG_DOBAVLJACU(SIFRA_D) AS UKUPAN_DUG
FROM
    DOBAVLJAC;


/*
====================================================================================================================================
 ZADATAK 3: TESTIRANJE INDEKSA
====================================================================================================================================
*/
BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '--- ZADATAK 3: TESTIRANJE PERFORMANSI INDEKSA ---');
    DBMS_OUTPUT.PUT_LINE('UPUTSTVO ZA TESTIRANJE:');
    DBMS_OUTPUT.PUT_LINE('1. Ako niste, pokrenite PL/SQL blok za generisanje test podataka iz fajla "ispravljeni_plsql.sql".');
    DBMS_OUTPUT.PUT_LINE('2. U vašem SQL klijentu, pokrenite: SET TIMING ON;');
    DBMS_OUTPUT.PUT_LINE('3. Pokrenite: DROP INDEX IDX_FAKTURA_STATUS_ROK;');
    DBMS_OUTPUT.PUT_LINE('4. Izvršite upit ispod i zabeležite vreme izvršavanja (Elapsed time).');
    DBMS_OUTPUT.PUT_LINE('5. Ponovo kreirajte indeks: CREATE INDEX IDX_FAKTURA_STATUS_ROK ON FAKTURA(STATUS_F, ROK_PLACANJA_F);');
    DBMS_OUTPUT.PUT_LINE('6. Ponovo izvršite isti upit i uporedite vreme izvršavanja.');
    DBMS_OUTPUT.PUT_LINE('   Vreme bi trebalo da bude značajno manje sa indeksom.');
END;
/

-- Upit za testiranje performansi
SELECT SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F
FROM FAKTURA
WHERE STATUS_F IN ('primljena', 'verifikovana') AND ROK_PLACANJA_F < SYSDATE;


/*
====================================================================================================================================
 ZADATAK 4: TESTIRANJE PROCEDURE ZA IZVEŠTAJ
====================================================================================================================================
*/
DECLARE
    v_placena_faktura_id FAKTURA.SIFRA_F%TYPE;
    v_kreator_id KORISNIK.SIFRA_K%TYPE;
BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '--- ZADATAK 4: TESTIRANJE PROCEDURE GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI ---');

    -- Potrebno je da imamo bar jednu plaćenu fakturu sa uspešnom transakcijom u tekućem mesecu
    -- Pronađi jednu plaćenu fakturu (iz test podataka ili regularnih)
    BEGIN
        SELECT SIFRA_F INTO v_placena_faktura_id
        FROM FAKTURA
        WHERE STATUS_F = 'isplacena' AND ROWNUM = 1;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            v_placena_faktura_id := NULL;
    END;

    -- Ako ne postoji, ili da bismo bili sigurni, dodajemo jednu uspešnu transakciju
    IF v_placena_faktura_id IS NOT NULL THEN
        DBMS_OUTPUT.PUT_LINE('Dodavanje test transakcije za fakturu ID: ' || v_placena_faktura_id);
        INSERT INTO TRANSAKCIJA (SIFRA_T, DATUM_T, POTVRDA_T, STATUS_T, FAKTURA_ID)
        VALUES (TRANSAKCIJA_SEQ.NEXTVAL, SYSDATE, 'TEST_TRANSAKCIJA_' || TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS'), 'uspesna', v_placena_faktura_id);
        COMMIT;
    ELSE
        DBMS_OUTPUT.PUT_LINE('UPOZORENJE: Nije pronađena nijedna "isplacena" faktura. Izveštaj može biti prazan.');
    END IF;

    -- Uzimamo prvog korisnika kao kreatora izveštaja
    SELECT SIFRA_K INTO v_kreator_id FROM KORISNIK WHERE ROWNUM = 1;

    -- Poziv procedure za generisanje izveštaja za tekući mesec i godinu
    DBMS_OUTPUT.PUT_LINE('Pozivanje procedure za generisanje izveštaja za tekući mesec...');
    GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI(EXTRACT(MONTH FROM SYSDATE), EXTRACT(YEAR FROM SYSDATE), v_kreator_id);
    DBMS_OUTPUT.PUT_LINE('Procedura je izvršena. Proverite tabelu IZVESTAJ za novi zapis.');

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Neočekivana greška u testu za Zadatak 4: ' || SQLERRM);
        ROLLBACK;
END;
/

-- Prikaz rezultata testa za proceduru (prikazuje poslednje kreirani izveštaj)
SELECT SIFRA_I, TIP_I, DATUM_I, KREIRAO_ID, SADRZAJ_I FROM IZVESTAJ WHERE SIFRA_I = (SELECT MAX(SIFRA_I) FROM IZVESTAJ);

BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '===================================================');
    DBMS_OUTPUT.PUT_LINE(' KRAJ TESTIRANJA ');
    DBMS_OUTPUT.PUT_LINE('===================================================');
END;
/