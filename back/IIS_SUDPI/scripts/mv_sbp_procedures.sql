-- Triger 1: Automatsko ažuriranje ocene dobavljača
CREATE OR REPLACE TRIGGER TRG_UPDATE_SUPPLIER_RATING
AFTER INSERT ON REKLAMACIJA
FOR EACH ROW
DECLARE
    v_current_rating NUMBER;
    v_penalty NUMBER;
BEGIN
    -- Dobavi trenutnu ocenu dobavljača
    SELECT OCENA_DB INTO v_current_rating
    FROM DOBAVLJAC
    WHERE SIFRA_DB = :NEW.DOBAVLJAC_SIFRA_DB;

    -- Izračunaj penalty na osnovu jačine žalbe
    v_penalty := CASE
        WHEN :NEW.JACINA_ZALBE_R <= 3 THEN :NEW.JACINA_ZALBE_R * 0.3
        WHEN :NEW.JACINA_ZALBE_R <= 7 THEN :NEW.JACINA_ZALBE_R * 0.3
        ELSE :NEW.JACINA_ZALBE_R * 0.3
    END;

    -- Ažuriraj ocenu dobavljača
    UPDATE DOBAVLJAC
    SET OCENA_DB = GREATEST(0, LEAST(10, v_current_rating - v_penalty)),
        DATUM_OCENJIVANJA = SYSDATE
    WHERE SIFRA_DB = :NEW.DOBAVLJAC_SIFRA_DB;
END;
/

-- Triger 2: Provera preklapanja poseta
CREATE OR REPLACE TRIGGER TRG_CHECK_VISIT_OVERLAP
BEFORE INSERT OR UPDATE ON POSETA
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    -- Proveri da li postoje preklapajuće posete za istog kontrolora
    SELECT COUNT(*)
    INTO v_count
    FROM POSETA
    WHERE KONTROLOR_KVALITETA_SIFRA_K = :NEW.KONTROLOR_KVALITETA_SIFRA_K
    AND STATUS_PO != 'otkazana'
    AND :NEW.DATUM_OD_PO < DATUM_DO_PO
    AND :NEW.DATUM_DO_PO > DATUM_OD_PO;

    IF v_count > 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Postoji preklapanje u terminima poseta');
    END IF;
END;
/


DELETE FROM KONTROLOR_KVALITETA;
DELETE FROM KORISNIK;
DELETE FROM REKLAMACIJA;
DELETE FROM DOBAVLJAC;
DELETE FROM IZVESTAJ;
COMMIT;

Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K)
values ('pbkdf2_sha256$870000$TBPa0G1YJA8WchwMpSej12$Z41cEGgRWcRHjhZwEKXaVA8a7anJRXettd0mkBCxzWI=',to_timestamp('08-OCT-25 02.25.41.558910000 PM','DD-MON-RR HH.MI.SSXFF AM'),0,'kontrolor@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 02.20.39.075427000 PM','DD-MON-RR HH.MI.SSXFF AM'),1,'kontrolor','kontrolor','kontrolor@gmail.com','kontrolor_kvaliteta');
-- KONTROLOR_KVALITETA PK je sada direktno SIFRA_K (arc na KORISNIK), bez posebne ID kolone.
Insert into KONTROLOR_KVALITETA (SIFRA_K) values (1);
COMMIT;

BEGIN
  FOR i IN 20..30 LOOP
    INSERT INTO DOBAVLJAC (
      SIFRA_DB,
      NAZIV_DB,
      EMAIL_DB,
      PIB_DB,
      IME_SIROVINE,
      CENA,
      ROK_ISPORUKE,
      OCENA_DB,
      DATUM_OCENJIVANJA,
      IZABRAN
    ) VALUES (
      i,
      'Dobavljac_' || i,
      'email' || i || '@example.com',
      'PIB' || LPAD(i, 2, '0'),
      'Čelik X1',
      ROUND(DBMS_RANDOM.VALUE(50, 500), 2),
      TRUNC(DBMS_RANDOM.VALUE(1, 30)),
      ROUND(DBMS_RANDOM.VALUE(1, 5), 1),
      TRUNC(SYSDATE - DBMS_RANDOM.VALUE(1, 365)),
      CASE WHEN DBMS_RANDOM.VALUE < 0.5 THEN 0 ELSE 1 END
    );
  END LOOP;
  COMMIT;
