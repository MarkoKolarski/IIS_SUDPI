/*
====================================================================================================================================
 ZADATAK 1: PL/SQL TRIGER
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Kreiranje jednog ili više netrivijalnih trigera (INSERT, UPDATE, DELETE).

 REŠENJE: Implementirana su dva netrivijalna trigera.
    1. AZURIRAJ_FAKTURU_NAKON_UNOSA: Triger koji se aktivira NAKON unosa nove stavke fakture i automatski
       preračunava i ažurira ukupan iznos na samoj fakturi. Ovo osigurava integritet podataka između povezanih tabela.
====================================================================================================================================
*/

-- TRIGER 1: Automatsko ažuriranje iznosa fakture
-- Tip: AFTER INSERT triger na tabeli STAVKA_FAKTURE
-- Funkcionalnost: Kada se unese nova stavka fakture, automatski preračunava i ažurira ukupan iznos na roditeljskoj fakturi
-- Biznis logika: Održavanje integriteta podataka između povezanih tabela

CREATE OR REPLACE TRIGGER AZURIRAJ_FAKTURU_NAKON_UNOSA
AFTER INSERT ON STAVKA_FAKTURE
FOR EACH ROW
DECLARE
    v_iznos_nove_stavke NUMBER;
BEGIN
    -- Izračunaj iznos samo za red koji se unosi, koristeći :NEW
    v_iznos_nove_stavke := :NEW.CENA_PO_JED_SF * :NEW.KOLICINA_SF;

    UPDATE FAKTURA F
    SET F.IZNOS_F = NVL(F.IZNOS_F, 0) + v_iznos_nove_stavke
    WHERE F.SIFRA_F = :NEW.FAKTURA_SIFRA_F;
    
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška u trigeru AZURIRAJ_FAKTURU_NAKON_UNOSA: ' || SQLERRM);
        RAISE;
END;
/

DROP TRIGGER AZURIRAJ_FAKTURU_NAKON_UNOSA;




/*
====================================================================================================================================
 ZADATAK 2: PL/SQL FUNKCIJA
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Jedna netrivijalna PL/SQL funkcija čiji se poziv uključuje u SQL upit.

 REŠENJE: Funkcija IZRACUNAJ_DUG_DOBAVLJACU prima ID dobavljača kao parametar. Ona zatim spaja tabele
 FAKTURA i UGOVOR kako bi izračunala ukupan zbir iznosa sa svih faktura za tog dobavljača koje
 još uvek nisu plaćene. Funkcija se poziva unutar SELECT upita da prikaže sve dobavljače i njihov
 trenutni dug.
====================================================================================================================================
*/
CREATE OR REPLACE FUNCTION IZRACUNAJ_DUG_DOBAVLJACU( 
    p_dobavljac_id IN NUMBER 
) RETURN NUMBER 
IS 
    v_ukupan_dug NUMBER := 0; 
BEGIN 
    SELECT NVL(SUM(F.IZNOS_F), 0)
    INTO v_ukupan_dug
    FROM FAKTURA F
    JOIN UGOVOR U ON F.UGOVOR_SIFRA_U = U.SIFRA_U
    WHERE U.DOBAVLJAC_SIFRA_DB = p_dobavljac_id
      AND F.STATUS_F != 'isplacena';
 
    RETURN v_ukupan_dug; 
EXCEPTION 
    WHEN OTHERS THEN 
        DBMS_OUTPUT.PUT_LINE('Greška u funkciji IZRACUNAJ_DUG_DOBAVLJACU: ' || SQLERRM); 
        RETURN -1; 
END; 
/

-- Primer poziva funkcije u SQL upitu
SELECT
    SIFRA_DB,
    NAZIV_DB,
    IZRACUNAJ_DUG_DOBAVLJACU(SIFRA_DB) AS UKUPAN_DUG
FROM
    DOBAVLJAC;


/*
====================================================================================================================================
 ZADATAK 3: SQL INDEKSI
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Postavljanje indeksa za ubrzanje konkretnog upita i demonstracija razlike u performansama
         na dovoljnoj količini podataka.

 REŠENJE:
 1. UPIT: Definisan je upit koji pronalazi sve fakture koje nisu plaćene ('primljena', 'verifikovana')
    i kojima je prošao rok plaćanja. Ovakav upit bi se često izvršavao u realnom sistemu.
 2. INDEKS: Kreiran je kompozitni B-tree indeks IDX_FAKTURA_STATUS_ROK na kolonama STATUS_F i ROK_PLACANJA_F.
    OBJAŠNJENJE: Bez indeksa, baza mora da skenira celu tabelu FAKTURA (Full Table Scan) da bi pronašla
    relevantne redove. Sa indeksom, baza prvo brzo pronalazi sve unose sa traženim statusima, a zatim
    unutar tog znatno manjeg skupa podataka efikasno pretražuje po datumu, drastično smanjujući vreme izvršavanja.
====================================================================================================================================
*/

