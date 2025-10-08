-- Triger 1: Automatsko ažuriranje ocene dobavljača
CREATE OR REPLACE TRIGGER TRG_UPDATE_SUPPLIER_RATING
AFTER INSERT ON REKLAMACIJA
FOR EACH ROW
DECLARE
    v_current_rating NUMBER;
    v_penalty NUMBER;
BEGIN
    -- Dobavi trenutnu ocenu dobavljača
    SELECT ocena INTO v_current_rating
    FROM DOBAVLJAC
    WHERE sifra_d = :NEW.dobavljac_id;
    
    -- Izračunaj penalty na osnovu jačine žalbe
    v_penalty := CASE 
        WHEN :NEW.jacina_zalbe <= 3 THEN :NEW.jacina_zalbe * 0.3
        WHEN :NEW.jacina_zalbe <= 7 THEN :NEW.jacina_zalbe * 0.3
        ELSE :NEW.jacina_zalbe * 0.3
    END;
    
    -- Ažuriraj ocenu dobavljača
    UPDATE DOBAVLJAC
    SET ocena = GREATEST(0, LEAST(10, v_current_rating - v_penalty)),
        datum_ocenjivanja = SYSDATE
    WHERE sifra_d = :NEW.dobavljac_id;
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
    WHERE kontrolor_id = :NEW.kontrolor_id
    AND status != 'otkazana'
    AND :NEW.datum_od < datum_do
    AND :NEW.datum_do > datum_od;
    
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
Insert into KONTROLOR_KVALITETA (ID, KORISNIK_ID) values (1, 1);
COMMIT;

BEGIN
  FOR i IN 20..30 LOOP
    INSERT INTO DOBAVLJAC (
      SIFRA_D,
      NAZIV,
      EMAIL,
      PIB_D,
      IME_SIROVINE,
      CENA,
      ROK_ISPORUKE,
      OCENA,
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

BEGIN
  FOR i IN 20..3000 LOOP
    INSERT INTO REKLAMACIJA (
      dobavljac_id,
      kontrolor_id,
      status,
      opis_problema,
      vreme_trajanja,
      jacina_zalbe,
      datum_prijema
    ) VALUES (
      TRUNC(DBMS_RANDOM.VALUE(20, 31)), -- dobavljac_id (assuming IDs 20-30 exist)
      1, -- kontrolor_id (assuming IDs 1-5 exist)
      CASE TRUNC(DBMS_RANDOM.VALUE(1, 5))
        WHEN 1 THEN 'prijem'
        WHEN 2 THEN 'analiza'
        WHEN 3 THEN 'odgovor'
        ELSE 'zatvaranje'
      END,
      'Problem ' || i, -- opis_problema
      TRUNC(DBMS_RANDOM.VALUE(1, 30)), -- vreme_trajanja
      TRUNC(DBMS_RANDOM.VALUE(1, 11)),  -- jacina_zalbe
      SYSDATE - TRUNC(DBMS_RANDOM.VALUE(0, 365)) -- datum_prijema
    );
  END LOOP;
  COMMIT;
END;
/


-- Funkcija 1: Izračunavanje prosečne ocene dobavljača za sirovinu
CREATE OR REPLACE FUNCTION IZRACUNAJ_PROSECNU_OCENU_SIROVINE(
    p_ime_sirovine VARCHAR2
) RETURN NUMBER IS
    v_prosecna_ocena NUMBER;
BEGIN
    SELECT AVG(ocena)
    INTO v_prosecna_ocena
    FROM DOBAVLJAC
    WHERE ime_sirovine = p_ime_sirovine;
    
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
    SELECT ime_sirovine INTO v_ime_sirovine
    FROM DOBAVLJAC
    WHERE sifra_d = p_dobavljac_id;
    
    -- Otvori kursor sa alternativnim dobavljačima
    OPEN v_result FOR
        SELECT sifra_d, naziv, ocena, rok_isporuke
        FROM DOBAVLJAC
        WHERE ime_sirovine = v_ime_sirovine
        AND sifra_d != p_dobavljac_id
        AND ocena > (SELECT ocena FROM DOBAVLJAC WHERE sifra_d = p_dobavljac_id)
        ORDER BY ocena DESC;
    
    RETURN v_result;
END;
/

DECLARE
    v_result_cursor SYS_REFCURSOR;
    v_sifra_d NUMBER;
    v_naziv VARCHAR2(200);
    v_ocena NUMBER;
    v_rok_isporuke NUMBER;
BEGIN
    v_result_cursor := NADJI_ALTERNATIVE_DOBAVLJACE(20);
    
    LOOP
        FETCH v_result_cursor INTO v_sifra_d, v_naziv, v_ocena, v_rok_isporuke;
        EXIT WHEN v_result_cursor%NOTFOUND;
        DBMS_OUTPUT.PUT_LINE('- ID: ' || v_sifra_d || ', Naziv: ' || v_naziv || ', Ocena: ' || v_ocena);
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

CREATE INDEX IDX_DOBAVLJAC_SIROVINA_OCENA ON DOBAVLJAC(ime_sirovine, ocena);

-- Indeks za brže pronalaženje poseta u određenom periodu
BEGIN
  EXECUTE IMMEDIATE 'DROP INDEX IDX_POSETA_DATUM';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

CREATE INDEX IDX_POSETA_DATUM ON POSETA(datum_od, datum_do, status);

-- Indeks za efikasnije pretraživanje reklamacija
BEGIN
  EXECUTE IMMEDIATE 'DROP INDEX IDX_REKLAMACIJA_DOBAVLJAC';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

CREATE INDEX IDX_REKLAMACIJA_DOBAVLJAC ON REKLAMACIJA(dobavljac_id, datum_prijema);


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
CREATE OR REPLACE FUNCTION Generisi_Izvestaj_Ocena_Dobavljaca
RETURN DobavljacOcenaTable PIPELINED
AS
    v_dobavljac_record DobavljacOcenaRecord;
    
    CURSOR c_dobavljaci IS
        WITH DobavljaciSirovine AS (
            SELECT 
                d.sifra_d,
                d.naziv AS naziv_dobavljaca,
                d.ime_sirovine
            FROM 
                DOBAVLJAC d
        ),
        ProsecneOcene AS (
            SELECT 
                d.sifra_d,
                AVG(d.ocena) AS prosecna_ocena
            FROM 
                DOBAVLJAC d
            GROUP BY 
                d.sifra_d
        ),
        BrojReklamacija AS (
            SELECT 
                r.dobavljac_id,
                COUNT(*) AS ukupan_broj_reklamacija
            FROM 
                REKLAMACIJA r
            GROUP BY 
                r.dobavljac_id
        )
        SELECT 
            ds.naziv_dobavljaca,
            ds.ime_sirovine,
            NVL(po.prosecna_ocena, 0) AS prosecna_ocena,
            NVL(br.ukupan_broj_reklamacija, 0) AS ukupan_broj_reklamacija
        FROM 
            DobavljaciSirovine ds
        LEFT JOIN 
            ProsecneOcene po ON ds.sifra_d = po.sifra_d
        LEFT JOIN 
            BrojReklamacija br ON ds.sifra_d = br.dobavljac_id
        WHERE po.prosecna_ocena > 3  -- Primer WHERE uslova
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
SELECT * FROM TABLE(Generisi_Izvestaj_Ocena_Dobavljaca());