END;
/

COMMIT;

BEGIN
  FOR i IN 20..3000 LOOP
    INSERT INTO REKLAMACIJA (
      DOBAVLJAC_SIFRA_DB,
      KONTROLOR_KVALITETA_SIFRA_K,
      STATUS_R,
      OPIS_PROBLEMA_R,
      VREME_TRAJANJA_R,
      JACINA_ZALBE_R,
      DATUM_PRIJEMA_R
    ) VALUES (
      TRUNC(DBMS_RANDOM.VALUE(20, 31)), -- DOBAVLJAC_SIFRA_DB (assuming IDs 20-30 exist)
      1, -- KONTROLOR_KVALITETA_SIFRA_K (assuming ID 1 exists)
      CASE TRUNC(DBMS_RANDOM.VALUE(1, 5))
        WHEN 1 THEN 'prijem'
        WHEN 2 THEN 'analiza'
        WHEN 3 THEN 'odgovor'
        ELSE 'zatvaranje'
      END,
      'Problem ' || i, -- OPIS_PROBLEMA_R
      TRUNC(DBMS_RANDOM.VALUE(1, 30)), -- VREME_TRAJANJA_R
      TRUNC(DBMS_RANDOM.VALUE(1, 11)),  -- JACINA_ZALBE_R
      SYSDATE - TRUNC(DBMS_RANDOM.VALUE(0, 365)) -- DATUM_PRIJEMA_R
    );
  END LOOP;
  COMMIT;
END;
/

COMMIT;

-- Funkcija 1: Izračunavanje prosečne ocene dobavljača za sirovinu
CREATE OR REPLACE FUNCTION IZRACUNAJ_PROSECNU_OCENU_SIROVINE(
    p_ime_sirovine VARCHAR2
) RETURN NUMBER IS
    v_prosecna_ocena NUMBER;
BEGIN
    SELECT AVG(OCENA_DB)
    INTO v_prosecna_ocena
    FROM DOBAVLJAC
    WHERE IME_SIROVINE = p_ime_sirovine;

    RETURN NVL(v_prosecna_ocena, 0);
END;
/

-- Testiranje funkcije
BEGIN
    DBMS_OUTPUT.PUT_LINE(IZRACUNAJ_PROSECNU_OCENU_SIROVINE('Čelik X1'));
END;
/

-- Funkcija 2: Pronalaženje alternativnih dobavljača
CREATE OR REPLACE FUNCTION NADJI_ALTERNATIVE_DOBAVLJACE(
    p_dobavljac_id NUMBER
) RETURN SYS_REFCURSOR IS
    v_result SYS_REFCURSOR;
    v_ime_sirovine VARCHAR2(200);
BEGIN
    -- Dobavi sirovinu trenutnog dobavljača
    SELECT IME_SIROVINE INTO v_ime_sirovine
    FROM DOBAVLJAC
    WHERE SIFRA_DB = p_dobavljac_id;

    -- Otvori kursor sa alternativnim dobavljačima
    OPEN v_result FOR
        SELECT SIFRA_DB, NAZIV_DB, OCENA_DB, ROK_ISPORUKE
        FROM DOBAVLJAC
        WHERE IME_SIROVINE = v_ime_sirovine
        AND SIFRA_DB != p_dobavljac_id
        AND OCENA_DB > (SELECT OCENA_DB FROM DOBAVLJAC WHERE SIFRA_DB = p_dobavljac_id)
        ORDER BY OCENA_DB DESC;

    RETURN v_result;
END;
/

DECLARE
    v_result_cursor SYS_REFCURSOR;
    v_sifra_db NUMBER;
    v_naziv VARCHAR2(200);
    v_ocena NUMBER;
    v_rok_isporuke NUMBER;
BEGIN
    v_result_cursor := NADJI_ALTERNATIVE_DOBAVLJACE(20);

    LOOP
        FETCH v_result_cursor INTO v_sifra_db, v_naziv, v_ocena, v_rok_isporuke;
        EXIT WHEN v_result_cursor%NOTFOUND;
        DBMS_OUTPUT.PUT_LINE('- ID: ' || v_sifra_db || ', Naziv: ' || v_naziv || ', Ocena: ' || v_ocena);
    END LOOP;
    CLOSE v_result_cursor;
