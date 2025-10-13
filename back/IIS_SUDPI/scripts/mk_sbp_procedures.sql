/*
====================================================================================================================================
                            PREDISPITNE OBAVEZE: SISTEMI BAZA PODATAKA
                                    IMPLEMENTACIJA PL/SQL KOMPONENTI

 Ovaj fajl sadrži rešenja za sve zadatke iz specifikacije, prilagođena za Oracle bazu podataka
 koja koristi šemu generisanu iz Django modela.

 LEGENDA IZMENA:
 1. Svi nazivi tabela i kolona su u VELIKIM SLOVIMA, u skladu sa Oracle standardom za Django migracije.
 2. Reference na kolone su usklađene sa nazivima atributa u Django modelima.
 3. Svaki zadatak je jasno odvojen i komentarisan kako bi se objasnilo kako ispunjava zahteve specifikacije.
====================================================================================================================================
*/


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
DECLARE
BEGIN
    -- Ažuriraj iznose svih faktura koje su dobile nove stavke u ovoj SQL izjavi
    MERGE INTO FAKTURA F
    USING (
        SELECT FAKTURA_ID, SUM(CENA_PO_JED * KOLICINA_SF) AS UKUPAN_IZNOS
        FROM STAVKA_FAKTURE
        GROUP BY FAKTURA_ID
    ) SF_SUM
    ON (F.SIFRA_F = SF_SUM.FAKTURA_ID)
    WHEN MATCHED THEN
        UPDATE SET F.IZNOS_F = SF_SUM.UKUPAN_IZNOS;
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška u trigeru AZURIRAJ_FAKTURU_NAKON_UNOSA: ' || SQLERRM);
        RAISE;
END;
/



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
    JOIN UGOVOR U ON F.UGOVOR_ID = U.SIFRA_U 
    WHERE U.DOBAVLJAC_ID = p_dobavljac_id 
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
    SIFRA_D,
    NAZIV,
    IZRACUNAJ_DUG_DOBAVLJACU(SIFRA_D) AS UKUPAN_DUG
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
EXPLAIN PLAN FOR 
SELECT SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F 
FROM FAKTURA 
WHERE STATUS_F IN ('primljena', 'verifikovana') 
  AND ROK_PLACANJA_F < SYSDATE;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY(NULL, NULL, 'BASIC +COST'));

PROMPT
PROMPT ============================================
PROMPT KREIRANJE INDEKSA
PROMPT ============================================

CREATE INDEX IDX_FAKTURA_STATUS_ROK ON FAKTURA(STATUS_F, ROK_PLACANJA_F);

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
EXPLAIN PLAN FOR 
SELECT SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F 
FROM FAKTURA 
WHERE STATUS_F IN ('primljena', 'verifikovana') 
  AND ROK_PLACANJA_F < SYSDATE;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY(NULL, NULL, 'BASIC +COST'));

--------------------------------------

CREATE INDEX IDX_FAKTURA_STATUS_ROK ON FAKTURA(STATUS_F, ROK_PLACANJA_F);


DECLARE
    v_ugovor_id UGOVOR.SIFRA_U%TYPE;
