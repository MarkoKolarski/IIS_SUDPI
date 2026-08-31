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
 ZADATAK 1: TESTIRANJE TRIGERA 1 – Automatsko ažuriranje iznosa fakture
====================================================================================================================================
*/
DECLARE
    v_faktura_id FAKTURA.SIFRA_F%TYPE;
    v_proizvod_id PROIZVOD.SIFRA_PR%TYPE;
    v_ugovor_id UGOVOR.SIFRA_U%TYPE;
    v_dobavljac_id DOBAVLJAC.SIFRA_DB%TYPE;
    v_proizvod_dobavljaca_id PROIZVOD_DOBAVLJACA.ID%TYPE;
    v_valuta_id VALUTA.SIFRA_V%TYPE;
    v_cenovnik_id CENOVNIK.SIFRA_C%TYPE;
BEGIN
    DBMS_OUTPUT.PUT_LINE(CHR(10) || '--- ZADATAK 1: TESTIRANJE TRIGERA 1 ---');
    DBMS_OUTPUT.PUT_LINE(CHR(10) || 'Testiranje trigera AZURIRAJ_FAKTURU_NAKON_UNOSA...');

    -- Potrebni su nam osnovni podaci za kreiranje fakture i stavki
    -- ISPRAVKA: Korišćenje ROWNUM = 1 radi bolje kompatibilnosti
    SELECT SIFRA_U, DOBAVLJAC_SIFRA_DB INTO v_ugovor_id, v_dobavljac_id FROM UGOVOR WHERE ROWNUM = 1;
    SELECT SIFRA_PR INTO v_proizvod_id FROM PROIZVOD WHERE ROWNUM = 1;
    SELECT SIFRA_V INTO v_valuta_id FROM VALUTA WHERE OZNAKA_V = 'RSD';

    -- STAVKA_FAKTURE sada pokazuje na CENOVNIK (Peta iteracija - veza
    -- naplaćena_po), ne direktno na PROIZVOD_DOBAVLJACA - nađi (ili kreiraj)
    -- katalošku stavku dobavljača, pa (ili kreiraj) red cenovnika za nju.
    BEGIN
        SELECT ID INTO v_proizvod_dobavljaca_id
        FROM PROIZVOD_DOBAVLJACA
        WHERE DOBAVLJAC_SIFRA_DB = v_dobavljac_id AND PROIZVOD_SIFRA_PR = v_proizvod_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            INSERT INTO PROIZVOD_DOBAVLJACA (DOBAVLJAC_SIFRA_DB, PROIZVOD_SIFRA_PR, SIFRA_KOD_DOBAVLJACA_PD)
            VALUES (v_dobavljac_id, v_proizvod_id, 'SBP-TEST')
            RETURNING ID INTO v_proizvod_dobavljaca_id;
    END;

    BEGIN
        SELECT SIFRA_C INTO v_cenovnik_id
        FROM CENOVNIK
        WHERE PROIZVOD_DOBAVLJACA_ID = v_proizvod_dobavljaca_id AND DATUM_DO_C IS NULL
        FETCH FIRST 1 ROWS ONLY;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            INSERT INTO CENOVNIK (SIFRA_C, CENA_C, DATUM_OD_C, DATUM_DO_C, PROIZVOD_DOBAVLJACA_ID, VALUTA_SIFRA_V)
            VALUES (CENOVNIK_SEQ.NEXTVAL, 1000, SYSDATE, NULL, v_proizvod_dobavljaca_id, v_valuta_id)
            RETURNING SIFRA_C INTO v_cenovnik_id;
    END;

    -- Kreiranje nove fakture sa početnim iznosom 0
    INSERT INTO FAKTURA (SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F, STATUS_F, UGOVOR_SIFRA_U, VALUTA_SIFRA_V)
    VALUES (FAKTURA_SEQ.NEXTVAL, 0, SYSDATE, SYSDATE + 30, 'primljena', v_ugovor_id, v_valuta_id)
    RETURNING SIFRA_F INTO v_faktura_id;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Kreirana je nova test faktura sa ID: ' || v_faktura_id || ' i početnim iznosom 0.');

    -- Unos prve stavke fakture
    DBMS_OUTPUT.PUT_LINE('Unos prve stavke (Količina: 2, Cena po jed: 1000). Očekivani iznos fakture: 2000.');
    INSERT INTO STAVKA_FAKTURE (SIFRA_SF, NAZIV_SF, KOLICINA_SF, CENA_PO_JED_SF, PDV_STOPA_SF, FAKTURA_SIFRA_F, CENOVNIK_SIFRA_C)
    VALUES (STAVKA_FAKTURE_SEQ.NEXTVAL, 'Test Stavka 1', 2, 1000, 20, v_faktura_id, v_cenovnik_id);
    COMMIT;

    -- Unos druge stavke fakture
    DBMS_OUTPUT.PUT_LINE('Unos druge stavke (Količina: 5, Cena po jed: 300). Očekivani iznos fakture: 3500.');
    INSERT INTO STAVKA_FAKTURE (SIFRA_SF, NAZIV_SF, KOLICINA_SF, CENA_PO_JED_SF, PDV_STOPA_SF, FAKTURA_SIFRA_F, CENOVNIK_SIFRA_C)
    VALUES (STAVKA_FAKTURE_SEQ.NEXTVAL, 'Test Stavka 2', 5, 300, 20, v_faktura_id, v_cenovnik_id);
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
    SIFRA_DB,
    NAZIV_DB,
    IZRACUNAJ_DUG_DOBAVLJACU(SIFRA_DB) AS UKUPAN_DUG
FROM
    DOBAVLJAC;


/*
====================================================================================================================================
 ZADATAK 3: TESTIRANJE INDEKSA
====================================================================================================================================
*/


/*
====================================================================================================================================
 ZADATAK 4: TESTIRANJE PROCEDURE ZA IZVEŠTAJ
====================================================================================================================================
*/

SET LONG 50000;
SET LINESIZE 250;

-- Napomena: IZVESTAJ.SADRZAJ_JSON je uklonjen u drugoj ER iteraciji - sadržaj
-- je sada relacioni. Ovde samo proveravamo da je procedura upisala zapis sa
-- ispravnim periodom i vezom na KREIRANJE; stvarni "sadržaj" (profitabilnost
-- po kategorijama) Django rekonstruiše iz STAVKA_FAKTURE za taj period
-- (views_sbp.py:_rekonstruisi_sadrzaj_izvestaja).
SELECT
    I.SIFRA_I,
    I.TIP_I,
    TO_CHAR(I.DATUM_I, 'DD.MM.YYYY HH24:MI:SS') AS Datum_Kreiranja,
    I.PERIOD_OD_I,
    I.PERIOD_DO_I,
    K.FINANSIJSKI_ANALITICAR_SIFRA_K
FROM IZVESTAJ I
JOIN KREIRANJE K ON I.KREIRANJE_ID = K.ID
WHERE I.TIP_I = 'FINANSIJSKI'
ORDER BY I.DATUM_I DESC
FETCH FIRST 1 ROWS ONLY;