END;
/

-- 3. SQL Indeksi
-- Indeks za brže pretraživanje dobavljača po sirovini i oceni
BEGIN
  EXECUTE IMMEDIATE 'DROP INDEX IDX_DOBAVLJAC_SIROVINA_OCENA';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

CREATE INDEX IDX_DOBAVLJAC_SIROVINA_OCENA ON DOBAVLJAC(IME_SIROVINE, OCENA_DB);

-- Indeks za brže pronalaženje poseta u određenom periodu
BEGIN
  EXECUTE IMMEDIATE 'DROP INDEX IDX_POSETA_DATUM';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

CREATE INDEX IDX_POSETA_DATUM ON POSETA(DATUM_OD_PO, DATUM_DO_PO, STATUS_PO);

-- Indeks za efikasnije pretraživanje reklamacija
BEGIN
  EXECUTE IMMEDIATE 'DROP INDEX IDX_REKLAMACIJA_DOBAVLJAC';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

CREATE INDEX IDX_REKLAMACIJA_DOBAVLJAC ON REKLAMACIJA(DOBAVLJAC_SIFRA_DB, DATUM_PRIJEMA_R);


-- Izvestaj


BEGIN
  EXECUTE IMMEDIATE 'DROP TYPE DobavljacOcenaTable';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/


BEGIN
  EXECUTE IMMEDIATE 'DROP TYPE DobavljacOcenaRecord';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- 4. PL/SQL Izveštaj

-- Definicija složenih tipova
CREATE OR REPLACE TYPE DobavljacOcenaRecord AS OBJECT (
    naziv_dobavljaca VARCHAR2(200),
    ime_sirovine VARCHAR2(200),
    prosecna_ocena NUMBER,
    ukupan_broj_reklamacija NUMBER
);
/

CREATE OR REPLACE TYPE DobavljacOcenaTable AS TABLE OF DobavljacOcenaRecord;
/

-- PL/SQL funkcija za generisanje izveštaja
CREATE OR REPLACE FUNCTION GenerisiIZvestajZaIzabraneSirovine
RETURN DobavljacOcenaTable PIPELINED
AS
    v_dobavljac_record DobavljacOcenaRecord;

    CURSOR c_dobavljaci IS
        WITH DobavljaciSirovine AS (
            SELECT
                d.SIFRA_DB,
                d.NAZIV_DB AS naziv_dobavljaca,
                d.IME_SIROVINE AS ime_sirovine,
                d.IZABRAN as izabran
            FROM
                DOBAVLJAC d
        ),
        ProsecneOcene AS (
            SELECT
                d.SIFRA_DB,
                AVG(d.OCENA_DB) AS prosecna_ocena
            FROM
                DOBAVLJAC d
            GROUP BY
                d.SIFRA_DB
        ),
        BrojReklamacija AS (
            SELECT
                r.DOBAVLJAC_SIFRA_DB,
                COUNT(*) AS ukupan_broj_reklamacija
            FROM
                REKLAMACIJA r
            GROUP BY
                r.DOBAVLJAC_SIFRA_DB
        )
        SELECT
            ds.naziv_dobavljaca,
            ds.ime_sirovine,
            NVL(po.prosecna_ocena, 0) AS prosecna_ocena,
            NVL(br.ukupan_broj_reklamacija, 0) AS ukupan_broj_reklamacija
        FROM
            DobavljaciSirovine ds
        LEFT JOIN
            ProsecneOcene po ON ds.SIFRA_DB = po.SIFRA_DB
        LEFT JOIN
            BrojReklamacija br ON ds.SIFRA_DB = br.DOBAVLJAC_SIFRA_DB
        WHERE ds.izabran = 1
        ORDER BY ds.naziv_dobavljaca;
BEGIN
    FOR rec IN c_dobavljaci LOOP
        v_dobavljac_record := DobavljacOcenaRecord(
            rec.naziv_dobavljaca,
            rec.ime_sirovine,
            rec.prosecna_ocena,
            rec.ukupan_broj_reklamacija
        );

        PIPE ROW (v_dobavljac_record);
    END LOOP;

    RETURN;
END;
/

-- Testiranje funkcije
SELECT * FROM TABLE(GenerisiIZvestajZaIzabraneSirovine());