--------------------------------------
PROMPT
PROMPT ============================================
PROMPT TESTIRANJE BEZ INDEKSA
PROMPT ============================================

SET TIMING ON;

SELECT COUNT(*), AVG(IZNOS_F)
FROM FAKTURA 
WHERE STATUS_F IN ('primljena', 'verifikovana') 
  AND ROK_PLACANJA_F < SYSDATE;

SET TIMING OFF;

PROMPT
PROMPT Execution plan BEZ indeksa:

EXPLAIN PLAN 
SET STATEMENT_ID = 'bez_indeksa'
FOR 
SELECT SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F 
FROM FAKTURA 
WHERE STATUS_F IN ('primljena', 'verifikovana') 
  AND ROK_PLACANJA_F < SYSDATE;

SELECT PLAN_TABLE_OUTPUT 
FROM TABLE(DBMS_XPLAN.DISPLAY(NULL, 'bez_indeksa', 'BASIC +COST'));

PROMPT
PROMPT ============================================
PROMPT KREIRANJE INDEKSA
PROMPT ============================================

CREATE INDEX IDX_FAKTURA_STATUS_ROK 
ON FAKTURA(STATUS_F, ROK_PLACANJA_F);

PROMPT
PROMPT ============================================
PROMPT TESTIRANJE SA INDEKSOM
PROMPT ============================================

SET TIMING ON;

SELECT COUNT(*), AVG(IZNOS_F)
FROM FAKTURA 
WHERE STATUS_F IN ('primljena', 'verifikovana') 
  AND ROK_PLACANJA_F < SYSDATE;

SET TIMING OFF;

PROMPT
PROMPT Execution plan SA indeksom:

EXPLAIN PLAN 
SET STATEMENT_ID = 'sa_indeksom'
FOR 
SELECT SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F 
FROM FAKTURA 
WHERE STATUS_F IN ('primljena', 'verifikovana') 
  AND ROK_PLACANJA_F < SYSDATE;

SELECT PLAN_TABLE_OUTPUT 
FROM TABLE(DBMS_XPLAN.DISPLAY(NULL, 'sa_indeksom', 'BASIC +COST'));

PROMPT
PROMPT ============================================
PROMPT ZAVRŠETAK TESTIRANJA
PROMPT ============================================

-- DROP INDEX IDX_FAKTURA_STATUS_ROK;

--------------------------------------

CREATE INDEX IDX_FAKTURA_STATUS_ROK ON FAKTURA(STATUS_F, ROK_PLACANJA_F);


-- DECLARE
--     v_ugovor_id UGOVOR.SIFRA_U%TYPE;
-- BEGIN
--     SELECT SIFRA_U INTO v_ugovor_id FROM UGOVOR FETCH FIRST 1 ROWS ONLY;

--     DBMS_OUTPUT.PUT_LINE('Pocinje generisanje 500,000 faktura...');
--     FOR i IN 1..500000 LOOP
--         INSERT INTO FAKTURA (SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F, STATUS_F, UGOVOR_SIFRA_U)
--         VALUES (
--             FAKTURA_SEQ.NEXTVAL,
--             TRUNC(DBMS_RANDOM.VALUE(1000, 50000), 2),
--             SYSDATE - TRUNC(DBMS_RANDOM.VALUE(1, 365)),
--             -- Većina faktura ima ROK U BUDUĆNOSTI
--             CASE 
--                 WHEN DBMS_RANDOM.VALUE(0, 100) < 10 THEN 
--                     -- Samo 10% faktura ima prošao rok (starije od danas)
--                     SYSDATE - TRUNC(DBMS_RANDOM.VALUE(1, 90))
--                 ELSE 
--                     -- 90% faktura ima rok u budućnosti (sledeća 2-6 meseci)
--                     SYSDATE + TRUNC(DBMS_RANDOM.VALUE(60, 180))
--             END,
--             CASE TRUNC(DBMS_RANDOM.VALUE(0, 100) / 50)
--                 WHEN 0 THEN 'primljena'      -- 25% primljene (ne-plaćene)
--                 WHEN 1 THEN 'verifikovana'   -- 25% verifikovane (ne-plaćene)
--                 ELSE 'isplacena'              -- 50% isplaćene
--             END,
--             v_ugovor_id
--         );
--     END LOOP;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Generisanje zavrseno.');
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('GRESKA: Nije pronadjen nijedan ugovor u tabeli UGOVOR. Unesite bar jedan ugovor pre pokretanja skripte.');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Neocekivana greska: ' || SQLERRM);
        ROLLBACK;
