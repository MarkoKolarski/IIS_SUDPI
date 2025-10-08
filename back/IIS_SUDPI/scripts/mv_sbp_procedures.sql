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

DELETE FROM DOBAVLJAC;
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


-- 4. Kompleksan izveštaj

BEGIN
  -- 1. Odbaciti proceduru koja zavisi od tipova
  EXECUTE IMMEDIATE 'DROP PROCEDURE GENERISI_IZVESTAJ_DOBAVLJACA';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  -- 2. Odbaciti tabelarni tip, jer zavisi od objektnog tipa
  EXECUTE IMMEDIATE 'DROP TYPE dobavljac_statistika_tbl';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  -- 3. Odbaciti objektni tip
  EXECUTE IMMEDIATE 'DROP TYPE dobavljac_statistika_t CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- Custom types for report generation
-- Custom types for report generation
CREATE OR REPLACE TYPE dobavljac_statistika_t AS OBJECT (
    sifra_d NUMBER,
    naziv VARCHAR2(200),
    ime_sirovine VARCHAR2(200),
    prosecna_ocena NUMBER,
    broj_reklamacija NUMBER,
    broj_poseta NUMBER,
    prosecno_vreme_resavanja_reklamacija NUMBER,
    procenat_otkazanih_poseta NUMBER
);
/

CREATE OR REPLACE TYPE dobavljac_statistika_tbl AS TABLE OF dobavljac_statistika_t;
/

-- Complex report generation procedure
CREATE OR REPLACE PROCEDURE GENERISI_IZVESTAJ_DOBAVLJACA (
    p_datum_od IN DATE,
    p_datum_do IN DATE,
    p_min_broj_reklamacija IN NUMBER DEFAULT 1,
    p_kreirao_id IN NUMBER
) IS
    v_statistika dobavljac_statistika_tbl;
    v_json_izvestaj CLOB;
    v_izvestaj_id NUMBER; -- Deklaracija
BEGIN
    -- Koristimo WITH klauzulu za pripremu međurezultata
    WITH reklamacije_stats AS (
        SELECT 
            d.sifra_d,
            COUNT(r.reklamacija_id) as broj_reklamacija,
            AVG(r.vreme_trajanja) as prosecno_vreme_resavanja
        FROM dobavljac d
        LEFT JOIN reklamacija r ON d.sifra_d = r.dobavljac_id
        WHERE r.datum_prijema BETWEEN p_datum_od AND p_datum_do
        GROUP BY d.sifra_d
    ),
    posete_stats AS (
        SELECT 
            d.sifra_d,
            COUNT(p.poseta_id) as ukupno_poseta,
            SUM(CASE WHEN p.status = 'otkazana' THEN 1 ELSE 0 END) as otkazane_posete
        FROM dobavljac d
        LEFT JOIN poseta p ON d.sifra_d = p.dobavljac_id
        WHERE p.datum_od BETWEEN p_datum_od AND p_datum_do
        GROUP BY d.sifra_d
    )
    -- BULK COLLECT za efikasno punjenje kolekcije
    SELECT dobavljac_statistika_t(
        d.sifra_d,
        d.naziv,
        d.ime_sirovine,
        d.ocena,
        NVL(r.broj_reklamacija, 0),
        NVL(p.ukupno_poseta, 0),
        NVL(r.prosecno_vreme_resavanja, 0),
        CASE 
            WHEN p.ukupno_poseta > 0 
            THEN (NVL(p.otkazane_posete, 0) / p.ukupno_poseta) * 100 
            ELSE 0 
        END
    )
    BULK COLLECT INTO v_statistika
    FROM dobavljac d
    LEFT JOIN reklamacije_stats r ON d.sifra_d = r.sifra_d
    LEFT JOIN posete_stats p ON d.sifra_d = p.sifra_d
    WHERE EXISTS (
        SELECT 1 
        FROM reklamacija rk 
        WHERE rk.dobavljac_id = d.sifra_d 
        AND rk.datum_prijema BETWEEN p_datum_od AND p_datum_do
        HAVING COUNT(*) >= p_min_broj_reklamacija
    )
    ORDER BY d.ocena DESC;

    -- Generisanje JSON izveštaja (Ispravno)
    SELECT JSON_OBJECT(
        'period' VALUE JSON_OBJECT('od' VALUE p_datum_od, 'do' VALUE p_datum_do),
        'datum_generisanja' VALUE SYSDATE,
        'dobavljaci' VALUE (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'sifra_d' VALUE d.sifra_d,
                    'naziv' VALUE d.naziv,
                    'ime_sirovine' VALUE d.ime_sirovine,
                    'statistika' VALUE JSON_OBJECT(
                        'prosecna_ocena' VALUE d.prosecna_ocena,
                        'broj_reklamacija' VALUE d.broj_reklamacija,
                        'broj_poseta' VALUE d.broj_poseta,
                        'prosecno_vreme_resavanja_reklamacija' VALUE d.prosecno_vreme_resavanja_reklamacija,
                        'procenat_otkazanih_poseta' VALUE d.procenat_otkazanih_poseta
                    )
                )
                ORDER BY d.prosecna_ocena DESC
            )
            FROM TABLE(v_statistika) d
        )
    FORMAT JSON) INTO v_json_izvestaj
    FROM dual;

    -- Čuvanje izveštaja u tabeli - ISPRAVKA ORA-01400: Dodato SIFRA_I i izvestaj_seq.NEXTVAL
    INSERT INTO izvestaj (
        sifra_i, -- Dodata kolona
        tip_i,
        sadrzaj_i,
        datum_i,
        kreirao_id
    ) VALUES (
        izvestaj_seq.NEXTVAL, -- Korišćenje sekvence za generisanje vrednosti
        'dobavljaci',
        v_json_izvestaj,
        SYSDATE,
        p_kreirao_id
    ) RETURNING sifra_i INTO v_izvestaj_id;

    COMMIT;

    -- Logovanje uspešnog generisanja - ISPRAVKA PLS-00201: Korišćenje "v_izvestaj_id"
    DBMS_OUTPUT.PUT_LINE('Izveštaj uspešno generisan. ID: ' || v_izvestaj_id);

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Greška pri generisanju izveštaja: ' || SQLERRM);
        RAISE;
END GENERISI_IZVESTAJ_DOBAVLJACA;
/

BEGIN
    GENERISI_IZVESTAJ_DOBAVLJACA(
        p_datum_od => TO_DATE('2023-01-01', 'YYYY-MM-DD'),
        p_datum_do => TO_DATE('2023-12-31', 'YYYY-MM-DD'),
        p_min_broj_reklamacija => 2,
        p_kreirao_id => 1
    );
END;
/