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

-- 3. SQL Indeksi
-- Indeks za brže pretraživanje dobavljača po sirovini i oceni
CREATE INDEX IDX_DOBAVLJAC_SIROVINA_OCENA ON DOBAVLJAC(ime_sirovine, ocena);

-- Indeks za brže pronalaženje poseta u određenom periodu
CREATE INDEX IDX_POSETA_DATUM ON POSETA(datum_od, datum_do, status);

-- Indeks za efikasnije pretraživanje reklamacija
CREATE INDEX IDX_REKLAMACIJA_DOBAVLJAC ON REKLAMACIJA(dobavljac_id, datum_prijema);


-- 4. Kompleksan izveštaj
CREATE OR REPLACE PROCEDURE GENERISI_IZVESTAJ_DOBAVLJACA(
    p_period_od DATE,
    p_period_do DATE
) IS
    -- Definicija tipova
    TYPE rec_dobavljac IS RECORD (
        sifra_d NUMBER,
        naziv VARCHAR2(200),
        ime_sirovine VARCHAR2(200),
        broj_reklamacija NUMBER,
        prosecna_jacina_zalbi NUMBER,
        broj_poseta NUMBER,
        trenutna_ocena NUMBER
    );
    
    TYPE tbl_dobavljaci IS TABLE OF rec_dobavljac;
    v_dobavljaci tbl_dobavljaci;
    
    -- JSON objekat za rezultat
    v_json_rezultat CLOB;
BEGIN
    -- Prikupi podatke pomoću složenog upita
    SELECT /*+ INDEX(d IDX_DOBAVLJAC_SIROVINA_OCENA) 
             INDEX(r IDX_REKLAMACIJA_DOBAVLJAC) */
           d.sifra_d,
           d.naziv,
           d.ime_sirovine,
           COUNT(DISTINCT r.reklamacija_id) as broj_reklamacija,
           AVG(r.jacina_zalbe) as prosecna_jacina_zalbi,
           COUNT(DISTINCT p.poseta_id) as broj_poseta,
           d.ocena as trenutna_ocena
    BULK COLLECT INTO v_dobavljaci
    FROM DOBAVLJAC d
    LEFT JOIN REKLAMACIJA r ON r.dobavljac_id = d.sifra_d 
        AND r.datum_prijema BETWEEN p_period_od AND p_period_do
    LEFT JOIN POSETA p ON p.dobavljac_id = d.sifra_d 
        AND p.datum_od BETWEEN p_period_od AND p_period_do
    GROUP BY d.sifra_d, d.naziv, d.ime_sirovine, d.ocena
    HAVING COUNT(DISTINCT r.reklamacija_id) > 0
    ORDER BY d.ocena;

    -- Generiši JSON izveštaj
    SELECT JSON_OBJECT(
        'period' VALUE JSON_OBJECT('od' VALUE p_period_od, 'do' VALUE p_period_do),
        'dobavljaci' VALUE JSON_ARRAYAGG(
            JSON_OBJECT(
                'sifra' VALUE d.sifra_d,
                'naziv' VALUE d.naziv,
                'sirovina' VALUE d.ime_sirovine,
                'statistika' VALUE JSON_OBJECT(
                    'broj_reklamacija' VALUE d.broj_reklamacija,
                    'prosecna_jacina_zalbi' VALUE d.prosecna_jacina_zalbi,
                    'broj_poseta' VALUE d.broj_poseta,
                    'trenutna_ocena' VALUE d.trenutna_ocena
                )
            )
            ORDER BY d.trenutna_ocena
        )
    ) INTO v_json_rezultat
    FROM TABLE(v_dobavljaci) d;

    -- Sačuvaj izveštaj
    INSERT INTO IZVESTAJ (
        sifra_i,
        datum_i,
        tip_i,
        sadrzaj_i
    ) VALUES (
        seq_izvestaj.NEXTVAL,
        SYSDATE,
        'dobavljaci',
        v_json_rezultat
    );
    
    COMMIT;
END;
/