END;
/

COMMIT;

/*
====================================================================================================================================
 ZADATAK 4: IZVEŠTAJ KOJI KORISTI PL/SQL
------------------------------------------------------------------------------------------------------------------------------------
 ZAHTEV: Kompleksan izveštaj koji poziva PL/SQL i implementira:
         ● Složene PL/SQL tipove (RECORD, TABLE OF)
         ● Kurzor
         ● Složen SQL upit (JOIN >= 3 tabele, WITH, GROUP BY, HAVING, WHERE, SUM/COUNT)

 REŠENJE: Procedura GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI kreira izveštaj o profitabilnosti po
 kategorijama proizvoda za zadati mesec i godinu.
    ● SLOŽENI TIPOVI: Koristi `rec_kategorija_profit` (RECORD) za čuvanje podataka o jednoj kategoriji
      i `tab_kategorija_profit` (TABLE OF RECORD) kao kolekciju za smeštanje celog rezultata upita.
    ● KURZOR: Koristi se implicitni kurzor unutar `SELECT ... BULK COLLECT INTO ...` naredbe. Ovo je moderna
      i visoko-performantna tehnika za obradu rezultata upita koja puni celu kolekciju jednim odlaskom u bazu.
    ● SLOŽEN UPIT:
        - WITH klauzula: `ProdajaPoStavkama` se koristi za prethodnu obradu i filtriranje podataka.
        - JOIN: Spaja se 5 tabela: STAVKA_FAKTURE, FAKTURA, PROIZVOD, TRANSAKCIJA, KATEGORIJA_PROIZVODA.
        - WHERE: Filtrira podatke po plaćenim fakturama i uspešnim transakcijama u zadatom vremenskom periodu.
        - GROUP BY: Grupiše podatke po nazivu kategorije proizvoda.
        - AGREGACIJE: Koristi `SUM` za ukupan prihod i `COUNT` za broj prodatih stavki.
        - HAVING: Filtrira grupisane rezultate i prikazuje samo kategorije sa prihodom većim od 1000.
 Rezultat se formatira kao JSON (i dalje, radi demonstracije) i upisuje se
 relacioni zapis u tabelu IZVESTAJ (druga ER iteracija je uklonila kolonu
 SADRZAJ_JSON - sadržaj se sada rekonstruiše iz STAVKA_FAKTURE na strani
 Django-a, vidi views_sbp.py:_rekonstruisi_sadrzaj_izvestaja). Procedura zato
 novu šifru izveštaja vraća kroz OUT parametar p_sifra_izvestaja.
====================================================================================================================================
*/
CREATE OR REPLACE PROCEDURE GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI (
    p_mesec IN NUMBER,
    p_godina IN NUMBER,
    p_kreator_id IN NUMBER,
    p_sifra_izvestaja OUT NUMBER
)
IS
    -- 1. Složeni PL/SQL tipovi
    TYPE rec_kategorija_profit IS RECORD (
        kategorija_naziv      KATEGORIJA_PROIZVODA.NAZIV_KP%TYPE,
        ukupan_prihod         NUMBER,
        broj_prodatih_artikala NUMBER
    );
    TYPE tab_kategorija_profit IS TABLE OF rec_kategorija_profit;

    l_profitabilnost tab_kategorija_profit;
    v_sadrzaj_izvestaja CLOB;
    v_kreiranje_id NUMBER;
    v_tabla_id NUMBER;
    v_period_od DATE := TRUNC(TO_DATE(p_mesec || '/' || p_godina, 'MM/YYYY'), 'MM');