BEGIN
    SELECT SIFRA_U INTO v_ugovor_id FROM UGOVOR FETCH FIRST 1 ROWS ONLY;

    DBMS_OUTPUT.PUT_LINE('Pocinje generisanje 800,000 faktura...');
    FOR i IN 1..800000 LOOP
        INSERT INTO FAKTURA (SIFRA_F, IZNOS_F, DATUM_PRIJEMA_F, ROK_PLACANJA_F, STATUS_F, UGOVOR_ID)
        VALUES (
            FAKTURA_SEQ.NEXTVAL,
            TRUNC(DBMS_RANDOM.VALUE(1000, 50000), 2),
            SYSDATE - TRUNC(DBMS_RANDOM.VALUE(1, 365)),
            -- Većina faktura ima ROK U BUDUĆNOSTI
            CASE 
                WHEN DBMS_RANDOM.VALUE(0, 100) < 10 THEN 
                    -- Samo 10% faktura ima prošao rok (starije od danas)
                    SYSDATE - TRUNC(DBMS_RANDOM.VALUE(1, 90))
                ELSE 
                    -- 90% faktura ima rok u budućnosti (sledeća 2-6 meseci)
                    SYSDATE + TRUNC(DBMS_RANDOM.VALUE(60, 180))
            END,
            -- Većina faktura je PLAĆENA
            CASE TRUNC(DBMS_RANDOM.VALUE(0, 10))
                WHEN 0 THEN 'primljena'      -- 10% primljene
                WHEN 1 THEN 'verifikovana'   -- 10% verifikovane
                ELSE 'isplacena'              -- 80% isplaćene
            END,
            v_ugovor_id
        );
    END LOOP;
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
 Rezultat se formatira kao JSON i upisuje u tabelu IZVESTAJ.
====================================================================================================================================
*/
CREATE OR REPLACE PROCEDURE GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI (
    p_mesec IN NUMBER,
    p_godina IN NUMBER,
    p_kreator_id IN NUMBER
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

BEGIN
    -- 2. Kurzor (implicitni) i 3. Složen SQL upit
    WITH ProdajaPoStavkama AS (
        SELECT
            SF.KOLICINA_SF,
            SF.CENA_PO_JED,
            P.KATEGORIJA_ID
        FROM STAVKA_FAKTURE SF
        JOIN FAKTURA F ON SF.FAKTURA_ID = F.SIFRA_F
        JOIN PROIZVOD P ON SF.PROIZVOD_ID = P.SIFRA_PR
        JOIN TRANSAKCIJA T ON F.SIFRA_F = T.FAKTURA_ID
        WHERE F.STATUS_F = 'isplacena'
          AND T.STATUS_T = 'uspesna'
          AND EXTRACT(MONTH FROM T.DATUM_T) = p_mesec
          AND EXTRACT(YEAR FROM T.DATUM_T) = p_godina
    )
    SELECT
        KP.NAZIV_KP,
        SUM(PPS.KOLICINA_SF * PPS.CENA_PO_JED),
        COUNT(PPS.KOLICINA_SF)
    BULK COLLECT INTO l_profitabilnost
    FROM ProdajaPoStavkama PPS
    JOIN KATEGORIJA_PROIZVODA KP ON PPS.KATEGORIJA_ID = KP.SIFRA_KP
    GROUP BY KP.NAZIV_KP
    HAVING SUM(PPS.KOLICINA_SF * PPS.CENA_PO_JED) > 1000
    ORDER BY SUM(PPS.KOLICINA_SF * PPS.CENA_PO_JED) DESC;

    -- Generisanje sadržaja izveštaja u JSON formatu
    v_sadrzaj_izvestaja := '{"izvestaj": "2Mesecna profitabilnost po kategorijama", "mesec": ' || p_mesec || ', "godina": ' || p_godina || ', "stavke": [';

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

    -- Čuvanje izveštaja u tabelu IZVESTAJ
    INSERT INTO IZVESTAJ (SIFRA_I, TIP_I, SADRZAJ_I, DATUM_I, KREIRAO_ID)
    VALUES (IZVESTAJ_SEQ.NEXTVAL, 'finansijski', v_sadrzaj_izvestaja, SYSDATE, p_kreator_id);

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška prilikom generisanja izvestaja: ' || SQLERRM);
        ROLLBACK;
END;
/

-- Primer poziva procedure za generisanje izveštaja za tekući mesec i godinu
-- Pretpostavka je da korisnik sa ID=1 poziva proceduru.
BEGIN
    GENERISI_MESECNI_IZVESTAJ_PROFITABILNOSTI(EXTRACT(MONTH FROM SYSDATE), EXTRACT(YEAR FROM SYSDATE), 1);
END;
/

COMMIT;