BEGIN
    -- 2. Kurzor (implicitni) i 3. Složen SQL upit
    -- JOIN je sada 6 tabela (STAVKA_FAKTURE -> PROIZVOD_DOBAVLJACA -> PROIZVOD
    -- je dodatni hop otkako STAVKA_FAKTURE ne pokazuje direktno na PROIZVOD).
    WITH ProdajaPoStavkama AS (
        SELECT
            SF.KOLICINA_SF,
            SF.CENA_PO_JED_SF,
            P.KATEGORIJA_PROIZVODA_SIFRA_KP
        FROM STAVKA_FAKTURE SF
        JOIN FAKTURA F ON SF.FAKTURA_SIFRA_F = F.SIFRA_F
        JOIN PROIZVOD_DOBAVLJACA PD ON SF.PROIZVOD_DOBAVLJACA_ID = PD.ID
        JOIN PROIZVOD P ON PD.PROIZVOD_SIFRA_PR = P.SIFRA_PR
        JOIN TRANSAKCIJA T ON F.SIFRA_F = T.FAKTURA_SIFRA_F
        WHERE F.STATUS_F = 'isplacena'
          AND T.STATUS_T = 'uspesna'
          AND EXTRACT(MONTH FROM T.DATUM_T) = p_mesec
          AND EXTRACT(YEAR FROM T.DATUM_T) = p_godina
    )
    SELECT
        KP.NAZIV_KP,
        SUM(PPS.KOLICINA_SF * PPS.CENA_PO_JED_SF),
        COUNT(PPS.KOLICINA_SF)
    BULK COLLECT INTO l_profitabilnost
    FROM ProdajaPoStavkama PPS
    JOIN KATEGORIJA_PROIZVODA KP ON PPS.KATEGORIJA_PROIZVODA_SIFRA_KP = KP.SIFRA_KP
    GROUP BY KP.NAZIV_KP
    HAVING SUM(PPS.KOLICINA_SF * PPS.CENA_PO_JED_SF) > 1000
    ORDER BY SUM(PPS.KOLICINA_SF * PPS.CENA_PO_JED_SF) DESC;

    -- Generisanje sadržaja izveštaja u JSON formatu (informativno/DBMS_OUTPUT -
    -- ne upisuje se više u bazu, vidi napomenu iznad).
    v_sadrzaj_izvestaja := '{"izvestaj": "Mesecna profitabilnost po kategorijama", "mesec": ' || p_mesec || ', "godina": ' || p_godina || ', "stavke": [';

    FOR i IN 1..l_profitabilnost.COUNT LOOP
        v_sadrzaj_izvestaja := v_sadrzaj_izvestaja ||
            '{"kategorija": "' || l_profitabilnost(i).kategorija_naziv ||
            '", "ukupan_prihod": ' || l_profitabilnost(i).ukupan_prihod ||
            ', "broj_prodatih_artikala": ' || l_profitabilnost(i).broj_prodatih_artikala || '}';
        IF i < l_profitabilnost.COUNT THEN
            v_sadrzaj_izvestaja := v_sadrzaj_izvestaja || ',';
        END IF;
    END LOOP;

    v_sadrzaj_izvestaja := v_sadrzaj_izvestaja || ']}';
    DBMS_OUTPUT.PUT_LINE(v_sadrzaj_izvestaja);

    -- Nađi (ili kreiraj) Kreiranje par (FA + kontrolna tabla) na koji Izvestaj
    -- mora da visi (ER: FK Izvestaj -> Kreiranje, NOT NULL).
    BEGIN
        SELECT ID INTO v_kreiranje_id
        FROM KREIRANJE
        WHERE FINANSIJSKI_ANALITICAR_SIFRA_K = p_kreator_id
        FETCH FIRST 1 ROWS ONLY;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            INSERT INTO KONTROLNA_TABLA (SIFRA_KT, NAZIV_KT, OPIS_KT)
            VALUES (KONTROLNA_TABLA_SEQ.NEXTVAL, 'Kontrolna tabla (SBP)', 'Automatski kreirana iz PL/SQL procedure zadatka 4.')
            RETURNING SIFRA_KT INTO v_tabla_id;

            INSERT INTO KREIRANJE (FINANSIJSKI_ANALITICAR_SIFRA_K, KONTROLNA_TABLA_SIFRA_KT, DATUM_KR)
            VALUES (p_kreator_id, v_tabla_id, SYSDATE)
            RETURNING ID INTO v_kreiranje_id;
    END;

    -- Čuvanje izveštaja u tabelu IZVESTAJ (relaciono - bez SADRZAJ_JSON)
    INSERT INTO IZVESTAJ (SIFRA_I, TIP_I, PERIOD_OD_I, PERIOD_DO_I, DATUM_I, KREIRANJE_ID)
    VALUES (IZVESTAJ_SEQ.NEXTVAL, 'FINANSIJSKI', v_period_od, LAST_DAY(v_period_od), SYSDATE, v_kreiranje_id)
    RETURNING SIFRA_I INTO p_sifra_izvestaja;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška prilikom generisanja izvestaja: ' || SQLERRM);
        ROLLBACK;
        p_sifra_izvestaja := NULL;
END;
/

-- Primer poziva procedure za generisanje izveštaja za tekući mesec i godinu
-- Pretpostavka je da korisnik sa ID=1 poziva proceduru.
DECLARE
    v_nova_sifra NUMBER;
BEGIN
    GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI(EXTRACT(MONTH FROM SYSDATE), EXTRACT(YEAR FROM SYSDATE), 1, v_nova_sifra);
    DBMS_OUTPUT.PUT_LINE('Novi izveštaj: ' || v_nova_sifra);
END;
/

COMMIT;
